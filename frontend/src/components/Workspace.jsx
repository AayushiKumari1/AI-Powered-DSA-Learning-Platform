import { useEffect, useMemo, useRef, useState } from "react";
import { Link } from "react-router-dom";
import CodeMirror from "@uiw/react-codemirror";
import { python } from "@codemirror/lang-python";
import { cpp } from "@codemirror/lang-cpp";
import { java } from "@codemirror/lang-java";
import { vscodeDark } from "@uiw/codemirror-theme-vscode";
import { keymap } from "@codemirror/view";
import { toast } from "sonner";
import { CheckCircle2, Clock, Code2, FileText, History, Lightbulb, ListChecks, Play, RotateCcw, Send, Sparkles, Terminal, Timer, XCircle } from "lucide-react";
import { api } from "@/lib/api";
import { cn } from "@/lib/utils";
import { openMentor } from "@/components/AiMentor";
import { Button, DifficultyBadge } from "@/components/ui";

const LANGS = { python: { label: "Python 3", file: "solution.py", ext: () => python() }, cpp: { label: "C++", file: "solution.cpp", ext: () => cpp() }, java: { label: "Java", file: "Main.java", ext: () => java() } };
const STARTER = {
  python: "import sys\n\ndef solve():\n    data = sys.stdin.read().split()\n    # write your solution here\n    pass\n\nif __name__ == \"__main__\":\n    solve()\n",
  cpp: "#include <bits/stdc++.h>\nusing namespace std;\n\nint main() {\n    ios::sync_with_stdio(false);\n    cin.tie(nullptr);\n    // write your solution here\n    return 0;\n}\n",
  java: "import java.util.*;\n\npublic class Main {\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        // write your solution here\n    }\n}\n",
};

/**
 * Problem + editor + console. Calls the existing Flask endpoints POST /coding/run and POST /coding/submit.
 * props: problem, lastSubmission, draftKey, toolbarLeft, toolbarRight (nodes), onSubmitted(result), isTest
 */
export default function Workspace({ problem, lastSubmission, draftKey, toolbarLeft, toolbarRight, onSubmitted, isTest }) {
  const storageKey = `em_draft_${draftKey || problem.id}`;
  const initial = useMemo(() => {
    try { const d = JSON.parse(localStorage.getItem(storageKey) || "null"); if (d?.code) return d; } catch { /* ignore */ }
    if (lastSubmission?.code && !isTest) return { code: lastSubmission.code, language: lastSubmission.language || "python" };
    return { code: STARTER.python, language: "python" };
  }, [storageKey, lastSubmission, isTest]);
  const [lang, setLang] = useState(initial.language in LANGS ? initial.language : "python");
  const [code, setCode] = useState(initial.code);
  const [tab, setTab] = useState("desc");
  const [panel, setPanel] = useState("console");
  const [output, setOutput] = useState({ text: "Run your code to see output for the sample input.", tone: "muted" });
  const [result, setResult] = useState(null);
  const [busy, setBusy] = useState(null);
  const [saved, setSaved] = useState("");
  const started = useRef(Date.now());
  const [elapsed, setElapsed] = useState(0);

  useEffect(() => { setLang(initial.language in LANGS ? initial.language : "python"); setCode(initial.code); setResult(null); started.current = Date.now(); }, [initial]);
  useEffect(() => { const t = setInterval(() => setElapsed(Math.floor((Date.now() - started.current) / 1000)), 1000); return () => clearInterval(t); }, []);
  useEffect(() => {
    setSaved("Saving…");
    const t = setTimeout(() => { try { localStorage.setItem(storageKey, JSON.stringify({ code, language: lang })); } catch { /* ignore */ } setSaved("Draft saved"); }, 600);
    return () => clearTimeout(t);
  }, [code, lang, storageKey]);

  function changeLang(next) {
    const isStarter = !code.trim() || Object.values(STARTER).some((s) => s.trim() === code.trim());
    if (isStarter || confirm("Switch language and replace the editor with starter code?")) setCode(STARTER[next]);
    setLang(next);
  }

  async function run() {
    setBusy("run"); setPanel("console"); setOutput({ text: "Running with sample input…", tone: "muted" });
    try {
      const d = await api.post("/coding/run", { code, language: lang, stdin: problem.sample_input || "" });
      setOutput(d.error ? { text: `Error\n\n${d.error}`, tone: "hard" } : { text: d.output === "" || d.output == null ? "(no output)" : d.output, tone: "fg" });
    } catch (e) { setOutput({ text: e.data?.error ? `Error\n\n${e.data.error}` : "Could not reach the code runner. Check the backend and try again.", tone: "hard" }); }
    setBusy(null);
  }

  async function submit() {
    setBusy("submit"); setPanel("tests"); setResult({ pending: true });
    try {
      const d = await api.post("/coding/submit", { code, language: lang, question_id: problem.id, solve_time_seconds: Math.max(1, Math.round((Date.now() - started.current) / 1000)) });
      const ok = d.total > 0 && d.passed === d.total;
      setResult({ ...d, ok });
      toast[ok ? "success" : "warning"](ok ? "Accepted — all tests passed" : `${d.passed}/${d.total} tests passed`);
      if (ok) try { localStorage.removeItem(storageKey); } catch { /* ignore */ }
      onSubmitted?.({ ...d, status: ok ? "Passed" : "Failed" });
    } catch (e) { setResult({ error: e.message }); }
    setBusy(null);
  }

  const latest = useRef({ run, submit }); latest.current = { run, submit };
  const keys = useMemo(() => keymap.of([
    { key: "Mod-Enter", run: () => { latest.current.submit(); return true; } },
    { key: "Mod-'", run: () => { latest.current.run(); return true; } },
  ]), []);
  const extensions = useMemo(() => [LANGS[lang].ext(), keys], [lang, keys]);
  const mm = String(Math.floor(elapsed / 60)).padStart(2, "0"), ss = String(elapsed % 60).padStart(2, "0");

  return (
    <div className="flex h-[calc(100vh-3.5rem)] flex-col">
      <div className="flex flex-wrap items-center gap-2 border-b border-border bg-background/60 px-4 py-2.5">
        {toolbarLeft}
        <h1 className="max-w-[40ch] truncate text-sm font-semibold">{problem.title}</h1>
        <DifficultyBadge difficulty={problem.difficulty} />
        <span className="hidden text-xs text-muted-foreground sm:inline">+{problem.xp} XP</span>
        <div className="ml-auto flex items-center gap-2">
          <span className="hidden items-center gap-1 font-mono text-xs text-muted-foreground md:flex" title="Time on this problem"><Timer className="h-3.5 w-3.5" />{mm}:{ss}</span>
          <div className="mx-1 hidden h-5 w-px bg-border md:block" />
          <select value={lang} onChange={(e) => changeLang(e.target.value)} aria-label="Language" className="rounded-md border border-border bg-card px-2 py-1 font-mono text-xs">
            {Object.entries(LANGS).map(([k, v]) => <option key={k} value={k}>{v.label}</option>)}
          </select>
          <Button variant="secondary" size="sm" onClick={run} loading={busy === "run"} title="Run with sample input (Ctrl+')"><Play /> Run</Button>
          <Button size="sm" onClick={submit} loading={busy === "submit"} title="Submit against hidden tests (Ctrl+Enter)"><Send /> Submit</Button>
          {toolbarRight}
        </div>
      </div>

      <div className="grid min-h-0 flex-1 grid-cols-1 lg:grid-cols-[minmax(0,5fr)_minmax(0,7fr)]">
        <section className="flex min-h-0 flex-col border-r border-border">
          <div className="flex h-10 items-center gap-1 border-b border-border px-2" role="tablist">
            <TabBtn on={tab === "desc"} onClick={() => setTab("desc")} icon={FileText}>Description</TabBtn>
            {!isTest && <Link to={`/practice/${problem.id}/submissions`} className="inline-flex h-7 items-center gap-1.5 rounded-md px-3 text-xs font-medium text-muted-foreground hover:text-foreground"><History className="h-3.5 w-3.5" />Submissions</Link>}
            {!isTest && lastSubmission && <TabBtn on={tab === "last"} onClick={() => setTab("last")} icon={Clock}>Last attempt</TabBtn>}
          </div>
          {tab === "desc" ? (
            <div className="min-h-0 flex-1 overflow-auto p-5">
              <div className="prose-dark mb-6" dangerouslySetInnerHTML={{ __html: problem.description || "" }} />
              {(problem.sample_input || problem.sample_output) && (
                <div className="space-y-3"><h2 className="text-sm font-semibold">Example</h2>
                  <div className="rounded-md border border-border bg-background/40 p-3 font-mono text-xs">
                    <p className="mb-1 text-muted-foreground">Input</p><pre className="whitespace-pre-wrap">{problem.sample_input}</pre>
                    <p className="mb-1 mt-3 text-muted-foreground">Output</p><pre className="whitespace-pre-wrap">{problem.sample_output}</pre>
                  </div>
                </div>
              )}
              <div className="mt-6 flex items-start gap-2 rounded-md border border-border bg-background/40 p-3 text-sm">
                <Lightbulb className="mt-0.5 h-4 w-4 shrink-0 text-medium" />
                {isTest ? <p className="text-muted-foreground">Read from stdin and print to stdout. Submit before moving on — your latest result for each question counts.</p>
                  : <p className="text-muted-foreground">Read from stdin and print to stdout. Stuck? <button className="text-primary hover:underline" onClick={() => openMentor(`Give me a hint for this problem: ${problem.title}`)}>Ask the AI mentor for a hint</button>.</p>}
              </div>
            </div>
          ) : (
            <div className="min-h-0 flex-1 overflow-auto p-5">
              <p className="mb-3 text-sm text-muted-foreground">{lastSubmission.status} · {lastSubmission.passed}/{lastSubmission.total} tests · {lastSubmission.language}</p>
              <pre className="max-h-96 overflow-auto rounded-md border border-border bg-background/40 p-3 font-mono text-xs">{lastSubmission.code}</pre>
              <Button variant="outline" size="sm" className="mt-3" onClick={() => { setLang(lastSubmission.language in LANGS ? lastSubmission.language : "python"); setCode(lastSubmission.code); toast.success("Last submission loaded"); }}>Load into editor</Button>
            </div>
          )}
        </section>

        <section className="grid min-h-0 grid-rows-[1fr_minmax(160px,34%)]">
          <div className="flex min-h-0 flex-col border-b border-border bg-card">
            <div className="flex items-center justify-between border-b border-border bg-background/40 px-3 py-1.5">
              <span className="flex items-center gap-2 font-mono text-xs text-muted-foreground"><Code2 className="h-3.5 w-3.5" />{LANGS[lang].file}</span>
              <div className="flex items-center gap-2"><span className="text-xs text-muted-foreground">{saved}</span>
                <button title="Reset to starter code" aria-label="Reset" onClick={() => confirm("Reset the editor to starter code?") && setCode(STARTER[lang])} className="grid h-7 w-7 place-items-center rounded-md text-muted-foreground hover:bg-accent hover:text-foreground"><RotateCcw className="h-3.5 w-3.5" /></button>
              </div>
            </div>
            <div className="min-h-[320px] flex-1 overflow-hidden">
              <CodeMirror value={code} height="100%" theme={vscodeDark} extensions={extensions} onChange={setCode} basicSetup={{ tabSize: 4 }} className="h-full" />
            </div>
          </div>
          <div className="flex min-h-0 flex-col bg-background/40">
            <div className="flex items-center gap-2 border-b border-border px-3 py-1.5">
              <TabBtn on={panel === "console"} onClick={() => setPanel("console")} icon={Terminal}>Console</TabBtn>
              <TabBtn on={panel === "tests"} onClick={() => setPanel("tests")} icon={ListChecks}>Test results</TabBtn>
              <div className="ml-auto flex items-center gap-2">
                {result?.analysis_ready && <Link to={`/practice/${problem.id}/analysis`} target={isTest ? "_blank" : undefined} className="inline-flex h-7 items-center gap-1.5 rounded-md border border-chart-5/40 bg-chart-5/15 px-2.5 text-xs font-medium text-chart-5 hover:bg-chart-5/25"><Sparkles className="h-3.5 w-3.5" />AI analysis</Link>}
                <button onClick={() => setOutput({ text: "", tone: "muted" })} className="text-xs text-muted-foreground hover:text-foreground">Clear</button>
              </div>
            </div>
            {panel === "console" ? (
              <pre className={cn("min-h-0 flex-1 overflow-auto whitespace-pre-wrap p-3 font-mono text-xs", { muted: "text-muted-foreground", fg: "text-foreground", hard: "text-hard" }[output.tone])}>{output.text}</pre>
            ) : (
              <div className="min-h-0 flex-1 overflow-auto p-3 text-sm">
                {!result ? <p className="text-xs text-muted-foreground">Submit to run hidden test cases.</p>
                  : result.pending ? <p className="text-xs text-muted-foreground">Running hidden test cases…</p>
                  : result.error ? <p className="text-hard">{result.error}</p>
                  : (<>
                    <div className="mb-3 flex flex-wrap items-center gap-3">
                      <span className={cn("text-base font-semibold", result.ok ? "text-easy" : "text-hard")}>{result.ok ? "Accepted" : "Wrong answer"}</span>
                      <span className="text-xs text-muted-foreground">{result.passed} / {result.total} test cases passed</span>
                      {result.performance_rating != null && <span className="rounded-md border border-chart-5/30 bg-chart-5/15 px-2 py-0.5 text-xs text-chart-5">Efficiency {result.performance_rating}/10</span>}
                    </div>
                    {result.performance_summary && <p className="mb-3 text-xs text-muted-foreground">{result.performance_summary}</p>}
                    <ul className="divide-y divide-border rounded-md border border-border">
                      {(result.results || []).map((r, i) => (
                        <li key={i} className="p-3">
                          <div className="flex items-center gap-2">
                            {r.status === "Passed" ? <CheckCircle2 className="h-4 w-4 text-easy" /> : <XCircle className="h-4 w-4 text-hard" />}
                            <span className="font-medium">Case {i + 1}</span><span className="text-xs text-muted-foreground">{r.status}</span>
                            {r.time_ms != null && <span className="ml-auto font-mono text-xs text-muted-foreground">{r.time_ms} ms</span>}
                          </div>
                          {r.status !== "Passed" && (
                            <div className="mt-2 grid gap-2 font-mono text-xs sm:grid-cols-3">
                              <div><p className="text-muted-foreground">Input</p><pre className="whitespace-pre-wrap rounded bg-muted px-2 py-1">{r.input}</pre></div>
                              <div><p className="text-muted-foreground">Your output</p><pre className="whitespace-pre-wrap rounded bg-muted px-2 py-1">{r.output}</pre></div>
                              {r.expected !== undefined && <div><p className="text-muted-foreground">Expected</p><pre className="whitespace-pre-wrap rounded bg-muted px-2 py-1">{r.expected}</pre></div>}
                            </div>
                          )}
                        </li>
                      ))}
                    </ul>
                  </>)}
              </div>
            )}
          </div>
        </section>
      </div>
    </div>
  );
}

function TabBtn({ on, onClick, icon: Icon, children }) {
  return <button role="tab" aria-selected={on} onClick={onClick} className={cn("inline-flex h-7 items-center gap-1.5 rounded-md px-3 text-xs font-medium transition-colors", on ? "bg-card text-foreground shadow" : "text-muted-foreground hover:text-foreground")}><Icon className="h-3.5 w-3.5" />{children}</button>;
}
