#!/usr/bin/env node
import assert from 'node:assert/strict';
import { mkdir, mkdtemp, readFile, rm, writeFile } from 'node:fs/promises';
import { dirname, join } from 'node:path';
import { tmpdir } from 'node:os';
import { REVISION, VERSION } from '../src/public-api.mjs';
import {
  runManagedBrowserPage,
  connectBrowserCdp,
  openPageTarget,
  evalJson as evalCdpJson,
  sleep
} from './browser_cdp_fixture.mjs';
import {
  createBrowserTabCloseOpfsProductWedgeReceipt,
  validateBrowserTabCloseOpfsProductWedgeReceipt
} from '../examples/browser-cross-tab-opfs-product-wedge-consumer.mjs';

import { preparePackageTarballForProbe, runNpmForPackageFixture } from './lib/package_installed_fixture.mjs';
const DEFAULT_OUT = `artifacts/validation/REV${REVISION.slice(3)}-PACKAGE-INSTALLED-BROWSER-TAB-CLOSE-OPFS-CONSUMER-PROBE.json`;
const argValue = (argv, flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };

const PAGE = `<!doctype html>
<meta charset="utf-8">
<title>BrowserRT installed browser tab-close OPFS consumer proof</title>
<script>
  window.__BROWSERRT_PACKAGE_BROWSER_TAB_CLOSE_OPFS_ERROR = null;
  window.addEventListener('error', (event) => {
    window.__BROWSERRT_PACKAGE_BROWSER_TAB_CLOSE_OPFS_ERROR = { type: 'error', message: event.message, filename: event.filename, lineno: event.lineno, colno: event.colno };
  });
  window.addEventListener('unhandledrejection', (event) => {
    const reason = event.reason || {};
    window.__BROWSERRT_PACKAGE_BROWSER_TAB_CLOSE_OPFS_ERROR = { type: 'unhandledrejection', message: reason.message || String(reason), stack: reason.stack || null, code: reason.code || null };
  });
</script>
<script type="importmap">
{
  "imports": {
    "browserrt": "/node_modules/browserrt/src/public-api.mjs"
  }
}
</script>
<body>BrowserRT installed browser tab-close OPFS consumer proof</body>
`;

function jsonExpression(source) {
  return `(async()=>{ const value = await (${source})(); return JSON.stringify(value); })()`;
}

function initParticipantExpression(tabId, prefixSuffix) {
  return jsonExpression(`async()=>{
    if (window.__BROWSERRT_PACKAGE_BROWSER_TAB_CLOSE_OPFS_ERROR) throw new Error(JSON.stringify(window.__BROWSERRT_PACKAGE_BROWSER_TAB_CLOSE_OPFS_ERROR));
    const api = await import('browserrt');
    const mod = await import('/node_modules/browserrt/examples/browser-cross-tab-opfs-product-wedge-consumer.mjs');
    const participant = await mod.createBrowserCrossTabOpfsParticipantWithApi(api, {
      tabId: ${JSON.stringify(tabId)},
      generatedAt: 'deterministic-installed-browser-tab-close-opfs-package-proof',
      source: 'installed-browser-tab-close-opfs-package-consumer.html',
      importSpecifier: 'browserrt',
      prefixSuffix: ${JSON.stringify(prefixSuffix)},
      lockTimeoutMs: 1200
    });
    window.__BROWSERRT_TAB_CLOSE_OPFS_PARTICIPANT = participant;
    return await participant.prepare();
  }`);
}

function callParticipantExpression(method, args = {}) {
  return jsonExpression(`async()=>{
    if (window.__BROWSERRT_PACKAGE_BROWSER_TAB_CLOSE_OPFS_ERROR) throw new Error(JSON.stringify(window.__BROWSERRT_PACKAGE_BROWSER_TAB_CLOSE_OPFS_ERROR));
    if (!window.__BROWSERRT_TAB_CLOSE_OPFS_PARTICIPANT) throw new Error('BrowserRT tab-close participant not initialized');
    return await window.__BROWSERRT_TAB_CLOSE_OPFS_PARTICIPANT[${JSON.stringify(method)}](${JSON.stringify(args)});
  }`);
}

function callParticipantWithRefExpression(method, ref, args = {}) {
  return jsonExpression(`async()=>{
    if (window.__BROWSERRT_PACKAGE_BROWSER_TAB_CLOSE_OPFS_ERROR) throw new Error(JSON.stringify(window.__BROWSERRT_PACKAGE_BROWSER_TAB_CLOSE_OPFS_ERROR));
    if (!window.__BROWSERRT_TAB_CLOSE_OPFS_PARTICIPANT) throw new Error('BrowserRT tab-close participant not initialized');
    return await window.__BROWSERRT_TAB_CLOSE_OPFS_PARTICIPANT[${JSON.stringify(method)}](${JSON.stringify(ref)}, ${JSON.stringify(args)});
  }`);
}

export async function runProbe() {
  const root = process.cwd();
  const workspace = await mkdtemp(join(tmpdir(), 'browserrt-package-browser-tab-close-opfs-smoke-'));
  const packDir = join(workspace, 'pack');
  const consumerDir = join(workspace, 'consumer');
  await mkdir(packDir, { recursive: true });
  await mkdir(consumerDir, { recursive: true });
  try {
    const packageTarball = await preparePackageTarballForProbe({ root, packDir });
    const { packInfo, tarball, fileNames } = packageTarball;
    assert.ok(packInfo?.filename, 'npm pack did not report a filename');
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
    assert.deepEqual(missingTarballFiles, [], `npm package missing tab-close OPFS dependency files: ${missingTarballFiles.join(', ')}`);
    const forbiddenPrefixes = ['artifacts/', 'tools/', 'test/', 'node_modules/'];
    const forbiddenFiles = fileNames.filter((name) => forbiddenPrefixes.some((prefix) => name.startsWith(prefix)));
    assert.deepEqual(forbiddenFiles, [], `npm package leaked development-only files: ${forbiddenFiles.slice(0, 12).join(', ')}`);

    runNpmForPackageFixture('npm', ['init', '-y'], { cwd: consumerDir });
    runNpmForPackageFixture('npm', ['install', '--ignore-scripts', '--no-audit', '--no-fund', tarball], { cwd: consumerDir });
    const installedExample = await readFile(join(consumerDir, 'node_modules', 'browserrt', 'examples', 'browser-cross-tab-opfs-product-wedge-consumer.mjs'), 'utf8');
    assert.match(installedExample, /startExclusiveWriteHold/, 'installed cross-tab example must expose a write-while-holding method for tab-close proof');
    assert.match(installedExample, /createBrowserTabCloseOpfsProductWedgeReceipt/, 'installed cross-tab example must expose tab-close receipt helpers');
    assert.match(installedExample, /rt\.storage\.opfsWebLockGuardedBlockStoreWithPosture/, 'installed tab-close OPFS example must use the postured guarded storage namespace');
    assert.doesNotMatch(installedExample, /writeBudgetGuard: \{ requireEstimate: true, minFreeBytes: 0, maxUsageRatio: 1 \}/, 'installed tab-close OPFS example must not hand-wire raw per-put write-budget guards');
    assert.match(installedExample, /writeBudgetGuardSource/, 'installed tab-close OPFS example must expose posture-derived write-budget provenance');
    assert.match(installedExample, /rt\.coordination\.crossLaneScheduler/, 'installed tab-close OPFS example must use the coordination namespace');
    const installedPackageJson = JSON.parse(await readFile(join(consumerDir, 'node_modules', 'browserrt', 'package.json'), 'utf8'));
    const prefixSuffix = `installed-tab-close-${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 8)}`;

    const browser = await runManagedBrowserPage({
      root: consumerDir,
      pagePath: '/installed-browser-tab-close-opfs-consumer.html',
      pageTitle: 'BrowserRT installed browser tab-close OPFS consumer proof',
      body: PAGE,
      allowedPrefixes: ['node_modules/browserrt/src/', 'node_modules/browserrt/examples/'],
      timeoutMs: 35000,
      stderrTerms: ['import', 'module', 'browserrt', 'opfs', 'lock', 'target', 'close']
    }, async ({ evalJson, pageState, pageUrl, cdpPort, listUrl, browserVersion }) => {
      const browserCdpConnection = await connectBrowserCdp(cdpPort, 10000);
      const browserCdp = browserCdpConnection.cdp;
      let holderPage = null;
      try {
        const survivor = await evalJson(initParticipantExpression('B', prefixSuffix), 25000);
        holderPage = await openPageTarget(browserCdp, { listUrl, url: `${pageUrl}?holder=A`, timeoutMs: 10000 });
        const evalHolder = (expression, ms = 25000) => evalCdpJson(holderPage.cdp, expression, ms);
        const holder = await evalHolder(initParticipantExpression('A', prefixSuffix), 25000);
        assert.equal(holder.environment.isSecureContext, true, 'holder tab must be secure context');
        assert.equal(survivor.environment.isSecureContext, true, 'survivor tab must be secure context');
        assert.equal(holder.environment.hasOpfs, true, 'holder tab must expose OPFS');
        assert.equal(survivor.environment.hasOpfs, true, 'survivor tab must expose OPFS');
        assert.equal(holder.environment.hasWebLocks, true, 'holder tab must expose Web Locks');
        assert.equal(survivor.environment.hasWebLocks, true, 'survivor tab must expose Web Locks');
        assert.equal(holder.namespace?.storage, true, 'holder tab must use the storage namespace');
        assert.equal(holder.namespace?.coordination, true, 'holder tab must use the coordination namespace');
        assert.equal(survivor.namespace?.storage, true, 'survivor tab must use the storage namespace');
        assert.equal(survivor.namespace?.coordination, true, 'survivor tab must use the coordination namespace');
        assert.equal(holder.prefix, survivor.prefix, 'tabs must share OPFS prefix');
        assert.equal(holder.lockName, survivor.lockName, 'tabs must share Web Lock name');
        assert.equal(new URL(holder.environment.href).origin, new URL(survivor.environment.href).origin, 'tabs must share origin');

        const hold = await evalHolder(callParticipantExpression('startExclusiveWriteHold', { acquireTimeoutMs: 2500, phase: 'holder-tab-close-open-ended-write' }), 10000);
        assert.equal(hold.hold.acquired, true, 'holder tab must acquire exclusive write-hold');
        assert.equal(hold.hold.write?.verifyOk, true, 'holder tab write must verify before the tab is closed');
        assert.equal(hold.hold.write?.readDigestMatches, true, 'holder tab write must self-read before close');
        assert.equal(hold.hold.write?.budgetChecked, true, 'holder tab write must check storage budget before close');
        const queryWhileHeld = await evalJson(callParticipantExpression('queryLocks', {}), 5000);
        if (queryWhileHeld.result?.available === true) assert.ok(queryWhileHeld.result.heldCount >= 1, 'survivor tab should observe the holder Web Lock before close');
        const timedOut = await evalJson(callParticipantExpression('attemptTimedPutWhileLocked', { timeoutMs: 120, labelSuffix: 'survivor-pending-timeout-before-holder-close' }), 5000);
        assert.equal(timedOut.timedOut, true, 'survivor tab write should time out while holder tab owns the Web Lock');

        const closeHolder = await holderPage.close();
        const holderTargetClosed = closeHolder?.result?.success !== false && !closeHolder?.error;
        assert.equal(holderTargetClosed, true, `holder target must close through CDP: ${JSON.stringify(closeHolder)}`);
        holderPage = null;
        await sleep(300);
        const settledAfterClose = await evalJson(callParticipantExpression('settled', { timeoutMs: 2500 }), 5000);
        assert.equal(settledAfterClose.ok, true, 'survivor tab lock queue must settle after holder tab close');
        const queryAfterClose = await evalJson(callParticipantExpression('queryLocks', {}), 5000);
        if (queryAfterClose.result?.available === true) assert.equal(queryAfterClose.result.heldCount, 0, 'no held lock rows should remain after holder tab close');

        const survivorWrite = await evalJson(callParticipantExpression('writeViaStorageLane', { opId: 'survivor-after-holder-close', phase: 'after-holder-tab-close' }), 10000);
        assert.equal(survivorWrite.verifyOk, true, 'survivor write after tab close must verify');
        assert.equal(survivorWrite.readDigest, survivorWrite.expectedDigest, 'survivor self-read after tab close must match');
        const holderRead = await evalJson(callParticipantWithRefExpression('readRefViaStorageLane', hold.hold.write.ref, { opId: 'survivor-read-holder-after-tab-close', expectedDigest: hold.hold.write.expectedDigest }), 10000);
        assert.equal(holderRead.digestMatches, true, 'survivor must read the holder tab block by ref after holder tab close');
        assert.equal(holderRead.verifyOk, true, 'survivor must verify the holder tab block by ref after holder tab close');

        const cleanup = await evalJson(callParticipantExpression('cleanup', {}), 10000);
        assert.equal(cleanup.result, true, 'cleanup must remove shared OPFS prefix');
        const finalSettled = await evalJson(callParticipantExpression('settled', { timeoutMs: 1500 }), 5000);
        assert.equal(finalSettled.ok, true, 'survivor locks must settle at end');
        const closeSurvivor = await evalJson(callParticipantExpression('close', {}), 5000);

        const observed = Object.freeze({
          imports: { publicApiOnly: true, importSpecifier: 'browserrt' },
          environment: {
            sameOrigin: new URL(holder.environment.href).origin === new URL(survivor.environment.href).origin,
            samePrefix: holder.prefix === survivor.prefix,
            sameLockName: holder.lockName === survivor.lockName,
            isSecureContext: holder.environment.isSecureContext === true && survivor.environment.isSecureContext === true,
            hasOpfs: holder.environment.hasOpfs === true && survivor.environment.hasOpfs === true,
            hasWebLocks: holder.environment.hasWebLocks === true && survivor.environment.hasWebLocks === true,
            holder: holder.environment,
            survivor: survivor.environment
          },
          namespace: { storage: holder.namespace?.storage === true && survivor.namespace?.storage === true, coordination: holder.namespace?.coordination === true && survivor.namespace?.coordination === true, holder: holder.namespace, survivor: survivor.namespace },
          tabs: { preparedCount: 2, holderTabId: 'A', survivorTabId: 'B', holder: { prefix: holder.prefix, lockName: holder.lockName, provider: holder.provider }, survivor: { prefix: survivor.prefix, lockName: survivor.lockName, provider: survivor.provider } },
          termination: {
            holderAcquired: hold.hold.acquired === true,
            holderWriteVerified: hold.hold.write?.verifyOk === true && hold.hold.write?.readDigestMatches === true,
            holderWriteBudgetChecked: hold.hold.write?.budgetChecked === true,
            survivorTimedOutBeforeClose: timedOut.timedOut === true,
            timeoutName: timedOut.error?.name || null,
            timeoutCode: timedOut.error?.code || null,
            timeoutMessage: timedOut.error?.message || null,
            holderTargetClosed,
            closeHolder,
            survivorSettledAfterClose: settledAfterClose.ok === true,
            survivorWriteAfterCloseOk: survivorWrite.verifyOk === true && survivorWrite.readDigest === survivorWrite.expectedDigest
          },
          locks: {
            queryWhileHeld: queryWhileHeld.result,
            queryAfterClose: queryAfterClose.result,
            settledAfterClose: settledAfterClose.result,
            finalSettled: finalSettled.result,
            survivorStats: closeSurvivor.store?.guard?.stats || null
          },
          storage: {
            posturedGuardedFactoryUsed: holder.storagePosture?.posturedGuardedFactoryUsed === true && survivor.storagePosture?.posturedGuardedFactoryUsed === true,
            postureStatus: holder.storagePosture?.postureStatus === 'observed' && survivor.storagePosture?.postureStatus === 'observed' ? 'observed' : 'partial',
            admissionStatus: holder.storagePosture?.admissionStatus === 'admit-with-guard' && survivor.storagePosture?.admissionStatus === 'admit-with-guard' ? 'admit-with-guard' : 'not-admitted',
            writeBudgetGuardSource: holder.storagePosture?.writeBudgetGuardSource === survivor.storagePosture?.writeBudgetGuardSource ? holder.storagePosture?.writeBudgetGuardSource || null : 'mismatch',
            lockContentionPolicy: holder.storagePosture?.lockContentionPolicy?.enabled === true && survivor.storagePosture?.lockContentionPolicy?.enabled === true && holder.storagePosture?.lockContentionPolicy?.source === 'postured-web-lock-guarded-opfs-factory' && survivor.storagePosture?.lockContentionPolicy?.source === 'postured-web-lock-guarded-opfs-factory' ? holder.storagePosture.lockContentionPolicy : null,
            holderStoragePosture: holder.storagePosture || null,
            survivorStoragePosture: survivor.storagePosture || null,
            holderWrite: hold.hold.write,
            survivorWrite,
            survivorReadHolder: holderRead,
            survivorReadHolderDigestMatches: holderRead.digestMatches === true,
            holderVerifyDigestMatches: holderRead.verifyDigest === hold.hold.write.expectedDigest,
            survivorAdapterSnapshotValid: survivorWrite.adapterSnapshotValid === true && holderRead.adapterSnapshotValid === true
          },
          cleanup: { accepted: cleanup.accepted === true, result: cleanup.result === true },
          trace: {
            holderClosedByTarget: holderTargetClosed,
            survivorClosed: closeSurvivor.closed === true && closeSurvivor.traceKinds?.includes('runtime:close'),
            survivorKinds: closeSurvivor.traceKinds || []
          }
        });
        const receipt = createBrowserTabCloseOpfsProductWedgeReceipt({ observed, generatedAt: 'deterministic-installed-browser-tab-close-opfs-package-proof', source: 'installed-browser-tab-close-opfs-package-consumer.html' });
        const validation = validateBrowserTabCloseOpfsProductWedgeReceipt(receipt);
        assert.equal(receipt.proof?.namespacedFacadeUsed, true, 'tab-close receipt must prove product namespaces');
        assert.equal(receipt.proof?.posturedGuardedFactoryUsed, true, 'tab-close receipt must prove the postured guarded factory and posture-derived budget guard');
        assert.equal(validation.ok, true, validation.errors.join('; '));
        return { pageUrl, pageState, browserVersion, holder, survivor, observed, receipt, validation };
      } finally {
        if (holderPage) await holderPage.close();
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
      probe_id: `${REVISION}-package-installed-browser-tab-close-opfs-consumer`,
      purpose: 'Package-installed browser tab-close OPFS proof: npm pack, local install, package-root public API import in two managed Chromium tabs, holder tab acquires an exclusive Web Lock and writes a real OPFS block, survivor times out before close, holder page target closes, survivor recovers, writes, reads holder block by ref, settles locks, cleans up, and validates a receipt.',
      package: {
        name: packInfo.name,
        version: packInfo.version,
        filename: packInfo.filename,
        fileCount: fileNames.length,
        unpackedSize: packInfo.unpackedSize,
        requiredTarballFiles,
        requiredTarballFilesPresent: true,
        forbiddenFilesAbsent: true,
        preparedPackageSource: packageTarball.source,
        reusedPreparedTarball: packageTarball.reusedPreparedTarball === true,
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
        termination: receipt.observed.termination,
        locks: receipt.observed.locks,
        storage: {
          posturedGuardedFactoryUsed: receipt.observed.storage.posturedGuardedFactoryUsed,
          writeBudgetGuardSource: receipt.observed.storage.writeBudgetGuardSource,
          lockContentionPolicy: receipt.observed.storage.lockContentionPolicy,
          holderWrite: { digest: receipt.observed.storage.holderWrite.digest, path: receipt.observed.storage.holderWrite.path, budgetChecked: receipt.observed.storage.holderWrite.budgetChecked },
          survivorWrite: { digest: receipt.observed.storage.survivorWrite.digest, path: receipt.observed.storage.survivorWrite.path, budgetChecked: receipt.observed.storage.survivorWrite.budgetChecked },
          survivorReadHolder: receipt.observed.storage.survivorReadHolder
        }
      },
      receipt,
      commands: {
        pack: 'npm pack --json --pack-destination <tmp>',
        install: `npm install --ignore-scripts --no-audit --no-fund ${packInfo.filename}`,
        serve: 'managed Chromium via tools/browser_cdp_fixture.mjs',
        run: 'two same-origin page targets import browserrt via import map and product namespaces; holder writes while holding a Web Lock; survivor times out, holder target closes, survivor writes/reads and validates receipt'
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
    const report = { project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1, status: 'failed', probe_id: `${REVISION}-package-installed-browser-tab-close-opfs-consumer`, error: { name: error?.name || 'Error', message: error?.message || String(error), stack: error?.stack, command: error?.result || null } };
    await mkdir(dirname(out), { recursive: true });
    await writeFile(out, JSON.stringify(report, null, 2) + '\n');
    console.error(out);
    console.error(`[package_installed_browser_tab_close_opfs_consumer_probe] FAIL: ${error?.stack || error}`);
    process.exitCode = 1;
  }
}
