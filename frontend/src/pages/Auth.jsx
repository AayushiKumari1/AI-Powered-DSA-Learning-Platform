import { useState } from "react";
import { Link, Navigate, useNavigate, useSearchParams } from "react-router-dom";
import { useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { Eye, EyeOff, Lock, Mail, User } from "lucide-react";
import { api } from "@/lib/api";
import { useAuth } from "@/hooks/useAuth";
import { Button, Input, Label, Tabs } from "@/components/ui";

function Field({ id, label, icon: Icon, type = "text", ...p }) {
  const [show, setShow] = useState(false);
  const isPw = type === "password";
  return (
    <div className="space-y-1.5">
      <Label htmlFor={id}>{label}</Label>
      <div className="relative">
        <Icon className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
        <Input id={id} type={isPw && show ? "text" : type} className={isPw ? "pl-9 pr-10" : "pl-9"} required {...p} />
        {isPw && <button type="button" onClick={() => setShow((s) => !s)} aria-label={show ? "Hide password" : "Show password"} className="absolute right-2 top-1/2 grid h-7 w-7 -translate-y-1/2 place-items-center rounded-md text-muted-foreground hover:text-foreground">{show ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}</button>}
      </div>
    </div>
  );
}

export default function Auth() {
  const { user } = useAuth();
  const [params] = useSearchParams();
  const [mode, setMode] = useState(params.get("mode") === "signup" ? "signup" : "signin");
  const [form, setForm] = useState({ username: "", email: "", password: "" });
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  const qc = useQueryClient();
  const next = params.get("next") || "/dashboard";
  if (user) return <Navigate to={next} replace />;

  const set = (k) => (e) => setForm((f) => ({ ...f, [k]: e.target.value }));
  async function submit(e) {
    e.preventDefault(); setLoading(true);
    try {
      const data = await api.post(mode === "signin" ? "/api/auth/login" : "/api/auth/signup", form);
      qc.setQueryData(["me"], { user: data.user, unread_notifications: 0 });
      qc.invalidateQueries({ queryKey: ["me"] });
      toast.success(mode === "signin" ? `Welcome back, ${data.user.username}` : "Account created");
      navigate(next, { replace: true });
    } catch (err) { toast.error(err.message); }
    setLoading(false);
  }

  return (
    <div className="grid min-h-screen bg-background text-foreground lg:grid-cols-2">
      <div className="hidden flex-col justify-between border-r border-border bg-gradient-to-br from-card to-background p-10 lg:flex">
        <Link to="/" className="flex items-center gap-2">
          <div className="grid h-8 w-8 place-items-center rounded-md bg-primary font-mono font-bold text-primary-foreground">E</div>
          <span className="text-lg font-semibold tracking-tight">EduMentor</span>
        </Link>
        <div>
          <h2 className="text-3xl font-semibold leading-tight tracking-tight">Learn, practice, and prove your coding skills.</h2>
          <p className="mt-4 max-w-md text-muted-foreground">Save flash notes, join community channels, and track your progress on every topic.</p>
          <ul className="mt-6 space-y-2 text-sm text-muted-foreground">
            <li>• Structured DSA tracks with curated YouTube lessons</li>
            <li>• LeetCode-style editor with AI code analysis</li>
            <li>• Visual analytics for XP, focus & topic mastery</li>
          </ul>
        </div>
        <p className="text-xs text-muted-foreground">© EduMentor. Built for serious interview prep.</p>
      </div>
      <div className="flex items-center justify-center p-6 sm:p-10">
        <div className="w-full max-w-sm">
          <Link to="/" className="mb-6 flex items-center gap-2 lg:hidden">
            <div className="grid h-8 w-8 place-items-center rounded-md bg-primary font-mono font-bold text-primary-foreground">E</div>
            <span className="font-semibold tracking-tight">EduMentor</span>
          </Link>
          <h1 className="text-2xl font-semibold tracking-tight">{mode === "signin" ? "Welcome back" : "Create your account"}</h1>
          <p className="mt-1 text-sm text-muted-foreground">{mode === "signin" ? "Sign in to pick up where you left off." : "Track topics, solve problems and earn XP from day one."}</p>
          <Tabs className="mt-6 grid w-full grid-cols-2" value={mode} onChange={setMode} items={[{ value: "signin", label: "Sign in" }, { value: "signup", label: "Sign up" }]} />
          <form onSubmit={submit} className="mt-4 space-y-3">
            {mode === "signup" && <Field id="username" label="Username" icon={User} placeholder="ada_lovelace" autoComplete="username" value={form.username} onChange={set("username")} />}
            <Field id="email" label="Email" icon={Mail} type="email" placeholder="you@example.com" autoComplete="email" value={form.email} onChange={set("email")} />
            <Field id="password" label="Password" icon={Lock} type="password" placeholder="••••••••" minLength={mode === "signup" ? 6 : undefined} autoComplete={mode === "signin" ? "current-password" : "new-password"} value={form.password} onChange={set("password")} />
            <Button type="submit" className="w-full" loading={loading}>{mode === "signin" ? "Sign in" : "Create account"}</Button>
          </form>
          <p className="mt-6 text-center text-xs text-muted-foreground">By continuing you agree to EduMentor's terms and privacy policy.</p>
          <p className="mt-2 text-center text-xs text-muted-foreground">Running the platform? <Link to="/admin/login" className="hover:text-foreground hover:underline">Admin sign in</Link></p>
        </div>
      </div>
    </div>
  );
}
