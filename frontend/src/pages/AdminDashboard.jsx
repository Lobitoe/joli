import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { ADMIN_DASH } from "@/constants/testIds";
import { Users, DollarSign, Calendar, TrendingUp } from "lucide-react";

export default function AdminDashboard() {
  const [data, setData] = useState(null);

  useEffect(() => {
    api.get("/admin/stats").then((r) => setData(r.data));
  }, []);

  if (!data) return <div className="py-20 text-center text-[#5C4E43]">Loading…</div>;

  const cards = [
    { testid: ADMIN_DASH.gmvCard, label: "GMV", value: `$${data.gmv}`, icon: <DollarSign size={16} /> },
    { testid: ADMIN_DASH.revenueCard, label: "Commission revenue", value: `$${data.commission_revenue}`, icon: <TrendingUp size={16} />, accent: true },
    { testid: ADMIN_DASH.practitionersCard, label: "Practitioners", value: data.total_practitioners, icon: <Users size={16} /> },
    { testid: ADMIN_DASH.clientsCard, label: "Clients", value: data.total_clients, icon: <Users size={16} /> },
  ];

  return (
    <div className="mx-auto max-w-6xl px-5 md:px-10 py-10">
      <h1 className="font-serif text-4xl md:text-5xl">Admin</h1>
      <p className="text-[#5C4E43] mt-1 mb-6">Marketplace health at a glance.</p>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
        {cards.map((c) => (
          <div key={c.label} data-testid={c.testid} className={`rounded-2xl p-5 border ${c.accent ? "bg-[#4A5D23] text-white border-[#4A5D23]" : "bg-white border-[#E2D9CF]"}`}>
            <div className={`text-xs uppercase tracking-widest ${c.accent ? "text-white/80" : "text-[#5C4E43]"} flex items-center gap-1`}>{c.icon} {c.label}</div>
            <div className="font-serif text-3xl mt-2">{c.value}</div>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="md:col-span-1 bg-white rounded-2xl border border-[#E2D9CF] p-6">
          <h2 className="font-serif text-xl mb-3">Supply mix</h2>
          <div className="space-y-2">
            {Object.entries(data.practitioners_by_type).map(([k, v]) => (
              <div key={k} className="flex items-center justify-between text-sm">
                <span className="capitalize">{k.replace("_", " ")}</span>
                <span className="font-semibold">{v}</span>
              </div>
            ))}
          </div>
        </div>
        <div className="md:col-span-2 bg-white rounded-2xl border border-[#E2D9CF] p-6" data-testid={ADMIN_DASH.recentBookingsTable}>
          <h2 className="font-serif text-xl mb-3 flex items-center gap-2"><Calendar size={16} /> Recent bookings</h2>
          <div className="space-y-2">
            {data.recent_bookings.length === 0 && <div className="text-[#5C4E43] text-sm">No bookings yet.</div>}
            {data.recent_bookings.map((b) => (
              <div key={b.id} className="flex items-center justify-between text-sm border-b border-[#E2D9CF] py-2 last:border-0">
                <div>
                  <div className="font-semibold">{b.service_name}</div>
                  <div className="text-xs text-[#5C4E43]">{b.client_name} → {b.practitioner_name} · {b.booking_date}</div>
                </div>
                <div className="text-right">
                  <div className="font-serif">${b.quoted_price}</div>
                  <div className="text-xs text-[#5C4E43]">commission ${b.commission_amount}</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
