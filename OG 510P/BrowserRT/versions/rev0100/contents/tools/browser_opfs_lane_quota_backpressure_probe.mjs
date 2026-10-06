#!/usr/bin/env node
import assert from 'node:assert/strict';
import { mkdir, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import { performance } from 'node:perf_hooks';
import { REVISION, VERSION } from '../src/browserrt.mjs';
import { runManagedBrowserPage, getStorageUsageAndQuota, overrideStorageQuotaForOrigin, resetStorageQuotaOverrideForOrigin } from './browser_cdp_fixture.mjs';
// Uses CDP Storage.getUsageAndQuota / Storage.overrideQuotaForOrigin through browser_cdp_fixture helpers.

const DEFAULT_OUT = `artifacts/validation/REV${REVISION.slice(3)}-BROWSER-OPFS-LANE-QUOTA-BACKPRESSURE-PROBE.json`;
const argValue = (argv, flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };
const hasFlag = (argv, flag) => argv.includes(flag);

function adapterConfig(prefix, label) {
  return `{
    label:${JSON.stringify(label)},
    prefix:${JSON.stringify(prefix)},
    schedulerConfig:{lanes:[
      {id:'storage',rank:70,capacity:1,quantum:65536,maxQueuedCost:262144},
      {id:'maintenance',rank:10,capacity:1,quantum:64,maxQueuedCost:4096}
    ],maxQueuedCost:266240}
  }`;
}

function exprForPrep(prefix) {
  return `(async()=>{
    const m=await import('/src/browserrt.mjs?rev=${REVISION}&slice=opfs-lane-quota-prep');
    const rt=await m.boot({telemetry:'browser-cdp',proof:'${REVISION}',browserCdpHarness:true,opfsAsyncBlockStoreProof:true,opfsStorageLaneAdapterProof:true,opfsLaneQuotaBackpressureProof:true,storageLaneProviderProof:true,crossLaneScheduler:true});
    const adapter=rt.opfsBlockStoreStorageLaneAdapter(${adapterConfig(prefix, `${REVISION}-opfs-lane-quota-prep`)});
    const cleanupBefore=await adapter.store.cleanupForTest();
    const estimateAfterCleanup=await adapter.store.estimate();
    const persistedBefore=navigator.storage?.persisted ? await navigator.storage.persisted().catch(e=>({error:String(e?.message||e)})) : null;
    const snapshot=adapter.snapshot();
    const trace=rt.close();
    return JSON.stringify({project:'BrowserRT',revision:m.REVISION,version:m.VERSION,
      page:{location:location.href,readyState:document.readyState,crossOriginIsolated,isSecureContext,origin:location.origin},
      capabilities:m.detectCapabilities(globalThis),availableTierNames:m.availableCapabilityTierNames(m.detectCapabilities(globalThis)),
      prefix:${JSON.stringify(prefix)},cleanupBefore,estimateAfterCleanup,persistedBefore,snapshot,traceKinds:trace.map(e=>e.kind)});
  })()`;
}

function exprForLaneQuota(prefix, blockBytes, maxBlocks) {
  return `(async()=>{
    const m=await import('/src/browserrt.mjs?rev=${REVISION}&slice=opfs-lane-quota-run');
    const rt=await m.boot({telemetry:'browser-cdp',proof:'${REVISION}',browserCdpHarness:true,opfsAsyncBlockStoreProof:true,opfsStorageLaneAdapterProof:true,opfsLaneQuotaBackpressureProof:true,storageLaneProviderProof:true,crossLaneScheduler:true});
    const adapter=rt.opfsBlockStoreStorageLaneAdapter(${adapterConfig(prefix, `${REVISION}-opfs-lane-quota`)});
    const blockBytes=${Number(blockBytes)};
    const maxBlocks=${Number(maxBlocks)};
    const successful=[];
    let failure=null;
    let failedHashAbsentAfterRollback=null;
    const fillBlock=(index)=>{ const bytes=new Uint8Array(blockBytes); for (let j=0;j<bytes.length;j++) bytes[j]=(index*53+j*29+(j>>>7))&255; bytes[0]=index&255; bytes[1]=(index*19)&255; return bytes; };
    const estimateBefore=await adapter.store.estimate();
    for (let i=0;i<maxBlocks;i++) {
      const id='lane-quota-put-'+i;
      const scheduled=adapter.schedulePut(fillBlock(i),{id,priority:'user-visible',label:'lane-quota-block-'+i});
      if (!scheduled.accepted) { failure={index:i,stage:'schedule',scheduled}; break; }
      const drain=await adapter.drain({maxSteps:3});
      const row=drain.results.find(r=>r.opId===id);
      const laneAfter=adapter.snapshot().executor.scheduler.lanes.find(l=>l.id==='storage');
      if (row?.ok) {
        const result=adapter.result(id);
        const got=await adapter.store.get(result.ref);
        successful.push({index:i,scheduled,result:adapter.resultSummary(id),ref:result.ref,readDigest:'sha256:'+await m.digestBytesHex(got),laneAfter,drain:drain.results.map(r=>({opId:r.opId,op:r.op,ok:r.ok,lane:r.lane,dispatched:r.dispatched,error:r.error}))});
      } else {
        const err=row?.error || {message:'missing drain failure row'};
        const hash=err?.providerDetail?.context?.hash || err?.providerDetail?.hash || null;
        if (hash) failedHashAbsentAfterRollback=!(await adapter.store.has(hash).catch(e=>({error:String(e?.message||e)})));
        failure={index:i,stage:'drain',scheduled,row,laneAfter,failedHash:hash,failedHashAbsentAfterRollback};
        break;
      }
    }
    const afterFailureSnapshot=adapter.snapshot();
    const postQuotaReject=adapter.schedulePut(new Uint8Array(64),{id:'post-quota-reject',priority:'user-visible',label:'post-quota-reject'});
    const maintenanceEstimate=adapter.scheduleEstimate({id:'maintenance-estimate-after-quota',fallbackLanes:['maintenance'],priority:'background'});
    const maintenanceCleanup=adapter.scheduleCleanupForTest({id:'maintenance-cleanup-after-quota'});
    const maintenanceDrain=await adapter.drain({maxSteps:8});
    const recoveryLane=adapter.markHealthy('storage','quota-cleanup-complete');
    const recoveredWrite=adapter.schedulePut(new Uint8Array(1024),{id:'post-cleanup-small-put',priority:'user-visible',label:'post-cleanup-small-put'});
    const recoveryDrain=await adapter.drain({maxSteps:4});
    const recoveredResult=adapter.resultSummary('post-cleanup-small-put');
    const finalCleanupScheduled=adapter.scheduleCleanupForTest({id:'final-cleanup-after-recovered-write'});
    const finalCleanupDrain=await adapter.drain({maxSteps:4});
    const estimateAfter=await adapter.store.estimate().catch(e=>({error:String(e?.message||e)}));
    const finalSnapshot=adapter.snapshot();
    const validation=m.validateOpfsStorageLaneAdapterSnapshot(finalSnapshot);
    const trace=rt.close();
    return JSON.stringify({project:'BrowserRT',revision:m.REVISION,version:m.VERSION,
      page:{location:location.href,readyState:document.readyState,crossOriginIsolated,isSecureContext,origin:location.origin},
      prefix:${JSON.stringify(prefix)},blockBytes,maxBlocks,estimateBefore,successful,failure,afterFailureSnapshot,postQuotaReject,maintenanceEstimate,maintenanceCleanup,
      maintenanceResults:{estimate:adapter.resultSummary('maintenance-estimate-after-quota'),cleanup:adapter.result('maintenance-cleanup-after-quota')},
      maintenanceDrain:maintenanceDrain.results.map(r=>({opId:r.opId,op:r.op,ok:r.ok,lane:r.lane,dispatched:r.dispatched,error:r.error})),
      recoveryLane,recoveredWrite,recoveryDrain:recoveryDrain.results.map(r=>({opId:r.opId,op:r.op,ok:r.ok,lane:r.lane,dispatched:r.dispatched,error:r.error})),recoveredResult,
      finalCleanupScheduled,finalCleanupDrain:finalCleanupDrain.results.map(r=>({opId:r.opId,op:r.op,ok:r.ok,lane:r.lane,dispatched:r.dispatched,error:r.error})),
      estimateAfter,finalSnapshot,validation,
      traceKinds:trace.map(e=>e.kind),
      normalizedTrace:trace.map(e=>({kind:e.kind,op:e.op,opId:e.opId,lane:e.lane,provider:e.provider,store:e.store,prefix:e.prefix,digest:e.digest,bytes:e.bytes,duplicate:e.duplicate,deleted:e.deleted,disposition:e.disposition,reason:e.reason,code:e.code,storageDisposition:e.storageDisposition,error:e.error,routeReason:e.routeReason})).filter(e=>e.kind)});
  })()`;
}

export async function runProbe(options = {}) {
  const prefix = options.prefix || `browserrt/${REVISION}/opfs-lane-quota-backpressure-proof`;
  const blockBytes = Number(options.blockBytes || 256 * 1024);
  const maxBlocks = Number(options.maxBlocks || 10);
  const requestedQuotaBytes = Number(options.quotaBytes || 768 * 1024);
  if (!Number.isFinite(blockBytes) || blockBytes < 64 * 1024) throw new Error('blockBytes must be at least 64 KiB');
  if (!Number.isFinite(maxBlocks) || maxBlocks < 3) throw new Error('maxBlocks must be at least 3');
  if (!Number.isFinite(requestedQuotaBytes) || requestedQuotaBytes < blockBytes * 2) throw new Error('quotaBytes must be at least two block writes');

  let quotaReset = null;
  const { result: observed, harness } = await runManagedBrowserPage({
    timeoutMs: options.timeoutMs,
    chromium: options.chromium,
    relaxPolicy: options.relaxPolicy,
    pagePath: '/opfs-lane-quota-backpressure-probe.html',
    pageTitle: 'BrowserRT OPFS lane quota backpressure probe',
    profilePrefix: 'browserrt-opfs-lane-quota-cdp-',
    stderrTerms: ['opfs', 'file', 'storage', 'quota', 'lane']
  }, async ({ cdp, evalJson, pageUrl, mark, timeoutMs }) => {
    const origin = new URL(pageUrl).origin;
    const prepStart = performance.now();
    const prep = await evalJson(exprForPrep(prefix), timeoutMs);
    mark('browser-opfs-lane-quota-prep-cleanup', prepStart);

    const cdpBaseline = await getStorageUsageAndQuota(cdp, origin, timeoutMs);
    const quotaBytes = Math.max(requestedQuotaBytes, Math.ceil((cdpBaseline?.usage || 0) + requestedQuotaBytes));
    const overrideStart = performance.now();
    const quotaOverride = await overrideStorageQuotaForOrigin(cdp, { origin, quotaSize: quotaBytes }, timeoutMs);
    mark('cdp-storage-quota-override', overrideStart);

    const runStart = performance.now();
    const lane = await evalJson(exprForLaneQuota(prefix, blockBytes, maxBlocks), timeoutMs);
    mark('browser-opfs-lane-quota-write-backpressure-cleanup', runStart);
    const cdpAfterLane = await getStorageUsageAndQuota(cdp, origin, timeoutMs);

    const resetStart = performance.now();
    quotaReset = await resetStorageQuotaOverrideForOrigin(cdp, origin, timeoutMs);
    mark('cdp-storage-quota-reset', resetStart);
    return { pageUrl, origin, prefix, blockBytes, maxBlocks, quotaBytes, prep, cdpBaseline, quotaOverride, lane, cdpAfterLane, quotaReset };
  });

  const { prep, lane } = observed;
  assert.equal(prep.project, 'BrowserRT');
  assert.equal(prep.revision, REVISION);
  assert.equal(prep.version, VERSION);
  assert.equal(prep.page.crossOriginIsolated, true);
  assert.equal(prep.capabilities.environment, 'browser-window');
  assert.equal(prep.capabilities.opfs, true);
  assert.equal(observed.quotaOverride.after.overrideActive, true);
  assert.equal(observed.quotaOverride.after.quota, observed.quotaBytes);
  assert.equal(lane.project, 'BrowserRT');
  assert.equal(lane.revision, REVISION);
  assert.equal(lane.validation.ok, true);
  assert.ok(lane.successful.length >= 1, 'lane quota proof must write at least one block before rejection');
  assert.ok(lane.failure, 'lane quota proof must observe an adapter failure under CDP quota override');
  assert.equal(lane.failure.stage, 'drain');
  assert.equal(lane.failure.row?.ok, false);
  assert.equal(lane.failure.row?.error?.code, 'BRT_OPFS_QUOTA_EXCEEDED');
  assert.equal(lane.failure.row?.error?.storageDisposition, 'BRT_OPFS_QUOTA_EXCEEDED');
  assert.equal(lane.failure.row?.error?.providerDetail?.rollback?.attempted, true);
  assert.equal(lane.failure.failedHashAbsentAfterRollback, true);
  assert.equal(lane.failure.laneAfter?.healthy, false);
  assert.equal(lane.failure.laneAfter?.healthReason, 'BRT_OPFS_QUOTA_EXCEEDED');
  assert.equal(lane.afterFailureSnapshot.executor.stats.laneHealthFailures, 1);
  assert.equal(lane.afterFailureSnapshot.store.stats.quotaRejects, 1);
  assert.equal(lane.afterFailureSnapshot.store.stats.rollbackAttempts, 1);
  assert.equal(lane.postQuotaReject.accepted, false);
  assert.equal(lane.postQuotaReject.scheduler.disposition, 'rejected-lane-unhealthy');
  assert.equal(lane.postQuotaReject.scheduler.noMutation, true);
  assert.equal(lane.maintenanceEstimate.accepted, true);
  assert.equal(lane.maintenanceEstimate.scheduler.disposition, 'accepted-routed');
  assert.equal(lane.maintenanceEstimate.scheduler.lane, 'maintenance');
  assert.equal(lane.maintenanceCleanup.accepted, true);
  assert.equal(lane.maintenanceResults.cleanup, true);
  assert.equal(lane.recoveryLane.healthy, true);
  assert.equal(lane.recoveredWrite.accepted, true);
  assert.equal(lane.recoveredResult.duplicate, false);
  assert.equal(lane.finalCleanupScheduled.accepted, true);
  assert.equal(observed.cdpAfterLane.overrideActive, true);
  assert.equal(observed.quotaReset.after.overrideActive, false);
  assert.equal(quotaReset.after.overrideActive, false);
  const allKinds = [...prep.traceKinds, ...lane.traceKinds];
  for (const kind of ['runtime:boot','object:opfs-storage-lane-adapter-ref','storage:opfs-block-put','storage:opfs-block-put-error','storage:opfs-block-put-rollback','storage-lane:provider-unhealthy','crosslane:lane-unhealthy','crosslane:reject','crosslane:routed-enqueue','storage:opfs-block-cleanup','crosslane:lane-healthy','runtime:close']) {
    assert.ok(allKinds.includes(kind), `missing OPFS lane quota trace kind ${kind}`);
  }

  return {
    project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1,
    probe_id: `${REVISION}-browser-opfs-lane-quota-backpressure-proof`, status: 'passed', generatedAt: new Date().toISOString(),
    purpose: 'Managed Chromium/CDP proof that a real OPFS quota rejection propagates through the storage-lane adapter: the provider error is classified, failed block rollback is attempted, the storage lane is marked unhealthy, follow-on writes reject without mutation, maintenance fallback can cleanup, and explicit recovery permits a small write under the same quota override.',
    observations: observed,
    harness,
    claimsChecked: [
      'CDP quota override activates for the probe origin',
      'OPFS scheduled through BlockStoreLaneAdapter reaches a real BRT_OPFS_QUOTA_EXCEEDED write failure',
      'failed OPFS put attempts best-effort rollback and the failed content hash is absent afterward',
      'StorageLaneExecutor treats BRT_OPFS_QUOTA_EXCEEDED as a provider-health failure',
      'follow-on storage writes reject without queue mutation while the storage lane is unhealthy',
      'maintenance fallback routing remains usable for estimate/cleanup',
      'explicit recovery marks the storage lane healthy and permits a subsequent small write',
      'the CDP quota override is reset before teardown'
    ],
    nonClaims: [
      'Chromium-in-cloudtainer CDP quota-override proof only, not cross-browser quota conformance.',
      'This is a simulated origin quota boundary, not organic low-disk eviction pressure.',
      'Best-effort failed-put rollback is tested for this quota slice; it is not an fsync, crash, or power-loss guarantee.',
      'Recovery is explicit/manual after cleanup; no automatic browser storage reclamation or retry policy claim.',
      'Not a throughput, latency, scheduler-performance, or production capacity benchmark.',
      'Temporary managed-policy relaxation is local to this command and restored during teardown.'
    ]
  };
}

const argv = process.argv.slice(2);
const out = argValue(argv, '--json', DEFAULT_OUT);
const timeoutMs = Number(argValue(argv, '--timeout-ms', '48000'));
const chromium = argValue(argv, '--chromium', null);
const prefix = argValue(argv, '--prefix', null);
const blockBytes = Number(argValue(argv, '--block-bytes', String(256 * 1024)));
const quotaBytes = Number(argValue(argv, '--quota-bytes', String(768 * 1024)));
const maxBlocks = Number(argValue(argv, '--max-blocks', '10'));
const relaxPolicy = !hasFlag(argv, '--no-policy-relaxation');

try {
  const report = await runProbe({ timeoutMs, chromium, prefix, relaxPolicy, blockBytes, quotaBytes, maxBlocks });
  if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); console.log(out); }
  else console.log(JSON.stringify(report, null, 2));
} catch (error) {
  const report = { project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1, probe_id: `${REVISION}-browser-opfs-lane-quota-backpressure-proof`, status: 'failed', generatedAt: new Date().toISOString(), error: { name: error?.name || 'Error', message: error?.message || String(error), stack: error?.stack }, nonClaims: ['Failed browser OPFS lane quota/backpressure probe is not silently skipped; keep it outside broad release and debug by explicit id.'] };
  if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); console.error(out); }
  console.error(`[browser_opfs_lane_quota_backpressure_probe] FAIL: ${error?.stack || error}`);
  process.exitCode = 1;
}
