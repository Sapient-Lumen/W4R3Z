#!/usr/bin/env node
import assert from 'node:assert/strict';
import { readFile, writeFile, mkdir } from 'node:fs/promises';
import { dirname } from 'node:path';
import { performance } from 'node:perf_hooks';
import { REVISION, VERSION } from '../src/browserrt.mjs';

const PFX = `REV${REVISION.slice(3)}`;
const CODENAME = 'OPFS Block Store Rollback Valid Block Preserve';
const PACKAGE_SLUG = 'opfs-block-store-rollback-valid-block-preserve-current-proof';
const RELEASE_TASK = 'opfs:block-store-rollback-valid-block-preserve-proof';
const BROWSER_TASK = 'browser:opfs-block-store-rollback-valid-block-preserve-proof';
const AUDIT_TASK = 'facility:opfs-block-store-rollback-valid-block-preserve-contract-audit';
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
  checks.push(includeAll('script:test:current', scripts['test:current'], [RELEASE_TASK, AUDIT_TASK, `${PFX}-OPFS-BLOCK-STORE-ROLLBACK-VALID-BLOCK-PRESERVE-RUN.json`]));
  checks.push(includeAll('script:test:browser:current', scripts['test:browser:current'], [BROWSER_TASK, `${PFX}-BROWSER-OPFS-BLOCK-STORE-ROLLBACK-VALID-BLOCK-PRESERVE-RUN.json`]));
  checks.push(includeAll('script:test:browser-current', scripts['test:browser-current'], [BROWSER_TASK, `${PFX}-BROWSER-OPFS-BLOCK-STORE-ROLLBACK-VALID-BLOCK-PRESERVE-RUN.json`]));
  checks.push(includeAll('script:audit:current', scripts['audit:current'], ['tools/opfs_block_store_rollback_valid_block_preserve_contract_audit.mjs', `${PFX}-OPFS-BLOCK-STORE-ROLLBACK-VALID-BLOCK-PRESERVE-CONTRACT-AUDIT.json`, 'current_office_audit.mjs', `${PFX}-CURRENT-OFFICE-AUDIT.json`]));
  checks.push(includeAll('script:package:current', scripts['package:current'], [PACKAGE_SLUG, '--reuse-validation']));
  for (const [name, body] of Object.entries(scripts)) {
    if (name.includes('current') && !PRIMARY_CURRENT_SCRIPTS.has(name)) {
      throw new Error(`non-primary npm script still uses current in its name: ${name}; rename historical shortcuts to replay:*`);
    }
    for (const hit of String(body).match(/REV\d{4}-/g) || []) {
      assert.equal(hit, `${PFX}-`, `npm script ${name} generated-artifact prefix`);
    }
    if (PRIMARY_CURRENT_SCRIPTS.has(name)) {
      checks.push(rejectAny(`script:${name}:stale-current-needles`, body, ['provenance-binding', 'replay-guard', 'expected-fingerprint', 'strict-option', 'abort-signal', 'owned-rollback', 'abort-signal', 'owned-rollback', 'WEB-LOCK-STRICT-OPTION', 'OPFS-BLOCK-STORE-ABORT-SIGNAL', 'OPFS-BLOCK-STORE-OWNED-ROLLBACK-GUARD', 'OPFS-BLOCK-STORE-WRITE-BUDGET-DUPLICATE-BYPASS', 'write-budget-duplicate-bypass-current-proof', 'REV0089', 'REV0090', 'REV0091', 'REV0092', 'REV0093', 'REV0094', 'REV0095', 'REV0096', 'REV0097', 'REV0098', 'REV0099']));
    }
  }
  checks.push({ label: 'script-generated-artifact-prefixes-current', status: 'passed', scriptCount: Object.keys(scripts).length });
  assert.ok(scripts['replay:quarantine-status-transition-import'], 'missing replay:quarantine-status-transition-import');
  assert.ok(scripts['replay:quarantine-receipt-restore-integrity'], 'missing replay:quarantine-receipt-restore-integrity');
  assert.ok(scripts['replay:quarantine-clearance-receipt-provenance-binding'], 'missing replay:quarantine-clearance-receipt-provenance-binding');
  checks.push({ label: 'historical-current-aliases-renamed-to-replay', status: 'passed', replayScripts: 3 });
  return checks;
}
function metadataChecks(label, obj) {
  const checks = [];
  assert.equal(obj.revision, REVISION, `${label}.revision`);
  assert.equal(obj.version, VERSION, `${label}.version`);
  assert.equal(obj.codename, CODENAME, `${label}.codename`);
  assert.equal(obj.package_slug, PACKAGE_SLUG, `${label}.package_slug`);
  assert.equal(obj.current_task, BROWSER_TASK, `${label}.current_task`);
  assert.equal(obj.current_audit, AUDIT_TASK, `${label}.current_audit`);
  const filenameKeys = ['filename', 'packaged_bundle_filename', 'package_filename', 'package_files', 'packageFileName', 'package_file_name'];
  for (const key of filenameKeys) {
    if (obj[key] == null) continue;
    const value = String(obj[key]);
    assert.ok(value.includes(PACKAGE_SLUG), `${label}.${key} missing package slug`);
    assert.ok(value.includes(REVISION), `${label}.${key} missing revision`);
    assert.ok(!/rev009[0-8]/.test(value) && !/write-budget-guard-current-proof|open-failure-recovery-current-proof|write-budget-duplicate-bypass-current-proof/.test(value), `${label}.${key} is stale: ${value}`);
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
  for (const command of obj.current_commands || []) {
    assert.ok(!/REV00(89|90|91|92|93|94|95|96|97|98|99)-/.test(command), `${label}.current_commands contains stale revision: ${command}`);
    assert.ok(!/provenance-binding|replay-guard|expected-fingerprint|strict-option|abort-signal|owned-rollback|write-budget-duplicate-bypass/.test(command), `${label}.current_commands contains stale slice: ${command}`);
  }
  checks.push({ label: `${label}:current-office-fields`, status: 'passed', filenameKeysChecked: filenameKeys.length, browserrtCurrentChecked: Boolean(obj.browserrt_current) });
  return checks;
}

export async function runAudit() {
  const started = performance.now();
  const pkg = await json('package.json');
  const makefile = await text('Makefile');
  const manifest = await json('test/manifest.json');
  const metaFiles = ['CUBE-META.json', 'REVISION-RECEIPT.json', 'REENTRY-CONTRACT.json', 'SURFACE-STATUS.json', 'VALIDATION-INDEX.json'];
  const checks = [];
  checks.push(...packageScriptChecks(pkg));
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
  checks.push(includeAll('makefile:current-targets', currentMakeTargets + '\n' + makefile, [RELEASE_TASK, BROWSER_TASK, AUDIT_TASK, PACKAGE_SLUG, 'ZIP ?=', 'current_office_audit.mjs', 'opfs_block_store_rollback_valid_block_preserve_contract_audit.mjs']));
  checks.push(rejectAny('makefile:primary-targets-stale-needles', currentMakeTargets, ['REV0089', 'REV0090', 'REV0091', 'REV0092', 'REV0093', 'REV0094', 'REV0095', 'REV0096', 'REV0097', 'REV0098', 'REV0099', 'provenance-binding', 'replay-guard', 'expected-fingerprint', 'strict-option', 'abort-signal', 'owned-rollback', 'write-budget-duplicate-bypass']));
  for (const file of metaFiles) checks.push(...metadataChecks(file, await json(file)));
  for (const task of manifest.tasks || []) {
    const command = (task.command || []).join(' ');
    for (const hit of command.match(/REV\d{4}-/g) || []) assert.equal(hit, `${PFX}-`, `${task.id} command output prefix`);
    for (const output of task.outputs || []) for (const hit of String(output).match(/REV\d{4}-/g) || []) assert.equal(hit, `${PFX}-`, `${task.id} output prefix`);
  }
  checks.push({ label: 'manifest-output-prefixes-current', status: 'passed', tasks: (manifest.tasks || []).length });
  const currentNamedScripts = Object.keys(pkg.scripts || {}).filter((name) => name.includes('current'));
  return Object.freeze({ project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1, task_id: 'facility:current-office-command-surface-audit', status: 'passed', generatedAt: new Date().toISOString(), durationMs: Math.round(performance.now() - started), codename: CODENAME, package_slug: PACKAGE_SLUG, current_scripts: currentNamedScripts, checks, purpose: 'Fail fast when human-facing current commands, Makefile targets, central metadata, package slug, or manifest output prefixes drift away from the actual current BrowserRT proof slice.', nonClaims: ['Current-office audit only; runtime/browser probes supply storage evidence.', 'Replay scripts remain available as explicit historical shortcuts but may not masquerade as current aliases.'] });
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
