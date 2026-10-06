// BrowserRT rev0025 SharedArrayBuffer frame-ring baby proof.
// Scope: single producer / single consumer, variable-size Uint8Array frames, bounded byte capacity.
// Non-scope: browser Worker frame proof, MPSC, MPMC, zero-copy typed schema, waitAsync, or throughput claims.

export const SAB_FRAME_RING_HEADER_INTS = 24;
export const SAB_FRAME_RING_MAGIC = 0x42524631; // BRF1
export const SAB_FRAME_WRAP_SENTINEL = -1;

const IDX_MAGIC = 0;
const IDX_CAPACITY_BYTES = 1;
const IDX_READ_OFFSET = 2;
const IDX_WRITE_OFFSET = 3;
const IDX_USED_BYTES = 4;
const IDX_CLOSED = 5;
const IDX_FULL_HITS = 6;
const IDX_EMPTY_WAITS = 7;
const IDX_PUSH_COUNT = 8;
const IDX_POP_COUNT = 9;
const IDX_NOTIFY_SEQ = 10;
const IDX_WRAP_COUNT = 11;
const IDX_MAX_FRAME_BYTES = 12;
const IDX_RESERVED_BYTES = 13;

const HEADER_BYTES = SAB_FRAME_RING_HEADER_INTS * Int32Array.BYTES_PER_ELEMENT;
const RECORD_HEADER_BYTES = 8; // int32 length + int32 sequence

function assertAtomicsReady() {
  if (typeof SharedArrayBuffer !== 'function') throw new Error('SharedArrayBuffer is unavailable');
  if (typeof Atomics !== 'object') throw new Error('Atomics is unavailable');
}

function align4(value) {
  return (value + 3) & ~3;
}

function asOwnedUint8Array(value) {
  if (typeof value === 'string') return new TextEncoder().encode(value);
  if (value instanceof Uint8Array) return new Uint8Array(value);
  if (value instanceof ArrayBuffer) return new Uint8Array(value.slice(0));
  if (ArrayBuffer.isView(value)) return new Uint8Array(value.buffer.slice(value.byteOffset, value.byteOffset + value.byteLength));
  throw new Error('SharedFrameRing payload must be string, ArrayBuffer, Uint8Array, or an ArrayBuffer view');
}

function assertCapacityBytes(capacityBytes) {
  if (!Number.isInteger(capacityBytes) || capacityBytes < 32 || capacityBytes % 4 !== 0) {
    throw new Error('SharedFrameRing capacityBytes must be an integer multiple of 4 and at least 32');
  }
}

function assertSeq(seq) {
  if (!Number.isInteger(seq) || seq < 0 || seq > 0x7fffffff) throw new Error('SharedFrameRing sequence must be a non-negative signed Int32');
}

function readI32(data, offset) {
  return new DataView(data.buffer, data.byteOffset + offset, 4).getInt32(0, true);
}

function writeI32(data, offset, value) {
  new DataView(data.buffer, data.byteOffset + offset, 4).setInt32(0, value, true);
}

function zeroPad(data, offset, length) {
  for (let i = 0; i < length; i += 1) data[offset + i] = 0;
}

export class SharedFrameRing {
  constructor({ sab, capacityBytes = null, label = 'sab-frame-ring', trace = null, initialize = false } = {}) {
    assertAtomicsReady();
    if (!(sab instanceof SharedArrayBuffer)) throw new Error('SharedFrameRing requires a SharedArrayBuffer');
    this.sab = sab;
    this.label = label;
    this.trace = trace;
    this.header = new Int32Array(sab, 0, SAB_FRAME_RING_HEADER_INTS);
    if (initialize) {
      assertCapacityBytes(capacityBytes);
      if (sab.byteLength < HEADER_BYTES + capacityBytes) throw new Error('SharedArrayBuffer too small for requested frame ring capacity');
      Atomics.store(this.header, IDX_MAGIC, SAB_FRAME_RING_MAGIC);
      Atomics.store(this.header, IDX_CAPACITY_BYTES, capacityBytes);
      Atomics.store(this.header, IDX_READ_OFFSET, 0);
      Atomics.store(this.header, IDX_WRITE_OFFSET, 0);
      Atomics.store(this.header, IDX_USED_BYTES, 0);
      Atomics.store(this.header, IDX_CLOSED, 0);
      Atomics.store(this.header, IDX_FULL_HITS, 0);
      Atomics.store(this.header, IDX_EMPTY_WAITS, 0);
      Atomics.store(this.header, IDX_PUSH_COUNT, 0);
      Atomics.store(this.header, IDX_POP_COUNT, 0);
      Atomics.store(this.header, IDX_NOTIFY_SEQ, 0);
      Atomics.store(this.header, IDX_WRAP_COUNT, 0);
      Atomics.store(this.header, IDX_MAX_FRAME_BYTES, 0);
      Atomics.store(this.header, IDX_RESERVED_BYTES, 0);
    }
    if (Atomics.load(this.header, IDX_MAGIC) !== SAB_FRAME_RING_MAGIC) throw new Error('SharedFrameRing missing BRF1 magic');
    this.capacityBytes = Atomics.load(this.header, IDX_CAPACITY_BYTES);
    assertCapacityBytes(this.capacityBytes);
    this.data = new Uint8Array(sab, HEADER_BYTES, this.capacityBytes);
    this.trace?.emit('ipc:sab-frame-ring-open', { label: this.label, capacityBytes: this.capacityBytes });
  }

  static allocate({ capacityBytes = 1024, label = 'sab-frame-ring', trace = null } = {}) {
    assertCapacityBytes(capacityBytes);
    const sab = new SharedArrayBuffer(HEADER_BYTES + capacityBytes);
    const ring = new SharedFrameRing({ sab, capacityBytes, label, trace, initialize: true });
    trace?.emit('ipc:sab-frame-ring-create', { label, capacityBytes, bytes: sab.byteLength });
    return ring;
  }

  tryPushFrame(payload, { seq = null } = {}) {
    const bytes = asOwnedUint8Array(payload);
    const sequence = seq ?? Atomics.load(this.header, IDX_PUSH_COUNT);
    assertSeq(sequence);
    if (Atomics.load(this.header, IDX_CLOSED)) {
      this.trace?.emit('ipc:sab-frame-ring-push-closed', { label: this.label, seq: sequence, bytes: bytes.byteLength });
      return false;
    }
    const payloadBytes = bytes.byteLength;
    const paddedPayloadBytes = align4(payloadBytes);
    const recordBytes = RECORD_HEADER_BYTES + paddedPayloadBytes;
    if (recordBytes > this.capacityBytes) {
      Atomics.add(this.header, IDX_FULL_HITS, 1);
      this.trace?.emit('ipc:sab-frame-ring-oversize', { label: this.label, seq: sequence, bytes: payloadBytes, recordBytes, capacityBytes: this.capacityBytes });
      return false;
    }

    let write = Atomics.load(this.header, IDX_WRITE_OFFSET);
    const used = Atomics.load(this.header, IDX_USED_BYTES);
    let needed = recordBytes;
    let wrapGap = 0;
    if (write + recordBytes > this.capacityBytes) {
      wrapGap = this.capacityBytes - write;
      needed += wrapGap;
    }
    if (used + needed > this.capacityBytes) {
      Atomics.add(this.header, IDX_FULL_HITS, 1);
      this.trace?.emit('ipc:sab-frame-ring-full', { label: this.label, seq: sequence, bytes: payloadBytes, recordBytes, used, needed, capacityBytes: this.capacityBytes });
      return false;
    }

    if (wrapGap > 0) {
      writeI32(this.data, write, SAB_FRAME_WRAP_SENTINEL);
      if (wrapGap > 4) zeroPad(this.data, write + 4, wrapGap - 4);
      Atomics.add(this.header, IDX_WRAP_COUNT, 1);
      Atomics.add(this.header, IDX_RESERVED_BYTES, wrapGap);
      Atomics.add(this.header, IDX_USED_BYTES, wrapGap);
      this.trace?.emit('ipc:sab-frame-ring-wrap', { label: this.label, fromOffset: write, gapBytes: wrapGap });
      write = 0;
      Atomics.store(this.header, IDX_WRITE_OFFSET, 0);
    }

    writeI32(this.data, write, payloadBytes);
    writeI32(this.data, write + 4, sequence);
    this.data.set(bytes, write + RECORD_HEADER_BYTES);
    if (paddedPayloadBytes > payloadBytes) zeroPad(this.data, write + RECORD_HEADER_BYTES + payloadBytes, paddedPayloadBytes - payloadBytes);
    const nextWrite = write + recordBytes === this.capacityBytes ? 0 : write + recordBytes;
    Atomics.store(this.header, IDX_WRITE_OFFSET, nextWrite);
    Atomics.add(this.header, IDX_USED_BYTES, recordBytes);
    Atomics.add(this.header, IDX_PUSH_COUNT, 1);
    Atomics.add(this.header, IDX_NOTIFY_SEQ, 1);
    const prevMax = Atomics.load(this.header, IDX_MAX_FRAME_BYTES);
    if (payloadBytes > prevMax) Atomics.store(this.header, IDX_MAX_FRAME_BYTES, payloadBytes);
    Atomics.notify(this.header, IDX_NOTIFY_SEQ, 1);
    Atomics.notify(this.header, IDX_WRITE_OFFSET, 1);
    this.trace?.emit('ipc:sab-frame-ring-push', { label: this.label, seq: sequence, bytes: payloadBytes, recordBytes, offset: write, nextWrite });
    return true;
  }

  popFrame() {
    let used = Atomics.load(this.header, IDX_USED_BYTES);
    if (used <= 0) {
      if (Atomics.load(this.header, IDX_CLOSED)) return { done: true, frame: null };
      return { done: false, frame: null };
    }
    let read = Atomics.load(this.header, IDX_READ_OFFSET);
    const length = readI32(this.data, read);
    if (length === SAB_FRAME_WRAP_SENTINEL) {
      const gap = this.capacityBytes - read;
      Atomics.store(this.header, IDX_READ_OFFSET, 0);
      Atomics.sub(this.header, IDX_USED_BYTES, gap);
      Atomics.notify(this.header, IDX_NOTIFY_SEQ, 1);
      Atomics.notify(this.header, IDX_READ_OFFSET, 1);
      this.trace?.emit('ipc:sab-frame-ring-consume-wrap', { label: this.label, fromOffset: read, gapBytes: gap });
      return this.popFrame();
    }
    if (length < 0 || length + RECORD_HEADER_BYTES > this.capacityBytes) {
      throw new Error(`SharedFrameRing invalid frame length ${length}`);
    }
    const seq = readI32(this.data, read + 4);
    const paddedPayloadBytes = align4(length);
    const recordBytes = RECORD_HEADER_BYTES + paddedPayloadBytes;
    if (recordBytes > used) return { done: false, frame: null };
    const payload = new Uint8Array(length);
    payload.set(this.data.subarray(read + RECORD_HEADER_BYTES, read + RECORD_HEADER_BYTES + length));
    const nextRead = read + recordBytes === this.capacityBytes ? 0 : read + recordBytes;
    Atomics.store(this.header, IDX_READ_OFFSET, nextRead);
    Atomics.sub(this.header, IDX_USED_BYTES, recordBytes);
    Atomics.add(this.header, IDX_POP_COUNT, 1);
    Atomics.notify(this.header, IDX_NOTIFY_SEQ, 1);
    Atomics.notify(this.header, IDX_READ_OFFSET, 1);
    this.trace?.emit('ipc:sab-frame-ring-pop', { label: this.label, seq, bytes: length, recordBytes, offset: read, nextRead });
    return { done: false, frame: { seq, payload } };
  }

  waitPopFrame({ timeoutMs = 1000 } = {}) {
    for (;;) {
      const got = this.popFrame();
      if (got.frame || got.done) return got;
      const seq = Atomics.load(this.header, IDX_NOTIFY_SEQ);
      Atomics.add(this.header, IDX_EMPTY_WAITS, 1);
      Atomics.wait(this.header, IDX_NOTIFY_SEQ, seq, timeoutMs);
    }
  }

  close() {
    Atomics.store(this.header, IDX_CLOSED, 1);
    Atomics.add(this.header, IDX_NOTIFY_SEQ, 1);
    Atomics.notify(this.header, IDX_NOTIFY_SEQ, Number.POSITIVE_INFINITY);
    Atomics.notify(this.header, IDX_WRITE_OFFSET, Number.POSITIVE_INFINITY);
    Atomics.notify(this.header, IDX_READ_OFFSET, Number.POSITIVE_INFINITY);
    this.trace?.emit('ipc:sab-frame-ring-close', { label: this.label, snapshot: this.snapshot() });
  }

  snapshot() {
    const readOffset = Atomics.load(this.header, IDX_READ_OFFSET);
    const writeOffset = Atomics.load(this.header, IDX_WRITE_OFFSET);
    const usedBytes = Atomics.load(this.header, IDX_USED_BYTES);
    return Object.freeze({
      label: this.label,
      capacityBytes: this.capacityBytes,
      readOffset,
      writeOffset,
      usedBytes,
      freeBytes: this.capacityBytes - usedBytes,
      closed: Boolean(Atomics.load(this.header, IDX_CLOSED)),
      fullHits: Atomics.load(this.header, IDX_FULL_HITS),
      emptyWaits: Atomics.load(this.header, IDX_EMPTY_WAITS),
      pushCount: Atomics.load(this.header, IDX_PUSH_COUNT),
      popCount: Atomics.load(this.header, IDX_POP_COUNT),
      notifySeq: Atomics.load(this.header, IDX_NOTIFY_SEQ),
      wrapCount: Atomics.load(this.header, IDX_WRAP_COUNT),
      maxFrameBytes: Atomics.load(this.header, IDX_MAX_FRAME_BYTES),
      reservedBytes: Atomics.load(this.header, IDX_RESERVED_BYTES)
    });
  }
}

export function createSharedFrameRing(config = {}) {
  return SharedFrameRing.allocate(config);
}

export function openSharedFrameRing(sab, config = {}) {
  return new SharedFrameRing({ ...config, sab, initialize: false });
}
