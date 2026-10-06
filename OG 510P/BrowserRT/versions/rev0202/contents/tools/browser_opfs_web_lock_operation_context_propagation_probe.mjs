#!/usr/bin/env node
import assert from 'node:assert/strict';
import { mkdir, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import { performance } from 'node:perf_hooks';
import { REVISION, VERSION } from '../src/browserrt.mjs';
import { runManagedBrowserPage } from './browser_cdp_fixture.mjs';

const TASK_ID = 'browser:opfs-web-lock-operation-context-propagation-proof';
const DEFAULT_OUT = `artifacts/validation/REV${REVISION.slice(3)}-BROWSER-OPFS-WEB-LOCK-OPERATION-CONTEXT-PROPAGATION-PROBE.json`;
const argValue = (argv, flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };

function pageExpression({ prefix, lockPrefix, lockName }) {
  return `(async () => {
    const moduleUrl = new URL('/src/browserrt.mjs', location.href).href;
    const m = await import(moduleUrl);
    const rt = await m.boot({ telemetry: 'browser-cdp', proof: '${REVISION}', operationContextPropagationProof: true });
    const raw = rt.opfsAsyncBlockStore({ name: '${REVISION}-operation-context-raw-store', prefix: ${JSON.stringify(prefix)} });
    await raw.open();
    await raw.cleanupForTest();
    await raw.open();
    const calls = [];
    const record = (method, options) => calls.push({ method, operationTimeoutMs: options?.operationTimeoutMs ?? null, hasSignal: Boolean(options?.signal || options?.abortSignal), optionKeys: Object.keys(options || {}).sort() });
    const recordingStore = {
      name: '${REVISION}-operation-context-recording-opfs-store',
      provider: 'recording:' + raw.provider,
      get prefix() { return raw.prefix; },
      get available() { return raw.available; },
      async put(payload, fields = {}, options = {}) { record('put', options); return await raw.put(payload, fields); },
      async get(ref, options = {}) { record('get', options); return await raw.get(ref); },
      async has(ref, options = {}) { record('has', options); return await raw.has(ref); },
      async verify(ref, options = {}) { record('verify', options); return await raw.verify(ref); },
      async delete(ref, options = {}) { record('delete', options); return await raw.delete(ref); },
      async estimate(options = {}) { record('estimate', options); return await raw.estimate(); },
      async cleanupForTest(options = {}) { record('cleanupForTest', options); return await raw.cleanupForTest(); },
      snapshot() { return { name: this.name, provider: this.provider, prefix: raw.prefix, available: raw.available, callCount: calls.length, calls: calls.slice(), raw: raw.snapshot() }; }
    };
    const guard = rt.opfsWebLockGuardedBlockStore({ store: recordingStore, lockPrefix: ${JSON.stringify(lockPrefix)}, lockName: ${JSON.stringify(lockName)}, label: '${REVISION}-operation-context-guard', lockTimeoutMs: 1200 });
    const scheduler = m.createCrossLaneScheduler({ label: '${REVISION}-operation-context-browser-scheduler', lanes: [ { id: 'storage', rank: 70, capacity: 1, quantum: 4096, maxQueuedCost: 8192 }, { id: 'maintenance', rank: 10, capacity: 1, quantum: 64, maxQueuedCost: 128 } ] });
    const adapter = rt.blockStoreLaneAdapter({ label: '${REVISION}-operation-context-browser-adapter', store: guard, scheduler, lane: 'storage', defaultOperationTimeoutMs: 101 });
    const bytesFromSeed = (seed, count) => { const out = new Uint8Array(count); const enc = new TextEncoder().encode(seed); out.set(enc.slice(0, Math.min(out.length, enc.length))); for (let i = enc.length; i < out.length; i += 1) out[i] = (i * 37 + 11) & 255; return out; };
    const payload = bytesFromSeed('${REVISION}:operation-context-payload', 4096);
    const scheduledPut = adapter.schedulePut(payload, { id: '${REVISION}-ctx-put', label: 'browser-context-put', priority: 'user-visible', operationTimeoutMs: 211 });
    const putDrain = await adapter.drain({ maxSteps: 2 });
    const putResult = putDrain.results.find((row) => row.opId === '${REVISION}-ctx-put') || null;
    const ref = putResult?.result?.ref;
    const scheduled = [
      scheduledPut,
      adapter.scheduleGet(ref, { id: '${REVISION}-ctx-get', priority: 'user-visible', operationTimeoutMs: 322 }),
      adapter.scheduleHas(ref, { id: '${REVISION}-ctx-has', priority: 'user-visible', operationTimeoutMs: 433 }),
      adapter.scheduleVerify(ref, { id: '${REVISION}-ctx-verify', priority: 'user-visible', operationTimeoutMs: 544 }),
      adapter.scheduleEstimate({ id: '${REVISION}-ctx-estimate', priority: 'background', operationTimeoutMs: 655 }),
      adapter.scheduleDelete(ref, { id: '${REVISION}-ctx-delete', priority: 'user-visible', operationTimeoutMs: 766 }),
      adapter.scheduleCleanupForTest({ id: '${REVISION}-ctx-cleanup', operationTimeoutMs: 877 })
    ];
    const remainingDrain = await adapter.drain({ maxSteps: 10 });
    const locksAfter = await guard.queryLocks();
    const finalSnapshot = adapter.snapshot();
    const trace = rt.close();
    return JSON.stringify({
      project: 'BrowserRT', revision: m.REVISION, version: m.VERSION, taskId: '${TASK_ID}',
      page: { location: location.href, readyState: document.readyState, crossOriginIsolated, isSecureContext, origin: location.origin },
      capabilities: { ...m.detectCapabilities(globalThis), webLocksQuery: typeof navigator.locks?.query === 'function' },
      scheduled, putDrain, putResult, remainingDrain, recordingCalls: calls, locksAfter, finalSnapshot,
      traceKinds: (Array.isArray(trace) ? trace : trace.events || []).map((event) => event.kind), traceEventCount: (Array.isArray(trace) ? trace : trace.events || []).length
    });
  })()`;
}

export async function runProbe({ jsonOut = DEFAULT_OUT } = {}) {
  const started = performance.now();
  const prefix = `browserrt/${REVISION}/operation-context-propagation/${Date.now().toString(36)}`;
  const lockPrefix = `${REVISION}:operation-context`;
  const lockName = `context-${Date.now().toString(36)}`;
  const browser = await runManagedBrowserPage({
    pagePath: '/operation-context-propagation.html',
    pageTitle: `${REVISION} operation context propagation proof`,
    allowedPrefixes: ['src/'],
    timeoutMs: 22000,
    profilePrefix: `browserrt-${REVISION}-operation-context-`,
    stderrTerms: ['opfs', 'locks', 'storage']
  }, async ({ evalJson }) => await evalJson(pageExpression({ prefix, lockPrefix, lockName }), 18000));
  const result = browser.result;
  const expectedTimeouts = { put: 211, get: 322, has: 433, verify: 544, estimate: 655, delete: 766, cleanupForTest: 877 };
  const observedTimeouts = Object.fromEntries((result.recordingCalls || []).map((call) => [call.method, call.operationTimeoutMs]));
  assert.equal(result.revision, REVISION);
  assert.equal(result.putResult?.ok, true);
  for (const scheduled of result.scheduled || []) assert.equal(scheduled.accepted, true, `${scheduled.opId || scheduled.adapterOp} should be accepted`);
  for (const [method, expected] of Object.entries(expectedTimeouts)) assert.equal(observedTimeouts[method], expected, `${method} operationTimeoutMs should propagate in browser`);
  assert.equal(result.locksAfter?.heldCount, 0);
  assert.equal(result.locksAfter?.pendingCount, 0);
  assert.equal(result.finalSnapshot?.executorValidation?.ok, true);
  for (const kind of ['storage:opfs-web-lock-guard-op-start', 'storage:opfs-web-lock-guard-op-complete', 'block-store-lane:op-start', 'block-store-lane:op-complete']) assert.ok((result.traceKinds || []).includes(kind), `missing trace kind ${kind}`);
  const report = {
    project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1, probe_id: `${REVISION}-browser-opfs-web-lock-operation-context-propagation-proof`, task_id: TASK_ID, status: 'passed', generatedAt: new Date().toISOString(), durationMs: Math.round(performance.now() - started),
    purpose: 'Managed Chromium proof that storage-lane operationTimeoutMs propagates through BrowserRT WebLockGuardedBlockStore into real OPFS provider calls.',
    browserHarness: browser.harness,
    observations: { expectedTimeouts, observedTimeouts, recordingCalls: result.recordingCalls, putResult: result.putResult, remainingDrain: result.remainingDrain, locksAfter: result.locksAfter, finalSnapshot: result.finalSnapshot, traceKinds: result.traceKinds, page: result.page, capabilities: result.capabilities },
    claimsChecked: ['BlockStoreLaneAdapter passes operation context to the scheduled block-store callback.', 'WebLockGuardedBlockStore passes provider options through to the underlying OPFS block-store wrapper.', 'Real managed Chromium OPFS/Web Locks path observes the expected operationTimeoutMs values for put/get/has/verify/estimate/delete/cleanup.'],
    nonClaims: ['This is not provider cancellation, rollback, no-mutation-on-timeout, durability, quota, eviction, persistent-retention, latency, throughput, SLO, or production-readiness evidence.', 'This is a managed Chromium proof only; no cross-browser OPFS/Web Locks claim.']
  };
  if (jsonOut) { await mkdir(dirname(jsonOut), { recursive: true }); await writeFile(jsonOut, JSON.stringify(report, null, 2) + '\n'); }
  return report;
}

const argv = process.argv.slice(2); const out = argValue(argv, '--json', DEFAULT_OUT);
try { const report = await runProbe({ jsonOut: out }); if (out) console.log(out); else console.log(JSON.stringify(report, null, 2)); }
catch (error) { const report = { project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1, probe_id: `${REVISION}-browser-opfs-web-lock-operation-context-propagation-proof`, task_id: TASK_ID, status: 'failed', generatedAt: new Date().toISOString(), error: { name: error?.name || 'Error', message: error?.message || String(error), code: error?.code || null, stack: error?.stack }, nonClaims: ['Failed browser context-propagation proof is not silently skipped.'] }; if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); console.error(out); } console.error(`[browser_opfs_web_lock_operation_context_propagation_probe] FAIL: ${error?.stack || error}`); process.exitCode = 1; }
