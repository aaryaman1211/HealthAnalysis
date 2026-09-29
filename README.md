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

- **`Daily_Health_Summary.xlsx`**: all 140 days merged from both exports. Tabs:
  - **Daily Summary**: one row per day with period, week, steps, distance, activity and workout calories, active minutes, resting/avg/max heart rate, workouts, and the full sleep-stage breakdown.
  - **Workout Sessions**: all 139 workouts with inferred activity name, duration, distance, pace (min/km) and calories per minute.
  - **Period Comparison**: P1 vs P2 side by side, with change and % change. Every value is a live formula over the other tabs.
  - **Weekly Trends**: weekly averages for steps, resting HR, sleep and workouts, with line charts.
  - **Notes**: every assumption made while merging and aggregating the raw CSVs.
- **`ANALYSIS.md`**: written findings, the P1 vs P2 comparison, and maintenance-calorie estimates.

## Known data-quality caveats

- **No HRV.** Not recorded in either export.
- **No food or calorie-intake log.** Only calories *out* are recorded.
- **No real weight trend.** There are two weight readings (63.0 kg on 2026-05-24, 65.0 kg on 2026-07-28), and the second looks like a profile update rather than a scale reading. So there's nothing to check any maintenance-calorie estimate against.
- **Sleep `naps` field is a placeholder.** Every nap timestamp in both exports reads `2024-10-04`, well outside the real date range, so only nap *counts* are usable.
- **Workout names are inferred, not labeled by the device.** Zepp exports sessions as numeric type codes with no name. Labels were inferred from each code's distance, pace and intensity. Two codes are new in P2: 191 (indoor, high intensity, from 2026-08-19) and 9 (one 21 km session at ~16.6 km/h, most likely cycling).
- **GPS dropouts.** Two sessions logged almost no distance for their length (2026-06-25 run: 59 min for 58 m; 2026-08-19 walk: 32 min for 152 m). Pace is left blank for any session under 500 m.
- **Workouts are grouped by UTC calendar date** of their start time, since the SPORT file has no local-date field. A session starting near midnight UTC could land on the neighboring local day.

## Adding a new export

Drop the new export into the repo root as another `Health Data...` folder with the same 11 subfolders. The summary merges every `Health Data*` folder and de-duplicates overlapping days, so the workbook can be rebuilt to cover the new period.
