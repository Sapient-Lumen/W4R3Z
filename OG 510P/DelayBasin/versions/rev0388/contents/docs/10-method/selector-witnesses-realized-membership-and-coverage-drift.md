# Selector witnesses, realized membership, and coverage drift

This is the compact successor surface for `OQ-0125`.

## Practice / observation

DelayBasin now has a compact renewal-scope witness for whether a fresh act stayed local to the same row, selector, and effect.
That solved the question of whether a current renewal silently widened beyond its declared target.
A smaller but still live problem remained:
a later pass can point to the same selector handle, tag, segment name, or rule label and still silently let that unchanged label stand in for a changed realized member set.

The archive does not need a standing selector court for that.
It needs one bounded witness that says whether the same selector still picks the same governed members or whether coverage drift happened underneath the label.

## External pressure from mutable labels, automatic dynamic membership, evaluated subsets, inherited tags, query-based groups, and synced segments

1. Kubernetes labels can be attached at creation time and later added or modified at any time, and selectors choose subsets of objects by those labels. That pressures DelayBasin not to treat the same label text as proof that the realized covered set stayed the same. ([`REF-0837`](../00-meta/bibliography.md))

2. Microsoft Entra dynamic membership groups add and remove members automatically when attributes change, and the security of the group depends on who can modify the referenced attributes. That pressures DelayBasin to separate stable selector prose from actual covered members. ([`REF-0838`](../00-meta/bibliography.md))

3. Azure Policy resource selectors evaluate only the resources applicable to the selector specifications and are used to narrow rollout subsets. That pressures DelayBasin to keep a selector handle distinct from the current evaluated coverage slice. ([`REF-0839`](../00-meta/bibliography.md))

4. Google Cloud effective tags can be directly attached or inherited from ancestors, overridden on descendants, and changed again if overrides are removed. That pressures DelayBasin not to treat the same tag key/value label as proof that the same descendants still inherit the same operative coverage. ([`REF-0840`](../00-meta/bibliography.md))

5. AWS Resource Groups define a group as resources matching the group query, including resource-type and tag criteria. That pressures DelayBasin to keep the query handle distinct from the currently matched member set. ([`REF-0841`](../00-meta/bibliography.md))

6. LaunchDarkly rule-based, list-based, and synced segments let multiple flags reuse the same segment, and those flags automatically pick up later segment changes. That pressures DelayBasin to keep the reusable segment label distinct from the current realized targeted contexts. ([`REF-0842`](../00-meta/bibliography.md))

## Working synthesis

> DelayBasin should preserve one compact **selector witness / realized-coverage card** whenever a current continuity claim depends on the same selector handle, label, tag, segment, or rule name still governing the same members across time. Name the **governed row or surface**, the **selector handle / selector text family**, the **prior realized coverage slice**, the **current realized coverage slice**, the **selector_membership_state**, and the **fail-closed repair / keep-current vs narrow-claim vs split-row vs issue-new-selector-witness vs quarantine-selector-governance consequence**. Keep exact member inventories, full query syntax, and broader policy narrative outside the compact token. Do not let unchanged labels, inherited bindings, synced-segment names, or rule handles silently count as unchanged realized coverage.

## Stable coverage vs expanded coverage vs narrowed coverage vs recomposed coverage

This is the heart of the successor surface.

- **stable-coverage** says the same selector still governs the same effective member slice for the current comparison.
- **expanded-coverage** says the same selector handle now reaches additional governed members that were not in the prior realized slice.
- **narrowed-coverage** says the same selector handle now governs fewer members than before.
- **recomposed-coverage** says the same selector handle still looks continuous, but the realized covered members changed composition enough that neither simple expansion nor simple narrowing captures the drift.

So the witness does not create a standing selector court.
It only says when “same selector, same governed set” is honest and when the archive should fail closed instead.

## Countermodels / probes

1. **The same selector text is already enough countermodel**
   - Maybe preserving the selector label, tag, or segment name already proves continuity.
   - Probe: compare later rereads on rows that preserve only the selector handle against rows that also preserve the compact selector witness and inspect whether later passes still treat changed covered members as if they were the same governed set.

2. **Exact membership inventories are always required countermodel**
   - Maybe any compact witness is too lossy and the archive should always carry a full member list.
   - Probe: keep exact inventories outside the compact token first and inspect whether a small prior/current realized-slice witness is already enough to stop label-continuity mistakes on ordinary rereads.

3. **Every selector drift needs standing governance countermodel**
   - Maybe selector truth is too cross-cutting for one bounded witness and always needs a selector board.
   - Probe: keep the witness narrow first and inspect whether repeated later passes still overflow into genuine standing selector arbitration rather than ordinary coverage-drift clarification.

## Design consequences

- add one controlled `selector_membership_state` family to `WITNESS-VOCABULARY.json` with the allowed tokens `stable-coverage`, `expanded-coverage`, `narrowed-coverage`, and `recomposed-coverage`;
- use the witness only where a current continuity claim depends on the same selector handle still governing the same members across time;
- keep exact inventories, full selector expressions, sync-source details, and inherited-path narratives outside the compact token itself;
- prefer `narrow-claim`, `split-row`, or `issue-new-selector-witness` when the current claim is honestly about a changed covered set;
- and quarantine any stronger selector court, membership senate, or coverage-authority board unless repeated overflow shows that one bounded witness is no longer enough.

## Overflow test

Reopen the stronger machinery only if one compact selector witness is no longer enough — for example, if the archive honestly needs standing governance over inherited-versus-direct membership, repeated external-sync authority, or cross-row coverage arbitration that cannot be expressed as one bounded witness plus the existing renewal-scope and obligation surfaces.

Until then, prefer this compact successor surface over a selector court, membership senate, or coverage-authority board.

## Transformer-facing implication

If this frame survives, then DelayBasin is preserving something sharper than “the same tag still appears.”
It is also preserving whether a later pass can honestly point to the **same realized governed members**, or whether it is only borrowing continuity from a durable selector handle whose covered set changed underneath.
That matters because later stateless passes can preserve all the nearby cautionary prose and still silently widen, narrow, or remap authority just by sounding label-consistent.
