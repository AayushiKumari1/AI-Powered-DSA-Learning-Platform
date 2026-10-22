import { useRef, useState } from "react";
import { Link } from "react-router-dom";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { BookOpen, FileSpreadsheet, Pencil, Plus, Search, Trash2, Upload } from "lucide-react";
import { api } from "@/lib/api";
import { Button, Card, Empty, ErrorState, Input, Page, PageHeader, PageSkeleton, Progress } from "@/components/ui";

export default function AdminTopics() {
  const qc = useQueryClient();
  const [q, setQ] = useState("");
  const fileRef = useRef(null);
  const { data, isLoading, error, refetch } = useQuery({ queryKey: ["admin-topics"], queryFn: () => api.get("/api/admin/topics") });
  const del = useMutation({ mutationFn: (id) => api.del(`/api/admin/topics/${id}`), onSuccess: () => { toast.success("Topic deleted"); qc.invalidateQueries({ queryKey: ["admin-topics"] }); }, onError: (e) => toast.error(e.message) });
  async function upload(file) {
    const fd = new FormData(); fd.append("file", file);
    const res = await fetch("/api/admin/topics/upload", { method: "POST", body: fd, credentials: "same-origin" });
    const d = await res.json().catch(() => ({}));
    if (!res.ok) return toast.error(d.error || "Upload failed");
    toast.success(`Imported ${d.added} topic${d.added !== 1 ? "s" : ""}${d.skipped ? `, skipped ${d.skipped} duplicate${d.skipped !== 1 ? "s" : ""}` : ""}`);
    qc.invalidateQueries({ queryKey: ["admin-topics"] });
  }
  if (isLoading) return <PageSkeleton />;
  if (error) return <ErrorState error={error} retry={refetch} />;
  const rows = data.topics.filter((t) => `${t.title} ${t.tags.join(" ")}`.toLowerCase().includes(q.toLowerCase()));
  return (
    <Page>
      <PageHeader title="Topics" subtitle={`${data.topics.length} published · lessons learners study before practising`}>
        <input ref={fileRef} type="file" accept=".csv" hidden onChange={(e) => { if (e.target.files[0]) upload(e.target.files[0]); e.target.value = ""; }} />
        <Button variant="outline" onClick={() => fileRef.current.click()}><Upload /> Import CSV</Button>
        <Button to="/admin/topics/new"><Plus /> New topic</Button>
      </PageHeader>
      <Card className="overflow-hidden">
        <div className="flex flex-wrap items-center gap-3 border-b border-border px-5 py-4">
          <div className="relative w-full sm:w-72"><Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" /><Input value={q} onChange={(e) => setQ(e.target.value)} placeholder="Filter by title or tag…" className="h-8 bg-background pl-9" aria-label="Filter topics" /></div>
          <p className="ml-auto flex items-center gap-1.5 text-xs text-muted-foreground"><FileSpreadsheet className="h-3.5 w-3.5" />CSV columns: title, intro, example, code, details, tags</p>
        </div>
        {rows.length ? <div className="overflow-x-auto"><table className="w-full text-sm">
          <thead><tr className="border-b border-border bg-background/40 text-left text-xs uppercase tracking-wider text-muted-foreground"><th className="h-10 w-14 px-4 font-medium">ID</th><th className="px-4 font-medium">Topic</th><th className="px-4 text-right font-medium">Learners</th><th className="w-48 px-4 font-medium">Completion</th><th className="px-4 text-right font-medium">Study time</th><th className="w-28 px-4" /></tr></thead>
          <tbody>{rows.map((t) => { const rate = t.started ? (t.completed / t.started) * 100 : 0; return (
            <tr key={t.id} className="border-b border-border last:border-0 hover:bg-muted/40">
              <td className="px-4 py-3 font-mono text-xs text-muted-foreground">{t.id}</td>
              <td className="px-4 py-3"><Link to={`/admin/topics/${t.id}`} className="font-medium hover:text-primary">{t.title}</Link><div className="mt-1 flex flex-wrap gap-1">{t.tags.map((g) => <span key={g} className="rounded bg-muted px-1.5 py-0.5 text-[11px] text-muted-foreground">{g}</span>)}</div></td>
              <td className="px-4 py-3 text-right tabular-nums">{t.started}</td>
              <td className="px-4 py-3"><div className="flex items-center gap-2"><Progress value={rate} color="var(--easy)" className="h-1.5" /><span className="w-9 text-right text-xs tabular-nums text-muted-foreground">{Math.round(rate)}%</span></div></td>
              <td className="px-4 py-3 text-right tabular-nums text-muted-foreground">{t.minutes} min</td>
              <td className="px-4 py-3"><div className="flex justify-end gap-1">
                <Link to={`/admin/topics/${t.id}`} aria-label={`Edit ${t.title}`} className="grid h-8 w-8 place-items-center rounded-md text-muted-foreground hover:bg-accent hover:text-foreground"><Pencil className="h-4 w-4" /></Link>
                <button aria-label={`Delete ${t.title}`} onClick={() => confirm(`Delete “${t.title}”? Learner progress for this topic will be removed.`) && del.mutate(t.id)} className="grid h-8 w-8 place-items-center rounded-md text-muted-foreground hover:bg-hard/15 hover:text-hard"><Trash2 className="h-4 w-4" /></button>
              </div></td>
            </tr>); })}</tbody>
        </table></div> : <Empty icon={BookOpen} title={q ? "No topics match" : "No topics yet"} action={<Button size="sm" to="/admin/topics/new">New topic</Button>} />}
      </Card>
    </Page>
  );
}
