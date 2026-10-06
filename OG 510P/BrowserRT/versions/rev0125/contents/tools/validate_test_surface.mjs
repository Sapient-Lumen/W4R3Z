#!/usr/bin/env node
import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import { REVISION, VERSION } from '../src/browserrt.mjs';
import { validateImpactMap, validateManifest, validateQuarantine, validateSurfaceInventory } from '../src/test-facility.mjs';

const args = new Set(process.argv.slice(2));
const out = `artifacts/validation/REV${REVISION.slice(3)}-TEST-SURFACE-REPORT.json`;
const manifest = JSON.parse(await readFile('test/manifest.json', 'utf8'));
const impact = JSON.parse(await readFile('test/impact-map.json', 'utf8'));
const inventory = JSON.parse(await readFile('test/surface-inventory.json', 'utf8'));
const quarantine = JSON.parse(await readFile('test/quarantine.json', 'utf8'));
const errors = [
  ...validateManifest(manifest, { currentRevision: REVISION }),
  ...validateImpactMap(impact, manifest, { currentRevision: REVISION }),
  ...validateSurfaceInventory(inventory, manifest, { currentRevision: REVISION }),
  ...validateQuarantine(quarantine, manifest, { currentRevision: REVISION })
];
const taskIds = new Set(manifest.tasks.map((task) => task.id));
const referenced = new Set();
for (const surface of inventory.surfaces) for (const id of surface.currentTaskIds || []) referenced.add(id);
const unreferencedReleaseTasks = manifest.tasks
  .filter((task) => task.tiers.includes('release') && !referenced.has(task.id))
  .map((task) => task.id);
const futureSurfaces = inventory.surfaces.filter((surface) => surface.phase === 'future').map((surface) => surface.id);
const report = {
  project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1,
  status: errors.length === 0 ? 'passed' : 'failed',
  generatedAt: new Date().toISOString(),
  taskCount: taskIds.size,
  surfaceCount: inventory.surfaces.length,
  impactRuleCount: impact.rules.length,
  quarantineCount: quarantine.entries.length,
  unreferencedReleaseTasks,
  futureSurfaces,
  errors
};
if (args.has('--write')) {
  await mkdir(dirname(out), { recursive: true });
  await writeFile(out, JSON.stringify(report, null, 2) + '\n');
  console.log(out);
} else {
  console.log(JSON.stringify(report, null, 2));
}
if (errors.length) process.exitCode = 1;
