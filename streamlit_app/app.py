"""
Streamlit version of the MADA Demo.

Run locally:
    streamlit run streamlit_app/app.py
"""
from __future__ import annotations

import random
import sys
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

sys.path.insert(0, str(Path(__file__).parent.parent))
from shared.weather_service import WeatherServiceError, get_weather_sync

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="MADA Demo — Streamlit",
    page_icon="🎲",
    layout="centered",
)

st.markdown(
    "<style>h1{color:#4f46e5!important}section.main>div{padding-top:2rem}</style>",
    unsafe_allow_html=True,
)

st.title("🎲 MADA Demo")
st.caption("Streamlit version · Python only, no React")

# ---------------------------------------------------------------------------
# 3-D dice cube — rendered as a self-contained HTML/JS component
# ---------------------------------------------------------------------------

_S   = 96        # cube side length (px)
_H   = _S // 2   # half = 48 (translateZ distance)
_DOT = 15        # dot diameter (px)

_DOTS: dict[int, list[tuple[int, int]]] = {
    1: [(50, 50)],
    2: [(28, 28), (72, 72)],
    3: [(28, 28), (50, 50), (72, 72)],
    4: [(28, 28), (72, 28), (28, 72), (72, 72)],
    5: [(28, 28), (72, 28), (50, 50), (28, 72), (72, 72)],
    6: [(28, 22), (72, 22), (28, 50), (72, 50), (28, 78), (72, 78)],
}

# Standard Western die: 1↔6, 2↔5, 3↔4
_FACE_VALUE = {"front": 1, "back": 6, "right": 2, "left": 5, "top": 3, "bottom": 4}
_FACE_BG = {
    "front":  "linear-gradient(145deg,#ffffff 0%,#f0f0f0 100%)",
    "back":   "linear-gradient(145deg,#d4d4d4 0%,#c4c4c4 100%)",
    "right":  "linear-gradient(145deg,#ebebeb 0%,#dcdcdc 100%)",
    "left":   "linear-gradient(145deg,#e4e4e4 0%,#d4d4d4 100%)",
    "top":    "linear-gradient(145deg,#fafafa 0%,#ebebeb 100%)",
    "bottom": "linear-gradient(145deg,#cccccc 0%,#bcbcbc 100%)",
}
_FACE_XFORM = {
    "front":  f"translateZ({_H}px)",
    "back":   f"rotateY(180deg) translateZ({_H}px)",
    "right":  f"rotateY(90deg) translateZ({_H}px)",
    "left":   f"rotateY(-90deg) translateZ({_H}px)",
    "top":    f"rotateX(-90deg) translateZ({_H}px)",
    "bottom": f"rotateX(90deg) translateZ({_H}px)",
}


def _build_faces() -> str:
    """All 6 faces for one cube — rotation of the container picks the visible value."""
    out = []
    for name, xform in _FACE_XFORM.items():
        value = _FACE_VALUE[name]
        dots = "".join(
            f'<div style="position:absolute;width:{_DOT}px;height:{_DOT}px;'
            f'border-radius:50%;'
            f'background:radial-gradient(circle at 35% 35%,#475569,#0f172a);'
            f'box-shadow:inset 1px 1px 2px rgba(255,255,255,.15),'
            f'0 1px 3px rgba(0,0,0,.35);'
            f'left:{_S*x/100 - _DOT/2:.1f}px;'
            f'top:{_S*y/100  - _DOT/2:.1f}px"></div>'
            for x, y in _DOTS[value]
        )
        out.append(
            f'<div class="face" style="transform:{xform};'
            f'background:{_FACE_BG[name]}">{dots}</div>'
        )
    return "".join(out)


def _dice_component(d1: int, d2: int, roll_count: int) -> None:
    """
    Render two 3-D dice as an HTML/JS iframe component.
    Each new roll_count triggers a smooth rotation to the correct face.
    """
    faces = _build_faces()
    html = f"""<!DOCTYPE html><html><head><style>
*{{box-sizing:border-box;margin:0;padding:0}}
body{{
  background:transparent;
  display:flex;justify-content:center;align-items:center;
  height:180px;overflow:hidden;
}}
.row{{display:flex;gap:48px;align-items:flex-end}}
.wrap{{display:flex;flex-direction:column;align-items:center;gap:14px}}
.scene{{perspective:520px}}
.cube{{
  width:{_S}px;height:{_S}px;
  position:relative;transform-style:preserve-3d;
}}
.face{{
  position:absolute;width:{_S}px;height:{_S}px;
  border-radius:16px;
  box-shadow:
    inset 2px 2px 5px rgba(255,255,255,.7),
    inset -2px -2px 5px rgba(0,0,0,.06);
  backface-visibility:hidden;
}}
.shadow{{
  width:70px;height:8px;border-radius:50%;
  background:rgba(0,0,0,.18);filter:blur(4px);
}}
</style></head><body>
<div class="row">
  <div class="wrap">
    <div class="scene"><div class="cube" id="c1">{faces}</div></div>
    <div class="shadow"></div>
  </div>
  <div class="wrap">
    <div class="scene"><div class="cube" id="c2">{faces}</div></div>
    <div class="shadow"></div>
  </div>
</div>
<script>
// Container rotation [rx,ry] that brings each face value to the front
const SHOW={{1:[0,0],2:[0,-90],3:[90,0],4:[-90,0],5:[0,90],6:[0,180]}};
const vals=[{d1},{d2}];
const rollCount={roll_count};

// Always move forward to the target angle; never snap backwards
function fwd(cur,tgt){{
  const c=((cur%360)+360)%360, t=((tgt%360)+360)%360;
  let d=((t-c)+360)%360;
  if(d<30)d+=360;
  return cur+d;
}}

['c1','c2'].forEach((id,i)=>{{
  const cube=document.getElementById(id);
  const[tRx,tRy]=SHOW[vals[i]];
  if(rollCount===0){{
    // First load — just show the face, no animation
    cube.style.transition='none';
    cube.style.transform=`rotateX(${{tRx}}deg) rotateY(${{tRy}}deg)`;
    return;
  }}
  // Start from a random scrambled orientation
  const sx=90+Math.random()*540, sy=90+Math.random()*540;
  cube.style.transition='none';
  cube.style.transform=`rotateX(${{sx}}deg) rotateY(${{sy}}deg)`;
  cube.getBoundingClientRect(); // force reflow before transition
  cube.style.transition='transform 0.85s cubic-bezier(0.25,0.46,0.45,0.94)';
  cube.style.transform=`rotateX(${{fwd(sx,tRx)}}deg) rotateY(${{fwd(sy,tRy)}}deg)`;
}});
</script>
</body></html>"""
    components.html(html, height=180)


# ---------------------------------------------------------------------------
# Dice Roller section
# ---------------------------------------------------------------------------
st.divider()
st.subheader("🎲 Dice Roller")

if "dice"       not in st.session_state: st.session_state.dice       = (1, 1)
if "roll_count" not in st.session_state: st.session_state.roll_count = 0

_dice_component(*st.session_state.dice, st.session_state.roll_count)

if st.button(
    "Roll Dice" if st.session_state.roll_count == 0 else "Roll Again",
    use_container_width=True,
):
    st.session_state.dice       = (random.randint(1, 6), random.randint(1, 6))
    st.session_state.roll_count += 1
    st.rerun()

if st.session_state.roll_count > 0:
    d1, d2 = st.session_state.dice
    st.markdown(
        f"<div style='text-align:center;margin-top:4px'>"
        f"<span style='font-size:2.6rem;font-weight:800;color:#4f46e5;letter-spacing:-1px'>"
        f"{d1+d2}</span><br>"
        f"<span style='color:#94a3b8;font-size:0.88rem'>{d1} + {d2}</span></div>",
        unsafe_allow_html=True,
    )

# ---------------------------------------------------------------------------
# City Temperature section
# ---------------------------------------------------------------------------
st.divider()
st.subheader("🌡️ City Temperature")

city_input = st.text_input(
    "City name",
    placeholder="e.g. Tokyo",
    label_visibility="collapsed",
)

if st.button("Get Temperature", use_container_width=True):
    if city_input.strip():
        with st.spinner("Fetching weather…"):
            try:
                result = get_weather_sync(city_input.strip())
                st.markdown(
                    f"<div style='text-align:center;padding:16px;background:#f8faff;"
                    f"border:1.5px solid #e0e7ff;border-radius:12px;margin-top:12px'>"
                    f"<div style='font-weight:600;color:#374151;font-size:1.05rem'>"
                    f"{result.city}, {result.country}</div>"
                    f"<div style='font-size:2.8rem;font-weight:700;color:#4f46e5;"
                    f"line-height:1.1;margin:4px 0'>"
                    f"{result.temperature}{result.unit}</div>"
                    f"<div style='color:#64748b;font-size:0.9rem'>"
                    f"{result.condition or ''}</div></div>",
                    unsafe_allow_html=True,
                )
            except WeatherServiceError as exc:
                st.error(str(exc))
            except Exception as exc:
                st.error(f"Unexpected error: {exc}")
    else:
        st.warning("Please enter a city name.")
