import { access, readFile, rm } from 'node:fs/promises';
import { spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';

import { build } from 'esbuild';

const extensionRoot = fileURLToPath(new URL('../', import.meta.url));
const distUrl = new URL('../dist/', import.meta.url);
const packageMetadata = JSON.parse(await readFile(new URL('../package.json', import.meta.url), 'utf8'));
const manifestMetadata = JSON.parse(await readFile(new URL('../manifest.json', import.meta.url), 'utf8'));
const buildVersion = packageMetadata.version;

if (typeof buildVersion !== 'string' || manifestMetadata.version !== buildVersion) {
  throw new Error('package.json and manifest.json must declare the same extension version');
}

await rm(distUrl, { recursive: true, force: true });

const typecheck = spawnSync('tsc', ['--noEmit', '-p', 'tsconfig.json'], {
  cwd: extensionRoot,
  stdio: 'inherit',
});

if (typecheck.status !== 0) {
  process.exit(typecheck.status ?? 1);
}

const entryPoints = [
  'src/background/main.ts',
  'src/content/main.ts',
  'src/sidepanel/main.ts',
  'src/options/main.ts',
  'src/probe/main.ts',
  'src/offscreen/main.ts',
];

const result = await build({
  absWorkingDir: extensionRoot,
  entryPoints,
  outbase: 'src',
  outdir: 'dist',
  entryNames: '[dir]/[name]',
  bundle: true,
  format: 'iife',
  platform: 'browser',
  target: 'chrome120',
  define: {
    __GLASSTTY_BUNDLE_VERSION__: JSON.stringify(buildVersion),
  },
  legalComments: 'none',
  logLevel: 'info',
  metafile: true,
  sourcemap: false,
});

const residualImports = Object.entries(result.metafile.outputs)
  .flatMap(([output, metadata]) => metadata.imports.map((dependency) => `${output} -> ${dependency.path}`));
if (residualImports.length > 0) {
  throw new Error(`browser bundles retain unresolved imports:\n${residualImports.join('\n')}`);
}

const requiredFiles = [
  '../manifest.json',
  '../sidepanel/index.html',
  '../options/index.html',
  '../probe/index.html',
  '../offscreen/index.html',
  '../dist/background/main.js',
  '../dist/content/main.js',
  '../dist/sidepanel/main.js',
  '../dist/options/main.js',
  '../dist/probe/main.js',
  '../dist/offscreen/main.js',
];

for (const relative of requiredFiles) {
  await access(new URL(relative, import.meta.url));
}
