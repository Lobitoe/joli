import { Scissors, ShieldCheck, FileBadge, Users, Star, BadgeCheck } from "lucide-react";

// Brand badge palette per Joli Brand v0.1
// Semantic mapping: trust=sage, certifications=plum, top-rated=saffron, community=clay
const META = {
  certified_barber: { label: "Certified Barber", Icon: Scissors, bg: "#3D1F2C", fg: "#F7F1E8", border: "#3D1F2C" },
  certified_hairstylist: { label: "Certified Stylist", Icon: Scissors, bg: "#3D1F2C", fg: "#F7F1E8", border: "#3D1F2C" },
  insured: { label: "Insured", Icon: ShieldCheck, bg: "#2D7D6F", fg: "#F7F1E8", border: "#2D7D6F" },
  background_checked: { label: "Background Checked", Icon: FileBadge, bg: "#2D7D6F", fg: "#F7F1E8", border: "#2D7D6F" },
  community_endorsed: { label: "Community Endorsed", Icon: Users, bg: "#C8552F", fg: "#F7F1E8", border: "#C8552F" },
  top_rated: { label: "Top Rated", Icon: Star, bg: "#E8A33D", fg: "#1F1A17", border: "#E8A33D" },
  verified: { label: "Verified", Icon: BadgeCheck, bg: "#F7F1E8", fg: "#2D7D6F", border: "#2D7D6F" },
};

export default function BadgeChip({ type, size = "sm" }) {
  const meta = META[type];
  if (!meta) return null;
  const padding = size === "lg" ? "px-3 py-1.5 text-xs" : "px-2 py-0.5 text-[10px]";
  const icon = size === "lg" ? 14 : 11;
  return (
    <span
      data-testid={`badge-${type}`}
      className={`inline-flex items-center gap-1 rounded-full font-semibold uppercase tracking-wider border ${padding}`}
      style={{ background: meta.bg, color: meta.fg, borderColor: meta.border, letterSpacing: "0.08em" }}
    >
      <meta.Icon size={icon} /> {meta.label}
    </span>
  );
}

export function BadgeRow({ badges = [], size = "sm", limit }) {
  if (!badges || badges.length === 0) return null;
  const shown = limit ? badges.slice(0, limit) : badges;
  return (
    <div className="flex flex-wrap gap-1.5">
      {shown.map((b) => <BadgeChip key={b} type={b} size={size} />)}
    </div>
  );
}
