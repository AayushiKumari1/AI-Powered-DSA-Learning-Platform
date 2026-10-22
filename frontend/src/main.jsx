import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { BrowserRouter } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { Toaster } from "sonner";
import { AuthProvider } from "@/hooks/useAuth";
import App from "./App";
import "./index.css";

const queryClient = new QueryClient({
  defaultOptions: { queries: { retry: (n, err) => err?.status !== 401 && err?.status !== 404 && n < 1, refetchOnWindowFocus: false } },
});

createRoot(document.getElementById("root")).render(
  <StrictMode>
    <QueryClientProvider client={queryClient}>
      <BrowserRouter basename="/app">
        <AuthProvider>
          <App />
          <Toaster theme="dark" position="bottom-right" richColors closeButton />
        </AuthProvider>
      </BrowserRouter>
    </QueryClientProvider>
  </StrictMode>
);
