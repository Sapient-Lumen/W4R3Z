# Reviewed finite-collection handoff mints exact artifact family and first spec stack

**Tier:** C (RFC → SPEC narrowing cut)  
**Profiles:** B, C, D  
**Pillars:** isolation, operability  
**Patterns:** Broker→Lease→Receipt, Registry→Diff→Gate

`docs/697-reviewed-finite-collection-handoff-current-contract-stack-and-stale-entrypoint-firewall.md` fixed how the recent reviewed finite-collection tightening cluster should be read without stale local summaries. The next small hard decision is no longer about another local boundary inside that cluster.
It is about naming the exact richer family and the smallest spec stack worth implementing.

This doc makes that decision explicit:
**the first richer reviewed finite-collection lane now mints the exact distinct artifact family `ui.collection.handoff.*`, and the first implementation floor is three portable artifacts: `grant`, `manifest`, and `receipt`.**

That is the right next cut because the archive had already earned the hard semantics:
- distinct from ordinary `ui.datatransfer.*`
- single-retrieve by default and auto-stopping after first success
- manifest-first and digest-bound
- read-only only in the first cut
- fresh-rooted retrieve
- B/C/D only, not a fleet-host baseline
- exact result-root evidence

What was still missing was the exact noun set to build.
At this point, keeping that provisional would cost more than deciding it.

This also matches the shape of the external lessons the archive has already been using: XDG's FileTransfer portal uses an explicit transfer session that another app later retrieves by key, while Android keeps narrow document selection separate from broader directory-tree authority instead of pretending both belong to one file-transfer primitive. DeriveBSD should likewise keep its richer selected-set handoff on one explicit family rather than broadening ordinary `ui.datatransfer.*`. 

See also:
- ADR: `adrs/ADR-0288-reviewed-finite-collection-handoff-mints-exact-artifact-family-and-first-spec-stack.md`
- current-stack map: `docs/697-reviewed-finite-collection-handoff-current-contract-stack-and-stale-entrypoint-firewall.md`
- draft RFC: `rfcs/RFC-0194-reviewed-finite-collection-handoff-session.md`
- prior intake split: `docs/672-workstation-richer-datatransfer-lanes-mint-distinct-artifact-families.md`
- queue head: `docs/673-workstation-first-richer-datatransfer-rfc-target-is-reviewed-finite-collection-handoff.md`

## Accepted cut

The accepted first richer family is:

- `ui.collection.handoff.grant`
- `ui.collection.handoff.manifest`
- `ui.collection.handoff.receipt`

The exact first-cut schemas/examples are:

- `spec/ui.collection.handoff.grant.schema.json`
- `spec/ui.collection.handoff.manifest.schema.json`
- `spec/ui.collection.handoff.receipt.schema.json`
- `spec/examples/ui.collection.handoff.grant.json`
- `spec/examples/ui.collection.handoff.manifest.json`
- `spec/examples/ui.collection.handoff.receipt.json`

## What each artifact is for

### 1) `ui.collection.handoff.grant`

This is the reviewed brokered authority artifact for one finite selected-set handoff session.
It names the exact source side and receiving side, stays read-only only in the first cut, stays single-retrieve-autostop in the first cut, and binds the session to one exact `collection_digest`.

This is intentionally **not** ordinary `ui.datatransfer.grant` with a collection flag.
The ordinary family remains the frozen portable baseline.
The richer family must look obviously different at the artifact boundary.

### 2) `ui.collection.handoff.manifest`

This is the authoritative manifest-first review/export surface for the richer lane.
It carries:
- the exact `selected_roots` set,
- the ancestor-closed canonical member list,
- and the authoritative compact identity `collection_digest`.

The digest rule stays the one the archive already accepted:
`collection_digest = sha256(utf8(JCS(authoritative_manifest)))`.

That means the portable compact identity is bound to the canonical reviewed manifest itself, not to tree-summary folklore, traversal order, or broker-local hashing.

### 3) `ui.collection.handoff.receipt`

This is the successful retrieve/materialization evidence surface.
It joins back to the exact grant artifact via `grant_digest`, joins back to the reviewed set via `collection_digest`, and pins the exact created fresh root through a receiver-local authoritative opaque handle.
Under the archive's canonical JSON posture, that means `collection_digest = sha256(utf8(JCS(authoritative_manifest)))` and receipt `grant_digest = sha256(utf8(JCS(grant_artifact)))` for the exact consumed `ui.collection.handoff.grant` artifact, so detached support/export can verify the same chain without broker-local memory.

Any display path, destination label, or other human-facing location text remains advisory and retrieve-frozen when present.
The authoritative result-root join stays handle-first.

## Why this is the right hard decision now

### 1) It turns the RFC from “precise but still provisional” into a buildable floor

The archive had already decided the meaning of the lane.
What was still missing was the exact portable noun set.
Without that, every implementation discussion would re-litigate where selected roots live, what joins the receipt carries, and whether the manifest is really portable or only broker-local.

### 2) It keeps one archive for A/B/C/D without pretending every lane belongs everywhere

This decision keeps the single archive coherent:
- **B / secure workstation** gets the lane it actually needs.
- **C / general-purpose OS** can ship it without creating a second artifact dialect.
- **D / appliance factory/regulatory** can use it in bounded maintenance/factory/review workflows.
- **A / secure fleet host** still stays on rollout/import/export/support/breakglass-shaped answers instead of inheriting workstation file-ferry ergonomics by default.

That is not a fork.
It is the point of profile-shaped defaults and supported lanes.

### 3) It reduces future drift pressure

Once the accepted family is exact, future widening pressure has to declare itself.
If someone wants writable receive, repeated retrieve, bookmark-like reopen, or filesystem-metadata preservation, they now have to say which later lane they are proposing instead of sneaking one more field into the first stack.

## What this still does not decide

This doc does **not** reopen any already-closed boundary inside the reviewed finite-collection queue.
It does **not** add writable receive.
It does **not** add bookmark-like reopen or repeated retrieve after success.
It does **not** widen the lane to A.
It does **not** standardize alias/disambiguation UX, sender-directed placement, or richer filesystem metadata.

Those are later-lane questions.
This doc only fixes the first exact artifact family and first spec stack for the lane already accepted.

## Related docs

- `docs/672-workstation-richer-datatransfer-lanes-mint-distinct-artifact-families.md`
- `docs/673-workstation-first-richer-datatransfer-rfc-target-is-reviewed-finite-collection-handoff.md`
- `docs/681-workstation-finite-collection-handoff-authoritative-collection-identity-stays-digest-bound-to-canonical-manifest.md`
- `docs/687-workstation-finite-collection-handoff-stays-profiled-to-b-c-d-and-not-a-fleet-host-baseline.md`
- `docs/691-workstation-finite-collection-handoff-receipts-pin-the-exact-created-fresh-root.md`
- `docs/697-reviewed-finite-collection-handoff-current-contract-stack-and-stale-entrypoint-firewall.md`
- `rfcs/RFC-0194-reviewed-finite-collection-handoff-session.md`
- `spec/ui.collection.handoff.grant.schema.json`
- `spec/ui.collection.handoff.manifest.schema.json`
- `spec/ui.collection.handoff.receipt.schema.json`

Last updated: 2026-03-23r429
