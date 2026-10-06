# Refresh-scope-distribution witnesses, clustered observed spillover, dispersed observed spillover, and distribution-gated generalization

This is the compact successor surface for `OQ-0146`.

## Practice / observation

Once DelayBasin can separate **one newly observed widened slice** from **a broader observed spillover pattern**, one more local failure mode remains.

Some observed spillover is still clustered.
Several widened slices are real and directly observed, but they still sit inside one local family: one component group, one team label, one service cluster, one zone, one topology neighborhood, one small children-set under a common parent.
That is broader than a single slice, but it is not yet the same thing as dispersed spread.

Some observed spillover is honestly dispersed.
The widened slices are still directly observed, but they now span multiple named families or failure domains rather than one local cluster.
Different component groups are affected.
Different label groups are affected.
Different teams, services, zones, or topology domains are affected.
That is the point where "spread" becomes the more honest word.

And some cases are still gated.
A few widened families are observed, but not enough to license archive-wide, page-wide, or family-class generalization.
The archive needs one more compact witness before it turns clustered or partial dispersion into diffusion talk.

DelayBasin does not need a refresh-distribution court for that.
It needs one bounded witness that says whether the current observed spillover is still clustered, already dispersed, still distribution-gated from broader generalization, or honestly mixed.

## External pressure from Statuspage component groups, Alertmanager grouping, Grafana grouping and scope routing, Kubernetes topology spread, and Google Cloud failure domains

1. Statuspage lets operators create **component groups**, add components to groups, and reorder the children inside a group. That pressures DelayBasin to distinguish spillover that still sits inside one named component family from spillover that is dispersed across several families. ([`REF-0946`](../00-meta/bibliography.md))

2. Alertmanager groups alerts of similar nature into a single notification, and during larger outages recommends grouping alerts by labels such as `cluster` and `alertname` while still letting operators see exactly which service instances were affected. That pressures DelayBasin to distinguish a clustered observed spillover inside one grouping label from broader spread across multiple groups or clusters. ([`REF-0947`](../00-meta/bibliography.md))

3. Grafana groups alert instances only when they have the same exact label values for the configured `Group by` labels, and its notification policies are explicitly scoped by labels such as team or service. That pressures DelayBasin to keep one grouped local cluster distinct from dispersed observed spillover across several scopes. ([`REF-0948`](../00-meta/bibliography.md))

4. Kubernetes topology spread constraints are about how Pods are spread across failure-domains such as regions, zones, nodes, and other topology domains. That pressures DelayBasin to distinguish a local observed cluster inside one failure domain from spillover dispersed across multiple topology domains. ([`REF-0949`](../00-meta/bibliography.md))

5. Google Cloud says resources should be distributed across multiple zones and regions to tolerate outages, and that zones are designed to minimize correlated failures from physical infrastructure problems. That pressures DelayBasin to distinguish one local correlated cluster from a genuinely dispersed multi-zone or multi-region spread. ([`REF-0950`](../00-meta/bibliography.md))

GPUstorming makes the pressure vivid. An open search can easily yield a small local family of observed matches that *feels* broad because the results arrive in parallel panes. But clustered hits inside one group, one domain, or one topology neighborhood are not yet the same thing as dispersed spread across several widened families.

## Working synthesis

> DelayBasin should preserve one compact **refresh-scope-distribution witness / diffusion card / cluster-spread brake** whenever a current continuity claim depends not only on whether public scope widened, on whether that widened scope is directly observed, and on whether the observed widening is already a broader pattern, but on whether the present observed spillover still clusters inside one named widened family or is honestly dispersed across several widened families. Name the **governed row or surface**, the **stake object / line of concern**, the **prior refresh-scope-extent evidence**, the **current widened-scope evidence**, the **observed clustered-family basis if any**, the **dispersed widened-family evidence if any**, the **distribution gate or uncovered family remainder if any**, the **`refresh_scope_distribution_state`**, and the **fail-closed repair / keep-current vs narrow-claim vs split-scope vs issue-new-refresh-scope-distribution-witness vs quarantine-refresh-distribution-governance consequence**. Keep exact component rosters, label matrices, topology-domain ids, zone names, graph inventories, and long diffusion narratives outside the compact token. Do not let a local observed cluster silently count as dispersed spread.

## Clustered observed spillover vs dispersed observed spillover vs distribution-gated generalization vs mixed refresh scope distribution

Use the controlled family `refresh_scope_distribution_state`:

- **clustered-observed-spillover** says the current observed spillover is real and broader than one slice, but still clustered inside one named widened family, group, or failure domain.
- **dispersed-observed-spillover** says the current observed spillover is directly observed across several named widened families or domains rather than remaining one local cluster.
- **distribution-gated-generalization** says some dispersion is observed, but broader family-wide or archive-wide generalization is still gated by uncovered families or incomplete spread.
- **mixed-refresh-scope-distribution** says the current situation honestly combines clustered and dispersed signals such that no single class stays honest.

So the witness does not create a standing diffusion senate.
It only says how the currently observed widened spillover is distributed.

## Countermodels / probes

1. **Refresh-scope-extent already covers this countermodel**
   - Maybe once one-vs-many slice truth is explicit, a separate distribution witness adds no real value.
   - Probe: compare later rereads that preserve only refresh-scope-extent truth against rereads that also preserve one compact refresh-scope-distribution witness and inspect whether local clusters still get narrated as dispersed spread.

2. **Grouping and topology are only notification conveniences countermodel**
   - Maybe component groups, label groups, and topology domains are too operational to justify a new archive witness.
   - Probe: look for later cases where ordinary continuity prose still slides from one grouped or co-located cluster to family-wide diffusion claims even without explicit observability jargon.

3. **Distribution classes are covert diffusion governance countermodel**
   - Maybe once clustered vs dispersed truth matters, the archive is really sneaking in a full refresh-distribution court.
   - Probe: only reopen stronger machinery if later revisions repeatedly need standing policy for cluster-admissibility, dispersion thresholds, or cross-domain diffusion authority that one bounded witness cannot absorb.

## Design consequences

- DelayBasin can now separate **broader observed spillover that is still clustered** from **broader observed spillover that is honestly dispersed**.
- The archive gets one explicit place to record when spread is still local to one named family, group, or domain.
- Refresh scope extent and refresh scope distribution now separate **how many widened slices are observed** from **how those observed slices are distributed across widened families**.
- Stronger refresh-distribution-governance stories stay quarantined until later overflow instead of sneaking in through diffusion rhetoric.

## Overflow test

Reopen this compact witness only if later revisions repeatedly need standing governance over cluster admissibility, dispersion thresholds, cross-domain spread authority, or diffusion policy that one bounded refresh-scope-distribution witness cannot honestly absorb.

## Transformer-facing implication

A later pass should not treat broader observed spillover as if it were already dispersed spread merely because several observed slices exist. Preserve the exact clustered-family basis if any, the dispersed-family evidence if any, the uncovered remainder if any, and the exact `refresh_scope_distribution_state` before claiming that the widening is already family-diffuse or archive-diffuse.
