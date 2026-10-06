export const DREAM_BOUNDARY_SCHEMA = 1;
export const DREAM_BOUNDARY_CATEGORIES = Object.freeze([
  'earned-in-cloudtainer',
  'buildable-in-cloudtainer',
  'smoke-testable-in-cloudtainer',
  'needs-external-evidence',
  'shelf-until-repeated-container-evidence'
]);
export const DREAM_BOUNDARY_AREAS = Object.freeze([
  'kernel',
  'storage',
  'ipc',
  'scheduler',
  'mesh',
  'accelerators',
  'network',
  'plugins',
  'devtools',
  'apps'
]);
export function createDreamBoundaryMap() {
  return Object.freeze({
    schema: DREAM_BOUNDARY_SCHEMA,
    title: 'BrowserRT mile-high dream boundary map',
    posture: 'Dream ambitiously, claim narrowly, promote only with evidence.',
    ambitions: Object.freeze([
      {
        id: 'local-userspace-kernel',
        area: 'kernel',
        category: 'buildable-in-cloudtainer',
        dream: 'A browser-resident userspace kernel that owns task lifecycles, object refs, resource lanes, traces, and non-claim boundaries.',
        nearProof: 'Node and browser-light release proofs can exercise fake providers, worker agents, scheduler lanes, and trace surfaces.',
        shelfRule: 'Do not claim production kernel semantics without provider-integrated browser histories and external application runs.'
      },
      {
        id: 'browser-object-runtime',
        area: 'kernel',
        category: 'buildable-in-cloudtainer',
        dream: 'A Ray-like object-ref/task/actor substrate for browser workers, OPFS blocks, streams, shared memory, and GPU buffers.',
        nearProof: 'Fake object refs, transfer refs, block refs, SAB rings, and OPFS block refs can be exercised in release/browser slices.',
        shelfRule: 'Do not claim distributed shared-memory behavior or real cluster semantics.'
      },
      {
        id: 'local-durable-workflows',
        area: 'storage',
        category: 'smoke-testable-in-cloudtainer',
        dream: 'A local Temporal-like history/replay layer for browser jobs, with resumable workflows backed by OPFS manifests and journals.',
        nearProof: 'Fake journal/manifest recovery and OPFS page-reload readback can be tested; browser crash/restart durability remains unearned.',
        shelfRule: 'Shelf durability, crash-recovery, fsync, quota, and eviction claims until repeated browser restart and quota-pressure evidence exists.'
      },
      {
        id: 'same-origin-mesh',
        area: 'mesh',
        category: 'smoke-testable-in-cloudtainer',
        dream: 'A same-origin browser mesh where tabs/workers elect leaders, coordinate storage maintenance, and route tasks through local agents.',
        nearProof: 'Web Locks and BroadcastChannel can be tested with local multi-tab CDP slices.',
        shelfRule: 'Do not claim user-device reliability, mobile background behavior, or multi-browser conformance from cloudtainer-only tests.'
      },
      {
        id: 'accelerator-broker',
        area: 'accelerators',
        category: 'needs-external-evidence',
        dream: 'A lane broker that chooses CPU, WebGPU, WebNN, and possibly WASM/SIMD providers based on calibrated cost and correctness.',
        nearProof: 'Cloudtainer can run capability probes and perhaps SwiftShader/WebGPU smoke kernels; it cannot prove real GPU/NPU performance.',
        shelfRule: 'Shelf performance, thermal, mobile, GPU-driver, and NPU claims until multiple real devices produce comparable traces.'
      },
      {
        id: 'network-transport-broker',
        area: 'network',
        category: 'needs-external-evidence',
        dream: 'A transport broker spanning postMessage, BroadcastChannel, WebRTC data channels, WebTransport streams/datagrams, and server relays.',
        nearProof: 'Local mocks and maybe loopback browser tests can validate API shape; NAT, TURN, HTTP/3, and real WAN behavior need outside evidence.',
        shelfRule: 'Shelf real peer-to-peer, WebTransport, datagram loss, NAT traversal, and latency claims until external network tests exist.'
      },
      {
        id: 'plugin-component-host',
        area: 'plugins',
        category: 'buildable-in-cloudtainer',
        dream: 'A capability-scoped plugin host inspired by WASI and the WebAssembly Component Model: resources, worlds, handles, and explicit rights.',
        nearProof: 'Type surfaces, fake providers, and small Wasm smoke tests can be built locally; robust sandbox security requires external review.',
        shelfRule: 'Do not claim secure sandboxing beyond browser/origin/platform guarantees.'
      },
      {
        id: 'runtime-devtools-flight-recorder',
        area: 'devtools',
        category: 'buildable-in-cloudtainer',
        dream: 'A BrowserRT DevTools/flight-recorder: traces, timelines, queue maps, model histories, replay artifacts, and claim checkers.',
        nearProof: 'Release-tier audit/model artifacts already prove the direction; UI screenshots and trace viewers can be tested with CDP.',
        shelfRule: 'Do not claim browser extension integration or production debugging coverage until tested across real apps.'
      },
      {
        id: 'browser-native-local-app-platform',
        area: 'apps',
        category: 'smoke-testable-in-cloudtainer',
        dream: 'A runtime that lets local-first browser apps feel closer to desktop apps without Electron/Tauri: private storage, workers, offline workflows, and plugin lanes.',
        nearProof: 'Small local apps/demos can be built in the cube; real UX, installability, mobile, filesystem grants, and long-session behavior need broader testing.',
        shelfRule: 'Shelf native-app parity claims until run on real browsers/devices over long sessions.'
      }
    ]),
    unshelfPolicy: Object.freeze({
      rule: 'A shelved capability may be promoted only after repeated, independent cloudtainer evidence or explicit external-device evidence, with artifacts and non-claims updated.',
      minimumContainerEvidence: 'At least three successful sessions across different extracted revisions, each with explicit manifest tasks, artifacts, and no hidden daemon dependency.',
      minimumExternalEvidence: 'At least two device/browser classes for performance, cross-browser, mobile, GPU/NPU, WAN, or quota/eviction claims.',
      alwaysRequired: ['manifest task', 'trace artifact', 'failure mode notes', 'non-claim update', 'source registry update']
    })
  });
}
export function validateDreamBoundaryMap(map = createDreamBoundaryMap()) {
  const errors = [];
  if (map.schema !== DREAM_BOUNDARY_SCHEMA) errors.push('schema mismatch');
  if (!Array.isArray(map.ambitions) || map.ambitions.length < 8) errors.push('expected at least eight ambitions');
  const ids = new Set();
  for (const ambition of map.ambitions || []) {
    if (!ambition.id || ids.has(ambition.id)) errors.push(`duplicate/missing ambition id: ${ambition.id}`);
    ids.add(ambition.id);
    if (!DREAM_BOUNDARY_AREAS.includes(ambition.area)) errors.push(`unknown area: ${ambition.area}`);
    if (!DREAM_BOUNDARY_CATEGORIES.includes(ambition.category)) errors.push(`unknown category: ${ambition.category}`);
    for (const field of ['dream', 'nearProof', 'shelfRule']) {
      if (typeof ambition[field] !== 'string' || ambition[field].length < 20) errors.push(`${ambition.id} missing ${field}`);
    }
  }
  const categories = new Set((map.ambitions || []).map((item) => item.category));
  for (const required of ['buildable-in-cloudtainer', 'smoke-testable-in-cloudtainer', 'needs-external-evidence']) {
    if (!categories.has(required)) errors.push(`missing category ${required}`);
  }
  if (!map.unshelfPolicy?.rule || !map.unshelfPolicy?.minimumContainerEvidence) errors.push('missing unshelf policy');
  return Object.freeze({ ok: errors.length === 0, errors });
}
