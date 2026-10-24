#!/usr/bin/env python3
"""CM21 (Chukyo Turf 1200m) nine-runner *pseudo*-simulation, version 1.0.
This IS NOT the game engine and is NOT a reliable estimate of real CM win rates.
Its purpose is sensitivity testing across mutually interacting race participants,
condition-sensitive skills and multiple assumed opponent populations.

Sources: uma.guide/cm21-guide, umamusu.wiki/Game:Mechanics,
'mihonostudios.com/champions-meeting/21', selected Game:Skills pages.
All rivals' STAT DISTRIBUTIONS AND SKILL PACKAGES ARE ASSUMPTIONS, not scraped
player builds or sampled actual Global CM21 participation.

Usage: python cm21_nine_runner_pseudo_sim.py --trials 1200 --output /mnt/data/cm21_pseudo_results
Produces JSON, CSV and readable summaries. Numba/numpy/pandas required.
"""
import argparse, csv, json, math, os
from collections import Counter
from pathlib import Path
import numpy as np
from numba import njit

# Style 0 front, 1 pace, 2 late, 3 end
SPEED_COEF = np.array([[1.000,.980,.962],[.978,.991,.975],[.938,.998,.994],[.931,1.000,1.000]],dtype=np.float64)
ACCEL_COEF = np.array([[1.000,1.000,.996],[.985,1.000,.996],[.975,1.000,1.000],[.945,1.000,.997]],dtype=np.float64)
HP_COEF = np.array([.95,.89,1.,.995],dtype=np.float64)
STATS_BAK = np.array([1515.,402.,1003.,695.,976.])
# Event columns: threshold, duration (seconds), speed, accel, condition, checked-to-proc
# conditions: 0 unrestricted, 1 <=2, 2 3-4, 3 <=5, 4 <=6, 5 in back half,
# 6 after late-start good placement, 7 side contact, 8 another just behind,
# 9 special opening -> unconditional
MAX_EVENTS = 17

# Carefully chosen alternatives using user's EXACT purchase prices. Golden upgrades include their white costs.
PRICES = {
    'Victoria por Plancha':120,'Operation Cacao':140,'Winter Runner':81,'Firm Conditions':81,
    'Professor of Curvature':306,'Straightaway Adept':153,'Early Lead':72,'Fast-Paced':162,
    'Final Push':117,'Turbo Sprint':320,'Sprinting Gear':160,'Front Runner Straightaways ◎':189,
    'Front Runner Savvy ○':88,'Groundwork':80,'Tail Held High':90,'See Ya Later!':208,
    'Light as a Feather':144,'I Wanna Win With You':380,'Top Runner':342,
    'Focus':126,'Moxie':126,'Mad Dash':126,
}
BALANCED = ['Victoria por Plancha','Operation Cacao','Winter Runner','Firm Conditions',
 'Professor of Curvature','Straightaway Adept','Early Lead','Fast-Paced','Final Push',
 'Turbo Sprint','Front Runner Straightaways ◎','Front Runner Savvy ○','Groundwork',
 'Tail Held High','See Ya Later!','Light as a Feather','I Wanna Win With You']
FRONT = [x for x in BALANCED if x!='I Wanna Win With You']+['Top Runner']
# Lower-SP package designed to isolate the merit of situational gold and skill-tradeoffs.
MINIMAL = ['Victoria por Plancha','Winter Runner','Firm Conditions','Front Runner Savvy ○',
 'Groundwork','Early Lead','Turbo Sprint','Professor of Curvature','Straightaway Adept',
 'Front Runner Straightaways ◎','Fast-Paced','Tail Held High','Light as a Feather']
WHITE = [x for x in BALANCED if x not in ('Turbo Sprint','Final Push')]+['Sprinting Gear','Focus']
BUILDS = {'No purchases':[], 'Opening/finishing core':MINIMAL,
          'Balanced gold + IWW':BALANCED, 'Contested gold + Top Runner':FRONT,
          'White Turbo + Focus':WHITE}
for nm,ls in BUILDS.items():
 c=sum(PRICES[s] for s in ls)
 assert c<=2751,(nm,c)

LOBBIES = {
 'Pace-heavy (1F 5P 3E)': [0,1,1,1,1,1,3,3,3],
 'Historical-mix (1F 4P 1L 3E)': [0,1,1,1,1,2,3,3,3],
 'Contested front (2F 4P 3E)': [0,0,1,1,1,1,3,3,3],
 'Front-heavy (3F 4P 2E)': [0,0,0,1,1,1,1,3,3],
}
# Strength: subjective training distributions, NOT live-sampled or historical player stats.
OPPONENTS = {
 'mixed':       {'speed':1430.,'power':1040.,'wit':1030.,'guts':650.,'stamina':390.,'sprint_s':.45,'turf_s':.35,'premium':.55},
 'competitive': {'speed':1525.,'power':1150.,'wit':1130.,'guts':730.,'stamina':370.,'sprint_s':.72,'turf_s':.55,'premium':.78},
 'elite':       {'speed':1590.,'power':1260.,'wit':1240.,'guts':800.,'stamina':380.,'sprint_s':.89,'turf_s':.80,'premium':.90},
}

@njit(cache=True)
def race_one(styles, stats, surf, dista, events, procs, phase_noise, starts, downhill_rolls, lane, mode_rolls, selected):
    n=9; d=np.zeros(n); v=np.full(n,3.); t=0.; dt=1./15.
    active=np.zeros((n,MAX_EVENTS),np.float64); fired=np.zeros((n,MAX_EVENTS),np.int32)
    alive=np.ones(n,np.int32); rank=np.ones(n,np.int32);finish_time=np.full(n,999.,dtype=np.float64)
    hp=np.empty(n); hpmax=np.empty(n); top=np.empty(n); finalplan=np.zeros(n)
    down=np.zeros(n,np.int32); near_side=np.zeros(n,np.float64)
    behind_same=np.zeros(n,np.float64); prev_rank=np.full(n,9,np.int32)
    first_2=np.zeros(n,np.int32); get_vic=np.zeros(n,np.int32)
    unique_fire=0; top_fire=0; see_fire=0; IWW_fire=0; turbo_fire=0; vic_fire=0; exhausted=0
    front_count=0
    for i in range(n):
        if styles[i]==0:front_count+=1
    for i in range(n):
        hpmax[i]=1200.+.8*HP_COEF[styles[i]]*stats[i,1]
        hp[i]=hpmax[i]
        # final spurt top target speed (approximate)
        s=stats[i,0];g=stats[i,3];di=dista[i]
        base=20.8*SPEED_COEF[styles[i],2]+math.sqrt(500*s)*di*.002
        top[i]=(base+.208)*1.05+math.sqrt(500*s)*di*.002+((450*g)**.597)*.0001
    for tick in range(1500):
        finished=True
        for i in range(n):
            if d[i]<1200.:finished=False
        if finished:break
        # Ranks for stage-dependent conditional skill checks
        for i in range(n):
            rank[i]=1
            for j in range(n):
                if j!=i and d[j]>d[i]: rank[i]+=1
        for i in range(n):
            if d[i]>=1200.:continue
            sti=styles[i];p=0 if d[i]<200. else (1 if d[i]<800. else 2)
            onslope=875.<=d[i]<975.; ondown=100.<=d[i]<875.
            # Downhill Mode: reenter checks each approx second; simulated independent rolls
            if (tick%15)==0 and ondown:
                if down[i]==1:
                    if downhill_rolls[i,tick//15,1]<.20:down[i]=0
                else:
                    if downhill_rolls[i,tick//15,0]<min(1.,stats[i,4]*.0004):down[i]=1
            if not ondown:down[i]=0
            # Position/near-lane approximations. Adjacent lanes simulate blocked_side; same lane behind simulates tailing. Static three-bucket lane IDs are an oversimplification.
            side=False; behind=False
            for j in range(n):
                if i==j:continue
                if abs(lane[i]-lane[j])==1 and abs(d[i]-d[j])<=1.2:side=True
                if lane[i]==lane[j] and 0.<d[i]-d[j]<=2.0: behind=True
            if side:near_side[i]+=dt
            else:near_side[i]=0.
            if behind:behind_same[i]+=dt
            else: behind_same[i]=0.
            if rank[i]<=2:first_2[i]+=1
            # Conditional event activation (position checks at current position, not arbitrary odds)
            fired_mid_count=0
            for j in range(MAX_EVENTS):
                if events[i,j,0]<0:continue
                if fired[i,j]==1 and 200.<=events[i,j,0]<800.:fired_mid_count+=1
            for j in range(MAX_EVENTS):
                if events[i,j,0]<0 or fired[i,j]==1 or procs[i,j]==0:continue
                threshold=events[i,j,0];cond=int(events[i,j,4]);timebar=events[i,j,5]
                if d[i]<threshold:continue
                permitted=False
                if cond==0:permitted=True
                elif cond==1:permitted=rank[i]<=2
                elif cond==2:permitted=3<=rank[i]<=4
                elif cond==3:permitted=rank[i]<=5
                elif cond==4:permitted=rank[i]<=6
                elif cond==5:permitted=rank[i]>=5
                elif cond==6:permitted=rank[i]<=3 and near_side[i]>=2.0 and d[i]>=600.
                elif cond==7:permitted=(near_side[i]>=2.0 or rank[i]<prev_rank[i]) and t>=5.
                elif cond==8:permitted=behind_same[i]>=3.0 and t>=10.
                elif cond==9:permitted=fired_mid_count>=3
                if not permitted:continue
                fired[i,j]=1;active[i,j]=t+events[i,j,1]
                if i==0:
                    if j==0: pass
                    # slot flag in events[i,j,6]
                    which=int(events[i,j,6])
                    if which==1:unique_fire=1
                    elif which==2:top_fire=1
                    elif which==3:see_fire=1
                    elif which==4:IWW_fire=1
                    elif which==5:turbo_fire=1
                    elif which==6:vic_fire=1
            speedbuff=0.;accbuff=0.
            for j in range(MAX_EVENTS):
                if active[i,j]>t:
                    speedbuff+=events[i,j,2]
                    accbuff+=events[i,j,3]
            basemid=20.8*SPEED_COEF[sti,p]
            if p==2:
                if finalplan[i]==0:
                    # HP-aware approximate spurt planner (not Cygames exact multi-candidate planner)
                    need=400./max(1.,top[i])*20.*(top[i]-20.8+12.)**2/144.*(1.+200./math.sqrt(600.*stats[i,3]))
                    frac=max(0.,min(1.,hp[i]/max(1.,need)))
                    bl=basemid+math.sqrt(500.*stats[i,0])*dista[i]*.002
                    finalplan[i]=bl+(top[i]-bl)*frac
                target=finalplan[i]
            else:
                section=min(23,int(d[i]/50.))
                target=basemid+phase_noise[i,section]
            if onslope:target-=2.*200./max(1.,stats[i,2])
            if down[i]==1: target+=.30+math.tan(math.pi/180.)/10.
            target+=speedbuff
            # Simplified early leader speed-up/overtake modes; 1.5y adjusted solo threshold.
            # Wit check is drawn once per runner/mode, whereas real game may check repeatedly.
            if sti==0 and d[i]<500.:
                if rank[i]==1:
                    second_gap=1000.
                    for j2 in range(n):
                        if j2!=i and d[i]-d[j2]>=0. and d[i]-d[j2]<second_gap:second_gap=d[i]-d[j2]
                    if second_gap<=(12.5 if front_count==1 else 4.5) and mode_rolls[i,0]<20.*math.log10(max(1.,stats[i,4]*.1))/100.:
                        target*=1.04
                elif mode_rolls[i,1]<20.*math.log10(max(1.,stats[i,4]*.1))/100.:
                    target*=1.05
            # A very weak final-straight dueling proxy; NOT actual game dueling.
            if d[i]>=788. and side and rank[i]<=5:
                target+=.12*stats[i,3]/800.
                accbuff+=.05*stats[i,3]/800.
            # POSITION KEEP PROXY with official approximate 1.04 speedup & 0.915 PDM coefficients.
            # Actual game has section cooldowns, mode roll timing, lane mechanics; this is approximate.
            if 70.<d[i]<500. and sti>0:
                lead=max(d)
                gap=lead-d[i]
                fact=1.16  # 1200m: 0.0008*(1200-1000)+1
                if sti==1:
                    lo=3.;hi=5.*fact
                elif sti==2:
                    lo=6.5*fact;hi=7.*fact
                else:
                    lo=7.5*fact;hi=8.*fact
                if gap>hi and mode_rolls[i,0]<15.*math.log10(max(1.,stats[i,4]*.1))/100.:
                    target*=1.04
                if gap<lo:
                    target*=.915
            if hp[i]<=0.:
                target=.85*20.8+math.sqrt(200.*stats[i,3])*.001
                if i==0:exhausted=1
            target=max(0.,min(30.,target))
            ac=(.0004 if onslope else .0006)*math.sqrt(500.*stats[i,2])*ACCEL_COEF[sti,p]*surf[i]+accbuff
            if t>=starts[i]:
                if v[i]<target:
                    if v[i]<.85*20.8 and d[i]<60.:
                        v[i]=min(.85*20.8,v[i]+(ac+24.)*dt)
                    else:v[i]=min(target,v[i]+max(0.,ac)*dt)
                else:v[i]=max(target,v[i]-(1.2 if p==0 else .8 if p==1 else 1.)*dt)
                if d[i]>=8.:
                    v[i]=max(v[i],.85*20.8+math.sqrt(200.*stats[i,3])*.001)
                step=max(0.,v[i])*dt
                if d[i]+step>=1200.:
                    # store elapsed finish by adding fractional time to d using overflow encoding? use finish array
                    finish_time[i]=t+(1200.-d[i])/max(.001,v[i]);d[i]=1200.
                else:d[i]+=step
                cost=20.*(v[i]-20.8+12.)**2/144.
                if p==2:cost*=1.+200./math.sqrt(600.*stats[i,3])
                if down[i]==1:cost*=.4
                hp[i]-=cost*dt
            prev_rank[i]=rank[i]
        t+=dt
    # Exact within-frame interpolation. Finishing time, NOT final distance, determines placing.
    place=1
    for j in range(1,n):
        if finish_time[j]<finish_time[0]:place+=1
    # any ties resolved via final d encoding and high finish tick variation
    return place,unique_fire,top_fire,see_fire,IWW_fire,turbo_fire,vic_fire,exhausted,max(0.,hp[0]),finish_time[0]


def adj(raw):
    # All test runners normal mood by default; stats beyond 1200 count half
    return min(2000.,min(1200.,raw)+max(0.,raw-1200.)/2.)

def add(events, name, pos,dur,speed,accel,cond=0,flag=0):
    events.append((pos,dur,speed,accel,cond,0.,flag,name))

def make_events(rng_own,rng_rivals,stats,styles,scenario,build):
    all_events=[]; proc_list=[]
    rng=rng_own
    # Own events
    s=BUILDS[build]; es=[]
    if 'Early Lead' in s:add(es,'Early Lead',5.,1.44,0.,.2)
    if 'Groundwork' in s and len([x for x in ('Winter Runner','Firm Conditions','Front Runner Savvy ○') if x in s])>=3:
        add(es,'Groundwork',3.,3.6,0.,.2)
    if 'Victoria por Plancha' in s:add(es,'Victoria',788.,3.6,.05,.1,1,6)
    if 'Professor of Curvature' in s:add(es,'Professor of Curvature',rng.uniform(300,780),2.88,.35,0)
    if 'Straightaway Adept' in s:add(es,'Straightaway Adept',rng.choice([rng.uniform(25,280),rng.uniform(790,1100)]),3.6,.15,0)
    if 'Front Runner Straightaways ◎' in s:add(es,'Front Straightaways ◎',rng.choice([rng.uniform(25,280),rng.uniform(790,1100)]),3.6,.25,0)
    if 'Fast-Paced' in s:add(es,'Fast-Paced',rng.uniform(205,775),3.6,.15,0,3)
    if 'Final Push' in s:add(es,'Final Push',rng.uniform(600,785),3.6,.15,0,1)
    if 'Turbo Sprint' in s:add(es,'Turbo Sprint',rng.uniform(800,995),3.6,0.,.4,0,5)
    if 'Sprinting Gear' in s:add(es,'Sprinting Gear',rng.uniform(800,995),3.6,0.,.2,0,5)
    if 'Light as a Feather' in s:add(es,'Light as a Feather',rng.uniform(500,790),2.88,.15,0,3)
    if 'Operation Cacao' in s:add(es,'Operation Cacao',rng.uniform(310,770),3.6,.15,0,3) # Overgenerous: needs late-coming runner!
    if 'I Wanna Win With You' in s:add(es,'I Wanna Win With You',rng.uniform(600,1110),1.44,.42,.24,4,4)
    if 'Top Runner' in s:add(es,'Top Runner',max(120.,rng.uniform(150,450)),3.6,.35,0,7,2)
    if 'See Ya Later!' in s:add(es,'See Ya Later!',230.,3.6,.35,0,8,3)
    if 'Tail Held High' in s:add(es,'Tail Held High',rng.uniform(550,785),3.6,.15,0,9)
    # native Bakushin unique must wait until rank<=3, and side contact >=2s after 600
    add(es,'Genius x Bakushin',600.,6.,.35,0.,6,1)
    all_events.append(es)
    # Rival skill templates, invented only to approximate current suggested archetypes, never actual player data.
    rng=rng_rivals
    for i in range(1,9):
        st=styles[i];e=[]
        # Opening sprint skills and mid speed: quality variation reflected through added SP package below
        if rng.random()<.55:add(e,'opener',rng.uniform(5,70),1.44,0.,.2)
        add(e,'mid speed gold',rng.uniform(265,745),3.6,.35,0.)
        if rng.random()<.65:add(e,'mid white',rng.uniform(350,770),3.6,.15,0.)
        if st==0:
            add(e,'front straight skill',rng.choice([rng.uniform(15,270),rng.uniform(795,1110)]),3.6,.25,0.)
            add(e,'front Victoria',788.,3.6,.05,.10,1)
            # Some Machan-like innate opening ability without promising an exact identity
            if rng.random()<.70:add(e,'specialist front mid',rng.uniform(300,650),4.0,.25,0.)
            if rng.random()<.50:add(e,'front turbo',rng.uniform(800,995),3.6,0.,.4)
        elif st==1:
            add(e,'Nishino-like final accel',800.,6.,.12,.21,2)
            add(e,'Pace Head-On',rng.uniform(800,945),3.6,0.,.2,3)
            if rng.random()<.35:add(e,'top-two Victoria',788.,3.6,.05,.10,1)
            add(e,'pace end speed',rng.uniform(910,1180),3.0,.22,0.,4)
        elif st==2:
            add(e,'late moving accel',rng.uniform(802,930),3.6,0.,.3,5)
            add(e,'late finish speed',rng.uniform(900,1170),3.6,.28,0.)
        else:
            add(e,'End Closer straight accel',800.,3.6,0.,.35,5)
            if rng.random()<.45:add(e,'Taishin gold',800.,3.6,0.,.15,5)
            add(e,'End finishing speed',rng.uniform(945,1150),4.,.27,0.,5)
        all_events.append(e)
    em=np.full((9,MAX_EVENTS,7),-1.,dtype=np.float64)
    pr=np.zeros((9,MAX_EVENTS),dtype=np.int32)
    for i,es in enumerate(all_events):
        assert len(es)<=MAX_EVENTS
        for k,(pos,dur,spd,ac,cond,timebar,flag,name) in enumerate(es):
            em[i,k,:]=[pos,dur,spd,ac,cond,timebar,flag]
            roll=(rng_own if i==0 else rng_rivals).random()
            # unique unaffected Wit checks
            pr[i,k]=int((name=='Genius x Bakushin') or roll<max(.2,1.-90./max(1.,stats[i,4])))
    return em,pr


def set_up(master_seed,lobby,level,build):
    rng=np.random.default_rng(np.random.SeedSequence([master_seed,101]))
    rng_own=np.random.default_rng(np.random.SeedSequence([master_seed,202]))
    rng_rivals=np.random.default_rng(np.random.SeedSequence([master_seed,303]))
    styles=np.array(LOBBIES[lobby],dtype=np.int32)
    # Shuffle adversary slot identities only: preserves exact scenario counts
    rng.shuffle(styles[1:])
    raw=np.zeros((9,5));raw[0]=STATS_BAK
    surf=np.ones(9);dista=np.ones(9)
    surf[0]=1.05;dista[0]=1.05
    params=OPPONENTS[level]
    for i in range(1,9):
        # Stat quality distribution is an ASSUMPTION; generous heterogeneity and overlapping profiles.
        z=rng.normal(0,1)
        bias=np.clip(z,-1.8,1.8)
        raw[i]=[params['speed']+75*bias+rng.normal(0,35),
                params['stamina']+rng.normal(0,75),
                params['power']+95*bias+rng.normal(0,60),
                params['guts']+60*bias+rng.normal(0,70),
                params['wit']+100*bias+rng.normal(0,70)]
        raw[i]=np.clip(raw[i],[900,200,450,250,450],[1800,900,1600,1300,1600])
        surf[i]=1.05 if rng.random()<params['turf_s'] else 1.
        dista[i]=1.05 if rng.random()<params['sprint_s'] else 1.
    if 'Winter Runner' in BUILDS[build]:raw[0,0]+=40
    if 'Firm Conditions' in BUILDS[build]:raw[0,2]+=40
    if 'Front Runner Savvy ○' in BUILDS[build]:raw[0,4]+=40
    st=np.vectorize(adj)(raw)
    starts=rng.uniform(0,.1,9)
    if 'Focus' in BUILDS[build] and rng_own.random()<max(.2,1-90/st[0,4]):starts[0]*=.9
    phase_noise=rng.uniform(-.15,.0,(9,24))
    downhill_rolls=rng.random((9,120,2))
    lane=rng.integers(0,3,9).astype(np.int32)
    events,procs=make_events(rng_own,rng_rivals,st,styles,lobby,build)
    mode_rolls=rng.random((9,2))
    return styles,st,surf,dista,events,procs,phase_noise,starts,downhill_rolls,lane,mode_rolls


def main():
    p=argparse.ArgumentParser();p.add_argument('--trials',type=int,default=1200)
    p.add_argument('--output',default='/mnt/data/cm21_pseudo_results')
    p.add_argument('--seed',type=int,default=2120226)
    args=p.parse_args();out=Path(args.output);out.mkdir(parents=True,exist_ok=True)
    results=[]
    for lobby in LOBBIES:
        for level in OPPONENTS:
            for build in BUILDS:
                n=args.trials; ranks=[];u=[];tr=[];se=[];iw=[];tu=[];vi=[];hps=[];ex=[]
                # Paired scenario seeds with same opponent generation but shuffled RNG consumption between builds.
                for j in range(n):
                    common_seed=int(np.random.SeedSequence([args.seed, list(LOBBIES).index(lobby), list(OPPONENTS).index(level), j]).generate_state(1)[0])
                    setup=set_up(common_seed,lobby,level,build)
                    place,unique,top,see,IWW,turbo,vic,exhaust,hp,rt=race_one(*setup,0)
                    ranks.append(place);u.append(unique);tr.append(top);se.append(see);iw.append(IWW);tu.append(turbo);vi.append(vic);ex.append(exhaust);hps.append(hp)
                k=lambda arr:round(100*float(np.mean(arr)),2)
                r={'lobby':lobby,'rival_strength':level,'package':build,'sp':sum(PRICES[x] for x in BUILDS[build]),
                   'trials':n,'win_pct':k(np.array(ranks)==1),'podium_pct':k(np.array(ranks)<=3),
                   'mean_rank':round(float(np.mean(ranks)),3),'unique_pct':k(u),
                   'victoria_pct':k(vi),'toprunner_pct':k(tr),'see_pct':k(se),
                   'iww_pct':k(iw),'turbo_pct':k(tu),'hp_exhausted_pct':k(ex),'mean_hp':round(float(np.mean(hps)),1)}
                results.append(r)
                print(f"{lobby[:18]:18s} | {level:11s} | {build[:24]:24s} | win {r['win_pct']:5.1f}% | podium {r['podium_pct']:5.1f}% | native {r['unique_pct']:5.1f}%")
    with open(out/'results.csv','w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(results[0]));w.writeheader();w.writerows(results)
    meta={'date':'2026-10-23','nature':'Illustrative pseudo race study. Not observed CM21 win rates.',
         'trial_count_per_configuration':args.trials,'race_course':'Chukyo 1200 Turf firm winter sunny','race_sections':{'downhill':[100,875],'uphill':[875,975],'late':800,'final_straight':788},
         'player':STATS_BAK.tolist(),'packages':[{'name':n,'sp':sum(PRICES[x] for x in skills),'skills':skills} for n,skills in BUILDS.items()],
         'lobbies':LOBBIES,'opponent_strength_assumptions':OPPONENTS,'results':results,
         'limitations':['All opponent stat distributions and skill templates are assumed, not measured.','Position keep, race lanes, blocking, duel, opponent skills approximated.','Nine participants are not split into three 3-runner teams; user has not supplied teammates.','No claim of calibrated absolute times or win probabilities; use scenario/sensitivity trends.','Pseudo skill scheduling can miss conditions and overcredit some skills, especially Operation Cacao and same-lane effects.']}
    # Provide one fully traceable nine-runner illustrative roster and its finishes.
    demo_seed=int(np.random.SeedSequence([args.seed, 8765]).generate_state(1)[0])
    dsetup=set_up(demo_seed,'Historical-mix (1F 4P 1L 3E)','competitive','Balanced gold + IWW')
    dres=race_one(*dsetup,0)
    names={0:['Aston Machan-like Front','Smart Falcon-like Front'],1:['Nishino-like Pace','Curren-like Pace','El-like Pace','Oguri-like Pace'],2:['Air Groove-like Late','Bamboo-like Late'],3:['Cheer King-like End','Taishin-like End','Sweep-like End']}
    used={k:0 for k in names}
    roster=[]
    for i,st in enumerate(dsetup[0]):
        if i==0:name='Sakura Bakushin O (user)'
        else:
            name=names[int(st)][used[int(st)]%len(names[int(st)])];used[int(st)]+=1
        roster.append({'name':name,'style':['Front','Pace','Late','End'][int(st)],'speed_effective':round(dsetup[1][i,0]),'stamina_effective':round(dsetup[1][i,1]),'power_effective':round(dsetup[1][i,2]),'guts_effective':round(dsetup[1][i,3]),'wit_effective':round(dsetup[1][i,4]),'turf_apt':'S' if dsetup[2][i]>1 else 'A','sprint_apt':'S' if dsetup[3][i]>1 else 'A'})
    demo_bak_place=int(dres[0])
    meta['example_lobby']={'rival_strength':'competitive','package':'Balanced gold + IWW','source':'all rival names are hypothetical archetype labels, not observed trainees','runners':roster,'bakushin_finish_place':demo_bak_place}
    (out/'study.json').write_text(json.dumps(meta,indent=2))
    with open(out/'example_9runner_lobby.csv','w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(roster[0]));w.writeheader();w.writerows(roster)

if __name__=='__main__':main()
