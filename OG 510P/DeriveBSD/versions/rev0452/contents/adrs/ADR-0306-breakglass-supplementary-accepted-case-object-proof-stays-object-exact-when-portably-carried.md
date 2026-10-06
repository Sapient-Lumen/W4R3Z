# ADR-0306: Breakglass supplementary accepted case-object proof stays object-exact when portably carried

- Status: Accepted
- Date: 2026-03-23

## Context

`ADR-0301` fixed official support handoff to stay authority-first on exact `breakglass.receipt` digests.
`ADR-0302` then fixed supplementary breakglass adapter/runtime exports to stay receipt-first on typed redaction/export/transport proof.
`ADR-0303` then fixed that those supplementary receipt chains still need the exact `breakglass.receipt` digest in the same portable story.
`ADR-0304` then fixed that the portable story must stay artifactized and off live control locators.
`ADR-0305` then fixed that portable supplementary evidence must stay payload-anchored to at least one passive artifact digest or accepted case-object proof.

That still leaves one small but expensive ambiguity:

**if the payload anchor takes the accepted case-object-proof lane instead of a passive artifact digest, is a parent case/ticket/thread id enough, or must the proof stay exact on the accepted remote object itself?**

If the archive leaves this fuzzy, implementations will drift toward another weak shortcut:

1. a bundle carries typed handling receipts plus some accepted case-object proof,
2. but the proof only names a parent case id, incident thread, or portal container,
3. later review can tell that *something* breakglass-shaped landed in the case,
4. but still cannot answer which exact accepted attachment/object/message-part was the payload anchor.

That is only a softer form of the same archaeology problem `ADR-0305` was meant to prevent.
A parent case container is useful context, but it is not object identity.

## Decision

1. When portable supplementary breakglass adapter/runtime evidence uses **accepted case-object proof** as its payload anchor, that proof must stay **object-exact**.

2. “Object-exact” means the accepted proof names the exact remote attachment/object/message-part identity that held the passive artifact, not merely the parent case/ticket/thread/container id.

3. Parent case/ticket/thread/container ids may still travel as context, but they do **not** satisfy the payload-anchor rule by themselves.

4. This decision does **not** mint a dedicated typed family for richer breakglass adapter/runtime material, and it does **not** require the stronger packet-capture-style continuity stack (`remote_validator`, `remote_protection`, `remote_locator`) for this supplementary lane yet.
   It closes only the smaller leak worth fixing now: accepted case-object proof must at least be exact about **which remote object** was accepted.

5. The existing boundaries still apply unchanged:
   - official handoff stays authority-first on `breakglass_receipt_digests`,
   - richer supplementary material stays receipt-first when exported,
   - the same portable story stays authority-anchored,
   - live control locators stay out,
   - and the payload anchor still stays passive rather than reconnect-capable.

## Consequences

Good:

- accepted case-object proof now names something reviewable enough to stand in for a passive artifact digest when that stronger handoff lane is used
- detached review no longer has to infer the payload anchor from a parent case id plus screenshots or portal clicking
- and future richer typed-family work can start from a cleaner floor instead of first undoing case/container ambiguity

Costs:

- support/export tooling must preserve the exact accepted remote object id when it wants to use case-object proof as the payload anchor
- some existing portal workflows that only preserve parent case ids will now be recognized as incomplete portable evidence
- and stronger remote-validator / protection / locator continuity still remains future work rather than something this cut settles now

## Why this is the right narrow cut

NIST SP 800-86 already points at the identity discipline needed for portable evidence by describing collection as identifying, labeling, recording, and acquiring data while preserving integrity. RFC 6920 likewise centers identity on the digital object rather than on a surrounding container by defining names for the object itself using the output of a hash function. DeriveBSD already made the same practical move for stronger packet-capture export by requiring remote-object continuity (`docs/521-packet-capture-strong-export-remote-object-continuity-boundary.md`). This breakglass cut keeps the supplementary lane aligned with that lesson without prematurely importing the whole stronger-export stack.

## Follow-on

Still open as later work:

- whether accepted case-object proof should later gain remote-validator / protection / locator continuity requirements
- whether the future richer typed family should define a canonical accepted-case-object schema instead of reusing generic supplementary evidence digests
- and whether some product shapes should suppress accepted external case-object anchors entirely in favor of passive artifact digests only
