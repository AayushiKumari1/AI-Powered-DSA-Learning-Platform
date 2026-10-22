import { Link } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { Area, AreaChart, Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { Activity, ArrowRight, BookOpen, CheckCircle2, Code2, FileCheck2, Users, XCircle } from "lucide-react";
import { api } from "@/lib/api";
import { C, initials, timeAgo } from "@/lib/utils";
import { Button, Card, DifficultyBadge, ErrorState, Page, PageSkeleton, StatCard, chartTooltip } from "@/components/ui";

export default function AdminDashboard() {
  const { data: d, isLoading, error, refetch } = useQuery({ queryKey: ["admin-dashboard"], queryFn: () => api.get("/api/admin/dashboard") });
  if (isLoading) return <PageSkeleton />;
  if (error) return <ErrorState error={error} retry={refetch} />;
  const c = d.counts;
  return (
    <Page>
      <div className="mb-8 flex flex-wrap items-end justify-between gap-4">
        <div><p className="text-sm text-muted-foreground">Admin console</p><h1 className="text-3xl font-semibold tracking-tight">Platform overview</h1></div>
        <Button to="/admin/learners">Learner analytics <ArrowRight /></Button>
      </div>
      <div className="mb-8 grid grid-cols-2 gap-4 md:grid-cols-4">
        <StatCard icon={Users} label="Learners" value={c.learners} accent="var(--chart-1)" sub={`${c.active_14d} active in 14 days`} />
        <StatCard icon={Activity} label="Submissions" value={c.submissions} accent="var(--chart-5)" sub={`${c.acceptance}% accepted`} />
        <StatCard icon={BookOpen} label="Topics" value={c.topics} accent="var(--easy)" sub={`${c.announcements} announcements sent`} />
        <StatCard icon={Code2} label="Problems · Tests" value={`${c.problems} · ${c.tests}`} accent="var(--hard)" sub="Practice bank and assessments" />
      </div>
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        <Card className="p-5 lg:col-span-2">
          <div className="mb-4 flex items-start justify-between"><div><h2 className="font-semibold">Platform activity</h2><p className="text-sm text-muted-foreground">Submissions and accepted solutions · last 14 days</p></div>
            <div className="flex gap-3 text-xs text-muted-foreground"><span className="flex items-center gap-1.5"><span className="h-2 w-2 rounded-sm" style={{ background: C.primary }} />Submissions</span><span className="flex items-center gap-1.5"><span className="h-2 w-2 rounded-sm" style={{ background: C.easy }} />Accepted</span></div></div>
          <div className="h-60"><ResponsiveContainer width="100%" height="100%">
            <AreaChart data={d.activity} margin={{ left: -20, right: 8, top: 8, bottom: 0 }}>
              <defs><linearGradient id="adm" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stopColor={C.primary} stopOpacity={0.45} /><stop offset="100%" stopColor={C.primary} stopOpacity={0} /></linearGradient></defs>
              <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" vertical={false} />
              <XAxis dataKey="label" stroke="var(--muted-foreground)" fontSize={11} tickLine={false} axisLine={false} interval={2} />
              <YAxis stroke="var(--muted-foreground)" fontSize={11} tickLine={false} axisLine={false} allowDecimals={false} />
              <Tooltip {...chartTooltip} cursor={{ stroke: "var(--border)" }} />
              <Area type="monotone" dataKey="submissions" name="Submissions" stroke={C.primary} strokeWidth={2} fill="url(#adm)" />
              <Area type="monotone" dataKey="accepted" name="Accepted" stroke={C.easy} strokeWidth={2} fill="transparent" />
            </AreaChart></ResponsiveContainer></div>
        </Card>
        <Card className="p-5">
          <div className="mb-4 flex items-center justify-between"><h2 className="font-semibold">Top learners</h2><Link to="/admin/learners" className="text-sm text-primary hover:underline">All</Link></div>
          <ol className="space-y-3">
            {d.top_learners.map((u, i) => (
              <li key={u.id}><Link to={`/admin/learners/${u.id}`} className="-mx-2 flex items-center gap-3 rounded-md px-2 py-1.5 hover:bg-muted/40">
                <span className={`w-4 font-mono text-xs ${i < 3 ? "text-medium" : "text-muted-foreground"}`}>{i + 1}</span>
                <span className="grid h-8 w-8 place-items-center rounded-full bg-gradient-to-br from-primary to-chart-5 text-xs font-semibold text-primary-foreground">{initials(u.username)}</span>
                <span className="flex-1 truncate text-sm font-medium">{u.username}</span><span className="text-sm font-semibold tabular-nums">{u.xp} XP</span>
              </Link></li>
            ))}
          </ol>
        </Card>
        <Card className="overflow-hidden lg:col-span-2">
          <h2 className="border-b border-border px-5 py-4 font-semibold">Recent submissions</h2>
          <ul className="divide-y divide-border">
            {d.recent_submissions.map((s, i) => (
              <li key={i} className="flex items-center gap-3 px-5 py-3 text-sm">
                {s.status === "Passed" ? <CheckCircle2 className="h-4 w-4 shrink-0 text-easy" /> : <XCircle className="h-4 w-4 shrink-0 text-hard" />}
                <Link to={`/admin/learners/${s.user_id}`} className="font-medium hover:text-primary">{s.user}</Link>
                <span className="min-w-0 flex-1 truncate text-muted-foreground">{s.problem}</span>
                <span className="hidden rounded bg-muted px-1.5 py-0.5 font-mono text-xs sm:inline">{s.language}</span>
                <span className="w-12 text-right text-xs tabular-nums text-muted-foreground">{s.passed}/{s.total}</span>
                <span className="w-16 text-right text-xs text-muted-foreground">{timeAgo(s.at)}</span>
              </li>
            ))}
          </ul>
        </Card>
        <div className="space-y-6">
          <Card className="p-5">
            <h2 className="mb-4 font-semibold">Problem bank</h2>
            {["easy", "medium", "hard"].map((k) => { const v = d.problems_by_difficulty[k] || 0, max = Math.max(...Object.values(d.problems_by_difficulty), 1); return (
              <div key={k} className="mb-3 flex items-center gap-3"><span className="w-20"><DifficultyBadge difficulty={k} /></span><div className="h-1.5 flex-1 overflow-hidden rounded-full bg-muted"><span className="block h-full rounded-full" style={{ width: `${(v / max) * 100}%`, background: C[k] }} /></div><span className="w-6 text-right text-sm font-medium tabular-nums">{v}</span></div>); })}
            <Button variant="outline" size="sm" className="mt-2 w-full" to="/admin/problems/new">Add a problem</Button>
          </Card>
          <Card className="p-5">
            <h2 className="mb-1 font-semibold">Badge distribution</h2><p className="mb-3 text-xs text-muted-foreground">Learners holding each badge</p>
            <div className="h-40"><ResponsiveContainer width="100%" height="100%">
              <BarChart data={d.badges} margin={{ left: -28, right: 0, top: 4, bottom: 0 }}>
                <XAxis dataKey="icon" tickLine={false} axisLine={false} fontSize={14} />
                <YAxis allowDecimals={false} tickLine={false} axisLine={false} fontSize={11} stroke="var(--muted-foreground)" />
                <Tooltip {...chartTooltip} labelFormatter={(_, p) => p?.[0]?.payload?.name} />
                <Bar dataKey="count" name="Learners" fill={C.violet} radius={[4, 4, 0, 0]} />
              </BarChart></ResponsiveContainer></div>
          </Card>
        </div>
      </div>
    </Page>
  );
}
