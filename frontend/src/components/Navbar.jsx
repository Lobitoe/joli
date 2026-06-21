import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "@/contexts/AuthContext";
import { HOME } from "@/constants/testIds";
import { Menu, LogOut, LayoutDashboard, Sparkles } from "lucide-react";
import { useState } from "react";

export default function Navbar() {
  const { user, logout } = useAuth();
  const nav = useNavigate();
  const [open, setOpen] = useState(false);

  const dashLink =
    user?.role === "practitioner"
      ? "/dashboard/practitioner"
      : user?.role === "admin"
      ? "/dashboard/admin"
      : "/dashboard/client";

  return (
    <nav className="glass-nav sticky top-0 z-50 border-b border-[#E2D9CF]">
      <div className="mx-auto max-w-7xl px-5 md:px-10 h-16 flex items-center justify-between">
        <Link to="/" data-testid={HOME.navLogo} className="flex items-center gap-2">
          <span className="inline-flex h-8 w-8 items-center justify-center rounded-full bg-[#984A23] text-white">
            <Sparkles size={16} />
          </span>
          <span className="text-2xl font-serif tracking-tight">Joli</span>
        </Link>

        <div className="hidden md:flex items-center gap-6 text-sm">
          <Link to="/browse" data-testid={HOME.navBrowse} className="hover:text-[#984A23] transition-colors">
            Browse
          </Link>
          <Link to="/blog" data-testid={HOME.navBlog} className="hover:text-[#984A23] transition-colors">
            Journal
          </Link>
          <Link to="/how-it-works" data-testid={HOME.navHowItWorks} className="hover:text-[#984A23] transition-colors">
            How it works
          </Link>
          {user ? (
            <>
              <Link
                to={dashLink}
                data-testid={HOME.navDashboard}
                className="rounded-full bg-[#2B231D] text-white px-4 py-2 hover:bg-[#3a2f27] transition-colors inline-flex items-center gap-1.5"
              >
                <LayoutDashboard size={14} /> Dashboard
              </Link>
              <button
                data-testid={HOME.navLogout}
                onClick={async () => {
                  await logout();
                  nav("/");
                }}
                className="text-[#5C4E43] hover:text-[#984A23] inline-flex items-center gap-1.5"
              >
                <LogOut size={14} /> Logout
              </button>
            </>
          ) : (
            <>
              <Link to="/login" data-testid={HOME.navLogin} className="hover:text-[#984A23] transition-colors">
                Log in
              </Link>
              <Link
                to="/register"
                data-testid={HOME.navRegister}
                className="rounded-full bg-[#984A23] text-white px-4 py-2 hover:bg-[#7e3d1d] transition-colors"
              >
                Join Joli
              </Link>
            </>
          )}
        </div>

        <button className="md:hidden p-2" onClick={() => setOpen((o) => !o)} data-testid="nav-mobile-toggle">
          <Menu size={22} />
        </button>
      </div>

      {open && (
        <div className="md:hidden border-t border-[#E2D9CF] bg-[#FAF9F6] px-5 py-3 flex flex-col gap-3 text-sm">
          <Link to="/browse" onClick={() => setOpen(false)} className="py-1">Browse</Link>
          <Link to="/blog" onClick={() => setOpen(false)} className="py-1">Journal</Link>
          <Link to="/how-it-works" onClick={() => setOpen(false)} className="py-1">How it works</Link>
          {user ? (
            <>
              <Link to={dashLink} onClick={() => setOpen(false)} className="py-1">Dashboard</Link>
              <button
                onClick={async () => {
                  await logout();
                  setOpen(false);
                  nav("/");
                }}
                className="text-left py-1"
              >
                Logout
              </button>
            </>
          ) : (
            <>
              <Link to="/login" onClick={() => setOpen(false)} className="py-1">Log in</Link>
              <Link to="/register" onClick={() => setOpen(false)} className="py-1 font-semibold text-[#984A23]">
                Join Joli
              </Link>
            </>
          )}
        </div>
      )}
    </nav>
  );
}
