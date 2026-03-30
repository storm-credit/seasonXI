"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useState } from "react";
import {
  LayoutDashboard,
  Calculator,
  Film,
  Settings,
  ChevronLeft,
  ChevronRight,
} from "lucide-react";

const NAV_ITEMS = [
  { key: "dashboard", label: "Dashboard", href: "/", icon: LayoutDashboard },
  { key: "evaluate", label: "Evaluate", href: "/evaluate", icon: Calculator },
  { key: "storyframe", label: "Storyframe", href: "/storyframe", icon: Film },
  { key: "settings", label: "Settings", href: "/settings", icon: Settings },
];

export default function Sidebar() {
  const pathname = usePathname();
  const [collapsed, setCollapsed] = useState(false);

  return (
    <aside
      className={`flex flex-col h-screen border-r border-[rgba(201,162,74,0.15)] bg-[rgba(11,13,18,0.95)] transition-all duration-300 ${
        collapsed ? "w-16" : "w-56"
      }`}
    >
      {/* Logo */}
      <div className="flex items-center gap-3 px-4 py-5 border-b border-[rgba(201,162,74,0.15)]">
        <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-sxi-gold to-sxi-gold-soft flex items-center justify-center flex-shrink-0">
          <span className="font-display text-sxi-black text-sm font-bold">XI</span>
        </div>
        {!collapsed && (
          <span className="font-display text-lg tracking-wider gold-text">
            SEASON XI
          </span>
        )}
      </div>

      {/* Navigation */}
      <nav className="flex-1 py-4 px-2 space-y-1">
        {NAV_ITEMS.map((item) => {
          const isActive =
            item.href === "/" ? pathname === "/" : pathname.startsWith(item.href);
          const Icon = item.icon;

          return (
            <Link
              key={item.key}
              href={item.href}
              className={`flex items-center gap-3 px-3 py-2.5 rounded-lg transition-all duration-200 group relative ${
                isActive
                  ? "bg-[rgba(201,162,74,0.1)] text-sxi-gold"
                  : "text-[rgba(245,247,250,0.5)] hover:text-sxi-white hover:bg-[rgba(245,247,250,0.05)]"
              }`}
            >
              {isActive && (
                <div className="absolute left-0 top-1/2 -translate-y-1/2 w-0.5 h-5 bg-sxi-gold rounded-r" />
              )}
              <Icon size={20} className="flex-shrink-0" />
              {!collapsed && (
                <span className="text-sm font-medium">{item.label}</span>
              )}
            </Link>
          );
        })}
      </nav>

      {/* HANESIS Badge */}
      {!collapsed && (
        <div className="px-4 py-3 mx-2 mb-3 rounded-lg bg-[rgba(201,162,74,0.05)] border border-[rgba(201,162,74,0.1)]">
          <p className="text-[10px] uppercase tracking-widest text-sxi-gold/60 mb-1">
            Engine
          </p>
          <p className="font-display text-sm tracking-wider text-sxi-gold">
            HANESIS v1.3
          </p>
        </div>
      )}

      {/* Collapse toggle */}
      <button
        onClick={() => setCollapsed(!collapsed)}
        className="flex items-center justify-center py-3 border-t border-[rgba(201,162,74,0.15)] text-sxi-white/40 hover:text-sxi-gold transition-colors"
      >
        {collapsed ? <ChevronRight size={16} /> : <ChevronLeft size={16} />}
      </button>
    </aside>
  );
}
