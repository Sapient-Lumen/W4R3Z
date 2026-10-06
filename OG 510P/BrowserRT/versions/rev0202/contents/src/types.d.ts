export const VERSION: '0.0.125';
export const REVISION: 'rev0125';
// Deep-audit runtime needles retained after rev0189 comment compaction: lane-wide receipts are lane-scoped; lane-wide timeout-quarantine clearance receipts are lane-scoped; receipt lane must be present; rev0086; restore registration gate fails closed; same visible opId; operationEpoch; rejected-cleared-quarantine-row-replay-downgrade. rejected-clearance-receipt-block-integrity; rejected-cleared-quarantine-replay. timed-out-operation-late-success; late-success-clear-review-required; late-success-clear-scope-required; rejected-timed-out-operation-quarantine.
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
storagePersisted: boolean;
storagePersist: boolean;
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
repairedCorrupt?: boolean;
repair?: unknown;
}
export type RtOpfsBlockStoreErrorCode =
| 'BRT_OPFS_QUOTA_EXCEEDED'
| 'BRT_OPFS_BLOCK_CHECKSUM_MISMATCH'
| 'BRT_OPFS_SECURITY_ERROR'
| 'BRT_OPFS_INVALID_STATE'
| 'BRT_OPFS_OPERATION_ABORTED'
| 'BRT_OPFS_ABORT_SIGNAL_INVALID'
| 'BRT_OPFS_WRITE_BUDGET_EXCEEDED'
| 'BRT_OPFS_WRITE_BUDGET_INVALID'
| 'BRT_OPFS_ESTIMATE_UNAVAILABLE'
| 'BRT_OPFS_STORE_CLOSED'
| 'BRT_OPFS_WEB_LOCK_GUARD_CLOSED'
| 'BRT_OPFS_STAGED_WRITE_VERIFY_FAILED'
| 'BRT_OPFS_STAGED_RECOVERY_FAILED'
| 'BRT_OPFS_STAGED_RECOVERY_INVALID'
| 'BRT_OPFS_DIRECTORY_ITERATION_UNAVAILABLE'
| 'BRT_OPFS_OPERATION_FAILED';
export type RtWebLockErrorCode =
| 'BRT_WEB_LOCK_TIMEOUT'
| 'BRT_WEB_LOCK_ABORTED'
| 'BRT_WEB_LOCKS_UNAVAILABLE'
| 'BRT_WEB_LOCK_SIGNAL_OPTION_CONFLICT';
export interface RtOpfsClassifiedError {
code: RtOpfsBlockStoreErrorCode | string;
name: string;
message: string;
domCode: number | null;
context: Readonly<Record<string, unknown>>;
}
export function classifyOpfsBlockStoreError(error: unknown, context?: Record<string, unknown>): Readonly<RtOpfsClassifiedError>;
export interface RtOpfsWriteBudgetGuard {
enabled?: boolean;
minFreeBytes?: number;
reserveBytes?: number;
minAvailableBytes?: number;
maxUsageRatio?: number;
maxProjectedUsageRatio?: number;
requireEstimate?: boolean;
requireStorageEstimate?: boolean;
transientWriteMultiplier?: number;
stagedWriteMultiplier?: number;
transientUsageMultiplier?: number;
transientOverheadBytes?: number;
stagedWriteOverheadBytes?: number;
accountForStagedWrites?: boolean;
source?: string;
policySource?: string | null;
}
export interface RtOpfsOperationOptions {
signal?: AbortSignal | null;
abortSignal?: AbortSignal | null;
}
export interface RtOpfsPutOptions extends RtOpfsOperationOptions {
writeBudgetGuard?: boolean | RtOpfsWriteBudgetGuard | null;
minFreeBytesForPut?: number;
maxUsageRatioForPut?: number;
requireStorageEstimateForPut?: boolean;
}
export class OpfsAsyncBlockStore {
constructor(config?: { name?: string; prefix?: string; provider?: string; trace?: TraceLog | null; verifyExistingBlocksOnPut?: boolean; verifyAfterWrite?: boolean; verifyOnHas?: boolean; repairCorruptOnPut?: boolean; exclusiveWriters?: boolean; writeBudgetGuard?: boolean | RtOpfsWriteBudgetGuard | null; minFreeBytesForPut?: number; maxUsageRatioForPut?: number; requireStorageEstimateForPut?: boolean; allowWriteBudgetGuardOverride?: boolean });
readonly name: string;
readonly provider: string;
readonly prefix: string;
readonly available: boolean;
readonly allowWriteBudgetGuardOverride: boolean;
readonly stats: Record<string, number>;
close(reason?: string): Readonly<Record<string, unknown>>;
closeAsync(options?: { reason?: string }): Promise<Readonly<Record<string, unknown>>>;
open(options?: RtOpfsOperationOptions): Promise<unknown>;
blockPath(hash: string): string;
put(value: string | Uint8Array | ArrayBuffer | ArrayBufferView, fields?: Record<string, unknown>, options?: RtOpfsPutOptions): Promise<Readonly<RtBlockPutResult & { path: string; repairedCorrupt?: boolean; repair?: Readonly<Record<string, unknown>> | null; budget?: Readonly<Record<string, unknown>> | null; staging?: Readonly<Record<string, unknown>> | null }>>;
get(refOrDigest: string | RtBlockRef, options?: RtOpfsOperationOptions): Promise<Uint8Array>;
has(refOrDigest: string | RtBlockRef, options?: RtOpfsOperationOptions): Promise<boolean>;
delete(refOrDigest: string | RtBlockRef, options?: RtOpfsOperationOptions): Promise<boolean>;
verify(refOrDigest: string | RtBlockRef, options?: RtOpfsOperationOptions): Promise<Readonly<{ digest: string; present: boolean; ok: boolean; bytes: number; path: string; actualDigest?: string | null; reason?: string | null }>>;
recoverStagedWrites(options?: RtOpfsOperationOptions & { reason?: string; failOnError?: boolean; maxDeletes?: number }): Promise<Readonly<Record<string, unknown>>>;
estimate(options?: RtOpfsOperationOptions): Promise<Readonly<{ quota: number | null; usage: number | null; usageDetails: unknown }>>;
cleanupForTest(options?: RtOpfsOperationOptions): Promise<boolean>;
snapshot(): Readonly<Record<string, unknown> & { stageSessionId?: string; activeStagedWrites?: number; activeWriteBudgetReservedBytes?: number }>;
}
export function createOpfsAsyncBlockStore(config?: object): OpfsAsyncBlockStore;
export class WebLockCoordinator {
constructor(config?: { locks?: unknown; prefix?: string; trace?: TraceLog | null; label?: string; requireAvailable?: boolean; defaultTimeoutMs?: number });
readonly available: boolean;
readonly prefix: string;
readonly label: string;
readonly stats: Record<string, number>;
lockName(name: string): string;
request<T = unknown>(name: string, callback: (lock: unknown) => T | Promise<T>, options?: { mode?: 'exclusive' | 'shared'; ifAvailable?: boolean; steal?: boolean; signal?: AbortSignal; timeoutMs?: number; metadata?: Record<string, unknown> }): Promise<T>;
exclusive<T = unknown>(name: string, callback: (lock: unknown) => T | Promise<T>, options?: Record<string, unknown>): Promise<T>;
shared<T = unknown>(name: string, callback: (lock: unknown) => T | Promise<T>, options?: Record<string, unknown>): Promise<T>;
query(): Promise<unknown>;
normalizeQueryResult(result: unknown, name?: string | null): Readonly<Record<string, unknown>>;
queryLocks(name?: string | null): Promise<Readonly<Record<string, unknown>>>;
waitForSettled(name?: string | null, options?: { timeoutMs?: number; intervalMs?: number }): Promise<Readonly<Record<string, unknown>>>;
snapshot(): Readonly<Record<string, unknown>>;
}
export function createWebLockCoordinator(config?: object): WebLockCoordinator;
export class WebLockGuardedBlockStore {
constructor(config: { store: unknown; coordinator?: WebLockCoordinator | null; locks?: unknown; lockName?: string | null; lockPrefix?: string; label?: string | null; trace?: TraceLog | null; readMode?: 'shared' | 'exclusive'; requireWebLocks?: boolean; lockTimeoutMs?: number; ownStore?: boolean; allowUnboundedLockTimeoutOverride?: boolean });
readonly name: string;
readonly provider: string;
readonly prefix: string | undefined;
readonly available: boolean;
readonly fullLockName: string;
readonly closed: boolean;
withExclusive<T = unknown>(callback: (lock: unknown) => T | Promise<T>, metadata?: Record<string, unknown>, options?: { timeoutMs?: number; operationTimeoutMs?: number; signal?: AbortSignal; abortSignal?: AbortSignal | null }): Promise<T>;
withShared<T = unknown>(callback: (lock: unknown) => T | Promise<T>, metadata?: Record<string, unknown>, options?: { timeoutMs?: number; operationTimeoutMs?: number; signal?: AbortSignal; abortSignal?: AbortSignal | null }): Promise<T>;
open(options?: { timeoutMs?: number; operationTimeoutMs?: number; signal?: AbortSignal; abortSignal?: AbortSignal | null }): Promise<unknown>;
put(value: string | Uint8Array | ArrayBuffer | ArrayBufferView, fields?: Record<string, unknown>, options?: { timeoutMs?: number; operationTimeoutMs?: number; signal?: AbortSignal; abortSignal?: AbortSignal | null }): Promise<Readonly<RtBlockPutResult & { path?: string }>>;
get(refOrDigest: string | RtBlockRef, options?: { timeoutMs?: number; operationTimeoutMs?: number; signal?: AbortSignal; abortSignal?: AbortSignal | null }): Promise<Uint8Array>;
has(refOrDigest: string | RtBlockRef, options?: { timeoutMs?: number; operationTimeoutMs?: number; signal?: AbortSignal; abortSignal?: AbortSignal | null }): Promise<boolean>;
delete(refOrDigest: string | RtBlockRef, options?: { timeoutMs?: number; operationTimeoutMs?: number; signal?: AbortSignal; abortSignal?: AbortSignal | null }): Promise<boolean>;
verify(refOrDigest: string | RtBlockRef, options?: { timeoutMs?: number; operationTimeoutMs?: number; signal?: AbortSignal; abortSignal?: AbortSignal | null }): Promise<Readonly<Record<string, unknown>>>;
estimate(options?: { timeoutMs?: number; operationTimeoutMs?: number; signal?: AbortSignal; abortSignal?: AbortSignal | null }): Promise<Readonly<Record<string, unknown>>>;
cleanupForTest(options?: { timeoutMs?: number; operationTimeoutMs?: number; signal?: AbortSignal; abortSignal?: AbortSignal | null }): Promise<boolean>;
recoverStagedWrites(options?: { timeoutMs?: number; operationTimeoutMs?: number; signal?: AbortSignal; abortSignal?: AbortSignal | null; reason?: string; failOnError?: boolean; maxDeletes?: number }): Promise<Readonly<Record<string, unknown>>>;
queryLocks(): Promise<Readonly<Record<string, unknown>>>;
waitForSettled(options?: { timeoutMs?: number; intervalMs?: number }): Promise<Readonly<Record<string, unknown>>>;
close(reason?: string): Readonly<Record<string, unknown>>;
closeAsync(options?: { reason?: string }): Promise<Readonly<Record<string, unknown>>>;
snapshot(): Readonly<Record<string, unknown>>;
}
export function createWebLockGuardedBlockStore(config?: object): WebLockGuardedBlockStore;
export const BROWSERRT_BROWSER_STORAGE_POSTURE_FORMAT: 'browserrt.browser-storage-posture.v1';
export const BROWSERRT_BROWSER_STORAGE_ADMISSION_POLICY_FORMAT: 'browserrt.browser-storage-admission-policy.v1';
export const BROWSERRT_BROWSER_STORAGE_RECOVERY_GUIDANCE_FORMAT: 'browserrt.browser-storage-recovery-guidance.v1';
export interface RtBrowserStorageRecoveryGuidance {
project: 'BrowserRT';
schema: 1;
format: 'browserrt.browser-storage-recovery-guidance.v1';
code: string;
category: string;
phase: string;
action: string;
retryable: boolean;
mutationAttempted: boolean | null;
mutationCommitted: boolean | null;
preMutationRejected: boolean;
shouldRetryAutomatically: boolean;
shouldQueryLocks: boolean;
shouldRefreshStoragePosture: boolean;
shouldVerifyDigestBeforeRetry: boolean;
op: string | null;
lock: Readonly<{ name: string | null; mode: string | null; timeoutMs: number | null }>;
quota: Readonly<Record<string, unknown>>;
retryHint: Readonly<Record<string, boolean>>;
recoverySteps: readonly string[];
compactDetail: Readonly<Record<string, unknown>>;
error: Readonly<{ name: string; message: string; code: string }>;
nonClaims: readonly string[];
}
export function createBrowserStorageRecoveryGuidance(error: unknown, context?: Record<string, unknown>): Readonly<RtBrowserStorageRecoveryGuidance>;
export interface RtBrowserStoragePostureWarning {
id: string;
severity: 'blocked' | 'warning' | 'info' | string;
message: string;
detail: Readonly<Record<string, unknown>>;
}
export interface RtBrowserStorageWriteBudgetGuard {
enabled: boolean;
requireEstimate: boolean;
minFreeBytes: number;
maxUsageRatio: number;
transientWriteMultiplier: number;
transientOverheadBytes: number;
source: string;
policySource?: string | null;
reason: string;
}
export interface RtBrowserStoragePostureGuardPolicy {
format: 'browserrt.postured-write-budget-guard-policy.v1';
label: string;
suppliedOverride: boolean;
overrideSource: string | null;
overrideDisabled: boolean;
allowUnsafeOverride: boolean;
enforced: boolean;
guardSource: string | null;
nonClaims: readonly string[];
}
export interface RtBrowserStorageAdmissionPolicy {
format: 'browserrt.browser-storage-admission-policy.v1';
schema: 1;
status: 'admit-with-guard' | 'reject-until-storage-freed' | 'estimate-required' | 'blocked' | string;
quotaKnown: boolean;
usageRatio: number | null;
freeBytes: number | null;
projectedWritableBytes: number | null;
plannedWriteBytes: number | null;
plannedBudgetedBytes: number | null;
transientWriteMultiplier: number;
transientOverheadBytes: number;
plannedWriteFits: boolean | null;
storagePrivacyPolicy: Readonly<Record<string, unknown>>;
persistentObserved: boolean;
persistenceRequestExplicit: boolean;
mutationSafeDefault: boolean;
writeBudgetGuard: Readonly<RtBrowserStorageWriteBudgetGuard>;
guardUsage: string;
nonClaims: readonly string[];
}
export interface RtBrowserStoragePostureReceipt {
format: 'browserrt.browser-storage-posture-receipt.v1';
schema: 1;
label: string;
generatedAt: string;
status: string;
quota: Readonly<Record<string, unknown>>;
internalByteLedger: Readonly<{ provided: boolean; bytes: number | null; blockCount: number | null; entryCount: number | null; exact: boolean; source: string; lastMutationReceipt: Readonly<Record<string, unknown>> | null; nonClaim: string }>;
persistence: Readonly<Record<string, unknown>>;
coordination: Readonly<{ webLocksAvailable: boolean; webLocksQueryAvailable: boolean; storageBucketsVisible: boolean }>;
lastMutationReceipt: Readonly<Record<string, unknown>> | null;
admission: Readonly<Record<string, unknown>>;
proof: Readonly<Record<string, boolean>>;
nonClaims: readonly string[];
}
export interface RtBrowserStoragePostureReport {
project: 'BrowserRT';
revision: string | null;
version: string | null;
schema: 1;
format: 'browserrt.browser-storage-posture.v1';
label: string;
status: 'observed' | 'partial' | 'blocked' | string;
riskLevel: 'low-observed-risk' | 'needs-product-policy' | 'blocked' | string;
generatedAt: string;
requestPersistentStorage: boolean;
capabilities: Readonly<Record<string, boolean>>;
estimate: Readonly<Record<string, unknown>>;
persisted: Readonly<Record<string, unknown>>;
persistRequest: Readonly<Record<string, unknown>>;
admissionPolicy: Readonly<RtBrowserStorageAdmissionPolicy>;
writeBudgetGuard: Readonly<RtBrowserStorageWriteBudgetGuard>;
opfsPostureReceipt: Readonly<RtBrowserStoragePostureReceipt>;
postureReceipt: Readonly<RtBrowserStoragePostureReceipt>;
warnings: readonly RtBrowserStoragePostureWarning[];
proof: Readonly<Record<string, boolean>>;
recommendedActions: readonly string[];
nonClaims: readonly string[];
}
export interface RtBrowserStoragePostureConfig { globalThis?: unknown; global?: unknown; requestPersistentStorage?: boolean; label?: string; maxWarnings?: number; generatedAt?: string; revision?: string; version?: string; budgetPolicy?: Record<string, unknown>; internalByteLedger?: Record<string, unknown>; byteLedger?: Record<string, unknown>; opfsByteLedger?: Record<string, unknown>; lastMutationReceipt?: Record<string, unknown>; lastMutation?: Record<string, unknown>; trace?: { emit?: (kind: string, detail?: Record<string, unknown>) => unknown } | null }
export function diagnoseBrowserStoragePosture(config?: RtBrowserStoragePostureConfig): Promise<Readonly<RtBrowserStoragePostureReport>>;
export interface RtPosturedOpfsAsyncBlockStore {
store: OpfsAsyncBlockStore;
posture: Readonly<RtBrowserStoragePostureReport>;
postureReceipt: Readonly<RtBrowserStoragePostureReceipt>;
admissionPolicy: Readonly<RtBrowserStorageAdmissionPolicy>;
writeBudgetGuard: Readonly<RtBrowserStorageWriteBudgetGuard>;
postureGuardPolicy: Readonly<RtBrowserStoragePostureGuardPolicy>;
status: 'admitted';
}
export interface RtBrowserStorageLockContentionPolicy {
enabled: boolean;
lockTimeoutMs: number;
defaulted: boolean;
source: 'postured-web-lock-guarded-opfs-factory' | string;
reason: string;
nonClaims: readonly string[];
}
export interface RtBrowserStorageLockFallbackPolicy {
format: 'browserrt.postured-web-lock-fallback-policy.v1';
label: string;
lockAvailable: boolean;
requireWebLocks: boolean;
singleOwnerFallbackRequested: boolean;
allowUnsafeSingleOwnerFallback: boolean;
enforced: boolean;
source: 'postured-web-lock-guarded-opfs-factory' | string;
nonClaims: readonly string[];
}
export interface RtPosturedWebLockGuardedOpfsBlockStore {
store: WebLockGuardedBlockStore;
guardedStore: WebLockGuardedBlockStore;
innerStore: OpfsAsyncBlockStore;
posture: Readonly<RtBrowserStoragePostureReport>;
postureReceipt: Readonly<RtBrowserStoragePostureReceipt>;
admissionPolicy: Readonly<RtBrowserStorageAdmissionPolicy>;
writeBudgetGuard: Readonly<RtBrowserStorageWriteBudgetGuard>;
postureGuardPolicy: Readonly<RtBrowserStoragePostureGuardPolicy>;
lockName: string;
lockContentionPolicy: Readonly<RtBrowserStorageLockContentionPolicy>;
lockFallbackPolicy: Readonly<RtBrowserStorageLockFallbackPolicy>;
status: 'admitted-and-guarded' | 'admitted-single-owner-fallback';
}
export interface RtPosturedWebLockGuardedOpfsStorageLaneAdapter {
adapter: OpfsBlockStoreStorageLaneAdapter;
laneAdapter: OpfsBlockStoreStorageLaneAdapter;
store: WebLockGuardedBlockStore;
guardedStore: WebLockGuardedBlockStore;
innerStore: OpfsAsyncBlockStore;
posturedGuarded: Readonly<RtPosturedWebLockGuardedOpfsBlockStore>;
posture: Readonly<RtBrowserStoragePostureReport>;
postureReceipt: Readonly<RtBrowserStoragePostureReceipt>;
admissionPolicy: Readonly<RtBrowserStorageAdmissionPolicy>;
writeBudgetGuard: Readonly<RtBrowserStorageWriteBudgetGuard>;
postureGuardPolicy: Readonly<RtBrowserStoragePostureGuardPolicy>;
lockName: string;
lockContentionPolicy: Readonly<RtBrowserStorageLockContentionPolicy>;
lockFallbackPolicy: Readonly<RtBrowserStorageLockFallbackPolicy>;
lane: string;
adapterFactorySource: 'postured-web-lock-guarded-storage-lane-adapter-factory' | string;
status: 'admitted-guarded-lane-adapter' | 'admitted-single-owner-fallback-lane-adapter';
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
revision: 'rev0125';
version: '0.0.125';
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
// rev0108: Raw OpfsAsyncBlockStore composes signal/abortSignal; boot flag marker: opfsRawCompositeAbortSignalProof?: boolean
export class TraceLog {
constructor(config?: { capacity?: number });
readonly capacity: number;
readonly droppedCount: number;
emit(kind: string, detail?: Record<string, unknown>): RtTraceEvent;
snapshot(): RtTraceEvent[];
find(kind: string): RtTraceEvent[];
count(kind: string): number;
kinds(): string[];
}
export interface RtOperationScopeSnapshot {
id: string;
label: string;
closed: boolean;
aborted: boolean;
reason: Readonly<Record<string, unknown>> | null;
createdAt: number;
deadlineAt: number | null;
activeRuns: number;
childCount: number;
resourceCount: number;
cleanupCount: number;
metadata: Readonly<Record<string, unknown>>;
}
export interface RtOperationScopeCloseReport {
disposition: string;
scopeId: string;
label: string;
aborted?: boolean;
reason?: Readonly<Record<string, unknown>>;
childCount?: number;
resourceCount?: number;
cleanupCount?: number;
failedCount?: number;
children: ReadonlyArray<Record<string, unknown>>;
resources: ReadonlyArray<Record<string, unknown>>;
cleanups: ReadonlyArray<Record<string, unknown>>;
snapshot?: RtOperationScopeSnapshot;
}
export interface RtOperationScopeLike {
readonly signal: AbortSignal;
readonly closed: boolean;
readonly aborted: boolean;
readonly reason: unknown;
track<TResource>(resource: TResource, options?: { kind?: string; label?: string | null; owned?: boolean }): TResource;
closeAsync(options?: { reason?: string }): Promise<RtOperationScopeCloseReport>;
}
export class OperationScope implements RtOperationScopeLike {
constructor(config?: { label?: string; trace?: TraceLog | null; parent?: OperationScope | RtOperationScopeLike | null; signal?: AbortSignal | null; abortSignal?: AbortSignal | null; timeoutMs?: number; metadata?: Record<string, unknown> });
readonly id: string;
readonly label: string;
readonly createdAt: number;
readonly deadlineAt: number | null;
readonly signal: AbortSignal;
readonly closed: boolean;
readonly aborted: boolean;
readonly reason: unknown;
readonly metadata: Readonly<Record<string, unknown>>;
child(config?: { label?: string; trace?: TraceLog | null; signal?: AbortSignal | null; abortSignal?: AbortSignal | null; timeoutMs?: number; metadata?: Record<string, unknown> }): OperationScope;
throwIfAborted(): void;
track<TResource>(resource: TResource, options?: { kind?: string; label?: string | null; owned?: boolean }): TResource;
onCleanup(callback: (event: { scope: OperationScope; reason: string }) => unknown | Promise<unknown>, options?: { label?: string }): () => void;
run<T = unknown>(callback: (scope: OperationScope) => T | Promise<T>, options?: { label?: string }): Promise<T>;
abort(reason?: unknown): RtOperationScopeSnapshot;
close(reason?: string): RtOperationScopeSnapshot;
closeAsync(options?: { reason?: string }): Promise<RtOperationScopeCloseReport>;
snapshot(): RtOperationScopeSnapshot;
}
export class BoundedChannel<T = unknown> {
constructor(config?: { capacity?: number; overflow?: RtOverflow; label?: string; trace?: TraceLog | null; maxWaitingSenders?: number; maxWaitingReceivers?: number });
capacity: number;
overflow: RtOverflow;
label: string;
send(value: T, options?: { signal?: AbortSignal | null; abortSignal?: AbortSignal | null; scope?: OperationScope | RtOperationScopeLike | null; timeoutMs?: number }): Promise<{ disposition: string }>;
receive(options?: { signal?: AbortSignal | null; abortSignal?: AbortSignal | null; scope?: OperationScope | RtOperationScopeLike | null; timeoutMs?: number }): Promise<T>;
close(reason?: string): Readonly<Record<string, unknown>>;
size(): number;
snapshot(): Readonly<Record<string, unknown>>;
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
constructor(config: { worker: Worker | unknown; name?: string; trace?: TraceLog; readyTimeoutMs?: number; lateSettlementRetention?: number });
readonly closed: boolean;
readonly failed: boolean;
readonly trace: TraceLog;
readonly ready: Promise<WorkerAgent>;
onExit(callback: (event: { agent: WorkerAgent; code: number | null; error: Error }) => void): () => void;
call<T = unknown>(op: string, payload?: unknown, options?: { transfer?: Transferable[]; timeoutMs?: number; lane?: RtLane; priority?: RtPriority; signal?: AbortSignal | null; abortSignal?: AbortSignal | null; cancelOnTimeout?: boolean; scope?: OperationScope | RtOperationScopeLike | null; terminateOnCancel?: boolean; cancelGraceMs?: number }): Promise<T>;
terminate(reason?: string): Promise<{ disposition: string }>;
}
export class Supervisor {
constructor(config?: { name?: string; workerURL?: URL | string; trace?: TraceLog; restartLimit?: number });
name: string;
restartLimit: number;
restartCount: number;
closed: boolean;
start(): Promise<Supervisor>;
call<T = unknown>(op: string, payload?: unknown, options?: { transfer?: Transferable[]; timeoutMs?: number; lane?: RtLane; priority?: RtPriority; signal?: AbortSignal | null; abortSignal?: AbortSignal | null; cancelOnTimeout?: boolean; scope?: OperationScope | RtOperationScopeLike | null; terminateOnCancel?: boolean; cancelGraceMs?: number }): Promise<T>;
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
export function createWebLockCoordinator(config?: object): WebLockCoordinator;
export function createWebLockGuardedBlockStore(config?: object): WebLockGuardedBlockStore;
export function createEnvelope(op: string, fields?: Partial<RtEnvelope>): RtEnvelope;
export function createSharedInt32Ring(config?: { capacity?: number; label?: string; trace?: TraceLog | null }): SharedInt32Ring;
export function openSharedInt32Ring(sab: SharedArrayBuffer, config?: { label?: string; trace?: TraceLog | null }): SharedInt32Ring;
export function createSharedFrameRing(config?: { capacityBytes?: number; label?: string; trace?: TraceLog | null }): SharedFrameRing;
export function openSharedFrameRing(sab: SharedArrayBuffer, config?: { label?: string; trace?: TraceLog | null }): SharedFrameRing;
export function createSpillFrameMailbox(config: { label?: string; provider: MemoryBlockStore; memoryCapacityBytes?: number; maxFrameBytes?: number; trace?: TraceLog | null; deleteSpilledBlocksOnAck?: boolean }): SpillFrameMailbox;
export function checksumFramePayload32(payload: Uint8Array | ArrayBuffer | ArrayBufferView | string): number;
export function spawnWorkerAgent(config?: { workerURL?: URL | string; name?: string; trace?: TraceLog; workerOptions?: Record<string, unknown>; readyTimeoutMs?: number; scope?: OperationScope | RtOperationScopeLike | null }): Promise<WorkerAgent>;
export function createSupervisor(config?: { name?: string; workerURL?: URL | string; trace?: TraceLog; restartLimit?: number }): Supervisor;
export function createBootReport(config?: { capabilities?: RtCapabilities; options?: Record<string, unknown> }): RtBootReport;
export type BrowserRTCoreNamespace = Readonly<Pick<BrowserRTRuntime,
| 'scope'
| 'channel'
| 'objectRef'
| 'transferObject'
| 'blockObjectRef'
| 'spawnAgent'
| 'supervisor'
>>;
export type BrowserRTStorageNamespace = Readonly<Pick<BrowserRTRuntime,
| 'blockStore'
| 'journaledBlockStore'
| 'recoverJournaledBlockStore'
| 'blockStoreLaneAdapter'
| 'opfsObjectRef'
| 'opfsSyncObjectRef'
| 'opfsAsyncWriteReadProbe'
| 'opfsAsyncBlockStore'
| 'opfsAsyncBlockStoreWithPosture'
| 'opfsBlockStoreStorageLaneAdapter'
| 'opfsWebLockGuardedBlockStore'
| 'opfsWebLockGuardedBlockStoreWithPosture'
| 'opfsWebLockGuardedStorageLaneAdapterWithPosture'
| 'browserStoragePosture'
| 'browserStorageRecoveryGuidance'
| 'kernelKitStoragePosture'
| 'kernelKitOpfsAbortBoundary'
>>;
export type BrowserRTCoordinationNamespace = Readonly<Pick<BrowserRTRuntime,
| 'admissionController'
| 'adaptiveConcurrencyController'
| 'priorityFairScheduler'
| 'crossLaneScheduler'
| 'storageLaneExecutor'
| 'retryBudgetAdmissionController'
| 'storageLaneRetryController'
| 'circuitBreakerBulkheadController'
| 'providerResilienceHistoryRunner'
| 'storageLaneAdmissionHistoryRunner'
| 'webLockCoordinator'
| 'kernelKitWebLockPosture'
>>;
export type BrowserRTDiagnosticsNamespace = Readonly<Pick<BrowserRTRuntime,
| 'kernelKitLifecycleCheckpoint'
| 'kernelKitSessionCoordinationCheckpoint'
| 'kernelKitRecoveryCheckpoint'
| 'kernelKitAdmissionCancellationCheckpoint'
| 'kernelKitDemoTraceSummary'
| 'kernelKitTraceExport'
| 'validateKernelKitTraceExport'
| 'kernelKitSupportBundle'
| 'validateKernelKitSupportBundle'
| 'kernelKitSupportBundlePrivacyScrub'
| 'validateKernelKitSupportBundlePrivacyScrub'
| 'kernelKitSupportBundleReplayPlan'
| 'validateKernelKitSupportBundleReplayPlan'
| 'kernelKitSupportBundleOperatorPreflightDisplaySnapshot'
| 'validateKernelKitSupportBundleOperatorPreflightDisplaySnapshot'
| 'kernelKitSupportBundleOperatorReplayGate'
| 'validateKernelKitSupportBundleOperatorReplayGate'
| 'kernelKitSupportBundleEvidenceLedger'
| 'validateKernelKitSupportBundleEvidenceLedger'
| 'kernelKitSupportBundleEvidenceCheckpoint'
| 'validateKernelKitSupportBundleEvidenceCheckpoint'
| 'kernelKitDiagnosticRunbook'
| 'validateKernelKitDiagnosticRunbook'
| 'kernelKitReadinessGate'
| 'validateKernelKitReadinessGate'
>>;
export type BrowserRTExperimentalNamespace = Readonly<Pick<BrowserRTRuntime,
| 'sharedInt32Ring'
| 'openSharedInt32Ring'
| 'sharedFrameRing'
| 'openSharedFrameRing'
| 'spillFrameMailbox'
| 'persistedSpillMailbox'
| 'recoverPersistedSpillMailbox'
| 'providerResilienceModelOracle'
| 'storageLaneAdmissionHistoryModelOracle'
| 'storageLaneOverloadGovernanceModelOracle'
| 'dreamBoundaryMap'
| 'validateDreamBoundaryMap'
| 'projectContinuationAssessment'
| 'validateProjectContinuationAssessment'
>>;
export interface BrowserRTRuntime {
  version: '0.0.125';
  revision: 'rev0125';
  options: Readonly<Record<string, unknown>>;
  capabilities: RtCapabilities;
  report: RtBootReport;
  trace: TraceLog;
  core: BrowserRTCoreNamespace;
  storage: BrowserRTStorageNamespace;
  coordination: BrowserRTCoordinationNamespace;
  diagnostics: BrowserRTDiagnosticsNamespace;
  experimental: BrowserRTExperimentalNamespace;
  scope(config?: { label?: string; trace?: TraceLog | null; parent?: OperationScope | RtOperationScopeLike | null; signal?: AbortSignal | null; abortSignal?: AbortSignal | null; timeoutMs?: number; metadata?: Record<string, unknown>; owned?: boolean }): OperationScope;
  channel<T = unknown>(config?: { capacity?: number; overflow?: RtOverflow; label?: string; maxWaitingSenders?: number; maxWaitingReceivers?: number; scope?: OperationScope | RtOperationScopeLike | null; owned?: boolean }): BoundedChannel<T>;
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
  opfsAsyncBlockStore(config?: object): OpfsAsyncBlockStore;
  opfsAsyncBlockStoreWithPosture(config?: { name?: string; label?: string; prefix?: string; provider?: string; storeConfig?: Record<string, unknown>; postureConfig?: Record<string, unknown>; budgetPolicy?: Record<string, unknown>; requestPersistentStorage?: boolean; allowEstimateRequired?: boolean; failOnStorageAdmission?: boolean; writeBudgetGuard?: boolean | RtOpfsWriteBudgetGuard | RtBrowserStorageWriteBudgetGuard | null; minFreeBytesForPut?: number; maxUsageRatioForPut?: number; requireStorageEstimateForPut?: boolean; allowPostureWriteBudgetGuardOverride?: boolean; allowUnsafeWriteBudgetGuardOverride?: boolean; owned?: boolean }): Promise<Readonly<RtPosturedOpfsAsyncBlockStore>>;
  browserStoragePosture(config?: RtBrowserStoragePostureConfig): Promise<Readonly<RtBrowserStoragePostureReport>>;
  browserStorageRecoveryGuidance(error: unknown, context?: Record<string, unknown>): Readonly<RtBrowserStorageRecoveryGuidance>;
  kernelKitOpfsAbortBoundary(config?: Record<string, unknown>): Promise<Readonly<Record<string, unknown>>>;
  kernelKitStoragePosture(config?: Record<string, unknown>): Promise<Readonly<Record<string, unknown>>>;
  kernelKitWebLockPosture(config?: Record<string, unknown>): Promise<Readonly<Record<string, unknown>>>;
  kernelKitLifecycleCheckpoint(input?: Record<string, unknown>, fields?: Record<string, unknown>): Readonly<Record<string, unknown>>;
  kernelKitSessionCoordinationCheckpoint(input?: Record<string, unknown>, fields?: Record<string, unknown>): Readonly<Record<string, unknown>>;
  kernelKitRecoveryCheckpoint(input?: Record<string, unknown>, fields?: Record<string, unknown>): Readonly<Record<string, unknown>>;
  kernelKitAdmissionCancellationCheckpoint(input?: Record<string, unknown>, fields?: Record<string, unknown>): Readonly<Record<string, unknown>>;
  kernelKitSupportBundlePrivacyScrub(input?: string | Record<string, unknown>, fields?: Record<string, unknown>): Readonly<Record<string, unknown>>;
  validateKernelKitSupportBundlePrivacyScrub(report?: Record<string, unknown>): Readonly<Record<string, unknown>>;
  validateKernelKitLifecycleCheckpoint(checkpoint?: Record<string, unknown>): Readonly<Record<string, unknown>>;
  validateKernelKitRecoveryCheckpoint(checkpoint?: Record<string, unknown>): Readonly<Record<string, unknown>>;
  validateKernelKitAdmissionCancellationCheckpoint(checkpoint?: Record<string, unknown>): Readonly<Record<string, unknown>>;
  validateKernelKitSessionCoordinationCheckpoint(checkpoint?: Record<string, unknown>): Readonly<Record<string, unknown>>;
  webLockCoordinator(config?: object): WebLockCoordinator;
  opfsWebLockGuardedBlockStore(config?: object): WebLockGuardedBlockStore;
  opfsWebLockGuardedBlockStoreWithPosture(config?: { name?: string; label?: string; guardLabel?: string; prefix?: string; provider?: string; storeConfig?: Record<string, unknown>; postureConfig?: Record<string, unknown>; budgetPolicy?: Record<string, unknown>; requestPersistentStorage?: boolean; allowEstimateRequired?: boolean; failOnStorageAdmission?: boolean; writeBudgetGuard?: boolean | RtOpfsWriteBudgetGuard | RtBrowserStorageWriteBudgetGuard | null; minFreeBytesForPut?: number; maxUsageRatioForPut?: number; requireStorageEstimateForPut?: boolean; allowPostureWriteBudgetGuardOverride?: boolean; allowUnsafeWriteBudgetGuardOverride?: boolean; lockName?: string; lockPrefix?: string; lockTimeoutMs?: number; lockContentionTimeoutMs?: number; allowUnboundedPostureLockWait?: boolean; allowUnsafeUnboundedPostureLockWait?: boolean; readMode?: 'shared' | 'exclusive'; requireWebLocks?: boolean; allowUnsafeSingleOwnerFallback?: boolean; allowPostureSingleOwnerFallback?: boolean; allowUnlockedSingleOwnerFallback?: boolean; locks?: unknown; coordinator?: WebLockCoordinator; owned?: boolean; ownStore?: boolean }): Promise<Readonly<RtPosturedWebLockGuardedOpfsBlockStore>>;
  opfsWebLockGuardedStorageLaneAdapterWithPosture(config?: { name?: string; label?: string; guardLabel?: string; adapterLabel?: string; prefix?: string; provider?: string; storeConfig?: Record<string, unknown>; adapterConfig?: Record<string, unknown>; postureConfig?: Record<string, unknown>; budgetPolicy?: Record<string, unknown>; requestPersistentStorage?: boolean; allowEstimateRequired?: boolean; failOnStorageAdmission?: boolean; writeBudgetGuard?: boolean | RtOpfsWriteBudgetGuard | RtBrowserStorageWriteBudgetGuard | null; minFreeBytesForPut?: number; maxUsageRatioForPut?: number; requireStorageEstimateForPut?: boolean; allowPostureWriteBudgetGuardOverride?: boolean; allowUnsafeWriteBudgetGuardOverride?: boolean; lockName?: string; lockPrefix?: string; lockTimeoutMs?: number; lockContentionTimeoutMs?: number; allowUnboundedPostureLockWait?: boolean; allowUnsafeUnboundedPostureLockWait?: boolean; readMode?: 'shared' | 'exclusive'; requireWebLocks?: boolean; allowUnsafeSingleOwnerFallback?: boolean; allowPostureSingleOwnerFallback?: boolean; allowUnlockedSingleOwnerFallback?: boolean; locks?: unknown; coordinator?: WebLockCoordinator; scheduler?: unknown; lanes?: unknown[]; schedulerConfig?: Record<string, unknown>; lane?: string; owned?: boolean; ownStore?: boolean; adapterOwned?: boolean }): Promise<Readonly<RtPosturedWebLockGuardedOpfsStorageLaneAdapter>>;
  spawnAgent(config?: { workerURL?: URL | string; name?: string; trace?: TraceLog; workerOptions?: Record<string, unknown>; readyTimeoutMs?: number; scope?: OperationScope | RtOperationScopeLike | null; owned?: boolean }): Promise<WorkerAgent>;
  supervisor(config?: { name?: string; workerURL?: URL | string; trace?: TraceLog; restartLimit?: number; owned?: boolean }): Supervisor;
  admissionController(config?: Record<string, unknown>): WatermarkAdmissionController;
  adaptiveConcurrencyController(config?: Record<string, unknown>): AdaptiveConcurrencyController;
  priorityFairScheduler(config?: Record<string, unknown>): PriorityFairScheduler;
  crossLaneScheduler(config?: Record<string, unknown>): CrossLaneScheduler;
  storageLaneExecutor(config?: Record<string, unknown>): StorageLaneExecutor;
  retryBudgetAdmissionController(config?: Record<string, unknown>): RetryBudgetAdmissionController;
  storageLaneRetryController(config?: Record<string, unknown>): StorageLaneRetryController;
  providerResilienceHistoryRunner(config?: Record<string, unknown>): ProviderResilienceHistoryRunner;
  circuitBreakerBulkheadController(config?: Record<string, unknown>): CircuitBreakerBulkheadController;
  providerResilienceModelOracle(config?: Record<string, unknown>): ProviderResilienceModelOracle;
  storageLaneAdmissionHistoryRunner(config?: Record<string, unknown>): StorageLaneAdmissionHistoryRunner;
  storageLaneAdmissionHistoryModelOracle(config?: Record<string, unknown>): StorageLaneAdmissionHistoryModelOracle;
  storageLaneOverloadGovernanceModelOracle(config?: Record<string, unknown>): StorageLaneOverloadGovernanceModelOracle;
  blockStoreLaneAdapter(config?: Record<string, unknown>): BlockStoreLaneAdapter;
  dreamBoundaryMap(): Readonly<Record<string, unknown>>;
  validateDreamBoundaryMap(map?: Record<string, unknown>): Readonly<Record<string, unknown>>;
  projectContinuationAssessment(): Readonly<Record<string, unknown>>;
  validateProjectContinuationAssessment(assessment?: Record<string, unknown>): Readonly<Record<string, unknown>>;
  kernelKitDemoPlan(): Readonly<Record<string, unknown>>;
  validateKernelKitDemoReport(report?: Record<string, unknown>): Readonly<Record<string, unknown>>;
  kernelKitDemoTranscript(report?: Record<string, unknown>): Readonly<Record<string, unknown>>;
  validateKernelKitDemoTranscript(transcript?: Record<string, unknown>): Readonly<Record<string, unknown>>;
  kernelKitDemoUsefulnessScore(report?: Record<string, unknown>): Readonly<Record<string, unknown>>;
  kernelKitDemoTraceSummary(traceKindsOrEvents?: ReadonlyArray<string | RtTraceEvent>): Readonly<Record<string, unknown>>;
  kernelKitTraceExport(report?: Record<string, unknown>, fields?: Record<string, unknown>): Readonly<Record<string, unknown>>;
  validateKernelKitTraceExport(exportReport?: Record<string, unknown>): Readonly<Record<string, unknown>>;
  kernelKitDemoExportBundle(report?: Record<string, unknown>, fields?: Record<string, unknown>): Readonly<Record<string, unknown>>;
  validateKernelKitDemoExportBundle(bundle?: Record<string, unknown>): Readonly<Record<string, unknown>>;
  kernelKitFailureModeReport(fields?: Record<string, unknown>): Readonly<Record<string, unknown>>;
  validateKernelKitFailureModeReport(report?: Record<string, unknown>): Readonly<Record<string, unknown>>;
  kernelKitTraceComparison(successReport?: Record<string, unknown>, failureReport?: Record<string, unknown>, fields?: Record<string, unknown>): Readonly<Record<string, unknown>>;
  validateKernelKitTraceComparison(comparison?: Record<string, unknown>): Readonly<Record<string, unknown>>;
  kernelKitDiagnosticRunbook(comparison?: Record<string, unknown>, fields?: Record<string, unknown>): Readonly<Record<string, unknown>>;
  validateKernelKitDiagnosticRunbook(runbook?: Record<string, unknown>): Readonly<Record<string, unknown>>;
  kernelKitSupportBundle(fields?: Record<string, unknown>): Readonly<Record<string, unknown>>;
  validateKernelKitSupportBundle(bundle?: Record<string, unknown>): Readonly<Record<string, unknown>>;
  kernelKitSupportBundleReplayPlan(input?: Record<string, unknown>, fields?: Record<string, unknown>): Readonly<Record<string, unknown>>;
  validateKernelKitSupportBundleReplayPlan(report?: Record<string, unknown>): Readonly<Record<string, unknown>>;
  kernelKitSupportBundleOperatorPreflightDisplaySnapshot(input?: Record<string, unknown>, fields?: Record<string, unknown>): KernelKitSupportBundleOperatorPreflightDisplaySnapshot;
  validateKernelKitSupportBundleOperatorPreflightDisplaySnapshot(report?: Record<string, unknown>): KernelKitDemoProofValidation & Readonly<{ rowCount: number; format: string | null; status: string | null }>;
  kernelKitSupportBundleOperatorReplayGate(input?: Record<string, unknown>, fields?: Record<string, unknown>): KernelKitSupportBundleOperatorReplayGate;
  validateKernelKitSupportBundleOperatorReplayGate(report?: Record<string, unknown>): KernelKitDemoProofValidation & Readonly<{ rowCount: number; format: string | null; status: string | null }>;
  kernelKitSupportBundleEvidenceLedger(input?: Record<string, unknown>, fields?: Record<string, unknown>): Readonly<Record<string, unknown>>;
  validateKernelKitSupportBundleEvidenceLedger(report?: Record<string, unknown>): Readonly<Record<string, unknown>>;
  kernelKitSupportBundleEvidenceCheckpoint(input?: Record<string, unknown>, artifacts?: Record<string, unknown>, fields?: Record<string, unknown>): Readonly<Record<string, unknown>>;
  validateKernelKitSupportBundleEvidenceCheckpoint(report?: Record<string, unknown>): Readonly<Record<string, unknown>>;
  kernelKitGuidedTour(fields?: Record<string, unknown>): Readonly<Record<string, unknown>>;
  validateKernelKitGuidedTour(tour?: Record<string, unknown>): Readonly<Record<string, unknown>>;
  kernelKitSupportBundleImportReport(input?: Record<string, unknown>, fields?: Record<string, unknown>): Readonly<Record<string, unknown>>;
  validateKernelKitSupportBundleImportReport(report?: Record<string, unknown>): Readonly<Record<string, unknown>>;
  kernelKitSupportBundleDiff(currentBundle?: Record<string, unknown>, candidateBundle?: Record<string, unknown>, fields?: Record<string, unknown>): Readonly<Record<string, unknown>>;
  validateKernelKitSupportBundleDiff(diff?: Record<string, unknown>): Readonly<Record<string, unknown>>;
  kernelKitHandoffMarkdown(fields?: Record<string, unknown>): Readonly<Record<string, unknown>>;
  validateKernelKitHandoffMarkdown(report?: Record<string, unknown>): Readonly<Record<string, unknown>>;
  kernelKitDemoHandoff(report?: Record<string, unknown>, fields?: Record<string, unknown>): Readonly<Record<string, unknown>>;
  validateKernelKitDemoHandoff(handoff?: Record<string, unknown>): Readonly<Record<string, unknown>>;
  kernelKitDemoUsefulnessReport(report?: Record<string, unknown>, fields?: Record<string, unknown>): Readonly<Record<string, unknown>>;
  validateKernelKitDemoUsefulnessReport(report?: Record<string, unknown>): Readonly<Record<string, unknown>>;
  kernelKitDemoObservatory(report?: Record<string, unknown>, fields?: Record<string, unknown>): Readonly<Record<string, unknown>>;
  validateKernelKitDemoObservatoryReport(report?: Record<string, unknown>): Readonly<Record<string, unknown>>;
  kernelKitGuidedTourReceipt(fields?: Record<string, unknown>): Readonly<Record<string, unknown>>;
  validateKernelKitGuidedTourReceipt(receipt?: Record<string, unknown>): Readonly<Record<string, unknown>>;
  kernelKitHandoffMarkdownImport(markdown: string, fields?: Record<string, unknown>): Readonly<Record<string, unknown>>;
  validateKernelKitHandoffMarkdownImportReport(report?: Record<string, unknown>): Readonly<Record<string, unknown>>;
  kernelKitReadinessGate(fields?: Record<string, unknown>): Readonly<Record<string, unknown>>;
  validateKernelKitReadinessGate(report?: Record<string, unknown>): Readonly<Record<string, unknown>>;
  kernelKitReadinessContrast(fields?: Record<string, unknown>): Readonly<Record<string, unknown>>;
  validateKernelKitReadinessContrast(report?: Record<string, unknown>): Readonly<Record<string, unknown>>;
  opfsBlockStoreStorageLaneAdapter(config?: Record<string, unknown>): OpfsBlockStoreStorageLaneAdapter;
  ownedResources(): Readonly<Record<string, unknown>>;
  close(reason?: string): RtTraceEvent[];
  closeAsync(options?: { reason?: string }): Promise<Readonly<{ revision: string; version: string; resourceClose: Readonly<Record<string, unknown>>; trace: RtTraceEvent[] }>>;
}
export function boot(options?: Record<string, unknown>): Promise<Readonly<BrowserRTRuntime>>;
export class WatermarkAdmissionController {
constructor(config?: Record<string, unknown>);
tryAdmit(input: { bytes: number; priority?: string; label?: string; metadata?: unknown; signal?: AbortSignal | { aborted: boolean; addEventListener?: (...args: unknown[]) => void; removeEventListener?: (...args: unknown[]) => void } | null; abortSignal?: AbortSignal | { aborted: boolean; addEventListener?: (...args: unknown[]) => void; removeEventListener?: (...args: unknown[]) => void } | null }): Readonly<Record<string, unknown>>;
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
constructor(config?: { label?: string; scheduler?: unknown; mailbox?: unknown; lane?: string; trace?: unknown; markUnhealthyOnError?: boolean; defaultOperationTimeoutMs?: number; operationTimeoutMs?: number; abortProviderOnOperationTimeout?: boolean });
readonly label: string;
readonly scheduler: unknown;
readonly mailbox: unknown;
readonly lane: string;
submit(op: 'enqueue' | 'dequeue' | 'ack' | 'checkpoint' | 'compact' | 'snapshot', args?: Record<string, unknown>, options?: { id?: string; priority?: string; cost?: number; dependsOn?: string[]; fallbackLanes?: string[]; flowId?: string; metadata?: unknown; operationTimeoutMs?: number; timeoutMs?: number; abortProviderOnOperationTimeout?: boolean }): Readonly<object>;
executeNext(options?: { autoComplete?: boolean }): Promise<Readonly<object>>;
executeDispatched(dispatched: object): Promise<Readonly<object>>;
markHealthy(reason?: string): Readonly<object>;
markUnhealthy(reason?: string): Readonly<object>;
unsettledTimedOutOperations(lane?: string | null): ReadonlyArray<Readonly<Record<string, unknown>>>;
unsettledTimedOutOperationCount(lane?: string | null): number;
successfulTimedOutOperations(lane?: string | null): ReadonlyArray<Readonly<Record<string, unknown>>>;
successfulTimedOutOperationCount(lane?: string | null): number;
failedTimedOutOperations(lane?: string | null): ReadonlyArray<Readonly<Record<string, unknown>>>;
failedTimedOutOperationCount(lane?: string | null): number;
timedOutOperationQuarantine(lane?: string | null): Readonly<object>;
timedOutOperationQuarantineCount(lane?: string | null): number;
exportTimedOutOperationQuarantine(options?: { lane?: string | null; reason?: string }): Readonly<object>;
importTimedOutOperationQuarantine(ledger: object, options?: { lane?: string | null; reason?: string; markUnhealthy?: boolean; allowPartialImport?: boolean; allowEmptyImport?: boolean }): Readonly<object>;
registerTimedOutOperationQuarantineClearanceReceipt(receipt: Record<string, unknown>, options?: { lane?: string | null; reason?: string }): Readonly<object>;
clearedTimedOutOperationQuarantineClearanceReceipts(lane?: string | null): ReadonlyArray<Readonly<Record<string, unknown>>>;
createTimedOutOperationQuarantineReview(options?: { lane?: string | null; reviewer?: string; reason?: string; opId?: string | null; opIds?: string[] | null; operationReplayKey?: string | null; operationReplayKeys?: string[] | null; category?: string | null; categories?: string[] | null; allowLaneWide?: boolean; all?: boolean; allowAll?: boolean; reviewToken?: string | null }): Readonly<object>;
clearTimedOutOperationQuarantine(options?: { category?: string | null; categories?: string[] | null; lane?: string | null; opId?: string | null; opIds?: string[] | null; operationReplayKey?: string | null; operationReplayKeys?: string[] | null; reason?: string; reviewed?: boolean; reviewToken?: string | null; reviewFingerprint?: string | null; requireReviewFingerprint?: boolean; reviewManifest?: Record<string, unknown> | null; allowLaneWide?: boolean; all?: boolean; allowAll?: boolean }): Readonly<object>;
finalizeUnsettledTimedOutOperations(options?: { lane?: string | null; opId?: string | null; opIds?: string[] | null; operationReplayKey?: string | null; operationReplayKeys?: string[] | null; reason?: string; reviewed?: boolean; reviewToken?: string | null; reviewFingerprint?: string | null; requireReviewFingerprint?: boolean; reviewManifest?: Record<string, unknown> | null; allowLaneWide?: boolean; all?: boolean; allowAll?: boolean; errorCode?: string; message?: string }): Readonly<object>;
clearSuccessfulTimedOutOperations(options?: { lane?: string | null; opId?: string | null; opIds?: string[] | null; operationReplayKey?: string | null; operationReplayKeys?: string[] | null; reason?: string; reviewed?: boolean; reviewToken?: string | null; reviewFingerprint?: string | null; requireReviewFingerprint?: boolean; reviewManifest?: Record<string, unknown> | null; allowLaneWide?: boolean; all?: boolean; allowAll?: boolean }): Readonly<object>;
clearFailedTimedOutOperations(options?: { lane?: string | null; opId?: string | null; opIds?: string[] | null; operationReplayKey?: string | null; operationReplayKeys?: string[] | null; reason?: string; reviewed?: boolean; reviewToken?: string | null; reviewFingerprint?: string | null; requireReviewFingerprint?: boolean; reviewManifest?: Record<string, unknown> | null; allowLaneWide?: boolean; all?: boolean; allowAll?: boolean }): Readonly<object>;
waitForTimedOutOperationsSettled(options?: { lane?: string | null; timeoutMs?: number; intervalMs?: number }): Promise<Readonly<object>>;
snapshot(): Readonly<object>;
}
export function createStorageLaneExecutor(config?: object): StorageLaneExecutor;
export function validateStorageLaneExecutorSnapshot(snapshot: Record<string, unknown>, options?: { requireMailbox?: boolean }): Readonly<{ ok: boolean; errors: string[]; pendingOperationCount: number; resultCount: number; unsettledTimedOutOperationCount: number; successfulTimedOutOperationCount: number; failedTimedOutOperationCount: number; timedOutOperationQuarantineCount: number; queuedCount: number; inFlightCount: number; mailboxQueueDepth: number; mailboxPendingCount: number }>;
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
schedulePut(bytes: Uint8Array | ArrayBuffer | ArrayBufferView | string, options?: BlockStoreLaneScheduleOptions): Readonly<object>;
scheduleGet(refOrDigest: string | Record<string, unknown>, options?: BlockStoreLaneScheduleOptions): Readonly<object>;
scheduleHas(refOrDigest: string | Record<string, unknown>, options?: BlockStoreLaneScheduleOptions): Readonly<object>;
scheduleVerify(refOrDigest: string | Record<string, unknown>, options?: BlockStoreLaneScheduleOptions): Readonly<object>;
scheduleDelete(refOrDigest: string | Record<string, unknown>, options?: BlockStoreLaneScheduleOptions): Readonly<object>;
scheduleEstimate(options?: BlockStoreLaneScheduleOptions): Readonly<object>;
scheduleCleanupForTest(options?: BlockStoreLaneScheduleOptions): Readonly<object>;
executeNext(): Promise<Readonly<object>>;
drain(options?: { maxSteps?: number }): Promise<Readonly<object>>;
result(opId: string): unknown;
markHealthy(lane?: string, reason?: string): Readonly<object>;
markUnhealthy(lane?: string, reason?: string): Readonly<object>;
successfulTimedOutOperations(lane?: string): ReadonlyArray<Readonly<Record<string, unknown>>>;
failedTimedOutOperations(lane?: string): ReadonlyArray<Readonly<Record<string, unknown>>>;
timedOutOperationQuarantine(lane?: string): Readonly<object>;
exportTimedOutOperationQuarantine(options?: { lane?: string; reason?: string }): Readonly<object>;
importTimedOutOperationQuarantine(ledger: object, options?: { lane?: string; reason?: string; markUnhealthy?: boolean; allowPartialImport?: boolean; allowEmptyImport?: boolean }): Readonly<object>;
persistTimedOutOperationQuarantine(options?: { ledger?: object; lane?: string; reason?: string; label?: string; fields?: Record<string, unknown>; putOptions?: Record<string, unknown> }): Promise<Readonly<object>>;
restoreTimedOutOperationQuarantineFromBlockStore(ref: string | Record<string, unknown>, options?: { lane?: string; reason?: string; markUnhealthy?: boolean; allowPartialImport?: boolean; allowEmptyImport?: boolean; verifyBeforeRestore?: boolean; allowUnsafeUnverifiedRestore?: boolean; expectedQuarantineFingerprint?: string; expectedReviewFingerprint?: string; expectedLedgerFingerprint?: string; verifyOptions?: Record<string, unknown>; getOptions?: Record<string, unknown> }): Promise<Readonly<object>>;
createTimedOutOperationQuarantineClearanceReceipt(clearResult: Record<string, unknown>, options?: { label?: string | null; createdAtMs?: number; reviewer?: string | null; source?: Record<string, unknown> | null }): Readonly<object>;
persistTimedOutOperationQuarantineClearanceReceipt(clearResultOrReceipt: Record<string, unknown>, options?: { label?: string; createdAtMs?: number; reviewer?: string | null; source?: Record<string, unknown> | null; fields?: Record<string, unknown>; putOptions?: Record<string, unknown> }): Promise<Readonly<object>>;
restoreTimedOutOperationQuarantineClearanceReceiptFromBlockStore(ref: string | Record<string, unknown>, options?: { lane?: string; reason?: string; verifyBeforeRestore?: boolean; allowUnsafeUnverifiedRestore?: boolean; expectedReceiptFingerprint?: string; expectedPreClearanceFingerprint?: string; expectedReviewFingerprint?: string; expectedQuarantineFingerprint?: string; expectedPostClearanceFingerprint?: string; verifyOptions?: Record<string, unknown>; getOptions?: Record<string, unknown> }): Promise<Readonly<object>>;
clearedTimedOutOperationQuarantineClearanceReceipts(lane?: string): ReadonlyArray<Readonly<Record<string, unknown>>>;
createTimedOutOperationQuarantineReview(options?: { lane?: string; reviewer?: string; reason?: string; opId?: string | null; opIds?: string[] | null; operationReplayKey?: string | null; operationReplayKeys?: string[] | null; category?: string | null; categories?: string[] | null; allowLaneWide?: boolean; all?: boolean; allowAll?: boolean; reviewToken?: string | null }): Readonly<object>;
clearTimedOutOperationQuarantine(options?: { category?: string | null; categories?: string[] | null; lane?: string; opId?: string | null; opIds?: string[] | null; operationReplayKey?: string | null; operationReplayKeys?: string[] | null; reason?: string; reviewed?: boolean; reviewToken?: string | null; reviewFingerprint?: string | null; requireReviewFingerprint?: boolean; reviewManifest?: Record<string, unknown> | null; allowLaneWide?: boolean; all?: boolean; allowAll?: boolean }): Readonly<object>;
finalizeUnsettledTimedOutOperations(options?: { lane?: string; opId?: string | null; opIds?: string[] | null; operationReplayKey?: string | null; operationReplayKeys?: string[] | null; reason?: string; reviewed?: boolean; reviewToken?: string | null; reviewFingerprint?: string | null; requireReviewFingerprint?: boolean; reviewManifest?: Record<string, unknown> | null; allowLaneWide?: boolean; all?: boolean; allowAll?: boolean; errorCode?: string; message?: string }): Readonly<object>;
clearSuccessfulTimedOutOperations(options?: { lane?: string; opId?: string | null; opIds?: string[] | null; operationReplayKey?: string | null; operationReplayKeys?: string[] | null; reason?: string; reviewed?: boolean; reviewToken?: string | null; reviewFingerprint?: string | null; requireReviewFingerprint?: boolean; reviewManifest?: Record<string, unknown> | null; allowLaneWide?: boolean; all?: boolean; allowAll?: boolean }): Readonly<object>;
clearFailedTimedOutOperations(options?: { lane?: string; opId?: string | null; opIds?: string[] | null; operationReplayKey?: string | null; operationReplayKeys?: string[] | null; reason?: string; reviewed?: boolean; reviewToken?: string | null; reviewFingerprint?: string | null; requireReviewFingerprint?: boolean; reviewManifest?: Record<string, unknown> | null; allowLaneWide?: boolean; all?: boolean; allowAll?: boolean }): Readonly<object>;
recoverWhenStoreSettled(options?: { lane?: string; timeoutMs?: number; intervalMs?: number; reason?: string; requireHealthy?: boolean; requireTimedOutOperationsSettled?: boolean; requireNoSuccessfulTimedOutOperations?: boolean; requireNoFailedTimedOutOperations?: boolean }): Promise<Readonly<object>>;
close(reason?: string): Readonly<object>;
closeAsync(options?: { reason?: string }): Promise<Readonly<object>>;
snapshot(): Readonly<object>;
}
export function createOpfsBlockStoreStorageLaneAdapter(config?: Record<string, unknown>): OpfsBlockStoreStorageLaneAdapter;
export function validateOpfsStorageLaneAdapterSnapshot(snapshot: Record<string, unknown>): Readonly<{ ok: boolean; errors: string[] }>;
export const OPFS_STORAGE_LANE_ADAPTER_SUPPORTED_OPS: ReadonlyArray<string>;
export type BlockStoreLaneProviderOptions = Record<string, unknown> & { signal?: AbortSignal | null; abortSignal?: AbortSignal | null; compositeAbortSignal?: boolean; providerSignalComposed?: boolean; };
export type BlockStoreLaneScheduleOptions = Record<string, unknown> & { providerOptions?: BlockStoreLaneProviderOptions; storeOptions?: BlockStoreLaneProviderOptions; putOptions?: BlockStoreLaneProviderOptions; getOptions?: BlockStoreLaneProviderOptions; hasOptions?: BlockStoreLaneProviderOptions; verifyOptions?: BlockStoreLaneProviderOptions; deleteOptions?: BlockStoreLaneProviderOptions; estimateOptions?: BlockStoreLaneProviderOptions; cleanupOptions?: BlockStoreLaneProviderOptions; operationTimeoutMs?: number; timeoutMs?: number; abortProviderOnOperationTimeout?: boolean; };
export class BlockStoreLaneAdapter {
constructor(config?: { label?: string; store?: unknown; executor?: StorageLaneExecutor; scheduler?: CrossLaneScheduler; lane?: string; trace?: TraceLog | null; markUnhealthyOnError?: boolean; defaultOperationTimeoutMs?: number; operationTimeoutMs?: number; abortProviderOnOperationTimeout?: boolean; ownStore?: boolean });
readonly label: string;
readonly lane: string;
readonly closed: boolean;
readonly store: unknown;
readonly executor: StorageLaneExecutor;
readonly scheduler: CrossLaneScheduler;
schedulePut(bytes: Uint8Array | ArrayBuffer | ArrayBufferView | string, options?: BlockStoreLaneScheduleOptions): Readonly<object>;
scheduleGet(refOrDigest: string | Record<string, unknown>, options?: BlockStoreLaneScheduleOptions): Readonly<object>;
scheduleHas(refOrDigest: string | Record<string, unknown>, options?: BlockStoreLaneScheduleOptions): Readonly<object>;
scheduleVerify(refOrDigest: string | Record<string, unknown>, options?: BlockStoreLaneScheduleOptions): Readonly<object>;
scheduleDelete(refOrDigest: string | Record<string, unknown>, options?: BlockStoreLaneScheduleOptions): Readonly<object>;
scheduleEstimate(options?: BlockStoreLaneScheduleOptions): Readonly<object>;
scheduleCleanupForTest(options?: BlockStoreLaneScheduleOptions): Readonly<object>;
executeNext(): Promise<Readonly<object>>;
drain(options?: { maxSteps?: number }): Promise<Readonly<object>>;
result(opId: string): unknown;
markHealthy(lane?: string, reason?: string): Readonly<object>;
markUnhealthy(lane?: string, reason?: string): Readonly<object>;
successfulTimedOutOperations(lane?: string): ReadonlyArray<Readonly<Record<string, unknown>>>;
failedTimedOutOperations(lane?: string): ReadonlyArray<Readonly<Record<string, unknown>>>;
timedOutOperationQuarantine(lane?: string): Readonly<object>;
exportTimedOutOperationQuarantine(options?: { lane?: string; reason?: string }): Readonly<object>;
importTimedOutOperationQuarantine(ledger: object, options?: { lane?: string; reason?: string; markUnhealthy?: boolean; allowPartialImport?: boolean; allowEmptyImport?: boolean }): Readonly<object>;
persistTimedOutOperationQuarantine(options?: { ledger?: object; lane?: string; reason?: string; label?: string; fields?: Record<string, unknown>; putOptions?: Record<string, unknown> }): Promise<Readonly<object>>;
restoreTimedOutOperationQuarantineFromBlockStore(ref: string | Record<string, unknown>, options?: { lane?: string; reason?: string; markUnhealthy?: boolean; allowPartialImport?: boolean; allowEmptyImport?: boolean; verifyBeforeRestore?: boolean; allowUnsafeUnverifiedRestore?: boolean; expectedQuarantineFingerprint?: string; expectedReviewFingerprint?: string; expectedLedgerFingerprint?: string; verifyOptions?: Record<string, unknown>; getOptions?: Record<string, unknown> }): Promise<Readonly<object>>;
createTimedOutOperationQuarantineClearanceReceipt(clearResult: Record<string, unknown>, options?: { label?: string | null; createdAtMs?: number; reviewer?: string | null; source?: Record<string, unknown> | null }): Readonly<object>;
persistTimedOutOperationQuarantineClearanceReceipt(clearResultOrReceipt: Record<string, unknown>, options?: { label?: string; createdAtMs?: number; reviewer?: string | null; source?: Record<string, unknown> | null; fields?: Record<string, unknown>; putOptions?: Record<string, unknown> }): Promise<Readonly<object>>;
restoreTimedOutOperationQuarantineClearanceReceiptFromBlockStore(ref: string | Record<string, unknown>, options?: { lane?: string; reason?: string; verifyBeforeRestore?: boolean; allowUnsafeUnverifiedRestore?: boolean; expectedReceiptFingerprint?: string; expectedPreClearanceFingerprint?: string; expectedReviewFingerprint?: string; expectedQuarantineFingerprint?: string; expectedPostClearanceFingerprint?: string; verifyOptions?: Record<string, unknown>; getOptions?: Record<string, unknown> }): Promise<Readonly<object>>;
clearedTimedOutOperationQuarantineClearanceReceipts(lane?: string): ReadonlyArray<Readonly<Record<string, unknown>>>;
createTimedOutOperationQuarantineReview(options?: { lane?: string; reviewer?: string; reason?: string; opId?: string | null; opIds?: string[] | null; operationReplayKey?: string | null; operationReplayKeys?: string[] | null; category?: string | null; categories?: string[] | null; allowLaneWide?: boolean; all?: boolean; allowAll?: boolean; reviewToken?: string | null }): Readonly<object>;
clearTimedOutOperationQuarantine(options?: { category?: string | null; categories?: string[] | null; lane?: string; opId?: string | null; opIds?: string[] | null; operationReplayKey?: string | null; operationReplayKeys?: string[] | null; reason?: string; reviewed?: boolean; reviewToken?: string | null; reviewFingerprint?: string | null; requireReviewFingerprint?: boolean; reviewManifest?: Record<string, unknown> | null; allowLaneWide?: boolean; all?: boolean; allowAll?: boolean }): Readonly<object>;
finalizeUnsettledTimedOutOperations(options?: { lane?: string; opId?: string | null; opIds?: string[] | null; operationReplayKey?: string | null; operationReplayKeys?: string[] | null; reason?: string; reviewed?: boolean; reviewToken?: string | null; reviewFingerprint?: string | null; requireReviewFingerprint?: boolean; reviewManifest?: Record<string, unknown> | null; allowLaneWide?: boolean; all?: boolean; allowAll?: boolean; errorCode?: string; message?: string }): Readonly<object>;
clearSuccessfulTimedOutOperations(options?: { lane?: string; opId?: string | null; opIds?: string[] | null; operationReplayKey?: string | null; operationReplayKeys?: string[] | null; reason?: string; reviewed?: boolean; reviewToken?: string | null; reviewFingerprint?: string | null; requireReviewFingerprint?: boolean; reviewManifest?: Record<string, unknown> | null; allowLaneWide?: boolean; all?: boolean; allowAll?: boolean }): Readonly<object>;
clearFailedTimedOutOperations(options?: { lane?: string; opId?: string | null; opIds?: string[] | null; operationReplayKey?: string | null; operationReplayKeys?: string[] | null; reason?: string; reviewed?: boolean; reviewToken?: string | null; reviewFingerprint?: string | null; requireReviewFingerprint?: boolean; reviewManifest?: Record<string, unknown> | null; allowLaneWide?: boolean; all?: boolean; allowAll?: boolean }): Readonly<object>;
recoverWhenStoreSettled(options?: { lane?: string; timeoutMs?: number; intervalMs?: number; reason?: string; requireHealthy?: boolean; requireTimedOutOperationsSettled?: boolean; requireNoSuccessfulTimedOutOperations?: boolean; requireNoFailedTimedOutOperations?: boolean }): Promise<Readonly<object>>;
close(reason?: string): Readonly<object>;
closeAsync(options?: { reason?: string }): Promise<Readonly<object>>;
snapshot(): Readonly<object>;
}
export function createBlockStoreLaneAdapter(config?: Record<string, unknown>): BlockStoreLaneAdapter;
export function validateBlockStoreLaneAdapterSnapshot(snapshot: Record<string, unknown>): Readonly<{ ok: boolean; errors: string[]; resultCount: number }>;
export const BLOCK_STORE_LANE_ADAPTER_OPS: ReadonlyArray<string>;
export type QuarantineClearanceReceipt = Readonly<Record<string, unknown>>;
export type QuarantineClearanceReceiptRegistrationProvenance = Readonly<Record<string, unknown>>;
export function createTimedOutOperationQuarantineClearanceReceipt(clearResult: Record<string, unknown>, options?: Record<string, unknown>): QuarantineClearanceReceipt;
export function validateTimedOutOperationQuarantineClearanceReceipt(receipt?: Record<string, unknown>): Readonly<{ ok: boolean; errors: readonly string[]; receiptFingerprint: string; clearedCount: number; successfulClearedCount: number; failedClearedCount: number }>;
export function timedOutOperationQuarantineClearanceReceiptFingerprint(receipt?: Record<string, unknown>): string;
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
export type KernelKitSupportBundlePrivacyScrub = Readonly<Record<string, unknown>>;
export declare const KERNEL_KIT_SUPPORT_BUNDLE_PRIVACY_SCRUB_FORMAT: string;
export declare const KERNEL_KIT_SUPPORT_BUNDLE_PRIVACY_SCRUB_NON_CLAIMS: readonly string[];
export declare function createKernelKitSupportBundlePrivacyScrub(candidate?: string | Record<string, unknown>, fields?: Record<string, unknown>): KernelKitSupportBundlePrivacyScrub;
export declare function validateKernelKitSupportBundlePrivacyScrub(report?: Record<string, unknown>): KernelKitDemoProofValidation & Readonly<{ redactedFieldCount: number; format: string | null; status: string | null }>;
export type KernelKitLifecycleCheckpoint = Readonly<Record<string, unknown>>;
export declare const KERNEL_KIT_LIFECYCLE_CHECKPOINT_FORMAT: string;
export declare const KERNEL_KIT_LIFECYCLE_CHECKPOINT_NON_CLAIMS: readonly string[];
export declare const KERNEL_KIT_LIFECYCLE_CHECKPOINT_REQUIRED_ROWS: readonly string[];
export declare function createKernelKitLifecycleCheckpoint(input?: Record<string, unknown>, fields?: Record<string, unknown>): KernelKitLifecycleCheckpoint;
export declare function validateKernelKitLifecycleCheckpoint(checkpoint?: Record<string, unknown>): KernelKitDemoProofValidation & Readonly<{ rowCount: number; observedCount: number; deferredCount: number; failedCount: number; format: string | null; status: string | null }>;
export type KernelKitSessionCoordinationCheckpoint = Readonly<Record<string, unknown>>;
export declare const KERNEL_KIT_SESSION_COORDINATION_CHECKPOINT_FORMAT: 'browserrt-kernel-kit-session-coordination-checkpoint-v1';
export declare const KERNEL_KIT_SESSION_COORDINATION_CHECKPOINT_NON_CLAIMS: readonly string[];
export declare const KERNEL_KIT_SESSION_COORDINATION_CHECKPOINT_REQUIRED_ROWS: readonly string[];
export declare function createKernelKitSessionCoordinationCheckpoint(input?: Record<string, unknown>, fields?: Record<string, unknown>): KernelKitSessionCoordinationCheckpoint;
export declare function validateKernelKitSessionCoordinationCheckpoint(checkpoint?: Record<string, unknown>): KernelKitDemoProofValidation & Readonly<{ rowCount: number; observedCount: number; deferredCount: number; failedCount: number; format: string | null; status: string | null }>;
export type KernelKitRecoveryCheckpoint = Readonly<Record<string, unknown>>;
export declare const KERNEL_KIT_RECOVERY_CHECKPOINT_FORMAT: 'browserrt-kernel-kit-recovery-checkpoint-v1';
export declare const KERNEL_KIT_RECOVERY_CHECKPOINT_NON_CLAIMS: readonly string[];
export declare const KERNEL_KIT_RECOVERY_CHECKPOINT_REQUIRED_ROWS: readonly string[];
export declare function createKernelKitRecoveryCheckpoint(input?: Record<string, unknown>, fields?: Record<string, unknown>): KernelKitRecoveryCheckpoint;
export declare function validateKernelKitRecoveryCheckpoint(checkpoint?: Record<string, unknown>): KernelKitDemoProofValidation & Readonly<{ rowCount: number; observedCount: number; deferredCount: number; failedCount: number; format: string | null; status: string | null }>;
export type KernelKitAdmissionCancellationCheckpoint = Readonly<Record<string, unknown>>;
export declare const KERNEL_KIT_ADMISSION_CANCELLATION_CHECKPOINT_FORMAT: 'browserrt-kernel-kit-admission-cancellation-checkpoint-v1';
export declare const KERNEL_KIT_ADMISSION_CANCELLATION_CHECKPOINT_NON_CLAIMS: readonly string[];
export declare const KERNEL_KIT_ADMISSION_CANCELLATION_CHECKPOINT_REQUIRED_ROWS: readonly string[];
export declare function createKernelKitAdmissionCancellationCheckpoint(input?: Record<string, unknown>, fields?: Record<string, unknown>): KernelKitAdmissionCancellationCheckpoint;
export declare function validateKernelKitAdmissionCancellationCheckpoint(checkpoint?: Record<string, unknown>): KernelKitDemoProofValidation & Readonly<{ rowCount: number; observedCount: number; deferredCount: number; failedCount: number; format: string | null; status: string | null }>;
export type KernelKitSupportBundleEvidenceLedger = Readonly<Record<string, unknown>>;
export declare const KERNEL_KIT_SUPPORT_BUNDLE_EVIDENCE_LEDGER_FORMAT: string;
export declare const KERNEL_KIT_SUPPORT_BUNDLE_EVIDENCE_LEDGER_NON_CLAIMS: readonly string[];
export declare function createKernelKitSupportBundleEvidenceLedger(candidate?: string | Record<string, unknown>, fields?: Record<string, unknown>): KernelKitSupportBundleEvidenceLedger;
export declare function validateKernelKitSupportBundleEvidenceLedger(report?: Record<string, unknown>): KernelKitDemoProofValidation & Readonly<{ entryCount: number; outputCount: number; format: string | null; status: string | null }>;
export type KernelKitSupportBundleEvidenceCheckpoint = Readonly<Record<string, unknown>>;
export declare const KERNEL_KIT_SUPPORT_BUNDLE_EVIDENCE_CHECKPOINT_FORMAT: string;
export declare const KERNEL_KIT_SUPPORT_BUNDLE_EVIDENCE_CHECKPOINT_NON_CLAIMS: readonly string[];
export declare function createKernelKitSupportBundleEvidenceCheckpoint(candidate?: string | Record<string, unknown>, artifacts?: Record<string, unknown> | readonly Record<string, unknown>[], fields?: Record<string, unknown>): KernelKitSupportBundleEvidenceCheckpoint;
export declare function validateKernelKitSupportBundleEvidenceCheckpoint(report?: Record<string, unknown>): KernelKitDemoProofValidation & Readonly<{ rowCount: number; satisfiedCount: number; deferredCount: number; missingCount: number; format: string | null; status: string | null }>;
export type KernelKitSupportBundleReplayPlan = Readonly<Record<string, unknown>>;
export declare const KERNEL_KIT_SUPPORT_BUNDLE_REPLAY_FORMAT: string;
export declare const KERNEL_KIT_SUPPORT_BUNDLE_REPLAY_NON_CLAIMS: readonly string[];
export declare const KERNEL_KIT_SUPPORT_BUNDLE_REPLAY_PHASE_IDS: readonly string[];
export declare function createKernelKitSupportBundleReplayPlan(candidate?: string | Record<string, unknown>, fields?: Record<string, unknown>): KernelKitSupportBundleReplayPlan;
export declare function validateKernelKitSupportBundleReplayPlan(report?: Record<string, unknown>): KernelKitDemoProofValidation & Readonly<{ phaseCount: number; commandCount: number; format: string | null; status: string | null }>;
export type KernelKitSupportBundleOperatorPreflightDisplaySnapshot = Readonly<Record<string, unknown>>;
export declare const KERNEL_KIT_SUPPORT_BUNDLE_OPERATOR_PREFLIGHT_DISPLAY_SNAPSHOT_FORMAT: 'browserrt-kernel-kit-support-bundle-operator-preflight-display-snapshot-v1';
export declare function createKernelKitSupportBundleOperatorPreflightDisplaySnapshot(candidate?: string | Record<string, unknown>, fields?: Record<string, unknown>): KernelKitSupportBundleOperatorPreflightDisplaySnapshot;
export declare function validateKernelKitSupportBundleOperatorPreflightDisplaySnapshot(report?: Record<string, unknown>): KernelKitDemoProofValidation & Readonly<{ rowCount: number; format: string | null; status: string | null }>;
export type KernelKitSupportBundleOperatorReplayGate = Readonly<Record<string, unknown>>;
export declare const KERNEL_KIT_SUPPORT_BUNDLE_OPERATOR_REPLAY_GATE_FORMAT: 'browserrt-kernel-kit-support-bundle-operator-replay-gate-v1';
export declare function createKernelKitSupportBundleOperatorReplayGate(candidate?: string | Record<string, unknown>, fields?: Record<string, unknown>): KernelKitSupportBundleOperatorReplayGate;
export declare function validateKernelKitSupportBundleOperatorReplayGate(report?: Record<string, unknown>): KernelKitDemoProofValidation & Readonly<{ rowCount: number; format: string | null; status: string | null }>;
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
export type KernelKitHandoffMarkdownImportReport = Readonly<Record<string, unknown>>;
export declare const KERNEL_KIT_HANDOFF_MARKDOWN_IMPORT_FORMAT: string;
export declare const KERNEL_KIT_HANDOFF_MARKDOWN_IMPORT_NON_CLAIMS: readonly string[];
export declare const KERNEL_KIT_HANDOFF_MARKDOWN_REQUIRED_COMMANDS: readonly string[];
export declare function createKernelKitHandoffMarkdownImportReport(input?: string | Record<string, unknown>, fields?: Record<string, unknown>): KernelKitHandoffMarkdownImportReport;
export declare function validateKernelKitHandoffMarkdownImportReport(report?: Record<string, unknown>): KernelKitDemoProofValidation & Readonly<{ commandCount: number; parsedCommandCount: number; riskCount: number; sectionCount: number; markdownBytes: number; status: string | null; format: string | null }>;
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
export type KernelKitReadinessGate = Readonly<Record<string, unknown>>;
export declare const KERNEL_KIT_READINESS_GATE_FORMAT: string;
export declare const KERNEL_KIT_READINESS_GATE_NON_CLAIMS: readonly string[];
export declare const KERNEL_KIT_READINESS_GATE_REQUIRED_GATES: readonly string[];
export declare const KERNEL_KIT_READINESS_GATE_PERSONAS: readonly string[];
export declare function createKernelKitReadinessGate(fields?: Record<string, unknown>): KernelKitReadinessGate;
export declare function validateKernelKitReadinessGate(report?: Record<string, unknown>): KernelKitDemoProofValidation & Readonly<{ gateCount: number; personaCount: number; commandCount: number; status: string | null; format: string | null }>;
export type KernelKitReadinessContrast = Readonly<Record<string, unknown>>;
export declare const KERNEL_KIT_READINESS_CONTRAST_FORMAT: string;
export declare const KERNEL_KIT_READINESS_CONTRAST_NON_CLAIMS: readonly string[];
export declare const KERNEL_KIT_READINESS_CONTRAST_DEFAULT_FAILED_GATES: readonly string[];
export declare function createDegradedKernelKitReadinessGate(readinessGate?: Record<string, unknown>, fields?: Record<string, unknown>): KernelKitReadinessGate;
export declare function createKernelKitReadinessContrast(fields?: Record<string, unknown>): KernelKitReadinessContrast;
export declare function validateKernelKitReadinessContrast(report?: Record<string, unknown>): KernelKitDemoProofValidation & Readonly<{ changedGateCount: number; missingGateCount: number; commandCount: number; status: string | null; format: string | null }>;
export type StorageLaneTimedOutOperationOrphanedCode = 'BRT_STORAGE_TIMED_OUT_OPERATION_ORPHANED';
