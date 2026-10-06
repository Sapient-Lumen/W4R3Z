// BrowserRT rev0047 Kernel Kit demo observatory.
// Converts proof artifacts into a human-legible demo receipt: stages, lanes,
// trace counts, capability badges, proof/non-claim split, and next-demo notes.
// This is not a browser-performance monitor or production observability system.

export const KERNEL_KIT_OBSERVATORY_CODENAME = 'Kernel Kit Demo Observatory';

export const KERNEL_KIT_OBSERVATORY_REQUIRED_SECTIONS = Object.freeze([
  'mission',
  'capability-badges',
  'stage-cards',
  'lane-timeline',
  'trace-summary',
  'proof-receipt',
  'non-claims',
  'next-demo-work'
]);

export const KERNEL_KIT_OBSERVATORY_NON_CLAIMS = Object.freeze([
  'No production observability claim.',
  'No browser download UX claim.',
  'No failure recovery automation claim.',
  'No browser performance claim.',
  'No OpenTelemetry compatibility claim.',
  'No Chrome DevTools trace-format compatibility claim.',
  'No OPFS durability, fsync, quota, eviction, crash-recovery, browser-restart, or multi-tab coordination claim.',
  'No product-market-fit claim.'
]);

const STAGE_DEFS = Object.freeze([
  { id: 'boot-runtime', title: 'Boot runtime', lane: 'main', proofKeys: ['booted'], traceKinds: ['runtime:boot'] },
  { id: 'bounded-channel-touch', title: 'Touch bounded channel', lane: 'main', proofKeys: ['boundedChannel'], traceKinds: ['channel:create', 'channel:send', 'channel:receive'] },
  { id: 'spawn-worker-agent', title: 'Spawn worker agent', lane: 'cpu', proofKeys: ['workerAgent', 'workerPing'], traceKinds: ['agent:spawn', 'agent:ready', 'agent:call', 'agent:result'] },
  { id: 'transfer-object-ref', title: 'Transfer object ref', lane: 'cpu', proofKeys: ['transferDetached'], traceKinds: ['object:transfer-ref'] },
  { id: 'admission-governor-gate', title: 'Apply admission gate', lane: 'scheduler', proofKeys: ['admissionAccepted', 'admissionRejectedNoMutation'], traceKinds: ['admission:admit', 'admission:reject', 'admission:release'] },
  { id: 'opfs-storage-lane-write', title: 'Write through OPFS storage lane', lane: 'storage', proofKeys: ['storageWrite', 'storageLaneWriteRead'], traceKinds: ['object:opfs-storage-lane-adapter-ref', 'block-store-lane:schedule', 'storage-lane:dispatch', 'block-store-lane:op-complete', 'storage:opfs-block-put'] },
  { id: 'page-reload-readback', title: 'Read back after page reload', lane: 'storage', proofKeys: ['reloadReadback'], traceKinds: ['storage:opfs-block-get'] },
  { id: 'trace-and-audit-artifact', title: 'Emit trace/audit receipt', lane: 'telemetry', proofKeys: ['traceComplete', 'traceEvidence'], traceKinds: ['runtime:close'] }
]);

function asArray(value) { return Array.isArray(value) ? value : []; }
function isObj(value) { return value && typeof value === 'object' && !Array.isArray(value); }
function bool(value) { return value === true; }
function firstDefined(...values) { return values.find((value) => value !== undefined && value !== null); }

function countBy(values) {
  const out = Object.create(null);
  for (const value of values) out[value] = (out[value] || 0) + 1;
  return out;
}

function unique(values) { return [...new Set(values.filter((value) => value !== undefined && value !== null))]; }

function extractTraceEvents(report) {
  const normalized = asArray(report?.normalizedTrace);
  const obs = report?.observations || {};
  const work = asArray(obs?.work?.normalizedTrace);
  const reload = asArray(obs?.reload?.normalizedTrace);
  const all = [...normalized, ...work, ...reload].filter(isObj);
  if (all.length) return all.map((event, index) => ({ order: index + 1, ...event }));
  const kinds = asArray(report?.traceKinds || report?.observations?.allTraceKinds || report?.trace?.kinds);
  return kinds.map((kind, index) => ({ order: index + 1, kind }));
}

function extractTraceKinds(report) {
  return unique([
    ...asArray(report?.traceKinds),
    ...asArray(report?.observations?.allTraceKinds),
    ...asArray(report?.observations?.work?.traceKinds),
    ...asArray(report?.observations?.reload?.traceKinds),
    ...extractTraceEvents(report).map((event) => event.kind)
  ]);
}

function extractProof(report) {
  const proof = isObj(report?.proof) ? report.proof : {};
  const obs = isObj(report?.observations) ? report.observations : {};
  return Object.freeze({ ...obs, ...proof });
}

function capabilityBadges(report) {
  const caps = report?.observations?.work?.capabilities || report?.capabilities || {};
  const page = report?.observations?.work?.page || report?.page || report?.observations?.page || {};
  const browserProof = report?.browserProof === true || Boolean(report?.chromium || report?.cdp || report?.observations?.work?.page);
  return Object.freeze([
    { id: 'node-release-proof', label: 'release-tier proof', status: report?.browserProof === false ? 'observed' : 'not-this-artifact' },
    { id: 'browser-cdp-proof', label: 'managed Chromium/CDP proof', status: browserProof ? 'observed' : 'not-this-artifact' },
    { id: 'cross-origin-isolated', label: 'cross-origin isolated', status: firstDefined(page.crossOriginIsolated, caps.crossOriginIsolated) === true ? 'observed' : 'not-observed' },
    { id: 'worker-agent', label: 'Worker/agent path', status: firstDefined(caps.workers, extractProof(report).workerAgent, extractProof(report).workerPing) ? 'observed' : 'not-observed' },
    { id: 'transferable-object-ref', label: 'transferable object ref', status: extractProof(report).transferDetached === true ? 'observed' : 'not-observed' },
    { id: 'opfs-provider', label: 'OPFS provider', status: firstDefined(caps.opfs, extractProof(report).reloadReadback, extractProof(report).storageWrite) ? 'observed' : 'not-observed' },
    { id: 'storage-lane-adapter', label: 'storage-lane adapter', status: firstDefined(extractProof(report).storageLaneWriteRead, extractProof(report).storageWrite) ? 'observed' : 'not-observed' },
    { id: 'webgpu-performance', label: 'WebGPU/performance', status: 'not-claimed' }
  ]);
}

function stageCards(report) {
  const proof = extractProof(report);
  const kinds = new Set(extractTraceKinds(report));
  return STAGE_DEFS.map((stage, index) => {
    const proofHit = stage.proofKeys.some((key) => bool(proof[key]));
    const traceHits = stage.traceKinds.filter((kind) => kinds.has(kind));
    return Object.freeze({
      order: index + 1,
      id: stage.id,
      title: stage.title,
      lane: stage.lane,
      status: proofHit || traceHits.length ? 'observed' : 'missing',
      proofKeys: stage.proofKeys.filter((key) => bool(proof[key])),
      traceHits,
      requiredTraceKinds: stage.traceKinds.slice()
    });
  });
}

function laneTimeline(report) {
  const events = extractTraceEvents(report);
  const rows = events.map((event, index) => ({
    order: event.order || index + 1,
    lane: event.lane || laneForKind(event.kind),
    kind: event.kind,
    label: event.label || event.op || event.opId || '',
    priority: event.priority || '',
    disposition: event.disposition || '',
    bytes: event.bytes || 0
  }));
  const laneCounts = countBy(rows.map((row) => row.lane || 'unknown'));
  return Object.freeze({ rows, laneCounts, eventCount: rows.length });
}

function laneForKind(kind = '') {
  if (kind.startsWith('storage:') || kind.startsWith('block-store-lane:') || kind.startsWith('storage-lane:')) return 'storage';
  if (kind.startsWith('agent:') || kind.startsWith('object:transfer')) return 'cpu';
  if (kind.startsWith('admission:')) return 'scheduler';
  if (kind.startsWith('channel:') || kind.startsWith('runtime:')) return 'main';
  return 'telemetry';
}

function traceSummary(report) {
  const events = extractTraceEvents(report);
  const kinds = extractTraceKinds(report);
  return Object.freeze({
    eventCount: events.length,
    uniqueKindCount: kinds.length,
    kinds,
    countsByKind: countBy(events.map((event) => event.kind)),
    countsByLane: countBy(events.map((event) => event.lane || laneForKind(event.kind)))
  });
}

function proofReceipt(report, stageRows) {
  const proof = extractProof(report);
  const observedStageCount = stageRows.filter((stage) => stage.status === 'observed').length;
  return Object.freeze({
    status: report?.status || (observedStageCount === STAGE_DEFS.length ? 'passed' : 'partial'),
    observedStageCount,
    requiredStageCount: STAGE_DEFS.length,
    workerAgent: Boolean(proof.workerAgent || proof.workerPing),
    transferDetached: Boolean(proof.transferDetached),
    boundedChannel: Boolean(proof.boundedChannel || proof.boundedChannelOverflow),
    admissionRejectedNoMutation: Boolean(proof.admissionRejectedNoMutation),
    storageLaneWriteRead: Boolean(proof.storageLaneWriteRead || proof.storageWrite),
    reloadReadback: Boolean(proof.reloadReadback),
    traceEvidence: Boolean(proof.traceEvidence || proof.traceComplete)
  });
}

export function createKernelKitDemoObservatoryReport(report, fields = {}) {
  const stages = stageCards(report);
  const trace = traceSummary(report);
  const timeline = laneTimeline(report);
  const receipt = proofReceipt(report, stages);
  const nonClaims = unique([
    ...KERNEL_KIT_OBSERVATORY_NON_CLAIMS,
    ...asArray(report?.nonClaims || report?.non_claims)
  ]);
  return Object.freeze({
    project: 'BrowserRT',
    schema: 1,
    revision: fields.revision || report?.revision || 'rev0044',
    codename: KERNEL_KIT_OBSERVATORY_CODENAME,
    generatedAt: fields.generatedAt || new Date().toISOString(),
    mission: 'Make the Kernel Kit proof legible: show what happened, which lanes participated, what evidence exists, and which claims remain forbidden.',
    sections: KERNEL_KIT_OBSERVATORY_REQUIRED_SECTIONS.slice(),
    sourceProofId: report?.proofId || report?.probe_id || report?.demo_id || 'unknown-proof',
    capabilityBadges: capabilityBadges(report),
    stageCards: stages,
    laneTimeline: timeline,
    traceSummary: trace,
    proofReceipt: receipt,
    nextDemoWork: Object.freeze([
      'Make the page runnable by a human click without CDP-only expression injection.',
      'Add exportable trace receipts for artifact workbench use.',
      'Keep browser/CDP proof explicit by tier/id; do not move it into broad release.',
      'Add OPFS journal/manifest or Worker sync-access-handle storage provider only after preserving current non-claims.'
    ]),
    nonClaims,
    ...fields
  });
}

export function validateKernelKitDemoObservatoryReport(report) {
  const errors = [];
  if (!isObj(report)) return Object.freeze({ ok: false, errors: ['observatory report must be an object'], observedStageCount: 0, traceKindCount: 0 });
  if (report.project !== 'BrowserRT') errors.push('project must be BrowserRT');
  if (!String(report.codename || '').includes('Observatory')) errors.push('codename must mention Observatory');
  const sections = asArray(report.sections);
  for (const section of KERNEL_KIT_OBSERVATORY_REQUIRED_SECTIONS) if (!sections.includes(section)) errors.push(`missing observatory section ${section}`);
  const badges = asArray(report.capabilityBadges);
  for (const id of ['browser-cdp-proof', 'worker-agent', 'transferable-object-ref', 'opfs-provider', 'webgpu-performance']) {
    if (!badges.some((badge) => badge.id === id)) errors.push(`missing capability badge ${id}`);
  }
  const stages = asArray(report.stageCards);
  for (const stage of STAGE_DEFS) if (!stages.some((row) => row.id === stage.id)) errors.push(`missing stage ${stage.id}`);
  const observed = stages.filter((row) => row.status === 'observed').length;
  if (observed < 6) errors.push(`too few observed stages: ${observed}`);
  const traceKinds = asArray(report.traceSummary?.kinds);
  for (const kind of ['runtime:boot', 'agent:result', 'admission:reject', 'storage-lane:dispatch', 'runtime:close']) {
    if (!traceKinds.includes(kind)) errors.push(`missing trace kind ${kind}`);
  }
  const nonClaims = asArray(report.nonClaims);
  for (const claim of KERNEL_KIT_OBSERVATORY_NON_CLAIMS) if (!nonClaims.includes(claim)) errors.push(`missing non-claim: ${claim}`);
  return Object.freeze({ ok: errors.length === 0, errors, observedStageCount: observed, traceKindCount: traceKinds.length, badgeCount: badges.length });
}
