# Harbor

[SlopOS](../README.md) · [Complete editions](../DOWNLOADS.md#harbor)

Harbor makes crossings legible. Opening a browser, returning from an external service, importing another project’s evidence, or responding to a warning all move something across a boundary. Harbor asks what crossed, by which route, under what scope, and what remains to happen afterward. Its contribution to the SlopOS family is a language for passage that preserves the difference between arrival and adoption.

## Out through the browser, back with evidence

An early specimen begins with a familiar detour: an application sends someone to a browser and expects a callback. Harbor divides the journey into a request envelope, possible routes, an admission choice, a time-bounded detour lease, callback evidence, and an aftermath receipt. The envelope identifies who asked, the requested return capability, and cancellation or timeout. The lease states what kind of proof a return should carry. A callback may never arrive, arrive without binding to the request, or return with bindable proof and a provider payload. Those are different stories, even when the browser window has closed. [Browser-detour specimen, rev0020](../sources/Harbor/rev0020/docs/30-architecture/specimen-flow-01-browser-detour-callback-proof.md).

This division is practical. It leaves room to explain “the route was admitted, but nothing returned” or “a response arrived, but local adoption has not happened” instead of squeezing both into a misleading success indicator. Harbor’s harbor is therefore not just an entrance. It includes the quay where an arrival is inspected and the receipt that remembers what followed.

## What a click actually says

By rev0111, the boundary also runs between an interface event and the meaning assigned to it. The response-event specimen starts after an explanation card for a revocation overlay has appeared. A person might inspect evidence, request a recheck, dismiss the card, copy a link, begin an appeal, or acknowledge receipt. Harbor preserves the event and its parent explanation while keeping the proposed follow-up separate from its outcome. Dismissal does not accept the warning; a copied link does not show that recipients read it; requesting a recheck does not mean it passed. [Response-event specimen](../sources/Harbor/rev0111/docs/30-architecture/specimen-flow-106-user-response-reliance-event-capture.md).

The resulting record includes the event’s kind, clock, surface, minimal actor reference, scope, interpretation limits, retention posture, and history. This is also a privacy choice: an explanation need not become an excuse to build an identity-rich analytics system. The authored harness uses bounded retention and pseudonymous actor references in accepted cases, and makes unbounded retention and direct-person analytics explicit refusal examples. Its 34 planned cases comprise 14 acceptances and 20 refusals. [Response-event harness](../sources/Harbor/rev0111/tools/harbor_user_response_event_harness.py).

There is substantive code behind this design. Shared helpers hash canonical JSON and file bytes with SHA-256. [Bundle helpers](../sources/Harbor/rev0111/tools/harbor_bundle_common.py). The checker verifies row and bundle digests, parent and helper bindings, fixed case order, guard values, and case-specific assertions. But the generator and checker share an authored case plan; the generated verdict starts from that plan’s expected outcome. This is a deterministic fixture and consistency-checking system, not an independent observer of browser behavior or a general classifier of consent. No real click, comprehension, or local account adoption is established by these examples. [Response-event checker](../sources/Harbor/rev0111/tools/check_harbor_user_response_event_bundle.py).

## Evidence from neighbors

Harbor’s cross-cube specimen gives the family resemblance a concrete shape. It imagines importing SlopOS append history, Foundry classification pins, Steward retry attempts, Schell retention context, ViewFS volition cards, Ward delegation warrants, and Helm repair traces. Each fragment enters with its material identity and parent context, receives an explicit scope translation, and awaits local rechecking. An imported repair trace remains evidence of an attempt, not a completed repair. Conflicting fragments may remain incomparable instead of being forced into a majority verdict. [Cross-cube lineage specimen](../sources/Harbor/rev0111/docs/30-architecture/specimen-flow-102-cross-cube-lineage-import-without-inherited-status.md).

That sequence distinguishes Harbor from a universal trust broker. Its subject is how evidence enters and what the recipient may responsibly make of it. Ward’s appraisal, Steward’s lifecycle decisions, and SlopOS’s native authority do not cross the boundary merely because their names appear on a packet.

The artistic strength is the attention to aftermath. Harbor gives software a way to remember an unfinished journey without disguising it as failure or polishing it into success. Its authored scenes and executable checks make that ethic concrete enough for later implementations to answer to.
