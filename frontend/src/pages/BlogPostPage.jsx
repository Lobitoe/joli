import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import DOMPurify from "dompurify";
import { api } from "@/lib/api";
import { BLOG } from "@/constants/testIds";
import { BadgeRow } from "@/components/BadgeChip";
import { ArrowLeft, Star, MapPin, ArrowRight, Calendar } from "lucide-react";

// Tiny safe markdown-ish renderer (h1/h2/h3, p, blockquote, lists, bold).
// All inline HTML is sanitized through DOMPurify to prevent XSS even though
// our content is admin-seeded today — defense in depth in case the blog
// surface ever takes user submissions.
const SAFE_HTML = { ALLOWED_TAGS: ["strong", "em", "br"], ALLOWED_ATTR: [] };
const safe = (s) => DOMPurify.sanitize(s, SAFE_HTML);

function renderMd(md) {
  const lines = md.split("\n");
  const out = [];
  let listBuf = [];
  const flushList = (anchor) => {
    if (listBuf.length) {
      out.push(
        <ul key={`ul-${anchor}`} className="list-disc pl-6 space-y-1 my-3 text-[#3D332B]">
          {listBuf.map((li, i) => (
            <li key={`${anchor}-li-${i}`} dangerouslySetInnerHTML={{ __html: safe(bold(li)) }} />
          ))}
        </ul>
      );
      listBuf = [];
    }
  };
  const bold = (s) => s.replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>");
  lines.forEach((raw, idx) => {
    const l = raw.trimEnd();
    const k = `md-${idx}`;
    if (/^# /.test(l)) { flushList(k); out.push(<h1 key={k} className="font-serif text-4xl md:text-5xl mt-10 mb-4">{l.replace(/^# /, "")}</h1>); }
    else if (/^## /.test(l)) { flushList(k); out.push(<h2 key={k} className="font-serif text-3xl mt-8 mb-3">{l.replace(/^## /, "")}</h2>); }
    else if (/^### /.test(l)) { flushList(k); out.push(<h3 key={k} className="font-serif text-2xl mt-6 mb-2">{l.replace(/^### /, "")}</h3>); }
    else if (/^> /.test(l)) { flushList(k); out.push(<blockquote key={k} className="border-l-4 border-[#C8552F] pl-4 my-4 italic text-[#6E5F50]">{l.replace(/^> /, "")}</blockquote>); }
    else if (/^- /.test(l)) { listBuf.push(l.replace(/^- /, "")); }
    else if (/^\d+\. /.test(l)) { listBuf.push(l.replace(/^\d+\. /, "")); }
    else if (l === "") { flushList(k); }
    else { flushList(k); out.push(<p key={k} className="leading-relaxed text-[#3D332B] my-3" dangerouslySetInnerHTML={{ __html: safe(bold(l)) }} />); }
  });
  flushList("end");
  return out;
}

export default function BlogPostPage() {
  const { slug } = useParams();
  const [post, setPost] = useState(null);
  const [err, setErr] = useState(false);

  useEffect(() => {
    api.get(`/blog/${slug}`).then((r) => setPost(r.data)).catch(() => setErr(true));
  }, [slug]);

  if (err) {
    return (
      <div className="py-20 text-center">
        <div className="font-serif text-3xl">Post not found.</div>
        <Link to="/blog" className="text-[#C8552F] mt-3 inline-block">← Back to Journal</Link>
      </div>
    );
  }
  if (!post) return <div className="py-20 text-center text-[#6E5F50]">Loading…</div>;

  return (
    <article className="mx-auto max-w-3xl px-5 md:px-10 py-10">
      <Link to="/blog" className="inline-flex items-center gap-1 text-sm text-[#6E5F50] hover:text-[#C8552F] mb-4">
        <ArrowLeft size={14} /> The Joli Journal
      </Link>
      <div className="text-xs uppercase tracking-[0.2em] font-bold text-[#C8552F]">
        {post.category}{post.city ? ` · ${post.city}` : ""}
      </div>
      <h1 className="font-serif text-4xl md:text-6xl mt-2 leading-[1.05]">{post.title}</h1>
      <div className="flex items-center gap-3 text-xs text-[#6E5F50] mt-3">
        <span>{post.author}</span>
        <span>·</span>
        <span className="inline-flex items-center gap-1"><Calendar size={11} /> {new Date(post.published_at).toLocaleDateString("en-CA", { year: "numeric", month: "long", day: "numeric" })}</span>
      </div>
      <div className="aspect-[16/9] rounded-3xl overflow-hidden mt-6">
        <img src={post.hero_image} alt={post.title} className="w-full h-full object-cover" />
      </div>

      <div data-testid={BLOG.postBody} className="mt-6 text-lg">
        {renderMd(post.body_markdown)}
      </div>

      {/* Embedded practitioners */}
      {post.embedded_practitioners?.length > 0 && (
        <div className="mt-10 border-t border-[#D9CFBE] pt-8">
          <div className="text-xs uppercase tracking-[0.2em] font-bold text-[#C8552F] mb-3">Book now from this story</div>
          <div className="space-y-4">
            {post.embedded_practitioners.map((p) => (
              <div key={p.id} data-testid={BLOG.embeddedPractitionerCard} className="bg-white rounded-2xl border border-[#D9CFBE] p-4 grid grid-cols-1 sm:grid-cols-5 gap-4 items-center">
                <div className="sm:col-span-1 aspect-square rounded-xl overflow-hidden">
                  <img src={p.profile_photo_url || p.portfolio_thumbs?.[0]} alt={p.display_name} className="w-full h-full object-cover" />
                </div>
                <div className="sm:col-span-3">
                  <div className="font-serif text-xl">{p.display_name}</div>
                  <div className="text-xs text-[#6E5F50] capitalize flex items-center gap-2 mt-1">
                    <span>{p.practitioner_type.replace("_", " ")}</span>
                    <MapPin size={12} /> {p.city}
                    <Star size={12} className="fill-[#E8A33D] text-[#E8A33D]" /> {p.avg_rating || "New"}
                  </div>
                  <div className="mt-2"><BadgeRow badges={p.badges} size="sm" /></div>
                  <div className="text-sm text-[#6E5F50] mt-2 line-clamp-2">{p.bio}</div>
                </div>
                <div className="sm:col-span-1 text-right">
                  <div className="font-serif text-lg">From ${p.starting_price}</div>
                  <Link
                    to={`/practitioner/${p.id}`}
                    data-testid={BLOG.embeddedBookButton}
                    className="mt-2 inline-flex items-center gap-1 rounded-full bg-[#C8552F] hover:bg-[#A8451C] text-white text-sm font-semibold px-4 py-2 transition-colors"
                  >
                    Book <ArrowRight size={12} />
                  </Link>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </article>
  );
}
