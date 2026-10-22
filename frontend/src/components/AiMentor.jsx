import { useEffect, useRef, useState } from "react";
import { Bot, Eraser, Send, Sparkles, X } from "lucide-react";
import { api } from "@/lib/api";
import { cn } from "@/lib/utils";

// Talks to the existing POST /chat/chatbot (Gemini, intent-routed in utils/chatbot_service.py)
const CHIPS = ["Give me a hint", "Next hint", "What should I study next?", "Make me a study plan", "Review code: "];
const INTRO = { role: "bot", text: "Stuck on a problem? Paste it and ask for a hint. You can also ask me to review code, explain a concept, or plan your week." };

function Md({ text }) {
  // tiny safe renderer: code fences, inline code, bold, line breaks
  const parts = String(text || "").split(/```(?:\w+)?\n?([\s\S]*?)```/g);
  return parts.map((p, i) => i % 2 ? (
    <pre key={i} className="my-2 overflow-x-auto rounded-md border border-border bg-background/60 p-2 font-mono text-xs">{p.replace(/\n$/, "")}</pre>
  ) : (
    <span key={i}>{p.split(/(`[^`\n]+`|\*\*[^*]+\*\*)/g).map((s, j) =>
      s.startsWith("`") ? <code key={j} className="rounded bg-muted px-1 py-0.5 font-mono text-xs">{s.slice(1, -1)}</code>
        : s.startsWith("**") ? <strong key={j}>{s.slice(2, -2)}</strong>
          : s.split("\n").map((line, k, arr) => <span key={k}>{line}{k < arr.length - 1 && <br />}</span>))}</span>
  ));
}

export default function AiMentor() {
  const [open, setOpen] = useState(false);
  const [msgs, setMsgs] = useState([INTRO]);
  const [input, setInput] = useState("");
  const [busy, setBusy] = useState(false);
  const logRef = useRef(null);
  const inputRef = useRef(null);

  useEffect(() => {
    const onOpen = (e) => { setOpen(true); if (e.detail) setInput(e.detail); setTimeout(() => inputRef.current?.focus(), 30); };
    window.addEventListener("em:mentor", onOpen);
    return () => window.removeEventListener("em:mentor", onOpen);
  }, []);
  useEffect(() => { logRef.current?.scrollTo(0, logRef.current.scrollHeight); }, [msgs, busy]);

  async function send(text) {
    text = text.trim();
    if (!text || busy) return;
    setMsgs((m) => [...m, { role: "user", text }]); setInput(""); setBusy(true);
    try {
      const data = await api.post("/chat/chatbot", { message: text });
      setMsgs((m) => [...m, { role: "bot", text: data?.reply || "No reply. Try rephrasing your question." }]);
    } catch (e) {
      setMsgs((m) => [...m, { role: "bot", error: true, text: e.status === 401 ? "Your session expired. Sign in again to use the mentor." : "The mentor could not be reached. Check your connection and try again." }]);
    }
    setBusy(false);
  }

  return (
    <>
      <button onClick={() => setOpen((o) => !o)} aria-expanded={open}
        className="glow-border fixed bottom-5 right-5 z-40 inline-flex h-11 items-center gap-2 rounded-full bg-primary px-4 text-sm font-medium text-primary-foreground shadow-lg hover:bg-primary/90">
        <Sparkles className="h-4 w-4" /><span className="hidden sm:inline">AI mentor</span>
      </button>
      {open && (
        <section aria-label="AI mentor" className="glow-border fixed bottom-20 right-4 z-50 flex h-[min(560px,calc(100vh-7rem))] w-[min(400px,calc(100vw-2rem))] flex-col overflow-hidden rounded-xl border border-border bg-card shadow-2xl">
          <header className="flex items-center gap-2 border-b border-border bg-background/60 px-4 py-3">
            <span className="grid h-7 w-7 place-items-center rounded-md bg-primary/20 text-primary"><Bot className="h-4 w-4" /></span>
            <div className="min-w-0 flex-1 leading-tight"><p className="text-sm font-semibold">AI mentor</p><p className="text-xs text-muted-foreground">Hints first, full solutions when you ask</p></div>
            <button onClick={() => setMsgs([INTRO])} title="Clear conversation" aria-label="Clear conversation" className="grid h-8 w-8 place-items-center rounded-md hover:bg-accent"><Eraser className="h-4 w-4" /></button>
            <button onClick={() => setOpen(false)} aria-label="Close" className="grid h-8 w-8 place-items-center rounded-md hover:bg-accent"><X className="h-4 w-4" /></button>
          </header>
          <div ref={logRef} className="flex-1 space-y-3 overflow-y-auto p-4 text-sm" aria-live="polite">
            {msgs.map((m, i) => m.role === "user" ? (
              <div key={i} className="flex justify-end"><div className="max-w-[85%] whitespace-pre-wrap rounded-lg rounded-tr-sm bg-primary px-3 py-2 text-primary-foreground">{m.text}</div></div>
            ) : (
              <div key={i} className="flex gap-2">
                <span className="grid h-6 w-6 shrink-0 place-items-center rounded-md bg-primary/20 text-primary"><Bot className="h-3.5 w-3.5" /></span>
                <div className={cn("min-w-0 max-w-[85%] rounded-lg rounded-tl-sm border border-border bg-background/40 px-3 py-2 leading-relaxed", m.error && "text-hard")}><Md text={m.text} /></div>
              </div>
            ))}
            {busy && <div className="flex gap-2 text-muted-foreground"><Bot className="h-4 w-4" /><span className="animate-pulse">Thinking…</span></div>}
          </div>
          <div className="flex flex-wrap gap-1.5 border-t border-border px-3 pt-3">
            {CHIPS.map((c) => (
              <button key={c} onClick={() => c.endsWith(": ") ? (setInput(c), inputRef.current?.focus()) : send(c)}
                className="rounded-md border border-border bg-card px-2 py-1 text-xs text-muted-foreground transition-colors hover:border-primary/40 hover:text-foreground">{c.replace(/: $/, "")}</button>
            ))}
          </div>
          <form className="flex items-end gap-2 p-3" onSubmit={(e) => { e.preventDefault(); send(input); }}>
            <textarea ref={inputRef} rows={1} value={input} onChange={(e) => setInput(e.target.value)} maxLength={6000}
              onKeyDown={(e) => { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); send(input); } }}
              placeholder="Ask anything about DSA…" aria-label="Message"
              className="max-h-32 min-h-9 flex-1 resize-none rounded-md border border-input bg-transparent px-3 py-2 text-sm placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring" />
            <button type="submit" disabled={busy} aria-label="Send" className="grid h-9 w-9 place-items-center rounded-md bg-primary text-primary-foreground hover:bg-primary/90 disabled:opacity-50"><Send className="h-4 w-4" /></button>
          </form>
        </section>
      )}
    </>
  );
}

export const openMentor = (prefill) => window.dispatchEvent(new CustomEvent("em:mentor", { detail: prefill }));
