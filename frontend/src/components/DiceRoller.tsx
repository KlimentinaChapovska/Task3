import { useState, useRef, useEffect } from "react";
import { Die } from "./Die";

function randomFace(): number {
  return Math.floor(Math.random() * 6) + 1;
}

export function DiceRoller() {
  const [dice, setDice] = useState<[number, number]>([1, 1]);
  const [rolling, setRolling] = useState(false);
  const [hasRolled, setHasRolled] = useState(false);
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const timeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  // Clean up timers on unmount
  useEffect(() => {
    return () => {
      if (intervalRef.current) clearInterval(intervalRef.current);
      if (timeoutRef.current) clearTimeout(timeoutRef.current);
    };
  }, []);

  function roll() {
    if (rolling) return;
    setRolling(true);
    setHasRolled(false);

    // Rapidly cycle random faces to simulate tumbling
    intervalRef.current = setInterval(() => {
      setDice([randomFace(), randomFace()]);
    }, 80);

    // Stop after 900 ms and lock in a final result
    timeoutRef.current = setTimeout(() => {
      if (intervalRef.current) clearInterval(intervalRef.current);
      const final: [number, number] = [randomFace(), randomFace()];
      setDice(final);
      setRolling(false);
      setHasRolled(true);
    }, 900);
  }

  const total = dice[0] + dice[1];

  return (
    <section aria-labelledby="dice-heading">
      <h2 id="dice-heading">Dice Roller</h2>

      <div
        style={{
          display: "flex",
          gap: 24,
          alignItems: "center",
          justifyContent: "center",
          margin: "24px 0",
        }}
      >
        <Die value={dice[0]} rolling={rolling} />
        <Die value={dice[1]} rolling={rolling} />
      </div>

      {hasRolled && !rolling && (
        <p className="result-text">
          {dice[0]} + {dice[1]} = <strong>{total}</strong>
        </p>
      )}

      <button
        onClick={roll}
        disabled={rolling}
        className="primary-btn"
        aria-label={hasRolled ? "Roll dice again" : "Roll dice"}
      >
        {rolling ? "Rolling…" : hasRolled ? "Roll Again" : "Roll Dice"}
      </button>
    </section>
  );
}
