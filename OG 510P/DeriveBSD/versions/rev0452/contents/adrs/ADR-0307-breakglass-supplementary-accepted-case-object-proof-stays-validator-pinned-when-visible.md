# ADR-0307: Breakglass supplementary accepted case-object proof stays validator-pinned when visible

- Status: Accepted
- Date: 2026-03-23

## Context

`ADR-0301` fixed official support handoff to stay authority-first on exact `breakglass.receipt` digests.
`ADR-0302` then fixed supplementary breakglass adapter/runtime exports to stay receipt-first on typed redaction/export/transport proof.
`ADR-0303` then fixed that those supplementary receipt chains still need the exact `breakglass.receipt` digest in the same portable story.
`ADR-0304` then fixed that the portable story must stay artifactized and off live control locators.
`ADR-0305` then fixed that portable supplementary evidence must stay payload-anchored to at least one passive artifact digest or accepted case-object proof.
`ADR-0306` then fixed that the accepted-case-object lane must stay object-exact on the accepted remote attachment/object/message-part.

That still leaves one small but expensive ambiguity:

**if accepted case-object proof is object-exact already, can it still drift across mutable remote revisions when the adapter can see a stronger revision / version / generation / ETag-like validator?**

If the archive leaves this fuzzy, implementations will drift toward another weak shortcut:

1. a bundle carries typed handling receipts plus accepted case-object proof for the right remote object,
2. but the remote object is mutable and the proof drops the revision/version validator the adapter could already see,
3. later review can tell which remote object family was involved,
4. but still cannot tell whether the proof refers to the same accepted representation/version that actually traveled.

That is the same coherence leak DeriveBSD already closed for stronger packet-capture export with `remote_validator` continuity.
This breakglass lane is smaller, but the same minimum lesson applies.

## Decision

1. When portable supplementary breakglass adapter/runtime evidence uses **accepted case-object proof** as its payload anchor, and the export/support adapter can see a remote revision / version / generation / ETag-like validator for that exact accepted object, the proof must stay **validator-pinned**.

2. “Validator-pinned” means the portable story preserves the strongest remote validator token the adapter can actually see for that exact accepted remote attachment/object/message-part.
   Typical examples include a strong `ETag`, attachment revision id, generation token, or another opaque remote version handle.

3. This rule is conditional on visibility.
   If the adapter cannot surface any such validator, `ADR-0306`'s object-exact floor still applies and the archive does not invent a fake revision token.

4. Parent case/ticket/thread/container ids remain context only, and the accepted object id still remains mandatory.
   Validator continuity is an additional strengthening rule on top of object-exactness when the adapter can actually see it.

5. This decision still does **not** mint a dedicated typed family for richer breakglass adapter/runtime material, and it still does **not** import the entire stronger packet-capture continuity stack (`remote_protection`, `remote_locator`, metadata-only reverification) into this supplementary lane yet.
   It closes only the next narrow leak worth fixing now: if the accepted-case-object lane can see a revision/version validator, keep it pinned.

## Consequences

Good:

- accepted case-object proof no longer silently degrades from “exact object” back into “whatever revision of that object the portal shows now”
- support/export adapters gain one portable rule for mutable remote objects without needing a whole new artifact family first
- future typed-family work can inherit a cleaner floor instead of first undoing object-latest folklore

Costs:

- support/export tooling that can see revision/version validators must preserve them when it uses accepted case-object proof as the payload anchor
- some existing portal workflows that only preserve the object id but discard the visible validator will now be recognized as incomplete stronger portable evidence
- and remote protection / locator continuity still remain future work rather than something this cut settles now

## Why this is the right narrow cut

HTTP already treats validators as the way to distinguish representations of the same resource, and RFC 9110 says entity tags can be strong or weak validators while `If-Match` uses strong comparison to prevent lost updates. RFC 7232 likewise explains that a strong validator changes whenever representation data that would be observable in a 200 response changes. DeriveBSD already imported the same lesson for stronger packet-capture export by keeping one stable `remote_validator` through transport, recipient acceptance, and final export evidence. This breakglass cut deliberately stops earlier than that stronger lane, but it keeps the same minimum discipline for accepted external objects: exact object when that is all the adapter can see, and exact object plus the visible validator when the adapter can see more.

## Follow-on

Still open as later work:

- whether accepted case-object proof should later gain remote-protection / remote-locator continuity requirements
- whether the future richer typed family should define a canonical accepted-case-object schema instead of reusing generic supplementary evidence digests
- and whether some product shapes should suppress accepted external case-object anchors entirely in favor of passive artifact digests only
