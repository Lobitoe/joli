import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api, formatApiError } from "@/lib/api";
import { CLIENT_DASH } from "@/constants/testIds";
import { Calendar, Star, Heart, X, MessageSquare } from "lucide-react";
import { toast } from "sonner";

function isUpcoming(b) {
  return ["pending", "confirmed"].includes(b.status);
}

export default function ClientDashboard() {
  const [bookings, setBookings] = useState([]);
  const [favorites, setFavorites] = useState([]);
  const [notifications, setNotifications] = useState([]);
  const [reviewFor, setReviewFor] = useState(null);
  const [rating, setRating] = useState(5);
  const [text, setText] = useState("");

  const load = async () => {
    const [b, f, n] = await Promise.all([
      api.get("/bookings"),
      api.get("/me/favorites"),
      api.get("/me/notifications"),
    ]);
    setBookings(b.data);
    setFavorites(f.data);
    setNotifications(n.data);
  };

  useEffect(() => {
    load();
  }, []);

  const cancel = async (id) => {
    try {
      await api.put(`/bookings/${id}/status`, { status: "cancelled_by_client" });
      toast.success("Booking cancelled");
      await load();
    } catch (e) {
      toast.error(formatApiError(e.response?.data?.detail));
    }
  };

  const markCompleteForDemo = async (id) => {
    // Helper for demo: allow client to mark a confirmed booking as completed so they can leave a review
    try {
      await api.put(`/bookings/${id}/status`, { status: "completed" });
      toast.success("Marked completed — leave a review now!");
      await load();
    } catch (e) {
      toast.error(formatApiError(e.response?.data?.detail));
    }
  };

  const submitReview = async () => {
    try {
      await api.post("/reviews", { booking_id: reviewFor.id, rating, text });
      toast.success("Thanks for reviewing!");
      setReviewFor(null);
      setText("");
      setRating(5);
      await load();
    } catch (e) {
      toast.error(formatApiError(e.response?.data?.detail));
    }
  };

  const upcoming = bookings.filter(isUpcoming);
  const past = bookings.filter((b) => !isUpcoming(b));

  return (
    <div className="mx-auto max-w-6xl px-5 md:px-10 py-10">
      <h1 className="font-serif text-4xl md:text-5xl">Hi, beautiful 👋</h1>
      <p className="text-[#6E5F50] mt-2">Here's what's coming up.</p>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mt-8">
        <div className="lg:col-span-2 space-y-6">
          {/* Upcoming */}
          <div className="bg-white rounded-2xl border border-[#D9CFBE] p-6" data-testid={CLIENT_DASH.upcomingBookings}>
            <div className="flex items-center justify-between mb-4">
              <h2 className="font-serif text-2xl flex items-center gap-2"><Calendar size={18} /> Upcoming</h2>
              <span className="text-sm text-[#6E5F50]">{upcoming.length} booking{upcoming.length !== 1 ? "s" : ""}</span>
            </div>
            {upcoming.length === 0 ? (
              <div className="text-[#6E5F50] text-sm">
                No upcoming bookings. <Link to="/browse" className="text-[#C8552F] font-semibold">Find a practitioner →</Link>
              </div>
            ) : (
              <div className="space-y-3">
                {upcoming.map((b) => (
                  <div key={b.id} className="flex items-center justify-between border border-[#D9CFBE] rounded-2xl p-4">
                    <div>
                      <div className="font-semibold">{b.service_name}</div>
                      <div className="text-xs text-[#6E5F50] mt-0.5">with {b.practitioner_name}</div>
                      <div className="text-sm mt-1">{b.booking_date} · {b.start_time}–{b.end_time}</div>
                    </div>
                    <div className="text-right text-sm">
                      <div className="font-serif text-lg">${b.quoted_price}</div>
                      <div className="text-xs text-[#6E5F50]">deposit ${b.deposit_amount} paid</div>
                      <div className="flex gap-2 mt-2 justify-end">
                        <button
                          onClick={() => markCompleteForDemo(b.id)}
                          className="text-xs rounded-full border border-[#D9CFBE] hover:border-[#2D7D6F] px-3 py-1"
                          title="Demo: mark completed"
                        >
                          Mark done
                        </button>
                        <button
                          data-testid={CLIENT_DASH.cancelBookingButton}
                          onClick={() => cancel(b.id)}
                          className="text-xs rounded-full border border-[#D9CFBE] hover:border-red-400 hover:text-red-500 px-3 py-1 inline-flex items-center gap-1"
                        >
                          <X size={12} /> Cancel
                        </button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Past */}
          <div className="bg-white rounded-2xl border border-[#D9CFBE] p-6" data-testid={CLIENT_DASH.pastBookings}>
            <h2 className="font-serif text-2xl mb-4">Past bookings</h2>
            {past.length === 0 ? (
              <div className="text-[#6E5F50] text-sm">No past bookings yet.</div>
            ) : (
              <div className="space-y-3">
                {past.map((b) => (
                  <div key={b.id} className="flex items-center justify-between border border-[#D9CFBE] rounded-2xl p-4">
                    <div>
                      <div className="font-semibold">{b.service_name}</div>
                      <div className="text-xs text-[#6E5F50] mt-0.5">with {b.practitioner_name} · {b.booking_date}</div>
                      <span className="chip mt-2 capitalize">{b.status.replace(/_/g, " ")}</span>
                    </div>
                    {b.status === "completed" && (
                      <button
                        data-testid={CLIENT_DASH.reviewButton}
                        onClick={() => setReviewFor(b)}
                        className="inline-flex items-center gap-1 text-sm rounded-full bg-[#2D7D6F] hover:bg-[#236359] text-white px-4 py-2"
                      >
                        <Star size={14} /> Leave review
                      </button>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* Favorites */}
          <div className="bg-white rounded-2xl border border-[#D9CFBE] p-6" data-testid={CLIENT_DASH.favoritesList}>
            <h2 className="font-serif text-xl flex items-center gap-2"><Heart size={16} /> Favorites</h2>
            {favorites.length === 0 ? (
              <div className="text-[#6E5F50] text-sm mt-3">No favorites yet.</div>
            ) : (
              <div className="space-y-3 mt-3">
                {favorites.map((p) => (
                  <Link key={p.id} to={`/practitioner/${p.id}`} className="flex items-center gap-3 hover:bg-[#EFE8DA] rounded-xl p-2">
                    <img src={p.portfolio_thumbs?.[0] || p.profile_photo_url} className="w-12 h-12 rounded-xl object-cover" alt="" />
                    <div>
                      <div className="font-semibold text-sm">{p.display_name}</div>
                      <div className="text-xs text-[#6E5F50] capitalize">{p.practitioner_type.replace("_", " ")} · {p.city}</div>
                    </div>
                  </Link>
                ))}
              </div>
            )}
          </div>

          {/* Notifications */}
          <div className="bg-white rounded-2xl border border-[#D9CFBE] p-6">
            <h2 className="font-serif text-xl flex items-center gap-2"><MessageSquare size={16} /> SMS / WhatsApp log</h2>
            <p className="text-xs text-[#6E5F50] mb-3">Mocked notifications</p>
            <div className="space-y-2 max-h-72 overflow-y-auto">
              {notifications.length === 0 ? (
                <div className="text-[#6E5F50] text-sm">Nothing yet.</div>
              ) : notifications.map((n) => (
                <div key={n.id} className="bg-[#EFE8DA] rounded-xl p-3 text-xs">
                  <div className="text-[10px] uppercase tracking-widest text-[#6E5F50] mb-1">{n.channel}</div>
                  <div>{n.body}</div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Review modal */}
      {reviewFor && (
        <div className="fixed inset-0 bg-black/50 z-50 flex items-end md:items-center justify-center p-4">
          <div className="bg-white rounded-2xl max-w-md w-full p-6">
            <div className="font-serif text-2xl mb-1">Leave a review</div>
            <div className="text-sm text-[#6E5F50] mb-4">for {reviewFor.practitioner_name}</div>
            <div className="flex gap-1 mb-3">
              {[1, 2, 3, 4, 5].map((n) => (
                <button key={n} onClick={() => setRating(n)} className="p-1">
                  <Star size={28} className={n <= rating ? "fill-[#E8A33D] text-[#E8A33D]" : "text-[#D9CFBE]"} />
                </button>
              ))}
            </div>
            <textarea
              value={text}
              onChange={(e) => setText(e.target.value)}
              rows={4}
              placeholder="Tell others how it went…"
              className="w-full rounded-2xl border border-[#D9CFBE] p-3 bg-[#EFE8DA] outline-none focus:ring-2 focus:ring-[#C8552F]"
            />
            <div className="flex gap-2 mt-4 justify-end">
              <button onClick={() => setReviewFor(null)} className="rounded-full border border-[#D9CFBE] px-4 py-2 text-sm">Cancel</button>
              <button onClick={submitReview} className="rounded-full bg-[#C8552F] hover:bg-[#A8451C] text-white px-4 py-2 text-sm font-semibold">Submit</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
