#!/usr/bin/env node
import assert from 'node:assert/strict';
import { mkdir, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import { REVISION, VERSION } from '../src/browserrt.mjs';
import { runManagedBrowserPage } from './browser_cdp_fixture.mjs';

const DEFAULT_OUT = `artifacts/validation/REV${REVISION.slice(3)}-BROWSER-WEB-LOCKS-COORDINATION-PROBE.json`;
const argValue = (argv, flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };
const hasFlag = (argv, flag) => argv.includes(flag);

export async function runProbe(options = {}) {
  const { result: observed, harness } = await runManagedBrowserPage({
    timeoutMs: options.timeoutMs,
    chromium: options.chromium,
    relaxPolicy: options.relaxPolicy,
    pagePath: '/web-locks-coordination-probe.html',
    pageTitle: 'BrowserRT Web Locks coordination probe',
    profilePrefix: 'browserrt-web-locks-',
    stderrTerms: ['locks', 'worker']
  }, async ({ evalJson, pageUrl, mark, timeoutMs }) => {
    const workerSource = `
      const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));
      self.onmessage = async (event) => {
        const { name, holdMs } = event.data;
        const hasLocks = typeof navigator.locks?.request === 'function';
        self.postMessage({ event: 'worker-ready', hasLocks });
        if (!hasLocks) return;
        await navigator.locks.request(name, async () => {
          self.postMessage({ event: 'worker-acquired' });
          await sleep(holdMs || 1);
          self.postMessage({ event: 'worker-releasing' });
        });
        self.postMessage({ event: 'worker-done' });
      };
    `;

    const expr = `(async()=>{
      const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));
      const events = [];
      const now = () => Math.round(performance.now() * 1000) / 1000;
      const record = (event, fields = {}) => events.push({ event, t: now(), ...fields });
      const baseName = 'browserrt-${REVISION}-' + Math.random().toString(36).slice(2);
      const page = { location: location.href, readyState: document.readyState, crossOriginIsolated, isSecureContext };
      const capabilities = {
        navigatorLocks: typeof navigator.locks,
        lockRequest: typeof navigator.locks?.request,
        lockQuery: typeof navigator.locks?.query,
        Worker: typeof Worker,
        Blob: typeof Blob,
        URLCreateObjectURL: typeof URL?.createObjectURL
      };
      if (typeof navigator.locks?.request !== 'function') {
        return JSON.stringify({ project: 'BrowserRT', revision: '${REVISION}', version: '${VERSION}', page, capabilities, available: false, events });
      }

      const exclusiveName = baseName + '-exclusive';
      let activeExclusive = 0;
      let maxExclusiveActive = 0;
      let exclusiveOverlap = false;
      const exclusiveOrder = [];
      const exclusiveHeld = (label, holdMs) => navigator.locks.request(exclusiveName, async () => {
        activeExclusive += 1;
        maxExclusiveActive = Math.max(maxExclusiveActive, activeExclusive);
        if (activeExclusive > 1) exclusiveOverlap = true;
        exclusiveOrder.push(label + ':enter');
        record('exclusive-enter', { label, activeExclusive });
        await sleep(holdMs);
        exclusiveOrder.push(label + ':exit');
        record('exclusive-exit', { label, activeExclusive });
        activeExclusive -= 1;
        return label;
      });
      const exclusiveA = exclusiveHeld('a', 65);
      await sleep(8);
      const exclusiveB = exclusiveHeld('b', 10);
      const exclusiveResults = await Promise.all([exclusiveA, exclusiveB]);

      const sharedName = baseName + '-shared';
      let activeShared = 0;
      let maxSharedActive = 0;
      let releaseShared;
      const releaseSharedPromise = new Promise((resolve) => { releaseShared = resolve; });
      const sharedHeld = (label) => navigator.locks.request(sharedName, { mode: 'shared' }, async () => {
        activeShared += 1;
        maxSharedActive = Math.max(maxSharedActive, activeShared);
        record('shared-enter', { label, activeShared });
        if (activeShared >= 2) releaseShared();
        await Promise.race([releaseSharedPromise, sleep(120)]);
        record('shared-exit', { label, activeShared });
        activeShared -= 1;
        return label;
      });
      const sharedResults = await Promise.all([sharedHeld('s1'), sharedHeld('s2')]);

      const workerName = baseName + '-worker';
      const workerMessages = [];
      let mainReleasedAt = null;
      const workerCode = ${JSON.stringify(workerSource)};
      const worker = new Worker(URL.createObjectURL(new Blob([workerCode], { type: 'text/javascript' })));
      const workerDone = new Promise((resolve, reject) => {
        const timer = setTimeout(() => reject(new Error('worker lock timeout')), 1200);
        worker.onmessage = (message) => {
          const row = { ...message.data, receivedAt: now() };
          workerMessages.push(row);
          record(row.event, { receivedAt: row.receivedAt });
          if (row.event === 'worker-done' || row.event === 'worker-ready' && row.hasLocks === false) {
            clearTimeout(timer);
            resolve(row);
          }
        };
        worker.onerror = (event) => {
          clearTimeout(timer);
          reject(new Error(event.message || 'worker error'));
        };
      });
      await navigator.locks.request(workerName, async () => {
        record('main-worker-lock-enter');
        worker.postMessage({ name: workerName, holdMs: 10 });
        await sleep(80);
        mainReleasedAt = now();
        record('main-worker-lock-release', { mainReleasedAt });
      });
      await workerDone;
      worker.terminate();
      const workerReady = workerMessages.find((row) => row.event === 'worker-ready');
      const workerAcquired = workerMessages.find((row) => row.event === 'worker-acquired');
      const workerAcquiredAfterMainRelease = Boolean(workerAcquired && mainReleasedAt !== null && workerAcquired.receivedAt >= mainReleasedAt);

      const query = await navigator.locks.query();
      return JSON.stringify({
        project: 'BrowserRT', revision: '${REVISION}', version: '${VERSION}', page, capabilities, available: true,
        exclusive: { name: exclusiveName, results: exclusiveResults, order: exclusiveOrder, maxExclusiveActive, exclusiveOverlap },
        shared: { name: sharedName, results: sharedResults, maxSharedActive },
        worker: { name: workerName, workerReady, workerAcquired, mainReleasedAt, workerAcquiredAfterMainRelease, messages: workerMessages },
        query: { heldCount: query.held?.length ?? null, pendingCount: query.pending?.length ?? null },
        events
      });
    })()`;
    const started = performance.now();
    const out = await evalJson(expr, timeoutMs);
    mark('web-locks-coordination-eval', started);
    out._pageUrl = pageUrl;
    return out;
  });

  assert.equal(observed.project, 'BrowserRT');
  assert.equal(observed.revision, REVISION);
  assert.equal(observed.version, VERSION);
  assert.equal(observed.page.location, observed._pageUrl);
  assert.equal(observed.available, true, 'navigator.locks.request must be available for this proof');
  assert.equal(observed.capabilities.lockRequest, 'function');
  assert.equal(observed.capabilities.lockQuery, 'function');
  assert.equal(observed.exclusive.maxExclusiveActive, 1, 'exclusive locks must not overlap');
  assert.equal(observed.exclusive.exclusiveOverlap, false);
  assert.deepEqual(observed.exclusive.results, ['a', 'b']);
  assert.ok(observed.shared.maxSharedActive >= 2, 'shared locks should co-hold the same name');
  assert.deepEqual(observed.shared.results.sort(), ['s1', 's2']);
  assert.equal(observed.worker.workerReady?.hasLocks, true, 'worker must expose navigator.locks');
  assert.ok(observed.worker.workerAcquired, 'worker should acquire after main lock releases');
  assert.equal(observed.worker.workerAcquiredAfterMainRelease, true, 'worker acquisition must wait for main exclusive lock release');

  return {
    project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1,
    probe_id: `${REVISION}-browser-web-locks-coordination-proof`, status: 'passed', generatedAt: new Date().toISOString(),
    purpose: 'Managed Chromium proof for Web Locks coordination semantics that BrowserRT treats as a risky mesh-tier prerequisite: exclusive same-name exclusion, shared co-holding, and same-origin window-to-worker lock handoff.',
    chromium: { executable: harness.chromiumExecutable, targetUrl: observed._pageUrl },
    observations: observed,
    harness: { policyRelaxation: harness.policyRelaxation, server: harness.server, profile: harness.profile, cdp: harness.cdp, timings: harness.timings, durationMs: harness.durationMs, chromeStderrSummary: harness.chromeStderrSummary, chromeStdoutBytes: harness.chromeStdoutBytes },
    claimsChecked: ['navigator.locks.request/query are available in the managed Chromium page', 'two exclusive same-origin requests for the same name do not overlap', 'two shared same-origin requests for the same name can co-hold', 'a dedicated worker waits for the main page to release an exclusive same-origin lock before acquiring it'],
    nonClaims: ['Chromium-in-cloudtainer proof only; not cross-browser conformance.', 'Does not prove multi-tab lifecycle correctness, crash recovery, background throttling behavior, or lock fairness under load.', 'Does not promote OPFS durability, quota, eviction, or exactly-once coordination claims.', 'Does not yet wire Web Locks into BrowserRT storage lanes; it proves a browser primitive needed by a future mesh/storage coordinator.']
  };
}

const argv = process.argv.slice(2);
const out = argValue(argv, '--json', DEFAULT_OUT);
const timeoutMs = Number(argValue(argv, '--timeout-ms', '24000'));
const chromium = argValue(argv, '--chromium', null);
const relaxPolicy = !hasFlag(argv, '--no-policy-relaxation');
try {
  const report = await runProbe({ timeoutMs, chromium, relaxPolicy });
  if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); console.log(out); }
  else console.log(JSON.stringify(report, null, 2));
} catch (error) {
  const report = { project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1, probe_id: `${REVISION}-browser-web-locks-coordination-proof`, status: 'failed', generatedAt: new Date().toISOString(), error: { name: error?.name || 'Error', message: error?.message || String(error), stack: error?.stack }, nonClaims: ['Failed browser Web Locks probe is not silently skipped; keep it outside broad release and run by id while developing mesh/storage coordination.'] };
  if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); console.error(out); }
  console.error(`[browser_web_locks_coordination_probe] FAIL: ${error?.stack || error}`); process.exitCode = 1;
}
