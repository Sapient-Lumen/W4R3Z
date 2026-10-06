#!/usr/bin/env node
import assert from 'node:assert/strict';
import { mkdir, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import { REVISION, VERSION } from '../src/browserrt.mjs';
import { createWebLockGuardedBlockStore } from '../src/opfs-web-lock-guarded-block-store.mjs';
import { runAudit as runCloseAbortContractAudit } from './web_lock_guarded_close_abort_contract_audit.mjs';

const PFX = `REV${REVISION.slice(3)}`;
const DEFAULT_OUT = `artifacts/validation/${PFX}-WEB-LOCK-GUARDED-CLOSE-ABORT-PROBE.json`;
const argValue = (argv, flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };
const delay = (ms) => new Promise((resolve) => setTimeout(resolve, ms));
async function waitUntil(fn, { timeoutMs = 250, intervalMs = 5 } = {}) {
  const start = Date.now();
  while (Date.now() - start < timeoutMs) {
    if (fn()) return true;
    await delay(intervalMs);
  }
  return false;
}
function abortDomError() {
  if (typeof DOMException === 'function') return new DOMException('The operation was aborted.', 'AbortError');
  const err = new Error('The operation was aborted.'); err.name = 'AbortError'; return err;
}
function describeError(error) { return { name: error?.name || 'Error', message: error?.message || String(error), code: error?.code ?? null, detail: error?.detail ?? null }; }
function quietStore(label) {
  return { name: `${label}:store`, provider: 'fake-opfs', prefix: `${label}/prefix`, puts: 0, put() { this.puts += 1; throw new Error('quietStore.put should not be reached'); }, snapshot() { return { name: this.name, provider: this.provider, prefix: this.prefix, puts: this.puts }; } };
}
async function pendingLockCloseAbortScenario() {
  const requests = [];
  const locks = { async request(name, options) {
    requests.push({ name, options, abortedAtRequest: options.signal?.aborted === true });
    return await new Promise((_resolve, reject) => {
      const onAbort = () => reject(abortDomError());
      if (options.signal?.aborted) onAbort();
      else options.signal?.addEventListener?.('abort', onAbort, { once: true });
    });
  } };
  const store = quietStore('pending-close-abort');
  const guard = createWebLockGuardedBlockStore({ store, locks, requireWebLocks: true, lockPrefix: 'browserrt:probe:close-abort', lockName: 'pending', lockTimeoutMs: 5000, ownStore: false, label: 'pending-close-abort-guard' });
  const started = Date.now();
  const op = guard.put(new Uint8Array([1, 2, 3]), { label: 'must-not-mutate' }).then((value) => ({ ok: true, value }), (error) => ({ ok: false, error }));
  assert.equal(await waitUntil(() => requests.length === 1), true, 'lock request should be pending before close');
  assert.equal(requests[0].options.signal?.aborted, false, 'close-owned lock signal must start live');
  const close = await guard.closeAsync({ reason: 'probe-close-while-pending-lock' });
  const result = await Promise.race([op, delay(200).then(() => ({ timeout: true }))]);
  assert.equal(result.timeout, undefined, 'close must abort queued lock request before the long timeout wins');
  assert.equal(result.ok, false, 'queued operation must reject when the guard closes');
  assert.equal(result.error?.code, 'BRT_WEB_LOCK_ABORTED', 'pending lock request should be classified as aborted before acquisition');
  assert.equal(result.error?.detail?.abortReasonCode, 'BRT_OPFS_WEB_LOCK_GUARD_CLOSED', 'pending lock abort should retain close-owned abort provenance');
  assert.equal(store.puts, 0, 'close-aborted queued operation must not call the provider');
  assert.equal(close.closeSignalAborted, true, 'close report must expose close-owned abort signal state');
  assert.equal(guard.snapshot().stats.closeAbortSignals, 1, 'guard close should publish exactly one close abort signal');
  assert.ok(Date.now() - started < 1000, 'close abort should beat the configured 5s lock timeout');
  return Object.freeze({ status: 'passed', lockRequestCount: requests.length, resultError: describeError(result.error), providerPuts: store.puts, close, snapshot: guard.snapshot() });
}
async function acquiredProviderCloseAbortScenario() {
  let capturedOptions = null;
  const locks = { async request(name, options, callback) { return await callback({ name, mode: options.mode || 'exclusive' }); } };
  const store = { name: 'acquired-provider-close-abort:store', provider: 'fake-opfs', prefix: 'acquired-provider-close-abort/prefix', puts: 0,
    async put(_value, _fields, options = {}) {
      this.puts += 1; capturedOptions = options;
      assert.equal(typeof options.signal?.addEventListener, 'function', 'provider should receive a close-composed AbortSignal');
      return await new Promise((_resolve, reject) => {
        const onAbort = () => reject(options.signal.reason || abortDomError());
        if (options.signal.aborted) onAbort();
        else options.signal.addEventListener('abort', onAbort, { once: true });
      });
    }, snapshot() { return { name: this.name, provider: this.provider, prefix: this.prefix, puts: this.puts, providerSignalAborted: capturedOptions?.signal?.aborted === true }; } };
  const guard = createWebLockGuardedBlockStore({ store, locks, requireWebLocks: true, lockPrefix: 'browserrt:probe:close-abort', lockName: 'acquired', lockTimeoutMs: 5000, ownStore: false, label: 'acquired-provider-close-abort-guard' });
  const op = guard.put(new Uint8Array([4, 5, 6]), { label: 'close-aborts-provider' }).then((value) => ({ ok: true, value }), (error) => ({ ok: false, error }));
  assert.equal(await waitUntil(() => capturedOptions !== null), true, 'provider put should be in flight before close');
  assert.equal(capturedOptions.signal.aborted, false, 'provider signal must start live');
  const close = await guard.closeAsync({ reason: 'probe-close-while-provider-in-flight' });
  const result = await Promise.race([op, delay(200).then(() => ({ timeout: true }))]);
  assert.equal(result.timeout, undefined, 'close must abort the provider signal before the long timeout wins');
  assert.equal(result.ok, false, 'in-flight provider operation should reject from close signal');
  assert.equal(result.error?.code, 'BRT_OPFS_WEB_LOCK_GUARD_CLOSED', 'provider should observe the close-owned guarded error');
  assert.equal(store.puts, 1, 'provider should have started exactly once before close abort');
  assert.equal(capturedOptions.signal.aborted, true, 'provider AbortSignal must be aborted by guard close');
  return Object.freeze({ status: 'passed', resultError: describeError(result.error), close, snapshot: guard.snapshot(), providerSignalAborted: capturedOptions.signal.aborted === true });
}

async function acquiredOpenCloseAbortScenario() {
  let capturedOptions = null;
  const locks = { async request(name, options, callback) { return await callback({ name, mode: options.mode || 'exclusive' }); } };
  const store = { name: 'acquired-open-provider-close-abort:store', provider: 'fake-opfs', prefix: 'acquired-open-provider-close-abort/prefix', opens: 0,
    async open(options = {}) {
      this.opens += 1; capturedOptions = options;
      assert.equal(typeof options.signal?.addEventListener, 'function', 'open provider should receive a close-composed AbortSignal');
      return await new Promise((_resolve, reject) => {
        const onAbort = () => reject(options.signal.reason || abortDomError());
        if (options.signal.aborted) onAbort();
        else options.signal.addEventListener('abort', onAbort, { once: true });
      });
    }, snapshot() { return { name: this.name, provider: this.provider, prefix: this.prefix, opens: this.opens, providerSignalAborted: capturedOptions?.signal?.aborted === true }; } };
  const guard = createWebLockGuardedBlockStore({ store, locks, requireWebLocks: true, lockPrefix: 'browserrt:probe:close-abort', lockName: 'acquired-open', lockTimeoutMs: 5000, ownStore: false, label: 'acquired-open-provider-close-abort-guard' });
  const op = guard.open({ label: 'close-aborts-open-provider' }).then((value) => ({ ok: true, value }), (error) => ({ ok: false, error }));
  assert.equal(await waitUntil(() => capturedOptions !== null), true, 'provider open should be in flight before close');
  const close = await guard.closeAsync({ reason: 'probe-close-while-open-provider-in-flight' });
  const result = await Promise.race([op, delay(200).then(() => ({ timeout: true }))]);
  assert.equal(result.timeout, undefined, 'close must abort the provider open signal before the long timeout wins');
  assert.equal(result.ok, false, 'in-flight provider open should reject from close signal');
  assert.equal(result.error?.code, 'BRT_OPFS_WEB_LOCK_GUARD_CLOSED', 'provider open should observe the close-owned guarded error');
  assert.equal(store.opens, 1, 'provider open should have started exactly once before close abort');
  assert.equal(capturedOptions.signal.aborted, true, 'provider open AbortSignal must be aborted by guard close');
  return Object.freeze({ status: 'passed', resultError: describeError(result.error), close, snapshot: guard.snapshot(), providerSignalAborted: capturedOptions.signal.aborted === true });
}

export async function runProbe() {
  const contract = await runCloseAbortContractAudit();
  const pending = await pendingLockCloseAbortScenario();
  const acquired = await acquiredProviderCloseAbortScenario();
  const acquiredOpen = await acquiredOpenCloseAbortScenario();
  return Object.freeze({ project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1, probe_id: `${REVISION}-web-lock-guarded-close-abort-proof`, status: 'passed', contract: { status: contract.status, audit_id: contract.audit_id, checks: contract.checks }, pending, acquired, acquiredOpen, proof: { staticContractAudited: contract.status === 'passed', pendingLockCloseRejectedBeforeAcquisition: pending.resultError.code === 'BRT_WEB_LOCK_ABORTED' && pending.resultError.detail?.abortReasonCode === 'BRT_OPFS_WEB_LOCK_GUARD_CLOSED' && pending.providerPuts === 0, acquiredProviderCloseSignalPropagated: acquired.providerSignalAborted === true && acquired.resultError.code === 'BRT_OPFS_WEB_LOCK_GUARD_CLOSED', acquiredOpenCloseSignalPropagated: acquiredOpen.providerSignalAborted === true && acquiredOpen.resultError.code === 'BRT_OPFS_WEB_LOCK_GUARD_CLOSED', closeAbortSignalVisibleInSnapshot: pending.snapshot.closeSignalAborted === true && acquired.snapshot.closeSignalAborted === true && acquiredOpen.snapshot.closeSignalAborted === true, longTimeoutDidNotGateClose: true }, nonClaims: ['Close abort is same-object lifecycle cancellation; it does not make Web Locks fair, durable, cross-tab quota-reserving, or crash-proof.'] });
}
if (import.meta.url === `file://${process.argv[1]}`) {
  const out = argValue(process.argv.slice(2), '--json', DEFAULT_OUT);
  const report = await runProbe();
  await mkdir(dirname(out), { recursive: true });
  await writeFile(out, JSON.stringify(report, null, 2) + '\n');
  console.log(out);
}
