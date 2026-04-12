#///Version 3.0 10/4/26 \\\
# /// Version 4.0 – Toton + Phoenix integrated backend ///

import streamlit as st
from datetime import datetime, time

st.set_page_config(page_title="NET Tram", layout="centered")
# --- Top-right icon ---
colA, colB, colC = st.columns([1, 1, 1])
with colC:
    st.image("assets/download.jpeg.jpg", width=1200)
    
st.markdown("<h1 style='color: green;'>Nottingham Tram NET App</h1>", unsafe_allow_html=True)

# ===========================================================
# MODE SELECTOR
# ============================================================
mode = st.radio(
    "Mode",
    ["Trip time calculator", "First & last trams","Mini‑Map"],
    horizontal=True
)

# ============================================================
# SHARED HELPERS
# ============================================================
def to_minutes(t):
    h, m = map(int, t.split(":"))
    return h*60 + m

def to_hhmm(m):
    m = int(m) % (24*60)
    return f"{m//60:02d}:{m%60:02d}"

# ============================================================
# LINE DEFINITIONS (UNIFIED BACKEND)
# ============================================================

LINES = {
    "Toton–Hucknall": {
        "runtime": 63,
        "anchors": {
            "south_first_dep": "06:01",   # Toton → Hucknall
            "south_last_dep":  "01:05",
            "north_first_dep": "06:04",   # Hucknall → Toton
            "north_last_dep":  "00:15",
        },
        "ratios": {
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
    },

    "Phoenix–Clifton": {
        "runtime": 46,
        "anchors": {
            "south_first_dep": "06:04",   # Phoenix Park → Clifton South
            "south_last_dep":  "00:15",
            "north_first_dep": "06:02",   # Clifton South → Phoenix Park
            "north_last_dep":  "00:48",
        },
        "ratios": {
            "Phoenix Park": 1.000,
            "Cinderhill": 0.030,
            "Highbury Vale": 0.066,
            "David Lane": 0.087,
            "Basford": 0.110,
            "Wilkinson Street": 0.153,
            "The Forest": 0.310,
            "Old Market Square": 0.435,
            "Nottingham Station": 0.500,
            "Meadows Embankment": 0.610,
            "Compton Acres": 0.740,
            "Clifton Centre": 0.881,
            "Clifton South": 0.000
        }
    }
}

# ============================================================
# INFERENCE ENGINE (UNIFIED)
# ============================================================
def infer_first_last(line_name, stop):
    line = LINES[line_name]
    r = line["ratios"][stop]
    runtime = line["runtime"]
    a = line["anchors"]

    south_first = to_hhmm(to_minutes(a["south_first_dep"]) + r * runtime)
    south_last  = to_hhmm(to_minutes(a["south_last_dep"])  + r * runtime)

    north_first = to_hhmm(to_minutes(a["north_first_dep"]) + (1 - r) * runtime)
    north_last  = to_hhmm(to_minutes(a["north_last_dep"])  + (1 - r) * runtime)

    return south_first, south_last, north_first, north_last

# ============================================================
# MODE: FIRST & LAST TRAMS
# ============================================================
if mode == "First & last trams":

    st.write("First and last trams")

    line_choice = st.selectbox("Line:", list(LINES.keys()))
    stop_choice = st.selectbox("Stop:", list(LINES[line_choice]["ratios"].keys()))

    sb_first, sb_last, nb_first, nb_last = infer_first_last(line_choice, stop_choice)

    st.write(f"Stop: {stop_choice}")
    st.write("Northbound")
    st.write(f"First tram: {sb_first}")
    st.write(f"Last tram: {sb_last}")

    st.write("")
    st.write("Southbound")
    st.write(f"First tram: {nb_first}")
    st.write(f"Last tram: {nb_last}")

    st.stop()

# ============================================================
# MODE: TRIP TIME CALCULATOR (YOUR ORIGINAL TOOL)
# ============================================================

# ---- Fare model ----
SHORT_HOP_THRESHOLD_MIN = 20
CONTACTLESS_SHORT_HOP = 1.50
MACHINE_SHORT_HOP = 2.00
CONTACTLESS_SINGLE = 3.50
MACHINE_SINGLE = 3.50
CONTACTLESS_DAILY_CAP = 5.65

def pretty_minutes(m: float) -> str:
    if m != m:
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

# ---- Network hub tables (unchanged) ----
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

# ---- Headways ----
TIME_WINDOWS = {
    "01:00-06:00": None,
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

def mean_connection_wait_from_headway(headway: int) -> float:
    return headway / 2.0

# ---- Trip calculator UI ----
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
            st.write(f"Time window: {window} — no trams")

        else:
            # Compute mean wait once
            mean_wait = mean_connection_wait_from_headway(headway)

            if origin_line == dest_line:
                # SAME LINE
                o2h = NETWORK[origin_line][origin_station]
                d2h = NETWORK[dest_line][dest_station]

                travel_minutes = abs(o2h - d2h)
                journey_minutes = travel_minutes 

                st.subheader("Result (same line)") 
                st.markdown("---")
                st.markdown(
                f"Time window: {window} — "
                f"Frequency: {'no service' if headway is None else f'every {headway} minutes'}"
                )
                st.write(f"- Journey time: {pretty_minutes(journey_minutes)}")
                st.write(f"- {origin_station} → {dest_station} on {origin_line}")

            else:
                # CROSS LINE
                o2h = NETWORK[origin_line][origin_station]
                d2h = NETWORK[dest_line][dest_station]

                travel_minutes = o2h + d2h
                journey_minutes = travel_minutes + mean_wait

                st.subheader("Result (cross-line)") 
                st.markdown("---")
                st.markdown(
                f"Time window: {window} — "
                f"Frequency: {'no service' if headway is None else f'every {headway} minutes'}"
                )
                st.write(f"Journey time: {pretty_minutes(journey_minutes)}")
                st.write(f"- Mean wait (per connection): {pretty_minutes(mean_wait)}")
                
            # ---- Fare calculation (applies to both same-line & cross-line) ----
            single_fare = estimate_single_fare(journey_minutes, payment_method)
            st.session_state.daily_spend, charged_now = apply_daily_cap(
                st.session_state.daily_spend,
                single_fare,
                payment_method
            )

            st.info(
                f"Single journey fare: £{single_fare:.2f}\n"
                f"Charge for this journey (after cap): £{charged_now:.2f}\n"
                f"Total paid today (NET contactless cap): £{st.session_state.daily_spend:.2f}"
            )
elif mode == "Mini‑Map":

    import base64

    # --- Clifton + Toton only ---
    mini_map_network = {
        "Clifton": NETWORK["Clifton"],
        "Toton": NETWORK["Toton"]
    }



    # --- UI ---
    line = st.selectbox("Choose your line", list(NETWORK.keys()))
    station = st.selectbox("Choose your station", list(NETWORK[line].keys()))

    # --- Compute adjacent stops ---
    stops_sorted = sorted(NETWORK[line].items(), key=lambda x: x[1], reverse=True)
    names = [s[0] for s in stops_sorted]

    idx = names.index(station)

    prev2 = names[idx - 2] if idx >= 2 else None
    prev1 = names[idx - 1] if idx >= 1 else None
    next1 = names[idx + 1] if idx + 1 < len(names) else None
    next2 = names[idx + 2] if idx + 2 < len(names) else None

    # --- Build SVG ---
    svg = """
    <svg xmlns='http://www.w3.org/2000/svg' width='1000' height='200'>
      <rect width='1600' height='300' fill='white' stroke='lightgrey'/>
      <line x1='80' y1='100' x2='920' y2='100' stroke='green' stroke-width='10'/>
    """

    positions = {
        "prev2": 80,
        "prev1": 290,
        "here": 500,
        "next1": 710,
        "next2": 920
    }

    def draw_stop(name, x, highlight=False):
        if not name:
            return ""
        fill = "Purple" if highlight else "Green"
        stroke = "Green" if highlight else "Green"
        return f"""
            <circle cx='{x}' cy='100' r='18' fill='{fill}' stroke='{stroke}' stroke-width='8'/>
            <text x='{x}' y='145' font-size='26' text-anchor='middle'>{name}</text>
        """

    svg += draw_stop(prev2, positions["prev2"])
    svg += draw_stop(prev1, positions["prev1"])
    svg += draw_stop(station, positions["here"], highlight=True)
    svg += draw_stop(next1, positions["next1"])
    svg += draw_stop(next2, positions["next2"])

    svg += "</svg>"

    # --- Encode for stlite ---
    svg_bytes = svg.encode("utf-8")
    b64 = base64.b64encode(svg_bytes).decode("utf-8")
    img_tag = f"<img src='data:image/svg+xml;base64,{b64}'/>"

    st.markdown(img_tag, unsafe_allow_html=True)
            

