#!/usr/bin/env node
import assert from 'node:assert/strict';
import { mkdir, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import { REVISION, VERSION } from '../src/browserrt.mjs';
import { runManagedBrowserPage } from './browser_cdp_fixture.mjs';

const PREFIX = `REV${REVISION.slice(3)}`;
const DEFAULT_OUT = `artifacts/validation/${PREFIX}-BROWSER-OPFS-WEB-LOCK-STRICT-OPTION-GUARD-PROBE.json`;
const argValue = (argv, flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };
const hasFlag = (argv, flag) => argv.includes(flag);

function exprForPage(prefix, lockPrefix, lockName, payload) {
  return `(async () => {
    const browserRtUrl = new URL('/src/browserrt.mjs', location.href).href;
    const page = { location: location.href, readyState: document.readyState, crossOriginIsolated, isSecureContext };
    const capabilities = {
      opfs: typeof navigator.storage?.getDirectory === 'function',
      webLocks: typeof navigator.locks?.request === 'function',
      webLocksQuery: typeof navigator.locks?.query === 'function',
      abortController: typeof AbortController === 'function',
      textEncoder: typeof TextEncoder === 'function'
    };
    const mod = await import(browserRtUrl);
    const rt = await mod.boot({ opfsAsyncBlockStoreProof: true, webLockStrictOptionGuardProof: true });
    const coordinator = rt.webLockCoordinator({ prefix: ${JSON.stringify(lockPrefix)}, label: 'browser-strict-option-coordinator', requireAvailable: true });
    const capture = async (label, fn) => {
      try { return { label, ok: true, value: await fn() }; }
      catch (error) { return { label, ok: false, error: { name: error?.name || 'Error', message: error?.message || String(error), code: error?.code || null, detail: error?.detail || null } }; }
    };
    const invalid = [];
    invalid.push(await capture('non-string-name', () => coordinator.request({ bad: 'name' }, async () => 'bad')));
    invalid.push(await capture('empty-mode-does-not-default', () => coordinator.request('browser-empty-mode', async () => 'bad', { mode: '' })));
    invalid.push(await capture('ifAvailable-string-false', () => coordinator.request('browser-string-ifavailable', async () => 'bad', { ifAvailable: 'false' })));
    invalid.push(await capture('steal-string-false', () => coordinator.request('browser-string-steal', async () => 'bad', { steal: 'false' })));
    invalid.push(await capture('ifAvailable-plus-steal', () => coordinator.request('browser-ifavailable-plus-steal', async () => 'bad', { ifAvailable: true, steal: true })));
    invalid.push(await capture('shared-plus-steal', () => coordinator.request('browser-shared-plus-steal', async () => 'bad', { mode: 'shared', steal: true })));
    invalid.push(await capture('signal-plus-ifAvailable', () => coordinator.request('browser-signal-plus-ifavailable', async () => 'bad', { signal: new AbortController().signal, ifAvailable: true })));
    invalid.push(await capture('plain-object-signal', () => coordinator.request('browser-plain-object-signal', async () => 'bad', { signal: { aborted: false, addEventListener() {}, removeEventListener() {} } })));

    const valid = [];
    valid.push(await capture('default-exclusive', () => coordinator.request('browser-default-exclusive', async (lock) => ({ name: lock.name, mode: lock.mode }))));
    valid.push(await capture('shared-mode', () => coordinator.request('browser-shared-mode', async (lock) => ({ name: lock.name, mode: lock.mode }), { mode: 'shared' })));
    valid.push(await capture('ifAvailable-false-preserved', () => coordinator.request('browser-ifavailable-false', async (lock) => ({ name: lock.name, mode: lock.mode }), { ifAvailable: false })));
    valid.push(await capture('steal-false-preserved', () => coordinator.request('browser-steal-false', async (lock) => ({ name: lock.name, mode: lock.mode }), { steal: false })));
    valid.push(await capture('ifAvailable-true', () => coordinator.request('browser-ifavailable-true', async (lock) => lock ? { name: lock.name, mode: lock.mode } : null, { ifAvailable: true })));
    valid.push(await capture('steal-true-exclusive', () => coordinator.request('browser-steal-true', async (lock) => ({ name: lock.name, mode: lock.mode }), { steal: true })));
    valid.push(await capture('real-abort-signal', () => coordinator.request('browser-real-signal', async (lock) => ({ name: lock.name, mode: lock.mode }), { signal: new AbortController().signal })));
    valid.push(await capture('null-signal-treated-as-absent', () => coordinator.request('browser-null-signal', async (lock) => ({ name: lock.name, mode: lock.mode }), { signal: null })));

    const store = rt.opfsAsyncBlockStore({ name: 'browser-strict-option-opfs-store', prefix: ${JSON.stringify(prefix)} });
    const guard = rt.opfsWebLockGuardedBlockStore({ store, lockPrefix: ${JSON.stringify(lockPrefix)}, lockName: ${JSON.stringify(lockName)}, label: 'browser-strict-option-opfs-guard', lockTimeoutMs: 100 });
    const cleanupBefore = await guard.cleanupForTest({ timeoutMs: 200 });
    const put = await guard.put(new TextEncoder().encode(${JSON.stringify(payload)}), { label: 'browser-strict-option-opfs-put' }, { signal: null, timeoutMs: 200 });
    const verify = await guard.verify(put.ref, { signal: null, timeoutMs: 200 });
    const cleanupAfter = await guard.cleanupForTest({ timeoutMs: 200 });
    const query = typeof navigator.locks?.query === 'function' ? await navigator.locks.query() : null;
    const snapshot = coordinator.snapshot();
    const guardSnapshot = guard.snapshot();
    const traceKinds = rt.trace.snapshot().map((row) => row.kind);
    rt.close();
    return JSON.stringify({ project: 'BrowserRT', revision: '${REVISION}', version: '${VERSION}', page, capabilities, invalid, valid, cleanupBefore, put: { digest: put.digest, bytes: put.bytes, ref: put.ref, path: put.path }, verify, cleanupAfter, query: query ? { heldCount: query.held?.length ?? null, pendingCount: query.pending?.length ?? null, held: query.held, pending: query.pending } : null, snapshot, guardSnapshot, traceKinds });
  })()`;
}

export async function runProbe(options = {}) {
  const prefix = options.prefix || `browserrt/${REVISION}/opfs-web-lock-strict-option-guard-proof`;
  const lockPrefix = options.lockPrefix || `browserrt:${REVISION}:strict-option-browser`;
  const lockName = options.lockName || `${REVISION}-strict-option-opfs-lock`;
  const payload = options.payload || `browser-strict-option-payload-${REVISION}-${Date.now()}`;
  const { result: observed, harness } = await runManagedBrowserPage({
    timeoutMs: options.timeoutMs ?? 16000,
    chromium: options.chromium,
    relaxPolicy: options.relaxPolicy,
    pagePath: '/opfs-web-lock-strict-option-guard-probe.html',
    pageTitle: 'BrowserRT OPFS Web Lock strict option guard probe',
    profilePrefix: 'browserrt-opfs-web-lock-strict-option-',
    stderrTerms: ['opfs', 'lock', 'signal', 'option', 'storage']
  }, async ({ evalJson, pageUrl, mark, timeoutMs }) => {
    const started = performance.now();
    const out = await evalJson(exprForPage(prefix, lockPrefix, lockName, payload), timeoutMs);
    mark('browser-opfs-web-lock-strict-option-eval', started);
    out._pageUrl = pageUrl;
    return out;
  });

  assert.equal(observed.project, 'BrowserRT');
  assert.equal(observed.revision, REVISION);
  assert.equal(observed.version, VERSION);
  assert.equal(observed.page.location, observed._pageUrl);
  assert.equal(observed.page.crossOriginIsolated, true);
  assert.equal(observed.page.isSecureContext, true);
  assert.equal(observed.capabilities.opfs, true, 'OPFS must be available for strict option guard browser proof');
  assert.equal(observed.capabilities.webLocks, true, 'Web Locks must be available for strict option guard browser proof');
  assert.equal(observed.capabilities.abortController, true, 'AbortController must be available for strict option guard browser proof');
  const expected = new Map([
    ['non-string-name', 'BRT_WEB_LOCK_NAME_INVALID'],
    ['empty-mode-does-not-default', 'BRT_WEB_LOCK_MODE_INVALID'],
    ['ifAvailable-string-false', 'BRT_WEB_LOCK_OPTION_TYPE'],
    ['steal-string-false', 'BRT_WEB_LOCK_OPTION_TYPE'],
    ['ifAvailable-plus-steal', 'BRT_WEB_LOCK_OPTION_CONFLICT'],
    ['shared-plus-steal', 'BRT_WEB_LOCK_OPTION_CONFLICT'],
    ['signal-plus-ifAvailable', 'BRT_WEB_LOCK_SIGNAL_OPTION_CONFLICT'],
    ['plain-object-signal', 'BRT_WEB_LOCK_SIGNAL_INVALID']
  ]);
  for (const row of observed.invalid) {
    assert.equal(row.ok, false, `${row.label} should reject in browser`);
    assert.equal(row.error?.code, expected.get(row.label), `${row.label} code mismatch`);
  }
  for (const row of observed.valid) assert.equal(row.ok, true, `${row.label} should pass in browser`);
  assert.equal(typeof observed.cleanupBefore, 'boolean');
  assert.equal(observed.verify.ok, true, 'guarded OPFS write with null signal compatibility should verify');
  assert.equal(observed.cleanupAfter, true);
  assert.equal(observed.query?.heldCount ?? 0, 0, 'browser Web Locks query should end with zero held locks');
  assert.equal(observed.query?.pendingCount ?? 0, 0, 'browser Web Locks query should end with zero pending locks');
  assert.equal(observed.snapshot.stats.optionRejected, observed.invalid.length, 'browser coordinator should count local option rejections');
  assert.ok(observed.traceKinds.includes('coord:web-lock-option-rejected'), 'browser trace should record strict option rejections');
  assert.ok(observed.traceKinds.includes('storage:opfs-block-put'), 'browser proof should write through OPFS after strict option rejection cases');
  assert.ok(observed.traceKinds.includes('storage:opfs-web-lock-guard-op-complete'), 'browser proof should complete a guarded OPFS Web Lock operation');

  return {
    project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1,
    probe_id: `${REVISION}-browser-opfs-web-lock-strict-option-guard-proof`, task_id: 'browser:opfs-web-lock-strict-option-guard-proof', status: 'passed', generatedAt: new Date().toISOString(),
    purpose: 'Managed Chromium proof that WebLockCoordinator strict option/name/signal validation runs in the real browser realm, rejects unsupported Web Locks option combinations before use, and still permits a guarded OPFS write with adapter-compatible null signal handling.',
    observed, harness,
    claimsChecked: [
      'Browser realm rejects invalid Web Lock names, modes, boolean controls, signal objects, and option combinations with BrowserRT error codes',
      'Browser realm accepts valid exclusive/shared/ifAvailable/steal/AbortSignal/null-signal requests',
      'A guarded OPFS write and verify still succeed after strict option rejection paths',
      'navigator.locks.query reports no held/pending lock leaks after the proof'
    ],
    nonClaims: [
      'Managed Chromium proof only; no cross-browser claim.',
      'No OPFS durability, quota, eviction, crash recovery, fairness, starvation-freedom, cryptographic attestation, or production readiness claim.'
    ]
  };
}

const argv = process.argv.slice(2);
const out = argValue(argv, '--json', DEFAULT_OUT);
try {
  const report = await runProbe({ timeoutMs: Number(argValue(argv, '--timeout-ms', 16000)), chromium: argValue(argv, '--chromium', null), relaxPolicy: !hasFlag(argv, '--no-relax-policy') });
  if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); console.log(out); }
  else console.log(JSON.stringify(report, null, 2));
} catch (error) {
  const report = { project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1, probe_id: `${REVISION}-browser-opfs-web-lock-strict-option-guard-proof`, task_id: 'browser:opfs-web-lock-strict-option-guard-proof', status: 'failed', generatedAt: new Date().toISOString(), error: { name: error?.name || 'Error', message: error?.message || String(error), stack: error?.stack, code: error?.code ?? null, detail: error?.detail ?? null }, nonClaims: ['Failed managed Chromium strict-option guard proof is not silently skipped.'] };
  if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); console.error(out); }
  console.error(`[browser_opfs_web_lock_strict_option_guard_probe] FAIL: ${error?.stack || error}`);
  process.exitCode = 1;
}
