# CM21 independent research

**Latest:** [788m course / correlated activation / green-SP / HP follow-up](followup-788/FOLLOWUP_REPORT.md), with [reproduction and result index](followup-788/README.md). Prior outputs and all three original purchase alternatives are preserved.

Start with [DECISION_MEMO.md](DECISION_MEMO.md), then [recommended_shop_order.md](recommended_shop_order.md).

- [INSTALL_AND_VERIFICATION.md](INSTALL_AND_VERIFICATION.md): exact base, commands, data provenance, controls and limitations.
- [REPRO_AUDIT.md](REPRO_AUDIT.md): independent audit of the preserved Python model.
- [research/skill_ablation.csv](research/skill_ablation.csv): 38 skills, costs, timings and activation rates.
- [research/upgrade_ablation.csv](research/upgrade_ablation.csv): nine controlled white/gold or ○/◎ upgrades.
- [research/groundwork.csv](research/groundwork.csv): prerequisite tests.
- [research/package_comparison.csv](research/package_comparison.csv): 36 package/scenario rows, 1024 trials each.
- [research/package_direct_comparison.csv](research/package_direct_comparison.csv): paired differences against the prior balanced package.
- [research/package_activation.csv](research/package_activation.csv): per-package skill activation rates and mean trigger time/distance.
- [research/native_pairwise.json](research/native_pairwise.json): 16 original application comparison rows, 256 trials each, native activation and HP summaries.
- [research/timestep_sensitivity.csv](research/timestep_sensitivity.csv): 15Hz/60Hz gain checks.
- [research/raw_results.json.gz](research/raw_results.json.gz): compressed per-trial solo results and activation logs; unpack with Python gzip or gzip -dc.
- [research/pseudo_checks.json](research/pseudo_checks.json): exact reproduction and aggregate checks.
- [research/pseudo_time_probe.csv](research/pseudo_time_probe.csv): additional synthetic nine-runner timing sensitivity.
- [build.mjs](research/build.mjs), [run.ts](research/run.ts), [pairwise.ts](research/pairwise.ts), [audit_repro.py](research/audit_repro.py), [summarize.py](research/summarize.py): reproducible scripts.

The archive's original documentation, scripts and outputs remain at this directory's root, byte-for-byte as extracted. New work is in the files listed above and `research/`. No Umalator application implementation or game data was changed. Research was performed on the isolated `work` branch based on `origin/cm21-research` at `96b870a`. The completed artifacts are published on `cm21-results` for a pull request targeting `cm21-research`; master was untouched.

Results validate behavior in this Umalator snapshot. They do not establish live Global fidelity, current shop discounts, nine-runner CM win rates, or a globally optimal skill package.
