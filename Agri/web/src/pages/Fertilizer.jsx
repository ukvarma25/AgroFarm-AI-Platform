import { useState } from "react";
import api from "../api.js";
import { useAuth } from "../AuthContext.jsx";

export default function Fertilizer() {
  const { farm } = useAuth();
  const [form, setForm] = useState({ crop: "rice", N: 20, P: 50, K: 50, ph: 4.8 });
  const [result, setResult] = useState(null);

  async function submit(e) {
    e.preventDefault();
    const { data } = await api.post("/predict/fertilizer-recommendation", { ...form, farm_id: farm?.id });
    setResult(data);
  }

  return (
    <div className="grid md:grid-cols-2 gap-4">
      <form className="card space-y-2" onSubmit={submit}>
        <h2 className="font-serif text-2xl">Fertilizer Recommendation</h2>
        {Object.keys(form).map((key) => (
          <div key={key}>
            <label className="text-sm font-semibold">{key}</label>
            <input value={form[key]} onChange={(e) => setForm({ ...form, [key]: key === "crop" ? e.target.value : Number(e.target.value) })} />
          </div>
        ))}
        <button className="w-full rounded-xl bg-leafdeep text-white py-3 font-bold">Recommend</button>
      </form>
      <div className="card">
        {result ? (
          <>
            <p className="text-sm font-bold text-leaf">{result.label || "Rule-Based — no ML accuracy applicable"}</p>
            <ul className="mt-3 list-disc pl-5 text-sm">
              {(result.recommendations || []).map((r) => (
                <li key={r}>{r}</li>
              ))}
            </ul>
            <h4 className="mt-4 font-semibold">Rule trace</h4>
            {(result.trace || []).map((t) => (
              <p key={t.nutrient} className="text-sm">{t.reason}</p>
            ))}
          </>
        ) : (
          <p className="text-[#6b5d4d]">Rule-based N/P/K/pH thresholds per crop.</p>
        )}
      </div>
    </div>
  );
}
