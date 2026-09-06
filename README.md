# Health Analysis

Raw wearable export (Zepp / Mi Band ecosystem) covering **2026-05-12 to 2026-07-20 (70 days)**, plus a compiled daily summary spreadsheet and written analysis.

## Contents

### Raw data (as exported from the device app)

| Folder | Contents |
|---|---|
| `USER/` | Profile: name, gender code, height, weight, birthday |
| `BODY/` | Single body-composition reading (2026-05-24): weight, height, BMI |
| `HEALTH_DATA/` | Body measurements (arm/calf/chest/hip/thigh/waist) — empty, never filled in |
| `ACTIVITY/` | Daily steps, distance, run distance, activity calories |
| `ACTIVITY_MINUTE/` | Minute-level step counts (only minutes with steps recorded) |
| `ACTIVITY_STAGE/` | ~675 continuous-movement segments (start/stop time, distance, calories, steps) |
| `SLEEP/` | Daily sleep summary: deep/light/REM minutes, wake time, sleep start/stop, naps |
| `SLEEP_MINUTE/` | ~30,600 minute-by-minute sleep-stage entries with heart rate & respiratory rate |
| `HEARTRATE_AUTO/` | ~97,000 automatic heart-rate readings (roughly per-minute) |
| `HEARTRATE/` | Manual heart-rate readings — empty, none logged |
| `SPORT/` | 66 logged workout sessions: type code, start time, duration, pace, distance, calories |

### Compiled output

- **`Daily_Health_Summary.xlsx`** — one row per day (70 rows) combining steps, distance, activity/workout calories, active minutes, resting/avg/max heart rate, workout details, and full sleep-stage breakdown. Includes a raw workout-sessions tab and a Notes tab documenting every assumption made while aggregating the raw CSVs (see the workbook's own "Notes" sheet for full detail).
- **`ANALYSIS.md`** — written findings and calorie-maintenance estimate derived from this data.

## Known data-quality caveats

- **No HRV** — not tracked anywhere in this export.
- **No food/calorie-intake log** — only calories *out* are recorded, never calories *in*.
- **Only one body-weight reading** in the whole export (63.0 kg, 2026-05-24) — no weight trend to validate any maintenance-calorie estimate against.
- **Sleep `naps` field is corrupted/placeholder** — every nap timestamp in the source data reads `2024-10-04`, well outside the real 2026 date range, so only nap *counts* are usable, not timing.
- **Workout activity names are inferred, not device-labeled** — Zepp exports sport sessions as numeric type codes with no name field; labels in the summary were inferred from each code's typical distance/pace pattern and should be treated as best-effort, not confirmed.
- **Sport sessions are grouped by UTC calendar date** of their start time, since the source file has no separate local-date field; a session starting near midnight UTC could land on the "wrong" local day.
