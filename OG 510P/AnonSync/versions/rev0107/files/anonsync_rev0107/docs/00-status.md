# Status

## Scope of this revision

This revision is an in-place continuation of `rev0106`, driven by the current request:

- continue researching and tightening the archive without letting it sprawl
- evaluate Resilio Sync further so the non-clone case stays evidence-based rather than rhetorical
- spend more time on interface specs, especially where portable offers already cross browser previews, QR carriers, copied text, and local-app handoff
- keep Linux-first, overlay-first, and least-privilege assumptions intact unless the evidence actually breaks them
- preserve the useful parts of Resilio's convenience model without inheriting hidden trust side effects
- make sure the archive can answer not only `what field was visible?` and `what stayed sealed?`, but also `is this preview sufficient for any real decision?` and `what missing governance facts must the UI explicitly refuse to infer?`

## Honesty note

This package **does** build directly on the immediately previous revision mounted in the working filesystem for this run.
The work therefore reflects a real continuation pass.

## Immediate output of this pass

The archive now contains:

- a fairer Resilio comparison that explicitly grants current strengths — maintained Sync v3, practical multi-carrier link/QR delivery, minimal landing-page preview, browser/app handoff, and private `#`-fragment delivery mechanics — while still naming the sharper reason not to clone its preview surface wholesale
- a new **offer preview sufficiency, omission classes, and non-inference boundary spec** that defines how one surface should answer `what decisions is this preview actually sufficient for?`, `which decisions are still blocked?`, and `which missing fields are omission facts rather than safe defaults?`
- stronger interface, offer-artifact, and daemon/API requirements so preview-sufficiency rows, omission explanations, sufficiency review plans, and non-inference receipts become first-class surfaces instead of something reconstructed from habit and support lore
- stronger workbench and pattern-language rules so `Recognition only`, `Routing only`, `Governance insufficient`, `Claim not ready`, and `Missing fields` remain adjacent across dense and full surfaces
- an additional canonical flow showing the core split this revision wants: the browser preview can help the operator recognize the offer without letting name/size familiarity stand in for permission, approval, expiry, use-count, or later trust truth
- README, roadmap, ADR, source-note, open-question, status, and reading-order updates so future revisions keep **preview sufficiency and omission non-inference** central wherever portable invitation mechanics and later durable trust meet

## The main shift

`rev0104` proved that delivery preview and authoritative intake must stay visibly separate.

`rev0105` proved that canonical artifact identity must survive carrier changes.

`rev0106` proved that preview-visible hints must stay separate from sealed authority-bearing fields.

`rev0107` tightens the lifecycle one level further:

> it is not enough to say `this label and size were only hints`. A serious operator product must also say whether those hints are sufficient for recognition only, for local routing only, or for any real governance decision at all — and it must name the omitted fields instead of letting operators silently fill them in.

That changes the archive in five specific ways:

- preview surfaces now publish **decision sufficiency** instead of merely `hint` versus `authoritative`
- omitted governance-bearing fields now become first-class facts rather than invisible absences
- minimal browser or QR previews can stay useful while still refusing inference about permissions, approval requirements, expiry, use counts, or durable trust consequences
- later claim/trust/budget decisions can now cite not only which field classes they used, but whether the preview phase was ever sufficient for that decision domain at all
- the non-clone case against Resilio gets tighter again: the missing piece is not the existence of a minimal preview, but the absence of one explicit sufficiency-and-omission contract that keeps `looks familiar` from turning into `safe to proceed`

## What still remains unresolved

This revision intentionally still leaves important questions open, including:

- how aggressively lightweight surfaces should compress `recognition only / routing only / governance insufficient / claim not ready` without becoming misleading
- whether some preview-visible fields should be suppressible by stricter sender policy even when they would help human recognition
- when repeated harmless preview exposure should still bias the product toward reissue through a narrower carrier
- how long omission history should remain prominent after local parse, claim, supersession, or revocation has already happened
- all prior unresolved questions from the surrounding archive, including mismatch-block thresholds, trust-family split thresholds, preview noise, review-queue aggressiveness, intake compression, transport scoping, settlement strictness, successor carry-forward boundaries, carrier-alias auto-collapse thresholds, and preview-metadata disclosure policy

## Files added in this revision

- `docs/120-offer-preview-sufficiency-and-omitted-governance-non-inference-spec.md`
- `update_rev0107.py`

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
