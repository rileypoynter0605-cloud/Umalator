import * as esbuild from 'esbuild';
import path from 'node:path';
const root=process.cwd();
await esbuild.build({entryPoints:['cm21-study/research/'+(process.argv[2]||'run')+'.ts'],outfile:'cm21-study/research/'+(process.argv[2]||'run')+'.cjs',bundle:true,platform:'node',define:{CC_GLOBAL:'true',CC_DEBUG:'false'},plugins:[{name:'global-data',setup(b){b.onResolve({filter:/skill_meta.json$/},a=>({path:path.join(root,'umalator-global/skill_meta.json')}));b.onResolve({filter:/\/data\/.*\.json$/},a=>({path:path.join(root,'umalator-global',a.path.split('/data/')[1])}));}}]});
