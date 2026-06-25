import Icon from "./Icon.jsx";

export default function ErrorBox({ message }) {
  if (!message) return null;
  return (
    <div
      style={{
        marginTop: 16,
        padding: "12px 14px",
        borderRadius: 6,
        border: "1px solid var(--danger-border)",
        background: "var(--danger-bg)",
        color: "var(--danger)",
        fontSize: 13,
        display: "flex",
        gap: 8,
        alignItems: "flex-start",
      }}
    >
      <Icon name="alert" size={15} />
      <span>{message}</span>
    </div>
  );
}
