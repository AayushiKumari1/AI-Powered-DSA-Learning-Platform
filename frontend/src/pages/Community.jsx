import { useState } from "react";
import { useSearchParams } from "react-router-dom";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { ArrowLeftRight, ChartLine, Copy, GitFork, Hash, Layers, Link2, MessagesSquare, Shield, Trash2, Type } from "lucide-react";
import { api } from "@/lib/api";
import { cn } from "@/lib/utils";
import { useSocket } from "@/hooks/useSocket";
import { Bubble, Composer, LiveDot, useAutoScroll } from "@/components/ChatThread";
import { Card, Empty, ErrorState, IconTile, Page, PageHeader, PageSkeleton } from "@/components/ui";

const ICONS = { "fa-layer-group": Layers, "fa-font": Type, "fa-arrows-left-right": ArrowLeftRight, "fa-link": Link2, "fa-clone": Copy, "fa-tree": GitFork, "fa-chart-line": ChartLine };

export default function Community({ admin = false }) {
  const API = admin ? "/api/admin/community" : "/api/community";
  const KEY = admin ? "admin-community" : "community";
  const [params, setParams] = useSearchParams();
  const group = params.get("group") || "arrays";
  const qc = useQueryClient();
  const [extra, setExtra] = useState([]);
  const { data, isLoading, error, refetch } = useQuery({ queryKey: [KEY, group], queryFn: () => api.get(`${API}?group=${group}`) });
  const base = data?.messages || [];
  const msgs = [...base, ...extra.filter((m) => m.group_key === group && !base.some((b) => b.id === m.id))];
  const connected = useSocket("join_community", { group_key: group }, {
    new_community_message: (p) => setExtra((e) => e.some((m) => m.id === p.id) ? e : [...e, p]),
  });
  const scrollRef = useAutoScroll(msgs.length);
  async function send(text) {
    try { await api.post(API, { message: text, group }); if (!connected) qc.invalidateQueries({ queryKey: [KEY, group] }); }
    catch (e) { toast.error(e.message); }
  }
  if (isLoading) return <PageSkeleton />;
  if (error) return <ErrorState error={error} retry={refetch} />;
  const cur = data.groups.find((g) => g.key === data.current) || data.groups[0];
  const CurIcon = ICONS[cur.icon] || Hash;

  return (
    <Page>
      <PageHeader title="Community" subtitle={admin ? "Moderate topic channels and post as Admin." : "Topic channels for discussing patterns, problems and approaches."}>{admin && <span className="inline-flex items-center gap-1.5 rounded-md border border-medium/30 bg-medium/15 px-2 py-1 text-xs text-medium"><Shield className="h-3.5 w-3.5" />Posting as Admin</span>}</PageHeader>
      <Card className="grid h-[calc(100vh-14rem)] min-h-[480px] grid-cols-1 overflow-hidden md:grid-cols-[260px_minmax(0,1fr)]">
        <aside className="flex min-h-0 flex-col border-b border-border md:border-b-0 md:border-r">
          <p className="flex h-8 items-center px-4 pt-3 text-xs font-medium text-muted-foreground">Channels · {data.groups.length}</p>
          <ul className="flex gap-1 overflow-x-auto p-2 md:flex-1 md:flex-col md:overflow-y-auto">
            {data.groups.map((g) => { const I = ICONS[g.icon] || Hash, on = g.key === data.current; return (
              <li key={g.key} className="shrink-0"><button onClick={() => { setExtra([]); setParams({ group: g.key }); }} aria-current={on ? "page" : undefined}
                className={cn("flex w-full items-center gap-2 rounded-md px-2.5 py-2 text-left text-sm transition-colors", on ? "bg-accent font-medium" : "text-muted-foreground hover:bg-muted/40 hover:text-foreground")}>
                <I className="h-4 w-4 shrink-0" /><span className="flex-1 truncate"># {g.label}</span>{g.count > 0 && <span className="text-xs text-muted-foreground">{g.count}</span>}
              </button></li>); })}
          </ul>
        </aside>
        <section className="flex min-h-0 flex-col">
          <header className="flex items-center gap-3 border-b border-border bg-background/60 px-4 py-3">
            <IconTile icon={CurIcon} className="h-9 w-9" />
            <div className="min-w-0 flex-1 leading-tight"><p className="text-sm font-semibold"># {cur.label}</p><p className="truncate text-xs text-muted-foreground">{cur.description}</p></div>
            <LiveDot on={connected} />
          </header>
          <div ref={scrollRef} className="flex-1 space-y-4 overflow-y-auto p-4">
            {msgs.length ? msgs.map((m) => (
              <div key={m.id} className="group relative">
                <Bubble showName out={admin ? m.is_admin : m.user_id === data.me.id && !m.is_admin} admin={m.is_admin} name={m.sender_name} time={m.created_at} text={m.message} />
                {admin && <button aria-label="Delete message" title="Delete message" onClick={async () => { if (!confirm("Delete this message?")) return; try { await api.del(`/api/admin/community/${m.id}`); setExtra((e) => e.filter((x) => x.id !== m.id)); qc.invalidateQueries({ queryKey: [KEY, group] }); toast.success("Message deleted"); } catch (err) { toast.error(err.message); } }} className="absolute right-0 top-0 hidden rounded-md p-1.5 text-muted-foreground hover:bg-hard/15 hover:text-hard group-hover:block"><Trash2 className="h-3.5 w-3.5" /></button>}
              </div>))
              : <Empty icon={MessagesSquare} title={`No messages in #${cur.label} yet`} text="Start the conversation — share a pattern or ask about a problem." />}
          </div>
          <Composer onSend={send} placeholder={`Message #${cur.label}`} />
        </section>
      </Card>
    </Page>
  );
}
