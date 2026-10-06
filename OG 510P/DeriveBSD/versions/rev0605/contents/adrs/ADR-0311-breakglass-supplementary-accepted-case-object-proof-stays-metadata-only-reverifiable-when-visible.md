# ADR-0311: Breakglass supplementary accepted case-object proof stays metadata-only reverifiable when visible

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
`ADR-0310` then fixed that, when the adapter can also see a safe redacted/non-secret passive locator for that same accepted object revision/version, the portable story must keep that object-exact locator aligned too rather than sending later review back to parent-page folklore.

That still leaves one small but expensive ambiguity:

**if the portable story already names the exact accepted object, its visible validator, any object-exact visible protection posture, and a safe object-exact locator, can later follow-up still collapse back into screenshots, portal clicking, or another body download instead of one typed metadata-only re-check of the same accepted object revision/version?**

If the archive leaves this fuzzy, implementations will drift toward another weak shortcut:

1. the portable story already preserves the exact accepted object identity,
2. it may even preserve the same visible validator / protection posture / locator for that exact accepted object revision/version,
3. but later support, audit, or regulatory work still proves continuity by downloading the body again or by screenshotting a portal,
4. so the archive loses the chance to treat the same accepted object as a typed metadata-only reverification lane.

That is another avoidable form of evidence folklore.
We already know enough to stop it without inventing a richer breakglass artifact family.

## Decision

1. When portable supplementary breakglass adapter/runtime evidence uses **accepted case-object proof** as its payload anchor, and the export/support adapter can later metadata-check that same accepted remote attachment/object/message-part revision/version without re-downloading the body, the canonical follow-up evidence object is now:
   - `transport.reverification.receipt`

2. This new breakglass accepted-case-object reverification lane stays **metadata-only reverification when visible**:
   - `reverification.body_downloaded = false`
   - the same accepted remote attachment/object/message-part identity from `ADR-0306` still stays exact,
   - the visible validator from `ADR-0307` still stays pinned when visible,
   - the visible protection / retention / hold posture from `ADR-0308` + `ADR-0309` still stays exact to the same accepted object revision/version when visible,
   - and the safe object-exact locator from `ADR-0310` still stays aligned when visible.

3. This is **follow-on evidence**, not a new export-completion requirement.
   The supplementary breakglass story still completes at the existing authority-first + receipt-first + payload-anchored handoff floor.
   But when later work wants to claim “the same accepted remote object still stands as the portable payload anchor,” the archive now expects a typed `transport.reverification.receipt` instead of screenshots, clicking, or another artifact/body download.

4. This rule is conditional on visibility and adapter honesty.
   If the adapter cannot metadata-check the same accepted object revision/version without body download, the archive does **not** invent a fake reverification receipt and it does **not** promote screenshots into equivalent proof.
   In that case the earlier `ADR-0306` .. `ADR-0310` floor still holds and reverification remains omitted.

5. This decision still does **not** mint a dedicated typed family for richer breakglass adapter/runtime material.
   It only fixes the next narrow follow-up boundary worth standardizing now: once accepted-case-object proof is already object-exact, validator-pinned when visible, protection-exact when visible, and locator-continuous when visible, later re-checks should use typed metadata-only reverification instead of portal folklore.

## Consequences

Good:

- later support/audit/regulatory follow-up can now prove continuity of the same accepted object revision/version without another artifact/body download
- detached review no longer has to trust screenshots or remembered portal navigation when the adapter can honestly re-check the same accepted object metadata
- this reuses an existing generic receipt shape instead of inventing a new breakglass-only evidence type

Costs:

- support/export adapters that can honestly metadata-check the same accepted object revision/version now need to emit `transport.reverification.receipt` instead of relying on ticket notes or screenshots
- some integrations will still only be able to preserve the `ADR-0306` .. `ADR-0310` floor and omit reverification because their portals lack a safe metadata lane
- this adds one more proof-chain object for stronger portable side-evidence stories

## Why this is the right narrow cut

HTTP already distinguishes metadata-first checks from body transfer: RFC 9110 defines HEAD as the method for transferring representation metadata without response content. Amazon S3 `HeadObject` likewise retrieves metadata from an object without returning the object itself, and object-version metadata lookup remains explicit through `versionId`. Azure `Get Blob Properties` similarly returns properties/metadata without blob content for a specific blob or version. DeriveBSD does not copy any one provider API, but it should steal the same boring lesson here: **if accepted case-object proof is already standing in for payload identity and the adapter can later re-check that same accepted object revision/version using metadata only, keep the follow-up proof on typed `transport.reverification.receipt` instead of another body download or portal screenshot ritual.**

## Follow-on

Still open as later work:

- whether some profiles should later require periodic accepted-case-object reverification rather than leaving it as optional follow-on evidence
- whether the accepted-case-object lane should later require a fresh remote digest when the adapter can obtain one metadata-first
- and whether a future richer typed family should eventually define a canonical breakglass supplementary-side-evidence profile for `transport.reverification.receipt`
