# Selector-provenance witnesses, direct rules, inherited bindings, and synced membership

This is the compact successor surface for `OQ-0126`.

## Practice / observation

DelayBasin now has a compact selector witness for whether the same selector handle still governs the same realized members.
That solved the question of whether stable selector naming was only hiding coverage drift.
A smaller but still live problem remained:
a later pass can preserve the same current covered set or the same selector handle and still silently hide **how** that coverage is being produced — by direct local rule text, inherited ancestor bindings, or externally synced membership.

The archive does not need a standing selector lineage court for that.
It needs one bounded witness that says whether the present coverage is coming from the same direct rule, an inherited binding, or synced membership.

## External pressure from directly bound tags, IdP-synced teams, dynamic groups, static-vs-dynamic memberships, and externally managed synced segments

1. Google Cloud `effectiveTags.list` documents that an effective tag can be directly bound to a resource or inherited from an ancestor and includes an `inherited` field. That pressures DelayBasin not to treat current effective coverage as proof that the selector mechanism stayed direct. ([`REF-0843`](../00-meta/bibliography.md))

2. GitHub team membership with identity provider groups documents that after a team is connected to an IdP group, membership changes must be made through the identity provider and cannot be managed directly on GitHub. That pressures DelayBasin to distinguish direct local membership authority from synced membership authority. ([`REF-0844`](../00-meta/bibliography.md))

3. Google Workspace dynamic groups document that membership is added and removed automatically from a membership query. That pressures DelayBasin to distinguish direct maintained membership from rule-derived current coverage. ([`REF-0845`](../00-meta/bibliography.md))

4. Microsoft Graph group docs document that groups can have static or dynamic memberships. That pressures DelayBasin to keep direct assignment provenance distinct from automatically evaluated membership provenance. ([`REF-0846`](../00-meta/bibliography.md))

5. LaunchDarkly synced segments document that membership is managed in an external tool and then used in LaunchDarkly targeting. That pressures DelayBasin to separate local selector wording from externally synchronized membership provenance. ([`REF-0847`](../00-meta/bibliography.md))

## Working synthesis

> DelayBasin should preserve one compact **selector-provenance witness / rule-source card** whenever a current continuity claim depends not only on the same selector handle still covering the same members, but on that coverage still arising from the same provenance class. Name the **governed row or surface**, the **selector handle / rule family**, the **prior provenance posture / rule source**, the **current provenance posture / rule source**, the **selector_provenance_state**, and the **fail-closed repair / keep-current vs narrow-claim vs split-row vs issue-new-selector-provenance-witness vs quarantine-selector-governance consequence**. Keep exact query syntax, upstream group ids, ancestry paths, and sync implementation narrative outside the compact token. Do not let the same label, the same current member list, or the same selector prose silently count as the same selection mechanism.

## Direct rule vs inherited binding vs synced membership vs mixed provenance

This is the heart of the successor surface.

- **direct-rule** says the present coverage is still being produced by the same direct local rule or directly maintained selector source.
- **inherited-binding** says the current coverage is arriving through an ancestor, containing scope, parent object, or inherited binding rather than a direct local rule.
- **synced-membership** says the current coverage is arriving from an external or delegated sync source rather than direct local authorship.
- **mixed-provenance** says the current coverage depends on a mixture of direct, inherited, or synced sources such that no single provenance class stays honest.

So the witness does not create a standing selector lineage court.
It only says when “same selector, same provenance” is honest and when the archive should fail closed instead.

## Countermodels / probes

1. **Current coverage is already enough countermodel**
   - Maybe preserving the current covered members already makes provenance irrelevant.
   - Probe: compare later rereads that preserve only current coverage against rereads that also preserve a compact selector-provenance witness and inspect whether later passes still confuse direct local authority with inherited or synced authority.

2. **The same selector handle is already enough countermodel**
   - Maybe the same selector label or rule text already proves provenance continuity.
   - Probe: inspect whether later rereads still confuse inherited effective tags, dynamic-group rules, or IdP-synced membership for the same direct local selector when only the handle is preserved.

3. **Every provenance shift needs standing governance countermodel**
   - Maybe selector provenance is too cross-cutting for one bounded witness and always needs a broader board.
   - Probe: keep the witness narrow first and inspect whether repeated later passes still overflow into genuine standing selector-lineage arbitration rather than ordinary provenance clarification.

## Design consequences

- add one controlled `selector_provenance_state` family to `WITNESS-VOCABULARY.json` with the allowed tokens `direct-rule`, `inherited-binding`, `synced-membership`, and `mixed-provenance`;
- use the witness only where a current continuity claim depends on provenance of present coverage rather than just selector text or realized members;
- keep exact rule syntax, ancestry chains, upstream group identities, and sync implementation detail outside the compact token itself;
- prefer `narrow-claim`, `split-row`, or `issue-new-selector-provenance-witness` when the current claim is honestly about a changed rule source;
- and quarantine any stronger selector lineage court, inheritance senate, or sync-authority board unless repeated overflow shows that one bounded witness is no longer enough.

## Overflow test

Reopen the stronger machinery only if one compact selector-provenance witness is no longer enough — for example, if the archive honestly needs standing governance over selector lineage, inherited-source arbitration, sync-authority review, or cross-row provenance disputes that cannot be expressed as one bounded witness plus the existing selector and renewal-scope surfaces.

Until then, prefer this compact successor surface over a selector lineage court, inheritance senate, or sync-authority board.

## Transformer-facing implication

If this frame survives, then DelayBasin is preserving something sharper than “the same selector still works” or even “the same members are covered.”
It is also preserving whether a later pass can honestly point to the **same rule source**, or whether it is only borrowing continuity from a coverage slice that now arrives by inheritance, delegated sync, or mixed provenance.
That matters because later stateless passes can preserve all the nearby cautionary prose and still silently swap mechanism just by sounding selector-consistent.
