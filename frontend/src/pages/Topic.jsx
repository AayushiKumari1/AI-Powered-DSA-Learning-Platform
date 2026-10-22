import { useEffect, useRef, useState } from "react";
import { useParams } from "react-router-dom";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { Brain, Check, CheckCircle2, Clock, Play, RotateCcw, Sparkles, VideoOff } from "lucide-react";
import { api } from "@/lib/api";
import { cn } from "@/lib/utils";
import { useAuth } from "@/hooks/useAuth";
import { openMentor } from "@/components/AiMentor";
import { Badge, Breadcrumbs, Button, Card, Empty, ErrorState, Page, PageSkeleton } from "@/components/ui";

function useStudyTimer(topicId) {
  const [active, setActive] = useState(0);
  const unsent = useRef(0);
  useEffect(() => {
    const url = `/study/${topicId}/track-time`;   // existing Flask endpoint
    const flush = () => {
      if (unsent.current <= 0) return;
      navigator.sendBeacon(url, new Blob([JSON.stringify({ seconds: unsent.current })], { type: "application/json" }));
      unsent.current = 0;
    };
    const tick = setInterval(() => { if (document.visibilityState === "visible") { unsent.current++; setActive((a) => a + 1); } }, 1000);
    const periodic = setInterval(flush, 60000);
    const onHide = () => document.visibilityState === "hidden" && flush();
    document.addEventListener("visibilitychange", onHide);
    window.addEventListener("pagehide", flush);
    return () => { clearInterval(tick); clearInterval(periodic); document.removeEventListener("visibilitychange", onHide); window.removeEventListener("pagehide", flush); flush(); };
  }, [topicId]);
  return active;
}

export default function Topic() {
  const { id } = useParams();
  const qc = useQueryClient();
  const { refresh } = useAuth();
  const { data, isLoading, error, refetch } = useQuery({ queryKey: ["topic", id], queryFn: () => api.get(`/api/topics/${id}`), staleTime: Infinity });
  const [video, setVideo] = useState(null);
  const session = useStudyTimer(id);
  const complete = useMutation({
    mutationFn: () => api.post(`/api/topics/${id}/complete`),
    onSuccess: (r) => { toast.success(r.already ? "Already completed" : "Topic completed · +10 XP"); qc.setQueryData(["topic", id], (d) => ({ ...d, progress: { ...d.progress, completed: true } })); qc.invalidateQueries({ queryKey: ["topics"] }); refresh(); },
    onError: (e) => toast.error(e.message),
  });
  if (isLoading) return <PageSkeleton />;
  if (error) return <ErrorState error={error} retry={refetch} />;
  const { topic, progress: p, videos } = data;
  const current = video || videos[0];

  return (
    <Page>
      <Breadcrumbs items={[{ label: "Learn", to: "/learn" }, { label: topic.title }]} />
      <div className="mb-6 flex flex-wrap items-end justify-between gap-4">
        <div className="min-w-0">
          <h1 className="text-3xl font-semibold tracking-tight">{topic.title}</h1>
          {topic.tags.length > 0 && <div className="mt-3 flex flex-wrap gap-1.5">{topic.tags.map((t) => <span key={t} className="rounded bg-muted px-2 py-0.5 text-xs text-muted-foreground">{t}</span>)}</div>}
        </div>
        {p.completed && <Badge tone="easy" className="px-3 py-1 text-sm"><CheckCircle2 className="h-4 w-4" /> Completed · +10 XP</Badge>}
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-[minmax(0,1fr)_320px]">
        <div className="min-w-0 space-y-6">
          <Card className="p-6">
            {topic.description
              ? <div className="prose-dark" dangerouslySetInnerHTML={{ __html: topic.description }} />
              : <p className="text-sm text-muted-foreground">No written lesson for this topic yet. Start with the videos below.</p>}
          </Card>
          <Card className="p-5">
            <div className="mb-4 flex items-center justify-between"><h2 className="font-semibold">Video lessons</h2><span className="text-xs text-muted-foreground">{videos.length} curated from YouTube</span></div>
            {current ? (<>
              <div className="aspect-video overflow-hidden rounded-lg border border-border bg-background">
                <iframe key={current.id} className="h-full w-full" src={`https://www.youtube.com/embed/${current.id}${video ? "?autoplay=1" : ""}`} title={current.title} allow="accelerometer; encrypted-media; gyroscope; picture-in-picture" allowFullScreen />
              </div>
              {videos.length > 1 && (
                <ul className="mt-4 grid grid-cols-1 gap-3 sm:grid-cols-2 xl:grid-cols-3">
                  {videos.map((v) => (
                    <li key={v.id}><button onClick={() => setVideo(v)} aria-pressed={current.id === v.id}
                      className={cn("group flex w-full flex-col overflow-hidden rounded-lg border bg-background/40 text-left transition-colors hover:border-primary/40", current.id === v.id ? "border-primary/60" : "border-border")}>
                      <span className="relative block aspect-video w-full overflow-hidden bg-muted">
                        {v.thumbnail && <img src={v.thumbnail} alt="" loading="lazy" className="h-full w-full object-cover" />}
                        <span className="absolute inset-0 grid place-items-center bg-black/30 opacity-0 transition-opacity group-hover:opacity-100"><Play className="h-6 w-6 text-white" /></span>
                      </span>
                      <span className="line-clamp-2 p-2.5 text-xs font-medium">{v.title}</span>
                    </button></li>
                  ))}
                </ul>
              )}
            </>) : <Empty icon={VideoOff} title="No videos available" text="Video suggestions need the YouTube API key in the backend .env file." />}
          </Card>
        </div>

        <aside className="space-y-4 lg:sticky lg:top-20 lg:self-start">
          <Card className="p-5">
            <h2 className="mb-4 font-semibold">Your progress</h2>
            <dl className="grid grid-cols-2 gap-3">
              <div className="rounded-md border border-border bg-background/40 p-3"><dt className="flex items-center gap-1 text-xs text-muted-foreground"><Clock className="h-3.5 w-3.5" /> Time spent</dt><dd className="mt-1 font-semibold">{Math.floor((p.seconds + session) / 60)}m {(p.seconds + session) % 60}s</dd></div>
              <div className="rounded-md border border-border bg-background/40 p-3"><dt className="flex items-center gap-1 text-xs text-muted-foreground"><RotateCcw className="h-3.5 w-3.5" /> Visits</dt><dd className="mt-1 font-semibold">{p.visits}</dd></div>
            </dl>
            <p className="mt-3 flex items-center gap-1.5 text-xs text-muted-foreground"><span className="h-2 w-2 animate-pulse rounded-full bg-easy" /> This session: <span className="font-mono text-foreground">{Math.floor(session / 60)}:{String(session % 60).padStart(2, "0")}</span></p>
            <div className="my-4 h-px bg-border" />
            {p.completed
              ? <p className="flex items-center gap-2 text-sm"><CheckCircle2 className="h-4 w-4 text-easy" /> You completed this topic.</p>
              : <Button variant="outline" className="w-full" loading={complete.isPending} onClick={() => complete.mutate()}><Check /> Mark as completed · +10 XP</Button>}
          </Card>
          <Card className="bg-gradient-to-br from-card to-accent p-5">
            <div className="mb-2 flex items-center gap-2 text-xs font-medium text-chart-5"><Brain className="h-3.5 w-3.5" /> AI QUIZ</div>
            <h3 className="font-semibold">Check your understanding</h3>
            <p className="mt-1 text-sm text-muted-foreground">5 fresh questions. Score 3 or more to complete the topic and earn 10 XP.</p>
            <Button to={`/learn/${id}/quiz`} className="mt-4 w-full">{p.quiz_passed ? "Retake the quiz" : "Take the quiz"}</Button>
          </Card>
          <Button variant="ghost" className="w-full justify-start text-muted-foreground" onClick={() => openMentor(`Explain ${topic.title} with an example`)}><Sparkles className="text-medium" /> Ask the AI mentor about {topic.title}</Button>
        </aside>
      </div>
    </Page>
  );
}
