import { useMemo, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Bookmark, BookOpen, CheckCircle2, Clock, RotateCcw, Search } from "lucide-react";
import { api } from "@/lib/api";
import { cn } from "@/lib/utils";
import { Card, Empty, ErrorState, Input, Page, PageHeader, PageSkeleton, Progress, Tabs } from "@/components/ui";

export default function Learn() {
  const [params, setParams] = useSearchParams();
  const search = params.get("search") || "";
  const [filter, setFilter] = useState("all");
  const qc = useQueryClient();
  const { data, isLoading, error, refetch } = useQuery({ queryKey: ["topics", search], queryFn: () => api.get(`/api/topics?search=${encodeURIComponent(search)}`) });
  const bookmark = useMutation({ mutationFn: (id) => api.post(`/api/topics/${id}/bookmark`), onSuccess: () => qc.invalidateQueries({ queryKey: ["topics"] }) });
  const topics = data?.topics || [];
  const shown = useMemo(() => topics.filter((t) => filter === "all" || (filter === "done" && t.completed) || (filter === "todo" && !t.completed) || (filter === "saved" && t.bookmarked)), [topics, filter]);
  if (isLoading) return <PageSkeleton />;
  if (error) return <ErrorState error={error} retry={refetch} />;
  const done = topics.filter((t) => t.completed).length;

  return (
    <Page>
      <PageHeader title="Learn" subtitle={search ? `Results for “${search}”` : "Master data structures and algorithms one topic at a time."} />
      <Card className="mb-6 p-4">
        <div className="flex flex-col gap-3 md:flex-row md:items-center">
          <form className="relative flex-1" onSubmit={(e) => { e.preventDefault(); setParams(e.target.q.value ? { search: e.target.q.value } : {}); }}>
            <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
            <Input name="q" defaultValue={search} key={search} placeholder="Search topics by name or tag…" className="border-border bg-background pl-9" aria-label="Search topics" />
          </form>
          <Tabs value={filter} onChange={setFilter} items={[{ value: "all", label: "All", count: topics.length }, { value: "todo", label: "To do" }, { value: "done", label: "Completed" }, { value: "saved", label: "Bookmarked" }]} />
        </div>
        <div className="mt-4 flex items-center gap-3"><Progress value={topics.length ? (done / topics.length) * 100 : 0} className="h-1.5" /><span className="whitespace-nowrap text-xs text-muted-foreground">{done} / {topics.length} completed</span></div>
      </Card>

      {shown.length ? (
        <div className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-3">
          {shown.map((t) => (
            <article key={t.id} className="group relative flex flex-col rounded-lg border border-border bg-card p-4 transition-colors hover:border-primary/40">
              <div className="mb-2 flex items-center gap-2">
                {t.completed ? <CheckCircle2 className="h-4 w-4 text-easy" /> : <BookOpen className="h-4 w-4 text-primary" />}
                <span className="text-xs uppercase tracking-wider text-muted-foreground">{t.completed ? "Completed" : t.visits ? "In progress" : "Not started"}</span>
                <button onClick={() => bookmark.mutate(t.id)} aria-pressed={t.bookmarked} aria-label={t.bookmarked ? "Remove bookmark" : "Bookmark"}
                  className={cn("relative z-10 ml-auto grid h-7 w-7 place-items-center rounded-md hover:bg-accent", t.bookmarked ? "text-medium" : "text-muted-foreground")}>
                  <Bookmark className={cn("h-4 w-4", t.bookmarked && "fill-current")} />
                </button>
              </div>
              <h2 className="mb-2 font-semibold transition-colors group-hover:text-primary"><Link to={`/learn/${t.id}`} className="after:absolute after:inset-0">{t.title}</Link></h2>
              {t.tags.length > 0 && <div className="mb-3 flex flex-wrap gap-1.5">{t.tags.map((g) => <span key={g} className="rounded bg-muted px-2 py-0.5 text-xs text-muted-foreground">{g}</span>)}</div>}
              <div className="mt-auto flex items-center gap-4 border-t border-border pt-3 text-xs text-muted-foreground">
                <span className="flex items-center gap-1"><RotateCcw className="h-3.5 w-3.5" />{t.visits} visits</span>
                <span className="flex items-center gap-1"><Clock className="h-3.5 w-3.5" />{Math.floor(t.seconds / 60)}m {t.seconds % 60}s</span>
                <span className={cn("ml-auto font-medium", t.completed ? "text-easy" : "text-primary")}>{t.completed ? "+10 XP earned" : t.visits ? "Continue →" : "Start →"}</span>
              </div>
            </article>
          ))}
        </div>
      ) : <Card><Empty icon={Search} title="No topics found" text="Try a shorter search or a different filter." /></Card>}
    </Page>
  );
}
