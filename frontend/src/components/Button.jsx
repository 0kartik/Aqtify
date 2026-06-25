const VARIANTS = {
  primary: { background: "var(--accent)", color: "var(--accent-contrast)" },
  secondary: {
    background: "var(--surface)",
    color: "var(--text)",
    border: "1px solid var(--border-strong)",
  },
  ghost: {
    background: "transparent",
    color: "var(--text-muted)",
    border: "1px solid var(--border)",
  },
};

export default function Button({
  children,
  onClick,
  variant = "primary",
  disabled,
  style,
  type = "button",
}) {
  const base = {
    fontFamily: "var(--sans)",
    fontWeight: 600,
    fontSize: 13.5,
    borderRadius: "var(--radius)",
    padding: "10px 16px",
    cursor: disabled ? "not-allowed" : "pointer",
    border: "1px solid transparent",
    display: "inline-flex",
    alignItems: "center",
    justifyContent: "center",
    gap: 8,
    transition: "background .12s ease, border-color .12s ease",
    opacity: disabled ? 0.5 : 1,
  };

  return (
    <button
      type={type}
      onClick={onClick}
      disabled={disabled}
      style={{ ...base, ...VARIANTS[variant], ...style }}
    >
      {children}
    </button>
  );
}
