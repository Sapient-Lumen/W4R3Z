#!/usr/bin/env node
import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import { REVISION } from '../src/browserrt.mjs';
import { estimatePlan, explainImpact, impactedTaskIds, matchesGlob, parseShard, selectTasks, stableHash32, validateImpactMap, validateManifest, validateQuarantine, validateSurfaceInventory } from '../src/test-facility.mjs';

const manifest = JSON.parse(await readFile(new URL('./manifest.json', import.meta.url), 'utf8'));
const impactMap = JSON.parse(await readFile(new URL('./impact-map.json', import.meta.url), 'utf8'));
const surfaceInventory = JSON.parse(await readFile(new URL('./surface-inventory.json', import.meta.url), 'utf8'));
const quarantine = JSON.parse(await readFile(new URL('./quarantine.json', import.meta.url), 'utf8'));
assert.deepEqual(validateManifest(manifest, { currentRevision: REVISION }), []);
assert.deepEqual(validateImpactMap(impactMap, manifest, { currentRevision: REVISION }), []);
assert.deepEqual(validateSurfaceInventory(surfaceInventory, manifest, { currentRevision: REVISION }), []);
assert.deepEqual(validateQuarantine(quarantine, manifest, { currentRevision: REVISION }), []);

const smoke = selectTasks(manifest, { tier: 'smoke' });
const release = selectTasks(manifest, { tier: 'release' });
const full = selectTasks(manifest, { tier: 'full' });
assert.ok(smoke.length >= 3, 'smoke tier should contain facility checks');
assert.ok(release.length >= smoke.length, 'release should be no smaller than smoke');
assert.ok(!release.some((task) => task.id === 'cube:check'), 'release harness should avoid cube-check artifact cycles');
assert.ok(full.length >= release.length, 'full should be no smaller than release');
assert.ok(release.some((task) => task.id === 'runtime:smoke'));
assert.ok(release.some((task) => task.id === 'proof:phase-zero-agent-supervisor'));
assert.ok(release.every((task) => task.size && task.isolation && task.capabilities?.length));

const shard = parseShard('1/2');
assert.equal(shard.index, 1);
assert.equal(shard.total, 2);
const shardA = selectTasks(manifest, { tier: 'release', shard: '1/2' });
const shardB = selectTasks(manifest, { tier: 'release', shard: '2/2' });
const union = new Set([...shardA, ...shardB].map((task) => task.id));
assert.equal(union.size, release.length, 'two shards should cover the release tier');
assert.notEqual(stableHash32('cube:check'), stableHash32('runtime:smoke'));

assert.equal(matchesGlob('src/browserrt.mjs', 'src/**'), true);
assert.equal(matchesGlob('docs/40-validation/x.md', 'docs/**'), true);
assert.equal(matchesGlob('README.md', '*.json'), false);
const impactIds = impactedTaskIds(impactMap, ['src/browserrt.mjs']);
assert.ok(impactIds.includes('runtime:smoke'));
assert.ok(impactIds.includes('proof:phase-zero-agent-supervisor'));
const impact = explainImpact(impactMap, ['src/browserrt.mjs', 'docs/40-validation/test.md']);
assert.ok(impact.matchedRuleCount >= 2);

const plan = estimatePlan(release);
assert.equal(plan.taskCount, release.length);
assert.ok(plan.estimatedMs > 0);
assert.ok(plan.lanes.main >= 1);
assert.ok(plan.sizes.tiny >= 1);
console.log('BrowserRT test harness selftest passed');
