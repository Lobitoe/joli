import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "@/contexts/AuthContext";
import { AUTH } from "@/constants/testIds";
import { Sparkles } from "lucide-react";

export default function LoginPage() {
  const { login } = useAuth();
  const nav = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const submit = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    const r = await login(email, password);
    setLoading(false);
    if (!r.ok) { setError(r.error); return; }
    if (r.user.role === "practitioner") nav("/dashboard/practitioner");
    else if (r.user.role === "admin") nav("/dashboard/admin");
    else nav("/dashboard/client");
  };

  return (
    <div className="mx-auto max-w-md px-5 py-16">
      <div className="text-center mb-8">
        <span className="joli-roundel h-12 w-12 text-2xl">ȷ</span>
        <h1 className="font-serif text-4xl mt-3">Welcome back</h1>
        <p className="text-[#6E5F50] mt-2">Log in to your Joli account</p>
      </div>
      <form onSubmit={submit} className="bg-white rounded-2xl border border-[#D9CFBE] p-6 space-y-4">
        <div>
          <label className="block text-xs font-semibold text-[#6E5F50] mb-1 uppercase tracking-widest">Email</label>
          <input
            data-testid={AUTH.loginEmailInput}
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            className="w-full h-12 rounded-full border border-[#D9CFBE] px-5 bg-[#EFE8DA] outline-none focus:ring-2 focus:ring-[#C8552F]"
            autoComplete="email"
          />
        </div>
        <div>
          <label className="block text-xs font-semibold text-[#6E5F50] mb-1 uppercase tracking-widest">Password</label>
          <input
            data-testid={AUTH.loginPasswordInput}
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            minLength={6}
            className="w-full h-12 rounded-full border border-[#D9CFBE] px-5 bg-[#EFE8DA] outline-none focus:ring-2 focus:ring-[#C8552F]"
            autoComplete="current-password"
          />
        </div>
        {error && <div data-testid={AUTH.loginError} className="text-sm text-red-600 bg-red-50 rounded-xl p-3">{error}</div>}
        <button
          data-testid={AUTH.loginSubmitButton}
          type="submit"
          disabled={loading}
          className="w-full rounded-full bg-[#C8552F] hover:bg-[#A8451C] disabled:opacity-50 text-white font-semibold h-12 transition-colors"
        >
          {loading ? "Logging in…" : "Log in"}
        </button>
        <div className="text-center text-sm text-[#6E5F50]">
          New to Joli? <Link data-testid={AUTH.goToRegisterLink} to="/register" className="text-[#C8552F] font-semibold hover:underline">Create an account</Link>
        </div>
      </form>
      <div className="mt-6 text-xs text-[#6E5F50] bg-[#EFE8DA] rounded-2xl p-4">
        <div className="font-semibold mb-1">Demo accounts</div>
        <div>Client: amara@tryjoli.com / Pass123!</div>
        <div>Practitioner: blessing@tryjoli.com / Pass123!</div>
        <div>Admin: admin@tryjoli.com / AdminPass123!</div>
      </div>
    </div>
  );
}
