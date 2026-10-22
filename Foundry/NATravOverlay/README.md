# NATravOverlay / natravcube

**Keep work coherent when the connection changes or disappears.**

NATravOverlay is a persistent node for exchanging authenticated observations, retaining delivery obligations and carrying out narrowly authorized work. Its useful question is not only “can these machines connect?” but “what survived, who authorized the next step, and what actually happened?” A connection, a custodian's acceptance and a final application's receipt answer different questions.

**Current rev0613:** [Complete-source ZIP](https://github.com/Sapient-Lumen/W4R3Z/releases/download/NATravOverlay-rev0613/NATravOverlay-rev0613-COMPLETE-SOURCE.1.zip) · [Matching bootstrap](https://github.com/Sapient-Lumen/W4R3Z/releases/download/NATravOverlay-rev0613/BOOTSTRAPROSE.md) · [Read the bootstrap](BOOTSTRAPROSE.md) · [Release](https://github.com/Sapient-Lumen/W4R3Z/releases/tag/NATravOverlay-rev0613)

The public runtime is named **natravcube**. The supplied complete-source package includes the build output `node/bin/natrav-overlay`; that difference is a rename and packaging distinction, not a missing predecessor. This drop provides the current source, executable, documentation and retained evidence together. Its executable is a compiled runtime, while source custody is supplied by the ZIP. It should not be confused with the newer binary Datacubes that embed an extractable project inside their executable.

## Change the carrier without changing whom you trust

The application stack can work above TCP, direct serial, bounded UDP or Unix datagrams, and explicitly configured packet adapters. An address or device tells the node where to communicate. It does not establish the other party's identity or permission to act.

For packet carriers, the finite packet-link layer reconstructs an ordered stream through bounded fragmentation, acknowledgments, duplicate handling and expiry. An OpenSSL adapter then places TLS above that stream. Peer authentication, the HELLO binding and the reusable NOS1 session protocol remain above the particular carrier. This arrangement lets transport plumbing change without quietly substituting a new trust model.

Above the connection, the node retains accepted evidence, corrections, local projections, delivery obligations and policy history. Computing a derived result and disclosing it remotely are separately authorized activities. An action-admission receipt and the action's eventual terminal result are likewise different records. These distinctions make a retained observation useful after a restart without treating every stored fact as permission for a new action.

## Custody can bridge absence

Imagine an explicitly authorized intermediary taking a bundle from one peer and later offering it to another. The sender and final recipient need not be available in the same instant, but the intermediary must not gain unrestricted forwarding authority merely by receiving the bundle.

The custody machinery starts with an encrypted one-hop capsule and adds a signed route with alternating transfer and acceptance history. Separate durable grants and session rules identify the permitted parties and signing generations. A passive receiver accepts a bounded incoming handoff; a distinct owner-dispatch operation authorizes one outbound offer from a retained receiver case. Receiving A→R does not automatically schedule R→B.

The final recipient's application import is another boundary. A custody service can retain and acknowledge a bundle without thereby proving that an application admitted, acted on or delivered its contents. The project preserves that separation in policy, service code and its returned evidence, rather than leaving it as a warning in the manual.

## What rev0613 makes easier

Suppose the owner requests a dispatch and loses the control response. The existing dispatch path already handles an exact duplicate request by recovering its durable result without another connection, though that recovery can still change local state. A missing reply must not be converted into a fresh dispatch identity or permission to try a different action. Revision 0613 supplies a separate read-only interface: ask what is already recorded, or discover the retained dispatch identities, without invoking the dispatch operation at all.

An exact-status query names the activation, generation and dispatch identity. The observer checks the dispatch index, durable record, current authority, signed offer, envelope metadata and reverse index. It reports reserved and observed attempt counts, retained result metadata and the presence and hash of retained acceptance bytes. That last observation is not a fresh verification of the acceptance signature, and it does not infer application delivery.

The companion inventory walks the existing finite dispatch index and validates every entry before pagination. It sorts canonical request identities, returns bounded metadata after a cursor, and applies both a record limit and an output-byte ceiling. A malformed record cannot be hidden simply by placing it beyond the requested page. The cursor identifies an observation position; it is not a stable snapshot commitment spanning several pages.

Both commands use dedicated noncreating inspection helpers. They do not repair a directory, reserve an attempt, connect to the next hop or schedule a retry. Local-control authorization still applies. This is operational visibility into existing work, not autonomous routing disguised as a status command.

## A source foundation for continued construction

The package's build graph names 94 translation units, with the current native node, its reused foundation subset, documentation, tests and revision evidence present. The source tree is complete for this supplied state; older archives are not required merely because the runtime changed its name. A rebuild still requires the C++20 toolchain and external libraries named by the build recipe. Project completeness and a fully vendored compiler/dependency environment are different things. The supplied runtime targets Linux/x86-64 and still needs appropriate host configuration, identity material, accepted policy and local state.

The retained development history explains how carrier ownership, serial and packet transports, offline capsules, durable custody authority, passive receipt and explicit dispatch came together. Failed attempts and corrected checks are useful construction materials alongside successful receipts. A recipient can inspect those decisions and develop another descendant without inheriting every historical instruction as a new obligation.

For a first reading, begin with the root `README.md` and current-first `BOOTSTRAPROSE.md`, then the custody and dispatch-reconciliation documents. Follow the mechanisms into `node/src/transport.cpp`, the packet-link and TLS implementations, `custody_session_service.cpp`, `daemon.cpp` and `main.cpp`. The revision-0613 status and build records identify the current object; older provenance files retain their own dates.

## Current artifact and evidence

- Source ZIP: 14,183,414 bytes; SHA-256 `54bf003f5f1a0b2c14aa5262211f3c203b3533f7e0b719e267319f28b5f0f7df`.
- `BOOTSTRAPROSE.md`: 88,954 bytes; SHA-256 `798c9e64c7712ec789cb523bbd28cf8ceee9a0b77527f95ff5952e9a3e95545d`.

The supplied bytes are unchanged. Static intake matched all 6,504 source-manifest entries and the included executable's recorded identity. Runtime receipts remain the supplied project's evidence, not an independent security audit or a physical-device qualification. Original attribution and dependency notices remain in context; the [repository owner declaration](../../LEGAL-NOTICE.txt) does not replace third-party terms.

## Changelog

- **Received 2026-10-22 · rev0613** — Exact dispatch status and bounded inventory expose retained work without sending, repairing or inferring delivery.

[Foundry](../README.md) · [Catalog](../../CATALOG.md) · [W4R3Z](../../README.md)
