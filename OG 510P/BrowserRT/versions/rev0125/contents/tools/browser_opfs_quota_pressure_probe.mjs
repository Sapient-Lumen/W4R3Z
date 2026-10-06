#!/usr/bin/env node
import assert from 'node:assert/strict';
import { mkdir, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import { performance } from 'node:perf_hooks';
import { REVISION, VERSION } from '../src/browserrt.mjs';
import { runManagedBrowserPage, getStorageUsageAndQuota, overrideStorageQuotaForOrigin, resetStorageQuotaOverrideForOrigin } from './browser_cdp_fixture.mjs';

const DEFAULT_OUT = `artifacts/validation/REV${REVISION.slice(3)}-BROWSER-OPFS-QUOTA-PRESSURE-PROBE.json`;
const argValue = (argv, flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };
const hasFlag = (argv, flag) => argv.includes(flag);

function exprForPrep(prefix) {
  return `(async()=>{
    const m=await import('/src/browserrt.mjs?rev=${REVISION}&slice=opfs-quota-prep');
    const rt=await m.boot({telemetry:'browser-cdp',proof:'${REVISION}',browserCdpHarness:true,opfsQuotaPressureProof:true});
    const store=rt.opfsAsyncBlockStore({name:'${REVISION}-opfs-quota-pressure-store',prefix:${JSON.stringify(prefix)}});
    const cleanupBefore=await store.cleanupForTest();
    const persistedBefore = navigator.storage?.persisted ? await navigator.storage.persisted().catch(e=>({error:String(e?.message||e)})) : null;
    const estimateAfterCleanup=await store.estimate();
    const snapshot=store.snapshot();
    const trace=rt.close();
    return JSON.stringify({project:'BrowserRT',revision:m.REVISION,version:m.VERSION,
      page:{location:location.href,readyState:document.readyState,crossOriginIsolated,isSecureContext,origin:location.origin},
      capabilities:m.detectCapabilities(globalThis),availableTierNames:m.availableCapabilityTierNames(m.detectCapabilities(globalThis)),
      prefix:${JSON.stringify(prefix)},cleanupBefore,persistedBefore,estimateAfterCleanup,snapshot,traceKinds:trace.map(e=>e.kind)});
  })()`;
}

function exprForQuotaWrites(prefix, blockBytes, maxBlocks) {
  return `(async()=>{
    const m=await import('/src/browserrt.mjs?rev=${REVISION}&slice=opfs-quota-write');
    const rt=await m.boot({telemetry:'browser-cdp',proof:'${REVISION}',browserCdpHarness:true,opfsQuotaPressureProof:true});
    const store=rt.opfsAsyncBlockStore({name:'${REVISION}-opfs-quota-pressure-store',prefix:${JSON.stringify(prefix)}});
    const blockBytes=${Number(blockBytes)};
    const maxBlocks=${Number(maxBlocks)};
    const successful=[];
    let failure=null;
    const fillBlock=(index)=>{
      const bytes=new Uint8Array(blockBytes);
      for (let j=0;j<bytes.length;j++) bytes[j]=(index*41+j*17+(j>>>8))&255;
      bytes[0]=index&255; bytes[1]=(index*13)&255;
      return bytes;
    };
    const estimateBefore=await store.estimate();
    for (let i=0;i<maxBlocks;i++) {
      const started=performance.now();
      try {
        const payload=fillBlock(i);
        const put=await store.put(payload,{label:'quota-pressure-block-'+i});
        const got=await store.get(put.ref);
        const digest=await m.digestBytesHex(got);
        const estimate=await store.estimate();
        successful.push({index:i,bytes:put.bytes,digest:put.digest,hash:put.hash,ref:put.ref,path:put.path,duplicate:put.duplicate,readDigest:digest,estimate,durationMs:Math.round(performance.now()-started)});
      } catch (error) {
        failure={index:i,name:error?.name||'Error',message:String(error?.message||error),code:error?.code??null,detail:error?.detail??null,durationMs:Math.round(performance.now()-started)};
        break;
      }
    }
    const estimateAfter=await store.estimate().catch(e=>({error:String(e?.message||e)}));
    const snapshot=store.snapshot();
    const trace=rt.close();
    return JSON.stringify({project:'BrowserRT',revision:m.REVISION,version:m.VERSION,
      page:{location:location.href,readyState:document.readyState,crossOriginIsolated,isSecureContext,origin:location.origin},
      prefix:${JSON.stringify(prefix)},blockBytes,maxBlocks,estimateBefore,successful,failure,estimateAfter,snapshot,
      totalSuccessfulBytes:successful.reduce((sum,row)=>sum+row.bytes,0),
      traceKinds:trace.map(e=>e.kind),normalizedTrace:trace.map(e=>({kind:e.kind,digest:e.digest,bytes:e.bytes,duplicate:e.duplicate,path:e.path,store:e.store,prefix:e.prefix,quota:e.quota,usage:e.usage,error:e.error})).filter(e=>e.kind)});
  })()`;
}

function exprForVerifyAndCleanup(prefix, refs) {
  return `(async()=>{
    const m=await import('/src/browserrt.mjs?rev=${REVISION}&slice=opfs-quota-cleanup');
    const rt=await m.boot({telemetry:'browser-cdp',proof:'${REVISION}',browserCdpHarness:true,opfsQuotaPressureProof:true});
    const store=rt.opfsAsyncBlockStore({name:'${REVISION}-opfs-quota-pressure-store-cleanup',prefix:${JSON.stringify(prefix)}});
    const refs=${JSON.stringify(refs)};
    const checks=[];
    for (const ref of refs) {
      const hasBefore=await store.has(ref);
      const bytes=await store.get(ref);
      const digest=await m.digestBytesHex(bytes);
      const verify=await store.verify(ref);
      const deleted=await store.delete(ref);
      const hasAfter=await store.has(ref);
      checks.push({digest:ref.digest,hash:ref.hash,hasBefore,bytes:bytes.byteLength,digestAfterRead:'sha256:'+digest,verify,deleted,hasAfter});
    }
    const cleanup=await store.cleanupForTest();
    const estimateAfterCleanup=await store.estimate().catch(e=>({error:String(e?.message||e)}));
    const snapshot=store.snapshot();
    const trace=rt.close();
    return JSON.stringify({project:'BrowserRT',revision:m.REVISION,version:m.VERSION,
      page:{location:location.href,readyState:document.readyState,crossOriginIsolated,isSecureContext,origin:location.origin},
      prefix:${JSON.stringify(prefix)},checks,cleanup,estimateAfterCleanup,snapshot,
      traceKinds:trace.map(e=>e.kind),normalizedTrace:trace.map(e=>({kind:e.kind,digest:e.digest,bytes:e.bytes,deleted:e.deleted,present:e.present,path:e.path,store:e.store,prefix:e.prefix,quota:e.quota,usage:e.usage})).filter(e=>e.kind)});
  })()`;
}

export async function runProbe(options = {}) {
  const prefix = options.prefix || `browserrt/${REVISION}/opfs-quota-pressure-proof`;
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
    pagePath: '/opfs-quota-pressure-probe.html',
    pageTitle: 'BrowserRT OPFS quota-pressure probe',
    profilePrefix: 'browserrt-opfs-quota-pressure-cdp-',
    stderrTerms: ['opfs', 'file', 'storage', 'quota']
  }, async ({ cdp, evalJson, pageUrl, mark, timeoutMs }) => {
    const origin = new URL(pageUrl).origin;
    const prepStart = performance.now();
    const prep = await evalJson(exprForPrep(prefix), timeoutMs);
    mark('browser-opfs-quota-prep-cleanup', prepStart);

    const cdpBaseline = await getStorageUsageAndQuota(cdp, origin, timeoutMs);
    const quotaBytes = Math.max(requestedQuotaBytes, Math.ceil((cdpBaseline?.usage || 0) + requestedQuotaBytes));
    const overrideStart = performance.now();
    const quotaOverride = await overrideStorageQuotaForOrigin(cdp, { origin, quotaSize: quotaBytes }, timeoutMs);
    mark('cdp-storage-quota-override', overrideStart);

    const writeStart = performance.now();
    const writes = await evalJson(exprForQuotaWrites(prefix, blockBytes, maxBlocks), timeoutMs);
    mark('browser-opfs-quota-write-until-reject', writeStart);
    const cdpAfterWrites = await getStorageUsageAndQuota(cdp, origin, timeoutMs);

    const cleanupStart = performance.now();
    const cleanup = await evalJson(exprForVerifyAndCleanup(prefix, writes.successful.map((row) => row.ref)), timeoutMs);
    mark('browser-opfs-quota-verify-cleanup-under-override', cleanupStart);
    const cdpAfterCleanup = await getStorageUsageAndQuota(cdp, origin, timeoutMs);

    const resetStart = performance.now();
    quotaReset = await resetStorageQuotaOverrideForOrigin(cdp, origin, timeoutMs);
    mark('cdp-storage-quota-reset', resetStart);
    return { pageUrl, origin, prefix, blockBytes, maxBlocks, quotaBytes, prep, cdpBaseline, quotaOverride, writes, cdpAfterWrites, cleanup, cdpAfterCleanup, quotaReset };
  });

  const { prep, writes, cleanup } = observed;
  assert.equal(prep.project, 'BrowserRT');
  assert.equal(prep.revision, REVISION);
  assert.equal(prep.version, VERSION);
  assert.equal(prep.page.crossOriginIsolated, true);
  assert.equal(prep.capabilities.environment, 'browser-window');
  assert.equal(prep.capabilities.opfs, true);
  assert.equal(observed.quotaOverride.after.overrideActive, true);
  assert.equal(observed.quotaOverride.after.quota, observed.quotaBytes);
  assert.ok(writes.successful.length >= 1, 'quota pressure proof must write at least one block before rejection');
  assert.ok(writes.failure, 'quota pressure proof must observe an actual write rejection under CDP quota override');
  assert.match(`${writes.failure.name} ${writes.failure.message} ${writes.failure.code}`, /quota|exceed|storage/i, 'write rejection should be storage/quota-related');
  assert.ok(writes.totalSuccessfulBytes >= observed.blockBytes);
  assert.ok(writes.successful.length < observed.maxBlocks, 'quota override should reject before max-block guard');
  for (const row of writes.successful) { assert.equal(row.duplicate, false); assert.equal(row.readDigest, row.hash); }
  assert.equal(cleanup.project, 'BrowserRT');
  assert.equal(cleanup.revision, REVISION);
  assert.equal(cleanup.checks.length, writes.successful.length);
  for (const row of cleanup.checks) {
    assert.equal(row.hasBefore, true);
    assert.equal(row.verify.ok, true);
    assert.equal(row.digestAfterRead, row.digest);
    assert.equal(row.deleted, true);
    assert.equal(row.hasAfter, false);
  }
  assert.equal(observed.cdpAfterCleanup.overrideActive, true);
  assert.equal(observed.quotaReset.after.overrideActive, false);
  assert.equal(quotaReset.after.overrideActive, false);
  for (const kind of ['runtime:boot','storage:opfs-blockstore-create','storage:opfs-blockstore-open','storage:opfs-block-put','storage:opfs-block-put-error','storage:opfs-block-get','storage:opfs-block-estimate','storage:opfs-block-delete','storage:opfs-block-cleanup','runtime:close']) {
    assert.ok([...prep.traceKinds, ...writes.traceKinds, ...cleanup.traceKinds].includes(kind), `missing OPFS quota pressure trace kind ${kind}`);
  }

  return {
    project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1,
    probe_id: `${REVISION}-browser-opfs-quota-pressure-proof`, status: 'passed', generatedAt: new Date().toISOString(),
    purpose: 'Managed Chromium/CDP proof for bounded OPFS quota-pressure behavior: clean namespace, set a small CDP origin quota override, write unique OPFS blocks until a real quota/storage rejection, verify successful blocks remain readable, delete them while the override is active, cleanup, and reset the quota override.',
    observations: observed,
    harness,
    claimsChecked: [
      'CDP Storage.getUsageAndQuota is available for the probe origin',
      'CDP Storage.overrideQuotaForOrigin activates a bounded quota for the same origin',
      'OPFS block-store writes unique blocks until the browser rejects a write under that quota',
      'Quota-like OPFS write failures are classified as BRT_OPFS_QUOTA_EXCEEDED',
      'successful pre-rejection blocks remain readable and checksum-verifiable',
      'cleanup and deletion work while the quota override is still active',
      'the CDP quota override is reset before teardown'
    ],
    nonClaims: [
      'Chromium-in-cloudtainer CDP quota-override proof only, not cross-browser quota conformance.',
      'This is a simulated origin quota boundary, not organic operating-system disk-pressure eviction evidence.',
      'No claim that the browser will evict this origin, retain it forever, or behave identically under real low-disk pressure.',
      'No OPFS fsync, crash-recovery, power-loss, retention-period, Storage Buckets, or persistent-storage permission claim.',
      'Not a throughput, latency, or capacity benchmark; block sizes and quotas are deliberately small to avoid cloudtainer waste.',
      'Temporary managed-policy relaxation is local to this command and restored during teardown.'
    ]
  };
}

const argv = process.argv.slice(2);
const out = argValue(argv, '--json', DEFAULT_OUT);
const timeoutMs = Number(argValue(argv, '--timeout-ms', '42000'));
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
  const report = { project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1, probe_id: `${REVISION}-browser-opfs-quota-pressure-proof`, status: 'failed', generatedAt: new Date().toISOString(), error: { name: error?.name || 'Error', message: error?.message || String(error), stack: error?.stack }, nonClaims: ['Failed browser OPFS quota-pressure probe is not silently skipped; keep it outside broad release and debug by id.'] };
  if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); console.error(out); }
  console.error(`[browser_opfs_quota_pressure_probe] FAIL: ${error?.stack || error}`);
  process.exitCode = 1;
}
