import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { api, formatApiError } from "@/lib/api";
import { toast } from "sonner";

const TYPES = [
  ["braider", "Braider"],
  ["loctician", "Loctician"],
  ["barber", "Barber"],
  ["nail_tech", "Nail Technician"],
  ["mua", "MUA / Bridal Makeup"],
  ["mehndi_artist", "Mehndi Artist"],
  ["threading_specialist", "Threading Specialist"],
  ["multi_service", "Multi-service"],
];
const LOCATION_TYPES = [
  ["home_studio", "Home studio"],
  ["mobile", "Mobile"],
  ["salon", "Salon"],
  ["shared_space", "Shared space"],
  ["mixed", "Mixed"],
];
const SERVICE_MODES = [
  ["clients_come_to_me", "Clients come to me"],
  ["i_travel_to_clients", "I travel to clients"],
  ["both", "Both"],
];
const PAYMENTS = ["card", "etransfer", "cash"];

export default function PractitionerOnboarding() {
  const nav = useNavigate();
  const [loaded, setLoaded] = useState(false);
  const [form, setForm] = useState({
    display_name: "",
    bio: "",
    profile_photo_url: "",
    practitioner_type: "braider",
    location_type: "home_studio",
    service_mode: "clients_come_to_me",
    address: "",
    city: "Calgary",
    province: "AB",
    service_neighbourhoods: [],
    service_radius_km: null,
    accepted_payments: ["card", "etransfer", "cash"],
    cancellation_policy: "48 hours notice required. Deposit forfeited otherwise.",
    cancellation_notice_hours: 48,
    instagram_handle: "",
    whatsapp_number: "",
    languages: ["en"],
  });
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    api.get("/me/practitioner").then((r) => {
      if (r.data.exists) {
        const p = r.data.practitioner;
        setForm({
          display_name: p.display_name || "",
          bio: p.bio || "",
          profile_photo_url: p.profile_photo_url || "",
          practitioner_type: p.practitioner_type || "braider",
          location_type: p.location_type || "home_studio",
          service_mode: p.service_mode || "clients_come_to_me",
          address: p.address || "",
          city: p.city || "Calgary",
          province: p.province || "AB",
          service_neighbourhoods: p.service_neighbourhoods || [],
          service_radius_km: p.service_radius_km,
          accepted_payments: p.accepted_payments || [],
          cancellation_policy: p.cancellation_policy || "",
          cancellation_notice_hours: p.cancellation_notice_hours || 48,
          instagram_handle: p.instagram_handle || "",
          whatsapp_number: p.whatsapp_number || "",
          languages: p.languages || ["en"],
        });
      }
      setLoaded(true);
    });
  }, []);

  const togglePay = (p) => {
    setForm((f) => ({
      ...f,
      accepted_payments: f.accepted_payments.includes(p)
        ? f.accepted_payments.filter((x) => x !== p)
        : [...f.accepted_payments, p],
    }));
  };

  const submit = async (e) => {
    e.preventDefault();
    setSaving(true);
    try {
      await api.post("/me/practitioner", form);
      toast.success("Profile saved!");
      nav("/dashboard/practitioner");
    } catch (e2) {
      toast.error(formatApiError(e2.response?.data?.detail));
    } finally {
      setSaving(false);
    }
  };

  if (!loaded) return <div className="py-20 text-center text-[#6E5F50]">Loading…</div>;

  return (
    <div className="mx-auto max-w-3xl px-5 md:px-10 py-10">
      <h1 className="font-serif text-4xl md:text-5xl">Set up your studio</h1>
      <p className="text-[#6E5F50] mt-2">Tell clients who you are, where you work, and what you offer.</p>

      <form onSubmit={submit} className="mt-8 bg-white rounded-2xl border border-[#D9CFBE] p-6 space-y-5">
        <Field label="Display name (e.g., Blessing's Braids YYC)">
          <input
            value={form.display_name}
            onChange={(e) => setForm({ ...form, display_name: e.target.value })}
            required
            data-testid="onb-display-name"
            className="w-full h-12 rounded-full border border-[#D9CFBE] px-5 bg-[#EFE8DA]"
          />
        </Field>
        <Field label="About you">
          <textarea
            rows={3}
            value={form.bio}
            onChange={(e) => setForm({ ...form, bio: e.target.value })}
            data-testid="onb-bio"
            className="w-full rounded-2xl border border-[#D9CFBE] p-4 bg-[#EFE8DA]"
          />
        </Field>
        <Field label="Profile photo URL (optional)">
          <input
            value={form.profile_photo_url}
            onChange={(e) => setForm({ ...form, profile_photo_url: e.target.value })}
            placeholder="https://..."
            className="w-full h-12 rounded-full border border-[#D9CFBE] px-5 bg-[#EFE8DA]"
          />
        </Field>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <Field label="Practitioner type">
            <select value={form.practitioner_type} onChange={(e) => setForm({ ...form, practitioner_type: e.target.value })} className="w-full h-12 rounded-full border border-[#D9CFBE] px-5 bg-[#EFE8DA]">
              {TYPES.map(([v, l]) => <option key={v} value={v}>{l}</option>)}
            </select>
          </Field>
          <Field label="Location type">
            <select value={form.location_type} onChange={(e) => setForm({ ...form, location_type: e.target.value })} className="w-full h-12 rounded-full border border-[#D9CFBE] px-5 bg-[#EFE8DA]">
              {LOCATION_TYPES.map(([v, l]) => <option key={v} value={v}>{l}</option>)}
            </select>
          </Field>
          <Field label="Service mode">
            <select value={form.service_mode} onChange={(e) => setForm({ ...form, service_mode: e.target.value })} className="w-full h-12 rounded-full border border-[#D9CFBE] px-5 bg-[#EFE8DA]">
              {SERVICE_MODES.map(([v, l]) => <option key={v} value={v}>{l}</option>)}
            </select>
          </Field>
          <Field label="City">
            <input value={form.city} onChange={(e) => setForm({ ...form, city: e.target.value })} className="w-full h-12 rounded-full border border-[#D9CFBE] px-5 bg-[#EFE8DA]" />
          </Field>
        </div>

        <Field label="Neighbourhoods served (comma-separated)">
          <input
            value={form.service_neighbourhoods.join(", ")}
            onChange={(e) => setForm({ ...form, service_neighbourhoods: e.target.value.split(",").map((s) => s.trim()).filter(Boolean) })}
            placeholder="NE Calgary, Saddle Ridge, Falconridge"
            className="w-full h-12 rounded-full border border-[#D9CFBE] px-5 bg-[#EFE8DA]"
          />
        </Field>

        {form.service_mode !== "clients_come_to_me" && (
          <Field label="Travel radius (km)">
            <input
              type="number"
              value={form.service_radius_km || ""}
              onChange={(e) => setForm({ ...form, service_radius_km: e.target.value ? parseInt(e.target.value) : null })}
              className="w-full h-12 rounded-full border border-[#D9CFBE] px-5 bg-[#EFE8DA]"
            />
          </Field>
        )}

        <Field label="Accepted payments">
          <div className="flex gap-2 flex-wrap">
            {PAYMENTS.map((p) => (
              <button type="button" key={p} onClick={() => togglePay(p)} className={`chip ${form.accepted_payments.includes(p) ? "chip-active" : ""}`}>
                {p === "card" ? "Card / Tap" : p === "etransfer" ? "E-transfer" : "Cash"}
              </button>
            ))}
          </div>
        </Field>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <Field label="Instagram handle">
            <input value={form.instagram_handle} onChange={(e) => setForm({ ...form, instagram_handle: e.target.value })} placeholder="@you" className="w-full h-12 rounded-full border border-[#D9CFBE] px-5 bg-[#EFE8DA]" />
          </Field>
          <Field label="WhatsApp number">
            <input value={form.whatsapp_number} onChange={(e) => setForm({ ...form, whatsapp_number: e.target.value })} placeholder="+1-403-555-0100" className="w-full h-12 rounded-full border border-[#D9CFBE] px-5 bg-[#EFE8DA]" />
          </Field>
        </div>

        <Field label="Cancellation policy">
          <textarea
            rows={2}
            value={form.cancellation_policy}
            onChange={(e) => setForm({ ...form, cancellation_policy: e.target.value })}
            className="w-full rounded-2xl border border-[#D9CFBE] p-4 bg-[#EFE8DA]"
          />
        </Field>

        <button type="submit" disabled={saving} className="w-full rounded-full bg-[#C8552F] hover:bg-[#A8451C] text-white font-semibold h-12">
          {saving ? "Saving…" : "Save profile"}
        </button>
      </form>
    </div>
  );
}

function Field({ label, children }) {
  return (
    <div>
      <label className="block text-xs font-semibold uppercase tracking-widest text-[#6E5F50] mb-1">{label}</label>
      {children}
    </div>
  );
}
