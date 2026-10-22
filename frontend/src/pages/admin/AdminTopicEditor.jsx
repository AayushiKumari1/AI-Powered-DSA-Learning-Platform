import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { Eye, Save } from "lucide-react";
import { api } from "@/lib/api";
import { Breadcrumbs, Button, Card, ErrorState, Input, Label, Page, PageHeader, PageSkeleton, Tabs, Textarea } from "@/components/ui";

export default function AdminTopicEditor() {
  const { id } = useParams();
  const isNew = !id || id === "new";
  const navigate = useNavigate();
  const qc = useQueryClient();
  const [f, setF] = useState({ title: "", tags: "", intro: "", example: "", code: "", details: "", description: "" });
  const [view, setView] = useState("edit");
  const { data, isLoading, error } = useQuery({ queryKey: ["admin-topic", id], queryFn: () => api.get(`/api/admin/topics/${id}`), enabled: !isNew });
  useEffect(() => { if (data) setF((x) => ({ ...x, ...data.topic })); }, [data]);
  const save = useMutation({
    mutationFn: () => isNew ? api.post("/api/admin/topics", f) : api.put(`/api/admin/topics/${id}`, f),
    onSuccess: () => { toast.success(isNew ? "Topic published" : "Topic saved"); qc.invalidateQueries({ queryKey: ["admin-topics"] }); navigate("/admin/topics"); },
    onError: (e) => toast.error(e.message),
  });
  const set = (k) => (e) => setF({ ...f, [k]: e.target.value });
  if (!isNew && isLoading) return <PageSkeleton />;
  if (error) return <ErrorState error={error} />;
  const esc = (s) => (s || "").replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
  const previewHtml = isNew
    ? `<section><h4>Introduction</h4><p>${esc(f.intro)}</p></section><section><h4>Example / Explanation</h4><p>${esc(f.example)}</p></section><section><h4>Code Example</h4><pre><code>${esc(f.code)}</code></pre></section><section><h4>Additional Details</h4><p>${esc(f.details)}</p></section>`
    : f.description;

  return (
    <Page className="max-w-5xl">
      <Breadcrumbs items={[{ label: "Topics", to: "/admin/topics" }, { label: isNew ? "New topic" : f.title || "Edit" }]} />
      <PageHeader title={isNew ? "New topic" : "Edit topic"} subtitle={isNew ? "Learners see this lesson, curated YouTube videos and an AI quiz generated from the title." : "Changes are visible to learners immediately."}>
        <Tabs value={view} onChange={setView} items={[{ value: "edit", label: "Edit" }, { value: "preview", label: "Preview", icon: Eye }]} />
      </PageHeader>
      <form onSubmit={(e) => { e.preventDefault(); save.mutate(); }}>
        {view === "edit" ? (
          <Card className="space-y-5 p-6">
            <div className="grid gap-4 sm:grid-cols-2">
              <div className="space-y-1.5"><Label htmlFor="title">Title</Label><Input id="title" required value={f.title} onChange={set("title")} placeholder="Binary Search" /></div>
              <div className="space-y-1.5"><Label htmlFor="tags">Tags</Label><Input id="tags" value={f.tags} onChange={set("tags")} placeholder="binary search, sorted, log n" /><p className="text-xs text-muted-foreground">Comma separated</p></div>
            </div>
            {isNew ? (<>
              <div className="space-y-1.5"><Label htmlFor="intro">Introduction</Label><Textarea id="intro" rows={3} required value={f.intro} onChange={set("intro")} placeholder="What is this topic and why does it matter?" /></div>
              <div className="space-y-1.5"><Label htmlFor="example">Example / explanation</Label><Textarea id="example" rows={4} value={f.example} onChange={set("example")} placeholder="Walk through a concrete example step by step." /></div>
              <div className="space-y-1.5"><Label htmlFor="code">Code example</Label><Textarea id="code" rows={8} spellCheck={false} className="font-mono text-xs" value={f.code} onChange={set("code")} placeholder="def binary_search(nums, target): …" /></div>
              <div className="space-y-1.5"><Label htmlFor="details">Complexity & details</Label><Textarea id="details" rows={3} value={f.details} onChange={set("details")} placeholder="Time and space complexity, edge cases, common mistakes." /></div>
            </>) : (
              <div className="space-y-1.5"><Label htmlFor="desc">Lesson HTML</Label><Textarea id="desc" rows={18} spellCheck={false} className="font-mono text-xs" value={f.description} onChange={set("description")} /><p className="text-xs text-muted-foreground">Use &lt;section&gt;, &lt;h4&gt;, &lt;p&gt;, &lt;pre&gt;&lt;code&gt; — check the Preview tab before saving.</p></div>
            )}
          </Card>
        ) : (
          <Card className="p-6"><h2 className="mb-4 text-2xl font-semibold tracking-tight">{f.title || "Untitled topic"}</h2><div className="prose-dark" dangerouslySetInnerHTML={{ __html: previewHtml }} /></Card>
        )}
        <div className="mt-4 flex justify-end gap-2"><Button variant="outline" to="/admin/topics">Cancel</Button><Button type="submit" loading={save.isPending}><Save /> {isNew ? "Publish topic" : "Save changes"}</Button></div>
      </form>
    </Page>
  );
}
