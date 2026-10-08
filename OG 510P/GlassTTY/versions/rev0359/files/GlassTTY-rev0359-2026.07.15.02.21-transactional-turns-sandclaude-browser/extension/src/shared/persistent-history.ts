import type { NativeLaneDiagnosis } from './native-lane';

export interface PersistentWorkerBoot {
  bootId: string;
  bootAt: string;
  bootCount: number;
}

export type PersistentNativeEventKind =
  | 'native.connected'
  | 'native.disconnected'
  | 'native.reconnect_succeeded'
  | 'native.reconnect_failed'
  | 'native.opportunistic_reconnect'
  | 'native.oneshot_reachable';

export interface PersistentNativeEvent {
  at: string;
  bootId: string;
  kind: PersistentNativeEventKind;
  trigger?: string;
  reason?: string;
  diagnosisStatus?: string;
  diagnosisSummary?: string;
  persistentBrokerRole?: string;
  oneShotBrokerRole?: string;
  snapshotBrokerRole?: string;
  nativeHost?: string;
  socketPath?: string;
  hostBootId?: string;
  hostPid?: number;
}

export interface PersistentRuntimeHint {
  status:
    | 'none'
    | 'current_boot_connected'
    | 'current_boot_oneshot_only'
    | 'restart_pending'
    | 'restart_churn'
    | 'current_boot_unproven';
  summary: string;
  recommendedAction: string;
  currentBootId?: string;
  currentBootSeenConnected: boolean;
  currentBootSeenOneShot: boolean;
  previousBootSeenConnected: boolean;
  bootCount: number;
  recentDisconnectReason?: string;
  recentReconnectFailureReason?: string;
}

export interface PersistentBridgeHistory {
  updatedAt?: string;
  workerBoots: PersistentWorkerBoot[];
  nativeEvents: PersistentNativeEvent[];
  runtimeHint?: PersistentRuntimeHint;
}

export interface PersistentHistoryOptions {
  maxWorkerBoots?: number;
  maxNativeEvents?: number;
}

export interface PersistentHistoryRuntimeInput {
  currentBootId?: string;
  currentBootAt?: string;
  bootCount?: number;
}

const DEFAULT_MAX_WORKER_BOOTS = 12;
const DEFAULT_MAX_NATIVE_EVENTS = 40;

function trimNewest<T>(items: T[], maxItems: number): T[] {
  if (items.length <= maxItems) return items;
  return items.slice(items.length - maxItems);
}

function normalizeWorkerBoots(value: unknown): PersistentWorkerBoot[] {
  if (!Array.isArray(value)) return [];
  return value.flatMap((item) => {
    if (!item || typeof item !== 'object') return [];
    const record = item as Record<string, unknown>;
    const bootId = typeof record.bootId === 'string' ? record.bootId : null;
    const bootAt = typeof record.bootAt === 'string' ? record.bootAt : null;
    const bootCount = typeof record.bootCount === 'number' && Number.isFinite(record.bootCount)
      ? Math.max(1, Math.trunc(record.bootCount))
      : null;
    if (!bootId || !bootAt || bootCount === null) return [];
    return [{ bootId, bootAt, bootCount } satisfies PersistentWorkerBoot];
  });
}

function normalizeNativeEvents(value: unknown): PersistentNativeEvent[] {
  if (!Array.isArray(value)) return [];
  return value.flatMap((item) => {
    if (!item || typeof item !== 'object') return [];
    const record = item as Record<string, unknown>;
    const at = typeof record.at === 'string' ? record.at : null;
    const bootId = typeof record.bootId === 'string' ? record.bootId : null;
    const kind = typeof record.kind === 'string' ? record.kind : null;
    if (!at || !bootId || !kind) return [];
    return [{
      at,
      bootId,
      kind: kind as PersistentNativeEventKind,
      trigger: typeof record.trigger === 'string' ? record.trigger : undefined,
      reason: typeof record.reason === 'string' ? record.reason : undefined,
      diagnosisStatus: typeof record.diagnosisStatus === 'string' ? record.diagnosisStatus : undefined,
      diagnosisSummary: typeof record.diagnosisSummary === 'string' ? record.diagnosisSummary : undefined,
      persistentBrokerRole: typeof record.persistentBrokerRole === 'string' ? record.persistentBrokerRole : undefined,
      oneShotBrokerRole: typeof record.oneShotBrokerRole === 'string' ? record.oneShotBrokerRole : undefined,
      snapshotBrokerRole: typeof record.snapshotBrokerRole === 'string' ? record.snapshotBrokerRole : undefined,
      nativeHost: typeof record.nativeHost === 'string' ? record.nativeHost : undefined,
      socketPath: typeof record.socketPath === 'string' ? record.socketPath : undefined,
      hostBootId: typeof record.hostBootId === 'string' ? record.hostBootId : undefined,
      hostPid: typeof record.hostPid === 'number' && Number.isFinite(record.hostPid) ? Math.trunc(record.hostPid) : undefined,
    } satisfies PersistentNativeEvent];
  });
}

export function normalizePersistentBridgeHistory(value: unknown, options: PersistentHistoryOptions = {}): PersistentBridgeHistory {
  const maxWorkerBoots = options.maxWorkerBoots ?? DEFAULT_MAX_WORKER_BOOTS;
  const maxNativeEvents = options.maxNativeEvents ?? DEFAULT_MAX_NATIVE_EVENTS;
  const record = value && typeof value === 'object' ? value as Record<string, unknown> : {};
  return {
    updatedAt: typeof record.updatedAt === 'string' ? record.updatedAt : undefined,
    workerBoots: trimNewest(normalizeWorkerBoots(record.workerBoots), maxWorkerBoots),
    nativeEvents: trimNewest(normalizeNativeEvents(record.nativeEvents), maxNativeEvents),
  };
}

export function recordPersistentWorkerBoot(
  history: PersistentBridgeHistory,
  boot: PersistentWorkerBoot,
  options: PersistentHistoryOptions = {},
): PersistentBridgeHistory {
  const maxWorkerBoots = options.maxWorkerBoots ?? DEFAULT_MAX_WORKER_BOOTS;
  const existing = history.workerBoots.filter((entry) => entry.bootId !== boot.bootId);
  return {
    ...history,
    updatedAt: boot.bootAt,
    workerBoots: trimNewest([...existing, boot], maxWorkerBoots),
  };
}

export function appendPersistentNativeEvent(
  history: PersistentBridgeHistory,
  event: PersistentNativeEvent,
  options: PersistentHistoryOptions = {},
): PersistentBridgeHistory {
  const maxNativeEvents = options.maxNativeEvents ?? DEFAULT_MAX_NATIVE_EVENTS;
  return {
    ...history,
    updatedAt: event.at,
    nativeEvents: trimNewest([...history.nativeEvents, event], maxNativeEvents),
  };
}

function timeSortKey(value: string): number {
  const parsed = Date.parse(value);
  return Number.isFinite(parsed) ? parsed : 0;
}

function mostRecentReason(events: PersistentNativeEvent[], kind: PersistentNativeEventKind): string | undefined {
  for (let index = events.length - 1; index >= 0; index -= 1) {
    const event = events[index];
    if (event.kind === kind && event.reason) return event.reason;
  }
  return undefined;
}

function bootIdsWithinWindow(boots: PersistentWorkerBoot[], now: number, windowMs: number): Set<string> {
  return new Set(
    boots
      .filter((boot) => {
        const parsed = Date.parse(boot.bootAt);
        return Number.isFinite(parsed) && (now - parsed) <= windowMs;
      })
      .map((boot) => boot.bootId),
  );
}

export function derivePersistentRuntimeHint(
  history: PersistentBridgeHistory,
  runtime: PersistentHistoryRuntimeInput,
  now = Date.now(),
): PersistentRuntimeHint {
  const currentBootId = runtime.currentBootId;
  const workerBoots = [...history.workerBoots].sort((a, b) => timeSortKey(a.bootAt) - timeSortKey(b.bootAt));
  const nativeEvents = [...history.nativeEvents].sort((a, b) => timeSortKey(a.at) - timeSortKey(b.at));
  const bootCount = Math.max(workerBoots.length, typeof runtime.bootCount === 'number' && Number.isFinite(runtime.bootCount) ? Math.trunc(runtime.bootCount) : 0);

  if (!currentBootId || (!workerBoots.length && !nativeEvents.length)) {
    return {
      status: 'none',
      summary: 'No persistent cross-restart bridge history yet.',
      recommendedAction: 'Run bridge.status or bridge.probe once to seed durable diagnostics.',
      currentBootId,
      currentBootSeenConnected: false,
      currentBootSeenOneShot: false,
      previousBootSeenConnected: false,
      bootCount,
    };
  }

  const currentBootEvents = nativeEvents.filter((event) => event.bootId === currentBootId);
  const previousBootEvents = nativeEvents.filter((event) => event.bootId !== currentBootId);
  const currentBootSeenConnected = currentBootEvents.some((event) => event.kind === 'native.connected');
  const currentBootSeenOneShot = currentBootEvents.some((event) => event.kind === 'native.oneshot_reachable');
  const previousBootSeenConnected = previousBootEvents.some((event) => event.kind === 'native.connected');
  const recentBootCount = bootIdsWithinWindow(workerBoots, now, 15 * 60_000).size;
  const recentDisconnectReason = mostRecentReason(nativeEvents, 'native.disconnected');
  const recentReconnectFailureReason = mostRecentReason(nativeEvents, 'native.reconnect_failed');

  if (currentBootSeenConnected) {
    return {
      status: 'current_boot_connected',
      summary: 'The current service-worker boot has already re-established the persistent native lane.',
      recommendedAction: 'No durable-resume action needed.',
      currentBootId,
      currentBootSeenConnected,
      currentBootSeenOneShot,
      previousBootSeenConnected,
      bootCount,
      recentDisconnectReason,
      recentReconnectFailureReason,
    };
  }

  if (currentBootSeenOneShot) {
    return {
      status: 'current_boot_oneshot_only',
      summary: 'This service-worker boot has durable proof that one-shot native diagnostics work, but it has not yet re-established the persistent native port.',
      recommendedAction: 'Trigger or inspect the persistent reconnect path now; the host manifest appears reachable from this boot.',
      currentBootId,
      currentBootSeenConnected,
      currentBootSeenOneShot,
      previousBootSeenConnected,
      bootCount,
      recentDisconnectReason,
      recentReconnectFailureReason,
    };
  }

  if (recentBootCount >= 3 && previousBootSeenConnected) {
    return {
      status: 'restart_churn',
      summary: 'Recent history shows repeated service-worker boots without the current boot reclaiming the persistent native lane.',
      recommendedAction: 'Inspect reconnect traces and browser/native-host logs; MV3 restart churn may be masking a deeper reconnect failure.',
      currentBootId,
      currentBootSeenConnected,
      currentBootSeenOneShot,
      previousBootSeenConnected,
      bootCount,
      recentDisconnectReason,
      recentReconnectFailureReason,
    };
  }

  if (previousBootSeenConnected) {
    return {
      status: 'restart_pending',
      summary: 'A previous worker boot held the persistent native lane, but the current boot has not yet proven it reclaimed that port.',
      recommendedAction: 'Run bridge.status or bridge.probe and check whether the reconnect alarm or explicit reseat path restores the port.',
      currentBootId,
      currentBootSeenConnected,
      currentBootSeenOneShot,
      previousBootSeenConnected,
      bootCount,
      recentDisconnectReason,
      recentReconnectFailureReason,
    };
  }

  return {
    status: 'current_boot_unproven',
    summary: 'The current service-worker boot has not yet established durable native-lane evidence.',
    recommendedAction: 'Collect bridge.status or bridge.probe once on this boot before drawing conclusions.',
    currentBootId,
    currentBootSeenConnected,
    currentBootSeenOneShot,
    previousBootSeenConnected,
    bootCount,
    recentDisconnectReason,
    recentReconnectFailureReason,
  };
}

export function buildPersistentDiagnosticsSnapshot(
  rawHistory: unknown,
  runtime: PersistentHistoryRuntimeInput,
  _diagnosis: Pick<NativeLaneDiagnosis, 'status' | 'summary' | 'recommendedAction'> | undefined,
  now = Date.now(),
): PersistentBridgeHistory {
  const history = normalizePersistentBridgeHistory(rawHistory);
  return {
    ...history,
    runtimeHint: derivePersistentRuntimeHint(history, runtime, now),
    updatedAt: history.updatedAt,
  };
}
