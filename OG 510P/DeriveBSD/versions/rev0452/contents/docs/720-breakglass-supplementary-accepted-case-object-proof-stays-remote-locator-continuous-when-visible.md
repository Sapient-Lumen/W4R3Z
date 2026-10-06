# Breakglass supplementary accepted case-object proof stays remote-locator-continuous when visible

**Tier:** B (Cross-cutting breakglass/export boundary)  
**Profiles:** A, B, C, D  
**Pillars:** operability, isolation, supply-chain  
**Patterns:** Bundles, Broker→Lease→Receipt, Adapter→Shadow→Replace

`docs/711` fixed official support handoff to stay authority-first on exact `breakglass.receipt` digests.
`docs/712` then fixed that supplementary breakglass adapter/runtime material stays receipt-first on typed redaction/export/transport proof when it travels.
`docs/713` then fixed that the same portable story still needs the exact `breakglass.receipt` digest.
`docs/714` then fixed that portable supplementary evidence stays artifactized and off live control locators.
`docs/715` then fixed that portable supplementary evidence must stay payload-anchored to at least one passive artifact digest or accepted case-object proof.
`docs/716` then fixed that accepted case-object proof must stay object-exact on the accepted remote attachment/object/message-part.
`docs/717` then fixed that the same accepted-case-object lane must stay validator-pinned when the adapter can see a stronger revision/version/generation/ETag-like validator for that exact accepted object.
`docs/718` then fixed that the same accepted-case-object lane must stay remote-protection-shaped when the adapter can see a protection / retention / hold posture for that exact accepted object.
`docs/719` then fixed that the same visible protection posture must stay exact to the same accepted object revision/version rather than collapsing into ambient case/container/bucket policy.

That still leaves one small but expensive seam:
**if the portable story already names the exact accepted object, its visible validator, and an object-exact visible protection posture, can later discovery still collapse back into a parent case page, container browse URL, or manual portal clicking instead of one locator for the same accepted object revision/version?**

## Accepted boundary

Keep visible accepted-case-object locators **remote-locator-continuous when visible**.

If richer supplementary breakglass adapter/runtime material travels portably and the payload anchor uses accepted case-object proof, keep the exact accepted remote attachment/object/message-part identity from `docs/716`.
Then, when the adapter can also see a revision/version/generation/ETag-like validator for that exact accepted object, keep it pinned as `docs/717` already requires.
And when the adapter can also see a protection / retention / hold posture, keep that posture exact to the same accepted object revision/version as `docs/719` already requires.
Finally, when the adapter can also see a **redacted/non-secret passive locator** for that same accepted object revision/version, keep that locator aligned too instead of satisfying later discoverability with only a parent case/thread/container browse page.

The portable story should still read like:

- exact `breakglass.receipt` digests for typed emergency authority proof,
- typed `redaction.receipt` / `export.receipt` / `transport.receipt` handling proof,
- an object-exact accepted case-object proof when that lane stands in for payload identity,
- the strongest visible remote validator for that exact accepted object when the adapter can actually see one,
- the strongest visible remote protection posture for that same accepted object revision/version when the adapter can actually see one,
- and the strongest honest redacted/non-secret locator for that same accepted object revision/version when the adapter can actually see one.

## What this means in practice

### Parent browse pages are context, not object-exact locator proof

A case homepage, thread URL, container browse page, or bucket listing can still be useful context.
But if the adapter can see a stronger locator for the exact accepted object revision/version, that is the locator the portable story should carry.
Do not let parent/container browsing context masquerade as object-exact locator proof.

### Live control locators are still forbidden

This cut does not weaken `docs/714`.
Console URLs, copied `ConsoleEntryCommand` values, `WebSocketEndpoint` strings, virtual-media image locators, and session ids/tokens are still off the portable archive surface.
The new locator continuity rule is only about safe recipient-side discovery for the **accepted passive object**, not about reviving live control entry hints.

### Keep the strongest honest object-version locator, not a fake one

This rule is conditional on visibility and safety.
If the adapter can honestly bind a redacted/non-secret `ticket-attachment`, `portal-object`, `message-part`, `object-path`, `opaque`, or other reviewed passive locator to the same accepted object revision/version, preserve it.
If the adapter can only see a parent case/container browse locator or a secret-bearing/live-control locator, do not promote that into fake object-exact truth.
In that case the archive keeps `docs/716` + `docs/717` + `docs/718` + `docs/719` and carries the broader locator only as context or omits it.

### This still stops short of metadata-only reverification

This cut does **not** require the next `transport.reverification.receipt` follow-up lane for breakglass supplementary evidence yet.
It only fixes the smaller next floor worth locking now:
visible safe object-exact locators should stay aligned to the same accepted object revision/version instead of collapsing later review back into parent-page folklore.

## Why this is the right narrow cut

The same object-vs-container lesson already exists in current storage protocols.
RFC 9110 treats the target URI as the identifier for the target resource and HEAD as a no-body metadata path for that same resource.
Amazon S3 `GetObject` documents `versionId` as the selector for a specific object version rather than “whatever is current under this key.”
Azure `Get Blob Properties` likewise uses `HEAD` and supports a `versionid` URI parameter for a specific blob version.
DeriveBSD does not copy any one provider API, but it should keep the same boring truth surface here:
**if accepted case-object proof is going to stand in for payload identity and the adapter can see a safe object-exact locator for that same accepted object revision/version, keep that locator too instead of sending later review back to parent-case folklore.**

## First spec cut

The implementation cut is intentionally small:

- tighten `incident.bundle.includes.extra[]` and nearby bundle/breakglass docs so accepted case-object proof keeps visible remote locator continuity when the adapter can honestly see a safe locator for the same accepted object revision/version
- refresh the example bundle so the richer breakglass side-evidence trail shows an object-exact accepted-case-object proof placeholder that stays validator-pinned, remote-protection exact to the same object revision, and remote-locator-continuous too
- add a guardrail that fails if the archive stops saying visible safe object-exact locators must stay aligned instead of being replaced by parent case/container browse URLs or portal clicking folklore

## What this does *not* decide

This cut does **not** decide:

- the future typed family for richer breakglass adapter-side evidence
- the exact typed schema for accepted case-object locator proof in that future family
- whether breakglass supplementary evidence should later require metadata-only reverification too
- or which support portals/case systems are approved to host accepted external case objects

It decides only the smaller boundary worth locking now:
**when accepted case-object proof is already object-exact and validator-pinned and the adapter can see a safe recipient-side locator for the same accepted object revision/version, keep that locator aligned too instead of letting discoverability regress into parent-page portal folklore.**

## Related docs

- ADR: `adrs/ADR-0310-breakglass-supplementary-accepted-case-object-proof-stays-remote-locator-continuous-when-visible.md`
- accepted-case-object exactness floor: `docs/716-breakglass-supplementary-accepted-case-object-proof-stays-object-exact-when-portably-carried.md`
- accepted-case-object validator continuity floor: `docs/717-breakglass-supplementary-accepted-case-object-proof-stays-validator-pinned-when-visible.md`
- accepted-case-object visible protection floor: `docs/718-breakglass-supplementary-accepted-case-object-proof-stays-remote-protection-shaped-when-visible.md`
- accepted-case-object visible protection exactness floor: `docs/719-breakglass-supplementary-accepted-case-object-proof-keeps-visible-remote-protection-exact-to-the-same-object-revision.md`
- packet-capture remote-locator inspiration: `docs/524-packet-capture-strong-export-remote-locator-continuity-boundary.md`
- live-locator firewall: `docs/714-breakglass-supplementary-adapter-side-evidence-stays-artifactized-and-off-live-control-locators.md`
- incident bundles: `docs/216-incident-snapshots-and-support-bundles.md`
- support bundle contract: `docs/481-support-bundle-contract-and-timeline-first-handoff.md`
- breakglass workflows: `docs/250-breakglass-and-recovery-workflows.md`
- guardrail: `tools/check_breakglass_adapter_case_object_remote_locator_boundary.py`

## References

- RFC 9110: HTTP Semantics (target URI identifies the target resource; HEAD returns no response content): https://www.rfc-editor.org/rfc/rfc9110
- Amazon S3 `GetObject` (use `versionId` to reference a specific object version): https://docs.aws.amazon.com/AmazonS3/latest/API/API_GetObject.html
- Azure `Get Blob Properties` (HEAD request and `versionid` parameter for a specific blob version): https://learn.microsoft.com/en-us/rest/api/storageservices/get-blob-properties

Last updated: 2026-03-23r451
