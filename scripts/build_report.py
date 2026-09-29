"""Generate report charts and print the statistics tables used in report/REPORT.md.

Run: python3 scripts/build_report.py
"""

from datetime import timedelta

import matplotlib

matplotlib.use("Agg")
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.colors import LinearSegmentedColormap
from scipy import stats

import healthdata as H

OUT = H.ROOT / "report" / "charts"
OUT.mkdir(parents=True, exist_ok=True)

# Reference palette (dataviz skill): categorical slots in fixed order, validated for CVD.
SLOTS = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100"]
SURF, INK, INK2, MUTED, GRID, AXIS = "#fcfcfb", "#0b0b0b", "#52514e", "#898781", "#e1e0d9", "#c3c2b7"
DIV_NEG, DIV_MID, DIV_POS = "#e34948", "#f0efec", "#2a78d6"

plt.rcParams.update({
    "font.family": "Arial", "font.size": 9.5, "text.color": INK,
    "axes.titlesize": 12.5, "axes.titleweight": "bold", "axes.titlelocation": "left", "axes.titlepad": 22,
    "axes.labelcolor": INK2, "axes.labelsize": 9.5, "axes.edgecolor": AXIS, "axes.linewidth": 0.8,
    "axes.grid": True, "axes.axisbelow": True, "grid.color": GRID, "grid.linewidth": 0.6,
    "axes.spines.top": False, "axes.spines.right": False,
    "xtick.color": AXIS, "ytick.color": AXIS, "xtick.labelcolor": INK2, "ytick.labelcolor": INK2,
    "figure.facecolor": SURF, "axes.facecolor": SURF, "savefig.facecolor": SURF,
    "legend.frameon": False, "legend.fontsize": 9, "lines.linewidth": 2, "figure.dpi": 100,
})

data = H.build()
daily, sessions, hr, steps_min, plist = data["daily"], data["sessions"], data["hr"], data["steps_min"], data["periods"]
NAMES = [p["name"] for p in plist]
COLOR = {n: SLOTS[i] for i, n in enumerate(NAMES)}
LABEL = {p["name"]: f'{p["name"]} ({p["start"]:%d %b} – {p["end"]:%d %b})' for p in plist}
daily["day_idx"] = (daily["date"] - daily["date"].min()).dt.days


def save(fig, name):
    fig.savefig(OUT / name, dpi=160, bbox_inches="tight")
    plt.close(fig)


def subtitle(ax, text):
    ax.text(0, 1.005, text, transform=ax.transAxes, fontsize=9, color=INK2, va="bottom")


def period_boundaries(ax, ymax_frac=0.97):
    for p in plist[1:]:
        x = p["start"] - timedelta(hours=12)
        ax.axvline(x, color=AXIS, lw=1, zorder=0)
        ax.text(x, ymax_frac, f' {p["name"]} →', transform=ax.get_xaxis_transform(), color=INK2, fontsize=8.5, va="top")


def date_axis(ax):
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    ax.xaxis.set_minor_locator(mdates.WeekdayLocator(byweekday=0))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
    ax.grid(axis="x", which="both", visible=False)


def legend_periods(ax, loc=None, marker=False):
    """Legend above the plot, right-aligned, so it never covers data."""
    handles = [plt.Line2D([], [], color=COLOR[n], lw=0 if marker else 2.5, marker="o" if marker else None, ms=7, label=LABEL[n])
               for n in NAMES]
    ax.legend(handles=handles, loc="lower right", bbox_to_anchor=(1, 1.005), ncol=len(NAMES), borderaxespad=0)


def daily_with_rolling(ax, col, bar=True, scale=1.0, dot=False):
    s = daily.set_index("date")[col] * scale
    roll = s.rolling(7, min_periods=4).mean()
    for n in NAMES:
        m = (daily["period"] == n).values
        if bar:
            ax.bar(s.index[m], s.values[m], width=0.72, color=COLOR[n], alpha=0.28, lw=0)
        if dot:
            ax.scatter(s.index[m], s.values[m], s=12, color=COLOR[n], alpha=0.35, lw=0)
        ax.plot(roll.index[m], roll.values[m], color=COLOR[n])
    return s, roll


def clock_fmt(v, _=None):
    v = v % 24
    return f"{int(v):02d}:{int(round((v % 1) * 60)) % 60:02d}"


# =================== statistics ===================
def compare(values, periods, day_idx=None):
    a = values[periods == NAMES[-2]].dropna()
    b = values[periods == NAMES[-1]].dropna()
    pooled = np.sqrt(((len(a) - 1) * a.var() + (len(b) - 1) * b.var()) / (len(a) + len(b) - 2))
    out = {
        "a_mean": a.mean(), "a_med": a.median(), "b_mean": b.mean(), "b_med": b.median(),
        "a_sd": a.std(), "b_sd": b.std(), "diff": b.mean() - a.mean(),
        "pct": (b.mean() - a.mean()) / a.mean() if a.mean() else np.nan,
        "p_welch": stats.ttest_ind(a, b, equal_var=False).pvalue,
        "p_mwu": stats.mannwhitneyu(a, b).pvalue,
        "d": (b.mean() - a.mean()) / pooled if pooled else np.nan,
        "p_levene": stats.levene(a, b).pvalue,
    }
    if day_idx is not None:
        ok = values.notna()
        lr = stats.linregress(day_idx[ok], values[ok])
        out["slope30"], out["p_trend"] = lr.slope * 30, lr.pvalue
    return out


def fmt_p(p):
    return "<0.001" if p < 0.001 else f"{p:.3f}"


DAILY_METRICS = [
    ("steps", "Steps / day", "{:,.0f}"),
    ("distance_km", "Distance / day (km)", "{:.2f}"),
    ("active_min", "Active minutes / day", "{:.0f}"),
    ("act_cal", "Activity calories / day", "{:,.0f}"),
    ("rhr_min", "Resting HR, daily low (bpm)", "{:.1f}"),
    ("sleep_hr_avg", "Sleeping HR, night avg (bpm)", "{:.1f}"),
    ("sleep_hr_low10", "Lowest 10-min sleeping HR (bpm)", "{:.1f}"),
    ("avg_hr", "All-day avg HR (bpm)", "{:.1f}"),
    ("max_hr", "Daily max HR (bpm)", "{:.0f}"),
    ("vigorous_min", f"Vigorous minutes (HR ≥ {H.VIGOROUS_HR})", "{:.1f}"),
    ("w_count", "Workouts / day", "{:.2f}"),
    ("w_min", "Workout minutes / day", "{:.0f}"),
    ("w_cal", "Workout calories / day", "{:,.0f}"),
    ("sleep_h", "Sleep (h)", "{:.2f}"),
    ("deep", "Deep sleep (min)", "{:.0f}"),
    ("light", "Light sleep (min)", "{:.0f}"),
    ("rem", "REM sleep (min)", "{:.0f}"),
    ("awake", "Awake in bed (min)", "{:.1f}"),
    ("deep_pct", "Deep % of sleep", "{:.1%}"),
    ("rem_pct", "REM % of sleep", "{:.1%}"),
    ("bed_clock", "Fell asleep (IST)", "clock"),
    ("wake_clock", "Woke up (IST)", "clock"),
    ("tdee", "Est. energy burned (kcal/day)", "{:,.0f}"),
]


def fv(v, f):
    return clock_fmt(v) if f == "clock" else f.format(v)


def fdiff(v, f):
    if f == "clock":
        sign = "+" if v >= 0 else "-"
        m = abs(v) * 60
        return f"{sign}{int(m // 60)}h{int(m % 60):02d}"
    return ("+" if v >= 0 else "") + f.format(v).replace("+", "")


rows = []
for col, name, f in DAILY_METRICS:
    r = compare(daily[col], daily["period"], daily["day_idx"])
    rows.append((name, f, r))
print(f"\n### Daily metrics: {NAMES[-2]} vs {NAMES[-1]}\n")
print(f"| Metric | {NAMES[-2]} mean (median) | {NAMES[-1]} mean (median) | Change | p (Welch) | p (Mann-Whitney) | Effect size d | 140-day trend / 30 days (p) |")
print("|---|---|---|---|---|---|---|---|")
for name, f, r in rows:
    trend = fdiff(r["slope30"], f) if f != "{:.1%}" else f"{r['slope30'] * 100:+.1f} pts"
    print(f"| {name} | {fv(r['a_mean'], f)} ({fv(r['a_med'], f)}) | {fv(r['b_mean'], f)} ({fv(r['b_med'], f)}) | "
          f"{fdiff(r['diff'], f)} | {fmt_p(r['p_welch'])} | {fmt_p(r['p_mwu'])} | {r['d']:+.2f} | {trend} ({fmt_p(r['p_trend'])}) |")

print("\n### Variability (std dev) and Levene test\n")
for col in ("bed_clock", "wake_clock", "sleep_h", "steps"):
    r = compare(daily[col], daily["period"])
    print(f"{col}: sd {r['a_sd']:.2f} -> {r['b_sd']:.2f}, Levene p={fmt_p(r['p_levene'])}")

runs = sessions[(sessions["type"] == "1") & sessions["pace_min_km"].notna()].copy()
print("\n### Session-level\n")
for label, frame, col, f in [
    ("Run pace (min/km)", runs, "pace_min_km", "{:.2f}"),
    ("Run efficiency (m per heartbeat)", runs, "m_per_beat", "{:.3f}"),
    ("Run avg HR", runs, "avg_hr", "{:.1f}"),
    ("Run distance (km)", runs.assign(km=runs["dist_m"] / 1000), "km", "{:.2f}"),
    ("All sessions avg HR", sessions, "avg_hr", "{:.1f}"),
    ("All sessions kcal/min", sessions, "kcal_min", "{:.2f}"),
    ("All sessions duration (min)", sessions, "dur_min", "{:.0f}"),
]:
    r = compare(frame[col], frame["period"])
    print(f"{label}: {fv(r['a_mean'], f)} -> {fv(r['b_mean'], f)} (n={frame[col][frame['period'] == NAMES[-2]].notna().sum()}/{frame[col][frame['period'] == NAMES[-1]].notna().sum()}), "
          f"Welch p={fmt_p(r['p_welch'])}, MWU p={fmt_p(r['p_mwu'])}, d={r['d']:+.2f}")
print("\nRuns detail:")
print(runs[["date", "period", "dist_m", "dur_min", "pace_min_km", "avg_hr", "m_per_beat"]].round(3).to_string(index=False))
lr = stats.linregress((runs["date"] - daily["date"].min()).dt.days, runs["m_per_beat"])
print(f"Run efficiency trend: {lr.slope * 30:+.4f} m/beat per 30 days, p={fmt_p(lr.pvalue)}, r={lr.rvalue:+.2f}")
lr = stats.linregress((runs["date"] - daily["date"].min()).dt.days, runs["pace_min_km"])
print(f"Run pace trend: {lr.slope * 30:+.3f} min/km per 30 days, p={fmt_p(lr.pvalue)}")

print("\nSessions by type:")
print(sessions.pivot_table(index="label", columns="period", values=["dur_min", "avg_hr", "kcal_min"],
                           aggfunc={"dur_min": ["count", "sum"], "avg_hr": "mean", "kcal_min": "mean"}).round(1).to_string())

print("\nSession start hour (IST) by period:")
print(sessions.assign(h=sessions["start"].dt.hour).groupby("period")["h"].describe().round(1).to_string())

# lagged relationships: activity on day D vs the night that ends on D+1
nxt = daily.set_index("date")[["sleep_h", "deep", "rem", "sleep_hr_avg", "bed_clock", "rhr_min"]].shift(-1, freq="D").add_suffix("_next")
lag = daily.set_index("date").join(nxt).reset_index()
print("\n### Lagged relationships (Spearman)\n")
pairs = [
    ("w_cal", "sleep_h_next", "Workout calories today → sleep tonight"),
    ("vigorous_min", "sleep_h_next", "Vigorous minutes today → sleep tonight"),
    ("steps", "sleep_h_next", "Steps today → sleep tonight"),
    ("vigorous_min", "sleep_hr_avg_next", "Vigorous minutes today → sleeping HR tonight"),
    ("w_cal", "sleep_hr_avg_next", "Workout calories today → sleeping HR tonight"),
    ("bed_clock_next", "sleep_h_next", "Later sleep onset → sleep length"),
    ("sleep_h", "w_cal", "Sleep last night → workout calories today"),
    ("sleep_h", "steps", "Sleep last night → steps today"),
    ("sleep_h", "rhr_min", "Sleep last night → resting HR today"),
    ("sleep_h_next", "sleep_hr_avg_next", "Sleep length → sleeping HR (same night)"),
]
for x, y, name in pairs:
    for scope in ["All"] + NAMES:
        f = lag if scope == "All" else lag[lag["period"] == scope]
        ok = f[[x, y]].dropna()
        rho, p = stats.spearmanr(ok[x], ok[y])
        print(f"{name} [{scope}]: rho={rho:+.2f}, p={fmt_p(p)}, n={len(ok)}")

print("\nWorst sleep nights:")
print(daily.nsmallest(8, "sleep_h")[["date", "period", "sleep_h", "bed_clock", "wake_clock", "w_cal"]].round(2).to_string(index=False))
print("\nBest/worst weeks for sleep:")
wk = daily.assign(week=daily["date"] - pd.to_timedelta(daily["date"].dt.weekday, unit="D")).groupby("week").agg(
    days=("date", "size"), sleep=("sleep_h", "mean"), w_cal=("w_cal", "mean"), vig=("vigorous_min", "sum"), steps=("steps", "mean"),
    rhr=("rhr_min", "mean"), shr=("sleep_hr_avg", "mean"))
print(wk.round(2).to_string())
print("\nWeekday means:")
print(daily.pivot_table(index="weekday", columns="period", values=["steps", "sleep_h", "w_count"], aggfunc="mean")
      .reindex(["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]).round(2).to_string())
print("\nEnergy components:")
print(daily.groupby("period")[["neat_kcal", "ex_kcal", "tdee"]].agg(["mean", "median"]).round(0).to_string())
print(f"BMR {data['bmr']:.0f}")

# =================== charts ===================
# 01 steps
fig, ax = plt.subplots(figsize=(11, 4.2))
s, roll = daily_with_rolling(ax, "steps")
ax.set_title("Daily steps")
subtitle(ax, "Bars = each day, line = 7-day average. " + " · ".join(f"{n} mean {daily.loc[daily.period == n, 'steps'].mean():,.0f}" for n in NAMES))
ax.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: f"{v / 1000:.0f}k"))
date_axis(ax); period_boundaries(ax); legend_periods(ax, loc="upper right")
save(fig, "01_steps_trend.png")

# 02 distributions
dist_metrics = [("steps", "Steps / day", 1), ("active_min", "Active minutes / day", 1), ("vigorous_min", "Vigorous minutes / day", 1),
                ("w_cal", "Workout kcal / day", 1), ("rhr_min", "Resting HR (bpm)", 1), ("sleep_hr_avg", "Sleeping HR (bpm)", 1),
                ("sleep_h", "Sleep (hours)", 1), ("rem", "REM sleep (min)", 1)]
fig, axes = plt.subplots(2, 4, figsize=(12.5, 6.4))
rng_ = np.random.default_rng(7)
for ax, (col, name, _) in zip(axes.flat, dist_metrics):
    for i, n in enumerate(NAMES):
        v = daily.loc[daily.period == n, col].dropna().values
        bp = ax.boxplot(v, positions=[i], widths=0.5, showfliers=False, patch_artist=True,
                        medianprops=dict(color=COLOR[n], lw=2), boxprops=dict(facecolor=SURF, edgecolor=COLOR[n], lw=1.2),
                        whiskerprops=dict(color=COLOR[n], lw=1), capprops=dict(color=COLOR[n], lw=1))
        ax.scatter(i + rng_.uniform(-0.18, 0.18, len(v)), v, s=9, color=COLOR[n], alpha=0.35, lw=0, zorder=3)
    r = compare(daily[col], daily["period"])
    ax.set_title(name, fontsize=10.5)
    subtitle(ax, f"p = {fmt_p(r['p_mwu'])} · d = {r['d']:+.2f}")
    ax.set_xticks(range(len(NAMES)), NAMES)
    ax.grid(axis="x", visible=False)
fig.suptitle("Period-by-period distributions (box = middle 50%, line = median, dots = days)", x=0.01, ha="left", fontsize=12.5, fontweight="bold")
fig.tight_layout(rect=(0, 0, 1, 0.95))
save(fig, "02_period_distributions.png")

# 03 heart-rate trends
fig, axes = plt.subplots(2, 1, figsize=(11, 6.6), sharex=True)
for ax, col, name in [(axes[0], "rhr_min", "Resting heart rate (lowest reading of the day)"),
                      (axes[1], "sleep_hr_avg", "Average heart rate while asleep")]:
    daily_with_rolling(ax, col, bar=False, dot=True)
    ax.set_title(name, fontsize=11.5)
    ax.set_ylabel("bpm")
    subtitle(ax, " · ".join(f"{n} {daily.loc[daily.period == n, col].mean():.1f}" for n in NAMES) + " bpm (dots = days, line = 7-day avg)")
    period_boundaries(ax)
date_axis(axes[1]); legend_periods(axes[0], loc="upper right")
fig.tight_layout()
save(fig, "03_heart_rate_trend.png")

# 04 intraday HR
fig, ax = plt.subplots(figsize=(11, 4.2))
hrd = hr.to_frame()
hrd["period"] = pd.Series(hrd.index.normalize()).map(daily.set_index("date")["period"]).values
hrd["hour"] = hrd.index.hour
prof = hrd.dropna().groupby(["period", "hour"])["hr"].mean().unstack(0)
for n in NAMES:
    ax.plot(prof.index, prof[n], color=COLOR[n], marker="o", ms=4.5, label=LABEL[n])
ax.set_xticks(range(0, 24, 2), [f"{h:02d}:00" for h in range(0, 24, 2)])
ax.set_ylabel("Average heart rate (bpm)")
ax.set_title("Average heart rate by hour of day (IST)")
subtitle(ax, "The low plateau is sleep; its edges show when you fall asleep and wake up")
ax.legend(loc="upper left")
save(fig, "04_intraday_heart_rate.png")

# 05 intraday steps
fig, ax = plt.subplots(figsize=(11, 4.2))
sm = steps_min.to_frame()
sm["period"] = pd.Series(sm.index.normalize()).map(daily.set_index("date")["period"]).values
sm["hour"] = sm.index.hour
days_per = daily.groupby("period").size()
prof = sm.dropna().groupby(["period", "hour"])["steps"].sum().unstack(0) / days_per
prof = prof.reindex(range(24)).fillna(0)
w = 0.4
for i, n in enumerate(NAMES):
    ax.bar(prof.index + (i - (len(NAMES) - 1) / 2) * w, prof[n], width=w * 0.9, color=COLOR[n], label=LABEL[n], lw=0)
ax.set_xticks(range(0, 24, 2), [f"{h:02d}:00" for h in range(0, 24, 2)])
ax.set_ylabel("Avg steps in that hour")
ax.set_title("When you move: average steps by hour of day (IST)")
subtitle(ax, "Everyday movement only. The minute-level export leaves out steps taken during logged workouts")
ax.grid(axis="x", visible=False); ax.legend(loc="upper left")
save(fig, "05_intraday_steps.png")

# 06 weekday
order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
fig, axes = plt.subplots(1, 3, figsize=(13, 4))
for ax, col, name, fmt in [(axes[0], "steps", "Avg steps", "{:,.0f}"), (axes[1], "sleep_h", "Avg sleep (h), by wake-up day", "{:.1f}"),
                           (axes[2], "w_count", "Avg workouts", "{:.1f}")]:
    piv = daily.pivot_table(index="weekday", columns="period", values=col, aggfunc="mean").reindex(order)
    x = np.arange(7)
    for i, n in enumerate(NAMES):
        ax.bar(x + (i - (len(NAMES) - 1) / 2) * 0.38, piv[n], width=0.36, color=COLOR[n], label=n, lw=0)
    ax.set_xticks(x, [d[:3] for d in order])
    ax.set_title(name, fontsize=11)
    ax.grid(axis="x", visible=False)
axes[0].yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: f"{v / 1000:.0f}k"))
axes[0].legend(loc="upper left")
fig.suptitle("Weekly rhythm", x=0.01, ha="left", fontsize=12.5, fontweight="bold")
fig.tight_layout(rect=(0, 0, 1, 0.94))
save(fig, "06_weekday_patterns.png")

# 07 sleep duration
fig, ax = plt.subplots(figsize=(11, 4.2))
daily_with_rolling(ax, "sleep_h")
for y, t in [(7, "7 h (recommended minimum)"), (6, "6 h")]:
    ax.axhline(y, color=INK2, lw=0.9)
    ax.text(daily["date"].min(), y + 0.1, t, color=INK2, fontsize=8.5)
ax.set_ylabel("Hours asleep")
ax.set_title("Nightly sleep (by wake-up date)")
subtitle(ax, " · ".join(f"{n}: {daily.loc[daily.period == n, 'sleep_h'].mean():.2f} h avg, {(daily.loc[daily.period == n, 'sleep_h'] < 6).sum()} nights under 6 h" for n in NAMES))
date_axis(ax); period_boundaries(ax); legend_periods(ax, loc="upper right")
save(fig, "07_sleep_duration_trend.png")

# 08 sleep stages
fig, axes = plt.subplots(1, 2, figsize=(12, 4))
stages = [("deep", "Deep"), ("light", "Light"), ("rem", "REM"), ("awake", "Awake")]
x = np.arange(len(stages))
tot = daily["deep"] + daily["light"] + daily["rem"] + daily["awake"]
for i, n in enumerate(NAMES):
    m = daily.period == n
    mins = [daily.loc[m, c].mean() for c, _ in stages]
    pct = [(daily.loc[m, c] / tot[m]).mean() * 100 for c, _ in stages]
    for ax, vals, fmt in [(axes[0], mins, "{:.0f}"), (axes[1], pct, "{:.0f}%")]:
        bars = ax.bar(x + (i - 0.5) * 0.38, vals, width=0.36, color=COLOR[n], label=LABEL[n], lw=0)
        for b, v in zip(bars, vals):
            ax.text(b.get_x() + b.get_width() / 2, v, fmt.format(v), ha="center", va="bottom", fontsize=8, color=INK2)
for ax, t in [(axes[0], "Minutes per night by stage"), (axes[1], "Share of time in bed by stage")]:
    ax.set_xticks(x, [s for _, s in stages]); ax.set_title(t, fontsize=11.5); ax.grid(axis="x", visible=False)
axes[0].legend(loc="upper right")
save(fig, "08_sleep_stages.png")

# 09 sleep timing
fig, ax = plt.subplots(figsize=(11, 4.8))
base = daily["date"] - timedelta(days=1)
bed_h = (daily["bedtime"] - base).dt.total_seconds() / 3600
wake_h = (daily["waketime"] - base).dt.total_seconds() / 3600
for n in NAMES:
    m = (daily.period == n) & bed_h.notna()
    ax.vlines(daily.loc[m, "date"], bed_h[m], wake_h[m], color=COLOR[n], lw=3, alpha=0.45)
    ax.plot(daily.loc[m, "date"], bed_h[m].rolling(7, min_periods=4).median(), color=COLOR[n], lw=2)
    ax.plot(daily.loc[m, "date"], wake_h[m].rolling(7, min_periods=4).median(), color=COLOR[n], lw=2)
ax.set_ylim(40, 18)
ax.yaxis.set_major_locator(matplotlib.ticker.MultipleLocator(2))
ax.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(clock_fmt))
ax.set_ylabel("Clock time (IST)")
ax.set_title("Sleep window each night: when you fell asleep and woke up")
subtitle(ax, "Each bar spans one night; lines = 7-night median sleep onset (top) and wake-up (bottom)")
date_axis(ax); period_boundaries(ax); legend_periods(ax, loc="lower right")
save(fig, "09_sleep_timing.png")

# 10 workout mix
mix = sessions.pivot_table(index="label", columns="period", values="dur_min", aggfunc=["count", "sum"]).fillna(0)
order_l = mix["count"].sum(axis=1).sort_values().index
fig, axes = plt.subplots(1, 2, figsize=(13, 4.6), sharey=True)
y = np.arange(len(order_l))
for i, n in enumerate(NAMES):
    axes[0].barh(y + (i - 0.5) * 0.38, mix["count"][n].reindex(order_l), height=0.36, color=COLOR[n], label=LABEL[n], lw=0)
    axes[1].barh(y + (i - 0.5) * 0.38, mix["sum"][n].reindex(order_l) / 60, height=0.36, color=COLOR[n], lw=0)
axes[0].set_yticks(y, order_l)
axes[0].set_title("Sessions by type", fontsize=11.5); axes[1].set_title("Hours by type", fontsize=11.5)
for ax in axes:
    ax.grid(axis="y", visible=False)
axes[0].legend(loc="lower right")
subtitle(axes[0], "Names inferred from Zepp type codes")
fig.tight_layout()
save(fig, "10_workout_mix.png")

# 11 weekly load
wk = daily.assign(week=daily["date"] - pd.to_timedelta(daily["date"].dt.weekday, unit="D"))
wagg = wk.groupby("week").agg(days=("date", "size"), w_min=("w_min", "sum"), vig=("vigorous_min", "sum"),
                              period=("period", lambda p: p.value_counts().idxmax()))
wagg = wagg[wagg["days"] >= 4]
fig, axes = plt.subplots(2, 1, figsize=(11, 6.4), sharex=True)
for ax, col, t, yl in [(axes[0], "w_min", "Weekly workout time", "Hours"), (axes[1], "vig", f"Weekly vigorous minutes (HR ≥ {H.VIGOROUS_HR} bpm)", "Minutes")]:
    vals = wagg[col] / (60 if col == "w_min" else 1)
    ax.bar(wagg.index, vals, width=5.6, color=[COLOR[p] for p in wagg["period"]], lw=0, align="edge")
    for n in NAMES:
        ax.hlines(vals[wagg.period == n].mean(), wagg.index[wagg.period == n].min(), wagg.index[wagg.period == n].max() + timedelta(days=6),
                  color=INK2, lw=1)
    ax.set_title(t, fontsize=11.5); ax.set_ylabel(yl); ax.grid(axis="x", visible=False)
    subtitle(ax, " · ".join(f"{n} avg {vals[wagg.period == n].mean():.0f}" for n in NAMES) + " per week (grey line = period average)")
    period_boundaries(ax)
date_axis(axes[1]); legend_periods(axes[0], loc="upper right")
fig.tight_layout()
save(fig, "11_weekly_training_load.png")

# 12 workout timing
fig, ax = plt.subplots(figsize=(11, 3.8))
hours = np.arange(24)
for i, n in enumerate(NAMES):
    c = sessions[sessions.period == n]["start"].dt.hour.value_counts().reindex(hours, fill_value=0)
    ax.bar(hours + (i - 0.5) * 0.4, c, width=0.36, color=COLOR[n], label=LABEL[n], lw=0)
ax.set_xticks(range(0, 24, 2), [f"{h:02d}:00" for h in range(0, 24, 2)])
ax.set_ylabel("Sessions started"); ax.grid(axis="x", visible=False)
ax.set_title("When you train: workout start time (IST)")
ax.legend(loc="upper left")
save(fig, "12_workout_timing.png")

# 13 running
fig, axes = plt.subplots(2, 1, figsize=(11, 6.8), sharex=True)
for n in NAMES:
    r = runs[runs.period == n]
    axes[0].scatter(r["date"], r["pace_min_km"], s=r["dist_m"] / 60 + 12, color=COLOR[n], alpha=0.75, lw=1.5, edgecolor=SURF, label=LABEL[n], zorder=3)
    axes[1].scatter(r["date"], r["m_per_beat"], s=r["dist_m"] / 60 + 12, color=COLOR[n], alpha=0.75, lw=1.5, edgecolor=SURF, zorder=3)
for ax, col in [(axes[0], "pace_min_km"), (axes[1], "m_per_beat")]:
    ok = runs[col].notna()
    xs = mdates.date2num(runs.loc[ok, "date"])
    lr = stats.linregress(xs, runs.loc[ok, col])
    xx = np.array([xs.min(), xs.max()])
    ax.plot(mdates.num2date(xx), lr.intercept + lr.slope * xx, color=INK2, lw=1)
    period_boundaries(ax)
for _, r in runs[runs["dist_m"] >= 9000].iterrows():
    axes[0].annotate(f'{r["dist_m"] / 1000:.1f} km\n{clock_fmt(r["pace_min_km"]).replace(":", "′")}″/km', (r["date"], r["pace_min_km"]),
                     textcoords="offset points", xytext=(8, -4), fontsize=8, color=INK2)
axes[0].invert_yaxis()
axes[0].yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: f"{int(v)}:{int(round(v % 1 * 60)):02d}"))
axes[0].set_ylabel("Pace (min/km), faster ↑"); axes[0].set_title("Run pace (dot size = distance)", fontsize=11.5)
axes[1].set_ylabel("Metres per heartbeat"); axes[1].set_title("Running efficiency: distance covered per heartbeat (higher = fitter)", fontsize=11.5)
axes[0].legend(loc="lower left", markerscale=0.6)
date_axis(axes[1]); fig.tight_layout()
save(fig, "13_running.png")

# 14 session intensity
common = [l for l in order_l[::-1] if all((sessions[(sessions.label == l) & (sessions.period == n)].shape[0] >= 3) for n in NAMES)]
fig, axes = plt.subplots(1, 2, figsize=(13, 4.2))
x = np.arange(len(common))
for i, n in enumerate(NAMES):
    g = sessions[sessions.period == n].groupby("label")
    axes[0].bar(x + (i - 0.5) * 0.38, g["avg_hr"].mean().reindex(common), width=0.36, color=COLOR[n], label=LABEL[n], lw=0)
    axes[1].bar(x + (i - 0.5) * 0.38, g["kcal_min"].mean().reindex(common), width=0.36, color=COLOR[n], lw=0)
for ax, t, yl in [(axes[0], "Average HR during session", "bpm"), (axes[1], "Calories per minute", "kcal/min")]:
    ax.set_xticks(x, [c.replace(" (", "\n(") for c in common], fontsize=8.5); ax.set_title(t, fontsize=11.5)
    ax.set_ylabel(yl); ax.grid(axis="x", visible=False)
axes[0].set_ylim(80, None)
axes[0].legend(loc="upper left")
subtitle(axes[0], "Workout types with 3+ sessions in both periods")
fig.tight_layout()
save(fig, "14_session_intensity.png")

# 15 correlations
cm_cols = [("steps", "Steps"), ("active_min", "Active min"), ("vigorous_min", "Vigorous min"), ("w_cal", "Workout kcal"),
           ("rhr_min", "Resting HR"), ("avg_hr", "Avg HR"), ("sleep_h_next", "Sleep (night after)"),
           ("deep_next", "Deep (night after)"), ("rem_next", "REM (night after)"), ("sleep_hr_avg_next", "Sleeping HR (night after)"),
           ("bed_clock_next", "Sleep onset (night after)")]
corr = lag[[c for c, _ in cm_cols]].corr(method="spearman")
cmap = LinearSegmentedColormap.from_list("div", [DIV_NEG, DIV_MID, DIV_POS])
fig, ax = plt.subplots(figsize=(9, 7.6))
im = ax.imshow(corr.values, cmap=cmap, vmin=-1, vmax=1)
lbl = [l for _, l in cm_cols]
ax.set_xticks(range(len(lbl)), lbl, rotation=40, ha="right"); ax.set_yticks(range(len(lbl)), lbl)
ax.grid(False)
for i in range(len(lbl)):
    for j in range(len(lbl)):
        v = corr.values[i, j]
        if i != j and abs(v) >= 0.3:
            ax.text(j, i, f"{v:+.2f}", ha="center", va="center", fontsize=8, color=INK)
for sp in ax.spines.values():
    sp.set_visible(False)
cb = fig.colorbar(im, ax=ax, fraction=0.04, pad=0.02)
cb.outline.set_visible(False); cb.set_label("Spearman correlation")
ax.set_title("How daily metrics move together (all 140 days)")
subtitle(ax, "Values shown where |ρ| ≥ 0.3. \"Night after\" = the sleep that follows that day's activity")
save(fig, "15_correlations.png")

# 16 recovery
fig, axes = plt.subplots(1, 2, figsize=(12.5, 4.6))
for ax, x, y, xl, yl, t in [
    (axes[0], "w_cal", "sleep_h_next", "Workout calories that day (kcal)", "Hours asleep that night", "Training load vs that night's sleep"),
    (axes[1], "vigorous_min", "sleep_hr_avg_next", "Vigorous minutes that day", "Sleeping HR that night (bpm)", "Hard days vs overnight heart rate"),
]:
    for n in NAMES:
        f = lag[lag.period == n]
        ax.scatter(f[x], f[y], s=22, color=COLOR[n], alpha=0.6, lw=1, edgecolor=SURF, label=LABEL[n])
    ok = lag[[x, y]].dropna()
    rho, p = stats.spearmanr(ok[x], ok[y])
    lr = stats.linregress(ok[x], ok[y])
    xx = np.array([ok[x].min(), ok[x].max()])
    ax.plot(xx, lr.intercept + lr.slope * xx, color=INK2, lw=1)
    ax.set_xlabel(xl); ax.set_ylabel(yl); ax.set_title(t, fontsize=11.5)
    subtitle(ax, f"Spearman ρ = {rho:+.2f}, p = {fmt_p(p)}, n = {len(ok)}")
axes[0].legend(loc="upper right")
fig.tight_layout()
save(fig, "16_recovery.png")

# 17 energy
fig, ax = plt.subplots(figsize=(11, 4))
ew = wk.groupby("week").agg(days=("date", "size"), tdee=("tdee", "mean"), period=("period", lambda p: p.value_counts().idxmax()))
ew = ew[ew["days"] >= 4]
ax.bar(ew.index, ew["tdee"], width=5.6, color=[COLOR[p] for p in ew["period"]], lw=0, align="edge")
for n in NAMES:
    v = daily.loc[daily.period == n, "tdee"]
    ax.hlines(v.mean(), ew.index[ew.period == n].min(), ew.index[ew.period == n].max() + timedelta(days=6), color=INK2, lw=1)
    ax.text(ew.index[ew.period == n].min(), v.mean() + 25, f"{n} avg {v.mean():,.0f} kcal/day", fontsize=8.5, color=INK2)
ax.set_ylim(1500, None)
ax.set_ylabel("kcal / day")
ax.set_title("Estimated daily energy burned, weekly average")
subtitle(ax, f"BMR {data['bmr']:,.0f} + everyday movement + workouts. An estimate, not a measurement")
ax.grid(axis="x", visible=False); date_axis(ax); period_boundaries(ax); legend_periods(ax, loc="upper right")
save(fig, "17_energy_expenditure.png")

print("\ncharts:", sorted(p.name for p in OUT.glob("*.png")))
