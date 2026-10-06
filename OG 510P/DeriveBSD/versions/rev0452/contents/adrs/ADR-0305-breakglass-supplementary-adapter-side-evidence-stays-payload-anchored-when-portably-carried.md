# ADR-0305: Breakglass supplementary adapter side evidence stays payload-anchored when portably carried

- Status: Accepted
- Date: 2026-03-23

## Context

`ADR-0301` fixed official support handoff to stay authority-first on exact `breakglass.receipt` digests.
`ADR-0302` then fixed supplementary breakglass adapter/runtime exports to stay receipt-first on typed redaction/export/transport proof instead of raw attachment folklore.
`ADR-0303` then fixed that those supplementary receipt chains still need the exact `breakglass.receipt` digest in the same portable story.
`ADR-0304` then fixed that the portable story must stay artifactized and off live control locators.

That still leaves one expensive ambiguity:

**can the portable story still degenerate into a receipt-only chain that proves handling happened, but never names the passive artifact or accepted case object that was actually carried?**

If the archive leaves this fuzzy, implementations will drift toward another bad shortcut:

1. a case exports only `redaction.receipt` / `export.receipt` / `transport.receipt` digests for richer breakglass adapter/runtime material,
2. later review can prove that *some* governed handling happened,
3. but the portable story never pins which passive artifact or accepted case object those receipts were about,
4. and support falls back to portal archaeology, screenshot filenames, or external case memory to recover the actual payload identity.

Receipt-first, authority-anchor, and live-locator firewall are still incomplete if the portable story can stop one step short of naming the thing that was handled.

## Decision

1. If richer supplementary breakglass adapter/runtime material travels portably, the same bundle or handoff must carry at least one **payload identity anchor** for that material.

2. A payload identity anchor is either:
   - an exported passive artifact digest, or
   - accepted case-object proof when the stronger handoff lane already has a typed accepted remote object for that passive artifact.

3. Typed handling receipts remain required where they already apply, but they are **not enough on their own**. A receipt-only chain is incomplete portable evidence for supplementary breakglass adapter/runtime material.

4. The payload identity anchor stays subject to the already-accepted boundaries:
   - authority-first on exact `breakglass.receipt` digests,
   - receipt-first on typed redaction/export/transport proof,
   - authority-anchored to the same portable story,
   - artifactized and off live control locators.

5. This decision does **not** mint a dedicated typed family for richer adapter-side evidence, and it does **not** standardize per-artifact/session joins. It only closes the smaller leak worth fixing immediately: portable supplementary evidence must still name at least one passive artifact or accepted case object rather than stopping at process receipts.

## Consequences

Good:

- portable review can identify both **that** governed handling happened and **what artifact/object** it governed
- support/export stories stay content-addressed instead of falling back to portal archaeology
- and the archive keeps passive artifact identity separate from live control-entry detail

Costs:

- some current practices that export only receipt digests for screenshots or console captures will now be recognized as incomplete portable evidence
- support/export tooling must preserve at least one passive artifact digest or accepted case-object proof when richer supplementary material travels
- and future richer adapter-side-evidence work still needs separate RFC/ADR treatment if stronger typed joins are desired

## Why this is the right narrow cut

The custody and integrity guidance already points this way. NIST SP 800-86 says forensic procedures should support admissibility by gathering and handling evidence properly, maintaining chain of custody, and storing evidence securely, and it stresses identifying, labeling, recording, and collecting data while preserving integrity. RFC 6920 likewise formalizes naming digital objects by hash so the referenced object can be authenticated to the same degree as the reference. Together, that is the boring portable-evidence answer here: typed handling receipts are useful, but the archive still needs at least one passive artifact or accepted case-object identity anchor for the thing those receipts handled.

## Follow-on

Still open as later work:

- whether a dedicated breakglass adapter-side-evidence family should later carry richer per-artifact/session joins
- whether accepted case-object proof needs tighter continuity rules in the first richer typed family
- and whether some product shapes want stronger defaults that suppress supplementary adapter/runtime material entirely
