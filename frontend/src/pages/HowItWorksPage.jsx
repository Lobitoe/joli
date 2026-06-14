import { Link } from "react-router-dom";
import { CheckCircle2, Shield, Calendar, Heart } from "lucide-react";

export default function HowItWorksPage() {
  return (
    <div className="mx-auto max-w-4xl px-5 md:px-10 py-12">
      <div className="text-center mb-12">
        <div className="overline text-xs tracking-[0.2em] uppercase font-bold text-[#984A23]">The way it works</div>
        <h1 className="font-serif text-5xl mt-2">Booking, deposits, and a fair model.</h1>
      </div>

      <div className="space-y-8">
        <Step n="01" title="Find someone who knows your texture or tradition" body="Search by style (Knotless Braids, Skin Fade, Bridal Mehndi) and city. Filter by mobile vs. studio. See actual portfolios — not stock photos." />
        <Step n="02" title="Book a real time block — even if it's 6 hours" body="Variable durations are first-class. Our calendar handles a 30-minute threading touch-up the same as a 6-hour braiding session, with breaks if you need them." />
        <Step n="03" title="Pay a 25% deposit to confirm" body="The deposit locks your slot and protects your practitioner from no-shows. The remainder is settled at the appointment in card, e-transfer, or cash — whichever your practitioner accepts." />
        <Step n="04" title="Get reminders via SMS / WhatsApp" body="Both you and your practitioner get a confirmation, a 24-hour reminder, and a 2-hour reminder. Practitioners get your address for mobile bookings." />
        <Step n="05" title="Show up, look incredible, leave a review" body="After your appointment, leave a rating with optional photos. Your practitioner can respond. The community learns." />
      </div>

      <div className="mt-14 rounded-3xl border border-[#E2D9CF] p-8 grid md:grid-cols-3 gap-6 bg-white">
        <ValueProp icon={<Shield size={20} />} title="10% / 0% commission" body="10% on first marketplace booking. 0% on repeats. 0% on bookings via your direct link — forever." />
        <ValueProp icon={<Calendar size={20} />} title="Direct booking link" body="Every practitioner gets a personal URL to share on Instagram and WhatsApp. Those bookings cost you nothing." />
        <ValueProp icon={<Heart size={20} />} title="Built for the diaspora" body="Cultural categories at the core: cornrows by length, fades by type, mehndi by complexity, bridal by tradition." />
      </div>

      <div className="mt-12 text-center">
        <Link to="/register" className="inline-flex rounded-full bg-[#984A23] hover:bg-[#7e3d1d] text-white font-semibold px-8 py-4">Get started</Link>
      </div>
    </div>
  );
}

function Step({ n, title, body }) {
  return (
    <div className="grid grid-cols-12 gap-4 items-start">
      <div className="col-span-2 md:col-span-1 font-serif text-4xl text-[#984A23]">{n}</div>
      <div className="col-span-10 md:col-span-11">
        <div className="font-serif text-2xl">{title}</div>
        <p className="text-[#5C4E43] mt-1 leading-relaxed">{body}</p>
      </div>
    </div>
  );
}

function ValueProp({ icon, title, body }) {
  return (
    <div>
      <div className="inline-flex h-10 w-10 items-center justify-center rounded-full bg-[#EEDDCB] text-[#4A2B12]">{icon}</div>
      <div className="font-serif text-xl mt-3">{title}</div>
      <div className="text-sm text-[#5C4E43] mt-1">{body}</div>
    </div>
  );
}
