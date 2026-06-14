import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { api } from "@/lib/api";
import { HOME } from "@/constants/testIds";
import { Search, MapPin, Star, ArrowRight, Sparkles, Shield, Heart, Calendar } from "lucide-react";

const CATEGORY_CARDS = [
  {
    name: "African & Caribbean Hair",
    query: "Knotless Braids",
    img: "https://images.unsplash.com/photo-1572955304332-bf714bd49add?crop=entropy&cs=srgb&fm=jpg&q=85&w=900",
    sub: "Braids · Locs · Natural Hair · Weaves",
  },
  {
    name: "Barber & Men's Grooming",
    query: "Skin Fade",
    img: "https://images.unsplash.com/photo-1567894340315-735d7c361db0?crop=entropy&cs=srgb&fm=jpg&q=85&w=900",
    sub: "Skin Fades · Designs · Waves · Beards",
  },
  {
    name: "Nail Studio",
    query: "Gel Manicure",
    img: "https://images.unsplash.com/photo-1688583417770-ff6cc18071dc?crop=entropy&cs=srgb&fm=jpg&q=85&w=900",
    sub: "Gel · Acrylic · Dip · 3D Nail Art",
  },
  {
    name: "South Asian Beauty",
    query: "Bridal Mehndi",
    img: "https://images.unsplash.com/photo-1623217509141-6f735087b50c?crop=entropy&cs=srgb&fm=jpg&q=85&w=900",
    sub: "Mehndi · Threading · Bridal MUA",
  },
];

const CITIES = ["Calgary", "Edmonton", "Toronto", "Ottawa", "Montreal"];

export default function LandingPage() {
  const [style, setStyle] = useState("");
  const [city, setCity] = useState("Calgary");
  const [featured, setFeatured] = useState([]);
  const nav = useNavigate();

  useEffect(() => {
    api.get("/practitioners").then((r) => setFeatured(r.data.slice(0, 6))).catch(() => {});
  }, []);

  const submit = (e) => {
    e?.preventDefault();
    const params = new URLSearchParams();
    if (style) params.set("category", style);
    if (city) params.set("city", city);
    nav(`/browse?${params.toString()}`);
  };

  return (
    <div data-testid={HOME.heroSection}>
      {/* HERO */}
      <section className="relative overflow-hidden">
        <div className="mx-auto max-w-7xl px-5 md:px-10 pt-14 pb-20 grid grid-cols-1 md:grid-cols-12 gap-10 items-center">
          <div className="md:col-span-7 fade-in">
            <div className="inline-flex items-center gap-2 rounded-full bg-[#EEDDCB] px-3 py-1 text-xs font-semibold tracking-[0.2em] uppercase text-[#4A2B12]">
              <Sparkles size={12} /> Calgary · Edmonton · Built for the diaspora
            </div>
            <h1 className="font-serif text-5xl md:text-7xl tracking-tight leading-[1.05] mt-5">
              Beauty that knows <span className="italic text-[#984A23]">your texture,</span> your tradition, your time.
            </h1>
            <p className="mt-5 text-lg text-[#5C4E43] max-w-xl leading-relaxed">
              Curlnect connects you with mobile and independent braiders, locticians, barbers,
              nail techs, mehndi artists and bridal MUAs — replacing Instagram DMs with real
              portfolios, real pricing and deposit-protected bookings.
            </p>

            <form
              onSubmit={submit}
              className="mt-8 bg-white border border-[#E2D9CF] shadow-sm rounded-2xl p-3 grid grid-cols-1 md:grid-cols-12 gap-2"
            >
              <div className="md:col-span-6 flex items-center gap-2 px-3 border-r-0 md:border-r border-[#E2D9CF]">
                <Search className="text-[#984A23]" size={18} />
                <input
                  data-testid={HOME.heroSearchStyle}
                  value={style}
                  onChange={(e) => setStyle(e.target.value)}
                  placeholder="Style (e.g., Knotless Braids, Skin Fade, Bridal Mehndi)"
                  className="w-full bg-transparent outline-none h-12 placeholder:text-[#A89C91] text-[#2B231D]"
                />
              </div>
              <div className="md:col-span-4 flex items-center gap-2 px-3">
                <MapPin className="text-[#984A23]" size={18} />
                <select
                  data-testid={HOME.heroSearchCity}
                  value={city}
                  onChange={(e) => setCity(e.target.value)}
                  className="w-full bg-transparent outline-none h-12 text-[#2B231D]"
                >
                  {CITIES.map((c) => (
                    <option key={c} value={c}>{c}</option>
                  ))}
                </select>
              </div>
              <button
                data-testid={HOME.heroSearchSubmit}
                type="submit"
                className="md:col-span-2 rounded-full bg-[#984A23] text-white font-semibold h-12 hover:bg-[#7e3d1d] transition-colors"
              >
                Find
              </button>
            </form>

            <div className="mt-6 flex flex-wrap gap-2 text-xs text-[#5C4E43]">
              <span className="chip">Knotless Braids</span>
              <span className="chip">Skin Fade</span>
              <span className="chip">Gel Manicure</span>
              <span className="chip">Bridal Mehndi</span>
              <span className="chip">Eyebrow Threading</span>
              <span className="chip">Loc Retwist</span>
            </div>
          </div>

          <div className="md:col-span-5 relative">
            <div className="relative aspect-[4/5] rounded-3xl overflow-hidden shadow-xl">
              <img
                src="https://images.unsplash.com/photo-1593351799227-75df2026356b?crop=entropy&cs=srgb&fm=jpg&q=85&w=900"
                alt="Multicultural beauty"
                className="w-full h-full object-cover"
              />
              <div className="absolute inset-0 bg-gradient-to-t from-black/40 via-transparent to-transparent" />
              <div className="absolute bottom-4 left-4 right-4 flex items-center justify-between text-white">
                <div>
                  <div className="text-xs uppercase tracking-widest opacity-90">Featured</div>
                  <div className="font-serif text-xl">Diaspora-led, community-rooted</div>
                </div>
              </div>
            </div>

            <div className="absolute -bottom-6 -left-6 hidden md:block bg-white rounded-2xl p-4 shadow-lg border border-[#E2D9CF] w-56">
              <div className="text-xs uppercase tracking-widest text-[#5C4E43]">No-show shield</div>
              <div className="text-2xl font-serif mt-1">25% deposit</div>
              <div className="text-xs text-[#5C4E43] mt-1">
                Locks your appointment. Your braider's 6-hour day is protected.
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* CATEGORIES */}
      <section className="mx-auto max-w-7xl px-5 md:px-10 pb-16">
        <div className="flex items-end justify-between mb-8">
          <div>
            <div className="overline text-xs tracking-[0.2em] uppercase font-bold text-[#984A23]">Browse by tradition</div>
            <h2 className="font-serif text-3xl md:text-4xl mt-1">Find your people</h2>
          </div>
          <Link to="/browse" className="hidden md:inline-flex items-center gap-1 text-sm text-[#984A23] hover:underline">
            See everything <ArrowRight size={14} />
          </Link>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-5">
          {CATEGORY_CARDS.map((c) => (
            <Link
              key={c.name}
              to={`/browse?category=${encodeURIComponent(c.query)}`}
              data-testid={HOME.categoryCard}
              className="group relative aspect-[4/5] rounded-2xl overflow-hidden block"
            >
              <img src={c.img} alt={c.name} className="absolute inset-0 w-full h-full object-cover img-hover-scale" />
              <div className="absolute inset-0 bg-gradient-to-t from-black/75 via-black/20 to-transparent" />
              <div className="absolute bottom-0 p-5 text-white">
                <div className="font-serif text-2xl leading-tight">{c.name}</div>
                <div className="text-xs opacity-90 mt-1">{c.sub}</div>
                <div className="mt-3 inline-flex items-center gap-1 text-xs uppercase tracking-widest opacity-80 group-hover:opacity-100">
                  Explore <ArrowRight size={12} />
                </div>
              </div>
            </Link>
          ))}
        </div>
      </section>

      {/* FEATURED PRACTITIONERS */}
      <section className="bg-[#F3EFEA]">
        <div className="mx-auto max-w-7xl px-5 md:px-10 py-16">
          <div className="mb-8">
            <div className="overline text-xs tracking-[0.2em] uppercase font-bold text-[#984A23]">Featured</div>
            <h2 className="font-serif text-3xl md:text-4xl mt-1">Practitioners shaping the scene</h2>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
            {featured.map((p) => (
              <Link
                key={p.id}
                to={`/practitioner/${p.id}`}
                data-testid={HOME.featuredPractitionerCard}
                className="bg-white rounded-2xl overflow-hidden border border-[#E2D9CF] hover:shadow-lg transition-shadow"
              >
                <div className="grid grid-cols-2 gap-0.5">
                  {(p.portfolio_thumbs || []).slice(0, 4).map((src, i) => (
                    <div key={i} className="aspect-square overflow-hidden">
                      <img src={src} alt="" className="w-full h-full object-cover img-hover-scale" />
                    </div>
                  ))}
                </div>
                <div className="p-5">
                  <div className="flex items-center justify-between">
                    <div className="font-serif text-xl">{p.display_name}</div>
                    <div className="flex items-center gap-1 text-sm">
                      <Star size={14} className="fill-[#E1A100] text-[#E1A100]" />
                      <span>{p.avg_rating || "New"}</span>
                    </div>
                  </div>
                  <div className="text-sm text-[#5C4E43] mt-1 capitalize">{p.practitioner_type.replace("_", " ")} · {p.city}</div>
                  <div className="text-xs text-[#5C4E43] mt-2 line-clamp-2">{p.bio}</div>
                  <div className="mt-3 flex items-center justify-between text-sm">
                    <span className="text-[#984A23] font-semibold">From ${p.starting_price ?? "—"}</span>
                    <span className="text-[#5C4E43]">{p.service_count} services</span>
                  </div>
                </div>
              </Link>
            ))}
          </div>
        </div>
      </section>

      {/* VALUE PROPS */}
      <section className="mx-auto max-w-7xl px-5 md:px-10 py-16 grid grid-cols-1 md:grid-cols-3 gap-6">
        {[
          { icon: <Shield size={20} />, title: "Deposit-protected bookings", body: "A 25% deposit locks your slot — practitioners stop losing 6-hour days, clients show up with confidence." },
          { icon: <Heart size={20} />, title: "Built for diasporic beauty", body: "Knotless braids that run 6 hours. Mehndi priced by complexity. Mobile barbers with route plans. Fresha can't do this." },
          { icon: <Calendar size={20} />, title: "Your own clients, 0% commission", body: "Practitioners get a direct booking link. Anyone who books through it pays you full price, forever." },
        ].map((v, i) => (
          <div key={i} className="bg-white border border-[#E2D9CF] rounded-2xl p-6">
            <div className="inline-flex h-10 w-10 items-center justify-center rounded-full bg-[#EEDDCB] text-[#4A2B12]">
              {v.icon}
            </div>
            <div className="font-serif text-xl mt-4">{v.title}</div>
            <div className="text-sm text-[#5C4E43] mt-2 leading-relaxed">{v.body}</div>
          </div>
        ))}
      </section>

      {/* CTA */}
      <section className="mx-auto max-w-7xl px-5 md:px-10 pb-20">
        <div className="rounded-3xl bg-[#2B231D] text-white p-8 md:p-12 grid md:grid-cols-2 gap-8 items-center">
          <div>
            <div className="overline text-xs tracking-[0.2em] uppercase font-bold text-[#C57245]">For practitioners</div>
            <h3 className="font-serif text-3xl md:text-4xl mt-2">Stop running your business out of Instagram DMs.</h3>
            <p className="mt-3 text-[#D9CFC6] leading-relaxed">
              Join Curlnect free. Get a beautiful style-specific portfolio, structured booking with deposits,
              a direct booking link that costs you 0%, and SMS/WhatsApp reminders that bring people to the door.
            </p>
          </div>
          <div className="flex flex-col sm:flex-row gap-3">
            <Link
              to="/register"
              className="inline-flex items-center justify-center rounded-full bg-[#C57245] hover:bg-[#a35a32] px-6 py-3 font-semibold transition-colors"
            >
              Become a practitioner
            </Link>
            <Link
              to="/browse"
              className="inline-flex items-center justify-center rounded-full border border-[#D9CFC6]/30 hover:border-white px-6 py-3 font-semibold transition-colors"
            >
              I'm here to book
            </Link>
          </div>
        </div>
      </section>
    </div>
  );
}
