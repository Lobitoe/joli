import { useEffect, useState } from "react";
import { useSearchParams, Link } from "react-router-dom";
import { api } from "@/lib/api";
import { BROWSE } from "@/constants/testIds";
import { Star, MapPin, Sparkles, Filter } from "lucide-react";

const CITIES = ["", "Calgary", "Edmonton", "Toronto", "Ottawa", "Montreal"];
const MODES = [
  { v: "", label: "All" },
  { v: "clients_come_to_me", label: "I go to them" },
  { v: "i_travel_to_clients", label: "They travel to me" },
];
const TYPES = [
  { v: "", label: "All" },
  { v: "braider", label: "Braider" },
  { v: "loctician", label: "Loctician" },
  { v: "barber", label: "Barber" },
  { v: "nail_tech", label: "Nail Tech" },
  { v: "mua", label: "MUA" },
  { v: "mehndi_artist", label: "Mehndi" },
  { v: "threading_specialist", label: "Threading" },
];

export default function BrowsePage() {
  const [sp, setSp] = useSearchParams();
  const [categories, setCategories] = useState([]);
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const city = sp.get("city") || "";
  const category = sp.get("category") || "";
  const mode = sp.get("mode") || "";
  const type = sp.get("type") || "";

  useEffect(() => {
    api.get("/categories").then((r) => setCategories(r.data));
  }, []);

  useEffect(() => {
    setLoading(true);
    const params = {};
    if (city) params.city = city;
    if (category) params.category = category;
    if (mode) params.service_mode = mode;
    if (type) params.practitioner_type = type;
    api.get("/practitioners", { params }).then((r) => {
      setResults(r.data);
      setLoading(false);
    });
  }, [city, category, mode, type]);

  const update = (key, value) => {
    const next = new URLSearchParams(sp);
    if (value) next.set(key, value);
    else next.delete(key);
    setSp(next);
  };

  return (
    <div className="mx-auto max-w-7xl px-5 md:px-10 py-10">
      <div className="flex items-end justify-between mb-6">
        <div>
          <div className="overline text-xs tracking-[0.2em] uppercase font-bold text-[#984A23]">Discover</div>
          <h1 className="font-serif text-4xl md:text-5xl mt-1">Browse practitioners</h1>
          <p className="text-[#5C4E43] mt-2">
            {category ? <>For <span className="font-semibold">{category}</span></> : "All styles & services"}
            {city ? <> in <span className="font-semibold">{city}</span></> : null}
          </p>
        </div>
      </div>

      {/* Filters */}
      <div className="bg-white rounded-2xl border border-[#E2D9CF] p-4 mb-8">
        <div className="flex items-center gap-2 mb-3 text-xs uppercase tracking-widest text-[#5C4E43]">
          <Filter size={14} /> Filters
        </div>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-3">
          <div>
            <label className="block text-xs text-[#5C4E43] mb-1">City</label>
            <select
              data-testid={BROWSE.filterCity}
              value={city}
              onChange={(e) => update("city", e.target.value)}
              className="w-full h-11 rounded-full border border-[#E2D9CF] px-4 bg-[#F3EFEA] outline-none focus:ring-2 focus:ring-[#984A23]"
            >
              {CITIES.map((c) => (
                <option key={c} value={c}>{c || "All cities"}</option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-xs text-[#5C4E43] mb-1">Style / Category</label>
            <select
              data-testid={BROWSE.filterCategory}
              value={category}
              onChange={(e) => update("category", e.target.value)}
              className="w-full h-11 rounded-full border border-[#E2D9CF] px-4 bg-[#F3EFEA] outline-none focus:ring-2 focus:ring-[#984A23]"
            >
              <option value="">All styles</option>
              {categories.map((c) => (
                <option key={c.id} value={c.name}>{c.parent_category} → {c.name}</option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-xs text-[#5C4E43] mb-1">Service mode</label>
            <select
              data-testid={BROWSE.filterServiceMode}
              value={mode}
              onChange={(e) => update("mode", e.target.value)}
              className="w-full h-11 rounded-full border border-[#E2D9CF] px-4 bg-[#F3EFEA] outline-none focus:ring-2 focus:ring-[#984A23]"
            >
              {MODES.map((m) => (
                <option key={m.v} value={m.v}>{m.label}</option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-xs text-[#5C4E43] mb-1">Type</label>
            <select
              value={type}
              onChange={(e) => update("type", e.target.value)}
              className="w-full h-11 rounded-full border border-[#E2D9CF] px-4 bg-[#F3EFEA] outline-none focus:ring-2 focus:ring-[#984A23]"
            >
              {TYPES.map((t) => (
                <option key={t.v} value={t.v}>{t.label}</option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {loading ? (
        <div className="py-20 text-center text-[#5C4E43]">Loading practitioners…</div>
      ) : results.length === 0 ? (
        <div className="py-20 text-center" data-testid={BROWSE.emptyState}>
          <Sparkles className="mx-auto text-[#984A23]" />
          <div className="font-serif text-2xl mt-3">No practitioners match these filters.</div>
          <p className="text-[#5C4E43] mt-2">Try removing a filter, or pick a different style.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {results.map((p) => (
            <Link
              key={p.id}
              to={`/practitioner/${p.id}`}
              data-testid={BROWSE.practitionerCard}
              className="bg-white rounded-2xl overflow-hidden border border-[#E2D9CF] hover:shadow-lg transition-shadow fade-in"
            >
              <div className="relative aspect-[4/3] overflow-hidden">
                {p.portfolio_thumbs?.[0] ? (
                  <img src={p.portfolio_thumbs[0]} alt="" className="w-full h-full object-cover img-hover-scale" />
                ) : (
                  <div className="w-full h-full bg-[#EEDDCB]" />
                )}
                <div className="absolute top-3 left-3 flex gap-1.5">
                  {p.is_featured && <span className="chip chip-active">Featured</span>}
                  <span className="chip capitalize bg-white/90">{p.practitioner_type.replace("_", " ")}</span>
                </div>
              </div>
              <div className="p-5">
                <div className="flex items-center justify-between">
                  <div className="font-serif text-xl">{p.display_name}</div>
                  <div className="flex items-center gap-1 text-sm">
                    <Star size={14} className="fill-[#E1A100] text-[#E1A100]" />
                    <span className="font-medium">{p.avg_rating || "New"}</span>
                    {p.total_reviews ? <span className="text-[#5C4E43]">({p.total_reviews})</span> : null}
                  </div>
                </div>
                <div className="text-sm text-[#5C4E43] mt-1 flex items-center gap-1">
                  <MapPin size={12} /> {p.city}
                  {p.service_mode === "i_travel_to_clients" && <span className="chip ml-1">Mobile</span>}
                  {p.service_mode === "both" && <span className="chip ml-1">Mobile + Studio</span>}
                </div>
                <div className="text-xs text-[#5C4E43] mt-2 line-clamp-2">{p.bio}</div>
                <div className="mt-3 flex items-center justify-between text-sm">
                  <span className="text-[#984A23] font-semibold">From ${p.starting_price ?? "—"}</span>
                  <span className="text-[#5C4E43]">{p.service_count} services</span>
                </div>
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
