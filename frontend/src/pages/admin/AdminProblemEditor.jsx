import { useEffect, useMemo, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { CheckCircle2, Eye, Plus, Save, Trash2, XCircle } from "lucide-react";
import { api } from "@/lib/api";
import { cn } from "@/lib/utils";
import { Breadcrumbs, Button, Card, ErrorState, Input, Label, Page, PageHeader, PageSkeleton, Tabs, Textarea } from "@/components/ui";

const EMPTY = { title: "", difficulty: "easy", description: "", sample_input: "", sample_output: "", test_cases: "[\n  {\"input\": \"\", \"output\": \"\"}\n]" };

export default function AdminProblemEditor() {
  const { id } = useParams();
  const isNew = !id || id === "new";
  const navigate = useNavigate();
  const qc = useQueryClient();
  const [f, setF] = useState(EMPTY);
  const [view, setView] = useState("edit");
  const { data, isLoading, error } = useQuery({ queryKey: ["admin-problem", id], queryFn: () => api.get(`/api/admin/problems/${id}`), enabled: !isNew });
  useEffect(() => { if (data) setF({ ...EMPTY, ...data.problem }); }, [data]);
  const cases = useMemo(() => { try { const c = JSON.parse(f.test_cases); return Array.isArray(c) && c.length && c.every((x) => x && "input" in x && "output" in x) ? c : null; } catch { return null; } }, [f.test_cases]);
  const save = useMutation({
    mutationFn: () => isNew ? api.post("/api/admin/problems", f) : api.put(`/api/admin/problems/${id}`, f),
    onSuccess: () => { toast.success(isNew ? "Problem published" : "Problem saved"); qc.invalidateQueries({ queryKey: ["admin-problems"] }); navigate("/admin/problems"); },
    onError: (e) => toast.error(e.message),
  });
  const set = (k) => (e) => setF({ ...f, [k]: e.target.value });
  const editCase = (i, k, v) => { const c = [...cases]; c[i] = { ...c[i], [k]: v }; setF({ ...f, test_cases: JSON.stringify(c, null, 2) }); };
  if (!isNew && isLoading) return <PageSkeleton />;
  if (error) return <ErrorState error={error} />;

  return (
    <Page className="max-w-5xl">
      <Breadcrumbs items={[{ label: "Problems", to: "/admin/problems" }, { label: isNew ? "New problem" : f.title || "Edit" }]} />
      <PageHeader title={isNew ? "New problem" : "Edit problem"} subtitle="Learners see the description and example; hidden test cases decide pass or fail.">
        <Tabs value={view} onChange={setView} items={[{ value: "edit", label: "Edit" }, { value: "preview", label: "Preview", icon: Eye }]} />
      </PageHeader>
      <form onSubmit={(e) => { e.preventDefault(); if (!cases) return toast.error("Fix the test case JSON first."); save.mutate(); }} className="space-y-4">
        {view === "edit" ? (<>
          <Card className="space-y-5 p-6">
            <div className="grid gap-4 sm:grid-cols-[1fr_200px]">
              <div className="space-y-1.5"><Label htmlFor="t">Title</Label><Input id="t" required value={f.title} onChange={set("title")} placeholder="Arrays: Two Sum" /><p className="text-xs text-muted-foreground">Start with a topic name (Arrays, Stack, Graphs…) so the ML model can map it.</p></div>
              <div className="space-y-1.5"><Label htmlFor="d">Difficulty</Label>
                <div className="grid grid-cols-3 gap-1 rounded-lg bg-muted p-1">{["easy", "medium", "hard"].map((d) => <button type="button" key={d} onClick={() => setF({ ...f, difficulty: d })} className={cn("rounded-md py-1 text-xs font-medium capitalize", f.difficulty === d ? { easy: "bg-easy/20 text-easy", medium: "bg-medium/20 text-medium", hard: "bg-hard/20 text-hard" }[d] : "text-muted-foreground")}>{d}</button>)}</div>
                <p className="text-xs text-muted-foreground">+{{ easy: 10, medium: 20, hard: 30 }[f.difficulty]} XP when solved</p></div>
            </div>
            <div className="space-y-1.5"><Label htmlFor="desc">Problem statement (HTML allowed)</Label><Textarea id="desc" rows={8} required value={f.description} onChange={set("description")} placeholder="<p>Describe the task…</p><h4>Input</h4><p>…</p><h4>Output</h4><p>…</p>" className="font-mono text-xs" /></div>
            <div className="grid gap-4 sm:grid-cols-2">
              <div className="space-y-1.5"><Label htmlFor="si">Sample input</Label><Textarea id="si" rows={4} spellCheck={false} className="font-mono text-xs" value={f.sample_input} onChange={set("sample_input")} /></div>
              <div className="space-y-1.5"><Label htmlFor="so">Sample output</Label><Textarea id="so" rows={4} spellCheck={false} className="font-mono text-xs" value={f.sample_output} onChange={set("sample_output")} /></div>
            </div>
          </Card>
          <Card className="p-6">
            <div className="mb-3 flex items-center justify-between">
              <div><h2 className="font-semibold">Hidden test cases</h2><p className="text-xs text-muted-foreground">Outputs are compared after trimming whitespace.</p></div>
              <span className={cn("flex items-center gap-1.5 text-xs", cases ? "text-easy" : "text-hard")}>{cases ? <><CheckCircle2 className="h-3.5 w-3.5" />{cases.length} valid case{cases.length !== 1 ? "s" : ""}</> : <><XCircle className="h-3.5 w-3.5" />Invalid JSON</>}</span>
            </div>
            {cases ? (
              <div className="space-y-3">
                {cases.map((c, i) => (
                  <div key={i} className="grid gap-2 rounded-lg border border-border bg-background/40 p-3 sm:grid-cols-[1fr_1fr_auto]">
                    <div><p className="mb-1 text-xs text-muted-foreground">Case {i + 1} · input</p><Textarea rows={3} spellCheck={false} className="font-mono text-xs" value={c.input} onChange={(e) => editCase(i, "input", e.target.value)} /></div>
                    <div><p className="mb-1 text-xs text-muted-foreground">Expected output</p><Textarea rows={3} spellCheck={false} className="font-mono text-xs" value={c.output} onChange={(e) => editCase(i, "output", e.target.value)} /></div>
                    <button type="button" aria-label={`Remove case ${i + 1}`} disabled={cases.length === 1} onClick={() => setF({ ...f, test_cases: JSON.stringify(cases.filter((_, j) => j !== i), null, 2) })} className="self-center rounded-md p-2 text-muted-foreground hover:bg-hard/15 hover:text-hard disabled:opacity-30"><Trash2 className="h-4 w-4" /></button>
                  </div>
                ))}
                <Button type="button" variant="outline" size="sm" onClick={() => setF({ ...f, test_cases: JSON.stringify([...cases, { input: "", output: "" }], null, 2) })}><Plus /> Add test case</Button>
              </div>
            ) : <Textarea rows={10} spellCheck={false} className="font-mono text-xs" value={f.test_cases} onChange={set("test_cases")} />}
            {cases && <details className="mt-4"><summary className="cursor-pointer text-xs text-muted-foreground hover:text-foreground">Edit as raw JSON</summary><Textarea rows={8} spellCheck={false} className="mt-2 font-mono text-xs" value={f.test_cases} onChange={set("test_cases")} /></details>}
          </Card>
        </>) : (
          <Card className="p-6">
            <h2 className="mb-1 text-xl font-semibold">{f.title || "Untitled problem"}</h2><p className="mb-4 text-xs capitalize text-muted-foreground">{f.difficulty}</p>
            <div className="prose-dark" dangerouslySetInnerHTML={{ __html: f.description }} />
            <div className="mt-4 rounded-md border border-border bg-background/40 p-3 font-mono text-xs"><p className="text-muted-foreground">Input</p><pre className="whitespace-pre-wrap">{f.sample_input}</pre><p className="mt-2 text-muted-foreground">Output</p><pre className="whitespace-pre-wrap">{f.sample_output}</pre></div>
          </Card>
        )}
        <div className="flex justify-end gap-2"><Button variant="outline" to="/admin/problems">Cancel</Button><Button type="submit" loading={save.isPending}><Save /> {isNew ? "Publish problem" : "Save changes"}</Button></div>
      </form>
    </Page>
  );
}
