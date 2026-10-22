import { useParams } from "react-router-dom";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { CheckCircle2, ChevronRight, Clock, Code2, Copy, Gauge, History, Send, Timer, Trash2, XCircle } from "lucide-react";
import { api } from "@/lib/api";
import { fmtTime } from "@/lib/utils";
import { Breadcrumbs, Button, Card, Empty, ErrorState, Page, PageHeader, PageSkeleton, StatCard } from "@/components/ui";

export default function Submissions() {
  const { id } = useParams();
  const qc = useQueryClient();
  const { data, isLoading, error, refetch } = useQuery({ queryKey: ["submissions", id], queryFn: () => api.get(`/api/problems/${id}/submissions`) });
  const del = useMutation({
    mutationFn: (sid) => api.del(`/coding/delete_submission/${sid}`),   // existing Flask endpoint
    onSuccess: (r) => { if (r?.success === false) return toast.error("Couldn't delete this submission."); toast.success("Submission deleted"); qc.invalidateQueries({ queryKey: ["submissions", id] }); },
    onError: (e) => toast.error(e.message),
  });
  if (isLoading) return <PageSkeleton />;
  if (error) return <ErrorState error={error} retry={refetch} />;
  const subs = data.submissions;
  const accepted = subs.filter((s) => s.status === "Passed").length;
  const rts = subs.map((s) => s.runtime).filter((r) => r != null);

  return (
    <Page>
      <Breadcrumbs items={[{ label: "Practice", to: "/practice" }, { label: data.problem.title, to: `/practice/${id}` }, { label: "Submissions" }]} />
      <PageHeader title="Submission history" subtitle={`${subs.length} attempt${subs.length !== 1 ? "s" : ""} on ${data.problem.title}`}><Button to={`/practice/${id}`}><Code2 /> Back to editor</Button></PageHeader>
      {subs.length ? (<>
        <div className="mb-6 grid grid-cols-2 gap-4 md:grid-cols-4">
          <StatCard icon={Send} label="Attempts" value={subs.length} accent="var(--chart-1)" />
          <StatCard icon={CheckCircle2} label="Accepted" value={accepted} accent="var(--easy)" />
          <StatCard icon={Gauge} label="Best runtime" value={rts.length ? `${Math.min(...rts).toFixed(1)} ms` : "—"} accent="var(--medium)" />
          <StatCard icon={Clock} label="Last attempt" value={fmtTime(subs[0].at).split(",")[0]} accent="var(--chart-5)" />
        </div>
        <Card className="overflow-hidden">
          <ul className="divide-y divide-border">
            {subs.map((s) => { const ok = s.total && s.passed === s.total; return (
              <li key={s.id} className="p-4">
                <div className="flex flex-wrap items-center gap-3">
                  {ok ? <CheckCircle2 className="h-4 w-4 text-easy" /> : <XCircle className="h-4 w-4 text-hard" />}
                  <span className={`text-sm font-medium ${ok ? "text-easy" : "text-hard"}`}>{ok ? "Accepted" : s.passed ? "Partial" : "Failed"}</span>
                  <span className="rounded bg-muted px-2 py-0.5 font-mono text-xs">{s.language}</span>
                  <span className="text-xs text-muted-foreground">{s.passed ?? 0}/{s.total ?? 0} tests</span>
                  {s.runtime != null && <span className="flex items-center gap-1 text-xs text-muted-foreground"><Gauge className="h-3.5 w-3.5" />{s.runtime.toFixed(1)} ms</span>}
                  {s.solve_time != null && <span className="flex items-center gap-1 text-xs text-muted-foreground"><Timer className="h-3.5 w-3.5" />{(s.solve_time / 60).toFixed(1)} min</span>}
                  <span className="ml-auto text-xs text-muted-foreground">{fmtTime(s.at)}</span>
                </div>
                <details className="group mt-3">
                  <summary className="flex cursor-pointer list-none items-center gap-1 text-xs text-primary hover:underline"><ChevronRight className="h-3.5 w-3.5 transition-transform group-open:rotate-90" /> View code</summary>
                  <pre className="mt-2 max-h-80 overflow-auto rounded-md border border-border bg-background/40 p-3 font-mono text-xs">{s.code}</pre>
                </details>
                <div className="mt-3 flex gap-2">
                  <Button variant="outline" size="sm" onClick={() => navigator.clipboard.writeText(s.code || "").then(() => toast.success("Code copied"), () => toast.error("Copy failed"))}><Copy /> Copy</Button>
                  <Button variant="ghost" size="sm" className="text-hard hover:text-hard" onClick={() => confirm("Delete this submission? This can't be undone.") && del.mutate(s.id)}><Trash2 /> Delete</Button>
                </div>
              </li>); })}
          </ul>
        </Card>
      </>) : <Card><Empty icon={History} title="No submissions yet" text="Submit a solution and it will show up here with test results and runtime." action={<Button size="sm" to={`/practice/${id}`}>Open the editor</Button>} /></Card>}
    </Page>
  );
}
