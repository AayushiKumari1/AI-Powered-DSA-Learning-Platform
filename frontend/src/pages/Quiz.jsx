import { useState } from "react";
import { useParams } from "react-router-dom";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { CheckCircle2, RotateCcw, Send, TriangleAlert, XCircle, Zap } from "lucide-react";
import { api } from "@/lib/api";
import { cn } from "@/lib/utils";
import { useAuth } from "@/hooks/useAuth";
import { Badge, Breadcrumbs, Button, Card, Empty, Page, Progress, Skeleton } from "@/components/ui";

const L = ["A", "B", "C", "D", "E", "F"];

export default function Quiz() {
  const { id } = useParams();
  const qc = useQueryClient();
  const { refresh } = useAuth();
  const [answers, setAnswers] = useState({});
  const [result, setResult] = useState(null);
  const quiz = useQuery({ queryKey: ["quiz", id], queryFn: () => api.get(`/api/topics/${id}/quiz`), staleTime: Infinity, gcTime: 0 });
  const submit = useMutation({
    mutationFn: () => api.post(`/api/topics/${id}/quiz`, { answers: (quiz.data?.questions || []).map((_, i) => answers[i] ?? null) }),
    onSuccess: (r) => { setResult(r); window.scrollTo({ top: 0, behavior: "smooth" }); qc.invalidateQueries({ queryKey: ["topic", id] }); qc.invalidateQueries({ queryKey: ["topics"] }); refresh(); },
    onError: (e) => toast.error(e.message),
  });
  function retry() { setAnswers({}); setResult(null); qc.removeQueries({ queryKey: ["quiz", id] }); quiz.refetch(); }

  const qs = quiz.data?.questions || [];
  const title = quiz.data?.topic?.title || "Topic";
  const answered = Object.keys(answers).length;

  return (
    <Page className="max-w-3xl">
      <Breadcrumbs items={[{ label: "Learn", to: "/learn" }, { label: title, to: `/learn/${id}` }, { label: "Quiz" }]} />
      {result ? (<>
        <Card className="mb-6 flex flex-col items-center gap-5 p-8 text-center sm:flex-row sm:text-left">
          <div className={cn("grid h-24 w-24 shrink-0 place-items-center rounded-full border-4", result.passed ? "border-easy/60" : "border-hard/60")}>
            <p className="text-3xl font-semibold">{result.score}<span className="text-lg text-muted-foreground">/{result.total}</span></p>
          </div>
          <div className="flex-1">
            <h1 className="text-2xl font-semibold tracking-tight">{result.passed ? "You passed the quiz" : "Not quite there yet"}</h1>
            <p className="mt-1 text-sm text-muted-foreground">{result.passed && !result.already_passed ? "Topic completed and +10 XP added to your profile." : result.passed ? "You had already passed this quiz, so no extra XP this time." : "You need at least 3 correct answers. Review below, then try a new set."}</p>
            <div className="mt-4 flex flex-wrap justify-center gap-2 sm:justify-start">
              {result.passed && !result.already_passed && <Badge tone="medium"><Zap className="h-3 w-3" /> +10 XP</Badge>}
              <Button variant="outline" size="sm" onClick={retry}><RotateCcw /> New quiz</Button>
              <Button size="sm" to={`/learn/${id}`}>Back to topic</Button>
            </div>
          </div>
        </Card>
        <h2 className="mb-3 font-semibold">Review</h2>
        <ol className="space-y-4">
          {result.results.map((r, qi) => (
            <Card key={qi} className="p-5">
              <div className="mb-3 flex items-start gap-3">
                {r.is_correct ? <CheckCircle2 className="mt-0.5 h-5 w-5 shrink-0 text-easy" /> : <XCircle className="mt-0.5 h-5 w-5 shrink-0 text-hard" />}
                <p className="font-medium"><span className="mr-1 font-mono text-xs text-muted-foreground">{qi + 1}.</span>{r.question}</p>
              </div>
              <ul className="grid gap-2 sm:grid-cols-2">
                {r.options.map((o, oi) => { const right = oi === r.correct_index, mine = oi === r.user_answer; return (
                  <li key={oi} className={cn("flex items-center gap-2 rounded-md border px-3 py-2 text-sm", right ? "border-easy/50 bg-easy/10" : mine ? "border-hard/50 bg-hard/10" : "border-border bg-background/40")}>
                    <span className={cn("grid h-6 w-6 shrink-0 place-items-center rounded font-mono text-xs", right ? "bg-easy/20 text-easy" : mine ? "bg-hard/20 text-hard" : "bg-muted text-muted-foreground")}>{L[oi]}</span>
                    <span className="flex-1">{o}</span>{mine && <span className="text-xs text-muted-foreground">Your answer</span>}
                  </li>); })}
              </ul>
            </Card>
          ))}
        </ol>
      </>) : (<>
        <div className="mb-6 flex flex-wrap items-end justify-between gap-4">
          <div><p className="text-sm text-muted-foreground">Topic quiz</p><h1 className="text-2xl font-semibold tracking-tight">{title}</h1></div>
          <Badge tone="medium"><Zap className="h-3 w-3" /> 3 of {qs.length || 5} to pass · +10 XP</Badge>
        </div>
        {quiz.isLoading ? <div className="space-y-4"><p className="text-sm text-muted-foreground">Generating fresh questions with AI…</p>{[0, 1, 2].map((i) => <Skeleton key={i} className="h-40" />)}</div>
          : !qs.length ? <Card><Empty icon={TriangleAlert} title="The quiz could not be generated" text="The AI service did not return questions. Check the Gemini API key on the backend, then try again." action={<Button variant="outline" size="sm" onClick={retry}>Try again</Button>} /></Card>
          : (<>
            <div className="sticky top-14 z-20 -mx-4 mb-4 bg-background/80 px-4 py-3 backdrop-blur-md md:-mx-8 md:px-8">
              <div className="flex items-center gap-3"><Progress value={(answered / qs.length) * 100} className="h-1.5" /><span className="whitespace-nowrap font-mono text-xs text-muted-foreground">{answered}/{qs.length} answered</span></div>
            </div>
            <div className="space-y-4">
              {qs.map((q, qi) => (
                <fieldset key={qi} className="rounded-xl border border-border bg-card p-5 shadow">
                  <legend className="sr-only">Question {qi + 1}</legend>
                  <p className="mb-4 font-medium"><span className="mr-1 font-mono text-xs text-muted-foreground">{qi + 1}.</span>{q.question}</p>
                  <div className="grid gap-2 sm:grid-cols-2">
                    {q.options.map((o, oi) => { const on = answers[qi] === oi; return (
                      <label key={oi} className={cn("flex cursor-pointer items-center gap-3 rounded-md border px-3 py-2.5 text-sm transition-colors hover:border-primary/40", on ? "border-primary/60 bg-primary/10" : "border-border bg-background/40")}>
                        <input type="radio" name={`q${qi}`} className="sr-only" checked={on} onChange={() => setAnswers((a) => ({ ...a, [qi]: oi }))} />
                        <span className={cn("grid h-6 w-6 shrink-0 place-items-center rounded font-mono text-xs", on ? "bg-primary text-primary-foreground" : "bg-muted text-muted-foreground")}>{L[oi]}</span>{o}
                      </label>); })}
                  </div>
                </fieldset>
              ))}
              <div className="flex flex-col items-center gap-2 pt-2">
                <Button size="lg" loading={submit.isPending} onClick={() => answered < qs.length ? toast.warning(`Answer all ${qs.length} questions before submitting.`) : submit.mutate()}><Send /> Submit answers</Button>
                <p className="text-xs text-muted-foreground">Answers are final once submitted.</p>
              </div>
            </div>
          </>)}
      </>)}
    </Page>
  );
}
