from __future__ import annotations

from pathlib import Path

import numpy as np
from PIL import Image


def _color_histogram(path: Path, bins: int = 8) -> np.ndarray:
    image = Image.open(path).convert("RGB").resize((64, 64))
    arr = np.asarray(image, dtype=np.float32)
    hist = []
    for channel in range(3):
        h, _ = np.histogram(arr[:, :, channel], bins=bins, range=(0, 255), density=True)
        hist.append(h)
    return np.concatenate(hist).astype(np.float32)


def infer_image(bundle: dict, image_path: Path, task: str) -> dict:
    kind = bundle.get("kind", "sklearn")
    if kind == "torch":
        return _infer_torch(bundle, image_path, task)
    features = _color_histogram(image_path).reshape(1, -1)
    model = bundle["model"]
    labels = bundle["labels"]
    proba = model.predict_proba(features)[0]
    idx = int(np.argmax(proba))
    confidence = float(proba[idx])
    predicted = str(labels[idx])
    overlay = _sklearn_heatmap(model, image_path, idx)
    result = {
        "predicted_class": predicted,
        "confidence": round(confidence, 4),
        "algorithm": bundle.get("algorithm", "random_forest_histogram"),
        "placeholder": False,
        "gradcam_url": overlay,
        "explanation": (
            "Color-histogram classifier with a patch-wise class-score overlay "
            "(Grad-CAM-style). EfficientNet weights were not present."
        ),
    }
    return result


def _sklearn_heatmap(model, image_path: Path, class_idx: int) -> str | None:
    try:
        img = Image.open(image_path).convert("RGB").resize((128, 128))
        arr = np.asarray(img, dtype=np.uint8)
        grid = 8
        step = 128 // grid
        heat = np.zeros((grid, grid), dtype=np.float32)
        tmp = image_path.parent / f"_patch_tmp_{image_path.stem}.png"
        for i in range(grid):
            for j in range(grid):
                patch = arr[i * step : (i + 1) * step, j * step : (j + 1) * step]
                patch_img = Image.fromarray(patch).resize((64, 64))
                patch_img.save(tmp)
                feat = _color_histogram(tmp).reshape(1, -1)
                proba = model.predict_proba(feat)[0]
                heat[i, j] = float(proba[class_idx])
        tmp.unlink(missing_ok=True)
        heat = heat - heat.min()
        denom = float(heat.max() + 1e-8)
        heat = heat / denom
        heat_img = Image.fromarray((heat * 255).astype(np.uint8)).resize((224, 224), Image.BILINEAR)
        base = Image.open(image_path).convert("RGB").resize((224, 224))
        red = Image.merge(
            "RGB",
            (heat_img, Image.new("L", heat_img.size), Image.new("L", heat_img.size)),
        )
        blended = Image.blend(base, red, 0.45)
        dest = image_path.parent / f"gradcam_{image_path.stem}.png"
        blended.save(dest)
        return str(dest.as_posix())
    except Exception:
        return None


def _infer_torch(bundle: dict, image_path: Path, task: str) -> dict:
    import torch
    from torchvision import transforms

    model = bundle["model"]
    labels = bundle["labels"]
    model.eval()
    tfm = transforms.Compose(
        [
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
        ]
    )
    image = Image.open(image_path).convert("RGB")
    tensor = tfm(image).unsqueeze(0)
    with torch.no_grad():
        logits = model(tensor)
        proba = torch.softmax(logits, dim=1)[0].cpu().numpy()
    idx = int(np.argmax(proba))
    confidence = float(proba[idx])
    cam_path = _gradcam(model, tensor, idx, image_path)
    result = {
        "predicted_class": str(labels[idx]),
        "confidence": round(confidence, 4),
        "algorithm": bundle.get("algorithm", "efficientnet_b0"),
        "placeholder": False,
        "gradcam_url": cam_path,
    }
    return result


def _gradcam(model, tensor, class_idx: int, image_path: Path) -> str | None:
    try:
        import torch
        from PIL import Image as PILImage

        activations = {}
        gradients = {}

        def fwd_hook(_module, _inp, out):
            activations["value"] = out.detach()

        def bwd_hook(_module, _gin, gout):
            gradients["value"] = gout[0].detach()

        target = None
        for name, module in model.named_modules():
            if name.endswith("features.8") or name.endswith("features.7"):
                target = module
        if target is None:
            children = list(model.children())
            target = children[0] if children else None
        if target is None:
            return None
        h1 = target.register_forward_hook(fwd_hook)
        h2 = target.register_full_backward_hook(bwd_hook)
        model.zero_grad()
        logits = model(tensor)
        logits[0, class_idx].backward()
        h1.remove()
        h2.remove()
        acts = activations["value"][0]
        grads = gradients["value"][0]
        weights = grads.mean(dim=(1, 2))
        cam = torch.relu((weights[:, None, None] * acts).sum(0))
        cam = cam - cam.min()
        cam = cam / (cam.max() + 1e-8)
        cam_np = (cam.cpu().numpy() * 255).astype(np.uint8)
        cam_img = PILImage.fromarray(cam_np).resize((224, 224))
        overlay_dir = image_path.parent
        dest = overlay_dir / f"gradcam_{image_path.stem}.png"
        base = Image.open(image_path).convert("RGB").resize((224, 224))
        heat = PILImage.merge(
            "RGB",
            (cam_img, PILImage.new("L", cam_img.size), PILImage.new("L", cam_img.size)),
        )
        blended = PILImage.blend(base, heat, 0.45)
        blended.save(dest)
        return str(dest.as_posix())
    except Exception:
        return None
