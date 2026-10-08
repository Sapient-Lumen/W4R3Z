import { detectAdapter } from '../adapters';
import { getSurfaceOverrides, setSurfaceOverrides, type SurfaceOverrides } from '../adapters/chatgpt';
import { makeEnvelope, replyTo, type Envelope } from '../shared/protocol';
import type { PageAdapter } from '../adapters/base';

let adapter: PageAdapter | null = detectAdapter(window.location.href, document);
let lastTranscript = '';
let transcriptObserver: MutationObserver | null = null;
let adapterWatcher: MutationObserver | null = null;
let lastAdapterName: string | null = adapter?.name ?? null;
let lastAdapterUrl = window.location.href;

type GlassTTYContentBootstrap = {
  version: string;
  adapterName?: string;
  bootedAt: string;
};

const globalScope = globalThis as typeof globalThis & {
  __glassttyContentBootstrap?: GlassTTYContentBootstrap;
};
const CONTENT_BOOTSTRAP_VERSION = 'rev0059';

const SURFACE_OVERRIDES_KEY = 'glasstty_surface_overrides';

/**
 * Chunked attachment transfer.
 *
 * Chrome's native-messaging host->extension limit is 1 MB. A 70 MB package
 * therefore cannot cross the bridge in one message — this is the exact wall that
 * forced the userscript queuer to stand up a whole local HTTP file server and
 * fetch the archive from inside the page. GlassTTY does not need a server: the
 * CLI splits the file, the chunks stream over the broker we already have, and the
 * content script reassembles them here.
 *
 * Buffers live in the content script (not the background worker) because MV3 can
 * evict the worker mid-transfer; the page's script survives as long as the page does.
 */
type AttachTransfer = {
  name: string;
  mime: string;
  size: number;
  chunks: (string | undefined)[];
  received: number;
  composer_keys_before: string[];
  input_files_before: number;
  known_chip_keys_before: string[];
  expected_name_visible_before: boolean;
  created_at: number;
};

const attachTransfers = new Map<string, AttachTransfer>();
const ATTACH_CHUNK_BYTES = 384 * 1024;
const MAX_ACTIVE_ATTACH_TRANSFERS = 4;
const MAX_ATTACH_CHUNKS = 4096;
const MAX_ATTACHMENT_BYTES = 512 * 1024 * 1024;
const MAX_ATTACH_CHUNK_BASE64 = 4 * Math.ceil(ATTACH_CHUNK_BYTES / 3);
const ATTACH_TRANSFER_TTL_MS = 30 * 60 * 1000;

function pruneAttachTransfers(now = Date.now()): void {
  for (const [transferId, transfer] of attachTransfers) {
    if (now - transfer.created_at > ATTACH_TRANSFER_TTL_MS) attachTransfers.delete(transferId);
  }
}

function decodeAttachmentChunks(chunks: (string | undefined)[], expectedSize: number): Uint8Array {
  const out = new Uint8Array(expectedSize);
  let offset = 0;
  for (let index = 0; index < chunks.length; index += 1) {
    const encoded = chunks[index];
    if (encoded === undefined) throw new Error(`attachment chunk ${index} is missing`);
    const binary = atob(encoded);
    if (offset + binary.length > expectedSize) throw new Error('decoded attachment exceeds declared size');
    for (let byteIndex = 0; byteIndex < binary.length; byteIndex += 1) {
      out[offset + byteIndex] = binary.charCodeAt(byteIndex);
    }
    offset += binary.length;
    chunks[index] = undefined;
  }
  if (offset !== expectedSize) throw new Error(`decoded attachment has ${offset} bytes, expected ${expectedSize}`);
  return out;
}

// Overrides live in extension storage so they survive reloads and apply to every
// ChatGPT tab at once. They are cached in-memory because the adapter's action
// path is synchronous; storage.onChanged keeps the cache fresh.
function loadSurfaceOverrides(): void {
  chrome.storage.local.get(SURFACE_OVERRIDES_KEY).then((stored) => {
    const value = stored?.[SURFACE_OVERRIDES_KEY];
    if (value && typeof value === 'object') setSurfaceOverrides(value as SurfaceOverrides);
  }).catch(() => undefined);
}

chrome.storage.onChanged.addListener((changes, area) => {
  if (area !== 'local' || !(SURFACE_OVERRIDES_KEY in changes)) return;
  const next = changes[SURFACE_OVERRIDES_KEY]?.newValue;
  setSurfaceOverrides((next && typeof next === 'object' ? next : {}) as SurfaceOverrides);
  log('surface overrides updated', next);
});

function log(...args: unknown[]): void {
  console.log('[GlassTTY content]', ...args);
}

function markDocument(): void {
  if (!adapter) {
    document.documentElement.removeAttribute('data-glasstty-adapter');
    return;
  }
  document.documentElement.setAttribute('data-glasstty-adapter', adapter.name);
}

function sendAdapterDetected(): void {
  if (!adapter) return;
  chrome.runtime.sendMessage(makeEnvelope('adapter.detected', {
    adapter: adapter.name,
    url: window.location.href,
  }));
}

function attemptIdFromMessage(message: Envelope): string | undefined {
  const payload = message.payload as { attempt_id?: unknown; attemptId?: unknown; run_id?: unknown; runId?: unknown } | undefined;
  const raw = payload?.attempt_id ?? payload?.attemptId ?? payload?.run_id ?? payload?.runId;
  return typeof raw === 'string' && raw.trim() ? raw.trim() : undefined;
}

function withAttemptMetadata<T extends object>(payload: T, attemptId: string | undefined): T & { attempt_id?: string; metadata?: Record<string, unknown> } {
  if (!attemptId) return payload;
  const record = payload as Record<string, unknown>;
  const metadata = typeof record.metadata === 'object' && record.metadata !== null && !Array.isArray(record.metadata)
    ? { ...(record.metadata as Record<string, unknown>), attempt_id: attemptId }
    : { attempt_id: attemptId };
  return { ...record, attempt_id: attemptId, metadata } as T & { attempt_id: string; metadata: Record<string, unknown> };
}

function resolveAdapter(reason = 'resolve'): PageAdapter | null {
  const next = detectAdapter(window.location.href, document);
  const nextName = next?.name ?? null;
  const urlChanged = window.location.href !== lastAdapterUrl;
  const adapterChanged = nextName !== lastAdapterName;
  adapter = next;
  if (globalScope.__glassttyContentBootstrap) {
    globalScope.__glassttyContentBootstrap.adapterName = adapter?.name;
  }
  markDocument();
  if (adapterChanged || urlChanged) {
    log(adapter ? 'adapter detected' : 'no adapter matched', { adapter: adapter?.name ?? null, reason, url: window.location.href });
    lastAdapterName = nextName;
    lastAdapterUrl = window.location.href;
    lastTranscript = '';
    sendAdapterDetected();
    if (adapter) startTranscriptObserver();
  }
  return adapter;
}

function startTranscriptObserver(): void {
  if (transcriptObserver) return;

  const emit = () => {
    const activeAdapter = resolveAdapter('transcript');
    if (!activeAdapter) return;
    const latest = activeAdapter.readLatestOutput(document) || '';
    if (!latest || latest === lastTranscript) return;
    lastTranscript = latest;
    chrome.runtime.sendMessage(makeEnvelope('transcript.delta', {
      adapter: activeAdapter.name,
      text: latest,
      length: latest.length,
      url: window.location.href,
    }));
  };

  emit();
  transcriptObserver = new MutationObserver(() => {
    window.setTimeout(emit, 50);
  });
  if (document.body) {
    transcriptObserver.observe(document.body, { childList: true, subtree: true, characterData: true });
  }
}

function startAdapterWatcher(): void {
  if (adapterWatcher) return;
  const sync = () => window.setTimeout(() => resolveAdapter('dom-or-route-change'), 50);
  adapterWatcher = new MutationObserver(sync);
  if (document.body) {
    adapterWatcher.observe(document.body, { childList: true, subtree: true });
  }
  const history = window.history as History & { __glassttyPatched?: boolean };
  if (!history.__glassttyPatched) {
    const wrap = (name: 'pushState' | 'replaceState') => {
      const original = history[name];
      history[name] = function patchedHistoryMethod(...args: Parameters<History[typeof name]>): ReturnType<History[typeof name]> {
        const result = original.apply(history, args);
        sync();
        return result;
      } as History[typeof name];
    };
    wrap('pushState');
    wrap('replaceState');
    history.__glassttyPatched = true;
  }
  window.addEventListener('popstate', sync, { passive: true });
  window.addEventListener('hashchange', sync, { passive: true });
  window.setInterval(() => resolveAdapter('periodic'), 2000);
}

function installRuntimeLane(): void {
  chrome.runtime.onMessage.addListener((message: Envelope, _sender, sendResponse) => {
    const activeAdapter = resolveAdapter(`message:${message.type}`);
    if (!activeAdapter) {
      sendResponse(replyTo(message, 'error.report', { error: 'no adapter matched current page', url: window.location.href }));
      return true;
    }

    const attemptId = attemptIdFromMessage(message);

    switch (message.type) {
      case 'prompt.read':
        sendResponse(replyTo(message, 'prompt.read', withAttemptMetadata({ text: activeAdapter.readPrompt(document), adapter: activeAdapter.name, url: window.location.href }, attemptId)));
        return true;
      case 'prompt.write':
        sendResponse(replyTo(message, 'prompt.write', withAttemptMetadata({ ok: activeAdapter.writePrompt(document, String((message.payload as { text?: string })?.text ?? '')), adapter: activeAdapter.name, readback: activeAdapter.readPrompt(document), url: window.location.href }, attemptId)));
        return true;
      case 'prompt.submit': {
        const promptBeforeSubmit = activeAdapter.readPrompt(document);
        const ok = activeAdapter.submitPrompt?.(document) ?? false;
        const promptAfterSubmit = activeAdapter.readPrompt(document);
        sendResponse(replyTo(message, 'prompt.submit', withAttemptMetadata({
          ok,
          adapter: activeAdapter.name,
          url: window.location.href,
          prompt_before_submit: promptBeforeSubmit,
          composer_readback_before_submit: promptBeforeSubmit,
          submitted_prompt: promptBeforeSubmit,
          prompt_after_submit: promptAfterSubmit,
        }, attemptId)));
        return true;
      }
      case 'transcript.latest': {
        const latestWitness = activeAdapter.readLatestOutputWitness?.(document);
        const latestUserTurnWitness = activeAdapter.readLatestUserTurnWitness?.(document);
        sendResponse(replyTo(message, 'transcript.latest', withAttemptMetadata({
          text: latestWitness ? latestWitness.text : activeAdapter.readLatestOutput(document),
          latest_output_witness: latestWitness,
          latest_user_turn_witness: latestUserTurnWitness,
          adapter: activeAdapter.name,
          url: window.location.href,
        }, attemptId)));
        return true;
      }
      case 'selection.read':
        sendResponse(replyTo(message, 'selection.read', withAttemptMetadata({ text: activeAdapter.readSelection(window), adapter: activeAdapter.name, url: window.location.href }, attemptId)));
        return true;
      case 'debug.dom_candidates':
        sendResponse(replyTo(message, 'debug.dom_candidates', withAttemptMetadata({ ...activeAdapter.debugCandidates(document), adapter: activeAdapter.name }, attemptId)));
        return true;
      case 'fixture.capture':
        sendResponse(replyTo(message, 'fixture.capture', withAttemptMetadata(activeAdapter.captureFixture ? activeAdapter.captureFixture(document, window) : {
          adapter: activeAdapter.name,
          url: window.location.href,
          title: document.title,
          prompt: activeAdapter.readPrompt(document),
          latest_output: activeAdapter.readLatestOutput(document),
          selection: activeAdapter.readSelection(window),
          candidates: activeAdapter.debugCandidates(document),
        }, attemptId)));
        return true;
      case 'state.snapshot': {
        const latestWitness = activeAdapter.readLatestOutputWitness?.(document);
        const latestUserTurnWitness = activeAdapter.readLatestUserTurnWitness?.(document);
        const generation = activeAdapter.generationSnapshot?.(document, window) ?? null;
        sendResponse(replyTo(message, 'state.snapshot', withAttemptMetadata({
          adapter: activeAdapter.name,
          prompt: activeAdapter.readPrompt(document),
          latest_output: latestWitness ? latestWitness.text : activeAdapter.readLatestOutput(document),
          latest_output_witness: latestWitness,
          latest_user_turn_witness: latestUserTurnWitness,
          generation,
          selection: activeAdapter.readSelection(window),
          url: window.location.href,
        }, attemptId)));
        return true;
      }
      case 'generation.state': {
        const generation = activeAdapter.generationSnapshot?.(document, window) ?? null;
        const latestWitness = activeAdapter.readLatestOutputWitness?.(document);
        sendResponse(replyTo(message, 'generation.state', withAttemptMetadata({
          adapter: activeAdapter.name,
          generation,
          latest_output: latestWitness ? latestWitness.text : activeAdapter.readLatestOutput(document),
          url: window.location.href,
        }, attemptId)));
        return true;
      }
      case 'attach.begin': {
        const payload = message.payload as { transfer_id: string; name: string; mime?: string; size: number; chunks: number };
        pruneAttachTransfers();
        const valid = typeof payload.transfer_id === 'string'
          && payload.transfer_id.length > 0
          && payload.transfer_id.length <= 128
          && typeof payload.name === 'string'
          && payload.name.length > 0
          && payload.name.length <= 1024
          && Number.isSafeInteger(payload.size)
          && payload.size > 0
          && payload.size <= MAX_ATTACHMENT_BYTES
          && Number.isSafeInteger(payload.chunks)
          && payload.chunks > 0
          && payload.chunks <= MAX_ATTACH_CHUNKS
          && payload.chunks === Math.ceil(payload.size / ATTACH_CHUNK_BYTES);
        if (!valid) {
          sendResponse(replyTo(message, 'attach.begin', withAttemptMetadata({
            ok: false,
            error: `invalid attachment envelope (max ${MAX_ATTACHMENT_BYTES} bytes / ${MAX_ATTACH_CHUNKS} chunks)`,
          }, attemptId)));
          return true;
        }
        if (attachTransfers.has(payload.transfer_id)) {
          sendResponse(replyTo(message, 'attach.begin', withAttemptMetadata({
            ok: false, error: 'duplicate transfer_id',
          }, attemptId)));
          return true;
        }
        if (attachTransfers.size >= MAX_ACTIVE_ATTACH_TRANSFERS) {
          sendResponse(replyTo(message, 'attach.begin', withAttemptMetadata({
            ok: false, error: `too many active attachment transfers (max ${MAX_ACTIVE_ATTACH_TRANSFERS})`,
          }, attemptId)));
          return true;
        }
        const readiness = activeAdapter.attachmentReadiness?.(document)
          ?? { ok: false, error: 'adapter cannot preflight file attachments' };
        if (!readiness.ok) {
          sendResponse(replyTo(message, 'attach.begin', withAttemptMetadata({
            ...readiness, adapter: activeAdapter.name, url: window.location.href,
          }, attemptId)));
          return true;
        }
        const composerKeysBefore = activeAdapter.composerKeys?.(document) ?? [];
        const witnessBefore = activeAdapter.attachmentWitness?.(
          document,
          composerKeysBefore,
          payload.name,
          false,
        ) ?? null;
        const rawInputFilesBefore = witnessBefore?.input_files;
        if (typeof rawInputFilesBefore !== 'number'
          || !Number.isSafeInteger(rawInputFilesBefore)
          || rawInputFilesBefore < 0) {
          sendResponse(replyTo(message, 'attach.begin', withAttemptMetadata({
            ok: false,
            error: 'adapter did not return a valid pre-transfer attachment count',
            adapter: activeAdapter.name,
            url: window.location.href,
          }, attemptId)));
          return true;
        }
        const inputFilesBefore = rawInputFilesBefore;
        const absoluteWitnessBefore = activeAdapter.attachmentWitness?.(document, [], '', false) ?? null;
        const knownChipKeysBefore = Array.isArray(absoluteWitnessBefore?.known_chip_keys)
          ? absoluteWitnessBefore.known_chip_keys
          : [];
        const expectedNameVisibleBefore = Boolean(witnessBefore?.expected_name_visible);
        attachTransfers.set(payload.transfer_id, {
          name: payload.name,
          mime: payload.mime || 'application/octet-stream',
          size: payload.size,
          chunks: new Array(payload.chunks),
          received: 0,
          // Snapshot the composer BEFORE the file lands, so the chip that appears
          // afterwards is detectable as a diff rather than a guessed selector.
          composer_keys_before: composerKeysBefore,
          input_files_before: inputFilesBefore,
          known_chip_keys_before: knownChipKeysBefore,
          expected_name_visible_before: expectedNameVisibleBefore,
          created_at: Date.now(),
        });
        sendResponse(replyTo(message, 'attach.begin', withAttemptMetadata({
          ...readiness, ok: true, adapter: activeAdapter.name, transfer_id: payload.transfer_id,
          composer_keys_before: composerKeysBefore,
          input_files_before: inputFilesBefore,
          known_chip_keys_before: knownChipKeysBefore,
          expected_name_visible_before: expectedNameVisibleBefore,
          url: window.location.href,
        }, attemptId)));
        return true;
      }
      case 'attach.chunk': {
        const payload = message.payload as { transfer_id: string; index: number; data: string };
        pruneAttachTransfers();
        const transfer = attachTransfers.get(payload.transfer_id);
        if (!transfer) {
          sendResponse(replyTo(message, 'attach.chunk', withAttemptMetadata({ ok: false, error: 'unknown transfer_id (did the page reload mid-transfer?)' }, attemptId)));
          return true;
        }
        if (!Number.isSafeInteger(payload.index) || payload.index < 0 || payload.index >= transfer.chunks.length) {
          sendResponse(replyTo(message, 'attach.chunk', withAttemptMetadata({
            ok: false, error: `chunk index ${String(payload.index)} is outside 0..${transfer.chunks.length - 1}`,
          }, attemptId)));
          return true;
        }
        if (typeof payload.data !== 'string' || payload.data.length === 0 || payload.data.length > MAX_ATTACH_CHUNK_BASE64) {
          sendResponse(replyTo(message, 'attach.chunk', withAttemptMetadata({
            ok: false, error: `invalid base64 chunk payload (max ${MAX_ATTACH_CHUNK_BASE64} characters)`,
          }, attemptId)));
          return true;
        }
        if (transfer.chunks[payload.index] === undefined) transfer.received += 1;
        transfer.chunks[payload.index] = payload.data;
        sendResponse(replyTo(message, 'attach.chunk', withAttemptMetadata({
          ok: true, transfer_id: payload.transfer_id, index: payload.index,
          received: transfer.received, expected: transfer.chunks.length,
        }, attemptId)));
        return true;
      }
      case 'attach.commit': {
        const payload = message.payload as { transfer_id: string };
        pruneAttachTransfers();
        const transfer = attachTransfers.get(payload.transfer_id);
        if (!transfer) {
          sendResponse(replyTo(message, 'attach.commit', withAttemptMetadata({ ok: false, error: 'unknown transfer_id' }, attemptId)));
          return true;
        }
        if (transfer.received !== transfer.chunks.length || transfer.chunks.some((chunk) => chunk === undefined)) {
          sendResponse(replyTo(message, 'attach.commit', withAttemptMetadata({
            ok: false, error: `incomplete transfer: ${transfer.received}/${transfer.chunks.length} chunks`,
          }, attemptId)));
          return true;
        }
        attachTransfers.delete(payload.transfer_id);
        const witnessBeforeCommit = activeAdapter.attachmentWitness?.(
          document,
          transfer.composer_keys_before,
          transfer.name,
          transfer.expected_name_visible_before,
        ) ?? null;
        const absoluteWitnessBeforeCommit = activeAdapter.attachmentWitness?.(document, [], '', false) ?? null;
        const knownChipKeysBeforeCommit = Array.isArray(absoluteWitnessBeforeCommit?.known_chip_keys)
          ? absoluteWitnessBeforeCommit.known_chip_keys
          : [];
        if (witnessBeforeCommit?.input_files !== transfer.input_files_before
          || JSON.stringify(knownChipKeysBeforeCommit) !== JSON.stringify(transfer.known_chip_keys_before)) {
          sendResponse(replyTo(message, 'attach.commit', withAttemptMetadata({
            ok: false,
            error: 'composer attachments changed during transfer; refusing to overwrite concurrent operator state',
            composer_keys_before: transfer.composer_keys_before,
            input_files_before: transfer.input_files_before,
            known_chip_keys_before: transfer.known_chip_keys_before,
            expected_name_visible_before: transfer.expected_name_visible_before,
          }, attemptId)));
          return true;
        }
        let bytes: Uint8Array;
        try {
          // Decode straight into the final buffer. Mapping every base64 chunk to
          // a second byte array briefly doubled large uploads in browser memory.
          bytes = decodeAttachmentChunks(transfer.chunks, transfer.size);
        } catch (error) {
          sendResponse(replyTo(message, 'attach.commit', withAttemptMetadata({
            ok: false, error: `attachment decode failed: ${error instanceof Error ? error.message : String(error)}`,
          }, attemptId)));
          return true;
        }

        const result = activeAdapter.attachFiles?.(document, [{ name: transfer.name, mime: transfer.mime, bytes }])
          ?? { ok: false, error: 'adapter cannot attach files', files_before: 0, files_after: 0 };
        const witness = activeAdapter.attachmentWitness?.(
          document,
          transfer.composer_keys_before,
          transfer.name,
          transfer.expected_name_visible_before,
        ) ?? null;
        sendResponse(replyTo(message, 'attach.commit', withAttemptMetadata({
          ...result, adapter: activeAdapter.name, name: transfer.name, bytes: bytes.byteLength,
          composer_keys_before: transfer.composer_keys_before,
          input_files_before: transfer.input_files_before,
          known_chip_keys_before: transfer.known_chip_keys_before,
          expected_name_visible_before: transfer.expected_name_visible_before,
          witness,
          url: window.location.href,
        }, attemptId)));
        return true;
      }
      case 'attach.status': {
        const payload = message.payload as {
          composer_keys_before?: string[]; expected_name?: string; expected_name_visible_before?: boolean;
        };
        const witness = activeAdapter.attachmentWitness?.(
          document,
          payload?.composer_keys_before ?? [],
          payload?.expected_name ?? '',
          payload?.expected_name_visible_before ?? false,
        ) ?? null;
        sendResponse(replyTo(message, 'attach.status', withAttemptMetadata({
          ok: true, adapter: activeAdapter.name, witness, url: window.location.href,
        }, attemptId)));
        return true;
      }
      case 'attach.abort': {
        const payload = message.payload as { transfer_id?: string };
        const aborted = typeof payload?.transfer_id === 'string' && attachTransfers.delete(payload.transfer_id);
        sendResponse(replyTo(message, 'attach.abort', withAttemptMetadata({
          ok: true, aborted, adapter: activeAdapter.name,
        }, attemptId)));
        return true;
      }
      case 'attach.clear': {
        const payload = message.payload as {
          composer_keys_before?: string[]; expected_name?: string; expected_name_visible_before?: boolean;
        };
        const result = activeAdapter.clearAttachments?.(document)
          ?? { ok: false, error: 'adapter cannot clear attachments', inputs_seen: 0, files_before: 0, files_after: 0 };
        const witness = activeAdapter.attachmentWitness?.(
          document,
          payload?.composer_keys_before ?? [],
          payload?.expected_name ?? '',
          payload?.expected_name_visible_before ?? false,
        ) ?? null;
        sendResponse(replyTo(message, 'attach.clear', withAttemptMetadata({
          ...result, adapter: activeAdapter.name, witness, url: window.location.href,
        }, attemptId)));
        return true;
      }
      case 'prompt.stop': {
        const ok = activeAdapter.stopGeneration?.(document, window) ?? false;
        sendResponse(replyTo(message, 'prompt.stop', withAttemptMetadata({ ok, adapter: activeAdapter.name, url: window.location.href }, attemptId)));
        return true;
      }
      case 'chat.new': {
        const ok = activeAdapter.newChat?.(document) ?? false;
        sendResponse(replyTo(message, 'chat.new', withAttemptMetadata({ ok, adapter: activeAdapter.name, url: window.location.href }, attemptId)));
        return true;
      }
      case 'surface.overrides.get': {
        sendResponse(replyTo(message, 'surface.overrides.get', withAttemptMetadata({
          ok: true, adapter: activeAdapter.name, overrides: getSurfaceOverrides(), url: window.location.href,
        }, attemptId)));
        return true;
      }
      case 'surface.overrides.set': {
        const requested = (message.payload as { overrides?: SurfaceOverrides })?.overrides ?? {};
        const next = (requested && typeof requested === 'object' ? requested : {}) as SurfaceOverrides;
        setSurfaceOverrides(next);
        chrome.storage.local.set({ [SURFACE_OVERRIDES_KEY]: next }).catch(() => undefined);
        sendResponse(replyTo(message, 'surface.overrides.set', withAttemptMetadata({
          ok: true, adapter: activeAdapter.name, overrides: next, url: window.location.href,
        }, attemptId)));
        return true;
      }
      case 'surface.probe': {
        const probe = activeAdapter.surfaceProbe?.(document, window) ?? null;
        sendResponse(replyTo(message, 'surface.probe', withAttemptMetadata({
          ok: Boolean(probe),
          adapter: activeAdapter.name,
          probe,
          url: window.location.href,
        }, attemptId)));
        return true;
      }
      case 'prompt.continue': {
        const ok = activeAdapter.continueGeneration?.(document, window) ?? false;
        const generation = activeAdapter.generationSnapshot?.(document, window) ?? null;
        sendResponse(replyTo(message, 'prompt.continue', withAttemptMetadata({
          ok,
          adapter: activeAdapter.name,
          generation,
          url: window.location.href,
        }, attemptId)));
        return true;
      }
      default:
        sendResponse(replyTo(message, 'error.report', { error: `unsupported content-script request: ${message.type}`, adapter: activeAdapter.name }));
        return true;
    }
  });
}

function bootstrapContentRuntime(): void {
  if (globalScope.__glassttyContentBootstrap) {
    resolveAdapter('bootstrap-reused');
    log('bootstrap reused', globalScope.__glassttyContentBootstrap);
    return;
  }

  globalScope.__glassttyContentBootstrap = {
    version: CONTENT_BOOTSTRAP_VERSION,
    adapterName: adapter?.name,
    bootedAt: new Date().toISOString(),
  };

  installRuntimeLane();
  setInterval(() => pruneAttachTransfers(), 60_000);
  loadSurfaceOverrides();
  startAdapterWatcher();
  resolveAdapter('bootstrap');
  if (adapter) startTranscriptObserver();
}

bootstrapContentRuntime();
