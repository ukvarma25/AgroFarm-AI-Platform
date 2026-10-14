import { useEffect, useState } from "react";
import { Bar, BarChart, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import api, { assetUrl } from "../api.js";

function metricVal(vals, key) {
  const v = vals?.[key];
  if (v == null) return null;
  if (typeof v === "object" && v.mean != null) return v.mean;
  return v;
}

function rowsFrom(algs, keys) {
  return Object.entries(algs || {}).map(([name, vals]) => {
    const row = { name };
    keys.forEach((k) => {
      row[k] = metricVal(vals, k);
    });
    return row;
  });
}

function Figure({ src, alt }) {
  return (
    <img
      src={assetUrl(src)}
      alt={alt}
      className="rounded-lg border border-[#d9cbb3] w-full bg-straw"
      onError={(e) => {
        e.currentTarget.style.display = "none";
      }}
    />
  );
}

export default function ModelEval() {
  const [metrics, setMetrics] = useState(null);
  useEffect(() => {
    api.get("/models/metrics").then(({ data }) => setMetrics(data));
  }, []);
  if (!metrics) return <div className="card">Loading metrics…</div>;

  const crop = metrics.crop_publication_split?.algorithms || metrics.crop_recommendation?.algorithms || {};
  const cropRows = rowsFrom(crop, ["accuracy", "precision", "recall", "f1"]);
  const yieldRows = rowsFrom(metrics.yield_prediction?.algorithms, ["mae", "rmse", "r2"]);
  const priceRows = rowsFrom(metrics.market_price?.algorithms, ["mae", "rmse", "r2"]);

  function curveRows(task) {
    const c = metrics[`${task}_detection`]?.curves;
    if (!c) return [];
    return (c.train_acc || []).map((acc, i) => ({
      epoch: i + 1,
      train_acc: acc,
      val_acc: c.val_acc?.[i],
      train_loss: c.train_loss?.[i],
      val_loss: c.val_loss?.[i],
    }));
  }

  return (
    <div className="space-y-4">
      <div className="card">
        <h2 className="font-serif text-2xl">Model Evaluation</h2>
        <p className="text-sm text-[#6b5d4d]">
          Live numbers from GET /models/metrics (training runs, not placeholders).
          {metrics.crop_publication_split?.justification && (
            <> Best crop model: {metrics.crop_publication_split.justification}</>
          )}
        </p>
      </div>

      <div className="card">
        <h3 className="font-serif text-xl">Crop comparison</h3>
        <div className="h-56">
          <ResponsiveContainer>
            <BarChart data={cropRows}>
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="accuracy" fill="#1f6b45" />
              <Bar dataKey="f1" fill="#3d9a66" />
            </BarChart>
          </ResponsiveContainer>
        </div>
        <div className="overflow-auto mt-3">
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left">
                <th>Model</th>
                <th>Accuracy</th>
                <th>Precision</th>
                <th>Recall</th>
                <th>F1</th>
              </tr>
            </thead>
            <tbody>
              {cropRows.map((r) => (
                <tr key={r.name}>
                  <td>{r.name}</td>
                  <td>{Number(r.accuracy).toFixed(4)}</td>
                  <td>{Number(r.precision ?? 0).toFixed(4)}</td>
                  <td>{Number(r.recall ?? 0).toFixed(4)}</td>
                  <td>{Number(r.f1).toFixed(4)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      <div className="grid md:grid-cols-2 gap-4">
        <div className="card">
          <h3 className="font-serif text-xl">Yield comparison (R²)</h3>
          <div className="h-56">
            <ResponsiveContainer>
              <BarChart data={yieldRows}>
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="r2" fill="#3d9a66" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
        <div className="card">
          <h3 className="font-serif text-xl">Market price (R²)</h3>
          <div className="h-56">
            <ResponsiveContainer>
              <BarChart data={priceRows}>
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="r2" fill="#0f3d28" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      <div className="card">
        <h3 className="font-serif text-xl">Confusion matrix / SHAP</h3>
        <div className="grid md:grid-cols-2 gap-3">
          <Figure src="/static/crop_confusion_matrix.png" alt="crop confusion" />
          <Figure src="/static/crop_shap_summary.png" alt="crop shap" />
          <Figure src="/static/yield_shap_summary.png" alt="yield shap" />
          <Figure src="/static/disease_confusion_matrix.png" alt="disease confusion" />
        </div>
      </div>

      {["disease"].map((task) => {
        const rows = curveRows(task);
        const algs = rowsFrom(metrics[`${task}_detection`]?.algorithms, ["accuracy", "precision", "recall", "f1"]);
        return (
          <div key={task} className="card">
            <h3 className="font-serif text-xl capitalize">{task} detection</h3>
            <p className="text-sm text-[#6b5d4d]">{metrics[`${task}_detection`]?.source}</p>
            <div className="grid md:grid-cols-2 gap-3 mt-3">
              <div className="h-44">
                <ResponsiveContainer>
                  <LineChart data={rows}>
                    <XAxis dataKey="epoch" />
                    <YAxis domain={[0, 1]} />
                    <Tooltip />
                    <Line dataKey="train_acc" stroke="#1f6b45" dot={false} />
                    <Line dataKey="val_acc" stroke="#3d9a66" dot={false} />
                  </LineChart>
                </ResponsiveContainer>
              </div>
              <div className="h-44">
                <ResponsiveContainer>
                  <BarChart data={algs}>
                    <XAxis dataKey="name" />
                    <YAxis />
                    <Tooltip />
                    <Bar dataKey="f1" fill="#1f6b45" />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>
            <div className="grid md:grid-cols-2 gap-3 mt-3">
              <Figure src={`/static/${task}_confusion_matrix.png`} alt={`${task} confusion`} />
              <Figure src={`/static/${task}_gradcam_example.png`} alt={`${task} overlay`} />
            </div>
          </div>
        );
      })}
    </div>
  );
}
