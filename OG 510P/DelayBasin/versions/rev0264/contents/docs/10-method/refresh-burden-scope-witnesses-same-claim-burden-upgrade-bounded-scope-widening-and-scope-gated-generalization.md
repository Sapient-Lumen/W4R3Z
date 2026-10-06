# Refresh-burden-scope witnesses, same-claim burden upgrade, bounded scope widening, and scope-gated generalization

This is the compact successor surface for `OQ-0143`.

## Practice / observation

Once DelayBasin can say **what changed**, **how sustained the return is**, **how broad the support looks**, **how independent that support really is**, and **whether the present support actually licenses a stronger public burden**, one more local failure mode remains.

A burden upgrade can still drift in scope.
Sometimes the archive really is saying something stronger about the same current claim.
The burden rises: more people should know, response expectations change, or the current row deserves stronger language.
But the governed claim itself has not widened.
Sometimes the stronger burden is paired with an explicit scope widening.
A previously local issue now honestly names more affected components, branches, paths, groups, projects, or service slices.
And sometimes the evidence only hints at a wider blast radius.
An upstream component is down, a neighboring project shares telemetry, or a ruleset applies to a broader family, but the archive still lacks the direct mapping that would make widened public scope honest.

The archive does not need a refresh-scope court for that.
It needs one bounded witness that says whether stronger burden still governs the same claim, honestly widens scope in a named way, or still needs another scope gate before public generalization is allowed.

## External pressure from Statuspage affected components and incident impact, Statuspage third-party overrides, Google Cloud resource-group alerting and metrics scopes, GitHub workflow/ruleset/code-owner targeting, and PagerDuty narrow-functional-scope guidance

1. Statuspage computes incident impact from the affected components of the incident, while top-level status is calculated from all components on the page. That pressures DelayBasin to distinguish a stronger burden on one affected slice from a claim that has widened to the whole page or service family. ([`REF-0932`](../00-meta/bibliography.md))

2. Statuspage incident creation explicitly asks you to specify which components are affected so incident updates, component states, and subscriber notifications stay in sync. That pressures DelayBasin to name scope widening directly instead of letting stronger urgency silently broaden the public claim. ([`REF-0933`](../00-meta/bibliography.md))

3. Statuspage also lets operators override a third-party component when an external incident does not affect their own service. That pressures DelayBasin not to let upstream trouble or adjacency alone widen the archive's current public claim. ([`REF-0934`](../00-meta/bibliography.md))

4. Google Cloud Monitoring lets an alerting policy monitor only a specified resource group, and widening the monitored universe requires explicit group or project scope choices. That pressures DelayBasin to keep burden on the same slice distinct from explicit scope widening across groups or projects. ([`REF-0935`](../00-meta/bibliography.md), [`REF-0936`](../00-meta/bibliography.md))

5. GitHub Actions workflows can be filtered to specific branches and paths, rulesets target selected branches or tags, and CODEOWNERS are branch-specific and path-pattern-specific. That pressures DelayBasin to distinguish stronger protection or burden on the same targeted surface from a claim that legitimately widens to more branches, paths, or governed areas. ([`REF-0937`](../00-meta/bibliography.md), [`REF-0938`](../00-meta/bibliography.md))

6. PagerDuty's automation guidance says trustworthy automation should keep a narrow functional scope to contain blast radius. That pressures DelayBasin to treat scope widening as a separate named move rather than as an automatic consequence of stronger burden. ([`REF-0939`](../00-meta/bibliography.md))

GPUstorming makes the pressure vivid. A re-opened search line might justify louder language, more followthrough, or stronger notification for the same row. That is not yet permission to say the whole adjacent cluster, upstream dependency tree, or neighboring branch family is implicated. The burden may rise before the claim scope does.

## Working synthesis

> DelayBasin should preserve one compact **refresh-burden-scope witness / scope-widening card / blast-radius brake** whenever a current continuity claim depends not only on what reactivated a concern, how sustained the return is, how broad and independent the support looks, and whether the present support licenses stronger burden, but on whether that stronger burden still governs the same current claim or honestly widens the public claim scope. Name the **governed row or surface**, the **stake object / line of concern**, the **prior refresh evidence**, the **current refresh evidence**, the **licensed burden upgrade if any**, the **same-claim scope anchor**, the **scope-widening evidence if any**, the **scope gate or non-local inference basis if any**, the **`refresh_burden_scope_state`**, and the **fail-closed repair / keep-current vs narrow-claim vs widen-scope vs issue-new-refresh-burden-scope-witness vs quarantine-refresh-scope-governance consequence**. Keep exact component ids, subscriber lists, resource-group filters, project names, path globs, branch targets, dependency trees, and long blast-radius narratives outside the compact token. Do not let stronger burden silently widen public claim scope, and do not let upstream or adjacent distress masquerade as already licensed scope expansion.

## Same-claim burden upgrade vs bounded scope widening vs scope-gated generalization vs mixed refresh burden scope

Use the controlled family `refresh_burden_scope_state`:

- **same-claim-burden-upgrade** says the current evidence licenses a stronger burden on the same governed claim or row, but does not honestly widen what public scope is being claimed.
- **bounded-scope-widening** says the current evidence also names a real widened scope — more affected components, groups, branches, paths, projects, or comparable governed slices — and the archive may honestly widen the public claim in that bounded way.
- **scope-gated-generalization** says the current evidence suggests a broader blast radius, adjacency, dependency, or topology implication, but the archive still lacks the direct mapping needed to widen the public claim honestly.
- **mixed-refresh-burden-scope** says the current situation honestly combines same-claim burden, bounded widening, or scope-gated generalization such that no single class stays honest.

So the witness does not create a standing blast-radius senate.
It only says whether stronger burden still governs the same claim, already licenses bounded widening, or still needs another gate before scope can widen.

## Countermodels / probes

1. **Refresh elevation already covers this countermodel**
   - Maybe once burden upgrade is explicit, a separate scope witness adds no real value.
   - Probe: compare later rereads that preserve only refresh-elevation truth against rereads that also preserve one compact refresh-burden-scope witness and inspect whether later passes still generalize from stronger burden to wider public claim.

2. **Statuspage or monitoring scoping analogies are too operational countermodel**
   - Maybe component, group, and path scoping are too implementation-specific to justify a new archive witness.
   - Probe: look for later cases where scope drift appears in ordinary continuity prose even when no operational component language is present.

3. **Scope-gated generalization is covert governance countermodel**
   - Maybe once scope gates matter, the archive is really sneaking in a full blast-radius court.
   - Probe: only reopen stronger machinery if later revisions repeatedly need standing policy for adjacency, dependency spillover, or cross-row scope widening that one bounded witness cannot absorb.

## Design consequences

- DelayBasin can now separate **stronger burden on the same claim** from **honest widening of the claim's public scope**.
- The archive gets one explicit place to record when scope widened for named reasons and when it only looked wider because of topology, upstream distress, or adjacency.
- Stake refresh, refresh strength, refresh support, refresh independence, refresh elevation, and refresh burden scope now separate **what changed**, **how sustained the return is**, **how broad the support looks**, **how independent it is**, **whether burden rises**, and **whether the claim scope itself may widen**.
- Stronger blast-radius-governance stories stay quarantined until later overflow instead of sneaking in through burden language.

## Overflow test

Reopen this compact witness only if later revisions repeatedly need standing governance over blast-radius policies, dependency-spillover admission, cross-row scope expansion, or audience-right rules for widened claims that one bounded refresh-burden-scope witness cannot honestly absorb.

## Transformer-facing implication

A later pass should not treat a stronger burden as if it automatically widens public claim scope. Preserve the same-claim scope anchor, any named widening evidence, any missing scope gate, and the exact `refresh_burden_scope_state` before generalizing beyond the current governed row.
