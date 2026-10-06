# Refresh-scope-extent witnesses, single observed slice, patterned observed spillover, and extent-gated generalization

This is the compact successor surface for `OQ-0145`.

## Practice / observation

Once DelayBasin can say that widened scope is **directly observed** rather than merely dependency- or topology-imputed, one more small failure mode remains.

Sometimes the widened scope is directly observed on exactly one newly added slice.
One extra component really is affected.
One extra host or queue partition really is hot.
One extra label-set instance really is firing.
That matters, but it is still only one newly observed widened slice.

Sometimes the widening is directly observed across several widened slices in a way that honestly looks like a broader spillover pattern.
Multiple newly added components are affected.
Several label-set instances are firing.
Several grouped surfaces now show direct impact.
That is no longer just one extra edge.

And sometimes there is at least one directly observed widened slice, but the remaining broader pattern is still only a projection.
The archive has one or two observed widened slices, but not yet enough direct widened evidence to talk as if the whole nearby family, region, or service cluster is now broadly affected.
That case needs a small gate.

The archive does not need a refresh-extent court for that.
It needs one bounded witness that says whether the current widened truth is still one observed slice, already a broader observed spillover pattern, extent-gated generalization from a smaller observed set, or honestly mixed.

## External pressure from Statuspage affected components and component subscriptions, Prometheus vector-element alerts, Grafana multi-dimensional alert instances, and Datadog simple-vs-multi alert aggregation

1. Statuspage incidents name **affected components**, and its component-subscription guidance shows a concrete progression where an incident first affects `Management Portal` alone and only later expands to `API` as an additional affected component. That pressures DelayBasin to keep one newly observed widened slice distinct from a later broader observed spillover pattern. ([`REF-0933`](../00-meta/bibliography.md); [`REF-0942`](../00-meta/bibliography.md))

2. Statuspage components are discrete service or feature slices with their own statuses, and subscribers can choose incident updates for particular components. That pressures DelayBasin not to narrate one newly affected component as if every nearby component were already part of the observed widened truth. ([`REF-0942`](../00-meta/bibliography.md))

3. Prometheus alerting rules count alerts as active for the **label sets** of the vector elements that match the expression, and the alerts UI shows the exact label sets for which an alert is active. That pressures DelayBasin to distinguish one newly active widened slice from many active widened slices. ([`REF-0943`](../00-meta/bibliography.md))

4. Grafana alerting creates a separate alert instance for every unique combination of labels: one rule, many instances, one per unique label set. That pressures DelayBasin to keep one new widened instance distinct from a broader observed multi-instance spillover pattern. ([`REF-0944`](../00-meta/bibliography.md))

5. Datadog distinguishes **simple alerts**, which aggregate grouped breaches into one alert, from **multi alerts**, which notify for each unique combination of groups and can reveal that several partitions are affected. That pressures DelayBasin to keep a one-slice observed widening distinct from a directly observed broader pattern and to name when the broader pattern is still hidden by aggregation. ([`REF-0945`](../00-meta/bibliography.md))

GPUstorming makes the pressure vivid. An open search can quickly surface one freshly affected component, one hot partition, or one firing label set and tempt a writer into talking as if the whole nearby family is already widened in observed form. The archive needs a compact brake on that inflation.

## Working synthesis

> DelayBasin should preserve one compact **refresh-scope-extent witness / spillover-pattern card / slice-count brake** whenever a current continuity claim depends not only on whether public scope widened and on whether that widened scope is directly observed, but on whether the current direct widening is still only one newly observed slice or already a broader observed spillover pattern. Name the **governed row or surface**, the **stake object / line of concern**, the **prior refresh-scope-basis evidence**, the **current widened-scope evidence**, the **observed widened slice or slice family**, the **broader observed spillover-pattern evidence if any**, the **extent gate / unobserved remainder if any**, the **`refresh_scope_extent_state`**, and the **fail-closed repair / keep-current vs narrow-claim vs split-scope vs issue-new-refresh-scope-extent-witness vs quarantine-refresh-extent-governance consequence**. Keep exact subscriber rosters, full component inventories, alert-instance ids, label-set enumerations, partition lists, and long blast-radius narratives outside the compact token. Do not let one newly affected slice silently count as a broader observed spillover pattern.

## Single observed slice vs patterned observed spillover vs extent-gated generalization vs mixed refresh scope extent

Use the controlled family `refresh_scope_extent_state`:

- **single-observed-slice** says the widened public scope is directly observed on one newly added slice, but not yet on a broader observed spillover pattern.
- **patterned-observed-spillover** says several widened slices are directly observed as affected in a way that honestly supports broader observed spillover language.
- **extent-gated-generalization** says at least one widened slice is directly observed, but the current evidence still does not justify generalizing to the broader nearby remainder as an observed pattern.
- **mixed-refresh-scope-extent** says the current situation honestly combines single-slice observation, some broader patterned spillover evidence, and unresolved extent gates such that no single class stays honest.

So the witness does not create a standing spillover-pattern senate.
It only says how broad the current directly observed widening really is.

## Countermodels / probes

1. **Refresh-scope-basis already covers this countermodel**
   - Maybe once the archive knows the widening is directly observed, nothing more needs to be said about extent.
   - Probe: compare later rereads that keep only basis truth against rereads that also preserve one compact extent witness and inspect whether one new widened slice still gets narrated as a broader observed pattern.

2. **Aggregation and instances are notification artifacts only countermodel**
   - Maybe component selections, alert instances, and grouped notifications are too operational to justify a new archive witness.
   - Probe: look for later continuity prose where one extra directly affected slice still turns into family-wide or region-wide language unless a bounded extent gate is named.

3. **Extent classes are covert saturation governance countermodel**
   - Maybe once single-slice and patterned spillover matter, the archive is really sneaking in a full refresh-extent court.
   - Probe: only reopen stronger machinery if later revisions repeatedly need standing policy about minimum widened slice count, dispersion, or saturation thresholds that one bounded witness cannot absorb.

## Design consequences

- DelayBasin can now separate **one newly observed widened slice** from **a broader observed spillover pattern**.
- The archive gets one explicit place to record when observed widening is still narrow even though it is real.
- Refresh scope basis and refresh scope extent now separate **what basis supports widened talk** from **how broad the directly observed widened pattern really is**.
- Stronger refresh-extent-governance stories stay quarantined until repeated overflow rather than sneaking in through pluralized outage rhetoric.

## Overflow test

Reopen this compact witness only if later revisions repeatedly need standing governance over minimum widened-slice counts, pattern-saturation thresholds, or broader observed-spillover admissibility that one bounded refresh-scope-extent witness cannot honestly absorb.

## Transformer-facing implication

A later pass should not treat one newly affected widened slice as if it already proves a broader observed spillover pattern. Preserve the observed widened slice, any broader observed spillover evidence, any unobserved remainder or extent gate, and the exact `refresh_scope_extent_state` before generalizing beyond the directly observed footprint.
