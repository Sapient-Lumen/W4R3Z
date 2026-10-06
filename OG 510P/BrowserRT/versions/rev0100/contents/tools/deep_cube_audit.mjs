#!/usr/bin/env node
import { access, mkdir, readdir, readFile, writeFile } from 'node:fs/promises';
import { createHash } from 'node:crypto';
import { dirname, relative } from 'node:path';
import { REVISION, VERSION } from '../src/browserrt.mjs';

const argv = process.argv.slice(2);
const argValue = (flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };
const CURRENT_PREFIX = `REV${REVISION.slice(3)}`;
const PREVIOUS_REV = `rev${String(Number(REVISION.slice(3)) - 1).padStart(4, '0')}`;
const PREVIOUS_PREFIX = `REV${PREVIOUS_REV.slice(3)}`;
const outPath = argValue('--json', `artifacts/audit/${CURRENT_PREFIX}-DEEP-CUBE-AUDIT.json`);

const EXPECTED = Object.freeze({
  revision: REVISION,
  version: VERSION,
  previous_revision: PREVIOUS_REV,
  codename: 'OPFS Block Store Rollback Valid Block Preserve',
  package_slug: 'opfs-block-store-rollback-valid-block-preserve-current-proof',
  current_task: 'browser:opfs-block-store-rollback-valid-block-preserve-proof',
  current_slice: 'browser:opfs-block-store-rollback-valid-block-preserve-proof',
  current_runtime_slice: 'browser:opfs-block-store-rollback-valid-block-preserve-proof',
  current_audit: 'facility:opfs-block-store-rollback-valid-block-preserve-contract-audit',
  current_audit_slice: 'facility:opfs-block-store-rollback-valid-block-preserve-contract-audit'
});

const RELEASE_TASK = 'opfs:block-store-rollback-valid-block-preserve-proof';
const BROWSER_TASK = EXPECTED.current_task;
const AUDIT_TASK = EXPECTED.current_audit;

const CORE_NONCLAIMS = Object.freeze(['cross-browser', 'quota', 'eviction', 'crash', 'browser-light']);

const REQUIRED_TASKS = [
  'scheduler:storage-lane-quarantine-clearance-receipt-lane-binding-proof',
  'facility:storage-lane-quarantine-clearance-receipt-lane-binding-contract-audit',
  'browser:opfs-web-lock-quarantine-clearance-receipt-lane-binding-proof',
  'scheduler:storage-lane-quarantine-lane-filter-import-guard-proof',
  'facility:storage-lane-quarantine-lane-filter-import-guard-contract-audit',
  'browser:opfs-web-lock-quarantine-lane-filter-import-guard-proof',
  'scheduler:storage-lane-quarantine-clearance-lanewide-scope-proof',
  'facility:storage-lane-quarantine-clearance-lanewide-scope-contract-audit',
  'browser:opfs-web-lock-quarantine-clearance-lanewide-scope-proof',
  'scheduler:storage-lane-quarantine-clearance-restore-registration-gate-proof',
  'facility:storage-lane-quarantine-clearance-restore-registration-gate-contract-audit',
  'browser:opfs-web-lock-quarantine-clearance-restore-registration-gate-proof',
  'scheduler:storage-lane-quarantine-receipt-restore-integrity-proof',
  'scheduler:storage-lane-quarantine-status-transition-import-proof',
  'facility:storage-lane-quarantine-status-transition-import-contract-audit',
  'browser:opfs-web-lock-quarantine-status-transition-import-proof',
  'scheduler:storage-lane-quarantine-clearance-replay-key-receipt-integrity-proof',
  'facility:storage-lane-quarantine-clearance-replay-key-receipt-integrity-contract-audit',
  'browser:opfs-web-lock-quarantine-clearance-replay-key-receipt-integrity-proof',
  'scheduler:storage-lane-quarantine-review-replay-key-scope-proof',
  'facility:storage-lane-quarantine-review-replay-key-scope-contract-audit',
  'browser:opfs-web-lock-quarantine-review-replay-key-scope-proof',
  'scheduler:storage-lane-quarantine-clearance-row-replay-guard-proof',
  'facility:storage-lane-quarantine-clearance-row-replay-guard-contract-audit',
  'browser:opfs-web-lock-quarantine-clearance-row-replay-guard-proof',
  'scheduler:storage-lane-unsettled-orphan-review-proof',
  'facility:storage-lane-unsettled-orphan-review-contract-audit',
  'browser:opfs-web-lock-unsettled-orphan-review-proof',
  'scheduler:storage-lane-quarantine-clearance-replay-guard-proof',
  'facility:storage-lane-quarantine-clearance-replay-guard-contract-audit',
  'browser:opfs-web-lock-quarantine-clearance-replay-guard-proof',
  'scheduler:storage-lane-quarantine-clearance-receipt-lane-binding-proof',
  'facility:storage-lane-quarantine-clearance-receipt-lane-binding-contract-audit',
  'browser:opfs-web-lock-quarantine-clearance-receipt-lane-binding-proof',
  'scheduler:storage-lane-quarantine-clearance-receipt-registration-integrity-proof',
  'facility:storage-lane-quarantine-clearance-receipt-registration-integrity-contract-audit',
  'browser:opfs-web-lock-quarantine-clearance-receipt-registration-integrity-proof',
  'scheduler:storage-lane-unsettled-orphan-review-proof',
  'facility:storage-lane-unsettled-orphan-review-contract-audit',
  'browser:opfs-web-lock-unsettled-orphan-review-proof',
  'scheduler:storage-lane-quarantine-review-binding-proof',
  'scheduler:storage-lane-quarantine-ledger-persistence-integrity-proof',
  'facility:storage-lane-quarantine-review-binding-contract-audit',
  'browser:opfs-web-lock-quarantine-review-binding-proof',
  'scheduler:storage-lane-quarantine-ledger-persistence-integrity-proof',
  'facility:storage-lane-quarantine-review-binding-contract-audit',
  'browser:opfs-web-lock-quarantine-review-binding-proof',
  'scheduler:storage-lane-quarantine-ledger-roundtrip-proof',
  'facility:storage-lane-quarantine-review-binding-contract-audit',
  'browser:opfs-web-lock-quarantine-review-binding-proof',
  'scheduler:storage-lane-operation-context-propagation-proof',
  'facility:operation-context-propagation-contract-audit',
  'browser:opfs-web-lock-operation-context-propagation-proof',
  'scheduler:storage-lane-late-failure-quarantine-proof',
  'facility:storage-lane-late-failure-quarantine-contract-audit',
  'browser:opfs-web-lock-late-failure-quarantine-proof',
  'scheduler:storage-lane-late-settlement-recovery-gate-proof',
  'facility:storage-lane-late-settlement-contract-audit',
  'browser:opfs-web-lock-late-settlement-recovery-gate-proof',
  'scheduler:storage-lane-operation-timeout-proof',
  'facility:storage-lane-operation-timeout-contract-audit',
  'browser:opfs-web-lock-operation-timeout-boundary-proof',
  'scheduler:storage-lane-web-lock-read-timeout-nonpoison-proof',
  'facility:web-lock-read-timeout-nonpoison-contract-audit',
  'browser:opfs-web-lock-read-timeout-nonpoison-proof',
  'browser:opfs-web-lock-service-worker-fetch-lifecycle-proof',
  'facility:service-worker-fetch-lifecycle-contract-audit',
  'browser:opfs-web-lock-service-worker-update-race-proof',
  'facility:service-worker-update-race-contract-audit',
  'browser:opfs-web-lock-service-worker-shutdown-boundary-proof',
  'facility:service-worker-shutdown-boundary-contract-audit',
  'browser:opfs-web-lock-service-worker-restart-update-proof',
  'facility:service-worker-restart-update-contract-audit',
  'browser:opfs-web-lock-service-worker-lifecycle-proof',
  'facility:service-worker-lifecycle-contract-audit',
  'browser:opfs-web-lock-settled-recovery-proof',
  'scheduler:storage-lane-web-lock-settled-recovery-proof',
  'facility:web-lock-settled-recovery-contract-audit',
  'browser:opfs-web-lock-tab-timeout-proof',
  'scheduler:storage-lane-web-lock-timeout-health-proof',
  'facility:branch-continuity-audit',
  'facility:web-lock-lifecycle-contract-audit',
  'coord:web-lock-timeout-proof',
  'browser:opfs-web-lock-timeout-proof',
  'opfs:block-store-corrupt-block-repair-proof',
  'browser:opfs-corrupt-block-repair-proof',
  'browser:opfs-web-lock-guarded-contention-proof',
  'coord:web-lock-strict-option-guard-proof',
  'facility:web-lock-strict-option-guard-contract-audit',
  'browser:opfs-web-lock-strict-option-guard-proof',
  'opfs:block-store-abort-signal-proof',
  'facility:opfs-block-store-abort-signal-contract-audit',
  'browser:opfs-block-store-abort-signal-proof',
  'opfs:block-store-write-budget-guard-proof',
  'facility:opfs-block-store-write-budget-guard-contract-audit',
  'browser:opfs-block-store-write-budget-guard-proof',
  'opfs:block-store-owned-rollback-guard-proof',
  'facility:opfs-block-store-owned-rollback-guard-contract-audit',
  'browser:opfs-block-store-owned-rollback-guard-proof',
  'opfs:block-store-open-failure-recovery-proof',
  'facility:opfs-block-store-open-failure-recovery-contract-audit',
  'browser:opfs-block-store-open-failure-recovery-proof',
  'opfs:block-store-write-budget-duplicate-bypass-proof',
  'facility:opfs-block-store-write-budget-duplicate-bypass-contract-audit',
  'browser:opfs-block-store-write-budget-duplicate-bypass-proof',
  'opfs:block-store-rollback-valid-block-preserve-proof',
  'facility:opfs-block-store-rollback-valid-block-preserve-contract-audit',
  'browser:opfs-block-store-rollback-valid-block-preserve-proof',
  'cube:deep-audit',
  'cube:artifact-budget-audit',
  'facility:foundation-audit'
];
const BROWSER_HEAVY = REQUIRED_TASKS.filter((id) => id.startsWith('browser:'));
const PLAN_FILES = [
  'src/storage-lane-scheduler.mjs',
  'src/block-store-lane-adapter.mjs',
  'src/browserrt.mjs',
  'src/types.d.ts',
  'tools/storage_lane_quarantine_restore_expected_fingerprint_probe.mjs',
  'tools/browser_opfs_web_lock_quarantine_restore_expected_fingerprint_probe.mjs',
  'tools/storage_lane_quarantine_restore_expected_fingerprint_contract_audit.mjs',
  'docs/40-validation/storage-lane-quarantine-restore-expected-fingerprint-slice.md',
  'docs/40-validation/browser-opfs-web-lock-quarantine-restore-expected-fingerprint-slice.md',
  'docs/40-validation/storage-lane-quarantine-restore-expected-fingerprint-contract-audit-slice.md',
  'src/web-lock-coordinator.mjs',
  'src/opfs-web-lock-guarded-block-store.mjs',
  'tools/web_lock_strict_option_guard_probe.mjs',
  'tools/browser_opfs_web_lock_strict_option_guard_probe.mjs',
  'tools/web_lock_strict_option_guard_contract_audit.mjs',
  'docs/40-validation/web-lock-strict-option-guard-slice.md',
  'docs/40-validation/browser-opfs-web-lock-strict-option-guard-slice.md',
  'docs/40-validation/web-lock-strict-option-guard-contract-audit-slice.md',
  'src/opfs-block-store.mjs',
  'tools/lib/fake_opfs_harness.mjs',
  'tools/opfs_block_store_abort_signal_probe.mjs',
  'tools/browser_opfs_block_store_abort_signal_probe.mjs',
  'tools/opfs_block_store_abort_signal_contract_audit.mjs',
  'docs/40-validation/opfs-block-store-abort-signal-slice.md',
  'docs/40-validation/browser-opfs-block-store-abort-signal-slice.md',
  'docs/40-validation/opfs-block-store-abort-signal-contract-audit-slice.md',
  'tools/opfs_block_store_write_budget_guard_probe.mjs',
  'tools/browser_opfs_block_store_write_budget_guard_probe.mjs',
  'tools/opfs_block_store_write_budget_guard_contract_audit.mjs',
  'docs/40-validation/opfs-block-store-write-budget-guard-slice.md',
  'docs/40-validation/browser-opfs-block-store-write-budget-guard-slice.md',
  'docs/40-validation/opfs-block-store-write-budget-guard-contract-audit-slice.md',
  'tools/opfs_block_store_owned_rollback_guard_probe.mjs',
  'tools/browser_opfs_block_store_owned_rollback_guard_probe.mjs',
  'tools/opfs_block_store_owned_rollback_guard_contract_audit.mjs',
  'docs/40-validation/opfs-block-store-owned-rollback-guard-slice.md',
  'docs/40-validation/browser-opfs-block-store-owned-rollback-guard-slice.md',
  'docs/40-validation/opfs-block-store-owned-rollback-guard-contract-audit-slice.md',
  'tools/opfs_block_store_open_failure_recovery_probe.mjs',
  'tools/browser_opfs_block_store_open_failure_recovery_probe.mjs',
  'tools/opfs_block_store_open_failure_recovery_contract_audit.mjs',
  'docs/40-validation/opfs-block-store-open-failure-recovery-slice.md',
  'docs/40-validation/browser-opfs-block-store-open-failure-recovery-slice.md',
  'docs/40-validation/opfs-block-store-open-failure-recovery-contract-audit-slice.md',
  'tools/opfs_block_store_write_budget_duplicate_bypass_probe.mjs',
  'tools/browser_opfs_block_store_write_budget_duplicate_bypass_probe.mjs',
  'tools/opfs_block_store_write_budget_duplicate_bypass_contract_audit.mjs',
  'docs/40-validation/opfs-block-store-write-budget-duplicate-bypass-slice.md',
  'docs/40-validation/browser-opfs-block-store-write-budget-duplicate-bypass-slice.md',
  'docs/40-validation/opfs-block-store-write-budget-duplicate-bypass-contract-audit-slice.md',
  'tools/opfs_block_store_rollback_valid_block_preserve_probe.mjs',
  'tools/browser_opfs_block_store_rollback_valid_block_preserve_probe.mjs',
  'tools/opfs_block_store_rollback_valid_block_preserve_contract_audit.mjs',
  'docs/40-validation/opfs-block-store-rollback-valid-block-preserve-slice.md',
  'docs/40-validation/browser-opfs-block-store-rollback-valid-block-preserve-slice.md',
  'docs/40-validation/opfs-block-store-rollback-valid-block-preserve-contract-audit-slice.md',
  'test/manifest.json',
  'test/impact-map.json',
  'test/surface-inventory.json',
  'README.md',
  'START_HERE.md',
  'AGENTS.md',
  'CONTEXT-PACK.md',
  'CHANGELOG.md',
  'CUBE-META.json',
  'REVISION-RECEIPT.json',
  'REENTRY-CONTRACT.json',
  'SURFACE-STATUS.json',
  'VALIDATION-INDEX.json',
  'tools/check_cube.py',
  'tools/deep_cube_audit.mjs',
  'package.json',
  'Makefile'
];

async function exists(path) { try { await access(path); return true; } catch { return false; } }
async function walk(dir = '.') {
  const out = [];
  for (const ent of await readdir(dir, { withFileTypes: true })) {
    if (['.git', 'node_modules', '__pycache__', 'out'].includes(ent.name)) continue;
    const p = `${dir}/${ent.name}`;
    if (ent.isDirectory()) out.push(...await walk(p));
    else out.push(p);
  }
  return out;
}
async function readJson(path) { return JSON.parse(await readFile(path, 'utf8')); }
function check(name, passed, detail = {}) { return { name, status: passed ? 'passed' : 'failed', ...detail }; }
function missingNeedles(body, needles) { return needles.filter((needle) => !String(body).includes(needle)); }
function missingNeedlesLower(body, needles) { const lower = String(body).toLowerCase(); return needles.filter((needle) => !lower.includes(String(needle).toLowerCase())); }
function sha256(bytes) { return createHash('sha256').update(bytes).digest('hex'); }
function revNumberFromPath(path) { const hits = [...String(path).matchAll(/(?:rev|REV)(\d{4})/g)].map((match) => Number(match[1])); return hits.length ? Math.max(...hits) : -1; }

const files = await walk('.');
const text = new Map();
const byteRows = [];
for (const file of files) {
  if (file.endsWith('.zip')) continue;
  const rel = relative('.', file);
  try { const bytes = await readFile(file); byteRows.push({ path: rel, bytes: bytes.length, hash: sha256(bytes) }); text.set(rel, bytes.toString('utf8')); } catch {}
}
const packageJson = await readJson('package.json');
const centralDocs = [
  ['CUBE-META.json', await readJson('CUBE-META.json')],
  ['REVISION-RECEIPT.json', await readJson('REVISION-RECEIPT.json')],
  ['REENTRY-CONTRACT.json', await readJson('REENTRY-CONTRACT.json')],
  ['SURFACE-STATUS.json', await readJson('SURFACE-STATUS.json')],
  ['VALIDATION-INDEX.json', await readJson('VALIDATION-INDEX.json')]
];
const manifest = await readJson('test/manifest.json');
const impact = await readJson('test/impact-map.json');
const inventory = await readJson('test/surface-inventory.json');
const quarantine = await readJson('test/quarantine.json');
const registry = await readJson('artifacts/research/RELATED-WORK-SOURCE-REGISTRY.json');
const testRegistry = await readJson('artifacts/research/TEST-FACILITY-RESEARCH-REGISTRY.json');
const compactionPath = `artifacts/datacube-audit/${CURRENT_PREFIX}-DUPLICATE-DOC-COMPACTION.json`;
const compaction = await readJson(compactionPath);

const centralRevisions = Object.fromEntries([...centralDocs, ['test/manifest.json', manifest], ['test/impact-map.json', impact], ['test/surface-inventory.json', inventory], ['test/quarantine.json', quarantine], ['RELATED-WORK-SOURCE-REGISTRY.json', registry], ['TEST-FACILITY-RESEARCH-REGISTRY.json', testRegistry]].map(([path, obj]) => [path, obj.revision]));
const currentnessRows = [];
for (const [path, obj] of [...centralDocs, ['package.json', packageJson]]) {
  for (const [key, expected] of Object.entries(EXPECTED)) if (obj[key] !== expected) currentnessRows.push({ path, key, actual: obj[key] ?? null, expected });
  for (const key of ['filename', 'packaged_bundle_filename', 'package_filename', 'package_files', 'packageFileName', 'package_file_name']) {
    if (obj[key] == null) continue;
    const filename = String(obj[key]);
    if (!filename.includes(REVISION) || !filename.includes(EXPECTED.package_slug) || /rev009[0-8]/.test(filename) || /write-budget-guard-current-proof|open-failure-recovery-current-proof/.test(filename)) {
      currentnessRows.push({ path, key, actual: filename, expected: `${REVISION}...${EXPECTED.package_slug}.zip` });
    }
  }
  if (obj.browserrt_current) {
    const expectedCurrent = { revision: REVISION, version: VERSION, codename: EXPECTED.codename, release_task: RELEASE_TASK, browser_task: BROWSER_TASK, audit_task: AUDIT_TASK, package_slug: EXPECTED.package_slug };
    for (const [key, expected] of Object.entries(expectedCurrent)) if (obj.browserrt_current[key] !== expected) currentnessRows.push({ path, key: `browserrt_current.${key}`, actual: obj.browserrt_current[key] ?? null, expected });
  }
}
const tasks = manifest.tasks || [];
const taskIds = tasks.map((task) => task.id);
const taskSet = new Set(taskIds);
const duplicateTaskIds = taskIds.filter((id, index) => taskIds.indexOf(id) !== index);
const releaseTasks = tasks.filter((task) => task.tiers?.includes('release'));
const browserTasks = tasks.filter((task) => task.lane === 'browser');
const releaseBrowserTasks = releaseTasks.filter((task) => task.lane === 'browser');
const releaseEstimateMs = releaseTasks.reduce((sum, task) => sum + (task.estimatedMs || 0), 0);
const browserEstimateMs = browserTasks.reduce((sum, task) => sum + (task.estimatedMs || 0), 0);
const requiredMissingTasks = REQUIRED_TASKS.filter((id) => !taskSet.has(id));
const taskById = new Map(tasks.map((task) => [task.id, task]));
const browserTaskTierProblems = BROWSER_HEAVY.map((id) => taskById.get(id)).filter(Boolean).filter((task) => task.tiers?.includes('release') || task.lane !== 'browser' || task.parallelGroup !== 'browser-process').map((task) => ({ id: task.id, tiers: task.tiers, lane: task.lane, parallelGroup: task.parallelGroup }));
const storageLaneTimeoutTask = taskById.get('scheduler:storage-lane-operation-timeout-proof');
const readTimeoutTask = taskById.get('scheduler:storage-lane-web-lock-read-timeout-nonpoison-proof');
const storageLaneReleaseProblem = !storageLaneTimeoutTask || !storageLaneTimeoutTask.tiers?.includes('release') || storageLaneTimeoutTask.lane === 'browser' || !readTimeoutTask || !readTimeoutTask.tiers?.includes('release') || readTimeoutTask.lane === 'browser';
const requiredFields = ['id','description','command','tiers','tags','areas','lane','parallelGroup','size','isolation','flakiness','risk','estimatedMs','timeoutMs','inputs','outputs','capabilities','cachePolicy','evidence'];
const missingManifestFields = [];
for (const task of tasks) for (const field of requiredFields) if (!(field in task)) missingManifestFields.push({ id: task.id || '<missing-id>', field });
const currentOutputProblems = [];
for (const task of tasks) {
  for (const output of task.outputs || []) for (const hit of String(output).match(/REV\d{4}-/g) || []) if (hit !== `${CURRENT_PREFIX}-`) currentOutputProblems.push({ id: task.id, outputHit: hit });
  const command = Array.isArray(task.command) ? task.command.join(' ') : String(task.command || '');
  for (const hit of command.match(/REV\d{4}-/g) || []) if (hit !== `${CURRENT_PREFIX}-`) currentOutputProblems.push({ id: task.id, commandHit: hit });
}
const artifactPaths = files.filter((file) => /^\.\/artifacts\/(audit|proof|validation)\//.test(file)).map((file) => relative('.', file));
const oldArtifactPrefixes = artifactPaths.filter((path) => /REV\d{4}-/.test(path) && !path.includes(CURRENT_PREFIX) && !path.includes(PREVIOUS_PREFIX));
const packagePlan = packageJson.scripts?.plan || '';
const makefileText = text.get('Makefile') || '';
const makefilePlan = makefileText.match(/^plan:[\s\S]*?(?=^\S|\Z)/m)?.[0] || makefileText;
const planDrift = PLAN_FILES.flatMap((file) => [packagePlan.includes(file) ? null : { path: 'package.json', field: 'scripts.plan', missing: file }]).filter(Boolean);
const docMissing = {
  readme: missingNeedlesLower(text.get('README.md') || '', ['Current packaged head: `' + REVISION + '`', EXPECTED.codename, EXPECTED.current_task, 'opfsasyncblockstore', 'rollbackvalidblockpreserves', 'rollback', 'preserve']),
  start: missingNeedlesLower(text.get('START_HERE.md') || '', ['Current packaged head: `' + REVISION + '`', EXPECTED.current_task, EXPECTED.current_audit, 'opfsasyncblockstore', 'rollbackvalidblockpreserves', 'preserve', 'browser-light']),
  agents: missingNeedlesLower(text.get('AGENTS.md') || '', ['Current revision: ' + REVISION, EXPECTED.codename, EXPECTED.current_task, 'rollbackvalidblockpreserves', 'storage', 'cross-browser', 'quota', 'eviction', 'crash']),
  context: missingNeedlesLower(text.get('CONTEXT-PACK.md') || '', ['# BrowserRT context pack — ' + REVISION, EXPECTED.current_task, 'rollbackvalidblockpreserves', 'opfs', 'fake-opfs', 'cross-browser', 'quota', 'eviction', 'crash'])
}
for (const [rel, body] of [['README.md', text.get('README.md')], ['START_HERE.md', text.get('START_HERE.md')], ['CONTEXT-PACK.md', text.get('CONTEXT-PACK.md')], ['AGENTS.md', text.get('AGENTS.md')], ['REVISION-RECEIPT.json', text.get('REVISION-RECEIPT.json')]]) docMissing[`${rel}:nonclaims`] = missingNeedlesLower(body || '', CORE_NONCLAIMS);
for (const rel of [
  'docs/40-validation/storage-lane-operation-context-propagation-slice.md',
  'docs/40-validation/browser-opfs-web-lock-operation-context-propagation-slice.md',
  'docs/40-validation/operation-context-propagation-contract-audit-slice.md',
  'docs/40-validation/storage-lane-late-failure-quarantine-slice.md',
  'docs/40-validation/browser-opfs-web-lock-late-failure-quarantine-slice.md',
  'docs/40-validation/storage-lane-late-failure-quarantine-contract-audit-slice.md',
  'docs/40-validation/storage-lane-operation-timeout-slice.md',
  'docs/40-validation/browser-opfs-web-lock-operation-timeout-boundary-slice.md',
  'docs/40-validation/browser-opfs-web-lock-read-timeout-nonpoison-slice.md',
  'docs/40-validation/web-lock-read-timeout-nonpoison-contract-audit-slice.md',
  'docs/40-validation/browser-opfs-web-lock-service-worker-fetch-lifecycle-slice.md',
  'docs/40-validation/service-worker-fetch-lifecycle-contract-audit-slice.md',
  'docs/40-validation/browser-opfs-web-lock-service-worker-update-race-slice.md',
  'docs/40-validation/service-worker-update-race-contract-audit-slice.md',
  'docs/40-validation/browser-opfs-web-lock-service-worker-shutdown-boundary-slice.md',
  'docs/40-validation/service-worker-shutdown-boundary-contract-audit-slice.md'
]) docMissing[rel] = missingNeedlesLower(text.get(rel) || '', ['cross-browser','quota','eviction','crash']);
docMissing.compactionIndex = missingNeedlesLower(text.get(`docs/00-meta/revision-doc-compaction-index-${REVISION}.md`) || '', ['Revision doc compaction index','duplicate',REVISION]);
const runtimeMissing = {
  webLockStrictOptionRuntime: missingNeedles(text.get('src/web-lock-coordinator.mjs') || '', ['BRT_WEB_LOCK_OPTION_TYPE','BRT_WEB_LOCK_OPTION_CONFLICT','BRT_WEB_LOCK_SIGNAL_INVALID','coord:web-lock-option-rejected','cleanOptionalBooleanOption','validateLockOptionCombinations']),
  webLockStrictOptionRelease: missingNeedles(text.get('tools/web_lock_strict_option_guard_probe.mjs') || '', ['coord:web-lock-strict-option-guard-proof','ifAvailable-string-false','steal-string-false','ifAvailable-plus-steal','plain-object-signal','optionRejected']),
  webLockStrictOptionBrowser: missingNeedles(text.get('tools/browser_opfs_web_lock_strict_option_guard_probe.mjs') || '', ['browser:opfs-web-lock-strict-option-guard-proof','navigator.locks?.request','opfsWebLockGuardedBlockStore','plain-object-signal','storage:opfs-block-put']),
  webLockStrictOptionAudit: missingNeedles(text.get('tools/web_lock_strict_option_guard_contract_audit.mjs') || '', ['facility:web-lock-strict-option-guard-contract-audit','surface:web-lock-strict-option-guard','runtime-no-boolean-string-coercion']),
  opfsBlockStoreAbortSignalRuntime: missingNeedles(text.get('src/opfs-block-store.mjs') || '', ['BRT_OPFS_OPERATION_ABORTED','BRT_OPFS_ABORT_SIGNAL_INVALID','storage:opfs-block-abort','abortSignalFromOptions','explicitAbortSignals','rollbackFailedPut']),
  opfsBlockStoreAbortSignalRelease: missingNeedles(text.get('tools/opfs_block_store_abort_signal_probe.mjs') || '', ['opfs:block-store-abort-signal-proof','mid-write-abort-onWrite','mid-write-abort-onBeforeClose','BRT_OPFS_OPERATION_ABORTED','BRT_OPFS_ABORT_SIGNAL_INVALID']),
  opfsBlockStoreAbortSignalBrowser: missingNeedles(text.get('tools/browser_opfs_block_store_abort_signal_probe.mjs') || '', ['browser:opfs-block-store-abort-signal-proof','runManagedBrowserPage','navigator.storage?.getDirectory','BRT_OPFS_OPERATION_ABORTED','BRT_OPFS_ABORT_SIGNAL_INVALID','opfsWebLockGuardedBlockStore']),
  opfsBlockStoreAbortSignalAudit: missingNeedles(text.get('tools/opfs_block_store_abort_signal_contract_audit.mjs') || '', ['facility:opfs-block-store-abort-signal-contract-audit','surface:opfs-block-store-abort-signal','surface:browser-opfs-block-store-abort-signal','not storage-lane timeout cancellation']),
  opfsBlockStoreWriteBudgetGuardRuntime: missingNeedles(text.get('src/opfs-block-store.mjs') || '', ['writeBudgetGuard','normalizeWriteBudgetGuard','BRT_OPFS_WRITE_BUDGET_EXCEEDED','BRT_OPFS_ESTIMATE_UNAVAILABLE','storage:opfs-block-write-budget-check','navigator.storage.estimate']),
  opfsBlockStoreWriteBudgetGuardRelease: missingNeedles(text.get('tools/opfs_block_store_write_budget_guard_probe.mjs') || '', ['opfs:block-store-write-budget-guard-proof','reserve-budget-reject-before-open','per-put-ratio-budget-reject-before-open','BRT_OPFS_WRITE_BUDGET_EXCEEDED','BRT_OPFS_ESTIMATE_UNAVAILABLE']),
  opfsBlockStoreWriteBudgetGuardBrowser: missingNeedles(text.get('tools/browser_opfs_block_store_write_budget_guard_probe.mjs') || '', ['browser:opfs-block-store-write-budget-guard-proof','navigator.storage.estimate','raw-write-budget-reject-before-open','opfsWebLockGuardedBlockStore','locksAfterGuarded']),
  opfsBlockStoreWriteBudgetGuardAudit: missingNeedles(text.get('tools/opfs_block_store_write_budget_guard_contract_audit.mjs') || '', ['facility:opfs-block-store-write-budget-guard-contract-audit','surface:opfs-block-store-write-budget-guard','fake-opfs-harness:storage-estimate-refactor']),
  opfsBlockStoreOwnedRollbackGuardRuntime: missingNeedles(text.get('src/opfs-block-store.mjs') || '', ['rollbackOwnsFinalBlock','rollbackOwnershipSkips','storage:opfs-block-put-rollback-skipped','pre-existing-duplicate-block-not-owned-by-put','final-block-not-created-by-put']),
  opfsBlockStoreOwnedRollbackGuardRelease: missingNeedles(text.get('tools/opfs_block_store_owned_rollback_guard_probe.mjs') || '', ['opfs:block-store-owned-rollback-guard-proof','duplicate-put-trace-failure-must-not-delete-existing-block','duplicate-put-abort-during-inspection-must-not-delete-existing-block','owned-write-failure-still-rolls-back-created-final-block']),
  opfsBlockStoreOwnedRollbackGuardBrowser: missingNeedles(text.get('tools/browser_opfs_block_store_owned_rollback_guard_probe.mjs') || '', ['browser:opfs-block-store-owned-rollback-guard-proof','browser-duplicate-put-trace-failure-must-not-delete-existing-block','bytesPreserved','opfsWebLockGuardedBlockStore','locksAfterGuarded']),
  opfsBlockStoreOwnedRollbackGuardAudit: missingNeedles(text.get('tools/opfs_block_store_owned_rollback_guard_contract_audit.mjs') || '', ['facility:opfs-block-store-owned-rollback-guard-contract-audit','surface:opfs-block-store-owned-rollback-guard','current-office:audit-needles']),
  opfsBlockStoreOpenFailureRecoveryRuntime: missingNeedles(text.get('src/opfs-block-store.mjs') || '', ['openFailures','openRetryResets','storage:opfs-blockstore-open-error','rootPromiseReset']),
  opfsBlockStoreOpenFailureRecoveryRelease: missingNeedles(text.get('tools/opfs_block_store_open_failure_recovery_probe.mjs') || '', ['opfs:block-store-open-failure-recovery-proof','first-open-fails-and-resets-root-promise','second-put-retries-open-and-succeeds','openRetryResets']),
  opfsBlockStoreOpenFailureRecoveryBrowser: missingNeedles(text.get('tools/browser_opfs_block_store_open_failure_recovery_probe.mjs') || '', ['browser:opfs-block-store-open-failure-recovery-proof','browser-first-open-fails-and-resets-root-promise','rootPromiseReset','locksAfterGuarded']),
  opfsBlockStoreOpenFailureRecoveryAudit: missingNeedles(text.get('tools/opfs_block_store_open_failure_recovery_contract_audit.mjs') || '', ['facility:opfs-block-store-open-failure-recovery-contract-audit','surface:opfs-block-store-open-failure-recovery','current-office:audit-needles']),
  opfsBlockStoreWriteBudgetDuplicateBypassRuntime: missingNeedles(text.get('src/opfs-block-store.mjs') || '', ['#bypassWriteBudgetForDuplicate','writeBudgetDuplicateBypasses','storage:opfs-block-write-budget-duplicate-bypass','#openExistingPrefix','#existingBucket']),
  opfsBlockStoreWriteBudgetDuplicateBypassRelease: missingNeedles(text.get('tools/opfs_block_store_write_budget_duplicate_bypass_probe.mjs') || '', ['opfs:block-store-write-budget-duplicate-bypass-proof','verified-duplicate-budget-bypass','new-write-budget-reject-after-readonly-dedupe-before-mutation','corrupt-repair-budget-reject-preserves-corrupt-file']),
  opfsBlockStoreWriteBudgetDuplicateBypassBrowser: missingNeedles(text.get('tools/browser_opfs_block_store_write_budget_duplicate_bypass_probe.mjs') || '', ['browser:opfs-block-store-write-budget-duplicate-bypass-proof','patchedEstimate','browser-duplicate-put-bypasses-impossible-budget','browser-new-write-still-rejects-before-mutation','locksAfterGuarded']),
  opfsBlockStoreWriteBudgetDuplicateBypassAudit: missingNeedles(text.get('tools/opfs_block_store_write_budget_duplicate_bypass_contract_audit.mjs') || '', ['facility:opfs-block-store-write-budget-duplicate-bypass-contract-audit','surface:opfs-block-store-write-budget-duplicate-bypass','fake-harness:estimate-recorder-refactor']),
  opfsBlockStoreRollbackValidBlockPreserveRuntime: missingNeedles(text.get('src/opfs-block-store.mjs') || '', ['rollbackValidBlockPreserves','rollbackIntegrityChecks','storage:opfs-block-put-rollback-preserved','valid-final-block-preserved','failed-put-rollback-preserve-check']),
  opfsBlockStoreRollbackValidBlockPreserveRelease: missingNeedles(text.get('tools/opfs_block_store_rollback_valid_block_preserve_probe.mjs') || '', ['opfs:block-store-rollback-valid-block-preserve-proof','trace-failure-after-close-preserves-valid-final-block','abort-after-close-preserves-valid-final-block','invalid-owned-failure-still-rolls-back-file']),
  opfsBlockStoreRollbackValidBlockPreserveBrowser: missingNeedles(text.get('tools/browser_opfs_block_store_rollback_valid_block_preserve_probe.mjs') || '', ['browser:opfs-block-store-rollback-valid-block-preserve-proof','browser-trace-failure-after-close-preserves-valid-final-block','opfsRollbackValidBlockPreserveProof','locksAfterGuarded']),
  opfsBlockStoreRollbackValidBlockPreserveAudit: missingNeedles(text.get('tools/opfs_block_store_rollback_valid_block_preserve_contract_audit.mjs') || '', ['facility:opfs-block-store-rollback-valid-block-preserve-contract-audit','surface:opfs-block-store-rollback-valid-block-preserve','current-office:current-needles']),
  fakeOpfsHarnessShared: missingNeedles((text.get('tools/opfs_block_store_corrupt_block_repair_probe.mjs') || '') + (text.get('tools/lib/fake_opfs_harness.mjs') || ''), ['./lib/fake_opfs_harness.mjs','withFakeNavigator','fakeTreeSummary']),
  quarantineClearanceReplayRelease: missingNeedles(text.get('tools/storage_lane_quarantine_clearance_replay_guard_probe.mjs') || '', ['scheduler:storage-lane-quarantine-clearance-replay-guard-proof','rejected-cleared-quarantine-replay','persistTimedOutOperationQuarantineClearanceReceipt','restoreTimedOutOperationQuarantineClearanceReceiptFromBlockStore']),
  quarantineClearanceReplayBrowser: missingNeedles(text.get('tools/browser_opfs_web_lock_quarantine_clearance_replay_guard_probe.mjs') || '', ['browser:opfs-web-lock-quarantine-clearance-replay-guard-proof','opfsWebLockGuardedBlockStore','rejected-cleared-quarantine-replay','same profile']),
  quarantineClearanceReplayAudit: missingNeedles(text.get('tools/storage_lane_quarantine_clearance_replay_guard_contract_audit.mjs') || '', ['facility:storage-lane-quarantine-clearance-replay-guard-contract-audit','surface:storage-lane-quarantine-clearance-replay-guard','surface:browser-opfs-web-lock-quarantine-clearance-replay-guard']),
  quarantineClearanceReplayDocs: missingNeedles(text.get('docs/40-validation/browser-opfs-web-lock-quarantine-clearance-replay-guard-slice.md') || '', ['Managed Chromium','same profile','rejected-cleared-quarantine-replay','not cross-browser']),
  quarantineClearanceRuntime: missingNeedles((text.get('src/storage-lane-scheduler.mjs') || '') + (text.get('src/block-store-lane-adapter.mjs') || ''), ['registerTimedOutOperationQuarantineClearanceReceipt','clearanceReceipt.v1','timed-out-quarantine-import-rejected-cleared','storage-lane:timed-out-quarantine-import-replay-rejected']),
  quarantineClearanceReceiptProvenanceBindingRuntime: missingNeedles((text.get('src/storage-lane-scheduler.mjs') || '') + (text.get('src/block-store-lane-adapter.mjs') || ''), ['operationEpoch','operationReplayKey','operationEpochForExecutor','rejected-cleared-quarantine-row-replay-downgrade','clearedLegacyOperationKeys']),
  quarantineClearanceReceiptEpochReplayRelease: missingNeedles(text.get('tools/storage_lane_quarantine_clearance_epoch_replay_guard_probe.mjs') || '', ['scheduler:storage-lane-quarantine-clearance-epoch-replay-guard-proof','operationEpoch','operationReplayKey','statusRewriteDowngrade','collisionImport']),
  quarantineClearanceReceiptEpochReplayBrowser: missingNeedles(text.get('tools/browser_opfs_web_lock_quarantine_clearance_epoch_replay_guard_probe.mjs') || '', ['browser:opfs-web-lock-quarantine-clearance-epoch-replay-guard-proof','opfsWebLockGuardedBlockStore','operationEpoch']),
  quarantineClearanceReceiptEpochReplayAudit: missingNeedles(text.get('tools/storage_lane_quarantine_clearance_epoch_replay_guard_contract_audit.mjs') || '', ['facility:storage-lane-quarantine-clearance-epoch-replay-guard-contract-audit','surface:storage-lane-quarantine-clearance-epoch-replay-guard','surface:browser-opfs-web-lock-quarantine-clearance-epoch-replay-guard']),
  quarantineClearanceReceiptLaneBindingRuntime: missingNeedles((text.get('src/storage-lane-scheduler.mjs') || '') + (text.get('src/block-store-lane-adapter.mjs') || ''), ['timed-out-quarantine-clearance-receipt-lane-mismatch','rejected-clearance-receipt-lane-binding','quarantineClearanceReceiptLaneBindingRejected','cleared row lane']),
  quarantineClearanceReceiptLaneBindingRelease: missingNeedles(text.get('tools/storage_lane_quarantine_clearance_receipt_lane_binding_probe.mjs') || '', ['scheduler:storage-lane-quarantine-clearance-receipt-lane-binding-proof','rowLaneMismatchValidation','wrongLaneRegister','markUnhealthyForced']),
  quarantineClearanceReceiptLaneBindingBrowser: missingNeedles(text.get('tools/browser_opfs_web_lock_quarantine_clearance_receipt_lane_binding_probe.mjs') || '', ['browser:opfs-web-lock-quarantine-clearance-receipt-lane-binding-proof','opfsWebLockGuardedBlockStore','wrongLaneRegister']),
  quarantineClearanceReceiptLaneBindingAudit: missingNeedles(text.get('tools/storage_lane_quarantine_clearance_receipt_lane_binding_contract_audit.mjs') || '', ['facility:storage-lane-quarantine-clearance-receipt-lane-binding-contract-audit','surface:storage-lane-quarantine-clearance-receipt-lane-binding','surface:browser-opfs-web-lock-quarantine-clearance-receipt-lane-binding']),

  quarantineLanewideScopeRuntime: missingNeedles((text.get('src/storage-lane-scheduler.mjs') || '') + (text.get('src/block-store-lane-adapter.mjs') || '') + (text.get('src/types.d.ts') || ''), ['lane-wide receipts are lane-scoped','receipt lane must be present','rev0086']),
  quarantineLanewideScopeRelease: missingNeedles(text.get('tools/storage_lane_quarantine_clearance_lanewide_scope_probe.mjs') || '', ['scheduler:storage-lane-quarantine-clearance-lanewide-scope-proof','ambiguousLaneWideReceipt','importAfterAmbiguousReject']),
  quarantineLanewideScopeBrowser: missingNeedles(text.get('tools/browser_opfs_web_lock_quarantine_clearance_lanewide_scope_probe.mjs') || '', ['browser:opfs-web-lock-quarantine-clearance-lanewide-scope-proof','opfsWebLockGuardedBlockStore','ambiguousLaneWideReceipt']),
  quarantineLanewideScopeAudit: missingNeedles(text.get('tools/storage_lane_quarantine_clearance_lanewide_scope_contract_audit.mjs') || '', ['facility:storage-lane-quarantine-clearance-lanewide-scope-contract-audit','surface:storage-lane-quarantine-clearance-lanewide-scope']),
  quarantineRestoreRegistrationGateRuntime: missingNeedles((text.get('src/block-store-lane-adapter.mjs') || '') + (text.get('src/types.d.ts') || ''), ['quarantineClearanceReceiptRegistrationRejectedOnRestore','registration?.ok !== true','restore registration gate fails closed']),
  quarantineRestoreRegistrationGateRelease: missingNeedles(text.get('tools/storage_lane_quarantine_clearance_restore_registration_gate_probe.mjs') || '', ['scheduler:storage-lane-quarantine-clearance-restore-registration-gate-proof','wrongLaneRestore','block-store-restore-clearance-receipt']),
  quarantineRestoreRegistrationGateBrowser: missingNeedles(text.get('tools/browser_opfs_web_lock_quarantine_clearance_restore_registration_gate_probe.mjs') || '', ['browser:opfs-web-lock-quarantine-clearance-restore-registration-gate-proof','opfsWebLockGuardedBlockStore','receiptVerifyBeforeRestore','wrongLaneRestore']),
  quarantineRestoreRegistrationGateAudit: missingNeedles(text.get('tools/storage_lane_quarantine_clearance_restore_registration_gate_contract_audit.mjs') || '', ['facility:storage-lane-quarantine-clearance-restore-registration-gate-contract-audit','surface:storage-lane-quarantine-clearance-restore-registration-gate']),
  quarantineOperationReplayKeyCollisionRuntime: missingNeedles((text.get('src/storage-lane-scheduler.mjs') || '') + (text.get('src/block-store-lane-adapter.mjs') || '') + (text.get('src/types.d.ts') || ''), ['timedOutOperationMapKey','duplicate operationReplayKey','operationReplayKey','same visible opId']),
  quarantineOperationReplayKeyCollisionRelease: missingNeedles(text.get('tools/storage_lane_quarantine_review_replay_key_scope_probe.mjs') || '', ['scheduler:storage-lane-quarantine-review-replay-key-scope-proof','same visible opId','duplicateOperationKeyLedger','rejected-ledger-integrity']),
  quarantineOperationReplayKeyCollisionBrowser: missingNeedles(text.get('tools/browser_opfs_web_lock_quarantine_review_replay_key_scope_probe.mjs') || '', ['browser:opfs-web-lock-quarantine-review-replay-key-scope-proof','opfsWebLockGuardedBlockStore','maintenanceReceipts','distinct operationReplayKey']),
  quarantineOperationReplayKeyCollisionAudit: missingNeedles(text.get('tools/storage_lane_quarantine_review_replay_key_scope_contract_audit.mjs') || '', ['facility:storage-lane-quarantine-review-replay-key-scope-contract-audit','surface:storage-lane-quarantine-review-replay-key-scope']),
  quarantineLaneFilterImportRuntime: missingNeedles((text.get('src/storage-lane-scheduler.mjs') || '') + (text.get('src/block-store-lane-adapter.mjs') || '') + (text.get('src/types.d.ts') || ''), ['allowPartialImport','allowEmptyImport','filteredOutCount','quarantineLedgerLaneFilterRejected','timed-out-quarantine-import-rejected-lane-filter-empty','timed-out-quarantine-import-rejected-lane-filter-partial']),
  quarantineLaneFilterImportRelease: missingNeedles(text.get('tools/storage_lane_quarantine_lane_filter_import_guard_probe.mjs') || '', ['scheduler:storage-lane-quarantine-lane-filter-import-guard-proof','rejected-lane-filter-empty-import','rejected-lane-filter-partial-import','markUnhealthyForced']),
  quarantineLaneFilterImportBrowser: missingNeedles(text.get('tools/browser_opfs_web_lock_quarantine_lane_filter_import_guard_probe.mjs') || '', ['browser:opfs-web-lock-quarantine-lane-filter-import-guard-proof','opfsWebLockGuardedBlockStore','rejected-lane-filter-empty-import','rejected-lane-filter-partial-import']),
  quarantineLaneFilterImportAudit: missingNeedles(text.get('tools/storage_lane_quarantine_lane_filter_import_guard_contract_audit.mjs') || '', ['facility:storage-lane-quarantine-lane-filter-import-guard-contract-audit','surface:storage-lane-quarantine-lane-filter-import-guard','surface:browser-opfs-web-lock-quarantine-lane-filter-import-guard']),
  quarantineClearanceRowReplayRuntime: missingNeedles((text.get('src/storage-lane-scheduler.mjs') || '') + (text.get('src/block-store-lane-adapter.mjs') || ''), ['clearedRowKeys','clearedOperationKeys','clearedReplayKeys','timed-out-quarantine-import-rejected-cleared-row','storage-lane:timed-out-quarantine-import-row-replay-rejected']),
  quarantineClearanceRowReplayRelease: missingNeedles(text.get('tools/storage_lane_quarantine_clearance_row_replay_guard_probe.mjs') || '', ['scheduler:storage-lane-quarantine-clearance-row-replay-guard-proof','rowReplay','statusRewriteReplay','operationKey','rejected-cleared-quarantine-row-replay']),
  quarantineClearanceRowReplayBrowser: missingNeedles(text.get('tools/browser_opfs_web_lock_quarantine_clearance_row_replay_guard_probe.mjs') || '', ['browser:opfs-web-lock-quarantine-clearance-row-replay-guard-proof','opfsWebLockGuardedBlockStore','statusRewriteReplay','rejected-cleared-quarantine-row-replay']),
  quarantineClearanceRowReplayAudit: missingNeedles(text.get('tools/storage_lane_quarantine_clearance_row_replay_guard_contract_audit.mjs') || '', ['facility:storage-lane-quarantine-clearance-row-replay-guard-contract-audit','surface:storage-lane-quarantine-clearance-row-replay-guard','surface:browser-opfs-web-lock-quarantine-clearance-row-replay-guard']),
  quarantineClearanceRowReplayDocs: missingNeedles(text.get('docs/40-validation/browser-opfs-web-lock-quarantine-clearance-row-replay-guard-slice.md') || '', ['Managed Chromium','status-rewritten','rejected-cleared-quarantine-row-replay','not cross-browser']),
  quarantineNoopClearanceRelease: missingNeedles(text.get('tools/storage_lane_quarantine_noop_clearance_receipt_guard_probe.mjs') || '', ['scheduler:storage-lane-quarantine-noop-clearance-receipt-guard-proof','timed-out-quarantine-clear-noop','zeroReceiptValidation','rejected-cleared-quarantine-replay']),
  quarantineNoopClearanceBrowser: missingNeedles(text.get('tools/browser_opfs_web_lock_quarantine_noop_clearance_receipt_guard_probe.mjs') || '', ['browser:opfs-web-lock-quarantine-noop-clearance-receipt-guard-proof','opfsWebLockGuardedBlockStore','timed-out-quarantine-clear-noop','zeroReceiptValidation']),
  quarantineNoopClearanceAudit: missingNeedles(text.get('tools/storage_lane_quarantine_noop_clearance_receipt_guard_contract_audit.mjs') || '', ['facility:storage-lane-quarantine-noop-clearance-receipt-guard-contract-audit','surface:storage-lane-quarantine-noop-clearance-receipt-guard','surface:browser-opfs-web-lock-quarantine-noop-clearance-receipt-guard']),
  quarantineNoopClearanceDocs: missingNeedles(text.get('docs/40-validation/browser-opfs-web-lock-quarantine-noop-clearance-receipt-guard-slice.md') || '', ['Managed Chromium','zero-row','timed-out-quarantine-clear-noop','not a cross-browser']),
  quarantineNoopClearanceRuntime: missingNeedles((text.get('src/storage-lane-scheduler.mjs') || '') + (text.get('src/block-store-lane-adapter.mjs') || ''), ['timed-out-quarantine-clear-noop','rejected-noop-clear','clearance receipt requires at least one cleared timed-out quarantine row','receipt must clear at least one timed-out quarantine row']),
  quarantineClearanceReceiptRegistrationIntegrityRuntime: missingNeedles((text.get('src/storage-lane-scheduler.mjs') || '') + (text.get('src/block-store-lane-adapter.mjs') || ''), ['rejected-clearance-receipt-integrity','rejected-clearance-receipt-integrity','validateTimedOutOperationQuarantineClearanceReceiptForRegistration','opIds must match cleared row opIds']),

  quarantineReviewRelease: missingNeedles(text.get('tools/storage_lane_quarantine_review_binding_probe.mjs') || '', ['scheduler:storage-lane-quarantine-review-binding-proof','timed-out-quarantine-clear-review-fingerprint-required','timed-out-quarantine-clear-review-fingerprint-mismatch','tamperedLedger','createTimedOutOperationQuarantineReview']),
  quarantineReviewBrowser: missingNeedles(text.get('tools/browser_opfs_web_lock_quarantine_review_binding_probe.mjs') || '', ['browser:opfs-web-lock-quarantine-review-binding-proof','tamperedLedger','missingFingerprintClear','staleFingerprintClear','reviewManifest','clearWithManifest']),
  quarantineReviewAudit: missingNeedles(text.get('tools/storage_lane_quarantine_review_binding_contract_audit.mjs') || '', ['facility:storage-lane-quarantine-review-binding-contract-audit','surface:storage-lane-quarantine-review-binding','surface:browser-opfs-web-lock-quarantine-review-binding']),
  quarantineReviewDocs: missingNeedles(text.get('docs/40-validation/browser-opfs-web-lock-quarantine-review-binding-slice.md') || '', ['Managed Chromium only','quarantineFingerprint','reviewFingerprint','not cryptographic attestation','not claim rollback']),
  quarantineLegacyClearRelease: missingNeedles(text.get('tools/storage_lane_quarantine_legacy_clear_binding_probe.mjs') || '', ['scheduler:storage-lane-quarantine-legacy-clear-binding-proof','late-success-clear-review-fingerprint-required','late-failure-clear-review-fingerprint-required','staleOldSuccessReviewOnFailure','reviewManifest']),
  quarantineLegacyClearBrowser: missingNeedles(text.get('tools/browser_opfs_web_lock_quarantine_legacy_clear_binding_probe.mjs') || '', ['browser:opfs-web-lock-quarantine-legacy-clear-binding-proof','opfsWebLockGuardedBlockStore','late-success-clear-review-fingerprint-required','late-failure-clear-review-fingerprint-required']),
  quarantineLegacyClearAudit: missingNeedles(text.get('tools/storage_lane_quarantine_legacy_clear_binding_contract_audit.mjs') || '', ['facility:storage-lane-quarantine-legacy-clear-binding-contract-audit','surface:storage-lane-quarantine-legacy-clear-binding','surface:browser-opfs-web-lock-quarantine-legacy-clear-binding']),
  quarantineUnsettledOrphanRelease: missingNeedles(text.get('tools/storage_lane_unsettled_orphan_review_probe.mjs') || '', ['scheduler:storage-lane-unsettled-orphan-review-proof','timed-out-operation-still-unsettled','BRT_STORAGE_TIMED_OUT_OPERATION_ORPHANED','finalizeUnsettledTimedOutOperations','timed-out-operation-late-failure']),
  quarantineUnsettledOrphanBrowser: missingNeedles(text.get('tools/browser_opfs_web_lock_unsettled_orphan_review_probe.mjs') || '', ['browser:opfs-web-lock-unsettled-orphan-review-proof','opfsWebLockGuardedBlockStore','BRT_STORAGE_OPERATION_TIMEOUT','BRT_STORAGE_TIMED_OUT_OPERATION_ORPHANED','coord:web-lock-acquired']),
  quarantineUnsettledOrphanAudit: missingNeedles(text.get('tools/storage_lane_unsettled_orphan_review_contract_audit.mjs') || '', ['facility:storage-lane-unsettled-orphan-review-contract-audit','surface:storage-lane-unsettled-orphan-review','surface:browser-opfs-web-lock-unsettled-orphan-review']),
  quarantineUnsettledOrphanDocs: missingNeedles(text.get('docs/40-validation/browser-opfs-web-lock-unsettled-orphan-review-slice.md') || '', ['managed Chromium','reviewed/fingerprint-bound','BRT_STORAGE_TIMED_OUT_OPERATION_ORPHANED','cross-browser']),
  quarantineUnsettledOrphanRuntime: missingNeedles((text.get('src/storage-lane-scheduler.mjs') || '') + (text.get('src/block-store-lane-adapter.mjs') || ''), ['finalizeUnsettledTimedOutOperations','BRT_STORAGE_TIMED_OUT_OPERATION_ORPHANED','storage-lane:timed-out-quarantine-orphans-finalized','createTimedOutOperationQuarantineReview']),
  quarantineUnsettledOrphanProofs: missingNeedles((text.get('tools/storage_lane_unsettled_orphan_review_probe.mjs') || '') + (text.get('tools/browser_opfs_web_lock_unsettled_orphan_review_probe.mjs') || '') + (text.get('tools/storage_lane_unsettled_orphan_review_contract_audit.mjs') || ''), ['scheduler:storage-lane-unsettled-orphan-review-proof','browser:opfs-web-lock-unsettled-orphan-review-proof','facility:storage-lane-unsettled-orphan-review-contract-audit','BRT_STORAGE_TIMED_OUT_OPERATION_ORPHANED','reviewManifest']),
  quarantineUnsettledOrphanDocsCombined: missingNeedles((text.get('docs/40-validation/storage-lane-unsettled-orphan-review-slice.md') || '') + (text.get('docs/40-validation/browser-opfs-web-lock-unsettled-orphan-review-slice.md') || ''), ['imported unsettled','reviewFingerprint','provider cancellation','production readiness']),
  quarantineReceiptRestoreIntegrityRuntime: missingNeedles((text.get('src/block-store-lane-adapter.mjs') || ''), ['verifyBeforeRestore','rejected-clearance-receipt-block-integrity','rejected-quarantine-ledger-block-integrity','block-store-lane:quarantine-clearance-receipt-restore-block-integrity-rejected','quarantineClearanceReceiptRestoreBlockIntegrityRejected']),
  quarantineReceiptRestoreIntegrityRelease: missingNeedles(text.get('tools/storage_lane_quarantine_receipt_restore_integrity_probe.mjs') || '', ['scheduler:storage-lane-quarantine-receipt-restore-integrity-proof','rejected-clearance-receipt-block-integrity','rejected-quarantine-ledger-block-integrity','must not call get() after failed verify']),
  quarantineReceiptRestoreIntegrityBrowser: missingNeedles(text.get('tools/browser_opfs_web_lock_quarantine_receipt_restore_integrity_probe.mjs') || '', ['browser:opfs-web-lock-quarantine-receipt-restore-integrity-proof','opfsWebLockGuardedBlockStore','storage:opfs-block-corrupt','rejected-clearance-receipt-block-integrity']),
  quarantineReceiptRestoreIntegrityAudit: missingNeedles(text.get('tools/storage_lane_quarantine_receipt_restore_integrity_contract_audit.mjs') || '', ['facility:storage-lane-quarantine-receipt-restore-integrity-contract-audit','surface:storage-lane-quarantine-receipt-restore-integrity','surface:browser-opfs-web-lock-quarantine-receipt-restore-integrity']),
  quarantineRestoreExpectedFingerprintRuntime: missingNeedles((text.get('src/block-store-lane-adapter.mjs') || '') + (text.get('src/types.d.ts') || ''), ['expectedQuarantineFingerprint','expectedReceiptFingerprint','expectedPreClearanceFingerprint','expectedPostClearanceFingerprint','rejected-quarantine-ledger-expected-fingerprint','rejected-clearance-receipt-expected-fingerprint']),
  quarantineRestoreExpectedFingerprintRelease: missingNeedles(text.get('tools/storage_lane_quarantine_restore_expected_fingerprint_probe.mjs') || '', ['scheduler:storage-lane-quarantine-restore-expected-fingerprint-proof','wrongLedgerRestore','wrongReceiptRestore','wrongPreclearanceRestore','rejected-quarantine-ledger-expected-fingerprint','rejected-clearance-receipt-expected-fingerprint']),
  quarantineRestoreExpectedFingerprintBrowser: missingNeedles((text.get('tools/browser_opfs_web_lock_quarantine_restore_expected_fingerprint_probe.mjs') || '') + (text.get('tools/lib/quarantine_restore_expected_fingerprint_harness.mjs') || ''), ['browser:opfs-web-lock-quarantine-restore-expected-fingerprint-proof','opfsWebLockGuardedBlockStore','expectedQuarantineFingerprint','expectedReceiptFingerprint','rejected-quarantine-ledger-expected-fingerprint','rejected-clearance-receipt-expected-fingerprint']),
  quarantineRestoreExpectedFingerprintAudit: missingNeedles(text.get('tools/storage_lane_quarantine_restore_expected_fingerprint_contract_audit.mjs') || '', ['facility:storage-lane-quarantine-restore-expected-fingerprint-contract-audit','expected-fingerprint','surface:storage-lane-quarantine-restore-expected-fingerprint']),
  quarantineStatusTransitionRuntime: missingNeedles((text.get('src/storage-lane-scheduler.mjs') || ''), ['statusTransitionReplacementCount','quarantineLedgerStatusTransitionReplacements','storage-lane:timed-out-quarantine-import-status-transition-replaced','removeExistingTimedOutRow']),
  quarantineStatusTransitionRelease: missingNeedles(text.get('tools/storage_lane_quarantine_status_transition_import_probe.mjs') || '', ['scheduler:storage-lane-quarantine-status-transition-import-proof','importFailed.statusTransitionReplacementCount','successful -> failed -> unsettled -> successful','staleReplay.disposition']),
  quarantineStatusTransitionBrowser: missingNeedles(text.get('tools/browser_opfs_web_lock_quarantine_status_transition_import_probe.mjs') || '', ['browser:opfs-web-lock-quarantine-status-transition-import-proof','opfsWebLockGuardedBlockStore','statusTransitionReplacementCount','guard.put']),
  quarantineStatusTransitionAudit: missingNeedles(text.get('tools/storage_lane_quarantine_status_transition_import_contract_audit.mjs') || '', ['facility:storage-lane-quarantine-status-transition-import-contract-audit','surface:storage-lane-quarantine-status-transition-import','surface:browser-opfs-web-lock-quarantine-status-transition-import']),
  quarantineReplayKeyReceiptIntegrityRuntime: missingNeedles((text.get('src/storage-lane-scheduler.mjs') || '') + (text.get('src/block-store-lane-adapter.mjs') || ''), ['operationReplayKeys must match cleared row operationReplayKeys','cleared row operationReplayKey mismatch','quarantineClearanceReceiptReplayKeyBindingRejected','clearanceRowsOperationReplayKeys']),
  quarantineReplayKeyReceiptIntegrityRelease: missingNeedles(text.get('tools/storage_lane_quarantine_clearance_replay_key_receipt_integrity_probe.mjs') || '', ['scheduler:storage-lane-quarantine-clearance-replay-key-receipt-integrity-proof','missing operationReplayKeys','extra operationReplayKeys','cleared row operationReplayKey mismatch']),
  quarantineReplayKeyReceiptIntegrityBrowser: missingNeedles(text.get('tools/browser_opfs_web_lock_quarantine_clearance_replay_key_receipt_integrity_probe.mjs') || '', ['browser:opfs-web-lock-quarantine-clearance-replay-key-receipt-integrity-proof','opfsWebLockGuardedBlockStore','operationReplayKeys must match cleared row operationReplayKeys']),
  quarantineReplayKeyReceiptIntegrityAudit: missingNeedles(text.get('tools/storage_lane_quarantine_clearance_replay_key_receipt_integrity_contract_audit.mjs') || '', ['facility:storage-lane-quarantine-clearance-replay-key-receipt-integrity-contract-audit','surface:storage-lane-quarantine-clearance-replay-key-receipt-integrity']),
  scheduler: missingNeedles(text.get('src/storage-lane-scheduler.mjs') || '', ['isStorageHealthFailure','BRT_WEB_LOCK_TIMEOUT','BRT_STORAGE_OPERATION_TIMEOUT','storage-lane:operation-timeout','defaultOperationTimeoutMs','operationTimeoutMs','READ_ONLY_WEB_LOCK_OPS','isReadOnlyWebLockTimeout','cancellation: false','unsettledTimedOutOperations','waitForTimedOutOperationsSettled','storage-lane:late-provider-settlement','storage-lane:late-provider-failure','storage-lane:late-provider-success','failedTimedOutOperations','successfulTimedOutOperations','clearFailedTimedOutOperations','clearSuccessfulTimedOutOperations','late-success-clear-scope-required','timedOutQuarantineFingerprint','quarantineFingerprint','createTimedOutOperationQuarantineReview','timed-out-quarantine-clear-review-fingerprint-mismatch']),
  blockStoreLaneAdapter: missingNeedles(text.get('src/block-store-lane-adapter.mjs') || '', ['const value = await run(context);','defaultOperationTimeoutMs','operationTimeoutMs','recoverWhenStoreSettled','block-store-lane:recover-settled','store-coordination-still-contended','requireTimedOutOperationsSettled','timed-out-operation-still-unsettled','timed-out-operation-late-failure','timed-out-operation-late-success','clearFailedTimedOutOperations','clearSuccessfulTimedOutOperations','createTimedOutOperationQuarantineReview','reviewFingerprint','reviewManifest']),
  coordinator: missingNeedles(text.get('src/web-lock-coordinator.mjs') || '', ['BRT_WEB_LOCK_TIMEOUT','BRT_WEB_LOCK_ABORTED','defaultTimeoutMs','coord:web-lock-timeout','queryLocks','waitForSettled']),
  guardedStore: missingNeedles(text.get('src/opfs-web-lock-guarded-block-store.mjs') || '', ['WebLockGuardedBlockStore','lockTimeoutMs','queryLocks(','waitForSettled(','storage:opfs-web-lock-guard-op-error','storage:opfs-web-lock-guard-settled']),
  quarantineLedgerRelease: missingNeedles(text.get('tools/storage_lane_quarantine_ledger_roundtrip_probe.mjs') || '', ['scheduler:storage-lane-quarantine-ledger-roundtrip-proof','timed-out-quarantine-clear-review-token-required','storage-lane:timed-out-quarantine-import']),
  quarantineLedgerBrowser: missingNeedles(text.get('tools/browser_opfs_web_lock_quarantine_ledger_persistence_integrity_probe.mjs') || '', ['browser:opfs-web-lock-quarantine-ledger-persistence-integrity-proof','runManagedBrowserPage','restoreTimedOutOperationQuarantineFromBlockStore']),
  quarantineLedgerAudit: missingNeedles(text.get('tools/storage_lane_quarantine_ledger_persistence_integrity_contract_audit.mjs') || '', ['facility:storage-lane-quarantine-ledger-persistence-integrity-contract-audit','surface:storage-lane-quarantine-ledger-persistence']),
  operationContextRelease: missingNeedles(text.get('tools/storage_lane_operation_context_propagation_probe.mjs') || '', ['scheduler:storage-lane-operation-context-propagation-proof','operationTimeoutMs reaches the provider','WebLockGuardedBlockStore']),
  operationContextBrowser: missingNeedles(text.get('tools/browser_opfs_web_lock_operation_context_propagation_probe.mjs') || '', ['browser:opfs-web-lock-operation-context-propagation-proof','Managed Chromium proof','recordingCalls']),
  operationContextAudit: missingNeedles(text.get('tools/operation_context_propagation_contract_audit.mjs') || '', ['facility:operation-context-propagation-contract-audit','adapter-passes-executor-context-to-run','guard-forwards-options-to-provider-methods']),
  lateSuccessRelease: missingNeedles(text.get('tools/storage_lane_late_success_quarantine_probe.mjs') || '', ['scheduler:storage-lane-late-success-quarantine-proof','timed-out-operation-late-success','lateProviderSettlementSuccesses','clearSuccessfulTimedOutOperations','late-success-clear-scope-required']),
  lateSuccessBrowser: missingNeedles(text.get('tools/browser_opfs_web_lock_late_success_quarantine_probe.mjs') || '', ['browser:opfs-web-lock-late-success-quarantine-proof','timed-out-operation-late-success','BRT_STORAGE_OPERATION_TIMEOUT','lateProviderSettlementSuccesses','clearSuccessfulTimedOutOperations']),
  lateSuccessAudit: missingNeedles(text.get('tools/storage_lane_late_success_quarantine_contract_audit.mjs') || '', ['facility:storage-lane-late-success-quarantine-contract-audit','surface:storage-lane-late-success-quarantine','late-success-clear-scope-required']),
  lateFailureRelease: missingNeedles(text.get('tools/storage_lane_late_failure_quarantine_probe.mjs') || '', ['scheduler:storage-lane-late-failure-quarantine-proof','timed-out-operation-late-failure','lateProviderSettlementFailures','clearFailedTimedOutOperations']),
  lateFailureBrowser: missingNeedles(text.get('tools/browser_opfs_web_lock_late_failure_quarantine_probe.mjs') || '', ['browser:opfs-web-lock-late-failure-quarantine-proof','timed-out-operation-late-failure','BRT_STORAGE_OPERATION_TIMEOUT','lateProviderSettlementFailures']),
  lateFailureAudit: missingNeedles(text.get('tools/storage_lane_late_failure_quarantine_contract_audit.mjs') || '', ['facility:storage-lane-late-failure-quarantine-contract-audit','surface:storage-lane-late-failure-quarantine']),
  lateSettlementRelease: missingNeedles(text.get('tools/storage_lane_late_settlement_recovery_gate_probe.mjs') || '', ['scheduler:storage-lane-late-settlement-recovery-gate-proof','timed-out-operation-still-unsettled','storage-lane:late-provider-settlement','adapterResultAfterLateSettlement']),
  lateSettlementBrowser: missingNeedles(text.get('tools/browser_opfs_web_lock_late_settlement_recovery_gate_probe.mjs') || '', ['browser:opfs-web-lock-late-settlement-recovery-gate-proof','locksAfterTimeout','timeoutBlockPresentBeforeRelease','adapterResultAfterLateSettlement']),
  lateSettlementAudit: missingNeedles(text.get('tools/storage_lane_late_settlement_contract_audit.mjs') || '', ['facility:storage-lane-late-settlement-contract-audit','surface:storage-lane-late-settlement-recovery-gate']),
  operationTimeoutRelease: missingNeedles(text.get('tools/storage_lane_operation_timeout_probe.mjs') || '', ['scheduler:storage-lane-operation-timeout-proof','BRT_STORAGE_OPERATION_TIMEOUT','not provider cancellation','operationTimeouts']),
  operationTimeoutBrowser: missingNeedles(text.get('tools/browser_opfs_web_lock_operation_timeout_probe.mjs') || '', ['browser:opfs-web-lock-operation-timeout-boundary-proof','providerWroteBeforeTimeout','blockedRecovery','BRT_STORAGE_OPERATION_TIMEOUT']),
  operationTimeoutAudit: missingNeedles(text.get('tools/storage_lane_operation_timeout_contract_audit.mjs') || '', ['facility:storage-lane-operation-timeout-contract-audit','surface:storage-lane-operation-timeout']),
  readTimeoutRelease: missingNeedles(text.get('tools/storage_lane_web_lock_read_timeout_nonpoison_probe.mjs') || '', ['scheduler:storage-lane-web-lock-read-timeout-nonpoison-proof','read-only Web Lock timeout','laneHealthFailures']),
  readTimeoutBrowser: missingNeedles(text.get('tools/browser_opfs_web_lock_read_timeout_nonpoison_probe.mjs') || '', ['browser:opfs-web-lock-read-timeout-nonpoison-proof','BRT_WEB_LOCK_TIMEOUT','finalLocks']),
  readTimeoutAudit: missingNeedles(text.get('tools/web_lock_read_timeout_nonpoison_contract_audit.mjs') || '', ['facility:web-lock-read-timeout-nonpoison-contract-audit','surface:storage-lane-web-lock-read-timeout-nonpoison']),
  serviceWorkerFetchProof: missingNeedles(text.get('tools/browser_opfs_web_lock_service_worker_fetch_lifecycle_probe.mjs') || '', ['browser:opfs-web-lock-service-worker-fetch-lifecycle-proof','browserrt-sw-fetch-lifecycle','BRT_WEB_LOCK_TIMEOUT','settledRecovery']),
  serviceWorkerFetchAudit: missingNeedles(text.get('tools/service_worker_fetch_lifecycle_contract_audit.mjs') || '', ['facility:service-worker-fetch-lifecycle-contract-audit','surface:browser-opfs-web-lock-service-worker-fetch-lifecycle','carried-forward']),
  serviceWorkerLifecycleProof: missingNeedles(text.get('tools/browser_opfs_web_lock_service_worker_lifecycle_probe.mjs') || '', ['browser:opfs-web-lock-service-worker-lifecycle-proof','browserrt_opfs_web_lock_service_worker_holder.mjs','navigator.serviceWorker.register','BRT_WEB_LOCK_TIMEOUT']),
  serviceWorkerLifecycleAudit: missingNeedles(text.get('tools/service_worker_lifecycle_contract_audit.mjs') || '', ['facility:service-worker-lifecycle-contract-audit','surface:browser-opfs-web-lock-service-worker-lifecycle','browserrt_opfs_web_lock_service_worker_holder.mjs']),
  serviceWorkerRestartUpdateProof: missingNeedles(text.get('tools/browser_opfs_web_lock_service_worker_restart_update_probe.mjs') || '', ['browser:opfs-web-lock-service-worker-restart-update-proof','SW_V1_ROUTE','SW_V2_ROUTE',"updateViaCache: 'none'"]),
  serviceWorkerRestartUpdateAudit: missingNeedles(text.get('tools/service_worker_restart_update_contract_audit.mjs') || '', ['facility:service-worker-restart-update-contract-audit','surface:browser-opfs-web-lock-service-worker-restart-update']),
  serviceWorkerShutdownBoundaryProof: missingNeedles(text.get('tools/browser_opfs_web_lock_service_worker_shutdown_boundary_probe.mjs') || '', ['browser:opfs-web-lock-service-worker-shutdown-boundary-proof','BRT_WEB_LOCK_TIMEOUT','recoverWhenStoreSettled']),
  serviceWorkerShutdownBoundaryAudit: missingNeedles(text.get('tools/service_worker_shutdown_boundary_contract_audit.mjs') || '', ['facility:service-worker-shutdown-boundary-contract-audit','surface:browser-opfs-web-lock-service-worker-shutdown-boundary']),
  serviceWorkerUpdateRaceProof: missingNeedles(text.get('tools/browser_opfs_web_lock_service_worker_update_race_probe.mjs') || '', ['browser:opfs-web-lock-service-worker-update-race-proof','SW_V1_ROUTE','SW_V2_ROUTE',"updateViaCache: 'none'",'BRT_WEB_LOCK_TIMEOUT','settledRecovery']),
  serviceWorkerUpdateRaceAudit: missingNeedles(text.get('tools/service_worker_update_race_contract_audit.mjs') || '', ['facility:service-worker-update-race-contract-audit','surface:browser-opfs-web-lock-service-worker-update-race']),
  cdpFixture: missingNeedles(text.get('tools/browser_cdp_fixture.mjs') || '', ['connectBrowserCdp','openPageTarget','closePageTarget','Storage.getUsageAndQuota','killProcessGroup','routes = {}','routeEntries','Target.getTargets','Target.closeTarget','closeServiceWorkerTargets']),
  types: missingNeedles(text.get('src/types.d.ts') || '', [`revision: '${REVISION}'`, `version: '${VERSION}'`, 'lockTimeoutMs','operationTimeoutMs','queryLocks','waitForSettled','failedTimedOutOperations','successfulTimedOutOperations','clearFailedTimedOutOperations','clearSuccessfulTimedOutOperations','createTimedOutOperationQuarantineReview','reviewFingerprint','reviewManifest'])
};
const impactTaskIds = new Set((impact.rules || []).flatMap((rule) => rule.taskIds || []));
const missingCurrentImpact = REQUIRED_TASKS.filter((id) => !impactTaskIds.has(id));
const inventoryIds = new Set((inventory.surfaces || []).map((surface) => surface.id));
const missingCurrentSurfaces = [
  'surface:web-lock-strict-option-guard',
  'surface:browser-opfs-web-lock-strict-option-guard',
  'surface:web-lock-strict-option-guard-contract-audit',
  'surface:opfs-block-store-abort-signal',
  'surface:browser-opfs-block-store-abort-signal',
  'surface:opfs-block-store-abort-signal-contract-audit',
  'surface:opfs-block-store-write-budget-guard',
  'surface:browser-opfs-block-store-write-budget-guard',
  'surface:opfs-block-store-write-budget-guard-contract-audit',
  'surface:opfs-block-store-owned-rollback-guard',
  'surface:browser-opfs-block-store-owned-rollback-guard',
  'surface:opfs-block-store-owned-rollback-guard-contract-audit',
  'surface:opfs-block-store-open-failure-recovery',
  'surface:browser-opfs-block-store-open-failure-recovery',
  'surface:opfs-block-store-open-failure-recovery-contract-audit',
  'surface:storage-lane-quarantine-restore-backpressure-binding-contract-audit',
  'surface:browser-opfs-web-lock-quarantine-restore-backpressure-binding',
  'surface:storage-lane-quarantine-restore-backpressure-binding',
  'surface:storage-lane-quarantine-restore-backpressure-binding-contract-audit',
  'surface:browser-opfs-web-lock-quarantine-restore-backpressure-binding',
  'surface:storage-lane-quarantine-restore-backpressure-binding',
  'surface:storage-lane-quarantine-review-binding-contract-audit',
  'surface:browser-opfs-web-lock-quarantine-review-binding',
  'surface:storage-lane-quarantine-review-binding',
  'surface:storage-lane-operation-context-propagation',
  'surface:operation-context-propagation-contract-audit',
  'surface:browser-opfs-web-lock-operation-context-propagation',
  'surface:storage-lane-late-failure-quarantine',
  'surface:storage-lane-late-failure-quarantine-contract-audit',
  'surface:browser-opfs-web-lock-late-failure-quarantine',
  'surface:storage-lane-late-settlement-recovery-gate',
  'surface:storage-lane-late-settlement-contract-audit',
  'surface:browser-opfs-web-lock-late-settlement-recovery-gate',
  'surface:storage-lane-operation-timeout',
  'surface:browser-opfs-web-lock-operation-timeout-boundary',
  'surface:storage-lane-operation-timeout-contract-audit',
  'surface:storage-lane-web-lock-read-timeout-nonpoison',
  'surface:browser-opfs-web-lock-read-timeout-nonpoison',
  'surface:web-lock-read-timeout-nonpoison-contract-audit',
  'surface:browser-opfs-web-lock-service-worker-fetch-lifecycle',
  'surface:service-worker-fetch-lifecycle-contract-audit',
  'surface:browser-opfs-web-lock-service-worker-update-race',
  'surface:service-worker-update-race-contract-audit',
  'surface:browser-opfs-web-lock-service-worker-shutdown-boundary',
  'surface:service-worker-shutdown-boundary-contract-audit',
  'surface:browser-opfs-web-lock-service-worker-restart-update',
  'surface:service-worker-restart-update-contract-audit',
  'surface:browser-opfs-web-lock-service-worker-lifecycle',
  'surface:service-worker-lifecycle-contract-audit',
  'surface:browser-opfs-web-lock-settled-recovery',
  'surface:storage-lane-web-lock-settled-recovery',
  'surface:browser-opfs-web-lock-tab-timeout',
  'surface:storage-lane-web-lock-timeout-health'
].filter((id) => !inventoryIds.has(id));
const missingScripts = [
  'test:storage-lane:quarantine-clearance-row-replay-guard',
  'test:browser:opfs-web-lock-quarantine-clearance-row-replay-guard',
  'audit:storage-lane-quarantine-clearance-row-replay-guard',
  'test:storage-lane:quarantine-noop-clearance-receipt-guard',
  'test:browser:opfs-web-lock-quarantine-noop-clearance-receipt-guard',
  'audit:storage-lane-quarantine-noop-clearance-receipt-guard',
  'test:storage-lane:quarantine-clearance-replay-guard',
  'test:browser:opfs-web-lock-quarantine-clearance-replay-guard',
  'audit:storage-lane-quarantine-clearance-replay-guard',
  'test-storage-lane-quarantine-restore-backpressure-binding',
  'test-browser-opfs-web-lock-quarantine-restore-backpressure-binding',
  'audit-storage-lane-quarantine-restore-backpressure-binding',
  'test:storage-lane:operation-context-propagation',
  'test:browser:opfs-web-lock-operation-context-propagation',
  'audit:operation-context-propagation',
  'test:storage-lane:late-failure-quarantine',
  'test:browser:opfs-web-lock-late-failure-quarantine',
  'audit:storage-lane-late-failure-quarantine',
  'test:storage-lane:late-settlement',
  'test:browser:opfs-web-lock-late-settlement',
  'audit:storage-lane-late-settlement',
  'test:storage-lane:operation-timeout',
  'test:browser:opfs-web-lock-operation-timeout',
  'audit:storage-lane-operation-timeout',
  'test:storage-lane:web-lock-read-timeout-nonpoison',
  'test:browser:opfs-web-lock-read-timeout-nonpoison',
  'audit:web-lock-read-timeout-nonpoison',
  'test:browser:opfs-web-lock-service-worker-fetch-lifecycle',
  'audit:service-worker-fetch-lifecycle',
  'test:browser:opfs-web-lock-service-worker-update-race',
  'audit:service-worker-update-race',
  'test:opfs-block-store-abort-signal',
  'test:browser:opfs-block-store-abort-signal',
  'audit:opfs-block-store-abort-signal',
  'test:opfs-block-store-write-budget-guard',
  'test:browser:opfs-block-store-write-budget-guard',
  'audit:opfs-block-store-write-budget-guard',
  'test:opfs-block-store-owned-rollback-guard',
  'test:browser:opfs-block-store-owned-rollback-guard',
  'audit:opfs-block-store-owned-rollback-guard',
  'test:opfs-block-store-write-budget-duplicate-bypass',
  'test:browser:opfs-block-store-write-budget-duplicate-bypass',
  'audit:opfs-block-store-write-budget-duplicate-bypass',
  'test:opfs-block-store-rollback-valid-block-preserve',
  'test:browser:opfs-block-store-rollback-valid-block-preserve',
  'audit:opfs-block-store-rollback-valid-block-preserve'
].filter((key) => !packageJson.scripts?.[key]);
const makefileMissingTargets = ['current:', 'browser:', 'audit:', 'package:', 'verify:'].filter((needle) => !makefileText.includes(needle));
const estimateProblems = tasks.filter((task) => task.estimatedMs < 100 || task.timeoutMs <= task.estimatedMs).map((task) => ({ id: task.id, estimatedMs: task.estimatedMs, timeoutMs: task.timeoutMs }));
const hashGroups = new Map();
for (const row of byteRows) { if (!hashGroups.has(row.hash)) hashGroups.set(row.hash, []); hashGroups.get(row.hash).push(row); }
const duplicateGroups = [...hashGroups.values()].filter((group) => group.length > 1).map((group) => { const sorted = group.slice().sort((a, b) => revNumberFromPath(b.path) - revNumberFromPath(a.path) || a.path.localeCompare(b.path)); return { bytes: sorted[0].bytes, count: sorted.length, duplicateBytes: sorted[0].bytes * (sorted.length - 1), paths: sorted.map((row) => row.path) }; }).sort((a, b) => b.duplicateBytes - a.duplicateBytes || a.paths[0].localeCompare(b.paths[0]));
const duplicateDocGroups = duplicateGroups.filter((group) => group.paths.every((path) => path.startsWith('docs/')));
const duplicateDocBytes = duplicateDocGroups.reduce((sum, group) => sum + group.duplicateBytes, 0);
const compactionOk = compaction.revision === REVISION && ['applied','planned','passed'].includes(compaction.status || '') && await exists(compactionPath);
const checks = [
  check('central-revision-alignment', Object.values(centralRevisions).every((rev) => rev === REVISION), { centralRevisions }),
  check('current-office-slice-consistency', currentnessRows.length === 0, { currentnessRows }),
  check('package-version-alignment', packageJson.version === VERSION && packageJson.revision === REVISION && packageJson.package_slug === EXPECTED.package_slug && packageJson.codename === EXPECTED.codename && packageJson.current_task === EXPECTED.current_task && packageJson.current_audit === EXPECTED.current_audit, { packageVersion: packageJson.version, packageRevision: packageJson.revision, packageSlug: packageJson.package_slug, codename: packageJson.codename, current_task: packageJson.current_task, current_audit: packageJson.current_audit }),
  check('changelog-head-current-and-specific', (text.get('CHANGELOG.md') || '').startsWith(`## ${REVISION} —`) && missingNeedles(text.get('CHANGELOG.md') || '', [EXPECTED.current_task, EXPECTED.current_audit, 'rollbackValidBlockPreserves', 'storage:opfs-block-put-rollback-preserved', 'valid-final-block-preserved']).length === 0),
  check('first-read-docs-current-specific-nonclaims', Object.values(docMissing).every((missing) => missing.length === 0), { docMissing }),
  check('plan-commands-current-slice', planDrift.length === 0, { planDrift }),
  check('manifest-unique-ids', duplicateTaskIds.length === 0, { duplicateTaskIds }),
  check('manifest-required-fields', missingManifestFields.length === 0, { missingManifestFields }),
  check('required-current-tasks-present', requiredMissingTasks.length === 0, { requiredMissingTasks }),
  check('browser-proofs-explicit-not-release', browserTaskTierProblems.length === 0, { browserTaskTierProblems }),
  check('storage-lane-operation-timeout-release', !storageLaneReleaseProblem, { storageLaneTimeoutTask, readTimeoutTask }),
  check('release-browser-light', releaseBrowserTasks.length === 0, { releaseBrowserTasks: releaseBrowserTasks.map((task) => task.id), browserTaskCount: browserTasks.length }),
  check('browser-serial-grouped', browserTasks.every((task) => task.parallelGroup === 'browser-process'), { browserTaskIds: browserTasks.map((task) => task.id) }),
  check('current-artifact-outputs', currentOutputProblems.length === 0, { currentOutputProblems }),
  check('artifact-retention-current-or-previous', oldArtifactPrefixes.length === 0, { oldArtifactPrefixes }),
  check('release-estimate-contained', releaseEstimateMs > 0 && releaseEstimateMs <= 70000, { releaseEstimateMs, browserEstimateMs }),
  check('estimate-timeout-sane', estimateProblems.length === 0, { estimateProblems }),
  check('current-impact-map-coverage', missingCurrentImpact.length === 0, { missingCurrentImpact }),
  check('current-surface-inventory-coverage', missingCurrentSurfaces.length === 0, { missingCurrentSurfaces }),
  check('runtime-and-refactor-hooks-present', Object.values(runtimeMissing).every((missing) => missing.length === 0), { runtimeMissing }),
  check('convenience-scripts-present', missingScripts.length === 0 && makefileMissingTargets.length === 0, { missingScripts, makefileMissingTargets }),
  check('duplicate-doc-compaction-recorded', compactionOk, { compaction: { status: compaction.status, duplicateBytes: compaction.duplicateBytes ?? null } }),
  check('duplicate-doc-debt-contained-after-compaction', duplicateDocBytes <= 256 * 1024, { duplicateDocBytes, duplicateDocGroupCount: duplicateDocGroups.length })
];
const failed = checks.filter((row) => row.status !== 'passed');
const report = {
  project: 'BrowserRT',
  revision: REVISION,
  version: VERSION,
  schema: 5,
  status: failed.length === 0 ? 'passed' : 'failed',
  generatedAt: new Date().toISOString(),
  purpose: 'Deep cube audit for current BrowserRT head: current surfaces must point at the OPFS block-store failed-put rollback valid-block preserve release proof, managed Chromium OPFS/Web Locks proof, current-office audit, and contract audit; carried quarantine, AbortSignal, operation-timeout, read-timeout, and Service Worker lifecycle evidence must remain wired, browser-heavy tasks must stay explicit, and artifact/doc waste must stay bounded.',
  counts: { fileCount: files.length, taskCount: tasks.length, releaseTaskCount: releaseTasks.length, browserTaskCount: browserTasks.length, currentArtifactCount: artifactPaths.filter((p) => p.includes(CURRENT_PREFIX)).length, previousArtifactCount: artifactPaths.filter((p) => p.includes(PREVIOUS_PREFIX)).length, duplicateDocGroupCount: duplicateDocGroups.length, duplicateDocBytes },
  checks,
  warnings: [browserEstimateMs > 60000 ? 'Browser tier is intentionally explicit and non-release; run current ids rather than broad browser sweeps while iterating.' : null, duplicateDocGroups.length ? 'Some byte-identical docs remain below the soft budget; compact only when alias history is clear.' : null].filter(Boolean),
  nonClaims: [
    'Deep cube audit does not prove BrowserRT runtime semantics.',
    'Deep cube audit does not prove provider cancellation, rollback, no-mutation after dispatch, exactly-once behavior, OPFS fsync durability, power-loss durability, general crash recovery, organic eviction survival, persistent-storage retention, or cross-browser quota/crash behavior.',
    'Deep cube audit is a guard against cube/documentation/test-facility drift and cloudtainer waste.'
  ]
};
await mkdir(dirname(outPath), { recursive: true });
await writeFile(outPath, JSON.stringify(report, null, 2) + '\n');
console.log(outPath);
if (report.status !== 'passed') process.exitCode = 1;
