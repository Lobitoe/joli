import { useEffect, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { api } from "@/lib/api";
import { BLOG } from "@/constants/testIds";
import { Newspaper, MapPin, ArrowRight } from "lucide-react";

const CATEGORIES = ["All", "Local Discovery", "Style Guide", "Practitioner Education"];
const CITIES = ["All", "Calgary", "Edmonton"];

export default function BlogIndexPage() {
  const [sp, setSp] = useSearchParams();
  const [posts, setPosts] = useState([]);
  const [loading, setLoading] = useState(true);
  const category = sp.get("category") || "All";
  const city = sp.get("city") || "All";

  useEffect(() => {
    setLoading(true);
    const params = {};
    if (category !== "All") params.category = category;
    if (city !== "All") params.city = city;
    api.get("/blog", { params }).then((r) => {
      setPosts(r.data);
      setLoading(false);
    });
  }, [category, city]);

  const update = (k, v) => {
    const next = new URLSearchParams(sp);
    if (v && v !== "All") next.set(k, v);
    else next.delete(k);
    setSp(next);
  };

  const featured = posts[0];
  const rest = posts.slice(1);

  return (
    <div className="mx-auto max-w-7xl px-5 md:px-10 py-12">
      <div className="flex items-center gap-2 text-xs uppercase tracking-[0.2em] font-bold text-[#984A23]">
        <Newspaper size={14} /> The Joli Journal
      </div>
      <h1 className="font-serif text-5xl md:text-6xl mt-2">Stories, guides & local discovery</h1>
      <p className="text-[#5C4E43] mt-3 max-w-2xl">
        Honest reviews of the best braiders, barbers, nail techs and mehndi artists across Canada — plus style guides and business tips for practitioners.
      </p>

      {/* Filters */}
      <div className="mt-8 flex flex-wrap gap-2">
        {CATEGORIES.map((c) => (
          <button
            key={c}
            onClick={() => update("category", c)}
            className={`chip ${category === c ? "chip-active" : ""}`}
          >
            {c}
          </button>
        ))}
        <div className="w-px bg-[#E2D9CF] mx-1"></div>
        {CITIES.map((c) => (
          <button
            key={c}
            onClick={() => update("city", c)}
            className={`chip ${city === c ? "chip-active" : ""}`}
          >
            <MapPin size={11} /> {c}
          </button>
        ))}
      </div>

      {loading ? (
        <div className="py-20 text-center text-[#5C4E43]">Loading…</div>
      ) : posts.length === 0 ? (
        <div className="py-20 text-center text-[#5C4E43]">No posts match those filters yet.</div>
      ) : (
        <>
          {/* Featured */}
          {featured && (
            <Link
              to={`/blog/${featured.slug}`}
              data-testid={BLOG.postCard}
              className="block mt-10 group grid md:grid-cols-5 gap-8 items-center"
            >
              <div className="md:col-span-3 aspect-[16/10] rounded-3xl overflow-hidden">
                <img src={featured.hero_image} alt={featured.title} className="w-full h-full object-cover img-hover-scale" />
              </div>
              <div className="md:col-span-2">
                <div className="text-xs uppercase tracking-[0.2em] font-bold text-[#984A23]">
                  {featured.category}{featured.city ? ` · ${featured.city}` : ""}
                </div>
                <h2 className="font-serif text-3xl md:text-4xl mt-3 leading-tight group-hover:text-[#984A23] transition-colors">
                  {featured.title}
                </h2>
                <p className="text-[#5C4E43] mt-3">{featured.excerpt}</p>
                <div className="mt-4 inline-flex items-center gap-1 text-sm font-semibold text-[#984A23]">
                  Read story <ArrowRight size={14} />
                </div>
              </div>
            </Link>
          )}

          {/* Grid of rest */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mt-12">
            {rest.map((p) => (
              <Link
                key={p.id}
                to={`/blog/${p.slug}`}
                data-testid={BLOG.postCard}
                className="group block bg-white border border-[#E2D9CF] rounded-2xl overflow-hidden hover:shadow-lg transition-shadow"
              >
                <div className="aspect-[16/10] overflow-hidden">
                  <img src={p.hero_image} alt={p.title} className="w-full h-full object-cover img-hover-scale" />
                </div>
                <div className="p-5">
                  <div className="text-[10px] uppercase tracking-[0.2em] font-bold text-[#984A23]">
                    {p.category}{p.city ? ` · ${p.city}` : ""}
                  </div>
                  <div className="font-serif text-xl mt-2 leading-tight group-hover:text-[#984A23] transition-colors">{p.title}</div>
                  <p className="text-sm text-[#5C4E43] mt-2 line-clamp-3">{p.excerpt}</p>
                </div>
              </Link>
            ))}
          </div>
        </>
      )}
    </div>
  );
}
