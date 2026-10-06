import { validateCrossLaneSchedulerSnapshot } from './cross-lane-scheduler.mjs';
const SUPPORTED_OPS = Object.freeze(['operation', 'enqueue', 'dequeue', 'ack', 'checkpoint', 'compact', 'snapshot']);
const SUPPORTED_OP_SET = new Set(SUPPORTED_OPS);
function summarizeResult(value) {
  if (value == null) return null;
  if (value instanceof Uint8Array) return { kind: 'Uint8Array', bytes: value.byteLength };
  if (typeof value !== 'object') return { value };
  const out = {};
  for (const key of ['disposition', 'seq', 'bytes', 'checksum32', 'pendingId', 'consumerId', 'deliveryCount', 'dryRun', 'candidateCount', 'deleted', 'deleteMisses', 'kind', 'version', 'opSeq', 'checksum']) if (key in value) out[key] = value[key];
  return out;
}
function describeError(error) {
  if (!error || typeof error !== 'object') return { name: 'Error', message: String(error), code: null, storageDisposition: null, providerDetail: null };
  const code = error.code || error.storageDisposition || null;
  const storageDisposition = error.storageDisposition || code || null;
  return {
    name: error.name || 'Error',
    message: error.message || String(error),
    code,
    storageDisposition,
    providerDetail: error.detail && typeof error.detail === 'object' ? error.detail : null
  };
}
function stableStringify(value) {
  if (value === null || typeof value !== 'object') return JSON.stringify(value);
  if (Array.isArray(value)) return `[${value.map((item) => stableStringify(item)).join(',')}]`;
  const keys = Object.keys(value).sort();
  return `{${keys.map((key) => `${JSON.stringify(key)}:${stableStringify(value[key])}`).join(',')}}`;
}
function fnv1a64Hex(input) {
  let hash = 0xcbf29ce484222325n;
  const prime = 0x100000001b3n;
  const mask = 0xffffffffffffffffn;
  const bytes = new TextEncoder().encode(String(input));
  for (const byte of bytes) {
    hash ^= BigInt(byte);
    hash = (hash * prime) & mask;
  }
  return hash.toString(16).padStart(16, '0');
}
function summarizeErrorForFingerprint(error) {
  const described = describeError(error);
  return Object.freeze({
    name: described.name || null,
    code: described.code || null,
    storageDisposition: described.storageDisposition || null,
    message: described.message || null
  });
}
function normalizeTimedOutRowForFingerprint(row, status) {
  const out = {
    status: String(status),
    opId: row?.opId == null ? '' : String(row.opId),
    kind: row?.kind == null ? 'operation' : String(row.kind),
    lane: row?.lane == null ? null : String(row.lane),
    operationEpoch: row?.operationEpoch == null ? null : String(row.operationEpoch),
    operationReplayKey: row?.operationReplayKey == null ? null : String(row.operationReplayKey),
    timeoutMs: normalizeOperationTimeoutMs(row?.timeoutMs ?? 0),
    timedOutAtMs: Number.isFinite(Number(row?.timedOutAtMs)) ? Number(row.timedOutAtMs) : null
  };
  if (status === 'successful') {
    out.settledAtMs = Number.isFinite(Number(row?.settledAtMs)) ? Number(row.settledAtMs) : null;
    out.result = row?.result && typeof row.result === 'object' ? row.result : (row?.result ?? null);
  }
  if (status === 'failed') {
    out.settledAtMs = Number.isFinite(Number(row?.settledAtMs)) ? Number(row.settledAtMs) : null;
    out.error = summarizeErrorForFingerprint(row?.error ?? row);
  }
  return Object.freeze(out);
}
export function timedOutQuarantineFingerprint(quarantine = {}) {
  const unsettled = [...(quarantine.unsettledTimedOutOperations || [])].map((row) => normalizeTimedOutRowForFingerprint(row, 'unsettled')).sort((a, b) => timedOutOperationRowSortKey(a).localeCompare(timedOutOperationRowSortKey(b)));
  const successful = [...(quarantine.successfulTimedOutOperations || [])].map((row) => normalizeTimedOutRowForFingerprint(row, 'successful')).sort((a, b) => timedOutOperationRowSortKey(a).localeCompare(timedOutOperationRowSortKey(b)));
  const failed = [...(quarantine.failedTimedOutOperations || [])].map((row) => normalizeTimedOutRowForFingerprint(row, 'failed')).sort((a, b) => timedOutOperationRowSortKey(a).localeCompare(timedOutOperationRowSortKey(b)));
  const payload = Object.freeze({
    schema: 'brt.storageLane.timedOutOperationQuarantine.v1',
    lane: quarantine.lane == null ? null : String(quarantine.lane),
    counts: Object.freeze({ total: unsettled.length + successful.length + failed.length, unsettled: unsettled.length, successful: successful.length, failed: failed.length }),
    unsettledTimedOutOperations: Object.freeze(unsettled),
    successfulTimedOutOperations: Object.freeze(successful),
    failedTimedOutOperations: Object.freeze(failed)
  });
  return `brt-qfp-v1:${fnv1a64Hex(stableStringify(payload))}`;
}
// Lane-wide clearance receipts are still lane-scoped.
// Timed-out quarantine rows preserve cancellation: false evidence.
const CLEARANCE_RECEIPT_SCHEMA = 'brt.storageLane.timedOutOperationQuarantine.clearanceReceipt.v1';
const CLEARANCE_RECEIPT_REGISTRATION_PROVENANCE_SCHEMA = 'brt.storageLane.timedOutOperationQuarantine.clearanceReceipt.registrationProvenance.v1';
const CLEARANCE_RECEIPT_REGISTRATION_PROVENANCE_SOURCES = new Set(['adapter-create-clearance-receipt', 'block-store-restore-clearance-receipt']);
function validateTimedOutOperationQuarantineClearanceReceiptRegistrationProvenance(provenance = null, receipt = {}, { lane = null, reason = null } = {}) {
  const errors = [];
  if (!provenance || typeof provenance !== 'object') errors.push('registration provenance must be an object');
  if (provenance?.schema !== CLEARANCE_RECEIPT_REGISTRATION_PROVENANCE_SCHEMA) errors.push(`registration provenance schema must be ${CLEARANCE_RECEIPT_REGISTRATION_PROVENANCE_SCHEMA}`);
  const source = provenance?.source == null ? '' : String(provenance.source);
  if (!CLEARANCE_RECEIPT_REGISTRATION_PROVENANCE_SOURCES.has(source)) errors.push(`unsupported registration provenance source ${source || '(missing)'}`);
  const receiptFingerprint = receipt?.receiptFingerprint == null ? '' : String(receipt.receiptFingerprint);
  const preClearanceFingerprint = receipt?.preClearanceFingerprint == null ? '' : String(receipt.preClearanceFingerprint);
  const reviewFingerprint = receipt?.reviewFingerprint == null ? '' : String(receipt.reviewFingerprint);
  const provenanceReceiptFingerprint = provenance?.receiptFingerprint == null ? '' : String(provenance.receiptFingerprint);
  const provenancePreClearanceFingerprint = provenance?.preClearanceFingerprint == null ? '' : String(provenance.preClearanceFingerprint);
  const provenanceReviewFingerprint = provenance?.reviewFingerprint == null ? '' : String(provenance.reviewFingerprint);
  if (!provenanceReceiptFingerprint) errors.push('registration provenance receiptFingerprint must be present');
  else if (receiptFingerprint && provenanceReceiptFingerprint !== receiptFingerprint) errors.push('registration provenance receiptFingerprint mismatch');
  if (!provenancePreClearanceFingerprint) errors.push('registration provenance preClearanceFingerprint must be present');
  else if (preClearanceFingerprint && provenancePreClearanceFingerprint !== preClearanceFingerprint) errors.push('registration provenance preClearanceFingerprint mismatch');
  if (provenanceReviewFingerprint && reviewFingerprint && provenanceReviewFingerprint !== reviewFingerprint) errors.push('registration provenance reviewFingerprint mismatch');
  const resolvedLane = lane == null ? (receipt?.lane == null ? null : String(receipt.lane)) : String(lane);
  const provenanceLane = provenance?.lane == null ? null : String(provenance.lane);
  if (provenanceLane != null && resolvedLane != null && provenanceLane !== resolvedLane) errors.push('registration provenance lane mismatch');
  if (source === 'adapter-create-clearance-receipt') {
    if (!provenance?.adapterLabel) errors.push('adapter-create provenance adapterLabel must be present');
    if (!provenance?.store) errors.push('adapter-create provenance store must be present');
    if (!provenance?.provider) errors.push('adapter-create provenance provider must be present');
  }
  if (source === 'block-store-restore-clearance-receipt') {
    const refDigest = provenance?.refDigest == null ? '' : String(provenance.refDigest);
    const blockVerifyDigest = provenance?.blockVerifyDigest == null ? '' : String(provenance.blockVerifyDigest);
    const bytes = Number(provenance?.bytes);
    const blockVerifyBytes = Number(provenance?.blockVerifyBytes);
    const unsafeUnverifiedRestore = provenance?.unsafeUnverifiedRestore === true;
    if (!refDigest) errors.push('block-store-restore provenance refDigest must be present');
    if (!Number.isFinite(bytes) || bytes <= 0) errors.push('block-store-restore provenance bytes must be positive');
    if (unsafeUnverifiedRestore) {
      if (provenance?.blockVerified === true) errors.push('unsafe block-store-restore provenance must not claim blockVerified true');
      if (!provenance?.unsafeReviewToken || typeof provenance.unsafeReviewToken !== 'string') errors.push('unsafe block-store-restore provenance unsafeReviewToken must be present');
    } else {
      if (provenance?.blockVerified !== true) errors.push('block-store-restore provenance blockVerified must be true');
      if (!blockVerifyDigest) errors.push('block-store-restore provenance blockVerifyDigest must be present');
      else if (refDigest && blockVerifyDigest !== refDigest) errors.push('block-store-restore provenance blockVerifyDigest must match refDigest');
      if (!Number.isFinite(blockVerifyBytes) || blockVerifyBytes <= 0) errors.push('block-store-restore provenance blockVerifyBytes must be positive');
      else if (Number.isFinite(bytes) && bytes > 0 && blockVerifyBytes !== bytes) errors.push('block-store-restore provenance blockVerifyBytes must match decoded bytes');
    }
    if (!provenance?.adapterLabel) errors.push('block-store-restore provenance adapterLabel must be present');
    if (!provenance?.store) errors.push('block-store-restore provenance store must be present');
    if (!provenance?.provider) errors.push('block-store-restore provenance provider must be present');
  }
  return Object.freeze({ ok: errors.length === 0, errors: Object.freeze(errors), schema: CLEARANCE_RECEIPT_REGISTRATION_PROVENANCE_SCHEMA, source: source || null, lane: resolvedLane, reason: reason == null ? null : String(reason), receiptFingerprint: receiptFingerprint || null, preClearanceFingerprint: preClearanceFingerprint || null });
}
function normalizeClearanceReceiptRow(row) {
  if (!row || typeof row !== 'object') return row;
  const normalized = {
    opId: row.opId == null ? null : String(row.opId),
    kind: row.kind ?? row.op ?? null,
    lane: row.lane ?? null,
    operationEpoch: row.operationEpoch == null ? null : String(row.operationEpoch),
    operationReplayKey: row.operationReplayKey == null ? null : String(row.operationReplayKey),
    disposition: row.disposition ?? null,
    summary: row.summary ?? null,
    error: row.error ?? null
  };
  if (!normalized.operationReplayKey && normalized.opId && normalized.lane) normalized.operationReplayKey = clearanceReceiptOperationReplayKey(normalized);
  return Object.freeze(normalized);
}
function normalizedClearanceReceiptPayload(receipt = {}) {
  return Object.freeze({
    schema: CLEARANCE_RECEIPT_SCHEMA,
    lane: receipt.lane ?? null,
    reviewToken: receipt.reviewToken ?? null,
    reviewFingerprint: receipt.reviewFingerprint ?? null,
    preClearanceFingerprint: receipt.preClearanceFingerprint ?? null,
    postClearanceFingerprint: receipt.postClearanceFingerprint ?? null,
    categories: Array.isArray(receipt.categories) ? [...receipt.categories].map(String).sort() : [],
    opIds: Array.isArray(receipt.opIds) ? [...receipt.opIds].map(String).sort() : [],
    operationReplayKeys: Array.isArray(receipt.operationReplayKeys) ? [...receipt.operationReplayKeys].map(String).sort() : [],
    allowLaneWide: receipt.allowLaneWide === true,
    cleared: Object.freeze({
      successful: Array.isArray(receipt.cleared?.successful) ? receipt.cleared.successful.map(normalizeClearanceReceiptRow).sort((a, b) => timedOutOperationRowSortKey(a).localeCompare(timedOutOperationRowSortKey(b))) : [],
      failed: Array.isArray(receipt.cleared?.failed) ? receipt.cleared.failed.map(normalizeClearanceReceiptRow).sort((a, b) => timedOutOperationRowSortKey(a).localeCompare(timedOutOperationRowSortKey(b))) : []
    }),
    counts: receipt.counts && typeof receipt.counts === 'object' ? receipt.counts : null
  });
}
function timedOutOperationQuarantineClearanceReceiptFingerprint(receipt = {}) {
  return `brt-qclear-v1:${fnv1a64Hex(stableStringify(normalizedClearanceReceiptPayload(receipt)))}`;
}
function clearanceReceiptRowReplayKey(row, status = null) {
  const opId = row?.opId == null ? '' : String(row.opId);
  const lane = row?.lane == null ? '' : String(row.lane);
  const kind = row?.kind == null ? 'operation' : String(row.kind);
  const normalizedStatus = status == null ? '' : String(status);
  const epoch = row?.operationEpoch == null ? '' : String(row.operationEpoch);
  if (epoch) return `${normalizedStatus}:${lane}:${kind}:${epoch}:${opId}`;
  return `${normalizedStatus}:legacy:${lane}:${kind}:${opId}`;
}
function clearanceReceiptLegacyOperationReplayKey(row) {
  const opId = row?.opId == null ? '' : String(row.opId);
  const lane = row?.lane == null ? '' : String(row.lane);
  const kind = row?.kind == null ? 'operation' : String(row.kind);
  return `operation-legacy:${lane}:${kind}:${opId}`;
}
function clearanceReceiptOperationReplayKey(row) {
  if (row?.operationReplayKey != null && String(row.operationReplayKey)) return String(row.operationReplayKey);
  const opId = row?.opId == null ? '' : String(row.opId);
  const lane = row?.lane == null ? '' : String(row.lane);
  const kind = row?.kind == null ? 'operation' : String(row.kind);
  const epoch = row?.operationEpoch == null ? '' : String(row.operationEpoch);
  if (epoch) return `operation:${lane}:${kind}:${epoch}:${opId}`;
  return clearanceReceiptLegacyOperationReplayKey(row);
}
function timedOutOperationRowSortKey(row) {
  const opId = row?.opId == null ? '' : String(row.opId);
  const operationReplayKey = row?.operationReplayKey == null ? '' : String(row.operationReplayKey);
  const operationEpoch = row?.operationEpoch == null ? '' : String(row.operationEpoch);
  const lane = row?.lane == null ? '' : String(row.lane);
  const kind = row?.kind == null ? 'operation' : String(row.kind);
  return `${opId}\0${operationReplayKey}\0${operationEpoch}\0${lane}\0${kind}`;
}
function timedOutOperationMapKey(row) {
  const replayKey = row?.operationReplayKey == null ? '' : String(row.operationReplayKey);
  if (replayKey) return replayKey;
  const opId = row?.opId == null ? '' : String(row.opId);
  const lane = row?.lane == null ? '' : String(row.lane);
  const kind = row?.kind == null ? 'operation' : String(row.kind);
  const epoch = row?.operationEpoch == null ? '' : String(row.operationEpoch);
  if (opId && lane) return clearanceReceiptOperationReplayKey({ opId, lane, kind, operationEpoch: epoch || null });
  return opId;
}
function rowOperationReplayKey(row) {
  return timedOutOperationMapKey(row);
}
function ambiguousOpIdScopes(rows, opIdSet, { lane = null } = {}) {
  if (!opIdSet || opIdSet.size === 0) return Object.freeze([]);
  const laneFilter = lane == null ? null : String(lane);
  const seen = new Map();
  for (const row of rows || []) {
    if (!row || typeof row !== 'object') continue;
    const opId = row.opId == null ? '' : String(row.opId);
    if (!opId || !opIdSet.has(opId)) continue;
    if (laneFilter != null && row.lane !== laneFilter) continue;
    if (!seen.has(opId)) seen.set(opId, new Set());
    seen.get(opId).add(rowOperationReplayKey(row));
  }
  return Object.freeze([...seen.entries()].filter(([, keys]) => keys.size > 1).map(([opId, keys]) => Object.freeze({ opId, operationReplayKeys: Object.freeze([...keys].sort()) })));
}
function importedTimedOutReplayCandidates(imported = {}) {
  const candidates = [];
  for (const [status, rows] of Object.entries(imported || {})) {
    const normalizedStatus = status === 'successful' ? 'successful' : (status === 'failed' ? 'failed' : 'unsettled');
    for (const row of rows || []) {
      const statusKey = clearanceReceiptRowReplayKey(row, normalizedStatus);
      const operationKey = clearanceReceiptOperationReplayKey(row);
      const legacyOperationKey = clearanceReceiptLegacyOperationReplayKey(row);
      candidates.push(Object.freeze({ key: statusKey, statusKey, operationKey, legacyOperationKey, hasOperationEpoch: Boolean(row.operationEpoch), replayKeys: Object.freeze([statusKey, operationKey]), status: normalizedStatus, opId: row.opId, lane: row.lane, kind: row.kind, operationEpoch: row.operationEpoch ?? null, operationReplayKey: row.operationReplayKey ?? operationKey }));
    }
  }
  return Object.freeze(candidates);
}
function clearanceReceiptReplayMatches(receipt, candidate) {
  const cleared = new Set([...(receipt.clearedReplayKeys || []), ...(receipt.clearedOperationKeys || []), ...(receipt.clearedRowKeys || [])]);
  const clearedLegacy = new Set([...(receipt.clearedLegacyOperationKeys || [])]);
  if (candidate.replayKeys.some((key) => cleared.has(key))) return Object.freeze({ ...candidate, replayKind: 'cleared-row-or-operation' });
  if (!candidate.hasOperationEpoch && clearedLegacy.has(candidate.legacyOperationKey)) return Object.freeze({ ...candidate, replayKind: 'cleared-operation-identity-downgrade' });
  return null;
}
function operationEpochForExecutor(label) {
  const random = Math.random().toString(36).slice(2);
  return `brt-op-epoch-v1:${fnv1a64Hex(`${label}:${Date.now()}:${random}`)}`;
}
function expectedClearanceReceiptOperationReplayKey(row) { const opId = row?.opId == null ? '' : String(row.opId); const lane = row?.lane == null ? '' : String(row.lane); const kind = row?.kind == null ? 'operation' : String(row.kind); const epoch = row?.operationEpoch == null ? '' : String(row.operationEpoch); if (epoch) return `operation:${lane}:${kind}:${epoch}:${opId}`; return `operation-legacy:${lane}:${kind}:${opId}`; }
function uniqueSortedStrings(values) { return Object.freeze([...new Set((values || []).map(String).filter(Boolean))].sort()); }
function arraysEqual(a = [], b = []) { return a.length === b.length && a.every((value, index) => value === b[index]); }
function validateTimedOutOperationQuarantineClearanceReceiptForRegistration(receipt = {}) {
  const errors = [];
  if (!receipt || typeof receipt !== 'object') errors.push('receipt must be an object');
  if (receipt?.schema !== CLEARANCE_RECEIPT_SCHEMA) errors.push(`schema must be ${CLEARANCE_RECEIPT_SCHEMA}`);
  for (const key of ['receiptFingerprint', 'reviewToken', 'reviewFingerprint', 'preClearanceFingerprint', 'postClearanceFingerprint']) {
    if (!receipt?.[key] || typeof receipt[key] !== 'string') errors.push(`${key} must be present`);
  }
  const successful = Array.isArray(receipt?.cleared?.successful) ? receipt.cleared.successful : [];
  const failed = Array.isArray(receipt?.cleared?.failed) ? receipt.cleared.failed : [];
  const allRows = successful.concat(failed);
  const receiptLane = receipt?.lane == null ? null : String(receipt.lane);
  const allowLaneWide = receipt?.allowLaneWide === true;
  if (!receiptLane) errors.push('receipt lane must be present; lane-wide receipts are lane-scoped, not lane-ambiguous');
  const statusRows = successful.map((row) => [row, 'successful']).concat(failed.map((row) => [row, 'failed']));
  const opIds = new Set();
  const seenOperationKeys = new Set();
  const clearedRowKeys = [];
  const clearedOperationKeys = [];
  const clearedLegacyOperationKeys = [];
  const clearedReplayKeys = [];
  for (const [row, status] of statusRows) {
    const opId = row?.opId == null ? '' : String(row.opId);
    if (!opId) errors.push('cleared row opId must be present'); else opIds.add(opId);
    const rowLane = row?.lane == null ? null : String(row.lane);
    if (!rowLane) errors.push('cleared row lane must be present'); else if (receiptLane && rowLane !== receiptLane) errors.push(`cleared row lane ${rowLane} must match receipt lane ${receiptLane}`);
    if (opId) {
      const statusKey = clearanceReceiptRowReplayKey(row, status);
      const operationKey = clearanceReceiptOperationReplayKey(row);
      const expectedOperationKey = expectedClearanceReceiptOperationReplayKey(row);
      const legacyOperationKey = clearanceReceiptLegacyOperationReplayKey(row);
      if (operationKey && expectedOperationKey && operationKey !== expectedOperationKey) errors.push(`cleared row operationReplayKey mismatch for ${opId}`);
      if (seenOperationKeys.has(operationKey)) errors.push(`duplicate cleared operationReplayKey ${operationKey}`); else seenOperationKeys.add(operationKey);
      clearedRowKeys.push(statusKey); clearedOperationKeys.push(operationKey); clearedLegacyOperationKeys.push(legacyOperationKey); clearedReplayKeys.push(statusKey, operationKey);
    }
  }
  const explicitOpIds = Array.isArray(receipt?.opIds) ? receipt.opIds.map(String).sort() : [];
  const rowOpIds = [...opIds].sort();
  if (explicitOpIds.length > 0 && !arraysEqual(explicitOpIds, rowOpIds)) errors.push('opIds must match cleared row opIds');
  const explicitOperationReplayKeys = Array.isArray(receipt?.operationReplayKeys) ? uniqueSortedStrings(receipt.operationReplayKeys) : [];
  const rowOperationReplayKeys = uniqueSortedStrings(clearedOperationKeys);
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
  if (allRows.length <= 0) errors.push('clearance receipt must clear at least one timed-out operation');
  if (receipt?.preClearanceFingerprint && receipt?.reviewFingerprint && String(receipt.preClearanceFingerprint) !== String(receipt.reviewFingerprint)) errors.push('preClearanceFingerprint must match reviewFingerprint');
  const expected = timedOutOperationQuarantineClearanceReceiptFingerprint(receipt || {});
  if (receipt?.receiptFingerprint && String(receipt.receiptFingerprint) !== expected) errors.push('receiptFingerprint mismatch');
  return Object.freeze({ ok: errors.length === 0, errors: Object.freeze(errors), receiptFingerprint: expected, receiptLane, allowLaneWide, operationReplayKeys: rowOperationReplayKeys, clearedRowKeys: Object.freeze(clearedRowKeys), clearedOperationKeys: Object.freeze([...new Set(clearedOperationKeys)]), clearedLegacyOperationKeys: Object.freeze([...new Set(clearedLegacyOperationKeys)]), clearedReplayKeys: Object.freeze([...new Set(clearedReplayKeys)]), clearedCount: allRows.length, successfulClearedCount: successful.length, failedClearedCount: failed.length });
}
function storageLaneError(code, message, detail = {}) {
  const error = new Error(message);
  error.name = 'BrowserRTStorageLaneError';
  error.code = code;
  error.storageDisposition = code;
  error.detail = Object.freeze({ ...detail });
  return error;
}
function normalizeOperationTimeoutMs(timeoutMs) {
  if (timeoutMs === undefined || timeoutMs === null || timeoutMs === false) return 0;
  const n = Number(timeoutMs);
  if (!Number.isFinite(n) || n < 0) throw new Error(`storage-lane operationTimeoutMs must be a non-negative finite number: ${timeoutMs}`);
  return Math.floor(n);
}
async function runWithOperationTimeout(run, { timeoutMs = 0, detail = null, onTimeout = null, onLateSettlement = null, abortProviderOnTimeout = false } = {}) {
  const normalizedTimeoutMs = normalizeOperationTimeoutMs(timeoutMs);
  let timedOut = false;
  const shouldAbortProviderOnTimeout = abortProviderOnTimeout === true;
  if (shouldAbortProviderOnTimeout && typeof AbortController !== 'function') {
    throw storageLaneError('BRT_STORAGE_OPERATION_TIMEOUT_ABORT_UNAVAILABLE', 'storage-lane provider timeout abort requires AbortController', { ...(detail || {}), timeoutMs: normalizedTimeoutMs });
  }
  const timeoutAbortController = shouldAbortProviderOnTimeout ? new AbortController() : null;
  const context = Object.freeze({
    ...(detail || {}),
    operationTimeoutMs: normalizedTimeoutMs,
    abortProviderOnOperationTimeout: shouldAbortProviderOnTimeout,
    signal: timeoutAbortController?.signal ?? null,
    abortSignal: timeoutAbortController?.signal ?? null,
    get timedOut() { return timedOut; },
    isTimedOut() { return timedOut; }
  });
  const runPromise = Promise.resolve().then(() => run(context));
  runPromise.then(
    (result) => { if (timedOut) onLateSettlement?.({ ok: true, result }); return result; },
    (error) => { if (timedOut) onLateSettlement?.({ ok: false, error }); }
  ).catch(() => {});
  if (normalizedTimeoutMs <= 0) return await runPromise;
  let timeoutId = null;
  const timeoutPromise = new Promise((_, reject) => {
    timeoutId = setTimeout(() => {
      timedOut = true;
      let abortDetail = null;
      if (timeoutAbortController && !timeoutAbortController.signal.aborted) {
        abortDetail = storageLaneError('BRT_STORAGE_OPERATION_TIMEOUT_ABORT', `storage-lane operation timeout aborted provider context after ${normalizedTimeoutMs}ms`, { ...(detail || {}), timeoutMs: normalizedTimeoutMs });
        try { timeoutAbortController.abort(abortDetail); } catch { timeoutAbortController.abort(); }
      }
      onTimeout?.({ abortProviderOnTimeout: shouldAbortProviderOnTimeout, providerAbortSignaled: Boolean(abortDetail) });
      reject(storageLaneError('BRT_STORAGE_OPERATION_TIMEOUT', `storage-lane operation timed out after ${normalizedTimeoutMs}ms`, { ...(detail || {}), timeoutMs: normalizedTimeoutMs, abortProviderOnTimeout: shouldAbortProviderOnTimeout, providerAbortSignaled: Boolean(abortDetail) }));
    }, normalizedTimeoutMs);
  });
  try {
    return await Promise.race([runPromise, timeoutPromise]);
  } finally {
    if (timeoutId !== null) clearTimeout(timeoutId);
  }
}
const READ_ONLY_WEB_LOCK_OPS = new Set(['get', 'has', 'verify', 'estimate']);
function webLockTimeoutOp(detail) {
  const providerDetail = detail?.providerDetail && typeof detail.providerDetail === 'object' ? detail.providerDetail : null;
  const metadata = providerDetail?.metadata && typeof providerDetail.metadata === 'object' ? providerDetail.metadata : null;
  return String(metadata?.op || providerDetail?.op || detail?.op || '');
}
function isReadOnlyWebLockTimeout(detail) {
  const code = String(detail?.code || detail?.storageDisposition || '');
  if (code !== 'BRT_WEB_LOCK_TIMEOUT') return false;
  return READ_ONLY_WEB_LOCK_OPS.has(webLockTimeoutOp(detail));
}
function isStorageHealthFailure(detail) {
  const code = String(detail?.code || detail?.storageDisposition || '');
  if (!code) return false;
  if (isReadOnlyWebLockTimeout(detail)) return false;
  return code.startsWith('BRT_STORAGE')
    || code === 'BRT_OPFS_QUOTA_EXCEEDED'
    || code === 'BRT_OPFS_SECURITY_ERROR'
    || code === 'BRT_OPFS_INVALID_STATE'
    || code === 'BRT_OPFS_OPERATION_FAILED'
    || code === 'BRT_WEB_LOCK_TIMEOUT'
    || code === 'BRT_WEB_LOCKS_UNAVAILABLE';
}
export class StorageLaneExecutor {
  #trace;
  #ops = new Map();
  #results = new Map();
  #unsettledTimedOutOps = new Map();
  #failedTimedOutOps = new Map();
  #successfulTimedOutOps = new Map();
  #clearedQuarantineReceipts = new Map();
  #nextTaskSeq = 1;
  #operationEpoch;
  constructor({ label = 'storage-lane-executor', scheduler, mailbox = null, lane = 'storage', trace = null, markUnhealthyOnError = true, defaultOperationTimeoutMs = 0, operationTimeoutMs = undefined, abortProviderOnOperationTimeout = false } = {}) {
    if (!scheduler || typeof scheduler.enqueue !== 'function' || typeof scheduler.dispatchNext !== 'function' || typeof scheduler.complete !== 'function') throw new Error('StorageLaneExecutor requires a CrossLaneScheduler-like scheduler');
    this.label = label; this.scheduler = scheduler; this.mailbox = mailbox; this.lane = lane; this.markUnhealthyOnError = Boolean(markUnhealthyOnError); this.abortProviderOnOperationTimeout = abortProviderOnOperationTimeout === true; this.#trace = trace;
    this.#operationEpoch = operationEpochForExecutor(label);
    this.defaultOperationTimeoutMs = normalizeOperationTimeoutMs(operationTimeoutMs === undefined ? defaultOperationTimeoutMs : operationTimeoutMs);
    this.stats = { scheduled: 0, rejected: 0, dispatched: 0, completed: 0, failed: 0, emptyDispatches: 0, laneHealthFailures: 0, operationTimeouts: 0, providerTimeoutAborts: 0, lateProviderSettlements: 0, lateProviderSettlementSuccesses: 0, lateProviderSettlementFailures: 0, unsettledTimedOutOperations: 0, successfulTimedOutOperations: 0, successfulTimedOutOperationsCleared: 0, failedTimedOutOperations: 0, failedTimedOutOperationsCleared: 0, timedOutOperationClearRejected: 0, lateProviderSuccessClearRejected: 0, lateProviderFailureClearRejected: 0, markHealthyQuarantineRejected: 0, timedOutOperationQuarantineQueries: 0, timedOutOperationQuarantineClearRejected: 0, timedOutOperationQuarantineCleared: 0, reviewedTimedOutOperationQuarantine: 0, quarantineLedgerExports: 0, quarantineLedgerImports: 0, quarantineLedgerImportRejected: 0, quarantineLedgerImportIntegrityRejected: 0, quarantineLedgerImportBackpressureForced: 0, quarantineLedgerLaneFilterRejected: 0, quarantineLedgerPartialImportRejected: 0, quarantineLedgerEmptyLaneFilterRejected: 0, quarantineLedgerPartialImportAllowed: 0, quarantineLedgerPartialImports: 0, importedUnsettledTimedOutOperations: 0, importedSuccessfulTimedOutOperations: 0, importedFailedTimedOutOperations: 0, reviewedLateProviderSuccesses: 0, reviewedLateProviderFailures: 0, timedOutOperationReviewManifests: 0, timedOutOperationReviewManifestRejected: 0, timedOutOperationReviewFingerprintRejected: 0, quarantineLedgerFingerprintRejected: 0, timedOutOperationReviewScopeRejected: 0, timedOutOperationReviewCountRejected: 0, unsettledTimedOutOperationsFinalized: 0, reviewedUnsettledTimedOutOperations: 0, timedOutOperationFinalizeRejected: 0, quarantineClearanceReceiptsRegistered: 0, quarantineLedgerReplayRejected: 0, quarantineLedgerRowReplayRejected: 0, quarantineLedgerLegacyRowReplayRejected: 0, quarantineClearanceReceiptRejected: 0, quarantineClearanceReceiptIntegrityRejected: 0, quarantineClearanceReceiptProvenanceRejected: 0, quarantineClearanceReceiptProvenanceAccepted: 0, quarantineClearanceReceiptLaneBindingRejected: 0, timedOutOperationReviewReplayKeyScopes: 0, timedOutOperationReviewReplayKeyScopeRejected: 0, timedOutOperationReviewOpIdAmbiguousRejected: 0, quarantineClearanceReceiptReplayKeyBindingRejected: 0, quarantineLedgerStatusTransitionReplacements: 0 };
    this.#emit('storage-lane:create', { lane, markUnhealthyOnError: this.markUnhealthyOnError, defaultOperationTimeoutMs: this.defaultOperationTimeoutMs, abortProviderOnOperationTimeout: this.abortProviderOnOperationTimeout });
  }
  #emit(kind, payload = {}) {
    const detail = { ...payload };
    if (Object.hasOwn(detail, 'kind')) {
      detail.opKind = detail.kind;
      delete detail.kind;
    }
    this.#trace?.emit(kind, { label: this.label, lane: this.lane, ...detail });
  }
  scheduleOperation({ id = null, kind = 'operation', lane = this.lane, fallbackLanes = [], priority = 'background', cost = 1, dependsOn = [], flowId = null, run, metadata = null, operationTimeoutMs = undefined, timeoutMs = undefined, abortProviderOnOperationTimeout = undefined } = {}) {
    if (typeof run !== 'function') throw new Error('scheduleOperation requires run()');
    const opId = id || `${this.label}:${kind}:${this.#nextTaskSeq++}`;
    const scheduler = this.scheduler.enqueue({ id: opId, lane, fallbackLanes, priority, cost, dependsOn, flowId: flowId || kind, payload: { component: 'StorageLaneExecutor', opId, kind }, metadata: { component: 'StorageLaneExecutor', kind, ...metadata } });
    if (!scheduler.accepted) {
      this.stats.rejected += 1;
      this.#emit('storage-lane:reject', { opId, kind, disposition: scheduler.disposition, reason: scheduler.reason, lane, noMutation: scheduler.noMutation === true });
      return Object.freeze({ accepted: false, opId, kind, scheduler });
    }
    this.stats.scheduled += 1;
    const opTimeoutMs = normalizeOperationTimeoutMs(operationTimeoutMs === undefined ? (timeoutMs === undefined ? this.defaultOperationTimeoutMs : timeoutMs) : operationTimeoutMs);
    const operationEpoch = this.#operationEpoch;
    const operationReplayKey = clearanceReceiptOperationReplayKey({ opId, kind, lane: scheduler.lane ?? lane, operationEpoch });
    const abortOnTimeout = abortProviderOnOperationTimeout === undefined ? this.abortProviderOnOperationTimeout : abortProviderOnOperationTimeout === true;
    this.#ops.set(opId, { opId, kind, run, operationTimeoutMs: opTimeoutMs, operationEpoch, operationReplayKey, abortProviderOnOperationTimeout: abortOnTimeout });
    this.#emit('storage-lane:schedule', { opId, kind, lane: scheduler.lane, requestedLane: scheduler.requestedLane, priority, cost, dependsOn, fallbackLanes, operationTimeoutMs: opTimeoutMs, abortProviderOnOperationTimeout: abortOnTimeout });
    return Object.freeze({ accepted: true, opId, kind, scheduler });
  }
  scheduleMailboxEnqueue(mailbox, payload, { id = null, priority = 'background', cost = null, dependsOn = [], lane = this.lane, fallbackLanes = [], enqueue = {}, operationTimeoutMs = undefined, timeoutMs = undefined } = {}) {
    const bytes = typeof payload === 'string' ? new TextEncoder().encode(payload).byteLength : (payload?.byteLength ?? payload?.length ?? 1);
    return this.scheduleOperation({ id, kind: 'mailbox-enqueue', lane, fallbackLanes, priority, cost: cost ?? Math.max(1, Math.ceil(bytes / 16)), dependsOn, run: async () => mailbox.enqueue(payload, enqueue), operationTimeoutMs, timeoutMs });
  }
  scheduleMailboxDequeue(mailbox, { id = null, priority = 'user-visible', cost = 1, dependsOn = [], lane = this.lane, fallbackLanes = [], consumerId = 'storage-lane-consumer', operationTimeoutMs = undefined, timeoutMs = undefined } = {}) {
    return this.scheduleOperation({ id, kind: 'mailbox-dequeue', lane, fallbackLanes, priority, cost, dependsOn, run: async () => mailbox.dequeue({ consumerId }), operationTimeoutMs, timeoutMs });
  }
  scheduleMailboxCheckpoint(mailbox, { id = null, priority = 'background', cost = 1, dependsOn = [], lane = this.lane, fallbackLanes = [], label = null, operationTimeoutMs = undefined, timeoutMs = undefined } = {}) {
    return this.scheduleOperation({ id, kind: 'mailbox-checkpoint', lane, fallbackLanes, priority, cost, dependsOn, run: async () => mailbox.checkpoint({ label }), operationTimeoutMs, timeoutMs });
  }
  scheduleMailboxCompact(mailbox, { id = null, priority = 'maintenance', cost = 2, dependsOn = [], lane = 'maintenance', fallbackLanes = [], dryRun = false, reason = 'storage-lane', operationTimeoutMs = undefined, timeoutMs = undefined } = {}) {
    return this.scheduleOperation({ id, kind: 'mailbox-compact', lane, fallbackLanes, priority, cost, dependsOn, run: async () => mailbox.compact({ dryRun, reason }), operationTimeoutMs, timeoutMs });
  }
  submit(op, args = {}, options = {}) {
    if (!SUPPORTED_OP_SET.has(op)) throw new Error(`Unsupported storage lane op: ${op}`);
    const mailbox = this.mailbox;
    if (!mailbox) throw new Error('submit() requires the executor to be constructed with mailbox');
    if (op === 'enqueue') return this.scheduleMailboxEnqueue(mailbox, args.payload ?? args.bytes ?? '', { id: options.id, priority: options.priority, cost: options.cost, dependsOn: options.dependsOn, lane: options.lane || this.lane, fallbackLanes: options.fallbackLanes, enqueue: { seq: args.seq ?? null, label: args.label ?? null }, operationTimeoutMs: options.operationTimeoutMs, timeoutMs: options.timeoutMs });
    if (op === 'dequeue') return this.scheduleMailboxDequeue(mailbox, { id: options.id, priority: options.priority, cost: options.cost, dependsOn: options.dependsOn, lane: options.lane || this.lane, fallbackLanes: options.fallbackLanes, consumerId: args.consumerId, operationTimeoutMs: options.operationTimeoutMs, timeoutMs: options.timeoutMs });
    if (op === 'checkpoint') return this.scheduleMailboxCheckpoint(mailbox, { id: options.id, priority: options.priority, cost: options.cost, dependsOn: options.dependsOn, lane: options.lane || this.lane, fallbackLanes: options.fallbackLanes, label: args.label, operationTimeoutMs: options.operationTimeoutMs, timeoutMs: options.timeoutMs });
    if (op === 'compact') return this.scheduleMailboxCompact(mailbox, { id: options.id, priority: options.priority, cost: options.cost, dependsOn: options.dependsOn, lane: options.lane || 'maintenance', fallbackLanes: options.fallbackLanes, dryRun: args.dryRun, reason: args.reason, operationTimeoutMs: options.operationTimeoutMs, timeoutMs: options.timeoutMs });
    if (op === 'ack') return this.scheduleOperation({ id: options.id, kind: 'mailbox-ack', lane: options.lane || this.lane, fallbackLanes: options.fallbackLanes || [], priority: options.priority || 'user-visible', cost: options.cost || 1, dependsOn: options.dependsOn || [], run: async () => mailbox.ack(args.pendingId, { deleteBlock: args.deleteBlock }), operationTimeoutMs: options.operationTimeoutMs, timeoutMs: options.timeoutMs });
    if (op === 'snapshot') return this.scheduleOperation({ id: options.id, kind: 'mailbox-snapshot', lane: options.lane || this.lane, fallbackLanes: options.fallbackLanes || [], priority: options.priority || 'background', cost: options.cost || 1, dependsOn: options.dependsOn || [], run: async () => mailbox.snapshot(), operationTimeoutMs: options.operationTimeoutMs, timeoutMs: options.timeoutMs });
  }
  async executeNext() { const drained = await this.drain({ maxSteps: 1 }); return drained.results[0] || Object.freeze({ dispatched: false, disposition: 'empty' }); }
  async executeDispatched(dispatched) { if (!dispatched?.task) throw new Error('executeDispatched requires a scheduler dispatch result'); return this.#runDispatched(dispatched); }
  async drain({ maxSteps = 100 } = {}) {
    const results = [];
    for (let i = 0; i < maxSteps; i += 1) {
      const dispatch = this.scheduler.dispatchNext();
      if (!dispatch.dispatched) { this.stats.emptyDispatches += 1; this.#emit('storage-lane:dispatch-empty', { disposition: dispatch.disposition || 'empty', queuedCount: dispatch.queuedCount, inFlightCount: dispatch.inFlightCount }); results.push(Object.freeze({ dispatched: false, disposition: dispatch.disposition || 'empty', scheduler: dispatch })); break; }
      results.push(await this.#runDispatched(dispatch));
    }
    return Object.freeze({ results, snapshot: this.snapshot() });
  }
  #rememberTimedOutOperation({ opId, kind, lane, timeoutMs, operationEpoch = null, operationReplayKey = null }) {
    const base = { opId: String(opId), kind: String(kind), lane: String(lane), operationEpoch: operationEpoch == null ? null : String(operationEpoch) };
    const row = Object.freeze({ ...base, operationReplayKey: operationReplayKey == null ? clearanceReceiptOperationReplayKey(base) : String(operationReplayKey), timeoutMs: normalizeOperationTimeoutMs(timeoutMs), timedOutAtMs: Date.now() });
    this.#unsettledTimedOutOps.set(timedOutOperationMapKey(row), row);
    this.stats.unsettledTimedOutOperations = this.#unsettledTimedOutOps.size;
    this.#emit('storage-lane:operation-timeout-unsettled', { opId: row.opId, kind: row.kind, lane: row.lane, operationEpoch: row.operationEpoch, operationReplayKey: row.operationReplayKey, timeoutMs: row.timeoutMs, unsettledTimedOutOperationCount: this.#unsettledTimedOutOps.size });
  }
  #settleTimedOutOperation(opId, { ok, result = null, error = null, operationReplayKey = null } = {}) {
    const requestedKey = operationReplayKey == null ? '' : String(operationReplayKey);
    let key = requestedKey && this.#unsettledTimedOutOps.has(requestedKey) ? requestedKey : String(opId);
    let row = this.#unsettledTimedOutOps.get(key);
    if (!row) {
      for (const [candidateKey, candidateRow] of this.#unsettledTimedOutOps.entries()) {
        if (candidateRow.opId === String(opId) && (!requestedKey || candidateRow.operationReplayKey === requestedKey)) { key = candidateKey; row = candidateRow; break; }
      }
    }
    if (!row) return;
    const errorDetail = ok ? null : describeError(error);
    this.#unsettledTimedOutOps.delete(key);
    this.stats.lateProviderSettlements += 1;
    const legacyOpId = row?.opId == null ? null : String(row.opId);
    const cleanupKeys = new Set([key, legacyOpId].filter((value) => value != null && String(value)));
    for (const cleanupKey of cleanupKeys) {
      this.#successfulTimedOutOps.delete(cleanupKey);
      this.#failedTimedOutOps.delete(cleanupKey);
    }
    if (ok) {
      const success = Object.freeze({ ...row, settledAtMs: Date.now(), result: summarizeResult(result) });
      this.#successfulTimedOutOps.set(key, success);
      this.stats.lateProviderSettlementSuccesses += 1;
      this.stats.successfulTimedOutOperations = this.#successfulTimedOutOps.size;
      this.#emit('storage-lane:late-provider-success', { opId: row.opId, kind: row.kind, lane: row.lane, result: summarizeResult(result), successfulTimedOutOperationCount: this.#successfulTimedOutOps.size });
    } else {
      const failure = Object.freeze({ ...row, settledAtMs: Date.now(), error: errorDetail });
      this.#failedTimedOutOps.set(key, failure);
      this.stats.lateProviderSettlementFailures += 1;
      this.stats.failedTimedOutOperations = this.#failedTimedOutOps.size;
      this.#emit('storage-lane:late-provider-failure', { opId: row.opId, kind: row.kind, lane: row.lane, error: errorDetail, failedTimedOutOperationCount: this.#failedTimedOutOps.size });
    }
    this.stats.unsettledTimedOutOperations = this.#unsettledTimedOutOps.size;
    this.#emit('storage-lane:late-provider-settlement', { opId: row.opId, kind: row.kind, lane: row.lane, ok: Boolean(ok), result: ok ? summarizeResult(result) : null, error: errorDetail, unsettledTimedOutOperationCount: this.#unsettledTimedOutOps.size, successfulTimedOutOperationCount: this.#successfulTimedOutOps.size, failedTimedOutOperationCount: this.#failedTimedOutOps.size });
  }
  unsettledTimedOutOperations(lane = null) {
    const laneFilter = lane == null ? null : String(lane);
    return Object.freeze([...this.#unsettledTimedOutOps.values()].filter((row) => laneFilter == null || row.lane === laneFilter).map((row) => Object.freeze({ ...row })));
  }
  unsettledTimedOutOperationCount(lane = null) {
    return this.unsettledTimedOutOperations(lane).length;
  }
  failedTimedOutOperations(lane = null) {
    const laneFilter = lane == null ? null : String(lane);
    return Object.freeze([...this.#failedTimedOutOps.values()].filter((row) => laneFilter == null || row.lane === laneFilter).map((row) => Object.freeze({ ...row })));
  }
  failedTimedOutOperationCount(lane = null) {
    return this.failedTimedOutOperations(lane).length;
  }
  successfulTimedOutOperations(lane = null) {
    const laneFilter = lane == null ? null : String(lane);
    return Object.freeze([...this.#successfulTimedOutOps.values()].filter((row) => laneFilter == null || row.lane === laneFilter).map((row) => Object.freeze({ ...row })));
  }
  successfulTimedOutOperationCount(lane = null) {
    return this.successfulTimedOutOperations(lane).length;
  }
  exportTimedOutOperationQuarantine({ lane = null, reason = 'operator-export-timed-out-operation-quarantine' } = {}) {
    const quarantine = this.timedOutOperationQuarantine(lane);
    const fingerprint = timedOutQuarantineFingerprint(quarantine);
    const ledger = Object.freeze({
      schema: quarantine.schema,
      quarantineFingerprint: fingerprint,
      reviewFingerprint: fingerprint,
      exportedAtMs: Date.now(),
      label: this.label,
      reason: String(reason),
      lane: quarantine.lane,
      counts: Object.freeze({
        total: quarantine.totalCount,
        unsettled: quarantine.unsettledTimedOutOperationCount,
        successful: quarantine.successfulTimedOutOperationCount,
        failed: quarantine.failedTimedOutOperationCount
      }),
      unsettledTimedOutOperations: quarantine.unsettledTimedOutOperations,
      successfulTimedOutOperations: quarantine.successfulTimedOutOperations,
      failedTimedOutOperations: quarantine.failedTimedOutOperations
    });
    this.stats.quarantineLedgerExports += 1;
    this.#emit('storage-lane:timed-out-quarantine-export', { lane: quarantine.lane, reason: ledger.reason, totalCount: quarantine.totalCount, unsettledTimedOutOperationCount: quarantine.unsettledTimedOutOperationCount, successfulTimedOutOperationCount: quarantine.successfulTimedOutOperationCount, failedTimedOutOperationCount: quarantine.failedTimedOutOperationCount, quarantineFingerprint: fingerprint });
    return ledger;
  }
  #normalizeImportedTimedOutRow(row, { fallbackLane = null, status = 'unsettled' } = {}) {
    if (!row || typeof row !== 'object') throw new Error('timed-out operation quarantine row must be an object');
    const opId = row.opId == null ? '' : String(row.opId);
    if (!opId) throw new Error('timed-out operation quarantine row requires opId');
    const lane = row.lane == null ? (fallbackLane == null ? this.lane : String(fallbackLane)) : String(row.lane);
    if (!lane) throw new Error('timed-out operation quarantine row requires lane');
    const kind = row.kind == null ? 'operation' : String(row.kind);
    const timeoutMs = normalizeOperationTimeoutMs(row.timeoutMs ?? 0);
    const timedOutAtMs = Number.isFinite(Number(row.timedOutAtMs)) ? Number(row.timedOutAtMs) : Date.now();
    const operationEpoch = row.operationEpoch == null ? null : String(row.operationEpoch);
    const computedOperationReplayKey = clearanceReceiptOperationReplayKey({ opId, kind, lane, operationEpoch });
    const operationReplayKey = row.operationReplayKey == null ? computedOperationReplayKey : String(row.operationReplayKey);
    if (operationReplayKey !== computedOperationReplayKey) throw new Error(`operationReplayKey mismatch for timed-out operation quarantine row: ${opId}`);
    const base = { opId, kind, lane, operationEpoch, operationReplayKey, timeoutMs, timedOutAtMs, importedAtMs: Date.now(), imported: true };
    if (status === 'successful') {
      return Object.freeze({ ...base, settledAtMs: Number.isFinite(Number(row.settledAtMs)) ? Number(row.settledAtMs) : Date.now(), result: row.result && typeof row.result === 'object' ? Object.freeze({ ...row.result }) : null });
    }
    if (status === 'failed') {
      return Object.freeze({ ...base, settledAtMs: Number.isFinite(Number(row.settledAtMs)) ? Number(row.settledAtMs) : Date.now(), error: row.error && typeof row.error === 'object' ? Object.freeze({ ...row.error }) : describeError(row.error ?? 'imported timed-out provider failure') });
    }
    return Object.freeze(base);
  }
  #validateTimedOutQuarantineLedger(ledger, { laneFilter = null } = {}) {
    if (!ledger || typeof ledger !== 'object') throw new Error('timed-out operation quarantine ledger must be an object');
    if (ledger.schema !== 'brt.storageLane.timedOutOperationQuarantine.v1') throw new Error(`unsupported timed-out operation quarantine ledger schema: ${ledger.schema}`);
    const bucketSpecs = Object.freeze([
      ['unsettledTimedOutOperations', 'unsettled'],
      ['successfulTimedOutOperations', 'successful'],
      ['failedTimedOutOperations', 'failed']
    ]);
    for (const [key] of bucketSpecs) {
      if (!Array.isArray(ledger[key])) throw new Error(`timed-out operation quarantine ledger requires array bucket ${key}`);
    }
    if (!ledger.counts || typeof ledger.counts !== 'object') throw new Error('timed-out operation quarantine ledger requires counts object');
    const rawCounts = Object.freeze({
      unsettled: ledger.unsettledTimedOutOperations.length,
      successful: ledger.successfulTimedOutOperations.length,
      failed: ledger.failedTimedOutOperations.length
    });
    const expectedTotal = rawCounts.unsettled + rawCounts.successful + rawCounts.failed;
    const countFields = Object.freeze([
      ['unsettled', rawCounts.unsettled],
      ['successful', rawCounts.successful],
      ['failed', rawCounts.failed]
    ]);
    for (const [key, value] of countFields) {
      if (Number(ledger.counts[key]) !== value) throw new Error(`counts.${key} mismatch for timed-out operation quarantine ledger`);
    }
    if (Number(ledger.counts.total) !== expectedTotal) throw new Error('counts.total mismatch for timed-out operation quarantine ledger');
    const expectedFingerprint = timedOutQuarantineFingerprint(ledger);
    for (const key of ['quarantineFingerprint', 'reviewFingerprint']) {
      if (ledger[key] != null && String(ledger[key]) !== expectedFingerprint) throw new Error(`${key} mismatch for timed-out operation quarantine ledger`);
    }
    const seen = new Map();
    const normalizedAll = { unsettled: [], successful: [], failed: [] };
    for (const [key, status] of bucketSpecs) {
      for (const row of ledger[key]) {
        const normalized = this.#normalizeImportedTimedOutRow(row, { fallbackLane: ledger.lane ?? laneFilter, status });
        const operationKey = timedOutOperationMapKey(normalized);
        if (seen.has(operationKey)) throw new Error(`duplicate operationReplayKey in timed-out operation quarantine ledger: ${operationKey}`);
        seen.set(operationKey, status);
        normalizedAll[status].push(normalized);
      }
    }
    const imported = { unsettled: [], successful: [], failed: [] };
    const filteredOut = { unsettled: [], successful: [], failed: [] };
    const affectedLanes = new Set();
    const filteredOutLanes = new Set();
    for (const status of ['unsettled', 'successful', 'failed']) {
      for (const normalized of normalizedAll[status]) {
        if (laneFilter != null && normalized.lane !== laneFilter) {
          filteredOut[status].push(normalized);
          filteredOutLanes.add(normalized.lane);
          continue;
        }
        imported[status].push(normalized);
        affectedLanes.add(normalized.lane);
      }
    }
    const importedCount = imported.unsettled.length + imported.successful.length + imported.failed.length;
    const filteredOutCount = filteredOut.unsettled.length + filteredOut.successful.length + filteredOut.failed.length;
    return Object.freeze({ imported, filteredOut, affectedLanes: Object.freeze([...affectedLanes]), filteredOutLanes: Object.freeze([...filteredOutLanes]), rawCounts, rawTotal: expectedTotal, expectedTotal, importedCount, filteredOutCount, quarantineFingerprint: expectedFingerprint });
  }
  registerTimedOutOperationQuarantineClearanceReceipt(receipt, { lane = null, reason = 'operator-register-timed-out-operation-quarantine-clearance-receipt', provenance = null } = {}) {
    const reject = (code, disposition, detail = {}) => {
      this.stats.quarantineClearanceReceiptRejected += 1;
      const result = Object.freeze({ ok: false, code, disposition, reason: String(reason), ...detail });
      this.#emit('storage-lane:timed-out-quarantine-clearance-receipt-rejected', result);
      return result;
    };
    if (!receipt || typeof receipt !== 'object') return reject('timed-out-quarantine-clearance-receipt-object-required', 'rejected-clearance-receipt-integrity');
    const requestedLane = lane == null ? null : String(lane);
    const suppliedReceiptLane = receipt.lane == null ? null : String(receipt.lane);
    const suppliedAllowLaneWide = receipt.allowLaneWide === true;
    if (requestedLane != null && suppliedReceiptLane != null && requestedLane !== suppliedReceiptLane) {
      this.stats.quarantineClearanceReceiptIntegrityRejected += 1;
      this.stats.quarantineClearanceReceiptLaneBindingRejected += 1;
      return reject('timed-out-quarantine-clearance-receipt-lane-mismatch', 'rejected-clearance-receipt-lane-binding', { receiptLane: suppliedReceiptLane, requestedLane, schema: receipt.schema ?? null, suppliedReceiptFingerprint: receipt.receiptFingerprint ?? null });
    }
    const validation = validateTimedOutOperationQuarantineClearanceReceiptForRegistration(receipt);
    if (!validation.ok) {
      this.stats.quarantineClearanceReceiptIntegrityRejected += 1;
      if (validation.errors.some((message) => String(message).includes('lane'))) this.stats.quarantineClearanceReceiptLaneBindingRejected += 1;
      if (validation.errors.some((message) => String(message).includes('operationReplayKey'))) this.stats.quarantineClearanceReceiptReplayKeyBindingRejected += 1;
      return reject('timed-out-quarantine-clearance-receipt-integrity-rejected', 'rejected-clearance-receipt-integrity', { errors: validation.errors, expectedReceiptFingerprint: validation.receiptFingerprint, suppliedReceiptFingerprint: receipt.receiptFingerprint ?? null, schema: receipt.schema ?? null });
    }
    const provenanceValidation = validateTimedOutOperationQuarantineClearanceReceiptRegistrationProvenance(provenance, receipt, { lane, reason });
    if (!provenanceValidation.ok) {
      this.stats.quarantineClearanceReceiptProvenanceRejected += 1;
      return reject('timed-out-quarantine-clearance-receipt-provenance-rejected', 'rejected-clearance-receipt-provenance', { errors: provenanceValidation.errors, receiptFingerprint: receipt.receiptFingerprint ?? null, preClearanceFingerprint: receipt.preClearanceFingerprint ?? null, provenanceSource: provenanceValidation.source, provenanceSchema: provenance?.schema ?? null });
    }
    this.stats.quarantineClearanceReceiptProvenanceAccepted += 1;
    const registrationProvenance = Object.freeze({
      schema: CLEARANCE_RECEIPT_REGISTRATION_PROVENANCE_SCHEMA,
      source: provenanceValidation.source,
      lane: provenanceValidation.lane,
      receiptFingerprint: provenanceValidation.receiptFingerprint,
      preClearanceFingerprint: provenanceValidation.preClearanceFingerprint,
      reviewFingerprint: provenance?.reviewFingerprint == null ? null : String(provenance.reviewFingerprint),
      refDigest: provenance?.refDigest == null ? null : String(provenance.refDigest),
      blockVerifyDigest: provenance?.blockVerifyDigest == null ? null : String(provenance.blockVerifyDigest),
      blockVerifyBytes: Number.isFinite(Number(provenance?.blockVerifyBytes)) ? Number(provenance.blockVerifyBytes) : null,
      blockVerified: provenance?.blockVerified === true,
      unsafeUnverifiedRestore: provenance?.unsafeUnverifiedRestore === true,
      bytes: Number.isFinite(Number(provenance?.bytes)) ? Number(provenance.bytes) : null,
      adapterLabel: provenance?.adapterLabel == null ? null : String(provenance.adapterLabel),
      store: provenance?.store == null ? null : String(provenance.store),
      provider: provenance?.provider == null ? null : String(provenance.provider)
    });
    const preClearanceFingerprint = String(receipt.preClearanceFingerprint);
    const receiptFingerprint = String(receipt.receiptFingerprint);
    const reviewFingerprint = String(receipt.reviewFingerprint);
    const reviewToken = String(receipt.reviewToken).trim();
    const row = Object.freeze({
      schema: CLEARANCE_RECEIPT_SCHEMA,
      lane: validation.receiptLane,
      allowLaneWide: validation.allowLaneWide === true,
      preClearanceFingerprint,
      postClearanceFingerprint: receipt.postClearanceFingerprint == null ? null : String(receipt.postClearanceFingerprint),
      reviewFingerprint,
      reviewToken,
      receiptFingerprint,
      clearedCount: Number.isFinite(Number(receipt.clearedCount ?? receipt.counts?.total)) ? Number(receipt.clearedCount ?? receipt.counts?.total) : null,
      successfulClearedCount: Number.isFinite(Number(receipt.successfulClearedCount ?? receipt.counts?.successful)) ? Number(receipt.successfulClearedCount ?? receipt.counts?.successful) : null,
      failedClearedCount: Number.isFinite(Number(receipt.failedClearedCount ?? receipt.counts?.failed)) ? Number(receipt.failedClearedCount ?? receipt.counts?.failed) : null,
      clearedRowKeys: validation.clearedRowKeys,
      clearedOperationKeys: validation.clearedOperationKeys,
      clearedLegacyOperationKeys: validation.clearedLegacyOperationKeys,
      clearedReplayKeys: validation.clearedReplayKeys,
      createdAtMs: Number.isFinite(Number(receipt.createdAtMs)) ? Number(receipt.createdAtMs) : null,
      registeredAtMs: Date.now(),
      registrationProvenance,
      registrationSource: registrationProvenance.source,
      reason: String(reason)
    });
    this.#clearedQuarantineReceipts.set(row.receiptFingerprint, row);
    this.stats.quarantineClearanceReceiptsRegistered += 1;
    const result = Object.freeze({ ok: true, disposition: 'timed-out-quarantine-clearance-receipt-registered', lane: row.lane, preClearanceFingerprint: row.preClearanceFingerprint, postClearanceFingerprint: row.postClearanceFingerprint, reviewFingerprint: row.reviewFingerprint, receiptFingerprint: row.receiptFingerprint, clearedCount: row.clearedCount, allowLaneWide: row.allowLaneWide === true, clearedRowKeys: row.clearedRowKeys, clearedOperationKeys: row.clearedOperationKeys, clearedLegacyOperationKeys: row.clearedLegacyOperationKeys, clearedReplayKeys: row.clearedReplayKeys, registrationProvenance: row.registrationProvenance, registrationSource: row.registrationSource, reason: row.reason });
    this.#emit('storage-lane:timed-out-quarantine-clearance-receipt-registered', result);
    return result;
  }
  clearedTimedOutOperationQuarantineClearanceReceipts(lane = null) {
    const laneFilter = lane == null ? null : String(lane);
    return Object.freeze([...this.#clearedQuarantineReceipts.values()].filter((row) => laneFilter == null || row.lane === laneFilter).map((row) => Object.freeze({ ...row }))); 
  }
  #findClearanceReceiptForQuarantineFingerprint(quarantineFingerprint, imported = null, affectedLanes = new Set()) {
    const fingerprint = quarantineFingerprint == null ? '' : String(quarantineFingerprint);
    if (!fingerprint) return null;
    const laneSet = affectedLanes instanceof Set ? affectedLanes : new Set(affectedLanes || []);
    const candidates = importedTimedOutReplayCandidates(imported);
    if (candidates.length === 0) return null;
    for (const row of this.#clearedQuarantineReceipts.values()) {
      if (row.preClearanceFingerprint !== fingerprint) continue;
      if (laneSet.size > 0 && (row.lane == null || !laneSet.has(row.lane))) continue;
      const matches = candidates.map((candidate) => clearanceReceiptReplayMatches(row, candidate));
      if (matches.every(Boolean)) return Object.freeze({ ...row, matchedRows: Object.freeze(matches) });
    }
    return null;
  }
  #findClearanceReceiptForImportedRows(imported, affectedLanes = new Set()) {
    const laneSet = affectedLanes instanceof Set ? affectedLanes : new Set(affectedLanes || []);
    const candidates = importedTimedOutReplayCandidates(imported);
    if (candidates.length === 0) return null;
    for (const receipt of this.#clearedQuarantineReceipts.values()) {
      if (laneSet.size > 0 && (receipt.lane == null || !laneSet.has(receipt.lane))) continue;
      const matches = candidates.flatMap((candidate) => {
        const match = clearanceReceiptReplayMatches(receipt, candidate);
        return match ? [match] : [];
      });
      if (matches.length > 0) return Object.freeze({ receipt, matches: Object.freeze(matches) });
    }
    return null;
  }
  importTimedOutOperationQuarantine(ledger, { lane = null, reason = 'operator-import-timed-out-operation-quarantine', markUnhealthy = true, allowPartialImport = false, allowEmptyImport = false } = {}) {
    const laneFilter = lane == null ? null : String(lane);
    try {
      const validated = this.#validateTimedOutQuarantineLedger(ledger, { laneFilter });
      const imported = validated.imported;
      const affectedLanes = new Set(validated.affectedLanes);
      const importedCount = imported.unsettled.length + imported.successful.length + imported.failed.length;
      const rawTotal = Number(validated.rawTotal ?? validated.expectedTotal ?? importedCount);
      const filteredOutCount = Number(validated.filteredOutCount ?? 0);
      const hasLaneFilter = laneFilter != null;
      if (hasLaneFilter && rawTotal > 0 && importedCount === 0 && allowEmptyImport !== true) {
        this.stats.quarantineLedgerImportRejected += 1;
        this.stats.quarantineLedgerLaneFilterRejected += 1;
        this.stats.quarantineLedgerEmptyLaneFilterRejected += 1;
        const result = Object.freeze({ ok: false, reason: String(reason), code: 'timed-out-quarantine-import-rejected-lane-filter-empty', disposition: 'rejected-lane-filter-empty-import', schema: ledger.schema, lane: laneFilter, importedCount: 0, rawTotal, filteredOutCount, allowPartialImport: allowPartialImport === true, allowEmptyImport: allowEmptyImport === true, filteredOutLanes: Object.freeze([...(validated.filteredOutLanes || [])]), quarantineFingerprint: validated.quarantineFingerprint, quarantine: this.timedOutOperationQuarantine(laneFilter) });
        this.#emit('storage-lane:timed-out-quarantine-import-lane-filter-rejected', result);
        return result;
      }
      if (hasLaneFilter && filteredOutCount > 0 && allowPartialImport !== true) {
        this.stats.quarantineLedgerImportRejected += 1;
        this.stats.quarantineLedgerLaneFilterRejected += 1;
        this.stats.quarantineLedgerPartialImportRejected += 1;
        const result = Object.freeze({ ok: false, reason: String(reason), code: 'timed-out-quarantine-import-rejected-lane-filter-partial', disposition: 'rejected-lane-filter-partial-import', schema: ledger.schema, lane: laneFilter, importedCount, rawTotal, filteredOutCount, allowPartialImport: false, allowEmptyImport: allowEmptyImport === true, affectedLanes: Object.freeze([...affectedLanes]), filteredOutLanes: Object.freeze([...(validated.filteredOutLanes || [])]), quarantineFingerprint: validated.quarantineFingerprint, quarantine: this.timedOutOperationQuarantine(laneFilter) });
        this.#emit('storage-lane:timed-out-quarantine-import-lane-filter-rejected', result);
        return result;
      }
      if (hasLaneFilter && filteredOutCount > 0 && allowPartialImport === true) {
        this.stats.quarantineLedgerPartialImportAllowed += 1;
        this.stats.quarantineLedgerPartialImports += 1;
        this.#emit('storage-lane:timed-out-quarantine-import-partial-allowed', { lane: laneFilter, reason: String(reason), importedCount, rawTotal, filteredOutCount, affectedLanes: Object.freeze([...affectedLanes]), filteredOutLanes: Object.freeze([...(validated.filteredOutLanes || [])]), quarantineFingerprint: validated.quarantineFingerprint });
      }
      const clearanceReceipt = importedCount > 0 ? this.#findClearanceReceiptForQuarantineFingerprint(validated.quarantineFingerprint, imported, affectedLanes) : null;
      if (clearanceReceipt) {
        this.stats.quarantineLedgerImportRejected += 1;
        this.stats.quarantineLedgerReplayRejected += 1;
        const result = Object.freeze({ ok: false, reason: String(reason), code: 'timed-out-quarantine-import-rejected-cleared', disposition: 'rejected-cleared-quarantine-replay', schema: ledger.schema, lane: laneFilter, importedCount: 0, quarantineFingerprint: validated.quarantineFingerprint, receiptFingerprint: clearanceReceipt.receiptFingerprint, reviewFingerprint: clearanceReceipt.reviewFingerprint, clearedAtMs: clearanceReceipt.createdAtMs, registeredAtMs: clearanceReceipt.registeredAtMs, affectedLanes: Object.freeze([...affectedLanes]), matchedRows: clearanceReceipt.matchedRows || Object.freeze([]), quarantine: this.timedOutOperationQuarantine(laneFilter) });
        this.#emit('storage-lane:timed-out-quarantine-import-replay-rejected', result);
        return result;
      }
      const rowReplay = importedCount > 0 ? this.#findClearanceReceiptForImportedRows(imported, affectedLanes) : null;
      if (rowReplay) {
        this.stats.quarantineLedgerImportRejected += 1;
        this.stats.quarantineLedgerReplayRejected += 1;
        this.stats.quarantineLedgerRowReplayRejected += 1;
        const hasLegacyDowngrade = rowReplay.matches.some((match) => match.replayKind === 'cleared-operation-identity-downgrade');
        if (hasLegacyDowngrade) this.stats.quarantineLedgerLegacyRowReplayRejected += 1;
        const result = Object.freeze({ ok: false, reason: String(reason), code: hasLegacyDowngrade ? 'timed-out-quarantine-import-rejected-cleared-row-downgrade' : 'timed-out-quarantine-import-rejected-cleared-row', disposition: hasLegacyDowngrade ? 'rejected-cleared-quarantine-row-replay-downgrade' : 'rejected-cleared-quarantine-row-replay', schema: ledger.schema, lane: laneFilter, importedCount: 0, quarantineFingerprint: validated.quarantineFingerprint, receiptFingerprint: rowReplay.receipt.receiptFingerprint, reviewFingerprint: rowReplay.receipt.reviewFingerprint, clearedAtMs: rowReplay.receipt.createdAtMs, registeredAtMs: rowReplay.receipt.registeredAtMs, affectedLanes: Object.freeze([...affectedLanes]), matchedRows: rowReplay.matches, quarantine: this.timedOutOperationQuarantine(laneFilter) });
        this.#emit('storage-lane:timed-out-quarantine-import-row-replay-rejected', result);
        return result;
      }
      const removeExistingTimedOutRow = (operationKey, legacyOpId, targetStatus) => {
        let replacementCount = 0;
        const deleteKeys = new Set([operationKey, legacyOpId].filter((key) => key != null && String(key)));
        const buckets = Object.freeze([
          ['unsettled', this.#unsettledTimedOutOps],
          ['successful', this.#successfulTimedOutOps],
          ['failed', this.#failedTimedOutOps]
        ]);
        for (const [status, existingMap] of buckets) {
          for (const key of deleteKeys) {
            if (!existingMap.has(key)) continue;
            const existing = existingMap.get(key);
            existingMap.delete(key);
            if (status !== targetStatus || key !== operationKey) {
              replacementCount += 1;
              this.#emit('storage-lane:timed-out-quarantine-import-status-transition-replaced', {
                operationReplayKey: operationKey,
                opId: legacyOpId,
                fromStatus: status,
                toStatus: targetStatus,
                replacedKey: key,
                existingLane: existing?.lane ?? null,
                existingOperationReplayKey: existing?.operationReplayKey ?? null
              });
            }
          }
        }
        return replacementCount;
      };
      const installRows = (rows, map, targetStatus) => {
        let replacementCount = 0;
        for (const normalized of rows) {
          const operationKey = timedOutOperationMapKey(normalized);
          replacementCount += removeExistingTimedOutRow(operationKey, normalized.opId, targetStatus);
          map.set(operationKey, normalized);
        }
        return replacementCount;
      };
      const statusTransitionReplacementCount =
        installRows(imported.unsettled, this.#unsettledTimedOutOps, 'unsettled') +
        installRows(imported.successful, this.#successfulTimedOutOps, 'successful') +
        installRows(imported.failed, this.#failedTimedOutOps, 'failed');
      if (statusTransitionReplacementCount > 0) this.stats.quarantineLedgerStatusTransitionReplacements += statusTransitionReplacementCount;
      this.stats.unsettledTimedOutOperations = this.#unsettledTimedOutOps.size;
      this.stats.successfulTimedOutOperations = this.#successfulTimedOutOps.size;
      this.stats.failedTimedOutOperations = this.#failedTimedOutOps.size;
      this.stats.quarantineLedgerImports += 1;
      this.stats.importedUnsettledTimedOutOperations += imported.unsettled.length;
      this.stats.importedSuccessfulTimedOutOperations += imported.successful.length;
      this.stats.importedFailedTimedOutOperations += imported.failed.length;
      const markedUnhealthyLanes = [];
      const markUnhealthyRequested = markUnhealthy !== false;
      const markUnhealthyForced = importedCount > 0 && !markUnhealthyRequested;
      const shouldMarkUnhealthy = markUnhealthyRequested || markUnhealthyForced;
      if (shouldMarkUnhealthy) {
        for (const affectedLane of affectedLanes) {
          const row = this.scheduler.markLaneUnhealthy(affectedLane, 'timed-out-operation-quarantine-imported');
          markedUnhealthyLanes.push(Object.freeze({ lane: affectedLane, healthy: row.healthy, healthReason: row.healthReason, queuedCount: row.queuedCount, inFlightCount: row.inFlightCount }));
        }
      }
      if (markUnhealthyForced) {
        this.stats.quarantineLedgerImportBackpressureForced += affectedLanes.size;
        this.#emit('storage-lane:timed-out-quarantine-import-backpressure-forced', { lane: laneFilter, reason: String(reason), importedCount, affectedLanes: Object.freeze([...affectedLanes]), quarantineFingerprint: validated.quarantineFingerprint });
      }
      const result = Object.freeze({ ok: true, schema: ledger.schema, lane: laneFilter, reason: String(reason), disposition: 'timed-out-quarantine-imported', importedCount, rawTotal, filteredOutCount, allowPartialImport: allowPartialImport === true, allowEmptyImport: allowEmptyImport === true, unsettledCount: imported.unsettled.length, successfulCount: imported.successful.length, failedCount: imported.failed.length, statusTransitionReplacementCount, quarantineFingerprint: validated.quarantineFingerprint, reviewFingerprint: validated.quarantineFingerprint, markUnhealthyRequested, markUnhealthyForced, affectedLanes: Object.freeze([...affectedLanes]), filteredOutLanes: Object.freeze([...(validated.filteredOutLanes || [])]), markedUnhealthyLanes: Object.freeze(markedUnhealthyLanes) });
      this.#emit('storage-lane:timed-out-quarantine-import', result);
      return result;
    } catch (error) {
      this.stats.quarantineLedgerImportRejected += 1;
      this.stats.quarantineLedgerImportIntegrityRejected += 1;
      if (/fingerprint/.test(String(error?.message || error))) this.stats.quarantineLedgerFingerprintRejected += 1;
      const result = Object.freeze({ ok: false, reason: String(reason), code: 'timed-out-quarantine-import-rejected', disposition: 'rejected-ledger-integrity', error: describeError(error), importedCount: 0, quarantine: this.timedOutOperationQuarantine(laneFilter) });
      this.#emit('storage-lane:timed-out-quarantine-import-rejected', result);
      return result;
    }
  }
  timedOutOperationQuarantine(lane = null) {
    const laneFilter = lane == null ? null : String(lane);
    const unsettled = this.unsettledTimedOutOperations(laneFilter);
    const successful = this.successfulTimedOutOperations(laneFilter);
    const failed = this.failedTimedOutOperations(laneFilter);
    const totalCount = unsettled.length + successful.length + failed.length;
    this.stats.timedOutOperationQuarantineQueries += 1;
    const fingerprint = timedOutQuarantineFingerprint({ lane: laneFilter, unsettledTimedOutOperations: unsettled, successfulTimedOutOperations: successful, failedTimedOutOperations: failed });
    return Object.freeze({
      schema: 'brt.storageLane.timedOutOperationQuarantine.v1',
      quarantineFingerprint: fingerprint,
      reviewFingerprint: fingerprint,
      lane: laneFilter,
      ok: totalCount === 0,
      totalCount,
      unsettledCount: unsettled.length,
      successfulCount: successful.length,
      failedCount: failed.length,
      unsettledTimedOutOperationCount: unsettled.length,
      successfulTimedOutOperationCount: successful.length,
      failedTimedOutOperationCount: failed.length,
      requiresReview: successful.length > 0 || failed.length > 0,
      requiresSettlement: unsettled.length > 0,
      unsettledTimedOutOperations: unsettled,
      successfulTimedOutOperations: successful,
      failedTimedOutOperations: failed,
      categories: Object.freeze({ unsettled, successful, failed }),
      opIds: Object.freeze({
        unsettled: Object.freeze(unsettled.map((row) => row.opId)),
        successful: Object.freeze(successful.map((row) => row.opId)),
        failed: Object.freeze(failed.map((row) => row.opId))
      }),
      blockedReasons: Object.freeze([
        ...(unsettled.length > 0 ? ['timed-out-operation-still-unsettled'] : []),
        ...(successful.length > 0 ? ['timed-out-operation-late-success'] : []),
        ...(failed.length > 0 ? ['timed-out-operation-late-failure'] : [])
      ])
    });
  }
  timedOutOperationQuarantineCount(lane = null) {
    return this.timedOutOperationQuarantine(lane).totalCount;
  }
  createTimedOutOperationQuarantineReview({ lane = null, reviewer = 'operator', reason = 'operator-reviewed-timed-out-operation-quarantine', opId = null, opIds = null, operationReplayKey = null, operationReplayKeys = null, categories = null, category = 'all', allowLaneWide = false, all = false, allowAll = false, reviewToken = null } = {}) {
    const laneFilter = lane == null ? null : String(lane);
    const quarantine = this.timedOutOperationQuarantine(laneFilter);
    const reviewFingerprint = quarantine.reviewFingerprint || quarantine.quarantineFingerprint;
    const selectedOpIds = opIds ? [...opIds].map(String) : (opId == null ? [] : [String(opId)]);
    const selectedOperationReplayKeys = operationReplayKeys ? [...operationReplayKeys].map(String) : (operationReplayKey == null ? [] : [String(operationReplayKey)]);
    const cats = categories ? [...categories].map(String) : [String(category || 'all')];
    const token = String(reviewToken || `review:${reviewFingerprint}:${Date.now()}`);
    const manifest = Object.freeze({
      schema: 'brt.storageLane.timedOutOperationQuarantine.review.v1',
      createdAtMs: Date.now(),
      reviewer: String(reviewer),
      reason: String(reason),
      reviewToken: token,
      quarantineFingerprint: reviewFingerprint,
      reviewFingerprint,
      lane: laneFilter,
      category: String(category || 'all'),
      categories: Object.freeze(cats),
      opIds: Object.freeze(selectedOpIds),
      operationReplayKeys: Object.freeze(selectedOperationReplayKeys),
      allowLaneWide: Boolean(allowLaneWide),
      all: Boolean(all || allowAll),
      counts: Object.freeze({ total: quarantine.totalCount, unsettled: quarantine.unsettledTimedOutOperationCount, successful: quarantine.successfulTimedOutOperationCount, failed: quarantine.failedTimedOutOperationCount })
    });
    this.stats.timedOutOperationReviewManifests += 1;
    this.#emit('storage-lane:timed-out-quarantine-review-created', { lane: laneFilter, reviewFingerprint, reviewToken: token, totalCount: quarantine.totalCount, categories: cats, opIds: selectedOpIds, operationReplayKeys: selectedOperationReplayKeys, allowLaneWide: manifest.allowLaneWide, all: manifest.all });
    return manifest;
  }
  clearTimedOutOperationQuarantine(options = {}) {
    const opts = options && typeof options === 'object' ? options : {};
    const { category = 'all', categories = null, lane = null, opId = null, opIds = null, operationReplayKey = null, operationReplayKeys = null, reason = 'operator-acknowledged-timed-out-operation-quarantine', reviewed = false, reviewToken = null, reviewFingerprint = null, requireReviewFingerprint = false, reviewManifest = null, allowLaneWide = false, all = false, allowAll = false } = opts;
    const hasOwnOption = (key) => Object.prototype.hasOwnProperty.call(opts, key);
    const manifest = reviewManifest && typeof reviewManifest === 'object' ? reviewManifest : null;
    const manifestLane = manifest?.lane == null ? null : String(manifest.lane);
    const laneFilter = lane == null ? manifestLane : String(lane);
    const normalizeCategory = (value) => {
      const v = value == null ? 'all' : String(value).toLowerCase();
      if (['success', 'successful', 'late-success', 'late_provider_success'].includes(v)) return 'successful';
      if (['failure', 'failed', 'late-failure', 'late_provider_failure'].includes(v)) return 'failed';
      if (['all', 'both', 'settled', 'quarantine', 'timed-out-quarantine'].includes(v)) return 'all';
      return v;
    };
    const requestedCategories = new Set();
    const addCategory = (value) => {
      const c = normalizeCategory(value);
      if (c === 'all') { requestedCategories.add('successful'); requestedCategories.add('failed'); }
      else requestedCategories.add(c);
    };
    const manifestOverrideKeys = manifest ? ['category', 'categories', 'opId', 'opIds', 'operationReplayKey', 'operationReplayKeys', 'allowLaneWide', 'all', 'allowAll', 'reviewFingerprint', 'reviewToken'].filter(hasOwnOption) : [];
    const categoryInputs = manifest ? (Array.isArray(manifest.categories) ? manifest.categories : [manifest.category ?? 'all']) : (Array.isArray(categories) ? categories : [category ?? 'all']);
    for (const c of categoryInputs) addCategory(c);
    const unsupported = [...requestedCategories].filter((c) => c !== 'successful' && c !== 'failed');
    const singleOpId = manifest ? null : (opId == null ? null : String(opId));
    const opIdSet = new Set();
    if (singleOpId != null) opIdSet.add(singleOpId);
    const scopedIds = manifest ? (Array.isArray(manifest.opIds) ? manifest.opIds : []) : (Array.isArray(opIds) ? opIds : []);
    for (const id of scopedIds) if (id != null) opIdSet.add(String(id));
    const hasScopedIds = opIdSet.size > 0;
    const operationReplayKeySet = new Set();
    if (!manifest && operationReplayKey != null) operationReplayKeySet.add(String(operationReplayKey));
    const scopedReplayKeys = manifest ? (Array.isArray(manifest.operationReplayKeys) ? manifest.operationReplayKeys : []) : (Array.isArray(operationReplayKeys) ? operationReplayKeys : []);
    for (const key of scopedReplayKeys) if (key != null) operationReplayKeySet.add(String(key));
    const hasScopedOperationReplayKeys = operationReplayKeySet.size > 0;
    const laneWide = manifest ? (manifest.allowLaneWide === true || manifest.all === true || manifest.allowAll === true) : (allowLaneWide === true || all === true || allowAll === true);
    const token = (manifest?.reviewToken ?? reviewToken ?? '') == null ? '' : String(manifest?.reviewToken ?? reviewToken ?? '').trim();
    const currentQuarantine = this.timedOutOperationQuarantine(laneFilter);
    const currentFingerprint = currentQuarantine.reviewFingerprint;
    const effectiveReviewFingerprint = manifest?.reviewFingerprint ?? manifest?.quarantineFingerprint ?? reviewFingerprint ?? null;
    const reject = (code, disposition) => {
      this.stats.timedOutOperationClearRejected += 1;
      this.stats.timedOutOperationQuarantineClearRejected += 1;
      if (String(code).includes('fingerprint')) this.stats.timedOutOperationReviewFingerprintRejected += 1;
      if (String(code).includes('review-scope') || String(code).includes('review-category') || String(code).includes('review-lane') || String(code).includes('review-manifest') || String(code).includes('review-token') || String(code).includes('opid-ambiguous')) this.stats.timedOutOperationReviewScopeRejected += 1;
      if (String(code).includes('opid-ambiguous')) this.stats.timedOutOperationReviewOpIdAmbiguousRejected += 1;
      const quarantine = this.timedOutOperationQuarantine(laneFilter);
      const result = Object.freeze({ ok: false, code, disposition, category: category == null ? null : String(category), categories: Object.freeze([...requestedCategories]), lane: laneFilter, opId: singleOpId, opIds: Object.freeze([...opIdSet]), operationReplayKey: operationReplayKey == null ? null : String(operationReplayKey), operationReplayKeys: Object.freeze([...operationReplayKeySet]), reason, reviewed: reviewed === true || Boolean(manifest), reviewToken: token || null, reviewFingerprint: effectiveReviewFingerprint == null ? null : String(effectiveReviewFingerprint), requiredReviewFingerprint: currentFingerprint, allowLaneWide: laneWide, clearedCount: 0, successfulClearedCount: 0, failedClearedCount: 0, quarantine });
      this.#emit('storage-lane:timed-out-quarantine-clear-rejected', result);
      return result;
    };
    if (unsupported.length > 0) return reject('timed-out-quarantine-clear-category-unsupported', 'rejected-category-unsupported');
    if (manifest) {
      if (manifest.schema !== 'brt.storageLane.timedOutOperationQuarantine.review.v1') { this.stats.timedOutOperationReviewManifestRejected += 1; return reject('timed-out-quarantine-clear-review-manifest-schema-unsupported', 'rejected-review-manifest-schema'); }
      if (manifestOverrideKeys.length > 0) { this.stats.timedOutOperationReviewManifestRejected += 1; this.stats.timedOutOperationReviewScopeRejected += 1; return reject('timed-out-quarantine-clear-review-manifest-scope-override', 'rejected-review-manifest-scope-override'); }
      if (manifestLane != null && laneFilter != null && manifestLane !== laneFilter) { this.stats.timedOutOperationReviewManifestRejected += 1; return reject('timed-out-quarantine-clear-review-lane-mismatch', 'rejected-review-scope-mismatch'); }
      if (!manifest.counts || typeof manifest.counts !== 'object') { this.stats.timedOutOperationReviewManifestRejected += 1; this.stats.timedOutOperationReviewCountRejected += 1; return reject('timed-out-quarantine-clear-review-manifest-counts-required', 'rejected-review-manifest-counts'); }
      const manifestCountChecks = [['total', currentQuarantine.totalCount], ['unsettled', currentQuarantine.unsettledTimedOutOperationCount], ['successful', currentQuarantine.successfulTimedOutOperationCount], ['failed', currentQuarantine.failedTimedOutOperationCount]];
      for (const [key, expected] of manifestCountChecks) if (Number(manifest.counts[key]) !== expected) { this.stats.timedOutOperationReviewManifestRejected += 1; this.stats.timedOutOperationReviewCountRejected += 1; return reject('timed-out-quarantine-clear-review-manifest-count-mismatch', 'rejected-review-manifest-counts'); }
      const manifestCategories = new Set();
      const manifestCategoryInput = Array.isArray(manifest.categories) ? manifest.categories : [manifest.category ?? 'all'];
      for (const c of manifestCategoryInput) {
        const normalized = normalizeCategory(c);
        if (normalized === 'all') { manifestCategories.add('successful'); manifestCategories.add('failed'); }
        else manifestCategories.add(normalized);
      }
      const badCategory = [...requestedCategories].find((c) => !manifestCategories.has(c));
      if (badCategory) return reject('timed-out-quarantine-clear-review-category-mismatch', 'rejected-review-scope-mismatch');
      const manifestLaneWide = manifest.allowLaneWide === true || manifest.all === true || manifest.allowAll === true;
      const manifestOpIds = new Set(Array.isArray(manifest.opIds) ? manifest.opIds.filter((id) => id != null).map(String) : []);
      const manifestOperationReplayKeys = new Set(Array.isArray(manifest.operationReplayKeys) ? manifest.operationReplayKeys.filter((key) => key != null).map(String) : []);
      if (!manifestLaneWide) {
        if (manifestOpIds.size === 0 && manifestOperationReplayKeys.size === 0) return reject('timed-out-quarantine-clear-review-scope-mismatch', 'rejected-review-scope-mismatch');
        for (const id of opIdSet) {
          if (!manifestOpIds.has(id)) return reject('timed-out-quarantine-clear-review-scope-mismatch', 'rejected-review-scope-mismatch');
        }
        for (const key of operationReplayKeySet) {
          if (!manifestOperationReplayKeys.has(key)) return reject('timed-out-quarantine-clear-review-scope-mismatch', 'rejected-review-scope-mismatch');
        }
      }
    }
    if (reviewed !== true && !manifest) return reject('timed-out-quarantine-clear-review-required', 'rejected-review-required');
    if (!token) return reject('timed-out-quarantine-clear-review-token-required', 'rejected-review-token-required');
    if ((requireReviewFingerprint || manifest) && !effectiveReviewFingerprint) return reject('timed-out-quarantine-clear-review-fingerprint-required', 'rejected-review-fingerprint-required');
    if (effectiveReviewFingerprint && String(effectiveReviewFingerprint) !== currentFingerprint) return reject('timed-out-quarantine-clear-review-fingerprint-mismatch', 'rejected-review-fingerprint-mismatch');
    if (!hasScopedIds && !hasScopedOperationReplayKeys && !laneWide) return reject('timed-out-quarantine-clear-scope-required', 'rejected-scope-required');
    if (hasScopedOperationReplayKeys) this.stats.timedOutOperationReviewReplayKeyScopes += 1;
    if (hasScopedIds && !hasScopedOperationReplayKeys && !laneWide) {
      const candidateRows = [
        ...(requestedCategories.has('successful') ? this.successfulTimedOutOperations(laneFilter) : []),
        ...(requestedCategories.has('failed') ? this.failedTimedOutOperations(laneFilter) : [])
      ];
      const ambiguous = ambiguousOpIdScopes(candidateRows, opIdSet, { lane: laneFilter });
      if (ambiguous.length > 0) return reject('timed-out-quarantine-clear-opid-ambiguous', 'rejected-ambiguous-opid-scope');
    }
    const matches = (row) => {
      if (laneFilter != null && row.lane !== laneFilter) return false;
      if (hasScopedIds && !opIdSet.has(row.opId)) return false;
      if (hasScopedOperationReplayKeys && !operationReplayKeySet.has(rowOperationReplayKey(row))) return false;
      return true;
    };
    const clearedSuccessful = [];
    const clearedFailed = [];
    if (requestedCategories.has('successful')) {
      for (const [key, row] of [...this.#successfulTimedOutOps.entries()]) {
        if (!matches(row)) continue;
        this.#successfulTimedOutOps.delete(key);
        clearedSuccessful.push(Object.freeze({ ...row }));
      }
    }
    if (requestedCategories.has('failed')) {
      for (const [key, row] of [...this.#failedTimedOutOps.entries()]) {
        if (!matches(row)) continue;
        this.#failedTimedOutOps.delete(key);
        clearedFailed.push(Object.freeze({ ...row }));
      }
    }
    if (clearedSuccessful.length + clearedFailed.length === 0) return reject('timed-out-quarantine-clear-noop', 'rejected-noop-clear');
    this.stats.successfulTimedOutOperations = this.#successfulTimedOutOps.size;
    this.stats.failedTimedOutOperations = this.#failedTimedOutOps.size;
    this.stats.successfulTimedOutOperationsCleared += clearedSuccessful.length;
    this.stats.failedTimedOutOperationsCleared += clearedFailed.length;
    this.stats.timedOutOperationQuarantineCleared += clearedSuccessful.length + clearedFailed.length;
    this.stats.reviewedTimedOutOperationQuarantine += clearedSuccessful.length + clearedFailed.length;
    this.stats.reviewedLateProviderSuccesses += clearedSuccessful.length;
    this.stats.reviewedLateProviderFailures += clearedFailed.length;
    const quarantine = this.timedOutOperationQuarantine(laneFilter);
    const result = Object.freeze({ ok: true, category: category == null ? null : String(category), categories: Object.freeze([...requestedCategories]), lane: laneFilter, opId: singleOpId, opIds: Object.freeze([...opIdSet]), operationReplayKey: operationReplayKey == null ? null : String(operationReplayKey), operationReplayKeys: Object.freeze([...operationReplayKeySet]), reason, reviewed: true, reviewToken: token, reviewFingerprint: effectiveReviewFingerprint ?? currentFingerprint, requiredReviewFingerprint: currentFingerprint, allowLaneWide: laneWide, clearedCount: clearedSuccessful.length + clearedFailed.length, successfulClearedCount: clearedSuccessful.length, failedClearedCount: clearedFailed.length, cleared: Object.freeze({ successful: Object.freeze(clearedSuccessful), failed: Object.freeze(clearedFailed) }), quarantine });
    this.#emit('storage-lane:timed-out-quarantine-cleared', result);
    return result;
  }
  finalizeUnsettledTimedOutOperations(options = {}) {
    const opts = options && typeof options === 'object' ? options : {};
    const { lane = null, opId = null, opIds = null, operationReplayKey = null, operationReplayKeys = null, reason = 'operator-classified-unsettled-timed-out-operation', reviewed = false, reviewToken = null, reviewFingerprint = null, requireReviewFingerprint = true, reviewManifest = null, allowLaneWide = false, all = false, allowAll = false, errorCode = 'BRT_STORAGE_TIMED_OUT_OPERATION_ORPHANED', message = 'timed-out provider operation was orphaned and explicitly classified by maintenance review' } = opts;
    const hasOwnOption = (key) => Object.prototype.hasOwnProperty.call(opts, key);
    const manifest = reviewManifest && typeof reviewManifest === 'object' ? reviewManifest : null;
    const manifestLane = manifest?.lane == null ? null : String(manifest.lane);
    const laneFilter = lane == null ? manifestLane : String(lane);
    const normalizeCategory = (value) => {
      const v = value == null ? 'unsettled' : String(value).toLowerCase();
      if (['unsettled', 'pending', 'orphan', 'orphaned', 'timed-out-unsettled'].includes(v)) return 'unsettled';
      if (['all', 'quarantine', 'timed-out-quarantine'].includes(v)) return 'unsettled';
      return v;
    };
    const manifestOverrideKeys = manifest ? ['opId', 'opIds', 'operationReplayKey', 'operationReplayKeys', 'allowLaneWide', 'all', 'allowAll', 'reviewFingerprint', 'reviewToken'].filter(hasOwnOption) : [];
    const categoryInputs = manifest ? (Array.isArray(manifest.categories) ? manifest.categories : [manifest.category ?? 'unsettled']) : ['unsettled'];
    const requestedCategories = new Set(categoryInputs.map(normalizeCategory));
    const unsupported = [...requestedCategories].filter((category) => category !== 'unsettled');
    const singleOpId = manifest ? null : (opId == null ? null : String(opId));
    const opIdSet = new Set();
    if (singleOpId != null) opIdSet.add(singleOpId);
    const scopedIds = manifest ? (Array.isArray(manifest.opIds) ? manifest.opIds : []) : (Array.isArray(opIds) ? opIds : []);
    for (const id of scopedIds) if (id != null) opIdSet.add(String(id));
    const hasScopedIds = opIdSet.size > 0;
    const operationReplayKeySet = new Set();
    if (!manifest && operationReplayKey != null) operationReplayKeySet.add(String(operationReplayKey));
    const scopedReplayKeys = manifest ? (Array.isArray(manifest.operationReplayKeys) ? manifest.operationReplayKeys : []) : (Array.isArray(operationReplayKeys) ? operationReplayKeys : []);
    for (const key of scopedReplayKeys) if (key != null) operationReplayKeySet.add(String(key));
    const hasScopedOperationReplayKeys = operationReplayKeySet.size > 0;
    const laneWide = manifest ? (manifest.allowLaneWide === true || manifest.all === true || manifest.allowAll === true) : (allowLaneWide === true || all === true || allowAll === true);
    const reviewedFinalize = reviewed === true || Boolean(manifest);
    const token = (manifest?.reviewToken ?? reviewToken ?? '') == null ? '' : String(manifest?.reviewToken ?? reviewToken ?? '').trim();
    const currentQuarantine = this.timedOutOperationQuarantine(laneFilter);
    const currentFingerprint = currentQuarantine.reviewFingerprint;
    const effectiveReviewFingerprint = manifest?.reviewFingerprint ?? manifest?.quarantineFingerprint ?? reviewFingerprint ?? null;
    const reject = (code, disposition) => {
      this.stats.timedOutOperationFinalizeRejected += 1;
      this.stats.timedOutOperationClearRejected += 1;
      if (String(code).includes('fingerprint')) this.stats.timedOutOperationReviewFingerprintRejected += 1;
      if (String(code).includes('review-scope') || String(code).includes('review-lane') || String(code).includes('review-manifest') || String(code).includes('review-token')) this.stats.timedOutOperationReviewScopeRejected += 1;
      const quarantine = this.timedOutOperationQuarantine(laneFilter);
      const result = Object.freeze({ ok: false, code, disposition, lane: laneFilter, opId: singleOpId, opIds: Object.freeze([...opIdSet]), operationReplayKey: operationReplayKey == null ? null : String(operationReplayKey), operationReplayKeys: Object.freeze([...operationReplayKeySet]), reason, reviewed: reviewedFinalize, reviewToken: token || null, reviewFingerprint: effectiveReviewFingerprint == null ? null : String(effectiveReviewFingerprint), requiredReviewFingerprint: currentFingerprint, requireReviewFingerprint: requireReviewFingerprint !== false || Boolean(manifest), allowLaneWide: laneWide, finalizedCount: 0, unsettledTimedOutOperationCount: this.unsettledTimedOutOperationCount(laneFilter), quarantine });
      this.#emit('storage-lane:timed-out-quarantine-finalize-rejected', result);
      return result;
    };
    if (unsupported.length > 0) return reject('timed-out-quarantine-finalize-category-unsupported', 'rejected-category-unsupported');
    if (manifest) {
      if (manifest.schema !== 'brt.storageLane.timedOutOperationQuarantine.review.v1') { this.stats.timedOutOperationReviewManifestRejected += 1; return reject('timed-out-quarantine-finalize-review-manifest-schema-unsupported', 'rejected-review-manifest-schema'); }
      if (manifestOverrideKeys.length > 0) { this.stats.timedOutOperationReviewManifestRejected += 1; this.stats.timedOutOperationReviewScopeRejected += 1; return reject('timed-out-quarantine-finalize-review-manifest-scope-override', 'rejected-review-manifest-scope-override'); }
      if (manifestLane != null && laneFilter != null && manifestLane !== laneFilter) { this.stats.timedOutOperationReviewManifestRejected += 1; return reject('timed-out-quarantine-finalize-review-lane-mismatch', 'rejected-review-scope-mismatch'); }
      if (!manifest.counts || typeof manifest.counts !== 'object') { this.stats.timedOutOperationReviewManifestRejected += 1; this.stats.timedOutOperationReviewCountRejected += 1; return reject('timed-out-quarantine-finalize-review-manifest-counts-required', 'rejected-review-manifest-counts'); }
      const manifestCountChecks = [['total', currentQuarantine.totalCount], ['unsettled', currentQuarantine.unsettledTimedOutOperationCount], ['successful', currentQuarantine.successfulTimedOutOperationCount], ['failed', currentQuarantine.failedTimedOutOperationCount]];
      for (const [key, expected] of manifestCountChecks) {
        if (Number(manifest.counts[key]) !== expected) { this.stats.timedOutOperationReviewManifestRejected += 1; this.stats.timedOutOperationReviewCountRejected += 1; return reject('timed-out-quarantine-finalize-review-manifest-count-mismatch', 'rejected-review-manifest-counts'); }
      }
      const manifestCategories = new Set();
      const manifestCategoryInputs = Array.isArray(manifest.categories) ? manifest.categories : [manifest.category ?? 'unsettled'];
      for (const c of manifestCategoryInputs) manifestCategories.add(normalizeCategory(c));
      const badCategory = [...manifestCategories].find((c) => c !== 'unsettled');
      if (badCategory) return reject('timed-out-quarantine-finalize-review-category-mismatch', 'rejected-review-scope-mismatch');
      const manifestLaneWide = manifest.allowLaneWide === true || manifest.all === true || manifest.allowAll === true;
      const manifestOpIds = new Set(Array.isArray(manifest.opIds) ? manifest.opIds.filter((id) => id != null).map(String) : []);
      const manifestOperationReplayKeys = new Set(Array.isArray(manifest.operationReplayKeys) ? manifest.operationReplayKeys.filter((key) => key != null).map(String) : []);
      if (!manifestLaneWide) {
        if (manifestOpIds.size === 0 && manifestOperationReplayKeys.size === 0) return reject('timed-out-quarantine-finalize-review-scope-mismatch', 'rejected-review-scope-mismatch');
        for (const id of opIdSet) {
          if (!manifestOpIds.has(id)) return reject('timed-out-quarantine-finalize-review-scope-mismatch', 'rejected-review-scope-mismatch');
        }
        for (const key of operationReplayKeySet) {
          if (!manifestOperationReplayKeys.has(key)) return reject('timed-out-quarantine-finalize-review-scope-mismatch', 'rejected-review-scope-mismatch');
        }
      }
    }
    if (!reviewedFinalize) return reject('timed-out-quarantine-finalize-review-required', 'rejected-review-required');
    if (!token) return reject('timed-out-quarantine-finalize-review-token-required', 'rejected-review-token-required');
    if (!hasScopedIds && !hasScopedOperationReplayKeys && !laneWide) return reject('timed-out-quarantine-finalize-scope-required', 'rejected-scope-required');
    if (hasScopedIds && !hasScopedOperationReplayKeys && !laneWide) {
      const ambiguous = ambiguousOpIdScopes(this.unsettledTimedOutOperations(laneFilter), opIdSet, { lane: laneFilter });
      if (ambiguous.length > 0) return reject('timed-out-quarantine-finalize-opid-ambiguous', 'rejected-ambiguous-opid-scope');
    }
    if ((requireReviewFingerprint !== false || manifest) && !effectiveReviewFingerprint) return reject('timed-out-quarantine-finalize-review-fingerprint-required', 'rejected-review-fingerprint-required');
    if (effectiveReviewFingerprint && String(effectiveReviewFingerprint) !== currentFingerprint) return reject('timed-out-quarantine-finalize-review-fingerprint-mismatch', 'rejected-review-fingerprint-mismatch');
    if (hasScopedOperationReplayKeys) this.stats.timedOutOperationReviewReplayKeyScopes += 1;
    const finalized = [];
    for (const [key, row] of [...this.#unsettledTimedOutOps.entries()]) {
      if (laneFilter != null && row.lane !== laneFilter) continue;
      if (hasScopedIds && !opIdSet.has(row.opId)) continue;
      if (hasScopedOperationReplayKeys && !operationReplayKeySet.has(rowOperationReplayKey(row))) continue;
      this.#unsettledTimedOutOps.delete(key);
      const error = Object.freeze({
        name: 'BrowserRTStorageLaneError',
        message: String(message),
        code: String(errorCode || 'BRT_STORAGE_TIMED_OUT_OPERATION_ORPHANED'),
        storageDisposition: String(errorCode || 'BRT_STORAGE_TIMED_OUT_OPERATION_ORPHANED'),
        providerDetail: Object.freeze({ reason: String(reason), reviewToken: token, reviewFingerprint: effectiveReviewFingerprint ?? currentFingerprint, orphaned: true })
      });
      const failed = Object.freeze({ ...row, settledAtMs: Date.now(), finalizedAtMs: Date.now(), finalized: true, finalization: 'reviewed-orphaned-unsettled-timeout', error });
      this.#failedTimedOutOps.set(key, failed);
      finalized.push(failed);
    }
    this.stats.unsettledTimedOutOperations = this.#unsettledTimedOutOps.size;
    this.stats.failedTimedOutOperations = this.#failedTimedOutOps.size;
    this.stats.unsettledTimedOutOperationsFinalized += finalized.length;
    this.stats.reviewedUnsettledTimedOutOperations += finalized.length;
    const quarantine = this.timedOutOperationQuarantine(laneFilter);
    const result = Object.freeze({ ok: true, lane: laneFilter, opId: singleOpId, opIds: Object.freeze([...opIdSet]), operationReplayKey: operationReplayKey == null ? null : String(operationReplayKey), operationReplayKeys: Object.freeze([...operationReplayKeySet]), reason, reviewed: true, reviewToken: token, reviewFingerprint: effectiveReviewFingerprint ?? currentFingerprint, requiredReviewFingerprint: currentFingerprint, requireReviewFingerprint: requireReviewFingerprint !== false || Boolean(manifest), allowLaneWide: laneWide, finalizedCount: finalized.length, failedTimedOutOperationCount: this.#failedTimedOutOps.size, unsettledTimedOutOperationCount: this.#unsettledTimedOutOps.size, finalized: Object.freeze(finalized), quarantine });
    this.#emit('storage-lane:timed-out-quarantine-orphans-finalized', result);
    return result;
  }
  clearSuccessfulTimedOutOperations({ lane = null, opId = null, opIds = null, operationReplayKey = null, operationReplayKeys = null, reason = 'operator-acknowledged-late-provider-success', reviewed = false, reviewToken = null, reviewFingerprint = null, requireReviewFingerprint = true, reviewManifest = null, allowLaneWide = false, all = false, allowAll = false } = {}) {
    const manifest = reviewManifest && typeof reviewManifest === 'object' ? reviewManifest : null;
    const laneFilter = lane == null ? (manifest?.lane == null ? null : String(manifest.lane)) : String(lane);
    const opIdFilter = opId == null ? null : String(opId);
    const opIdSet = new Set();
    if (opIdFilter != null) opIdSet.add(opIdFilter);
    const scopedIds = Array.isArray(opIds) ? opIds : (Array.isArray(manifest?.opIds) ? manifest.opIds : []);
    for (const id of scopedIds) if (id != null) opIdSet.add(String(id));
    const operationReplayKeySet = new Set();
    if (operationReplayKey != null) operationReplayKeySet.add(String(operationReplayKey));
    const scopedReplayKeys = Array.isArray(operationReplayKeys) ? operationReplayKeys : (Array.isArray(manifest?.operationReplayKeys) ? manifest.operationReplayKeys : []);
    for (const key of scopedReplayKeys) if (key != null) operationReplayKeySet.add(String(key));
    const reviewedClear = reviewed === true || Boolean(manifest);
    const laneWide = allowLaneWide === true || all === true || allowAll === true || manifest?.allowLaneWide === true || manifest?.all === true;
    const token = (reviewToken ?? manifest?.reviewToken ?? '') == null ? '' : String(reviewToken ?? manifest?.reviewToken ?? '').trim();
    const currentFingerprint = this.timedOutOperationQuarantine(laneFilter).reviewFingerprint;
    const effectiveReviewFingerprint = reviewFingerprint ?? manifest?.reviewFingerprint ?? manifest?.quarantineFingerprint ?? null;
    const reject = (code, disposition) => {
      this.stats.timedOutOperationClearRejected += 1;
      this.stats.lateProviderSuccessClearRejected += 1;
      if (String(code).includes('fingerprint')) this.stats.timedOutOperationReviewFingerprintRejected += 1;
      if (String(code).includes('opid-ambiguous')) { this.stats.timedOutOperationReviewScopeRejected += 1; this.stats.timedOutOperationReviewOpIdAmbiguousRejected += 1; }
      const result = Object.freeze({ ok: false, lane: laneFilter, opId: opIdFilter, opIds: Object.freeze([...opIdSet]), operationReplayKey: operationReplayKey == null ? null : String(operationReplayKey), operationReplayKeys: Object.freeze([...operationReplayKeySet]), reason, reviewed: reviewedClear, reviewToken: token || null, reviewFingerprint: effectiveReviewFingerprint == null ? null : String(effectiveReviewFingerprint), requiredReviewFingerprint: currentFingerprint, requireReviewFingerprint: requireReviewFingerprint !== false || Boolean(manifest), allowLaneWide: laneWide, code, disposition, clearedCount: 0, successfulTimedOutOperationCount: this.#successfulTimedOutOps.size, cleared: Object.freeze([]) });
      this.#emit('storage-lane:late-provider-success-clear-rejected', result);
      this.#emit('storage-lane:late-provider-successes-clear-rejected', result);
      return result;
    };
    if (!reviewedClear) return reject('late-success-clear-review-required', 'rejected-review-required');
    if (!token) return reject('late-success-clear-review-token-required', 'rejected-review-token-required');
    if (opIdSet.size === 0 && operationReplayKeySet.size === 0 && !laneWide) return reject('late-success-clear-scope-required', 'rejected-scope-required');
    if (opIdSet.size > 0 && operationReplayKeySet.size === 0 && !laneWide) {
      const ambiguous = ambiguousOpIdScopes(this.successfulTimedOutOperations(laneFilter), opIdSet, { lane: laneFilter });
      if (ambiguous.length > 0) return reject('late-success-clear-opid-ambiguous', 'rejected-ambiguous-opid-scope');
    }
    if ((requireReviewFingerprint !== false || manifest) && !effectiveReviewFingerprint) return reject('late-success-clear-review-fingerprint-required', 'rejected-review-fingerprint-required');
    if (effectiveReviewFingerprint && String(effectiveReviewFingerprint) !== currentFingerprint) return reject('late-success-clear-review-fingerprint-mismatch', 'rejected-review-fingerprint-mismatch');
    const cleared = [];
    for (const [key, row] of [...this.#successfulTimedOutOps.entries()]) {
      if (laneFilter != null && row.lane !== laneFilter) continue;
      if (opIdSet.size > 0 && !opIdSet.has(row.opId)) continue;
      if (operationReplayKeySet.size > 0 && !operationReplayKeySet.has(rowOperationReplayKey(row))) continue;
      this.#successfulTimedOutOps.delete(key);
      cleared.push(Object.freeze({ ...row }));
    }
    this.stats.successfulTimedOutOperations = this.#successfulTimedOutOps.size;
    this.stats.successfulTimedOutOperationsCleared += cleared.length;
    this.stats.reviewedLateProviderSuccesses += cleared.length;
    const result = Object.freeze({ ok: true, lane: laneFilter, opId: opIdFilter, opIds: Object.freeze([...opIdSet]), operationReplayKey: operationReplayKey == null ? null : String(operationReplayKey), operationReplayKeys: Object.freeze([...operationReplayKeySet]), reason, reviewed: true, reviewToken: token, reviewFingerprint: effectiveReviewFingerprint ?? currentFingerprint, requiredReviewFingerprint: currentFingerprint, requireReviewFingerprint: requireReviewFingerprint !== false || Boolean(manifest), allowLaneWide: laneWide, clearedCount: cleared.length, successfulTimedOutOperationCount: this.#successfulTimedOutOps.size, cleared: Object.freeze(cleared), quarantine: this.timedOutOperationQuarantine(laneFilter) });
    this.#emit('storage-lane:late-provider-successes-cleared', result);
    return result;
  }
  clearFailedTimedOutOperations({ lane = null, opId = null, opIds = null, operationReplayKey = null, operationReplayKeys = null, reason = 'operator-acknowledged-late-provider-failure', reviewed = false, reviewToken = null, reviewFingerprint = null, requireReviewFingerprint = true, reviewManifest = null, allowLaneWide = false, all = false, allowAll = false } = {}) {
    const manifest = reviewManifest && typeof reviewManifest === 'object' ? reviewManifest : null;
    const laneFilter = lane == null ? (manifest?.lane == null ? null : String(manifest.lane)) : String(lane);
    const opIdFilter = opId == null ? null : String(opId);
    const opIdSet = new Set();
    if (opIdFilter != null) opIdSet.add(opIdFilter);
    const scopedIds = Array.isArray(opIds) ? opIds : (Array.isArray(manifest?.opIds) ? manifest.opIds : []);
    for (const id of scopedIds) if (id != null) opIdSet.add(String(id));
    const operationReplayKeySet = new Set();
    if (operationReplayKey != null) operationReplayKeySet.add(String(operationReplayKey));
    const scopedReplayKeys = Array.isArray(operationReplayKeys) ? operationReplayKeys : (Array.isArray(manifest?.operationReplayKeys) ? manifest.operationReplayKeys : []);
    for (const key of scopedReplayKeys) if (key != null) operationReplayKeySet.add(String(key));
    const reviewedClear = reviewed === true || Boolean(manifest);
    const laneWide = allowLaneWide === true || all === true || allowAll === true || manifest?.allowLaneWide === true || manifest?.all === true;
    const token = (reviewToken ?? manifest?.reviewToken ?? '') == null ? '' : String(reviewToken ?? manifest?.reviewToken ?? '').trim();
    const currentFingerprint = this.timedOutOperationQuarantine(laneFilter).reviewFingerprint;
    const effectiveReviewFingerprint = reviewFingerprint ?? manifest?.reviewFingerprint ?? manifest?.quarantineFingerprint ?? null;
    const reject = (code, disposition) => {
      this.stats.timedOutOperationClearRejected += 1;
      this.stats.lateProviderFailureClearRejected += 1;
      if (String(code).includes('fingerprint')) this.stats.timedOutOperationReviewFingerprintRejected += 1;
      if (String(code).includes('opid-ambiguous')) { this.stats.timedOutOperationReviewScopeRejected += 1; this.stats.timedOutOperationReviewOpIdAmbiguousRejected += 1; }
      const result = Object.freeze({ ok: false, lane: laneFilter, opId: opIdFilter, opIds: Object.freeze([...opIdSet]), operationReplayKey: operationReplayKey == null ? null : String(operationReplayKey), operationReplayKeys: Object.freeze([...operationReplayKeySet]), reason, reviewed: reviewedClear, reviewToken: token || null, reviewFingerprint: effectiveReviewFingerprint == null ? null : String(effectiveReviewFingerprint), requiredReviewFingerprint: currentFingerprint, requireReviewFingerprint: requireReviewFingerprint !== false || Boolean(manifest), allowLaneWide: laneWide, code, disposition, clearedCount: 0, failedTimedOutOperationCount: this.#failedTimedOutOps.size, cleared: Object.freeze([]) });
      this.#emit('storage-lane:late-provider-failure-clear-rejected', result);
      this.#emit('storage-lane:late-provider-failures-clear-rejected', result);
      return result;
    };
    if (!reviewedClear) return reject('late-failure-clear-review-required', 'rejected-review-required');
    if (!token) return reject('late-failure-clear-review-token-required', 'rejected-review-token-required');
    if (opIdSet.size === 0 && operationReplayKeySet.size === 0 && !laneWide) return reject('late-failure-clear-scope-required', 'rejected-scope-required');
    if (opIdSet.size > 0 && operationReplayKeySet.size === 0 && !laneWide) {
      const ambiguous = ambiguousOpIdScopes(this.failedTimedOutOperations(laneFilter), opIdSet, { lane: laneFilter });
      if (ambiguous.length > 0) return reject('late-failure-clear-opid-ambiguous', 'rejected-ambiguous-opid-scope');
    }
    if ((requireReviewFingerprint !== false || manifest) && !effectiveReviewFingerprint) return reject('late-failure-clear-review-fingerprint-required', 'rejected-review-fingerprint-required');
    if (effectiveReviewFingerprint && String(effectiveReviewFingerprint) !== currentFingerprint) return reject('late-failure-clear-review-fingerprint-mismatch', 'rejected-review-fingerprint-mismatch');
    const cleared = [];
    for (const [key, row] of [...this.#failedTimedOutOps.entries()]) {
      if (laneFilter != null && row.lane !== laneFilter) continue;
      if (opIdSet.size > 0 && !opIdSet.has(row.opId)) continue;
      if (operationReplayKeySet.size > 0 && !operationReplayKeySet.has(rowOperationReplayKey(row))) continue;
      this.#failedTimedOutOps.delete(key);
      cleared.push(Object.freeze({ ...row }));
    }
    this.stats.failedTimedOutOperations = this.#failedTimedOutOps.size;
    this.stats.failedTimedOutOperationsCleared += cleared.length;
    this.stats.reviewedLateProviderFailures += cleared.length;
    const result = Object.freeze({ ok: true, lane: laneFilter, opId: opIdFilter, opIds: Object.freeze([...opIdSet]), operationReplayKey: operationReplayKey == null ? null : String(operationReplayKey), operationReplayKeys: Object.freeze([...operationReplayKeySet]), reason, reviewed: true, reviewToken: token, reviewFingerprint: effectiveReviewFingerprint ?? currentFingerprint, requiredReviewFingerprint: currentFingerprint, requireReviewFingerprint: requireReviewFingerprint !== false || Boolean(manifest), allowLaneWide: laneWide, clearedCount: cleared.length, failedTimedOutOperationCount: this.#failedTimedOutOps.size, cleared: Object.freeze(cleared), quarantine: this.timedOutOperationQuarantine(laneFilter) });
    this.#emit('storage-lane:late-provider-failures-cleared', result);
    return result;
  }
  async waitForTimedOutOperationsSettled({ lane = null, timeoutMs = 1000, intervalMs = 25 } = {}) {
    const normalizedTimeoutMs = normalizeOperationTimeoutMs(timeoutMs);
    const normalizedIntervalMs = Math.max(1, normalizeOperationTimeoutMs(intervalMs));
    const started = Date.now();
    let operations = this.unsettledTimedOutOperations(lane);
    while (operations.length > 0 && Date.now() - started < normalizedTimeoutMs) {
      await new Promise((resolve) => setTimeout(resolve, normalizedIntervalMs));
      operations = this.unsettledTimedOutOperations(lane);
    }
    const elapsedMs = Date.now() - started;
    return Object.freeze({ ok: operations.length === 0, lane: lane == null ? null : String(lane), count: operations.length, operations, elapsedMs, timeoutMs: normalizedTimeoutMs, reason: operations.length === 0 ? 'timed-out-operations-settled' : 'timed-out-operation-still-unsettled' });
  }
  async #runDispatched(dispatch) {
    this.stats.dispatched += 1;
    const task = dispatch.task; const op = this.#ops.get(task.id);
    this.#emit('storage-lane:dispatch', { opId: task.id, kind: op?.kind || task.payload?.kind || 'unknown', lane: dispatch.lane, priority: task.priority, cost: task.cost });
    if (!op) { this.stats.failed += 1; this.scheduler.complete(task.id, { outcome: 'storage-lane:missing-op' }); return Object.freeze({ dispatched: true, ok: false, opId: task.id, lane: dispatch.lane, error: 'missing-operation' }); }
    try {
      const timeoutMs = normalizeOperationTimeoutMs(op.operationTimeoutMs);
      if (timeoutMs > 0) this.#emit('storage-lane:operation-timeout-arm', { opId: op.opId, kind: op.kind, lane: dispatch.lane, timeoutMs });
      const result = await runWithOperationTimeout(op.run, {
        timeoutMs,
        detail: { opId: op.opId, kind: op.kind, lane: dispatch.lane, executor: this.label },
        abortProviderOnTimeout: op.abortProviderOnOperationTimeout === true,
        onTimeout: (timeoutInfo = {}) => {
          this.stats.operationTimeouts += 1;
          if (timeoutInfo.providerAbortSignaled) this.stats.providerTimeoutAborts += 1;
          this.#rememberTimedOutOperation({ opId: op.opId, kind: op.kind, lane: dispatch.lane, timeoutMs, operationEpoch: op.operationEpoch, operationReplayKey: op.operationReplayKey });
          this.#emit('storage-lane:operation-timeout', { opId: op.opId, kind: op.kind, lane: dispatch.lane, timeoutMs, cancellation: timeoutInfo.providerAbortSignaled === true, abortProviderOnOperationTimeout: op.abortProviderOnOperationTimeout === true });
        },
        onLateSettlement: (settlement) => this.#settleTimedOutOperation(op.opId, { ...settlement, operationReplayKey: op.operationReplayKey })
      });
      if (String(result?.disposition || '').startsWith('rejected-provider')) { const err = new Error(`provider rejected ${op.kind}: ${result.reason}`); err.name = 'BrowserRTStorageLaneProviderError'; err.code = result.reason || 'BRT_STORAGE_PROVIDER_REJECTED'; throw err; }
      this.#results.set(op.opId, result); this.#ops.delete(op.opId); this.scheduler.complete(task.id, { outcome: `storage-lane:${op.kind}:complete`, metadata: summarizeResult(result) });
      this.stats.completed += 1; this.#emit('storage-lane:complete', { opId: op.opId, kind: op.kind, lane: dispatch.lane, result: summarizeResult(result) });
      return Object.freeze({ dispatched: true, ok: true, opId: op.opId, taskId: op.opId, op: op.kind, lane: dispatch.lane, result });
    } catch (error) {
      const detail = describeError(error);
      this.#ops.delete(op.opId); this.stats.failed += 1;
      if (this.markUnhealthyOnError && isStorageHealthFailure(detail)) { this.scheduler.markLaneUnhealthy(dispatch.lane, detail.code || detail.storageDisposition); this.stats.laneHealthFailures += 1; this.#emit('storage-lane:provider-unhealthy', { opId: op.opId, lane: dispatch.lane, code: detail.code, storageDisposition: detail.storageDisposition }); }
      this.scheduler.complete(task.id, { outcome: `storage-lane:${op.kind}:error`, metadata: detail });
      this.#emit('storage-lane:error', { opId: op.opId, kind: op.kind, lane: dispatch.lane, error: detail });
      return Object.freeze({ dispatched: true, ok: false, opId: op.opId, taskId: op.opId, op: op.kind, lane: dispatch.lane, error: detail });
    }
  }
  markHealthy(lane = this.lane, reason = 'manual-recovery', { allowWithTimedOutQuarantine = false, reviewToken = null } = {}) {
    const quarantine = this.timedOutOperationQuarantine(lane);
    if (!allowWithTimedOutQuarantine && quarantine.totalCount > 0) {
      this.stats.markHealthyQuarantineRejected += 1;
      const result = Object.freeze({ healthy: false, lane: String(lane), reason: 'timed-out-operation-quarantine-active', disposition: 'rejected-timed-out-operation-quarantine', requestedReason: String(reason), reviewToken: reviewToken == null ? null : String(reviewToken), quarantine });
      this.#emit('storage-lane:provider-healthy-rejected', { lane: String(lane), reason: result.reason, requestedReason: result.requestedReason, quarantineCount: quarantine.totalCount, unsettledTimedOutOperationCount: quarantine.unsettledTimedOutOperationCount, successfulTimedOutOperationCount: quarantine.successfulTimedOutOperationCount, failedTimedOutOperationCount: quarantine.failedTimedOutOperationCount });
      return result;
    }
    const row = this.scheduler.markLaneHealthy(lane, reason);
    this.#emit('storage-lane:provider-healthy', { lane, reason, queuedCount: row.queuedCount, inFlightCount: row.inFlightCount });
    return row;
  }
  markUnhealthy(lane = this.lane, reason = 'manual-unhealthy') { const row = this.scheduler.markLaneUnhealthy(lane, reason); this.#emit('storage-lane:provider-unhealthy', { lane, reason, queuedCount: row.queuedCount, inFlightCount: row.inFlightCount }); return row; }
  result(opId) { return this.#results.get(String(opId)); }
  resultMap() { return new Map(this.#results); }
  snapshot() { const scheduler = this.scheduler.snapshot(); const quarantine = this.timedOutOperationQuarantine(); return Object.freeze({ label: this.label, operationEpoch: this.#operationEpoch, defaultOperationTimeoutMs: this.defaultOperationTimeoutMs, abortProviderOnOperationTimeout: this.abortProviderOnOperationTimeout, pendingOperationCount: this.#ops.size, resultCount: this.#results.size, timedOutOperationQuarantineCount: quarantine.totalCount, timedOutOperationQuarantine: quarantine, clearedQuarantineReceiptCount: this.#clearedQuarantineReceipts.size, clearedQuarantineReceipts: this.clearedTimedOutOperationQuarantineClearanceReceipts(), unsettledTimedOutOperationCount: this.#unsettledTimedOutOps.size, unsettledTimedOutOperations: this.unsettledTimedOutOperations(), successfulTimedOutOperationCount: this.#successfulTimedOutOps.size, successfulTimedOutOperations: this.successfulTimedOutOperations(), failedTimedOutOperationCount: this.#failedTimedOutOps.size, failedTimedOutOperations: this.failedTimedOutOperations(), stats: { ...this.stats }, schedulerValidation: validateCrossLaneSchedulerSnapshot(scheduler), scheduler, mailbox: this.mailbox?.snapshot?.() ?? null }); }
}
export function validateStorageLaneExecutorSnapshot(snapshot, { requireMailbox = true } = {}) {
  const errors = [];
  const isObj = (value) => value && typeof value === 'object';
  if (!isObj(snapshot)) {
    return Object.freeze({ ok: false, errors: ['snapshot must be an object'], pendingOperationCount: 0, resultCount: 0, unsettledTimedOutOperationCount: 0, failedTimedOutOperationCount: 0, queuedCount: 0, inFlightCount: 0, mailboxQueueDepth: 0, mailboxPendingCount: 0 });
  }
  const nonNeg = (name, value) => { if (!Number.isInteger(value) || value < 0) errors.push(`${name} must be a non-negative integer`); };
  nonNeg('pendingOperationCount', snapshot.pendingOperationCount);
  nonNeg('resultCount', snapshot.resultCount);
  if (snapshot.unsettledTimedOutOperationCount !== undefined) nonNeg('unsettledTimedOutOperationCount', snapshot.unsettledTimedOutOperationCount);
  if (snapshot.successfulTimedOutOperationCount !== undefined) nonNeg('successfulTimedOutOperationCount', snapshot.successfulTimedOutOperationCount);
  if (snapshot.failedTimedOutOperationCount !== undefined) nonNeg('failedTimedOutOperationCount', snapshot.failedTimedOutOperationCount);
  if (snapshot.timedOutOperationQuarantineCount !== undefined) nonNeg('timedOutOperationQuarantineCount', snapshot.timedOutOperationQuarantineCount);
  if (Array.isArray(snapshot.unsettledTimedOutOperations) && snapshot.unsettledTimedOutOperationCount !== undefined && snapshot.unsettledTimedOutOperations.length !== snapshot.unsettledTimedOutOperationCount) errors.push('unsettledTimedOutOperations length must match unsettledTimedOutOperationCount');
  if (Array.isArray(snapshot.successfulTimedOutOperations) && snapshot.successfulTimedOutOperationCount !== undefined && snapshot.successfulTimedOutOperations.length !== snapshot.successfulTimedOutOperationCount) errors.push('successfulTimedOutOperations length must match successfulTimedOutOperationCount');
  if (Array.isArray(snapshot.failedTimedOutOperations) && snapshot.failedTimedOutOperationCount !== undefined && snapshot.failedTimedOutOperations.length !== snapshot.failedTimedOutOperationCount) errors.push('failedTimedOutOperations length must match failedTimedOutOperationCount');
  if (snapshot.timedOutOperationQuarantine && snapshot.timedOutOperationQuarantineCount !== undefined && snapshot.timedOutOperationQuarantine.totalCount !== snapshot.timedOutOperationQuarantineCount) errors.push('timedOutOperationQuarantine.totalCount must match timedOutOperationQuarantineCount');
  if (!isObj(snapshot.stats)) errors.push('stats must be present');
  const scheduler = snapshot.scheduler;
  if (!isObj(scheduler)) errors.push('scheduler snapshot must be present');
  const schedulerValidation = snapshot.schedulerValidation;
  if (!isObj(schedulerValidation) || schedulerValidation.ok !== true) errors.push('schedulerValidation.ok must be true');
  const queuedCount = Number.isInteger(scheduler?.queuedCount) ? scheduler.queuedCount : 0;
  const inFlightCount = Number.isInteger(scheduler?.inFlightCount) ? scheduler.inFlightCount : 0;
  if (scheduler && Array.isArray(scheduler.lanes)) {
    const laneQueued = scheduler.lanes.reduce((sum, lane) => sum + (Number.isInteger(lane.queuedCount) ? lane.queuedCount : 0), 0);
    const laneInFlight = scheduler.lanes.reduce((sum, lane) => sum + (Number.isInteger(lane.inFlightCount) ? lane.inFlightCount : 0), 0);
    if (laneQueued !== queuedCount) errors.push(`scheduler queuedCount mismatch: lanes=${laneQueued} global=${queuedCount}`);
    if (laneInFlight !== inFlightCount) errors.push(`scheduler inFlightCount mismatch: lanes=${laneInFlight} global=${inFlightCount}`);
  } else if (scheduler) errors.push('scheduler.lanes must be an array');
  const mailbox = snapshot.mailbox;
  if (requireMailbox && !isObj(mailbox)) errors.push('mailbox snapshot must be present');
  let mailboxQueueDepth = 0;
  let mailboxPendingCount = 0;
  if (isObj(mailbox)) {
    mailboxQueueDepth = mailbox.queueDepth;
    mailboxPendingCount = mailbox.pendingCount;
    nonNeg('mailbox.queueDepth', mailboxQueueDepth);
    nonNeg('mailbox.pendingCount', mailboxPendingCount);
    if (Array.isArray(mailbox.queueSeqs) && mailbox.queueSeqs.length !== mailboxQueueDepth) errors.push('mailbox queueSeqs length must match queueDepth');
    if (Array.isArray(mailbox.pendingSeqs) && mailbox.pendingSeqs.length !== mailboxPendingCount) errors.push('mailbox pendingSeqs length must match pendingCount');
    if (Number.isInteger(mailbox.retainedBlockCount) && Array.isArray(mailbox.liveBlockDigests) && mailbox.retainedBlockCount < mailbox.liveBlockDigests.length) errors.push('retainedBlockCount must cover liveBlockDigests');
    const provider = mailbox.providerSnapshot;
    if (isObj(provider) && Number.isInteger(provider.blockCount) && provider.blockCount < mailbox.liveBlockDigests?.length) errors.push('provider blockCount must cover liveBlockDigests');
  }
  return Object.freeze({ ok: errors.length === 0, errors, pendingOperationCount: snapshot.pendingOperationCount || 0, resultCount: snapshot.resultCount || 0, unsettledTimedOutOperationCount: snapshot.unsettledTimedOutOperationCount || 0, failedTimedOutOperationCount: snapshot.failedTimedOutOperationCount || 0, queuedCount, inFlightCount, mailboxQueueDepth, mailboxPendingCount });
}
export function createStorageLaneExecutor(config = {}) { return new StorageLaneExecutor(config); }
export const STORAGE_LANE_EXECUTOR_SUPPORTED_OPS = SUPPORTED_OPS;
