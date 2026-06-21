import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api, formatApiError } from "@/lib/api";
import { VERIFICATION } from "@/constants/testIds";
import { BadgeRow } from "@/components/BadgeChip";
import { ArrowLeft, Save, ShieldCheck, FileBadge, Scissors } from "lucide-react";
import { toast } from "sonner";

const SECTIONS = [
  { type: "government_id", title: "Government ID", subtitle: "Required to go live. Driver's licence, passport, PR card.", Icon: ShieldCheck },
  { type: "trade_certificate", title: "Trade Certificate", subtitle: "For barbers & hairstylists. Earns a 'Certified' badge.", Icon: Scissors },
  { type: "insurance", title: "Liability Insurance", subtitle: "Optional but recommended for mobile services. Earns 'Insured' badge.", Icon: FileBadge },
];

export default function VerificationPage() {
  const [data, setData] = useState({ verifications: [], badges: [], verification_status: "unverified" });
  const [drafts, setDrafts] = useState({});
  const [saving, setSaving] = useState(null);

  const load = async () => {
    const r = await api.get("/me/practitioner/verifications");
    setData(r.data);
  };
  useEffect(() => { load(); }, []);

  const findExisting = (type) => data.verifications.find((v) => v.verification_type === type);

  const submit = async (type) => {
    const url = drafts[type];
    if (!url) { toast.error("Paste a document URL or image link"); return; }
    setSaving(type);
    try {
      await api.post("/me/practitioner/verifications", { verification_type: type, document_url: url });
      toast.success("Submitted for review — we'll get back to you within 48 hours.");
      setDrafts({ ...drafts, [type]: "" });
      await load();
    } catch (e) {
      toast.error(formatApiError(e.response?.data?.detail));
    } finally {
      setSaving(null);
    }
  };

  return (
    <div className="mx-auto max-w-3xl px-5 md:px-10 py-10">
      <Link to="/dashboard/practitioner" className="inline-flex items-center gap-1 text-sm text-[#6E5F50] hover:text-[#C8552F] mb-4">
        <ArrowLeft size={14} /> Back to dashboard
      </Link>
      <h1 className="font-serif text-4xl md:text-5xl">Verification & badges</h1>
      <p className="text-[#6E5F50] mt-2">
        Verified practitioners earn badges that appear on every profile and booking. Clients trust them more — and so do search algorithms.
      </p>

      <div className="mt-6 bg-white rounded-2xl border border-[#D9CFBE] p-5">
        <div className="text-xs uppercase tracking-widest text-[#6E5F50]">Your current status</div>
        <div className="flex items-center justify-between mt-2">
          <div className="font-serif text-2xl capitalize">{data.verification_status}</div>
          <span
            data-testid={VERIFICATION.statusBadge}
            className={`chip ${data.verification_status === "verified" ? "chip-active" : ""}`}
          >
            {data.verification_status === "verified" ? "Approved" : data.verification_status === "pending" ? "Under review" : "Unverified"}
          </span>
        </div>
        {data.badges?.length > 0 && (
          <div className="mt-4">
            <div className="text-xs text-[#6E5F50] mb-2">Active badges</div>
            <BadgeRow badges={data.badges} size="lg" />
          </div>
        )}
      </div>

      <div className="mt-6 space-y-4">
        {SECTIONS.map((s) => {
          const existing = findExisting(s.type);
          return (
            <div key={s.type} className="bg-white rounded-2xl border border-[#D9CFBE] p-5">
              <div className="flex items-start gap-3">
                <div className="h-10 w-10 rounded-full bg-[#EFE8DA] inline-flex items-center justify-center text-[#3D1F2C]">
                  <s.Icon size={18} />
                </div>
                <div className="flex-1">
                  <div className="font-serif text-xl">{s.title}</div>
                  <div className="text-sm text-[#6E5F50]">{s.subtitle}</div>
                  {existing && (
                    <div className="mt-2 flex items-center gap-2 text-xs">
                      <span className={`chip ${existing.status === "verified" ? "chip-active" : ""}`}>{existing.status}</span>
                      {existing.rejection_reason && <span className="text-red-600">{existing.rejection_reason}</span>}
                    </div>
                  )}
                  <div className="mt-3 flex gap-2 flex-wrap">
                    <input
                      data-testid={s.type === "government_id" ? VERIFICATION.uploadIdInput : s.type === "trade_certificate" ? VERIFICATION.uploadCertInput : VERIFICATION.uploadInsuranceInput}
                      placeholder="Paste a document URL or image link"
                      value={drafts[s.type] || ""}
                      onChange={(e) => setDrafts({ ...drafts, [s.type]: e.target.value })}
                      className="flex-1 min-w-[200px] h-11 rounded-full border border-[#D9CFBE] px-4 bg-[#EFE8DA] outline-none focus:ring-2 focus:ring-[#C8552F]"
                    />
                    <button
                      onClick={() => submit(s.type)}
                      disabled={saving === s.type}
                      data-testid={VERIFICATION.submitButton}
                      className="rounded-full bg-[#C8552F] hover:bg-[#A8451C] disabled:opacity-50 text-white px-4 h-11 text-sm font-semibold inline-flex items-center gap-1"
                    >
                      <Save size={14} /> {saving === s.type ? "…" : existing ? "Resubmit" : "Submit"}
                    </button>
                  </div>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      <div className="mt-6 text-xs text-[#6E5F50] bg-[#EFE8DA] rounded-2xl p-4">
        <strong>Demo note:</strong> in production, this is a real file upload (Cloudinary / S3). For the MVP, paste any URL and an admin will approve from <code>/dashboard/admin/verifications</code>.
      </div>
    </div>
  );
}
