# CM21 Chukyo 1200m — Sakura Bakushin O simulated nine-runner study

**Date:** October 23, 2026.  **Status:** Completed exploratory numerical experiment; NOT validated game-engine output or actual Global matchmaking win rates.

## What was actually executed

Two reproducible seed batches, each with **400 nine-runner pseudo-races** for every combination of:
- Four racing-style compositions: 1F/5P/0L/3E; 1F/4P/1L/3E; 2F/4P/0L/3E; 3F/4P/0L/2E.
- Three hypothetical competing-field training standards: mixed, competitive, elite.
- Five user skill-purchase packages, including no purchases, 1,886-SP opening/finishing core, 2,731-SP balanced package (I Wanna Win With You), 2,693-SP contested-front package (Top Runner), and 2,580-SP White Turbo + Focus package.

**Total: 4 x 3 x 5 x 400 x 2 = 48,000 simulated nine-runner races.** Each row in `combined_results.csv` aggregates 800 races across both seed batches. The user build, original unique and track conditions are constant.

## Key observed *model output*, not real-world probabilities

Against the model's 'competitive' opposing field, the illustrative individual pseudo-win rates were:

| Lobby | Balanced + IWW | Top Runner alternative |
| --- | ---: | ---: |
| 1 Front / 5 Pace / 3 End | 32.0% | 32.25% |
| 1 Front / 4 Pace / 1 Late / 3 End | 37.62% | 36.62% |
| 2 Front / 4 Pace / 3 End | 29.5% | 29.25% |
| 3 Front / 4 Pace / 2 End | 37.62% | 35.88% |

Differences between the two full-budget packages are smaller than Monte Carlo variability and dwarfed by uncertainty from approximate lane, pack, and skill mechanics. With 800 simulations at p≈0.33, approximate binomial 95% sampling error is ±3.3 percentage points for an individual percentage; **systematic model uncertainty is far larger**.

## Track representation

- Chukyo turf 1200 m, left, firm, sunny, winter.
- Opening 0–200 m, middle 200–800 m, final 800–1000 m, last spurt 1000–1200 m.
- Downhill 100–875 m (+0.3 target speed while Downhill Mode and 60% lower HP expenditure); uphill 875–975 m (lower acceleration and speed).
- Final straight begins 788 m; final leg begins at 800 m.
- 15 ticks/s. Individual runners have physically evolving track positions, approximate acceleration and target speed, true within-frame finish-order interpolation, and conditional rank checks for positioning skills.
- Bakushin's unique is a side-by-side proxy; Victoria por plancha checks 1st/2nd; Top Runner requires mid/opening position improvement or 2 s side interaction; See Ya Later checks a runner behind in the same lane for 3 s after 10 s.

## IMPORTANT limitations

1. **There is no live CM21 matchmaking population on Oct. 23, 2026.** Global CM21 starts later; the only 'live data' used to inform scenario choices are October 2026 pre-CM community discussions and then-current game-guide information. An arbitrary relative sample of public discussions cannot establish character usage shares.
2. Historic JP January 2023 measurements disagree by sample: Altema's room matches recorded 7.7% Fronts, 49.8% Paces, 8.0% Lates, 34.5% Ends; a separate 259-entry Round 2 Graded League collection reported 16.2% Fronts, 59.8% Paces, 12% Lates, 12% Ends. We use explicit scenarios rather than pretending either is the true current Global average.
3. **Opponent stat and skill distributions are invented assumptions**, not downloaded opponent cards. The 'mixed', 'competitive', and 'elite' fields intentionally vary Speed, Power, Wit, Guts, stamina, aptitudes, race skills; see `study_seed1.json` for their numerical parameters.
4. **This isn't the official game engine or Umalator.** It approximates position keep, leader overtake modes, Wit checks, late dueling, continuous lanes, HP planning, per-skill triggers, opponent skill packages, and character-specific behavior. Some skills (especially Operation Cacao) are over-generously triggered; others may be missed.
5. Real Champions Meeting is 3v3v3. Because the user's other two trainees were not supplied, the other eight runners are generic *placeholders*, not a genuine three-team setup; **this cannot predict the user's team win rate**.
6. Absolute win rate is **extremely sensitive** to how position-keeping speed-up and pace-down rules are approximated; a simpler alternative implementation produced a very different absolute figure. Prioritize broad within-model rankings over percentages.
7. Package swaps include multiple skills; White Turbo + Focus is **not a controlled Turbo-only ablation**. Do not interpret its poorer performance as a precisely measured gold Turbo gain.
8. The sample nine-runner roster is a concrete numerical draw from the *assumed distributions*. Archetype labels such as “Nishino-like Pace” don't represent a real opponent build or a verified complete skill kit. The script exports Bakushin's finish place, not a full result sheet for all runners.

## Findings with practical relevance

- Two fully budgeted gold-Turbo packages remain approximately tied across scenarios.
- Victoria's activation becomes less certain with additional Front Runners. Top Runner's modeled activation becomes more frequent, but this did not produce a statistically distinguishable package advantage.
- HP exhaustion was not observed for Bakushin under any of these modeled assumptions; this is not a guarantee against stamina debuffs or different HP mechanics.
- The model supports taking Victoria por plancha, a complete Groundwork opening setup, and late-race acceleration seriously. It **does not prove** that the published 2,731-SP full shopping list is optimal.

## Reproduce

Install Python 3.11+ and packages `numpy`, `numba` (and optionally `pandas` for your own analysis).

Run:

```bash
python cm21_nine_runner_pseudo_sim.py --trials 400 --seed 2120226 --output seed1
python cm21_nine_runner_pseudo_sim.py --trials 400 --seed 7654321 --output seed2
```

`combined_results.csv` averages the two batches. The simulator script is user-editable and declares all opponent distributions and package lists at the top.

## Sources consulted

- Course and current pre-CM guide: https://uma.guide/guides/cm21-guide
- Course sections and greens: https://www.mihonostudios.com/champions-meeting/21
- Racing mechanics and skills: https://umamusu.wiki/Game:Mechanics
- PVP team/front interactions: https://www.umareference.com/guide/pvp-champions-meeting/making-a-team
- Historical JP room matches: https://altema.jp/umamusume/capricornhaitier
- Separate JP Graded League historical sample: https://www.mihonostudios.com/champions-meeting/21
- Current community discussion on running styles: https://www.reddit.com/r/UmamusumeGame/comments/1x918dn/
- Skill condition reference: https://www.mihonostudios.com/database/skills/900141

Results should be calibrated against actual practice-room races or a validated game-engine simulator before committing SP.
