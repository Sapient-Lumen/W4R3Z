# ADR-0244: Workstation sanitized inspection derivatives stay inspection-shaped and disposable-first

Date: 2026-03-22
Status: Accepted

## Context

`adrs/ADR-0196-workstation-imported-foreign-documents-stay-view-first-and-working-copy-shaped.md` already fixed the first mutation boundary for foreign imported originals:

- imported foreign originals stay **view-first**
- editing them requires an explicit working-copy step
- and baseline workstation behavior is **work on a copy**, not **edit the imported original in place**

`adrs/ADR-0243-workstation-imported-foreign-document-viewing-stays-disposable-first.md` then fixed the first viewer-lifetime boundary too:

- the ordinary viewing route for newly imported foreign originals is **disposable-first**
- the allow-path route is **policy-pinned** rather than a remembered persistent-reader default
- and missing disposable support fails closed instead of silently weakening the posture

That still left one practical implementation ambiguity:
**once a sanitize/convert pipeline has produced an inspection derivative from that same foreign import, does the workstation baseline now treat the derivative as an ordinary trusted/local document for persistent viewing by default, or does it remain an inspection-shaped object until some later explicit promotion/authoring act occurs?**

If the archive leaves that open, sanitization easily turns into provenance laundering:

- the system imports risky foreign bytes,
- produces a sanitized inspection derivative,
- then quietly reclassifies the result as an ordinary persistent-viewer document,
- and humans lose the distinction between **safer to inspect** and **fully promoted/trusted-local by default**.

Qubes / Dangerzone patterns and Protected View style lessons point toward a smaller answer: safer inspection is not the same as implicit trust-promotion. We need one more cut so the workstation story stays implementable without turning sanitizer success into ambient ordinary-document authority.

## Decision

1. **Sanitized inspection derivatives remain inspection-shaped by default.**
sanitized inspection derivatives remain inspection-shaped by default.
   - A sanitized or converted derivative produced from foreign imported content does not automatically become an ordinary trusted/local document class.
   - The archive should keep naming that state explicitly as `sanitized-inspection-derivative` where typed evidence needs it.

2. **Ordinary viewing of sanitized inspection derivatives stays disposable-first.**
   - The ordinary `document_viewing` route for that derivative remains policy-pinned to an enrolled disposable viewer target.
   - Remembered persistent `document_viewing` defaults do not silently win just because the sanitizer succeeded.

3. **Sanitizer success is not implicit trust-promotion.**
sanitizer success is not implicit trust-promotion.
   - It may justify a safer inspection story than the original imported bytes.
   - It does not by itself justify ambient persistent-viewer defaults, ambient editing authority, or a hidden provenance reset.

4. **Mutation still requires the existing explicit working-copy lane.**
   - If a user wants to modify the sanitized derivative, the next official step is still `content.working-copy.plan` / `content.working-copy.receipt`.
   - The typed source class for that act should remain `sanitized-inspection-derivative` rather than collapsing into generic local-document folklore.

5. **Any broader trusted/local or persistent-viewing posture needs a later explicit boundary.**
   - If the archive later wants a promotion/finalization adapter or a narrow class of sanitized documents that may default to persistent viewing, that must be decided separately.
   - It is not implied by sanitize success alone.

## Consequences

### What this locks now

- The baseline workstation document story becomes: **import → disposable inspect original → optional disposable inspect sanitized derivative → explicit working copy if mutation is intended**.
- Sanitization remains useful for safer inspection without becoming an ambient trust-promotion shortcut.
- The archive keeps its anti-laundering story coherent: provenance and import lineage do not disappear just because a converter produced a new inspection artifact.
- Existing typed surfaces are enough: we can keep using the current route receipts plus `content.working-copy.*.source.source_class = sanitized-inspection-derivative` instead of inventing a new subsystem.

### What stays intentionally open

This ADR does **not** decide:

- whether some narrow sanitized classes should later support explicit promotion into persistent viewing
- what the typed promotion/finalization artifact should look like
- profile-`C` compatibility adapters for broader desktop convenience
- media/IDE/design-tool role families

## Why this is the smallest viable cut

The archive already had almost all the needed pieces:

- a sanitize-first instinct
- an anti-laundering origin boundary
- a disposable-first viewing floor for imported originals
- and an explicit working-copy lane for mutation

The missing move was simply to say that sanitized inspection output is still inspection output unless a later boundary explicitly says otherwise.
That single distinction keeps safer inspection from quietly turning into ambient trusted/local handling semantics.

## Wiring

- sanitization portal: `docs/267-sanitization-portal-and-disposable-sandboxes.md`
- anti-laundering boundary: `docs/484-origin-label-authority-and-anti-laundering-boundary.md`
- imported-original view-first boundary: `docs/606-workstation-imported-foreign-documents-stay-view-first.md`
- imported-original disposable-viewing boundary: `docs/653-workstation-imported-foreign-document-viewing-stays-disposable-first.md`
- new sanitized-derivative boundary doc: `docs/654-workstation-sanitized-inspection-derivatives-stay-inspection-shaped-and-disposable-first.md`
- working-copy lane: `docs/607-workstation-working-copy-receipts-and-edit-route-joins.md`
- risk/open questions: `docs/266-open-questions-and-risk-register.md`
