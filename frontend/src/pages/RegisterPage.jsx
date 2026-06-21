import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "@/contexts/AuthContext";
import { AUTH } from "@/constants/testIds";
import { Sparkles, Scissors, User } from "lucide-react";

export default function RegisterPage() {
  const { register } = useAuth();
  const nav = useNavigate();
  const [form, setForm] = useState({ name: "", email: "", password: "", role: "client" });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const onChange = (k) => (e) => setForm((f) => ({ ...f, [k]: e.target.value }));

  const submit = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    const r = await register(form);
    setLoading(false);
    if (!r.ok) { setError(r.error); return; }
    if (r.user.role === "practitioner") nav("/dashboard/practitioner/onboarding");
    else nav("/dashboard/client");
  };

  return (
    <div className="mx-auto max-w-md px-5 py-12">
      <div className="text-center mb-8">
        <span className="joli-roundel h-12 w-12 text-2xl">ȷ</span>
        <h1 className="font-serif text-4xl mt-3">Join Joli</h1>
        <p className="text-[#6E5F50] mt-2">Beauty that knows you.</p>
      </div>
      <form onSubmit={submit} className="bg-white rounded-2xl border border-[#D9CFBE] p-6 space-y-4">
        <div className="grid grid-cols-2 gap-2">
          <button
            type="button"
            data-testid={AUTH.registerRoleClient}
            onClick={() => setForm((f) => ({ ...f, role: "client" }))}
            className={`flex items-center justify-center gap-2 rounded-2xl border p-4 transition-colors ${form.role === "client" ? "bg-[#C8552F] text-white border-[#C8552F]" : "border-[#D9CFBE] hover:border-[#C8552F]"}`}
          >
            <User size={16} /> Book services
          </button>
          <button
            type="button"
            data-testid={AUTH.registerRolePractitioner}
            onClick={() => setForm((f) => ({ ...f, role: "practitioner" }))}
            className={`flex items-center justify-center gap-2 rounded-2xl border p-4 transition-colors ${form.role === "practitioner" ? "bg-[#C8552F] text-white border-[#C8552F]" : "border-[#D9CFBE] hover:border-[#C8552F]"}`}
          >
            <Scissors size={16} /> Offer services
          </button>
        </div>
        <div>
          <label className="block text-xs font-semibold text-[#6E5F50] mb-1 uppercase tracking-widest">Full name</label>
          <input
            data-testid={AUTH.registerNameInput}
            value={form.name}
            onChange={onChange("name")}
            required
            className="w-full h-12 rounded-full border border-[#D9CFBE] px-5 bg-[#EFE8DA] outline-none focus:ring-2 focus:ring-[#C8552F]"
          />
        </div>
        <div>
          <label className="block text-xs font-semibold text-[#6E5F50] mb-1 uppercase tracking-widest">Email</label>
          <input
            data-testid={AUTH.registerEmailInput}
            type="email"
            value={form.email}
            onChange={onChange("email")}
            required
            className="w-full h-12 rounded-full border border-[#D9CFBE] px-5 bg-[#EFE8DA] outline-none focus:ring-2 focus:ring-[#C8552F]"
          />
        </div>
        <div>
          <label className="block text-xs font-semibold text-[#6E5F50] mb-1 uppercase tracking-widest">Password</label>
          <input
            data-testid={AUTH.registerPasswordInput}
            type="password"
            value={form.password}
            onChange={onChange("password")}
            required
            minLength={6}
            className="w-full h-12 rounded-full border border-[#D9CFBE] px-5 bg-[#EFE8DA] outline-none focus:ring-2 focus:ring-[#C8552F]"
          />
        </div>
        {error && <div data-testid={AUTH.registerError} className="text-sm text-red-600 bg-red-50 rounded-xl p-3">{error}</div>}
        <button
          data-testid={AUTH.registerSubmitButton}
          type="submit"
          disabled={loading}
          className="w-full rounded-full bg-[#C8552F] hover:bg-[#A8451C] disabled:opacity-50 text-white font-semibold h-12 transition-colors"
        >
          {loading ? "Creating…" : "Create my account"}
        </button>
        <div className="text-center text-sm text-[#6E5F50]">
          Already have an account? <Link data-testid={AUTH.goToLoginLink} to="/login" className="text-[#C8552F] font-semibold hover:underline">Log in</Link>
        </div>
      </form>
    </div>
  );
}
