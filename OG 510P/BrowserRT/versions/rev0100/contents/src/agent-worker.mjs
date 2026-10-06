// Compatibility entrypoint. BrowserRT now keeps the shared operation runtime in
// agent-runtime.mjs and picks a backend-specific shell at runtime.
if (typeof self !== 'undefined' && !(globalThis.process?.versions?.node)) {
  await import('./browser-agent-worker.mjs');
} else {
  await import('./node-agent-worker.mjs');
}
