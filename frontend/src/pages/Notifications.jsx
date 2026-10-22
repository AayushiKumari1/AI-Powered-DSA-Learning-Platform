import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { BellOff, Check, CheckCheck, Megaphone, X } from "lucide-react";
import { api } from "@/lib/api";
import { cn, fmtTime } from "@/lib/utils";
import { useAuth } from "@/hooks/useAuth";
import { Badge, Button, Card, Empty, ErrorState, IconTile, Page, PageHeader, PageSkeleton, Tabs } from "@/components/ui";

export default function Notifications() {
  const qc = useQueryClient();
  const { refresh } = useAuth();
  const [filter, setFilter] = useState("all");
  const { data, isLoading, error, refetch } = useQuery({ queryKey: ["notifications"], queryFn: () => api.get("/api/notifications") });
  const act = useMutation({ mutationFn: (url) => api.post(url), onSuccess: () => { qc.invalidateQueries({ queryKey: ["notifications"] }); qc.invalidateQueries({ queryKey: ["dashboard"] }); refresh(); } });
  if (isLoading) return <PageSkeleton />;
  if (error) return <ErrorState error={error} retry={refetch} />;
  const items = data.notifications.filter((n) => filter === "all" ? true : filter === "unread" ? !n.is_read && !n.is_removed : filter === "read" ? n.is_read && !n.is_removed : n.is_removed);

  return (
    <Page>
      <PageHeader title="Notifications" subtitle="Announcements from the EduMentor team.">
        {data.unread > 0 && <Button variant="outline" onClick={() => act.mutate("/api/notifications/read-all")}><CheckCheck /> Mark all read</Button>}
      </PageHeader>
      <Tabs className="mb-4" value={filter} onChange={setFilter} items={[{ value: "all", label: "All" }, { value: "unread", label: "Unread", count: data.unread || null }, { value: "read", label: "Read" }, { value: "removed", label: "Removed" }]} />
      <Card className="overflow-hidden">
        {items.length ? (
          <ul className="divide-y divide-border">
            {items.map((n) => (
              <li key={n.id} className={cn("flex gap-4 p-4", !n.is_read && !n.is_removed && "bg-primary/5", n.is_removed && "opacity-60")}>
                <IconTile icon={Megaphone} color={!n.is_read ? "var(--chart-1)" : "var(--muted-foreground)"} className="mt-0.5 h-8 w-8" />
                <div className="min-w-0 flex-1">
                  <div className="flex flex-wrap items-center gap-2">
                    {!n.is_read && !n.is_removed && <span className="h-2 w-2 rounded-full bg-primary" aria-label="Unread" />}
                    <h2 className="font-medium">{n.title}</h2>
                    {n.is_removed ? <Badge>Removed</Badge> : n.is_read ? <Badge>Read</Badge> : <Badge tone="primary">New</Badge>}
                  </div>
                  <p className="mt-1 whitespace-pre-line text-sm text-foreground/80">{n.content}</p>
                  <p className="mt-2 text-xs text-muted-foreground">{fmtTime(n.at)}</p>
                </div>
                <div className="flex shrink-0 items-start gap-1">
                  {!n.is_removed && !n.is_read && <Button variant="ghost" size="sm" onClick={() => act.mutate(`/api/notifications/${n.id}/read`)}><Check /><span className="hidden sm:inline">Mark read</span></Button>}
                  {!n.is_removed && <Button variant="ghost" size="sm" aria-label="Remove" onClick={() => act.mutate(`/api/notifications/${n.id}/remove`)}><X /></Button>}
                </div>
              </li>
            ))}
          </ul>
        ) : <Empty icon={BellOff} title="You're all caught up" text="New announcements will appear here." />}
      </Card>
    </Page>
  );
}
