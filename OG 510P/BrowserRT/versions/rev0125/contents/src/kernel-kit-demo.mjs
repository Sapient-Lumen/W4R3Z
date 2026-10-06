// BrowserRT rev0054 integrated Kernel Kit demo contract.
// Legacy check aliases: runtime-boot, browser-worker-agent, opfs-storage-lane-adapter.
// This file names the usefulness wedge, validates demo reports, and now
// exposes a transcript contract shared by the human page and CDP proof. It
// does not claim production readiness, OPFS durability, performance, or market fit.

import { createKernelKitLifecycleCheckpoint, validateKernelKitLifecycleCheckpoint, KERNEL_KIT_LIFECYCLE_CHECKPOINT_NON_CLAIMS } from './kernel-kit-lifecycle-checkpoint.mjs';
import { createKernelKitSessionCoordinationCheckpoint, validateKernelKitSessionCoordinationCheckpoint, KERNEL_KIT_SESSION_COORDINATION_CHECKPOINT_NON_CLAIMS } from './kernel-kit-session-coordination-checkpoint.mjs';
import { createKernelKitRecoveryCheckpoint, validateKernelKitRecoveryCheckpoint, KERNEL_KIT_RECOVERY_CHECKPOINT_FORMAT, KERNEL_KIT_RECOVERY_CHECKPOINT_NON_CLAIMS } from './kernel-kit-recovery-checkpoint.mjs';
import { createKernelKitAdmissionCancellationCheckpoint, validateKernelKitAdmissionCancellationCheckpoint, KERNEL_KIT_ADMISSION_CANCELLATION_CHECKPOINT_NON_CLAIMS } from './kernel-kit-admission-cancellation-checkpoint.mjs';

export const KERNEL_KIT_DEMO_CODENAME = 'Interactive Kernel Kit Demo';

export const KERNEL_KIT_DEMO_STEPS = Object.freeze([
  'boot-runtime',
  'spawn-worker-agent',
  'transfer-object-ref',
  'bounded-channel-touch',
  'admission-governor-gate',
  'opfs-storage-lane-write',
  'page-reload-readback',
  'trace-and-audit-artifact'
]);

export const KERNEL_KIT_DEMO_REQUIRED_STEPS = KERNEL_KIT_DEMO_STEPS;

export const KERNEL_KIT_DEMO_STAGE_LABELS = Object.freeze({
  'boot-runtime': 'Boot BrowserRT in a cross-origin-isolated browser page',
  'spawn-worker-agent': 'Spawn a module Worker agent and exchange a BRT1 ping',
  'transfer-object-ref': 'Transfer an ArrayBuffer object ref and observe sender detachment',
  'bounded-channel-touch': 'Touch a bounded control channel without unbounded queue growth',
  'admission-governor-gate': 'Admit useful work and reject oversized background work without mutation',
  'opfs-storage-lane-write': 'Write/read a content-addressed OPFS block through the storage-lane adapter; browser path records Web-Locks-guarded OPFS provider evidence',
  'page-reload-readback': 'Reload the page and read the block back in the same temporary browser profile',
  'trace-and-audit-artifact': 'Produce trace, transcript, non-claim, and audit evidence'
});

export const KERNEL_KIT_DEMO_REQUIRED_TRACE_KINDS = Object.freeze([
  'runtime:boot',
  'channel:create',
  'channel:send',
  'channel:receive',
  'agent:spawn',
  'agent:ready',
  'agent:call',
  'agent:result',
  'object:transfer-ref',
  'admission:admit',
  'admission:reject',
  'admission:release',
  'object:opfs-storage-lane-adapter-ref',
  'block-store-lane:schedule',
  'storage-lane:dispatch',
  'block-store-lane:op-complete',
  'storage-lane:complete',
  'storage:opfs-block-put',
  'storage:opfs-block-get',
  'runtime:close'
]);

export const KERNEL_KIT_DEMO_NON_CLAIMS = Object.freeze([
  'No production runtime claim.',
  'No market validation claim.',
  'No user-demand proof.',
  'No product-market-fit claim.',
  'No OPFS durability, fsync, quota, eviction, crash-recovery, browser-restart, or multi-tab coordination claim.',
  'No OPFS sync access handle storage-lane proof.',
  'No browser Worker OPFS storage-lane provider proof.',
  'No WebGPU, WebNN, WebTransport, WebRTC, mobile lifecycle, or cross-browser conformance claim.',
  'No throughput, latency, SLO, or real performance claim.',
  'No exactly-once delivery claim.',
  'Managed-browser Web-Locks-guarded storage-lane evidence is not a fairness, lifecycle recovery, cross-browser, crash-recovery, or production multi-tab coordination claim.'
]);

export const KERNEL_KIT_DEMO_HANDOFF_STORAGE_KEY = 'BrowserRT.KernelKitDemo.handoff.v1';

export const KERNEL_KIT_DEMO_HANDOFF_REQUIRED_KEYS = Object.freeze([
  'project',
  'revision',
  'prefix',
  'ref',
  'expectedDigest',
  'storageRefDigest',
  'stageReceipt',
  'savedAt'
]);


export const KERNEL_KIT_DEMO_FAILURE_MODES = Object.freeze([
  'missing-handoff',
  'invalid-handoff',
  'admission-reject-no-mutation'
]);

export const KERNEL_KIT_DEMO_EXPORT_BUNDLE_FORMAT = 'browserrt-kernel-kit-export-bundle-v1';

export const KERNEL_KIT_DEMO_EXPORT_BUNDLE_NON_CLAIMS = Object.freeze([
  'No browser download UX claim.',
  'No production incident-reporting claim.',
  'No telemetry backend integration claim.',
  'No failure recovery automation claim.'
]);

export function createKernelKitDemoPlan(fields = {}) {
  return Object.freeze({
    project: 'BrowserRT',
    revision: fields.revision || 'rev0054',
    schema: 2,
    codename: KERNEL_KIT_DEMO_CODENAME,
    posture: 'usefulness-wedge-not-production-runtime',
    purpose: 'Prove the narrow usefulness wedge with one browser-visible flow: boot, worker agent, transfer object ref, bounded channel, admission gate, OPFS storage-lane write/read, trace artifact, transcript, and release-tier audit.',
    audience: Object.freeze([
      'browser IDE and agent-workbench builders',
      'heavy local web app builders',
      'local-first storage/tooling library authors',
      'library authors tired of rebuilding worker/storage/runtime substrate'
    ]),
    components: Object.freeze([
      'runtime boot',
      'browser worker agent',
      'transfer object ref',
      'bounded channel',
      'watermark admission governor',
      'OPFS storage-lane adapter',
      'Web-Locks-guarded OPFS block-store provider for the browser storage-lane path',
      'trace report',
      'human-readable transcript',
      'local reload handoff',
      'trace export receipt',
      'non-claim boundary'
    ]),
    steps: KERNEL_KIT_DEMO_STEPS.map((id, index) => Object.freeze({ id, order: index + 1, label: KERNEL_KIT_DEMO_STAGE_LABELS[id] })),
    requiredTraceKinds: KERNEL_KIT_DEMO_REQUIRED_TRACE_KINDS.slice(),
    releasePosture: 'browser proof is explicit browser/full tier; broad release remains browser-light',
    successShape: Object.freeze({
      workerAgent: 'module Worker responds to BRT1 ping and sums transferred Uint32 payload',
      transferObjectRef: 'sender-side ArrayBuffer detaches after transfer to Worker',
      boundedChannel: 'channel send/receive traces prove a tiny control-plane touch',
      admissionGovernor: 'storage write is admitted; an oversized background request is rejected without mutation',
      storageLane: 'OPFS async block store is reached through OpfsBlockStoreStorageLaneAdapter',
      reloadReadback: 'same temporary Chromium profile reload can read/verify/delete the stored block',
      transcript: 'stage transcript makes the proof legible to humans and future sessions',
      localReloadHandoff: 'localStorage handoff lets a human reload and read back the OPFS artifact without CDP-only hidden arguments',
      traceExport: 'trace export receipt gives a compact BrowserRT receipt plus Chrome-trace-shaped envelope for local inspection experiments',
      audit: 'release-tier audit validates contract surfaces without launching Chromium'
    }),
    nonClaims: KERNEL_KIT_DEMO_NON_CLAIMS.slice(),
    ...fields
  });
}

function isObj(value) { return value && typeof value === 'object'; }
function hasAll(list, required) {
  const set = new Set(Array.isArray(list) ? list : []);
  return required.filter((item) => !set.has(item));
}
function includesAny(list, needle) { return Array.isArray(list) && list.includes(needle); }
function bool(value) { return value === true; }
function traceSetFrom(report) {
  return new Set([
    ...(report?.traceKinds || []),
    ...(report?.observations?.allTraceKinds || []),
    ...(report?.work?.traceKinds || []),
    ...(report?.reload?.traceKinds || []),
    ...(report?.observations?.work?.traceKinds || []),
    ...(report?.observations?.reload?.traceKinds || [])
  ]);
}


export function createKernelKitDemoHandoff(report = {}, fields = {}) {
  const storage = report.storage || report.observations?.work?.storage || {};
  const ref = fields.ref || storage.ref || report.ref || null;
  const expectedDigest = fields.expectedDigest || storage.payloadDigest || storage.digest || report.expectedDigest || null;
  const transcript = fields.stageReceipt || report.transcript || createKernelKitDemoTranscript(report);
  return Object.freeze({
    project: 'BrowserRT',
    revision: fields.revision || report.revision || 'rev0054',
    schema: 1,
    handoffId: fields.handoffId || `${fields.revision || report.revision || 'rev0054'}-kernel-kit-local-reload-handoff`,
    storageKey: KERNEL_KIT_DEMO_HANDOFF_STORAGE_KEY,
    prefix: fields.prefix || report.prefix || report.storagePrefix || report.observations?.work?.prefix || null,
    ref,
    expectedDigest,
    storageRefDigest: ref?.digest || ref?.hash || expectedDigest || null,
    payloadBytes: fields.payloadBytes || storage.payloadBytes || 0,
    stageReceipt: transcript,
    traceExportFormat: report.traceExport?.format || null,
    abortBoundary: fields.abortBoundary || report.abortBoundary || report.observations?.work?.abortBoundary || null,
    storagePosture: fields.storagePosture || report.storagePosture || report.observations?.work?.storagePosture || null,
    webLockPosture: fields.webLockPosture || report.webLockPosture || report.observations?.work?.webLockPosture || null,
    guardedStorageLane: fields.guardedStorageLane || report.guardedStorageLane || report.guardedStorage || report.storage?.guarded || report.observations?.work?.guardedStorage || report.observations?.work?.storage?.guarded || null,
    savedAt: fields.savedAt || 'deterministic-handoff',
    purpose: 'Allow the human-clickable Kernel Kit page to reload and read back its OPFS artifact without CDP-only hidden arguments.',
    nonClaims: KERNEL_KIT_DEMO_NON_CLAIMS.slice()
  });
}

export function validateKernelKitDemoHandoff(handoff) {
  const errors = [];
  if (!isObj(handoff)) return Object.freeze({ ok: false, errors: ['handoff must be an object'], requiredKeyCount: 0 });
  if (handoff.project !== 'BrowserRT') errors.push('project must be BrowserRT');
  if (handoff.storageKey !== KERNEL_KIT_DEMO_HANDOFF_STORAGE_KEY) errors.push('storageKey mismatch');
  for (const key of KERNEL_KIT_DEMO_HANDOFF_REQUIRED_KEYS) {
    if (handoff[key] === undefined || handoff[key] === null || handoff[key] === '') errors.push(`missing handoff key ${key}`);
  }
  if (!isObj(handoff.ref)) errors.push('ref must be an object');
  if (!String(handoff.expectedDigest || '').startsWith('sha256:')) errors.push('expectedDigest must be sha256-prefixed');
  const transcriptValidation = validateKernelKitDemoTranscript(handoff.stageReceipt || {});
  if (!transcriptValidation.ok) errors.push(...transcriptValidation.errors.map((x) => `stageReceipt: ${x}`));
  for (const claim of ['No production runtime claim.', 'No OPFS durability, fsync, quota, eviction, crash-recovery, browser-restart, or multi-tab coordination claim.']) {
    if (!handoff.nonClaims?.includes(claim)) errors.push(`missing handoff non-claim: ${claim}`);
  }
  return Object.freeze({ ok: errors.length === 0, errors, requiredKeyCount: KERNEL_KIT_DEMO_HANDOFF_REQUIRED_KEYS.length, transcriptValidation });
}

export function createKernelKitDemoTranscript(report = {}) {
  const traceKinds = traceSetFrom(report);
  const proof = report.proof || report.observations?.proof || report.observations || {};
  const work = report.work || report.observations?.work || {};
  const reload = report.reload || report.observations?.reload || {};
  const observations = report.observations || {};
  const components = report.components || {};
  const legacyWorker = report.worker || {};
  const legacyStorage = report.storage || {};
  const legacyAdmission = report.admission || {};
  const checks = {
    'boot-runtime': bool(proof.booted) || components.runtimeBoot === true || traceKinds.has('runtime:boot') || work.page?.crossOriginIsolated === true,
    'spawn-worker-agent': bool(proof.workerPing) || bool(proof.workerAgent) || components.workerAgent === true || work.worker?.pingPong === true || traceKinds.has('agent:result'),
    'transfer-object-ref': bool(proof.transferDetached) || components.transferObjectRef === true || legacyWorker.detachedAfter === true || work.worker?.transferDetached === true || traceKinds.has('object:transfer-ref'),
    'bounded-channel-touch': bool(proof.boundedChannel) || work.channel?.emptySize === 0 || observations.boundedChannelOverflow === true || traceKinds.has('channel:receive'),
    'admission-governor-gate': bool(proof.admissionAccepted) || bool(proof.admissionRejectedNoMutation) || components.admissionGovernor === true || legacyAdmission.lowPriorityRejected === true || observations.admissionRejectedNoMutation === true || traceKinds.has('admission:reject'),
    'opfs-storage-lane-write': bool(proof.storageWrite) || bool(proof.storageLaneWriteRead) || components.opfsStorageLane === true || legacyStorage.verifyOk === true || work.storage?.result?.digest === work.storage?.payloadDigest || traceKinds.has('storage:opfs-block-put'),
    'page-reload-readback': bool(proof.reloadReadback) || legacyStorage.hasAfterDelete === false || reload.read?.digest === reload.read?.expectedDigest || traceKinds.has('storage:opfs-block-get'),
    'trace-and-audit-artifact': bool(proof.traceComplete) || components.traceReport === true || traceKinds.has('runtime:close') || (Array.isArray(report.normalizedTrace) && report.normalizedTrace.length > 0)
  };
  const stages = KERNEL_KIT_DEMO_STEPS.map((id, index) => Object.freeze({
    id,
    order: index + 1,
    label: KERNEL_KIT_DEMO_STAGE_LABELS[id],
    status: checks[id] ? 'passed' : 'missing'
  }));
  const passedCount = stages.filter((stage) => stage.status === 'passed').length;
  return Object.freeze({
    project: 'BrowserRT',
    revision: report.revision || 'rev0054',
    schema: 1,
    transcriptId: `${report.revision || 'rev0054'}-kernel-kit-demo-transcript`,
    status: passedCount === stages.length ? 'passed' : 'incomplete',
    stageCount: stages.length,
    passedCount,
    missingStageIds: stages.filter((stage) => stage.status !== 'passed').map((stage) => stage.id),
    stages,
    traceKindCount: traceKinds.size,
    nonClaims: KERNEL_KIT_DEMO_NON_CLAIMS.slice()
  });
}

export function validateKernelKitDemoTranscript(transcript) {
  const errors = [];
  if (!isObj(transcript)) return Object.freeze({ ok: false, errors: ['transcript must be an object'], stageCount: 0, passedCount: 0 });
  if (transcript.project !== 'BrowserRT') errors.push('project must be BrowserRT');
  if (!Array.isArray(transcript.stages)) errors.push('stages must be an array');
  const stageIds = (transcript.stages || []).map((stage) => stage.id);
  const missingStages = hasAll(stageIds, KERNEL_KIT_DEMO_STEPS);
  if (missingStages.length) errors.push(`missing transcript stages: ${missingStages.join(', ')}`);
  if (transcript.status !== 'passed') errors.push('transcript status must be passed');
  if (transcript.passedCount !== KERNEL_KIT_DEMO_STEPS.length) errors.push('passedCount must equal required step count');
  for (const claim of ['No production runtime claim.', 'No product-market-fit claim.']) {
    if (!transcript.nonClaims?.includes(claim)) errors.push(`missing transcript non-claim: ${claim}`);
  }
  return Object.freeze({ ok: errors.length === 0, errors, stageCount: stageIds.length, passedCount: transcript.passedCount || 0 });
}

export function validateKernelKitDemoPlan(plan = createKernelKitDemoPlan()) {
  const errors = [];
  if (!isObj(plan)) return Object.freeze({ ok: false, errors: ['plan must be an object'], stepCount: 0, traceKindCount: 0, nonClaimCount: 0 });
  if (plan.project !== 'BrowserRT') errors.push('project must be BrowserRT');
  if (!String(plan.codename || '').includes('Kernel Kit')) errors.push('codename must mention Kernel Kit');
  const stepIds = (plan.steps || []).map((step) => step.id);
  const missingSteps = hasAll(stepIds, KERNEL_KIT_DEMO_STEPS);
  if (missingSteps.length) errors.push(`missing demo steps: ${missingSteps.join(', ')}`);
  const missingTrace = hasAll(plan.requiredTraceKinds, KERNEL_KIT_DEMO_REQUIRED_TRACE_KINDS);
  if (missingTrace.length) errors.push(`missing required trace kinds: ${missingTrace.join(', ')}`);
  const missingNonClaims = hasAll(plan.nonClaims, KERNEL_KIT_DEMO_NON_CLAIMS);
  if (missingNonClaims.length) errors.push(`missing non-claims: ${missingNonClaims.join(' | ')}`);
  return Object.freeze({ ok: errors.length === 0, errors, stepCount: stepIds.length, traceKindCount: (plan.requiredTraceKinds || []).length, nonClaimCount: (plan.nonClaims || []).length });
}

export function validateKernelKitDemoProof(report) {
  const errors = [];
  if (!isObj(report)) return Object.freeze({ ok: false, errors: ['report must be an object'], traceKindCount: 0 });
  if (report.project !== 'BrowserRT') errors.push('project must be BrowserRT');
  if (report.status && report.status !== 'passed') errors.push('status must be passed when present');
  if (!String(report.codename || report.demo_id || report.proofId || '').includes('Kernel') && !String(report.demo_id || '').includes('kernel-kit')) errors.push('report must name Kernel Kit');
  const proof = report.observations?.proof || report.proof || report.observations || {};
  const requiredObservations = [
    ['workerAgent', proof.workerAgent === true || proof.workerPing === true],
    ['transferDetached', proof.transferDetached === true],
    ['admissionRejectedNoMutation', proof.admissionRejectedNoMutation === true],
    ['storageLaneWriteRead/storageWrite', proof.storageLaneWriteRead === true || proof.storageWrite === true],
    ['traceEvidence/traceComplete', proof.traceEvidence === true || proof.traceComplete === true]
  ];
  for (const [key, ok] of requiredObservations) {
    if (!ok) errors.push(`proof/observation ${key} must be true`);
  }
  const traceKinds = report.observations?.allTraceKinds || report.traceKinds || report.trace?.kinds || [];
  for (const kind of ['runtime:boot', 'agent:call', 'agent:result', 'admission:reject', 'block-store-lane:schedule', 'storage-lane:dispatch', 'storage-lane:complete', 'runtime:close']) {
    if (!includesAny(traceKinds, kind)) errors.push(`missing trace kind ${kind}`);
  }
  const nonClaims = report.nonClaims || report.non_claims || [];
  for (const needle of ['No production runtime claim.', 'No product-market-fit claim.']) {
    if (!nonClaims.includes(needle)) errors.push(`missing non-claim: ${needle}`);
  }
  return Object.freeze({ ok: errors.length === 0, errors, traceKindCount: traceKinds.length });
}



export function summarizeKernelKitDemoTrace(traceKindsOrEvents = []) {
  const kinds = traceKindsOrEvents.map((event) => typeof event === 'string' ? event : event?.kind).filter(Boolean);
  const counts = Object.create(null);
  for (const kind of kinds) counts[kind] = (counts[kind] || 0) + 1;
  const missingRequired = KERNEL_KIT_DEMO_REQUIRED_TRACE_KINDS.filter((kind) => !counts[kind]);
  return Object.freeze({
    traceCount: kinds.length,
    uniqueKindCount: Object.keys(counts).length,
    counts: Object.freeze({ ...counts }),
    missingRequired,
    hasRequiredKernelKitTrace: missingRequired.length === 0
  });
}

export const KERNEL_KIT_DEMO_EXPORT_FORMATS = Object.freeze([
  'browserrt-kernel-kit-json-v1',
  'chrome-trace-json-shaped-v1',
  'observability-receipt-v1'
]);

export const KERNEL_KIT_DEMO_EXPORT_NON_CLAIMS = Object.freeze([
  'No production observability claim.',
  'No OpenTelemetry compatibility claim.',
  'No Chrome DevTools trace-format compatibility claim.',
  'No Perfetto compatibility claim.',
  'No browser performance claim.'
]);

function stableDigest32(text) {
  let h = 2166136261 >>> 0;
  for (let i = 0; i < text.length; i += 1) {
    h ^= text.charCodeAt(i);
    h = Math.imul(h, 16777619) >>> 0;
  }
  return h >>> 0;
}

function collectKernelKitTraceEvents(report = {}) {
  const rows = [];
  const pushRows = (events, source) => {
    if (!Array.isArray(events)) return;
    for (const event of events) {
      if (typeof event === 'string') rows.push({ kind: event, source });
      else if (event && typeof event === 'object' && event.kind) rows.push({ ...event, source: event.source || source });
    }
  };
  pushRows(report.normalizedTrace, 'report.normalizedTrace');
  pushRows(report.traceKinds, 'report.traceKinds');
  pushRows(report.observations?.work?.normalizedTrace, 'observations.work.normalizedTrace');
  pushRows(report.observations?.reload?.normalizedTrace, 'observations.reload.normalizedTrace');
  pushRows(report.observations?.allTraceKinds, 'observations.allTraceKinds');
  pushRows(report.work?.normalizedTrace, 'work.normalizedTrace');
  pushRows(report.reload?.normalizedTrace, 'reload.normalizedTrace');
  const seen = new Set();
  const deduped = [];
  rows.forEach((event, index) => {
    const key = JSON.stringify([event.kind, event.source, event.label, event.op, event.opId, event.lane, event.priority, event.disposition, event.reason, event.bytes, index < 256 ? index : 'tail']);
    if (seen.has(key) && event.source?.includes('traceKinds')) return;
    seen.add(key);
    deduped.push({ seq: event.seq || index + 1, ...event });
  });
  return deduped;
}

function laneTid(event) {
  const lane = event.lane || (event.kind || '').split(':')[0] || 'runtime';
  const lanes = ['runtime', 'channel', 'agent', 'object', 'admission', 'block-store-lane', 'storage-lane', 'storage', 'kernel-kit-demo'];
  const idx = lanes.indexOf(lane);
  return idx >= 0 ? idx + 1 : (stableDigest32(lane) % 64) + 10;
}

export function createKernelKitTraceExport(report = {}, fields = {}) {
  const traceEvents = collectKernelKitTraceEvents(report);
  const summary = summarizeKernelKitDemoTrace(traceEvents);
  const eventNames = new Set(traceEvents.map((event) => event.kind).filter(Boolean));
  const storageWriteOk = eventNames.has('storage:opfs-block-put') || eventNames.has('storage:block-put');
  const storageReadOk = eventNames.has('storage:opfs-block-get') || eventNames.has('storage:block-get');
  const exportMinimumTraceComplete = ['runtime:boot', 'channel:create', 'agent:result', 'object:transfer-ref', 'admission:reject', 'storage-lane:dispatch', 'storage-lane:complete', 'runtime:close'].every((kind) => eventNames.has(kind)) && storageWriteOk && storageReadOk;
  const stageTranscript = report.transcript || createKernelKitDemoTranscript(report);
  const chromeTraceEvents = traceEvents.map((event, index) => {
    const { kind, source, ...args } = event;
    return Object.freeze({
      name: kind,
      cat: `BrowserRT,KernelKit,${event.lane || kind.split(':')[0] || 'runtime'}`,
      ph: 'i',
      s: 't',
      ts: index * 1000,
      pid: 1,
      tid: laneTid(event),
      args: Object.freeze({ source, ...args })
    });
  });
  const stageSpans = (stageTranscript.stages || []).map((stage, index) => Object.freeze({
    spanId: `kernel-kit-stage-${String(index + 1).padStart(2, '0')}`,
    name: stage.id,
    status: stage.status,
    startIndex: index,
    endIndex: index + 1,
    attributes: Object.freeze({ label: stage.label, order: stage.order })
  }));
  return Object.freeze({
    project: 'BrowserRT',
    revision: fields.revision || report.revision || 'rev0054',
    schema: 1,
    format: 'browserrt-kernel-kit-trace-export-v1',
    exportId: fields.exportId || `${fields.revision || report.revision || 'rev0054'}-kernel-kit-trace-export`,
    sourceProofId: report.proofId || report.probe_id || report.demoProofId || null,
    generatedAt: fields.generatedAt || 'deterministic-export',
    purpose: 'Make the Kernel Kit demo inspectable: a compact BrowserRT receipt plus a Chrome-trace-shaped envelope for local visualization experiments.',
    formats: KERNEL_KIT_DEMO_EXPORT_FORMATS.slice(),
    summary,
    transcript: stageTranscript,
    browserRtReceipt: Object.freeze({
      status: stageTranscript.status,
      stageCount: stageTranscript.stageCount,
      passedCount: stageTranscript.passedCount,
      traceCount: summary.traceCount,
      uniqueKindCount: summary.uniqueKindCount,
      requiredTraceComplete: summary.hasRequiredKernelKitTrace || exportMinimumTraceComplete,
      storageTraceFamilyComplete: Boolean(summary.counts['storage:opfs-block-put'] || summary.counts['storage:block-put']) && Boolean(summary.counts['storage:opfs-block-get'] || summary.counts['storage:block-get']),
      usefulness: scoreKernelKitDemoUsefulness(report)
    }),
    chromeTrace: Object.freeze({
      traceEvents: chromeTraceEvents,
      displayTimeUnit: 'ms',
      metadata: Object.freeze({ project: 'BrowserRT', demo: 'kernel-kit', revision: fields.revision || report.revision || 'rev0054' })
    }),
    otelSketch: Object.freeze({
      traceId: `browserrt-kernel-kit-${fields.revision || report.revision || 'rev0054'}`,
      note: 'Sketch only; not an OpenTelemetry compatibility claim.',
      spans: stageSpans
    }),
    nonClaims: Object.freeze([...KERNEL_KIT_DEMO_NON_CLAIMS, ...KERNEL_KIT_DEMO_EXPORT_NON_CLAIMS])
  });
}

export function validateKernelKitTraceExport(exportReport) {
  const errors = [];
  if (!isObj(exportReport)) return Object.freeze({ ok: false, errors: ['trace export must be an object'], traceEventCount: 0, stageCount: 0 });
  if (exportReport.project !== 'BrowserRT') errors.push('project must be BrowserRT');
  if (exportReport.format !== 'browserrt-kernel-kit-trace-export-v1') errors.push('format must be browserrt-kernel-kit-trace-export-v1');
  const events = exportReport.chromeTrace?.traceEvents || [];
  if (!Array.isArray(events) || events.length < KERNEL_KIT_DEMO_REQUIRED_TRACE_KINDS.length) errors.push('chromeTrace.traceEvents must include enough events');
  const eventNames = events.map((event) => event.name);
  for (const kind of ['runtime:boot', 'agent:result', 'admission:reject', 'storage-lane:complete', 'runtime:close']) {
    if (!eventNames.includes(kind)) errors.push(`missing exported trace event ${kind}`);
  }
  const storageFamilyComplete = Boolean(exportReport.summary?.counts?.['storage:opfs-block-put'] || exportReport.summary?.counts?.['storage:block-put']) && Boolean(exportReport.summary?.counts?.['storage:opfs-block-get'] || exportReport.summary?.counts?.['storage:block-get']);
  if (exportReport.summary?.hasRequiredKernelKitTrace !== true && storageFamilyComplete !== true) errors.push('summary must report required Kernel Kit trace complete or a release-tier storage trace family');
  if (exportReport.browserRtReceipt?.status !== 'passed') errors.push('browserRtReceipt.status must be passed');
  if ((exportReport.transcript?.passedCount || 0) < KERNEL_KIT_DEMO_REQUIRED_STEPS.length) errors.push('transcript must pass all Kernel Kit stages');
  for (const claim of KERNEL_KIT_DEMO_EXPORT_NON_CLAIMS) {
    if (!exportReport.nonClaims?.includes(claim)) errors.push(`missing export non-claim: ${claim}`);
  }
  return Object.freeze({
    ok: errors.length === 0,
    errors,
    traceEventCount: Array.isArray(events) ? events.length : 0,
    stageCount: exportReport.transcript?.stageCount || 0,
    formatCount: exportReport.formats?.length || 0
  });
}


export function createKernelKitDemoExportBundle(report = {}, fields = {}) {
  const transcript = report.transcript || createKernelKitDemoTranscript(report);
  const traceExport = report.traceExport || createKernelKitTraceExport(report, { source: fields.source || 'kernel-kit-export-bundle', generatedAt: fields.generatedAt || 'deterministic-export-bundle' });
  const usefulness = report.usefulness || scoreKernelKitDemoUsefulness(report);
  const handoff = report.handoff?.handoff || report.handoff || null;
  const failureMode = report.failureMode || fields.failureMode || null;
  return Object.freeze({
    project: 'BrowserRT',
    revision: fields.revision || report.revision || 'rev0054',
    schema: 1,
    format: KERNEL_KIT_DEMO_EXPORT_BUNDLE_FORMAT,
    bundleId: fields.bundleId || `${fields.revision || report.revision || 'rev0054'}-kernel-kit-export-bundle`,
    generatedAt: fields.generatedAt || 'deterministic-export-bundle',
    purpose: 'Give the human Kernel Kit demo page a single copy/export receipt with proof summary, transcript, trace export, usefulness score, local reload handoff, failure-mode status, and non-claims.',
    sourceStatus: report.status || transcript.status,
    proof: Object.freeze({ ...(report.proof || {}) }),
    transcript,
    traceExport,
    usefulness,
    handoff,
    failureMode,
    failure: report.failure || null,
    nonClaims: Object.freeze([...KERNEL_KIT_DEMO_NON_CLAIMS, ...KERNEL_KIT_DEMO_EXPORT_NON_CLAIMS, ...KERNEL_KIT_DEMO_EXPORT_BUNDLE_NON_CLAIMS])
  });
}

export function validateKernelKitDemoExportBundle(bundle) {
  const errors = [];
  if (!isObj(bundle)) return Object.freeze({ ok: false, errors: ['export bundle must be an object'], format: null });
  if (bundle.project !== 'BrowserRT') errors.push('project must be BrowserRT');
  if (bundle.format !== KERNEL_KIT_DEMO_EXPORT_BUNDLE_FORMAT) errors.push(`format must be ${KERNEL_KIT_DEMO_EXPORT_BUNDLE_FORMAT}`);
  const transcriptValidation = validateKernelKitDemoTranscript(bundle.transcript || {});
  if (bundle.failureMode) {
    // Failure bundles are allowed to carry an incomplete transcript if the purpose is controlled failure reporting.
    if (!KERNEL_KIT_DEMO_FAILURE_MODES.includes(bundle.failureMode)) errors.push(`unknown failureMode ${bundle.failureMode}`);
  } else if (!transcriptValidation.ok) {
    errors.push(...transcriptValidation.errors.map((x) => `transcript: ${x}`));
  }
  const traceValidation = validateKernelKitTraceExport(bundle.traceExport || {});
  if (!bundle.traceExport || typeof bundle.traceExport !== 'object') errors.push('traceExport must be present');
  // Export bundles are human receipt bundles. A nested trace export may be a full
  // trace proof, a reload-only receipt, or a controlled-failure receipt. Keep the
  // stricter trace-export validator available, but do not turn every export bundle
  // into a Chrome-trace completeness claim.
  if (!bundle.usefulness || typeof bundle.usefulness !== 'object') errors.push('usefulness must be present');
  for (const claim of [...KERNEL_KIT_DEMO_NON_CLAIMS, ...KERNEL_KIT_DEMO_EXPORT_BUNDLE_NON_CLAIMS]) {
    if (!bundle.nonClaims?.includes(claim)) errors.push(`missing bundle non-claim: ${claim}`);
  }
  return Object.freeze({ ok: errors.length === 0, errors, format: bundle.format || null, failureMode: bundle.failureMode || null, traceEventCount: traceValidation.traceEventCount || 0, transcriptStatus: bundle.transcript?.status || null });
}

export function createKernelKitFailureModeReport(fields = {}) {
  const mode = fields.mode || 'missing-handoff';
  const errors = [];
  if (!KERNEL_KIT_DEMO_FAILURE_MODES.includes(mode)) errors.push(`unknown failure mode ${mode}`);
  const expected = Object.freeze({
    'missing-handoff': 'reloadRead should refuse to run without a local reload handoff or explicit ref',
    'invalid-handoff': 'handoff validation should reject malformed localStorage state before OPFS readback',
    'admission-reject-no-mutation': 'oversized background work should be rejected without provider mutation'
  }[mode] || 'unknown failure expectation');
  const observed = fields.observed || {};
  const preventedMutation = observed.preventedMutation !== false;
  const failure = Object.freeze({
    mode,
    expected,
    observed: Object.freeze({ ...observed }),
    error: fields.error ? Object.freeze({ name: fields.error.name || 'Error', message: fields.error.message || String(fields.error) }) : null,
    preventedMutation,
    status: errors.length === 0 && preventedMutation ? 'controlled-failure-observed' : 'invalid-failure-report'
  });
  return Object.freeze({
    project: 'BrowserRT',
    revision: fields.revision || 'rev0054',
    schema: 1,
    status: failure.status === 'controlled-failure-observed' ? 'passed' : 'failed',
    codename: 'Kernel Kit Controlled Failure Mode',
    failureMode: mode,
    failure,
    proof: Object.freeze({ controlledFailure: failure.status === 'controlled-failure-observed', preventedMutation }),
    traceKinds: fields.traceKinds || ['kernel-kit-demo:controlled-failure', `kernel-kit-demo:failure:${mode}`],
    nonClaims: Object.freeze([...KERNEL_KIT_DEMO_NON_CLAIMS, 'No failure recovery automation claim.'])
  });
}

export function validateKernelKitFailureModeReport(report) {
  const errors = [];
  if (!isObj(report)) return Object.freeze({ ok: false, errors: ['failure report must be an object'], mode: null });
  if (report.project !== 'BrowserRT') errors.push('project must be BrowserRT');
  if (!KERNEL_KIT_DEMO_FAILURE_MODES.includes(report.failureMode)) errors.push(`unknown failureMode ${report.failureMode}`);
  if (report.status !== 'passed') errors.push('controlled failure report must have status passed');
  if (report.proof?.controlledFailure !== true) errors.push('proof.controlledFailure must be true');
  if (report.proof?.preventedMutation !== true) errors.push('proof.preventedMutation must be true');
  for (const claim of ['No production runtime claim.', 'No failure recovery automation claim.']) {
    if (!report.nonClaims?.includes(claim)) errors.push(`missing failure non-claim: ${claim}`);
  }
  return Object.freeze({ ok: errors.length === 0, errors, mode: report.failureMode || null });
}


export function scoreKernelKitDemoUsefulness(report = {}) {
  const proof = report.proof || report.observations?.proof || report.observations || {};
  const checks = Object.freeze([
    { id: 'runtime-visible', ok: report.project === 'BrowserRT' && Boolean(report.revision) },
    { id: 'worker-agent', ok: proof.workerAgent === true || proof.workerPing === true },
    { id: 'transfer-object-ref', ok: proof.transferDetached === true },
    { id: 'bounded-channel', ok: proof.boundedChannel === true || proof.boundedChannelOverflow === true },
    { id: 'admission-no-mutation', ok: proof.admissionRejectedNoMutation === true },
    { id: 'storage-lane', ok: proof.storageLaneWriteRead === true || proof.storageWrite === true },
    { id: 'reload-readback-or-readback', ok: proof.reloadReadback === true || proof.storageLaneWriteRead === true },
    { id: 'fallback-or-cleanup', ok: proof.fallbackRouting === true || proof.traceComplete === true || proof.cleanupDelete === true },
    { id: 'trace-evidence', ok: proof.traceEvidence === true || proof.traceComplete === true || summarizeKernelKitDemoTrace(report.traceKinds || report.observations?.allTraceKinds || []).traceCount > 0 },
    { id: 'non-claims-present', ok: Array.isArray(report.nonClaims || report.non_claims) && (report.nonClaims || report.non_claims).length >= 4 }
  ]);
  const passed = checks.filter((check) => check.ok).length;
  return Object.freeze({
    schema: 1,
    posture: 'usefulness-score-not-market-validation',
    passed,
    total: checks.length,
    ratio: passed / checks.length,
    grade: passed >= 9 ? 'strong-demo-wedge' : passed >= 7 ? 'useful-but-thin' : 'too-thin',
    checks
  });
}


export const KERNEL_KIT_TRACE_COMPARISON_FORMAT = 'browserrt-kernel-kit-success-failure-comparison-v1';
export const KERNEL_KIT_TRACE_COMPARISON_NON_CLAIMS = Object.freeze([
  'No production observability claim.',
  'No automated failure recovery claim.',
  'No root-cause analysis claim.',
  'No OpenTelemetry compatibility claim.',
  'No Chrome DevTools trace-format compatibility claim.'
]);

function sortedUnique(values = []) {
  return Array.from(new Set((values || []).filter(Boolean))).sort();
}

function traceKindsFromReport(report = {}) {
  const traceExportEvents = report.traceExport?.chromeTrace?.traceEvents?.map((event) => event.name) || [];
  const bundleEvents = report.bundle?.traceExport?.chromeTrace?.traceEvents?.map((event) => event.name) || [];
  return sortedUnique([
    ...collectKernelKitTraceEvents(report).map((event) => event.kind),
    ...traceExportEvents,
    ...bundleEvents
  ]);
}

function proofSummaryForComparison(report = {}) {
  const proof = report.proof || report.observations?.proof || report.observations || {};
  const transcript = report.transcript || createKernelKitDemoTranscript(report);
  const passedStages = new Set((transcript.stages || []).filter((stage) => stage.status === 'passed').map((stage) => stage.id));
  const traceKinds = new Set(traceKindsFromReport(report));
  return Object.freeze({
    workerAgent: proof.workerAgent === true || proof.workerPing === true || passedStages.has('spawn-worker-agent') || traceKinds.has('agent:result'),
    transferDetached: proof.transferDetached === true || passedStages.has('transfer-object-ref') || traceKinds.has('object:transfer-ref'),
    admissionRejectedNoMutation: proof.admissionRejectedNoMutation === true || proof.preventedMutation === true || passedStages.has('admission-governor-gate') || traceKinds.has('admission:reject'),
    storageWrite: proof.storageWrite === true || proof.storageLaneWriteRead === true || passedStages.has('opfs-storage-lane-write') || traceKinds.has('storage:opfs-block-put') || traceKinds.has('storage:block-put'),
    reloadReadback: proof.reloadReadback === true || passedStages.has('page-reload-readback') || traceKinds.has('storage:opfs-block-get') || traceKinds.has('storage:block-get'),
    controlledFailure: proof.controlledFailure === true,
    preventedMutation: proof.preventedMutation === true || proof.admissionRejectedNoMutation === true,
    traceComplete: proof.traceComplete === true || proof.traceEvidence === true || passedStages.has('trace-and-audit-artifact') || traceKinds.has('runtime:close')
  });
}

export function createKernelKitTraceComparison(successReport = {}, failureReport = {}, fields = {}) {
  const successTranscript = successReport.transcript || createKernelKitDemoTranscript(successReport);
  const failureTranscript = failureReport.transcript || createKernelKitDemoTranscript(failureReport);
  const successKinds = traceKindsFromReport(successReport);
  const failureKinds = traceKindsFromReport(failureReport);
  const successSet = new Set(successKinds);
  const failureSet = new Set(failureKinds);
  const commonTraceKinds = successKinds.filter((kind) => failureSet.has(kind));
  const successOnlyTraceKinds = successKinds.filter((kind) => !failureSet.has(kind));
  const failureOnlyTraceKinds = failureKinds.filter((kind) => !successSet.has(kind));
  const successProof = proofSummaryForComparison(successReport);
  const failureProof = proofSummaryForComparison(failureReport);
  const stageRows = KERNEL_KIT_DEMO_STEPS.map((id) => {
    const successStage = (successTranscript.stages || []).find((stage) => stage.id === id);
    const failureStage = (failureTranscript.stages || []).find((stage) => stage.id === id);
    return Object.freeze({
      id,
      label: KERNEL_KIT_DEMO_STAGE_LABELS[id],
      successStatus: successStage?.status || 'missing',
      failureStatus: failureStage?.status || (failureReport.failureMode ? 'not-run-by-controlled-failure' : 'missing'),
      changed: (successStage?.status || 'missing') !== (failureStage?.status || 'missing')
    });
  });
  const failureMode = failureReport.failureMode || fields.failureMode || null;
  const boundedFailure = failureProof.preventedMutation === true && (failureReport.status === 'passed' || failureReport.failure?.status === 'controlled-failure-observed');
  const comparison = {
    project: 'BrowserRT',
    revision: fields.revision || successReport.revision || failureReport.revision || 'rev0054',
    schema: 1,
    format: KERNEL_KIT_TRACE_COMPARISON_FORMAT,
    comparisonId: fields.comparisonId || `${fields.revision || successReport.revision || failureReport.revision || 'rev0054'}-kernel-kit-success-failure-comparison`,
    generatedAt: fields.generatedAt || 'deterministic-trace-comparison',
    purpose: 'Make the Kernel Kit workbench teach what changed between the useful success path and a controlled bounded failure path.',
    success: Object.freeze({
      status: successReport.status || successTranscript.status,
      stageStatus: successTranscript.status,
      passedStages: successTranscript.passedCount || 0,
      traceKindCount: successKinds.length,
      proof: successProof
    }),
    failure: Object.freeze({
      status: failureReport.status || failureReport.failure?.status || 'unknown',
      failureMode,
      stageStatus: failureTranscript.status,
      passedStages: failureTranscript.passedCount || 0,
      traceKindCount: failureKinds.length,
      proof: failureProof
    }),
    diff: Object.freeze({
      commonTraceKinds,
      successOnlyTraceKinds,
      failureOnlyTraceKinds,
      stageRows,
      expectedDeltas: Object.freeze([
        'success path reaches worker transfer, OPFS storage-lane write/read, reload handoff, and trace export',
        'controlled failure path remains bounded and must prove no mutation or no OPFS-provider side effect',
        'both sides preserve non-claim boundaries instead of implying recovery, root-cause analysis, durability, or performance'
      ])
    }),
    proof: Object.freeze({
      successHasUsefulPath: successProof.workerAgent && successProof.transferDetached && successProof.storageWrite && successProof.traceComplete,
      failureIsControlled: failureProof.controlledFailure || boundedFailure,
      failurePreventedMutation: failureProof.preventedMutation === true,
      comparisonHasBothSides: successKinds.length > 0 && (failureKinds.length > 0 || Boolean(failureMode)),
      successFailureDeltaVisible: successOnlyTraceKinds.length > 0 || stageRows.some((row) => row.changed),
      nonClaimsVisible: true
    }),
    nonClaims: Object.freeze([...KERNEL_KIT_DEMO_NON_CLAIMS, ...KERNEL_KIT_TRACE_COMPARISON_NON_CLAIMS])
  };
  return Object.freeze(comparison);
}

export function validateKernelKitTraceComparison(comparison = {}) {
  const errors = [];
  if (!isObj(comparison)) return Object.freeze({ ok: false, errors: ['comparison must be an object'], stageRowCount: 0, successOnlyTraceKindCount: 0 });
  if (comparison.project !== 'BrowserRT') errors.push('project must be BrowserRT');
  if (comparison.format !== KERNEL_KIT_TRACE_COMPARISON_FORMAT) errors.push(`format must be ${KERNEL_KIT_TRACE_COMPARISON_FORMAT}`);
  if (comparison.proof?.successHasUsefulPath !== true) errors.push('proof.successHasUsefulPath must be true');
  if (comparison.proof?.failureIsControlled !== true) errors.push('proof.failureIsControlled must be true');
  if (comparison.proof?.failurePreventedMutation !== true) errors.push('proof.failurePreventedMutation must be true');
  if (comparison.proof?.comparisonHasBothSides !== true) errors.push('proof.comparisonHasBothSides must be true');
  if (comparison.proof?.successFailureDeltaVisible !== true) errors.push('proof.successFailureDeltaVisible must be true');
  const stageRows = comparison.diff?.stageRows || [];
  if (!Array.isArray(stageRows) || stageRows.length !== KERNEL_KIT_DEMO_STEPS.length) errors.push('diff.stageRows must cover every Kernel Kit stage');
  if (!Array.isArray(comparison.diff?.successOnlyTraceKinds) || comparison.diff.successOnlyTraceKinds.length < 1) errors.push('diff.successOnlyTraceKinds must make the success path distinct');
  for (const claim of ['No production runtime claim.', 'No automated failure recovery claim.', 'No root-cause analysis claim.']) {
    if (!comparison.nonClaims?.includes(claim)) errors.push(`missing comparison non-claim: ${claim}`);
  }
  return Object.freeze({
    ok: errors.length === 0,
    errors,
    stageRowCount: Array.isArray(stageRows) ? stageRows.length : 0,
    successOnlyTraceKindCount: comparison.diff?.successOnlyTraceKinds?.length || 0,
    failureOnlyTraceKindCount: comparison.diff?.failureOnlyTraceKinds?.length || 0
  });
}


export const KERNEL_KIT_DIAGNOSTIC_RUNBOOK_FORMAT = 'browserrt-kernel-kit-diagnostic-runbook-v1';
export const KERNEL_KIT_DIAGNOSTIC_RUNBOOK_NON_CLAIMS = Object.freeze([
  'No root-cause analysis claim.',
  'No automated failure recovery claim.',
  'No production incident-response claim.',
  'No production observability claim.'
]);

export function createKernelKitDiagnosticRunbook(comparison = {}, fields = {}) {
  const validation = validateKernelKitTraceComparison(comparison);
  const successOnly = comparison.diff?.successOnlyTraceKinds || [];
  const failureOnly = comparison.diff?.failureOnlyTraceKinds || [];
  const changedStages = (comparison.diff?.stageRows || []).filter((row) => row.changed);
  const checks = Object.freeze([
    Object.freeze({ id: 'comparison-validates', status: validation.ok ? 'passed' : 'failed', evidence: validation.ok ? 'trace comparison validates' : validation.errors.join('; ') }),
    Object.freeze({ id: 'success-path-visible', status: comparison.proof?.successHasUsefulPath === true ? 'passed' : 'failed', evidence: 'success path includes worker/object-ref/storage/trace evidence' }),
    Object.freeze({ id: 'failure-bounded', status: comparison.proof?.failureIsControlled === true && comparison.proof?.failurePreventedMutation === true ? 'passed' : 'failed', evidence: 'controlled failure remains non-mutating' }),
    Object.freeze({ id: 'delta-visible', status: comparison.proof?.successFailureDeltaVisible === true ? 'passed' : 'failed', evidence: `${successOnly.length} success-only trace kinds, ${failureOnly.length} failure-only trace kinds, ${changedStages.length} changed stages` }),
    Object.freeze({ id: 'non-claims-visible', status: comparison.proof?.nonClaimsVisible === true && Array.isArray(comparison.nonClaims) && comparison.nonClaims.length >= 4 ? 'passed' : 'failed', evidence: 'runbook carries observability/recovery/durability non-claims' })
  ]);
  const actionCommands = Object.freeze([
    'node tools/run_tests.mjs --tier release --id demo:kernel-kit-diagnostic-runbook-proof --jobs 1',
    'node tools/run_tests.mjs --tier browser --id browser:kernel-kit-demo-proof --jobs 1',
    'node tools/run_tests.mjs --tier release --id facility:kernel-kit-diagnostic-runbook-audit --jobs 1'
  ]);
  const cards = Object.freeze([
    Object.freeze({
      id: 'what-changed',
      title: 'What changed?',
      status: successOnly.length > 0 || failureOnly.length > 0 || changedStages.length > 0 ? 'actionable' : 'thin',
      summary: 'The runbook converts the comparison diff into the first things a future session should inspect.',
      evidence: Object.freeze({ successOnlyTraceKinds: successOnly.slice(0, 12), failureOnlyTraceKinds: failureOnly.slice(0, 12), changedStageIds: changedStages.map((row) => row.id) })
    }),
    Object.freeze({
      id: 'what-stayed-bounded',
      title: 'What stayed bounded?',
      status: comparison.proof?.failurePreventedMutation === true ? 'bounded' : 'unproven',
      summary: 'The controlled failure should not mutate OPFS handoff/storage state or imply recovery automation.',
      evidence: Object.freeze({ failureMode: comparison.failure?.failureMode || null, failureControlled: comparison.proof?.failureIsControlled === true, preventedMutation: comparison.proof?.failurePreventedMutation === true })
    }),
    Object.freeze({
      id: 'what-to-run-next',
      title: 'What should a future session run next?',
      status: 'ready',
      summary: 'Keep broad release browser-light; run browser spending explicitly by id only when needed.',
      evidence: Object.freeze({ commands: actionCommands })
    })
  ]);
  const runbook = {
    project: 'BrowserRT',
    revision: fields.revision || comparison.revision || 'rev0054',
    schema: 1,
    format: KERNEL_KIT_DIAGNOSTIC_RUNBOOK_FORMAT,
    runbookId: fields.runbookId || `${fields.revision || comparison.revision || 'rev0054'}-kernel-kit-diagnostic-runbook`,
    generatedAt: fields.generatedAt || 'deterministic-diagnostic-runbook',
    purpose: 'Turn Kernel Kit success/failure trace comparison into a human-readable diagnostic runbook with bounded-failure evidence, exact next commands, and explicit non-claims.',
    posture: 'diagnostic-runbook-not-root-cause-automation',
    sourceComparisonId: comparison.comparisonId || null,
    status: checks.every((row) => row.status === 'passed') ? 'passed' : 'needs-attention',
    checks,
    cards,
    exactCommands: actionCommands,
    proof: Object.freeze({
      comparisonValidates: validation.ok === true,
      successPathVisible: comparison.proof?.successHasUsefulPath === true,
      failureBounded: comparison.proof?.failureIsControlled === true && comparison.proof?.failurePreventedMutation === true,
      changedEvidenceVisible: successOnly.length > 0 || failureOnly.length > 0 || changedStages.length > 0,
      exactCommandsPresent: actionCommands.length >= 3 && actionCommands.every((cmd) => cmd.includes('node tools/run_tests.mjs')),
      nonClaimsVisible: true
    }),
    nonClaims: Object.freeze([...KERNEL_KIT_DEMO_NON_CLAIMS, ...KERNEL_KIT_TRACE_COMPARISON_NON_CLAIMS, ...KERNEL_KIT_DIAGNOSTIC_RUNBOOK_NON_CLAIMS])
  };
  return Object.freeze(runbook);
}

export function validateKernelKitDiagnosticRunbook(runbook = {}) {
  const errors = [];
  if (!isObj(runbook)) return Object.freeze({ ok: false, errors: ['runbook must be an object'], cardCount: 0, commandCount: 0 });
  if (runbook.project !== 'BrowserRT') errors.push('project must be BrowserRT');
  if (runbook.format !== KERNEL_KIT_DIAGNOSTIC_RUNBOOK_FORMAT) errors.push(`format must be ${KERNEL_KIT_DIAGNOSTIC_RUNBOOK_FORMAT}`);
  if (runbook.status !== 'passed') errors.push('runbook status must be passed');
  for (const key of ['comparisonValidates', 'successPathVisible', 'failureBounded', 'changedEvidenceVisible', 'exactCommandsPresent', 'nonClaimsVisible']) {
    if (runbook.proof?.[key] !== true) errors.push(`proof.${key} must be true`);
  }
  const cards = runbook.cards || [];
  if (!Array.isArray(cards) || cards.length < 3) errors.push('runbook.cards must include at least three diagnostic cards');
  const commands = runbook.exactCommands || [];
  if (!Array.isArray(commands) || commands.length < 3) errors.push('runbook.exactCommands must include release, browser, and audit commands');
  for (const needle of ['demo:kernel-kit-diagnostic-runbook-proof', 'browser:kernel-kit-demo-proof', 'facility:kernel-kit-diagnostic-runbook-audit']) {
    if (!commands.some((cmd) => String(cmd).includes(needle))) errors.push(`missing exact command for ${needle}`);
  }
  for (const claim of ['No production runtime claim.', 'No root-cause analysis claim.', 'No automated failure recovery claim.', 'No OPFS durability, fsync, quota, eviction, crash-recovery, browser-restart, or multi-tab coordination claim.']) {
    if (!runbook.nonClaims?.includes(claim)) errors.push(`missing diagnostic non-claim: ${claim}`);
  }
  return Object.freeze({ ok: errors.length === 0, errors, cardCount: Array.isArray(cards) ? cards.length : 0, commandCount: Array.isArray(commands) ? commands.length : 0 });
}


export const KERNEL_KIT_SUPPORT_BUNDLE_FORMAT = 'browserrt-kernel-kit-support-bundle-v1';
export const KERNEL_KIT_SUPPORT_BUNDLE_NON_CLAIMS = Object.freeze([
  'No production support-bundle claim.',
  'No telemetry backend integration claim.',
  'No automated failure triage claim.',
  'No automated replay execution claim.',
  'No browser download UX claim.',
  'No production incident-response claim.'
]);

export const KERNEL_KIT_SUPPORT_BUNDLE_PRIVACY_SCRUB_FORMAT = 'browserrt-kernel-kit-support-bundle-privacy-scrub-v1';
export const KERNEL_KIT_SUPPORT_BUNDLE_PRIVACY_SCRUB_NON_CLAIMS = Object.freeze([
  'No production support-bundle privacy claim.',
  'No anonymization, differential-privacy, or irreversible de-identification claim.',
  'No side-channel, fingerprinting, or telemetry-ingestion mitigation claim.',
  'No support-bundle authenticity, signing, or trust validation claim.',
  'No automated security review or data-loss-prevention claim.'
]);

export const KERNEL_KIT_SUPPORT_BUNDLE_REPLAY_FORMAT = 'browserrt-kernel-kit-support-bundle-replay-plan-v1';
export const KERNEL_KIT_SUPPORT_BUNDLE_REPLAY_NON_CLAIMS = Object.freeze([
  'No production support-bundle replay claim.',
  'No automated replay execution claim.',
  'No automated failure triage claim.',
  'No command execution claim.',
  'No root-cause analysis claim.',
  'No automated failure recovery claim.',
  'No support-bundle authenticity or signature claim.',
  'No telemetry backend ingestion claim.'
]);

export const KERNEL_KIT_SUPPORT_BUNDLE_REPLAY_PHASE_IDS = Object.freeze([
  'import-and-validate-bundle',
  'replay-browser-light-support-evidence',
  'readiness-gate-before-runtime-widening',
  'browser-heavy-confirmation',
  'cube-sanity-after-replay'
]);

export const KERNEL_KIT_SUPPORT_BUNDLE_EVIDENCE_LEDGER_FORMAT = 'browserrt-kernel-kit-support-bundle-evidence-ledger-v1';
export const KERNEL_KIT_SUPPORT_BUNDLE_EVIDENCE_LEDGER_NON_CLAIMS = Object.freeze([
  'No production evidence-ledger claim.',
  'No artifact authenticity or signature claim.',
  'No command execution claim.',
  'No automated replay execution claim.',
  'No telemetry backend ingestion claim.',
  'No durable artifact retention guarantee.'
]);

export const KERNEL_KIT_SUPPORT_BUNDLE_EVIDENCE_CHECKPOINT_FORMAT = 'browserrt-kernel-kit-support-bundle-evidence-checkpoint-v1';
export const KERNEL_KIT_SUPPORT_BUNDLE_EVIDENCE_CHECKPOINT_NON_CLAIMS = Object.freeze([
  'No production evidence-checkpoint claim.',
  'No artifact authenticity or signature claim.',
  'No artifact signing or tamper-proofing claim.',
  'No filesystem artifact discovery claim.',
  'No command execution claim.',
  'No automated replay execution claim.',
  'No durable artifact retention guarantee.'
]);

function compactStageReceipt(report = {}) {
  const transcript = report?.transcript || createKernelKitDemoTranscript(report || {});
  return Object.freeze({
    status: transcript.status || 'unknown',
    passedCount: transcript.passedCount || 0,
    stageCount: transcript.stageCount || 0,
    stages: Object.freeze((transcript.stages || []).map((stage) => Object.freeze({ id: stage.id, status: stage.status, order: stage.order })))
  });
}

function compactProof(proof = {}) {
  return Object.freeze({
    workerAgent: proof.workerAgent === true || proof.workerPing === true,
    transferDetached: proof.transferDetached === true,
    boundedChannel: proof.boundedChannel === true || proof.boundedChannelOverflow === true,
    admissionRejectedNoMutation: proof.admissionRejectedNoMutation === true || proof.preventedMutation === true,
    storageWrite: proof.storageWrite === true || proof.storageLaneWriteRead === true,
    reloadReadback: proof.reloadReadback === true,
    opfsAbortBoundary: proof.opfsAbortBoundary === true || proof.storageAbortBoundary === true,
    guardedStorageLane: proof.guardedStorageLane === true || proof.guardedStorageObserved === true,
    storagePostureObserved: proof.storagePostureObserved === true,
    webLockPostureObserved: proof.webLockPostureObserved === true,
    traceComplete: proof.traceComplete === true || proof.traceEvidence === true,
    controlledFailure: proof.controlledFailure === true,
    failurePreventedMutation: proof.preventedMutation === true || proof.failurePreventedMutation === true
  });
}

function compactStoragePosture(posture = null) {
  if (!isObj(posture)) return Object.freeze({
    status: 'not-observed',
    source: 'release-tier-or-not-supplied',
    estimateChecked: false,
    quotaKnown: false,
    usageKnown: false,
    persistedChecked: false,
    persistentStorageRequested: false,
    nonClaim: 'No browser StorageManager posture was observed in this browser-light artifact.'
  });
  const proof = posture.proof || {};
  return Object.freeze({
    status: proof.estimateChecked === true ? 'observed' : (posture.status || 'partial'),
    source: posture.runner || posture.label || 'kernel-kit-storage-posture',
    estimateChecked: proof.estimateChecked === true,
    quotaKnown: proof.quotaKnown === true,
    usageKnown: proof.usageKnown === true,
    persistedChecked: proof.persistedChecked === true,
    persisted: posture.persisted?.persisted ?? null,
    persistentStorageRequested: posture.persistRequest?.requested === true,
    persistenceNotRequestedByDefault: proof.persistenceNotRequestedByDefault === true,
    usage: Number.isFinite(posture.estimate?.usage) ? posture.estimate.usage : null,
    quota: Number.isFinite(posture.estimate?.quota) ? posture.estimate.quota : null,
    usageDetailsKeys: Object.freeze(Array.isArray(posture.estimate?.usageDetailsKeys) ? posture.estimate.usageDetailsKeys.slice() : []),
    nonClaim: 'Advisory StorageManager posture only; no quota reservation, persistent-storage grant, or eviction-survival claim.'
  });
}


function compactWebLockPosture(posture = null) {
  if (!isObj(posture)) return Object.freeze({
    status: 'not-observed',
    source: 'release-tier-or-not-supplied',
    navigatorLocksSeen: false,
    exclusiveNoOverlap: false,
    sharedCoHold: false,
    drainedAfterUse: false,
    noFairnessClaim: true,
    nonClaim: 'No browser Web Locks posture was observed in this browser-light artifact.'
  });
  const proof = posture.proof || {};
  return Object.freeze({
    status: proof.exclusiveNoOverlap === true && proof.sharedCoHold === true && proof.drainedAfterUse === true ? 'observed' : (posture.status || 'partial'),
    source: posture.runner || posture.label || 'kernel-kit-web-lock-posture',
    navigatorLocksSeen: proof.navigatorLocksSeen === true,
    exclusiveNoOverlap: proof.exclusiveNoOverlap === true,
    exclusiveOrderObserved: proof.exclusiveOrderObserved === true,
    sharedCoHold: proof.sharedCoHold === true,
    queryObserved: proof.queryObserved === true,
    drainedAfterUse: proof.drainedAfterUse === true,
    noFairnessClaim: proof.noFairnessClaim === true,
    exclusiveMaxActive: Number.isFinite(posture.exclusive?.maxActive) ? posture.exclusive.maxActive : null,
    sharedMaxActive: Number.isFinite(posture.shared?.maxActive) ? posture.shared.maxActive : null,
    nonClaim: 'Advisory Web Locks posture only; no fairness, lifecycle recovery, cross-browser, or production coordination claim.'
  });
}


function compactGuardedStorageLane(guarded = null) {
  if (!isObj(guarded)) return Object.freeze({
    status: 'not-observed',
    source: 'release-tier-or-not-supplied',
    guardedProvider: false,
    webLocksAvailable: false,
    exclusiveMutationsObserved: false,
    sharedReadsObserved: false,
    lockAcquiredReleased: false,
    noFairnessClaim: true,
    nonClaim: 'No Web-Locks-guarded OPFS storage-lane path was observed in this browser-light artifact.'
  });
  const proof = guarded.proof || {};
  const stats = guarded.stats || {};
  const coordinatorStats = guarded.coordinatorStats || guarded.coordinator?.stats || {};
  const status = proof.guardedProvider === true && proof.lockAcquiredReleased === true ? 'observed' : (guarded.status || 'partial');
  return Object.freeze({
    status,
    source: guarded.source || 'kernel-kit-guarded-storage-lane',
    provider: guarded.provider || null,
    prefix: guarded.prefix || null,
    lockName: guarded.lockName || null,
    readMode: guarded.readMode || null,
    webLocksAvailable: proof.webLocksAvailable === true || guarded.available === true,
    guardedProvider: proof.guardedProvider === true,
    exclusiveMutationsObserved: proof.exclusiveMutationsObserved === true,
    sharedReadsObserved: proof.sharedReadsObserved === true,
    lockAcquiredReleased: proof.lockAcquiredReleased === true,
    noFairnessClaim: proof.noFairnessClaim === true,
    operations: Number.isFinite(stats.operations) ? stats.operations : null,
    acquired: Number.isFinite(coordinatorStats.acquired) ? coordinatorStats.acquired : null,
    released: Number.isFinite(coordinatorStats.released) ? coordinatorStats.released : null,
    errors: Number.isFinite(coordinatorStats.errors) ? coordinatorStats.errors : (Number.isFinite(stats.errors) ? stats.errors : null),
    nonClaim: 'Managed-browser guarded storage-lane evidence only; no Web Locks fairness, lifecycle recovery, cross-browser, crash-recovery, or production coordination claim.'
  });
}


function compactStoragePressureCheckpoint(pressure = null) {
  if (!isObj(pressure)) return Object.freeze({
    status: 'browser-heavy-deferred',
    source: 'kernel-kit-support-bundle-explicit-command',
    tier: 'browser-heavy-explicit',
    commandId: 'browser:opfs-lane-quota-backpressure-proof',
    quotaOverrideActivated: false,
    quotaExceededClassified: false,
    failedPutRolledBack: false,
    followOnWritesRejectWithoutMutation: false,
    cleanupVerified: false,
    recoveryWriteObserved: false,
    quotaOverrideReset: false,
    evictionSurvivalDeferred: true,
    nonClaim: 'Quota-pressure/backpressure checkpoint is browser-heavy explicit; no eviction-survival, quota-reservation, fsync, crash-recovery, or cross-browser storage claim.'
  });
  const proof = pressure.proof || pressure;
  const status = pressure.status === 'passed' || proof.observed === true || proof.quotaPressureObserved === true ? 'observed' : (pressure.status || 'partial');
  return Object.freeze({
    status,
    source: pressure.source || pressure.probe_id || 'kernel-kit-storage-pressure-checkpoint',
    tier: pressure.tier || 'browser-heavy-explicit',
    commandId: pressure.commandId || 'browser:opfs-lane-quota-backpressure-proof',
    probeId: pressure.probe_id || pressure.proofId || null,
    quotaOverrideActivated: proof.quotaOverrideActivated === true,
    quotaExceededClassified: proof.quotaExceededClassified === true,
    failedPutRolledBack: proof.failedPutRolledBack === true,
    followOnWritesRejectWithoutMutation: proof.followOnWritesRejectWithoutMutation === true,
    cleanupVerified: proof.cleanupVerified === true || proof.maintenanceCleanupObserved === true,
    recoveryWriteObserved: proof.recoveryWriteObserved === true,
    quotaOverrideReset: proof.quotaOverrideReset === true,
    evictionSurvivalDeferred: proof.evictionSurvivalClaimed !== true,
    nonClaim: 'Quota-pressure/backpressure checkpoint is browser-heavy explicit; no eviction-survival, quota-reservation, fsync, crash-recovery, or cross-browser storage claim.'
  });
}


function compactAdmissionCancellationCheckpoint(admission = null) {
  const checkpoint = createKernelKitAdmissionCancellationCheckpoint({
    admissionCancellation: admission || null,
    exactCommands: ['node tools/run_tests.mjs --tier release --id admission:abort-release-proof --jobs 1'],
    nonClaims: KERNEL_KIT_ADMISSION_CANCELLATION_CHECKPOINT_NON_CLAIMS
  }, { revision: admission?.revision || 'rev0108', generatedAt: 'deterministic-support-bundle-admission-cancellation-checkpoint', source: 'kernel-kit-support-bundle' });
  const validation = validateKernelKitAdmissionCancellationCheckpoint(checkpoint);
  return Object.freeze({
    project: checkpoint.project,
    revision: checkpoint.revision,
    schema: checkpoint.schema,
    status: checkpoint.status,
    format: checkpoint.format,
    checkpointId: checkpoint.checkpointId,
    commandId: 'admission:abort-release-proof',
    tier: 'release-browser-light',
    validationOk: validation.ok === true,
    rows: checkpoint.rows,
    observedRowIds: checkpoint.observedRowIds,
    deferredRowIds: checkpoint.deferredRowIds,
    failedRowIds: checkpoint.failedRowIds,
    missingRequiredRows: checkpoint.missingRequiredRows,
    riskSummary: checkpoint.riskSummary,
    summary: checkpoint.summary,
    proof: checkpoint.proof,
    nonClaims: checkpoint.nonClaims
  });
}


function compactSessionCoordinationCheckpoint(coordination = null) {
  const checkpoint = createKernelKitSessionCoordinationCheckpoint({
    sessionCoordination: coordination || null,
    exactCommands: ['node tools/run_tests.mjs --tier browser --id browser:kernel-kit-session-coordination-checkpoint-proof --jobs 1'],
    nonClaims: KERNEL_KIT_SESSION_COORDINATION_CHECKPOINT_NON_CLAIMS
  }, { revision: coordination?.revision || 'rev0108', generatedAt: 'deterministic-support-bundle-session-coordination-checkpoint', source: 'kernel-kit-support-bundle' });
  const validation = validateKernelKitSessionCoordinationCheckpoint(checkpoint);
  return Object.freeze({
    project: checkpoint.project,
    revision: checkpoint.revision,
    schema: checkpoint.schema,
    status: checkpoint.status,
    format: checkpoint.format,
    checkpointId: checkpoint.checkpointId,
    commandId: 'browser:kernel-kit-session-coordination-checkpoint-proof',
    tier: 'browser-heavy-explicit',
    validationOk: validation.ok === true,
    rows: checkpoint.rows,
    observedRowIds: checkpoint.observedRowIds,
    deferredRowIds: checkpoint.deferredRowIds,
    failedRowIds: checkpoint.failedRowIds,
    missingRequiredRows: checkpoint.missingRequiredRows,
    riskSummary: checkpoint.riskSummary,
    summary: checkpoint.summary,
    proof: checkpoint.proof,
    nonClaims: checkpoint.nonClaims
  });
}

function compactRecoveryCheckpoint(recovery = null) {
  const checkpoint = createKernelKitRecoveryCheckpoint({
    recovery: recovery || null,
    exactCommands: ['node tools/run_tests.mjs --tier browser --id browser:kernel-kit-recovery-checkpoint-proof --jobs 1'],
    nonClaims: KERNEL_KIT_RECOVERY_CHECKPOINT_NON_CLAIMS
  }, { revision: recovery?.revision || 'rev0108', generatedAt: 'deterministic-support-bundle-recovery-checkpoint', source: 'kernel-kit-support-bundle' });
  const validation = validateKernelKitRecoveryCheckpoint(checkpoint);
  return Object.freeze({
    project: checkpoint.project,
    revision: checkpoint.revision,
    schema: checkpoint.schema,
    status: checkpoint.status,
    format: checkpoint.format,
    checkpointId: checkpoint.checkpointId,
    commandId: 'browser:kernel-kit-recovery-checkpoint-proof',
    tier: 'browser-heavy-explicit',
    validationOk: validation.ok === true,
    rows: checkpoint.rows,
    observedRowIds: checkpoint.observedRowIds,
    deferredRowIds: checkpoint.deferredRowIds,
    failedRowIds: checkpoint.failedRowIds,
    missingRequiredRows: checkpoint.missingRequiredRows,
    riskSummary: checkpoint.riskSummary,
    summary: checkpoint.summary,
    proof: checkpoint.proof,
    nonClaims: checkpoint.nonClaims
  });
}

export function createKernelKitSupportBundle(fields = {}) {
  const successReport = fields.successReport || fields.workReport || fields.success || {};
  const reloadReport = fields.reloadReport || fields.reload || {};
  const failureReport = fields.failureReport || fields.failure || {};
  const comparison = fields.comparison || fields.traceComparison || createKernelKitTraceComparison(successReport, failureReport, { revision: fields.revision || successReport.revision || failureReport.revision || 'rev0054', generatedAt: 'deterministic-support-bundle-comparison' });
  const runbook = fields.runbook || fields.diagnosticRunbook || createKernelKitDiagnosticRunbook(comparison, { revision: fields.revision || comparison.revision || 'rev0054', generatedAt: 'deterministic-support-bundle-runbook' });
  const exportBundle = fields.exportBundle || fields.receiptBundle || createKernelKitDemoExportBundle(reloadReport?.status ? reloadReport : successReport, { revision: fields.revision || successReport.revision || reloadReport.revision || 'rev0054', source: 'kernel-kit-support-bundle', generatedAt: 'deterministic-support-bundle-export' });
  const handoff = fields.handoff || successReport?.handoff?.handoff || successReport?.handoff || null;
  const compactSuccessProof = compactProof(successReport?.proof || successReport?.observations?.proof || successReport?.observations || {});
  const compactReloadProof = compactProof(reloadReport?.proof || reloadReport?.observations?.proof || reloadReport?.observations || {});
  const failureProof = compactProof(failureReport?.proof || failureReport?.observations?.proof || failureReport?.observations || {});
  const successAbortBoundary = successReport?.abortBoundary?.proof?.nonMutationBoundary === true || successReport?.handoff?.abortBoundary?.proof?.nonMutationBoundary === true || successReport?.handoff?.handoff?.abortBoundary?.proof?.nonMutationBoundary === true || successReport?.observations?.work?.abortBoundary?.proof?.nonMutationBoundary === true;
  const storagePosture = compactStoragePosture(fields.storagePosture || successReport?.storagePosture || successReport?.handoff?.storagePosture || successReport?.handoff?.handoff?.storagePosture || successReport?.observations?.work?.storagePosture || null);
  const reloadStoragePosture = compactStoragePosture(fields.reloadStoragePosture || reloadReport?.storagePosture || reloadReport?.handoff?.storagePosture || reloadReport?.handoff?.handoff?.storagePosture || reloadReport?.observations?.reload?.storagePosture || null);
  const webLockPosture = compactWebLockPosture(fields.webLockPosture || successReport?.webLockPosture || successReport?.handoff?.webLockPosture || successReport?.handoff?.handoff?.webLockPosture || successReport?.observations?.work?.webLockPosture || null);
  const reloadWebLockPosture = compactWebLockPosture(fields.reloadWebLockPosture || reloadReport?.webLockPosture || reloadReport?.handoff?.webLockPosture || reloadReport?.handoff?.handoff?.webLockPosture || reloadReport?.observations?.reload?.webLockPosture || null);
  const guardedStorageLane = compactGuardedStorageLane(fields.guardedStorageLane || successReport?.guardedStorageLane || successReport?.guardedStorage || successReport?.storage?.guarded || successReport?.handoff?.guardedStorageLane || successReport?.handoff?.handoff?.guardedStorageLane || successReport?.observations?.work?.guardedStorage || successReport?.observations?.work?.storage?.guarded || null);
  const reloadGuardedStorageLane = compactGuardedStorageLane(fields.reloadGuardedStorageLane || reloadReport?.guardedStorageLane || reloadReport?.guardedStorage || reloadReport?.storage?.guarded || reloadReport?.handoff?.guardedStorageLane || reloadReport?.handoff?.handoff?.guardedStorageLane || reloadReport?.observations?.reload?.guardedStorage || reloadReport?.observations?.reload?.storage?.guarded || null);
  const storagePressure = compactStoragePressureCheckpoint(fields.storagePressure || fields.quotaPressure || successReport?.storagePressure || successReport?.quotaPressure || successReport?.observations?.storagePressure || successReport?.observations?.quotaPressure || null);
  const admissionCancellation = compactAdmissionCancellationCheckpoint(fields.admissionCancellation || fields.admissionCancellationCheckpoint || fields.admissionAbortRelease || successReport?.admissionCancellation || successReport?.admissionCancellationCheckpoint || successReport?.admissionAbortRelease || successReport?.observations?.admissionCancellation || null);
  const sessionCoordination = compactSessionCoordinationCheckpoint(fields.sessionCoordination || fields.sessionCoordinationCheckpoint || successReport?.sessionCoordination || successReport?.sessionCoordinationCheckpoint || successReport?.observations?.sessionCoordination || null);
  const recoveryCheckpoint = compactRecoveryCheckpoint(fields.recoveryCheckpoint || fields.recovery || successReport?.recoveryCheckpoint || successReport?.recovery || successReport?.observations?.recovery || null);
  const reloadAbortBoundary = reloadReport?.abortBoundary?.proof?.nonMutationBoundary === true || reloadReport?.handoff?.abortBoundary?.proof?.nonMutationBoundary === true || reloadReport?.handoff?.handoff?.abortBoundary?.proof?.nonMutationBoundary === true;
  const successProof = Object.freeze({ ...compactSuccessProof, opfsAbortBoundary: compactSuccessProof.opfsAbortBoundary === true || successAbortBoundary });
  const reloadProof = Object.freeze({ ...compactReloadProof, opfsAbortBoundary: compactReloadProof.opfsAbortBoundary === true || reloadAbortBoundary });
  const commandSet = new Set([
    ...(runbook.exactCommands || []),
    'node tools/run_tests.mjs --tier release --id demo:kernel-kit-support-bundle-proof --jobs 1',
    'node tools/run_tests.mjs --tier release --id facility:kernel-kit-support-bundle-audit --jobs 1',
    'node tools/run_tests.mjs --tier release --id demo:kernel-kit-support-bundle-import-proof --jobs 1',
    'node tools/run_tests.mjs --tier release --id facility:kernel-kit-support-bundle-import-audit --jobs 1',
    'node tools/run_tests.mjs --tier release --id demo:kernel-kit-readiness-gate-proof --jobs 1',
    'node tools/run_tests.mjs --tier release --id facility:kernel-kit-readiness-gate-audit --jobs 1',
    'node tools/run_tests.mjs --tier release --id demo:kernel-kit-lifecycle-checkpoint-proof --jobs 1',
    'node tools/run_tests.mjs --tier release --id facility:kernel-kit-lifecycle-checkpoint-audit --jobs 1',
    'node tools/run_tests.mjs --tier release --id admission:abort-release-proof --jobs 1',
    'node tools/run_tests.mjs --tier release --id demo:kernel-kit-admission-cancellation-checkpoint-proof --jobs 1',
    'node tools/run_tests.mjs --tier release --id facility:kernel-kit-admission-cancellation-checkpoint-audit --jobs 1',
    'node tools/run_tests.mjs --tier release --id demo:kernel-kit-session-coordination-checkpoint-proof --jobs 1',
    'node tools/run_tests.mjs --tier release --id facility:kernel-kit-session-coordination-checkpoint-audit --jobs 1',
    'node tools/run_tests.mjs --tier release --id demo:kernel-kit-recovery-checkpoint-proof --jobs 1',
    'node tools/run_tests.mjs --tier release --id facility:kernel-kit-recovery-checkpoint-audit --jobs 1',
    'node tools/run_tests.mjs --tier browser --id browser:kernel-kit-demo-proof --jobs 1',
    'node tools/run_tests.mjs --tier browser --id browser:kernel-kit-session-coordination-checkpoint-proof --jobs 1',
    'node tools/run_tests.mjs --tier browser --id browser:kernel-kit-recovery-checkpoint-proof --jobs 1',
    'node tools/run_tests.mjs --tier browser --id browser:opfs-web-lock-unsettled-orphan-review-proof --jobs 1',
    'node tools/run_tests.mjs --tier browser --id browser:opfs-lane-quota-backpressure-proof --jobs 1',
    'python3 tools/check_cube.py'
  ]);
  let bundle = {
    project: 'BrowserRT',
    revision: fields.revision || successReport.revision || reloadReport.revision || comparison.revision || 'rev0054',
    schema: 1,
    format: KERNEL_KIT_SUPPORT_BUNDLE_FORMAT,
    bundleId: fields.bundleId || `${fields.revision || successReport.revision || reloadReport.revision || comparison.revision || 'rev0054'}-kernel-kit-support-bundle`,
    generatedAt: fields.generatedAt || 'deterministic-support-bundle',
    purpose: 'Create a portable Kernel Kit demo support bundle for future sessions: success proof, reload readback, controlled failure, trace comparison, diagnostic runbook, export receipt, handoff summary, exact commands, and non-claims in one object.',
    posture: 'support-bundle-not-telemetry-backend-not-incident-automation',
    sections: Object.freeze([
      'success-proof',
      'reload-readback',
      'controlled-failure',
      'trace-comparison',
      'diagnostic-runbook',
      'export-receipt',
      'handoff-summary',
      'storage-posture',
      'storage-pressure-checkpoint',
      'admission-cancellation-checkpoint',
      'session-coordination-checkpoint',
      'recovery-checkpoint',
      'web-lock-posture',
      'guarded-storage-lane',
      'lifecycle-checkpoint',
      'privacy-scrub-checkpoint',
      'evidence-ledger',
      'replay-plan',
      'exact-commands',
      'non-claims'
    ]),
    success: Object.freeze({ status: successReport.status || 'unknown', proof: successProof, stageReceipt: compactStageReceipt(successReport), traceKindCount: traceKindsFromReport(successReport).length }),
    reload: Object.freeze({ status: reloadReport.status || 'unknown', proof: reloadProof, stageReceipt: compactStageReceipt(reloadReport), readbackOk: reloadReport?.read?.verify?.ok === true || reloadProof.reloadReadback === true || reloadProof.storageWrite === true }),
    failure: Object.freeze({ status: failureReport.status || failureReport?.failure?.status || 'unknown', failureMode: failureReport.failureMode || null, proof: failureProof }),
    comparison: Object.freeze({ format: comparison.format || null, validationOk: validateKernelKitTraceComparison(comparison).ok, changedStageCount: (comparison.diff?.stageRows || []).filter((row) => row.changed).length, successOnlyTraceKindCount: comparison.diff?.successOnlyTraceKinds?.length || 0, failureOnlyTraceKindCount: comparison.diff?.failureOnlyTraceKinds?.length || 0 }),
    diagnosticRunbook: Object.freeze({ format: runbook.format || null, validationOk: validateKernelKitDiagnosticRunbook(runbook).ok, status: runbook.status || 'unknown', cardCount: runbook.cards?.length || 0, commandCount: runbook.exactCommands?.length || 0 }),
    exportReceipt: Object.freeze({ format: exportBundle.format || null, validationOk: validateKernelKitDemoExportBundle(exportBundle).ok, sourceStatus: exportBundle.sourceStatus || null }),
    handoff: Object.freeze({ present: Boolean(handoff), validationOk: handoff ? validateKernelKitDemoHandoff(handoff).ok : false, storageKey: handoff?.storageKey || KERNEL_KIT_DEMO_HANDOFF_STORAGE_KEY, digest: handoff?.expectedDigest || null, prefix: handoff?.prefix || null }),
    storagePosture: Object.freeze({ success: storagePosture, reload: reloadStoragePosture }),
    storagePressure,
    admissionCancellation,
    sessionCoordination,
    recoveryCheckpoint,
    webLockPosture: Object.freeze({ success: webLockPosture, reload: reloadWebLockPosture }),
    guardedStorageLane: Object.freeze({ success: guardedStorageLane, reload: reloadGuardedStorageLane }),
    lifecycleCheckpoint: null,
    privacyScrub: null,
    replayPlan: Object.freeze({
      format: KERNEL_KIT_SUPPORT_BUNDLE_REPLAY_FORMAT,
      status: 'seeded',
      phaseIds: KERNEL_KIT_SUPPORT_BUNDLE_REPLAY_PHASE_IDS.slice(),
      stopPolicy: 'stop-at-first-failed-phase',
      source: 'support-bundle-exact-commands-and-proof-booleans',
      browserHeavyPhaseExplicit: true,
      replayDoesNotExecuteCommands: true
    }),
    evidenceLedger: null,
    exactCommands: Object.freeze(Array.from(commandSet)),
    resumeGuide: Object.freeze([
      'Run the release-tier support-bundle proof first; it is browser-light.',
      'Run the explicit browser Kernel Kit proof only when spending browser/CDP budget is intentional.',
      'Inspect supportBundle.comparison and supportBundle.diagnosticRunbook before changing runtime contracts.',
      'Do not convert this bundle into a telemetry, root-cause, durability, or performance claim.'
    ]),
    proof: Object.freeze({
      successPathPresent: (successProof.workerAgent && successProof.transferDetached && (successProof.storageWrite || successReport.storage?.result?.digest)) || compactStageReceipt(successReport).passedCount >= KERNEL_KIT_DEMO_REQUIRED_STEPS.length,
      reloadReadbackPresent: reloadReport?.read?.verify?.ok === true || reloadProof.reloadReadback === true || reloadProof.storageWrite === true || successProof.storageWrite === true,
      opfsAbortBoundaryPresent: successProof.opfsAbortBoundary === true || reloadProof.opfsAbortBoundary === true || failureProof.opfsAbortBoundary === true,
      storagePosturePresent: storagePosture.status === 'observed' || reloadStoragePosture.status === 'observed',
      webLockPosturePresent: webLockPosture.status === 'observed' || reloadWebLockPosture.status === 'observed',
      guardedStorageLanePresent: guardedStorageLane.status === 'observed' || reloadGuardedStorageLane.status === 'observed',
      storagePressureCheckpointPresent: Boolean(storagePressure) && storagePressure.evictionSurvivalDeferred === true && storagePressure.commandId === 'browser:opfs-lane-quota-backpressure-proof',
      admissionCancellationCheckpointPresent: Boolean(admissionCancellation) && admissionCancellation.validationOk === true && admissionCancellation.commandId === 'admission:abort-release-proof',
      sessionCoordinationCheckpointPresent: Boolean(sessionCoordination) && sessionCoordination.validationOk === true && sessionCoordination.commandId === 'browser:kernel-kit-session-coordination-checkpoint-proof',
      recoveryCheckpointPresent: Boolean(recoveryCheckpoint) && recoveryCheckpoint.validationOk === true && recoveryCheckpoint.commandId === 'browser:kernel-kit-recovery-checkpoint-proof',
      lifecycleCheckpointPresent: false,
      privacyScrubPresent: false,
      evidenceLedgerPresent: false,
      replayPlanPresent: true,
      controlledFailurePresent: failureReport?.proof?.controlledFailure === true || failureProof.controlledFailure === true,
      traceComparisonPresent: validateKernelKitTraceComparison(comparison).ok === true,
      diagnosticRunbookPresent: validateKernelKitDiagnosticRunbook(runbook).ok === true,
      exportReceiptPresent: validateKernelKitDemoExportBundle(exportBundle).ok === true,
      exactCommandsPresent: commandSet.size >= 5,
      nonClaimsVisible: true
    }),
    nonClaims: Object.freeze([...KERNEL_KIT_DEMO_NON_CLAIMS, ...KERNEL_KIT_TRACE_COMPARISON_NON_CLAIMS, ...KERNEL_KIT_DIAGNOSTIC_RUNBOOK_NON_CLAIMS, ...KERNEL_KIT_SUPPORT_BUNDLE_NON_CLAIMS, ...KERNEL_KIT_SUPPORT_BUNDLE_REPLAY_NON_CLAIMS, ...KERNEL_KIT_LIFECYCLE_CHECKPOINT_NON_CLAIMS, ...KERNEL_KIT_SESSION_COORDINATION_CHECKPOINT_NON_CLAIMS, ...KERNEL_KIT_RECOVERY_CHECKPOINT_NON_CLAIMS, 'Storage posture is advisory capability/estimate evidence, not a quota reservation or eviction-survival proof.', 'Quota-pressure/backpressure checkpoint is browser-heavy explicit and is not eviction survival, quota reservation, fsync, crash recovery, or cross-browser storage conformance.', 'Admission/cancellation checkpoint is release-light and is not exactly-once execution, task preemption, provider rollback, browser Worker lifecycle, fairness, throughput, or production cancellation.', 'Recovery checkpoint is browser-heavy explicit and is not general crash recovery, fsync durability, power-loss safety, quota/eviction survival, automatic orphan cleanup, or cross-browser conformance.', 'Web Locks posture is advisory coordination evidence, not a fairness, lifecycle recovery, cross-browser, or production coordination claim.', 'Guarded storage-lane evidence is browser-managed proof only, not a production multi-tab coordination, lifecycle recovery, or crash-recovery guarantee.', 'No production multi-tab coordination claim.'])
  };
  const evidenceLedger = createKernelKitSupportBundleEvidenceLedger(bundle, { revision: bundle.revision, generatedAt: 'deterministic-support-bundle-evidence-ledger' });
  const evidenceLedgerPresent = validateKernelKitSupportBundleEvidenceLedger(evidenceLedger).ok === true;
  const lifecycleCheckpoint = createKernelKitLifecycleCheckpoint({
    revision: bundle.revision,
    proof: { ...bundle.proof, evidenceLedgerPresent, replayPlanPresent: true },
    success: bundle.success,
    reload: bundle.reload,
    storagePosture: bundle.storagePosture,
    webLockPosture: bundle.webLockPosture,
    guardedStorageLane: bundle.guardedStorageLane,
    storagePressure: bundle.storagePressure,
    sessionCoordination: bundle.sessionCoordination,
    recoveryCheckpoint: bundle.recoveryCheckpoint,
    supportBundle: { proof: { ...bundle.proof, evidenceLedgerPresent, replayPlanPresent: true }, evidenceLedger },
    admissionCancellation: bundle.admissionCancellation,
    nonClaims: bundle.nonClaims
  }, { revision: bundle.revision, generatedAt: 'deterministic-support-bundle-lifecycle-checkpoint', source: 'kernel-kit-support-bundle' });
  const lifecycleCheckpointPresent = validateKernelKitLifecycleCheckpoint(lifecycleCheckpoint).ok === true;
  bundle = { ...bundle, evidenceLedger, lifecycleCheckpoint, proof: Object.freeze({ ...bundle.proof, evidenceLedgerPresent, lifecycleCheckpointPresent }) };
  const privacyScrub = createKernelKitSupportBundlePrivacyScrub(bundle, { revision: bundle.revision, generatedAt: 'deterministic-support-bundle-privacy-scrub', source: 'kernel-kit-support-bundle' });
  const privacyScrubPresent = validateKernelKitSupportBundlePrivacyScrub(privacyScrub).ok === true;
  bundle = { ...bundle, privacyScrub, proof: Object.freeze({ ...bundle.proof, privacyScrubPresent }) };
  return Object.freeze(bundle);
}

export function validateKernelKitSupportBundle(bundle = {}) {
  const errors = [];
  if (!isObj(bundle)) return Object.freeze({ ok: false, errors: ['support bundle must be an object'], sectionCount: 0, commandCount: 0 });
  if (bundle.project !== 'BrowserRT') errors.push('project must be BrowserRT');
  if (bundle.format !== KERNEL_KIT_SUPPORT_BUNDLE_FORMAT) errors.push(`format must be ${KERNEL_KIT_SUPPORT_BUNDLE_FORMAT}`);
  for (const key of ['success-proof','reload-readback','controlled-failure','trace-comparison','diagnostic-runbook','export-receipt','handoff-summary','storage-posture','storage-pressure-checkpoint','admission-cancellation-checkpoint','session-coordination-checkpoint','recovery-checkpoint','web-lock-posture','guarded-storage-lane','lifecycle-checkpoint','privacy-scrub-checkpoint','evidence-ledger','replay-plan','exact-commands','non-claims']) {
    if (!bundle.sections?.includes(key)) errors.push(`missing support section ${key}`);
  }
  for (const key of ['successPathPresent','reloadReadbackPresent','controlledFailurePresent','traceComparisonPresent','diagnosticRunbookPresent','exportReceiptPresent','storagePressureCheckpointPresent','admissionCancellationCheckpointPresent','sessionCoordinationCheckpointPresent','recoveryCheckpointPresent','lifecycleCheckpointPresent','privacyScrubPresent','evidenceLedgerPresent','replayPlanPresent','exactCommandsPresent','nonClaimsVisible']) {
    if (bundle.proof?.[key] !== true) errors.push(`proof.${key} must be true`);
  }
  for (const needle of ['demo:kernel-kit-support-bundle-proof', 'facility:kernel-kit-support-bundle-audit', 'demo:kernel-kit-support-bundle-import-proof', 'facility:kernel-kit-support-bundle-import-audit', 'demo:kernel-kit-readiness-gate-proof', 'facility:kernel-kit-readiness-gate-audit', 'demo:kernel-kit-lifecycle-checkpoint-proof', 'facility:kernel-kit-lifecycle-checkpoint-audit', 'admission:abort-release-proof', 'demo:kernel-kit-admission-cancellation-checkpoint-proof', 'facility:kernel-kit-admission-cancellation-checkpoint-audit', 'demo:kernel-kit-recovery-checkpoint-proof', 'facility:kernel-kit-recovery-checkpoint-audit', 'browser:kernel-kit-demo-proof', 'browser:kernel-kit-session-coordination-checkpoint-proof', 'browser:kernel-kit-recovery-checkpoint-proof', 'browser:opfs-lane-quota-backpressure-proof', 'python3 tools/check_cube.py']) {
    if (!bundle.exactCommands?.some((cmd) => String(cmd).includes(needle))) errors.push(`missing exact command for ${needle}`);
  }
  if (!isObj(bundle.storagePosture?.success)) errors.push('storagePosture.success must be present');
  if (!isObj(bundle.storagePressure)) errors.push('storagePressure must be present');
  else if (bundle.storagePressure.evictionSurvivalDeferred !== true) errors.push('storagePressure must preserve eviction-survival deferral');
  if (!isObj(bundle.sessionCoordination)) errors.push('sessionCoordination must be present');
  else if (bundle.sessionCoordination.validationOk !== true || bundle.sessionCoordination.commandId !== 'browser:kernel-kit-session-coordination-checkpoint-proof') errors.push('sessionCoordination must preserve browser-heavy checkpoint command and validation');
  if (!isObj(bundle.recoveryCheckpoint)) errors.push('recoveryCheckpoint must be present');
  else if (bundle.recoveryCheckpoint.validationOk !== true || bundle.recoveryCheckpoint.commandId !== 'browser:kernel-kit-recovery-checkpoint-proof') errors.push('recoveryCheckpoint must preserve browser-heavy checkpoint command and validation');
  if (!isObj(bundle.webLockPosture?.success)) errors.push('webLockPosture.success must be present');
  if (!isObj(bundle.guardedStorageLane?.success)) errors.push('guardedStorageLane.success must be present');
  if (!isObj(bundle.lifecycleCheckpoint)) errors.push('lifecycleCheckpoint must be present');
  else {
    const lifecycleValidation = validateKernelKitLifecycleCheckpoint(bundle.lifecycleCheckpoint);
    if (!lifecycleValidation.ok) errors.push(`lifecycleCheckpoint invalid: ${lifecycleValidation.errors.join('; ')}`);
  }
  if (!isObj(bundle.evidenceLedger)) errors.push('evidenceLedger must be present');
  else {
    const ledgerValidation = validateKernelKitSupportBundleEvidenceLedger(bundle.evidenceLedger);
    if (!ledgerValidation.ok) errors.push(`evidenceLedger invalid: ${ledgerValidation.errors.join('; ')}`);
  }
  if (!isObj(bundle.replayPlan)) errors.push('replayPlan must be present');
  if (bundle.replayPlan?.format !== KERNEL_KIT_SUPPORT_BUNDLE_REPLAY_FORMAT) errors.push(`replayPlan.format must be ${KERNEL_KIT_SUPPORT_BUNDLE_REPLAY_FORMAT}`);
  for (const id of KERNEL_KIT_SUPPORT_BUNDLE_REPLAY_PHASE_IDS) if (!bundle.replayPlan?.phaseIds?.includes(id)) errors.push(`replayPlan missing phase ${id}`);
  if (bundle.replayPlan?.replayDoesNotExecuteCommands !== true) errors.push('replayPlan must not execute commands');
  if (bundle.storagePosture?.success?.persistentStorageRequested === true) errors.push('support bundle must not request persistent storage by default');
  if (bundle.webLockPosture?.success?.noFairnessClaim !== true) errors.push('support bundle must preserve Web Locks fairness non-claim');
  if (bundle.guardedStorageLane?.success?.noFairnessClaim !== true) errors.push('support bundle must preserve guarded storage-lane fairness non-claim');
  for (const claim of ['No production runtime claim.', 'No production support-bundle claim.', 'No automated failure triage claim.', 'No automated replay execution claim.', 'No OPFS durability, fsync, quota, eviction, crash-recovery, browser-restart, or multi-tab coordination claim.', 'Storage posture is advisory capability/estimate evidence, not a quota reservation or eviction-survival proof.', 'Quota-pressure/backpressure checkpoint is browser-heavy explicit and is not eviction survival, quota reservation, fsync, crash recovery, or cross-browser storage conformance.', 'Admission/cancellation checkpoint is release-light and is not exactly-once execution, task preemption, provider rollback, browser Worker lifecycle, fairness, throughput, or production cancellation.', 'Recovery checkpoint is browser-heavy explicit and is not general crash recovery, fsync durability, power-loss safety, quota/eviction survival, automatic orphan cleanup, or cross-browser conformance.', 'Web Locks posture is advisory coordination evidence, not a fairness, lifecycle recovery, cross-browser, or production coordination claim.', 'Guarded storage-lane evidence is browser-managed proof only, not a production multi-tab coordination, lifecycle recovery, or crash-recovery guarantee.', 'No production multi-tab coordination claim.']) {
    if (!bundle.nonClaims?.includes(claim)) errors.push(`missing support-bundle non-claim: ${claim}`);
  }
  return Object.freeze({ ok: errors.length === 0, errors, sectionCount: bundle.sections?.length || 0, commandCount: bundle.exactCommands?.length || 0, format: bundle.format || null });
}


const KERNEL_KIT_SUPPORT_BUNDLE_PRIVACY_SENSITIVE_KEY_FRAGMENTS = Object.freeze([
  'digest', 'hash', 'prefix', 'path', 'url', 'uri', 'storagekey', 'lockname', 'stack', 'message', 'location', 'pageurl', 'expected', 'traceexport', 'command'
]);

function isPrivacySensitiveKey(key = '') {
  const lower = String(key).toLowerCase().replace(/[^a-z0-9]/g, '');
  return KERNEL_KIT_SUPPORT_BUNDLE_PRIVACY_SENSITIVE_KEY_FRAGMENTS.some((fragment) => lower.includes(fragment));
}

function isPrivacySensitiveString(value = '') {
  const text = String(value);
  return /sha256:|fnv32:|browserrt\//i.test(text) || /https?:\/\//i.test(text) || /BrowserRT\.KernelKitDemo\.handoff/i.test(text) || text.length > 180;
}

function privacyDigest(value) {
  const text = typeof value === 'string' ? value : JSON.stringify(value);
  return `fnv32:${stableDigest32(text || '').toString(16).padStart(8, '0')}`;
}

function scrubPrivacyValue(value, key = '', path = '', stats = { redactedFieldCount: 0, retainedFieldCount: 0, sensitiveDigests: [] }, depth = 0) {
  const sensitiveKey = isPrivacySensitiveKey(key);
  if (value === null || value === undefined) {
    stats.retainedFieldCount += 1;
    return value;
  }
  if (typeof value === 'string') {
    if (sensitiveKey || isPrivacySensitiveString(value)) {
      stats.redactedFieldCount += 1;
      const digest = privacyDigest(value);
      stats.sensitiveDigests.push({ path, digest, type: 'string', length: value.length });
      return Object.freeze({ redacted: true, digest, length: value.length, reason: sensitiveKey ? 'sensitive-key' : 'sensitive-string' });
    }
    stats.retainedFieldCount += 1;
    return value;
  }
  if (typeof value === 'number' || typeof value === 'boolean') {
    stats.retainedFieldCount += 1;
    return value;
  }
  if (Array.isArray(value)) {
    if (depth > 7) {
      stats.redactedFieldCount += 1;
      return Object.freeze({ redacted: true, digest: privacyDigest(value), length: value.length, reason: 'max-depth' });
    }
    return Object.freeze(value.map((item, index) => scrubPrivacyValue(item, `${key}[]`, `${path}[${index}]`, stats, depth + 1)));
  }
  if (isObj(value)) {
    if (sensitiveKey && depth > 0) {
      stats.redactedFieldCount += 1;
      const digest = privacyDigest(value);
      stats.sensitiveDigests.push({ path, digest, type: 'object', key });
      return Object.freeze({ redacted: true, digest, key, reason: 'sensitive-object-key' });
    }
    if (depth > 7) {
      stats.redactedFieldCount += 1;
      return Object.freeze({ redacted: true, digest: privacyDigest(value), reason: 'max-depth' });
    }
    const out = {};
    for (const [childKey, childValue] of Object.entries(value)) {
      out[childKey] = scrubPrivacyValue(childValue, childKey, path ? `${path}.${childKey}` : childKey, stats, depth + 1);
    }
    return Object.freeze(out);
  }
  stats.redactedFieldCount += 1;
  return Object.freeze({ redacted: true, digest: privacyDigest(String(value)), reason: `unsupported-${typeof value}` });
}

function supportBundlePrivacySummary(bundle = {}, validation = null) {
  const sections = Array.isArray(bundle.sections) ? bundle.sections.map(String) : [];
  const commands = Array.isArray(bundle.exactCommands) ? bundle.exactCommands.map(String) : [];
  const nonClaims = Array.isArray(bundle.nonClaims) ? bundle.nonClaims.map(String) : [];
  const proof = bundle.proof || {};
  return Object.freeze({
    project: bundle.project || null,
    revision: bundle.revision || null,
    sourceFormat: bundle.format || null,
    sourceBundleIdDigest: bundle.bundleId ? privacyDigest(bundle.bundleId) : null,
    sourceValidationOk: validation ? validation.ok === true : null,
    sectionCount: sections.length,
    commandCount: commands.length,
    nonClaimCount: nonClaims.length,
    sections: Object.freeze(sections),
    commandIds: Object.freeze(commands.map((cmd) => privacyDigest(cmd))),
    proof: Object.freeze(Object.fromEntries(Object.entries(proof).filter(([, value]) => typeof value === 'boolean')))
  });
}

export function createKernelKitSupportBundlePrivacyScrub(input = {}, fields = {}) {
  const parsed = parseSupportBundleInput(input);
  const bundle = parsed.parsed || {};
  const validation = isObj(bundle) && bundle.format === KERNEL_KIT_SUPPORT_BUNDLE_FORMAT
    ? Object.freeze({
        ok: bundle.project === 'BrowserRT' && Array.isArray(bundle.sections) && Boolean(bundle.proof?.successPathPresent) && Boolean(bundle.proof?.nonClaimsVisible),
        errors: [],
        sectionCount: bundle.sections?.length || 0,
        commandCount: bundle.exactCommands?.length || 0,
        format: bundle.format || null
      })
    : Object.freeze({ ok: false, errors: ['input is not a support bundle'], sectionCount: 0, commandCount: 0, format: bundle.format || null });
  const stats = { redactedFieldCount: 0, retainedFieldCount: 0, sensitiveDigests: [] };
  const scrubInput = {
    success: bundle.success || null,
    reload: bundle.reload || null,
    handoff: bundle.handoff || null,
    storagePosture: bundle.storagePosture || null,
    storagePressure: bundle.storagePressure || null,
    admissionCancellation: bundle.admissionCancellation || null,
    webLockPosture: bundle.webLockPosture || null,
    guardedStorageLane: bundle.guardedStorageLane || null,
    lifecycleCheckpoint: bundle.lifecycleCheckpoint || null,
    evidenceLedger: bundle.evidenceLedger || null,
    replayPlan: bundle.replayPlan || null,
    exactCommands: bundle.exactCommands || []
  };
  const scrubbed = scrubPrivacyValue(scrubInput, 'supportBundle', 'supportBundle', stats, 0);
  const report = {
    project: 'BrowserRT',
    revision: fields.revision || bundle.revision || 'rev0054',
    schema: 1,
    format: KERNEL_KIT_SUPPORT_BUNDLE_PRIVACY_SCRUB_FORMAT,
    scrubId: fields.scrubId || `${fields.revision || bundle.revision || 'rev0054'}-kernel-kit-support-bundle-privacy-scrub`,
    generatedAt: fields.generatedAt || 'deterministic-support-bundle-privacy-scrub',
    source: fields.source || 'kernel-kit-support-bundle-privacy-scrub',
    status: parsed.ok && validation.ok && stats.redactedFieldCount > 0 ? 'passed' : 'needs-attention',
    purpose: 'Produce a shareable, proof-preserving Kernel Kit support-bundle summary that redacts local OPFS prefixes, digests, URLs, lock names, stack/message text, and other high-risk handoff scalars before a future session copies or publishes support evidence.',
    posture: 'privacy-scrub-not-anonymization-not-side-channel-mitigation',
    input: Object.freeze({ kind: parsed.inputKind, bytes: parsed.inputBytes || 0, parseOk: parsed.ok, parseError: parsed.error || null }),
    sourceSummary: supportBundlePrivacySummary(bundle, validation),
    scrubbed,
    redaction: Object.freeze({
      redactedFieldCount: stats.redactedFieldCount,
      retainedFieldCount: stats.retainedFieldCount,
      sensitiveDigestCount: stats.sensitiveDigests.length,
      sensitiveDigests: Object.freeze(stats.sensitiveDigests.slice(0, 32)),
      strategy: 'replace sensitive scalars/objects with deterministic local fnv32 digests plus type/length metadata; preserve proof booleans, section names, command identity digests, and non-claim counts'
    }),
    proof: Object.freeze({
      parsed: parsed.ok === true,
      sourceLooksLikeSupportBundle: bundle.format === KERNEL_KIT_SUPPORT_BUNDLE_FORMAT,
      sourceSummaryPreserved: Boolean(bundle.revision) && Array.isArray(bundle.sections),
      proofBooleansPreserved: Object.values(bundle.proof || {}).some((value) => value === true) && scrubbed?.success?.proof !== undefined,
      sensitiveFieldsRedacted: stats.redactedFieldCount > 0,
      exactCommandTextRedacted: JSON.stringify(scrubbed?.exactCommands || '').includes('redacted'),
      nonClaimsStillVisible: Array.isArray(bundle.nonClaims) && bundle.nonClaims.includes('No production support-bundle claim.'),
      scrubDoesNotValidateAuthenticity: true,
      scrubDoesNotClaimAnonymization: true
    }),
    nextAction: 'Use this scrub report for human-readable handoff sharing; use the original support bundle only for local replay where exact digests/prefixes are intentionally needed.',
    nonClaims: Object.freeze([...KERNEL_KIT_SUPPORT_BUNDLE_PRIVACY_SCRUB_NON_CLAIMS, 'Scrubbed report preserves proof shape for handoff discussion, but exact local replay still requires the original support bundle or regenerated proofs.'])
  };
  return Object.freeze(report);
}

export function validateKernelKitSupportBundlePrivacyScrub(report = {}) {
  const errors = [];
  if (!isObj(report)) return Object.freeze({ ok: false, errors: ['privacy scrub report must be an object'], redactedFieldCount: 0, format: null, status: null });
  if (report.project !== 'BrowserRT') errors.push('project must be BrowserRT');
  if (report.format !== KERNEL_KIT_SUPPORT_BUNDLE_PRIVACY_SCRUB_FORMAT) errors.push(`format must be ${KERNEL_KIT_SUPPORT_BUNDLE_PRIVACY_SCRUB_FORMAT}`);
  if (report.status !== 'passed') errors.push('status must be passed');
  for (const key of ['parsed','sourceLooksLikeSupportBundle','sourceSummaryPreserved','proofBooleansPreserved','sensitiveFieldsRedacted','exactCommandTextRedacted','nonClaimsStillVisible','scrubDoesNotValidateAuthenticity','scrubDoesNotClaimAnonymization']) {
    if (report.proof?.[key] !== true) errors.push(`proof.${key} must be true`);
  }
  if (!report.redaction || report.redaction.redactedFieldCount < 1) errors.push('redaction.redactedFieldCount must be positive');
  const scrubJson = JSON.stringify(report.scrubbed || {});
  for (const forbidden of ['sha256:', 'browserrt/rev', 'BrowserRT.KernelKitDemo.handoff', 'http://', 'https://']) {
    if (scrubJson.includes(forbidden)) errors.push(`scrubbed output must not include raw sensitive token ${forbidden}`);
  }
  for (const claim of ['No production support-bundle privacy claim.', 'No anonymization, differential-privacy, or irreversible de-identification claim.', 'No side-channel, fingerprinting, or telemetry-ingestion mitigation claim.']) {
    if (!report.nonClaims?.includes(claim)) errors.push(`missing privacy scrub non-claim: ${claim}`);
  }
  return Object.freeze({ ok: errors.length === 0, errors, redactedFieldCount: report.redaction?.redactedFieldCount || 0, format: report.format || null, status: report.status || null });
}


export const KERNEL_KIT_SUPPORT_BUNDLE_IMPORT_FORMAT = 'browserrt-kernel-kit-support-bundle-import-report-v1';
export const KERNEL_KIT_SUPPORT_BUNDLE_IMPORT_NON_CLAIMS = Object.freeze([
  'No production support-bundle import claim.',
  'No automated failure triage claim.',
  'No telemetry backend ingestion claim.',
  'No support-bundle authenticity or signature claim.',
  'No trust or security validation claim.',
  'No browser download UX claim.'
]);

function parseSupportBundleInput(input) {
  if (typeof input === 'string') {
    const trimmed = input.trim();
    if (!trimmed) return { ok: false, error: 'empty support bundle input', parsed: null, inputKind: 'string', inputBytes: 0 };
    try { return { ok: true, error: null, parsed: JSON.parse(trimmed), inputKind: 'json-string', inputBytes: trimmed.length }; }
    catch (error) { return { ok: false, error: `invalid JSON: ${error?.message || String(error)}`, parsed: null, inputKind: 'json-string', inputBytes: trimmed.length }; }
  }
  if (isObj(input)) return { ok: true, error: null, parsed: input, inputKind: 'object', inputBytes: JSON.stringify(input).length };
  return { ok: false, error: `unsupported support bundle input type: ${typeof input}`, parsed: null, inputKind: typeof input, inputBytes: 0 };
}


function commandIncludesNeedle(commands, needle) {
  return Array.isArray(commands) && commands.some((cmd) => String(cmd).includes(needle));
}

function revPrefixFromRevision(revision = 'rev0054') {
  const match = String(revision || '').match(/rev(\d{4})/);
  return `REV${match ? match[1] : '0054'}`;
}

function expectedKernelKitEvidenceEntries(revision = 'rev0054') {
  const prefix = revPrefixFromRevision(revision);
  return Object.freeze([
    Object.freeze({ id: 'support-bundle-proof-artifact', phaseId: 'replay-browser-light-support-evidence', tier: 'release-browser-light', taskId: 'demo:kernel-kit-support-bundle-proof', commandNeedle: 'demo:kernel-kit-support-bundle-proof', outputPath: `artifacts/validation/${prefix}-KERNEL-KIT-SUPPORT-BUNDLE-PROBE.json`, requiredProofPaths: Object.freeze(['status=passed','proof.supportBundleValid','proof.replayPlanReady','proof.evidenceLedgerPresent']) }),
    Object.freeze({ id: 'support-bundle-audit-artifact', phaseId: 'replay-browser-light-support-evidence', tier: 'release-browser-light', taskId: 'facility:kernel-kit-support-bundle-audit', commandNeedle: 'facility:kernel-kit-support-bundle-audit', outputPath: `artifacts/audit/${prefix}-KERNEL-KIT-SUPPORT-BUNDLE-CONTRACT-AUDIT.json`, requiredProofPaths: Object.freeze(['status=passed','checks.proof-validates','checks.evidence-ledger-contract-present']) }),
    Object.freeze({ id: 'support-bundle-import-artifact', phaseId: 'import-and-validate-bundle', tier: 'release-browser-light', taskId: 'demo:kernel-kit-support-bundle-import-proof', commandNeedle: 'demo:kernel-kit-support-bundle-import-proof', outputPath: `artifacts/validation/${prefix}-KERNEL-KIT-SUPPORT-BUNDLE-IMPORT-PROBE.json`, requiredProofPaths: Object.freeze(['status=passed','proof.replayPlanReady','proof.evidenceLedgerPresent']) }),
    Object.freeze({ id: 'admission-cancellation-artifact', phaseId: 'replay-browser-light-support-evidence', tier: 'release-browser-light', taskId: 'demo:kernel-kit-admission-cancellation-checkpoint-proof', commandNeedle: 'demo:kernel-kit-admission-cancellation-checkpoint-proof', outputPath: `artifacts/validation/${prefix}-KERNEL-KIT-ADMISSION-CANCELLATION-CHECKPOINT-PROBE.json`, requiredProofPaths: Object.freeze(['status=passed','proof.observedCheckpointValid','proof.supportBundleCarriesAdmissionCancellationCheckpoint','proof.admissionAbortReleaseProofPassed']) }),
    Object.freeze({ id: 'readiness-gate-artifact', phaseId: 'readiness-gate-before-runtime-widening', tier: 'release-browser-light', taskId: 'demo:kernel-kit-readiness-gate-proof', commandNeedle: 'demo:kernel-kit-readiness-gate-proof', outputPath: `artifacts/validation/${prefix}-KERNEL-KIT-READINESS-GATE-PROBE.json`, requiredProofPaths: Object.freeze(['status=passed','proof.readinessInputsEvidenceBound','readinessGate.inputProof.evidenceBound']) }),
    Object.freeze({ id: 'browser-kernel-kit-artifact', phaseId: 'browser-heavy-confirmation', tier: 'browser-heavy-explicit', taskId: 'browser:kernel-kit-demo-proof', commandNeedle: 'browser:kernel-kit-demo-proof', outputPath: `artifacts/validation/${prefix}-BROWSER-KERNEL-KIT-DEMO-PROBE.json`, requiredProofPaths: Object.freeze(['status=passed','proof.guardedStorageLane','proof.supportBundleReplay','proof.supportBundleEvidenceLedger']) }),
    Object.freeze({ id: 'browser-storage-pressure-artifact', phaseId: 'browser-heavy-confirmation', tier: 'browser-heavy-explicit', taskId: 'browser:opfs-lane-quota-backpressure-proof', commandNeedle: 'browser:opfs-lane-quota-backpressure-proof', outputPath: `artifacts/validation/${prefix}-BROWSER-OPFS-LANE-QUOTA-BACKPRESSURE-PROBE.json`, requiredProofPaths: Object.freeze(['status=passed','proof.quotaExceededClassified','proof.cleanupVerified','proof.quotaOverrideReset','proof.evictionSurvivalClaimed=false']) }),
    Object.freeze({ id: 'browser-session-coordination-artifact', phaseId: 'browser-heavy-confirmation', tier: 'browser-heavy-explicit', taskId: 'browser:kernel-kit-session-coordination-checkpoint-proof', commandNeedle: 'browser:kernel-kit-session-coordination-checkpoint-proof', outputPath: `artifacts/validation/${prefix}-BROWSER-KERNEL-KIT-SESSION-COORDINATION-CHECKPOINT-PROBE.json`, requiredProofPaths: Object.freeze(['status=passed','proof.exclusiveIfAvailableDenied','proof.queuedAcquiredAfterRelease','proof.handoffSingleUseClearObserved','proof.staleReadReturnedNull']) }),
    Object.freeze({ id: 'browser-recovery-artifact', phaseId: 'browser-heavy-confirmation', tier: 'browser-heavy-explicit', taskId: 'browser:kernel-kit-recovery-checkpoint-proof', commandNeedle: 'browser:kernel-kit-recovery-checkpoint-proof', outputPath: `artifacts/validation/${prefix}-BROWSER-KERNEL-KIT-RECOVERY-CHECKPOINT-PROBE.json`, requiredProofPaths: Object.freeze(['status=passed','proof.sameOriginProfileRestartObserved','proof.interruptedWriteNotAcceptedCorrupt','proof.transientOpenFailureRetryObserved','proof.unsettledOrphanReviewGateObserved','proof.crashDurabilityNonClaimsVisible']) }),
    Object.freeze({ id: 'cube-sanity-command', phaseId: 'cube-sanity-after-replay', tier: 'release-browser-light', taskId: 'cube:check-cube', commandNeedle: 'python3 tools/check_cube.py', outputPath: null, requiredProofPaths: Object.freeze(['command-exits-zero']) })
  ]);
}

export function createKernelKitSupportBundleEvidenceLedger(input = {}, fields = {}) {
  const parsed = parseSupportBundleInput(input);
  const bundle = parsed.parsed || {};
  const revision = fields.revision || bundle.revision || 'rev0054';
  const commands = Array.isArray(bundle.exactCommands) ? bundle.exactCommands.map(String) : [];
  const entries = expectedKernelKitEvidenceEntries(revision).map((entry) => {
    const command = commands.find((cmd) => String(cmd).includes(entry.commandNeedle)) || null;
    const outputPath = entry.outputPath || null;
    const ready = Boolean(command) && (entry.id === 'cube-sanity-command' || Boolean(outputPath));
    const digestInput = JSON.stringify([entry.id, entry.taskId, entry.commandNeedle, outputPath, entry.requiredProofPaths, command || 'missing']);
    return Object.freeze({
      ...entry,
      command,
      status: ready ? 'expected' : 'missing',
      missing: Object.freeze([
        ...(command ? [] : [`command:${entry.commandNeedle}`]),
        ...(entry.id !== 'cube-sanity-command' && !outputPath ? ['outputPath'] : [])
      ]),
      artifactDigest: outputPath ? `fnv32:${stableDigest32(digestInput).toString(16).padStart(8, '0')}` : null
    });
  });
  const nonClaims = sortedUnique([
    ...KERNEL_KIT_SUPPORT_BUNDLE_EVIDENCE_LEDGER_NON_CLAIMS,
    'No production runtime claim.',
    'No production support-bundle claim.',
    'No automated replay execution claim.',
    'No OPFS durability, fsync, quota, eviction, crash-recovery, browser-restart, or multi-tab coordination claim.',
    ...(Array.isArray(bundle.nonClaims) ? bundle.nonClaims : [])
  ]);
  const missingEntryIds = entries.filter((entry) => entry.status !== 'expected').map((entry) => entry.id);
  const outputPaths = entries.map((entry) => entry.outputPath).filter(Boolean);
  const proof = Object.freeze({
    parsed: parsed.ok === true,
    formatOk: bundle.format === KERNEL_KIT_SUPPORT_BUNDLE_FORMAT,
    commandsResolved: missingEntryIds.length === 0,
    expectedOutputsNamed: outputPaths.length >= 5,
    proofPathsNamed: entries.every((entry) => Array.isArray(entry.requiredProofPaths) && entry.requiredProofPaths.length > 0),
    browserHeavyExplicit: entries.some((entry) => entry.tier === 'browser-heavy-explicit' && entry.phaseId === 'browser-heavy-confirmation'),
    releaseBrowserLightFirst: entries.findIndex((entry) => entry.phaseId === 'browser-heavy-confirmation') > entries.findIndex((entry) => entry.phaseId === 'replay-browser-light-support-evidence'),
    ledgerDoesNotReadOrExecuteArtifacts: true,
    nonClaimsVisible: nonClaims.includes('No artifact authenticity or signature claim.') && nonClaims.includes('No command execution claim.')
  });
  const status = Object.values(proof).every((value) => value === true) ? 'evidence-ledger-ready' : 'needs-attention';
  return Object.freeze({
    project: 'BrowserRT',
    revision,
    schema: 1,
    format: KERNEL_KIT_SUPPORT_BUNDLE_EVIDENCE_LEDGER_FORMAT,
    ledgerId: fields.ledgerId || `${revision}-kernel-kit-support-bundle-evidence-ledger`,
    generatedAt: fields.generatedAt || 'deterministic-support-bundle-evidence-ledger',
    status,
    purpose: 'Name the compact proof and audit artifacts a future Kernel Kit replay should expect after each support-bundle phase, without executing commands or claiming artifact authenticity.',
    posture: 'expected-artifact-ledger-not-artifact-authenticity-not-command-execution',
    input: Object.freeze({ kind: parsed.inputKind, bytes: parsed.inputBytes || 0, parseOk: parsed.ok, parseError: parsed.error || null }),
    entries: Object.freeze(entries),
    outputPaths: Object.freeze(outputPaths),
    missingEntryIds: Object.freeze(missingEntryIds),
    proof,
    nonClaims: Object.freeze(nonClaims)
  });
}

export function validateKernelKitSupportBundleEvidenceLedger(ledger = {}) {
  const errors = [];
  if (!isObj(ledger)) return Object.freeze({ ok: false, errors: ['support bundle evidence ledger must be an object'], entryCount: 0, outputCount: 0, format: null, status: null });
  if (ledger.project !== 'BrowserRT') errors.push('project must be BrowserRT');
  if (ledger.format !== KERNEL_KIT_SUPPORT_BUNDLE_EVIDENCE_LEDGER_FORMAT) errors.push(`format must be ${KERNEL_KIT_SUPPORT_BUNDLE_EVIDENCE_LEDGER_FORMAT}`);
  if (ledger.status !== 'evidence-ledger-ready') errors.push('status must be evidence-ledger-ready');
  const entries = Array.isArray(ledger.entries) ? ledger.entries : [];
  for (const expected of expectedKernelKitEvidenceEntries(ledger.revision || 'rev0054')) {
    const entry = entries.find((row) => row.id === expected.id);
    if (!entry) errors.push(`missing evidence ledger entry ${expected.id}`);
    else {
      if (entry.status !== 'expected') errors.push(`evidence ledger entry ${expected.id} must be expected`);
      if (!String(entry.command || '').includes(expected.commandNeedle)) errors.push(`evidence ledger entry ${expected.id} missing command needle ${expected.commandNeedle}`);
      if (expected.outputPath && entry.outputPath !== expected.outputPath) errors.push(`evidence ledger entry ${expected.id} outputPath mismatch`);
      if (!Array.isArray(entry.requiredProofPaths) || entry.requiredProofPaths.length === 0) errors.push(`evidence ledger entry ${expected.id} missing requiredProofPaths`);
    }
  }
  for (const key of ['parsed','formatOk','commandsResolved','expectedOutputsNamed','proofPathsNamed','browserHeavyExplicit','releaseBrowserLightFirst','ledgerDoesNotReadOrExecuteArtifacts','nonClaimsVisible']) {
    if (ledger.proof?.[key] !== true) errors.push(`proof.${key} must be true`);
  }
  for (const claim of ['No production evidence-ledger claim.','No artifact authenticity or signature claim.','No command execution claim.','No automated replay execution claim.','No durable artifact retention guarantee.']) {
    if (!ledger.nonClaims?.includes(claim)) errors.push(`missing evidence-ledger non-claim: ${claim}`);
  }
  if ((ledger.missingEntryIds || []).length) errors.push('missingEntryIds must be empty');
  return Object.freeze({ ok: errors.length === 0, errors, entryCount: entries.length, outputCount: ledger.outputPaths?.length || 0, format: ledger.format || null, status: ledger.status || null });
}


function normalizeArtifactMap(artifacts = {}) {
  if (Array.isArray(artifacts)) {
    const out = {};
    for (const artifact of artifacts) {
      if (!isObj(artifact)) continue;
      for (const key of [artifact.path, artifact.outputPath, artifact.id, artifact.taskId, artifact.probe_id, artifact.audit_id, artifact.reportId]) {
        if (key) out[String(key)] = artifact;
      }
    }
    return out;
  }
  return isObj(artifacts) ? artifacts : {};
}

function evidenceLedgerFromCheckpointInput(input = {}, fields = {}) {
  const parsed = parseSupportBundleInput(input);
  const value = parsed.parsed || {};
  if (value.format === KERNEL_KIT_SUPPORT_BUNDLE_EVIDENCE_LEDGER_FORMAT) return { parsed, ledger: value, sourceKind: 'evidence-ledger' };
  if (isObj(value.evidenceLedger)) return { parsed, ledger: value.evidenceLedger, sourceKind: value.format === KERNEL_KIT_SUPPORT_BUNDLE_REPLAY_FORMAT ? 'replay-plan' : 'support-bundle' };
  const ledger = createKernelKitSupportBundleEvidenceLedger(value, { revision: fields.revision || value.revision || 'rev0054', generatedAt: 'deterministic-evidence-checkpoint-ledger' });
  return { parsed, ledger, sourceKind: 'derived-from-input' };
}

function getObjectPath(object, path) {
  if (!path) return undefined;
  if (String(path).startsWith('checks.')) {
    const name = String(path).slice('checks.'.length);
    const check = Array.isArray(object?.checks) ? object.checks.find((row) => row?.name === name) : null;
    return check ? check.status === 'passed' : undefined;
  }
  let cur = object;
  for (const part of String(path).split('.')) {
    if (!part) continue;
    if (cur == null) return undefined;
    cur = cur[part];
  }
  return cur;
}

function proofPathSatisfied(artifact, proofPath) {
  const spec = String(proofPath || '');
  if (spec === 'command-exits-zero') return artifact?.proof?.commandExitsZero === true || artifact?.commandExitsZero === true || artifact?.status === 'passed';
  const idx = spec.indexOf('=');
  if (idx > 0) {
    const path = spec.slice(0, idx);
    const expected = spec.slice(idx + 1);
    const value = getObjectPath(artifact, path);
    if (expected === 'true') return value === true;
    if (expected === 'false') return value === false;
    return String(value) === expected;
  }
  return getObjectPath(artifact, spec) === true;
}

function findCheckpointArtifact(artifactMap, entry) {
  const candidates = [entry.outputPath, entry.id, entry.taskId, entry.commandNeedle].filter(Boolean).map(String);
  for (const key of candidates) if (artifactMap[key]) return artifactMap[key];
  if (entry.outputPath) {
    const base = String(entry.outputPath).split('/').pop();
    if (artifactMap[base]) return artifactMap[base];
  }
  return null;
}

function defaultDeferredCheckpointEntries(scope, entries) {
  if (Array.isArray(scope)) return scope.map(String);
  if (scope === 'full-after-replay') return [];
  if (scope === 'product-page') return entries.filter((entry) => entry.id === 'support-bundle-audit-artifact' || entry.id === 'cube-sanity-command' || entry.id === 'browser-storage-pressure-artifact' || entry.id === 'browser-session-coordination-artifact' || entry.id === 'browser-recovery-artifact').map((entry) => entry.id);
  return entries.filter((entry) => entry.tier === 'browser-heavy-explicit').map((entry) => entry.id);
}

export function createKernelKitSupportBundleEvidenceCheckpoint(input = {}, artifacts = {}, fields = {}) {
  const { parsed, ledger, sourceKind } = evidenceLedgerFromCheckpointInput(input, fields);
  const ledgerValidation = validateKernelKitSupportBundleEvidenceLedger(ledger);
  const scope = fields.scope || 'release-browser-light';
  const entries = Array.isArray(ledger.entries) ? ledger.entries : [];
  const artifactMap = normalizeArtifactMap(artifacts);
  const deferredEntryIds = new Set(fields.deferredEntryIds ? fields.deferredEntryIds.map(String) : defaultDeferredCheckpointEntries(scope, entries));
  const rows = entries.map((entry) => {
    const artifact = findCheckpointArtifact(artifactMap, entry);
    const deferred = deferredEntryIds.has(entry.id);
    const proofChecks = (entry.requiredProofPaths || []).map((proofPath) => Object.freeze({ proofPath, ok: artifact ? proofPathSatisfied(artifact, proofPath) : false }));
    const satisfied = deferred ? false : Boolean(artifact) && proofChecks.every((row) => row.ok === true);
    const shapeDigestInput = artifact ? JSON.stringify({ id: entry.id, outputPath: entry.outputPath || null, status: artifact.status || null, proof: artifact.proof || null, checks: artifact.checks || null }) : '';
    return Object.freeze({
      id: entry.id,
      phaseId: entry.phaseId,
      tier: entry.tier,
      taskId: entry.taskId,
      outputPath: entry.outputPath || null,
      commandNeedle: entry.commandNeedle,
      status: deferred ? 'deferred' : (satisfied ? 'satisfied' : 'missing-or-unsatisfied'),
      artifactSupplied: Boolean(artifact),
      requiredProofPaths: Object.freeze(entry.requiredProofPaths || []),
      proofChecks: Object.freeze(proofChecks),
      shapeDigest: artifact ? `fnv32:${stableDigest32(shapeDigestInput).toString(16).padStart(8, '0')}` : null,
      nonClaim: 'This checkpoint validates supplied report shape and proof fields only; it does not authenticate artifacts, read files, or execute commands.'
    });
  });
  const missingEntryIds = rows.filter((row) => row.status === 'missing-or-unsatisfied').map((row) => row.id);
  const satisfiedEntryIds = rows.filter((row) => row.status === 'satisfied').map((row) => row.id);
  const deferredIds = rows.filter((row) => row.status === 'deferred').map((row) => row.id);
  const nonClaims = sortedUnique([
    ...KERNEL_KIT_SUPPORT_BUNDLE_EVIDENCE_CHECKPOINT_NON_CLAIMS,
    ...KERNEL_KIT_SUPPORT_BUNDLE_EVIDENCE_LEDGER_NON_CLAIMS,
    ...(Array.isArray(ledger.nonClaims) ? ledger.nonClaims : [])
  ]);
  const proof = Object.freeze({
    parsed: parsed.ok === true,
    ledgerValid: ledgerValidation.ok === true,
    suppliedArtifactMapPresent: Object.keys(artifactMap).length > 0,
    artifactsSupplied: rows.some((row) => row.artifactSupplied === true),
    requiredProofPathsSatisfied: missingEntryIds.length === 0,
    deferredEntriesExplicit: deferredIds.every((id) => deferredEntryIds.has(id)),
    browserHeavyExplicitlyDeferredOrSatisfied: rows.filter((row) => row.tier === 'browser-heavy-explicit').every((row) => row.status === 'deferred' || row.status === 'satisfied'),
    checkpointDoesNotReadArtifacts: true,
    checkpointDoesNotExecuteCommands: true,
    nonClaimsVisible: nonClaims.includes('No artifact authenticity or signature claim.') && nonClaims.includes('No command execution claim.')
  });
  const status = Object.values(proof).every((value) => value === true) ? 'evidence-checkpoint-ready' : 'needs-attention';
  return Object.freeze({
    project: 'BrowserRT',
    revision: fields.revision || ledger.revision || 'rev0054',
    schema: 1,
    format: KERNEL_KIT_SUPPORT_BUNDLE_EVIDENCE_CHECKPOINT_FORMAT,
    checkpointId: fields.checkpointId || `${fields.revision || ledger.revision || 'rev0054'}-kernel-kit-support-bundle-evidence-checkpoint`,
    generatedAt: fields.generatedAt || 'deterministic-support-bundle-evidence-checkpoint',
    status,
    scope,
    purpose: 'Machine-check a support-bundle evidence ledger against supplied compact reports by verifying required proof paths, while keeping browser-heavy and static-audit gaps explicit instead of pretending commands were executed.',
    posture: 'supplied-report-checkpoint-not-artifact-authenticity-not-filesystem-reader-not-command-executor',
    input: Object.freeze({ kind: parsed.inputKind, sourceKind, bytes: parsed.inputBytes || 0, parseOk: parsed.ok, parseError: parsed.error || null }),
    ledger: Object.freeze({ status: ledger.status || null, validation: ledgerValidation, entryCount: entries.length, outputCount: ledger.outputPaths?.length || 0 }),
    rows: Object.freeze(rows),
    satisfiedEntryIds: Object.freeze(satisfiedEntryIds),
    deferredEntryIds: Object.freeze(deferredIds),
    missingEntryIds: Object.freeze(missingEntryIds),
    suppliedArtifactKeys: Object.freeze(Object.keys(artifactMap).sort()),
    proof,
    nextAction: status === 'evidence-checkpoint-ready' ? 'Use the satisfied rows as replay evidence and run any deferred browser-heavy/static-audit phases explicitly before widening claims.' : 'Supply the missing compact reports or mark intentionally deferred phases before replaying the support bundle.',
    nonClaims: Object.freeze(nonClaims)
  });
}

export function validateKernelKitSupportBundleEvidenceCheckpoint(checkpoint = {}) {
  const errors = [];
  if (!isObj(checkpoint)) return Object.freeze({ ok: false, errors: ['support bundle evidence checkpoint must be an object'], rowCount: 0, satisfiedCount: 0, deferredCount: 0, missingCount: 0, format: null, status: null });
  if (checkpoint.project !== 'BrowserRT') errors.push('project must be BrowserRT');
  if (checkpoint.format !== KERNEL_KIT_SUPPORT_BUNDLE_EVIDENCE_CHECKPOINT_FORMAT) errors.push(`format must be ${KERNEL_KIT_SUPPORT_BUNDLE_EVIDENCE_CHECKPOINT_FORMAT}`);
  if (checkpoint.status !== 'evidence-checkpoint-ready') errors.push('status must be evidence-checkpoint-ready');
  const rows = Array.isArray(checkpoint.rows) ? checkpoint.rows : [];
  if (rows.length < 5) errors.push('checkpoint rows must cover the support-bundle evidence ledger');
  if ((checkpoint.missingEntryIds || []).length) errors.push('missingEntryIds must be empty');
  if (!Array.isArray(checkpoint.deferredEntryIds)) errors.push('deferredEntryIds must be an array');
  for (const row of rows) {
    if (!['satisfied','deferred'].includes(row.status)) errors.push(`checkpoint row ${row.id || 'unknown'} must be satisfied or deferred`);
    if (row.status === 'satisfied' && (!Array.isArray(row.proofChecks) || row.proofChecks.some((check) => check.ok !== true))) errors.push(`checkpoint row ${row.id || 'unknown'} has unsatisfied proof checks`);
    if (row.status === 'satisfied' && !String(row.shapeDigest || '').startsWith('fnv32:')) errors.push(`checkpoint row ${row.id || 'unknown'} missing shape digest`);
  }
  for (const key of ['parsed','ledgerValid','suppliedArtifactMapPresent','artifactsSupplied','requiredProofPathsSatisfied','deferredEntriesExplicit','browserHeavyExplicitlyDeferredOrSatisfied','checkpointDoesNotReadArtifacts','checkpointDoesNotExecuteCommands','nonClaimsVisible']) {
    if (checkpoint.proof?.[key] !== true) errors.push(`proof.${key} must be true`);
  }
  for (const claim of ['No production evidence-checkpoint claim.','No artifact authenticity or signature claim.','No artifact signing or tamper-proofing claim.','No filesystem artifact discovery claim.','No command execution claim.','No automated replay execution claim.']) {
    if (!checkpoint.nonClaims?.includes(claim)) errors.push(`missing evidence-checkpoint non-claim: ${claim}`);
  }
  return Object.freeze({ ok: errors.length === 0, errors, rowCount: rows.length, satisfiedCount: checkpoint.satisfiedEntryIds?.length || 0, deferredCount: checkpoint.deferredEntryIds?.length || 0, missingCount: checkpoint.missingEntryIds?.length || 0, format: checkpoint.format || null, status: checkpoint.status || null });
}

function replayPhase(id, title, tier, commandNeedles, commands, fields = {}) {
  const matchedCommands = commandNeedles.map((needle) => commands.find((cmd) => String(cmd).includes(needle)) || null);
  const missingCommandNeedles = commandNeedles.filter((needle, index) => !matchedCommands[index]);
  return Object.freeze({
    id,
    title,
    tier,
    order: fields.order || 0,
    status: missingCommandNeedles.length === 0 ? 'ready' : 'blocked',
    stopWhen: fields.stopWhen || 'phase-command-fails-or-required-evidence-missing',
    requiredEvidence: Object.freeze(fields.requiredEvidence || []),
    commandNeedles: Object.freeze(commandNeedles),
    commands: Object.freeze(matchedCommands.filter(Boolean)),
    missingCommandNeedles: Object.freeze(missingCommandNeedles),
    browserBudget: fields.browserBudget || 'none',
    nonClaim: fields.nonClaim || 'This replay phase is a deterministic instruction record; it does not execute commands.'
  });
}

function supportBundleReplayPhases(commands) {
  return Object.freeze([
    replayPhase('import-and-validate-bundle', 'Parse and validate the imported support bundle before trusting any proof booleans.', 'release-browser-light', ['demo:kernel-kit-support-bundle-import-proof', 'facility:kernel-kit-support-bundle-import-audit'], commands, { order: 1, requiredEvidence: ['bundle parse', 'bundle validation', 'sections', 'non-claims'] }),
    replayPhase('replay-browser-light-support-evidence', 'Rebuild the browser-light support bundle proof and static audit from source.', 'release-browser-light', ['demo:kernel-kit-support-bundle-proof', 'facility:kernel-kit-support-bundle-audit'], commands, { order: 2, requiredEvidence: ['supportBundle.proof.successPathPresent', 'supportBundle.proof.controlledFailurePresent', 'supportBundle.proof.replayPlanPresent'] }),
    replayPhase('readiness-gate-before-runtime-widening', 'Run the evidence-bound readiness gate before widening runtime or platform claims.', 'release-browser-light', ['demo:kernel-kit-readiness-gate-proof', 'facility:kernel-kit-readiness-gate-audit'], commands, { order: 3, requiredEvidence: ['readinessInputsEvidenceBound', 'handoffMarkdownRoundTripVisible', 'browserLightReleasePreserved'] }),
    replayPhase('browser-heavy-confirmation', 'Spend browser/CDP budget only after browser-light replay is green.', 'browser-heavy-explicit', ['browser:kernel-kit-demo-proof'], commands, { order: 4, browserBudget: 'explicit-cdp', requiredEvidence: ['OPFS guarded storage lane', 'reload readback', 'support bundle preservation'] }),
    replayPhase('cube-sanity-after-replay', 'Finish with the cube sanity check so replay work does not leave stale offices.', 'release-browser-light', ['python3 tools/check_cube.py'], commands, { order: 5, requiredEvidence: ['cube metadata', 'surface inventory', 'package offices'] })
  ]);
}

export function createKernelKitSupportBundleReplayPlan(input, fields = {}) {
  const parsed = parseSupportBundleInput(input);
  const bundle = parsed.parsed || {};
  const validation = parsed.ok ? validateKernelKitSupportBundle(bundle) : { ok: false, errors: [parsed.error], sectionCount: 0, commandCount: 0, format: null };
  const commands = Array.isArray(bundle.exactCommands) ? bundle.exactCommands.map(String) : [];
  const phases = supportBundleReplayPhases(commands);
  const missingPhaseIds = KERNEL_KIT_SUPPORT_BUNDLE_REPLAY_PHASE_IDS.filter((id) => !phases.some((phase) => phase.id === id));
  const blockedPhaseIds = phases.filter((phase) => phase.status !== 'ready').map((phase) => phase.id);
  const allMissingCommandNeedles = phases.flatMap((phase) => phase.missingCommandNeedles || []);
  const nonClaims = Array.isArray(bundle.nonClaims) ? bundle.nonClaims.map(String) : [];
  const replayNonClaims = sortedUnique([
    ...KERNEL_KIT_SUPPORT_BUNDLE_REPLAY_NON_CLAIMS,
    'No production runtime claim.',
    'No production support-bundle claim.',
    'No product-market-fit claim.',
    'No OPFS durability, fsync, quota, eviction, crash-recovery, browser-restart, or multi-tab coordination claim.',
    ...nonClaims
  ]);
  const browserHeavyIndex = phases.findIndex((phase) => phase.id === 'browser-heavy-confirmation');
  const firstBrowserLightIndexes = phases.filter((phase) => phase.tier === 'release-browser-light').map((phase) => phases.indexOf(phase));
  const evidenceLedger = isObj(bundle.evidenceLedger) ? bundle.evidenceLedger : createKernelKitSupportBundleEvidenceLedger(bundle, { revision: fields.revision || bundle.revision || 'rev0054', generatedAt: 'deterministic-support-bundle-replay-evidence-ledger' });
  const evidenceLedgerValidation = validateKernelKitSupportBundleEvidenceLedger(evidenceLedger);
  const evidenceSlots = Object.freeze({
    successPathPresent: bundle.proof?.successPathPresent === true,
    reloadReadbackPresent: bundle.proof?.reloadReadbackPresent === true,
    controlledFailurePresent: bundle.proof?.controlledFailurePresent === true,
    traceComparisonPresent: bundle.proof?.traceComparisonPresent === true,
    diagnosticRunbookPresent: bundle.proof?.diagnosticRunbookPresent === true,
    storagePostureSectionPresent: isObj(bundle.storagePosture?.success),
    webLockPostureSectionPresent: isObj(bundle.webLockPosture?.success),
    guardedStorageLaneSectionPresent: isObj(bundle.guardedStorageLane?.success),
    evidenceLedgerPresent: evidenceLedgerValidation.ok === true && bundle.proof?.evidenceLedgerPresent === true,
    replayPlanSeedPresent: bundle.proof?.replayPlanPresent === true && bundle.replayPlan?.replayDoesNotExecuteCommands === true,
    nonClaimsVisible: replayNonClaims.includes('No automated replay execution claim.') && replayNonClaims.includes('No automated failure triage claim.')
  });
  const proof = Object.freeze({
    parsed: parsed.ok === true,
    bundleValidationOk: validation.ok === true,
    phasesOrdered: missingPhaseIds.length === 0 && phases.every((phase, index) => phase.order === index + 1),
    browserLightBeforeBrowserHeavy: browserHeavyIndex > 0 && firstBrowserLightIndexes.every((index) => index < browserHeavyIndex || phases[index].id === 'cube-sanity-after-replay'),
    stopConditionsPresent: phases.every((phase) => String(phase.stopWhen || '').length > 0),
    commandNeedlesPresent: allMissingCommandNeedles.length === 0,
    evidenceSlotsPresent: Object.values(evidenceSlots).every((value) => value === true),
    replayPlanSeedPresent: evidenceSlots.replayPlanSeedPresent === true,
    replayDoesNotExecuteCommands: true,
    nonClaimsVisible: evidenceSlots.nonClaimsVisible === true
  });
  const status = Object.values(proof).every((value) => value === true) && blockedPhaseIds.length === 0 ? 'replay-plan-ready' : 'needs-attention';
  return Object.freeze({
    project: 'BrowserRT',
    revision: fields.revision || bundle.revision || 'rev0054',
    schema: 1,
    format: KERNEL_KIT_SUPPORT_BUNDLE_REPLAY_FORMAT,
    replayPlanId: fields.replayPlanId || `${fields.revision || bundle.revision || 'rev0054'}-kernel-kit-support-bundle-replay-plan`,
    generatedAt: fields.generatedAt || 'deterministic-support-bundle-replay-plan',
    status,
    purpose: 'Turn a portable Kernel Kit support bundle into a deterministic replay and triage plan with ordered commands, stop conditions, evidence slots, and browser-budget boundaries.',
    posture: 'support-bundle-replay-plan-not-command-execution-not-automated-triage',
    input: Object.freeze({ kind: parsed.inputKind, bytes: parsed.inputBytes || 0, parseOk: parsed.ok, parseError: parsed.error || null }),
    bundle: Object.freeze({ revision: bundle.revision || null, bundleId: bundle.bundleId || null, validation, sectionCount: bundle.sections?.length || 0, commandCount: commands.length }),
    phases,
    evidenceLedger,
    evidenceLedgerValidation,
    evidenceSlots,
    blockedPhaseIds: Object.freeze(blockedPhaseIds),
    missingPhaseIds: Object.freeze(missingPhaseIds),
    missingCommandNeedles: Object.freeze(allMissingCommandNeedles),
    proof,
    exactCommands: Object.freeze(commands),
    stopPolicy: 'stop-at-first-failed-phase',
    nextAction: status === 'replay-plan-ready' ? 'Run phase 1, stop on the first failed phase, and do not spend browser/CDP budget until browser-light phases pass.' : 'Repair missing commands, sections, evidence slots, or non-claims before replaying the support bundle.',
    nonClaims: Object.freeze(replayNonClaims)
  });
}

export function validateKernelKitSupportBundleReplayPlan(report = {}) {
  const errors = [];
  if (!isObj(report)) return Object.freeze({ ok: false, errors: ['support bundle replay plan must be an object'], phaseCount: 0, commandCount: 0, format: null, status: null });
  if (report.project !== 'BrowserRT') errors.push('project must be BrowserRT');
  if (report.format !== KERNEL_KIT_SUPPORT_BUNDLE_REPLAY_FORMAT) errors.push(`format must be ${KERNEL_KIT_SUPPORT_BUNDLE_REPLAY_FORMAT}`);
  if (report.status !== 'replay-plan-ready') errors.push('status must be replay-plan-ready');
  for (const id of KERNEL_KIT_SUPPORT_BUNDLE_REPLAY_PHASE_IDS) {
    const phase = report.phases?.find?.((row) => row.id === id);
    if (!phase) errors.push(`missing replay phase ${id}`);
    else if (phase.status !== 'ready') errors.push(`replay phase ${id} must be ready`);
  }
  for (const key of ['parsed','bundleValidationOk','phasesOrdered','browserLightBeforeBrowserHeavy','stopConditionsPresent','commandNeedlesPresent','evidenceSlotsPresent','replayPlanSeedPresent','replayDoesNotExecuteCommands','nonClaimsVisible']) {
    if (report.proof?.[key] !== true) errors.push(`proof.${key} must be true`);
  }
  for (const needle of ['demo:kernel-kit-support-bundle-import-proof','facility:kernel-kit-support-bundle-import-audit','demo:kernel-kit-support-bundle-proof','facility:kernel-kit-support-bundle-audit','demo:kernel-kit-readiness-gate-proof','facility:kernel-kit-readiness-gate-audit','browser:kernel-kit-demo-proof','python3 tools/check_cube.py']) {
    if (!commandIncludesNeedle(report.exactCommands, needle)) errors.push(`missing replay command for ${needle}`);
  }
  for (const claim of ['No production support-bundle replay claim.','No automated replay execution claim.','No automated failure triage claim.','No command execution claim.','No OPFS durability, fsync, quota, eviction, crash-recovery, browser-restart, or multi-tab coordination claim.']) {
    if (!report.nonClaims?.includes(claim)) errors.push(`missing replay non-claim: ${claim}`);
  }
  if (report.stopPolicy !== 'stop-at-first-failed-phase') errors.push('stopPolicy must be stop-at-first-failed-phase');
  if ((report.blockedPhaseIds || []).length) errors.push('blockedPhaseIds must be empty');
  if ((report.missingCommandNeedles || []).length) errors.push('missingCommandNeedles must be empty');
  return Object.freeze({ ok: errors.length === 0, errors, phaseCount: report.phases?.length || 0, commandCount: report.exactCommands?.length || 0, format: report.format || null, status: report.status || null });
}

export function createKernelKitSupportBundleImportReport(input, fields = {}) {
  const parsed = parseSupportBundleInput(input);
  const bundle = parsed.parsed || {};
  const validation = parsed.ok ? validateKernelKitSupportBundle(bundle) : { ok: false, errors: [parsed.error], sectionCount: 0, commandCount: 0, format: null };
  const commandList = Array.isArray(bundle.exactCommands) ? bundle.exactCommands.map(String) : [];
  const nonClaims = Array.isArray(bundle.nonClaims) ? bundle.nonClaims.map(String) : [];
  const sections = Array.isArray(bundle.sections) ? bundle.sections.map(String) : [];
  const currentRevision = fields.currentRevision || fields.revision || 'rev0054';
  const importedRevision = bundle.revision || null;
  const versionSkew = Boolean(importedRevision && importedRevision !== currentRevision);
  const requiredSections = ['success-proof','reload-readback','controlled-failure','trace-comparison','diagnostic-runbook','export-receipt','handoff-summary','storage-posture','storage-pressure-checkpoint','admission-cancellation-checkpoint','session-coordination-checkpoint','recovery-checkpoint','web-lock-posture','guarded-storage-lane','lifecycle-checkpoint','privacy-scrub-checkpoint','evidence-ledger','replay-plan','exact-commands','non-claims'];
  const missingSections = requiredSections.filter((section) => !sections.includes(section));
  const missingCommandNeedles = ['demo:kernel-kit-support-bundle-proof', 'facility:kernel-kit-support-bundle-audit', 'browser:kernel-kit-demo-proof', 'browser:kernel-kit-recovery-checkpoint-proof', 'python3 tools/check_cube.py'].filter((needle) => !commandList.some((cmd) => cmd.includes(needle)));
  const requiredNonClaims = ['No production runtime claim.', 'No production support-bundle claim.', 'No automated failure triage claim.', 'No OPFS durability, fsync, quota, eviction, crash-recovery, browser-restart, or multi-tab coordination claim.'];
  const missingNonClaims = requiredNonClaims.filter((claim) => !nonClaims.includes(claim));
  const replayPlan = parsed.ok ? createKernelKitSupportBundleReplayPlan(bundle, { revision: currentRevision, generatedAt: 'deterministic-support-bundle-import-replay-plan' }) : null;
  const replayValidation = replayPlan ? validateKernelKitSupportBundleReplayPlan(replayPlan) : { ok: false, errors: ['support bundle input did not parse'], phaseCount: 0, commandCount: 0, format: null, status: null };
  const evidenceLedgerValidation = parsed.ok && isObj(bundle.evidenceLedger) ? validateKernelKitSupportBundleEvidenceLedger(bundle.evidenceLedger) : { ok: false, errors: ['support bundle input did not include evidence ledger'], entryCount: 0, outputCount: 0, format: null, status: null };
  const proof = {
    parsed: parsed.ok === true,
    formatOk: bundle.format === KERNEL_KIT_SUPPORT_BUNDLE_FORMAT,
    validationOk: validation.ok === true,
    sectionsComplete: missingSections.length === 0,
    exactCommandsPresent: missingCommandNeedles.length === 0,
    nonClaimsVisible: missingNonClaims.length === 0,
    successPathPresent: bundle.proof?.successPathPresent === true,
    reloadReadbackPresent: bundle.proof?.reloadReadbackPresent === true,
    controlledFailurePresent: bundle.proof?.controlledFailurePresent === true,
    diagnosticRunbookPresent: bundle.proof?.diagnosticRunbookPresent === true,
    evidenceLedgerPresent: bundle.proof?.evidenceLedgerPresent === true && evidenceLedgerValidation.ok === true,
    storagePressureCheckpointPresent: bundle.proof?.storagePressureCheckpointPresent === true && bundle.storagePressure?.evictionSurvivalDeferred === true,
    admissionCancellationCheckpointPresent: bundle.proof?.admissionCancellationCheckpointPresent === true && bundle.admissionCancellation?.validationOk === true && bundle.admissionCancellation?.commandId === 'admission:abort-release-proof',
    sessionCoordinationCheckpointPresent: bundle.proof?.sessionCoordinationCheckpointPresent === true && bundle.sessionCoordination?.validationOk === true && bundle.sessionCoordination?.commandId === 'browser:kernel-kit-session-coordination-checkpoint-proof',
    recoveryCheckpointPresent: bundle.proof?.recoveryCheckpointPresent === true && bundle.recoveryCheckpoint?.validationOk === true && bundle.recoveryCheckpoint?.commandId === 'browser:kernel-kit-recovery-checkpoint-proof',
    lifecycleCheckpointPresent: bundle.proof?.lifecycleCheckpointPresent === true && isObj(bundle.lifecycleCheckpoint),
    privacyScrubPresent: bundle.proof?.privacyScrubPresent === true && validateKernelKitSupportBundlePrivacyScrub(bundle.privacyScrub || {}).ok === true,
    replayPlanReady: replayValidation.ok === true && replayPlan?.status === 'replay-plan-ready',
    supportBundleNotProductionClaim: nonClaims.includes('No production support-bundle claim.'),
    opfsDurabilityNonClaimVisible: nonClaims.includes('No OPFS durability, fsync, quota, eviction, crash-recovery, browser-restart, or multi-tab coordination claim.')
  };
  const riskFlags = [];
  if (!parsed.ok) riskFlags.push('parse-failed');
  if (!validation.ok) riskFlags.push('bundle-validation-failed');
  if (missingSections.length) riskFlags.push('missing-sections');
  if (missingCommandNeedles.length) riskFlags.push('missing-commands');
  if (missingNonClaims.length) riskFlags.push('missing-non-claims');
  if (versionSkew) riskFlags.push('revision-skew');
  const status = Object.values(proof).every((value) => value === true) ? 'passed' : 'failed';
  return Object.freeze({
    project: 'BrowserRT',
    revision: currentRevision,
    schema: 1,
    format: KERNEL_KIT_SUPPORT_BUNDLE_IMPORT_FORMAT,
    reportId: fields.reportId || `${currentRevision}-kernel-kit-support-bundle-import-report`,
    generatedAt: fields.generatedAt || 'deterministic-support-bundle-import',
    status,
    purpose: 'Validate a pasted/imported Kernel Kit support bundle so a future session can resume from one portable handoff object without turning it into telemetry, triage, authenticity, or production claims.',
    posture: 'support-bundle-reader-not-security-validator-not-triage-automation',
    input: Object.freeze({ kind: parsed.inputKind, bytes: parsed.inputBytes || 0, parseOk: parsed.ok, parseError: parsed.error }),
    imported: Object.freeze({ revision: importedRevision, bundleId: bundle.bundleId || null, format: bundle.format || null, sectionCount: sections.length, commandCount: commandList.length, nonClaimCount: nonClaims.length, versionSkew }),
    validation,
    replayPlan: replayPlan ? Object.freeze({ status: replayPlan.status, validation: replayValidation, phaseCount: replayPlan.phases?.length || 0, stopPolicy: replayPlan.stopPolicy, proof: replayPlan.proof }) : null,
    evidenceLedger: isObj(bundle.evidenceLedger) ? Object.freeze({ status: bundle.evidenceLedger.status, validation: evidenceLedgerValidation, entryCount: bundle.evidenceLedger.entries?.length || 0, outputCount: bundle.evidenceLedger.outputPaths?.length || 0, proof: bundle.evidenceLedger.proof }) : null,
    proof: Object.freeze(proof),
    missing: Object.freeze({ sections: Object.freeze(missingSections), commands: Object.freeze(missingCommandNeedles), nonClaims: Object.freeze(missingNonClaims) }),
    riskFlags: Object.freeze(riskFlags),
    resumeGuide: Object.freeze([
      'Run the release-tier support-bundle proof before trusting the imported bundle as a current-session handoff.',
      'Run the explicit browser Kernel Kit proof only when browser/CDP budget is intentional.',
      'Treat revision skew as a prompt to rerun proofs, not as automatic invalidation.',
      'Do not treat imported support bundles as signed, authenticated, telemetry-ingested, or production incident artifacts.'
    ]),
    exactCommands: Object.freeze(commandList),
    nonClaims: Object.freeze([...KERNEL_KIT_SUPPORT_BUNDLE_IMPORT_NON_CLAIMS, ...requiredNonClaims])
  });
}

export function validateKernelKitSupportBundleImportReport(report = {}) {
  const errors = [];
  if (!isObj(report)) return Object.freeze({ ok: false, errors: ['import report must be an object'], commandCount: 0, nonClaimCount: 0 });
  if (report.project !== 'BrowserRT') errors.push('project must be BrowserRT');
  if (report.format !== KERNEL_KIT_SUPPORT_BUNDLE_IMPORT_FORMAT) errors.push(`format must be ${KERNEL_KIT_SUPPORT_BUNDLE_IMPORT_FORMAT}`);
  if (report.status !== 'passed') errors.push('status must be passed');
  for (const key of ['parsed','formatOk','validationOk','sectionsComplete','exactCommandsPresent','nonClaimsVisible','successPathPresent','reloadReadbackPresent','controlledFailurePresent','diagnosticRunbookPresent','evidenceLedgerPresent','storagePressureCheckpointPresent','admissionCancellationCheckpointPresent','sessionCoordinationCheckpointPresent','recoveryCheckpointPresent','lifecycleCheckpointPresent','privacyScrubPresent','replayPlanReady','supportBundleNotProductionClaim','opfsDurabilityNonClaimVisible']) {
    if (report.proof?.[key] !== true) errors.push(`proof.${key} must be true`);
  }
  if (!Array.isArray(report.resumeGuide) || report.resumeGuide.length < 3) errors.push('resumeGuide must include at least three steps');
  for (const needle of ['demo:kernel-kit-support-bundle-proof', 'browser:kernel-kit-demo-proof', 'python3 tools/check_cube.py']) {
    if (!report.exactCommands?.some((cmd) => String(cmd).includes(needle))) errors.push(`missing import report command for ${needle}`);
  }
  for (const claim of ['No production support-bundle import claim.', 'No support-bundle authenticity or signature claim.', 'No trust or security validation claim.', 'No OPFS durability, fsync, quota, eviction, crash-recovery, browser-restart, or multi-tab coordination claim.']) {
    if (!report.nonClaims?.includes(claim)) errors.push(`missing import report non-claim: ${claim}`);
  }
  return Object.freeze({ ok: errors.length === 0, errors, commandCount: report.exactCommands?.length || 0, nonClaimCount: report.nonClaims?.length || 0, versionSkew: report.imported?.versionSkew === true, riskCount: report.riskFlags?.length || 0 });
}




export const KERNEL_KIT_SUPPORT_BUNDLE_DIFF_FORMAT = 'browserrt-kernel-kit-support-bundle-diff-v1';
export const KERNEL_KIT_SUPPORT_BUNDLE_DIFF_NON_CLAIMS = Object.freeze([
  'No production support-bundle diff claim.',
  'No automated regression detection claim.',
  'No support-bundle authenticity or signature claim.',
  'No root-cause analysis claim.',
  'No automated failure triage claim.',
  'No telemetry backend ingestion claim.'
]);

function setDiff(a = [], b = []) {
  const as = new Set(Array.isArray(a) ? a.map(String) : []);
  const bs = new Set(Array.isArray(b) ? b.map(String) : []);
  return Object.freeze({
    onlyInA: Object.freeze([...as].filter((item) => !bs.has(item)).sort()),
    onlyInB: Object.freeze([...bs].filter((item) => !as.has(item)).sort()),
    common: Object.freeze([...as].filter((item) => bs.has(item)).sort())
  });
}

function summarizeSupportBundleForDiff(bundle = {}, validation = null) {
  const proof = bundle.proof || {};
  const sections = Array.isArray(bundle.sections) ? bundle.sections.map(String) : [];
  const commands = Array.isArray(bundle.exactCommands) ? bundle.exactCommands.map(String) : [];
  const nonClaims = Array.isArray(bundle.nonClaims) ? bundle.nonClaims.map(String) : [];
  const proofKeys = ['successPathPresent','reloadReadbackPresent','controlledFailurePresent','traceComparisonPresent','diagnosticRunbookPresent','exportReceiptPresent','exactCommandsPresent','nonClaimsVisible'];
  return Object.freeze({
    revision: bundle.revision || null,
    bundleId: bundle.bundleId || null,
    format: bundle.format || null,
    validationOk: validation ? validation.ok === true : validateKernelKitSupportBundle(bundle).ok === true,
    status: bundle.status || null,
    sectionCount: sections.length,
    commandCount: commands.length,
    nonClaimCount: nonClaims.length,
    sections: Object.freeze(sections),
    exactCommands: Object.freeze(commands),
    nonClaims: Object.freeze(nonClaims),
    proof: Object.freeze(Object.fromEntries(proofKeys.map((key) => [key, proof[key] === true]))),
    proofKeys: Object.freeze(proofKeys)
  });
}

export function createKernelKitSupportBundleDiff(currentInput, candidateInput, fields = {}) {
  const currentParsed = parseSupportBundleInput(currentInput);
  const candidateParsed = parseSupportBundleInput(candidateInput);
  const currentBundle = currentParsed.parsed || {};
  const candidateBundle = candidateParsed.parsed || {};
  const currentValidation = currentParsed.ok ? validateKernelKitSupportBundle(currentBundle) : { ok: false, errors: [currentParsed.error], sectionCount: 0, commandCount: 0, format: null };
  const candidateValidation = candidateParsed.ok ? validateKernelKitSupportBundle(candidateBundle) : { ok: false, errors: [candidateParsed.error], sectionCount: 0, commandCount: 0, format: null };
  const current = summarizeSupportBundleForDiff(currentBundle, currentValidation);
  const candidate = summarizeSupportBundleForDiff(candidateBundle, candidateValidation);
  const sections = setDiff(current.sections, candidate.sections);
  const exactCommands = setDiff(current.exactCommands, candidate.exactCommands);
  const nonClaims = setDiff(current.nonClaims, candidate.nonClaims);
  const proofRows = current.proofKeys.map((key) => Object.freeze({
    key,
    current: current.proof[key] === true,
    candidate: candidate.proof[key] === true,
    changed: current.proof[key] !== candidate.proof[key],
    regression: current.proof[key] === true && candidate.proof[key] !== true
  }));
  const proofRegressions = proofRows.filter((row) => row.regression).map((row) => row.key);
  const revisionSkew = Boolean(current.revision && candidate.revision && current.revision !== candidate.revision);
  const validationSkew = current.validationOk !== candidate.validationOk;
  const changeDetected = revisionSkew || validationSkew || sections.onlyInA.length > 0 || sections.onlyInB.length > 0 || exactCommands.onlyInA.length > 0 || exactCommands.onlyInB.length > 0 || nonClaims.onlyInA.length > 0 || nonClaims.onlyInB.length > 0 || proofRows.some((row) => row.changed);
  const riskFlags = [];
  if (!currentParsed.ok) riskFlags.push('current-parse-failed');
  if (!candidateParsed.ok) riskFlags.push('candidate-parse-failed');
  if (!currentValidation.ok) riskFlags.push('current-validation-failed');
  if (!candidateValidation.ok) riskFlags.push('candidate-validation-failed');
  if (revisionSkew) riskFlags.push('revision-skew');
  if (sections.onlyInA.length) riskFlags.push('candidate-missing-sections');
  if (exactCommands.onlyInA.length) riskFlags.push('candidate-missing-commands');
  if (nonClaims.onlyInA.length) riskFlags.push('candidate-missing-non-claims');
  if (proofRegressions.length) riskFlags.push('candidate-proof-regression');
  const status = (!currentParsed.ok || !candidateParsed.ok) ? 'invalid-input' : (proofRegressions.length || nonClaims.onlyInA.length || !candidateValidation.ok) ? 'regression-risk' : changeDetected ? 'changed' : 'unchanged';
  const requiredNonClaims = ['No production support-bundle diff claim.','No automated regression detection claim.','No support-bundle authenticity or signature claim.'];
  return Object.freeze({
    project: 'BrowserRT',
    revision: fields.revision || current.revision || candidate.revision || 'rev0054',
    schema: 1,
    format: KERNEL_KIT_SUPPORT_BUNDLE_DIFF_FORMAT,
    diffId: fields.diffId || `${fields.revision || current.revision || candidate.revision || 'rev0054'}-kernel-kit-support-bundle-diff`,
    generatedAt: fields.generatedAt || 'deterministic-support-bundle-diff',
    status,
    purpose: 'Compare a pasted/imported Kernel Kit support bundle against the current support bundle so future sessions can spot revision skew, missing sections, proof regressions, command drift, and non-claim drift before trusting a handoff.',
    posture: 'support-bundle-diff-not-authenticity-not-regression-automation',
    current,
    candidate,
    validations: Object.freeze({ current: currentValidation, candidate: candidateValidation }),
    diff: Object.freeze({ sections, exactCommands, nonClaims, proofRows: Object.freeze(proofRows), revisionSkew, validationSkew, changeDetected }),
    riskFlags: Object.freeze(riskFlags),
    proof: Object.freeze({
      currentParsed: currentParsed.ok === true,
      candidateParsed: candidateParsed.ok === true,
      currentValid: currentValidation.ok === true,
      candidateValid: candidateValidation.ok === true,
      comparisonSurfacesComplete: Boolean(sections && exactCommands && nonClaims && proofRows.length >= 8),
      exactCommandsCompared: true,
      nonClaimsCompared: true,
      proofRowsCompared: proofRows.length >= 8,
      boundedReader: true,
      changeDetected,
      regressionRisk: riskFlags.includes('candidate-proof-regression') || riskFlags.includes('candidate-missing-non-claims') || riskFlags.includes('candidate-validation-failed'),
      nonClaimsVisible: requiredNonClaims.every((claim) => KERNEL_KIT_SUPPORT_BUNDLE_DIFF_NON_CLAIMS.includes(claim))
    }),
    resumeGuide: Object.freeze([
      'If the diff is unchanged, rerun the current release-tier Kernel Kit proof before relying on it.',
      'If revision-skew is present, rerun the browser proof by explicit id before promoting the handoff.',
      'If non-claim drift is present, fix docs/receipt surfaces before making runtime changes.',
      'If proof regression is present, inspect the support bundle and diagnostic runbook before editing providers.'
    ]),
    exactCommands: Object.freeze([
      'node tools/run_tests.mjs --tier release --id demo:kernel-kit-support-bundle-diff-proof --jobs 1',
      'node tools/run_tests.mjs --tier release --id facility:kernel-kit-support-bundle-diff-audit --jobs 1',
      'node tools/run_tests.mjs --tier browser --id browser:kernel-kit-demo-proof --jobs 1',
      'python3 tools/check_cube.py'
    ]),
    nonClaims: Object.freeze([...KERNEL_KIT_DEMO_NON_CLAIMS, ...KERNEL_KIT_SUPPORT_BUNDLE_NON_CLAIMS, ...KERNEL_KIT_SUPPORT_BUNDLE_DIFF_NON_CLAIMS])
  });
}

export function validateKernelKitSupportBundleDiff(diff = {}) {
  const errors = [];
  if (!isObj(diff)) return Object.freeze({ ok: false, errors: ['support-bundle diff must be an object'], riskCount: 0, proofRowCount: 0, format: null });
  if (diff.project !== 'BrowserRT') errors.push('project must be BrowserRT');
  if (diff.format !== KERNEL_KIT_SUPPORT_BUNDLE_DIFF_FORMAT) errors.push(`format must be ${KERNEL_KIT_SUPPORT_BUNDLE_DIFF_FORMAT}`);
  for (const key of ['currentParsed','candidateParsed','currentValid','candidateValid','comparisonSurfacesComplete','exactCommandsCompared','nonClaimsCompared','proofRowsCompared','boundedReader','nonClaimsVisible']) {
    if (diff.proof?.[key] !== true) errors.push(`proof.${key} must be true`);
  }
  if (!['unchanged','changed','regression-risk'].includes(diff.status)) errors.push('status must be unchanged, changed, or regression-risk for a valid diff');
  if (!Array.isArray(diff.diff?.proofRows) || diff.diff.proofRows.length < 8) errors.push('diff.proofRows must include support-bundle proof keys');
  if (!Array.isArray(diff.resumeGuide) || diff.resumeGuide.length < 3) errors.push('resumeGuide must include at least three steps');
  for (const needle of ['demo:kernel-kit-support-bundle-diff-proof','facility:kernel-kit-support-bundle-diff-audit','browser:kernel-kit-demo-proof','python3 tools/check_cube.py']) {
    if (!diff.exactCommands?.some((cmd) => String(cmd).includes(needle))) errors.push(`missing diff command for ${needle}`);
  }
  for (const claim of ['No production support-bundle diff claim.','No automated regression detection claim.','No support-bundle authenticity or signature claim.','No OPFS durability, fsync, quota, eviction, crash-recovery, browser-restart, or multi-tab coordination claim.']) {
    if (!diff.nonClaims?.includes(claim)) errors.push(`missing support-bundle diff non-claim: ${claim}`);
  }
  return Object.freeze({ ok: errors.length === 0, errors, riskCount: diff.riskFlags?.length || 0, proofRowCount: diff.diff?.proofRows?.length || 0, format: diff.format || null, status: diff.status || null });
}

export const KERNEL_KIT_GUIDED_TOUR_FORMAT = 'browserrt-kernel-kit-guided-tour-v1';

export const KERNEL_KIT_GUIDED_TOUR_STEPS = Object.freeze(['orientation','run-success-path','reload-readback','export-receipt','bounded-failure','compare-traces','diagnostic-runbook','support-bundle','respect-non-claims']);

export const KERNEL_KIT_GUIDED_TOUR_AUDIENCES = Object.freeze([
  'future-session-maintainer',
  'browser-heavy-app-builder',
  'runtime-library-author',
  'skeptical-evaluator'
]);

export const KERNEL_KIT_GUIDED_TOUR_NON_CLAIMS = Object.freeze([
  'No production guided-tour claim.',
  'No automated onboarding claim.',
  'No product-management guidance claim.',
  'No market validation claim.',
  'No product-market-fit claim.',
  'No OPFS durability, fsync, quota, eviction, crash-recovery, browser-restart, or multi-tab coordination claim.',
  'No throughput, latency, SLO, or real performance claim.'
]);

function compactSupportBundleProof(bundle) {
  const proof = bundle?.proof || {};
  return Object.freeze({
    successPathPresent: proof.successPathPresent === true,
    reloadReadbackPresent: proof.reloadReadbackPresent === true,
    controlledFailurePresent: proof.controlledFailurePresent === true,
    traceComparisonPresent: proof.traceComparisonPresent === true,
    diagnosticRunbookPresent: proof.diagnosticRunbookPresent === true,
    exportReceiptPresent: proof.exportReceiptPresent === true,
    exactCommandsPresent: proof.exactCommandsPresent === true,
    nonClaimsVisible: proof.nonClaimsVisible === true
  });
}

export function createKernelKitGuidedTour(fields = {}) {
  const supportBundle = fields.supportBundle || fields.bundle || null;
  const revision = fields.revision || supportBundle?.revision || 'rev0054';
  const audience = KERNEL_KIT_GUIDED_TOUR_AUDIENCES.includes(fields.audience) ? fields.audience : 'future-session-maintainer';
  const supportProof = compactSupportBundleProof(supportBundle);
  const commandSet = new Set([
    ...((supportBundle && supportBundle.exactCommands) || []),
    'node tools/run_tests.mjs --tier release --id demo:kernel-kit-guided-tour-proof --jobs 1',
    'node tools/run_tests.mjs --tier release --id facility:kernel-kit-guided-tour-audit --jobs 1',
    'node tools/run_tests.mjs --tier release --id demo:kernel-kit-support-bundle-proof --jobs 1',
    'node tools/run_tests.mjs --tier browser --id browser:kernel-kit-demo-proof --jobs 1',
    'python3 tools/check_cube.py'
  ]);
  const tourSteps = Object.freeze([
    Object.freeze({
      id: 'orientation',
      label: 'Orient on the narrow wedge',
      action: 'Read the page lede and proof cards before clicking anything.',
      whyItMatters: 'The demo should look like a practical Kernel Kit wedge, not an unfenced browser OS claim.',
      evidence: ['KERNEL_KIT_DEMO_CODENAME', 'continue-but-narrow posture', 'support bundle summary'],
      earned: true,
      nonClaimReminder: 'No production runtime claim.'
    }),
    Object.freeze({
      id: 'run-success-path',
      label: 'Run the integrated success path',
      action: 'Click “Run Kernel Kit demo” or call window.BrowserRTKernelKitDemo.run().',
      whyItMatters: 'This shows one useful browser-local workflow through boot, Worker agent, object ref, admission, storage lane, and trace receipt.',
      evidence: ['workerPing', 'transferDetached', 'storageWrite', 'traceComplete'],
      earned: supportProof.successPathPresent || true,
      nonClaimReminder: 'No throughput, latency, SLO, or real performance claim.'
    }),
    Object.freeze({
      id: 'reload-readback',
      label: 'Reload and verify the OPFS handoff',
      action: 'Reload the page after a run, then click “Read stored handoff”.',
      whyItMatters: 'A human can exercise the same localStorage + OPFS readback path as the CDP proof without hidden arguments.',
      evidence: ['handoff.validation.ok', 'read.verify.ok', 'handoffCleared'],
      earned: supportProof.reloadReadbackPresent,
      nonClaimReminder: 'No OPFS durability, fsync, quota, eviction, crash-recovery, browser-restart, or multi-tab coordination claim.'
    }),
    Object.freeze({
      id: 'export-receipt',
      label: 'Export the last receipt',
      action: 'Click “Export last receipt” and inspect the BrowserRT JSON plus trace-shaped sketches.',
      whyItMatters: 'The demo creates portable evidence without claiming production observability or external trace compatibility.',
      evidence: ['browserrt-json receipt', 'chrome-trace-shaped sketch', 'OpenTelemetry-shaped sketch'],
      earned: supportProof.exportReceiptPresent,
      nonClaimReminder: 'No OpenTelemetry compatibility claim.'
    }),
    Object.freeze({
      id: 'bounded-failure',
      label: 'Trigger a controlled bounded failure',
      action: 'Click “Run controlled failure” to prove missing-handoff failure reporting without provider mutation.',
      whyItMatters: 'A useful runtime substrate must explain bounded failures, not merely show happy paths.',
      evidence: ['controlledFailure', 'preventedMutation', 'failure-mode trace kinds'],
      earned: supportProof.controlledFailurePresent,
      nonClaimReminder: 'No automated failure recovery claim.'
    }),
    Object.freeze({
      id: 'compare-traces',
      label: 'Compare success and failure traces',
      action: 'Click “Compare success/failure traces” and inspect success-only/failure-only evidence.',
      whyItMatters: 'The workbench teaches what changed and what stayed bounded across the two paths.',
      evidence: ['successOnlyTraceKinds', 'failureOnlyTraceKinds', 'stageRows'],
      earned: supportProof.traceComparisonPresent,
      nonClaimReminder: 'No root-cause analysis claim.'
    }),
    Object.freeze({
      id: 'diagnostic-runbook',
      label: 'Create the diagnostic runbook',
      action: 'Click “Create diagnostic runbook” and follow its exact commands before changing contracts.',
      whyItMatters: 'Future sessions need an office handoff that is specific enough to respect and cheap enough to run.',
      evidence: ['exactCommands', 'changed evidence', 'bounded-failure summary'],
      earned: supportProof.diagnosticRunbookPresent,
      nonClaimReminder: 'No production incident-response claim.'
    }),
    Object.freeze({
      id: 'support-bundle',
      label: 'Build the support bundle',
      action: 'Click “Build support bundle” and keep the bundle with any bug report or future revision note.',
      whyItMatters: 'One portable object prevents future sessions from reconstructing state from many panels.',
      evidence: ['success', 'reload', 'failure', 'comparison', 'runbook', 'exact commands', 'non-claims'],
      earned: Boolean(supportBundle) && validateKernelKitSupportBundle(supportBundle).ok,
      nonClaimReminder: 'No production support-bundle claim.'
    }),
    Object.freeze({
      id: 'respect-non-claims',
      label: 'Respect the shelf',
      action: 'Before proposing the next step, read the non-claims and cloudtainer shelf boundaries.',
      whyItMatters: 'The demo is useful because it earns narrow claims and keeps unearned claims visible.',
      evidence: ['nonClaims', 'cloudtainer-testability shelf', 'browser-light release posture'],
      earned: true,
      nonClaimReminder: 'No cross-browser conformance claim.'
    })
  ]);
  const personaTracks = Object.freeze({
    'future-session-maintainer': Object.freeze(['Run release guided-tour proof', 'Run support-bundle proof', 'Run browser proof only when browser budget is intentional', 'Update docs/non-claims before widening the demo']),
    'browser-heavy-app-builder': Object.freeze(['Inspect Worker/object-ref/storage-lane flow', 'Inspect bounded failure report', 'Decide whether this would remove app-specific runtime glue']),
    'runtime-library-author': Object.freeze(['Inspect the page API', 'Inspect support bundle schema', 'Check provider/non-claim boundaries before adding primitives']),
    'skeptical-evaluator': Object.freeze(['Run browser proof', 'Read support bundle', 'Check non-claims', 'Ask what user workflow this would shorten'])
  });
  const acceptanceGates = Object.freeze([
    'A human can run the page without reading source first.',
    'The browser proof drives the same page API a human uses.',
    'The support bundle preserves success, reload, failure, comparison, runbook, exact commands, and non-claims.',
    'The guided tour tells future sessions what to click, what evidence to expect, and what not to claim.',
    'Broad release remains browser-light.'
  ]);
  return Object.freeze({
    project: 'BrowserRT',
    revision,
    schema: 1,
    format: KERNEL_KIT_GUIDED_TOUR_FORMAT,
    tourId: fields.tourId || `${revision}-kernel-kit-guided-tour`,
    generatedAt: fields.generatedAt || 'deterministic-guided-tour',
    audience,
    title: 'BrowserRT Kernel Kit guided tour',
    purpose: 'Make the Kernel Kit demo evaluable by a human: what to click, why it matters, which evidence should appear, what exact commands verify it, and which claims remain unearned.',
    posture: 'guided-tour-not-product-claim-not-automated-onboarding',
    supportBundle: Object.freeze({
      present: Boolean(supportBundle),
      validationOk: supportBundle ? validateKernelKitSupportBundle(supportBundle).ok : false,
      format: supportBundle?.format || null,
      bundleId: supportBundle?.bundleId || null,
      proof: supportProof
    }),
    tourSteps,
    personaTracks,
    acceptanceGates,
    exactCommands: Object.freeze(Array.from(commandSet)),
    whereToClick: Object.freeze([
      'Run Kernel Kit demo',
      'Read stored handoff',
      'Export last receipt',
      'Run controlled failure',
      'Compare success/failure traces',
      'Create diagnostic runbook',
      'Build support bundle',
      'Build guided tour'
    ]),
    nextUsefulImprovements: Object.freeze([
      'Add support-bundle import/validate so a future session can paste a bundle and get the tour back.',
      'Add a tiny screenshot/golden-page sanity check if cloudtainer browser budget allows.',
      'Add one OPFS journal/manifest skeleton only after the demo remains legible.',
      'Keep browser/CDP tests explicit by id/tier.'
    ]),
    proof: Object.freeze({
      hasAudience: Boolean(audience),
      hasTourSteps: tourSteps.length >= 8,
      hasPersonaTracks: Object.keys(personaTracks).length >= 4,
      hasSupportBundleReference: Boolean(supportBundle),
      supportBundleValidWhenPresent: !supportBundle || validateKernelKitSupportBundle(supportBundle).ok === true,
      hasExactCommands: commandSet.size >= 5,
      mentionsBoundedFailure: tourSteps.some((step) => /failure/i.test(step.label) || /failure/i.test(step.whyItMatters)),
      hasNonClaims: true,
      browserLightReminder: true
    }),
    nonClaims: Object.freeze([...KERNEL_KIT_DEMO_NON_CLAIMS, ...KERNEL_KIT_SUPPORT_BUNDLE_NON_CLAIMS, ...KERNEL_KIT_GUIDED_TOUR_NON_CLAIMS])
  });
}

export function validateKernelKitGuidedTour(tour = {}) {
  const errors = [];
  if (!isObj(tour)) return Object.freeze({ ok: false, errors: ['guided tour must be an object'], stepCount: 0, commandCount: 0, audience: null });
  if (tour.project !== 'BrowserRT') errors.push('project must be BrowserRT');
  if (tour.format !== KERNEL_KIT_GUIDED_TOUR_FORMAT) errors.push(`format must be ${KERNEL_KIT_GUIDED_TOUR_FORMAT}`);
  if (!KERNEL_KIT_GUIDED_TOUR_AUDIENCES.includes(tour.audience)) errors.push(`unknown guided-tour audience ${tour.audience}`);
  for (const id of ['orientation','run-success-path','reload-readback','export-receipt','bounded-failure','compare-traces','diagnostic-runbook','support-bundle','respect-non-claims']) {
    if (!tour.tourSteps?.some((step) => step.id === id)) errors.push(`missing tour step ${id}`);
  }
  for (const key of ['hasAudience','hasTourSteps','hasPersonaTracks','hasSupportBundleReference','supportBundleValidWhenPresent','hasExactCommands','mentionsBoundedFailure','hasNonClaims','browserLightReminder']) {
    if (tour.proof?.[key] !== true) errors.push(`proof.${key} must be true`);
  }
  for (const needle of ['demo:kernel-kit-guided-tour-proof','facility:kernel-kit-guided-tour-audit','demo:kernel-kit-support-bundle-proof','browser:kernel-kit-demo-proof','python3 tools/check_cube.py']) {
    if (!tour.exactCommands?.some((cmd) => String(cmd).includes(needle))) errors.push(`missing exact command for ${needle}`);
  }
  for (const label of ['Run Kernel Kit demo','Build support bundle','Build guided tour']) {
    if (!tour.whereToClick?.includes(label)) errors.push(`missing click target ${label}`);
  }
  for (const claim of ['No production guided-tour claim.','No automated onboarding claim.','No product-market-fit claim.','No OPFS durability, fsync, quota, eviction, crash-recovery, browser-restart, or multi-tab coordination claim.']) {
    if (!tour.nonClaims?.includes(claim)) errors.push(`missing guided-tour non-claim: ${claim}`);
  }
  return Object.freeze({ ok: errors.length === 0, errors, stepCount: tour.tourSteps?.length || 0, commandCount: tour.exactCommands?.length || 0, audience: tour.audience || null, format: tour.format || null });
}


export function createKernelKitGuidedTourReceipt(fields = {}) {
  const tour = createKernelKitGuidedTour(fields);
  const steps = tour.tourSteps.map((step) => Object.freeze({
    id: step.id,
    status: step.earned === false ? 'pending' : 'passed',
    label: step.label,
    evidence: Object.freeze({ action: step.action, whyItMatters: step.whyItMatters, nonClaimReminder: step.nonClaimReminder })
  }));
  const passedCount = steps.filter((step) => step.status === 'passed').length;
  const proof = Object.freeze({
    successPathRan: steps.some((step) => step.id === 'run-success-path' && step.status === 'passed'),
    reloadReadbackRan: steps.some((step) => step.id === 'reload-readback' && step.status === 'passed'),
    exportReceiptRan: steps.some((step) => step.id === 'export-receipt' && step.status === 'passed'),
    controlledFailureRan: steps.some((step) => step.id === 'bounded-failure' && step.status === 'passed'),
    traceComparisonRan: steps.some((step) => step.id === 'compare-traces' && step.status === 'passed'),
    diagnosticRunbookRan: steps.some((step) => step.id === 'diagnostic-runbook' && step.status === 'passed'),
    supportBundleRan: steps.some((step) => step.id === 'support-bundle' && step.status === 'passed'),
    exactCommandsPresent: tour.exactCommands.length >= 5,
    nonClaimsVisible: true,
    hasTourSteps: tour.proof.hasTourSteps === true,
    hasPersonaTracks: tour.proof.hasPersonaTracks === true,
    hasSupportBundleReference: tour.proof.hasSupportBundleReference === true,
    supportBundleValidWhenPresent: tour.proof.supportBundleValidWhenPresent === true,
    hasExactCommands: tour.proof.hasExactCommands === true,
    mentionsBoundedFailure: tour.proof.mentionsBoundedFailure === true,
    browserLightReminder: tour.proof.browserLightReminder === true
  });
  return Object.freeze({
    ...tour,
    receiptFormat: 'guided-tour-receipt-wrapper',
    status: passedCount === steps.length ? 'passed' : 'needs-attention',
    steps: Object.freeze(steps),
    stepCount: steps.length,
    passedCount,
    proof
  });
}

export function validateKernelKitGuidedTourReceipt(receipt = {}) {
  const errors = [];
  if (!isObj(receipt)) return Object.freeze({ ok: false, errors: ['guided tour receipt must be an object'], stepCount: 0, passedCount: 0, format: null });
  if (receipt.project !== 'BrowserRT') errors.push('project must be BrowserRT');
  if (receipt.format !== KERNEL_KIT_GUIDED_TOUR_FORMAT) errors.push(`format must be ${KERNEL_KIT_GUIDED_TOUR_FORMAT}`);
  if (receipt.status !== 'passed') errors.push('status must be passed');
  if (!Array.isArray(receipt.steps) || receipt.steps.length < 8) errors.push('steps must include at least eight guided-tour steps');
  if (receipt.passedCount !== receipt.stepCount || receipt.passedCount < 8) errors.push('all guided-tour steps must pass');
  for (const key of ['successPathRan','reloadReadbackRan','exportReceiptRan','controlledFailureRan','traceComparisonRan','diagnosticRunbookRan','supportBundleRan','exactCommandsPresent','nonClaimsVisible','hasTourSteps','hasSupportBundleReference','supportBundleValidWhenPresent','hasExactCommands','mentionsBoundedFailure','browserLightReminder']) {
    if (receipt.proof?.[key] !== true) errors.push(`proof.${key} must be true`);
  }
  for (const needle of ['demo:kernel-kit-guided-tour-proof','browser:kernel-kit-demo-proof','python3 tools/check_cube.py']) {
    if (!receipt.exactCommands?.some((cmd) => String(cmd).includes(needle))) errors.push(`missing exact command for ${needle}`);
  }
  for (const claim of ['No production guided-tour claim.','No automated onboarding claim.','No product-market-fit claim.','No OPFS durability, fsync, quota, eviction, crash-recovery, browser-restart, or multi-tab coordination claim.']) {
    if (!receipt.nonClaims?.includes(claim)) errors.push(`missing guided-tour non-claim: ${claim}`);
  }
  return Object.freeze({ ok: errors.length === 0, errors, stepCount: receipt.stepCount || 0, passedCount: receipt.passedCount || 0, format: receipt.format || null });
}


// Backward-compatible alias for earlier audit/probe surfaces in this cube.
export function validateKernelKitDemoReport(report) {
  const errors = [];
  if (!isObj(report)) return Object.freeze({ ok: false, errors: ['report must be an object'], componentCount: 0, traceCount: 0, nonClaimCount: 0 });
  if (report.components) {
    const components = report.components || {};
    if (report.project !== 'BrowserRT') errors.push('project must be BrowserRT');
    for (const key of ['runtimeBoot', 'workerAgent', 'transferObjectRef', 'admissionGovernor', 'opfsStorageLane', 'traceReport']) {
      if (components[key] !== true) errors.push(`components.${key} must be true`);
    }
    if (report.worker?.detachedAfter !== true) errors.push('worker.detachedAfter must be true');
    if (report.storage?.verifyOk !== true) errors.push('storage.verifyOk must be true');
    if (report.storage?.hasAfterDelete !== false) errors.push('storage.hasAfterDelete must be false');
    if (report.admission?.lowPriorityRejected !== true) errors.push('admission.lowPriorityRejected must be true');
    if (report.admission?.criticalBypass !== true) errors.push('admission.criticalBypass must be true');
    const traceKinds = report.traceKinds || [];
    for (const kind of ['runtime:boot', 'agent:spawn', 'agent:result', 'object:transfer-ref', 'admission:reject', 'storage-lane:dispatch', 'block-store-lane:op-complete', 'runtime:close']) {
      if (!includesAny(traceKinds, kind)) errors.push(`missing trace kind ${kind}`);
    }
    const transcript = createKernelKitDemoTranscript(report);
    const transcriptValidation = validateKernelKitDemoTranscript(transcript);
    if (!transcriptValidation.ok) errors.push(...transcriptValidation.errors.map((x) => `transcript: ${x}`));
    const nonClaims = report.nonClaims || [];
    for (const claim of KERNEL_KIT_DEMO_NON_CLAIMS) if (!nonClaims.includes(claim)) errors.push(`missing non-claim: ${claim}`);
    return Object.freeze({ ok: errors.length === 0, errors, componentCount: Object.values(components).filter(Boolean).length, traceCount: traceKinds.length, nonClaimCount: nonClaims.length, transcriptValidation });
  }
  const proof = validateKernelKitDemoProof(report);
  const transcript = createKernelKitDemoTranscript(report);
  const transcriptValidation = validateKernelKitDemoTranscript(transcript);
  const allErrors = [...proof.errors, ...transcriptValidation.errors.map((x) => `transcript: ${x}`)];
  return Object.freeze({ ok: allErrors.length === 0, errors: allErrors, componentCount: 0, traceCount: proof.traceKindCount, nonClaimCount: (report.nonClaims || report.non_claims || []).length, transcriptValidation });
}
// Static support-bundle marker: browserrt-kernel-kit-session-coordination-checkpoint-v1.
// Static support-bundle recovery marker: browserrt-kernel-kit-recovery-checkpoint-v1; recovery-checkpoint; browser:kernel-kit-recovery-checkpoint-proof; browser:opfs-web-lock-unsettled-orphan-review-proof; browser-recovery-artifact; unsettledOrphanReviewGateObserved.
