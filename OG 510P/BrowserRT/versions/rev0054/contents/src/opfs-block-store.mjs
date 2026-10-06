// BrowserRT OPFS async block-store provider.
// This is intentionally a narrow async browser-window provider proof surface:
// content-addressed put/get/has/delete/verify using navigator.storage.getDirectory().
// It does not claim fsync durability, quota behavior, crash recovery, multi-tab safety, or sync-handle behavior.

const DEFAULT_PROVIDER = 'opfs-async-block-store-v0';

function storageError(code, message, detail = {}) {
  const error = new Error(message);
  error.name = 'BrowserRTOpfsBlockStoreError';
  error.code = code;
  error.detail = detail;
  return error;
}

function toOwnedUint8Array(value) {
  if (typeof value === 'string') return new TextEncoder().encode(value);
  if (value instanceof Uint8Array) return new Uint8Array(value);
  if (value instanceof ArrayBuffer) return new Uint8Array(value.slice(0));
  if (ArrayBuffer.isView(value)) return new Uint8Array(value.buffer.slice(value.byteOffset, value.byteOffset + value.byteLength));
  throw new Error('OPFS block-store bytes must be a string, ArrayBuffer, Uint8Array, or ArrayBuffer view');
}

function bytesToHex(bytes) {
  return Array.from(new Uint8Array(bytes)).map((x) => x.toString(16).padStart(2, '0')).join('');
}

async function digestBytesHexLocal(value) {
  const bytes = toOwnedUint8Array(value);
  if (globalThis.crypto?.subtle?.digest) {
    const digest = await globalThis.crypto.subtle.digest('SHA-256', bytes);
    return bytesToHex(digest);
  }
  throw new Error('OPFS block store requires crypto.subtle.digest for sha256 block refs');
}

function blockKeyFromRef(refOrDigest) {
  if (typeof refOrDigest === 'string') {
    if (refOrDigest.startsWith('block:sha256:')) return refOrDigest.slice('block:sha256:'.length);
    if (refOrDigest.startsWith('sha256:')) return refOrDigest.slice('sha256:'.length);
    if (/^[0-9a-f]{64}$/.test(refOrDigest)) return refOrDigest;
  }
  if (refOrDigest && typeof refOrDigest === 'object') {
    if (typeof refOrDigest.hash === 'string') return blockKeyFromRef(refOrDigest.hash);
    if (typeof refOrDigest.digest === 'string') return blockKeyFromRef(refOrDigest.digest);
    if (typeof refOrDigest.id === 'string') return blockKeyFromRef(refOrDigest.id);
  }
  throw new Error('OPFS block ref must be sha256 digest string or block object ref');
}

function cleanPathPart(part) {
  if (typeof part !== 'string' || !part.length || part === '.' || part === '..' || /[\\/]/.test(part)) {
    throw new Error(`Invalid OPFS path segment: ${part}`);
  }
  return part;
}

function cleanPrefix(prefix) {
  const parts = String(prefix || '').split('/').filter(Boolean).map(cleanPathPart);
  if (!parts.length) throw new Error('OPFS block-store prefix must contain at least one path segment');
  return parts;
}

function createBlockRef(hash, fields = {}) {
  if (typeof hash !== 'string' || !/^[0-9a-f]{64}$/.test(hash)) {
    throw new Error('OPFS block ref requires lowercase 64-character sha256 hash');
  }
  return Object.freeze({
    kind: 'block',
    id: fields.id ?? `block:sha256:${hash}`,
    digest: `sha256:${hash}`,
    hash,
    algorithm: 'sha256',
    backend: fields.backend ?? DEFAULT_PROVIDER,
    path: fields.path ?? null,
    bytes: fields.bytes ?? 0,
    label: fields.label ?? null,
    ownership: fields.ownership ?? 'origin-private-content-addressed-provider',
    createdAt: fields.createdAt ?? Date.now()
  });
}

async function missingAsFalse(fn) {
  try { await fn(); return true; } catch (error) {
    if (error?.name === 'NotFoundError') return false;
    throw error;
  }
}

export class OpfsAsyncBlockStore {
  #trace;
  #rootPromise = null;
  #opened = false;

  constructor({ name = 'opfs-async-block-store', prefix = 'browserrt/blocks', provider = DEFAULT_PROVIDER, trace = null } = {}) {
    this.name = name;
    this.provider = provider;
    this.prefix = cleanPrefix(prefix).join('/');
    this.#trace = trace;
    this.stats = { opens: 0, puts: 0, duplicatePuts: 0, gets: 0, has: 0, deletes: 0, verifies: 0, checksumFailures: 0, estimateCalls: 0, cleanupCalls: 0 };
    this.#trace?.emit('storage:opfs-blockstore-create', { name: this.name, provider: this.provider, prefix: this.prefix });
  }

  get available() {
    return typeof globalThis.navigator?.storage?.getDirectory === 'function';
  }

  async open() {
    if (!this.available) {
      throw storageError('BRT_OPFS_UNAVAILABLE', 'navigator.storage.getDirectory is unavailable for OPFS async block store', { store: this.name });
    }
    if (!this.#rootPromise) {
      this.#rootPromise = (async () => {
        const originRoot = await globalThis.navigator.storage.getDirectory();
        let dir = originRoot;
        for (const part of this.prefix.split('/')) dir = await dir.getDirectoryHandle(part, { create: true });
        this.stats.opens += 1;
        this.#opened = true;
        this.#trace?.emit('storage:opfs-blockstore-open', { store: this.name, prefix: this.prefix });
        return dir;
      })();
    }
    return await this.#rootPromise;
  }

  blockPath(hash) {
    if (typeof hash !== 'string' || !/^[0-9a-f]{64}$/.test(hash)) throw new Error('blockPath requires sha256 hex hash');
    return `${this.prefix}/${hash.slice(0, 2)}/${hash.slice(2, 4)}/${hash}.blk`;
  }

  async #bucket(hash, create = true) {
    const root = await this.open();
    const a = await root.getDirectoryHandle(hash.slice(0, 2), { create });
    return await a.getDirectoryHandle(hash.slice(2, 4), { create });
  }

  async put(value, fields = {}) {
    const bytes = toOwnedUint8Array(value);
    const hash = await digestBytesHexLocal(bytes);
    const digest = `sha256:${hash}`;
    const path = this.blockPath(hash);
    const bucket = await this.#bucket(hash, true);
    const fileName = `${hash}.blk`;
    const duplicate = await missingAsFalse(async () => { await bucket.getFileHandle(fileName, { create: false }); });
    if (!duplicate) {
      const file = await bucket.getFileHandle(fileName, { create: true });
      const writable = await file.createWritable();
      await writable.write(bytes);
      await writable.close();
    }
    this.stats.puts += 1;
    if (duplicate) this.stats.duplicatePuts += 1;
    const ref = createBlockRef(hash, { bytes: bytes.byteLength, backend: this.provider, path, label: fields.label ?? null });
    this.#trace?.emit('storage:opfs-block-put', { store: this.name, digest, hash, bytes: bytes.byteLength, duplicate, path, label: ref.label });
    return Object.freeze({ ref, digest, hash, bytes: bytes.byteLength, duplicate, path });
  }

  async get(refOrDigest) {
    const hash = blockKeyFromRef(refOrDigest);
    const digest = `sha256:${hash}`;
    const bucket = await this.#bucket(hash, false);
    const file = await bucket.getFileHandle(`${hash}.blk`, { create: false });
    const stored = new Uint8Array(await (await file.getFile()).arrayBuffer());
    const actualHash = await digestBytesHexLocal(stored);
    if (actualHash !== hash) {
      this.stats.checksumFailures += 1;
      this.#trace?.emit('storage:opfs-block-checksum-error', { store: this.name, digest, actualDigest: `sha256:${actualHash}` });
      throw storageError('BRT_OPFS_BLOCK_CHECKSUM_MISMATCH', 'OPFS block checksum mismatch', { store: this.name, digest, actualDigest: `sha256:${actualHash}` });
    }
    this.stats.gets += 1;
    this.#trace?.emit('storage:opfs-block-get', { store: this.name, digest, bytes: stored.byteLength, path: this.blockPath(hash) });
    return stored;
  }

  async has(refOrDigest) {
    const hash = blockKeyFromRef(refOrDigest);
    this.stats.has += 1;
    const present = await missingAsFalse(async () => {
      const bucket = await this.#bucket(hash, false);
      await bucket.getFileHandle(`${hash}.blk`, { create: false });
    });
    this.#trace?.emit('storage:opfs-block-has', { store: this.name, digest: `sha256:${hash}`, present });
    return present;
  }

  async delete(refOrDigest) {
    const hash = blockKeyFromRef(refOrDigest);
    const digest = `sha256:${hash}`;
    let deleted = false;
    try {
      const bucket = await this.#bucket(hash, false);
      await bucket.removeEntry(`${hash}.blk`);
      deleted = true;
    } catch (error) {
      if (error?.name !== 'NotFoundError') throw error;
    }
    this.stats.deletes += 1;
    this.#trace?.emit('storage:opfs-block-delete', { store: this.name, digest, deleted, path: this.blockPath(hash) });
    return deleted;
  }

  async verify(refOrDigest) {
    const hash = blockKeyFromRef(refOrDigest);
    try {
      const bytes = await this.get(hash);
      this.stats.verifies += 1;
      return Object.freeze({ digest: `sha256:${hash}`, present: true, ok: true, bytes: bytes.byteLength, path: this.blockPath(hash) });
    } catch (error) {
      if (error?.name === 'NotFoundError' || error?.code === 'BRT_STORAGE_NOT_FOUND') {
        this.stats.verifies += 1;
        return Object.freeze({ digest: `sha256:${hash}`, present: false, ok: false, bytes: 0, path: this.blockPath(hash) });
      }
      throw error;
    }
  }

  async estimate() {
    this.stats.estimateCalls += 1;
    if (typeof globalThis.navigator?.storage?.estimate !== 'function') return Object.freeze({ quota: null, usage: null, usageDetails: null });
    const estimate = await globalThis.navigator.storage.estimate();
    this.#trace?.emit('storage:opfs-block-estimate', { store: this.name, quota: estimate.quota ?? null, usage: estimate.usage ?? null, usageDetails: estimate.usageDetails ?? null });
    return Object.freeze({ quota: estimate.quota ?? null, usage: estimate.usage ?? null, usageDetails: estimate.usageDetails ?? null });
  }

  async cleanupForTest() {
    this.stats.cleanupCalls += 1;
    try {
      const originRoot = await globalThis.navigator.storage.getDirectory();
      const parts = this.prefix.split('/');
      let dir = originRoot;
      for (const part of parts.slice(0, -1)) dir = await dir.getDirectoryHandle(part, { create: false });
      await dir.removeEntry(parts.at(-1), { recursive: true });
      this.#trace?.emit('storage:opfs-block-cleanup', { store: this.name, prefix: this.prefix, deleted: true });
      return true;
    } catch (error) {
      if (error?.name === 'NotFoundError') {
        this.#trace?.emit('storage:opfs-block-cleanup', { store: this.name, prefix: this.prefix, deleted: false });
        return false;
      }
      throw error;
    }
  }

  snapshot() {
    return Object.freeze({ name: this.name, provider: this.provider, prefix: this.prefix, opened: this.#opened, available: this.available, stats: { ...this.stats } });
  }
}

export function createOpfsAsyncBlockStore(config = {}) {
  return new OpfsAsyncBlockStore(config);
}
