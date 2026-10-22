import { useQuery, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/api";

export function useAdmin() {
  const qc = useQueryClient();
  const q = useQuery({ queryKey: ["admin-me"], queryFn: () => api.get("/api/admin/me"), staleTime: 30_000 });
  return {
    isAdmin: !!q.data?.admin,
    loading: q.isLoading,
    async signOut() { await api.post("/api/admin/logout"); qc.removeQueries({ predicate: (x) => String(x.queryKey[0]).startsWith("admin") }); qc.setQueryData(["admin-me"], { admin: false }); },
  };
}
