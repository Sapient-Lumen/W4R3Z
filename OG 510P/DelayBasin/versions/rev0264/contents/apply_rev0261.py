from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent

REV = "rev0261"
PREV = "rev0260"
STAMP = "2026.03.28.09.18"
CREATED_AT = "2026-03-28T09:18:00-04:00"
SLUG = "aftercare-resumeq-resumecarry-stitchglass"
BUNDLE = f"DelayBasin-{REV}-{STAMP}-{SLUG}.zip"
SUMMARY_HIGHLIGHT = "resumecarry"
CODENAME = "stitchglass"
NEW_DOC = "docs/10-method/refresh-scope-axis-remediation-displacement-aftercare-witnesses-resumable-displacement-terminal-displacement-and-mixed-aftercare.md"
NEW_DOC_NAME = NEW_DOC.split("/")[-1]
NEW_CHECKER = "tools/check_refresh_scope_axis_remediation_displacement_aftercare_witness_contract.py"
QWS = "QWS-0239"
QWS_LABEL = "resume credit / checkpoint escrow / restart tax"
CL = "CL-0154"
RS = "RS-0163"
OQ = "OQ-0156"
NEXT_OQ = "OQ-0157"
PP = "PP-0114"
AP = "AP-0155"
OB = "OB-0156"
AS = "AS-0160"
FP = "FP-0160"
TL = "TL-0166"
FT = "FT-0163"
RT = "RT-0150"
FB = "FB-0157"
FAMILY = "refresh_scope_axis_remediation_displacement_aftercare_state"
ALLOWED = [
    "resumable-displacement-aftercare",
    "terminal-displacement-aftercare",
    "mixed-refresh-scope-axis-remediation-displacement-aftercare",
]
EXCLUDED = [
    "requeue-means-paid-back",
    "suspend-means-free",
    "cancel-means-minor",
    "aftercare-ish",
]


def read_text(rel: str) -> str:
    return (ROOT / rel).read_text(encoding="utf-8")


def write_text(rel: str, text: str) -> None:
    (ROOT / rel).write_text(text, encoding="utf-8")


def load_json(rel: str):
    return json.loads(read_text(rel))


def dump_json(rel: str, obj) -> None:
    write_text(rel, json.dumps(obj, indent=2, ensure_ascii=False) + "\n")


def ensure_contains(rel: str, needle: str, addition: str) -> None:
    text = read_text(rel)
    if addition in text:
        return
    if needle not in text:
        raise RuntimeError(f"needle not found in {rel}: {needle}")
    write_text(rel, text.replace(needle, needle + addition, 1))


def replace_once(rel: str, old: str, new: str) -> None:
    text = read_text(rel)
    if new in text:
        return
    if old not in text:
        raise RuntimeError(f"old block not found in {rel}")
    write_text(rel, text.replace(old, new, 1))


def replace_regex(rel: str, pattern: str, repl: str, *, count: int = 1) -> None:
    text = read_text(rel)
    new_text, n = re.subn(pattern, repl, text, count=count, flags=re.S)
    if n == 0:
        raise RuntimeError(f"pattern not found in {rel}: {pattern}")
    write_text(rel, new_text)


def append_item(rel: str, item: dict) -> None:
    obj = load_json(rel)
    items = obj["items"]
    if any(existing["id"] == item["id"] for existing in items):
        return
    items.append(item)
    dump_json(rel, obj)


new_doc_text = """# Refresh-scope-axis-remediation-displacement-aftercare witnesses, resumable displacement, terminal displacement, and mixed aftercare

This is the compact successor surface for `OQ-0156`.

## Practice / observation

Once DelayBasin can say that corroborating axes are genuinely independent, materially backed, decoupled under perturbation, hard-enforced, durable, explicit about who restored the decoupling, honest about how wide the remediation was, and honest about whether the restored placement reused free capacity or only came back by displacing unrelated lower-priority work, one more ambiguity remains.

Some displacement-backed repairs are still comparatively reversible.
The lower-priority work that paid the bill is suspended, paused, or requeued with a live path back into execution.
Progress may still be slowed or partially lost.
But the archive can still honestly say that the aftercare posture was resumable rather than sacrificial.

Other displacement-backed repairs are terminal.
The displaced work is canceled, deactivated after retry limits, dropped, or otherwise abandoned.
Those cases should not silently inherit the same legitimacy as a temporary suspension or queue detour.
The repaired placement now rests on a stronger sacrifice than mere reversible borrowing.

Some cases are honestly mixed.
A scheduler may suspend one victim, requeue another, and cancel a third.
A workload may be requeued several times and only later deactivated.
Those cases should not be flattened into a clean resumable story or a clean sacrifice story.

DelayBasin does not need a standing restitution court here.
It needs one bounded witness that says whether displacement aftercare is still resumable, terminal, or honestly mixed.

## External pressure from Slurm suspend, requeue, and cancel modes, Kubernetes Jobs suspend/resume and disruption handling, Kueue requeue and deactivation limits, and NVIDIA Run:ai automatic resume with checkpointing

1. Slurm's preemption docs say `REQUEUE` preempts jobs by requeuing them if possible or canceling them, while `SUSPEND` suspends jobs and later the Gang scheduler resumes them; Slurm's configuration docs separately say `CANCEL` cancels the preempted job. That pressures DelayBasin to distinguish resumable displacement from terminal sacrifice even when both free room for a higher-priority job. ([`REF-0991`](../00-meta/bibliography.md), [`REF-0993`](../00-meta/bibliography.md))

2. Kubernetes Job docs say suspending a Job deletes its active Pods until the Job is resumed again, and the controller will start a new Pod if a Pod fails or is deleted. That pressures DelayBasin to treat some disruption paths as resumable controller-managed continuation rather than immediate abandonment. ([`REF-0994`](../00-meta/bibliography.md))

3. Kubernetes Pod failure policy docs show that a Job can be configured so Pod disruptions do not count toward failure and the Job resumes and succeeds, while without that policy and with `backoffLimit: 0` the same disruption would terminate the entire Job. That pressures DelayBasin not to narrate all displacement or eviction aftermath as the same aftercare class. ([`REF-0995`](../00-meta/bibliography.md))

4. Kueue's configuration API says timeouts can evict and requeue a Workload in the same ClusterQueue, and a recovery timeout can suspend it again and requeue it after backoff delay. Kueue's wait-for-pods-ready task docs also say repeated requeues continue until `backoffLimitCount`, after which the Workload is deactivated. That pressures DelayBasin to distinguish live requeue paths from aftercare that eventually becomes terminal. ([`REF-0996`](../00-meta/bibliography.md), [`REF-0997`](../00-meta/bibliography.md))

5. NVIDIA Run:ai docs say preemptible workloads may be paused while resources are reassigned to higher-priority workloads and are automatically resumed when resources become available, with checkpointing recommended to preserve progress. That pressures GPUstorming not to flatten automatic resume and checkpoint-backed return into outright sacrifice, while still keeping stronger restart accounting out of canon for now. ([`REF-0998`](../00-meta/bibliography.md))

GPUstorming makes the difference vivid. Two repaired GPU placements can both be preemption-backed. In one case, lower-priority work is merely suspended or requeued and remains on a believable path back. In another, the work is canceled, deactivated, or quietly sacrificed. Capacity-source truth alone does not say what kind of aftercare bill was actually imposed.

## Working synthesis

> DelayBasin should preserve one compact **refresh-scope-axis-remediation-displacement-aftercare witness / reversibility card / sacrifice brake** whenever a current continuity claim depends not only on whether corroborating axes are genuinely independent, materially backed, decoupled, hard-enforced, durable, explicitly restored, honest about collateral width, and honest about whether restored placement reused free capacity or displaced unrelated lower-priority work, but on what happened to the displaced work afterward. Name the **governed row or surface**, the **stake object / line of concern**, the **prior refresh-scope-axis-remediation-capacity-source evidence**, the **current corroborating axes**, the **resumable-aftercare basis if any**, the **terminal-aftercare basis if any**, the **`refresh_scope_axis_remediation_displacement_aftercare_state`**, and the **fail-closed repair / keep-current vs narrow-claim vs split-scope vs issue-new-refresh-scope-axis-remediation-displacement-aftercare-witness vs quarantine-resume-credit consequence**. Keep raw eviction events, retry counters, checkpoint traces, suspend/resume logs, and controller histories outside the compact token. Do not let outright sacrifice silently inherit the authority of reversible priority borrowing.

## Resumable displacement aftercare vs terminal displacement aftercare vs mixed refresh scope axis remediation displacement aftercare

Use the controlled family `refresh_scope_axis_remediation_displacement_aftercare_state`:

- **resumable-displacement-aftercare** says the displaced lower-priority work was suspended, paused, requeued, retried, or otherwise kept on a live public path back into execution rather than deliberately abandoned.
- **terminal-displacement-aftercare** says the displaced lower-priority work was canceled, deactivated, abandoned, or otherwise left without a live public resumption path.
- **mixed-refresh-scope-axis-remediation-displacement-aftercare** says the current situation honestly combines resumable and terminal aftercare, or the public evidence cannot keep one clean class honest.

So the witness does not create a full restitution ledger.
It only preserves the smallest load-bearing truth about whether preemption-backed repair borrowed work temporarily or sacrificed it outright.

## Countermodels / probes

1. **Requeue is not always cheap forever**
   - A workload may be requeued several times and only later deactivated or abandoned.
   - Probe: if the live public story needs both phases, keep the mixed state rather than flattering the case as purely resumable.

2. **Resumable is not the same as lossless**
   - Slurm suspend/resume, Run:ai checkpoint-backed return, and controller-driven pod recreation all preserve different amounts of progress.
   - Probe: keep the current canon question narrow. This witness only classifies whether aftercare stayed live or went terminal. Finer distinctions about in-memory resume, checkpoint replay, and cold restart belong to the next frontier unless repeated overflow says otherwise.

3. **Free-capacity restoration should not import aftercare debt**
   - If the restoration did not actually displace unrelated work, aftercare language should not be forced in by atmosphere.
   - Probe: require prior refresh-scope-axis-remediation-capacity-source evidence before applying this witness.

## Design consequences

- DelayBasin can now keep displacement-backed repair from sounding equally reversible when some repairs merely pause lower-priority work and others permanently discard it.
- The archive gets one explicit place to record when a repaired GPU placement borrowed time from lower-priority work versus consumed that work entirely.
- GPUstorming can now distinguish reversible queue borrowing from sacrificial preemption without inflating a broader restitution board.
- Stronger resume-credit, checkpoint-escrow, or restart-tax stories stay quarantined until repeated overflow rather than entering canon by atmosphere.

## Overflow test

Reopen this compact witness only if later revisions repeatedly need explicit public accounting for in-memory resume versus checkpoint-backed replay versus cold restart, compensation or restitution rules for sacrificed work, or branch-wide restart taxation that one bounded refresh-scope-axis-remediation-displacement-aftercare witness cannot honestly absorb.

## Transformer-facing implication

A later pass should not treat all displacement-backed repair as if the lower-priority work paid the same kind of bill. Preserve the smallest token that says whether the present aftercare is `resumable-displacement-aftercare`, `terminal-displacement-aftercare`, or honestly `mixed-refresh-scope-axis-remediation-displacement-aftercare`, and quarantine stronger resume-credit ambitions until repeated overflow makes them unavoidable.
"""
write_text(NEW_DOC, new_doc_text)
write_text(
    NEW_CHECKER,
    'from packet_contract_common import require_named_refresh_scope_axis_branch_witness_packet_and_vocabulary\n\nrequire_named_refresh_scope_axis_branch_witness_packet_and_vocabulary("refresh_scope_axis_remediation_displacement_aftercare_witness_contract")\n\nprint("check_refresh_scope_axis_remediation_displacement_aftercare_witness_contract: OK")\n',
)

bib_add = """

- `REF-0993` — Slurm Workload Manager, **slurm.conf** (accessed 2026-03-28)
  - URL: https://slurm.schedmd.com/slurm.conf.html
  - Load-bearing use: Slurm configuration docs define `CANCEL` as canceling the preempted job and `SUSPEND`/`GANG` as later resuming suspended jobs, which pressures DelayBasin to distinguish resumable displacement from terminal sacrifice.

- `REF-0994` — Kubernetes Documentation, **Jobs** (accessed 2026-03-28)
  - URL: https://kubernetes.io/docs/concepts/workloads/controllers/job/
  - Load-bearing use: suspending a Job deletes active Pods until the Job is resumed again and the controller replaces failed or deleted Pods, which pressures DelayBasin to treat some disruption paths as resumable rather than terminal.

- `REF-0995` — Kubernetes Documentation, **Handling retriable and non-retriable pod failures with Pod failure policy** (accessed 2026-03-28)
  - URL: https://kubernetes.io/docs/tasks/job/pod-failure-policy/
  - Load-bearing use: Kubernetes shows that ignored Pod disruptions can let a Job resume and succeed while the same disruption can otherwise terminate the Job, which pressures DelayBasin to separate resumable and terminal aftercare.

- `REF-0996` — Kueue Documentation, **Kueue Configuration v1beta1 API** (accessed 2026-03-28)
  - URL: https://kueue.sigs.k8s.io/docs/reference/kueue-config.v1beta1/
  - Load-bearing use: Kueue explicitly evicts and requeues workloads on timeout, can suspend and requeue them again after recovery timeout, and therefore pressures DelayBasin to keep live requeue paths distinct from terminal aftermath.

- `REF-0997` — Kueue Documentation, **Setup All-or-nothing with ready Pods** (accessed 2026-03-28)
  - URL: https://kueue.sigs.k8s.io/docs/tasks/manage/setup_wait_for_pods_ready/
  - Load-bearing use: repeated requeues continue until `backoffLimitCount`, after which Kueue deactivates the workload, which pressures DelayBasin to distinguish resumable aftercare from eventually terminal aftercare.

- `REF-0998` — NVIDIA Run:ai Documentation, **Best Practices: Checkpointing Preemptible Training Workloads** (accessed 2026-03-28)
  - URL: https://run-ai-docs.nvidia.com/self-hosted/workloads-in-nvidia-run-ai/using-training/checkpointing-preemptible-workloads
  - Load-bearing use: Run:ai pauses preemptible workloads, later resumes them automatically, and recommends checkpointing, which pressures DelayBasin to distinguish resumable displacement from terminal sacrifice without yet promoting full restart accounting.
"""
ensure_contains(
    "docs/00-meta/bibliography.md",
    "- `REF-0992` — Ray Documentation, **Gang scheduling, Priority scheduling, and Autoscaling for RayJob resources with Kueue** (accessed 2026-03-28)\n  - URL: https://docs.ray.io/en/latest/cluster/kubernetes/k8s-ecosystem/kueue.html\n  - Load-bearing use: Ray's Kueue integration shows a higher-priority RayJob preempting a lower-priority RayJob, which pressures GPUstorming to keep displacement-backed GPU recovery distinct from simple spare-capacity reuse.\n",
    bib_add,
)

ensure_contains(
    "docs/README.md",
    f"- [`10-method/refresh-scope-axis-remediation-capacity-source-witnesses-free-capacity-restoration-preemption-backed-restoration-and-mixed-restoration.md`](10-method/refresh-scope-axis-remediation-capacity-source-witnesses-free-capacity-restoration-preemption-backed-restoration-and-mixed-restoration.md)\n",
    f"- [`10-method/{NEW_DOC_NAME}`](10-method/{NEW_DOC_NAME})\n",
)
ensure_contains(
    "docs/00-meta/llm-runbook.md",
    "Use `docs/10-method/refresh-scope-axis-remediation-capacity-source-witnesses-free-capacity-restoration-preemption-backed-restoration-and-mixed-restoration.md` when the live question is whether repaired decoupling came back on already-available capacity or only by preempting unrelated lower-priority work.\n",
    "Use `docs/10-method/refresh-scope-axis-remediation-displacement-aftercare-witnesses-resumable-displacement-terminal-displacement-and-mixed-aftercare.md` when the live question is what happened afterward to the lower-priority work that paid the preemption bill: whether it stayed on a live path back or was terminally sacrificed.\n",
)

claim_add = """

- `CL-0154` — Archive continuity may improve when DelayBasin preserves one compact **refresh-scope-axis-remediation-displacement-aftercare witness / reversibility card / sacrifice brake** whenever a current continuity claim depends not only on whether corroborating axes are genuinely independent, materially backed, decoupled under perturbation, hard-enforced, durable, explicitly restored, honest about collateral width, and honest about whether restored placement reused free capacity or displaced unrelated lower-priority work, but on what happened to the displaced work afterward: name the **governed row or surface**, the **stake object / line of concern**, the **prior refresh-scope-axis-remediation-capacity-source evidence**, the **current corroborating axes**, the **resumable-aftercare basis if any**, the **terminal-aftercare basis if any**, the **refresh_scope_axis_remediation_displacement_aftercare_state**, and the **fail-closed repair** rather than letting outright sacrifice silently inherit the authority of reversible priority borrowing.
  - Status: speculative but central
  - Wired docs: `docs/10-method/refresh-scope-axis-remediation-displacement-aftercare-witnesses-resumable-displacement-terminal-displacement-and-mixed-aftercare.md`, `docs/20-constitution/open-question-registry.md`, `docs/20-constitution/prompt-pair-registry.md`, `docs/50-promptcraft/prompt-pairs.md`, `docs/00-meta/llm-runbook.md`, `WITNESS-VOCABULARY.json`, `REVISION-RECEIPT.json`
"""
ensure_contains(
    "docs/20-constitution/claim-registry.md",
    "- `CL-0153` — Archive continuity may improve when DelayBasin preserves one compact **refresh-scope-axis-remediation-capacity-source witness / priority-bill card / displacement brake** whenever a current continuity claim depends not only on whether corroborating axes are genuinely independent, materially backed, decoupled under perturbation, hard-enforced, durable, explicitly restored, and honest about collateral width, but on whether the restored placement reused already-available capacity or succeeded only by displacing unrelated lower-priority work: name the **governed row or surface**, the **stake object / line of concern**, the **prior refresh-scope-axis-remediation-collateral evidence**, the **current corroborating axes**, the **free-capacity basis if any**, the **preemption-backed basis if any**, the **refresh_scope_axis_remediation_capacity_source_state**, and the **fail-closed repair** rather than letting preemption-backed restoration silently inherit the cheap authority of free-capacity recovery.\n  - Status: speculative but central\n  - Wired docs: `docs/10-method/refresh-scope-axis-remediation-capacity-source-witnesses-free-capacity-restoration-preemption-backed-restoration-and-mixed-restoration.md`, `docs/20-constitution/open-question-registry.md`, `docs/20-constitution/prompt-pair-registry.md`, `docs/50-promptcraft/prompt-pairs.md`, `docs/00-meta/llm-runbook.md`, `WITNESS-VOCABULARY.json`, `REVISION-RECEIPT.json`\n",
    claim_add,
)

pp_reg_add = """

- `PP-0114` — Name whether displaced lower-priority work remained resumable or was terminally sacrificed
  - Goal: keep terminal sacrifice from silently inheriting reversible-borrowing authority by requiring explicit prior remediation-capacity-source evidence, current corroborating axes, resumable-aftercare basis, terminal-aftercare basis, `refresh_scope_axis_remediation_displacement_aftercare_state`, and fail-closed repair before later passes call the restored support merely preempted rather than sacrificial.
  - Canonical text: `docs/50-promptcraft/prompt-pairs.md#pp-0114--name-whether-displaced-lower-priority-work-remained-resumable-or-was-terminally-sacrificed`
"""
ensure_contains(
    "docs/20-constitution/prompt-pair-registry.md",
    "- `PP-0113` — Name whether restored decoupling reused free capacity or displaced lower-priority work\n  - Goal: keep preemption-backed restoration from silently inheriting cheap free-capacity authority by requiring explicit prior remediation-collateral evidence, current corroborating axes, free-capacity basis, preemption-backed basis, `refresh_scope_axis_remediation_capacity_source_state`, and fail-closed repair before later passes call the restored support cheaply available.\n  - Canonical text: `docs/50-promptcraft/prompt-pairs.md#pp-0113--name-whether-restored-decoupling-reused-free-capacity-or-displaced-lower-priority-work`\n",
    pp_reg_add,
)

prompt_pair_add = """

## PP-0114 — Name whether displaced lower-priority work remained resumable or was terminally sacrificed

**Opening prompt**

```text
Read the latest DelayBasin archive and inspect whether the current revision should also materialize one compact refresh-scope-axis-remediation-displacement-aftercare witness for honest resumable-vs-terminal preemption aftermath.

Focus only on cases where the corroborating axes already look genuinely independent, materially backed, decoupled under perturbation, hard-enforced, durable, explicit about who restored the decoupling, honest about how wide the remediation was, and honest about whether restored placement reused free capacity or only came back by displacing unrelated lower-priority work. The missing question is what happened afterward to the lower-priority work that paid the preemption bill.

If yes, preserve exactly one small witness that:
- names the governed row or surface,
- names the stake object / line of concern,
- names the prior refresh-scope-axis-remediation-capacity-source evidence,
- names the current corroborating axes,
- names the resumable-aftercare basis if any,
- names the terminal-aftercare basis if any,
- names the `refresh_scope_axis_remediation_displacement_aftercare_state` / whether this is resumable-displacement-aftercare, terminal-displacement-aftercare, or mixed-refresh-scope-axis-remediation-displacement-aftercare,
- states what stronger surfaces still outrank the witness,
- and states the fail-closed repair / keep-current vs narrow-claim vs split-scope vs issue-new-refresh-scope-axis-remediation-displacement-aftercare-witness vs quarantine-resume-credit consequence if the present continuity claim is not actually supported by the claimed aftercare.

Do not use refresh-scope-axis-remediation-displacement-aftercare as a standing restitution or restart-tax board. Use this prompt pair only where axis independence, materiality, coupling, enforcement, durability, remediation provenance, remediation collateral, and remediation capacity source are already established and the missing question is whether the displaced work still had a live path back.
```

**Continuation prompt**

```text
Continue the refresh-scope-axis-remediation-displacement-aftercare pass with one high-leverage aftercare clarification only. Prefer the smallest witness that says what governed row is still being justified, what stake object is supposedly widened, what prior refresh-scope-axis-remediation-capacity-source evidence exists, what current corroborating axes exist, what resumable-aftercare basis if any now exists, what terminal-aftercare basis if any now exists, what `refresh_scope_axis_remediation_displacement_aftercare_state` is honest, what stronger surfaces still outrank the witness, and what keep-current, narrow-claim, split-scope, issue-new-refresh-scope-axis-remediation-displacement-aftercare-witness, quarantine, or recover-resync consequence follows if the present aftercare is resumable-displacement-aftercare, terminal-displacement-aftercare, or mixed-refresh-scope-axis-remediation-displacement-aftercare. Run `make lint` and package the release.
```

Use `docs/10-method/refresh-scope-axis-remediation-displacement-aftercare-witnesses-resumable-displacement-terminal-displacement-and-mixed-aftercare.md` when the live question is what happened afterward to the lower-priority work that paid the preemption bill.
"""
ensure_contains(
    "docs/50-promptcraft/prompt-pairs.md",
    "Use `docs/10-method/refresh-scope-axis-remediation-capacity-source-witnesses-free-capacity-restoration-preemption-backed-restoration-and-mixed-restoration.md` when the live question is whether repaired or rebalanced decoupling came back through already-available slack or only by displacing lower-priority work.\n",
    prompt_pair_add,
)

replace_regex(
    "docs/20-constitution/open-question-registry.md",
    r"- `OQ-0156` — what remediation-displacement-aftercare witness distinguishes restoration that only suspends or requeues displaced lower-priority work from restoration that cancels or abandons it\?\n  - Why it matters: if DelayBasin cannot separate resumable displacement from outright sacrifice, later sessions may narrate bounded priority borrowing from repairs that permanently discard unrelated work\.\n  - Current posture: unresolved\n",
    "- `OQ-0156` — what remediation-displacement-aftercare witness distinguishes restoration that only suspends or requeues displaced lower-priority work from restoration that cancels or abandons it?\n  - Why it matters: if DelayBasin cannot separate resumable displacement from outright sacrifice, later sessions may narrate bounded priority borrowing from repairs that permanently discard unrelated work.\n  - Current posture: resolved by `RS-0163` via `docs/10-method/refresh-scope-axis-remediation-displacement-aftercare-witnesses-resumable-displacement-terminal-displacement-and-mixed-aftercare.md`; reopen only if the compact refresh-scope-axis-remediation-displacement-aftercare witness proves insufficient and stronger resumption-basis or restitution governance is honestly required\n\n- `OQ-0157` — what remediation-displacement-resumption-basis witness distinguishes in-memory continuation from checkpoint-backed replay and cold restart after displacement?\n  - Why it matters: if DelayBasin cannot separate live resume, replay-from-checkpoint, and fresh restart, later sessions may over-credit resumable displacement that actually lost substantial work.\n  - Current posture: unresolved\n",
)

replace_regex(
    "docs/00-meta/trajectory-map.md",
    r"112\. Determine what remediation-displacement-aftercare witness distinguishes restoration that temporarily suspends or requeues displaced work from restoration that cancels or abandons it\.\n\nA fresh extension is that once capacity source is explicit, DelayBasin may next need to say what happens to the work that paid the preemption bill\. Otherwise displacement-backed repair may silently inherit the authority of reversible priority borrowing even when it permanently cancels or abandons unrelated work\.\n- `OQ-0156` — what remediation-displacement-aftercare witness distinguishes restoration that only suspends or requeues displaced lower-priority work from restoration that cancels or abandons it\?\n  - Why it matters: if DelayBasin cannot separate resumable displacement from outright sacrifice, later sessions may narrate bounded priority borrowing from repairs that permanently discard unrelated work\.\n  - Current posture: unresolved\n",
    "112. Determine what remediation-displacement-aftercare witness distinguishes restoration that temporarily suspends or requeues displaced work from restoration that cancels or abandons it.\n\nA fresh extension is that once capacity source is explicit, DelayBasin may next need to say what happens to the work that paid the preemption bill. Otherwise displacement-backed repair may silently inherit the authority of reversible priority borrowing even when it permanently cancels or abandons unrelated work.\n- `OQ-0156` — what remediation-displacement-aftercare witness distinguishes restoration that only suspends or requeues displaced lower-priority work from restoration that cancels or abandons it?\n  - Why it matters: if DelayBasin cannot separate resumable displacement from outright sacrifice, later sessions may narrate bounded priority borrowing from repairs that permanently discard unrelated work.\n  - Current posture: resolved by `RS-0163` via `docs/10-method/refresh-scope-axis-remediation-displacement-aftercare-witnesses-resumable-displacement-terminal-displacement-and-mixed-aftercare.md`; reopen only if the compact refresh-scope-axis-remediation-displacement-aftercare witness proves insufficient and stronger resumption-basis or restitution governance is honestly required\n\n113. Determine what remediation-displacement-resumption-basis witness distinguishes in-memory continuation from checkpoint-backed replay and cold restart after displacement.\n\nA fresh extension is that once aftercare is explicit, DelayBasin may next need to say what kind of return path the displaced work actually retained. Suspended work resumed in memory, checkpoint-backed replay, and cold restart after eviction all count as not-yet-abandoned in one weak sense, but they do not preserve the same continuity.\n- `OQ-0157` — what remediation-displacement-resumption-basis witness distinguishes in-memory continuation from checkpoint-backed replay and cold restart after displacement?\n  - Why it matters: if DelayBasin cannot separate live resume, replay-from-checkpoint, and fresh restart, later sessions may over-credit resumable displacement that actually lost substantial work.\n  - Current posture: unresolved\n",
)

qws_add = """
## QWS-0239 — Some continuations may eventually need a resume credit / checkpoint escrow / restart tax rather than only a compact refresh-scope-axis-remediation-displacement-aftercare witness

### Claim
Some later continuations may need stronger public machinery for how displaced work returns, how much progress it actually preserved, and what penalty should apply when a supposedly resumable preemption really implies replay or cold restart. One compact resumable-vs-terminal aftercare witness may eventually stop being enough.

### What follows if true
- DelayBasin may eventually need an explicit way to distinguish in-memory resume, checkpoint-backed replay, and fresh restart rather than treating all nonterminal aftercare as equally reversible.
- The archive might need a bounded resume-credit or checkpoint-escrow layer if later revisions repeatedly compare several preemption-backed repairs whose displaced work returned with very different continuity costs.

### What would count against it
- Several later revisions keep fitting cleanly inside one compact refresh-scope-axis-remediation-displacement-aftercare witness without repeated confusion about what kind of return path the displaced work really retained.
- The archive almost never needs public reasoning about restart depth once resumable-vs-terminal aftercare is already made explicit.

### Why it stays quarantined
The current evidence justifies one bounded witness for resumable versus terminal displacement aftercare. It does not yet justify a standing resume-credit board, checkpoint escrow, or restart tax layer.
"""
ensure_contains(
    "docs/90-quarantine/wild-speculations-2026-03-08.md",
    "The current evidence justifies one bounded witness for free-capacity restoration vs preemption-backed restoration. It does not yet justify a standing priority tariff board, debt ledger, or resumability escrow layer.\n",
    qws_add,
)

packet_spec_add = """
"refresh_scope_axis_remediation_displacement_aftercare_witness_contract": refresh_scope_axis_branch_spec(
    doc_path="docs/10-method/refresh-scope-axis-remediation-displacement-aftercare-witnesses-resumable-displacement-terminal-displacement-and-mixed-aftercare.md",
    title="Refresh-scope-axis-remediation-displacement-aftercare witnesses, resumable displacement, terminal displacement, and mixed aftercare",
    oq_id="OQ-0156",
    external_pressure_heading="## External pressure from Slurm suspend, requeue, and cancel modes, Kubernetes Jobs suspend/resume and disruption handling, Kueue requeue and deactivation limits, and NVIDIA Run:ai automatic resume with checkpointing",
    comparison_heading="## Resumable displacement aftercare vs terminal displacement aftercare vs mixed refresh scope axis remediation displacement aftercare",
    runbook_ref="refresh-scope-axis-remediation-displacement-aftercare-witnesses-resumable-displacement-terminal-displacement-and-mixed-aftercare.md",
    prompt_id="PP-0114",
    prompt_needles=["Use `docs/10-method/refresh-scope-axis-remediation-displacement-aftercare-witnesses-resumable-displacement-terminal-displacement-and-mixed-aftercare.md`", "resumable-displacement-aftercare, terminal-displacement-aftercare, or mixed-refresh-scope-axis-remediation-displacement-aftercare"],
    claim_id="CL-0154",
    resolution_id="RS-0163",
    trajectory_oq_id="OQ-0157",
    qws_id="QWS-0239",
    qws_label="resume credit / checkpoint escrow / restart tax",
    changelog_needles=["refresh-scope-axis-remediation-displacement-aftercare-witnesses-resumable-displacement-terminal-displacement-and-mixed-aftercare.md", "check_refresh_scope_axis_remediation_displacement_aftercare_witness_contract.py"],
    family="refresh_scope_axis_remediation_displacement_aftercare_state",
    allowed=["resumable-displacement-aftercare", "terminal-displacement-aftercare", "mixed-refresh-scope-axis-remediation-displacement-aftercare"],
    excluded=["requeue-means-paid-back", "suspend-means-free", "cancel-means-minor", "aftercare-ish"],
),
"""
ensure_contains(
    "tools/packet_contract_common.py",
    '    excluded=["priority-means-preempted", "borrowed-quota-is-free-enough", "preemption-is-just-capacity", "capacity-ish"],\n),\n',
    packet_spec_add,
)

replace_once(
    "tools/release_hygiene_lib.py",
    "PACKAGING_EXCLUDED_SUFFIXES = {\".pyc\", \".pyo\"}\n\n\ndef is_frozen_bundle_part(part: str) -> bool:\n    return bool(re.fullmatch(r\"DelayBasin-rev\\d{4}-.*\", part))\n",
    "PACKAGING_EXCLUDED_SUFFIXES = {\".pyc\", \".pyo\"}\n\n\ndef build_bundle_name(revision: str, timestamp: str, slug: str) -> str:\n    return f\"DelayBasin-{revision}-{timestamp}-{slug}.zip\"\n\n\ndef is_frozen_bundle_part(part: str) -> bool:\n    return bool(re.fullmatch(r\"DelayBasin-rev\\d{4}-.*\", part))\n",
)
replace_once(
    "tools/package_release.py",
    "from release_hygiene_lib import should_skip_release_path\n",
    "from release_hygiene_lib import build_bundle_name, should_skip_release_path\n",
)
replace_once(
    "tools/package_release.py",
    "bundle_name = f\"DelayBasin-{rev}-{args.timestamp}-{args.slug}.zip\"\n",
    "bundle_name = build_bundle_name(rev, args.timestamp, args.slug)\n",
)

assumption_item = {
    "id": AS,
    "title": "one compact refresh-scope-axis-remediation-displacement-aftercare witness is enough for now",
    "state": "active",
    "scope": "continuity passes whose current widened public claim depends not only on whether corroborating axes are genuinely independent, materially backed, decoupled, hard-enforced, durable, explicitly restored, honest about collateral width, and honest about whether restored placement reused free capacity or displaced unrelated lower-priority work, but on what happened afterward to the displaced work",
    "invalidation_triggers": [
        "repeated later revisions need standing governance over resume credit, checkpoint escrow, restart taxation, or restitution rather than one compact aftercare witness",
        "the archive needs a separate public rule just to distinguish in-memory continuation, checkpoint replay, and cold restart",
        "aftercare cases repeatedly fail to stay distinguishable even with the witness in place",
    ],
    "assumption_state": "active",
    "repair": "ordinary-continuation",
    "origin_revision": REV,
    "revision": REV,
    "assumption": "One compact refresh-scope-axis-remediation-displacement-aftercare witness is enough for now.",
    "supporting_surfaces": [NEW_DOC, f"docs/90-quarantine/wild-speculations-2026-03-08.md#{QWS}", f"APPLICABILITY-LEDGER.json#{AP}", f"FOREIGN-PRESSURE-LEDGER.json#{FP}"],
    "discharge": "retire-or-promote-if-refresh-scope-axis-remediation-displacement-aftercare-overflows",
    "witness_surface": f"ASSUMPTION-LEDGER.json#{AS}",
    "assumption_surface": f"ASSUMPTION-LEDGER.json#{AS}",
    "assumption_statement": "A single compact witness is enough to keep resumable displacement distinct from terminal sacrifice for now, without a standing resume-credit or checkpoint-escrow layer.",
    "action_lane": "keep-compact",
    "gate_class": "concrete-evidence",
}
append_item("ASSUMPTION-LEDGER.json", assumption_item)

ob_item = {
    "id": OB,
    "title": "when repaired decoupling keeps needing resumable-vs-terminal separation, DelayBasin should preserve one compact refresh-scope-axis-remediation-displacement-aftercare witness rather than a resume credit ledger",
    "state": "open",
    "witness_surface": f"OBLIGATION-LEDGER.json#{OB}",
    "target_surfaces": [NEW_DOC, f"docs/90-quarantine/wild-speculations-2026-03-08.md#{QWS}"],
    "missing_support": "need repeated evidence that one compact aftercare witness no longer keeps preemption aftermath honest",
    "current_support": [NEW_DOC, f"APPLICABILITY-LEDGER.json#{AP}", f"FOREIGN-PRESSURE-LEDGER.json#{FP}"],
    "discharge_path": "either show later that one compact refresh-scope-axis-remediation-displacement-aftercare witness keeps sufficing or promote stronger resumption-basis governance explicitly",
    "obligation_state": "open",
    "repair": "ordinary-continuation",
    "origin_revision": REV,
    "discharge": "reopen-only-if-refresh-scope-axis-remediation-displacement-aftercare-overflows",
    "revision": REV,
    "owner_surface": f"OBLIGATION-LEDGER.json#{OB}",
    "action_lane": "keep-compact",
    "gate_class": "overflow",
}
append_item("OBLIGATION-LEDGER.json", ob_item)

app_item = {
    "id": AP,
    "title": "the refresh-scope-axis-remediation-displacement-aftercare witness stays smaller than a resume-credit ledger",
    "state": "gated",
    "question": "when should DelayBasin treat preemption aftermath with one compact remediation-displacement-aftercare witness instead of promoting broader restart accounting or restitution?",
    "applies_when": [
        "a revision already has a row whose current claim depends on corroborating axes that are already judged genuinely independent, materially backed, decoupled under perturbation, hard-enforced, durable, explicitly restored, honest about collateral width, and honest about whether restored placement reused free capacity or displaced unrelated lower-priority work",
        "later passes still need to distinguish resumable-displacement-aftercare, terminal-displacement-aftercare, or mixed-refresh-scope-axis-remediation-displacement-aftercare posture",
        "one compact successor surface plus the existing admitted refresh-scope-axis-remediation-capacity-source and related scheduler surfaces still keeps aftercare truth honest without standing resume-credit or checkpoint machinery",
    ],
    "does_not_apply_when": [
        "the archive honestly requires standing governance over in-memory resume versus checkpoint replay versus cold restart, explicit restart taxation, or restitution for sacrificed work",
        "the questioned surface is not really about what happened afterward to the displaced lower-priority work",
    ],
    "budget": "one compact refresh-scope-axis-remediation-displacement-aftercare witness plus one resolution of OQ-0156; no resume credit ledger",
    "negative_transfer_budget": "do not treat any preemption-backed repair as if all displaced work paid the same kind of reversible bill",
    "origin_revision": REV,
    "discharge": "reopen-only-if-refresh-scope-axis-remediation-displacement-aftercare-overflows",
    "action_lane": "keep-compact",
    "gate_class": "concrete-evidence",
    "witness_surface": f"APPLICABILITY-LEDGER.json#{AP}",
    "applicability_state": "gated",
    "repair": "ordinary-continuation",
    "matched_budget": "one compact witness foregrounding resumable versus terminal aftercare without widening into restart accounting",
    "revision": REV,
    "target_objective": "keep displacement aftercare honest without inflating a general resume-credit layer",
    "carry_object": "refresh-scope-axis-remediation-displacement-aftercare witness",
    "open_question": NEXT_OQ,
    "applicability_conditions": [
        "a revision already has a row whose current claim depends on corroborating axes that are already judged genuinely independent, materially backed, decoupled under perturbation, hard-enforced, durable, explicitly restored, honest about collateral width, and honest about whether restored placement reused free capacity or displaced unrelated lower-priority work",
        "later passes still need to distinguish resumable-displacement-aftercare, terminal-displacement-aftercare, or mixed-refresh-scope-axis-remediation-displacement-aftercare posture",
        "one compact successor surface plus the existing admitted refresh-scope-axis-remediation-capacity-source and related scheduler surfaces still keeps aftercare truth honest without standing resume-credit or checkpoint machinery",
    ],
    "baselines": [
        "prior refresh-scope-axis-remediation-capacity-source witness already names whether displacement happened at all",
        "current question is only whether the displaced work retained a live return path or was terminally sacrificed",
    ],
    "non_fit_slice": "questions about restart-depth accounting, checkpoint quality, or restitution policy do not fit this compact witness",
}
append_item("APPLICABILITY-LEDGER.json", app_item)

fp_item = {
    "id": FP,
    "title": "Slurm, Kubernetes, Kueue, and Run:ai all force aftercare truth once preemption-backed repair is in play",
    "state": "adopted",
    "pressure_summary": "Official scheduler and workload docs distinguish suspend or requeue paths that preserve a live return route from cancel or deactivation paths that terminate the displaced work, so DelayBasin should keep aftercare truth explicit once capacity-source truth is already in play.",
    "sources": [
        "docs/00-meta/bibliography.md#ref-0991",
        "docs/00-meta/bibliography.md#ref-0993",
        "docs/00-meta/bibliography.md#ref-0994",
        "docs/00-meta/bibliography.md#ref-0995",
        "docs/00-meta/bibliography.md#ref-0996",
        "docs/00-meta/bibliography.md#ref-0997",
        "docs/00-meta/bibliography.md#ref-0998",
    ],
    "why_now": "rev0260 made capacity-source truth explicit, and the next honest ambiguity is what happened afterward to the work that paid the preemption bill.",
    "imported_pressure": "Keep resumable displacement distinct from terminal sacrifice.",
    "quarantined_non_take": [QWS_LABEL],
    "pressure_state": "adopted",
    "repair": "ordinary-continuation",
    "origin_revision": REV,
    "revision": REV,
    "witness_surface": f"FOREIGN-PRESSURE-LEDGER.json#{FP}",
    "action_lane": "keep-compact",
    "gate_class": "concrete-evidence",
    "discharge": "retain-unless-a-later-revision-needs-stronger-resumption-accounting",
}
append_item("FOREIGN-PRESSURE-LEDGER.json", fp_item)

tl_item = {
    "id": TL,
    "title": "refresh-scope-axis-remediation-displacement-aftercare evidence supports resolving OQ-0156 with one compact resumable-vs-terminal card rather than a resume credit ledger",
    "state": "supporting-only",
    "reviewed_pattern": "resumable displacement aftercare vs terminal displacement aftercare across already preemption-backed repaired corroboration",
    "import_decision": "support a compact refresh-scope-axis-remediation-displacement-aftercare witness and resolve OQ-0156",
    "adopted_take": "DelayBasin should add one compact witness that says whether displaced lower-priority work remained on a live resumption path, became terminally sacrificed, or honestly mixed the two",
    "supporting_only_take": "the current evidence cleanly supports a bounded refresh-scope-axis-remediation-displacement-aftercare witness without promoting broader resume-credit governance",
    "deferred_or_rejected_take": ["resume credit", "checkpoint escrow", "restart tax"],
    "local_gap": "the archive still lacked one compact successor surface for whether lower-priority work displaced by repair remained resumable or became terminally sacrificed",
    "anchor_surfaces": [
        "docs/10-method/refresh-scope-axis-remediation-capacity-source-witnesses-free-capacity-restoration-preemption-backed-restoration-and-mixed-restoration.md",
        "docs/20-constitution/open-question-registry.md",
        "docs/00-meta/trajectory-map.md",
        f"docs/90-quarantine/wild-speculations-2026-03-08.md#{QWS}",
    ],
    "open_question": NEXT_OQ,
    "repair": "ordinary-continuation",
    "origin_revision": REV,
    "action_lane": "keep-compact",
    "gate_class": "concrete-evidence",
    "discharge": "reopen-only-if-refresh-scope-axis-remediation-displacement-aftercare-overflows",
    "revision": REV,
    "witness_surface": f"DATACUBE-TRANSFER-LEDGER.json#{TL}",
    "transfer_state": "supporting-only",
    "bounded_take": "Keep the archive compact by extracting one refresh-scope-axis-remediation-displacement-aftercare witness over the existing refresh-scope-axis-remediation-capacity-source and related admitted surfaces; do not promote a resume credit board, checkpoint escrow, or restart tax.",
    "explicit_non_take": ["no resume credit ledger", "no checkpoint escrow", "no restart tax"],
    "open_transfer_question": "whether later passes should add a separate remediation-displacement-resumption-basis witness once aftercare is explicit",
    "missing_support": "a later public check on whether one compact refresh-scope-axis-remediation-displacement-aftercare witness keeps sufficing",
    "current_support": [f"APPLICABILITY-LEDGER.json#{AP}", f"FOREIGN-PRESSURE-LEDGER.json#{FP}", f"DATACUBE-TRANSFER-LEDGER.json#{TL}"],
    "discharge_path": "either show later that one compact refresh-scope-axis-remediation-displacement-aftercare witness keeps sufficing or promote broader resumption governance explicitly",
    "reviewed_datacubes": [
        {
            "datacube": "SlurmPreemptionAftercare-2026",
            "surfaces": ["REF-0991", "REF-0993"],
            "pattern": "Slurm separates suspend, requeue, and cancel preemption modes",
            "pressure": "resumable and terminal aftercare should remain distinct",
        },
        {
            "datacube": "KubernetesJobSuspendRetry-2026",
            "surfaces": ["REF-0994", "REF-0995"],
            "pattern": "Jobs can resume after suspension or ignored disruptions but can also terminate on disruption",
            "pressure": "controller-managed resumability should not be flattened into sacrifice",
        },
        {
            "datacube": "KueueRequeueDeactivation-2026",
            "surfaces": ["REF-0996", "REF-0997"],
            "pattern": "Kueue requeues workloads with backoff and later deactivates them when limits are exceeded",
            "pressure": "live requeue paths should stay distinct from terminal deactivation",
        },
        {
            "datacube": "RunAiCheckpointResume-2026",
            "surfaces": ["REF-0998"],
            "pattern": "preemptible workloads pause, later resume, and may rely on checkpoints to preserve progress",
            "pressure": "GPU aftercare should not be narrated as outright sacrifice when it stays resumable",
        },
    ],
}
append_item("DATACUBE-TRANSFER-LEDGER.json", tl_item)

res_item = {
    "id": RS,
    "title": "resolve OQ-0156 with one compact refresh-scope-axis-remediation-displacement-aftercare witness rather than a resume credit ledger",
    "state": "resolved",
    "closure_state": "resolved",
    "closure_reason": "rev0261 extracted one compact refresh-scope-axis-remediation-displacement-aftercare witness, kept the admitted refresh-scope-axis-remediation-capacity-source and related analog surfaces narrow, and kept stronger resume-credit stories quarantined.",
    "discharge": "reopen-only-if-refresh-scope-axis-remediation-displacement-aftercare-overflows",
    "gate_class": "concrete-evidence",
    "origin_revision": REV,
    "prior_state": "open gap: DelayBasin already had refresh-scope-axis-remediation-capacity-source truth but still lacked one compact successor surface for whether displaced lower-priority work remained resumable or was terminally sacrificed.",
    "question": "whether one compact refresh-scope-axis-remediation-displacement-aftercare witness over the existing refresh-scope-axis-remediation-capacity-source and related admitted surfaces is enough for honest resumable-vs-terminal aftermath comparison",
    "reopen_trigger": "refresh-scope-axis-remediation-displacement-aftercare pressure overflows one compact successor surface",
    "reopen_triggers": [
        "later revisions need standing governance over in-memory resume versus checkpoint replay versus cold restart, explicit restitution, or broader restart accounting that one compact refresh-scope-axis-remediation-displacement-aftercare witness cannot honestly absorb",
    ],
    "repair": "ordinary-continuation",
    "resolved_objects": [OQ, AP, FP, TL],
    "revision": REV,
    "successor_surface": NEW_DOC,
    "target_surfaces": [NEW_DOC],
    "action_lane": "keep-compact",
    "witness_surface": f"RESOLUTION-LEDGER.json#{RS}",
}
append_item("RESOLUTION-LEDGER.json", res_item)

rt_item = {
    "id": RT,
    "title": "revisit whether refresh-scope-axis-remediation-displacement-aftercare pressure stayed bounded after rev0261",
    "state": "cooling",
    "candidate_surface": f"docs/90-quarantine/wild-speculations-2026-03-08.md#{QWS}",
    "cooldown_window": "keep the stronger resume credit, checkpoint escrow, or restart tax story cooled until at least one later revision shows that one compact refresh-scope-axis-remediation-displacement-aftercare witness is no longer enough.",
    "adjudication_family": "refresh scope axis remediation displacement aftercare / resumability / sacrifice pressure",
    "supersession_link": f"OBLIGATION-LEDGER.json#{OB}",
    "origin_revision": REV,
    "discharge": "keep-cooling-unless-refresh-scope-axis-remediation-displacement-aftercare-overflows",
    "action_lane": "keep-compact",
    "gate_class": "overflow",
    "witness_surface": f"RETROSPECTIVE-QUEUE.json#{RT}",
    "revision": REV,
    "cooling_state": "cooling",
    "disposition": "await-adjudication",
    "repair": "keep-cooling",
}
append_item("RETROSPECTIVE-QUEUE.json", rt_item)

fb_item = {
    "id": FB,
    "title": "the refresh-scope-axis-remediation-displacement-aftercare import should count as one compact resumable-vs-terminal repair, not as permission to narrate a resume-credit court",
    "state": "quarantined",
    "witness_surface": f"FIREBREAK-LEDGER.json#{FB}",
    "judged_property": "the rev0261 decision that DelayBasin should extract one compact refresh-scope-axis-remediation-displacement-aftercare witness over the existing refresh-scope-axis-remediation-capacity-source and related admitted surfaces and `refresh_scope_axis_remediation_displacement_aftercare_state` family while the broader resume credit / checkpoint escrow / restart tax story remains quarantined",
    "public_extract": "Keep one compact resumable-vs-terminal aftercare card; do not infer a standing resume-credit board.",
    "withheld_trace_surface": "private working notes / search trace",
    "allowed_role": "brief public reasoning summary only",
    "exposure_rule": "do not expose raw private chain-of-thought or unpublished scratch reasoning; expose only the compact cited rationale and named successor surfaces",
    "trace_state": "quarantined",
    "repair": "ordinary-continuation",
    "origin_revision": REV,
    "action_lane": "keep-compact",
    "gate_class": "negative-transfer",
    "firebreak_surface": f"FIREBREAK-LEDGER.json#{FB}",
    "discharge": "retain-unless-a-later-revision-openly-promotes-resumption-governance",
    "revision": REV,
    "blocked_object": "resume credit / checkpoint escrow / restart tax",
}
append_item("FIREBREAK-LEDGER.json", fb_item)

ft_item = {
    "id": FT,
    "title": "keep checking whether refresh-scope-axis-remediation-displacement-aftercare pressure still fits inside one compact successor surface",
    "state": "queued",
    "blocked_object": QWS_LABEL,
    "local_surface": f"docs/90-quarantine/wild-speculations-2026-03-08.md#{QWS}",
    "followthrough_state": "queued",
    "boundary": "do not promote bounded refresh-scope-axis-remediation-displacement-aftercare clarification into a general resume-credit machine",
    "next_proof_surface": NEW_DOC,
    "receiving_surface": f"FOLLOWTHROUGH-QUEUE.json#{FT}",
    "repair": "ordinary-continuation",
    "origin_revision": REV,
    "discharge": "revisit-on-next-real-refresh-scope-axis-remediation-displacement-aftercare-overflow",
    "action_lane": "keep-compact",
    "gate_class": "overflow",
    "blocked_output": QWS_LABEL,
    "owner_surface": f"OBLIGATION-LEDGER.json#{OB}",
    "revision": REV,
    "missing_support": "a later public check on whether one compact aftercare witness keeps overflowing the bounded rule and honestly warrants richer resumption governance",
    "candidate_surface": f"docs/90-quarantine/wild-speculations-2026-03-08.md#{QWS}",
    "blocked_by": "need repeated evidence that resumable-vs-terminal aftercare truth overflows one compact witness",
}
append_item("FOLLOWTHROUGH-QUEUE.json", ft_item)

wv = load_json("WITNESS-VOCABULARY.json")
if FAMILY not in wv["families"]:
    new_cf = {}
    inserted = False
    for k, v in wv["families"].items():
        new_cf[k] = v
        if k == "refresh_scope_axis_remediation_capacity_source_state":
            new_cf[FAMILY] = {
                "allowed": ALLOWED,
                "surfaces": ["WITNESS-VOCABULARY.json", "REVISION-RECEIPT.json", NEW_DOC],
                "excluded_synonyms": EXCLUDED,
                "comparability_budget": "refresh-scope-axis-remediation-displacement-aftercare truth is compared by token; the compact witness says whether displaced work stayed resumable, became terminal, or honestly mixed the two while raw eviction histories, checkpoint traces, retry counters, and scheduler logs stay in surrounding prose",
            }
            inserted = True
    if not inserted:
        new_cf[FAMILY] = {
            "allowed": ALLOWED,
            "surfaces": ["WITNESS-VOCABULARY.json", "REVISION-RECEIPT.json", NEW_DOC],
            "excluded_synonyms": EXCLUDED,
            "comparability_budget": "refresh-scope-axis-remediation-displacement-aftercare truth is compared by token; the compact witness says whether displaced work stayed resumable, became terminal, or honestly mixed the two while raw eviction histories, checkpoint traces, retry counters, and scheduler logs stay in surrounding prose",
        }
    wv["families"] = new_cf
    dump_json("WITNESS-VOCABULARY.json", wv)

receipt = load_json("REVISION-RECEIPT.json")
receipt["revision"] = REV
receipt["previous_revision"] = PREV
receipt["summary"] = "Resolved refresh-scope-axis-remediation displacement aftercare with a compact resumable-vs-terminal witness, honestly quarantined stronger resume-credit governance, and refactored bundle-name construction so packaging stays small and wired."
receipt["canon_additions"] = [NEW_DOC, f"{RS} resolved {OQ} with one compact refresh-scope-axis-remediation-displacement-aftercare witness"]
receipt["quarantine_additions"] = [f"docs/90-quarantine/wild-speculations-2026-03-08.md#{QWS}"]
receipt["refs_used"] = [
    "docs/00-meta/bibliography.md#ref-0991",
    "docs/00-meta/bibliography.md#ref-0993",
    "docs/00-meta/bibliography.md#ref-0994",
    "docs/00-meta/bibliography.md#ref-0995",
    "docs/00-meta/bibliography.md#ref-0996",
    "docs/00-meta/bibliography.md#ref-0997",
    "docs/00-meta/bibliography.md#ref-0998",
]
receipt["checks_passed"] = ["make lint"]
receipt["touched_surfaces"] = [
    NEW_DOC,
    "docs/00-meta/bibliography.md",
    "docs/00-meta/llm-runbook.md",
    "docs/README.md",
    "docs/20-constitution/claim-registry.md",
    "docs/20-constitution/open-question-registry.md",
    "docs/20-constitution/prompt-pair-registry.md",
    "docs/00-meta/trajectory-map.md",
    "docs/50-promptcraft/prompt-pairs.md",
    "docs/90-quarantine/wild-speculations-2026-03-08.md",
    "WITNESS-VOCABULARY.json",
    "FOLLOWTHROUGH-QUEUE.json",
    "ASSUMPTION-LEDGER.json",
    "OBLIGATION-LEDGER.json",
    "APPLICABILITY-LEDGER.json",
    "FOREIGN-PRESSURE-LEDGER.json",
    "DATACUBE-TRANSFER-LEDGER.json",
    "RESOLUTION-LEDGER.json",
    "RETROSPECTIVE-QUEUE.json",
    "FIREBREAK-LEDGER.json",
    "REVISION-RECEIPT.json",
    "SURFACE-STATUS.json",
    "RELEASE-MANIFEST.json",
    "CHANGELOG.md",
    "ARCHIVE_INDEX.md",
    "tools/packet_contract_common.py",
    NEW_CHECKER,
    "tools/release_hygiene_lib.py",
    "tools/package_release.py",
    "apply_rev0261.py",
]
receipt["packaged_release"] = True
receipt["packaged_bundle_filename"] = BUNDLE
receipt["basis_witness"].update({
    "expected_head": PREV,
    "observed_head": PREV,
    "basis_surfaces": [
        "docs/10-method/refresh-scope-axis-remediation-capacity-source-witnesses-free-capacity-restoration-preemption-backed-restoration-and-mixed-restoration.md",
        "docs/00-meta/trajectory-map.md",
        "docs/20-constitution/open-question-registry.md",
    ],
    "session_provenance": f"DelayBasin-{PREV}-2026.03.28.07.24-capacitysource-debtq-preemptcarry-queueglass.zip",
    "basis_omission_basis": "broader resumption accounting was intentionally omitted from canon because the evidence only justified one bounded refresh-scope-axis-remediation-displacement-aftercare witness",
    "origin_revision": REV,
    "revision_span": f"{PREV} -> {REV}",
})
receipt["scope_witness"].update({
    "exact_target": "one compact refresh-scope-axis-remediation-displacement-aftercare witness plus one quarantined resume-credit move and one small packaging-helper refactor",
    "scope_surfaces": [
        "docs/20-constitution/open-question-registry.md",
        "docs/00-meta/trajectory-map.md",
        NEW_DOC,
        f"docs/90-quarantine/wild-speculations-2026-03-08.md#{QWS}",
        "tools/release_hygiene_lib.py",
        "tools/package_release.py",
    ],
    "scope_of_change": "refresh-scope-axis-remediation-displacement-aftercare",
    "origin_revision": REV,
})
receipt["authorship_witness"]["origin_revision"] = REV
receipt["status_witness"].update({"frozen_public_surface": BUNDLE})
receipt["reentry_cue_witness"]["origin_revision"] = REV
receipt["retrospective_write_witness"] = rt_item
receipt["followthrough_witness"] = ft_item
receipt["assumption_witness"] = assumption_item
receipt["obligation_witness"] = ob_item
receipt["applicability_witness"] = app_item
receipt["foreign_pressure_witness"] = fp_item
receipt["transfer_witness"] = tl_item
receipt["resolution_witness"] = res_item
receipt["reasoning_firebreak_witness"] = fb_item
receipt["vocabulary_witness"] = {
    "witness_surface": "WITNESS-VOCABULARY.json",
    "controlled_families": [FAMILY, "action_lane", "gate_class"],
    "target_surfaces": [
        "WITNESS-VOCABULARY.json",
        "REVISION-RECEIPT.json",
        NEW_DOC,
        "FOLLOWTHROUGH-QUEUE.json",
        "RETROSPECTIVE-QUEUE.json",
        "ASSUMPTION-LEDGER.json",
        "OBLIGATION-LEDGER.json",
        "APPLICABILITY-LEDGER.json",
        "FOREIGN-PRESSURE-LEDGER.json",
        "DATACUBE-TRANSFER-LEDGER.json",
        "RESOLUTION-LEDGER.json",
        "FIREBREAK-LEDGER.json",
    ],
    "ambient_synonyms_excluded": EXCLUDED,
    "comparability_budget": "refresh-scope-axis-remediation-displacement-aftercare truth is compared by token; the compact witness says whether displaced work stayed resumable, became terminal, or honestly mixed the two while raw eviction histories, checkpoint traces, retry counters, and scheduler logs stay outside the token",
    "vocabulary_state": "locked",
    "repair": "ordinary-continuation",
    FAMILY: wv["families"][FAMILY],
    "action_lane": load_json("REVISION-RECEIPT.json")["vocabulary_witness"]["action_lane"],
    "gate_class": load_json("REVISION-RECEIPT.json")["vocabulary_witness"]["gate_class"],
}
receipt["counterfactual_shadow"] = {
    "status": "quarantined",
    "nearby_rejected_move": QWS_LABEL,
    "pivot_surface": f"docs/90-quarantine/wild-speculations-2026-03-08.md#{QWS}",
    "rejection_reason": "the current evidence supports one compact resumable-vs-terminal witness but not a standing resume-credit economy",
    "still_live": True,
}
receipt["summary_highlight"] = SUMMARY_HIGHLIGHT
receipt["codename"] = CODENAME
receipt["created_at"] = CREATED_AT
receipt["comparison_witness"] = {
    "previous_revision": PREV,
    "current_revision": REV,
    "current_pressure_id": FP,
    "current_import_id": TL,
    "basis_surface": "docs/10-method/refresh-scope-axis-remediation-capacity-source-witnesses-free-capacity-restoration-preemption-backed-restoration-and-mixed-restoration.md",
    "delta_surface": NEW_DOC,
    "comparison_summary": "rev0261 adds one compact refresh-scope-axis-remediation-displacement-aftercare witness so preemption-backed repair no longer all reads as if suspended, requeued, and sacrificed work were the same class of aftermath.",
}
receipt["changes"] = [
    {"kind": "canon", "surface": NEW_DOC, "summary": "added one compact refresh-scope-axis-remediation-displacement-aftercare witness with resumable, terminal, and mixed states"},
    {"kind": "quarantine", "surface": f"docs/90-quarantine/wild-speculations-2026-03-08.md#{QWS}", "summary": "kept stronger resume-credit or checkpoint-escrow governance quarantined rather than promoting it into canon"},
    {"kind": "hygiene", "surface": "tools/release_hygiene_lib.py", "summary": "factored bundle-name construction into release hygiene helpers so packaging and exclusion logic stay wired to one canonical release stem"},
]
receipt["firebreak_witness"] = fb_item
receipt["receipt_freshness_witness"] = {
    "packaged_bundle_filename": BUNDLE,
    "manifest_timestamp_token": STAMP,
    "receipt_timestamp_token": STAMP,
    "bundle_stem_suffix_relation": f"slug ends with {SUMMARY_HIGHLIGHT} and {CODENAME} as summary highlight and codename",
    "current_import_id": TL,
    "current_pressure_id": FP,
    "change_anchor_surface": NEW_DOC,
    "freshness_state": "current-aligned",
    "repair": "ordinary-continuation",
}
receipt["question_posture_witness"] = {
    "resolution_surface": "RESOLUTION-LEDGER.json",
    "registry_surface": "docs/20-constitution/open-question-registry.md",
    "trajectory_surface": "docs/00-meta/trajectory-map.md",
    "synced_resolved_questions": [OQ],
    "frontier_selection_rule": "select the last source-backed unresolved hot open question already projected into context-pack.json",
    "posture_state": "resolved-sync-current",
    "repair": "ordinary-continuation",
}
receipt["current_import_id"] = TL
receipt["current_pressure_id"] = FP
receipt["import_witness"] = tl_item
receipt["new_classes_or_families"] = [FAMILY]
receipt["quarantined_non_take"] = ["resume credit", "checkpoint escrow", "restart tax"]
receipt["artifacts_touched"] = list(receipt["touched_surfaces"])
receipt["bundle"] = BUNDLE
receipt["slug"] = SLUG
receipt["resolved_question"] = OQ
receipt["next_open_question"] = NEXT_OQ
receipt["canonical_additions"] = [NEW_DOC]
receipt["checker_additions"] = [NEW_CHECKER]
receipt["change_summary"] = [
    {"kind": "canon", "surface": NEW_DOC, "summary": "added one compact refresh-scope-axis-remediation-displacement-aftercare witness for resumable versus terminal aftercare"},
    {"kind": "quarantine", "surface": f"docs/90-quarantine/wild-speculations-2026-03-08.md#{QWS}", "summary": "kept the stronger resume credit / checkpoint escrow / restart tax move explicitly quarantined"},
    {"kind": "hygiene", "surface": "tools/release_hygiene_lib.py", "summary": "factored bundle-name construction into release hygiene helpers so packaging stays synchronized"},
]
receipt["refresh_scope_axis_remediation_displacement_aftercare_witness"] = {
    "witness_surface": NEW_DOC,
    "family": FAMILY,
    "allowed_tokens": ALLOWED,
    "overflow_rule": "reopen-only-if-refresh-scope-axis-remediation-displacement-aftercare-overflows",
}
receipt["refresh_scope_axis_remediation_displacement_aftercare_witness_contract"] = {
    "family": FAMILY,
    "allowed_tokens": ALLOWED,
}
receipt["refresh_scope_axis_remediation_displacement_aftercare_witness_meta"] = {"checker": NEW_CHECKER}
receipt["refresh_scope_axis_remediation_capacity_source_witness_meta"] = receipt.get("refresh_scope_axis_remediation_capacity_source_witness_meta", {"checker": "tools/check_refresh_scope_axis_remediation_capacity_source_witness_contract.py"})
dump_json("REVISION-RECEIPT.json", receipt)

status = load_json("SURFACE-STATUS.json")
status["operational_head"]["revision"] = REV
status["status_lanes"]["frozen_public_surface"] = BUNDLE
status["status_lanes"]["current_release_surface"] = BUNDLE
status["citation_head"]["revision"] = REV
status["citation_head"]["surface"] = BUNDLE
status["previous_citation_head"]["revision"] = PREV
status["previous_citation_head"]["surface"] = f"DelayBasin-{PREV}-2026.03.28.07.24-capacitysource-debtq-preemptcarry-queueglass.zip"
status["revision"] = REV
status["stamp"] = STAMP
status["slug"] = SLUG
dump_json("SURFACE-STATUS.json", status)

dump_json("RELEASE-MANIFEST.json", {"project": "DelayBasin", "revision": REV, "timestamp": STAMP, "slug": SLUG, "bundle": BUNDLE})

new_changelog = f"## {REV} - {STAMP} - aftercare / resumeq / {SUMMARY_HIGHLIGHT} / {CODENAME}\n\n- Added `{NEW_DOC}` to resolve `{OQ}` with a compact resumable-vs-terminal remediation-displacement-aftercare witness.\n- Kept the stronger resume credit / checkpoint escrow / restart tax move explicitly quarantined as `{QWS}` instead of laundering it into canon.\n- Hygiene/meta-engineering improvement: factored bundle-name construction into `tools/release_hygiene_lib.py` so packaging and release skipping share one canonical helper, while adding `{NEW_CHECKER}` through the shared refresh-scope-axis branch scaffold.\n\n"
write_text("CHANGELOG.md", new_changelog + read_text("CHANGELOG.md"))

archive_text = read_text("ARCHIVE_INDEX.md")
legacy_idx = archive_text.find("\nLegacy continuity markers")
if legacy_idx == -1:
    raise RuntimeError("ARCHIVE_INDEX.md missing legacy marker")
body = archive_text[:legacy_idx].strip().splitlines()
rows = [line for line in body if line.startswith("| DelayBasin-")]
new_row = f"| {BUNDLE} | 2026-03-28 | Refresh-scope-axis-remediation-displacement-aftercare revision: resolved {OQ} with a compact resumable-vs-terminal witness, honestly quarantined stronger resume-credit governance, and refactored bundle-name helpers so packaging stays wired and cumulative. |"
if new_row not in rows:
    rows.insert(0, new_row)
rest = archive_text[legacy_idx:].lstrip("\n")
archive_new = "# Archive index\n\n| Bundle | Date | Notes |\n| --- | --- | --- |\n" + "\n".join(rows) + "\n\n" + rest
write_text("ARCHIVE_INDEX.md", archive_new)

print(f"Applied {REV}")
