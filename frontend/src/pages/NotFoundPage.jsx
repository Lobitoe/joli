import { Link } from "react-router-dom";
import { Search, ArrowLeft } from "lucide-react";

export default function NotFoundPage() {
  return (
    <section className="mx-auto max-w-3xl px-5 md:px-10 py-24 md:py-32 text-center">
      <div className="inline-flex items-center gap-2 rounded-full bg-[#EFE8DA] px-3 py-1 text-xs font-semibold tracking-[0.2em] uppercase text-[#3D1F2C]">
        Error 404
      </div>
      <h1 className="font-serif text-7xl md:text-9xl tracking-tight leading-none mt-6 text-[#1F1A17]">
        4<span className="text-[#C8552F]">0</span>4
      </h1>
      <h2 className="font-serif text-3xl md:text-4xl mt-4 text-[#1F1A17]">Page not found</h2>
      <p className="mt-4 text-lg text-[#6E5F50] max-w-xl mx-auto leading-relaxed">
        We couldn't find the page you were looking for. It may have moved, or
        the link might be out of date. Let's get you back to the good stuff.
      </p>

      <div className="mt-8 flex flex-col sm:flex-row gap-3 justify-center">
        <Link
          to="/"
          className="inline-flex items-center justify-center gap-2 rounded-full bg-[#C8552F] text-white px-6 py-3 font-semibold hover:bg-[#A8451C] transition-colors"
        >
          <ArrowLeft size={16} /> Back home
        </Link>
        <Link
          to="/browse"
          className="inline-flex items-center justify-center gap-2 rounded-full border border-[#D9CFBE] bg-white text-[#1F1A17] px-6 py-3 font-semibold hover:border-[#C8552F] hover:text-[#C8552F] transition-colors"
        >
          <Search size={16} /> Browse practitioners
        </Link>
      </div>
    </section>
  );
}
