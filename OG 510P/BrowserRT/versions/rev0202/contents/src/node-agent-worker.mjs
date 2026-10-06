import { parentPort } from 'node:worker_threads';
import { errorMessage, handleAgentCall, resultMessage } from './agent-runtime.mjs';
if (!parentPort) throw new Error('BrowserRT node agent worker requires parentPort');
const controllers = new Map();
parentPort.postMessage({ type: 'agent:ready', detail: { backend: 'node-worker-threads', cancellation: 'per-call-abort-controller' } });
parentPort.on('message', async (message) => {
  if (message && message.type === 'agent:cancel') {
    const controller = controllers.get(message.id);
    if (controller) {
      controller.abort(message.reason || 'cancelled');
      parentPort.postMessage({ type: 'agent:cancelled', id: message.id, reason: message.reason || 'cancelled' });
    }
    return;
  }
  if (message && message.type === 'agent:call' && message.op === 'crash-now') {
    parentPort.postMessage({ type: 'agent:trace', kind: 'agent:crashing', detail: { reason: 'crash-now' } });
    process.exit(12);
    return;
  }
  if (!message || message.type !== 'agent:call') return;
  const controller = new AbortController();
  controllers.set(message.id, controller);
  try {
    const result = await handleAgentCall(message, { signal: controller.signal });
    parentPort.postMessage(resultMessage(message, result));
  } catch (error) {
    parentPort.postMessage(errorMessage(message, error));
  } finally {
    controllers.delete(message.id);
  }
});
