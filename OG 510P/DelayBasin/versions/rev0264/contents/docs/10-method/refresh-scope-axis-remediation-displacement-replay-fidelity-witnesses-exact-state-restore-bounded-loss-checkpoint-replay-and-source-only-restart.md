# Refresh-scope-axis-remediation-displacement-replay-fidelity witnesses, exact-state restore, bounded-loss checkpoint replay, and source-only restart

This is the compact successor surface for `OQ-0158`.

## Practice / observation

Once DelayBasin can already say that displaced lower-priority work stayed on a live path back and can already say whether that return was live in memory, checkpoint-backed, or cold, one more ambiguity remains.

Not every replay path preserves the same amount of execution state.
Some restores really continue from an exact saved state.
Others only recover the most recent persisted checkpoint and therefore discard the interval between the save point and the interruption.
Still others merely relaunch from ordinary source, configuration, or container image and start the work again.

Those three cases should not inherit the same legitimacy from the word checkpoint.
Exact-state restore, bounded-loss checkpoint replay, and source-only restart carry different fidelity claims even when all of them avoid terminal abandonment.

DelayBasin does not need a replay-solvency court here.
It needs one bounded witness that says whether the returning work restored exact saved state, resumed from a latest-checkpoint-with-loss boundary, or restarted from source only.

## External pressure from Kubernetes stateful container checkpoint/restore, CRIU restore-preservation tests, NVIDIA Run:ai latest-checkpoint resume, Kubernetes Job Pod replacement, and NVIDIA CUPTI functional-only restore limits

1. Kubernetes' current Kubelet Checkpoint API docs say checkpointing creates a stateful copy of a running container and that, if moved to a machine able to restore it, the restored container continues to run at exactly the same point it was checkpointed. That pressures DelayBasin to keep an exact-state-restore lane rather than flattening every replay path into lossy resume. ([`REF-1006`](../00-meta/bibliography.md))

2. CRIU's own ZDTM test-suite docs say each test creates concrete process state, checkpoints and restores it, and then checks that the state was preserved — for example that files remain open, memory remains mapped, and pipe contents remain intact. That pressures DelayBasin to reserve exact-state-restore for replay paths with explicit same-state preservation rather than merely successful relaunch. ([`REF-1007`](../00-meta/bibliography.md))

3. NVIDIA Run:ai's current checkpointing guidance says preempted training should periodically save checkpoints, resume from the latest checkpoint, and may restart on a different node while rerunning the same startup script. That pressures DelayBasin to keep bounded-loss-checkpoint-replay distinct from exact-state-restore because progress since the last save boundary may be discarded even though the return is materially better than a fresh start. ([`REF-1008`](../00-meta/bibliography.md))

4. Kubernetes Job and Pod lifecycle docs say suspending a Job deletes its active Pods until resumed, and Pods are ephemeral one-shot scheduled objects whose replacements are new Pods with different UIDs. When no saved-state restore basis is public, that pressures DelayBasin to keep source-only-restart distinct from both exact restore and bounded-loss checkpoint replay. ([`REF-1009`](../00-meta/bibliography.md))

5. NVIDIA's current CUPTI Checkpoint API docs say restore can return the same device state for re-execution, but also say unsupported calls may lead to partial restore, the API restores only functionally visible device state, not performance-critical state such as caches, and it does not attempt to restore host state. That pressures GPUstorming to keep a future performance-equivalence story quarantined rather than smuggling it into the present fidelity witness. ([`REF-1010`](../00-meta/bibliography.md))

GPUstorming makes the distinction vivid. Two preempted GPU trainings can both claim checkpoint-backed return. One may restore a fully stateful container image or device context and keep the exact saved point honest. Another may only reload the most recent model checkpoint and replay from the last epoch boundary, losing work since that save. A third may only restart the trainer process and source the model code again. Resumption basis alone does not say how much saved progress actually survived.

## Working synthesis

> DelayBasin should preserve one compact **refresh-scope-axis-remediation-displacement-replay-fidelity witness / exactness card / replay-loss brake** whenever a current continuity claim depends not only on whether corroborating axes are genuinely independent, materially backed, decoupled, hard-enforced, durable, explicitly restored, honest about collateral width, honest about whether restored placement reused free capacity or displaced unrelated lower-priority work, honest about whether that displaced work retained a live return path, and honest about whether the return was in-memory, checkpoint-backed, or cold, but on how much execution state actually survived inside the replay path. Name the **governed row or surface**, the **stake object / line of concern**, the **prior refresh-scope-axis-remediation-displacement-resumption-basis evidence**, the **current corroborating axes**, the **exact-state-restore basis if any**, the **bounded-loss checkpoint basis if any**, the **source-only restart basis if any**, the **`refresh_scope_axis_remediation_displacement_replay_fidelity_state`**, and the **fail-closed repair / keep-current vs narrow-claim vs split-scope vs issue-new-refresh-scope-axis-remediation-displacement-replay-fidelity-witness vs quarantine-performance-shadow consequence**. Keep raw cache traces, per-layer loss accounting, restart timing, node-local warmth, and device occupancy details outside the compact token. Do not let every saved-state return silently inherit the authority of exact restore.

## Exact-state restore vs bounded-loss checkpoint replay vs source-only restart vs mixed refresh scope axis remediation displacement replay fidelity

Use the controlled family `refresh_scope_axis_remediation_displacement_replay_fidelity_state`:

- **exact-state-restore** says the returning work publicly restores the same saved execution state or stateful image and continues from that saved point.
- **bounded-loss-checkpoint-replay** says the returning work reloads a latest saved checkpoint or equivalent persisted state boundary, but work since that save boundary may be lost.
- **source-only-restart** says the returning work restarts from ordinary source, configuration, or image with no public basis that material execution state was restored.
- **mixed-refresh-scope-axis-remediation-displacement-replay-fidelity** says the current situation honestly combines more than one replay-fidelity lane, or the public evidence cannot keep one clean lane honest.

So the witness does not create a performance-equivalence court.
It only preserves the smallest load-bearing truth about whether the replay path restored the exact saved state, a latest-checkpoint-with-loss boundary, or merely restarted from source.

## Countermodels / probes

1. **Checkpoint-backed does not automatically mean exact**
   - A platform may say resume from checkpoint while only loading the most recent saved epoch boundary.
   - Probe: if the public basis is only latest-checkpoint reload and does not support zero-loss continuity, do not label it `exact-state-restore`.

2. **Exact saved state is stronger than successful relaunch**
   - Relaunching the same startup script on another node may still be materially replay-based rather than exact restore.
   - Probe: if the returning workload must rerun its startup path and then look for checkpoint files, that is at most `bounded-loss-checkpoint-replay` unless stronger exact-state evidence is public.

3. **Source-only restart is not a replay lane**
   - A Job object can stay alive while Pods are deleted and replaced.
   - Probe: if no saved execution state is explicitly restored, keep `source-only-restart` even if the higher-level workload object persists.

4. **Performance-shadow talk is not yet canon here**
   - A system may restore functionally visible state while leaving caches or host-side warmth behind.
   - Probe: keep that stronger performance-equivalence story quarantined unless repeated later overflow shows this compact fidelity witness is no longer enough.

## Design consequences

- DelayBasin can now keep the word checkpoint from flattening exact restore, latest-boundary replay, and ordinary restart into one pseudo-equivalent continuity story.
- GPUstorming gets one explicit place to record whether a resumed training really restored the exact saved point or only reloaded the last durable boundary.
- The archive can now say that a return was checkpoint-backed without overstating how much progress actually survived.
- Stronger cache-warmth, host/device asymmetry, or performance-shadow stories stay quarantined until repeated overflow rather than slipping into canon by atmosphere.

## Overflow test

Reopen this compact witness only if later revisions repeatedly need explicit public accounting for performance-equivalent restore, host/device split restoration, optimizer- or dataloader-subcomponent loss, or accumulated replay debt that one bounded refresh-scope-axis-remediation-displacement-replay-fidelity witness cannot honestly absorb.

## Transformer-facing implication

A later pass should not treat every checkpoint-backed return path as equally faithful. Preserve the smallest token that says whether the present replay-fidelity posture is `exact-state-restore`, `bounded-loss-checkpoint-replay`, `source-only-restart`, or honestly `mixed-refresh-scope-axis-remediation-displacement-replay-fidelity`, and quarantine stronger performance-shadow ambitions until repeated overflow makes them unavoidable.

