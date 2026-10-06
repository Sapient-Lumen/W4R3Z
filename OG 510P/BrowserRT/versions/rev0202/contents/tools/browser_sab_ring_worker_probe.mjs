#!/usr/bin/env node
import assert from 'node:assert/strict';
import { mkdir, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import { performance } from 'node:perf_hooks';
import { REVISION, VERSION } from '../src/browserrt.mjs';
import { runManagedBrowserPage } from './browser_cdp_fixture.mjs';

// Manifest task: browser:sab-ring-worker-proof
const DEFAULT_OUT = `artifacts/validation/REV${REVISION.slice(3)}-BROWSER-SAB-RING-WORKER-PROBE.json`;
const argValue = (argv, flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };
const hasFlag = (argv, flag) => argv.includes(flag);

export async function runProbe(options = {}) {
  const { result: observed, harness } = await runManagedBrowserPage({
    timeoutMs: options.timeoutMs,
    chromium: options.chromium,
    relaxPolicy: options.relaxPolicy,
    pagePath: '/browser-sab-ring-worker-probe.html',
    pageTitle: 'BrowserRT browser SAB ring worker probe',
    profilePrefix: 'browserrt-sab-ring-cdp-',
    stderrTerms: ['sab', 'SharedArrayBuffer', 'Atomics']
  }, async ({ evalJson, pageUrl, mark, timeoutMs }) => {
    const proofStart = performance.now();
    const expr = `(async()=>{
      const sleep=(ms)=>new Promise((resolve)=>setTimeout(resolve,ms));
      const m=await import('/src/browserrt.mjs?rev=${REVISION}&slice=browser-sab-ring-worker');
      const rt=await m.boot({telemetry:'browser-cdp',proof:'${REVISION}',browserCdpHarness:true,browserSabRingWorkerProbe:true,sharedMemoryRingProbe:true});
      const caps=m.detectCapabilities(globalThis);
      if(!crossOriginIsolated) throw new Error('browser SAB ring proof requires crossOriginIsolated');
      if(typeof SharedArrayBuffer!=='function') throw new Error('SharedArrayBuffer unavailable in browser page');
      if(typeof Atomics!=='object') throw new Error('Atomics unavailable in browser page');
      const capacity=8;
      const messageCount=64;
      const ring=rt.sharedInt32Ring({capacity,label:'${REVISION}-browser-sab-ring'});
      const sharedRef=rt.objectRef('shared',{id:'shared:${REVISION}:browser-sab-ring',bytes:ring.sab.byteLength,ownership:'shared-browser-worker',backend:'SharedArrayBuffer'});
      for(let value=1;value<=capacity;value+=1){ if(!ring.tryPush(value)) throw new Error('failed to prefill ring value '+value); }
      const fullBeforeConsumer=ring.tryPush(999)===false;
      const byteLengthBefore=ring.sab.byteLength;
      const workerUrl='/src/browser-sab-ring-worker.mjs?rev=${REVISION}&slice=browser-sab-ring-worker';
      rt.trace.emit('worker:sab-ring-spawn',{workerUrl,capacity,messageCount});
      const worker=new Worker(workerUrl,{type:'module',name:'browserrt-sab-ring-worker'});
      const waitMessage=(predicate,ms=9000)=>new Promise((resolve,reject)=>{
        const timer=setTimeout(()=>{worker.removeEventListener('message',onMessage);reject(new Error('timeout waiting for SAB ring worker message'));},ms);
        const onMessage=(event)=>{ if(predicate(event.data)){ clearTimeout(timer); worker.removeEventListener('message',onMessage); resolve(event.data); } };
        worker.addEventListener('message',onMessage);
        worker.addEventListener('error',(event)=>{clearTimeout(timer);reject(event.error||new Error(event.message||'worker error'));},{once:true});
      });
      const ready=await waitMessage((msg)=>msg&&msg.type==='sab-ring:ready');
      rt.trace.emit('worker:sab-ring-ready',{workerScope:ready.detail?.workerScope,crossOriginIsolated:ready.detail?.crossOriginIsolated});
      worker.postMessage({type:'sab-ring:consume',id:'call:${REVISION}:browser-sab-ring',sab:ring.sab,label:'${REVISION}-browser-sab-ring-worker',timeoutMs:1000});
      const sabStillSharedAfterPost=ring.sab.byteLength===byteLengthBefore;
      rt.trace.emit('ipc:sab-ring-worker-call',{bytes:ring.sab.byteLength,sharedRefId:sharedRef.id,sabStillSharedAfterPost});
      const pushStats={producerWaits:0,maxPushTries:0};
      async function pushEventually(value){ let tries=0; while(!ring.tryPush(value)){ tries+=1; pushStats.producerWaits+=1; await sleep(1); if(tries>3000) throw new Error('producer could not push value '+value); } pushStats.maxPushTries=Math.max(pushStats.maxPushTries,tries+1); }
      for(let value=capacity+1;value<=messageCount;value+=1){ await pushEventually(value); }
      ring.close();
      const response=await waitMessage((msg)=>msg&&msg.id==='call:${REVISION}:browser-sab-ring');
      if(response.type==='sab-ring:error') throw new Error(response.error?.message||'browser SAB ring worker error');
      const expectedValues=Array.from({length:messageCount},(_,i)=>i+1);
      const expectedSum=expectedValues.reduce((sum,value)=>sum+value,0);
      const valuesInOrder=response.values.length===expectedValues.length && response.values.every((value,i)=>value===expectedValues[i]);
      const ringSnapshot=ring.snapshot();
      rt.trace.emit('ipc:sab-ring-worker-result',{count:response.count,sum:response.sum,valuesInOrder,workerPopCount:response.snapshot?.popCount});
      worker.terminate();
      rt.trace.emit('worker:sab-ring-terminate',{reason:'proof-complete'});
      const closeTrace=rt.close();
      return JSON.stringify({
        project:'BrowserRT',revision:m.REVISION,version:m.VERSION,
        page:{location:location.href,readyState:document.readyState,crossOriginIsolated,isSecureContext},
        capabilities:caps,availableTierNames:m.availableCapabilityTierNames(caps),
        constructors:{Worker:typeof Worker,SharedArrayBuffer:typeof SharedArrayBuffer,Atomics:typeof Atomics},
        sabWorkerProof:{
          workerReady:ready,sharedRef:{kind:sharedRef.kind,id:sharedRef.id,bytes:sharedRef.bytes,ownership:sharedRef.ownership,backend:sharedRef.backend},
          capacity,messageCount,fullBeforeConsumer,sabStillSharedAfterPost,
          producerBackpressureObserved:pushStats.producerWaits>0 || ringSnapshot.fullHits>0,
          wraparoundObserved:ringSnapshot.write>capacity && ringSnapshot.read>capacity,
          allReceived:response.count===messageCount,valuesInOrder,sumMatches:response.sum===expectedSum,
          ringClosed:ringSnapshot.closed===true,noPendingItems:ringSnapshot.size===0,workerPopCountMatches:response.snapshot?.popCount===messageCount,
          responseType:response.type,workerScope:response.workerScope,workerCrossOriginIsolated:response.crossOriginIsolated,workerConstructors:response.constructors,
          firstValues:response.values.slice(0,8),lastValues:response.values.slice(-8),workerDurationMs:response.durationMs,pushStats,ringSnapshot,workerSnapshot:response.snapshot
        },
        traceKinds:closeTrace.map(e=>e.kind),
        normalizedTrace:closeTrace.map(e=>({kind:e.kind,label:e.label,capacity:e.capacity,bytes:e.bytes,read:e.read,write:e.write,workerUrl:e.workerUrl,sharedRefId:e.sharedRefId,sabStillSharedAfterPost:e.sabStillSharedAfterPost,count:e.count,sum:e.sum,valuesInOrder:e.valuesInOrder,reason:e.reason})).filter(e=>e.kind)
      });
    })()`;
    const out = await evalJson(expr, timeoutMs);
    mark('browser-sab-ring-worker-eval', proofStart);
    out._pageUrl = pageUrl;
    return out;
  });
  assert.equal(observed.project, 'BrowserRT');
  assert.equal(observed.revision, REVISION);
  assert.equal(observed.version, VERSION);
  assert.equal(observed.page.location, observed._pageUrl);
  assert.equal(observed.page.crossOriginIsolated, true);
  assert.equal(observed.capabilities.environment, 'browser-window');
  assert.equal(observed.constructors.Worker, 'function');
  assert.equal(observed.constructors.SharedArrayBuffer, 'function');
  assert.equal(observed.constructors.Atomics, 'object');
  const proof = observed.sabWorkerProof;
  assert.equal(proof.workerReady.type, 'sab-ring:ready');
  assert.equal(proof.workerReady.detail.workerScope, true);
  assert.equal(proof.sharedRef.kind, 'shared');
  assert.equal(proof.sharedRef.backend, 'SharedArrayBuffer');
  for (const key of ['fullBeforeConsumer','sabStillSharedAfterPost','producerBackpressureObserved','wraparoundObserved','allReceived','valuesInOrder','sumMatches','ringClosed','noPendingItems','workerPopCountMatches','workerScope']) assert.equal(proof[key], true, key);
  assert.equal(proof.workerConstructors.sharedArrayBuffer, 'function');
  assert.equal(proof.workerConstructors.atomics, 'object');
  assert.equal(proof.ringSnapshot.pushCount, 64);
  assert.equal(proof.ringSnapshot.popCount, 64);
  for (const kind of ['runtime:boot','ipc:sab-ring-create','ipc:sab-ring-open','object:shared-ring-ref','object:ref','ipc:sab-ring-full','worker:sab-ring-spawn','worker:sab-ring-ready','ipc:sab-ring-worker-call','ipc:sab-ring-close','ipc:sab-ring-worker-result','worker:sab-ring-terminate','runtime:close']) assert.ok(observed.traceKinds.includes(kind), `missing browser SAB ring trace kind ${kind}`);
  return {
    project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1,
    probe_id: `${REVISION}-browser-sab-ring-worker-probe`, status: 'passed', generatedAt: new Date().toISOString(),
    purpose: 'One-shot browser Worker SharedArrayBuffer ring proof using the shared browser fixture: cross-origin isolation, module Worker spawn, non-detached SAB postMessage sharing, SPSC Int32 ring, Atomics.wait in worker, Atomics.notify from producer, wraparound, close, trace evidence, teardown.',
    chromium: { executable: harness.chromiumExecutable, targetUrl: observed._pageUrl }, policyRelaxation: harness.policyRelaxation, observations: observed,
    server: harness.server, cdp: harness.cdp, timings: harness.timings, durationMs: harness.durationMs, chromeStderrSummary: harness.chromeStderrSummary, chromeStdoutBytes: harness.chromeStdoutBytes,
    nonClaims: ['Chromium-in-cloudtainer browser Worker SAB proof only, not cross-browser conformance.','SPSC fixed Int32 ring only; no MPSC, MPMC, variable-length frame, or multi-consumer proof.','Uses Atomics.wait only inside a dedicated Worker; no browser main-thread blocking wait.','No waitAsync, WebAssembly shared-memory, SharedWorker, ServiceWorker, mesh, throughput, or latency proof.','Temporary managed-policy relaxation is local to this command and restored during teardown.']
  };
}

const argv = process.argv.slice(2);
const out = argValue(argv, '--json', DEFAULT_OUT);
const timeoutMs = Number(argValue(argv, '--timeout-ms', '18000'));
const chromium = argValue(argv, '--chromium', null);
const relaxPolicy = !hasFlag(argv, '--no-policy-relaxation');
try {
  const report = await runProbe({ timeoutMs, chromium, relaxPolicy });
  if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); console.log(out); } else console.log(JSON.stringify(report, null, 2));
} catch (error) {
  const report = { project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1, probe_id: `${REVISION}-browser-sab-ring-worker-probe`, status: 'failed', generatedAt: new Date().toISOString(), error: { name: error?.name || 'Error', message: error?.message || String(error), stack: error?.stack }, nonClaims: ['Failed browser SAB ring Worker probe is not silently skipped. Run this task by id to debug before broad release reruns.'] };
  if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); console.error(out); }
  console.error(`[browser_sab_ring_worker_probe] FAIL: ${error?.stack || error}`);
  process.exitCode = 1;
}
