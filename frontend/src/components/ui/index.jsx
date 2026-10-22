// shadcn/ui-style primitives matching DSA Study Buddy's components
import { forwardRef } from "react";
import { Link } from "react-router-dom";
import { Loader2 } from "lucide-react";
import { cn } from "@/lib/utils";

const variants = {
  default: "bg-primary text-primary-foreground shadow hover:bg-primary/90",
  destructive: "bg-destructive text-destructive-foreground shadow-sm hover:bg-destructive/90",
  outline: "border border-input bg-background shadow-sm hover:bg-accent hover:text-accent-foreground",
  secondary: "bg-secondary text-secondary-foreground shadow-sm hover:bg-secondary/80",
  ghost: "hover:bg-accent hover:text-accent-foreground",
  link: "text-primary underline-offset-4 hover:underline",
};
const sizes = { default: "h-9 px-4 py-2", sm: "h-8 rounded-md px-3 text-xs", lg: "h-10 rounded-md px-8", icon: "h-9 w-9" };
export const buttonClass = (variant = "default", size = "default", className) =>
  cn("inline-flex items-center justify-center gap-2 whitespace-nowrap rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:pointer-events-none disabled:opacity-50 [&_svg]:pointer-events-none [&_svg]:size-4 [&_svg]:shrink-0",
    variants[variant], sizes[size], className);

export const Button = forwardRef(function Button({ variant, size, className, to, href, loading, children, ...props }, ref) {
  const cls = buttonClass(variant, size, className);
  if (to) return <Link to={to} className={cls} ref={ref} {...props}>{children}</Link>;
  if (href) return <a href={href} className={cls} ref={ref} {...props}>{children}</a>;
  return <button ref={ref} className={cls} disabled={loading || props.disabled} {...props}>{loading && <Loader2 className="animate-spin" />}{children}</button>;
});

export const Card = ({ className, ...p }) => <div className={cn("rounded-xl border border-border bg-card text-card-foreground shadow", className)} {...p} />;

export const Input = forwardRef(function Input({ className, ...p }, ref) {
  return <input ref={ref} className={cn("flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-base shadow-sm transition-colors placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:opacity-50 md:text-sm", className)} {...p} />;
});

export const Textarea = forwardRef(function Textarea({ className, ...p }, ref) {
  return <textarea ref={ref} className={cn("flex min-h-[60px] w-full rounded-md border border-input bg-transparent px-3 py-2 text-base shadow-sm placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring md:text-sm", className)} {...p} />;
});

export const Label = ({ className, ...p }) => <label className={cn("text-sm font-medium leading-none", className)} {...p} />;

export function Progress({ value = 0, className, color }) {
  return (
    <div className={cn("relative h-2 w-full overflow-hidden rounded-full bg-primary/20", className)} role="progressbar" aria-valuenow={Math.round(value)} aria-valuemin={0} aria-valuemax={100}>
      <div className="h-full bg-primary transition-all" style={{ width: `${Math.min(100, Math.max(0, value))}%`, ...(color ? { background: color } : {}) }} />
    </div>
  );
}

export function DifficultyBadge({ difficulty }) {
  const d = (difficulty || "").toLowerCase();
  const map = { easy: "bg-easy/15 text-easy border-easy/30", medium: "bg-medium/15 text-medium border-medium/30", hard: "bg-hard/15 text-hard border-hard/30" };
  return <span className={cn("inline-flex items-center rounded-md border px-2 py-0.5 text-xs font-medium", map[d] || "border-border bg-muted text-muted-foreground")}>{d ? d[0].toUpperCase() + d.slice(1) : "—"}</span>;
}

export function Badge({ tone = "muted", className, ...p }) {
  const tones = { muted: "border-border bg-muted text-muted-foreground", primary: "bg-primary/15 text-primary border-primary/30", easy: "bg-easy/15 text-easy border-easy/30", medium: "bg-medium/15 text-medium border-medium/30", hard: "bg-hard/15 text-hard border-hard/30", violet: "bg-chart-5/15 text-chart-5 border-chart-5/30" };
  return <span className={cn("inline-flex items-center gap-1 rounded-md border px-2 py-0.5 text-xs font-medium", tones[tone], className)} {...p} />;
}

export function Tabs({ value, onChange, items, className, size }) {
  return (
    <div role="tablist" className={cn("inline-flex h-9 items-center justify-center rounded-lg bg-muted p-1 text-muted-foreground", size === "sm" && "h-8", className)}>
      {items.map((it) => (
        <button key={it.value} type="button" role="tab" aria-selected={value === it.value} onClick={() => onChange(it.value)}
          className={cn("inline-flex items-center justify-center gap-1.5 whitespace-nowrap rounded-md px-3 py-1 text-sm font-medium transition-all", size === "sm" && "h-6 text-xs", value === it.value && "bg-background text-foreground shadow")}>
          {it.icon && <it.icon className="h-3.5 w-3.5" />}{it.label}{it.count != null && <span className="text-xs text-muted-foreground">{it.count}</span>}
        </button>
      ))}
    </div>
  );
}

export function IconTile({ icon: Icon, color = "var(--primary)", className, iconClass = "h-4 w-4" }) {
  return (
    <span className={cn("grid h-7 w-7 shrink-0 place-items-center rounded-md", className)} style={{ background: `color-mix(in oklab, ${color} 18%, transparent)`, color }}>
      <Icon className={iconClass} />
    </span>
  );
}

export function StatCard({ icon, label, value, accent, sub }) {
  return (
    <Card className="p-4">
      <div className="mb-2 flex items-center gap-2 text-xs text-muted-foreground"><IconTile icon={icon} color={accent} />{label}</div>
      <p className="text-2xl font-semibold tracking-tight">{value}</p>
      {sub && <p className="mt-1 text-xs text-muted-foreground">{sub}</p>}
    </Card>
  );
}

export function PageHeader({ title, subtitle, eyebrow, children }) {
  return (
    <div className="mb-6 flex flex-wrap items-end justify-between gap-4">
      <div className="min-w-0">
        {eyebrow && <p className="text-sm text-muted-foreground">{eyebrow}</p>}
        <h1 className="text-2xl font-semibold tracking-tight md:text-3xl">{title}</h1>
        {subtitle && <p className="mt-1 text-sm text-muted-foreground">{subtitle}</p>}
      </div>
      {children && <div className="flex flex-wrap items-center gap-2">{children}</div>}
    </div>
  );
}

export function Empty({ icon: Icon, title, text, action }) {
  return (
    <div className="flex flex-col items-center justify-center px-6 py-12 text-center">
      <IconTile icon={Icon} color="var(--muted-foreground)" className="mb-3 h-10 w-10" iconClass="h-5 w-5" />
      <p className="font-medium">{title}</p>
      {text && <p className="mt-1 max-w-sm text-sm text-muted-foreground">{text}</p>}
      {action && <div className="mt-4">{action}</div>}
    </div>
  );
}

export function Skeleton({ className }) { return <div className={cn("animate-pulse rounded-md bg-primary/10", className)} />; }

export function PageSkeleton() {
  return (
    <Page>
      <Skeleton className="mb-2 h-4 w-32" /><Skeleton className="mb-8 h-8 w-72" />
      <div className="mb-8 grid grid-cols-2 gap-4 md:grid-cols-4">{[0, 1, 2, 3].map((i) => <Skeleton key={i} className="h-24" />)}</div>
      <Skeleton className="h-72" />
    </Page>
  );
}

export function ErrorState({ error, retry }) {
  return (
    <Page><Card><Empty icon={Loader2} title="Couldn't load this page" text={error?.message || "Check that the Flask server is running, then try again."} action={retry && <Button variant="outline" size="sm" onClick={retry}>Try again</Button>} /></Card></Page>
  );
}

export const Page = ({ className, ...p }) => <div className={cn("mx-auto w-full max-w-7xl px-4 py-6 md:px-8 md:py-10", className)} {...p} />;

export function Breadcrumbs({ items }) {
  return (
    <nav aria-label="Breadcrumb" className="mb-4 flex items-center gap-1.5 text-sm text-muted-foreground">
      {items.map((it, i) => (
        <span key={i} className="flex min-w-0 items-center gap-1.5">
          {i > 0 && <span aria-hidden>/</span>}
          {it.to ? <Link to={it.to} className="truncate hover:text-foreground">{it.label}</Link> : <span className="truncate text-foreground">{it.label}</span>}
        </span>
      ))}
    </nav>
  );
}

export const chartTooltip = { contentStyle: { background: "var(--popover)", border: "1px solid var(--border)", borderRadius: 8, fontSize: 12 }, labelStyle: { color: "var(--foreground)" }, itemStyle: { color: "var(--foreground)" }, cursor: { fill: "oklch(30% .04 245 / .25)" } };
