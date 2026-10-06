# Refresh-scope-axis-remediation witnesses, native controller restoration, external remediator restoration, and operator replay restoration

This is the compact successor surface for `OQ-0153`.

## Practice / observation

Once DelayBasin can say that corroborating axes are genuinely independent, materially backed, decoupled under perturbation, hard-enforced, and honestly durable or grandfathered, one more ambiguity remains.

Some restored decoupling comes back through the platform's own admitted controller path.
A workload controller, scheduler-adjacent controller, or first-party upgrade controller notices the violated or evicted object and recreates the replacement inside the same ordinary policy loop.
That is still a repair story.
But it is not the same as a recovery that only happens because an extra remediator, rebalance service, or administrator steps in from outside the ordinary controller lane.

Some restored decoupling comes back through an external remediator.
A descheduler, node-remediation operator, or comparable auxiliary control loop evicts, taints, drains, or fences work so the desired spread can be re-established.
That still counts as real restoration.
But it should not silently inherit the authority of native controller repair, because the restoration depends on an extra control plane that can be absent, paused, or differently governed.

Some restored decoupling only comes back through operator replay.
A privileged user requeues the job, drains or resumes nodes, deletes the stale pod, or otherwise manually kicks the system back into a good configuration.
That can be perfectly legitimate.
But it is weaker continuation evidence than an admitted controller path that would have repaired the drift without human replay.

DelayBasin does not need a remediation provenance credit ledger for these cases.
It needs one bounded witness that says whether restored decoupling is native-controller, external-remediator, operator-replay, or honestly mixed.

## External pressure from Kubernetes controller replacement, VPA recreate mode, descheduler rebalance, remediation operators, Slurm manual replay, and NVIDIA GPU Operator manual OnDelete

1. Kubernetes Vertical Pod Autoscaling says `Recreate` mode actively evicts Pods whose current requests diverge, then the workload controller creates a replacement Pod and the VPA admission controller applies updated requests to the new Pod. That pressures DelayBasin to keep native controller restoration distinct from broader or manual repair stories. ([`REF-0975`](../00-meta/bibliography.md))

2. Kubernetes Pod Lifecycle says controllers manage disposable Pod instances, a replacement Pod is a new Pod with a different UID, and Kubernetes does not reschedule the same Pod object onto another node. That pressures DelayBasin to name restoration provenance explicitly rather than treating every repaired placement as the same continuing runtime object. ([`REF-0976`](../00-meta/bibliography.md))

3. Kubernetes' SIG Scheduling spotlight says descheduler evicts Pods violating scheduling constraints so they are recreated and rescheduled. That pressures DelayBasin to separate auxiliary rebalance loops from native controller repair when drifted decoupling is restored later. ([`REF-0977`](../00-meta/bibliography.md))

4. Red Hat's Self Node Remediation docs say `MachineHealthCheck` or `NodeHealthCheck` creates a `SelfNodeRemediation` custom resource which triggers the operator, and the operator can use `ResourceDeletion` or `OutOfServiceTaint` strategies. That pressures DelayBasin to treat remediation-operator restoration as a real but externally mediated provenance class rather than as ordinary workload-controller repair. ([`REF-0978`](../00-meta/bibliography.md))

5. Slurm's `scontrol` docs say privileged users can `requeue` jobs back into pending state, and can `DRAIN` or `RESUME` nodes with explicit node-state changes. That pressures DelayBasin to keep operator replay distinct from controller-native restoration when GPU-cluster decoupling only comes back through admin acts. ([`REF-0979`](../00-meta/bibliography.md))

6. NVIDIA GPU Operator docs say the upgrade controller automates upgrade state transitions, while `OnDelete` means a new driver pod is deployed only once the old driver pod is manually deleted by an admin. That pressures DelayBasin to keep controller-native automation distinct from operator-triggered replay even in GPU-native maintenance flows. ([`REF-0980`](../00-meta/bibliography.md))

GPUstorming makes the difference vivid. A topology can look durable because the same anti-affinity, taint, rack, or GPU-domain picture reappears after drift. But sometimes that return came from the admitted controller path, sometimes from an extra remediator, and sometimes from a human replaying drain, delete, or requeue steps. Remediation provenance is the missing compact truth.

## Working synthesis

> DelayBasin should preserve one compact **refresh-scope-axis-remediation witness / repair-provenance card / replay-lane brake** whenever a current continuity claim depends not only on whether corroborating axes are genuinely independent, materially backed, decoupled, hard-enforced, and durable, but on who or what actually restores the decoupling after drift. Name the **governed row or surface**, the **stake object / line of concern**, the **prior refresh-scope-axis-durability evidence**, the **current corroborating axes**, the **native-controller basis if any**, the **external-remediator basis if any**, the **operator-replay basis if any**, the **`refresh_scope_axis_remediation_state`**, and the **fail-closed repair / keep-current vs narrow-claim vs split-scope vs issue-new-refresh-scope-axis-remediation-witness vs quarantine-remediation-provenance-credit consequence**. Keep raw controller DAGs, event streams, runbook transcripts, CRD manifests, and shell replay logs outside the compact token. Do not let restored decoupling silently inherit native self-repair authority when it actually depends on an auxiliary controller or human replay.

## Native controller restoration vs external remediator restoration vs operator replay restoration vs mixed refresh scope axis remediation

Use the controlled family `refresh_scope_axis_remediation_state`:

- **native-controller-restoration** says the documented restoration happens through the platform's admitted workload, scheduler-adjacent, or first-party controller path without requiring a separate remediation operator or manual replay step.
- **external-remediator-restoration** says restored decoupling depends on an auxiliary rebalance, remediation, or health-repair controller outside the primary controller path.
- **operator-replay-restoration** says restored decoupling depends on a privileged manual replay, delete, drain, resume, or requeue act rather than an admitted automated controller path.
- **mixed-refresh-scope-axis-remediation** says the current situation honestly combines native-controller, external-remediator, and operator-replay restoration such that no single provenance class stays honest.

So the witness does not create a remediation provenance credit ledger.
It only says whether restored decoupling currently comes back through native controller action, an auxiliary remediator, a manual replay act, or an honest mix.

## Countermodels / probes

1. **Durability already captures enough countermodel**
   - Maybe once DelayBasin preserves eviction-preserved versus repair-restored versus grandfathered truth, remediation provenance adds only implementation-color.
   - Probe: compare later rereads that preserve only durability truth against rereads that also preserve one compact remediation token and inspect whether repaired spread still gets narrated as native self-healing even when descheduler or admin replay did the actual work.

2. **External remediator and operator replay collapse countermodel**
   - Maybe any non-native restoration is just "extra help" and does not deserve two public classes.
   - Probe: look for later cases where auxiliary controllers remain continuously installed and policy-bounded while manual drain, delete, or requeue acts remain contingent on human intervention and different failure budgets.

3. **Collateral disruption is the real next question countermodel**
   - Maybe provenance is still not enough because the archive's real next need is whether remediation only replaces the violating workload or drains or fences broader substrates.
   - Probe: keep that next question explicit as frontier work unless later revisions show that native-vs-external-vs-manual provenance itself is still insufficient.

## Design consequences

- DelayBasin can now keep repaired decoupling from sounding more self-healing than its actual restoration path warrants.
- The archive gets one explicit place to record when restored spread comes back through descheduler-style rebalance or remediation operators rather than through the main controller lane.
- GPUstorming can now separate controller-native GPU maintenance from operator-replayed drain/delete/requeue flows without opening a full remediation governance stack.
- Stronger remediation provenance credit, controller tariff, or override escrow stories stay quarantined until repeated overflow rather than entering canon by atmosphere.

## Overflow test

Reopen this compact witness only if later revisions repeatedly need controller-authority weighting, remediation trust tariffs, override budgets, or provenance-exchange rules that one bounded refresh-scope-axis-remediation witness cannot honestly absorb.

## Transformer-facing implication

A later pass should not treat every repaired or rebalanced decoupling surface as if the same native controller path restored it. Preserve the smallest token that says whether the present restoration is `native-controller-restoration`, `external-remediator-restoration`, `operator-replay-restoration`, or honestly `mixed-refresh-scope-axis-remediation`, and quarantine stronger remediation-provenance-credit ambitions until repeated overflow makes them unavoidable.
