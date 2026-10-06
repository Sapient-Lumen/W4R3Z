#!/usr/bin/env node
import assert from 'node:assert/strict';
import { mkdtemp, mkdir, readFile, rm, writeFile } from 'node:fs/promises';
import { dirname, join } from 'node:path';
import { tmpdir } from 'node:os';
import { spawnSync } from 'node:child_process';
import { REVISION, VERSION } from '../src/browserrt.mjs';
import {
  runManagedBrowserPage,
  connectBrowserCdp,
  openPageTarget,
  evalJson as evalCdpJson
} from './browser_cdp_fixture.mjs';
import {
  createBrowserCrossTabOpfsProductWedgeReceipt,
  validateBrowserCrossTabOpfsProductWedgeReceipt
} from '../examples/browser-cross-tab-opfs-product-wedge-consumer.mjs';

const DEFAULT_OUT = `artifacts/validation/REV${REVISION.slice(3)}-PACKAGE-INSTALLED-BROWSER-CROSS-TAB-OPFS-CONSUMER-PROBE.json`;
const argValue = (argv, flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };

function run(command, args, options = {}) {
  const result = spawnSync(command, args, { encoding: 'utf8', maxBuffer: 1024 * 1024 * 10, ...options });
  if (result.status !== 0) {
    const error = new Error(`${command} ${args.join(' ')} failed with ${result.status}`);
    error.result = { stdout: result.stdout, stderr: result.stderr, status: result.status };
    throw error;
  }
  return result;
}

function parseNpmPackJson(stdout) {
  const trimmed = String(stdout || '').trim();
  const parsed = JSON.parse(trimmed || '[]');
  if (Array.isArray(parsed)) return parsed;
  throw new Error(`npm pack did not return parseable JSON: ${trimmed.slice(0, 400)}`);
}

const PAGE = `<!doctype html>
<meta charset="utf-8">
<title>BrowserRT installed browser cross-tab OPFS consumer proof</title>
<script>
  window.__BROWSERRT_PACKAGE_BROWSER_CROSS_TAB_OPFS_ERROR = null;
  window.addEventListener('error', (event) => {
    window.__BROWSERRT_PACKAGE_BROWSER_CROSS_TAB_OPFS_ERROR = { type: 'error', message: event.message, filename: event.filename, lineno: event.lineno, colno: event.colno };
  });
  window.addEventListener('unhandledrejection', (event) => {
    const reason = event.reason || {};
    window.__BROWSERRT_PACKAGE_BROWSER_CROSS_TAB_OPFS_ERROR = { type: 'unhandledrejection', message: reason.message || String(reason), stack: reason.stack || null, code: reason.code || null };
  });
</script>
<script type="importmap">
{
  "imports": {
    "browserrt": "/node_modules/browserrt/src/public-api.mjs"
  }
}
</script>
<body>BrowserRT installed browser cross-tab OPFS consumer proof</body>
`;

function jsonExpression(source) {
  return `(async()=>{ const value = await (${source})(); return JSON.stringify(value); })()`;
}

function initParticipantExpression(tabId, prefixSuffix) {
  return jsonExpression(`async()=>{
    if (window.__BROWSERRT_PACKAGE_BROWSER_CROSS_TAB_OPFS_ERROR) throw new Error(JSON.stringify(window.__BROWSERRT_PACKAGE_BROWSER_CROSS_TAB_OPFS_ERROR));
    const api = await import('browserrt');
    const mod = await import('/node_modules/browserrt/examples/browser-cross-tab-opfs-product-wedge-consumer.mjs');
    const participant = await mod.createBrowserCrossTabOpfsParticipantWithApi(api, {
      tabId: ${JSON.stringify(tabId)},
      generatedAt: 'deterministic-installed-browser-cross-tab-opfs-package-proof',
      source: 'installed-browser-cross-tab-opfs-package-consumer.html',
      importSpecifier: 'browserrt',
      prefixSuffix: ${JSON.stringify(prefixSuffix)},
      lockTimeoutMs: 1200
    });
    window.__BROWSERRT_CROSS_TAB_OPFS_PARTICIPANT = participant;
    return await participant.prepare();
  }`);
}

function callParticipantExpression(method, args = {}) {
  return jsonExpression(`async()=>{
    if (window.__BROWSERRT_PACKAGE_BROWSER_CROSS_TAB_OPFS_ERROR) throw new Error(JSON.stringify(window.__BROWSERRT_PACKAGE_BROWSER_CROSS_TAB_OPFS_ERROR));
    if (!window.__BROWSERRT_CROSS_TAB_OPFS_PARTICIPANT) throw new Error('BrowserRT cross-tab participant not initialized');
    return await window.__BROWSERRT_CROSS_TAB_OPFS_PARTICIPANT[${JSON.stringify(method)}](${JSON.stringify(args)});
  }`);
}

function callParticipantWithRefExpression(method, ref, args = {}) {
  return jsonExpression(`async()=>{
    if (window.__BROWSERRT_PACKAGE_BROWSER_CROSS_TAB_OPFS_ERROR) throw new Error(JSON.stringify(window.__BROWSERRT_PACKAGE_BROWSER_CROSS_TAB_OPFS_ERROR));
    if (!window.__BROWSERRT_CROSS_TAB_OPFS_PARTICIPANT) throw new Error('BrowserRT cross-tab participant not initialized');
    return await window.__BROWSERRT_CROSS_TAB_OPFS_PARTICIPANT[${JSON.stringify(method)}](${JSON.stringify(ref)}, ${JSON.stringify(args)});
  }`);
}

export async function runProbe() {
  const root = process.cwd();
  const workspace = await mkdtemp(join(tmpdir(), 'browserrt-package-browser-cross-tab-opfs-smoke-'));
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
      'src/browserrt.mjs',
      'src/opfs-block-store.mjs',
      'src/opfs-web-lock-guarded-block-store.mjs',
      'src/web-lock-coordinator.mjs',
      'src/block-store-lane-adapter.mjs',
      'src/storage-lane-scheduler.mjs',
      'examples/browser-cross-tab-opfs-product-wedge-consumer.mjs'
    ];
    const missingTarballFiles = requiredTarballFiles.filter((name) => !fileNames.includes(name));
    assert.deepEqual(missingTarballFiles, [], `npm package missing cross-tab OPFS dependency files: ${missingTarballFiles.join(', ')}`);
    const forbiddenPrefixes = ['artifacts/', 'tools/', 'test/', 'node_modules/'];
    const forbiddenFiles = fileNames.filter((name) => forbiddenPrefixes.some((prefix) => name.startsWith(prefix)));
    assert.deepEqual(forbiddenFiles, [], `npm package leaked development-only files: ${forbiddenFiles.slice(0, 12).join(', ')}`);

    run('npm', ['init', '-y'], { cwd: consumerDir });
    run('npm', ['install', '--ignore-scripts', '--no-audit', '--no-fund', tarball], { cwd: consumerDir });
    const installedExample = await readFile(join(consumerDir, 'node_modules', 'browserrt', 'examples', 'browser-cross-tab-opfs-product-wedge-consumer.mjs'), 'utf8');
    assert.match(installedExample, /startExclusiveHold/, 'installed cross-tab example must expose an exclusive hold participant method');
    assert.match(installedExample, /attemptTimedPutWhileLocked/, 'installed cross-tab example must verify pending lock timeout before release');
    assert.match(installedExample, /startQueuedPutWhileLocked/, 'installed cross-tab example must expose a queued waiter that can acquire after release');
    assert.match(installedExample, /awaitQueuedPut/, 'installed cross-tab example must expose queued waiter completion after release');
    assert.match(installedExample, /verifyDigestAbsentViaStorageLane/, 'installed cross-tab example must expose timed-out ghost-write absence verification');
    assert.match(installedExample, /rt\.storage\.opfsWebLockGuardedBlockStore/, 'installed cross-tab OPFS example must use the storage namespace');
    assert.match(installedExample, /rt\.coordination\.crossLaneScheduler/, 'installed cross-tab OPFS example must use the coordination namespace');
    const installedPackageJson = JSON.parse(await readFile(join(consumerDir, 'node_modules', 'browserrt', 'package.json'), 'utf8'));
    const prefixSuffix = `installed-cross-tab-${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 8)}`;

    const browser = await runManagedBrowserPage({
      root: consumerDir,
      pagePath: '/installed-browser-cross-tab-opfs-consumer.html',
      pageTitle: 'BrowserRT installed browser cross-tab OPFS consumer proof',
      body: PAGE,
      allowedPrefixes: ['node_modules/browserrt/src/', 'node_modules/browserrt/examples/'],
      timeoutMs: 30000,
      stderrTerms: ['import', 'module', 'browserrt', 'opfs', 'lock', 'target']
    }, async ({ cdp, evalJson, pageState, pageUrl, cdpPort, listUrl, browserVersion }) => {
      const browserCdpConnection = await connectBrowserCdp(cdpPort, 10000);
      const browserCdp = browserCdpConnection.cdp;
      let pageB = null;
      try {
        const tabA = await evalJson(initParticipantExpression('A', prefixSuffix), 25000);
        pageB = await openPageTarget(browserCdp, { listUrl, url: `${pageUrl}?tab=B`, timeoutMs: 10000 });
        const evalB = (expression, ms = 25000) => evalCdpJson(pageB.cdp, expression, ms);
        const tabB = await evalB(initParticipantExpression('B', prefixSuffix), 25000);
        assert.equal(tabA.environment.isSecureContext, true, 'tab A must be secure context');
        assert.equal(tabB.environment.isSecureContext, true, 'tab B must be secure context');
        assert.equal(tabA.environment.hasOpfs, true, 'tab A must expose OPFS');
        assert.equal(tabB.environment.hasOpfs, true, 'tab B must expose OPFS');
        assert.equal(tabA.environment.hasWebLocks, true, 'tab A must expose Web Locks');
        assert.equal(tabB.environment.hasWebLocks, true, 'tab B must expose Web Locks');
        assert.equal(tabA.namespace?.storage, true, 'tab A must use the storage namespace');
        assert.equal(tabA.namespace?.coordination, true, 'tab A must use the coordination namespace');
        assert.equal(tabB.namespace?.storage, true, 'tab B must use the storage namespace');
        assert.equal(tabB.namespace?.coordination, true, 'tab B must use the coordination namespace');
        assert.equal(tabA.prefix, tabB.prefix, 'tabs must share OPFS prefix');
        assert.equal(tabA.lockName, tabB.lockName, 'tabs must share Web Lock name');
        assert.equal(new URL(tabA.environment.href).origin, new URL(tabB.environment.href).origin, 'tabs must share origin');

        const hold = await evalJson(callParticipantExpression('startExclusiveHold', { acquireTimeoutMs: 2000 }), 5000);
        assert.equal(hold.hold.acquired, true, 'tab A must acquire exclusive hold');
        const timedOut = await evalB(callParticipantExpression('attemptTimedPutWhileLocked', { timeoutMs: 120, labelSuffix: 'b-pending-timeout-before-release' }), 5000);
        assert.equal(timedOut.timedOut, true, 'tab B write should time out while tab A holds the same Web Lock');
        assert.match(String(timedOut.expectedDigest || ''), /^sha256:[0-9a-f]{64}$/, 'timed-out queued request must report the content-addressed digest so ghost writes can be checked after release');
        const queuedStart = await evalB(callParticipantExpression('startQueuedPutWhileLocked', { opId: 'tab-b-queued-waiter-after-release', timeoutMs: 2500, labelSuffix: 'b-queued-waiter-after-release' }), 5000);
        assert.equal(queuedStart.started, true, 'tab B must start a queued write while tab A still holds the same Web Lock');
        let pendingBeforeRelease = null;
        for (let attempt = 0; attempt < 20; attempt += 1) {
          pendingBeforeRelease = await evalB(callParticipantExpression('queryLocks', {}), 2000);
          if ((pendingBeforeRelease.result?.pendingCount || 0) >= 1 && (pendingBeforeRelease.result?.heldCount || 0) >= 1) break;
          await new Promise((resolve) => setTimeout(resolve, 50));
        }
        assert.ok((pendingBeforeRelease?.result?.pendingCount || 0) >= 1, 'tab B queued waiter must be visible as pending before tab A releases');
        assert.ok((pendingBeforeRelease?.result?.heldCount || 0) >= 1, 'tab A exclusive hold must still be visible while tab B is pending');
        const release = await evalJson(callParticipantExpression('releaseExclusiveHold', {}), 5000);
        assert.equal(release.result.released, true, 'tab A must release exclusive hold');
        const queuedComplete = await evalB(callParticipantExpression('awaitQueuedPut', { opId: 'tab-b-queued-waiter-after-release' }), 10000);
        assert.equal(queuedComplete.row.ok, true, 'tab B queued waiter must acquire and write after tab A releases');
        assert.equal(queuedComplete.row.digestMatches, true, 'tab B queued waiter read/verify digest must match after release');
        assert.equal(queuedComplete.row.budgetChecked, true, 'tab B queued waiter must keep write-budget checks on');
        const timedOutAbsentAfterRelease = await evalB(callParticipantWithRefExpression('verifyDigestAbsentViaStorageLane', timedOut.expectedDigest, { opId: 'tab-b-timed-out-ghost-write-check' }), 10000);
        assert.equal(timedOutAbsentAfterRelease.absent, true, 'the timed-out queued request must not ghost-write its digest after the lock holder releases');
        assert.equal(timedOutAbsentAfterRelease.adapterSnapshotValid, true, 'timed-out ghost-write absence check must preserve adapter health');
        const settledAfterReleaseA = await evalJson(callParticipantExpression('settled', { timeoutMs: 1500 }), 5000);
        const settledAfterReleaseB = await evalB(callParticipantExpression('settled', { timeoutMs: 1500 }), 5000);
        assert.equal(settledAfterReleaseA.ok, true, 'tab A lock queue must settle after release');
        assert.equal(settledAfterReleaseB.ok, true, 'tab B lock queue must settle after timeout/release/queued-write completion');

        const writeA = await evalJson(callParticipantExpression('writeViaStorageLane', { opId: 'tab-a-after-release', phase: 'after-release' }), 10000);
        const writeB = await evalB(callParticipantExpression('writeViaStorageLane', { opId: 'tab-b-after-release', phase: 'after-release' }), 10000);
        assert.equal(writeA.verifyOk, true, 'tab A write must verify');
        assert.equal(writeB.verifyOk, true, 'tab B write must verify');
        assert.equal(writeA.readDigest, writeA.expectedDigest, 'tab A self-read digest must match');
        assert.equal(writeB.readDigest, writeB.expectedDigest, 'tab B self-read digest must match');
        const aReadsB = await evalJson(callParticipantWithRefExpression('readRefViaStorageLane', writeB.ref, { opId: 'tab-a-read-tab-b', expectedDigest: writeB.expectedDigest }), 10000);
        const bReadsA = await evalB(callParticipantWithRefExpression('readRefViaStorageLane', writeA.ref, { opId: 'tab-b-read-tab-a', expectedDigest: writeA.expectedDigest }), 10000);
        assert.equal(aReadsB.digestMatches, true, 'tab A must read tab B block by ref from shared OPFS prefix');
        assert.equal(bReadsA.digestMatches, true, 'tab B must read tab A block by ref from shared OPFS prefix');

        const cleanup = await evalJson(callParticipantExpression('cleanup', {}), 10000);
        assert.equal(cleanup.result, true, 'cleanup must remove shared OPFS prefix');
        const finalASettled = await evalJson(callParticipantExpression('settled', { timeoutMs: 1500 }), 5000);
        const finalBSettled = await evalB(callParticipantExpression('settled', { timeoutMs: 1500 }), 5000);
        assert.equal(finalASettled.ok, true, 'tab A locks must settle at end');
        assert.equal(finalBSettled.ok, true, 'tab B locks must settle at end');
        const closeA = await evalJson(callParticipantExpression('close', {}), 5000);
        const closeB = await evalB(callParticipantExpression('close', {}), 5000);
        const observed = Object.freeze({
          imports: { publicApiOnly: true, importSpecifier: 'browserrt' },
          environment: {
            sameOrigin: new URL(tabA.environment.href).origin === new URL(tabB.environment.href).origin,
            samePrefix: tabA.prefix === tabB.prefix,
            sameLockName: tabA.lockName === tabB.lockName,
            isSecureContext: tabA.environment.isSecureContext === true && tabB.environment.isSecureContext === true,
            hasOpfs: tabA.environment.hasOpfs === true && tabB.environment.hasOpfs === true,
            hasWebLocks: tabA.environment.hasWebLocks === true && tabB.environment.hasWebLocks === true,
            tabA: tabA.environment,
            tabB: tabB.environment
          },
          namespace: { storage: tabA.namespace?.storage === true && tabB.namespace?.storage === true, coordination: tabA.namespace?.coordination === true && tabB.namespace?.coordination === true, tabA: tabA.namespace, tabB: tabB.namespace },
          tabs: { preparedCount: 2, tabIds: ['A', 'B'], tabA: { prefix: tabA.prefix, lockName: tabA.lockName, provider: tabA.provider }, tabB: { prefix: tabB.prefix, lockName: tabB.lockName, provider: tabB.provider } },
          contention: {
            holdAcquired: hold.hold.acquired === true,
            holdReleased: release.result.released === true,
            timedOutBeforeRelease: timedOut.timedOut === true,
            timedOutExpectedDigest: timedOut.expectedDigest || null,
            timedOutDigestAbsentAfterRelease: timedOutAbsentAfterRelease.absent === true,
            timedOutNoMutationAfterRelease: timedOut.timedOut === true && timedOutAbsentAfterRelease.absent === true && timedOutAbsentAfterRelease.adapterSnapshotValid === true,
            timeoutName: timedOut.error?.name || null,
            timeoutCode: timedOut.error?.code || null,
            timeoutMessage: timedOut.error?.message || null,
            queuedWaiterPendingBeforeRelease: (pendingBeforeRelease?.result?.pendingCount || 0) >= 1 && (pendingBeforeRelease?.result?.heldCount || 0) >= 1,
            queuedWaiterCompletedAfterRelease: queuedComplete.row?.ok === true && queuedComplete.row?.completedAt >= queuedComplete.row?.startedAt,
            queuedWaiterDigestMatches: queuedComplete.row?.digestMatches === true,
            queuedWaiterBudgetChecked: queuedComplete.row?.budgetChecked === true,
            writeAfterReleaseOk: writeA.verifyOk === true && writeB.verifyOk === true,
            queuedStart,
            pendingBeforeRelease: pendingBeforeRelease?.result || null,
            queuedComplete: queuedComplete.row || null,
            timedOutAbsentAfterRelease
          },
          storage: {
            writeA,
            writeB,
            aAdapterSnapshotValid: writeA.adapterSnapshotValid === true && aReadsB.adapterSnapshotValid === true,
            bAdapterSnapshotValid: writeB.adapterSnapshotValid === true && bReadsA.adapterSnapshotValid === true
          },
          crossRead: {
            aReadBDigestMatches: aReadsB.digestMatches === true,
            bReadADigestMatches: bReadsA.digestMatches === true,
            aReadsB,
            bReadsA
          },
          locks: {
            aSettled: finalASettled.ok === true,
            bSettled: finalBSettled.ok === true,
            settledAfterReleaseA: settledAfterReleaseA.ok === true,
            settledAfterReleaseB: settledAfterReleaseB.ok === true,
            aStats: closeA.store?.guard?.stats || null,
            bStats: closeB.store?.guard?.stats || null
          },
          cleanup: { accepted: cleanup.accepted === true, result: cleanup.result === true },
          trace: {
            aClosed: closeA.closed === true && closeA.traceKinds?.includes('runtime:close'),
            bClosed: closeB.closed === true && closeB.traceKinds?.includes('runtime:close'),
            aKinds: closeA.traceKinds || [],
            bKinds: closeB.traceKinds || []
          }
        });
        const receipt = createBrowserCrossTabOpfsProductWedgeReceipt({ observed, generatedAt: 'deterministic-installed-browser-cross-tab-opfs-package-proof', source: 'installed-browser-cross-tab-opfs-package-consumer.html' });
        const validation = validateBrowserCrossTabOpfsProductWedgeReceipt(receipt);
        assert.equal(receipt.proof?.namespacedFacadeUsed, true, 'cross-tab receipt must prove product namespaces');
        assert.equal(validation.ok, true, validation.errors.join('; '));
        return { pageUrl, pageState, browserVersion, tabA, tabB, observed, receipt, validation };
      } finally {
        if (pageB) await pageB.close();
        browserCdp.close();
      }
    });

    const receipt = browser.result.receipt;
    const validation = browser.result.validation;
    return Object.freeze({
      project: 'BrowserRT',
      revision: REVISION,
      version: VERSION,
      schema: 1,
      status: 'passed',
      probe_id: `${REVISION}-package-installed-browser-cross-tab-opfs-consumer`,
      purpose: 'Package-installed browser cross-tab OPFS consumer proof: npm pack, local install, package-root public API import in two managed Chromium tabs, shared OPFS prefix, same Web Lock name, queued pending-lock timeout before acquisition, proof that the timed-out request does not ghost-write after holder release, a second queued waiter that remains pending then acquires after release, successful writes after release, cross-tab reads by ref, settled locks, cleanup, and receipt validation.',
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
        pageUrl: browser.result.pageUrl,
        pageState: browser.result.pageState,
        cdp: browser.harness.cdp,
        requestCount: browser.harness.server?.requestCount ?? null,
        durationMs: browser.harness.durationMs,
        chromeStderrSummary: browser.harness.chromeStderrSummary
      },
      consumer: {
        importSpecifier: 'browserrt',
        status: receipt.status,
        proof: receipt.proof,
        validation,
        environment: receipt.observed.environment,
        contention: receipt.observed.contention,
        locks: receipt.observed.locks,
        storage: {
          writeA: { digest: receipt.observed.storage.writeA.digest, path: receipt.observed.storage.writeA.path, budgetChecked: receipt.observed.storage.writeA.budgetChecked },
          writeB: { digest: receipt.observed.storage.writeB.digest, path: receipt.observed.storage.writeB.path, budgetChecked: receipt.observed.storage.writeB.budgetChecked },
          queuedWaiter: receipt.observed.contention.queuedComplete || null,
          crossRead: receipt.observed.crossRead
        }
      },
      receipt,
      commands: {
        pack: 'npm pack --json --pack-destination <tmp>',
        install: `npm install --ignore-scripts --no-audit --no-fund ${packInfo.filename}`,
        serve: 'managed Chromium via tools/browser_cdp_fixture.mjs',
        run: 'two same-origin page targets import browserrt via import map and product namespaces, hold one Web Lock, time out one queued tab request, keep a second queued waiter pending until release, release, prove the timed-out digest is absent, write/read through storage-lane, and validate cross-tab receipt'
      },
      nonClaims: receipt.nonClaims
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
    const report = { project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1, status: 'failed', probe_id: `${REVISION}-package-installed-browser-cross-tab-opfs-consumer`, error: { name: error?.name || 'Error', message: error?.message || String(error), stack: error?.stack, command: error?.result || null } };
    await mkdir(dirname(out), { recursive: true });
    await writeFile(out, JSON.stringify(report, null, 2) + '\n');
    console.error(out);
    console.error(`[package_installed_browser_cross_tab_opfs_consumer_probe] FAIL: ${error?.stack || error}`);
    process.exitCode = 1;
  }
}
