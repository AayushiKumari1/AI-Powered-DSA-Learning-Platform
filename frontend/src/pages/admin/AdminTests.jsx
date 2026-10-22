import { useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { ExternalLink, FileCheck2, Plus, Save, Search, Trash2, Users, X, Zap } from "lucide-react";
import { api } from "@/lib/api";
import { cn, fmtDate } from "@/lib/utils";
import { Breadcrumbs, Button, Card, DifficultyBadge, Empty, ErrorState, IconTile, Input, Label, Page, PageHeader, PageSkeleton, Textarea } from "@/components/ui";

export function AdminTests() {
  const qc = useQueryClient();
  const { data, isLoading, error, refetch } = useQuery({ queryKey: ["admin-tests"], queryFn: () => api.get("/api/admin/tests") });
  const del = useMutation({ mutationFn: (id) => api.del(`/api/admin/tests/${id}`), onSuccess: () => { toast.success("Test deleted"); qc.invalidateQueries({ queryKey: ["admin-tests"] }); }, onError: (e) => toast.error(e.message) });
  if (isLoading) return <PageSkeleton />;
  if (error) return <ErrorState error={error} retry={refetch} />;
  return (
    <Page>
      <PageHeader title="Tests" subtitle={`${data.tests.length} proctored coding tests`}><Button to="/admin/tests/new"><Plus /> New test</Button></PageHeader>
      {data.tests.length ? (
        <div className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-3">
          {data.tests.map((t) => (
            <Card key={t.id} className="flex flex-col p-5">
              <div className="mb-3 flex items-center gap-2"><IconTile icon={FileCheck2} color="var(--hard)" /><span className="font-mono text-xs text-muted-foreground">#{t.id}</span><span className="ml-auto text-xs text-muted-foreground">{fmtDate(t.created_at)}</span></div>
              <h2 className="font-semibold">{t.title}</h2>
              <p className="mt-1 line-clamp-2 text-sm text-muted-foreground">{t.description || "No description."}</p>
              <ul className="mt-3 space-y-1.5">{t.questions.map((q) => <li key={q.id} className="flex items-center gap-2 text-xs"><span className="flex-1 truncate">{q.title}</span><DifficultyBadge difficulty={q.difficulty} /></li>)}</ul>
              <div className="mt-4 grid grid-cols-3 gap-2 border-t border-border pt-3 text-center">
                <div><p className="text-xs text-muted-foreground">Takers</p><p className="font-semibold tabular-nums">{t.takers}</p></div>
                <div><p className="text-xs text-muted-foreground">Pass rate</p><p className="font-semibold tabular-nums">{t.pass_rate}%</p></div>
                <div><p className="text-xs text-muted-foreground">Max XP</p><p className="font-semibold tabular-nums">{t.max_xp}</p></div>
              </div>
              <div className="mt-3 flex gap-2">
                <Button variant="outline" size="sm" className="flex-1" to={`/tests/${t.id}`} target="_blank"><ExternalLink /> Preview</Button>
                <Button variant="ghost" size="sm" className="text-hard hover:text-hard" onClick={() => confirm(`Delete “${t.title}”? All learner results for it will be removed.`) && del.mutate(t.id)}><Trash2 /> Delete</Button>
              </div>
            </Card>
          ))}
        </div>
      ) : <Card><Empty icon={FileCheck2} title="No tests yet" text="Bundle problems into a timed, proctored test." action={<Button size="sm" to="/admin/tests/new">New test</Button>} /></Card>}
    </Page>
  );
}

export function AdminTestNew() {
  const navigate = useNavigate();
  const qc = useQueryClient();
  const [f, setF] = useState({ title: "", description: "" });
  const [qids, setQids] = useState([]);
  const [tids, setTids] = useState([]);
  const [q, setQ] = useState("");
  const probs = useQuery({ queryKey: ["admin-problems"], queryFn: () => api.get("/api/admin/problems") });
  const topics = useQuery({ queryKey: ["admin-topics"], queryFn: () => api.get("/api/admin/topics") });
  const save = useMutation({ mutationFn: () => api.post("/api/admin/tests", { ...f, question_ids: qids, topic_ids: tids }), onSuccess: () => { toast.success("Test created"); qc.invalidateQueries({ queryKey: ["admin-tests"] }); navigate("/admin/tests"); }, onError: (e) => toast.error(e.message) });
  const P = probs.data?.problems || [];
  const selected = qids.map((id) => P.find((p) => p.id === id)).filter(Boolean);
  const shown = useMemo(() => P.filter((p) => p.title.toLowerCase().includes(q.toLowerCase())), [P, q]);
  if (probs.isLoading || topics.isLoading) return <PageSkeleton />;
  if (probs.error) return <ErrorState error={probs.error} />;
  const xp = selected.reduce((a, p) => a + ({ easy: 10, medium: 20, hard: 30 }[p.difficulty] || 0), 0);
  const toggle = (arr, set, id) => set(arr.includes(id) ? arr.filter((x) => x !== id) : [...arr, id]);

  return (
    <Page>
      <Breadcrumbs items={[{ label: "Tests", to: "/admin/tests" }, { label: "New test" }]} />
      <PageHeader title="New test" subtitle="Pick the problems learners will solve, in order, and tag the topics it covers." />
      <form onSubmit={(e) => { e.preventDefault(); if (!qids.length) return toast.warning("Select at least one problem."); save.mutate(); }} className="grid grid-cols-1 gap-6 lg:grid-cols-[minmax(0,1fr)_320px]">
        <div className="space-y-6">
          <Card className="space-y-4 p-6">
            <div className="space-y-1.5"><Label htmlFor="tt">Title</Label><Input id="tt" required value={f.title} onChange={(e) => setF({ ...f, title: e.target.value })} placeholder="Week 3 · Graphs & DP" /></div>
            <div className="space-y-1.5"><Label htmlFor="td">Description</Label><Textarea id="td" rows={3} value={f.description} onChange={(e) => setF({ ...f, description: e.target.value })} placeholder="What does this test cover?" /></div>
          </Card>
          <Card className="overflow-hidden">
            <div className="flex flex-wrap items-center gap-3 border-b border-border px-5 py-4"><h2 className="mr-auto font-semibold">Problems</h2>
              <div className="relative w-full sm:w-64"><Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" /><Input value={q} onChange={(e) => setQ(e.target.value)} placeholder="Filter problems…" className="h-8 bg-background pl-9" aria-label="Filter problems" /></div></div>
            <ul className="max-h-[440px] divide-y divide-border overflow-y-auto">
              {shown.map((p) => { const on = qids.includes(p.id); return (
                <li key={p.id}><label className={cn("flex cursor-pointer items-center gap-3 px-5 py-2.5 transition-colors hover:bg-muted/40", on && "bg-primary/10")}>
                  <input type="checkbox" checked={on} onChange={() => toggle(qids, setQids, p.id)} className="h-4 w-4 accent-[var(--primary)]" />
                  <span className="w-8 font-mono text-xs text-muted-foreground">{p.id}.</span><span className="flex-1 truncate text-sm">{p.title}</span><DifficultyBadge difficulty={p.difficulty} />
                </label></li>); })}
            </ul>
          </Card>
          <Card className="p-5"><h2 className="mb-3 font-semibold">Topics covered</h2>
            <div className="flex flex-wrap gap-2">{(topics.data?.topics || []).map((t) => <button type="button" key={t.id} onClick={() => toggle(tids, setTids, t.id)} aria-pressed={tids.includes(t.id)} className={cn("rounded-md border px-2.5 py-1 text-xs transition-colors", tids.includes(t.id) ? "border-primary/60 bg-primary/15 text-primary" : "border-border bg-background/40 hover:border-primary/40")}>{t.title}</button>)}</div>
          </Card>
        </div>
        <aside className="lg:sticky lg:top-20 lg:self-start">
          <Card className="p-5">
            <h2 className="mb-4 font-semibold">Summary</h2>
            <dl className="mb-4 grid grid-cols-3 gap-2 text-center">
              <div className="rounded-md border border-border bg-background/40 p-2"><dt className="text-xs text-muted-foreground">Problems</dt><dd className="font-semibold">{qids.length}</dd></div>
              <div className="rounded-md border border-border bg-background/40 p-2"><dt className="text-xs text-muted-foreground">Max XP</dt><dd className="font-semibold">{xp}</dd></div>
              <div className="rounded-md border border-border bg-background/40 p-2"><dt className="text-xs text-muted-foreground">Minutes</dt><dd className="font-semibold">{qids.length * 10}</dd></div>
            </dl>
            {selected.length ? <ol className="mb-4 space-y-1.5">{selected.map((p, i) => <li key={p.id} className="flex items-center gap-2 text-xs"><span className="font-mono text-muted-foreground">{i + 1}.</span><span className="flex-1 truncate">{p.title}</span><button type="button" aria-label="Remove" onClick={() => toggle(qids, setQids, p.id)} className="text-muted-foreground hover:text-hard"><X className="h-3.5 w-3.5" /></button></li>)}</ol>
              : <p className="mb-4 text-xs text-muted-foreground">Selected problems appear here in test order.</p>}
            <Button type="submit" className="w-full" loading={save.isPending}><Save /> Create test</Button>
          </Card>
        </aside>
      </form>
    </Page>
  );
}
