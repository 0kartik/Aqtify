export default function Logo({ size = 26 }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none">
      <path
        d="M12 2l8 3.5v6c0 5-3.4 8.8-8 10.5-4.6-1.7-8-5.5-8-10.5v-6L12 2z"
        fill="var(--accent)"
      />
      <path
        d="M8.5 12l2.5 2.5L16 9"
        stroke="var(--accent-contrast)"
        strokeWidth={1.8}
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
}
