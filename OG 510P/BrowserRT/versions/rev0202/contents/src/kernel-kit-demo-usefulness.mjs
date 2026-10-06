import {
  KERNEL_KIT_DEMO_NON_CLAIMS,
  KERNEL_KIT_DEMO_REQUIRED_STEPS,
  createKernelKitDemoTranscript,
  validateKernelKitDemoTranscript,
  summarizeKernelKitDemoTrace,
  scoreKernelKitDemoUsefulness
} from './kernel-kit-demo.mjs';
export const KERNEL_KIT_USEFULNESS_CODENAME = 'Kernel Kit Usefulness Scorecard';
export const KERNEL_KIT_USEFULNESS_REQUIRED_SECTIONS = Object.freeze([
  'beneficiary-fit',
  'workflow-scorecard',
  'earned-evidence',
  'missing-evidence',
  'next-demo-gate',
  'non-claims'
]);
export const KERNEL_KIT_USEFULNESS_AUDIENCES = Object.freeze([
  'browser-ide-and-agent-workbench-builders',
  'heavy-local-web-app-builders',
  'local-first-storage-tool-builders',
  'runtime-library-authors'
]);
export const KERNEL_KIT_USEFULNESS_NON_CLAIMS = Object.freeze([
  ...KERNEL_KIT_DEMO_NON_CLAIMS,
  'No user research claim.',
  'No adoption evidence claim.',
  'No pricing, market-size, or product-market-fit claim.',
  'No claim that this demo is the final product shape.'
]);
const WORKFLOW_DEFINITIONS = Object.freeze([
  {
    id: 'runtime-control-plane',
    lane: 'main',
    title: 'Runtime control plane',
    beneficiaryPain: 'Stop scattering boot/capability/trace setup across app code.',
    evidenceKeys: ['booted', 'boundedChannel'],
    traceKinds: ['runtime:boot', 'channel:create', 'channel:receive']
  },
  {
    id: 'worker-compute-agent',
    lane: 'cpu',
    title: 'Worker compute agent',
    beneficiaryPain: 'Move CPU work off the UI thread with a lifecycle-managed agent.',
    evidenceKeys: ['workerPing'],
    traceKinds: ['agent:spawn', 'agent:ready', 'agent:call', 'agent:result']
  },
  {
    id: 'data-plane-object-ref',
    lane: 'data-plane',
    title: 'Transfer object ref',
    beneficiaryPain: 'Move bytes by ownership transfer instead of giant JS object graphs.',
    evidenceKeys: ['transferDetached'],
    traceKinds: ['object:transfer-ref']
  },
  {
    id: 'overload-governance',
    lane: 'scheduler',
    title: 'Admission/overload gate',
    beneficiaryPain: 'Reject unsafe work without mutating provider state.',
    evidenceKeys: ['admissionAccepted', 'admissionRejectedNoMutation'],
    traceKinds: ['admission:admit', 'admission:reject', 'admission:release']
  },
  {
    id: 'storage-lane-provider',
    lane: 'storage',
    title: 'OPFS storage lane',
    beneficiaryPain: 'Route storage through a provider/adapter surface instead of ad hoc browser APIs.',
    evidenceKeys: ['storageWrite', 'reloadReadback'],
    traceKinds: ['object:opfs-storage-lane-adapter-ref', 'block-store-lane:schedule', 'storage-lane:dispatch', 'storage:opfs-block-put', 'storage:opfs-block-get']
  },
  {
    id: 'trace-receipt',
    lane: 'telemetry',
    title: 'Trace receipt',
    beneficiaryPain: 'Leave behind proof artifacts future sessions can audit and refactor around.',
    evidenceKeys: ['traceComplete'],
    traceKinds: ['runtime:close']
  }
]);
function uniq(list) { return [...new Set(list)]; }
function bool(value) { return value === true; }
function proofOf(report = {}) { return report.proof || report.observations?.proof || report.observations || {}; }
function traceKindsOf(report = {}) {
  return uniq([
    ...(report.traceKinds || []),
    ...(report.observations?.allTraceKinds || []),
    ...(report.work?.traceKinds || []),
    ...(report.reload?.traceKinds || []),
    ...(report.observations?.work?.traceKinds || []),
    ...(report.observations?.reload?.traceKinds || []),
    ...(report.normalizedTrace || []).map((event) => event?.kind).filter(Boolean)
  ]);
}
function hasAll(list, required) {
  const set = new Set(Array.isArray(list) ? list : []);
  return required.every((item) => set.has(item));
}
function workflowStatus(def, proof, traceKinds) {
  const evidenceHits = def.evidenceKeys.filter((key) => bool(proof[key]));
  const traceHits = def.traceKinds.filter((kind) => traceKinds.includes(kind));
  const passed = evidenceHits.length === def.evidenceKeys.length || traceHits.length >= Math.max(1, Math.min(def.traceKinds.length, 2));
  return Object.freeze({
    id: def.id,
    title: def.title,
    lane: def.lane,
    beneficiaryPain: def.beneficiaryPain,
    status: passed ? 'earned' : 'missing',
    evidenceKeys: def.evidenceKeys,
    evidenceHits,
    requiredTraceKinds: def.traceKinds,
    traceHits
  });
}
function beneficiaryFit(workflows) {
  const earned = new Set(workflows.filter((row) => row.status === 'earned').map((row) => row.id));
  const def = (id, label, needs, why) => Object.freeze({
    id,
    label,
    needs,
    earnedNeeds: needs.filter((need) => earned.has(need)),
    missingNeeds: needs.filter((need) => !earned.has(need)),
    fit: needs.every((need) => earned.has(need)) ? 'strong-for-demo-wedge' : 'partial',
    why
  });
  return Object.freeze([
    def('browser-ide-and-agent-workbench-builders', 'Browser IDE / agent workbench builders', ['runtime-control-plane','worker-compute-agent','data-plane-object-ref','trace-receipt'], 'They need worker orchestration, object refs, and proof receipts more than a generic UI widget.'),
    def('heavy-local-web-app-builders', 'Heavy local web app builders', ['worker-compute-agent','data-plane-object-ref','overload-governance','trace-receipt'], 'They need local work to avoid main-thread jank and unbounded queues.'),
    def('local-first-storage-tool-builders', 'Local-first storage/tool builders', ['storage-lane-provider','overload-governance','trace-receipt'], 'They need OPFS/provider boundaries plus honest non-claims around durability.'),
    def('runtime-library-authors', 'Runtime library authors', ['runtime-control-plane','overload-governance','storage-lane-provider','trace-receipt'], 'They benefit from reusable kernel contracts and a testable evidence envelope.')
  ]);
}
export function createKernelKitDemoUsefulnessReport(report = {}, fields = {}) {
  const proof = proofOf(report);
  const traceKinds = traceKindsOf(report);
  const transcript = report.transcript || createKernelKitDemoTranscript(report);
  const transcriptValidation = validateKernelKitDemoTranscript(transcript);
  const workflowScorecard = WORKFLOW_DEFINITIONS.map((def) => workflowStatus(def, proof, traceKinds));
  const earnedWorkflows = workflowScorecard.filter((row) => row.status === 'earned').map((row) => row.id);
  const missingWorkflows = workflowScorecard.filter((row) => row.status !== 'earned').map((row) => row.id);
  const traceSummary = summarizeKernelKitDemoTrace(traceKinds);
  const usefulness = scoreKernelKitDemoUsefulness(report);
  const sections = KERNEL_KIT_USEFULNESS_REQUIRED_SECTIONS.slice();
  const strongBeneficiaries = beneficiaryFit(workflowScorecard).filter((row) => row.fit === 'strong-for-demo-wedge').map((row) => row.id);
  const earnedEvidence = Object.freeze([
    ...earnedWorkflows.map((id) => `workflow:${id}`),
    transcriptValidation.ok ? 'transcript:valid' : 'transcript:incomplete',
    traceSummary.uniqueKindCount >= 8 ? 'trace:multi-lane' : 'trace:thin',
    usefulness.status === 'useful-wedge-earned' ? 'usefulness:wedge-earned' : `usefulness:${usefulness.status}`
  ]);
  const missingEvidence = Object.freeze([
    ...missingWorkflows.map((id) => `workflow:${id}`),
    'market:user-research',
    'production:runtime-hardening',
    'opfs:durability-quota-crash-recovery',
    'browser:cross-browser-mobile-lifecycle',
    'performance:real-device-throughput-latency'
  ]);
  const status = missingWorkflows.length === 0 && transcriptValidation.ok ? 'usefulness-wedge-earned' : 'partial';
  return Object.freeze({
    project: 'BrowserRT',
    revision: report.revision || fields.revision || 'rev0044',
    schema: 1,
    codename: KERNEL_KIT_USEFULNESS_CODENAME,
    purpose: 'Make the Kernel Kit demo answer who benefits, what evidence is earned, and what remains explicitly unproven.',
    sourceProofId: report.proofId || report.probe_id || fields.sourceProofId || 'unknown-proof',
    status,
    sections,
    beneficiaryFit: beneficiaryFit(workflowScorecard),
    strongBeneficiaries,
    workflowScorecard,
    earnedEvidence,
    missingEvidence,
    acceptanceGate: Object.freeze({
      nextGate: 'A future session should be able to open the page, run one workflow, inspect the receipt, and explain the non-claims without reading the whole cube.',
      currentlyEarned: status === 'usefulness-wedge-earned',
      requiredForNext: Object.freeze([
        'single-click run remains human-readable',
        'receipt can be copied/exported or captured by CDP',
        'failure/non-claim panels stay visible',
        'browser-heavy proof stays explicit by id/tier'
      ])
    }),
    transcript: Object.freeze({ status: transcript.status, passedCount: transcript.passedCount, stageCount: transcript.stageCount, validation: transcriptValidation }),
    traceSummary,
    usefulnessScore: usefulness,
    nonClaims: KERNEL_KIT_USEFULNESS_NON_CLAIMS.slice(),
    ...fields
  });
}
export function validateKernelKitDemoUsefulnessReport(report = {}) {
  const errors = [];
  if (!report || typeof report !== 'object') return Object.freeze({ ok: false, errors: ['report must be an object'], earnedWorkflowCount: 0 });
  if (report.project !== 'BrowserRT') errors.push('project must be BrowserRT');
  if (report.codename !== KERNEL_KIT_USEFULNESS_CODENAME) errors.push('codename mismatch');
  if (!hasAll(report.sections, KERNEL_KIT_USEFULNESS_REQUIRED_SECTIONS)) errors.push('missing required usefulness sections');
  if (!Array.isArray(report.workflowScorecard) || report.workflowScorecard.length !== WORKFLOW_DEFINITIONS.length) errors.push('workflowScorecard must include all workflow definitions');
  const earnedWorkflowCount = (report.workflowScorecard || []).filter((row) => row.status === 'earned').length;
  if (earnedWorkflowCount < WORKFLOW_DEFINITIONS.length) errors.push('all Kernel Kit workflows must be earned for this usefulness wedge');
  if (!Array.isArray(report.beneficiaryFit) || report.beneficiaryFit.length < KERNEL_KIT_USEFULNESS_AUDIENCES.length) errors.push('beneficiaryFit missing expected audiences');
  if (!Array.isArray(report.strongBeneficiaries) || report.strongBeneficiaries.length < 3) errors.push('at least three strong demo-wedge beneficiary fits expected');
  if (!report.acceptanceGate?.nextGate || !report.acceptanceGate?.currentlyEarned) errors.push('acceptanceGate must be earned and explain next gate');
  for (const claim of ['No user research claim.', 'No product-market-fit claim.', 'No OPFS durability, fsync, quota, eviction, crash-recovery, browser-restart, or multi-tab coordination claim.']) {
    if (!report.nonClaims?.includes(claim)) errors.push(`missing usefulness non-claim: ${claim}`);
  }
  return Object.freeze({ ok: errors.length === 0, errors, earnedWorkflowCount, strongBeneficiaryCount: report.strongBeneficiaries?.length || 0 });
}
