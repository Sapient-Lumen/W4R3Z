# ADR-0308: Breakglass supplementary accepted case-object proof stays remote-protection-shaped when visible

- Status: Accepted
- Date: 2026-03-23

## Context

`ADR-0301` fixed official support handoff to stay authority-first on exact `breakglass.receipt` digests.
`ADR-0302` then fixed supplementary breakglass adapter/runtime exports to stay receipt-first on typed redaction/export/transport proof.
`ADR-0303` then fixed that those supplementary receipt chains still need the exact `breakglass.receipt` digest in the same portable story.
`ADR-0304` then fixed that the portable story must stay artifactized and off live control locators.
`ADR-0305` then fixed that portable supplementary evidence must stay payload-anchored to at least one passive artifact digest or accepted case-object proof.
`ADR-0306` then fixed that the accepted-case-object lane must stay object-exact on the accepted remote attachment/object/message-part.
`ADR-0307` then fixed that the same accepted-case-object lane must stay validator-pinned when the adapter can see a stronger revision / version / generation / ETag-like validator for that exact accepted object.

That still leaves one small but expensive ambiguity:

**if the portable story already has the exact accepted object and its visible validator, can it still quietly treat any accepted portal copy as durable evidence even when the adapter can also see an explicit overwrite/delete-resistance posture for that same accepted object?**

If the archive leaves this fuzzy, implementations will drift toward another weak shortcut:

1. a bundle carries typed handling receipts plus accepted case-object proof for the right remote object,
2. and it may even preserve the visible validator for that exact accepted representation,
3. but it still says nothing typed about whether that accepted remote copy was under retention, legal hold, append-only discipline, or only ordinary mutable portal storage,
4. so later review cannot tell whether the accepted external object was merely delivered or also claimed to be protected from routine overwrite/delete.

That is the same coherence leak DeriveBSD already closed for stronger packet-capture export with `remote_protection` continuity.
This breakglass lane is smaller, but the same minimum lesson applies.

## Decision

1. When portable supplementary breakglass adapter/runtime evidence uses **accepted case-object proof** as its payload anchor, and the export/support adapter can see a remote protection / retention / hold posture for that exact accepted object, the proof must stay **remote-protection-shaped when visible**.

2. “Remote-protection-shaped when visible” means the portable story preserves the strongest recipient-side overwrite/delete-resistance posture the adapter can actually see for that same accepted remote attachment/object/message-part.
   Typical examples include a retention-until window, legal hold, policy-locked retention, append-only logging, versioned noncurrent retention, or another opaque reviewed protection posture.

3. This rule is conditional on visibility.
   If the adapter cannot surface any such protection posture, `ADR-0306`'s object-exact floor and `ADR-0307`'s validator-pinned floor still apply and the archive does not invent a fake durability claim.

4. Parent case/ticket/thread/container ids remain context only, and the accepted object id and visible validator (when available) still remain mandatory.
   Remote protection continuity is an additional strengthening rule on top of object-exactness and validator pinning when the adapter can actually see it.

5. This decision still does **not** mint a dedicated typed family for richer breakglass adapter/runtime material, and it still does **not** import remote locator continuity or metadata-only reverification into this supplementary lane yet.
   It closes only the next narrow leak worth fixing now: if the accepted-case-object lane can already see a remote protection posture for that exact accepted object, keep it aligned too.

## Consequences

Good:

- accepted case-object proof no longer silently upgrades any accepted portal object into “durable evidence” when the adapter could already say whether overwrite/delete resistance existed
- support/export adapters gain one portable rule for visible remote retention/hold posture without needing a whole new artifact family first
- future typed-family work can inherit a cleaner floor instead of first undoing durability folklore

Costs:

- support/export tooling that can see remote protection posture must preserve it when it uses accepted case-object proof as the payload anchor
- some existing portal workflows that only preserve accepted object id + validator but discard visible hold/retention state will now be recognized as incomplete stronger portable evidence
- and remote locator continuity still remains future work rather than something this cut settles now

## Why this is the right narrow cut

Mainstream evidence/object stores already separate “the right object landed” from “that object is protected.” Amazon S3 Object Lock distinguishes retention periods from legal holds and says those controls prevent an object version from being overwritten or deleted. Azure immutable blob storage documents time-based retention and legal holds as WORM posture that prevents modification or deletion during the effective retention period. Google Cloud Storage Object Retention Lock likewise lets an object retain a retention configuration that can prevent the retention time from being reduced or removed. DeriveBSD does not copy any one backend API, but it should steal the same lesson here: if the accepted-case-object lane can already see overwrite/delete-resistance posture for the exact accepted object, preserve that posture instead of calling every accepted remote object durable evidence by implication.

## Follow-on

Still open as later work:

- whether accepted case-object proof should later gain remote-locator continuity requirements
- whether the future richer typed family should define a canonical accepted-case-object schema instead of reusing generic supplementary evidence digests
- and whether some product shapes should suppress accepted external case-object anchors entirely in favor of passive artifact digests only
