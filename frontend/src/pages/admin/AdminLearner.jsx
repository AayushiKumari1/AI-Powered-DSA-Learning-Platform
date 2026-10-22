import { useState } from "react";
import { useParams } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { Area, AreaChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { BookOpen, CheckCircle2, Clock, Code2, MessageCircle, Target, XCircle, Zap } from "lucide-react";
import { api } from "@/lib/api";
import { C, fmtDate, initials, timeAgo } from "@/lib/utils";
import { Badge, Breadcrumbs, Button, Card, DifficultyBadge, Empty, ErrorState, Page, PageSkeleton, StatCard, Tabs, chartTooltip } from "@/components/ui";

export default function AdminLearner() {
  const { id } = useParams();
  const [tab, setTab] = useState("topics");
  const { data: d, isLoading, error, refetch } = useQuery({ queryKey: ["admin-learner", id], queryFn: () => api.get(`/api/admin/learners/${id}`) });
  if (isLoading) return <PageSkeleton />;
  if (error) return <ErrorState error={error} retry={refetch} />;
  const l = d.learner;
  return (
    <Page>
      <Breadcrumbs items={[{ label: "Learners", to: "/admin/learners" }, { label: l.username }]} />
      <div className="mb-6 flex flex-wrap items-center gap-4">
        <span className="grid h-14 w-14 place-items-center rounded-full bg-gradient-to-br from-primary to-chart-5 text-lg font-semibold text-primary-foreground">{initials(l.username)}</span>
        <div className="min-w-0 flex-1">
          <h1 className="text-2xl font-semibold tracking-tight">{l.username} {l.badge && <span className="text-xl" title={l.badge.name}>{l.badge.icon}</span>}</h1>
          <p className="text-sm text-muted-foreground">{l.email} · joined {fmtDate(l.joined)} · last active {l.last_active ? timeAgo(l.last_active) : "never"}</p>
        </div>
        <Button to={`/admin/inbox?user=${l.id}`}><MessageCircle /> Message</Button>
      </div>
      <div className="mb-6 grid grid-cols-2 gap-4 md:grid-cols-5">
        <StatCard icon={Zap} label="XP" value={l.xp} accent="var(--medium)" sub={l.badge?.name} />
        <StatCard icon={BookOpen} label="Topics completed" value={l.completed_topics} accent="var(--chart-1)" />
        <StatCard icon={Code2} label="Problems solved" value={l.solved} accent="var(--easy)" />
        <StatCard icon={Target} label="Acceptance" value={`${l.acceptance}%`} accent="var(--chart-5)" sub={`${l.submissions} submissions`} />
        <StatCard icon={Clock} label="Study time" value={`${l.minutes} min`} accent="var(--hard)" />
      </div>
      <Card className="mb-6 p-5">
        <h2 className="mb-1 font-semibold">Activity · last 30 days</h2><p className="mb-4 text-sm text-muted-foreground">Practice submissions and accepted solutions</p>
        <div className="h-52"><ResponsiveContainer width="100%" height="100%">
          <AreaChart data={d.daily} margin={{ left: -20, right: 8, top: 8, bottom: 0 }}>
            <defs><linearGradient id="lrn" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stopColor={C.primary} stopOpacity={0.45} /><stop offset="100%" stopColor={C.primary} stopOpacity={0} /></linearGradient></defs>
            <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" vertical={false} />
            <XAxis dataKey="label" stroke="var(--muted-foreground)" fontSize={11} tickLine={false} axisLine={false} interval={4} />
            <YAxis stroke="var(--muted-foreground)" fontSize={11} tickLine={false} axisLine={false} allowDecimals={false} />
            <Tooltip {...chartTooltip} cursor={{ stroke: "var(--border)" }} />
            <Area type="monotone" dataKey="submissions" name="Submissions" stroke={C.primary} strokeWidth={2} fill="url(#lrn)" />
            <Area type="monotone" dataKey="accepted" name="Accepted" stroke={C.easy} strokeWidth={2} fill="transparent" />
          </AreaChart></ResponsiveContainer></div>
      </Card>
      <Tabs className="mb-4" value={tab} onChange={setTab} items={[{ value: "topics", label: "Topics", count: d.topics.length }, { value: "practice", label: "Practice", count: d.submissions.length }, { value: "tests", label: "Tests", count: d.tests.length }]} />
      <Card className="overflow-hidden">
        <div className="overflow-x-auto">
          {tab === "topics" && (d.topics.length ? <table className="w-full text-sm">
            <thead><tr className="border-b border-border bg-background/40 text-left text-xs uppercase tracking-wider text-muted-foreground"><th className="h-10 px-4 font-medium">Topic</th><th className="px-4 font-medium">Status</th><th className="px-4 font-medium">Quiz</th><th className="px-4 text-right font-medium">Visits</th><th className="px-4 text-right font-medium">Minutes</th><th className="px-4 font-medium">Last opened</th></tr></thead>
            <tbody>{d.topics.map((t) => <tr key={t.id} className="border-b border-border last:border-0 hover:bg-muted/40"><td className="px-4 py-3 font-medium">{t.title}</td><td className="px-4 py-3">{t.completed ? <Badge tone="easy">Completed</Badge> : <Badge tone="medium">In progress</Badge>}</td><td className="px-4 py-3">{t.quiz_passed ? <CheckCircle2 className="h-4 w-4 text-easy" /> : <span className="text-muted-foreground">—</span>}</td><td className="px-4 py-3 text-right tabular-nums">{t.visits}</td><td className="px-4 py-3 text-right tabular-nums">{t.minutes}</td><td className="px-4 py-3 text-xs text-muted-foreground">{timeAgo(t.last_accessed)}</td></tr>)}</tbody>
          </table> : <Empty icon={BookOpen} title="No topic activity yet" />)}
          {tab === "practice" && (d.submissions.length ? <table className="w-full text-sm">
            <thead><tr className="border-b border-border bg-background/40 text-left text-xs uppercase tracking-wider text-muted-foreground"><th className="h-10 px-4 font-medium">Result</th><th className="px-4 font-medium">Problem</th><th className="px-4 font-medium">Difficulty</th><th className="px-4 font-medium">Language</th><th className="px-4 text-right font-medium">Tests</th><th className="px-4 font-medium">When</th></tr></thead>
            <tbody>{d.submissions.map((s) => <tr key={s.id} className="border-b border-border last:border-0 hover:bg-muted/40"><td className="px-4 py-3">{s.status === "Passed" ? <span className="flex items-center gap-1.5 text-easy"><CheckCircle2 className="h-4 w-4" />Accepted</span> : <span className="flex items-center gap-1.5 text-hard"><XCircle className="h-4 w-4" />Failed</span>}</td><td className="px-4 py-3 font-medium">{s.problem}</td><td className="px-4 py-3"><DifficultyBadge difficulty={s.difficulty} /></td><td className="px-4 py-3 font-mono text-xs">{s.language}</td><td className="px-4 py-3 text-right tabular-nums">{s.passed}/{s.total}</td><td className="px-4 py-3 text-xs text-muted-foreground">{timeAgo(s.at)}</td></tr>)}</tbody>
          </table> : <Empty icon={Code2} title="No practice submissions yet" />)}
          {tab === "tests" && (d.tests.length ? <table className="w-full text-sm">
            <thead><tr className="border-b border-border bg-background/40 text-left text-xs uppercase tracking-wider text-muted-foreground"><th className="h-10 px-4 font-medium">Test</th><th className="px-4 font-medium">Question</th><th className="px-4 font-medium">Difficulty</th><th className="px-4 font-medium">Status</th><th className="px-4 text-right font-medium">Time</th><th className="px-4 text-right font-medium">Marks</th></tr></thead>
            <tbody>{d.tests.map((t, i) => <tr key={i} className="border-b border-border last:border-0 hover:bg-muted/40"><td className="px-4 py-3 text-muted-foreground">{t.test}</td><td className="px-4 py-3 font-medium">{t.problem}</td><td className="px-4 py-3"><DifficultyBadge difficulty={t.difficulty} /></td><td className={`px-4 py-3 ${t.status === "Passed" ? "text-easy" : "text-hard"}`}>{t.status}</td><td className="px-4 py-3 text-right font-mono text-xs text-muted-foreground">{t.time_taken}s</td><td className="px-4 py-3 text-right font-semibold tabular-nums">{t.marks}</td></tr>)}</tbody>
          </table> : <Empty icon={Target} title="No test attempts yet" />)}
        </div>
      </Card>
    </Page>
  );
}
