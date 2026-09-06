# Analysis Notes

Findings below are derived from the 70-day export (2026-05-12 to 2026-07-20). All figures are estimates from device data, not clinical or lab measurements — see the caveats in [README.md](README.md) and in `Daily_Health_Summary.xlsx`'s Notes tab.

## Activity & sleep patterns

- **Steps**: mean 7,893/day, median 6,496, range 1,833–24,675.
- **Sleep**: mean 6.55 h/night; **23 of 70 nights (33%) were under 6 hours**.
- **Bedtime consistency is the biggest red flag**, not sleep duration on average — bedtime swings with a ~2.6-hour standard deviation across a >15-hour window over the 70 days. Irregular sleep timing tends to hurt sleep quality more than total duration alone.
- **More steps in a day correlates with *less* sleep that night** (Pearson r = -0.46, moderate negative) — high-activity days are consistently cutting into sleep, not the reverse.
- The three lowest-sleep nights (2.4 h on 2026-05-26, 2.9 h on 2026-07-20, 3.2 h on 2026-05-30) all followed days with 9,000+ steps.
- **Sunday is the most active day** (avg 12,080 steps) but also the **worst sleep night** (5.84 h avg) — weekend activity appears to come at the cost of weekend sleep.
- Sleep architecture looks structurally normal: deep sleep ~18% of total, REM ~23% of total.
- Worked out on 50 of 70 days (71%).

## Resting heart rate

- Mean resting HR (daily minimum from continuous auto-readings): 42.2 bpm.
- No meaningful trend over the 10 weeks (42.6 bpm first half vs. 42.3 bpm second half — essentially flat).
- The two highest resting-HR days (53 bpm, vs. the 42 bpm average) both followed **under 4 hours of sleep combined with a hard workout that day** — poor sleep stacked on hard training looks like the clearest driver of elevated resting HR in this data, more than training load alone.

## Estimated maintenance calories (TDEE)

No food-intake log or repeated weight measurements exist in this export, so a true empirically-measured maintenance number isn't possible from this data alone. The figure below is a formula-based estimate, built bottom-up to avoid double-counting:

**Inputs used:** 65 kg, 172 cm (5'8"), 20 years old, ~12–14% body fat.

1. **BMR** — cross-checked two methods:
   - Mifflin-St Jeor (weight-based): 1,630 kcal
   - Katch-McArdle (lean-mass-based, using 12–14% BF): 1,577–1,606 kcal (1,591 at the 13% midpoint)
   - Both methods converge on **~1,590–1,630 kcal**, which is reassuring given the different inputs each uses.
2. **NEAT** (non-workout background steps) — isolated a kcal/step rate purely from rest days with zero logged workouts (~0.042 kcal/step at the device's on-file weight), then rescaled to actual body weight and applied only to steps not already attributed to a running/walking workout (to avoid counting those steps twice).
3. **Exercise** (gym, HIIT, runs — everything in `SPORT/`) — taken directly from each session's own device-reported calorie estimate, rescaled to actual body weight.

**Result:**

| | value |
|---|---|
| BMR | ~1,591 kcal |
| NEAT (avg/day) | ~285 kcal |
| Exercise (avg/day) | ~409 kcal |
| **Mean total** | **~2,286 kcal/day** |
| **Median (typical day)** | **~2,119 kcal/day** |

**Best estimate: maintenance is roughly 2,100–2,300 kcal/day**, with the median a better "typical day" figure than the mean (a handful of double-workout days pull the mean up).

### Why this might be an underestimate

Despite training frequently (running, gym, HIIT), the number lands lower than intuition suggests, for physiologically sound reasons:
- **BMR is capped by body mass, not training volume.** At 65 kg, BMR has a hard ceiling regardless of fitness level — a heavier person doing identical training would have a meaningfully higher BMR just from carrying more tissue.
- **A hard session burns less than it feels like.** Calorie burn during exercise scales with body weight; at 65 kg, even demanding sessions (HIIT, resistance training) come out to roughly 250–600 kcal per session by MET-table math, which matches the device's own logged numbers reasonably well.
- **Wearable HR-based calorie algorithms are known to underestimate resistance training specifically**, since they lean on heart-rate response rather than mechanical work. This is the one place the estimate could plausibly run high by a few hundred kcal/day.

**The only way to resolve this for certain**: log food intake consistently (e.g. ~2,300–2,500 kcal/day) for 2–3 weeks while weighing in every few days at the same time of day. Whatever intake keeps weight flat over that window is the real maintenance number — no formula substitutes for that test.
