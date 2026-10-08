import { rm } from 'node:fs/promises';
import { spawnSync } from 'node:child_process';

await rm(new URL('../dist/', import.meta.url), { recursive: true, force: true });

const result = spawnSync('tsc', ['-p', 'tsconfig.build.json'], {
  cwd: new URL('..', import.meta.url),
  stdio: 'inherit',
});

if (result.status !== 0) {
  process.exit(result.status ?? 1);
}
