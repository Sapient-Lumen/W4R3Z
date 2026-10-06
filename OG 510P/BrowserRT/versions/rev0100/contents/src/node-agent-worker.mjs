import { parentPort } from 'node:worker_threads';
import { errorMessage, handleAgentCall, resultMessage } from './agent-runtime.mjs';

if (!parentPort) throw new Error('BrowserRT node agent worker requires parentPort');

parentPort.postMessage({ type: 'agent:ready', detail: { backend: 'node-worker-threads' } });

parentPort.on('message', async (message) => {
  if (message && message.type === 'agent:call' && message.op === 'crash-now') {
    parentPort.postMessage({ type: 'agent:trace', kind: 'agent:crashing', detail: { reason: 'crash-now' } });
    process.exit(12);
    return;
  }
  try {
    const result = await handleAgentCall(message);
    parentPort.postMessage(resultMessage(message, result));
  } catch (error) {
    parentPort.postMessage(errorMessage(message, error));
  }
});
