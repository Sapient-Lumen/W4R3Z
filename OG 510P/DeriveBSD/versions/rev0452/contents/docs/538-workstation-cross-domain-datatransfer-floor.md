# Workstation cross-domain data-transfer floor

**Tier:** B (Base contract boundary)  
**Profiles:** A, B, C, D  
**Pillars:** isolation, operability  
**Patterns:** Broker→Lease→Receipt, Adapter→Shadow→Replace  

`docs/537-workstation-remoted-session-surface-boundary.md` already decided that clipboard, file selection, print, camera/microphone, and similar crossings stay outside the session surface.
This doc makes the next small but expensive cut:
**clipboard and file transfer stay separate brokered lanes, and the baseline workstation floor does not require ambient shared clipboard sync or cross-domain drag&drop.**

See also:
- ADR: `adrs/ADR-0128-workstation-cross-domain-datatransfer-floor.md`
- data-transfer portal notes: `docs/205-data-transfer-portals-clipboard-and-dnd.md`
- workstation host/AppVM boundary: `docs/457-workstation-host-ui-and-appvm-boundary.md`
- desktop viability checklist: `docs/410-desktop-viability-checklist.md`

## Why this needs a hard decision

Once the GUI boundary is host-owned and session-surface-first, cross-domain data movement becomes the next place ambient authority tries to sneak back in.
If the archive does not choose, people will naturally reach for the easiest thing:

- a hidden cross-domain clipboard sync service,
- ambient clipboard/history authority in the trusted host,
- cross-domain drag targets as a day-one expectation,
- or file movement disguised as “paste” and “open” behavior.

That would rebuild exactly the kind of invisible privilege expansion the workstation story is trying to prevent.

## Accepted baseline

For the ordinary workstation lane:

- there is **no ambient shared clipboard** across host/AppVM or AppVM↔AppVM boundaries
- cross-domain clipboard transfer is **explicit, directional, and single-delivery by default**
- the host clipboard is **host-local**; the cross-domain lane uses a separate broker/session/offer path
- ordinary workstation viability requires **bounded text clipboard transfer** plus **explicit file export/import**
- cross-domain drag&drop is **not baseline**
- in other words: **cross-domain drag&drop is not baseline** for the ordinary workstation lane
- clipboard/history-manager authority across compartment boundaries is not baseline and must not hide in the host

That same anti-ambient posture now carries into the first richer finite-collection lane too: `docs/693-workstation-finite-collection-handoff-result-root-locator-stays-handle-first-and-path-snapshot-advisory.md`, `docs/694-workstation-finite-collection-handoff-advisory-display-snapshot-stays-retrieve-frozen.md`, and `docs/695-workstation-finite-collection-handoff-result-root-handle-stays-opaque-and-non-path-shaped.md` keep successful retrieve joined through an authoritative receiver-local stable result-root handle that stays opaque and non-path-shaped, while any human-facing path/display text remains advisory only.
- reviewed retry/re-offer remains a fresh grant story, and explicit successor continuity uses `renewal_posture` plus `supersedes_grant_digest` rather than in-place extension or latest-wins grant folklore
- that successor continuity is only for the same actor pair and same-or-narrower offer scope; wider MIME/byte/source/destination changes are fresh-grant required and should not hide behind retry wording
- that successor continuity is also exact-payload-bound through payload digest (`offer.payload_digest`); semantic-equivalence rebinding or payload substitution is fresh-grant required
- that successor continuity also keeps `constraints.requires_foreground` exact; add/drop/swap of the foreground requirement is fresh-grant required rather than old-story retry convenience
- that successor continuity also keeps exact `constraints.expires_at`; add/drop/swap of the reviewed outer absolute-expiry ceiling is fresh-grant required instead of successor folklore
- that successor continuity also keeps `delivery_mode` exact; one-shot review must not quietly become multi-delivery retry authority under the old story
- that successor continuity also keeps `constraints.rate_limit` exact; old-story retry must not quietly change reviewed throttling posture
- ordinary `ui.datatransfer.grant.constraints` is a closed-world typed vocabulary; hidden extra `constraints.*` keys are not baseline and future extra posture needs an ADR/spec change
- Wayland clipboard-manager protocols remain privileged control surfaces, not baseline client behavior

The mental model should be “send this clipboard payload there,” not “all compartments share one clipboard now.”

## Practical transfer model

### Clipboard text / bounded payloads

The smallest useful ordinary lane is:

- source compartment requests export of text / bounded clipboard payload
- broker creates a typed offer/grant with MIME, size, expiry, and delivery posture
- destination compartment explicitly accepts or retrieves that offer
- broker emits a transfer receipt
- that receipt keeps `offer_source_subject` exact while subject remains the consumer/recipient on the ordinary read side
- single-delivery grants exhaust by default

That keeps the common “copy a URL / token / snippet” use case workable without creating global shared state. `docs/657-workstation-ocr-text-egress-stays-explicit-plain-text-single-delivery.md` now makes one follow-on explicit too: copied OCR-derived text from searchable foreign inspection should reuse this same plain-text, single-delivery broker lane instead of quietly reopening ambient clipboard/export behavior. `docs/659-workstation-datatransfer-receipts-join-exact-grants-by-digest.md` then fixes the next evidence join too: receipts should also carry `grant_digest`, so support/export can answer which exact grant artifact was consumed rather than reconstructing policy from `offer_id` and `lease_id`. `docs/661-workstation-datatransfer-grants-carry-exact-effective-until-and-late-delivery-fails-closed.md` then fixes the next lifetime join too: ordinary grants publish exact `effective_until`, successful transfer must not land later than that joined deadline, and later retry is fresh grant / re-offer required. `docs/662-workstation-datatransfer-renewals-stay-successor-grants-and-predecessor-digest-linked.md` then fixes the next continuity join too: any reviewed retry must mint either a `fresh-grant` or a successor grant that names the exact prior grant digest instead of mutating the old grant in place. `docs/663-workstation-successor-datatransfer-grants-stay-same-actor-pair-and-no-wider-offer.md` then fixes the next scope join too: successor continuity stays same-actor-pair and no-wider-offer, so broader MIME/byte/source/destination changes are fresh-grant required rather than successor folklore. `docs/664-workstation-successor-datatransfer-grants-keep-payload-lineage-and-redaction-posture-exact.md` then fixes the next payload join too: reviewed successor continuity must also preserve exact payload lineage and redaction posture, so `offer.content_source` and `offer.redaction_profile_digest` cannot silently change under the old story. `docs/665-workstation-successor-datatransfer-grants-stay-exact-payload-bound-and-no-semantic-equivalence-rebinding.md` then fixes the next exact-bytes join too: reviewed successor continuity is exact-payload-bound through payload digest (`offer.payload_digest`), so newly rendered or semantically equivalent bytes are fresh-grant required instead of old-story folklore. `docs/666-workstation-successor-datatransfer-grants-keep-foreground-requirement-exact.md` then fixes the next interactivity join too: reviewed successor continuity also preserves exact `constraints.requires_foreground`, so retry cannot silently become background-capable under the old story. `docs/667-workstation-successor-datatransfer-grants-keep-delivery-mode-exact.md` then fixes the next replay-width join too: reviewed successor continuity also preserves exact `delivery_mode`, so a one-shot reviewed transfer cannot silently become multi-delivery authority under successor wording.

### Files stay a separate lane

Files should remain explicit export/import acts.
That may still use the same broker family and evidence style, but it is not the same thing as ambient clipboard sharing.

This matters because file authority is usually broader, longer-lived, and more review-sensitive than text transfer.

### Drag&drop is deferred

Bounded cross-domain drag&drop may become useful later.
But the archive should not pretend it is required before the basic workstation lane is coherent.

Cross-domain drag targets are implementation-heavy and easy to turn into hidden ambient data paths.
The baseline should optimize for explicit transfer first.

## Artifact decision: make delivery posture explicit

DeriveBSD already has typed data-transfer artifacts:

- `spec/ui.datatransfer.grant.schema.json`
- `spec/ui.datatransfer.receipt.schema.json`
- `docs/658-workstation-datatransfer-evidence-binds-offer-source-and-transfer-subjects-exactly.md`
- `docs/660-workstation-single-delivery-datatransfer-grants-stay-one-shot-and-fresh-grant-required.md`
- `docs/659-workstation-datatransfer-receipts-join-exact-grants-by-digest.md`

To keep the new floor implementable instead of rhetorical:

- grants must state a typed `delivery_mode`
- grants/receipts must carry exact `offer_source_subject` so the offer side stays visible in the artifact itself
- the baseline value is `single-delivery`
- receipts should say whether the grant was exhausted after use
- receipts should also carry `grant_digest` so detached tooling can join back to the exact reviewed grant artifact
- and in the ordinary lane, the first successful read-side transfer exhausts the grant, so retry/recovery is fresh grant / re-offer required rather than replay/history resurrection (see `docs/660-workstation-single-delivery-datatransfer-grants-stay-one-shot-and-fresh-grant-required.md`)

That keeps “clipboard clears on delivery” or “multi-delivery exception” out of broker folklore and inside reviewable artifacts. It also means successor retry continuity is about the same reviewed payload story, not merely the same actors, MIME envelope, lineage hints, interactivity posture, or UI wording.

## What this buys

### 1) No stealth global clipboard

A host-side clipboard manager no longer becomes a stealthy ambient data broker across compartments.

### 2) Better receipts and support surfaces

A support/export surface can answer:

- which compartment offered the data (`offer_source_subject`)
- which compartment accepted it (`subject` on the ordinary read-side receipt)
- whether it was clipboard text or file transfer
- what MIME and size policy applied
- whether the transfer was single-delivery and exhausted
- whether recovery now requires a fresh grant / re-offer because the ordinary grant was one-shot

That is much easier to reason about than “the clipboard happened to contain something at the time.”

### 3) A smaller workstation floor

The ordinary workstation lane only has to solve explicit transfer and explicit file movement.
It does **not** require cross-domain drag targets, cross-domain clipboard history sync, or a fully reconstructed host-native DnD/windowing substrate.

## What is explicitly not baseline

The ordinary workstation lane does **not** require:

- ambient host↔AppVM shared clipboard synchronization
- persistent cross-domain clipboard history as ordinary behavior
- cross-domain drag&drop as a hidden day-one requirement
- host clipboard managers with compartment-spanning privilege by default
- hidden helper daemons that mirror clipboard state between compartments

## Future bounded lane

A future bounded drag&drop or richer clipboard lane may still be useful.
But it should only arrive after an explicit RFC/ADR answers:

- how MIME/size/type policy stays visible,
- how clipboard/history authority stays reviewable,
- how single-delivery defaults are relaxed without recreating ambient state,
- and how receipts remain intelligible in support/export surfaces.

Until then, the archive should optimize for explicit transfer.

## Related docs

- `docs/205-data-transfer-portals-clipboard-and-dnd.md`
- `docs/410-desktop-viability-checklist.md`
- `docs/457-workstation-host-ui-and-appvm-boundary.md`
- `docs/537-workstation-remoted-session-surface-boundary.md`
- `spec/ui.datatransfer.grant.schema.json`
- `spec/ui.datatransfer.receipt.schema.json`
- `docs/658-workstation-datatransfer-evidence-binds-offer-source-and-transfer-subjects-exactly.md`

- grants should also carry exact `effective_until` so detached tooling can answer the reviewed transfer deadline directly
- successful ordinary transfer must not be later than the joined grant `effective_until`; late delivery fails closed and later retry is fresh grant / re-offer required
- `docs/661-workstation-datatransfer-grants-carry-exact-effective-until-and-late-delivery-fails-closed.md`
- `docs/662-workstation-datatransfer-renewals-stay-successor-grants-and-predecessor-digest-linked.md`
- `docs/663-workstation-successor-datatransfer-grants-stay-same-actor-pair-and-no-wider-offer.md`
- `docs/664-workstation-successor-datatransfer-grants-keep-payload-lineage-and-redaction-posture-exact.md`
- `docs/665-workstation-successor-datatransfer-grants-stay-exact-payload-bound-and-no-semantic-equivalence-rebinding.md`
- `docs/666-workstation-successor-datatransfer-grants-keep-foreground-requirement-exact.md`
- `docs/667-workstation-successor-datatransfer-grants-keep-delivery-mode-exact.md`
- `docs/668-workstation-successor-datatransfer-grants-keep-rate-limit-posture-exact.md`
- `docs/669-workstation-successor-datatransfer-grants-keep-absolute-expiry-posture-exact.md`
Successor reviewed retry continuity stays explicit and narrow too: `docs/663-workstation-successor-datatransfer-grants-stay-same-actor-pair-and-no-wider-offer.md` keeps successor grants carrying `successor_scope_posture`, and that successor path is only for the same actor pair with the same or narrower typed offer envelope rather than widened source/destination or broader MIME/byte scope. `docs/664-workstation-successor-datatransfer-grants-keep-payload-lineage-and-redaction-posture-exact.md` then makes the same-story rule stricter again: successor continuity also keeps payload lineage and redaction posture exact, so `content_source` and `redaction_profile_digest` cannot quietly change under familiar retry wording. `docs/665-workstation-successor-datatransfer-grants-stay-exact-payload-bound-and-no-semantic-equivalence-rebinding.md` narrows the same lane one notch further: successor continuity also keeps exact payload digest parity, so semantically equivalent or re-rendered bytes must go back through a fresh reviewed grant. `docs/666-workstation-successor-datatransfer-grants-keep-foreground-requirement-exact.md` narrows it once more on execution posture: successor continuity also keeps exact `requires_foreground` parity, so a reviewed foreground transfer cannot quietly turn into a background-capable retry under the old story. `docs/667-workstation-successor-datatransfer-grants-keep-delivery-mode-exact.md` keeps replay width exact too, so one-shot review cannot quietly become multi-delivery retry authority. `docs/668-workstation-successor-datatransfer-grants-keep-rate-limit-posture-exact.md` then keeps throttling posture exact too, so old-story retry wording cannot quietly change `constraints.rate_limit`. `docs/669-workstation-successor-datatransfer-grants-keep-absolute-expiry-posture-exact.md` then keeps the outer absolute-expiry ceiling exact too, so old-story retry wording cannot quietly change `constraints.expires_at` while pretending to continue the same reviewed transfer story. `docs/670-workstation-datatransfer-constraints-stay-closed-world-and-no-hidden-successor-posture.md` then closes the remaining open-ended posture seam too: ordinary `ui.datatransfer.grant.constraints` is now closed-world, so there is no hidden extra successor execution posture beyond the already accepted typed keys. `docs/671-workstation-ordinary-datatransfer-baseline-stays-frozen-and-richer-lanes-are-rfc-first.md` then makes the next intake rule explicit too: this ordinary portable baseline is now frozen and complete enough to implement, and any richer widened/substituting/broader transfer lane is RFC-first instead of silent growth of the same artifact family. `docs/672-workstation-richer-datatransfer-lanes-mint-distinct-artifact-families.md` then makes the artifact split explicit too: if a richer lane is accepted later, it must look like a distinct family instead of one more interpretation of ordinary `ui.datatransfer.grant` / `ui.datatransfer.receipt`. `docs/673-workstation-first-richer-datatransfer-rfc-target-is-reviewed-finite-collection-handoff.md` then fixes the next design queue too: the first richer-lane RFC target is a reviewed finite collection handoff, kept session-bounded and read-only only in its first cut instead of reopening the ordinary lane or jumping straight to persistent tree authority. `docs/674-workstation-reviewed-finite-collection-handoff-stays-single-retrieve-by-default-and-auto-stopping.md` then fixes the first retrieve-width cut inside that richer lane too: the first cut stays single-retrieve by default and auto-stop after the first successful retrieve instead of quietly becoming replay-friendly session authority. `docs/675-workstation-finite-collection-handoff-directory-members-stay-snapshot-shaped-and-no-live-tree-traversal-first.md` then fixes the next directory-semantics cut too: selected directories in that first richer lane stay finite reviewed snapshot membership rather than live tree traversal or persistent directory authority. `docs/676-workstation-finite-collection-handoff-snapshot-membership-stays-manifest-first-and-tree-summary-is-supplementary.md` then fixes the next representation cut too: that same richer lane keeps an explicit per-member manifest for reviewed membership, and any tree/collection digest stays supplementary summary evidence rather than replacing the manifest-first review/export surface. `docs/677-workstation-finite-collection-handoff-first-cut-stays-read-only-and-write-enabled-receive-is-follow-on-rfc-only.md` then fixes the next access-mode cut too: the first richer finite-collection handoff now stays read-only only, and any write-enabled receive must come back as a separate follow-on RFC/ADR decision instead of lingering inside the first cut. `docs/678-workstation-finite-collection-handoff-first-cut-rejects-symlinks-and-special-files.md` then fixes the next member-kind cut too: the same first richer lane is now regular-files-plus-explicit-directories only, and symlink or special-file members must fail closed instead of smuggling path-resolution or active endpoint authority into the reviewable collection floor. `docs/679-workstation-finite-collection-handoff-manifest-entry-floor-stays-content-identity-first-and-stat-light.md` then fixes the next manifest-entry seam too: the first richer finite-collection handoff now stays content-identity-first and stat-light, with normalized review path + member kind for every entry and exact payload digest + byte length for regular files instead of path-only or full-stat folklore. `docs/680-workstation-finite-collection-handoff-manifest-order-stays-canonical-by-review-path.md` then fixes the next serialization seam too: that authoritative manifest is now ordered only by normalized review path, locale-independent, with duplicate paths failing closed instead of preserving traversal or click order as hidden reviewed state. `docs/681-workstation-finite-collection-handoff-authoritative-collection-identity-stays-digest-bound-to-canonical-manifest.md` then fixes the next compact-identity seam too: the same richer lane now carries one authoritative manifest digest derived from the canonical explicit manifest, so later review/export joins can stay digest-bound to the reviewed set instead of reconstructing identity from tree summaries or implementation-local hashing. `docs/682-workstation-finite-collection-handoff-review-path-normalization-stays-relative-clean-and-nfc-canonical.md` then fixes the next path-grammar seam too: that same reviewed set now uses collection-relative clean slash-separated Unicode NFC review paths with no leading/trailing slash or dot segments, and collisions after normalization fail closed instead of relying on host or toolkit cleanup folklore. `docs/683-workstation-finite-collection-handoff-top-level-review-names-stay-explicit-and-no-silent-auto-rename.md` then fixes the next multi-root naming seam too: that same richer lane now keeps reviewed top-level names explicit, with no silent auto-rename or wrapper-root repair, so any collision disambiguation must become reviewed state or fail closed. `docs/684-workstation-finite-collection-handoff-manifest-stays-ancestor-closed-and-no-implicit-parent-synthesis.md` then fixes the next namespace-shape seam too: that same richer lane now keeps the authoritative manifest ancestor-closed, so parent directories are explicit reviewed structural state rather than retrieve-time implicit synthesis. `docs/685-workstation-finite-collection-handoff-selected-roots-stay-overlap-free-and-no-silent-subsumption.md` then fixes the next reviewed-root seam too: accepted selected roots are now overlap-free after normalization and reviewed aliasing; selected roots overlap-free is now explicit reviewed state, so ancestor/descendant root overlap cannot quietly collapse into one larger reviewed snapshot or hidden broker memory. `docs/686-workstation-finite-collection-handoff-retrieve-stays-fresh-rooted-and-no-silent-merge-into-existing-tree.md` then fixes the next retrieve/materialization seam too: that same richer lane now lands under a fresh destination root, so it does not silently merge into an existing tree or inherit overwrite/rename/same-bytes reuse folklore from receiver-local state. `docs/687-workstation-finite-collection-handoff-stays-profiled-to-b-c-d-and-not-a-fleet-host-baseline.md` then fixes the next product-scope seam too: the first richer family is now explicitly out of fleet-host baseline, so A should stay on rollout/support/import-export/breakglass-shaped answers unless a distinct later operator lane is justified. `docs/688-workstation-finite-collection-handoff-first-implementation-keeps-top-level-aliasing-out-and-collisions-fail-closed.md` then fixes the next first-implementation seam too: the first richer family now keeps top-level alias/disambiguation UX out of scope, so multi-root basename collisions fail closed instead of widening the first trusted review surface. `docs/689-workstation-finite-collection-handoff-review-ui-may-path-compress-deterministic-ancestor-only-runs.md` then fixes the next review-surface seam too: that same trusted review surface may use bounded path-compression of deterministic ancestor-only directory runs, but the explicit ancestor-closed manifest still remains authoritative. `docs/690-workstation-finite-collection-handoff-advisory-mime-stays-optional-and-non-authoritative.md` then fixes the next metadata seam too: advisory MIME stays optional descriptive metadata, so the first richer lane remains path/kind/payload-first instead of inheriting MIME-registry or detector baggage. `docs/696-workstation-finite-collection-handoff-no-owner-mode-mtime-xattr-fidelity-in-this-lane.md` then fixes the next filesystem-fidelity seam too: owner/group, mode-bit, mtime, xattr, ACL, and similar richer filesystem metadata stay out of this lane entirely, so the first richer lane does not quietly widen into a filesystem-preserving archive format. `docs/691-workstation-finite-collection-handoff-receipts-pin-the-exact-created-fresh-root.md` then fixes the next retrieve-result evidence seam too: successful retrieve receipts must pin the exact created fresh root instead of stopping at a parent chooser hint or pathless success prose. `docs/692-workstation-finite-collection-handoff-placement-hints-stay-advisory-and-receiver-local.md` then fixes the next placement-authority seam too: parent chooser or destination label stays receiver-local advisory UI state rather than reviewed cross-domain placement authority. `docs/693-workstation-finite-collection-handoff-result-root-locator-stays-handle-first-and-path-snapshot-advisory.md` then fixes the next receipt-locator seam too: the exact created fresh root now travels as a receiver-local stable result-root handle, and any human-facing path/display snapshot stays advisory rather than becoming the authoritative local result locator. `docs/694-workstation-finite-collection-handoff-advisory-display-snapshot-stays-retrieve-frozen.md` then fixes the next continuity seam too: when such text exists, it remains a retrieve-frozen advisory display snapshot instead of silently rewriting itself into a moving current-location story. `docs/698-reviewed-finite-collection-handoff-mints-exact-artifact-family-and-first-spec-stack.md` then fixes the next spec-facing seam too by minting the accepted portable `ui.collection.handoff.grant` / `manifest` / `receipt` family instead of leaving those nouns provisional.

Last updated: 2026-03-23r428
For the canonical current-stack map over the recent `docs/674-*` through `docs/696-*` reviewed finite-collection tightening cluster, see `docs/697-reviewed-finite-collection-handoff-current-contract-stack-and-stale-entrypoint-firewall.md` rather than relying on this local page to act as the full current companion list.
