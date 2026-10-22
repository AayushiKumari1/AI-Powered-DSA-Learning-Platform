import { createContext, useContext, useEffect } from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/api";

const AuthCtx = createContext(null);

export function AuthProvider({ children }) {
  const qc = useQueryClient();
  const q = useQuery({ queryKey: ["me"], queryFn: () => api.get("/api/auth/me"), staleTime: 30_000 });
  useEffect(() => {
    const onUnauth = () => qc.setQueryData(["me"], { user: null });
    window.addEventListener("em:unauthorized", onUnauth);
    return () => window.removeEventListener("em:unauthorized", onUnauth);
  }, [qc]);
  const value = {
    user: q.data?.user ?? null,
    unread: q.data?.unread_notifications ?? 0,
    loading: q.isLoading,
    refresh: () => qc.invalidateQueries({ queryKey: ["me"] }),
    async signOut() { await api.post("/api/auth/logout"); qc.clear(); qc.setQueryData(["me"], { user: null }); },
  };
  return <AuthCtx.Provider value={value}>{children}</AuthCtx.Provider>;
}

export const useAuth = () => useContext(AuthCtx);
