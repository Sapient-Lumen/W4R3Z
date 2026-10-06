# Continue narrow wedge roadmap

Current revision: rev0054

## Recommendation

Continue BrowserRT, but narrow the next several revisions toward an integrated kernel-kit demo.

## Roadmap

1. Preserve browser-light release and explicit browser tiers.
2. Build one or two more OPFS/provider prerequisites only if they serve the kernel-kit demo.
3. Add an integrated demo proof:
   - boot runtime;
   - spawn worker;
   - transfer object ref;
   - write/read OPFS through adapter;
   - schedule through storage lane;
   - apply one overload governor;
   - emit trace;
   - show artifact.
4. Use that demo to decide whether BrowserRT feels like a product or only infrastructure notes.
5. If the demo is weak, pivot to the test facility and runtime-contract tooling as the valuable artifact.

## What stays shelved

- WebGPU performance claims.
- WebNN/NPU claims.
- WebRTC/WebTransport network behavior claims.
- Mobile/background lifecycle claims.
- Production security sandbox claims.
- Cross-browser conformance claims.
- Native-shell parity claims.

## What would change the decision

Promote the project if the integrated demo makes a hard browser app obviously easier to build. Pivot if the demo cannot name a beneficiary or if future sessions cannot maintain the cube without confusion.

## Rev0041 audit keywords

continue-but-narrow. BrowserRT Kernel Kit. Who benefits: browser-heavy app builders, browser IDE and agent-tool builders, local-first app builders, data/media web apps, library authors, and privacy/cloud-cost sensitive teams.

No market validation claim. No user-demand proof. No product-market-fit claim. No production runtime claim. No WebGPU performance claim. No OPFS durability, quota, eviction, crash-recovery, or browser-restart claim. No cross-browser conformance claim.
Current audit slice: `facility:project-worth-audit`.

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

