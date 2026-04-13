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
    ["Trip time calculator", "First & last trams", "Mini‑Map", "Journey Map",],
    horizontal=True
)
# ============================================================
# SHARED HELPERS
# ============================================================
def to_minutes(t):
    h, m = map(int, t.split(":"))
    return h * 60 + m

def to_hhmm(m):
    m = int(m) % (24 * 60)
    return f"{m // 60:02d}:{m % 60:02d}"
# ============================================================
# LINE DEFINITIONS (UNIFIED BACKEND) FIRST & LAST
# ============================================================

LINES = {
    "Toton–Hucknall": {
        "runtime": 63,
        "anchors": {
            "south_first_dep": "06:01",
            "south_last_dep": "01:05",
            "north_first_dep": "06:04",
            "north_last_dep": "00:15",
        },
        "ratios": {
            "Toton Lane": 0.00, "Inham Road":0.03, "Eskdale Dr":0.063, "Bramcote Ln":0.095, "Cator Ln":0.127, "High Rd":0.1587,
            "Chilwell Rd":0.17,"Beeston Centre": 0.19, "Middle St":0.254, "University Boulevard":0.23, "University Of Nottingham":0.317,
            "QMC": 0.35, "Gregory Street":0.381, "Meadows Way West":0.452, "NG2": 0.41,"Nottingham Station": 0.492, "Lace Market":0.515,
            "Old Market Square": 0.539, "Royal Centre":0.57, "Nottingham Trent Uni":0.603, "High School":0.635, "The Forest": 0.66, 
            "Noel St":0.675, "Beaconsfield St":0.69, "Shipstone St":0.733, "Wilkinson Street": 0.746, "Basford":0.777, "David Lane":0.81, 
            "Highbury Vale": 0.84, "Bulwell": 0.87, "Bulwell Forest":0.873, "Moor Bridge":0.905, "Butlers Hill":0.97, "Hucknall": 1.00, 
        }
    },

    "Phoenix–Clifton": {
        "runtime": 46,
        "anchors": {
            "south_first_dep": "06:04",
            "south_last_dep": "00:15",
            "north_first_dep": "06:02",
            "north_last_dep": "00:48",
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
    south_last = to_hhmm(to_minutes(a["south_last_dep"]) + r * runtime)

    north_first = to_hhmm(to_minutes(a["north_first_dep"]) + (1 - r) * runtime)
    north_last = to_hhmm(to_minutes(a["north_last_dep"]) + (1 - r) * runtime)

    return south_first, south_last, north_first, north_last
# ============================================================
# MODE: Journey Map
# ============================================================    
if mode == "Journey Map":
    st.header("Journey Map")
    # --- Standalone Journey Map Feature ---
    stops = [
        "Toton Lane","Beeston Centre","QMC","NG2","Station","Old Market Sq", "The Forest", "Wilkinson St", "Highbury Vale",
        "Hucknall"
    ]

    start_name = st.selectbox("Choose start stop", stops)
    end_name   = st.selectbox("Choose end stop", stops)

    if st.button("Map My Journey"):

        i1 = stops.index(start_name)
        i2 = stops.index(end_name)

        if i1 > i2:
            i1, i2 = i2, i1

        segment = stops[i1 : i2 + 1]
        st.write("Selected segment:", segment)
        
        spacing = 150
        radius = 10
        y = 50
        total_width = len(segment) * spacing + 100
        svg = "<svg width='{total_width}' height='150' xmlns='http://www.w3.org/2000/svg'>"

        for i in range(len(segment) - 1):
            x1 = i * spacing + 50
            x2 = (i + 1) * spacing + 50
            svg += f"<line x1='{x1}' y1='{y}' x2='{x2}' y2='{y}' stroke='Green' stroke-width='10' />"

        for i, name in enumerate(segment):
            x = i * spacing + 50
            svg += f"<circle cx='{x}' cy='{y}' r='{radius}' fill='Purple' stroke='Green' stroke-width='4' />"
            svg += f"<text x='{x}' y='{y+30}' font-size='18' text-anchor='middle'>{name}</text>"

        svg += "</svg>"

        # MOBILE-FRIENDLY HORIZONTAL SCROLL WRAPPER
        st.markdown(
            f"""
            <div style="overflow-x: auto; white-space: nowrap; padding-bottom: 10px;">
                {svg}
            </div>
            """,
            unsafe_allow_html=True
        )

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
# MODE: TRIP TIME CALCULATOR
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

# ---- Network hub tables ----
HUBS = ["Station", "David Lane"]

CLIFTONPHOENIX = {
    "Clifton South": 0, "Summerwood Lane": 2, "Holy Trinity": 4,
    "Clifton Centre": 5, "Rivergreen": 7, "Southchurch Dr N": 9,
    "Ruddington Lane": 11, "Compton Acres": 12, "Wilford Lane": 13,
    "Wilford Village": 15, "Meadows Embankment": 18, "Queens Walk": 20,
    "Station": 23, "Lace Market": 25, "Old Market Sq": 26, "Royal Centre": 28,
    "Nott Trent Uni": 29, "High School": 31, "The Forest": 32,
    "Hyson Gr Market": 35, "Radford Rd": 37, "Wilkinson St": 39,
    "Basford": 41, "David Lane": 42, "Highbury Vale": 43,
    "Cinderhill": 45, "Phoenix Park": 46
}

TOTONHUCKNALL = {
    "Toton": 0, "Inham Road": 2, "Eskdale Drive": 4, "Bramcote Lane": 6,
    "Cator Lane": 8, "High Road": 10, "Chilwell Road": 12,
    "Beeston Centre": 14.5, "Middle Street": 16,
    "University Boulevard": 18.5, "University Of Nottingham": 20,
    "QMC": 22, "Gregory Street": 24, "NG2": 26, "Meadows Way West": 28.5,
    "Station": 31, "Lace Market": 32.5, "Old Market Sq": 34,
    "Royal Centre": 36, "Nott Trent Uni": 38, "High School": 40,
    "The Forest": 42, "Noel St": 43.25, "Beaconsfield St": 44.5,
    "Shipstone St": 45.75, "Wilkinson St": 47, "Basford": 49,
    "David Lane": 51, "Highbury Vale": 53, "Bulwell": 55,
    "Bulwell Forest": 57, "Moor Bridge": 59, "Butlers Hill": 61,
    "Hucknall": 63
}

NETWORK = {
    "CliftonPhoenix": CLIFTONPHOENIX,
    "TotonHucknall": TOTONHUCKNALL,
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

chosen_hub = st.selectbox("Choose interchange hub", HUBS)

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
            mean_wait = mean_connection_wait_from_headway(headway)

            if origin_line == dest_line:
                o2h = NETWORK[origin_line][origin_station]
                d2h = NETWORK[dest_line][dest_station]
                travel_minutes = abs(o2h - d2h)
                journey_minutes = travel_minutes

                st.subheader("Result (same line)")
                st.markdown("---")
                st.markdown(
                    f"Time window: {window} — "
                    f"Frequency: every {headway} minutes"
                )
                st.write(f"- Journey time: {pretty_minutes(journey_minutes)}")
                st.write(f"- {origin_station} → {dest_station} on {origin_line}")

            else:
                dist_origin = NETWORK[origin_line][origin_station]
                dist_dest = NETWORK[dest_line][dest_station]

                o2h = abs(NETWORK[origin_line][origin_station] - NETWORK[origin_line][chosen_hub])
                d2h = abs(NETWORK[dest_line][dest_station] - NETWORK[dest_line][chosen_hub])

                travel_minutes = o2h + d2h
                journey_minutes = travel_minutes + mean_wait

                st.subheader("Result (cross line)")
                st.markdown("---")
                st.markdown(
                    f"Time window: {window} — every {headway} minutes"
                )
                st.write(f"- Hub used: {chosen_hub}")
                st.write(f"- Journey time: {pretty_minutes(journey_minutes)}")
                st.write(f"- {origin_station} → {chosen_hub} → {dest_station}")
                st.write(f"- Mean wait (per connection): {pretty_minutes(mean_wait)}")

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

    mini_map_network = {
        "Clifton": NETWORK["CliftonPhoenix"],
        "Toton": NETWORK["TotonHucknall"]
    }

    line = st.selectbox("Choose your line", list(NETWORK.keys()))
    station = st.selectbox("Choose your station", list(NETWORK[line].keys()))

    stops_sorted = sorted(NETWORK[line].items(), key=lambda x: x[1], reverse=True)
    names = [s[0] for s in stops_sorted]

    idx = names.index(station)

    prev2 = names[idx - 2] if idx >= 2 else None
    prev1 = names[idx - 1] if idx >= 1 else None
    next1 = names[idx + 1] if idx + 1 < len(names) else None
    next2 = names[idx + 2] if idx + 2 < len(names) else None

    svg = """
    <svg xmlns='http://www.w3.org/2000/svg' width='1000' height='1200'>
      <rect width='1900' height='300' fill='white' stroke='lightgrey'/>
      <line x1='100' y1='100' x2='900' y2='100' stroke='green' stroke-width='25'/>
    """

    positions = {
        "prev2": 100,
        "prev1": 300,
        "here": 500,
        "next1": 700,
        "next2": 900
    }

    def draw_stop(name, x, highlight=False):
        if not name:
            return ""
        fill = "Purple" if highlight else "Green"
        stroke = "Green"
        return f"""
            <circle cx='{x}' cy='100' r='44' fill='{fill}' stroke='{stroke}' stroke-width='14'/>
            <text x='{x}' y='200' font-size='25' text-anchor='middle'>{name}</text>
        """

    svg += draw_stop(prev2, positions["prev2"])
    svg += draw_stop(prev1, positions["prev1"])
    svg += draw_stop(station, positions["here"], highlight=True)
    svg += draw_stop(next1, positions["next1"])
    svg += draw_stop(next2, positions["next2"])

    svg += "</svg>"

    svg_bytes = svg.encode("utf-8")
    b64 = base64.b64encode(svg_bytes).decode("utf-8")
    img_tag = f"<img src='data:image/svg+xml;base64,{b64}'/>"

    st.markdown(img_tag, unsafe_allow_html=True)
