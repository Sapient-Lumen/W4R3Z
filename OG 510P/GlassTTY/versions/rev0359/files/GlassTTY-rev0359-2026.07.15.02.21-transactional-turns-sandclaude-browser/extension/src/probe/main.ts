import { makeEnvelope, type Envelope } from '../shared/protocol';

const outputNode = document.getElementById('probe-json');
const summaryNode = document.getElementById('summary');
if (!outputNode || !summaryNode) throw new Error('probe page root missing');
const output = outputNode as HTMLPreElement;
const summary = summaryNode as HTMLSpanElement;

interface ReceiverCoverageExperiment {
  id: string;
  label: string;
  addressedFrameCount: number;
  remainingGapCount: number;
  incrementalGapReduction: number;
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

interface ProbeResponsePayload {
  probeAt: string;
  manifest: {
    version: string;
    minimumChromeVersion?: string;
    permissions?: string[];
    hostPermissions?: string[];
    probeUrl: string;
    contentScriptPolicy?: {
      staticContentScriptCount: number;
      dynamicContentScriptCount: number;
      matches: string[];
      allFrames: boolean;
      matchAboutBlank: boolean;
      matchOriginAsFallback: boolean;
      runAt: string[];
      activeExperiment?: {
        id: string;
        label: string;
        requiresNavigation: boolean;
      };
    };
  };
  receiverAudit?: {
    coverageAudit?: {
      gapCount: number;
      experimentPlan?: {
        currentExperimentId: string;
        recommendedExperimentId?: string;
        recommendedRationale?: string;
        experiments: ReceiverCoverageExperiment[];
      };
    };
  };
  status: {
    activeTab?: { id?: number; url?: string; supported: boolean };
    targetTab?: { tabId: number; url?: string; adapter?: string } | null;
    selectedTargetTabId?: number | null;
    supportedTabs?: Array<{ tabId: number; url?: string; adapter?: string; title?: string; receiverReady?: boolean }>;
    nativeConnection?: {
      connected: boolean;
      laneDiagnosis?: {
        status: string;
        summary: string;
        recommendedAction: string;
      };
      lastDisconnectReason?: string;
      lastHealthOk?: boolean;
      lastHealthError?: string;
      lastHealthRoundTripMs?: number;
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
    runtime?: {
      currentBootId: string;
      currentBootAt: string;
      bootCount: number;
      lastBootstrapAt: string;
      lastStartupSignalAt?: string;
      lastInstalledAt?: string;
      lastSuspendSignalAt?: string;
    };
    persistentDiagnostics?: {
      updatedAt?: string;
      runtimeHint?: { status: string; summary: string; recommendedAction: string };
      workerBoots?: Array<Record<string, unknown>>;
      nativeEvents?: Array<Record<string, unknown>>;
    };
  };
  contexts: {
    runtimeId: string;
    runtimeVersion: string;
    hasRuntimeGetContexts: boolean;
    openContexts: Array<Record<string, unknown>>;
  };
  offscreen?: {
    supported: boolean;
    requested: boolean;
    enabled: boolean;
    url: string;
    contextCount: number;
    documentUrls: string[];
    runtimeGetContexts: boolean;
    lastError?: string;
  };
  nativeStatusSnapshot?: {
    capturedAt: string;
    trigger: string;
    native_host?: string;
    socket_path?: string;
    event_count?: number;
    host_identity?: NativeHostIdentity;
    broker?: NativeBrokerSummary;
    matches_persistent_host?: boolean;
    overflow_inventory?: {
      artifact_count?: number;
      total_disk_bytes?: number;
      message_type_counts?: Record<string, number>;
      recent_artifacts?: Array<Record<string, unknown>>;
    };
  };
  trace: { events: Array<Record<string, unknown>> };
  sessionMirror: Record<string, unknown>;
}

interface FixtureFlowResult {
  fixtureUrl: string;
  fixtureTabId?: number;
  observedTarget?: Record<string, unknown> | null;
  initialPrompt?: string | null;
  latestOutput?: string | null;
  writeText?: string | null;
  afterWritePrompt?: string | null;
  snapshot?: unknown;
  capture?: unknown;
  errors: string[];
}

interface ProbeRunResult {
  ok: boolean;
  startedAt: string;
  completedAt: string;
  query: Record<string, string>;
  bridge: ProbeResponsePayload | null;
  fixture?: FixtureFlowResult;
  errors: string[];
}

function probePayload(envelope: Envelope<ProbeResponsePayload>): ProbeResponsePayload {
  const payload = envelope.payload as unknown;
  if (payload && typeof payload === 'object' && 'status' in payload) {
    return payload as ProbeResponsePayload;
  }
  const error = payload && typeof payload === 'object' && 'error' in payload
    ? String((payload as { error?: unknown }).error)
    : `unexpected ${envelope.type} response`;
  throw new Error(`bridge.probe failed: ${error}`);
}

function setSummary(text: string, tone: 'muted' | 'ok' | 'warn' | 'bad' = 'muted'): void {
  summary.textContent = text;
  summary.className = tone;
}

function activeContentScriptExperimentSummary(bridge: ProbeResponsePayload | null): string | null {
  const active = bridge?.manifest?.contentScriptPolicy?.activeExperiment;
  if (!active) return null;
  return active.requiresNavigation
    ? `Active content-script experiment: ${active.label}. Reload or renavigate the supported tab before comparing coverage.`
    : `Active content-script experiment: ${active.label}.`;
}

function nativeStatusSummary(bridge: ProbeResponsePayload | null): string | null {
  const snapshot = bridge?.nativeStatusSnapshot;
  const inventory = snapshot?.overflow_inventory;
  if (!snapshot) return null;
  const parts = [
    snapshot.native_host ? `native host: ${snapshot.native_host}` : null,
    snapshot.broker?.role ? `broker role: ${snapshot.broker.role}` : null,
    snapshot.matches_persistent_host === true ? 'same host process as persistent port' : null,
    snapshot.matches_persistent_host === false ? 'different host process than persistent port' : null,
    typeof snapshot.host_identity?.pid === 'number' ? `pid: ${snapshot.host_identity.pid}` : null,
    typeof snapshot.event_count === 'number' ? `events: ${snapshot.event_count}` : null,
    typeof inventory?.artifact_count === 'number' ? `overflow artifacts: ${inventory.artifact_count}` : null,
    typeof inventory?.total_disk_bytes === 'number' ? `overflow bytes: ${inventory.total_disk_bytes}` : null,
  ].filter(Boolean);
  return parts.length ? `Native status snapshot: ${parts.join(' · ')}.` : 'Native status snapshot captured.';
}

function coverageExperimentSummary(bridge: ProbeResponsePayload | null): string | null {
  const coverageAudit = bridge?.receiverAudit?.coverageAudit;
  const plan = coverageAudit?.experimentPlan;
  if (!coverageAudit || !plan) return null;
  const current = plan.experiments.find((experiment) => experiment.id === plan.currentExperimentId);
  const recommended = plan.recommendedExperimentId
    ? plan.experiments.find((experiment) => experiment.id === plan.recommendedExperimentId)
    : undefined;
  if (coverageAudit.gapCount === 0) return 'No current receiver coverage gaps were observed.';
  if (!recommended || recommended.id === current?.id) {
    return plan.recommendedRationale ?? `Receiver coverage gaps remain (${coverageAudit.gapCount}), but the current conservative runtime-priming path is still the recommended next move.`;
  }
  return `${recommended.label} would reduce remaining gaps from ${current?.remainingGapCount ?? coverageAudit.gapCount} to ${recommended.remainingGapCount}. ${plan.recommendedRationale ?? ''}`.trim();
}

function render(result: ProbeRunResult): void {
  output.textContent = JSON.stringify(result, null, 2);
  document.body.dataset.probeReady = '1';
  document.body.dataset.probeOk = result.ok ? '1' : '0';
  const coverageSummary = coverageExperimentSummary(result.bridge);
  const activeExperimentSummary = activeContentScriptExperimentSummary(result.bridge);
  const nativeSummary = nativeStatusSummary(result.bridge);
  const suffix = [coverageSummary, activeExperimentSummary, nativeSummary].filter(Boolean).join(' ');
  if (suffix) {
    setSummary(`${result.ok ? 'Probe completed successfully.' : 'Probe completed with failures.'} ${suffix}`, result.ok ? 'ok' : 'bad');
    return;
  }
  setSummary(result.ok ? 'Probe completed successfully.' : 'Probe completed with failures.', result.ok ? 'ok' : 'bad');
}

async function bridgeRequest<T = unknown>(type: Envelope['type'], payload: Record<string, unknown> = {}): Promise<Envelope<T>> {
  return chrome.runtime.sendMessage(makeEnvelope(type, payload)) as Promise<Envelope<T>>;
}

function queryParams(): Record<string, string> {
  const params: Record<string, string> = {};
  new URLSearchParams(window.location.search).forEach((value, key) => {
    params[key] = value;
  });
  return params;
}

async function waitForTabComplete(tabId: number, timeoutMs: number): Promise<void> {
  const deadline = Date.now() + timeoutMs;
  while (Date.now() < deadline) {
    const tab = await chrome.tabs.get(tabId);
    if (tab.status === 'complete') return;
    await new Promise((resolve) => window.setTimeout(resolve, 125));
  }
}

async function waitForObservedSupportedTab(tabId: number, timeoutMs: number): Promise<ProbeResponsePayload> {
  const deadline = Date.now() + timeoutMs;
  while (Date.now() < deadline) {
    const response = await bridgeRequest<ProbeResponsePayload>('bridge.probe', { limit: 60, await_health_ms: 500 });
    const payload = probePayload(response);
    const supportedTabs = payload.status.supportedTabs ?? [];
    if (supportedTabs.some((tab) => tab.tabId === tabId)) return payload;
    await new Promise((resolve) => window.setTimeout(resolve, 200));
  }
  throw new Error(`supported tab ${tabId} was not observed before timeout`);
}

async function fixtureFlow(fixtureUrl: string, writeText: string | null): Promise<FixtureFlowResult> {
  const result: FixtureFlowResult = {
    fixtureUrl,
    writeText,
    errors: [],
  };

  const created = await chrome.tabs.create({ url: fixtureUrl, active: false });
  if (!created.id) throw new Error('failed to create fixture tab');
  result.fixtureTabId = created.id;
  await waitForTabComplete(created.id, 12_000);
  const observed = await waitForObservedSupportedTab(created.id, 12_000);
  result.observedTarget = observed.status.supportedTabs?.find((tab) => tab.tabId === created.id) ?? null;

  await bridgeRequest('bridge.set_target_tab', { tab_id: created.id });

  const initialPrompt = await bridgeRequest<{ text?: string | null }>('prompt.read', { tab_id: created.id });
  result.initialPrompt = initialPrompt.payload?.text ?? null;

  if (writeText) {
    await bridgeRequest('prompt.write', { tab_id: created.id, text: writeText });
    const afterWrite = await bridgeRequest<{ text?: string | null }>('prompt.read', { tab_id: created.id });
    result.afterWritePrompt = afterWrite.payload?.text ?? null;
    if (result.afterWritePrompt !== writeText) {
      result.errors.push(`prompt.write verification mismatch: expected ${JSON.stringify(writeText)} got ${JSON.stringify(result.afterWritePrompt)}`);
    }
  }

  const latest = await bridgeRequest<{ text?: string | null }>('transcript.latest', { tab_id: created.id });
  result.latestOutput = latest.payload?.text ?? null;
  const snapshot = await bridgeRequest('state.snapshot', { tab_id: created.id });
  result.snapshot = snapshot.payload ?? null;
  const capture = await bridgeRequest('fixture.capture', { tab_id: created.id });
  result.capture = capture.payload ?? null;
  return result;
}

async function runProbe(opts: { includeFixture: boolean }): Promise<void> {
  document.body.dataset.probeReady = '0';
  document.body.dataset.probeOk = '0';
  const query = queryParams();
  const result: ProbeRunResult = {
    ok: false,
    startedAt: new Date().toISOString(),
    completedAt: '',
    query,
    bridge: null,
    errors: [],
  };

  try {
    setSummary('Collecting bridge probe…');
    const bridge = await bridgeRequest<ProbeResponsePayload>('bridge.probe', {
      limit: 80,
      await_health_ms: 1800,
      ensure_offscreen: query.offscreen === '1',
    });
    result.bridge = probePayload(bridge);
    const fixtureUrl = query.fixture || 'https://chatgpt.com/';
    const writeText = query.write ?? 'hello from glasstty probe';
    if (opts.includeFixture || query.fixture) {
      setSummary('Running fixture flow…', 'warn');
      result.fixture = await fixtureFlow(fixtureUrl, writeText);
    }
    const native = result.bridge?.status.nativeConnection;
    const persistentHealthy = Boolean(native && native.connected !== false && native.lastHealthOk !== false && !native.lastHealthError);
    const oneShotHealthy = Boolean(native?.lastOneShotProbeOk && !native?.lastOneShotProbeError);
    const nativeHealthy = persistentHealthy || oneShotHealthy;
    const fixtureHealthy = !result.fixture || result.fixture.errors.length === 0;
    result.ok = Boolean(result.bridge && nativeHealthy && fixtureHealthy);
    if (!nativeHealthy) {
      const diagnosis = native?.laneDiagnosis;
      const runtimeHint = result.bridge?.status.persistentDiagnostics?.runtimeHint;
      result.errors.push(`native health not confirmed: ${diagnosis?.summary ?? native?.lastHealthError ?? native?.lastOneShotProbeError ?? native?.lastDisconnectReason ?? 'not connected'}`);
      if (diagnosis?.recommendedAction) {
        result.errors.push(`native next action: ${diagnosis.recommendedAction}`);
      }
      if (runtimeHint?.summary) {
        result.errors.push(`durable runtime hint: ${runtimeHint.summary}`);
      }
      if (runtimeHint?.recommendedAction) {
        result.errors.push(`durable runtime action: ${runtimeHint.recommendedAction}`);
      }
    }
    if (result.fixture?.errors.length) {
      result.errors.push(...result.fixture.errors);
    }
  } catch (error) {
    result.errors.push(error instanceof Error ? error.message : String(error));
    result.ok = false;
  } finally {
    result.completedAt = new Date().toISOString();
    render(result);
  }
}

window.addEventListener('DOMContentLoaded', () => {
  document.getElementById('run-probe')?.addEventListener('click', () => {
    void runProbe({ includeFixture: false });
  });
  document.getElementById('run-fixture')?.addEventListener('click', () => {
    void runProbe({ includeFixture: true });
  });
  const query = queryParams();
  if (query.run === '1') {
    void runProbe({ includeFixture: Boolean(query.fixture) });
  }
});
