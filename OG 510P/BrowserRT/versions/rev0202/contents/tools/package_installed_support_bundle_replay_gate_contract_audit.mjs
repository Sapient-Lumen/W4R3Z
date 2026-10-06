#!/usr/bin/env node
// Manifest slice: facility:package-installed-support-bundle-replay-gate-audit. Static contract audit for installed support-bundle replay gate.
import assert from 'node:assert/strict';
import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import { REVISION, VERSION } from '../src/public-api.mjs';

const REVISION_PREFIX = `REV${REVISION.slice(3)}`;
const DEFAULT_OUT = `artifacts/audit/${REVISION_PREFIX}-PACKAGE-INSTALLED-SUPPORT-BUNDLE-REPLAY-GATE-CONTRACT-AUDIT.json`;
const argValue = (argv, flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };
const readJson = async (path) => JSON.parse(await readFile(path, 'utf8'));

function missing(text, needles) {
  return needles.filter((needle) => !String(text).includes(needle));
}

function check(name, ok, details = {}) {
  return Object.freeze({ name, status: ok ? 'passed' : 'failed', ...details });
}

export async function runAudit() {
  const pkg = await readJson('package.json');
  const manifest = await readJson('test/manifest.json');
  const runtimeText = await readFile('src/browserrt.mjs', 'utf8');
  const typesText = await readFile('src/types.d.ts', 'utf8');
  const publicAuditText = await readFile('tools/public_api_contract_audit.mjs', 'utf8');
  const smokeText = await readFile('tools/package_installed_consumer_smoke_probe.mjs', 'utf8');
  const probeText = await readFile('tools/package_installed_support_bundle_replay_gate_probe.mjs', 'utf8');
  const exampleText = await readFile('examples/support-bundle-replay-consumer.mjs', 'utf8');
  const taskIds = new Set((manifest.tasks || []).map((task) => task.id));
  const taskById = (id) => (manifest.tasks || []).find((task) => task.id === id) || {};
  const productTask = taskById('product:package-installed-support-bundle-replay-gate-proof');
  const facilityTask = taskById('facility:package-installed-support-bundle-replay-gate-audit');

  const checks = [
    check('runtime-diagnostics-exposes-operator-replay-gate', missing(runtimeText, [
      'kernelKitSupportBundleOperatorPreflightDisplaySnapshot(input = {}, fields = {})',
      'validateKernelKitSupportBundleOperatorPreflightDisplaySnapshot(report)',
      'kernelKitSupportBundleOperatorReplayGate(input = {}, fields = {})',
      'validateKernelKitSupportBundleOperatorReplayGate(report)',
      "'kernelKitSupportBundleOperatorReplayGate'",
      "'kernelKitSupportBundleOperatorPreflightDisplaySnapshot'"
    ]).length === 0),
    check('types-declare-runtime-and-diagnostics-operator-replay-gate', missing(typesText, [
      "| 'kernelKitSupportBundleOperatorPreflightDisplaySnapshot'",
      "| 'validateKernelKitSupportBundleOperatorPreflightDisplaySnapshot'",
      "| 'kernelKitSupportBundleOperatorReplayGate'",
      "| 'validateKernelKitSupportBundleOperatorReplayGate'",
      'kernelKitSupportBundleOperatorPreflightDisplaySnapshot(input?: Record<string, unknown>, fields?: Record<string, unknown>): KernelKitSupportBundleOperatorPreflightDisplaySnapshot;',
      'kernelKitSupportBundleOperatorReplayGate(input?: Record<string, unknown>, fields?: Record<string, unknown>): KernelKitSupportBundleOperatorReplayGate;'
    ]).length === 0),
    check('installed-example-uses-package-root-runtime-diagnostics', missing(exampleText, [
      'runSupportBundleReplayWithApi',
      'boot({ telemetry: \'support-bundle-replay-consumer\'',
      'rt.diagnostics.kernelKitSupportBundle(',
      'rt.diagnostics.kernelKitSupportBundleReplayPlan(',
      'rt.diagnostics.kernelKitSupportBundleOperatorPreflightDisplaySnapshot(',
      'rt.diagnostics.kernelKitSupportBundleOperatorReplayGate(',
      'validateSupportBundleReplayConsumerReport',
      'noCommandsExecuted'
    ]).length === 0 && !/kernel-kit-demo\.mjs|\.\.\/src\/browserrt\.mjs/.test(exampleText)),
    check('package-installed-probe-installs-tarball-and-imports-example', missing(probeText, [
      'preparePackageTarballForProbe',
      'npm install',
      "import * as api from 'browserrt';",
      "./node_modules/browserrt/examples/support-bundle-replay-consumer.mjs",
      'examples/support-bundle-replay-consumer.mjs',
      'operatorReplayGateReady',
      'hiddenRowsCarryCanonicalDisplayFields'
    ]).length === 0 && !/\.\.\/src\/kernel-kit-demo\.mjs/.test(probeText)),
    check('installed-smoke-typecheck-covers-new-runtime-methods', missing(smokeText, [
      'runtime.diagnostics.kernelKitSupportBundleOperatorPreflightDisplaySnapshot',
      'runtime.diagnostics.kernelKitSupportBundleOperatorReplayGate',
      'runtime.kernelKitSupportBundleOperatorPreflightDisplaySnapshot',
      'runtime.validateKernelKitSupportBundleOperatorReplayGate',
      'examples/support-bundle-replay-consumer.mjs',
      'declarationMethodNames.length, 113'
    ]).length === 0),
    check('package-files-include-examples-glob', Array.isArray(pkg.files) && pkg.files.includes('examples/*.mjs') && !pkg.files.includes('tools/**') && !pkg.files.includes('artifacts/**')),
    check('scripts-register-package-installed-replay-gate', String(pkg.scripts?.['test:package-installed-support-bundle-replay-gate'] || '').includes('tools/package_installed_support_bundle_replay_gate_probe.mjs') && String(pkg.scripts?.['audit:package-installed-support-bundle-replay-gate'] || '').includes('tools/package_installed_support_bundle_replay_gate_contract_audit.mjs')),
    check('manifest-registers-product-and-facility-tasks', taskIds.has('product:package-installed-support-bundle-replay-gate-proof') && taskIds.has('facility:package-installed-support-bundle-replay-gate-audit'), {
      productTaskPresent: taskIds.has('product:package-installed-support-bundle-replay-gate-proof'),
      facilityTaskPresent: taskIds.has('facility:package-installed-support-bundle-replay-gate-audit')
    }),
    check('manifest-product-task-invalidates-package-runtime-types-example',
      Array.isArray(productTask.inputs) && ['package.json','src/*.mjs','src/*.d.ts','examples/support-bundle-replay-consumer.mjs','tools/package_installed_support_bundle_replay_gate_probe.mjs'].every((item) => productTask.inputs.includes(item)) &&
      Array.isArray(productTask.outputs) && productTask.outputs.includes(`artifacts/validation/${REVISION_PREFIX}-PACKAGE-INSTALLED-SUPPORT-BUNDLE-REPLAY-GATE-PROBE.json`) &&
      Array.isArray(productTask.requiredEvidence) && productTask.requiredEvidence.some((item) => /installed package/i.test(item)) && productTask.requiredEvidence.some((item) => /operator replay gate/i.test(item))
    ),
    check('manifest-facility-task-locks-contract-audit',
      Array.isArray(facilityTask.inputs) && ['src/browserrt.mjs','src/types.d.ts','examples/support-bundle-replay-consumer.mjs','tools/package_installed_support_bundle_replay_gate_probe.mjs'].every((item) => facilityTask.inputs.includes(item)) &&
      Array.isArray(facilityTask.outputs) && facilityTask.outputs.includes(`artifacts/audit/${REVISION_PREFIX}-PACKAGE-INSTALLED-SUPPORT-BUNDLE-REPLAY-GATE-CONTRACT-AUDIT.json`)
    ),
    check('public-api-contract-audit-knows-replay-gate-example', missing(publicAuditText, [
      'support-bundle-replay-consumer.mjs',
      'kernelKitSupportBundleOperatorReplayGate',
      'product:package-installed-support-bundle-replay-gate-proof'
    ]).length === 0)
  ];

  const failed = checks.filter((row) => row.status !== 'passed');
  assert.deepEqual(failed.map((row) => row.name), [], `package-installed support-bundle replay gate contract failed: ${failed.map((row) => row.name).join(', ')}`);
  return Object.freeze({
    project: 'BrowserRT',
    revision: REVISION,
    version: VERSION,
    schema: 1,
    status: 'passed',
    audit_id: `${REVISION}-package-installed-support-bundle-replay-gate-contract-audit`,
    purpose: 'Static audit that the installed-package support-bundle replay gate is reachable through boot() diagnostics, typed in BrowserRTRuntime, packaged as an example, proven through local npm install, and registered in the manifest without opening internal/development surfaces.',
    checks,
    nonClaims: Object.freeze([
      'This audit checks local source, declaration, package, and manifest wiring only; it does not publish a package, run browser OPFS, reserve quota, survive eviction, prove cross-browser behavior, or prove production retry safety.',
      'The operator replay gate remains display/package-consumer gating only and does not execute commands, repair storage, grant quota, preserve Service Worker lifetime, or prove Web Lock fairness.'
    ])
  });
}

if (import.meta.url === `file://${process.argv[1]}`) {
  const out = argValue(process.argv.slice(2), '--json', DEFAULT_OUT);
  try {
    const report = await runAudit();
    await mkdir(dirname(out), { recursive: true });
    await writeFile(out, JSON.stringify(report, null, 2) + '\n');
    console.log(out);
  } catch (error) {
    const report = { project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1, status: 'failed', audit_id: `${REVISION}-package-installed-support-bundle-replay-gate-contract-audit`, error: { name: error?.name || 'Error', message: error?.message || String(error), stack: error?.stack } };
    await mkdir(dirname(out), { recursive: true });
    await writeFile(out, JSON.stringify(report, null, 2) + '\n');
    console.error(out);
    console.error(`[package_installed_support_bundle_replay_gate_contract_audit] FAIL: ${error?.stack || error}`);
    process.exitCode = 1;
  }
}
