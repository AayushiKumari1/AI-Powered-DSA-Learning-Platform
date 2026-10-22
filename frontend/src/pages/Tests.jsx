import { useState } from "react";
import { Link } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { CheckCircle2, Clock, FileCheck2, FileSearch, ListChecks, Search, Zap } from "lucide-react";
import { api } from "@/lib/api";
import { Card, DifficultyBadge, Empty, ErrorState, IconTile, Input, Page, PageHeader, PageSkeleton } from "@/components/ui";

export default function Tests() {
  const [q, setQ] = useState("");
  const { data, isLoading, error, refetch } = useQuery({ queryKey: ["tests"], queryFn: () => api.get("/api/tests") });
  if (isLoading) return <PageSkeleton />;
  if (error) return <ErrorState error={error} retry={refetch} />;
  const tests = data.tests.filter((t) => `${t.title} ${t.description || ""}`.toLowerCase().includes(q.toLowerCase()));
  return (
    <Page>
      <PageHeader title="Tests" subtitle="Timed, proctored coding assessments. Each solved question earns XP by difficulty." />
      <Card className="mb-6 p-4"><div className="relative"><Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" /><Input value={q} onChange={(e) => setQ(e.target.value)} placeholder="Search tests…" className="bg-background pl-9" aria-label="Search tests" /></div></Card>
      {tests.length ? (
        <div className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-3">
          {tests.map((t) => (
            <article key={t.id} className="group relative flex flex-col rounded-lg border border-border bg-card p-5 transition-colors hover:border-primary/40">
              <div className="mb-3 flex items-center gap-2"><IconTile icon={FileCheck2} color="var(--hard)" /><DifficultyBadge difficulty={t.level} />
                {t.attempted && <span className="flex items-center gap-1 text-xs text-easy"><CheckCircle2 className="h-3.5 w-3.5" />Attempted</span>}
                <span className="ml-auto font-mono text-xs text-muted-foreground">#{t.id}</span></div>
              <h2 className="font-semibold transition-colors group-hover:text-primary"><Link to={`/tests/${t.id}`} className="after:absolute after:inset-0">{t.title}</Link></h2>
              <p className="mt-1 line-clamp-2 text-sm text-muted-foreground">{t.description || "No description."}</p>
              {t.topics.length > 0 && <div className="mt-3 flex flex-wrap gap-1.5">{t.topics.slice(0, 4).map((x) => <span key={x} className="rounded bg-muted px-2 py-0.5 text-xs text-muted-foreground">{x}</span>)}{t.topics.length > 4 && <span className="text-xs text-muted-foreground">+{t.topics.length - 4}</span>}</div>}
              <div className="mt-4 flex items-center gap-4 border-t border-border pt-3 text-xs text-muted-foreground">
                <span className="flex items-center gap-1"><ListChecks className="h-3.5 w-3.5" />{t.questions} questions</span>
                <span className="flex items-center gap-1"><Clock className="h-3.5 w-3.5" />~{t.minutes} min</span>
                <span className="flex items-center gap-1"><Zap className="h-3.5 w-3.5" />{t.max_xp} XP</span>
              </div>
            </article>
          ))}
        </div>
      ) : <Card><Empty icon={FileSearch} title={q ? `No tests match “${q}”` : "No tests published yet"} text={q ? "Try a different search." : "Check back soon."} /></Card>}
    </Page>
  );
}
