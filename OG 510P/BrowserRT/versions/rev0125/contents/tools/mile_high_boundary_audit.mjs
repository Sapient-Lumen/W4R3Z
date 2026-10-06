#!/usr/bin/env node
import { readFile, writeFile, mkdir } from 'node:fs/promises';
import { dirname } from 'node:path';
import { REVISION, VERSION, createDreamBoundaryMap, validateDreamBoundaryMap } from '../src/browserrt.mjs';

const argv = process.argv.slice(2);
const argValue = (flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };
const PREFIX = `REV${REVISION.slice(3)}`;
const outPath = argValue('--json', `artifacts/audit/${PREFIX}-MILE-HIGH-BOUNDARY-AUDIT.json`);

async function readText(path) { return await readFile(path, 'utf8'); }
async function readJson(path) { return JSON.parse(await readText(path)); }
function check(name, passed, detail = {}) { return { name, status: passed ? 'passed' : 'failed', ...detail }; }
function includesAll(text, needles) { return needles.filter((needle) => !text.includes(needle)); }

const map = createDreamBoundaryMap();
const validation = validateDreamBoundaryMap(map);
const manifest = await readJson('test/manifest.json');
const impact = await readJson('test/impact-map.json');
const inventory = await readJson('test/surface-inventory.json');
const registry = await readJson('artifacts/research/RELATED-WORK-SOURCE-REGISTRY.json');
const receipt = await readJson('REVISION-RECEIPT.json');
const files = {
  mileHigh: await readText('docs/00-meta/mile-high-dream-rev0044.md'),
  frontier: await readText('docs/20-architecture/browserrt-moonshot-frontier.md'),
  shelf: await readText('docs/40-validation/cloudtainer-testability-and-shelf-ledger.md'),
  office: await readText('docs/00-meta/future-session-office-manual.md'),
  charter: await readText('docs/00-meta/non-claims-and-goals-charter.md'),
  dreambank: await readText('docs/20-architecture/runtime-dreambank-035.md'),
  research: await readText('docs/05-research/related-work-research-pass-035.md')
};
const docsText = Object.values(files).join('\n');
const tasks = new Map((manifest.tasks || []).map((task) => [task.id, task]));
const titles = new Set((registry.families || []).flatMap((family) => family.sources || []).map((source) => source.title));
const requiredTitles = [
  'workerd open source Workers runtime',
  'WebContainers browser runtime',
  'WebAssembly Component Model introduction',
  'WASI capabilities',
  'WebGPU API - MDN',
  'WebNN specification',
  'WebTransport API - MDN',
  'WebRTC API - MDN',
  'Cloudflare Durable Objects overview',
  'Ray actors and object refs'
];
const requiredNeedles = [
  'one runtime, many providers',
  'cloudtainer-buildable',
  'smoke-testable',
  'needs external evidence',
  'shelf until repeated container evidence',
  'No WebGPU performance claim.',
  'No WebNN/NPU claim.',
  'No real WebTransport or WebRTC WAN/NAT claim.',
  'No mobile/background-lifecycle claim.',
  'No production security sandbox claim.'
];
const manifestTask = tasks.get('facility:mile-high-boundary-audit');
const impactTaskIds = new Set((impact.rules || []).flatMap((rule) => rule.taskIds || []));
const inventoryTaskIds = new Set((inventory.surfaces || []).flatMap((surface) => surface.currentTaskIds || []));
const checks = [
  check('dream-boundary-map-valid', validation.ok, { errors: validation.errors }),
  check('manifest-task-present-release', Boolean(manifestTask) && manifestTask.tiers?.includes('release') && manifestTask.lane === 'main', { task: manifestTask || null }),
  check('impact-map-covers-task', impactTaskIds.has('facility:mile-high-boundary-audit')),
  check('surface-inventory-covers-task', inventoryTaskIds.has('facility:mile-high-boundary-audit')),
  check('research-sources-registered', requiredTitles.filter((title) => !titles.has(title)).length === 0, { missingTitles: requiredTitles.filter((title) => !titles.has(title)) }),
  check('docs-contain-boundary-language', includesAll(docsText, requiredNeedles).length === 0, { missingNeedles: includesAll(docsText, requiredNeedles) }),
  check('receipt-mile-high-carried-forward', receipt.revision === REVISION && (receipt.current_audit_slice === 'facility:mile-high-boundary-audit' || (receipt.carried_forward_audits || []).includes('facility:mile-high-boundary-audit')), { currentAudit: receipt.current_audit_slice, carriedForwardAudits: receipt.carried_forward_audits || [], receiptRevision: receipt.revision }),
  check('unshelf-policy-legible', files.shelf.includes('three successful sessions') && files.shelf.includes('external-device evidence') && files.shelf.includes('do not promote'))
];
const failed = checks.filter((row) => row.status !== 'passed');
const report = {
  project: 'BrowserRT',
  revision: REVISION,
  version: VERSION,
  schema: 1,
  status: failed.length ? 'failed' : 'passed',
  generatedAt: new Date().toISOString(),
  purpose: 'Audit rev0044 mile-high dream, cloudtainer testability boundary, source registry, manifest, impact, surface inventory, and non-claim legibility.',
  dreamBoundary: map,
  checks,
  nonClaims: [
    'This audit does not prove any new runtime provider behavior.',
    'This audit does not prove WebGPU/WebNN/WebTransport/WebRTC, mobile, cross-browser, production security, durability, or performance behavior.',
    'This audit only keeps the dream boundary legible for future sessions.'
  ]
};
await mkdir(dirname(outPath), { recursive: true });
await writeFile(outPath, JSON.stringify(report, null, 2) + '\n');
console.log(outPath);
if (report.status !== 'passed') process.exitCode = 1;
