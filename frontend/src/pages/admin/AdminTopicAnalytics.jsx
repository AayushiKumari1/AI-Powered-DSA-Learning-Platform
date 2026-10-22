import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Bar, BarChart, CartesianGrid, Cell, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { BookOpen, CheckCircle2, Clock, MousePointerClick } from "lucide-react";
import { api } from "@/lib/api";
import { C } from "@/lib/utils";
import { Card, ErrorState, Page, PageHeader, PageSkeleton, Progress, StatCard, Tabs, chartTooltip } from "@/components/ui";

export default function AdminTopicAnalytics() {
  const [metric, setMetric] = useState("completed");
  const { data, isLoading, error, refetch } = useQuery({ queryKey: ["admin-topics"], queryFn: () => api.get("/api/admin/topics") });
  if (isLoading) return <PageSkeleton />;
  if (error) return <ErrorState error={error} retry={refetch} />;
  const T = data.topics, started = T.reduce((a, t) => a + t.started, 0), done = T.reduce((a, t) => a + t.completed, 0);
  const chart = [...T].sort((a, b) => b[metric] - a[metric]);
  const labels = { completed: "Completions", started: "Learners started", minutes: "Study minutes", quiz_passed: "Quiz passes" };
  return (
    <Page>
      <PageHeader title="Topic analytics" subtitle={`Engagement across ${T.length} topics and ${data.learners} learners`} />
      <div className="mb-6 grid grid-cols-2 gap-4 md:grid-cols-4">
        <StatCard icon={BookOpen} label="Topics" value={T.length} accent="var(--chart-1)" />
        <StatCard icon={MousePointerClick} label="Topic starts" value={started} accent="var(--chart-5)" />
        <StatCard icon={CheckCircle2} label="Completions" value={done} accent="var(--easy)" sub={`${started ? Math.round((done / started) * 100) : 0}% completion rate`} />
        <StatCard icon={Clock} label="Total study time" value={`${(T.reduce((a, t) => a + t.minutes, 0) / 60).toFixed(1)} h`} accent="var(--medium)" />
      </div>
      <Card className="mb-6 p-5">
        <div className="mb-4 flex flex-wrap items-start justify-between gap-3"><div><h2 className="font-semibold">By topic</h2><p className="text-sm text-muted-foreground">{labels[metric]}, highest first</p></div>
          <Tabs size="sm" value={metric} onChange={setMetric} items={[{ value: "completed", label: "Completions" }, { value: "started", label: "Started" }, { value: "minutes", label: "Minutes" }, { value: "quiz_passed", label: "Quizzes" }]} /></div>
        <div style={{ height: chart.length * 26 + 30 }}><ResponsiveContainer width="100%" height="100%">
          <BarChart data={chart} layout="vertical" margin={{ left: 0, right: 16, top: 0, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" horizontal={false} />
            <XAxis type="number" stroke="var(--muted-foreground)" fontSize={11} tickLine={false} axisLine={false} allowDecimals={false} />
            <YAxis type="category" dataKey="title" width={150} stroke="var(--muted-foreground)" fontSize={11} tickLine={false} axisLine={false} />
            <Tooltip {...chartTooltip} />
            <Bar dataKey={metric} name={labels[metric]} radius={[0, 4, 4, 0]} maxBarSize={16}>{chart.map((t) => <Cell key={t.id} fill={metric === "completed" ? C.easy : metric === "minutes" ? C.violet : metric === "quiz_passed" ? C.medium : C.primary} />)}</Bar>
          </BarChart></ResponsiveContainer></div>
      </Card>
      <Card className="overflow-hidden"><div className="overflow-x-auto"><table className="w-full text-sm">
        <thead><tr className="border-b border-border bg-background/40 text-left text-xs uppercase tracking-wider text-muted-foreground"><th className="h-10 px-4 font-medium">Topic</th><th className="px-4 text-right font-medium">Started</th><th className="px-4 text-right font-medium">Completed</th><th className="px-4 text-right font-medium">Quiz passes</th><th className="w-1/4 px-4 font-medium">Completion rate</th><th className="px-4 text-right font-medium">Minutes</th></tr></thead>
        <tbody>{[...T].sort((a, b) => b.started - a.started).map((t) => { const r = t.started ? (t.completed / t.started) * 100 : 0; return (
          <tr key={t.id} className="border-b border-border last:border-0 hover:bg-muted/40"><td className="px-4 py-3 font-medium">{t.title}</td><td className="px-4 py-3 text-right tabular-nums">{t.started}</td><td className="px-4 py-3 text-right tabular-nums">{t.completed}</td><td className="px-4 py-3 text-right tabular-nums">{t.quiz_passed}</td><td className="px-4 py-3"><div className="flex items-center gap-2"><Progress value={r} color="var(--easy)" className="h-1.5" /><span className="w-9 text-right text-xs tabular-nums text-muted-foreground">{Math.round(r)}%</span></div></td><td className="px-4 py-3 text-right tabular-nums text-muted-foreground">{t.minutes}</td></tr>); })}</tbody>
      </table></div></Card>
    </Page>
  );
}
