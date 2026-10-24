"""Check preserved pseudo outputs and quantify synthetic field sensitivity."""
import csv, json, sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import cm21_nine_runner_pseudo_sim as sim
import numpy as np
root=Path(__file__).resolve().parent
checks={}
for i in (1,2):
    supplied=list(csv.DictReader(open(root.parent/f'seed{i}_results.csv')))
    rerun=list(csv.DictReader(open(root/f'pseudo-seed{i}/results.csv')))
    assert supplied==rerun
    checks[f'seed{i}']={'rows':len(rerun),'all_fields_equal':True}
combined=list(csv.DictReader(open(root.parent/'combined_results.csv')))
a=list(csv.DictReader(open(root/'pseudo-seed1/results.csv')))
b=list(csv.DictReader(open(root/'pseudo-seed2/results.csv')))
for supplied,x,y in zip(combined,a,b):
    for k in supplied:
        if k in ('lobby','rival_strength','package','sp'): assert supplied[k]==x[k]==y[k]
        elif k=='trials': assert float(supplied[k])==float(x[k])+float(y[k])
        else: assert abs(float(supplied[k])-(float(x[k])+float(y[k]))/2)<1e-8
checks['combined']={'rows':len(combined),'all_common_fields_equal':True}
(root/'pseudo_checks.json').write_text(json.dumps(checks,indent=2))
rows=[]
for lobby in sim.LOBBIES:
    for level in sim.OPPONENTS:
        for build in ('No purchases','Balanced gold + IWW','Contested gold + Top Runner'):
            vals=[]
            for j in range(128):
                seed=int(np.random.SeedSequence([2120226,list(sim.LOBBIES).index(lobby),list(sim.OPPONENTS).index(level),j]).generate_state(1)[0])
                vals.append(sim.race_one(*sim.set_up(seed,lobby,level,build),0))
            rows.append({'lobby':lobby,'strength':level,'package':build,'trials':128,'mean_seconds':np.mean([v[-1] for v in vals]),'mean_hp':np.mean([v[-2] for v in vals]),'pseudo_win_fraction':np.mean([v[0]==1 for v in vals]),'limitation':'Synthetic nine-runner model; not Umalator or measured CM outcomes'})
with open(root/'pseudo_time_probe.csv','w') as f:
    w=csv.DictWriter(f,fieldnames=rows[0]);w.writeheader();w.writerows(rows)
print(json.dumps(checks,indent=2))
