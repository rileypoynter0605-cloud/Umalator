# CM21 decision memo

**The previous pseudo-simulation is reproducible, but its 2731-SP recommendation is not established as optimal.** Use the 522-SP opening core as the strongest common foundation for review. The remaining spend depends on positional-skill reliability. The three complete, budget-legal alternatives and their exact purchase order are in `recommended_shop_order.md`.

## What was validated

- Fetched research branch 96b870a and retained isolated `work`; upstream application and data are unchanged.
- Reproduced both original 24,000-race batches exactly and checked their 48,000-race aggregate.
- Ran original Global Umalator mechanics through an external TS harness: 38 single-skill rows, 9 upgrade comparisons, four Groundwork setups and complete budget packages. Trials per principal row: 1024, seed 2120226. Candidate screening: 128 trials on independent seed 7654321.
- Ran native application `runComparison` with solo and synthetic virtual pacers, 256 trials per row. These are pairwise margins, not nine-runner win rates.
- Exact deterministic baseline replay passed. Checked 15Hz vs 60Hz stepping; recorded full per-trial outputs and immutable source hashes.

## Results and their practical limits

Baseline (normal mood, unique Lv4, sampled side-contact condition): mean 56.445s, range 56.149–56.780s. Mean remaining HP 25.5%, zero HP exhaustions in 1024. These are local-engine outputs, not observed race times. The unique activates in 99.9% of this sample because its proximity condition is modeled probabilistically; this is not an actual race trigger prediction.

| Package | SP | Sampled lead conditions: seconds saved | Proximity unavailable: seconds saved |
|---|---:|---:|---:|
| opening_core | 522 | 0.310 | 0.317 |
| prior_balanced | 2731 | 0.731 | 0.687 |
| prior_top_runner | 2693 | 0.749 | 0.657 |
| candidate_1 | 2693 | 0.778 | 0.628 |
| candidate_2 | 2742 | 0.779 | 0.652 |
| conservative | 2694 | 0.692 | 0.722 |

The conditional candidate improves on the prior balanced list under sampled lead conditions, but loses that advantage with proximity disabled. The lower-proximity-dependence alternative sacrifices optimistic mean gain for fewer unsupported opponent-interaction assumptions. No unconditional best purchase plan follows from these tests. Knapsack scores generate candidates; full-package tests check nonlinear interactions, including Tail Held High. This is a shortlist search, not an exhaustive optimization of every legal package.

Victoria alone saves about 0.115s here at rank 1 with HP available, activating just past 800m. Groundwork alone never activates; three guaranteed greens enable it at about 91%, and greens+Groundwork save about 0.167s relative to native-only. The full 522-SP core saves about 0.310s under sampled lead assumptions. These findings justify prioritizing the opening setup and correctly timed acceleration for review.

| Isolated upgrade in prior balanced context | Extra SP | Mean seconds saved |
|---|---:|---:|
| Sprinting Gear → Turbo Sprint | 160 | 0.0395 |
| Corner Adept → Professor of Curvature | 126 | 0.0274 |
| Leader's Pride → Top Runner | 162 | 0.0279 |
| Playtime's Over → See Ya Later | 112 | 0.0295 |
| On the Way to Our Dream → I Wanna Win With You | 180 | 0.0188 |
| Front Runner Straightaways ○ → Front Runner Straightaways ◎ | 98 | 0.0091 |
| Front Runner Savvy ○ → Front Runner Savvy ◎ | 104 | 0.0050 |
| Winter Runner ○ → Winter Runner ◎ | 99 | 0.0098 |
| Firm Conditions ○ → Firm Conditions ◎ | 99 | 0.0074 |

The gold Turbo result is a controlled upgrade, unlike the previous White Turbo + Focus multi-skill swap. Do not add single-skill gains to predict a complete package. Even statistically separated means remain conditional on these mechanics and settings.

## Course and source caveats

Local course 10701 has downhill 100–875m, uphill 875–975m, final straight at **800m**, final phase at 800m, and phase-3 boundary 1000m. The handoff’s 788m final straight is inconsistent with this local snapshot. No live client course data was available to adjudicate which geometry is current. Umalator downhill mode adds **0.2m/s target speed** for its -10000 slope, versus the prior Python model’s approximately 0.302. Neither is an instant movement-speed increase.

The prior code incorrectly treats Final Push as speed instead of acceleration, ignores unique level scaling, changes green handling above 1200, simplifies spurt planning, overgrants Cacao and does not simulate teams. Details and source-level comparisons are in REPRO_AUDIT.md. The local I Wanna Win values are .42 speed/.24 acceleration; there is no fan-count input in the engine to independently check the 271,088-fan scaling.

Course/skill data last changed October 1, 2026. No supplied live game database, practice replays or shop screenshot can independently establish live Global parity or current discounts. The supplied event conditions and prices remain explicit inputs.

## Lobby conclusions

Four original nine-runner compositions and three strength tiers were rerun, all synthetic. Their pseudo-win fractions must not be interpreted as observed or predicted Global CM probabilities. More fronts may reduce Victoria availability while enabling early interaction skills; solo-front/pace-heavy fields can favor different purchases. The local engine cannot calibrate that joint distribution from these tests.

`opponent_sensitivity.csv` deliberately shows the same solo timing across attached rivals with position keeping disabled: adding an opponent object does not make rank/gap proxies faithful. `native_pairwise.json` additionally uses the application’s virtual-pacer workflow, including synthetic stronger Front and Pace pacers. Those results are measured within that workflow, not calibrated nine-agent CM outcomes. First-place statistics are among compared engine horses, not nine-runner lobby or team win rates.

No empirical Global character/style frequency was collected. Historical JP percentages and community anecdotes in the handoff remain unverified background. The user’s teammates are not supplied; no 3v3v3 team-win recommendation is possible.

## Uncertainty

The CSV intervals quantify paired Monte Carlo variation only. Environment/trigger streams are aligned, but WIT-check consumption can change with activation order. Baseline 15Hz vs 60Hz times differ by about 0.022s on average; the tested package gains change by only a few milliseconds, recorded in timestep_sensitivity.csv. Structural uncertainty is larger: fixed order filters, sampled proximity, simplified pacers, disabled competition/dueling, unknown debuffs and current-client parity. A tiny mean advantage cannot settle purchases under these uncertainties.

Before spending, verify current prices/upgrade totals and course implementation, then compare practice-room races with actual teammates and representative solo-front, contested-front and pace-heavy fields. Record actual Victoria/Top Runner/See Ya Later/Cacao trigger rates and Mad Dash stamina outcomes. This study supplies reproducible engine comparisons and bounded recommendations; it does not validate CM win percentages.

## Native comparison cross-check

Margins below are purchased build versus native-only baseline, in engine lengths (2.5m), 256 trials per cell. They are not seconds and not CM win probabilities. This separate path uses the unmodified application comparison function and its own RNG behavior.

| Synthetic pacer setting | Prior balanced | Prior Top Runner | Conditional candidate | Lower-proximity package |
|---|---:|---:|---:|---:|
| solo-comparison | 7.499 | 7.599 | 7.926 | 7.107 |
| virtual-front | 7.545 | 7.645 | 7.929 | 7.206 |
| virtual-pace | 7.073 | 6.938 | 7.207 | 6.843 |
| virtual-elite-front | 7.547 | 7.651 | 7.933 | 7.206 |

The prior Top Runner variant leads the balanced variant in the solo/front-pacer settings but trails it with the Pace pacer. This is evidence of sensitivity inside Umalator, not an estimate of how often each setting occurs in a nine-runner lobby.
