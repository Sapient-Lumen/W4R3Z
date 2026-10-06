#!/usr/bin/env node
import assert from 'node:assert/strict';
import { mkdir, writeFile, mkdtemp, rm } from 'node:fs/promises';
import { dirname, join } from 'node:path';
import { tmpdir } from 'node:os';
import { performance } from 'node:perf_hooks';
import { REVISION, VERSION } from '../src/browserrt.mjs';
import { runManagedBrowserPage, startProbeServer } from './browser_cdp_fixture.mjs';

const DEFAULT_OUT = `artifacts/validation/REV${REVISION.slice(3)}-BROWSER-OPFS-RESTART-PERSISTENCE-PROBE.json`;
const argValue = (argv, flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };
const hasFlag = (argv, flag) => argv.includes(flag);

function exprForWrite(prefix) {
  return `(async()=>{
    const m=await import('/src/browserrt.mjs?rev=${REVISION}&slice=opfs-restart-write');
    const rt=await m.boot({telemetry:'browser-cdp',proof:'${REVISION}',browserCdpHarness:true,opfsRestartPersistenceProof:true});
    const store=rt.opfsAsyncBlockStore({name:'${REVISION}-opfs-restart-store',prefix:${JSON.stringify(prefix)}});
    await store.cleanupForTest();
    const persistedBefore = navigator.storage?.persisted ? await navigator.storage.persisted().catch(e=>({error:String(e?.message||e)})) : null;
    const persistAttempt = navigator.storage?.persist ? await navigator.storage.persist().catch(e=>({error:String(e?.message||e)})) : null;
    const payload=new TextEncoder().encode('BrowserRT ${REVISION} OPFS restart persistence payload :: '+new Array(9).fill('restart').join('/'));
    const put=await store.put(payload,{label:'restart-payload'});
    const got=await store.get(put.ref);
    const verify=await store.verify(put.ref);
    const has=await store.has(put.ref);
    const estimate=await store.estimate();
    const snapshot=store.snapshot();
    const trace=rt.close();
    return JSON.stringify({project:'BrowserRT',revision:m.REVISION,version:m.VERSION,
      page:{location:location.href,readyState:document.readyState,crossOriginIsolated,isSecureContext},
      capabilities:m.detectCapabilities(globalThis),availableTierNames:m.availableCapabilityTierNames(m.detectCapabilities(globalThis)),
      prefix:${JSON.stringify(prefix)}, ref:put.ref, put, read:{bytes:got.byteLength,digest:await m.digestBytesHex(got)}, verify, has, estimate, persistedBefore, persistAttempt, snapshot,
      traceKinds:trace.map(e=>e.kind), normalizedTrace:trace.map(e=>({kind:e.kind,digest:e.digest,bytes:e.bytes,duplicate:e.duplicate,path:e.path,store:e.store,prefix:e.prefix})).filter(e=>e.kind)});
  })()`;
}

function exprForRestartRead(prefix, ref) {
  return `(async()=>{
    const m=await import('/src/browserrt.mjs?rev=${REVISION}&slice=opfs-restart-read');
    const rt=await m.boot({telemetry:'browser-cdp',proof:'${REVISION}',browserCdpHarness:true,opfsRestartPersistenceProof:true});
    const store=rt.opfsAsyncBlockStore({name:'${REVISION}-opfs-restart-store-read',prefix:${JSON.stringify(prefix)}});
    const ref=${JSON.stringify(ref)};
    const persistedAfter = navigator.storage?.persisted ? await navigator.storage.persisted().catch(e=>({error:String(e?.message||e)})) : null;
    const hasBefore=await store.has(ref);
    const got=await store.get(ref);
    const digest=await m.digestBytesHex(got);
    const verify=await store.verify(ref);
    const deleted=await store.delete(ref);
    const hasAfter=await store.has(ref);
    const cleanup=await store.cleanupForTest();
    const estimate=await store.estimate();
    const snapshot=store.snapshot();
    const trace=rt.close();
    return JSON.stringify({project:'BrowserRT',revision:m.REVISION,version:m.VERSION,
      page:{location:location.href,readyState:document.readyState,crossOriginIsolated,isSecureContext}, prefix:${JSON.stringify(prefix)}, ref,
      persistedAfter, hasBefore, restartRead:{bytes:got.byteLength,digest}, verify, deleted, hasAfter, cleanup, estimate, snapshot,
      traceKinds:trace.map(e=>e.kind), normalizedTrace:trace.map(e=>({kind:e.kind,digest:e.digest,bytes:e.bytes,deleted:e.deleted,path:e.path,store:e.store,prefix:e.prefix})).filter(e=>e.kind)});
  })()`;
}

export async function runProbe(options = {}) {
  const prefix = options.prefix || `browserrt/${REVISION}/opfs-restart-persistence-proof`;
  const profileDir = options.profileDir || await mkdtemp(join(tmpdir(), 'browserrt-opfs-restart-profile-'));
  const server = await startProbeServer({ pagePath: '/opfs-restart-persistence-probe.html', pageTitle: 'BrowserRT OPFS restart-persistence probe', allowedPrefixes: ['src/'] });
  const harnesses = {};
  try {
    const first = await runManagedBrowserPage({
      timeoutMs: options.timeoutMs, chromium: options.chromium, relaxPolicy: options.relaxPolicy, server,
      pagePath: server.pagePath, profileDir, keepProfile: true, profilePrefix: 'browserrt-opfs-restart-', stderrTerms: ['opfs','file','storage']
    }, async ({ evalJson, pageUrl, mark, timeoutMs, profileDir: activeProfile }) => {
      const writeStart = performance.now();
      const write = await evalJson(exprForWrite(prefix), timeoutMs);
      mark('browser-opfs-restart-write-eval', writeStart);
      write._pageUrl = pageUrl;
      write._profileDir = activeProfile;
      return write;
    });
    harnesses.first = first.harness;

    const second = await runManagedBrowserPage({
      timeoutMs: options.timeoutMs, chromium: options.chromium, relaxPolicy: options.relaxPolicy, server,
      pagePath: server.pagePath, profileDir, keepProfile: true, profilePrefix: 'browserrt-opfs-restart-', stderrTerms: ['opfs','file','storage']
    }, async ({ evalJson, pageUrl, mark, timeoutMs, profileDir: activeProfile }) => {
      const readStart = performance.now();
      const read = await evalJson(exprForRestartRead(prefix, first.result.ref), timeoutMs);
      mark('browser-opfs-restart-read-eval', readStart);
      read._pageUrl = pageUrl;
      read._profileDir = activeProfile;
      return read;
    });
    harnesses.second = second.harness;

    const write = first.result;
    const read = second.result;
    assert.equal(write.project, 'BrowserRT');
    assert.equal(read.project, 'BrowserRT');
    assert.equal(write.revision, REVISION);
    assert.equal(read.revision, REVISION);
    assert.equal(write.version, VERSION);
    assert.equal(read.version, VERSION);
    assert.equal(write.page.crossOriginIsolated, true);
    assert.equal(read.page.crossOriginIsolated, true);
    assert.equal(write.page.location, read.page.location, 'same local origin/page must be reused');
    assert.equal(write._profileDir, profileDir);
    assert.equal(read._profileDir, profileDir);
    assert.equal(write.has, true);
    assert.equal(write.verify.ok, true);
    assert.equal(write.read.digest, write.put.hash);
    assert.equal(read.hasBefore, true);
    assert.equal(read.restartRead.digest, write.put.hash);
    assert.equal(read.restartRead.bytes, write.put.bytes);
    assert.equal(read.verify.ok, true);
    assert.equal(read.deleted, true);
    assert.equal(read.hasAfter, false);
    for (const kind of ['runtime:boot','storage:opfs-blockstore-create','storage:opfs-blockstore-open','storage:opfs-block-put','storage:opfs-block-get','storage:opfs-block-has','storage:opfs-block-delete','runtime:close']) {
      assert.ok([...write.traceKinds, ...read.traceKinds].includes(kind), `missing OPFS restart trace kind ${kind}`);
    }

    return {
      project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1,
      probe_id: `${REVISION}-browser-opfs-restart-persistence-proof`, status: 'passed', generatedAt: new Date().toISOString(),
      purpose: 'Two-launch managed Chromium proof for async OPFS content-addressed block-store restart persistence: write/verify in one browser process, clean teardown, relaunch with same temporary profile and same local origin, read/verify/delete/cleanup in the second process.',
      observations: { prefix, sameOrigin: write.page.location === read.page.location, profileReused: write._profileDir === read._profileDir && read._profileDir === profileDir, write, restartRead: read },
      harness: { server: { port: server.port, requestCount: server.requests.length, requests: server.requests.slice(0, 30) }, profile: { path: profileDir, reused: true, removedAfterProbe: true }, first: harnesses.first, second: harnesses.second, durationMs: (harnesses.first?.durationMs || 0) + (harnesses.second?.durationMs || 0) },
      claimsChecked: [
        'same local origin served both launches',
        'same temporary profile reused across two managed Chromium launches inside one command',
        'OPFS block written, immediately read, and verified before teardown',
        'OPFS block read and verified after clean browser-process restart',
        'OPFS block deleted and namespace cleaned after restart readback',
        'StorageManager.persist() observations are recorded as environment facts only'
      ],
      nonClaims: [
        'Chromium-in-cloudtainer async OPFS restart-persistence proof only, not cross-browser conformance.',
        'Clean process restart with the same temporary profile is not crash recovery, power-loss recovery, fsync durability, quota-pressure, eviction, storage-bucket, or multi-tab coordination evidence.',
        'StorageManager.persist() observations are recorded as environment facts only; this probe does not require or claim persistent-storage permission.',
        'Not a throughput, latency, capacity, retention-period, or production durability benchmark.',
        'Temporary managed-policy relaxation is local to each browser launch and restored during teardown.'
      ]
    };
  } finally {
    await server.close();
    await rm(profileDir, { recursive: true, force: true });
  }
}

const argv = process.argv.slice(2);
const out = argValue(argv, '--json', DEFAULT_OUT);
const timeoutMs = Number(argValue(argv, '--timeout-ms', '42000'));
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
  const report = { project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1, probe_id: `${REVISION}-browser-opfs-restart-persistence-proof`, status: 'failed', generatedAt: new Date().toISOString(), error: { name: error?.name || 'Error', message: error?.message || String(error), stack: error?.stack }, nonClaims: ['Failed browser OPFS restart-persistence probe is not silently skipped; keep it outside broad release and debug by id.'] };
  if (out) {
    await mkdir(dirname(out), { recursive: true });
    await writeFile(out, JSON.stringify(report, null, 2) + '\n');
    console.error(out);
  }
  console.error(`[browser_opfs_restart_persistence_probe] FAIL: ${error?.stack || error}`);
  process.exitCode = 1;
}
