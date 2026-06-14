import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { api } from "@/lib/api";
import { PRACTITIONER_DASH } from "@/constants/testIds";
import { Copy, ExternalLink, Calendar, DollarSign, Star, Settings, Image as ImageIcon, Clock, MessageSquare } from "lucide-react";
import { toast } from "sonner";

export default function PractitionerDashboard() {
  const [data, setData] = useState(null);
  const [notifications, setNotifications] = useState([]);
  const nav = useNavigate();

  useEffect(() => {
    api.get("/me/practitioner/dashboard").then((r) => {
      if (!r.data.exists) {
        nav("/dashboard/practitioner/onboarding");
        return;
      }
      setData(r.data);
    });
    api.get("/me/notifications").then((r) => setNotifications(r.data));
  }, [nav]);

  if (!data) return <div className="py-20 text-center text-[#5C4E43]">Loading…</div>;
  const s = data.stats;
  const link = `${window.location.origin}/p/${s.direct_booking_slug}`;

  const copy = () => {
    navigator.clipboard.writeText(link);
    toast.success("Link copied — share it on Instagram, WhatsApp, anywhere");
  };

  return (
    <div className="mx-auto max-w-6xl px-5 md:px-10 py-10">
      <div className="flex items-center justify-between flex-wrap gap-3 mb-6">
        <div>
          <h1 className="font-serif text-4xl md:text-5xl">Your studio</h1>
          <p className="text-[#5C4E43] mt-1">Bookings, earnings, and your community in one place.</p>
        </div>
        <Link to="/dashboard/practitioner/onboarding" data-testid={PRACTITIONER_DASH.editProfileButton} className="rounded-full border border-[#E2D9CF] hover:border-[#984A23] px-4 py-2 text-sm inline-flex items-center gap-1">
          <Settings size={14} /> Edit profile
        </Link>
      </div>

      {/* Direct link */}
      <div className="bg-gradient-to-br from-[#2B231D] to-[#4a3a30] text-white rounded-2xl p-6 mb-6">
        <div className="text-xs uppercase tracking-widest text-[#C57245]">Your zero-commission link</div>
        <div className="font-serif text-2xl mt-1">Share once. Book forever. 0% commission.</div>
        <div className="mt-4 flex gap-2 flex-wrap items-center">
          <input
            data-testid={PRACTITIONER_DASH.shareLinkInput}
            readOnly
            value={link}
            className="flex-1 min-w-[200px] bg-white/10 border border-white/20 rounded-full px-4 h-11 text-sm"
          />
          <button data-testid={PRACTITIONER_DASH.copyLinkButton} onClick={copy} className="rounded-full bg-[#C57245] hover:bg-[#a35a32] px-4 h-11 text-sm font-semibold inline-flex items-center gap-1">
            <Copy size={14} /> Copy
          </button>
          <a href={link} target="_blank" rel="noreferrer" className="rounded-full border border-white/30 hover:border-white px-4 h-11 text-sm font-semibold inline-flex items-center gap-1">
            <ExternalLink size={14} /> Preview
          </a>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
        <StatCard testid={PRACTITIONER_DASH.earningsCard} label="Gross GMV" value={`$${s.gross_gmv}`} icon={<DollarSign size={16} />} />
        <StatCard label="Net payout" value={`$${s.net_payout}`} icon={<DollarSign size={16} />} accent />
        <StatCard label="Upcoming" value={s.upcoming_bookings} icon={<Calendar size={16} />} />
        <StatCard label="Rating" value={`${s.avg_rating || "—"} (${s.total_reviews})`} icon={<Star size={16} />} />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 bg-white rounded-2xl border border-[#E2D9CF] p-6" data-testid={PRACTITIONER_DASH.upcomingBookings}>
          <div className="flex items-center justify-between mb-3">
            <h2 className="font-serif text-2xl">Upcoming bookings</h2>
            <Link to="#" onClick={() => nav(0)} className="text-xs text-[#984A23] hover:underline">Refresh</Link>
          </div>
          {data.upcoming.length === 0 ? (
            <div className="text-[#5C4E43] text-sm">No upcoming bookings yet.</div>
          ) : (
            <div className="space-y-3">
              {data.upcoming.map((b) => (
                <div key={b.id} data-testid={PRACTITIONER_DASH.bookingCard} className="border border-[#E2D9CF] rounded-2xl p-4">
                  <div className="flex items-start justify-between gap-3">
                    <div>
                      <div className="font-semibold">{b.service_name}</div>
                      <div className="text-xs text-[#5C4E43] mt-0.5">{b.client_name} · {b.client_email}</div>
                      <div className="text-sm mt-1">{b.booking_date} · {b.start_time}–{b.end_time}</div>
                      {b.service_location === "client_location" && (
                        <div className="text-xs text-[#5C4E43] mt-1">📍 Mobile to: {b.client_address}</div>
                      )}
                      {b.client_notes && <div className="text-xs italic text-[#5C4E43] mt-1">"{b.client_notes}"</div>}
                    </div>
                    <div className="text-right">
                      <div className="font-serif text-lg">${b.quoted_price}</div>
                      <div className="text-xs text-[#5C4E43]">Deposit ${b.deposit_amount}</div>
                      <div className="text-xs text-[#5C4E43]">Commission ${b.commission_amount}</div>
                      <span className="chip text-[10px] mt-2">{b.client_source === "direct_link" ? "Direct (0%)" : b.is_first_marketplace_booking ? "Marketplace 10%" : "Repeat 0%"}</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        <div className="space-y-6">
          <div className="bg-white rounded-2xl border border-[#E2D9CF] p-6">
            <h2 className="font-serif text-xl mb-3">Quick actions</h2>
            <div className="space-y-2">
              <Link to="/dashboard/practitioner/services" data-testid={PRACTITIONER_DASH.manageServicesButton} className="flex items-center justify-between rounded-xl border border-[#E2D9CF] hover:border-[#984A23] p-3 text-sm">
                <span className="flex items-center gap-2"><Settings size={14} /> Manage services</span>
                <span>→</span>
              </Link>
              <Link to="/dashboard/practitioner/portfolio" data-testid={PRACTITIONER_DASH.managePortfolioButton} className="flex items-center justify-between rounded-xl border border-[#E2D9CF] hover:border-[#984A23] p-3 text-sm">
                <span className="flex items-center gap-2"><ImageIcon size={14} /> Manage portfolio</span>
                <span>→</span>
              </Link>
              <Link to="/dashboard/practitioner/availability" data-testid={PRACTITIONER_DASH.manageAvailabilityButton} className="flex items-center justify-between rounded-xl border border-[#E2D9CF] hover:border-[#984A23] p-3 text-sm">
                <span className="flex items-center gap-2"><Clock size={14} /> Manage availability</span>
                <span>→</span>
              </Link>
            </div>
          </div>

          <div className="bg-white rounded-2xl border border-[#E2D9CF] p-6">
            <h2 className="font-serif text-xl flex items-center gap-2"><MessageSquare size={16} /> Recent alerts</h2>
            <div className="space-y-2 mt-3 max-h-64 overflow-y-auto">
              {notifications.length === 0 ? (
                <div className="text-[#5C4E43] text-sm">No alerts yet.</div>
              ) : notifications.slice(0, 5).map((n) => (
                <div key={n.id} className="bg-[#F3EFEA] rounded-xl p-3 text-xs">{n.body}</div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function StatCard({ label, value, icon, accent, testid }) {
  return (
    <div data-testid={testid} className={`rounded-2xl p-5 border ${accent ? "bg-[#984A23] text-white border-[#984A23]" : "bg-white border-[#E2D9CF]"}`}>
      <div className={`text-xs uppercase tracking-widest ${accent ? "text-white/80" : "text-[#5C4E43]"} flex items-center gap-1`}>
        {icon} {label}
      </div>
      <div className="font-serif text-3xl mt-2">{value}</div>
    </div>
  );
}
