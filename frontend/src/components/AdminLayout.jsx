import { useEffect, useState } from "react";
import { Link, Navigate, NavLink, Outlet, useLocation, useNavigate } from "react-router-dom";
import { toast } from "sonner";
import { BarChart3, BookOpen, Code2, FileCheck2, Inbox, LayoutDashboard, LogOut, Megaphone, MessagesSquare, PanelLeft, Plus, ShieldCheck, Users } from "lucide-react";
import { cn } from "@/lib/utils";
import { useAdmin } from "@/hooks/useAdmin";
import { Button, PageSkeleton } from "@/components/ui";

const GROUPS = [
  ["Overview", [["Dashboard", "/admin", LayoutDashboard, true], ["Learners", "/admin/learners", Users], ["Topic analytics", "/admin/topic-analytics", BarChart3]]],
  ["Content", [["Topics", "/admin/topics", BookOpen], ["Problems", "/admin/problems", Code2], ["Tests", "/admin/tests", FileCheck2]]],
  ["Engage", [["Announcements", "/admin/announcements", Megaphone], ["Mentor inbox", "/admin/inbox", Inbox], ["Community", "/admin/community", MessagesSquare]]],
];

export default function AdminLayout() {
  const { isAdmin, loading, signOut } = useAdmin();
  const navigate = useNavigate();
  const { pathname } = useLocation();
  const [collapsed, setCollapsed] = useState(() => localStorage.getItem("em_admin_sidebar") === "collapsed");
  const [mobileOpen, setMobileOpen] = useState(false);
  useEffect(() => setMobileOpen(false), [pathname]);
  if (loading) return <PageSkeleton />;
  if (!isAdmin) return <Navigate to={`/admin/login?next=${encodeURIComponent(pathname)}`} replace />;

  function toggle() {
    if (window.matchMedia("(max-width: 767px)").matches) return setMobileOpen((o) => !o);
    setCollapsed((c) => { localStorage.setItem("em_admin_sidebar", c ? "expanded" : "collapsed"); return !c; });
  }
  const hide = collapsed && "md:hidden";

  return (
    <div className="flex min-h-screen w-full bg-background">
      <div className={cn("hidden shrink-0 transition-[width] duration-200 md:block", collapsed ? "w-12" : "w-64")} />
      {mobileOpen && <div className="fixed inset-0 z-40 bg-black/80 md:hidden" onClick={() => setMobileOpen(false)} />}
      <aside className={cn("fixed inset-y-0 left-0 z-50 flex h-svh w-72 flex-col border-r border-sidebar-border bg-sidebar transition-[width,transform] duration-200 md:z-10 md:translate-x-0",
        mobileOpen ? "translate-x-0" : "-translate-x-full", collapsed ? "md:w-12" : "md:w-64")}>
        <div className="border-b border-sidebar-border p-2">
          <Link to="/admin" className={cn("flex items-center gap-2 px-2 py-2", collapsed && "md:justify-center md:px-0")}>
            <div className="grid h-8 w-8 shrink-0 place-items-center rounded-md bg-primary font-mono font-bold text-primary-foreground">E</div>
            <div className={cn("flex flex-col leading-tight", hide)}><span className="font-semibold tracking-tight">EduMentor</span><span className="text-[10px] uppercase tracking-widest text-muted-foreground">admin console</span></div>
          </Link>
        </div>
        <nav className="flex min-h-0 flex-1 flex-col gap-2 overflow-y-auto p-2" aria-label="Admin">
          {GROUPS.map(([label, items]) => (
            <div key={label}>
              <p className={cn("flex h-8 items-center px-2 text-xs font-medium text-sidebar-foreground/70", hide)}>{label}</p>
              <div className="flex flex-col gap-1">
                {items.map(([title, to, Icon, end]) => (
                  <NavLink key={to} to={to} end={end} title={title} className={({ isActive }) => cn("flex h-8 items-center gap-2 overflow-hidden rounded-md px-2 text-sm text-sidebar-foreground/85 transition-colors hover:bg-sidebar-accent hover:text-sidebar-foreground",
                    isActive && "bg-sidebar-accent font-medium text-sidebar-foreground", collapsed && "md:mx-auto md:w-8 md:justify-center md:px-0")}>
                    <Icon className="h-4 w-4 shrink-0" /><span className={cn("truncate", hide)}>{title}</span>
                  </NavLink>
                ))}
              </div>
            </div>
          ))}
        </nav>
        <div className="border-t border-sidebar-border p-2">
          <div className={cn("flex items-center gap-2 px-2 py-2", collapsed && "md:justify-center md:px-0")}>
            <div className="grid h-9 w-9 shrink-0 place-items-center rounded-full bg-gradient-to-br from-medium to-hard text-sm font-semibold text-primary-foreground">AD</div>
            <div className={cn("flex min-w-0 flex-1 flex-col leading-tight", hide)}><span className="text-sm font-medium">Admin</span><span className="flex items-center gap-1 text-xs text-muted-foreground"><ShieldCheck className="h-3 w-3 text-easy" />Full access</span></div>
            <button aria-label="Sign out" title="Sign out" className={cn("grid h-8 w-8 place-items-center rounded-md hover:bg-accent", hide)}
              onClick={async () => { await signOut(); toast.success("Signed out"); navigate("/admin/login", { replace: true }); }}><LogOut className="h-4 w-4" /></button>
          </div>
        </div>
      </aside>
      <div className="flex min-w-0 flex-1 flex-col">
        <header className="sticky top-0 z-30 flex h-14 items-center gap-3 border-b border-border bg-background/80 px-4 backdrop-blur-md">
          <button onClick={toggle} aria-label="Toggle sidebar" className="grid h-7 w-7 place-items-center rounded-md hover:bg-accent"><PanelLeft className="h-4 w-4" /></button>
          <span className="hidden items-center gap-2 text-sm text-muted-foreground md:flex"><ShieldCheck className="h-4 w-4" />Admin console</span>
          <div className="ml-auto flex items-center gap-2">
            <Button variant="ghost" size="sm" to="/admin/topics/new" className="hidden sm:inline-flex"><Plus /> Topic</Button>
            <Button variant="ghost" size="sm" to="/admin/problems/new" className="hidden sm:inline-flex"><Plus /> Problem</Button>
            <Button size="sm" to="/admin/announcements"><Megaphone /> Announce</Button>
          </div>
        </header>
        <main className="min-w-0 flex-1"><Outlet /></main>
      </div>
    </div>
  );
}
