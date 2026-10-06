export const VERSION: '0.0.5';
export const REVISION: 'rev0005';

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
export type RtObjectRefKind = 'inline' | 'transfer' | 'shared' | 'opfs' | 'stream' | 'gpu';
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

export interface RtTransferObject {
  ref: RtObjectRef & { kind: 'transfer'; transferType: 'ArrayBuffer' };
  buffer: ArrayBuffer;
  transferList: ArrayBuffer[];
}

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
  revision: 'rev0005';
  version: '0.0.5';
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
export function createTransferObjectRef(buffer: ArrayBuffer, fields?: Record<string, unknown>): RtObjectRef;
export function createTransferObject(buffer: ArrayBuffer, fields?: Record<string, unknown>): RtTransferObject;
export function createEnvelope(op: string, fields?: Partial<RtEnvelope>): RtEnvelope;
export function spawnWorkerAgent(config?: { workerURL?: URL | string; name?: string; trace?: TraceLog; workerOptions?: Record<string, unknown> }): Promise<WorkerAgent>;
export function createSupervisor(config?: { name?: string; workerURL?: URL | string; trace?: TraceLog; restartLimit?: number }): Supervisor;
export function createBootReport(config?: { capabilities?: RtCapabilities; options?: Record<string, unknown> }): RtBootReport;
export function boot(options?: Record<string, unknown>): Promise<Readonly<{
  version: '0.0.5';
  revision: 'rev0005';
  options: Readonly<Record<string, unknown>>;
  capabilities: RtCapabilities;
  report: RtBootReport;
  trace: TraceLog;
  channel<T = unknown>(config?: { capacity?: number; overflow?: RtOverflow; label?: string }): BoundedChannel<T>;
  objectRef(kind: RtObjectRefKind, fields?: Record<string, unknown>): RtObjectRef;
  transferObject(buffer: ArrayBuffer, fields?: Record<string, unknown>): RtTransferObject;
  spawnAgent(config?: { workerURL?: URL | string; name?: string; trace?: TraceLog; workerOptions?: Record<string, unknown> }): Promise<WorkerAgent>;
  supervisor(config?: { name?: string; workerURL?: URL | string; trace?: TraceLog; restartLimit?: number }): Supervisor;
  close(): RtTraceEvent[];
}>>;
