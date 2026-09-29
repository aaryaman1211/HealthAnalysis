"""Load and merge every Zepp export folder in the repo into analysis-ready tables.

HEARTRATE_AUTO, ACTIVITY_MINUTE, ACTIVITY_STAGE, SLEEP_MINUTE and ACTIVITY dates are
already in local time (IST). SPORT, SLEEP start/stop and BODY carry explicit UTC
timestamps and are converted here, so every output column is in IST.
"""

import csv
import re
from datetime import datetime, timedelta
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
LOCAL_OFFSET = timedelta(hours=5, minutes=30)  # IST; confirmed by aligning workouts to HR spikes

# User-provided body stats (not in the export).
WEIGHT_KG = 65.0
BODY_FAT = 0.13
AGE = 20
HR_MAX = 220 - AGE
VIGOROUS_HR = round(0.7 * HR_MAX)
MIN_GPS_DISTANCE_M = 500

SPORT_LABELS = {
    "1": "Running",
    "6": "Walk/Jog",
    "8": "Walk/Jog",
    "9": "Cycling",
    "10": "Indoor workout",
    "14": "Indoor workout",
    "49": "Indoor cardio/HIIT",
    "52": "Strength/Gym",
    "85": "High-intensity indoor (85)",
    "191": "High-intensity indoor (191)",
    "227": "Indoor workout",
}
DISTANCE_TYPES = {"1": 1.05, "6": 0.75, "8": 0.75}  # stride length (m) for workouts that add steps


def _export_ts(path):
    return int(re.search(r"_(\d+)\.csv$", str(path)).group(1))


def export_folders():
    folders = [p for p in ROOT.glob("Health Data*") if p.is_dir()]
    return sorted(folders, key=lambda f: _export_ts(next((f / "ACTIVITY").glob("*.csv"))))


def _read(path, escape=False):
    with open(path, encoding="utf-8-sig", newline="") as f:
        if escape:
            rows = list(csv.reader(f, escapechar="\\"))
            return pd.DataFrame(rows[1:], columns=rows[0])
        return pd.DataFrame(list(csv.DictReader(f)))


def load(category, key, escape=False):
    """All exports of one category, later exports winning on duplicate keys."""
    frames = []
    for i, folder in enumerate(export_folders()):
        for path in (folder / category).glob("*.csv"):
            df = _read(path, escape)
            df["_export"] = i
            frames.append(df)
    df = pd.concat(frames, ignore_index=True)
    return df.drop_duplicates(subset=key, keep="last").reset_index(drop=True)


def utc_to_local(series):
    return pd.to_datetime(series.str[:19], format="%Y-%m-%d %H:%M:%S") + LOCAL_OFFSET


def periods():
    """One period per export; a date shared by two exports belongs to the earlier one."""
    out, taken = [], set()
    for i, folder in enumerate(export_folders()):
        dates = sorted(set(_read(next((folder / "ACTIVITY").glob("*.csv")))["date"]) - taken)
        taken |= set(dates)
        out.append({"name": f"P{i + 1}", "start": pd.Timestamp(dates[0]), "end": pd.Timestamp(dates[-1])})
    return out


def _period_of(dates, plist):
    labels = pd.Series(pd.NA, index=dates.index, dtype="object")
    for p in plist:
        labels[(dates >= p["start"]) & (dates <= p["end"])] = p["name"]
    return labels


def _export_profile_weights():
    return {i: float(_read(next((f / "USER").glob("*.csv")))["weight"].iloc[0]) for i, f in enumerate(export_folders())}


def build():
    plist = periods()

    hr = load("HEARTRATE_AUTO", ["date", "time"])
    hr = pd.Series(hr["heartRate"].astype(int).values,
                   index=pd.to_datetime(hr["date"] + " " + hr["time"]), name="hr").sort_index()

    steps_min = load("ACTIVITY_MINUTE", ["date", "time"])
    steps_min = pd.Series(steps_min["steps"].astype(int).values,
                          index=pd.to_datetime(steps_min["date"] + " " + steps_min["time"]), name="steps").sort_index()

    sleep_min = load("SLEEP_MINUTE", ["date", "time"])
    sleep_min["ts"] = pd.to_datetime(sleep_min["date"] + " " + sleep_min["time"])
    sleep_min["hr"] = pd.to_numeric(sleep_min["hr"], errors="coerce")
    sleep_min = sleep_min.set_index("ts").sort_index()[["stage", "hr"]]

    # ---- sessions ----
    sp = load("SPORT", ["startTime"])
    s = pd.DataFrame({
        "start": utc_to_local(sp["startTime"]),
        "type": sp["type"],
        "dur_min": sp["sportTime(s)"].astype(float) / 60,
        "dist_m": sp["distance(m)"].astype(float).clip(lower=0),
        "pace_raw": sp["avgPace(/meter)"].astype(float),
        "cal_device": sp["calories(kcal)"].astype(float),
        "_export": sp["_export"],
    }).sort_values("start").reset_index(drop=True)
    s["label"] = s["type"].map(SPORT_LABELS).fillna("Type " + s["type"])
    s["date"] = s["start"].dt.normalize()
    s["period"] = _period_of(s["date"], plist)
    valid_gps = (s["dist_m"] >= MIN_GPS_DISTANCE_M) & (s["pace_raw"] > 0)
    s["pace_min_km"] = np.where(valid_gps, s["pace_raw"] * 1000 / 60, np.nan)
    s["kcal_min"] = s["cal_device"] / s["dur_min"]
    avg_hr, max_hr = [], []
    for start, dur in zip(s["start"], s["dur_min"]):
        w = hr.loc[start: start + timedelta(minutes=dur)]
        ok = len(w) >= 0.5 * dur
        avg_hr.append(w.mean() if ok else np.nan)
        max_hr.append(w.max() if ok else np.nan)
    s["avg_hr"], s["max_hr"] = avg_hr, max_hr
    speed_m_min = s["dist_m"] / s["dur_min"]
    s["m_per_beat"] = np.where(valid_gps & s["avg_hr"].notna(), speed_m_min / s["avg_hr"], np.nan)

    # ---- daily ----
    act = load("ACTIVITY", ["date"])
    daily = pd.DataFrame({
        "date": pd.to_datetime(act["date"]),
        "steps": act["steps"].astype(int),
        "distance_km": act["distance"].astype(int) / 1000,
        "run_distance_km": act["runDistance"].astype(int) / 1000,
        "act_cal": act["calories"].astype(int),
        "_export": act["_export"],
    }).sort_values("date").reset_index(drop=True)
    daily["period"] = _period_of(daily["date"], plist)
    daily = daily[daily["period"].notna()].reset_index(drop=True)

    st = load("ACTIVITY_STAGE", ["date", "start", "stop"])
    to_min = lambda t: t.str[:2].astype(int) * 60 + t.str[3:].astype(int)
    st["mins"] = (to_min(st["stop"]) - to_min(st["start"])) % 1440
    daily["active_min"] = daily["date"].dt.strftime("%Y-%m-%d").map(st.groupby("date")["mins"].sum()).fillna(0)

    hr_day = hr.groupby(hr.index.normalize())
    daily["rhr_min"] = daily["date"].map(hr_day.min())
    daily["avg_hr"] = daily["date"].map(hr_day.mean())
    daily["max_hr"] = daily["date"].map(hr_day.max())
    daily["vigorous_min"] = daily["date"].map((hr >= VIGOROUS_HR).groupby(hr.index.normalize()).sum()).fillna(0)

    sg = s.groupby("date")
    daily["w_count"] = daily["date"].map(sg.size()).fillna(0).astype(int)
    daily["w_min"] = daily["date"].map(sg["dur_min"].sum()).fillna(0)
    daily["w_cal"] = daily["date"].map(sg["cal_device"].sum()).fillna(0)
    daily["workouts"] = daily["date"].map(
        sg[["label", "dur_min"]].apply(lambda g: "; ".join(f"{l} ({d:.0f} min)" for l, d in zip(g["label"], g["dur_min"])))).fillna("")

    sl = load("SLEEP", ["date"], escape=True)
    sl = pd.DataFrame({
        "date": pd.to_datetime(sl["date"]),
        "deep": pd.to_numeric(sl["deepSleepTime"]),
        "light": pd.to_numeric(sl["shallowSleepTime"]),
        "rem": pd.to_numeric(sl["REMTime"]),
        "awake": pd.to_numeric(sl["wakeTime"]),
        "bedtime": utc_to_local(sl["start"]),
        "waketime": utc_to_local(sl["stop"]),
        "naps": sl["naps"].str.count('"start"').fillna(0).astype(int),
    })
    sl["sleep_min"] = sl["deep"] + sl["light"] + sl["rem"]
    sleep_hr_avg, sleep_hr_low = [], []
    for b, w in zip(sl["bedtime"], sl["waketime"]):
        h = sleep_min.loc[b:w, "hr"].dropna()
        sleep_hr_avg.append(h.mean() if len(h) >= 60 else np.nan)
        sleep_hr_low.append(h.rolling(10).mean().min() if len(h) >= 60 else np.nan)
    sl["sleep_hr_avg"] = sleep_hr_avg
    sl["sleep_hr_low10"] = sleep_hr_low
    daily = daily.merge(sl, on="date", how="left")
    daily["sleep_h"] = daily["sleep_min"] / 60
    daily["deep_pct"] = daily["deep"] / daily["sleep_min"]
    daily["rem_pct"] = daily["rem"] / daily["sleep_min"]
    clock = lambda t: t.dt.hour + t.dt.minute / 60
    bed = clock(daily["bedtime"])
    daily["bed_clock"] = np.where(bed < 12, bed + 24, bed)  # hours after midnight of the previous day, e.g. 25.5 = 01:30
    daily["wake_clock"] = clock(daily["waketime"])
    daily["weekday"] = daily["date"].dt.day_name()

    # ---- energy expenditure (bottom-up, see ANALYSIS.md) ----
    bmr = 370 + 21.6 * WEIGHT_KG * (1 - BODY_FAT)
    profile_w = _export_profile_weights()
    daily["weight_scale"] = WEIGHT_KG / daily["_export"].map(profile_w)
    rest = daily[(daily["w_count"] == 0) & (daily["steps"] > 0)]
    neat_rate = (rest["act_cal"] / rest["steps"]).groupby(rest["period"]).mean()
    workout_steps = s[s["type"].isin(DISTANCE_TYPES)].assign(
        est_steps=lambda d: d["dist_m"] / d["type"].map(DISTANCE_TYPES)).groupby("date")["est_steps"].sum()
    neat_steps = (daily["steps"] - daily["date"].map(workout_steps).fillna(0)).clip(lower=0)
    daily["neat_kcal"] = neat_steps * daily["period"].map(neat_rate) * daily["weight_scale"]
    daily["ex_kcal"] = daily["w_cal"] * daily["weight_scale"]
    daily["tdee"] = bmr + daily["neat_kcal"] + daily["ex_kcal"]

    body = load("BODY", ["time"])
    body["time"] = utc_to_local(body["time"])

    return {
        "periods": plist, "daily": daily, "sessions": s, "hr": hr,
        "steps_min": steps_min, "sleep_min": sleep_min, "body": body, "bmr": bmr,
    }
