#!/usr/bin/env node
import assert from 'node:assert/strict';
import { readFile, writeFile, mkdir } from 'node:fs/promises';
import { dirname } from 'node:path';
import { performance } from 'node:perf_hooks';
import { REVISION, VERSION } from '../src/browserrt.mjs';

const PFX = `REV${REVISION.slice(3)}`;
const DEFAULT_OUT = `artifacts/audit/${PFX}-WEB-LOCK-STRICT-OPTION-GUARD-CONTRACT-AUDIT.json`;
const RELEASE_TASK = 'coord:web-lock-strict-option-guard-proof';
const BROWSER_TASK = 'browser:opfs-web-lock-strict-option-guard-proof';
const AUDIT_TASK = 'facility:web-lock-strict-option-guard-contract-audit';
const argValue = (argv, flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };
async function text(path) { return await readFile(path, 'utf8'); }
async function json(path) { return JSON.parse(await text(path)); }
function missingNeedles(body, needles) { return needles.filter((needle) => !String(body).includes(needle)); }
function check(checks, label, condition, detail = {}) {
  checks.push({ label, status: condition ? 'passed' : 'failed', ...detail });
  assert.equal(condition, true, `${label} failed: ${JSON.stringify(detail)}`);
}
function taskById(manifest, id) { return (manifest.tasks || []).find((task) => task.id === id); }

export async function runAudit() {
  const started = performance.now();
  const checks = [];
  const files = {
    coordinator: await text('src/web-lock-coordinator.mjs'),
    types: await text('src/types.d.ts'),
    releaseProbe: await text('tools/web_lock_strict_option_guard_probe.mjs'),
    browserProbe: await text('tools/browser_opfs_web_lock_strict_option_guard_probe.mjs'),
    audit: await text('tools/web_lock_strict_option_guard_contract_audit.mjs'),
    releaseDoc: await text('docs/40-validation/web-lock-strict-option-guard-slice.md'),
    browserDoc: await text('docs/40-validation/browser-opfs-web-lock-strict-option-guard-slice.md'),
    auditDoc: await text('docs/40-validation/web-lock-strict-option-guard-contract-audit-slice.md'),
    packageJson: await text('package.json'),
    makefile: await text('Makefile')
  };
  const manifest = await json('test/manifest.json');
  const impact = await json('test/impact-map.json');
  const surface = await json('test/surface-inventory.json');

  check(checks, 'runtime-strict-option-guards-present', missingNeedles(files.coordinator, [
    'BRT_WEB_LOCK_OPTION_TYPE',
    'BRT_WEB_LOCK_OPTION_CONFLICT',
    'BRT_WEB_LOCK_SIGNAL_INVALID',
    'BRT_WEB_LOCK_NAME_INVALID',
    'BRT_WEB_LOCK_MODE_INVALID',
    'coord:web-lock-option-rejected',
    'cleanOptionalBooleanOption',
    'validateLockOptionCombinations',
    'ifAvailable === true && steal === true',
    "steal === true && mode !== 'exclusive'",
    'signal === undefined || signal === null'
  ]).length === 0, { missing: missingNeedles(files.coordinator, ['BRT_WEB_LOCK_OPTION_TYPE','BRT_WEB_LOCK_OPTION_CONFLICT','BRT_WEB_LOCK_SIGNAL_INVALID','BRT_WEB_LOCK_NAME_INVALID','BRT_WEB_LOCK_MODE_INVALID','coord:web-lock-option-rejected','cleanOptionalBooleanOption','validateLockOptionCombinations']) });
  check(checks, 'runtime-no-boolean-string-coercion', !files.coordinator.includes('Boolean(ifAvailable)') && !files.coordinator.includes('Boolean(steal)'), { rejected: ['Boolean(ifAvailable)', 'Boolean(steal)'] });
  check(checks, 'runtime-name-validated-before-includes', files.coordinator.includes('const baseName = cleanLockName(name);') && files.coordinator.includes('baseName.includes'), { purpose: 'avoid name.includes TypeError before BrowserRT error surface' });
  check(checks, 'types-web-lock-options-remain-boolean', missingNeedles(files.types, ['ifAvailable?: boolean', 'steal?: boolean', 'signal?: AbortSignal']).length === 0, { missing: missingNeedles(files.types, ['ifAvailable?: boolean', 'steal?: boolean', 'signal?: AbortSignal']) });
  check(checks, 'release-probe-invalid-and-valid-paths', missingNeedles(files.releaseProbe, ['ifAvailable-string-false', 'steal-string-false', 'ifAvailable-plus-steal', 'shared-plus-steal', 'plain-object-signal', 'null-signal-treated-as-absent-for-adapter-compat', 'locks.calls.length, 0', 'optionRejected']).length === 0, { missing: missingNeedles(files.releaseProbe, ['ifAvailable-string-false','steal-string-false','ifAvailable-plus-steal','shared-plus-steal','plain-object-signal','optionRejected']) });
  check(checks, 'browser-probe-real-realm-and-opfs-paths', missingNeedles(files.browserProbe, ['runManagedBrowserPage', 'navigator.locks?.request', 'opfsAsyncBlockStore', 'opfsWebLockGuardedBlockStore', 'plain-object-signal', 'signal-plus-ifAvailable', 'storage:opfs-block-put', 'navigator.locks?.query']).length === 0, { missing: missingNeedles(files.browserProbe, ['runManagedBrowserPage','navigator.locks?.request','opfsAsyncBlockStore','opfsWebLockGuardedBlockStore','plain-object-signal','storage:opfs-block-put']) });
  for (const [label, body] of [['release-doc', files.releaseDoc], ['browser-doc', files.browserDoc], ['audit-doc', files.auditDoc]]) {
    check(checks, `${label}-nonclaims-visible`, missingNeedles(body.toLowerCase(), ['cross-browser', 'quota', 'eviction', 'crash']).length === 0, { missing: missingNeedles(body.toLowerCase(), ['cross-browser', 'quota', 'eviction', 'crash']) });
  }

  const releaseTask = taskById(manifest, RELEASE_TASK);
  const browserTask = taskById(manifest, BROWSER_TASK);
  const auditTask = taskById(manifest, AUDIT_TASK);
  check(checks, 'manifest-release-task-wired', Boolean(releaseTask) && (releaseTask.tiers || []).includes('release') && (releaseTask.command || []).join(' ').includes(`artifacts/validation/${PFX}-WEB-LOCK-STRICT-OPTION-GUARD-PROBE.json`), { task: releaseTask?.id ?? null });
  check(checks, 'manifest-browser-task-wired', Boolean(browserTask) && (browserTask.tiers || []).includes('browser') && (browserTask.command || []).join(' ').includes(`artifacts/validation/${PFX}-BROWSER-OPFS-WEB-LOCK-STRICT-OPTION-GUARD-PROBE.json`), { task: browserTask?.id ?? null });
  check(checks, 'manifest-audit-task-wired', Boolean(auditTask) && (auditTask.tiers || []).includes('release') && (auditTask.command || []).join(' ').includes(`artifacts/audit/${PFX}-WEB-LOCK-STRICT-OPTION-GUARD-CONTRACT-AUDIT.json`), { task: auditTask?.id ?? null });
  const impacted = JSON.stringify(impact);
  check(checks, 'impact-map-routes-web-lock-coordinator', impacted.includes('impact:web-lock-strict-option-guard') && impacted.includes(RELEASE_TASK) && impacted.includes(BROWSER_TASK) && impacted.includes(AUDIT_TASK), { rule: 'impact:web-lock-strict-option-guard' });
  const surfaced = JSON.stringify(surface);
  check(checks, 'surface-inventory-strict-option-surfaces', surfaced.includes('surface:web-lock-strict-option-guard') && surfaced.includes('surface:browser-opfs-web-lock-strict-option-guard') && surfaced.includes('surface:web-lock-strict-option-guard-contract-audit'), { surfaces: 3 });
  const packageData = JSON.parse(files.packageJson);
  const packageCurrentOrCarried = (packageData.current_task === BROWSER_TASK && packageData.current_audit === AUDIT_TASK)
    || ((packageData.carried_forward_browser_proofs || []).includes(BROWSER_TASK) && (packageData.carried_forward_audits || []).includes(AUDIT_TASK))
    || (files.packageJson.includes('test:web-lock-strict-option-guard') && files.packageJson.includes('test:browser:opfs-web-lock-strict-option-guard') && files.packageJson.includes('audit:web-lock-strict-option-guard'));
  check(checks, 'package-scripts-current-or-carried-strict-option-slice', packageCurrentOrCarried, { currentSlice: packageData.current_task, audit: packageData.current_audit });
  const makefileCurrentOrCarried = files.makefile.includes(RELEASE_TASK) && files.makefile.includes(BROWSER_TASK) && files.makefile.includes(AUDIT_TASK);
  check(checks, 'makefile-current-or-carried-strict-option-slice', makefileCurrentOrCarried || packageCurrentOrCarried, { currentSlice: packageData.current_task, note: 'top-level Makefile may be reserved for current office after handoff' });

  return {
    project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1,
    task_id: AUDIT_TASK, status: 'passed', generatedAt: new Date().toISOString(), durationMs: Math.round(performance.now() - started),
    purpose: 'Contract audit for the WebLockCoordinator strict option/name/signal guard slice, including runtime implementation, release proof, browser proof, docs, manifest, impact map, surface inventory, package scripts, and Makefile current office.',
    checks,
    nonClaims: ['Static/current-office audit only; runtime and managed Chromium probes supply behavior evidence.', 'No cross-browser, OPFS durability, quota, eviction, crash recovery, cryptographic attestation, fairness, or production readiness claim.']
  };
}

const out = argValue(process.argv.slice(2), '--json', DEFAULT_OUT);
try {
  const report = await runAudit();
  if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); console.log(out); }
  else console.log(JSON.stringify(report, null, 2));
} catch (error) {
  const report = { project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1, task_id: AUDIT_TASK, status: 'failed', generatedAt: new Date().toISOString(), error: { name: error?.name || 'Error', message: error?.message || String(error), stack: error?.stack } };
  if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); console.error(out); }
  console.error(`[web_lock_strict_option_guard_contract_audit] FAIL: ${error?.stack || error}`);
  process.exitCode = 1;
}
