import { createStorageLaneExecutor, validateStorageLaneExecutorSnapshot, timedOutQuarantineFingerprint } from './storage-lane-scheduler.mjs';
const BLOCK_STORE_OPS = Object.freeze(['put', 'get', 'has', 'verify', 'delete', 'estimate', 'snapshot', 'cleanup']);
const BLOCK_STORE_OP_SET = new Set(BLOCK_STORE_OPS);
function assertScheduler(scheduler) {
  if (!scheduler || typeof scheduler.enqueue !== 'function' || typeof scheduler.dispatchNext !== 'function' || typeof scheduler.complete !== 'function') {
    throw new Error('BlockStoreLaneAdapter requires a CrossLaneScheduler-like scheduler when no executor is supplied');
  }
}
function assertStore(store, methods = ['put', 'get', 'has', 'verify', 'delete', 'snapshot']) {
  for (const method of methods) {
    if (!store || typeof store[method] !== 'function') throw new Error(`BlockStoreLaneAdapter requires a store with ${method}()`);
  }
}
function payloadBytes(value) {
  if (typeof value === 'string') return new TextEncoder().encode(value).byteLength;
  if (value instanceof ArrayBuffer) return value.byteLength;
  if (ArrayBuffer.isView(value)) return value.byteLength;
  if (value && typeof value === 'object' && Number.isFinite(value.bytes)) return Number(value.bytes);
  return 1;
}
function summarize(value) {
  if (value instanceof Uint8Array) return { kind: 'Uint8Array', bytes: value.byteLength };
  if (value instanceof ArrayBuffer) return { kind: 'ArrayBuffer', bytes: value.byteLength };
  if (value == null || typeof value !== 'object') return { value };
  const out = {};
  for (const key of ['digest', 'hash', 'bytes', 'duplicate', 'present', 'ok', 'deleted', 'quota', 'usage', 'path', 'provider', 'blockCount', 'opened', 'available']) {
    if (Object.hasOwn(value, key)) out[key] = value[key];
  }
  if (value.ref && typeof value.ref === 'object') out.ref = { id: value.ref.id, digest: value.ref.digest, hash: value.ref.hash, backend: value.ref.backend, bytes: value.ref.bytes, path: value.ref.path };
  return out;
}
function optionBag(value, label) {
  if (value === undefined || value === null) return {};
  if (typeof value !== 'object' || Array.isArray(value)) throw new Error(`${label} must be an object when supplied`);
  return { ...value };
}
function scheduledProviderOptions(options = {}, op = 'operation') {
  const providerOptions = optionBag(options.providerOptions, 'providerOptions');
  const storeOptions = optionBag(options.storeOptions, 'storeOptions');
  const namedOptions = optionBag(options[`${op}Options`], `${op}Options`);
  return Object.freeze({ ...providerOptions, ...storeOptions, ...namedOptions });
}
function providerOptionKeys(options = {}) {
  return Object.freeze(Object.keys(options || {}).filter((key) => key !== 'signal' && key !== 'abortSignal').sort());
}
const SCHEDULED_COMPOSITE_ABORT_CLEANUP = Symbol('BrowserRT.scheduledCompositeAbortCleanup');
function isAbortSignalLike(value) {
  return value && typeof value === 'object' && typeof value.aborted === 'boolean' && typeof value.addEventListener === 'function';
}
function abortReason(signal, fallback) {
  if (!signal || typeof signal !== 'object') return fallback;
  return 'reason' in signal ? signal.reason : fallback;
}
function composeAbortSignals(signals = []) {
  const uniqueSignals = [];
  const seen = new Set();
  for (const signal of signals) {
    if (!isAbortSignalLike(signal) || seen.has(signal)) continue;
    seen.add(signal);
    uniqueSignals.push(signal);
  }
  if (uniqueSignals.length === 0) return Object.freeze({ signal: null, cleanup: null, composed: false });
  if (uniqueSignals.length === 1) return Object.freeze({ signal: uniqueSignals[0], cleanup: null, composed: false });
  if (typeof AbortSignal === 'function' && typeof AbortSignal.any === 'function') {
    return Object.freeze({ signal: AbortSignal.any(uniqueSignals), cleanup: null, composed: true, nativeAny: true });
  }
  if (typeof AbortController !== 'function') return Object.freeze({ signal: uniqueSignals[0], cleanup: null, composed: false, degraded: true });
  const controller = new AbortController();
  const listeners = [];
  const abortFrom = (signal) => {
    if (controller.signal.aborted) return;
    try { controller.abort(abortReason(signal, new Error('BrowserRT scheduled provider signal aborted'))); } catch { controller.abort(); }
  };
  for (const signal of uniqueSignals) {
    if (signal.aborted) { abortFrom(signal); continue; }
    const listener = () => abortFrom(signal);
    signal.addEventListener('abort', listener, { once: true });
    listeners.push([signal, listener]);
  }
  const cleanup = () => {
    for (const [signal, listener] of listeners.splice(0)) {
      try { signal.removeEventListener('abort', listener); } catch {}
    }
  };
  return Object.freeze({ signal: controller.signal, cleanup, composed: true, nativeAny: false });
}
function withScheduledContextOptions(providerOptions = {}, context = {}) {
  const out = { ...(providerOptions || {}) };
  const providerSignalSupplied = Object.prototype.hasOwnProperty.call(out, 'signal');
  const providerAbortSignalSupplied = Object.prototype.hasOwnProperty.call(out, 'abortSignal');
  const providerSignals = [];
  if (providerSignalSupplied && out.signal !== null && out.signal !== undefined) providerSignals.push(out.signal);
  if (providerAbortSignalSupplied && out.abortSignal !== null && out.abortSignal !== undefined) providerSignals.push(out.abortSignal);
  const invalidProviderSignals = providerSignals.filter((signal) => !isAbortSignalLike(signal));
  const contextSignal = context?.signal ?? context?.abortSignal ?? null;
  // Preserve invalid caller signal shape for the underlying provider to reject; do not mask it with a timeout signal.
  if (invalidProviderSignals.length > 0) {
    if (context?.operationTimeoutMs !== undefined && context?.operationTimeoutMs !== null) out.operationTimeoutMs = context.operationTimeoutMs;
    else if (!Object.prototype.hasOwnProperty.call(out, 'operationTimeoutMs')) out.operationTimeoutMs = null;
    return out;
  }
  const composition = composeAbortSignals([...providerSignals, contextSignal]);
  if (composition.signal) {
    out.signal = composition.signal;
    out.abortSignal = composition.signal;
    if (composition.composed) {
      out.compositeAbortSignal = true;
      out.providerSignalComposed = true;
    }
    if (composition.cleanup) Object.defineProperty(out, SCHEDULED_COMPOSITE_ABORT_CLEANUP, { value: composition.cleanup, enumerable: false });
  } else if (!Object.prototype.hasOwnProperty.call(out, 'signal') && !Object.prototype.hasOwnProperty.call(out, 'abortSignal')) {
    out.signal = null;
  }
  if (context?.operationTimeoutMs !== undefined && context?.operationTimeoutMs !== null) out.operationTimeoutMs = context.operationTimeoutMs;
  else if (!Object.prototype.hasOwnProperty.call(out, 'operationTimeoutMs')) out.operationTimeoutMs = null;
  return out;
}
async function callStoreWithScheduledContextOptions(providerOptions, context, call) {
  const options = withScheduledContextOptions(providerOptions, context);
  try { return await call(options); }
  finally {
    const cleanup = options?.[SCHEDULED_COMPOSITE_ABORT_CLEANUP];
    if (typeof cleanup === 'function') cleanup();
  }
}
function encodeJsonBytes(value) { return new TextEncoder().encode(JSON.stringify(value, null, 2) + '\n'); }
function decodeJsonBytes(bytes) {
  const view = bytes instanceof Uint8Array ? bytes : bytes instanceof ArrayBuffer ? new Uint8Array(bytes) : ArrayBuffer.isView(bytes) ? new Uint8Array(bytes.buffer, bytes.byteOffset, bytes.byteLength) : new TextEncoder().encode(String(bytes));
  return JSON.parse(new TextDecoder().decode(view));
}
function assertQuarantineLedger(ledger) {
  if (!ledger || typeof ledger !== 'object') throw new Error('timed-out operation quarantine ledger must be an object');
  if (ledger.schema !== 'brt.storageLane.timedOutOperationQuarantine.v1') throw new Error(`unsupported timed-out operation quarantine ledger schema: ${ledger?.schema}`);
  return ledger;
}
function describeError(error) {
  return Object.freeze({ name: error?.name || 'Error', message: error?.message || String(error), code: error?.code ?? null, storageDisposition: error?.storageDisposition ?? null });
}
function blockRefDigest(ref) {
  if (typeof ref === 'string') return ref;
  if (!ref || typeof ref !== 'object') return null;
  return ref.digest ?? ref.ref?.digest ?? ref.hash ?? ref.ref?.hash ?? ref.id ?? ref.ref?.id ?? null;
}
function summarizeBlockVerify(value) {
  if (!value || typeof value !== 'object') return Object.freeze({ ok: false, present: null, digest: null, bytes: null, reason: 'verify-result-missing' });
  return Object.freeze({
    ok: value.ok === true,
    present: value.present ?? null,
    digest: value.digest ?? null,
    actualDigest: value.actualDigest ?? null,
    bytes: Number.isFinite(Number(value.bytes)) ? Number(value.bytes) : null,
    path: value.path ?? null,
    reason: value.reason ?? null
  });
}
function nonEmptyString(value) { return value == null ? null : (String(value).trim() || null); }
function blankExpectedFingerprintOption(options = {}, keys = []) {
  for (const key of keys) {
    if (!Object.hasOwn(options, key)) continue;
    const value = options[key];
    if (typeof value === 'string' && value.trim() === '') return Object.freeze({ key, supplied: value });
  }
  return null;
}
function expectedFingerprintMismatch(expected, actual) {
  const e = nonEmptyString(expected);
  if (!e) return null;
  const a = nonEmptyString(actual);
  return a === e ? null : Object.freeze({ expected: e, actual: a });
}
const CLEARANCE_RECEIPT_SCHEMA = 'brt.storageLane.timedOutOperationQuarantine.clearanceReceipt.v1';
const CLEARANCE_RECEIPT_REGISTRATION_PROVENANCE_SCHEMA = 'brt.storageLane.timedOutOperationQuarantine.clearanceReceipt.registrationProvenance.v1';
function stableStringify(value) { if (Array.isArray(value)) return `[${value.map(stableStringify).join(',')}]`; if (value && typeof value === 'object') return `{${Object.keys(value).sort().map((key) => `${JSON.stringify(key)}:${stableStringify(value[key])}`).join(',')}}`; return JSON.stringify(value); }
function fnv1a64Hex(text) { let hash = 0xcbf29ce484222325n; const prime = 0x100000001b3n; for (const byte of new TextEncoder().encode(String(text))) { hash ^= BigInt(byte); hash = (hash * prime) & 0xffffffffffffffffn; } return hash.toString(16).padStart(16, '0'); }
function clearanceRow(row) { if (!row || typeof row !== 'object') return row; return Object.freeze({ opId: row.opId == null ? null : String(row.opId), kind: row.kind ?? row.op ?? null, lane: row.lane ?? null, operationEpoch: row.operationEpoch == null ? null : String(row.operationEpoch), operationReplayKey: row.operationReplayKey == null ? null : String(row.operationReplayKey), disposition: row.disposition ?? null, summary: row.summary ?? null, error: row.error ?? null }); }
function clearanceRowSortKey(row) { const opId = row?.opId == null ? '' : String(row.opId); const replay = row?.operationReplayKey == null ? '' : String(row.operationReplayKey); const epoch = row?.operationEpoch == null ? '' : String(row.operationEpoch); const lane = row?.lane == null ? '' : String(row.lane); const kind = row?.kind == null ? 'operation' : String(row.kind); return `${opId}\0${replay}\0${epoch}\0${lane}\0${kind}`; }
function expectedClearanceOperationReplayKey(row) { const opId = row?.opId == null ? '' : String(row.opId); const lane = row?.lane == null ? '' : String(row.lane); const kind = row?.kind == null ? 'operation' : String(row.kind); const epoch = row?.operationEpoch == null ? '' : String(row.operationEpoch); if (epoch) return `operation:${lane}:${kind}:${epoch}:${opId}`; return `operation-legacy:${lane}:${kind}:${opId}`; }
function clearanceOperationReplayKey(row) { if (row?.operationReplayKey != null && String(row.operationReplayKey)) return String(row.operationReplayKey); return expectedClearanceOperationReplayKey(row); }
function uniqueSortedStrings(values) { return Object.freeze([...new Set((values || []).map(String).filter(Boolean))].sort()); }
function arraysEqual(a = [], b = []) { return a.length === b.length && a.every((value, index) => value === b[index]); }
function clearanceRowsOperationReplayKeys(rows = []) { return uniqueSortedStrings(rows.map((row) => clearanceOperationReplayKey(row))); }
function normalizedClearanceReceiptPayload(receipt = {}) { return { schema: CLEARANCE_RECEIPT_SCHEMA, lane: receipt.lane ?? null, reviewToken: receipt.reviewToken ?? null, reviewFingerprint: receipt.reviewFingerprint ?? null, preClearanceFingerprint: receipt.preClearanceFingerprint ?? null, postClearanceFingerprint: receipt.postClearanceFingerprint ?? null, categories: Array.isArray(receipt.categories) ? [...receipt.categories].map(String).sort() : [], opIds: Array.isArray(receipt.opIds) ? [...receipt.opIds].map(String).sort() : [], operationReplayKeys: Array.isArray(receipt.operationReplayKeys) ? [...receipt.operationReplayKeys].map(String).sort() : [], allowLaneWide: receipt.allowLaneWide === true, cleared: { successful: Array.isArray(receipt.cleared?.successful) ? receipt.cleared.successful.map(clearanceRow).sort((a, b) => clearanceRowSortKey(a).localeCompare(clearanceRowSortKey(b))) : [], failed: Array.isArray(receipt.cleared?.failed) ? receipt.cleared.failed.map(clearanceRow).sort((a, b) => clearanceRowSortKey(a).localeCompare(clearanceRowSortKey(b))) : [] }, counts: receipt.counts && typeof receipt.counts === 'object' ? receipt.counts : null }; }
export function timedOutOperationQuarantineClearanceReceiptFingerprint(receipt = {}) { return `brt-qclear-v1:${fnv1a64Hex(stableStringify(normalizedClearanceReceiptPayload(receipt)))}`; }
function inferClearanceReceiptLane(clearResult, clearedSuccessful = [], clearedFailed = []) {
  if (clearResult?.lane != null) return String(clearResult.lane);
  const lanes = new Set([...clearedSuccessful, ...clearedFailed].map((row) => row?.lane == null ? null : String(row.lane)).filter(Boolean));
  if (lanes.size === 1) return [...lanes][0];
  return null;
}
export function createTimedOutOperationQuarantineClearanceReceipt(clearResult, { label = null, createdAtMs = Date.now(), reviewer = null, source = null } = {}) {
  if (!clearResult || clearResult.ok !== true) throw new Error('clearance receipt requires an ok clearTimedOutOperationQuarantine result');
  if (Number(clearResult.clearedCount ?? 0) <= 0) throw new Error('clearance receipt requires at least one cleared timed-out quarantine row');
  const clearedSuccessful = Array.isArray(clearResult.cleared?.successful) ? clearResult.cleared.successful.map(clearanceRow) : [];
  const clearedFailed = Array.isArray(clearResult.cleared?.failed) ? clearResult.cleared.failed.map(clearanceRow) : [];
  const clearedOperationReplayKeys = clearanceRowsOperationReplayKeys(clearedSuccessful.concat(clearedFailed));
  const receiptLane = inferClearanceReceiptLane(clearResult, clearedSuccessful, clearedFailed);
  const base = Object.freeze({ schema: CLEARANCE_RECEIPT_SCHEMA, createdAtMs, label, reviewer, lane: receiptLane, reviewToken: clearResult.reviewToken ?? null, reviewFingerprint: clearResult.reviewFingerprint ?? clearResult.requiredReviewFingerprint ?? null, requiredReviewFingerprint: clearResult.requiredReviewFingerprint ?? clearResult.reviewFingerprint ?? null, preClearanceFingerprint: clearResult.requiredReviewFingerprint ?? clearResult.reviewFingerprint ?? null, postClearanceFingerprint: clearResult.quarantine?.reviewFingerprint ?? clearResult.quarantine?.quarantineFingerprint ?? null, categories: Object.freeze([...(clearResult.categories || [])].map(String).sort()), opIds: Object.freeze([...(clearResult.opIds || [])].map(String).sort()), operationReplayKeys: clearedOperationReplayKeys, allowLaneWide: clearResult.allowLaneWide === true, clearedCount: clearResult.clearedCount ?? clearedSuccessful.length + clearedFailed.length, successfulClearedCount: clearResult.successfulClearedCount ?? clearedSuccessful.length, failedClearedCount: clearResult.failedClearedCount ?? clearedFailed.length, counts: Object.freeze({ total: clearResult.clearedCount ?? clearedSuccessful.length + clearedFailed.length, successful: clearedSuccessful.length, failed: clearedFailed.length }), cleared: Object.freeze({ successful: Object.freeze(clearedSuccessful), failed: Object.freeze(clearedFailed) }), source });
  const receiptFingerprint = timedOutOperationQuarantineClearanceReceiptFingerprint(base);
  return Object.freeze({ ...base, receiptFingerprint });
}
export function validateTimedOutOperationQuarantineClearanceReceipt(receipt = {}) {
  const errors = [];
  if (!receipt || typeof receipt !== 'object') errors.push('receipt must be an object');
  if (receipt?.schema !== CLEARANCE_RECEIPT_SCHEMA) errors.push(`schema must be ${CLEARANCE_RECEIPT_SCHEMA}`);
  if (!receipt?.receiptFingerprint || typeof receipt.receiptFingerprint !== 'string') errors.push('receiptFingerprint must be present');
  for (const key of ['reviewToken','reviewFingerprint','preClearanceFingerprint','postClearanceFingerprint']) if (!receipt?.[key] || typeof receipt[key] !== 'string') errors.push(`${key} must be present`);
  const successful = Array.isArray(receipt?.cleared?.successful) ? receipt.cleared.successful : [];
  const failed = Array.isArray(receipt?.cleared?.failed) ? receipt.cleared.failed : [];
  const allRows = successful.concat(failed);
  const receiptLane = receipt?.lane == null ? null : String(receipt.lane);
  const allowLaneWide = receipt?.allowLaneWide === true;
  if (!receiptLane) errors.push('receipt lane must be present; lane-wide receipts are lane-scoped, not lane-ambiguous');
  if (allRows.length <= 0) errors.push('receipt must clear at least one timed-out quarantine row');
  const opIds = new Set();
  const operationKeys = new Set();
  for (const row of allRows) {
    const opId = row?.opId == null ? '' : String(row.opId);
    if (!opId) errors.push('cleared row opId must be present'); else opIds.add(opId);
    const expectedKey = expectedClearanceOperationReplayKey(row);
    const operationKey = opId ? clearanceOperationReplayKey(row) : '';
    if (operationKey && expectedKey && operationKey !== expectedKey) errors.push(`cleared row operationReplayKey mismatch for ${opId}`);
    if (operationKey) { if (operationKeys.has(operationKey)) errors.push(`duplicate cleared operationReplayKey ${operationKey}`); else operationKeys.add(operationKey); }
    const rowLane = row?.lane == null ? null : String(row.lane);
    if (!rowLane) errors.push('cleared row lane must be present'); else if (receiptLane && rowLane !== receiptLane) errors.push(`cleared row lane ${rowLane} must match receipt lane ${receiptLane}`);
  }
  const explicitOpIds = Array.isArray(receipt?.opIds) ? receipt.opIds.map(String).sort() : [];
  const rowOpIds = [...opIds].sort();
  if (explicitOpIds.length > 0 && !arraysEqual(explicitOpIds, rowOpIds)) errors.push('opIds must match cleared row opIds');
  const explicitOperationReplayKeys = Array.isArray(receipt?.operationReplayKeys) ? uniqueSortedStrings(receipt.operationReplayKeys) : [];
  const rowOperationReplayKeys = uniqueSortedStrings([...operationKeys]);
  if (!arraysEqual(explicitOperationReplayKeys, rowOperationReplayKeys)) errors.push('operationReplayKeys must match cleared row operationReplayKeys');
  const categories = Array.isArray(receipt?.categories) ? receipt.categories.map(String) : [];
  const allowedCategories = new Set(['all', 'successful', 'failed']);
  for (const category of categories) if (!allowedCategories.has(category)) errors.push(`unsupported clearance receipt category ${category}`);
  const counts = receipt?.counts || {};
  if (Number(counts.successful) !== successful.length) errors.push('counts.successful mismatch');
  if (Number(counts.failed) !== failed.length) errors.push('counts.failed mismatch');
  if (Number(counts.total) !== allRows.length) errors.push('counts.total mismatch');
  if (Number(receipt?.clearedCount ?? allRows.length) !== allRows.length) errors.push('clearedCount mismatch');
  if (Number(receipt?.successfulClearedCount ?? successful.length) !== successful.length) errors.push('successfulClearedCount mismatch');
  if (Number(receipt?.failedClearedCount ?? failed.length) !== failed.length) errors.push('failedClearedCount mismatch');
  if (receipt?.preClearanceFingerprint && receipt?.reviewFingerprint && String(receipt.preClearanceFingerprint) !== String(receipt.reviewFingerprint)) errors.push('preClearanceFingerprint must match reviewFingerprint');
  const expected = timedOutOperationQuarantineClearanceReceiptFingerprint(receipt || {});
  if (receipt?.receiptFingerprint && String(receipt.receiptFingerprint) !== expected) errors.push('receiptFingerprint mismatch');
  return Object.freeze({ ok: errors.length === 0, errors: Object.freeze(errors), receiptFingerprint: expected, receiptLane, allowLaneWide, operationReplayKeys: rowOperationReplayKeys, clearedCount: allRows.length, successfulClearedCount: successful.length, failedClearedCount: failed.length });
}
export class BlockStoreLaneAdapter {
  #trace;
  #store;
  #executor;
  #results = new Map();
  #lateResults = new Map();
  #nextOpSeq = 1;
  #closed = false;
  #ownStore = false;
  constructor({ label = 'block-store-lane-adapter', store, executor = null, scheduler = null, lane = 'storage', trace = null, markUnhealthyOnError = true, defaultOperationTimeoutMs = 0, operationTimeoutMs = undefined, abortProviderOnOperationTimeout = false, ownStore = undefined } = {}) {
    assertStore(store, ['put', 'get', 'has', 'verify', 'delete', 'snapshot']);
    if (!executor) assertScheduler(scheduler);
    this.label = label;
    this.lane = lane;
    this.#ownStore = ownStore === undefined ? false : ownStore !== false;
    this.#store = store;
    this.#executor = executor || createStorageLaneExecutor({ label: `${label}:executor`, scheduler, mailbox: null, lane, trace, markUnhealthyOnError, defaultOperationTimeoutMs, operationTimeoutMs, abortProviderOnOperationTimeout });
    this.#trace = trace;
    this.stats = { scheduled: 0, rejected: 0, completed: 0, failed: 0, emptyDispatches: 0, lateCompletions: 0, lateFailures: 0, quarantineLedgerPersists: 0, quarantineLedgerRestores: 0, quarantineLedgerRestoreFailures: 0, quarantineLedgerRestoreRejected: 0, quarantineLedgerRestoreBlockIntegrityRejected: 0, quarantineLedgerRestoreVerifications: 0, quarantineLedgerRestoreUnverifiedRejected: 0, quarantineLedgerRestoreUnverifiedAccepted: 0, quarantineLedgerRestoreExpectedFingerprintRejected: 0, quarantineReviewManifests: 0, quarantineOrphanFinalizations: 0, quarantineClearanceReceiptsCreated: 0, quarantineClearanceReceiptPersists: 0, quarantineClearanceReceiptRestores: 0, quarantineClearanceReceiptRestoreRejected: 0, quarantineClearanceReceiptRestoreFailures: 0, quarantineClearanceReceiptRestoreBlockIntegrityRejected: 0, quarantineClearanceReceiptRestoreVerifications: 0, quarantineClearanceReceiptRestoreUnverifiedRejected: 0, quarantineClearanceReceiptRestoreUnverifiedAccepted: 0, quarantineClearanceReceiptRestoreExpectedFingerprintRejected: 0, quarantineClearanceReceiptReplayRejected: 0, quarantineClearanceReceiptRegistrationRejectedOnRestore: 0, closeCalls: 0, closedOperationRejects: 0 };
    this.#emit('block-store-lane:create', { store: this.storeName, provider: this.providerName, lane, defaultOperationTimeoutMs: this.#executor.defaultOperationTimeoutMs ?? 0 });
  }
  get store() { return this.#store; }
  get executor() { return this.#executor; }
  get scheduler() { return this.#executor.scheduler; }
  get storeName() { return this.#store.name || this.#store.label || 'unnamed-block-store'; }
  get providerName() { return this.#store.provider || this.#store.name || 'unknown-block-provider'; }
  get closed() { return this.#closed; }
  #throwIfClosed(op = 'operation') {
    if (!this.#closed) return;
    this.stats.closedOperationRejects += 1;
    const error = new Error(`BlockStoreLaneAdapter ${this.label} is closed`);
    error.name = 'BrowserRTBlockStoreLaneAdapterError';
    error.code = 'BRT_BLOCK_STORE_LANE_ADAPTER_CLOSED';
    error.detail = { label: this.label, lane: this.lane, op, store: this.storeName, provider: this.providerName };
    this.#emit('block-store-lane:closed-reject', error.detail);
    throw error;
  }
  #emit(kind, payload = {}) { this.#trace?.emit(kind, { label: this.label, lane: this.lane, ...payload }); }
  #opId(kind, id) { return id || `${this.label}:${kind}:${this.#nextOpSeq++}`; }
  schedule(kind, run, { id = null, priority = 'background', cost = 1, dependsOn = [], lane = this.lane, fallbackLanes = [], metadata = null, operationTimeoutMs = undefined, timeoutMs = undefined, abortProviderOnOperationTimeout = undefined } = {}) {
    this.#throwIfClosed(kind);
    if (!BLOCK_STORE_OP_SET.has(kind)) throw new Error(`Unsupported block-store lane op: ${kind}`);
    const opId = this.#opId(kind, id);
    const accepted = this.#executor.scheduleOperation({
      id: opId,
      kind: `block-${kind}`,
      lane,
      fallbackLanes,
      priority,
      cost,
      dependsOn,
      flowId: 'block-store',
      metadata: { component: 'BlockStoreLaneAdapter', blockStoreOp: kind, store: this.storeName, provider: this.providerName, ...(metadata || {}) },
      operationTimeoutMs,
      timeoutMs,
      abortProviderOnOperationTimeout,
      run: async (context = {}) => {
        const timedOut = () => context?.timedOut === true || (typeof context?.isTimedOut === 'function' && context.isTimedOut() === true);
        this.#emit('block-store-lane:op-start', { opId, op: kind, store: this.storeName, provider: this.providerName });
        try {
          const value = await run(context);
          if (timedOut()) {
            const row = Object.freeze({ opId, op: kind, value, summary: summarize(value), settledAt: new Date().toISOString(), disposition: 'late-provider-complete-after-timeout' });
            this.#lateResults.set(opId, row);
            this.stats.lateCompletions += 1;
            this.#emit('block-store-lane:op-late-complete', { opId, op: kind, result: row.summary, disposition: row.disposition });
            return value;
          }
          this.#results.set(opId, value);
          this.stats.completed += 1;
          this.#emit('block-store-lane:op-complete', { opId, op: kind, result: summarize(value) });
          return value;
        } catch (error) {
          if (timedOut()) {
            const row = Object.freeze({ opId, op: kind, error: { name: error?.name || 'Error', message: error?.message || String(error), code: error?.code ?? null, storageDisposition: error?.storageDisposition ?? null }, settledAt: new Date().toISOString(), disposition: 'late-provider-error-after-timeout' });
            this.#lateResults.set(opId, row);
            this.stats.lateFailures += 1;
            this.#emit('block-store-lane:op-late-error', { opId, op: kind, error: row.error, disposition: row.disposition });
          }
          throw error;
        }
      }
    });
    if (!accepted.accepted) {
      this.stats.rejected += 1;
      this.#emit('block-store-lane:reject', { opId, op: kind, reason: accepted.scheduler?.reason, disposition: accepted.scheduler?.disposition, noMutation: accepted.scheduler?.noMutation === true });
      return Object.freeze({ ...accepted, adapterOp: kind });
    }
    this.stats.scheduled += 1;
    this.#emit('block-store-lane:schedule', { opId, op: kind, priority, cost, dependsOn, lane, fallbackLanes, operationTimeoutMs: accepted.task?.metadata?.operationTimeoutMs ?? operationTimeoutMs ?? timeoutMs ?? null, abortProviderOnOperationTimeout: abortProviderOnOperationTimeout ?? this.#executor.abortProviderOnOperationTimeout ?? false });
    return Object.freeze({ ...accepted, adapterOp: kind });
  }
  schedulePut(payload, { id = null, priority = 'user-visible', cost = null, dependsOn = [], lane = this.lane, fallbackLanes = [], label = null, fields = {}, operationTimeoutMs = undefined, timeoutMs = undefined, abortProviderOnOperationTimeout = undefined, ...options } = {}) {
    const bytes = payloadBytes(payload);
    const providerOptions = scheduledProviderOptions(options, 'put');
    return this.schedule('put', (context = {}) => callStoreWithScheduledContextOptions(providerOptions, context, (scheduledOptions) => this.#store.put(payload, { label, ...fields }, scheduledOptions)), { id, priority, cost: cost ?? Math.max(1, Math.ceil(bytes / 16)), dependsOn, lane, fallbackLanes, operationTimeoutMs, timeoutMs, abortProviderOnOperationTimeout, metadata: { bytes, label, providerOptionKeys: providerOptionKeys(providerOptions), abortProviderOnOperationTimeoutOverride: abortProviderOnOperationTimeout === undefined ? null : abortProviderOnOperationTimeout === true } });
  }
  scheduleGet(ref, options = {}) {
    const providerOptions = scheduledProviderOptions(options, 'get');
    return this.schedule('get', (context = {}) => callStoreWithScheduledContextOptions(providerOptions, context, (scheduledOptions) => this.#store.get(ref, scheduledOptions)), { priority: 'user-visible', cost: 1, ...options, metadata: { refDigest: ref?.digest || ref?.id || String(ref), providerOptionKeys: providerOptionKeys(providerOptions) } });
  }
  scheduleHas(ref, options = {}) {
    const providerOptions = scheduledProviderOptions(options, 'has');
    return this.schedule('has', (context = {}) => callStoreWithScheduledContextOptions(providerOptions, context, (scheduledOptions) => this.#store.has(ref, scheduledOptions)), { priority: 'user-visible', cost: 1, ...options, metadata: { refDigest: ref?.digest || ref?.id || String(ref), providerOptionKeys: providerOptionKeys(providerOptions) } });
  }
  scheduleVerify(ref, options = {}) {
    const providerOptions = scheduledProviderOptions(options, 'verify');
    return this.schedule('verify', (context = {}) => callStoreWithScheduledContextOptions(providerOptions, context, (scheduledOptions) => this.#store.verify(ref, scheduledOptions)), { priority: 'user-visible', cost: 1, ...options, metadata: { refDigest: ref?.digest || ref?.id || String(ref), providerOptionKeys: providerOptionKeys(providerOptions) } });
  }
  scheduleDelete(ref, options = {}) {
    const providerOptions = scheduledProviderOptions(options, 'delete');
    return this.schedule('delete', (context = {}) => callStoreWithScheduledContextOptions(providerOptions, context, (scheduledOptions) => this.#store.delete(ref, scheduledOptions)), { priority: 'user-visible', cost: 1, ...options, metadata: { refDigest: ref?.digest || ref?.id || String(ref), providerOptionKeys: providerOptionKeys(providerOptions) } });
  }
  scheduleEstimate(options = {}) {
    const providerOptions = scheduledProviderOptions(options, 'estimate');
    const run = typeof this.#store.estimate === 'function' ? (context = {}) => callStoreWithScheduledContextOptions(providerOptions, context, (scheduledOptions) => this.#store.estimate(scheduledOptions)) : async () => ({ quota: null, usage: null, unavailable: true });
    return this.schedule('estimate', run, { priority: 'background', cost: 1, ...options, metadata: { providerOptionKeys: providerOptionKeys(providerOptions) } });
  }
  scheduleSnapshot(options = {}) {
    const providerOptions = scheduledProviderOptions(options, 'snapshot');
    return this.schedule('snapshot', (context = {}) => callStoreWithScheduledContextOptions(providerOptions, context, (scheduledOptions) => this.#store.snapshot(scheduledOptions)), { priority: 'background', cost: 1, ...options, metadata: { providerOptionKeys: providerOptionKeys(providerOptions) } });
  }
  scheduleCleanupForTest(options = {}) {
    if (typeof this.#store.cleanupForTest !== 'function') throw new Error('block-store cleanupForTest is unavailable');
    const providerOptions = scheduledProviderOptions(options, 'cleanup');
    return this.schedule('cleanup', (context = {}) => callStoreWithScheduledContextOptions(providerOptions, context, (scheduledOptions) => this.#store.cleanupForTest(scheduledOptions)), { priority: 'maintenance', cost: 1, lane: 'maintenance', ...options, metadata: { providerOptionKeys: providerOptionKeys(providerOptions) } });
  }
  submit(op, args = {}, options = {}) {
    if (op === 'put' || op === 'block-put') return this.schedulePut(args.payload ?? args.bytes ?? '', options);
    if (op === 'get' || op === 'block-get') return this.scheduleGet(args.ref ?? args.digest, options);
    if (op === 'has' || op === 'block-has') return this.scheduleHas(args.ref ?? args.digest, options);
    if (op === 'verify' || op === 'block-verify') return this.scheduleVerify(args.ref ?? args.digest, options);
    if (op === 'delete' || op === 'block-delete') return this.scheduleDelete(args.ref ?? args.digest, options);
    if (op === 'estimate' || op === 'block-estimate') return this.scheduleEstimate(options);
    if (op === 'snapshot' || op === 'block-snapshot') return this.scheduleSnapshot(options);
    if (op === 'cleanup' || op === 'cleanupForTest' || op === 'block-cleanup') return this.scheduleCleanupForTest(options);
    throw new Error(`Unsupported block-store lane submit op: ${op}`);
  }
  async drain(options = {}) {
    const drained = await this.#executor.drain(options);
    for (const row of drained.results) {
      if (row.dispatched === false) this.stats.emptyDispatches += 1;
      if (row.dispatched && row.ok === false) {
        this.stats.failed += 1;
        this.#emit('block-store-lane:op-error', { opId: row.opId, op: row.op, error: row.error });
      }
    }
    return drained;
  }
  async executeNext() { const drained = await this.drain({ maxSteps: 1 }); return drained.results[0] || Object.freeze({ dispatched: false, disposition: 'empty' }); }
  result(opId) { return this.#results.get(String(opId)) ?? this.#executor.result?.(opId); }
  lateResult(opId) { return this.#lateResults.get(String(opId)) ?? null; }
  lateResultMap() { return new Map(this.#lateResults); }
  resultSummary(opId) { return summarize(this.result(opId)); }
  markHealthy(lane = this.lane, reason = 'manual-recovery', options = {}) { return this.#executor.markHealthy(lane, reason, options); }
  markUnhealthy(lane = this.lane, reason = 'manual-unhealthy') { return this.#executor.markUnhealthy(lane, reason); }
  timedOutOperationQuarantine(lane = this.lane) { return this.#executor.timedOutOperationQuarantine?.(lane) ?? Object.freeze({ ok: true, totalCount: 0, lane }); }
  exportTimedOutOperationQuarantine(options = {}) { return this.#executor.exportTimedOutOperationQuarantine?.({ lane: options.lane ?? this.lane, reason: options.reason ?? 'operator-export-block-store-lane-quarantine' }); }
  importTimedOutOperationQuarantine(ledger, options = {}) { return this.#executor.importTimedOutOperationQuarantine?.(ledger, { lane: options.lane ?? this.lane, reason: options.reason ?? 'operator-import-block-store-lane-quarantine', markUnhealthy: options.markUnhealthy !== false, allowPartialImport: options.allowPartialImport === true, allowEmptyImport: options.allowEmptyImport === true }); }
  async persistTimedOutOperationQuarantine(options = {}) {
    const ledger = assertQuarantineLedger(options.ledger ?? this.exportTimedOutOperationQuarantine({ lane: options.lane ?? this.lane, reason: options.reason ?? 'operator-persist-block-store-lane-quarantine' }));
    const bytes = encodeJsonBytes(ledger);
    const label = options.label ?? `timed-out-operation-quarantine:${ledger.lane ?? options.lane ?? this.lane}:${Date.now()}`;
    const ref = await this.#store.put(bytes, { label, purpose: 'timed-out-operation-quarantine-ledger', schema: ledger.schema, ...options.fields }, options.putOptions ?? {});
    this.stats.quarantineLedgerPersists += 1;
    const result = Object.freeze({ ok: true, schema: ledger.schema, lane: ledger.lane ?? options.lane ?? this.lane, label, bytes: bytes.byteLength, ref: ref?.ref ?? ref, put: ref, digest: ref?.digest ?? ref?.ref?.digest ?? ref?.hash ?? ref?.ref?.hash ?? ref?.id ?? null, counts: ledger.counts ?? null, quarantineFingerprint: ledger.quarantineFingerprint ?? null, reviewFingerprint: ledger.reviewFingerprint ?? ledger.quarantineFingerprint ?? null, persisted: true });
    this.#emit('block-store-lane:quarantine-ledger-persisted', { label, schema: result.schema, lane: result.lane, bytes: result.bytes, digest: result.digest, counts: result.counts, quarantineFingerprint: result.quarantineFingerprint });
    return result;
  }
  async restoreTimedOutOperationQuarantineFromBlockStore(ref, options = {}) {
    const lane = options.lane ?? this.lane;
    try {
      let blockVerify = null;
      const unverifiedRequested = options.verifyBeforeRestore === false;
      if (unverifiedRequested && options.allowUnsafeUnverifiedRestore !== true) {
        this.stats.quarantineLedgerRestoreRejected += 1;
        this.stats.quarantineLedgerRestoreUnverifiedRejected += 1;
        const result = Object.freeze({ ok: false, code: 'timed-out-quarantine-restore-unverified-rejected', disposition: 'rejected-unverified-quarantine-ledger-restore', schema: 'brt.storageLane.timedOutOperationQuarantine.v1', lane, ref, refDigest: blockRefDigest(ref), blockVerify: null, unverifiedRestoreRequested: true });
        this.#emit('block-store-lane:quarantine-ledger-restore-unverified-rejected', result);
        this.#emit('block-store-lane:quarantine-ledger-restore-rejected', result);
        return result;
      }
      if (unverifiedRequested) {
        this.stats.quarantineLedgerRestoreUnverifiedAccepted += 1;
        this.#emit('block-store-lane:quarantine-ledger-restore-unverified-accepted', { lane, refDigest: blockRefDigest(ref), reason: options.reason ?? 'operator-restore-block-store-lane-quarantine' });
      }
      if (options.verifyBeforeRestore !== false) {
        blockVerify = summarizeBlockVerify(await this.#store.verify(ref, options.verifyOptions ?? {}));
        this.stats.quarantineLedgerRestoreVerifications += 1;
        if (blockVerify.ok !== true) {
          this.stats.quarantineLedgerRestoreRejected += 1;
          this.stats.quarantineLedgerRestoreBlockIntegrityRejected += 1;
          const result = Object.freeze({ ok: false, code: 'timed-out-quarantine-restore-block-integrity-rejected', disposition: 'rejected-quarantine-ledger-block-integrity', schema: 'brt.storageLane.timedOutOperationQuarantine.v1', lane, ref, refDigest: blockRefDigest(ref), blockVerify });
          this.#emit('block-store-lane:quarantine-ledger-restore-block-integrity-rejected', result);
          this.#emit('block-store-lane:quarantine-ledger-restore-rejected', result);
          return result;
        }
      }
      const blankExpectedFingerprint = blankExpectedFingerprintOption(options, ['expectedQuarantineFingerprint', 'expectedReviewFingerprint', 'expectedLedgerFingerprint']);
      if (blankExpectedFingerprint) {
        this.stats.quarantineLedgerRestoreRejected += 1;
        this.stats.quarantineLedgerRestoreExpectedFingerprintRejected += 1;
        const result = Object.freeze({ ok: false, code: 'timed-out-quarantine-restore-expected-fingerprint-blank', disposition: 'rejected-quarantine-ledger-expected-fingerprint', schema: 'brt.storageLane.timedOutOperationQuarantine.v1', lane, ref, refDigest: blockRefDigest(ref), blockVerify, expectedFingerprintOption: blankExpectedFingerprint.key });
        this.#emit('block-store-lane:quarantine-ledger-restore-expected-fingerprint-rejected', { schema: result.schema, lane: result.lane, code: result.code, disposition: result.disposition, blockVerify, expectedFingerprintOption: result.expectedFingerprintOption });
        this.#emit('block-store-lane:quarantine-ledger-restore-rejected', result);
        return result;
      }
      const bytes = await this.#store.get(ref, options.getOptions ?? {});
      const ledger = assertQuarantineLedger(decodeJsonBytes(bytes));
      const computedQuarantineFingerprint = timedOutQuarantineFingerprint(ledger);
      const expectedQuarantineFingerprint = options.expectedQuarantineFingerprint ?? options.expectedReviewFingerprint ?? options.expectedLedgerFingerprint ?? null;
      const fingerprintMismatch = expectedFingerprintMismatch(expectedQuarantineFingerprint, computedQuarantineFingerprint);
      if (fingerprintMismatch) {
        this.stats.quarantineLedgerRestoreRejected += 1;
        this.stats.quarantineLedgerRestoreExpectedFingerprintRejected += 1;
        const result = Object.freeze({ ok: false, code: 'timed-out-quarantine-restore-expected-fingerprint-mismatch', disposition: 'rejected-quarantine-ledger-expected-fingerprint', schema: ledger.schema, lane, ref, refDigest: blockRefDigest(ref), blockVerify, bytes: bytes?.byteLength ?? null, expectedQuarantineFingerprint: fingerprintMismatch.expected, actualQuarantineFingerprint: fingerprintMismatch.actual, ledgerQuarantineFingerprint: ledger.quarantineFingerprint ?? null, ledgerReviewFingerprint: ledger.reviewFingerprint ?? null, ledger });
        this.#emit('block-store-lane:quarantine-ledger-restore-expected-fingerprint-rejected', { schema: result.schema, lane: result.lane, bytes: result.bytes, code: result.code, disposition: result.disposition, blockVerify, expectedQuarantineFingerprint: result.expectedQuarantineFingerprint, actualQuarantineFingerprint: result.actualQuarantineFingerprint });
        this.#emit('block-store-lane:quarantine-ledger-restore-rejected', result);
        return result;
      }
      const importResult = this.importTimedOutOperationQuarantine(ledger, { lane, reason: options.reason ?? 'operator-restore-block-store-lane-quarantine', markUnhealthy: options.markUnhealthy !== false, allowPartialImport: options.allowPartialImport === true, allowEmptyImport: options.allowEmptyImport === true });
      if (importResult?.ok !== true) {
        this.stats.quarantineLedgerRestoreRejected += 1;
        const result = Object.freeze({ ok: false, code: importResult?.code ?? 'timed-out-quarantine-restore-rejected', disposition: importResult?.disposition ?? 'rejected-ledger-integrity', schema: ledger.schema, lane, ref, refDigest: blockRefDigest(ref), blockVerify, bytes: bytes?.byteLength ?? null, ledger, importResult });
        this.#emit('block-store-lane:quarantine-ledger-restore-rejected', { schema: result.schema, lane: result.lane, bytes: result.bytes, code: result.code, disposition: result.disposition, blockVerify, importResult });
        return result;
      }
      this.stats.quarantineLedgerRestores += 1;
      const result = Object.freeze({ ok: true, schema: ledger.schema, lane, ref, refDigest: blockRefDigest(ref), blockVerify, bytes: bytes?.byteLength ?? null, ledger, importResult });
      this.#emit('block-store-lane:quarantine-ledger-restored', { schema: result.schema, lane: result.lane, bytes: result.bytes, blockVerify, importedCount: importResult?.importedCount ?? null, ok: result.ok });
      return result;
    } catch (error) {
      this.stats.quarantineLedgerRestoreFailures += 1;
      const result = Object.freeze({ ok: false, ref, lane, refDigest: blockRefDigest(ref), code: 'timed-out-quarantine-restore-error', disposition: 'restore-error', error: describeError(error) });
      this.#emit('block-store-lane:quarantine-ledger-restore-error', result);
      return result;
    }
  }
  failedTimedOutOperations(lane = this.lane) { return this.#executor.failedTimedOutOperations?.(lane) ?? Object.freeze([]); }
  successfulTimedOutOperations(lane = this.lane) { return this.#executor.successfulTimedOutOperations?.(lane) ?? Object.freeze([]); }
  createTimedOutOperationQuarantineReview(options = {}) {
    const manifest = this.#executor.createTimedOutOperationQuarantineReview?.({ lane: options.lane ?? this.lane, reviewer: options.reviewer ?? 'operator', reason: options.reason ?? 'operator-reviewed-block-store-lane-quarantine', opId: options.opId ?? null, opIds: options.opIds ?? null, operationReplayKey: options.operationReplayKey ?? null, operationReplayKeys: options.operationReplayKeys ?? null, category: options.category ?? 'all', categories: options.categories ?? null, allowLaneWide: options.allowLaneWide === true, all: options.all === true || options.allowAll === true, reviewToken: options.reviewToken ?? null });
    if (manifest) this.stats.quarantineReviewManifests += 1;
    return manifest;
  }
  clearTimedOutOperationQuarantine(options = {}) {
    const opts = { ...(options || {}) };
    if (!Object.prototype.hasOwnProperty.call(opts, 'lane')) opts.lane = this.lane;
    if (!Object.prototype.hasOwnProperty.call(opts, 'reason')) opts.reason = 'operator-acknowledged-timed-out-operation-quarantine';
    return this.#executor.clearTimedOutOperationQuarantine?.(opts);
  }
  createTimedOutOperationQuarantineClearanceReceipt(clearResult, options = {}) {
    const receipt = createTimedOutOperationQuarantineClearanceReceipt(clearResult, { label: options.label ?? null, createdAtMs: options.createdAtMs ?? Date.now(), reviewer: options.reviewer ?? null, source: { adapterLabel: this.label, store: this.storeName, provider: this.providerName, lane: this.lane, ...(options.source || {}) } });
    this.stats.quarantineClearanceReceiptsCreated += 1;
    const registrationProvenance = Object.freeze({ schema: CLEARANCE_RECEIPT_REGISTRATION_PROVENANCE_SCHEMA, source: 'adapter-create-clearance-receipt', lane: receipt.lane ?? this.lane, receiptFingerprint: receipt.receiptFingerprint, preClearanceFingerprint: receipt.preClearanceFingerprint, reviewFingerprint: receipt.reviewFingerprint, adapterLabel: this.label, store: this.storeName, provider: this.providerName });
    const registration = this.#executor.registerTimedOutOperationQuarantineClearanceReceipt?.(receipt, { lane: receipt.lane ?? this.lane, reason: options.reason ?? 'operator-create-clearance-receipt', provenance: registrationProvenance }) ?? null;
    this.#emit('block-store-lane:quarantine-clearance-receipt-created', { lane: receipt.lane, receiptFingerprint: receipt.receiptFingerprint, preClearanceFingerprint: receipt.preClearanceFingerprint, postClearanceFingerprint: receipt.postClearanceFingerprint, clearedCount: receipt.clearedCount, registration });
    return receipt;
  }
  async persistTimedOutOperationQuarantineClearanceReceipt(clearResultOrReceipt, options = {}) {
    const receipt = clearResultOrReceipt?.schema === CLEARANCE_RECEIPT_SCHEMA ? clearResultOrReceipt : this.createTimedOutOperationQuarantineClearanceReceipt(clearResultOrReceipt, options);
    const validation = validateTimedOutOperationQuarantineClearanceReceipt(receipt);
    if (!validation.ok) { this.stats.quarantineClearanceReceiptRestoreRejected += 1; const result = Object.freeze({ ok: false, code: 'timed-out-quarantine-clearance-receipt-invalid', disposition: 'rejected-clearance-receipt-integrity', validation, receipt }); this.#emit('block-store-lane:quarantine-clearance-receipt-restore-rejected', result); return result; }
    const bytes = encodeJsonBytes(receipt);
    const label = options.label ?? `timed-out-operation-quarantine-clearance-receipt:${receipt.lane ?? options.lane ?? this.lane}:${Date.now()}`;
    const ref = await this.#store.put(bytes, { label, purpose: 'timed-out-operation-quarantine-clearance-receipt', schema: CLEARANCE_RECEIPT_SCHEMA, receiptFingerprint: receipt.receiptFingerprint, preClearanceFingerprint: receipt.preClearanceFingerprint, ...options.fields }, options.putOptions ?? {});
    this.stats.quarantineClearanceReceiptPersists += 1;
    const result = Object.freeze({ ok: true, schema: CLEARANCE_RECEIPT_SCHEMA, lane: receipt.lane ?? options.lane ?? this.lane, label, bytes: bytes.byteLength, ref: ref?.ref ?? ref, put: ref, digest: ref?.digest ?? ref?.ref?.digest ?? ref?.hash ?? ref?.ref?.hash ?? ref?.id ?? null, receipt, receiptFingerprint: receipt.receiptFingerprint, preClearanceFingerprint: receipt.preClearanceFingerprint, persisted: true, validation });
    this.#emit('block-store-lane:quarantine-clearance-receipt-persisted', { label, schema: result.schema, lane: result.lane, bytes: result.bytes, digest: result.digest, receiptFingerprint: result.receiptFingerprint, preClearanceFingerprint: result.preClearanceFingerprint });
    return result;
  }
  async restoreTimedOutOperationQuarantineClearanceReceiptFromBlockStore(ref, options = {}) {
    const lane = options.lane ?? this.lane;
    try {
      let blockVerify = null;
      const unverifiedRequested = options.verifyBeforeRestore === false;
      if (unverifiedRequested && options.allowUnsafeUnverifiedRestore !== true) {
        this.stats.quarantineClearanceReceiptRestoreRejected += 1;
        this.stats.quarantineClearanceReceiptRestoreUnverifiedRejected += 1;
        const result = Object.freeze({ ok: false, code: 'timed-out-quarantine-clearance-receipt-restore-unverified-rejected', disposition: 'rejected-unverified-clearance-receipt-restore', schema: CLEARANCE_RECEIPT_SCHEMA, lane, ref, refDigest: blockRefDigest(ref), blockVerify: null, unverifiedRestoreRequested: true });
        this.#emit('block-store-lane:quarantine-clearance-receipt-restore-unverified-rejected', result);
        this.#emit('block-store-lane:quarantine-clearance-receipt-restore-rejected', result);
        return result;
      }
      if (unverifiedRequested) {
        this.stats.quarantineClearanceReceiptRestoreUnverifiedAccepted += 1;
        this.#emit('block-store-lane:quarantine-clearance-receipt-restore-unverified-accepted', { lane, refDigest: blockRefDigest(ref), reason: options.reason ?? 'operator-restore-clearance-receipt' });
      }
      if (options.verifyBeforeRestore !== false) {
        blockVerify = summarizeBlockVerify(await this.#store.verify(ref, options.verifyOptions ?? {}));
        this.stats.quarantineClearanceReceiptRestoreVerifications += 1;
        if (blockVerify.ok !== true) {
          this.stats.quarantineClearanceReceiptRestoreRejected += 1;
          this.stats.quarantineClearanceReceiptRestoreBlockIntegrityRejected += 1;
          const result = Object.freeze({ ok: false, code: 'timed-out-quarantine-clearance-receipt-restore-block-integrity-rejected', disposition: 'rejected-clearance-receipt-block-integrity', schema: CLEARANCE_RECEIPT_SCHEMA, lane, ref, refDigest: blockRefDigest(ref), blockVerify });
          this.#emit('block-store-lane:quarantine-clearance-receipt-restore-block-integrity-rejected', result);
          this.#emit('block-store-lane:quarantine-clearance-receipt-restore-rejected', result);
          return result;
        }
      }
      const blankExpectedFingerprint = blankExpectedFingerprintOption(options, ['expectedReceiptFingerprint', 'expectedPreClearanceFingerprint', 'expectedReviewFingerprint', 'expectedQuarantineFingerprint', 'expectedPostClearanceFingerprint']);
      if (blankExpectedFingerprint) {
        this.stats.quarantineClearanceReceiptRestoreRejected += 1;
        this.stats.quarantineClearanceReceiptRestoreExpectedFingerprintRejected += 1;
        const result = Object.freeze({ ok: false, code: 'timed-out-quarantine-clearance-receipt-restore-expected-fingerprint-blank', disposition: 'rejected-clearance-receipt-expected-fingerprint', schema: CLEARANCE_RECEIPT_SCHEMA, lane, ref, refDigest: blockRefDigest(ref), blockVerify, expectedFingerprintOption: blankExpectedFingerprint.key });
        this.#emit('block-store-lane:quarantine-clearance-receipt-restore-expected-fingerprint-rejected', { schema: result.schema, lane: result.lane, code: result.code, disposition: result.disposition, blockVerify, expectedFingerprintOption: result.expectedFingerprintOption });
        this.#emit('block-store-lane:quarantine-clearance-receipt-restore-rejected', result);
        return result;
      }
      const bytes = await this.#store.get(ref, options.getOptions ?? {});
      const receipt = decodeJsonBytes(bytes);
      const validation = validateTimedOutOperationQuarantineClearanceReceipt(receipt);
      if (!validation.ok) { this.stats.quarantineClearanceReceiptRestoreRejected += 1; const result = Object.freeze({ ok: false, code: 'timed-out-quarantine-clearance-receipt-restore-rejected', disposition: 'rejected-clearance-receipt-integrity', schema: receipt?.schema ?? null, lane, ref, refDigest: blockRefDigest(ref), blockVerify, bytes: bytes?.byteLength ?? null, receipt, validation }); this.#emit('block-store-lane:quarantine-clearance-receipt-restore-rejected', { schema: result.schema, lane: result.lane, bytes: result.bytes, code: result.code, disposition: result.disposition, blockVerify, validation }); return result; }
      const expectedReceiptFingerprint = options.expectedReceiptFingerprint ?? null;
      const expectedPreClearanceFingerprint = options.expectedPreClearanceFingerprint ?? options.expectedReviewFingerprint ?? options.expectedQuarantineFingerprint ?? null;
      const expectedPostClearanceFingerprint = options.expectedPostClearanceFingerprint ?? null;
      const receiptFingerprintMismatch = expectedFingerprintMismatch(expectedReceiptFingerprint, receipt.receiptFingerprint);
      const preClearanceMismatch = expectedFingerprintMismatch(expectedPreClearanceFingerprint, receipt.preClearanceFingerprint ?? receipt.reviewFingerprint);
      const postClearanceMismatch = expectedFingerprintMismatch(expectedPostClearanceFingerprint, receipt.postClearanceFingerprint);
      if (receiptFingerprintMismatch || preClearanceMismatch || postClearanceMismatch) {
        this.stats.quarantineClearanceReceiptRestoreRejected += 1;
        this.stats.quarantineClearanceReceiptRestoreExpectedFingerprintRejected += 1;
        const mismatches = Object.freeze({ receiptFingerprint: receiptFingerprintMismatch, preClearanceFingerprint: preClearanceMismatch, postClearanceFingerprint: postClearanceMismatch });
        const result = Object.freeze({ ok: false, code: 'timed-out-quarantine-clearance-receipt-restore-expected-fingerprint-mismatch', disposition: 'rejected-clearance-receipt-expected-fingerprint', schema: receipt?.schema ?? null, lane, ref, refDigest: blockRefDigest(ref), blockVerify, bytes: bytes?.byteLength ?? null, receipt, receiptFingerprint: receipt.receiptFingerprint ?? null, preClearanceFingerprint: receipt.preClearanceFingerprint ?? null, validation, mismatches });
        this.#emit('block-store-lane:quarantine-clearance-receipt-restore-expected-fingerprint-rejected', { schema: result.schema, lane: result.lane, bytes: result.bytes, code: result.code, disposition: result.disposition, blockVerify, receiptFingerprint: result.receiptFingerprint, preClearanceFingerprint: result.preClearanceFingerprint, mismatches });
        this.#emit('block-store-lane:quarantine-clearance-receipt-restore-rejected', result);
        return result;
      }
      const refDigest = blockRefDigest(ref);
      const registrationProvenance = Object.freeze({ schema: CLEARANCE_RECEIPT_REGISTRATION_PROVENANCE_SCHEMA, source: 'block-store-restore-clearance-receipt', lane, receiptFingerprint: receipt.receiptFingerprint, preClearanceFingerprint: receipt.preClearanceFingerprint, reviewFingerprint: receipt.reviewFingerprint, refDigest: refDigest == null ? null : String(refDigest), blockVerifyDigest: blockVerify?.digest ?? null, blockVerifyBytes: blockVerify?.bytes ?? null, blockVerified: blockVerify?.ok === true, unsafeUnverifiedRestore: unverifiedRequested && options.allowUnsafeUnverifiedRestore === true, unsafeReviewToken: options.unsafeReviewToken ?? null, bytes: bytes?.byteLength ?? null, adapterLabel: this.label, store: this.storeName, provider: this.providerName });
      const registration = this.#executor.registerTimedOutOperationQuarantineClearanceReceipt?.(receipt, { lane, reason: options.reason ?? 'operator-restore-clearance-receipt', provenance: registrationProvenance }) ?? null;
      if (registration?.ok !== true) {
        this.stats.quarantineClearanceReceiptRestoreRejected += 1;
        this.stats.quarantineClearanceReceiptRegistrationRejectedOnRestore += 1;
        const result = Object.freeze({ ok: false, code: registration?.code ?? 'timed-out-quarantine-clearance-receipt-restore-registration-rejected', disposition: registration?.disposition ?? 'rejected-clearance-receipt-registration', schema: CLEARANCE_RECEIPT_SCHEMA, lane, receiptLane: receipt.lane ?? null, ref, refDigest, blockVerify, bytes: bytes?.byteLength ?? null, receipt, receiptFingerprint: validation.receiptFingerprint, preClearanceFingerprint: receipt.preClearanceFingerprint ?? null, validation, registration });
        this.#emit('block-store-lane:quarantine-clearance-receipt-restore-rejected', { schema: result.schema, lane: result.lane, bytes: result.bytes, code: result.code, disposition: result.disposition, blockVerify, receiptFingerprint: result.receiptFingerprint, preClearanceFingerprint: result.preClearanceFingerprint, registration, validation });
        return result;
      }
      this.stats.quarantineClearanceReceiptRestores += 1;
      const result = Object.freeze({ ok: true, schema: CLEARANCE_RECEIPT_SCHEMA, lane, receiptLane: receipt.lane ?? null, ref, refDigest, blockVerify, bytes: bytes?.byteLength ?? null, receipt, receiptFingerprint: validation.receiptFingerprint, preClearanceFingerprint: receipt.preClearanceFingerprint ?? null, validation, registration });
      this.#emit('block-store-lane:quarantine-clearance-receipt-restored', { schema: result.schema, lane: result.lane, bytes: result.bytes, blockVerify, receiptFingerprint: result.receiptFingerprint, preClearanceFingerprint: result.preClearanceFingerprint, registration, ok: result.ok });
      return result;
    } catch (error) {
      this.stats.quarantineClearanceReceiptRestoreFailures += 1;
      const result = Object.freeze({ ok: false, ref, lane, refDigest: blockRefDigest(ref), code: 'timed-out-quarantine-clearance-receipt-restore-error', disposition: 'restore-error', error: describeError(error) });
      this.#emit('block-store-lane:quarantine-clearance-receipt-restore-error', result);
      return result;
    }
  }
  clearedTimedOutOperationQuarantineClearanceReceipts(lane = this.lane) { return this.#executor.clearedTimedOutOperationQuarantineClearanceReceipts?.(lane) ?? Object.freeze([]); }
  finalizeUnsettledTimedOutOperations(options = {}) {
    const opts = { ...(options || {}) };
    if (!Object.prototype.hasOwnProperty.call(opts, 'lane')) opts.lane = this.lane;
    if (!Object.prototype.hasOwnProperty.call(opts, 'reason')) opts.reason = 'operator-classified-unsettled-timed-out-operation';
    if (!Object.prototype.hasOwnProperty.call(opts, 'requireReviewFingerprint')) opts.requireReviewFingerprint = true;
    if (!Object.prototype.hasOwnProperty.call(opts, 'errorCode')) opts.errorCode = 'BRT_STORAGE_TIMED_OUT_OPERATION_ORPHANED';
    const result = this.#executor.finalizeUnsettledTimedOutOperations?.(opts);
    if (result?.ok) this.stats.quarantineOrphanFinalizations += result.finalizedCount ?? 0;
    return result;
  }
  clearSuccessfulTimedOutOperations(options = {}) { return this.#executor.clearSuccessfulTimedOutOperations?.({ lane: options.lane ?? this.lane, opId: options.opId ?? null, opIds: options.opIds ?? null, operationReplayKey: options.operationReplayKey ?? null, operationReplayKeys: options.operationReplayKeys ?? null, all: options.all === true || options.allowAll === true, allowLaneWide: options.allowLaneWide === true, reviewed: options.reviewed === true, reviewToken: options.reviewToken ?? null, reviewFingerprint: options.reviewFingerprint ?? null, requireReviewFingerprint: options.requireReviewFingerprint !== false, reviewManifest: options.reviewManifest ?? null, reason: options.reason ?? 'operator-acknowledged-late-provider-success' }); }
  clearFailedTimedOutOperations(options = {}) { return this.#executor.clearFailedTimedOutOperations?.({ lane: options.lane ?? this.lane, opId: options.opId ?? null, opIds: options.opIds ?? null, operationReplayKey: options.operationReplayKey ?? null, operationReplayKeys: options.operationReplayKeys ?? null, all: options.all === true || options.allowAll === true, allowLaneWide: options.allowLaneWide === true, reviewed: options.reviewed === true, reviewToken: options.reviewToken ?? null, reviewFingerprint: options.reviewFingerprint ?? null, requireReviewFingerprint: options.requireReviewFingerprint !== false, reviewManifest: options.reviewManifest ?? null, reason: options.reason ?? 'operator-acknowledged-late-provider-failure' }); }
  async recoverWhenStoreSettled({ lane = this.lane, timeoutMs = 1000, intervalMs = 25, reason = 'store-coordination-settled', requireHealthy = false, requireTimedOutOperationsSettled = true, requireNoSuccessfulTimedOutOperations = true, requireNoFailedTimedOutOperations = true } = {}) {
    const waitForSettled = this.#store?.waitForSettled;
    if (typeof waitForSettled !== 'function') {
      const result = Object.freeze({ recovered: false, reason: 'store-settle-check-unavailable', lane, settled: null });
      this.#emit('block-store-lane:recover-settled-unavailable', { lane, reason: result.reason, store: this.storeName, provider: this.providerName });
      return result;
    }
    const settled = await waitForSettled.call(this.#store, { timeoutMs, intervalMs });
    if (!settled?.ok) {
      const result = Object.freeze({ recovered: false, reason: 'store-coordination-still-contended', lane, settled });
      this.#emit('block-store-lane:recover-settled-blocked', { lane, reason: result.reason, store: this.storeName, provider: this.providerName, heldCount: settled?.last?.heldCount ?? null, pendingCount: settled?.last?.pendingCount ?? null, available: settled?.last?.available ?? null });
      return result;
    }
    if (requireTimedOutOperationsSettled && typeof this.#executor.waitForTimedOutOperationsSettled === 'function') {
      const timeoutSettled = await this.#executor.waitForTimedOutOperationsSettled({ lane, timeoutMs, intervalMs });
      if (!timeoutSettled?.ok) {
        const result = Object.freeze({ recovered: false, reason: 'timed-out-operation-still-unsettled', lane, settled, timeoutSettled, quarantine: this.timedOutOperationQuarantine(lane) });
        const blockedPayload = { lane, reason: result.reason, store: this.storeName, provider: this.providerName, unsettledTimedOutOperationCount: timeoutSettled?.count ?? null };
        this.#emit('block-store-lane:recover-timed-out-unsettled-blocked', blockedPayload);
        this.#emit('block-store-lane:recover-timed-out-ops-blocked', blockedPayload);
        return result;
      }
      this.#emit('block-store-lane:recover-timed-out-ops-settled', { lane, store: this.storeName, provider: this.providerName, elapsedMs: timeoutSettled.elapsedMs ?? null });
    }
    if (requireNoSuccessfulTimedOutOperations && typeof this.#executor.successfulTimedOutOperations === 'function') {
      const successfulTimedOutOperations = this.#executor.successfulTimedOutOperations(lane);
      if (successfulTimedOutOperations.length > 0) {
        const result = Object.freeze({ recovered: false, reason: 'timed-out-operation-late-success', lane, settled, successfulTimedOutOperations, quarantine: this.timedOutOperationQuarantine(lane) });
        this.#emit('block-store-lane:recover-timed-out-successes-blocked', { lane, reason: result.reason, store: this.storeName, provider: this.providerName, successfulTimedOutOperationCount: successfulTimedOutOperations.length, firstKind: successfulTimedOutOperations[0]?.kind ?? null });
        return result;
      }
      this.#emit('block-store-lane:recover-timed-out-successes-clear', { lane, store: this.storeName, provider: this.providerName });
    }
    if (requireNoFailedTimedOutOperations && typeof this.#executor.failedTimedOutOperations === 'function') {
      const failedTimedOutOperations = this.#executor.failedTimedOutOperations(lane);
      if (failedTimedOutOperations.length > 0) {
        const result = Object.freeze({ recovered: false, reason: 'timed-out-operation-late-failure', lane, settled, failedTimedOutOperations, quarantine: this.timedOutOperationQuarantine(lane) });
        this.#emit('block-store-lane:recover-timed-out-failures-blocked', { lane, reason: result.reason, store: this.storeName, provider: this.providerName, failedTimedOutOperationCount: failedTimedOutOperations.length, firstCode: failedTimedOutOperations[0]?.error?.code ?? null });
        return result;
      }
      this.#emit('block-store-lane:recover-timed-out-failures-clear', { lane, store: this.storeName, provider: this.providerName });
    }
    const health = this.#executor.scheduler?.snapshotLane?.(lane) ?? null;
    if (requireHealthy && health?.healthy === true) {
      const result = Object.freeze({ recovered: false, reason: 'lane-already-healthy', lane, settled, health });
      this.#emit('block-store-lane:recover-settled-skip', { lane, reason: result.reason, store: this.storeName, provider: this.providerName });
      return result;
    }
    const recovery = this.markHealthy(lane, reason);
    const result = Object.freeze({ recovered: true, reason, lane, settled, recovery });
    this.#emit('block-store-lane:recover-settled', { lane, reason, store: this.storeName, provider: this.providerName, heldCount: settled.last?.heldCount ?? null, pendingCount: settled.last?.pendingCount ?? null });
    return result;
  }
  close(reason = 'block-store-lane-adapter-close') {
    void this.closeAsync({ reason });
    return this.snapshot();
  }
  async closeAsync({ reason = 'block-store-lane-adapter-close' } = {}) {
    this.stats.closeCalls += 1;
    const wasClosed = this.#closed;
    this.#closed = true;
    let storeClose = null;
    if (!wasClosed && this.#ownStore && this.#store && typeof this.#store.closeAsync === 'function') storeClose = await this.#store.closeAsync({ reason });
    else if (!wasClosed && this.#ownStore && this.#store && typeof this.#store.close === 'function') storeClose = this.#store.close(reason);
    const report = Object.freeze({ disposition: wasClosed ? 'already-closed' : 'closed', label: this.label, lane: this.lane, store: this.storeName, provider: this.providerName, ownStore: this.#ownStore, storeClose, reason });
    this.#emit('block-store-lane:close', { disposition: report.disposition, store: this.storeName, provider: this.providerName, ownStore: this.#ownStore, storeClosed: Boolean(storeClose), reason });
    return report;
  }
  snapshot() {
    const executor = this.#executor.snapshot();
    const store = this.#store.snapshot();
    return Object.freeze({ label: this.label, lane: this.lane, storeName: this.storeName, provider: this.providerName, closed: this.#closed, ownStore: this.#ownStore, stats: { ...this.stats }, resultCount: this.#results.size, lateResultCount: this.#lateResults.size, lateResults: Array.from(this.#lateResults.values()).map((row) => ({ opId: row.opId, op: row.op, disposition: row.disposition, summary: row.summary ?? null, error: row.error ?? null, settledAt: row.settledAt })), timedOutOperationQuarantine: this.timedOutOperationQuarantine(), store, executor, executorValidation: validateStorageLaneExecutorSnapshot(executor, { requireMailbox: false }) });
  }
}
export function validateBlockStoreLaneAdapterSnapshot(snapshot) {
  const errors = [];
  const isObj = (value) => value && typeof value === 'object';
  if (!isObj(snapshot)) return Object.freeze({ ok: false, errors: ['snapshot must be an object'], resultCount: 0 });
  if (typeof snapshot.label !== 'string' || !snapshot.label) errors.push('label must be non-empty string');
  if (typeof snapshot.provider !== 'string' || !snapshot.provider) errors.push('provider must be non-empty string');
  if (!isObj(snapshot.store)) errors.push('store snapshot must be present');
  if (!isObj(snapshot.executor)) errors.push('executor snapshot must be present');
  if (!isObj(snapshot.executorValidation) || snapshot.executorValidation.ok !== true) errors.push('executorValidation.ok must be true');
  if (!Number.isInteger(snapshot.resultCount) || snapshot.resultCount < 0) errors.push('resultCount must be non-negative integer');
  if (snapshot.lateResultCount !== undefined && (!Number.isInteger(snapshot.lateResultCount) || snapshot.lateResultCount < 0)) errors.push('lateResultCount must be non-negative integer');
  if (Array.isArray(snapshot.lateResults) && snapshot.lateResultCount !== undefined && snapshot.lateResults.length !== snapshot.lateResultCount) errors.push('lateResults length must match lateResultCount');
  if (!isObj(snapshot.stats)) errors.push('stats must be present');
  return Object.freeze({ ok: errors.length === 0, errors, resultCount: snapshot.resultCount || 0 });
}
export function createBlockStoreLaneAdapter(config = {}) { return new BlockStoreLaneAdapter(config); }
export const BLOCK_STORE_LANE_ADAPTER_OPS = BLOCK_STORE_OPS;
