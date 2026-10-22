import { useState } from "react";
import { Link, Navigate, useNavigate, useSearchParams } from "react-router-dom";
import { useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { Eye, EyeOff, Lock, ShieldCheck, User } from "lucide-react";
import { api } from "@/lib/api";
import { useAdmin } from "@/hooks/useAdmin";
import { Button, Input, Label } from "@/components/ui";

export default function AdminLogin() {
  const { isAdmin } = useAdmin();
  const [params] = useSearchParams();
  const [form, setForm] = useState({ username: "", password: "" });
  const [show, setShow] = useState(false);
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  const qc = useQueryClient();
  const next = params.get("next") || "/admin";
  if (isAdmin) return <Navigate to={next} replace />;
  async function submit(e) {
    e.preventDefault(); setLoading(true);
    try { await api.post("/api/admin/login", form); qc.setQueryData(["admin-me"], { admin: true }); toast.success("Welcome, Admin"); navigate(next, { replace: true }); }
    catch (err) { toast.error(err.message); }
    setLoading(false);
  }
  return (
    <div className="grid min-h-screen bg-background lg:grid-cols-2">
      <div className="hidden flex-col justify-between border-r border-border bg-gradient-to-br from-card to-background p-10 lg:flex">
        <Link to="/" className="flex items-center gap-2"><div className="grid h-8 w-8 place-items-center rounded-md bg-primary font-mono font-bold text-primary-foreground">E</div><span className="text-lg font-semibold tracking-tight">EduMentor</span></Link>
        <div>
          <h2 className="text-3xl font-semibold leading-tight tracking-tight">Run the EduMentor platform.</h2>
          <p className="mt-4 max-w-md text-muted-foreground">Publish topics and problems, build proctored tests, track every learner and keep them informed.</p>
          <ul className="mt-6 space-y-2 text-sm text-muted-foreground">
            <li>• Topic, problem and test management with CSV import</li>
            <li>• Learner analytics with 30-day activity and ML mastery</li>
            <li>• Announcements, a mentor inbox and community moderation</li>
          </ul>
        </div>
        <p className="text-xs text-muted-foreground">© EduMentor admin console</p>
      </div>
      <div className="flex items-center justify-center p-6 sm:p-10">
        <form onSubmit={submit} className="w-full max-w-sm space-y-4">
          <span className="inline-flex items-center gap-1.5 rounded-md border border-border bg-card px-2 py-0.5 text-xs text-muted-foreground"><ShieldCheck className="h-3.5 w-3.5 text-easy" /> Admin console</span>
          <div><h1 className="text-2xl font-semibold tracking-tight">Admin sign in</h1><p className="mt-1 text-sm text-muted-foreground">Use your administrator credentials.</p></div>
          <div className="space-y-1.5"><Label htmlFor="u">Username</Label><div className="relative"><User className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" /><Input id="u" required autoFocus autoComplete="username" className="pl-9" value={form.username} onChange={(e) => setForm({ ...form, username: e.target.value })} /></div></div>
          <div className="space-y-1.5"><Label htmlFor="p">Password</Label><div className="relative"><Lock className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" /><Input id="p" type={show ? "text" : "password"} required autoComplete="current-password" className="pl-9 pr-10" value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} />
            <button type="button" onClick={() => setShow(!show)} aria-label={show ? "Hide password" : "Show password"} className="absolute right-2 top-1/2 grid h-7 w-7 -translate-y-1/2 place-items-center rounded-md text-muted-foreground hover:text-foreground">{show ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}</button></div></div>
          <Button type="submit" className="w-full" loading={loading}>Sign in to console</Button>
          <p className="text-center text-sm text-muted-foreground">Not an admin? <Link to="/auth" className="text-primary hover:underline">Learner sign in</Link></p>
        </form>
      </div>
    </div>
  );
}
