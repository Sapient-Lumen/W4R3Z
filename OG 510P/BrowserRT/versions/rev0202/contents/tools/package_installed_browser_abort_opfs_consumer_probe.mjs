#!/usr/bin/env node
import assert from 'node:assert/strict';
import { mkdir, mkdtemp, readFile, rm, writeFile } from 'node:fs/promises';
import { dirname, join } from 'node:path';
import { tmpdir } from 'node:os';
import { REVISION, VERSION } from '../src/public-api.mjs';
import { runManagedBrowserPage } from './browser_cdp_fixture.mjs';
import { preparePackageTarballForProbe, runNpmForPackageFixture } from './lib/package_installed_fixture.mjs';

const DEFAULT_OUT = `artifacts/validation/REV${REVISION.slice(3)}-PACKAGE-INSTALLED-BROWSER-OPFS-ABORT-CONSUMER-PROBE.json`;
const argValue = (argv, flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };

const PAGE = `<!doctype html>
<meta charset="utf-8">
<title>BrowserRT installed browser OPFS abort consumer proof</title>
<script>
  window.__BROWSERRT_PACKAGE_BROWSER_OPFS_ABORT_ERROR = null;
  window.addEventListener('error', (event) => {
    window.__BROWSERRT_PACKAGE_BROWSER_OPFS_ABORT_ERROR = { type: 'error', message: event.message, filename: event.filename, lineno: event.lineno, colno: event.colno };
  });
  window.addEventListener('unhandledrejection', (event) => {
    const reason = event.reason || {};
    window.__BROWSERRT_PACKAGE_BROWSER_OPFS_ABORT_ERROR = { type: 'unhandledrejection', message: reason.message || String(reason), stack: reason.stack || null, code: reason.code || null };
  });
</script>
<script type="importmap">
{
  "imports": {
    "browserrt": "/node_modules/browserrt/src/public-api.mjs"
  }
}
</script>
<body>BrowserRT installed browser OPFS abort consumer proof</body>
<script type="module">
  import * as api from 'browserrt';
  import { runBrowserOpfsAbortProductWedgeWithApi } from '/node_modules/browserrt/examples/browser-opfs-abort-product-wedge-consumer.mjs';

  window.__BROWSERRT_PACKAGE_BROWSER_OPFS_ABORT_SMOKE = (async () => {
    const report = await runBrowserOpfsAbortProductWedgeWithApi(api, {
      generatedAt: 'deterministic-installed-browser-opfs-abort-package-proof',
      source: 'installed-browser-opfs-abort-package-consumer.html',
      importSpecifier: 'browserrt'
    });
    const payload = {
      project: 'BrowserRT',
      revision: api.REVISION,
      version: api.VERSION,
      schema: 1,
      status: report.status,
      environment: report.receipt.observed.environment,
      importSpecifier: 'browserrt',
      receipt: report.receipt,
      validation: report.validation
    };
    window.__BROWSERRT_PACKAGE_BROWSER_OPFS_ABORT_REPORT = payload;
    return payload;
  })();
</script>
`;

function browserAbortExpression(timeoutMs = 28000) {
  return `(async()=>{
    const start = performance.now();
    while (performance.now() - start < ${Number(timeoutMs)}) {
      if (window.__BROWSERRT_PACKAGE_BROWSER_OPFS_ABORT_ERROR) throw new Error(JSON.stringify(window.__BROWSERRT_PACKAGE_BROWSER_OPFS_ABORT_ERROR));
      if (window.__BROWSERRT_PACKAGE_BROWSER_OPFS_ABORT_SMOKE) {
        const result = await window.__BROWSERRT_PACKAGE_BROWSER_OPFS_ABORT_SMOKE;
        return JSON.stringify(result);
      }
      await new Promise((resolve)=>setTimeout(resolve, 50));
    }
    throw new Error('Timed out waiting for installed browser OPFS abort package smoke module');
  })()`;
}

export async function runProbe() {
  const root = process.cwd();
  const workspace = await mkdtemp(join(tmpdir(), 'browserrt-package-browser-opfs-abort-smoke-'));
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
      'src/browser-storage-posture.mjs',
      'src/browser-storage-recovery-guidance.mjs',
      'src/block-store-lane-adapter.mjs',
      'src/storage-lane-scheduler.mjs',
      'examples/browser-opfs-abort-product-wedge-consumer.mjs'
    ];
    const missingTarballFiles = requiredTarballFiles.filter((name) => !fileNames.includes(name));
    assert.deepEqual(missingTarballFiles, [], `npm package missing browser OPFS abort runtime dependency files: ${missingTarballFiles.join(', ')}`);
    const forbiddenPrefixes = ['artifacts/', 'tools/', 'test/', 'node_modules/'];
    const forbiddenFiles = fileNames.filter((name) => forbiddenPrefixes.some((prefix) => name.startsWith(prefix)));
    assert.deepEqual(forbiddenFiles, [], `npm package leaked development-only files: ${forbiddenFiles.slice(0, 12).join(', ')}`);

    runNpmForPackageFixture('npm', ['init', '-y'], { cwd: consumerDir });
    runNpmForPackageFixture('npm', ['install', '--ignore-scripts', '--no-audit', '--no-fund', tarball], { cwd: consumerDir });
    const installedExample = await readFile(join(consumerDir, 'node_modules', 'browserrt', 'examples', 'browser-opfs-abort-product-wedge-consumer.mjs'), 'utf8');
    assert.match(installedExample, /BRT_STORAGE_OPERATION_TIMEOUT/, 'installed OPFS abort product wedge example must assert storage-lane timeout');
    assert.match(installedExample, /BRT_OPFS_OPERATION_ABORTED/, 'installed OPFS abort product wedge example must assert provider abort settlement');
    assert.match(installedExample, /storage:opfs-block-put-rollback/, 'installed OPFS abort product wedge example must require rollback trace evidence');
    assert.match(installedExample, /storage:opfs-block-staged-cleanup/, 'installed OPFS abort product wedge example must accept staged rollback cleanup evidence');
    assert.match(installedExample, /rt\.storage\.opfsWebLockGuardedBlockStoreWithPosture/, 'installed OPFS abort product wedge example must use the postured guarded storage namespace');
    assert.doesNotMatch(installedExample, /rt\.storage\.opfsWebLockGuardedBlockStore\s*\(/, 'installed OPFS abort product wedge example must not hand-wire raw guarded OPFS construction');
    assert.match(installedExample, /writeBudgetGuardSource/, 'installed OPFS abort product wedge example must surface the posture-derived write budget guard');
    assert.match(installedExample, /rt\.coordination\.crossLaneScheduler/, 'installed OPFS abort product wedge example must use the coordination namespace');
    assert.match(installedExample, /recoveryBlockedBeforeOverride/, 'installed OPFS abort product wedge example must prove quarantine blocks recovery before override');
    const installedPackageJson = JSON.parse(await readFile(join(consumerDir, 'node_modules', 'browserrt', 'package.json'), 'utf8'));

    const browser = await runManagedBrowserPage({
      root: consumerDir,
      pagePath: '/installed-browser-opfs-abort-consumer.html',
      pageTitle: 'BrowserRT installed browser OPFS abort consumer proof',
      body: PAGE,
      allowedPrefixes: ['node_modules/browserrt/src/', 'node_modules/browserrt/examples/'],
      timeoutMs: 36000,
      stderrTerms: ['import', 'module', 'browserrt', 'opfs', 'abort', 'timeout', 'rollback', 'lock']
    }, async ({ evalJson, pageState, pageUrl, browserVersion }) => {
      const consumerReport = await evalJson(browserAbortExpression(28000), 32000);
      assert.equal(consumerReport.status, 'passed', consumerReport.validation?.errors?.join('; '));
      assert.equal(consumerReport.importSpecifier, 'browserrt');
      assert.equal(consumerReport.revision, REVISION);
      assert.equal(consumerReport.version, VERSION);
      assert.equal(consumerReport.environment.isSecureContext, true, 'managed server should provide secure localhost context');
      assert.equal(consumerReport.environment.hasOpfs, true, 'managed Chromium should expose OPFS');
      assert.equal(consumerReport.environment.hasWebLocks, true, 'managed Chromium should expose Web Locks');
      assert.equal(consumerReport.receipt?.proof?.timeoutAbortObserved, true, 'receipt must prove storage-lane timeout with provider abort');
      assert.equal(consumerReport.receipt?.proof?.providerAbortSettled, true, 'receipt must prove provider abort settled as a late failure');
      assert.equal(consumerReport.receipt?.proof?.abortedWriteDidNotCommit, true, 'receipt must prove aborted digest did not commit');
      assert.equal(consumerReport.receipt?.proof?.rollbackVisible, true, 'receipt must prove OPFS rollback/staged cleanup was visible');
      assert.equal(consumerReport.receipt?.proof?.namespacedFacadeUsed, true, 'receipt must prove the package example uses product namespaces');
      assert.equal(consumerReport.receipt?.proof?.posturedGuardedFactoryUsed, true, 'receipt must prove the abort wedge uses the postured guarded OPFS factory');
      assert.equal(consumerReport.receipt?.observed?.storage?.writeBudgetGuardSource, 'browser-storage-posture-admission-policy', 'abort wedge must use the posture-derived write budget guard');
      assert.equal(consumerReport.receipt?.proof?.recoveryBlockedBeforeOverride, true, 'receipt must prove quarantine blocks recovery before override');
      assert.equal(consumerReport.receipt?.observed?.recovery?.preOverrideRecoveryRejected, true, 'pre-override recovery attempt must be rejected');
      assert.equal(consumerReport.receipt?.observed?.recovery?.preOverrideNoMutation, true, 'pre-override rejection must be a no-mutation scheduler rejection');
      assert.equal(consumerReport.receipt?.observed?.recovery?.preOverrideHasAfterReject, false, 'pre-override rejected digest must not be present');
      assert.equal(consumerReport.receipt?.observed?.recovery?.preOverrideVerifyPresentAfterReject, false, 'pre-override rejected digest must not verify as present');
      assert.equal(consumerReport.receipt?.proof?.storageLaneRecoveredAfterAbort, true, 'receipt must prove storage lane recovered after explicit override');
      return { pageUrl, pageState, browserVersion, consumerReport };
    });

    const consumerReport = browser.result.consumerReport;
    return Object.freeze({
      project: 'BrowserRT',
      revision: REVISION,
      version: VERSION,
      schema: 1,
      status: 'passed',
      probe_id: `${REVISION}-package-installed-browser-opfs-abort-consumer`,
      purpose: 'Package-installed browser OPFS abort proof: npm pack, local install, package-root public API import in managed Chromium, deterministic storage-lane operation timeout with provider abort of an in-progress guarded OPFS put, staged rollback cleanup or final-block rollback/no-commit evidence, explicit health override, recovery write/read, lock settlement, cleanup, and receipt validation.',
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
        process: browser.harness.process || null,
        profileReap: browser.harness.profileReap || null,
        teardownMode: browser.harness.teardownMode || null,
        chromeStderrSummary: browser.harness.chromeStderrSummary
      },
      consumer: {
        importSpecifier: consumerReport.importSpecifier,
        status: consumerReport.status,
        environment: consumerReport.environment,
        proof: consumerReport.receipt?.proof || null,
        validation: consumerReport.validation || null,
        abort: consumerReport.receipt?.observed?.abort || null,
        recovery: consumerReport.receipt?.observed?.recovery || null,
        locks: consumerReport.receipt?.observed?.locks || null
      },
      receipt: consumerReport.receipt,
      commands: {
        pack: 'npm pack --json --pack-destination <tmp>',
        install: `npm install --ignore-scripts --no-audit --no-fund ${packInfo.filename}`,
        serve: 'managed Chromium via tools/browser_cdp_fixture.mjs',
        proof: 'import browserrt from package root via product namespaces, create OPFS through the postured Web-Lock-guarded factory, force a storage-lane timeout/provider abort during OPFS put, prove quarantine blocks pre-override recovery with no mutation, then explicitly recover and read a valid block'
      },
      nonClaims: consumerReport.receipt?.nonClaims || []
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
    const report = { project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1, status: 'failed', probe_id: `${REVISION}-package-installed-browser-opfs-abort-consumer`, error: { name: error?.name || 'Error', message: error?.message || String(error), stack: error?.stack, command: error?.result || null } };
    await mkdir(dirname(out), { recursive: true });
    await writeFile(out, JSON.stringify(report, null, 2) + '\n');
    console.error(out);
    console.error(`[package_installed_browser_abort_opfs_consumer_probe] FAIL: ${error?.stack || error}`);
    process.exitCode = 1;
  }
}
