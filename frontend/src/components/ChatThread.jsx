import { useEffect, useRef, useState } from "react";
import { Send } from "lucide-react";
import { cn, fmtTime, initials } from "@/lib/utils";

export function Bubble({ out, name, admin, time, text, showName }) {
  return (
    <div className={cn("flex gap-2", out && "flex-row-reverse")}>
      <div className={cn("grid h-8 w-8 shrink-0 place-items-center rounded-full text-xs font-semibold", admin ? "bg-medium/20 text-medium" : out ? "bg-primary text-primary-foreground" : "bg-muted text-muted-foreground")}>{initials(name)}</div>
      <div className={cn("flex max-w-[75%] flex-col", out ? "items-end" : "items-start")}>
        <span className="mb-1 text-xs text-muted-foreground">{showName && <>{name}{admin && " (Admin)"} · </>}{time ? (time.includes("T") ? fmtTime(time) : time) : "now"}</span>
        <div className={cn("whitespace-pre-wrap break-words rounded-lg px-3 py-2 text-sm", out ? "rounded-tr-sm bg-primary text-primary-foreground" : "rounded-tl-sm border border-border bg-card")}>{text}</div>
      </div>
    </div>
  );
}

export function Composer({ onSend, placeholder, disabled }) {
  const [v, setV] = useState("");
  const ref = useRef(null);
  const send = () => { const t = v.trim(); if (!t) return; onSend(t); setV(""); if (ref.current) ref.current.style.height = ""; };
  return (
    <form className="flex items-end gap-2 border-t border-border p-3" onSubmit={(e) => { e.preventDefault(); send(); }}>
      <textarea ref={ref} rows={1} value={v} maxLength={2000} placeholder={placeholder} aria-label="Message" disabled={disabled}
        onChange={(e) => { setV(e.target.value); e.target.style.height = "auto"; e.target.style.height = Math.min(e.target.scrollHeight, 128) + "px"; }}
        onKeyDown={(e) => { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); send(); } }}
        className="max-h-32 min-h-9 flex-1 resize-none rounded-md border border-input bg-transparent px-3 py-2 text-sm placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring" />
      <button type="submit" disabled={disabled} aria-label="Send" className="grid h-9 w-9 shrink-0 place-items-center rounded-md bg-primary text-primary-foreground hover:bg-primary/90 disabled:opacity-50"><Send className="h-4 w-4" /></button>
    </form>
  );
}

export function useAutoScroll(dep) {
  const ref = useRef(null);
  useEffect(() => { ref.current?.scrollTo(0, ref.current.scrollHeight); }, [dep]);
  return ref;
}

export const LiveDot = ({ on }) => <span className="flex items-center gap-1.5 text-xs text-muted-foreground"><span className={cn("h-2 w-2 rounded-full", on ? "bg-easy" : "bg-muted-foreground")} />{on ? "Live" : "Connecting…"}</span>;
