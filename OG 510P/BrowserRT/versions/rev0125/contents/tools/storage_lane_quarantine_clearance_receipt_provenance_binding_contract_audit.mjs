#!/usr/bin/env node
import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import { REVISION, VERSION } from '../src/browserrt.mjs';

const argv = process.argv.slice(2);
const argValue = (flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };
const PFX = `REV${REVISION.slice(3)}`;
const outPath = argValue('--json', `artifacts/audit/${PFX}-STORAGE-LANE-QUARANTINE-CLEARANCE-RECEIPT-PROVENANCE-BINDING-CONTRACT-AUDIT.json`);
const CURRENT = 'browser:opfs-web-lock-quarantine-clearance-receipt-provenance-binding-proof';
const RELEASE = 'scheduler:storage-lane-quarantine-clearance-receipt-provenance-binding-proof';
const AUDIT = 'facility:storage-lane-quarantine-clearance-receipt-provenance-binding-contract-audit';
const SURFACES = ['surface:storage-lane-quarantine-clearance-receipt-provenance-binding','surface:browser-opfs-web-lock-quarantine-clearance-receipt-provenance-binding','surface:storage-lane-quarantine-clearance-receipt-provenance-binding-contract-audit'];
async function text(path) { return await readFile(path, 'utf8'); }
async function json(path) { return JSON.parse(await text(path)); }
function miss(body, needles) { return needles.filter((needle) => !String(body).includes(needle)); }
function check(name, ok, detail = {}) { return { name, status: ok ? 'passed' : 'failed', ...detail }; }
const files = {
  scheduler: await text('src/storage-lane-scheduler.mjs'),
  adapter: await text('src/block-store-lane-adapter.mjs'),
  browserrt: await text('src/browserrt.mjs'),
  types: await text('src/types.d.ts'),
  releaseProof: await text('tools/storage_lane_quarantine_clearance_receipt_provenance_binding_probe.mjs'),
  browserProof: await text('tools/browser_opfs_web_lock_quarantine_clearance_receipt_provenance_binding_probe.mjs'),
  storageDoc: await text('docs/40-validation/storage-lane-quarantine-clearance-receipt-provenance-binding-slice.md'),
  browserDoc: await text('docs/40-validation/browser-opfs-web-lock-quarantine-clearance-receipt-provenance-binding-slice.md'),
  auditDoc: await text('docs/40-validation/storage-lane-quarantine-clearance-receipt-provenance-binding-contract-audit-slice.md'),
  readme: await text('README.md'), start: await text('START_HERE.md'), agents: await text('AGENTS.md'), context: await text('CONTEXT-PACK.md'),
  package: await text('package.json'), makefile: await text('Makefile'), changelog: await text('CHANGELOG.md')
};
const manifest = await json('test/manifest.json');
const impact = await json('test/impact-map.json');
const inventory = await json('test/surface-inventory.json');
const taskIds = new Set((manifest.tasks || []).map((task) => task.id));
const impactIds = new Set((impact.rules || []).flatMap((rule) => rule.taskIds || rule.run || []));
const surfaceIds = new Set((inventory.surfaces || []).map((surface) => surface.id));
const runtime = files.scheduler + files.adapter;
const checks = [
  check('runtime-registration-provenance-validation', miss(runtime, ['validateTimedOutOperationQuarantineClearanceReceiptForRegistration','validateTimedOutOperationQuarantineClearanceReceiptRegistrationProvenance','quarantineClearanceReceiptProvenanceRejected','timed-out-quarantine-clearance-receipt-provenance-rejected','rejected-clearance-receipt-provenance','blockVerified','blockVerifyDigest','blockVerifyBytes']).length === 0),
  check('public-validation-tightened', miss(files.adapter + files.browserrt + files.types, ['validateTimedOutOperationQuarantineClearanceReceipt','timedOutOperationQuarantineClearanceReceiptFingerprint','opIds must match cleared row opIds','preClearanceFingerprint must match reviewFingerprint']).length === 0),
  check('proofs', miss(files.releaseProof + files.browserProof, [RELEASE,CURRENT,'bareValidDirectRegister','mismatchedProvenanceRegister','validDirectRegister','rejected-clearance-receipt-provenance','rejected-cleared-quarantine-replay','missingBlockVerifyRegister','mismatchedBlockVerifyDigestRegister','mismatchedBlockVerifyBytesRegister','validRestoreProvenanceRegister']).length === 0),
  check('docs', miss(files.storageDoc + files.browserDoc + files.auditDoc, ['clearance receipt','registration provenance','blockVerified','blockVerifyDigest','fail closed','Managed Chromium','not provider cancellation','cross-browser']).length === 0),
  check('manifest', [RELEASE,AUDIT,CURRENT].every((id) => taskIds.has(id))),
  check('impact-map', [RELEASE,AUDIT,CURRENT].every((id) => impactIds.has(id))),
  check('surface-inventory', SURFACES.every((id) => surfaceIds.has(id))),
  check('first-read-docs', miss(files.readme + files.start + files.agents + files.context, [CURRENT,AUDIT,'registration provenance','bound provenance','blockVerified','browser-light']).length === 0),
  check('manifest-command-wiring', miss(JSON.stringify(manifest), ['storage_lane_quarantine_clearance_receipt_provenance_binding_probe.mjs','browser_opfs_web_lock_quarantine_clearance_receipt_provenance_binding_probe.mjs','storage_lane_quarantine_clearance_receipt_provenance_binding_contract_audit.mjs']).length === 0),
  check('changelog', files.changelog.startsWith(`## ${REVISION} —`) && miss(files.changelog, [CURRENT,AUDIT,'registration provenance','blockVerified','rejected-clearance-receipt-provenance']).length === 0)
];
const failed = checks.filter((row) => row.status !== 'passed');
const report = { project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1, task_id: AUDIT, status: failed.length ? 'failed' : 'passed', generatedAt: new Date().toISOString(), purpose: 'facility:storage-lane-quarantine-clearance-receipt-provenance-binding-contract-audit keeps direct clearance-receipt registration validation wired to runtime, proofs, docs, and cube surfaces.', checks, nonClaims: ['Audit only; does not launch Chromium.', 'No cancellation, rollback, no-mutation-on-timeout, OPFS durability, cross-browser behavior, quota/eviction survival, or production readiness claim.', 'Receipt fingerprints are deterministic integrity/review binding, not cryptographic attestation or tamper-proof storage.'] };
await mkdir(dirname(outPath), { recursive: true });
await writeFile(outPath, JSON.stringify(report, null, 2) + '\n');
console.log(outPath);
if (report.status !== 'passed') process.exitCode = 1;
