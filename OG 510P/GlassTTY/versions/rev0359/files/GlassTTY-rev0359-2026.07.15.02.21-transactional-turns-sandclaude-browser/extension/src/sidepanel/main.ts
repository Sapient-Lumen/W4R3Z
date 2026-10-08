import { makeEnvelope, type Envelope } from '../shared/protocol';
import { contentReceiverKey, contentReceiverLabel, type ContentReceiverState } from '../shared/receivers';

const app = document.getElementById('app');
if (!app) throw new Error('sidepanel root missing');
const root = app as HTMLDivElement;

const CHATGPT_FIRST_PROOF_PROMPT = 'Reply with exactly this text and nothing else: GLASSTTY-CHECKPOINT';
const CHATGPT_FIRST_PROOF_EXPECTED_REPLY = 'GLASSTTY-CHECKPOINT';
let proofLog: Envelope[] = [];

const PROOF_RECOVERY_VAULT_KEY = 'glasstty.chatgpt.firstProof.recoveryVault.v1';

interface SupportedTabState {
  tabId: number;
  windowId?: number;
  url?: string;
  adapter?: string;
  title?: string;
  documentId?: string;
  frameId?: number;
  documentLifecycle?: string;
  discarded?: boolean;
  frozen?: boolean;
  receiverReady?: boolean;
  receivers?: ContentReceiverState[];
  receiverCount?: number;
  readyReceiverCount?: number;
  receiverFrameIds?: number[];
  receiverDocumentIds?: string[];
  receiverSelectionPolicy?: string;
  receiverInventoryStatus?: string;
  receiverTopFrameReady?: boolean;
  receiverOverrideKey?: string | null;
  receiverOverrideStatus?: string;
  selectedReceiverKey?: string;
  selectedReceiverLabel?: string;
  lastSeenAt: string;
}

interface BridgeTraceEntry {
  at: string;
  kind: string;
  level: 'info' | 'warn' | 'error';
  data?: unknown;
}

interface NativeHostIdentity {
  pid?: number;
  boot_id?: string;
  started_at?: string;
  message_count?: number;
  first_message_at?: string;
  first_message_type?: string;
  last_message_at?: string;
  last_message_type?: string;
}

interface NativeBrokerSummary {
  role?: string;
  lock_path?: string;
  metadata_path?: string;
  socket_path?: string;
  socket_exists?: boolean;
  connected_clients?: number | null;
  owner_metadata?: {
    native_host?: string;
    socket_path?: string;
    lock_path?: string;
    metadata_path?: string;
    host_identity?: NativeHostIdentity;
  };
}

interface BridgeStatusPayload {
  activeTab?: { id?: number; url?: string; windowId?: number; supported: boolean; discarded?: boolean; frozen?: boolean };
  nativeConnection?: {
    connected: boolean;
    laneDiagnosis?: {
      status: string;
      summary: string;
      recommendedAction: string;
    };
    lastConnectedAt?: string;
    lastDisconnectedAt?: string;
    lastDisconnectReason?: string;
    reconnectAttempt?: number;
    reconnectScheduledFor?: string | null;
    reconnectDelayMinutes?: number | null;
    lastHealthPingAt?: string;
    lastHealthPongAt?: string;
    lastHealthRoundTripMs?: number;
    lastHealthRequestId?: string;
    lastHealthTrigger?: string;
    lastHealthOk?: boolean;
    lastHealthError?: string;
    lastOneShotProbeAt?: string;
    lastOneShotProbeOk?: boolean;
    lastOneShotProbeError?: string;
    lastOneShotProbeRoundTripMs?: number;
    lastOneShotProbeHost?: string;
    lastOneShotProbeSocketPath?: string;
    lastOneShotProbeHostIdentity?: NativeHostIdentity;
    lastOneShotProbeBroker?: NativeBrokerSummary;
    persistentHostIdentity?: NativeHostIdentity;
    persistentBroker?: NativeBrokerSummary;
    nativeHost?: string;
    socketPath?: string;
  };
  targetTab?: SupportedTabState | null;
  selectedTargetTabId?: number | null;
  supportedTabs?: SupportedTabState[];
  adapters?: Array<{ name: string; origin_patterns: string[]; capabilities: Record<string, boolean> }>;
  lastNativeMessage?: unknown;
  lastContentMessage?: unknown;
  lastOversizedHostMessage?: unknown;
  lastNativeStatusSnapshot?: {
    capturedAt: string;
    trigger: string;
    native_host?: string;
    socket_path?: string;
    host_identity?: NativeHostIdentity;
    broker?: NativeBrokerSummary;
    matches_persistent_host?: boolean;
  } | unknown;
  lastNativeStatusError?: string;
  lastError?: unknown;
  persistentDiagnostics?: {
    updatedAt?: string;
    workerBoots?: Array<Record<string, unknown>>;
    nativeEvents?: Array<Record<string, unknown>>;
    runtimeHint?: { status: string; summary: string; recommendedAction: string };
  };
}

interface BridgeTracePayload {
  events?: BridgeTraceEntry[];
}

function card(title: string, body: string): string {
  return `<section class="card"><h2>${title}</h2><pre>${body}</pre></section>`;
}

function receiverHtml(tab: SupportedTabState): string {
  const receivers = tab.receivers ?? [];
  if (!receivers.length) return '';
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

function adaptersHtml(adapters: BridgeStatusPayload['adapters'] = []): string {
  if (!adapters.length) return '';
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

function supportedTabsHtml(tabs: SupportedTabState[] = [], targetTabId?: number | null): string {
  if (tabs.length === 0) return '<section class="card"><h2>Supported tabs</h2><p>No supported tabs observed yet.</p></section>';
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

function traceHtml(events: BridgeTraceEntry[] = []): string {
  if (!events.length) return '<section class="card"><h2>Recent bridge trace</h2><p>No extension-side trace entries yet.</p></section>';
  return card('Recent bridge trace', JSON.stringify(events, null, 2));
}

function nativeConnectionHtml(nativeConnection?: BridgeStatusPayload['nativeConnection']): string {
  if (!nativeConnection) return '';
  return card('Native bridge', JSON.stringify(nativeConnection, null, 2));
}

function overflowHtml(lastOversizedHostMessage?: unknown): string {
  if (!lastOversizedHostMessage) return '';
  return card('Host overflow guard', JSON.stringify(lastOversizedHostMessage, null, 2));
}

function persistentDiagnosticsHtml(persistentDiagnostics?: BridgeStatusPayload['persistentDiagnostics']): string {
  if (!persistentDiagnostics) return '';
  return card('Persistent local diagnostics', JSON.stringify(persistentDiagnostics, null, 2));
}

function nativeStatusSnapshotHtml(snapshot?: unknown, error?: string): string {
  if (!snapshot && !error) return '';
  return card('Native host local status snapshot', JSON.stringify({ snapshot, error }, null, 2));
}

function selectedTabId(): number | undefined {
  const selected = document.querySelector<HTMLInputElement>('input[name="target-tab"]:checked');
  return selected ? Number(selected.value) : undefined;
}

async function bridgeRequest<T = unknown>(type: Envelope['type'], payload: Record<string, unknown> = {}): Promise<Envelope<T>> {
  return chrome.runtime.sendMessage(makeEnvelope(type, payload)) as Promise<Envelope<T>>;
}

async function refreshStatus(): Promise<void> {
  const [response, traceResponse, storage, localStorage] = await Promise.all([
    bridgeRequest<BridgeStatusPayload>('bridge.status'),
    bridgeRequest<BridgeTracePayload>('bridge.trace', { limit: 30 }),
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

  document.querySelectorAll<HTMLInputElement>('input[name="target-tab"]').forEach((input) => {
    input.addEventListener('change', () => {
      if (input.checked) void bridgeRequest('bridge.set_target_tab', { tab_id: Number(input.value) }).then(refreshStatus).catch(console.error);
    });
  });
  document.querySelectorAll<HTMLInputElement>('input[data-receiver-tab-id]').forEach((input) => {
    input.addEventListener('change', () => {
      if (!input.checked) return;
      const tabId = Number(input.dataset.receiverTabId);
      void bridgeRequest('bridge.set_receiver_override', { tab_id: tabId, receiver_key: input.value }).then(refreshStatus).catch(console.error);
    });
  });
  document.querySelectorAll<HTMLButtonElement>('button[data-clear-receiver-override]').forEach((button) => {
    button.addEventListener('click', () => {
      const tabId = Number(button.dataset.clearReceiverOverride);
      void bridgeRequest('bridge.clear_receiver_override', { tab_id: tabId }).then(refreshStatus).catch(console.error);
    });
  });
  document.getElementById('clear-target')?.addEventListener('click', () => {
    void bridgeRequest('bridge.clear_target_tab', {}).then(refreshStatus).catch(console.error);
  });
}

async function request(type: Envelope['type'], payload: Record<string, unknown> = {}): Promise<Envelope> {
  const tabId = selectedTabId();
  const response = await chrome.runtime.sendMessage(makeEnvelope(type, { ...payload, ...(tabId ? { tab_id: tabId } : {}) })) as Envelope;
  const output = document.getElementById('last-response');
  if (output) output.textContent = JSON.stringify(response, null, 2);
  await refreshStatus();
  return response;
}

function compactTimestampForAttemptId(date = new Date()): string {
  return date.toISOString().replace(/[-:]/g, '').replace(/\.\d{3}Z$/, 'Z');
}

function proofAttemptInput(): HTMLInputElement | null {
  return document.getElementById('proof-attempt-id') as HTMLInputElement | null;
}

function ensureProofAttemptId(): string {
  const input = proofAttemptInput();
  const existing = input?.value.trim();
  if (existing) return existing;
  const generated = `chatgpt-first-proof-${compactTimestampForAttemptId()}`;
  if (input) input.value = generated;
  return generated;
}

function proofOutput(): HTMLElement | null {
  return document.getElementById('proof-capture-output');
}

function proofTransferStatusEl(): HTMLElement | null {
  return document.getElementById('proof-transfer-status');
}

function setProofTransferStatus(message: string, detail?: unknown): void {
  const el = proofTransferStatusEl();
  if (!el) return;
  el.textContent = detail === undefined ? message : `${message}\n${JSON.stringify(detail, null, 2)}`;
}

function proofVaultStatusEl(): HTMLElement | null {
  return document.getElementById('proof-recovery-vault-status');
}

function setProofVaultStatus(message: string, detail?: unknown): void {
  const el = proofVaultStatusEl();
  if (!el) return;
  el.textContent = detail === undefined ? message : `${message}\n${JSON.stringify(detail, null, 2)}`;
}

function safeDownloadComponent(value: string): string {
  const compacted = value.trim().replace(/[^A-Za-z0-9_.-]+/g, '-').replace(/-+/g, '-').replace(/^-|-$/g, '');
  return compacted.slice(0, 96) || 'chatgpt-first-proof';
}

function proofCaptureJsonFilename(attemptId = ensureProofAttemptId()): string {
  return `GlassTTY-${safeDownloadComponent(attemptId)}-chatgpt-first-proof-capture.json`;
}

function proofScreenshotFilename(attemptId = ensureProofAttemptId()): string {
  return `GlassTTY-${safeDownloadComponent(attemptId)}-chatgpt-visible-proof-screenshot.png`;
}

function triggerBlobDownload(filename: string, mimeType: string, body: string): void {
  const blob = new Blob([body], { type: mimeType });
  const url = URL.createObjectURL(blob);
  try {
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    link.rel = 'noopener';
    document.body.appendChild(link);
    link.click();
    link.remove();
  } finally {
    window.setTimeout(() => URL.revokeObjectURL(url), 30_000);
  }
}

function triggerDataUrlDownload(filename: string, dataUrl: string): void {
  const link = document.createElement('a');
  link.href = dataUrl;
  link.download = filename;
  link.rel = 'noopener';
  document.body.appendChild(link);
  link.click();
  link.remove();
}

function redactLargeProofValuesForDisplay(value: unknown): unknown {
  if (typeof value === 'string') {
    if (value.startsWith('data:image/png;base64,')) {
      return `[redacted image data URL for side-panel display; length=${value.length}; hash=${fnv1a32(value)}; use Copy/Download proof JSON for full payload]`;
    }
    if (value.length > 50_000) {
      return `[redacted large string for side-panel display; length=${value.length}; hash=${fnv1a32(value)}]`;
    }
    return value;
  }
  if (Array.isArray(value)) return value.map(redactLargeProofValuesForDisplay);
  if (value && typeof value === 'object') {
    return Object.fromEntries(Object.entries(value).map(([key, item]) => [key, redactLargeProofValuesForDisplay(item)]));
  }
  return value;
}

function fnv1a32(value: string): string {
  let hash = 0x811c9dc5;
  for (let index = 0; index < value.length; index += 1) {
    hash ^= value.charCodeAt(index);
    hash = Math.imul(hash, 0x01000193);
  }
  return `fnv1a32:${(hash >>> 0).toString(16).padStart(8, '0')}`;
}

function latestProofScreenshotPayload(): Record<string, unknown> | undefined {
  for (let index = proofLog.length - 1; index >= 0; index -= 1) {
    const response = proofLog[index];
    if (response.type === 'proof.surface_screenshot') return proofPayload(response);
  }
  return undefined;
}

function screenshotDataUrlDimensions(dataUrl: string): { width: number | null; height: number | null } {
  // PNG dimensions live in the IHDR chunk. Avoid decoding full pixel data in the side panel.
  const prefix = 'data:image/png;base64,';
  if (!dataUrl.startsWith(prefix)) return { width: null, height: null };
  try {
    const binary = atob(dataUrl.slice(prefix.length, prefix.length + 64));
    if (binary.length < 24) return { width: null, height: null };
    const width = ((binary.charCodeAt(16) & 0xff) << 24)
      | ((binary.charCodeAt(17) & 0xff) << 16)
      | ((binary.charCodeAt(18) & 0xff) << 8)
      | (binary.charCodeAt(19) & 0xff);
    const height = ((binary.charCodeAt(20) & 0xff) << 24)
      | ((binary.charCodeAt(21) & 0xff) << 16)
      | ((binary.charCodeAt(22) & 0xff) << 8)
      | (binary.charCodeAt(23) & 0xff);
    return { width, height };
  } catch {
    return { width: null, height: null };
  }
}

function proofPayload(response: Envelope): Record<string, unknown> {
  return (typeof response.payload === 'object' && response.payload !== null && !Array.isArray(response.payload))
    ? response.payload as Record<string, unknown>
    : {};
}


function chatgptConversationRoutePath(value: unknown): string | undefined {
  if (typeof value !== 'string') return undefined;
  try {
    const parsed = new URL(value);
    if (parsed.hostname !== 'chatgpt.com' && !parsed.hostname.endsWith('.chatgpt.com')) return undefined;
    const parts = parsed.pathname.split('/').filter(Boolean);
    if (parts.length >= 2 && parts[0] === 'c' && parts[1]) return `/c/${parts[1]}`;
  } catch {
    return undefined;
  }
  return undefined;
}

function compactProofText(value: unknown): string | undefined {
  return typeof value === 'string' ? value.replace(/\s+/g, ' ').trim() : undefined;
}

function proofTextExactlyMatchesProbe(value: unknown): boolean | undefined {
  const text = compactProofText(value);
  if (text === undefined) return undefined;
  return text === CHATGPT_FIRST_PROOF_PROMPT;
}


type ProofLiveGateVerdictName = 'proof-live-gate-ok' | 'proof-live-gate-blocked';

interface ProofLiveGateVerdict {
  ok: boolean;
  verdict: ProofLiveGateVerdictName;
  checked_at: string;
  blockers: string[];
  warnings: string[];
  recommendations: string[];
  expected: Record<string, unknown>;
  observed: Record<string, unknown>;
}


interface ProofAttemptReadinessReport {
  schema_version: 1;
  tool: 'glasstty-chatgpt-sidepanel-attempt-readiness';
  checked_at: string;
  attempt_id: string;
  ok: boolean;
  verdict: string;
  next_stage: string;
  next_action: string;
  blockers: string[];
  warnings: string[];
  checks: Record<string, boolean>;
  observed: Record<string, unknown>;
  recovery_vault?: Record<string, unknown>;
  cli_after_download: string;
}

interface ProofRecoveryVaultRecord {
  schema_version: 1;
  storage_key: string;
  storage_backend: 'chrome.storage.local';
  saved_at: string;
  save_reason: string;
  attempt_id: string;
  envelope_count: number;
  document_bytes: number;
  document_hash: string;
  has_screenshot: boolean;
  screenshot_data_url_hash?: string;
  screenshot_dimensions?: unknown;
  saved_full_document: boolean;
  document?: Record<string, unknown>;
  redacted_preview: unknown;
  warnings: string[];
}

const PROOF_LIVE_GATE_EXPECTED = {
  surface_key: 'chatgpt',
  route_posture: 'plain-chat',
  prompt_selector: '#prompt-textarea',
  send_selector: '#composer-submit-button',
  send_testid: 'send-button',
  send_aria_label: 'Send prompt',
  blocked_non_send_selector: '#composer-plus-btn',
  blocked_non_send_aria_label: 'Add files and more',
};

function asRecord(value: unknown): Record<string, unknown> | undefined {
  return typeof value === 'object' && value !== null && !Array.isArray(value)
    ? value as Record<string, unknown>
    : undefined;
}

function stringField(record: Record<string, unknown> | undefined, key: string): string | undefined {
  const value = record?.[key];
  return typeof value === 'string' ? value : undefined;
}

function boolField(record: Record<string, unknown> | undefined, key: string): boolean | undefined {
  const value = record?.[key];
  return typeof value === 'boolean' ? value : undefined;
}

function numberField(record: Record<string, unknown> | undefined, key: string): number | undefined {
  const value = record?.[key];
  return typeof value === 'number' && Number.isFinite(value) ? value : undefined;
}

function selectorLooksLike(actual: unknown, expected: string): boolean {
  return typeof actual === 'string' && actual.includes(expected);
}

function proofLiveGateStatusEl(): HTMLElement | null {
  return document.getElementById('proof-live-gate-status');
}

function setProofLiveGateStatus(message: string, verdict?: ProofLiveGateVerdict): void {
  const el = proofLiveGateStatusEl();
  if (!el) return;
  const suffix = verdict ? `\n${JSON.stringify(verdict, null, 2)}` : '';
  el.textContent = `${message}${suffix}`;
}


function proofAttemptReadinessStatusEl(): HTMLElement | null {
  return document.getElementById('proof-attempt-readiness-status');
}

function setProofAttemptReadinessStatus(message: string, report?: ProofAttemptReadinessReport): void {
  const el = proofAttemptReadinessStatusEl();
  if (!el) return;
  const suffix = report ? `\n${JSON.stringify(report, null, 2)}` : '';
  el.textContent = `${message}${suffix}`;
}

function latestProofPayloadByType(type: Envelope['type']): Record<string, unknown> | undefined {
  for (let index = proofLog.length - 1; index >= 0; index -= 1) {
    const item = proofLog[index];
    if (item.type === type) return proofPayload(item);
  }
  return undefined;
}

function latestProofLiveGateOk(): boolean {
  for (let index = proofLog.length - 1; index >= 0; index -= 1) {
    const payload = proofPayload(proofLog[index]);
    if (typeof payload.proof_live_gate_ok === 'boolean') return payload.proof_live_gate_ok;
  }
  return false;
}

function proofSubmitReadbackSeen(): boolean {
  return proofLog.some((response) => {
    if (response.type !== 'prompt.submit') return false;
    const payload = proofPayload(response);
    return [payload.composer_readback_before_submit, payload.prompt_before_submit, payload.submitted_prompt]
      .some((value) => proofTextExactlyMatchesProbe(value) === true);
  });
}

function proofLatestReplySeen(): boolean {
  return proofLog.some((response) => {
    if (response.type !== 'transcript.latest') return false;
    return compactProofText(proofPayload(response).text) === CHATGPT_FIRST_PROOF_EXPECTED_REPLY;
  });
}

function proofLatestUserTurnSeen(): boolean {
  return proofLog.some((response) => {
    if (response.type !== 'transcript.latest') return false;
    const userWitness = asRecord(proofPayload(response).latest_user_turn_witness);
    return compactProofText(userWitness?.text) === CHATGPT_FIRST_PROOF_PROMPT;
  });
}

function activeSupportedTargetFromStatus(payload: BridgeStatusPayload): SupportedTabState | undefined {
  const radioTabId = selectedTabId();
  const selectedTargetId = radioTabId ?? (typeof payload.selectedTargetTabId === 'number' ? payload.selectedTargetTabId : undefined);
  if (selectedTargetId && Array.isArray(payload.supportedTabs)) {
    const found = payload.supportedTabs.find((tab) => tab.tabId === selectedTargetId);
    if (found) return found;
  }
  if (payload.targetTab) return payload.targetTab;
  if (Array.isArray(payload.supportedTabs) && payload.supportedTabs.length === 1) return payload.supportedTabs[0];
  return undefined;
}

function targetLooksLikeChatGpt(tab: SupportedTabState | undefined): boolean {
  return typeof tab?.url === 'string' && tab.url.startsWith('https://chatgpt.com/');
}

function targetReceiverLooksReady(tab: SupportedTabState | undefined): boolean {
  if (!tab) return false;
  if (tab.receiverReady === true) return true;
  if (tab.receiverTopFrameReady === true) return true;
  if (typeof tab.readyReceiverCount === 'number') return tab.readyReceiverCount > 0;
  return false;
}

async function runProofAttemptReadiness(): Promise<ProofAttemptReadinessReport> {
  const status = await bridgeRequest<BridgeStatusPayload>('bridge.status');
  const statusPayload = status.payload ?? {};
  const target = activeSupportedTargetFromStatus(statusPayload);
  const activeTab = statusPayload.activeTab;
  const vault = await loadProofRecoveryVault().catch(() => undefined);
  const screenshotPayload = latestProofScreenshotPayload();
  const attemptId = ensureProofAttemptId();
  const checks: Record<string, boolean> = {
    target_selected: Boolean(target?.tabId),
    target_adapter_chatgpt: target?.adapter === 'chatgpt',
    target_url_chatgpt: targetLooksLikeChatGpt(target),
    target_receiver_ready: targetReceiverLooksReady(target),
    active_tab_matches_target: Boolean(activeTab?.id && target?.tabId && activeTab.id === target.tabId),
    checkpoint_write_readback: proofWriteReadbackSeen(),
    live_gate_ok: latestProofLiveGateOk(),
    visible_screenshot_captured: typeof screenshotPayload?.visible_tab_screenshot_data_url === 'string' && screenshotPayload.visible_tab_screenshot_data_url.startsWith('data:image/png;base64,'),
    submit_readback_exact_probe: proofSubmitReadbackSeen(),
    latest_reply_exact_checkpoint: proofLatestReplySeen(),
    latest_user_turn_exact_prompt: proofLatestUserTurnSeen(),
    recovery_vault_available: Boolean(vault),
  };
  const blockers: string[] = [];
  const warnings: string[] = [];

  if (!checks.target_selected) blockers.push('No supported ChatGPT target tab is selected.');
  if (checks.target_selected && !checks.target_adapter_chatgpt) blockers.push('Selected target tab is not using the ChatGPT adapter.');
  if (checks.target_selected && !checks.target_url_chatgpt) blockers.push('Selected target tab is not on https://chatgpt.com/.');
  if (checks.target_selected && !checks.target_receiver_ready) blockers.push('Selected ChatGPT tab does not have a ready top-frame receiver.');
  if (checks.target_selected && !checks.active_tab_matches_target) warnings.push('Selected target is not the active visible tab; screenshot capture will be blocked until the tab is active.');
  if (statusPayload.nativeConnection && statusPayload.nativeConnection.connected === false) {
    warnings.push('Native host is disconnected. The ChatGPT proof path is browser-side, but bridge diagnostics/native workflows may be unavailable.');
  }
  if (vault && vault.saved_full_document === false) warnings.push('Recovery vault has only a preview; download proof JSON before leaving the side panel.');

  let nextStage = 'select-chatgpt-tab';
  let nextAction = 'Open https://chatgpt.com/, refresh this panel, and select the supported ChatGPT tab.';
  if (!blockers.length) {
    if (!checks.checkpoint_write_readback) {
      nextStage = 'write-checkpoint';
      nextAction = 'Press Write checkpoint + capture.';
    } else if (!checks.live_gate_ok) {
      nextStage = 'check-live-gate';
      nextAction = 'Press Check live gate; do not submit until it passes.';
    } else if (!checks.visible_screenshot_captured) {
      nextStage = 'capture-visible-screenshot';
      nextAction = 'Activate the selected ChatGPT tab, then press Capture visible screenshot.';
    } else if (!checks.submit_readback_exact_probe) {
      nextStage = 'submit-checkpoint';
      nextAction = 'Press Submit checkpoint (gated), then wait for ChatGPT to settle.';
    } else if (!checks.latest_reply_exact_checkpoint || !checks.latest_user_turn_exact_prompt) {
      nextStage = 'read-latest';
      nextAction = 'After the assistant reply settles, press Read latest + capture.';
    } else {
      nextStage = 'download-proof-json';
      nextAction = `Press Download proof JSON, then run glassttyd proof-autopilot --execute-live --input ${proofCaptureJsonFilename(attemptId)} --clean --pretty.`;
    }
  }

  const ok = !blockers.length && nextStage === 'download-proof-json';
  const report: ProofAttemptReadinessReport = {
    schema_version: 1,
    tool: 'glasstty-chatgpt-sidepanel-attempt-readiness',
    checked_at: new Date().toISOString(),
    attempt_id: attemptId,
    ok,
    verdict: ok ? 'proof-attempt-ready-to-download' : 'proof-attempt-not-ready',
    next_stage: nextStage,
    next_action: nextAction,
    blockers,
    warnings,
    checks,
    observed: {
      target_tab_id: target?.tabId,
      target_window_id: target?.windowId,
      target_adapter: target?.adapter,
      target_url: target?.url,
      receiver_count: target?.receiverCount,
      ready_receiver_count: target?.readyReceiverCount,
      selected_receiver_label: target?.selectedReceiverLabel,
      active_tab_id: activeTab?.id,
      active_tab_url: activeTab?.url,
      proof_log_envelope_count: proofLog.length,
      proof_log_types: proofLog.map((item) => item.type),
      latest_gate_ok: checks.live_gate_ok,
      screenshot_hash: typeof screenshotPayload?.screenshot_data_url_hash === 'string' ? screenshotPayload.screenshot_data_url_hash : undefined,
    },
    recovery_vault: vault ? {
      saved_at: vault.saved_at,
      attempt_id: vault.attempt_id,
      envelope_count: vault.envelope_count,
      document_hash: vault.document_hash,
      saved_full_document: vault.saved_full_document,
      has_screenshot: vault.has_screenshot,
      warnings: vault.warnings,
    } : undefined,
    cli_after_download: `glassttyd proof-autopilot --execute-live --input ${proofCaptureJsonFilename(attemptId)} --clean --pretty`,
  };
  const envelope = makeEnvelope('proof.operator_readiness', report, target?.tabId);
  proofLog.push(envelope);
  setProofAttemptReadinessStatus(ok ? 'Proof attempt is ready to download.' : 'Proof attempt is not ready yet.', report);
  renderProofCapture();
  return report;
}

function proofWriteReadbackSeen(): boolean {
  return proofLog.some((response) => {
    if (response.type !== 'prompt.write') return false;
    return proofTextExactlyMatchesProbe(proofPayload(response).readback) === true;
  });
}

function fixturePayloadToLiveGateVerdict(payload: Record<string, unknown>): ProofLiveGateVerdict {
  const metadata = asRecord(payload.metadata) ?? {};
  const actionPolicy = asRecord(metadata.action_policy);
  const blockers: string[] = [];
  const warnings: string[] = [];
  const recommendations: string[] = [];
  const promptText = compactProofText(payload.prompt);
  const observed = {
    adapter: stringField(payload, 'adapter'),
    url: stringField(payload, 'url'),
    route_posture: stringField(metadata, 'route_posture'),
    surface_route: stringField(metadata, 'surface_route'),
    prompt_selector: stringField(metadata, 'prompt_selector'),
    prompt_text_matches_checkpoint: promptText === CHATGPT_FIRST_PROOF_PROMPT,
    submit_selector: stringField(metadata, 'submit_selector'),
    submit_score: numberField(metadata, 'submit_score'),
    submit_signal_intent: boolField(metadata, 'submit_signal_intent'),
    submit_signal_explicit: boolField(metadata, 'submit_signal_explicit'),
    submit_signal_disqualified: boolField(metadata, 'submit_signal_disqualified'),
    observed_live_send_selector: stringField(metadata, 'observed_live_send_selector'),
    observed_live_send_testid: stringField(metadata, 'observed_live_send_testid'),
    observed_live_send_aria_label: stringField(metadata, 'observed_live_send_aria_label'),
    blocked_composer_control_selector: stringField(metadata, 'blocked_composer_control_selector'),
    blocked_composer_control_disqualified: boolField(metadata, 'blocked_composer_control_disqualified'),
    generation_state: stringField(metadata, 'generation_state'),
    action_policy_submit_method: stringField(actionPolicy, 'submit_method'),
    action_policy_route_safe: boolField(actionPolicy, 'route_posture_allows_submit'),
    action_policy_prompt_present: boolField(actionPolicy, 'prompt_present_for_submit'),
    action_policy_button_found: boolField(actionPolicy, 'submit_button_found'),
    action_policy_requires_explicit: boolField(actionPolicy, 'submit_button_requires_explicit_send_intent'),
    action_policy_rejects_non_send: boolField(actionPolicy, 'submit_button_rejects_non_send_composer_controls'),
  };

  if (observed.adapter !== 'chatgpt') blockers.push('target adapter is not chatgpt');
  if (!String(observed.url || '').startsWith('https://chatgpt.com/')) blockers.push('target URL is not on chatgpt.com');
  if (observed.route_posture !== PROOF_LIVE_GATE_EXPECTED.route_posture) blockers.push('route posture is not plain-chat');
  if (!selectorLooksLike(observed.prompt_selector, PROOF_LIVE_GATE_EXPECTED.prompt_selector)) blockers.push('prompt selector is not #prompt-textarea');
  if (!observed.prompt_text_matches_checkpoint) blockers.push('composer readback no longer matches the checkpoint prompt');
  if (!selectorLooksLike(observed.submit_selector, PROOF_LIVE_GATE_EXPECTED.send_selector)) blockers.push('strict send selector is not #composer-submit-button');
  if (observed.submit_signal_intent !== true) blockers.push('send candidate does not declare send intent');
  if (observed.submit_signal_explicit !== true) blockers.push('send candidate is not an explicit send control');
  if (observed.submit_signal_disqualified === true) blockers.push('send candidate is disqualified by non-send control rules');
  if (observed.action_policy_route_safe !== true) blockers.push('adapter action policy does not allow submit on this route');
  if (observed.action_policy_prompt_present !== true) blockers.push('adapter action policy does not see prompt text at submit time');
  if (observed.action_policy_button_found !== true) blockers.push('adapter action policy did not find a submit button');
  if (observed.action_policy_requires_explicit !== true) blockers.push('adapter action policy is not requiring explicit send intent');
  if (observed.action_policy_rejects_non_send !== true) blockers.push('adapter action policy is not rejecting non-send composer controls');
  if (observed.generation_state && observed.generation_state !== 'settled-or-idle') blockers.push(`generation state is ${observed.generation_state}`);
  if (!selectorLooksLike(observed.observed_live_send_selector, PROOF_LIVE_GATE_EXPECTED.send_selector)) warnings.push('fixture did not record the expected live send selector constant');
  if (observed.observed_live_send_testid !== PROOF_LIVE_GATE_EXPECTED.send_testid) warnings.push('fixture did not record the expected send-button test id');
  if (observed.observed_live_send_aria_label !== PROOF_LIVE_GATE_EXPECTED.send_aria_label) warnings.push('fixture did not record the expected send aria-label');
  if (observed.blocked_composer_control_selector && !selectorLooksLike(observed.blocked_composer_control_selector, PROOF_LIVE_GATE_EXPECTED.blocked_non_send_selector)) {
    warnings.push('blocked composer control is not the known plus/add-files control');
  }
  if (observed.blocked_composer_control_selector && observed.blocked_composer_control_disqualified !== true) {
    blockers.push('known non-send composer control is visible but not disqualified');
  }

  if (blockers.length) {
    recommendations.push('Do not submit. Run the Tampermonkey surface oracle/drift verdict and update the ChatGPT adapter or surface contract before retrying.');
  } else {
    recommendations.push('Surface gate passed. Operator may submit the checkpoint prompt and then wait for settled latest-output readback.');
  }
  if (warnings.length) recommendations.push('Review warnings before treating the next live artifact as reviewable evidence.');

  return {
    ok: blockers.length === 0,
    verdict: blockers.length === 0 ? 'proof-live-gate-ok' : 'proof-live-gate-blocked',
    checked_at: new Date().toISOString(),
    blockers,
    warnings,
    recommendations,
    expected: PROOF_LIVE_GATE_EXPECTED,
    observed,
  };
}

async function runProofLiveGate(): Promise<ProofLiveGateVerdict> {
  const fixture = await proofRequest('fixture.capture', {}, {
    proof_live_gate_check: true,
    proof_live_gate_expected: PROOF_LIVE_GATE_EXPECTED,
  });
  const verdict = fixturePayloadToLiveGateVerdict(proofPayload(fixture));
  const payload = proofPayload(fixture);
  fixture.payload = {
    ...payload,
    proof_live_gate_verdict: verdict.verdict,
    proof_live_gate_ok: verdict.ok,
    proof_live_gate_blockers: verdict.blockers,
    proof_live_gate_warnings: verdict.warnings,
    proof_live_gate_recommendations: verdict.recommendations,
    proof_live_gate_expected: verdict.expected,
    proof_live_gate_observed: verdict.observed,
  };
  setProofLiveGateStatus(verdict.ok ? 'Proof live gate passed.' : 'Proof live gate blocked submit.', verdict);
  renderProofCapture();
  return verdict;
}

async function guardedProofSubmit(): Promise<void> {
  if (!proofWriteReadbackSeen()) {
    const verdict: ProofLiveGateVerdict = {
      ok: false,
      verdict: 'proof-live-gate-blocked',
      checked_at: new Date().toISOString(),
      blockers: ['checkpoint write/readback evidence is missing; run Write checkpoint + capture first'],
      warnings: [],
      recommendations: ['Run Write checkpoint + capture, confirm readback, then rerun gated submit.'],
      expected: PROOF_LIVE_GATE_EXPECTED,
      observed: { write_readback_exact_probe_seen: false },
    };
    setProofLiveGateStatus('Proof live gate blocked submit.', verdict);
    return;
  }

  const verdict = await runProofLiveGate();
  if (!verdict.ok) return;

  await proofRequest('prompt.submit', {}, {
    operator_submit_confirmed: true,
    operator_action: 'sidepanel-chatgpt-first-proof-submit-button',
    operator_confirmed_at: new Date().toISOString(),
    submit_method: 'sidepanel-operator-click',
    proof_live_gate_verdict: verdict.verdict,
    proof_live_gate_ok: verdict.ok,
    proof_live_gate_checked_at: verdict.checked_at,
    proof_live_gate_expected: verdict.expected,
    proof_live_gate_observed: verdict.observed,
  });
}

async function captureVisibleProofScreenshot(): Promise<void> {
  const tabId = selectedTabId();
  if (typeof tabId !== 'number' || !Number.isFinite(tabId)) {
    setProofTransferStatus('Screenshot capture blocked.', { blocker: 'select a supported ChatGPT tab first' });
    return;
  }
  const tab = await chrome.tabs.get(tabId);
  const url = typeof tab.url === 'string' ? tab.url : '';
  if (!url.startsWith('https://chatgpt.com/')) {
    setProofTransferStatus('Screenshot capture blocked.', { blocker: 'selected tab is not https://chatgpt.com/', url });
    return;
  }
  if (tab.active === false) {
    setProofTransferStatus('Screenshot capture blocked.', {
      blocker: 'selected ChatGPT tab is not the active visible tab in its window',
      tab_id: tabId,
      window_id: tab.windowId,
      operator_action: 'activate the ChatGPT tab, then press Capture visible screenshot again',
    });
    return;
  }
  const dataUrl = await chrome.tabs.captureVisibleTab(tab.windowId, { format: 'png' });
  const dimensions = screenshotDataUrlDimensions(dataUrl);
  const attemptId = ensureProofAttemptId();
  const payload: Record<string, unknown> = {
    ok: true,
    attempt_id: attemptId,
    adapter: 'chatgpt',
    url,
    tab_id: tabId,
    window_id: tab.windowId,
    capture_kind: 'sidepanel-visible-tab-screenshot',
    captured_at: new Date().toISOString(),
    visible_tab_screenshot_data_url: dataUrl,
    screenshot_mime_type: dataUrl.startsWith('data:image/png;base64,') ? 'image/png' : 'unknown',
    screenshot_data_url_length: dataUrl.length,
    screenshot_data_url_hash: fnv1a32(dataUrl),
    screenshot_dimensions: dimensions,
    screenshot_operator_note: 'Local visible-tab capture. Human redaction review is still required before publication/support use.',
  };
  const envelope: Envelope<Record<string, unknown>> = {
    version: '0.1',
    request_id: crypto.randomUUID(),
    type: 'proof.surface_screenshot',
    tab_id: tabId,
    timestamp: new Date().toISOString(),
    payload,
  };
  proofLog.push(envelope as Envelope);
  setProofTransferStatus('Visible ChatGPT screenshot captured into proof JSON.', {
    tab_id: tabId,
    dimensions,
    data_url_length: dataUrl.length,
    data_url_hash: payload.screenshot_data_url_hash,
  });
  renderProofCapture();
}

async function copyProofCaptureJson(): Promise<void> {
  const documentJson = JSON.stringify(proofCaptureDocument(), null, 2);
  try {
    await navigator.clipboard.writeText(documentJson);
    setProofTransferStatus('Proof capture JSON copied to clipboard.', {
      bytes: documentJson.length,
      recommended_filename: proofCaptureJsonFilename(),
    });
  } catch (error) {
    setProofTransferStatus('Clipboard copy failed; use Download proof JSON or select and copy the assembled JSON manually.', {
      error: error instanceof Error ? error.message : String(error),
      bytes: documentJson.length,
      recommended_filename: proofCaptureJsonFilename(),
    });
  }
}

async function downloadProofCaptureJson(): Promise<void> {
  const readiness = await runProofAttemptReadiness();
  if (!readiness.ok) {
    setProofTransferStatus('Proof capture JSON download blocked by attempt readiness.', {
      verdict: readiness.verdict,
      next_stage: readiness.next_stage,
      next_action: readiness.next_action,
      blockers: readiness.blockers,
      warnings: readiness.warnings,
      note: 'Run the recommended side-panel step, then press Download proof JSON again so the capture includes a fresh proof.operator_readiness envelope.',
    });
    return;
  }
  const documentJson = JSON.stringify(proofCaptureDocument(), null, 2);
  const filename = proofCaptureJsonFilename();
  triggerBlobDownload(filename, 'application/json;charset=utf-8', documentJson);
  setProofTransferStatus('Proof capture JSON download started after attempt readiness passed.', {
    filename,
    bytes: documentJson.length,
    sha_like_hash: fnv1a32(documentJson),
    readiness_verdict: readiness.verdict,
    next_command: `glassttyd proof-attempt-audit --input ${filename} --require-ready-to-download --pretty && glassttyd proof-autopilot --execute-live --input ${filename} --clean --pretty`,
  });
}

function downloadProofScreenshotPng(): void {
  const screenshotPayload = latestProofScreenshotPayload();
  const dataUrl = typeof screenshotPayload?.visible_tab_screenshot_data_url === 'string'
    ? screenshotPayload.visible_tab_screenshot_data_url
    : undefined;
  if (!dataUrl) {
    setProofTransferStatus('Screenshot download blocked.', { blocker: 'capture a visible ChatGPT screenshot first' });
    return;
  }
  const filename = proofScreenshotFilename();
  triggerDataUrlDownload(filename, dataUrl);
  setProofTransferStatus('Visible screenshot PNG download started.', {
    filename,
    data_url_length: dataUrl.length,
    data_url_hash: fnv1a32(dataUrl),
    note: 'The proof JSON still embeds the screenshot for evidence-pack export; this PNG is an operator review convenience copy.',
  });
}

function proofCaptureDocument(): Record<string, unknown> {
  const attemptId = ensureProofAttemptId();
  const actions: Record<string, unknown>[] = [];
  const captures: Record<string, unknown> = {};

  proofLog.forEach((response, index) => {
    const payload = proofPayload(response);
    const payloadUrl = typeof payload.url === 'string' ? payload.url : undefined;
    const payloadAdapter = typeof payload.adapter === 'string' ? payload.adapter : undefined;
    const latestOutputWitness = typeof payload.latest_output_witness === 'object' && payload.latest_output_witness !== null && !Array.isArray(payload.latest_output_witness)
      ? payload.latest_output_witness as Record<string, unknown>
      : undefined;
    const latestUserTurnWitness = typeof payload.latest_user_turn_witness === 'object' && payload.latest_user_turn_witness !== null && !Array.isArray(payload.latest_user_turn_witness)
      ? payload.latest_user_turn_witness as Record<string, unknown>
      : undefined;
    const payloadText = typeof payload.text === 'string' ? payload.text : undefined;
    const writeReadbackExactProbe = response.type === 'prompt.write' ? proofTextExactlyMatchesProbe(payload.readback) : undefined;
    const submitReadbackExactProbe = response.type === 'prompt.submit'
      ? [payload.composer_readback_before_submit, payload.prompt_before_submit, payload.submitted_prompt].some((value) => proofTextExactlyMatchesProbe(value) === true)
      : undefined;
    const latestOutputWitnessText = typeof latestOutputWitness?.text === 'string' ? latestOutputWitness.text : undefined;
    const latestUserTurnWitnessText = typeof latestUserTurnWitness?.text === 'string' ? latestUserTurnWitness.text : undefined;
    const latestOutputWitnessDocumentOrderIndex = typeof latestOutputWitness?.document_order_index === 'number' ? latestOutputWitness.document_order_index : undefined;
    const latestUserTurnWitnessDocumentOrderIndex = typeof latestUserTurnWitness?.document_order_index === 'number' ? latestUserTurnWitness.document_order_index : undefined;
    const latestOutputWitnessFramePath = typeof latestOutputWitness?.frame_path === 'string' ? latestOutputWitness.frame_path : undefined;
    const latestUserTurnWitnessFramePath = typeof latestUserTurnWitness?.frame_path === 'string' ? latestUserTurnWitness.frame_path : undefined;
    const latestOutputWitnessFrameDepth = typeof latestOutputWitness?.frame_depth === 'number' ? latestOutputWitness.frame_depth : undefined;
    const latestUserTurnWitnessFrameDepth = typeof latestUserTurnWitness?.frame_depth === 'number' ? latestUserTurnWitness.frame_depth : undefined;
    const latestOutputWitnessTextMatchesText = response.type === 'transcript.latest' && latestOutputWitnessText !== undefined && payloadText !== undefined
      ? latestOutputWitnessText === payloadText
      : undefined;
    const latestUserTurnWitnessTextMatchesProbe = response.type === 'transcript.latest' && latestUserTurnWitnessText !== undefined
      ? latestUserTurnWitnessText === CHATGPT_FIRST_PROOF_PROMPT
      : undefined;
    const latestTurnPairSameFrame = response.type === 'transcript.latest' && latestOutputWitness && latestUserTurnWitness
      ? (latestOutputWitnessFramePath ?? null) === (latestUserTurnWitnessFramePath ?? null) && (latestOutputWitnessFrameDepth ?? null) === (latestUserTurnWitnessFrameDepth ?? null)
      : undefined;
    const latestTurnPairUserBeforeAssistant = response.type === 'transcript.latest' && typeof latestUserTurnWitnessDocumentOrderIndex === 'number' && typeof latestOutputWitnessDocumentOrderIndex === 'number'
      ? latestUserTurnWitnessDocumentOrderIndex < latestOutputWitnessDocumentOrderIndex
      : undefined;
    actions.push({
      attempt_id: attemptId,
      sequence_index: index,
      type: response.type,
      request_type: response.type,
      response_type: response.type,
      tab_id: response.tab_id,
      ok: typeof payload.ok === 'boolean' ? payload.ok : undefined,
      readback: payload.readback,
      write_readback_exact_probe: writeReadbackExactProbe,
      prompt_before_submit: payload.prompt_before_submit,
      composer_readback_before_submit: payload.composer_readback_before_submit,
      submitted_prompt: payload.submitted_prompt,
      submit_readback_exact_probe: submitReadbackExactProbe,
      prompt_after_submit: payload.prompt_after_submit,
      url: payloadUrl,
      adapter: payloadAdapter,
      payload_url: payloadUrl,
      payload_adapter: payloadAdapter,
      conversation_route_path: chatgptConversationRoutePath(payloadUrl),
      payload_conversation_route_path: chatgptConversationRoutePath(payloadUrl),
      operator_submit_confirmed: payload.operator_submit_confirmed,
      operator_action: payload.operator_action,
      operator_confirmed_at: payload.operator_confirmed_at,
      submit_method: payload.submit_method,
      latest_output_witness_text: latestOutputWitnessText,
      latest_output_witness_text_matches_text: latestOutputWitnessTextMatchesText,
      latest_output_witness_document_order_index: latestOutputWitnessDocumentOrderIndex,
      latest_output_witness_frame_path: latestOutputWitnessFramePath,
      latest_output_witness_frame_depth: latestOutputWitnessFrameDepth,
      latest_user_turn_witness_text: latestUserTurnWitnessText,
      latest_user_turn_witness_text_matches_probe: latestUserTurnWitnessTextMatchesProbe,
      latest_user_turn_witness_document_order_index: latestUserTurnWitnessDocumentOrderIndex,
      latest_user_turn_witness_frame_path: latestUserTurnWitnessFramePath,
      latest_user_turn_witness_frame_depth: latestUserTurnWitnessFrameDepth,
      latest_turn_pair_same_frame: latestTurnPairSameFrame,
      latest_turn_pair_user_before_assistant: latestTurnPairUserBeforeAssistant,
      payload,
      envelope_request_id: response.request_id,
      envelope_timestamp: response.timestamp,
    });
    if (response.type === 'fixture.capture') captures[`fixture_${index}`] = { ...payload, attempt_id: attemptId };
    if (response.type === 'state.snapshot') captures[`snapshot_${index}`] = { ...payload, attempt_id: attemptId };
    if (response.type === 'transcript.latest') captures[`latest_${index}`] = { ...payload, attempt_id: attemptId };
    if (response.type === 'proof.surface_screenshot') captures[`screenshot_${index}`] = { ...payload, visible_tab_screenshot_data_url: '[embedded in root visible_tab_screenshot_data_url]', attempt_id: attemptId };
  });

  const observedTabIds = Array.from(new Set(actions
    .map((action) => action.tab_id)
    .filter((value): value is number => typeof value === 'number')));
  const observedConversationRoutePaths = Array.from(new Set(actions
    .map((action) => action.conversation_route_path)
    .filter((value): value is string => typeof value === 'string' && value.length > 0)));
  const latestConversationRoutePaths = Array.from(new Set(actions
    .filter((action) => action.type === 'transcript.latest')
    .map((action) => action.conversation_route_path)
    .filter((value): value is string => typeof value === 'string' && value.length > 0)));
  const settledConversationRoutePaths = Array.from(new Set(actions
    .filter((action) => action.type === 'fixture.capture' || action.type === 'state.snapshot')
    .map((action) => action.conversation_route_path)
    .filter((value): value is string => typeof value === 'string' && value.length > 0)));
  const proofChainConversationRoutePath = latestConversationRoutePaths.length === 1 ? latestConversationRoutePaths[0] : null;
  const screenshotPayload = latestProofScreenshotPayload();
  const visibleTabScreenshotDataUrl = typeof screenshotPayload?.visible_tab_screenshot_data_url === 'string'
    ? screenshotPayload.visible_tab_screenshot_data_url
    : undefined;

  return {
    schema_version: 1,
    surface_key: 'chatgpt',
    observed_tab_ids: observedTabIds,
    single_tab_context: observedTabIds.length === 1,
    proof_chain_tab_id: observedTabIds.length === 1 ? observedTabIds[0] : null,
    observed_conversation_route_paths: observedConversationRoutePaths,
    latest_conversation_route_paths: latestConversationRoutePaths,
    settled_conversation_route_paths: settledConversationRoutePaths,
    proof_chain_conversation_route_path: proofChainConversationRoutePath,
    same_conversation_route_after_latest: proofChainConversationRoutePath !== null && settledConversationRoutePaths.includes(proofChainConversationRoutePath),
    write_readback_exact_probe_seen: actions.some((action) => action.type === 'prompt.write' && action.write_readback_exact_probe === true),
    submit_readback_exact_probe_seen: actions.some((action) => action.type === 'prompt.submit' && action.submit_readback_exact_probe === true),
    proof_live_gate_ok_seen: actions.some((action) => asRecord(action.payload)?.proof_live_gate_ok === true),
    proof_live_gate_verdicts: Array.from(new Set(actions
      .map((action) => asRecord(action.payload)?.proof_live_gate_verdict)
      .filter((value): value is string => typeof value === 'string' && value.length > 0))),
    capture_kind: 'sidepanel-manual-chatgpt-first-proof',
    generated_at: new Date().toISOString(),
    attempt_id: attemptId,
    visible_tab_screenshot_data_url: visibleTabScreenshotDataUrl,
    surface_screenshot_capture: screenshotPayload ? { ...screenshotPayload, visible_tab_screenshot_data_url: visibleTabScreenshotDataUrl ? '[embedded in root visible_tab_screenshot_data_url]' : undefined } : undefined,
    operator_transfer: {
      recommended_json_filename: proofCaptureJsonFilename(attemptId),
      recommended_screenshot_filename: proofScreenshotFilename(attemptId),
      sidepanel_buttons: {
        copy_json: 'proof-copy-json',
        download_json: 'proof-download-json',
        download_gate: 'proof-attempt-readiness',
        download_screenshot: 'proof-download-screenshot',
        save_recovery_vault: 'proof-save-vault',
        restore_recovery_vault: 'proof-restore-vault',
        download_recovery_json: 'proof-download-vault',
        clear_recovery_vault: 'proof-clear-vault',
      },
      recovery_vault: {
        storage_key: PROOF_RECOVERY_VAULT_KEY,
        storage_backend: 'chrome.storage.local',
        purpose: 'local recovery only; downloaded proof JSON remains the handoff source of truth',
      },
      finalize_command: `glassttyd proof-attempt-audit --input ${proofCaptureJsonFilename(attemptId)} --require-ready-to-download --pretty && glassttyd proof-autopilot --execute-live --input ${proofCaptureJsonFilename(attemptId)} --clean --pretty`,
      note: 'Use Download proof JSON as the primary transfer path; clipboard copy and local recovery vault are convenience fallbacks and can be truncated, blocked, or quota-limited by the browser.',
    },
    probe_prompt: {
      text: CHATGPT_FIRST_PROOF_PROMPT,
      expected_exact_reply: CHATGPT_FIRST_PROOF_EXPECTED_REPLY,
    },
    operator_notes: [
      'Use the same attempt_id, the same explicit tab_id, monotonic sequence_index values, and per-action ChatGPT adapter/url witnesses for write/readback, submit, and transcript.latest readback; the winning write and submit readbacks must exactly equal the checkpoint prompt, not merely contain it.',
      'Use the dedicated gated proof submit button so the assembled JSON includes a proof-live-gate verdict, an operator-submit attestation, and a submit-time composer readback matching the checkpoint prompt; ordinary prompt.submit is intentionally not enough for the evaluator.',
      'After submit, wait until ChatGPT has settled on a /c/ conversation route before running transcript.latest, then run the proof latest helper so transcript.latest carries matching latest_output_witness.text, a latest_user_turn_witness.text matching the checkpoint prompt, same-frame user-before-assistant witness order indices with explicit frame_depth/frame_path context, and the settled fixture receives a later sequence_index plus the same tab_id, the same /c/ conversation route path, and ChatGPT url/adapter witnesses.',
      'Use Download proof JSON as the primary transfer path. That button runs a final attempt-readiness gate and embeds a fresh proof.operator_readiness envelope before download; then run proof-attempt-audit and proof-autopilot with --input pointing to that downloaded JSON.',
      'A reviewable evaluator verdict remains local-only and does not widen support claims.',
    ],
    actions,
    captures,
    raw_envelopes: proofLog,
  };
}

function proofRecoveryVaultRecordFromDocument(document: Record<string, unknown>, reason: string): ProofRecoveryVaultRecord {
  const documentJson = JSON.stringify(document);
  const screenshotCapture = asRecord(document.surface_screenshot_capture);
  const screenshotDimensions = screenshotCapture?.screenshot_dimensions;
  const screenshotHash = typeof screenshotCapture?.screenshot_data_url_hash === 'string'
    ? screenshotCapture.screenshot_data_url_hash
    : undefined;
  const hasScreenshot = typeof document.visible_tab_screenshot_data_url === 'string'
    && document.visible_tab_screenshot_data_url.startsWith('data:image/png;base64,');
  const warnings: string[] = [];
  if (!hasScreenshot) warnings.push('No embedded visible-tab screenshot has been captured yet.');
  if (documentJson.length > 4_500_000) {
    warnings.push('Proof document is large; browser local storage quota may reject the full recovery copy. Download proof JSON as soon as possible.');
  }
  return {
    schema_version: 1,
    storage_key: PROOF_RECOVERY_VAULT_KEY,
    storage_backend: 'chrome.storage.local',
    saved_at: new Date().toISOString(),
    save_reason: reason,
    attempt_id: typeof document.attempt_id === 'string' ? document.attempt_id : ensureProofAttemptId(),
    envelope_count: Array.isArray(document.raw_envelopes) ? document.raw_envelopes.length : proofLog.length,
    document_bytes: documentJson.length,
    document_hash: fnv1a32(documentJson),
    has_screenshot: hasScreenshot,
    screenshot_data_url_hash: screenshotHash,
    screenshot_dimensions: screenshotDimensions,
    saved_full_document: true,
    document,
    redacted_preview: redactLargeProofValuesForDisplay(document),
    warnings,
  };
}

async function saveProofRecoveryVault(reason = 'manual'): Promise<ProofRecoveryVaultRecord | undefined> {
  if (!proofLog.length) {
    setProofVaultStatus('Recovery vault not saved.', { blocker: 'no proof capture is assembled yet' });
    return undefined;
  }
  const document = proofCaptureDocument();
  const record = proofRecoveryVaultRecordFromDocument(document, reason);
  try {
    await chrome.storage.local.set({ [PROOF_RECOVERY_VAULT_KEY]: record });
    setProofVaultStatus(reason === 'auto' ? 'Recovery vault auto-saved locally.' : 'Recovery vault saved locally.', {
      attempt_id: record.attempt_id,
      envelope_count: record.envelope_count,
      bytes: record.document_bytes,
      document_hash: record.document_hash,
      has_screenshot: record.has_screenshot,
      warnings: record.warnings,
    });
    return record;
  } catch (error) {
    const fallback: ProofRecoveryVaultRecord = {
      ...record,
      saved_full_document: false,
      document: undefined,
      warnings: [
        ...record.warnings,
        'Full proof document could not be persisted in chrome.storage.local. Download proof JSON immediately.',
      ],
    };
    try {
      await chrome.storage.local.set({ [PROOF_RECOVERY_VAULT_KEY]: fallback });
    } catch {
      // Ignore fallback failure; the visible status is the important operator signal.
    }
    setProofVaultStatus('Recovery vault save failed; download proof JSON immediately.', {
      error: error instanceof Error ? error.message : String(error),
      attempted_bytes: record.document_bytes,
      document_hash: record.document_hash,
      fallback_saved_without_full_document: true,
    });
    return fallback;
  }
}

async function loadProofRecoveryVault(): Promise<ProofRecoveryVaultRecord | undefined> {
  const storage = await chrome.storage.local.get(PROOF_RECOVERY_VAULT_KEY);
  const record = storage[PROOF_RECOVERY_VAULT_KEY];
  if (!record || typeof record !== 'object' || Array.isArray(record)) return undefined;
  return record as ProofRecoveryVaultRecord;
}

async function restoreProofRecoveryVault(): Promise<void> {
  const record = await loadProofRecoveryVault();
  if (!record) {
    setProofVaultStatus('No local recovery vault entry found.');
    return;
  }
  const document = asRecord(record.document);
  const rawEnvelopes = Array.isArray(document?.raw_envelopes) ? document.raw_envelopes : [];
  if (!document || !rawEnvelopes.length) {
    const output = proofOutput();
    if (output) output.textContent = JSON.stringify(record.redacted_preview ?? record, null, 2);
    setProofVaultStatus('Recovery vault restored preview only; full raw envelopes were not saved.', {
      attempt_id: record.attempt_id,
      saved_at: record.saved_at,
      document_hash: record.document_hash,
      warnings: record.warnings,
    });
    return;
  }
  proofLog = rawEnvelopes as Envelope[];
  const input = proofAttemptInput();
  if (input) input.value = record.attempt_id;
  renderProofCapture({ persist: false });
  setProofVaultStatus('Recovery vault restored into side-panel proof log.', {
    attempt_id: record.attempt_id,
    saved_at: record.saved_at,
    envelope_count: record.envelope_count,
    document_hash: record.document_hash,
    has_screenshot: record.has_screenshot,
    next_action: 'Review the preview, then Download proof JSON before continuing operator handoff.',
  });
}

async function downloadProofRecoveryVaultJson(): Promise<void> {
  const record = await loadProofRecoveryVault();
  const document = asRecord(record?.document);
  if (!record || !document) {
    setProofVaultStatus('Recovery vault download blocked.', { blocker: 'no full proof document is saved locally' });
    return;
  }
  const filename = proofCaptureJsonFilename(record.attempt_id);
  const documentJson = JSON.stringify(document, null, 2);
  triggerBlobDownload(filename, 'application/json;charset=utf-8', documentJson);
  setProofVaultStatus('Recovery vault proof JSON download started.', {
    filename,
    bytes: documentJson.length,
    document_hash: fnv1a32(documentJson),
    saved_at: record.saved_at,
  });
}

async function clearProofRecoveryVault(): Promise<void> {
  await chrome.storage.local.remove(PROOF_RECOVERY_VAULT_KEY);
  setProofVaultStatus('Recovery vault cleared from chrome.storage.local.');
}

function renderProofCapture(options: { persist?: boolean } = {}): void {
  const output = proofOutput();
  if (!output) return;
  if (!proofLog.length) {
    output.textContent = 'No proof capture assembled yet.';
    return;
  }
  output.textContent = JSON.stringify(redactLargeProofValuesForDisplay(proofCaptureDocument()), null, 2);
  if (options.persist !== false) {
    void saveProofRecoveryVault('auto').catch((error) => {
      setProofVaultStatus('Recovery vault auto-save failed.', { error: error instanceof Error ? error.message : String(error) });
    });
  }
}

async function proofRequest(type: Envelope['type'], payload: Record<string, unknown> = {}, evidence: Record<string, unknown> = {}): Promise<Envelope> {
  const attemptId = ensureProofAttemptId();
  const response = await request(type, { ...payload, attempt_id: attemptId });
  const responsePayload = proofPayload(response);
  const loggedResponse = {
    ...response,
    payload: {
      ...responsePayload,
      ...evidence,
      attempt_id: attemptId,
    },
  } as Envelope;
  proofLog.push(loggedResponse);
  renderProofCapture();
  return loggedResponse;
}

async function writeCheckpointAndCapture(): Promise<void> {
  const draft = document.getElementById('prompt-draft') as HTMLTextAreaElement | null;
  if (draft) draft.value = CHATGPT_FIRST_PROOF_PROMPT;
  proofLog = [];
  await proofRequest('prompt.write', { text: CHATGPT_FIRST_PROOF_PROMPT });
  await proofRequest('fixture.capture');
  await proofRequest('state.snapshot');
}

async function readLatestAndCapture(): Promise<void> {
  await proofRequest('transcript.latest');
  await proofRequest('fixture.capture');
  await proofRequest('state.snapshot');
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
    const text = (document.getElementById('prompt-draft') as HTMLTextAreaElement | null)?.value ?? '';
    void request('prompt.write', { text });
  });
  document.getElementById('submit-prompt')?.addEventListener('click', () => void request('prompt.submit'));
  document.getElementById('proof-new-attempt')?.addEventListener('click', () => {
    const input = proofAttemptInput();
    if (input) input.value = `chatgpt-first-proof-${compactTimestampForAttemptId()}`;
    proofLog = [];
    renderProofCapture();
  });
  document.getElementById('proof-attempt-readiness')?.addEventListener('click', () => void runProofAttemptReadiness().catch((error) => setProofAttemptReadinessStatus('Attempt readiness check failed.', {
    schema_version: 1,
    tool: 'glasstty-chatgpt-sidepanel-attempt-readiness',
    checked_at: new Date().toISOString(),
    attempt_id: ensureProofAttemptId(),
    ok: false,
    verdict: 'proof-attempt-readiness-error',
    next_stage: 'debug-sidepanel',
    next_action: 'Refresh the side panel and run proof-status/autopilot from the CLI.',
    blockers: [error instanceof Error ? error.message : String(error)],
    warnings: [],
    checks: {},
    observed: {},
    cli_after_download: '',
  })));
  document.getElementById('proof-write-capture')?.addEventListener('click', () => void writeCheckpointAndCapture().catch(console.error));
  document.getElementById('proof-live-gate-check')?.addEventListener('click', () => void runProofLiveGate().catch(console.error));
  document.getElementById('proof-capture-screenshot')?.addEventListener('click', () => void captureVisibleProofScreenshot().catch((error) => setProofTransferStatus('Screenshot capture failed.', { error: error instanceof Error ? error.message : String(error) })));
  document.getElementById('proof-submit')?.addEventListener('click', () => void guardedProofSubmit().catch(console.error));
  document.getElementById('proof-read-latest')?.addEventListener('click', () => void readLatestAndCapture().catch(console.error));
  document.getElementById('proof-copy-json')?.addEventListener('click', () => void copyProofCaptureJson().catch(console.error));
  document.getElementById('proof-download-json')?.addEventListener('click', () => {
    void downloadProofCaptureJson().catch((error) => setProofTransferStatus('Proof capture JSON download failed.', {
      error: error instanceof Error ? error.message : String(error),
    }));
  });
  document.getElementById('proof-download-screenshot')?.addEventListener('click', () => {
    try {
      downloadProofScreenshotPng();
    } catch (error) {
      setProofTransferStatus('Screenshot download failed.', { error: error instanceof Error ? error.message : String(error) });
    }
  });
  document.getElementById('proof-save-vault')?.addEventListener('click', () => void saveProofRecoveryVault('manual').catch((error) => setProofVaultStatus('Recovery vault save failed.', { error: error instanceof Error ? error.message : String(error) })));
  document.getElementById('proof-restore-vault')?.addEventListener('click', () => void restoreProofRecoveryVault().catch((error) => setProofVaultStatus('Recovery vault restore failed.', { error: error instanceof Error ? error.message : String(error) })));
  document.getElementById('proof-download-vault')?.addEventListener('click', () => void downloadProofRecoveryVaultJson().catch((error) => setProofVaultStatus('Recovery vault download failed.', { error: error instanceof Error ? error.message : String(error) })));
  document.getElementById('proof-clear-vault')?.addEventListener('click', () => void clearProofRecoveryVault().catch((error) => setProofVaultStatus('Recovery vault clear failed.', { error: error instanceof Error ? error.message : String(error) })));
  document.getElementById('proof-clear')?.addEventListener('click', () => {
    proofLog = [];
    renderProofCapture({ persist: false });
    setProofVaultStatus('Proof log cleared in memory. Local recovery vault is unchanged unless you press Clear recovery vault.');
  });
  chrome.storage.onChanged.addListener((_changes, areaName) => {
    if (areaName === 'session' || areaName === 'local') void refreshStatus();
  });
  const existingVault = await loadProofRecoveryVault().catch(() => undefined);
  if (existingVault) {
    setProofVaultStatus('Recovery vault available locally.', {
      attempt_id: existingVault.attempt_id,
      saved_at: existingVault.saved_at,
      envelope_count: existingVault.envelope_count,
      document_hash: existingVault.document_hash,
      has_screenshot: existingVault.has_screenshot,
      action: 'Press Restore recovery vault or Download recovery JSON if the side-panel capture was lost.',
    });
  }
  await refreshStatus();
});
