import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../AuthContext.jsx";

const ROLES = [
  { value: "farmer", label: "Farmer" },
  { value: "agri_officer", label: "Agri Officer" },
  { value: "fertilizer_dealer", label: "Fertilizer Dealer" },
  { value: "admin", label: "Admin" },
];
const SOILS = ["Alluvial", "Black", "Red", "Laterite", "Arid", "Mountain", "Other"];

const empty = {
  full_name: "",
  email: "",
  phone: "",
  password: "",
  confirm_password: "",
  role: "farmer",
  farm_name: "",
  farm_location: "",
  land_size_acres: "",
  soil_type: "Alluvial",
  lat: null,
  lng: null,
};

export default function Register() {
  const { register } = useAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState(empty);
  const [errors, setErrors] = useState({});
  const [formError, setFormError] = useState("");

  function set(key, value) {
    setForm((f) => ({ ...f, [key]: value }));
  }

  function validate() {
    const next = {};
    const required = [
      "full_name",
      "email",
      "phone",
      "password",
      "confirm_password",
      "farm_name",
      "farm_location",
      "land_size_acres",
    ];
    required.forEach((key) => {
      if (!String(form[key] || "").trim()) next[key] = "This field is required";
    });
    if (form.email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.email)) next.email = "Enter a valid email";
    if (form.phone && !/^\d{10}$/.test(String(form.phone).replace(/\D/g, ""))) next.phone = "Phone must be 10 digits";
    if (form.password && form.password.length < 8) next.password = "Minimum 8 characters";
    if (form.password !== form.confirm_password) next.confirm_password = "Passwords must match";
    setErrors(next);
    return Object.keys(next).length === 0;
  }

  async function onSubmit(e) {
    e.preventDefault();
    setFormError("");
    if (!validate()) return;
    const payload = {
      ...form,
      land_size_acres: Number(form.land_size_acres),
    };
    try {
      await register(payload);
      navigate("/");
    } catch (err) {
      const detail = err.response?.data?.detail;
      setFormError(typeof detail === "string" ? detail : "Registration failed");
    }
  }

  function useLocation() {
    if (!navigator.geolocation) return;
    navigator.geolocation.getCurrentPosition((pos) => {
      set("lat", pos.coords.latitude);
      set("lng", pos.coords.longitude);
      if (!form.farm_location) {
        set("farm_location", `${pos.coords.latitude.toFixed(4)}, ${pos.coords.longitude.toFixed(4)}`);
      }
    });
  }

  const field = (key, label, props = {}) => (
    <div>
      <label className="text-sm font-semibold">{label}</label>
      <input
        value={form[key]}
        onChange={(e) => set(key, e.target.value)}
        {...props}
      />
      {errors[key] && <p className="text-sm text-amber-800 mt-1">{errors[key]}</p>}
    </div>
  );

  return (
    <div className="min-h-screen grid place-items-center px-4 py-8">
      <form onSubmit={onSubmit} className="card w-full max-w-md space-y-3">
        <p className="text-xs uppercase tracking-[0.2em] text-leaf font-bold">AgroFarm AI</p>
        <h1 className="font-serif text-3xl">Register</h1>
        {field("full_name", "Full Name")}
        {field("email", "Email", { type: "email" })}
        {field("phone", "Phone Number")}
        {field("password", "Password", { type: "password" })}
        {field("confirm_password", "Confirm Password", { type: "password" })}
        <div>
          <label className="text-sm font-semibold">Role</label>
          <select value={form.role} onChange={(e) => set("role", e.target.value)}>
            {ROLES.map((r) => (
              <option key={r.value} value={r.value}>
                {r.label}
              </option>
            ))}
          </select>
        </div>
        {field("farm_name", "Farm Name")}
        <div>
          <label className="text-sm font-semibold">Farm Location</label>
          <input value={form.farm_location} onChange={(e) => set("farm_location", e.target.value)} />
          <button type="button" className="mt-2 text-sm text-leaf" onClick={useLocation}>
            Use current location
          </button>
          {errors.farm_location && <p className="text-sm text-amber-800 mt-1">{errors.farm_location}</p>}
        </div>
        {field("land_size_acres", "Land Size (acres)", { type: "number", step: "any" })}
        <div>
          <label className="text-sm font-semibold">Soil Type</label>
          <select value={form.soil_type} onChange={(e) => set("soil_type", e.target.value)}>
            {SOILS.map((s) => (
              <option key={s}>{s}</option>
            ))}
          </select>
        </div>
        <button className="w-full rounded-xl bg-leafdeep text-white py-3 font-bold">Register</button>
        {formError && <p className="text-sm text-red-800">{formError}</p>}
        <p className="text-sm">
          Already have an account?{" "}
          <Link className="text-leaf font-semibold" to="/login">
            Login
          </Link>
        </p>
      </form>
    </div>
  );
}
