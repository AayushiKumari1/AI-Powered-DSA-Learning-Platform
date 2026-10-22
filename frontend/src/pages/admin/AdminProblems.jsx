import { useMemo, useRef, useState } from "react";
import { Link } from "react-router-dom";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { Code2, ExternalLink, Pencil, Plus, Search, Trash2, Upload } from "lucide-react";
import { api } from "@/lib/api";
import { Button, Card, DifficultyBadge, Empty, ErrorState, Input, Page, PageHeader, PageSkeleton, StatCard } from "@/components/ui";

export default function AdminProblems() {
  const qc = useQueryClient();
  const fileRef = useRef(null);
  const [q, setQ] = useState("");
  const [diff, setDiff] = useState("all");
  const { data, isLoading, error, refetch } = useQuery({ queryKey: ["admin-problems"], queryFn: () => api.get("/api/admin/problems") });
  const del = useMutation({ mutationFn: (id) => api.del(`/api/admin/problems/${id}`), onSuccess: () => { toast.success("Problem deleted"); qc.invalidateQueries({ queryKey: ["admin-problems"] }); }, onError: (e) => toast.error(e.message) });
  const rows = useMemo(() => (data?.problems || []).filter((p) => p.title.toLowerCase().includes(q.toLowerCase()) && (diff === "all" || p.difficulty === diff)), [data, q, diff]);
  async function upload(file) {
    const fd = new FormData(); fd.append("file", file);
    const res = await fetch("/api/admin/problems/upload", { method: "POST", body: fd, credentials: "same-origin" });
    const d = await res.json().catch(() => ({}));
    if (!res.ok) return toast.error(d.error || "Upload failed");
    toast.success(`Imported ${d.added} problem${d.added !== 1 ? "s" : ""}`);
    d.errors?.forEach((e) => toast.error(e));
    qc.invalidateQueries({ queryKey: ["admin-problems"] });
  }
  if (isLoading) return <PageSkeleton />;
  if (error) return <ErrorState error={error} retry={refetch} />;
  const P = data.problems, count = (d) => P.filter((p) => p.difficulty === d).length;
  return (
    <Page>
      <PageHeader title="Problems" subtitle={`${P.length} problems in the practice bank`}>
        <input ref={fileRef} type="file" accept=".csv" hidden onChange={(e) => { if (e.target.files[0]) upload(e.target.files[0]); e.target.value = ""; }} />
        <Button variant="outline" onClick={() => fileRef.current.click()}><Upload /> Import CSV</Button>
        <Button to="/admin/problems/new"><Plus /> New problem</Button>
      </PageHeader>
      <div className="mb-6 grid grid-cols-2 gap-4 md:grid-cols-4">
        <StatCard icon={Code2} label="Total" value={P.length} accent="var(--chart-1)" />
        <StatCard icon={Code2} label="Easy" value={count("easy")} accent="var(--easy)" />
        <StatCard icon={Code2} label="Medium" value={count("medium")} accent="var(--medium)" />
        <StatCard icon={Code2} label="Hard" value={count("hard")} accent="var(--hard)" />
      </div>
      <Card className="overflow-hidden">
        <div className="flex flex-wrap items-center gap-3 border-b border-border px-5 py-4">
          <div className="relative w-full sm:w-72"><Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" /><Input value={q} onChange={(e) => setQ(e.target.value)} placeholder="Filter by title…" className="h-8 bg-background pl-9" aria-label="Filter problems" /></div>
          <div className="flex gap-1.5">{["all", "easy", "medium", "hard"].map((d) => <Button key={d} size="sm" variant={diff === d ? "default" : "outline"} onClick={() => setDiff(d)}>{d[0].toUpperCase() + d.slice(1)}</Button>)}</div>
        </div>
        {rows.length ? <div className="overflow-x-auto"><table className="w-full text-sm">
          <thead><tr className="border-b border-border bg-background/40 text-left text-xs uppercase tracking-wider text-muted-foreground"><th className="h-10 w-14 px-4 font-medium">ID</th><th className="px-4 font-medium">Title</th><th className="px-4 font-medium">Difficulty</th><th className="px-4 text-right font-medium">Test cases</th><th className="px-4 text-right font-medium">Attempts</th><th className="px-4 text-right font-medium">Solved by</th><th className="w-32 px-4" /></tr></thead>
          <tbody>{rows.map((p) => (
            <tr key={p.id} className="border-b border-border last:border-0 hover:bg-muted/40">
              <td className="px-4 py-3 font-mono text-xs text-muted-foreground">{p.id}</td>
              <td className="px-4 py-3"><Link to={`/admin/problems/${p.id}`} className="font-medium hover:text-primary">{p.title}</Link></td>
              <td className="px-4 py-3"><DifficultyBadge difficulty={p.difficulty} /></td>
              <td className="px-4 py-3 text-right tabular-nums">{p.cases}</td>
              <td className="px-4 py-3 text-right tabular-nums">{p.attempts}</td>
              <td className="px-4 py-3 text-right tabular-nums">{p.solved_by}<span className="text-muted-foreground">/{p.learners}</span></td>
              <td className="px-4 py-3"><div className="flex justify-end gap-1">
                <Link to={`/practice/${p.id}`} target="_blank" aria-label="Preview as learner" title="Preview as learner" className="grid h-8 w-8 place-items-center rounded-md text-muted-foreground hover:bg-accent hover:text-foreground"><ExternalLink className="h-4 w-4" /></Link>
                <Link to={`/admin/problems/${p.id}`} aria-label={`Edit ${p.title}`} className="grid h-8 w-8 place-items-center rounded-md text-muted-foreground hover:bg-accent hover:text-foreground"><Pencil className="h-4 w-4" /></Link>
                <button aria-label={`Delete ${p.title}`} onClick={() => confirm(`Delete “${p.title}”? Its submissions and test results will be removed too.`) && del.mutate(p.id)} className="grid h-8 w-8 place-items-center rounded-md text-muted-foreground hover:bg-hard/15 hover:text-hard"><Trash2 className="h-4 w-4" /></button>
              </div></td>
            </tr>))}</tbody>
        </table></div> : <Empty icon={Code2} title="No problems match" />}
      </Card>
    </Page>
  );
}
