# CM21 Umalator research task

## Objective
Audit a previous custom race simulator and produce evidence-based skill purchase recommendations for Sakura Bakushin O in Global CM21 / Capricorn Cup, Chukyo Turf 1200m, left-handed, winter, sunny, firm.

## Fixed trainee
- Sakura Bakushin O, Front A / Sprint S / Turf S
- Stats Speed 1515, Stamina 402, Power 1003, Guts 695, Wit 976
- Level 4 native unique; fans 271,088; unspent SP 2,751
- Do not spend SP or change the character; this is a research comparison.

## Required input
The user will add `CM21_Codex_Handoff.zip` to this branch. Unzip it to `cm21-study/`, then read `cm21-study/START_HERE.md` and `cm21-study/CODEX_TASK.md`. The archive includes previous Python simulators, configuration, baseline assumptions, samples, and result tables.

## Research expectations
1. Confirm course layout (long downhill, final uphill), pace phases, key skill triggers and their live Global implementations from the local Umalator source/game data. Explain any discrepancy.
2. Reproduce and critically audit the previous 9-runner pseudo-simulation. **Never interpret pseudo-sim win percentages as measured CM win rates.**
3. Find a reproducible programmatic path to Umalator's real mechanics; distinguish its supported one-/two-runner comparisons from nine-runner interactions it cannot model.
4. Compare legal skill packages within 2,751 SP, isolating one variable at a time as well as complete packages. Validate exact in-game discounts and SP arithmetic. Pay special attention to Victoria por Plancha, Groundwork with 3 early activations, Turbo Sprint vs Sprinting Gear, Top Runner, I Wanna Win With You, See Ya Later, and other available skills.
5. For meta assumptions, separate historical Japanese race samples from October 2026 Global anecdotes; report assumptions, not invented live frequencies. Evaluate different lobby compositions and rival strengths as sensitivity analysis.
6. Document seeds, trials, conditions, actual skill trigger rates, limitations and uncertainty. Prioritize correct mechanics over compelling-looking win percentages.
7. Keep changes confined to a separate research branch, preserving upstream application code as much as possible. Save reproducible scripts/results and a decision memo explaining recommended purchases and alternatives.

The environment startup guidance has already validated Umalator's browser flow via `node build.mjs --serve 8000` in `umalator-global`. Do not rerun updates that require a local game master.mdb or overwrite tracked bundles.
