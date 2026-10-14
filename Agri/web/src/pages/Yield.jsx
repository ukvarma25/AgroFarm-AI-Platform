import { useState } from "react";
import { Bar, BarChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import api from "../api.js";
import { useAuth } from "../AuthContext.jsx";

export default function YieldPage() {
  const { farm } = useAuth();
  const [form, setForm] = useState({
    Region: "South",
    Soil_Type: "Clay",
    Crop: "Rice",
    Rainfall_mm: 992,
    Temperature_Celsius: 18,
    Fertilizer_Used: true,
    Irrigation_Used: true,
    Weather_Condition: "Rainy",
    Days_to_Harvest: 140,
  });
  const [price, setPrice] = useState({ crop: "Rice", season: "Kharif", region: "Karnataka", quantity: 10 });
  const [result, setResult] = useState(null);
  const [priceResult, setPriceResult] = useState(null);

  async function submit(e) {
    e.preventDefault();
    const { data } = await api.post("/predict/yield-prediction", { ...form, farm_id: farm?.id });
    setResult(data);
  }
  async function submitPrice(e) {
    e.preventDefault();
    const { data } = await api.post("/predict/market-price", { ...price, farm_id: farm?.id });
    setPriceResult(data);
  }

  const shap = (result?.explanations || []).slice(0, 8);

  return (
    <div className="grid md:grid-cols-2 gap-4">
      <form className="card space-y-2" onSubmit={submit}>
        <h2 className="font-serif text-2xl">Yield Prediction</h2>
        {Object.entries(form).map(([key, value]) => (
          <div key={key}>
            <label className="text-sm font-semibold">{key}</label>
            {typeof value === "boolean" ? (
              <select value={String(value)} onChange={(e) => setForm({ ...form, [key]: e.target.value === "true" })}>
                <option value="true">true</option>
                <option value="false">false</option>
              </select>
            ) : (
              <input value={value} onChange={(e) => setForm({ ...form, [key]: typeof value === "number" ? Number(e.target.value) : e.target.value })} />
            )}
          </div>
        ))}
        <button className="w-full rounded-xl bg-leafdeep text-white py-3 font-bold">Predict yield</button>
        {result && (
          <div className="pt-2">
            <p className="font-serif text-4xl">{result.predicted_yield_t_ha}</p>
            <p className="text-sm">{result.algorithm} · tons / hectare</p>
            {shap.length > 0 && (
              <div className="h-48 mt-3">
                <ResponsiveContainer>
                  <BarChart data={shap} layout="vertical" margin={{ left: 24 }}>
                    <XAxis type="number" />
                    <YAxis type="category" dataKey="feature" width={110} tick={{ fontSize: 10 }} />
                    <Tooltip />
                    <Bar dataKey="shap_value" fill="#1f6b45" />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            )}
          </div>
        )}
      </form>
      <form className="card space-y-2" onSubmit={submitPrice}>
        <h2 className="font-serif text-2xl">Market Price</h2>
        {Object.keys(price).map((key) => (
          <div key={key}>
            <label className="text-sm font-semibold">{key}</label>
            <input value={price[key]} onChange={(e) => setPrice({ ...price, [key]: key === "quantity" ? Number(e.target.value) : e.target.value })} />
          </div>
        ))}
        <button className="w-full rounded-xl bg-leafdeep text-white py-3 font-bold">Predict price</button>
        {priceResult && (
          <p className="font-serif text-3xl mt-2">
            {priceResult.predicted_price} {priceResult.currency}
            <span className="block text-sm font-sans font-normal text-[#6b5d4d]">{priceResult.algorithm}</span>
          </p>
        )}
      </form>
    </div>
  );
}
