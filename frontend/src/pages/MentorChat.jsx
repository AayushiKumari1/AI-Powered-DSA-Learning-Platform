import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { toast } from "sonner";
import { Code2, Link2, MessageCircle, Sparkles, Target } from "lucide-react";
import { api } from "@/lib/api";
import { useSocket } from "@/hooks/useSocket";
import { useAuth } from "@/hooks/useAuth";
import { openMentor } from "@/components/AiMentor";
import { Bubble, Composer, LiveDot, useAutoScroll } from "@/components/ChatThread";
import { Button, Card, Empty, ErrorState, Page, PageHeader, PageSkeleton } from "@/components/ui";

export default function MentorChat() {
  const { user } = useAuth();
  const [extra, setExtra] = useState([]);
  const { data, isLoading, error, refetch } = useQuery({ queryKey: ["mentor-chat"], queryFn: () => api.get("/api/chat/messages") });
  const msgs = [...(data?.messages || []), ...extra.filter((m) => !(data?.messages || []).some((d) => d.id === m.id))];
  const connected = useSocket(user ? "join_chat" : null, { user_id: user?.id }, {
    new_chat_message: (p) => setExtra((e) => e.some((m) => m.id === p.id) ? e : [...e, p]),
  });
  const scrollRef = useAutoScroll(msgs.length);
  async function send(text) {
    try { const r = await api.post("/api/chat/messages", { message: text }); setExtra((e) => e.some((m) => m.id === r.message.id) ? e : [...e, r.message]); }
    catch (e) { toast.error(e.message); }
  }
  if (isLoading) return <PageSkeleton />;
  if (error) return <ErrorState error={error} retry={refetch} />;
  return (
    <Page>
      <PageHeader title="Ask a mentor" subtitle="Message the EduMentor team directly. Replies show up here in real time." />
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-[minmax(0,1fr)_300px]">
        <Card className="flex h-[calc(100vh-15rem)] min-h-[420px] flex-col overflow-hidden">
          <header className="flex items-center gap-3 border-b border-border bg-background/60 px-4 py-3">
            <div className="grid h-9 w-9 place-items-center rounded-full bg-medium/20 text-sm font-semibold text-medium">AD</div>
            <div className="min-w-0 flex-1 leading-tight"><p className="text-sm font-semibold">EduMentor team</p><LiveDot on={connected} /></div>
          </header>
          <div ref={scrollRef} className="flex-1 space-y-4 overflow-y-auto p-4">
            {msgs.length ? msgs.map((m) => <Bubble key={m.id} out={m.sender_type === "user"} admin={m.sender_type === "admin"} name={m.sender_type === "user" ? user.username : "Admin"} time={m.created_at} text={m.message} />)
              : <Empty icon={MessageCircle} title="No messages yet" text="Ask about a concept, a problem you're stuck on, or your study plan." />}
          </div>
          <Composer onSend={send} placeholder="Ask the mentor team…" />
        </Card>
        <aside className="space-y-4">
          <Card className="p-5"><h2 className="mb-3 font-semibold">Get a faster answer</h2>
            <ul className="space-y-3 text-sm text-muted-foreground">
              <li className="flex gap-2"><Link2 className="mt-0.5 h-4 w-4 shrink-0 text-primary" />Mention the problem or topic name.</li>
              <li className="flex gap-2"><Code2 className="mt-0.5 h-4 w-4 shrink-0 text-primary" />Paste the part of your code that fails.</li>
              <li className="flex gap-2"><Target className="mt-0.5 h-4 w-4 shrink-0 text-primary" />Say what you expected and what happened.</li>
            </ul></Card>
          <Card className="bg-gradient-to-br from-card to-accent p-5">
            <p className="mb-1 flex items-center gap-2 text-xs font-medium text-medium"><Sparkles className="h-3.5 w-3.5" /> INSTANT HELP</p>
            <p className="text-sm text-muted-foreground">Need an answer right now? The AI mentor replies instantly with hints, reviews and study plans.</p>
            <Button size="sm" className="mt-3 w-full" onClick={() => openMentor()}>Open AI mentor</Button>
          </Card>
        </aside>
      </div>
    </Page>
  );
}
