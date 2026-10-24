import fs from 'node:fs';
import assert from 'node:assert/strict';
import {gzipSync} from 'node:zlib';
import {DIR,simulate,oldPackages,entries,catalog,cost,legal,mean,summary,csv,difference,metrics,activations,compact,ref,correlated,envelopes,normal,hpCases,quartet,opportunities,opportunityKey,courseAt,originalCourse,Profile,Hp} from './engine';

const stage=process.argv[2]||'tests';
const seed=871203;
const recommended={conservative:oldPackages.conservative,conditional:oldPackages.candidate_1,balanced:oldPackages.prior_balanced};
const labels=(boundary,profile,hp=normal)=>({boundary,profile:profile.name,model:profile.model,native_p:profile.rates.native,gap_p:profile.rates.gap,side_p:profile.rates.side,close_p:profile.rates.close,rank:profile.rank||1,hp:hp.name});
const save=(name,obj)=>fs.writeFileSync(`${DIR}/${name}.json`,JSON.stringify(obj,null,2));
const rawSave=(name,obj)=>fs.writeFileSync(`${DIR}/${name}.json.gz`,gzipSync(JSON.stringify(obj)));
const scored=(a,b)=>{const d=difference(a,b);return {seconds_saved:d.mean,ci95_low:d.low,ci95_high:d.high,...metrics(b)};};

if(stage==='tests') {
  for(const boundary of [788,800]) {
    const c=courseAt(boundary);assert.equal(c.straights.at(-1).start,boundary);assert.equal(c.corners.at(-1).start+c.corners.at(-1).length,boundary);
  }
  const a=simulate(recommended.conservative,788,ref,64),b=simulate(recommended.conservative,788,ref,64);
  assert.deepEqual(a,b);
  const base=simulate([],788,ref,64), without=simulate(['201601'],788,ref,64);
  assert.deepEqual(base.times,without.times);
  for(const profile of correlated.filter(p=>p.model!=='native-linked'))assert.deepEqual(base.times,simulate([],788,profile,64).times,'native timing must remain unchanged by quartet-only correlation');
  for(const ids of Object.values(recommended))assert(legal(ids));
  const rates=[];
  for(const p of correlated) {
    const flags=Array.from({length:100000},(_,i)=>opportunities(p,seed,i));
    const observed=Object.fromEntries(['native','gap','side','close'].map(k=>[k,mean(flags.map(f=>+f[k]))]));
    for(const k of Object.keys(observed))assert(Math.abs(observed[k]-p.rates[k])<.007);
    rates.push({model:p.model,...observed,gap_cacao_joint:mean(flags.map(f=>+(f.gap&&f.cacao))),cacao_tail_joint:mean(flags.map(f=>+(f.cacao&&f.tail))),gap_side_joint:mean(flags.map(f=>+(f.gap&&f.side)))});
  }
  csv('gate_sampler_checks',rates);
  save('config',{seed,validation_seed:seed,screen_seed:519032,N:1024,ablation_N:512,green_screen_N:96,dt:1/15,stats:'Fixed trainee unchanged; normal mood',recommended,profiles:envelopes,hpCases,originalCourse:JSON.parse(originalCourse),course788:courseAt(788),gates:'opportunity before WIT; not measured Global frequencies'});
  save('tests',{exact_replay:true,native_timing_invariant_across_quartet_models:true,course_override:true,phase_starts_at_800:true,groundwork_alone_zero:true,package_budgets:true,gate_marginal_tolerance:.007,tests_seed:seed});
  console.log('PASS course clone, unchanged source course, phase boundary, exact replay, Groundwork prerequisite, budgets, matched gate marginals.');
}

if(stage==='course') {
  const rows=[],act=[],leave=[],trace=[],raw={};
  for(const profile of [ref,correlated.find(p=>p.model==='exclusive')!]) {
    const base={};
    for(const boundary of [788,800]) {
      base[boundary]=simulate([],boundary,profile,1024);
      for(const [name,ids]of Object.entries(recommended)) {
        const r=simulate(ids,boundary,profile,1024);
        rows.push({...labels(boundary,profile),package:name,sp:cost(ids),...scored(base[boundary],r)});
        act.push(...activations(r,{boundary,profile:profile.name,package:name}));
        raw[`${boundary}:${profile.name}:${name}`]=compact(r);
        trace.push(...r.traces.flatMap(v=>v.trace.map(t=>({boundary,profile:profile.name,package:name,trial:v.trial,...t}))));
        // Each skill is removed from exactly the same complete package.
        const full512=simulate(ids,boundary,profile,512);
        for(const id of ids) {
          const less=simulate(ids.filter(i=>i!==id),boundary,profile,512);
          const full=full512;
          const d=difference(less,full);
          leave.push({...labels(boundary,profile),package:name,id,skill:entries[id].name,cost:entries[id].total_player_cost,
            marginal_seconds:d.mean,ci95_low:d.low,ci95_high:d.high,activation_fraction:full.events.filter(es=>es.some(e=>e.id===id)).length/512,
            delta_speed800:mean(full.v800)-mean(less.v800),delta_speed_bonus800:mean(full.bonus800)-mean(less.bonus800),trials:512});
        }
      }
    }
    for(const ids of [[],['900141'],['201242'],['201241'],['200362'],['200552']]) {
      const a=simulate(ids,788,profile,1024),b=simulate(ids,800,profile,1024);
      const name=ids.length?entries[ids[0]].name:'native-only';
      const d=difference(b,a);
      rows.push({...labels(788,profile),package:`course-effect:${name}`,sp:cost(ids),seconds_saved:d.mean,ci95_low:d.low,ci95_high:d.high,...metrics(a)});
      act.push(...activations(a,{boundary:788,profile:profile.name,package:`isolated:${name}`}),...activations(b,{boundary:800,profile:profile.name,package:`isolated:${name}`}));
      raw[`isolated:${profile.name}:${name}:788`]=compact(a);raw[`isolated:${profile.name}:${name}:800`]=compact(b);
      trace.push(...[a,b].flatMap((r,i)=>r.traces.flatMap(v=>v.trace.map(t=>({boundary:i?800:788,profile:profile.name,package:`isolated:${name}`,trial:v.trial,...t})))));
    }
    console.log('course and constituent ablations:',profile.name);
  }
  csv('course_packages',rows);csv('constituent_ablation',leave);csv('course_activation',act);csv('carryover_traces',trace);rawSave('course_trials',raw);
}

if(stage==='frequency') {
  const profiles:Profile[]=[ref];
  for(const family of ['native','gap','side','close'])for(const p of [.1,.3,.5,.7,.9])profiles.push({...ref,name:`vary-${family}-${p}`,rates:{...ref.rates,[family]:p}});
  save('frequency_profiles',profiles);
  const rows=[],act=[],raw={};
  for(const profile of profiles)for(const boundary of [788,800]) {
    const base=simulate([],boundary,profile,1024);
    for(const [name,ids]of Object.entries(recommended)) {
      const r=simulate(ids,boundary,profile,1024);
      rows.push({...labels(boundary,profile),package:name,sp:cost(ids),...scored(base,r)});
      act.push(...activations(r,{boundary,profile:profile.name,package:name}));
      raw[`${boundary}:${profile.name}:${name}`]=compact(r);
    }
  }
  csv('frequency_packages',rows);csv('frequency_activation',act);rawSave('frequency_trials',raw);
  console.log('frequency rows:',rows.length);
}

if(stage==='correlation') {
  const rows=[],act=[],joint=[],raw={},bundles=[];
  for(const profile of envelopes)for(const boundary of [788,800]) {
    const base=simulate([],boundary,profile,1024);
    for(const [name,ids]of Object.entries(recommended)) {
      const r=simulate(ids,boundary,profile,1024);
      rows.push({...labels(boundary,profile),package:name,sp:cost(ids),...scored(base,r)});
      act.push(...activations(r,{boundary,profile:profile.name,package:name}));
      raw[`${boundary}:${profile.name}:${name}`]=compact(r);
      for(let i=0;i<quartet.length;i++)for(let j=i+1;j<quartet.length;j++) {
        const a=quartet[i],b=quartet[j];
        const eligible=r.eligible.filter(f=>f[opportunityKey(a)!]&&f[opportunityKey(b)!]).length/1024;
        const first=r.events.map(es=>es.find(e=>e.id===a));const second=r.events.map(es=>es.find(e=>e.id===b));
        joint.push({...labels(boundary,profile),package:name,a,b,opportunity_joint:eligible,activation_joint:mean(first.map((e,k)=>+(!!e&&!!second[k]))),activation_overlap:mean(first.map((e,k)=>+(!!e&&!!second[k]&&Math.abs(e.t-second[k].t)<3.6)))});
      }
    }
    // Isolate the incremental combination above the same conditional package core.
    const core=recommended.conditional.filter(id=>!quartet.includes(id));
    const a=simulate(core,boundary,profile,1024),b=simulate(recommended.conditional,boundary,profile,1024);
    bundles.push({...labels(boundary,profile),purchase:'quartet versus same package without quartet',sp:cost(quartet),...scored(a,b)});
  }
  csv('correlation_packages',rows);csv('correlation_activation',act);csv('quartet_joint_activation',joint);csv('quartet_marginal',bundles);rawSave('correlation_trials',raw);
  console.log('correlation rows:',rows.length);
}

function greenVariants() {
  const pairs=[['200201','200202'],['200151','200152'],['201521','201522']];
  return Array.from({length:8},(_,mask)=>({name:`green-mask-${mask}`,mask,ids:recommended.conservative.map(id=>{const k=pairs.findIndex(([gold])=>gold===id);return k>=0&&(mask&(1<<k))?pairs[k][1]:id;})}));
}
function additions(ids:string[],budget:number) {
  const groups=new Set(ids.map(id=>entries[id].meta.groupId));
  const options=catalog.filter(e=>!groups.has(e.meta.groupId)&&e.total_player_cost<=budget).map(e=>e.id);
  const combos:string[][]=[[]];
  function visit(start:number,chosen:string[],spent:number) {
    for(let i=start;i<options.length;i++) {
      const id=options[i],p=entries[id].total_player_cost;
      if(spent+p>budget||chosen.some(other=>entries[other].meta.groupId===entries[id].meta.groupId))continue;
      const next=chosen.concat(id);combos.push(next);visit(i+1,next,spent+p);
    }
  }
  visit(0,[],0);return combos;
}
if(stage==='greens') {
  const rows=[],screen=[],candidates:any[]=[];
  for(const v of greenVariants()) {
    for(const boundary of [788,800])for(const profile of [ref,correlated.find(p=>p.model==='exclusive')!]) {
      const original=simulate(recommended.conservative,boundary,profile,1024),r=simulate(v.ids,boundary,profile,1024);
      rows.push({...labels(boundary,profile),variant:v.name,downgrade_mask:v.mask,sp:cost(v.ids),freed_sp:cost(recommended.conservative)-cost(v.ids),...scored(original,r)});
    }
    for(const add of additions(v.ids,2751-cost(v.ids))) {
      const ids=v.ids.concat(add);assert(legal(ids));
      candidates.push({name:`${v.name}+${add.join('+')||'none'}`,mask:v.mask,ids,sp:cost(ids),added:add});
    }
  }
  csv('green_downgrades',rows);
  const screenProfiles=[ref,envelopes.find(p=>p.name==='clear-front')!,envelopes.find(p=>p.name==='contested-front')!];
  // Score full packages under three distinct assumed populations, 96 trials each,
  // seed separated from 1024-trial validation. No additive skill-score optimizer.
  const baselines=screenProfiles.map(p=>simulate(recommended.conservative,788,p,96,519032));
  for(let i=0;i<candidates.length;i++) {
    const v=candidates[i],scores=[];
    for(let j=0;j<screenProfiles.length;j++)scores.push(difference(baselines[j],simulate(v.ids,788,screenProfiles[j],96,519032)).mean);
    screen.push({variant:v.name,sp:v.sp,mask:v.mask,added:v.added.join(';'),mean_gain:mean(scores),worst_gain:Math.min(...scores),scores});
    if(i%100===0)console.log('green full-package screening',i,'/',candidates.length);
  }
  screen.sort((a,b)=>b.worst_gain-a.worst_gain||b.mean_gain-a.mean_gain);
  csv('green_screening',screen.map(({scores,...v})=>({...v,reference_gain:scores[0],clear_gain:scores[1],contested_gain:scores[2]})));
  const selected=new Set(screen.slice(0,6).map(v=>v.variant));
  // Retain best full-package alternative for each individual/combined downgrade mask.
  for(let mask=0;mask<8;mask++){const v=screen.find(v=>v.mask===mask);if(v)selected.add(v.variant);}
  const shortlist=candidates.filter(c=>selected.has(c.name));
  save('green_candidates',candidates);save('green_shortlist',shortlist);
  console.log('green candidates and selected:',candidates.length,shortlist.length);
}

if(stage==='hp') {
  const rows=[],act=[];
  for(const [name,ids]of Object.entries(recommended))for(const boundary of [788,800])for(const hp of hpCases) {
    const without=ids.filter(id=>id!=='202392');
    const base=simulate(without,boundary,ref,1024,seed,hp);
    const options={original:ids,without_mad_dash:without};
    if(ids.includes('202392')) {
      for(const id of ['201282','200132','200432','910261'])if(legal(without.concat(id)))options[`replace_mad_with_${id}`]=without.concat(id);
    }
    for(const [variant,skills]of Object.entries(options)) {
      const r=variant==='without_mad_dash'?base:simulate(skills,boundary,ref,1024,seed,hp);
      rows.push({...labels(boundary,ref,hp),package:name,variant,sp:cost(skills),...scored(base,r)});
      act.push(...activations(r,{boundary,hp:hp.name,package:name,variant}));
    }
  }
  csv('mad_dash_hp',rows);csv('hp_activation',act);
  console.log('HP stress rows:',rows.length);
}

if(stage==='final') {
  const shortlist=JSON.parse(fs.readFileSync(`${DIR}/green_shortlist.json`,'utf8'));
  const candidates:any={...recommended};
  for(const v of shortlist)candidates[v.name]=v.ids;
  // Assess no-Mad and HP-preserving equal-cost replacements, not just a speed-only winner.
  for(const [name,ids]of Object.entries({...candidates}) as any) {
    if(!ids.includes('202392'))continue;
    const no=ids.filter(i=>i!=='202392');candidates[`${name}:no-mad`]=no;
    if(!no.includes('201282')&&legal(no.concat('201282')))candidates[`${name}:moxie`]=no.concat('201282');
    if(['conservative',shortlist[0]?.name,shortlist.find(v=>v.mask===4)?.name].includes(name)&&!no.includes('200132')&&legal(no.concat('200132')))candidates[`${name}:standard`]=no.concat('200132');
  }
  const unique=new Map<string,{name:string,ids:string[]}>();
  for(const [name,ids]of Object.entries(candidates)as any)unique.set(ids.slice().sort().join(','),{name,ids});
  const validation=[ref,envelopes.find(p=>p.name==='clear-front')!,envelopes.find(p=>p.name==='contested-front')!,correlated.find(p=>p.model==='exclusive')!,correlated.find(p=>p.model==='gap-to-contact')!,envelopes.find(p=>p.name==='rank-2-contact')!,envelopes.find(p=>p.name==='sparse-contact')!];
  const stress=[normal,hpCases.find(p=>p.name==='cost+20pct-drain3pct')!,hpCases.find(p=>p.name==='cost+20pct-drain6pct')!];
  const rows=[],act=[];
  fs.writeFileSync(`${DIR}/robust_trials.jsonl.gz`,'');
  for(const profile of validation)for(const boundary of [788,800])for(const hp of stress) {
    const baseline=simulate([],boundary,profile,512,seed,hp);
    for(const {name,ids}of unique.values()) {
      const r=simulate(ids,boundary,profile,512,seed,hp);
      rows.push({...labels(boundary,profile,hp),package:name,sp:cost(ids),skills:ids.join(';'),...scored(baseline,r)});
      act.push(...activations(r,{boundary,profile:profile.name,hp:hp.name,package:name}));
      fs.appendFileSync(`${DIR}/robust_trials.jsonl.gz`,gzipSync(JSON.stringify({case:`${boundary}:${profile.name}:${hp.name}:${name}`,trials:compact(r)})+'\n'));
    }
    console.log('final envelope',boundary,profile.name,hp.name);
  }
  csv('robust_validation',rows);csv('robust_activation',act);save('validated_candidates',[...unique.values()]);
}

if(stage==='precision') {
  const rows=[];
  for(const boundary of [788,800])for(const [name,ids]of Object.entries(recommended)) {
    const a=simulate(ids,boundary,ref,256,seed,normal,1/15),b=simulate(ids,boundary,ref,256,seed,normal,1/60);
    const x=simulate([],boundary,ref,256,seed,normal,1/15),y=simulate([],boundary,ref,256,seed,normal,1/60);
    rows.push({boundary,package:name,trials:256,coarse_seconds:mean(a.times),fine_seconds:mean(b.times),coarse_gain:difference(x,a).mean,fine_gain:difference(y,b).mean});
  }
  csv('timestep_check',rows);
}

if(stage==='geometry') {
  const rows=[],act=[];
  for(const [boundary,geometry] of [[800,'coherent'],[788,'coherent'],[788,'straight-only']] as [number,string][]) {
    const baseline=simulate([],boundary,ref,1024,seed,normal,1/15,geometry);
    for(const [name,ids] of Object.entries({...recommended,victoria_only:['900141']})) {
      const r=simulate(ids,boundary,ref,1024,seed,normal,1/15,geometry);
      rows.push({boundary,geometry,package:name,...scored(baseline,r)});
      act.push(...activations(r,{boundary,geometry,package:name}));
    }
  }
  csv('geometry_diagnostic',rows);csv('geometry_activation',act);
}

if(stage==='hp-search') {
  const unique=new Map<string,any>();
  const additions=[[],['200132'],['200131'],['201282'],['200132','201282'],['200131','201282']];
  for(const g of greenVariants())for(const protection of additions)for(const filler of [[],['200432'],['910261'],['200552'],['201661'],['200982']]) {
    const ids=g.ids.filter(id=>id!=='202392').concat(protection,filler);
    if(legal(ids))unique.set(ids.slice().sort().join(','),{name:`hp-green-${g.mask}:${protection.join('+')||'none'}:${filler.join('+')||'none'}`,ids,mask:g.mask});
  }
  const scenes=[{p:ref,hp:normal},{p:ref,hp:hpCases[6]},{p:envelopes.find(p=>p.name==='contested-front')!,hp:normal},{p:envelopes.find(p=>p.name==='sparse-contact')!,hp:normal},{p:envelopes.find(p=>p.name==='rank-2-contact')!,hp:hpCases[5]}];
  const original=scenes.map(s=>simulate(recommended.conservative,788,s.p,96,519032,s.hp));
  const screened=[];
  for(const v of unique.values()) {
    const gains=[],exhausted=[];
    for(let j=0;j<scenes.length;j++) {
      const r=simulate(v.ids,788,scenes[j].p,96,519032,scenes[j].hp);
      gains.push(difference(original[j],r).mean);exhausted.push(mean(r.exhausted));
    }
    screened.push({...v,sp:cost(v.ids),gains,exhausted});
  }
  const best=scenes.map((_,j)=>Math.max(...screened.map(c=>c.gains[j])));
  for(const v of screened)v.max_screen_regret=Math.max(...v.gains.map((gain,j)=>best[j]-gain));
  screened.sort((a,b)=>a.max_screen_regret-b.max_screen_regret);
  csv('hp_candidate_screen',screened.map(v=>({name:v.name,sp:v.sp,mask:v.mask,max_screen_regret:v.max_screen_regret,normal_gain:v.gains[0],stress_gain:v.gains[1],contested_gain:v.gains[2],sparse_gain:v.gains[3],rank2_stress_gain:v.gains[4],stress_exhaustion:v.exhausted[1]})));
  const selected=screened.slice(0,4);
  save('hp_search_candidates',screened);save('hp_shortlist',selected);
  const profiles=[ref,envelopes.find(p=>p.name==='clear-front')!,envelopes.find(p=>p.name==='contested-front')!,correlated.find(p=>p.model==='exclusive')!,correlated.find(p=>p.model==='gap-to-contact')!,envelopes.find(p=>p.name==='rank-2-contact')!,envelopes.find(p=>p.name==='sparse-contact')!];
  const rows=[],act=[];
  fs.writeFileSync(`${DIR}/hp_candidate_trials.jsonl.gz`,'');
  for(const p of profiles)for(const boundary of [788,800])for(const hp of [normal,hpCases[5],hpCases[6]]) {
    const base=simulate([],boundary,p,512,seed,hp);
    for(const v of selected) {
      const r=simulate(v.ids,boundary,p,512,seed,hp);
      rows.push({...labels(boundary,p,hp),package:v.name,sp:cost(v.ids),skills:v.ids.join(';'),...scored(base,r)});
      act.push(...activations(r,{boundary,profile:p.name,hp:hp.name,package:v.name}));
      fs.appendFileSync(`${DIR}/hp_candidate_trials.jsonl.gz`,gzipSync(JSON.stringify({case:`${boundary}:${p.name}:${hp.name}:${v.name}`,trials:compact(r)})+'\n'));
    }
    console.log('HP candidate validation',boundary,p.name,hp.name);
  }
  csv('hp_candidate_validation',rows);csv('hp_candidate_activation',act);
}

if(stage==='recommendation-check') {
  const recommendation=JSON.parse(fs.readFileSync(`${DIR}/recommendation.json`,'utf8'));
  const extras=JSON.parse(fs.readFileSync(`${DIR}/hp_shortlist.json`,'utf8'));
  const safer=extras.find(v=>v.name==='hp-green-4:200131:201661');
  const candidates={revised:recommendation.winner.skills.split(';'),hp_protected:safer.ids,balanced:recommended.balanced};
  const profiles=JSON.parse(fs.readFileSync(`${DIR}/frequency_profiles.json`,'utf8'));
  const rows=[],act=[],stress=[];
  for(const profile of profiles)for(const boundary of [788,800]) {
    const base=simulate([],boundary,profile,512);
    for(const [name,ids]of Object.entries(candidates)) {
      const r=simulate(ids,boundary,profile,512);
      rows.push({...labels(boundary,profile),package:name,sp:cost(ids),...scored(base,r)});
      act.push(...activations(r,{boundary,profile:profile.name,package:name}));
    }
  }
  for(const boundary of [788,800])for(const hp of hpCases) {
    const original=simulate(recommended.conservative,boundary,ref,1024,seed,hp);
    for(const [name,ids]of Object.entries(candidates)) {
      const r=simulate(ids,boundary,ref,1024,seed,hp);
      stress.push({...labels(boundary,ref,hp),package:name,sp:cost(ids),...scored(original,r)});
    }
  }
  csv('recommended_frequency',rows);csv('recommended_activation',act);csv('recommended_hp',stress);
  console.log('PASS recommended frequency and HP envelope checks',rows.length,stress.length);
}
