"""Aggregate follow-up outputs, validate preservation, and update the decision memo.
Uses only Python's standard library. Does not regenerate or edit prior results.
"""
import csv,gzip,hashlib,json,math,re,subprocess
from collections import defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
D=ROOT/'cm21-study/followup-788'
def load(name):return list(csv.DictReader(open(D/(name+'.csv'))))
def write(name,rows):
    with open(D/(name+'.csv'),'w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=rows[0],lineterminator='\n');w.writeheader();w.writerows(rows)
def f(r,k):return float(r[k])
def case(r):return (r['boundary'],r['profile'],r['hp'])
def stats(a):
    m=sum(a)/len(a);se=math.sqrt(sum((x-m)**2 for x in a)/max(1,len(a)-1)/len(a))
    return m,m-1.96*se,m+1.96*se
catalog={v['id']:v for v in json.loads((ROOT/'cm21-study/research/skill_catalog.json').read_text())}
old=json.loads((ROOT/'cm21-study/research/packages.json').read_text())
validation=load('robust_validation')+load('hp_candidate_validation')
canonical={tuple(sorted(old['conservative'])):'conservative',tuple(sorted(old['candidate_1'])):'conditional',tuple(sorted(old['prior_balanced'])):'balanced'}
aliases={r['package']:canonical.get(tuple(sorted(r['skills'].split(';'))),r['package'])for r in validation}
(D/'canonical_names.json').write_text(json.dumps(aliases,indent=2)+'\n')
for r in validation:r['package']=aliases[r['package']]
groups=defaultdict(list)
for r in validation:groups[case(r)].append(r)
assert len(groups)==42
best={k:min(f(r,'mean_seconds')for r in rs)for k,rs in groups.items()}
by=defaultdict(list)
for r in validation:by[r['package']].append(r)
ranking=[]
for name,rs in by.items():
    assert len(rs)==42,(name,len(rs))
    ids=rs[0]['skills'].split(';')
    assert sum(catalog[i]['total_player_cost'] for i in ids)<=2751
    assert len(ids)==len({catalog[i]['meta']['groupId']for i in ids})
    assert all(int(r['trials'])==512 for r in rs)
    regrets=[f(r,'mean_seconds')-best[case(r)]for r in rs]
    normal=[r for r in rs if r['hp']=='normal']
    rank={'package':name,'sp':int(rs[0]['sp']),'remaining_sp':2751-int(rs[0]['sp']),
          'max_regret_seconds':max(regrets),'mean_regret_seconds':sum(regrets)/len(regrets),
          'max_normal_regret_seconds':max(f(r,'mean_seconds')-best[case(r)]for r in normal),
          'worst_exhaustion_fraction':max(f(r,'exhausted_fraction')for r in rs),
          'minimum_full_spurt_fraction':min(f(r,'full_spurt_fraction')for r in rs),
          'normal_reference_788_gain':next(f(r,'seconds_saved')for r in rs if r['boundary']=='788' and r['profile']=='reference-independent' and r['hp']=='normal'),
          'skills':rs[0]['skills']}
    ranking.append(rank)
ranking.sort(key=lambda r:(r['max_regret_seconds'],r['mean_regret_seconds']))
write('robust_ranking',ranking)
winner=ranking[0]
selected={winner['package'],'conservative','conditional','balanced'}
selected.update(r['package']for r in ranking[:3])
# Retain paired per-trial differences for the winner and original alternatives.
trials={}
for file in ['robust_trials.jsonl.gz','hp_candidate_trials.jsonl.gz']:
    with gzip.open(D/file,'rt')as stream:
        for line in stream:
            obj=json.loads(line)
            boundary,profile,hp,name=obj['case'].split(':',3)
            name=aliases.get(name,name)
            if name in selected:trials[(boundary,profile,hp,name)]=obj['trials']
paired=[]
for k in groups:
    w=trials[(*k,winner['package'])]['times']
    for name in ['conservative','conditional','balanced']:
        a=trials[(*k,name)]['times'];m,lo,hi=stats([x-y for x,y in zip(a,w)])
        paired.append({'boundary':k[0],'profile':k[1],'hp':k[2],'winner':winner['package'],'versus':name,
                       'seconds_saved':m,'ci95_low':lo,'ci95_high':hi,'trials':len(w)})
write('robust_paired_differences',paired)
# Validate exact preservation of every old artifact except the two intentionally updated entry points.
allowed={'cm21-study/DECISION_MEMO.md','cm21-study/README.md'}
preserved={}
for line in subprocess.check_output(['git','ls-tree','-r','be947c1','--','cm21-study'],cwd=ROOT,text=True).splitlines():
    info,path=line.split('\t');blob=info.split()[2]
    if path in allowed:continue
    content=(ROOT/path).read_bytes();actual=hashlib.sha1(b'blob '+str(len(content)).encode()+b'\0'+content).hexdigest()
    assert actual==blob,path
    preserved[path]=hashlib.sha256(content).hexdigest()
subprocess.run(['git','diff','--exit-code','be947c1','--','uma-skill-tools','umalator','umalator-global','components'],cwd=ROOT,check=True,capture_output=True)
before=subprocess.check_output(['git','show','be947c1:cm21-study/DECISION_MEMO.md'],cwd=ROOT)
assert (D/'DECISION_MEMO_BEFORE.md').read_bytes()==before
(D/'prior_artifact_hashes.json').write_text(json.dumps(preserved,indent=2)+'\n')

geometry=load('geometry_diagnostic');leave=load('constituent_ablation');greens=load('green_downgrades')
corr=load('correlation_packages');quart=load('quartet_marginal');hp=load('mad_dash_hp')
course_rows=[]
for package in ['conservative','conditional','balanced','victoria_only']:
    a=next(r for r in geometry if r['geometry']=='coherent'and r['boundary']=='788'and r['package']==package)
    b=next(r for r in geometry if r['geometry']=='coherent'and r['boundary']=='800'and r['package']==package)
    course_rows.append({'package':package,'gain_788':f(a,'seconds_saved'),'gain_800':f(b,'seconds_saved'),
        'extra_gain_788':f(a,'seconds_saved')-f(b,'seconds_saved'),'speed_800_boundary788':f(a,'speed_800'),
        'speed_800_boundary800':f(b,'speed_800'),'speed_bonus800_boundary788':f(a,'speed_bonus_800'),'speed_bonus800_boundary800':f(b,'speed_bonus_800')})
write('course_effect_summary',course_rows)
lines=['# CM21 follow-up: course, positional opportunities, green upgrades and HP','',
'**The 788m course correction is supported as the primary hypothesis supplied by the user. It changes timing by milliseconds here; the positional-opportunity and HP assumptions change the purchase decision much more.**',
'',f"**Most robust tested package:** `{winner['package']}`, **{winner['sp']} SP, {winner['remaining_sp']} SP remaining**. This minimizes the maximum mean-time regret across the explicitly declared 42-case envelope among the tested candidate set. It is not a proven game-wide optimum or a calibrated nine-runner result.",
'', 'All three prior purchase alternatives remain intact in `../recommended_shop_order.md`. New data and scripts are confined to this directory; the previous memo is preserved as `DECISION_MEMO_BEFORE.md`.','',
'## Controlled course comparison','',
'The user identifies GameTora and the October 18, 2026 uma.guide CM21 guide as supporting final straight 788m and final phase 800m. These external sources were supplied as context, not independently fetched in this follow-up. Both hypotheses are tested. The harness clones local course 10701, moves the last straight start **and final corner end** to 788 or 800, and leaves phases (200/800/1000), distance, hills and all game-data files unchanged. An extra straight-field-only diagnostic deliberately leaves a corner/straight overlap; Victoria still waits until 800 in that diagnostic because `corner==0` is unsatisfied before then.','',
'| Package | Gain at 788m, seconds | Gain at 800m, seconds | Extra gain with 788m |','|---|---:|---:|---:|']
for r in course_rows:lines.append(f"| {r['package']} | {r['gain_788']:.5f} | {r['gain_800']:.5f} | {r['extra_gain_788']:.5f} |")
lines += ['',
'These are paired-seed local-engine gains versus native-only in the same scenario, 1024 trials. Victoria can activate roughly 0.6 seconds before final phase, adding .05 target speed and .1 acceleration for 3.6 seconds. Its speed bonus and a slightly higher actual movement speed can carry into 800m; some acceleration duration is spent before spurt. Thus early activation is not automatically wasted, nor is every pre-phase acceleration frame useful. `geometry_activation.csv`, `course_effect_summary.csv` and checkpoint traces show actual trigger distances, speed and active bonuses around 788/800/810/825m.',
'', 'Every purchased constituent was removed individually from its complete package at both boundaries, under independent and exclusive-opportunity assumptions (512 paired trials per marginal row). The marginal gains are in `constituent_ablation.csv`; they should not be added together. Final Push remains pre-phase acceleration, not the speed effect in the old Python model. Final-straight and corner random skills also change their sampling support when the geometry is made consistent.',
'', '## Opportunity frequency and correlated conditions','',
'Opportunity gates are hypothetical **eligibility before the WIT check and timing constraints**, not specified actual activation probabilities. Native unique, lead gap, side/overtake, Cacao proximity and See Ya Later proximity have distinct recorded gates/activation rates. Reference opportunity probabilities are native .50, gap .35, side .45, close-behind .50. Cacao and See Ya Later have separate independent draws in the independent model, even though the close-behind frequency axis changes both marginals. A one-at-a-time .10/.30/.50/.70/.90 sweep varies native, gap, side and close separately. Actual rates are saved alongside the inputs.',
'',
'Correlation tests preserve marginal opportunities while changing their joint structure: independent uniforms; shared positive opportunities; a shifted uniform making clear-gap and contact opportunities mutually exclusive when their marginals permit; explicit gap→contact and contact→gap trigger-ready windows; and native-linked opportunities. **Native timing stays unchanged across the temporal quartet models.** Only its separately declared gate changes in the native-linked case. Temporal windows are synthetic trigger-ready windows, not an actual nine-agent lane simulation or an inferred population frequency.',
'', '| 788m assumption | Conservative gain | Conditional gain | Prior balanced gain | Quartet marginal gain (996 SP) |','|---|---:|---:|---:|---:|']
for profile in ['reference-independent','reference-positive','reference-exclusive','reference-gap-to-contact','reference-contact-to-gap','reference-native-linked','clear-front','contested-front','rank-2-contact','sparse-contact']:
    vals={r['package']:f(r,'seconds_saved')for r in corr if r['boundary']=='788'and r['profile']==profile}
    q=next(f(r,'seconds_saved')for r in quart if r['boundary']=='788'and r['profile']==profile)
    lines.append('| '+profile+' | '+' | '.join(f'{vals[k]:.4f}'for k in ['conservative','conditional','balanced'])+f' | {q:.4f} |')
lines += ['',
'The quartet remains beneficial against the same package without those four skills, including correlated scenarios; matched-marginal correlation alone does not erase its mean value. However, a positive marginal gain does not justify **996 SP** versus replacement purchases. Its opportunities, timing and rank availability matter, and the conditional package is not consistently superior to the alternatives. `quartet_joint_activation.csv` distinguishes joint eligibility, actual coactivation and overlapping effect times. This rejects the claim that four independently sampled useful triggers establish a robust purchase recommendation.',
'', '## Green upgrades and freed-SP alternatives','',
'Each downgrade keeps the ○ skill, so all three guaranteed opening activations remain available for Groundwork. Mask bit 1 removes Winter ◎, bit 2 Firm ◎, bit 4 Front Savvy ◎; masks include every combination. Original conservative cost is 2694 SP and already has 57 SP unspent.',
'', '| Downgrade mask | Removed upgrades | Freed SP | No-reinvestment change vs original, seconds (788m reference) |','|---:|---|---:|---:|']
for r in greens:
    if r['boundary']!='788'or r['profile']!='reference-independent':continue
    mask=int(r['downgrade_mask']);names=[n for i,n in enumerate(['Winter','Firm','Front Savvy'])if mask&(1<<i)]
    lines.append(f"| {mask} | {', '.join(names)or'none'} | {r['freed_sp']} | {f(r,'seconds_saved'):+.5f} |")
lines += ['',
'All three ◎ upgrades have small positive gains when simply removed. That does not establish optimal SP allocation. The full-package search screens **302** legal green-downgrade/reinvestment packages, with all supplied available skill groups considered for the remaining budget. It uses 96 trials on screening seed 519032 over reference, clear-front and contested-front assumptions. The retained candidates are re-evaluated on seed 871203, both course boundaries, rank/contact alternatives and HP stress. A second HP-aware search considers no-Mad variants with Standard Distance ○/◎, Moxie, and selected legal fillers. Its full candidate list, screen scores and shortlist are preserved.',
'',
'Final Push or lead/proximity fillers can beat a green upgrade in a leading, adequate-HP scenario. Their gains can disappear with rank/contact changes. HP protection can outperform those nominal-speed trades under stress. Therefore **buying all three ◎ upgrades is not an unconditional conclusion**; the robust recommendation below states exactly which are retained within the tested envelope. No green ○ is removed from the opening setup.',
'', '## Mad Dash HP sensitivity','',
'HP stress scales the existing GameHpPolicy status modifier for both expenditure **and spurt planning**. Debuff-like scenarios explicitly remove 3% of maximum HP at 400m and/or 650m. These doses are synthetic; they do not assert that particular rival cards or debuffs occur at those rates. Mad Dash still uses its actual local-data 4% HP cost and speed effect. Kakari remains enabled. Stats are unchanged.',
'', '| Conservative, 788m | Mad Dash marginal seconds | Exhaustion with Mad | Exhaustion without Mad | Full spurt with Mad | Full spurt without Mad |','|---|---:|---:|---:|---:|---:|']
for scenario in ['normal','cost+10pct','cost+20pct','drain6pct','cost+20pct-drain3pct','cost+20pct-drain6pct','cost+35pct-drain6pct']:
    a=next(r for r in hp if r['package']=='conservative'and r['boundary']=='788'and r['hp']==scenario and r['variant']=='original')
    b=next(r for r in hp if r['package']=='conservative'and r['boundary']=='788'and r['hp']==scenario and r['variant']=='without_mad_dash')
    lines.append(f"| {scenario} | {f(a,'seconds_saved'):+.4f} | {f(a,'exhausted_fraction'):.1%} | {f(b,'exhausted_fraction'):.1%} | {f(a,'full_spurt_fraction'):.1%} | {f(b,'full_spurt_fraction'):.1%} |")
lines += ['',
'Mad Dash is a modest normal-HP improvement and an avoidable liability under stronger consumption/drain assumptions. Removing it, or replacing it with Standard Distance or Moxie, improves HP robustness. Extreme +35% consumption plus 6% drain makes even several protected builds unreliable; that case is a diagnostic stress bound, not a promised matchup. The 42-case recommendation envelope includes normal costs and +20% with 3%/6% drains, but not that extreme +35% case.',
'', '## Most robust tested recommendation','',
'The decision criterion is **minimum maximum mean-time regret**, where regret is the candidate’s mean finish time minus the fastest tested candidate in each case. The envelope contains both boundaries × seven declared positional profiles × three HP assumptions = 42 cases. Profiles are not weighted as empirical matchmaking frequencies. Results use 512 paired validation trials per case; all inputs, remaining HP tails, exhaustion and full-spurt rates are retained. The maximum is a decision rule, not a confidence bound.',
'', '| Candidate | SP | Maximum regret, seconds | 788m normal reference gain | Worst exhaustion in envelope |','|---|---:|---:|---:|---:|']
show=ranking[:5]+[r for r in ranking if r['package']in ['conservative','conditional','balanced']and r not in ranking[:5]]
for r in show:lines.append(f"| `{r['package']}` | {r['sp']} | {r['max_regret_seconds']:.4f} | {r['normal_reference_788_gain']:.4f} | {r['worst_exhaustion_fraction']:.1%} |")
safer=min(ranking,key=lambda r:r['worst_exhaustion_fraction'])
second=ranking[1]
lines+=['',f"The leading maximum-regret estimates differ by only {second['max_regret_seconds']-winner['max_regret_seconds']:.5f}s. That is below this experiment's practical numerical/model resolution; the revised list is a preferred HP-aware compromise, not a statistically established unique winner. The prior balanced package remains a credible near-tied alternative.",'',f"For a stronger HP preference, `{safer['package']}` costs {safer['sp']} SP and has worst-envelope exhaustion {safer['worst_exhaustion_fraction']:.1%}, with maximum timing regret {safer['max_regret_seconds']:.4f}s. The selected package's corresponding exhaustion is {winner['worst_exhaustion_fraction']:.1%}; neither guarantees survival in the severe synthetic stress case.",'',f"Selected **{winner['sp']} SP / {winner['remaining_sp']} remaining**. Exact IDs and arithmetic are in `robust_ranking.csv` and `recommendation.json`. Shop prices remain the player-supplied totals; current hint discounts have not been independently checked.",'','| Purchase | Total from unowned | Cumulative |','|---|---:|---:|']
ids=winner['skills'].split(';');total=0
for id in ids:
    c=catalog[id];total+=c['total_player_cost'];lines.append(f"| {c['name']} | {c['total_player_cost']} | {total} |")
assert total==winner['sp']
lines += ['',
'Gold totals include their white prerequisite; ◎ totals include ○. Do not add the white/○ price a second time. If the shop presents upgrades separately, subtract the listed white/○ total from the gold/◎ total to obtain the incremental upgrade. Native unique Lv4 remains equipped at zero additional SP.',
'', '## What survives and what changes','',
'- **Survives:** Victoria and the complete three-green Groundwork opening setup remain central. The 788/800 correction does not reverse their usefulness. Gold/white skill effects and Final Push’s acceleration identity remain as audited.',
'- **Changes:** The original full-proxy conditional ranking is not robust to finite opportunity rates. Correlation alone at fixed marginals is a smaller effect than opportunity frequency and timing, but the quartet’s cost still needs comparison with alternatives.',
'- **Changes:** Three ◎ upgrades are small, separable benefits rather than mandatory purchases. Reinvestment can improve a full package under some assumptions; HP-aware alternatives alter the preferred tradeoff.',
'- **Changes:** Normal-case “no exhaustion” is not evidence that Mad Dash is safe under debuffs or extra consumption. Its nominal gain is small relative to the downside in the tested stress envelope.',
'- **Still unknown:** Actual Global opportunity frequencies, joint trajectories, rival builds, teammate tactics, exact live skill/data parity and current discounts. This is Umalator with explicit research overrides, not the game’s official engine and not a calibrated nine-runner or team-win simulation.',
'', '## Numerical and model limits','',
'Follow-up and prior absolute means should not be subtracted to attribute a course effect: the follow-up changes seed and keys subsequent WIT rolls by skill group while preserving the engine formula. Opening constructor rolls stay engine-native. In this snapshot, Front Runner Savvy changes horse.wisdom but not rawWisdom used in the skill-check formula; do not assume its ◎ upgrade raises skill proc probability. All course effects reported here compare otherwise matched follow-up runs. Trigger streams use common group seeds and opportunity uniforms are shared across package comparisons; native unique WIT exemptions remain native. Frequency gates do not replace condition timing or the WIT check.',
'',
'Exact rank-1/rank-2 builder filters are scenario assumptions, not evolving lobby positions. Umalator relaxes some forward-rank regions after 900m; Victoria’s normal trigger in these runs is earlier. Proximity gates and temporal windows bound uncertainty, but do not create a physical nine-runner pack. Temporal trigger readiness and native/contact correlation are declared assumptions. The checkpoint speeds interpolate the crossing frame; bonuses are the step state around the crossing, so consult the subsequent 810/825m checkpoints as well.',
'',
'`timestep_check.csv` compares 15Hz and 60Hz. Package gains move by a few milliseconds; individual green/geometry differences of that scale should not be overinterpreted despite narrow Monte Carlo intervals. Confidence intervals quantify randomization within this model, not source, geometry or lobby-model error. Candidate selection is a bounded search; the final ranking is among tested candidates, and near ties do not prove a unique optimum. Practice-room activation and stamina observations remain the next discriminating evidence.']
if (D/'recommended_frequency.csv').exists():
    frequency=load('recommended_frequency')
    lines+=['','## Revised-package follow-through','','The revised and HP-protected candidates were also run through the full one-at-a-time frequency grid (512 trials per row). These checks do not extend the minimax selection envelope after selection; they show sensitivity outside that fixed envelope.','','| 788m native/gap/side/close opportunity sweep | Revised gain range | HP-protected gain range | Balanced gain range |','|---|---:|---:|---:|']
    for family in ['native','gap','side','close']:
        ranges=[]
        for name in ['revised','hp_protected','balanced']:
            vals=[f(r,'seconds_saved')for r in frequency if r['boundary']=='788'and r['profile'].startswith('vary-'+family+'-')and r['package']==name]
            ranges.append(f'{min(vals):.4f}–{max(vals):.4f}')
        lines.append('| '+family+' | '+' | '.join(ranges)+' |')
    lines+=['','`recommended_hp.csv` applies every declared HP scenario, including the +35% extreme diagnostic, to the revised list, HP-protected list and balanced control with 1024 trials each. These results support the HP tradeoff; they do not turn unobserved debuff frequencies into empirical probabilities.']
(D/'FOLLOWUP_REPORT.md').write_text('\n'.join(lines)+'\n')
(D/'recommendation.json').write_text(json.dumps({'criterion':'minimum maximum mean-time regret over declared 42-case envelope','winner':winner,'skills':[catalog[i]for i in ids],'ranked_candidates':len(ranking),'envelope_cases':42,'trial_count_per_case':512,'price_status':'supplied totals, discounts not independently verified'},indent=2)+'\n')
notice=f'''\n> **Follow-up supersedes the original default recommendation:** The 788m/800m, correlated-opportunity, green-upgrade and HP study is complete. The most robust tested package within its declared envelope costs **{winner['sp']} SP ({winner['remaining_sp']} remaining)**. See [the follow-up report](followup-788/FOLLOWUP_REPORT.md) and [exact revised purchases](followup-788/recommendation.json). All three original alternatives below remain preserved as historical comparisons.\n'''
old_memo=(D/'DECISION_MEMO_BEFORE.md').read_text();title,rest=old_memo.split('\n',1)
(ROOT/'cm21-study/DECISION_MEMO.md').write_text(title+'\n'+notice+rest)
(D/'verification.json').write_text(json.dumps({'old_artifacts_preserved':len(preserved),'old_source_unchanged':True,'old_memo_snapshot_exact':True,'cases':len(groups),'validated_candidates':len(ranking),'rows':len(validation),'candidate_budgets_valid':True,'prior_commit':'be947c18356144e82faf3b99bcd0ac645f8128ca','source_hashes':{p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest()for p in ['uma-skill-tools/RaceSolver.ts','uma-skill-tools/RaceSolverBuilder.ts','uma-skill-tools/HpPolicy.ts','umalator-global/course_data.json','umalator-global/skill_data.json']}},indent=2)+'\n')
print(json.dumps({'winner':winner,'validated_candidates':len(ranking),'rows':len(validation),'old_artifacts_preserved':len(preserved)},indent=2))
