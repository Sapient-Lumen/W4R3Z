# ADR 0251: Dispatch and maintain content-v2 in the Agent

Status: accepted deterministic Agent product gate; genuine-provider qualification remains open,
2026-08-29.

## Context

ADR 0250 completed the transport-neutral one-source subscriber, but feature bit 29 remained dark.
The Agent did not route its packets or file events, content revisions could not use the ordinary
activation control, and the CAS had no signed reachability, repair, or quarantine boundary. Enabling
only packet dispatch would have advertised a path that could converge bytes but could not safely
recover, inspect, activate, or maintain them.

The first product entrance should exercise the frozen framing without prematurely importing the
multi-source scheduler. It must also preserve the existing rule that an accepted HEAD is not an
activation instruction and that garbage collection never derives deletion authority from missing
metadata.

## Decision

Construct the content publisher and one-source subscriber whenever an enabled namespace store
contains at least one valid `content-v2` policy. Startup recovers exact publication, reconstruction,
and CTA1 staging, then authenticates and walks every persisted live content graph under the namespace
transaction. A missing or conflicting live root is a construction failure. Feature bit 29 remains
absent from the static implemented mask and is added to the frozen HELLO mask only after both content
services and that startup gate succeed.

On a negotiated primary carrier, the Agent now:

1. dispatches canonical content HEAD, object, and availability requests to the publisher and HEAD or
   object results to the subscriber;
2. correlates content jobs before range-v1 jobs, offers each exact FileId to the content subscriber
   first, and routes terminal file truth back into the owning subscriber;
3. starts or exactly retries a one-source `sync-pull`, reports content jobs in `sync-status`, and
   routes `sync-cancel` to the owning engine without making numeric job IDs global aliases;
4. reconstructs and accepts HEAD last through ADR 0250, then permits only an explicit exact-token
   `sync-activate` after whole artifact and manifest verification through content CAS paths; and
5. routes `sync-repair` and `sync-gc` to engine-specific maintenance while preserving their existing
   local-only authority boundary.

Published, accepted, activated, and retained signed roots form the content reachability set. A
published root retains its complete manifest/page/chunk fabric but does not require a duplicate whole
artifact object; accepted and retained roots retain the whole artifact as well. The walker verifies
signed root relationships, rollback-guard consistency, root/page identity, manifest semantics, and
bounded physical inventory. If a required root or page is absent, traversal is incomplete and no
object is classified as unreferenced.

Repair rehashes the strict CAS and moves only digest/name mismatches into an owner-private quarantine.
GC replans authenticated reachability while holding the transaction, freezes exact device/inode/
owner/link/mode/size identities, and uses same-filesystem no-replace rename plus directory fsync. It
has dry-run and quarantine modes only. Purge, remote invocation, automatic startup collection, and
expiry remain absent.

The first live Agent path deliberately uses one complete primary source and one object lane. The
publisher can answer the frozen sparse-availability protocol, but the Agent subscriber does not yet
consume availability, choose partial sources, stripe, or assign content work to auxiliary routes.

## Qualification

The owned registry has 659 checks. A full Agent test builds a paged 384 KiB-plus revision with
multiple manifest pages in a separately owned mock-provider CAS. Through real Agent custom-packet
dispatch and finite-file events it negotiates bit 29, fetches root/pages/chunks, reconstructs the
byte-identical whole artifact, commits accepted HEAD last, explicitly activates the exact record, and
runs content repair plus dry-run GC.

Separate maintenance tests walk a paged graph, quarantine only one unreferenced CAS object, refuse
classification when a required page is missing, and quarantine same-size rooted corruption without
moving valid rooted bytes. GCC builds these paths with warnings as errors. This is deterministic
provider evidence, not a genuine Sandwurm carrier receipt.

## Consequences

- Content-v2 is no longer a dark library feature: a correctly configured Agent can negotiate and use
  the frozen one-source primary-carrier protocol end to end.
- Advertisement is construction truth, not a global compile-time promise. An Agent with no content
  namespace does not advertise bit 29; corrupt live content state prevents startup rather than
  weakening the gate.
- Content convergence still never implies activation, OTA installation, execution, or mutable-device
  authority.
- Genuine direct-UDP and forced-TCP one-source convergence are the next required evidence. Sparse
  availability consumption, multiple simultaneous sources, selected-source loss, auxiliary-carrier
  scheduling, performance comparison, and daemon-restart transport qualification remain later gates.
