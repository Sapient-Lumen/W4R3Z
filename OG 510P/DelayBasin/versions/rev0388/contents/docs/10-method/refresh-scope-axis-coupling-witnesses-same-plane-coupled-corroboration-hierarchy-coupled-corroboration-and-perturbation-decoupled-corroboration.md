# Refresh-scope-axis-coupling witnesses, same-plane coupled corroboration, hierarchy-coupled corroboration, and perturbation-decoupled corroboration

This is the compact successor surface for `OQ-0150`.

## Practice / observation

Once DelayBasin can say that corroborating axes are genuinely independent and materially backed, one more ambiguity remains.

Some materially backed corroboration still rides one plane.
The views differ in real topology, substrate, or failure meaning, but they still collapse together when the relevant switch, scheduler, rack, or parent slice moves.
That is stronger than a mere label difference, yet weaker than truly decoupled corroboration.

Some materially backed corroboration is only hierarchy-separated.
A node axis under one zone, or a compute instance inside one GPU instance, is not just a renamed label.
But it is still nested inside one parent plane and can fail or interfere together in ways that a truly decoupled corroboration surface would not.

And some corroboration really does stay apart under the relevant perturbation.
That is where multi-axis support becomes materially and operationally stronger.

DelayBasin does not need an axis covariance court for those cases.
It needs one bounded witness that says whether the present corroboration is still same-plane coupled, hierarchy-coupled, perturbation-decoupled, or honestly mixed.

## External pressure from Kubernetes topology hierarchy, Ray placement groups, Slurm topology-aware selection, and NVIDIA GI-vs-CI isolation

1. Kubernetes says a zone is a logical failure domain, that nodes within a zone might share a network switch, and that regions and zones are hierarchical with zones as strict subsets of regions. That pressures DelayBasin not to read node-vs-zone corroboration as automatically decoupled just because both are real topology axes. ([`REF-0961`](../00-meta/bibliography.md))

2. Kubernetes topology spread constraints explicitly spread Pods across failure-domains such as regions, zones, nodes, and other user-defined topology domains. That pressures DelayBasin to remember that a multi-level spread can still sit inside one hierarchy unless the relevant perturbation actually separates the axes. ([`REF-0956`](../00-meta/bibliography.md), [`REF-0961`](../00-meta/bibliography.md))

3. Ray placement groups reserve bundles atomically and can either pack them together for locality or spread them apart. Ray also says spreading resources across multiple nodes can help ensure training continues when a node dies. That pressures DelayBasin to distinguish materially backed corroboration that is still packed into one failure plane from corroboration that stays live under node perturbation. ([`REF-0964`](../00-meta/bibliography.md))

4. Slurm's select plugin is topology-aware, groups nodes based on network topology when configured, and can over-subscribe resources for gang scheduling. That pressures DelayBasin to remember that scheduler-visible diversity can still ride one coupled topology or scheduler plane. ([`REF-0965`](../00-meta/bibliography.md))

5. NVIDIA's MIG concepts say a GPU Instance provides memory QoS, but Compute Instances inside one GPU Instance share memory and engines. That pressures DelayBasin to distinguish hierarchy-separated corroboration inside one parent slice from corroboration that really escapes the parent plane. ([`REF-0959`](../00-meta/bibliography.md))

6. NVIDIA's CUPTI documentation says an isolated Compute Instance owns all of its assigned resources and does not share any GPU unit with another Compute Instance, while a shared Compute Instance can use resources potentially also accessed by sibling Compute Instances. That pressures DelayBasin to keep same-plane coupling, hierarchy coupling, and true decoupling distinct even inside one MIG-backed substrate. ([`REF-0966`](../00-meta/bibliography.md))

GPUstorming makes the distinction useful. A search pass can uncover a second real topology axis or a genuine partition mode and still leave the archive overconfident if the axes collapse under one switch, one parent GPU instance, or one packed placement group. The missing question is no longer “is this axis real?” but “does it actually stay apart when the system is perturbed?”

## Working synthesis

> DelayBasin should preserve one compact **refresh-scope-axis-coupling witness / shared-plane brake / perturbation-decoupling card** whenever a current continuity claim depends not only on whether corroborating axes are genuinely independent and materially backed, but on whether that corroboration still rides one coupled failure or execution plane. Name the **governed row or surface**, the **stake object / line of concern**, the **prior refresh-scope-axis-materiality evidence**, the **current corroborating axes**, the **same-plane basis if any**, the **hierarchy-coupled basis if any**, the **perturbation-decoupled basis if any**, the **`refresh_scope_axis_coupling_state`**, and the **fail-closed repair / keep-current vs narrow-claim vs split-scope vs issue-new-refresh-scope-axis-coupling-witness vs quarantine-axis-covariance-machine consequence**. Keep raw topology trees, failure simulations, scheduler configs, and GPU partition tables outside the compact token. Do not let materially real but still coupled corroboration silently inherit the authority of corroboration that remains decoupled under the relevant perturbation.

## Same-plane coupled corroboration vs hierarchy-coupled corroboration vs perturbation-decoupled corroboration vs mixed refresh scope axis coupling

Use the controlled family `refresh_scope_axis_coupling_state`:

- **same-plane-coupled-corroboration** says the corroborating axes are materially real, but the current evidence still places them on one coupled failure or execution plane such that the relevant perturbation can collapse them together.
- **hierarchy-coupled-corroboration** says the corroborating axes are materially distinct, but one remains a child or refinement inside the other's parent failure or execution hierarchy.
- **perturbation-decoupled-corroboration** says the corroborating axes remain meaningfully separate under the perturbation that actually matters for the present claim.
- **mixed-refresh-scope-axis-coupling** says the current situation honestly combines same-plane, hierarchy-coupled, and perturbation-decoupled features such that no single class stays honest.

So the witness does not create a blast-radius matrix.
It only says whether the current corroboration still collapses onto one plane, stays nested inside one hierarchy, remains decoupled under perturbation, or is honestly mixed.

## Countermodels / probes

1. **Materiality already does enough countermodel**
   - Maybe once label-vs-failure-domain-vs-isolation truth is explicit, a separate coupling witness only restates ordinary prose.
   - Probe: compare later rereads that preserve only refresh-scope-axis-materiality truth against rereads that also preserve one compact coupling token and inspect whether materially backed but still packed or nested corroboration keeps being over-read as robustly decoupled.

2. **Hierarchy and same-plane collapse countermodel**
   - Maybe same-plane and hierarchy-coupled cases are close enough that they should live in one shared coupled state.
   - Probe: look for later cases where “inside one parent plane” and “sibling views on exactly one plane” change different downstream judgments, especially under zone-vs-node or GI-vs-CI reasoning.

3. **Covariance is the real issue countermodel**
   - Maybe once coupling matters, the archive really needs a covariance matrix or blast-radius table rather than one flat classification witness.
   - Probe: keep that bolder move quarantined unless later revisions repeatedly need numerical discounts, pairwise covariance language, or explicit perturbation tables that this compact coupling witness cannot honestly absorb.

## Design consequences

- DelayBasin can now separate materially real corroboration that still collapses together from corroboration that remains decoupled under the perturbation that matters.
- The archive gets one explicit place to say that node-vs-zone or CI-vs-GI corroboration is real but still hierarchy-coupled.
- GPUstorming can import sharper topology and partition facts without automatically laundering them into robust decoupling claims.
- Stronger covariance, blast-radius, or perturbation-insurance stories stay quarantined until repeated overflow rather than entering canon by atmosphere.

## Overflow test

Reopen this compact witness only if later revisions repeatedly need pairwise covariance rules, blast-radius tables, perturbation ladders, or quantitative coupling discounts that one bounded refresh-scope-axis-coupling witness cannot honestly absorb.

## Transformer-facing implication

A later pass should not treat every materially backed corroboration surface as equally decoupled. Preserve the smallest token that says whether the present corroboration is `same-plane-coupled-corroboration`, `hierarchy-coupled-corroboration`, `perturbation-decoupled-corroboration`, or honestly `mixed-refresh-scope-axis-coupling`, and quarantine stronger covariance or blast-radius ambitions until repeated overflow makes them unavoidable.
