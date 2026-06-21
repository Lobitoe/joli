import { useEffect, useState } from "react";
import { useParams, useNavigate, Link } from "react-router-dom";
import { api } from "@/lib/api";
import { Sparkles, MapPin, Star } from "lucide-react";

// Page accessed via /p/:slug — practitioner's direct booking link.
// Any client who books from here has client_source=direct_link → 0% commission forever.
export default function DirectBookingPage() {
  const { slug } = useParams();
  const nav = useNavigate();
  const [p, setP] = useState(null);
  const [err, setErr] = useState(false);

  useEffect(() => {
    api.get(`/practitioners/slug/${slug}`).then((r) => setP(r.data)).catch(() => setErr(true));
  }, [slug]);

  if (err) {
    return (
      <div className="py-20 text-center">
        <div className="font-serif text-3xl">We couldn't find that link.</div>
        <Link to="/browse" className="text-[#C8552F] mt-3 inline-block">Browse practitioners →</Link>
      </div>
    );
  }
  if (!p) return <div className="py-20 text-center text-[#6E5F50]">Loading…</div>;

  return (
    <div className="mx-auto max-w-3xl px-5 md:px-10 py-10">
      <div className="inline-flex items-center gap-2 rounded-full bg-[#EFE8DA] px-3 py-1 text-xs font-semibold tracking-[0.2em] uppercase text-[#3D1F2C]">
        <Sparkles size={12} /> Direct booking · 0% platform fee for {p.display_name.split("'")[0]}
      </div>
      <h1 className="font-serif text-4xl md:text-5xl mt-3">{p.display_name}</h1>
      <div className="text-sm text-[#6E5F50] mt-2 flex items-center gap-3">
        <span className="flex items-center gap-1"><MapPin size={14} /> {p.city}, {p.province}</span>
        <span className="flex items-center gap-1"><Star size={14} className="fill-[#E8A33D] text-[#E8A33D]" /> {p.avg_rating || "New"} ({p.total_reviews})</span>
      </div>
      <p className="mt-4 text-[#6E5F50]">{p.bio}</p>

      <div className="grid grid-cols-3 gap-2 mt-6">
        {p.portfolio.slice(0, 6).map((it) => (
          <div key={it.id} className="aspect-square rounded-xl overflow-hidden">
            <img src={it.image_url} alt="" className="w-full h-full object-cover" />
          </div>
        ))}
      </div>

      <h2 className="font-serif text-2xl mt-8 mb-3">Book a service</h2>
      <div className="space-y-2">
        {p.services.map((s) => (
          <button
            key={s.id}
            onClick={() => nav(`/book/${p.id}/${s.id}?source=direct_link`)}
            className="w-full text-left bg-white rounded-2xl border border-[#D9CFBE] hover:border-[#C8552F] p-4 flex items-center justify-between"
          >
            <div>
              <div className="text-xs text-[#C8552F] font-semibold uppercase tracking-widest">{s.category_name}</div>
              <div className="font-semibold">{s.name}</div>
              <div className="text-xs text-[#6E5F50]">{Math.round(s.duration_minutes_min / 60 * 10) / 10}h</div>
            </div>
            <div className="text-right">
              <div className="font-serif text-lg">${s.price_min}</div>
              <div className="text-xs text-[#6E5F50]">${(s.price_min * 0.25).toFixed(2)} deposit</div>
            </div>
          </button>
        ))}
      </div>
    </div>
  );
}
