import { useParams, Link } from "react-router-dom";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { ArrowLeft, ChevronLeft, ChevronRight } from "lucide-react";
import { api } from "@/lib/api";
import { useAuth } from "@/hooks/useAuth";
import Workspace from "@/components/Workspace";
import { ErrorState, Skeleton } from "@/components/ui";

export default function Problem() {
  const { id } = useParams();
  const qc = useQueryClient();
  const { refresh } = useAuth();
  const { data, isLoading, error, refetch } = useQuery({ queryKey: ["problem", id], queryFn: () => api.get(`/api/problems/${id}`) });
  if (isLoading) return <div className="p-4"><Skeleton className="h-[calc(100vh-6rem)]" /></div>;
  if (error) return <ErrorState error={error} retry={refetch} />;
  return (
    <Workspace
      problem={data.problem}
      lastSubmission={data.last_submission}
      onSubmitted={() => { qc.invalidateQueries({ queryKey: ["problems"] }); qc.invalidateQueries({ queryKey: ["dashboard"] }); refresh(); }}
      toolbarLeft={<>
        <Link to="/practice" aria-label="Back to problems" className="grid h-8 w-8 place-items-center rounded-md hover:bg-accent"><ArrowLeft className="h-4 w-4" /></Link>
        <span className="font-mono text-xs text-muted-foreground">{data.problem.id}.</span>
      </>}
      toolbarRight={<div className="hidden items-center sm:flex">
        <Link to={data.prev_id ? `/practice/${data.prev_id}` : "#"} aria-disabled={!data.prev_id} aria-label="Previous problem" className={`grid h-8 w-8 place-items-center rounded-md hover:bg-accent ${!data.prev_id ? "pointer-events-none opacity-40" : ""}`}><ChevronLeft className="h-4 w-4" /></Link>
        <Link to={data.next_id ? `/practice/${data.next_id}` : "#"} aria-disabled={!data.next_id} aria-label="Next problem" className={`grid h-8 w-8 place-items-center rounded-md hover:bg-accent ${!data.next_id ? "pointer-events-none opacity-40" : ""}`}><ChevronRight className="h-4 w-4" /></Link>
      </div>}
    />
  );
}
