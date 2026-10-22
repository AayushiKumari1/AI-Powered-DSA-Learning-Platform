import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { Megaphone, Send } from "lucide-react";
import { api } from "@/lib/api";
import { fmtTime } from "@/lib/utils";
import { Button, Card, Empty, ErrorState, IconTile, Input, Label, Page, PageHeader, PageSkeleton, Progress, Textarea } from "@/components/ui";

export default function AdminAnnouncements() {
  const qc = useQueryClient();
  const [f, setF] = useState({ title: "", content: "" });
  const { data, isLoading, error, refetch } = useQuery({ queryKey: ["admin-announcements"], queryFn: () => api.get("/api/admin/announcements") });
  const send = useMutation({ mutationFn: () => api.post("/api/admin/announcements", f), onSuccess: (r) => { toast.success(`Sent to ${r.recipients} learners`); setF({ title: "", content: "" }); qc.invalidateQueries({ queryKey: ["admin-announcements"] }); }, onError: (e) => toast.error(e.message) });
  if (isLoading) return <PageSkeleton />;
  if (error) return <ErrorState error={error} retry={refetch} />;
  return (
    <Page>
      <PageHeader title="Announcements" subtitle="Each announcement lands in every learner's notifications and on their dashboard." />
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-[380px_minmax(0,1fr)]">
        <Card className="h-fit space-y-4 p-5 lg:sticky lg:top-20">
          <h2 className="font-semibold">New announcement</h2>
          <form className="space-y-4" onSubmit={(e) => { e.preventDefault(); if (confirm("Send this announcement to every learner?")) send.mutate(); }}>
            <div className="space-y-1.5"><Label htmlFor="at">Title</Label><Input id="at" required maxLength={200} value={f.title} onChange={(e) => setF({ ...f, title: e.target.value })} placeholder="New weekly contest is live" /></div>
            <div className="space-y-1.5"><Label htmlFor="ac">Message</Label><Textarea id="ac" rows={6} required value={f.content} onChange={(e) => setF({ ...f, content: e.target.value })} placeholder="What should learners know?" /></div>
            {(f.title || f.content) && <div className="rounded-lg border border-primary/30 bg-gradient-to-br from-card to-accent p-3 text-sm"><p className="mb-1 text-xs text-muted-foreground">Preview</p><p className="font-semibold">{f.title}</p><p className="mt-1 whitespace-pre-line text-foreground/80">{f.content}</p></div>}
            <Button type="submit" className="w-full" loading={send.isPending}><Send /> Send to all learners</Button>
          </form>
        </Card>
        <Card className="overflow-hidden">
          <h2 className="border-b border-border px-5 py-4 font-semibold">Sent · {data.announcements.length}</h2>
          {data.announcements.length ? <ul className="divide-y divide-border">{data.announcements.map((a) => { const rate = a.recipients ? (a.read / a.recipients) * 100 : 0; return (
            <li key={a.id} className="flex gap-4 p-5">
              <IconTile icon={Megaphone} color="var(--medium)" className="mt-0.5 h-8 w-8" />
              <div className="min-w-0 flex-1">
                <div className="flex flex-wrap items-center gap-2"><h3 className="font-medium">{a.title}</h3><span className="ml-auto text-xs text-muted-foreground">{fmtTime(a.at)}</span></div>
                <p className="mt-1 whitespace-pre-line text-sm text-foreground/80">{a.content}</p>
                <div className="mt-3 flex items-center gap-3"><Progress value={rate} className="h-1 max-w-48" /><span className="text-xs text-muted-foreground">Read by {a.read} of {a.recipients}</span></div>
              </div>
            </li>); })}</ul> : <Empty icon={Megaphone} title="No announcements yet" />}
        </Card>
      </div>
    </Page>
  );
}
