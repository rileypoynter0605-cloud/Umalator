# Codex task: independently validate CM21 Sakura Bakushin O skill purchases using Umalator

## Goal

Install and run the best currently applicable **Global Umamusume** Umalator implementation, understand its actual race/skill simulation code, and use it to audit and refine a player's skill purchase plan for Sakura Bakushin O in CM21. The user has NOT purchased any listed skills and needs a credible best-value 2751-SP set. The attached existing Python nine-runner model and outputs are **approximate prior exploratory work**, not the official game engine or validated win rates.

### Useful source repositories

1. Andrew's fork (candidate best workflow for local batch comparisons): https://github.com/Andrew123Shi/Umalator
2. Kachi fork: https://github.com/kachi-dev/uma-tools
3. Original: https://github.com/alpha123/uma-tools

Andrew's project README says its global skill chart, Monte Carlo compare, unique levels, and optional stamina handling are improved. Inspect the current repo, verify skill/game-data version and applicability to Global October 2026, and choose a sound implementation. Avoid assuming Andrew's Windows Electron packaged EXE can execute on a Linux cloud runner; use Node/TypeScript source or a browser automation harness if needed. Record exact commit hash/branch, Node version, command lines and any patches. If the source doesn't support headless batch runs, write an external harness, CLI wrapper, or minimal tests that invoke its own simulation functions rather than inventing another simulator.

## Fixed build

- Sakura Bakushin O, original/default outfit. Her existing unique is **Genius × Bakushin = Victory**, at **level 4**. Preserve existing unique; do not count it toward SP spend.
- Stats in order Speed/Stamina/Power/Guts/Wit: **1515 / 402 / 1003 / 695 / 976**.
- Aptitudes: **Turf S / Sprint S / Front Runner A**.
- Fans: 271,088; relevant for skill effects such as I Wanna Win With You.
- Available unspent skill points: **2,751**.
- CM21 Capricorn Cup (Takamatsunomiya Kinen): Chukyo Turf 1200m, left-handed, winter, sunny, firm (ensure course conditions are verified against the user's Global event).
- Important track geometry: long downhill roughly 100–875m, uphill 875–975m; final straight begins ~788m; final phase around 800m. ***Reverify actual course geometry from simulator data.***
- No extra purchased skills are claimed beyond native unique. Treat available shop entries below as alternatives.

## Exact available skill costs as supplied by the player

```
Victoria por Plancha                        120
Operation Cacao                            140
Prideful King                              180
Standard Distance ○ / ◎                     81 / 99 incremental
Firm Conditions ○ / ◎                        81 / 99 incremental
Winter Runner ○ / ◎                          81 / 99 incremental
Outer Post Proficiency ○ / ◎                 81 / 99 incremental
Professor of Curvature / Corner Adept      306 / 180 (gold versus white, not additive)
Straightaway Adept                         153
Focus                                      126
Early Lead                                  72
Fast-Paced                                 162
Final Push                                 117
Turbo Sprint / Sprinting Gear              320 / 160 (gold versus white, not additive)
Staggering Lead / Huge Lead                306 / 136 (gold versus white, not additive)
Countermeasure                             160
Front Runner Straightaways ○ / ◎           91 / 98 incremental
Top Runner / Leader's Pride                342 / 180 (gold versus white, not additive)
Moxie                                      126
Front Runner Savvy ○ / ◎                    88 / 104 incremental
Groundwork                                  80
Tail Held High                              90
See Ya Later / Playtime's Over             208 / 96 (gold versus white, not additive)
Light as a Feather                         144
Mad Dash                                   126
I Wanna Win With You / On the Way to Our Dream 380 / 200 (gold versus white, not additive)
```

Note: some skill names/cost-pair ordering depend on the game shop representation. Confirm whether gold/white and ○/◎ are upgrades, mutually exclusive, or incremental. Account for all prerequisites and exact SP totals. Do NOT assume our previous simulator's cost handling was perfect.

## Prior experimental evidence attached

The `cm21_nine_runner_pseudo_sim.py` file is OUR CUSTOM approximate nine-runner model written for this conversation, not Umalator or Cygames code. Its `ORIGINAL_STUDY_README.md` explains implementation and limitations. Reproduce and audit BEFORE using as an external baseline:

```
python cm21_nine_runner_pseudo_sim.py --trials 400 --seed 2120226 --output seed1
python cm21_nine_runner_pseudo_sim.py --trials 400 --seed 7654321 --output seed2
```

Dependencies Python 3.11+, numpy, numba. The attached study input JSONs and seed results provide reproducibility comparisons, and `combined_results.csv` provides prior aggregate output. If dependencies aren't available, report that fact. Never claim a run completed unless verified logs/files were produced.

Prior experiment design: 4 lobby-style compositions × 3 **hypothetical** opponent strength tiers (mixed / competitive / elite) × 5 skill packages × 400 runs × 2 batches = **48,000 pseudo-races**. The four compositions were 1F5P3E, 1F4P1L3E, 2F4P3E and 3F4P2E. This was NOT empirical Global matchmaking, as CM21 wasn't yet underway when the sample was constructed. All opponent stats, skill rosters, character behavior are assumptions; no actual rival training cards were obtained.

The primary packages in that script are:
- 2731 SP **balanced**: Victoria, Operation Cacao, Winter Runner ○, Firm Conditions ○, Professor of Curvature, Straightaway Adept, Early Lead, Fast-Paced, Final Push, Turbo Sprint, Front Runner Straightaways ◎ [91+98], Front Runner Savvy ○, Groundwork, Tail Held High, See Ya Later, Light as a Feather, I Wanna Win With You.
- 2693 SP **contested-front**: same as balanced but replace I Wanna Win With You (380) with Top Runner (342).
- 2580 SP **White Turbo + Focus**: a multi-skill swap, NOT an isolated gold vs. white Turbo ablation.
- 1886 SP opening/finishing core and a no-purchases baseline.

The earlier pseudo-win rates are not reliably interpretable as real CM win probabilities. For example, the model yielded near-tied 32.0 vs 32.25% in one competitive pace-heavy condition, but this cannot support a fractional win probability prediction. Some effects/conditions are approximated generously and the solver is sensitive to position keep.

### Required audit of our custom code

- Confirm race phases and downhill-mode target speed vs actual movement speed, activation chance, exit chance, and HP conservation.
- Check 15 ticks/second numerical integration, crossing interpolation, spurt planner, phase/slope modifiers, lane/blocking proxy, rank checks, order/position checks, start delay, Wit checks, and whether all rivals are actually represented as evolving agents.
- Check whether conditions for **Genius × Bakushin = Victory, Victoria por Plancha, Operation Cacao, Groundwork, Top Runner, See Ya Later, Turbo Sprint, I Wanna Win With You** reflect actual game data. Point out incorrect triggers/effect units/durations. Validate SP math and competing package choices.
- Check seeding/independence. Show reproducibility diffs versus attached inputs or explain why different.
- Explicitly separate *randomization uncertainty* from the substantially larger *model structural uncertainty*.

## Proposed Umalator experiments

1. **Baseline validation**. Run Bakushin with native unique only, proper unique level 4, all aptitudes, course, and HP policy. Report timing/HP distribution, skill activation checks, any abnormal slope-mode handling, and a deterministic replay if possible.
2. **Single-skill ablations** using common random seeds: each listed skill individually added to the baseline when technically valid. Record seconds or distances gained, activation rate and timing distribution, and whether effectiveness depends on simulated runner position. Report conditions the engine cannot represent.
3. **Upgrade ablations** using identical remaining skills: white Sprinting Gear vs. Turbo Sprint gold; Corner Adept vs Professor of Curvature; Leader's Pride vs Top Runner; Playtime's Over vs See Ya Later; On the Way to Our Dream vs I Wanna Win With You; front runner greens ○ vs ◎. Do not change two skills simultaneously in a comparison claimed to isolate one.
4. **Budget optimization**: assess 2751-SP packages, accounting for prerequisites, overlapping/competing skills, the Groundwork opening three-skill requirement, and maximum useful combination rather than blindly buying all the seemingly good skills. Generate top 3 *explicit shop-order purchase lists*, total SP, remaining SP. Record uncertainty about positional skills.
5. **Opponent-sensitivity tests**: if the Umalator API permits comparison against constructed rivals, test solo-front vs competing Front Runner vs Pace-heavy. Umalator's pairwise simulations don't imply realistic 9-runner win rates! If it supports only 1v1, state exactly that; don't forge 9-runner Umalator outputs.
6. **Our nine-runner calibration**: compare fundamental mechanics with our script, identify divergences, optionally patch OUR script as an explicitly experimental model, then rerun side-by-side tests without claiming new engine fidelity. Opponent build distributions must be labeled synthetic.
7. **Conclusions**: identify skills with strong, repeatable expected impact in the Umalator engine; distinguish those requiring genuine lobby proximity/rank from those that work in isolation; provide the most justified actual spend recommendation (including rationale when it differs from our 2731-SP initial proposal). Also flag any source/game-version uncertainties.

## Output artifacts requested

- `INSTALL_AND_VERIFICATION.md`: repo/commit, installation steps, tools and tests, warnings.
- `REPRO_AUDIT.md`: what our Python model did, where it misrepresented mechanics, which reported findings remain robust.
- `skill_ablation.csv`: each skill, cost, absolute and relative performance measure, trials, effect timing and limitations.
- `package_comparison.csv`: packages, SP, baseline-relative outcome under *paired random seeds* and uncertainty intervals.
- `recommended_shop_order.md`: top 3 budget-legal packages, exact shop-order item prices and SP totals, plus explicit caution against buying until checked.
- Scripts/patches needed to reproduce all comparisons. Do not silently modify upstream game data; declare any patches.

Prioritize scientific reproducibility over the appearance of precise output. ***If not feasible to simulate a realistic nine-runner lobby with the existing code, say so.*** Deliver validated pairwise/solo Umalator analyses instead of pretending to have validated win rates.
