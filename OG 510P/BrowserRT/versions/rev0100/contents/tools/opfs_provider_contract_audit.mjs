#!/usr/bin/env node
import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import { REVISION, VERSION } from '../src/browserrt.mjs';
import { readTextWithRevisionFallback } from './revision_doc_fallback.mjs';

const PREFIX = `REV${REVISION.slice(3)}`;
const DEFAULT_OUT = `artifacts/audit/${PREFIX}-OPFS-PROVIDER-CONTRACT-AUDIT.json`;
const argv = process.argv.slice(2);
const argValue = (flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };
async function readText(path) { return await readTextWithRevisionFallback(path); }
async function readJson(path) { return JSON.parse(await readText(path)); }
function check(name, passed, detail = {}) { return { name, status: passed ? 'passed' : 'failed', ...detail }; }
function includesAll(text, needles) { return needles.filter((n) => !text.includes(n)); }

const out = argValue('--json', DEFAULT_OUT);
const manifest = await readJson('test/manifest.json');
const inventory = await readJson('test/surface-inventory.json');
const registry = await readJson('artifacts/research/RELATED-WORK-SOURCE-REGISTRY.json');
const receipt = await readJson('REVISION-RECEIPT.json');
const source = await readText('src/opfs-block-store.mjs');
const runtime = await readText('src/browserrt.mjs');
const types = await readText('src/types.d.ts');
const probe = await readText('tools/browser_opfs_block_store_probe.mjs');
const frontier = await readText('docs/20-architecture/opfs-block-store-frontier.md');
const sliceDoc = await readText('docs/40-validation/browser-opfs-block-store-slice.md');
const charter = await readText('docs/00-meta/non-claims-and-goals-charter.md');

const tasks = new Map((manifest.tasks || []).map((task) => [task.id, task]));
const browserTask = tasks.get('browser:opfs-block-store-proof');
const auditTask = tasks.get('facility:opfs-provider-contract-audit');
let artifact = null;
try { artifact = await readJson(`artifacts/validation/${PREFIX}-BROWSER-OPFS-BLOCK-STORE-PROBE.json`); } catch {}
const titles = new Set((registry.families || []).flatMap((family) => family.sources || []).map((source) => source.title));
const taskIdsFromInventory = new Set((inventory.surfaces || []).flatMap((surface) => surface.currentTaskIds || []));
const nonClaimNeedles = [
  'No OPFS durability, fsync, quota, eviction, crash-recovery, or browser restart claim.',
  'No OPFS storage-lane durability proof.',
  'No OPFS sync access handle storage-lane proof.',
  'No OPFS multi-tab coordination proof.',
  'No OPFS performance claim.'
];
const checks = [
  check('revision-alignment', [manifest.revision, inventory.revision, registry.revision, receipt.revision].every((rev) => rev === REVISION), { revision: REVISION }),
  check('source-provider-surface', includesAll(source, ['OpfsAsyncBlockStore','createOpfsAsyncBlockStore','storage:opfs-block-put','storage:opfs-block-delete','BRT_OPFS_UNAVAILABLE']).length === 0),
  check('runtime-export-surface', includesAll(runtime, ['OpfsAsyncBlockStore','createOpfsAsyncBlockStore','opfsAsyncBlockStoreProof','object:opfs-async-block-store-ref']).length === 0),
  check('type-surface', includesAll(types, ['OpfsAsyncBlockStore','createOpfsAsyncBlockStore','cleanupForTest']).length === 0),
  check('browser-probe-surface', includesAll(probe, ['Page.reload','duplicate','cleanupForTest','Not an OPFS sync access handle']).length === 0),
  check('manifest-browser-task-present', Boolean(browserTask) && browserTask.lane === 'browser' && browserTask.tiers.includes('browser') && !browserTask.tiers.includes('release') && browserTask.parallelGroup === 'browser-process', { browserTask }),
  check('manifest-audit-task-present', Boolean(auditTask) && auditTask.tiers.includes('release') && auditTask.lane !== 'browser', { auditTask }),
  check('inventory-covers-opfs-provider', taskIdsFromInventory.has('browser:opfs-block-store-proof') && taskIdsFromInventory.has('facility:opfs-provider-contract-audit')),
  check('research-registered', ['Origin private file system - MDN', 'FileSystemFileHandle createSyncAccessHandle - MDN', 'SQLite Wasm OPFS persistence options', 'Storage quotas and eviction criteria - MDN'].every((title) => titles.has(title))),
  check('docs-explain-boundary', includesAll(frontier + sliceDoc, ['async OPFS content-addressed block-store', 'not a durability claim', 'page-reload readback', 'storage-lane provider integration']).length === 0),
  check('non-claims-legible', nonClaimNeedles.every((needle) => (JSON.stringify(receipt) + charter).includes(needle)), { nonClaimNeedles }),
  check('proof-artifact-current-if-present', !artifact || (artifact.revision === REVISION && artifact.status === 'passed' && artifact.observations?.read?.hasBefore?.a === true), { artifactPresent: Boolean(artifact), artifactStatus: artifact?.status ?? null })
];
const failed = checks.filter((row) => row.status !== 'passed');
const report = {
  project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1,
  status: failed.length ? 'failed' : 'passed', generatedAt: new Date().toISOString(),
  purpose: 'Contract audit for the async OPFS content-addressed block-store provider slice: source/export/type wiring, browser-task isolation, research registration, docs, artifact presence, and non-claim legibility.',
  checks,
  nonClaims: [
    'This audit does not run Chromium and does not prove OPFS behavior by itself.',
    'This audit checks the slice contract and optional current proof artifact only.',
    'No durability, quota, eviction, crash-recovery, multi-tab, performance, or cross-browser claim.'
  ]
};
await mkdir(dirname(out), { recursive: true });
await writeFile(out, JSON.stringify(report, null, 2) + '\n');
console.log(out);
if (report.status !== 'passed') process.exitCode = 1;
