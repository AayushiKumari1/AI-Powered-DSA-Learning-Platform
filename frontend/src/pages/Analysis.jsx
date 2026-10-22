import { Link, useParams } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { ArrowLeft, ArrowRight, Compass, Gauge, Lightbulb, ListChecks, Route, Sparkles, Timer, Zap } from "lucide-react";
import { api } from "@/lib/api";
import { Breadcrumbs, Button, Card, DifficultyBadge, Empty, Page, PageHeader, PageSkeleton, Progress, StatCard } from "@/components/ui";

export default function Analysis() {
  const { id } = useParams();
  const { data, isLoading, error } = useQuery({ queryKey: ["analysis", id], queryFn: () => api.get(`/api/problems/${id}/analysis`) });
  if (isLoading) return <PageSkeleton />;
  if (error) return <Page><Card><Empty icon={Sparkles} title="No analysis yet" text={error.message} action={<Button size="sm" to={`/practice/${id}`}>Open the editor</Button>} /></Card></Page>;
  const { analysis: a, problem } = data;
  const score = a.performance_rating ?? 0;
  const passedAll = a.total_cases && a.passed_cases === a.total_cases;

  return (
    <Page>
      <Breadcrumbs items={[{ label: "Practice", to: "/practice" }, { label: problem.title, to: `/practice/${id}` }, { label: "AI analysis" }]} />
      <PageHeader title="AI code analysis" subtitle={problem.title}>
        <Button variant="outline" to={`/practice/${id}`}><ArrowLeft /> Back to editor</Button>
        <Button to="/practice">Next problem <ArrowRight /></Button>
      </PageHeader>
      <div className="mb-6 grid grid-cols-2 gap-4 md:grid-cols-4">
        <StatCard icon={ListChecks} label="Tests passed" value={`${a.passed_cases ?? 0}/${a.total_cases ?? 0}`} accent={passedAll ? "var(--easy)" : "var(--hard)"} sub={passedAll ? "Accepted" : "Needs fixes"} />
        <StatCard icon={Gauge} label="Efficiency" value={`${score}/10`} accent="var(--chart-5)" />
        <StatCard icon={Timer} label="Solve time" value={`${((a.solve_time_seconds || 0) / 60).toFixed(1)} min`} accent="var(--medium)" />
        <StatCard icon={Zap} label="Avg case time" value={`${a.avg_case_time_ms ?? 0} ms`} accent="var(--chart-1)" />
      </div>
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        <Card className="p-5 lg:col-span-2">
          <h2 className="mb-4 font-semibold">Complexity</h2>
          <div className="grid gap-3 sm:grid-cols-3">
            {[["Your time complexity", a.used, a.used === a.best ? "text-easy" : "text-medium"], ["Best known", a.best, "text-easy"], ["Space", a.space_complexity, ""]].map(([l, v, c]) => (
              <div key={l} className="rounded-lg border border-border bg-background/40 p-4"><p className="text-xs text-muted-foreground">{l}</p><p className={`mt-1 font-mono text-xl font-semibold ${c}`}>{v || "—"}</p></div>
            ))}
          </div>
          <div className="mt-5">
            <div className="mb-1.5 flex justify-between text-xs text-muted-foreground"><span>Efficiency score</span><span className="text-foreground">{score}/10</span></div>
            <Progress value={score * 10} color={score >= 7 ? "var(--easy)" : score >= 4 ? "var(--medium)" : "var(--hard)"} />
            {a.performance_summary && <p className="mt-3 text-sm text-muted-foreground">{a.performance_summary}</p>}
          </div>
          {a.explanation && <><div className="my-5 h-px bg-border" /><h3 className="mb-2 text-sm font-semibold">What the AI noticed</h3><p className="text-sm leading-relaxed text-foreground/90">{a.explanation}</p></>}
          {a.optimization_tips?.length > 0 && <><h3 className="mb-2 mt-5 text-sm font-semibold">Optimization tips</h3><ul className="space-y-2">{a.optimization_tips.map((t, i) => <li key={i} className="flex items-start gap-2 text-sm"><Lightbulb className="mt-0.5 h-4 w-4 shrink-0 text-medium" />{t}</li>)}</ul></>}
          {a.recommended_approach && <div className="mt-5 rounded-md border border-primary/30 bg-primary/10 p-3 text-sm"><p className="mb-1 flex items-center gap-1.5 text-xs font-medium text-primary"><Route className="h-3.5 w-3.5" /> Recommended approach</p>{a.recommended_approach}</div>}
        </Card>
        <aside className="space-y-6">
          <Card className="bg-gradient-to-br from-card to-accent p-5">
            <div className="mb-2 flex items-center gap-2 text-xs font-medium text-chart-5"><Compass className="h-3.5 w-3.5" /> {(data.topic_label || "").toUpperCase()}</div>
            <h2 className="font-semibold">{data.solved_cleanly ? "What to learn next" : "Focus here first"}</h2>
            {data.focus_message && <p className="mt-1 text-sm text-muted-foreground">{data.focus_message}</p>}
            <ol className="mt-4 space-y-2">{data.next_steps.map((s, i) => <li key={i} className="flex items-start gap-2 text-sm"><span className="mt-0.5 font-mono text-xs text-muted-foreground">{i + 1}.</span>{s}</li>)}</ol>
          </Card>
          <Card className="p-5">
            <h2 className="mb-3 font-semibold">Practise more {data.topic_label}</h2>
            {data.related.length ? <ul className="divide-y divide-border">{data.related.map((r) => (
              <li key={r.id}><Link to={`/practice/${r.id}`} className="-mx-2 flex items-center gap-3 rounded-md px-2 py-2.5 transition-colors hover:bg-muted/40"><span className="w-8 font-mono text-xs text-muted-foreground">{r.id}.</span><span className="flex-1 truncate text-sm font-medium">{r.title}</span><DifficultyBadge difficulty={r.difficulty} /></Link></li>
            ))}</ul> : <p className="text-sm text-muted-foreground">No more related problems yet.</p>}
          </Card>
        </aside>
      </div>
    </Page>
  );
}
