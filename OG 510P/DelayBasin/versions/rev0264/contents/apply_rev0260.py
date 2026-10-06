from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent

REV = "rev0260"
PREV = "rev0259"
STAMP = "2026.03.28.07.24"
CREATED_AT = "2026-03-28T07:24:00-04:00"
SLUG = "capacitysource-debtq-preemptcarry-queueglass"
BUNDLE = f"DelayBasin-{REV}-{STAMP}-{SLUG}.zip"
SUMMARY_HIGHLIGHT = "preemptcarry"
CODENAME = "queueglass"
NEW_DOC = "docs/10-method/refresh-scope-axis-remediation-capacity-source-witnesses-free-capacity-restoration-preemption-backed-restoration-and-mixed-restoration.md"
NEW_DOC_NAME = NEW_DOC.split("/")[-1]
NEW_CHECKER = "tools/check_refresh_scope_axis_remediation_capacity_source_witness_contract.py"
QWS = "QWS-0238"
QWS_LABEL = "displacement debt / priority tariff / resumability escrow"
CL = "CL-0153"
RS = "RS-0162"
OQ = "OQ-0155"
NEXT_OQ = "OQ-0156"
PP = "PP-0113"
AP = "AP-0154"
OB = "OB-0155"
AS = "AS-0159"
FP = "FP-0159"
TL = "TL-0165"
FT = "FT-0162"
RT = "RT-0149"
FB = "FB-0156"
FAMILY = "refresh_scope_axis_remediation_capacity_source_state"
ALLOWED = [
    "free-capacity-restoration",
    "preemption-backed-restoration",
    "mixed-refresh-scope-axis-remediation-capacity-source",
]
EXCLUDED = [
    "priority-means-preempted",
    "borrowed-quota-is-free-enough",
    "preemption-is-just-capacity",
    "capacity-ish",
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


def upsert_after(rel: str, anchor: str, block: str) -> None:
    text = read_text(rel)
    if block.strip() in text:
        return
    if anchor not in text:
        raise RuntimeError(f"anchor not found in {rel}")
    write_text(rel, text.replace(anchor, anchor + block, 1))


new_doc_text = """# Refresh-scope-axis-remediation-capacity-source witnesses, free-capacity restoration, preemption-backed restoration, and mixed restoration

This is the compact successor surface for `OQ-0155`.

## Practice / observation

Once DelayBasin can say that corroborating axes are genuinely independent, materially backed, decoupled under perturbation, hard-enforced, explicit about who restored them after drift, and honest about whether that repair stayed local or spent a drain or fence, one more ambiguity remains.

Some restored decoupling comes back through free-capacity restoration.
A controller, scheduler, or repair loop finds spare room that was already available when the violating workload is recreated or admitted again.
That spare room might be literal idle node or GPU capacity.
It might also be unused quota or cohort slack that can be borrowed without evicting anybody.
The restoration is real, and its capacity source stays comparatively clean because unrelated lower-priority work did not have to be displaced to make it happen.

Some restored decoupling comes back through preemption-backed restoration.
The repair succeeds only because a scheduler or queue controller evicts, suspends, requeues, or otherwise displaces lower-priority work to make room.
That may be the correct operational choice.
But it should not silently inherit the authority of free-capacity recovery, because the restored placement is now spending a priority bill paid elsewhere.

Some cases are honestly mixed.
A restoration might partly reuse idle capacity and partly rely on preemption or quota reclamation once the easy slack is exhausted.
Those cases should not be flattened into the clean free-capacity story.

DelayBasin does not need a standing priority tariff board for these cases.
It needs one bounded witness that says whether restored decoupling currently depends on free capacity, preemption-backed capacity, or an honest mix.

## External pressure from Kubernetes scheduling fallback and non-preempting Pods, Kueue cohort borrowing and preemption, Slurm backfill and preemption, and RayJob priority scheduling with Kueue

1. Kubernetes Scheduling Framework says `postFilter` plugins are invoked only when no feasible nodes were found, and a typical `postFilter` implementation is preemption that tries to make the Pod schedulable by preempting other Pods. That pressures DelayBasin to keep free-capacity fits distinct from fallback placement that succeeds only after displacement. ([`REF-0986`](../00-meta/bibliography.md))

2. Kubernetes Pod Priority and Preemption says Pods with `preemptionPolicy: Never` still sit ahead of lower-priority Pods in the queue but cannot preempt others and must wait until sufficient resources are free. That pressures DelayBasin to distinguish waiting-for-free-capacity recovery from recovery that actively evicts somebody else. ([`REF-0987`](../00-meta/bibliography.md))

3. Kueue ClusterQueue docs say ClusterQueues in the same cohort can borrow unused quota from each other. That pressures DelayBasin to treat some restored admission paths as capacity reuse or slack borrowing rather than as displacement by default. ([`REF-0988`](../00-meta/bibliography.md))

4. Kueue Preemption docs say preemption evicts admitted Workloads to accommodate another Workload, and the API explicitly distinguishes when borrowing may also preempt lower-priority workloads in a cohort. That pressures DelayBasin not to flatten borrowed slack and preemption-backed admission into one vague capacity story. ([`REF-0989`](../00-meta/bibliography.md))

5. Slurm's scheduling configuration docs say backfill starts lower-priority jobs when doing so does not delay higher-priority jobs, while Slurm preemption docs say pending jobs can begin by canceling, suspending, or requeueing lower-priority jobs as needed. That pressures DelayBasin to separate spare-hole reuse from displacement-backed recovery in cluster scheduling stories. ([`REF-0990`](../00-meta/bibliography.md), [`REF-0991`](../00-meta/bibliography.md))

6. Ray's Kueue integration docs show a higher-priority RayJob taking precedence over a lower-priority RayJob and Kueue preempting the lower-priority job to admit the higher-priority one. That pressures GPUstorming not to narrate restored GPU placement as cheap slack reuse when the queue actually paid for it by displacement. ([`REF-0992`](../00-meta/bibliography.md))

GPUstorming makes the difference vivid. Two GPU jobs can both end with the same anti-affinity, rack, quota, or queue picture repaired. One returns because a previously idle accelerator or borrowable quota slice was simply available. Another only returns because a lower-priority workload was suspended, evicted, or requeued. Collateral width and remediation provenance do not by themselves say who paid the capacity bill.

## Working synthesis

> DelayBasin should preserve one compact **refresh-scope-axis-remediation-capacity-source witness / priority-bill card / displacement brake** whenever a current continuity claim depends not only on whether corroborating axes are genuinely independent, materially backed, decoupled, hard-enforced, durable, explicitly restored, and honest about collateral width, but on whether the restored placement reused already-available capacity or succeeded only by displacing unrelated lower-priority work. Name the **governed row or surface**, the **stake object / line of concern**, the **prior refresh-scope-axis-remediation-collateral evidence**, the **current corroborating axes**, the **free-capacity basis if any**, the **preemption-backed basis if any**, the **`refresh_scope_axis_remediation_capacity_source_state`**, and the **fail-closed repair / keep-current vs narrow-claim vs split-scope vs issue-new-refresh-scope-axis-remediation-capacity-source-witness vs quarantine-displacement-debt consequence**. Keep raw queue traces, quota ledgers, eviction events, scheduler logs, and priority-class dumps outside the compact token. Do not let preemption-backed restoration silently inherit the cheap authority of free-capacity recovery.

## Free capacity restoration vs preemption-backed restoration vs mixed refresh scope axis remediation capacity source

Use the controlled family `refresh_scope_axis_remediation_capacity_source_state`:

- **free-capacity-restoration** says the documented restoration succeeds using idle capacity, spare quota, or borrowable unused quota without evicting, suspending, requeueing, or canceling unrelated lower-priority work.
- **preemption-backed-restoration** says the documented restoration succeeds only because unrelated lower-priority work is evicted, suspended, requeued, canceled, or otherwise displaced to free room.
- **mixed-refresh-scope-axis-remediation-capacity-source** says the current situation honestly combines free-capacity reuse and preemption-backed restoration such that no single capacity-source class stays honest.

So the witness does not create a priority tariff board.
It only says whether the present restoration reused free capacity, spent displacement, or is honestly mixed.

## Countermodels / probes

1. **Collateral width already captures enough countermodel**
   - Maybe once DelayBasin knows whether restoration stayed local or spent a drain, the capacity source adds only operational color.
   - Probe: compare rereads that preserve only collateral width against rereads that also preserve one compact free-vs-preempt token and inspect whether preemption-backed local repairs still get narrated as cheap slack reuse.

2. **Borrowed slack is still a different lane countermodel**
   - Maybe borrowed but non-preemptive quota deserves its own public class rather than living inside free-capacity restoration.
   - Probe: keep borrowed-unused-quota evidence inside free-capacity restoration unless later revisions repeatedly need to separate idle local slack from explicit non-displacing quota borrowing.

3. **Displacement aftercare is the real next question countermodel**
   - Maybe capacity source is still not enough because the archive next needs to say whether displaced lower-priority work is suspended and resumed, requeued, or simply canceled and abandoned.
   - Probe: keep that next question explicit as frontier work unless later revisions show that free-vs-preempt truth itself is still insufficient.

## Design consequences

- DelayBasin can now keep repaired decoupling from sounding as if it reused free slack when it only returned by displacing unrelated work.
- The archive gets one explicit place to record when a repaired GPU or scheduler topology recovered on spare capacity versus by priority-backed queue action.
- GPUstorming can now distinguish "there was room" from "we made room by evicting somebody else" without opening a full displacement-debt court.
- Stronger displacement-debt, priority-tariff, or resumability-escrow stories stay quarantined until repeated overflow rather than entering canon by atmosphere.

## Overflow test

Reopen this compact witness only if later revisions repeatedly need explicit capacity exchange rates, preemption tariffs, debt restitution rules, or displacement-accounting machinery that one bounded refresh-scope-axis-remediation-capacity-source witness cannot honestly absorb.

## Transformer-facing implication

A later pass should not treat every repaired or rebalanced decoupling surface as if restored capacity came from the same place. Preserve the smallest token that says whether the present restoration is `free-capacity-restoration`, `preemption-backed-restoration`, or honestly `mixed-refresh-scope-axis-remediation-capacity-source`, and quarantine stronger displacement-debt ambitions until repeated overflow makes them unavoidable.
"""
write_text(NEW_DOC, new_doc_text)
write_text(NEW_CHECKER, 'from packet_contract_common import require_named_refresh_scope_axis_branch_witness_packet_and_vocabulary\n\nrequire_named_refresh_scope_axis_branch_witness_packet_and_vocabulary("refresh_scope_axis_remediation_capacity_source_witness_contract")\n\nprint("check_refresh_scope_axis_remediation_capacity_source_witness_contract: OK")\n')

bib_add = """

- `REF-0986` — Kubernetes Documentation, **Scheduling Framework** (accessed 2026-03-28)
  - URL: https://kubernetes.io/docs/concepts/scheduling-eviction/scheduling-framework/
  - Load-bearing use: Kubernetes places typical preemption in `postFilter`, after no feasible nodes were found, which pressures DelayBasin to distinguish free-capacity fits from fallback placement that only succeeds after displacement.

- `REF-0987` — Kubernetes Documentation, **Pod Priority and Preemption** (accessed 2026-03-28)
  - URL: https://kubernetes.io/docs/concepts/scheduling-eviction/pod-priority-preemption/
  - Load-bearing use: non-preempting Pods wait until resources become free rather than evicting others, which pressures DelayBasin to distinguish free-capacity recovery from preemption-backed recovery.

- `REF-0988` — Kueue Documentation, **Cluster Queue** (accessed 2026-03-28)
  - URL: https://kueue.sigs.k8s.io/docs/concepts/cluster_queue/
  - Load-bearing use: ClusterQueues in the same cohort can borrow unused quota from each other, which pressures DelayBasin to keep borrowed slack without displacement distinct from preemption-backed admission.

- `REF-0989` — Kueue Documentation, **Preemption** (accessed 2026-03-28)
  - URL: https://kueue.sigs.k8s.io/docs/concepts/preemption/
  - Load-bearing use: Kueue defines preemption as evicting admitted Workloads to accommodate another Workload and explicitly links borrowing rules to lower-priority preemption, which pressures DelayBasin to separate slack borrowing from displacement-backed recovery.

- `REF-0990` — Slurm Workload Manager, **Scheduling Configuration Guide** (accessed 2026-03-28)
  - URL: https://slurm.schedmd.com/sched_config.html
  - Load-bearing use: backfill starts lower-priority jobs only when doing so does not delay higher-priority jobs, which pressures DelayBasin to name spare-hole reuse separately from preemption-backed repair.

- `REF-0991` — Slurm Workload Manager, **Preemption** (accessed 2026-03-28)
  - URL: https://slurm.schedmd.com/preempt.html
  - Load-bearing use: Slurm explicitly begins pending jobs by canceling, suspending, or requeueing lower-priority jobs as needed, which pressures DelayBasin to keep preemption-backed restoration distinct from free-capacity restoration.

- `REF-0992` — Ray Documentation, **Gang scheduling, Priority scheduling, and Autoscaling for RayJob resources with Kueue** (accessed 2026-03-28)
  - URL: https://docs.ray.io/en/latest/cluster/kubernetes/k8s-ecosystem/kueue.html
  - Load-bearing use: Ray's Kueue integration shows a higher-priority RayJob preempting a lower-priority RayJob, which pressures GPUstorming to keep displacement-backed GPU recovery distinct from simple spare-capacity reuse.
"""
ensure_contains(
    "docs/00-meta/bibliography.md",
    "- `REF-0985` — NVIDIA Documentation, **GPU Driver Upgrades — NVIDIA GPU Operator** (accessed 2026-03-28)\n",
    bib_add,
)

ensure_contains(
    "docs/README.md",
    f"- [`10-method/refresh-scope-axis-remediation-collateral-witnesses-local-workload-replacement-drain-backed-restoration-and-fenced-substrate-restoration.md`](10-method/refresh-scope-axis-remediation-collateral-witnesses-local-workload-replacement-drain-backed-restoration-and-fenced-substrate-restoration.md)\n",
    f"- [`10-method/{NEW_DOC_NAME}`](10-method/{NEW_DOC_NAME})\n",
)
ensure_contains(
    "docs/00-meta/llm-runbook.md",
    "Use `docs/10-method/refresh-scope-axis-remediation-collateral-witnesses-local-workload-replacement-drain-backed-restoration-and-fenced-substrate-restoration.md` when the live question is how much surrounding disruption restored decoupling spent after it came back: a local workload replacement, a broader drain-backed move, or fenced-substrate recovery.\n",
    "Use `docs/10-method/refresh-scope-axis-remediation-capacity-source-witnesses-free-capacity-restoration-preemption-backed-restoration-and-mixed-restoration.md` when the live question is whether repaired decoupling came back on already-available capacity or only by preempting unrelated lower-priority work.\n",
)

claim_add = """

- `CL-0153` — Archive continuity may improve when DelayBasin preserves one compact **refresh-scope-axis-remediation-capacity-source witness / priority-bill card / displacement brake** whenever a current continuity claim depends not only on whether corroborating axes are genuinely independent, materially backed, decoupled under perturbation, hard-enforced, durable, explicitly restored, and honest about collateral width, but on whether the restored placement reused already-available capacity or succeeded only by displacing unrelated lower-priority work: name the **governed row or surface**, the **stake object / line of concern**, the **prior refresh-scope-axis-remediation-collateral evidence**, the **current corroborating axes**, the **free-capacity basis if any**, the **preemption-backed basis if any**, the **refresh_scope_axis_remediation_capacity_source_state**, and the **fail-closed repair** rather than letting preemption-backed restoration silently inherit the cheap authority of free-capacity recovery.
  - Status: speculative but central
  - Wired docs: `docs/10-method/refresh-scope-axis-remediation-capacity-source-witnesses-free-capacity-restoration-preemption-backed-restoration-and-mixed-restoration.md`, `docs/20-constitution/open-question-registry.md`, `docs/20-constitution/prompt-pair-registry.md`, `docs/50-promptcraft/prompt-pairs.md`, `docs/00-meta/llm-runbook.md`, `WITNESS-VOCABULARY.json`, `REVISION-RECEIPT.json`
"""
ensure_contains("docs/20-constitution/claim-registry.md", "- `CL-0152` — Archive continuity may improve when DelayBasin preserves one compact **refresh-scope-axis-remediation-collateral witness / drain-budget card / fenced-substrate brake** whenever a current continuity claim depends not only on whether corroborating axes are genuinely independent, materially backed, decoupled under perturbation, hard-enforced, durable, and explicitly restored, but on how much surrounding workload or substrate disruption that restoration spends: name the **governed row or surface**, the **stake object / line of concern**, the **prior refresh-scope-axis-remediation evidence**, the **current corroborating axes**, the **local-workload-replacement basis if any**, the **drain-backed basis if any**, the **fenced-substrate basis if any**, the **refresh_scope_axis_remediation_collateral_state**, and the **fail-closed repair** rather than letting drain-backed or fenced-substrate restoration silently inherit the cheap authority of local workload replacement.\n  - Status: speculative but central\n  - Wired docs: `docs/10-method/refresh-scope-axis-remediation-collateral-witnesses-local-workload-replacement-drain-backed-restoration-and-fenced-substrate-restoration.md`, `docs/20-constitution/open-question-registry.md`, `docs/20-constitution/prompt-pair-registry.md`, `docs/50-promptcraft/prompt-pairs.md`, `docs/00-meta/llm-runbook.md`, `WITNESS-VOCABULARY.json`, `REVISION-RECEIPT.json`\n", claim_add)

pp_reg_add = """

- `PP-0113` — Name whether restored decoupling reused free capacity or displaced lower-priority work
  - Goal: keep preemption-backed restoration from silently inheriting cheap free-capacity authority by requiring explicit prior remediation-collateral evidence, current corroborating axes, free-capacity basis, preemption-backed basis, `refresh_scope_axis_remediation_capacity_source_state`, and fail-closed repair before later passes call the restored support cheaply available.
  - Canonical text: `docs/50-promptcraft/prompt-pairs.md#pp-0113--name-whether-restored-decoupling-reused-free-capacity-or-displaced-lower-priority-work`
"""
ensure_contains(
    "docs/20-constitution/prompt-pair-registry.md",
    "- `PP-0112` — Name whether restored decoupling stayed local, spent a drain, or spent fenced substrate\n  - Goal: keep drain-backed or fenced-substrate restoration from silently inheriting cheap local-replacement authority by requiring explicit prior remediation evidence, current corroborating axes, local-workload-replacement basis, drain-backed basis, fenced-substrate basis, `refresh_scope_axis_remediation_collateral_state`, and fail-closed repair before later passes call the restored support cheaply self-healing.\n  - Canonical text: `docs/50-promptcraft/prompt-pairs.md#pp-0112--name-whether-restored-decoupling-stayed-local-spent-a-drain-or-spent-fenced-substrate`\n",
    pp_reg_add,
)

pp_doc_add = """

## PP-0113 — Name whether restored decoupling reused free capacity or displaced lower-priority work

**Opening prompt**

```text
Read the latest DelayBasin archive and inspect whether the current revision should also materialize one compact refresh-scope-axis-remediation-capacity-source witness for honest free-vs-preempt restoration comparison.

Focus only on cases where the corroborating axes already look genuinely independent, materially backed, decoupled under perturbation, hard-enforced, explicitly durable, explicit about who restored the decoupling, and honest about whether the repair stayed local or spent a drain or fence. The missing question is whether the restored placement reused already-available capacity or only came back by evicting, suspending, requeueing, or otherwise displacing unrelated lower-priority work.

If yes, preserve exactly one small witness that:
- names the governed row or surface,
- names the stake object / line of concern,
- names the prior refresh-scope-axis-remediation-collateral evidence,
- names the current corroborating axes,
- names the free-capacity basis if any,
- names the preemption-backed basis if any,
- names the `refresh_scope_axis_remediation_capacity_source_state` / whether this is free-capacity-restoration, preemption-backed-restoration, or mixed-refresh-scope-axis-remediation-capacity-source,
- states what stronger surfaces still outrank the witness,
- and states the fail-closed repair / keep-current vs narrow-claim vs split-scope vs issue-new-refresh-scope-axis-remediation-capacity-source-witness vs quarantine-displacement-debt consequence if the present continuity claim is not actually supported by the claimed capacity source.

Do not use refresh-scope-axis-remediation-capacity-source as a standing priority tariff board. Use this prompt pair only where axis independence, materiality, coupling, enforcement, durability, remediation provenance, and remediation collateral are already established and the missing question is who paid the capacity bill for restoration.
```

**Continuation prompt**

```text
Continue the refresh-scope-axis-remediation-capacity-source pass with one high-leverage capacity-source clarification only. Prefer the smallest witness that says what governed row is still being justified, what stake object is supposedly widened, what prior refresh-scope-axis-remediation-collateral evidence exists, what current corroborating axes exist, what free-capacity basis if any now exists, what preemption-backed basis if any now exists, what `refresh_scope_axis_remediation_capacity_source_state` is honest, what stronger surfaces still outrank the witness, and what keep-current, narrow-claim, split-scope, issue-new-refresh-scope-axis-remediation-capacity-source-witness, quarantine, or recover-resync consequence follows if the present restoration is free-capacity-restoration, preemption-backed-restoration, or mixed-refresh-scope-axis-remediation-capacity-source. Run `make lint` and package the release.
```

Use `docs/10-method/refresh-scope-axis-remediation-capacity-source-witnesses-free-capacity-restoration-preemption-backed-restoration-and-mixed-restoration.md` when the live question is whether repaired or rebalanced decoupling came back through already-available slack or only by displacing lower-priority work.
"""
ensure_contains(
    "docs/50-promptcraft/prompt-pairs.md",
    "Use `docs/10-method/refresh-scope-axis-remediation-collateral-witnesses-local-workload-replacement-drain-backed-restoration-and-fenced-substrate-restoration.md` when the live question is whether repaired or rebalanced decoupling came back through a local workload replacement, a broader drain-backed move, or fenced-substrate recovery.\n",
    pp_doc_add,
)

resolved_oq_block = """- `OQ-0155` — what remediation-capacity-source witness distinguishes restoration that reuses free capacity from restoration that succeeds only by preempting unrelated lower-priority work?
  - Why it matters: if DelayBasin cannot separate free-capacity recovery from preemption-backed recovery, later sessions may narrate low-collateral self-healing from restoration that only works by displacing unrelated work.
  - Current posture: resolved by `RS-0162` via `docs/10-method/refresh-scope-axis-remediation-capacity-source-witnesses-free-capacity-restoration-preemption-backed-restoration-and-mixed-restoration.md`; reopen only if the compact refresh-scope-axis-remediation-capacity-source witness proves insufficient and stronger displacement-debt governance is honestly required

- `OQ-0156` — what remediation-displacement-aftercare witness distinguishes restoration that only suspends or requeues displaced lower-priority work from restoration that cancels or abandons it?
  - Why it matters: if DelayBasin cannot separate resumable displacement from outright sacrifice, later sessions may narrate bounded priority borrowing from repairs that permanently discard unrelated work.
  - Current posture: unresolved"""
replace_regex(
    "docs/20-constitution/open-question-registry.md",
    r"- `OQ-0155` — .*?Current posture: unresolved(?:\n- `OQ-0155` — .*?Current posture: unresolved)?",
    resolved_oq_block,
)

trajectory_pattern = r"111\. Determine what remediation-capacity-source witness distinguishes restoration that reuses free capacity from restoration that succeeds only by preempting unrelated lower-priority work\..*?Current posture: unresolved"
trajectory_repl = """111. Determine what remediation-capacity-source witness distinguishes restoration that reuses free capacity from restoration that succeeds only by preempting unrelated lower-priority work.

A fresh extension is that once restoration collateral is explicit, DelayBasin may next need to say whether the recovered placement used spare capacity already available or only returned by evicting or suspending unrelated lower-priority work. Otherwise even a local-looking replacement may silently inherit the authority of low-collateral repair when it actually depends on a priority or preemption bill paid elsewhere.
- `OQ-0155` — what remediation-capacity-source witness distinguishes restoration that reuses free capacity from restoration that succeeds only by preempting unrelated lower-priority work?
  - Why it matters: if DelayBasin cannot separate free-capacity recovery from preemption-backed recovery, later sessions may narrate low-collateral self-healing from restoration that only works by displacing unrelated work.
  - Current posture: resolved by `RS-0162` via `docs/10-method/refresh-scope-axis-remediation-capacity-source-witnesses-free-capacity-restoration-preemption-backed-restoration-and-mixed-restoration.md`; reopen only if the compact refresh-scope-axis-remediation-capacity-source witness proves insufficient and stronger displacement-debt governance is honestly required

112. Determine what remediation-displacement-aftercare witness distinguishes restoration that temporarily suspends or requeues displaced work from restoration that cancels or abandons it.

A fresh extension is that once capacity source is explicit, DelayBasin may next need to say what happens to the work that paid the preemption bill. Otherwise displacement-backed repair may silently inherit the authority of reversible priority borrowing even when it permanently cancels or abandons unrelated work.
- `OQ-0156` — what remediation-displacement-aftercare witness distinguishes restoration that only suspends or requeues displaced lower-priority work from restoration that cancels or abandons it?
  - Why it matters: if DelayBasin cannot separate resumable displacement from outright sacrifice, later sessions may narrate bounded priority borrowing from repairs that permanently discard unrelated work.
  - Current posture: unresolved"""
replace_regex("docs/00-meta/trajectory-map.md", trajectory_pattern, trajectory_repl)

qws_add = """

## QWS-0238 — Some continuations may eventually need a displacement debt / priority tariff / resumability escrow rather than only a compact refresh-scope-axis-remediation-capacity-source witness

### Claim
Some later continuations may need stronger public machinery for who paid, how much was paid, and what restitution is owed when repaired decoupling only comes back by displacing lower-priority work. One compact free-vs-preempt witness may eventually stop being enough.

### What follows if true
- DelayBasin may eventually need an explicit way to distinguish cheap slack reuse, reversible suspension or requeue, and permanent sacrifice of displaced work rather than leaving those costs in surrounding prose.
- The archive might need a bounded displacement-debt or resumability ledger if later revisions repeatedly need to compare priority-backed recovery costs across several branches.

### What would count against it
- Several later revisions keep fitting cleanly inside one compact refresh-scope-axis-remediation-capacity-source witness without repeated confusion about who paid the capacity bill.
- The archive almost never needs public reasoning about what happened to displaced work after a preemption-backed repair.

### Why it stays quarantined
The current evidence justifies one bounded witness for free-capacity restoration vs preemption-backed restoration. It does not yet justify a standing priority tariff board, debt ledger, or resumability escrow layer.
"""
qws_anchor = "## QWS-0237 — Some continuations may eventually need a remediation collateral tariff / disruption-budget escrow / blast-radius ledger rather than only a compact refresh-scope-axis-remediation-collateral witness"
ensure_contains("docs/90-quarantine/wild-speculations-2026-03-08.md", qws_anchor, qws_add)

# packet contract common
checker_spec = '''
"refresh_scope_axis_remediation_capacity_source_witness_contract": refresh_scope_axis_branch_spec(
    doc_path="docs/10-method/refresh-scope-axis-remediation-capacity-source-witnesses-free-capacity-restoration-preemption-backed-restoration-and-mixed-restoration.md",
    title="Refresh-scope-axis-remediation-capacity-source witnesses, free-capacity restoration, preemption-backed restoration, and mixed restoration",
    oq_id="OQ-0155",
    external_pressure_heading="## External pressure from Kubernetes scheduling fallback and non-preempting Pods, Kueue cohort borrowing and preemption, Slurm backfill and preemption, and RayJob priority scheduling with Kueue",
    comparison_heading="## Free capacity restoration vs preemption-backed restoration vs mixed refresh scope axis remediation capacity source",
    runbook_ref="refresh-scope-axis-remediation-capacity-source-witnesses-free-capacity-restoration-preemption-backed-restoration-and-mixed-restoration.md",
    prompt_id="PP-0113",
    prompt_needles=["Use `docs/10-method/refresh-scope-axis-remediation-capacity-source-witnesses-free-capacity-restoration-preemption-backed-restoration-and-mixed-restoration.md`", "free-capacity-restoration, preemption-backed-restoration, or mixed-refresh-scope-axis-remediation-capacity-source"],
    claim_id="CL-0153",
    resolution_id="RS-0162",
    trajectory_oq_id="OQ-0156",
    qws_id="QWS-0238",
    qws_label="displacement debt / priority tariff / resumability escrow",
    changelog_needles=["refresh-scope-axis-remediation-capacity-source-witnesses-free-capacity-restoration-preemption-backed-restoration-and-mixed-restoration.md", "check_refresh_scope_axis_remediation_capacity_source_witness_contract.py"],
    family="refresh_scope_axis_remediation_capacity_source_state",
    allowed=["free-capacity-restoration", "preemption-backed-restoration", "mixed-refresh-scope-axis-remediation-capacity-source"],
    excluded=["priority-means-preempted", "borrowed-quota-is-free-enough", "preemption-is-just-capacity", "capacity-ish"],
),
'''
ensure_contains(
    "tools/packet_contract_common.py",
    '"refresh_scope_axis_remediation_collateral_witness_contract": refresh_scope_axis_branch_spec(\n',
    checker_spec,
)

# ledgers
assumption_item = {
    "id": AS,
    "title": "one compact refresh-scope-axis-remediation-capacity-source witness is enough for now",
    "state": "active",
    "scope": "continuity passes whose current widened public claim depends not only on whether corroborating axes are genuinely independent, materially backed, decoupled, hard-enforced, durable, explicitly restored, and honest about collateral width, but on whether restored placement reused already-available capacity or required displacement of unrelated lower-priority work",
    "invalidation_triggers": [
        "repeated later revisions need standing governance over displacement debt, priority tariffs, resumability escrow, or capacity exchange rates",
        "later revisions repeatedly need to distinguish borrowed unused quota from plain free slack as a separate governed class",
        "one compact free-vs-preempt witness stops keeping repaired placement truth honest"
    ],
    "assumption_state": "active",
    "repair": "ordinary-continuation",
    "origin_revision": REV,
    "revision": REV,
    "assumption": "One compact refresh-scope-axis-remediation-capacity-source witness is enough for now.",
    "supporting_surfaces": [
        NEW_DOC,
        "docs/20-constitution/open-question-registry.md",
        "docs/00-meta/trajectory-map.md",
        "docs/90-quarantine/wild-speculations-2026-03-08.md#QWS-0238"
    ],
    "discharge": "retire-or-promote-if-refresh-scope-axis-remediation-capacity-source-overflows",
    "witness_surface": f"ASSUMPTION-LEDGER.json#{AS}",
    "assumption_surface": f"ASSUMPTION-LEDGER.json#{AS}",
    "assumption_statement": "A single compact witness is enough to keep free-capacity restoration distinct from preemption-backed restoration for now, without a standing displacement-debt or priority-tariff board.",
    "action_lane": "keep-compact",
    "gate_class": "concrete-evidence",
}
append_item("ASSUMPTION-LEDGER.json", assumption_item)

ob_item = {
    "id": OB,
    "title": "when repaired decoupling keeps needing free-vs-preempt separation, DelayBasin should preserve one compact refresh-scope-axis-remediation-capacity-source witness rather than a displacement debt ledger",
    "state": "open",
    "witness_surface": f"OBLIGATION-LEDGER.json#{OB}",
    "target_surfaces": [NEW_DOC, "docs/90-quarantine/wild-speculations-2026-03-08.md#QWS-0238"],
    "missing_support": "need repeated evidence that one compact free-vs-preempt witness no longer keeps repaired placement truth honest",
    "current_support": [NEW_DOC, f"APPLICABILITY-LEDGER.json#{AP}", f"FOREIGN-PRESSURE-LEDGER.json#{FP}"],
    "discharge_path": "either show later that one compact refresh-scope-axis-remediation-capacity-source witness keeps sufficing or promote stronger displacement-debt governance explicitly",
    "obligation_state": "open",
    "repair": "ordinary-continuation",
    "origin_revision": REV,
    "discharge": "reopen-only-if-refresh-scope-axis-remediation-capacity-source-overflows",
    "revision": REV,
    "owner_surface": NEW_DOC,
    "action_lane": "keep-compact",
    "gate_class": "overflow",
}
append_item("OBLIGATION-LEDGER.json", ob_item)

app_item = {
    "id": AP,
    "title": "the refresh-scope-axis-remediation-capacity-source witness stays smaller than a displacement debt ledger",
    "state": "gated",
    "question": "when should DelayBasin treat repaired decoupling with one compact remediation-capacity-source witness instead of promoting broader priority pricing or displacement accounting?",
    "applies_when": [
        "a revision already has a row whose current claim depends on corroborating axes that are already judged genuinely independent, materially backed, decoupled under perturbation, hard-enforced, durable, explicitly restored, and honest about collateral width",
        "later passes still need to distinguish free-capacity-restoration, preemption-backed-restoration, or mixed-refresh-scope-axis-remediation-capacity-source posture",
        "one compact successor surface plus the existing admitted refresh-scope-axis-remediation-collateral and related scheduler surfaces still keeps remediation capacity source honest without standing debt or tariff machinery",
    ],
    "does_not_apply_when": [
        "the archive honestly requires standing governance over displacement debt, priority pricing, capacity exchange rates, or resumability escrow",
        "the questioned surface is not really about whether restored placement reused free capacity or displaced unrelated lower-priority work",
    ],
    "budget": "one compact refresh-scope-axis-remediation-capacity-source witness plus one resolution of OQ-0155; no displacement debt ledger",
    "negative_transfer_budget": "do not treat any repaired or rebalanced return as if it automatically carried the cheap authority of free-capacity recovery",
    "origin_revision": REV,
    "discharge": "reopen-only-if-refresh-scope-axis-remediation-capacity-source-overflows",
    "action_lane": "keep-compact",
    "gate_class": "concrete-evidence",
    "witness_surface": f"APPLICABILITY-LEDGER.json#{AP}",
    "applicability_state": "gated",
    "repair": "ordinary-continuation",
    "matched_budget": "one compact witness foregrounding free-capacity vs preemption-backed restoration without widening into displacement accounting",
    "revision": REV,
    "target_objective": "keep remediation capacity source honest without inflating a general priority-pricing layer",
    "carry_object": "refresh-scope-axis-remediation-capacity-source witness",
    "open_question": NEXT_OQ,
    "applicability_conditions": [
        "a revision already has a row whose current claim depends on corroborating axes that are already judged genuinely independent, materially backed, decoupled under perturbation, hard-enforced, durable, explicitly restored, and honest about collateral width",
        "later passes still need to distinguish free-capacity-restoration, preemption-backed-restoration, or mixed-refresh-scope-axis-remediation-capacity-source posture",
        "one compact successor surface plus the existing admitted refresh-scope-axis-remediation-collateral and related scheduler surfaces still keeps remediation capacity source honest without standing debt or tariff machinery",
    ],
    "baselines": [
        "prior refresh-scope-axis-remediation-collateral witness already names how wide the restoration was",
        "current question is only who paid the capacity bill for that restoration",
    ],
    "non_fit_slice": "questions about standing displacement pricing, capacity exchange rates, or resumability governance do not fit this compact witness",
}
append_item("APPLICABILITY-LEDGER.json", app_item)

fp_item = {
    "id": FP,
    "title": "scheduler and queueing docs support one compact refresh-scope-axis-remediation-capacity-source witness rather than a displacement debt ledger",
    "state": "imported",
    "source_packets": [
        {"datacube": "KubernetesSchedulingFallback-2026", "surfaces": ["REF-0986", "REF-0987"], "pressure": "Kubernetes separates waiting for free resources from preemption fallback, which pressures DelayBasin to keep free-capacity recovery distinct from displacement-backed recovery."},
        {"datacube": "KueueBorrowingAndPreemption-2026", "surfaces": ["REF-0988", "REF-0989"], "pressure": "Kueue exposes both unused quota borrowing and explicit workload preemption, which pressures DelayBasin not to flatten slack borrowing and eviction-backed admission into one capacity story."},
        {"datacube": "SlurmCapacitySource-2026", "surfaces": ["REF-0990", "REF-0991"], "pressure": "Slurm distinguishes spare-hole backfill from explicit preemption by cancel, suspend, or requeue, which pressures DelayBasin to keep free-capacity reuse distinct from displacement-backed recovery."},
        {"datacube": "RayGpuPriorityPreemption-2026", "surfaces": ["REF-0992"], "pressure": "RayJob priority scheduling with Kueue makes GPU recovery by preempting lower-priority work concrete enough that GPUstorming should keep it separate from simple slack reuse."},
    ],
    "reviewed_pattern": "free capacity restoration vs preemption-backed restoration across already remediated decoupled corroboration",
    "import_decision": "support a compact refresh-scope-axis-remediation-capacity-source witness and resolve OQ-0155",
    "adopted_take": "DelayBasin should add one compact witness that says whether restored decoupling came back through free capacity, preemption-backed restoration, or an honest mix",
    "supporting_only_take": "the current evidence cleanly supports a bounded refresh-scope-axis-remediation-capacity-source witness without promoting broader displacement-debt governance",
    "deferred_or_rejected_take": ["displacement debt ledger", "priority tariff", "resumability escrow"],
    "local_gap": "the archive still lacked one compact successor surface for whether repaired decoupling reused already-available capacity or only returned by displacing unrelated lower-priority work",
    "anchor_surfaces": [
        "docs/10-method/refresh-scope-axis-remediation-collateral-witnesses-local-workload-replacement-drain-backed-restoration-and-fenced-substrate-restoration.md",
        "docs/20-constitution/open-question-registry.md",
        "docs/00-meta/trajectory-map.md",
        "docs/90-quarantine/wild-speculations-2026-03-08.md#QWS-0238",
    ],
    "open_question": NEXT_OQ,
    "repair": "ordinary-continuation",
    "origin_revision": REV,
    "action_lane": "keep-compact",
    "gate_class": "concrete-evidence",
    "discharge": "reopen-only-if-refresh-scope-axis-remediation-capacity-source-overflows",
    "revision": REV,
    "witness_surface": f"FOREIGN-PRESSURE-LEDGER.json#{FP}",
    "bounded_take": "Keep the archive compact by extracting one refresh-scope-axis-remediation-capacity-source witness over the existing refresh-scope-axis-remediation-collateral and related admitted surfaces; do not promote a displacement debt ledger, priority tariff, or resumability escrow.",
    "explicit_non_take": ["no displacement debt ledger", "no priority tariff", "no resumability escrow"],
    "assimilation_state": "imported",
    "foreign_pressure_state": "imported",
    "open_transfer_question": "what remediation-displacement-aftercare witness distinguishes resumable displacement from cancellation or abandonment after preemption-backed restoration?",
    "missing_support": "the current corpus does not yet justify a standing displacement-pricing or restitution economy across refresh-scope-axis branches",
}
append_item("FOREIGN-PRESSURE-LEDGER.json", fp_item)

tl_item = {
    "id": TL,
    "title": "refresh-scope-axis-remediation-capacity-source evidence supports resolving OQ-0155 with one compact free-vs-preempt card rather than a displacement debt ledger",
    "state": "supporting-only",
    "reviewed_pattern": "free capacity restoration vs preemption-backed restoration across already remediated decoupled corroboration",
    "import_decision": "support a compact refresh-scope-axis-remediation-capacity-source witness and resolve OQ-0155",
    "adopted_take": "DelayBasin should add one compact witness that says whether restored decoupling came back through free capacity, preemption-backed restoration, or an honest mix",
    "supporting_only_take": "the current evidence cleanly supports a bounded refresh-scope-axis-remediation-capacity-source witness without promoting broader displacement-debt governance",
    "deferred_or_rejected_take": ["displacement debt ledger", "priority tariff", "resumability escrow"],
    "local_gap": "the archive still lacked one compact successor surface for whether repaired decoupling reused already-available capacity or only returned by displacing unrelated lower-priority work",
    "anchor_surfaces": [
        "docs/10-method/refresh-scope-axis-remediation-collateral-witnesses-local-workload-replacement-drain-backed-restoration-and-fenced-substrate-restoration.md",
        "docs/20-constitution/open-question-registry.md",
        "docs/00-meta/trajectory-map.md",
        "docs/90-quarantine/wild-speculations-2026-03-08.md#QWS-0238",
    ],
    "open_question": NEXT_OQ,
    "repair": "ordinary-continuation",
    "origin_revision": REV,
    "action_lane": "keep-compact",
    "gate_class": "concrete-evidence",
    "discharge": "reopen-only-if-refresh-scope-axis-remediation-capacity-source-overflows",
    "revision": REV,
    "witness_surface": f"DATACUBE-TRANSFER-LEDGER.json#{TL}",
    "transfer_state": "supporting-only",
    "bounded_take": "Keep the archive compact by extracting one refresh-scope-axis-remediation-capacity-source witness over the existing refresh-scope-axis-remediation-collateral and related admitted surfaces; do not promote a displacement debt ledger, priority tariff, or resumability escrow.",
    "explicit_non_take": ["no displacement debt ledger", "no priority tariff", "no resumability escrow"],
    "open_transfer_question": "whether later passes should add a separate remediation-displacement-aftercare witness once capacity source is explicit",
    "missing_support": "a later public check on whether one compact refresh-scope-axis-remediation-capacity-source witness keeps sufficing",
    "current_support": [f"APPLICABILITY-LEDGER.json#{AP}", f"FOREIGN-PRESSURE-LEDGER.json#{FP}", f"DATACUBE-TRANSFER-LEDGER.json#{TL}"],
    "discharge_path": "either show later that one compact refresh-scope-axis-remediation-capacity-source witness keeps sufficing or promote broader displacement governance explicitly",
    "reviewed_datacubes": [
        {"datacube": "KubernetesSchedulingFallback-2026", "surfaces": ["REF-0986"], "pattern": "preemption appears as postFilter fallback after no feasible nodes", "pressure": "free-capacity fits should stay distinct from fallback displacement"},
        {"datacube": "KubernetesNonPreemptingPods-2026", "surfaces": ["REF-0987"], "pattern": "non-preempting pods wait until resources are free", "pressure": "waiting for slack should stay distinct from evicting lower-priority work"},
        {"datacube": "KueueBorrowingQuota-2026", "surfaces": ["REF-0988"], "pattern": "cohorts can borrow unused quota without defaulting to eviction", "pressure": "borrowed slack can remain inside free-capacity restoration rather than being flattened into preemption"},
        {"datacube": "KueuePreemption-2026", "surfaces": ["REF-0989"], "pattern": "admitted workloads are evicted to accommodate another workload", "pressure": "preemption-backed restoration should stay explicit"},
        {"datacube": "SlurmBackfillAndPreemption-2026", "surfaces": ["REF-0990", "REF-0991"], "pattern": "backfill uses holes while preemption cancels, suspends, or requeues lower-priority jobs", "pressure": "capacity source should stay explicit in cluster scheduling narratives"},
        {"datacube": "RayGpuPriorityPreemption-2026", "surfaces": ["REF-0992"], "pattern": "higher-priority RayJob preempts lower-priority RayJob under Kueue", "pressure": "GPU recovery should not inherit free-slack authority when it is queue-backed displacement"},
    ],
}
append_item("DATACUBE-TRANSFER-LEDGER.json", tl_item)

res_item = {
    "id": RS,
    "title": "resolve OQ-0155 with one compact refresh-scope-axis-remediation-capacity-source witness rather than a displacement debt ledger",
    "state": "resolved",
    "closure_state": "resolved",
    "closure_reason": f"{REV} extracted one compact refresh-scope-axis-remediation-capacity-source witness, kept the admitted refresh-scope-axis-remediation-collateral and related analog surfaces narrow, and kept stronger displacement-debt stories quarantined.",
    "discharge": "reopen-only-if-refresh-scope-axis-remediation-capacity-source-overflows",
    "gate_class": "concrete-evidence",
    "origin_revision": REV,
    "prior_state": "open gap: DelayBasin already had refresh-scope-axis-remediation-collateral truth but still lacked one compact successor surface for whether repaired decoupling reused already-available capacity or only returned by displacing unrelated lower-priority work.",
    "question": "whether one compact refresh-scope-axis-remediation-capacity-source witness over the existing refresh-scope-axis-remediation-collateral and related admitted surfaces is enough for honest free-vs-preempt restoration comparison",
    "reopen_trigger": "refresh-scope-axis-remediation-capacity-source pressure overflows one compact successor surface",
    "reopen_triggers": [
        "later revisions need standing governance over displacement debt, priority pricing, capacity exchange rates, or broader restitution policy that one compact refresh-scope-axis-remediation-capacity-source witness cannot honestly absorb"
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
    "title": "revisit whether refresh-scope-axis-remediation-capacity-source pressure stayed bounded after rev0260",
    "state": "cooling",
    "candidate_surface": "docs/90-quarantine/wild-speculations-2026-03-08.md#QWS-0238",
    "cooldown_window": "keep the stronger displacement debt, priority tariff, or resumability escrow story cooled until at least one later revision shows that one compact refresh-scope-axis-remediation-capacity-source witness is no longer enough.",
    "adjudication_family": "refresh scope axis remediation capacity source / displacement bill / priority pressure",
    "supersession_link": f"OBLIGATION-LEDGER.json#{OB}",
    "origin_revision": REV,
    "discharge": "keep-cooling-unless-refresh-scope-axis-remediation-capacity-source-overflows",
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
    "title": "the refresh-scope-axis-remediation-capacity-source import should count as one compact free-vs-preempt repair, not as permission to narrate a displacement debt court",
    "state": "sealed",
    "witness_surface": f"FIREBREAK-LEDGER.json#{FB}",
    "judged_property": f"the {REV} decision that DelayBasin should extract one compact refresh-scope-axis-remediation-capacity-source witness over the existing refresh-scope-axis-remediation-collateral and related admitted surfaces and `{FAMILY}` family while the broader displacement debt / priority tariff / resumability escrow story remains quarantined",
    "public_extract": "Keep one compact free-vs-preempt restoration card; do not infer a displacement debt board.",
    "withheld_trace_surface": "private working notes / search trace",
    "allowed_role": "brief public reasoning summary only",
    "exposure_rule": "do not expose raw private chain-of-thought or unpublished scratch reasoning; expose only the compact cited rationale and named successor surfaces",
    "trace_state": "sealed",
    "repair": "ordinary-continuation",
    "origin_revision": REV,
    "action_lane": "keep-compact",
    "gate_class": "negative-transfer",
    "firebreak_surface": f"FIREBREAK-LEDGER.json#{FB}",
    "discharge": "retain-unless-a-later-revision-openly-promotes-displacement-governance",
    "revision": REV,
    "blocked_object": "displacement debt ledger / priority tariff / resumability escrow",
}
append_item("FIREBREAK-LEDGER.json", fb_item)

ft_item = {
    "id": FT,
    "title": "keep checking whether refresh-scope-axis-remediation-capacity-source pressure still fits inside one compact successor surface",
    "state": "queued",
    "blocked_object": QWS_LABEL,
    "local_surface": f"docs/90-quarantine/wild-speculations-2026-03-08.md#{QWS}",
    "followthrough_state": "queued",
    "boundary": "do not promote bounded refresh-scope-axis-remediation-capacity-source clarification into a general displacement-debt machine",
    "next_proof_surface": NEW_DOC,
    "receiving_surface": f"FOLLOWTHROUGH-QUEUE.json#{FT}",
    "repair": "ordinary-continuation",
    "origin_revision": REV,
    "discharge": "revisit-on-next-real-refresh-scope-axis-remediation-capacity-source-overflow",
    "action_lane": "keep-compact",
    "gate_class": "overflow",
    "blocked_output": QWS_LABEL,
    "owner_surface": f"OBLIGATION-LEDGER.json#{OB}",
    "revision": REV,
    "missing_support": "a later public check on whether one compact refresh-scope-axis-remediation-capacity-source witness keeps overflowing the bounded rule and honestly warrants richer displacement governance",
    "candidate_surface": f"docs/90-quarantine/wild-speculations-2026-03-08.md#{QWS}",
    "blocked_by": "need repeated evidence that free-vs-preempt capacity-source truth overflows one compact witness",
}
append_item("FOLLOWTHROUGH-QUEUE.json", ft_item)

# witness vocabulary
wv = load_json("WITNESS-VOCABULARY.json")
if FAMILY not in wv["families"]:
    after = list(wv["families"].items())
    new_cf = {}
    inserted = False
    for k, v in after:
        new_cf[k] = v
        if k == "refresh_scope_axis_remediation_collateral_state":
            new_cf[FAMILY] = {
                "allowed": ALLOWED,
                "surfaces": ["WITNESS-VOCABULARY.json", "REVISION-RECEIPT.json", NEW_DOC],
                "excluded_synonyms": EXCLUDED,
                "comparability_budget": "refresh-scope-axis-remediation-capacity-source truth is compared by token; the compact witness says whether restored decoupling came back through free capacity, preemption-backed restoration, or an honest mix, while raw queue traces, quota ledgers, eviction events, and scheduler logs stay in surrounding prose",
            }
            inserted = True
    if not inserted:
        new_cf[FAMILY] = {
            "allowed": ALLOWED,
            "surfaces": ["WITNESS-VOCABULARY.json", "REVISION-RECEIPT.json", NEW_DOC],
            "excluded_synonyms": EXCLUDED,
            "comparability_budget": "refresh-scope-axis-remediation-capacity-source truth is compared by token; the compact witness says whether restored decoupling came back through free capacity, preemption-backed restoration, or an honest mix, while raw queue traces, quota ledgers, eviction events, and scheduler logs stay in surrounding prose",
        }
    wv["families"] = new_cf
    dump_json("WITNESS-VOCABULARY.json", wv)

# receipt
receipt = load_json("REVISION-RECEIPT.json")
receipt["revision"] = REV
receipt["previous_revision"] = PREV
receipt["summary"] = "Resolved refresh-scope-axis-remediation capacity source with a compact free-vs-preempt witness, honestly quarantined stronger displacement-debt governance, and tightened the archive index/open-question surfaces so the archive stays small and cumulative."
receipt["canon_additions"] = [NEW_DOC, f"{RS} resolved {OQ} with one compact refresh-scope-axis-remediation-capacity-source witness"]
receipt["quarantine_additions"] = [f"docs/90-quarantine/wild-speculations-2026-03-08.md#{QWS}"]
receipt["refs_used"] = [
    "docs/00-meta/bibliography.md#ref-0986",
    "docs/00-meta/bibliography.md#ref-0987",
    "docs/00-meta/bibliography.md#ref-0988",
    "docs/00-meta/bibliography.md#ref-0989",
    "docs/00-meta/bibliography.md#ref-0990",
    "docs/00-meta/bibliography.md#ref-0991",
    "docs/00-meta/bibliography.md#ref-0992",
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
    "apply_rev0260.py",
]
receipt["packaged_release"] = True
receipt["packaged_bundle_filename"] = BUNDLE
receipt["basis_witness"].update({
    "expected_head": PREV,
    "observed_head": PREV,
    "basis_surfaces": [
        "docs/10-method/refresh-scope-axis-remediation-collateral-witnesses-local-workload-replacement-drain-backed-restoration-and-fenced-substrate-restoration.md",
        "docs/00-meta/trajectory-map.md",
        "docs/20-constitution/open-question-registry.md",
    ],
    "session_provenance": f"DelayBasin-{PREV}-2026.03.28.06.47-remediationcollateral-tariffq-draincarry-braidglass.zip",
    "basis_omission_basis": "broader displacement pricing was intentionally omitted from canon because the evidence only justified one bounded refresh-scope-axis-remediation-capacity-source witness",
    "origin_revision": REV,
    "revision_span": f"{PREV} -> {REV}",
})
receipt["scope_witness"].update({
    "exact_target": "one compact refresh-scope-axis-remediation-capacity-source witness plus one quarantined displacement-debt move and one small archive-surface hygiene cleanup",
    "scope_surfaces": [
        "docs/20-constitution/open-question-registry.md",
        "docs/00-meta/trajectory-map.md",
        NEW_DOC,
        f"docs/90-quarantine/wild-speculations-2026-03-08.md#{QWS}",
        "ARCHIVE_INDEX.md",
    ],
    "scope_of_change": "refresh-scope-axis-remediation-capacity-source",
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
    "comparability_budget": "refresh-scope-axis-remediation-capacity-source truth is compared by token; the compact witness says whether restored decoupling came back through free capacity, preemption-backed restoration, or an honest mix while raw queue traces, quota ledgers, eviction events, and scheduler logs stay outside the token",
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
    "rejection_reason": "the current evidence supports one compact free-vs-preempt witness but not a standing displacement-debt economy",
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
    "basis_surface": "docs/10-method/refresh-scope-axis-remediation-collateral-witnesses-local-workload-replacement-drain-backed-restoration-and-fenced-substrate-restoration.md",
    "delta_surface": NEW_DOC,
    "comparison_summary": "rev0260 adds one compact refresh-scope-axis-remediation-capacity-source witness so repaired decoupling no longer all reads as if spare slack and displacement-backed recovery were the same class of restoration.",
}
receipt["changes"] = [
    {"kind": "canon", "surface": NEW_DOC, "summary": "added one compact refresh-scope-axis-remediation-capacity-source witness with free-capacity-restoration, preemption-backed-restoration, and mixed states"},
    {"kind": "quarantine", "surface": f"docs/90-quarantine/wild-speculations-2026-03-08.md#{QWS}", "summary": "kept stronger displacement-debt or priority-tariff governance quarantined rather than promoting it into canon"},
    {"kind": "hygiene", "surface": "ARCHIVE_INDEX.md", "summary": "normalized the release index back into one proper top-header table and removed the duplicated OQ-0155 registry block so reentry surfaces stay small and cumulative"},
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
receipt["quarantined_non_take"] = ["displacement debt ledger", "priority tariff", "resumability escrow"]
receipt["artifacts_touched"] = list(receipt["touched_surfaces"])
receipt["bundle"] = BUNDLE
receipt["slug"] = SLUG
receipt["resolved_question"] = OQ
receipt["next_open_question"] = NEXT_OQ
receipt["canonical_additions"] = [NEW_DOC]
receipt["checker_additions"] = [NEW_CHECKER]
receipt["change_summary"] = [
    {"kind": "canon", "surface": NEW_DOC, "summary": "added one compact refresh-scope-axis-remediation-capacity-source witness for free-capacity vs preemption-backed restoration"},
    {"kind": "quarantine", "surface": f"docs/90-quarantine/wild-speculations-2026-03-08.md#{QWS}", "summary": "kept the stronger displacement debt / priority tariff / resumability escrow move explicitly quarantined"},
    {"kind": "hygiene", "surface": "ARCHIVE_INDEX.md", "summary": "repaired the archive index table shape and removed the duplicated OQ-0155 registry block so reentry stays cleaner"},
]
receipt["refresh_scope_axis_remediation_capacity_source_witness"] = {
    "witness_surface": NEW_DOC,
    "family": FAMILY,
    "allowed_tokens": ALLOWED,
    "overflow_rule": "reopen-only-if-refresh-scope-axis-remediation-capacity-source-overflows",
}
receipt["refresh_scope_axis_remediation_capacity_source_witness_contract"] = {
    "family": FAMILY,
    "allowed_tokens": ALLOWED,
}
receipt["refresh_scope_axis_remediation_capacity_source_witness_meta"] = {"checker": NEW_CHECKER}
# keep legacy helper sections current
receipt["refresh_scope_axis_remediation_collateral_witness_meta"] = receipt.get("refresh_scope_axis_remediation_collateral_witness_meta", {"checker": "tools/check_refresh_scope_axis_remediation_collateral_witness_contract.py"})
dump_json("REVISION-RECEIPT.json", receipt)

# status + manifest placeholders
status = load_json("SURFACE-STATUS.json")
status["operational_head"]["revision"] = REV
status["status_lanes"]["frozen_public_surface"] = BUNDLE
status["status_lanes"]["current_release_surface"] = BUNDLE
status["citation_head"]["revision"] = REV
status["citation_head"]["surface"] = BUNDLE
status["previous_citation_head"]["revision"] = PREV
status["previous_citation_head"]["surface"] = f"DelayBasin-{PREV}-2026.03.28.06.47-remediationcollateral-tariffq-draincarry-braidglass.zip"
status["revision"] = REV
status["stamp"] = STAMP
status["slug"] = SLUG
dump_json("SURFACE-STATUS.json", status)

dump_json("RELEASE-MANIFEST.json", {"project": "DelayBasin", "revision": REV, "timestamp": STAMP, "slug": SLUG, "bundle": BUNDLE})

# changelog
new_changelog = f"## {REV} - {STAMP} - capacitysource / debtq / {SUMMARY_HIGHLIGHT} / {CODENAME}\n\n- Added `{NEW_DOC}` to resolve `{OQ}` with a compact free-vs-preempt remediation-capacity-source witness.\n- Kept the stronger displacement debt / priority tariff / resumability escrow move explicitly quarantined as `{QWS}` instead of laundering it into canon.\n- Hygiene/meta-engineering improvement: normalized `ARCHIVE_INDEX.md` back into one proper table and removed the duplicated `OQ-0155` block in `docs/20-constitution/open-question-registry.md`, while adding `{NEW_CHECKER}` through the shared refresh-scope-axis branch scaffold.\n\n"
write_text("CHANGELOG.md", new_changelog + read_text("CHANGELOG.md"))

# archive index repair
archive_text = read_text("ARCHIVE_INDEX.md")
legacy_idx = archive_text.find("\nLegacy continuity markers")
if legacy_idx == -1:
    raise RuntimeError("ARCHIVE_INDEX.md missing legacy marker")
body = archive_text[:legacy_idx].strip().splitlines()
rows = []
for line in body:
    if line.startswith("| DelayBasin-"):
        rows.append(line)
new_row = f"| {BUNDLE} | 2026-03-28 | Refresh-scope-axis-remediation-capacity-source revision: resolved {OQ} with a compact free-vs-preempt witness, honestly quarantined stronger displacement-debt governance, and cleaned the archive index/open-question surfaces so the archive stays wired and cumulative. |"
if new_row not in rows:
    rows.insert(0, new_row)
rest = archive_text[legacy_idx:].lstrip("\n")
archive_new = "# Archive index\n\n| Bundle | Date | Notes |\n| --- | --- | --- |\n" + "\n".join(rows) + "\n\n" + rest
write_text("ARCHIVE_INDEX.md", archive_new)

print(f"Applied {REV}")
