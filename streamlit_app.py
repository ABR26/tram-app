#///Version 3.0 10/4/26 \\\
# /// Version 3.1 –11/04/26 streamlined backend + first/last trams ///

import streamlit as st
from datetime import datetime, time

# ---- Fare model ----
SHORT_HOP_THRESHOLD_MIN = 20
CONTACTLESS_SHORT_HOP = 1.50
MACHINE_SHORT_HOP = 2.00

CONTACTLESS_SINGLE = 3.50
MACHINE_SINGLE = 3.50

CONTACTLESS_DAILY_CAP = 5.65

st.set_page_config(page_title="NET Tram", layout="centered")
st.markdown("<h1 style='color: green;'>Nottingham Tram NET Trip time</h1>", unsafe_allow_html=True)

# --- Mode selector ---
mode = st.radio(
    "Mode",
    ["Trip time calculator", "First & last trams"],
    horizontal=True
)

# ---- Shared helpers ----
def minutes_since_midnight(t: time) -> int:
    return t.hour * 60 + t.minute

def pretty_minutes(m: float) -> str:
    if m != m:  # NaN
        return "N/A"
    return f"{int(m)} minutes" if m.is_integer() else f"{m:.1f} minutes"

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

# ============================================================
# MODE: FIRST & LAST TRAMS (Toton ↔ Hucknall)
# ============================================================
if mode == "First & last trams":

    def to_minutes(t):
        h, m = map(int, t.split(":"))
        return h*60 + m

    def to_hhmm(m):
        m = int(m) % (24*60)
        return f"{m//60:02d}:{m%60:02d}"

    runtime = 63  # minutes end-to-end

    anchors = {
        "south_first_dep": "06:01",
        "south_last_dep":  "01:05",
        "north_first_dep": "06:04",
        "north_last_dep":  "00:15",
    }

    tram_stops = {
        "Toton Lane": 0.00,
        "Beeston Centre": 0.19,
        "QMC": 0.35,
        "NG2": 0.41,
        "Nottingham Station": 0.492,
        "Old Market Square": 0.539,
        "The Forest": 0.66,
        "Wilkinson Street": 0.746,
        "Highbury Vale": 0.84,
        "Bulwell": 0.87,
        "Hucknall": 1.00
    }

    def infer_southbound(r):
        first = to_minutes(anchors["south_first_dep"]) + r * runtime
        last  = to_minutes(anchors["south_last_dep"])  + r * runtime
        return to_hhmm(first), to_hhmm(last)

    def infer_northbound(r):
        first = to_minutes(anchors["north_first_dep"]) + (1 - r) * runtime
        last  = to_minutes(anchors["north_last_dep"])  + (1 - r) * runtime
        return to_hhmm(first), to_hhmm(last)

    st.write("First and last trams")

    stop = st.selectbox("Stop:", list(tram_stops.keys()))
    r = tram_stops[stop]

    sb_first, sb_last = infer_southbound(r)
    nb_first, nb_last = infer_northbound(r)

    st.write(f"Stop: {stop}")
    st.write("Northbound (Toton → Hucknall)")
    st.write(f"First tram: {sb_first}")
    st.write(f"Last tram: {sb_last}")

    st.write("")
    st.write("Southbound (Hucknall → Toton)")
    st.write(f"First tram: {nb_first}")
    st.write(f"Last tram: {nb_last}")

    st.stop()

# ============================================================
# MODE: TRIP TIME CALCULATOR (your existing tool)
# ============================================================
# --- network minutes-to-hub tables ---
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

# --- time windows -> headway mapping ---
TIME_WINDOWS = {
    "01:00-06:00": None,
    "06:00-07:00": 15,
    "07:00-10:00": 7,
    "10:00-15:00": 10,
    "15:00-19:00": 7,
    "19:00-21:00": 10,
    "21:00-01:00": 15,
}

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

def mean_connection_wait_from_headway(headway: int) -> float:
    return headway / 2.0

# --- UI for trip calculator ---
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
            if origin_line == dest_line:
                o2h = NETWORK[origin_line][origin_station]
                d2h = NETWORK[dest_line][dest_station]
                journey_minutes = abs(o2h - d2h)

                st.subheader("Result (same line)")
                st.write(f"- Travel time: **{pretty_minutes(journey_minutes)}**")
                st.write(f"- {origin_station} → {dest_station} on {origin_line}")
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
