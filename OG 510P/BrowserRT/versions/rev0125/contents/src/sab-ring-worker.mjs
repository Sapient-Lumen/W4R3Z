import { parentPort, workerData } from 'node:worker_threads';
import { openSharedInt32Ring } from './sab-ring.mjs';

const ring = openSharedInt32Ring(workerData.sab, { label: workerData.label || 'sab-ring-worker' });
const values = [];
let sum = 0;
const startedAt = Date.now();
for (;;) {
  const item = ring.waitPop({ timeoutMs: workerData.timeoutMs || 1000 });
  if (item.done) break;
  values.push(item.value);
  sum += item.value;
}
const endedAt = Date.now();
parentPort.postMessage({
  type: 'sab-ring-result',
  count: values.length,
  sum,
  values,
  durationMs: endedAt - startedAt,
  snapshot: ring.snapshot()
});
