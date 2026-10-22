import { useMemo, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { Pencil, Plus, Save, Search, StickyNote, Trash2, X } from "lucide-react";
import { api } from "@/lib/api";
import { cn, fmtDate } from "@/lib/utils";
import { Badge, Button, Card, Empty, ErrorState, Input, Label, Page, PageHeader, PageSkeleton, Textarea } from "@/components/ui";

const blank = { subject: "", title: "", content: "" };

export default function Notes() {
  const qc = useQueryClient();
  const { data, isLoading, error, refetch } = useQuery({ queryKey: ["notes"], queryFn: () => api.get("/api/notes") });
  const [form, setForm] = useState(blank);
  const [editing, setEditing] = useState(null);
  const [q, setQ] = useState("");
  const [subject, setSubject] = useState("");
  const notes = data?.notes || [];
  const subjects = useMemo(() => [...new Set(notes.map((n) => n.subject))].sort(), [notes]);
  const shown = notes.filter((n) => (!subject || n.subject === subject) && `${n.subject} ${n.title} ${n.content}`.toLowerCase().includes(q.toLowerCase()));
  const done = (msg) => () => { toast.success(msg); qc.invalidateQueries({ queryKey: ["notes"] }); setForm(blank); setEditing(null); };
  const save = useMutation({ mutationFn: () => editing ? api.put(`/api/notes/${editing}`, form) : api.post("/api/notes", form), onSuccess: done(editing ? "Note updated" : "Note saved"), onError: (e) => toast.error(e.message) });
  const del = useMutation({ mutationFn: (id) => api.del(`/api/notes/${id}`), onSuccess: done("Note deleted"), onError: (e) => toast.error(e.message) });
  const set = (k) => (e) => setForm((f) => ({ ...f, [k]: e.target.value }));
  if (isLoading) return <PageSkeleton />;
  if (error) return <ErrorState error={error} retry={refetch} />;

  return (
    <Page>
      <PageHeader title="Flash notes" subtitle="Short revision cards you can scan before an interview.">
        <Button onClick={() => { setEditing(null); setForm(blank); document.getElementById("note-subject")?.focus(); }}><Plus /> New note</Button>
      </PageHeader>
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-[320px_minmax(0,1fr)]">
        <aside className="lg:sticky lg:top-20 lg:self-start">
          <Card className={cn("space-y-3 p-5", editing && "border-primary/50")}>
            <div className="flex items-center justify-between"><h2 className="font-semibold">{editing ? "Edit note" : "New note"}</h2>{editing && <button onClick={() => { setEditing(null); setForm(blank); }} aria-label="Cancel edit" className="text-muted-foreground hover:text-foreground"><X className="h-4 w-4" /></button>}</div>
            <form className="space-y-3" onSubmit={(e) => { e.preventDefault(); save.mutate(); }}>
              <div className="space-y-1.5"><Label htmlFor="note-subject">Subject</Label><Input id="note-subject" list="subjects" required maxLength={120} placeholder="e.g. Graphs" value={form.subject} onChange={set("subject")} /><datalist id="subjects">{subjects.map((s) => <option key={s} value={s} />)}</datalist></div>
              <div className="space-y-1.5"><Label htmlFor="note-title">Title</Label><Input id="note-title" required maxLength={200} placeholder="Dijkstra vs Bellman-Ford" value={form.title} onChange={set("title")} /></div>
              <div className="space-y-1.5"><div className="flex justify-between"><Label htmlFor="note-content">Note</Label><span className="text-xs text-muted-foreground">{form.content.length}/1000</span></div><Textarea id="note-content" rows={5} required maxLength={1000} placeholder="Keep it short — one idea per card." value={form.content} onChange={set("content")} /></div>
              <Button type="submit" className="w-full" loading={save.isPending}><Save /> {editing ? "Save changes" : "Save note"}</Button>
            </form>
          </Card>
        </aside>
        <section className="min-w-0">
          <Card className="mb-4 flex flex-col gap-3 p-4 sm:flex-row">
            <div className="relative flex-1"><Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" /><Input value={q} onChange={(e) => setQ(e.target.value)} placeholder="Search notes…" className="bg-background pl-9" aria-label="Search notes" /></div>
            <select value={subject} onChange={(e) => setSubject(e.target.value)} aria-label="Subject" className="h-9 rounded-md border border-input bg-card px-3 text-sm sm:w-48"><option value="">All subjects</option>{subjects.map((s) => <option key={s}>{s}</option>)}</select>
          </Card>
          <p className="mb-3 text-xs text-muted-foreground">{shown.length} note{shown.length !== 1 ? "s" : ""}</p>
          {shown.length ? (
            <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
              {shown.map((n) => (
                <Card key={n.id} className="flex flex-col p-4">
                  <div className="mb-2 flex items-center gap-2"><button onClick={() => setSubject(n.subject)}><Badge tone="primary">{n.subject}</Badge></button><span className="ml-auto text-xs text-muted-foreground">{fmtDate(n.updated_at)}</span></div>
                  <h3 className="font-semibold">{n.title}</h3>
                  <p className="mt-1 flex-1 whitespace-pre-line text-sm text-foreground/80">{n.content}</p>
                  <div className="mt-4 flex gap-2 border-t border-border pt-3">
                    <Button variant="ghost" size="sm" onClick={() => { setEditing(n.id); setForm({ subject: n.subject, title: n.title, content: n.content }); window.scrollTo({ top: 0, behavior: "smooth" }); }}><Pencil /> Edit</Button>
                    <Button variant="ghost" size="sm" className="text-hard hover:text-hard" onClick={() => confirm("Delete this note?") && del.mutate(n.id)}><Trash2 /> Delete</Button>
                  </div>
                </Card>
              ))}
            </div>
          ) : <Card><Empty icon={StickyNote} title={notes.length ? "No notes found" : "No notes yet"} text={notes.length ? "Try a different search." : "Write your first flash note on the left."} /></Card>}
        </section>
      </div>
    </Page>
  );
}
