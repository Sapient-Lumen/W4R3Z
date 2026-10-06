#!/usr/bin/env node
import { availableParallelism, platform, arch, cpus, totalmem, freemem } from 'node:os';
import { mkdir, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import { detectCapabilities, availableCapabilityTierNames, REVISION, VERSION } from '../src/browserrt.mjs';

function argValue(argv, flag, fallback = null) {
  const i = argv.indexOf(flag);
  return i >= 0 ? argv[i + 1] : fallback;
}

const out = argValue(process.argv.slice(2), '--json');
const caps = detectCapabilities(globalThis);
const report = {
  project: 'BrowserRT',
  revision: REVISION,
  version: VERSION,
  schema: 1,
  status: 'passed',
  generatedAt: new Date().toISOString(),
  environment: {
    node: process.version,
    platform: platform(),
    arch: arch(),
    availableParallelism: availableParallelism?.() || null,
    cpuCount: cpus().length,
    totalmem: totalmem(),
    freemem: freemem()
  },
  capabilities: caps,
  availableTierNames: availableCapabilityTierNames(caps),
  nonClaims: [
    'No browser API support is proven by this Node-only survey.',
    'Cloudtainer CPU/memory values are planning hints, not performance claims.'
  ]
};

if (out) {
  await mkdir(dirname(out), { recursive: true });
  await writeFile(out, JSON.stringify(report, null, 2) + '\n');
  console.log(out);
} else {
  console.log(JSON.stringify(report, null, 2));
}
