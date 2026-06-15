# VERSION 2.4  15-06-26
import streamlit as st
import pandas as pd

min_gap = 7

# =========================
# Stop reference dictionaries
# =========================

# Hucknall → Toton
StopRefToton = {
    "Hucknall":0,"Butlers Hill":2,"Moor Bridge":5,"Bulwell Forest":7,"Bulwell":8,
    "Highbury Vale North East":10,"David Lane":12,"Basford":13,"Wilkinson Street":15,"Radford Road":17,
    "Hyson Green Market":19,"The Forest":21,"High School":23,"Nottingham Trent University":25,
    "Royal Centre":27,"Old Market Square":28,"Lace Market":30,"Station":32,"Meadows Way West":34,
    "NG2":36,"Gregory Street":38,"QMC":40,"University of Nottingham":42,"University Boulevard":46,
    "Middle Street":48,"Beeston Centre":50,"Chilwell Road":52,"High Road Central College":53,
    "Cator Lane":55,"Bramcote Lane":57,"Eskdale Drive":59,"Inham Road":60,"Toton":63
}

# Toton → Hucknall
StopRefHucknall = {
    "Hucknall":63,"Butlers Hill":61,"Moor Bridge":58,"Bulwell Forest":57,"Bulwell":55,
    "Highbury Vale North East":53,"David Lane":51,"Basford":50,"Wilkinson Street":47,"Shipstone Street":46,"Beaconsfield Street":44,
    "Noel Street":43,"The Forest":42,"High School":40,"Nottingham Trent University":37,
    "Royal Centre":35,"Old Market Square":34,"Lace Market":33,"Station":31,"Meadows Way West":28,
    "NG2":26,"Gregory Street":24,"QMC":22,"University of Nottingham":19,"University Boulevard":16,
    "Middle Street":14,"Beeston Centre":12,"Chilwell Road":10,"High Road Central College":9,
    "Cator Lane":7,"Bramcote Lane":6,"Eskdale Drive":4,"Inham Road":2,"Toton":0
}

# Phoenix Park → Clifton South
StopRefClifton = {
    "Phoenix Park":0,"Cinderhill":1,"Highbury Vale South West":2,"David Lane":4,
    "Basford":5,"Wilkinson Street":8,"Radford Road":10,"Hyson Green Market":12,"The Forest":14,
    "High School":16,"Nottingham Trent University":18,"Royal Centre":20,"Old Market Square":21,
    "Lace Market":23,"Station":25,"Queens Walk":27,"Meadows Embankment":28,"Wilford Village":29,
    "Wilford Lane":32,"Compton Acres":34,"Ruddington Lane":35,"Southchurch Drive North":38,"Rivergreen":39,
    "Clifton Centre":40,"Holy Trinity":43,"Summerwood Lane":45,"Clifton South":46
}

# Clifton South → Phoenix Park
StopRefPhoenix = {
    "Phoenix Park":46,"Cinderhill":44,"Highbury Vale South West":43,"David Lane":42,
    "Basford":41,"Wilkinson Street":39,"Shipstone Street":38,"Beaconsfield Street":36,"Noel Street":34,"The Forest":32,
    "High School":30,"Nottingham Trent University":27,"Royal Centre":25,"Old Market Square":24,
    "Lace Market":23,"Station":21,"Queens Walk":19,"Meadows Embankment":17,"Wilford Village":16,
    "Wilford Lane":13,"Compton Acres":11,"Ruddington Lane":10,"Southchurch Drive North":8,"Rivergreen":6,
    "Clifton Centre":5,"Holy Trinity":3,"Summerwood Lane":1,"Clifton South":0
}

# =========================
# Timetable engines
# =========================

def timetable_hucknall_to_toton(stop, day_type):
    LateStops = {
        "Hucknall":0,"Butlers Hill":2,"Moor Bridge":5,"Bulwell Forest":7,"Bulwell":8,
        "Highbury Vale North East":10,"David Lane":12,"Basford":13,"Wilkinson Street":15,"Radford Road":17,
        "Hyson Green Market":19,"The Forest":21,"High School":23,"Nottingham Trent University":25,
        "Royal Centre":27,"Old Market Square":28,"Lace Market":30,"Station":32
    }

    EarlyStops = {
        "The Forest":21,"High School":2,"Nottingham Trent University":4,
        "Royal Centre":6,"Old Market Square":7,"Lace Market":9,"Station":11,"Meadows Way West":13,
        "NG2":15,"Gregory Street":17,"QMC":19,"University of Nottingham":21,"University Boulevard":25,
        "Middle Street":27,"Beeston Centre":29,"Chilwell Road":31,"High Road Central College":32,
        "Cator Lane":34,"Bramcote Lane":36,"Eskdale Drive":38,"Inham Road":39,"Toton":42
    }

    if day_type == "Weekdays":
        LateStopTime = [1455]
        EarlyStopTime = [316, 331, 345, 355, 370]
        Directory = [364, 420, 599, 900, 1139, 1260, 1440]
        Freq = [15, 7, 10, 7, 10, 15]
    elif day_type == "Saturday":
        LateStopTime = [1440, 1455]
        EarlyStopTime = [316, 331, 345, 355, 370, 385]
        Directory = [364, 426, 606, 1139, 1260, 1440]
        Freq = [15, 10, 7, 10, 15]
    elif day_type == "Sunday":
        LateStopTime = [1380, 1395]
        EarlyStopTime = [316, 331, 345, 355, 370, 385]
        Directory = [364, 420, 1140, 1380]
        Freq = [15, 10, 15]
    else:
        return []

    early_list, normal_list, late_list = [], [], []

    if stop in EarlyStops:
        early_offset = EarlyStops[stop]
        for t in EarlyStopTime:
            early_list.append(t + early_offset)

    normal_offset = StopRefToton[stop]
    for i in range(len(Freq)):
        start = Directory[i]
        end = Directory[i+1]
        step = Freq[i]
        t = start
        while t < end - min_gap:
            normal_list.append(t + normal_offset)
            t += step

    if stop in LateStops:
        late_offset = LateStops[stop]
        for t in LateStopTime:
            late_list.append(t + late_offset)

    SeedList = sorted(early_list + normal_list + late_list)
    return [(t // 60, t % 60) for t in SeedList]


def timetable_toton_to_hucknall(stop, day_type):
    EarlyStops = {
        "Hucknall":32,"Butlers Hill":30,"Moor Bridge":27,"Bulwell Forest":26,"Bulwell":24,
        "Highbury Vale North East":22,"David Lane":20,"Basford":19,"Wilkinson Street":16,"Shipstone Street":15,"Beaconsfield Street":13,
        "Noel Street":12,"The Forest":11,"High School":9,"Nottingham Trent University":6,
        "Royal Centre":4,"Old Market Square":3,"Lace Market":2,"Station":0
    }

    LateStops = {
        "Wilkinson Street":47,"Shipstone Street":46,"Beaconsfield Street":44,
        "Noel Street":43,"The Forest":42,"High School":40,"Nottingham Trent University":37,
        "Royal Centre":35,"Old Market Square":34,"Lace Market":33,"Station":31,"Meadows Way West":28,
        "NG2":26,"Gregory Street":24,"QMC":22,"University of Nottingham":19,"University Boulevard":16,
        "Middle Street":14,"Beeston Centre":12,"Chilwell Road":10,"High Road Central College":9,
        "Cator Lane":7,"Bramcote Lane":6,"Eskdale Drive":4,"Inham Road":2,"Toton":0
    }

    if day_type == "Weekdays":
        LateStopTime = [1460,1476,1490,1505]
        EarlyStopTime = [360,375,392]
        Directory = [361,421,615,908,1155,1265,1445]
        Freq = [15,7,10,7,10,15]
    elif day_type == "Saturday":
        EarlyStopTime = [360,375]
        LateStopTime = [1445,1460,1476,1490,1505]
        Directory = [361,421,601,1155,1275,1445]
        Freq = [15,10,7,10,15]
    elif day_type == "Sunday":
        LateStopTime = [1385,1400,1415,1430,1445]
        EarlyStopTime = [360,375,392]
        Directory = [361,425,1145,1375]
        Freq = [15,10,15]
    else:
        return []

    early_list, normal_list, late_list = [], [], []

    if stop in EarlyStops:
        early_offset = EarlyStops[stop]
        for t in EarlyStopTime:
            early_list.append(t + early_offset)

    normal_offset = StopRefHucknall[stop]
    for i in range(len(Freq)):
        start = Directory[i]
        end = Directory[i+1]
        step = Freq[i]
        t = start
        while t < end - min_gap:
            normal_list.append(t + normal_offset)
            t += step

    if stop in LateStops:
        late_offset = LateStops[stop]
        for t in LateStopTime:
            late_list.append(t + late_offset)

    SeedList = sorted(early_list + normal_list + late_list)
    return [(t // 60, t % 60) for t in SeedList]


def timetable_phoenix_to_clifton(stop, day_type):
    LateStops = {
        "Phoenix Park":0,"Cinderhill":1,"Highbury Vale South West":2,"David Lane":4,
        "Basford":5,"Wilkinson Street":8,"Radford Road":10,"Hyson Green Market":12,"The Forest":14,
        "High School":16,"Nottingham Trent University":18,"Royal Centre":20,"Old Market Square":21,
        "Lace Market":23,"Station":25
    }

    EarlyStops = {
        "The Forest":0,"High School":2,"Nottingham Trent University":4,"Royal Centre":6,
        "Old Market Square":7,"Lace Market":9,"Station":11,"Queens Walk":13,"Meadows Embankment":14,
        "Wilford Village":15,"Wilford Lane":18,"Compton Acres":20,"Ruddington Lane":21,"Southchurch Drive North":24,
        "Rivergreen":25,"Clifton Centre":26,"Holy Trinity":29,"Summerwood Lane":31,"Clifton South":32
    }

    if day_type == "Weekdays":
        LateStopTime = [1440,1455]
        EarlyStopTime = [327,342,356,363]
        Directory = [364,420,559,900,1139,1260,1440]
        Freq = [15,7,10,7,10,15]
    elif day_type == "Saturday":
        EarlyStopTime = [327,342,356,363,378]
        LateStopTime = [1440,1455]
        Directory = [364,438,617,1150,1262,1440]
        Freq = [15,10,7,10,15]
    elif day_type == "Sunday":
        LateStopTime = [1380, 1395]
        EarlyStopTime = [327,342,356,363,378]
        Directory = [364,422,1142,1380]
        Freq = [15,10,15]
    else:
        return []

    early_list, normal_list, late_list = [], [], []

    if stop in EarlyStops:
        early_offset = EarlyStops[stop]
        for t in EarlyStopTime:
            early_list.append(t + early_offset)

    normal_offset = StopRefClifton[stop]
    for i in range(len(Freq)):
        start = Directory[i]
        end = Directory[i+1]
        step = Freq[i]
        t = start
        while t < end - min_gap:
            normal_list.append(t + normal_offset)
            t += step

    if stop in LateStops:
        late_offset = LateStops[stop]
        for t in LateStopTime:
            late_list.append(t + late_offset)

    SeedList = sorted(early_list + normal_list + late_list)
    return [(t // 60, t % 60) for t in SeedList]


def timetable_clifton_to_phoenix(stop, day_type):
    LateStops = {
        "Shipstone Street":38,"Beaconsfield Street":36,"Noel Street":34,"The Forest":32,
        "High School":30,"Nottingham Trent University":27,"Royal Centre":25,"Old Market Square":24,
        "Lace Market":23,"Station":21,"Queens Walk":19,"Meadows Embankment":17,"Wilford Village":16,
        "Wilford Lane":13,"Compton Acres":11,"Ruddington Lane":10,"Southchurch Drive North":8,"Rivergreen":6,
        "Clifton Centre":5,"Holy Trinity":3,"Summerwood Lane":1,"Clifton South":0
    }

    EarlyStops = {
        "Phoenix Park":25,"Cinderhill":23,"Highbury Vale South West":22,"David Lane":21,
        "Basford":20,"Wilkinson Street":18,"Shipstone Street":17,"Beaconsfield Street":15,"Noel Street":13,"The Forest":11,
        "High School":9,"Nottingham Trent University":6,"Royal Centre":4,"Old Market Square":3,
        "Lace Market":2,"Station":0
    }

    if day_type == "Weekdays":
        LateStopTime = [1463,1473,1508]
        EarlyStopTime = [368]
        Directory = [364,420,559,900,1139,1260,1440]
        Freq = [15,7,10,7,10,15]
    elif day_type == "Saturday":
        EarlyStopTime = [368,383]
        LateStopTime = [1448,1463,1473,1488]
        Directory = [362,425,606,1141,1266,1448]
        Freq = [15,10,7,10,15]
    elif day_type == "Sunday":
        LateStopTime = [1388,1403,1413,1428]
        EarlyStopTime = [368,383]
        Directory = [362,421,1131,1388]
        Freq = [15,10,15]
    else:
        return []

    early_list, normal_list, late_list = [], [], []

    if stop in EarlyStops:
        early_offset = EarlyStops[stop]
        for t in EarlyStopTime:
            early_list.append(t + early_offset)

    normal_offset = StopRefPhoenix[stop]
    for i in range(len(Freq)):
        start = Directory[i]
        end = Directory[i+1]
        step = Freq[i]
        t = start
        while t < end - min_gap:
            normal_list.append(t + normal_offset)
            t += step

    if stop in LateStops:
        late_offset = LateStops[stop]
        for t in LateStopTime:
            late_list.append(t + late_offset)

    SeedList = sorted(early_list + normal_list + late_list)
    return [(t // 60, t % 60) for t in SeedList]

# =========================
# 1. FULL TIMETABLES MODE – FIRST TOOL
# =========================

def run_timetable_mode():
    st.subheader("Full Timetables")

    route = st.radio(
        "Select a route:",
        [
            "Hucknall → Toton Lane",
            "Toton Lane → Hucknall",
            "Phoenix Park → Clifton South",
            "Clifton South → Phoenix Park"
        ],
        key="route_selector"
    )

    day_type = st.radio(
        "Select day type:",
        ["Weekdays", "Saturday", "Sunday"],
        horizontal=True,
        key="timetable_day_type"
    )

    if route == "Hucknall → Toton Lane":
        stop = st.selectbox(
            "Choose your stop:",
            list(StopRefToton.keys()),
            key="timetable_stop_toton"
        )
    elif route == "Toton Lane → Hucknall":
        stop = st.selectbox(
            "Choose your stop:",
            list(StopRefHucknall.keys()),
            key="timetable_stop_hucknall"
        )
    elif route == "Phoenix Park → Clifton South":
        stop = st.selectbox(
            "Choose your stop:",
            list(StopRefClifton.keys()),
            key="timetable_stop_clifton"
        )
    else:
        stop = st.selectbox(
            "Choose your stop:",
            list(StopRefPhoenix.keys()),
            key="timetable_stop_phoenix"
        )

    if st.button("Generate Timetable", key="generate_timetable") and stop is not None:
        if route == "Hucknall → Toton Lane":
            timetable = timetable_hucknall_to_toton(stop, day_type)
        elif route == "Toton Lane → Hucknall":
            timetable = timetable_toton_to_hucknall(stop, day_type)
        elif route == "Phoenix Park → Clifton South":
            timetable = timetable_phoenix_to_clifton(stop, day_type)
        else:
            timetable = timetable_clifton_to_phoenix(stop, day_type)

        formatted = [f"{h:02d}:{m:02d}" for h, m in timetable]
        df = pd.DataFrame({"Arrival Time": formatted})

        st.success(f"Timetable for **{stop}** on **{route}** ({day_type})")
        st.table(df)

# =========================================================
# 2. NEXT TRAM (GTFS-STYLE) MODE – SECOND TOOL
# =========================================================

StopSeed = {
    "Toton":0,"Inham Road":2,"Eskdale Drive":4,"Bramcote Lane":6,"Cator lane":7,
    "High Road Central College":9,"Chilwell Road":10,"Beeston Centre":12,"Middle Street":14,
    "University Boulevard":16,"University of Nottingham":20,"QMC":22,"Gregory Street":24,"NG2":26,
    "Meadows Way West":28,"Station":31,"Lace Market":33,"Old Market Square":34,"Royal Centre":35,
    "Nottingham Trent University":37,"High School":40,"The Forest":42,"Noel Street":43,"Beaconsfield Street":44,
    "Shipstone Street":46,"Wilkinson St":47,"Basford":50,"David Lane":51,"Highbury Vale North East":53,"Bulwell":55,
    "Bulwell Forest":57,"Moor Bridge":58,"Butlers Hill":61,"Hucknall":63
}

StopSeedEarly = {
    "Station":0,"Lace Market":2,"Old Market Sq":3,"Royal Centre":4,
    "Nottingham Trent University":6,"High School":9,"The Forest":11,"Noel Street":12,"Beaconsfield Street":13,
    "Shipstone Street":15,"Wilkinson St":16,"Basford":19,"David Lane":20,"Highbury Vale North East":22,"Bulwell":24,
    "Bulwell Forest":26,"Moor Bridge":28,"Butlers Hill":30,"Hucknall":32
}

StopSeedLate = {
    "Toton":0,"Inham Road":2,"Eskdale Drive":4,"Bramcote Lane":6,"Cator lane":7,
    "High Road Central College":9,"Chilwell Road":10,"Beeston Centre":12,"Middle Street":14,
    "University Boulevard":16,"University of Nottingham":20,"QMC":22,"Gregory Street":24,"NG2":26,
    "Meadows Way West":28,"Station":31,"Lace Market":33,"Old Market Square":34,"Royal Centre":35,
    "Nottingham Trent University":37,"High School":40,"The Forest":42,"Noel Street":43,"Beaconsfield Street":44,
    "Shipstone Street":46
}

StopSeed2 = {
    "Hucknall":0,"Butlers Hill":2,"Moor Bridge":5,"Bulwell Forest":7,"Bulwell":8,
    "Highbury Vale North East":10,"David Lane":12,"Basford":13,"Wilkinson St":16,"Radford Road":17,
    "Hyson Green Market":19,"The Forest":21,"High School":23,"Nottingham Trent University":25,
    "Royal Centre":27,"Old Market Square":28,"Lace Market":30,"Station":32,"Meadows Way West":34,
    "NG2":36,"Gregory Street":38,"QMC":40,"University of Nottingham":42,"University Boulevard":46,
    "Middle Street":48,"Beeston Centre":50,"Chilwell Road":52,"High Road Central College":53,
    "Cator Lane":55,"Bramcote Lane":57,"Eskdale Drive":59,"Inham Road":60,"Toton":63
}

StopSeedEarly2 = {
    "The Forest":0,"High School":2,"Nottingham Trent Uni":4,
    "Royal Centre":6,"Old Market Square":7,"Lace Market":8,"Station":11,"Meadows Way West":13,
    "NG2":15,"Gregory Street":17,"QMC":19,"University of Nottingham":22,"University Boulevard":24,
    "Middle Street":27,"Beeston Centre":29,"Chilwell Road":31,"High Road Central College":32,
    "Cator Lane":34,"Bramcote Lane":36,"Eskdale Drive":38,"Inham Road":40,"Toton":42
}

StopSeedLate2 = {
    "Hucknall":0,"Butlers Hill":2,"Moor Bridge":5,"Bulwell Forest":7,"Bulwell":8,
    "Highbury Vale North East":10,"David Lane":12,"Basford":13,"Wilkinson St":16,"Radford Road":17,
    "Hyson Green Market":19,"The Forest":21,"High School":23,"Notingham Trent Uni":25,
    "Royal Centre":27,"Old Market Sq":28,"Lace Market":30,"Station":32
}

StopSeed3 = {
    "Phoenix":0,"Cinderhill":1,"Highbury Vale South West":2,"David Lane":4,"Basford":5,
    "Wilkinson Street":8,"Radford Road":10,"Hyson Green Market":12,"The Forest":14,"High School":16,
    "Nottingham Trent University":18,"Royal Centre":20,"Old Market Square":21,"Lace Market":22,"Station":25,
    "Queens Walk":27,"Meadows Embankment":28,"Wilford Village":29,"Wilford Lane":32,
    "Compton Acres":34,"Ruddington Lane":35,"Southchurch Drive North":38,"Rivergreen":39,
    "Clifton Centre":40,"Holy Trinity":43,"Summerwood Lane":44,"Clifton South":46
}

StopSeedEarly3 = {
    "Wilkinson Street":8,"Radford Road":2,"Hyson Green Market":4,"The Forest":6,"High School":8,
    "Nottingham Trent University":10,"Royal Centre":13,"Old Market Square":14,"Lace Market":14,
    "Station":17,"Queens Walk":19,"Meadows Embankment":20,"Wilford Village":21,"Wilford Lane":24,
    "Compton Acres":26,"Ruddington Lane":27,"Southchurch Drive North":30,"Rivergreen":31,
    "Clifton Centre":32,"Holy Trinity":35,"Summerwood Lane":36,"Clifton South":38
}

StopSeedLate3 = {
    "Phoenix":0,"Cinderhill":1,"Highbury Vale South West":2,"David Lane":4,"Basford":5,
    "Wilkinson Street":8,"Radford Road":10,"Hyson Green Market":12,"The Forest":14,"High School":16,
    "Nottingham Trent University":18,"Royal Centre":20,"Old Market Square":21,"Lace Market":22,"Station":25
}

StopSeed4 = {
    "Phoenix":46,"Cinderhill":44,"Highbury Vale South West":43,"David Lane":42,"Basford":41,
    "Wilkinson Street":39,"Shipstone Street":38,"Beaconsfield Street":36,"Noel Street":34,"The Forest":32,
    "High School":30,"Nottingham Trent University":27,"Royal Centre":25,"Old Market Square":24,"Lace Market":23,
    "Station":21,"Queens Walk":19,"Meadows Embankment":18,"Wilford Village":16,"Wilford Lane":13,
    "Compton Acres":11,"Ruddington Lane":10,"Southchurch Drive North":7,"Rivergreen":6,
    "Clifton Centre":5,"Holy Trinity":3,"Summerwood Lane":1,"Clifton South":0
}

StopSeedEarly4 = {
    "Phoenix":25,"Cinderhill":23,"Highbury Vale South West":22,"David Lane":21,"Basford":20,
    "Wilkinson Street":18,"Shipstone Street":17,"Beaconsfield Street":15,"Noel Street":13,"The Forest":11,
    "High School":9,"Nottingham Trent University":6,"Royal Centre":4,"Old Market Square":3,"Lace Market":2,
    "Station":0
}

StopSeedLate4 = {
    "The Forest":32,"High School":30,"Nottingham Trent University":27,"Royal Centre":25,"Old Market Square":24,
    "Lace Market":23,"Station":21,"Queens Walk":19,"Meadows Embankment":18,"Wilford Village":16,
    "Wilford Lane":13,"Compton Acres":11,"Ruddington Lane":10,"Southchurch Drive North":7,
    "Rivergreen":6,"Clifton Centre":5,"Holy Trinity":3,"Summerwood Lane":1,"Clifton South":0
}

def fmt(t: int) -> str:
    return f"{t//60:02d}:{t%60:02d}"

def run_next_tram_mode():
    st.subheader("Next Tram (GTFS-style)")

    day_type = st.radio(
        "Select day type:",
        ["Weekdays", "Saturday", "Sunday"],
        horizontal=True,
        key="nexttram_day_type"
    )

    time_input = st.time_input("Enter time", key="nexttram_time")
    ChosenTime = time_input.hour * 60 + time_input.minute

    all_stops = sorted(set(
        list(StopSeed.keys()) +
        list(StopSeed2.keys()) +
        list(StopSeed3.keys()) +
        list(StopSeed4.keys())
    ))

    ChosenStop = st.selectbox("Choose your stop", all_stops, key="nexttram_stop")

    if day_type == "Weekdays":
        TimeEarly = [360,375,392]
        TimeLate = [1460,1476,1490,1505]
        TimeBracket = [361,421,615,908,1155,1265,1445]
        Freq = [15,7,10,7,10,15]

        TimeEarly2 = [316,331,345,355,370]
        TimeLate2 = [1440,1455]
        TimeBracket2 = [364,420,599,900,1139,1260,1440]
        Freq2 = [15,7,10,7,10,15]

        TimeEarly3 = [327,342,356,363]
        TimeLate3 = [1440,1455]
        TimeBracket3 = [364,420,610,900,1139,1260,1440]
        Freq3 = [15,7,10,7,10,15]

        TimeEarly4 = [368]
        TimeLate4 = [1463,1473,1508]
        TimeBracket4 = [364,420,601,900,1139,1260,1440]
        Freq4 = [15,7,10,7,10,15]

    elif day_type == "Saturday":
        TimeEarly = [360,375,392]
        TimeLate = [1445,1460,1476,1490,1505]
        TimeBracket = [361,421,601,1155,1275,1445]
        Freq = [15,10,7,10,15]

        TimeEarly2 = [316,331,345,355,370,385]
        TimeLate2 = [1440,1455]
        TimeBracket2 = [364,426,606,1139,1260,1440]
        Freq2 = [15,10,7,10,15]

        TimeEarly3 = [327,342,356,363,378]
        TimeLate3 = [1440,1455]
        TimeBracket3 = [364,438,617,1150,1262,1440]
        Freq3 = [15,10,7,10,15]

        TimeEarly4 = [368,383]
        TimeLate4 = [1448,1463,1473,1488]
        TimeBracket4 = [362,425,606,1141,1266,1448]
        Freq4 = [15,10,7,10,15]

    else:
        TimeEarly = [360,375,392]
        TimeLate = [1385,1400,1415,1430,1445]
        TimeBracket = [361,425,1145,1375]
        Freq = [15,10,15]

        TimeEarly2 = [316,331,345,355,370,385]
        TimeLate2 = [1380,1395]
        TimeBracket2 = [364,420,1140,1380]
        Freq2 = [15,10,15]

        TimeEarly3 = [327,342,356,363,378]
        TimeLate3 = [1380,1395]
        TimeBracket3 = [364,422,1142,1380]
        Freq3 = [15,10,15]

        TimeEarly4 = [368,383]
        TimeLate4 = [1388,1403,1413,1428]
        TimeBracket4 = [362,421,1131,1388]
        Freq4 = [15,10,15]

    if st.button("Show All Trams", key="show_trams"):

        # HUCKNALL DIRECTION (Toton → Hucknall)
        st.header("For Hucknall")

        for i in range(len(TimeBracket) - 1):
            if TimeBracket[i] <= ChosenTime < TimeBracket[i+1] and ChosenStop in StopSeed:
                SeedTime = ChosenTime - StopSeed[ChosenStop]
                WindowDelta = SeedTime - TimeBracket[i]
                Remainder = WindowDelta % Freq[i]
                ttnt = abs(Remainder - Freq[i])
                NextTram = ChosenTime + ttnt
                st.write("Next tram:", fmt(NextTram))
                if NextTram < int(TimeBracket[i+1]):
                    NextTram2 = NextTram + Freq[i]
                    st.write("2nd:", fmt(NextTram2))
                    if NextTram2 < int(TimeBracket[i+1]):
                        NextTram3 = NextTram2 + Freq[i]
                        st.write("3rd:", fmt(NextTram3))

            if ChosenTime < int(TimeBracket[i]) and ChosenStop in StopSeedEarly:
                for j in range(len(TimeEarly) - 1):
                    if TimeEarly[j] <= ChosenTime < TimeEarly[j+1]:
                        NextTram = int(TimeEarly[j+1] + StopSeedEarly[ChosenStop])
                        st.write("Next early tram:", fmt(NextTram))
                        break
                    elif ChosenTime < int(TimeEarly[j]):
                        NextTram = int(TimeEarly[j] + StopSeedEarly[ChosenStop])
                        st.write("First tram:", fmt(NextTram))
                        break
                break

            if ChosenTime > int(TimeBracket[-1]) and ChosenStop in StopSeedLate:
                for k in range(len(TimeLate) - 1):
                    if TimeLate[k] <= ChosenTime < TimeLate[k+1]:
                        NextTram = int(TimeLate[k+1] + StopSeedLate[ChosenStop])
                        st.write("Next late tram:", fmt(NextTram))
                        break
                    elif ChosenTime > int(TimeLate[-1]):
                        NextTram = int(TimeLate[-1] + StopSeedLate[ChosenStop])
                        st.write("Final tram:", fmt(NextTram))
                        break
                break

        # TOTON DIRECTION (Hucknall → Toton)
        st.header("For Toton Lane")

        for l in range(len(TimeBracket2) - 1):
            if TimeBracket2[l] <= ChosenTime < TimeBracket2[l+1] and ChosenStop in StopSeed2:
                SeedTime = ChosenTime - StopSeed2[ChosenStop]
                WindowDelta = SeedTime - TimeBracket2[l]
                Remainder = WindowDelta % Freq2[l]
                ttnt = abs(Remainder - Freq2[l])
                NextTram = ChosenTime + ttnt
                st.write("Next tram:", fmt(NextTram))
                if NextTram < int(TimeBracket2[l+1]):
                    NextTram2 = NextTram + Freq2[l]
                    st.write("2nd:", fmt(NextTram2))
                    if NextTram2 < int(TimeBracket2[l+1]):
                        NextTram3 = NextTram2 + Freq2[l]
                        st.write("3rd:", fmt(NextTram3))

            if ChosenTime < int(TimeBracket2[l]) and ChosenStop in StopSeedEarly2:
                for m in range(len(TimeEarly2) - 1):
                    if TimeEarly2[m] <= ChosenTime < TimeEarly2[m+1]:
                        NextTram = int(TimeEarly2[m+1] + StopSeedEarly2[ChosenStop])
                        st.write("Next early tram:", fmt(NextTram))
                        break
                    elif ChosenTime < int(TimeEarly2[m]):
                        NextTram = int(TimeEarly2[m] + StopSeedEarly2[ChosenStop])
                        st.write("First tram:", fmt(NextTram))
                        break
                break

            if ChosenTime > int(TimeBracket2[-1]) and ChosenStop in StopSeedLate2:
                for n in range(len(TimeLate2) - 1):
                    if TimeLate2[n] <= ChosenTime < TimeLate2[n+1]:
                        NextTram = int(TimeLate2[n+1] + StopSeedLate2[ChosenStop])
                        st.write("Next late tram:", fmt(NextTram))
                        break
                    elif ChosenTime > int(TimeLate2[-1]):
                        NextTram = int(TimeLate2[-1] + StopSeedLate2[ChosenStop])
                        st.write("Final tram:", fmt(NextTram))
                        break
                break

        # CLIFTON SOUTH DIRECTION (Phoenix → Clifton)
        st.header("For Clifton South")

        for O in range(len(TimeBracket3) - 1):
            if TimeBracket3[O] <= ChosenTime < TimeBracket3[O+1] and ChosenStop in StopSeed3:
                SeedTime = ChosenTime - StopSeed3[ChosenStop]
                WindowDelta = SeedTime - TimeBracket3[O]
                Remainder = WindowDelta % Freq3[O]
                ttnt = abs(Remainder - Freq3[O])
                NextTram = ChosenTime + ttnt
                st.write("Next tram:", fmt(NextTram))
                if NextTram < int(TimeBracket3[O+1]):
                    NextTram2 = NextTram + Freq3[O]
                    st.write("2nd:", fmt(NextTram2))
                    if NextTram2 < int(TimeBracket3[O+1]):
                        NextTram3 = NextTram2 + Freq3[O]
                        st.write("3rd:", fmt(NextTram3))

            if ChosenTime < int(TimeBracket3[O]) and ChosenStop in StopSeedEarly3:
                for p in range(len(TimeEarly3) - 1):
                    if TimeEarly3[p] <= ChosenTime < TimeEarly3[p+1]:
                        NextTram = int(TimeEarly3[p+1] + StopSeedEarly3[ChosenStop])
                        st.write("Next early tram:", fmt(NextTram))
                        break
                    elif ChosenTime < int(TimeEarly3[p]):
                        NextTram = int(TimeEarly3[p] + StopSeedEarly3[ChosenStop])
                        st.write("First tram:", fmt(NextTram))
                        break
                break

            if ChosenTime > int(TimeBracket3[-1]) and ChosenStop in StopSeedLate3:
                for q in range(len(TimeLate3) - 1):
                    if TimeLate3[q] <= ChosenTime < TimeLate3[q+1]:
                        NextTram = int(TimeLate3[q+1] + StopSeedLate3[ChosenStop])
                        st.write("Next late tram:", fmt(NextTram))
                        break
                    elif ChosenTime > int(TimeLate3[-1]):
                        NextTram = int(TimeLate3[-1] + StopSeedLate3[ChosenStop])
                        st.write("Final tram:", fmt(NextTram))
                        break
                break

        # PHOENIX PARK DIRECTION (Clifton → Phoenix)
        st.header("For Phoenix Park")

        for r in range(len(TimeBracket4) - 1):
            if TimeBracket4[r] <= ChosenTime < TimeBracket4[r+1] and ChosenStop in StopSeed4:
                SeedTime = ChosenTime - StopSeed4[ChosenStop]
                WindowDelta = SeedTime - TimeBracket4[r]
                Remainder = WindowDelta % Freq4[r]
                ttnt = abs(Remainder - Freq4[r])
                NextTram = ChosenTime + ttnt
                st.write("Next tram:", fmt(NextTram))
                if NextTram < int(TimeBracket4[r+1]):
                    NextTram2 = NextTram + Freq4[r]
                    st.write("2nd:", fmt(NextTram2))
                    if NextTram2 < int(TimeBracket4[r+1]):
                        NextTram3 = NextTram2 + Freq4[r]
                        st.write("3rd:", fmt(NextTram3))

            if ChosenTime < int(TimeBracket4[r]) and ChosenStop in StopSeedEarly4:
                for s in range(len(TimeEarly4) - 1):
                    if TimeEarly4[s] <= ChosenTime < TimeEarly4[s+1]:
                        NextTram = int(TimeEarly4[s+1] + StopSeedEarly4[ChosenStop])
                        st.write("Next early tram:", fmt(NextTram))
                        break
                    elif ChosenTime < int(TimeEarly4[s]):
                        NextTram = int(TimeEarly4[s] + StopSeedEarly4[ChosenStop])
                        st.write("First tram:", fmt(NextTram))
                        break
                break

            if ChosenTime > int(TimeBracket4[-1]) and ChosenStop in StopSeedLate4:
                for t in range(len(TimeLate4) - 1):
                    if TimeLate4[t] <= ChosenTime < TimeLate4[t+1]:
                        NextTram = int(TimeLate4[t+1] + StopSeedLate4[ChosenStop])
                        st.write("Next late tram:", fmt(NextTram))
                        break
                    elif ChosenTime > int(TimeLate4[-1]):
                        NextTram = int(TimeLate4[-1] + StopSeedLate4[ChosenStop])
                        st.write("Final tram:", fmt(NextTram))
                        break
                break

# =========================================================
# 3. TOP-LEVEL MODE SELECTOR
# =========================================================

st.title("🚋 Nottingham Tram App")

mode = st.radio(
    "Select mode:",
    ["Full Timetables", "Next Tram (GTFS-style)"],
    horizontal=True,
    key="mode_selector"
)

if mode == "Full Timetables":
    run_timetable_mode()
else:
    run_next_tram_mode()
