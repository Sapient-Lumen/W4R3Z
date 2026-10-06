export class FakeNotFoundError extends Error {
  constructor(message) { super(message); this.name = 'NotFoundError'; }
}

function ownedBytes(value) {
  if (typeof value === 'string') return new TextEncoder().encode(value);
  if (value instanceof Uint8Array) return new Uint8Array(value);
  if (value instanceof ArrayBuffer) return new Uint8Array(value.slice(0));
  if (ArrayBuffer.isView(value)) return new Uint8Array(value.buffer.slice(value.byteOffset, value.byteOffset + value.byteLength));
  throw new Error('fake writable only accepts bytes/string');
}

export class FakeFileHandle {
  constructor(name, { hooks = null, path = name } = {}) {
    this.name = name;
    this.path = path;
    this.bytes = new Uint8Array();
    this.hooks = hooks || {};
    this.createWritableCalls = [];
  }

  async getFile() {
    const snapshot = new Uint8Array(this.bytes);
    return { size: snapshot.byteLength, async arrayBuffer() { return snapshot.buffer.slice(snapshot.byteOffset, snapshot.byteOffset + snapshot.byteLength); } };
  }

  async createWritable(options = {}) {
    this.createWritableCalls.push(Object.freeze({ ...options }));
    await this.hooks.onCreateWritable?.({ file: this, options });
    const handle = this;
    let buffer = new Uint8Array();
    let closed = false;
    return {
      async write(value) {
        if (closed) throw new Error('fake writable already closed');
        buffer = ownedBytes(value);
        await handle.hooks.onWrite?.({ file: handle, bytes: new Uint8Array(buffer), options });
      },
      async close() {
        if (closed) throw new Error('fake writable already closed');
        await handle.hooks.onBeforeClose?.({ file: handle, bytes: new Uint8Array(buffer), options });
        closed = true;
        handle.bytes = new Uint8Array(buffer);
        await handle.hooks.onClose?.({ file: handle, bytes: new Uint8Array(buffer), options });
      },
      async abort() {
        closed = true;
        buffer = new Uint8Array();
        await handle.hooks.onAbort?.({ file: handle, options });
      }
    };
  }
}

export class FakeDirectoryHandle {
  constructor(name = '', { hooks = null, path = name } = {}) {
    this.name = name;
    this.path = path;
    this.hooks = hooks || {};
    this.dirs = new Map();
    this.files = new Map();
  }

  childPath(name) { return this.path ? `${this.path}/${name}` : name; }

  async getDirectoryHandle(name, options = {}) {
    await this.hooks.onGetDirectoryHandle?.({ dir: this, name, options });
    if (this.dirs.has(name)) return this.dirs.get(name);
    if (!options.create) throw new FakeNotFoundError(`directory not found: ${name}`);
    const dir = new FakeDirectoryHandle(name, { hooks: this.hooks, path: this.childPath(name) });
    this.dirs.set(name, dir);
    await this.hooks.onCreateDirectory?.({ dir: this, child: dir, name, options });
    return dir;
  }

  async getFileHandle(name, options = {}) {
    await this.hooks.onGetFileHandle?.({ dir: this, name, options });
    if (this.files.has(name)) return this.files.get(name);
    if (!options.create) throw new FakeNotFoundError(`file not found: ${name}`);
    const file = new FakeFileHandle(name, { hooks: this.hooks, path: this.childPath(name) });
    this.files.set(name, file);
    await this.hooks.onCreateFile?.({ dir: this, file, name, options });
    return file;
  }

  async removeEntry(name, options = {}) {
    await this.hooks.onRemoveEntry?.({ dir: this, name, options });
    if (this.files.delete(name)) return;
    if (this.dirs.has(name)) { this.dirs.delete(name); return; }
    throw new FakeNotFoundError(`entry not found: ${name}`);
  }
}

export async function writeFakePath(root, path, bytes) {
  const parts = path.split('/').filter(Boolean);
  let dir = root;
  for (const part of parts.slice(0, -1)) dir = await dir.getDirectoryHandle(part, { create: true });
  const file = await dir.getFileHandle(parts.at(-1), { create: true });
  const writable = await file.createWritable({ mode: 'exclusive' });
  await writable.write(bytes);
  await writable.close();
  return file;
}

export function fakeTreeSummary(root) {
  let dirCount = 0;
  let fileCount = 0;
  let byteCount = 0;
  const files = [];
  function walk(dir) {
    for (const child of dir.dirs.values()) { dirCount += 1; walk(child); }
    for (const file of dir.files.values()) {
      fileCount += 1;
      byteCount += file.bytes.byteLength;
      files.push({ path: file.path, bytes: file.bytes.byteLength });
    }
  }
  walk(root);
  return Object.freeze({ dirCount, fileCount, byteCount, files: Object.freeze(files) });
}

export function createStorageEstimateRecorder(estimate = null) {
  const calls = [];
  const estimateFn = async (root) => {
    const before = fakeTreeSummary(root);
    const value = typeof estimate === 'function'
      ? await estimate(root, before)
      : (estimate || { quota: 1024 * 1024, usage: before.byteCount, usageDetails: { fake: true, recorder: true } });
    calls.push(Object.freeze({
      call: calls.length + 1,
      byteCountBeforeEstimate: before.byteCount,
      fileCountBeforeEstimate: before.fileCount,
      quota: value?.quota ?? null,
      usage: value?.usage ?? null,
      usageDetails: value?.usageDetails ?? null
    }));
    return value;
  };
  return Object.freeze({ estimate: estimateFn, snapshot: () => Object.freeze({ callCount: calls.length, calls: Object.freeze([...calls]) }) });
}


export function createFailOnceDirectoryOpenHarness({ matchName = 'browserrt', errorName = 'InvalidStateError', message = 'simulated fake OPFS directory open failure' } = {}) {
  let remainingFailures = 1;
  const failures = [];
  const hooks = {
    async onGetDirectoryHandle(ctx) {
      const shouldMatch = matchName === null || matchName === undefined || ctx.name === matchName;
      if (remainingFailures > 0 && shouldMatch) {
        remainingFailures -= 1;
        const error = new Error(message);
        error.name = errorName;
        failures.push(Object.freeze({ name: ctx.name, path: ctx.dir?.path || '', options: Object.freeze({ ...(ctx.options || {}) }), errorName, message }));
        throw error;
      }
    }
  };
  return Object.freeze({
    hooks,
    reset(count = 1) { remainingFailures = count; },
    snapshot() { return Object.freeze({ remainingFailures, failureCount: failures.length, failures: Object.freeze([...failures]) }); }
  });
}

// Fake navigator.storage.estimate support for OPFS write-budget proofs.
export async function withFakeNavigator(fn, { hooks = null, estimate = null, storageExtras = null } = {}) {
  const root = new FakeDirectoryHandle('root', { hooks });
  const previous = Object.getOwnPropertyDescriptor(globalThis, 'navigator');
  const storage = { async getDirectory() { return root; } };
  if (estimate !== false) {
    storage.estimate = async () => (typeof estimate === 'function' ? await estimate(root) : (estimate || { quota: 1024 * 1024, usage: fakeTreeSummary(root).byteCount, usageDetails: { fake: true } }));
  }
  Object.assign(storage, storageExtras || {});
  Object.defineProperty(globalThis, 'navigator', { configurable: true, value: { storage } });
  try { return await fn(root); }
  finally {
    if (previous) Object.defineProperty(globalThis, 'navigator', previous);
    else delete globalThis.navigator;
  }
}
