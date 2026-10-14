import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { Bar, BarChart, Cell, Pie, PieChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import api, { assetUrl } from "../api.js";
import { useAuth } from "../AuthContext.jsx";

const ACTIONS = [
  { to: "/crop", label: "Crop" },
  { to: "/soil", label: "Soil" },
  { to: "/disease", label: "Disease" },
  { to: "/fertilizer", label: "Fertilizer" },
  { to: "/yield", label: "Yield" },
];

export default function Dashboard() {
  const { user, farm } = useAuth();
  const [data, setData] = useState(null);

  useEffect(() => {
    api.get("/dashboard/summary").then(({ data: body }) => setData(body));
  }, [farm]);

  const stats = data?.stats || { total_fields: 0, total_area: 0, crops_grown: 0, soil_health: 0 };
  const health = data?.health || { overall: 70, soil: 70, crop: 70, disease: 70, nutrient: 70 };
  const crop = data?.latest?.["crop-recommendation"];
  const soil = data?.latest_soil;
  const disease = data?.latest?.["disease-detection"];
  const yieldPred = data?.latest?.["yield-prediction"];
  const cropShap = (crop?.explanations || []).slice(0, 6);
  const yieldShap = (yieldPred?.explanations || []).slice(0, 5);
  const yieldHistory = data?.yield_history?.length
    ? data.yield_history
    : yieldPred?.predicted_yield_t_ha != null
      ? [{ at: "latest", yield: yieldPred.predicted_yield_t_ha }]
      : [];

  const ring = [{ name: "health", value: health.overall }, { name: "rest", value: 100 - health.overall }];

  return (
    <div className="space-y-6">
      <section className="rounded-2xl bg-leafdeep text-white px-6 py-8">
        <h2 className="font-serif text-3xl">Hello, {user?.full_name}</h2>
        <p className="mt-1 text-emerald-100">A calm view of fields, soil, and model advice — not a guarantee of what to grow.</p>
        <Link to="/crop" className="inline-block mt-4 rounded-xl bg-white text-leafdeep px-4 py-2 font-bold">
          Run crop recommendation
        </Link>
      </section>

      <section className="grid grid-cols-2 lg:grid-cols-4 gap-3">
        {[
          [stats.total_fields, "Total Fields"],
          [stats.total_area, "Total Area"],
          [stats.crops_grown, "Crops Grown"],
          [`${stats.soil_health}%`, "Soil Health"],
        ].map(([n, l]) => (
          <div key={l} className="card">
            <b className="block text-2xl font-serif">{n}</b>
            <span className="text-sm text-[#6b5d4d]">{l}</span>
          </div>
        ))}
      </section>

      <section className="grid md:grid-cols-2 gap-4">
        <div className="card">
          <h3 className="font-serif text-xl">Farm Snapshot</h3>
          <p className="mt-2 text-sm">Latest crop: <b>{crop?.predicted_crop || "Not run yet"}</b></p>
          <p className="text-sm text-[#6b5d4d]">{crop?.recommendation || "Save soil data to populate this card from the live API."}</p>
          <div className="mt-4 text-sm">
            Soil N/P/K: {soil ? `${soil.N} / ${soil.P} / ${soil.K}` : "No soil record"} · pH {soil?.ph ?? "—"}
          </div>
          {cropShap.length > 0 && (
            <div className="h-40 mt-3">
              <ResponsiveContainer>
                <BarChart data={cropShap} layout="vertical" margin={{ left: 24 }}>
                  <XAxis type="number" />
                  <YAxis type="category" dataKey="feature" width={80} tick={{ fontSize: 11 }} />
                  <Tooltip />
                  <Bar dataKey="shap_value" fill="#1f6b45" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          )}
        </div>
        <div className="card">
          <h3 className="font-serif text-xl">Farm Health Analysis</h3>
          <div className="h-40">
            <ResponsiveContainer>
              <PieChart>
                <Pie data={ring} innerRadius={48} outerRadius={70} dataKey="value" startAngle={90} endAngle={-270}>
                  <Cell fill="#1f6b45" />
                  <Cell fill="#efe6d6" />
                </Pie>
              </PieChart>
            </ResponsiveContainer>
          </div>
          <ul className="text-sm space-y-1">
            {["soil", "crop", "disease", "nutrient"].map((k) => (
              <li key={k} className="flex justify-between capitalize">
                <span>{k} {k === "disease" ? "risk inverted" : "health"}</span>
                <b>{health[k]}%</b>
              </li>
            ))}
          </ul>
        </div>
      </section>

      <section className="card">
        <h3 className="font-serif text-xl">Disease Detection</h3>
        <div className="grid md:grid-cols-1 gap-4 mt-3">
          {[["Disease", disease, null]].map(([label, item, extra]) => (
            <div key={label}>
              <p className="text-xs uppercase tracking-widest text-leaf">{label}</p>
              <div className="grid grid-cols-2 gap-2 mt-1">
                {item?.image_url && <img src={assetUrl(item.image_url)} alt={label} className="h-24 w-full rounded-lg object-cover" />}
                {item?.gradcam_url && <img src={assetUrl(item.gradcam_url)} alt={`${label} overlay`} className="h-24 w-full rounded-lg object-cover" />}
              </div>
              <p className="mt-2 font-semibold">{item?.predicted_class || `No ${label.toLowerCase()} scan yet`}</p>
              <p className="text-sm">
                {item ? `${Math.round((item.confidence || 0) * 100)}%${extra ? ` · ${extra}` : ""}` : ""}
              </p>
            </div>
          ))}
        </div>
      </section>

      <section className="grid md:grid-cols-2 gap-4">
        <div className="card">
          <h3 className="font-serif text-xl">Yield Prediction</h3>
          <p className="font-serif text-4xl mt-2">{yieldPred?.predicted_yield_t_ha ?? "—"}</p>
          <p className="text-sm text-[#6b5d4d]">tons / hectare · {yieldPred?.algorithm || "save soil to run the yield model"}</p>
          {yieldShap.length > 0 && (
            <ul className="mt-2 text-xs text-[#6b5d4d] space-y-1">
              {yieldShap.map((x) => (
                <li key={x.feature}>{x.feature}: {x.shap_value}</li>
              ))}
            </ul>
          )}
          <div className="h-40 mt-3">
            <ResponsiveContainer>
              <BarChart data={yieldHistory}>
                <XAxis dataKey="at" hide={yieldHistory.length < 2} />
                <YAxis />
                <Tooltip />
                <Bar dataKey="yield" fill="#1f6b45" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
        <div className="card">
          <h3 className="font-serif text-xl">Quick Actions</h3>
          <div className="mt-3 flex flex-nowrap justify-between gap-2 overflow-x-auto">
            {ACTIONS.map((a) => (
              <Link key={a.to} to={a.to} className="flex-1 min-w-[4.5rem] text-center rounded-xl bg-straw py-3 text-sm font-semibold">
                {a.label}
              </Link>
            ))}
          </div>
        </div>
      </section>

      <section className="grid md:grid-cols-2 gap-4">
        <div className="card">
          <div className="flex justify-between">
            <h3 className="font-serif text-xl">Recent Alerts</h3>
            <Link to="/weather" className="text-leaf text-sm">View All</Link>
          </div>
          <ul className="mt-2 text-sm space-y-2">
            {(data?.alerts || []).slice(0, 3).map((a, i) => (
              <li key={i}>{a.title} — {a.detail}</li>
            ))}
            {!(data?.alerts || []).length && <li className="text-[#6b5d4d]">No alerts yet.</li>}
          </ul>
        </div>
        <div className="card">
          <div className="flex justify-between">
            <h3 className="font-serif text-xl">Recent Reports</h3>
            <Link to="/reports" className="text-leaf text-sm">View All</Link>
          </div>
          <ul className="mt-2 text-sm space-y-2">
            {(data?.reports || []).slice(0, 3).map((a, i) => (
              <li key={i}>{a.title}</li>
            ))}
            {!(data?.reports || []).length && <li className="text-[#6b5d4d]">No reports yet.</li>}
          </ul>
        </div>
      </section>
    </div>
  );
}
