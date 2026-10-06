# BrowserRT continuation assessment — rev0044

Current revision: rev0055

## Verdict

BrowserRT should continue, but only under a narrower wedge:

> Build a small browser runtime kernel kit for heavy local web apps, not a universal browser operating system yet.

The project is worth continuing because the surrounding ecosystem validates many fragments of the problem: WebContainers shows that browser-resident runtimes are useful; Comlink shows that worker ergonomics are painful; DuckDB-Wasm and SQLite-Wasm show that serious in-browser compute and persistence are real; OPFS, SharedArrayBuffer, WebGPU, and Web Locks show the browser substrate is becoming powerful enough to need coordination.

The project should not continue as unfenced architecture ambition. It should continue only while each step produces executable proofs, audit artifacts, non-claims, and a clearer adoption wedge.

## Who benefits most

The strongest early beneficiaries are:

1. Browser IDE, agent-tool, and artifact-workbench builders.
2. Browser-heavy data, media, and visualization app builders.
3. Local-first tool builders who need honest storage/worker/runtime contracts.
4. Library authors who keep rebuilding worker, storage, IPC, queue, and test harness substrate.
5. Teams trying to shift safe compute or storage to the client for privacy, latency, or cloud-cost reasons.

## Who probably does not need BrowserRT

Simple CRUD apps, marketing sites, small dashboards, and ordinary client apps with little local compute should not adopt it. Apps needing guaranteed durability, OS integration, or proven mobile/cross-browser/performance behavior today should use a native shell, server runtime, or existing focused library.

## What would make this not worth doing

Kill or pivot if:

- tests become too expensive or flaky for cloudtainer iteration;
- architecture surfaces grow faster than useful proofs;
- no tiny integrated demo emerges;
- existing focused libraries cover the first wedge more simply;
- future sessions repeatedly cannot resume the office without confusion;
- the project cannot name a real user who would benefit from the current kernel kit.

## Narrow first wedge

The first product-shaped wedge should be:

> BrowserRT Kernel Kit: worker agents, object refs, bounded mailboxes, OPFS block-store adapter, storage-lane scheduler, overload governors, trace logs, and cloudtainer-friendly test slices.

Do not lead with WebGPU, WebNN, WebRTC, WebTransport, a plugin marketplace, or a full browser OS. Keep those in the dream boundary until repeated evidence says they are ready.

## Current non-claims

- No market validation claim.
- No user-demand proof.
- No product-market-fit claim.
- No production runtime claim.
- No WebGPU performance claim.
- No OPFS durability, quota, eviction, crash-recovery, or browser-restart claim.
- No cross-browser conformance claim.

## Rev0041 audit keywords

continue-but-narrow. BrowserRT Kernel Kit. Who benefits: browser-heavy app builders, browser IDE and agent-tool builders, local-first app builders, data/media web apps, library authors, and privacy/cloud-cost sensitive teams.

No market validation claim. No user-demand proof. No product-market-fit claim. No production runtime claim. No WebGPU performance claim. No OPFS durability, quota, eviction, crash-recovery, or browser-restart claim. No cross-browser conformance claim.
Current audit slice: `facility:project-worth-audit`.

