#!/usr/bin/env node
import assert from 'node:assert/strict';
import { mkdir, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import { REVISION, VERSION } from '../src/browserrt.mjs';
import { createWebLockCoordinator } from '../src/web-lock-coordinator.mjs';

const PREFIX = `REV${REVISION.slice(3)}`;
const DEFAULT_OUT = `artifacts/validation/${PREFIX}-WEB-LOCK-STRICT-OPTION-GUARD-PROBE.json`;
const argValue = (argv, flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };

class RecordingLocks {
  constructor() { this.calls = []; }
  async request(name, options, callback) {
    if (typeof options === 'function') { callback = options; options = {}; }
    const row = {
      name,
      options: {
        mode: options?.mode ?? null,
        ifAvailable: Object.prototype.hasOwnProperty.call(options || {}, 'ifAvailable') ? options.ifAvailable : undefined,
        steal: Object.prototype.hasOwnProperty.call(options || {}, 'steal') ? options.steal : undefined,
        hasSignal: Boolean(options?.signal),
        signalIsAbortSignal: typeof AbortSignal === 'function' ? options?.signal instanceof AbortSignal : Boolean(options?.signal)
      }
    };
    this.calls.push(row);
    if (options?.ifAvailable === true && name.includes('not-available')) return await callback(null);
    return await callback(Object.freeze({ name, mode: options?.mode || 'exclusive' }));
  }
  async query() { return { held: [], pending: [] }; }
}

function traceCollector() {
  const events = [];
  return { events, emit(kind, fields = {}) { events.push({ kind, ...fields }); }, snapshot() { return events.slice(); } };
}

async function capture(label, fn) {
  try {
    const value = await fn();
    return { label, ok: true, value };
  } catch (error) {
    return { label, ok: false, error: { name: error?.name || 'Error', message: error?.message || String(error), code: error?.code ?? null, detail: error?.detail ?? null } };
  }
}

function assertRejected(row, code) {
  assert.equal(row.ok, false, `${row.label} should reject`);
  assert.equal(row.error.code, code, `${row.label} should reject with ${code}`);
}

function assertPassed(row, expected) {
  assert.equal(row.ok, true, `${row.label} should pass`);
  if (expected !== undefined) assert.deepEqual(row.value, expected, `${row.label} result mismatch`);
}

export async function runProbe() {
  const locks = new RecordingLocks();
  const trace = traceCollector();
  const coordinator = createWebLockCoordinator({ locks, prefix: `browserrt:${REVISION}:strict-options`, label: `${REVISION}-strict-option-guard`, trace, requireAvailable: true });

  const invalidCases = [
    ['non-string-name', () => coordinator.request({ bad: 'name' }, async () => 'bad')],
    ['blank-name', () => coordinator.request('  ', async () => 'bad')],
    ['nul-name', () => coordinator.request('bad\0name', async () => 'bad')],
    ['empty-mode-does-not-default', () => coordinator.request('empty-mode', async () => 'bad', { mode: '' })],
    ['ifAvailable-string-false', () => coordinator.request('string-ifavailable', async () => 'bad', { ifAvailable: 'false' })],
    ['steal-string-false', () => coordinator.request('string-steal', async () => 'bad', { steal: 'false' })],
    ['ifAvailable-plus-steal', () => coordinator.request('ifavailable-plus-steal', async () => 'bad', { ifAvailable: true, steal: true })],
    ['shared-plus-steal', () => coordinator.request('shared-plus-steal', async () => 'bad', { mode: 'shared', steal: true })],
    ['timeout-plus-ifAvailable', () => coordinator.request('timeout-plus-ifavailable', async () => 'bad', { timeoutMs: 10, ifAvailable: true })],
    ['timeout-plus-steal', () => coordinator.request('timeout-plus-steal', async () => 'bad', { timeoutMs: 10, steal: true })],
    ['plain-object-signal', () => coordinator.request('plain-object-signal', async () => 'bad', { signal: { aborted: false, addEventListener() {}, removeEventListener() {} } })]
  ];
  const invalid = [];
  for (const [label, fn] of invalidCases) invalid.push(await capture(label, fn));
  const expectedCodes = new Map([
    ['non-string-name', 'BRT_WEB_LOCK_NAME_INVALID'],
    ['blank-name', 'BRT_WEB_LOCK_NAME_INVALID'],
    ['nul-name', 'BRT_WEB_LOCK_NAME_INVALID'],
    ['empty-mode-does-not-default', 'BRT_WEB_LOCK_MODE_INVALID'],
    ['ifAvailable-string-false', 'BRT_WEB_LOCK_OPTION_TYPE'],
    ['steal-string-false', 'BRT_WEB_LOCK_OPTION_TYPE'],
    ['ifAvailable-plus-steal', 'BRT_WEB_LOCK_OPTION_CONFLICT'],
    ['shared-plus-steal', 'BRT_WEB_LOCK_OPTION_CONFLICT'],
    ['timeout-plus-ifAvailable', 'BRT_WEB_LOCK_SIGNAL_OPTION_CONFLICT'],
    ['timeout-plus-steal', 'BRT_WEB_LOCK_SIGNAL_OPTION_CONFLICT'],
    ['plain-object-signal', 'BRT_WEB_LOCK_SIGNAL_INVALID']
  ]);
  for (const row of invalid) assertRejected(row, expectedCodes.get(row.label));
  assert.equal(locks.calls.length, 0, 'invalid option/name cases must fail before native locks.request is called');

  const controller = new AbortController();
  const valid = [];
  valid.push(await capture('default-exclusive', () => coordinator.request('default-exclusive', async (lock) => ({ name: lock.name, mode: lock.mode }))));
  valid.push(await capture('trimmed-name', () => coordinator.request('  trimmed-name  ', async (lock) => ({ name: lock.name, mode: lock.mode }))));
  valid.push(await capture('shared-mode', () => coordinator.request('shared-mode', async (lock) => ({ name: lock.name, mode: lock.mode }), { mode: 'shared' })));
  valid.push(await capture('ifAvailable-false-preserved', () => coordinator.request('ifavailable-false', async (lock) => ({ name: lock.name, mode: lock.mode }), { ifAvailable: false })));
  valid.push(await capture('steal-false-preserved', () => coordinator.request('steal-false', async (lock) => ({ name: lock.name, mode: lock.mode }), { steal: false })));
  valid.push(await capture('ifAvailable-true-grants-null-without-reject', () => coordinator.request('not-available-case', async (lock) => lock === null ? 'not-acquired' : 'acquired', { ifAvailable: true })));
  valid.push(await capture('steal-true-exclusive', () => coordinator.request('steal-true', async (lock) => ({ name: lock.name, mode: lock.mode }), { steal: true })));
  valid.push(await capture('real-abort-signal-no-timeout', () => coordinator.request('real-signal', async (lock) => ({ name: lock.name, mode: lock.mode }), { signal: controller.signal })));
  valid.push(await capture('null-signal-treated-as-absent-for-adapter-compat', () => coordinator.request('null-signal', async (lock) => ({ name: lock.name, mode: lock.mode }), { signal: null })));
  for (const row of valid) assertPassed(row);

  const calls = locks.calls.slice();
  const byLabel = Object.fromEntries(calls.map((call) => [call.name.split(':').at(-1), call]));
  assert.equal(byLabel['ifavailable-false'].options.ifAvailable, false, 'ifAvailable:false must remain false, not be dropped/coerced true');
  assert.equal(byLabel['steal-false'].options.steal, false, 'steal:false must remain false, not be dropped/coerced true');
  assert.equal(byLabel['not-available-case'].options.ifAvailable, true, 'ifAvailable:true must remain true');
  assert.equal(byLabel['steal-true'].options.steal, true, 'steal:true must remain true for exclusive mode');
  assert.equal(byLabel['real-signal'].options.hasSignal, true, 'real AbortSignal should be proxied to native request');
  assert.equal(byLabel['real-signal'].options.signalIsAbortSignal, true, 'proxied signal should be an AbortSignal');
  assert.equal(byLabel['null-signal'].options.hasSignal, false, 'null signal should not be forwarded to native request');

  const snapshot = coordinator.snapshot();
  const traceKinds = trace.snapshot().map((row) => row.kind);
  assert.equal(snapshot.stats.optionRejected, invalid.length, 'all invalid control cases should be counted as optionRejected');
  assert.equal(snapshot.stats.requests, valid.length, 'only valid cases should reach request accounting');
  assert.equal(snapshot.stats.notAcquired, 1, 'ifAvailable true unavailable case should report notAcquired');
  assert.equal(traceKinds.filter((kind) => kind === 'coord:web-lock-option-rejected').length, invalid.length, 'invalid cases should emit option rejection traces');

  return {
    project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1,
    probe_id: `${REVISION}-web-lock-strict-option-guard-proof`, task_id: 'coord:web-lock-strict-option-guard-proof', status: 'passed', generatedAt: new Date().toISOString(),
    purpose: 'Release-tier proof that WebLockCoordinator validates lock names, modes, boolean control options, AbortSignal shape, and unsupported Web Locks option combinations before calling locks.request, while preserving explicit false values for valid calls.',
    observations: { invalid, valid, calls, snapshot, traceKinds },
    claimsChecked: [
      'non-string, blank, and NUL lock names fail with BRT_WEB_LOCK_NAME_INVALID before native request',
      'empty mode does not silently become exclusive',
      'ifAvailable/steal must be booleans; string "false" is rejected instead of coerced true',
      'ifAvailable+steal, shared+steal, timeout/signal+ifAvailable, and timeout/signal+steal fail closed locally',
      'plain object signal is rejected, real AbortSignal is accepted, and null signal remains adapter-compatible absent signal',
      'explicit false values for ifAvailable and steal are preserved in the native request options'
    ],
    nonClaims: [
      'Release-tier fake-lock proof only; browser Web Locks behavior is covered by the explicit managed Chromium strict-option proof.',
      'No fairness, starvation-freedom, cross-browser, OPFS durability, quota, eviction, crash recovery, cryptographic attestation, or production readiness claim.'
    ]
  };
}

const out = argValue(process.argv.slice(2), '--json', DEFAULT_OUT);
try {
  const report = await runProbe();
  if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); console.log(out); }
  else console.log(JSON.stringify(report, null, 2));
} catch (error) {
  const report = { project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1, probe_id: `${REVISION}-web-lock-strict-option-guard-proof`, task_id: 'coord:web-lock-strict-option-guard-proof', status: 'failed', generatedAt: new Date().toISOString(), error: { name: error?.name || 'Error', message: error?.message || String(error), stack: error?.stack, code: error?.code ?? null, detail: error?.detail ?? null }, nonClaims: ['Failed strict-option guard proof is not silently skipped.'] };
  if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); console.error(out); }
  console.error(`[web_lock_strict_option_guard_probe] FAIL: ${error?.stack || error}`);
  process.exitCode = 1;
}
