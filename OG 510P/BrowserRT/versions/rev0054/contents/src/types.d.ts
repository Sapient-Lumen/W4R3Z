export const VERSION: '0.0.54';
export const REVISION: 'rev0054';

export type RtLane =
  | 'main'
  | 'interactive'
  | 'cpu'
  | 'storage'
  | 'gpu'
  | 'render'
  | 'media'
  | 'audio'
  | 'ml'
  | 'network'
  | 'cross-tab'
  | 'plugin'
  | 'maintenance';

export type RtPriority = 'critical' | 'user-blocking' | 'user-visible' | 'background' | 'maintenance';
export type RtObjectRefKind = 'inline' | 'transfer' | 'shared' | 'opfs' | 'stream' | 'gpu' | 'block';
export type RtOverflow = 'wait' | 'drop-oldest' | 'drop-newest' | 'fail';

export interface RtCapabilities {
  environment: string;
  workers: boolean;
  moduleWorkers: boolean;
  transferableArrayBuffer: boolean;
  sharedArrayBuffer: boolean;
  atomics: boolean;
  crossOriginIsolated: boolean;
  opfs: boolean;
  storageEstimate: boolean;
  webgpu: boolean;
  webnn: boolean;
  offscreenCanvas: boolean;
  webcodecs: boolean;
  videoFrameTransfer: boolean;
  broadcastChannel: boolean;
  messageChannel: boolean;
  sharedWorker: boolean;
  serviceWorker: boolean;
  webLocks: boolean;
  schedulerPostTask: boolean;
  schedulerYield: boolean;
  performanceObserver: boolean;
  measureMemory: boolean;
}

export interface RtObjectRef {
  kind: RtObjectRefKind;
  id: string;
  bytes: number;
  ownership: string;
  createdAt: number;
  [key: string]: unknown;
}

export interface RtBlockRef extends RtObjectRef {
  kind: 'block';
  digest: string;
  hash: string;
  algorithm: 'sha256';
  backend: string;
  bytes: number;
}

export interface RtTransferObject {
  ref: RtObjectRef & { kind: 'transfer'; transferType: 'ArrayBuffer' };
  buffer: ArrayBuffer;
  transferList: ArrayBuffer[];
}

export interface RtOpfsProbeResult {
  ref: RtObjectRef & { kind: 'opfs'; path: string; backend: 'opfs-async' };
  bytesWritten: number;
  bytesRead: number;
  same: boolean;
  digest: string;
  fileName: string;
  path: string;
  cleanup: boolean;
}

export interface RtBlockPutResult {
  ref: RtBlockRef;
  digest: string;
  hash: string;
  bytes: number;
  duplicate: boolean;
}

export class OpfsAsyncBlockStore {
  constructor(config?: { name?: string; prefix?: string; provider?: string; trace?: TraceLog | null });
  readonly name: string;
  readonly provider: string;
  readonly prefix: string;
  readonly available: boolean;
  readonly stats: Record<string, number>;
  open(): Promise<unknown>;
  blockPath(hash: string): string;
  put(value: string | Uint8Array | ArrayBuffer | ArrayBufferView, fields?: Record<string, unknown>): Promise<Readonly<RtBlockPutResult & { path: string }>>;
  get(refOrDigest: string | RtBlockRef): Promise<Uint8Array>;
  has(refOrDigest: string | RtBlockRef): Promise<boolean>;
  delete(refOrDigest: string | RtBlockRef): Promise<boolean>;
  verify(refOrDigest: string | RtBlockRef): Promise<Readonly<{ digest: string; present: boolean; ok: boolean; bytes: number; path: string }>>;
  estimate(): Promise<Readonly<{ quota: number | null; usage: number | null; usageDetails: unknown }>>;
  cleanupForTest(): Promise<boolean>;
  snapshot(): Readonly<Record<string, unknown>>;
}
export function createOpfsAsyncBlockStore(config?: object): OpfsAsyncBlockStore;

export interface RtEnvelope {
  magic: 'BRT1';
  version: 1;
  id: string;
  parentId: string | null;
  traceId: string | null;
  op: string;
  lane: RtLane;
  priority: RtPriority;
  deadlineMs: number;
  flags: number;
  payloadRef: RtObjectRef | null;
}

export interface RtTraceEvent {
  seq: number;
  t: number;
  kind: string;
  [key: string]: unknown;
}

export interface RtBootReport {
  project: 'BrowserRT';
  revision: 'rev0039';
  version: '0.0.39';
  environment: string;
  createdAt: string;
  options: Readonly<Record<string, unknown>>;
  capabilities: RtCapabilities;
  availableTierNames: string[];
  lanes: RtLane[];
  priorities: RtPriority[];
  capabilityTiers: Array<{ id: number; name: string; meaning: string }>;
  executableProofs: Readonly<Record<string, boolean>>;
}

export class TraceLog {
  emit(kind: string, detail?: Record<string, unknown>): RtTraceEvent;
  snapshot(): RtTraceEvent[];
  find(kind: string): RtTraceEvent[];
  count(kind: string): number;
  kinds(): string[];
}

export class BoundedChannel<T = unknown> {
  constructor(config?: { capacity?: number; overflow?: RtOverflow; label?: string; trace?: TraceLog | null });
  capacity: number;
  overflow: RtOverflow;
  label: string;
  send(value: T): Promise<{ disposition: string }>;
  receive(): Promise<T>;
  size(): number;
}

export class MemoryBlockStore {
  constructor(config?: { name?: string; trace?: TraceLog | null; provider?: string; quotaBytes?: number; faults?: Array<Record<string, unknown>> });
  name: string;
  provider: string;
  quotaBytes: number;
  createdAt: number;
  stats: Record<string, number>;
  put(value: Uint8Array | ArrayBuffer | ArrayBufferView | string, options?: { label?: string }): Promise<RtBlockPutResult>;
  get(ref: RtBlockRef | RtObjectRef | string): Promise<Uint8Array>;
  has(ref: RtBlockRef | RtObjectRef | string): Promise<boolean>;
  delete(ref: RtBlockRef | RtObjectRef | string): Promise<boolean>;
  verify(ref: RtBlockRef | RtObjectRef | string): Promise<Readonly<{ digest: string; actualDigest?: string; present: boolean; ok: boolean; bytes?: number }>>;
  corrupt(ref: RtBlockRef | RtObjectRef | string, options?: { mode?: 'flip-first-byte' | 'truncate' }): Readonly<{ digest: string; mode: string }>;
  corruptForTest(ref: RtBlockRef | RtObjectRef | string, mutator?: ((bytes: Uint8Array) => void) | null): boolean;
  injectFault(fault: Record<string, unknown>): void;
  failNextPutForTest(reason?: string): void;
  bytesUsed(): number;
  snapshot(): Readonly<Record<string, unknown>>;
  manifest(): Readonly<Record<string, unknown>>;
}


export interface RtJournalRecoveryResult {
  checkpointSeq: number;
  finalSeq: number;
  appliedJournalRecords: number;
  appliedJournalSeqs: number[];
  ignoredTailRecords: number;
  blockCount: number;
}

export class JournaledMemoryBlockStore {
  constructor(config?: { name?: string; trace?: TraceLog | null; provider?: string });
  name: string;
  provider: string;
  stats: Record<string, number>;
  put(value: Uint8Array | ArrayBuffer | ArrayBufferView | string, options?: { label?: string }): Promise<RtBlockPutResult & { seq: number }>;
  get(ref: RtBlockRef | RtObjectRef | string): Promise<Uint8Array>;
  has(ref: RtBlockRef | RtObjectRef | string): Promise<boolean>;
  delete(ref: RtBlockRef | RtObjectRef | string): Promise<boolean>;
  checkpoint(options?: { label?: string }): Promise<Readonly<Record<string, unknown>>>;
  exportJournal(): Array<Record<string, unknown>>;
  tornRecordForTest(options?: Record<string, unknown>): Record<string, unknown>;
  snapshot(): Readonly<Record<string, unknown>>;
  manifestView(): Readonly<Record<string, unknown>>;
  static recover(config?: { manifest: Record<string, unknown>; journal?: Array<Record<string, unknown>>; trace?: TraceLog | null; name?: string; provider?: string; strictTail?: boolean }): Promise<Readonly<{ store: JournaledMemoryBlockStore; recovery: RtJournalRecoveryResult }>>;
}


export interface RtSharedRingSnapshot {
  label: string;
  capacity: number;
  read: number;
  write: number;
  size: number;
  closed: boolean;
  fullHits: number;
  emptyWaits: number;
  pushCount: number;
  popCount: number;
  notifySeq: number;
}

export class SharedInt32Ring {
  constructor(config: { sab: SharedArrayBuffer; capacity?: number | null; label?: string; trace?: TraceLog | null; initialize?: boolean });
  static allocate(config?: { capacity?: number; label?: string; trace?: TraceLog | null }): SharedInt32Ring;
  sab: SharedArrayBuffer;
  label: string;
  capacity: number;
  tryPush(value: number): boolean;
  pop(): { done: boolean; value: number | null };
  waitPop(options?: { timeoutMs?: number }): { done: boolean; value: number | null };
  close(): void;
  snapshot(): RtSharedRingSnapshot;
}


export interface RtSharedFrameRingSnapshot {
  label: string;
  capacityBytes: number;
  readOffset: number;
  writeOffset: number;
  usedBytes: number;
  freeBytes: number;
  closed: boolean;
  fullHits: number;
  emptyWaits: number;
  pushCount: number;
  popCount: number;
  notifySeq: number;
  wrapCount: number;
  maxFrameBytes: number;
  reservedBytes: number;
}

export class SharedFrameRing {
  constructor(config: { sab: SharedArrayBuffer; capacityBytes?: number | null; label?: string; trace?: TraceLog | null; initialize?: boolean });
  static allocate(config?: { capacityBytes?: number; label?: string; trace?: TraceLog | null }): SharedFrameRing;
  sab: SharedArrayBuffer;
  label: string;
  capacityBytes: number;
  tryPushFrame(payload: Uint8Array | ArrayBuffer | ArrayBufferView | string, options?: { seq?: number | null }): boolean;
  popFrame(): { done: boolean; frame: { seq: number; payload: Uint8Array } | null };
  waitPopFrame(options?: { timeoutMs?: number }): { done: boolean; frame: { seq: number; payload: Uint8Array } | null };
  close(): void;
  snapshot(): RtSharedFrameRingSnapshot;
}

export interface RtSpillMailboxSnapshot {
  label: string;
  provider: string;
  queueDepth: number;
  pendingCount: number;
  memoryCapacityBytes: number;
  memoryUsed: number;
  maxFrameBytes: number;
  stats: Record<string, number>;
  providerSnapshot: Readonly<Record<string, unknown>>;
}

export class SpillFrameMailbox {
  constructor(config: { label?: string; provider: MemoryBlockStore; memoryCapacityBytes?: number; maxFrameBytes?: number; trace?: TraceLog | null; deleteSpilledBlocksOnAck?: boolean });
  label: string;
  provider: MemoryBlockStore;
  memoryCapacityBytes: number;
  maxFrameBytes: number;
  deleteSpilledBlocksOnAck: boolean;
  stats: Record<string, number>;
  enqueue(payload: Uint8Array | ArrayBuffer | ArrayBufferView | string, options?: { seq?: number | null; label?: string | null }): Promise<Readonly<Record<string, unknown>>>;
  dequeue(options?: { consumerId?: string }): Promise<Readonly<{ pendingId: string; consumerId: string; seq: number; source: string; bytes: number; checksum32: number; payload: Uint8Array; ref: RtBlockRef | null }> | null>;
  ack(pendingId: string, options?: { deleteSpilledBlock?: boolean }): Promise<boolean>;
  reclaimPending(options?: { max?: number }): Readonly<Record<string, unknown>>;
  snapshot(): RtSpillMailboxSnapshot;
}


export class PersistedSpillMailbox {
  constructor(config: { label?: string; provider: JournaledMemoryBlockStore | MemoryBlockStore; trace?: TraceLog | null; maxFrameBytes?: number; deleteBlockOnAck?: boolean });
  label: string;
  provider: JournaledMemoryBlockStore | MemoryBlockStore;
  maxFrameBytes: number;
  deleteBlockOnAck: boolean;
  stats: Record<string, number>;
  enqueue(payload: Uint8Array | ArrayBuffer | ArrayBufferView | string, options?: { label?: string | null }): Promise<Readonly<Record<string, unknown>>>;
  dequeue(options?: { consumerId?: string }): Promise<Readonly<{ pendingId: string; consumerId: string; seq: number; ref: RtBlockRef; bytes: number; checksum32: number; deliveryCount: number; payload: Uint8Array }> | null>;
  ack(pendingId: string, options?: { deleteBlock?: boolean }): Promise<boolean>;
  reclaimPending(options?: { max?: number }): Readonly<Record<string, unknown>>;
  checkpoint(options?: { label?: string | null }): Promise<Readonly<Record<string, unknown>>>;
  compact(options?: { dryRun?: boolean; reason?: string; includeProviderManifest?: boolean }): Promise<Readonly<Record<string, unknown>>>;
  exportJournal(): Array<Record<string, unknown>>;
  tornRecordForTest(options?: Record<string, unknown>): Record<string, unknown>;
  snapshot(): Readonly<Record<string, unknown>>;
  static recover(config?: { manifest: Record<string, unknown>; journal?: Array<Record<string, unknown>>; provider: JournaledMemoryBlockStore | MemoryBlockStore; trace?: TraceLog | null; label?: string; strictTail?: boolean; requeuePending?: boolean }): Promise<Readonly<{ mailbox: PersistedSpillMailbox; recovery: Record<string, unknown> }>>;
}
export function createPersistedSpillMailbox(config: { label?: string; provider: JournaledMemoryBlockStore | MemoryBlockStore; trace?: TraceLog | null; memoryCapacityBytes?: number; maxFrameBytes?: number; deleteBlockOnAck?: boolean }): PersistedSpillMailbox;
export function recoverPersistedSpillMailbox(config: { manifest: Record<string, unknown>; journal?: Array<Record<string, unknown>>; provider: JournaledMemoryBlockStore | MemoryBlockStore; trace?: TraceLog | null; label?: string; strictTail?: boolean; requeuePending?: boolean }): Promise<Readonly<{ mailbox: PersistedSpillMailbox; recovery: Record<string, unknown> }>>;
export function checksumPersistedSpillPayload32(payload: Uint8Array | ArrayBuffer | ArrayBufferView | string): number;

export class WorkerAgent {
  constructor(config: { worker: Worker | unknown; name?: string; trace?: TraceLog });
  readonly closed: boolean;
  readonly failed: boolean;
  readonly trace: TraceLog;
  readonly ready: Promise<WorkerAgent>;
  onExit(callback: (event: { agent: WorkerAgent; code: number | null; error: Error }) => void): () => void;
  call<T = unknown>(op: string, payload?: unknown, options?: { transfer?: Transferable[]; timeoutMs?: number; lane?: RtLane; priority?: RtPriority }): Promise<T>;
  terminate(reason?: string): Promise<{ disposition: string }>;
}

export class Supervisor {
  constructor(config?: { name?: string; workerURL?: URL | string; trace?: TraceLog; restartLimit?: number });
  name: string;
  restartLimit: number;
  restartCount: number;
  closed: boolean;
  start(): Promise<Supervisor>;
  call<T = unknown>(op: string, payload?: unknown, options?: { transfer?: Transferable[]; timeoutMs?: number; lane?: RtLane; priority?: RtPriority }): Promise<T>;
  snapshot(): Readonly<Record<string, unknown>>;
  close(): Promise<Readonly<Record<string, unknown>>>;
}

export function detectCapabilities(g?: unknown): RtCapabilities;
export function capabilityTierNames(): string[];
export function availableCapabilityTierNames(capabilities?: RtCapabilities): string[];
export function createObjectRef(kind: RtObjectRefKind, fields?: Record<string, unknown>): RtObjectRef;
export function digestBytesHex(bytes: Uint8Array | ArrayBuffer): Promise<string>;
export function createBlockObjectRef(hash: string, fields?: Record<string, unknown>): RtBlockRef;
export function createMemoryBlockStore(config?: { name?: string; trace?: TraceLog | null; provider?: string; quotaBytes?: number; faults?: Array<Record<string, unknown>> }): MemoryBlockStore;
export function createJournaledMemoryBlockStore(config?: { name?: string; trace?: TraceLog | null; provider?: string }): JournaledMemoryBlockStore;
export function recoverJournaledMemoryBlockStore(config?: { manifest: Record<string, unknown>; journal?: Array<Record<string, unknown>>; trace?: TraceLog | null; name?: string; provider?: string; strictTail?: boolean }): Promise<Readonly<{ store: JournaledMemoryBlockStore; recovery: RtJournalRecoveryResult }>>;
export function createTransferObjectRef(buffer: ArrayBuffer, fields?: Record<string, unknown>): RtObjectRef;
export function createTransferObject(buffer: ArrayBuffer, fields?: Record<string, unknown>): RtTransferObject;
export function createOpfsObjectRef(path: string, fields?: Record<string, unknown>): RtObjectRef & { kind: 'opfs'; path: string; backend: string };
export function createOpfsSyncObjectRef(path: string, fields?: Record<string, unknown>): RtObjectRef & { kind: 'opfs'; path: string; backend: 'opfs-sync-access-handle' };
export function opfsAsyncWriteReadProbe(config?: { path?: string; bytes?: Uint8Array; text?: string; cleanup?: boolean }): Promise<RtOpfsProbeResult>;
export function createEnvelope(op: string, fields?: Partial<RtEnvelope>): RtEnvelope;
export function createSharedInt32Ring(config?: { capacity?: number; label?: string; trace?: TraceLog | null }): SharedInt32Ring;
export function openSharedInt32Ring(sab: SharedArrayBuffer, config?: { label?: string; trace?: TraceLog | null }): SharedInt32Ring;
export function createSharedFrameRing(config?: { capacityBytes?: number; label?: string; trace?: TraceLog | null }): SharedFrameRing;
export function openSharedFrameRing(sab: SharedArrayBuffer, config?: { label?: string; trace?: TraceLog | null }): SharedFrameRing;
export function createSpillFrameMailbox(config: { label?: string; provider: MemoryBlockStore; memoryCapacityBytes?: number; maxFrameBytes?: number; trace?: TraceLog | null; deleteSpilledBlocksOnAck?: boolean }): SpillFrameMailbox;
export function checksumFramePayload32(payload: Uint8Array | ArrayBuffer | ArrayBufferView | string): number;
export function spawnWorkerAgent(config?: { workerURL?: URL | string; name?: string; trace?: TraceLog; workerOptions?: Record<string, unknown> }): Promise<WorkerAgent>;
export function createSupervisor(config?: { name?: string; workerURL?: URL | string; trace?: TraceLog; restartLimit?: number }): Supervisor;
export function createBootReport(config?: { capabilities?: RtCapabilities; options?: Record<string, unknown> }): RtBootReport;
export function boot(options?: Record<string, unknown>): Promise<Readonly<{
  version: '0.0.54';
  revision: 'rev0054';
  options: Readonly<Record<string, unknown>>;
  capabilities: RtCapabilities;
  report: RtBootReport;
  trace: TraceLog;
  channel<T = unknown>(config?: { capacity?: number; overflow?: RtOverflow; label?: string }): BoundedChannel<T>;
  objectRef(kind: RtObjectRefKind, fields?: Record<string, unknown>): RtObjectRef;
  sharedInt32Ring(config?: { capacity?: number; label?: string; trace?: TraceLog | null }): SharedInt32Ring;
  openSharedInt32Ring(sab: SharedArrayBuffer, config?: { label?: string; trace?: TraceLog | null }): SharedInt32Ring;
  sharedFrameRing(config?: { capacityBytes?: number; label?: string; trace?: TraceLog | null }): SharedFrameRing;
  openSharedFrameRing(sab: SharedArrayBuffer, config?: { label?: string; trace?: TraceLog | null }): SharedFrameRing;
  spillFrameMailbox(config?: { label?: string; provider?: MemoryBlockStore; memoryCapacityBytes?: number; maxFrameBytes?: number; trace?: TraceLog | null; deleteSpilledBlocksOnAck?: boolean }): SpillFrameMailbox;
  persistedSpillMailbox(config?: { label?: string; provider?: JournaledMemoryBlockStore | MemoryBlockStore; memoryCapacityBytes?: number; maxFrameBytes?: number; trace?: TraceLog | null; deleteBlockOnAck?: boolean }): PersistedSpillMailbox;
  recoverPersistedSpillMailbox(config?: { manifest: Record<string, unknown>; journal?: Array<Record<string, unknown>>; provider: JournaledMemoryBlockStore | MemoryBlockStore; trace?: TraceLog | null; label?: string; strictTail?: boolean; requeuePending?: boolean }): Promise<Readonly<{ mailbox: PersistedSpillMailbox; recovery: Record<string, unknown> }>>;
  blockObjectRef(hash: string, fields?: Record<string, unknown>): RtBlockRef;
  blockStore(config?: { name?: string; trace?: TraceLog | null; provider?: string; quotaBytes?: number; faults?: Array<Record<string, unknown>> }): MemoryBlockStore;
  journaledBlockStore(config?: { name?: string; trace?: TraceLog | null; provider?: string }): JournaledMemoryBlockStore;
  recoverJournaledBlockStore(config?: { manifest: Record<string, unknown>; journal?: Array<Record<string, unknown>>; trace?: TraceLog | null; name?: string; provider?: string; strictTail?: boolean }): Promise<Readonly<{ store: JournaledMemoryBlockStore; recovery: RtJournalRecoveryResult }>>;
  transferObject(buffer: ArrayBuffer, fields?: Record<string, unknown>): RtTransferObject;
  opfsObjectRef(path: string, fields?: Record<string, unknown>): RtObjectRef & { kind: 'opfs'; path: string; backend: string };
  opfsSyncObjectRef(path: string, fields?: Record<string, unknown>): RtObjectRef & { kind: 'opfs'; path: string; backend: 'opfs-sync-access-handle' };
  opfsAsyncWriteReadProbe(config?: { path?: string; bytes?: Uint8Array; text?: string; cleanup?: boolean }): Promise<RtOpfsProbeResult>;
  spawnAgent(config?: { workerURL?: URL | string; name?: string; trace?: TraceLog; workerOptions?: Record<string, unknown> }): Promise<WorkerAgent>;
  supervisor(config?: { name?: string; workerURL?: URL | string; trace?: TraceLog; restartLimit?: number }): Supervisor;
  admissionController(config?: Record<string, unknown>): WatermarkAdmissionController;
  adaptiveConcurrencyController(config?: Record<string, unknown>): AdaptiveConcurrencyController;
  priorityFairScheduler(config?: Record<string, unknown>): PriorityFairScheduler;
  crossLaneScheduler(config?: Record<string, unknown>): CrossLaneScheduler;
  storageLaneExecutor(config?: Record<string, unknown>): StorageLaneExecutor;
  retryBudgetAdmissionController(config?: Record<string, unknown>): RetryBudgetAdmissionController;
  storageLaneRetryController(config?: Record<string, unknown>): StorageLaneRetryController;
  providerResilienceHistoryRunner(config?: Record<string, unknown>): ProviderResilienceHistoryRunner;
  close(): RtTraceEvent[];
}>>;

export class WatermarkAdmissionController {
  constructor(config?: Record<string, unknown>);
  tryAdmit(input: { bytes: number; priority?: string; label?: string; metadata?: unknown }): Readonly<Record<string, unknown>>;
  release(leaseId: string, input?: { outcome?: string }): Readonly<Record<string, unknown>>;
  markProviderUnhealthy(reason?: string): void;
  markProviderHealthy(reason?: string): void;
  snapshot(): Readonly<Record<string, unknown>>;
}
export function createWatermarkAdmissionController(config?: Record<string, unknown>): WatermarkAdmissionController;


export class AdaptiveConcurrencyController {
  constructor(config?: Record<string, unknown>);
  label: string;
  limit: number;
  minLimit: number;
  maxLimit: number;
  inFlight: number;
  windowIndex: number;
  stats: Record<string, number>;
  tryAcquire(input?: { priority?: string; weight?: number; label?: string; metadata?: unknown }): Readonly<Record<string, unknown>>;
  release(leaseId: string, input?: { latencyMs?: number; outcome?: string }): Readonly<Record<string, unknown>>;
  observeWindow(input?: { forceProbe?: boolean }): Readonly<Record<string, unknown>>;
  markProviderUnhealthy(reason?: string): void;
  markProviderHealthy(reason?: string): void;
  snapshot(): Readonly<Record<string, unknown>>;
}
export function createAdaptiveConcurrencyController(config?: Record<string, unknown>): AdaptiveConcurrencyController;


export type PriorityFairTaskPriority = 'critical' | 'user-blocking' | 'user-visible' | 'background' | 'maintenance';
export class PriorityFairScheduler {
  constructor(options?: Record<string, unknown>);
  enqueue(task: { id?: string; flowId: string; priority?: PriorityFairTaskPriority; cost?: number; weight?: number; payload?: unknown; metadata?: unknown }): Readonly<Record<string, unknown>>;
  dispatchNext(): Readonly<Record<string, unknown>>;
  drain(options?: { limit?: number }): ReadonlyArray<Record<string, unknown>>;
  snapshot(): Readonly<Record<string, unknown>>;
}
export function createPriorityFairScheduler(options?: Record<string, unknown>): PriorityFairScheduler;
export function createPriorityFairSchedulerObjectRef(id?: string, fields?: Record<string, unknown>): Readonly<Record<string, unknown>>;

export class CrossLaneScheduler {
  constructor(options?: Record<string, unknown>);
  enqueue(task: { id?: string; lane?: string; priority?: PriorityFairTaskPriority; cost?: number; flowId?: string; dependsOn?: string[]; fallbackLanes?: string[]; payload?: unknown; metadata?: unknown }): Readonly<Record<string, unknown>>;
  dispatchNext(): Readonly<Record<string, unknown>>;
  complete(taskId: string, options?: { outcome?: string; metadata?: unknown }): Readonly<Record<string, unknown>>;
  markCompleted(taskId: string, options?: { reason?: string }): Readonly<Record<string, unknown>>;
  markLaneUnhealthy(laneId: string, reason?: string): Readonly<Record<string, unknown>>;
  markLaneHealthy(laneId: string, reason?: string): Readonly<Record<string, unknown>>;
  snapshotLane(laneId: string): Readonly<Record<string, unknown>>;
  snapshot(): Readonly<Record<string, unknown>>;
}
export function createCrossLaneScheduler(options?: Record<string, unknown>): CrossLaneScheduler;
export function validateCrossLaneSchedulerSnapshot(snapshot: Record<string, unknown>, options?: { requireSortedCompleted?: boolean }): Readonly<{ ok: boolean; errors: string[]; queuedCount: number; queuedCost: number; inFlightCount: number; laneCount: number; completedCount: number }>;


export class StorageLaneExecutor {
  constructor(config?: { label?: string; scheduler?: unknown; mailbox?: unknown; lane?: string; trace?: unknown; markUnhealthyOnError?: boolean });
  readonly label: string;
  readonly scheduler: unknown;
  readonly mailbox: unknown;
  readonly lane: string;
  submit(op: 'enqueue' | 'dequeue' | 'ack' | 'checkpoint' | 'compact' | 'snapshot', args?: Record<string, unknown>, options?: { id?: string; priority?: string; cost?: number; dependsOn?: string[]; fallbackLanes?: string[]; flowId?: string; metadata?: unknown }): Readonly<object>;
  executeNext(options?: { autoComplete?: boolean }): Promise<Readonly<object>>;
  executeDispatched(dispatched: object): Promise<Readonly<object>>;
  markHealthy(reason?: string): Readonly<object>;
  markUnhealthy(reason?: string): Readonly<object>;
  snapshot(): Readonly<object>;
}
export function createStorageLaneExecutor(config?: object): StorageLaneExecutor;
export function validateStorageLaneExecutorSnapshot(snapshot: Record<string, unknown>, options?: { requireMailbox?: boolean }): Readonly<{ ok: boolean; errors: string[]; pendingOperationCount: number; resultCount: number; queuedCount: number; inFlightCount: number; mailboxQueueDepth: number; mailboxPendingCount: number }>;
export const STORAGE_LANE_EXECUTOR_SUPPORTED_OPS: readonly string[];


export class StorageLaneRetryPolicy {
  constructor(config?: { maxAttempts?: number; initialDelayTicks?: number; multiplier?: number; maxDelayTicks?: number; jitterTicks?: number; jitterSeed?: number; retryableCodes?: string[]; nonRetryableCodes?: string[] });
  readonly maxAttempts: number;
  delayTicksForAttempt(attempt: number, id?: string): number;
  shouldRetry(input: { attempt: number; code?: string | null }): Readonly<{ retry: boolean; reason: string }>;
  snapshot(): Readonly<object>;
}
export class StorageLaneRetryController {
  constructor(config?: { label?: string; executor?: StorageLaneExecutor; policy?: StorageLaneRetryPolicy | Record<string, unknown>; retryBudget?: RetryBudgetAdmissionController | null; trace?: unknown });
  readonly label: string;
  readonly executor: StorageLaneExecutor;
  readonly policy: StorageLaneRetryPolicy;
  readonly nowTick: number;
  submitMailboxEnqueue(mailbox: unknown, payload: Uint8Array | ArrayBuffer | ArrayBufferView | string, options?: Record<string, unknown>): Readonly<object>;
  scheduleDueRetries(): number;
  drainReady(options?: { maxSteps?: number }): Promise<Readonly<object>>;
  advanceToNextRetry(): Readonly<object>;
  operation(id: string): Readonly<object> | null;
  snapshot(): Readonly<object>;
}
export function createStorageLaneRetryPolicy(config?: object): StorageLaneRetryPolicy;
export function createStorageLaneRetryController(config?: object): StorageLaneRetryController;

export class RetryBudgetAdmissionController {
  constructor(config?: { label?: string; maxRetryCredits?: number; initialRetryCredits?: number; refillPerPrimarySuccess?: number; refillPerPrimaryFailure?: number; maxActiveRetries?: number; minRetryCredits?: number; allowCriticalBypass?: boolean; requireIdempotent?: boolean; trace?: unknown });
  readonly label: string;
  readonly maxRetryCredits: number;
  readonly retryCredits: number;
  readonly maxActiveRetries: number;
  observePrimary(result?: { ok?: boolean; opId?: string; attempt?: number; kind?: string }): Readonly<object>;
  tryAcquireRetry(input?: { opId?: string; id?: string; attempt?: number; nextAttempt?: number; priority?: string; idempotent?: boolean; code?: string | null }): Readonly<object>;
  releaseRetry(leaseOrId: string | { leaseId?: string }, result?: { ok?: boolean; opId?: string; attempt?: number }): Readonly<object>;
  markProviderUnhealthy(reason?: string): void;
  markProviderHealthy(reason?: string): void;
  snapshot(): Readonly<object>;
}
export function createRetryBudgetAdmissionController(config?: object): RetryBudgetAdmissionController;
export function validateRetryBudgetAdmissionSnapshot(snapshot: Record<string, unknown>): Readonly<{ ok: boolean; errors: string[]; retryCredits: number; activeRetries: number; leaseCount: number }>;


export type CircuitBreakerBulkheadState = 'closed' | 'open' | 'half-open' | 'forced-open' | 'disabled' | 'metrics-only';
export class CircuitBreakerBulkheadController {
  constructor(config?: { label?: string; maxConcurrent?: number; slidingWindowSize?: number; minimumCalls?: number; failureRateThreshold?: number; slowCallRateThreshold?: number; slowCallDurationTicks?: number; openDurationTicks?: number; halfOpenMaxCalls?: number; countSlowCallsAsFailures?: boolean; trace?: unknown });
  readonly label: string;
  readonly maxConcurrent: number;
  readonly state: CircuitBreakerBulkheadState;
  readonly nowTick: number;
  tryAcquire(input?: { opId?: string; id?: string; priority?: string; kind?: string }): Readonly<object>;
  release(leaseOrId: string | { leaseId?: string }, result?: { ok?: boolean; durationTicks?: number }): Readonly<object>;
  advanceTicks(ticks?: number): Readonly<object>;
  forceOpen(reason?: string): Readonly<object>;
  close(reason?: string): Readonly<object>;
  snapshot(): Readonly<object>;
}
export function createCircuitBreakerBulkheadController(config?: object): CircuitBreakerBulkheadController;
export function validateCircuitBreakerBulkheadSnapshot(snapshot: Record<string, unknown>): Readonly<{ ok: boolean; errors: string[]; state: string | null; active: number; leaseCount: number; windowTotal: number }>;


export class ProviderResilienceHistoryRunner {
  constructor(config?: { label?: string; executor?: StorageLaneExecutor; mailbox?: PersistedSpillMailbox; breaker?: CircuitBreakerBulkheadController; retryBudget?: RetryBudgetAdmissionController; retryPolicy?: StorageLaneRetryPolicy | Record<string, unknown>; trace?: unknown });
  readonly label: string;
  readonly executor: StorageLaneExecutor;
  readonly mailbox: PersistedSpillMailbox;
  readonly breaker: CircuitBreakerBulkheadController;
  readonly retryBudget: RetryBudgetAdmissionController;
  readonly retryPolicy: StorageLaneRetryPolicy;
  runMailboxEnqueue(input?: { id?: string; payload?: Uint8Array | ArrayBuffer | ArrayBufferView | string; priority?: string; maxAttempts?: number; idempotent?: boolean; durationTicks?: number; lane?: string; fallbackLanes?: string[]; cost?: number; autoHealOnRetry?: boolean }): Promise<Readonly<object>>;
  history(): Array<Record<string, unknown>>;
  snapshot(): Readonly<object>;
}
export function createProviderResilienceHistoryRunner(config?: object): ProviderResilienceHistoryRunner;
export function validateProviderResilienceHistorySnapshot(snapshot: Record<string, unknown>): Readonly<{ ok: boolean; errors: string[]; executorValidation?: object; breakerValidation?: object; budgetValidation?: object }>;

export class ProviderResilienceModelOracle {
  constructor(config?: { provider?: Record<string, unknown>; breaker?: Record<string, unknown>; retryBudget?: Record<string, unknown>; retryPolicy?: Record<string, unknown> });
  runMailboxEnqueue(input?: { id?: string; payload?: Uint8Array | ArrayBuffer | ArrayBufferView | string; priority?: string; maxAttempts?: number; idempotent?: boolean; durationTicks?: number; autoHealOnRetry?: boolean }): Readonly<object>;
  snapshot(): Readonly<object>;
}
export function createProviderResilienceModelOracle(config?: object): ProviderResilienceModelOracle;
export function compareProviderResilienceHistoryToModel(realRows: Array<Record<string, unknown>>, modelRows: Array<Record<string, unknown>>): Readonly<{ ok: boolean; errors: string[]; compared: number }>;
export function validateProviderResilienceModelSnapshot(snapshot: Record<string, unknown>): Readonly<{ ok: boolean; errors: string[] }>;


export class StorageLaneAdmissionHistoryRunner {
  constructor(config?: { label?: string; admission?: WatermarkAdmissionController; resilienceRunner?: ProviderResilienceHistoryRunner; mailbox?: PersistedSpillMailbox; trace?: unknown });
  readonly label: string;
  readonly admission: WatermarkAdmissionController;
  readonly resilienceRunner: ProviderResilienceHistoryRunner;
  readonly mailbox: PersistedSpillMailbox;
  markAdmissionProviderUnhealthy(reason?: string): void;
  markAdmissionProviderHealthy(reason?: string): void;
  runMailboxEnqueue(input?: { id?: string; payload?: Uint8Array | ArrayBuffer | ArrayBufferView | string; priority?: string; bytes?: number; maxAttempts?: number; idempotent?: boolean; durationTicks?: number; lane?: string; fallbackLanes?: string[]; cost?: number; autoHealOnRetry?: boolean }): Promise<Readonly<object>>;
  history(): Array<Record<string, unknown>>;
  snapshot(): Readonly<object>;
}
export function createStorageLaneAdmissionHistoryRunner(config?: object): StorageLaneAdmissionHistoryRunner;
export function validateStorageLaneAdmissionHistorySnapshot(snapshot: Record<string, unknown>): Readonly<{ ok: boolean; errors: string[] }>;


export class StorageLaneAdmissionHistoryModelOracle {
  constructor(config?: { label?: string; lowWatermarkBytes?: number; highWatermarkBytes?: number; hardLimitBytes?: number; criticalMinPriority?: string; rejectMinPriorityWhileCongested?: string; trace?: unknown });
  readonly label: string;
  holdLease(input?: { bytes?: number; priority?: string; label?: string }): Readonly<object>;
  releaseHeld(leaseId: string, reason?: string): Readonly<object>;
  markProviderUnhealthy(reason?: string): void;
  markProviderHealthy(reason?: string): void;
  predictAdmission(input?: { bytes?: number; priority?: string; label?: string }): Readonly<object>;
  observeOperation(input?: Record<string, unknown>, row?: Record<string, unknown>, options?: { providerBlocksBefore?: number; providerBlocksAfter?: number; expectedFinal?: string }): Readonly<{ ok: boolean; errors: string[]; expected: object }>;
  snapshot(): Readonly<object>;
}
export function createStorageLaneAdmissionHistoryModelOracle(config?: object): StorageLaneAdmissionHistoryModelOracle;
export function compareStorageLaneAdmissionHistoryToModel(realSnapshot: Record<string, unknown>, modelSnapshot: Record<string, unknown>, options?: { providerSnapshot?: Record<string, unknown> }): Readonly<{ ok: boolean; errors: string[] }>;
export function validateStorageLaneAdmissionHistoryModelSnapshot(snapshot: Record<string, unknown>): Readonly<{ ok: boolean; errors: string[] }>;


export class StorageLaneOverloadGovernanceModelOracle {
  constructor(config?: { label?: string; trace?: TraceLog | null });
  label: string;
  stats: Record<string, number>;
  observeOperation(input?: Record<string, unknown>): Readonly<Record<string, unknown>>;
  observeSnapshot(input?: Record<string, unknown>): Readonly<Record<string, unknown>>;
  history(): Array<Record<string, unknown>>;
  snapshot(): Readonly<Record<string, unknown>>;
}
export function createStorageLaneOverloadGovernanceModelOracle(config?: Record<string, unknown>): StorageLaneOverloadGovernanceModelOracle;
export function validateStorageLaneOverloadGovernanceSnapshot(snapshot: Record<string, unknown>): Readonly<{ ok: boolean; errors: string[] }>;
export function compareStorageLaneOverloadGovernanceToRuntime(governanceSnapshot: Record<string, unknown>, runtimeSnapshot?: Record<string, unknown>): Readonly<{ ok: boolean; errors: string[]; stats: Record<string, unknown> }>;

export class OpfsBlockStoreStorageLaneAdapter {
  constructor(config?: { label?: string; store?: OpfsAsyncBlockStore; scheduler?: CrossLaneScheduler; executor?: StorageLaneExecutor; lane?: string; trace?: TraceLog | null; storeConfig?: Record<string, unknown>; schedulerConfig?: Record<string, unknown>; executorConfig?: Record<string, unknown> });
  readonly label: string;
  readonly lane: string;
  readonly store: OpfsAsyncBlockStore;
  readonly scheduler: CrossLaneScheduler;
  readonly executor: StorageLaneExecutor;
  stats: Record<string, number>;
  schedulePut(bytes: Uint8Array | ArrayBuffer | ArrayBufferView | string, options?: Record<string, unknown>): Readonly<object>;
  scheduleGet(refOrDigest: string | Record<string, unknown>, options?: Record<string, unknown>): Readonly<object>;
  scheduleHas(refOrDigest: string | Record<string, unknown>, options?: Record<string, unknown>): Readonly<object>;
  scheduleVerify(refOrDigest: string | Record<string, unknown>, options?: Record<string, unknown>): Readonly<object>;
  scheduleDelete(refOrDigest: string | Record<string, unknown>, options?: Record<string, unknown>): Readonly<object>;
  scheduleEstimate(options?: Record<string, unknown>): Readonly<object>;
  scheduleCleanupForTest(options?: Record<string, unknown>): Readonly<object>;
  executeNext(): Promise<Readonly<object>>;
  drain(options?: { maxSteps?: number }): Promise<Readonly<object>>;
  result(opId: string): unknown;
  snapshot(): Readonly<object>;
}
export function createOpfsBlockStoreStorageLaneAdapter(config?: Record<string, unknown>): OpfsBlockStoreStorageLaneAdapter;
export function validateOpfsStorageLaneAdapterSnapshot(snapshot: Record<string, unknown>): Readonly<{ ok: boolean; errors: string[] }>;
export const OPFS_STORAGE_LANE_ADAPTER_SUPPORTED_OPS: ReadonlyArray<string>;


export class BlockStoreLaneAdapter {
  constructor(config?: { label?: string; store?: unknown; executor?: StorageLaneExecutor; scheduler?: CrossLaneScheduler; lane?: string; trace?: TraceLog | null; markUnhealthyOnError?: boolean });
  readonly label: string;
  readonly lane: string;
  readonly store: unknown;
  readonly executor: StorageLaneExecutor;
  readonly scheduler: CrossLaneScheduler;
  schedulePut(bytes: Uint8Array | ArrayBuffer | ArrayBufferView | string, options?: Record<string, unknown>): Readonly<object>;
  scheduleGet(refOrDigest: string | Record<string, unknown>, options?: Record<string, unknown>): Readonly<object>;
  scheduleHas(refOrDigest: string | Record<string, unknown>, options?: Record<string, unknown>): Readonly<object>;
  scheduleVerify(refOrDigest: string | Record<string, unknown>, options?: Record<string, unknown>): Readonly<object>;
  scheduleDelete(refOrDigest: string | Record<string, unknown>, options?: Record<string, unknown>): Readonly<object>;
  scheduleEstimate(options?: Record<string, unknown>): Readonly<object>;
  scheduleCleanupForTest(options?: Record<string, unknown>): Readonly<object>;
  executeNext(): Promise<Readonly<object>>;
  drain(options?: { maxSteps?: number }): Promise<Readonly<object>>;
  result(opId: string): unknown;
  snapshot(): Readonly<object>;
}
export function createBlockStoreLaneAdapter(config?: Record<string, unknown>): BlockStoreLaneAdapter;
export function validateBlockStoreLaneAdapterSnapshot(snapshot: Record<string, unknown>): Readonly<{ ok: boolean; errors: string[]; resultCount: number }>;
export const BLOCK_STORE_LANE_ADAPTER_OPS: ReadonlyArray<string>;

export type DreamBoundaryCategory = 'earned-in-cloudtainer' | 'buildable-in-cloudtainer' | 'smoke-testable-in-cloudtainer' | 'needs-external-evidence' | 'shelf-until-repeated-container-evidence';
export type DreamBoundaryArea = 'kernel' | 'storage' | 'ipc' | 'scheduler' | 'mesh' | 'accelerators' | 'network' | 'plugins' | 'devtools' | 'apps';
export type DreamBoundaryAmbition = Readonly<{ id: string; area: DreamBoundaryArea; category: DreamBoundaryCategory; dream: string; nearProof: string; shelfRule: string }>;
export type DreamBoundaryMap = Readonly<{ schema: number; title: string; posture: string; ambitions: ReadonlyArray<DreamBoundaryAmbition>; unshelfPolicy: Readonly<Record<string, unknown>> }>;
export const DREAM_BOUNDARY_CATEGORIES: ReadonlyArray<DreamBoundaryCategory>;
export const DREAM_BOUNDARY_AREAS: ReadonlyArray<DreamBoundaryArea>;
export function createDreamBoundaryMap(): DreamBoundaryMap;
export function validateDreamBoundaryMap(map?: DreamBoundaryMap): Readonly<{ ok: boolean; errors: string[] }>;

export type ProjectAssessmentPosture = 'continue' | 'narrow-first-wedge' | 'pause' | 'kill' | 'external-evidence-required';
export type ProjectAssessmentAudience =
  | 'browser-heavy-app-builders'
  | 'local-first-tool-builders'
  | 'data-and-media-web-apps'
  | 'browser-ide-and-agent-tool-builders'
  | 'library-authors-needing-runtime-substrate'
  | 'teams-needing-cloud-cost-or-privacy-reduction';
export type ProjectContinuationAssessment = Readonly<{
  schema: number;
  revision: string;
  codename: string;
  verdict: string;
  decision: Readonly<Record<string, unknown>>;
  beneficiaries: ReadonlyArray<Record<string, unknown>>;
  nonBeneficiaries: ReadonlyArray<string>;
  competitionMap: ReadonlyArray<Record<string, unknown>>;
  continuationGates: ReadonlyArray<string>;
  killConditions: ReadonlyArray<string>;
  externalEvidenceNeeded: ReadonlyArray<string>;
  recommendedNextWedge: Readonly<Record<string, unknown>>;
  requiredNonClaims: ReadonlyArray<string>;
}>;
export const PROJECT_ASSESSMENT_AUDIENCES: ReadonlyArray<ProjectAssessmentAudience>;
export const PROJECT_ASSESSMENT_POSTURES: ReadonlyArray<ProjectAssessmentPosture>;
export function createProjectContinuationAssessment(): ProjectContinuationAssessment;
export function validateProjectContinuationAssessment(assessment?: ProjectContinuationAssessment): Readonly<{ ok: boolean; errors: string[] }>;

export type KernelKitDemoPlan = Readonly<{
  project: 'BrowserRT';
  revision: string;
  schema: number;
  codename: string;
  posture: string;
  purpose: string;
  audience: readonly string[];
  components: readonly string[];
  steps: readonly { id: string; order: number; label?: string }[];
  requiredTraceKinds: readonly string[];
  releasePosture: string;
  successShape: Readonly<Record<string, string>>;
  nonClaims: readonly string[];
}>;


export type KernelKitDemoTranscript = Readonly<{
  project: 'BrowserRT';
  revision: string;
  schema: number;
  transcriptId: string;
  status: string;
  stageCount: number;
  passedCount: number;
  missingStageIds: readonly string[];
  stages: readonly Readonly<{ id: string; order: number; label: string; status: string }>[];
  traceKindCount: number;
  nonClaims: readonly string[];
}>;

export type KernelKitDemoProofValidation = Readonly<{
  ok: boolean;
  errors: string[];
  stepCount?: number;
  traceKindCount?: number;
  nonClaimCount?: number;
  componentCount?: number;
  traceCount?: number;
}>;

export declare const KERNEL_KIT_DEMO_CODENAME: string;
export declare const KERNEL_KIT_DEMO_STEPS: readonly string[];
export declare const KERNEL_KIT_DEMO_REQUIRED_STEPS: readonly string[];
export declare const KERNEL_KIT_DEMO_STAGE_LABELS: Readonly<Record<string, string>>;
export declare const KERNEL_KIT_DEMO_REQUIRED_TRACE_KINDS: readonly string[];
export declare const KERNEL_KIT_DEMO_NON_CLAIMS: readonly string[];


export type KernelKitDemoHandoff = Readonly<{
  project: 'BrowserRT';
  revision: string;
  schema: number;
  handoffId: string;
  storageKey: string;
  prefix: string;
  ref: Record<string, unknown>;
  expectedDigest: string;
  storageRefDigest: string;
  payloadBytes: number;
  stageReceipt: KernelKitDemoTranscript;
  savedAt: string;
  purpose: string;
  nonClaims: readonly string[];
}>;

export type KernelKitTraceExport = Readonly<{
  project: 'BrowserRT';
  revision: string;
  schema: number;
  format: 'browserrt-kernel-kit-trace-export-v1';
  exportId: string;
  browserRtReceipt: Readonly<Record<string, unknown>>;
  chromeTrace: Readonly<{ traceEvents: readonly Record<string, unknown>[]; displayTimeUnit: string; metadata: Readonly<Record<string, unknown>> }>;
  otelSketch: Readonly<Record<string, unknown>>;
  nonClaims: readonly string[];
}>;

export declare function createKernelKitDemoPlan(fields?: Record<string, unknown>): KernelKitDemoPlan;
export declare function validateKernelKitDemoPlan(plan?: KernelKitDemoPlan): KernelKitDemoProofValidation;
export declare function validateKernelKitDemoProof(report: Record<string, unknown>): KernelKitDemoProofValidation;
export declare function createKernelKitDemoTranscript(report?: Record<string, unknown>): KernelKitDemoTranscript;
export declare function validateKernelKitDemoTranscript(transcript?: Record<string, unknown>): KernelKitDemoProofValidation;
export declare function summarizeKernelKitDemoTrace(traceKindsOrEvents?: readonly unknown[]): Readonly<Record<string, unknown>>;
export declare function scoreKernelKitDemoUsefulness(report?: Record<string, unknown>): Readonly<Record<string, unknown>>;
export declare function validateKernelKitDemoReport(report: Record<string, unknown>): KernelKitDemoProofValidation;
export declare function createKernelKitDemoHandoff(report?: Record<string, unknown>, fields?: Record<string, unknown>): KernelKitDemoHandoff;
export declare function validateKernelKitDemoHandoff(handoff: Record<string, unknown>): KernelKitDemoProofValidation & Readonly<{ requiredKeyCount: number }>;
export declare const KERNEL_KIT_DEMO_HANDOFF_STORAGE_KEY: string;
export declare const KERNEL_KIT_DEMO_HANDOFF_REQUIRED_KEYS: readonly string[];
export declare function createKernelKitTraceExport(report?: Record<string, unknown>, fields?: Record<string, unknown>): KernelKitTraceExport;
export declare function validateKernelKitTraceExport(exportReport: Record<string, unknown>): KernelKitDemoProofValidation & Readonly<{ traceEventCount: number; stageCount: number; formatCount: number }>;
export declare const KERNEL_KIT_DEMO_EXPORT_FORMATS: readonly string[];
export declare const KERNEL_KIT_DEMO_EXPORT_NON_CLAIMS: readonly string[];
export declare const KERNEL_KIT_DEMO_FAILURE_MODES: readonly string[];
export declare const KERNEL_KIT_DEMO_EXPORT_BUNDLE_FORMAT: string;
export declare const KERNEL_KIT_DEMO_EXPORT_BUNDLE_NON_CLAIMS: readonly string[];
export type KernelKitDemoExportBundle = Readonly<Record<string, unknown>>;
export type KernelKitFailureModeReport = Readonly<Record<string, unknown>>;
export declare function createKernelKitDemoExportBundle(report?: Record<string, unknown>, fields?: Record<string, unknown>): KernelKitDemoExportBundle;
export declare function validateKernelKitDemoExportBundle(bundle: Record<string, unknown>): KernelKitDemoProofValidation & Readonly<{ format: string | null; failureMode: string | null; traceEventCount: number; transcriptStatus: string | null }>;
export declare function createKernelKitFailureModeReport(fields?: Record<string, unknown>): KernelKitFailureModeReport;
export declare function validateKernelKitFailureModeReport(report: Record<string, unknown>): KernelKitDemoProofValidation & Readonly<{ mode: string | null }>;

export type KernelKitTraceComparison = Readonly<Record<string, unknown>>;
export declare const KERNEL_KIT_TRACE_COMPARISON_FORMAT: string;
export declare const KERNEL_KIT_TRACE_COMPARISON_NON_CLAIMS: readonly string[];
export declare function createKernelKitTraceComparison(successReport?: Record<string, unknown>, failureReport?: Record<string, unknown>, fields?: Record<string, unknown>): KernelKitTraceComparison;
export declare function validateKernelKitTraceComparison(comparison?: Record<string, unknown>): KernelKitDemoProofValidation & Readonly<{ stageRowCount: number; successOnlyTraceKindCount: number; failureOnlyTraceKindCount: number }>;

export type KernelKitDiagnosticRunbook = Readonly<Record<string, unknown>>;
export declare const KERNEL_KIT_DIAGNOSTIC_RUNBOOK_FORMAT: string;
export declare const KERNEL_KIT_DIAGNOSTIC_RUNBOOK_NON_CLAIMS: readonly string[];
export declare function createKernelKitDiagnosticRunbook(comparison?: Record<string, unknown>, fields?: Record<string, unknown>): KernelKitDiagnosticRunbook;
export declare function validateKernelKitDiagnosticRunbook(runbook?: Record<string, unknown>): KernelKitDemoProofValidation & Readonly<{ cardCount: number; commandCount: number }>;

export type KernelKitSupportBundle = Readonly<Record<string, unknown>>;
export declare const KERNEL_KIT_SUPPORT_BUNDLE_FORMAT: string;
export declare const KERNEL_KIT_SUPPORT_BUNDLE_NON_CLAIMS: readonly string[];
export declare function createKernelKitSupportBundle(fields?: Record<string, unknown>): KernelKitSupportBundle;
export declare function validateKernelKitSupportBundle(bundle?: Record<string, unknown>): KernelKitDemoProofValidation & Readonly<{ sectionCount: number; commandCount: number; format: string | null }>;
export type KernelKitSupportBundleImportReport = Readonly<Record<string, unknown>>;
export declare const KERNEL_KIT_SUPPORT_BUNDLE_IMPORT_FORMAT: string;
export declare const KERNEL_KIT_SUPPORT_BUNDLE_IMPORT_NON_CLAIMS: readonly string[];
export declare function createKernelKitSupportBundleImportReport(candidate?: string | Record<string, unknown>, fields?: Record<string, unknown>): KernelKitSupportBundleImportReport;
export declare function validateKernelKitSupportBundleImportReport(report?: Record<string, unknown>): KernelKitDemoProofValidation & Readonly<{ riskCount: number; commandCount: number; format: string | null }>;



export type KernelKitSupportBundleDiff = Readonly<Record<string, unknown>>;
export declare const KERNEL_KIT_SUPPORT_BUNDLE_DIFF_FORMAT: string;
export declare const KERNEL_KIT_SUPPORT_BUNDLE_DIFF_NON_CLAIMS: readonly string[];
export declare function createKernelKitSupportBundleDiff(current?: string | Record<string, unknown>, candidate?: string | Record<string, unknown>, fields?: Record<string, unknown>): KernelKitSupportBundleDiff;
export declare function validateKernelKitSupportBundleDiff(diff?: Record<string, unknown>): KernelKitDemoProofValidation & Readonly<{ riskCount: number; proofRowCount: number; format: string | null; status: string | null }>;

export type KernelKitGuidedTourReceipt = Readonly<Record<string, unknown>>;
export declare const KERNEL_KIT_GUIDED_TOUR_FORMAT: string;
export declare const KERNEL_KIT_GUIDED_TOUR_STEPS: readonly string[];
export declare const KERNEL_KIT_GUIDED_TOUR_NON_CLAIMS: readonly string[];
export declare function createKernelKitGuidedTourReceipt(fields?: Record<string, unknown>): KernelKitGuidedTourReceipt;
export declare function validateKernelKitGuidedTourReceipt(receipt?: Record<string, unknown>): KernelKitDemoProofValidation & Readonly<{ stepCount: number; passedCount: number; format: string | null }>;


export type KernelKitHandoffMarkdown = Readonly<Record<string, unknown>>;
export declare const KERNEL_KIT_HANDOFF_MARKDOWN_FORMAT: string;
export declare const KERNEL_KIT_HANDOFF_MARKDOWN_NON_CLAIMS: readonly string[];
export declare function createKernelKitHandoffMarkdown(fields?: Record<string, unknown>): KernelKitHandoffMarkdown;
export declare function validateKernelKitHandoffMarkdown(report?: Record<string, unknown>): KernelKitDemoProofValidation & Readonly<{ commandCount: number; markdownBytes: number; sectionCount: number; status: string | null; format: string | null }>;
// Runtime convenience method marker: kernelKitHandoffMarkdown / validateKernelKitHandoffMarkdown.

export type KernelKitHandoffMarkdownImportReport = Readonly<Record<string, unknown>>;
export declare const KERNEL_KIT_HANDOFF_MARKDOWN_IMPORT_FORMAT: string;
export declare const KERNEL_KIT_HANDOFF_MARKDOWN_IMPORT_NON_CLAIMS: readonly string[];
export declare const KERNEL_KIT_HANDOFF_MARKDOWN_REQUIRED_COMMANDS: readonly string[];
export declare function createKernelKitHandoffMarkdownImportReport(input?: string | Record<string, unknown>, fields?: Record<string, unknown>): KernelKitHandoffMarkdownImportReport;
export declare function validateKernelKitHandoffMarkdownImportReport(report?: Record<string, unknown>): KernelKitDemoProofValidation & Readonly<{ commandCount: number; parsedCommandCount: number; riskCount: number; sectionCount: number; markdownBytes: number; status: string | null; format: string | null }>;
// Runtime convenience method marker: kernelKitHandoffMarkdownImport / validateKernelKitHandoffMarkdownImportReport.


export type KernelKitDemoObservatoryReport = Readonly<{
  project: 'BrowserRT';
  revision: string;
  schema: number;
  codename: string;
  mission: string;
  sections: readonly string[];
  sourceProofId: string;
  capabilityBadges: readonly Readonly<{ id: string; label: string; status: string }>[];
  stageCards: readonly Readonly<{ order: number; id: string; title: string; lane: string; status: string; proofKeys: readonly string[]; traceHits: readonly string[]; requiredTraceKinds: readonly string[] }>[];
  laneTimeline: Readonly<{ rows: readonly Record<string, unknown>[]; laneCounts: Record<string, number>; eventCount: number }>;
  traceSummary: Readonly<{ eventCount: number; uniqueKindCount: number; kinds: readonly string[]; countsByKind: Record<string, number>; countsByLane: Record<string, number> }>;
  proofReceipt: Readonly<Record<string, unknown>>;
  nextDemoWork: readonly string[];
  nonClaims: readonly string[];
}>;
export declare const KERNEL_KIT_OBSERVATORY_CODENAME: string;
export declare const KERNEL_KIT_OBSERVATORY_REQUIRED_SECTIONS: readonly string[];
export declare const KERNEL_KIT_OBSERVATORY_NON_CLAIMS: readonly string[];
export declare function createKernelKitDemoObservatoryReport(report: Record<string, unknown>, fields?: Record<string, unknown>): KernelKitDemoObservatoryReport;
export declare function validateKernelKitDemoObservatoryReport(report: Record<string, unknown>): Readonly<{ ok: boolean; errors: string[]; observedStageCount: number; traceKindCount: number; badgeCount?: number }>;

export type KernelKitDemoUsefulnessWorkflow = Readonly<{
  id: string;
  title: string;
  lane: string;
  beneficiaryPain: string;
  status: string;
  evidenceKeys: readonly string[];
  evidenceHits: readonly string[];
  requiredTraceKinds: readonly string[];
  traceHits: readonly string[];
}>;
export type KernelKitDemoUsefulnessReport = Readonly<{
  project: 'BrowserRT';
  revision: string;
  schema: number;
  codename: string;
  purpose: string;
  sourceProofId: string;
  status: string;
  sections: readonly string[];
  beneficiaryFit: readonly Readonly<Record<string, unknown>>[];
  strongBeneficiaries: readonly string[];
  workflowScorecard: readonly KernelKitDemoUsefulnessWorkflow[];
  earnedEvidence: readonly string[];
  missingEvidence: readonly string[];
  acceptanceGate: Readonly<Record<string, unknown>>;
  transcript: Readonly<Record<string, unknown>>;
  traceSummary: Readonly<Record<string, unknown>>;
  usefulnessScore: Readonly<Record<string, unknown>>;
  nonClaims: readonly string[];
}>;
export declare const KERNEL_KIT_USEFULNESS_CODENAME: string;
export declare const KERNEL_KIT_USEFULNESS_REQUIRED_SECTIONS: readonly string[];
export declare const KERNEL_KIT_USEFULNESS_AUDIENCES: readonly string[];
export declare const KERNEL_KIT_USEFULNESS_NON_CLAIMS: readonly string[];
export declare function createKernelKitDemoUsefulnessReport(report?: Record<string, unknown>, fields?: Record<string, unknown>): KernelKitDemoUsefulnessReport;
export declare function validateKernelKitDemoUsefulnessReport(report?: Record<string, unknown>): Readonly<{ ok: boolean; errors: string[]; earnedWorkflowCount: number; strongBeneficiaryCount: number }>;

// Runtime convenience method marker: kernelKitTraceComparison / kernelKitDiagnosticRunbook / kernelKitSupportBundle / kernelKitGuidedTourReceipt.
// Runtime convenience method marker: kernelKitSupportBundleImportReport / validateKernelKitSupportBundleImportReport / kernelKitSupportBundleDiff / validateKernelKitSupportBundleDiff.

export type KernelKitReadinessGate = Readonly<Record<string, unknown>>;
export declare const KERNEL_KIT_READINESS_GATE_FORMAT: string;
export declare const KERNEL_KIT_READINESS_GATE_NON_CLAIMS: readonly string[];
export declare const KERNEL_KIT_READINESS_GATE_REQUIRED_GATES: readonly string[];
export declare const KERNEL_KIT_READINESS_GATE_PERSONAS: readonly string[];
export declare function createKernelKitReadinessGate(fields?: Record<string, unknown>): KernelKitReadinessGate;
export declare function validateKernelKitReadinessGate(report?: Record<string, unknown>): KernelKitDemoProofValidation & Readonly<{ gateCount: number; personaCount: number; commandCount: number; status: string | null; format: string | null }>;
// Runtime convenience method marker: kernelKitReadinessGate / validateKernelKitReadinessGate.


export type KernelKitReadinessContrast = Readonly<Record<string, unknown>>;
export declare const KERNEL_KIT_READINESS_CONTRAST_FORMAT: string;
export declare const KERNEL_KIT_READINESS_CONTRAST_NON_CLAIMS: readonly string[];
export declare const KERNEL_KIT_READINESS_CONTRAST_DEFAULT_FAILED_GATES: readonly string[];
export declare function createDegradedKernelKitReadinessGate(readinessGate?: Record<string, unknown>, fields?: Record<string, unknown>): KernelKitReadinessGate;
export declare function createKernelKitReadinessContrast(fields?: Record<string, unknown>): KernelKitReadinessContrast;
export declare function validateKernelKitReadinessContrast(report?: Record<string, unknown>): KernelKitDemoProofValidation & Readonly<{ changedGateCount: number; missingGateCount: number; commandCount: number; status: string | null; format: string | null }>;
// Runtime convenience method marker: kernelKitReadinessContrast / validateKernelKitReadinessContrast.
