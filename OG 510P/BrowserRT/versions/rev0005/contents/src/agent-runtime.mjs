export const AGENT_PROTOCOL_VERSION = 1;

function errorLike(error) {
  return {
    name: error?.name || 'Error',
    message: error?.message || String(error),
    stack: error?.stack
  };
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
  const payload = message.payload || {};
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
