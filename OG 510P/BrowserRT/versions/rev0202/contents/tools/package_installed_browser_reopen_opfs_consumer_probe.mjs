#!/usr/bin/env node
import assert from 'node:assert/strict';
import { mkdir, mkdtemp, readFile, rm, writeFile } from 'node:fs/promises';
import { dirname, join } from 'node:path';
import { tmpdir } from 'node:os';
import { REVISION, VERSION } from '../src/public-api.mjs';
import { runManagedBrowserPage, sleep } from './browser_cdp_fixture.mjs';
import {
  createBrowserOpfsReopenProductWedgeReceipt,
  validateBrowserOpfsReopenProductWedgeReceipt
} from '../examples/browser-opfs-reopen-product-wedge-consumer.mjs';

import { preparePackageTarballForProbe, runNpmForPackageFixture } from './lib/package_installed_fixture.mjs';
const DEFAULT_OUT = `artifacts/validation/REV${REVISION.slice(3)}-PACKAGE-INSTALLED-BROWSER-OPFS-REOPEN-CONSUMER-PROBE.json`;
const argValue = (argv, flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };

const PAGE = `<!doctype html>
<meta charset="utf-8">
<title>BrowserRT installed browser OPFS reopen consumer proof</title>
<script>
  window.__BROWSERRT_PACKAGE_BROWSER_OPFS_REOPEN_ERROR = null;
  window.__BROWSERRT_PAGE_LOAD_ID = (globalThis.crypto && crypto.randomUUID) ? crypto.randomUUID() : String(Date.now()) + ':' + String(Math.random());
  window.addEventListener('error', (event) => {
    window.__BROWSERRT_PACKAGE_BROWSER_OPFS_REOPEN_ERROR = { type: 'error', message: event.message, filename: event.filename, lineno: event.lineno, colno: event.colno };
  });
  window.addEventListener('unhandledrejection', (event) => {
    const reason = event.reason || {};
    window.__BROWSERRT_PACKAGE_BROWSER_OPFS_REOPEN_ERROR = { type: 'unhandledrejection', message: reason.message || String(reason), stack: reason.stack || null, code: reason.code || null };
  });
</script>
<script type="importmap">
{
  "imports": {
    "browserrt": "/node_modules/browserrt/src/public-api.mjs"
  }
}
</script>
<body>BrowserRT installed browser OPFS reopen consumer proof</body>
`;

function jsonExpression(source) {
  return `(async()=>{ const value = await (${source})(); return JSON.stringify(value); })()`;
}

function pageLoadIdExpression() {
  return jsonExpression(`async()=>({ pageLoadId: window.__BROWSERRT_PAGE_LOAD_ID || null, href: location.href, readyState: document.readyState, error: window.__BROWSERRT_PACKAGE_BROWSER_OPFS_REOPEN_ERROR || null })`);
}

function writeExpression(prefixSuffix) {
  return jsonExpression(`async()=>{
    if (window.__BROWSERRT_PACKAGE_BROWSER_OPFS_REOPEN_ERROR) throw new Error(JSON.stringify(window.__BROWSERRT_PACKAGE_BROWSER_OPFS_REOPEN_ERROR));
    const api = await import('browserrt');
    const mod = await import('/node_modules/browserrt/examples/browser-opfs-reopen-product-wedge-consumer.mjs');
    return await mod.writeBrowserOpfsReopenBlockWithApi(api, {
      generatedAt: 'deterministic-installed-browser-opfs-reopen-package-proof-write',
      source: 'installed-browser-opfs-reopen-package-consumer.html',
      importSpecifier: 'browserrt',
      prefixSuffix: ${JSON.stringify(prefixSuffix)},
      lockTimeoutMs: 2000,
      pageLoadId: window.__BROWSERRT_PAGE_LOAD_ID || null
    });
  }`);
}

function readExpression({ ref, expectedDigest, prefixSuffix }) {
  return jsonExpression(`async()=>{
    if (window.__BROWSERRT_PACKAGE_BROWSER_OPFS_REOPEN_ERROR) throw new Error(JSON.stringify(window.__BROWSERRT_PACKAGE_BROWSER_OPFS_REOPEN_ERROR));
    const api = await import('browserrt');
    const mod = await import('/node_modules/browserrt/examples/browser-opfs-reopen-product-wedge-consumer.mjs');
    return await mod.readBrowserOpfsReopenBlockWithApi(api, {
      generatedAt: 'deterministic-installed-browser-opfs-reopen-package-proof-read',
      source: 'installed-browser-opfs-reopen-package-consumer.html',
      importSpecifier: 'browserrt',
      prefixSuffix: ${JSON.stringify(prefixSuffix)},
      ref: ${JSON.stringify(ref)},
      expectedDigest: ${JSON.stringify(expectedDigest)},
      lockTimeoutMs: 2000,
      pageLoadId: window.__BROWSERRT_PAGE_LOAD_ID || null,
      cleanup: true
    });
  }`);
}

async function waitForReady(evalJson, timeoutMs = 10000) {
  const deadline = Date.now() + timeoutMs;
  let last = null;
  while (Date.now() < deadline) {
    last = await evalJson(pageLoadIdExpression(), Math.min(1000, timeoutMs));
    if (last.error) throw new Error(`page error after reload: ${JSON.stringify(last.error)}`);
    if (last.readyState && last.readyState !== 'loading') return last;
    await sleep(50);
  }
  throw new Error(`Timed out waiting for page ready after reload; last=${JSON.stringify(last)}`);
}

export async function runProbe() {
  const root = process.cwd();
  const workspace = await mkdtemp(join(tmpdir(), 'browserrt-package-browser-opfs-reopen-smoke-'));
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
      'examples/browser-opfs-reopen-product-wedge-consumer.mjs'
    ];
    const missingTarballFiles = requiredTarballFiles.filter((name) => !fileNames.includes(name));
    assert.deepEqual(missingTarballFiles, [], `npm package missing browser OPFS reopen dependency files: ${missingTarballFiles.join(', ')}`);
    const forbiddenPrefixes = ['artifacts/', 'tools/', 'test/', 'node_modules/'];
    const forbiddenFiles = fileNames.filter((name) => forbiddenPrefixes.some((prefix) => name.startsWith(prefix)));
    assert.deepEqual(forbiddenFiles, [], `npm package leaked development-only files: ${forbiddenFiles.slice(0, 12).join(', ')}`);

    runNpmForPackageFixture('npm', ['init', '-y'], { cwd: consumerDir });
    runNpmForPackageFixture('npm', ['install', '--ignore-scripts', '--no-audit', '--no-fund', tarball], { cwd: consumerDir });
    const installedExample = await readFile(join(consumerDir, 'node_modules', 'browserrt', 'examples', 'browser-opfs-reopen-product-wedge-consumer.mjs'), 'utf8');
    assert.match(installedExample, /readBrowserOpfsReopenBlockWithApi/, 'installed OPFS reopen wedge example must expose a reopen/read session');
    assert.match(installedExample, /pageReloadObserved/, 'installed OPFS reopen wedge receipt must include explicit reload proof');
    assert.match(installedExample, /rt\.storage\.opfsWebLockGuardedBlockStoreWithPosture/, 'installed OPFS reopen wedge must use the postured guarded storage namespace');
    assert.doesNotMatch(installedExample, /rt\.storage\.opfsWebLockGuardedBlockStore\(\{/, 'installed OPFS reopen wedge must not hand-wire raw guarded OPFS construction');
    assert.match(installedExample, /posturedGuardedFactoryUsedAcrossSessions/, 'installed OPFS reopen receipt must prove postured guarded factory use across reload');
    assert.match(installedExample, /budgetPolicySource/, 'installed OPFS reopen receipt must prove posture-derived write-budget provenance');
    const installedPackageJson = JSON.parse(await readFile(join(consumerDir, 'node_modules', 'browserrt', 'package.json'), 'utf8'));
    const prefixSuffix = `installed-reopen-${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 8)}`;

    const browser = await runManagedBrowserPage({
      root: consumerDir,
      pagePath: '/installed-browser-opfs-reopen-consumer.html',
      pageTitle: 'BrowserRT installed browser OPFS reopen consumer proof',
      body: PAGE,
      allowedPrefixes: ['node_modules/browserrt/src/', 'node_modules/browserrt/examples/'],
      timeoutMs: 35000,
      stderrTerms: ['import', 'module', 'browserrt', 'opfs', 'lock', 'reload']
    }, async ({ cdp, evalJson, pageState, pageUrl, browserVersion }) => {
      const beforePage = await evalJson(pageLoadIdExpression(), 5000);
      assert.equal(beforePage.error, null, `initial page error: ${JSON.stringify(beforePage.error)}`);
      const write = await evalJson(writeExpression(prefixSuffix), 25000);
      assert.equal(write.importSpecifier, 'browserrt');
      assert.equal(write.revision, REVISION);
      assert.equal(write.version, VERSION);
      assert.equal(write.environment.isSecureContext, true, 'managed server should provide secure localhost context');
      assert.equal(write.environment.hasOpfs, true, 'managed Chromium should expose OPFS');
      assert.equal(write.environment.hasWebLocks, true, 'managed Chromium should expose Web Locks');
      assert.equal(write.storage.readDigestMatches, true, 'write session self-read must match');
      assert.equal(write.storage.verifyDigestMatches, true, 'write session verify digest must match');
      assert.equal(write.storage.budgetChecked, true, 'write session must check storage budget estimate');
      assert.equal(write.storage.posturedGuardedFactoryUsed, true, 'write session must use the postured guarded OPFS factory');
      assert.equal(write.storage.writeBudgetGuardSource, 'browser-storage-posture-admission-policy', 'write session must expose posture-derived write-budget guard source');
      assert.equal(write.storage.budgetPolicySource, 'browser-storage-posture-admission-policy', 'write session put must preserve posture-derived budget policy provenance');
      assert.equal(write.storage.lockContentionPolicy?.source, 'postured-web-lock-guarded-opfs-factory', 'write session must expose postured Web Lock contention policy');
      assert.equal(write.trace.closed, true, 'write runtime must close before page reload');

      await cdp.send('Page.reload', { ignoreCache: true }, 5000);
      const afterPage = await waitForReady(evalJson, 10000);
      assert.notEqual(beforePage.pageLoadId, afterPage.pageLoadId, 'page reload must replace the JS realm before the reopen read');
      assert.equal(afterPage.href, pageUrl, 'page must reload at the same origin/path');

      const read = await evalJson(readExpression({ ref: write.storage.ref, expectedDigest: write.storage.expectedDigest, prefixSuffix }), 25000);
      assert.equal(read.importSpecifier, 'browserrt');
      assert.equal(read.revision, REVISION);
      assert.equal(read.version, VERSION);
      assert.equal(read.prefix, write.prefix, 'reopen read must use the same OPFS prefix');
      assert.equal(read.lockName, write.lockName, 'reopen read must use the same Web Lock name');
      assert.equal(read.storage.readDigestMatches, true, 'reopen read digest must match the write digest');
      assert.equal(read.storage.verifyDigestMatches, true, 'reopen verify digest must match the write digest');
      assert.equal(read.storage.readDigest, write.storage.expectedDigest, 'reopen read must recover the exact written bytes');
      assert.equal(read.storage.posturedGuardedFactoryUsed, true, 'reopen read must use the postured guarded OPFS factory');
      assert.equal(read.storage.writeBudgetGuardSource, 'browser-storage-posture-admission-policy', 'reopen read must expose posture-derived guard source');
      assert.equal(read.storage.lockContentionPolicy?.source, 'postured-web-lock-guarded-opfs-factory', 'reopen read must expose postured Web Lock contention policy');
      assert.equal(read.cleanup.accepted, true, 'cleanup must be scheduled after reopened read');
      assert.equal(read.cleanup.result, true, 'cleanup must remove the reopened OPFS prefix');
      assert.equal(read.trace.closed, true, 'read runtime must close after cleanup');

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
        reload: { beforePageLoadId: beforePage.pageLoadId, afterPageLoadId: afterPage.pageLoadId, href: afterPage.href, readyState: afterPage.readyState },
        write,
        read
      });
      const receipt = createBrowserOpfsReopenProductWedgeReceipt({ observed, generatedAt: 'deterministic-installed-browser-opfs-reopen-package-proof', source: 'installed-browser-opfs-reopen-package-consumer.html' });
      const validation = validateBrowserOpfsReopenProductWedgeReceipt(receipt);
      assert.equal(validation.ok, true, validation.errors.join('; '));
      return { pageUrl, pageState, browserVersion, beforePage, afterPage, write, read, observed, receipt, validation };
    });

    const receipt = browser.result.receipt;
    return Object.freeze({
      project: 'BrowserRT',
      revision: REVISION,
      version: VERSION,
      schema: 1,
      status: 'passed',
      probe_id: `${REVISION}-package-installed-browser-opfs-reopen-consumer`,
      purpose: 'Package-installed browser OPFS reopen proof: npm pack, local install, package-root public API import in managed Chromium, real OPFS write through the postured WebLockGuardedBlockStore/storage-lane, runtime close, full page reload, new runtime read/verify by ref from the same prefix, cleanup, and receipt validation.',
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
        validation: browser.result.validation,
        reload: receipt.observed.reload,
        storage: {
          write: { digest: receipt.observed.write.storage.digest, path: receipt.observed.write.storage.path, budgetChecked: receipt.observed.write.storage.budgetChecked, budgetPolicySource: receipt.observed.write.storage.budgetPolicySource, posturedGuardedFactoryUsed: receipt.observed.write.storage.posturedGuardedFactoryUsed },
          read: { readDigest: receipt.observed.read.storage.readDigest, verifyDigest: receipt.observed.read.storage.verifyDigest, cleanup: receipt.observed.read.cleanup, posturedGuardedFactoryUsed: receipt.observed.read.storage.posturedGuardedFactoryUsed }
        },
        locks: { write: receipt.observed.write.locks, read: receipt.observed.read.locks }
      },
      receipt,
      commands: {
        pack: 'npm pack --json --pack-destination <tmp>',
        install: `npm install --ignore-scripts --no-audit --no-fund ${packInfo.filename}`,
        serve: 'managed Chromium via tools/browser_cdp_fixture.mjs',
        run: 'package-root browserrt import writes OPFS by ref, closes runtime, reloads page, imports browserrt again, and reads/verifies the same ref before cleanup'
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
    const report = { project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1, status: 'failed', probe_id: `${REVISION}-package-installed-browser-opfs-reopen-consumer`, error: { name: error?.name || 'Error', message: error?.message || String(error), stack: error?.stack, command: error?.result || null } };
    await mkdir(dirname(out), { recursive: true });
    await writeFile(out, JSON.stringify(report, null, 2) + '\n');
    console.error(out);
    console.error(`[package_installed_browser_reopen_opfs_consumer_probe] FAIL: ${error?.stack || error}`);
    process.exitCode = 1;
  }
}
