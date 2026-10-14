import { useEffect, useState } from "react";
import { Bar, BarChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import api from "../api.js";
import { useAuth } from "../AuthContext.jsx";

export default function Crop() {
  const { farm } = useAuth();
  const [form, setForm] = useState({
    N: 90, P: 42, K: 43, temperature: 20.9, humidity: 82, ph: 6.5, rainfall: 202.9,
  });
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!farm) return;
    api.get(`/farm/${farm.id}/soil-data`).then(({ data }) => {
      const soil = data[0];
      if (!soil) return;
      setForm((f) => ({
        ...f,
        N: soil.nitrogen,
        P: soil.phosphorus,
        K: soil.potassium,
        ph: soil.ph,
        temperature: soil.temperature || f.temperature,
        humidity: soil.humidity || f.humidity,
        rainfall: soil.rainfall || f.rainfall,
      }));
    });
  }, [farm]);

  async function submit(e) {
    e.preventDefault();
    setError("");
    try {
      const { data } = await api.post("/predict/crop-recommendation", { ...form, farm_id: farm?.id });
      setResult(data);
    } catch (err) {
      setError(err.response?.data?.detail || "Prediction failed");
    }
  }

  const shap = (result?.explanations || []).slice(0, 7).map((x) => ({
    feature: x.feature,
    shap_value: x.shap_value,
  }));

  return (
    <div className="grid md:grid-cols-2 gap-4">
      <form className="card space-y-2" onSubmit={submit}>
        <h2 className="font-serif text-2xl">Crop Recommendation</h2>
        {Object.keys(form).map((key) => (
          <div key={key}>
            <label className="text-sm font-semibold capitalize">{key}</label>
            <input type="number" step="any" value={form[key]} onChange={(e) => setForm({ ...form, [key]: Number(e.target.value) })} />
          </div>
        ))}
        <button className="w-full rounded-xl bg-leafdeep text-white py-3 font-bold">Recommend</button>
        {error && <p className="text-sm text-red-800">{String(error)}</p>}
      </form>
      <div className="card">
        {result ? (
          <>
            <p className="text-xs uppercase tracking-widest text-leaf">Predicted crop</p>
            <h3 className="font-serif text-4xl uppercase">{result.predicted_crop}</h3>
            <p className="mt-2">{result.recommendation}</p>
            <div className="h-48 mt-4">
              <ResponsiveContainer>
                <BarChart data={result.top_k || []}>
                  <XAxis dataKey="crop" />
                  <YAxis />
                  <Tooltip />
                  <Bar dataKey="probability" fill="#1f6b45" />
                </BarChart>
              </ResponsiveContainer>
            </div>
            <h4 className="mt-4 font-semibold">SHAP factors</h4>
            {shap.length ? (
              <div className="h-48">
                <ResponsiveContainer>
                  <BarChart data={shap} layout="vertical" margin={{ left: 48 }}>
                    <XAxis type="number" />
                    <YAxis type="category" dataKey="feature" width={80} />
                    <Tooltip />
                    <Bar dataKey="shap_value" fill="#3d9a66" />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            ) : (
              <p className="text-sm text-[#6b5d4d]">No SHAP values for this run (tree explainer unavailable).</p>
            )}
            <p className="text-xs text-[#6b5d4d] mt-4">{result.disclaimer}</p>
          </>
        ) : (
          <p className="text-[#6b5d4d]">Submit field values to see ranking and SHAP bars.</p>
        )}
      </div>
    </div>
  );
}
