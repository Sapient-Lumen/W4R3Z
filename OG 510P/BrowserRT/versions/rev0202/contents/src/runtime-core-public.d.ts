export const VERSION: '0.0.125';
export const REVISION: 'rev0125';
export const BROWSERRT_RUNTIME_CORE_ENTRY_FORMAT: 'browserrt.runtime-core-entry.v1';
export const BROWSERRT_RUNTIME_CORE_EXPORTS: readonly string[];
export const BROWSERRT_BROWSER_STORAGE_POSTURE_FORMAT: string;
export const BROWSERRT_BROWSER_STORAGE_RECOVERY_GUIDANCE_FORMAT: string;
export interface TraceEvent { readonly kind: string; readonly seq: number; readonly t: number; readonly [key: string]: unknown; }
export class TraceLog {
  constructor(options?: { capacity?: number });
  readonly capacity: number;
  readonly droppedCount: number;
  emit(kind: string, detail?: Record<string, unknown>): TraceEvent;
  snapshot(): TraceEvent[];
  find(kind: string): TraceEvent[];
  count(kind: string): number;
  kinds(): string[];
}
export interface BrowserRtObjectRef { readonly kind: string; readonly id: string; readonly bytes: number; readonly ownership: string; readonly createdAt: number; readonly [key: string]: unknown; }
export interface BrowserRtBlockRef extends BrowserRtObjectRef { readonly digest: string; readonly hash: string; readonly algorithm: 'sha256'; readonly backend: string; }
export interface BrowserRtEnvelope { readonly magic: 'BRT1'; readonly version: 1; readonly id: string; readonly op: string; readonly lane: string; readonly priority: string; readonly [key: string]: unknown; }
export interface BrowserRtMemoryBlockStore {
  readonly name?: string;
  readonly provider?: string;
  put(value: unknown, fields?: Record<string, unknown>): Promise<Readonly<Record<string, unknown>>>;
  get(refOrDigest: unknown, options?: Record<string, unknown>): Promise<Uint8Array>;
  has(refOrDigest: unknown, options?: Record<string, unknown>): Promise<boolean>;
  verify(refOrDigest: unknown, options?: Record<string, unknown>): Promise<Readonly<Record<string, unknown>>>;
  delete(refOrDigest: unknown, options?: Record<string, unknown>): Promise<Readonly<Record<string, unknown>>>;
  estimate(options?: Record<string, unknown>): Readonly<Record<string, unknown>>;
  snapshot(options?: Record<string, unknown>): Readonly<Record<string, unknown>>;
  cleanupForTest(options?: Record<string, unknown>): Promise<Readonly<Record<string, unknown>>>;
}
export interface BrowserRtCrossLaneScheduler {
  enqueue(task?: Record<string, unknown>): Readonly<Record<string, unknown>>;
  dispatchNext(options?: Record<string, unknown>): Readonly<Record<string, unknown>>;
  complete(taskId: string, options?: Record<string, unknown>): Readonly<Record<string, unknown>>;
  cancelQueued(taskId: string, options?: Record<string, unknown>): Readonly<Record<string, unknown>>;
  snapshot(): Readonly<Record<string, unknown>>;
}
export interface BrowserRtBlockStoreLaneAdapter {
  readonly closed: boolean;
  schedule(kind: string, run: (...args: unknown[]) => unknown, options?: Record<string, unknown>): Readonly<Record<string, unknown>>;
  schedulePut(payload: unknown, options?: Record<string, unknown>): Readonly<Record<string, unknown>>;
  scheduleGet(ref: unknown, options?: Record<string, unknown>): Readonly<Record<string, unknown>>;
  scheduleHas(ref: unknown, options?: Record<string, unknown>): Readonly<Record<string, unknown>>;
  scheduleVerify(ref: unknown, options?: Record<string, unknown>): Readonly<Record<string, unknown>>;
  scheduleDelete(ref: unknown, options?: Record<string, unknown>): Readonly<Record<string, unknown>>;
  scheduleEstimate(options?: Record<string, unknown>): Readonly<Record<string, unknown>>;
  scheduleSnapshot(options?: Record<string, unknown>): Readonly<Record<string, unknown>>;
  scheduleCleanupForTest(options?: Record<string, unknown>): Readonly<Record<string, unknown>>;
  submit(op: string, args?: Record<string, unknown>, options?: Record<string, unknown>): Readonly<Record<string, unknown>>;
  result(opId: string): unknown;
  error(opId: string): unknown;
  dispatchOne(context?: Record<string, unknown>): Promise<Readonly<Record<string, unknown>>>;
  drain(options?: Record<string, unknown>): Promise<Readonly<Record<string, unknown>>>;
  close(reason?: string): Readonly<Record<string, unknown>>;
  snapshot(): Readonly<Record<string, unknown>>;
}
export interface BrowserRtRuntimeCore {
  readonly revision: typeof REVISION;
  readonly version: typeof VERSION;
  readonly entry: typeof BROWSERRT_RUNTIME_CORE_ENTRY_FORMAT;
  readonly trace: TraceLog;
  readonly capabilities: Readonly<Record<string, unknown>>;
  readonly core: Readonly<{
    channel(config?: Record<string, unknown>): { send(value: unknown): Promise<Readonly<Record<string, unknown>>>; receive(): Promise<unknown>; close(): void; snapshot(): Readonly<Record<string, unknown>> };
    transferObject(buffer: ArrayBuffer, fields?: Record<string, unknown>): Readonly<{ ref: BrowserRtObjectRef; buffer: ArrayBuffer; transferList: ArrayBuffer[] }>;
    objectRef(kind: string, fields?: Record<string, unknown>): BrowserRtObjectRef;
    blockRef(hash: string, fields?: Record<string, unknown>): BrowserRtBlockRef;
    envelope(op: string, fields?: Record<string, unknown>): BrowserRtEnvelope;
  }>;
  readonly storage: Readonly<{
    blockStore(config?: Record<string, unknown>): BrowserRtMemoryBlockStore;
    blockStoreLaneAdapter(config?: Record<string, unknown>): BrowserRtBlockStoreLaneAdapter;
    browserStoragePosture(config?: Record<string, unknown>): Promise<Readonly<Record<string, unknown>>>;
    browserStorageRecoveryGuidance(error: unknown, context?: Record<string, unknown>): Readonly<Record<string, unknown>>;
  }>;
  readonly coordination: Readonly<{
    admissionController(config?: Record<string, unknown>): Record<string, unknown>;
    crossLaneScheduler(config?: Record<string, unknown>): BrowserRtCrossLaneScheduler;
  }>;
  close(reason?: string): TraceEvent[];
}
export function detectCapabilities(g?: unknown): Readonly<Record<string, unknown>>;
export function availableCapabilityTierNames(capabilities?: Readonly<Record<string, unknown>>): string[];
export function createObjectRef(kind: string, fields?: Record<string, unknown>): BrowserRtObjectRef;
export function createTransferObjectRef(buffer: ArrayBuffer, fields?: Record<string, unknown>): BrowserRtObjectRef;
export function createTransferObject(buffer: ArrayBuffer, fields?: Record<string, unknown>): Readonly<{ ref: BrowserRtObjectRef; buffer: ArrayBuffer; transferList: ArrayBuffer[] }>;
export function createBlockObjectRef(hash: string, fields?: Record<string, unknown>): BrowserRtBlockRef;
export function createEnvelope(op: string, fields?: Record<string, unknown>): BrowserRtEnvelope;
export function digestBytesHex(bytes: ArrayBuffer | ArrayBufferView | string | unknown): Promise<string>;
export function createMemoryBlockStore(config?: Record<string, unknown>): BrowserRtMemoryBlockStore;
export function diagnoseBrowserStoragePosture(config?: Record<string, unknown>): Promise<Readonly<Record<string, unknown>>>;
export function createBrowserStorageRecoveryGuidance(error: unknown, context?: Record<string, unknown>): Readonly<Record<string, unknown>>;
export function validateBlockStoreLaneAdapterSnapshot(snapshot: unknown): Readonly<{ ok: boolean; errors: string[] }>;
export function bootRuntimeCore(options?: Record<string, unknown>): BrowserRtRuntimeCore;
export const boot: typeof bootRuntimeCore;
