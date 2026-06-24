import type { CSSProperties } from "react";

interface Props {
  value: number; // 1-6
  rolling: boolean;
}

// Dot positions keyed by face value
const DOT_LAYOUTS: Record<number, [number, number][]> = {
  1: [[50, 50]],
  2: [
    [25, 25],
    [75, 75],
  ],
  3: [
    [25, 25],
    [50, 50],
    [75, 75],
  ],
  4: [
    [25, 25],
    [75, 25],
    [25, 75],
    [75, 75],
  ],
  5: [
    [25, 25],
    [75, 25],
    [50, 50],
    [25, 75],
    [75, 75],
  ],
  6: [
    [25, 20],
    [75, 20],
    [25, 50],
    [75, 50],
    [25, 80],
    [75, 80],
  ],
};

export function Die({ value, rolling }: Props) {
  const dots = DOT_LAYOUTS[value] ?? DOT_LAYOUTS[1];

  const containerStyle: CSSProperties = {
    width: 80,
    height: 80,
    borderRadius: 14,
    background: "white",
    border: "2px solid #d1d5db",
    boxShadow: rolling
      ? "0 0 0 3px #6366f1, 0 4px 16px rgba(99,102,241,0.4)"
      : "0 2px 8px rgba(0,0,0,0.12)",
    position: "relative",
    transition: "box-shadow 0.15s",
    animation: rolling ? "spin 0.15s linear infinite" : "none",
    flexShrink: 0,
  };

  return (
    <div style={containerStyle} aria-label={`Die showing ${value}`}>
      {dots.map(([x, y], i) => (
        <span
          key={i}
          style={{
            position: "absolute",
            width: 14,
            height: 14,
            borderRadius: "50%",
            background: "#1e293b",
            left: `calc(${x}% - 7px)`,
            top: `calc(${y}% - 7px)`,
          }}
        />
      ))}
    </div>
  );
}
