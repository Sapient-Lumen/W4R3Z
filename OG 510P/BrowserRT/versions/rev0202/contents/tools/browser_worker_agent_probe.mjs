#!/usr/bin/env node
import assert from 'node:assert/strict';
import { mkdir, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import { performance } from 'node:perf_hooks';
import { REVISION, VERSION } from '../src/browserrt.mjs';
import { runManagedBrowserPage } from './browser_cdp_fixture.mjs';

const DEFAULT_OUT = `artifacts/validation/REV${REVISION.slice(3)}-BROWSER-WORKER-AGENT-PROBE.json`;
const argValue = (argv, flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };
const hasFlag = (argv, flag) => argv.includes(flag);

export async function runProbe(options = {}) {
  const { result: observed, harness } = await runManagedBrowserPage({
    timeoutMs: options.timeoutMs,
    chromium: options.chromium,
    relaxPolicy: options.relaxPolicy,
    pagePath: '/worker-agent-probe.html',
    pageTitle: 'BrowserRT Worker agent probe',
    profilePrefix: 'browserrt-worker-cdp-',
    stderrTerms: ['worker']
  }, async ({ evalJson, pageUrl, mark, timeoutMs }) => {
    const proofStart = performance.now();
    const expr = `(async()=>{
      const m=await import('/src/browserrt.mjs?rev=${REVISION}&slice=browser-worker-agent');
      const rt=await m.boot({telemetry:'browser-cdp',proof:'${REVISION}',browserWorkerAgentProbe:true,browserCdpHarness:true});
      const agent=await rt.spawnAgent({name:'browser-worker-agent-probe'});
      const ping=await agent.call('ping',{value:'browser-worker-agent'});
      const buffer=new ArrayBuffer(16);
      new Uint32Array(buffer).set([11,13,17,19]);
      const transfer=rt.transferObject(buffer,{id:'transfer:browser-worker-sum',label:'browser-worker-sum'});
      const refBefore={id:transfer.ref.id,bytes:transfer.ref.bytes,ownership:transfer.ref.ownership};
      const sum=await agent.call('sum-u32',{buffer:transfer.buffer,ref:transfer.ref},{transfer:transfer.transferList,priority:'user-blocking',lane:'cpu'});
      const detachedAfter=transfer.buffer.byteLength===0 && buffer.byteLength===0;
      await agent.terminate('browser-worker-agent-proof-complete');
      const closeTrace=rt.close();
      const caps=m.detectCapabilities(globalThis);
      return JSON.stringify({
        project:'BrowserRT',revision:m.REVISION,version:m.VERSION,
        page:{location:location.href,readyState:document.readyState,crossOriginIsolated,isSecureContext},
        capabilities:caps,availableTierNames:m.availableCapabilityTierNames(caps),
        workerProof:{
          pingPong:ping.pong===true,
          pingBackend:ping.payload?.value,
          pingEnvelopeMagic:ping.envelope?.magic,
          transferRefBefore:refBefore,
          sum:sum.sum,count:sum.count,bytes:sum.bytes,refId:sum.ref?.id,
          detachedAfter,
          workerTerminated:true
        },
        traceKinds:closeTrace.map(e=>e.kind),
        normalizedTrace:closeTrace.map(e=>({kind:e.kind,name:e.name,label:e.label,op:e.op,transferCount:e.transferCount,lane:e.lane,priority:e.priority,reason:e.reason})).filter(e=>e.kind),
        constructors:{Worker:typeof Worker,SharedArrayBuffer:typeof SharedArrayBuffer,Atomics:typeof Atomics,MessageChannel:typeof MessageChannel}
      });
    })()`;
    const out = await evalJson(expr, timeoutMs);
    mark('browser-worker-agent-eval', proofStart);
    out._pageUrl = pageUrl;
    return out;
  });
  assert.equal(observed.project, 'BrowserRT');
  assert.equal(observed.revision, REVISION);
  assert.equal(observed.version, VERSION);
  assert.equal(observed.page.location, observed._pageUrl);
  assert.equal(observed.page.crossOriginIsolated, true);
  assert.equal(observed.capabilities.environment, 'browser-window');
  assert.equal(observed.workerProof.pingPong, true);
  assert.equal(observed.workerProof.pingEnvelopeMagic, 'BRT1');
  assert.equal(observed.workerProof.sum, 60);
  assert.equal(observed.workerProof.count, 4);
  assert.equal(observed.workerProof.bytes, 16);
  assert.equal(observed.workerProof.refId, 'transfer:browser-worker-sum');
  assert.equal(observed.workerProof.detachedAfter, true);
  for (const kind of ['runtime:boot', 'agent:spawn', 'agent:ready', 'agent:call', 'agent:result', 'object:transfer-ref', 'agent:terminate', 'runtime:close']) {
    assert.ok(observed.traceKinds.includes(kind), `missing browser worker trace kind ${kind}`);
  }
  return {
    project: 'BrowserRT',
    revision: REVISION,
    version: VERSION,
    schema: 2,
    probe_id: `${REVISION}-browser-worker-agent-probe`,
    status: 'passed',
    generatedAt: new Date().toISOString(),
    purpose: 'One-shot browser Worker agent proof using the shared browser fixture: local server, temporary Chromium URL-policy relaxation, CDP attach, BrowserRT module import, module Worker spawn, ping RPC, transferable ArrayBuffer sum, sender detachment, trace evidence, teardown.',
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
      'Chromium-in-cloudtainer browser Worker proof only, not cross-browser conformance.',
      'Not a performance benchmark.',
      'Does not prove OPFS sync handle, SAB ring, WebGPU, shared worker, service worker, or mesh correctness.',
      'Worker termination proof is caller-managed teardown, not crash/supervisor behavior in the browser.',
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
    schema: 2,
    probe_id: `${REVISION}-browser-worker-agent-probe`,
    status: 'failed',
    generatedAt: new Date().toISOString(),
    error: { name: error?.name || 'Error', message: error?.message || String(error), stack: error?.stack },
    nonClaims: ['Failed browser Worker probe is not silently skipped. Run this task by id to debug before broad release reruns.']
  };
  if (out) {
    await mkdir(dirname(out), { recursive: true });
    await writeFile(out, JSON.stringify(report, null, 2) + '\n');
    console.error(out);
  }
  console.error(`[browser_worker_agent_probe] FAIL: ${error?.stack || error}`);
  process.exitCode = 1;
}
