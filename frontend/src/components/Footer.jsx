import { Link } from "react-router-dom";

export default function Footer() {
  return (
    <footer className="mt-20 border-t border-[#D9CFBE] bg-[#EFE8DA]">
      <div className="mx-auto max-w-7xl px-5 md:px-10 py-10 grid grid-cols-1 md:grid-cols-4 gap-8 text-sm">
        <div>
          <div className="joli-wordmark text-3xl mb-3">jol<span className="tittle">i</span></div>
          <p className="text-[#6E5F50] leading-relaxed">
            Beauty that knows you. A culturally-intelligent marketplace for braiders,
            locticians, barbers, nail technicians, mehndi artists, threading specialists
            and bridal MUAs across Canada.
          </p>
        </div>
        <div>
          <div className="font-semibold mb-2">For Clients</div>
          <ul className="space-y-1.5 text-[#6E5F50]">
            <li><Link to="/browse" className="hover:text-[#C8552F] transition-colors">Browse practitioners</Link></li>
            <li><Link to="/how-it-works" className="hover:text-[#C8552F] transition-colors">How booking works</Link></li>
            <li><Link to="/how-it-works" className="hover:text-[#C8552F] transition-colors">Deposit & cancellation policy</Link></li>
            <li><Link to="/blog" className="hover:text-[#C8552F] transition-colors">The Joli Journal</Link></li>
          </ul>
        </div>
        <div>
          <div className="font-semibold mb-2">For Practitioners</div>
          <ul className="space-y-1.5 text-[#6E5F50]">
            <li><Link to="/register" className="hover:text-[#C8552F] transition-colors">Join Joli</Link></li>
            <li><Link to="/how-it-works" className="hover:text-[#C8552F] transition-colors">0% on your own clients</Link></li>
            <li><Link to="/how-it-works" className="hover:text-[#C8552F] transition-colors">No-show protection</Link></li>
            <li><Link to="/blog?category=Practitioner%20Education" className="hover:text-[#C8552F] transition-colors">Practitioner guides</Link></li>
          </ul>
        </div>
        <div>
          <div className="font-semibold mb-2">Cities</div>
          <ul className="space-y-1.5 text-[#6E5F50]">
            <li><Link to="/browse?city=Calgary" className="hover:text-[#C8552F] transition-colors">Calgary</Link></li>
            <li><Link to="/browse?city=Edmonton" className="hover:text-[#C8552F] transition-colors">Edmonton</Link></li>
            <li className="text-[#8A7B6B]">Coming soon: Toronto, Ottawa, Montreal</li>
          </ul>
        </div>
      </div>
      <div className="border-t border-[#D9CFBE] py-4 text-center text-xs text-[#6E5F50]">
        &copy; {new Date().getFullYear()} Joli. Built for the diaspora.
      </div>
    </footer>
  );
}
