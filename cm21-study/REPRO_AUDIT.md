# Audit of the previous CM21 simulation

The prior results reproduce, but they do not validate the purchase recommendation or CM win probabilities. Both 400-trial batches match all 60 supplied rows and every CSV field exactly. The combined table is checked separately by `research/audit_repro.py`. No original Python simulator was edited.

## Mechanics comparison

| Mechanic | Preserved nine-runner Python model | Local Global Umalator source/data |
|---|---|---|
| Phases | 200 / 800 / 1000 m boundaries | Same boundaries; maximum spurt can begin at 800 m. 1000 m is not necessarily spurt start. |
| Course | Downhill 100–875; uphill 875–975; final straight 788 | Course 10701 agrees on hills, but final straight starts 800; corners 300–550 and 550–800. Local data is not independent proof of physical course geometry. |
| Downhill | Per-second entry WIT × .0004; 20% exit; +.301745 target speed | Entry on slope entry and per-second checks, WIT × .0004; exit roll >.8; +.3 + (-10000)/100000 = **+.2 m/s** in this snapshot. Both change target, not immediate movement speed. |
| HP downhill | ×.4 expenditure | ×.4; engine additionally accounts for rushed/position-keep/competition state. |
| Uphill | Target penalty 400 / power; lower acceleration | Agrees in broad form for slope 20000; timing/integration differs. |
| Speed >1200 | Half overcap, fractional part retained; greens added before folding | Engine floors overcap and applies greens at activation after base stat conversion. Winter +40 is not reduced to +20 by overcap in the engine. |
| Stamina/spurt | One-shot proportional interpolation toward maximum speed from estimated HP need | `GameHpPolicy` evaluates speed/delay candidates and uses WIT-dependent candidate acceptance; not equivalent. |
| Native unique | Starts after 600, rank ≤3, ≥2s side contact; .35 for 6s | Data agrees on broad condition, engine samples side-contact timing. Level 4 multiplies target-speed .35 by 1.07 = .3745 for 6s. Python ignores level scaling. |
| Victoria | At ≥788, top two; .05 speed and .1 accel for 3.6s | Final-corner-exit condition intersects straight at 800, HP ≥30%, order ≤2; same effect sizes/duration. Python omits HP condition and grants early overlap. |
| Operation Cacao | Any rank ≤5 at sampled mid-corner distance; speed only | Order ≤4, mid-race corner, runner within 3 lengths behind; +.15 speed plus .0035 recovery for inherited version. Engine samples gap proximity rather than measuring actual lobby proximity. |
| Groundwork | Hard-coded requires three named greens; triggers at 3m; applies WIT check | Engine counts **any three successful opening activations**, then applies WIT check. Three guaranteed event greens meet prerequisite, but Groundwork itself is not guaranteed to pass WIT. |
| Early Lead | Scheduled at 5m | Immediate opening acceleration in engine; .2 for 1.44s. |
| Final Push | **Incorrectly +.15 target speed**, no first-place restriction | **+.2 acceleration**, random final corner, first place. This is a material error in the prior purchase valuation. |
| Professor | One random trigger 300–780 | `all_corner_random` engine policy and full actual corner regions; not identical sampling. |
| Straight skills | Equal choice of shortened straight windows | Engine's `StraightRandomPolicy`; includes different location support, including opening. |
| Turbo / white | Random 800–995; .4/.2 for 3.6s | Random phase 2, true 800–1000 region with engine sampler's 10m window; effect sizes agree. Isolated gold/white comparisons now provided. |
| Top Runner | Rank improvement or side-contact proxy, ≥5s; mid/opening | Actual condition broadly agrees; engine approximates trigger time using an Erlang policy. Does not establish actual solo-front activation. |
| See Ya Later | Same static lane within 2m behind for 3s after 10s | Gold .35/3.6s, behind-near-lane-time ≥3 and elapsed ≥10. Engine samples this condition. White **Playtime's Over** is .15. Metadata rarity resolves any naming ambiguity. |
| I Wanna Win With You | .42 speed/.24 accel, 1.44s; random 600–1110, rank ≤6 | Same effect sizes in current local data; random second half includes through 1200. WIT check applies. Local data already contains these values; engine has no fan-count parameter. It does not independently validate fan scaling for 271,088 fans. |
| Tail Held High | Requires 3 events whose scheduled threshold lies in middle | Engine requires 3 actual middle-phase activations. Threshold and actual activation phase need not agree. |
| Mad Dash | Not in original tested packages | Engine +.25 speed for 3.24s, **4% HP cost**. Relevant new alternative; avoid claiming stamina safety under debuffs from these tests. |

## Nine agents, but approximate interactions

All nine runners evolve positions, speeds, HP and skills; they are not eight fixed finish-time draws. The solver uses 15 ticks/s and fractional finish crossing interpolation. These are useful properties, not proof of faithful game mechanics.

Lanes are three fixed buckets, not a continuous lane solver. Blocking/side contact, dueling and position keeping are manually constructed approximations. Rank is computed once before each frame, while runner positions are updated sequentially inside the frame: later slots can observe earlier slots' updated positions in proximity/leader-gap checks. That introduces slot-order dependence. Start delays are quantized by the step and do not faithfully integrate fractional leftover time. WIT checks are rolled once per event, and greens/prerequisites are hard-coded. Kakari, true team identities and teammate tactics are absent. Opponent archetype skills and strengths are invented, and the `premium` field in the declared distributions is not used in event generation.

Both implementations use numerical stepping; neither should be called the official Cygames engine. Umalator is valuable as a separate implementation with data-driven skill conditions. Its positional proxies still limit CM predictions.

## Randomization and uncertainty

`SeedSequence([batch,lobby_index,tier_index,trial])` supplies repeatable scenario seeds. Separate own, rival and environmental generators preserve opponent draws across packages. Own trigger/proc draw consumption shifts when skills are changed; Focus consumes an additional own RNG draw. This is partial pairing, not identical per-skill rolls. Independent trial seeds support sampling comparisons, but the two seeds do not test structural correctness.

The new engine harness shares environment seeds and keys trigger-policy streams by skill group. Engine WIT-check draw order can still change when activation order changes. Reported 95% intervals are paired-trial normal intervals for **that estimator within that model**, not live CM uncertainty. Screening candidates on seed 7654321 and evaluating on 2120226 reduces selection reuse, but neither knapsack nor the shortlist proves a global optimum.

The original 48,000 pseudo-races cover four synthetic lobby compositions and three strength tiers. `research/pseudo_time_probe.csv` adds 128-trial timing/HP probes per lobby/tier/package. Historical JP usage percentages and October 2026 anecdotes remain unverified statements in the handoff, not a sampled Global population. No live frequencies are inferred. Teammates are unspecified, so none of these results estimates a 3v3v3 team win rate.

The robust conclusions are narrower: test Victoria and complete opening activation setups, isolate Turbo's upgrade, and treat proximity-dependent purchases as lobby-sensitive. The earlier 2731-SP list is a hypothesis, not an established optimum.
