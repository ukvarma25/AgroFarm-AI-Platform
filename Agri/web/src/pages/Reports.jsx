import { useEffect, useState } from "react";
import api, { assetUrl } from "../api.js";

function Section({ title, children }) {
  return (
    <section className="rounded-xl bg-straw p-4">
      <h3 className="font-serif text-xl">{title}</h3>
      <div className="mt-3">{children}</div>
    </section>
  );
}

function Value({ label, value }) {
  return (
    <div>
      <p className="text-xs uppercase tracking-widest text-leaf">{label}</p>
      <p className="mt-1 font-semibold">{value ?? "Not available"}</p>
    </div>
  );
}

export default function Reports() {
  const [report, setReport] = useState(null);
  const [error, setError] = useState("");
  useEffect(() => {
    api
      .get("/ai-report")
      .then(({ data }) => setReport(data))
      .catch((err) => setError(err.response?.data?.detail || "Could not build report"));
  }, []);
  if (error) return <div className="card">{error}</div>;
  if (!report) return <div className="card">Building report…</div>;
  const soil = report.latest_soil;
  const crop = report.crop_recommendation || {};
  const yieldResult = report.yield_prediction || {};
  const fertilizer = report.fertilizer_recommendation || {};
  const disease = report.disease_result || {};
  const weather = report.weather_alert || {};
  const refs = report.shap_or_gradcam_refs || {};

  return (
    <div className="card space-y-4">
      <div>
        <p className="text-xs uppercase tracking-widest text-leaf">Farm summary</p>
        <h2 className="font-serif text-3xl">AI Report</h2>
        <p className="mt-1 text-sm text-[#6b5d4d]">
          A plain-language summary of your latest soil, model, disease, fertilizer, and weather data.
        </p>
      </div>

      <Section title="Farm">
        <div className="grid sm:grid-cols-3 gap-4">
          <Value label="Farmer" value={report.farmer?.name} />
          <Value label="Farm" value={report.farm?.name} />
          <Value label="Land" value={`${report.farm?.land_size_acres ?? "—"} acres`} />
          <Value label="Location" value={report.farm?.location} />
          <Value label="Soil type" value={report.farm?.soil_type} />
        </div>
      </Section>

      <Section title="Latest soil reading">
        {soil ? (
          <div className="grid grid-cols-2 sm:grid-cols-5 gap-4">
            <Value label="Nitrogen" value={soil.N} />
            <Value label="Phosphorus" value={soil.P} />
            <Value label="Potassium" value={soil.K} />
            <Value label="pH" value={soil.ph} />
            <Value label="Temperature" value={`${soil.temperature ?? "—"} °C`} />
          </div>
        ) : <p className="text-sm text-[#6b5d4d]">No soil reading has been saved yet.</p>}
      </Section>

      <div className="grid md:grid-cols-2 gap-4">
        <Section title="Crop recommendation">
          <p className="font-serif text-3xl capitalize">{crop.predicted_crop || "Not available"}</p>
          <p className="mt-2 text-sm">{crop.recommendation || "Run a soil analysis to generate a recommendation."}</p>
          {crop.confidence != null && <p className="mt-2 text-sm font-semibold">Confidence: {Math.round(crop.confidence * 100)}%</p>}
        </Section>
        <Section title="Yield prediction">
          <p className="font-serif text-3xl">{yieldResult.predicted_yield_t_ha ?? "—"}</p>
          <p className="text-sm text-[#6b5d4d]">tons per hectare · {yieldResult.algorithm || "No prediction yet"}</p>
        </Section>
      </div>

      <Section title="Fertilizer recommendation">
        <p className="font-semibold">{fertilizer.primary_action || "No recommendation yet"}</p>
        <p className="mt-1 text-sm text-[#6b5d4d]">{fertilizer.label || "Rule-based guidance"}</p>
        {fertilizer.recommendations?.length > 0 && (
          <ul className="mt-2 list-disc pl-5 text-sm space-y-1">
            {fertilizer.recommendations.map((item, index) => <li key={index}>{item}</li>)}
          </ul>
        )}
      </Section>

      <Section title="Disease detection">
        {disease.predicted_class ? (
          <div className="grid md:grid-cols-2 gap-4">
            <div>
              <p className="font-semibold capitalize">{disease.predicted_class}</p>
              <p className="text-sm">Confidence: {Math.round((disease.confidence || 0) * 100)}%</p>
              {disease.explanation && <p className="mt-2 text-sm text-[#6b5d4d]">{disease.explanation}</p>}
            </div>
            {disease.gradcam_url && <img src={assetUrl(disease.gradcam_url)} alt="Disease analysis overlay" className="max-h-48 rounded-lg object-contain" />}
          </div>
        ) : <p className="text-sm text-[#6b5d4d]">No disease image has been analyzed yet.</p>}
      </Section>

      <Section title="Weather and risk">
        <p className="font-semibold">{weather.description || "Weather unavailable"}</p>
        <p className="mt-1 text-sm">{weather.temperature_c ?? "—"} °C · Wind {weather.wind_ms ?? "—"} m/s · Rain {weather.precipitation_mm ?? "—"} mm</p>
        <ul className="mt-2 text-sm space-y-1">{(weather.alerts || []).map((alert) => <li key={alert.type}>{alert.message}</li>)}</ul>
      </Section>

      {(refs.crop?.length || refs.yield?.length) && (
        <Section title="How the models reached these results">
          <p className="text-sm text-[#6b5d4d]">The crop and yield models expose their strongest contributing features in the dashboard charts.</p>
          <div className="mt-2 flex gap-3 text-sm font-semibold">
            {refs.crop?.length > 0 && <span>Crop explanation available</span>}
            {refs.yield?.length > 0 && <span>Yield explanation available</span>}
          </div>
        </Section>
      )}
    </div>
  );
}
