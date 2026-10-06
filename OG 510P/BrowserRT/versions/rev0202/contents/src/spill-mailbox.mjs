function toOwnedUint8Array(value) {
  if (typeof value === 'string') return new TextEncoder().encode(value);
  if (value instanceof Uint8Array) return new Uint8Array(value);
  if (value instanceof ArrayBuffer) return new Uint8Array(value.slice(0));
  if (ArrayBuffer.isView(value)) return new Uint8Array(value.buffer.slice(value.byteOffset, value.byteOffset + value.byteLength));
  throw new Error('SpillFrameMailbox payload must be a string, ArrayBuffer, Uint8Array, or ArrayBuffer view');
}
function checksum32(bytes) {
  let sum = 0;
  for (const byte of new Uint8Array(bytes)) sum = (sum + byte) >>> 0;
  return sum >>> 0;
}
function assertProvider(provider) {
  for (const method of ['put', 'get', 'delete', 'snapshot']) {
    if (!provider || typeof provider[method] !== 'function') throw new Error(`SpillFrameMailbox requires a provider with ${method}()`);
  }
}
function storageCode(error) {
  return error?.code || error?.name || 'BRT_STORAGE_UNKNOWN';
}
export class SpillFrameMailbox {
  #queue = [];
  #pending = new Map();
  #nextSeq = 1;
  #nextPending = 1;
  #memoryUsed = 0;
  #trace;
  constructor({ label = 'spill-frame-mailbox', provider, memoryCapacityBytes = 1024, maxFrameBytes = 64 * 1024, trace = null, deleteSpilledBlocksOnAck = true } = {}) {
    assertProvider(provider);
    if (!Number.isInteger(memoryCapacityBytes) || memoryCapacityBytes < 0) throw new Error('memoryCapacityBytes must be a non-negative integer');
    if (!Number.isInteger(maxFrameBytes) || maxFrameBytes < 1) throw new Error('maxFrameBytes must be a positive integer');
    this.label = label;
    this.provider = provider;
    this.memoryCapacityBytes = memoryCapacityBytes;
    this.maxFrameBytes = maxFrameBytes;
    this.deleteSpilledBlocksOnAck = Boolean(deleteSpilledBlocksOnAck);
    this.#trace = trace;
    this.stats = { enqueued: 0, memoryEnqueued: 0, spilledEnqueued: 0, rejected: 0, oversizeRejected: 0, quotaRejected: 0, dequeued: 0, acked: 0, reclaimed: 0, emptyPolls: 0, blockDeletes: 0 };
    this.#trace?.emit('mailbox:spill-create', { label: this.label, provider: provider.provider || provider.name || 'unknown-provider', memoryCapacityBytes: this.memoryCapacityBytes, maxFrameBytes: this.maxFrameBytes, deleteSpilledBlocksOnAck: this.deleteSpilledBlocksOnAck });
  }
  async enqueue(payload, { seq = null, label = null } = {}) {
    const bytes = toOwnedUint8Array(payload);
    const frameSeq = seq ?? this.#nextSeq++;
    const frame = { seq: frameSeq, bytes: bytes.byteLength, checksum32: checksum32(bytes), label };
    if (bytes.byteLength > this.maxFrameBytes) {
      this.stats.rejected += 1; this.stats.oversizeRejected += 1;
      this.#trace?.emit('mailbox:spill-reject', { label: this.label, seq: frameSeq, bytes: bytes.byteLength, reason: 'oversize', maxFrameBytes: this.maxFrameBytes });
      return Object.freeze({ disposition: 'rejected-oversize', reason: 'oversize', ...frame });
    }
    if (this.#memoryUsed + bytes.byteLength <= this.memoryCapacityBytes) {
      this.#queue.push({ ...frame, source: 'memory', payload: bytes });
      this.#memoryUsed += bytes.byteLength;
      this.stats.enqueued += 1; this.stats.memoryEnqueued += 1;
      this.#trace?.emit('mailbox:enqueue-memory', { label: this.label, seq: frameSeq, bytes: bytes.byteLength, memoryUsed: this.#memoryUsed, queueDepth: this.#queue.length });
      return Object.freeze({ disposition: 'memory', source: 'memory', queueDepth: this.#queue.length, memoryUsed: this.#memoryUsed, ...frame });
    }
    try {
      const put = await this.provider.put(bytes, { label: label ?? `${this.label}:seq:${frameSeq}` });
      this.#queue.push({ ...frame, source: 'spill', ref: put.ref });
      this.stats.enqueued += 1; this.stats.spilledEnqueued += 1;
      this.#trace?.emit('mailbox:spill-write', { label: this.label, seq: frameSeq, bytes: bytes.byteLength, digest: put.digest, queueDepth: this.#queue.length, memoryUsed: this.#memoryUsed });
      return Object.freeze({ disposition: 'spilled', source: 'spill', ref: put.ref, digest: put.digest, queueDepth: this.#queue.length, memoryUsed: this.#memoryUsed, ...frame });
    } catch (error) {
      const code = storageCode(error);
      this.stats.rejected += 1;
      if (code === 'BRT_STORAGE_QUOTA_EXCEEDED') this.stats.quotaRejected += 1;
      this.#trace?.emit('mailbox:spill-reject', { label: this.label, seq: frameSeq, bytes: bytes.byteLength, reason: code, memoryUsed: this.#memoryUsed });
      return Object.freeze({ disposition: 'rejected-spill', reason: code, error: { name: error.name, message: error.message, code }, ...frame });
    }
  }
  async dequeue({ consumerId = 'consumer' } = {}) {
    const entry = this.#queue.shift();
    if (!entry) { this.stats.emptyPolls += 1; this.#trace?.emit('mailbox:dequeue-empty', { label: this.label, pendingCount: this.#pending.size }); return null; }
    let payload;
    if (entry.source === 'memory') { payload = entry.payload; this.#memoryUsed -= payload.byteLength; }
    else payload = await this.provider.get(entry.ref);
    const pendingId = `pending:${this.#nextPending++}`;
    const pending = { ...entry, pendingId, consumerId, payload: entry.source === 'memory' ? payload : null, deliveredAt: Date.now() };
    this.#pending.set(pendingId, pending); this.stats.dequeued += 1;
    this.#trace?.emit('mailbox:dequeue', { label: this.label, pendingId, seq: entry.seq, bytes: entry.bytes, source: entry.source, consumerId, queueDepth: this.#queue.length, pendingCount: this.#pending.size, memoryUsed: this.#memoryUsed });
    return Object.freeze({ pendingId, consumerId, seq: entry.seq, source: entry.source, bytes: entry.bytes, checksum32: entry.checksum32, payload: new Uint8Array(payload), ref: entry.ref ?? null });
  }
  async ack(pendingId, { deleteSpilledBlock = this.deleteSpilledBlocksOnAck } = {}) {
    const pending = this.#pending.get(pendingId);
    if (!pending) { this.#trace?.emit('mailbox:ack-miss', { label: this.label, pendingId }); return false; }
    this.#pending.delete(pendingId);
    let deletedBlock = false;
    if (pending.source === 'spill' && deleteSpilledBlock) { deletedBlock = await this.provider.delete(pending.ref); if (deletedBlock) this.stats.blockDeletes += 1; }
    this.stats.acked += 1;
    this.#trace?.emit('mailbox:ack', { label: this.label, pendingId, seq: pending.seq, source: pending.source, deletedBlock, pendingCount: this.#pending.size });
    return true;
  }
  reclaimPending({ max = Number.POSITIVE_INFINITY } = {}) {
    const rows = [...this.#pending.values()].sort((a, b) => a.deliveredAt - b.deliveredAt || a.seq - b.seq).slice(0, max);
    for (let i = rows.length - 1; i >= 0; i -= 1) {
      const entry = rows[i]; this.#pending.delete(entry.pendingId);
      const queueEntry = entry.source === 'memory' ? { seq: entry.seq, bytes: entry.bytes, checksum32: entry.checksum32, label: entry.label, source: 'memory', payload: entry.payload } : { seq: entry.seq, bytes: entry.bytes, checksum32: entry.checksum32, label: entry.label, source: 'spill', ref: entry.ref };
      if (queueEntry.source === 'memory') this.#memoryUsed += queueEntry.payload.byteLength;
      this.#queue.unshift(queueEntry); this.stats.reclaimed += 1;
      this.#trace?.emit('mailbox:pending-reclaim', { label: this.label, pendingId: entry.pendingId, seq: entry.seq, source: entry.source, queueDepth: this.#queue.length, pendingCount: this.#pending.size });
    }
    return Object.freeze({ reclaimed: rows.length, queueDepth: this.#queue.length, pendingCount: this.#pending.size, memoryUsed: this.#memoryUsed });
  }
  snapshot() {
    return Object.freeze({ label: this.label, provider: this.provider.provider || this.provider.name || 'unknown-provider', queueDepth: this.#queue.length, pendingCount: this.#pending.size, memoryCapacityBytes: this.memoryCapacityBytes, memoryUsed: this.#memoryUsed, maxFrameBytes: this.maxFrameBytes, stats: { ...this.stats }, providerSnapshot: this.provider.snapshot() });
  }
}
export function createSpillFrameMailbox(config = {}) { return new SpillFrameMailbox(config); }
export function checksumFramePayload32(payload) { return checksum32(toOwnedUint8Array(payload)); }
