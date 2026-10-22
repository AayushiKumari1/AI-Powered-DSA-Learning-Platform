import { useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { toast } from "sonner";
import { ChevronsUpDown, Download, MessageCircle, Search, Users } from "lucide-react";
import { api } from "@/lib/api";
import { initials, timeAgo } from "@/lib/utils";
import { Button, Card, Empty, ErrorState, Input, Page, PageHeader, PageSkeleton, StatCard } from "@/components/ui";

const COLS = [["username", "Learner"], ["xp", "XP"], ["completed_topics", "Topics"], ["solved", "Solved"], ["acceptance", "Acceptance"], ["minutes", "Study time"], ["last_active", "Last active"]];

export default function AdminLearners() {
  const [q, setQ] = useState("");
  const [sort, setSort] = useState({ key: "xp", dir: "desc" });
  const { data, isLoading, error, refetch } = useQuery({ queryKey: ["admin-learners"], queryFn: () => api.get("/api/admin/learners") });
  const rows = useMemo(() => {
    const r = (data?.learners || []).filter((l) => `${l.username} ${l.email}`.toLowerCase().includes(q.toLowerCase()));
    return [...r].sort((a, b) => { const x = a[sort.key] ?? "", y = b[sort.key] ?? ""; return (x > y ? 1 : x < y ? -1 : 0) * (sort.dir === "asc" ? 1 : -1); });
  }, [data, q, sort]);
  if (isLoading) return <PageSkeleton />;
  if (error) return <ErrorState error={error} retry={refetch} />;
  const L = data.learners;
  const avg = (k) => (L.length ? Math.round(L.reduce((a, l) => a + l[k], 0) / L.length) : 0);
  function exportCsv() {
    const lines = ["Username,Email,XP,Topics completed,Problems solved,Submissions,Acceptance %,Study minutes,Joined,Last active",
      ...L.map((l) => [l.username, l.email, l.xp, l.completed_topics, l.solved, l.submissions, l.acceptance, l.minutes, l.joined, l.last_active || ""].join(","))];
    const a = Object.assign(document.createElement("a"), { href: URL.createObjectURL(new Blob([lines.join("\n")], { type: "text/csv" })), download: "edumentor-learners.csv" });
    a.click(); toast.success("Exported learners");
  }
  return (
    <Page>
      <PageHeader title="Learners" subtitle={`${L.length} registered learners`}><Button variant="outline" size="sm" onClick={exportCsv}><Download /> Export CSV</Button></PageHeader>
      <div className="mb-6 grid grid-cols-2 gap-4 md:grid-cols-4">
        <StatCard icon={Users} label="Learners" value={L.length} accent="var(--chart-1)" />
        <StatCard icon={Users} label="Average XP" value={avg("xp")} accent="var(--medium)" />
        <StatCard icon={Users} label="Avg problems solved" value={avg("solved")} accent="var(--easy)" />
        <StatCard icon={Users} label="Avg acceptance" value={`${avg("acceptance")}%`} accent="var(--chart-5)" />
      </div>
      <Card className="overflow-hidden">
        <div className="flex flex-wrap items-center gap-3 border-b border-border px-5 py-4">
          <h2 className="mr-auto text-sm font-semibold">All learners</h2>
          <div className="relative w-full sm:w-64"><Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" /><Input value={q} onChange={(e) => setQ(e.target.value)} placeholder="Search name or email…" className="h-8 bg-background pl-9" aria-label="Search learners" /></div>
        </div>
        {rows.length ? (
          <div className="overflow-x-auto"><table className="w-full text-sm">
            <thead><tr className="border-b border-border bg-background/40 text-left text-xs uppercase tracking-wider text-muted-foreground">
              <th className="h-10 w-10 px-4 font-medium">#</th>
              {COLS.map(([k, l]) => <th key={k} className={`px-4 font-medium ${k !== "username" ? "text-right" : ""}`}><button onClick={() => setSort((s) => ({ key: k, dir: s.key === k && s.dir === "desc" ? "asc" : "desc" }))} className="inline-flex items-center gap-1 uppercase hover:text-foreground">{l}<ChevronsUpDown className="h-3 w-3" /></button></th>)}
              <th className="w-12 px-4" />
            </tr></thead>
            <tbody>{rows.map((l, i) => (
              <tr key={l.id} className="border-b border-border last:border-0 hover:bg-muted/40">
                <td className="px-4 py-3 font-mono text-xs text-muted-foreground">{i + 1}</td>
                <td className="px-4 py-3"><Link to={`/admin/learners/${l.id}`} className="flex items-center gap-2.5">
                  <span className="grid h-8 w-8 shrink-0 place-items-center rounded-full bg-gradient-to-br from-primary to-chart-5 text-xs font-semibold text-primary-foreground">{initials(l.username)}</span>
                  <span className="min-w-0"><span className="block truncate font-medium hover:text-primary">{l.username} {l.badge && <span title={l.badge.name}>{l.badge.icon}</span>}</span><span className="block truncate text-xs text-muted-foreground">{l.email}</span></span>
                </Link></td>
                <td className="px-4 py-3 text-right font-semibold tabular-nums">{l.xp}</td>
                <td className="px-4 py-3 text-right tabular-nums">{l.completed_topics}</td>
                <td className="px-4 py-3 text-right tabular-nums">{l.solved}</td>
                <td className="px-4 py-3 text-right tabular-nums">{l.acceptance}%</td>
                <td className="px-4 py-3 text-right tabular-nums text-muted-foreground">{l.minutes} min</td>
                <td className="px-4 py-3 text-right text-xs text-muted-foreground">{l.last_active ? timeAgo(l.last_active) : "—"}</td>
                <td className="px-4 py-3"><Link to={`/admin/inbox?user=${l.id}`} title="Message" aria-label={`Message ${l.username}`} className="grid h-8 w-8 place-items-center rounded-md text-muted-foreground hover:bg-accent hover:text-foreground"><MessageCircle className="h-4 w-4" /></Link></td>
              </tr>))}</tbody>
          </table></div>
        ) : <Empty icon={Search} title="No learners match" />}
      </Card>
    </Page>
  );
}
