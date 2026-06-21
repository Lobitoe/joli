import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api, formatApiError } from "@/lib/api";
import { Plus, Trash2, ArrowLeft } from "lucide-react";
import { toast } from "sonner";

export default function PortfolioManager() {
  const [categories, setCategories] = useState([]);
  const [items, setItems] = useState([]);
  const [draft, setDraft] = useState({ category_id: "", image_url: "", caption: "", tags: "" });

  const load = async () => {
    const [c, p] = await Promise.all([api.get("/categories"), api.get("/me/portfolio")]);
    setCategories(c.data);
    setItems(p.data);
  };
  useEffect(() => { load(); }, []);

  const add = async () => {
    if (!draft.category_id || !draft.image_url) { toast.error("Pick a category and add an image URL"); return; }
    try {
      await api.post("/me/portfolio", {
        category_id: draft.category_id,
        image_url: draft.image_url,
        caption: draft.caption,
        tags: draft.tags.split(",").map((t) => t.trim()).filter(Boolean),
        is_featured: false,
      });
      toast.success("Added to portfolio");
      setDraft({ category_id: "", image_url: "", caption: "", tags: "" });
      await load();
    } catch (e) {
      toast.error(formatApiError(e.response?.data?.detail));
    }
  };

  const remove = async (id) => {
    if (!confirm("Remove this image?")) return;
    await api.delete(`/me/portfolio/${id}`);
    await load();
  };

  return (
    <div className="mx-auto max-w-5xl px-5 md:px-10 py-10">
      <Link to="/dashboard/practitioner" className="inline-flex items-center gap-1 text-sm text-[#6E5F50] hover:text-[#C8552F] mb-4"><ArrowLeft size={14} /> Back</Link>
      <h1 className="font-serif text-4xl">Portfolio</h1>
      <p className="text-[#6E5F50] mt-1 mb-6">Add photos of your actual work, organized by style category.</p>

      <div className="bg-white rounded-2xl border border-[#D9CFBE] p-5 mb-6 grid grid-cols-1 md:grid-cols-12 gap-3">
        <select value={draft.category_id} onChange={(e) => setDraft({ ...draft, category_id: e.target.value })} className="md:col-span-3 h-12 rounded-full border border-[#D9CFBE] px-5 bg-[#EFE8DA]">
          <option value="">Category</option>
          {categories.map((c) => <option key={c.id} value={c.id}>{c.name}</option>)}
        </select>
        <input value={draft.image_url} onChange={(e) => setDraft({ ...draft, image_url: e.target.value })} placeholder="Image URL" className="md:col-span-4 h-12 rounded-full border border-[#D9CFBE] px-5 bg-[#EFE8DA]" />
        <input value={draft.caption} onChange={(e) => setDraft({ ...draft, caption: e.target.value })} placeholder="Caption" className="md:col-span-2 h-12 rounded-full border border-[#D9CFBE] px-5 bg-[#EFE8DA]" />
        <input value={draft.tags} onChange={(e) => setDraft({ ...draft, tags: e.target.value })} placeholder="tags (comma)" className="md:col-span-2 h-12 rounded-full border border-[#D9CFBE] px-5 bg-[#EFE8DA]" />
        <button onClick={add} className="md:col-span-1 h-12 rounded-full bg-[#C8552F] hover:bg-[#A8451C] text-white inline-flex items-center justify-center gap-1"><Plus size={14} /></button>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        {items.map((it) => (
          <div key={it.id} className="relative aspect-[4/5] rounded-2xl overflow-hidden border border-[#D9CFBE] group">
            <img src={it.image_url} alt={it.caption} className="w-full h-full object-cover" />
            <div className="absolute top-2 left-2 chip bg-white/90 text-[10px]">{it.category_name}</div>
            <button onClick={() => remove(it.id)} className="absolute top-2 right-2 bg-white/90 hover:bg-red-500 hover:text-white p-2 rounded-full"><Trash2 size={14} /></button>
          </div>
        ))}
      </div>
    </div>
  );
}
