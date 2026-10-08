from pathlib import Path
import re

ROOT = Path('.')
rev = 'rev0104'
ts = '2026.03.18.06.28'
codename = 'handoffprovenanceharbor'


def read(path: str) -> str:
    return Path(path).read_text()


def write(path: str, text: str) -> None:
    Path(path).write_text(text)


new_spec = '''# Offer delivery-handoff provenance, preview authority, and app-intake boundary interface spec

## Purpose

The archive already separates:

- artifact lifetime from durable trust promotion
- sender intent from actual redeemer identity
- artifact budget from per-redemption trust fanout
- repeated-attempt equivalence from honest slot treatment
- predecessor/successor reissue lineage from raw link recreation

One real gap still remained:

> once a portable offer travels through a browser landing page, QR scanner, e-mail client, clipboard, or other delivery surface, the operator still needs one explicit answer to what was merely previewed in transit, what was actually ingested by the local app, what any external service could see, and what facts only became authoritative after local inspection.

This document turns that boundary into one explicit interface contract.
It is the delivery/handoff companion to `52-capability-offer-and-claim-artifact-spec.md`, the preview-truth companion to `66-claim-and-adoption-intake-interface-spec.md`, and the portable-offer companion to `113-offer-recipient-intent-and-redeemer-identity-boundary-interface-spec.md` through `116-offer-reissue-lineage-and-successor-boundary-interface-spec.md`.

## Why this needs its own spec

Current Resilio docs still make this seam concrete in a useful but incomplete way.
`Link structure and flow` says a clicked Sync link first opens a landing page on the Resilio website that shows only basic folder info such as folder name and approximate size; if the browser has seen Sync links before, the page may immediately transfer the link into the Sync app; and the URL parameters after `#` are not actually sent to Resilio's server.
`Comprehensive guide to syncing (Desktop-Desktop)` says a link can be sent through e-mail or any convenient and trusted way, and that the default browser may ask permission to launch the external Sync application and may remember that choice.
Those docs are helpful, but they still leave one operator question too reconstructive:

- which delivery channel carried the artifact here
- what metadata was merely previewed outside the app
- whether any external surface saw only a wrapper URL, saw the full artifact, or only observed a landing-page hit
- whether the handoff into the local app was automatic, browser-confirmed, manual paste, QR scan, or local-file import
- which facts are merely delivery hints versus locally parsed artifact semantics versus fully authoritative, receipt-backed facts

That is not a criticism of browser links, QR codes, or landing pages.
It is a criticism of any surface that lets `the browser showed a folder name` or `the app auto-opened` stand in for one explicit proof story about delivery path, external touch, preview authority, and post-ingest truth.
AnonSync should therefore expose one explicit **delivery-handoff provenance and preview-authority contract** wherever portable offers cross surface boundaries before the real local inspection begins.

## Core rule

Delivery preview, artifact ingestion, and authoritative local inspection are three separate public facts.

A browser page, QR overlay, e-mail body, or clipboard preview may show something about an offer.
The local app may then ingest a portable artifact through a handoff step.
Only after local inspection and later review should the product claim authoritative offer semantics, trust consequences, or local-admission readiness.
None of those stages collapse the others.

The product is not fully inspectable until it can answer ten questions in one place:

1. which delivery channel carried the artifact here
2. which preview surface, if any, displayed metadata before local inspection
3. what metadata was shown there
4. what any external service or wrapper surface could actually observe
5. whether the handoff into the local app was automatic, confirmed, manual, or local-only
6. which fields were only preview hints
7. which fields were locally parsed from the received artifact
8. which fields are authoritative only after local inspection or later review
9. what tempting but unsafe shortcut is being refused
10. which receipt later proves the delivery path, preview-authority boundary, and current authoritative interpretation

If the operator still has to infer from `clicked in browser`, `opened automatically`, and a folder-name preview whether the artifact is already trusted, locally parsed, or externally disclosed, the surface is not explicit enough.

## Public objects

### Offer delivery-handoff row

A compact read object describing how one portable offer arrived, what was previewed before app ingestion, and what the current authority boundary is.

Suggested fields:

- `offer_delivery_handoff_row_id`
- `offer_ref` nullable
- `delivery_event_ref`
- `delivery_channel` (`browser-link-click`, `browser-auto-handoff`, `browser-confirmed-external-app`, `clipboard-paste`, `manual-text-entry`, `qr-scan`, `email-client-open`, `saved-file-open`, `api-submit`, `local-app-share`, `unknown`)
- `preview_surface` (`browser-landing-page`, `qr-overlay`, `mail-body`, `chat-message`, `file-manager`, `none`, `unknown`)
- `preview_fields[]` (`folder-name-hint`, `approx-size-hint`, `issuer-hint`, `expiry-hint`, `version-hint`, `none`, `unknown`)
- `external_touch_posture` (`local-only`, `wrapper-url-observed`, `landing-page-hit-fragment-not-sent`, `external-surface-saw-full-artifact`, `unknown`)
- `handoff_posture` (`auto-transferred-to-app`, `browser-confirmed-launch`, `manual-copy-into-app`, `local-file-import`, `local-only`, `blocked`, `unknown`)
- `preview_authority_posture` (`preview-only`, `artifact-derived-unreviewed`, `locally-parsed`, `locally-inspected`, `receipt-backed`, `unknown`)
- `authoritative_offer_ref` nullable
- `recommended_next_action`
- `supporting_receipt_refs[]`

### Delivery-authority explanation

A read object explaining the exact boundary between delivery preview and authoritative local interpretation.

Suggested fields:

- `offer_delivery_authority_explanation_id`
- `delivery_event_ref`
- `offer_ref` nullable
- `delivery_channel`
- `preview_surface`
- `external_touch_posture`
- `handoff_posture`
- `preview_authority_posture`
- `preview_summary`
- `authoritative_summary`
- `non_effect_summary`
- `why`
- `proof_refs[]`

### Delivery-handoff review plan

A prepared review object for deciding whether one delivery event may proceed to local inspection, needs stronger warning language, or should be reissued or re-delivered through a narrower channel.

Suggested fields:

- `offer_delivery_handoff_plan_id`
- `delivery_event_ref`
- `offer_ref` nullable
- `current_delivery_channel`
- `current_external_touch_posture`
- `current_preview_authority_posture`
- `requested_outcome` (`continue-to-local-inspect`, `require-manual-confirm`, `freeze-at-preview-only`, `re-deliver-local-only`, `reissue-narrower-artifact`, `reject-ambiguous-handoff`, `keep-current-policy`)
- `effect_summary`
- `non_effect_summary`
- `blockers[]`
- `receipt_promise`

### Delivery-handoff receipt

A durable object proving how one portable offer crossed a delivery surface, what was merely previewed there, and what became authoritative afterward.

Suggested fields:

- `offer_delivery_handoff_receipt_id`
- `delivery_event_ref`
- `offer_ref` nullable
- `delivery_channel`
- `preview_surface`
- `preview_fields[]`
- `external_touch_posture`
- `handoff_posture`
- `preview_authority_posture_before`
- `preview_authority_posture_after`
- `authoritative_offer_ref` nullable
- `outcome`
- `recorded_at`
- `proof_refs[]`

## Delivery channel classes

### `browser-link-click`

Use when an operator clicked a portable link in a browser but the browser did not yet auto-transfer it into the local app.

### `browser-auto-handoff`

Use when a browser immediately transferred the link to the local app due to remembered protocol permission.
This class must render stronger reminder language because convenience can hide the handoff boundary.

### `browser-confirmed-external-app`

Use when a browser prompted the operator before launching the local app.

### `clipboard-paste`

Use when a portable offer string is pasted into the app or CLI directly.

### `manual-text-entry`

Use when the operator typed or otherwise re-entered offer material manually.

### `qr-scan`

Use when the delivery wrapper is a QR presentation rather than a text link.

### `saved-file-open`

Use when an offer artifact was opened from the local filesystem.

## Preview authority postures

### `preview-only`

Use when the surface is showing hints that the app has not yet parsed or verified locally.

### `artifact-derived-unreviewed`

Use when the app has the artifact bytes or text but has not yet completed normalized inspection.

### `locally-parsed`

Use when the app has parsed the artifact and can describe its declared semantics, but later review or contact proof may still narrow the truth.

### `locally-inspected`

Use when the local inspect step has completed and the artifact's own declared policy is authoritative for inspection purposes.

### `receipt-backed`

Use when later claim/review receipts now prove the delivery event and authoritative interpretation chain.

## External touch postures

### `local-only`

Use when the artifact never crossed an external preview surface before local inspection.

### `wrapper-url-observed`

Use when an external surface could observe a wrapper URL or transport shell, but not the full authority-bearing payload.

### `landing-page-hit-fragment-not-sent`

Use when a browser reached a landing page that rendered preview metadata while the authority-bearing fragment or payload was not transmitted to the landing-page service.

### `external-surface-saw-full-artifact`

Use when the channel actually exposed the full portable artifact to a third-party surface or service.
This class should render stronger review language.

## Fixed inspection order

Every delivery-handoff surface should preserve the same sections in the same order:

1. **Received via and external touch**
2. **What the preview surface actually showed**
3. **What the local app has parsed so far**
4. **What is authoritative now**
5. **What definitely is not implied**
6. **Receipts and proof links**

### 1) Received via and external touch

This section should show:

- delivery channel
- whether a browser/QR/mail/chat/file-manager surface was involved
- whether the external surface saw a wrapper only, landing-page hit only, or the full artifact
- whether the handoff into the local app was automatic, confirmed, manual, blocked, or local-only

### 2) What the preview surface actually showed

This section should show:

- preview surface class
- preview fields rendered there
- any clearly approximate or hint-only values
- whether the local app is merely restating those hints or has already parsed the actual artifact

### 3) What the local app has parsed so far

This section should show:

- normalized artifact ID if available
- declared subject, expiry, budget, or sender-intent posture if already parsed locally
- whether parsing happened through app inspect, CLI inspect, or deferred handoff
- any parse blockers or ambiguity

### 4) What is authoritative now

This section should show:

- preview-authority posture
- authoritative summary in one or two sentences
- whether later review is still required for admission, trust promotion, or claim application
- which receipt or inspect record currently grounds the answer

### 5) What definitely is not implied

This section should say, in plain language:

- previewed folder name or size does not prove trust or byte availability
- automatic browser handoff does not prove deliberate approval by the operator in this moment
- landing-page display does not mean the external service saw the full authority-bearing payload
- locally parsed artifact semantics do not yet prove later claim or remembered-trust consequences

### 6) Receipts and proof links

This section should link to:

- delivery-handoff receipt
- inspect receipt
- later claim or approval receipts if they exist
- predecessor or successor offer lineage when relevant

## Review grammar

Good labels:

- `Received via browser handoff`
- `Previewed in browser only`
- `Landing page saw wrapper; fragment stayed local`
- `Locally parsed after handoff`
- `Authoritative after inspect`
- `Full artifact exposed to external surface`
- `Re-deliver through local-only channel`

Bad labels:

- `Trusted link`
- `Verified in browser`
- `Safe because auto-opened`
- `Website approved`
- `Same as inspected`

## CLI implications

Example commands:

```text
anonsync offer intake show --latest
anonsync offer intake inspect dlv_01J...
anonsync offer inspect --from-browser-handoff dlv_01J...
anonsync offer handoff explain dlv_01J...
anonsync offer handoff review prepare dlv_01J... --outcome continue-to-local-inspect
anonsync offer handoff receipt show dhr_01J...
```

CLI output should keep `Received via`, `Preview said`, `Parsed locally`, `Authoritative now`, and `Not implied` adjacent.

## Daemon/API implications

A local daemon should expose delivery events separately from offer artifacts and claim outcomes.
Minimum surface:

```text
GET    /v1/offer-delivery-events
GET    /v1/offer-delivery-events/{delivery_event_id}
GET    /v1/offer-delivery-events/{delivery_event_id}/explain
POST   /v1/offer-delivery-events/{delivery_event_id}/inspect
POST   /v1/offer-delivery-events/{delivery_event_id}/prepare-review
GET    /v1/offer-delivery-handoff-receipts
GET    /v1/offer-delivery-handoff-receipts/{receipt_id}
```

Event stream additions:

- `offer.delivery_event_observed`
- `offer.delivery_preview_recorded`
- `offer.delivery_handoff_completed`
- `offer.delivery_authority_posture_changed`
- `offer.delivery_handoff_receipt_issued`

## Workbench implications

The workbench should add one intake-adjacent drawer or lane for **Received via / Preview / Parsed / Authoritative**.
That surface should let an operator answer, without opening logs:

- did this artifact come from browser auto-handoff, manual paste, QR scan, or local-only import
- what did the preview surface claim before the app inspected anything
- did any external service see only a wrapper or the full artifact
- what has the app parsed locally now
- what is still only hint-level, and what is actually authoritative

The workbench must not let `clicked in browser` become a trust badge.
Delivery convenience and preview confidence must remain inspectable public state.

## Canonical questions this layer must answer

A mature operator surface should be able to answer all of these without support-lore reconstruction:

- “Did this arrive through a browser landing page, clipboard, QR, or local file?”
- “What exactly was shown before the app inspected it?”
- “Did any third-party surface see the full artifact or only a wrapper?”
- “Was the handoff into the app automatic, confirmed, or manual?”
- “Which values are still hints, and which values are authoritative now?”
- “Which receipt proves that distinction later?”

## Non-clone conclusion

Resilio's current docs are useful precisely because they expose the seam.
They explain that a clicked link may open a landing page, may immediately hand off to the app, and may keep the authority-bearing fragment out of the landing-page request.
What they do not turn into one first-class operator surface is the boundary between `previewed outside the app` and `authoritative inside the app`.

AnonSync should keep the convenience while refusing the ambiguity.
The product should expose one explicit delivery-handoff provenance and preview-authority model so browser pages, QR overlays, clipboard strings, and local app inspection never blur into one vague `opened link` story.
'''

write('docs/117-offer-delivery-handoff-provenance-and-preview-authority-boundary-interface-spec.md', new_spec)

# README
readme = read('README.md')
readme = re.sub(r"- Revision: `rev\d+`", f"- Revision: `{rev}`", readme)
readme = re.sub(r"- Timestamp: `[^`]+` \(America/New_York\)", f"- Timestamp: `{ts}` (America/New_York)", readme)
readme = re.sub(r"- Codename: `[^`]+`", f"- Codename: `{codename}`", readme)
readme = re.sub(r"## What changed in this revision\n\n.*?\n## Current conclusion", f'''## What changed in this revision

This revision continues directly from `rev0103` and does six things:

1. Re-checks **Resilio Sync** again around the remaining delivery/handoff seam: current docs still say Sync links first open a landing page on the Resilio website that shows only basic folder info, may immediately transfer into the app when the browser already trusts the protocol handoff, and keep the `#` fragment out of the landing-page request.
2. Adds a dedicated **offer delivery-handoff provenance, preview authority, and app-intake boundary interface spec** so the archive no longer stops at `portable offer artifact`, but also answers `how did it arrive?`, `what was merely previewed before inspect?`, `what did any external surface actually see?`, and `what only became authoritative after local inspection?`
3. Tightens the **evaluation** so the non-clone case against Resilio gets sharper again: the product still has useful link/QR/browser convenience, but current docs still leave `opened in browser` too close to a vague trust story.
4. Extends the **interface, daemon/API, and offer-artifact contract** with delivery-event rows, preview-authority explanations, review plans, and receipts so clients can render `preview only`, `landing-page hit, fragment stayed local`, `browser auto-handoff`, or `locally inspected` without folklore.
5. Adds an additional **canonical flow** showing the new distinction this revision wants: once a portable offer crossed a browser or other delivery surface, the product must expose one explicit preview-versus-authority boundary instead of pretending `opened link` is self-explanatory.
6. Refreshes the **workbench, pattern language, ADRs, roadmap, offer-artifact spec, open questions, status, and reading order** so future revisions keep **delivery provenance separate from authoritative intake truth** wherever portable invitation mechanics, browser handoff, and later durable trust meet.

## Current conclusion''', readme, flags=re.S)
readme = re.sub(r"The sharper reason after this revision is: .*?linked receipts\.",
                 "The sharper reason after this revision is: Resilio still has strong mechanics, but current docs still leave one important seam too reconstructive once a portable offer passes through a browser or other delivery surface. AnonSync should let the operator ask all of `how did this arrive?`, `what did the preview surface actually say?`, `what did any external service really observe?`, `was the handoff automatic or explicit?`, `which fields are just hints?`, `which ones are locally parsed?`, and `what receipt proves the authority boundary later?` and get one explicit answer with delivery channel, preview surface, external-touch posture, handoff posture, current preview-authority class, authoritative offer reference, and linked receipts.",
                 readme, count=1, flags=re.S)
needle = "- `docs/116-offer-reissue-lineage-and-successor-boundary-interface-spec.md` — fixed predecessor/successor review anatomy for reissue reasons, successor relation, budget reset posture, explicit carry-forward limits, and successor-boundary receipts\n"
insert = needle + "- `docs/117-offer-delivery-handoff-provenance-and-preview-authority-boundary-interface-spec.md` — fixed delivery-event review anatomy for received-via, preview hints, external-touch posture, browser/app handoff, authority boundary, and delivery-handoff receipts\n"
readme = readme.replace(needle, insert)
readme += f'''\n\n## Revision addendum — delivery handoff and preview authority\n\nThis revision adds the next portable-offer governance layer:\n\n- delivery-event, preview-authority-explanation, and delivery-handoff-receipt object model work so browser landing pages, QR overlays, clipboard intake, and local-file import no longer collapse into one vague `opened link` story\n- UI and API work so `preview only`, `landing page saw wrapper only`, `browser auto-handoff`, `locally parsed`, and `authoritative after inspect` stay visibly distinct\n- lineage work linking later claim and trust consequences back to one exact delivery event instead of letting browser convenience stand in for authoritative intake truth\n'''
write('README.md', readme)

# Status
status = f'''# Status

## Scope of this revision

This revision is an in-place continuation of `rev0103`, driven by the current request:

- continue researching and tightening the archive without letting it sprawl
- evaluate Resilio Sync further so the non-clone case stays evidence-based rather than rhetorical
- spend more time on interface specs, especially where portable offers have already grown browser/app/QR delivery seams that must stay truthful
- keep Linux-first, overlay-first, and least-privilege assumptions intact unless the evidence actually breaks them
- preserve the useful parts of Resilio's convenience model without inheriting hidden trust side effects
- make sure the archive can answer not only `who redeemed this?`, `how many uses are left?`, and `what successor replaced it?`, but also `how did it get here?`, `what was merely previewed outside the app?`, and `what is authoritative only after local inspection?`

## Honesty note

This package **does** build directly on the immediately previous revision mounted in the working filesystem for this run.
The work therefore reflects a real continuation pass.

## Immediate output of this pass

The archive now contains:

- a fairer Resilio comparison that explicitly grants current strengths — maintained Sync v3, practical portable links, browser/app convenience, fragment-not-sent landing-page design, and strong approval-time identity review — while still naming the sharper reason not to clone its `opened link` story wholesale
- a new **offer delivery-handoff provenance, preview authority, and app-intake boundary interface spec** that defines how one surface should answer `how did this arrive?`, `what did the preview surface say?`, `what did any external surface actually see?`, `how did the app receive it?`, and `what is authoritative now?`
- stronger interface, offer-artifact, and daemon/API requirements so delivery-event rows, preview-authority explanations, handoff review plans, and delivery-handoff receipts become first-class surfaces instead of something reconstructed from browser history, remembered protocol permissions, and later claim outcomes
- stronger workbench and pattern-language rules so `Received via`, `Preview said`, `Parsed locally`, `Authoritative now`, and `Not implied` remain adjacent across dense and full surfaces
- an additional canonical flow showing the core split this revision wants: `opened in browser` is not the end of the story; the operator also needs one explicit preview-versus-authority surface before intake truth is trusted
- README, roadmap, ADR, source-note, open-question, status, and reading-order updates so future revisions keep **delivery provenance separate from authoritative intake truth** central wherever portable invitation mechanics, browser handoff, and later durable trust meet

## The main shift

`rev0101` proved that a serious operator surface needs a public redemption ledger.

`rev0102` proved that familiar attempts still need explicit equivalence and slot treatment.

`rev0103` proved that reissue still needs explicit predecessor/successor boundary truth.

`rev0104` tightens the lifecycle one level further:

> it is not enough to say `clicked a link` or `the browser opened the app`. A serious operator product must also say how the artifact arrived, what was merely previewed outside the app, what any external surface actually observed, and what only became authoritative after local inspection.

That changes the archive in five specific ways:

- delivery events now become first-class rows instead of ephemeral UI trivia
- preview metadata and authoritative local interpretation now have to stay visibly separate
- external-touch posture is now first-class, so `wrapper only`, `landing page saw request only`, and `full artifact exposed` stay visibly different
- browser auto-handoff can now stay convenient without masquerading as present-tense deliberate approval or proof
- the non-clone case against Resilio gets tighter again: the missing piece is not browser convenience itself, but the absence of one explicit contract for what a landing-page preview and app handoff actually mean

## What still remains unresolved

This revision intentionally still leaves important questions open, including:

- how much preview/handoff detail lightweight surfaces should show by default before they become noisy
- whether some delivery channels should be auto-frozen to `preview only` until manual confirm, even when parsing is technically possible
- when a landing-page/wrapper-only touch should still count as operationally sensitive enough to demand reissue through a narrower channel
- how long delivery-event history should remain prominent after the artifact has already been inspected, claimed, superseded, or revoked
- all prior unresolved questions from the surrounding archive, including mismatch-block thresholds, trust-family split thresholds, preview noise, review-queue aggressiveness, intake compression, pathless visibility ergonomics, transport scoping, settlement strictness, and successor carry-forward boundaries

## Files added in this revision

- `docs/117-offer-delivery-handoff-provenance-and-preview-authority-boundary-interface-spec.md`
- `update_rev0104.py`

## Files updated in this revision

- `README.md`
- `docs/00-status.md`
- `docs/10-resilio-sync-evaluation.md`
- `docs/30-interface-spec.md`
- `docs/31-daemon-api-spec.md`
- `docs/32-interface-flows.md`
- `docs/38-operator-workbench-interface-spec.md`
- `docs/39-interface-pattern-language.md`
- `docs/40-architecture-decisions.md`
- `docs/50-roadmap.md`
- `docs/52-capability-offer-and-claim-artifact-spec.md`
- `docs/64-critical-open-questions.md`
- `docs/sources.md`
'''
write('docs/00-status.md', status)

# Evaluation addendum
valuation_append = '''

## 16au) Browser landing pages and app handoff still leave preview authority too reconstructive

Current Resilio docs still make the problem concrete without yet turning it into one first-class contract.
`Link structure and flow` says a clicked Sync link first opens a landing page on the Resilio website that shows only basic folder info such as folder name and approximate size; if the browser has seen Sync links before, the page may immediately transfer the link into the Sync app; and the parameters after `#` are not actually sent to Resilio's server.
`Comprehensive guide to syncing (Desktop-Desktop)` says the default browser may ask permission to run the external Sync application and may remember that choice.
Those current docs are genuinely helpful, but they still leave one operator question too reconstructive:

- how the artifact arrived here in the first place
- what was merely previewed on an external surface before the local app inspected anything
- whether any external service saw only a wrapper URL, only a landing-page hit, or the full authority-bearing artifact
- whether app launch happened automatically because of old browser permission or because of a fresh explicit action now
- which values are still just hints and which are authoritative after local inspection

AnonSync should do better.
The product should preserve the convenience while insisting on one explicit delivery/handoff surface that says, in order, how the artifact arrived, what the preview surface showed, what any external surface could really see, how the local app received it, what is authoritative now, what definitely is not implied, and what receipt later proves the whole boundary.

### Requirement 84 — delivery provenance and preview authority must be explicit for portable offers

If the operator still has to combine `clicked link`, browser launch memory, landing-page preview, and later local inspect state to answer `how did this arrive, what was only previewed, and what is authoritative now?`, the product has not actually exposed its portable-offer intake truth.

AnonSync should instead publish one public model with:

- explicit delivery-channel classes such as `browser auto-handoff`, `browser confirmed launch`, `clipboard paste`, `QR scan`, and `local file open`
- explicit preview-surface classes and preview-field lists so `folder name` and `approx size` remain visibly hint-level unless later inspection proves them
- explicit external-touch posture such as `wrapper only`, `landing page saw request only`, `full artifact exposed`, and `local only`
- explicit preview-authority classes that keep `preview only`, `artifact derived unreviewed`, `locally parsed`, `locally inspected`, and `receipt backed` distinct
- explicit non-effects so browser auto-open, landing-page display, or QR preview never silently claim trust, byte availability, or claim readiness
- durable delivery-handoff receipts proving how the artifact crossed surfaces and when authority actually became local and inspectable

## Conclusion addendum from this pass

The reason not to clone Resilio is now even less about raw capability and even more about delivery truth.
Resilio clearly proves that browser/app convenience, landing-page previews, and fragment-not-sent link structure are useful.
What AnonSync should not copy is the way `opened in browser` can still sit too close to a vague trust story.

AnonSync should therefore preserve:

- practical portable-link delivery through ordinary channels
- clear local-app handoff when the operator really wants convenience
- privacy-preserving separation between wrapper request and authority-bearing fragment where the channel allows it

But it should reject:

- any design where browser preview metadata silently counts as authoritative offer truth
- any design where remembered protocol-launch convenience silently stands in for fresh operator intent or later trust
- any design where the operator cannot tell what external surfaces actually observed during delivery
'''
write('docs/10-resilio-sync-evaluation.md', read('docs/10-resilio-sync-evaluation.md') + valuation_append)

# Interface spec addendum
interface_append = '''

## Revision addendum — portable-offer delivery provenance and preview authority

Portable offers can now cross multiple surfaces before the real local inspection begins.
The interface contract must therefore preserve five adjacent truths wherever one portable offer enters the product:

- `Received via`
- `Preview said`
- `External touch`
- `Parsed locally`
- `Authoritative now`

A serious interface must be able to say:

- the browser landing page showed only hint metadata
- the authority-bearing fragment stayed local during landing-page fetch
- the browser auto-launched the app because the operator had previously allowed that protocol handoff
- the local app has now parsed the artifact, but claim/trust consequences still require later review

The operator must not need packet-capture lore, browser-memory guesswork, or support history to answer those questions.
'''
write('docs/30-interface-spec.md', read('docs/30-interface-spec.md') + interface_append)

# API addendum
api_append = '''

## Revision addendum — delivery events and preview-authority surfaces

Portable-offer intake now needs one additional public surface before claim or approval objects take over.
The daemon/API should therefore expose delivery events as first-class read objects.

Minimum additions:

```text
GET    /v1/offer-delivery-events
GET    /v1/offer-delivery-events/{delivery_event_id}
GET    /v1/offer-delivery-events/{delivery_event_id}/explain
POST   /v1/offer-delivery-events/{delivery_event_id}/inspect
POST   /v1/offer-delivery-events/{delivery_event_id}/prepare-review
GET    /v1/offer-delivery-handoff-receipts
GET    /v1/offer-delivery-handoff-receipts/{receipt_id}
```

A delivery event object should at minimum name:

- delivery channel
- preview surface
- preview fields
- external-touch posture
- handoff posture
- preview-authority posture
- authoritative offer reference if local parsing already succeeded

Event stream additions:

- `offer.delivery_event_observed`
- `offer.delivery_preview_recorded`
- `offer.delivery_handoff_completed`
- `offer.delivery_authority_posture_changed`
- `offer.delivery_handoff_receipt_issued`
'''
write('docs/31-daemon-api-spec.md', read('docs/31-daemon-api-spec.md') + api_append)

# Flow 163
flow_append = '''

## Flow 163 — browser landing page preview is not the same thing as authoritative local intake

Actors:

- **Ava** — folder owner issuing a portable offer
- **Ben** — receiver clicking the offer from a chat message
- **AnonSync** — the local product on Ben's machine

Goal:

Ben should be able to accept convenient browser/app handoff without losing the ability to tell what was merely previewed outside the app, what any external surface actually observed, and what only became authoritative after local inspection.

Initial conditions:

- Ava created a portable offer for subject `Research Photos`
- the offer is delivered to Ben via a chat message containing an HTTPS wrapper link
- Ben's browser has previously been allowed to launch AnonSync for this protocol family
- the delivery wrapper exposes a landing page that can preview folder name and approximate size

Steps:

1. Ben clicks the link in chat.
2. The browser opens a landing page that shows `Research Photos` and an approximate size hint.
3. Because Ben already allowed protocol launch earlier, the browser auto-hands the link to AnonSync.
4. AnonSync records a **delivery event** immediately before any claim is prepared.
5. The intake drawer shows a compact row:
   - `Received via: Browser auto-handoff`
   - `Preview said: Research Photos, approx size only`
   - `External touch: landing-page hit, fragment stayed local`
   - `Parsed locally: pending`
   - `Authoritative now: preview only`
6. Ben opens the intake explanation pane.
7. The explanation pane shows two separate blocks:
   - **Preview surface** — browser landing page, hint-only metadata, no trust or claim semantics implied
   - **Authority boundary** — app has not yet parsed the artifact; no claim/trust consequence has been established
8. Ben chooses `Inspect locally`.
9. AnonSync parses the artifact and updates the row:
   - `Received via: Browser auto-handoff`
   - `Preview said: Research Photos, approx size only`
   - `External touch: landing-page hit, fragment stayed local`
   - `Parsed locally: subject, expiry, sender-intent posture, redemption budget`
   - `Authoritative now: locally inspected`
10. The pane explicitly states non-effects:
    - browser preview did not prove byte availability
    - auto-launch did not prove fresh approval in this moment
    - local inspect did not yet grant local claim or broader remembered trust
11. Ben exports a delivery-handoff receipt for later audit.

Expected outcome:

- Ben gets browser/app convenience without letting `opened link` collapse preview, transport, parsing, and trust into one vague story
- delivery provenance remains inspectable even after later claim or approval work begins
- later support/debug/audit work can point to one durable receipt instead of browser folklore
'''
write('docs/32-interface-flows.md', read('docs/32-interface-flows.md') + flow_append)

# Workbench addendum
workbench_append = '''

## Revision addendum — intake must keep delivery provenance adjacent to authority truth

Offer-intake surfaces should now reserve one compact strip or drawer for:

- `Received via`
- `Preview said`
- `External touch`
- `Parsed locally`
- `Authoritative now`

The workbench should not require opening raw logs to answer whether a browser landing page merely previewed a folder name, whether the app was auto-launched by remembered permission, or whether the local app has actually parsed the artifact yet.

Dense rows should still preserve at least:

- one delivery-channel chip
- one preview-authority chip
- one external-touch chip
- one `Inspect locally` or `Review handoff` verb when the current state is still ambiguous
'''
write('docs/38-operator-workbench-interface-spec.md', read('docs/38-operator-workbench-interface-spec.md') + workbench_append)

# Pattern language addendum
pattern_append = '''

## Revision addendum — received-via / preview / authority adjacency

Portable-offer surfaces should now follow one additional adjacency rule:

- **Received via**
- **Preview said**
- **Authoritative now**

should remain visually adjacent, with **External touch** immediately nearby when any browser, QR, mail, chat, or file-manager surface participated.

Good compression:

- `Browser auto-handoff`
- `Preview only`
- `Landing page saw wrapper only`
- `Locally inspected`

Bad compression:

- `Opened successfully`
- `Trusted link`
- `Verified by browser`
'''
write('docs/39-interface-pattern-language.md', read('docs/39-interface-pattern-language.md') + pattern_append)

# ADR 117
adr_append = '''

## ADR-117 — delivery preview must stay separate from authoritative local intake

### Status

Accepted

### Context

Portable offers now have first-class objects for sender intent, actual redeemer identity, budget, multi-redemption history, slot treatment, and successor lineage.
One remaining seam still risked collapsing too much into one vague story: browser landing pages, QR overlays, clipboard intake, and external-app handoff can show useful preview information before the local app has actually performed authoritative inspection.

Current Resilio docs make that seam real in a useful way: links open a landing page that shows basic folder info, may immediately transfer into the app if protocol launch is already trusted, and keep the `#` fragment out of the landing-page request.
That is useful convenience and useful privacy posture, but it still leaves too much room for an operator surface to blur `previewed outside the app` with `authoritative inside the app`.

### Decision

AnonSync will model **delivery events** separately from offer artifacts, claim preparation, and later trust consequences.
Every portable-offer intake path must preserve at least these distinct public facts:

- delivery channel
- preview surface
- external-touch posture
- handoff posture
- preview-authority posture
- authoritative offer reference once local parsing succeeds

The interface must keep preview hints, local parse results, and authoritative review truth visibly separate.
`Opened in browser`, `auto-launched app`, or `previewed folder name` can never stand in for trust, byte availability, claim readiness, or remembered approval.

### Consequences

Positive:

- browser/app convenience remains usable without becoming trust folklore
- external-touch privacy posture becomes inspectable public state
- later audit/support work can reason from delivery receipts instead of browser-memory guesswork

Costs:

- intake surfaces gain one more layer of row/detail state
- APIs and logs need a delivery-event object family in addition to offer and claim objects
- lightweight clients must compress the story carefully without hiding the preview-versus-authority boundary

### Alternatives rejected

- treat browser landing-page preview as just another offer inspect result
- bury delivery provenance only in debug logs
- collapse `auto-opened successfully` into a generic success badge
'''
write('docs/40-architecture-decisions.md', read('docs/40-architecture-decisions.md') + adr_append)

# Roadmap addendum
roadmap_append = '''

## Revision addendum — delivery provenance and preview-authority boundaries

This revision adds the next portable-offer governance layer:

- delivery-event, preview-authority-explanation, and delivery-handoff-receipt object model work so browser landing pages, QR overlays, clipboard intake, and local-file import no longer collapse into one vague `opened link` story
- UI and API work so `preview only`, `landing page saw wrapper only`, `browser auto-handoff`, `locally parsed`, and `authoritative after inspect` stay visibly distinct
- lineage work linking later claim and trust consequences back to one exact delivery event instead of letting browser convenience stand in for authoritative intake truth
'''
write('docs/50-roadmap.md', read('docs/50-roadmap.md') + roadmap_append)

# Offer artifact spec addendum
artifact_append = '''

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
'''
write('docs/52-capability-offer-and-claim-artifact-spec.md', read('docs/52-capability-offer-and-claim-artifact-spec.md') + artifact_append)

# Open questions addendum
openq_append = '''

## 31) How much delivery provenance should lightweight intake surfaces keep visible before they become noisy?

The archive now makes delivery provenance and preview-authority first-class, but one policy seam still needs real judgment:

- when should dense/mobile intake rows show only `Received via` + `Authoritative now`, and when must `External touch` stay visible too
- whether browser auto-handoff should always trigger at least one expanded explanation surface before claim prep begins
- how aggressively old delivery events should remain visible after local inspect, claim, or supersession has already happened
- when a `landing-page hit, fragment stayed local` posture is still sensitive enough to bias the product toward re-delivery through a narrower channel

This matters because too little visibility recreates `opened link = trusted enough`, while too much visibility could make routine safe intake feel like a networking seminar.
'''
write('docs/64-critical-open-questions.md', read('docs/64-critical-open-questions.md') + openq_append)

# Sources addendum
sources_append = '''

## Revision note — rev0104

This revision mainly leans again on the same current Resilio sources already in the archive, especially:

- `Link structure and flow` for landing-page preview, browser/app handoff, link fragment handling, and approval-time public-key flow
- `Comprehensive guide to syncing (Desktop-Desktop)` for browser launch prompts, remembered external-app handoff, and ordinary-channel delivery of links/keys
- `Sync Share Dialog (Desktop)` as continuing background for portable-link sharing means and link/QR mechanics
'''
write('docs/sources.md', read('docs/sources.md') + sources_append)

# update doc map in README maybe already did; done.

# insert map entry in top README maybe no more.

# record new script in itself maybe nothing.
