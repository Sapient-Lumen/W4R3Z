from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent

REV = "rev0259"
PREV = "rev0258"
STAMP = "2026.03.28.06.47"
CREATED_AT = "2026-03-28T06:47:00-04:00"
SLUG = "remediationcollateral-tariffq-draincarry-braidglass"
BUNDLE = f"DelayBasin-{REV}-{STAMP}-{SLUG}.zip"
SUMMARY_HIGHLIGHT = "draincarry"
CODENAME = "braidglass"
NEW_DOC = "docs/10-method/refresh-scope-axis-remediation-collateral-witnesses-local-workload-replacement-drain-backed-restoration-and-fenced-substrate-restoration.md"
NEW_DOC_NAME = NEW_DOC.split('/')[-1]
NEW_CHECKER = "tools/check_refresh_scope_axis_remediation_collateral_witness_contract.py"
QWS = "QWS-0237"
QWS_LABEL = "remediation collateral tariff / disruption-budget escrow / blast-radius ledger"
CL = "CL-0152"
RS = "RS-0161"
OQ = "OQ-0154"
NEXT_OQ = "OQ-0155"
PP = "PP-0112"
AP = "AP-0153"
OB = "OB-0154"
AS = "AS-0158"
FP = "FP-0158"
TL = "TL-0164"
FT = "FT-0161"
RT = "RT-0148"
FB = "FB-0155"


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
    text = text.replace(needle, needle + addition)
    write_text(rel, text)


def replace_once(rel: str, old: str, new: str) -> None:
    text = read_text(rel)
    if new in text:
        return
    if old not in text:
        raise RuntimeError(f"old block not found in {rel}")
    write_text(rel, text.replace(old, new, 1))


def append_item(rel: str, item: dict) -> None:
    obj = load_json(rel)
    items = obj["items"]
    if any(existing["id"] == item["id"] for existing in items):
        return
    items.append(item)
    dump_json(rel, obj)


def replace_open_question_block(rel: str, oq_id: str, new_block: str) -> None:
    text = read_text(rel)
    pattern = rf"- `{re.escape(oq_id)}` — .*?(?=\n- `OQ-|\Z)"
    if re.search(pattern, text, flags=re.S) is None:
        raise RuntimeError(f"open question block {oq_id} not found in {rel}")
    text = re.sub(pattern, new_block.strip(), text, count=1, flags=re.S)
    write_text(rel, text)


def replace_registry_block(rel: str, key: str, new_block: str) -> None:
    text = read_text(rel)
    pattern = rf'"{re.escape(key)}": .*?(?=\n"[A-Za-z0-9_]+": |\n\}})'
    if re.search(pattern, text, flags=re.S) is None:
        raise RuntimeError(f"registry block {key} not found")
    text = re.sub(pattern, new_block.rstrip(), text, count=1, flags=re.S)
    write_text(rel, text)


# --- new canonical doc ---
new_doc_text = """# Refresh-scope-axis-remediation-collateral witnesses, local workload replacement, drain-backed restoration, and fenced-substrate restoration

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
"""
write_text(NEW_DOC, new_doc_text)
write_text(NEW_CHECKER, 'from packet_contract_common import require_named_refresh_scope_axis_branch_witness_packet_and_vocabulary\n\nrequire_named_refresh_scope_axis_branch_witness_packet_and_vocabulary("refresh_scope_axis_remediation_collateral_witness_contract")\n\nprint("check_refresh_scope_axis_remediation_collateral_witness_contract: OK")\n')

# --- bibliography ---
bib_add = """

- `REF-0981` — Kubernetes Documentation, **kubectl drain** (accessed 2026-03-28)
  - URL: https://kubernetes.io/docs/reference/kubectl/generated/kubectl_drain/
  - Load-bearing use: `kubectl drain` marks a node unschedulable and evicts or deletes all Pods on that node except mirror Pods, which pressures DelayBasin to distinguish broad drain-backed restoration from merely replacing one violating workload.

- `REF-0982` — Kubernetes Documentation, **Node Shutdowns** (accessed 2026-03-28)
  - URL: https://kubernetes.io/docs/concepts/cluster-administration/node-shutdown/
  - Load-bearing use: the out-of-service taint forcefully deletes Pods lacking matching tolerations and immediately detaches volumes so recovery can occur elsewhere, which pressures DelayBasin to distinguish fenced-substrate restoration from local replacement or ordinary drain.

- `REF-0983` — Red Hat Documentation, **Remediation, fencing, and maintenance** (accessed 2026-03-28)
  - URL: https://docs.redhat.com/en/documentation/workload_availability_for_red_hat_openshift/25.4/html/remediation_fencing_and_maintenance/about-remediation-fencing-maintenance
  - Load-bearing use: Red Hat explicitly separates node maintenance cordon-and-drain flows from self-node-remediation reboot-and-delete flows and machine-deletion reprovisioning, which pressures DelayBasin to separate local replacement, drain-backed restoration, and fenced-substrate remediation.

- `REF-0984` — Slurm Workload Manager, **scontrol** (accessed 2026-03-28)
  - URL: https://slurm.schedmd.com/scontrol.html
  - Load-bearing use: `DRAIN`, `DOWN`, `RESUME`, and `requeue` distinguish node-level maintenance or shutdown from job-level replay, which pressures DelayBasin to keep workload replacement distinct from broader drain or substrate-level collateral.

- `REF-0985` — NVIDIA Documentation, **GPU Driver Upgrades — NVIDIA GPU Operator** (accessed 2026-03-28)
  - URL: https://docs.nvidia.com/datacenter/cloud-native/gpu-operator/latest/gpu-driver-upgrades.html
  - Load-bearing use: NVIDIA first attempts evicting only GPU Pods and only falls back to node drain when local eviction fails and auto-drain is enabled, which pressures DelayBasin to distinguish local repair collateral from broader maintenance drain in GPU-native upgrade paths.
"""
ensure_contains("docs/00-meta/bibliography.md", "- `REF-0980` — NVIDIA Documentation, **GPU Driver Upgrades — NVIDIA GPU Operator** (accessed 2026-03-28)\n  - URL: https://docs.nvidia.com/datacenter/cloud-native/gpu-operator/latest/gpu-driver-upgrades.html\n  - Load-bearing use: NVIDIA distinguishes the default upgrade controller from manual `OnDelete` rollout where admins delete the old driver pod to trigger replacement, which pressures DelayBasin to separate controller-native automation from operator-triggered replay in GPU maintenance flows.\n", bib_add)

# --- docs index and runbook ---
ensure_contains("docs/README.md", "- [`10-method/refresh-scope-axis-remediation-witnesses-native-controller-restoration-external-remediator-restoration-and-operator-replay-restoration.md`](10-method/refresh-scope-axis-remediation-witnesses-native-controller-restoration-external-remediator-restoration-and-operator-replay-restoration.md)\n", f"- [`10-method/{NEW_DOC_NAME}`](10-method/{NEW_DOC_NAME})\n")
ensure_contains("docs/00-meta/llm-runbook.md", "Use `docs/10-method/refresh-scope-axis-remediation-witnesses-native-controller-restoration-external-remediator-restoration-and-operator-replay-restoration.md` when the live question is who actually restores drifted decoupling after it comes back: the platform's own controller path, an auxiliary remediator, or a manual operator replay act.\n", "Use `docs/10-method/refresh-scope-axis-remediation-collateral-witnesses-local-workload-replacement-drain-backed-restoration-and-fenced-substrate-restoration.md` when the live question is how much surrounding disruption restored decoupling spent after it came back: a local workload replacement, a broader drain-backed move, or fenced-substrate recovery.\n")

# --- prompt pair registry and prompt pairs ---
pp_reg_add = """

- `PP-0112` — Name whether restored decoupling stayed local, spent a drain, or spent fenced substrate
  - Goal: keep drain-backed or fenced-substrate restoration from silently inheriting cheap local-replacement authority by requiring explicit prior remediation evidence, current corroborating axes, local-workload-replacement basis, drain-backed basis, fenced-substrate basis, `refresh_scope_axis_remediation_collateral_state`, and fail-closed repair before later passes call the restored support cheaply self-healing.
  - Canonical text: `docs/50-promptcraft/prompt-pairs.md#pp-0112--name-whether-restored-decoupling-stayed-local-spent-a-drain-or-spent-fenced-substrate`
"""
ensure_contains("docs/20-constitution/prompt-pair-registry.md", "- `PP-0111` — Name whether restored decoupling comes back through native controllers, auxiliary remediators, or operator replay\n  - Goal: keep repaired decoupling from silently inheriting native self-healing authority by requiring explicit prior durability evidence, current corroborating axes, native-controller basis, external-remediator basis, operator-replay basis, `refresh_scope_axis_remediation_state`, and fail-closed repair before later passes call the support self-restoring.\n  - Canonical text: `docs/50-promptcraft/prompt-pairs.md#pp-0111--name-whether-restored-decoupling-comes-back-through-native-controllers-auxiliary-remediators-or-operator-replay`\n", pp_reg_add)

pp_doc_add = """

## PP-0112 — Name whether restored decoupling stayed local, spent a drain, or spent fenced substrate

**Opening prompt**

```text
Read the latest DelayBasin archive and inspect whether the current revision should also materialize one compact refresh-scope-axis-remediation-collateral witness for honest local-vs-drain-vs-fence restoration comparison.

Focus only on cases where the corroborating axes already look genuinely independent, materially backed, decoupled under perturbation, hard-enforced, explicitly durable, and explicit about who restored the decoupling. The missing question is how much surrounding workload or substrate disruption the restoration spends: only a local workload replacement, a broader drain-backed move, a fenced-substrate move, or an honest mix.

If yes, preserve exactly one small witness that:
- names the governed row or surface,
- names the stake object / line of concern,
- names the prior refresh-scope-axis-remediation evidence,
- names the current corroborating axes,
- names the local-workload-replacement basis if any,
- names the drain-backed basis if any,
- names the fenced-substrate basis if any,
- names the `refresh_scope_axis_remediation_collateral_state` / whether this is local-workload-replacement, drain-backed-restoration, fenced-substrate-restoration, or mixed-refresh-scope-axis-remediation-collateral,
- states what stronger surfaces still outrank the witness,
- and states the fail-closed repair / keep-current vs narrow-claim vs split-scope vs issue-new-refresh-scope-axis-remediation-collateral-witness vs quarantine-remediation-collateral-tariff consequence if the present continuity claim is not actually restored by the claimed collateral lane.

Do not use refresh-scope-axis-remediation-collateral as a standing disruption-budget court. Use this prompt pair only where axis independence, materiality, coupling, enforcement, durability, and remediation provenance are already established and the missing question is how much collateral the restoration spent once drift was repaired.
```

**Continuation prompt**

```text
Continue the refresh-scope-axis-remediation-collateral pass with one high-leverage collateral clarification only. Prefer the smallest witness that says what governed row is still being justified, what stake object is supposedly widened, what prior refresh-scope-axis-remediation evidence exists, what current corroborating axes exist, what local-workload-replacement basis if any now exists, what drain-backed basis if any now exists, what fenced-substrate basis if any now exists, what `refresh_scope_axis_remediation_collateral_state` is honest, what stronger surfaces still outrank the witness, and what keep-current, narrow-claim, split-scope, issue-new-refresh-scope-axis-remediation-collateral-witness, quarantine, or recover-resync consequence follows if the present restoration is local-workload-replacement, drain-backed-restoration, fenced-substrate-restoration, or mixed-refresh-scope-axis-remediation-collateral. Run `make lint` and package the release.
```

Use `docs/10-method/refresh-scope-axis-remediation-collateral-witnesses-local-workload-replacement-drain-backed-restoration-and-fenced-substrate-restoration.md` when the live question is whether repaired or rebalanced decoupling came back through a local workload replacement, a broader drain-backed move, or fenced-substrate recovery.
"""
ensure_contains("docs/50-promptcraft/prompt-pairs.md", "Use `docs/10-method/refresh-scope-axis-remediation-witnesses-native-controller-restoration-external-remediator-restoration-and-operator-replay-restoration.md` when the live question is whether repaired or rebalanced decoupling came back through the platform's own controller path, an auxiliary remediator, or a manual replay act.\n", pp_doc_add)

# --- claim registry ---
claim_add = f"""
- `{CL}` — Archive continuity may improve when DelayBasin preserves one compact **refresh-scope-axis-remediation-collateral witness / drain-budget card / fenced-substrate brake** whenever a current continuity claim depends not only on whether corroborating axes are genuinely independent, materially backed, decoupled under perturbation, hard-enforced, durable, and explicitly restored, but on how much surrounding workload or substrate disruption that restoration spends: name the **governed row or surface**, the **stake object / line of concern**, the **prior refresh-scope-axis-remediation evidence**, the **current corroborating axes**, the **local-workload-replacement basis if any**, the **drain-backed basis if any**, the **fenced-substrate basis if any**, the **refresh_scope_axis_remediation_collateral_state**, and the **fail-closed repair** rather than letting drain-backed or fenced-substrate restoration silently inherit the cheap authority of local workload replacement.
  - Status: speculative but central
  - Wired docs: `{NEW_DOC}`, `docs/20-constitution/open-question-registry.md`, `docs/20-constitution/prompt-pair-registry.md`, `docs/50-promptcraft/prompt-pairs.md`, `docs/00-meta/llm-runbook.md`, `WITNESS-VOCABULARY.json`, `REVISION-RECEIPT.json`
"""
ensure_contains("docs/20-constitution/claim-registry.md", "- `CL-0151` — Archive continuity may improve when DelayBasin preserves one compact **refresh-scope-axis-remediation witness / repair-provenance card / replay-lane brake** whenever a current continuity claim depends not only on whether corroborating axes are genuinely independent, materially backed, decoupled under perturbation, hard-enforced, and durable, but on who or what actually restores the decoupling after drift: name the **governed row or surface**, the **stake object / line of concern**, the **prior refresh-scope-axis-durability evidence**, the **current corroborating axes**, the **native-controller basis if any**, the **external-remediator basis if any**, the **operator-replay basis if any**, the **refresh_scope_axis_remediation_state**, and the **fail-closed repair** rather than letting repaired decoupling silently inherit the authority of native self-healing when it actually depends on auxiliary loops or operator replay.\n  - Status: speculative but central\n  - Wired docs: `docs/10-method/refresh-scope-axis-remediation-witnesses-native-controller-restoration-external-remediator-restoration-and-operator-replay-restoration.md`, `docs/20-constitution/open-question-registry.md`, `docs/20-constitution/prompt-pair-registry.md`, `docs/50-promptcraft/prompt-pairs.md`, `docs/00-meta/llm-runbook.md`, `WITNESS-VOCABULARY.json`, `REVISION-RECEIPT.json`\n", "\n" + claim_add)

# --- open questions + trajectory ---
new_oq_block = f"""
- `{OQ}` — what remediation-collateral witness distinguishes local workload replacement from drain or fenced-substrate restoration after drift?
  - Why it matters: if DelayBasin cannot separate local replacement from broad drain or fenced-substrate recovery, later sessions may narrate cheap self-healing from restoration that actually spends a much wider disruption budget.
  - Current posture: resolved by `{RS}` via `{NEW_DOC}`; reopen only if the compact refresh-scope-axis-remediation-collateral witness proves insufficient and stronger remediation-collateral governance is honestly required

- `{NEXT_OQ}` — what remediation-capacity-source witness distinguishes restoration that reuses free capacity from restoration that succeeds only by preempting unrelated lower-priority work?
  - Why it matters: if DelayBasin cannot separate free-capacity recovery from preemption-backed recovery, later sessions may narrate low-collateral self-healing from restoration that only works by displacing unrelated work.
  - Current posture: unresolved
"""
replace_open_question_block("docs/20-constitution/open-question-registry.md", OQ, new_oq_block)

traj_old = """110. Determine what refresh-scope-axis-remediation-collateral witness distinguishes local workload replacement from broad drain or fenced-substrate restoration when decoupling is restored after drift.

A fresh extension is that once remediation provenance is explicit, DelayBasin may next need to say how much surrounding substrate or neighboring workload disruption the restoration spends. Otherwise native or external restoration may silently inherit the authority of cheap local repair even when the real mechanism drains or fences a broader slice of the system.
- `OQ-0154` — what remediation-collateral witness distinguishes local workload replacement from drain or fenced-substrate restoration after drift?
  - Why it matters: if DelayBasin cannot separate local replacement from broad drain or fenced-substrate recovery, later sessions may narrate cheap self-healing from restoration that actually spends a much wider disruption budget.
  - Current posture: unresolved
"""
traj_new = f"""110. Determine what refresh-scope-axis-remediation-collateral witness distinguishes local workload replacement from broad drain or fenced-substrate restoration when decoupling is restored after drift.

A fresh extension is that once remediation provenance is explicit, DelayBasin may next need to say how much surrounding substrate or neighboring workload disruption the restoration spends. Otherwise native or external restoration may silently inherit the authority of cheap local repair even when the real mechanism drains or fences a broader slice of the system.
- `{OQ}` — what remediation-collateral witness distinguishes local workload replacement from drain or fenced-substrate restoration after drift?
  - Why it matters: if DelayBasin cannot separate local replacement from broad drain or fenced-substrate recovery, later sessions may narrate cheap self-healing from restoration that actually spends a much wider disruption budget.
  - Current posture: resolved by `{RS}` via `{NEW_DOC}`; reopen only if the compact refresh-scope-axis-remediation-collateral witness proves insufficient and stronger remediation-collateral governance is honestly required

111. Determine what remediation-capacity-source witness distinguishes restoration that reuses free capacity from restoration that succeeds only by preempting unrelated lower-priority work.

A fresh extension is that once restoration collateral is explicit, DelayBasin may next need to say whether the recovered placement used spare capacity already available or only returned by evicting or suspending unrelated lower-priority work. Otherwise even a local-looking replacement may silently inherit the authority of low-collateral repair when it actually depends on a priority or preemption bill paid elsewhere.
- `{NEXT_OQ}` — what remediation-capacity-source witness distinguishes restoration that reuses free capacity from restoration that succeeds only by preempting unrelated lower-priority work?
  - Why it matters: if DelayBasin cannot separate free-capacity recovery from preemption-backed recovery, later sessions may narrate low-collateral self-healing from restoration that only works by displacing unrelated work.
  - Current posture: unresolved
"""
replace_once("docs/00-meta/trajectory-map.md", traj_old, traj_new)

# --- quarantine ---
quarantine_add = f"""

## {QWS} — Some continuations may eventually need a remediation collateral tariff / disruption-budget escrow / blast-radius ledger rather than only a compact refresh-scope-axis-remediation-collateral witness

The bounded admitted move says only how much surrounding disruption the restoration spent: a local workload replacement, a drain-backed move, a fenced-substrate move, or an honest mix.
A stronger neighboring move keeps tempting the archive.
Perhaps later continuations will need to charge broader drain-backed restorations a collateral tariff, keep explicit disruption-budget escrow for fenced substrate recovery, or maintain a blast-radius ledger rather than merely classifying the present restoration lane.

That stronger move is not yet canonical.
The present evidence justifies one compact remediation-collateral witness, not a standing budget or tariff court.

Keep this stronger move quarantined unless repeated future overflows show that local-workload-replacement, drain-backed-restoration, and fenced-substrate-restoration cannot stay honest without explicit disruption pricing or collateral exchange rules.
"""
quarantine = read_text("docs/90-quarantine/wild-speculations-2026-03-08.md")
if f"## {QWS} —" not in quarantine:
    write_text("docs/90-quarantine/wild-speculations-2026-03-08.md", quarantine + quarantine_add)

# --- packet contract common: refactor remaining manual axis branch specs + add new collateral spec ---
new_independence = '''"refresh_scope_axis_independence_witness_contract": refresh_scope_axis_branch_spec(
    doc_path="docs/10-method/refresh-scope-axis-independence-witnesses-renamed-or-mirrored-axis-restatement-nested-axis-restatement-and-independent-axis-corroboration.md",
    title="Refresh-scope-axis-independence witnesses, renamed-or-mirrored axis restatement, nested axis restatement, and independent axis corroboration",
    oq_id="OQ-0148",
    external_pressure_heading="## External pressure from Alertmanager route grouping, Grafana matcher conjunction, Datadog multi-attribute grouping, Kubernetes multiple topology constraints, and Google Cloud layered labels",
    comparison_heading="## Renamed or mirrored axis restatement vs nested axis restatement vs independent axis corroboration vs mixed refresh scope axis independence",
    runbook_ref="refresh-scope-axis-independence-witnesses-renamed-or-mirrored-axis-restatement-nested-axis-restatement-and-independent-axis-corroboration.md",
    prompt_id="PP-0106",
    prompt_needles=["Use `docs/10-method/refresh-scope-axis-independence-witnesses-renamed-or-mirrored-axis-restatement-nested-axis-restatement-and-independent-axis-corroboration.md`", "renamed-or-mirrored-axis-restatement, nested-axis-restatement, independent-axis-corroboration, or mixed-refresh-scope-axis-independence"],
    claim_id="CL-0146",
    resolution_id="RS-0155",
    trajectory_oq_id="OQ-0149",
    qws_id="QWS-0231",
    qws_label="axis materiality ladder / substrate notary / corroboration weight scale",
    changelog_needles=["refresh-scope-axis-independence-witnesses-renamed-or-mirrored-axis-restatement-nested-axis-restatement-and-independent-axis-corroboration.md", "check_refresh_scope_axis_independence_witness_contract.py"],
    family="refresh_scope_axis_independence_state",
    allowed=["renamed-or-mirrored-axis-restatement", "nested-axis-restatement", "independent-axis-corroboration", "mixed-refresh-scope-axis-independence"],
    excluded=["renamed-view-counts-twice", "same-tree-levels-mean-independent", "second-label-proves-second-axis", "axis-independence-ish"],
),'''
replace_registry_block("tools/packet_contract_common.py", "refresh_scope_axis_independence_witness_contract", new_independence)
new_materiality = '''"refresh_scope_axis_materiality_witness_contract": refresh_scope_axis_branch_spec(
    doc_path="docs/10-method/refresh-scope-axis-materiality-witnesses-label-distinct-only-corroboration-failure-domain-backed-corroboration-and-isolation-backed-corroboration.md",
    title="Refresh-scope-axis-materiality witnesses, label-distinct-only corroboration, failure-domain-backed corroboration, and isolation-backed corroboration",
    oq_id="OQ-0149",
    external_pressure_heading="## External pressure from Ray label selectors, Kubernetes zones and topology spread, Slurm and Oracle shape fault domains, and NVIDIA MIG isolation",
    comparison_heading="## Label-distinct-only corroboration vs failure-domain-backed corroboration vs isolation-backed corroboration vs mixed refresh scope axis materiality",
    runbook_ref="refresh-scope-axis-materiality-witnesses-label-distinct-only-corroboration-failure-domain-backed-corroboration-and-isolation-backed-corroboration.md",
    prompt_id="PP-0107",
    prompt_needles=["Use `docs/10-method/refresh-scope-axis-materiality-witnesses-label-distinct-only-corroboration-failure-domain-backed-corroboration-and-isolation-backed-corroboration.md`", "label-distinct-only-corroboration, failure-domain-backed-corroboration, isolation-backed-corroboration, or mixed-refresh-scope-axis-materiality"],
    claim_id="CL-0147",
    resolution_id="RS-0156",
    trajectory_oq_id="OQ-0150",
    qws_id="QWS-0232",
    qws_label="axis-materiality exchange rate / coupling haircut / corroboration capital stack",
    changelog_needles=["refresh-scope-axis-materiality-witnesses-label-distinct-only-corroboration-failure-domain-backed-corroboration-and-isolation-backed-corroboration.md", "check_refresh_scope_axis_materiality_witness_contract.py"],
    family="refresh_scope_axis_materiality_state",
    allowed=["label-distinct-only-corroboration", "failure-domain-backed-corroboration", "isolation-backed-corroboration", "mixed-refresh-scope-axis-materiality"],
    excluded=["different-label-means-material", "zone-sounding-means-isolated", "shared-slice-counts-like-mig", "materiality-ish", "second-label-proves-fault-domain", "shared-gpu-slice-counts-as-isolation", "topology-name-means-substrate-proof"],
),'''
replace_registry_block("tools/packet_contract_common.py", "refresh_scope_axis_materiality_witness_contract", new_materiality)
new_enforcement = '''"refresh_scope_axis_enforcement_witness_contract": refresh_scope_axis_branch_spec(
    doc_path="docs/10-method/refresh-scope-axis-enforcement-witnesses-hard-enforced-decoupled-corroboration-best-effort-decoupled-corroboration-and-advisory-corroboration.md",
    title="Refresh-scope-axis-enforcement witnesses, hard-enforced decoupled corroboration, best-effort decoupled corroboration, and advisory corroboration",
    oq_id="OQ-0151",
    external_pressure_heading="## External pressure from Kubernetes required affinity, topology spread `whenUnsatisfiable`, Slurm `--constraint` versus `--prefer`, Ray strict placement groups, and Topology Manager policies",
    comparison_heading="## Hard-enforced decoupled corroboration vs best-effort decoupled corroboration vs advisory corroboration vs mixed refresh scope axis enforcement",
    runbook_ref="refresh-scope-axis-enforcement-witnesses-hard-enforced-decoupled-corroboration-best-effort-decoupled-corroboration-and-advisory-corroboration.md",
    prompt_id="PP-0109",
    prompt_needles=["Use `docs/10-method/refresh-scope-axis-enforcement-witnesses-hard-enforced-decoupled-corroboration-best-effort-decoupled-corroboration-and-advisory-corroboration.md`", "hard-enforced-decoupled-corroboration, best-effort-decoupled-corroboration, advisory-corroboration, or mixed-refresh-scope-axis-enforcement"],
    claim_id="CL-0149",
    resolution_id="RS-0158",
    trajectory_oq_id="OQ-0152",
    qws_id="QWS-0234",
    qws_label="enforcement credit ledger / softness tax / fallback escrow",
    changelog_needles=["refresh-scope-axis-enforcement-witnesses-hard-enforced-decoupled-corroboration-best-effort-decoupled-corroboration-and-advisory-corroboration.md", "check_refresh_scope_axis_enforcement_witness_contract.py"],
    family="refresh_scope_axis_enforcement_state",
    allowed=["hard-enforced-decoupled-corroboration", "best-effort-decoupled-corroboration", "advisory-corroboration", "mixed-refresh-scope-axis-enforcement"],
    excluded=["preferred-spread-means-guaranteed", "soft-hint-counts-as-hard-gate", "topology-label-means-binding-policy", "enforcement-ish"],
),'''
replace_registry_block("tools/packet_contract_common.py", "refresh_scope_axis_enforcement_witness_contract", new_enforcement)
new_coupling = '''"refresh_scope_axis_coupling_witness_contract": refresh_scope_axis_branch_spec(
    doc_path="docs/10-method/refresh-scope-axis-coupling-witnesses-same-plane-coupled-corroboration-hierarchy-coupled-corroboration-and-perturbation-decoupled-corroboration.md",
    title="Refresh-scope-axis-coupling witnesses, same-plane coupled corroboration, hierarchy-coupled corroboration, and perturbation-decoupled corroboration",
    oq_id="OQ-0150",
    external_pressure_heading="## External pressure from Kubernetes topology hierarchy, Ray placement groups, Slurm topology-aware selection, and NVIDIA GI-vs-CI isolation",
    comparison_heading="## Same-plane coupled corroboration vs hierarchy-coupled corroboration vs perturbation-decoupled corroboration vs mixed refresh scope axis coupling",
    runbook_ref="refresh-scope-axis-coupling-witnesses-same-plane-coupled-corroboration-hierarchy-coupled-corroboration-and-perturbation-decoupled-corroboration.md",
    prompt_id="PP-0108",
    prompt_needles=["Use `docs/10-method/refresh-scope-axis-coupling-witnesses-same-plane-coupled-corroboration-hierarchy-coupled-corroboration-and-perturbation-decoupled-corroboration.md`", "same-plane-coupled-corroboration, hierarchy-coupled-corroboration, perturbation-decoupled-corroboration, or mixed-refresh-scope-axis-coupling"],
    claim_id="CL-0148",
    resolution_id="RS-0157",
    trajectory_oq_id="OQ-0151",
    qws_id="QWS-0233",
    qws_label="axis-covariance matrix / blast-radius notary / perturbation insurance table",
    changelog_needles=["refresh-scope-axis-coupling-witnesses-same-plane-coupled-corroboration-hierarchy-coupled-corroboration-and-perturbation-decoupled-corroboration.md", "check_refresh_scope_axis_coupling_witness_contract.py"],
    family="refresh_scope_axis_coupling_state",
    allowed=["same-plane-coupled-corroboration", "hierarchy-coupled-corroboration", "perturbation-decoupled-corroboration", "mixed-refresh-scope-axis-coupling"],
    excluded=["same-zone-means-decoupled", "nested-topology-counts-twice", "packed-bundles-prove-resilience", "coupling-ish"],
),'''
replace_registry_block("tools/packet_contract_common.py", "refresh_scope_axis_coupling_witness_contract", new_coupling)

# add new collateral spec after remediation
pcc = read_text("tools/packet_contract_common.py")
if '"refresh_scope_axis_remediation_collateral_witness_contract"' not in pcc:
    insertion = '''"refresh_scope_axis_remediation_collateral_witness_contract": refresh_scope_axis_branch_spec(
    doc_path="docs/10-method/refresh-scope-axis-remediation-collateral-witnesses-local-workload-replacement-drain-backed-restoration-and-fenced-substrate-restoration.md",
    title="Refresh-scope-axis-remediation-collateral witnesses, local workload replacement, drain-backed restoration, and fenced-substrate restoration",
    oq_id="OQ-0154",
    external_pressure_heading="## External pressure from Kubernetes controller replacement, `kubectl drain`, out-of-service fencing, OpenShift remediation and maintenance operators, Slurm drain/down states, and NVIDIA GPU Operator node-drain fallback",
    comparison_heading="## Local workload replacement vs drain-backed restoration vs fenced-substrate restoration vs mixed refresh scope axis remediation collateral",
    runbook_ref="refresh-scope-axis-remediation-collateral-witnesses-local-workload-replacement-drain-backed-restoration-and-fenced-substrate-restoration.md",
    prompt_id="PP-0112",
    prompt_needles=["Use `docs/10-method/refresh-scope-axis-remediation-collateral-witnesses-local-workload-replacement-drain-backed-restoration-and-fenced-substrate-restoration.md`", "local-workload-replacement, drain-backed-restoration, fenced-substrate-restoration, or mixed-refresh-scope-axis-remediation-collateral"],
    claim_id="CL-0152",
    resolution_id="RS-0161",
    trajectory_oq_id="OQ-0155",
    qws_id="QWS-0237",
    qws_label="remediation collateral tariff / disruption-budget escrow / blast-radius ledger",
    changelog_needles=["refresh-scope-axis-remediation-collateral-witnesses-local-workload-replacement-drain-backed-restoration-and-fenced-substrate-restoration.md", "check_refresh_scope_axis_remediation_collateral_witness_contract.py"],
    family="refresh_scope_axis_remediation_collateral_state",
    allowed=["local-workload-replacement", "drain-backed-restoration", "fenced-substrate-restoration", "mixed-refresh-scope-axis-remediation-collateral"],
    excluded=["recreated-means-local-enough", "drain-is-just-a-replacement", "fence-counts-like-drain", "collateral-ish"],
),
'''
    marker = '"refresh_scope_axis_remediation_witness_contract": refresh_scope_axis_branch_spec('
    start = pcc.index(marker)
    end = pcc.index('"refresh_scope_axis_coupling_witness_contract"', start)
    pcc = pcc[:end] + insertion + pcc[end:]
    write_text("tools/packet_contract_common.py", pcc)

# --- witness vocabulary ---
wv = load_json("WITNESS-VOCABULARY.json")
wv["families"]["refresh_scope_axis_remediation_collateral_state"] = {
    "allowed": [
        "local-workload-replacement",
        "drain-backed-restoration",
        "fenced-substrate-restoration",
        "mixed-refresh-scope-axis-remediation-collateral",
    ],
    "surfaces": [
        "WITNESS-VOCABULARY.json",
        "REVISION-RECEIPT.json",
        NEW_DOC,
    ],
    "excluded_synonyms": [
        "recreated-means-local-enough",
        "drain-is-just-a-replacement",
        "fence-counts-like-drain",
        "collateral-ish",
    ],
    "comparability_budget": "refresh-scope-axis-remediation-collateral truth is compared by token; the compact witness says whether restored decoupling came back through local workload replacement, a drain-backed move, fenced-substrate recovery, or an honest mix, while raw drain logs, reboot traces, and maintenance runbooks stay in surrounding prose",
}
dump_json("WITNESS-VOCABULARY.json", wv)

# --- ledgers ---
append_item("FOLLOWTHROUGH-QUEUE.json", {
    "id": FT,
    "title": "keep checking whether refresh-scope-axis-remediation-collateral pressure still fits inside one compact successor surface",
    "state": "queued",
    "blocked_object": QWS_LABEL,
    "local_surface": f"docs/90-quarantine/wild-speculations-2026-03-08.md#{QWS}",
    "followthrough_state": "queued",
    "boundary": "do not promote bounded refresh-scope-axis-remediation-collateral clarification into a general disruption-budget machine",
    "next_proof_surface": NEW_DOC,
    "receiving_surface": f"FOLLOWTHROUGH-QUEUE.json#{FT}",
    "repair": "ordinary-continuation",
    "origin_revision": REV,
    "discharge": "revisit-on-next-real-refresh-scope-axis-remediation-collateral-overflow",
    "action_lane": "keep-compact",
    "gate_class": "overflow",
    "blocked_output": QWS_LABEL,
    "owner_surface": f"OBLIGATION-LEDGER.json#{OB}",
    "revision": REV,
    "missing_support": "a later public check on whether one compact refresh-scope-axis-remediation-collateral witness keeps overflowing the bounded rule and honestly warrants richer disruption-budget governance",
    "candidate_surface": f"docs/90-quarantine/wild-speculations-2026-03-08.md#{QWS}",
    "blocked_by": "need repeated evidence that local-vs-drain-vs-fence collateral truth overflows one compact witness",
})
append_item("ASSUMPTION-LEDGER.json", {
    "id": AS,
    "title": "one compact refresh-scope-axis-remediation-collateral witness is enough for now",
    "state": "active",
    "scope": "continuity passes whose current widened public claim depends not only on whether corroborating axes are genuinely independent, materially backed, decoupled, hard-enforced, durable, and explicitly restored, but on whether restored decoupling returned by local workload replacement, drain-backed restoration, or fenced-substrate restoration",
    "invalidation_triggers": [
        "repeated later revisions need standing remediation collateral pricing or disruption-budget accounting rather than one compact refresh-scope-axis-remediation-collateral witness",
        "the archive needs a collateral tariff or blast-radius ledger just to keep local, drain-backed, and fenced-substrate restoration distinct",
        "remediation collateral cases repeatedly fail to stay distinguishable even with the witness in place",
    ],
    "assumption_state": "active",
    "repair": "ordinary-continuation",
    "origin_revision": REV,
    "revision": REV,
    "assumption": "the current evidence only requires one compact refresh-scope-axis-remediation-collateral witness over the existing refresh-scope-axis-remediation and related admitted surfaces rather than a remediation collateral tariff, disruption-budget escrow, or blast-radius ledger",
    "supporting_surfaces": [f"APPLICABILITY-LEDGER.json#{AP}", f"DATACUBE-TRANSFER-LEDGER.json#{TL}", f"FOREIGN-PRESSURE-LEDGER.json#{FP}"],
    "discharge": "discharge when later revisions can keep local-vs-drain-vs-fence restoration honest without a dedicated refresh-scope-axis-remediation-collateral witness, or retire/quarantine it if broader collateral governance becomes repeatedly necessary",
    "witness_surface": f"ASSUMPTION-LEDGER.json#{AS}",
    "assumption_surface": f"ASSUMPTION-LEDGER.json#{AS}",
    "assumption_statement": "the current evidence only requires one compact refresh-scope-axis-remediation-collateral witness over the existing refresh-scope-axis-remediation and related admitted surfaces rather than a remediation collateral tariff, disruption-budget escrow, or blast-radius ledger",
    "action_lane": "keep-compact",
    "gate_class": "concrete-evidence",
})
append_item("OBLIGATION-LEDGER.json", {
    "id": OB,
    "title": "when repaired decoupling keeps needing local-vs-drain-vs-fence separation, DelayBasin should preserve one compact refresh-scope-axis-remediation-collateral witness rather than a collateral tariff ledger",
    "state": "open",
    "witness_surface": f"OBLIGATION-LEDGER.json#{OB}",
    "target_surfaces": [f"docs/90-quarantine/wild-speculations-2026-03-08.md#{QWS}"],
    "missing_support": "a later public check on whether one compact refresh-scope-axis-remediation-collateral witness keeps sufficing and whether local, drain-backed, and fenced-substrate restoration stay distinct without broader disruption pricing",
    "current_support": [f"APPLICABILITY-LEDGER.json#{AP}", f"FOREIGN-PRESSURE-LEDGER.json#{FP}", f"DATACUBE-TRANSFER-LEDGER.json#{TL}"],
    "discharge_path": "either show later that one compact refresh-scope-axis-remediation-collateral witness keeps sufficing or promote broader remediation collateral governance explicitly",
    "obligation_state": "open",
    "repair": "ordinary-continuation",
    "origin_revision": REV,
    "discharge": "reopen-only-if-refresh-scope-axis-remediation-collateral-overflows",
    "revision": REV,
    "owner_surface": f"OBLIGATION-LEDGER.json#{OB}",
    "action_lane": "keep-compact",
    "gate_class": "overflow",
})
append_item("APPLICABILITY-LEDGER.json", {
    "id": AP,
    "title": "the refresh-scope-axis-remediation-collateral witness stays smaller than a remediation collateral tariff ledger",
    "state": "gated",
    "question": "when should DelayBasin treat repaired decoupling with one compact remediation-collateral witness instead of promoting broader disruption pricing or blast-radius accounting?",
    "applies_when": [
        "a revision already has a row whose current claim depends on corroborating axes that are already judged genuinely independent, materially backed, decoupled under perturbation, hard-enforced, durable, and explicit about who restored them",
        "later passes still need to distinguish local-workload-replacement, drain-backed-restoration, fenced-substrate-restoration, or mixed-refresh-scope-axis-remediation-collateral posture",
        "one compact successor surface plus the existing admitted refresh-scope-axis-remediation and related scheduler surfaces still keeps remediation collateral honest without standing budget or tariff machinery",
    ],
    "does_not_apply_when": [
        "the archive honestly requires standing governance over remediation collateral pricing, disruption-budget exchange rates, or blast-radius escrow",
        "the questioned surface is not really about how much surrounding workload or substrate disruption restored drifted decoupling spent",
    ],
    "budget": "one compact refresh-scope-axis-remediation-collateral witness plus one resolution of OQ-0154; no remediation collateral tariff ledger",
    "negative_transfer_budget": "do not treat any repaired or rebalanced return as if it automatically carried the cheap authority of local replacement",
    "origin_revision": REV,
    "discharge": "reopen-only-if-refresh-scope-axis-remediation-collateral-overflows",
    "action_lane": "keep-compact",
    "gate_class": "concrete-evidence",
    "witness_surface": f"APPLICABILITY-LEDGER.json#{AP}",
    "applicability_state": "gated",
    "repair": "ordinary-continuation",
    "matched_budget": "one compact witness foregrounding local replacement vs drain vs fence collateral without widening into disruption-budget accounting",
    "revision": REV,
    "target_objective": "keep remediation collateral honest without inflating a general disruption-pricing layer",
    "carry_object": "refresh-scope-axis-remediation-collateral witness",
    "open_question": NEXT_OQ,
    "applicability_conditions": [
        "a revision already has a row whose current claim depends on corroborating axes that are already judged genuinely independent, materially backed, decoupled under perturbation, hard-enforced, durable, and explicit about who restored them",
        "later passes still need to distinguish local-workload-replacement, drain-backed-restoration, fenced-substrate-restoration, or mixed-refresh-scope-axis-remediation-collateral posture",
        "one compact successor surface plus the existing admitted refresh-scope-axis-remediation and related scheduler surfaces still keeps remediation collateral honest without standing budget or tariff machinery",
    ],
})
append_item("RETROSPECTIVE-QUEUE.json", {
    "id": RT,
    "title": "revisit whether refresh-scope-axis-remediation-collateral pressure stayed bounded after rev0259",
    "state": "cooling",
    "candidate_surface": f"docs/90-quarantine/wild-speculations-2026-03-08.md#{QWS}",
    "cooldown_window": "keep the stronger remediation collateral tariff, disruption-budget escrow, or blast-radius ledger story cooled until at least one later revision shows that one compact refresh-scope-axis-remediation-collateral witness is no longer enough.",
    "adjudication_family": "refresh scope axis remediation collateral / disruption width / blast-radius pressure",
    "supersession_link": f"OBLIGATION-LEDGER.json#{OB}",
    "origin_revision": REV,
    "discharge": "keep-cooling-unless-refresh-scope-axis-remediation-collateral-overflows",
    "action_lane": "keep-compact",
    "gate_class": "overflow",
    "witness_surface": f"RETROSPECTIVE-QUEUE.json#{RT}",
    "revision": REV,
    "cooling_state": "cooling",
    "disposition": "await-adjudication",
    "repair": "keep-cooling",
})
append_item("FIREBREAK-LEDGER.json", {
    "id": FB,
    "title": "the refresh-scope-axis-remediation-collateral import should count as one compact local-vs-drain-vs-fence repair, not as promotion of a remediation collateral tariff ledger",
    "state": "withheld",
    "witness_surface": f"FIREBREAK-LEDGER.json#{FB}",
    "judged_property": "the rev0259 decision that DelayBasin should extract one compact refresh-scope-axis-remediation-collateral witness over the existing refresh-scope-axis-remediation and related admitted surfaces and `refresh_scope_axis_remediation_collateral_state` family while the broader remediation collateral tariff / disruption-budget escrow / blast-radius ledger story remains quarantined",
    "public_extract": [
        NEW_DOC,
        "docs/10-method/refresh-scope-axis-remediation-witnesses-native-controller-restoration-external-remediator-restoration-and-operator-replay-restoration.md",
        "docs/20-constitution/open-question-registry.md",
        f"FOREIGN-PRESSURE-LEDGER.json#{FP}",
        f"APPLICABILITY-LEDGER.json#{AP}",
        "REVISION-RECEIPT.json",
    ],
    "withheld_trace_surface": "same-session drafting residue behind the compact refresh-scope-axis-remediation-collateral-witness versus remediation-collateral-tariff-ledger decision",
    "allowed_role": "bounded drafting aid only; not public support for a broader remediation collateral tariff, disruption-budget escrow, or blast-radius ledger",
    "exposure_rule": "expose or reintegrate only if later passes show that one compact refresh-scope-axis-remediation-collateral witness cannot keep local-vs-drain-vs-fence truth bounded",
    "trace_state": "withheld",
    "repair": "ordinary-continuation",
    "origin_revision": REV,
    "action_lane": "keep-compact",
    "gate_class": "overflow",
    "firebreak_surface": f"FIREBREAK-LEDGER.json#{FB}",
    "discharge": "reopen-only-if-refresh-scope-axis-remediation-collateral-overflows",
    "revision": REV,
    "blocked_object": QWS_LABEL,
})
append_item("FOREIGN-PRESSURE-LEDGER.json", {
    "id": FP,
    "title": "external scheduler and remediation docs support one compact refresh-scope-axis-remediation-collateral witness rather than a disruption-budget ledger",
    "state": "imported",
    "source_packets": [
        {
            "datacube": "KubernetesLocalReplacementAndDrain-2026",
            "surfaces": ["REF-0976", "REF-0981"],
            "pressure": "controller-created workload replacement and explicit node drain are publicly different moves, which pressures DelayBasin not to narrate all restoration as equally local or cheap.",
        },
        {
            "datacube": "KubernetesAndOpenShiftFencing-2026",
            "surfaces": ["REF-0982", "REF-0983"],
            "pressure": "out-of-service taints, remediation reboots, machine deletion, and maintenance operators expose fenced-substrate and drain-backed restoration as distinct collateral classes.",
        },
        {
            "datacube": "SlurmAndGpuOperatorCollateral-2026",
            "surfaces": ["REF-0984", "REF-0985"],
            "pressure": "Slurm node-state controls and NVIDIA's local-GPU-pod-eviction before node-drain fallback keep workload-level replay distinct from drain or substrate collateral in GPU recovery stories.",
        },
    ],
    "reviewed_pattern": "local workload replacement vs drain-backed restoration vs fenced-substrate restoration across already remediated decoupled corroboration",
    "import_decision": "support a compact refresh-scope-axis-remediation-collateral witness and resolve OQ-0154",
    "adopted_take": "DelayBasin should add one compact witness that says whether restored decoupling came back through local workload replacement, drain-backed restoration, fenced-substrate restoration, or an honest mix",
    "supporting_only_take": "the current evidence cleanly supports a bounded refresh-scope-axis-remediation-collateral witness without promoting broader disruption-budget governance",
    "deferred_or_rejected_take": ["remediation collateral tariff", "disruption-budget escrow", "blast-radius ledger"],
    "local_gap": "the archive still lacked one compact successor surface for whether repaired decoupling stayed local, spent a drain, or spent fenced substrate",
    "anchor_surfaces": [
        "docs/10-method/refresh-scope-axis-remediation-witnesses-native-controller-restoration-external-remediator-restoration-and-operator-replay-restoration.md",
        "docs/20-constitution/open-question-registry.md",
        "docs/00-meta/trajectory-map.md",
        f"docs/90-quarantine/wild-speculations-2026-03-08.md#{QWS}",
    ],
    "open_question": NEXT_OQ,
    "repair": "ordinary-continuation",
    "origin_revision": REV,
    "action_lane": "keep-compact",
    "gate_class": "concrete-evidence",
    "discharge": "reopen-only-if-refresh-scope-axis-remediation-collateral-overflows",
    "revision": REV,
    "witness_surface": f"FOREIGN-PRESSURE-LEDGER.json#{FP}",
    "bounded_take": "Keep the archive compact by extracting one refresh-scope-axis-remediation-collateral witness over the existing refresh-scope-axis-remediation and related admitted surfaces; do not promote a remediation collateral tariff, disruption-budget escrow, or blast-radius ledger.",
    "explicit_non_take": ["no remediation collateral tariff", "no disruption-budget escrow", "no blast-radius ledger"],
    "assimilation_state": "imported",
    "foreign_pressure_state": "imported",
    "open_transfer_question": "what remediation-capacity-source witness distinguishes restoration that reuses free capacity from restoration that succeeds only by preempting unrelated lower-priority work?",
    "missing_support": "the current corpus does not yet justify a standing disruption-pricing or collateral-exchange economy across refresh-scope-axis branches",
})
append_item("DATACUBE-TRANSFER-LEDGER.json", {
    "id": TL,
    "title": "refresh-scope-axis-remediation-collateral evidence supports resolving OQ-0154 with one compact local-vs-drain-vs-fence card rather than a disruption-budget ledger",
    "state": "supporting-only",
    "reviewed_pattern": "local workload replacement vs drain-backed restoration vs fenced-substrate restoration across already remediated decoupled corroboration",
    "import_decision": "support a compact refresh-scope-axis-remediation-collateral witness and resolve OQ-0154",
    "adopted_take": "DelayBasin should add one compact witness that says whether restored decoupling came back through local workload replacement, drain-backed restoration, fenced-substrate restoration, or an honest mix",
    "supporting_only_take": "the current evidence cleanly supports a bounded refresh-scope-axis-remediation-collateral witness without promoting broader disruption-budget governance",
    "deferred_or_rejected_take": ["remediation collateral tariff", "disruption-budget escrow", "blast-radius ledger"],
    "local_gap": "the archive still lacked one compact successor surface for whether repaired decoupling stayed local, spent a drain, or spent fenced substrate",
    "anchor_surfaces": [
        "docs/10-method/refresh-scope-axis-remediation-witnesses-native-controller-restoration-external-remediator-restoration-and-operator-replay-restoration.md",
        "docs/20-constitution/open-question-registry.md",
        "docs/00-meta/trajectory-map.md",
        f"docs/90-quarantine/wild-speculations-2026-03-08.md#{QWS}",
    ],
    "open_question": NEXT_OQ,
    "repair": "ordinary-continuation",
    "origin_revision": REV,
    "action_lane": "keep-compact",
    "gate_class": "concrete-evidence",
    "discharge": "reopen-only-if-refresh-scope-axis-remediation-collateral-overflows",
    "revision": REV,
    "witness_surface": f"DATACUBE-TRANSFER-LEDGER.json#{TL}",
    "transfer_state": "supporting-only",
    "bounded_take": "Keep the archive compact by extracting one refresh-scope-axis-remediation-collateral witness over the existing refresh-scope-axis-remediation and related admitted surfaces; do not promote a remediation collateral tariff, disruption-budget escrow, or blast-radius ledger.",
    "explicit_non_take": ["no remediation collateral tariff", "no disruption-budget escrow", "no blast-radius ledger"],
    "open_transfer_question": "whether later passes should add a separate remediation-capacity-source witness once restoration collateral is explicit",
    "missing_support": "a later public check on whether one compact refresh-scope-axis-remediation-collateral witness keeps sufficing",
    "current_support": [f"APPLICABILITY-LEDGER.json#{AP}", f"FOREIGN-PRESSURE-LEDGER.json#{FP}", f"DATACUBE-TRANSFER-LEDGER.json#{TL}"],
    "discharge_path": "either show later that one compact refresh-scope-axis-remediation-collateral witness keeps sufficing or promote broader collateral governance explicitly",
    "reviewed_datacubes": [
        {
            "datacube": "KubernetesPodReplacement-2026",
            "surfaces": ["REF-0976"],
            "pattern": "controller replaces disposable Pods with new instances rather than moving the same Pod object",
            "pressure": "local workload replacement should remain a distinct collateral class",
        },
        {
            "datacube": "KubernetesDrain-2026",
            "surfaces": ["REF-0981"],
            "pattern": "maintenance drain evicts or deletes Pods across a node",
            "pressure": "drain-backed restoration should not inherit local-replacement cheapness",
        },
        {
            "datacube": "KubernetesAndOpenShiftFencing-2026",
            "surfaces": ["REF-0982", "REF-0983"],
            "pattern": "out-of-service and remediation flows fence or reboot substrate before recovery",
            "pressure": "fenced-substrate restoration should remain distinct from drain-backed or local recovery",
        },
        {
            "datacube": "SlurmNodeStates-2026",
            "surfaces": ["REF-0984"],
            "pattern": "node DRAIN/DOWN controls differ from job requeue",
            "pressure": "job-level replay should not be flattened into node-level collateral",
        },
        {
            "datacube": "NvidiaGpuOperatorDrainFallback-2026",
            "surfaces": ["REF-0985"],
            "pattern": "evict GPU pods first, then fall back to node drain only when needed",
            "pressure": "GPU maintenance flows make local-vs-drain collateral explicit and should stay separated",
        },
    ],
})
append_item("RESOLUTION-LEDGER.json", {
    "id": RS,
    "title": "resolve OQ-0154 with one compact refresh-scope-axis-remediation-collateral witness rather than a remediation collateral tariff ledger",
    "state": "resolved",
    "closure_state": "resolved",
    "closure_reason": "rev0259 extracted one compact refresh-scope-axis-remediation-collateral witness, kept the admitted refresh-scope-axis-remediation and related analog surfaces narrow, and kept stronger remediation-collateral-ledger stories quarantined.",
    "discharge": "reopen-only-if-refresh-scope-axis-remediation-collateral-overflows",
    "gate_class": "concrete-evidence",
    "origin_revision": REV,
    "prior_state": "open gap: DelayBasin already had refresh-scope-axis-remediation truth but still lacked one compact successor surface for whether repaired decoupling returned through local workload replacement, drain-backed restoration, or fenced-substrate recovery.",
    "question": "whether one compact refresh-scope-axis-remediation-collateral witness over the existing refresh-scope-axis-remediation and related admitted surfaces is enough for honest local-vs-drain-vs-fence restoration comparison",
    "reopen_trigger": "refresh-scope-axis-remediation-collateral pressure overflows one compact successor surface",
    "reopen_triggers": [
        "later revisions need standing governance over collateral pricing, blast-radius budgets, disruption exchange rates, or broader remediation authority that one compact refresh-scope-axis-remediation-collateral witness cannot honestly absorb"
    ],
    "repair": "ordinary-continuation",
    "resolved_objects": [OQ, AP, FP, TL],
    "revision": REV,
    "successor_surface": NEW_DOC,
    "target_surfaces": [NEW_DOC],
    "action_lane": "keep-compact",
    "witness_surface": f"RESOLUTION-LEDGER.json#{RS}",
})

# --- changelog and archive index ---
changelog = read_text("CHANGELOG.md")
if f"## {REV}" not in changelog:
    entry = f"## {REV} - 2026.03.28.06.47 - remediationcollateral / tariffq / draincarry / braidglass\n\n- Added `{NEW_DOC}` to resolve `{OQ}` with a compact local-vs-drain-vs-fence remediation-collateral witness.\n- Kept the stronger remediation collateral tariff / disruption-budget escrow / blast-radius ledger move explicitly quarantined as `{QWS}` instead of laundering it into canon.\n- Hygiene/meta-engineering improvement: migrated the remaining manual refresh-scope-axis branch specs in `tools/packet_contract_common.py` onto `refresh_scope_axis_branch_spec(...)` so the whole branch family now shares one contract scaffold, and added `{NEW_CHECKER}`.\n\n"
    write_text("CHANGELOG.md", entry + changelog)

arch = read_text("ARCHIVE_INDEX.md")
row = f"| {BUNDLE} | 2026-03-28 | Refresh-scope-axis-remediation-collateral revision: resolved {OQ} with a compact local-vs-drain-vs-fence witness, honestly quarantined stronger remediation collateral governance, and finished standardizing scope-axis branch contract scaffolding to stay wired and cumulative. |\n"
if row not in arch:
    arch = arch.replace("# Archive index\n\n", "# Archive index\n\n" + row)
    write_text("ARCHIVE_INDEX.md", arch)

# --- surface status ---
status = load_json("SURFACE-STATUS.json")
status["operational_head"]["revision"] = REV
status["status_lanes"]["frozen_public_surface"] = BUNDLE
status["status_lanes"]["current_release_surface"] = BUNDLE
status["citation_head"] = {"revision": REV, "surface": BUNDLE}
status["previous_citation_head"] = {"revision": PREV, "surface": f"DelayBasin-{PREV}-2026.03.28.06.12-axisremediation-provenanceq-loopcarry-handrail.zip"}
status["revision"] = REV
status["stamp"] = STAMP
status["slug"] = SLUG
dump_json("SURFACE-STATUS.json", status)

# --- revision receipt ---
receipt = load_json("REVISION-RECEIPT.json")
receipt["revision"] = REV
receipt["created_at"] = CREATED_AT
receipt["summary"] = "Resolved refresh-scope-axis-remediation collateral with a compact local-vs-drain-vs-fence witness, honestly quarantined stronger disruption-budget governance, and finished standardizing remaining scope-axis branch contract specs."
receipt["bundle"] = BUNDLE
receipt["slug"] = SLUG
receipt["summary_highlight"] = SUMMARY_HIGHLIGHT
receipt["codename"] = CODENAME
receipt["resolved_question"] = OQ
receipt["next_open_question"] = NEXT_OQ
receipt["canonical_additions"] = [NEW_DOC]
receipt["quarantine_additions"] = [f"docs/90-quarantine/wild-speculations-2026-03-08.md#{QWS}"]
receipt["checker_additions"] = [NEW_CHECKER]
receipt["change_summary"] = [
    {"kind": "canon", "surface": NEW_DOC, "summary": "added one compact refresh-scope-axis-remediation-collateral witness for local workload replacement vs drain-backed vs fenced-substrate restoration"},
    {"kind": "quarantine", "surface": f"docs/90-quarantine/wild-speculations-2026-03-08.md#{QWS}", "summary": "kept the stronger remediation collateral tariff / disruption-budget escrow / blast-radius ledger move explicitly quarantined"},
    {"kind": "hygiene", "surface": "tools/packet_contract_common.py", "summary": "migrated the remaining manual refresh-scope-axis branch specs onto refresh_scope_axis_branch_spec(...) so the whole branch family now shares one contract scaffold"},
]
receipt["basis_witness"].update({
    "expected_head": PREV,
    "observed_head": PREV,
    "basis_surfaces": [
        "docs/10-method/refresh-scope-axis-remediation-witnesses-native-controller-restoration-external-remediator-restoration-and-operator-replay-restoration.md",
        "docs/00-meta/trajectory-map.md",
        "docs/20-constitution/open-question-registry.md",
    ],
    "session_provenance": f"DelayBasin-{PREV}-2026.03.28.06.12-axisremediation-provenanceq-loopcarry-handrail.zip",
    "basis_omission_basis": "broader remediation collateral pricing was intentionally omitted from canon because the evidence only justified one bounded refresh-scope-axis-remediation-collateral witness",
    "origin_revision": REV,
    "revision_span": f"{PREV} -> {REV}",
})
receipt["scope_witness"].update({
    "exact_target": "one compact refresh-scope-axis-remediation-collateral witness plus one quarantined collateral-tariff move and one small branch-spec refactor",
    "scope_surfaces": [
        "docs/20-constitution/open-question-registry.md",
        "docs/00-meta/trajectory-map.md",
        NEW_DOC,
        "docs/90-quarantine/wild-speculations-2026-03-08.md",
    ],
    "scope_of_change": "refresh-scope-axis-remediation-collateral",
    "origin_revision": REV,
})
receipt["authorship_witness"]["origin_revision"] = REV
receipt["reentry_cue_witness"]["origin_revision"] = REV
receipt["retrospective_write_witness"] = load_json("RETROSPECTIVE-QUEUE.json")["items"][-1]
receipt["followthrough_witness"] = load_json("FOLLOWTHROUGH-QUEUE.json")["items"][-1]
receipt["assumption_witness"] = load_json("ASSUMPTION-LEDGER.json")["items"][-1]
receipt["obligation_witness"] = load_json("OBLIGATION-LEDGER.json")["items"][-1]
receipt["applicability_witness"] = load_json("APPLICABILITY-LEDGER.json")["items"][-1]
receipt["foreign_pressure_witness"] = load_json("FOREIGN-PRESSURE-LEDGER.json")["items"][-1]
receipt["transfer_witness"] = load_json("DATACUBE-TRANSFER-LEDGER.json")["items"][-1]
receipt["resolution_witness"] = load_json("RESOLUTION-LEDGER.json")["items"][-1]
receipt["reasoning_firebreak_witness"] = load_json("FIREBREAK-LEDGER.json")["items"][-1]
receipt["firebreak_witness"] = load_json("FIREBREAK-LEDGER.json")["items"][-1]
receipt["status_witness"].update({
    "frozen_public_surface": BUNDLE,
    "public_state": "frozen-citable",
    "execution_state": "packaged",
})
receipt["vocabulary_witness"] = {
    "witness_surface": "WITNESS-VOCABULARY.json",
    "controlled_families": ["refresh_scope_axis_remediation_collateral_state", "action_lane", "gate_class"],
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
    "ambient_synonyms_excluded": [
        "recreated-means-local-enough",
        "drain-is-just-a-replacement",
        "fence-counts-like-drain",
        "collateral-ish",
    ],
    "comparability_budget": "refresh-scope-axis-remediation-collateral truth is compared by token; the compact witness says whether restored decoupling came back through local workload replacement, a drain-backed move, fenced-substrate recovery, or an honest mix while raw drain logs, reboot traces, and maintenance runbooks stay outside the token",
    "vocabulary_state": "locked",
    "repair": "ordinary-continuation",
    "refresh_scope_axis_remediation_collateral_state": wv["families"]["refresh_scope_axis_remediation_collateral_state"],
    "action_lane": receipt["vocabulary_witness"]["action_lane"],
    "gate_class": receipt["vocabulary_witness"]["gate_class"],
}
receipt["counterfactual_shadow"] = {
    "status": "recorded",
    "nearby_rejected_move": QWS_LABEL,
    "pivot_surface": "docs/90-quarantine/wild-speculations-2026-03-08.md",
    "rejection_reason": "current evidence supports a bounded remediation collateral witness but not a canon-level disruption-budget economy",
    "still_live": f"docs/90-quarantine/wild-speculations-2026-03-08.md#{QWS}",
}
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
receipt["refresh_scope_axis_remediation_collateral_witness"] = {
    "witness_surface": NEW_DOC,
    "family": "refresh_scope_axis_remediation_collateral_state",
    "allowed_tokens": [
        "local-workload-replacement",
        "drain-backed-restoration",
        "fenced-substrate-restoration",
        "mixed-refresh-scope-axis-remediation-collateral",
    ],
    "overflow_rule": "reopen-only-if-refresh-scope-axis-remediation-collateral-overflows",
}
receipt["refresh_scope_axis_remediation_collateral_witness_contract"] = {
    "family": "refresh_scope_axis_remediation_collateral_state",
    "allowed_tokens": [
        "local-workload-replacement",
        "drain-backed-restoration",
        "fenced-substrate-restoration",
        "mixed-refresh-scope-axis-remediation-collateral",
    ],
}
receipt["refresh_scope_axis_remediation_collateral_witness_meta"] = {
    "checker": NEW_CHECKER,
}
artifacts = [
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
    "apply_rev0259.py",
]
receipt["artifacts_touched"] = artifacts
receipt["touched_surfaces"] = artifacts
receipt["import_witness"] = receipt.get("import_witness", {})
dump_json("REVISION-RECEIPT.json", receipt)

print(f"Applied {REV} surfaces.")
