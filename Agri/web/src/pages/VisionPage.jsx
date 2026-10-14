import { useState } from "react";
import api, { assetUrl } from "../api.js";
import { useAuth } from "../AuthContext.jsx";

export default function VisionPage({ task, title }) {
  const { farm } = useAuth();
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState("");
  const [result, setResult] = useState(null);

  async function submit(e) {
    e.preventDefault();
    const body = new FormData();
    body.append("farm_id", farm.id);
    body.append("file", file);
    const { data } = await api.post(`/predict/${task}-detection`, body);
    setResult(data);
  }

  return (
    <div className="grid md:grid-cols-2 gap-4">
      <form className="card space-y-3" onSubmit={submit}>
        <h2 className="font-serif text-2xl">{title}</h2>
        <input
          type="file"
          accept="image/*"
          onChange={(e) => {
            const f = e.target.files[0];
            setFile(f);
            setPreview(f ? URL.createObjectURL(f) : "");
          }}
        />
        {preview && <img src={preview} alt="" className="h-40 rounded-lg object-cover" />}
        {!farm && <p className="text-sm text-amber-800">Create / register a farm before uploading.</p>}
        <button disabled={!farm || !file} className="w-full rounded-xl bg-leafdeep text-white py-3 font-bold disabled:opacity-50">
          Analyze image
        </button>
      </form>
      <div className="card">
        {result ? (
          <>
            <p className="font-serif text-3xl">{result.predicted_class}</p>
            <p>{Math.round((result.confidence || 0) * 100)}% confidence</p>
            {result.severity && <p>Severity: {result.severity}</p>}
            {result.affected_area_pct != null && <p>Affected area: {result.affected_area_pct}%</p>}
            <p className="text-xs text-[#6b5d4d] mt-2">{result.explanation}</p>
            <div className="grid grid-cols-2 gap-3 mt-4">
              <div>
                <p className="text-xs uppercase tracking-widest text-leaf mb-1">Upload</p>
                {result.image_url && <img src={assetUrl(result.image_url)} alt="upload" className="rounded-lg" />}
              </div>
              <div>
                <p className="text-xs uppercase tracking-widest text-leaf mb-1">Grad-CAM overlay</p>
                {result.gradcam_url ? (
                  <img src={assetUrl(result.gradcam_url)} alt="gradcam" className="rounded-lg" />
                ) : (
                  <p className="text-sm text-[#6b5d4d]">Overlay was not generated for this file.</p>
                )}
              </div>
            </div>
          </>
        ) : (
          <p className="text-[#6b5d4d]">Upload a leaf/field photo. Grad-CAM overlay appears beside the image when available.</p>
        )}
      </div>
    </div>
  );
}
