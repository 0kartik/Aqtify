import { useEffect, useState } from "react";

const TONES = {
  ok: { bg: "var(--success-bg)", border: "var(--success-border)", color: "var(--success)" },
  warn: { bg: "var(--warn-bg)", border: "var(--warn-border)", color: "var(--warn)" },
  bad: { bg: "var(--danger-bg)", border: "var(--danger-border)", color: "var(--danger)" },
};

function useCountUp(target, durationMs = 600) {
  const [value, setValue] = useState(0);
  const numeric = typeof target === "number";

  useEffect(() => {
    if (!numeric) return;
    let raf;
    const start = performance.now();
    const tick = (now) => {
      const progress = Math.min((now - start) / durationMs, 1);
      setValue(Math.round(target * (1 - Math.pow(1 - progress, 3))));
      if (progress < 1) raf = requestAnimationFrame(tick);
    };
    raf = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(raf);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [target]);

  return numeric ? value : target;
}

export default function VerdictBanner({ tone, score, title, subtitle }) {
  const t = TONES[tone];
  const displayScore = useCountUp(score);

  return (
    <div
      style={{
        display: "flex",
        alignItems: "center",
        gap: 18,
        padding: "18px 20px",
        borderRadius: "var(--radius)",
        background: t.bg,
        border: `1px solid ${t.border}`,
        marginBottom: 18,
        boxShadow: "0 2px 10px rgba(20,20,15,0.05)",
      }}
    >
      <div style={{ fontSize: 34, fontWeight: 700, color: t.color, minWidth: 64 }}>{displayScore}</div>
      <div>
        <div style={{ fontWeight: 700, fontSize: 16, color: t.color }}>{title}</div>
        <div style={{ fontSize: 12.5, color: "var(--text-muted)", marginTop: 2 }}>{subtitle}</div>
      </div>
    </div>
  );
}
