#!/usr/bin/env node
import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import { mkdir, mkdtemp, readFile, rm, writeFile } from 'node:fs/promises';
import { dirname, join } from 'node:path';
import { tmpdir } from 'node:os';
import { REVISION, VERSION } from '../src/public-api.mjs';

const DEFAULT_OUT = `artifacts/validation/REV${REVISION.slice(3)}-PACKAGE-INSTALLED-CONSUMER-SMOKE-PROBE.json`;
const argValue = (argv, flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };

function run(cmd, args, options = {}) {
  const result = spawnSync(cmd, args, {
    cwd: options.cwd || process.cwd(),
    encoding: 'utf8',
    maxBuffer: 16 * 1024 * 1024,
    env: { ...process.env, npm_config_update_notifier: 'false', npm_config_fund: 'false', npm_config_audit: 'false', ...(options.env || {}) }
  });
  if (result.status !== 0) {
    const err = new Error(`${cmd} ${args.join(' ')} failed with ${result.status}`);
    err.result = { status: result.status, signal: result.signal, stdout: result.stdout, stderr: result.stderr };
    throw err;
  }
  return result;
}

function parseNpmPackJson(stdout) {
  const trimmed = String(stdout || '').trim();
  try { return JSON.parse(trimmed); } catch {}
  const first = trimmed.indexOf('[');
  const last = trimmed.lastIndexOf(']');
  if (first >= 0 && last > first) return JSON.parse(trimmed.slice(first, last + 1));
  throw new Error(`npm pack did not return parseable JSON: ${trimmed.slice(0, 400)}`);
}

function declaredBrowserRtRuntimeMethods(typesSource) {
  const marker = 'export interface BrowserRTRuntime {';
  const start = typesSource.indexOf(marker);
  assert.ok(start >= 0, 'installed declarations missing BrowserRTRuntime interface');
  const bodyStart = start + marker.length;
  const end = typesSource.indexOf('\n}\n', bodyStart);
  assert.ok(end > bodyStart, 'installed BrowserRTRuntime interface is not structurally readable');
  const body = typesSource.slice(bodyStart, end);
  return [...body.matchAll(/^  ([A-Za-z_$][\w$]*)\s*(?:<[^\n>]+>)?\(/gm)].map((match) => match[1]).sort();
}

const TYPESCRIPT_CONSUMER = String.raw`
import { boot, REVISION, VERSION, type BrowserRTRuntime } from 'browserrt';

const runtime: Readonly<BrowserRTRuntime> = await boot({ telemetry: 'typed-installed-package-consumer' });
const typedRevision: typeof REVISION = runtime.revision;
const typedVersion: typeof VERSION = runtime.version;
void typedRevision;
void typedVersion;

const store = runtime.storage.blockStore({ name: 'typed-consumer-store' });
const scheduler = runtime.coordination.crossLaneScheduler({
  label: 'typed-consumer-scheduler',
  lanes: [{ id: 'storage', rank: 50, capacity: 1, quantum: 64, maxQueuedCost: 256 }]
});
const adapter = runtime.storage.blockStoreLaneAdapter({ label: 'typed-consumer-adapter', store, scheduler });
const scheduled = adapter.schedulePut(new Uint8Array([1, 2, 3]), { id: 'typed-put' });
void scheduled;
void adapter.snapshot();
void runtime.core.scope;
void runtime.core.channel;
void runtime.core.spawnAgent;
void runtime.scope;
void runtime.storage.blockStoreLaneAdapter;
void runtime.storage.opfsAsyncBlockStore;
void runtime.coordination.crossLaneScheduler;
void runtime.coordination.webLockCoordinator;
void runtime.diagnostics.kernelKitTraceExport;
void runtime.diagnostics.kernelKitSupportBundle;
void runtime.experimental.providerResilienceModelOracle;


// These references make the complete supported boot facade a compile-time
// contract instead of allowing runtime-only methods to drift out of the .d.ts.
void runtime.circuitBreakerBulkheadController;
void runtime.providerResilienceModelOracle;
void runtime.storageLaneAdmissionHistoryRunner;
void runtime.storageLaneAdmissionHistoryModelOracle;
void runtime.storageLaneOverloadGovernanceModelOracle;
void runtime.dreamBoundaryMap;
void runtime.validateDreamBoundaryMap;
void runtime.projectContinuationAssessment;
void runtime.validateProjectContinuationAssessment;
void runtime.kernelKitDemoPlan;
void runtime.validateKernelKitDemoReport;
void runtime.kernelKitDemoTranscript;
void runtime.validateKernelKitDemoTranscript;
void runtime.kernelKitDemoUsefulnessScore;
void runtime.kernelKitDemoTraceSummary;
void runtime.kernelKitTraceExport;
void runtime.validateKernelKitTraceExport;
void runtime.kernelKitDemoExportBundle;
void runtime.validateKernelKitDemoExportBundle;
void runtime.kernelKitFailureModeReport;
void runtime.validateKernelKitFailureModeReport;
void runtime.kernelKitTraceComparison;
void runtime.validateKernelKitTraceComparison;
void runtime.kernelKitDiagnosticRunbook;
void runtime.validateKernelKitDiagnosticRunbook;
void runtime.kernelKitSupportBundle;
void runtime.validateKernelKitSupportBundle;
void runtime.kernelKitSupportBundleReplayPlan;
void runtime.validateKernelKitSupportBundleReplayPlan;
void runtime.kernelKitSupportBundleEvidenceLedger;
void runtime.validateKernelKitSupportBundleEvidenceLedger;
void runtime.kernelKitSupportBundleEvidenceCheckpoint;
void runtime.validateKernelKitSupportBundleEvidenceCheckpoint;
void runtime.kernelKitGuidedTour;
void runtime.validateKernelKitGuidedTour;
void runtime.kernelKitSupportBundleImportReport;
void runtime.validateKernelKitSupportBundleImportReport;
void runtime.kernelKitSupportBundleDiff;
void runtime.validateKernelKitSupportBundleDiff;
void runtime.kernelKitHandoffMarkdown;
void runtime.validateKernelKitHandoffMarkdown;
void runtime.kernelKitDemoHandoff;
void runtime.validateKernelKitDemoHandoff;
void runtime.kernelKitDemoUsefulnessReport;
void runtime.validateKernelKitDemoUsefulnessReport;
void runtime.kernelKitDemoObservatory;
void runtime.validateKernelKitDemoObservatoryReport;
void runtime.kernelKitGuidedTourReceipt;
void runtime.validateKernelKitGuidedTourReceipt;
void runtime.kernelKitHandoffMarkdownImport;
void runtime.validateKernelKitHandoffMarkdownImportReport;
void runtime.kernelKitReadinessGate;
void runtime.validateKernelKitReadinessGate;
void runtime.kernelKitReadinessContrast;
void runtime.validateKernelKitReadinessContrast;
void runtime.opfsBlockStoreStorageLaneAdapter;

runtime.close();
`;

const TYPESCRIPT_CONFIG = JSON.stringify({
  compilerOptions: {
    target: 'ES2022',
    module: 'ESNext',
    moduleResolution: 'Bundler',
    lib: ['ES2022', 'DOM'],
    strict: true,
    noEmit: true,
    skipLibCheck: false
  },
  include: ['consumer.ts']
}, null, 2) + '\n';

const CONSUMER = String.raw`
import assert from 'node:assert/strict';
import * as api from 'browserrt';
import { runProductWedgeWithApi } from './node_modules/browserrt/examples/product-wedge-consumer.mjs';
import { runGoldenWorkloadWithApi } from './node_modules/browserrt/examples/golden-workload-consumer.mjs';
const report = await runProductWedgeWithApi(api, { generatedAt: 'deterministic-installed-package-smoke', source: 'installed-package-consumer.mjs', importSpecifier: 'browserrt' });
const golden = await runGoldenWorkloadWithApi(api, { generatedAt: 'deterministic-installed-package-golden-workload', source: 'installed-package-consumer.mjs', importSpecifier: 'browserrt' });
const surfaceRuntime = await api.boot({ telemetry: 'installed-package-runtime-surface' });
const runtimeMethodNames = Object.entries(surfaceRuntime).filter(([, value]) => typeof value === 'function').map(([name]) => name).sort();
const runtimeNamespaceNames = ['core', 'storage', 'coordination', 'diagnostics', 'experimental'].filter((name) => surfaceRuntime[name] && typeof surfaceRuntime[name] === 'object').sort();
surfaceRuntime.close();
assert.equal(report.status, 'passed', report.validation.errors.join('; '));
assert.equal(report.receipt.observed.imports.importSpecifier, 'browserrt');
assert.equal(report.receipt.proof.storageLaneWriteRead, true);
assert.equal(golden.status, 'passed', golden.validation.errors.join('; '));
assert.equal(golden.receipt.proof.namespacedFacadeUsed, true);
assert.equal(golden.receipt.proof.abortCancelledBeforeCommit, true);
assert.equal(golden.receipt.proof.recoveryWriteAfterAbort, true);
console.log(JSON.stringify({ project: 'BrowserRT', revision: api.REVISION, version: api.VERSION, schema: 1, status: 'passed', importSpecifier: 'browserrt', runtimeMethodNames, runtimeNamespaceNames, receipt: report.receipt, validation: report.validation, golden: { receipt: golden.receipt, validation: golden.validation } }, null, 2));
`;


export async function runProbe() {
  const root = process.cwd();
  const workspace = await mkdtemp(join(tmpdir(), 'browserrt-package-installed-smoke-'));
  const packDir = join(workspace, 'pack');
  const consumerDir = join(workspace, 'consumer');
  await mkdir(packDir, { recursive: true });
  await mkdir(consumerDir, { recursive: true });
  try {
    const pack = run('npm', ['pack', '--json', '--pack-destination', packDir], { cwd: root });
    const packRows = parseNpmPackJson(pack.stdout);
    const packInfo = packRows[0];
    assert.ok(packInfo?.filename, 'npm pack did not report a filename');
    const tarball = join(packDir, packInfo.filename);
    const fileNames = (packInfo.files || []).map((file) => file.path).sort();
    const requiredTarballFiles = [
      'package.json',
      'src/public-api.mjs',
      'src/public-api.d.ts',
      'src/product-wedge.mjs',
      'src/browserrt.mjs',
      'src/sab-ring.mjs',
      'src/block-store-lane-adapter.mjs',
      'src/agent-worker.mjs',
      'src/node-agent-worker.mjs',
      'src/storage-lane-scheduler.mjs',
      'src/types.d.ts',
      'examples/product-wedge-consumer.mjs',
      'examples/golden-workload-consumer.mjs'
    ];
    const missingTarballFiles = requiredTarballFiles.filter((name) => !fileNames.includes(name));
    assert.deepEqual(missingTarballFiles, [], `npm package missing runtime dependency files: ${missingTarballFiles.join(', ')}`);
    const forbiddenPrefixes = ['artifacts/', 'tools/', 'test/', 'node_modules/'];
    const forbiddenFiles = fileNames.filter((name) => forbiddenPrefixes.some((prefix) => name.startsWith(prefix)));
    assert.deepEqual(forbiddenFiles, [], `npm package leaked development-only files: ${forbiddenFiles.slice(0, 12).join(', ')}`);

    run('npm', ['init', '-y'], { cwd: consumerDir });
    const install = run('npm', ['install', '--ignore-scripts', '--no-audit', '--no-fund', tarball], { cwd: consumerDir });
    await writeFile(join(consumerDir, 'consumer.mjs'), CONSUMER, 'utf8');
    const consumer = run('node', ['consumer.mjs'], { cwd: consumerDir });
    const consumerReport = JSON.parse(consumer.stdout);
    await writeFile(join(consumerDir, 'consumer.ts'), TYPESCRIPT_CONSUMER, 'utf8');
    await writeFile(join(consumerDir, 'tsconfig.json'), TYPESCRIPT_CONFIG, 'utf8');
    const typecheck = run(process.env.BROWSERRT_TSC || 'tsc', ['--project', 'tsconfig.json', '--pretty', 'false'], { cwd: consumerDir });
    assert.equal(consumerReport.status, 'passed');
    assert.equal(consumerReport.importSpecifier, 'browserrt');
    assert.equal(consumerReport.revision, REVISION);
    assert.equal(consumerReport.version, VERSION);
    const installedPackageJson = JSON.parse(await readFile(join(consumerDir, 'node_modules', 'browserrt', 'package.json'), 'utf8'));
    assert.equal(installedPackageJson.exports?.['.']?.import, './src/public-api.mjs');
    assert.equal(installedPackageJson.exports?.['./internal'], undefined, 'installed package must not expose ./internal');
    const installedTypesSource = await readFile(join(consumerDir, 'node_modules', 'browserrt', 'src', 'types.d.ts'), 'utf8');
    const declarationMethodNames = declaredBrowserRtRuntimeMethods(installedTypesSource);
    assert.deepEqual(declarationMethodNames, consumerReport.runtimeMethodNames, 'installed BrowserRTRuntime declaration method names drifted from boot() runtime methods');
    assert.equal(declarationMethodNames.length, 104, 'unexpected BrowserRTRuntime method count');
    assert.deepEqual(consumerReport.runtimeNamespaceNames, ['coordination', 'core', 'diagnostics', 'experimental', 'storage'], 'installed runtime missing product namespaces');
    return Object.freeze({
      project: 'BrowserRT',
      revision: REVISION,
      version: VERSION,
      schema: 1,
      status: 'passed',
      probe_id: `${REVISION}-package-installed-consumer-smoke`,
      purpose: 'Package-installed consumer smoke: npm pack, local install, package-root JavaScript execution, package-root TypeScript compilation, public API product wedge execution, golden bounded local workload execution, and tarball file-boundary hygiene.',
      package: {
        name: packInfo.name,
        version: packInfo.version,
        filename: packInfo.filename,
        fileCount: fileNames.length,
        unpackedSize: packInfo.unpackedSize,
        requiredTarballFiles,
        requiredTarballFilesPresent: true,
        forbiddenFilesAbsent: true,
        packageRootExport: installedPackageJson.exports?.['.'] || null,
        internalExportAbsent: installedPackageJson.exports?.['./internal'] === undefined
      },
      consumer: {
        importSpecifier: consumerReport.importSpecifier,
        status: consumerReport.status,
        proof: consumerReport.receipt?.proof || null,
        validation: consumerReport.validation || null,
        goldenWorkload: {
          proof: consumerReport.golden?.receipt?.proof || null,
          validation: consumerReport.golden?.validation || null,
          workload: consumerReport.golden?.receipt?.workload || null
        },
        traceKinds: consumerReport.receipt?.traceKinds || [],
        typescript: {
          status: 'passed',
          compiler: process.env.BROWSERRT_TSC || 'tsc',
          command: 'tsc --project tsconfig.json --pretty false',
          declaredRuntimeType: 'BrowserRTRuntime',
          flagshipMethod: 'blockStoreLaneAdapter',
          runtimeMethodCount: consumerReport.runtimeMethodNames.length,
          declarationMethodCount: declarationMethodNames.length,
          runtimeDeclarationMethodParity: true,
          namespaceTypecheck: true,
          methodNames: declarationMethodNames,
          runtimeNamespaceNames: consumerReport.runtimeNamespaceNames,
          stdout: String(typecheck.stdout || '').trim()
        }
      },
      commands: {
        pack: 'npm pack --json --pack-destination <tmp>',
        install: `npm install --ignore-scripts --no-audit --no-fund ${packInfo.filename}`,
        run: 'node consumer.mjs',
        typecheck: 'tsc --project tsconfig.json --pretty false'
      },
      nonClaims: [
        'Local tarball install and TypeScript compiler smoke only; it does not publish to a registry, prove semver compatibility, prove every bundler, or prove cross-browser behavior.',
        'The product wedge and golden workload use fast memory-backed storage lanes through the product namespaces; OPFS/Web Locks proofs remain separate explicit browser/runtime tasks.'
      ]
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
    const report = { project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1, status: 'failed', probe_id: `${REVISION}-package-installed-consumer-smoke`, error: { name: error?.name || 'Error', message: error?.message || String(error), stack: error?.stack, command: error?.result || null } };
    await mkdir(dirname(out), { recursive: true });
    await writeFile(out, JSON.stringify(report, null, 2) + '\n');
    console.error(out);
    console.error(`[package_installed_consumer_smoke_probe] FAIL: ${error?.stack || error}`);
    process.exitCode = 1;
  }
}
