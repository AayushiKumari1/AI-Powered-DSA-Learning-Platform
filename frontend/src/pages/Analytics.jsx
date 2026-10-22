import { useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { toast } from "sonner";
import { Area, AreaChart, Bar, BarChart, CartesianGrid, Cell, Pie, PieChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { BookOpen, ChevronsUpDown, CircleDashed, Clock, Code2, Download, ListChecks, Search, Target, TrendingUp } from "lucide-react";
import { api } from "@/lib/api";
import { C, cn } from "@/lib/utils";
import { Badge, Button, Card, DifficultyBadge, Empty, ErrorState, Input, Page, PageSkeleton, Progress, Tabs, chartTooltip } from "@/components/ui";

export default function Analytics() {
  const { data, isLoading, error, refetch } = useQuery({ queryKey: ["analytics"], queryFn: () => api.get("/api/analytics") });
  const [metric, setMetric] = useState("visits");
  const [status, setStatus] = useState("all");
  const [q, setQ] = useState("");
  const [sort, setSort] = useState({ key: null, dir: "desc" });

  const topics = data?.topics || [];
  const statusOf = (t) => (t.completed ? "done" : t.visits ? "progress" : "todo");
  const chartRows = useMemo(() => topics.filter((t) => t.visits || t.minutes).sort((a, b) => b[metric] - a[metric]).slice(0, 15), [topics, metric]);
  const tableRows = useMemo(() => {
    let r = topics.filter((t) => (status === "all" || statusOf(t) === status) && t.title.toLowerCase().includes(q.toLowerCase()));
    if (sort.key) r = [...r].sort((a, b) => (a[sort.key] > b[sort.key] ? 1 : a[sort.key] < b[sort.key] ? -1 : 0) * (sort.dir === "asc" ? 1 : -1));
    return r;
  }, [topics, status, q, sort]);
  if (isLoading) return <PageSkeleton />;
  if (error) return <ErrorState error={error} retry={refetch} />;

  const t = data.totals, sd = data.solved_by_difficulty, md = data.marks_by_difficulty;
  const xpTotal = Math.max(t.topic_xp + t.quiz_xp + t.coding_xp + t.other_xp, 1);
  const started = topics.filter((x) => x.visits).length;
  const inProgress = Math.max(started - t.completed_topics, 0), notStarted = topics.length - started;
  const passRate = t.topics ? Math.round((t.quizzes_passed / t.topics) * 1000) / 10 : 0;
  const completion = t.topics ? Math.round((t.completed_topics / t.topics) * 1000) / 10 : 0;
  const maxMin = Math.max(...topics.map((x) => x.minutes), 0.1);
  const top = [...topics].sort((a, b) => b.minutes - a.minutes)[0];
  const gap = ["easy", "medium", "hard"].find((d) => !sd[d]);
  const parts = [["Topics", t.topic_xp, C.primary], ["Quizzes", t.quiz_xp, C.easy], ["Coding", t.coding_xp, C.hard], ["Other", t.other_xp, C.violet]];
  const toggleSort = (key) => setSort((s) => ({ key, dir: s.key === key && s.dir === "desc" ? "asc" : "desc" }));

  function exportCsv() {
    const esc = (v) => `"${String(v).replace(/"/g, '""')}"`;
    const lines = ["Topic,Completed,Quiz passed,Visits,Minutes", ...topics.map((r) => [esc(r.title), r.completed ? "yes" : "no", r.quiz_passed ? "yes" : "no", r.visits, r.minutes].join(",")),
      "", `Total XP,${t.xp}`, `Problems solved,${t.solved}`, `Submissions,${t.submissions}`, `Acceptance %,${t.acceptance}`];
    const a = Object.assign(document.createElement("a"), { href: URL.createObjectURL(new Blob([lines.join("\n")], { type: "text/csv" })), download: "edumentor-analytics.csv" });
    a.click(); setTimeout(() => URL.revokeObjectURL(a.href), 1000); toast.success("Analytics exported");
  }

  const kpis = [
    { label: "Total XP", value: t.xp, sub: `${Math.round((t.coding_xp / xpTotal) * 100)}% from coding` },
    { label: "Topic completion", value: `${completion}%`, sub: `${t.completed_topics} of ${t.topics} topics`, pct: completion, color: "var(--primary)" },
    { label: "Quiz pass rate", value: `${passRate}%`, sub: `${t.quizzes_passed} of ${t.topics} passed`, pct: passRate, color: "var(--easy)" },
    { label: "Problems solved", value: t.solved, sub: `${sd.easy} E · ${sd.medium} M · ${sd.hard} H` },
    { label: "Acceptance rate", value: `${t.acceptance}%`, sub: `${t.submissions} submissions`, pct: t.acceptance, color: "var(--chart-5)" },
    { label: "Study time", value: `${Math.round(t.minutes)} min`, sub: `${(t.minutes / 60).toFixed(1)} hours tracked` },
  ];

  return (
    <Page>
      <div className="mb-6 flex flex-wrap items-end justify-between gap-4">
        <div><h1 className="text-2xl font-semibold tracking-tight md:text-3xl">Analytics</h1><p className="mt-1 text-sm text-muted-foreground">Performance across topics, quizzes and coding practice.</p></div>
        <div className="flex gap-2"><Button variant="outline" size="sm" onClick={exportCsv}><Download /> Export CSV</Button><Button size="sm" to="/practice"><Code2 /> Practice</Button></div>
      </div>

      <section aria-label="Key figures" className="mb-6 grid grid-cols-2 gap-px overflow-hidden rounded-xl border border-border bg-border shadow md:grid-cols-3 xl:grid-cols-6">
        {kpis.map((k) => (
          <div key={k.label} className="bg-card p-5">
            <p className="text-xs font-medium text-muted-foreground">{k.label}</p>
            <p className="mt-1.5 text-2xl font-semibold tabular-nums tracking-tight">{k.value}</p>
            {k.pct != null && <Progress value={k.pct} color={k.color} className="mt-2 h-1" />}
            <p className="mt-1.5 text-xs text-muted-foreground">{k.sub}</p>
          </div>
        ))}
      </section>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        <Card className="p-5 lg:col-span-2">
          <div className="mb-4 flex items-start justify-between"><div><h2 className="text-sm font-semibold">Submissions · last 30 days</h2><p className="text-xs text-muted-foreground">All attempts vs accepted solutions</p></div>
            <div className="flex gap-3 text-xs text-muted-foreground"><span className="flex items-center gap-1.5"><span className="h-2 w-2 rounded-sm" style={{ background: C.primary }} />Submissions</span><span className="flex items-center gap-1.5"><span className="h-2 w-2 rounded-sm" style={{ background: C.easy }} />Accepted</span></div></div>
          <div className="h-56">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={data.daily} margin={{ left: -20, right: 8, top: 8, bottom: 0 }}>
                <defs><linearGradient id="subs" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stopColor={C.primary} stopOpacity={0.45} /><stop offset="100%" stopColor={C.primary} stopOpacity={0} /></linearGradient></defs>
                <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" vertical={false} />
                <XAxis dataKey="label" stroke="var(--muted-foreground)" fontSize={11} tickLine={false} axisLine={false} interval={4} />
                <YAxis stroke="var(--muted-foreground)" fontSize={11} tickLine={false} axisLine={false} allowDecimals={false} />
                <Tooltip {...chartTooltip} cursor={{ stroke: "var(--border)" }} />
                <Area type="monotone" dataKey="submissions" name="Submissions" stroke={C.primary} strokeWidth={2} fill="url(#subs)" />
                <Area type="monotone" dataKey="accepted" name="Accepted" stroke={C.easy} strokeWidth={2} fill="transparent" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </Card>

        <Card className="p-5">
          <h2 className="text-sm font-semibold">Quiz performance</h2><p className="mb-4 text-xs text-muted-foreground">Topic quizzes, 3 of 5 correct to pass</p>
          <div className="flex items-center gap-5">
            <div className="relative h-28 w-28 shrink-0">
              <ResponsiveContainer width="100%" height="100%"><PieChart><Pie data={[{ v: t.quizzes_passed }, { v: Math.max(t.topics - t.quizzes_passed, 0) }]} dataKey="v" innerRadius="78%" outerRadius="100%" stroke="none" startAngle={90} endAngle={-270}><Cell fill={C.easy} /><Cell fill="oklch(65% .02 255 / .25)" /></Pie></PieChart></ResponsiveContainer>
              <div className="pointer-events-none absolute inset-0 grid place-items-center text-center"><div><p className="text-xl font-semibold tabular-nums">{Math.round(passRate)}%</p><p className="text-[10px] text-muted-foreground">pass rate</p></div></div>
            </div>
            <dl className="flex-1 space-y-2 text-sm">
              <div className="flex justify-between"><dt className="flex items-center gap-2 text-muted-foreground"><span className="h-2 w-2 rounded-sm bg-easy" />Passed</dt><dd className="font-medium tabular-nums">{t.quizzes_passed}</dd></div>
              <div className="flex justify-between"><dt className="flex items-center gap-2 text-muted-foreground"><span className="h-2 w-2 rounded-sm bg-muted-foreground/40" />Pending</dt><dd className="font-medium tabular-nums">{t.topics - t.quizzes_passed}</dd></div>
              <div className="flex justify-between border-t border-border pt-2"><dt className="text-muted-foreground">Total</dt><dd className="font-medium tabular-nums">{t.topics}</dd></div>
            </dl>
          </div>
        </Card>

        <Card className="p-5">
          <h2 className="text-sm font-semibold">XP composition</h2><p className="mb-4 text-xs text-muted-foreground">Where your {t.xp} XP came from</p>
          <div className="flex h-2.5 w-full overflow-hidden rounded-full bg-muted" role="img" aria-label="XP composition">{parts.filter((p) => p[1]).map(([n, v, c]) => <span key={n} title={`${n}: ${v} XP`} style={{ width: `${(v / xpTotal) * 100}%`, background: c }} />)}</div>
          <table className="mt-5 w-full text-sm"><tbody className="divide-y divide-border">
            {parts.map(([n, v, c]) => <tr key={n}><td className="py-2"><span className="mr-2 inline-block h-2 w-2 rounded-sm align-middle" style={{ background: c }} />{n}</td><td className="py-2 text-right font-medium tabular-nums">{v}</td><td className="w-14 py-2 text-right text-xs tabular-nums text-muted-foreground">{Math.round((v / xpTotal) * 100)}%</td></tr>)}
          </tbody></table>
        </Card>

        <Card className="p-5">
          <h2 className="text-sm font-semibold">Coding by difficulty</h2><p className="mb-4 text-xs text-muted-foreground">Practice and test solves combined</p>
          <table className="w-full text-sm">
            <thead><tr className="text-xs text-muted-foreground"><th className="pb-2 text-left font-medium">Level</th><th className="pb-2 text-left font-medium">Solved</th><th className="pb-2 text-right font-medium">Marks</th></tr></thead>
            <tbody className="divide-y divide-border">
              {[["easy", C.easy], ["medium", C.medium], ["hard", C.hard]].map(([d, c]) => { const max = Math.max(sd.easy, sd.medium, sd.hard, 1); return (
                <tr key={d}><td className="w-24 py-2.5"><DifficultyBadge difficulty={d} /></td>
                  <td className="py-2.5"><div className="flex items-center gap-2"><div className="h-1.5 flex-1 overflow-hidden rounded-full bg-muted"><span className="block h-full rounded-full" style={{ width: `${(sd[d] / max) * 100}%`, background: c }} /></div><span className="w-6 text-right font-medium tabular-nums">{sd[d]}</span></div></td>
                  <td className="w-14 py-2.5 text-right tabular-nums text-muted-foreground">{md[d]}</td></tr>); })}
            </tbody>
          </table>
        </Card>

        <Card className="p-5">
          <h2 className="text-sm font-semibold">Insights</h2><p className="mb-4 text-xs text-muted-foreground">Based on your current numbers</p>
          <ul className="space-y-4 text-sm">
            {top?.minutes > 0 && <li className="flex gap-3"><Clock className="mt-0.5 h-4 w-4 shrink-0 text-chart-1" /><p><span className="font-medium">{top.title}</span> has your most study time ({top.minutes} min, {top.completed ? "completed" : "not yet completed"}).</p></li>}
            {inProgress > 0 && <li className="flex gap-3"><CircleDashed className="mt-0.5 h-4 w-4 shrink-0 text-medium" /><p><span className="font-medium tabular-nums">{inProgress}</span> topic{inProgress !== 1 ? "s" : ""} opened but not completed. Finishing {inProgress === 1 ? "it" : "them"} is the quickest XP available.</p></li>}
            {t.topics - t.quizzes_passed > 0 && <li className="flex gap-3"><ListChecks className="mt-0.5 h-4 w-4 shrink-0 text-easy" /><p><span className="font-medium tabular-nums">{t.topics - t.quizzes_passed}</span> quizzes pending, worth up to {(t.topics - t.quizzes_passed) * 10} XP.</p></li>}
            {gap ? <li className="flex gap-3"><Target className="mt-0.5 h-4 w-4 shrink-0 text-hard" /><p>No {gap} problems solved yet. <Link to="/practice" className="text-primary hover:underline">Try one</Link>.</p></li>
              : <li className="flex gap-3"><TrendingUp className="mt-0.5 h-4 w-4 shrink-0 text-easy" /><p>You've solved problems at every difficulty.</p></li>}
          </ul>
        </Card>

        <Card className="p-5 lg:col-span-3">
          <div className="mb-4 flex flex-wrap items-start justify-between gap-3">
            <div><h2 className="text-sm font-semibold">Topic activity</h2><p className="text-xs text-muted-foreground">{metric === "visits" ? "Visits" : "Minutes"} per topic · top 15 opened topics · green = completed</p></div>
            <Tabs size="sm" value={metric} onChange={setMetric} items={[{ value: "visits", label: "Visits" }, { value: "minutes", label: "Minutes" }]} />
          </div>
          {chartRows.length ? (
            <div style={{ height: Math.max(chartRows.length * 28 + 30, 160) }}>
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={chartRows} layout="vertical" margin={{ left: 0, right: 16, top: 0, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" horizontal={false} />
                  <XAxis type="number" stroke="var(--muted-foreground)" fontSize={11} tickLine={false} axisLine={false} allowDecimals={metric === "minutes"} />
                  <YAxis type="category" dataKey="title" width={150} stroke="var(--muted-foreground)" fontSize={11} tickLine={false} axisLine={false} />
                  <Tooltip {...chartTooltip} />
                  <Bar dataKey={metric} name={metric === "visits" ? "Visits" : "Minutes"} radius={[0, 4, 4, 0]} maxBarSize={18}>
                    {chartRows.map((r) => <Cell key={r.id} fill={r.completed ? C.easy : C.primary} />)}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          ) : <Empty icon={BookOpen} title="No topic activity yet" text="Open a topic to start building your history." action={<Button size="sm" to="/learn">Browse topics</Button>} />}
        </Card>

        <Card className="overflow-hidden lg:col-span-3">
          <div className="flex flex-wrap items-center gap-3 border-b border-border px-5 py-4">
            <div className="mr-auto"><h2 className="text-sm font-semibold">Topic breakdown</h2><p className="text-xs text-muted-foreground">{t.completed_topics} completed · {inProgress} in progress · {notStarted} not started</p></div>
            <Tabs size="sm" value={status} onChange={setStatus} items={[{ value: "all", label: "All" }, { value: "done", label: "Completed" }, { value: "progress", label: "In progress" }, { value: "todo", label: "Not started" }]} />
            <div className="relative w-full sm:w-56"><Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" /><Input value={q} onChange={(e) => setQ(e.target.value)} placeholder="Filter topics…" className="h-8 bg-background pl-9" aria-label="Filter topics" /></div>
          </div>
          <div className="max-h-[480px] overflow-auto">
            <table className="w-full text-sm">
              <thead className="sticky top-0 z-10 bg-card"><tr className="border-b border-border text-left text-xs uppercase tracking-wider text-muted-foreground">
                <th className="h-10 px-4 font-medium"><button onClick={() => toggleSort("title")} className="inline-flex items-center gap-1 uppercase hover:text-foreground">Topic <ChevronsUpDown className="h-3 w-3" /></button></th>
                <th className="px-4 font-medium">Status</th><th className="px-4 font-medium">Quiz</th>
                <th className="px-4 text-right font-medium"><button onClick={() => toggleSort("visits")} className="inline-flex items-center gap-1 uppercase hover:text-foreground">Visits <ChevronsUpDown className="h-3 w-3" /></button></th>
                <th className="px-4 text-right font-medium"><button onClick={() => toggleSort("minutes")} className="inline-flex items-center gap-1 uppercase hover:text-foreground">Minutes <ChevronsUpDown className="h-3 w-3" /></button></th>
                <th className="hidden w-1/4 px-4 font-medium md:table-cell">Share of study time</th>
              </tr></thead>
              <tbody>
                {tableRows.map((r) => { const s = statusOf(r); return (
                  <tr key={r.id} className="border-b border-border last:border-0 hover:bg-muted/40">
                    <td className="px-4 py-3 font-medium"><Link to={`/learn/${r.id}`} className="hover:text-primary">{r.title}</Link></td>
                    <td className="px-4 py-3">{s === "done" ? <Badge tone="easy">Completed</Badge> : s === "progress" ? <Badge tone="medium">In progress</Badge> : <Badge>Not started</Badge>}</td>
                    <td className="px-4 py-3 text-xs">{r.quiz_passed ? <span className="text-easy">Passed</span> : <span className="text-muted-foreground">—</span>}</td>
                    <td className="px-4 py-3 text-right tabular-nums">{r.visits}</td>
                    <td className="px-4 py-3 text-right tabular-nums">{r.minutes}</td>
                    <td className="hidden px-4 py-3 md:table-cell"><div className="h-1.5 overflow-hidden rounded-full bg-muted"><span className="block h-full rounded-full bg-primary" style={{ width: `${(r.minutes / maxMin) * 100}%` }} /></div></td>
                  </tr>); })}
              </tbody>
            </table>
            {!tableRows.length && <p className={cn("p-8 text-center text-sm text-muted-foreground")}>No topics match this filter.</p>}
          </div>
        </Card>
      </div>
    </Page>
  );
}
