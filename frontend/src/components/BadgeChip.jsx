import { Scissors, ShieldCheck, FileBadge, Users, Star, BadgeCheck } from "lucide-react";

const META = {
  certified_barber: { label: "Certified Barber", Icon: Scissors, color: "bg-[#2B231D] text-white border-[#2B231D]" },
  certified_hairstylist: { label: "Certified Stylist", Icon: Scissors, color: "bg-[#2B231D] text-white border-[#2B231D]" },
  insured: { label: "Insured", Icon: ShieldCheck, color: "bg-[#4A5D23] text-white border-[#4A5D23]" },
  background_checked: { label: "Background Checked", Icon: FileBadge, color: "bg-[#4A5D23] text-white border-[#4A5D23]" },
  community_endorsed: { label: "Community Endorsed", Icon: Users, color: "bg-[#984A23] text-white border-[#984A23]" },
  top_rated: { label: "Top Rated", Icon: Star, color: "bg-[#E1A100] text-[#2B231D] border-[#E1A100]" },
  verified: { label: "ID Verified", Icon: BadgeCheck, color: "bg-white text-[#2B231D] border-[#2B231D]" },
};

export default function BadgeChip({ type, size = "sm" }) {
  const meta = META[type];
  if (!meta) return null;
  const padding = size === "lg" ? "px-3 py-1.5 text-xs" : "px-2 py-0.5 text-[10px]";
  const icon = size === "lg" ? 14 : 11;
  return (
    <span data-testid={`badge-${type}`} className={`inline-flex items-center gap-1 rounded-full border font-semibold uppercase tracking-wider ${padding} ${meta.color}`}>
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
