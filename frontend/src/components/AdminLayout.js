import { Outlet, NavLink, useNavigate, Link } from "react-router-dom";
import { useAuth } from "@/context/AuthContext";
import { LayoutDashboard, Users, CalendarDays, Building2, ClipboardList, BarChart3, LogOut, Heart } from "lucide-react";

const nav = [
  { to: "/admin", icon: LayoutDashboard, label: "Overview", end: true },
  { to: "/admin/candidates", icon: Users, label: "Candidates" },
  { to: "/admin/events", icon: CalendarDays, label: "Training Sessions" },
  { to: "/admin/organisations", icon: Building2, label: "Organisations" },
  { to: "/admin/questions", icon: ClipboardList, label: "MCQ Questions" },
  { to: "/admin/reports", icon: BarChart3, label: "Reports" },
];

export default function AdminLayout() {
  const { admin, logout } = useAuth();
  const navigate = useNavigate();

  const doLogout = () => {
    logout();
    navigate("/admin/login");
  };

  return (
    <div className="min-h-screen bg-slate-50 flex">
      <aside className="w-64 kfr-navy text-white flex flex-col shrink-0 sticky top-0 h-screen">
        <Link to="/admin" className="p-6 border-b border-white/10 flex items-center gap-3" data-testid="side-brand">
          <img src="/assets/kfr-shield.png" alt="KFR" className="h-10 w-auto" />
          <div>
            <div className="font-display font-bold text-sm">Kerala First Responders</div>
            <div className="text-[9px] uppercase tracking-[0.25em] text-kfr-gold mt-0.5">Admin Console</div>
          </div>
        </Link>
        <nav className="flex-1 py-6 space-y-1 px-3">
          {nav.map((n) => {
            const Icon = n.icon;
            return (
              <NavLink
                key={n.to}
                to={n.to}
                end={n.end}
                data-testid={`nav-${n.label.toLowerCase().replace(/\s/g, "-")}`}
                className={({ isActive }) =>
                  `flex items-center gap-3 px-4 py-2.5 rounded-md text-sm transition-colors ${
                    isActive ? "bg-white/10 text-white" : "text-white/60 hover:text-white hover:bg-white/5"
                  }`
                }
              >
                <Icon className="w-4 h-4" />
                {n.label}
              </NavLink>
            );
          })}
        </nav>
        <div className="p-4 border-t border-white/10">
          <div className="px-3 py-2">
            <div className="text-white/50 text-[10px] uppercase tracking-widest">Signed in</div>
            <div className="text-white text-sm mt-1 truncate">{admin?.email}</div>
          </div>
          <button onClick={doLogout} data-testid="admin-logout-btn" className="w-full mt-2 flex items-center gap-3 px-4 py-2.5 rounded-md text-sm text-white/70 hover:text-white hover:bg-white/5 transition-colors">
            <LogOut className="w-4 h-4" /> Sign out
          </button>
        </div>
      </aside>

      <main className="flex-1 min-w-0">
        <Outlet />
      </main>
    </div>
  );
}
