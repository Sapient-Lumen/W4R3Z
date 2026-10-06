#!/usr/bin/env node
import assert from 'node:assert/strict';
import { mkdir, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import { performance } from 'node:perf_hooks';
import { REVISION, VERSION } from '../src/browserrt.mjs';
import { runManagedBrowserPage } from './browser_cdp_fixture.mjs';

const TASK_ID = 'browser:opfs-guarded-corrupt-repair-timeout-proof';
const DEFAULT_OUT = `artifacts/validation/REV${REVISION.slice(3)}-BROWSER-OPFS-GUARDED-CORRUPT-REPAIR-TIMEOUT-PROBE.json`;
const argValue = (argv, flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };
const hasFlag = (argv, flag) => argv.includes(flag);

function pageExpression({ prefix, lockPrefix, lockName, lockTimeoutMs, holdMs, payloadBytes, corruptBytes }) {
  return `(async () => {
    const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));
    const bytesFromSeed = (seed, count) => {
      const out = new Uint8Array(count);
      const enc = new TextEncoder().encode(seed);
      out.set(enc.slice(0, Math.min(enc.length, out.length)));
      for (let i = enc.length; i < out.length; i += 1) out[i] = (31 + i * 17 + (i >>> 2)) & 255;
      return out;
    };
    const moduleUrl = new URL('/src/browserrt.mjs', location.href).href;
    const m = await import(moduleUrl);
    const rt = await m.boot({ telemetry: 'browser-cdp', proof: '${REVISION}', opfsAsyncBlockStoreProof: true, opfsGuardedCorruptRepairTimeoutProof: true });
    const store = rt.opfsAsyncBlockStore({
      name: '${REVISION}-guarded-corrupt-repair-timeout-store',
      prefix: ${JSON.stringify(prefix)}
    });
    const guard = rt.opfsWebLockGuardedBlockStore({
      store,
      lockPrefix: ${JSON.stringify(lockPrefix)},
      lockName: ${JSON.stringify(lockName)},
      label: '${REVISION}-guarded-corrupt-repair-timeout-guard',
      lockTimeoutMs: 1000
    });
    const cleanupBefore = await guard.cleanupForTest({ timeoutMs: 1000 });

    async function bucketForHash(hash, create) {
      const root = await navigator.storage.getDirectory();
      let dir = root;
      for (const part of ${JSON.stringify(prefix)}.split('/').filter(Boolean)) dir = await dir.getDirectoryHandle(part, { create: true });
      const a = await dir.getDirectoryHandle(hash.slice(0, 2), { create });
      return await a.getDirectoryHandle(hash.slice(2, 4), { create });
    }
    async function createWritableExclusive(file) {
      try { return await file.createWritable({ mode: 'exclusive' }); }
      catch (error) { if (error?.name === 'TypeError') return await file.createWritable(); throw error; }
    }
    async function digest(bytes) { return 'sha256:' + await m.digestBytesHex(bytes); }

    const payload = bytesFromSeed('BrowserRT ${REVISION} guarded corrupt repair timeout payload', ${JSON.stringify(payloadBytes)});
    const hash = await m.digestBytesHex(payload);
    const digestExpected = 'sha256:' + hash;
    const ref = Object.freeze({ kind: 'block', id: 'block:sha256:' + hash, digest: digestExpected, hash, algorithm: 'sha256', backend: 'opfs-async-block-store-v0', bytes: payload.byteLength, path: store.blockPath(hash) });
    const corrupt = bytesFromSeed('BrowserRT ${REVISION} deliberately corrupt final hash residue', ${JSON.stringify(corruptBytes)});
    corrupt[0] ^= 0xa5;
    corrupt[corrupt.length - 1] ^= 0x5a;
    const corruptDigest = await digest(corrupt);
    const bucket = await bucketForHash(hash, true);
    const file = await bucket.getFileHandle(hash + '.blk', { create: true });
    const writable = await createWritableExclusive(file);
    await writable.write(corrupt);
    await writable.close();

    const hasBefore = await guard.has(ref);
    const verifyBefore = await guard.verify(ref);
    let getBeforeError = null;
    try { await guard.get(ref); } catch (error) { getBeforeError = { name: error?.name || 'Error', message: error?.message || String(error), code: error?.code || null, detail: error?.detail || null }; }
    const repaired = await guard.put(payload, { label: 'guarded-repair-after-corrupt-final-path' });
    const verifyAfterRepair = await guard.verify(repaired.ref);
    const gotAfterRepair = await guard.get(repaired.ref);
    const digestAfterRepair = await digest(gotAfterRepair);
    const duplicateAfterRepair = await guard.put(payload, { label: 'guarded-duplicate-after-repair' });
    const verifyAfterDuplicate = await guard.verify(duplicateAfterRepair.ref);

    const timeoutPayload = bytesFromSeed('BrowserRT ${REVISION} guarded timeout candidate should not persist', Math.max(8192, Math.floor(${JSON.stringify(payloadBytes)} / 2)));
    const timeoutHash = await m.digestBytesHex(timeoutPayload);
    const timeoutDigest = 'sha256:' + timeoutHash;
    let holderEnteredAt = null;
    let holderReleasedAt = null;
    const holder = guard.withExclusive(async () => {
      holderEnteredAt = performance.now();
      await sleep(${JSON.stringify(holdMs)});
      holderReleasedAt = performance.now();
      return { heldMs: holderReleasedAt - holderEnteredAt };
    }, { op: 'same-page-held-exclusive-for-timeout' }, { timeoutMs: 0 });
    const waitStart = performance.now();
    while (holderEnteredAt === null && performance.now() - waitStart < 1000) await sleep(5);
    let timeoutError = null;
    try {
      await guard.put(timeoutPayload, { label: 'guarded-timeout-candidate' }, { timeoutMs: ${JSON.stringify(lockTimeoutMs)} });
    } catch (error) {
      timeoutError = { name: error?.name || 'Error', message: error?.message || String(error), code: error?.code || null, detail: error?.detail || null };
    }
    const holderResult = await holder;
    const timeoutPresentAfterHolder = await guard.has(timeoutDigest);
    const recoveryPut = await guard.put(bytesFromSeed('BrowserRT ${REVISION} guarded timeout recovery payload', 16384), { label: 'guarded-timeout-recovery' }, { timeoutMs: 250 });
    const recoveryVerify = await guard.verify(recoveryPut.ref);
    const settled = await guard.coordinator.waitForSettled(guard.fullLockName, { timeoutMs: 500, intervalMs: 10 });
    const query = typeof navigator.locks?.query === 'function' ? await navigator.locks.query() : null;
    const cleanupAfter = await guard.cleanupForTest({ timeoutMs: 1000 });
    const snapshot = guard.snapshot();
    const trace = rt.close();
    return JSON.stringify({
      project: 'BrowserRT', revision: m.REVISION, version: m.VERSION, taskId: '${TASK_ID}',
      page: { location: location.href, readyState: document.readyState, crossOriginIsolated, isSecureContext, origin: location.origin },
      capabilities: m.detectCapabilities(globalThis),
      prefix: ${JSON.stringify(prefix)}, lockPrefix: ${JSON.stringify(lockPrefix)}, lockName: ${JSON.stringify(lockName)}, lockTimeoutMs: ${JSON.stringify(lockTimeoutMs)}, holdMs: ${JSON.stringify(holdMs)},
      cleanupBefore,
      digestExpected, corruptDigest, corruptBytes: corrupt.byteLength, payloadBytes: payload.byteLength, ref,
      hasBefore, verifyBefore, getBeforeError,
      repaired, verifyAfterRepair, digestAfterRepair, duplicateAfterRepair, verifyAfterDuplicate,
      timeoutDigest, timeoutError, holderResult, holderEnteredAt, holderReleasedAt, timeoutPresentAfterHolder,
      recoveryPut: { digest: recoveryPut.digest, bytes: recoveryPut.bytes, duplicate: recoveryPut.duplicate, path: recoveryPut.path, ref: recoveryPut.ref }, recoveryVerify,
      settled, query: query ? { heldCount: query.held?.length ?? null, pendingCount: query.pending?.length ?? null, held: query.held, pending: query.pending } : null,
      cleanupAfter, snapshot,
      traceKinds: trace.map((event) => event.kind),
      normalizedTrace: trace.map((event) => ({ kind: event.kind, name: event.name, mode: event.mode, timeoutMs: event.timeoutMs, op: event.op, error: event.error, digest: event.digest, actualDigest: event.actualDigest, duplicate: event.duplicate, repairedCorrupt: event.repairedCorrupt, source: event.source, writerMode: event.writerMode, verifiedAfterWrite: event.verifiedAfterWrite })).filter((event) => event.kind)
    });
  })()`;
}

export async function runProbe(options = {}) {
  const started = performance.now();
  const prefix = options.prefix || `browserrt/${REVISION}/opfs-guarded-corrupt-repair-timeout-proof`;
  const lockPrefix = options.lockPrefix || 'browserrt:opfs-guarded-corrupt-repair-timeout';
  const lockName = options.lockName || `${REVISION}-guarded-corrupt-repair-timeout-lock`;
  const lockTimeoutMs = Number(options.lockTimeoutMs || 45);
  const holdMs = Number(options.holdMs || 160);
  const payloadBytes = Number(options.payloadBytes || 32 * 1024);
  const corruptBytes = Number(options.corruptBytes || 12 * 1024);
  if (!Number.isFinite(lockTimeoutMs) || lockTimeoutMs < 10 || lockTimeoutMs > 1000) throw new Error('lockTimeoutMs must be between 10 and 1000');
  if (!Number.isFinite(holdMs) || holdMs <= lockTimeoutMs || holdMs > 5000) throw new Error('holdMs must be greater than lockTimeoutMs and <= 5000');
  if (!Number.isFinite(payloadBytes) || payloadBytes < 4096 || payloadBytes > 1024 * 1024) throw new Error('payloadBytes must be between 4 KiB and 1 MiB');
  const { result, harness } = await runManagedBrowserPage({
    timeoutMs: options.timeoutMs,
    chromium: options.chromium,
    relaxPolicy: options.relaxPolicy,
    pagePath: '/opfs-guarded-corrupt-repair-timeout-probe.html',
    pageTitle: 'BrowserRT OPFS guarded corrupt repair and timeout probe',
    allowedPrefixes: ['src/'],
    profilePrefix: 'browserrt-opfs-guarded-corrupt-repair-timeout-',
    stderrTerms: ['opfs', 'lock', 'timeout', 'corrupt', 'checksum', 'storage']
  }, async ({ evalJson, pageUrl, mark, timeoutMs }) => {
    const evalStart = performance.now();
    const report = await evalJson(pageExpression({ prefix, lockPrefix, lockName, lockTimeoutMs, holdMs, payloadBytes, corruptBytes }), timeoutMs);
    mark('browser-opfs-guarded-corrupt-repair-timeout-eval', evalStart);
    report.pageUrl = pageUrl;
    return report;
  });

  assert.equal(result.project, 'BrowserRT');
  assert.equal(result.revision, REVISION);
  assert.equal(result.version, VERSION);
  assert.equal(result.taskId, TASK_ID);
  assert.equal(result.page.crossOriginIsolated, true);
  assert.equal(result.page.isSecureContext, true);
  assert.equal(result.capabilities.opfs, true);
  assert.equal(result.capabilities.webLocks, true);
  assert.equal(result.hasBefore, false, 'guarded has() must reject corrupt final hash file');
  assert.equal(result.verifyBefore.present, true, 'verify() must see corrupt final hash file');
  assert.equal(result.verifyBefore.ok, false, 'verify() must reject corrupt final hash file');
  assert.equal(result.verifyBefore.actualDigest, result.corruptDigest);
  assert.equal(result.getBeforeError?.code, 'BRT_OPFS_BLOCK_CHECKSUM_MISMATCH');
  assert.equal(result.repaired.duplicate, false);
  assert.equal(result.repaired.repairedCorrupt, true);
  assert.equal(result.verifyAfterRepair.ok, true);
  assert.equal(result.digestAfterRepair, result.digestExpected);
  assert.equal(result.duplicateAfterRepair.duplicate, true);
  assert.equal(result.verifyAfterDuplicate.ok, true);
  assert.equal(result.timeoutError?.code, 'BRT_WEB_LOCK_TIMEOUT');
  assert.equal(result.timeoutPresentAfterHolder, false, 'timed-out guarded candidate must remain absent after holder releases');
  assert.equal(result.recoveryVerify.ok, true);
  assert.equal(result.settled.ok, true);
  assert.equal(result.query?.heldCount ?? 0, 0);
  assert.equal(result.query?.pendingCount ?? 0, 0);
  assert.equal(result.cleanupAfter, true);
  assert.equal(result.snapshot.store.stats.corruptRepairs, 1);
  assert.equal(result.snapshot.store.stats.corruptDeletes, 1);
  assert.equal(result.snapshot.coordinator.stats.timeouts, 1);
  for (const kind of ['storage:opfs-block-corrupt', 'storage:opfs-block-repair', 'storage:opfs-block-write-close', 'storage:opfs-block-integrity-ok', 'coord:web-lock-timeout', 'coord:web-lock-wait-settled-complete']) {
    assert.ok(result.traceKinds.includes(kind), `missing trace kind ${kind}`);
  }

  return {
    project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1,
    probe_id: `${REVISION}-browser-opfs-guarded-corrupt-repair-timeout-proof`, status: 'passed', generatedAt: new Date().toISOString(),
    taskId: TASK_ID,
    purpose: 'Managed Chromium proof that BrowserRT can combine WebLockGuardedBlockStore coordination with OPFS content-addressed corruption repair and acquisition timeout recovery without accepting corrupt files or timed-out mutations.',
    durationMs: Math.round(performance.now() - started),
    observed: {
      payloadBytes: result.payloadBytes,
      corruptBytes: result.corruptBytes,
      hasBefore: result.hasBefore,
      verifyBeforeOk: result.verifyBefore.ok,
      getBeforeCode: result.getBeforeError?.code,
      repairedCorrupt: result.repaired.repairedCorrupt,
      duplicateAfterRepair: result.duplicateAfterRepair.duplicate,
      timeoutCode: result.timeoutError?.code,
      timeoutPresentAfterHolder: result.timeoutPresentAfterHolder,
      recoveryVerify: result.recoveryVerify.ok,
      settled: result.settled,
      stats: result.snapshot.store.stats,
      coordinatorStats: result.snapshot.coordinator.stats,
      traceKinds: result.traceKinds,
      harnessDurationMs: harness.durationMs,
      policy: harness.policyRelaxation,
      chromeStderrSummary: harness.chromeStderrSummary
    },
    checks: [
      'guarded has/get/verify reject a corrupt final content-addressed OPFS block',
      'guarded put repairs the corrupt block and verifies the rewritten content before dedupe',
      'duplicate put dedupes only after the repaired bytes verify',
      'a queued guarded put behind a held exclusive Web Lock times out as BRT_WEB_LOCK_TIMEOUT',
      'the timed-out candidate is absent after the lock holder releases',
      'a later guarded recovery write verifies and lock state settles'
    ],
    nonClaims: [
      'Chromium-in-cloudtainer proof only; no cross-browser Web Locks or OPFS conformance claim.',
      'The corrupt final file is deliberately injected, not organic filesystem, crash, or power-loss evidence.',
      'The timeout bounds pending lock acquisition only; it does not cancel work after a lock has been granted.',
      'No OPFS fsync durability, quota survival, eviction survival, persistent-storage retention, fairness, starvation-freedom, throughput, latency, SLO, or production readiness claim.'
    ]
  };
}

const argv = process.argv.slice(2);
const out = argValue(argv, '--json', DEFAULT_OUT);
const timeoutMs = Number(argValue(argv, '--timeout-ms', '45000'));
const chromium = argValue(argv, '--chromium', null);
const prefix = argValue(argv, '--prefix', null);
const lockTimeoutMs = Number(argValue(argv, '--lock-timeout-ms', '45'));
const holdMs = Number(argValue(argv, '--hold-ms', '160'));
const payloadBytes = Number(argValue(argv, '--payload-bytes', String(32 * 1024)));
const corruptBytes = Number(argValue(argv, '--corrupt-bytes', String(12 * 1024)));
const relaxPolicy = !hasFlag(argv, '--no-policy-relaxation');

try {
  const report = await runProbe({ timeoutMs, chromium, prefix, lockTimeoutMs, holdMs, payloadBytes, corruptBytes, relaxPolicy });
  if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); console.log(out); }
  else console.log(JSON.stringify(report, null, 2));
} catch (error) {
  const report = { project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1, probe_id: `${REVISION}-browser-opfs-guarded-corrupt-repair-timeout-proof`, status: 'failed', generatedAt: new Date().toISOString(), error: { name: error?.name || 'Error', message: error?.message || String(error), stack: error?.stack }, nonClaims: ['Failed browser OPFS guarded corrupt repair timeout proof is not silently skipped.'] };
  if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); console.error(out); }
  console.error(`[browser_opfs_guarded_corrupt_repair_timeout_probe] FAIL: ${error?.stack || error}`);
  process.exitCode = 1;
}
