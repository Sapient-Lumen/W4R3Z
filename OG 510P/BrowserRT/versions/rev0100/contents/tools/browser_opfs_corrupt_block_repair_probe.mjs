#!/usr/bin/env node
import assert from 'node:assert/strict';
import { mkdir, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import { performance } from 'node:perf_hooks';
import { REVISION, VERSION } from '../src/browserrt.mjs';
import { runManagedBrowserPage } from './browser_cdp_fixture.mjs';

const TASK_ID = 'browser:opfs-corrupt-block-repair-proof';
const DEFAULT_OUT = `artifacts/validation/REV${REVISION.slice(3)}-BROWSER-OPFS-CORRUPT-BLOCK-REPAIR-PROBE.json`;
const argValue = (argv, flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };
const hasFlag = (argv, flag) => argv.includes(flag);

function corruptRepairExpression(prefix, payloadBytes) {
  return `(async()=>{
    const m=await import('/src/browserrt.mjs?rev=${REVISION}&slice=opfs-corrupt-block-repair');
    const rt=await m.boot({telemetry:'browser-cdp',proof:'${REVISION}',browserCdpHarness:true,opfsAsyncBlockStoreProof:true,opfsCorruptBlockRepairProof:true});
    const store=rt.opfsAsyncBlockStore({name:'${REVISION}-opfs-corrupt-block-repair-store',prefix:${JSON.stringify(prefix)}});
    await store.cleanupForTest();

    const payload=new Uint8Array(${Number(payloadBytes)});
    for (let i=0;i<payload.length;i++) payload[i]=(i*31+${REVISION.slice(3)}) & 255;
    const marker=new TextEncoder().encode('BrowserRT ${REVISION} corrupt final block repair proof / ');
    payload.set(marker.slice(0, Math.min(marker.length, payload.length)));
    const hash=await m.digestBytesHex(payload);
    const digest='sha256:'+hash;
    const ref={kind:'block',id:'block:sha256:'+hash,digest,hash,algorithm:'sha256',backend:'opfs-async-block-store-v0',bytes:payload.byteLength,path:store.blockPath(hash)};

    async function bucketForHash(create=true) {
      const root=await navigator.storage.getDirectory();
      let dir=root;
      for (const part of ${JSON.stringify(prefix)}.split('/').filter(Boolean)) dir=await dir.getDirectoryHandle(part,{create});
      dir=await dir.getDirectoryHandle(hash.slice(0,2),{create});
      return await dir.getDirectoryHandle(hash.slice(2,4),{create});
    }
    async function createWritableExclusive(file) {
      try { return await file.createWritable({mode:'exclusive'}); } catch (e) { if (e?.name === 'TypeError') return await file.createWritable(); throw e; }
    }

    const corruptBytes=new Uint8Array(Math.max(32, Math.floor(payload.length/2)));
    for (let i=0;i<corruptBytes.length;i++) corruptBytes[i]=(payload[i % payload.length]^0xa5)&255;
    const corruptDigest='sha256:'+await m.digestBytesHex(corruptBytes);
    const bucket=await bucketForHash(true);
    const file=await bucket.getFileHandle(hash+'.blk',{create:true});
    const writable=await createWritableExclusive(file);
    await writable.write(corruptBytes);
    await writable.close();

    const hasBefore=await store.has(ref);
    const verifyBefore=await store.verify(ref);
    let getBeforeError=null;
    try { await store.get(ref); } catch (error) { getBeforeError={name:error?.name||'Error',message:error?.message||String(error),code:error?.code||null,detail:error?.detail||null}; }

    const repairedPut=await store.put(payload,{label:'repair-after-corrupt-final-path'});
    const hasAfterRepair=await store.has(repairedPut.ref);
    const verifyAfterRepair=await store.verify(repairedPut.ref);
    const gotAfterRepair=await store.get(repairedPut.ref);
    const digestAfterRepair='sha256:'+await m.digestBytesHex(gotAfterRepair);
    const duplicatePut=await store.put(payload,{label:'duplicate-after-repair'});
    const verifyAfterDuplicate=await store.verify(duplicatePut.ref);
    const deleted=await store.delete(repairedPut.ref);
    const hasAfterDelete=await store.has(repairedPut.ref);
    const cleanup=await store.cleanupForTest();
    const snapshot=store.snapshot();
    const trace=rt.close();
    return JSON.stringify({project:'BrowserRT',revision:m.REVISION,version:m.VERSION,taskId:'${TASK_ID}',
      page:{location:location.href,readyState:document.readyState,crossOriginIsolated,isSecureContext,origin:location.origin},
      capabilities:m.detectCapabilities(globalThis),availableTierNames:m.availableCapabilityTierNames(m.detectCapabilities(globalThis)),
      prefix:${JSON.stringify(prefix)},payloadBytes:payload.byteLength,hash,digest,ref,corrupt:{bytes:corruptBytes.byteLength,digest:corruptDigest,path:store.blockPath(hash)},
      hasBefore,verifyBefore,getBeforeError,repairedPut,hasAfterRepair,verifyAfterRepair,digestAfterRepair,duplicatePut,verifyAfterDuplicate,deleted,hasAfterDelete,cleanup,snapshot,
      traceKinds:trace.map(e=>e.kind),normalizedTrace:trace.map(e=>({kind:e.kind,digest:e.digest,actualDigest:e.actualDigest,bytes:e.bytes,duplicate:e.duplicate,repairedCorrupt:e.repairedCorrupt,deleted:e.deleted,path:e.path,store:e.store,prefix:e.prefix,label:e.label,source:e.source,writerMode:e.writerMode,verifiedAfterWrite:e.verifiedAfterWrite})).filter(e=>e.kind)});
  })()`;
}

export async function runProbe(options = {}) {
  const prefix = options.prefix || `browserrt/${REVISION}/opfs-corrupt-block-repair-proof`;
  const payloadBytes = Number(options.payloadBytes || 48 * 1024);
  if (!Number.isFinite(payloadBytes) || payloadBytes < 1024 || payloadBytes > 1024 * 1024) throw new Error('payloadBytes must be between 1 KiB and 1 MiB');
  const started = performance.now();
  const { result, harness } = await runManagedBrowserPage({
    timeoutMs: options.timeoutMs,
    chromium: options.chromium,
    relaxPolicy: options.relaxPolicy,
    pagePath: '/opfs-corrupt-block-repair-probe.html',
    pageTitle: 'BrowserRT OPFS corrupt block repair probe',
    allowedPrefixes: ['src/'],
    profilePrefix: 'browserrt-opfs-corrupt-repair-',
    stderrTerms: ['opfs','file','storage','corrupt','quota']
  }, async ({ evalJson, pageUrl, mark, timeoutMs }) => {
    const evalStart = performance.now();
    const report = await evalJson(corruptRepairExpression(prefix, payloadBytes), timeoutMs);
    mark('browser-opfs-corrupt-block-repair-eval', evalStart);
    report.pageUrl = pageUrl;
    return report;
  });

  assert.equal(result.project, 'BrowserRT');
  assert.equal(result.revision, REVISION);
  assert.equal(result.version, VERSION);
  assert.equal(result.taskId, TASK_ID);
  assert.equal(result.page.crossOriginIsolated, true, 'probe server must keep cross-origin isolation active');
  assert.equal(result.hasBefore, false, 'corrupt final-hash file must not satisfy has()');
  assert.equal(result.verifyBefore.present, true, 'verify() should see the corrupt file before repair');
  assert.equal(result.verifyBefore.ok, false, 'verify() should reject corrupt content before repair');
  assert.equal(result.verifyBefore.actualDigest, result.corrupt.digest, 'verify() should report the corrupt file digest');
  assert.equal(result.getBeforeError?.code, 'BRT_OPFS_BLOCK_CHECKSUM_MISMATCH', 'get() must fail closed on corrupt content');
  assert.equal(result.repairedPut.duplicate, false, 'repair put must rewrite, not accept corrupt duplicate');
  assert.equal(result.repairedPut.repairedCorrupt, true, 'put() must classify the rewrite as corrupt repair');
  assert.equal(result.repairedPut.repair?.existing?.actualDigest, result.corrupt.digest, 'repair detail must point at corrupt digest');
  assert.equal(result.hasAfterRepair, true);
  assert.equal(result.verifyAfterRepair.ok, true);
  assert.equal(result.digestAfterRepair, result.digest);
  assert.equal(result.duplicatePut.duplicate, true, 'second put after repair should dedupe only after valid-content verification');
  assert.equal(result.duplicatePut.repairedCorrupt, false);
  assert.equal(result.verifyAfterDuplicate.ok, true);
  assert.equal(result.deleted, true);
  assert.equal(result.hasAfterDelete, false);
  assert.equal(result.snapshot.stats.corruptBlocksDetected >= 2, true, 'corrupt file should be detected by has/verify/get or put');
  assert.equal(result.snapshot.stats.corruptRepairs, 1);
  assert.equal(result.snapshot.stats.corruptDeletes, 1);
  assert.equal(result.snapshot.stats.postWriteVerifications >= 1, true);
  for (const kind of ['runtime:boot','storage:opfs-block-corrupt','storage:opfs-block-repair','storage:opfs-block-write-close','storage:opfs-block-integrity-ok','storage:opfs-block-put','storage:opfs-block-get','storage:opfs-block-delete','storage:opfs-block-cleanup','runtime:close']) {
    assert.ok(result.traceKinds.includes(kind), `missing OPFS corrupt-repair trace kind ${kind}`);
  }

  return {
    project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1,
    probe_id: `${REVISION}-browser-opfs-corrupt-block-repair-proof`, status: 'passed', generatedAt: new Date().toISOString(),
    taskId: TASK_ID,
    purpose: 'Managed Chromium/CDP proof that the async OPFS block store does not trust final hash-path existence: corrupt content is rejected by has/get/verify and repaired by a subsequent content-addressed put.',
    durationMs: Math.round(performance.now() - started),
    observed: {
      payloadBytes: result.payloadBytes,
      corruptBytes: result.corrupt.bytes,
      digest: result.digest,
      corruptDigest: result.corrupt.digest,
      hasBefore: result.hasBefore,
      verifyBeforeOk: result.verifyBefore.ok,
      getBeforeCode: result.getBeforeError?.code,
      repairedPutDuplicate: result.repairedPut.duplicate,
      repairedCorrupt: result.repairedPut.repairedCorrupt,
      duplicateAfterRepair: result.duplicatePut.duplicate,
      stats: result.snapshot.stats,
      traceKinds: result.traceKinds,
      harnessDurationMs: harness.durationMs,
      policy: harness.policyRelaxation,
      chromeStderrSummary: harness.chromeStderrSummary
    },
    checks: [
      'corrupt final-hash file did not satisfy has()',
      'verify() reported present but checksum-mismatch before repair',
      'get() failed closed with BRT_OPFS_BLOCK_CHECKSUM_MISMATCH',
      'put() deleted and rewrote the corrupt file instead of accepting filename-only dedupe',
      'second put deduped only after valid-content verification',
      'delete/cleanup removed the repaired namespace'
    ],
    nonClaims: [
      'Chromium-in-cloudtainer async OPFS corruption-repair proof only, not cross-browser conformance.',
      'This proof injects a corrupt final block file deliberately; it is not organic crash, power-loss, quota-eviction, or filesystem-fault evidence.',
      'Content verification and repair do not prove fsync durability, persistent-storage retention, Storage Buckets behavior, multi-tab coordination, throughput, latency, or production durability.',
      'Browser-heavy proof remains explicit browser/full tier only; broad release remains browser-light.'
    ]
  };
}

const argv = process.argv.slice(2);
const out = argValue(argv, '--json', DEFAULT_OUT);
const timeoutMs = Number(argValue(argv, '--timeout-ms', '36000'));
const chromium = argValue(argv, '--chromium', null);
const prefix = argValue(argv, '--prefix', null);
const payloadBytes = Number(argValue(argv, '--payload-bytes', String(48 * 1024)));
const relaxPolicy = !hasFlag(argv, '--no-policy-relaxation');

try {
  const report = await runProbe({ timeoutMs, chromium, prefix, payloadBytes, relaxPolicy });
  if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); console.log(out); }
  else console.log(JSON.stringify(report, null, 2));
} catch (error) {
  const report = { project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1, probe_id: `${REVISION}-browser-opfs-corrupt-block-repair-proof`, status: 'failed', generatedAt: new Date().toISOString(), error: { name: error?.name || 'Error', message: error?.message || String(error), stack: error?.stack }, nonClaims: ['Failed browser OPFS corrupt block repair proof is not silently skipped; keep it outside broad release and debug by id.'] };
  if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); console.error(out); }
  console.error(`[browser_opfs_corrupt_block_repair_probe] FAIL: ${error?.stack || error}`);
  process.exitCode = 1;
}
