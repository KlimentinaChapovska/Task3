import { useEffect, useRef, useState } from "react";

interface Props {
  value: number;
  rolling: boolean;
}

const DOTS: Record<number, [number, number][]> = {
  1: [[50, 50]],
  2: [[28, 28], [72, 72]],
  3: [[28, 28], [50, 50], [72, 72]],
  4: [[28, 28], [72, 28], [28, 72], [72, 72]],
  5: [[28, 28], [72, 28], [50, 50], [28, 72], [72, 72]],
  6: [[28, 22], [72, 22], [28, 50], [72, 50], [28, 78], [72, 78]],
};

// Standard Western die: 1↔6, 2↔5, 3↔4.
// When face 1 is toward viewer and face 2 is on the right, face 3 is on top.
const FACE_VALUE: Record<string, number> = {
  front: 1, back: 6, right: 2, left: 5, top: 3, bottom: 4,
};

// CSS transform that places each face onto the cube surface
const FACE_XFORM: Record<string, string> = {
  front:  "translateZ(48px)",
  back:   "rotateY(180deg) translateZ(48px)",
  right:  "rotateY(90deg) translateZ(48px)",
  left:   "rotateY(-90deg) translateZ(48px)",
  top:    "rotateX(-90deg) translateZ(48px)",
  bottom: "rotateX(90deg) translateZ(48px)",
};

// Simulated lighting: faces that face top-left are lighter
const FACE_BG: Record<string, string> = {
  front:  "linear-gradient(145deg,#ffffff 0%,#f0f0f0 100%)",
  back:   "linear-gradient(145deg,#d4d4d4 0%,#c4c4c4 100%)",
  right:  "linear-gradient(145deg,#ebebeb 0%,#dcdcdc 100%)",
  left:   "linear-gradient(145deg,#e4e4e4 0%,#d4d4d4 100%)",
  top:    "linear-gradient(145deg,#fafafa 0%,#ebebeb 100%)",
  bottom: "linear-gradient(145deg,#cccccc 0%,#bcbcbc 100%)",
};

// Container rotation [rx, ry] (degrees) that brings each face value to the front
const SHOW: Record<number, [number, number]> = {
  1: [0,    0],
  2: [0,  -90],
  3: [90,   0],
  4: [-90,  0],
  5: [0,   90],
  6: [0,  180],
};

// Return the next cumulative angle that lands on `target`, always moving forward
function forwardTo(current: number, target: number): number {
  const cur  = ((current % 360) + 360) % 360;
  const tgt  = ((target  % 360) + 360) % 360;
  let   diff = ((tgt - cur) + 360) % 360;
  // Never snap less than 30° — always look like it settled properly
  if (diff < 30) diff += 360;
  return current + diff;
}

function DiceFace({ name }: { name: string }) {
  const dots = DOTS[FACE_VALUE[name]];
  return (
    <div
      className="die-face"
      style={{ transform: FACE_XFORM[name], background: FACE_BG[name] }}
    >
      {dots.map(([x, y], i) => (
        <span
          key={i}
          className="die-dot"
          style={{ left: `calc(${x}% - 7.5px)`, top: `calc(${y}% - 7.5px)` }}
        />
      ))}
    </div>
  );
}

export function Die({ value, rolling }: Props) {
  const rafRef     = useRef<number | null>(null);
  const rotRef     = useRef({ rx: 0, ry: 0 });   // cumulative degrees
  const valueRef   = useRef(value);
  const hasRolled  = useRef(false);
  const speedRef   = useRef({ rx: 0, ry: 0 });

  const [cubeTransform, setCubeTransform] = useState("rotateX(0deg) rotateY(0deg)");
  const [cubeTransition, setCubeTransition] = useState("none");

  // Keep valueRef pointing at the current value so the stop-effect can read it
  useEffect(() => { valueRef.current = value; }, [value]);

  useEffect(() => {
    if (rolling) {
      hasRolled.current = true;
      setCubeTransition("none");

      // Each die gets slightly different tumble speeds so they look independent
      speedRef.current = {
        rx: 200 + Math.random() * 140,  // deg/s
        ry: 230 + Math.random() * 110,
      };
      let last = performance.now();

      function frame(now: number) {
        const dt = (now - last) / 1000;
        last = now;
        rotRef.current.rx += speedRef.current.rx * dt;
        rotRef.current.ry += speedRef.current.ry * dt;
        setCubeTransform(
          `rotateX(${rotRef.current.rx}deg) rotateY(${rotRef.current.ry}deg)`
        );
        rafRef.current = requestAnimationFrame(frame);
      }

      rafRef.current = requestAnimationFrame(frame);
      return () => { if (rafRef.current) cancelAnimationFrame(rafRef.current); };

    } else if (hasRolled.current) {
      // Rolling just stopped — smoothly rotate to the correct face
      if (rafRef.current) cancelAnimationFrame(rafRef.current);

      const [tRx, tRy] = SHOW[valueRef.current];
      const finalRx = forwardTo(rotRef.current.rx, tRx);
      const finalRy = forwardTo(rotRef.current.ry, tRy);
      rotRef.current = { rx: finalRx, ry: finalRy };

      setCubeTransition("transform 0.65s cubic-bezier(0.25,0.46,0.45,0.94)");
      setCubeTransform(`rotateX(${finalRx}deg) rotateY(${finalRy}deg)`);
    }
  }, [rolling]);

  return (
    <div className="die-scene" aria-label={`Die showing ${value}`}>
      <div
        className={`die-cube${rolling ? " die-cube--rolling" : ""}`}
        style={{ transform: cubeTransform, transition: cubeTransition }}
      >
        {Object.keys(FACE_XFORM).map((name) => (
          <DiceFace key={name} name={name} />
        ))}
      </div>
      <div className={`die-shadow${rolling ? " die-shadow--up" : ""}`} />
    </div>
  );
}
