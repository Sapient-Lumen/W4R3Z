# ADR 0137: recover from an unusable synchronization basis

Status: accepted

Date: 2026-08-22

## Decision

An accepted artifact is range-reuse input, not authority for a successor. After the subscriber has
committed and independently reverified the successor's complete manifest, it rechecks the exact
artifact named by its current accepted HEAD. If that basis is absent or fails strict size/digest
verification, the subscriber abandons range planning and requests the successor's complete artifact
through the existing whole-object protocol.

The fallback receives a new request message ID, FileId, and durable scheduler attempt. It retains the
same authenticated peer epoch, exact signed successor HEAD, namespace policy, and manifest. The
ordinary object path still requires strict private staging, complete SHA-256 identity, durable attempt
clearance, scheduler commit, and accepted-HEAD-last ordering. Activation remains a separate exact-token
operation. A missing or corrupt basis therefore changes efficiency only; it cannot weaken revision or
activation authority.

Fallback is deliberately narrow. A corrupt successor manifest, storage I/O error, invalid policy,
quota failure, or internal invariant failure remains terminal. The subscriber also does not unlink,
replace, quarantine, or otherwise mutate the unusable basis. Automatic scrub, quarantine, purge, and
repair of a corrupt object occupying the successor's own digest path remain separate destructive-store
work under `../sync-gc-containment-plan.md`.

`sync-status` exposes `range-fallback=1` on the retained pull tombstone. `range-transfer=0` means the
successful artifact path was the complete-object lane; the bounded detail distinguishes an unusable
basis from a valid plan that simply offered no useful reuse.

## Consequences

- Loss or bit corruption in an older accepted artifact cannot prevent convergence on a valid linked
  successor when the complete successor remains available.
- The peer cannot nominate a basis, cause arbitrary-path reads, or turn fallback into implicit
  replacement of local state. Every pathname remains derived locally from policy plus digest.
- Prior accepted and activated records remain unchanged until the fully verified successor commits;
  failure leaves the last signed state authoritative even when its referenced bytes need operator
  repair.
- This is recovery from an unusable optimization, not silent healing of every corrupt store object,
  partial-range continuation, garbage collection, or proof against same-user local tampering.

## Evidence

The owned subscriber gate first completes a genuine range reconstruction, then corrupts the exact
private generation-2 basis without changing its strict file shape. A parent-linked generation-3 pull
commits and verifies its manifest, emits an ordinary artifact request rather than a range request,
commits the exact complete artifact, clears durable attempts, and accepts generation 3 last. The old
corrupt digest path remains present and demonstrably invalid, proving that recovery did not smuggle in
deletion or replacement authority.

The genuine `sync-file-corrupt-basis` Sandwurm cell repeats this boundary with two simultaneous
source-linked IoTox guests. Direct UDP and forced TCP both converge and explicitly activate the same
4 MiB generation-2 successor, report fallback on both roles with zero range-reuse accounting, and
preserve the corrupt old basis. Both compact exports independently reverify; exact bindings are in
`../evidence/2026-08-22-sandwurm-sync-corrupt-basis.md`.
