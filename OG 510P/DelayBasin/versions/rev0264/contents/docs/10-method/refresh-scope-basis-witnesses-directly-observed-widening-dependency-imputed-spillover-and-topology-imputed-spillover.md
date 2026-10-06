# Refresh-scope-basis witnesses, directly observed widening, dependency-imputed spillover, and topology-imputed spillover

This is the compact successor surface for `OQ-0144`.

## Practice / observation

Once DelayBasin can separate **stronger burden on the same claim** from **honest scope widening**, one more local failure mode remains.

Some widened scope is directly observed on the widened surface itself.
A newly added component really shows degraded state.
A newly added service really shows errors.
A newly added row really contains current evidence on that widened slice.
That is the easy case.

Some widened scope is only dependency-imputed.
A local row depends on an upstream service, queue, or provider that is failing.
The dependency relation is real, and it may matter, but the widened target has not yet been directly observed as affected.

And some widened scope is only topology-imputed.
A graph, map, or context chain shows adjacency, call flow, or shared placement.
That is useful for prediction, routing, and diagnosis.
It is not yet the same thing as direct observation on every widened surface the map suggests.

The archive does not need a refresh-topology court for that.
It needs one bounded witness that says whether the widened public scope is directly observed, dependency-imputed, topology-imputed, or honestly mixed.

## External pressure from Statuspage affected-component impact, Statuspage third-party overrides, Datadog observed service maps and inferred dependency nodes, Grafana dependency graphs and blast-radius exploration, and OpenTelemetry context propagation

1. Statuspage computes incident impact from the affected components of the incident. That pressures DelayBasin to treat widened scope as directly observed only when the widened affected surface is actually named and affected rather than merely nearby. ([`REF-0932`](../00-meta/bibliography.md))

2. Statuspage also lets operators override a third-party component when the external incident does not affect their own service. That pressures DelayBasin to preserve a dependency-imputed class instead of promoting every upstream incident into directly observed local widening. ([`REF-0934`](../00-meta/bibliography.md))

3. Datadog's Service Map draws **observed dependencies** between services in real time, while a resource Dependency Map is scoped to the selected service/resource and explicitly marks some databases, queues, or third-party services as **inferred service dependencies**. That pressures DelayBasin to separate widened scope directly observed on the widened surface from widened scope only inferred through dependency structure. ([`REF-0940`](../00-meta/bibliography.md))

4. Grafana's entity graph helps teams **predict** incident blast radius and assess change impact from relationships, while Tempo service graphs explicitly **infer the topology** of a distributed system. That pressures DelayBasin to keep topology-imputed spillover distinct from directly observed widening on the widened public surface. ([`REF-0941`](../00-meta/bibliography.md))

5. OpenTelemetry context propagation lets traces, metrics, and logs be correlated across service boundaries through shared context. That pressures DelayBasin not to treat context-linked widening as if every linked service has already been directly observed as affected. ([`REF-0922`](../00-meta/bibliography.md))

GPUstorming makes the pressure vivid. An open search may expose a dependency path, a graph edge, or a correlated telemetry chain that suggests broader risk. That is often the right place to look next. It is not yet permission to speak as if every newly linked surface is already directly affected.

## Working synthesis

> DelayBasin should preserve one compact **refresh-scope-basis witness / spillover-basis card / map-glow brake** whenever a current continuity claim depends not only on whether public scope widened, but on whether that widened scope is directly observed on the widened surface or only inferred from dependency or topology relations. Name the **governed row or surface**, the **stake object / line of concern**, the **prior refresh-burden-scope evidence**, the **current widened-scope evidence**, the **direct observation basis if any**, the **dependency relation basis if any**, the **topology relation basis if any**, the **`refresh_scope_basis_state`**, and the **fail-closed repair / keep-current vs narrow-claim vs split-scope vs issue-new-refresh-scope-basis-witness vs quarantine-refresh-topology-governance consequence**. Keep exact component ids, span ids, graph nodes, path enumerations, service names, and long blast-radius narratives outside the compact token. Do not let graph or map glow silently count as directly observed widened impact.

## Directly observed widening vs dependency-imputed spillover vs topology-imputed spillover vs mixed refresh scope basis

Use the controlled family `refresh_scope_basis_state`:

- **directly-observed-widening** says the widened public scope is backed by current observation on the widened surface itself.
- **dependency-imputed-spillover** says the widened scope is presently inferred through an upstream, downstream, or other dependency relation rather than direct observation on the widened surface.
- **topology-imputed-spillover** says the widened scope is presently inferred through map, graph, adjacency, context, or placement structure rather than direct observation on the widened surface.
- **mixed-refresh-scope-basis** says the current situation honestly combines directly observed widening with dependency- or topology-imputed spillover such that no single class stays honest.

So the witness does not create a standing spillover senate.
It only says what basis currently licenses the widened-scope talk.

## Countermodels / probes

1. **Refresh-burden-scope already covers this countermodel**
   - Maybe once widened scope is explicit, a separate basis witness adds no real value.
   - Probe: compare later rereads that preserve only refresh-burden-scope truth against rereads that also preserve one compact refresh-scope-basis witness and inspect whether later passes still slide from widened scope to directly observed impact without naming basis.

2. **Dependency and topology analogies are only diagnostic aids countermodel**
   - Maybe service maps, entity graphs, and trace context are too operational or predictive to justify a new archive witness.
   - Probe: look for later cases where ordinary continuity prose still overclaims widened impact from adjacency or upstream distress even outside overt observability language.

3. **Spillover classes are covert topology governance countermodel**
   - Maybe once dependency-imputed and topology-imputed classes matter, the archive is really sneaking in a full refresh-topology court.
   - Probe: only reopen stronger machinery if later revisions repeatedly need standing policy for graph admissibility, dependency authority, or topology evidence classes that one bounded witness cannot absorb.

## Design consequences

- DelayBasin can now separate **widened scope that is directly observed** from **widened scope that is only inferred through dependency or topology**.
- The archive gets one explicit place to record when broadened public scope is real observation and when it is still only a spillover forecast or adjacency cue.
- Refresh burden scope and refresh scope basis now separate **whether scope widened at all** from **what basis supports talking that way**.
- Stronger refresh-topology-governance stories stay quarantined until later overflow instead of sneaking in through graph-shaped rhetoric.

## Overflow test

Reopen this compact witness only if later revisions repeatedly need standing governance over graph admissibility, spillover authority, dependency-evidence classes, or topology-evidence policy that one bounded refresh-scope-basis witness cannot honestly absorb.

## Transformer-facing implication

A later pass should not treat widened public scope as if it were directly observed merely because a dependency map, service graph, or context chain links the surfaces. Preserve the exact direct-observation basis if any, the dependency or topology basis if any, and the exact `refresh_scope_basis_state` before claiming that widened scope is already observed truth.
