#!/usr/bin/env node
// BrowserRT rev0031 circuit-breaker/bulkhead proof.
// Fake-provider/virtual-tick proof only; no OPFS/browser, real-time, SLO, or production resilience claim.

import assert from 'node:assert/strict';
import { mkdir, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import {
  REVISION,
  VERSION,
  boot,
  createCircuitBreakerBulkheadController,
  validateCircuitBreakerBulkheadSnapshot
} from '../src/browserrt.mjs';

const argv = process.argv.slice(2);
const argValue = (flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };
const PREFIX = `REV${REVISION.slice(3)}`;
const outPath = argValue('--json', `artifacts/validation/${PREFIX}-CIRCUIT-BREAKER-BULKHEAD-PROBE.json`);
function kinds(trace) { return [...new Set(trace.map((event) => event.kind))].sort(); }
function hasKind(trace, kind) { return trace.some((event) => event.kind === kind); }
function acquire(controller, id, options = {}) {
  const row = controller.tryAcquire({ opId: id, kind: options.kind || 'storage-op', priority: options.priority || 'user-visible' });
  assert.equal(row.accepted, true, `${id} should acquire`);
  return row;
}
function release(controller, lease, result) {
  const row = controller.release(lease, result);
  assert.equal(row.released, true, `${lease.leaseId} should release`);
  return row;
}

const rt = await boot({ circuitBreakerBulkheadProof: true });

// Scenario 1: bulkhead capacity rejects without mutating active lease accounting.
const bulkhead = createCircuitBreakerBulkheadController({ label: 'rev0031-bulkhead', maxConcurrent: 2, slidingWindowSize: 4, minimumCalls: 4, trace: rt.trace });
const b1 = acquire(bulkhead, 'bulkhead-one');
const b2 = acquire(bulkhead, 'bulkhead-two');
const beforeBulkheadReject = bulkhead.snapshot();
const bReject = bulkhead.tryAcquire({ opId: 'bulkhead-three', priority: 'background' });
assert.equal(bReject.accepted, false);
assert.equal(bReject.reason, 'bulkhead-full');
assert.equal(bulkhead.snapshot().active, beforeBulkheadReject.active);
release(bulkhead, b1, { ok: true, durationTicks: 1 });
release(bulkhead, b2, { ok: true, durationTicks: 1 });
assert.equal(bulkhead.snapshot().active, 0);
assert.equal(validateCircuitBreakerBulkheadSnapshot(bulkhead.snapshot()).ok, true);

// Scenario 2: closed -> open on failure threshold, open rejects without lease growth, virtual tick moves to half-open, probes close it.
const breaker = createCircuitBreakerBulkheadController({
  label: 'rev0031-failure-threshold', maxConcurrent: 3, slidingWindowSize: 4, minimumCalls: 4,
  failureRateThreshold: 50, slowCallRateThreshold: 100, openDurationTicks: 3, halfOpenMaxCalls: 2, trace: rt.trace
});
for (const [id, ok] of [['cb-a', false], ['cb-b', true], ['cb-c', false], ['cb-d', true]]) {
  const lease = acquire(breaker, id);
  release(breaker, lease, { ok, durationTicks: 1 });
}
assert.equal(breaker.snapshot().state, 'open');
const openBefore = breaker.snapshot();
const openReject = breaker.tryAcquire({ opId: 'cb-open-reject' });
assert.equal(openReject.accepted, false);
assert.equal(openReject.reason, 'circuit-open');
assert.equal(breaker.snapshot().active, openBefore.active);
breaker.advanceTicks(3);
assert.equal(breaker.snapshot().state, 'half-open');
const hp1 = acquire(breaker, 'cb-half-probe-one');
const hp2 = acquire(breaker, 'cb-half-probe-two');
const hpReject = breaker.tryAcquire({ opId: 'cb-half-probe-three' });
assert.equal(hpReject.accepted, false);
assert.equal(hpReject.reason, 'half-open-limit');
release(breaker, hp1, { ok: true, durationTicks: 1 });
assert.equal(breaker.snapshot().state, 'half-open');
release(breaker, hp2, { ok: true, durationTicks: 1 });
assert.equal(breaker.snapshot().state, 'closed');
assert.equal(breaker.snapshot().window.total, 0);

// Scenario 3: half-open failure reopens and resets the open timer.
const failingProbe = createCircuitBreakerBulkheadController({ label: 'rev0031-half-open-failure', maxConcurrent: 1, slidingWindowSize: 2, minimumCalls: 2, failureRateThreshold: 50, openDurationTicks: 2, halfOpenMaxCalls: 1, trace: rt.trace });
for (const [id, ok] of [['hp-fail-a', false], ['hp-fail-b', true]]) {
  const lease = acquire(failingProbe, id);
  release(failingProbe, lease, { ok, durationTicks: 1 });
}
assert.equal(failingProbe.snapshot().state, 'open');
failingProbe.advanceTicks(2);
assert.equal(failingProbe.snapshot().state, 'half-open');
const badProbe = acquire(failingProbe, 'hp-fail-probe');
release(failingProbe, badProbe, { ok: false, durationTicks: 1 });
assert.equal(failingProbe.snapshot().state, 'open');
assert.equal(failingProbe.snapshot().openUntilTick, failingProbe.snapshot().nowTick + failingProbe.openDurationTicks);

// Scenario 4: slow-call threshold trips independently of outright failures.
const slowBreaker = createCircuitBreakerBulkheadController({ label: 'rev0031-slow-threshold', maxConcurrent: 1, slidingWindowSize: 4, minimumCalls: 4, failureRateThreshold: 100, slowCallRateThreshold: 50, slowCallDurationTicks: 5, openDurationTicks: 2, halfOpenMaxCalls: 1, trace: rt.trace });
for (const [id, durationTicks] of [['slow-a', 6], ['slow-b', 1], ['slow-c', 7], ['slow-d', 1]]) {
  const lease = acquire(slowBreaker, id);
  release(slowBreaker, lease, { ok: true, durationTicks });
}
assert.equal(slowBreaker.snapshot().state, 'open');
assert.equal(slowBreaker.snapshot().window.slow, 2);

// Scenario 5: runtime object factory and snapshot validation stay wired.
const fromRuntime = rt.circuitBreakerBulkheadController({ label: 'rev0031-runtime-factory', maxConcurrent: 1, slidingWindowSize: 2, minimumCalls: 2 });
assert.equal(validateCircuitBreakerBulkheadSnapshot(fromRuntime.snapshot()).ok, true);

const trace = rt.close();
const traceKinds = kinds(trace);
const requiredTraceKinds = [
  'resilience:create',
  'resilience:acquire',
  'resilience:release',
  'resilience:reject',
  'resilience:window-record',
  'resilience:state-transition',
  'resilience:tick',
  'resilience:half-open-probe-success',
  'object:circuit-breaker-bulkhead-controller-ref'
];
const observations = {
  controllerCreated: true,
  bulkheadCapacityRejectsWithoutMutation: bReject.reason === 'bulkhead-full' && bulkhead.snapshot().active === 0,
  failureThresholdOpensCircuit: openBefore.state === 'open',
  openCircuitRejectsWithoutLeaseGrowth: openReject.reason === 'circuit-open' && breaker.snapshot().stats.circuitOpenRejected >= 1,
  virtualTickMovesOpenToHalfOpen: trace.some((event) => event.kind === 'resilience:state-transition' && event.reason === 'open-duration-elapsed'),
  halfOpenProbeLimitRejects: hpReject.reason === 'half-open-limit',
  halfOpenSuccessesCloseCircuit: breaker.snapshot().state === 'closed',
  halfOpenFailureReopensCircuit: failingProbe.snapshot().state === 'open' && failingProbe.snapshot().stats.opened >= 2,
  slowCallRateOpensCircuit: slowBreaker.snapshot().state === 'open' && slowBreaker.snapshot().window.slow === 2,
  runtimeFactoryIntegration: validateCircuitBreakerBulkheadSnapshot(fromRuntime.snapshot()).ok === true,
  finalLeaseAccountingEmpty: [bulkhead, breaker, failingProbe, slowBreaker, fromRuntime].every((c) => c.snapshot().leaseCount === 0 && c.snapshot().active === 0),
  traceHasRequiredEvents: requiredTraceKinds.every((kind) => hasKind(trace, kind))
};
Object.entries(observations).forEach(([name, value]) => assert.equal(value, true, `${name} should be true`));

const report = {
  project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1, status: 'passed', generatedAt: new Date().toISOString(),
  slice: 'scheduler:circuit-breaker-bulkhead-proof',
  purpose: 'Prove the fake-provider/virtual-tick circuit-breaker + bulkhead baby contract before OPFS/browser/provider integration.',
  observations,
  snapshots: {
    bulkhead: bulkhead.snapshot(),
    breaker: breaker.snapshot(),
    failingProbe: failingProbe.snapshot(),
    slowBreaker: slowBreaker.snapshot(),
    runtimeFactory: fromRuntime.snapshot()
  },
  trace: { count: trace.length, kinds: traceKinds, requiredTraceKinds },
  nonClaims: [
    'No OPFS circuit-breaker/bulkhead proof.',
    'No browser Worker circuit-breaker/bulkhead proof.',
    'No production resilience, latency-SLO, real-time timer, throughput, or cross-browser claim.',
    'No exact Resilience4j, Hystrix, Envoy, Azure, or SRE implementation claim.'
  ]
};
await mkdir(dirname(outPath), { recursive: true });
await writeFile(outPath, JSON.stringify(report, null, 2) + '\n');
console.log(outPath);
