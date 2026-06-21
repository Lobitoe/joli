import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api, formatApiError } from "@/lib/api";
import { BadgeRow } from "@/components/BadgeChip";
import { ArrowLeft, Search, Pause, Play, Star, User, Scissors, ShieldCheck, Calendar, MessageSquare } from "lucide-react";
import { toast } from "sonner";

const ROLE_TABS = [
  { v: "", label: "All", Icon: User },
  { v: "practitioner", label: "Practitioners", Icon: Scissors },
  { v: "client", label: "Clients", Icon: User },
  { v: "admin", label: "Admins", Icon: ShieldCheck },
];

const ACTIVITY_ICON = {
  user_joined: User,
  booking_created: Calendar,
  review_posted: Star,
  verification_submitted: ShieldCheck,
};

export default function AdminUsersPage() {
  const [users, setUsers] = useState([]);
  const [activity, setActivity] = useState([]);
  const [role, setRole] = useState("");
  const [search, setSearch] = useState("");
  const [loading, setLoading] = useState(true);

  const load = async () => {
    setLoading(true);
    const params = {};
    if (role) params.role = role;
    if (search) params.search = search;
    const [u, a] = await Promise.all([
      api.get("/admin/users", { params }),
      api.get("/admin/activity"),
    ]);
    setUsers(u.data);
    setActivity(a.data);
    setLoading(false);
  };

  useEffect(() => { load(); /* eslint-disable-next-line */ }, [role]);

  const onSearch = (e) => {
    e.preventDefault();
    load();
  };

  const toggleSuspend = async (u) => {
    const next = !u.is_suspended;
    const reason = next ? prompt("Reason for suspension (sent to internal log):") : null;
    if (next && reason === null) return; // user cancelled
    try {
      await api.put(`/admin/practitioners/${u.practitioner_id}/suspend`, {
        suspended: next,
        reason: reason || null,
      });
      toast.success(next ? "Practitioner suspended" : "Practitioner reinstated");
      await load();
    } catch (e) {
      toast.error(formatApiError(e.response?.data?.detail));
    }
  };

  return (
    <div className="mx-auto max-w-7xl px-5 md:px-10 py-10">
      <Link to="/dashboard/admin" className="inline-flex items-center gap-1 text-sm text-[#6E5F50] hover:text-[#C8552F] mb-4">
        <ArrowLeft size={14} /> Admin
      </Link>
      <div className="flex items-end justify-between flex-wrap gap-3 mb-6">
        <div>
          <h1 className="font-serif text-4xl md:text-5xl">Users & activity</h1>
          <p className="text-[#6E5F50] mt-1">Monitor accounts, suspend practitioners, watch the marketplace pulse.</p>
        </div>
        <div className="flex gap-2">
          <Link to="/dashboard/admin/verifications" className="rounded-full bg-[#C8552F] hover:bg-[#A8451C] text-white font-semibold px-4 py-2 text-sm inline-flex items-center gap-1">
            <ShieldCheck size={14} /> Verification queue
          </Link>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Users panel */}
        <div className="lg:col-span-2 bg-white rounded-2xl border border-[#D9CFBE] p-5 shadow-card">
          <div className="flex flex-wrap gap-2 items-center justify-between mb-4">
            <div className="flex gap-1.5 flex-wrap">
              {ROLE_TABS.map((t) => (
                <button
                  key={t.v}
                  data-testid={`admin-users-tab-${t.v || "all"}`}
                  onClick={() => setRole(t.v)}
                  className={`chip ${role === t.v ? "chip-active" : ""}`}
                >
                  <t.Icon size={11} /> {t.label}
                </button>
              ))}
            </div>
            <form onSubmit={onSearch} className="flex items-center gap-1 bg-[#EFE8DA] rounded-full px-3 h-10 border border-[#D9CFBE]">
              <Search size={14} className="text-[#6E5F50]" />
              <input
                data-testid="admin-users-search"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                placeholder="Search name or email"
                className="bg-transparent outline-none text-sm w-40 sm:w-56"
              />
            </form>
          </div>

          {loading ? (
            <div className="py-12 text-center text-[#6E5F50]">Loading…</div>
          ) : users.length === 0 ? (
            <div className="py-12 text-center text-[#6E5F50]">No users match.</div>
          ) : (
            <div className="divide-y divide-[#EFE8DA]">
              {users.map((u) => (
                <div key={u.id} data-testid="admin-user-row" className="py-3 flex items-center justify-between gap-3">
                  <div className="min-w-0 flex-1">
                    <div className="flex items-center gap-2 flex-wrap">
                      <div className="font-semibold truncate">{u.name}</div>
                      <span className={`chip text-[10px] capitalize ${u.role === "admin" ? "chip-active" : ""}`}>{u.role}</span>
                      {u.is_suspended && <span className="chip text-[10px] bg-[#B83A2A] text-white border-[#B83A2A]">Suspended</span>}
                      {u.role === "practitioner" && u.verification_status === "verified" && (
                        <span className="chip text-[10px] bg-[#2D7D6F] text-white border-[#2D7D6F]">Verified</span>
                      )}
                    </div>
                    <div className="text-xs text-[#6E5F50] truncate">{u.email}</div>
                    {u.role === "practitioner" && u.practitioner_display_name && (
                      <div className="text-xs text-[#6E5F50] mt-0.5">
                        Studio: <Link to={`/practitioner/${u.practitioner_id}`} className="underline hover:text-[#C8552F]">{u.practitioner_display_name}</Link>
                        {" · "}
                        <span className="num">★ {u.avg_rating || "—"} ({u.total_reviews})</span>
                      </div>
                    )}
                  </div>
                  <div className="text-right flex-shrink-0">
                    <div className="text-xs text-[#6E5F50]">Bookings</div>
                    <div className="num text-lg">{u.bookings_count || 0}</div>
                  </div>
                  {u.role === "practitioner" && u.practitioner_id && (
                    <button
                      data-testid="admin-suspend-toggle"
                      onClick={() => toggleSuspend(u)}
                      className={`rounded-full px-3 py-2 text-xs font-semibold inline-flex items-center gap-1 transition-colors ${
                        u.is_suspended
                          ? "bg-[#2D7D6F] hover:bg-[#236359] text-white"
                          : "border border-[#D9CFBE] hover:border-[#B83A2A] hover:text-[#B83A2A]"
                      }`}
                    >
                      {u.is_suspended ? <><Play size={11} /> Reinstate</> : <><Pause size={11} /> Suspend</>}
                    </button>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Activity feed */}
        <div className="bg-white rounded-2xl border border-[#D9CFBE] p-5 shadow-card" data-testid="admin-activity-feed">
          <h2 className="font-serif text-2xl mb-3 flex items-center gap-2"><MessageSquare size={16} /> Activity</h2>
          <p className="text-xs text-[#6E5F50] mb-4">Last 50 platform events, newest first.</p>
          <div className="space-y-3 max-h-[600px] overflow-y-auto pr-1">
            {activity.length === 0 ? (
              <div className="text-[#6E5F50] text-sm">No activity yet.</div>
            ) : activity.map((a, i) => {
              const Icon = ACTIVITY_ICON[a.kind] || MessageSquare;
              return (
                <div key={`${a.kind}-${a.at}-${i}`} className="border-l-2 border-[#D9CFBE] pl-3 py-1">
                  <div className="flex items-center gap-1.5 text-[10px] uppercase tracking-widest text-[#C8552F] font-bold">
                    <Icon size={11} /> {a.kind.replace(/_/g, " ")}
                  </div>
                  <div className="text-sm mt-1 text-[#1F1A17]">{a.summary}</div>
                  <div className="text-[10px] text-[#6E5F50] mt-0.5 num">{new Date(a.at).toLocaleString("en-CA")}</div>
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
}
