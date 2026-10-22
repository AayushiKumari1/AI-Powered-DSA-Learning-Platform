import { useEffect, useState } from "react";
import { Link, NavLink, Outlet, useLocation, useNavigate } from "react-router-dom";
import { toast } from "sonner";
import {
  BarChart3, Bell, BookOpen, Code2, FileCheck2, LayoutDashboard, LogOut, MessageCircle,
  MessagesSquare, PanelLeft, Search, Sparkles, StickyNote, Zap,
} from "lucide-react";
import { cn, initials } from "@/lib/utils";
import { useAuth } from "@/hooks/useAuth";
import { Input } from "@/components/ui";
import AiMentor from "@/components/AiMentor";

const PRIMARY = [
  { title: "Dashboard", url: "/dashboard", icon: LayoutDashboard },
  { title: "Practice", url: "/practice", icon: Code2 },
  { title: "Learn", url: "/learn", icon: BookOpen },
  { title: "Analytics", url: "/analytics", icon: BarChart3 },
  { title: "Tests", url: "/tests", icon: FileCheck2 },
];
const SECONDARY = [
  { title: "Notes", url: "/notes", icon: StickyNote },
  { title: "Community", url: "/community", icon: MessagesSquare },
  { title: "Ask a mentor", url: "/mentor", icon: MessageCircle },
  { title: "Notifications", url: "/notifications", icon: Bell, badge: "unread" },
];

export default function AppLayout() {
  const { user, unread, signOut } = useAuth();
  const navigate = useNavigate();
  const { pathname } = useLocation();
  const [collapsed, setCollapsed] = useState(() => localStorage.getItem("em_sidebar") === "collapsed");
  const [mobileOpen, setMobileOpen] = useState(false);
  const [q, setQ] = useState("");
  const fullBleed = /^\/(practice\/\d+|tests\/\d+\/solve)/.test(pathname);

  useEffect(() => setMobileOpen(false), [pathname]);
  useEffect(() => {
    const onKey = (e) => {
      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "b") { e.preventDefault(); toggle(); }
      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "k") { e.preventDefault(); document.getElementById("global-search")?.focus(); }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  });
  function toggle() {
    if (window.matchMedia("(max-width: 767px)").matches) return setMobileOpen((o) => !o);
    setCollapsed((c) => { localStorage.setItem("em_sidebar", c ? "expanded" : "collapsed"); return !c; });
  }
  async function handleSignOut() { await signOut(); toast.success("Signed out"); navigate("/auth", { replace: true }); }

  const name = user?.username || "Learner";
  const item = (it) => (
    <NavLink key={it.title} to={it.url} title={it.title}
      className={({ isActive }) => cn("flex h-8 w-full items-center gap-2 overflow-hidden rounded-md px-2 text-sm text-sidebar-foreground/85 transition-colors hover:bg-sidebar-accent hover:text-sidebar-foreground [&>svg]:size-4 [&>svg]:shrink-0",
        isActive && "bg-sidebar-accent font-medium text-sidebar-foreground", collapsed && "md:mx-auto md:w-8 md:justify-center md:px-0")}>
      <it.icon /><span className={cn("flex-1 truncate", collapsed && "md:hidden")}>{it.title}</span>
      {it.badge === "unread" && unread > 0 && <span className={cn("rounded-md bg-primary/15 px-1.5 text-[10px] font-semibold text-primary", collapsed && "md:hidden")}>{unread}</span>}
    </NavLink>
  );

  return (
    <div className="flex min-h-screen w-full bg-background">
      <div className={cn("hidden shrink-0 transition-[width] duration-200 ease-linear md:block", collapsed ? "w-12" : "w-64")} />
      {mobileOpen && <div className="fixed inset-0 z-40 bg-black/80 md:hidden" onClick={() => setMobileOpen(false)} />}
      <aside className={cn("fixed inset-y-0 left-0 z-50 flex h-svh flex-col border-r border-sidebar-border bg-sidebar text-sidebar-foreground transition-[width,transform] duration-200 ease-linear md:z-10",
        "w-72 md:translate-x-0", mobileOpen ? "translate-x-0" : "-translate-x-full", collapsed ? "md:w-12" : "md:w-64")}>
        <div className="border-b border-sidebar-border p-2">
          <Link to="/" className={cn("flex items-center gap-2 px-2 py-2", collapsed && "md:justify-center md:px-0")}>
            <div className="grid h-8 w-8 shrink-0 place-items-center rounded-md bg-primary font-mono font-bold text-primary-foreground">E</div>
            <div className={cn("flex flex-col leading-tight", collapsed && "md:hidden")}>
              <span className="font-semibold tracking-tight">EduMentor</span>
              <span className="text-[10px] uppercase tracking-widest text-muted-foreground">learn · practice · prove</span>
            </div>
          </Link>
        </div>
        <nav className="flex min-h-0 flex-1 flex-col gap-2 overflow-y-auto p-2" aria-label="Main">
          <div><p className={cn("flex h-8 items-center px-2 text-xs font-medium text-sidebar-foreground/70", collapsed && "md:hidden")}>Workspace</p><div className="flex flex-col gap-1">{PRIMARY.map(item)}</div></div>
          <div><p className={cn("flex h-8 items-center px-2 text-xs font-medium text-sidebar-foreground/70", collapsed && "md:hidden")}>More</p><div className="flex flex-col gap-1">{SECONDARY.map(item)}</div></div>
        </nav>
        <div className="border-t border-sidebar-border p-2">
          <div className={cn("flex items-center gap-2 px-2 py-2", collapsed && "md:justify-center md:px-0")}>
            <div className="grid h-9 w-9 shrink-0 place-items-center rounded-full bg-gradient-to-br from-primary to-chart-5 text-sm font-semibold text-primary-foreground" title={name}>{initials(name)}</div>
            <div className={cn("flex min-w-0 flex-1 flex-col leading-tight", collapsed && "md:hidden")}>
              <span className="truncate text-sm font-medium">{name}</span>
              <span className="flex items-center gap-1 text-xs text-muted-foreground"><Zap className="h-3 w-3 text-medium" /> {user?.xp ?? 0} XP{user?.badge ? ` · ${user.badge.icon}` : ""}</span>
            </div>
            <button onClick={handleSignOut} aria-label="Sign out" title="Sign out" className={cn("grid h-8 w-8 shrink-0 place-items-center rounded-md hover:bg-accent", collapsed && "md:hidden")}><LogOut className="h-4 w-4" /></button>
          </div>
        </div>
      </aside>

      <div className="flex min-w-0 flex-1 flex-col">
        <header className="sticky top-0 z-30 flex h-14 items-center gap-3 border-b border-border bg-background/80 px-4 backdrop-blur-md">
          <button onClick={toggle} aria-label="Toggle sidebar" className="grid h-7 w-7 place-items-center rounded-md hover:bg-accent"><PanelLeft className="h-4 w-4" /></button>
          <form className="hidden max-w-md flex-1 items-center gap-2 md:flex" role="search"
            onSubmit={(e) => { e.preventDefault(); navigate(`/learn?search=${encodeURIComponent(q)}`); }}>
            <div className="relative w-full">
              <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
              <Input id="global-search" value={q} onChange={(e) => setQ(e.target.value)} placeholder="Search problems, lessons, tests…" className="h-9 border-border bg-card pl-9 pr-14" aria-label="Search" />
              <kbd className="pointer-events-none absolute right-2 top-1/2 -translate-y-1/2 rounded border border-border bg-muted px-1.5 py-0.5 font-mono text-[10px] text-muted-foreground">Ctrl K</kbd>
            </div>
          </form>
          <div className="ml-auto flex items-center gap-2">
            <Link to="/practice" className="hidden h-8 items-center gap-1.5 rounded-md px-3 text-xs font-medium hover:bg-accent sm:inline-flex"><Sparkles className="h-4 w-4 text-medium" />Daily Challenge</Link>
            <Link to="/notifications" aria-label={`Notifications${unread ? ` (${unread} unread)` : ""}`} className="relative grid h-9 w-9 place-items-center rounded-md hover:bg-accent">
              <Bell className="h-4 w-4" />
              {unread > 0 && <span className="absolute right-2 top-2 h-2 w-2 rounded-full bg-hard ring-2 ring-background" />}
            </Link>
          </div>
        </header>
        <main className="min-w-0 flex-1"><Outlet /></main>
      </div>
      {!fullBleed || pathname.startsWith("/practice") ? <AiMentor /> : null}
    </div>
  );
}
