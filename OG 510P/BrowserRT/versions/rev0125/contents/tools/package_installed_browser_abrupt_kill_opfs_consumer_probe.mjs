#!/usr/bin/env node
import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import { mkdir, mkdtemp, readFile, rm, writeFile } from 'node:fs/promises';
import { dirname, join } from 'node:path';
import { tmpdir } from 'node:os';
import { REVISION, VERSION } from '../src/public-api.mjs';
import { runManagedBrowserPage, startProbeServer } from './browser_cdp_fixture.mjs';
import {
  createBrowserOpfsAbruptKillProductWedgeReceipt,
  validateBrowserOpfsAbruptKillProductWedgeReceipt
} from '../examples/browser-opfs-reopen-product-wedge-consumer.mjs';

const DEFAULT_OUT = `artifacts/validation/REV${REVISION.slice(3)}-PACKAGE-INSTALLED-BROWSER-OPFS-ABRUPT-KILL-CONSUMER-PROBE.json`;
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

const PAGE = `<!doctype html>
<meta charset="utf-8">
<title>BrowserRT installed browser OPFS abrupt-kill consumer proof</title>
<script>
  window.__BROWSERRT_PACKAGE_BROWSER_OPFS_ABRUPT_KILL_ERROR = null;
  window.__BROWSERRT_PAGE_LOAD_ID = (globalThis.crypto && crypto.randomUUID) ? crypto.randomUUID() : String(Date.now()) + ':' + String(Math.random());
  window.addEventListener('error', (event) => {
    window.__BROWSERRT_PACKAGE_BROWSER_OPFS_ABRUPT_KILL_ERROR = { type: 'error', message: event.message, filename: event.filename, lineno: event.lineno, colno: event.colno };
  });
  window.addEventListener('unhandledrejection', (event) => {
    const reason = event.reason || {};
    window.__BROWSERRT_PACKAGE_BROWSER_OPFS_ABRUPT_KILL_ERROR = { type: 'unhandledrejection', message: reason.message || String(reason), stack: reason.stack || null, code: reason.code || null };
  });
</script>
<script type="importmap">
{
  "imports": {
    "browserrt": "/node_modules/browserrt/src/public-api.mjs"
  }
}
</script>
<body>BrowserRT installed browser OPFS abrupt-kill consumer proof</body>
`;

function jsonExpression(source) {
  return `(async()=>{ const value = await (${source})(); return JSON.stringify(value); })()`;
}

function pageLoadIdExpression() {
  return jsonExpression(`async()=>({ pageLoadId: window.__BROWSERRT_PAGE_LOAD_ID || null, href: location.href, readyState: document.readyState, error: window.__BROWSERRT_PACKAGE_BROWSER_OPFS_ABRUPT_KILL_ERROR || null, origin: location.origin })`);
}

function writeExpression(prefixSuffix) {
  return jsonExpression(`async()=>{
    if (window.__BROWSERRT_PACKAGE_BROWSER_OPFS_ABRUPT_KILL_ERROR) throw new Error(JSON.stringify(window.__BROWSERRT_PACKAGE_BROWSER_OPFS_ABRUPT_KILL_ERROR));
    const api = await import('browserrt');
    const mod = await import('/node_modules/browserrt/examples/browser-opfs-reopen-product-wedge-consumer.mjs');
    return await mod.writeBrowserOpfsReopenBlockWithApi(api, {
      generatedAt: 'deterministic-installed-browser-opfs-abrupt-kill-package-proof-write',
      source: 'installed-browser-opfs-abrupt-kill-package-consumer.html',
      importSpecifier: 'browserrt',
      prefixSuffix: ${JSON.stringify(prefixSuffix)},
      lockTimeoutMs: 2000,
      pageLoadId: window.__BROWSERRT_PAGE_LOAD_ID || null
    });
  }`);
}

function readExpression({ ref, expectedDigest, prefixSuffix, cleanup = true }) {
  return jsonExpression(`async()=>{
    if (window.__BROWSERRT_PACKAGE_BROWSER_OPFS_ABRUPT_KILL_ERROR) throw new Error(JSON.stringify(window.__BROWSERRT_PACKAGE_BROWSER_OPFS_ABRUPT_KILL_ERROR));
    const api = await import('browserrt');
    const mod = await import('/node_modules/browserrt/examples/browser-opfs-reopen-product-wedge-consumer.mjs');
    return await mod.readBrowserOpfsReopenBlockWithApi(api, {
      generatedAt: 'deterministic-installed-browser-opfs-abrupt-kill-package-proof-read',
      source: 'installed-browser-opfs-abrupt-kill-package-consumer.html',
      importSpecifier: 'browserrt',
      prefixSuffix: ${JSON.stringify(prefixSuffix)},
      ref: ${JSON.stringify(ref)},
      expectedDigest: ${JSON.stringify(expectedDigest)},
      lockTimeoutMs: 2000,
      pageLoadId: window.__BROWSERRT_PAGE_LOAD_ID || null,
      cleanup: ${cleanup === true ? 'true' : 'false'}
    });
  }`);
}

function interruptedCandidateExpression(prefixSuffix) {
  return jsonExpression(`async()=>{
    if (window.__BROWSERRT_PACKAGE_BROWSER_OPFS_ABRUPT_KILL_ERROR) throw new Error(JSON.stringify(window.__BROWSERRT_PACKAGE_BROWSER_OPFS_ABRUPT_KILL_ERROR));
    const api = await import('browserrt');
    const mod = await import('/node_modules/browserrt/examples/browser-opfs-reopen-product-wedge-consumer.mjs');
    return await mod.createBrowserOpfsInterruptedCandidateWithApi(api, {
      generatedAt: 'deterministic-installed-browser-opfs-abrupt-kill-package-proof-interrupted-candidate',
      source: 'installed-browser-opfs-abrupt-kill-package-consumer.html',
      importSpecifier: 'browserrt',
      prefixSuffix: ${JSON.stringify(prefixSuffix)},
      totalBytes: 524288,
      firstChunkBytes: 65536,
      pageLoadId: window.__BROWSERRT_PAGE_LOAD_ID || null
    });
  }`);
}

function inspectInterruptedCandidateExpression({ candidate, prefixSuffix, cleanup = true, repairFullCandidate = false }) {
  return jsonExpression(`async()=>{
    if (window.__BROWSERRT_PACKAGE_BROWSER_OPFS_ABRUPT_KILL_ERROR) throw new Error(JSON.stringify(window.__BROWSERRT_PACKAGE_BROWSER_OPFS_ABRUPT_KILL_ERROR));
    const api = await import('browserrt');
    const mod = await import('/node_modules/browserrt/examples/browser-opfs-reopen-product-wedge-consumer.mjs');
    return await mod.inspectBrowserOpfsInterruptedCandidateWithApi(api, {
      generatedAt: 'deterministic-installed-browser-opfs-abrupt-kill-package-proof-interrupted-inspection',
      source: 'installed-browser-opfs-abrupt-kill-package-consumer.html',
      importSpecifier: 'browserrt',
      prefixSuffix: ${JSON.stringify(prefixSuffix)},
      candidate: ${JSON.stringify(candidate)},
      lockTimeoutMs: 2000,
      cleanup: ${cleanup === true ? 'true' : 'false'},
      repairFullCandidate: ${repairFullCandidate === true ? 'true' : 'false'},
      pageLoadId: window.__BROWSERRT_PAGE_LOAD_ID || null
    });
  }`);
}

export async function runProbe(options = {}) {
  const root = process.cwd();
  const workspace = await mkdtemp(join(tmpdir(), 'browserrt-package-browser-opfs-abrupt-kill-smoke-'));
  const packDir = join(workspace, 'pack');
  const consumerDir = join(workspace, 'consumer');
  const profileDir = join(workspace, 'profile');
  await mkdir(packDir, { recursive: true });
  await mkdir(consumerDir, { recursive: true });
  await mkdir(profileDir, { recursive: true });
  let server = null;
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
      'src/browserrt.mjs',
      'src/opfs-block-store.mjs',
      'src/opfs-web-lock-guarded-block-store.mjs',
      'src/web-lock-coordinator.mjs',
      'src/block-store-lane-adapter.mjs',
      'src/storage-lane-scheduler.mjs',
      'examples/browser-opfs-reopen-product-wedge-consumer.mjs'
    ];
    const missingTarballFiles = requiredTarballFiles.filter((name) => !fileNames.includes(name));
    assert.deepEqual(missingTarballFiles, [], `npm package missing browser OPFS abrupt-kill dependency files: ${missingTarballFiles.join(', ')}`);
    const forbiddenPrefixes = ['artifacts/', 'tools/', 'test/', 'node_modules/'];
    const forbiddenFiles = fileNames.filter((name) => forbiddenPrefixes.some((prefix) => name.startsWith(prefix)));
    assert.deepEqual(forbiddenFiles, [], `npm package leaked development-only files: ${forbiddenFiles.slice(0, 12).join(', ')}`);

    run('npm', ['init', '-y'], { cwd: consumerDir });
    run('npm', ['install', '--ignore-scripts', '--no-audit', '--no-fund', tarball], { cwd: consumerDir });
    const installedExample = await readFile(join(consumerDir, 'node_modules', 'browserrt', 'examples', 'browser-opfs-reopen-product-wedge-consumer.mjs'), 'utf8');
    assert.match(installedExample, /writeBrowserOpfsReopenBlockWithApi/, 'installed OPFS reopen wedge example must expose write session');
    assert.match(installedExample, /createBrowserOpfsInterruptedCandidateWithApi/, 'installed OPFS reopen wedge example must expose interrupted candidate creator');
    assert.match(installedExample, /inspectBrowserOpfsInterruptedCandidateWithApi/, 'installed OPFS reopen wedge example must expose interrupted candidate inspector');
    assert.match(installedExample, /repairFullCandidate/, 'installed OPFS reopen wedge example must expose interrupted candidate repair/retry option');
    assert.match(installedExample, /interruptedCandidateRepairRetryVerified/, 'installed OPFS reopen wedge receipt must require repair/retry verification');
    assert.match(installedExample, /createBrowserOpfsAbruptKillProductWedgeReceipt/, 'installed OPFS reopen wedge example must expose abrupt-kill receipt helpers');
    const installedPackageJson = JSON.parse(await readFile(join(consumerDir, 'node_modules', 'browserrt', 'package.json'), 'utf8'));
    const prefixSuffix = `installed-abrupt-kill-${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 8)}`;

    server = await startProbeServer({
      root: consumerDir,
      pagePath: '/installed-browser-opfs-abrupt-kill-consumer.html',
      pageTitle: 'BrowserRT installed browser OPFS abrupt-kill consumer proof',
      body: PAGE,
      allowedPrefixes: ['node_modules/browserrt/src/', 'node_modules/browserrt/examples/']
    });

    const first = await runManagedBrowserPage({
      root: consumerDir,
      server,
      pagePath: server.pagePath,
      profileDir,
      keepProfile: true,
      teardownMode: 'kill',
      killWaitMs: 2500,
      timeoutMs: options.timeoutMs || 35000,
      stderrTerms: ['import', 'module', 'browserrt', 'opfs', 'lock', 'kill', 'storage']
    }, async ({ evalJson, pageState, pageUrl, browserVersion, profileDir: activeProfile, teardownMode }) => {
      const beforePage = await evalJson(pageLoadIdExpression(), 5000);
      assert.equal(beforePage.error, null, `initial write-launch page error: ${JSON.stringify(beforePage.error)}`);
      const write = await evalJson(writeExpression(prefixSuffix), 25000);
      assert.equal(write.importSpecifier, 'browserrt');
      assert.equal(write.revision, REVISION);
      assert.equal(write.version, VERSION);
      assert.equal(write.environment.isSecureContext, true, 'managed server should provide secure localhost context');
      assert.equal(write.environment.hasOpfs, true, 'managed Chromium should expose OPFS');
      assert.equal(write.environment.hasWebLocks, true, 'managed Chromium should expose Web Locks');
      assert.equal(write.storage.readDigestMatches, true, 'write self-read must match before browser SIGKILL');
      assert.equal(write.storage.verifyDigestMatches, true, 'write verify digest must match before browser SIGKILL');
      assert.equal(write.storage.budgetChecked, true, 'write session must check storage budget estimate');
      assert.equal(write.trace.closed, true, 'runtime must close before process SIGKILL so acknowledged block has a clear receipt');
      assert.equal(write.namespace?.storage, true, 'write session must use the product storage namespace');
      assert.equal(write.namespace?.coordination, true, 'write session must use the product coordination namespace');
      const interruptedCandidate = await evalJson(interruptedCandidateExpression(prefixSuffix), 10000);
      assert.equal(interruptedCandidate.importSpecifier, 'browserrt');
      assert.equal(interruptedCandidate.closeCalled, false, 'interrupted candidate must intentionally remain unclosed before process SIGKILL');
      assert.ok(interruptedCandidate.firstChunkBytes > 0 && interruptedCandidate.firstChunkBytes < interruptedCandidate.bytes, 'interrupted candidate must write only a partial first chunk');
      assert.equal(interruptedCandidate.environment.hasOpfs, true, 'interrupted candidate must be created in OPFS before SIGKILL');
      return { pageUrl, pageState, browserVersion, beforePage, write, interruptedCandidate, profileDir: activeProfile, teardownMode };
    });

    assert.equal(first.result.teardownMode, 'kill', 'first launch must use SIGKILL teardown mode');
    assert.equal(first.harness.teardownMode, 'kill', 'first harness must record SIGKILL teardown mode');
    assert.ok((first.harness.process?.requestedSignals || []).some((signal) => String(signal).includes('SIGKILL')), 'first browser launch must be torn down with SIGKILL');
    assert.equal(first.harness.process?.timedOut, false, 'killed browser process group must close before timeout');

    const second = await runManagedBrowserPage({
      root: consumerDir,
      server,
      pagePath: server.pagePath,
      profileDir,
      keepProfile: true,
      timeoutMs: options.timeoutMs || 35000,
      stderrTerms: ['import', 'module', 'browserrt', 'opfs', 'lock', 'relaunch', 'storage']
    }, async ({ evalJson, pageState, pageUrl, browserVersion, profileDir: activeProfile }) => {
      const beforePage = await evalJson(pageLoadIdExpression(), 5000);
      assert.equal(beforePage.error, null, `read-launch page error: ${JSON.stringify(beforePage.error)}`);
      const write = first.result.write;
      const read = await evalJson(readExpression({ ref: write.storage.ref, expectedDigest: write.storage.expectedDigest, prefixSuffix, cleanup: false }), 25000);
      assert.equal(read.importSpecifier, 'browserrt');
      assert.equal(read.revision, REVISION);
      assert.equal(read.version, VERSION);
      assert.equal(read.prefix, write.prefix, 'relaunch read must use the same OPFS prefix');
      assert.equal(read.lockName, write.lockName, 'relaunch read must use the same Web Lock name');
      assert.equal(read.storage.readDigestMatches, true, 'relaunch read digest must match the acknowledged write digest');
      assert.equal(read.storage.verifyDigestMatches, true, 'relaunch verify digest must match the acknowledged write digest');
      assert.equal(read.storage.readDigest, write.storage.expectedDigest, 'relaunch read must recover the exact written bytes');
      assert.equal(read.cleanup.accepted, null, 'acknowledged read leaves cleanup to the interrupted-candidate inspection');
      assert.equal(read.trace.closed, true, 'read runtime must close before interrupted-candidate inspection');
      assert.equal(read.namespace?.storage, true, 'read session must use the product storage namespace');
      assert.equal(read.namespace?.coordination, true, 'read session must use the product coordination namespace');
      const interruptedInspection = await evalJson(inspectInterruptedCandidateExpression({ candidate: first.result.interruptedCandidate, prefixSuffix, cleanup: true, repairFullCandidate: true }), 25000);
      assert.equal(interruptedInspection.importSpecifier, 'browserrt');
      assert.ok(['absent-after-unclosed-interrupted-write', 'present-but-checksum-rejected-after-unclosed-interrupted-write', 'present-but-read-rejected-after-unclosed-interrupted-write'].includes(interruptedInspection.inspection.disposition), `interrupted candidate must be absent or rejected, got ${interruptedInspection.inspection.disposition}`);
      assert.equal(interruptedInspection.repair.ok, true, `repair/retry of interrupted candidate digest must verify: ${JSON.stringify(interruptedInspection.repair)}`);
      assert.equal(interruptedInspection.repair.payloadMatchesCandidate, true, 'repair payload must reconstruct the same interrupted candidate digest');
      assert.equal(interruptedInspection.repair.putDigestMatchesCandidate, true, 'repair retry must put the same candidate digest');
      assert.equal(interruptedInspection.repair.readDigestMatchesCandidate, true, 'repair retry readback must match the candidate digest');
      assert.equal(interruptedInspection.repair.verifyAfterDeletePresent, false, 'repair retry cleanup must remove the repaired candidate block before prefix cleanup');
      assert.equal(interruptedInspection.cleanup.result, true, 'cleanup must remove the OPFS prefix after interrupted-candidate repair inspection');
      assert.equal(interruptedInspection.trace.closed, true, 'interrupted-candidate inspection runtime must close after cleanup');
      return { pageUrl, pageState, browserVersion, beforePage, read, interruptedInspection, profileDir: activeProfile };
    });

    const write = first.result.write;
    const read = second.result.read;
    assert.equal(first.result.pageUrl, second.result.pageUrl, 'same local origin/page must be reused after browser SIGKILL relaunch');
    assert.equal(first.result.profileDir, profileDir, 'write launch must use the shared profile');
    assert.equal(second.result.profileDir, profileDir, 'read launch must reuse the shared profile');

    const observed = Object.freeze({
      imports: { publicApiOnly: true, writeImportSpecifier: 'browserrt', readImportSpecifier: 'browserrt' },
      environment: {
        isSecureContext: write.environment.isSecureContext === true && read.environment.isSecureContext === true,
        hasOpfs: write.environment.hasOpfs === true && read.environment.hasOpfs === true,
        hasWebLocks: write.environment.hasWebLocks === true && read.environment.hasWebLocks === true,
        sameOrigin: new URL(write.environment.href).origin === new URL(read.environment.href).origin,
        write: write.environment,
        read: read.environment
      },
      lifecycle: {
        sameOriginPage: first.result.pageUrl === second.result.pageUrl,
        profileReused: first.result.profileDir === second.result.profileDir && second.result.profileDir === profileDir,
        firstPageLoadId: first.result.beforePage.pageLoadId,
        secondPageLoadId: second.result.beforePage.pageLoadId,
        firstBrowserProcessSigkilled: first.harness.teardownMode === 'kill' && (first.harness.process?.requestedSignals || []).some((signal) => String(signal).includes('SIGKILL')),
        firstProcessTimedOut: first.harness.process?.timedOut === true,
        firstProcessSignal: first.harness.process?.signal || null,
        firstProcessRequestedSignals: first.harness.process?.requestedSignals || []
      },
      write,
      read,
      interruptedCandidate: first.result.interruptedCandidate,
      interruptedInspection: second.result.interruptedInspection
    });
    const receipt = createBrowserOpfsAbruptKillProductWedgeReceipt({ observed, generatedAt: 'deterministic-installed-browser-opfs-abrupt-kill-package-proof', source: 'installed-browser-opfs-abrupt-kill-package-consumer.html' });
    const validation = validateBrowserOpfsAbruptKillProductWedgeReceipt(receipt);
    assert.equal(validation.ok, true, validation.errors.join('; '));

    return Object.freeze({
      project: 'BrowserRT',
      revision: REVISION,
      version: VERSION,
      schema: 1,
      status: 'passed',
      probe_id: `${REVISION}-package-installed-browser-opfs-abrupt-kill-consumer`,
      purpose: 'Package-installed browser OPFS abrupt-kill proof: npm pack, local install, same-origin managed Chromium launch writes/verifies through package-root public API, the browser process group is SIGKILLed, then the same profile/origin relaunch imports browserrt again, reads/verifies the acknowledged ref, and cleans up.',
      package: {
        name: packInfo.name,
        version: packInfo.version,
        filename: packInfo.filename,
        fileCount: fileNames.length,
        unpackedSize: packInfo.unpackedSize,
        requiredTarballFiles,
        requiredTarballFilesPresent: true,
        forbiddenFilesAbsent: true,
        packageRootExport: installedPackageJson.exports?.['.'] || null
      },
      browser: {
        pageUrl: first.result.pageUrl,
        sameOriginRelaunch: first.result.pageUrl === second.result.pageUrl,
        profileReused: observed.lifecycle.profileReused,
        first: { cdp: first.harness.cdp, process: first.harness.process, durationMs: first.harness.durationMs, chromeStderrSummary: first.harness.chromeStderrSummary },
        second: { cdp: second.harness.cdp, process: second.harness.process, durationMs: second.harness.durationMs, chromeStderrSummary: second.harness.chromeStderrSummary },
        server: { port: server.port, requestCount: server.requests.length, requests: server.requests.slice(0, 40) }
      },
      consumer: {
        importSpecifier: 'browserrt',
        status: receipt.status,
        proof: receipt.proof,
        validation,
        lifecycle: receipt.observed.lifecycle,
        storage: {
          write: { digest: receipt.observed.write.storage.digest, path: receipt.observed.write.storage.path, budgetChecked: receipt.observed.write.storage.budgetChecked },
          read: { readDigest: receipt.observed.read.storage.readDigest, verifyDigest: receipt.observed.read.storage.verifyDigest, cleanup: receipt.observed.read.cleanup },
          interrupted: { disposition: receipt.observed.interruptedInspection.inspection.disposition, delete: receipt.observed.interruptedInspection.inspection.delete, repair: receipt.observed.interruptedInspection.repair, cleanup: receipt.observed.interruptedInspection.cleanup }
        },
        locks: { write: receipt.observed.write.locks, read: receipt.observed.read.locks }
      },
      receipt,
      commands: {
        pack: 'npm pack --json --pack-destination <tmp>',
        install: `npm install --ignore-scripts --no-audit --no-fund ${packInfo.filename}`,
        firstLaunch: 'managed Chromium imports browserrt, writes/verifies OPFS ref through public API, creates an intentionally unclosed partial OPFS candidate, then harness SIGKILLs process group',
        secondLaunch: 'same managed origin/profile imports browserrt again, reads/verifies acknowledged ref, proves the unclosed partial candidate is absent or checksum-rejected, repairs/retries the full candidate digest through the guarded store, verifies it, and cleans up'
      },
      nonClaims: receipt.nonClaims
    });
  } finally {
    if (server) await server.close();
    await rm(workspace, { recursive: true, force: true });
  }
}

if (import.meta.url === `file://${process.argv[1]}`) {
  const out = argValue(process.argv.slice(2), '--json', DEFAULT_OUT);
  try {
    const report = await runProbe({ timeoutMs: Number(argValue(process.argv.slice(2), '--timeout-ms', '35000')) });
    await mkdir(dirname(out), { recursive: true });
    await writeFile(out, JSON.stringify(report, null, 2) + '\n');
    console.log(out);
  } catch (error) {
    const report = { project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1, status: 'failed', probe_id: `${REVISION}-package-installed-browser-opfs-abrupt-kill-consumer`, error: { name: error?.name || 'Error', message: error?.message || String(error), stack: error?.stack, command: error?.result || null } };
    await mkdir(dirname(out), { recursive: true });
    await writeFile(out, JSON.stringify(report, null, 2) + '\n');
    console.error(out);
    console.error(`[package_installed_browser_abrupt_kill_opfs_consumer_probe] FAIL: ${error?.stack || error}`);
    process.exitCode = 1;
  }
}
