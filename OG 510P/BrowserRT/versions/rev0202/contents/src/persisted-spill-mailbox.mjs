function toOwnedUint8Array(value) {
  if (typeof value === 'string') return new TextEncoder().encode(value);
  if (value instanceof Uint8Array) return new Uint8Array(value);
  if (value instanceof ArrayBuffer) return new Uint8Array(value.slice(0));
  if (ArrayBuffer.isView(value)) return new Uint8Array(value.buffer.slice(value.byteOffset, value.byteOffset + value.byteLength));
  throw new Error('PersistedSpillMailbox payload must be a string, ArrayBuffer, Uint8Array, or ArrayBuffer view');
}
function checksum32(value) {
  const bytes = typeof value === 'string' ? new TextEncoder().encode(value) : new Uint8Array(value);
  let sum = 0x811c9dc5;
  for (const byte of bytes) {
    sum ^= byte;
    sum = Math.imul(sum, 0x01000193) >>> 0;
  }
  return sum >>> 0;
}
function payloadChecksum(payload) {
  return `brt32:${checksum32(canonicalJson(payload)).toString(16).padStart(8, '0')}`;
}
function canonicalJson(value) {
  if (value === null || typeof value !== 'object') return JSON.stringify(value);
  if (Array.isArray(value)) return `[${value.map(canonicalJson).join(',')}]`;
  const keys = Object.keys(value).sort();
  return `{${keys.map((key) => `${JSON.stringify(key)}:${canonicalJson(value[key])}`).join(',')}}`;
}
function cloneJson(value) {
  return JSON.parse(JSON.stringify(value));
}
function freezeEntry(entry) {
  return Object.freeze({ ...entry, ref: entry.ref ? cloneJson(entry.ref) : null });
}
function assertProvider(provider) {
  for (const method of ['put', 'get', 'delete', 'snapshot']) {
    if (!provider || typeof provider[method] !== 'function') throw new Error(`PersistedSpillMailbox requires a provider with ${method}()`);
  }
}
function storageCode(error) {
  return error?.code || error?.name || 'BRT_STORAGE_UNKNOWN';
}
function refDigest(ref) {
  if (!ref) return null;
  if (typeof ref === 'string') return ref.startsWith('sha256:') ? ref : `sha256:${ref}`;
  if (typeof ref.digest === 'string') return ref.digest;
  if (typeof ref.hash === 'string') return `sha256:${ref.hash}`;
  return null;
}
function compactRef(ref) {
  const digest = refDigest(ref);
  return digest ? Object.freeze({ digest, ref: cloneJson(ref) }) : null;
}
function entryFromRecord(payload) {
  return {
    seq: payload.seq,
    bytes: payload.bytes,
    checksum32: payload.checksum32,
    ref: cloneJson(payload.ref),
    label: payload.label ?? null,
    hot: Boolean(payload.hot),
    deliveryCount: payload.deliveryCount || 0
  };
}
function removeFirstBySeq(rows, seq) {
  const index = rows.findIndex((row) => row.seq === seq);
  if (index < 0) return null;
  return rows.splice(index, 1)[0];
}
export class PersistedSpillMailbox {
  #queue = [];
  #pending = new Map();
  #journal = [];
  #retainedRefs = new Map();
  #opSeq = 0;
  #nextSeq = 1;
  #nextPending = 1;
  #memoryUsed = 0;
  #trace;
  constructor({ label = 'persisted-spill-mailbox', provider, memoryCapacityBytes = 1024, maxFrameBytes = 64 * 1024, trace = null, deleteBlockOnAck = true } = {}) {
    assertProvider(provider);
    if (!Number.isInteger(memoryCapacityBytes) || memoryCapacityBytes < 0) throw new Error('memoryCapacityBytes must be a non-negative integer');
    if (!Number.isInteger(maxFrameBytes) || maxFrameBytes < 1) throw new Error('maxFrameBytes must be a positive integer');
    this.label = label;
    this.provider = provider;
    this.memoryCapacityBytes = memoryCapacityBytes;
    this.maxFrameBytes = maxFrameBytes;
    this.deleteBlockOnAck = Boolean(deleteBlockOnAck);
    this.stats = { enqueued: 0, hotEnqueued: 0, spilledEnqueued: 0, delivered: 0, acked: 0, rejected: 0, oversizeRejected: 0, spillRejected: 0, blockDeletes: 0, checkpoints: 0, recoveries: 0, pendingRequeued: 0, tornRecordsIgnored: 0, compactions: 0, compactDryRuns: 0, compactedBlocks: 0, compactDeleteMisses: 0 };
    this.#trace = trace;
    this.#trace?.emit('mailbox:persisted-create', { label: this.label, provider: provider.provider || provider.name || 'unknown-provider', memoryCapacityBytes, maxFrameBytes, deleteBlockOnAck: this.deleteBlockOnAck });
  }
  async enqueue(payload, { seq = null, label = null } = {}) {
    const bytes = toOwnedUint8Array(payload);
    const frameSeq = seq ?? this.#nextSeq++;
    if (bytes.byteLength > this.maxFrameBytes) {
      this.stats.rejected += 1;
      this.stats.oversizeRejected += 1;
      this.#trace?.emit('mailbox:persisted-reject', { label: this.label, seq: frameSeq, bytes: bytes.byteLength, reason: 'oversize', maxFrameBytes: this.maxFrameBytes });
      return Object.freeze({ disposition: 'rejected-oversize', reason: 'oversize', seq: frameSeq, bytes: bytes.byteLength });
    }
    let put;
    try {
      put = await this.provider.put(bytes, { label: label ?? `${this.label}:seq:${frameSeq}` });
    } catch (error) {
      this.stats.rejected += 1;
      this.stats.spillRejected += 1;
      const code = storageCode(error);
      this.#trace?.emit('mailbox:persisted-reject', { label: this.label, seq: frameSeq, bytes: bytes.byteLength, reason: code });
      return Object.freeze({ disposition: 'rejected-provider', reason: code, seq: frameSeq, bytes: bytes.byteLength });
    }
    const hot = this.#memoryUsed + bytes.byteLength <= this.memoryCapacityBytes;
    if (hot) this.#memoryUsed += bytes.byteLength;
    const entry = { seq: frameSeq, bytes: bytes.byteLength, checksum32: checksum32(bytes), ref: put.ref, label, hot, payload: hot ? new Uint8Array(bytes) : null, deliveryCount: 0 };
    this.#rememberRef(put.ref);
    await this.#append('enqueue', { seq: frameSeq, bytes: entry.bytes, checksum32: entry.checksum32, ref: put.ref, label, hot, deliveryCount: 0 });
    this.#queue.push(entry);
    this.#nextSeq = Math.max(this.#nextSeq, frameSeq + 1);
    this.stats.enqueued += 1;
    if (hot) this.stats.hotEnqueued += 1;
    else this.stats.spilledEnqueued += 1;
    this.#trace?.emit('mailbox:persisted-enqueue', { label: this.label, seq: frameSeq, bytes: entry.bytes, source: hot ? 'hot-cache' : 'spill-only', queueDepth: this.#queue.length, pendingCount: this.#pending.size, opSeq: this.#opSeq });
    return Object.freeze({ disposition: hot ? 'hot-persisted' : 'spilled-persisted', seq: frameSeq, bytes: entry.bytes, checksum32: entry.checksum32, ref: put.ref, opSeq: this.#opSeq });
  }
  async dequeue({ consumerId = 'consumer' } = {}) {
    const entry = this.#queue.shift();
    if (!entry) {
      this.#trace?.emit('mailbox:persisted-dequeue-empty', { label: this.label, pendingCount: this.#pending.size });
      return null;
    }
    if (entry.hot && entry.payload) this.#memoryUsed -= entry.payload.byteLength;
    const payload = entry.payload ? new Uint8Array(entry.payload) : await this.provider.get(entry.ref);
    const pendingId = `pending:${this.#nextPending++}`;
    entry.deliveryCount += 1;
    const pending = { ...entry, pendingId, consumerId, deliveredAt: Date.now(), payload: null };
    this.#pending.set(pendingId, pending);
    await this.#append('deliver', { seq: entry.seq, pendingId, consumerId, deliveryCount: entry.deliveryCount, ref: entry.ref });
    this.stats.delivered += 1;
    this.#trace?.emit('mailbox:persisted-deliver', { label: this.label, seq: entry.seq, pendingId, consumerId, bytes: entry.bytes, deliveryCount: entry.deliveryCount, queueDepth: this.#queue.length, pendingCount: this.#pending.size, opSeq: this.#opSeq });
    return Object.freeze({ pendingId, consumerId, seq: entry.seq, bytes: entry.bytes, checksum32: entry.checksum32, deliveryCount: entry.deliveryCount, payload, ref: entry.ref });
  }
  async ack(pendingId, { deleteBlock = this.deleteBlockOnAck } = {}) {
    const pending = this.#pending.get(pendingId);
    if (!pending) {
      this.#trace?.emit('mailbox:persisted-ack-miss', { label: this.label, pendingId });
      return false;
    }
    this.#pending.delete(pendingId);
    let deletedBlock = false;
    if (deleteBlock) {
      deletedBlock = await this.provider.delete(pending.ref);
      if (deletedBlock) {
        this.stats.blockDeletes += 1;
        this.#forgetRef(pending.ref);
      }
    }
    await this.#append('ack', { seq: pending.seq, pendingId, ref: pending.ref, deletedBlock });
    this.stats.acked += 1;
    this.#trace?.emit('mailbox:persisted-ack', { label: this.label, seq: pending.seq, pendingId, deletedBlock, pendingCount: this.#pending.size, opSeq: this.#opSeq });
    return true;
  }
  async checkpoint({ label = null } = {}) {
    const payload = {
      kind: 'persisted-spill-mailbox-manifest-payload',
      version: 1,
      label: this.label,
      provider: this.provider.provider || this.provider.name || 'unknown-provider',
      checkpointLabel: label,
      opSeq: this.#opSeq,
      nextSeq: this.#nextSeq,
      nextPending: this.#nextPending,
      memoryCapacityBytes: this.memoryCapacityBytes,
      maxFrameBytes: this.maxFrameBytes,
      deleteBlockOnAck: this.deleteBlockOnAck,
      queue: this.#queue.map((entry) => ({ seq: entry.seq, bytes: entry.bytes, checksum32: entry.checksum32, ref: cloneJson(entry.ref), label: entry.label, hot: false, deliveryCount: entry.deliveryCount })),
      pending: [...this.#pending.values()].map((entry) => ({ pendingId: entry.pendingId, consumerId: entry.consumerId, seq: entry.seq, bytes: entry.bytes, checksum32: entry.checksum32, ref: cloneJson(entry.ref), label: entry.label, deliveryCount: entry.deliveryCount })),
      retainedRefs: [...this.#retainedRefs.values()].map((row) => cloneJson(row.ref))
    };
    const manifest = Object.freeze({ kind: 'persisted-spill-mailbox-manifest', version: 1, opSeq: this.#opSeq, checksum: payloadChecksum(payload), payload });
    this.stats.checkpoints += 1;
    this.#trace?.emit('mailbox:persisted-checkpoint', { label: this.label, opSeq: manifest.opSeq, queueDepth: payload.queue.length, pendingCount: payload.pending.length, checksum: manifest.checksum, checkpointLabel: label });
    return manifest;
  }
  exportJournal() {
    return this.#journal.map(cloneJson);
  }
  tornRecordForTest(fields = {}) {
    return { opSeq: this.#opSeq + 1, op: fields.op || 'enqueue', payload: { seq: fields.seq ?? 9999, bytes: 1, checksum32: 0, ref: null }, checksum: 'brt32:bad-tail-checksum' };
  }
  snapshot() {
    const liveDigests = this.#liveRefDigestSet();
    return Object.freeze({ label: this.label, provider: this.provider.provider || this.provider.name || 'unknown-provider', opSeq: this.#opSeq, nextSeq: this.#nextSeq, queueDepth: this.#queue.length, pendingCount: this.#pending.size, memoryCapacityBytes: this.memoryCapacityBytes, memoryUsed: this.#memoryUsed, stats: { ...this.stats }, queueSeqs: this.#queue.map((entry) => entry.seq), pendingSeqs: [...this.#pending.values()].map((entry) => entry.seq), retainedBlockCount: this.#retainedRefs.size, retainedBlockDigests: [...this.#retainedRefs.keys()].sort(), liveBlockDigests: [...liveDigests].sort(), providerSnapshot: this.provider.snapshot() });
  }
  async compact({ dryRun = false, reason = 'manual', includeProviderManifest = true } = {}) {
    const live = this.#liveRefDigestSet();
    const candidates = new Map();
    for (const [digest, row] of this.#retainedRefs.entries()) {
      if (!live.has(digest)) candidates.set(digest, row.ref);
    }
    if (includeProviderManifest && typeof this.provider.manifest === 'function') {
      const manifest = this.provider.manifest();
      for (const block of manifest.blocks || []) {
        const digest = block.digest;
        if (!live.has(digest) && this.#retainedRefs.has(digest)) candidates.set(digest, this.#retainedRefs.get(digest).ref);
      }
    }
    const digests = [...candidates.keys()].sort();
    this.#trace?.emit('mailbox:persisted-compact-start', { label: this.label, dryRun: Boolean(dryRun), reason, candidateCount: digests.length, liveCount: live.size, retainedBlockCount: this.#retainedRefs.size });
    if (dryRun) {
      this.stats.compactDryRuns += 1;
      return Object.freeze({ dryRun: true, reason, candidateCount: digests.length, candidates: digests, deleted: 0, deleteMisses: 0, liveCount: live.size, retainedBlockCount: this.#retainedRefs.size });
    }
    let deleted = 0;
    let deleteMisses = 0;
    for (const digest of digests) {
      const ref = candidates.get(digest);
      const ok = await this.provider.delete(ref);
      if (ok) deleted += 1;
      else deleteMisses += 1;
      this.#forgetRef(ref);
      await this.#append('compact-delete', { digest, ref, deleted: Boolean(ok), reason });
      this.#trace?.emit('mailbox:persisted-compact-delete', { label: this.label, digest, deleted: Boolean(ok), reason });
    }
    this.stats.compactions += 1;
    this.stats.compactedBlocks += deleted;
    this.stats.compactDeleteMisses += deleteMisses;
    const result = Object.freeze({ dryRun: false, reason, candidateCount: digests.length, candidates: digests, deleted, deleteMisses, liveCount: live.size, retainedBlockCount: this.#retainedRefs.size });
    this.#trace?.emit('mailbox:persisted-compact', { label: this.label, ...result });
    return result;
  }
  #rememberRef(ref) {
    const row = compactRef(ref);
    if (row) this.#retainedRefs.set(row.digest, row);
  }
  #forgetRef(ref) {
    const digest = refDigest(ref);
    if (digest) this.#retainedRefs.delete(digest);
  }
  #liveRefDigestSet() {
    const live = new Set();
    for (const entry of this.#queue) {
      const digest = refDigest(entry.ref);
      if (digest) live.add(digest);
    }
    for (const entry of this.#pending.values()) {
      const digest = refDigest(entry.ref);
      if (digest) live.add(digest);
    }
    return live;
  }
  async #append(op, payload) {
    const record = { opSeq: this.#opSeq + 1, op, payload: cloneJson(payload) };
    record.checksum = payloadChecksum({ opSeq: record.opSeq, op: record.op, payload: record.payload });
    this.#opSeq = record.opSeq;
    this.#journal.push(record);
    this.#trace?.emit('mailbox:persisted-journal-append', { label: this.label, opSeq: record.opSeq, op, seq: payload.seq ?? null });
    return record;
  }
  static async recover({ manifest, journal = [], provider, trace = null, requeuePending = true, strictTail = false, label = null } = {}) {
    assertProvider(provider);
    if (!manifest || manifest.kind !== 'persisted-spill-mailbox-manifest') {
      trace?.emit('mailbox:persisted-recover-error', { reason: 'missing-or-unsupported-manifest' });
      throw Object.assign(new Error('Missing or unsupported persisted-spill mailbox manifest'), { code: 'BRT_MAILBOX_BAD_MANIFEST' });
    }
    const expected = payloadChecksum(manifest.payload);
    if (expected !== manifest.checksum) {
      trace?.emit('mailbox:persisted-recover-error', { reason: 'checksum-mismatch', expected, actual: manifest.checksum, opSeq: manifest.opSeq });
      throw Object.assign(new Error('Persisted-spill mailbox manifest checksum mismatch'), { code: 'BRT_MAILBOX_BAD_MANIFEST_CHECKSUM' });
    }
    const box = new PersistedSpillMailbox({
      label: label || manifest.payload.label || 'recovered-persisted-spill-mailbox',
      provider,
      memoryCapacityBytes: manifest.payload.memoryCapacityBytes || 0,
      maxFrameBytes: manifest.payload.maxFrameBytes || 64 * 1024,
      deleteBlockOnAck: manifest.payload.deleteBlockOnAck !== false,
      trace
    });
    box.#opSeq = manifest.payload.opSeq || 0;
    box.#nextSeq = manifest.payload.nextSeq || 1;
    box.#nextPending = manifest.payload.nextPending || 1;
    box.#queue = (manifest.payload.queue || []).map((row) => ({ ...entryFromRecord(row), payload: null, hot: false }));
    box.#pending = new Map((manifest.payload.pending || []).map((row) => [row.pendingId, { ...entryFromRecord(row), pendingId: row.pendingId, consumerId: row.consumerId, payload: null, deliveredAt: Date.now() }]));
    const retainedRefs = manifest.payload.retainedRefs || [...box.#queue.map((row) => row.ref), ...[...box.#pending.values()].map((row) => row.ref)];
    for (const ref of retainedRefs) box.#rememberRef(ref);
    trace?.emit('mailbox:persisted-manifest-recover', { label: box.label, opSeq: box.#opSeq, queueDepth: box.#queue.length, pendingCount: box.#pending.size, checksum: manifest.checksum });
    let ignoredTailRecords = 0;
    const applied = [];
    const sorted = journal.map(cloneJson).sort((a, b) => (a.opSeq || 0) - (b.opSeq || 0));
    for (const record of sorted) {
      if ((record.opSeq || 0) <= box.#opSeq) continue;
      const recordExpected = payloadChecksum({ opSeq: record.opSeq, op: record.op, payload: record.payload });
      if (recordExpected !== record.checksum) {
        ignoredTailRecords += 1;
        box.stats.tornRecordsIgnored += 1;
        trace?.emit('mailbox:persisted-torn-record-ignored', { label: box.label, opSeq: record.opSeq, op: record.op, expected: recordExpected, actual: record.checksum });
        if (strictTail) throw Object.assign(new Error('Persisted-spill mailbox journal record checksum mismatch'), { code: 'BRT_MAILBOX_BAD_JOURNAL_RECORD' });
        break;
      }
      if (record.op === 'enqueue') {
        box.#rememberRef(record.payload.ref);
        box.#queue.push({ ...entryFromRecord(record.payload), payload: null, hot: false });
        box.#nextSeq = Math.max(box.#nextSeq, record.payload.seq + 1);
      } else if (record.op === 'deliver') {
        const entry = removeFirstBySeq(box.#queue, record.payload.seq);
        if (entry) {
          box.#pending.set(record.payload.pendingId, { ...entry, pendingId: record.payload.pendingId, consumerId: record.payload.consumerId, deliveryCount: record.payload.deliveryCount || ((entry.deliveryCount || 0) + 1), payload: null, deliveredAt: Date.now() });
          const pendingNumber = Number.parseInt(String(record.payload.pendingId).split(':')[1] || '0', 10);
          if (Number.isFinite(pendingNumber)) box.#nextPending = Math.max(box.#nextPending, pendingNumber + 1);
        }
      } else if (record.op === 'ack') {
        box.#pending.delete(record.payload.pendingId);
        removeFirstBySeq(box.#queue, record.payload.seq);
        if (record.payload.deletedBlock) box.#forgetRef(record.payload.ref);
      } else if (record.op === 'compact-delete') {
        box.#forgetRef(record.payload.ref || record.payload.digest);
      } else {
        ignoredTailRecords += 1;
        trace?.emit('mailbox:persisted-torn-record-ignored', { label: box.label, opSeq: record.opSeq, op: record.op, reason: 'unknown-op' });
        break;
      }
      box.#opSeq = record.opSeq;
      box.#journal.push(record);
      applied.push(record.opSeq);
      trace?.emit('mailbox:persisted-journal-replay-apply', { label: box.label, opSeq: record.opSeq, op: record.op, seq: record.payload.seq ?? null });
    }
    let requeuedPending = 0;
    if (requeuePending && box.#pending.size) {
      const pendingRows = [...box.#pending.values()].sort((a, b) => a.seq - b.seq);
      box.#pending.clear();
      requeuedPending = pendingRows.length;
      box.#queue = [...pendingRows.map((entry) => ({ ...entry, pendingId: undefined, consumerId: undefined, payload: null, hot: false })), ...box.#queue];
      box.stats.pendingRequeued += requeuedPending;
      trace?.emit('mailbox:persisted-requeue-pending', { label: box.label, requeuedPending, queueDepth: box.#queue.length });
    }
    box.stats.recoveries += 1;
    const recovery = Object.freeze({ checkpointOpSeq: manifest.payload.opSeq || 0, finalOpSeq: box.#opSeq, appliedJournalRecords: applied.length, appliedJournalOps: applied, ignoredTailRecords, requeuedPending, queueDepth: box.#queue.length, pendingCount: box.#pending.size });
    trace?.emit('mailbox:persisted-recover', { label: box.label, ...recovery });
    return Object.freeze({ mailbox: box, recovery });
  }
}
export function createPersistedSpillMailbox(config = {}) { return new PersistedSpillMailbox(config); }
export async function recoverPersistedSpillMailbox(config = {}) { return PersistedSpillMailbox.recover(config); }
export function checksumPersistedFramePayload32(payload) { return checksum32(toOwnedUint8Array(payload)); }
export function checksumPersistedSpillPayload32(payload) { return checksumPersistedFramePayload32(payload); }
