#!/usr/bin/env node
import assert from 'node:assert/strict';
import { mkdir, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import { performance } from 'node:perf_hooks';
import { REVISION, VERSION } from '../src/browserrt.mjs';
import { runManagedBrowserPage } from './browser_cdp_fixture.mjs';

const DEFAULT_OUT = `artifacts/validation/REV${REVISION.slice(3)}-BROWSER-OPFS-ASYNC-PROBE.json`;
const argValue = (argv, flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };
const hasFlag = (argv, flag) => argv.includes(flag);

export async function runProbe(options = {}) {
  const { result: observed, harness } = await runManagedBrowserPage({
    timeoutMs: options.timeoutMs,
    chromium: options.chromium,
    relaxPolicy: options.relaxPolicy,
    pagePath: '/opfs-async-probe.html',
    pageTitle: 'BrowserRT OPFS async probe',
    profilePrefix: 'browserrt-opfs-cdp-',
    stderrTerms: ['opfs', 'file']
  }, async ({ evalJson, pageUrl, mark, timeoutMs }) => {
    const proofStart = performance.now();
    const expr = `(async()=>{
      const m=await import('/src/browserrt.mjs?rev=${REVISION}&slice=browser-opfs-async');
      const rt=await m.boot({telemetry:'browser-cdp',proof:'${REVISION}',browserCdpHarness:true,browserOpfsAsyncProbe:true,opfsAsyncProbe:true});
      const payload='BrowserRT ${REVISION} OPFS async write/read proof :: '+new Array(9).fill('chunk').join('-');
      const path='browserrt/${REVISION}/opfs-async-proof.txt';
      const result=await rt.opfsAsyncWriteReadProbe({path,text:payload,cleanup:true});
      const ref=rt.opfsObjectRef(path,{bytes:result.bytesRead,id:'opfs:${REVISION}:async-proof'});
      const closeTrace=rt.close();
      const caps=m.detectCapabilities(globalThis);
      let estimate=null;
      if (navigator.storage?.estimate) {
        const e=await navigator.storage.estimate();
        estimate={quota:typeof e.quota==='number'?e.quota:null,usage:typeof e.usage==='number'?e.usage:null,usageDetails:e.usageDetails||null};
      }
      return JSON.stringify({
        project:'BrowserRT',revision:m.REVISION,version:m.VERSION,
        page:{location:location.href,readyState:document.readyState,crossOriginIsolated,isSecureContext},
        capabilities:caps,availableTierNames:m.availableCapabilityTierNames(caps),
        opfsProof:{
          available:!!navigator.storage?.getDirectory,
          path:result.path,
          refKind:result.ref.kind,
          refBackend:result.ref.backend,
          refPath:result.ref.path,
          explicitRefId:ref.id,
          explicitRefKind:ref.kind,
          bytesWritten:result.bytesWritten,
          bytesRead:result.bytesRead,
          same:result.same,
          digest:result.digest,
          cleanup:result.cleanup,
          estimate
        },
        traceKinds:closeTrace.map(e=>e.kind),
        normalizedTrace:closeTrace.map(e=>({kind:e.kind,path:e.path,bytesWritten:e.bytesWritten,bytesRead:e.bytesRead,same:e.same,id:e.id,backend:e.backend})).filter(e=>e.kind),
        constructors:{FileSystemDirectoryHandle:typeof FileSystemDirectoryHandle,FileSystemFileHandle:typeof FileSystemFileHandle,WritableStream:typeof WritableStream}
      });
    })()`;
    const out = await evalJson(expr, timeoutMs);
    mark('browser-opfs-async-eval', proofStart);
    out._pageUrl = pageUrl;
    return out;
  });
  assert.equal(observed.project, 'BrowserRT');
  assert.equal(observed.revision, REVISION);
  assert.equal(observed.version, VERSION);
  assert.equal(observed.page.location, observed._pageUrl);
  assert.equal(observed.page.crossOriginIsolated, true);
  assert.equal(observed.capabilities.environment, 'browser-window');
  assert.equal(observed.opfsProof.available, true);
  assert.equal(observed.opfsProof.refKind, 'opfs');
  assert.equal(observed.opfsProof.refBackend, 'opfs-async');
  assert.equal(observed.opfsProof.explicitRefKind, 'opfs');
  assert.equal(observed.opfsProof.same, true);
  assert.equal(observed.opfsProof.bytesWritten, observed.opfsProof.bytesRead);
  assert.ok(observed.opfsProof.bytesRead > 40);
  for (const kind of ['runtime:boot', 'storage:opfs-async-probe-start', 'storage:opfs-async-probe-result', 'object:opfs-ref', 'runtime:close']) {
    assert.ok(observed.traceKinds.includes(kind), `missing OPFS trace kind ${kind}`);
  }
  return {
    project: 'BrowserRT',
    revision: REVISION,
    version: VERSION,
    schema: 1,
    probe_id: `${REVISION}-browser-opfs-async-probe`,
    status: 'passed',
    generatedAt: new Date().toISOString(),
    purpose: 'One-shot browser OPFS async write/read proof using the shared browser fixture: local server, temporary Chromium URL-policy relaxation, CDP attach, BrowserRT module import, navigator.storage.getDirectory, createWritable write, getFile readback, OPFS object-ref trace evidence, teardown.',
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
      'Chromium-in-cloudtainer OPFS async write/read proof only, not cross-browser conformance.',
      'Not a storage durability, quota, compaction, crash-recovery, sync-access-handle, or multi-tab concurrency proof.',
      'Not a performance benchmark.',
      'Temporary managed-policy relaxation is local to this command and restored during teardown.'
    ]
  };
}

const argv = process.argv.slice(2);
const out = argValue(argv, '--json', DEFAULT_OUT);
const timeoutMs = Number(argValue(argv, '--timeout-ms', '14000'));
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
    probe_id: `${REVISION}-browser-opfs-async-probe`,
    status: 'failed',
    generatedAt: new Date().toISOString(),
    error: { name: error?.name || 'Error', message: error?.message || String(error), stack: error?.stack },
    nonClaims: ['Failed browser OPFS async probe is not silently skipped. Run this task by id to debug before broad release reruns.']
  };
  if (out) {
    await mkdir(dirname(out), { recursive: true });
    await writeFile(out, JSON.stringify(report, null, 2) + '\n');
    console.error(out);
  }
  console.error(`[browser_opfs_async_probe] FAIL: ${error?.stack || error}`);
  process.exitCode = 1;
}
