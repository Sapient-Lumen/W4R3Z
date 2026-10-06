export const AGENT_PROTOCOL_VERSION = 1;

function errorLike(error) {
  return {
    name: error?.name || 'Error',
    message: error?.message || String(error),
    stack: error?.stack,
    code: error?.code ?? null
  };
}

function throwIfAborted(signal) {
  if (!signal?.aborted) return;
  const reason = signal.reason;
  if (reason instanceof Error) throw reason;
  const err = new Error(reason ? String(reason) : 'BrowserRT agent operation aborted');
  err.name = 'AbortError';
  err.code = 'BRT_AGENT_OPERATION_ABORTED';
  throw err;
}

function sleep(ms, signal) {
  const timeoutMs = Math.max(0, Math.floor(Number(ms) || 0));
  throwIfAborted(signal);
  if (timeoutMs === 0) return Promise.resolve();
  return new Promise((resolve, reject) => {
    let timer = null;
    const cleanup = () => {
      if (timer) clearTimeout(timer);
      if (signal && onAbort) signal.removeEventListener('abort', onAbort);
    };
    const onAbort = () => {
      cleanup();
      try { throwIfAborted(signal); } catch (error) { reject(error); }
    };
    if (signal) signal.addEventListener('abort', onAbort, { once: true });
    timer = setTimeout(() => {
      cleanup();
      resolve();
    }, timeoutMs);
  });
}

function sumUint32(buffer) {
  if (!(buffer instanceof ArrayBuffer)) {
    throw new Error('sum-u32 requires an ArrayBuffer payload');
  }
  if (buffer.byteLength % 4 !== 0) {
    throw new Error('sum-u32 requires a byte length divisible by four');
  }
  const view = new Uint32Array(buffer);
  let sum = 0;
  for (let i = 0; i < view.length; i += 1) sum += view[i];
  return { sum, count: view.length, bytes: buffer.byteLength };
}

export async function handleAgentCall(message, controls = {}) {
  if (!message || message.type !== 'agent:call') {
    throw new Error('Expected BrowserRT agent:call message');
  }
  const signal = controls.signal || null;
  const payload = message.payload || {};
  throwIfAborted(signal);
  if (message.op === 'ping') {
    return {
      pong: true,
      protocol: AGENT_PROTOCOL_VERSION,
      payload,
      envelope: message.envelope || null
    };
  }
  if (message.op === 'sum-u32') {
    return {
      ...sumUint32(payload.buffer),
      ref: payload.ref || payload.objectRef || null,
      envelope: message.envelope || null
    };
  }
  if (message.op === 'busy-loop') {
    const durationMs = Math.max(0, Math.min(5000, Number(payload.durationMs || 0)));
    const started = Date.now();
    // Intentionally non-cooperative: this simulates user code that ignores
    // AbortSignal while the parent-side WorkerAgent proves escalation can kill
    // abandoned work instead of merely recording a timeout.
    while (Date.now() - started < durationMs) {}
    throwIfAborted(signal);
    return { busyLoopMs: durationMs, elapsedMs: Date.now() - started, envelope: message.envelope || null };
  }
  if (message.op === 'delayed-echo') {
    const delayMs = Math.max(0, Number(payload.delayMs || 0));
    const stepMs = Math.max(1, Math.min(25, Number(payload.stepMs || 10)));
    let elapsedMs = 0;
    while (elapsedMs < delayMs) {
      throwIfAborted(signal);
      const chunk = Math.min(stepMs, delayMs - elapsedMs);
      await sleep(chunk, signal);
      elapsedMs += chunk;
    }
    throwIfAborted(signal);
    return { echoed: payload.value ?? null, delayMs, cancelled: false, envelope: message.envelope || null };
  }
  if (message.op === 'crash-now') {
    if (typeof controls.crash === 'function') {
      await controls.crash();
      return { crashing: true };
    }
    throw new Error('crash-now requested but no crash control exists');
  }
  throw new Error(`Unsupported BrowserRT agent op: ${message.op}`);
}

export function resultMessage(message, result) {
  return { type: 'agent:result', id: message.id, result };
}

export function errorMessage(message, error) {
  return { type: 'agent:error', id: message?.id || 'unknown', error: errorLike(error) };
}
