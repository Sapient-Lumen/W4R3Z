export const BROWSERRT_PRODUCT_WEDGE_FORMAT = 'browserrt.product-wedge-receipt.v1';
export const BROWSERRT_PUBLIC_API_EXPORTS = Object.freeze([
  'VERSION',
  'REVISION',
  'detectCapabilities',
  'availableCapabilityTierNames',
  'boot',
  'createObjectRef',
  'createTransferObjectRef',
  'createTransferObject',
  'createBlockObjectRef',
  'createEnvelope',
  'digestBytesHex',
  'diagnoseBrowserStoragePosture',
  'createBrowserStorageRecoveryGuidance',
  'BROWSERRT_BROWSER_STORAGE_POSTURE_FORMAT',
  'BROWSERRT_BROWSER_STORAGE_RECOVERY_GUIDANCE_FORMAT',
  'validateBlockStoreLaneAdapterSnapshot',
  'TraceLog',
  'BROWSERRT_PRODUCT_WEDGE_FORMAT',
  'BROWSERRT_PUBLIC_API_EXPORTS',
  'createBrowserRtProductWedgeReceipt',
  'validateBrowserRtProductWedgeReceipt'
]);
const REQUIRED_PROOF = Object.freeze([
  'publicApiImportOnly',
  'runtimeBooted',
  'boundedChannelBackpressure',
  'workerAgentRoundTrip',
  'transferDetached',
  'admissionRejectedWithoutMutation',
  'storageLaneWriteRead',
  'traceReceiptClosed'
]);
function bool(value) { return value === true; }
function proofFromObserved(observed = {}) {
  return Object.freeze({
    publicApiImportOnly: observed.imports?.publicApiOnly === true,
    runtimeBooted: observed.runtime?.revisionMatches === true && observed.runtime?.versionMatches === true,
    boundedChannelBackpressure: observed.channel?.overflowDisposition === 'failed-full' && observed.channel?.receivedCurrentWork === true,
    workerAgentRoundTrip: observed.worker?.pingPong === true && observed.worker?.sum === 36 && observed.worker?.count === 4,
    transferDetached: observed.worker?.transferDetached === true,
    admissionRejectedWithoutMutation: observed.admission?.accepted === true && observed.admission?.rejectedNoMutation === true,
    storageLaneWriteRead: observed.storage?.putAccepted === true && observed.storage?.verifyOk === true && observed.storage?.readDigestMatches === true && observed.storage?.adapterSnapshotValid === true,
    traceReceiptClosed: Array.isArray(observed.trace?.kinds) && observed.trace.kinds.includes('runtime:boot') && observed.trace.kinds.includes('runtime:close')
  });
}
export function createBrowserRtProductWedgeReceipt({ revision, version, observed, traceKinds = [], generatedAt = new Date().toISOString(), source = 'product-wedge-consumer' } = {}) {
  const proof = proofFromObserved(observed);
  const missing = REQUIRED_PROOF.filter((key) => !bool(proof[key]));
  return Object.freeze({
    project: 'BrowserRT',
    revision,
    version,
    schema: 1,
    format: BROWSERRT_PRODUCT_WEDGE_FORMAT,
    source,
    generatedAt,
    status: missing.length === 0 ? 'passed' : 'failed',
    purpose: 'Consumer-facing BrowserRT product wedge: public API import, boot, bounded channel, Worker agent, transferable object ref, admission, storage-lane write/read, and trace receipt.',
    publicApi: Object.freeze({ supportedExports: BROWSERRT_PUBLIC_API_EXPORTS.slice(), exportCount: BROWSERRT_PUBLIC_API_EXPORTS.length }),
    proof,
    missing,
    observed,
    traceKinds: traceKinds.slice(),
    nonClaims: Object.freeze([
      'Public API wedge only; not a full package-compatibility, semver, browser matrix, cross-browser, quota, eviction, fsync, or crash-recovery claim.',
      'The storage provider in this fast wedge is memory-backed; browser OPFS/Web Locks proofs remain separate explicit tests.'
    ])
  });
}
export function validateBrowserRtProductWedgeReceipt(receipt) {
  const errors = [];
  if (!receipt || typeof receipt !== 'object') errors.push('receipt must be an object');
  if (receipt?.project !== 'BrowserRT') errors.push('project must be BrowserRT');
  if (receipt?.format !== BROWSERRT_PRODUCT_WEDGE_FORMAT) errors.push(`format must be ${BROWSERRT_PRODUCT_WEDGE_FORMAT}`);
  if (receipt?.schema !== 1) errors.push('schema must be 1');
  if (!/^rev\d{4}$/.test(String(receipt?.revision || ''))) errors.push('revision must be rev####');
  if (!/^\d+\.\d+\.\d+$/.test(String(receipt?.version || ''))) errors.push('version must be x.y.z');
  const proof = receipt?.proof && typeof receipt.proof === 'object' ? receipt.proof : {};
  for (const key of REQUIRED_PROOF) if (proof[key] !== true) errors.push(`proof.${key} must be true`);
  const exports = receipt?.publicApi?.supportedExports;
  if (!Array.isArray(exports)) errors.push('publicApi.supportedExports must be an array');
  else for (const key of BROWSERRT_PUBLIC_API_EXPORTS) if (!exports.includes(key)) errors.push(`publicApi.supportedExports missing ${key}`);
  if (!Array.isArray(receipt?.nonClaims) || !receipt.nonClaims.some((claim) => /cross-browser/.test(claim))) errors.push('cross-browser non-claim must be visible');
  if (receipt?.status !== (errors.length ? 'failed' : 'passed')) errors.push('status does not match validation result');
  return Object.freeze({ ok: errors.length === 0, errors, requiredProof: REQUIRED_PROOF.slice(), proof });
}
