#!/usr/bin/env node
import assert from 'node:assert/strict';
import { mkdir, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import { performance } from 'node:perf_hooks';
import { REVISION, VERSION } from '../src/browserrt.mjs';
import { runManagedBrowserPage } from './browser_cdp_fixture.mjs';

const DEFAULT_OUT = `artifacts/validation/REV${REVISION.slice(3)}-BROWSER-OPFS-SYNC-WORKER-PROBE.json`;
const argValue = (argv, flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };
const hasFlag = (argv, flag) => argv.includes(flag);

export async function runProbe(options = {}) {
  const { result: observed, harness } = await runManagedBrowserPage({
    timeoutMs: options.timeoutMs,
    chromium: options.chromium,
    relaxPolicy: options.relaxPolicy,
    pagePath: '/opfs-sync-worker-probe.html',
    pageTitle: 'BrowserRT OPFS sync worker probe',
    profilePrefix: 'browserrt-opfs-sync-cdp-',
    stderrTerms: ['opfs', 'sync', 'access']
  }, async ({ evalJson, pageUrl, mark, timeoutMs }) => {
    const proofStart = performance.now();
    const expr = `(async()=>{
      const m=await import('/src/browserrt.mjs?rev=${REVISION}&slice=browser-opfs-sync-worker');
      const rt=await m.boot({telemetry:'browser-cdp',proof:'${REVISION}',browserCdpHarness:true,browserOpfsSyncWorkerProbe:true,opfsSyncWorkerProbe:true});
      const payload='BrowserRT ${REVISION} OPFS sync access handle worker proof :: '+new Array(11).fill('sync').join('-');
      const path='browserrt/${REVISION}/opfs-sync-worker-proof.bin';
      const bytes=new TextEncoder().encode(payload);
      const transfer=rt.transferObject(bytes.buffer,{id:'transfer:${REVISION}:opfs-sync-worker-payload',label:'opfs-sync-worker-payload'});
      const envelope=m.createEnvelope('opfs-sync-write-read',{lane:'storage',priority:'user-visible',payloadRef:transfer.ref});
      const workerUrl='/src/browser-opfs-sync-worker.mjs?rev=${REVISION}&slice=browser-opfs-sync-worker';
      rt.trace.emit('worker:opfs-sync-spawn',{workerUrl});
      const worker=new Worker(workerUrl,{type:'module',name:'browserrt-opfs-sync-worker'});
      const waitMessage=(predicate,ms=9000)=>new Promise((resolve,reject)=>{
        const timer=setTimeout(()=>{worker.removeEventListener('message',onMessage);reject(new Error('timeout waiting for OPFS sync worker message'));},ms);
        const onMessage=(event)=>{
          if(predicate(event.data)){
            clearTimeout(timer);
            worker.removeEventListener('message',onMessage);
            resolve(event.data);
          }
        };
        worker.addEventListener('message',onMessage);
        worker.addEventListener('error',(event)=>{clearTimeout(timer);reject(event.error||new Error(event.message||'worker error'));},{once:true});
      });
      const ready=await waitMessage((m)=>m&&m.type==='opfs-sync:ready');
      rt.trace.emit('worker:opfs-sync-ready',{backend:ready.detail?.backend});
      worker.postMessage({type:'opfs-sync:write-read',id:'call:${REVISION}:opfs-sync-worker',path,buffer:transfer.buffer,cleanup:true,envelope},transfer.transferList);
      const detachedAfter=transfer.buffer.byteLength===0;
      rt.trace.emit('storage:opfs-sync-worker-call',{path,detachedAfter,payloadBytes:transfer.ref.bytes});
      const response=await waitMessage((m)=>m&&m.id==='call:${REVISION}:opfs-sync-worker');
      if(response.type==='opfs-sync:error') throw new Error(response.error?.message||'OPFS sync worker error');
      const result=response.result;
      const explicitRef=rt.opfsObjectRef(path,{id:'opfs:${REVISION}:sync-worker-explicit-ref',bytes:result.bytesRead,backend:'opfs-sync-access-handle',ownership:'origin-private-worker-exclusive'});
      rt.trace.emit('storage:opfs-sync-worker-result',{path,bytesWritten:result.bytesWritten,bytesRead:result.bytesRead,same:result.same,backend:result.ref?.backend});
      worker.terminate();
      rt.trace.emit('worker:opfs-sync-terminate',{reason:'proof-complete'});
      const closeTrace=rt.close();
      const caps=m.detectCapabilities(globalThis);
      let estimate=null;
      if(navigator.storage?.estimate){
        const e=await navigator.storage.estimate();
        estimate={quota:typeof e.quota==='number'?e.quota:null,usage:typeof e.usage==='number'?e.usage:null,usageDetails:e.usageDetails||null};
      }
      return JSON.stringify({
        project:'BrowserRT',revision:m.REVISION,version:m.VERSION,
        page:{location:location.href,readyState:document.readyState,crossOriginIsolated,isSecureContext},
        capabilities:caps,availableTierNames:m.availableCapabilityTierNames(caps),
        workerReady:ready,
        syncWorkerProof:{
          path,
          detachedAfter,
          responseType:response.type,
          envelopeMagic:response.envelope?.magic,
          envelopeOp:response.envelope?.op,
          methods:result.methods,
          constructorTypes:result.constructorTypes,
          bytesWritten:result.bytesWritten,
          bytesRead:result.bytesRead,
          size:result.size,
          same:result.same,
          digest:result.digest,
          refKind:result.ref?.kind,
          refBackend:result.ref?.backend,
          refOwnership:result.ref?.ownership,
          explicitRefKind:explicitRef.kind,
          explicitRefBackend:explicitRef.backend,
          cleanup:result.cleanup,
          closed:result.closed,
          workerScope:result.workerScope,
          estimate
        },
        traceKinds:closeTrace.map(e=>e.kind),
        normalizedTrace:closeTrace.map(e=>({kind:e.kind,path:e.path,bytesWritten:e.bytesWritten,bytesRead:e.bytesRead,same:e.same,backend:e.backend,detachedAfter:e.detachedAfter,workerUrl:e.workerUrl,reason:e.reason})).filter(e=>e.kind)
      });
    })()`;
    const out = await evalJson(expr, timeoutMs);
    mark('browser-opfs-sync-worker-eval', proofStart);
    out._pageUrl = pageUrl;
    return out;
  });
  assert.equal(observed.project, 'BrowserRT');
  assert.equal(observed.revision, REVISION);
  assert.equal(observed.version, VERSION);
  assert.equal(observed.page.location, observed._pageUrl);
  assert.equal(observed.page.crossOriginIsolated, true);
  assert.equal(observed.capabilities.environment, 'browser-window');
  assert.equal(observed.syncWorkerProof.detachedAfter, true);
  assert.equal(observed.syncWorkerProof.envelopeMagic, 'BRT1');
  assert.equal(observed.syncWorkerProof.envelopeOp, 'opfs-sync-write-read');
  assert.equal(observed.syncWorkerProof.same, true);
  assert.equal(observed.syncWorkerProof.bytesWritten, observed.syncWorkerProof.bytesRead);
  assert.ok(observed.syncWorkerProof.bytesRead > 50);
  assert.equal(observed.syncWorkerProof.refKind, 'opfs');
  assert.equal(observed.syncWorkerProof.refBackend, 'opfs-sync-access-handle');
  assert.equal(observed.syncWorkerProof.explicitRefKind, 'opfs');
  assert.equal(observed.syncWorkerProof.explicitRefBackend, 'opfs-sync-access-handle');
  assert.equal(observed.syncWorkerProof.workerScope, true);
  assert.equal(observed.syncWorkerProof.closed, true);
  for (const method of ['read', 'write', 'truncate', 'flush', 'getSize', 'close']) {
    assert.equal(observed.syncWorkerProof.methods[method], 'function', `sync access handle missing ${method}`);
  }
  for (const kind of ['runtime:boot', 'object:transfer-ref', 'worker:opfs-sync-spawn', 'worker:opfs-sync-ready', 'storage:opfs-sync-worker-call', 'object:opfs-ref', 'storage:opfs-sync-worker-result', 'worker:opfs-sync-terminate', 'runtime:close']) {
    assert.ok(observed.traceKinds.includes(kind), `missing OPFS sync worker trace kind ${kind}`);
  }
  return {
    project: 'BrowserRT',
    revision: REVISION,
    version: VERSION,
    schema: 1,
    probe_id: `${REVISION}-browser-opfs-sync-worker-probe`,
    status: 'passed',
    generatedAt: new Date().toISOString(),
    purpose: 'One-shot browser OPFS sync access handle proof inside a dedicated module Worker using the shared browser fixture: transfer payload, createSyncAccessHandle, synchronous write/read/flush/close, OPFS object-ref trace evidence, teardown.',
    chromium: { executable: harness.chromiumExecutable, targetUrl: observed._pageUrl },
    policyRelaxation: harness.policyRelaxation,
    observations: observed,
    server: harness.server,
    cdp: harness.cdp,
    timings: harness.timings,
    durationMs: harness.durationMs,
    chromeStderrSummary: harness.chromeStderrSummary,
    chromeStdoutBytes: harness.chromeStdoutBytes,
    nonClaims: [
      'Chromium-in-cloudtainer OPFS sync access handle proof only, not cross-browser conformance.',
      'Proves a one-file dedicated-worker sync write/read path, not a journaled block store.',
      'Not a durability, quota-pressure, compaction, crash-recovery, or multi-tab concurrency proof.',
      'Not a performance benchmark.',
      'Temporary managed-policy relaxation is local to this command and restored during teardown.'
    ]
  };
}

const argv = process.argv.slice(2);
const out = argValue(argv, '--json', DEFAULT_OUT);
const timeoutMs = Number(argValue(argv, '--timeout-ms', '15000'));
const chromium = argValue(argv, '--chromium', null);
const relaxPolicy = !hasFlag(argv, '--no-policy-relaxation');

try {
  const report = await runProbe({ timeoutMs, chromium, relaxPolicy });
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
    probe_id: `${REVISION}-browser-opfs-sync-worker-probe`,
    status: 'failed',
    generatedAt: new Date().toISOString(),
    error: { name: error?.name || 'Error', message: error?.message || String(error), stack: error?.stack },
    nonClaims: ['Failed browser OPFS sync worker probe is not silently skipped. Run this task by id to debug before broad release reruns.']
  };
  if (out) {
    await mkdir(dirname(out), { recursive: true });
    await writeFile(out, JSON.stringify(report, null, 2) + '\n');
    console.error(out);
  }
  console.error(`[browser_opfs_sync_worker_probe] FAIL: ${error?.stack || error}`);
  process.exitCode = 1;
}
