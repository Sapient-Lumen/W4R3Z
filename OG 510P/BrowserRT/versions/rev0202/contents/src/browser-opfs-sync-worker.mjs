import { REVISION, VERSION, createOpfsObjectRef } from './browserrt.mjs';
function describeError(error) {
  if (!error || typeof error !== 'object') return { name: 'Error', message: String(error) };
  return { name: error.name || 'Error', message: error.message || String(error), stack: error.stack };
}
async function digestHex(bytes) {
  if (globalThis.crypto?.subtle?.digest) {
    const digest = await globalThis.crypto.subtle.digest('SHA-256', bytes.buffer.slice(bytes.byteOffset, bytes.byteOffset + bytes.byteLength));
    return Array.from(new Uint8Array(digest)).map((x) => x.toString(16).padStart(2, '0')).join('');
  }
  let hash = 2166136261;
  for (const byte of bytes) {
    hash ^= byte;
    hash = Math.imul(hash, 16777619) >>> 0;
  }
  return `fnv32:${hash.toString(16).padStart(8, '0')}`;
}
function normalizePath(path) {
  const parts = String(path || '').split('/').filter(Boolean);
  if (!parts.length || parts.some((part) => part === '..' || part.includes('\\'))) {
    throw new Error('OPFS sync worker path must be a non-empty relative path without parent traversal');
  }
  return parts;
}
async function maybe(value) {
  return await value;
}
async function opfsSyncWriteRead({ path, buffer, cleanup = true }) {
  if (!navigator.storage?.getDirectory) throw new Error('navigator.storage.getDirectory is unavailable in worker');
  const parts = normalizePath(path);
  const input = new Uint8Array(buffer);
  const root = await navigator.storage.getDirectory();
  let dir = root;
  for (const part of parts.slice(0, -1)) {
    dir = await dir.getDirectoryHandle(part, { create: true });
  }
  const fileName = parts.at(-1);
  const file = await dir.getFileHandle(fileName, { create: true });
  if (typeof file.createSyncAccessHandle !== 'function') {
    throw new Error('createSyncAccessHandle is unavailable in this dedicated worker');
  }
  const handle = await file.createSyncAccessHandle();
  let closed = false;
  try {
    const methods = {
      read: typeof handle.read,
      write: typeof handle.write,
      truncate: typeof handle.truncate,
      flush: typeof handle.flush,
      getSize: typeof handle.getSize,
      close: typeof handle.close
    };
    await maybe(handle.truncate(0));
    const written = handle.write(input, { at: 0 });
    await maybe(handle.truncate(input.byteLength));
    await maybe(handle.flush());
    const size = await maybe(handle.getSize());
    const readBuffer = new Uint8Array(size);
    const read = handle.read(readBuffer, { at: 0 });
    await maybe(handle.close());
    closed = true;
    const same = read === input.byteLength && readBuffer.length === input.byteLength && readBuffer.every((value, i) => value === input[i]);
    if (cleanup && typeof dir.removeEntry === 'function') {
      await dir.removeEntry(fileName).catch(() => {});
    }
    const ref = createOpfsObjectRef(path, {
      id: `opfs:${REVISION}:sync-worker-proof`,
      bytes: readBuffer.byteLength,
      backend: 'opfs-sync-access-handle',
      ownership: 'origin-private-worker-exclusive'
    });
    return {
      revision: REVISION,
      version: VERSION,
      path,
      fileName,
      methods,
      constructorTypes: {
        FileSystemSyncAccessHandle: typeof FileSystemSyncAccessHandle,
        FileSystemFileHandle: typeof FileSystemFileHandle,
        WorkerNavigatorStorage: typeof navigator.storage
      },
      bytesWritten: written,
      bytesRead: read,
      size,
      same,
      digest: await digestHex(readBuffer),
      ref,
      cleanup,
      closed: true,
      workerScope: typeof DedicatedWorkerGlobalScope === 'function' && self instanceof DedicatedWorkerGlobalScope
    };
  } finally {
    if (!closed) {
      try { await maybe(handle.close()); } catch {}
    }
  }
}
self.postMessage({ type: 'opfs-sync:ready', detail: { backend: 'browser-dedicated-worker', revision: REVISION, version: VERSION } });
self.onmessage = async (event) => {
  const message = event.data || {};
  if (message.type !== 'opfs-sync:write-read') return;
  try {
    const result = await opfsSyncWriteRead(message);
    self.postMessage({ type: 'opfs-sync:result', id: message.id, envelope: message.envelope, result });
  } catch (error) {
    self.postMessage({ type: 'opfs-sync:error', id: message.id, envelope: message.envelope, error: describeError(error) });
  }
};
