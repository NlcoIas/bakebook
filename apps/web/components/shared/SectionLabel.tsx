interface SectionLabelProps {
  children: React.ReactNode;
}

export function SectionLabel({ children }: SectionLabelProps) {
  return (
    <div className="mt-[18px] flex items-center gap-3 font-mono text-[10px] tracking-[0.22em] uppercase text-ink-faint">
      <span>{children}</span>
      <span
        className="flex-1 h-px"
        style={{
          background:
            "repeating-linear-gradient(to right, var(--rule) 0 4px, transparent 4px 8px)",
        }}
      />
    </div>
  );
}
