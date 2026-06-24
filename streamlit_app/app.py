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

# Allow importing from shared/ when run from the project root or from streamlit_app/
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

st.title("🎲 MADA Demo")
st.caption("Streamlit version · Python only, no React")

# ---------------------------------------------------------------------------
# Dice Roller
# ---------------------------------------------------------------------------

DOT_CHARS: dict[int, str] = {1: "⚀", 2: "⚁", 3: "⚂", 4: "⚃", 5: "⚄", 6: "⚅"}

st.divider()
st.subheader("🎲 Dice Roller")

if "dice" not in st.session_state:
    st.session_state.dice = (1, 1)
    st.session_state.rolled = False

col_d1, col_d2 = st.columns(2)
with col_d1:
    st.markdown(
        f"<div style='font-size:5rem;text-align:center'>{DOT_CHARS[st.session_state.dice[0]]}</div>",
        unsafe_allow_html=True,
    )
with col_d2:
    st.markdown(
        f"<div style='font-size:5rem;text-align:center'>{DOT_CHARS[st.session_state.dice[1]]}</div>",
        unsafe_allow_html=True,
    )

if st.button("Roll Dice" if not st.session_state.rolled else "Roll Again", use_container_width=True):
    # Animate by cycling rapidly through faces
    placeholder_d1 = col_d1.empty()
    placeholder_d2 = col_d2.empty()

    for _ in range(10):
        r1, r2 = random.randint(1, 6), random.randint(1, 6)
        placeholder_d1.markdown(
            f"<div style='font-size:5rem;text-align:center'>{DOT_CHARS[r1]}</div>",
            unsafe_allow_html=True,
        )
        placeholder_d2.markdown(
            f"<div style='font-size:5rem;text-align:center'>{DOT_CHARS[r2]}</div>",
            unsafe_allow_html=True,
        )
        time.sleep(0.07)

    final = (random.randint(1, 6), random.randint(1, 6))
    st.session_state.dice = final
    st.session_state.rolled = True
    st.rerun()

if st.session_state.rolled:
    d1, d2 = st.session_state.dice
    st.markdown(
        f"**{d1} + {d2} = {d1 + d2}**",
        help="Sum of the two dice",
    )

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

if st.button("Get Temperature", use_container_width=True) or city_input:
    # Only fetch when Enter or button pressed — avoid fetching on every keystroke
    # st.text_input triggers rerun on Enter, so this block runs at the right time.
    if city_input.strip():
        with st.spinner("Fetching weather…"):
            try:
                result = get_weather_sync(city_input.strip())
                st.metric(
                    label=f"{result.city}, {result.country}",
                    value=f"{result.temperature}{result.unit}",
                    help=result.condition or "No condition available",
                )
                if result.condition:
                    st.caption(result.condition)
            except WeatherServiceError as exc:
                st.error(str(exc))
            except Exception as exc:
                st.error(f"Unexpected error: {exc}")
    else:
        st.warning("Please enter a city name.")
