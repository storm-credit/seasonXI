interface GlassPanelProps {
  children: React.ReactNode;
  className?: string;
  hover?: boolean;
  glow?: boolean;
}

export default function GlassPanel({
  children,
  className = "",
  hover = false,
  glow = false,
}: GlassPanelProps) {
  return (
    <div
      className={`glass-panel ${hover ? "glass-panel-hover" : ""} ${
        glow ? "gold-glow" : ""
      } ${className}`}
    >
      {children}
    </div>
  );
}
