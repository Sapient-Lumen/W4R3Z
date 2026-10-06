if (typeof self !== 'undefined' && !(globalThis.process?.versions?.node)) {
  await import('./browser-agent-worker.mjs');
} else {
  await import('./node-agent-worker.mjs');
}
