# Installation and verification

Research base: `rileypoynter0605-cloud/Umalator`, `origin/cm21-research` commit **96b870a1cf1c9947a81167cce680fa61081d3e07**. Initial branch was clean `work` at bc4781d. Fetched the requested branch explicitly and fast-forwarded `work` to it, preserving the isolated workflow. No master checkout, update, or push was performed.

Both `CM21_RESEARCH_TASK.md` and `CM21_Codex_Handoff_REMADE.zip` were present on that research commit. Extracted the archive into `cm21-study/`; read START_HERE, CODEX_TASK and ORIGINAL_STUDY_README. The task's older ZIP filename was superseded by the user's explicit REMADE filename.

## Reproduction

Executed with Node v24.19.0, Python 3.12.14, existing lockfile/node_modules (esbuild 0.19.x), and the pinned Python packages in `research/requirements.txt`. Run from repository root:

```bash
npm ci
python -m pip install --target /tmp/cm21-python -r cm21-study/research/requirements.txt
PYTHONPATH=/tmp/cm21-python python cm21-study/cm21_nine_runner_pseudo_sim.py --trials 400 --seed 2120226 --output cm21-study/research/pseudo-seed1
PYTHONPATH=/tmp/cm21-python python cm21-study/cm21_nine_runner_pseudo_sim.py --trials 400 --seed 7654321 --output cm21-study/research/pseudo-seed2
PYTHONPATH=/tmp/cm21-python python cm21-study/research/audit_repro.py
node cm21-study/research/build.mjs
node cm21-study/research/run.cjs
node cm21-study/research/build.mjs pairwise
node cm21-study/research/pairwise.cjs
python cm21-study/research/summarize.py
```

`npm ci` is a clean-install instruction, not a claim it was rerun in this session; startup had already supplied dependencies. Network fetch initially failed inside the default sandbox; the supported command network grant allowed the explicit branch fetch and Python installation. No game master database update or tracked browser bundle rebuild was run. An initial harness parse error and metadata subprocess restriction were corrected before the successful complete run; final engine.log and verification.json correspond to the corrected harness.

## Engine path and settings

`research/build.mjs` bundles the **original** RaceSolverBuilder / RaceSolver / GameHpPolicy using `CC_GLOBAL=true`, the same Global data redirection as the application's build. It retains Node assertions. No upstream TS, game JSON or application bundle is patched. The harness uses course 10701, normal mood, sunny/firm/winter, native unique 100411 Lv4, Turf S / Sprint S / Front A and the fixed player stats. HP, WIT checks and kakari are enabled. Main solo comparisons disable position keeping, lead competition and dueling to isolate mechanics. These are deliberate experiment controls, not comprehensive race simulations.

Harness changes are external: keyed per-skill-group trigger RNG, interpolated crossing time, logging, and a proximity-unavailable scenario which replaces selected skills' dynamic conditions with false. Sampled-condition runs use the original policies. Exact rank filters 1, 2 and 4 are assumptions; Umalator's `orderFilter` is a region filter and relaxes some forward-rank requirements beyond 900m. Rank sensitivity is therefore not a dynamically evolving nine-runner position test.

`pairwise.ts` separately invokes **unaltered `runComparison`** with its normal shared-RNG ordering and outputs margins in **lengths (2.5m)**. Baseline and purchased build are two compared counterfactual horses, not actual rival cards. Additional virtual pacers are explicitly synthetic; virtual position keeping is an engine approximation. `native_pairwise.json` includes activation and HP summaries. The simpler `opponent_sensitivity.csv` leaves position keeping off and gives identical results across rivals: it is a useful negative control showing that merely attaching a rival does not validate lobby interactions.

## Provenance and limits

Global course and skill JSON last changed at **26d5f0eaa82ae0c549625c26f6ff38a939833ab2**, October 1, 2026. This establishes repository provenance, not fidelity to the live October 24 Global client. No live master.mdb, actual event announcement, practice-room replays, shop screenshots/hint levels, or observed rival cards were supplied. Event conditions are the user's specified conditions. Local skill metadata plus supplied total prices validate arithmetic and groups; they cannot establish the player's exact discounts independently.

`verification.json` records the full course, runner, baseline distributions, exact replay assertion and timestep check. `raw_results.json.gz` contains per-trial times, HP, activation distances/times and paired package/upgrade results. `skill_catalog.json` captures raw conditions, units, rarity and costs. Other CSVs give single-skill, upgrade, Groundwork, package, direct package difference, timestep and rival sensitivity outcomes. `pseudo_checks.json` verifies original batches and aggregation. `source_hashes.json` records immutable input checksums; `summarize.py` also checks that upstream source is unchanged relative to the research base.

Do not interpret sampled proximity activation near 90% (or native unique near 100%) as an actual lobby activation rate. Do not interpret pairwise margins or pseudo-win fractions as measured CM win rates. Numerical, source-version and positional-model errors exceed the precision suggested by small Monte Carlo intervals. Recommendations are conditional research alternatives and require checking the current shop and practice races before spending.
