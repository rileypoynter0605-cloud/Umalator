#!/usr/bin/env python3
"""CM21 (Global Capricorn Cup) comparative *single-runner* simulator.

Mechanics reference: https://github.com/jalbarrang/torena-sim/blob/main/docs/mechanics/README.md
Track data: https://gametora.com/umamusume/racetracks/chukyo

IMPORTANT: This is an illustrative reduced-order Monte Carlo model, NOT Umalator or
an exact Cygames engine. It intentionally does NOT implement 9-runner position
keeping, lanes, blocked paths, dueling, spot struggle, or precise skill logic.
It cannot estimate a trustworthy CM win rate or absolute multi-style ranking.
Its valid primary use is same-runner, matched-seed comparisons of explicitly
parameterized candidate skills and provisional stamina adequacy.
"""
import argparse
import csv
import hashlib
import json
import math
import random
import statistics
from pathlib import Path

DIST = 1200.0
FPS = 15
DT = 1 / FPS
BASE_V = 20.8
MOOD = {'great': 1.04, 'good': 1.02, 'normal': 1.0, 'bad': 0.98, 'awful': 0.96}
STYLES = {
    'Front Runner': ((1, .980, .962), (1, 1, .996), .95),
    'Pace Chaser': ((.978, .991, .975), (.985, 1, .996), .89),
    'Late Surger': ((.938, .998, .994), (.975, 1, 1), 1.0),
    'End Closer': ((.931, 1, 1), (.945, 1, .997), .995),
    'Runaway': ((1.063, .962, .950), (1.17, .94, .956), .86),
}
DIST_APT = {'S':1.05,'A':1.,'B':.9,'C':.8,'D':.6,'E':.4,'F':.2,'G':.1}
SURF_APT = {'S':1.05,'A':1.,'B':.9,'C':.8,'D':.7,'E':.5,'F':.3,'G':.1}
STYLE_APT = {'S':1.1,'A':1.,'B':.85,'C':.75,'D':.6,'E':.4,'F':.2,'G':.1}
VALID_TYPES = {'speed', 'accel', 'current_speed', 'recover', 'speed_accel', 'speed_recover', 'green_speed',
               'green_stamina', 'green_power', 'green_guts', 'green_wit'}
VALID_TRIGGERS = {'start', 'early_entry', 'mid_entry', 'late_entry', 'last_phase_entry',
                  'final_straight_entry', 'late_straight_entry', 'random_straight',
                  'random_corner', 'random_mid', 'random_late', 'at_distance',
                  'late_corner','random_half','mid_latehalf','random_earlymid','random_finalcorner','random_latephase','mid_corner'}


def seed_for(*things):
    return int.from_bytes(hashlib.blake2b('|'.join(map(str, things)).encode(), digest_size=8).digest(), 'big')


def adjusted(x, mood):
    return min(2000., max(1., (min(x, 1200.) + max(0., x-1200.)/2) * mood))


def course_position(rule, spec, rng):
    if rule == 'start': return 0.
    if rule == 'early_entry': return 0.
    if rule == 'mid_entry': return 200.
    if rule == 'late_entry': return 800.
    if rule == 'last_phase_entry': return 1000.
    if rule == 'final_straight_entry': return 788.
    if rule == 'late_straight_entry': return 800.
    if rule == 'random_straight':
        a,b = rng.choice([(0,300), (788,1200)])
        return rng.uniform(a, b-10)
    if rule == 'random_corner':
        a,b = rng.choice([(300,550), (550,788)])
        return rng.uniform(a,b-10)
    if rule == 'random_mid': return rng.uniform(200,790)
    if rule == 'random_half': return rng.uniform(600,1190)
    if rule == 'mid_latehalf': return rng.uniform(500,790)
    if rule == 'random_earlymid': return rng.uniform(205,495)
    if rule == 'random_finalcorner': return rng.uniform(590,780)
    if rule == 'random_latephase': return rng.uniform(805,995)
    if rule == 'mid_corner': return rng.uniform(310,780)
    if rule == 'random_late': return rng.uniform(800,1190)
    if rule == 'at_distance': return float(spec['at_m'])
    if rule == 'late_corner': return math.inf  # Impossible: course is straight after 800 m.
    raise ValueError('Unknown trigger: '+rule)


def validate(data):
    u = data['runner']
    if u.get('style') not in STYLES: raise ValueError('Unknown style: '+str(u.get('style')))
    for k in ('speed','stamina','power','guts','wit'):
        if not isinstance(u.get(k), (int, float)) or u[k] <= 0:
            raise ValueError(f'Fill runner.{k} with a positive numeric final stat.')
    for k, opts in [('distance_apt', DIST_APT),('surface_apt',SURF_APT),('style_apt',STYLE_APT)]:
        if u.get(k,'A') not in opts: raise ValueError(f'Invalid {k} grade')
    if not data.get('options'): raise ValueError('Add at least one option.')
    for option in data['options']:
        names = [s['name'] for s in data.get('owned_skills', [])+option.get('skills', [])]
        if len(names)!=len(set(names)): raise ValueError('Duplicate skill name in option '+option['name'])
        for skill in data.get('owned_skills', [])+option.get('skills', []):
            if skill['type'] not in VALID_TYPES: raise ValueError('Unknown skill effect '+skill['type'])
            if skill.get('trigger','start') not in VALID_TRIGGERS: raise ValueError('Unknown trigger '+str(skill.get('trigger')))
            if 'position_min' in skill or 'position_max' in skill:
                if 'position_probability' not in skill:
                    raise ValueError(f"Position-sensitive skill '{skill['name']}' needs an explicit position_probability (0..1): race ranks are NOT simulated")
            p=skill.get('position_probability',1.)
            if not 0 <= p <= 1: raise ValueError('position_probability must be 0..1')


def skill_schedule(skills, s0, trial, name, stat_wit):
    events=[]
    for s in skills:
        typ=s['type']
        rng=random.Random(seed_for(s0, trial, name, s['name']))
        # Greens activate at the gate if corresponding CM21 condition is met; user must
        # enter only matching greens (Winter, Left-Handed, etc.).
        wit_chance = max(.20, 1.0-90.0/max(1.,stat_wit))
        if typ.startswith('green_'):
            if not s.get('applies',True): continue
            events.append((0.,s))
            continue
        if not s.get('guaranteed',False) and rng.random()>wit_chance:
            continue
        if rng.random()>s.get('position_probability',1.):
            continue
        event_m=course_position(s.get('trigger','start'),s,rng)
        if event_m < math.inf: events.append((event_m,s))
    return sorted(events,key=lambda x:x[0])


def run_one(u,skills,seed,trial,option_name):
    mood=MOOD[u.get('mood','great').lower()]
    basic={k: adjusted(u[k],mood) for k in ('speed','stamina','power','guts','wit')}
    # Only the current course's matching greens should be supplied.
    events=skill_schedule(skills,seed,trial,u.get('name','Trainee'),basic['wit'])
    for _, s in events:
        if s['type'].startswith('green_'):
            basic[s['type'].replace('green_','')]+=float(s.get('value',40))
    vstat=min(2000,basic['speed']); power=min(2000,basic['power'])
    stamina=min(2000,basic['stamina']); guts=min(2000,basic['guts']); wit=min(2000,basic['wit'])
    sty_v,sty_a,stam_coeff=STYLES[u['style']]
    dapt=DIST_APT[u.get('distance_apt','A')]
    surf=SURF_APT[u.get('surface_apt','A')]
    # Status below D lowers acceleration; high ranks leave acceleration unchanged.
    accel_dapt={'E':.6,'F':.5,'G':.4}.get(u.get('distance_apt','A'),1.)
    # Style aptitude influences effective Wit, but not the skill activation check.
    wit_effective=wit*STYLE_APT[u.get('style_apt','A')]
    hpmax=DIST+.8*stam_coeff*stamina
    hp=hpmax
    rng=random.Random(seed_for(seed,trial,option_name,'physics'))
    # To keep paired comparisons on the same course luck, isolate physics RNG from option name.
    rng=random.Random(seed_for(seed,trial,'physics',u.get('name','Trainee')))
    start_delay=rng.uniform(0,.12)*float(u.get('start_delay_multiplier',1.0))
    section_noise=[]
    maxpct=(wit_effective/5500*math.log10(max(wit_effective*.1,1)))/100.
    for _ in range(24):section_noise.append(BASE_V*rng.uniform(maxpct-.0065,maxpct))
    downhill_rolls=[(rng.random(),rng.random()) for _ in range(120)]
    downhill_active=False
    effects=[]
    used=[]
    t=0.; d=0.; v=3.; last_pos=0.
    event_i=0; sec_old=-1; hill_i=0; spurt_plan=None; exhausted=False
    while d < DIST and t < 130:
        oldd=d
        while event_i < len(events) and d >= events[event_i][0]:
            where,s=events[event_i]
            event_i+=1
            typ=s['type']
            if typ.startswith('green_'): continue
            if typ in ('recover','speed_recover'):
                hp=min(hpmax,hp+hpmax*float(s.get('recover_value',s['value'])))
            if typ != 'recover':
                base_duration=float(s.get('duration',0))*DIST/1000
                if base_duration<=0: raise ValueError(f"Missing duration for timed skill {s['name']}")
                if typ in ('speed_accel','speed_recover'):
                    effects.append((t+base_duration,'speed',float(s['value'])))
                    if typ == 'speed_accel':
                        effects.append((t+base_duration,'accel',float(s.get('accel_value',0))))
                else:
                    effects.append((t+base_duration,typ,float(s['value'])))
            used.append((s['name'],round(d,1)))
        effects=[e for e in effects if e[0] > t]
        speedbuff=sum(x for _,typ,x in effects if typ=='speed')
        accbuff=sum(x for _,typ,x in effects if typ=='accel')
        currentbuff=sum(x for _,typ,x in effects if typ=='current_speed')
        phase=0 if d < 200 else 1 if d < 800 else 2
        if phase<2: target=BASE_V*sty_v[phase]
        else:
            base_late=BASE_V*sty_v[2]+math.sqrt(500*vstat)*dapt*.002
            top=(base_late+.01*BASE_V)*1.05+math.sqrt(500*vstat)*dapt*.002+(450*guts)**.597*.0001
            if spurt_plan is None:
                # Reduced-order HP planner, not the game's multi-candidate selection.
                expected_time=400/max(1,top)
                hpcost=20*(top-BASE_V+12)**2/144*(1+200/math.sqrt(600*guts))
                frac=max(0,min(1,hp/max(1.,expected_time*hpcost)))
                spurt_plan=base_late+(top-base_late)*frac
            target=spurt_plan
        sec=min(23,int(d//50))
        if phase<2:target+=section_noise[sec]
        on_uphill=875 <= d < 975
        on_downhill=100 <= d < 875
        if on_uphill:target-=2.0*200/max(power,1)
        target+=speedbuff
        if hp <=0:
            exhausted=True
            target=.85*BASE_V+math.sqrt(200*guts)*.001
        target=min(30,max(0,target))
        acceleration=(.0004 if on_uphill else .0006)*math.sqrt(500*power)*sty_a[phase]*surf*accel_dapt+accbuff
        if t<start_delay: effective_dt=0
        else: effective_dt=DT if t-start_delay >= DT else (t-start_delay) % DT
        if v < target:
            if v<.85*BASE_V and d<60:
                v=min(.85*BASE_V,v+(acceleration+24)*DT)
            else:
                v=min(target,v+max(0,acceleration)*DT)
        else:v=max(target,v-(1.2 if phase==0 else .8 if phase==1 else 1.0)*DT)
        if d >= 8 and v<.85*BASE_V+math.sqrt(200*guts)*.001 and hp>0:
            v=.85*BASE_V+math.sqrt(200*guts)*.001
        # Downhill mode is simplified to a chance to enter / end per second.
        if int(t) != int(max(0,t-DT)) and on_downhill:
            enter, leave=downhill_rolls[hill_i%len(downhill_rolls)];hill_i+=1
            if downhill_active and leave<.20:downhill_active=False
            elif not downhill_active and enter < min(1,wit_effective*.0004):downhill_active=True
        if not on_downhill:downhill_active=False
        actualv=v+currentbuff+(.30 if downhill_active else 0)
        if t >= start_delay:
            step=actualv*DT
            if d+step >= DIST:
                remainder=(DIST-d)/max(.01,actualv)
                t+=remainder
                d=DIST
                break
            d+=step
            cost=20*(v-BASE_V+12)**2/144
            if phase==2:cost*=1+200/math.sqrt(600*guts)
            if downhill_active:cost*=.4
            hp-=cost*DT
        t+=DT
    return {'time':round(t,5),'hp':round(hp,1),'exhausted':exhausted,'used':used,
            'spurt_fraction':round((spurt_plan or 0),3)}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('input',help='JSON config path')
    p.add_argument('--runs',type=int,default=250,help='Paired random seeds per option (default 250)')
    p.add_argument('--csv',help='Optional output CSV, all per-run results')
    args=p.parse_args()
    if args.runs<10: raise SystemExit('--runs must be >=10')
    data=json.loads(Path(args.input).read_text(encoding='utf-8'))
    validate(data)
    runner=data['runner'];base_skills=data.get('owned_skills',[]);master_seed=data.get('seed',2212026)
    samples={}; rows=[]
    for option in data['options']:
        skills=base_skills+option.get('skills',[])
        name=option['name']
        arr=[]
        for i in range(args.runs):
            r=run_one(runner,skills,master_seed,i,name)
            arr.append(r)
            rows.append({'trial':i,'option':name,'time':r['time'],'hp':r['hp'],
                         'exhausted':r['exhausted'],'triggered_skills':'; '.join(x[0] for x in r['used'])})
        samples[name]=arr
    baseline=samples[data['options'][0]['name']]
    print('CM21 | Chukyo turf 1200m | winter, sunny, firm, left | single-runner proxy')
    print('NOTICE: Not a live 9-uma sim. NO validated win probabilities or rank comparisons.')
    print('Runner:',runner.get('name','Trainee'), '|',runner['style'], '|',
          'distance',runner.get('distance_apt','A'),'surface',runner.get('surface_apt','A'))
    print('Trials:',args.runs, '| Matched seed:',master_seed)
    print('Option | SP | Mean s | Median s | P10–P90 s | Better vs baseline | Exhaustions')
    for option in data['options']:
        a=samples[option['name']]
        v=[x['time'] for x in a]
        sp=sum(x.get('sp',0) for x in option.get('skills',[]))
        if data.get('sp_budget') is not None and sp>data['sp_budget']:
            print('  WARNING: option',option['name'],'exceeds budget by',sp-data['sp_budget'])
        better=sum(1 for i,x in enumerate(v) if x<baseline[i]['time'])/len(v)
        percentile=statistics.quantiles(v,n=10,method='inclusive')
        print(f"{option['name'][:28]:28s} | {sp:4} | {statistics.mean(v):6.3f} | "
              f"{statistics.median(v):6.3f} | {percentile[0]:5.2f}–{percentile[8]:5.2f} | "
              f"{100*better:5.1f}% | {sum(x['exhausted'] for x in a)}/{len(a)}")
        if option is not data['options'][0]:
            gains=[baseline[i]['time']-v[i] for i in range(len(v))]
            print('  Paired seconds saved (positive = improvement):',f'{statistics.mean(gains):.4f}',
                  '| median:', f'{statistics.median(gains):.4f}')
    if args.csv:
        with open(args.csv,'w',newline='',encoding='utf-8') as f:
            w=csv.DictWriter(f,fieldnames=list(rows[0]))
            w.writeheader();w.writerows(rows)
        print('Saved',args.csv)

if __name__=='__main__':main()
