# ADR 0254: Consume exact sparse content from explicit primary peers

Status: accepted deterministic product gate, 2026-08-30; genuine-provider qualification pending.

## Context

ADRs 0242, 0244, and 0245 froze multi-source authority, the bounded content coordinator, and the
exact sparse-availability exchange. ADRs 0249–0252 then activated and qualified only a complete
one-source product path. The live subscriber still treated availability types 30/31 as publisher-
only protocol surface and had no owner-local way to attach another authorized source to an active
pull.

The next boundary is not permissionless discovery, route bonding, or mutable revision selection.
It is the narrower ability to reconstruct one already accepted candidate from complementary primary
Tox peers without allowing any added peer to choose the HEAD or activation state.

## Decision

Local-control v1.40 operation 87 and `iotox sync-source-add JOB_ID FRIEND` attach one source to an
active content-v2 pull. The operation is same-user, process-local intent. Its payload is exactly one
nonzero job identifier as u64 followed by one friend number as u32. The Agent admits only an
application-ready primary Tox session which negotiated feature bit 29.

The subscriber independently requires exact authority-ledger v3 proof, `sync.publish`, and writer
membership for every source. The original `sync-pull` peer remains the sole HEAD authority. Adding a
source cannot request, replace, or accept a HEAD, cannot activate content, and cannot select or
manufacture an auxiliary carrier. The candidate signed-HEAD record remains byte-identical and frozen
for the job.

Once root bootstrap constructs the coordinator, two or more sources receive canonical type-30
requests for the exact current page/chunk window. The subscriber waits for one canonical type-31
result from every registered source, reapplies authority and authenticated-context checks, rejects
conflicting replay or a mismatched window, and installs only the exact returned bitmap. The bounded
coordinator selects a source for each object. The resulting object request, FileId offer, CTA1 record,
completion, cancellation, and retirement all remain bound to that selected source's primary peer
context and stable principal. A new window causes a fresh exact availability round. One-source jobs
retain their complete-source fast path.

Current source disappearance remains fail-closed for the whole pull. It is not silently treated as
an empty availability result and does not trigger auxiliary assignment. Source-loss continuation is
a separate qualification gate.

## Qualification

The owned deterministic registry publishes the same 384 KiB-plus revision independently under two
authorized writer identities, keeps root metadata at both sources, and divides chunk CAS objects
into complementary even/odd stores. The real publisher services answer exact availability requests;
the product subscriber schedules real object requests and FileId joins through two distinct
authenticated contexts. Both providers must contribute availability and objects, after which the
subscriber reconstructs the byte-identical artifact and accepts the originally frozen HEAD last.

Agent, local-control codec, and CLI tests cover operation 87, the v1.40 version boundary, unavailable
peer refusal, parsing, and status counters. The complete 660-check owned registry passes. This is
deterministic product qualification; it is not yet genuine c-toxcore/Sandwurm evidence.

## Consequences

- Sparse availability is now consumed by the product receiver rather than merely published.
- Multi-source means multiple independently authorized primary peers supplying immutable CAS
  objects for one frozen revision. It does not mean multiple routes to one peer.
- The command is deliberately explicit and job-scoped. There is no ambient discovery, automatic
  trust, or durable source subscription.
- Genuine-provider convergence, selected-source loss, content daemon restart, auxiliary carriers,
  multiple simultaneous lanes, comparative performance, and physical-host diversity remain open.
