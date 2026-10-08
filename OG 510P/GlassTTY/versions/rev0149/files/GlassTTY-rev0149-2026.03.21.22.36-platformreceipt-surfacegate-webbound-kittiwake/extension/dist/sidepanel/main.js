import { makeEnvelope } from '../shared/protocol';
import { contentReceiverKey, contentReceiverLabel } from '../shared/receivers';
const app = document.getElementById('app');
if (!app)
    throw new Error('sidepanel root missing');
const root = app;
function card(title, body) {
    return `<section class="card"><h2>${title}</h2><pre>${body}</pre></section>`;
}
function receiverHtml(tab) {
    const receivers = tab.receivers ?? [];
    if (!receivers.length)
        return '';
    return `
    <div class="card" style="margin-top:0.5rem; background:#11151c;">
      <div class="row" style="justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
        <strong>Receivers</strong>
        <button type="button" data-clear-receiver-override="${tab.tabId}">Auto select</button>
      </div>
      <small>${[
        tab.selectedReceiverLabel ? `active:${tab.selectedReceiverLabel}` : null,
        tab.receiverOverrideStatus ? `override:${tab.receiverOverrideStatus}` : null,
        tab.receiverSelectionPolicy ? `policy:${tab.receiverSelectionPolicy}` : null,
    ].filter(Boolean).join(' · ')}</small>
      <div class="list" style="margin-top:0.5rem;">
        ${receivers.map((receiver) => {
        const key = contentReceiverKey(receiver) ?? '';
        const checked = Boolean(tab.receiverOverrideKey && key === tab.receiverOverrideKey);
        const selected = Boolean(key && tab.selectedReceiverKey === key);
        return `
            <label class="tab-row" style="padding-left:0; border-top:1px solid rgba(255,255,255,0.06);">
              <input type="radio" name="receiver-${tab.tabId}" value="${key}" data-receiver-tab-id="${tab.tabId}" ${checked ? 'checked' : ''} />
              <span>
                <strong>${contentReceiverLabel(receiver)}</strong>
                <small>${[
            key,
            receiver.adapter ? `adapter:${receiver.adapter}` : null,
            receiver.frameType ? `type:${receiver.frameType}` : null,
            typeof receiver.frameDepth === 'number' ? `depth:${receiver.frameDepth}` : null,
            typeof receiver.parentFrameId === 'number' && receiver.parentFrameId >= 0 ? `parent:${receiver.parentFrameId}` : null,
            receiver.frameOrigin ? `origin:${receiver.frameOrigin}` : null,
            selected ? 'selected' : null,
        ].filter(Boolean).join(' · ')}</small>
                ${receiver.framePathLabel ? `<small>path:${receiver.framePathLabel}</small>` : ''}
                ${receiver.frameUrl ? `<small>${receiver.frameUrl}</small>` : ''}
              </span>
            </label>
          `;
    }).join('')}
      </div>
    </div>
  `;
}
function adaptersHtml(adapters = []) {
    if (!adapters.length)
        return '';
    return `
    <section class="card">
      <h2>Adapters</h2>
      <div class="list">
        ${adapters.map((adapter) => `
          <div class="tab-row">
            <span>
              <strong>${adapter.name}</strong>
              <small>${adapter.origin_patterns.join(', ')}</small>
              <small>${Object.entries(adapter.capabilities).filter(([, enabled]) => enabled).map(([name]) => name).join(', ')}</small>
            </span>
          </div>
        `).join('')}
      </div>
    </section>
  `;
}
function supportedTabsHtml(tabs = [], targetTabId) {
    if (tabs.length === 0)
        return '<section class="card"><h2>Supported tabs</h2><p>No supported tabs observed yet.</p></section>';
    return `
    <section class="card">
      <div class="row" style="justify-content: space-between; align-items: center; margin-bottom: 0.75rem;">
        <h2 style="margin-bottom: 0;">Supported tabs</h2>
        <button id="clear-target" type="button">Clear target</button>
      </div>
      <div class="list">
        ${tabs.map((tab) => `
          <div class="tab-row" style="padding:0;">
            <label class="tab-row">
              <input type="radio" name="target-tab" value="${tab.tabId}" ${tab.tabId === targetTabId ? 'checked' : ''} />
              <span>
                <strong>#${tab.tabId} ${tab.title ? `— ${tab.title}` : ''}</strong>
                ${tab.adapter ? `<em>${tab.adapter}</em>` : ''}
                <small>${tab.url ?? ''}</small>
                <small>${[
        tab.receiverReady === false ? 'receiver-missing' : null,
        tab.discarded ? 'discarded' : null,
        tab.frozen ? 'frozen' : null,
        typeof tab.receiverCount === 'number' ? `receivers:${tab.receiverCount}` : null,
        typeof tab.readyReceiverCount === 'number' ? `ready:${tab.readyReceiverCount}` : null,
        tab.receiverInventoryStatus ? `inventory:${tab.receiverInventoryStatus}` : null,
        tab.receiverSelectionPolicy ? `policy:${tab.receiverSelectionPolicy}` : null,
        tab.receiverOverrideStatus && tab.receiverOverrideStatus !== 'none' ? `override:${tab.receiverOverrideStatus}` : null,
        tab.selectedReceiverLabel ? `selected:${tab.selectedReceiverLabel}` : null,
        Array.isArray(tab.receiverFrameIds) && tab.receiverFrameIds.length ? `frames:${tab.receiverFrameIds.join(',')}` : null,
        tab.documentId ? `doc:${tab.documentId}` : null,
        typeof tab.frameId === 'number' ? `frame:${tab.frameId}` : null,
    ].filter(Boolean).join(' · ')}</small>
              </span>
            </label>
            ${(tab.receivers?.length ?? 0) > 1 || Boolean(tab.receiverOverrideKey) ? receiverHtml(tab) : ''}
          </div>
        `).join('')}
      </div>
    </section>
  `;
}
function traceHtml(events = []) {
    if (!events.length)
        return '<section class="card"><h2>Recent bridge trace</h2><p>No extension-side trace entries yet.</p></section>';
    return card('Recent bridge trace', JSON.stringify(events, null, 2));
}
function nativeConnectionHtml(nativeConnection) {
    if (!nativeConnection)
        return '';
    return card('Native bridge', JSON.stringify(nativeConnection, null, 2));
}
function overflowHtml(lastOversizedHostMessage) {
    if (!lastOversizedHostMessage)
        return '';
    return card('Host overflow guard', JSON.stringify(lastOversizedHostMessage, null, 2));
}
function persistentDiagnosticsHtml(persistentDiagnostics) {
    if (!persistentDiagnostics)
        return '';
    return card('Persistent local diagnostics', JSON.stringify(persistentDiagnostics, null, 2));
}
function nativeStatusSnapshotHtml(snapshot, error) {
    if (!snapshot && !error)
        return '';
    return card('Native host local status snapshot', JSON.stringify({ snapshot, error }, null, 2));
}
function selectedTabId() {
    const selected = document.querySelector('input[name="target-tab"]:checked');
    return selected ? Number(selected.value) : undefined;
}
async function bridgeRequest(type, payload = {}) {
    return chrome.runtime.sendMessage(makeEnvelope(type, payload));
}
async function refreshStatus() {
    const [response, traceResponse, storage, localStorage] = await Promise.all([
        bridgeRequest('bridge.status'),
        bridgeRequest('bridge.trace', { limit: 30 }),
        chrome.storage.session.get(['bridgeState', 'bridgeTrace']),
        chrome.storage.local.get(['bridgePersistentHistory']),
    ]);
    const payload = response.payload ?? {};
    const tracePayload = traceResponse.payload ?? {};
    const mirrored = JSON.stringify(storage.bridgeState ?? {}, null, 2);
    const mirroredLocal = JSON.stringify(localStorage.bridgePersistentHistory ?? {}, null, 2);
    root.innerHTML = [
        card('Bridge status', JSON.stringify(payload, null, 2)),
        nativeConnectionHtml(payload.nativeConnection),
        persistentDiagnosticsHtml(payload.persistentDiagnostics),
        nativeStatusSnapshotHtml(payload.lastNativeStatusSnapshot, payload.lastNativeStatusError),
        overflowHtml(payload.lastOversizedHostMessage),
        supportedTabsHtml(payload.supportedTabs, payload.selectedTargetTabId),
        traceHtml(tracePayload.events),
        adaptersHtml(payload.adapters),
        card('Mirrored session state', mirrored),
        card('Mirrored local history', mirroredLocal),
    ].join('');
    document.querySelectorAll('input[name="target-tab"]').forEach((input) => {
        input.addEventListener('change', () => {
            if (input.checked)
                void bridgeRequest('bridge.set_target_tab', { tab_id: Number(input.value) }).then(refreshStatus).catch(console.error);
        });
    });
    document.querySelectorAll('input[data-receiver-tab-id]').forEach((input) => {
        input.addEventListener('change', () => {
            if (!input.checked)
                return;
            const tabId = Number(input.dataset.receiverTabId);
            void bridgeRequest('bridge.set_receiver_override', { tab_id: tabId, receiver_key: input.value }).then(refreshStatus).catch(console.error);
        });
    });
    document.querySelectorAll('button[data-clear-receiver-override]').forEach((button) => {
        button.addEventListener('click', () => {
            const tabId = Number(button.dataset.clearReceiverOverride);
            void bridgeRequest('bridge.clear_receiver_override', { tab_id: tabId }).then(refreshStatus).catch(console.error);
        });
    });
    document.getElementById('clear-target')?.addEventListener('click', () => {
        void bridgeRequest('bridge.clear_target_tab', {}).then(refreshStatus).catch(console.error);
    });
}
async function request(type, payload = {}) {
    const tabId = selectedTabId();
    const response = await chrome.runtime.sendMessage(makeEnvelope(type, { ...payload, ...(tabId ? { tab_id: tabId } : {}) }));
    const output = document.getElementById('last-response');
    if (output)
        output.textContent = JSON.stringify(response, null, 2);
    await refreshStatus();
}
window.addEventListener('DOMContentLoaded', async () => {
    document.getElementById('refresh-status')?.addEventListener('click', () => void refreshStatus());
    document.getElementById('read-prompt')?.addEventListener('click', () => void request('prompt.read'));
    document.getElementById('read-latest')?.addEventListener('click', () => void request('transcript.latest'));
    document.getElementById('snapshot')?.addEventListener('click', () => void request('state.snapshot'));
    document.getElementById('contexts')?.addEventListener('click', () => void request('bridge.contexts'));
    document.getElementById('trace')?.addEventListener('click', () => void request('bridge.trace', { limit: 30 }));
    document.getElementById('debug')?.addEventListener('click', () => void request('debug.dom_candidates'));
    document.getElementById('capture-fixture')?.addEventListener('click', () => void request('fixture.capture'));
    document.getElementById('write-prompt')?.addEventListener('click', () => {
        const text = document.getElementById('prompt-draft')?.value ?? '';
        void request('prompt.write', { text });
    });
    document.getElementById('submit-prompt')?.addEventListener('click', () => void request('prompt.submit'));
    chrome.storage.onChanged.addListener((_changes, areaName) => {
        if (areaName === 'session' || areaName === 'local')
            void refreshStatus();
    });
    await refreshStatus();
});
