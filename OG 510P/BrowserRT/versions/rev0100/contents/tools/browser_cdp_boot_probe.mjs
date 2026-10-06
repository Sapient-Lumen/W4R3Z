#!/usr/bin/env node
import assert from 'node:assert/strict';
import { mkdir, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import { performance } from 'node:perf_hooks';
import { REVISION, VERSION } from '../src/browserrt.mjs';
import { runManagedBrowserPage } from './browser_cdp_fixture.mjs';

const DEFAULT_OUT = `artifacts/validation/REV${REVISION.slice(3)}-BROWSER-CDP-BOOT-PROBE.json`;
const argValue = (argv, flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };
const hasFlag = (argv, flag) => argv.includes(flag);

export async function runProbe(options = {}) {
  const { result: observed, harness } = await runManagedBrowserPage({
    timeoutMs: options.timeoutMs,
    chromium: options.chromium,
    relaxPolicy: options.relaxPolicy,
    pagePath: '/boot-probe.html',
    pageTitle: 'BrowserRT CDP boot probe',
    profilePrefix: 'browserrt-cdp-',
    stderrTerms: ['CDP']
  }, async ({ evalJson, pageUrl, mark, timeoutMs }) => {
    const proofStart = performance.now();
    const expr = `(async()=>{const m=await import('/src/browserrt.mjs?rev=${REVISION}&slice=browser-cdp-boot');const rt=await m.boot({telemetry:'browser-cdp',proof:'${REVISION}',browserCdpBootProbe:true});const report=rt.report;const trace=rt.close();const caps=m.detectCapabilities(globalThis);return JSON.stringify({project:'BrowserRT',revision:m.REVISION,version:m.VERSION,page:{location:location.href,readyState:document.readyState,crossOriginIsolated,isSecureContext},capabilities:caps,availableTierNames:m.availableCapabilityTierNames(caps),report,traceKinds:trace.map(e=>e.kind),constructors:{Worker:typeof Worker,SharedArrayBuffer:typeof SharedArrayBuffer,Atomics:typeof Atomics,MessageChannel:typeof MessageChannel,navigatorStorageGetDirectory:typeof navigator.storage?.getDirectory,navigatorGpu:typeof navigator.gpu}});})()`;
    const out = await evalJson(expr, timeoutMs);
    mark('browserrt-boot-eval', proofStart);
    out._pageUrl = pageUrl;
    return out;
  });
  assert.equal(observed.project, 'BrowserRT');
  assert.equal(observed.revision, REVISION);
  assert.equal(observed.version, VERSION);
  assert.equal(observed.page.location, observed._pageUrl);
  assert.equal(observed.page.crossOriginIsolated, true);
  assert.equal(observed.capabilities.environment, 'browser-window');
  assert.ok(observed.traceKinds.includes('runtime:boot'));
  assert.ok(observed.traceKinds.includes('runtime:close'));
  return {
    project: 'BrowserRT',
    revision: REVISION,
    version: VERSION,
    schema: 2,
    probe_id: `${REVISION}-browser-cdp-boot-probe`,
    status: 'passed',
    generatedAt: new Date().toISOString(),
    purpose: 'One-shot managed browser/CDP boot report using the shared browser fixture: local server, temporary Chromium URL-policy relaxation, CDP attach, BrowserRT import, capability probe, teardown evidence.',
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
      'Chromium-in-cloudtainer CDP boot proof only, not cross-browser conformance.',
      'Not a performance benchmark.',
      'Does not prove browser Worker, OPFS sync handle, SAB ring, WebGPU, shared worker, service worker, or mesh correctness.',
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
    probe_id: `${REVISION}-browser-cdp-boot-probe`,
    status: 'failed',
    generatedAt: new Date().toISOString(),
    error: { name: error?.name || 'Error', message: error?.message || String(error), stack: error?.stack },
    nonClaims: ['Failed browser CDP boot probe is not silently skipped. Run this task by id to debug before broad release reruns.']
  };
  if (out) {
    await mkdir(dirname(out), { recursive: true });
    await writeFile(out, JSON.stringify(report, null, 2) + '\n');
    console.error(out);
  }
  console.error(`[browser_cdp_boot_probe] FAIL: ${error?.stack || error}`);
  process.exitCode = 1;
}
