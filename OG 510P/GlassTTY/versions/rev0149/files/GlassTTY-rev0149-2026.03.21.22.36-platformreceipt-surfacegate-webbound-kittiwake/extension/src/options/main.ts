import { makeEnvelope, type Envelope } from '../shared/protocol';

interface BridgeStatusPayload {
  adapters?: Array<{ name: string; origin_patterns: string[]; capabilities: Record<string, boolean> }>;
  supportedTabs?: Array<Record<string, unknown>>;
  selectedTargetTabId?: number | null;
  targetTab?: Record<string, unknown> | null;
  activeTab?: Record<string, unknown>;
}

function setText(id: string, value: string): void {
  const node = document.getElementById(id);
  if (node) node.textContent = value;
}

function setValue(id: string, value: string): void {
  const node = document.getElementById(id) as HTMLTextAreaElement | null;
  if (node) node.value = value;
}

async function bridgeStatus(): Promise<Envelope<BridgeStatusPayload>> {
  return chrome.runtime.sendMessage(makeEnvelope('bridge.status', {})) as Promise<Envelope<BridgeStatusPayload>>;
}

function installHelperText(extensionId: string): string {
  return [
    '# browser-aware native-host install',
    './scripts/install-native-host.sh \\',
    '  --target auto \\',
    '  --extension-id auto',
    '',
    '# inspect what GlassTTY expects before or after install',
    'python scripts/native-host-report.py --pretty',
    '',
    '# launch an isolated profile and preserve native-host/debug context together',
    './scripts/glasstty-profile.sh open main --remote-debugging-port auto chrome://extensions/',
    './scripts/glasstty-profile.sh info main --pretty',
    '',
    '# current unpacked extension id',
    extensionId,
    '# wrapper path default',
    'scripts/native-host-wrapper.sh',
  ].join('\n');
}

async function refresh(): Promise<void> {
  const manifest = chrome.runtime.getManifest();
  const status = await bridgeStatus();
  const payload = status.payload ?? {};
  setText('extension-meta', JSON.stringify({
    id: chrome.runtime.id,
    version: manifest.version,
    minimum_chrome_version: manifest.minimum_chrome_version,
    host_permissions: manifest.host_permissions,
    probe_url: chrome.runtime.getURL('probe/index.html'),
  }, null, 2));
  setText('bridge-status', JSON.stringify(payload, null, 2));
  setText('adapter-registry', JSON.stringify(payload.adapters ?? [], null, 2));
  setValue('install-command', installHelperText(chrome.runtime.id));
}

window.addEventListener('DOMContentLoaded', () => {
  document.getElementById('refresh')?.addEventListener('click', () => { void refresh(); });
  void refresh();
});
