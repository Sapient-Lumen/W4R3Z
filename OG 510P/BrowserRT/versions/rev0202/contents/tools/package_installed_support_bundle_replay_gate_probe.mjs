#!/usr/bin/env node
// Manifest slice: product:package-installed-support-bundle-replay-gate-proof. Installed-package proof for support-bundle operator replay gate through boot().
import assert from 'node:assert/strict';
import { mkdtemp, mkdir, readFile, rm, writeFile } from 'node:fs/promises';
import { dirname, join } from 'node:path';
import { tmpdir } from 'node:os';
import { REVISION, VERSION } from '../src/public-api.mjs';
import { preparePackageTarballForProbe, runNpmForPackageFixture } from './lib/package_installed_fixture.mjs';

const REVISION_PREFIX = `REV${REVISION.slice(3)}`;
const DEFAULT_OUT = `artifacts/validation/${REVISION_PREFIX}-PACKAGE-INSTALLED-SUPPORT-BUNDLE-REPLAY-GATE-PROBE.json`;
const argValue = (argv, flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };

const CONSUMER = String.raw`
import assert from 'node:assert/strict';
import * as api from 'browserrt';
import { runSupportBundleReplayWithApi, validateSupportBundleReplayConsumerReport } from './node_modules/browserrt/examples/support-bundle-replay-consumer.mjs';

const report = await runSupportBundleReplayWithApi(api, {
  generatedAt: 'deterministic-package-installed-support-bundle-replay-gate',
  source: 'package-installed-support-bundle-replay-gate-consumer.mjs',
  importSpecifier: 'browserrt'
});
const consumerValidation = validateSupportBundleReplayConsumerReport(report);
assert.equal(report.status, 'passed', report.missing.join('; '));
assert.equal(consumerValidation.ok, true, consumerValidation.errors.join('; '));
assert.equal(report.importSpecifier, 'browserrt');
assert.equal(report.proof.packageRootApiOnly, true);
assert.equal(report.proof.diagnosticsNamespaceUsed, true);
assert.equal(report.proof.supportBundleReplayPlanReady, true);
assert.equal(report.proof.operatorReplayGateReady, true);
assert.equal(report.proof.retryControlsHiddenForVerifyAndStop, true);
assert.equal(report.proof.hiddenRowsCarryCanonicalDisplayFields, true);
assert.equal(report.proof.noCommandsExecuted, true);
console.log(JSON.stringify({ ...report, consumerValidation }, null, 2));
`;

export async function runProbe() {
  const root = process.cwd();
  const workspace = await mkdtemp(join(tmpdir(), 'browserrt-package-installed-support-bundle-replay-'));
  const packDir = join(workspace, 'pack');
  const consumerDir = join(workspace, 'consumer');
  await mkdir(packDir, { recursive: true });
  await mkdir(consumerDir, { recursive: true });
  try {
    const prepared = await preparePackageTarballForProbe({ root, packDir });
    const { packInfo, tarball, fileNames } = prepared;
    const requiredTarballFiles = [
      'package.json',
      'src/public-api.mjs',
      'src/public-api.d.ts',
      'src/browserrt.mjs',
      'src/kernel-kit-demo.mjs',
      'src/types.d.ts',
      'examples/support-bundle-replay-consumer.mjs'
    ];
    const missingTarballFiles = requiredTarballFiles.filter((name) => !fileNames.includes(name));
    assert.deepEqual(missingTarballFiles, [], `npm package missing support-bundle replay gate files: ${missingTarballFiles.join(', ')}`);
    const forbiddenFiles = fileNames.filter((name) => name.startsWith('tools/') || name.startsWith('artifacts/') || name.startsWith('test/') || name.startsWith('node_modules/'));
    assert.deepEqual(forbiddenFiles, [], `npm package leaked development-only files: ${forbiddenFiles.slice(0, 12).join(', ')}`);

    runNpmForPackageFixture('npm', ['init', '-y'], { cwd: consumerDir });
    runNpmForPackageFixture('npm', ['install', '--ignore-scripts', '--no-audit', '--no-fund', tarball], { cwd: consumerDir });
    await writeFile(join(consumerDir, 'consumer.mjs'), CONSUMER, 'utf8');
    const consumer = runNpmForPackageFixture('node', ['consumer.mjs'], { cwd: consumerDir });
    const consumerReport = JSON.parse(consumer.stdout);
    const installedPackageJson = JSON.parse(await readFile(join(consumerDir, 'node_modules', 'browserrt', 'package.json'), 'utf8'));

    assert.equal(consumerReport.project, 'BrowserRT');
    assert.equal(consumerReport.revision, REVISION);
    assert.equal(consumerReport.version, VERSION);
    assert.equal(consumerReport.status, 'passed');
    assert.equal(consumerReport.consumerValidation?.ok, true, consumerReport.consumerValidation?.errors?.join('; '));
    assert.equal(installedPackageJson.exports?.['.']?.import, './src/public-api.mjs');
    assert.equal(installedPackageJson.exports?.['./internal'], undefined, 'installed package must not expose ./internal');

    return Object.freeze({
      project: 'BrowserRT',
      revision: REVISION,
      version: VERSION,
      schema: 1,
      status: 'passed',
      probe_id: `${REVISION}-package-installed-support-bundle-replay-gate`,
      purpose: 'Package-installed consumer proof that browserrt boot() exposes support-bundle replay, operator display snapshot, and operator replay gate through the diagnostics namespace without importing development tools or internal helper modules.',
      package: Object.freeze({
        name: packInfo.name,
        version: packInfo.version,
        filename: packInfo.filename,
        fileCount: fileNames.length,
        unpackedSize: packInfo.unpackedSize,
        source: prepared.source,
        reusedPreparedTarball: prepared.reusedPreparedTarball,
        requiredTarballFiles,
        requiredTarballFilesPresent: true,
        forbiddenFilesAbsent: true,
        packageRootExport: installedPackageJson.exports?.['.'] || null,
        internalExportAbsent: installedPackageJson.exports?.['./internal'] === undefined
      }),
      consumer: Object.freeze({
        importSpecifier: consumerReport.importSpecifier,
        status: consumerReport.status,
        proof: consumerReport.proof,
        counts: consumerReport.counts,
        validation: consumerReport.validation,
        replayGate: consumerReport.replayGate,
        reportValidation: consumerReport.consumerValidation
      }),
      commands: Object.freeze({
        pack: 'npm pack --json --pack-destination <tmp>',
        install: `npm install --ignore-scripts --no-audit --no-fund ${packInfo.filename}`,
        run: 'node consumer.mjs'
      }),
      nonClaims: Object.freeze([
        'Installed package support-bundle replay gate proof validates package-root wiring and display gating only; it does not publish to a registry, run browser OPFS, reserve quota, survive eviction, or prove cross-browser behavior.',
        'Operator replay gate remains a non-executing gate; it does not repair storage, grant quota, preserve Service Worker lifetime, prove Web Lock fairness, or authorize production retry.'
      ])
    });
  } finally {
    await rm(workspace, { recursive: true, force: true });
  }
}

if (import.meta.url === `file://${process.argv[1]}`) {
  const out = argValue(process.argv.slice(2), '--json', DEFAULT_OUT);
  try {
    const report = await runProbe();
    await mkdir(dirname(out), { recursive: true });
    await writeFile(out, JSON.stringify(report, null, 2) + '\n');
    console.log(out);
  } catch (error) {
    const report = { project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1, status: 'failed', probe_id: `${REVISION}-package-installed-support-bundle-replay-gate`, error: { name: error?.name || 'Error', message: error?.message || String(error), stack: error?.stack, command: error?.result || null } };
    await mkdir(dirname(out), { recursive: true });
    await writeFile(out, JSON.stringify(report, null, 2) + '\n');
    console.error(out);
    console.error(`[package_installed_support_bundle_replay_gate_probe] FAIL: ${error?.stack || error}`);
    process.exitCode = 1;
  }
}
