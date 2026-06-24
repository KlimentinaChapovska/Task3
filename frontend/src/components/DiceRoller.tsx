import { useState, useRef, useEffect } from "react";
import { Die } from "./Die";

function randomFace() { return Math.floor(Math.random() * 6) + 1; }

export function DiceRoller() {
  const [dice, setDice]           = useState<[number, number]>([1, 1]);
  const [rolling, setRolling]     = useState(false);
  const [showResult, setShowResult] = useState(false);
  const timer1 = useRef<ReturnType<typeof setTimeout> | null>(null);
  const timer2 = useRef<ReturnType<typeof setTimeout> | null>(null);

  useEffect(() => () => {
    if (timer1.current) clearTimeout(timer1.current);
    if (timer2.current) clearTimeout(timer2.current);
  }, []);

  function roll() {
    if (rolling) return;
    setRolling(true);
    setShowResult(false);

    // The cube spins freely for 1.1s, then the final value is locked in and
    // the Die component smoothly rotates to that face (takes ~0.65s).
    // We reveal the result text just after that transition finishes.
    timer1.current = setTimeout(() => {
      const final: [number, number] = [randomFace(), randomFace()];
      setDice(final);    // value prop → Die reads it when rolling stops
      setRolling(false); // triggers Die's face-landing transition

      timer2.current = setTimeout(() => setShowResult(true), 700);
    }, 1100);
  }

  const total = dice[0] + dice[1];
  const hasRolled = showResult;

  return (
    <section aria-labelledby="dice-heading">
      <h2 id="dice-heading">Dice Roller</h2>

      <div className="dice-tray">
        <Die value={dice[0]} rolling={rolling} />
        <Die value={dice[1]} rolling={rolling} />
      </div>

      <div className="result-area">
        {showResult && (
          <div className="result-reveal">
            <span className="result-total">{total}</span>
            <span className="result-breakdown">{dice[0]} + {dice[1]}</span>
          </div>
        )}
      </div>

      <button
        onClick={roll}
        disabled={rolling}
        className="primary-btn roll-btn"
        aria-label={hasRolled ? "Roll dice again" : "Roll dice"}
      >
        {rolling ? "Rolling…" : hasRolled ? "Roll Again" : "Roll Dice"}
      </button>
    </section>
  );
}
