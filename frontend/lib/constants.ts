export const APP_NAME = "DataSpot AI";
export const APP_TAGLINE = "Find the signal in your data.";

export const NAV_ITEMS = [
  { href: "/dashboard", label: "Dashboard", icon: "LayoutDashboard" },
  { href: "/data-insights", label: "Data Insights", icon: "Sparkles" },
  { href: "/predictive-analysis", label: "Predictive Analysis", icon: "TrendingUp" },
  { href: "/data-quality", label: "Data Quality", icon: "ShieldCheck" },
  { href: "/ai-insights", label: "AI Insights", icon: "BrainCircuit" },
  { href: "/decision-making", label: "Decision Making", icon: "Target" },
  { href: "/export-results", label: "Export Results", icon: "Download" },
  { href: "/projects", label: "Projects", icon: "FolderKanban" },
  { href: "/datasets", label: "Datasets", icon: "Database" },
  { href: "/chat", label: "Chat Assistant", icon: "MessageCircle" },
] as const;

export const NAV_FOOTER_ITEMS = [
  { href: "/settings", label: "Settings", icon: "Settings" },
  { href: "/profile", label: "User Profile", icon: "UserCircle" },
] as const;
