import { useEffect, useMemo, useState } from "react";
import { useParams, useNavigate, useLocation } from "react-router-dom";
import { api, formatApiError } from "@/lib/api";
import { BOOKING } from "@/constants/testIds";
import { useAuth } from "@/contexts/AuthContext";
import { Calendar, Clock, MapPin, CheckCircle2, ArrowLeft, CreditCard } from "lucide-react";
import { toast } from "sonner";

const MS_PER_DAY = 86400000;

function fmtDate(d) {
  return d.toISOString().slice(0, 10);
}

export default function BookingPage() {
  const { practitionerId, serviceId } = useParams();
  const { user } = useAuth();
  const nav = useNavigate();
  const location = useLocation();
  const directLink = new URLSearchParams(location.search).get("source") === "direct_link";

  const [practitioner, setPractitioner] = useState(null);
  const [service, setService] = useState(null);
  const [date, setDate] = useState(fmtDate(new Date(Date.now() + MS_PER_DAY)));
  const [slots, setSlots] = useState([]);
  const [slot, setSlot] = useState(null);
  const [serviceLocation, setServiceLocation] = useState("practitioner_location");
  const [clientAddress, setClientAddress] = useState("");
  const [notes, setNotes] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [confirmation, setConfirmation] = useState(null);

  useEffect(() => {
    api.get(`/practitioners/${practitionerId}`).then((r) => {
      setPractitioner(r.data);
      const s = r.data.services.find((x) => x.id === serviceId);
      setService(s);
      if (r.data.service_mode === "i_travel_to_clients") setServiceLocation("client_location");
    });
  }, [practitionerId, serviceId]);

  useEffect(() => {
    if (!practitioner || !service) return;
    api.get(`/practitioners/${practitionerId}/slots`, { params: { date, service_id: serviceId } })
      .then((r) => {
        setSlots(r.data.slots);
        setSlot(null);
      });
  }, [date, practitioner, service, practitionerId, serviceId]);

  const deposit = service ? +(service.price_min * 0.25).toFixed(2) : 0;
  const remaining = service ? +(service.price_min - deposit).toFixed(2) : 0;

  const submit = async () => {
    if (!slot) { toast.error("Pick a time slot"); return; }
    if (serviceLocation === "client_location" && !clientAddress) {
      toast.error("Add your address for mobile booking");
      return;
    }
    setSubmitting(true);
    try {
      const { data } = await api.post("/bookings", {
        practitioner_id: practitionerId,
        service_id: serviceId,
        booking_date: date,
        start_time: slot,
        service_location: serviceLocation,
        client_address: clientAddress || null,
        client_notes: notes || null,
        client_source: directLink ? "direct_link" : "marketplace",
      });
      setConfirmation(data);
    } catch (e) {
      toast.error(formatApiError(e.response?.data?.detail) || "Booking failed");
    } finally {
      setSubmitting(false);
    }
  };

  if (!practitioner || !service) {
    return <div className="py-20 text-center text-[#6E5F50]">Loading…</div>;
  }

  if (confirmation) {
    return (
      <div className="mx-auto max-w-2xl px-5 md:px-10 py-16">
        <div className="bg-white rounded-3xl border border-[#D9CFBE] p-8 text-center fade-in" data-testid={BOOKING.confirmationStatus}>
          <div className="inline-flex h-16 w-16 items-center justify-center rounded-full bg-[#2D7D6F] text-white mb-4">
            <CheckCircle2 size={32} />
          </div>
          <h1 className="font-serif text-4xl">Booking confirmed</h1>
          <p className="text-[#6E5F50] mt-2">
            We've notified <span className="font-semibold">{practitioner.display_name}</span> via SMS + WhatsApp (mocked).
          </p>
          <div className="mt-6 bg-[#EFE8DA] rounded-2xl p-5 text-left text-sm space-y-2">
            <div><span className="text-[#6E5F50]">Service:</span> <span className="font-semibold">{service.name}</span></div>
            <div><span className="text-[#6E5F50]">When:</span> <span className="font-semibold">{confirmation.booking_date} at {confirmation.start_time} – {confirmation.end_time}</span></div>
            <div><span className="text-[#6E5F50]">Deposit paid:</span> <span className="font-semibold">${confirmation.deposit_amount}</span></div>
            <div><span className="text-[#6E5F50]">Remaining (at appointment):</span> <span className="font-semibold">${(confirmation.quoted_price - confirmation.deposit_amount).toFixed(2)}</span></div>
            <div><span className="text-[#6E5F50]">Pay with:</span> <span className="font-semibold">{practitioner.accepted_payments.join(" / ")}</span></div>
          </div>
          <div className="mt-6 flex gap-3 justify-center">
            <button onClick={() => nav("/dashboard/client")} className="rounded-full bg-[#C8552F] text-white px-6 py-3 font-semibold hover:bg-[#A8451C]">
              View my bookings
            </button>
            <button onClick={() => nav("/browse")} className="rounded-full border border-[#D9CFBE] px-6 py-3 font-semibold hover:border-[#C8552F]">
              Keep browsing
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-5xl px-5 md:px-10 py-10">
      <button onClick={() => nav(-1)} className="inline-flex items-center gap-1 text-sm text-[#6E5F50] hover:text-[#C8552F] mb-4">
        <ArrowLeft size={14} /> Back
      </button>
      <h1 className="font-serif text-4xl md:text-5xl">Book your appointment</h1>
      <p className="text-[#6E5F50] mt-2">with {practitioner.display_name}</p>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mt-8">
        <div className="lg:col-span-2 space-y-6">
          {/* Date */}
          <div className="bg-white rounded-2xl border border-[#D9CFBE] p-5">
            <div className="font-semibold mb-2 flex items-center gap-2"><Calendar size={16} /> Pick a date</div>
            <input
              type="date"
              data-testid={BOOKING.dateInput}
              value={date}
              min={fmtDate(new Date())}
              onChange={(e) => setDate(e.target.value)}
              className="h-12 rounded-full border border-[#D9CFBE] px-5 bg-[#EFE8DA] outline-none focus:ring-2 focus:ring-[#C8552F]"
            />
          </div>

          {/* Time slots */}
          <div className="bg-white rounded-2xl border border-[#D9CFBE] p-5">
            <div className="font-semibold mb-3 flex items-center gap-2"><Clock size={16} /> Choose a time</div>
            {slots.length === 0 ? (
              <div className="text-sm text-[#6E5F50]">No slots available on this date. Try another day.</div>
            ) : (
              <div className="grid grid-cols-3 md:grid-cols-5 gap-2">
                {slots.map((s) => (
                  <button
                    key={s}
                    data-testid={BOOKING.slotButton}
                    onClick={() => setSlot(s)}
                    className={`h-11 rounded-full border text-sm font-medium transition-colors ${slot === s ? "bg-[#C8552F] text-white border-[#C8552F]" : "border-[#D9CFBE] hover:border-[#C8552F]"}`}
                  >
                    {s}
                  </button>
                ))}
              </div>
            )}
          </div>

          {/* Location */}
          {practitioner.service_mode !== "clients_come_to_me" && (
            <div className="bg-white rounded-2xl border border-[#D9CFBE] p-5">
              <div className="font-semibold mb-3 flex items-center gap-2"><MapPin size={16} /> Service location</div>
              <div className="flex gap-2 mb-3 flex-wrap">
                {practitioner.service_mode !== "i_travel_to_clients" && (
                  <button
                    onClick={() => setServiceLocation("practitioner_location")}
                    className={`chip ${serviceLocation === "practitioner_location" ? "chip-active" : ""}`}
                  >
                    At practitioner's location
                  </button>
                )}
                <button
                  onClick={() => setServiceLocation("client_location")}
                  className={`chip ${serviceLocation === "client_location" ? "chip-active" : ""}`}
                >
                  Travel to me (mobile)
                </button>
              </div>
              {serviceLocation === "client_location" && (
                <input
                  data-testid={BOOKING.addressInput}
                  value={clientAddress}
                  onChange={(e) => setClientAddress(e.target.value)}
                  placeholder="Your address (street, city, postal)"
                  className="w-full h-12 rounded-full border border-[#D9CFBE] px-5 bg-[#EFE8DA] outline-none focus:ring-2 focus:ring-[#C8552F]"
                />
              )}
            </div>
          )}

          {/* Notes */}
          <div className="bg-white rounded-2xl border border-[#D9CFBE] p-5">
            <div className="font-semibold mb-3">Notes for your practitioner</div>
            <textarea
              data-testid={BOOKING.notesInput}
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              rows={3}
              placeholder="Hair type, length, design references, special requests…"
              className="w-full rounded-2xl border border-[#D9CFBE] p-4 bg-[#EFE8DA] outline-none focus:ring-2 focus:ring-[#C8552F]"
            />
          </div>
        </div>

        {/* Summary */}
        <div className="lg:col-span-1">
          <div className="sticky top-20 bg-white rounded-2xl border border-[#D9CFBE] p-5">
            <div className="font-serif text-2xl mb-4">Booking summary</div>
            <div className="space-y-3 text-sm">
              <div>
                <div className="text-[#6E5F50] text-xs">Service</div>
                <div className="font-semibold">{service.name}</div>
              </div>
              <div>
                <div className="text-[#6E5F50] text-xs">Duration</div>
                <div>{Math.round(service.duration_minutes_min / 60 * 10) / 10} hours</div>
              </div>
              <div>
                <div className="text-[#6E5F50] text-xs">Date & time</div>
                <div>{date}{slot ? ` · ${slot}` : ""}</div>
              </div>
              <hr className="border-[#D9CFBE]" />
              <div className="flex justify-between"><span>Total</span><span className="font-semibold">${service.price_min.toFixed(2)}</span></div>
              <div className="flex justify-between text-[#C8552F] font-semibold"><span>Deposit (25%)</span><span>${deposit.toFixed(2)}</span></div>
              <div className="flex justify-between text-[#6E5F50]"><span>Remaining at appointment</span><span>${remaining.toFixed(2)}</span></div>
              <div className="text-xs text-[#6E5F50] mt-2">
                Remainder via {practitioner.accepted_payments.join(" / ")}.
              </div>
              {directLink && (
                <div className="text-xs bg-[#EFE8DA] text-[#3D1F2C] rounded-xl p-2">
                  ✦ Direct link booking — 0% commission to {practitioner.display_name}.
                </div>
              )}
            </div>
            <button
              data-testid={BOOKING.payDepositButton}
              onClick={submit}
              disabled={submitting || !slot}
              className="mt-5 w-full inline-flex items-center justify-center gap-2 rounded-full bg-[#C8552F] hover:bg-[#A8451C] disabled:opacity-50 text-white font-semibold py-3 transition-colors"
            >
              <CreditCard size={16} /> {submitting ? "Processing…" : `Pay $${deposit.toFixed(2)} deposit (mocked)`}
            </button>
            <div className="text-xs text-[#6E5F50] mt-3 text-center">
              Stripe Connect mocked for MVP demo. No real charge.
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
