import fs from 'node:fs';
import {runComparison} from '../../umalator/compare';
import {HorseState,SkillSet} from '../../components/HorseDefTypes';
import {CourseHelpers} from '../../uma-skill-tools/CourseData';
const packages=JSON.parse(fs.readFileSync('cm21-study/research/packages.json','utf8'));
const base={speed:1515,stamina:402,power:1003,guts:695,wisdom:976,strategy:'Nige',distanceAptitude:'S',surfaceAptitude:'S',strategyAptitude:'A',mood:0,uniqueLevel:4};
const results=[];
for(const mode of ['solo-comparison','virtual-front','virtual-pace','virtual-elite-front'])for(const name of ['prior_balanced','prior_top_runner','candidate_1','conservative']){
 if(!packages[name])continue;
 const a=new HorseState({...base,skills:SkillSet(['100411'])});
 const b=new HorseState({...base,skills:SkillSet(['100411',...packages[name]])});
 const pacer=mode==='solo-comparison'?null:new HorseState({...base,speed:mode==='virtual-elite-front'?1590:1525,power:mode==='virtual-elite-front'?1260:1150,wisdom:mode==='virtual-elite-front'?1240:1130,strategy:mode==='virtual-pace'?'Senkou':'Nige',skills:SkillSet(['200202','200152','201522','201601','200532','200651','201271','900141'])});
 const r=runComparison(256,CourseHelpers.getCourse(10701),{groundCondition:1,weather:1,season:4,time:2,grade:100,mood:0,popularity:1,orderRange:[1,2],numUmas:9} as any,a,b,pacer,{seed:2120226,mode:'compare',posKeepMode:mode==='solo-comparison'?0:2,pacemakerCount:pacer?1:0,hpConsumption:true,skillWisdomCheck:true,rushedKakari:true,competeFight:false,leadCompetition:false,syncRng:true});
 const vals=r.results;const mean=vals.reduce((a,b)=>a+b,0)/vals.length;const se=Math.sqrt(vals.reduce((a,b)=>a+(b-mean)**2,0)/(vals.length-1)/vals.length);
 results.push({mode,package:name,trials:256,mean_engine_margin:mean,ci95_low:mean-1.96*se,ci95_high:mean+1.96*se,stamina:r.staminaStats,activation:r.skillActivationStats,first:r.firstUmaStats});
}
fs.writeFileSync('cm21-study/research/native_pairwise.json',JSON.stringify(results,null,2));console.log(results.map(({stamina,activation,first,...r})=>r));
