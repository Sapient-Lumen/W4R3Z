# RFC-0194: Reviewed finite collection handoff session

- Status: draft
- Author(s): OpenAI / archive maintenance pass
- Created: 2026-03-22
- Last updated: 2026-03-23r428

## Summary

Design a first richer workstation transfer lane for a **reviewed finite collection handoff**:
a session-bounded way to hand a finite selected set of files and/or directories from one compartment to one receiving lane without widening ordinary `ui.datatransfer.*` into persistent tree authority, ambient shared mounts, or quiet source writeback.

This RFC is explicitly downstream of:
- `adrs/ADR-0261-workstation-ordinary-datatransfer-baseline-stays-frozen-and-richer-lanes-are-rfc-first.md`
- `adrs/ADR-0262-workstation-richer-datatransfer-lanes-mint-distinct-artifact-families.md`
- `adrs/ADR-0263-workstation-first-richer-datatransfer-rfc-target-is-reviewed-finite-collection-handoff.md`
- `adrs/ADR-0264-workstation-reviewed-finite-collection-handoff-stays-single-retrieve-by-default-and-auto-stopping.md`
- `adrs/ADR-0265-workstation-finite-collection-handoff-directory-members-stay-snapshot-shaped-and-no-live-tree-traversal-first.md`
- `adrs/ADR-0266-workstation-finite-collection-handoff-snapshot-membership-stays-manifest-first-and-tree-summary-is-supplementary.md`
- `adrs/ADR-0267-workstation-finite-collection-handoff-first-cut-stays-read-only-and-write-enabled-receive-is-follow-on-rfc-only.md`
- `adrs/ADR-0268-workstation-finite-collection-handoff-first-cut-rejects-symlinks-and-special-files.md`
- `adrs/ADR-0269-workstation-finite-collection-handoff-manifest-entry-floor-stays-content-identity-first-and-stat-light.md`
- `adrs/ADR-0270-workstation-finite-collection-handoff-manifest-order-stays-canonical-by-review-path.md`
- `adrs/ADR-0271-workstation-finite-collection-handoff-authoritative-collection-identity-stays-digest-bound-to-canonical-manifest.md`
- `adrs/ADR-0272-workstation-finite-collection-handoff-review-path-normalization-stays-relative-clean-and-nfc-canonical.md`
- `adrs/ADR-0273-workstation-finite-collection-handoff-top-level-review-names-stay-explicit-and-no-silent-auto-rename.md`
- `adrs/ADR-0274-workstation-finite-collection-handoff-manifest-stays-ancestor-closed-and-no-implicit-parent-synthesis.md`
- `adrs/ADR-0275-workstation-finite-collection-handoff-selected-roots-stay-overlap-free-and-no-silent-subsumption.md`
- `adrs/ADR-0276-workstation-finite-collection-handoff-retrieve-stays-fresh-rooted-and-no-silent-merge-into-existing-tree.md`
- `adrs/ADR-0277-workstation-finite-collection-handoff-stays-profiled-to-b-c-d-and-not-a-fleet-host-baseline.md`
- `adrs/ADR-0278-workstation-finite-collection-handoff-first-implementation-keeps-top-level-aliasing-out-and-collisions-fail-closed.md`
- `adrs/ADR-0279-workstation-finite-collection-handoff-review-ui-may-path-compress-deterministic-ancestor-only-runs.md`
- `adrs/ADR-0280-workstation-finite-collection-handoff-advisory-mime-stays-optional-and-non-authoritative.md`

For the canonical current-stack map over the recent `docs/674-*` through `docs/698-*` reviewed finite-collection tightening cluster, see `docs/697-reviewed-finite-collection-handoff-current-contract-stack-and-stale-entrypoint-firewall.md` rather than relying on this RFC or adjacent local docs to act as the full current companion list. The accepted first exact artifact family/spec stack is then fixed in `docs/698-reviewed-finite-collection-handoff-mints-exact-artifact-family-and-first-spec-stack.md`.

## Motivation

The ordinary workstation `ui.datatransfer.*` lane is now coherent enough to implement, but it is intentionally narrow:
- one-shot by default
- payload-bounded
- exact-payload-bound under reviewed retry continuity
- not a general file-set or directory authority lane

The next practical pressure is usually a user or operator wanting to move a **small selected set of filesystem objects** across the compartment boundary:
- a few screenshots,
- several attachments,
- a selected project folder snapshot,
- or a bounded drag/drop-like handoff.

That need is real, but the archive should answer it with a lane that remains visibly separate from ordinary `ui.datatransfer.*` and that stays much narrower than persistent tree or bookmark-style authority.

## Goals / Non-goals

### Goals

- finite selected set of files and/or directories
- one reviewed handoff session to one receiving lane
- distinct artifact family from ordinary `ui.datatransfer.*`
- session-bounded authority
- single-retrieve by default
- auto-stop after the first successful retrieve
- read-only only in the first cut
- explicit collection membership / review surface
- explicit per-member manifest for snapshot membership
- a small exact per-member manifest floor
- regular-file manifest entries plus explicit directory entries only in the first cut
- explicit receipt/evidence surface
- compatibility with later import / working-copy / reintegration lanes rather than quiet source writeback

### Non-goals

- persistent document-tree authority
- ambient shared folders or shared mounts
- background sync / watcher semantics
- silent writeback to the source lineage
- symlink/device/special-object handoff as part of the first cut
- multi-recipient broadcast as the first richer lane
- retrofitting the ordinary `ui.datatransfer.*` family with “one more mode”

## Proposal

### 1) Keep the richer lane visibly distinct

The accepted archive rule already requires a distinct artifact family. This RFC should therefore avoid ordinary `ui.datatransfer.grant` / `ui.datatransfer.receipt` reuse.

The accepted first exact family is now fixed in `docs/698-reviewed-finite-collection-handoff-mints-exact-artifact-family-and-first-spec-stack.md` as `ui.collection.handoff.grant`, `ui.collection.handoff.manifest`, and `ui.collection.handoff.receipt`, all kept visibly separate from ordinary `ui.datatransfer.*`.

### 1a) Fix the first exact artifact family and spec stack

The first accepted spec-facing stack for this lane is now:

- `ui.collection.handoff.grant` for the reviewed retrieve authority itself
- `ui.collection.handoff.manifest` for the authoritative reviewed selected-set membership and canonical manifest digest input
- `ui.collection.handoff.receipt` for the exact retrieve result, including the result-root evidence joined to the exact grant and collection digests
- matching schemas/examples in `spec/ui.collection.handoff.grant.schema.json`, `spec/ui.collection.handoff.manifest.schema.json`, `spec/ui.collection.handoff.receipt.schema.json`, `spec/examples/ui.collection.handoff.grant.json`, `spec/examples/ui.collection.handoff.manifest.json`, and `spec/examples/ui.collection.handoff.receipt.json`

### 2) Start with finite collection handoff, not persistent authority

The first richer lane should hand off a **finite selected collection**.
The sender chooses a bounded set of objects.
The collection membership then becomes part of the reviewed session story rather than something the receiver can expand later by browsing outward.

For directory-shaped members, the first cut should use **finite reviewed directory snapshot semantics**. Selecting a directory means reviewed snapshot membership at handoff creation time, not live outward traversal of a source tree and not later source-tree growth visibility.

### 2b) Keep snapshot membership manifest-first

The first cut should require an **explicit per-member manifest** for the reviewed finite set.
For directory-shaped members, reviewed snapshot membership should expand into explicit descendant-member entries at handoff creation time rather than staying represented only by a directory handle or only by an aggregate digest.

A tree/collection digest may still be useful as **supplementary summary evidence**, but it should not replace the explicit reviewed member manifest in the first cut.
tree-digest-only or summary-only membership representation should come back only as a later explicit RFC decision, not as the ordinary first-cut surface.

### 2c) Keep the first member-kind vocabulary narrow

The first cut should allow only **regular-file manifest entries** and **explicit directory manifest entries**.
No symlink, device-node, FIFO, or socket member semantics are part of the first cut.
unsupported member kinds must fail closed instead of being silently followed, preserved for later resolution, or omitted.


### 2d) Keep the first manifest floor content-identity-first and stat-light
### 2da) Keep normalized review-path grammar explicit, relative, and clean

The first cut should also define what a **normalized review path** actually is before ordering, duplicate detection, and manifest hashing depend on it.
Every manifest entry's review path should be a **collection-relative identity path**, not a destination-placement hint or source writeback handle.
The normalized form should be a **non-empty UTF-8 text path normalized to Unicode NFC**.
`/` should be the **only separator**. Backslash is never a separator.
Normalized review paths should have **no leading slash**, **no trailing slash**, **no empty segments**, **no repeated separators**, and **no `.` or `..` segments**.
U+0000 NUL is forbidden.
Explicit directories should stay distinguished by **member kind**, not by a trailing slash suffix.
If two source members collapse to the same normalized review path after applying these rules, handoff creation should **fail closed** instead of relying on host filesystem cleanup or UI reconstruction folklore.

### 2db) Keep top-level reviewed names explicit and collision-safe

The first cut should also define how a multi-root reviewed handoff gets its top-level reviewed names.
Those names are part of the authoritative reviewed namespace, not a broker-local extraction convenience.
The broker **must not silently inject a synthetic wrapper root**, must not silently append copy-style or numeric de-duplication suffixes, and must not silently prepend hidden parent directories, volume names, or source identifiers as disambiguators.
The first implementation should **not** support trusted-UI top-level aliasing or other reviewed rename/disambiguation state.
If two top-level selected members collapse to the same normalized reviewed name after accepted normalization, handoff creation should **fail closed** until the selection is revised.
Any later reviewed alias/disambiguation support should return only as a **later explicit RFC/ADR cut** with its own typed reviewed state and exact evidence/export semantics.

### 2dc) Keep manifest ancestry explicit and ancestor-closed

The first cut should also define whether parent directories of reviewed paths are themselves part of the authoritative reviewed artifact.
The authoritative manifest should be **ancestor-closed**.
For every manifest entry whose normalized `review_path` contains `/`, **every proper parent path** of that `review_path` must appear exactly once in the authoritative manifest as an explicit `directory` member entry.
Those ancestor entries are **authoritative reviewed structural state**, not retrieve-time reconstruction hints.
Ancestor closure should be derived mechanically from the final normalized reviewed namespace; it is not a second naming-repair pass and must not invent wrapper roots, hidden source parents, or extra disambiguators.
Receiver/import/materialization code must **not silently synthesize missing parent directories** beyond the destination root; a non-ancestor-closed authoritative manifest should fail closed instead.
Ancestor-only directory entries should remain **stat-light** in the first cut: they carry `review_path` plus `member_kind = directory`, but no file-style payload digest, byte length, or required rich host-stat fidelity.

### 2dd) Keep accepted selected roots overlap-free and non-subsuming

The first cut should also define whether the reviewed root set itself may overlap.
The accepted selected-root set should be **authoritative reviewed state**, even though descendant membership still expands into the authoritative manifest.
After normalized top-level naming, selected roots should form an **overlap-free antichain** in the reviewed namespace.
No selected root may be equal to, an ancestor of, or a descendant of another selected root in that accepted set.
If a sender proposes both an ancestor directory root and one of its descendants, the broker **must not silently** drop the descendant as redundant, keep it only as hidden local review memory, or reinterpret the overlap as one larger reviewed snapshot without trusted review.
The trusted review surface may still ask the user to revise the candidate selection until the accepted roots are overlap-free, but creation should succeed only once the final reviewed root set is already overlap-free.
If overlap remains after normalization, handoff creation should **fail closed**.
Preserving extra “this descendant was also separately selected” intent is out of scope for the first cut unless a later RFC standardizes a distinct reviewed-intent artifact instead of broker-local memory.

### 2dd) Keep authoritative manifest explicit while allowing bounded path-compressed review presentation

The first cut should also define how trusted review may make ancestor-closed structure legible without changing authoritative reviewed state.
The authoritative manifest should stay **fully explicit and ancestor-closed**.
Trusted review UIs may visually path-compress deterministic ancestor-only directory runs for legibility, but only as presentation.
A collapsible run is a contiguous chain of explicit directory entries where each directory in the chain has exactly one reviewed child directory and no direct reviewed file children.
Empty directories, branch points, and ordinary file rows should remain individually visible.
Any collapsed presentation must be derived only from the authoritative manifest, not from source-path breadcrumbs, hidden broker memory, or destination-placement state.
The trusted UI must be able to reveal the full explicit rows before approval/export, and support/export surfaces must continue to rely on the explicit authoritative manifest rather than collapsed shorthand.
Any richer tree-editor/search/filter affordance should come back only as a **later explicit RFC/ADR cut**.

### 2de) Keep the first implementation fail-closed on top-level collisions

The first implementation should also define whether trusted review can rescue multi-root basename collisions by minting reviewed aliases.
It should not.
The first implementation should keep top-level aliasing **out of scope** so the trusted review surface stays a bounded review UI rather than becoming a rename/disambiguation editor.
If two top-level selected members collide after accepted normalization, handoff creation should **fail closed** and require the sender to revise the selection instead of minting reviewed alias state.
Any later alias/disambiguation UX should come back only as a **later explicit RFC/ADR cut** with an explicit reviewed alias as typed reviewed state and exact evidence/export semantics.

### 2df) Keep retrieve fresh-rooted and no-silent-merge into existing tree

The first cut should also define how the reviewed collection lands on the receiver.
Each successful retrieve/materialization should land under a **fresh destination root** created for that retrieve.
The receiver must **not silently** merge the reviewed collection into a pre-existing destination tree, overwrite colliding names, auto-rename around collisions, or short-circuit the collision because matching bytes already exist locally.
If the requested destination placement would reuse a pre-existing tree instead of yielding a fresh destination root, retrieve should **fail closed** until the placement is revised.
Implementation strategy remains open, but the contract-visible result must stay one **fresh-rooted reviewed retrieve**, not a merge into local namespace history.

The first cut should keep the explicit per-member manifest **small and exact**.
Every manifest entry should carry a **normalized review path** that is unique within the reviewed collection and an exact **member kind**.
In plain terms, every entry must carry a normalized review path and exact member kind.
That normalized review path should already follow the relative-clean Unicode-NFC grammar above before it reaches the authoritative manifest.
Every regular-file entry should also carry exact **payload digest** and exact **byte length**.
Explicit directory entries remain reviewed members but do not need file-style payload digest / byte-length fields in the first cut.

MIME type, display labels, last-modified time, owner/group, mode bits, xattrs, thumbnails, and other platform-specific stat fidelity should stay **out of the required first-cut manifest floor**.
If such metadata appears later, it should stay clearly advisory rather than replacing path/kind/payload identity as the authoritative review/export surface.
Richer stat fidelity should come back only as a later explicit RFC decision rather than quietly inflating the first reviewed handoff lane.

### 2dfa) Keep owner/mode/mtime/xattr fidelity out of this lane entirely

The archive should now close the remaining filesystem-metadata loophole instead of leaving it as a standing maybe.
Owner/group fidelity, mode-bit fidelity, mtime fidelity, xattr/ACL/capability fidelity, and similar richer filesystem metadata should stay **out of this lane entirely**, not merely out of the minimum field floor.
Retrieve/materialization may still apply receiver-local defaults or policy-controlled local metadata, but those values count as **receiver-local realization detail**, not portable reviewed state for the handoff itself.
If a later design wants filesystem-metadata preservation, archive-shaped restore semantics, or richer cross-host materialization guarantees, it should come back as a **separate explicit RFC/ADR cut** instead of widening this lane.

### 2dg) Keep retrieve receipts exact on the created fresh destination root

The first cut should also define what a successful retrieve receipt must say about placement.
A successful retrieve/materialization receipt must pin the exact **created fresh destination root** for that retrieve.
That receipt-visible locator must name the result root that was actually created, not merely the parent chooser hint, destination label, or requested placement prompt.
Later rename/move/import/promote actions may mint their own receipts, but they must not retroactively redefine what the original retrieve receipt says the reviewed collection created.
Detached tooling should be able to answer both **which reviewed manifest digest was retrieved** and **which fresh root was created** without reopening broker-local memory or local filesystem history.
Under the archive's canonical JSON posture, that means `collection_digest = sha256(utf8(JCS(authoritative_manifest)))`, and receipt `grant_digest` names the exact consumed `ui.collection.handoff.grant` artifact by digest instead of relying on `lease_id`, a session key, or broker-local reconstruction.
Pathless success prose or parent-only placement evidence is insufficient.

### 2dga) Keep result-root locator handle-first and display-path snapshots advisory

The first cut should also define what kind of locator counts as the authoritative local result locator.
A successful retrieve/materialization receipt should carry a **receiver-local stable result-root handle** for the exact created fresh root.
That handle, not mutable path text, should be the authoritative local result locator for the original retrieve outcome.
An optional path string, destination label, or display-path snapshot may still appear, but it should stay **advisory only**.
Later rename/move/import/promote actions may mint their own receipts, but they should not retroactively redefine the original receipt's result-root handle or turn a later path into the original retrieve outcome.
If a later lane wants portable destination paths, bookmark-like reopen semantics, or stronger cross-host locator guarantees, it should come back as a **later explicit RFC/ADR cut**.

### 2dgb) Keep advisory display snapshots retrieve-frozen when present

If a successful retrieve/materialization receipt carries any advisory human-facing path string, destination label, or display-path snapshot for the created fresh root, that text should count as a **retrieve-time snapshot**.
That advisory snapshot should be **retrieve-frozen** for the lifetime of the original retrieve receipt.
Later local rename/move/import/promote actions may mint successor receipts with their own current path/display snapshots, but they should **not silently rewrite** the original receipt's advisory display snapshot in place.
The original retrieve receipt remains valid even when the advisory snapshot is absent, shortened, filtered, or redacted on some export/support surface, because the authoritative local join still comes from the receiver-local stable result-root handle.
If a later lane wants one mutable current-location story, bookmark-like reopen semantics, or automatic "latest local path" projection, it should come back as a **later explicit RFC/ADR cut**.

### 2dgc) Keep result-root handles opaque and non-path-shaped

The first cut should also define what kind of string the authoritative result-root handle may be.
Even though the handle is receiver-local and stable, it should still remain **opaque and non-path-shaped** on the contract-visible surface.
The authoritative handle should **not** be a filesystem path, URI, sender-provided reviewed name, destination label, or other human-facing placement text reused as the authoritative local join.
Implementations may back that handle with bookmark ids, document ids, database keys, filesystem-handle adapters, or other local mechanisms, but those backend details should stay non-normative as long as the receipt-visible handle remains opaque and non-path-shaped.
If a later lane wants portable destination paths, bookmark-like reopen semantics, or path-derived authoritative locator text, it should come back as a **later explicit RFC/ADR cut**.

### 2dh) Keep placement hints advisory and receiver-local, not reviewed authority

The first cut should also define what any destination-parent or placement affordance means.
Any parent chooser, destination label, suggested folder, or save-into prompt should stay **receiver-local advisory UI state**.
Those hints must **not** become authoritative reviewed state, sender-directed destination policy, or a second reviewed placement contract beside the authoritative manifest and exact result-root receipt.
The grant, authoritative manifest, and receipt-visible reviewed identity should remain complete without carrying a sender-directed destination parent or reviewed placement hint.
A successful retrieve receipt still pins the exact created fresh root, but that does **not** make the earlier chooser hint or destination prompt authoritative reviewed input.
If a later lane wants sender-directed placement, reviewed drop-zone policy, or profile-specific destination semantics, it should come back as a **later explicit RFC/ADR cut**.

### 2e) Keep authoritative manifest order canonical and duplicate-free

The first cut should make the explicit per-member manifest **deterministically serializable** too.
Authoritative manifest entries should appear in **strict ascending bytewise order of normalized review path**.
That ordering must be **locale-independent**, and duplicate normalized review paths must fail closed instead of leaving member precedence to traversal order or UI order.

Source filesystem enumeration order, drag-selection order, display grouping, and member-kind bucket order may still matter for UI presentation, but they should stay **non-authoritative** unless a later RFC explicitly standardizes them.
The first reviewed/exported membership surface should answer the boring question “what exact reviewed set was serialized?” the same way across honest implementations.

### 2f) Keep authoritative collection identity digest-bound to the canonical manifest

The first cut should also carry one **authoritative compact identity** for the reviewed finite set: an **authoritative manifest digest**.
That digest should be computed over the **canonical serialized authoritative per-member manifest**, after the accepted field-floor and canonical normalized-review-path ordering rules have already been applied.
Using the archive's existing canonical JSON rule, that compact identity should be **`sha256(utf8(JCS(authoritative_manifest)))`**.

Grants, receipts, detached review, compare/export tooling, and support bundles should treat that authoritative manifest digest as the portable compact handle for the reviewed finite collection.
Aggregate tree/collection digests may still exist as **supplementary summary evidence**, but they should not replace the authoritative manifest digest in the first cut.
Any later tree-summary or directory-summary digest work should stay secondary unless a later RFC explicitly proves a better authoritative compact identity than the canonical manifest digest.

### 3) Keep the first cut read-only only

The first richer lane should be **read-only only** in its first cut.
No write-enabled receive exception is part of the first cut.
If writable receive is ever worth designing later, it should arrive only as a **follow-on RFC/ADR decision**, not as an option quietly retained inside this first lane.

### 4) Keep the lane session-bounded

Authority should die with the handoff session.
The first richer lane should not act like a bookmark, a remembered grant, or a background mount that outlives the session unless a later, separate decision proves that value outweighs the added laundering and support cost.

### 4a) Keep the lane profiled to B/C/D and out of fleet-host baseline

The first reviewed finite-collection handoff family should stay supported for **B/C/D**, not **A**.
For **B**, this is a direct human-facing workstation need.
For **C**, it remains a bounded compatibility/developer ergonomic lane rather than ambient shared-tree authority.
For **D**, it may exist only on explicit factory, maintenance, approval, or quarantined ingest/export stations and workflows, not as ambient production-image runtime convenience.
For **A**, the baseline answer should remain rollout, support-bundle, import/export, or breakglass/operator lanes rather than ad-hoc reviewed file ferrying on fleet hosts.
If fleet-host workflows later prove they need a richer host-local file-ferry surface, that should return as a **distinct later RFC/ADR lane**, not by silently widening this workstation family.

### 4b) Keep advisory MIME optional and non-authoritative

Advisory MIME stays optional descriptive metadata and must not become authoritative reviewed identity for the first richer lane.
A valid first-cut authoritative manifest remains complete without MIME when it already carries the accepted normalized review path, member kind, and regular-file payload digest + byte length floor.
If implementations choose to compute or display advisory MIME, that data must remain descriptive only: it must not override member kind, payload identity, ordering, normalization, or any fail-closed decision already bound to the authoritative manifest.
The first cut must not require a MIME detector, MIME registry, filename-extension table, or broker-local classification service to produce or verify the authoritative manifest.
Any later lane that wants mandatory reviewed content classification should come back as a **distinct later RFC/ADR cut**, not as silent inflation of this baseline.

### 5) Re-enter existing authoring lanes on mutation


If the receiver wants to edit the handed-off material, the design should prefer re-entry into existing import / working-copy / reintegration lanes rather than turning the richer handoff lane itself into quiet source-authority writeback.

### 6) Keep the first cut single-retrieve by default and auto-stopping

The first cut should keep retrieve semantics boring:
- **single-retrieve by default**
- **auto-stop after the first successful retrieve**
- no repeated-retrieve posture in the first cut

If repeated retrieve is ever worth standardizing later, it should come back as an explicit follow-on RFC decision rather than hiding inside the default richer lane.

## Alternatives considered

### Make multi-delivery clipboard history the first richer lane

Rejected as first priority because it mainly widens replay convenience without addressing the more common selected-files / selected-folder handoff pressure.

### Make persistent document-tree authority the first richer lane

Rejected as first priority because it is broader, more stateful, and harder to keep audit-friendly than a reviewed finite collection handoff.

### Make the first richer lane write-enabled from day one

Rejected because the first cut should learn collection membership, retrieve semantics, and bounded lifetimes before it also takes on mutation and conflict semantics.

### Keep a narrowed write-enabled exception inside the first RFC

Rejected because it preserves a standing scope-creep seam inside the first cut and blurs the boundary between handoff lanes and existing import / working-copy / reintegration lanes.

### Keep repeated-retrieve posture open in the first cut

Rejected for now because the first richer lane is already broader than ordinary `ui.datatransfer.*` by being collection-shaped; adding replay-friendly retrieve semantics at the same time would make the first cut harder to reason about and easier to launder into convenience authority.

### Treat A as a baseline profile for the same richer lane

That would blur a human-facing reviewed file handoff into a fleet-host admin primitive.
If fleet hosts later need a richer operator file-ferry surface, that should come back as a distinct lane with artifacted operator semantics rather than widening this family.

### Support trusted-UI top-level aliasing in the first implementation

Rejected for now because it would widen the first trusted review surface into a rename/disambiguation tool before the archive has earned the narrower reviewed-membership lane. A later explicit RFC/ADR can still standardize typed reviewed alias state if real practice proves it worth the extra entropy.

### Leave retrieve success pathless or parent-only in receipts

Rejected because it would force detached support/export back onto broker-local history, parent chooser folklore, or later move/import notes when the archive already decided retrieve itself must materialize under one fresh root.

### Make mutable path text the authoritative local result locator

Rejected for now because the first cut keeps the receiver-local stable result-root handle authoritative for the original retrieve outcome, while any display-path snapshot or later renamed location stays descriptive only.

### Make parent chooser or sender-suggested destination placement authoritative

Rejected for now because it would widen the first richer lane from reviewed collection handoff into reviewed receiver-local namespace policy. The first cut keeps parent chooser and destination-label affordances as local advisory UI state; any real sender-directed placement semantics must return as a later explicit lane.

### Make the authoritative result-root handle a path string or URI

Rejected for now because that would reopen mutable-path and reopen/bookmark drift inside the slot that is supposed to keep the original retrieve outcome handle-first. The first cut keeps the authoritative result-root handle opaque and non-path-shaped, while any human-facing path/display text stays advisory only.

### Rewrite the original advisory display snapshot after later local rename or move

Rejected for now because it would turn the original retrieve receipt into a mutable current-location note. The first cut keeps any advisory path/display text retrieve-frozen when present, and requires later rename/move/import/promote acts to mint successor receipts if they want to describe current local location.

### Standardize owner/mode/mtime/xattr fidelity later inside this same lane

Rejected for now because it would turn the reviewed finite-collection handoff into a filesystem-preserving archive format inside the same contract surface. The first cut keeps owner/group, mode-bit, mtime, xattr, ACL, and similar richer filesystem metadata out of this lane entirely; any future filesystem-metadata-preserving design must return as a separate explicit lane.

### Allow retrieve to merge into an existing destination tree

Rejected for now because merge/overwrite/auto-rename/same-bytes reuse are all real policy choices, and leaving them implicit would make receiver-local namespace state part of the reviewed handoff story again.

### Make advisory MIME mandatory for this lane

Rejected for now because the first richer lane already has a coherent path/kind/payload identity floor, while mandatory MIME would add detector/registry variability and implementation baggage without earning a smaller or safer first contract. If stronger reviewed content classification proves necessary later, it should return as a distinct later lane instead of inflating this baseline.

### Leave authoritative manifest order unspecified

Rejected because manifest-first review without deterministic ordering still leaves digest/export behavior implementation-defined and turns source traversal or selection order into accidental authority.

## Backwards compatibility

The RFC no longer leaves the final richer-lane family unnamed: the accepted first stack is now `ui.collection.handoff.*` with matching schemas/examples, and future widening work must extend or replace that stack explicitly instead of pretending the first implementation nouns are still provisional.

## Security considerations

- collection membership must be explicit and reviewable
- the receiver must not gain ambient discovery outside the finite selected set
- directory members should not silently become live open-ended tree grants
- snapshot-shaped directory membership should stay reviewable as a finite selected set, not a browse-later authority story
- authoritative result-root handles should stay opaque and non-path-shaped, so mutable path text or URI-looking locator strings cannot quietly retake authority under a new field name
- explicit per-member manifest is the first-cut review/export surface; aggregate digests are supplementary summary evidence, not a substitute
- first-cut member kinds stay regular-files-plus-explicit-directories only; symlinks and special objects are out of scope unless a later RFC explicitly reopens them
- the first-cut manifest floor stays path/kind/payload identity first: normalized review path + member kind for every entry, plus exact payload digest + exact byte length for regular files
- normalized review paths stay collection-relative, clean slash-separated Unicode NFC text with no leading/trailing slash, no empty or dot segments, no NUL, and collisions after normalization fail closed
- top-level reviewed names stay explicit reviewed state: no silent wrapper-root injection or silent copy-style auto-rename, and the first implementation fails closed on top-level collisions instead of minting reviewed alias state
- authoritative manifest ancestry stays explicit and ancestor-closed: every proper parent path of each nested `review_path` must be present as an explicit directory entry, and receivers must not silently synthesize missing parent directories later
- trusted review may still use bounded manifest-derived path-compression of deterministic ancestor-only directory runs, but collapsed presentation must remain revealable and never replace the explicit authoritative manifest
- advisory MIME stays optional descriptive metadata and must not become authoritative reviewed identity; detectors, registries, or filename-extension folklore are not required to produce or verify the first-cut authoritative manifest
- selected roots stay overlap-free after normalization: ancestor/descendant root overlap must fail closed instead of silently collapsing into one larger reviewed snapshot or hidden broker memory
- retrieve/materialization stays fresh-rooted: the reviewed collection must not silently merge into an existing destination tree, overwrite names, auto-rename around collisions, or reuse same-bytes local state as hidden acceptance policy
- successful retrieve/materialization receipts must pin the exact created fresh destination root rather than only a parent chooser hint or pathless success prose
- parent chooser, destination label, suggested folder, or save-into prompt remain receiver-local advisory UI state rather than authoritative reviewed placement policy
- if present, any advisory human-facing path/display snapshot on the original retrieve receipt stays retrieve-frozen rather than silently rewriting itself after later local rename/move/import/promote state
- the first-cut authoritative compact identity is the manifest digest over the canonical serialized authoritative manifest, not a tree-summary or implementation-local traversal hash
- the first richer finite-collection handoff family stays supported for B/C/D, while A keeps rollout/support/import-export/breakglass-shaped answers instead of reusing this workstation lane
- owner/group, mode-bit, mtime, xattr, ACL, and similar richer filesystem metadata stay out of this lane entirely; receiver-local materialized metadata remains realization detail rather than portable reviewed truth
- authoritative manifest order stays canonical by normalized review path, locale-independent, and duplicate-free
- authoritative compact collection identity stays digest-bound to the canonical serialized manifest
- write-enabled receive is deferred out of the first cut and should be treated as a separate future risk family, not a standing option inside the first lane
- session lifetime must be explicit so the lane does not decay into a hidden persistent mount or bookmark
- repeated retrieve is a separate replay-width risk and should not quietly ride along in the first cut

## Open questions

No standing open questions remain inside this first reviewed finite-collection lane after the current narrowing cuts. Any future filesystem-metadata-preserving, bookmark-like, or write-enabled reopen work should return as a separate explicit RFC/ADR lane on top of — not in place of — the accepted first `ui.collection.handoff.*` spec stack.
