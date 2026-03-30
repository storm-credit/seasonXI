import type { TierName } from "@/lib/types";
import { TIER_CONFIG } from "@/lib/constants";

interface TierBadgeProps {
  tier: string;
  size?: "sm" | "md" | "lg";
}

export default function TierBadge({ tier, size = "md" }: TierBadgeProps) {
  const tierKey = tier.toUpperCase() as TierName;
  const config = TIER_CONFIG[tierKey] || TIER_CONFIG.BRONZE;

  const sizeClasses = {
    sm: "text-[10px] px-1.5 py-0.5",
    md: "text-xs px-2 py-0.5",
    lg: "text-sm px-3 py-1",
  };

  return (
    <span
      className={`inline-block font-display tracking-widest rounded font-bold ${config.bg} ${sizeClasses[size]}`}
    >
      {tierKey}
    </span>
  );
}
