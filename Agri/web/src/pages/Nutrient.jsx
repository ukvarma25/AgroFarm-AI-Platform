import { useEffect, useState } from "react";
import api from "../api.js";
import { useAuth } from "../AuthContext.jsx";

export default function Nutrient() {
  const { farm } = useAuth();
  const [soil, setSoil] = useState(null);
  const [trace, setTrace] = useState(null);

  useEffect(() => {
    if (!farm) return;
    api.get(`/farm/${farm.id}/soil-data`).then(async ({ data }) => {
      const latest = data[0];
      setSoil(latest);
      if (!latest) return;
      const { data: fert } = await api.post("/predict/fertilizer-recommendation", {
        farm_id: farm.id,
        crop: "rice",
        N: latest.nitrogen,
        P: latest.phosphorus,
        K: latest.potassium,
        ph: latest.ph,
      });
      setTrace(fert);
    });
  }, [farm]);

  return (
    <div className="grid md:grid-cols-2 gap-4">
      <div className="card">
        <h2 className="font-serif text-2xl">Nutrient Analysis</h2>
        {soil ? (
          <ul className="mt-4 space-y-2">
            <li>Nitrogen {soil.nitrogen}</li>
            <li>Phosphorus {soil.phosphorus}</li>
            <li>Potassium {soil.potassium}</li>
            <li>pH {soil.ph}</li>
            <li>Moisture {soil.moisture}</li>
          </ul>
        ) : (
          <p className="text-[#6b5d4d] mt-2">Save a soil record first.</p>
        )}
      </div>
      <div className="card">
        <h3 className="font-serif text-xl">Deficiency trace (rice defaults)</h3>
        <p className="text-sm text-leaf font-semibold mt-1">{trace?.label}</p>
        <ul className="mt-3 space-y-2 text-sm">
          {(trace?.trace || []).map((t) => (
            <li key={t.nutrient} className="rounded-lg bg-straw p-3">
              {t.reason}
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}
