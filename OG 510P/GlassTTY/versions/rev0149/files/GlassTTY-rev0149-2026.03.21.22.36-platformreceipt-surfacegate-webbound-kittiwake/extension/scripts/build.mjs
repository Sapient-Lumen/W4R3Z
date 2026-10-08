import { rm, access } from 'node:fs/promises';
import { spawnSync } from 'node:child_process';

await rm(new URL('../dist/', import.meta.url), { recursive: true, force: true });

const result = spawnSync('tsc', ['-p', 'tsconfig.build.json'], {
  cwd: new URL('..', import.meta.url),
  stdio: 'inherit',
});

if (result.status !== 0) {
  process.exit(result.status ?? 1);
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
