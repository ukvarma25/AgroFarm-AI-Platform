import { Navigate, Route, Routes } from "react-router-dom";
import { useAuth } from "./AuthContext.jsx";
import AppShell from "./layout/AppShell.jsx";
import Assistant from "./pages/Assistant.jsx";
import Crop from "./pages/Crop.jsx";
import Dashboard from "./pages/Dashboard.jsx";
import Fertilizer from "./pages/Fertilizer.jsx";
import Login from "./pages/Login.jsx";
import ModelEval from "./pages/ModelEval.jsx";
import Nutrient from "./pages/Nutrient.jsx";
import Register from "./pages/Register.jsx";
import Reports from "./pages/Reports.jsx";
import Soil from "./pages/Soil.jsx";
import VisionPage from "./pages/VisionPage.jsx";
import Weather from "./pages/Weather.jsx";
import YieldPage from "./pages/Yield.jsx";

function Guard({ children }) {
  const { user } = useAuth();
  if (!user) return <Navigate to="/login" replace />;
  return children;
}

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />
      <Route
        element={
          <Guard>
            <AppShell />
          </Guard>
        }
      >
        <Route path="/" element={<Dashboard />} />
        <Route path="/crop" element={<Crop />} />
        <Route path="/soil" element={<Soil />} />
        <Route path="/disease" element={<VisionPage task="disease" title="Disease Detection" />} />
        <Route path="/nutrient" element={<Nutrient />} />
        <Route path="/fertilizer" element={<Fertilizer />} />
        <Route path="/yield" element={<YieldPage />} />
        <Route path="/weather" element={<Weather />} />
        <Route path="/assistant" element={<Assistant />} />
        <Route path="/reports" element={<Reports />} />
        <Route path="/evaluation" element={<ModelEval />} />
      </Route>
    </Routes>
  );
}
