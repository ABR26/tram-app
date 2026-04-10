#///Version 3.0 10/4/26 \\\
#///Version 3.0 10/4/26 \\\

# streamlit_simple_crossline.py
# Minimal Streamlit trip time calculator using "origin->hub + dest->hub + mean connection wait" for cross-line trips.
# Run with: streamlit run streamlit_simple_crossline.py

import streamlit as st
from datetime import datetime, time

# ---- Fare model (adjust values to match current NET fares) ----
SHORT_HOP_THRESHOLD_MIN = 20      # minutes
CONTACTLESS_SHORT_HOP = 1.50
MACHINE_SHORT_HOP = 2.00

CONTACTLESS_SINGLE = 3.50        # standard single (over short-hop)
MACHINE_SINGLE = 3.50            # treat as equivalent for now

CONTACTLESS_DAILY_CAP = 5.65     # NET-only daily cap

st.set_page_config(page_title="Simple Tram Trip Time", layout="centered")
st.markdown("<h1 style='color: green;'>Nottingham Tram NET Trip time</h1>", unsafe_allow_html=True)

# --- network minutes-to-hub tables (minutes to central 'Station' hub) ---
CLIFTON = {
    "Clifton South": 21, "Summerwood Lane": 20, "Holy Trinity": 19,
    "Clifton Centre": 16, "Rivergreen": 15, "Southchurch Drive North": 13.5,
    "Ruddington Lane": 11, "Compton Acres": 10, "Wilford Lane": 8,
    "Wilford Village": 4, "Meadows Embankment": 3, "Queens Walk": 1.5, "Station": 0,
}
TOTON = {
    "Toton": 31, "Inham Road": 29, "Eskdale Drive": 27, "Bramcote Lane": 25,
    "Cator Lane": 23, "High Road": 21, "Chilwell Road": 20, "Beeston Centre": 18,
    "Middle Street": 16, "University Boulevard": 14, "University Of Nottingham": 10,
    "QMC": 8, "Gregory Street": 6.5, "NG2": 4, "Meadows Way West": 2.5, "Station": 0,
}
HUCKNALL = {
    "Hucknall": 12, "Butlers Hill": 9, "Moor Bridge": 7, "Bulwell Forest": 5,
    "Bulwell": 3, "Highbury Vale": 1, "David Lane": 0,
}
PHOENIX = {
    "Phoenix": 4, "CinderHill": 2, "Highbury Vale": 1, "David Lane": 0,
}
FOREST = {
    "The Forest": 10, "High School": 8, "Nottingham Trent Uni": 6,
    "Royal Centre": 4, "Old Market Square": 3, "Lace Market": 2, "Station": 0,
}
NOEL = {
    "Noel Street": 2, "The Forest": 0, "Beaconsfield Road": 4,
    "Shipstone Street": 6, "Wilkinson Street": 8,
}
HYSON = {
    "Hyson Green": 2, "The Forest": 0, "Radford Road": 5, "Wilkinson Street": 8,
}
BASFORD = {
    "Basford": 2, "Wilkinson Street": 0, "David Lane": 4,
}

NETWORK = {
    "Clifton": CLIFTON,
    "Toton": TOTON,
    "Hucknall": HUCKNALL,
    "Phoenix": PHOENIX,
    "The Forest": FOREST,
    "Noel Street": NOEL,
    "Hyson Green": HYSON,
    "Basford": BASFORD,
}

# --- time windows -> headway (minutes) mapping (adjust as needed) ---
TIME_WINDOWS = {
    "01:00-06:00": None,        # no service
    "06:00-07:00": 15,
    "07:00-10:00": 7,
    "10:00-15:00": 10,
    "15:00-19:00": 7,
    "19:00-21:00": 10,
    "21:00-01:00": 15,
}

def minutes_since_midnight(t: time) -> int:
    return t.hour * 60 + t.minute

def map_time_to_window(t_min: int) -> str:
    if 60 <= t_min < 360:
        return "01:00-06:00"
    if 360 <= t_min < 420:
        return "06:00-07:00"
    if 420 <= t_min < 600:
        return "07:00-10:00"
    if 600 <= t_min < 900:
        return "10:00-15:00"
    if 900 <= t_min < 1140:
        return "15:00-19:00"
    if 1140 <= t_min < 1260:
        return "19:00-21:00"
    return "21:00-01:00"

# ---- Fare logic ----
def estimate_single_fare(journey_minutes, payment_method):
    if journey_minutes <= SHORT_HOP_THRESHOLD_MIN:
        return CONTACTLESS_SHORT_HOP if payment_method == "contactless" else MACHINE_SHORT_HOP
    return CONTACTLESS_SINGLE if payment_method == "contactless" else MACHINE_SINGLE

def apply_daily_cap(current_total, new_fare, payment_method):
    if payment_method != "contactless":
        return current_total + new_fare, new_fare
    before = current_total
    after = min(before + new_fare, CONTACTLESS_DAILY_CAP)
    return after, after - before

# ---- Helpers ----
def mean_connection_wait_from_headway(headway: int) -> float:
    return headway / 2.0

def pretty_minutes(m: float) -> str:
    if m != m:  # NaN
        return "N/A"
    return f"{int(m)} minutes" if m.is_integer() else f"{m:.1f} minutes"

# --- UI ---
if "daily_spend" not in st.session_state:
    st.session_state.daily_spend = 0.0

payment_method = st.radio(
    "Payment method",
    ["contactless", "machine"],
    horizontal=True
)

col1, col2 = st.columns(2)
with col1:
    origin_line = st.selectbox("Origin line", list(NETWORK.keys()), index=0)
    origin_station = st.selectbox("Origin station", sorted(NETWORK[origin_line].keys()), index=0)
with col2:
    dest_line = st.selectbox("Destination line", list(NETWORK.keys()), index=1)
    dest_station = st.selectbox("Destination station", sorted(NETWORK[dest_line].keys()), index=0)

time_choice = st.radio("Arrival time", ("Now", "Pick time"), index=0)
t = datetime.now().time() if time_choice == "Now" else st.time_input("Pick arrival time")

window = map_time_to_window(minutes_since_midnight(t))
headway = TIME_WINDOWS[window]

if st.button("Calculate trip time"):
    if origin_station not in NETWORK[origin_line]:
        st.error("Origin station not found on selected line.")
    elif dest_station not in NETWORK[dest_line]:
        st.error("Destination station not found on selected line.")
    else:
        if headway is None:
            st.subheader("No service in this time window")
            st.write(f"Time window: **{window}** — no trams")
        else:
            # SAME LINE
            if origin_line == dest_line:
                o2h = NETWORK[origin_line][origin_station]
                d2h = NETWORK[dest_line][dest_station]
                journey_minutes = abs(o2h - d2h)

                st.subheader("Result (same line)")
                st.write(f"- Travel time: **{pretty_minutes(journey_minutes)}**")
                st.write(f"- {origin_station} → {dest_station} on {origin_line}")

            # CROSS LINE
            else:
                o2h = NETWORK[origin_line][origin_station]
                d2h = NETWORK[dest_line][dest_station]
                mean_wait = mean_connection_wait_from_headway(headway)
                journey_minutes = o2h + d2h + mean_wait

                st.subheader("Result (cross-line)")
                st.write(f"- Origin to hub: **{pretty_minutes(o2h)}**")
                st.write(f"- Destination to hub: **{pretty_minutes(d2h)}**")
                st.write(f"- Mean wait: **{pretty_minutes(mean_wait)}**")
                st.subheader(f"Estimated trip time: **{pretty_minutes(journey_minutes)}**")

            # ---- Fare calculation ----
            single_fare = estimate_single_fare(journey_minutes, payment_method)
            st.session_state.daily_spend, charged_now = apply_daily_cap(
                st.session_state.daily_spend,
                single_fare,
                payment_method
            )

            st.info(
                f"Single journey fare: £{single_fare:.2f}\n"
                f"Charged this journey (after cap): £{charged_now:.2f}\n"
                f"Total paid today (NET contactless cap): £{st.session_state.daily_spend:.2f}"
            )

            st.markdown("---")
            st.markdown(
                f"**Time window:** {window} — "
                f"**Frequency:** {'no service' if headway is None else f'every {headway} minutes'}"
            )
            st.caption("Random arrival model: mean wait = headway / 2.")

