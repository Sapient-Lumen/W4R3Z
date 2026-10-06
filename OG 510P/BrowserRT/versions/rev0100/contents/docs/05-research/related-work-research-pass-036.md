# Related-work research pass 036 — should BrowserRT continue?

Current revision: rev0055

This pass asks whether BrowserRT is a real need or only an attractive architecture exercise.

## Evidence that the direction is real

WebContainers demonstrate browser-hosted runtime demand: development environments and Node-like execution can happen inside a browser tab. BrowserRT should not clone WebContainers, but WebContainers validate the premise that serious runtime substrate in the browser can be valuable.

Comlink demonstrates that worker communication is painful enough that a widely used ergonomic abstraction exists. BrowserRT should not compete as “Comlink, but bigger”; it should absorb worker RPC as a cold-path convenience and focus on lanes, object refs, bounded queues, storage, traces, and tests.

DuckDB-Wasm and SQLite-Wasm/OPFS demonstrate that serious compute and persistence are already moving into browsers. BrowserRT should complement them with scheduling, provider contracts, OPFS adapters, and test facilities rather than trying to replace them.

workerd, Deno, and WinterTC demonstrate that web-platform runtime vocabulary is spreading outside browsers. BrowserRT should stay web-native and capability-gated rather than inventing gratuitous runtime semantics.

Ray, Temporal, Durable Objects, and similar systems validate task/actor/object-ref/history/coordination vocabulary. BrowserRT should borrow the vocabulary, not the distributed-system claims.

Tauri and native-shell frameworks show there is appetite for native-feeling local software. BrowserRT is not a native shell; its value is helping pure browser apps go farther before needing one.

## Evidence against overreach

The browser remains constrained. OPFS is not a durability guarantee. SharedArrayBuffer needs cross-origin isolation. WebGPU/WebNN performance depends on real hardware. WebRTC/WebTransport behavior depends on real networks. Mobile and background lifecycle behavior cannot be fully earned in this cloudtainer.

Therefore, BrowserRT should continue only as an earned staircase: fake-provider/model proofs first, explicit browser slices second, external-device evidence last.

## Research posture

The ecosystem suggests need for a coordination layer, but not automatic demand for BrowserRT specifically. The next proof of worth is not more theory. It is a tiny integrated demo and developer-facing API surface that makes a heavy browser app easier to build.

## Rev0041 audit keywords

continue-but-narrow. BrowserRT Kernel Kit. Who benefits: browser-heavy app builders, browser IDE and agent-tool builders, local-first app builders, data/media web apps, library authors, and privacy/cloud-cost sensitive teams.

No market validation claim. No user-demand proof. No product-market-fit claim. No production runtime claim. No WebGPU performance claim. No OPFS durability, quota, eviction, crash-recovery, or browser-restart claim. No cross-browser conformance claim.

## Rev0049 project-worth carry-forward guard

Current verdict: **continue-but-narrow**. The narrow wedge remains **BrowserRT Kernel Kit**.

Who benefits: browser IDE / agent workbench builders, heavy local browser app builders, local-first app builders, library authors who keep rebuilding worker/storage/trace facilities, privacy/cloud-cost-sensitive teams, and future BrowserRT sessions that need a legible office.

Required non-claims carried forward:

- No market validation claim.
- No user-demand proof.
- No product-market-fit claim.
- No production runtime claim.
- No WebGPU performance claim.
- No OPFS durability, quota, eviction, crash-recovery, or browser-restart claim.
- No cross-browser conformance claim.

