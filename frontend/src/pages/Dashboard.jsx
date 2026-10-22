import { Link } from "react-router-dom";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Area, AreaChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { ArrowRight, Award, BookOpen, CheckCircle2, Clock, Flame, Megaphone, Target, Trophy, X, XCircle, Zap } from "lucide-react";
import { api } from "@/lib/api";
import { C, timeAgo } from "@/lib/utils";
import { useAuth } from "@/hooks/useAuth";
import { Button, Card, DifficultyBadge, ErrorState, IconTile, PageSkeleton, Page, Progress, StatCard, chartTooltip } from "@/components/ui";

const ACTIVITY = { solve: [CheckCircle2, "var(--easy)"], lesson: [BookOpen, "var(--chart-1)"], fail: [XCircle, "var(--hard)"], contest: [Trophy, "var(--medium)"], badge: [Award, "var(--chart-5)"] };

export default function Dashboard() {
  const qc = useQueryClient();
  const { refresh } = useAuth();
  const { data: d, isLoading, error, refetch } = useQuery({ queryKey: ["dashboard"], queryFn: () => api.get("/api/dashboard") });
  const dismiss = useMutation({
    mutationFn: ({ id, action }) => api.post(`/api/notifications/${id}/${action}`),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ["dashboard"] }); refresh(); },
  });
  if (isLoading) return <PageSkeleton />;
  if (error) return <ErrorState error={error} retry={refetch} />;
  const s = d.stats;
  const weekSubs = d.week.reduce((a, w) => a + w.submissions, 0);
  const weekSolved = d.week.reduce((a, w) => a + w.solved, 0);

  return (
    <Page>
      <div className="mb-8 flex flex-wrap items-end justify-between gap-4">
        <div>
          <p className="text-sm text-muted-foreground">Welcome back</p>
          <h1 className="text-3xl font-semibold tracking-tight">{d.user.username.split(/[\s_]/)[0]}, ready to ship?</h1>
        </div>
        <Button to={d.continue_learning[0] ? `/learn/${d.continue_learning[0].id}` : "/learn"}>Resume learning <ArrowRight className="ml-1.5 h-4 w-4" /></Button>
      </div>

      {d.announcement && (
        <Card className="mb-8 flex flex-col gap-4 border-primary/30 bg-gradient-to-br from-card to-accent p-5 sm:flex-row sm:items-start">
          <IconTile icon={Megaphone} className="h-9 w-9" />
          <div className="min-w-0 flex-1">
            <p className="mb-1 text-xs text-muted-foreground">New announcement · {timeAgo(d.announcement.at)}</p>
            <h2 className="font-semibold">{d.announcement.title}</h2>
            <p className="mt-1 text-sm text-foreground/80">{d.announcement.content}</p>
          </div>
          <div className="flex shrink-0 gap-2">
            <Button variant="outline" size="sm" onClick={() => dismiss.mutate({ id: d.announcement.id, action: "read" })}>Mark read</Button>
            <Button variant="ghost" size="sm" aria-label="Remove" onClick={() => dismiss.mutate({ id: d.announcement.id, action: "remove" })}><X /></Button>
          </div>
        </Card>
      )}

      <div className="mb-8 grid grid-cols-2 gap-4 md:grid-cols-4">
        <StatCard icon={Zap} label="Total XP" value={s.xp} accent="var(--medium)" sub={d.user.badge ? `${d.user.badge.icon} ${d.user.badge.name}` : "No badge yet"} />
        <StatCard icon={CheckCircle2} label="Problems solved" value={s.solved} accent="var(--easy)" sub={`of ${s.total_problems}`} />
        <StatCard icon={BookOpen} label="Topics completed" value={s.completed_topics} accent="var(--chart-1)" sub={`of ${s.total_topics} topics`} />
        <StatCard icon={Target} label="Next badge" value={d.next_badge ? `${d.next_badge_progress}%` : "All earned"} accent="var(--chart-5)" sub={d.next_badge ? `${d.xp_to_next} XP to ${d.next_badge.name}` : `${d.badges_earned}/${d.badges_total} badges`} />
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        <Card className="p-5 lg:col-span-2">
          <div className="mb-4 flex items-center justify-between">
            <div><h2 className="font-semibold">Activity this week</h2><p className="text-sm text-muted-foreground">{weekSubs} submissions · {s.minutes} min focused overall</p></div>
            <div className="flex items-center gap-1.5 text-xs text-easy"><Flame className="h-3.5 w-3.5" />{weekSolved} accepted</div>
          </div>
          <div className="h-56">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={d.week} margin={{ left: -20, right: 8, top: 8, bottom: 0 }}>
                <defs><linearGradient id="solved" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stopColor={C.primary} stopOpacity={0.5} /><stop offset="100%" stopColor={C.primary} stopOpacity={0} /></linearGradient></defs>
                <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" vertical={false} />
                <XAxis dataKey="day" stroke="var(--muted-foreground)" fontSize={12} tickLine={false} axisLine={false} />
                <YAxis stroke="var(--muted-foreground)" fontSize={12} tickLine={false} axisLine={false} allowDecimals={false} />
                <Tooltip {...chartTooltip} cursor={{ stroke: "var(--border)" }} />
                <Area type="monotone" dataKey="submissions" name="Submissions" stroke={C.primary} strokeWidth={2} fill="url(#solved)" />
                <Area type="monotone" dataKey="solved" name="Accepted" stroke={C.easy} strokeWidth={2} fill="transparent" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </Card>

        <Card className="flex flex-col bg-gradient-to-br from-card to-accent p-5">
          {d.live_test ? (<>
            <div className="mb-2 flex items-center gap-2 text-xs font-medium text-hard"><span className="inline-block h-2 w-2 animate-pulse rounded-full bg-hard" />LIVE NOW</div>
            <h3 className="mb-1 text-lg font-semibold">{d.live_test.title}</h3>
            <p className="mb-4 text-sm text-muted-foreground">{d.live_test.questions} questions · {d.live_test.minutes} minutes</p>
            <div className="mb-5 flex items-center gap-4 text-xs text-muted-foreground"><span className="flex items-center gap-1"><Clock className="h-3.5 w-3.5" /> Proctored</span><span className="flex items-center gap-1"><Zap className="h-3.5 w-3.5" /> XP by difficulty</span></div>
            <Button to={`/tests/${d.live_test.id}`} className="mt-auto w-full">Enter contest</Button>
          </>) : <p className="text-sm text-muted-foreground">No tests published yet.</p>}
        </Card>

        <Card className="p-5 lg:col-span-2">
          <div className="mb-4 flex items-center justify-between"><h2 className="font-semibold">Recommended for you</h2><Link to="/practice" className="text-sm text-primary hover:underline">View all</Link></div>
          {d.recommended.length ? (
            <ul className="divide-y divide-border">
              {d.recommended.map((p) => (
                <li key={p.id}><Link to={`/practice/${p.id}`} className="-mx-2 flex items-center gap-3 rounded-md px-2 py-3 transition-colors hover:bg-muted/40">
                  <span className="w-8 font-mono text-xs text-muted-foreground">{p.id}.</span>
                  <span className="flex-1 truncate text-sm font-medium">{p.title}</span>
                  <span className="hidden text-xs text-muted-foreground sm:inline">+{p.xp} XP</span>
                  <DifficultyBadge difficulty={p.difficulty} />
                </Link></li>
              ))}
            </ul>
          ) : <p className="py-6 text-center text-sm text-muted-foreground">You've solved every problem. Impressive.</p>}
        </Card>

        <Card className="p-5">
          <h2 className="mb-4 font-semibold">Recent activity</h2>
          {d.activity.length ? (
            <ul className="space-y-3">
              {d.activity.map((a, i) => { const [Icon, color] = ACTIVITY[a.kind] || ACTIVITY.lesson; return (
                <li key={i} className="flex items-start gap-3 text-sm">
                  <IconTile icon={Icon} color={color} className="h-6 w-6" iconClass="h-3.5 w-3.5" />
                  <div className="min-w-0 flex-1"><p className="truncate font-medium">{a.what}</p><p className="truncate text-xs text-muted-foreground">{a.meta}</p></div>
                  <span className="whitespace-nowrap text-xs text-muted-foreground">{timeAgo(a.at)}</span>
                </li>); })}
            </ul>
          ) : <p className="text-sm text-muted-foreground">Solve a problem or finish a topic to see activity here.</p>}
        </Card>

        <Card className="p-5 lg:col-span-3">
          <div className="mb-4 flex items-center justify-between"><h2 className="font-semibold">Continue learning</h2><Link to="/learn" className="text-sm text-primary hover:underline">Browse tracks</Link></div>
          <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
            {d.continue_learning.map((t, i) => (
              <Link key={t.id} to={`/learn/${t.id}`} className="group rounded-lg border border-border bg-background/40 p-4 transition-colors hover:border-primary/40">
                <div className="mb-2 flex items-center gap-2"><BookOpen className="h-4 w-4" style={{ color: [C.primary, C.easy, C.violet][i % 3] }} /><span className="text-xs uppercase tracking-wider text-muted-foreground">{t.completed ? "Completed" : t.visits ? `${t.visits} visits` : "Not started"}</span></div>
                <h3 className="mb-1 font-semibold transition-colors group-hover:text-primary">{t.title}</h3>
                <p className="mb-3 line-clamp-2 text-xs text-muted-foreground">{t.tags.join(" · ") || "DSA fundamentals"}</p>
                <Progress value={t.completed ? 100 : Math.min(t.minutes * 10, 90)} className="h-1.5" />
                <p className="mt-1.5 text-xs text-muted-foreground">{t.completed ? "100% complete" : `${t.minutes} min studied`}</p>
              </Link>
            ))}
          </div>
        </Card>
      </div>
    </Page>
  );
}
