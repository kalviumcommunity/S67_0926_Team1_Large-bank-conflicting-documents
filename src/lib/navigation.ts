export interface NavigationItem {
  label: string;
  path: string;
  icon: string;
}

export const navigationItems: NavigationItem[] = [
  {
    label: "Compliance Copilot",
    path: "/",
    icon: "✦",
  },
  {
    label: "Dashboard",
    path: "/dashboard",
    icon: "▦",
  },
  {
    label: "Active Rules",
    path: "/rules",
    icon: "✓",
  },
  {
    label: "Compare Rules",
    path: "/compare",
    icon: "⇄",
  },
  {
    label: "Documents",
    path: "/documents",
    icon: "▤",
  },
  {
    label: "Audit Trail",
    path: "/audit",
    icon: "◷",
  },
];