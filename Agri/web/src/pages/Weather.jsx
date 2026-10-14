import { useEffect, useState } from "react";
import api from "../api.js";

export default function Weather() {
  const [data, setData] = useState(null);
  const [error, setError] = useState("");
  useEffect(() => {
    api
      .get("/weather-alert")
      .then(({ data: body }) => setData(body))
      .catch((err) => setError(err.response?.data?.detail || "Weather unavailable"));
  }, []);
  if (error) return <div className="card">{error}</div>;
  if (!data) return <div className="card">Loading weather…</div>;
  return (
    <div className="card">
      <h2 className="font-serif text-2xl">Weather & Risk</h2>
      <p className="font-serif text-5xl mt-2">{Math.round(data.temperature_c)}°C</p>
      <p>{data.description} · source {data.source}</p>
      <ul className="mt-4 space-y-2">
        {data.alerts.map((a) => (
          <li key={a.type} className="rounded-xl bg-straw p-3">{a.message}</li>
        ))}
      </ul>
    </div>
  );
}
