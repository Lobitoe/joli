import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api, formatApiError } from "@/lib/api";
import { Plus, Trash2, ArrowLeft, Save } from "lucide-react";
import { toast } from "sonner";

const blank = (cat) => ({
  category_id: cat?.id || "",
  name: "",
  description: "",
  price_min: 50,
  price_max: null,
  duration_minutes_min: 60,
  duration_minutes_max: null,
  reference_photo_url: "",
  includes_break: false,
  break_duration_minutes: null,
});

export default function ServicesManager() {
  const [categories, setCategories] = useState([]);
  const [services, setServices] = useState([]);
  const [showNew, setShowNew] = useState(false);
  const [draft, setDraft] = useState(null);

  const load = async () => {
    const [c, s] = await Promise.all([api.get("/categories"), api.get("/me/services")]);
    setCategories(c.data);
    setServices(s.data);
    if (!draft) setDraft(blank(c.data[0]));
  };
  useEffect(() => { load(); }, []);

  const create = async () => {
    if (!draft.category_id || !draft.name) { toast.error("Pick a category and name your service"); return; }
    try {
      await api.post("/me/services", { ...draft, price_min: Number(draft.price_min), price_max: draft.price_max ? Number(draft.price_max) : null, duration_minutes_min: Number(draft.duration_minutes_min), duration_minutes_max: draft.duration_minutes_max ? Number(draft.duration_minutes_max) : null });
      toast.success("Service added");
      setShowNew(false);
      setDraft(blank(categories[0]));
      await load();
    } catch (e) {
      toast.error(formatApiError(e.response?.data?.detail));
    }
  };

  const remove = async (id) => {
    if (!confirm("Delete this service?")) return;
    await api.delete(`/me/services/${id}`);
    await load();
  };

  return (
    <div className="mx-auto max-w-4xl px-5 md:px-10 py-10">
      <Link to="/dashboard/practitioner" className="inline-flex items-center gap-1 text-sm text-[#6E5F50] hover:text-[#C8552F] mb-4">
        <ArrowLeft size={14} /> Back to dashboard
      </Link>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="font-serif text-4xl">Services & pricing</h1>
          <p className="text-[#6E5F50]">Style-specific menu items that clients book.</p>
        </div>
        <button onClick={() => setShowNew(true)} className="rounded-full bg-[#C8552F] hover:bg-[#A8451C] text-white px-4 py-2 inline-flex items-center gap-1 text-sm font-semibold">
          <Plus size={14} /> Add service
        </button>
      </div>

      <div className="space-y-3">
        {services.length === 0 && <div className="bg-white rounded-2xl border border-[#D9CFBE] p-6 text-[#6E5F50]">No services yet.</div>}
        {services.map((s) => (
          <div key={s.id} className="bg-white rounded-2xl border border-[#D9CFBE] p-4 flex items-center justify-between">
            <div>
              <div className="text-xs text-[#C8552F] font-semibold uppercase tracking-widest">{s.category_name}</div>
              <div className="font-semibold">{s.name}</div>
              <div className="text-sm text-[#6E5F50]">${s.price_min}{s.price_max && s.price_max !== s.price_min ? `–$${s.price_max}` : ""} · {Math.round(s.duration_minutes_min / 60 * 10) / 10}h</div>
            </div>
            <button onClick={() => remove(s.id)} className="text-red-500 hover:bg-red-50 p-2 rounded-full"><Trash2 size={16} /></button>
          </div>
        ))}
      </div>

      {showNew && draft && (
        <div className="fixed inset-0 bg-black/50 z-50 flex items-end md:items-center justify-center p-4">
          <div className="bg-white rounded-2xl max-w-lg w-full p-6 space-y-3">
            <div className="font-serif text-2xl">New service</div>
            <select value={draft.category_id} onChange={(e) => setDraft({ ...draft, category_id: e.target.value })} className="w-full h-12 rounded-full border border-[#D9CFBE] px-5 bg-[#EFE8DA]">
              <option value="">Select category</option>
              {categories.map((c) => <option key={c.id} value={c.id}>{c.parent_category} → {c.name}</option>)}
            </select>
            <input placeholder="Service name (e.g., Knotless Braids — Hip Length)" value={draft.name} onChange={(e) => setDraft({ ...draft, name: e.target.value })} className="w-full h-12 rounded-full border border-[#D9CFBE] px-5 bg-[#EFE8DA]" />
            <div className="grid grid-cols-2 gap-2">
              <input type="number" placeholder="Price min" value={draft.price_min} onChange={(e) => setDraft({ ...draft, price_min: e.target.value })} className="h-12 rounded-full border border-[#D9CFBE] px-5 bg-[#EFE8DA]" />
              <input type="number" placeholder="Price max (opt.)" value={draft.price_max || ""} onChange={(e) => setDraft({ ...draft, price_max: e.target.value })} className="h-12 rounded-full border border-[#D9CFBE] px-5 bg-[#EFE8DA]" />
              <input type="number" placeholder="Duration min (minutes)" value={draft.duration_minutes_min} onChange={(e) => setDraft({ ...draft, duration_minutes_min: e.target.value })} className="h-12 rounded-full border border-[#D9CFBE] px-5 bg-[#EFE8DA]" />
              <input type="number" placeholder="Duration max (opt.)" value={draft.duration_minutes_max || ""} onChange={(e) => setDraft({ ...draft, duration_minutes_max: e.target.value })} className="h-12 rounded-full border border-[#D9CFBE] px-5 bg-[#EFE8DA]" />
            </div>
            <input placeholder="Reference photo URL (optional)" value={draft.reference_photo_url} onChange={(e) => setDraft({ ...draft, reference_photo_url: e.target.value })} className="w-full h-12 rounded-full border border-[#D9CFBE] px-5 bg-[#EFE8DA]" />
            <div className="flex gap-2 justify-end">
              <button onClick={() => setShowNew(false)} className="rounded-full border border-[#D9CFBE] px-4 py-2 text-sm">Cancel</button>
              <button onClick={create} className="rounded-full bg-[#C8552F] hover:bg-[#A8451C] text-white px-4 py-2 text-sm font-semibold inline-flex items-center gap-1"><Save size={14} /> Save</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
