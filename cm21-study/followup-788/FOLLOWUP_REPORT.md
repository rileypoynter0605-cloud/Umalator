# CM21 follow-up: course, positional opportunities, green upgrades and HP

**The 788m course correction is supported as the primary hypothesis supplied by the user. It changes timing by milliseconds here; the positional-opportunity and HP assumptions change the purchase decision much more.**

**Most robust tested package:** `green-mask-6+200552+201661:moxie`, **2704 SP, 47 SP remaining**. This minimizes the maximum mean-time regret across the explicitly declared 42-case envelope among the tested candidate set. It is not a proven game-wide optimum or a calibrated nine-runner result.

All three prior purchase alternatives remain intact in `../recommended_shop_order.md`. New data and scripts are confined to this directory; the previous memo is preserved as `DECISION_MEMO_BEFORE.md`.

## Controlled course comparison

The user identifies GameTora and the October 18, 2026 uma.guide CM21 guide as supporting final straight 788m and final phase 800m. These external sources were supplied as context, not independently fetched in this follow-up. Both hypotheses are tested. The harness clones local course 10701, moves the last straight start **and final corner end** to 788 or 800, and leaves phases (200/800/1000), distance, hills and all game-data files unchanged. An extra straight-field-only diagnostic deliberately leaves a corner/straight overlap; Victoria still waits until 800 in that diagnostic because `corner==0` is unsatisfied before then.

| Package | Gain at 788m, seconds | Gain at 800m, seconds | Extra gain with 788m |
|---|---:|---:|---:|
| conservative | 0.72722 | 0.72146 | 0.00576 |
| conditional | 0.70238 | 0.70158 | 0.00080 |
| balanced | 0.72426 | 0.72338 | 0.00088 |
| victoria_only | 0.12358 | 0.11845 | 0.00512 |

These are paired-seed local-engine gains versus native-only in the same scenario, 1024 trials. Victoria can activate roughly 0.6 seconds before final phase, adding .05 target speed and .1 acceleration for 3.6 seconds. Its speed bonus and a slightly higher actual movement speed can carry into 800m; some acceleration duration is spent before spurt. Thus early activation is not automatically wasted, nor is every pre-phase acceleration frame useful. `geometry_activation.csv`, `course_effect_summary.csv` and checkpoint traces show actual trigger distances, speed and active bonuses around 788/800/810/825m.

Every purchased constituent was removed individually from its complete package at both boundaries, under independent and exclusive-opportunity assumptions (512 paired trials per marginal row). The marginal gains are in `constituent_ablation.csv`; they should not be added together. Final Push remains pre-phase acceleration, not the speed effect in the old Python model. Final-straight and corner random skills also change their sampling support when the geometry is made consistent.

## Opportunity frequency and correlated conditions

Opportunity gates are hypothetical **eligibility before the WIT check and timing constraints**, not specified actual activation probabilities. Native unique, lead gap, side/overtake, Cacao proximity and See Ya Later proximity have distinct recorded gates/activation rates. Reference opportunity probabilities are native .50, gap .35, side .45, close-behind .50. Cacao and See Ya Later have separate independent draws in the independent model, even though the close-behind frequency axis changes both marginals. A one-at-a-time .10/.30/.50/.70/.90 sweep varies native, gap, side and close separately. Actual rates are saved alongside the inputs.

Correlation tests preserve marginal opportunities while changing their joint structure: independent uniforms; shared positive opportunities; a shifted uniform making clear-gap and contact opportunities mutually exclusive when their marginals permit; explicit gap→contact and contact→gap trigger-ready windows; and native-linked opportunities. **Native timing stays unchanged across the temporal quartet models.** Only its separately declared gate changes in the native-linked case. Temporal windows are synthetic trigger-ready windows, not an actual nine-agent lane simulation or an inferred population frequency.

| 788m assumption | Conservative gain | Conditional gain | Prior balanced gain | Quartet marginal gain (996 SP) |
|---|---:|---:|---:|---:|
| reference-independent | 0.7272 | 0.7024 | 0.7243 | 0.0795 |
| reference-positive | 0.7272 | 0.7016 | 0.7253 | 0.0788 |
| reference-exclusive | 0.7272 | 0.7042 | 0.7258 | 0.0814 |
| reference-gap-to-contact | 0.7272 | 0.7030 | 0.7243 | 0.0801 |
| reference-contact-to-gap | 0.7272 | 0.6989 | 0.7236 | 0.0760 |
| reference-native-linked | 0.7260 | 0.7007 | 0.7247 | 0.0787 |
| clear-front | 0.7354 | 0.6955 | 0.7105 | 0.0652 |
| contested-front | 0.7208 | 0.7229 | 0.7416 | 0.1059 |
| rank-2-contact | 0.7208 | 0.7005 | 0.7271 | 0.0979 |
| sparse-contact | 0.7368 | 0.6609 | 0.7095 | 0.0293 |

The quartet remains beneficial against the same package without those four skills, including correlated scenarios; matched-marginal correlation alone does not erase its mean value. However, a positive marginal gain does not justify **996 SP** versus replacement purchases. Its opportunities, timing and rank availability matter, and the conditional package is not consistently superior to the alternatives. `quartet_joint_activation.csv` distinguishes joint eligibility, actual coactivation and overlapping effect times. This rejects the claim that four independently sampled useful triggers establish a robust purchase recommendation.

## Green upgrades and freed-SP alternatives

Each downgrade keeps the ○ skill, so all three guaranteed opening activations remain available for Groundwork. Mask bit 1 removes Winter ◎, bit 2 Firm ◎, bit 4 Front Savvy ◎; masks include every combination. Original conservative cost is 2694 SP and already has 57 SP unspent.

| Downgrade mask | Removed upgrades | Freed SP | No-reinvestment change vs original, seconds (788m reference) |
|---:|---|---:|---:|
| 0 | none | 0 | +0.00000 |
| 1 | Winter | 99 | -0.00961 |
| 2 | Firm | 99 | -0.00760 |
| 3 | Winter, Firm | 198 | -0.01719 |
| 4 | Front Savvy | 104 | -0.00490 |
| 5 | Winter, Front Savvy | 203 | -0.01451 |
| 6 | Firm, Front Savvy | 203 | -0.01243 |
| 7 | Winter, Firm, Front Savvy | 302 | -0.02201 |

All three ◎ upgrades have small positive gains when simply removed. That does not establish optimal SP allocation. The full-package search screens **302** legal green-downgrade/reinvestment packages, with all supplied available skill groups considered for the remaining budget. It uses 96 trials on screening seed 519032 over reference, clear-front and contested-front assumptions. The retained candidates are re-evaluated on seed 871203, both course boundaries, rank/contact alternatives and HP stress. A second HP-aware search considers no-Mad variants with Standard Distance ○/◎, Moxie, and selected legal fillers. Its full candidate list, screen scores and shortlist are preserved.

Final Push or lead/proximity fillers can beat a green upgrade in a leading, adequate-HP scenario. Their gains can disappear with rank/contact changes. HP protection can outperform those nominal-speed trades under stress. Therefore **buying all three ◎ upgrades is not an unconditional conclusion**; the robust recommendation below states exactly which are retained within the tested envelope. No green ○ is removed from the opening setup.

## Mad Dash HP sensitivity

HP stress scales the existing GameHpPolicy status modifier for both expenditure **and spurt planning**. Debuff-like scenarios explicitly remove 3% of maximum HP at 400m and/or 650m. These doses are synthetic; they do not assert that particular rival cards or debuffs occur at those rates. Mad Dash still uses its actual local-data 4% HP cost and speed effect. Kakari remains enabled. Stats are unchanged.

| Conservative, 788m | Mad Dash marginal seconds | Exhaustion with Mad | Exhaustion without Mad | Full spurt with Mad | Full spurt without Mad |
|---|---:|---:|---:|---:|---:|
| normal | +0.0293 | 0.0% | 0.0% | 100.0% | 100.0% |
| cost+10pct | +0.0288 | 0.8% | 0.1% | 99.6% | 100.0% |
| cost+20pct | +0.0070 | 18.2% | 5.2% | 90.2% | 97.5% |
| drain6pct | +0.0293 | 0.3% | 0.0% | 100.0% | 100.0% |
| cost+20pct-drain3pct | -0.0326 | 38.2% | 13.6% | 73.4% | 93.1% |
| cost+20pct-drain6pct | -0.1181 | 61.5% | 32.1% | 48.7% | 80.0% |
| cost+35pct-drain6pct | -0.3938 | 98.4% | 95.2% | 0.5% | 3.5% |

Mad Dash is a modest normal-HP improvement and an avoidable liability under stronger consumption/drain assumptions. Removing it, or replacing it with Standard Distance or Moxie, improves HP robustness. Extreme +35% consumption plus 6% drain makes even several protected builds unreliable; that case is a diagnostic stress bound, not a promised matchup. The 42-case recommendation envelope includes normal costs and +20% with 3%/6% drains, but not that extreme +35% case.

## Most robust tested recommendation

The decision criterion is **minimum maximum mean-time regret**, where regret is the candidate’s mean finish time minus the fastest tested candidate in each case. The envelope contains both boundaries × seven declared positional profiles × three HP assumptions = 42 cases. Profiles are not weighted as empirical matchmaking frequencies. Results use 512 paired validation trials per case; all inputs, remaining HP tails, exhaustion and full-spurt rates are retained. The maximum is a decision rule, not a confidence bound.

| Candidate | SP | Maximum regret, seconds | 788m normal reference gain | Worst exhaustion in envelope |
|---|---:|---:|---:|---:|
| `green-mask-6+200552+201661:moxie` | 2704 | 0.0382 | 0.7111 | 24.4% |
| `balanced` | 2731 | 0.0386 | 0.7273 | 32.6% |
| `green-mask-6+910261+200552:moxie` | 2748 | 0.0387 | 0.7107 | 22.7% |
| `green-mask-7+200552+200982+201661:moxie` | 2741 | 0.0433 | 0.7097 | 23.8% |
| `green-mask-6+910261+200552:no-mad` | 2622 | 0.0434 | 0.7107 | 32.8% |
| `conservative` | 2694 | 0.1736 | 0.7305 | 64.5% |
| `conditional` | 2693 | 0.2210 | 0.7094 | 59.2% |

The leading maximum-regret estimates differ by only 0.00041s. That is below this experiment's practical numerical/model resolution; the revised list is a preferred HP-aware compromise, not a statistically established unique winner. The prior balanced package remains a credible near-tied alternative.

For a stronger HP preference, `hp-green-4:200131:201661` costs 2740 SP and has worst-envelope exhaustion 16.2%, with maximum timing regret 0.0517s. The selected package's corresponding exhaustion is 24.4%; neither guarantees survival in the severe synthetic stress case.

Selected **2704 SP / 47 remaining**. Exact IDs and arithmetic are in `robust_ranking.csv` and `recommendation.json`. Shop prices remain the player-supplied totals; current hint discounts have not been independently checked.

| Purchase | Total from unowned | Cumulative |
|---|---:|---:|
| Winter Runner ◎ | 180 | 180 |
| Firm Conditions ○ | 81 | 261 |
| Front Runner Savvy ○ | 88 | 349 |
| Groundwork | 80 | 429 |
| Early Lead | 72 | 501 |
| Victoria por Plancha | 120 | 621 |
| Professor of Curvature | 306 | 927 |
| Straightaway Adept | 153 | 1080 |
| Fast-Paced | 162 | 1242 |
| Turbo Sprint | 320 | 1562 |
| Front Runner Straightaways ◎ | 189 | 1751 |
| Light as a Feather | 144 | 1895 |
| I Wanna Win With You | 380 | 2275 |
| Tail Held High | 90 | 2365 |
| Final Push | 117 | 2482 |
| Playtime's Over | 96 | 2578 |
| Moxie | 126 | 2704 |

Gold totals include their white prerequisite; ◎ totals include ○. Do not add the white/○ price a second time. If the shop presents upgrades separately, subtract the listed white/○ total from the gold/◎ total to obtain the incremental upgrade. Native unique Lv4 remains equipped at zero additional SP.

## What survives and what changes

- **Survives:** Victoria and the complete three-green Groundwork opening setup remain central. The 788/800 correction does not reverse their usefulness. Gold/white skill effects and Final Push’s acceleration identity remain as audited.
- **Changes:** The original full-proxy conditional ranking is not robust to finite opportunity rates. Correlation alone at fixed marginals is a smaller effect than opportunity frequency and timing, but the quartet’s cost still needs comparison with alternatives.
- **Changes:** Three ◎ upgrades are small, separable benefits rather than mandatory purchases. Reinvestment can improve a full package under some assumptions; HP-aware alternatives alter the preferred tradeoff.
- **Changes:** Normal-case “no exhaustion” is not evidence that Mad Dash is safe under debuffs or extra consumption. Its nominal gain is small relative to the downside in the tested stress envelope.
- **Still unknown:** Actual Global opportunity frequencies, joint trajectories, rival builds, teammate tactics, exact live skill/data parity and current discounts. This is Umalator with explicit research overrides, not the game’s official engine and not a calibrated nine-runner or team-win simulation.

## Numerical and model limits

Follow-up and prior absolute means should not be subtracted to attribute a course effect: the follow-up changes seed and keys subsequent WIT rolls by skill group while preserving the engine formula. Opening constructor rolls stay engine-native. In this snapshot, Front Runner Savvy changes horse.wisdom but not rawWisdom used in the skill-check formula; do not assume its ◎ upgrade raises skill proc probability. All course effects reported here compare otherwise matched follow-up runs. Trigger streams use common group seeds and opportunity uniforms are shared across package comparisons; native unique WIT exemptions remain native. Frequency gates do not replace condition timing or the WIT check.

Exact rank-1/rank-2 builder filters are scenario assumptions, not evolving lobby positions. Umalator relaxes some forward-rank regions after 900m; Victoria’s normal trigger in these runs is earlier. Proximity gates and temporal windows bound uncertainty, but do not create a physical nine-runner pack. Temporal trigger readiness and native/contact correlation are declared assumptions. The checkpoint speeds interpolate the crossing frame; bonuses are the step state around the crossing, so consult the subsequent 810/825m checkpoints as well.

`timestep_check.csv` compares 15Hz and 60Hz. Package gains move by a few milliseconds; individual green/geometry differences of that scale should not be overinterpreted despite narrow Monte Carlo intervals. Confidence intervals quantify randomization within this model, not source, geometry or lobby-model error. Candidate selection is a bounded search; the final ranking is among tested candidates, and near ties do not prove a unique optimum. Practice-room activation and stamina observations remain the next discriminating evidence.

## Revised-package follow-through

The revised and HP-protected candidates were also run through the full one-at-a-time frequency grid (512 trials per row). These checks do not extend the minimax selection envelope after selection; they show sensitivity outside that fixed envelope.

| 788m native/gap/side/close opportunity sweep | Revised gain range | HP-protected gain range | Balanced gain range |
|---|---:|---:|---:|
| native | 0.7016–0.7210 | 0.6950–0.7156 | 0.7179–0.7368 |
| gap | 0.7111–0.7111 | 0.7048–0.7048 | 0.7273–0.7273 |
| side | 0.7111–0.7111 | 0.7048–0.7048 | 0.7273–0.7273 |
| close | 0.7026–0.7192 | 0.6969–0.7129 | 0.6986–0.7559 |

`recommended_hp.csv` applies every declared HP scenario, including the +35% extreme diagnostic, to the revised list, HP-protected list and balanced control with 1024 trials each. These results support the HP tradeoff; they do not turn unobserved debuff frequencies into empirical probabilities.
