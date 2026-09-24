import {
  LayoutDashboard,
  Bot,
  ScrollText,
  GitCompare,
  FileText,
  ClipboardList,
} from "lucide-react"

export const navigationItems = [
  {
    label: "Dashboard",
    path: "/dashboard",
    icon: LayoutDashboard,
  },
  {
    label: "Compliance Copilot",
    path: "/copilot",
    icon: Bot,
  },
  {
    label: "Active Rules",
    path: "/rules",
    icon: ScrollText,
  },
  {
    label: "Compare Rules",
    path: "/compare",
    icon: GitCompare,
  },
  {
    label: "Documents",
    path: "/documents",
    icon: FileText,
  },
  {
    label: "Audit Trail",
    path: "/audit",
    icon: ClipboardList,
  },
]