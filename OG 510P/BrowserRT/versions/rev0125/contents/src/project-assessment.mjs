export const PROJECT_ASSESSMENT_AUDIENCES = Object.freeze([
  'browser-heavy-app-builders',
  'local-first-tool-builders',
  'data-and-media-web-apps',
  'browser-ide-and-agent-tool-builders',
  'library-authors-needing-runtime-substrate',
  'teams-needing-cloud-cost-or-privacy-reduction'
]);

export const PROJECT_ASSESSMENT_POSTURES = Object.freeze([
  'continue',
  'narrow-first-wedge',
  'pause',
  'kill',
  'external-evidence-required'
]);

const REQUIRED_NON_CLAIMS = [
  'No market validation claim.',
  'No user-demand proof.',
  'No product-market-fit claim.',
  'No production runtime claim.',
  'No WebGPU performance claim.',
  'No OPFS durability, quota, eviction, crash-recovery, or browser-restart claim.',
  'No cross-browser conformance claim.'
];

export function createProjectContinuationAssessment() {
  return Object.freeze({
    schema: 1,
    revision: 'rev0044',
    codename: 'Continue Narrow Wedge',
    verdict: 'continue-but-narrow',
    decision: {
      continue: true,
      kill: false,
      pause: false,
      rationale: 'BrowserRT is worth continuing if it stays a substrate project with a narrow first product wedge: browser runtime/test facility plus storage/worker/IPC scheduling primitives for heavy local web apps. It is not yet a product-market-fit win and must not claim production runtime maturity.',
      firstUsefulWedge: 'A BrowserRT kernel kit for heavy browser apps: manifest-driven tests, worker agents, object refs, bounded mailboxes, OPFS block-store adapter, storage-lane scheduling, overload governors, and trace/audit surfaces.',
      strongestReasonToContinue: 'Independent ecosystems already validate fragments of the need: WebContainers prove browser-resident runtime ambition, Comlink proves worker ergonomics pain, OPFS/SQLite/DuckDB-Wasm prove serious in-browser persistence/compute demand, and Tauri/Electron-like tools show appetite for native-feeling local software. BrowserRT targets the missing coordination layer among these primitives.',
      strongestReasonToStop: 'If the project remains only a grand runtime essay with many fake-provider proofs and no developer-facing wedge, it will become architecture cosplay. Continue only while each revision tightens evidence, tests, and a concrete adoption path.'
    },
    beneficiaries: [
      {
        audience: 'browser-heavy-app-builders',
        need: 'coordinated workers, storage, IPC, admission, and traces for applications that feel native but remain pure web',
        benefit: 'a shared runtime contract instead of a pile of one-off browser API wrappers',
        wedgeFit: 'very-high-if-heavy-local-work'
      },
      {
        audience: 'browser-ide-and-agent-tool-builders',
        need: 'fast local artifact, worker, storage, trace, and replay substrate for browser-resident development tools',
        benefit: 'less custom harness code, fewer duplicated worker/storage abstractions, better reproducibility inside constrained sessions',
        wedgeFit: 'very-high'
      },
      {
        audience: 'data-and-media-web-apps',
        need: 'large local datasets or media pipelines without main-thread jank or constant server round trips',
        benefit: 'bounded queues, worker lanes, OPFS refs, explicit capability fallbacks, trace evidence',
        wedgeFit: 'high'
      },
      {
        audience: 'local-first-tool-builders',
        need: 'durable-ish local browser state, sync boundaries, cross-tab coordination, and failure-aware maintenance',
        benefit: 'provider contracts and non-claims keep persistence honest while giving a path to OPFS/Web Locks tests',
        wedgeFit: 'high-but-evidence-gated'
      },
      {
        audience: 'library-authors-needing-runtime-substrate',
        need: 'shared lower-level worker/IPC/storage/testing substrate rather than one-off wrappers',
        benefit: 'reuse of object refs, mailboxes, storage-lane scheduling, audit/test facilities',
        wedgeFit: 'medium-high'
      },
      {
        audience: 'teams-needing-cloud-cost-or-privacy-reduction',
        need: 'shift safe compute/storage to the client while preserving responsiveness and policy boundaries',
        benefit: 'local-first runtime primitives and explicit capability tiers',
        wedgeFit: 'medium-and-external-demand-needed'
      }
    ],
    nonBeneficiaries: [
      'simple marketing sites',
      'ordinary CRUD apps with small state and no heavy local work',
      'apps needing guaranteed durability or OS-level capabilities without a native shell',
      'teams unwilling to configure isolation headers when SAB/high-power features matter',
      'teams needing proven mobile/cross-browser/performance guarantees today'
    ],
    competitionMap: [
      { name: 'Comlink', relation: 'worker RPC ergonomics', BrowserRTGap: 'BrowserRT must not compete as mere RPC; it should provide lanes, memory refs, backpressure, storage, traces, and tests.' },
      { name: 'WebContainers', relation: 'browser-hosted runtime/development environment', BrowserRTGap: 'BrowserRT can be the lower-level coordination kit for apps that need runtime substrate without becoming a Node-in-browser product.' },
      { name: 'workerd / edge runtimes', relation: 'web-compatible JS/Wasm runtime infrastructure', BrowserRTGap: 'BrowserRT stays inside the browser and coordinates browser providers rather than becoming a server runtime.' },
      { name: 'DuckDB-Wasm / SQLite-Wasm', relation: 'serious in-browser compute and persistence', BrowserRTGap: 'BrowserRT should complement these with scheduling, OPFS/provider, mailbox, trace, and test surfaces.' },
      { name: 'Tauri/Electron/native shells', relation: 'native-feeling apps with OS integration', BrowserRTGap: 'BrowserRT cannot claim OS powers; it can help pure-web apps delay or avoid native shells when browser substrate suffices.' },
      { name: 'Ray/Temporal/Durable Objects', relation: 'tasks, actors, object refs, durable histories, coordination owners', BrowserRTGap: 'BrowserRT borrows vocabulary but keeps claims browser-local and capability-gated.' }
    ],
    continuationGates: [
      'Keep release-tier tests under a small cloudtainer budget and browser-heavy proofs explicit by id/tier.',
      'Produce one developer-facing package path: boot runtime, spawn worker, pass object ref, schedule storage op, trace it, audit it.',
      'Promote no provider dream without a proof artifact and non-claim boundary.',
      'After several more slices, build a tiny demo app that uses BrowserRT primitives together rather than only isolated probes.',
      'If no clear wedge emerges after the demo, pivot to the test facility/runtime-contract tooling rather than the entire browser kernel moonshot.'
    ],
    killConditions: [
      'Tests become too expensive or flaky for cloudtainer iteration despite slicing and browser-light release policy.',
      'The codebase grows architecture surfaces faster than executable proofs and audit surfaces.',
      'A strong existing library covers the first wedge more simply and BrowserRT cannot articulate a complementary role.',
      'Future sessions repeatedly cannot resume without confusion even after office-manual and non-claim surfaces.',
      'No useful demo or adopter persona survives narrowing.'
    ],
    externalEvidenceNeeded: [
      'actual developer interviews or usage by browser-heavy app builders',
      'real-device WebGPU/SAB/OPFS performance and failure data',
      'cross-browser conformance trials',
      'mobile/background lifecycle trials',
      'long-session browser profile persistence and eviction observations'
    ],
    recommendedNextWedge: {
      name: 'BrowserRT Kernel Kit',
      elevatorPitch: 'A small browser runtime kit for worker agents, object refs, bounded mailboxes, OPFS block-store adapters, storage-lane scheduling, overload governors, traces, and cloudtainer-friendly tests.',
      notYet: ['full plugin system', 'WebGPU lane', 'WebNN lane', 'WebRTC/WebTransport mesh', 'production durability', 'native shell parity'],
      nextSlices: ['OPFS journal/manifest skeleton', 'OPFS sync worker block-store provider', 'multi-tab Web Locks leader-election smoke', 'tiny integrated demo app']
    },
    requiredNonClaims: REQUIRED_NON_CLAIMS
  });
}

export function validateProjectContinuationAssessment(assessment = createProjectContinuationAssessment()) {
  const errors = [];
  if (!assessment || typeof assessment !== 'object') errors.push('assessment must be object');
  if (assessment.revision !== 'rev0044') errors.push('revision must be rev0044');
  if (assessment.verdict !== 'continue-but-narrow') errors.push('verdict must be continue-but-narrow');
  if (!assessment.decision?.continue || assessment.decision?.kill) errors.push('decision must continue and not kill');
  for (const audience of PROJECT_ASSESSMENT_AUDIENCES) {
    if (!assessment.beneficiaries?.some((row) => row.audience === audience)) errors.push(`missing beneficiary ${audience}`);
  }
  for (const name of ['Comlink','WebContainers','workerd / edge runtimes','DuckDB-Wasm / SQLite-Wasm','Tauri/Electron/native shells','Ray/Temporal/Durable Objects']) {
    if (!assessment.competitionMap?.some((row) => row.name === name)) errors.push(`missing competition map entry ${name}`);
  }
  for (const claim of REQUIRED_NON_CLAIMS) {
    if (!assessment.requiredNonClaims?.includes(claim)) errors.push(`missing non-claim ${claim}`);
  }
  if ((assessment.continuationGates || []).length < 5) errors.push('continuation gates too thin');
  if ((assessment.killConditions || []).length < 5) errors.push('kill conditions too thin');
  if (!assessment.recommendedNextWedge?.name) errors.push('missing recommended next wedge');
  return Object.freeze({ ok: errors.length === 0, errors });
}
