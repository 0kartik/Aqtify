import Icon from "./Icon.jsx";

const STATE_STYLES = {
  idle: { borderColor: "var(--border)", color: "var(--text-faint)", background: "var(--surface-alt)" },
  active: { borderColor: "var(--accent)", color: "var(--accent)", background: "var(--surface)" },
  done: {
    borderColor: "var(--success-border)",
    color: "var(--success)",
    background: "var(--success-bg)",
  },
};

export default function Pipeline({ steps, activeIndex }) {
  return (
    <div style={{ display: "flex", gap: 6, flexWrap: "wrap", margin: "18px 0" }}>
      {steps.map((s, i) => {
        const state =
          activeIndex === null ? "idle" : i < activeIndex ? "done" : i === activeIndex ? "active" : "idle";
        return (
          <div
            key={s}
            style={{
              flex: "1 1 100px",
              padding: "8px 10px",
              borderRadius: 6,
              border: "1px solid",
              fontSize: 11.5,
              fontWeight: 600,
              textAlign: "center",
              transition: "all .2s ease",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              gap: 5,
              ...STATE_STYLES[state],
            }}
          >
            {state === "done" && <Icon name="check" size={11} />}
            {s}
          </div>
        );
      })}
    </div>
  );
}
