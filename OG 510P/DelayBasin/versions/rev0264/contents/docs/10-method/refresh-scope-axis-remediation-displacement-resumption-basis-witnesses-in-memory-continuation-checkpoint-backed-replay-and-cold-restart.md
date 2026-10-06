# Refresh-scope-axis-remediation-displacement-resumption-basis witnesses, in-memory continuation, checkpoint-backed replay, and cold restart

This is the compact successor surface for `OQ-0157`.

## Practice / observation

Once DelayBasin can already say that corroborating axes are genuinely independent, materially backed, decoupled under perturbation, hard-enforced, durable, explicit about who restored the decoupling, honest about how wide the remediation was, honest about whether restored placement reused free capacity or displaced unrelated lower-priority work, and honest about whether displaced lower-priority work kept a live path back at all, one more ambiguity remains.

Not every live path back returns in the same way.
Some displaced work is really still there in memory, merely stopped and later continued.
Other work comes back only because a checkpoint is replayed after re-admission.
Still other work returns only as a fresh restart with no preserved execution state beyond source, configuration, or whatever the application saved on its own.

Those three cases should not inherit the same legitimacy from the word resume.
In-memory continuation, checkpoint-backed replay, and cold restart carry different continuity costs even when all of them avoid outright terminal sacrifice.

DelayBasin does not need a restart-economy board here.
It needs one bounded witness that says whether the resumed work was still live in memory, came back by replaying saved state, or came back as a cold restart.

## External pressure from Slurm suspend and checkpoint-restart paths, Kubernetes Job suspension and Pod replacement, and NVIDIA Run:ai checkpoint-driven preemptible resume

1. Slurm's current configuration docs say `SUSPEND` preempts jobs by suspending them so the Gang scheduler later resumes them, that suspended jobs still use memory on the allocated nodes, and that suspended jobs do not release GRES. Slurm's batch-submission docs likewise say suspended jobs still reside in memory. That pressures DelayBasin to keep genuine in-memory continuation distinct from every kind of replay or restart. ([`REF-0999`](../00-meta/bibliography.md), [`REF-1000`](../00-meta/bibliography.md), [`REF-1001`](../00-meta/bibliography.md))

2. Slurm's scheduler-design material says `scontrol checkpoint vacate` releases nodes back to the scheduling pool and restart relies on a new job being scheduled. That pressures DelayBasin to distinguish checkpoint-backed replay from live in-memory continuation because the resumed work is admitted again rather than merely thawed in place. ([`REF-1002`](../00-meta/bibliography.md))

3. Kubernetes Job docs say suspending a Job deletes its active Pods until the Job is resumed again, sends SIGTERM to the running Pods, and explicitly notes that handling suspension may involve saving progress for later. Kubernetes Pod lifecycle docs also say Pods are relatively ephemeral, are scheduled only once, are never rescheduled to a different node, and replacements are new Pods with different UIDs. Together, that pressures DelayBasin to treat much Kubernetes-style resume as replacement-pod replay or restart rather than as in-memory continuation; when no saved progress basis is public, the honest reading is cold restart after displacement. ([`REF-1003`](../00-meta/bibliography.md), [`REF-1004`](../00-meta/bibliography.md))

4. NVIDIA Run:ai says preemptible workloads may be paused for higher-priority work and later automatically resumed, but also says resumed workloads may land on a different node, should save checkpoints on shared storage, can use signal hooks to save state before suspension, and on resume will run the same startup script as on the first run and must explicitly load saved checkpoints. That pressures GPUstorming to keep checkpoint-backed replay distinct from both true in-memory continuation and bare cold restart. ([`REF-1005`](../00-meta/bibliography.md))

GPUstorming makes the distinction vivid. Two lower-priority GPU trainings can both count as resumable aftercare. One may really remain live in RAM with its claimed execution state intact. Another may only come back after replaying a checkpoint. A third may merely relaunch containers and start again from scratch. Aftercare truth alone does not say how warm the return actually was.

## Working synthesis

> DelayBasin should preserve one compact **refresh-scope-axis-remediation-displacement-resumption-basis witness / warmth card / replay brake** whenever a current continuity claim depends not only on whether corroborating axes are genuinely independent, materially backed, decoupled, hard-enforced, durable, explicitly restored, honest about collateral width, honest about whether restored placement reused free capacity or displaced unrelated lower-priority work, and honest about whether that displaced work retained a live return path, but on how the work actually came back. Name the **governed row or surface**, the **stake object / line of concern**, the **prior refresh-scope-axis-remediation-displacement-aftercare evidence**, the **current corroborating axes**, the **in-memory continuation basis if any**, the **checkpoint-backed replay basis if any**, the **cold-restart basis if any**, the **`refresh_scope_axis_remediation_displacement_resumption_basis_state`**, and the **fail-closed repair / keep-current vs narrow-claim vs split-scope vs issue-new-refresh-scope-axis-remediation-displacement-resumption-basis-witness vs quarantine-warm-state-credit consequence**. Keep raw checkpoint intervals, replay durations, cache warmth, optimizer details, and node-local trace data outside the compact token. Do not let every nonterminal return silently inherit the authority of live in-memory continuation.

## In-memory continuation vs checkpoint-backed replay vs cold restart after displacement vs mixed refresh scope axis remediation displacement resumption basis

Use the controlled family `refresh_scope_axis_remediation_displacement_resumption_basis_state`:

- **in-memory-continuation** says the displaced work stayed live in memory or equivalent live execution state and later continued without requiring a new replay from saved state.
- **checkpoint-backed-replay** says the displaced work came back by loading previously saved state, checkpoint artifacts, or equivalent persisted execution state after re-admission or relaunch.
- **cold-restart-after-displacement** says the displaced work came back only as a fresh start without public evidence of restored execution state beyond ordinary source or configuration.
- **mixed-refresh-scope-axis-remediation-displacement-resumption-basis** says the current situation honestly combines more than one basis, or the public evidence cannot keep one clean basis honest.

So the witness does not create a restart tax table.
It only preserves the smallest load-bearing truth about whether a supposedly resumable return was still warm in memory, replayed from saved state, or restarted cold.

## Countermodels / probes

1. **Automatic resume is not automatically in-memory**
   - A platform may say resume while also running the startup script again on another node.
   - Probe: if the public basis depends on loading checkpoints or new Pod creation, do not label it `in-memory-continuation`.

2. **Checkpoint-backed replay is not the same as cold restart**
   - Replaying saved weights, optimizer state, or other persisted execution data is still materially different from starting from scratch.
   - Probe: if saved state is explicitly loaded on return, keep `checkpoint-backed-replay` even when some progress since the last save was lost.

3. **Replacement Pods can masquerade as continuation**
   - Kubernetes may preserve a Job object while deleting the running Pod and creating a new one later.
   - Probe: if the returning unit is a replacement Pod with a new UID and no public saved-state basis, that is not live continuation.

4. **Resumable aftercare and resumption basis are different witnesses**
   - Work can remain resumable rather than terminal while still returning by cold restart.
   - Probe: require prior refresh-scope-axis-remediation-displacement-aftercare evidence before this witness is applied.

## Design consequences

- DelayBasin can now keep the word resume from flattening live suspension, checkpoint replay, and fresh restart into one pseudo-equivalent continuity story.
- GPUstorming gets one explicit place to record whether lower-priority work really stayed warm or only came back through saved state or fresh relaunch.
- The archive can now say that a return path stayed nonterminal without overstating how much execution state actually survived.
- Stronger warm-state credit, locality-carry, or checkpoint-solvency stories stay quarantined until repeated overflow rather than slipping into canon by atmosphere.

## Overflow test

Reopen this compact witness only if later revisions repeatedly need explicit public accounting for replay fidelity inside checkpoint-backed return, exact-versus-bounded progress loss, node-local warmth or locality carry, or standing compensation rules for colder restarts that one bounded refresh-scope-axis-remediation-displacement-resumption-basis witness cannot honestly absorb.

## Transformer-facing implication

A later pass should not treat every nonterminal return path as equally warm. Preserve the smallest token that says whether the present return basis is `in-memory-continuation`, `checkpoint-backed-replay`, `cold-restart-after-displacement`, or honestly `mixed-refresh-scope-axis-remediation-displacement-resumption-basis`, and quarantine stronger warm-state-credit ambitions until repeated overflow makes them unavoidable.
