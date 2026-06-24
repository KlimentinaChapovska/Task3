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
    page_title="MADA Demo",
    page_icon="🎲",
    layout="centered",
)

# ---------------------------------------------------------------------------
# Global CSS — match the React version's look
# ---------------------------------------------------------------------------
st.markdown("""
<style>
/* ── background ──────────────────────────────────────────────── */
[data-testid="stAppViewContainer"] > .main { background: #f1f5f9; }
[data-testid="stHeader"]  { background: transparent; }
footer, #MainMenu        { display: none !important; }

/* ── card containers (border=True) ───────────────────────────── */
[data-testid="stVerticalBlockBorderWrapper"] {
  border: none !important;
  border-radius: 16px !important;
  background: white !important;
  box-shadow: 0 1px 3px rgba(0,0,0,.07), 0 4px 16px rgba(0,0,0,.06) !important;
  padding: 8px 4px !important;
}

/* ── primary buttons ─────────────────────────────────────────── */
.stButton > button {
  background: #4f46e5 !important;
  color: white !important;
  border: none !important;
  border-radius: 8px !important;
  font-weight: 500 !important;
  transition: background .15s !important;
}
.stButton > button:hover  { background: #4338ca !important; border: none !important; }
.stButton > button:active { background: #3730a3 !important; }
.stButton > button:focus:not(:active) { border: none !important; box-shadow: none !important; }

/* ── text input ──────────────────────────────────────────────── */
.stTextInput input {
  border-radius: 8px !important;
  border: 1.5px solid #d1d5db !important;
  font-size: .95rem !important;
}
.stTextInput input:focus {
  border-color: #6366f1 !important;
  box-shadow: none !important;
}

/* ── column gap ──────────────────────────────────────────────── */
[data-testid="stColumns"] { gap: 24px !important; }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------
st.markdown("""
<div style="text-align:center;padding:32px 0 24px">
  <div style="font-size:2.6rem;font-weight:700;color:#4f46e5;letter-spacing:-.5px">
    MADA Demo
  </div>
  <div style="color:#64748b;margin-top:6px;font-size:.95rem">
    React + FastAPI · Deployment Showcase
  </div>
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# 3-D dice component helpers
# ---------------------------------------------------------------------------
_S, _H, _DOT = 96, 48, 15

_DOTS: dict[int, list[tuple[int, int]]] = {
    1: [(50, 50)],
    2: [(28, 28), (72, 72)],
    3: [(28, 28), (50, 50), (72, 72)],
    4: [(28, 28), (72, 28), (28, 72), (72, 72)],
    5: [(28, 28), (72, 28), (50, 50), (28, 72), (72, 72)],
    6: [(28, 22), (72, 22), (28, 50), (72, 50), (28, 78), (72, 78)],
}
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
    parts = []
    for name, xform in _FACE_XFORM.items():
        v = _FACE_VALUE[name]
        dots = "".join(
            f'<div style="position:absolute;width:{_DOT}px;height:{_DOT}px;'
            f'border-radius:50%;'
            f'background:radial-gradient(circle at 35% 35%,#475569,#0f172a);'
            f'box-shadow:inset 1px 1px 2px rgba(255,255,255,.15),0 1px 3px rgba(0,0,0,.35);'
            f'left:{_S*x/100-_DOT/2:.1f}px;top:{_S*y/100-_DOT/2:.1f}px"></div>'
            for x, y in _DOTS[v]
        )
        parts.append(
            f'<div class="face" style="transform:{xform};background:{_FACE_BG[name]}">'
            f'{dots}</div>'
        )
    return "".join(parts)


def _dice_component(d1: int, d2: int, roll_count: int) -> None:
    faces = _build_faces()
    html = f"""<!DOCTYPE html><html><head><style>
*{{box-sizing:border-box;margin:0;padding:0}}
body{{background:transparent;display:flex;justify-content:center;
      align-items:center;height:160px;overflow:hidden}}
.row{{display:flex;gap:48px;align-items:flex-end}}
.wrap{{display:flex;flex-direction:column;align-items:center;gap:14px}}
.scene{{perspective:520px}}
.cube{{width:{_S}px;height:{_S}px;position:relative;transform-style:preserve-3d}}
.face{{position:absolute;width:{_S}px;height:{_S}px;border-radius:16px;
       box-shadow:inset 2px 2px 5px rgba(255,255,255,.7),
                  inset -2px -2px 5px rgba(0,0,0,.06);
       backface-visibility:hidden}}
.shadow{{width:70px;height:8px;border-radius:50%;
         background:rgba(0,0,0,.18);filter:blur(4px)}}
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
const SHOW={{1:[0,0],2:[0,-90],3:[90,0],4:[-90,0],5:[0,90],6:[0,180]}};
const vals=[{d1},{d2}], rc={roll_count};
function fwd(c,t){{
  const a=((c%360)+360)%360,b=((t%360)+360)%360;
  let d=((b-a)+360)%360; if(d<30)d+=360; return c+d;
}}
['c1','c2'].forEach((id,i)=>{{
  const el=document.getElementById(id),[tRx,tRy]=SHOW[vals[i]];
  if(rc===0){{el.style.cssText='transition:none;transform:rotateX('+tRx+'deg) rotateY('+tRy+'deg)';return;}}
  const sx=90+Math.random()*540,sy=90+Math.random()*540;
  el.style.cssText='transition:none;transform:rotateX('+sx+'deg) rotateY('+sy+'deg)';
  el.getBoundingClientRect();
  el.style.transition='transform .85s cubic-bezier(.25,.46,.45,.94)';
  el.style.transform='rotateX('+fwd(sx,tRx)+'deg) rotateY('+fwd(sy,tRy)+'deg)';
}});
</script></body></html>"""
    components.html(html, height=160)


# ---------------------------------------------------------------------------
# Two-column layout — mirrors the React side-by-side cards
# ---------------------------------------------------------------------------
col_left, col_right = st.columns(2, gap="large")

# ── Dice Roller ─────────────────────────────────────────────────────────────
with col_left:
    with st.container(border=True):
        st.markdown(
            "<div style='font-size:1.2rem;font-weight:600;color:#374151;"
            "margin-bottom:4px'>Dice Roller</div>",
            unsafe_allow_html=True,
        )

        if "dice"       not in st.session_state: st.session_state.dice       = (1, 1)
        if "roll_count" not in st.session_state: st.session_state.roll_count = 0

        _dice_component(*st.session_state.dice, st.session_state.roll_count)

        if st.button(
            "Roll Dice" if st.session_state.roll_count == 0 else "Roll Again",
            use_container_width=True,
            key="roll_btn",
        ):
            st.session_state.dice       = (random.randint(1, 6), random.randint(1, 6))
            st.session_state.roll_count += 1
            st.rerun()

        if st.session_state.roll_count > 0:
            d1, d2 = st.session_state.dice
            st.markdown(
                f"<div style='text-align:center;margin-top:8px'>"
                f"<span style='font-size:2.8rem;font-weight:800;color:#4f46e5;"
                f"letter-spacing:-1px;line-height:1'>{d1+d2}</span><br>"
                f"<span style='color:#94a3b8;font-size:.88rem'>{d1} + {d2}</span>"
                f"</div>",
                unsafe_allow_html=True,
            )

# ── City Temperature ────────────────────────────────────────────────────────
with col_right:
    with st.container(border=True):
        st.markdown(
            "<div style='font-size:1.2rem;font-weight:600;color:#374151;"
            "margin-bottom:4px'>City Temperature</div>",
            unsafe_allow_html=True,
        )

        city = st.text_input(
            "City name",
            placeholder="Enter a city, e.g. London",
            label_visibility="collapsed",
            key="city_input",
        )

        if st.button("Get Temperature", use_container_width=True, key="weather_btn"):
            if city.strip():
                with st.spinner("Fetching weather…"):
                    try:
                        r = get_weather_sync(city.strip())
                        st.markdown(
                            f"<div style='text-align:center;margin-top:12px;padding:20px;"
                            f"background:#f8faff;border:1.5px solid #e0e7ff;"
                            f"border-radius:12px'>"
                            f"<div style='font-weight:600;color:#374151;font-size:1.05rem'>"
                            f"{r.city}, {r.country}</div>"
                            f"<div style='font-size:2.8rem;font-weight:700;color:#4f46e5;"
                            f"line-height:1.1;margin:6px 0'>{r.temperature}{r.unit}</div>"
                            f"<div style='color:#64748b;font-size:.9rem'>"
                            f"{r.condition or ''}</div></div>",
                            unsafe_allow_html=True,
                        )
                    except WeatherServiceError as exc:
                        st.error(str(exc))
                    except Exception as exc:
                        st.error(f"Unexpected error: {exc}")
            else:
                st.warning("Please enter a city name.")
