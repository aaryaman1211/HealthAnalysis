# Health Analysis

Raw wearable exports (Zepp / Mi Band ecosystem) covering **2026-05-12 to 2026-09-28 (140 days)**, plus a compiled daily summary spreadsheet and written analysis.

The data is split into two export periods:

| Period | Dates | Folder |
|---|---|---|
| P1 | 2026-05-12 to 2026-07-20 (70 days) | `Health Data (12-05-2026 to 20-07-2026)/` |
| P2 | 2026-07-21 to 2026-09-28 (70 days) | `Health Data(20-07-26 to 28-09-26)/` |

The two exports overlap on 2026-07-20. That day's data is identical in both, so it's counted once, in P1.

## Contents

### Raw data (as exported from the device app)

Each period folder has the same 11 category subfolders:

| Folder | Contents | P1 rows | P2 rows |
|---|---|---|---|
| `USER/` | Profile: name, gender code, height, weight, birthday | 1 | 1 |
| `BODY/` | Weight, height, BMI readings | 1 (63.0 kg, 2026-05-24) | 1 (65.0 kg, 2026-07-28) |
| `HEALTH_DATA/` | Body measurements (arm/calf/chest/hip/thigh/waist). Empty, never filled in | 0 | 0 |
| `ACTIVITY/` | Daily steps, distance, run distance, activity calories | 70 | 71 |
| `ACTIVITY_MINUTE/` | Minute-level step counts (only minutes with steps recorded) | 13,077 | 12,964 |
| `ACTIVITY_STAGE/` | Continuous-movement segments (start/stop time, distance, calories, steps) | 674 | 750 |
| `SLEEP/` | Daily sleep summary: deep/light/REM minutes, wake time, sleep start/stop, naps | 70 | 71 |
| `SLEEP_MINUTE/` | Minute-by-minute sleep stage with heart rate and respiratory rate | 30,639 | 32,606 |
| `HEARTRATE_AUTO/` | Automatic heart-rate readings (roughly per minute) | 97,023 | 98,863 |
| `HEARTRATE/` | Manual heart-rate readings. Empty, none logged | 0 | 0 |
| `SPORT/` | Logged workouts: type code, start time, duration, pace, distance, calories | 66 | 73 |

### Compiled output

- **[`report/REPORT.md`](report/REPORT.md)**: the full P1 vs P2 comparison and trend analysis. It covers every metric, with 17 charts (in `report/charts/`), significance tests, 140-day trend lines, and how training, sleep and heart rate affect each other.
- **`ANALYSIS.md`**: short summary of the key findings, plus the maintenance-calorie method.
- **`Daily_Health_Summary.xlsx`**: all 140 days merged from both exports. Tabs:
  - **Daily Summary**: one row per day covering:
    - period and week
    - steps, distance, active minutes, activity and workout calories
    - resting, average, max and sleeping heart rate, plus vigorous minutes
    - workouts
    - the full sleep-stage breakdown, with the times you fell asleep and woke up
    - estimated calories burned
  - **Workout Sessions**: all 139 workouts with inferred activity name, start time, duration, distance, pace (min/km), calories per minute, and average and max heart rate during the session.
  - **Period Comparison**: P1 vs P2 side by side, with change and % change. Every value is a live formula over the other tabs.
  - **Weekly Trends**: weekly averages for steps, resting and sleeping HR, sleep and workouts, with line charts.
  - **Notes**: every assumption made while merging and aggregating the raw CSVs.

### Scripts

| Script | What it does |
|---|---|
| `scripts/healthdata.py` | Loads and merges every `Health Data*` export, removes duplicate days, converts all times to IST, and builds the daily and per-workout tables. |
| `scripts/build_summary.py` | Rebuilds `Daily_Health_Summary.xlsx`. Open it in Excel once afterwards so the formulas calculate. |
| `scripts/build_report.py` | Regenerates the charts in `report/charts/` and prints the statistics used in `REPORT.md`. |

Requires Python 3 with `pandas`, `numpy`, `scipy`, `matplotlib` and `openpyxl`.

## Known data-quality caveats

- **No HRV.** Not recorded in either export.
- **No food or calorie-intake log.** Only calories *out* are recorded.
- **No real weight trend.** There are two weight readings (63.0 kg on 2026-05-24, 65.0 kg on 2026-07-28), and the second looks like a profile update rather than a scale reading. So there's nothing to check any maintenance-calorie estimate against.
- **Sleep `naps` field is a placeholder.** Every nap timestamp in both exports reads `2024-10-04`, well outside the real date range, so only nap *counts* are usable.
- **Workout names are inferred, not labeled by the device.** Zepp exports sessions as numeric type codes with no name. Labels were inferred from each code's distance, pace and intensity. Two codes are new in P2: 191 (indoor, high intensity, from 2026-08-19) and 9 (one 21 km session at ~16.6 km/h, most likely cycling).
- **GPS dropouts.** Two sessions logged almost no distance for their length (2026-06-25 run: 59 min for 58 m; 2026-08-19 walk: 32 min for 152 m). Pace is left blank for any session under 500 m.
- **Mixed timezones in the export.** `HEARTRATE_AUTO`, `ACTIVITY_MINUTE`, `ACTIVITY_STAGE` and `SLEEP_MINUTE` are in local time (IST, UTC+5:30). `SPORT` start times, `SLEEP` start/stop and `BODY` are UTC. The scripts convert everything to IST. The offset was confirmed by lining up workouts with heart-rate spikes: 79 of 129 sessions peak at exactly +5:30.
- **The minute-level step file leaves out workout steps.** `ACTIVITY_MINUTE` doesn't include steps taken during logged workouts, so on run days its total falls short of the daily `ACTIVITY` figure.
- **Respiratory rate is empty.** The `respiratory_rate` column in `SLEEP_MINUTE` has no values in either export.

## Adding a new export

Drop the new export into the repo root as another `Health Data...` folder with the same 11 subfolders, then run:

```bash
python3 scripts/build_summary.py && python3 scripts/build_report.py
```

Each export becomes its own period (P3, P4, …). Overlapping days are de-duplicated, and the new period appears automatically in the workbook, the comparison tab and every chart. The written narrative in `report/REPORT.md` then needs updating to match the new numbers.
