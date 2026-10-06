export const SAB_RING_HEADER_INTS = 16;
export const SAB_RING_MAGIC = 0x42525431; // BRT1
const IDX_MAGIC = 0;
const IDX_CAPACITY = 1;
const IDX_READ = 2;
const IDX_WRITE = 3;
const IDX_CLOSED = 4;
const IDX_FULL_HITS = 5;
const IDX_EMPTY_WAITS = 6;
const IDX_PUSH_COUNT = 7;
const IDX_POP_COUNT = 8;
const IDX_NOTIFY_SEQ = 9;
function assertAtomicsReady() {
  if (typeof SharedArrayBuffer !== 'function') throw new Error('SharedArrayBuffer is unavailable');
  if (typeof Atomics !== 'object') throw new Error('Atomics is unavailable');
}
function assertPositiveCapacity(capacity) {
  if (!Number.isInteger(capacity) || capacity < 1) {
    throw new Error('SharedInt32Ring capacity must be a positive integer');
  }
}
function int32(value) {
  if (!Number.isFinite(value)) throw new Error('SharedInt32Ring value must be finite');
  return value | 0;
}
export class SharedInt32Ring {
  constructor({ sab, capacity = null, label = 'sab-ring', trace = null, initialize = false } = {}) {
    assertAtomicsReady();
    if (!(sab instanceof SharedArrayBuffer)) throw new Error('SharedInt32Ring requires a SharedArrayBuffer');
    this.sab = sab;
    this.label = label;
    this.trace = trace;
    this.cells = new Int32Array(sab);
    this.header = this.cells.subarray(0, SAB_RING_HEADER_INTS);
    if (initialize) {
      assertPositiveCapacity(capacity);
      if (this.cells.length < SAB_RING_HEADER_INTS + capacity) throw new Error('SharedArrayBuffer too small for requested ring capacity');
      Atomics.store(this.header, IDX_MAGIC, SAB_RING_MAGIC);
      Atomics.store(this.header, IDX_CAPACITY, capacity);
      Atomics.store(this.header, IDX_READ, 0);
      Atomics.store(this.header, IDX_WRITE, 0);
      Atomics.store(this.header, IDX_CLOSED, 0);
      Atomics.store(this.header, IDX_FULL_HITS, 0);
      Atomics.store(this.header, IDX_EMPTY_WAITS, 0);
      Atomics.store(this.header, IDX_PUSH_COUNT, 0);
      Atomics.store(this.header, IDX_POP_COUNT, 0);
      Atomics.store(this.header, IDX_NOTIFY_SEQ, 0);
    }
    if (Atomics.load(this.header, IDX_MAGIC) !== SAB_RING_MAGIC) throw new Error('SharedInt32Ring missing BRT1 magic');
    this.capacity = Atomics.load(this.header, IDX_CAPACITY);
    assertPositiveCapacity(this.capacity);
    this.data = this.cells.subarray(SAB_RING_HEADER_INTS, SAB_RING_HEADER_INTS + this.capacity);
    this.trace?.emit('ipc:sab-ring-open', { label: this.label, capacity: this.capacity });
  }
  static allocate({ capacity = 8, label = 'sab-ring', trace = null } = {}) {
    assertPositiveCapacity(capacity);
    const sab = new SharedArrayBuffer(Int32Array.BYTES_PER_ELEMENT * (SAB_RING_HEADER_INTS + capacity));
    const ring = new SharedInt32Ring({ sab, capacity, label, trace, initialize: true });
    trace?.emit('ipc:sab-ring-create', { label, capacity, bytes: sab.byteLength });
    return ring;
  }
  tryPush(value) {
    const write = Atomics.load(this.header, IDX_WRITE);
    const read = Atomics.load(this.header, IDX_READ);
    if (Atomics.load(this.header, IDX_CLOSED)) {
      this.trace?.emit('ipc:sab-ring-push-closed', { label: this.label, value: int32(value) });
      return false;
    }
    if (write - read >= this.capacity) {
      Atomics.add(this.header, IDX_FULL_HITS, 1);
      this.trace?.emit('ipc:sab-ring-full', { label: this.label, read, write, capacity: this.capacity });
      return false;
    }
    const slot = write % this.capacity;
    Atomics.store(this.data, slot, int32(value));
    Atomics.store(this.header, IDX_WRITE, write + 1);
    Atomics.add(this.header, IDX_PUSH_COUNT, 1);
    Atomics.add(this.header, IDX_NOTIFY_SEQ, 1);
    Atomics.notify(this.header, IDX_WRITE, 1);
    this.trace?.emit('ipc:sab-ring-push', { label: this.label, value: int32(value), slot, read, write: write + 1 });
    return true;
  }
  pop() {
    const read = Atomics.load(this.header, IDX_READ);
    const write = Atomics.load(this.header, IDX_WRITE);
    if (read >= write) {
      if (Atomics.load(this.header, IDX_CLOSED)) return { done: true, value: null };
      return { done: false, value: null };
    }
    const slot = read % this.capacity;
    const value = Atomics.load(this.data, slot);
    Atomics.store(this.header, IDX_READ, read + 1);
    Atomics.add(this.header, IDX_POP_COUNT, 1);
    Atomics.notify(this.header, IDX_READ, 1);
    this.trace?.emit('ipc:sab-ring-pop', { label: this.label, value, slot, read: read + 1, write });
    return { done: false, value };
  }
  waitPop({ timeoutMs = 1000 } = {}) {
    for (;;) {
      const got = this.pop();
      if (got.value !== null || got.done) return got;
      const write = Atomics.load(this.header, IDX_WRITE);
      Atomics.add(this.header, IDX_EMPTY_WAITS, 1);
      Atomics.wait(this.header, IDX_WRITE, write, timeoutMs);
    }
  }
  close() {
    Atomics.store(this.header, IDX_CLOSED, 1);
    Atomics.add(this.header, IDX_NOTIFY_SEQ, 1);
    Atomics.notify(this.header, IDX_WRITE, Number.POSITIVE_INFINITY);
    Atomics.notify(this.header, IDX_READ, Number.POSITIVE_INFINITY);
    this.trace?.emit('ipc:sab-ring-close', { label: this.label, snapshot: this.snapshot() });
  }
  snapshot() {
    const read = Atomics.load(this.header, IDX_READ);
    const write = Atomics.load(this.header, IDX_WRITE);
    return Object.freeze({
      label: this.label,
      capacity: this.capacity,
      read,
      write,
      size: Math.max(0, write - read),
      closed: Boolean(Atomics.load(this.header, IDX_CLOSED)),
      fullHits: Atomics.load(this.header, IDX_FULL_HITS),
      emptyWaits: Atomics.load(this.header, IDX_EMPTY_WAITS),
      pushCount: Atomics.load(this.header, IDX_PUSH_COUNT),
      popCount: Atomics.load(this.header, IDX_POP_COUNT),
      notifySeq: Atomics.load(this.header, IDX_NOTIFY_SEQ)
    });
  }
}
export function createSharedInt32Ring(config = {}) {
  return SharedInt32Ring.allocate(config);
}
export function openSharedInt32Ring(sab, config = {}) {
  return new SharedInt32Ring({ ...config, sab, initialize: false });
}
