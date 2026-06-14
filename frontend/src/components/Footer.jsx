export default function Footer() {
  return (
    <footer className="mt-20 border-t border-[#E2D9CF] bg-[#F3EFEA]">
      <div className="mx-auto max-w-7xl px-5 md:px-10 py-10 grid grid-cols-1 md:grid-cols-4 gap-8 text-sm">
        <div>
          <div className="text-2xl font-serif mb-3">Curlnect</div>
          <p className="text-[#5C4E43] leading-relaxed">
            A culturally-intelligent marketplace for braiders, locticians, barbers, nail technicians,
            mehndi artists, threading specialists and bridal MUAs across Canada.
          </p>
        </div>
        <div>
          <div className="font-semibold mb-2">For Clients</div>
          <ul className="space-y-1 text-[#5C4E43]">
            <li>Browse practitioners</li>
            <li>How booking works</li>
            <li>Deposit & cancellation policy</li>
          </ul>
        </div>
        <div>
          <div className="font-semibold mb-2">For Practitioners</div>
          <ul className="space-y-1 text-[#5C4E43]">
            <li>Join Curlnect</li>
            <li>0% commission on your own clients</li>
            <li>No-show protection</li>
          </ul>
        </div>
        <div>
          <div className="font-semibold mb-2">Cities</div>
          <ul className="space-y-1 text-[#5C4E43]">
            <li>Calgary</li>
            <li>Edmonton</li>
            <li>Coming soon: Toronto, Ottawa, Montreal</li>
          </ul>
        </div>
      </div>
      <div className="border-t border-[#E2D9CF] py-4 text-center text-xs text-[#5C4E43]">
        &copy; {new Date().getFullYear()} Curlnect. Built for the diaspora.
      </div>
    </footer>
  );
}
