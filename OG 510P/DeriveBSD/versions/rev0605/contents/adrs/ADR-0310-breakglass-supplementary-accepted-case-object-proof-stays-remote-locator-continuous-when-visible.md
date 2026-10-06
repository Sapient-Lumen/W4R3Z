# ADR-0310: Breakglass supplementary accepted case-object proof stays remote-locator-continuous when visible

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
`ADR-0308` then fixed that the same accepted-case-object lane must stay remote-protection-shaped when the adapter can see a protection / retention / hold posture for that exact accepted object.
`ADR-0309` then fixed that the same visible protection posture must stay exact to the same accepted object revision/version rather than collapsing into ambient case/container/bucket policy.

That still leaves one small but expensive ambiguity:

**if the adapter can already name the exact accepted object, its visible validator, and an object-exact visible protection posture, can later retrieval/discovery still collapse back into a parent case URL, container browse page, or manual portal clicking rather than one locator for the same accepted object revision/version?**

If the archive leaves this fuzzy, implementations will drift toward another weak shortcut:

1. a portable story names the exact accepted object and its visible validator,
2. and it may even preserve visible protection posture for that same accepted object revision/version,
3. but later review still has to navigate a parent case page, a container listing, or ticket prose to rediscover where that exact accepted object revision/version lives,
4. so the portable story remains partly dependent on portal archaeology instead of a typed locator for the same accepted object.

That is another softer form of evidence folklore.
A parent case or browse URL can be useful context, but it is not the same truth as “this exact accepted object revision/version is discoverable here.”

## Decision

1. When portable supplementary breakglass adapter/runtime evidence uses **accepted case-object proof** as its payload anchor, and the export/support adapter can see a redacted/non-secret passive locator for that same accepted remote attachment/object/message-part revision/version, the payload anchor must stay **remote-locator-continuous when visible**.

2. “Remote-locator-continuous when visible” means:
   - the accepted remote attachment/object/message-part identity from `ADR-0306` still stays exact,
   - the visible validator/revision token from `ADR-0307` still stays pinned when visible,
   - the visible protection / retention / hold posture from `ADR-0308` + `ADR-0309` still stays exact to the same accepted object revision/version when visible,
   - and any carried locator must describe that same accepted object revision/version rather than only a parent case, thread, container, bucket, or browse page.

3. Parent case/ticket/thread/container browse URLs may still travel as context, but they do **not** satisfy the remote-locator-continuous rule by themselves when the adapter can see a stronger object-exact locator.

4. This rule is conditional on visibility and safety.
   If the adapter can only see a parent/container locator, or the only visible locator is secret-bearing / live-control shaped, the archive does not invent a fake exact locator and it does not relax `ADR-0304`.
   In that case `ADR-0306` + `ADR-0307` + `ADR-0308` + `ADR-0309` still hold, and the locator remains omitted or contextual rather than promoted into portable truth.

5. This decision still does **not** mint a dedicated typed family for richer breakglass adapter/runtime material, and it still does **not** import metadata-only reverification into this supplementary lane yet.
   It closes only the next narrow leak worth fixing now: when a safe object-exact locator is visible for the same accepted object revision/version, keep that locator aligned too instead of sending later review back to portal browsing folklore.

## Consequences

Good:

- later review can now distinguish “the exact accepted object revision exists somewhere under this case/container” from “here is the same accepted object locator again”
- detached support and regulatory review no longer have to rely on case-page clicking when the adapter could already preserve a redacted/non-secret object locator
- future metadata-only reverification work can start from a cleaner floor instead of first undoing locator folklore

Costs:

- support/export tooling must preserve the strongest honest redacted/non-secret locator it can actually bind to the same accepted object revision/version
- some portal workflows that only preserve a parent browse URL will now be recognized as contextual but weaker portable evidence
- and metadata-only reverification still remains future work rather than something this cut settles now

## Why this is the right narrow cut

HTTP already treats the target URI as the resource identifier, and object stores commonly make version-specific retrieval / metadata lookup explicit on that same object locator rather than requiring container browsing. Amazon S3's `GetObject` documents `versionId` as the selector for a specific object version, and Azure Blob Storage's `Get Blob Properties` uses a `HEAD` request and supports a `versionid` URI parameter for a specific blob version. DeriveBSD does not copy any one provider API, but it should keep the same boring lesson here: **if accepted case-object proof is going to stand in for payload identity and the adapter can also see a safe object-exact locator for that same accepted object revision/version, keep that locator aligned too instead of collapsing later review back into parent-page folklore.**

## Follow-on

Still open as later work:

- whether accepted-case-object payload anchors should later gain metadata-only reverification on `transport.reverification.receipt`
- whether some product shapes should eventually forbid parent/container browse URLs entirely as carried context when an object-exact locator is visible
- and whether a future richer typed family should define a canonical accepted-case-object locator shape instead of reusing generic supplementary evidence joins
