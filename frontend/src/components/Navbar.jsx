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
    <nav className="glass-nav sticky top-0 z-50 border-b border-[#D9CFBE]">
      <div className="mx-auto max-w-7xl px-5 md:px-10 h-16 flex items-center justify-between">
        <Link to="/" data-testid={HOME.navLogo} className="flex items-center gap-2.5">
          <span className="joli-roundel h-8 w-8 text-lg">ȷ</span>
          <span className="joli-wordmark text-3xl">
            jol<span className="tittle">i</span>
          </span>
        </Link>

        <div className="hidden md:flex items-center gap-6 text-sm">
          <Link to="/browse" data-testid={HOME.navBrowse} className="hover:text-[#C8552F] transition-colors">
            Browse
          </Link>
          <Link to="/blog" data-testid={HOME.navBlog} className="hover:text-[#C8552F] transition-colors">
            Journal
          </Link>
          <Link to="/how-it-works" data-testid={HOME.navHowItWorks} className="hover:text-[#C8552F] transition-colors">
            How it works
          </Link>
          {user ? (
            <>
              <Link
                to={dashLink}
                data-testid={HOME.navDashboard}
                className="rounded-full bg-[#1F1A17] text-white px-4 py-2 hover:bg-[#3D332B] transition-colors inline-flex items-center gap-1.5"
              >
                <LayoutDashboard size={14} /> Dashboard
              </Link>
              <button
                data-testid={HOME.navLogout}
                onClick={async () => {
                  await logout();
                  nav("/");
                }}
                className="text-[#6E5F50] hover:text-[#C8552F] inline-flex items-center gap-1.5"
              >
                <LogOut size={14} /> Logout
              </button>
            </>
          ) : (
            <>
              <Link to="/login" data-testid={HOME.navLogin} className="hover:text-[#C8552F] transition-colors">
                Log in
              </Link>
              <Link
                to="/register"
                data-testid={HOME.navRegister}
                className="rounded-full bg-[#C8552F] text-white px-4 py-2 hover:bg-[#A8451C] transition-colors"
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
        <div className="md:hidden border-t border-[#D9CFBE] bg-[#F7F1E8] px-5 py-3 flex flex-col gap-3 text-sm">
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
              <Link to="/register" onClick={() => setOpen(false)} className="py-1 font-semibold text-[#C8552F]">
                Join Joli
              </Link>
            </>
          )}
        </div>
      )}
    </nav>
  );
}
