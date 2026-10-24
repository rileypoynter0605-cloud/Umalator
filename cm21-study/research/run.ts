import fs from 'node:fs';
import {gzipSync} from 'node:zlib';
import assert from 'node:assert/strict';
import {RaceSolverBuilder} from '../../uma-skill-tools/RaceSolverBuilder';
import {CourseHelpers} from '../../uma-skill-tools/CourseData';
import {Rule30CARng} from '../../uma-skill-tools/Random';
import data from '../../umalator-global/skill_data.json';
import meta from '../../umalator-global/skill_meta.json';

const out='cm21-study/research';
// Prices are player-supplied TOTAL costs from unowned state. Green ◎ includes ○.
const rows=[
['900141','Victoria por Plancha',120],['910261','Operation Cacao',140],['900611','Prideful King',180],
['200132','Standard Distance ○',81],['200131','Standard Distance ◎',180],['200152','Firm Conditions ○',81],['200151','Firm Conditions ◎',180],['200202','Winter Runner ○',81],['200201','Winter Runner ◎',180],['200262','Outer Post Proficiency ○',81],['200261','Outer Post Proficiency ◎',180],['200331','Professor of Curvature',306],['200332','Corner Adept',180],['200362','Straightaway Adept',153],['200432','Focus',126],['200532','Early Lead',72],['200542','Fast-Paced',162],['200552','Final Push',117],['200651','Turbo Sprint',320],['200652','Sprinting Gear',160],['200981','Staggering Lead',306],['200982','Huge Lead',136],['200992','Countermeasure',160],['201242','Front Runner Straightaways ○',91],['201241','Front Runner Straightaways ◎',189],['201271','Top Runner',342],['201272',"Leader's Pride",180],['201282','Moxie',126],['201522','Front Runner Savvy ○',88],['201521','Front Runner Savvy ◎',192],['201601','Groundwork',80],['201611','Tail Held High',90],['201662','See Ya Later',208],['201661',"Playtime's Over",96],['202042','Light as a Feather',144],['202392','Mad Dash',126],['210071','I Wanna Win With You',380],['210072','On the Way to Our Dream',200]
] as [string,string,number][];
const price=Object.fromEntries(rows.map(r=>[r[0],r[2]]));
const names=Object.fromEntries(rows.map(r=>[r[0],r[1]]));
const proximity=new Set(['100411','910261','201271','201272','201662','201661','200981','200982']);
const horse={speed:1515,stamina:402,power:1003,guts:695,wisdom:976,strategy:'Nige',distanceAptitude:'S',surfaceAptitude:'S',strategyAptitude:'A',mood:0 as const,uniqueLevel:4};
const course=CourseHelpers.getCourse(10701);
const N=Number(process.env.CM21_TRIALS||1024), seed=2120226;
function csv(file:string,rs:any[]){const keys=Object.keys(rs[0]);fs.writeFileSync(`${out}/${file}`,keys.join(',')+'\n'+rs.map(r=>keys.map(k=>JSON.stringify(r[k]??'')).join(',')).join('\n')+'\n');}
function stat(a:number[]){const m=a.reduce((x,y)=>x+y,0)/a.length;const se=Math.sqrt(a.reduce((x,y)=>x+(y-m)**2,0)/(a.length-1)/a.length);return {mean:m,lo:m-1.96*se,hi:m+1.96*se,min:Math.min(...a),max:Math.max(...a)};}
function legal(ids:string[]){return ids.reduce((x,id)=>x+price[id],0)<=2751&&new Set(ids.map(id=>meta[id].groupId)).size===ids.length;}
let calls=0;
function simulate(ids:string[],n=N,scenario='sampled',batchSeed=seed,dt=1/15,rival?:any){
 const events:any[][]=[], times:number[]=[], hp:number[]=[], exhausted:number[]=[],downs:number[]=[],early:number[]=[];
 const builder=new RaceSolverBuilder(n).seed(batchSeed).course(course).horse(horse).mood(0).ground(1).weather(1).season(4).numUmas(9).order(scenario==='back-rank'?4:scenario==='rank-2'?2:1,scenario==='back-rank'?4:scenario==='rank-2'?2:1).mode('compare').hpConsumption(true).skillWisdomCheck(true).rushedKakari(true).competeFight(false).leadCompetition(false);
 // Preserve engine sampling distributions, but key trigger streams by skill GROUP.
 // Thus adding a different skill cannot shift common skills' trigger samples.
 for(const id of ['100411',...ids])builder.addSkill(id,undefined,undefined,undefined,4);
 builder._extraSkillHooks.push(sds=>{for(const sd of sds){const original=sd.samplePolicy;const group=Number((meta as any)[sd.skillId]?.groupId||sd.skillId);sd.samplePolicy={...original,sample:(regions,count,_rng)=>original.sample(regions,count,new Rule30CARng((batchSeed^Math.imul(group,2654435761))>>>0))};if(scenario==='no-proximity'&&proximity.has(sd.skillId))sd.extraCondition=()=>false;}});
 let ev:any[]=[];builder.onSkillActivate((s,id)=>ev.push({id,pos:s.pos,t:s.accumulatetime.t}));
 let index=0;
 for(const s of builder.build()){
  // Constructor can activate green skills, so collect its callbacks before stepping.
  const other=rival?new RaceSolverBuilder(1).seed((batchSeed+index)>>>0).course(course).horse({...horse,...rival}).ground(1).season(4).hpConsumption(true).competeFight(false).leadCompetition(false).build().next().value:null;
  s.initUmas(other?[other]:[]);other?.initUmas([s]);let t=0,finish=0,down=0;
  while(s.pos<1200&&t<120){const p=s.pos;s.step(dt);if(other&&other.pos<1200)other.step(dt);if(s.isDownhillMode)down+=dt;t+=dt;if(s.pos>=1200)finish=t-dt+dt*(1200-p)/(s.pos-p);}
  assert(finish>0&&Number.isFinite(s.hp.hpRatioRemaining()));
  times.push(finish);hp.push(s.hp.hpRatioRemaining());exhausted.push(+s.hpDied);downs.push(down);early.push(s.activateCount[0]);events.push(ev);ev=[];index++;
 }
 calls++;return {times,hp,exhausted,downs,early,events};
}
function compare(a:any,b:any){const z=stat(a.times.map((t,i)=>t-b.times[i]));return {seconds_saved:z.mean,ci95_low:z.lo,ci95_high:z.hi,mean_seconds:stat(b.times).mean,hp_ratio:stat(b.hp).mean,hp_exhausted:b.exhausted.reduce((x,y)=>x+y,0),trials:b.times.length};}
const baseline=simulate([]);
const singles:any[]=[];const score:any={};const cache:any={};
for(const [id,name,cost] of rows){const r=simulate([id]);cache[id]=r;score[id]=compare(baseline,r).seconds_saved;const ev=r.events.flatMap(e=>e.filter(x=>x.id===id));singles.push({id,skill:name,cost,...compare(baseline,r),activation_rate:r.events.filter(e=>e.some(x=>x.id===id)).length/N,activation_m_mean:ev.length?stat(ev.map(x=>x.pos)).mean:null,activation_m_min:ev.length?Math.min(...ev.map(x=>x.pos)):null,activation_m_max:ev.length?Math.max(...ev.map(x=>x.pos)):null,limitation:proximity.has(id)?'sampled proximity; not measured lobby trigger':id==='201601'?'single skill lacks three early activations':id==='200552'?'rank 1 assumption, pre-final-phase acceleration':'fixed rank 1; local Global data'});}
csv('skill_ablation.csv',singles);
const core=['200202','200152','201522','201601','200532','900141'];
const balanced=['900141','910261','200202','200152','200331','200362','200532','200542','200552','200651','201241','201522','201601','201611','201662','202042','210071'];
const packages:any={baseline:[],opening_core:core,prior_balanced:balanced,prior_top_runner:balanced.filter(x=>x!=='210071').concat('201271'),prior_white_focus:balanced.filter(x=>!['200651','200552'].includes(x)).concat('200652','200432')};
// Grouped knapsack generates candidates, followed by complete engine evaluations.
function optimize(excluded:Set<string>){const groups=new Map<string,string[]>();for(const [id]of rows){if(score[id]<=0||excluded.has(id)||core.includes(id)||core.some(x=>meta[x].groupId===meta[id].groupId))continue;const g=meta[id].groupId;groups.set(g,[...(groups.get(g)||[]),id]);}let dp:any[]=Array(2752).fill(null);for(let mask=0;mask<8;mask++){const ids=core.map(id=>{const k=['200202','200152','201522'].indexOf(id);return k>=0&&(mask&(1<<k))?String(Number(id)-1):id;});const initial=ids.reduce((x,id)=>x+price[id],0);dp[initial]={v:ids.reduce((x,id)=>x+(score[id]||0),0),ids};}for(const ids of groups.values()){const next=dp.slice();for(let c=0;c<dp.length;c++){if(!dp[c])continue;for(const id of ids){const k=c+price[id];if(k<=2751&&(!next[k]||next[k].v<dp[c].v+score[id]))next[k]={v:dp[c].v+score[id],ids:dp[c].ids.concat(id)};}}dp=next;}return dp.filter(Boolean).sort((a,b)=>b.v-a.v).slice(0,12);}
const candidates=[...optimize(new Set()),...optimize(new Set([...proximity,'200552','900611','200262','200261']))];
const unique=new Map(candidates.map(x=>[x.ids.slice().sort().join(','),x.ids]));let ix=0;
// Tail's isolated score is zero, but its middle-activation synergy matters in packages.
for(const ids of [...unique.values()])if(!ids.some(id=>proximity.has(id))){
 const tail=ids.includes('201611')?ids:ids.concat('201611');
 const variants=[tail];
 for(const gold of ['200201','200151','201521'])if(tail.includes(gold))variants.push(tail.map(id=>id===gold?String(Number(id)+1):id).concat('200432'));
 for(const v of variants)if(legal(v))unique.set(v.slice().sort().join(','),v);
}
const screening=[];const screenBase=simulate([],128,'sampled',7654321);
for(const ids of unique.values()){assert(legal(ids));const r=simulate(ids,128,'sampled',7654321);screening.push({ids,score:compare(screenBase,r).seconds_saved});}
screening.sort((a,b)=>b.score-a.score);fs.writeFileSync(`${out}/screening.json`,JSON.stringify(screening,null,2));
for(const s of screening.slice(0,3))packages[`candidate_${++ix}`]=s.ids;
// Also retain the best package that excludes purchase-dependent proximity triggers.
const safe=screening.find(s=>!s.ids.some(id=>proximity.has(id)));if(safe)packages.conservative=safe.ids;
const results:any[]=[];const raw:any={baseline,singles:cache,packages:{},upgrades:{}};
for(const scenario of ['sampled','no-proximity','rank-2','back-rank']){const base=scenario==='sampled'?baseline:simulate([],N,scenario);for(const [name,ids]of Object.entries(packages) as any){assert(legal(ids));const r=name==='baseline'?base:simulate(ids,N,scenario);results.push({scenario,package:name,sp:ids.reduce((x,id)=>x+price[id],0),...compare(base,r),skills:ids.map(id=>names[id]).join('; ')});raw.packages[`${scenario}:${name}`]=r;}}
csv('package_comparison.csv',results);
const direct=[];for(const scenario of ['sampled','no-proximity','rank-2','back-rank'])for(const name of ['candidate_1','candidate_2','candidate_3','conservative','prior_top_runner'])if(packages[name])direct.push({scenario,package:name,versus:'prior_balanced',...compare(raw.packages[`${scenario}:prior_balanced`],raw.packages[`${scenario}:${name}`])});csv('package_direct_comparison.csv',direct);
const upgrades:any[]=[];
for(const [white,gold]of [['200652','200651'],['200332','200331'],['201272','201271'],['201661','201662'],['210072','210071'],['201242','201241'],['201522','201521'],['200202','200201'],['200152','200151']]){const context=balanced.filter(id=>meta[id].groupId!==meta[white].groupId);const a=simulate(context.concat(white)),b=simulate(context.concat(gold));upgrades.push({white:names[white],gold:names[gold],incremental_sp:price[gold]-price[white],...compare(a,b)});raw.upgrades[gold]={a,b};}
csv('upgrade_ablation.csv',upgrades);
const ground=[];for(const ids of [['201601'],['200202','201601'],['200202','200152','201601'],['200202','200152','201522','201601']]){const r=simulate(ids);ground.push({skills:ids.join(';'),activation_rate:r.events.filter(e=>e.some(x=>x.id==='201601')).length/N,...compare(baseline,r)});}csv('groundwork.csv',ground);
const sensitivity=[];for(const rival of [{label:'front-competitive',strategy:'Nige',speed:1525,power:1150,wisdom:1130},{label:'pace-competitive',strategy:'Senkou',speed:1525,power:1150,wisdom:1130},{label:'front-elite',strategy:'Nige',speed:1590,power:1260,wisdom:1240}]){const base=simulate([],256,'sampled',seed,1/15,rival);for(const name of ['prior_balanced','candidate_1','conservative'].filter(n=>packages[n])){const r=simulate(packages[name],256,'sampled',seed,1/15,rival);sensitivity.push({rival:rival.label,package:name,...compare(base,r)});}}csv('opponent_sensitivity.csv',sensitivity);
const replay=simulate([],N);assert.deepEqual(baseline,replay);
const fine=simulate([],128,'sampled',seed,1/60),coarse=simulate([],128);const timestep=stat(coarse.times.map((t,i)=>t-fine.times[i]));
const convergence=[];for(const name of ['prior_balanced','candidate_1','conservative'])if(packages[name]){const a=simulate(packages[name],128),b=simulate(packages[name],128,'sampled',seed,1/60);convergence.push({package:name,coarse_gain:compare(coarse,a).seconds_saved,fine_gain:compare(fine,b).seconds_saved});}csv('timestep_sensitivity.csv',convergence);
fs.writeFileSync(`${out}/raw_results.json.gz`,gzipSync(JSON.stringify(raw)));
fs.writeFileSync(`${out}/packages.json`,JSON.stringify(packages,null,2));
fs.writeFileSync(`${out}/skill_catalog.json`,JSON.stringify(rows.map(([id,name,cost])=>({id,name,total_player_cost:cost,meta:meta[id],data:data[id]})),null,2));
fs.writeFileSync(`${out}/verification.json`,JSON.stringify({commit:process.env.CM21_COMMIT||'96b870a1cf1c9947a81167cce680fa61081d3e07',node:process.version,N,seed,course,horse,replay_exact:true,timestep_seconds:timestep,baseline:{time:stat(baseline.times),hp:stat(baseline.hp),downhill_seconds:stat(baseline.downs),exhausted:baseline.exhausted.reduce((x,y)=>x+y,0),unique_activation:baseline.events.filter(e=>e.some(x=>x.id==='100411')).length/N},calls},null,2));
console.log(JSON.stringify({calls,N,baseline:stat(baseline.times),best:results.filter(r=>r.scenario==='sampled').sort((a,b)=>b.seconds_saved-a.seconds_saved).slice(0,4)},null,2));
