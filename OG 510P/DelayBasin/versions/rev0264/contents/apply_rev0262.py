from __future__ import annotations

import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent

REV = 'rev0262'
PREV = 'rev0261'
STAMP = '2026.03.28.03.06'
CREATED_AT = '2026-03-28T03:06:00-04:00'
SLUG = 'resumptionbasis-warmq-replaycarry-memoryglass'
BUNDLE = f'DelayBasin-{REV}-{STAMP}-{SLUG}.zip'
SUMMARY_HIGHLIGHT = 'replaycarry'
CODENAME = 'memoryglass'

NEW_DOC = 'docs/10-method/refresh-scope-axis-remediation-displacement-resumption-basis-witnesses-in-memory-continuation-checkpoint-backed-replay-and-cold-restart.md'
NEW_CHECKER = 'tools/check_refresh_scope_axis_remediation_displacement_resumption_basis_witness_contract.py'
QWS = 'QWS-0240'
QWS_LABEL = 'warm-state credit / checkpoint solvency / locality carry'
CL = 'CL-0155'
RS = 'RS-0164'
OQ = 'OQ-0157'
NEXT_OQ = 'OQ-0158'
PP = 'PP-0115'
AP = 'AP-0156'
OB = 'OB-0157'
AS = 'AS-0161'
FP = 'FP-0161'
TL = 'TL-0167'
FT = 'FT-0164'
RT = 'RT-0151'
FB = 'FB-0158'
FAMILY = 'refresh_scope_axis_remediation_displacement_resumption_basis_state'
ALLOWED = [
    'in-memory-continuation',
    'checkpoint-backed-replay',
    'cold-restart-after-displacement',
    'mixed-refresh-scope-axis-remediation-displacement-resumption-basis',
]
EXCLUDED = [
    'resume-means-same-state',
    'checkpoint-means-lossless',
    'new-pod-means-same-run',
    'resumption-basis-ish',
]


def read(rel: str) -> str:
    return (ROOT / rel).read_text(encoding='utf-8')


def write(rel: str, text: str) -> None:
    (ROOT / rel).write_text(text, encoding='utf-8')


def loadj(rel: str):
    return json.loads(read(rel))


def dumpj(rel: str, obj) -> None:
    write(rel, json.dumps(obj, indent=2, ensure_ascii=False) + '\n')


def append_if_missing(rel: str, text: str) -> None:
    current = read(rel)
    if text not in current:
        if not current.endswith('\n'):
            current += '\n'
        current += text
        if not current.endswith('\n'):
            current += '\n'
        write(rel, current)


def replace_once(rel: str, old: str, new: str) -> None:
    text = read(rel)
    if new in text:
        return
    if old not in text:
        raise RuntimeError(f'old block not found in {rel}')
    write(rel, text.replace(old, new, 1))


def insert_after(rel: str, needle: str, addition: str) -> None:
    text = read(rel)
    if addition in text:
        return
    if needle not in text:
        raise RuntimeError(f'needle not found in {rel}: {needle}')
    write(rel, text.replace(needle, needle + addition, 1))


def append_item(rel: str, item: dict) -> None:
    obj = loadj(rel)
    items = obj['items']
    if any(existing['id'] == item['id'] for existing in items):
        return
    items.append(item)
    dumpj(rel, obj)


new_doc_text = """# Refresh-scope-axis-remediation-displacement-resumption-basis witnesses, in-memory continuation, checkpoint-backed replay, and cold restart

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
"""

write(NEW_DOC, new_doc_text)

write(NEW_CHECKER, "from packet_contract_common import require_named_refresh_scope_axis_branch_witness_packet_and_vocabulary\n\nrequire_named_refresh_scope_axis_branch_witness_packet_and_vocabulary(\"refresh_scope_axis_remediation_displacement_resumption_basis_witness_contract\")\n\nprint(\"check_refresh_scope_axis_remediation_displacement_resumption_basis_witness_contract: OK\")\n")

bibliography_addition = """
- `REF-0999` — Slurm Workload Manager, **slurm.conf** (accessed 2026-03-28)
  - URL: https://slurm.schedmd.com/slurm.conf.html
  - Load-bearing use: Slurm says `SUSPEND` later resumes preempted jobs, that suspended jobs still use memory on their allocated nodes, and that suspended jobs do not release GRES, which pressures DelayBasin to keep true in-memory continuation distinct from replay or restart.

- `REF-1000` — Slurm Workload Manager, **sbatch** (accessed 2026-03-28)
  - URL: https://slurm.schedmd.com/sbatch.html
  - Load-bearing use: Slurm says suspended jobs still reside in memory, which pressures DelayBasin to treat gang-scheduled suspension as a materially warmer continuation class than replay or fresh restart.

- `REF-1001` — Slurm Workload Manager, **Generic Resource (GRES) Scheduling** (accessed 2026-03-28)
  - URL: https://slurm.schedmd.com/gres.html
  - Load-bearing use: Slurm says suspended jobs do not release their GRES, which pressures GPUstorming to recognize a live in-memory continuation class rather than flattening all returns into replay.

- `REF-1002` — David Lipari, **The SLURM Scheduler Design** (SchedMD / LLNL presentation, accessed 2026-03-28)
  - URL: https://slurm.schedmd.com/slurm_ug_2012/SUG-2012-Scheduling.pdf
  - Load-bearing use: the scheduler design material says `scontrol checkpoint vacate` releases nodes back to the pool and restart relies on a new job being scheduled, which pressures DelayBasin to distinguish checkpoint-backed replay from live in-memory continuation.

- `REF-1003` — Kubernetes Documentation, **Jobs** (accessed 2026-03-28)
  - URL: https://kubernetes.io/docs/concepts/workloads/controllers/job/
  - Load-bearing use: Kubernetes says suspending a Job deletes its active Pods until resumed, sends SIGTERM to running Pods, and may require saving progress for later, which pressures DelayBasin to distinguish replay-or-restart return from live in-memory continuation.

- `REF-1004` — Kubernetes Documentation, **Pod Lifecycle** (accessed 2026-03-28)
  - URL: https://kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/
  - Load-bearing use: Kubernetes says Pods are ephemeral, are scheduled only once, and replacements are new Pods with different UIDs that are not rescheduled to a different node, which pressures DelayBasin to recognize cold restart or replacement replay rather than same-object continuation.

- `REF-1005` — NVIDIA Run:ai Documentation, **Best Practices: Checkpointing Preemptible Training Workloads** (accessed 2026-03-28)
  - URL: https://run-ai-docs.nvidia.com/self-hosted/workloads-in-nvidia-run-ai/using-training/checkpointing-preemptible-workloads
  - Load-bearing use: Run:ai says preempted workloads can automatically resume, may land on a different node, should save checkpoints on shared storage, and on resume rerun the startup script and explicitly load saved checkpoints, which pressures DelayBasin to distinguish checkpoint-backed replay from both live in-memory continuation and cold restart.
"""
append_if_missing('docs/00-meta/bibliography.md', bibliography_addition)

text = read('docs/20-constitution/open-question-registry.md')
old_oq = """- `OQ-0157` — what remediation-displacement-resumption-basis witness distinguishes in-memory continuation from checkpoint-backed replay and cold restart after displacement?
  - Why it matters: if DelayBasin cannot separate live resume, replay-from-checkpoint, and fresh restart, later sessions may over-credit resumable displacement that actually lost substantial work.
  - Current posture: unresolved
"""
new_oq = """- `OQ-0157` — what remediation-displacement-resumption-basis witness distinguishes in-memory continuation from checkpoint-backed replay and cold restart after displacement?
  - Why it matters: if DelayBasin cannot separate live resume, replay-from-checkpoint, and fresh restart, later sessions may over-credit resumable displacement that actually lost substantial work.
  - Current posture: resolved by `RS-0164` via `docs/10-method/refresh-scope-axis-remediation-displacement-resumption-basis-witnesses-in-memory-continuation-checkpoint-backed-replay-and-cold-restart.md`; reopen only if the compact refresh-scope-axis-remediation-displacement-resumption-basis witness proves insufficient and stronger replay-fidelity or warm-state governance is honestly required

- `OQ-0158` — what remediation-displacement-replay-fidelity witness distinguishes exact-state restore from bounded-loss checkpoint replay and source-only restart?
  - Why it matters: if DelayBasin cannot separate exact restore from truncated replay and source-only restart, later sessions may still over-credit checkpoint-backed return that discards meaningful progress.
  - Current posture: unresolved
"""
replace_once('docs/20-constitution/open-question-registry.md', old_oq, new_oq)

old_traj = """113. Determine what remediation-displacement-resumption-basis witness distinguishes in-memory continuation from checkpoint-backed replay and cold restart after displacement.

A fresh extension is that once aftercare is explicit, DelayBasin may next need to say what kind of return path the displaced work actually retained. Suspended work resumed in memory, checkpoint-backed replay, and cold restart after eviction all count as not-yet-abandoned in one weak sense, but they do not preserve the same continuity.
- `OQ-0157` — what remediation-displacement-resumption-basis witness distinguishes in-memory continuation from checkpoint-backed replay and cold restart after displacement?
  - Why it matters: if DelayBasin cannot separate live resume, replay-from-checkpoint, and fresh restart, later sessions may over-credit resumable displacement that actually lost substantial work.
  - Current posture: resolved by `RS-0164` via `docs/10-method/refresh-scope-axis-remediation-displacement-resumption-basis-witnesses-in-memory-continuation-checkpoint-backed-replay-and-cold-restart.md`; reopen only if the compact refresh-scope-axis-remediation-displacement-resumption-basis witness proves insufficient and stronger replay-fidelity or warm-state governance is honestly required

114. Determine what remediation-displacement-replay-fidelity witness distinguishes exact-state restore from bounded-loss checkpoint replay and source-only restart.

A fresh extension is that once resumption basis is explicit, DelayBasin may next need to say how much meaningful execution state actually survived inside the replay path. Otherwise checkpoint-backed return may still silently inherit the authority of exact restore.
- `OQ-0158` — what remediation-displacement-replay-fidelity witness distinguishes exact-state restore from bounded-loss checkpoint replay and source-only restart?
  - Why it matters: if DelayBasin cannot separate exact restore from truncated replay and source-only restart, later sessions may still over-credit checkpoint-backed return that discards meaningful progress.
  - Current posture: unresolved
"""
new_traj = """113. Determine what remediation-displacement-resumption-basis witness distinguishes in-memory continuation from checkpoint-backed replay and cold restart after displacement.

A fresh extension is that once aftercare is explicit, DelayBasin may next need to say how warm or cold the returning execution actually was. Otherwise every nonterminal return path may silently inherit the authority of live in-memory continuation.
- `OQ-0157` — what remediation-displacement-resumption-basis witness distinguishes in-memory continuation from checkpoint-backed replay and cold restart after displacement?
  - Why it matters: if DelayBasin cannot separate live resume, replay-from-checkpoint, and fresh restart, later sessions may over-credit resumable displacement that actually lost substantial work.
  - Current posture: resolved by `RS-0164` via `docs/10-method/refresh-scope-axis-remediation-displacement-resumption-basis-witnesses-in-memory-continuation-checkpoint-backed-replay-and-cold-restart.md`; reopen only if the compact refresh-scope-axis-remediation-displacement-resumption-basis witness proves insufficient and stronger replay-fidelity or warm-state governance is honestly required

114. Determine what remediation-displacement-replay-fidelity witness distinguishes exact-state restore from bounded-loss checkpoint replay and source-only restart.

A fresh extension is that once resumption basis is explicit, DelayBasin may next need to say how much meaningful execution state actually survived inside the replay path. Otherwise checkpoint-backed return may still silently inherit the authority of exact restore.
- `OQ-0158` — what remediation-displacement-replay-fidelity witness distinguishes exact-state restore from bounded-loss checkpoint replay and source-only restart?
  - Why it matters: if DelayBasin cannot separate exact restore from truncated replay and source-only restart, later sessions may still over-credit checkpoint-backed return that discards meaningful progress.
  - Current posture: unresolved
"""
replace_once('docs/00-meta/trajectory-map.md', old_traj, new_traj)

claim_addition = """

- `CL-0155` — Archive continuity may improve when DelayBasin preserves one compact **refresh-scope-axis-remediation-displacement-resumption-basis witness / warmth card / replay brake** whenever a current continuity claim depends not only on whether corroborating axes are genuinely independent, materially backed, decoupled under perturbation, hard-enforced, durable, explicitly restored, honest about collateral width, honest about whether restored placement reused free capacity or displaced unrelated lower-priority work, and honest about whether the displaced work retained a live path back, but on how that work actually came back: name the **governed row or surface**, the **stake object / line of concern**, the **prior refresh-scope-axis-remediation-displacement-aftercare evidence**, the **current corroborating axes**, the **in-memory continuation basis if any**, the **checkpoint-backed replay basis if any**, the **cold-restart basis if any**, the **refresh_scope_axis_remediation_displacement_resumption_basis_state**, and the **fail-closed repair** rather than letting every nonterminal return silently inherit the authority of live in-memory continuation.
  - Status: speculative but central
  - Wired docs: `docs/10-method/refresh-scope-axis-remediation-displacement-resumption-basis-witnesses-in-memory-continuation-checkpoint-backed-replay-and-cold-restart.md`, `docs/20-constitution/open-question-registry.md`, `docs/20-constitution/prompt-pair-registry.md`, `docs/50-promptcraft/prompt-pairs.md`, `docs/00-meta/llm-runbook.md`, `WITNESS-VOCABULARY.json`, `REVISION-RECEIPT.json`
"""
append_if_missing('docs/20-constitution/claim-registry.md', claim_addition)

prompt_reg_addition = """
- `PP-0115` — Name whether a nonterminal return stayed in memory, replayed checkpoints, or restarted cold
  - Goal: keep resumable aftercare from silently inheriting live-continuation authority by requiring explicit prior remediation-displacement-aftercare evidence, current corroborating axes, in-memory basis, checkpoint basis, cold-restart basis, `refresh_scope_axis_remediation_displacement_resumption_basis_state`, and fail-closed repair before later passes call the returning work equally resumed.
  - Canonical text: `docs/50-promptcraft/prompt-pairs.md#pp-0115--name-whether-a-nonterminal-return-stayed-in-memory-replayed-checkpoints-or-restarted-cold`
"""
append_if_missing('docs/20-constitution/prompt-pair-registry.md', prompt_reg_addition)

prompt_pairs_addition = """

## PP-0115 — Name whether a nonterminal return stayed in memory, replayed checkpoints, or restarted cold

**Opening prompt**

```text
Read the latest DelayBasin archive and inspect whether the current revision should also materialize one compact refresh-scope-axis-remediation-displacement-resumption-basis witness for honest warm-vs-replay-vs-cold return.

Focus only on cases where the corroborating axes already look genuinely independent, materially backed, decoupled under perturbation, hard-enforced, durable, explicit about who restored the decoupling, honest about how wide the remediation was, honest about whether restored placement reused free capacity or only came back by displacing unrelated lower-priority work, and honest about whether the displaced lower-priority work stayed nonterminal. The missing question is how that work actually returned.

If yes, preserve exactly one small witness that:
- names the governed row or surface,
- names the stake object / line of concern,
- names the prior refresh-scope-axis-remediation-displacement-aftercare evidence,
- names the current corroborating axes,
- names the in-memory continuation basis if any,
- names the checkpoint-backed replay basis if any,
- names the cold-restart basis if any,
- names the `refresh_scope_axis_remediation_displacement_resumption_basis_state` / whether this is in-memory-continuation, checkpoint-backed-replay, cold-restart-after-displacement, or mixed-refresh-scope-axis-remediation-displacement-resumption-basis,
- states what stronger surfaces still outrank the witness,
- and states the fail-closed repair / keep-current vs narrow-claim vs split-scope vs issue-new-refresh-scope-axis-remediation-displacement-resumption-basis-witness vs quarantine-warm-state-credit consequence if the present continuity claim is not actually supported by the claimed return basis.

Do not use refresh-scope-axis-remediation-displacement-resumption-basis as a standing replay-fidelity board or warmth market. Use this prompt pair only where axis independence, materiality, coupling, enforcement, durability, remediation provenance, remediation collateral, remediation capacity source, and remediation displacement aftercare are already established and the missing question is whether the displaced work returned live in memory, via saved-state replay, or via cold restart.
```

**Continuation prompt**

```text
Continue the refresh-scope-axis-remediation-displacement-resumption-basis pass with one high-leverage return-basis clarification only. Prefer the smallest witness that says what governed row is still being justified, what stake object is supposedly widened, what prior refresh-scope-axis-remediation-displacement-aftercare evidence exists, what current corroborating axes exist, what in-memory continuation basis if any now exists, what checkpoint-backed replay basis if any now exists, what cold-restart basis if any now exists, what `refresh_scope_axis_remediation_displacement_resumption_basis_state` is honest, what stronger surfaces still outrank the witness, and what keep-current, narrow-claim, split-scope, issue-new-refresh-scope-axis-remediation-displacement-resumption-basis-witness, quarantine, or recover-resync consequence follows if the present return basis is in-memory-continuation, checkpoint-backed-replay, cold-restart-after-displacement, or mixed-refresh-scope-axis-remediation-displacement-resumption-basis. Run `make lint` and package the release.
```

Use `docs/10-method/refresh-scope-axis-remediation-displacement-resumption-basis-witnesses-in-memory-continuation-checkpoint-backed-replay-and-cold-restart.md` when the live question is how a supposedly resumable displaced workload actually came back.
"""
append_if_missing('docs/50-promptcraft/prompt-pairs.md', prompt_pairs_addition)

insert_after('docs/00-meta/llm-runbook.md',
             'Use `docs/10-method/refresh-scope-axis-remediation-displacement-aftercare-witnesses-resumable-displacement-terminal-displacement-and-mixed-aftercare.md` when the live question is what happened afterward to the lower-priority work that paid the preemption bill: whether it stayed on a live path back or was terminally sacrificed.\n',
             'Use `docs/10-method/refresh-scope-axis-remediation-displacement-resumption-basis-witnesses-in-memory-continuation-checkpoint-backed-replay-and-cold-restart.md` when the live question is how a supposedly nonterminal displaced workload actually returned: still live in memory, by replaying saved checkpoints, or only by cold restart.\n')

qws_addition = """
## QWS-0240 — Some continuations may eventually need a warm-state credit / checkpoint solvency / locality carry rather than only a compact refresh-scope-axis-remediation-displacement-resumption-basis witness

### Claim
Some later continuations may need stronger public machinery for how warm a return really was inside the checkpoint-backed path, whether locality or cache warmth materially changed the continuity bill, and whether repeated colder restarts should accumulate an explicit continuity debt. One compact in-memory-vs-replay-vs-cold witness may eventually stop being enough.

### What follows if true
- DelayBasin may eventually need an explicit way to distinguish exact-state restore, bounded-loss replay, and merely nominal replay that preserved little but a label.
- The archive might need a bounded warm-state credit or checkpoint-solvency layer if later revisions repeatedly compare several nonterminal returns whose practical continuity differs because one comes back hot and another comes back cold on another node.

### What would count against it
- Several later revisions keep fitting cleanly inside one compact refresh-scope-axis-remediation-displacement-resumption-basis witness without repeated confusion about replay quality, node locality, or warm-state carry.
- The archive almost never needs public reasoning about checkpoint quality once in-memory continuation, checkpoint-backed replay, and cold restart are already separated.

### Why it stays quarantined
The current evidence justifies one bounded witness for in-memory continuation versus checkpoint-backed replay versus cold restart. It does not yet justify a standing warm-state credit board, checkpoint-solvency ledger, or locality-carry market.
"""
append_if_missing('docs/90-quarantine/wild-speculations-2026-03-08.md', qws_addition)

vocab = loadj('WITNESS-VOCABULARY.json')
vocab['revision'] = REV
vocab['families'][FAMILY] = {
    'allowed': ALLOWED,
    'surfaces': ['WITNESS-VOCABULARY.json', 'REVISION-RECEIPT.json', NEW_DOC],
    'excluded_synonyms': EXCLUDED,
    'comparability_budget': 'refresh-scope-axis-remediation-displacement-resumption-basis truth is compared by token; the compact witness says whether displaced work returned as live in-memory continuation, checkpoint-backed replay, cold restart, or an honest mix while raw checkpoint intervals, replay runtimes, cache warmth, and scheduler traces stay in surrounding prose',
}
dumpj('WITNESS-VOCABULARY.json', vocab)

insert_after('tools/packet_contract_common.py',
             '"refresh_scope_axis_remediation_displacement_aftercare_witness_contract": refresh_scope_axis_branch_spec(\n    doc_path="docs/10-method/refresh-scope-axis-remediation-displacement-aftercare-witnesses-resumable-displacement-terminal-displacement-and-mixed-aftercare.md",\n    title="Refresh-scope-axis-remediation-displacement-aftercare witnesses, resumable displacement, terminal displacement, and mixed aftercare",\n    oq_id="OQ-0156",\n    external_pressure_heading="## External pressure from Slurm suspend, requeue, and cancel modes, Kubernetes Jobs suspend/resume and disruption handling, Kueue requeue and deactivation limits, and NVIDIA Run:ai automatic resume with checkpointing",\n    comparison_heading="## Resumable displacement aftercare vs terminal displacement aftercare vs mixed refresh scope axis remediation displacement aftercare",\n    runbook_ref="refresh-scope-axis-remediation-displacement-aftercare-witnesses-resumable-displacement-terminal-displacement-and-mixed-aftercare.md",\n    prompt_id="PP-0114",\n    prompt_needles=["Use `docs/10-method/refresh-scope-axis-remediation-displacement-aftercare-witnesses-resumable-displacement-terminal-displacement-and-mixed-aftercare.md`", "resumable-displacement-aftercare, terminal-displacement-aftercare, or mixed-refresh-scope-axis-remediation-displacement-aftercare"],\n    claim_id="CL-0154",\n    resolution_id="RS-0163",\n    trajectory_oq_id="OQ-0157",\n    qws_id="QWS-0239",\n    qws_label="resume credit / checkpoint escrow / restart tax",\n    changelog_needles=["refresh-scope-axis-remediation-displacement-aftercare-witnesses-resumable-displacement-terminal-displacement-and-mixed-aftercare.md", "check_refresh_scope_axis_remediation_displacement_aftercare_witness_contract.py"],\n    family="refresh_scope_axis_remediation_displacement_aftercare_state",\n    allowed=["resumable-displacement-aftercare", "terminal-displacement-aftercare", "mixed-refresh-scope-axis-remediation-displacement-aftercare"],\n    excluded=["requeue-means-paid-back", "suspend-means-free", "cancel-means-minor", "aftercare-ish"],\n),\n',
             '\n"refresh_scope_axis_remediation_displacement_resumption_basis_witness_contract": refresh_scope_axis_branch_spec(\n    doc_path="docs/10-method/refresh-scope-axis-remediation-displacement-resumption-basis-witnesses-in-memory-continuation-checkpoint-backed-replay-and-cold-restart.md",\n    title="Refresh-scope-axis-remediation-displacement-resumption-basis witnesses, in-memory continuation, checkpoint-backed replay, and cold restart",\n    oq_id="OQ-0157",\n    external_pressure_heading="## External pressure from Slurm suspend and checkpoint-restart paths, Kubernetes Job suspension and Pod replacement, and NVIDIA Run:ai checkpoint-driven preemptible resume",\n    comparison_heading="## In-memory continuation vs checkpoint-backed replay vs cold restart after displacement vs mixed refresh scope axis remediation displacement resumption basis",\n    runbook_ref="refresh-scope-axis-remediation-displacement-resumption-basis-witnesses-in-memory-continuation-checkpoint-backed-replay-and-cold-restart.md",\n    prompt_id="PP-0115",\n    prompt_needles=["Use `docs/10-method/refresh-scope-axis-remediation-displacement-resumption-basis-witnesses-in-memory-continuation-checkpoint-backed-replay-and-cold-restart.md`", "in-memory-continuation, checkpoint-backed-replay, cold-restart-after-displacement, or mixed-refresh-scope-axis-remediation-displacement-resumption-basis"],\n    claim_id="CL-0155",\n    resolution_id="RS-0164",\n    trajectory_oq_id="OQ-0158",\n    qws_id="QWS-0240",\n    qws_label="warm-state credit / checkpoint solvency / locality carry",\n    changelog_needles=["refresh-scope-axis-remediation-displacement-resumption-basis-witnesses-in-memory-continuation-checkpoint-backed-replay-and-cold-restart.md", "check_refresh_scope_axis_remediation_displacement_resumption_basis_witness_contract.py"],\n    family="refresh_scope_axis_remediation_displacement_resumption_basis_state",\n    allowed=["in-memory-continuation", "checkpoint-backed-replay", "cold-restart-after-displacement", "mixed-refresh-scope-axis-remediation-displacement-resumption-basis"],\n    excluded=["resume-means-same-state", "checkpoint-means-lossless", "new-pod-means-same-run", "resumption-basis-ish"],\n),\n')

release_lib = read('tools/release_hygiene_lib.py')
if 'def extract_revision_from_changelog' not in release_lib:
    release_lib += """

def extract_revision_from_changelog(changelog_text: str) -> str:
    match = re.search(r"(rev\\d{4})", changelog_text)
    if not match:
        raise ValueError("CHANGELOG.md missing rev header")
    return match.group(1)


def build_release_manifest(revision: str, timestamp: str, slug: str) -> dict[str, str]:
    return {
        "project": "DelayBasin",
        "revision": revision,
        "timestamp": timestamp,
        "slug": slug,
        "bundle": build_bundle_name(revision, timestamp, slug),
    }
"""
    write('tools/release_hygiene_lib.py', release_lib)

package_release = read('tools/package_release.py')
package_release = package_release.replace(
    'from release_hygiene_lib import build_bundle_name, should_skip_release_path\n',
    'from release_hygiene_lib import build_bundle_name, build_release_manifest, extract_revision_from_changelog, should_skip_release_path\n',
)
package_release = package_release.replace(
    'changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")\nm = re.search(r"(rev\\d{4})", changelog)\nif not m:\n    raise SystemExit("CHANGELOG.md missing rev header")\nrev = m.group(1)\n\nbundle_name = build_bundle_name(rev, args.timestamp, args.slug)\nbundle_path = ROOT.parent / bundle_name\n\nmanifest = {\n    "project": "DelayBasin",\n    "revision": rev,\n    "timestamp": args.timestamp,\n    "slug": args.slug,\n    "bundle": bundle_name,\n}\n(ROOT / "RELEASE-MANIFEST.json").write_text(json.dumps(manifest, indent=2) + "\\n", encoding="utf-8")\n',
    'changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")\nrev = extract_revision_from_changelog(changelog)\n\nmanifest = build_release_manifest(rev, args.timestamp, args.slug)\nbundle_name = manifest["bundle"]\nbundle_path = ROOT.parent / bundle_name\n(ROOT / "RELEASE-MANIFEST.json").write_text(json.dumps(manifest, indent=2) + "\\n", encoding="utf-8")\n',
)
write('tools/package_release.py', package_release)

app_item = {
    'id': AP,
    'title': 'the refresh-scope-axis-remediation-displacement-resumption-basis witness stays smaller than a warm-state-credit ledger',
    'state': 'gated',
    'question': 'when should DelayBasin treat nonterminal displaced work with one compact remediation-displacement-resumption-basis witness instead of promoting broader replay-fidelity or warmth accounting?',
    'applies_when': [
        'a revision already has a row whose current claim depends on corroborating axes that are already judged genuinely independent, materially backed, decoupled under perturbation, hard-enforced, durable, explicitly restored, honest about collateral width, honest about whether restored placement reused free capacity or displaced unrelated lower-priority work, and honest about whether displaced work stayed nonterminal',
        'later passes still need to distinguish in-memory-continuation, checkpoint-backed-replay, cold-restart-after-displacement, or mixed-refresh-scope-axis-remediation-displacement-resumption-basis posture',
        'one compact successor surface plus the existing admitted refresh-scope-axis-remediation-displacement-aftercare and related scheduler surfaces still keeps return-basis truth honest without standing replay-fidelity or warm-state machinery',
    ],
    'does_not_apply_when': [
        'the archive honestly requires standing governance over exact-state-restore versus bounded-loss checkpoint replay, locality carry, warm-state credit, or checkpoint solvency',
        'the questioned surface is not really about how nonterminal displaced work returned',
    ],
    'budget': 'one compact refresh-scope-axis-remediation-displacement-resumption-basis witness plus one resolution of OQ-0157; no warm-state credit ledger',
    'negative_transfer_budget': 'do not treat every nonterminal return as if it preserved the same amount of live execution state',
    'origin_revision': REV,
    'discharge': 'reopen-only-if-refresh-scope-axis-remediation-displacement-resumption-basis-overflows',
    'action_lane': 'keep-compact',
    'gate_class': 'concrete-evidence',
    'witness_surface': f'APPLICABILITY-LEDGER.json#{AP}',
    'applicability_state': 'gated',
    'repair': 'ordinary-continuation',
    'matched_budget': 'one compact witness foregrounding in-memory versus checkpoint-backed versus cold return without widening into replay-fidelity accounting',
    'revision': REV,
    'target_objective': 'keep return-basis truth honest without inflating a general warm-state-credit layer',
    'carry_object': 'refresh-scope-axis-remediation-displacement-resumption-basis witness',
    'open_question': NEXT_OQ,
    'applicability_conditions': [
        'a revision already has a row whose current claim depends on corroborating axes that are already judged genuinely independent, materially backed, decoupled under perturbation, hard-enforced, durable, explicitly restored, honest about collateral width, honest about whether restored placement reused free capacity or displaced unrelated lower-priority work, and honest about whether displaced work stayed nonterminal',
        'later passes still need to distinguish in-memory-continuation, checkpoint-backed-replay, cold-restart-after-displacement, or mixed-refresh-scope-axis-remediation-displacement-resumption-basis posture',
        'one compact successor surface plus the existing admitted refresh-scope-axis-remediation-displacement-aftercare and related scheduler surfaces still keeps return-basis truth honest without standing replay-fidelity or warm-state machinery',
    ],
    'baselines': [
        'prior refresh-scope-axis-remediation-displacement-aftercare witness already names whether the displaced work retained a live path back at all',
        'current question is only whether that return stayed live in memory, replayed saved state, or restarted cold',
    ],
    'non_fit_slice': 'questions about exact replay quality, checkpoint intervals, or locality carry do not fit this compact witness',
}
append_item('APPLICABILITY-LEDGER.json', app_item)

assumption_item = {
    'id': AS,
    'title': 'one compact refresh-scope-axis-remediation-displacement-resumption-basis witness is enough for now',
    'state': 'active',
    'scope': 'continuity passes whose current widened public claim depends not only on whether corroborating axes are genuinely independent, materially backed, decoupled, hard-enforced, durable, explicitly restored, honest about collateral width, honest about whether restored placement reused free capacity or displaced unrelated lower-priority work, and honest about whether the displaced work stayed nonterminal, but on how that work actually returned',
    'invalidation_triggers': [
        'repeated later revisions need standing governance over exact-state restore versus bounded-loss replay, warm-state credit, or locality carry rather than one compact resumption-basis witness',
        'the archive needs a separate public rule just to compare replay fidelity inside checkpoint-backed return',
        'return-basis cases repeatedly fail to stay distinguishable even with the witness in place',
    ],
    'assumption_state': 'active',
    'repair': 'ordinary-continuation',
    'origin_revision': REV,
    'revision': REV,
    'assumption': 'One compact refresh-scope-axis-remediation-displacement-resumption-basis witness is enough for now.',
    'supporting_surfaces': [NEW_DOC, f'docs/90-quarantine/wild-speculations-2026-03-08.md#{QWS}', f'APPLICABILITY-LEDGER.json#{AP}', f'FOREIGN-PRESSURE-LEDGER.json#{FP}'],
    'discharge': 'retire-or-promote-if-refresh-scope-axis-remediation-displacement-resumption-basis-overflows',
    'witness_surface': f'ASSUMPTION-LEDGER.json#{AS}',
    'assumption_surface': f'ASSUMPTION-LEDGER.json#{AS}',
    'assumption_statement': 'A single compact witness is enough to keep in-memory continuation distinct from checkpoint-backed replay and cold restart for now, without a standing warm-state-credit or checkpoint-solvency layer.',
    'action_lane': 'keep-compact',
    'gate_class': 'concrete-evidence',
}
append_item('ASSUMPTION-LEDGER.json', assumption_item)

ob_item = {
    'id': OB,
    'title': 'when repaired decoupling keeps needing live-vs-replay-vs-cold separation, DelayBasin should preserve one compact refresh-scope-axis-remediation-displacement-resumption-basis witness rather than a warm-state-credit ledger',
    'state': 'open',
    'witness_surface': f'OBLIGATION-LEDGER.json#{OB}',
    'target_surfaces': [NEW_DOC, f'docs/90-quarantine/wild-speculations-2026-03-08.md#{QWS}'],
    'missing_support': 'need repeated evidence that one compact resumption-basis witness no longer keeps nonterminal return honest',
    'current_support': [NEW_DOC, f'APPLICABILITY-LEDGER.json#{AP}', f'FOREIGN-PRESSURE-LEDGER.json#{FP}'],
    'discharge_path': 'either show later that one compact refresh-scope-axis-remediation-displacement-resumption-basis witness keeps sufficing or promote stronger replay-fidelity governance explicitly',
    'obligation_state': 'open',
    'repair': 'ordinary-continuation',
    'origin_revision': REV,
    'discharge': 'reopen-only-if-refresh-scope-axis-remediation-displacement-resumption-basis-overflows',
    'revision': REV,
    'owner_surface': f'OBLIGATION-LEDGER.json#{OB}',
    'action_lane': 'keep-compact',
    'gate_class': 'overflow',
}
append_item('OBLIGATION-LEDGER.json', ob_item)

fp_item = {
    'id': FP,
    'title': 'Slurm, Kubernetes, and Run:ai all force return-basis truth once nonterminal displacement is explicit',
    'state': 'imported',
    'pressure_summary': 'Official scheduler and workload docs distinguish live suspended continuation from checkpoint-driven replay and from replacement-pod or fresh-start return, so DelayBasin should keep resumption basis explicit once aftercare truth is already in play.',
    'sources': [f'docs/00-meta/bibliography.md#ref-0999', f'docs/00-meta/bibliography.md#ref-1000', f'docs/00-meta/bibliography.md#ref-1001', f'docs/00-meta/bibliography.md#ref-1002', f'docs/00-meta/bibliography.md#ref-1003', f'docs/00-meta/bibliography.md#ref-1004', f'docs/00-meta/bibliography.md#ref-1005'],
    'why_now': 'rev0261 made aftercare truth explicit, and the next honest ambiguity is how warm the returning work actually was.',
    'imported_pressure': 'Keep live continuation distinct from checkpoint-backed replay and cold restart.',
    'quarantined_non_take': [QWS_LABEL],
    'pressure_state': 'adopted',
    'repair': 'ordinary-continuation',
    'origin_revision': REV,
    'revision': REV,
    'witness_surface': f'FOREIGN-PRESSURE-LEDGER.json#{FP}',
    'action_lane': 'keep-compact',
    'gate_class': 'concrete-evidence',
    'discharge': 'retain-unless-a-later-revision-needs-stronger-replay-fidelity-accounting',
    'assimilation_state': 'imported',
    'source_packets': [
        {'datacube': 'SlurmWarmSuspend-2026', 'surfaces': ['REF-0999', 'REF-1000', 'REF-1001'], 'pattern': 'Slurm suspend keeps memory and GRES live while later resuming the job', 'pressure': 'in-memory continuation should stay distinct from replay or restart'},
        {'datacube': 'SlurmCheckpointReplay-2026', 'surfaces': ['REF-1002'], 'pattern': 'checkpoint vacate releases nodes and restart requires a new scheduling event', 'pressure': 'checkpoint-backed return should stay distinct from live suspended continuation'},
        {'datacube': 'KubernetesReplacementReturn-2026', 'surfaces': ['REF-1003', 'REF-1004'], 'pattern': 'Job suspension deletes active Pods and replacement Pods are new objects rather than the same Pod continuing', 'pressure': 'replacement-pod return should not inherit same-object continuation authority'},
        {'datacube': 'RunAiCheckpointResume-2026', 'surfaces': ['REF-1005'], 'pattern': 'preemptible workloads may resume on another node and the startup script must explicitly reload checkpoints', 'pressure': 'checkpoint-backed replay should stay distinct from both live in-memory continuation and cold restart'},
    ],
}
append_item('FOREIGN-PRESSURE-LEDGER.json', fp_item)

tl_item = {
    'id': TL,
    'title': 'adopt the smallest return-basis take and keep warm-state governance out of canon',
    'state': 'adopted',
    'transfer_summary': 'Imported just enough scheduler and workload evidence to separate in-memory continuation, checkpoint-backed replay, and cold restart after displacement while explicitly not importing a stronger warmth or checkpoint-solvency economy.',
    'sources': [f'docs/00-meta/bibliography.md#ref-0999', f'docs/00-meta/bibliography.md#ref-1000', f'docs/00-meta/bibliography.md#ref-1001', f'docs/00-meta/bibliography.md#ref-1002', f'docs/00-meta/bibliography.md#ref-1003', f'docs/00-meta/bibliography.md#ref-1004', f'docs/00-meta/bibliography.md#ref-1005'],
    'target_surfaces': [NEW_DOC, 'docs/20-constitution/open-question-registry.md', 'docs/00-meta/trajectory-map.md', f'docs/90-quarantine/wild-speculations-2026-03-08.md#{QWS}'],
    'open_question': NEXT_OQ,
    'repair': 'ordinary-continuation',
    'origin_revision': REV,
    'action_lane': 'keep-compact',
    'gate_class': 'concrete-evidence',
    'discharge': 'reopen-only-if-refresh-scope-axis-remediation-displacement-resumption-basis-overflows',
    'revision': REV,
    'witness_surface': f'DATACUBE-TRANSFER-LEDGER.json#{TL}',
    'transfer_state': 'supporting-only',
    'bounded_take': 'Keep the archive compact by extracting one refresh-scope-axis-remediation-displacement-resumption-basis witness over the existing refresh-scope-axis-remediation-displacement-aftercare and related admitted surfaces; do not promote a warm-state credit board, checkpoint-solvency ledger, or locality-carry market.',
    'explicit_non_take': ['no warm-state credit ledger', 'no checkpoint solvency board', 'no locality carry market'],
    'open_transfer_question': 'whether later passes should add a separate replay-fidelity witness once resumption basis is explicit',
    'missing_support': 'a later public check on whether one compact refresh-scope-axis-remediation-displacement-resumption-basis witness keeps sufficing',
    'current_support': [f'APPLICABILITY-LEDGER.json#{AP}', f'FOREIGN-PRESSURE-LEDGER.json#{FP}', f'DATACUBE-TRANSFER-LEDGER.json#{TL}'],
    'discharge_path': 'either show later that one compact refresh-scope-axis-remediation-displacement-resumption-basis witness keeps sufficing or promote broader replay-fidelity governance explicitly',
    'reviewed_datacubes': [
        {'datacube': 'SlurmWarmSuspend-2026', 'surfaces': ['REF-0999', 'REF-1000', 'REF-1001'], 'pattern': 'suspend keeps jobs live in memory and on their GRES', 'pressure': 'live continuation should not flatten into replay'},
        {'datacube': 'SlurmCheckpointReplay-2026', 'surfaces': ['REF-1002'], 'pattern': 'checkpoint restart resumes only after new scheduling', 'pressure': 'checkpoint-backed replay should stay distinct from in-memory continuation'},
        {'datacube': 'KubernetesReplacementReturn-2026', 'surfaces': ['REF-1003', 'REF-1004'], 'pattern': 'suspended Jobs delete Pods and replacement Pods are new objects', 'pressure': 'cold or replayed return should not inherit same-object warmth'},
        {'datacube': 'RunAiCheckpointResume-2026', 'surfaces': ['REF-1005'], 'pattern': 'preemptible workloads use saved checkpoints and rerun startup scripts on return', 'pressure': 'checkpoint-backed replay is a distinct return basis'},
    ],
}
append_item('DATACUBE-TRANSFER-LEDGER.json', tl_item)

res_item = {
    'id': RS,
    'title': 'resolve OQ-0157 with one compact refresh-scope-axis-remediation-displacement-resumption-basis witness rather than a warm-state-credit ledger',
    'state': 'resolved',
    'closure_state': 'resolved',
    'closure_reason': 'rev0262 extracted one compact refresh-scope-axis-remediation-displacement-resumption-basis witness, kept the admitted refresh-scope-axis-remediation-displacement-aftercare and related analog surfaces narrow, and kept stronger warm-state-credit stories quarantined.',
    'discharge': 'reopen-only-if-refresh-scope-axis-remediation-displacement-resumption-basis-overflows',
    'gate_class': 'concrete-evidence',
    'origin_revision': REV,
    'prior_state': 'open gap: DelayBasin already had refresh-scope-axis-remediation-displacement-aftercare truth but still lacked one compact successor surface for whether the displaced work returned as live continuation, checkpoint replay, or cold restart.',
    'question': 'whether one compact refresh-scope-axis-remediation-displacement-resumption-basis witness over the existing refresh-scope-axis-remediation-displacement-aftercare and related admitted surfaces is enough for honest warm-vs-replay-vs-cold comparison',
    'reopen_trigger': 'refresh-scope-axis-remediation-displacement-resumption-basis pressure overflows one compact successor surface',
    'reopen_triggers': ['later revisions need standing governance over replay fidelity inside checkpoint-backed return, locality carry, warm-state credit, or broader restart-quality accounting that one compact refresh-scope-axis-remediation-displacement-resumption-basis witness cannot honestly absorb'],
    'repair': 'ordinary-continuation',
    'resolved_objects': [OQ, AP, FP, TL],
    'revision': REV,
    'successor_surface': NEW_DOC,
    'target_surfaces': [NEW_DOC],
    'action_lane': 'keep-compact',
    'witness_surface': f'RESOLUTION-LEDGER.json#{RS}',
}
append_item('RESOLUTION-LEDGER.json', res_item)

rt_item = {
    'id': RT,
    'title': 'revisit whether refresh-scope-axis-remediation-displacement-resumption-basis pressure stayed bounded after rev0262',
    'state': 'cooling',
    'candidate_surface': f'docs/90-quarantine/wild-speculations-2026-03-08.md#{QWS}',
    'cooldown_window': 'keep the stronger warm-state credit, checkpoint solvency, or locality carry story cooled until at least one later revision shows that one compact refresh-scope-axis-remediation-displacement-resumption-basis witness is no longer enough.',
    'adjudication_family': 'refresh scope axis remediation displacement resumption basis / warmth / replay pressure',
    'supersession_link': f'OBLIGATION-LEDGER.json#{OB}',
    'origin_revision': REV,
    'discharge': 'keep-cooling-unless-refresh-scope-axis-remediation-displacement-resumption-basis-overflows',
    'action_lane': 'keep-compact',
    'gate_class': 'overflow',
    'witness_surface': f'RETROSPECTIVE-QUEUE.json#{RT}',
    'revision': REV,
    'cooling_state': 'cooling',
    'disposition': 'await-adjudication',
    'repair': 'keep-cooling',
}
append_item('RETROSPECTIVE-QUEUE.json', rt_item)

fb_item = {
    'id': FB,
    'title': 'the refresh-scope-axis-remediation-displacement-resumption-basis import should count as one compact warm-vs-replay-vs-cold repair, not as permission to narrate a warm-state-credit court',
    'state': 'quarantined',
    'witness_surface': f'FIREBREAK-LEDGER.json#{FB}',
    'judged_property': 'the rev0262 decision that DelayBasin should extract one compact refresh-scope-axis-remediation-displacement-resumption-basis witness over the existing refresh-scope-axis-remediation-displacement-aftercare and related admitted surfaces and `refresh_scope_axis_remediation_displacement_resumption_basis_state` family while the broader warm-state credit / checkpoint solvency / locality carry story remains quarantined',
    'public_extract': 'Keep one compact warm-vs-replay-vs-cold return card; do not infer a standing warm-state-credit board.',
    'withheld_trace_surface': 'private working notes / search trace',
    'allowed_role': 'brief public reasoning summary only',
    'exposure_rule': 'do not expose raw private chain-of-thought or unpublished scratch reasoning; expose only the compact cited rationale and named successor surfaces',
    'trace_state': 'quarantined',
    'repair': 'ordinary-continuation',
    'origin_revision': REV,
    'action_lane': 'keep-compact',
    'gate_class': 'negative-transfer',
    'firebreak_surface': f'FIREBREAK-LEDGER.json#{FB}',
    'discharge': 'retain-unless-a-later-revision-openly-promotes-warm-state-governance',
    'revision': REV,
    'blocked_object': QWS_LABEL,
}
append_item('FIREBREAK-LEDGER.json', fb_item)

ft_item = {
    'id': FT,
    'title': 'keep checking whether refresh-scope-axis-remediation-displacement-resumption-basis pressure still fits inside one compact successor surface',
    'state': 'queued',
    'blocked_object': QWS_LABEL,
    'local_surface': f'docs/90-quarantine/wild-speculations-2026-03-08.md#{QWS}',
    'followthrough_state': 'queued',
    'boundary': 'do not promote bounded refresh-scope-axis-remediation-displacement-resumption-basis clarification into a general warm-state-credit machine',
    'next_proof_surface': NEW_DOC,
    'receiving_surface': f'FOLLOWTHROUGH-QUEUE.json#{FT}',
    'repair': 'ordinary-continuation',
    'origin_revision': REV,
    'discharge': 'revisit-on-next-real-refresh-scope-axis-remediation-displacement-resumption-basis-overflow',
    'action_lane': 'keep-compact',
    'gate_class': 'overflow',
    'blocked_output': QWS_LABEL,
    'owner_surface': f'OBLIGATION-LEDGER.json#{OB}',
    'revision': REV,
    'missing_support': 'a later public check on whether one compact return-basis witness keeps overflowing the bounded rule and honestly warrants richer replay-fidelity governance',
    'candidate_surface': f'docs/90-quarantine/wild-speculations-2026-03-08.md#{QWS}',
    'blocked_by': 'need repeated evidence that warm-vs-replay-vs-cold return truth overflows one compact witness',
}
append_item('FOLLOWTHROUGH-QUEUE.json', ft_item)

print('apply_rev0262: OK')
