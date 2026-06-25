import { useRef, useState } from "react";

export default function BeforeAfterSlider({ beforeSrc, afterSrc, height = 220 }) {
  const [pos, setPos] = useState(50);
  const containerRef = useRef(null);
  const dragging = useRef(false);

  const updateFromClientX = (clientX) => {
    const rect = containerRef.current.getBoundingClientRect();
    const pct = ((clientX - rect.left) / rect.width) * 100;
    setPos(Math.min(100, Math.max(0, pct)));
  };

  return (
    <div style={{ marginTop: 14 }}>
      <div
        style={{
          fontSize: 11.5,
          fontWeight: 600,
          color: "var(--text-muted)",
          textTransform: "uppercase",
          letterSpacing: "0.04em",
          marginBottom: 8,
        }}
      >
        Original vs. secured (watermarked)
      </div>
      <div
        ref={containerRef}
        onMouseDown={(e) => {
          dragging.current = true;
          updateFromClientX(e.clientX);
        }}
        onMouseMove={(e) => dragging.current && updateFromClientX(e.clientX)}
        onMouseUp={() => (dragging.current = false)}
        onMouseLeave={() => (dragging.current = false)}
        onTouchMove={(e) => updateFromClientX(e.touches[0].clientX)}
        style={{
          position: "relative",
          height,
          borderRadius: 8,
          overflow: "hidden",
          border: "1px solid var(--border)",
          cursor: "ew-resize",
          userSelect: "none",
          background: "var(--surface-alt)",
        }}
      >
        <img
          src={beforeSrc}
          alt="original"
          style={{ position: "absolute", inset: 0, width: "100%", height: "100%", objectFit: "cover" }}
          draggable={false}
        />
        <div
          style={{
            position: "absolute",
            inset: 0,
            width: `${pos}%`,
            overflow: "hidden",
          }}
        >
          <img
            src={afterSrc}
            alt="secured"
            style={{
              width: containerRef.current ? containerRef.current.offsetWidth : "100%",
              height: "100%",
              objectFit: "cover",
            }}
            draggable={false}
          />
        </div>
        <div
          style={{
            position: "absolute",
            top: 0,
            bottom: 0,
            left: `${pos}%`,
            width: 2,
            background: "var(--accent)",
            transform: "translateX(-1px)",
          }}
        />
        <div
          style={{
            position: "absolute",
            top: "50%",
            left: `${pos}%`,
            transform: "translate(-50%, -50%)",
            width: 26,
            height: 26,
            borderRadius: "50%",
            background: "var(--accent)",
            color: "var(--accent-contrast)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            fontSize: 11,
            fontWeight: 700,
            boxShadow: "0 2px 6px rgba(0,0,0,0.25)",
          }}
        >
          ⇔
        </div>
        <span
          style={{
            position: "absolute",
            top: 8,
            left: 8,
            fontSize: 10.5,
            fontWeight: 700,
            color: "#fff",
            background: "rgba(0,0,0,0.55)",
            padding: "3px 7px",
            borderRadius: 4,
          }}
        >
          ORIGINAL
        </span>
        <span
          style={{
            position: "absolute",
            top: 8,
            right: 8,
            fontSize: 10.5,
            fontWeight: 700,
            color: "#fff",
            background: "rgba(0,0,0,0.55)",
            padding: "3px 7px",
            borderRadius: 4,
          }}
        >
          SECURED
        </span>
      </div>
    </div>
  );
}
