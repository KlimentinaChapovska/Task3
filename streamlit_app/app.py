"""
Streamlit version of the MADA Demo.

Run locally:
    streamlit run streamlit_app/app.py
"""

from __future__ import annotations

import random
import sys
import time
from pathlib import Path

import streamlit as st

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

# ---------------------------------------------------------------------------
# Helpers — HTML/CSS dice faces
# ---------------------------------------------------------------------------

_DOT_POS: dict[int, list[tuple[int, int]]] = {
    1: [(50, 50)],
    2: [(28, 28), (72, 72)],
    3: [(28, 28), (50, 50), (72, 72)],
    4: [(28, 28), (72, 28), (28, 72), (72, 72)],
    5: [(28, 28), (72, 28), (50, 50), (28, 72), (72, 72)],
    6: [(28, 22), (72, 22), (28, 50), (72, 50), (28, 78), (72, 78)],
}
_SIZE = 110
_DOT  = 16


def _die_html(value: int) -> str:
    dots = "".join(
        f'<div style="position:absolute;width:{_DOT}px;height:{_DOT}px;'
        f'border-radius:50%;'
        f'background:radial-gradient(circle at 35% 35%,#475569,#0f172a);'
        f'box-shadow:0 1px 3px rgba(0,0,0,.35);'
        f'left:{_SIZE*x/100 - _DOT/2:.1f}px;'
        f'top:{_SIZE*y/100  - _DOT/2:.1f}px;"></div>'
        for x, y in _DOT_POS[value]
    )
    return (
        f'<div style="'
        f'width:{_SIZE}px;height:{_SIZE}px;'
        f'border-radius:18px;'
        f'background:linear-gradient(145deg,#ffffff 0%,#e8ecf0 100%);'
        f'box-shadow:'
        f'  4px 4px 10px rgba(0,0,0,.18),'
        f' -2px -2px  6px rgba(255,255,255,.9),'
        f'  inset 1px 1px 2px rgba(255,255,255,.8),'
        f'  inset -1px -1px 2px rgba(0,0,0,.04);'
        f'position:relative;display:inline-block;'
        f'flex-shrink:0;">'
        f'{dots}</div>'
    )


def _dice_row(d1: int, d2: int, rolling: bool = False) -> str:
    shadow = "0 0 0 3px #6366f1,0 8px 28px rgba(99,102,241,.35)" if rolling else ""
    extra  = f"box-shadow:{shadow};" if shadow else ""
    # wrap each die in a small div so the glow applies per-die
    def wrap(v: int) -> str:
        inner = _die_html(v)
        if not rolling:
            return inner
        # re-render with glow outline
        glow = (
            f'<div style="border-radius:20px;{extra}display:inline-block;">'
            f'{inner}</div>'
        )
        return glow

    return (
        f'<div style="display:flex;gap:40px;justify-content:center;'
        f'align-items:center;margin:28px 0 20px;">'
        f'{wrap(d1)}{wrap(d2)}'
        f'</div>'
    )


# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------
st.title("🎲 MADA Demo")
st.caption("Streamlit version · Python only, no React")

# ---------------------------------------------------------------------------
# Dice Roller
# ---------------------------------------------------------------------------
st.divider()
st.subheader("🎲 Dice Roller")

if "dice" not in st.session_state:
    st.session_state.dice   = (1, 1)
    st.session_state.rolled = False

dice_placeholder = st.empty()
dice_placeholder.markdown(
    _dice_row(*st.session_state.dice),
    unsafe_allow_html=True,
)

if st.button(
    "Roll Dice" if not st.session_state.rolled else "Roll Again",
    use_container_width=True,
):
    # Animate — cycle random faces rapidly
    for _ in range(12):
        r1, r2 = random.randint(1, 6), random.randint(1, 6)
        dice_placeholder.markdown(
            _dice_row(r1, r2, rolling=True),
            unsafe_allow_html=True,
        )
        time.sleep(0.07)

    final = (random.randint(1, 6), random.randint(1, 6))
    st.session_state.dice   = final
    st.session_state.rolled = True
    dice_placeholder.markdown(_dice_row(*final), unsafe_allow_html=True)
    st.rerun()

if st.session_state.rolled:
    d1, d2 = st.session_state.dice
    st.markdown(f"**{d1} + {d2} = {d1 + d2}**")

# ---------------------------------------------------------------------------
# City Temperature
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
                st.metric(
                    label=f"{result.city}, {result.country}",
                    value=f"{result.temperature}{result.unit}",
                )
                if result.condition:
                    st.caption(result.condition)
            except WeatherServiceError as exc:
                st.error(str(exc))
            except Exception as exc:
                st.error(f"Unexpected error: {exc}")
    else:
        st.warning("Please enter a city name.")
