import { makeEnvelope } from '../shared/protocol';
function setText(id, value) {
    const node = document.getElementById(id);
    if (node)
        node.textContent = value;
}
function setValue(id, value) {
    const node = document.getElementById(id);
    if (node)
        node.value = value;
}
async function bridgeStatus() {
    return chrome.runtime.sendMessage(makeEnvelope('bridge.status', {}));
}
function installHelperText(extensionId) {
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
async function refresh() {
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
