import { useEffect, useState } from "react";
import { NavLink, Outlet, useNavigate } from "react-router-dom";
import ChatWidget from "../components/ChatWidget.jsx";
import api from "../api.js";
import { useAuth } from "../AuthContext.jsx";
import { NAV } from "../nav.js";

export default function AppShell() {
  const { user, farm, logout } = useAuth();
  const navigate = useNavigate();
  const [open, setOpen] = useState(false);
  const [query, setQuery] = useState("");
  const [weather, setWeather] = useState(null);
  const [bell, setBell] = useState([]);

  useEffect(() => {
    api
      .get("/weather-alert")
      .then(({ data }) => {
        setWeather(data);
        setBell(data.alerts || []);
      })
      .catch(() => {});
  }, [farm]);

  const filtered = NAV.filter((item) =>
    item.label.toLowerCase().includes(query.toLowerCase())
  );

  return (
    <div className="min-h-screen">
      <aside
        className={`fixed inset-y-0 left-0 z-40 w-64 bg-leafdeep text-white p-4 transition-transform ${
          open ? "translate-x-0" : "-translate-x-full"
        } md:translate-x-0`}
      >
        <p className="text-xs uppercase tracking-[0.2em] text-emerald-200">AgroFarm AI</p>
        <h1 className="font-serif text-2xl mt-1 mb-6">Precision farm</h1>
        <nav className="space-y-1 text-sm">
          {NAV.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.to === "/"}
              onClick={() => setOpen(false)}
              className={({ isActive }) =>
                `block rounded-lg px-3 py-2 ${isActive ? "bg-white/15" : "hover:bg-white/10"}`
              }
            >
              {item.label}
            </NavLink>
          ))}
        </nav>
      </aside>

      <div className="md:pl-64">
        <header className="sticky top-0 z-30 flex items-center gap-3 border-b border-[#d9cbb3] bg-paper/90 px-4 py-3 backdrop-blur">
          <button className="md:hidden rounded-lg border px-3 py-1" onClick={() => setOpen((v) => !v)}>
            Menu
          </button>
          <input
            placeholder="Search pages…"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            className="max-w-sm"
          />
          <div className="ml-auto flex items-center gap-3">
            <div className="relative">
              <span className="text-lg">🔔</span>
              {bell.length > 0 && (
                <span className="absolute -right-1 -top-1 h-4 min-w-4 rounded-full bg-leaf text-[10px] text-white text-center">
                  {bell.length}
                </span>
              )}
            </div>
            <div className="flex items-center gap-2">
              <div className="h-9 w-9 rounded-full bg-leaf text-white grid place-items-center font-bold">
                {(user?.full_name || "F")[0]}
              </div>
              <div className="hidden sm:block text-sm leading-tight">
                <div>Hello, {user?.full_name}</div>
                <div className="text-xs text-[#6b5d4d] capitalize">{user?.role?.replace("_", " ")}</div>
              </div>
            </div>
            <button
              className="text-sm text-[#6b5d4d]"
              onClick={() => {
                logout();
                navigate("/login");
              }}
            >
              Logout
            </button>
          </div>
        </header>

        {query && (
          <div className="px-6 pt-3 text-sm">
            {filtered.map((item) => (
              <NavLink key={item.to} to={item.to} className="mr-3 text-leaf">
                {item.label}
              </NavLink>
            ))}
          </div>
        )}

        <div className="grid xl:grid-cols-[1fr_280px] gap-5 p-5 md:p-6">
          <main>
            <Outlet />
          </main>
          <aside className="card h-fit">
            <p className="text-xs uppercase tracking-widest text-leaf font-bold">Weather & Risk</p>
            {weather ? (
              <>
                <p className="font-serif text-3xl mt-2">{Math.round(weather.temperature_c)}°C</p>
                <p className="text-sm text-[#6b5d4d]">{weather.description}</p>
                <p className="text-xs mt-1">Wind {weather.wind_ms} m/s · Rain {weather.precipitation_mm} mm</p>
                <ul className="mt-3 space-y-2 text-sm">
                  {(weather.alerts || []).map((a) => (
                    <li key={a.type} className="rounded-lg bg-straw px-3 py-2">
                      {a.message}
                    </li>
                  ))}
                </ul>
              </>
            ) : (
              <p className="text-sm text-[#6b5d4d] mt-2">Weather loads after a farm exists.</p>
            )}
          </aside>
        </div>
      </div>
      <ChatWidget />
    </div>
  );
}
