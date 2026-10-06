#!/usr/bin/env node
// Manifest slice: browser:kernel-kit-session-coordination-checkpoint-proof. Browser-heavy same-origin Web Locks + local handoff coordination proof.
import assert from 'node:assert/strict';
import { mkdir, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import {
  REVISION,
  VERSION,
  createKernelKitSessionCoordinationCheckpoint,
  validateKernelKitSessionCoordinationCheckpoint,
  KERNEL_KIT_SESSION_COORDINATION_CHECKPOINT_NON_CLAIMS
} from '../src/browserrt.mjs';
import { runManagedBrowserPage, connectBrowserCdp, openPageTarget, evalJson, sleep } from './browser_cdp_fixture.mjs';

const PREFIX = `REV${REVISION.slice(3)}`;
const DEFAULT_OUT = `artifacts/validation/${PREFIX}-BROWSER-KERNEL-KIT-SESSION-COORDINATION-CHECKPOINT-PROBE.json`;
const argValue = (argv, flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };
const TIMEOUT_MS = Number(process.env.BROWSERRT_BROWSER_TIMEOUT_MS || 22000);

function pageBody() {
  return `<!doctype html>
<meta charset="utf-8">
<title>BrowserRT session coordination checkpoint</title>
<body>BrowserRT session coordination checkpoint</body>
<script>
window.__BRT_SESSION_COORD_READY = true;
</script>`;
}

async function waitForReady(cdp, timeoutMs) {
  return await evalJson(cdp, `(async()=>{ for(let i=0;i<100;i+=1){ if(window.__BRT_SESSION_COORD_READY) return JSON.stringify({ready:true, location:location.href, origin:location.origin, hasLocks:!!navigator.locks, hasLocalStorage:!!window.localStorage}); await new Promise(r=>setTimeout(r,25)); } throw new Error('session coordination page not ready'); })()`, timeoutMs);
}

async function pollPeerQueued(peerCdp, timeoutMs) {
  const deadline = Date.now() + timeoutMs;
  let last = null;
  while (Date.now() < deadline) {
    last = await evalJson(peerCdp, `(async()=>JSON.stringify({acquired:window.__brtQueued?.acquired===true, done:window.__brtQueued?.done===true, result:window.__brtQueued?.result||null, events:window.__brtQueued?.events||[]}))()`, Math.min(1000, timeoutMs));
    if (last.done === true) return last;
    await sleep(40);
  }
  throw new Error(`queued peer lock did not finish: ${JSON.stringify(last)}`);
}

async function pollStorageEvents(cdp, timeoutMs) {
  const deadline = Date.now() + timeoutMs;
  let last = null;
  while (Date.now() < deadline) {
    last = await evalJson(cdp, `(async()=>JSON.stringify({events:window.__brtStorageEvents||[]}))()`, Math.min(1000, timeoutMs));
    const events = Array.isArray(last.events) ? last.events : [];
    const sawSet = events.some((event) => event.newPresent === true);
    const sawClear = events.some((event) => event.oldPresent === true && event.newPresent === false);
    if (sawSet && sawClear) return { ...last, sawSet, sawClear };
    await sleep(40);
  }
  const events = Array.isArray(last?.events) ? last.events : [];
  return { events, sawSet: events.some((event) => event.newPresent === true), sawClear: events.some((event) => event.oldPresent === true && event.newPresent === false) };
}

function compactCheckpoint(checkpoint, validation) {
  return Object.freeze({
    status: checkpoint.status,
    validationOk: validation.ok === true,
    observedRowIds: checkpoint.observedRowIds,
    deferredRowIds: checkpoint.deferredRowIds,
    failedRowIds: checkpoint.failedRowIds,
    riskSummary: checkpoint.riskSummary,
    proof: checkpoint.proof,
    summary: checkpoint.summary
  });
}

export async function runProbe() {
  let browserClient = null;
  let peer = null;
  const observed = await runManagedBrowserPage({
    pagePath: '/session-coordination.html',
    pageTitle: 'BrowserRT session coordination checkpoint',
    body: pageBody(),
    allowedPrefixes: ['src/'],
    timeoutMs: TIMEOUT_MS,
    stderrTerms: ['Web Locks', 'localStorage', 'quota']
  }, async ({ cdp, pageUrl, cdpPort, listUrl, timeoutMs }) => {
    const readyA = await waitForReady(cdp, timeoutMs);
    assert.equal(readyA.hasLocks, true, 'primary page must expose navigator.locks');
    assert.equal(readyA.hasLocalStorage, true, 'primary page must expose localStorage');
    const browser = await connectBrowserCdp(cdpPort, timeoutMs);
    browserClient = browser.cdp;
    peer = await openPageTarget(browserClient, { listUrl, url: pageUrl, timeoutMs });
    const readyB = await waitForReady(peer.cdp, timeoutMs);
    assert.equal(readyB.origin, readyA.origin, 'peer page must be same-origin');
    const lockName = `BrowserRT:${REVISION}:session-coordination`;
    const handoffKey = `BrowserRT.KernelKitDemo.handoff.${REVISION}.sessionCoordination`;

    const primaryAcquire = await evalJson(cdp, `(async()=>{
      const name=${JSON.stringify(lockName)};
      window.__brtLockHold={events:[], acquired:false, released:false, done:false};
      window.__brtLockHold.promise=navigator.locks.request(name,{mode:'exclusive'},async(lock)=>{
        window.__brtLockHold.acquired=!!lock;
        window.__brtLockHold.events.push('primary-acquired');
        await new Promise((resolve)=>{ window.__brtLockHold.release=()=>{ window.__brtLockHold.events.push('primary-release-called'); resolve(); }; });
        window.__brtLockHold.released=true;
        window.__brtLockHold.events.push('primary-released');
        return 'primary-done';
      }).then((value)=>{ window.__brtLockHold.done=true; window.__brtLockHold.result=value; return value; });
      for(let i=0;i<100;i+=1){ if(window.__brtLockHold.acquired) return JSON.stringify({acquired:true, events:window.__brtLockHold.events, hasLocks:!!navigator.locks}); await new Promise((resolve)=>setTimeout(resolve,20)); }
      throw new Error('primary lock did not acquire');
    })()`, timeoutMs);
    assert.equal(primaryAcquire.acquired, true, 'primary page should acquire exclusive lock');

    const ifAvailable = await evalJson(peer.cdp, `(async()=>JSON.stringify(await navigator.locks.request(${JSON.stringify(lockName)},{mode:'exclusive',ifAvailable:true},(lock)=>({acquired:!!lock}))))()`, timeoutMs);
    assert.equal(ifAvailable.acquired, false, 'peer ifAvailable request should be denied while primary holds lock');

    const queuedBeforeRelease = await evalJson(peer.cdp, `(async()=>{
      const name=${JSON.stringify(lockName)};
      window.__brtQueued={acquired:false, done:false, events:[]};
      window.__brtQueued.promise=navigator.locks.request(name,{mode:'exclusive'},async(lock)=>{
        window.__brtQueued.acquired=!!lock;
        window.__brtQueued.events.push('peer-acquired');
        return 'peer-done';
      }).then((value)=>{ window.__brtQueued.done=true; window.__brtQueued.result=value; return value; });
      await new Promise((resolve)=>setTimeout(resolve,90));
      return JSON.stringify({started:true, acquired:window.__brtQueued.acquired, done:window.__brtQueued.done, events:window.__brtQueued.events});
    })()`, timeoutMs);
    assert.equal(queuedBeforeRelease.acquired, false, 'queued peer must wait until primary releases');
    assert.equal(queuedBeforeRelease.done, false, 'queued peer must not finish before release');

    const releasePrimary = await evalJson(cdp, `(async()=>{
      if(typeof window.__brtLockHold?.release !== 'function') throw new Error('primary release function missing');
      window.__brtLockHold.release();
      await window.__brtLockHold.promise;
      return JSON.stringify({released:window.__brtLockHold.released===true, done:window.__brtLockHold.done===true, result:window.__brtLockHold.result||null, events:window.__brtLockHold.events});
    })()`, timeoutMs);
    assert.equal(releasePrimary.done, true, 'primary lock promise should finish after release');

    const queuedAfterRelease = await pollPeerQueued(peer.cdp, timeoutMs);
    assert.equal(queuedAfterRelease.acquired, true, 'peer queued request should acquire after primary release');
    assert.equal(queuedAfterRelease.done, true, 'peer queued request should finish after release');

    const queryAfter = await evalJson(cdp, `(async()=>{
      const name=${JSON.stringify(lockName)};
      const q=await navigator.locks.query();
      const held=(q.held||[]).filter((row)=>row.name===name);
      const pending=(q.pending||[]).filter((row)=>row.name===name);
      return JSON.stringify({heldCount:held.length, pendingCount:pending.length, drained:held.length===0 && pending.length===0});
    })()`, timeoutMs);
    assert.equal(queryAfter.drained, true, 'lock query should be drained after proof');

    const listener = await evalJson(cdp, `(async()=>{
      const key=${JSON.stringify(handoffKey)};
      window.__brtStorageEvents=[];
      window.addEventListener('storage',(event)=>{ if(event.key===key) window.__brtStorageEvents.push({key:event.key, oldPresent:event.oldValue!==null, newPresent:event.newValue!==null}); });
      return JSON.stringify({listener:true});
    })()`, timeoutMs);
    assert.equal(listener.listener, true);

    const handoffStore = await evalJson(peer.cdp, `(async()=>{
      const key=${JSON.stringify(handoffKey)};
      const value={project:'BrowserRT',revision:${JSON.stringify(REVISION)},checkpoint:'session-coordination',nonce:'deterministic-session-coordination'};
      localStorage.setItem(key, JSON.stringify(value));
      return JSON.stringify({stored:true, valuePresent:localStorage.getItem(key)!==null});
    })()`, timeoutMs);
    assert.equal(handoffStore.stored, true);
    await sleep(80);
    const handoffConsume = await evalJson(peer.cdp, `(async()=>{
      const key=${JSON.stringify(handoffKey)};
      const before=localStorage.getItem(key);
      const parsed=before ? JSON.parse(before) : null;
      localStorage.removeItem(key);
      const after=localStorage.getItem(key);
      return JSON.stringify({beforePresent:before!==null, parsedRevision:parsed?.revision||null, afterValue:after});
    })()`, timeoutMs);
    assert.equal(handoffConsume.beforePresent, true, 'handoff should exist before single-use consume');
    assert.equal(handoffConsume.afterValue, null, 'handoff should be absent after single-use consume');
    const storageEvents = await pollStorageEvents(cdp, timeoutMs);
    assert.equal(storageEvents.sawClear, true, 'primary page should observe peer localStorage clear event');

    const coordination = Object.freeze({
      project: 'BrowserRT',
      revision: REVISION,
      status: 'passed',
      source: `${REVISION}-browser-kernel-kit-session-coordination-checkpoint-probe`,
      probe_id: `${REVISION}-browser-kernel-kit-session-coordination-checkpoint-probe`,
      commandId: 'browser:kernel-kit-session-coordination-checkpoint-proof',
      tier: 'browser-heavy-explicit',
      origin: readyA.origin,
      sameOriginPages: readyA.origin === readyB.origin,
      lockContention: Object.freeze({
        sameOrigin: readyA.origin === readyB.origin,
        navigatorLocksSeen: readyA.hasLocks === true && readyB.hasLocks === true,
        ifAvailable: Object.freeze({ acquired: ifAvailable.acquired }),
        queue: Object.freeze({ waitedUntilRelease: queuedBeforeRelease.acquired === false && queuedBeforeRelease.done === false, acquiredAfterRelease: queuedAfterRelease.acquired === true && queuedAfterRelease.done === true }),
        queryAfter: Object.freeze(queryAfter)
      }),
      handoff: Object.freeze({
        keyDigest: `fnv32:${(handoffKey.length * 2654435761 >>> 0).toString(16).padStart(8, '0')}`,
        storageEvent: Object.freeze({ observed: storageEvents.sawClear === true, sawSet: storageEvents.sawSet === true, sawClear: storageEvents.sawClear === true, eventCount: storageEvents.events.length }),
        singleUseClearObserved: handoffConsume.beforePresent === true && handoffConsume.afterValue === null,
        afterConsume: Object.freeze({ value: handoffConsume.afterValue }),
        staleReadReturnedNull: handoffConsume.afterValue === null
      }),
      proof: Object.freeze({
        sameOriginPages: readyA.origin === readyB.origin,
        sameOriginSessionScopeVisible: readyA.origin === readyB.origin,
        navigatorLocksSeen: readyA.hasLocks === true && readyB.hasLocks === true,
        exclusiveIfAvailableDenied: ifAvailable.acquired === false,
        queuedWaitedUntilRelease: queuedBeforeRelease.acquired === false && queuedBeforeRelease.done === false,
        queuedAcquiredAfterRelease: queuedAfterRelease.acquired === true && queuedAfterRelease.done === true,
        locksDrainedAfterUse: queryAfter.drained === true,
        crossTabStorageEventObserved: storageEvents.sawClear === true,
        handoffSingleUseClearObserved: handoffConsume.beforePresent === true && handoffConsume.afterValue === null,
        staleReadReturnedNull: handoffConsume.afterValue === null,
        noFairnessClaim: true,
        noCrashRecoveryClaim: true,
        browserHeavyExplicit: true,
        abandonedLockReleaseClaimed: false
      }),
      nonClaims: KERNEL_KIT_SESSION_COORDINATION_CHECKPOINT_NON_CLAIMS
    });
    const checkpoint = createKernelKitSessionCoordinationCheckpoint({
      sessionCoordination: coordination,
      exactCommands: ['node tools/run_tests.mjs --tier browser --id browser:kernel-kit-session-coordination-checkpoint-proof --jobs 1'],
      nonClaims: KERNEL_KIT_SESSION_COORDINATION_CHECKPOINT_NON_CLAIMS
    }, { revision: REVISION, generatedAt: 'deterministic-browser-session-coordination-checkpoint', source: 'browser-kernel-kit-session-coordination-checkpoint-probe' });
    const validation = validateKernelKitSessionCoordinationCheckpoint(checkpoint);
    assert.equal(validation.ok, true, validation.errors.join('; '));
    assert.equal(checkpoint.status, 'risk-checkpoint-ready');

    return Object.freeze({ pageUrl, readyA, readyB, primaryAcquire, ifAvailable, queuedBeforeRelease, releasePrimary, queuedAfterRelease, queryAfter, handoffStore, handoffConsume, storageEvents, coordination, checkpoint: compactCheckpoint(checkpoint, validation), validation });
  }).finally(async () => {
    if (peer) {
      try { await peer.close(); } catch {}
      peer = null;
    }
    if (browserClient) {
      try { browserClient.close(); } catch {}
      browserClient = null;
    }
  });

  const coordination = observed.result.coordination;
  const report = Object.freeze({
    project: 'BrowserRT',
    revision: REVISION,
    version: VERSION,
    schema: 1,
    probe_id: `${REVISION}-browser-kernel-kit-session-coordination-checkpoint-probe`,
    status: 'passed',
    proofId: `${REVISION}-browser-kernel-kit-session-coordination-checkpoint`,
    observations: Object.freeze({
      origin: coordination.origin,
      lock: Object.freeze({ ifAvailableAcquired: observed.result.ifAvailable.acquired, queuedAcquiredAfterRelease: observed.result.queuedAfterRelease.acquired, locksDrained: observed.result.queryAfter.drained }),
      handoff: Object.freeze({ singleUseClearObserved: coordination.handoff.singleUseClearObserved, staleReadReturnedNull: coordination.handoff.staleReadReturnedNull, storageEventObserved: coordination.handoff.storageEvent.observed })
    }),
    checkpoint: observed.result.checkpoint,
    validation: observed.result.validation,
    harness: observed.harness,
    proof: Object.freeze({
      sameOriginPages: coordination.proof.sameOriginPages,
      navigatorLocksSeen: coordination.proof.navigatorLocksSeen,
      exclusiveIfAvailableDenied: coordination.proof.exclusiveIfAvailableDenied,
      queuedWaitedUntilRelease: coordination.proof.queuedWaitedUntilRelease,
      queuedAcquiredAfterRelease: coordination.proof.queuedAcquiredAfterRelease,
      locksDrainedAfterUse: coordination.proof.locksDrainedAfterUse,
      crossTabStorageEventObserved: coordination.proof.crossTabStorageEventObserved,
      handoffSingleUseClearObserved: coordination.proof.handoffSingleUseClearObserved,
      staleReadReturnedNull: coordination.proof.staleReadReturnedNull,
      noFairnessClaim: coordination.proof.noFairnessClaim,
      noCrashRecoveryClaim: coordination.proof.noCrashRecoveryClaim,
      abandonedLockReleaseClaimed: false,
      browserHeavyExplicit: true,
      checkpointReady: observed.result.checkpoint.status === 'risk-checkpoint-ready'
    }),
    nonClaims: KERNEL_KIT_SESSION_COORDINATION_CHECKPOINT_NON_CLAIMS
  });
  return report;
}

const isMain = process.argv[1] && import.meta.url === new URL(process.argv[1], 'file:').href;
if (isMain) {
  const out = argValue(process.argv.slice(2), '--json', DEFAULT_OUT);
  const report = await runProbe();
  if (out) {
    await mkdir(dirname(out), { recursive: true });
    await writeFile(out, JSON.stringify(report, null, 2) + '\n');
    console.log(out);
  } else console.log(JSON.stringify(report, null, 2));
}

// Static audit markers: browser:kernel-kit-session-coordination-checkpoint-proof; browserrt-kernel-kit-session-coordination-checkpoint-v1; navigator.locks.request; navigator.locks.query; localStorage.setItem; localStorage.removeItem; storage event; exclusiveIfAvailableDenied; queuedAcquiredAfterRelease; handoffSingleUseClearObserved; staleReadReturnedNull; No Web Locks fairness, starvation-freedom, or scheduler ordering claim.
