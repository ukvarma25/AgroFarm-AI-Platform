import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      "/auth": "http://127.0.0.1:8000",
      "/farm": "http://127.0.0.1:8000",
      "/predict": "http://127.0.0.1:8000",
      "/models": "http://127.0.0.1:8000",
      "/weather-alert": "http://127.0.0.1:8000",
      "/ai-report": "http://127.0.0.1:8000",
      "/chatbot": "http://127.0.0.1:8000",
      "/dashboard": "http://127.0.0.1:8000",
      "/uploads": "http://127.0.0.1:8000",
      "/static": "http://127.0.0.1:8000",
      "/health": "http://127.0.0.1:8000",
    },
  },
});
