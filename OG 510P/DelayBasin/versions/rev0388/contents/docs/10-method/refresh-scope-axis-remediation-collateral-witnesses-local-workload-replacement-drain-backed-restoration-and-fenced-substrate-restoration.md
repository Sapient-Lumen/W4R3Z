# Refresh-scope-axis-remediation-collateral witnesses, local workload replacement, drain-backed restoration, and fenced-substrate restoration

This is the compact successor surface for `OQ-0154`.

## Practice / observation

Once DelayBasin can say that corroborating axes are genuinely independent, materially backed, decoupled under perturbation, hard-enforced, honestly durable, and explicit about who restores them after drift, one more ambiguity remains.

Some restored decoupling comes back through local workload replacement.
A violating or stranded Pod, task, or job is recreated elsewhere by its controller or scheduler lane.
The restoration is real.
But its collateral can still stay comparatively local: the old workload is replaced, while the surrounding node, rack, or substrate is not broadly drained or fenced.

Some restored decoupling comes back through drain-backed restoration.
A node, host, or maintenance surface is cordoned, drained, or otherwise cleared so multiple neighboring workloads move away and the desired spread can be re-established.
That may be entirely appropriate.
But it should not silently inherit the authority of a cheap local replacement, because the restoration spent a broader disruption budget than replacing only the violating workload.

Some restored decoupling comes back through fenced-substrate restoration.
A node is marked out of service, rebooted, power-cycled, reprovisioned, or otherwise fenced before workloads recover elsewhere.
That can be the honest thing to do when safety, attachment, or at-most-one semantics matter.
But it is a wider and costlier collateral lane than local replacement or even ordinary drain.

DelayBasin does not need a disruption-budget court for these cases.
It needs one bounded witness that says whether restored decoupling currently depends on local workload replacement, drain-backed restoration, fenced-substrate restoration, or an honest mix.

## External pressure from Kubernetes controller replacement, `kubectl drain`, out-of-service fencing, OpenShift remediation and maintenance operators, Slurm drain/down states, and NVIDIA GPU Operator node-drain fallback

1. Kubernetes Pod Lifecycle says controllers manage disposable Pods, replacements are new Pods with different UIDs, and Kubernetes does not reschedule the same Pod object onto another node. That pressures DelayBasin to keep local workload replacement explicit rather than narrating every recovery as a substrate event. ([`REF-0976`](../00-meta/bibliography.md))

2. `kubectl drain` says a node is marked unschedulable and the command evicts or deletes all Pods on the node except mirror Pods, waiting for graceful termination before maintenance proceeds. That pressures DelayBasin to distinguish broad drain-backed restoration from merely replacing one violating workload. ([`REF-0981`](../00-meta/bibliography.md))

3. Kubernetes Node Shutdowns says the `node.kubernetes.io/out-of-service` taint forcefully deletes Pods lacking matching tolerations, immediately performs volume detach work, and lets Pods recover on another node. That pressures DelayBasin to distinguish fenced-substrate restoration from ordinary local replacement or drain. ([`REF-0982`](../00-meta/bibliography.md))

4. Red Hat's remediation, fencing, and maintenance docs say Self Node Remediation reboots unhealthy nodes and deletes resources, Machine Deletion Remediation deletes the machine so an owning controller recreates a replacement, and Node Maintenance cordons and drains a node while the maintenance resource exists. That pressures DelayBasin to separate local replacement, maintenance drain, and fenced-substrate remediation rather than flattening them into one generic restoration class. ([`REF-0983`](../00-meta/bibliography.md))

5. Slurm `scontrol` says `DRAIN` blocks new jobs while existing jobs complete, `DOWN` stops running and suspended jobs and makes the node unavailable, and `requeue` returns jobs to pending state. That pressures DelayBasin to keep job-level replay distinct from node-drain or node-down collateral in GPU-cluster recovery stories. ([`REF-0984`](../00-meta/bibliography.md))

6. NVIDIA GPU Operator docs say `k8s-driver-manager` first attempts evicting only GPU Pods from the node and only falls back to a node drain when that local eviction path fails and auto-drain is enabled. That pressures DelayBasin to keep local replacement or local eviction distinct from broader maintenance-drain collateral in GPU-native repair flows. ([`REF-0985`](../00-meta/bibliography.md))

GPUstorming makes the difference vivid. Two clusters can both end with the same anti-affinity, rack, taint, or GPU-domain picture restored after drift. But one got there by replacing a single violating workload, another by draining a node full of neighbors, and another by fencing or reprovisioning substrate. Remediation provenance alone does not say how much collateral the repair spent.

## Working synthesis

> DelayBasin should preserve one compact **refresh-scope-axis-remediation-collateral witness / drain-budget card / fenced-substrate brake** whenever a current continuity claim depends not only on whether corroborating axes are genuinely independent, materially backed, decoupled, hard-enforced, durable, and explicitly restored, but on how much surrounding workload or substrate disruption that restoration spends. Name the **governed row or surface**, the **stake object / line of concern**, the **prior refresh-scope-axis-remediation evidence**, the **current corroborating axes**, the **local-workload-replacement basis if any**, the **drain-backed basis if any**, the **fenced-substrate basis if any**, the **`refresh_scope_axis_remediation_collateral_state`**, and the **fail-closed repair / keep-current vs narrow-claim vs split-scope vs issue-new-refresh-scope-axis-remediation-collateral-witness vs quarantine-remediation-collateral-tariff consequence**. Keep raw drain transcripts, volume-attachment traces, reboot logs, host fencing records, and full maintenance runbooks outside the compact token. Do not let drain-backed or fenced-substrate restoration silently inherit the cheap authority of local workload replacement.

## Local workload replacement vs drain-backed restoration vs fenced-substrate restoration vs mixed refresh scope axis remediation collateral

Use the controlled family `refresh_scope_axis_remediation_collateral_state`:

- **local-workload-replacement** says the documented restoration replaces or requeues the violating workload locally without needing a broad maintenance drain or explicit substrate fencing step.
- **drain-backed-restoration** says restored decoupling depends on cordoning, draining, or otherwise clearing a node or maintenance surface so neighboring workloads are moved away.
- **fenced-substrate-restoration** says restored decoupling depends on marking substrate out of service, rebooting, power-cycling, force-detaching, reprovisioning, or comparable fencing before recovery proceeds.
- **mixed-refresh-scope-axis-remediation-collateral** says the current situation honestly combines local replacement, drain-backed restoration, and fenced-substrate restoration such that no single collateral class stays honest.

So the witness does not create a disruption-budget ledger.
It only says whether the present restoration stays local, spends a drain, spends a fenced substrate, or is honestly mixed.

## Countermodels / probes

1. **Remediation provenance already captures enough countermodel**
   - Maybe once DelayBasin knows whether restoration was native, external, or manual, collateral width adds only operational color.
   - Probe: compare later rereads that preserve only provenance truth against rereads that also preserve one compact collateral token and inspect whether drain- or fence-backed recoveries still get narrated as cheap local repair.

2. **Drain and fence collapse countermodel**
   - Maybe any non-local restoration is just "broad disruption" and does not deserve two public classes.
   - Probe: look for later cases where drain leaves substrate live and schedulable again while fence or out-of-service handling reboots, reprovisions, or forcibly detaches attachments before recovery.

3. **Capacity source is the real next question countermodel**
   - Maybe collateral width is still not enough because the archive next needs to say whether recovery used free spare capacity or reclaimed capacity by preempting unrelated lower-priority work.
   - Probe: keep that next question explicit as frontier work unless later revisions show that local-vs-drain-vs-fence truth itself is still insufficient.

## Design consequences

- DelayBasin can now keep repaired decoupling from sounding cheaper or narrower than the restoration actually was.
- The archive gets one explicit place to record when a repaired GPU or scheduler topology only returned after draining neighbors or fencing substrate rather than replacing the violating workload locally.
- GPUstorming can now separate "replace the bad Pod" from "drain the host" from "fence the substrate" without opening a full disruption-budget court.
- Stronger collateral-tariff, blast-radius ledger, or disruption-budget escrow stories stay quarantined until repeated overflow rather than entering canon by atmosphere.

## Overflow test

Reopen this compact witness only if later revisions repeatedly need explicit disruption tariffs, collateral exchange rates, blast-radius budgets, or remediation-pricing rules that one bounded refresh-scope-axis-remediation-collateral witness cannot honestly absorb.

## Transformer-facing implication

A later pass should not treat every repaired or rebalanced decoupling surface as if it spent the same disruption budget. Preserve the smallest token that says whether the present restoration is `local-workload-replacement`, `drain-backed-restoration`, `fenced-substrate-restoration`, or honestly `mixed-refresh-scope-axis-remediation-collateral`, and quarantine stronger remediation-collateral-tariff ambitions until repeated overflow makes them unavoidable.
