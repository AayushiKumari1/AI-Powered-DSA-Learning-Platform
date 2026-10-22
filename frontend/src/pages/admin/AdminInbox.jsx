import { useMemo, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { BarChart3, Inbox, Search } from "lucide-react";
import { api } from "@/lib/api";
import { cn, initials, timeAgo } from "@/lib/utils";
import { useSocket } from "@/hooks/useSocket";
import { Bubble, Composer, LiveDot, useAutoScroll } from "@/components/ChatThread";
import { Card, Empty, ErrorState, Input, Page, PageHeader, PageSkeleton } from "@/components/ui";

export default function AdminInbox() {
  const [params, setParams] = useSearchParams();
  const uid = params.get("user");
  const [q, setQ] = useState("");
  const [extra, setExtra] = useState([]);
  const qc = useQueryClient();
  const list = useQuery({ queryKey: ["admin-inbox"], queryFn: () => api.get("/api/admin/inbox") });
  const thread = useQuery({ queryKey: ["admin-thread", uid], queryFn: () => api.get(`/api/admin/inbox/${uid}`), enabled: !!uid });
  const base = thread.data?.messages || [];
  const msgs = [...base, ...extra.filter((m) => !base.some((b) => b.id === m.id))];
  const connected = useSocket(uid ? "join_chat" : null, { user_id: Number(uid) }, { new_chat_message: (p) => setExtra((e) => e.some((m) => m.id === p.id) ? e : [...e, p]) });
  const scrollRef = useAutoScroll(msgs.length + (uid || ""));
  const convs = useMemo(() => (list.data?.conversations || []).filter((c) => `${c.username} ${c.email}`.toLowerCase().includes(q.toLowerCase())), [list.data, q]);
  async function send(text) {
    try { const r = await api.post(`/api/admin/inbox/${uid}`, { message: text }); setExtra((e) => e.some((m) => m.id === r.message.id) ? e : [...e, r.message]); qc.invalidateQueries({ queryKey: ["admin-inbox"] }); }
    catch (e) { toast.error(e.message); }
  }
  if (list.isLoading) return <PageSkeleton />;
  if (list.error) return <ErrorState error={list.error} retry={list.refetch} />;
  const user = thread.data?.user;
  return (
    <Page>
      <PageHeader title="Mentor inbox" subtitle="One-to-one conversations with learners. Replies appear on their side in real time." />
      <Card className="grid h-[calc(100vh-14rem)] min-h-[480px] grid-cols-1 overflow-hidden md:grid-cols-[300px_minmax(0,1fr)]">
        <aside className="flex min-h-0 flex-col border-b border-border md:border-b-0 md:border-r">
          <div className="border-b border-border p-3"><div className="relative"><Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" /><Input value={q} onChange={(e) => setQ(e.target.value)} placeholder="Search learners…" className="h-8 bg-background pl-9" aria-label="Search learners" /></div></div>
          <ul className="max-h-48 flex-1 overflow-y-auto p-2 md:max-h-none">
            {convs.map((c) => (
              <li key={c.id}><button onClick={() => { setExtra([]); setParams({ user: c.id }); }} aria-current={String(c.id) === uid}
                className={cn("flex w-full items-center gap-3 rounded-md px-2 py-2 text-left transition-colors", String(c.id) === uid ? "bg-accent" : "hover:bg-muted/40")}>
                <span className="grid h-9 w-9 shrink-0 place-items-center rounded-full bg-gradient-to-br from-primary to-chart-5 text-xs font-semibold text-primary-foreground">{initials(c.username)}</span>
                <span className="min-w-0 flex-1">
                  <span className="flex items-center gap-2"><span className="truncate text-sm font-medium">{c.username}</span>{c.at && <span className="ml-auto shrink-0 text-[11px] text-muted-foreground">{timeAgo(c.at)}</span>}</span>
                  <span className={cn("block truncate text-xs", c.sender === "user" ? "text-foreground/80" : "text-muted-foreground")}>{c.message ? `${c.sender === "admin" ? "You: " : ""}${c.message}` : "No messages yet"}</span>
                </span>
              </button></li>
            ))}
          </ul>
        </aside>
        <section className="flex min-h-0 flex-col">
          {uid ? (thread.isLoading ? <div className="p-6 text-sm text-muted-foreground">Loading…</div> : (<>
            <header className="flex items-center gap-3 border-b border-border bg-background/60 px-4 py-3">
              <span className="grid h-9 w-9 place-items-center rounded-full bg-gradient-to-br from-primary to-chart-5 text-sm font-semibold text-primary-foreground">{initials(user?.username)}</span>
              <div className="min-w-0 flex-1 leading-tight"><p className="text-sm font-semibold">{user?.username}</p><p className="truncate text-xs text-muted-foreground">{user?.email}</p></div>
              <LiveDot on={connected} />
              <Link to={`/admin/learners/${uid}`} className="inline-flex h-8 items-center gap-1.5 rounded-md border border-border px-3 text-xs hover:bg-accent"><BarChart3 className="h-3.5 w-3.5" />Profile</Link>
            </header>
            <div ref={scrollRef} className="flex-1 space-y-4 overflow-y-auto p-4">
              {msgs.length ? msgs.map((m) => <Bubble key={m.id} out={m.sender_type === "admin"} admin={m.sender_type === "admin"} name={m.sender_type === "admin" ? "Admin" : user?.username} time={m.created_at} text={m.message} />)
                : <Empty icon={Inbox} title="No messages yet" text={`Start the conversation with ${user?.username}.`} />}
            </div>
            <Composer onSend={send} placeholder={`Reply to ${user?.username}…`} />
          </>)) : <Empty icon={Inbox} title="Select a conversation" text="Pick a learner on the left to read and reply." />}
        </section>
      </Card>
    </Page>
  );
}
