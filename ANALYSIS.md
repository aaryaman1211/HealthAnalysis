# Analysis Notes

Findings from 140 days of device data (2026-05-12 to 2026-09-28), split into two 70-day periods:

- **P1:** 2026-05-12 to 2026-07-20
- **P2:** 2026-07-21 to 2026-09-28

All figures are estimates from a wearable, not clinical measurements. See the caveats in [README.md](README.md) and the Notes tab of `Daily_Health_Summary.xlsx`.

## P1 vs P2 at a glance

| Metric | P1 | P2 | Change |
|---|---|---|---|
| Avg steps / day | 7,893 | 7,823 | -1% |
| Avg active minutes / day | 149 | 158 | +6% |
| Avg resting HR (bpm) | 42.2 | 41.4 | -0.8 |
| Avg all-day HR (bpm) | 65.0 | 62.1 | -2.9 |
| Workout days | 50 | 46 | -4 |
| Workout sessions | 66 | 73 | +7 |
| Avg workout calories / day | 396 | 430 | +9% |
| Runs logged | 12 | 10 | -2 |
| Total run distance (km) | 84.7 | 63.6 | -25% |
| Avg sleep (hours) | 6.55 | 6.04 | -0.51 |
| Nights under 6 h | 23 | 36 | +13 |
| Avg REM (min) | 93 | 81 | -12 |
| Bedtime variation (std dev, hours) | 2.56 | 1.77 | more consistent |

## Fitness: modest but real improvement

- **Heart rate is down.** Resting HR fell 0.8 bpm and average all-day HR fell almost 3 bpm. A lower heart rate at similar activity levels is one of the better cardio-fitness signals a wearable gives.
- **Running got faster at the same distances.** Average pace looks flat (6:25 vs 6:26 per km) because P2 mixes very different runs. Comparing like with like:

  | Run | P1 | P2 |
  |---|---|---|
  | ~10 km | 6:23/km (2026-05-29) | 5:16/km (2026-09-08) |
  | ~4–5 km | 5:34–5:52/km | 5:05–5:12/km |

  This is the clearest improvement in the data.
- **Training shifted toward high-intensity indoor work.** Sessions rose 66 to 73 but on fewer days, so there are more double-session days. A new session type (code 191) started on 2026-08-19: 9 sessions of about 55–100 minutes at roughly 650 kcal each, the heaviest regular session in the data. Running volume dropped by about a quarter.

## Sleep: shorter, but better timed

- **Less sleep.** Average sleep fell half an hour to 6.04 h, and more than half of P2's nights (36 of 70) were under 6 hours. REM dropped by about 12 minutes a night.
- **Timing improved.** Bedtime moved about 1.6 hours earlier and became much more regular: the std dev fell from 2.6 to 1.8 hours. The P1 finding that bedtime timing was the biggest problem has partly been fixed. The remaining problem is the length of the night.
- **The worst weeks line up with hard training.** The weeks starting 2026-07-27 and 2026-09-07 both averaged about 4.9 h of sleep, and 09-07 was the heaviest training week in P2 (about 620 kcal/day of workouts).
- **Activity and sleep are less tied together.** In P1, busier days strongly predicted shorter nights (r = -0.46). In P2 that link is weaker (r = -0.23), consistent with the more regular bedtime.
- Sleep structure still looks normal: deep sleep is about 17–18% of total in both periods.

## P1 detail (first 70 days)

- **Steps:** median 6,496, range 1,833–24,675.
- **Worst nights:** the three lowest-sleep nights (2.4 h on 2026-05-26, 2.9 h on 2026-07-20, 3.2 h on 2026-05-30) all followed days with 9,000+ steps.
- **Weekly pattern:** Sunday was the most active day (avg 12,080 steps) and the worst sleep night (5.84 h avg).
- **Resting-HR spikes:** the two highest resting-HR days (53 bpm) both combined under 4 hours of sleep with a hard workout that day. Poor sleep stacked on hard training looks like the clearest driver of raised resting HR.

## Estimated maintenance calories (TDEE)

There's no food-intake log and no real weight trend, so a measured maintenance number isn't possible. The estimate below is built bottom-up and avoids double-counting.

**Inputs:** 65 kg, 172 cm (5'8"), 20 years old, ~12–14% body fat.

1. **BMR:** Katch-McArdle (lean-mass based) gives 1,577–1,606 kcal (1,591 at 13% body fat). Mifflin-St Jeor (weight based) gives 1,630 kcal. The two methods agree closely.
2. **NEAT (non-workout movement):** a calories-per-step rate taken only from rest days with no workouts, applied to steps that don't belong to a logged run or walk. This keeps those steps from being counted twice.
3. **Exercise:** each SPORT session's own calorie estimate (gym, HIIT, runs, everything). P1 values are scaled from the device's 63 kg profile to 65 kg; the P2 profile was already 65 kg.

| | P1 | P2 |
|---|---|---|
| BMR | ~1,591 | ~1,591 |
| NEAT (avg/day) | ~285 | ~310 |
| Exercise (avg/day) | ~409 | ~430 |
| **Mean total** | **~2,285 kcal/day** | **~2,332 kcal/day** |
| **Median (typical day)** | **~2,119 kcal/day** | **~2,136 kcal/day** |

**Best estimate: maintenance is about 2,100–2,350 kcal/day.** It rose slightly in P2 because of the heavier indoor sessions. The median is the better "typical day" figure, since a few double-workout days pull the mean up.

### Why this might be an underestimate

- **BMR is set by body mass, not training volume.** At 65 kg BMR has a ceiling, however fit you are.
- **A hard session burns less than it feels like.** At 65 kg, even demanding sessions come to roughly 250–650 kcal by MET-table math, which matches the device's numbers.
- **Wearables tend to undercount resistance training.** Their calorie estimates lean on heart rate rather than mechanical work, so the true figure could run a few hundred kcal/day higher.

**The only way to know for certain:** log food intake (e.g. ~2,300–2,500 kcal/day) for 2–3 weeks and weigh in every few days at the same time of day. Whatever intake keeps your weight flat is your real maintenance number.
