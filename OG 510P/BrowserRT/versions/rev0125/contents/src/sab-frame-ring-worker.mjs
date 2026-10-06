import { parentPort, workerData } from 'node:worker_threads';
import { performance } from 'node:perf_hooks';
import { openSharedFrameRing } from './sab-frame-ring.mjs';

function checksum(bytes) {
  let out = 2166136261 >>> 0;
  for (const b of bytes) {
    out ^= b;
    out = Math.imul(out, 16777619) >>> 0;
  }
  return out >>> 0;
}

const started = performance.now();
const ring = openSharedFrameRing(workerData.sab, { label: workerData.label || 'sab-frame-ring-worker' });
const frames = [];
let combinedChecksum = 0;
let totalBytes = 0;
for (;;) {
  const got = ring.waitPopFrame({ timeoutMs: workerData.timeoutMs ?? 1000 });
  if (got.done) break;
  if (!got.frame) continue;
  const frameChecksum = checksum(got.frame.payload);
  combinedChecksum = (combinedChecksum + frameChecksum + got.frame.seq) >>> 0;
  totalBytes += got.frame.payload.byteLength;
  frames.push({ seq: got.frame.seq, bytes: got.frame.payload.byteLength, checksum: frameChecksum });
}
parentPort.postMessage({
  status: 'passed',
  count: frames.length,
  totalBytes,
  combinedChecksum,
  frames,
  firstFrames: frames.slice(0, 8),
  lastFrames: frames.slice(-8),
  durationMs: Math.round(performance.now() - started),
  snapshot: ring.snapshot()
});
