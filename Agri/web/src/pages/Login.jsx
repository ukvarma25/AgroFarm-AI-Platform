import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../AuthContext.jsx";

export default function Login() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [errors, setErrors] = useState({});
  const [formError, setFormError] = useState("");

  function validate() {
    const next = {};
    if (!email) next.email = "Email is required";
    else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) next.email = "Enter a valid email";
    if (!password) next.password = "Password is required";
    setErrors(next);
    return Object.keys(next).length === 0;
  }

  async function onSubmit(e) {
    e.preventDefault();
    setFormError("");
    if (!validate()) return;
    try {
      await login(email, password);
      navigate("/");
    } catch (err) {
      setFormError(err.response?.data?.detail || "Login failed");
    }
  }

  return (
    <div className="min-h-screen grid place-items-center px-4">
      <form onSubmit={onSubmit} className="card w-full max-w-md space-y-4">
        <p className="text-xs uppercase tracking-[0.2em] text-leaf font-bold">AgroFarm AI</p>
        <h1 className="font-serif text-3xl">Login</h1>
        <div>
          <label className="text-sm font-semibold">Email</label>
          <input value={email} onChange={(e) => setEmail(e.target.value)} />
          {errors.email && <p className="text-sm text-amber-800 mt-1">{errors.email}</p>}
        </div>
        <div>
          <label className="text-sm font-semibold">Password</label>
          <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} />
          {errors.password && <p className="text-sm text-amber-800 mt-1">{errors.password}</p>}
        </div>
        <button className="w-full rounded-xl bg-leafdeep text-white py-3 font-bold">Login</button>
        {formError && <p className="text-sm text-red-800">{formError}</p>}
        <p className="text-sm">
          <a className="text-leaf" href="#forgot">Forgot password?</a>
        </p>
        <p className="text-sm">
          Don't have an account?{" "}
          <Link className="text-leaf font-semibold" to="/register">
            Register
          </Link>
        </p>
      </form>
    </div>
  );
}
