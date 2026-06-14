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
        <span className="inline-flex h-10 w-10 items-center justify-center rounded-full bg-[#984A23] text-white">
          <Sparkles size={18} />
        </span>
        <h1 className="font-serif text-4xl mt-3">Welcome back</h1>
        <p className="text-[#5C4E43] mt-2">Log in to your Curlnect account</p>
      </div>
      <form onSubmit={submit} className="bg-white rounded-2xl border border-[#E2D9CF] p-6 space-y-4">
        <div>
          <label className="block text-xs font-semibold text-[#5C4E43] mb-1 uppercase tracking-widest">Email</label>
          <input
            data-testid={AUTH.loginEmailInput}
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            className="w-full h-12 rounded-full border border-[#E2D9CF] px-5 bg-[#F3EFEA] outline-none focus:ring-2 focus:ring-[#984A23]"
            autoComplete="email"
          />
        </div>
        <div>
          <label className="block text-xs font-semibold text-[#5C4E43] mb-1 uppercase tracking-widest">Password</label>
          <input
            data-testid={AUTH.loginPasswordInput}
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            minLength={6}
            className="w-full h-12 rounded-full border border-[#E2D9CF] px-5 bg-[#F3EFEA] outline-none focus:ring-2 focus:ring-[#984A23]"
            autoComplete="current-password"
          />
        </div>
        {error && <div data-testid={AUTH.loginError} className="text-sm text-red-600 bg-red-50 rounded-xl p-3">{error}</div>}
        <button
          data-testid={AUTH.loginSubmitButton}
          type="submit"
          disabled={loading}
          className="w-full rounded-full bg-[#984A23] hover:bg-[#7e3d1d] disabled:opacity-50 text-white font-semibold h-12 transition-colors"
        >
          {loading ? "Logging in…" : "Log in"}
        </button>
        <div className="text-center text-sm text-[#5C4E43]">
          New to Curlnect? <Link data-testid={AUTH.goToRegisterLink} to="/register" className="text-[#984A23] font-semibold hover:underline">Create an account</Link>
        </div>
      </form>
      <div className="mt-6 text-xs text-[#5C4E43] bg-[#EEDDCB] rounded-2xl p-4">
        <div className="font-semibold mb-1">Demo accounts</div>
        <div>Client: amara@curlnect.com / Pass123!</div>
        <div>Practitioner: blessing@curlnect.com / Pass123!</div>
        <div>Admin: admin@curlnect.com / AdminPass123!</div>
      </div>
    </div>
  );
}
