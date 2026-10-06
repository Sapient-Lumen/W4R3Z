#!/usr/bin/env node
import assert from 'node:assert/strict';
import { mkdir, mkdtemp, rm, writeFile } from 'node:fs/promises';
import { dirname, join } from 'node:path';
import { tmpdir } from 'node:os';
import { performance } from 'node:perf_hooks';
import { REVISION, VERSION } from '../src/browserrt.mjs';
import { runManagedBrowserPage, startProbeServer } from './browser_cdp_fixture.mjs';

const TASK_ID = 'browser:opfs-abrupt-kill-boundary-proof';
const DEFAULT_OUT = `artifacts/validation/REV${REVISION.slice(3)}-BROWSER-OPFS-ABRUPT-KILL-BOUNDARY-PROBE.json`;
const argValue = (argv, flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };
const hasFlag = (argv, flag) => argv.includes(flag);

function exprForAcknowledgedAndInterruptedWrite(prefix, acknowledgedCount, acknowledgedBytes, interruptedBytes, interruptedFirstChunkBytes) {
  return `(async()=>{
    const m=await import('/src/browserrt.mjs?rev=${REVISION}&slice=opfs-abrupt-kill-write');
    const rt=await m.boot({telemetry:'browser-cdp',proof:'${REVISION}',browserCdpHarness:true,opfsAsyncBlockStoreProof:true,opfsAbruptKillBoundaryProof:true});
    const prefix=${JSON.stringify(prefix)};
    const store=rt.opfsAsyncBlockStore({name:'${REVISION}-opfs-abrupt-kill-boundary-store',prefix});
    await store.cleanupForTest();
    const acknowledged=[];
    for (let i=0;i<${Number(acknowledgedCount)};i++) {
      const payload=new Uint8Array(${Number(acknowledgedBytes)});
      for (let j=0;j<payload.length;j++) payload[j]=(i*41+j*29+${REVISION.slice(3)}) & 255;
      const marker=new TextEncoder().encode('BrowserRT ${REVISION} acknowledged OPFS block before abrupt kill '+i+' / ');
      payload.set(marker.slice(0, Math.min(marker.length, payload.length)));
      const put=await store.put(payload,{label:'acknowledged-before-abrupt-kill-'+i});
      const got=await store.get(put.ref);
      const digest='sha256:'+await m.digestBytesHex(got);
      const verify=await store.verify(put.ref);
      acknowledged.push({index:i,ref:put.ref,hash:put.hash,digest:put.digest,bytes:put.bytes,duplicate:put.duplicate,path:put.path,readDigest:digest,verify});
    }

    const interruptedPayload=new Uint8Array(${Number(interruptedBytes)});
    for (let j=0;j<interruptedPayload.length;j++) interruptedPayload[j]=(j*31+${REVISION.slice(3)}*17+91) & 255;
    const interruptedMarker=new TextEncoder().encode('BrowserRT ${REVISION} interrupted unclosed OPFS stream candidate / ');
    interruptedPayload.set(interruptedMarker.slice(0, Math.min(interruptedMarker.length, interruptedPayload.length)));
    const interruptedHash=await m.digestBytesHex(interruptedPayload);
    const interruptedDigest='sha256:'+interruptedHash;
    const root=await navigator.storage.getDirectory();
    let dir=root;
    for (const part of prefix.split('/').filter(Boolean)) dir=await dir.getDirectoryHandle(part,{create:true});
    const d1=await dir.getDirectoryHandle(interruptedHash.slice(0,2),{create:true});
    const d2=await d1.getDirectoryHandle(interruptedHash.slice(2,4),{create:true});
    const estimateBeforeInterruptedWrite = await store.estimate().catch(e=>({error:String(e?.message||e)}));
    const file=await d2.getFileHandle(interruptedHash+'.blk',{create:true});
    const writable=await file.createWritable();
    const firstChunk=interruptedPayload.slice(0, ${Number(interruptedFirstChunkBytes)});
    let firstWriteSettled=false;
    let firstWriteError=null;
    const firstWritePromise=writable.write(firstChunk).then(()=>{ firstWriteSettled=true; return 'fulfilled'; }).catch(error=>{ firstWriteSettled=true; firstWriteError={name:error?.name||'Error',message:error?.message||String(error),code:error?.code||null}; return 'rejected'; });
    const firstWriteRace=await Promise.race([firstWritePromise, new Promise(resolve=>setTimeout(()=>resolve('pending-after-250ms'),250))]);
    window.__brtInterruptedWritable=writable;
    window.__brtInterruptedWritePromise=firstWritePromise;
    window.__brtInterruptedPayload=interruptedPayload;
    window.__brtInterruptedCandidate={hash:interruptedHash,digest:interruptedDigest,bytes:interruptedPayload.byteLength,firstChunkBytes:firstChunk.byteLength,path:prefix+'/'+interruptedHash.slice(0,2)+'/'+interruptedHash.slice(2,4)+'/'+interruptedHash+'.blk',writeCallIssued:true,firstWriteRace,firstWriteSettled,firstWriteError,closeCalled:false};
    console.log('BRT_OPFS_ABRUPT_KILL_CANDIDATE '+JSON.stringify(window.__brtInterruptedCandidate));
    const estimateBeforeKill = {skippedBecauseWritableLeftOpen:true, estimateBeforeInterruptedWrite};
    const snapshot=store.snapshot();
    const trace=rt.close();
    return JSON.stringify({project:'BrowserRT',revision:m.REVISION,version:m.VERSION,
      page:{location:location.href,readyState:document.readyState,crossOriginIsolated,isSecureContext,origin:location.origin},
      capabilities:m.detectCapabilities(globalThis),availableTierNames:m.availableCapabilityTierNames(m.detectCapabilities(globalThis)),
      prefix,acknowledged,interruptedCandidate:window.__brtInterruptedCandidate,estimateBeforeKill,snapshot,
      traceKinds:trace.map(e=>e.kind),normalizedTrace:trace.map(e=>({kind:e.kind,digest:e.digest,bytes:e.bytes,duplicate:e.duplicate,path:e.path,store:e.store,prefix:e.prefix,label:e.label})).filter(e=>e.kind)});
  })()`;
}

function exprForRestartInspection(prefix, acknowledged, interruptedCandidate) {
  return `(async()=>{
    const m=await import('/src/browserrt.mjs?rev=${REVISION}&slice=opfs-abrupt-kill-restart-inspect');
    const rt=await m.boot({telemetry:'browser-cdp',proof:'${REVISION}',browserCdpHarness:true,opfsAsyncBlockStoreProof:true,opfsAbruptKillBoundaryProof:true});
    const prefix=${JSON.stringify(prefix)};
    const store=rt.opfsAsyncBlockStore({name:'${REVISION}-opfs-abrupt-kill-boundary-store-read',prefix});
    const acknowledged=${JSON.stringify(acknowledged)};
    const interruptedCandidate=${JSON.stringify(interruptedCandidate)};
    const acknowledgedChecks=[];
    for (const row of acknowledged) {
      const hasBefore=await store.has(row.ref);
      const got=await store.get(row.ref);
      const digest='sha256:'+await m.digestBytesHex(got);
      const verify=await store.verify(row.ref);
      const deleted=await store.delete(row.ref);
      const hasAfter=await store.has(row.ref);
      acknowledgedChecks.push({index:row.index,digest:row.digest,hash:row.hash,hasBefore,bytes:got.byteLength,digestAfterRead:digest,verify,deleted,hasAfter});
    }

    const interruptedRef={kind:'block',id:'block:sha256:'+interruptedCandidate.hash,digest:interruptedCandidate.digest,hash:interruptedCandidate.hash,algorithm:'sha256',backend:'opfs-async-block-store-v0',path:interruptedCandidate.path,bytes:interruptedCandidate.bytes,label:'interrupted-unclosed-stream'};
    const interrupted={candidate:interruptedCandidate,hasBefore:null,disposition:null,bytes:null,digestAfterRead:null,verify:null,error:null,deleted:null,hasAfter:null};
    try {
      interrupted.hasBefore=await store.has(interruptedRef);
      if (!interrupted.hasBefore) {
        interrupted.disposition='absent-after-unclosed-interrupted-write';
      } else {
        try {
          const got=await store.get(interruptedRef);
          interrupted.bytes=got.byteLength;
          interrupted.digestAfterRead='sha256:'+await m.digestBytesHex(got);
          interrupted.verify=await store.verify(interruptedRef);
          interrupted.disposition=interrupted.digestAfterRead===interruptedCandidate.digest && interrupted.bytes===interruptedCandidate.bytes
            ? 'complete-valid-after-unclosed-interrupted-write'
            : 'unexpected-readable-digest-mismatch';
        } catch (error) {
          interrupted.error={name:error?.name||'Error',message:error?.message||String(error),code:error?.code||null,detail:error?.detail||null};
          interrupted.disposition=error?.code==='BRT_OPFS_BLOCK_CHECKSUM_MISMATCH'
            ? 'present-but-checksum-rejected-after-unclosed-interrupted-write'
            : 'present-but-read-rejected-after-unclosed-interrupted-write';
        }
        interrupted.deleted=await store.delete(interruptedRef).catch(error=>({error:{name:error?.name||'Error',message:error?.message||String(error),code:error?.code||null}}));
        interrupted.hasAfter=await store.has(interruptedRef).catch(error=>({error:{name:error?.name||'Error',message:error?.message||String(error),code:error?.code||null}}));
      }
    } catch (error) {
      interrupted.error={name:error?.name||'Error',message:error?.message||String(error),code:error?.code||null,detail:error?.detail||null};
      interrupted.disposition='inspection-error';
    }

    const cleanup=await store.cleanupForTest();
    const estimateAfterCleanup=await store.estimate().catch(e=>({error:String(e?.message||e)}));
    const snapshot=store.snapshot();
    const trace=rt.close();
    return JSON.stringify({project:'BrowserRT',revision:m.REVISION,version:m.VERSION,
      page:{location:location.href,readyState:document.readyState,crossOriginIsolated,isSecureContext,origin:location.origin},prefix,acknowledgedChecks,interrupted,cleanup,estimateAfterCleanup,snapshot,
      traceKinds:trace.map(e=>e.kind),normalizedTrace:trace.map(e=>({kind:e.kind,digest:e.digest,bytes:e.bytes,deleted:e.deleted,present:e.present,path:e.path,store:e.store,prefix:e.prefix,error:e.error?.code||e.error?.name||null})).filter(e=>e.kind)});
  })()`;
}

export async function runProbe(options = {}) {
  const prefix = options.prefix || `browserrt/${REVISION}/opfs-abrupt-kill-boundary-proof`;
  const acknowledgedCount = Number(options.acknowledgedCount || 2);
  const acknowledgedBytes = Number(options.acknowledgedBytes || 64 * 1024);
  const interruptedBytes = Number(options.interruptedBytes || 4 * 1024 * 1024);
  const interruptedFirstChunkBytes = Number(options.interruptedFirstChunkBytes || 256 * 1024);
  if (!Number.isFinite(acknowledgedCount) || acknowledgedCount < 1 || acknowledgedCount > 8) throw new Error('acknowledgedCount must be between 1 and 8');
  if (!Number.isFinite(acknowledgedBytes) || acknowledgedBytes < 1024 || acknowledgedBytes > 1024 * 1024) throw new Error('acknowledgedBytes must be between 1 KiB and 1 MiB');
  if (!Number.isFinite(interruptedBytes) || interruptedBytes < 1024 * 1024 || interruptedBytes > 16 * 1024 * 1024) throw new Error('interruptedBytes must be between 1 MiB and 16 MiB');
  if (!Number.isFinite(interruptedFirstChunkBytes) || interruptedFirstChunkBytes < 1024 || interruptedFirstChunkBytes > interruptedBytes) throw new Error('interruptedFirstChunkBytes must be positive and no larger than interruptedBytes');

  const profileDir = options.profileDir || await mkdtemp(join(tmpdir(), 'browserrt-opfs-abrupt-kill-profile-'));
  const server = await startProbeServer({ pagePath: '/opfs-abrupt-kill-boundary-probe.html', pageTitle: 'BrowserRT OPFS abrupt-kill boundary probe', allowedPrefixes: ['src/'] });
  const harnesses = {};
  try {
    const first = await runManagedBrowserPage({
      timeoutMs: options.timeoutMs,
      chromium: options.chromium,
      relaxPolicy: options.relaxPolicy,
      server,
      pagePath: server.pagePath,
      profileDir,
      keepProfile: true,
      teardownMode: 'kill',
      killWaitMs: 2500,
      profilePrefix: 'browserrt-opfs-abrupt-kill-boundary-',
      stderrTerms: ['opfs','file','storage','kill','crash']
    }, async ({ evalJson, pageUrl, mark, timeoutMs, profileDir: activeProfile, teardownMode }) => {
      const writeStart = performance.now();
      const write = await evalJson(exprForAcknowledgedAndInterruptedWrite(prefix, acknowledgedCount, acknowledgedBytes, interruptedBytes, interruptedFirstChunkBytes), timeoutMs);
      mark('browser-opfs-abrupt-kill-write-eval', writeStart);
      write._pageUrl = pageUrl;
      write._profileDir = activeProfile;
      write._teardownMode = teardownMode;
      return write;
    });
    harnesses.first = first.harness;

    const second = await runManagedBrowserPage({
      timeoutMs: options.timeoutMs,
      chromium: options.chromium,
      relaxPolicy: options.relaxPolicy,
      server,
      pagePath: server.pagePath,
      profileDir,
      keepProfile: true,
      profilePrefix: 'browserrt-opfs-abrupt-kill-boundary-',
      stderrTerms: ['opfs','file','storage','recovery','checksum']
    }, async ({ evalJson, pageUrl, mark, timeoutMs, profileDir: activeProfile }) => {
      const readStart = performance.now();
      const read = await evalJson(exprForRestartInspection(prefix, first.result.acknowledged, first.result.interruptedCandidate), timeoutMs);
      mark('browser-opfs-abrupt-kill-restart-inspection-eval', readStart);
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
    assert.equal(write.page.location, read.page.location, 'same local origin/page must be reused after abrupt browser kill');
    assert.equal(write._profileDir, profileDir);
    assert.equal(read._profileDir, profileDir);
    assert.equal(write._teardownMode, 'kill');
    assert.equal(harnesses.first.teardownMode, 'kill');
    assert.ok(harnesses.first.process?.requestedSignals?.some((signal) => signal.includes('SIGKILL')), 'first browser launch must be torn down with SIGKILL');
    assert.equal(harnesses.first.process?.timedOut, false, 'killed browser process group must close before timeout');
    assert.equal(write.acknowledged.length, acknowledgedCount);
    assert.equal(read.acknowledgedChecks.length, write.acknowledged.length);
    for (const row of write.acknowledged) {
      assert.equal(row.duplicate, false);
      assert.equal(row.readDigest, row.digest);
      assert.equal(row.verify.ok, true);
      assert.equal(row.bytes, acknowledgedBytes);
    }
    for (const row of read.acknowledgedChecks) {
      assert.equal(row.hasBefore, true);
      assert.equal(row.digestAfterRead, row.digest);
      assert.equal(row.verify.ok, true);
      assert.equal(row.bytes, acknowledgedBytes);
      assert.equal(row.deleted, true);
      assert.equal(row.hasAfter, false);
    }
    assert.equal(write.interruptedCandidate.closeCalled, false, 'interrupted candidate must intentionally leave FileSystemWritableFileStream unclosed');
    assert.equal(write.interruptedCandidate.firstChunkBytes, interruptedFirstChunkBytes);
    assert.equal(write.interruptedCandidate.bytes, interruptedBytes);
    assert.notEqual(read.interrupted.disposition, 'unexpected-readable-digest-mismatch', 'interrupted unclosed write must not read back as corrupt-but-accepted content');
    assert.notEqual(read.interrupted.disposition, 'inspection-error');
    if (read.interrupted.hasBefore === true && read.interrupted.disposition === 'complete-valid-after-unclosed-interrupted-write') {
      assert.equal(read.interrupted.digestAfterRead, write.interruptedCandidate.digest);
      assert.equal(read.interrupted.bytes, interruptedBytes);
    }
    if (read.interrupted.hasBefore === true && typeof read.interrupted.deleted === 'boolean') {
      assert.equal(read.interrupted.deleted, true, 'present interrupted candidate should be removed during cleanup path');
      assert.equal(read.interrupted.hasAfter, false);
    }
    assert.equal(read.cleanup, true);
    for (const kind of ['runtime:boot','storage:opfs-blockstore-create','storage:opfs-blockstore-open','storage:opfs-block-put','storage:opfs-block-get','storage:opfs-block-has','storage:opfs-block-delete','storage:opfs-block-cleanup','runtime:close']) {
      assert.ok([...write.traceKinds, ...read.traceKinds].includes(kind), `missing OPFS abrupt-kill trace kind ${kind}`);
    }

    return {
      project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1,
      probe_id: `${REVISION}-${TASK_ID}`, status: 'passed', generatedAt: new Date().toISOString(),
      purpose: 'Two-launch managed Chromium boundary proof for async OPFS across abrupt browser-process SIGKILL: acknowledged content-addressed blocks are read/verified after relaunch, while an intentionally unclosed in-flight write is either absent, complete-valid, or checksum/read rejected rather than silently accepted as corrupt content.',
      observations: {
        prefix,
        acknowledgedCount,
        acknowledgedBytes,
        interruptedBytes,
        interruptedFirstChunkBytes,
        sameOrigin: write.page.location === read.page.location,
        profileReused: write._profileDir === read._profileDir && read._profileDir === profileDir,
        write,
        restartInspection: read
      },
      harness: { server: { port: server.port, requestCount: server.requests.length, requests: server.requests.slice(0, 40) }, profile: { path: profileDir, reused: true, removedAfterProbe: true }, first: harnesses.first, second: harnesses.second, durationMs: (harnesses.first?.durationMs || 0) + (harnesses.second?.durationMs || 0) },
      claimsChecked: [
        'same local origin served both launches',
        'same temporary browser profile reused across an abrupt-kill restart boundary inside one command',
        'acknowledged OPFS blocks were written, read, and checksum-verified before browser-process SIGKILL',
        'the first browser process group was terminated with SIGKILL rather than clean browser shutdown',
        'acknowledged OPFS blocks were readable and checksum-verifiable after relaunch',
        'an intentionally unclosed in-flight OPFS write was not silently accepted as corrupt content-addressed data after relaunch',
        'acknowledged and interrupted-candidate namespaces were deleted/cleaned after restart inspection'
      ],
      nonClaims: [
        'Chromium-in-cloudtainer async OPFS abrupt-kill boundary proof only, not cross-browser conformance.',
        'This proves only acknowledged writes whose FileSystemWritableFileStream.close() and readback completed before SIGKILL, plus one intentionally unclosed write candidate; it does not prove general crash recovery.',
        'SIGKILL is not a power-loss, kernel panic, drive-cache flush, fsync, or transactional durability guarantee.',
        'No organic quota-pressure eviction, Storage Buckets, persistent-storage retention, multi-tab coordination, throughput, latency, or production durability claim.',
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
const timeoutMs = Number(argValue(argv, '--timeout-ms', '48000'));
const chromium = argValue(argv, '--chromium', null);
const prefix = argValue(argv, '--prefix', null);
const acknowledgedCount = Number(argValue(argv, '--acknowledged-count', '2'));
const acknowledgedBytes = Number(argValue(argv, '--acknowledged-bytes', String(64 * 1024)));
const interruptedBytes = Number(argValue(argv, '--interrupted-bytes', String(4 * 1024 * 1024)));
const interruptedFirstChunkBytes = Number(argValue(argv, '--interrupted-first-chunk-bytes', String(256 * 1024)));
const relaxPolicy = !hasFlag(argv, '--no-policy-relaxation');

try {
  const report = await runProbe({ timeoutMs, chromium, prefix, relaxPolicy, acknowledgedCount, acknowledgedBytes, interruptedBytes, interruptedFirstChunkBytes });
  if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); console.log(out); }
  else console.log(JSON.stringify(report, null, 2));
} catch (error) {
  const report = { project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1, probe_id: `${REVISION}-${TASK_ID}`, status: 'failed', generatedAt: new Date().toISOString(), error: { name: error?.name || 'Error', message: error?.message || String(error), stack: error?.stack }, nonClaims: ['Failed browser OPFS abrupt-kill boundary probe is not silently skipped; keep it outside broad release and debug by id.'] };
  if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); console.error(out); }
  console.error(`[browser_opfs_abrupt_kill_boundary_probe] FAIL: ${error?.stack || error}`);
  process.exitCode = 1;
}
