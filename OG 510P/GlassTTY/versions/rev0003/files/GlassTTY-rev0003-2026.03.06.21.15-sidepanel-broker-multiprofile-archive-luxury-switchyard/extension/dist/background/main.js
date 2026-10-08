import { getActiveTab, isSupportedUrl } from '../shared/browser';
import { makeEnvelope, replyTo } from '../shared/protocol';
const HOST_NAME = 'com.glasstty.bridge';
const STORAGE_KEY = 'bridgeState';
let nativePort = null;
function log(...args) {
    console.log('[GlassTTY background]', ...args);
}
async function getBridgeState() {
    const result = await chrome.storage.local.get(STORAGE_KEY);
    return result[STORAGE_KEY] ?? {};
}
async function patchBridgeState(patch) {
    const next = {
        ...(await getBridgeState()),
        ...patch,
        updatedAt: new Date().toISOString(),
    };
    await chrome.storage.local.set({ [STORAGE_KEY]: next });
    return next;
}
function ensureNativePort() {
    if (nativePort)
        return nativePort;
    nativePort = chrome.runtime.connectNative(HOST_NAME);
    nativePort.onMessage.addListener((msg) => {
        void patchBridgeState({ lastNativeMessage: msg }).catch(console.error);
        log('native message', msg);
    });
    nativePort.onDisconnect.addListener(() => {
        log('native port disconnected', chrome.runtime.lastError?.message ?? '');
        void patchBridgeState({ lastError: chrome.runtime.lastError?.message ?? 'native port disconnected' }).catch(console.error);
        nativePort = null;
    });
    return nativePort;
}
async function refreshActiveTabState() {
    const tab = await getActiveTab();
    await patchBridgeState({
        activeTab: {
            id: tab?.id,
            url: tab?.url,
            windowId: tab?.windowId,
            supported: isSupportedUrl(tab?.url),
        },
    });
}
async function sendToActiveContentScript(request) {
    const tab = await getActiveTab();
    if (!tab?.id || !isSupportedUrl(tab.url)) {
        const error = replyTo(request, 'error.report', {
            error: 'no supported active tab',
            active_url: tab?.url ?? null,
        });
        await patchBridgeState({ lastError: error });
        return error;
    }
    try {
        const response = await chrome.tabs.sendMessage(tab.id, {
            ...request,
            tab_id: tab.id,
        });
        await patchBridgeState({ lastContentMessage: response, activeTab: { id: tab.id, url: tab.url, windowId: tab.windowId, supported: true } });
        return response;
    }
    catch (error) {
        const failure = replyTo(request, 'error.report', {
            error: String(error),
            active_url: tab.url ?? null,
        }, tab.id);
        await patchBridgeState({ lastError: failure });
        return failure;
    }
}
async function forwardResponseToNative(response) {
    const port = ensureNativePort();
    port.postMessage(response);
    await patchBridgeState({ lastContentMessage: response });
}
async function handleNativeMessage(message) {
    log('native message', message);
    if (message.type === 'bridge.forward_to_active_tab') {
        const forwarded = message.payload?.request;
        if (!forwarded) {
            const error = replyTo(message, 'error.report', { error: 'bridge.forward_to_active_tab missing payload.request' });
            ensureNativePort().postMessage(error);
            await patchBridgeState({ lastError: error });
            return;
        }
        const response = await sendToActiveContentScript(forwarded);
        await forwardResponseToNative(response);
        return;
    }
    if (message.type === 'bridge.status') {
        await patchBridgeState({ lastNativeMessage: message });
        return;
    }
    log('unhandled native message type', message.type);
}
async function performAction(type, payload = {}) {
    const request = makeEnvelope(type, payload);
    const response = await sendToActiveContentScript(request);
    await forwardResponseToNative(response);
    return response;
}
chrome.runtime.onInstalled.addListener(() => {
    void chrome.sidePanel.setPanelBehavior({ openPanelOnActionClick: true }).catch(console.error);
    void ensureNativePort();
    void refreshActiveTabState();
    log('installed');
});
chrome.runtime.onStartup.addListener(() => {
    ensureNativePort();
    void refreshActiveTabState();
});
chrome.tabs.onActivated.addListener(() => {
    void refreshActiveTabState();
});
chrome.tabs.onUpdated.addListener((_tabId, _changeInfo, _tab) => {
    void refreshActiveTabState();
});
chrome.commands.onCommand.addListener(async (command) => {
    if (command === 'pull-latest-output') {
        await performAction('transcript.latest');
    }
    else if (command === 'pull-current-prompt') {
        await performAction('prompt.read');
    }
    else if (command === 'debug-dom-candidates') {
        await performAction('debug.dom_candidates');
    }
});
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    const fromExtensionPage = !sender.tab;
    if (fromExtensionPage && message.type === 'bridge.status') {
        void refreshActiveTabState()
            .then(() => getBridgeState())
            .then((state) => sendResponse(replyTo(message, 'bridge.status', state)))
            .catch((error) => sendResponse(replyTo(message, 'error.report', { error: String(error) })));
        return true;
    }
    if (fromExtensionPage && ['prompt.read', 'prompt.write', 'prompt.submit', 'transcript.latest', 'selection.read', 'debug.dom_candidates', 'state.snapshot'].includes(message.type)) {
        void performAction(message.type, message.payload)
            .then((response) => sendResponse(response))
            .catch((error) => sendResponse(replyTo(message, 'error.report', { error: String(error) })));
        return true;
    }
    void patchBridgeState({
        lastContentMessage: message,
        lastAdapterDetected: message.type === 'adapter.detected' ? message : undefined,
        lastError: message.type === 'error.report' ? message : undefined,
    }).catch(console.error);
    try {
        const port = ensureNativePort();
        port.postMessage(message);
        sendResponse({ ok: true });
    }
    catch (error) {
        sendResponse({ ok: false, error: String(error) });
    }
    return true;
});
