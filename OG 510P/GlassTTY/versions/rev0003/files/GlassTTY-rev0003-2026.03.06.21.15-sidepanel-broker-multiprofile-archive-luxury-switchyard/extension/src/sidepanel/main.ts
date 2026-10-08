import { makeEnvelope, type Envelope } from '../shared/protocol';

const app = document.getElementById('app');
if (!app) throw new Error('sidepanel root missing');
const root = app as HTMLDivElement;

function card(title: string, body: string): string {
  return `<section class="card"><h2>${title}</h2><pre>${body}</pre></section>`;
}

async function refreshStatus(): Promise<void> {
  const response = await chrome.runtime.sendMessage(makeEnvelope('bridge.status', {})) as Envelope;
  const payload = JSON.stringify(response.payload, null, 2);
  const storage = await chrome.storage.local.get('bridgeState');
  const mirrored = JSON.stringify(storage.bridgeState ?? {}, null, 2);
  root.innerHTML = [
    card('Bridge status', payload),
    card('Mirrored storage state', mirrored),
  ].join('');
}

async function request(type: Envelope['type'], payload: Record<string, unknown> = {}): Promise<void> {
  const response = await chrome.runtime.sendMessage(makeEnvelope(type, payload)) as Envelope;
  const output = document.getElementById('last-response');
  if (output) {
    output.textContent = JSON.stringify(response, null, 2);
  }
  await refreshStatus();
}

window.addEventListener('DOMContentLoaded', async () => {
  document.getElementById('refresh-status')?.addEventListener('click', () => void refreshStatus());
  document.getElementById('read-prompt')?.addEventListener('click', () => void request('prompt.read'));
  document.getElementById('read-latest')?.addEventListener('click', () => void request('transcript.latest'));
  document.getElementById('snapshot')?.addEventListener('click', () => void request('state.snapshot'));
  document.getElementById('debug')?.addEventListener('click', () => void request('debug.dom_candidates'));
  chrome.storage.onChanged.addListener((_changes, areaName) => {
    if (areaName === 'local') {
      void refreshStatus();
    }
  });
  await refreshStatus();
});
