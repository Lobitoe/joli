import { useEffect, useState } from "react";
import { useParams, Link, useNavigate } from "react-router-dom";
import { api } from "@/lib/api";
import { PROFILE } from "@/constants/testIds";
import { BadgeRow } from "@/components/BadgeChip";
import { Star, MapPin, Instagram, MessageCircle, CreditCard, Banknote, Smartphone, Heart, Share2, Clock, Languages, CheckCircle2 } from "lucide-react";
import { useAuth } from "@/contexts/AuthContext";
import { toast } from "sonner";

const PAYMENT_ICONS = {
  card: { Icon: CreditCard, label: "Card / Tap" },
  etransfer: { Icon: Smartphone, label: "E-transfer" },
  cash: { Icon: Banknote, label: "Cash" },
};

export default function PractitionerProfilePage() {
  const { id } = useParams();
  const { user } = useAuth();
  const [p, setP] = useState(null);
  const [activeCategory, setActiveCategory] = useState("all");
  const [favorite, setFavorite] = useState(false);
  const nav = useNavigate();

  useEffect(() => {
    api.get(`/practitioners/${id}`).then((r) => setP(r.data));
    if (user?.role === "client") {
      api.get("/me/favorites").then((r) => {
        setFavorite(!!r.data.find((x) => x.id === id));
      });
    }
  }, [id, user]);

  if (!p) {
    return <div className="py-20 text-center text-[#6E5F50]">Loading…</div>;
  }

  const portfolioCats = ["all", ...Array.from(new Set(p.portfolio.map((x) => x.category_name)))];
  const filteredPortfolio = activeCategory === "all" ? p.portfolio : p.portfolio.filter((x) => x.category_name === activeCategory);
  const servicesByCategory = p.services.reduce((acc, s) => {
    (acc[s.category_name] = acc[s.category_name] || []).push(s);
    return acc;
  }, {});

  const toggleFavorite = async () => {
    if (!user) { nav("/login"); return; }
    if (user.role !== "client") return;
    if (favorite) {
      await api.delete(`/me/favorites/${p.id}`);
      setFavorite(false);
      toast.success("Removed from favorites");
    } else {
      await api.post("/me/favorites", { practitioner_id: p.id });
      setFavorite(true);
      toast.success("Saved to favorites");
    }
  };

  const copyLink = () => {
    const link = `${window.location.origin}/p/${p.direct_booking_slug}`;
    navigator.clipboard.writeText(link);
    toast.success("Direct booking link copied");
  };

  return (
    <div className="mx-auto max-w-7xl px-5 md:px-10 py-10">
      {/* Header */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="md:col-span-1">
          <div className="aspect-square rounded-3xl overflow-hidden border border-[#D9CFBE]">
            <img src={p.profile_photo_url || p.portfolio[0]?.image_url} alt={p.display_name} className="w-full h-full object-cover" />
          </div>
        </div>
        <div className="md:col-span-2 flex flex-col justify-between">
          <div>
            <div className="flex items-center gap-2 text-xs uppercase tracking-widest text-[#C8552F] font-bold">
              <span>{p.practitioner_type.replace("_", " ")}</span>
              <span>·</span>
              <span>{p.location_type.replace("_", " ")}</span>
              {p.service_mode === "i_travel_to_clients" && <><span>·</span><span>Travels to clients</span></>}
              {p.service_mode === "both" && <><span>·</span><span>Studio + Mobile</span></>}
            </div>
            <h1 className="font-serif text-4xl md:text-5xl mt-2">{p.display_name}</h1>
            <div className="flex items-center gap-3 text-sm text-[#6E5F50] mt-2">
              <span className="flex items-center gap-1"><Star size={14} className="fill-[#E8A33D] text-[#E8A33D]" /> {p.avg_rating || "New"} ({p.total_reviews})</span>
              <span>·</span>
              <span className="flex items-center gap-1"><MapPin size={14} /> {p.city}, {p.province}</span>
              {p.languages?.length > 0 && (
                <>
                  <span>·</span>
                  <span className="flex items-center gap-1"><Languages size={14} /> {p.languages.join(", ").toUpperCase()}</span>
                </>
              )}
            </div>
            <p className="mt-4 text-[#6E5F50] leading-relaxed max-w-2xl">{p.bio}</p>

            {p.badges?.length > 0 && (
              <div className="mt-4"><BadgeRow badges={p.badges} size="lg" /></div>
            )}

            <div className="mt-4 flex flex-wrap items-center gap-3 text-sm">
              {p.instagram_handle && (
                <a href={`https://instagram.com/${p.instagram_handle.replace("@", "")}`} target="_blank" rel="noreferrer" className="flex items-center gap-1 hover:text-[#C8552F]">
                  <Instagram size={16} /> {p.instagram_handle}
                </a>
              )}
              {p.whatsapp_number && (
                <span className="flex items-center gap-1 text-[#6E5F50]"><MessageCircle size={16} /> {p.whatsapp_number}</span>
              )}
              {p.service_neighbourhoods?.length > 0 && (
                <span className="text-[#6E5F50]">Serves: {p.service_neighbourhoods.join(", ")}</span>
              )}
              {p.service_radius_km && (
                <span className="text-[#6E5F50]">Travels up to {p.service_radius_km} km</span>
              )}
            </div>

            <div className="mt-5 flex items-center gap-2 flex-wrap">
              {p.accepted_payments.map((pm) => {
                const meta = PAYMENT_ICONS[pm];
                if (!meta) return null;
                return (
                  <span key={pm} className="chip">
                    <meta.Icon size={12} /> {meta.label}
                  </span>
                );
              })}
            </div>
          </div>

          <div className="mt-6 flex gap-3 flex-wrap">
            <button
              onClick={toggleFavorite}
              data-testid={PROFILE.favoriteButton}
              className={`inline-flex items-center gap-2 rounded-full px-5 py-2.5 border ${favorite ? "bg-[#C8552F] text-white border-[#C8552F]" : "border-[#D9CFBE] hover:border-[#C8552F]"}`}
            >
              <Heart size={16} className={favorite ? "fill-white" : ""} /> {favorite ? "Saved" : "Save"}
            </button>
            <button
              onClick={copyLink}
              data-testid={PROFILE.shareDirectLink}
              className="inline-flex items-center gap-2 rounded-full px-5 py-2.5 border border-[#D9CFBE] hover:border-[#C8552F]"
            >
              <Share2 size={16} /> Share
            </button>
          </div>
        </div>
      </div>

      {/* Portfolio + Services + Reviews */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Portfolio (lg:col-span-2) */}
        <div className="lg:col-span-2">
          <div className="flex items-center justify-between mb-4">
            <h2 className="font-serif text-2xl">Portfolio</h2>
          </div>
          <div className="flex gap-2 flex-wrap mb-4 overflow-x-auto pb-2">
            {portfolioCats.map((c) => (
              <button
                key={c}
                onClick={() => setActiveCategory(c)}
                className={`chip whitespace-nowrap ${activeCategory === c ? "chip-active" : ""}`}
              >
                {c === "all" ? "All work" : c}
              </button>
            ))}
          </div>
          <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
            {filteredPortfolio.map((item) => (
              <div key={item.id} data-testid={PROFILE.portfolioImage} className="relative aspect-[4/5] rounded-2xl overflow-hidden border border-[#D9CFBE]">
                <img src={item.image_url} alt={item.caption} className="w-full h-full object-cover img-hover-scale" />
                <div className="absolute inset-x-0 bottom-0 p-2 bg-gradient-to-t from-black/60 to-transparent text-white text-xs">
                  {item.category_name}
                </div>
              </div>
            ))}
          </div>

          {/* Reviews */}
          <div className="mt-10">
            <h2 className="font-serif text-2xl mb-4">Reviews ({p.total_reviews || 0})</h2>
            {p.reviews.length === 0 ? (
              <div className="text-[#6E5F50] bg-[#EFE8DA] p-4 rounded-2xl">No reviews yet.</div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {p.reviews.map((r) => (
                  <div key={r.id} className="bg-white rounded-2xl border border-[#D9CFBE] p-4">
                    <div className="flex items-center justify-between">
                      <div className="font-semibold">{r.client_name}</div>
                      <div className="flex items-center gap-1 text-sm">
                        <Star size={14} className="fill-[#E8A33D] text-[#E8A33D]" /> {r.rating}
                      </div>
                    </div>
                    <p className="text-[#6E5F50] mt-2 text-sm leading-relaxed">{r.text}</p>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Services panel */}
        <div className="lg:col-span-1">
          <div className="sticky top-20 bg-white rounded-2xl border border-[#D9CFBE] p-5">
            <h2 className="font-serif text-2xl mb-3">Services</h2>
            <p className="text-xs text-[#6E5F50] mb-4">
              Cancellation: <span className="text-[#1F1A17]">{p.cancellation_policy}</span>
            </p>
            <div className="space-y-5 max-h-[600px] overflow-y-auto pr-1">
              {Object.entries(servicesByCategory).map(([cat, svcs]) => (
                <div key={cat}>
                  <div className="overline text-[10px] font-bold tracking-[0.2em] uppercase text-[#C8552F] mb-2">{cat}</div>
                  <div className="space-y-2">
                    {svcs.map((s) => (
                      <div key={s.id} data-testid={PROFILE.serviceItem} className="rounded-xl border border-[#D9CFBE] p-3 hover:border-[#C8552F] transition-colors">
                        <div className="flex items-start justify-between gap-2">
                          <div>
                            <div className="font-semibold">{s.name}</div>
                            <div className="text-xs text-[#6E5F50] flex items-center gap-2 mt-1">
                              <Clock size={12} /> {Math.round(s.duration_minutes_min / 60 * 10) / 10}h
                              {s.includes_break ? <span className="chip text-[10px]">incl. break</span> : null}
                            </div>
                          </div>
                          <div className="text-right">
                            <div className="font-serif text-lg">${s.price_min}{s.price_max && s.price_max !== s.price_min ? `–$${s.price_max}` : ""}</div>
                          </div>
                        </div>
                        <Link
                          to={`/book/${p.id}/${s.id}`}
                          data-testid={PROFILE.bookNowButton}
                          className="mt-3 inline-flex items-center justify-center w-full rounded-full bg-[#C8552F] hover:bg-[#A8451C] text-white text-sm font-semibold py-2 transition-colors"
                        >
                          Book — ${(s.price_min * 0.25).toFixed(2)} deposit
                        </Link>
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>
            <div className="mt-4 text-xs text-[#6E5F50] flex items-start gap-2">
              <CheckCircle2 size={14} className="text-[#2D7D6F] flex-shrink-0 mt-0.5" />
              <span>25% deposit confirms your slot. Remainder is settled with your practitioner via {p.accepted_payments.join(" / ")}.</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
