import { createContext, useContext, useEffect, useMemo, useState } from "react";
import api from "./api.js";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(() => {
    const raw = localStorage.getItem("user");
    return raw ? JSON.parse(raw) : null;
  });
  const [farm, setFarm] = useState(null);

  async function refreshFarm() {
    if (!localStorage.getItem("token")) return;
    const { data } = await api.get("/farm/mine");
    setFarm(data[0] || null);
  }

  useEffect(() => {
    if (user) refreshFarm().catch(() => {});
  }, [user]);

  const value = useMemo(
    () => ({
      user,
      farm,
      setFarm,
      refreshFarm,
      login: async (email, password) => {
        const { data } = await api.post("/auth/login", { email, password });
        localStorage.setItem("token", data.access_token);
        localStorage.setItem("user", JSON.stringify(data.user));
        setUser(data.user);
        return data.user;
      },
      register: async (payload) => {
        console.log("POST /auth/register payload", payload);
        const { data } = await api.post("/auth/register", payload);
        localStorage.setItem("token", data.access_token);
        localStorage.setItem("user", JSON.stringify(data.user));
        setUser(data.user);
        return data.user;
      },
      logout: () => {
        localStorage.removeItem("token");
        localStorage.removeItem("user");
        setUser(null);
        setFarm(null);
      },
    }),
    [user, farm]
  );
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  return useContext(AuthContext);
}
