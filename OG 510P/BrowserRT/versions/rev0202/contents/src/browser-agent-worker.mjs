import { errorMessage, handleAgentCall, resultMessage } from './agent-runtime.mjs';
const controllers = new Map();
self.postMessage({ type: 'agent:ready', detail: { backend: 'browser-worker', cancellation: 'per-call-abort-controller' } });
self.onmessage = async (event) => {
  const message = event.data;
  if (message && message.type === 'agent:cancel') {
    const controller = controllers.get(message.id);
    if (controller) {
      controller.abort(message.reason || 'cancelled');
      self.postMessage({ type: 'agent:cancelled', id: message.id, reason: message.reason || 'cancelled' });
    }
    return;
  }
  if (message && message.type === 'agent:call' && message.op === 'crash-now') {
    self.postMessage({ type: 'agent:trace', kind: 'agent:crashing', detail: { reason: 'crash-now' } });
    self.close();
    return;
  }
  if (!message || message.type !== 'agent:call') return;
  const controller = new AbortController();
  controllers.set(message.id, controller);
  try {
    const result = await handleAgentCall(message, { signal: controller.signal });
    self.postMessage(resultMessage(message, result));
  } catch (error) {
    self.postMessage(errorMessage(message, error));
  } finally {
    controllers.delete(message.id);
  }
};
