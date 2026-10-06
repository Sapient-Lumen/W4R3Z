import { openSharedInt32Ring } from './sab-ring.mjs';
const startedAt = Date.now();
function describeError(error) {
  return {
    name: error?.name || 'Error',
    message: error?.message || String(error),
    stack: error?.stack || null
  };
}
self.postMessage({
  type: 'sab-ring:ready',
  detail: {
    workerScope: typeof WorkerGlobalScope !== 'undefined' && self instanceof WorkerGlobalScope,
    sharedArrayBuffer: typeof SharedArrayBuffer,
    atomics: typeof Atomics,
    crossOriginIsolated: Boolean(globalThis.crossOriginIsolated)
  }
});
self.addEventListener('message', (event) => {
  const msg = event.data || {};
  if (msg.type !== 'sab-ring:consume') return;
  try {
    const ring = openSharedInt32Ring(msg.sab, { label: msg.label || 'browser-sab-ring-worker' });
    const values = [];
    let sum = 0;
    for (;;) {
      const item = ring.waitPop({ timeoutMs: msg.timeoutMs || 1000 });
      if (item.done) break;
      values.push(item.value);
      sum += item.value;
      if (Number.isInteger(msg.maxValues) && values.length >= msg.maxValues) break;
    }
    self.postMessage({
      type: 'sab-ring:result',
      id: msg.id,
      count: values.length,
      sum,
      values,
      durationMs: Date.now() - startedAt,
      snapshot: ring.snapshot(),
      constructors: { sharedArrayBuffer: typeof SharedArrayBuffer, atomics: typeof Atomics },
      workerScope: typeof WorkerGlobalScope !== 'undefined' && self instanceof WorkerGlobalScope,
      crossOriginIsolated: Boolean(globalThis.crossOriginIsolated)
    });
  } catch (error) {
    self.postMessage({ type: 'sab-ring:error', id: msg.id, error: describeError(error) });
  }
});
