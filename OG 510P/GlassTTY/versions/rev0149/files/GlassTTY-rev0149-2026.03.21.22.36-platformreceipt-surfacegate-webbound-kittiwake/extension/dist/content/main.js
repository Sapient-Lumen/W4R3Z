import { detectAdapter } from '../adapters';
import { makeEnvelope, replyTo } from '../shared/protocol';
const adapter = detectAdapter(window.location.href, document);
let lastTranscript = '';
const globalScope = globalThis;
const CONTENT_BOOTSTRAP_VERSION = 'rev0055';
function log(...args) {
    console.log('[GlassTTY content]', ...args);
}
function markDocument() {
    if (!adapter)
        return;
    document.documentElement.setAttribute('data-glasstty-adapter', adapter.name);
}
function sendAdapterDetected() {
    if (!adapter)
        return;
    chrome.runtime.sendMessage(makeEnvelope('adapter.detected', {
        adapter: adapter.name,
        url: window.location.href,
    }));
}
function startTranscriptObserver() {
    if (!adapter)
        return;
    const emit = () => {
        const latest = adapter.readLatestOutput(document) || '';
        if (!latest || latest === lastTranscript)
            return;
        lastTranscript = latest;
        chrome.runtime.sendMessage(makeEnvelope('transcript.delta', {
            adapter: adapter.name,
            text: latest,
            length: latest.length,
            url: window.location.href,
        }));
    };
    emit();
    const observer = new MutationObserver(() => {
        window.setTimeout(emit, 50);
    });
    observer.observe(document.body, { childList: true, subtree: true, characterData: true });
}
function installRuntimeLane() {
    chrome.runtime.onMessage.addListener((message, _sender, sendResponse) => {
        if (!adapter) {
            sendResponse(replyTo(message, 'error.report', { error: 'no adapter matched current page' }));
            return true;
        }
        switch (message.type) {
            case 'prompt.read':
                sendResponse(replyTo(message, 'prompt.read', { text: adapter.readPrompt(document), adapter: adapter.name }));
                return true;
            case 'prompt.write':
                sendResponse(replyTo(message, 'prompt.write', { ok: adapter.writePrompt(document, String(message.payload?.text ?? '')), adapter: adapter.name }));
                return true;
            case 'prompt.submit':
                sendResponse(replyTo(message, 'prompt.submit', { ok: adapter.submitPrompt?.(document) ?? false, adapter: adapter.name }));
                return true;
            case 'transcript.latest':
                sendResponse(replyTo(message, 'transcript.latest', { text: adapter.readLatestOutput(document), adapter: adapter.name }));
                return true;
            case 'selection.read':
                sendResponse(replyTo(message, 'selection.read', { text: adapter.readSelection(window), adapter: adapter.name }));
                return true;
            case 'debug.dom_candidates':
                sendResponse(replyTo(message, 'debug.dom_candidates', { ...adapter.debugCandidates(document), adapter: adapter.name }));
                return true;
            case 'fixture.capture':
                sendResponse(replyTo(message, 'fixture.capture', adapter.captureFixture ? adapter.captureFixture(document, window) : {
                    adapter: adapter.name,
                    url: window.location.href,
                    title: document.title,
                    prompt: adapter.readPrompt(document),
                    latest_output: adapter.readLatestOutput(document),
                    selection: adapter.readSelection(window),
                    candidates: adapter.debugCandidates(document),
                }));
                return true;
            case 'state.snapshot':
                sendResponse(replyTo(message, 'state.snapshot', {
                    adapter: adapter.name,
                    prompt: adapter.readPrompt(document),
                    latest_output: adapter.readLatestOutput(document),
                    selection: adapter.readSelection(window),
                    url: window.location.href,
                }));
                return true;
            default:
                sendResponse(replyTo(message, 'error.report', { error: `unsupported content-script request: ${message.type}`, adapter: adapter.name }));
                return true;
        }
    });
}
function bootstrapContentRuntime() {
    if (globalScope.__glassttyContentBootstrap) {
        markDocument();
        sendAdapterDetected();
        log('bootstrap reused', globalScope.__glassttyContentBootstrap);
        return;
    }
    globalScope.__glassttyContentBootstrap = {
        version: CONTENT_BOOTSTRAP_VERSION,
        adapterName: adapter?.name,
        bootedAt: new Date().toISOString(),
    };
    installRuntimeLane();
    if (adapter) {
        markDocument();
        log('adapter detected', adapter.name);
        sendAdapterDetected();
        startTranscriptObserver();
    }
    else {
        log('no adapter matched');
    }
}
bootstrapContentRuntime();
