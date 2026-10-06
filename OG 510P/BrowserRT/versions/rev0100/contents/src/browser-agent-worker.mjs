import { errorMessage, handleAgentCall, resultMessage } from './agent-runtime.mjs';

self.postMessage({ type: 'agent:ready', detail: { backend: 'browser-worker' } });

self.onmessage = async (event) => {
  const message = event.data;
  if (message && message.type === 'agent:call' && message.op === 'crash-now') {
    self.postMessage({ type: 'agent:trace', kind: 'agent:crashing', detail: { reason: 'crash-now' } });
    self.close();
    return;
  }
  try {
    const result = await handleAgentCall(message);
    self.postMessage(resultMessage(message, result));
  } catch (error) {
    self.postMessage(errorMessage(message, error));
  }
};
