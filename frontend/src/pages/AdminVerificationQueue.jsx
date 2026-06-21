import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api, formatApiError } from "@/lib/api";
import { ADMIN_VERIFY } from "@/constants/testIds";
import { CheckCircle2, XCircle, ArrowLeft, ExternalLink } from "lucide-react";
import { toast } from "sonner";

const BADGE_OPTIONS_BY_TYPE = {
  government_id: ["community_endorsed"],
  trade_certificate: ["certified_barber", "certified_hairstylist"],
  insurance: ["insured"],
  selfie: [],
  background_check: ["background_checked"],
};

export default function AdminVerificationQueue() {
  const [items, setItems] = useState([]);
  const [reasonFor, setReasonFor] = useState(null);
  const [reason, setReason] = useState("");
  const [pickedBadges, setPickedBadges] = useState({}); // id -> array

  const load = async () => {
    const r = await api.get("/admin/verifications");
    setItems(r.data);
  };
  useEffect(() => { load(); }, []);

  const approve = async (item) => {
    try {
      const badges = pickedBadges[item.id] || BADGE_OPTIONS_BY_TYPE[item.verification_type] || [];
      await api.put(`/admin/verifications/${item.id}`, { decision: "verified", grant_badges: badges });
      toast.success(`Approved · ${badges.length ? "granted: " + badges.join(", ") : "no badges granted"}`);
      await load();
    } catch (e) {
      toast.error(formatApiError(e.response?.data?.detail));
    }
  };

  const reject = async () => {
    try {
      await api.put(`/admin/verifications/${reasonFor.id}`, { decision: "rejected", rejection_reason: reason });
      toast.success("Rejected");
      setReasonFor(null);
      setReason("");
      await load();
    } catch (e) {
      toast.error(formatApiError(e.response?.data?.detail));
    }
  };

  return (
    <div className="mx-auto max-w-5xl px-5 md:px-10 py-10">
      <Link to="/dashboard/admin" className="inline-flex items-center gap-1 text-sm text-[#6E5F50] hover:text-[#C8552F] mb-4">
        <ArrowLeft size={14} /> Admin
      </Link>
      <h1 className="font-serif text-4xl md:text-5xl">Verification queue</h1>
      <p className="text-[#6E5F50] mt-1 mb-6">{items.length} pending</p>

      {items.length === 0 ? (
        <div className="bg-white rounded-2xl border border-[#D9CFBE] p-8 text-center text-[#6E5F50]">
          Inbox zero. Nice.
        </div>
      ) : (
        <div className="space-y-3">
          {items.map((it) => {
            const candidateBadges = BADGE_OPTIONS_BY_TYPE[it.verification_type] || [];
            const selected = pickedBadges[it.id] || candidateBadges;
            return (
              <div key={it.id} data-testid={ADMIN_VERIFY.queueItem} className="bg-white rounded-2xl border border-[#D9CFBE] p-5">
                <div className="flex items-start justify-between gap-4 flex-wrap">
                  <div>
                    <div className="text-xs uppercase tracking-widest text-[#C8552F] font-bold">{it.verification_type.replace("_", " ")}</div>
                    <div className="font-serif text-xl mt-1">{it.practitioner_name}</div>
                    <div className="text-sm text-[#6E5F50] capitalize">{it.practitioner_type?.replace("_", " ")} · {it.practitioner_email}</div>
                    <a href={it.document_url} target="_blank" rel="noreferrer" className="mt-2 inline-flex items-center gap-1 text-sm text-[#C8552F] hover:underline">
                      <ExternalLink size={12} /> View document
                    </a>
                    {candidateBadges.length > 0 && (
                      <div className="mt-3">
                        <div className="text-xs text-[#6E5F50] mb-1">Grant on approval:</div>
                        <div className="flex flex-wrap gap-1">
                          {candidateBadges.map((b) => (
                            <button
                              key={b}
                              onClick={() => {
                                const has = selected.includes(b);
                                const next = has ? selected.filter((x) => x !== b) : [...selected, b];
                                setPickedBadges({ ...pickedBadges, [it.id]: next });
                              }}
                              className={`chip text-[10px] ${selected.includes(b) ? "chip-active" : ""}`}
                            >
                              {b.replace("_", " ")}
                            </button>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                  <div className="flex gap-2">
                    <button
                      data-testid={ADMIN_VERIFY.approveButton}
                      onClick={() => approve(it)}
                      className="rounded-full bg-[#2D7D6F] hover:bg-[#236359] text-white font-semibold px-4 py-2 text-sm inline-flex items-center gap-1"
                    >
                      <CheckCircle2 size={14} /> Approve
                    </button>
                    <button
                      data-testid={ADMIN_VERIFY.rejectButton}
                      onClick={() => setReasonFor(it)}
                      className="rounded-full border border-[#D9CFBE] hover:border-red-500 hover:text-red-500 font-semibold px-4 py-2 text-sm inline-flex items-center gap-1"
                    >
                      <XCircle size={14} /> Reject
                    </button>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {reasonFor && (
        <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl max-w-md w-full p-6">
            <div className="font-serif text-2xl mb-2">Reject verification</div>
            <div className="text-sm text-[#6E5F50] mb-3">Tell the practitioner why so they can re-submit.</div>
            <textarea rows={4} value={reason} onChange={(e) => setReason(e.target.value)} className="w-full rounded-2xl border border-[#D9CFBE] p-3 bg-[#EFE8DA] outline-none" placeholder="e.g. ID photo is blurry — please re-upload" />
            <div className="flex gap-2 mt-4 justify-end">
              <button onClick={() => { setReasonFor(null); setReason(""); }} className="rounded-full border border-[#D9CFBE] px-4 py-2 text-sm">Cancel</button>
              <button onClick={reject} className="rounded-full bg-red-500 hover:bg-red-600 text-white px-4 py-2 text-sm font-semibold">Reject</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
