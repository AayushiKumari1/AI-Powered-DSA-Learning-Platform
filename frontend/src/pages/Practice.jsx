import { useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { CheckCircle2, Circle, Search } from "lucide-react";
import { api } from "@/lib/api";
import { Button, Card, DifficultyBadge, ErrorState, Input, Page, PageHeader, PageSkeleton } from "@/components/ui";

export default function Practice() {
  const [q, setQ] = useState("");
  const [diff, setDiff] = useState("all");
  const [status, setStatus] = useState("all");
  const { data, isLoading, error, refetch } = useQuery({ queryKey: ["problems"], queryFn: () => api.get("/api/problems") });
  const rows = useMemo(() => (data?.problems || []).filter((p) =>
    p.title.toLowerCase().includes(q.toLowerCase()) && (diff === "all" || p.difficulty === diff) &&
    (status === "all" || (status === "solved" ? p.solved : status === "attempted" ? !p.solved && p.attempts : !p.attempts))), [data, q, diff, status]);
  if (isLoading) return <PageSkeleton />;
  if (error) return <ErrorState error={error} retry={refetch} />;

  return (
    <Page>
      <PageHeader title="Practice" subtitle={`${data.problems.length} problems · ${data.solved} solved`} />
      <Card className="mb-4 p-4">
        <div className="flex flex-col gap-3 md:flex-row">
          <div className="relative flex-1">
            <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
            <Input value={q} onChange={(e) => setQ(e.target.value)} placeholder="Search problems…" className="border-border bg-background pl-9" aria-label="Search problems" />
          </div>
          <div className="flex flex-wrap gap-1.5">
            {["all", "easy", "medium", "hard"].map((d) => <Button key={d} size="sm" variant={diff === d ? "default" : "outline"} onClick={() => setDiff(d)}>{d === "all" ? "All" : d[0].toUpperCase() + d.slice(1)}</Button>)}
          </div>
        </div>
        <div className="mt-3 flex flex-wrap gap-1.5">
          {[["all", "Any status"], ["todo", "Todo"], ["attempted", "Attempted"], ["solved", "Solved"]].map(([k, l]) => (
            <button key={k} onClick={() => setStatus(k)} className={`rounded-md border px-2 py-0.5 text-xs ${status === k ? "border-primary/40 bg-primary/15 text-primary" : "border-border text-muted-foreground hover:text-foreground"}`}>{l}</button>
          ))}
        </div>
      </Card>
      <Card className="overflow-hidden">
        <div className="hidden grid-cols-[40px_60px_1fr_120px_90px] items-center gap-3 border-b border-border bg-background/40 px-4 py-3 text-xs font-medium uppercase tracking-wider text-muted-foreground md:grid">
          <span>Status</span><span>#</span><span>Title</span><span className="text-right">Reward</span><span className="text-right">Difficulty</span>
        </div>
        {rows.length ? (
          <ul className="divide-y divide-border">
            {rows.map((p) => (
              <li key={p.id}><Link to={`/practice/${p.id}`} className="grid grid-cols-[40px_60px_1fr_90px] items-center gap-3 px-4 py-3 transition-colors hover:bg-muted/40 md:grid-cols-[40px_60px_1fr_120px_90px]">
                {p.solved ? <CheckCircle2 className="h-4 w-4 text-easy" aria-label="Solved" /> : <Circle className={`h-4 w-4 ${p.attempts ? "text-medium/70" : "text-muted-foreground/40"}`} aria-label={p.attempts ? "Attempted" : "Todo"} />}
                <span className="font-mono text-xs text-muted-foreground">{p.id}.</span>
                <span className="min-w-0"><span className="block truncate text-sm font-medium">{p.title}</span>{p.attempts > 0 && <span className="block text-xs text-muted-foreground">{p.attempts} attempt{p.attempts > 1 ? "s" : ""}</span>}</span>
                <span className="hidden text-right text-xs text-muted-foreground md:inline">+{p.xp} XP</span>
                <span className="text-right"><DifficultyBadge difficulty={p.difficulty} /></span>
              </Link></li>
            ))}
          </ul>
        ) : <div className="p-10 text-center text-sm text-muted-foreground">No problems match your filters.</div>}
      </Card>
    </Page>
  );
}
