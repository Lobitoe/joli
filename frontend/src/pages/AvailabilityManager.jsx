import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api, formatApiError } from "@/lib/api";
import { ArrowLeft, Save } from "lucide-react";
import { toast } from "sonner";

const DAYS = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];

export default function AvailabilityManager() {
  const [rows, setRows] = useState(
    [0, 1, 2, 3, 4, 5, 6].map((d) => ({ day_of_week: d, start_time: "09:00", end_time: "19:00", is_available: d !== 0 }))
  );
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    api.get("/me/availability").then((r) => {
      if (r.data.length === 0) return;
      const byDay = Object.fromEntries(r.data.map((x) => [x.day_of_week, x]));
      setRows(
        [0, 1, 2, 3, 4, 5, 6].map((d) =>
          byDay[d] ? { day_of_week: d, start_time: byDay[d].start_time, end_time: byDay[d].end_time, is_available: byDay[d].is_available } : { day_of_week: d, start_time: "09:00", end_time: "19:00", is_available: false }
        )
      );
    });
  }, []);

  const save = async () => {
    setSaving(true);
    try {
      await api.put("/me/availability", rows.filter((r) => r.is_available));
      toast.success("Availability saved");
    } catch (e) {
      toast.error(formatApiError(e.response?.data?.detail));
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="mx-auto max-w-3xl px-5 md:px-10 py-10">
      <Link to="/dashboard/practitioner" className="inline-flex items-center gap-1 text-sm text-[#6E5F50] hover:text-[#C8552F] mb-4"><ArrowLeft size={14} /> Back</Link>
      <h1 className="font-serif text-4xl">Weekly availability</h1>
      <p className="text-[#6E5F50] mt-1 mb-6">Slots calculated from these blocks.</p>

      <div className="bg-white rounded-2xl border border-[#D9CFBE] p-5 space-y-2">
        {rows.map((r, i) => (
          <div key={r.day_of_week} className="grid grid-cols-12 gap-2 items-center">
            <div className="col-span-3 font-semibold">{DAYS[r.day_of_week]}</div>
            <label className="col-span-2 text-sm flex items-center gap-2">
              <input type="checkbox" checked={r.is_available} onChange={(e) => setRows(rows.map((x, idx) => idx === i ? { ...x, is_available: e.target.checked } : x))} />
              Open
            </label>
            <input type="time" value={r.start_time} onChange={(e) => setRows(rows.map((x, idx) => idx === i ? { ...x, start_time: e.target.value } : x))} disabled={!r.is_available} className="col-span-3 h-11 rounded-full border border-[#D9CFBE] px-4 bg-[#EFE8DA] disabled:opacity-50" />
            <span className="col-span-1 text-center">–</span>
            <input type="time" value={r.end_time} onChange={(e) => setRows(rows.map((x, idx) => idx === i ? { ...x, end_time: e.target.value } : x))} disabled={!r.is_available} className="col-span-3 h-11 rounded-full border border-[#D9CFBE] px-4 bg-[#EFE8DA] disabled:opacity-50" />
          </div>
        ))}
      </div>

      <button onClick={save} disabled={saving} className="mt-6 rounded-full bg-[#C8552F] hover:bg-[#A8451C] text-white px-6 py-3 font-semibold inline-flex items-center gap-2"><Save size={14} /> {saving ? "Saving…" : "Save"}</button>
    </div>
  );
}
