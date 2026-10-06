import { openSharedFrameRing } from './sab-frame-ring.mjs';
function describeError(error) {
  if (!error || typeof error !== 'object') return { name: 'Error', message: String(error) };
  return { name: error.name || 'Error', message: error.message || String(error), stack: error.stack };
}
function checksum(bytes) {
  let out = 2166136261 >>> 0;
  for (const b of bytes) {
    out ^= b;
    out = Math.imul(out, 16777619) >>> 0;
  }
  return out >>> 0;
}
const startedAt = Date.now();
self.postMessage({
  type: 'sab-frame-ring:ready',
  detail: {
    workerScope: typeof WorkerGlobalScope !== 'undefined' && self instanceof WorkerGlobalScope,
    sharedArrayBuffer: typeof SharedArrayBuffer,
    atomics: typeof Atomics,
    crossOriginIsolated: Boolean(globalThis.crossOriginIsolated)
  }
});
self.addEventListener('message', (event) => {
  const msg = event.data || {};
  if (msg.type !== 'sab-frame-ring:consume') return;
  try {
    const ring = openSharedFrameRing(msg.sab, { label: msg.label || 'browser-sab-frame-ring-worker' });
    const frames = [];
    let combinedChecksum = 0;
    let totalBytes = 0;
    for (;;) {
      const got = ring.waitPopFrame({ timeoutMs: msg.timeoutMs || 1000 });
      if (got.done) break;
      if (!got.frame) continue;
      const frameChecksum = checksum(got.frame.payload);
      combinedChecksum = (combinedChecksum + frameChecksum + got.frame.seq) >>> 0;
      totalBytes += got.frame.payload.byteLength;
      frames.push({ seq: got.frame.seq, bytes: got.frame.payload.byteLength, checksum: frameChecksum });
      if (Number.isInteger(msg.maxFrames) && frames.length >= msg.maxFrames) break;
    }
    self.postMessage({
      type: 'sab-frame-ring:result',
      id: msg.id,
      count: frames.length,
      totalBytes,
      combinedChecksum,
      frames,
      firstFrames: frames.slice(0, 8),
      lastFrames: frames.slice(-8),
      durationMs: Date.now() - startedAt,
      snapshot: ring.snapshot(),
      constructors: { sharedArrayBuffer: typeof SharedArrayBuffer, atomics: typeof Atomics },
      workerScope: typeof WorkerGlobalScope !== 'undefined' && self instanceof WorkerGlobalScope,
      crossOriginIsolated: Boolean(globalThis.crossOriginIsolated)
    });
  } catch (error) {
    self.postMessage({ type: 'sab-frame-ring:error', id: msg.id, error: describeError(error) });
  }
});
