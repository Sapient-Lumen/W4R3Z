#!/usr/bin/env node
import { readFile, writeFile, mkdir } from 'node:fs/promises';
import { dirname } from 'node:path';
import { REVISION, VERSION } from '../src/browserrt.mjs';

const PREFIX = `REV${REVISION.slice(3)}`;
const DEFAULT_OUT = `artifacts/audit/${PREFIX}-WEB-LOCK-LIFECYCLE-CONTRACT-AUDIT.json`;
const argValue = (argv, flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };
async function text(path) { return await readFile(path, 'utf8'); }
function missing(body, needles) { return needles.filter((needle) => !body.includes(needle)); }
function check(name, passed, detail = {}) { return { name, status: passed ? 'passed' : 'failed', ...detail }; }

const files = {
  coordinator: await text('src/web-lock-coordinator.mjs'),
  guarded: await text('src/opfs-web-lock-guarded-block-store.mjs'),
  fixture: await text('tools/browser_cdp_fixture.mjs'),
  tabProbe: await text('tools/browser_opfs_web_lock_tab_termination_probe.mjs'),
  tabTimeoutProbe: await text('tools/browser_opfs_web_lock_tab_timeout_probe.mjs'),
  timeoutProbe: await text('tools/browser_opfs_web_lock_timeout_probe.mjs'),
  releaseProbe: await text('tools/web_lock_guarded_block_store_probe.mjs'),
  tabDoc: await text('docs/40-validation/browser-opfs-web-lock-tab-termination-slice.md'),
  tabTimeoutDoc: await text('docs/40-validation/browser-opfs-web-lock-tab-timeout-slice.md'),
  timeoutDoc: await text('docs/40-validation/browser-opfs-web-lock-timeout-slice.md'),
  manifest: await text('test/manifest.json'),
  impact: await text('test/impact-map.json'),
  inventory: await text('test/surface-inventory.json'),
  packageJson: await text('package.json'),
  makefile: await text('Makefile')
};

const checks = [
  check('coordinator-query-and-timeout-surfaces', missing(files.coordinator, ['queryLocks', 'waitForSettled', 'coord:web-lock-query-normalized', 'coord:web-lock-wait-settled-complete', 'BRT_WEB_LOCK_TIMEOUT', 'BRT_WEB_LOCK_ABORTED']).length === 0, { missing: missing(files.coordinator, ['queryLocks', 'waitForSettled', 'coord:web-lock-query-normalized', 'coord:web-lock-wait-settled-complete', 'BRT_WEB_LOCK_TIMEOUT', 'BRT_WEB_LOCK_ABORTED']) }),
  check('guarded-store-timeout-plumbing-preserved', missing(files.guarded, ['lockTimeoutMs', 'timeoutMs', 'storage:opfs-web-lock-guard-op-error']).length === 0, { missing: missing(files.guarded, ['lockTimeoutMs', 'timeoutMs', 'storage:opfs-web-lock-guard-op-error']) }),
  check('browser-fixture-target-helpers', missing(files.fixture, ['connectBrowserCdp', 'openPageTarget', 'closePageTarget', 'Target.createTarget', 'Target.closeTarget', 'browserVersion']).length === 0, { missing: missing(files.fixture, ['connectBrowserCdp', 'openPageTarget', 'closePageTarget', 'Target.createTarget', 'Target.closeTarget', 'browserVersion']) }),
  check('tab-termination-proof-present', missing(files.tabProbe, ['browser:opfs-web-lock-tab-termination-proof', 'closePageTarget', 'holder-acquired', 'waiter-acquired', 'lockQueryBeforeClose', 'heldCount', 'pendingCount', 'waiter should acquire after holder tab close']).length === 0, { missing: missing(files.tabProbe, ['browser:opfs-web-lock-tab-termination-proof', 'closePageTarget', 'holder-acquired', 'waiter-acquired', 'lockQueryBeforeClose', 'heldCount', 'pendingCount', 'waiter should acquire after holder tab close']) }),
  check('tab-timeout-proof-present', missing(files.tabTimeoutProbe, ['browser:opfs-web-lock-tab-timeout-proof', 'BRT_WEB_LOCK_TIMEOUT', 'holderStillHeldAfterTimeout', 'timeoutPresent', 'lockQueryWhilePending', 'closePageTarget', 'recovery write']).length === 0, { missing: missing(files.tabTimeoutProbe, ['browser:opfs-web-lock-tab-timeout-proof', 'BRT_WEB_LOCK_TIMEOUT', 'holderStillHeldAfterTimeout', 'timeoutPresent', 'lockQueryWhilePending', 'closePageTarget', 'recovery write']) }),
  check('timeout-proof-still-present', missing(files.timeoutProbe, ['browser:opfs-web-lock-timeout-proof', 'BRT_WEB_LOCK_TIMEOUT', 'timeoutPresentAfterRelease', 'recoveryVerify']).length === 0, { missing: missing(files.timeoutProbe, ['browser:opfs-web-lock-timeout-proof', 'BRT_WEB_LOCK_TIMEOUT', 'timeoutPresentAfterRelease', 'recoveryVerify']) }),
  check('release-guard-covers-query-settled', missing(files.releaseProbe, ['queryLocks', 'waitForSettled', 'coord:web-lock-query-normalized', 'coord:web-lock-wait-settled-complete']).length === 0, { missing: missing(files.releaseProbe, ['queryLocks', 'waitForSettled', 'coord:web-lock-query-normalized', 'coord:web-lock-wait-settled-complete']) }),
  check('docs-carry-lifecycle-boundary', missing(files.tabDoc, ['holder tab', 'pending', 'closed', 'zero held', 'zero pending', 'cross-browser', 'OPFS fsync']).length === 0, { missing: missing(files.tabDoc, ['holder tab', 'pending', 'closed', 'zero held', 'zero pending', 'cross-browser', 'OPFS fsync']) }),
  check('docs-carry-tab-timeout-boundary', missing(files.tabTimeoutDoc, ['BRT_WEB_LOCK_TIMEOUT', 'holder tab', 'zero held', 'zero pending', 'cross-browser', 'OPFS durability']).length === 0, { missing: missing(files.tabTimeoutDoc, ['BRT_WEB_LOCK_TIMEOUT', 'holder tab', 'zero held', 'zero pending', 'cross-browser', 'OPFS durability']) }),
  check('docs-carry-timeout-boundary', missing(files.timeoutDoc, ['BRT_WEB_LOCK_TIMEOUT', 'does not cancel work after a lock has already been granted', 'cross-browser', 'OPFS durability']).length === 0, { missing: missing(files.timeoutDoc, ['BRT_WEB_LOCK_TIMEOUT', 'does not cancel work after a lock has already been granted', 'cross-browser', 'OPFS durability']) }),
  check('manifest-impact-inventory-wired', missing(files.manifest + files.impact + files.inventory, ['browser:opfs-web-lock-tab-timeout-proof', 'browser:opfs-web-lock-tab-termination-proof', 'browser:opfs-web-lock-timeout-proof', 'coord:web-lock-guarded-block-store-proof', 'facility:web-lock-lifecycle-contract-audit', 'surface:browser-opfs-web-lock-tab-termination', 'impact:opfs-web-lock-tab-termination']).length === 0, { missing: missing(files.manifest + files.impact + files.inventory, ['browser:opfs-web-lock-tab-timeout-proof', 'browser:opfs-web-lock-tab-termination-proof', 'browser:opfs-web-lock-timeout-proof', 'coord:web-lock-guarded-block-store-proof', 'facility:web-lock-lifecycle-contract-audit', 'surface:browser-opfs-web-lock-tab-termination', 'impact:opfs-web-lock-tab-termination']) }),
  check('operator-shortcuts-wired', missing(files.packageJson + files.makefile, ['test:browser:opfs-web-lock-tab-timeout', 'test:browser:opfs-web-lock-tab-termination', 'audit:web-lock-lifecycle', 'test-browser-opfs-web-lock-tab-timeout', 'test-browser-opfs-web-lock-tab-termination', 'audit-web-lock-lifecycle']).length === 0, { missing: missing(files.packageJson + files.makefile, ['test:browser:opfs-web-lock-tab-timeout', 'test:browser:opfs-web-lock-tab-termination', 'audit:web-lock-lifecycle', 'test-browser-opfs-web-lock-tab-timeout', 'test-browser-opfs-web-lock-tab-termination', 'audit-web-lock-lifecycle']) })
];

const status = checks.every((row) => row.status === 'passed') ? 'passed' : 'failed';
const report = {
  project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1,
  probe_id: `${REVISION}-web-lock-lifecycle-contract-audit`, status, generatedAt: new Date().toISOString(),
  purpose: 'Static contract audit for the Web Lock lifecycle slice: keep timeout behavior, normalized query/wait helpers, browser multi-target fixture helpers, tab-termination/tab-timeout proof wiring, docs, manifest, impact map, surface inventory, and operator shortcuts aligned.',
  checks,
  nonClaims: [
    'Static/source audit only; it does not replace managed Chromium lifecycle proof or browser-light release guard execution.',
    'No cross-browser lifecycle, mobile/background suspension, fairness, starvation-freedom, service-worker, or OPFS durability claim.'
  ]
};

const out = argValue(process.argv.slice(2), '--json', DEFAULT_OUT);
if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); console.log(out); }
else console.log(JSON.stringify(report, null, 2));
if (status !== 'passed') process.exitCode = 1;
