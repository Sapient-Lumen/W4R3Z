#!/usr/bin/env node
import assert from 'node:assert/strict';
import { mkdir, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import { performance } from 'node:perf_hooks';
import { REVISION, VERSION } from '../src/browserrt.mjs';
import { runManagedBrowserPage } from './browser_cdp_fixture.mjs';

// Manifest task: browser:sab-frame-ring-worker-proof
const DEFAULT_OUT = `artifacts/validation/REV${REVISION.slice(3)}-BROWSER-SAB-FRAME-RING-WORKER-PROBE.json`;
const argValue = (argv, flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };
const hasFlag = (argv, flag) => argv.includes(flag);

export async function runProbe(options = {}) {
  const { result: observed, harness } = await runManagedBrowserPage({
    timeoutMs: options.timeoutMs,
    chromium: options.chromium,
    relaxPolicy: options.relaxPolicy,
    pagePath: '/browser-sab-frame-ring-worker-probe.html',
    pageTitle: 'BrowserRT browser SAB frame-ring worker probe',
    profilePrefix: 'browserrt-sab-frame-ring-cdp-',
    stderrTerms: ['sab', 'SharedArrayBuffer', 'Atomics', 'frame']
  }, async ({ evalJson, pageUrl, mark, timeoutMs }) => {
    const proofStart = performance.now();
    const expr = `(async()=>{
      const sleep=(ms)=>new Promise((resolve)=>setTimeout(resolve,ms));
      function makePayload(seq){
        const length=1+((seq*17)%47);
        const payload=new Uint8Array(length);
        for(let i=0;i<payload.length;i+=1) payload[i]=(seq*31+i*7+length)&0xff;
        return payload;
      }
      function checksum(bytes){
        let out=2166136261>>>0;
        for(const b of bytes){ out^=b; out=Math.imul(out,16777619)>>>0; }
        return out>>>0;
      }
      const m=await import('/src/browserrt.mjs?rev=${REVISION}&slice=browser-sab-frame-ring-worker');
      const rt=await m.boot({telemetry:'browser-cdp',proof:'${REVISION}',browserCdpHarness:true,browserSabFrameRingWorkerProbe:true,sharedMemoryFrameRingProbe:true});
      const caps=m.detectCapabilities(globalThis);
      if(!crossOriginIsolated) throw new Error('browser SAB frame-ring proof requires crossOriginIsolated');
      if(typeof SharedArrayBuffer!=='function') throw new Error('SharedArrayBuffer unavailable in browser page');
      if(typeof Atomics!=='object') throw new Error('Atomics unavailable in browser page');
      const capacityBytes=192;
      const frameCount=72;
      const frames=Array.from({length:frameCount},(_,seq)=>({seq,payload:makePayload(seq)}));
      const ring=rt.sharedFrameRing({capacityBytes,label:'${REVISION}-browser-sab-frame-ring'});
      const sharedRef=rt.objectRef('shared',{id:'shared:${REVISION}:browser-sab-frame-ring',bytes:ring.sab.byteLength,ownership:'shared-browser-worker',backend:'SharedArrayBuffer-frame-ring'});
      const oversizeRejected=ring.tryPushFrame(new Uint8Array(capacityBytes),{seq:0x7fff})===false;
      let prefilled=0;
      for(;prefilled<frames.length;prefilled+=1){ if(!ring.tryPushFrame(frames[prefilled].payload,{seq:frames[prefilled].seq})) break; }
      const fullBeforeConsumer=prefilled>0 && ring.tryPushFrame(new Uint8Array(31),{seq:0x7ffe})===false;
      const byteLengthBefore=ring.sab.byteLength;
      const workerUrl='/src/browser-sab-frame-ring-worker.mjs?rev=${REVISION}&slice=browser-sab-frame-ring-worker';
      rt.trace.emit('worker:sab-frame-ring-spawn',{workerUrl,capacityBytes,frameCount,prefilled});
      const worker=new Worker(workerUrl,{type:'module',name:'browserrt-sab-frame-ring-worker'});
      const waitMessage=(predicate,ms=10000)=>new Promise((resolve,reject)=>{
        const timer=setTimeout(()=>{worker.removeEventListener('message',onMessage);reject(new Error('timeout waiting for SAB frame-ring worker message'));},ms);
        const onMessage=(event)=>{ if(predicate(event.data)){ clearTimeout(timer); worker.removeEventListener('message',onMessage); resolve(event.data); } };
        worker.addEventListener('message',onMessage);
        worker.addEventListener('error',(event)=>{ clearTimeout(timer); reject(event.error||new Error(event.message||'worker error')); },{once:true});
      });
      const ready=await waitMessage((msg)=>msg&&msg.type==='sab-frame-ring:ready');
      rt.trace.emit('worker:sab-frame-ring-ready',{workerScope:ready.detail?.workerScope,crossOriginIsolated:ready.detail?.crossOriginIsolated});
      worker.postMessage({type:'sab-frame-ring:consume',id:'call:${REVISION}:browser-sab-frame-ring',sab:ring.sab,label:'${REVISION}-browser-sab-frame-ring-worker',timeoutMs:1000});
      const sabStillSharedAfterPost=ring.sab.byteLength===byteLengthBefore;
      rt.trace.emit('ipc:sab-frame-ring-worker-call',{bytes:ring.sab.byteLength,sharedRefId:sharedRef.id,sabStillSharedAfterPost,prefilled});
      const pushStats={producerWaits:0,maxPushTries:0,prefilled};
      async function pushEventually(frame){
        let tries=0;
        while(!ring.tryPushFrame(frame.payload,{seq:frame.seq})){
          tries+=1;
          pushStats.producerWaits+=1;
          await sleep(1);
          if(tries>3000) throw new Error('producer could not push frame '+frame.seq);
        }
        pushStats.maxPushTries=Math.max(pushStats.maxPushTries,tries+1);
      }
      for(let i=prefilled;i<frames.length;i+=1) await pushEventually(frames[i]);
      ring.close();
      const response=await waitMessage((msg)=>msg&&msg.id==='call:${REVISION}:browser-sab-frame-ring');
      if(response.type==='sab-frame-ring:error') throw new Error(response.error?.message||'browser SAB frame-ring worker error');
      const expectedDescriptors=frames.map((frame)=>({seq:frame.seq,bytes:frame.payload.byteLength,checksum:checksum(frame.payload)}));
      const expectedTotalBytes=expectedDescriptors.reduce((sum,frame)=>sum+frame.bytes,0);
      const expectedCombinedChecksum=expectedDescriptors.reduce((sum,frame)=>(sum+frame.checksum+frame.seq)>>>0,0);
      const seqsInOrder=response.frames.length===expectedDescriptors.length && response.frames.every((frame,i)=>frame.seq===expectedDescriptors[i].seq);
      const lengthsMatch=response.frames.length===expectedDescriptors.length && response.frames.every((frame,i)=>frame.bytes===expectedDescriptors[i].bytes);
      const checksumsMatch=response.frames.length===expectedDescriptors.length && response.frames.every((frame,i)=>frame.checksum===expectedDescriptors[i].checksum);
      const ringSnapshot=ring.snapshot();
      rt.trace.emit('ipc:sab-frame-ring-worker-result',{count:response.count,totalBytes:response.totalBytes,combinedChecksum:response.combinedChecksum,seqsInOrder,checksumsMatch,workerPopCount:response.snapshot?.popCount});
      worker.terminate();
      rt.trace.emit('worker:sab-frame-ring-terminate',{reason:'proof-complete'});
      const closeTrace=rt.close();
      return JSON.stringify({
        project:'BrowserRT',revision:m.REVISION,version:m.VERSION,
        page:{location:location.href,readyState:document.readyState,crossOriginIsolated,isSecureContext},
        capabilities:caps,availableTierNames:m.availableCapabilityTierNames(caps),
        constructors:{Worker:typeof Worker,SharedArrayBuffer:typeof SharedArrayBuffer,Atomics:typeof Atomics},
        sabFrameWorkerProof:{
          workerReady:ready,sharedRef:{kind:sharedRef.kind,id:sharedRef.id,bytes:sharedRef.bytes,ownership:sharedRef.ownership,backend:sharedRef.backend},
          capacityBytes,frameCount,prefilled,variableLengthsObserved:new Set(expectedDescriptors.map((frame)=>frame.bytes)).size>8,
          oversizeRejected,fullBeforeConsumer,sabStillSharedAfterPost,
          producerBackpressureObserved:pushStats.producerWaits>0 || ringSnapshot.fullHits>0,
          wraparoundObserved:ringSnapshot.wrapCount>0,reservedGapBytesObserved:ringSnapshot.reservedBytes>0,
          allReceived:response.count===frameCount,seqsInOrder,lengthsMatch,checksumsMatch,
          totalBytesMatches:response.totalBytes===expectedTotalBytes,combinedChecksumMatches:response.combinedChecksum===expectedCombinedChecksum,
          ringClosed:ringSnapshot.closed===true,noPendingBytes:ringSnapshot.usedBytes===0,workerPopCountMatches:response.snapshot?.popCount===frameCount,
          responseType:response.type,workerScope:response.workerScope,workerCrossOriginIsolated:response.crossOriginIsolated,workerConstructors:response.constructors,
          firstFrames:response.firstFrames,lastFrames:response.lastFrames,workerDurationMs:response.durationMs,pushStats,ringSnapshot,workerSnapshot:response.snapshot
        },
        traceKinds:closeTrace.map(e=>e.kind),
        normalizedTrace:closeTrace.map(e=>({kind:e.kind,label:e.label,capacityBytes:e.capacityBytes,bytes:e.bytes,readOffset:e.readOffset,writeOffset:e.writeOffset,fromOffset:e.fromOffset,gapBytes:e.gapBytes,seq:e.seq,count:e.count,totalBytes:e.totalBytes,combinedChecksum:e.combinedChecksum,seqsInOrder:e.seqsInOrder,checksumsMatch:e.checksumsMatch,workerUrl:e.workerUrl,sharedRefId:e.sharedRefId,sabStillSharedAfterPost:e.sabStillSharedAfterPost,reason:e.reason})).filter(e=>e.kind)
      });
    })()`;
    const out = await evalJson(expr, timeoutMs);
    mark('browser-sab-frame-ring-worker-eval', proofStart);
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
  const proof = observed.sabFrameWorkerProof;
  assert.equal(proof.workerReady.type, 'sab-frame-ring:ready');
  assert.equal(proof.workerReady.detail.workerScope, true);
  assert.equal(proof.sharedRef.kind, 'shared');
  assert.equal(proof.sharedRef.backend, 'SharedArrayBuffer-frame-ring');
  for (const key of ['variableLengthsObserved','oversizeRejected','fullBeforeConsumer','sabStillSharedAfterPost','producerBackpressureObserved','wraparoundObserved','reservedGapBytesObserved','allReceived','seqsInOrder','lengthsMatch','checksumsMatch','totalBytesMatches','combinedChecksumMatches','ringClosed','noPendingBytes','workerPopCountMatches','workerScope']) assert.equal(proof[key], true, key);
  assert.equal(proof.workerConstructors.sharedArrayBuffer, 'function');
  assert.equal(proof.workerConstructors.atomics, 'object');
  assert.equal(proof.ringSnapshot.pushCount, 72);
  assert.equal(proof.ringSnapshot.popCount, 72);
  for (const kind of ['runtime:boot','ipc:sab-frame-ring-create','ipc:sab-frame-ring-open','object:shared-frame-ring-ref','object:ref','ipc:sab-frame-ring-oversize','ipc:sab-frame-ring-full','ipc:sab-frame-ring-wrap','worker:sab-frame-ring-spawn','worker:sab-frame-ring-ready','ipc:sab-frame-ring-worker-call','ipc:sab-frame-ring-close','ipc:sab-frame-ring-worker-result','worker:sab-frame-ring-terminate','runtime:close']) assert.ok(observed.traceKinds.includes(kind), `missing browser SAB frame-ring trace kind ${kind}`);

  return {
    project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1,
    probe_id: `${REVISION}-browser-sab-frame-ring-worker-probe`, status: 'passed', generatedAt: new Date().toISOString(),
    purpose: 'One-shot browser Worker variable-frame SharedArrayBuffer proof using the shared browser fixture: cross-origin isolation, module Worker spawn, non-detached SAB postMessage sharing, SPSC frame ring, variable payloads, oversize/full rejection, Atomics.wait in worker, Atomics.notify from producer, wrap sentinel, close, trace evidence, teardown.',
    chromium: { executable: harness.chromiumExecutable, targetUrl: observed._pageUrl }, policyRelaxation: harness.policyRelaxation, observations: observed,
    server: harness.server, cdp: harness.cdp, timings: harness.timings, durationMs: harness.durationMs, chromeStderrSummary: harness.chromeStderrSummary, chromeStdoutBytes: harness.chromeStdoutBytes,
    nonClaims: ['Chromium-in-cloudtainer browser Worker SAB frame-ring proof only, not cross-browser conformance.','SPSC copied-frame mailbox only; no MPSC, MPMC, zero-copy schema view, or multi-consumer proof.','Uses Atomics.wait only inside a dedicated Worker; no browser main-thread blocking wait.','No waitAsync, WebAssembly shared-memory, OPFS spill, mesh, latency, or throughput claim.']
  };
}

async function main() {
  const jsonPath = argValue(process.argv, '--json', DEFAULT_OUT);
  const chromium = argValue(process.argv, '--chromium', null);
  const timeout = Number(argValue(process.argv, '--timeout-ms', '26000'));
  const report = await runProbe({ chromium, timeoutMs: timeout, relaxPolicy: !hasFlag(process.argv, '--no-relax-policy') });
  if (jsonPath) {
    await mkdir(dirname(jsonPath), { recursive: true });
    await writeFile(jsonPath, JSON.stringify(report, null, 2) + '\n');
  }
  console.log(`[browser_sab_frame_ring_worker_probe] ${report.status} ${report.probe_id} in ${report.durationMs}ms`);
}

if (import.meta.url === `file://${process.argv[1]}`) main().catch((error) => { console.error(`[browser_sab_frame_ring_worker_probe] FAIL: ${error.stack || error.message}`); process.exitCode = 1; });
