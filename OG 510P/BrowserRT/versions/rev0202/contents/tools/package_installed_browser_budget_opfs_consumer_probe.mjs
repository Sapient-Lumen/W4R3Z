#!/usr/bin/env node
import assert from 'node:assert/strict';
import { mkdir, mkdtemp, readFile, rm, writeFile } from 'node:fs/promises';
import { dirname, join } from 'node:path';
import { tmpdir } from 'node:os';
import { REVISION, VERSION } from '../src/public-api.mjs';
import { runManagedBrowserPage } from './browser_cdp_fixture.mjs';
import { preparePackageTarballForProbe, runNpmForPackageFixture } from './lib/package_installed_fixture.mjs';

const DEFAULT_OUT = `artifacts/validation/REV${REVISION.slice(3)}-PACKAGE-INSTALLED-BROWSER-OPFS-BUDGET-CONSUMER-PROBE.json`;
const argValue = (argv, flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };

const PAGE = `<!doctype html>
<meta charset="utf-8">
<title>BrowserRT installed browser OPFS budget consumer proof</title>
<script>
  window.__BROWSERRT_PACKAGE_BROWSER_OPFS_BUDGET_ERROR = null;
  window.addEventListener('error', (event) => {
    window.__BROWSERRT_PACKAGE_BROWSER_OPFS_BUDGET_ERROR = { type: 'error', message: event.message, filename: event.filename, lineno: event.lineno, colno: event.colno };
  });
  window.addEventListener('unhandledrejection', (event) => {
    const reason = event.reason || {};
    window.__BROWSERRT_PACKAGE_BROWSER_OPFS_BUDGET_ERROR = { type: 'unhandledrejection', message: reason.message || String(reason), stack: reason.stack || null, code: reason.code || null };
  });
</script>
<script type="importmap">
{
  "imports": {
    "browserrt": "/node_modules/browserrt/src/public-api.mjs"
  }
}
</script>
<body>BrowserRT installed browser OPFS budget consumer proof</body>
<script type="module">
  import * as api from 'browserrt';
  import { runBrowserOpfsBudgetProductWedgeWithApi } from '/node_modules/browserrt/examples/browser-opfs-budget-product-wedge-consumer.mjs';

  window.__BROWSERRT_PACKAGE_BROWSER_OPFS_BUDGET_SMOKE = (async () => {
    const report = await runBrowserOpfsBudgetProductWedgeWithApi(api, {
      generatedAt: 'deterministic-installed-browser-opfs-budget-package-proof',
      source: 'installed-browser-opfs-budget-package-consumer.html',
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
    window.__BROWSERRT_PACKAGE_BROWSER_OPFS_BUDGET_REPORT = payload;
    return payload;
  })();
</script>
`;

function browserBudgetExpression(timeoutMs = 22000) {
  return `(async()=>{
    const start = performance.now();
    while (performance.now() - start < ${Number(timeoutMs)}) {
      if (window.__BROWSERRT_PACKAGE_BROWSER_OPFS_BUDGET_ERROR) throw new Error(JSON.stringify(window.__BROWSERRT_PACKAGE_BROWSER_OPFS_BUDGET_ERROR));
      if (window.__BROWSERRT_PACKAGE_BROWSER_OPFS_BUDGET_SMOKE) {
        const result = await window.__BROWSERRT_PACKAGE_BROWSER_OPFS_BUDGET_SMOKE;
        return JSON.stringify(result);
      }
      await new Promise((resolve)=>setTimeout(resolve, 50));
    }
    throw new Error('Timed out waiting for installed browser OPFS budget package smoke module');
  })()`;
}

export async function runProbe() {
  const root = process.cwd();
  const workspace = await mkdtemp(join(tmpdir(), 'browserrt-package-browser-opfs-budget-smoke-'));
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
      'src/browser-storage-posture.mjs',
      'src/browser-storage-recovery-guidance.mjs',
      'src/web-lock-coordinator.mjs',
      'src/block-store-lane-adapter.mjs',
      'src/storage-lane-scheduler.mjs',
      'examples/browser-opfs-budget-product-wedge-consumer.mjs'
    ];
    const missingTarballFiles = requiredTarballFiles.filter((name) => !fileNames.includes(name));
    assert.deepEqual(missingTarballFiles, [], `npm package missing browser OPFS budget runtime dependency files: ${missingTarballFiles.join(', ')}`);
    const forbiddenPrefixes = ['artifacts/', 'tools/', 'test/', 'node_modules/'];
    const forbiddenFiles = fileNames.filter((name) => forbiddenPrefixes.some((prefix) => name.startsWith(prefix)));
    assert.deepEqual(forbiddenFiles, [], `npm package leaked development-only files: ${forbiddenFiles.slice(0, 12).join(', ')}`);

    runNpmForPackageFixture('npm', ['init', '-y'], { cwd: consumerDir });
    runNpmForPackageFixture('npm', ['install', '--ignore-scripts', '--no-audit', '--no-fund', tarball], { cwd: consumerDir });
    const installedExample = await readFile(join(consumerDir, 'node_modules', 'browserrt', 'examples', 'browser-opfs-budget-product-wedge-consumer.mjs'), 'utf8');
    assert.match(installedExample, /BRT_OPFS_WRITE_BUDGET_EXCEEDED/, 'installed OPFS budget product wedge example must assert explicit write-budget rejection code');
    assert.match(installedExample, /1e20/, 'installed OPFS budget product wedge example must force a deterministic budget rejection');
    assert.match(installedExample, /rt\.storage\.opfsWebLockGuardedBlockStoreWithPosture/, 'installed OPFS budget product wedge example must use the postured guarded storage namespace');
    assert.doesNotMatch(installedExample, /rt\.storage\.opfsWebLockGuardedBlockStore\(/, 'installed OPFS budget product wedge example must not hand-wire raw guarded OPFS construction');
    const installedPackageJson = JSON.parse(await readFile(join(consumerDir, 'node_modules', 'browserrt', 'package.json'), 'utf8'));

    const browser = await runManagedBrowserPage({
      root: consumerDir,
      pagePath: '/installed-browser-opfs-budget-consumer.html',
      pageTitle: 'BrowserRT installed browser OPFS budget consumer proof',
      body: PAGE,
      allowedPrefixes: ['node_modules/browserrt/src/', 'node_modules/browserrt/examples/'],
      timeoutMs: 32000,
      stderrTerms: ['import', 'module', 'browserrt', 'opfs', 'budget', 'quota', 'lock']
    }, async ({ evalJson, pageState, pageUrl, browserVersion }) => {
      const consumerReport = await evalJson(browserBudgetExpression(24000), 28000);
      assert.equal(consumerReport.status, 'passed', consumerReport.validation?.errors?.join('; '));
      assert.equal(consumerReport.importSpecifier, 'browserrt');
      assert.equal(consumerReport.revision, REVISION);
      assert.equal(consumerReport.version, VERSION);
      assert.equal(consumerReport.environment.isSecureContext, true, 'managed server should provide secure localhost context');
      assert.equal(consumerReport.environment.hasOpfs, true, 'managed Chromium should expose OPFS');
      assert.equal(consumerReport.environment.hasWebLocks, true, 'managed Chromium should expose Web Locks');
      assert.equal(consumerReport.receipt?.proof?.posturedGuardedFactoryUsed, true, 'receipt must prove the postured guarded OPFS factory was used');
      assert.equal(consumerReport.receipt?.proof?.postureGuardPropagated, true, 'receipt must prove posture-derived guard and bounded lock policy propagated');
      assert.equal(consumerReport.receipt?.observed?.storage?.writeBudgetGuardSource, 'browser-storage-posture-admission-policy', 'receipt must expose posture-derived write-budget source');
      assert.equal(consumerReport.receipt?.observed?.storage?.lockContentionPolicySource, 'postured-web-lock-guarded-opfs-factory', 'receipt must expose bounded lock-contention policy source');
      assert.equal(consumerReport.receipt?.proof?.writeBudgetRejectObserved, true, 'receipt must prove explicit budget rejection');
      assert.equal(consumerReport.receipt?.proof?.rejectedWriteDidNotCommit, true, 'receipt must prove rejected write did not commit a content block');
      assert.equal(consumerReport.receipt?.proof?.storageLaneRecoveredAfterRejection, true, 'receipt must prove storage lane recovers after budget rejection');
      assert.equal(consumerReport.receipt?.proof?.writeBudgetPassObserved, true, 'receipt must prove a subsequent accepted write still observes budget estimate');
      assert.equal(consumerReport.receipt?.proof?.cleanupAttempted, true, 'receipt must prove cleanup');
      return { pageUrl, pageState, browserVersion, consumerReport };
    });

    const consumerReport = browser.result.consumerReport;
    return Object.freeze({
      project: 'BrowserRT',
      revision: REVISION,
      version: VERSION,
      schema: 1,
      status: 'passed',
      probe_id: `${REVISION}-package-installed-browser-opfs-budget-consumer`,
      purpose: 'Package-installed browser OPFS budget proof: npm pack, local install, package-root public API import in managed Chromium, deterministic OPFS write-budget rejection before mutation, no committed rejected block, post-rejection storage-lane recovery write/verify/read/estimate, lock settlement, cleanup, and receipt validation.',
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
        importSpecifier: consumerReport.importSpecifier,
        status: consumerReport.status,
        environment: consumerReport.environment,
        proof: consumerReport.receipt?.proof || null,
        validation: consumerReport.validation || null,
        rejection: consumerReport.receipt?.observed?.rejection || null,
        recovery: consumerReport.receipt?.observed?.recovery || null,
        storage: consumerReport.receipt?.observed?.storage || null,
        locks: consumerReport.receipt?.observed?.locks || null
      },
      receipt: consumerReport.receipt,
      commands: {
        pack: 'npm pack --json --pack-destination <tmp>',
        install: `npm install --ignore-scripts --no-audit --no-fund ${packInfo.filename}`,
        serve: 'managed Chromium via tools/browser_cdp_fixture.mjs',
        proof: 'import browserrt from package root, force write-budget rejection, prove no commit, then recover with a successful OPFS storage-lane write/read'
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
    const report = { project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1, status: 'failed', probe_id: `${REVISION}-package-installed-browser-opfs-budget-consumer`, error: { name: error?.name || 'Error', message: error?.message || String(error), stack: error?.stack, command: error?.result || null } };
    await mkdir(dirname(out), { recursive: true });
    await writeFile(out, JSON.stringify(report, null, 2) + '\n');
    console.error(out);
    console.error(`[package_installed_browser_budget_opfs_consumer_probe] FAIL: ${error?.stack || error}`);
    process.exitCode = 1;
  }
}
