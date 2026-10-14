import { useEffect, useState } from "react";
import api from "../api.js";
import { useAuth } from "../AuthContext.jsx";

export default function Soil() {
  const { farm, refreshFarm } = useAuth();
  const [form, setForm] = useState({
    nitrogen: 90, phosphorus: 42, potassium: 43, ph: 6.5, moisture: 20, temperature: 25, humidity: 70, rainfall: 120,
  });
  const [rows, setRows] = useState([]);

  async function load() {
    if (!farm) return;
    const { data } = await api.get(`/farm/${farm.id}/soil-data`);
    setRows(data);
  }
  useEffect(() => {
    load();
  }, [farm]);

  async function submit(e) {
    e.preventDefault();
    await api.post(`/farm/${farm.id}/soil-data`, form);
    await refreshFarm();
    load();
  }

  return (
    <div className="grid md:grid-cols-2 gap-4">
      <form className="card space-y-2" onSubmit={submit}>
        <h2 className="font-serif text-2xl">Soil Analysis</h2>
        {Object.keys(form).map((key) => (
          <div key={key}>
            <label className="text-sm font-semibold capitalize">{key}</label>
            <input type="number" step="any" value={form[key]} onChange={(e) => setForm({ ...form, [key]: Number(e.target.value) })} />
          </div>
        ))}
        {!farm && <p className="text-sm text-amber-800">Register a farm before saving soil data.</p>}
        <button disabled={!farm} className="w-full rounded-xl bg-leafdeep text-white py-3 font-bold disabled:opacity-50">Save soil record</button>
      </form>
      <div className="card">
        <h3 className="font-serif text-xl">History</h3>
        <ul className="mt-3 space-y-2 text-sm">
          {rows.map((r) => (
            <li key={r.id} className="rounded-lg bg-straw p-3">
              N{r.nitrogen} P{r.phosphorus} K{r.potassium} pH{r.ph}
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}
