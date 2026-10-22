import { Link } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { ArrowRight, BarChart3, BookOpen, CheckCircle2, Code2, FileCheck2, MessageCircle, MessagesSquare, Quote, Sparkles, Star, StickyNote } from "lucide-react";
import { api } from "@/lib/api";
import { useAuth } from "@/hooks/useAuth";
import { Button } from "@/components/ui";

const FEATURES = [
  { icon: Code2, title: "Coding workspace", body: "Split-pane editor with run/submit, console, languages, and hints — built for flow.", to: "/practice", color: "var(--chart-1)" },
  { icon: BookOpen, title: "Learning tracks", body: "Bite-sized lessons paired with the right practice problem at the right time.", to: "/learn", color: "var(--chart-2)" },
  { icon: BarChart3, title: "Visual analytics", body: "XP breakdowns, quiz pass rates, focus minutes — see where you actually improve.", to: "/analytics", color: "var(--chart-5)" },
  { icon: FileCheck2, title: "Timed contests", body: "Proctored coding tests with ML topic-mastery analysis to test under real conditions.", to: "/tests", color: "var(--medium)" },
  { icon: MessagesSquare, title: "Community", body: "Channels for every topic — get unstuck fast, share approaches, find a study buddy.", to: "/community", color: "var(--chart-2)" },
  { icon: StickyNote, title: "Flash notes", body: "Tiny revision notes for the tricks you keep forgetting. Tag, search, recall.", to: "/notes", color: "var(--chart-3)" },
  { icon: MessageCircle, title: "Ask a mentor", body: "Message the EduMentor team directly and get replies in real time.", to: "/mentor", color: "var(--chart-4)" },
  { icon: Sparkles, title: "AI mentor", body: "Hints before answers, code reviews and study plans from an AI mentor that knows your progress.", to: "/dashboard", color: "var(--easy)" },
];
// Sample quotes — replace with real learner feedback before publishing.
const TESTIMONIALS = [
  { quote: "The topic analytics showed me my graphs gap. Two weeks later I cleared a phone screen with a graph question.", name: "Priya M.", role: "SDE-2" },
  { quote: "I had bounced off LeetCode three times. The learning topics plus the AI mentor's hints made it finally stick.", name: "Daniel K.", role: "New grad SWE" },
  { quote: "The proctored tests are the best part. Real pressure, real results, and a community to debrief with.", name: "Sana R.", role: "Software engineer" },
];

export default function Landing() {
  const { user } = useAuth();
  const { data: s } = useQuery({ queryKey: ["stats"], queryFn: () => api.get("/api/stats") });
  const appTo = user ? "/dashboard" : "/auth";
  const stats = [
    { label: "Active learners", value: s?.learners }, { label: "Learning topics", value: s?.topics },
    { label: "Coding problems", value: s?.problems }, { label: "Code submissions", value: s?.submissions },
  ];

  return (
    <div className="min-h-screen bg-background text-foreground">
      <header className="sticky top-0 z-30 border-b border-border bg-background/70 backdrop-blur-md">
        <div className="mx-auto flex h-14 max-w-6xl items-center gap-4 px-4 md:px-6">
          <Link to="/" className="flex items-center gap-2">
            <div className="grid h-7 w-7 place-items-center rounded-md bg-primary font-mono text-sm font-bold text-primary-foreground">E</div>
            <span className="font-semibold tracking-tight">EduMentor</span>
          </Link>
          <nav className="ml-6 hidden items-center gap-5 text-sm text-muted-foreground md:flex">
            <Link to="/practice" className="transition-colors hover:text-foreground">Practice</Link>
            <Link to="/learn" className="transition-colors hover:text-foreground">Learn</Link>
            <Link to="/tests" className="transition-colors hover:text-foreground">Contests</Link>
            <Link to="/analytics" className="transition-colors hover:text-foreground">Analytics</Link>
          </nav>
          <div className="ml-auto flex items-center gap-2">
            {!user && <Button variant="ghost" size="sm" to="/auth" className="hidden sm:inline-flex">Sign in</Button>}
            <Button size="sm" to={appTo}>Open app <ArrowRight className="ml-1 h-4 w-4" /></Button>
          </div>
        </div>
      </header>

      <section className="relative overflow-hidden">
        <div className="pointer-events-none absolute inset-0" aria-hidden style={{ background: "radial-gradient(ellipse 60% 50% at 50% 0%, var(--accent-glow), transparent 70%)" }} />
        <div className="relative mx-auto max-w-6xl px-4 pb-20 pt-16 text-center md:px-6 md:pb-28 md:pt-24">
          <div className="mb-6 inline-flex items-center gap-2 rounded-full border border-border bg-card/60 px-3 py-1 text-xs text-muted-foreground">
            <Sparkles className="h-3.5 w-3.5 text-medium" />v2.0 — Visual analytics & adaptive practice
          </div>
          <h1 className="mb-5 text-4xl font-semibold leading-[1.05] tracking-tight md:text-6xl">
            Learn DSA the way<br />
            <span className="bg-gradient-to-r from-primary via-chart-5 to-primary bg-clip-text text-transparent">top engineers actually practice.</span>
          </h1>
          <p className="mx-auto mb-8 max-w-2xl text-base text-muted-foreground md:text-lg">
            Structured lessons, a LeetCode-style coding workspace, deep visual analytics, and timed contests — all in one focused dark IDE.
          </p>
          <div className="flex flex-wrap items-center justify-center gap-3">
            <Button size="lg" to={user ? "/dashboard" : "/auth?mode=signup"}>Start practicing — free <ArrowRight className="ml-1.5 h-4 w-4" /></Button>
            <Button size="lg" variant="outline" to="/practice">Browse problems</Button>
          </div>
          <div className="mt-10 flex flex-wrap items-center justify-center gap-x-6 gap-y-2 text-xs text-muted-foreground">
            {[`${s?.problems ?? "20"}+ curated problems`, `${s?.topics ?? "50"} learning topics`, "Proctored contests", "Visual progress"].map((f) => (
              <span key={f} className="inline-flex items-center gap-1.5"><CheckCircle2 className="h-3.5 w-3.5 text-easy" /> {f}</span>
            ))}
          </div>
        </div>
      </section>

      <section className="mx-auto max-w-6xl px-4 pb-20 md:px-6">
        <div className="mb-16 grid grid-cols-2 gap-px overflow-hidden rounded-2xl border border-border bg-border md:grid-cols-4">
          {stats.map((st) => (
            <div key={st.label} className="bg-card px-6 py-6 text-center">
              <p className="bg-gradient-to-b from-foreground to-muted-foreground bg-clip-text text-2xl font-semibold tracking-tight text-transparent md:text-3xl">{st.value != null ? st.value.toLocaleString() : "—"}</p>
              <p className="mt-1 text-xs uppercase tracking-wider text-muted-foreground">{st.label}</p>
            </div>
          ))}
        </div>

        <div className="mb-10 text-center">
          <p className="mb-2 text-xs uppercase tracking-widest text-muted-foreground">Everything in one workspace</p>
          <h2 className="text-2xl font-semibold tracking-tight md:text-3xl">Built to make practice click.</h2>
        </div>
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          {FEATURES.map((f) => (
            <Link key={f.title} to={f.to} className="group rounded-xl border border-border bg-card p-5 transition-colors hover:border-primary/40">
              <div className="mb-4 grid h-10 w-10 place-items-center rounded-lg" style={{ background: `color-mix(in oklab, ${f.color} 18%, transparent)`, color: f.color }}><f.icon className="h-5 w-5" /></div>
              <h3 className="mb-1.5 font-semibold transition-colors group-hover:text-primary">{f.title}</h3>
              <p className="text-sm text-muted-foreground">{f.body}</p>
            </Link>
          ))}
        </div>

        <div className="glow-border mt-16 overflow-hidden rounded-2xl border border-border bg-card shadow-2xl">
          <div className="flex items-center gap-2 border-b border-border bg-background/60 px-4 py-2.5">
            <div className="flex gap-1.5"><span className="h-2.5 w-2.5 rounded-full bg-hard/60" /><span className="h-2.5 w-2.5 rounded-full bg-medium/60" /><span className="h-2.5 w-2.5 rounded-full bg-easy/60" /></div>
            <span className="ml-2 font-mono text-xs text-muted-foreground">edumentor · two_sum.py</span>
          </div>
          <div className="grid font-mono text-xs md:grid-cols-2 md:text-sm">
            <div className="border-b border-border p-5 md:border-b-0 md:border-r">
              <p className="mb-2 text-muted-foreground"># Problem</p>
              <p className="text-foreground/90">Given an array of integers <span className="text-primary">nums</span> and an integer <span className="text-primary">target</span>, return the indices of the two numbers that add up to <span className="text-primary">target</span>.</p>
            </div>
            <div className="bg-background/40 p-5 text-foreground/90">
              <pre className="leading-relaxed"><code>{`def two_sum(nums, target):
    seen = {}
    for i, x in enumerate(nums):
        if target - x in seen:
            return [seen[target - x], i]
        seen[x] = i`}</code></pre>
              <p className="mt-3 text-easy">✓ Accepted · 4/4 test cases · AI efficiency 9/10</p>
            </div>
          </div>
        </div>

        <div className="mt-20">
          <div className="mb-10 text-center">
            <p className="mb-2 text-xs uppercase tracking-widest text-muted-foreground">Loved by interviewers & interviewees</p>
            <h2 className="text-2xl font-semibold tracking-tight md:text-3xl">From "scared of DP" to interview-ready in 8 weeks.</h2>
          </div>
          <div className="grid gap-4 md:grid-cols-3">
            {TESTIMONIALS.map((t) => (
              <figure key={t.name} className="rounded-xl border border-border bg-card p-5">
                <Quote className="mb-3 h-5 w-5 text-primary/60" />
                <blockquote className="mb-4 text-sm leading-relaxed text-foreground/90">"{t.quote}"</blockquote>
                <figcaption className="flex items-center gap-3 border-t border-border pt-3">
                  <div className="grid h-9 w-9 place-items-center rounded-full bg-gradient-to-br from-primary to-chart-5 text-xs font-semibold text-primary-foreground">{t.name.split(" ").map((p) => p[0]).join("")}</div>
                  <div><p className="text-sm font-medium leading-tight">{t.name}</p><p className="text-xs text-muted-foreground">{t.role}</p></div>
                  <div className="ml-auto flex text-medium" aria-label="5 stars">{Array.from({ length: 5 }).map((_, i) => <Star key={i} className="h-3 w-3 fill-current" />)}</div>
                </figcaption>
              </figure>
            ))}
          </div>
        </div>

        <div className="relative mt-20 overflow-hidden rounded-2xl border border-border bg-gradient-to-br from-card via-card to-accent p-10 text-center md:p-14">
          <div className="pointer-events-none absolute inset-0 opacity-60" aria-hidden style={{ background: "radial-gradient(ellipse 60% 60% at 50% 0%, var(--accent-glow), transparent 70%)" }} />
          <div className="relative">
            <h2 className="mb-3 text-2xl font-semibold tracking-tight md:text-4xl">Your future self has shipped 200 problems.</h2>
            <p className="mx-auto mb-6 max-w-xl text-muted-foreground">Free forever for individual learners. No credit card. Start with today's daily challenge.</p>
            <div className="flex flex-wrap items-center justify-center gap-3">
              <Button size="lg" to={appTo}>Open EduMentor <ArrowRight className="ml-1.5 h-4 w-4" /></Button>
              <Button size="lg" variant="outline" to="/learn">See learning tracks</Button>
            </div>
          </div>
        </div>
      </section>

      <footer className="border-t border-border">
        <div className="mx-auto flex max-w-6xl flex-wrap items-center justify-between gap-3 px-4 py-8 text-xs text-muted-foreground md:px-6">
          <span>© {new Date().getFullYear()} EduMentor. Built for serious learners.</span>
          <div className="flex items-center gap-4">
            <Link to="/learn" className="hover:text-foreground">Learn</Link>
            <Link to="/practice" className="hover:text-foreground">Practice</Link>
            <Link to="/analytics" className="hover:text-foreground">Analytics</Link>
            <Link to="/admin/login" className="hover:text-foreground">Admin</Link>
          </div>
        </div>
      </footer>
    </div>
  );
}
