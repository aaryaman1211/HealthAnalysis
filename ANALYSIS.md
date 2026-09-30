# Analysis Notes

Key findings from 140 days of device data (2026-05-12 to 2026-09-28), split into two 70-day periods:

- **P1:** 2026-05-12 to 2026-07-20
- **P2:** 2026-07-21 to 2026-09-28

All times are IST (UTC+5:30). **The full analysis, with charts, significance tests and trend lines, is in [report/REPORT.md](report/REPORT.md).** This page is the short version, plus the method behind the maintenance-calorie estimate.

All figures are estimates from a wearable, not clinical measurements. See the caveats in [README.md](README.md).

## P1 vs P2 at a glance

| Metric | P1 | P2 | Change | Significance |
|---|---|---|---|---|
| Avg steps / day | 7,893 | 7,823 | -1% | none |
| Avg active minutes / day | 149 | 158 | +6% | none |
| Resting HR (daily low, bpm) | 42.2 | 41.4 | -0.8 | borderline (p = 0.055) |
| Sleeping HR (night avg, bpm) | 48.6 | 47.4 | -1.2 | borderline (p = 0.077) |
| All-day avg HR (bpm) | 65.0 | 62.1 | -2.9 | **yes (p = 0.004)** |
| Workout sessions | 66 | 73 | +7 | – |
| Avg workout calories / day | 396 | 430 | +9% | none |
| Run efficiency (m per heartbeat) | 0.956 | 1.036 | +8% | suggestive (p = 0.07) |
| Avg sleep (hours) | 6.55 | 6.04 | -0.51 | **yes (p = 0.028)** |
| Nights under 6 h | 23 | 36 | +13 | – |
| Avg REM (min) | 93 | 81 | -12 | **yes (p = 0.027)** |
| Fell asleep | 03:21 | 01:38 | 1 h 42 earlier | **yes (p < 0.001)** |
| Woke up | 10:28 | 07:54 | 2 h 33 earlier | **yes (p < 0.001)** |

## Main findings

- **Fitness improved modestly.**
  - All-day heart rate dropped about 3 bpm, and resting and sleeping HR each dropped about 1 bpm.
  - Running got more efficient: you ran 5:05–5:16/km in September at distances you ran at 5:34–6:23/km in May–June, at a similar or lower heart rate.
- **Your sleep schedule moved about two hours earlier and became more regular,** but the wake-up moved further than the bedtime. Nights are now about 30 minutes shorter, and more than half of P2's nights were under 6 hours. REM, which comes mostly late in the night, took most of the loss.
- **Training doesn't shorten your sleep.** Workout load on a given day has no relationship with that night's sleep length (ρ = +0.06).
  - It does raise that night's sleeping heart rate (ρ = +0.25, p = 0.004). That's normal recovery load.
  - The link that is strong runs the other way: **short nights come before busy days** (ρ = -0.35, p < 0.001), which points to early starts.
- **Rest weeks are clearly visible as recovery.** The two lightest training weeks (6 Jul, 14 Sep) had the best sleep (7.4 h), and 14 Sep also had the lowest resting and sleeping HR in the data.
- **Resting-HR spikes come from short sleep stacked on hard training.** The two 53 bpm days (24 May, 27 Jun) both combined under 4 hours of sleep with a hard workout.

> **Correction:** an earlier version of this page said "more steps in a day correlates with less sleep that night (r = -0.46)". That paired each day with the sleep record of the *same date*, which is the night *before*. Paired correctly, activity doesn't predict that night's sleep. Short sleep predicts a busier *next* day.

## Estimated maintenance calories (TDEE)

There's no food-intake log and no real weight trend, so a measured maintenance number isn't possible. The estimate below is built bottom-up and avoids double-counting.

**Inputs:** 65 kg, 172 cm (5'8"), 20 years old, ~12–14% body fat (user-provided).

1. **BMR:** Katch-McArdle (lean-mass based) gives 1,577–1,606 kcal (1,591 at 13% body fat). Mifflin-St Jeor (weight based) gives 1,630 kcal. The two methods agree closely.
2. **Everyday movement (NEAT):** a calories-per-step rate taken only from rest days with no workouts, applied to steps that don't belong to a logged run or walk. This keeps those steps from being counted twice.
3. **Exercise:** each workout's own calorie estimate (gym, HIIT, runs, everything).
4. **Weight scaling:** device calories are rescaled from the export's profile weight (63 kg in P1, 65 kg in P2) to 65 kg.

| | P1 | P2 |
|---|---|---|
| BMR | ~1,591 | ~1,591 |
| NEAT (avg/day) | ~276 | ~310 |
| Exercise (avg/day) | ~409 | ~430 |
| **Mean total** | **~2,277 kcal/day** | **~2,332 kcal/day** |
| **Median (typical day)** | **~2,112 kcal/day** | **~2,136 kcal/day** |

**Best estimate: maintenance is about 2,100–2,350 kcal/day.** The median is the better "typical day" figure, since a few double-workout days pull the mean up.

### Why this might be an underestimate

- **BMR is set by body mass, not training volume.** At 65 kg, BMR has a ceiling however fit you are.
- **A hard session burns less than it feels like.** At 65 kg, even demanding sessions come to roughly 250–650 kcal by MET-table math, which matches the device's numbers.
- **Wearables tend to undercount resistance training.** Their calorie estimates lean on heart rate rather than mechanical work, so the true figure could run a few hundred kcal/day higher.

**The only way to know for certain:** log food intake (e.g. ~2,300–2,500 kcal/day) for 2–3 weeks and weigh in every few days at the same time of day. Whatever intake keeps your weight flat is your real maintenance number.
