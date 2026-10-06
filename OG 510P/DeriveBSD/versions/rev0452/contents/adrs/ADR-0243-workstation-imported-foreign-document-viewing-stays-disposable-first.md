# ADR-0243: Workstation imported foreign document viewing stays disposable-first

Date: 2026-03-22
Status: Accepted

## Context

`adrs/ADR-0195-workstation-file-open-import-join-and-bounded-document-roles.md` already fixed the high-level file-open shape:

- import first, route second,
- keep ordinary document handling inside bounded `document_viewing` / `document_editing` roles,
- keep host-open fallback off the baseline,
- and keep file-open evidence joined back to `content.import.receipt`.

`adrs/ADR-0196-workstation-imported-foreign-documents-stay-view-first-and-working-copy-shaped.md` then fixed the next mutation boundary:

- foreign imported originals stay **view-first**,
- `document_editing` does not apply to the imported original,
- and baseline workstation behavior becomes **work on a copy** instead of **edit the imported original in place**.

That still left one expensive implementation ambiguity:
**when a newly imported foreign/quarantined document is merely being viewed, should the remembered persistent `document_viewing` target win by default, or should the baseline force a disposable viewer posture?**

If the archive leaves that open, the easiest implementation path becomes the real product:

- a persistent viewer AppVM quietly becomes the ordinary landing zone for risky foreign bytes,
- remembered `document_viewing` defaults start acting like ambient approval for raw imported content,
- “we have a disposable viewer too” turns into a convenience option rather than the default safety posture,
- and support/export surfaces can no longer assume that ordinary foreign-document inspection stayed in a short-lived no-network lane.

Qubes disposable-open patterns, document-portal thinking, and Protected View style lessons all point toward the same smaller answer: foreign imported content should open in a disposable inspection lane unless and until a later boundary explicitly promotes it elsewhere.

We need one more hard cut so the workstation story stays implementable without quietly normalizing persistent foreign-document viewers.

## Decision

1. **Newly imported foreign/quarantined document viewing is disposable-first.**
   - The ordinary route for a foreign imported original on the `document_viewing` lane should resolve to an enrolled disposable viewer target.
   - The authoritative intent-route interpretation is that this is a **policy-shaped foreign-content posture**, not just whatever remembered role default happens to be present.

2. **Remembered persistent `document_viewing` defaults do not silently win for foreign imported originals.**
   - A persistent viewer target may still exist in `intent.role.binding` for trusted/local/stable reading workflows.
   - But the ordinary foreign-import path must not silently fall back to that persistent target just because it is the remembered default.

3. **No disposable viewer target means fail closed or take a separately typed stronger step.**
   - If no disposable `document_viewing` target is enrolled/healthy, baseline routing should deny the open or require a separately typed sanitize/compatibility path.
   - It must not quietly reopen the persistent-viewer fallback.

4. **Use existing objects rather than inventing a new subsystem.**
   - The foreign-document inspection posture should continue compiling through existing `content.import.plan` / `content.import.receipt` execution fields (`isolation`, `network`, `lifetime`) plus existing `intent.request` / `intent.route.receipt` joins.
   - For the ordinary foreign-document baseline, that means `microvm` + `none` + `disposable` remains the canonical inspection execution posture.

5. **Persistent `document_viewing` still has a place, but not as the baseline foreign-import lane.**
   - Trusted/local reading workflows may still use persistent viewers.
   - Later ADRs may decide which sanitized or trusted-local derivatives are eligible for persistent viewing by default.
   - Profile `C` may later document a bounded compatibility adapter if needed, but that must stay explicit and must not weaken profile `B`.

## Consequences

### What this locks now

- The baseline workstation foreign-document story is now: **import → disposable view → explicit working copy if mutation is intended**.
- `intent.role.binding` can keep both persistent and disposable `document_viewing` targets without letting the persistent one become ambient foreign-content authority.
- The ordinary foreign-document route can now be expressed concretely in examples: `intent.request.context.import_receipt_digest` joins to the import, and the allow-path document-view route becomes `policy-pinned` rather than a remembered persistent default.
- Support/export posture stays smaller and more explainable because ordinary foreign-document inspection remains short-lived and no-network by default.
- A/B/C/D stay coherent without forking: B gets the stronger boring default, A/D can reuse it for risky maintenance artifacts, and C can still carry explicit adapter pressure without redefining the baseline.

### What stays intentionally open

This ADR does **not** decide:

- which trusted/local file classes should prefer persistent vs disposable `document_viewing`,
- whether some sanitized derivatives deserve a persistent-reading default later,
- media/IDE/design-tool role families,
- exact disposable-viewer health probing,
- or the exact shape of any future profile-`C` compatibility adapter.

## Why this is the smallest viable cut

The archive already had the right moving parts:

- import receipts,
- route receipts,
- role bindings with both persistent and disposable targets,
- a view-first mutation boundary,
- and explicit working-copy transitions.

The missing move was simply to stop treating remembered persistent viewer state as the de facto answer for foreign imported originals.
That distinction is small, but it prevents the workstation safety story from collapsing back into a convenience-shaped persistent-reader default.

## Wiring

- file-open floor: `docs/605-workstation-file-open-import-and-bounded-document-roles.md`
- view-first boundary: `docs/606-workstation-imported-foreign-documents-stay-view-first.md`
- new viewing-posture boundary doc: `docs/653-workstation-imported-foreign-document-viewing-stays-disposable-first.md`
- workstation host/AppVM boundary: `docs/457-workstation-host-ui-and-appvm-boundary.md`
- intent routing: `docs/199-intent-routing-and-plumbing.md`
- portals/powerbox: `docs/179-portals-and-powerbox.md`
- risk/open questions: `docs/266-open-questions-and-risk-register.md`
