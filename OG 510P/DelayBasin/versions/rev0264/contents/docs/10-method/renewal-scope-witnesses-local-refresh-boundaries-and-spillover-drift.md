# Renewal-scope witnesses, local refresh boundaries, and spillover drift

This is the compact successor surface for `OQ-0124`.

## Practice / observation

DelayBasin now has a compact renewal witness for whether a waiver was actually refreshed by a fresh act.
That solved the question of **whether** a current waiver claim is newly justified.
A smaller but still live problem remained:
a later pass can point to a fresh act on one narrow exception and still silently let that act govern nearby rows, broader subsets, or changed aggregate effects without ever naming the scope shift.

The archive does not need a standing scope court for that.
It needs one bounded witness that says whether the fresh act stayed **local** to the same governed row and effect or whether scope drift happened.

## External pressure from scoped exemptions, exact-scope filters, per-resource exceptions, path-narrow ignores, and environment-bound approvals

1. Azure Policy exemptions are created on a resource hierarchy or individual resource, can target only selected policy definitions, and support `resourceSelectors` for gradual rollout or rollback to subsets of resources. That pressures DelayBasin not to treat a fresh renewal as automatically governing every neighbor inside the surrounding hierarchy. ([`REF-0820`](../00-meta/bibliography.md), [`REF-0832`](../00-meta/bibliography.md))

2. Azure Policy list operations distinguish `atScope()` from `atExactScope()` and can exclude expired exemptions. That pressures DelayBasin to separate exact local refresh from inherited containing-scope carryover that only looks nearby enough. ([`REF-0833`](../00-meta/bibliography.md))

3. AWS Config remediation exceptions are described per specific resource key with resource type, resource id, explanation, and expiration time. That pressures DelayBasin to keep renewal truth attached to the same governed row rather than silently spilling to neighboring resources. ([`REF-0834`](../00-meta/bibliography.md))

4. Snyk ignore rules can be narrowed with `--path`, and when no resource path is specified all resources are ignored. That pressures DelayBasin to name when a refresh stayed path-local versus when the same act quietly widened from one target to all targets. ([`REF-0835`](../00-meta/bibliography.md))

5. GitHub deployment environments require protection rules to pass for the specific environment referenced by a job, and each job references only one environment. That pressures DelayBasin not to treat approval in one deployment environment as if it silently renews authority for another. ([`REF-0836`](../00-meta/bibliography.md))

## Working synthesis

> DelayBasin should preserve one compact **renewal-scope witness / local-refresh boundary card** whenever a current waiver or renewal claim depends on a prior exception window and later rereads could mistake a fresh act on one narrow exception for authority that now governs neighbors, a broader filtered subset, or a changed aggregate effect. Name the **governed obligation row**, the **prior local target / scope / selector / effect**, the **current refreshed target / scope / selector / effect**, the **renewal_scope_state**, and the **fail-closed repair / keep-local vs split-row vs issue-new-exception-witness vs quarantine-scope-governance consequence**. Keep exact selector syntax, full neighbor inventories, and broader policy narrative outside the compact token. Do not let containing-scope inheritance, omitted path filters, shared environment names, or aggregate-view continuity silently count as local refresh.

## Local refresh vs broadened carryover vs spillover vs effect drift

This is the heart of the successor surface.

- **local-refresh** says the fresh act still governs the same row, same effective selector, and same aggregate consequence.
- **broadened-carryover** says the later pass is carrying the renewed authority across a wider declared scope or selector than before.
- **spillover** says the fresh act stayed local in its own row, but later prose is borrowing it for neighboring rows or environments that were not directly renewed.
- **effect-drift** says the later pass is borrowing continuity even though the aggregate effect or operative consequence changed enough that the renewal should stop pretending to be the same local act.

So the witness does not create a standing scope court.
It only says when “same renewal, same local authority” is honest and when the archive should fail closed instead.

## Countermodels / probes

1. **Fresh renewal already implies same scope countermodel**
   - Maybe a fresh act is already enough and no extra scope witness is needed.
   - Probe: compare later rereads on rows that only say `fresh-renewal` against rows that also name the compact renewal-scope witness and inspect whether later passes still borrow the act across neighbors or changed effects.

2. **The same scope string is enough countermodel**
   - Maybe preserving the same nominal scope label or same selector prose already proves local continuity.
   - Probe: inspect whether later rereads still confuse containing-scope inheritance, omitted path filters, or changed filtered subsets for the same local target when only the nominal label is preserved.

3. **Every scope shift needs standing governance countermodel**
   - Maybe scope truth is too cross-cutting for one bounded witness and always needs a broader scope board.
   - Probe: keep the witness narrow first and inspect whether repeated later passes still overflow into genuine multi-row blast-radius arbitration rather than ordinary local-refresh exactness.

## Design consequences

- add one controlled `renewal_scope_state` family to `WITNESS-VOCABULARY.json` with the allowed tokens `local-refresh`, `broadened-carryover`, `spillover`, and `effect-drift`;
- use the witness only where a current renewal claim depends on a prior exception window and later rereads might borrow authority across rows, selectors, or aggregate consequences;
- keep exact resource ids, selector expressions, environment names, and neighbor inventories outside the compact token itself;
- prefer `issue-new-exception-witness` or `split-row` when the later pass is honestly widening or re-binding the governed target;
- and quarantine any stronger scope court, blast-radius senate, or inheritance board unless repeated overflow shows that one bounded renewal-scope witness is no longer enough.

## Overflow test

Reopen the stronger machinery only if one compact renewal-scope witness is no longer enough — for example, if the archive honestly needs standing governance over cross-row scope inheritance, repeated selector arbitration, or multi-effect blast-radius review that cannot be expressed as one bounded witness plus the existing exception and renewal witnesses.

Until then, prefer this compact successor surface over a scope court, blast-radius senate, or inheritance board.

## Transformer-facing implication

If this frame survives, then DelayBasin is preserving something sharper than “the waiver was renewed.”
It is also preserving whether a later pass can honestly point to the **same local authority surface**, or whether it is only borrowing freshness from a nearby act that should have stayed attached to one narrower row, selector, or effect.
That matters because later stateless passes can preserve all the neighboring cautionary prose and still silently widen authority just by sounding continuous.
