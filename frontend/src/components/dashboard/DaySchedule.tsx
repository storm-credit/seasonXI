"use client";

import { SCHEDULE } from "@/lib/constants";

interface DayScheduleProps {
  selectedDay: number;
  onSelectDay: (index: number) => void;
}

export default function DaySchedule({ selectedDay, onSelectDay }: DayScheduleProps) {
  return (
    <div className="flex gap-2 overflow-x-auto pb-2 scrollbar-thin">
      {SCHEDULE.map((day, i) => (
        <button
          key={day.date}
          onClick={() => onSelectDay(i)}
          className={`flex-shrink-0 px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200 ${
            selectedDay === i
              ? "bg-gradient-to-r from-sxi-gold to-sxi-gold-soft text-sxi-black"
              : "bg-[rgba(245,247,250,0.05)] text-sxi-white/50 hover:text-sxi-white hover:bg-[rgba(245,247,250,0.08)] border border-[rgba(201,162,74,0.1)]"
          }`}
        >
          <span className="block font-display tracking-wide">
            {day.label}
          </span>
          <span className={`block text-[10px] mt-0.5 ${selectedDay === i ? "text-sxi-black/60" : "text-sxi-white/30"}`}>
            {day.date}
          </span>
        </button>
      ))}
    </div>
  );
}
