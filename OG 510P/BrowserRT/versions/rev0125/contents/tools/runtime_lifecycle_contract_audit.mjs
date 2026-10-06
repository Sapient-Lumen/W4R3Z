#!/usr/bin/env node
import assert from 'node:assert/strict';
import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import { performance } from 'node:perf_hooks';
import { REVISION, VERSION } from '../src/browserrt.mjs';

const PREFIX = `REV${REVISION.slice(3)}`;
const DEFAULT_OUT = `artifacts/audit/${PREFIX}-RUNTIME-LIFECYCLE-CONTRACT-AUDIT.json`;
const argValue = (argv, flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };
const includeAll = (name, body, needles) => {
  const missing = needles.filter((needle) => !body.includes(needle));
  return { name, status: missing.length === 0 ? 'passed' : 'failed', missing };
};

async function text(path) { return await readFile(path, 'utf8'); }

export async function runAudit() {
  const started = performance.now();
  const browserrt = await text('src/browserrt.mjs');
  const agentRuntime = await text('src/agent-runtime.mjs');
  const nodeWorker = await text('src/node-agent-worker.mjs');
  const browserWorker = await text('src/browser-agent-worker.mjs');
  const smoke = await text('test/smoke.mjs');
  const types = await text('src/types.d.ts');
  const opfsStore = await text('src/opfs-block-store.mjs');
  const laneAdapter = await text('src/block-store-lane-adapter.mjs');
  const guardedStore = await text('src/opfs-web-lock-guarded-block-store.mjs');
  const checks = [
    includeAll('bounded-channel-waiters-finite', browserrt, ['maxWaitingSenders', 'maxWaitingReceivers', 'BRT_CHANNEL_WAITERS_FULL', 'failed-waiter-limit']),
    includeAll('bounded-channel-waits-abortable-and-closeable', browserrt, ['channel:send-abort', 'channel:receive-abort', 'channel:send-timeout', 'channel:receive-timeout', 'channel:close']),
    includeAll('worker-agent-startup-deadline', browserrt, ['readyTimeoutMs', 'agent:ready-timeout', 'BRT_AGENT_READY_TIMEOUT']),
    includeAll('worker-agent-call-cancellation', browserrt, ['agent:cancel-sent', 'agent:call-timeout', 'agent:call-abort', 'agent:late-error-after-cancel', 'agent:late-result-after-cancel']),
    includeAll('worker-agent-cancel-escalation', browserrt, ['terminateOnCancel', 'cancelGraceMs', 'agent:cancel-escalate-terminate', 'agent:cancel-escalate-error', '#scheduleCancelEscalation']),
    includeAll('worker-shells-own-per-call-controllers', nodeWorker + browserWorker, ['const controllers = new Map()', "message.type === 'agent:cancel'", 'AbortController', 'agent:cancelled']),
    includeAll('agent-runtime-cooperative-cancellation', agentRuntime, ['throwIfAborted', "message.op === 'delayed-echo'", 'controls.signal']),
    includeAll('agent-runtime-noncooperative-cancellation-proof', agentRuntime, ["message.op === 'busy-loop'", 'busyLoopMs', 'busy-loop']),
    includeAll('operation-scope-lifecycle-present', browserrt, ['class OperationScope', 'scope:create', 'scope:abort', 'scope:close', 'scope:resource-close', 'BRT_SCOPE_TIMEOUT', 'BRT_SCOPE_CLOSED']),
    includeAll('runtime-resource-owner-present', browserrt, ['class RuntimeResourceOwner', 'runtime:resource-own', 'runtime:resource-close', 'closeAsync', 'ownedResources']),
    includeAll('runtime-factories-track-closeable-resources', browserrt, ["track(channel, 'channel'", "track(agent, 'worker-agent'", "track(supervisor, 'supervisor'", "track(ring, 'shared-int32-ring'", "track(ring, 'shared-frame-ring'", "track(store, 'opfs-async-block-store'", "track(adapter, 'opfs-storage-lane-adapter'", "track(guard, 'opfs-web-lock-guarded-block-store'"]),
    includeAll('opfs-close-boundary-owned-by-runtime', browserrt + smoke + types + opfsStore + laneAdapter + guardedStore, ['BRT_OPFS_STORE_CLOSED', 'BRT_BLOCK_STORE_LANE_ADAPTER_CLOSED', 'BRT_OPFS_WEB_LOCK_GUARD_CLOSED', 'runtime-owned-close-opfs-store', 'runtime-owned-close-opfs-adapter', 'runtime-owned-close-opfs-guard', 'storage:opfs-blockstore-close', 'block-store-lane:close', 'storage:opfs-web-lock-guard-close']),
    includeAll('smoke-exercises-runtime-lifecycle', smoke, ['waiter-bound-smoke', 'receive-abort-smoke', 'scope-smoke', 'scope-owned-channel', "agent.call('delayed-echo'", 'NeverReadyWorker', 'noncooperative-cancel-agent', 'agent:cancel-escalate-terminate', 'runtime-owned-close-agent', 'closeAsync']),
    includeAll('types-expose-lifecycle-contract', types, ['maxWaitingSenders', 'maxWaitingReceivers', 'OperationScope', 'RtOperationScopeLike', 'scope(config', 'closeAsync', 'ownedResources', 'readyTimeoutMs', 'cancelOnTimeout', 'terminateOnCancel', 'cancelGraceMs'])
  ];
  for (const check of checks) assert.equal(check.status, 'passed', `${check.name} missing ${check.missing.join(', ')}`);
  return Object.freeze({
    project: 'BrowserRT',
    revision: REVISION,
    version: VERSION,
    schema: 1,
    status: 'passed',
    audit_id: `${REVISION}-runtime-lifecycle-contract-audit`,
    generatedAt: new Date().toISOString(),
    durationMs: Math.round(performance.now() - started),
    purpose: 'Audit the rev0121 runtime lifecycle refactor that closes false-green risk seams: finite channel waiters, scoped operation ownership, cooperative cancellation with opt-in worker termination escalation, startup deadlines, and deterministic resource close.',
    checks,
    correctedRiskSeams: [
      'BoundedChannel no longer allows unbounded pending senders/receivers under overflow=wait.',
      'WorkerAgent timeouts and caller aborts now send per-call cancellation to worker shells and classify late settlements.',
      'OperationScope now gives callers a bounded owner for child scopes, closeable resources, cleanup callbacks, and abort propagation.',
      'WorkerAgent calls can opt into terminateOnCancel with cancelGraceMs so non-cooperative work cannot survive invisibly after abandonment.',
      'WorkerAgent startup now has a ready deadline instead of an immortal ready promise.',
      'boot() now owns closeable resources it creates and exposes closeAsync()/ownedResources() for deterministic teardown evidence.',
      'The smoke test now exercises a non-cooperative busy loop and proves cancel escalation terminates the stuck worker.'
    ],
    remainingRisks: [
      'Worker cancellation is cooperative by default; terminateOnCancel is opt-in because escalation terminates the whole WorkerAgent, not just one call.',
      'Compatibility close() dispatches resource closure but returns the legacy trace array; closeAsync() is the deterministic close contract.',
      'Cross-browser behavior for these lifecycle paths still depends on browser-tier probes.'
    ],
    nonClaims: [
      'This audit reads source/test contract evidence and does not replace runtime smoke or browser execution.',
      'No OPFS crash durability, quota reservation, eviction survival, or cross-browser conformance claim.'
    ]
  });
}

const out = argValue(process.argv.slice(2), '--json', DEFAULT_OUT);
runAudit().then(async (report) => {
  if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); console.log(out); }
  else console.log(JSON.stringify(report, null, 2));
}).catch(async (error) => {
  const report = { project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1, status: 'failed', error: { name: error?.name || 'Error', message: error?.message || String(error), stack: error?.stack } };
  if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); console.log(out); }
  console.error(`[runtime_lifecycle_contract_audit] FAIL: ${error.stack || error.message}`);
  process.exitCode = 1;
});
