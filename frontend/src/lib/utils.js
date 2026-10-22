import { clsx } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs) { return twMerge(clsx(inputs)); }

export const XP = { easy: 10, medium: 20, hard: 30 };

export function timeAgo(iso) {
  if (!iso) return "";
  const s = Math.max(0, (Date.now() - new Date(iso).getTime()) / 1000);
  if (s < 60) return "just now";
  if (s < 3600) return `${Math.floor(s / 60)}m ago`;
  if (s < 86400) return `${Math.floor(s / 3600)}h ago`;
  if (s < 86400 * 7) return `${Math.floor(s / 86400)}d ago`;
  return new Date(iso).toLocaleDateString(undefined, { day: "numeric", month: "short" });
}

export function fmtDate(iso, opts = { day: "numeric", month: "short", year: "numeric" }) {
  return iso ? new Date(iso).toLocaleDateString(undefined, opts) : "—";
}

export function fmtTime(iso) {
  return iso ? new Date(iso).toLocaleString(undefined, { day: "numeric", month: "short", hour: "numeric", minute: "2-digit" }) : "";
}

export function initials(name = "") {
  return name.split(/[\s_]+/).map((p) => p[0]).join("").slice(0, 2).toUpperCase() || "?";
}

// Chart colours (hex equivalents of the oklch tokens, for Recharts)
export const C = { primary: "#36acff", easy: "#5bc663", medium: "#efa831", hard: "#ff4a63", violet: "#a883ff", muted: "#87909c", border: "#2b3039", card: "#1b1f27", fg: "#e2e9f0" };
