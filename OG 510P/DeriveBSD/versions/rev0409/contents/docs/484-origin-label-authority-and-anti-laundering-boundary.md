# Origin label authority and anti-laundering boundary

**Tier:** B (Base)  
**Profiles:** A, B, C, D  
**Pillars:** operability, supply-chain, isolation  
**Patterns:** Broker→Lease→Receipt, Quarantine→Promote  

DeriveBSD already wanted origin labels, quarantine state, sanitize-first imports, and queryable metadata.
The hard decision this archive was missing was **which layer is authoritative**.

This doc fixes that boundary for v0.

## Accepted boundary

DeriveBSD uses a **dual-layer provenance model**:

1. **Authoritative record:** `content.origin`
   - content-addressed, queryable, bundle-carryable
   - binds a subject digest to capture context
   - the semantic source of truth for provenance
2. **Local filesystem pointer/cache:** quarantine/origin label
   - lives next to the file for fast local UX
   - carries current state plus a pointer to the authoritative record
   - may be stripped by some filesystems/tools, so it is not authoritative

`content.import.receipt` is the join object that tells operators which path occurred for a given import result.
It must record:

- the authoritative `content.origin` digest,
- whether the file-local metadata was **preserved**,
- **rehydrated** through an approved portal/bundle lane,
- **cleared-by-policy** on purpose,
- or **laundering-suspected** because the workflow lost provenance.

## Why this is the right narrow decision

Treating xattrs/ADS/labels as the whole provenance story makes the archive brittle.
Treating provenance as only sidecars/CAS records makes everyday UX weak and slows incident response.

The small, coherent compromise is:

- keep the semantic truth in `content.origin`,
- keep the local label tiny and cheap,
- require import/export portals to preserve or rehydrate labels when the transport is lossy,
- and never silently pretend stripped metadata is intact.

## Contract details

### `content.origin` is the authority

The authoritative provenance object is `content.origin`.
It is the object incidents, exports, support bundles, and query/index layers should join against.

### The filesystem label is pointer-only

A label/xattr/attribute may carry:

- current quarantine state,
- an `origin_id`,
- an `origin_digest`,
- or another tiny pointer form.

It should **not** be treated as the only meaning-bearing provenance record.
If the label is lost, the system can still explain provenance when the authoritative record is available.

### `content.import.receipt` records metadata survival

`content.import.receipt` now carries a `metadata` block.
The important fields are:

- `authority`
- `transport`
- `status`
- `authoritative_origin_digest`

This is the smallest typed surface that makes “preserved vs rehydrated vs laundered” implementable.

### Official preservation lanes

DeriveBSD only promises provenance preservation across lossy transports through official lanes:

- portal copy / file transfer
- deterministic export / bundle lanes
- archive extraction paths that emit derived origin chains and receipts

Raw `cp`, ad-hoc `zip`, or foreign filesystems without the preserving lane are compatibility territory, not the guaranteed provenance-preserving story.

## Operational meaning

### Safe success case

- file arrives from download, USB, share, or attachment
- `content.origin` is created
- file gets a local quarantine/origin pointer
- import/sanitize/open path emits `content.import.receipt`
- receipt says `status=preserved` or `status=rehydrated`

### Suspicious case

- labeled content is copied/repacked/exported outside approved lanes
- the destination bytes arrive without a trustworthy pointer
- the system can still match parent receipts or bundle evidence, or it cannot
- if it cannot, the result stays quarantined and `content.import.receipt.metadata.status` becomes `laundering-suspected`

This prevents the archive from laundering mystery bytes into trusted-looking files.

## Relationship to query/index work

This decision intentionally does **not** make query/index services authoritative.
Indexes remain derivative convenience surfaces built from:

- current file-local pointers,
- authoritative `content.origin` records,
- and other evidence joins.

That keeps query privacy/governance open while unblocking the core provenance contract.

## Sanitized inspection derivatives are still provenance-bound

The workstation archive now applies this same anti-laundering discipline to document viewing too.
`docs/654-workstation-sanitized-inspection-derivatives-stay-inspection-shaped-and-disposable-first.md` makes the narrow follow-on cut explicit: sanitizer success can make foreign bytes safer to inspect, but sanitizer success is not implicit trust-promotion into a remembered persistent viewer or ambient trusted/local document class. `docs/655-workstation-ocr-searchable-sanitized-derivatives-stay-explicit-secondary-and-nondefault.md` then keeps the next laundering edge visible too: OCR/searchable reconstruction should remain an explicit `ocr-inspection-derivative`, not disappear into generic “safe PDF” wording or silently replace the flat sanitized baseline. `docs/656-workstation-ocr-searchable-sanitized-derivatives-stay-out-of-ambient-host-indexes-by-default.md` then fixes the next ambient-corpus leak too: searchable foreign-derived inspection output does not gain ambient/global host indexing by default just because a text layer now exists. `docs/657-workstation-ocr-text-egress-stays-explicit-plain-text-single-delivery.md` then fixes the next copy/export laundering edge too: when OCR-derived text does leave that lane, typed `ui.datatransfer.*.content_source` can preserve the excerpt's provenance instead of letting copied text become ambient clipboard folklore. `docs/658-workstation-datatransfer-evidence-binds-offer-source-and-transfer-subjects-exactly.md` then fixes the actor-side join too: transfer evidence now carries exact `offer_source_subject` alongside `subject`, so anti-laundering review does not have to rediscover who actually exported the bytes from broker-private state.

That is the document-handling version of the same provenance rule here:

- do not let a convenience surface erase foreign lineage,
- do not let a successful transform silently become authority,
- and keep later promotion as a separate explicit step when it matters.

## Related docs

- `adrs/ADR-0074-origin-label-authority-and-anti-laundering-boundary.md`
- `docs/280-origin-labels-and-quarantine-attributes.md`
- `docs/293-attribute-indexed-metadata-and-live-queries.md`
- `docs/251-export-policies-and-support-bundle-portal.md`
- `docs/279-usb-quarantine-and-removable-media-workflow.md`
- `docs/654-workstation-sanitized-inspection-derivatives-stay-inspection-shaped-and-disposable-first.md`
- `docs/655-workstation-ocr-searchable-sanitized-derivatives-stay-explicit-secondary-and-nondefault.md`
- `docs/658-workstation-datatransfer-evidence-binds-offer-source-and-transfer-subjects-exactly.md`
- `spec/content.origin.schema.json`
- `spec/content.import.receipt.schema.json`
- `spec/examples/content.origin.json`
- `spec/examples/content.import.receipt.json`


`docs/661-workstation-datatransfer-grants-carry-exact-effective-until-and-late-delivery-fails-closed.md` fixes the next laundering edge too: the reviewed transfer artifact now publishes exact `effective_until`, so policy lifetime does not quietly expand through stale local broker state or grace-period folklore.
Cross-domain workstation transfer now follows the same anti-laundering pattern too: `docs/658-workstation-datatransfer-evidence-binds-offer-source-and-transfer-subjects-exactly.md` keeps the actor pair explicit and `docs/659-workstation-datatransfer-receipts-join-exact-grants-by-digest.md` now keeps the policy join explicit, so copied OCR excerpts or bounded clipboard payloads cannot shed the exact reviewed transfer grant behind generic clipboard folklore. In concrete terms, `ui.datatransfer.receipt.grant_digest` now keeps the policy join explicit too. `docs/660-workstation-single-delivery-datatransfer-grants-stay-one-shot-and-fresh-grant-required.md` then fixes the next recovery escape hatch too: the ordinary single-delivery lane is one-shot, so copied OCR excerpts or bounded clipboard payloads do not quietly gain replay/history semantics once the first successful read-side transfer has spent the grant; later recovery is fresh grant / re-offer required. `docs/662-workstation-datatransfer-renewals-stay-successor-grants-and-predecessor-digest-linked.md` then fixes the next continuity escape hatch: reviewed retries are new successor grants with explicit `supersedes_grant_digest`, not silent broker-side mutation of the earlier grant story. `docs/663-workstation-successor-datatransfer-grants-stay-same-actor-pair-and-no-wider-offer.md` then fixes the next widening escape hatch: successor continuity must carry `successor_scope_posture` and stay same-actor-pair and no-wider-offer instead of using retry wording to smuggle a broader transfer.


Successor clipboard retry continuity is narrowed further too: `docs/664-workstation-successor-datatransfer-grants-keep-payload-lineage-and-redaction-posture-exact.md` keeps `offer.content_source` and `offer.redaction_profile_digest` exact under successor continuity, so provenance-bearing transfers do not quietly shed or swap their origin/redaction posture under familiar retry wording. `docs/665-workstation-successor-datatransfer-grants-stay-exact-payload-bound-and-no-semantic-equivalence-rebinding.md` then keeps the exact reviewed payload visible too: successor continuity must preserve payload digest (`offer.payload_digest`), so semantic-equivalence rebinding does not become a new laundering seam. `docs/666-workstation-successor-datatransfer-grants-keep-foreground-requirement-exact.md` closes the next execution-posture seam too: successor continuity must preserve exact `constraints.requires_foreground`, so a reviewed foreground crossing cannot quietly become background-capable under retry wording. `docs/667-workstation-successor-datatransfer-grants-keep-delivery-mode-exact.md` then closes the next replay-width seam too: successor continuity must preserve exact `delivery_mode`, so a reviewed one-shot crossing cannot quietly become multi-delivery authority under retry wording. `docs/668-workstation-successor-datatransfer-grants-keep-rate-limit-posture-exact.md` then closes the next throttling seam too: successor continuity must preserve exact `constraints.rate_limit`, so a reviewed transfer cannot quietly change tempo/throughput posture under retry wording; add/drop/swap is fresh-grant required. `docs/669-workstation-successor-datatransfer-grants-keep-absolute-expiry-posture-exact.md` then closes the next timing seam too: successor continuity must preserve exact `constraints.expires_at`, so a reviewed provenance-bearing transfer cannot quietly replace or remove its outer absolute-expiry ceiling under retry wording; add/drop/swap is fresh-grant required. `docs/670-workstation-datatransfer-constraints-stay-closed-world-and-no-hidden-successor-posture.md` then closes the remaining vocabulary seam too: ordinary `ui.datatransfer.grant.constraints` is now closed-world, so laundering cannot hide behind hidden extra `constraints.*` keys or product-local extra posture in the ordinary portable lane. `docs/671-workstation-ordinary-datatransfer-baseline-stays-frozen-and-richer-lanes-are-rfc-first.md` then closes the next process seam too: widened/substituting/broader transfer lanes are not allowed to quietly become the ordinary portable lane; they are RFC-first instead of baseline drift. `docs/672-workstation-richer-datatransfer-lanes-mint-distinct-artifact-families.md` then closes the next artifact-family seam too: if a richer lane is accepted later, it must mint a distinct artifact family instead of quietly reusing ordinary `ui.datatransfer.grant` / `ui.datatransfer.receipt`. `docs/673-workstation-first-richer-datatransfer-rfc-target-is-reviewed-finite-collection-handoff.md` then fixes the next queueing seam too: the first richer-lane design target is a reviewed finite collection handoff, kept read-only-only in its first cut and with no persistent directory authority so the archive does not jump straight from a frozen ordinary lane into ambient tree laundering. `docs/674-workstation-reviewed-finite-collection-handoff-stays-single-retrieve-by-default-and-auto-stopping.md` then fixes the first replay-width seam inside that richer lane too: the first cut stays single-retrieve-by-default and auto-stopping after the first successful retrieve instead of quietly laundering “send these few objects” into session-local collection replay authority. `docs/675-workstation-finite-collection-handoff-directory-members-stay-snapshot-shaped-and-no-live-tree-traversal-first.md` then fixes the next namespace seam too: selected directories in that first richer lane stay snapshot-shaped reviewed membership rather than live browse/traverse authority that would launder a finite handoff into quiet tree access. `docs/676-workstation-finite-collection-handoff-snapshot-membership-stays-manifest-first-and-tree-summary-is-supplementary.md` then fixes the next representation seam too: that richer lane keeps manifest-first reviewed membership through an explicit per-member manifest, so tree/collection digests do not become the only visible membership story and later reconstruction does not become a new laundering seam. `docs/677-workstation-finite-collection-handoff-first-cut-stays-read-only-and-write-enabled-receive-is-follow-on-rfc-only.md` then fixes the next access-mode seam too: the first richer finite-collection handoff now stays read-only only, so collection handoff does not quietly become writable shared-folder authority in the same first cut. `docs/678-workstation-finite-collection-handoff-first-cut-rejects-symlinks-and-special-files.md` then fixes the next member-kind seam too: that same richer first cut rejects symlinks and special files, so “selected folder snapshot” cannot quietly launder path-resolution or active endpoint authority back across the boundary. `docs/679-workstation-finite-collection-handoff-manifest-entry-floor-stays-content-identity-first-and-stat-light.md` then fixes the next manifest-evidence seam too: the first richer lane keeps path/kind/payload identity on the reviewed/exported surface through normalized review path + member kind for every entry and exact payload digest + byte length for regular files, instead of laundering membership through broker-local richer stat folklore.

Last updated: 2026-03-22r409
