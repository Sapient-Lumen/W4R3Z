# ADR-0309: Breakglass supplementary accepted case-object proof keeps visible remote protection exact to the same object revision

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

That still leaves one small but expensive ambiguity:

**if the adapter can see a protection / retention / hold posture, does it have to be exact for the same accepted object revision/version, or can an ambient case/container/bucket policy stand in for it?**

If the archive leaves this fuzzy, implementations will drift toward another weak shortcut:

1. a portable story names the exact accepted object and its visible validator,
2. but the carried protection posture is only a parent ticket SLA, container-wide hold, or bucket default,
3. later review can tell that some surrounding store had a retention policy,
4. but still cannot tell whether the exact accepted object revision/version that acted as the payload anchor was the thing actually protected.

That is another softer form of evidence folklore.
A surrounding policy can be useful context, but it is not the same truth as “this exact accepted object revision/version had this overwrite/delete-resistance posture.”

## Decision

1. When portable supplementary breakglass adapter/runtime evidence uses **accepted case-object proof** as its payload anchor, and the export/support adapter can see a remote protection / retention / hold posture, that posture must stay **exact to the same accepted object revision/version**.

2. “Exact to the same accepted object revision/version” means:
   - the accepted remote attachment/object/message-part identity from `ADR-0306` still stays exact,
   - the visible validator/revision token from `ADR-0307` still stays pinned when visible,
   - and any carried protection / retention / hold posture from `ADR-0308` must describe that same accepted object revision/version rather than only a parent case, thread, container, bucket, or ambient store default.

3. Ambient case/thread/container/bucket policy may still travel as context, but it does **not** satisfy the remote-protection-shaped rule by itself when the adapter can see a stronger object-exact posture.

4. This rule is conditional on visibility.
   If the adapter can only see an ambient policy and cannot honestly relate that policy to the accepted object revision/version, the archive does not invent a fake exact posture. In that case `ADR-0306` + `ADR-0307` still hold, and `ADR-0308` is satisfied only by the strongest posture the adapter can honestly bind to the exact accepted object.

5. This decision still does **not** mint a dedicated typed family for richer breakglass adapter/runtime material, and it still does **not** import remote-locator continuity or metadata-only reverification into this supplementary lane yet.
   It closes only the next narrow leak worth fixing now: visible protection posture must stay exact to the same accepted object revision/version instead of collapsing into ambient storage policy.

## Consequences

Good:

- the accepted-case-object lane can now distinguish “this exact accepted object revision was under hold/retention” from “something around it had a policy”
- detached review no longer has to guess whether a container-level or bucket-level rule actually covered the accepted payload anchor revision
- future richer typed-family work can start from a cleaner floor instead of first undoing ambient-policy folklore

Costs:

- support/export tooling must preserve the strongest object-exact protection posture it can honestly bind to the accepted object revision/version
- some portal workflows that only preserve a case-level or bucket-level retention setting will now be recognized as contextual but incomplete stronger portable evidence
- and remote-locator continuity / metadata-only reverification still remain future work rather than something this cut settles now

## Why this is the right narrow cut

Mainstream stores already separate object/version-exact protection from surrounding defaults. Amazon S3 Object Lock says legal holds apply to individual object versions, that lock information is stored in the metadata for that object version, and explicit object-version settings override bucket property retention settings. Azure documents a similar distinction: version-level legal holds can be configured on an individual blob version, while container-level legal holds apply to all blobs in the container and policy precedence is Blob -> Container -> Account. Google Cloud Storage likewise distinguishes Object Retention Lock, which defines retention on a per-object basis, from Bucket Lock, which defines retention uniformly for all objects in the bucket. DeriveBSD should keep the same boring truth surface here: **if the accepted-case-object lane carries visible overwrite/delete-resistance posture, it should stay exact to the same accepted object revision/version rather than treating ambient container or bucket policy as if it were object-exact evidence.**

## Follow-on

Still open as later work:

- whether accepted-case-object payload anchors should later gain remote-locator continuity
- whether metadata-only remote reverification should later become the next closure cut for this lane
- and whether some product shapes should eventually forbid ambient-policy-only posture entirely for portable accepted-case-object anchors
