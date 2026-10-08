import { adapterDescriptors, supportedMatchPatterns } from '../adapters';
import { getActiveTab, getTabById, isSupportedUrl } from '../shared/browser';
import { deriveNativeLaneDiagnosis, type NativeLaneDiagnosis } from '../shared/native-lane';
import { appendPersistentNativeEvent, buildPersistentDiagnosticsSnapshot, normalizePersistentBridgeHistory, recordPersistentWorkerBoot, type PersistentBridgeHistory } from '../shared/persistent-history';
import { makeEnvelope, replyTo, type Envelope } from '../shared/protocol';
import { describeReceiverCoverageExperimentPlan, describeReceiverCoveragePolicyHints, describeReceiverPrimingAudit, mergePrimedReceiverKeys, planReceiverPriming, type ReceiverCoverageExperimentPlan, type ReceiverPrimingAuditSummary } from '../shared/receiver-priming';
import { buildContentScriptExperimentRegistration, dynamicContentScriptRulesFromRegisteredScripts, glassTTYExperimentIdFromScriptId, staticContentScriptRulesFromManifest, summarizeContentScriptPolicy, type ContentScriptExperimentId, type ContentScriptPolicySummary } from '../shared/content-script-experiments';
import { contentReceiverKey, contentReceiverLabel, describeContentReceiverAudit, mergeContentReceivers, messageTargetForReceivers, preferredContentReceiver, reconcileContentReceivers, summarizeContentReceivers, type ContentReceiverResolutionSummary, type ContentReceiverResolverAudit, type ContentReceiverState } from '../shared/receivers';

declare const __GLASSTTY_BUNDLE_VERSION__: string;

const HOST_NAME = 'com.glasstty.bridge';
const STORAGE_KEY = 'bridgeState';
const PERSISTENT_HISTORY_KEY = 'bridgePersistentHistory';
const SESSION_TABS_KEY = 'supportedTabs';
const SESSION_PRIMED_RECEIVERS_KEY = 'primedReceivers';
const TRACE_KEY = 'bridgeTrace';
const TRACE_LIMIT = 160;
const MENU_PATTERNS = supportedMatchPatterns();
const MENU_OPEN_PANEL = 'open-panel';
const MENU_SET_TARGET = 'set-target-tab';
const MENU_READ_LATEST = 'read-latest';
const MENU_READ_PROMPT = 'read-prompt';
const MENU_WRITE_SELECTION = 'write-selection-to-prompt';
const MENU_CAPTURE_FIXTURE = 'capture-fixture';
const NATIVE_RECONNECT_ALARM = 'native-reconnect';
const NATIVE_RECONNECT_MINUTES = 0.5;
const NATIVE_RECONNECT_MAX_MINUTES = 8;
const MANIFEST_VERSION = chrome.runtime.getManifest().version;
const BUNDLE_VERSION_IS_CURRENT = MANIFEST_VERSION === __GLASSTTY_BUNDLE_VERSION__;
const STALE_BUNDLE_RELOAD_KEY = 'staleBundleReloadAttempt';
let nativePort: chrome.runtime.Port | null = null;
let pendingNativeHealth: { requestId: string; envelopeRequestId: string; startedAt: number; timeoutId: number } | null = null;
const WORKER_BOOT_ID = typeof crypto !== 'undefined' && 'randomUUID' in crypto ? crypto.randomUUID() : `boot-${Date.now()}`;

async function enforceCurrentBundle(): Promise<boolean> {
  if (BUNDLE_VERSION_IS_CURRENT) {
    await chrome.storage.local.remove(STALE_BUNDLE_RELOAD_KEY);
    return true;
  }

  const expected = `${__GLASSTTY_BUNDLE_VERSION__}->${MANIFEST_VERSION}`;
  const stored = await chrome.storage.local.get(STALE_BUNDLE_RELOAD_KEY);
  if (stored[STALE_BUNDLE_RELOAD_KEY] === expected) {
    console.error(
      `GlassTTY worker bundle ${__GLASSTTY_BUNDLE_VERSION__} is still stale for manifest ${MANIFEST_VERSION} after one reload; rebuild and reload the unpacked extension`,
    );
    return false;
  }

  await chrome.storage.local.set({ [STALE_BUNDLE_RELOAD_KEY]: expected });
  console.warn(
    `GlassTTY worker bundle ${__GLASSTTY_BUNDLE_VERSION__} is stale for manifest ${MANIFEST_VERSION}; reloading the unpacked extension once`,
  );
  (chrome.runtime as typeof chrome.runtime & { reload: () => void }).reload();
  return false;
}
const WORKER_BOOT_AT = new Date().toISOString();
const OFFSCREEN_DOCUMENT_PATH = 'offscreen/index.html';
const OFFSCREEN_JUSTIFICATION = 'GlassTTY hidden diagnostics context for bridge proof and future headless lab work';
const OFFSCREEN_REASONS: chrome.offscreen.Reason[] = ['TESTING', 'DOM_PARSER'];
let creatingOffscreenDocument: Promise<void> | null = null;

interface ExtensionContextSummary {
  runtimeId: string;
  runtimeVersion: string;
  hasRuntimeGetContexts: boolean;
  openContexts: Array<{
    contextId?: string;
    contextType: string;
    documentId?: string;
    documentUrl?: string;
    documentOrigin?: string;
    tabId?: number;
    windowId?: number;
    frameId?: number;
    incognito?: boolean;
  }>;
}

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

interface TraceEntry {
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

interface NativeBrokerOwnerMetadata {
  native_host?: string;
  socket_path?: string;
  lock_path?: string;
  metadata_path?: string;
  host_identity?: NativeHostIdentity;
}

interface NativeBrokerSummary {
  role?: string;
  lock_path?: string;
  metadata_path?: string;
  socket_path?: string;
  socket_exists?: boolean;
  connected_clients?: number | null;
  owner_metadata?: NativeBrokerOwnerMetadata;
}

interface NativeConnectionState {
  connected: boolean;
  laneDiagnosis?: NativeLaneDiagnosis;
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
  lastOneShotProbeRequestId?: string;
  lastOneShotProbeTrigger?: string;
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
}

interface RuntimeLaneState {
  currentBootId: string;
  currentBootAt: string;
  bootCount: number;
  lastBootstrapAt: string;
  lastStartupSignalAt?: string;
  lastInstalledAt?: string;
  lastSuspendSignalAt?: string;
}

interface OffscreenReadyPayload {
  readyAt: string;
  href: string;
  title: string;
  userAgent: string;
  visibilityState: string;
}

interface OffscreenSemanticOutline {
  heading_outline: string[];
  prompt_labels: string[];
  accessible_names: string[];
  prompt_descriptions: string[];
  submit_labels: string[];
  form_names: string[];
  form_actions: string[];
  fieldset_legends: string[];
  dialog_names: string[];
  iframe_names: string[];
  iframe_titles: string[];
  control_kinds: string[];
  option_labels: string[];
  choice_groups: string[];
  autocomplete_tokens: string[];
  state_flags: string[];
  constraint_hints: string[];
  link_hosts: string[];
}

interface OffscreenCandidateInfo {
  selector_hint: string;
  score: number;
  text_length: number;
  visible: boolean;
  label_text?: string;
  labels?: string[];
  accessible_name?: string;
  accessible_names?: string[];
  description_text?: string;
  descriptions?: string[];
  fieldset_legend?: string;
  fieldset_legends?: string[];
  dialog_name?: string;
  dialog_role?: string;
  dialog_modal?: boolean;
  dialog_open?: boolean;
  control_kind?: string;
  form_name?: string;
  form_action?: string;
  form_method?: string;
  option_count?: number;
  option_labels?: string[];
  selected_options?: string[];
  required?: boolean;
  invalid?: boolean;
  role?: string;
  text_sample?: string;
  submit_action?: string;
  submit_method?: string;
  submit_target?: string;
}

interface OffscreenDomSummary {
  parsedAt: string;
  title: string;
  baseUrl?: string;
  textLength: number;
  textSample: string;
  linkCount: number;
  buttonCount: number;
  formCount: number;
  dialogCount: number;
  iframeCount: number;
  textareaCount: number;
  inputCount: number;
  editableCount: number;
  selectorMatches: Array<{ selector: string; count: number; error?: string }>;
  headings: Array<{ level: string; text: string }>;
  editableCandidates: Array<{
    tagName: string;
    type?: string;
    id?: string;
    name?: string;
    placeholder?: string;
    ariaLabel?: string;
    selectorHint: string;
    valueLength: number;
    textLength: number;
    labelText?: string;
    labels?: string[];
    accessibleName?: string;
    accessibleNames?: string[];
    descriptionText?: string;
    descriptions?: string[];
    fieldsetLegend?: string;
    fieldsetLegends?: string[];
    dialogName?: string;
    dialogRole?: string;
    dialogModal?: boolean;
    dialogOpen?: boolean;
    controlKind?: string;
    formName?: string;
    formAction?: string;
    formMethod?: string;
    optionCount?: number;
    optionLabels?: string[];
    selectedOptions?: string[];
    required?: boolean;
    invalid?: boolean;
  }>;
  submitCandidates: OffscreenCandidateInfo[];
  semanticOutline: OffscreenSemanticOutline;
  linkSamples: Array<{
    text: string;
    href: string;
    resolvedHref?: string;
  }>;
  formSamples: Array<{
    method: string;
    action?: string;
    resolvedAction?: string;
    inputCount: number;
    textareaCount: number;
    buttonCount: number;
  }>;
  dialogSamples: Array<{
    selectorHint: string;
    role: string;
    name?: string;
    modal?: boolean;
    open?: boolean;
  }>;
  iframeSamples: Array<{
    selectorHint: string;
    src?: string;
    resolvedSrc?: string;
    name?: string;
    title?: string;
  }>;
}

interface OffscreenFixtureCapture {
  adapter: string;
  url: string;
  title?: string;
  prompt: string | null;
  latest_output: string | null;
  selection: string | null;
  candidates: {
    inputs: OffscreenCandidateInfo[];
    outputs: OffscreenCandidateInfo[];
  };
  html_samples?: {
    prompt?: string | null;
    latest_output?: string | null;
    submit?: string | null;
  };
  metadata?: Record<string, unknown>;
}

interface OffscreenState {
  supported: boolean;
  requested: boolean;
  enabled: boolean;
  url: string;
  contextCount: number;
  documentUrls: string[];
  runtimeGetContexts: boolean;
  responsive?: boolean;
  lastReady?: OffscreenReadyPayload;
  lastDomSummary?: OffscreenDomSummary;
  lastError?: string;
}

interface NativeOverflowSummary {
  kind?: string;
  artifact_path?: string;
  original_type?: string;
  message_size_bytes?: number;
  limit_bytes?: number;
  captured_at?: string;
  request_id?: string;
  tab_id?: number;
  emitted_at?: string;
}

interface NativeOverflowInventoryDigest {
  latest_path?: string;
  latest_exists?: boolean;
  artifact_count?: number;
  total_disk_bytes?: number;
  total_reported_message_bytes?: number;
  message_type_counts?: Record<string, number>;
  newest_captured_at?: string;
  oldest_captured_at?: string;
  latest_artifact_path?: string | null;
  latest_artifact_exists?: boolean;
  latest_artifact_in_inventory?: boolean;
  recent_limit?: number;
  recent_artifacts?: Array<{
    path?: string;
    name?: string;
    captured_at?: string;
    message_type?: string;
    request_id?: string;
    tab_id?: number;
    reported_size_bytes?: number;
    size_on_disk_bytes?: number;
    parse_ok?: boolean;
  }>;
}

interface NativeStatusSnapshot {
  capturedAt: string;
  trigger: string;
  native_host?: string;
  socket_path?: string;
  state_root?: string;
  events_path?: string;
  event_count?: number;
  latest_dir?: string;
  fixtures_dir?: string;
  run_dir?: string;
  host_identity?: NativeHostIdentity;
  broker?: NativeBrokerSummary;
  matches_persistent_host?: boolean;
  last_oversized_host_message?: NativeOverflowSummary;
  overflow_inventory?: NativeOverflowInventoryDigest;
}

interface BridgeState {
  activeTab?: { id?: number; url?: string; windowId?: number; supported: boolean; discarded?: boolean; frozen?: boolean };
  targetTab?: SupportedTabState | null;
  selectedTargetTabId?: number | null;
  supportedTabs?: SupportedTabState[];
  adapters?: ReturnType<typeof adapterDescriptors>;
  lastAdapterDetected?: unknown;
  lastContentMessage?: unknown;
  lastNativeMessage?: unknown;
  lastOversizedHostMessage?: NativeOverflowSummary;
  lastNativeStatusSnapshot?: NativeStatusSnapshot;
  lastNativeStatusError?: string;
  lastError?: unknown;
  nativeConnection?: NativeConnectionState;
  runtime?: RuntimeLaneState;
  persistentDiagnostics?: PersistentBridgeHistory;
  updatedAt?: string;
}

interface ReceiverCoveragePolicyHint {
  lever: 'runtime_priming' | 'manifest_all_frames' | 'manifest_match_about_blank' | 'manifest_match_origin_as_fallback';
  rationale: string;
  frameCount: number;
  frameIds?: number[];
}

interface ReceiverCoveragePolicyHints {
  manifestPolicy: ContentScriptPolicySummary;
  runtimePrimingCandidateCount: number;
  relatedFrameGapCount: number;
  aboutBlankGapCount: number;
  opaqueRelatedFrameGapCount: number;
  missingTargetGapCount: number;
  hints: ReceiverCoveragePolicyHint[];
}

interface ReceiverCoverageAuditSummary {
  frameCount: number;
  supportedUrlCount: number;
  relatedFrameUrlCount: number;
  observedCount: number;
  primedCount: number;
  topFrameCount: number;
  candidateCount: number;
  candidateDocumentCount: number;
  candidateFrameCount: number;
  gapCount: number;
  skippedReasonCounts: ReceiverPrimingAuditSummary['counts']['skippedReasonCounts'];
  plan: ReceiverPrimingAuditSummary['plan'];
  frames: ReceiverPrimingAuditSummary['frames'];
  policyHints: ReceiverCoveragePolicyHints;
  experimentPlan: ReceiverCoverageExperimentPlan;
}

interface ReceiverAuditSummary {
  targetTabId?: number;
  targetTabTitle?: string;
  targetTabUrl?: string;
  selectedTargetTabId?: number | null;
  receiverCount: number;
  readyReceiverCount: number;
  receiverSelectionPolicy: string;
  receiverInventoryStatus: string;
  receiverOverrideKey?: string | null;
  receiverOverrideStatus?: string;
  selectedReceiverKey?: string;
  selectedReceiverLabel?: string;
  resolverPolicy?: ContentReceiverResolverAudit['resolverPolicy'];
  receiverResolution?: ContentReceiverResolutionSummary;
  rankedMatches?: ContentReceiverResolutionSummary[];
  coverageAudit?: ReceiverCoverageAuditSummary;
  receivers: Array<{
    key?: string | null;
    label: string;
    frameId?: number;
    documentId?: string;
    adapter?: string;
    documentLifecycle?: string;
    frameType?: string;
    parentFrameId?: number;
    parentDocumentId?: string;
    frameUrl?: string;
    frameOrigin?: string;
    frameDepth?: number;
    framePathFrameIds?: number[];
    framePathHosts?: string[];
    framePathLabel?: string;
    receiverReady?: boolean;
    lastSeenAt: string;
  }>;
}

interface BridgeProbePayload {
  probeAt: string;
  manifest: {
    version: string;
    minimumChromeVersion?: string;
    permissions?: string[];
    hostPermissions?: string[];
    probeUrl: string;
    contentScriptPolicy: ContentScriptPolicySummary;
  };
  status: BridgeState;
  receiverAudit?: ReceiverAuditSummary;
  contexts: ExtensionContextSummary;
  offscreen: OffscreenState;
  nativeStatusSnapshot?: NativeStatusSnapshot;
  trace: { events: TraceEntry[] };
  sessionMirror: {
    bridgeState?: BridgeState;
    bridgeTrace?: TraceEntry[];
    supportedTabs?: SupportedTabState[];
  };
}

function log(...args: unknown[]): void {
  console.log('[GlassTTY background]', ...args);
}

function errorMessage(error: unknown): string {
  return error instanceof Error ? error.message : String(error);
}

function sleep(ms: number): Promise<void> {
  return new Promise((resolve) => self.setTimeout(resolve, ms));
}

function originFromUrl(url: string | undefined): string | undefined {
  if (!url) return undefined;
  try {
    return new URL(url).origin;
  } catch {
    return undefined;
  }
}

function hostnameFromUrl(url: string | undefined): string | undefined {
  if (!url) return undefined;
  try {
    return new URL(url).hostname || undefined;
  } catch {
    return undefined;
  }
}

function compactString(value: unknown): string | undefined {
  if (typeof value !== 'string') return undefined;
  const trimmed = value.trim();
  return trimmed || undefined;
}

function uniqueStrings(values: Array<unknown>): string[] {
  const out: string[] = [];
  const seen = new Set<string>();
  for (const value of values) {
    const normalized = compactString(value);
    if (!normalized || seen.has(normalized)) continue;
    seen.add(normalized);
    out.push(normalized);
  }
  return out;
}

function uniqueNumbers(values: Array<number | null | undefined>): number[] {
  const out: number[] = [];
  const seen = new Set<number>();
  for (const value of values) {
    if (typeof value !== 'number' || seen.has(value)) continue;
    seen.add(value);
    out.push(value);
  }
  return out;
}

function dynamicScriptingApi(): typeof chrome.scripting & {
  getRegisteredContentScripts?: () => Promise<unknown[]>;
  registerContentScripts?: (scripts: unknown[]) => Promise<void>;
  unregisterContentScripts?: (filter?: { ids?: string[] }) => Promise<void>;
} {
  return chrome.scripting as typeof chrome.scripting & {
    getRegisteredContentScripts?: () => Promise<unknown[]>;
    registerContentScripts?: (scripts: unknown[]) => Promise<void>;
    unregisterContentScripts?: (filter?: { ids?: string[] }) => Promise<void>;
  };
}

async function glassTTYDynamicContentScripts(): Promise<Array<Record<string, unknown>>> {
  const scripting = dynamicScriptingApi();
  if (!scripting.getRegisteredContentScripts) return [];
  try {
    const scripts = await scripting.getRegisteredContentScripts();
    return (scripts as Array<Record<string, unknown>>).filter((script) => glassTTYExperimentIdFromScriptId(compactString(script.id)) !== undefined);
  } catch (error) {
    await appendTrace('content_scripts.dynamic_inventory_failed', { error: errorMessage(error) }, 'warn');
    return [];
  }
}

async function contentScriptPolicySummary(manifest = chrome.runtime.getManifest()): Promise<ContentScriptPolicySummary> {
  const staticRules = staticContentScriptRulesFromManifest(manifest as Record<string, unknown>);
  const dynamicRules = dynamicContentScriptRulesFromRegisteredScripts(await glassTTYDynamicContentScripts());
  return summarizeContentScriptPolicy(staticRules, dynamicRules);
}

async function contentScriptExperimentStatus(manifest = chrome.runtime.getManifest()): Promise<{
  policy: ContentScriptPolicySummary;
  dynamicScriptCount: number;
}> {
  const dynamicScripts = await glassTTYDynamicContentScripts();
  const dynamicRules = dynamicContentScriptRulesFromRegisteredScripts(dynamicScripts);
  return {
    policy: summarizeContentScriptPolicy(staticContentScriptRulesFromManifest(manifest as Record<string, unknown>), dynamicRules),
    dynamicScriptCount: dynamicScripts.length,
  };
}

async function clearContentScriptExperimentRegistration(options: { traceReason?: string } = {}): Promise<ContentScriptPolicySummary> {
  const dynamicScripts = await glassTTYDynamicContentScripts();
  const ids = uniqueStrings(dynamicScripts.map((script) => script.id));
  if (ids.length) {
    const scripting = dynamicScriptingApi();
    if (!scripting.unregisterContentScripts) throw new Error('chrome.scripting.unregisterContentScripts is unavailable in this Chrome build');
    await scripting.unregisterContentScripts({ ids });
  }
  const policy = await contentScriptPolicySummary();
  await appendTrace('content_scripts.experiment_cleared', { clearedIds: ids, traceReason: options.traceReason ?? null, activeExperiment: policy.activeExperiment?.id ?? null });
  return policy;
}

async function applyContentScriptExperiment(experimentId: ContentScriptExperimentId): Promise<{
  policy: ContentScriptPolicySummary;
  registration: ReturnType<typeof buildContentScriptExperimentRegistration>;
}> {
  const manifest = chrome.runtime.getManifest();
  const registration = buildContentScriptExperimentRegistration(staticContentScriptRulesFromManifest(manifest as Record<string, unknown>), experimentId);
  const existing = await glassTTYDynamicContentScripts();
  const existingIds = uniqueStrings(existing.map((script) => script.id));
  if (existingIds.length) {
    const scripting = dynamicScriptingApi();
    if (!scripting.unregisterContentScripts) throw new Error('chrome.scripting.unregisterContentScripts is unavailable in this Chrome build');
    await scripting.unregisterContentScripts({ ids: existingIds });
  }
  if (!registration.registeredScripts.length) {
    throw new Error(`no static GlassTTY content scripts were available to clone for ${experimentId}`);
  }
  const scripting = dynamicScriptingApi();
  if (!scripting.registerContentScripts) throw new Error('chrome.scripting.registerContentScripts is unavailable in this Chrome build');
  await scripting.registerContentScripts(registration.registeredScripts as unknown[]);
  const policy = await contentScriptPolicySummary(manifest);
  await appendTrace('content_scripts.experiment_set', {
    experimentId,
    scriptIds: registration.scriptIds,
    widenedMatchPatterns: registration.widenedMatchPatterns,
    invalidMatchPatterns: registration.invalidMatchPatterns,
    activeExperiment: policy.activeExperiment?.id ?? null,
  });
  return { policy, registration };
}

function frameContextKey(details: { documentId?: string; frameId?: number }): string | null {
  if (details.documentId) return `doc:${details.documentId}`;
  if (typeof details.frameId === 'number') return `frame:${details.frameId}`;
  return null;
}

async function frameContextIndexForTab(tabId: number): Promise<Map<string, Partial<ContentReceiverState>>> {
  const index = new Map<string, Partial<ContentReceiverState>>();
  let frames: chrome.webNavigation.GetAllFramesResultDetails[] | undefined;
  try {
    frames = await chrome.webNavigation.getAllFrames({ tabId });
  } catch (error) {
    await appendTrace('receivers.frame_context_failed', { tabId, error: errorMessage(error) }, 'warn');
    return index;
  }
  const byFrameId = new Map<number, chrome.webNavigation.GetAllFramesResultDetails>();
  for (const frame of frames || []) {
    if (typeof frame.frameId === 'number') byFrameId.set(frame.frameId, frame);
  }
  function lineage(frame: chrome.webNavigation.GetAllFramesResultDetails): chrome.webNavigation.GetAllFramesResultDetails[] {
    const seen = new Set<number>();
    const chain: chrome.webNavigation.GetAllFramesResultDetails[] = [];
    let current: chrome.webNavigation.GetAllFramesResultDetails | undefined = frame;
    while (current) {
      chain.push(current);
      if (typeof current.parentFrameId !== 'number' || current.parentFrameId < 0 || seen.has(current.parentFrameId)) break;
      seen.add(current.frameId);
      current = byFrameId.get(current.parentFrameId);
    }
    return chain.reverse();
  }
  for (const frame of frames || []) {
    const key = frameContextKey({ documentId: frame.documentId, frameId: frame.frameId });
    if (!key) continue;
    const chain = lineage(frame);
    const framePathFrameIds = chain.map((entry) => entry.frameId).filter((value): value is number => typeof value === 'number');
    const framePathUrls = chain.map((entry) => entry.url).filter((value): value is string => typeof value === 'string' && value.length > 0);
    const framePathHosts = chain.map((entry) => hostnameFromUrl(entry.url) ?? (entry.frameId === 0 ? 'top-frame' : `frame:${entry.frameId}`));
    index.set(key, {
      documentId: frame.documentId,
      frameId: frame.frameId,
      documentLifecycle: frame.documentLifecycle,
      frameType: frame.frameType,
      parentFrameId: typeof frame.parentFrameId === 'number' ? frame.parentFrameId : undefined,
      parentDocumentId: frame.parentDocumentId,
      frameUrl: frame.url,
      frameOrigin: originFromUrl(frame.url),
      frameDepth: Math.max(0, chain.length - 1),
      framePathFrameIds,
      framePathUrls,
      framePathHosts,
      framePathLabel: framePathHosts.join(' → '),
    });
  }
  return index;
}

async function enrichReceiversWithFrameContext(tabId: number, receivers: ContentReceiverState[] = []): Promise<ContentReceiverState[]> {
  if (!receivers.length) return [];
  const frameIndex = await frameContextIndexForTab(tabId);
  if (!frameIndex.size) return receivers;
  return receivers.map((receiver) => {
    const key = frameContextKey(receiver);
    const context = key ? frameIndex.get(key) : undefined;
    return context ? { ...receiver, ...context } : receiver;
  });
}

function receiverKeysForFrames(frames: chrome.webNavigation.GetAllFramesResultDetails[] = []): string[] {
  return Array.from(new Set(frames.map((frame) => frameContextKey({ documentId: frame.documentId, frameId: frame.frameId })).filter((value): value is string => Boolean(value))));
}

async function setPrimedReceiverKeys(tabId: number, keys: string[]): Promise<string[]> {
  const normalizedTabId = String(tabId);
  const state = await getPrimedReceivers();
  const nextKeys = mergePrimedReceiverKeys([], keys);
  await chrome.storage.session.set({
    [SESSION_PRIMED_RECEIVERS_KEY]: {
      ...state,
      [normalizedTabId]: nextKeys,
    },
  });
  return nextKeys;
}

async function refreshSupportedTabReceiverContexts(tabId: number): Promise<void> {
  const existing = (await getSupportedTabs()).find((entry) => entry.tabId === tabId);
  if (!existing?.receivers?.length) return;
  const tab = await getTabById(tabId);
  if (!tab?.id || !isSupportedUrl(tab.url)) return;
  const frameIndex = await frameContextIndexForTab(tab.id);
  const reconciled = frameIndex.size
    ? reconcileContentReceivers(existing.receivers || [], Array.from(frameIndex.values()))
    : { receivers: existing.receivers || [], removed: [], removedKeys: [], retainedKeys: [] };
  if (reconciled.removedKeys.length) {
    await appendTrace('receivers.reconciled', { tabId: tab.id, removedKeys: reconciled.removedKeys, retainedKeys: reconciled.retainedKeys });
  }
  const supportedTabs = await rememberSupportedTab({
    ...existing,
    tabId: tab.id,
    windowId: tab.windowId,
    url: tab.url,
    title: tab.title,
    discarded: tab.discarded ?? existing.discarded,
    frozen: tab.frozen ?? existing.frozen,
    receivers: reconciled.receivers,
    lastSeenAt: new Date().toISOString(),
  });
  const state = await getBridgeState();
  await patchBridgeState({
    supportedTabs,
    targetTab: state.selectedTargetTabId === tab.id
      ? (supportedTabs.find((entry) => entry.tabId === tab.id) ?? state.targetTab)
      : state.targetTab,
  });
}

async function primeSupportedSubframeReceivers(tab: chrome.tabs.Tab | undefined, knownState?: SupportedTabState): Promise<void> {
  if (!tab?.id || !isSupportedUrl(tab.url)) return;
  if (tab.discarded || knownState?.discarded) return;
  if (tab.frozen || knownState?.frozen) return;

  let frames: chrome.webNavigation.GetAllFramesResultDetails[] | undefined;
  try {
    frames = await chrome.webNavigation.getAllFrames({ tabId: tab.id });
  } catch (error) {
    await appendTrace('receivers.prime_inventory_failed', { tabId: tab.id, error: errorMessage(error) }, 'warn');
    return;
  }

  const state = knownState ?? (await getSupportedTabs()).find((entry) => entry.tabId === tab.id);
  const liveReceiverKeys = new Set(receiverKeysForFrames(frames || []));
  const primedKeysBefore = await primedReceiverKeysForTab(tab.id);
  const primedKeys = liveReceiverKeys.size
    ? primedKeysBefore.filter((key) => liveReceiverKeys.has(key))
    : primedKeysBefore;
  if (primedKeys.length !== primedKeysBefore.length) {
    await setPrimedReceiverKeys(tab.id, primedKeys);
    await appendTrace('receivers.primed_keys_reconciled', { tabId: tab.id, removedKeys: primedKeysBefore.filter((key) => !liveReceiverKeys.has(key)), retainedKeyCount: primedKeys.length });
  }
  const observedReceivers = liveReceiverKeys.size
    ? (state?.receivers || []).filter((receiver) => {
        const key = contentReceiverKey(receiver);
        return !key || liveReceiverKeys.has(key);
      })
    : (state?.receivers || []);
  const plan = planReceiverPriming(frames || [], {
    existingReceivers: observedReceivers,
    primedKeys,
    isSupportedUrl,
  });
  if (!plan.candidates.length) return;

  await appendTrace('receivers.prime_planned', {
    tabId: tab.id,
    candidateCount: plan.candidates.length,
    documentIdCount: plan.documentIds.length,
    frameIdCount: plan.frameIds.length,
    candidateKeys: plan.candidateKeys,
  });

  if (plan.documentIds.length) {
    try {
      await chrome.scripting.executeScript({
        target: { tabId: tab.id, documentIds: plan.documentIds },
        files: ['dist/content/main.js'],
      });
      await rememberPrimedReceiverKeys(tab.id, plan.candidates.filter((candidate) => candidate.documentId).map((candidate) => candidate.key));
      await appendTrace('receivers.prime_succeeded', { tabId: tab.id, mode: 'documentIds', documentIds: plan.documentIds });
    } catch (error) {
      await appendTrace('receivers.prime_failed', { tabId: tab.id, mode: 'documentIds', documentIds: plan.documentIds, error: errorMessage(error) }, 'warn');
    }
  }

  if (plan.frameIds.length) {
    try {
      await chrome.scripting.executeScript({
        target: { tabId: tab.id, frameIds: plan.frameIds },
        files: ['dist/content/main.js'],
      });
      await rememberPrimedReceiverKeys(tab.id, plan.candidates.filter((candidate) => !candidate.documentId).map((candidate) => candidate.key));
      await appendTrace('receivers.prime_succeeded', { tabId: tab.id, mode: 'frameIds', frameIds: plan.frameIds });
    } catch (error) {
      await appendTrace('receivers.prime_failed', { tabId: tab.id, mode: 'frameIds', frameIds: plan.frameIds, error: errorMessage(error) }, 'warn');
    }
  }
}

function reconnectDelayMinutes(attempt: number): number {
  const boundedAttempt = Math.max(1, attempt);
  return Math.min(NATIVE_RECONNECT_MAX_MINUTES, NATIVE_RECONNECT_MINUTES * 2 ** (boundedAttempt - 1));
}

function defaultNativeConnectionState(): NativeConnectionState {
  return {
    connected: false,
    reconnectAttempt: 0,
    reconnectScheduledFor: null,
    reconnectDelayMinutes: null,
  };
}

function defaultRuntimeLaneState(): RuntimeLaneState {
  return {
    currentBootId: WORKER_BOOT_ID,
    currentBootAt: WORKER_BOOT_AT,
    bootCount: 0,
    lastBootstrapAt: WORKER_BOOT_AT,
  };
}

function offscreenDocumentUrl(): string {
  return chrome.runtime.getURL(OFFSCREEN_DOCUMENT_PATH);
}

async function offscreenContexts(): Promise<chrome.runtime.ExtensionContext[]> {
  if (typeof chrome.runtime.getContexts !== 'function') return [];
  return chrome.runtime.getContexts({
    contextTypes: ['OFFSCREEN_DOCUMENT'],
    documentUrls: [offscreenDocumentUrl()],
  });
}

async function pingOffscreenDocument(timeoutMs = 1500): Promise<{ ok: boolean; payload?: OffscreenReadyPayload; error?: string }> {
  const deadline = Date.now() + timeoutMs;
  let lastError: string | undefined;
  while (Date.now() < deadline) {
    try {
      const response = await chrome.runtime.sendMessage(makeEnvelope('offscreen.document_ping', { probeAt: new Date().toISOString() })) as Envelope<OffscreenReadyPayload>;
      if (response?.type === 'offscreen.document_pong' && response.payload) {
        return { ok: true, payload: response.payload };
      }
      lastError = `unexpected offscreen ping response: ${String(response?.type ?? 'missing')}`;
    } catch (error) {
      lastError = errorMessage(error);
    }
    await sleep(100);
  }
  return { ok: false, error: lastError ?? 'offscreen ping timed out' };
}

async function requestOffscreenDomSummary(
  html: string,
  selectors: string[],
  maxCandidates: number,
  baseUrl?: string,
  timeoutMs = 2500,
): Promise<{ ok: boolean; summary?: OffscreenDomSummary; error?: string }> {
  const deadline = Date.now() + timeoutMs;
  let lastError: string | undefined;
  while (Date.now() < deadline) {
    try {
      const response = await chrome.runtime.sendMessage(
        makeEnvelope('offscreen.document_parse_html', {
          html,
          selectors,
          max_candidates: maxCandidates,
          ...(baseUrl ? { base_url: baseUrl } : {}),
        }),
      ) as Envelope<{ ok?: boolean; summary?: OffscreenDomSummary; error?: string }>;
      if (response?.type === 'offscreen.document_parse_html_result' && response.payload?.ok && response.payload.summary) {
        return { ok: true, summary: response.payload.summary };
      }
      if (response?.payload?.error) {
        lastError = String(response.payload.error);
      } else {
        lastError = `unexpected offscreen parse response: ${String(response?.type ?? 'missing')}`;
      }
    } catch (error) {
      lastError = errorMessage(error);
    }
    await sleep(100);
  }
  return { ok: false, error: lastError ?? 'offscreen DOM parse timed out' };
}

async function requestOffscreenFixtureCapture(
  html: string,
  selectors: string[],
  maxCandidates: number,
  baseUrl?: string,
  timeoutMs = 2500,
): Promise<{ ok: boolean; summary?: OffscreenDomSummary; fixture?: OffscreenFixtureCapture; error?: string }> {
  const deadline = Date.now() + timeoutMs;
  let lastError: string | undefined;
  while (Date.now() < deadline) {
    try {
      const response = await chrome.runtime.sendMessage(
        makeEnvelope('offscreen.document_capture_fixture', {
          html,
          selectors,
          max_candidates: maxCandidates,
          ...(baseUrl ? { base_url: baseUrl } : {}),
        }),
      ) as Envelope<{ ok?: boolean; summary?: OffscreenDomSummary; fixture?: OffscreenFixtureCapture; error?: string }>;
      if (response?.type === 'offscreen.document_capture_fixture_result' && response.payload?.ok && response.payload.summary && response.payload.fixture) {
        return { ok: true, summary: response.payload.summary, fixture: response.payload.fixture };
      }
      if (response?.payload?.error) {
        lastError = String(response.payload.error);
      } else {
        lastError = `unexpected offscreen fixture response: ${String(response?.type ?? 'missing')}`;
      }
    } catch (error) {
      lastError = errorMessage(error);
    }
    await sleep(100);
  }
  return { ok: false, error: lastError ?? 'offscreen fixture capture timed out' };
}

async function ensureOffscreenDocument(
  requested: boolean,
  opts: { ping?: boolean; pingTimeoutMs?: number } = {},
): Promise<OffscreenState> {
  const url = offscreenDocumentUrl();
  const hasRuntimeGetContexts = typeof chrome.runtime.getContexts === 'function';
  const offscreenApi = (chrome as typeof chrome & { offscreen?: { createDocument?: (options: { url: string; reasons: chrome.offscreen.Reason[]; justification: string }) => Promise<void> } }).offscreen;
  const supported = Boolean(hasRuntimeGetContexts && typeof offscreenApi?.createDocument === 'function');
  const existing = supported ? await offscreenContexts() : [];
  const base: OffscreenState = {
    supported,
    requested,
    enabled: existing.length > 0,
    url,
    contextCount: existing.length,
    documentUrls: existing.map((context) => context.documentUrl).filter((value): value is string => typeof value === 'string'),
    runtimeGetContexts: hasRuntimeGetContexts,
    ...(supported ? {} : { lastError: hasRuntimeGetContexts ? 'offscreen API unavailable' : 'runtime.getContexts unavailable' }),
  };
  if (!requested || !supported) {
    if (opts.ping && base.enabled) {
      const ping = await pingOffscreenDocument(opts.pingTimeoutMs);
      return {
        ...base,
        responsive: ping.ok,
        lastReady: ping.payload,
        ...(ping.ok ? {} : { lastError: ping.error ?? base.lastError }),
      };
    }
    return base;
  }
  if (!existing.length) {
    if (creatingOffscreenDocument) {
      await creatingOffscreenDocument;
    } else {
      creatingOffscreenDocument = offscreenApi!.createDocument({
        url: OFFSCREEN_DOCUMENT_PATH,
        reasons: OFFSCREEN_REASONS,
        justification: OFFSCREEN_JUSTIFICATION,
      });
      try {
        await creatingOffscreenDocument;
        await appendTrace('offscreen.document_ensured', { url, reasons: OFFSCREEN_REASONS });
      } catch (error) {
        const failure = errorMessage(error);
        await appendTrace('offscreen.document_failed', { url, error: failure }, 'warn');
        return {
          supported,
          requested,
          enabled: false,
          url,
          contextCount: 0,
          documentUrls: [],
          runtimeGetContexts: hasRuntimeGetContexts,
          responsive: false,
          lastError: failure,
        };
      } finally {
        creatingOffscreenDocument = null;
      }
    }
  }
  const ensured = await offscreenContexts();
  const next: OffscreenState = {
    supported,
    requested,
    enabled: ensured.length > 0,
    url,
    contextCount: ensured.length,
    documentUrls: ensured.map((context) => context.documentUrl).filter((value): value is string => typeof value === 'string'),
    runtimeGetContexts: hasRuntimeGetContexts,
  };
  if (opts.ping && next.enabled) {
    const ping = await pingOffscreenDocument(opts.pingTimeoutMs);
    return {
      ...next,
      responsive: ping.ok,
      lastReady: ping.payload,
      ...(ping.ok ? {} : { lastError: ping.error }),
    };
  }
  return next;
}

async function patchRuntimeLane(patch: Partial<RuntimeLaneState>): Promise<BridgeState> {

  const state = await getBridgeState();
  const next: RuntimeLaneState = {
    ...defaultRuntimeLaneState(),
    ...(state.runtime ?? {}),
    ...patch,
  };
  return patchBridgeState({ runtime: next });
}

async function recordRuntimeBoot(): Promise<void> {
  const state = await getBridgeState();
  const previous = state.runtime ?? defaultRuntimeLaneState();
  const bootCount = Math.max(1, Number(previous.bootCount ?? 0) + 1);
  const runtime = { ...previous, currentBootId: WORKER_BOOT_ID, currentBootAt: WORKER_BOOT_AT, bootCount, lastBootstrapAt: WORKER_BOOT_AT };
  await patchBridgeState({ runtime });
  await updatePersistentBridgeHistory((current) => recordPersistentWorkerBoot(current, { bootId: runtime.currentBootId, bootAt: runtime.currentBootAt, bootCount: runtime.bootCount }));
  await appendTrace('runtime.worker_boot', { bootId: WORKER_BOOT_ID, bootAt: WORKER_BOOT_AT, bootCount });
}

async function recordRuntimeSignal(signal: 'startup' | 'installed' | 'suspend'): Promise<void> {
  const at = new Date().toISOString();
  if (signal === 'startup') {
    await patchRuntimeLane({ lastStartupSignalAt: at });
  } else if (signal === 'installed') {
    await patchRuntimeLane({ lastInstalledAt: at });
  } else {
    await patchRuntimeLane({ lastSuspendSignalAt: at });
  }
  await appendTrace(`runtime.${signal}_signal`, { at, bootId: WORKER_BOOT_ID });
}

async function patchNativeConnection(patch: Partial<NativeConnectionState>): Promise<BridgeState> {
  const state = await getBridgeState();
  const next: NativeConnectionState = {
    ...defaultNativeConnectionState(),
    ...(state.nativeConnection ?? {}),
    ...patch,
  };
  return patchBridgeState({ nativeConnection: next });
}

async function markNativeConnected(): Promise<void> {
  await chrome.alarms.clear(NATIVE_RECONNECT_ALARM).catch(console.error);
  await patchNativeConnection({
    connected: true,
    lastConnectedAt: new Date().toISOString(),
    reconnectAttempt: 0,
    reconnectScheduledFor: null,
    reconnectDelayMinutes: null,
    lastHealthError: undefined,
  });
}

async function markNativeDisconnected(reason: string): Promise<void> {
  await patchNativeConnection({
    connected: false,
    lastDisconnectedAt: new Date().toISOString(),
    lastDisconnectReason: reason,
    lastHealthOk: false,
    lastHealthError: reason,
  });
}

async function scheduleNativeReconnect(reason: string, attempt: number): Promise<void> {
  const delayInMinutes = reconnectDelayMinutes(attempt);
  const scheduledFor = new Date(Date.now() + delayInMinutes * 60_000).toISOString();
  await chrome.alarms.create(NATIVE_RECONNECT_ALARM, { delayInMinutes });
  await patchNativeConnection({
    connected: false,
    lastDisconnectReason: reason,
    reconnectAttempt: attempt,
    reconnectScheduledFor: scheduledFor,
    reconnectDelayMinutes: delayInMinutes,
  });
  await appendTrace('native.reconnect_scheduled', { reason, attempt, delayInMinutes, scheduledFor }, 'warn');
}

function clearPendingNativeHealth(reason: string): void {
  if (!pendingNativeHealth) return;
  clearTimeout(pendingNativeHealth.timeoutId);
  pendingNativeHealth = null;
  void appendTrace('native.health_cancelled', { reason }, 'warn').catch(console.error);
}

async function requestNativeHealth(trigger: string, timeoutMs = 1500): Promise<boolean> {
  if (!nativePort || pendingNativeHealth) return false;
  const requestId = `health-${Date.now()}`;
  const startedAt = Date.now();
  const healthRequest = makeEnvelope('health.ping', {
    requestId,
    trigger,
    sentAt: new Date(startedAt).toISOString(),
    broker_intent: 'owner_candidate',
  });
  const timeoutId = self.setTimeout(() => {
    if (!pendingNativeHealth || pendingNativeHealth.requestId !== requestId) return;
    pendingNativeHealth = null;
    void patchNativeConnection({
      lastHealthPingAt: new Date(startedAt).toISOString(),
      lastHealthRequestId: requestId,
      lastHealthTrigger: trigger,
      lastHealthOk: false,
      lastHealthError: `timeout after ${timeoutMs}ms`,
    }).catch(console.error);
    void appendTrace('native.health_timeout', { requestId, trigger, timeoutMs }, 'warn').catch(console.error);
  }, timeoutMs);
  pendingNativeHealth = { requestId, envelopeRequestId: healthRequest.request_id, startedAt, timeoutId };
  await patchNativeConnection({
    lastHealthPingAt: new Date(startedAt).toISOString(),
    lastHealthRequestId: requestId,
    lastHealthTrigger: trigger,
    lastHealthOk: false,
    lastHealthError: undefined,
  });
  await appendTrace('native.health_ping', { requestId, trigger }).catch(console.error);
  try {
    nativePort.postMessage(healthRequest);
    return true;
  } catch (error) {
    clearPendingNativeHealth('post_failed');
    await patchNativeConnection({
      lastHealthRequestId: requestId,
      lastHealthTrigger: trigger,
      lastHealthOk: false,
      lastHealthError: errorMessage(error),
    });
    await appendTrace('native.health_post_failed', { requestId, trigger, error: errorMessage(error) }, 'warn');
    return false;
  }
}



function nativeHostIdentityFromRecord(record: Record<string, unknown> | null | undefined): NativeHostIdentity | undefined {
  if (!record || typeof record !== 'object') return undefined;
  return {
    pid: typeof record.pid === 'number' ? record.pid : undefined,
    boot_id: typeof record.boot_id === 'string' ? record.boot_id : undefined,
    started_at: typeof record.started_at === 'string' ? record.started_at : undefined,
    message_count: typeof record.message_count === 'number' ? record.message_count : undefined,
    first_message_at: typeof record.first_message_at === 'string' ? record.first_message_at : undefined,
    first_message_type: typeof record.first_message_type === 'string' ? record.first_message_type : undefined,
    last_message_at: typeof record.last_message_at === 'string' ? record.last_message_at : undefined,
    last_message_type: typeof record.last_message_type === 'string' ? record.last_message_type : undefined,
  };
}

function nativeBrokerOwnerMetadataFromRecord(record: Record<string, unknown> | null | undefined): NativeBrokerOwnerMetadata | undefined {
  if (!record || typeof record !== 'object') return undefined;
  return {
    native_host: typeof record.native_host === 'string' ? record.native_host : undefined,
    socket_path: typeof record.socket_path === 'string' ? record.socket_path : undefined,
    lock_path: typeof record.lock_path === 'string' ? record.lock_path : undefined,
    metadata_path: typeof record.metadata_path === 'string' ? record.metadata_path : undefined,
    host_identity: nativeHostIdentityFromRecord(typeof record.host_identity === 'object' && record.host_identity ? record.host_identity as Record<string, unknown> : undefined),
  };
}

function nativeBrokerSummaryFromPayload(payload: Record<string, unknown> | null | undefined): NativeBrokerSummary | undefined {
  if (!payload || typeof payload !== 'object') return undefined;
  const broker = typeof payload.broker === 'object' && payload.broker
    ? payload.broker as Record<string, unknown>
    : payload;
  return {
    role: typeof broker.role === 'string' ? broker.role : undefined,
    lock_path: typeof broker.lock_path === 'string' ? broker.lock_path : undefined,
    metadata_path: typeof broker.metadata_path === 'string' ? broker.metadata_path : undefined,
    socket_path: typeof broker.socket_path === 'string' ? broker.socket_path : undefined,
    socket_exists: typeof broker.socket_exists === 'boolean' ? broker.socket_exists : undefined,
    connected_clients: typeof broker.connected_clients === 'number' || broker.connected_clients === null ? broker.connected_clients as number | null : undefined,
    owner_metadata: nativeBrokerOwnerMetadataFromRecord(typeof broker.owner_metadata === 'object' && broker.owner_metadata ? broker.owner_metadata as Record<string, unknown> : undefined),
  };
}

function nativeHostIdentitiesMatch(left: NativeHostIdentity | undefined, right: NativeHostIdentity | undefined): boolean | undefined {
  if (!left || !right) return undefined;
  if (!left.boot_id || !right.boot_id) return undefined;
  if (typeof left.pid !== 'number' || typeof right.pid !== 'number') return undefined;
  return left.boot_id === right.boot_id && left.pid === right.pid;
}

function nativeOverflowSummaryFromPayload(payload: Record<string, unknown> | null | undefined): NativeOverflowSummary | undefined {
  if (!payload || typeof payload !== 'object') return undefined;
  const overflow = typeof payload.last_oversized_host_message === 'object' && payload.last_oversized_host_message
    ? payload.last_oversized_host_message as Record<string, unknown>
    : payload;
  return {
    kind: typeof overflow.kind === 'string' ? overflow.kind : 'oversized-host-outbound',
    artifact_path: typeof overflow.artifact_path === 'string' ? overflow.artifact_path : undefined,
    original_type: typeof overflow.original_type === 'string' ? overflow.original_type : undefined,
    message_size_bytes: typeof overflow.message_size_bytes === 'number' ? overflow.message_size_bytes : undefined,
    limit_bytes: typeof overflow.limit_bytes === 'number' ? overflow.limit_bytes : undefined,
    captured_at: typeof overflow.captured_at === 'string' ? overflow.captured_at : undefined,
    request_id: typeof overflow.request_id === 'string' ? overflow.request_id : undefined,
    tab_id: typeof overflow.tab_id === 'number' ? overflow.tab_id : undefined,
    emitted_at: typeof overflow.emitted_at === 'string' ? overflow.emitted_at : undefined,
  };
}

function nativeOverflowInventoryDigestFromPayload(payload: Record<string, unknown> | null | undefined): NativeOverflowInventoryDigest | undefined {
  if (!payload || typeof payload !== 'object') return undefined;
  const inventory = typeof payload.overflow_inventory === 'object' && payload.overflow_inventory
    ? payload.overflow_inventory as Record<string, unknown>
    : payload;
  const recentArtifactsRaw = Array.isArray(inventory.recent_artifacts) ? inventory.recent_artifacts : [];
  return {
    latest_path: typeof inventory.latest_path === 'string' ? inventory.latest_path : undefined,
    latest_exists: typeof inventory.latest_exists === 'boolean' ? inventory.latest_exists : undefined,
    artifact_count: typeof inventory.artifact_count === 'number' ? inventory.artifact_count : undefined,
    total_disk_bytes: typeof inventory.total_disk_bytes === 'number' ? inventory.total_disk_bytes : undefined,
    total_reported_message_bytes: typeof inventory.total_reported_message_bytes === 'number' ? inventory.total_reported_message_bytes : undefined,
    message_type_counts: typeof inventory.message_type_counts === 'object' && inventory.message_type_counts ? inventory.message_type_counts as Record<string, number> : undefined,
    newest_captured_at: typeof inventory.newest_captured_at === 'string' ? inventory.newest_captured_at : undefined,
    oldest_captured_at: typeof inventory.oldest_captured_at === 'string' ? inventory.oldest_captured_at : undefined,
    latest_artifact_path: typeof inventory.latest_artifact_path === 'string' ? inventory.latest_artifact_path : undefined,
    latest_artifact_exists: typeof inventory.latest_artifact_exists === 'boolean' ? inventory.latest_artifact_exists : undefined,
    latest_artifact_in_inventory: typeof inventory.latest_artifact_in_inventory === 'boolean' ? inventory.latest_artifact_in_inventory : undefined,
    recent_limit: typeof inventory.recent_limit === 'number' ? inventory.recent_limit : undefined,
    recent_artifacts: recentArtifactsRaw.map((entry) => {
      const item = typeof entry === 'object' && entry ? entry as Record<string, unknown> : {};
      return {
        path: typeof item.path === 'string' ? item.path : undefined,
        name: typeof item.name === 'string' ? item.name : undefined,
        captured_at: typeof item.captured_at === 'string' ? item.captured_at : undefined,
        message_type: typeof item.message_type === 'string' ? item.message_type : undefined,
        request_id: typeof item.request_id === 'string' ? item.request_id : undefined,
        tab_id: typeof item.tab_id === 'number' ? item.tab_id : undefined,
        reported_size_bytes: typeof item.reported_size_bytes === 'number' ? item.reported_size_bytes : undefined,
        size_on_disk_bytes: typeof item.size_on_disk_bytes === 'number' ? item.size_on_disk_bytes : undefined,
        parse_ok: typeof item.parse_ok === 'boolean' ? item.parse_ok : undefined,
      };
    }),
  };
}

function nativeStatusSnapshotFromPayload(payload: Record<string, unknown> | null | undefined, trigger: string, capturedAt: string, persistentHostIdentity?: NativeHostIdentity): NativeStatusSnapshot {
  const hostIdentity = nativeHostIdentityFromRecord(typeof payload?.host_identity === 'object' && payload?.host_identity ? payload.host_identity as Record<string, unknown> : undefined);
  return {
    capturedAt,
    trigger,
    native_host: typeof payload?.native_host === 'string' ? payload.native_host : undefined,
    socket_path: typeof payload?.socket_path === 'string' ? payload.socket_path : undefined,
    state_root: typeof payload?.state_root === 'string' ? payload.state_root : undefined,
    events_path: typeof payload?.events_path === 'string' ? payload.events_path : undefined,
    event_count: typeof payload?.event_count === 'number' ? payload.event_count : undefined,
    latest_dir: typeof payload?.latest_dir === 'string' ? payload.latest_dir : undefined,
    fixtures_dir: typeof payload?.fixtures_dir === 'string' ? payload.fixtures_dir : undefined,
    run_dir: typeof payload?.run_dir === 'string' ? payload.run_dir : undefined,
    host_identity: hostIdentity,
    broker: nativeBrokerSummaryFromPayload(payload),
    matches_persistent_host: nativeHostIdentitiesMatch(hostIdentity, persistentHostIdentity),
    last_oversized_host_message: nativeOverflowSummaryFromPayload(payload),
    overflow_inventory: nativeOverflowInventoryDigestFromPayload(payload),
  };
}

function nativeStatusSnapshotIsStale(state: BridgeState, maxAgeMs = 15_000): boolean {
  const capturedAt = state.lastNativeStatusSnapshot?.capturedAt ? Date.parse(state.lastNativeStatusSnapshot.capturedAt) : Number.NaN;
  return !Number.isFinite(capturedAt) || (Date.now() - capturedAt) > maxAgeMs;
}

async function requestNativeStatusOneShot(trigger: string): Promise<NativeStatusSnapshot | undefined> {
  const requestId = `status-${Date.now()}`;
  const capturedAt = new Date().toISOString();
  await appendTrace('native.status_snapshot_requested', { requestId, trigger }).catch(console.error);
  try {
    const response = await chrome.runtime.sendNativeMessage(HOST_NAME, makeEnvelope('bridge.status', { requestId, trigger, sentAt: capturedAt, broker_intent: 'secondary_only' }));
    const payload = typeof response === 'object' && response && 'payload' in response
      ? ((response as { payload?: unknown }).payload as Record<string, unknown> | undefined)
      : undefined;
    const stateBeforePatch = await getBridgeState();
    const snapshot = nativeStatusSnapshotFromPayload(payload ?? null, trigger, capturedAt, stateBeforePatch.nativeConnection?.persistentHostIdentity);
    await patchBridgeState({
      lastNativeStatusSnapshot: snapshot,
      lastNativeStatusError: undefined,
      lastOversizedHostMessage: snapshot.last_oversized_host_message ?? stateBeforePatch.lastOversizedHostMessage,
    });
    await recordPersistentNativeEvent('native.oneshot_reachable', { trigger, at: capturedAt, nativeHost: snapshot.native_host, socketPath: snapshot.socket_path });
    await appendTrace('native.status_snapshot_result', {
      requestId,
      trigger,
      nativeHost: snapshot.native_host ?? null,
      brokerRole: snapshot.broker?.role ?? null,
      matchesPersistentHost: snapshot.matches_persistent_host ?? null,
      artifactCount: snapshot.overflow_inventory?.artifact_count ?? null,
    }).catch(console.error);
    return snapshot;
  } catch (error) {
    const failure = errorMessage(error);
    await patchBridgeState({ lastNativeStatusError: failure });
    await appendTrace('native.status_snapshot_failed', { requestId, trigger, error: failure }, 'warn').catch(console.error);
    return undefined;
  }
}

async function requestNativeHealthOneShot(trigger: string): Promise<boolean> {
  const requestId = `oneshot-${Date.now()}`;
  const startedAt = Date.now();
  const sentAt = new Date(startedAt).toISOString();
  await patchNativeConnection({
    lastOneShotProbeAt: sentAt,
    lastOneShotProbeRequestId: requestId,
    lastOneShotProbeTrigger: trigger,
    lastOneShotProbeOk: false,
    lastOneShotProbeError: undefined,
  });
  await appendTrace('native.oneshot_probe', { requestId, trigger }).catch(console.error);
  try {
    const response = await chrome.runtime.sendNativeMessage(HOST_NAME, makeEnvelope('health.ping', { requestId, trigger, sentAt, broker_intent: 'secondary_only' }));
    const payload = typeof response === 'object' && response && 'payload' in response
      ? ((response as { payload?: unknown }).payload as Record<string, unknown> | undefined)
      : undefined;
    const host = typeof payload?.native_host === 'string' ? payload.native_host : undefined;
    const socketPath = typeof payload?.socket_path === 'string' ? payload.socket_path : undefined;
    const hostIdentity = nativeHostIdentityFromRecord(typeof payload?.host_identity === 'object' && payload?.host_identity ? payload.host_identity as Record<string, unknown> : undefined);
    const broker = nativeBrokerSummaryFromPayload(payload ?? null);
    const ok = payload?.ok !== false;
    await patchNativeConnection({
      lastOneShotProbeAt: sentAt,
      lastOneShotProbeRequestId: requestId,
      lastOneShotProbeTrigger: trigger,
      lastOneShotProbeOk: ok,
      lastOneShotProbeError: ok ? undefined : 'native host response did not confirm ok=true',
      lastOneShotProbeRoundTripMs: Date.now() - startedAt,
      lastOneShotProbeHost: host,
      lastOneShotProbeSocketPath: socketPath,
      lastOneShotProbeHostIdentity: hostIdentity,
      lastOneShotProbeBroker: broker,
      nativeHost: host,
      socketPath,
    });
    await appendTrace('native.oneshot_probe_result', { requestId, trigger, ok, host: host ?? null, socketPath: socketPath ?? null, brokerRole: broker?.role ?? null }).catch(console.error);
    if (ok) {
      await recordPersistentNativeEvent('native.oneshot_reachable', { trigger, at: sentAt, nativeHost: host, socketPath });
    }
    return ok;
  } catch (error) {
    await patchNativeConnection({
      lastOneShotProbeAt: sentAt,
      lastOneShotProbeRequestId: requestId,
      lastOneShotProbeTrigger: trigger,
      lastOneShotProbeOk: false,
      lastOneShotProbeError: errorMessage(error),
      lastOneShotProbeRoundTripMs: Date.now() - startedAt,
    });
    await appendTrace('native.oneshot_probe_failed', { requestId, trigger, error: errorMessage(error) }, 'warn').catch(console.error);
    return false;
  }
}

async function resumeNativeConnectionLane(trigger: 'bootstrap' | 'startup' | 'installed'): Promise<void> {
  const state = await getBridgeState();
  const nativeConnection = state.nativeConnection ?? defaultNativeConnectionState();
  const scheduledFor = nativeConnection.reconnectScheduledFor ? Date.parse(nativeConnection.reconnectScheduledFor) : Number.NaN;
  const reconnectAlarm = await chrome.alarms.get(NATIVE_RECONNECT_ALARM).catch(() => undefined);
  if (nativeConnection.connected || !nativeConnection.reconnectScheduledFor) {
    await attemptNativeReconnect(trigger, `runtime.${trigger}`);
    return;
  }
  if (Number.isFinite(scheduledFor) && scheduledFor <= Date.now()) {
    await attemptNativeReconnect('alarm', `runtime.${trigger}.scheduled_due`);
    return;
  }
  if (reconnectAlarm) {
    await appendTrace('native.reconnect_alarm_preserved', { trigger, reconnectAlarm }, 'warn');
    return;
  }
  const minutesUntil = Number.isFinite(scheduledFor) ? Math.max(NATIVE_RECONNECT_MINUTES, (scheduledFor - Date.now()) / 60_000) : (nativeConnection.reconnectDelayMinutes ?? NATIVE_RECONNECT_MINUTES);
  await chrome.alarms.create(NATIVE_RECONNECT_ALARM, { delayInMinutes: minutesUntil });
  await appendTrace('native.reconnect_alarm_restored', { trigger, minutesUntil, scheduledFor: nativeConnection.reconnectScheduledFor }, 'warn');
}

async function hardenStorageAccess(): Promise<void> {
  try {
    await chrome.storage.local.setAccessLevel({ accessLevel: 'TRUSTED_CONTEXTS' });
    await chrome.storage.session.setAccessLevel({ accessLevel: 'TRUSTED_CONTEXTS' });
  } catch (error) {
    log('storage access hardening failed', error);
    await appendTrace('storage.hardening_failed', { error: errorMessage(error) }, 'warn');
    return;
  }
  await appendTrace('storage.hardened');
}

async function getPersistentBridgeHistory(): Promise<PersistentBridgeHistory> {
  const result = await chrome.storage.local.get(PERSISTENT_HISTORY_KEY);
  return normalizePersistentBridgeHistory(result[PERSISTENT_HISTORY_KEY]);
}

async function setPersistentBridgeHistory(next: PersistentBridgeHistory): Promise<PersistentBridgeHistory> {
  await chrome.storage.local.set({ [PERSISTENT_HISTORY_KEY]: next });
  return next;
}

async function updatePersistentBridgeHistory(mutator: (current: PersistentBridgeHistory) => PersistentBridgeHistory): Promise<PersistentBridgeHistory> {
  const current = await getPersistentBridgeHistory();
  return setPersistentBridgeHistory(mutator(current));
}

async function persistentDiagnosticsSnapshot(state?: BridgeState): Promise<PersistentBridgeHistory> {
  const resolved = state ?? await getBridgeState();
  const rawHistory = (await chrome.storage.local.get(PERSISTENT_HISTORY_KEY))[PERSISTENT_HISTORY_KEY];
  return buildPersistentDiagnosticsSnapshot(rawHistory, resolved.runtime ?? defaultRuntimeLaneState(), resolved.nativeConnection?.laneDiagnosis);
}

async function bridgeStateWithPersistentDiagnostics(state?: BridgeState): Promise<BridgeState> {
  const resolved = state ?? await getBridgeState();
  return { ...resolved, persistentDiagnostics: await persistentDiagnosticsSnapshot(resolved) };
}

function persistentEventHostIdentity(state: BridgeState): NativeHostIdentity | undefined {
  return state.nativeConnection?.persistentHostIdentity ?? state.nativeConnection?.lastOneShotProbeHostIdentity ?? state.lastNativeStatusSnapshot?.host_identity;
}

async function recordPersistentNativeEvent(kind: 'native.connected' | 'native.disconnected' | 'native.reconnect_succeeded' | 'native.reconnect_failed' | 'native.opportunistic_reconnect' | 'native.oneshot_reachable', extras: Partial<{ at: string; trigger: string; reason: string; nativeHost: string; socketPath: string }> = {}): Promise<void> {
  const state = await getBridgeState();
  const diagnosis = state.nativeConnection?.laneDiagnosis;
  const hostIdentity = persistentEventHostIdentity(state);
  const at = extras.at ?? new Date().toISOString();
  await updatePersistentBridgeHistory((current) => appendPersistentNativeEvent(current, {
    at,
    bootId: state.runtime?.currentBootId ?? WORKER_BOOT_ID,
    kind,
    ...(extras.trigger ? { trigger: extras.trigger } : {}),
    ...(extras.reason ? { reason: extras.reason } : {}),
    ...(diagnosis?.status ? { diagnosisStatus: diagnosis.status } : {}),
    ...(diagnosis?.summary ? { diagnosisSummary: diagnosis.summary } : {}),
    ...(state.nativeConnection?.persistentBroker?.role ? { persistentBrokerRole: state.nativeConnection.persistentBroker.role } : {}),
    ...(state.nativeConnection?.lastOneShotProbeBroker?.role ? { oneShotBrokerRole: state.nativeConnection.lastOneShotProbeBroker.role } : {}),
    ...(state.lastNativeStatusSnapshot?.broker?.role ? { snapshotBrokerRole: state.lastNativeStatusSnapshot.broker.role } : {}),
    ...((extras.nativeHost ?? state.nativeConnection?.nativeHost ?? state.lastNativeStatusSnapshot?.native_host) ? { nativeHost: extras.nativeHost ?? state.nativeConnection?.nativeHost ?? state.lastNativeStatusSnapshot?.native_host } : {}),
    ...((extras.socketPath ?? state.nativeConnection?.socketPath ?? state.lastNativeStatusSnapshot?.socket_path) ? { socketPath: extras.socketPath ?? state.nativeConnection?.socketPath ?? state.lastNativeStatusSnapshot?.socket_path } : {}),
    ...(hostIdentity?.boot_id ? { hostBootId: hostIdentity.boot_id } : {}),
    ...(typeof hostIdentity?.pid === 'number' ? { hostPid: hostIdentity.pid } : {}),
  }));
}

async function getSupportedTabs(): Promise<SupportedTabState[]> {
  const result = await chrome.storage.session.get(SESSION_TABS_KEY);
  return (result[SESSION_TABS_KEY] as SupportedTabState[] | undefined) ?? [];
}

async function setSupportedTabs(next: SupportedTabState[]): Promise<void> {
  await chrome.storage.session.set({ [SESSION_TABS_KEY]: next });
}

async function getPrimedReceivers(): Promise<Record<string, string[]>> {
  const result = await chrome.storage.session.get(SESSION_PRIMED_RECEIVERS_KEY);
  return (result[SESSION_PRIMED_RECEIVERS_KEY] as Record<string, string[]> | undefined) ?? {};
}

async function primedReceiverKeysForTab(tabId: number): Promise<string[]> {
  const state = await getPrimedReceivers();
  return Array.isArray(state[String(tabId)]) ? state[String(tabId)] : [];
}

async function rememberPrimedReceiverKeys(tabId: number, keys: string[]): Promise<string[]> {
  const normalizedTabId = String(tabId);
  const state = await getPrimedReceivers();
  const nextKeys = mergePrimedReceiverKeys(state[normalizedTabId] || [], keys);
  await chrome.storage.session.set({
    [SESSION_PRIMED_RECEIVERS_KEY]: {
      ...state,
      [normalizedTabId]: nextKeys,
    },
  });
  return nextKeys;
}

async function forgetPrimedReceiverKeys(tabId: number): Promise<void> {
  const normalizedTabId = String(tabId);
  const state = await getPrimedReceivers();
  if (!(normalizedTabId in state)) return;
  const next = { ...state };
  delete next[normalizedTabId];
  await chrome.storage.session.set({ [SESSION_PRIMED_RECEIVERS_KEY]: next });
}

async function getTraceEntries(): Promise<TraceEntry[]> {
  const result = await chrome.storage.session.get(TRACE_KEY);
  return (result[TRACE_KEY] as TraceEntry[] | undefined) ?? [];
}

async function appendTrace(kind: string, data?: unknown, level: TraceEntry['level'] = 'info'): Promise<TraceEntry[]> {
  const entry: TraceEntry = { at: new Date().toISOString(), kind, level, ...(data === undefined ? {} : { data }) };
  const next = [...(await getTraceEntries()), entry].slice(-TRACE_LIMIT);
  await chrome.storage.session.set({ [TRACE_KEY]: next });
  return next;
}

async function recentTrace(limit = 40): Promise<TraceEntry[]> {
  const entries = await getTraceEntries();
  return entries.slice(Math.max(0, entries.length - Math.max(1, limit)));
}

async function rememberSupportedTab(patch: SupportedTabState): Promise<SupportedTabState[]> {
  const existing = await getSupportedTabs();
  const current = existing.find((tab) => tab.tabId === patch.tabId);
  const merged = summarizeSupportedTabReceivers({
    ...(current || {}),
    ...patch,
    receivers: patch.receivers ?? current?.receivers,
    lastSeenAt: patch.lastSeenAt || current?.lastSeenAt || new Date().toISOString(),
  } as SupportedTabState);
  const without = existing.filter((tab) => tab.tabId !== patch.tabId);
  const next = [merged, ...without].slice(0, 12);
  await setSupportedTabs(next);
  return next;
}

function summarizeSupportedTabReceivers(tab: SupportedTabState): SupportedTabState {
  const summary = summarizeContentReceivers(tab.receivers || [], { overrideKey: tab.receiverOverrideKey });
  const preferred = preferredContentReceiver(tab.receivers || [], { overrideKey: tab.receiverOverrideKey });
  return {
    ...tab,
    ...(preferred?.documentId ? { documentId: preferred.documentId } : {}),
    ...(typeof preferred?.frameId === 'number' ? { frameId: preferred.frameId } : {}),
    ...(preferred?.documentLifecycle ? { documentLifecycle: preferred.documentLifecycle } : {}),
    ...(typeof preferred?.receiverReady === 'boolean' ? { receiverReady: preferred.receiverReady } : {}),
    receiverCount: summary.receiverCount,
    readyReceiverCount: summary.readyReceiverCount,
    receiverFrameIds: summary.receiverFrameIds,
    receiverDocumentIds: summary.receiverDocumentIds,
    receiverSelectionPolicy: summary.receiverSelectionPolicy,
    receiverInventoryStatus: summary.receiverInventoryStatus,
    receiverTopFrameReady: summary.receiverTopFrameReady,
    receiverOverrideStatus: summary.receiverOverrideStatus,
    selectedReceiverKey: summary.selectedReceiverKey,
    selectedReceiverLabel: summary.selectedReceiverLabel,
  };
}

async function receiverCoverageAuditForTab(tab: SupportedTabState | null | undefined, manifestPolicy?: ContentScriptPolicySummary): Promise<ReceiverCoverageAuditSummary | undefined> {
  if (!tab?.tabId) return undefined;
  let frames: chrome.webNavigation.GetAllFramesResultDetails[] | undefined;
  try {
    frames = await chrome.webNavigation.getAllFrames({ tabId: tab.tabId });
  } catch (error) {
    await appendTrace('receivers.coverage_inventory_failed', { tabId: tab.tabId, error: errorMessage(error) }, 'warn');
    return undefined;
  }
  const primingAudit = describeReceiverPrimingAudit(frames || [], {
    existingReceivers: tab.receivers || [],
    primedKeys: await primedReceiverKeysForTab(tab.tabId),
    isSupportedUrl,
  });
  const effectivePolicy = manifestPolicy ?? await contentScriptPolicySummary();
  return {
    frameCount: primingAudit.counts.frameCount,
    supportedUrlCount: primingAudit.counts.supportedUrlCount,
    relatedFrameUrlCount: primingAudit.counts.relatedFrameUrlCount,
    observedCount: primingAudit.counts.observedCount,
    primedCount: primingAudit.counts.primedCount,
    topFrameCount: primingAudit.counts.topFrameCount,
    candidateCount: primingAudit.counts.candidateCount,
    candidateDocumentCount: primingAudit.counts.candidateDocumentCount,
    candidateFrameCount: primingAudit.counts.candidateFrameCount,
    gapCount: primingAudit.counts.gapCount,
    skippedReasonCounts: primingAudit.counts.skippedReasonCounts,
    plan: primingAudit.plan,
    frames: primingAudit.frames,
    policyHints: { ...describeReceiverCoveragePolicyHints(primingAudit, effectivePolicy), manifestPolicy: effectivePolicy },
    experimentPlan: describeReceiverCoverageExperimentPlan(primingAudit, effectivePolicy),
  };
}

async function receiverAuditForTab(tab: SupportedTabState | null | undefined, state?: BridgeState, manifestPolicy?: ContentScriptPolicySummary): Promise<ReceiverAuditSummary | undefined> {
  if (!tab) return undefined;
  const summarized = summarizeSupportedTabReceivers(tab);
  const resolverAudit = describeContentReceiverAudit(summarized.receivers || [], { overrideKey: summarized.receiverOverrideKey });
  const coverageAudit = await receiverCoverageAuditForTab(summarized, manifestPolicy);
  return {
    targetTabId: summarized.tabId,
    targetTabTitle: summarized.title,
    targetTabUrl: summarized.url,
    selectedTargetTabId: state?.selectedTargetTabId ?? null,
    receiverCount: summarized.receiverCount ?? 0,
    readyReceiverCount: summarized.readyReceiverCount ?? 0,
    receiverSelectionPolicy: summarized.receiverSelectionPolicy ?? 'none',
    receiverInventoryStatus: summarized.receiverInventoryStatus ?? 'none',
    receiverOverrideKey: summarized.receiverOverrideKey ?? null,
    receiverOverrideStatus: summarized.receiverOverrideStatus ?? 'none',
    selectedReceiverKey: summarized.selectedReceiverKey,
    selectedReceiverLabel: summarized.selectedReceiverLabel,
    resolverPolicy: resolverAudit.resolverPolicy,
    receiverResolution: resolverAudit.receiverResolution,
    rankedMatches: resolverAudit.rankedMatches,
    coverageAudit,
    receivers: (summarized.receivers || []).map((receiver) => ({
      key: contentReceiverKey(receiver),
      label: contentReceiverLabel(receiver),
      frameId: receiver.frameId,
      documentId: receiver.documentId,
      adapter: receiver.adapter,
      documentLifecycle: receiver.documentLifecycle,
      frameType: receiver.frameType,
      parentFrameId: receiver.parentFrameId,
      parentDocumentId: receiver.parentDocumentId,
      frameUrl: receiver.frameUrl,
      frameOrigin: receiver.frameOrigin,
      frameDepth: receiver.frameDepth,
      framePathFrameIds: receiver.framePathFrameIds,
      framePathHosts: receiver.framePathHosts,
      framePathLabel: receiver.framePathLabel,
      receiverReady: receiver.receiverReady,
      lastSeenAt: receiver.lastSeenAt,
    })),
  };
}

function receiverAuditTarget(state: BridgeState): SupportedTabState | undefined {
  const selectedId = state.selectedTargetTabId;
  if (typeof selectedId === 'number') {
    const selected = state.supportedTabs?.find((tab) => tab.tabId === selectedId);
    if (selected) return selected;
  }
  if (state.targetTab) return state.targetTab;
  if ((state.supportedTabs?.length ?? 0) === 1) return state.supportedTabs?.[0];
  return undefined;
}

async function forgetSupportedTab(tabId: number): Promise<SupportedTabState[]> {
  const next = (await getSupportedTabs()).filter((tab) => tab.tabId !== tabId);
  await setSupportedTabs(next);
  const state = await getBridgeState();
  if (state.selectedTargetTabId === tabId) {
    await patchBridgeState({ selectedTargetTabId: null, targetTab: null });
  }
  return next;
}

async function getBridgeState(): Promise<BridgeState> {
  const result = await chrome.storage.session.get(STORAGE_KEY);
  return (result[STORAGE_KEY] as BridgeState | undefined) ?? {
    adapters: adapterDescriptors(),
    selectedTargetTabId: null,
    nativeConnection: defaultNativeConnectionState(),
    runtime: defaultRuntimeLaneState(),
  };
}

async function patchBridgeState(patch: Partial<BridgeState>): Promise<BridgeState> {
  const next = {
    ...(await getBridgeState()),
    adapters: adapterDescriptors(),
    ...patch,
    updatedAt: new Date().toISOString(),
  } satisfies BridgeState;
  const resolvedNativeConnection: NativeConnectionState = {
    ...defaultNativeConnectionState(),
    ...(next.nativeConnection ?? {}),
  };
  const nextWithDiagnosis = {
    ...next,
    nativeConnection: {
      ...resolvedNativeConnection,
      laneDiagnosis: deriveNativeLaneDiagnosis({
        nativeConnection: resolvedNativeConnection,
        lastNativeStatusSnapshot: next.lastNativeStatusSnapshot,
        lastNativeStatusError: next.lastNativeStatusError,
      }),
    },
  } satisfies BridgeState;
  await chrome.storage.session.set({ [STORAGE_KEY]: nextWithDiagnosis });
  return nextWithDiagnosis;
}

async function attemptNativeReconnect(trigger: 'bootstrap' | 'startup' | 'installed' | 'disconnect' | 'alarm' | 'status' | 'probe', reason: string): Promise<boolean> {
  try {
    ensureNativePort();
    await appendTrace(`native.reconnect_${trigger}_succeeded`, { reason });
    await recordPersistentNativeEvent('native.reconnect_succeeded', { trigger, reason });
    return true;
  } catch (error) {
    const nextAttempt = ((await getBridgeState()).nativeConnection?.reconnectAttempt ?? 0) + 1;
    const failureReason = errorMessage(error);
    await appendTrace(`native.reconnect_${trigger}_failed`, { reason, error: failureReason, attempt: nextAttempt }, 'warn');
    await scheduleNativeReconnect(reason, nextAttempt);
    await recordPersistentNativeEvent('native.reconnect_failed', { trigger, reason: failureReason });
    return false;
  }
}

function messageTargetOptions(tab: chrome.tabs.Tab, state?: SupportedTabState): chrome.tabs.SendMessageOptions | undefined {
  if (!tab.id) return undefined;
  const receiverTarget = messageTargetForReceivers(state?.receivers || [], { overrideKey: state?.receiverOverrideKey });
  if (receiverTarget?.documentId) return { documentId: receiverTarget.documentId };
  if (typeof receiverTarget?.frameId === 'number') return { frameId: receiverTarget.frameId };
  if (state?.documentId) {
    return { documentId: state.documentId };
  }
  if (typeof state?.frameId === 'number' && state.frameId >= 0) {
    return { frameId: state.frameId };
  }
  return undefined;
}

function isMissingReceiverError(error: unknown): boolean {
  const message = String(error ?? '');
  return message.includes('Receiving end does not exist') || message.includes('Could not establish connection');
}

async function syncActionForTab(tab: chrome.tabs.Tab | undefined, state: BridgeState): Promise<void> {
  if (!tab?.id) return;

  const tabId = tab.id;
  const supported = isSupportedUrl(tab.url);
  let text = '';
  let color = '#5b6475';
  let title = 'GlassTTY';

  if (!supported) {
    title = 'GlassTTY: unsupported tab';
  } else if (tab.discarded) {
    text = 'DISC';
    color = '#8b5a2b';
    title = 'GlassTTY: supported tab is discarded and must be activated before messaging';
  } else if (tab.frozen) {
    text = 'FRZ';
    color = '#6b46c1';
    title = 'GlassTTY: supported tab is frozen and may not process messages until activated';
  } else if (state.selectedTargetTabId === tabId) {
    text = 'TGT';
    color = '#1f6feb';
    title = 'GlassTTY: selected target tab';
  } else {
    text = 'OK';
    color = '#2f855a';
    title = 'GlassTTY: supported tab observed';
  }

  await chrome.action.setBadgeBackgroundColor({ tabId, color }).catch(console.error);
  await chrome.action.setBadgeText({ tabId, text }).catch(console.error);
  await chrome.action.setTitle({ tabId, title }).catch(console.error);
}

async function tryInjectContentScript(tab: chrome.tabs.Tab, state?: SupportedTabState): Promise<{ ok: boolean; reason?: string; injected?: boolean }> {
  if (!tab.id || !isSupportedUrl(tab.url)) return { ok: false, reason: 'unsupported tab' };
  if (tab.discarded || state?.discarded) return { ok: false, reason: 'tab is discarded' };
  if (tab.frozen || state?.frozen) return { ok: false, reason: 'tab is frozen' };

  const target: chrome.scripting.InjectionTarget = { tabId: tab.id };
  const preferred = preferredContentReceiver(state?.receivers || [], { overrideKey: state?.receiverOverrideKey });
  if (preferred?.documentId) {
    target.documentIds = [preferred.documentId];
  } else if (typeof preferred?.frameId === 'number' && preferred.frameId >= 0) {
    target.frameIds = [preferred.frameId];
  } else if (state?.documentId) {
    target.documentIds = [state.documentId];
  } else if (typeof state?.frameId === 'number' && state.frameId >= 0) {
    target.frameIds = [state.frameId];
  }
  try {
    await chrome.scripting.executeScript({ target, files: ['dist/content/main.js'] });
    await appendTrace('content.reinject_succeeded', { tabId: tab.id, documentIds: target.documentIds, frameIds: target.frameIds });
    return { ok: true, injected: true };
  } catch (error) {
    await appendTrace('content.reinject_failed', { tabId: tab.id, error: errorMessage(error), documentIds: target.documentIds, frameIds: target.frameIds }, 'warn');
    return { ok: false, reason: String(error) };
  }
}

async function selectedTargetTab(): Promise<chrome.tabs.Tab | undefined> {
  const state = await getBridgeState();
  if (!state.selectedTargetTabId) return undefined;
  const tab = await getTabById(state.selectedTargetTabId);
  if (tab?.id && isSupportedUrl(tab.url)) return tab;
  await patchBridgeState({ selectedTargetTabId: null, targetTab: null });
  return undefined;
}

async function setSelectedTargetTab(tabId: number | null, hint?: chrome.tabs.Tab): Promise<BridgeState> {
  if (!tabId) {
    return patchBridgeState({ selectedTargetTabId: null, targetTab: null });
  }
  const tab = hint?.id === tabId ? hint : await getTabById(tabId);
  if (!tab?.id || !isSupportedUrl(tab.url)) {
    throw new Error(`tab ${tabId} is not a supported GlassTTY tab`);
  }
  const supportedTabs = await rememberSupportedTab({
    tabId: tab.id,
    windowId: tab.windowId,
    url: tab.url,
    title: tab.title,
    lastSeenAt: new Date().toISOString(),
  });
  return patchBridgeState({
    supportedTabs,
    selectedTargetTabId: tab.id,
    targetTab: supportedTabs.find((entry) => entry.tabId === tab.id) ?? {
      tabId: tab.id,
      windowId: tab.windowId,
      url: tab.url,
      title: tab.title,
      lastSeenAt: new Date().toISOString(),
    },
  });
}

async function setReceiverOverride(tabId: number, receiverKey: string | null): Promise<BridgeState> {
  const supportedTabs = await getSupportedTabs();
  const current = supportedTabs.find((entry) => entry.tabId === tabId);
  if (!current) {
    throw new Error(`tab ${tabId} has no observed GlassTTY receiver inventory`);
  }
  const nextTabs = await rememberSupportedTab({
    ...current,
    receiverOverrideKey: receiverKey,
    lastSeenAt: new Date().toISOString(),
  });
  const state = await getBridgeState();
  return patchBridgeState({
    supportedTabs: nextTabs,
    targetTab: state.selectedTargetTabId === tabId ? (nextTabs.find((entry) => entry.tabId === tabId) ?? current) : state.targetTab,
  });
}

async function resolveTargetTab(): Promise<chrome.tabs.Tab | undefined> {
  const pinned = await selectedTargetTab();
  if (pinned?.id) return pinned;

  const active = await getActiveTab();
  if (active?.id && isSupportedUrl(active.url)) return active;

  const supported = await getSupportedTabs();
  for (const entry of supported) {
    const tab = await getTabById(entry.tabId);
    if (tab?.id && isSupportedUrl(tab.url)) return tab;
  }
  return undefined;
}

async function chooseTargetTab(request?: Envelope): Promise<chrome.tabs.Tab | undefined> {
  const explicit = await getTabById(request?.tab_id);
  if (explicit?.id && isSupportedUrl(explicit.url)) return explicit;
  return resolveTargetTab();
}

async function syncSidePanelForTab(tab?: chrome.tabs.Tab): Promise<void> {
  if (!tab?.id) return;
  const enabled = isSupportedUrl(tab.url);
  await chrome.sidePanel.setOptions({
    tabId: tab.id,
    path: 'sidepanel/index.html',
    enabled,
  }).catch(console.error);
}

async function refreshActiveTabState(): Promise<void> {
  const tab = await getActiveTab();
  await syncSidePanelForTab(tab);
  const supportedTabs = await getSupportedTabs();
  const state = await getBridgeState();
  const targetTab = await resolveTargetTab();
  const nextState = await patchBridgeState({
    activeTab: {
      id: tab?.id,
      url: tab?.url,
      windowId: tab?.windowId,
      supported: isSupportedUrl(tab?.url),
      discarded: tab?.discarded,
      frozen: tab?.frozen,
    },
    selectedTargetTabId: state.selectedTargetTabId ?? null,
    targetTab: targetTab?.id ? supportedTabs.find((entry) => entry.tabId === targetTab.id) ?? {
      tabId: targetTab.id,
      windowId: targetTab.windowId,
      url: targetTab.url,
      title: targetTab.title,
      discarded: targetTab.discarded,
      frozen: targetTab.frozen,
      lastSeenAt: new Date().toISOString(),
    } : null,
    supportedTabs,
  });
  await syncActionForTab(tab, nextState);
  if (targetTab?.id && targetTab.id !== tab?.id) {
    await syncActionForTab(targetTab, nextState);
  }
}

async function recordTabObservation(tab: chrome.tabs.Tab | undefined, details: Partial<SupportedTabState> = {}): Promise<void> {
  if (!tab?.id || !isSupportedUrl(tab.url)) return;
  const existing = (await getSupportedTabs()).find((entry) => entry.tabId === tab.id);
  const observedAt = new Date().toISOString();
  const shouldMergeReceiver = [details.documentId, details.frameId, details.documentLifecycle, details.adapter].some((value) => value !== undefined) || typeof details.receiverReady === 'boolean';
  const mergedReceivers = shouldMergeReceiver
    ? mergeContentReceivers(existing?.receivers || [], {
        documentId: details.documentId,
        frameId: details.frameId,
        documentLifecycle: details.documentLifecycle,
        adapter: details.adapter,
        receiverReady: details.receiverReady,
        lastSeenAt: observedAt,
      })
    : (existing?.receivers || []);
  const receivers = await enrichReceiversWithFrameContext(tab.id, mergedReceivers);
  const nextTab = summarizeSupportedTabReceivers({
    tabId: tab.id,
    windowId: tab.windowId,
    url: tab.url,
    title: tab.title,
    documentId: details.documentId ?? existing?.documentId,
    frameId: typeof details.frameId === 'number' ? details.frameId : existing?.frameId,
    documentLifecycle: details.documentLifecycle ?? existing?.documentLifecycle,
    discarded: details.discarded ?? tab.discarded ?? existing?.discarded,
    frozen: details.frozen ?? tab.frozen ?? existing?.frozen,
    receiverReady: details.receiverReady ?? existing?.receiverReady,
    adapter: details.adapter ?? existing?.adapter,
    receiverOverrideKey: details.receiverOverrideKey ?? existing?.receiverOverrideKey,
    receivers,
    lastSeenAt: observedAt,
  });
  const supportedTabs = await rememberSupportedTab(nextTab);
  await patchBridgeState({ supportedTabs });
}

async function recordSenderObservation(sender: chrome.runtime.MessageSender, message: Envelope): Promise<void> {
  const senderTab = sender.tab;
  if (!senderTab?.id || !isSupportedUrl(senderTab.url)) return;
  await recordTabObservation(senderTab, {
    adapter: message.type === 'adapter.detected' ? String((message.payload as { adapter?: string } | undefined)?.adapter ?? '') : undefined,
    documentId: sender.documentId,
    frameId: sender.frameId,
    documentLifecycle: sender.documentLifecycle,
    receiverReady: true,
  });
  const observed = (await getSupportedTabs()).find((entry) => entry.tabId === senderTab.id);
  await appendTrace('content.sender_observed', { tabId: senderTab.id, messageType: message.type, documentId: sender.documentId, frameId: sender.frameId, documentLifecycle: sender.documentLifecycle, receiverCount: observed?.receiverCount, receiverInventoryStatus: observed?.receiverInventoryStatus, receiverSelectionPolicy: observed?.receiverSelectionPolicy, receiverOverrideStatus: observed?.receiverOverrideStatus, selectedReceiverKey: observed?.selectedReceiverKey });
  await primeSupportedSubframeReceivers(senderTab, observed);
}

async function annotateResponseWithReceiver(request: Envelope, response: Envelope, tab: chrome.tabs.Tab, knownState?: SupportedTabState): Promise<Envelope> {
  const selected = preferredContentReceiver(knownState?.receivers || [], { overrideKey: knownState?.receiverOverrideKey });
  const resolverAudit = describeContentReceiverAudit(knownState?.receivers || [], { overrideKey: knownState?.receiverOverrideKey });
  const coverageAudit = await receiverCoverageAuditForTab(knownState, await contentScriptPolicySummary());
  const selectedKey = selected ? contentReceiverKey(selected) : undefined;
  if (request.type !== 'fixture.capture' || response.type !== 'fixture.capture') {
    return response;
  }
  const payload = typeof response.payload === 'object' && response.payload ? { ...(response.payload as Record<string, unknown>) } : {};
  const metadata = typeof payload.metadata === 'object' && payload.metadata ? { ...(payload.metadata as Record<string, unknown>) } : {};
  metadata.receiver_target_policy = knownState?.receiverSelectionPolicy ?? 'none';
  metadata.receiver_override_status = knownState?.receiverOverrideStatus ?? 'none';
  metadata.receiver_target_key = selectedKey ?? null;
  metadata.receiver_target_label = selected ? contentReceiverLabel(selected) : null;
  metadata.receiver_target_frame_id = typeof selected?.frameId === 'number' ? selected.frameId : null;
  metadata.receiver_target_document_id = selected?.documentId ?? null;
  metadata.receiver_target_frame_type = selected?.frameType ?? null;
  metadata.receiver_target_frame_url = selected?.frameUrl ?? null;
  metadata.receiver_target_frame_origin = selected?.frameOrigin ?? null;
  metadata.receiver_target_parent_frame_id = typeof selected?.parentFrameId === 'number' ? selected.parentFrameId : null;
  metadata.receiver_target_frame_depth = typeof selected?.frameDepth === 'number' ? selected.frameDepth : null;
  metadata.receiver_target_frame_path_frame_ids = Array.isArray(selected?.framePathFrameIds) ? selected?.framePathFrameIds : null;
  metadata.receiver_target_frame_path_hosts = Array.isArray(selected?.framePathHosts) ? selected?.framePathHosts : null;
  metadata.receiver_target_frame_path_label = selected?.framePathLabel ?? null;
  metadata.receiver_inventory_status = knownState?.receiverInventoryStatus ?? 'none';
  metadata.receiver_resolver_policy = resolverAudit.resolverPolicy;
  metadata.receiver_resolution = resolverAudit.receiverResolution ?? null;
  metadata.receiver_ranked_matches = resolverAudit.rankedMatches;
  metadata.receiver_coverage_audit = coverageAudit ?? null;
  metadata.receiver_coverage_policy_hints = coverageAudit?.policyHints ?? null;
  metadata.receiver_coverage_experiment_plan = coverageAudit?.experimentPlan ?? null;
  metadata.receiver_coverage_gaps = coverageAudit?.frames.filter((frame) => ['candidate_document', 'candidate_frame', 'related_frame_url', 'missing_target'].includes(frame.status)) ?? [];
  payload.metadata = metadata;
  return { ...response, payload } as Envelope;
}

async function sendToContentScript(tab: chrome.tabs.Tab, request: Envelope): Promise<Envelope> {
  const knownState = (await getSupportedTabs()).find((entry) => entry.tabId === tab.id);
  const payload = { ...request, tab_id: tab.id };
  const targetOptions = messageTargetOptions(tab, knownState);
  await appendTrace('content.send_attempt', { requestType: request.type, tabId: tab.id, documentId: knownState?.documentId, frameId: knownState?.frameId, receiverCount: knownState?.receiverCount, receiverSelectionPolicy: knownState?.receiverSelectionPolicy, receiverOverrideStatus: knownState?.receiverOverrideStatus, receiverOverrideKey: knownState?.receiverOverrideKey ?? null, selectedReceiverKey: knownState?.selectedReceiverKey ?? null, targetOptions: targetOptions ?? null, discarded: tab.discarded ?? false, frozen: tab.frozen ?? false });

  try {
    const response = await annotateResponseWithReceiver(request, await chrome.tabs.sendMessage(tab.id as number, payload, targetOptions) as Envelope, tab, knownState);
    await recordTabObservation(tab, { receiverReady: true });
    await patchBridgeState({
      lastContentMessage: response,
      activeTab: { id: tab.id, url: tab.url, windowId: tab.windowId, supported: true, discarded: tab.discarded, frozen: tab.frozen },
    });
    await appendTrace('content.send_succeeded', { requestType: request.type, tabId: tab.id, responseType: response.type, selectedReceiverKey: knownState?.selectedReceiverKey ?? null, receiverSelectionPolicy: knownState?.receiverSelectionPolicy, receiverOverrideStatus: knownState?.receiverOverrideStatus });
    return response;
  } catch (error) {
    if (isMissingReceiverError(error)) {
      await appendTrace('content.missing_receiver', { requestType: request.type, tabId: tab.id, error: errorMessage(error) }, 'warn');
      const reinjected = await tryInjectContentScript(tab, knownState);
      if (reinjected.ok) {
        try {
          const retried = await annotateResponseWithReceiver(request, await chrome.tabs.sendMessage(tab.id as number, payload, targetOptions) as Envelope, tab, knownState);
          await recordTabObservation(tab, { receiverReady: true, documentId: undefined, frameId: undefined, documentLifecycle: undefined });
          await patchBridgeState({
            lastContentMessage: retried,
            activeTab: { id: tab.id, url: tab.url, windowId: tab.windowId, supported: true, discarded: tab.discarded, frozen: tab.frozen },
          });
          await appendTrace('content.retry_succeeded', { requestType: request.type, tabId: tab.id, responseType: retried.type, receiverOverrideStatus: knownState?.receiverOverrideStatus, receiverOverrideKey: knownState?.receiverOverrideKey ?? null });
          return retried;
        } catch (retryError) {
          const failure = replyTo(request, 'error.report', {
            error: String(retryError),
            active_url: tab.url ?? null,
            recovery_attempted: true,
            injection_result: reinjected,
            tab_state: { discarded: tab.discarded ?? false, frozen: tab.frozen ?? false },
          }, tab.id);
          await recordTabObservation(tab, { receiverReady: false });
          await patchBridgeState({ lastError: failure });
          await appendTrace('content.retry_failed', { requestType: request.type, tabId: tab.id, error: errorMessage(retryError), injectionResult: reinjected }, 'warn');
          return failure;
        }
      }

      const failure = replyTo(request, 'error.report', {
        error: reinjected.reason ?? String(error),
        active_url: tab.url ?? null,
        recovery_attempted: true,
        injection_result: reinjected,
        tab_state: { discarded: tab.discarded ?? false, frozen: tab.frozen ?? false },
      }, tab.id);
      await recordTabObservation(tab, { receiverReady: false });
      await patchBridgeState({ lastError: failure });
      await appendTrace('content.recovery_unavailable', { requestType: request.type, tabId: tab.id, injectionResult: reinjected }, 'warn');
      return failure;
    }

    const failure = replyTo(request, 'error.report', {
      error: String(error),
      active_url: tab.url ?? null,
      tab_state: { discarded: tab.discarded ?? false, frozen: tab.frozen ?? false },
    }, tab.id);
    await recordTabObservation(tab, { receiverReady: false });
    await patchBridgeState({ lastError: failure });
    await appendTrace('content.send_failed', { requestType: request.type, tabId: tab.id, error: errorMessage(error) }, 'warn');
    return failure;
  }
}

async function sendToTargetContentScript(request: Envelope): Promise<Envelope> {
  const tab = await chooseTargetTab(request);
  if (!tab?.id || !isSupportedUrl(tab.url)) {
    const error = replyTo(request, 'error.report', {
      error: 'no supported target tab',
      active_url: (await getActiveTab())?.url ?? null,
      known_supported_tabs: await getSupportedTabs(),
    });
    await patchBridgeState({ lastError: error });
    return error;
  }
  return sendToContentScript(tab, request);
}

async function forwardResponseToNative(response: Envelope): Promise<void> {
  const port = ensureNativePort();
  port.postMessage(response);
  await patchBridgeState({ lastContentMessage: response });
  await appendTrace('native.forward_response', { responseType: response.type, tabId: response.tab_id });
}

async function mirrorResponseToNativeIfAvailable(response: Envelope): Promise<{ ok: boolean; error?: string }> {
  try {
    await forwardResponseToNative(response);
    return { ok: true };
  } catch (error) {
    const failure = errorMessage(error);
    await patchBridgeState({ lastContentMessage: response });
    await appendTrace('native.forward_response_skipped', { responseType: response.type, tabId: response.tab_id, error: failure }, 'warn');
    return { ok: false, error: failure };
  }
}

async function performAction(type: Envelope['type'], payload: unknown = {}, tabId?: number): Promise<Envelope> {
  const request = makeEnvelope(type, payload, tabId);
  const response = await sendToTargetContentScript(request);
  await mirrorResponseToNativeIfAvailable(response);
  return response;
}

async function openPanelForTab(tab?: chrome.tabs.Tab): Promise<void> {
  if (!tab?.id || !tab.windowId) return;
  await chrome.sidePanel.open({ tabId: tab.id, windowId: tab.windowId }).catch(console.error);
}

async function openPanelForBestTab(): Promise<void> {
  const tab = await resolveTargetTab();
  await openPanelForTab(tab);
}

async function extensionContextsSummary(): Promise<ExtensionContextSummary> {
  const runtimeVersion = chrome.runtime.getManifest().version;
  const hasRuntimeGetContexts = typeof chrome.runtime.getContexts === 'function';
  const openContexts = hasRuntimeGetContexts
    ? (await chrome.runtime.getContexts({})).map((context) => ({
        contextId: context.contextId,
        contextType: context.contextType,
        documentId: context.documentId,
        documentUrl: context.documentUrl,
        documentOrigin: context.documentOrigin,
        tabId: context.tabId,
        windowId: context.windowId,
        frameId: context.frameId,
        incognito: context.incognito,
      }))
    : [];
  return {
    runtimeId: chrome.runtime.id,
    runtimeVersion,
    hasRuntimeGetContexts,
    openContexts,
  };
}

function nativeDiagnosticsShowReachability(state: BridgeState): boolean {
  const nativeConnection = state.nativeConnection;
  if (nativeConnection?.connected) return false;
  if (nativeConnection?.lastOneShotProbeOk && !nativeConnection?.lastOneShotProbeError) return true;
  return Boolean(state.lastNativeStatusSnapshot && !state.lastNativeStatusError);
}

async function maybeReconnectNativeFromDiagnostics(trigger: 'bridge.status' | 'bridge.probe', waitForHealthMs = 0): Promise<boolean> {
  const state = await getBridgeState();
  if (!nativeDiagnosticsShowReachability(state)) return false;
  await appendTrace('native.opportunistic_reconnect', {
    trigger,
    diagnosis: state.nativeConnection?.laneDiagnosis?.status ?? null,
    lastOneShotProbeOk: state.nativeConnection?.lastOneShotProbeOk ?? null,
    snapshotCapturedAt: state.lastNativeStatusSnapshot?.capturedAt ?? null,
  }, 'warn');
  await recordPersistentNativeEvent('native.opportunistic_reconnect', { trigger });
  const reconnected = await attemptNativeReconnect(trigger === 'bridge.status' ? 'status' : 'probe', `explicit ${trigger} confirmed one-shot native-host reachability`);
  if (!reconnected || waitForHealthMs <= 0) return reconnected;
  const requestId = (await getBridgeState()).nativeConnection?.lastHealthRequestId;
  await waitForNativeHealthResult(requestId, waitForHealthMs + 150);
  return (await getBridgeState()).nativeConnection?.connected === true;
}

async function currentBridgeStatus(request: Envelope): Promise<Envelope> {
  await refreshActiveTabState();
  const state = await getBridgeState();
  const nativeConnection = state.nativeConnection;
  const lastHealthPongAt = nativeConnection?.lastHealthPongAt ? Date.parse(nativeConnection.lastHealthPongAt) : Number.NaN;
  const healthIsStale = !Number.isFinite(lastHealthPongAt) || (Date.now() - lastHealthPongAt) > 10_000;
  if (nativeConnection?.connected && healthIsStale) {
    const requested = await requestNativeHealth('bridge.status');
    if (requested) {
      const requestId = (await getBridgeState()).nativeConnection?.lastHealthRequestId;
      await waitForNativeHealthResult(requestId, 1650);
    }
  }
  if (nativeStatusSnapshotIsStale(state)) {
    await requestNativeStatusOneShot('bridge.status');
  }
  await maybeReconnectNativeFromDiagnostics('bridge.status', 1200);
  return replyTo(request, 'bridge.status', await bridgeStateWithPersistentDiagnostics());
}

async function waitForNativeHealthResult(requestId: string | undefined, timeoutMs: number): Promise<void> {
  const deadline = Date.now() + timeoutMs;
  while (Date.now() < deadline) {
    const nativeConnection = (await getBridgeState()).nativeConnection;
    const requestMatches = !requestId || nativeConnection?.lastHealthRequestId === requestId;
    const healthSettled = requestMatches && (nativeConnection?.lastHealthOk === true || typeof nativeConnection?.lastHealthError === 'string');
    if (healthSettled) return;
    await sleep(100);
  }
}

async function currentBridgeProbe(request: Envelope): Promise<Envelope<BridgeProbePayload>> {
  await refreshActiveTabState();
  const payload = (request.payload as { limit?: unknown; await_health_ms?: unknown; ensure_offscreen?: unknown } | undefined) ?? {};
  const limitValue = Number(payload.limit ?? 40);
  const limit = Number.isFinite(limitValue) ? Math.max(1, Math.min(200, Math.trunc(limitValue))) : 40;
  const awaitHealthValue = Number(payload.await_health_ms ?? 1500);
  const awaitHealthMs = Number.isFinite(awaitHealthValue) ? Math.max(0, Math.min(5000, Math.trunc(awaitHealthValue))) : 1500;
  const ensureOffscreenRequested = payload.ensure_offscreen === true || payload.ensure_offscreen === 1 || payload.ensure_offscreen === '1';
  const beforeHealth = (await getBridgeState()).nativeConnection;
  const shouldRefreshHealth = Boolean(beforeHealth?.connected && awaitHealthMs > 0);
  const lastOneShotAt = beforeHealth?.lastOneShotProbeAt ? Date.parse(beforeHealth.lastOneShotProbeAt) : Number.NaN;
  const oneShotIsStale = !Number.isFinite(lastOneShotAt) || (Date.now() - lastOneShotAt) > 10_000;
  const shouldRunOneShot = Boolean(!beforeHealth?.connected && awaitHealthMs > 0 && oneShotIsStale);
  if (shouldRefreshHealth) {
    const requested = await requestNativeHealth('bridge.probe', awaitHealthMs);
    if (requested) {
      const requestId = (await getBridgeState()).nativeConnection?.lastHealthRequestId;
      await waitForNativeHealthResult(requestId, awaitHealthMs + 150);
    }
  } else if (shouldRunOneShot) {
    await requestNativeHealthOneShot('bridge.probe');
  }
  const stateBeforeSnapshot = await getBridgeState();
  const nativeStatusSnapshot = nativeStatusSnapshotIsStale(stateBeforeSnapshot)
    ? await requestNativeStatusOneShot('bridge.probe')
    : stateBeforeSnapshot.lastNativeStatusSnapshot;
  await maybeReconnectNativeFromDiagnostics('bridge.probe', awaitHealthMs);
  const offscreen = await ensureOffscreenDocument(ensureOffscreenRequested, { ping: ensureOffscreenRequested });
  const session = await chrome.storage.session.get([STORAGE_KEY, TRACE_KEY, SESSION_TABS_KEY]);
  const manifest = chrome.runtime.getManifest();
  const effectiveContentScriptPolicy = await contentScriptPolicySummary(manifest);
  const status = await getBridgeState();
  return replyTo(request, 'bridge.probe', {
    probeAt: new Date().toISOString(),
    manifest: {
      version: manifest.version,
      minimumChromeVersion: manifest.minimum_chrome_version,
      permissions: manifest.permissions,
      hostPermissions: manifest.host_permissions,
      probeUrl: chrome.runtime.getURL('probe/index.html'),
      contentScriptPolicy: effectiveContentScriptPolicy,
    },
    status: await bridgeStateWithPersistentDiagnostics(status),
    receiverAudit: await receiverAuditForTab(receiverAuditTarget(status), status, effectiveContentScriptPolicy),
    contexts: await extensionContextsSummary(),
    offscreen,
    nativeStatusSnapshot,
    trace: { events: await recentTrace(limit) },
    sessionMirror: {
      bridgeState: session[STORAGE_KEY] as BridgeState | undefined,
      persistentDiagnostics: await persistentDiagnosticsSnapshot(status),
      bridgeTrace: session[TRACE_KEY] as TraceEntry[] | undefined,
      supportedTabs: session[SESSION_TABS_KEY] as SupportedTabState[] | undefined,
    },
  });
}

async function handleBackgroundRequest(request: Envelope): Promise<Envelope | null> {
  if (request.type === 'bridge.status') {
    return currentBridgeStatus(request);
  }
if (request.type === 'bridge.contexts') {
  const ensureOffscreenRequested = ((request.payload as { ensure_offscreen?: unknown } | undefined)?.ensure_offscreen) === true
    || ((request.payload as { ensure_offscreen?: unknown } | undefined)?.ensure_offscreen) === 1
    || ((request.payload as { ensure_offscreen?: unknown } | undefined)?.ensure_offscreen) === '1';
  if (ensureOffscreenRequested) {
    await ensureOffscreenDocument(true);
  }
  return replyTo(request, 'bridge.contexts', await extensionContextsSummary());
}
  if (request.type === 'bridge.trace') {
    const limitValue = Number((request.payload as { limit?: unknown } | undefined)?.limit ?? 40);
    const limit = Number.isFinite(limitValue) ? Math.max(1, Math.min(200, Math.trunc(limitValue))) : 40;
    return replyTo(request, 'bridge.trace', { events: await recentTrace(limit) });
  }
  if (request.type === 'bridge.probe') {
    return currentBridgeProbe(request);
  }
  if (request.type === 'bridge.content_script_experiment') {
    const status = await contentScriptExperimentStatus();
    return replyTo(request, 'bridge.content_script_experiment', {
      ok: true,
      policy: status.policy,
      dynamicScriptCount: status.dynamicScriptCount,
      activeExperiment: status.policy.activeExperiment ?? null,
    });
  }
  if (request.type === 'bridge.set_content_script_experiment') {
    const experimentId = compactString((request.payload as { experiment_id?: unknown } | undefined)?.experiment_id) as ContentScriptExperimentId | undefined;
    if (!experimentId || !['manifest_all_frames', 'manifest_match_about_blank', 'manifest_match_origin_as_fallback'].includes(experimentId)) {
      return replyTo(request, 'error.report', { error: 'bridge.set_content_script_experiment requires experiment_id: manifest_all_frames | manifest_match_about_blank | manifest_match_origin_as_fallback' });
    }
    const applied = await applyContentScriptExperiment(experimentId);
    await refreshActiveTabState();
    return replyTo(request, 'bridge.set_content_script_experiment', {
      ok: true,
      experimentId,
      policy: applied.policy,
      activeExperiment: applied.policy.activeExperiment ?? null,
      registration: applied.registration,
    });
  }
  if (request.type === 'bridge.clear_content_script_experiment') {
    const policy = await clearContentScriptExperimentRegistration({ traceReason: 'bridge.clear_content_script_experiment' });
    await refreshActiveTabState();
    return replyTo(request, 'bridge.clear_content_script_experiment', {
      ok: true,
      policy,
      activeExperiment: policy.activeExperiment ?? null,
    });
  }
  if (request.type === 'bridge.offscreen_dom') {
    const payload = (request.payload as { html?: unknown; selectors?: unknown; max_candidates?: unknown; base_url?: unknown } | undefined) ?? {};
    const html = typeof payload.html === 'string' ? payload.html : '';
    const selectors = Array.isArray(payload.selectors)
      ? payload.selectors.filter((value): value is string => typeof value === 'string' && value.trim().length > 0)
      : [];
    const requestedMax = Number(payload.max_candidates ?? 8);
    const maxCandidates = Number.isFinite(requestedMax) ? Math.max(1, Math.min(24, Math.trunc(requestedMax))) : 8;
    const baseUrl = typeof payload.base_url === 'string' && payload.base_url.trim().length > 0 ? payload.base_url.trim() : undefined;
    const offscreen = await ensureOffscreenDocument(true, { ping: true, pingTimeoutMs: 2000 });
    if (!offscreen.enabled) {
      return replyTo(request, 'error.report', { error: offscreen.lastError ?? 'offscreen document unavailable', offscreen });
    }
    const parsed = await requestOffscreenDomSummary(html, selectors, maxCandidates, baseUrl);
    if (!parsed.ok || !parsed.summary) {
      return replyTo(request, 'error.report', { error: parsed.error ?? 'offscreen DOM parse failed', offscreen });
    }
    return replyTo(request, 'bridge.offscreen_dom', {
      ok: true,
      offscreen: { ...offscreen, lastDomSummary: parsed.summary },
      summary: parsed.summary,
    });
  }
  if (request.type === 'bridge.offscreen_fixture') {
    const payload = (request.payload as { html?: unknown; selectors?: unknown; max_candidates?: unknown; base_url?: unknown } | undefined) ?? {};
    const html = typeof payload.html === 'string' ? payload.html : '';
    const selectors = Array.isArray(payload.selectors)
      ? payload.selectors.filter((value): value is string => typeof value === 'string' && value.trim().length > 0)
      : [];
    const requestedMax = Number(payload.max_candidates ?? 8);
    const maxCandidates = Number.isFinite(requestedMax) ? Math.max(1, Math.min(24, Math.trunc(requestedMax))) : 8;
    const baseUrl = typeof payload.base_url === 'string' && payload.base_url.trim().length > 0 ? payload.base_url.trim() : undefined;
    const offscreen = await ensureOffscreenDocument(true, { ping: true, pingTimeoutMs: 2000 });
    if (!offscreen.enabled) {
      return replyTo(request, 'error.report', { error: offscreen.lastError ?? 'offscreen document unavailable', offscreen });
    }
    const captured = await requestOffscreenFixtureCapture(html, selectors, maxCandidates, baseUrl);
    if (!captured.ok || !captured.summary || !captured.fixture) {
      return replyTo(request, 'error.report', { error: captured.error ?? 'offscreen fixture capture failed', offscreen });
    }
    return replyTo(request, 'bridge.offscreen_fixture', {
      ok: true,
      offscreen: { ...offscreen, lastDomSummary: captured.summary },
      summary: captured.summary,
      fixture: captured.fixture,
    });
  }
  if (request.type === 'bridge.set_target_tab') {
    const tabId = typeof (request.payload as { tab_id?: unknown } | undefined)?.tab_id === 'number'
      ? Number((request.payload as { tab_id?: number }).tab_id)
      : request.tab_id;
    if (!tabId) {
      return replyTo(request, 'error.report', { error: 'bridge.set_target_tab requires tab_id' });
    }
    await setSelectedTargetTab(tabId);
    await appendTrace('bridge.target_selected', { tabId });
    await refreshActiveTabState();
    return replyTo(request, 'bridge.set_target_tab', await getBridgeState(), tabId);
  }
  if (request.type === 'bridge.clear_target_tab') {
    await setSelectedTargetTab(null);
    await appendTrace('bridge.target_cleared');
    await refreshActiveTabState();
    return replyTo(request, 'bridge.clear_target_tab', await getBridgeState());
  }
  if (request.type === 'bridge.set_receiver_override') {
    const payload = (request.payload as { tab_id?: unknown; receiver_key?: unknown } | undefined) ?? {};
    const tabId = typeof payload.tab_id === 'number' ? Number(payload.tab_id) : request.tab_id;
    const receiverKey = typeof payload.receiver_key === 'string' && payload.receiver_key.trim().length > 0 ? payload.receiver_key.trim() : null;
    if (!tabId || !receiverKey) {
      return replyTo(request, 'error.report', { error: 'bridge.set_receiver_override requires tab_id and receiver_key' });
    }
    await setReceiverOverride(tabId, receiverKey);
    await appendTrace('bridge.receiver_override_set', { tabId, receiverKey });
    await refreshActiveTabState();
    return replyTo(request, 'bridge.set_receiver_override', await getBridgeState(), tabId);
  }
  if (request.type === 'bridge.clear_receiver_override') {
    const payload = (request.payload as { tab_id?: unknown } | undefined) ?? {};
    const tabId = typeof payload.tab_id === 'number' ? Number(payload.tab_id) : request.tab_id;
    if (!tabId) {
      return replyTo(request, 'error.report', { error: 'bridge.clear_receiver_override requires tab_id' });
    }
    await setReceiverOverride(tabId, null);
    await appendTrace('bridge.receiver_override_cleared', { tabId });
    await refreshActiveTabState();
    return replyTo(request, 'bridge.clear_receiver_override', await getBridgeState(), tabId);
  }
  return null;
}

function nativeOverflowSummaryFromMessage(message: Envelope): NativeOverflowSummary | undefined {
  if (message.type !== 'error.report') return undefined;
  const payload = typeof message.payload === 'object' && message.payload ? message.payload as Record<string, unknown> : null;
  if (!payload || payload.overflow !== true) return undefined;
  return {
    ...nativeOverflowSummaryFromPayload(payload),
    request_id: typeof message.request_id === 'string' ? message.request_id : undefined,
    tab_id: typeof message.tab_id === 'number' ? message.tab_id : undefined,
  };
}

async function handleNativeMessage(message: Envelope): Promise<void> {
  log('native message', message);

  if (message.type === 'bridge.forward_to_active_tab') {
    const forwarded = (message.payload as { request?: Envelope } | undefined)?.request;
    if (!forwarded) {
      const error = replyTo(message, 'error.report', { error: 'bridge.forward_to_active_tab missing payload.request' });
      ensureNativePort().postMessage(error);
      await patchBridgeState({ lastError: error });
      return;
    }
    const backgroundResponse = await handleBackgroundRequest(forwarded);
    const response = backgroundResponse ?? await sendToTargetContentScript(forwarded);
    await forwardResponseToNative(response);
    return;
  }

  if (message.type === 'health.ping') {
    const payload = (message.payload as {
      requestId?: unknown;
      trigger?: unknown;
      echo?: unknown;
      host?: unknown;
      native_host?: unknown;
      socket_path?: unknown;
      host_identity?: Record<string, unknown>;
      broker?: Record<string, unknown>;
    } | undefined) ?? {};
    const echo = typeof payload.echo === 'object' && payload.echo ? payload.echo as Record<string, unknown> : {};
    const echoedRequestId = typeof payload.requestId === 'string'
      ? payload.requestId
      : typeof echo.requestId === 'string' ? echo.requestId : undefined;
    const pending = pendingNativeHealth && (
      pendingNativeHealth.requestId === echoedRequestId
      || pendingNativeHealth.envelopeRequestId === message.request_id
    ) ? pendingNativeHealth : null;
    if (pendingNativeHealth && !pending) {
      await appendTrace('native.health_stale_pong', {
        responseRequestId: message.request_id,
        echoedRequestId: echoedRequestId ?? null,
        expectedRequestId: pendingNativeHealth.requestId,
        expectedEnvelopeRequestId: pendingNativeHealth.envelopeRequestId,
      }, 'warn').catch(console.error);
      return;
    }
    const requestId = echoedRequestId ?? pending?.requestId ?? message.request_id ?? 'unknown';
    const trigger = typeof payload.trigger === 'string'
      ? payload.trigger
      : typeof echo.trigger === 'string' ? echo.trigger : 'native.health';
    if (pending) {
      clearTimeout(pending.timeoutId);
      pendingNativeHealth = null;
    }
    const roundTripMs = pending ? Math.max(0, Date.now() - pending.startedAt) : undefined;
    const hostIdentity = nativeHostIdentityFromRecord(payload.host_identity ?? null);
    const broker = nativeBrokerSummaryFromPayload(payload.broker ?? null);
    const host = typeof payload.host === 'string'
      ? payload.host
      : typeof payload.native_host === 'string' ? payload.native_host : undefined;
    const stateBeforeHealthPatch = await getBridgeState();
    await patchNativeConnection({
      connected: true,
      lastHealthPongAt: new Date().toISOString(),
      lastHealthRoundTripMs: roundTripMs,
      lastHealthRequestId: requestId,
      lastHealthTrigger: trigger,
      lastHealthOk: true,
      lastHealthError: undefined,
      persistentHostIdentity: hostIdentity,
      persistentBroker: broker,
      nativeHost: host,
      socketPath: payload.socket_path ? String(payload.socket_path) : undefined,
    });
    await appendTrace('native.health_pong', { requestId, roundTripMs, trigger, host: host ?? null, socketPath: payload.socket_path ?? null, brokerRole: broker?.role ?? null, bootId: hostIdentity?.boot_id ?? null }).catch(console.error);
    if (!stateBeforeHealthPatch.nativeConnection?.connected || stateBeforeHealthPatch.nativeConnection?.lastHealthOk !== true) {
      await recordPersistentNativeEvent('native.connected', { trigger, reason: roundTripMs !== undefined ? `health pong ${roundTripMs}ms` : 'health pong' });
    }
    return;
  }

  if (message.type === 'bridge.status') {
    await patchBridgeState({ lastNativeMessage: message });
    return;
  }

  if (message.type === 'error.report') {
    const overflow = nativeOverflowSummaryFromMessage(message);
    await patchBridgeState({ lastError: message, lastOversizedHostMessage: overflow ?? undefined });
    if (overflow) {
      await appendTrace('native.host_outbound_overflow', overflow, 'warn').catch(console.error);
      return;
    }
    return;
  }

  log('unhandled native message type', message.type);
}

function ensureNativePort(): chrome.runtime.Port {
  if (nativePort) return nativePort;

  try {
    nativePort = chrome.runtime.connectNative(HOST_NAME);
  } catch (error) {
    void patchBridgeState({ lastError: errorMessage(error) }).catch(console.error);
    void appendTrace('native.connect_failed', { error: errorMessage(error) }, 'error').catch(console.error);
    throw error;
  }

  void appendTrace('native.connected').catch(console.error);
  void markNativeConnected().catch(console.error);
  void requestNativeHealth('native.connected').catch(console.error);
  nativePort.onMessage.addListener((msg) => {
    void patchBridgeState({ lastNativeMessage: msg }).catch(console.error);
    void appendTrace('native.message', { type: (msg as { type?: unknown } | undefined)?.type ?? null }).catch(console.error);
    log('native message', msg);
    void handleNativeMessage(msg as Envelope).catch(console.error);
  });
  nativePort.onDisconnect.addListener(() => {
    const reason = chrome.runtime.lastError?.message ?? 'native port disconnected';
    log('native port disconnected', reason);
    nativePort = null;
    void (async () => {
      clearPendingNativeHealth('native.disconnect');
      await patchBridgeState({ lastError: reason });
      await markNativeDisconnected(reason);
      await appendTrace('native.disconnected', { reason }, 'warn');
      await recordPersistentNativeEvent('native.disconnected', { trigger: 'disconnect', reason });
      await attemptNativeReconnect('disconnect', reason);
    })().catch(console.error);
  });
  return nativePort;
}

function installContextMenus(): void {
  chrome.contextMenus.removeAll(() => {
    chrome.contextMenus.create({
      id: MENU_OPEN_PANEL,
      title: 'Open GlassTTY side panel',
      contexts: ['page', 'selection'],
      documentUrlPatterns: MENU_PATTERNS,
    });
    chrome.contextMenus.create({
      id: MENU_SET_TARGET,
      title: 'Target this tab with GlassTTY',
      contexts: ['page', 'selection'],
      documentUrlPatterns: MENU_PATTERNS,
    });
    chrome.contextMenus.create({
      id: MENU_READ_LATEST,
      title: 'Read latest output into GlassTTY',
      contexts: ['page'],
      documentUrlPatterns: MENU_PATTERNS,
    });
    chrome.contextMenus.create({
      id: MENU_READ_PROMPT,
      title: 'Read prompt draft into GlassTTY',
      contexts: ['page'],
      documentUrlPatterns: MENU_PATTERNS,
    });
    chrome.contextMenus.create({
      id: MENU_CAPTURE_FIXTURE,
      title: 'Capture page fixture into GlassTTY',
      contexts: ['page'],
      documentUrlPatterns: MENU_PATTERNS,
    });
    chrome.contextMenus.create({
      id: MENU_WRITE_SELECTION,
      title: 'Write selected text into prompt draft',
      contexts: ['selection'],
      documentUrlPatterns: MENU_PATTERNS,
    });
  });
}

chrome.runtime.onInstalled.addListener(() => {
  if (!BUNDLE_VERSION_IS_CURRENT) return;
  void hardenStorageAccess();
  void chrome.sidePanel.setPanelBehavior({ openPanelOnActionClick: true }).catch(console.error);
  installContextMenus();
  void recordRuntimeSignal('installed').catch(console.error);
  void resumeNativeConnectionLane('installed');
  void refreshActiveTabState();
  void appendTrace('lifecycle.installed').catch(console.error);
  log('installed');
});

chrome.runtime.onStartup.addListener(() => {
  if (!BUNDLE_VERSION_IS_CURRENT) return;
  void hardenStorageAccess();
  installContextMenus();
  void recordRuntimeSignal('startup').catch(console.error);
  void resumeNativeConnectionLane('startup');
  void appendTrace('lifecycle.startup').catch(console.error);
  void refreshActiveTabState();
});

chrome.tabs.onActivated.addListener((info) => {
  if (!BUNDLE_VERSION_IS_CURRENT) return;
  void appendTrace('tabs.activated', { tabId: info.tabId, windowId: info.windowId }).catch(console.error);
  void refreshActiveTabState();
});

chrome.tabs.onUpdated.addListener(async (tabId, changeInfo, tab) => {
  if (!BUNDLE_VERSION_IS_CURRENT) return;
  if (changeInfo.url || changeInfo.status || typeof changeInfo.discarded === 'boolean' || typeof changeInfo.frozen === 'boolean') {
    await appendTrace('tabs.updated', { tabId, url: changeInfo.url ?? tab.url ?? null, status: changeInfo.status ?? tab.status ?? null, discarded: changeInfo.discarded ?? tab.discarded ?? null, frozen: changeInfo.frozen ?? tab.frozen ?? null });
  }
  await syncSidePanelForTab(tab);
  if (isSupportedUrl(tab.url)) {
    await recordTabObservation(tab);
    const observed = (await getSupportedTabs()).find((entry) => entry.tabId === tab.id);
    await primeSupportedSubframeReceivers(tab, observed);
  }
  await refreshActiveTabState();
});

chrome.tabs.onRemoved.addListener((tabId) => {
  if (!BUNDLE_VERSION_IS_CURRENT) return;
  void appendTrace('tabs.removed', { tabId }).catch(console.error);
  void forgetSupportedTab(tabId)
    .then((supportedTabs) => patchBridgeState({ supportedTabs }))
    .then(() => forgetPrimedReceiverKeys(tabId))
    .then(() => refreshActiveTabState())
    .catch(console.error);
});

for (const [eventName, listener] of [
  ['onCommitted', chrome.webNavigation.onCommitted],
  ['onHistoryStateUpdated', chrome.webNavigation.onHistoryStateUpdated],
  ['onReferenceFragmentUpdated', chrome.webNavigation.onReferenceFragmentUpdated],
] as const) {
  listener.addListener((details) => {
    if (!BUNDLE_VERSION_IS_CURRENT) return;
    void refreshSupportedTabReceiverContexts(details.tabId).catch(console.error);
    void (async () => {
      const tab = await getTabById(details.tabId);
      if (!tab?.id || !isSupportedUrl(tab.url)) return;
      const observed = (await getSupportedTabs()).find((entry) => entry.tabId === tab.id);
      await primeSupportedSubframeReceivers(tab, observed);
    })().catch(console.error);
    void appendTrace('receivers.frame_navigation', {
      event: eventName,
      tabId: details.tabId,
      frameId: details.frameId,
      documentId: details.documentId,
      documentLifecycle: details.documentLifecycle,
      parentFrameId: details.parentFrameId,
      frameType: details.frameType,
      url: details.url,
    }).catch(console.error);
  });
}

chrome.alarms.onAlarm.addListener((alarm) => {
  if (!BUNDLE_VERSION_IS_CURRENT) return;
  if (alarm.name !== NATIVE_RECONNECT_ALARM) return;
  void (async () => {
    await appendTrace('native.reconnect_alarm_fired', { scheduledTime: alarm.scheduledTime });
    const reason = (await getBridgeState()).nativeConnection?.lastDisconnectReason ?? 'native reconnect alarm';
    await attemptNativeReconnect('alarm', reason);
  })().catch(console.error);
});

chrome.contextMenus.onClicked.addListener((info, tab) => {
  if (!BUNDLE_VERSION_IS_CURRENT) return;
  if (!tab?.id || !isSupportedUrl(tab.url)) return;
  const tabId = tab.id as number;
  void (async () => {
    if (info.menuItemId === MENU_OPEN_PANEL) {
      await setSelectedTargetTab(tabId, tab);
      await openPanelForTab(tab);
      await refreshActiveTabState();
      return;
    }
    if (info.menuItemId === MENU_SET_TARGET) {
      await setSelectedTargetTab(tabId, tab);
      await openPanelForTab(tab);
      await refreshActiveTabState();
      return;
    }
    if (info.menuItemId === MENU_READ_LATEST) {
      await setSelectedTargetTab(tabId, tab);
      await performAction('transcript.latest', {}, tabId);
      return;
    }
    if (info.menuItemId === MENU_READ_PROMPT) {
      await setSelectedTargetTab(tabId, tab);
      await performAction('prompt.read', {}, tabId);
      return;
    }
    if (info.menuItemId === MENU_CAPTURE_FIXTURE) {
      await setSelectedTargetTab(tabId, tab);
      await performAction('fixture.capture', {}, tabId);
      return;
    }
    if (info.menuItemId === MENU_WRITE_SELECTION && info.selectionText) {
      await setSelectedTargetTab(tabId, tab);
      await performAction('prompt.write', { text: info.selectionText }, tabId);
      return;
    }
  })().catch(console.error);
});

chrome.commands.onCommand.addListener(async (command) => {
  if (!BUNDLE_VERSION_IS_CURRENT) return;
  void appendTrace('command.invoked', { command }).catch(console.error);
  if (command === 'pull-latest-output') {
    await performAction('transcript.latest');
  } else if (command === 'pull-current-prompt') {
    await performAction('prompt.read');
  } else if (command === 'debug-dom-candidates') {
    await performAction('debug.dom_candidates');
  } else if (command === 'open-glasstty-side-panel') {
    await openPanelForBestTab();
  }
});

chrome.runtime.onSuspend.addListener(() => {
  if (!BUNDLE_VERSION_IS_CURRENT) return;
  void recordRuntimeSignal('suspend').catch(console.error);
});

chrome.runtime.onMessage.addListener((message: Envelope, sender, sendResponse) => {
  if (!BUNDLE_VERSION_IS_CURRENT) {
    sendResponse(replyTo(message, 'error.report', {
      error: `stale GlassTTY worker bundle ${__GLASSTTY_BUNDLE_VERSION__}; manifest requires ${MANIFEST_VERSION}`,
    }));
    return false;
  }
  const fromExtensionPage = !sender.tab;
  const senderUrl = sender.url ?? sender.documentUrl;
  const fromOffscreenDocument = senderUrl === offscreenDocumentUrl();

  if (sender.tab) {
    void recordSenderObservation(sender, message).then(() => refreshActiveTabState()).catch(console.error);
  }

  if (fromOffscreenDocument && message.type === 'offscreen.document_ready') {
    void appendTrace('offscreen.document_ready', { url: senderUrl, payload: message.payload ?? null }).catch(console.error);
    sendResponse(replyTo(message, 'offscreen.document_ack', { ok: true, url: senderUrl }));
    return true;
  }

  if (fromExtensionPage && ['bridge.status', 'bridge.contexts', 'bridge.trace', 'bridge.probe', 'bridge.content_script_experiment', 'bridge.set_content_script_experiment', 'bridge.clear_content_script_experiment', 'bridge.offscreen_dom', 'bridge.offscreen_fixture', 'bridge.set_target_tab', 'bridge.clear_target_tab', 'bridge.set_receiver_override', 'bridge.clear_receiver_override'].includes(message.type)) {
    void handleBackgroundRequest(message)
      .then((response) => sendResponse(response ?? replyTo(message, 'error.report', { error: `no background handler for ${message.type}` })))
      .catch((error) => sendResponse(replyTo(message, 'error.report', { error: String(error) })));
    return true;
  }

  if (fromExtensionPage && ['prompt.read', 'prompt.write', 'prompt.submit', 'transcript.latest', 'selection.read', 'debug.dom_candidates', 'state.snapshot', 'fixture.capture'].includes(message.type)) {
    const tabId = typeof (message.payload as { tab_id?: unknown } | undefined)?.tab_id === 'number'
      ? ((message.payload as { tab_id?: number }).tab_id)
      : message.tab_id;
    const payload = typeof message.payload === 'object' && message.payload ? { ...(message.payload as Record<string, unknown>) } : {};
    delete (payload as { tab_id?: unknown }).tab_id;
    void performAction(message.type, payload, tabId)
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
  } catch (error) {
    sendResponse({ ok: false, error: String(error) });
  }
  return true;
});

void enforceCurrentBundle()
  .then((current) => {
    if (!current) return;
    void recordRuntimeBoot().catch(console.error);
    void hardenStorageAccess();
    void refreshActiveTabState();
    installContextMenus();
    void resumeNativeConnectionLane('bootstrap').catch(console.error);
  })
  .catch(console.error);
