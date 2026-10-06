#!/usr/bin/env node
import assert from 'node:assert/strict';
import { mkdir, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import { performance } from 'node:perf_hooks';
import { REVISION, VERSION } from '../src/browserrt.mjs';
import { runManagedBrowserPage, sleep } from './browser_cdp_fixture.mjs';

const DEFAULT_OUT = `artifacts/validation/REV${REVISION.slice(3)}-BROWSER-OPFS-STORAGE-LANE-ADAPTER-PROBE.json`;
const argValue = (argv, flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };
const hasFlag = (argv, flag) => argv.includes(flag);

function exprForWrite(prefix) {
  return `(async()=>{
    const m=await import('/src/browserrt.mjs?rev=${REVISION}&slice=browser-opfs-storage-lane-write');
    const rt=await m.boot({telemetry:'browser-cdp',proof:'${REVISION}',browserCdpHarness:true,opfsAsyncBlockStoreProof:true,opfsStorageLaneAdapterProof:true,storageLaneProviderProof:true,crossLaneScheduler:true});
    const adapter=rt.opfsBlockStoreStorageLaneAdapter({label:'${REVISION}-opfs-storage-lane',prefix:${JSON.stringify(prefix)}});
    await adapter.store.cleanupForTest();
    const payloadA=new TextEncoder().encode('BrowserRT ${REVISION} OPFS storage-lane payload A :: '+new Array(9).fill('adapter').join('/'));
    const payloadB=new Uint8Array(Array.from({length:128},(_,i)=>(i*23+11)&255));
    const putA=adapter.schedulePut(payloadA,{id:'put-a',priority:'user-visible',label:'payload-a'});
    const putB=adapter.schedulePut(payloadB,{id:'put-b',priority:'background',label:'payload-b'});
    const drain1=await adapter.drain({maxSteps:8});
    const refA=adapter.result('put-a').ref;
    const refB=adapter.result('put-b').ref;
    const dupA=adapter.schedulePut(payloadA,{id:'dup-a',priority:'background',label:'payload-a-dup'});
    const estimate=adapter.scheduleEstimate({id:'estimate-a',priority:'background'});
    const drain2=await adapter.drain({maxSteps:8});
    const snapshot=adapter.snapshot();
    const validation=m.validateOpfsStorageLaneAdapterSnapshot(snapshot);
    const trace=rt.close();
    return JSON.stringify({
      project:'BrowserRT',revision:m.REVISION,version:m.VERSION,
      page:{location:location.href,readyState:document.readyState,crossOriginIsolated,isSecureContext},
      capabilities:m.detectCapabilities(globalThis),availableTierNames:m.availableCapabilityTierNames(m.detectCapabilities(globalThis)),
      prefix:${JSON.stringify(prefix)},
      accepted:{putA,putB,dupA,estimate},
      refs:{a:refA,b:refB},
      results:{putA:adapter.resultSummary('put-a'),putB:adapter.resultSummary('put-b'),dupA:adapter.resultSummary('dup-a'),estimate:adapter.resultSummary('estimate-a')},
      drain:{first:drain1.results.map(r=>({op:r.op,ok:r.ok,lane:r.lane,dispatched:r.dispatched})),second:drain2.results.map(r=>({op:r.op,ok:r.ok,lane:r.lane,dispatched:r.dispatched}))},
      snapshot,validation,
      traceKinds:trace.map(e=>e.kind),
      normalizedTrace:trace.map(e=>({kind:e.kind,op:e.op,opId:e.opId,lane:e.lane,provider:e.provider,store:e.store,prefix:e.prefix,digest:e.digest,bytes:e.bytes,duplicate:e.duplicate,disposition:e.disposition,reason:e.reason})).filter(e=>e.kind)
    });
  })()`;
}

function exprForReloadRead(prefix, refA, refB) {
  return `(async()=>{
    const m=await import('/src/browserrt.mjs?rev=${REVISION}&slice=browser-opfs-storage-lane-reload-read');
    const rt=await m.boot({telemetry:'browser-cdp',proof:'${REVISION}',browserCdpHarness:true,opfsAsyncBlockStoreProof:true,opfsStorageLaneAdapterProof:true,storageLaneProviderProof:true,crossLaneScheduler:true});
    const adapter=rt.opfsBlockStoreStorageLaneAdapter({label:'${REVISION}-opfs-storage-lane-reload',prefix:${JSON.stringify(prefix)}});
    const refA=${JSON.stringify(refA)};
    const refB=${JSON.stringify(refB)};
    const hasA=adapter.scheduleHas(refA,{id:'has-a'});
    const getA=adapter.scheduleGet(refA,{id:'get-a'});
    const verifyB=adapter.scheduleVerify(refB,{id:'verify-b'});
    const drainRead=await adapter.drain({maxSteps:8});
    const readA=adapter.result('get-a');
    adapter.markUnhealthy('storage','intentional-route-test');
    const routedEstimate=adapter.scheduleEstimate({id:'estimate-routed',fallbackLanes:['maintenance']});
    const drainRoute=await adapter.drain({maxSteps:4});
    adapter.markHealthy('storage','route-test-recovery');
    const deleteA=adapter.scheduleDelete(refA,{id:'delete-a'});
    const deleteB=adapter.scheduleDelete(refB,{id:'delete-b'});
    const drainDelete=await adapter.drain({maxSteps:8});
    const hasAfterA=adapter.scheduleHas(refA,{id:'has-after-a'});
    const hasAfterB=adapter.scheduleHas(refB,{id:'has-after-b'});
    const cleanup=adapter.scheduleCleanupForTest({id:'cleanup-proof'});
    const drainAfter=await adapter.drain({maxSteps:8});
    const snapshot=adapter.snapshot();
    const validation=m.validateOpfsStorageLaneAdapterSnapshot(snapshot);
    const trace=rt.close();
    return JSON.stringify({
      project:'BrowserRT',revision:m.REVISION,version:m.VERSION,
      page:{location:location.href,readyState:document.readyState,crossOriginIsolated,isSecureContext},
      prefix:${JSON.stringify(prefix)},
      accepted:{hasA,getA,verifyB,routedEstimate,deleteA,deleteB,hasAfterA,hasAfterB,cleanup},
      results:{hasA:adapter.result('has-a'),getADigest:await m.digestBytesHex(readA),getABytes:readA.byteLength,verifyB:adapter.result('verify-b'),routedEstimate:adapter.resultSummary('estimate-routed'),deleteA:adapter.result('delete-a'),deleteB:adapter.result('delete-b'),hasAfterA:adapter.result('has-after-a'),hasAfterB:adapter.result('has-after-b'),cleanup:adapter.result('cleanup-proof')},
      drain:{read:drainRead.results.map(r=>({op:r.op,ok:r.ok,lane:r.lane,dispatched:r.dispatched})),route:drainRoute.results.map(r=>({op:r.op,ok:r.ok,lane:r.lane,dispatched:r.dispatched})),del:drainDelete.results.map(r=>({op:r.op,ok:r.ok,lane:r.lane,dispatched:r.dispatched})),after:drainAfter.results.map(r=>({op:r.op,ok:r.ok,lane:r.lane,dispatched:r.dispatched}))},
      snapshot,validation,
      traceKinds:trace.map(e=>e.kind),
      normalizedTrace:trace.map(e=>({kind:e.kind,op:e.op,opId:e.opId,lane:e.lane,provider:e.provider,store:e.store,prefix:e.prefix,digest:e.digest,bytes:e.bytes,deleted:e.deleted,disposition:e.disposition,reason:e.reason,routeReason:e.routeReason})).filter(e=>e.kind)
    });
  })()`;
}

export async function runProbe(options = {}) {
  const prefix = options.prefix || `browserrt/${REVISION}/opfs-storage-lane-adapter-proof`;
  const { result: observed, harness } = await runManagedBrowserPage({
    timeoutMs: options.timeoutMs,
    chromium: options.chromium,
    relaxPolicy: options.relaxPolicy,
    pagePath: '/opfs-storage-lane-adapter-probe.html',
    pageTitle: 'BrowserRT OPFS storage-lane adapter probe',
    profilePrefix: 'browserrt-opfs-storage-lane-cdp-',
    stderrTerms: ['opfs','storage','lane','block']
  }, async ({ cdp, evalJson, pageUrl, mark, timeoutMs }) => {
    const writeStart = performance.now();
    const write = await evalJson(exprForWrite(prefix), timeoutMs);
    mark('browser-opfs-storage-lane-write-eval', writeStart);

    const reloadStart = performance.now();
    await cdp.send('Page.reload', {}, timeoutMs);
    const deadline = performance.now() + timeoutMs;
    let pageState = null;
    while (performance.now() < deadline) {
      await sleep(100);
      pageState = await evalJson('JSON.stringify({location:location.href,readyState:document.readyState,crossOriginIsolated,isSecureContext})', Math.min(1000, timeoutMs));
      if (pageState.location === pageUrl && pageState.readyState !== 'loading') break;
    }
    mark('browser-opfs-storage-lane-page-reload', reloadStart);
    assert.equal(pageState?.location, pageUrl);

    const readStart = performance.now();
    const read = await evalJson(exprForReloadRead(prefix, write.refs.a, write.refs.b), timeoutMs);
    mark('browser-opfs-storage-lane-reload-read-eval', readStart);
    return { pageUrl, write, read };
  });

  const write = observed.write;
  const read = observed.read;
  assert.equal(write.project, 'BrowserRT');
  assert.equal(write.revision, REVISION);
  assert.equal(write.version, VERSION);
  assert.equal(write.page.crossOriginIsolated, true);
  assert.equal(write.capabilities.opfs, true);
  assert.equal(write.validation.ok, true);
  assert.equal(write.accepted.putA.accepted, true);
  assert.equal(write.accepted.putB.accepted, true);
  assert.equal(write.accepted.dupA.accepted, true);
  assert.equal(write.results.putA.duplicate, false);
  assert.equal(write.results.putB.duplicate, false);
  assert.equal(write.results.dupA.duplicate, true);
  assert.equal(write.results.putA.digest, write.results.dupA.digest);
  assert.equal(read.page.crossOriginIsolated, true);
  assert.equal(read.validation.ok, true);
  assert.equal(read.results.hasA, true);
  assert.equal(read.results.getADigest, write.refs.a.hash);
  assert.equal(read.results.verifyB.ok, true);
  assert.equal(read.accepted.routedEstimate.accepted, true);
  assert.equal(read.accepted.routedEstimate.scheduler.disposition, 'accepted-routed');
  assert.equal(read.accepted.routedEstimate.scheduler.lane, 'maintenance');
  assert.equal(read.results.deleteA, true);
  assert.equal(read.results.deleteB, true);
  assert.equal(read.results.hasAfterA, false);
  assert.equal(read.results.hasAfterB, false);
  assert.equal(read.results.cleanup, true);
  const allKinds = [...write.traceKinds, ...read.traceKinds];
  for (const kind of ['runtime:boot','object:opfs-storage-lane-adapter-ref','block-store-lane:schedule','storage-lane:schedule','storage-lane:dispatch','block-store-lane:op-complete','storage-lane:complete','crosslane:routed-enqueue','storage:opfs-block-put','storage:opfs-block-get','storage:opfs-block-delete','runtime:close']) {
    assert.ok(allKinds.includes(kind), `missing OPFS storage-lane trace kind ${kind}`);
  }
  return {
    project: 'BrowserRT',
    revision: REVISION,
    version: VERSION,
    schema: 1,
    probe_id: `${REVISION}-browser-opfs-storage-lane-adapter-probe`,
    status: 'passed',
    generatedAt: new Date().toISOString(),
    purpose: 'One-shot browser proof that OpfsAsyncBlockStore operations can be scheduled through the storage-lane adapter and CrossLaneScheduler: put/get/has/verify/delete/estimate/cleanup, fallback routing, page-reload readback, trace evidence, and teardown.',
    chromium: { executable: harness.chromiumExecutable, targetUrl: observed.pageUrl },
    policyRelaxation: harness.policyRelaxation,
    observations: observed,
    server: harness.server,
    cdp: harness.cdp,
    timings: harness.timings,
    durationMs: harness.durationMs,
    chromeStderrSummary: harness.chromeStderrSummary,
    chromeStdoutBytes: harness.chromeStdoutBytes,
    nonClaims: [
      'Chromium-in-cloudtainer async OPFS storage-lane adapter proof only, not cross-browser conformance.',
      'Not an OPFS sync access handle, browser Worker, journal, crash-recovery, quota-pressure, compaction, multi-tab, or durability proof.',
      'Page-reload readback in one temporary Chromium profile is not a browser restart or crash recovery claim.',
      'Storage-lane scheduling evidence is functional/trace evidence, not throughput, latency, or production scheduler proof.',
      'Not a throughput, latency, scheduler-performance, or production scheduler claim.',
      'Temporary managed-policy relaxation is local to this command and restored during teardown.'
    ]
  };
}

const argv = process.argv.slice(2);
const out = argValue(argv, '--json', DEFAULT_OUT);
const timeoutMs = Number(argValue(argv, '--timeout-ms', '18000'));
const chromium = argValue(argv, '--chromium', null);
const prefix = argValue(argv, '--prefix', null);
const relaxPolicy = !hasFlag(argv, '--no-policy-relaxation');

try {
  const report = await runProbe({ timeoutMs, chromium, prefix, relaxPolicy });
  if (out) {
    await mkdir(dirname(out), { recursive: true });
    await writeFile(out, JSON.stringify(report, null, 2) + '\n');
    console.log(out);
  } else {
    console.log(JSON.stringify(report, null, 2));
  }
} catch (error) {
  const report = {
    project: 'BrowserRT',
    revision: REVISION,
    version: VERSION,
    schema: 1,
    probe_id: `${REVISION}-browser-opfs-storage-lane-adapter-probe`,
    status: 'failed',
    generatedAt: new Date().toISOString(),
    error: { name: error?.name || 'Error', message: error?.message || String(error), stack: error?.stack }
  };
  if (out) {
    await mkdir(dirname(out), { recursive: true });
    await writeFile(out, JSON.stringify(report, null, 2) + '\n');
  }
  throw error;
}
