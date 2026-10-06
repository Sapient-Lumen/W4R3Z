#!/usr/bin/env node
import assert from 'node:assert/strict';
import { mkdir, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import { performance } from 'node:perf_hooks';
import { REVISION, VERSION, boot } from '../src/browserrt.mjs';

const MANIFEST_ID = 'storage:journal-recovery-proof';
const DEFAULT_OUT = `artifacts/validation/REV${REVISION.slice(3)}-JOURNAL-RECOVERY-PROBE.json`;
const argValue = (argv, flag, fallback = null) => {
  const i = argv.indexOf(flag);
  return i >= 0 ? argv[i + 1] : fallback;
};
const sameBytes = (a, b) => a.byteLength === b.byteLength && a.every((value, i) => value === b[i]);

async function expectMissing(store, ref) {
  try { await store.get(ref); return false; } catch (error) { return error.code === 'BRT_STORAGE_NOT_FOUND' || /not found/i.test(error.message); }
}

async function main() {
  const out = argValue(process.argv.slice(2), '--json', DEFAULT_OUT);
  const started = performance.now();
  const rt = await boot({ telemetry: 'always', journalRecoveryProbe: true });
  const store = rt.journaledBlockStore({ name: 'rev0025-journal-fake-store', provider: 'journaled-memory-fake-provider-v0' });

  const alphaBytes = new TextEncoder().encode('alpha before first checkpoint');
  const betaBytes = new TextEncoder().encode('beta before first checkpoint');
  const gammaBytes = new TextEncoder().encode('gamma after first checkpoint');
  const deltaBytes = new TextEncoder().encode('delta after second checkpoint');

  const alpha = await store.put(alphaBytes, { label: 'alpha' });
  const beta = await store.put(betaBytes, { label: 'beta' });
  const oldManifest = await store.checkpoint({ label: 'old-checkpoint' });
  const gamma = await store.put(gammaBytes, { label: 'gamma' });
  await store.delete(alpha.ref);
  const latestManifest = await store.checkpoint({ label: 'latest-checkpoint' });
  const delta = await store.put(deltaBytes, { label: 'delta' });
  const journalWithTornTail = [...store.exportJournal(), store.tornRecordForTest()];

  const latestRecovery = await rt.recoverJournaledBlockStore({ manifest: latestManifest, journal: journalWithTornTail, name: 'rev0025-latest-recovery' });
  const olderRecovery = await rt.recoverJournaledBlockStore({ manifest: oldManifest, journal: journalWithTornTail, name: 'rev0025-old-recovery' });
  const repeatRecovery = await rt.recoverJournaledBlockStore({ manifest: latestManifest, journal: journalWithTornTail, name: 'rev0025-repeat-recovery' });

  const betaRecoveredLatest = sameBytes(await latestRecovery.store.get(beta.ref), betaBytes);
  const gammaRecoveredLatest = sameBytes(await latestRecovery.store.get(gamma.ref), gammaBytes);
  const deltaRecoveredLatest = sameBytes(await latestRecovery.store.get(delta.ref), deltaBytes);
  const deletedBlockNotRecoveredFromLatestCheckpoint = await expectMissing(latestRecovery.store, alpha.ref);
  const deletedBlockNotRecoveredFromOlderCheckpoint = await expectMissing(olderRecovery.store, alpha.ref);
  const betaRecoveredOlder = sameBytes(await olderRecovery.store.get(beta.ref), betaBytes);
  const gammaRecoveredOlder = sameBytes(await olderRecovery.store.get(gamma.ref), gammaBytes);
  const deltaRecoveredOlder = sameBytes(await olderRecovery.store.get(delta.ref), deltaBytes);

  const corruptManifest = JSON.parse(JSON.stringify(latestManifest));
  corruptManifest.payload.blocks[0].bytes = 123456;
  let corruptManifestRejected = false;
  try { await rt.recoverJournaledBlockStore({ manifest: corruptManifest, journal: journalWithTornTail, name: 'rev0025-corrupt-manifest-recovery' }); }
  catch (error) { corruptManifestRejected = error.code === 'BRT_STORAGE_BAD_MANIFEST_CHECKSUM' || /checksum/i.test(error.message); }

  const latestView = latestRecovery.store.manifestView();
  const repeatView = repeatRecovery.store.manifestView();
  const repeatRecoveryIdempotent = latestView.seq === repeatView.seq && JSON.stringify(latestView.blocks) === JSON.stringify(repeatView.blocks);
  const olderCheckpointReplaysMore = olderRecovery.recovery.appliedJournalRecords > latestRecovery.recovery.appliedJournalRecords;
  const tornTailIgnoredLatest = latestRecovery.recovery.ignoredTailRecords === 1;

  assert.equal(betaRecoveredLatest, true);
  assert.equal(gammaRecoveredLatest, true);
  assert.equal(deltaRecoveredLatest, true);
  assert.equal(deletedBlockNotRecoveredFromLatestCheckpoint, true);
  assert.equal(deletedBlockNotRecoveredFromOlderCheckpoint, true);
  assert.equal(betaRecoveredOlder, true);
  assert.equal(gammaRecoveredOlder, true);
  assert.equal(deltaRecoveredOlder, true);
  assert.equal(olderCheckpointReplaysMore, true);
  assert.equal(tornTailIgnoredLatest, true);
  assert.equal(corruptManifestRejected, true);
  assert.equal(repeatRecoveryIdempotent, true);

  const traceKinds = rt.trace.kinds();
  for (const kind of ['storage:journaled-blockstore-create', 'storage:journal-append', 'storage:manifest-checkpoint', 'storage:manifest-recover', 'storage:journal-replay-apply', 'storage:journal-torn-record-ignored', 'storage:journal-recover', 'storage:manifest-recover-error']) {
    assert.equal(traceKinds.includes(kind), true, `missing trace kind ${kind}`);
  }

  const report = {
    project: 'BrowserRT',
    revision: REVISION,
    version: VERSION,
    probe: 'journal-manifest-fake-recovery-proof',
    status: 'passed',
    generatedAt: new Date().toISOString(),
    durationMs: Math.round(performance.now() - started),
    observations: {
      manifestId: MANIFEST_ID,
      oldManifestSeq: oldManifest.seq,
      latestManifestSeq: latestManifest.seq,
      journalRecordsExported: store.exportJournal().length,
      latestRecoveryAppliedJournalRecords: latestRecovery.recovery.appliedJournalRecords,
      oldRecoveryAppliedJournalRecords: olderRecovery.recovery.appliedJournalRecords,
      latestAppliedJournalSeqs: latestRecovery.recovery.appliedJournalSeqs,
      olderAppliedJournalSeqs: olderRecovery.recovery.appliedJournalSeqs,
      deletedBlockNotRecoveredFromLatestCheckpoint,
      deletedBlockNotRecoveredFromOlderCheckpoint,
      olderCheckpointReplaysMore,
      tornTailIgnoredLatest,
      corruptManifestRejected,
      repeatRecoveryIdempotent,
      betaRecovered: betaRecoveredLatest && betaRecoveredOlder,
      gammaRecovered: gammaRecoveredLatest && gammaRecoveredOlder,
      deltaRecovered: deltaRecoveredLatest && deltaRecoveredOlder,
      traceKinds
    },
    manifests: {
      old: { seq: oldManifest.seq, checksum: oldManifest.checksum, blockCount: oldManifest.payload.blockCount },
      latest: { seq: latestManifest.seq, checksum: latestManifest.checksum, blockCount: latestManifest.payload.blockCount }
    },
    recovery: {
      latest: latestRecovery.recovery,
      older: olderRecovery.recovery
    },
    nonClaims: [
      'JournaledMemoryBlockStore is a fake/in-memory recovery proof, not durable storage.',
      'This probe does not prove OPFS recovery, browser restart recovery, fsync/flush semantics, quota or eviction behavior, compaction, or multi-tab safety.',
      'The baby journal and manifest formats are deliberately provisional and should remain provider-versioned.'
    ]
  };

  if (out) {
    await mkdir(dirname(out), { recursive: true });
    await writeFile(out, JSON.stringify(report, null, 2) + '\n');
    console.log(out);
  } else {
    console.log(JSON.stringify(report, null, 2));
  }
}

await main();
