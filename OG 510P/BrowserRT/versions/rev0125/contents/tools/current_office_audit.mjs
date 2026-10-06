#!/usr/bin/env node
import assert from 'node:assert/strict';
import { readFile, writeFile, mkdir } from 'node:fs/promises';
import { dirname } from 'node:path';
import { performance } from 'node:perf_hooks';
import { REVISION, VERSION } from '../src/browserrt.mjs';

const PFX = `REV${REVISION.slice(3)}`;
const CODENAME = 'OPFS Raw Composite AbortSignal';
const PACKAGE_SLUG = 'opfs-block-store-raw-composite-abort-signal-current-proof';
const RELEASE_TASK = 'opfs:block-store-raw-composite-abort-signal-proof';
const BROWSER_TASK = 'browser:opfs-block-store-raw-composite-abort-signal-proof';
const AUDIT_TASK = 'facility:opfs-block-store-raw-composite-abort-signal-contract-audit';
const CURRENT_SURFACE = 'surface:opfs-block-store-raw-composite-abort-signal';
const CURRENT_SURFACE_IDS = Object.freeze([
  'surface:opfs-block-store-raw-composite-abort-signal',
  'surface:browser-opfs-block-store-raw-composite-abort-signal',
  'surface:opfs-block-store-raw-composite-abort-signal-contract-audit'
]);
const CURRENT_HOT_PATHS = Object.freeze([
  'src/opfs-block-store.mjs',
  'src/browserrt.mjs',
  'src/types.d.ts',
  'tools/opfs_block_store_raw_composite_abort_signal_probe.mjs',
  'tools/browser_opfs_block_store_raw_composite_abort_signal_probe.mjs',
  'tools/opfs_block_store_raw_composite_abort_signal_contract_audit.mjs',
  'docs/40-validation/opfs-block-store-raw-composite-abort-signal-slice.md',
  'docs/40-validation/browser-opfs-block-store-raw-composite-abort-signal-slice.md',
  'docs/40-validation/opfs-block-store-raw-composite-abort-signal-contract-audit-slice.md'
]);
const HOT_FIELD_STALE_NEEDLES = Object.freeze([
  'storage-lane-composite-abort-signal',
  'web-lock-guarded-abort-signal',
  'Web Lock Guarded AbortSignal',
  'WebLockGuardedBlockStore',
  'timeout-abort bridge',
  'open-failure-recovery',
  'readonly-no-create',
  'rollback-valid-block-preserve',
  'write-budget-duplicate-bypass',
  'block-store-lane-provider-options',
  'provider-timeout-abort-current-proof',
  'Recovery orphan-review gate',
  'Admission cancellation checkpoint'
]);
const CURRENT_SUMMARY_NEEDLES = Object.freeze([
  'Raw OPFS',
  'raw OPFS',
  'OPFS Raw Composite AbortSignal',
  'raw OPFS composite AbortSignal',
  'opfs-block-store-raw-composite-abort-signal'
]);
const CURRENT_COMMAND_NEEDLES = Object.freeze([RELEASE_TASK, BROWSER_TASK, AUDIT_TASK]);
const RESEARCH_REGISTRY_FORBIDDEN_HOT_KEYS = Object.freeze(['previous_revision', 'previousRevision', 'codename', 'package_slug', 'current_task', 'current_slice', 'current_runtime_slice', 'current_audit', 'current_audit_slice', 'packaged_bundle_filename', 'package_filename']);
const PRIMARY_CURRENT_SCRIPTS = new Set(['test:current', 'test:browser:current', 'test:browser-current', 'audit:current', 'package:current']);
const DEFAULT_OUT = `artifacts/audit/${PFX}-CURRENT-OFFICE-AUDIT.json`;
const argValue = (argv, flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };
async function text(path) { return await readFile(path, 'utf8'); }
async function json(path) { return JSON.parse(await text(path)); }
function includeAll(label, value, needles) {
  const missing = needles.filter((needle) => !String(value).includes(needle));
  assert.deepEqual(missing, [], `${label} missing ${missing.join(', ')}`);
  return { label, status: 'passed', needles: needles.length };
}
function rejectAny(label, value, needles) {
  const hits = needles.filter((needle) => String(value).includes(needle));
  assert.deepEqual(hits, [], `${label} contains stale needles ${hits.join(', ')}`);
  return { label, status: 'passed', rejectedNeedles: needles.length };
}
function packageScriptChecks(pkg) {
  const checks = [];
  const scripts = pkg.scripts || {};
  for (const name of PRIMARY_CURRENT_SCRIPTS) assert.ok(scripts[name], `missing primary current script ${name}`);
  checks.push(includeAll('script:test:current', scripts['test:current'], [RELEASE_TASK, AUDIT_TASK, `${PFX}-OPFS-BLOCK-STORE-RAW-COMPOSITE-ABORT-SIGNAL-RUN.json`]));
  checks.push(includeAll('script:test:browser:current', scripts['test:browser:current'], ['tools/run_browser_bundle.mjs', '--mode current', `${PFX}-BROWSER-OPFS-BLOCK-STORE-RAW-COMPOSITE-ABORT-SIGNAL-RUN.json`]));
  checks.push(includeAll('script:test:browser-current', scripts['test:browser-current'], ['tools/run_browser_bundle.mjs', '--mode current', `${PFX}-BROWSER-OPFS-BLOCK-STORE-RAW-COMPOSITE-ABORT-SIGNAL-RUN.json`]));
  assert.ok(!/--id\s+/.test(String(scripts['test:browser:current'])), 'test:browser:current must not use a hand-maintained --id subset');
  assert.ok(!/--id\s+/.test(String(scripts['test:browser-current'])), 'test:browser-current must not use a hand-maintained --id subset');
  checks.push(includeAll('script:audit:current', scripts['audit:current'], ['tools/opfs_block_store_raw_composite_abort_signal_contract_audit.mjs', `${PFX}-OPFS-BLOCK-STORE-RAW-COMPOSITE-ABORT-SIGNAL-CONTRACT-AUDIT.json`, 'current_office_audit.mjs', `${PFX}-CURRENT-OFFICE-AUDIT.json`]));
  checks.push(includeAll('script:package:current', scripts['package:current'], [PACKAGE_SLUG, '--reuse-validation']));
  for (const [name, body] of Object.entries(scripts)) {
    if (name.includes('current') && !PRIMARY_CURRENT_SCRIPTS.has(name)) {
      throw new Error(`non-primary npm script still uses current in its name: ${name}; rename historical shortcuts to replay:*`);
    }
    for (const hit of String(body).match(/REV\d{4}-/g) || []) {
      assert.equal(hit, `${PFX}-`, `npm script ${name} generated-artifact prefix`);
    }
    if (PRIMARY_CURRENT_SCRIPTS.has(name)) {
      checks.push(rejectAny(`script:${name}:stale-current-needles`, body, ['provenance-binding', 'replay-guard', 'expected-fingerprint', 'strict-option', 'owned-rollback', 'owned-rollback', 'WEB-LOCK-STRICT-OPTION', 'OPFS-BLOCK-STORE-ABORT-SIGNAL', 'OPFS-BLOCK-STORE-OWNED-ROLLBACK-GUARD', 'OPFS-BLOCK-STORE-WRITE-BUDGET-DUPLICATE-BYPASS', 'OPFS-BLOCK-STORE-ROLLBACK-VALID-BLOCK-PRESERVE', 'write-budget-duplicate-bypass-current-proof', 'readonly-no-create-current-proof', 'block-store-lane-provider-options-current-proof', 'provider-timeout-abort-current-proof', 'web-lock-guarded-abort-signal-current-proof', 'WEB-LOCK-GUARDED-ABORT-SIGNAL', 'REV0089', 'REV0090', 'REV0091', 'REV0092', 'REV0093', 'REV0094', 'REV0095', 'REV0096', 'REV0097', 'REV0098', 'REV0099', 'REV0100', 'REV0101', 'REV0102', 'REV0103', 'REV0104', 'REV0105', 'REV0106', 'REV0106', 'REV0106']));
    }
  }
  assert.ok(Array.isArray(pkg.carried_forward_audit_anchors), 'package.json.carried_forward_audit_anchors must be an array');
  assert.ok(pkg.carried_forward_audit_anchors.length <= 16, `package.json.carried_forward_audit_anchors must be compact pointers, got ${pkg.carried_forward_audit_anchors.length}`);
  checks.push({ label: 'script-generated-artifact-prefixes-current', status: 'passed', scriptCount: Object.keys(scripts).length });
  checks.push({ label: 'package-carried-forward-anchor-budget', status: 'passed', anchorCount: pkg.carried_forward_audit_anchors.length, maximum: 16 });
  assert.ok(scripts['replay:quarantine-status-transition-import'], 'missing replay:quarantine-status-transition-import');
  assert.ok(scripts['replay:quarantine-receipt-restore-integrity'], 'missing replay:quarantine-receipt-restore-integrity');
  assert.ok(scripts['replay:quarantine-clearance-receipt-provenance-binding'], 'missing replay:quarantine-clearance-receipt-provenance-binding');
  checks.push({ label: 'historical-current-aliases-renamed-to-replay', status: 'passed', replayScripts: 3 });
  return checks;
}
function assertHotFieldNoStale(label, key, value) {
  if (value == null) return;
  const textValue = JSON.stringify(value);
  const hits = HOT_FIELD_STALE_NEEDLES.filter((needle) => textValue.includes(needle));
  assert.deepEqual(hits, [], `${label}.${key} contains stale hot-field needles ${hits.join(', ')}`);
}
function assertArrayIncludes(label, key, value, needles) {
  assert.ok(Array.isArray(value), `${label}.${key} must be an array`);
  for (const needle of needles) assert.ok(value.includes(needle), `${label}.${key} missing ${needle}`);
}
function assertSummaryNamesCurrentSlice(label, key, value) {
  if (typeof value !== 'string' || !value.trim()) return;
  assert.ok(CURRENT_SUMMARY_NEEDLES.some((needle) => value.includes(needle)), `${label}.${key} does not name the current raw OPFS composite AbortSignal slice`);
}
function assertCommandListNamesCurrentSlice(label, key, value) {
  if (value == null) return;
  const body = JSON.stringify(value);
  for (const needle of CURRENT_COMMAND_NEEDLES) assert.ok(body.includes(needle), `${label}.${key} missing current command needle ${needle}`);
  assertHotFieldNoStale(label, key, value);
}
function metadataChecks(label, obj, { packageStamp = null } = {}) {
  const checks = [];
  assert.equal(obj.revision, REVISION, `${label}.revision`);
  assert.equal(obj.version, VERSION, `${label}.version`);
  assert.equal(obj.codename, CODENAME, `${label}.codename`);
  assert.equal(obj.package_slug, PACKAGE_SLUG, `${label}.package_slug`);
  assert.equal(obj.current_task, BROWSER_TASK, `${label}.current_task`);
  assert.equal(obj.current_audit, AUDIT_TASK, `${label}.current_audit`);
  if (obj.current_surface !== undefined) assert.equal(obj.current_surface, CURRENT_SURFACE, `${label}.current_surface`);
  if (obj.current_surfaces !== undefined) assertArrayIncludes(label, 'current_surfaces', obj.current_surfaces, CURRENT_SURFACE_IDS);
  if (obj.current_surface_ids !== undefined) assertArrayIncludes(label, 'current_surface_ids', obj.current_surface_ids, CURRENT_SURFACE_IDS);
  if (obj.must_read !== undefined) assertArrayIncludes(label, 'must_read', obj.must_read, CURRENT_HOT_PATHS);
  if (obj.changed !== undefined) assertArrayIncludes(label, 'changed', obj.changed, CURRENT_HOT_PATHS);
  if (obj.added !== undefined) assertArrayIncludes(label, 'added', obj.added, CURRENT_HOT_PATHS.slice(3));
  for (const key of ['current_surface', 'current_surfaces', 'current_surface_ids', 'current_focus', 'summary', 'description', 'package_summary', 'summary_highlight', 'next_recommended_slice', 'next_recommended_task', 'next_slice_reminder', 'must_read', 'changed', 'added', 'current_commands', 'current_validation_commands', 'last_verified_commands', 'validation_commands', 'package_commands']) assertHotFieldNoStale(label, key, obj[key]);
  for (const key of ['summary', 'package_summary', 'summary_highlight']) assertSummaryNamesCurrentSlice(label, key, obj[key]);
  for (const key of ['current_commands', 'current_validation_commands', 'last_verified_commands', 'validation_commands']) assertCommandListNamesCurrentSlice(label, key, obj[key]);
  const localPackageStamp = obj.package_stamp ?? packageStamp;
  if (packageStamp && obj.package_stamp !== undefined) assert.equal(obj.package_stamp, packageStamp, `${label}.package_stamp`);
  const filenameKeys = ['filename', 'packaged_bundle_filename', 'package_filename', 'package_files', 'packageFileName', 'package_file_name'];
  for (const key of filenameKeys) {
    if (obj[key] == null) continue;
    const value = String(obj[key]);
    assert.ok(value.includes(PACKAGE_SLUG), `${label}.${key} missing package slug`);
    assert.ok(value.includes(REVISION), `${label}.${key} missing revision`);
    if (localPackageStamp) assert.ok(value.includes(localPackageStamp), `${label}.${key} missing package stamp ${localPackageStamp}`);
    assert.ok(!/rev009[0-8]/.test(value) && !/write-budget-guard-current-proof|open-failure-recovery-current-proof|write-budget-duplicate-bypass-current-proof|rollback-valid-block-preserve-current-proof|storage-lane-composite-abort-signal-current-proof|web-lock-guarded-abort-signal-current-proof/.test(value), `${label}.${key} is stale: ${value}`);
  }
  if (obj.package_commands != null) {
    const commandBody = JSON.stringify(obj.package_commands);
    assert.ok(commandBody.includes(PACKAGE_SLUG), `${label}.package_commands missing package slug`);
    if (localPackageStamp) assert.ok(commandBody.includes(`--timestamp ${localPackageStamp}`), `${label}.package_commands missing package stamp ${localPackageStamp}`);
  }
  if (obj.browserrt_current) {
    assert.equal(obj.browserrt_current.revision, REVISION, `${label}.browserrt_current.revision`);
    assert.equal(obj.browserrt_current.version, VERSION, `${label}.browserrt_current.version`);
    assert.equal(obj.browserrt_current.codename, CODENAME, `${label}.browserrt_current.codename`);
    assert.equal(obj.browserrt_current.release_task, RELEASE_TASK, `${label}.browserrt_current.release_task`);
    assert.equal(obj.browserrt_current.browser_task, BROWSER_TASK, `${label}.browserrt_current.browser_task`);
    assert.equal(obj.browserrt_current.audit_task, AUDIT_TASK, `${label}.browserrt_current.audit_task`);
    assert.equal(obj.browserrt_current.package_slug, PACKAGE_SLUG, `${label}.browserrt_current.package_slug`);
  }
  for (const key of ['current_commands', 'current_validation_commands', 'last_verified_commands', 'validation_commands', 'package_commands']) {
    for (const command of obj[key] || []) {
      assert.ok(!/REV00(89|90|91|92|93|94|95|96|97|98|99)-/.test(command) && !/REV0100-|REV0101-|REV0102-|REV0103-|REV0104-|REV0105-|REV0106-/.test(command), `${label}.${key} contains stale revision: ${command}`);
      assert.ok(!/provenance-binding|replay-guard|expected-fingerprint|strict-option|owned-rollback|write-budget-duplicate-bypass|rollback-valid-block-preserve|readonly-no-create|block-store-lane-provider-options|provider-timeout-abort|storage-lane-composite-abort-signal|web-lock-guarded-abort-signal/.test(command), `${label}.${key} contains stale slice: ${command}`);
    }
  }
  checks.push({ label: `${label}:current-office-fields`, status: 'passed', filenameKeysChecked: filenameKeys.length, browserrtCurrentChecked: Boolean(obj.browserrt_current) });
  checks.push({ label: `${label}:metadata-hot-fields-current`, status: 'passed', currentSurface: obj.current_surface ?? null, hotPathsChecked: CURRENT_HOT_PATHS.length });
  return checks;
}

export async function runAudit() {
  const started = performance.now();
  const pkg = await json('package.json');
  const makefile = await text('Makefile');
  const browserBundle = await text('tools/run_browser_bundle.mjs');
  const manifest = await json('test/manifest.json');
  const metaFiles = ['CUBE-META.json', 'REVISION-RECEIPT.json', 'REENTRY-CONTRACT.json', 'SURFACE-STATUS.json', 'VALIDATION-INDEX.json'];
  const checks = [];
  checks.push(...packageScriptChecks(pkg));
  checks.push(includeAll('browser-bundle-runner:current-office-raw-task', browserBundle, [BROWSER_TASK, 'CURRENT_TASKS', 'BATCH_LAYOUT']));
  checks.push(...metadataChecks('package.json', pkg, { packageStamp: pkg.package_stamp ?? null }));
  function targetBlocks(body, names) {
    const lines = body.split('\n');
    const blocks = [];
    let capture = false;
    let current = [];
    for (const line of lines) {
      const match = /^([A-Za-z0-9_.:-]+):/.exec(line);
      if (match) {
        if (capture) blocks.push(current.join('\n'));
        capture = names.includes(match[1]);
        current = capture ? [line] : [];
      } else if (capture) {
        current.push(line);
      }
    }
    if (capture) blocks.push(current.join('\n'));
    return blocks.join('\n');
  }
  const currentMakeTargets = targetBlocks(makefile, ['current', 'browser', 'release', 'audit', 'package', 'verify']);
  checks.push(includeAll('makefile:current-targets', currentMakeTargets + '\n' + makefile, [RELEASE_TASK, BROWSER_TASK, AUDIT_TASK, PACKAGE_SLUG, 'ZIP ?=', 'current_office_audit.mjs', 'opfs_block_store_raw_composite_abort_signal_contract_audit.mjs']));
  checks.push(rejectAny('makefile:primary-targets-stale-needles', currentMakeTargets, ['REV0089', 'REV0090', 'REV0091', 'REV0092', 'REV0093', 'REV0094', 'REV0095', 'REV0096', 'REV0097', 'REV0098', 'REV0099', 'REV0100', 'REV0101', 'REV0102', 'REV0103', 'REV0104', 'REV0105', 'REV0106', 'REV0106', 'provenance-binding', 'replay-guard', 'expected-fingerprint', 'strict-option', 'owned-rollback', 'write-budget-duplicate-bypass', 'rollback-valid-block-preserve', 'web-lock-guarded-abort-signal']));
  for (const file of metaFiles) checks.push(...metadataChecks(file, await json(file), { packageStamp: pkg.package_stamp ?? null }));
  for (const file of ['AGENTS.md', 'CONTEXT-PACK.md']) {
    const body = await text(file);
    const declarations = [...body.matchAll(/current office remains (rev\d{4})/gi)].map((match) => match[1].toLowerCase());
    assert.ok(declarations.length > 0, `${file} must state the current office explicitly`);
    assert.ok(declarations.every((revision) => revision === REVISION), `${file} carries stale current-office declarations: ${declarations.join(', ')}`);
    checks.push({ label: `${file}:current-office-declaration`, status: 'passed', declarations });
  }
  for (const file of ['artifacts/research/RELATED-WORK-SOURCE-REGISTRY.json', 'artifacts/research/TEST-FACILITY-RESEARCH-REGISTRY.json']) {
    const registry = await json(file);
    assert.equal(registry.revision, REVISION, `${file}.revision`);
    assert.equal(registry.version, VERSION, `${file}.version`);
    assert.equal(registry.registry_status, 'research-registry-not-current-office', `${file}.registry_status`);
    const present = RESEARCH_REGISTRY_FORBIDDEN_HOT_KEYS.filter((key) => Object.hasOwn(registry, key));
    assert.deepEqual(present, [], `${file} carries forbidden current-office aliases: ${present.join(', ')}`);
    checks.push({ label: `${file}:research-metadata-scope`, status: 'passed', forbiddenKeysChecked: RESEARCH_REGISTRY_FORBIDDEN_HOT_KEYS.length });
  }
  for (const task of manifest.tasks || []) {
    const command = (task.command || []).join(' ');
    for (const hit of command.match(/REV\d{4}-/g) || []) assert.equal(hit, `${PFX}-`, `${task.id} command output prefix`);
    for (const output of task.outputs || []) for (const hit of String(output).match(/REV\d{4}-/g) || []) assert.equal(hit, `${PFX}-`, `${task.id} output prefix`);
  }
  checks.push({ label: 'manifest-output-prefixes-current', status: 'passed', tasks: (manifest.tasks || []).length });
  const currentNamedScripts = Object.keys(pkg.scripts || {}).filter((name) => name.includes('current'));
  return Object.freeze({ project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1, task_id: 'facility:current-office-command-surface-audit', status: 'passed', generatedAt: new Date().toISOString(), durationMs: Math.round(performance.now() - started), codename: CODENAME, package_slug: PACKAGE_SLUG, current_scripts: currentNamedScripts, checks, purpose: 'Fail fast when human-facing current commands, first-read declarations, research-registry scope, package metadata budgets, central metadata, package slug, or manifest output prefixes drift away from the actual current BrowserRT proof slice.', nonClaims: ['Current-office audit only; runtime/browser probes supply storage evidence.', 'Replay scripts remain available as explicit historical shortcuts but may not masquerade as current aliases.'] });
}

const argv = process.argv.slice(2);
const out = argValue(argv, '--json', DEFAULT_OUT);
try {
  const report = await runAudit();
  if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); console.log(out); } else console.log(JSON.stringify(report, null, 2));
} catch (error) {
  const report = { project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1, task_id: 'facility:current-office-command-surface-audit', status: 'failed', generatedAt: new Date().toISOString(), error: { name: error?.name || 'Error', message: error?.message || String(error), stack: error?.stack } };
  if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); console.error(out); }
  console.error(`[current_office_audit] FAIL: ${error?.stack || error}`);
  process.exitCode = 1;
}
