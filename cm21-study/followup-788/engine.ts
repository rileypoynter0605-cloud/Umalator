import fs from 'node:fs';
import assert from 'node:assert/strict';
import {RaceSolverBuilder} from '../../uma-skill-tools/RaceSolverBuilder';
import {CourseHelpers} from '../../uma-skill-tools/CourseData';
import {Rule30CARng} from '../../uma-skill-tools/Random';
import {Region} from '../../uma-skill-tools/Region';

export const DIR = 'cm21-study/followup-788';
export const catalog = JSON.parse(fs.readFileSync('cm21-study/research/skill_catalog.json', 'utf8'));
export const entries = Object.fromEntries(catalog.map(x => [x.id, x]));
export const oldPackages = JSON.parse(fs.readFileSync('cm21-study/research/packages.json', 'utf8'));
export const originalCourse = JSON.stringify(CourseHelpers.getCourse(10701));
export const stats = {speed:1515, stamina:402, power:1003, guts:695, wisdom:976,
  strategy:'Nige', distanceAptitude:'S', surfaceAptitude:'S', strategyAptitude:'A', mood:0 as const, uniqueLevel:4};
export const quartet = ['200981', '201271', '910261', '201662'];
export const families = {native:['100411'], gap:['200981','200982'], side:['201271','201272'], close:['910261','201662','201661']};
export type Rates = {native:number, gap:number, side:number, close:number};
export type Model = 'independent'|'positive'|'exclusive'|'gap-to-contact'|'contact-to-gap'|'native-linked';
export interface Profile {name:string; rates:Rates; model:Model; rank?:number;}
export interface Hp {name:string; multiplier:number; drains:[number,number][];}
export const normal:Hp = {name:'normal', multiplier:1, drains:[]};
export const ref:Profile = {name:'reference-independent', model:'independent', rates:{native:.5,gap:.35,side:.45,close:.5}};
export const correlated:Profile[] = [ref, ...(['positive','exclusive','gap-to-contact','contact-to-gap','native-linked'] as Model[]).map(model => ({...ref, name:`reference-${model}`, model}))];
export const envelopes:Profile[] = [
  ...correlated,
  {name:'clear-front', model:'exclusive', rates:{native:.2,gap:.75,side:.2,close:.2}},
  {name:'contested-front', model:'exclusive', rates:{native:.7,gap:.1,side:.75,close:.8}},
  {name:'rank-2-contact', model:'exclusive', rank:2, rates:{native:.7,gap:0,side:.7,close:.8}},
  {name:'sparse-contact', model:'independent', rates:{native:.15,gap:.25,side:.1,close:.15}}
];
export const hpCases:Hp[] = [normal,
  {name:'cost+10pct',multiplier:1.1,drains:[]},
  {name:'cost+20pct',multiplier:1.2,drains:[]},
  {name:'drain3pct',multiplier:1,drains:[[400,.03]]},
  {name:'drain6pct',multiplier:1,drains:[[400,.03],[650,.03]]},
  {name:'cost+20pct-drain3pct',multiplier:1.2,drains:[[400,.03]]},
  {name:'cost+20pct-drain6pct',multiplier:1.2,drains:[[400,.03],[650,.03]]},
  {name:'cost+35pct-drain6pct',multiplier:1.35,drains:[[400,.03],[650,.03]]}
];
export function cost(ids:string[]) {return ids.reduce((sum,id) => sum+entries[id].total_player_cost, 0);}
export function legal(ids:string[]) {return cost(ids)<=2751 && new Set(ids.map(id=>entries[id].meta.groupId)).size===ids.length;}
export function mean(a:number[]) {return a.reduce((x,y)=>x+y,0)/a.length;}
export function summary(a:number[]) {
  const m=mean(a), se=Math.sqrt(a.reduce((x,y)=>x+(y-m)**2,0)/Math.max(1,a.length-1)/a.length);
  const sorted=[...a].sort((x,y)=>x-y);
  return {mean:m, low:m-1.96*se, high:m+1.96*se, min:sorted[0], p05:sorted[Math.floor(a.length*.05)], max:sorted.at(-1)};
}
export function csv(name:string, rows:any[]) {
  if(!rows.length) return;
  const keys=Object.keys(rows[0]);
  const quote=(v:any)=>JSON.stringify(v??'');
  fs.writeFileSync(`${DIR}/${name}.csv`,keys.join(',')+'\n'+rows.map(r=>keys.map(k=>quote(r[k])).join(',')).join('\n')+'\n');
}
// Independent deterministic uniform streams by trial and purpose; no global Math.random.
export function u(seed:number,trial:number,key:number) {
  let x=(seed ^ Math.imul(trial+1,0x9e3779b9) ^ Math.imul(key+1,0x85ebca6b))>>>0;
  x^=x>>>16; x=Math.imul(x,0x7feb352d); x^=x>>>15; x=Math.imul(x,0x846ca68b); x^=x>>>16;
  return (x>>>0)/4294967296;
}
export function opportunityKey(id:string) {return id==='910261'?'cacao':['201662','201661'].includes(id)?'tail':family(id);}
function family(id:string) {return Object.keys(families).find(k=>families[k].includes(id));}
export function opportunities(profile:Profile, seed:number, trial:number) {
  const {rates:p,model}=profile;
  const shared=u(seed,trial,70);
  const out:any = {};
  for(const k of Object.keys(families)) {
    const i=Object.keys(families).indexOf(k);
    let r=u(seed,trial,80+i);
    if(k!=='native' && model!=='independent') r=shared;
    if(model==='native-linked') r=shared;
    // Circularly shifted shared uniforms preserve marginals while making a clear
    // gap and contact mutually exclusive whenever the requested marginals allow.
    if(model==='exclusive' && k!=='native' && k!=='gap') r=(shared-p.gap+1)%1;
    out[k]=r<p[k];
  }
  out.cacao=(model==='independent'?u(seed,trial,90):model==='exclusive'?(shared-p.gap+1)%1:shared)<p.close;
  out.tail=(model==='independent'?u(seed,trial,91):model==='exclusive'?(shared-p.gap+1)%1:shared)<p.close;
  return out;
}
export function courseAt(boundary:number, geometry='coherent') {
  assert([788,800].includes(boundary));
  const c=JSON.parse(originalCourse);
  c.straights.at(-1).start=boundary;
  if(geometry==='coherent')c.corners.at(-1).length=boundary-c.corners.at(-1).start;
  if(geometry==='coherent')assert.equal(c.corners.at(-1).start+c.corners.at(-1).length,c.straights.at(-1).start);
  assert.equal(CourseHelpers.phaseStart(c.distance,2),800);
  return c;
}
function window(fam:string, profile:Profile):[number,number] {
  if(profile.model==='gap-to-contact') {
    return fam==='gap'?[200,420]:fam==='side'?[420,650]:fam==='close'?[650,788]:[600,1200];
  }
  if(profile.model==='contact-to-gap') {
    return fam==='gap'?[550,788]:fam==='side'?[100,350]:fam==='close'?[350,550]:[600,1200];
  }
  return [0,1200];
}
export interface Result {times:number[]; hp:number[]; exhausted:number[]; full:number[]; delay:number[]; v788:number[]; v800:number[]; hp800:number[]; bonus800:number[]; accel800:number[]; events:any[][]; eligible:any[]; traces:any[]; ids:string[];}
export function simulate(ids:string[], boundary=788, profile:Profile=ref, n=1024, seed=871203, hp:Hp=normal, dt=1/15, geometry='coherent'):Result {
  const all=['100411',...ids].sort((a,b)=>Number(a)-Number(b));
  assert.equal(new Set(all).size,all.length);
  const r:Result={times:[],hp:[],exhausted:[],full:[],delay:[],v788:[],v800:[],hp800:[],bonus800:[],accel800:[],events:[],eligible:[],traces:[],ids:all};
  let trial=0, ev:any[]=[];
  const flags=Array.from({length:n},(_,i)=>opportunities(profile,seed,i));
  const b=new RaceSolverBuilder(n).seed(seed).course(courseAt(boundary,geometry)).horse(stats).mood(0)
    .ground(1).weather(1).season(4).numUmas(9).order(profile.rank||1,profile.rank||1)
    .mode('compare').hpConsumption(true).skillWisdomCheck(true).rushedKakari(true).competeFight(false).leadCompetition(false);
  all.forEach(id=>b.addSkill(id,undefined,undefined,undefined,4));
  b._extraSkillHooks.push(sds=>{
    for(const sd of sds) {
      const policy=sd.samplePolicy, group=Number(entries[sd.skillId]?.meta.groupId||sd.skillId);
      // Same group, same samples even after adding/removing other skills or changing boundary.
      sd.samplePolicy={...policy,sample:(regions,count,_rng)=>policy.sample(regions,count,new Rule30CARng((seed^Math.imul(group,2654435761))>>>0))};
      const fam=family(sd.skillId), originalCondition=sd.extraCondition;
      if(fam) {
        const [lo,hi]=window(fam,profile);
        // Timed synthetic contact windows use Umalator's static valid regions but
        // replace its sampled proxy with a persistent window (not a live lobby).
        if(fam!=='native' && ['gap-to-contact','contact-to-gap'].includes(profile.model)) {
          const regs=sd.regions.map(x=>new Region(Math.max(x.start,lo),Math.min(x.end,hi))).filter(x=>x.end>x.start);
          sd.samplePolicy={...policy,sample:(_regions,count,_rng)=>Array.from({length:count},()=>regs[0]||new Region(9999,10000))};
          sd.extraCondition=(s)=>flags[trial][opportunityKey(sd.skillId)!] && s.pos>=lo && s.pos<hi && originalCondition(s);
        } else {
          sd.extraCondition=(s)=>flags[trial][opportunityKey(sd.skillId)!] && originalCondition(s);
        }
      }
    }
  });
  b.onSkillActivate((s,id)=>ev.push({id,pos:s.pos,t:s.accumulatetime.t,phase:s.phase}));
  for(const s of b.build()) {
    // Greens/early-start constructor decisions remain engine-native. Subsequent
    // WIT rolls preserve the engine formula but use a per-group/trial draw.
    s.checkWisdomForSkill=(skill)=>{
      const wisdom=skill.perspective===2&&skill.originWisdom!==undefined?skill.originWisdom:s.horse.rawWisdom;
      return u(seed,trial,1000+Number(entries[skill.skillId]?.meta.groupId||skill.skillId))<=Math.max(100-9000/wisdom,20)*.01;
    };
    const policy:any=s.hp, originalModifier=policy.getStatusModifier.bind(policy);
    policy.getStatusModifier=(state)=>originalModifier(state)*hp.multiplier;
    s.initUmas([]);
    let t=0,finish=0,dose=0,nextCheckpoint=0;
    const checkpoints=[788,800,810,825,850,875,900,975,1000];
    const trace:any[]=[];
    while(s.pos<1200&&t<150) {
      while(dose<hp.drains.length&&s.pos>=hp.drains[dose][0]) {policy.recover(-hp.drains[dose][1]);dose++;}
      const before={pos:s.pos,v:s.currentSpeed,t, hp:s.hp.hpRatioRemaining()};
      s.step(dt);t+=dt;
      while(nextCheckpoint<checkpoints.length&&s.pos>=checkpoints[nextCheckpoint]) {
        const x=checkpoints[nextCheckpoint++];
        const fraction=(x-before.pos)/(s.pos-before.pos);
        const snap={distance:x,t:t-dt+dt*fraction,speed:before.v+(s.currentSpeed-before.v)*fraction,
          hp:s.hp.hpRatioRemaining(),target:s.targetSpeed,accel:s.accel,
          speed_bonus:s.modifiers.targetSpeed.acc+s.modifiers.targetSpeed.err,
          accel_bonus:s.modifiers.accel.acc+s.modifiers.accel.err,
          active_speed:s.activeTargetSpeedSkills.map(a=>a.skillId).join(';'),
          active_accel:s.activeAccelSkills.map(a=>a.skillId).join(';')};
        trace.push(snap);
      }
      if(s.pos>=1200)finish=t-dt+dt*(1200-before.pos)/(s.pos-before.pos);
    }
    assert(finish>0&&Number.isFinite(finish));
    const at=(x)=>trace.find(v=>v.distance===x);
    r.times.push(finish);r.hp.push(s.hp.hpRatioRemaining());r.exhausted.push(+s.hpDied);
    r.full.push(+s.fullSpurt);r.delay.push(s.nonFullSpurtDelayDistance??0);
    r.v788.push(at(788).speed);r.v800.push(at(800).speed);r.hp800.push(at(800).hp);
    r.bonus800.push(at(800).speed_bonus);r.accel800.push(at(800).accel_bonus);
    r.events.push(ev);r.eligible.push(flags[trial]);
    if(trial<4)r.traces.push({trial,trace,events:ev});
    ev=[];trial++;
  }
  assert.equal(JSON.stringify(CourseHelpers.getCourse(10701)),originalCourse);
  return r;
}
export function difference(a:Result,b:Result) {return summary(a.times.map((v,i)=>v-b.times[i]));}
export function metrics(r:Result) {
  const t=summary(r.times),h=summary(r.hp);
  return {trials:r.times.length,mean_seconds:t.mean,mean_hp:h.mean,hp_p05:h.p05,hp_min:h.min,
    exhausted_fraction:mean(r.exhausted),full_spurt_fraction:mean(r.full),mean_spurt_delay_m:mean(r.delay),
    speed_788:mean(r.v788),speed_800:mean(r.v800),hp_800:mean(r.hp800),speed_bonus_800:mean(r.bonus800),accel_bonus_800:mean(r.accel800)};
}
export function activations(r:Result,labels:any) {
  return r.ids.map(id=>{
    const events=r.events.flatMap(es=>es.filter(e=>e.id===id));
    const fam=family(id);
    const v=(key)=>events.length?mean(events.map(e=>e[key])):null;
    return {...labels,id,skill:entries[id]?.name||'Native unique Lv4',family:fam||'non-proximity',
      opportunity_fraction:fam?mean(r.eligible.map(e=>+e[opportunityKey(id)!])):null,
      activation_fraction:r.events.filter(es=>es.some(e=>e.id===id)).length/r.events.length,
      mean_trigger_m:v('pos'),mean_trigger_seconds:v('t'),pre800_fraction:events.length?events.filter(e=>e.pos<800).length/r.events.length:0};
  });
}
export function compact(r:Result) {
  const bits=r.events.map(es=>es.reduce((sum,e)=>sum+2**r.ids.indexOf(e.id),0));
  return {...r,events:undefined,activation_bits:bits,traces:r.traces};
}
