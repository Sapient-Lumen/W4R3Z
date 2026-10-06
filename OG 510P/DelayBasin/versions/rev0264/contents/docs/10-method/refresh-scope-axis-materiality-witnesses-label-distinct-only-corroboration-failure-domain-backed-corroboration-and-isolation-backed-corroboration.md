# Refresh-scope-axis-materiality witnesses, label-distinct-only corroboration, failure-domain-backed corroboration, and isolation-backed corroboration

This is the compact successor surface for `OQ-0149`.

## Practice / observation

Once DelayBasin can say that corroborating axes are genuinely independent rather than renamed, mirrored, or nested, one more ambiguity remains.

Some independent axes are still weakly material.
They differ as labels, dashboards, or selectors, but not yet in a way that changes where failures cluster or how execution is isolated.
They are independent enough to count as different views, but not yet strong enough to inherit the force of a fault-domain or substrate split.

Some independent axes are backed by failure domains.
A zone axis is not just another name when it tracks where correlated outages are expected to stop.
A topology domain can change expected availability even if it does not carve the execution substrate into isolated slices.

Some independent axes are backed by substrate isolation.
A GPU partition with dedicated compute and memory is not only another label.
It changes interference, isolation, and fault boundaries in a way that a relabeled shared surface does not.

DelayBasin does not need an exchange rate for those cases.
It needs one bounded witness that says whether the present corroboration is only label-distinct, backed by a failure domain, backed by substrate isolation, or honestly mixed.

## External pressure from Ray label selectors, Kubernetes zones and topology spread, Slurm and Oracle shape fault domains, and NVIDIA MIG isolation

1. Ray label selectors let a task or actor require one or more labels, and when multiple selectors are present the candidate node must meet all requirements. That pressures DelayBasin to remember that a distinct selector clause can still be only a routing or labeling fact rather than a material split in failure or execution consequences. ([`REF-0957`](../00-meta/bibliography.md))

2. Kubernetes topology spread constraints explicitly spread Pods across failure-domains such as regions, zones, nodes, and other topology domains. That pressures DelayBasin to distinguish a corroborating axis that is backed by a public failure-domain story from one that is only label-distinct. ([`REF-0956`](../00-meta/bibliography.md))

3. Kubernetes also says a zone is a logical failure domain, commonly used for increased availability, with failure independence from other zones. That pressures DelayBasin to treat some topology axes as materially stronger than ordinary labels even when they are still represented through labels in configuration. ([`REF-0961`](../00-meta/bibliography.md))

4. Slurm's GRES guide says MPS lets GPUs be shared by multiple jobs and that the same GPU can be allocated as MPS resources to multiple jobs, while MIG instances can be treated as individual GPUs with cgroup isolation and task binding. That pressures DelayBasin to distinguish a shared substrate with percentage slices from a materially isolated substrate split. ([`REF-0962`](../00-meta/bibliography.md))

5. NVIDIA's Kubernetes time-slicing guide says time-slicing has no memory or fault isolation between replicas, while MIG provides memory and fault isolation at the hardware layer. That pressures DelayBasin not to let a label change like `-SHARED` inherit the authority of a hardware-isolated partition. ([`REF-0963`](../00-meta/bibliography.md))

GPUstorming makes the difference vivid. A search shell can expose a new label, queue, or product suffix and make the archive feel multi-axis. But a time-sliced shared GPU with a renamed product string is still materially weaker than a MIG-backed split, and a zone-backed spread is stronger in a different way than a mere dashboard regrouping.

## Working synthesis

> DelayBasin should preserve one compact **refresh-scope-axis-materiality witness / fault-domain brake / isolation-backed corroboration card** whenever a current continuity claim depends not only on whether corroborating axes are genuinely independent, but on whether that independence is only label-distinct, backed by a public failure domain, or backed by substrate isolation. Name the **governed row or surface**, the **stake object / line of concern**, the **prior refresh-scope-axis-independence evidence**, the **current corroborating axes**, the **label-distinct-only basis if any**, the **failure-domain basis if any**, the **isolation-backed basis if any**, the **`refresh_scope_axis_materiality_state`**, and the **fail-closed repair / keep-current vs narrow-claim vs split-scope vs issue-new-refresh-scope-axis-materiality-witness vs quarantine-axis-materiality-exchange-rate consequence**. Keep raw schedulers, topology maps, GPU inventories, and isolation tables outside the compact token. Do not let a merely label-distinct axis silently inherit the authority of a failure-domain or isolation-backed corroboration surface.

## Label-distinct-only corroboration vs failure-domain-backed corroboration vs isolation-backed corroboration vs mixed refresh scope axis materiality

Use the controlled family `refresh_scope_axis_materiality_state`:

- **label-distinct-only-corroboration** says the axes are genuinely distinct enough to count as separate views, but the current evidence only licenses a naming, routing, or selector distinction rather than a stronger fault-domain or isolation consequence.
- **failure-domain-backed-corroboration** says the corroborating axis is backed by a public topology or failure-domain story that changes expected correlated failure or availability posture.
- **isolation-backed-corroboration** says the corroborating axis is backed by substrate isolation or materially separate execution slices rather than only by labels or routing surfaces.
- **mixed-refresh-scope-axis-materiality** says the current situation honestly combines label-distinct, failure-domain, and isolation-backed features such that no single class stays honest.

So the witness does not create a corroboration capital stack.
It only says whether the present corroboration is weakly material, failure-domain-backed, isolation-backed, or honestly mixed.

## Countermodels / probes

1. **Independence already does enough countermodel**
   - Maybe once renamed, nested, and genuinely independent axes are separated, adding materiality only restates obvious prose.
   - Probe: compare later rereads that preserve only refresh-scope-axis-independence truth against rereads that also preserve one compact materiality token and inspect whether label-distinct axes still inherit the force of stronger fault-domain or isolation-backed corroboration.

2. **Failure-domain and isolation distinctions collapse countermodel**
   - Maybe zone-backed and substrate-isolated corroboration are both just “strong enough” and do not deserve separate public states.
   - Probe: look for later cases where availability-oriented domains and execution-isolation domains change different downstream judgments even when both are materially stronger than labels.

3. **Weighting is the real issue countermodel**
   - Maybe once materiality matters, the archive really needs an exchange rate or haircut rather than one flat classification witness.
   - Probe: keep that bolder move quarantined unless later revisions repeatedly need additive weights, coupling haircuts, or capital-stack language that this compact materiality witness cannot honestly absorb.

## Design consequences

- DelayBasin can now separate genuine axis independence from the stronger question of whether the present corroboration is only label-distinct, failure-domain-backed, or isolation-backed.
- The archive gets one explicit place to say that an apparently new axis remains materially weak even when it is not merely renamed or nested.
- Failure-domain-backed and isolation-backed corroboration now stay available without forcing a full weighting regime.
- Stronger exchange-rate or capital-stack stories stay quarantined until repeated overflow rather than entering canon by vibe.

## Overflow test

Reopen this compact witness only if later revisions repeatedly need standing weighting rules, coupling haircuts, or additive corroboration policy that one bounded refresh-scope-axis-materiality witness cannot honestly absorb.

## Transformer-facing implication

A later pass should not treat every genuinely independent axis as if it carried the same material force. Preserve the smallest token that says whether the present corroboration is `label-distinct-only-corroboration`, `failure-domain-backed-corroboration`, `isolation-backed-corroboration`, or honestly `mixed-refresh-scope-axis-materiality`, and quarantine stronger exchange-rate ambitions until repeated overflow makes them unavoidable.
