#!/usr/bin/env node
import assert from 'node:assert/strict';
import { mkdir, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import { performance } from 'node:perf_hooks';
import { REVISION, VERSION } from '../src/browserrt.mjs';
import { runManagedBrowserPage, sleep } from './browser_cdp_fixture.mjs';

const DEFAULT_OUT = `artifacts/validation/REV${REVISION.slice(3)}-BROWSER-OPFS-BLOCK-STORE-PROBE.json`;
const argValue = (argv, flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };
const hasFlag = (argv, flag) => argv.includes(flag);

function exprForWrite(prefix) {
  return `(async()=>{
    const m=await import('/src/browserrt.mjs?rev=${REVISION}&slice=browser-opfs-block-store-write');
    const rt=await m.boot({telemetry:'browser-cdp',proof:'${REVISION}',browserCdpHarness:true,opfsAsyncBlockStoreProof:true});
    const store=rt.opfsAsyncBlockStore({name:'${REVISION}-opfs-block-store',prefix:${JSON.stringify(prefix)}});
    await store.cleanupForTest();
    const payloadA=new TextEncoder().encode('BrowserRT ${REVISION} OPFS async block store payload A :: '+new Array(7).fill('alpha').join('-'));
    const payloadB=new Uint8Array(Array.from({length:96},(_,i)=>(i*17+5)&255));
    const putA=await store.put(payloadA,{label:'payload-a'});
    const putB=await store.put(payloadB,{label:'payload-b'});
    const dupA=await store.put(payloadA,{label:'payload-a-duplicate'});
    const gotA=await store.get(putA.ref);
    const gotB=await store.get(putB.ref.digest);
    const verifyA=await store.verify(putA.ref);
    const hasB=await store.has(putB.ref);
    const estimate=await store.estimate();
    const snapshot=store.snapshot();
    const trace=rt.close();
    return JSON.stringify({
      project:'BrowserRT',revision:m.REVISION,version:m.VERSION,
      page:{location:location.href,readyState:document.readyState,crossOriginIsolated,isSecureContext},
      capabilities:m.detectCapabilities(globalThis),availableTierNames:m.availableCapabilityTierNames(m.detectCapabilities(globalThis)),
      prefix:${JSON.stringify(prefix)},
      refs:{a:putA.ref,b:putB.ref},
      paths:{a:putA.path,b:putB.path},
      puts:{a:putA,b:putB,dupA},
      reads:{aBytes:gotA.byteLength,bBytes:gotB.byteLength,aDigest:await m.digestBytesHex(gotA),bDigest:await m.digestBytesHex(gotB)},
      verifyA,hasB,estimate,snapshot,
      traceKinds:trace.map(e=>e.kind),
      normalizedTrace:trace.map(e=>({kind:e.kind,digest:e.digest,bytes:e.bytes,duplicate:e.duplicate,path:e.path,store:e.store,prefix:e.prefix})).filter(e=>e.kind)
    });
  })()`;
}

function exprForReloadRead(prefix, refA, refB) {
  return `(async()=>{
    const m=await import('/src/browserrt.mjs?rev=${REVISION}&slice=browser-opfs-block-store-reload-read');
    const rt=await m.boot({telemetry:'browser-cdp',proof:'${REVISION}',browserCdpHarness:true,opfsAsyncBlockStoreProof:true});
    const store=rt.opfsAsyncBlockStore({name:'${REVISION}-opfs-block-store-reloaded',prefix:${JSON.stringify(prefix)}});
    const refA=${JSON.stringify(refA)};
    const refB=${JSON.stringify(refB)};
    const hasA=await store.has(refA);
    const hasB=await store.has(refB);
    const gotA=await store.get(refA);
    const gotB=await store.get(refB.digest);
    const verifyA=await store.verify(refA);
    const verifyB=await store.verify(refB);
    const deletedA=await store.delete(refA);
    const deletedB=await store.delete(refB);
    const hasAfterA=await store.has(refA);
    const hasAfterB=await store.has(refB);
    const cleanup=await store.cleanupForTest();
    const snapshot=store.snapshot();
    const trace=rt.close();
    return JSON.stringify({
      project:'BrowserRT',revision:m.REVISION,version:m.VERSION,
      page:{location:location.href,readyState:document.readyState,crossOriginIsolated,isSecureContext},
      prefix:${JSON.stringify(prefix)},
      hasBefore:{a:hasA,b:hasB},
      reloadReads:{aBytes:gotA.byteLength,bBytes:gotB.byteLength,aDigest:await m.digestBytesHex(gotA),bDigest:await m.digestBytesHex(gotB)},
      verifyA,verifyB,deleted:{a:deletedA,b:deletedB},hasAfter:{a:hasAfterA,b:hasAfterB},cleanup,snapshot,
      traceKinds:trace.map(e=>e.kind),
      normalizedTrace:trace.map(e=>({kind:e.kind,digest:e.digest,bytes:e.bytes,deleted:e.deleted,path:e.path,store:e.store,prefix:e.prefix})).filter(e=>e.kind)
    });
  })()`;
}

export async function runProbe(options = {}) {
  const prefix = options.prefix || `browserrt/${REVISION}/opfs-block-store-proof`;
  const { result: observed, harness } = await runManagedBrowserPage({
    timeoutMs: options.timeoutMs,
    chromium: options.chromium,
    relaxPolicy: options.relaxPolicy,
    pagePath: '/opfs-block-store-probe.html',
    pageTitle: 'BrowserRT OPFS block-store probe',
    profilePrefix: 'browserrt-opfs-block-store-cdp-',
    stderrTerms: ['opfs','block','file']
  }, async ({ cdp, evalJson, pageUrl, mark, timeoutMs }) => {
    const writeStart = performance.now();
    const write = await evalJson(exprForWrite(prefix), timeoutMs);
    mark('browser-opfs-block-store-write-eval', writeStart);

    const reloadStart = performance.now();
    await cdp.send('Page.reload', {}, timeoutMs);
    const deadline = performance.now() + timeoutMs;
    let pageState = null;
    while (performance.now() < deadline) {
      await sleep(100);
      pageState = await evalJson('JSON.stringify({location:location.href,readyState:document.readyState,crossOriginIsolated,isSecureContext})', Math.min(1000, timeoutMs));
      if (pageState.location === pageUrl && pageState.readyState !== 'loading') break;
    }
    mark('browser-opfs-block-store-page-reload', reloadStart);
    assert.equal(pageState?.location, pageUrl);

    const readStart = performance.now();
    const read = await evalJson(exprForReloadRead(prefix, write.refs.a, write.refs.b), timeoutMs);
    mark('browser-opfs-block-store-reload-read-eval', readStart);
    return { pageUrl, write, read };
  });

  const write = observed.write;
  const read = observed.read;
  assert.equal(write.project, 'BrowserRT');
  assert.equal(write.revision, REVISION);
  assert.equal(write.version, VERSION);
  assert.equal(write.page.crossOriginIsolated, true);
  assert.equal(write.capabilities.environment, 'browser-window');
  assert.equal(write.capabilities.opfs, true);
  assert.equal(write.puts.a.duplicate, false);
  assert.equal(write.puts.b.duplicate, false);
  assert.equal(write.puts.dupA.duplicate, true);
  assert.equal(write.puts.a.digest, write.puts.dupA.digest);
  assert.equal(write.reads.aDigest, write.puts.a.hash);
  assert.equal(write.reads.bDigest, write.puts.b.hash);
  assert.equal(write.verifyA.ok, true);
  assert.equal(write.hasB, true);
  assert.equal(write.snapshot.provider, 'opfs-async-block-store-v0');
  assert.equal(read.page.crossOriginIsolated, true);
  assert.equal(read.hasBefore.a, true);
  assert.equal(read.hasBefore.b, true);
  assert.equal(read.reloadReads.aDigest, write.puts.a.hash);
  assert.equal(read.reloadReads.bDigest, write.puts.b.hash);
  assert.equal(read.verifyA.ok, true);
  assert.equal(read.verifyB.ok, true);
  assert.equal(read.deleted.a, true);
  assert.equal(read.deleted.b, true);
  assert.equal(read.hasAfter.a, false);
  assert.equal(read.hasAfter.b, false);
  for (const kind of ['runtime:boot','storage:opfs-blockstore-create','storage:opfs-blockstore-open','storage:opfs-block-put','storage:opfs-block-get','storage:opfs-block-has','storage:opfs-block-delete','runtime:close']) {
    assert.ok([...write.traceKinds, ...read.traceKinds].includes(kind), `missing OPFS block-store trace kind ${kind}`);
  }
  return {
    project: 'BrowserRT',
    revision: REVISION,
    version: VERSION,
    schema: 1,
    probe_id: `${REVISION}-browser-opfs-block-store-probe`,
    status: 'passed',
    generatedAt: new Date().toISOString(),
    purpose: 'One-shot browser proof for the async OPFS content-addressed block-store provider: local CDP fixture, BrowserRT import, put/get/has/verify/delete, duplicate dedupe, page-reload readback, trace evidence, cleanup, teardown.',
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
      'Chromium-in-cloudtainer async OPFS block-store proof only, not cross-browser conformance.',
      'Not an OPFS sync access handle, storage-lane provider, journal, crash-recovery, quota-pressure, compaction, multi-tab, or durability proof.',
      'Page-reload readback in one temporary Chromium profile is not a browser restart or crash recovery claim.',
      'Not a throughput, latency, or persistence benchmark.',
      'Temporary managed-policy relaxation is local to this command and restored during teardown.'
    ]
  };
}

const argv = process.argv.slice(2);
const out = argValue(argv, '--json', DEFAULT_OUT);
const timeoutMs = Number(argValue(argv, '--timeout-ms', '16000'));
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
    probe_id: `${REVISION}-browser-opfs-block-store-probe`,
    status: 'failed',
    generatedAt: new Date().toISOString(),
    error: { name: error?.name || 'Error', message: error?.message || String(error), stack: error?.stack },
    nonClaims: ['Failed browser OPFS block-store probe is not silently skipped. Run this task by id to debug before broad release reruns.']
  };
  if (out) {
    await mkdir(dirname(out), { recursive: true });
    await writeFile(out, JSON.stringify(report, null, 2) + '\n');
    console.error(out);
  }
  console.error(`[browser_opfs_block_store_probe] FAIL: ${error?.stack || error}`);
  process.exitCode = 1;
}
