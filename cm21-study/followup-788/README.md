# CM21 targeted follow-up: 788m versus 800m

Start with [FOLLOWUP_REPORT.md](FOLLOWUP_REPORT.md), [the revised purchase record](recommendation.json), and [the updated decision memo](../DECISION_MEMO.md). The original memo is preserved [here](DECISION_MEMO_BEFORE.md); [all three original purchase lists](../recommended_shop_order.md) are unchanged.

## Reproduce

Research base: `cm21-results` commit `be947c18356144e82faf3b99bcd0ac645f8128ca`, itself based on `cm21-research` at `96b870a`. Node v24.19.0, existing repository dependencies/lockfile, Python 3.12.14 (standard library only for reporting). No external game-data update, browser bundle rebuild or original application patch is needed.

From repository root, use the repository's normal dependency installation if needed, then:

```bash
node cm21-study/followup-788/build.mjs
node cm21-study/followup-788/run.cjs tests
node cm21-study/followup-788/run.cjs course
node cm21-study/followup-788/run.cjs frequency
node cm21-study/followup-788/run.cjs correlation
node cm21-study/followup-788/run.cjs greens
node cm21-study/followup-788/run.cjs hp
node cm21-study/followup-788/run.cjs final
node cm21-study/followup-788/run.cjs hp-search
node cm21-study/followup-788/run.cjs precision
node cm21-study/followup-788/run.cjs geometry
python cm21-study/followup-788/report.py
node cm21-study/followup-788/run.cjs recommendation-check
python cm21-study/followup-788/report.py
```

The recipe regenerates only new follow-up outputs and the decision-memo notice. It does not rerun the original `research/summarize.py`, which would regenerate the historical memo instead. Preserve the historical `DECISION_MEMO_BEFORE.md`. Dependencies between stages: final needs greens; report needs all result stages; recommendation-check needs the first report. Runs may take several minutes. stdout was saved in the corresponding `.log` files for this study.

## Design and controls

- **Engine:** original Global RaceSolverBuilder / RaceSolver / GameHpPolicy, bundled with `CC_GLOBAL=true` and Global data redirection. Fixed trainee, stats, aptitudes, normal mood and Lv4 unique; HP, WIT checks and kakari enabled; solo position keeping, dueling and lead competition disabled. These controlled runs do not simulate a physical nine-runner lobby.
- **Course:** clone 10701 in memory. Coherent alternatives end the last corner and begin the last straight at 788m or 800m. The final phase remains at 800m and hills remain 100–875 / 875–975m. A diagnostic changes only the straight field to demonstrate why the corner predicate must also agree. No tracked course data is changed.
- **Randomization:** validation seed 871203; screening seed 519032. Trigger draws are keyed by skill group. After constructor-time opening activations, WIT draws are keyed by trial and group using the original engine success formula. Greens/native exemptions are retained. Constructor-time checks remain native. This makes course/skill removal comparisons reproducible without shifting all later WIT rolls. It is a declared harness adjustment; old and new absolute means should not be subtracted as a course effect.
- **Opportunities:** native unique, lead-gap, side/overtake, Cacao and See Ya Later have separate gates. Rates are eligibility before WIT and valid trigger timing, not guaranteed activations. Independent Cacao and See draws share the frequency parameter, not the random draw. Reference rates are native .50, gap .35, side .45, close .50. Frequencies .10/.30/.50/.70/.90 are varied one family at a time. These are uncertainty scenarios, not measured Global frequencies.
- **Dependence:** shared positive uniforms, shifted mutually exclusive gap/contact opportunities, gap→contact and contact→gap trigger-ready windows, and a separate native-linked model. Marginal gate rates are tested on 100,000 draws. Temporal quartet models retain the native unique's original timing policy; a baseline-invariance test checks this. The windows describe trigger readiness after required contact duration, not observed lane trajectories.
- **Rank:** main tests assume first place; one envelope profile assumes second place with no lead-gap opportunity. Native Umalator rank filters are static regions and relax some forward-rank conditions after 900m; no evolving rank prediction is claimed.
- **HP:** multipliers affect both engine consumption and its spurt planner. Synthetic debuff-like drains remove 3% maximum HP at 400m and/or 650m. The +35%/6%-drain case is an extreme diagnostic, excluded from the 42-case recommendation envelope. No particular rival/debuff frequency is implied.
- **Search:** every combination of the three green ◎→○ downgrades, 302 full legal reinvestment candidates, then a separate HP-aware candidate search. Screen at 96 trials, validate retained packages at 512 trials over both boundaries × seven positional profiles × three HP cases. Principal original-package/frequency/HP checks use 1024 trials. Constituent leave-one-out and final frequency checks use 512. Near ties are not proof of a unique optimum.

Full inputs are in [config.json](config.json), [frequency_profiles.json](frequency_profiles.json), [green_candidates.json](green_candidates.json), [green_shortlist.json](green_shortlist.json), [hp_search_candidates.json](hp_search_candidates.json), and [hp_shortlist.json](hp_shortlist.json). [engine.ts](engine.ts), [run.ts](run.ts), [build.mjs](build.mjs), and [report.py](report.py) implement the study. The report records what source behavior is measured and what is supplied by the synthetic opportunity/HP model.

## Results for direct GitHub review

| Question | Primary outputs |
|---|---|
| Boundary and carryover | [course_effect_summary.csv](course_effect_summary.csv), [geometry_diagnostic.csv](geometry_diagnostic.csv), [geometry_activation.csv](geometry_activation.csv), [carryover_traces.csv](carryover_traces.csv) |
| Original packages and constituent skills | [course_packages.csv](course_packages.csv), [constituent_ablation.csv](constituent_ablation.csv), [course_activation.csv](course_activation.csv) |
| Separate frequency axes | [frequency_packages.csv](frequency_packages.csv), [frequency_activation.csv](frequency_activation.csv) |
| Correlation and quartet value | [correlation_packages.csv](correlation_packages.csv), [quartet_marginal.csv](quartet_marginal.csv), [quartet_joint_activation.csv](quartet_joint_activation.csv), [correlation_activation.csv](correlation_activation.csv) |
| Green and SP tradeoffs | [green_downgrades.csv](green_downgrades.csv), [green_screening.csv](green_screening.csv), [hp_candidate_screen.csv](hp_candidate_screen.csv) |
| Mad Dash and HP | [mad_dash_hp.csv](mad_dash_hp.csv), [hp_activation.csv](hp_activation.csv), [recommended_hp.csv](recommended_hp.csv) |
| Robust candidate envelope | [robust_ranking.csv](robust_ranking.csv), [robust_validation.csv](robust_validation.csv), [hp_candidate_validation.csv](hp_candidate_validation.csv), [robust_paired_differences.csv](robust_paired_differences.csv) |
| Revised-package checks | [recommended_frequency.csv](recommended_frequency.csv), [recommended_activation.csv](recommended_activation.csv), [robust_activation.csv](robust_activation.csv), [hp_candidate_activation.csv](hp_candidate_activation.csv) |
| Numerical/preservation checks | [tests.json](tests.json), [gate_sampler_checks.csv](gate_sampler_checks.csv), [timestep_check.csv](timestep_check.csv), [verification.json](verification.json), [prior_artifact_hashes.json](prior_artifact_hashes.json) |

`course_trials.json.gz`, `frequency_trials.json.gz`, and `correlation_trials.json.gz` contain compact per-trial JSON. `robust_trials.jsonl.gz` and `hp_candidate_trials.jsonl.gz` contain concatenated gzip members whose decompressed contents are JSON Lines; Python `gzip.open` and `gzip -dc` support them. Each record includes times, HP, exhaustion, spurt flags/delay, crossing speeds, opportunities and activation bit masks. Bit *i* corresponds to `ids[i]`; the first four trials also include checkpoint traces and activation events. [canonical_names.json](canonical_names.json) maps deduplicated candidate labels to the three original package names used in reporting.

All results remain local Umalator behavior with explicit research assumptions. They do not establish real CM win rates, Global population frequencies, current discounts, or live-client parity. No merge is performed.
