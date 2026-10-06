# Related-work research pass 035 — mile-high runtime competition and inspirations

Current revision: rev0055

Rev0040 asks what BrowserRT could become if it keeps climbing after the current OPFS/storage-lane bridge. The important conclusion is that BrowserRT should not try to clone any one competitor. Its opportunity is to become a browser-resident runtime layer that steals vocabulary from many systems and keeps the browser-specific boundaries legible.

## Competition and inspiration map

### Browser-hosted runtimes and IDE substrates

**WebContainers** prove that a serious runtime can live inside the browser and expose a development environment rather than just a demo. The steal: make runtime startup, worker communication, file persistence, package/runtime ergonomics, and browser support explicit product surfaces. The boundary: BrowserRT is not trying to be a Node-compatible environment.

### Edge/server JavaScript runtimes

**workerd, Cloudflare Workers, Deno Deploy, Supabase Edge Runtime, and WinterTC** point toward web-interoperable runtime APIs, isolates, local testing, and standards-aligned server runtimes. The steal: BrowserRT should align with web APIs wherever possible, treat provider capability detection as a first-class surface, and avoid inventing needless non-web APIs. The boundary: BrowserRT runs under browser constraints; it cannot assume server process control, sockets, native filesystem semantics, or stable long-running daemons.

### Distributed runtime primitives

**Ray** gives useful vocabulary for tasks, actors, object refs, and object stores. **Temporal** gives durable history, retries, and workflow replay pressure. **Durable Objects** give named coordination owners. The steal: BrowserRT should use object refs, actors/agents, histories, and coordination ownership as runtime-level nouns. The boundary: BrowserRT is not a distributed cluster and does not get server-side durability for free.

### Native/web app shells

**Tauri** and Electron-like shells show the demand for native-feeling applications using web UI. The steal: BrowserRT should make browser apps feel more local and capable without requiring a native shell. The boundary: BrowserRT cannot claim native filesystem, process, OS integration, or mobile background behavior unless tested outside the cloudtainer.

### Capability-oriented component systems

**WASI** and the **WebAssembly Component Model** give BrowserRT a long-term vocabulary for capability handles, resource ownership, interfaces, and plugin worlds. The steal: BrowserRT plugin/process boundaries should feel like explicit capabilities, not hidden globals. The boundary: BrowserRT cannot claim secure sandboxing beyond the browser/platform guarantees and whatever narrow proof it earns.

### Browser power APIs

OPFS, SharedArrayBuffer, Web Locks, WebGPU, WebNN, WebTransport, and WebRTC define the high-ceiling provider frontier. The steal: expose them as optional providers with CPU/mock/fake fallbacks, trace evidence, and capability-gated tasks. The boundary: many of their strongest claims require real devices, real networks, real browsers, or long sessions.

## What this adds to the cube

Rev0040 adds a research-backed separation between **ambition** and **evidence class**. Future sessions should be able to decide whether a feature is:

- release-tier fake-provider work;
- explicit browser/CDP work;
- cloudtainer smoke-only work;
- shelf-until-repeated-container-evidence work;
- external-device-evidence work.

## Research source families registered in this pass

- Browser-hosted runtimes: WebContainers.
- Web-interoperable runtimes: workerd, Workers, Deno Deploy, WinterTC.
- Runtime primitives: Ray, Temporal, Durable Objects.
- Capability plugins: WASI, WebAssembly Component Model.
- Browser provider frontier: OPFS, SharedArrayBuffer, Web Locks, WebGPU, WebNN, WebTransport, WebRTC.
- App shell contrast: Tauri.
