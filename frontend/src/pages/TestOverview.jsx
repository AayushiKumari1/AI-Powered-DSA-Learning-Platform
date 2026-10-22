import { useParams } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { ClipboardX, Clock, ListChecks, Maximize, Play, Send, TriangleAlert, Video, Zap } from "lucide-react";
import { api } from "@/lib/api";
import { Breadcrumbs, Button, Card, DifficultyBadge, ErrorState, Page, PageSkeleton } from "@/components/ui";

export default function TestOverview() {
  const { id } = useParams();
  const { data, isLoading, error, refetch } = useQuery({ queryKey: ["test", id], queryFn: () => api.get(`/api/tests/${id}`) });
  if (isLoading) return <PageSkeleton />;
  if (error) return <ErrorState error={error} retry={refetch} />;
  const t = data.test;
  return (
    <Page>
      <Breadcrumbs items={[{ label: "Tests", to: "/tests" }, { label: t.title }]} />
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        <div className="space-y-6 lg:col-span-2">
          <Card className="p-6">
            <div className="mb-2 flex items-center gap-2"><DifficultyBadge difficulty={t.level} /></div>
            <h1 className="text-2xl font-semibold tracking-tight">{t.title}</h1>
            <p className="mt-2 text-sm text-muted-foreground">{t.description || "No description provided."}</p>
            {t.topics.length > 0 && <div className="mt-4 flex flex-wrap gap-1.5">{t.topics.map((x) => <span key={x} className="rounded bg-muted px-2 py-0.5 text-xs text-muted-foreground">{x}</span>)}</div>}
            <div className="mt-6 grid grid-cols-3 gap-3">
              {[[ListChecks, "Questions", t.questions.length], [Clock, "Suggested time", `${t.minutes} min`], [Zap, "Max XP", t.max_xp]].map(([I, l, v]) => (
                <div key={l} className="rounded-md border border-border bg-background/40 p-3"><p className="flex items-center gap-1 text-xs text-muted-foreground"><I className="h-3.5 w-3.5" />{l}</p><p className="mt-1 font-semibold">{v}</p></div>
              ))}
            </div>
          </Card>
          <Card className="overflow-hidden">
            <h2 className="border-b border-border px-5 py-4 font-semibold">Questions</h2>
            <ol className="divide-y divide-border">
              {t.questions.map((q, i) => (
                <li key={q.id} className="flex items-center gap-3 px-5 py-3"><span className="w-6 font-mono text-xs text-muted-foreground">{i + 1}.</span><span className="flex-1 truncate text-sm font-medium">{q.title}</span><span className="hidden text-xs text-muted-foreground sm:inline">+{q.xp} XP</span><DifficultyBadge difficulty={q.difficulty} /></li>
              ))}
              {!t.questions.length && <li className="p-5 text-sm text-muted-foreground">This test has no questions yet.</li>}
            </ol>
          </Card>
        </div>
        <aside className="lg:sticky lg:top-20 lg:self-start">
          <Card className="bg-gradient-to-br from-card to-accent p-5">
            <div className="mb-2 flex items-center gap-2 text-xs font-medium text-hard"><span className="inline-block h-2 w-2 animate-pulse rounded-full bg-hard" /> PROCTORED</div>
            <h2 className="text-lg font-semibold">Before you start</h2>
            <ul className="mt-3 space-y-2.5 text-sm">
              {[[Maximize, "The test runs in fullscreen"], [Video, "Camera and microphone are monitored"], [ClipboardX, "Copy, paste and right-click are disabled"], [TriangleAlert, "3 violations submit the test automatically"], [Send, "Submit each answer before moving on"]].map(([I, x]) => (
                <li key={x} className="flex items-start gap-2"><I className="mt-0.5 h-4 w-4 shrink-0 text-muted-foreground" />{x}</li>
              ))}
            </ul>
            {t.questions.length > 0 && <Button to={`/tests/${id}/solve/0`} className="mt-5 w-full"><Play /> Start test</Button>}
            <Button variant="ghost" to={`/tests/${id}/result`} className="mt-2 w-full">View my last result</Button>
          </Card>
        </aside>
      </div>
    </Page>
  );
}
