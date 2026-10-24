import * as esbuild from 'esbuild';
import path from 'node:path';
const root = process.cwd();
await esbuild.build({
  entryPoints: ['cm21-study/followup-788/run.ts'],
  outfile: 'cm21-study/followup-788/run.cjs',
  bundle: true, platform: 'node',
  define: {CC_GLOBAL: 'true', CC_DEBUG: 'false'},
  plugins: [{name: 'global-data', setup(build) {
    build.onResolve({filter: /skill_meta.json$/}, () => ({path: path.join(root, 'umalator-global/skill_meta.json')}));
    build.onResolve({filter: /\/data\/.*\.json$/}, args => ({path: path.join(root, 'umalator-global', args.path.split('/data/')[1])}));
  }}]
});
