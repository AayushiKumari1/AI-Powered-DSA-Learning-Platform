import { useParams } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { BookOpen, CheckCircle2, CircleDashed, Clock, Code2, Compass, Lock, Minus, RotateCcw, Sparkles, Target, TrendingDown, TrendingUp, XCircle, Zap } from "lucide-react";
import { api } from "@/lib/api";
import { Breadcrumbs, Button, Card, DifficultyBadge, ErrorState, Page, PageHeader, PageSkeleton, StatCard } from "@/components/ui";

export default function TestResult() {
  const { id } = useParams();
  const { data: d, isLoading, error, refetch } = useQuery({ queryKey: ["result", id], queryFn: () => api.get(`/api/tests/${id}/result`) });
  if (isLoading) return <PageSkeleton />;
  if (error) return <ErrorState error={error} retry={refetch} />;
  const pct = d.total ? Math.round((d.passed / d.total) * 1000) / 10 : 0;
  return (
    <Page>
      <Breadcrumbs items={[{ label: "Tests", to: "/tests" }, { label: d.test.title, to: `/tests/${id}` }, { label: "Result" }]} />
      <PageHeader title={`${d.test.title} — results`} subtitle="Your latest attempt on every question in this test.">
        <Button variant="outline" to={`/tests/${id}/solve/0`}><RotateCcw /> Retake</Button><Button to="/tests">All tests</Button>
      </PageHeader>
      <div className="mb-6 grid grid-cols-2 gap-4 md:grid-cols-4">
        <StatCard icon={Target} label="Score" value={`${d.passed}/${d.total}`} accent={pct >= 60 ? "var(--easy)" : "var(--hard)"} sub={`${pct}% passed`} />
        <StatCard icon={Clock} label="Total time" value={`${d.total_time}s`} accent="var(--chart-1)" sub={`${d.total ? (d.total_time / d.total).toFixed(1) : 0}s per question`} />
        <StatCard icon={Zap} label="XP earned" value={`+${d.xp_earned}`} accent="var(--medium)" />
        <StatCard icon={Compass} label="Focus next" value={d.recommended || "—"} accent="var(--chart-5)" />
      </div>
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        <Card className="overflow-hidden lg:col-span-2">
          <h2 className="border-b border-border px-5 py-4 font-semibold">Question breakdown</h2>
          <div className="overflow-x-auto"><table className="w-full text-sm">
            <thead><tr className="border-b border-border bg-background/40 text-left text-xs uppercase tracking-wider text-muted-foreground"><th className="h-10 w-10 px-4 font-medium">#</th><th className="px-4 font-medium">Question</th><th className="px-4 font-medium">Difficulty</th><th className="px-4 font-medium">Status</th><th className="px-4 text-right font-medium">Time</th></tr></thead>
            <tbody>{d.rows.map((r, i) => (
              <tr key={r.id} className="border-b border-border last:border-0 hover:bg-muted/40">
                <td className="px-4 py-3 font-mono text-xs text-muted-foreground">{i + 1}</td><td className="px-4 py-3 font-medium">{r.title}</td><td className="px-4 py-3"><DifficultyBadge difficulty={r.difficulty} /></td>
                <td className="px-4 py-3">{r.status === "Passed" ? <span className="flex items-center gap-1.5 text-easy"><CheckCircle2 className="h-4 w-4" />Passed</span> : r.status === "Failed" ? <span className="flex items-center gap-1.5 text-hard"><XCircle className="h-4 w-4" />Failed</span> : <span className="flex items-center gap-1.5 text-muted-foreground"><CircleDashed className="h-4 w-4" />{r.status}</span>}</td>
                <td className="px-4 py-3 text-right font-mono text-xs text-muted-foreground">{r.time_taken}s</td>
              </tr>))}</tbody>
          </table></div>
        </Card>
        <Card className="p-5">
          <h2 className="mb-1 font-semibold">Topic mastery</h2><p className="mb-4 text-xs text-muted-foreground">Estimated by the ML mastery model</p>
          {[["Strong", "var(--easy)", TrendingUp], ["Average", "var(--medium)", Minus], ["Weak", "var(--hard)", TrendingDown]].map(([lvl, color, I]) => (
            <div key={lvl} className="mb-4">
              <p className="mb-2 flex items-center gap-1.5 text-xs font-medium" style={{ color }}><I className="h-3.5 w-3.5" />{lvl}</p>
              <div className="flex flex-wrap gap-1.5">{(d.mastery[lvl] || []).length ? d.mastery[lvl].map((t) => <span key={t} className="rounded-md border px-2 py-0.5 text-xs" style={{ borderColor: `color-mix(in oklab, ${color} 35%, transparent)`, background: `color-mix(in oklab, ${color} 12%, transparent)` }}>{t}</span>) : <span className="text-xs text-muted-foreground">None</span>}</div>
            </div>
          ))}
          {d.blocked.length > 0 && <div className="mt-2 rounded-md border border-border bg-background/40 p-3"><p className="mb-2 flex items-center gap-1.5 text-xs font-medium text-muted-foreground"><Lock className="h-3.5 w-3.5" /> Locked until prerequisites improve</p><div className="flex flex-wrap gap-1.5">{d.blocked.map((t) => <span key={t} className="rounded bg-muted px-2 py-0.5 text-xs">{t}</span>)}</div></div>}
        </Card>
        {Object.keys(d.explanations).length > 0 && (
          <Card className="p-5 lg:col-span-3">
            <h2 className="mb-4 font-semibold">What this means for each topic</h2>
            <div className="grid gap-4 md:grid-cols-2">{Object.entries(d.explanations).map(([topic, text]) => (
              <div key={topic} className="rounded-lg border border-border bg-background/40 p-4"><p className="mb-1 flex items-center gap-2 text-sm font-semibold"><Sparkles className="h-4 w-4 text-chart-5" />{topic}</p><p className="text-sm leading-relaxed text-muted-foreground">{text}</p></div>
            ))}</div>
          </Card>
        )}
      </div>
      <div className="mt-6 flex flex-wrap gap-2"><Button variant="outline" to="/learn"><BookOpen /> Study weak topics</Button><Button variant="outline" to="/practice"><Code2 /> Practice problems</Button></div>
    </Page>
  );
}
