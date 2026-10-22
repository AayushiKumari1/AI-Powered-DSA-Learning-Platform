import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";
import path from "node:path";

// Flask runs on :5000. In dev, Vite serves the React app on :5173/app/ and
// forwards every backend path (JSON API, existing JSON routes, Socket.IO) to Flask,
// so the session cookie is shared and no CORS setup is needed.
const FLASK = "http://127.0.0.1:5000";
const backend = ["/api", "/coding/run", "/coding/submit", "/coding/delete_submission", "/study",
  "/coding-tests/submit-result", "/badges/equip", "/badges/unequip", "/chat/chatbot"];

export default defineConfig({
  base: "/app/",
  plugins: [react(), tailwindcss()],
  resolve: { alias: { "@": path.resolve(import.meta.dirname, "src") } },
  server: {
    port: 5173,
    proxy: {
      ...Object.fromEntries(backend.map((p) => [p, { target: FLASK, changeOrigin: false }])),
      "/socket.io": { target: FLASK, ws: true },
    },
  },
  build: { outDir: "dist", emptyOutDir: true, chunkSizeWarningLimit: 1500 },
});
