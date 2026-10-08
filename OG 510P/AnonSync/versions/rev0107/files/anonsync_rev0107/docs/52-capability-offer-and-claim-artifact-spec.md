# Capability offer, artifact, and claim spec

## Why this deserves its own layer

The archive already had `invite` and `claim` objects.
What it still lacked was a full public contract for a more basic operator question:

> what capability is actually inside this artifact I am creating, delivering, inspecting, or accepting?

Resilio's current docs still answer that question through a mixture of type-specific sharing rituals:

- manual sharing can happen through key, link, or QR code, and the docs explicitly say they have different flow and functionality
- Standard-folder keys bypass the approval mechanism that links use
- link security options add approval posture, expiry period, and use-count limits
- Advanced folders use certificate-backed ACLs and Owner semantics, while Standard folders allow peers to re-share the key they possess without the same bounded governance model
- local shares inherit source permissions and can require remove-and-re-share ritual when access needs to change

Those features are individually understandable.
Together, they still scatter one important truth:

- what authority is being offered
- how it is constrained
- who or what may redeem it
- whether it can be re-delegated
- what local outcome a receiver is about to create by consuming it

AnonSync should not clone that shape.
The product should expose one public artifact grammar for capability-bearing offers, and one equally explicit claim/apply grammar for local acceptance.

## Core stance

1. delivery encoding is not authority semantics
2. offer artifact, claim, and applied result are separate public objects
3. approval posture is explicit policy, not an accident of artifact kind
4. redelegation must be inspectable and bounded
5. the same authority offer should render consistently across file, URI, QR, clipboard string, or local handoff
6. accepting an offer should describe the intended local outcome before any path, role, or linked-group mutation happens
7. every consumed offer should leave durable provenance after the portable artifact itself expires or is deleted
8. portable invitation lifetime must stay separate from any later durable trust promotion created after claim

## Terms

### Offer artifact

A portable or local capability-bearing object that can be delivered to another subject or imported on another device.
An offer artifact says what *could* be claimed; it is not the same thing as local acceptance.

### Delivery encoding

The concrete transport wrapper of an offer artifact.
Examples:

- file
- URI / link
- QR payload
- clipboard string
- local handoff between trusted local processes or surfaces

Encoding affects ergonomics, not what authority exists.

### Offer policy

A durable policy that constrains how an offer may be redeemed.
It may specify expiry, redemption count, peer pinning, approver scope, maximum role, path hints, or whether claim review is mandatory.

### Claim

A local review object created from an offer artifact or incoming visibility state.
A claim records the operator's intended local outcome before apply.

### Claim receipt

A durable record proving which offer was consumed, by whom, into which local outcome, under which policy and proof objects.

## Public objects

### Offer artifact

Minimum fields:

- `offer_id`
- `offer_kind` (`device-link`, `share-access`, `share-observe`, `successor-handoff`, `maintenance-delegate`, `recovery-material`, `local-handoff`)
- `delivery_encoding` (`file`, `uri`, `qr`, `clipboard`, `local-handoff`)
- `subject_refs[]`
- `offered_role` or `offered_capabilities[]`
- `redelegation_policy` (`none`, `same-scope-only`, `narrower-only`, `explicit-subdelegate`)
- `approval_posture` (`claim-required`, `approval-required`, `known-peer-fast-path`, `policy-bound-auto-claim`)
- `post_claim_trust_promotion_policy` (`none`, `subject-only`, `reviewed-seat-only`, `review-required-for-family`, `family-reuse-candidate`)
- `expiry_at` nullable
- `redemption_limit` nullable
- `peer_constraints` (`any`, `pinned-fingerprint`, `contact-tag`, `linked-group-only`)
- `path_hint` nullable
- `share_visibility_hint` (`incoming-only`, `adopt-suggested`, `mount-required`, `visibility-only`)
- `provenance`
- `status` (`active`, `partially-redeemed`, `redeemed`, `expired`, `revoked`, `superseded`)

### Offer policy

Minimum fields:

- `offer_policy_id`
- `default_expiry`
- `default_redemption_limit`
- `default_claim_requirement`
- `default_redelegation_policy`
- `allowed_delivery_encodings[]`
- `required_peer_pinning` boolean
- `requires_report_types[]`
- `allow_path_hint` boolean
- `auto_revoke_after_first_claim` boolean

### Claim receipt

Minimum fields:

- `claim_receipt_id`
- `claim_ref`
- `offer_ref`
- `subject_outcome_refs[]`
- `applied_role_or_capabilities`
- `delivery_encoding_seen`
- `policy_refs[]`
- `preflight_refs[]`
- `plan_ref` nullable
- `report_refs[]`
- `applied_at`
- `residual_offer_state` (`still-valid`, `use-budget-reduced`, `consumed`, `revoked-on-apply`)

## Principles

1. **Offer creation must say what is being offered, not only how it is delivered.**  
   An operator should not need to infer from “link” versus “QR” versus “file” whether the payload is share access, link membership, or some broader delegated authority.

2. **Approval is a first-class constraint, not an artifact-family accident.**  
   A product should not make “key means no approval” and “link means approval is possible” part of the public mental model. Approval posture belongs in explicit policy.

3. **Redelegation must be visible.**  
   The operator should always be able to answer whether a receiver may pass equivalent authority onward, only a narrower form, or nothing at all.

4. **Encoding changes must preserve semantic identity.**  
   Rendering one offer as QR instead of file should not silently widen, weaken, or otherwise mutate the authority being offered.

5. **Claim review must describe local outcome, not just remote authorization.**  
   The receiver should see whether claiming this offer would create visibility only, adopt a mount, widen a role, join a linked group, or require a path decision.

6. **Offer lifetime and claim lifetime are different things.**  
   The portable artifact may expire or be deleted while the durable local authority and audit trail remain inspectable.

7. **Offer lifetime and trust lifetime are also different things.**  
   A one-time or expiring invitation may admit one subject without necessarily promoting broader remembered approval, and any broader promotion must be separately inspectable.

8. **Receipts should outlive convenience surfaces.**  
   Later audit should be able to answer which artifact was consumed, what policy constrained it, what local state was created, and whether any durable remembered approval survived even after transient inbox items disappear.

## Interface implications

The workbench and CLI should each have one coherent offer surface.
They should not scatter offer semantics across share menus, QR widgets, ad hoc “copy link” popovers, and hidden advanced options.

A trustworthy surface should make it easy to answer:

- what authority this artifact carries
- how many times it may be redeemed
- when it expires
- whether claim review is mandatory
- whether redelegation is allowed
- which peers or identities are eligible to redeem it
- which claim receipt proves later consumption

## CLI shape

### `anonsync offer`

Create, inspect, revoke, reissue, and audit capability-bearing artifacts.

```text
anonsync offer create --kind share-access --share vault --role readonly-viewer --delivery file --expires 7d --uses 1 --approval required --output ./vault-readonly.aso
anonsync offer create --kind device-link --group personal --delivery qr --peer-pin fp_01J... --output ./phone-link.png
anonsync offer show ./vault-readonly.aso
anonsync offer show off_01J...
anonsync offer list --share vault
anonsync offer revoke off_01J...
anonsync offer reissue off_01J... --delivery uri --output ./vault-link.txt
anonsync offer receipt list --subject shr_vault
```

Semantics:

- `offer create` must produce one explicit artifact manifest regardless of delivery encoding
- `offer show` should work on both portable artifact input and durable daemon-known offer IDs
- `offer revoke` should end future redemption without rewriting already-applied local outcomes
- `offer reissue` should preserve semantic identity unless the operator explicitly changes scope, policy, or role
- `offer receipt list` should show later redemption and revocation history

### `anonsync invite`

`invite` may remain as ergonomic alias vocabulary for common portable-sharing flows.
However, the public object model should still be `offer`.
The interface must not force operators to remember that some artifacts are offers while others are “special invites” with different semantics hidden in the delivery mechanism.

### `anonsync claim`

Claim preparation should explicitly reference offer identity and intended local outcome.

```text
anonsync claim prepare --offer ./vault-readonly.aso --path ~/Sync/Vault --mode selective
anonsync claim prepare --offer off_01J... --visibility-only
anonsync claim show clm_01J...
anonsync claim apply clm_01J...
anonsync claim reject clm_01J... --reason "wrong share"
anonsync claim receipt show clr_01J...
```

Semantics:

- a claim must say whether local outcome is `visibility-only`, `mount-adopt`, `linked-group-join`, `role-widen`, or other supported result
- claim review should restate the offer constraints in operator language before apply
- apply should fail safely if expiry, use budget, peer pinning, or referenced preflight/report state drifted
- successful apply should emit a claim receipt even when the portable artifact is one-time and immediately consumed

## Daemon/API implications

A local daemon should expose offer resources separately from claims.
Receivers and senders both need durable inspection.

Minimum surface:

```text
GET    /v1/offers
POST   /v1/offers
POST   /v1/offers/inspect
GET    /v1/offers/{offer_id}
POST   /v1/offers/{offer_id}/revoke
POST   /v1/offers/{offer_id}/reissue
GET    /v1/claim-receipts
GET    /v1/claim-receipts/{claim_receipt_id}
```

`POST /v1/offers/inspect` should parse a portable artifact without applying it.
Inspection should return one normalized object regardless of whether the input arrived as file, URI, QR payload, or clipboard string.

## Workbench implications

The workbench should have:

- a sender-side offer drawer showing active artifacts, expiry, redemption count, and claim receipts
- a receiver-side intake page that renders artifact semantics before any local mutation
- one action vocabulary across delivery encodings: `Inspect`, `Prepare claim`, `Reissue`, `Revoke`, `Show receipts`

The workbench must not let delivery widgets become miniature trust systems.
A QR export popover, a copied URI, and a saved file should all point back to the same offer detail page.

## Canonical questions this layer must answer

A mature operator surface should be able to answer all of these without support-lore reconstruction:

- “Does this thing grant visibility only, or writable authority?”
- “Can the receiver pass this onward?”
- “Will acceptance require another approval step?”
- “How many redemptions are left?”
- “Which receipt proves who consumed it?”
- “Did I reissue the same offer in a different encoding, or create broader authority by accident?”

## Non-clone conclusion

Resilio's current docs are strong enough to teach two useful lessons at once.
First, portable sharing artifacts with expiry, use-count, and approval options are genuinely useful.
Second, it is still too easy there to make delivery mechanism or folder type stand in for authority semantics.

AnonSync should keep the convenience while replacing the fragmentation.
The product should expose one explicit offer-artifact and claim-receipt model so delivery, approval, redelegation, and local outcome remain inspectable public state.

## Recipient intent and actual redeemer are not the same thing

Portable offers may be copied, forwarded, or redeemed by possession.
That convenience is valuable, but the public artifact model must not let `whoever redeemed it successfully` silently stand in for `who the sender meant it for`.

Offer inspection should therefore preserve at least these separate facts whenever known:

- sender-intent posture (`portable open`, `named hint`, `reviewed seat expected`, `family expected`)
- actual redeemer identity
- proof basis for the actual redeemer claim
- match class between sender intent and actual redeemer
- reviewed mismatch outcome
- resulting durable-trust posture

Claim semantics should remain honest about non-effects:

- a successful claim does not prove the redeemer matched sender intent
- accepting an unexpected redeemer for one subject does not silently authorize later unrelated subjects
- durable remembered approval, if any, must still be proven by later promotion/mismatch receipts rather than inferred from claim success alone


## One artifact may have many redemption events; the budget story is not the trust story

If an offer artifact has a redemption limit greater than one, the product must preserve two separate truths:

- the artifact-level budget story (`limit`, `consumed`, `remaining`, `expired`, `revoked`, `superseded`)
- the per-redemption trust story (`who redeemed`, `what proof identified them`, `what trust survived from that exact event`)

That means:

- `redemption_limit` is not the same thing as `approved audience size`
- a successful redemption does not explain all later remembered approval created by other successful redemptions of the same artifact
- a budget-denied attempt does not mean prior successful redemptions were revoked
- reissuing a new artifact may be safer than continuing to stretch a partially consumed one across additional redeemers

## Repeated or familiar redemption attempts still need explicit equivalence policy

If one offer artifact can be used more than once, the public artifact model must preserve not only `how many uses remain`, but also **what kind of repeat this is**.

Offer inspection should therefore preserve at least these additional facts whenever relevant:

- comparison attempt reference
- equivalence class between current attempt and earlier attempt
- governing slot-accounting policy
- resulting slot effect (`collapse`, `consume`, `blocked pending reissue`)
- any resulting trust posture that survives without changing slot count

Claim semantics should remain honest about non-effects:

- same redeemer does not automatically mean same slot
- same human hint does not prove same reviewed seat
- collapsing a replay does not silently widen remembered approval
- consuming a new slot does not by itself mean the attempt was suspicious


## Reissue is not enough; successor lineage must also be explicit

Once the product already knows the honest next action is `reissue new artifact`, the public artifact model must preserve one more layer of truth:

- predecessor artifact and terminal/risky posture
- reissue reason
- successor relation (`same-scope`, `narrowed`, `broadened`, `fresh-scope`, `delivery-only`)
- budget reset posture
- carried-forward policy summary
- explicit non-carry summary
- successor-boundary receipt

Offer semantics should remain honest about non-effects:

- creating a successor does not erase predecessor receipts
- same governed subject does not imply same budget family
- delivery-only re-encoding does not reset expiry or use count
- remembered approval may survive independently of the predecessor artifact, but it must not silently stand in for successor scope review


## Delivery provenance and preview authority are not the same thing as local inspect truth

Portable offers may now arrive through browser landing pages, QR scans, clipboard paste, mail bodies, saved files, or local app handoff.
That convenience is valuable, but the public artifact model must not let `opened in browser` stand in for `locally inspected`.

Offer inspection should therefore preserve at least these additional facts whenever relevant:

- delivery channel
- preview surface
- preview fields shown before local inspection
- external-touch posture
- handoff posture
- preview-authority posture
- authoritative offer reference after local parsing succeeds

Claim semantics should remain honest about non-effects:

- landing-page preview does not prove trust or byte availability
- browser auto-launch does not prove fresh deliberate approval in this moment
- locally parsed artifact semantics do not yet prove later claim success or remembered-trust promotion
- keeping a fragment out of the landing-page request does not mean the whole delivery path was local-only


## Carrier aliases are not the same thing as artifact identity

Portable offers may now travel through browser wrapper URLs, protocol URLs, QR payloads, copied text, mail-body copies, or local file envelopes.
That convenience is valuable, but the public artifact model must not let whichever carrier was seen last stand in for the thing itself.

Offer inspection should therefore preserve at least these additional facts whenever relevant:

- canonical offer reference
- carrier alias reference
- carrier kind
- carrier authority posture
- equivalence posture
- normalization basis
- explicit alias-vs-successor judgment

Claim semantics should remain honest about non-effects:

- delivery-only re-encoding does not mint fresh budget
- seeing a QR and a wrapper URL does not imply two offers existed
- a browser wrapper is not automatically the authoritative artifact identity
- similar-looking carriers may still be different successors if governed semantics changed


## Offer fields need explicit hint/sealed/authoritative partition

Portable offers may now preserve canonical identity across many carriers without making every field equally visible or equally authoritative.
That convenience is valuable, but the public artifact model must not let whichever field happened to be previewed first stand in for the governed thing itself.

Offer inspection should therefore preserve at least these additional facts whenever relevant:

- field semantic role
- field exposure posture
- field authority posture
- preview-visible surfaces
- sealed-until-parse posture
- authoritative-after-parse posture
- eligible later inferences
- ineligible later inferences

Claim semantics should remain honest about non-effects:

- previewed folder label does not prove intended-recipient match
- previewed approximate size does not prove byte availability now
- sealed authority-bearing material staying out of a landing request does not mean the whole delivery path was local-only
- authoritative local parse still does not by itself prove later approval or durable trust promotion


## Preview usefulness still needs explicit decision sufficiency and omission truth

Portable offers may now preserve delivery provenance, canonical identity, and field-class partition without yet telling the operator whether the preview is enough for any actual decision.
That convenience is valuable, but the public artifact model must not let recognition hints masquerade as governance truth.

Offer inspection should therefore preserve at least these additional facts whenever relevant:

- preview fields shown
- omitted governance-bearing fields
- recognition sufficiency
- routing sufficiency
- governance sufficiency
- trust sufficiency
- unsafe inferences refused
- preview-sufficiency receipt

Claim semantics should remain honest about non-effects:

- familiar label and approximate size do not prove permission class
- familiar preview does not prove approval posture or remaining use budget
- local parse may remove some omissions without eliminating later approval review
- later durable trust must not claim preview sufficiency it never had
