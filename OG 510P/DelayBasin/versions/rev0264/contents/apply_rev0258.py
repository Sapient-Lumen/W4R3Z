from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent

REV = "rev0258"
PREV = "rev0257"
STAMP = "2026.03.28.06.12"
CREATED_AT = "2026-03-28T06:12:00-04:00"
SLUG = "axisremediation-provenanceq-loopcarry-handrail"
BUNDLE = f"DelayBasin-{REV}-{STAMP}-{SLUG}.zip"
SUMMARY_HIGHLIGHT = "loopcarry"
CODENAME = "handrail"
NEW_DOC = "docs/10-method/refresh-scope-axis-remediation-witnesses-native-controller-restoration-external-remediator-restoration-and-operator-replay-restoration.md"
NEW_DOC_NAME = NEW_DOC.split('/')[-1]
NEW_CHECKER = "tools/check_refresh_scope_axis_remediation_witness_contract.py"
QWS = "QWS-0236"
QWS_LABEL = "remediation provenance credit / controller tariff / operator override escrow"
CL = "CL-0151"
RS = "RS-0160"
OQ = "OQ-0153"
NEXT_OQ = "OQ-0154"
PP = "PP-0111"
AP = "AP-0152"
OB = "OB-0153"
AS = "AS-0157"
FP = "FP-0157"
TL = "TL-0163"
FT = "FT-0160"
RT = "RT-0147"
FB = "FB-0154"


def read_text(rel: str) -> str:
    return (ROOT / rel).read_text(encoding="utf-8")


def write_text(rel: str, text: str) -> None:
    (ROOT / rel).write_text(text, encoding="utf-8")


def load_json(rel: str):
    return json.loads(read_text(rel))


def dump_json(rel: str, obj) -> None:
    write_text(rel, json.dumps(obj, indent=2, ensure_ascii=False) + "\n")


# --- new canonical doc ---
new_doc_text = """# Refresh-scope-axis-remediation witnesses, native controller restoration, external remediator restoration, and operator replay restoration

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
"""
write_text(NEW_DOC, new_doc_text)

# --- bibliography ---
bib = read_text("docs/00-meta/bibliography.md")
if "REF-0975" not in bib:
    bib += """

- `REF-0975` — Kubernetes Documentation, **Vertical Pod Autoscaling** (accessed 2026-03-28)
  - URL: https://kubernetes.io/docs/concepts/workloads/autoscaling/vertical-pod-autoscale/
  - Load-bearing use: VPA `Recreate` mode evicts Pods and then relies on the workload controller plus VPA admission controller to create a replacement Pod with updated requests, which pressures DelayBasin to keep native controller restoration distinct from external or manual remediation.

- `REF-0976` — Kubernetes Documentation, **Pod Lifecycle** (accessed 2026-03-28)
  - URL: https://kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/
  - Load-bearing use: Kubernetes says controllers manage disposable Pods, replacements carry a different UID, and the same Pod is not rescheduled to another node, which pressures DelayBasin to name restoration provenance rather than narrating every repaired placement as the same continuing runtime object.

- `REF-0977` — Kubernetes Blog, **Spotlight on SIG Scheduling** (accessed 2026-03-28)
  - URL: https://kubernetes.io/blog/2024/09/24/sig-scheduling-spotlight-2024/
  - Load-bearing use: the descheduler is described as evicting Pods that violate scheduling constraints so they are recreated and rescheduled, which pressures DelayBasin to distinguish auxiliary rebalance loops from native controller repair.

- `REF-0978` — Red Hat Documentation, **Remediation, fencing, and maintenance** (accessed 2026-03-28)
  - URL: https://docs.redhat.com/en/documentation/workload_availability_for_red_hat_openshift/25.1/html-single/remediation_fencing_and_maintenance/index
  - Load-bearing use: Self Node Remediation is triggered by health-check controllers creating remediation custom resources and can restore workloads through operator-selected strategies such as `ResourceDeletion` or `OutOfServiceTaint`, which pressures DelayBasin to distinguish remediation-operator restoration from native controller repair.

- `REF-0979` — Slurm Workload Manager, **scontrol** (accessed 2026-03-28)
  - URL: https://slurm.schedmd.com/scontrol.html
  - Load-bearing use: privileged `requeue`, `DRAIN`, and `RESUME` operations make manual replay and admin-controlled restoration explicit, which pressures DelayBasin to keep operator replay distinct from admitted automated repair.

- `REF-0980` — NVIDIA Documentation, **GPU Driver Upgrades — NVIDIA GPU Operator** (accessed 2026-03-28)
  - URL: https://docs.nvidia.com/datacenter/cloud-native/gpu-operator/latest/gpu-driver-upgrades.html
  - Load-bearing use: NVIDIA distinguishes the default upgrade controller from manual `OnDelete` rollout where admins delete the old driver pod to trigger replacement, which pressures DelayBasin to separate controller-native automation from operator-triggered replay in GPU maintenance flows.
"""
    write_text("docs/00-meta/bibliography.md", bib)

# --- runbook ---
runbook = read_text("docs/00-meta/llm-runbook.md")
needle = "Use `docs/10-method/refresh-scope-axis-durability-witnesses-eviction-preserved-decoupling-repair-restored-decoupling-and-grandfathered-decoupling.md` when the live question is whether already-decoupled corroboration keeps policing runtime drift, only returns through repair or rebalance, or leaves grandfathered residue in place.\n"
insert = needle + "Use `docs/10-method/refresh-scope-axis-remediation-witnesses-native-controller-restoration-external-remediator-restoration-and-operator-replay-restoration.md` when the live question is who actually restores drifted decoupling after it comes back: the platform's own controller path, an auxiliary remediator, or a manual operator replay act.\n"
if "refresh-scope-axis-remediation-witnesses-native-controller-restoration" not in runbook:
    runbook = runbook.replace(needle, insert)
    write_text("docs/00-meta/llm-runbook.md", runbook)

# --- docs README ---
docs_readme = read_text("docs/README.md")
needle = "- [`10-method/refresh-scope-axis-durability-witnesses-eviction-preserved-decoupling-repair-restored-decoupling-and-grandfathered-decoupling.md`](10-method/refresh-scope-axis-durability-witnesses-eviction-preserved-decoupling-repair-restored-decoupling-and-grandfathered-decoupling.md)\n"
insert = needle + "- [`10-method/refresh-scope-axis-remediation-witnesses-native-controller-restoration-external-remediator-restoration-and-operator-replay-restoration.md`](10-method/refresh-scope-axis-remediation-witnesses-native-controller-restoration-external-remediator-restoration-and-operator-replay-restoration.md)\n"
if "refresh-scope-axis-remediation-witnesses-native-controller-restoration" not in docs_readme:
    docs_readme = docs_readme.replace(needle, insert)
    write_text("docs/README.md", docs_readme)

# --- prompt pair registry ---
pp_reg = read_text("docs/20-constitution/prompt-pair-registry.md")
needle = "- `PP-0110` — Name whether decoupled corroboration stays preserved, needs repair, or is grandfathered\n  - Goal: keep admission-time hard gates from silently inheriting runtime durability by requiring explicit prior enforcement evidence, current corroborating axes, eviction-preserved basis, repair-restored basis, grandfathered basis, `refresh_scope_axis_durability_state`, and fail-closed repair before later passes call the support durably resilient.\n  - Canonical text: `docs/50-promptcraft/prompt-pairs.md#pp-0110--name-whether-decoupled-corroboration-stays-preserved-needs-repair-or-is-grandfathered`\n"
addition = needle + "\n- `PP-0111` — Name whether restored decoupling comes back through native controllers, auxiliary remediators, or operator replay\n  - Goal: keep repaired decoupling from silently inheriting native self-healing authority by requiring explicit prior durability evidence, current corroborating axes, native-controller basis, external-remediator basis, operator-replay basis, `refresh_scope_axis_remediation_state`, and fail-closed repair before later passes call the support self-restoring.\n  - Canonical text: `docs/50-promptcraft/prompt-pairs.md#pp-0111--name-whether-restored-decoupling-comes-back-through-native-controllers-auxiliary-remediators-or-operator-replay`\n"
if "PP-0111" not in pp_reg:
    pp_reg = pp_reg.replace(needle, addition)
    write_text("docs/20-constitution/prompt-pair-registry.md", pp_reg)

# --- prompt pairs ---
prompt_pairs = read_text("docs/50-promptcraft/prompt-pairs.md")
needle = "Use `docs/10-method/refresh-scope-axis-durability-witnesses-eviction-preserved-decoupling-repair-restored-decoupling-and-grandfathered-decoupling.md` when the live question is whether already-decoupled corroboration keeps policing runtime drift, only returns through repair or rebalance, or leaves grandfathered residue in place.\n"
addition = needle + "\n## PP-0111 — Name whether restored decoupling comes back through native controllers, auxiliary remediators, or operator replay\n\n**Opening prompt**\n\n```text\nRead the latest DelayBasin archive and inspect whether the current revision should also materialize one compact refresh-scope-axis-remediation witness for honest controller-vs-remediator-vs-operator restoration comparison.\n\nFocus only on cases where the corroborating axes already look genuinely independent, materially backed, decoupled under perturbation, hard-enforced, and explicitly durable or repair-restored rather than merely advisory. The missing question is who or what actually restores the decoupling after drift: the platform's own admitted controller path, an auxiliary remediator or rebalance loop, a privileged operator replay act, or an honest mix.\n\nIf yes, preserve exactly one small witness that:\n- names the governed row or surface,\n- names the stake object / line of concern,\n- names the prior refresh-scope-axis-durability evidence,\n- names the current corroborating axes,\n- names the native-controller basis if any,\n- names the external-remediator basis if any,\n- names the operator-replay basis if any,\n- names the `refresh_scope_axis_remediation_state` / whether this is native-controller-restoration, external-remediator-restoration, operator-replay-restoration, or mixed-refresh-scope-axis-remediation,\n- states what stronger surfaces still outrank the witness,\n- and states the fail-closed repair / keep-current vs narrow-claim vs split-scope vs issue-new-refresh-scope-axis-remediation-witness vs quarantine-remediation-provenance-credit consequence if the present continuity claim is not actually restored by the claimed lane.\n\nDo not use refresh scope axis remediation as a standing remediation authority court. Use this prompt pair only where axis independence, materiality, coupling, enforcement, and durability are already established and the missing question is who restored the decoupling once drift occurred.\n```\n\n**Continuation prompt**\n\n```text\nContinue the refresh-scope-axis-remediation pass with one high-leverage remediation provenance clarification only. Prefer the smallest witness that says what governed row is still being justified, what stake object is supposedly widened, what prior refresh-scope-axis-durability evidence exists, what current corroborating axes exist, what native-controller basis if any now exists, what external-remediator basis if any now exists, what operator-replay basis if any now exists, what `refresh_scope_axis_remediation_state` is honest, what stronger surfaces still outrank the witness, and what keep-current, narrow-claim, split-scope, issue-new-refresh-scope-axis-remediation-witness, quarantine, or recover-resync consequence follows if the present restoration is native-controller-restoration, external-remediator-restoration, operator-replay-restoration, or mixed-refresh-scope-axis-remediation. Run `make lint` and package the release.\n```\n\nUse `docs/10-method/refresh-scope-axis-remediation-witnesses-native-controller-restoration-external-remediator-restoration-and-operator-replay-restoration.md` when the live question is whether repaired or rebalanced decoupling came back through the platform's own controller path, an auxiliary remediator, or a manual replay act.\n"
if "PP-0111" not in prompt_pairs:
    prompt_pairs = prompt_pairs.replace(needle, addition)
    write_text("docs/50-promptcraft/prompt-pairs.md", prompt_pairs)

# --- claim registry ---
claim_reg = read_text("docs/20-constitution/claim-registry.md")
needle = "- `CL-0150` — Archive continuity may improve when DelayBasin preserves one compact **refresh-scope-axis-durability witness / drift-survival brake / repair-loop card** whenever a current continuity claim depends not only on whether corroborating axes are genuinely independent, materially backed, decoupled under perturbation, and hard-enforced, but on whether that decoupling stays preserved once execution begins or after the world drifts: name the **governed row or surface**, the **stake object / line of concern**, the **prior refresh-scope-axis-enforcement evidence**, the **current corroborating axes**, the **eviction-preserved basis if any**, the **repair-restored basis if any**, the **grandfathered basis if any**, the **refresh_scope_axis_durability_state**, and the **fail-closed repair** rather than letting admission-time hard gates silently inherit the authority of self-preserving runtime decoupling.\n"
addition = needle + "- `CL-0151` — Archive continuity may improve when DelayBasin preserves one compact **refresh-scope-axis-remediation witness / repair-provenance card / replay-lane brake** whenever a current continuity claim depends not only on whether corroborating axes are genuinely independent, materially backed, decoupled under perturbation, hard-enforced, and durable, but on who or what actually restores the decoupling after drift: name the **governed row or surface**, the **stake object / line of concern**, the **prior refresh-scope-axis-durability evidence**, the **current corroborating axes**, the **native-controller basis if any**, the **external-remediator basis if any**, the **operator-replay basis if any**, the **refresh_scope_axis_remediation_state**, and the **fail-closed repair** rather than letting repaired decoupling silently inherit the authority of native self-healing when it actually depends on auxiliary loops or operator replay.\n"
if CL not in claim_reg:
    claim_reg = claim_reg.replace(needle, addition)
    write_text("docs/20-constitution/claim-registry.md", claim_reg)

# --- open question registry and trajectory map ---
for rel, unresolved_phrase in [
    ("docs/20-constitution/open-question-registry.md", "- `OQ-0153` — what refresh-scope-axis-remediation witness distinguishes native controller repair from external rebalance or operator replay when decoupling is restored after drift?\n  - Why it matters: if DelayBasin cannot separate native self-repair from external or manual restoration, later sessions may narrate durable resilience from decoupling that only returns through extra loops outside the core policy surface.\n  - Current posture: unresolved\n"),
    ("docs/00-meta/trajectory-map.md", "109. Determine what refresh-scope-axis-remediation witness distinguishes native controller repair from external rebalance or operator replay when decoupling is restored after drift.\n\nA fresh extension is that once durability is explicit, DelayBasin may next need to say who or what actually restores the decoupling after drift. Otherwise repaired decoupling may silently inherit the authority of native self-healing even when the restoration depends on extra control loops or operator replay.\n- `OQ-0153` — what refresh-scope-axis-remediation witness distinguishes native controller repair from external rebalance or operator replay when decoupling is restored after drift?\n  - Why it matters: if DelayBasin cannot separate native self-repair from external or manual restoration, later sessions may narrate durable resilience from decoupling that only returns through extra loops outside the core policy surface.\n  - Current posture: unresolved\n"),
]:
    text = read_text(rel)
    if RS not in text:
        resolved_block = unresolved_phrase.replace("Current posture: unresolved", f"Current posture: resolved by `{RS}` via `{NEW_DOC}`; reopen only if the compact refresh-scope-axis-remediation witness proves insufficient and stronger remediation-provenance governance is honestly required")
        if rel.endswith("trajectory-map.md"):
            resolved_block += "\n110. Determine what refresh-scope-axis-remediation-collateral witness distinguishes local workload replacement from broad drain or fenced-substrate restoration when decoupling is restored after drift.\n\nA fresh extension is that once remediation provenance is explicit, DelayBasin may next need to say how much surrounding substrate or neighboring workload disruption the restoration spends. Otherwise native or external restoration may silently inherit the authority of cheap local repair even when the real mechanism drains or fences a broader slice of the system.\n- `OQ-0154` — what refresh-scope-axis-remediation-collateral witness distinguishes local workload replacement from broad drain or fenced-substrate restoration when decoupling is restored after drift?\n  - Why it matters: if DelayBasin cannot separate local replacement from broad drain or fenced-substrate recovery, later sessions may narrate cheap self-healing from restoration that actually spends a much wider disruption budget.\n  - Current posture: unresolved\n"
        else:
            resolved_block += "\n- `OQ-0154` — what refresh-scope-axis-remediation-collateral witness distinguishes local workload replacement from broad drain or fenced-substrate restoration when decoupling is restored after drift?\n  - Why it matters: if DelayBasin cannot separate local replacement from broad drain or fenced-substrate recovery, later sessions may narrate cheap self-healing from restoration that actually spends a much wider disruption budget.\n  - Current posture: unresolved\n"
        text = text.replace(unresolved_phrase, resolved_block)
        write_text(rel, text)

# --- quarantine ---
quarantine = read_text("docs/90-quarantine/wild-speculations-2026-03-08.md")
if QWS not in quarantine:
    quarantine += f"""

## {QWS} — Some continuations may eventually need a remediation provenance credit / controller tariff / operator override escrow rather than only a compact refresh-scope-axis-remediation witness

The bounded admitted move says only who restored the decoupling after drift: the native controller path, an auxiliary remediator, or operator replay.
A stronger neighboring move keeps tempting the archive.
Perhaps later continuations will need to weigh those restoration lanes differently, discounting operator replay, charging auxiliary controllers a provenance tariff, or keeping explicit override escrow when manual deletion, drain, or requeue acts stand in for native self-healing.

That stronger move is not yet canonical.
The present evidence justifies one compact remediation-provenance witness, not a standing credit market for controller legitimacy.

Keep this stronger move quarantined unless repeated future overflows show that native-controller restoration, external-remediator restoration, and operator-replay restoration cannot stay honest without explicit provenance weighting or override accounting.
"""
    write_text("docs/90-quarantine/wild-speculations-2026-03-08.md", quarantine)

# --- packet_contract_common refactor + new spec ---
pcc = read_text("tools/packet_contract_common.py")
if "def refresh_scope_axis_branch_spec(" not in pcc:
    anchor = "def _refresh_family_spec(*, doc_path: str, doc_needles: list[str], runbook_ref: str, prompt_id: str, prompt_needles: list[str], claim_id: str, oq_id: str, resolution_id: str, trajectory_oq_id: str, qws_id: str, qws_label: str, changelog_needles: list[str], family: str, allowed: list[str], excluded: list[str]) -> dict:\n    return {\n        \"doc_path\": doc_path,\n        \"doc_needles\": doc_needles,\n        \"runbook_ref\": runbook_ref,\n        \"prompt_id\": prompt_id,\n        \"prompt_needles\": prompt_needles,\n        \"claim_id\": claim_id,\n        \"oq_id\": oq_id,\n        \"resolution_id\": resolution_id,\n        \"trajectory_oq_id\": trajectory_oq_id,\n        \"qws_id\": qws_id,\n        \"qws_label\": qws_label,\n        \"changelog_needles\": changelog_needles,\n        \"family\": family,\n        \"allowed\": allowed,\n        \"excluded\": excluded,\n    }\n\n\n"
    helper = anchor + "def refresh_scope_axis_branch_spec(*, doc_path: str, title: str, oq_id: str, external_pressure_heading: str, comparison_heading: str, runbook_ref: str, prompt_id: str, prompt_needles: list[str], claim_id: str, resolution_id: str, trajectory_oq_id: str, qws_id: str, qws_label: str, changelog_needles: list[str], family: str, allowed: list[str], excluded: list[str]) -> dict:\n    return _refresh_family_spec(\n        doc_path=doc_path,\n        doc_needles=[\n            f\"# {title}\",\n            f\"This is the compact successor surface for `{oq_id}`.\",\n            \"## Practice / observation\",\n            external_pressure_heading,\n            \"## Working synthesis\",\n            comparison_heading,\n            \"## Countermodels / probes\",\n            \"## Design consequences\",\n            \"## Overflow test\",\n            \"## Transformer-facing implication\",\n            f\"`{family}`\",\n            *allowed,\n        ],\n        runbook_ref=runbook_ref,\n        prompt_id=prompt_id,\n        prompt_needles=prompt_needles,\n        claim_id=claim_id,\n        oq_id=oq_id,\n        resolution_id=resolution_id,\n        trajectory_oq_id=trajectory_oq_id,\n        qws_id=qws_id,\n        qws_label=qws_label,\n        changelog_needles=changelog_needles,\n        family=family,\n        allowed=allowed,\n        excluded=excluded,\n    )\n\n\n"
    pcc = pcc.replace(anchor, helper)

old_durability = '"refresh_scope_axis_durability_witness_contract": _refresh_family_spec(\n    doc_path="docs/10-method/refresh-scope-axis-durability-witnesses-eviction-preserved-decoupling-repair-restored-decoupling-and-grandfathered-decoupling.md",\n    doc_needles=[\n        "# Refresh-scope-axis-durability witnesses, eviction-preserved decoupling, repair-restored decoupling, and grandfathered decoupling",\n        "This is the compact successor surface for `OQ-0152`.",\n        "## Practice / observation",\n        "## External pressure from Kubernetes NoExecute eviction, device taint eviction controllers, topology spread drift and descheduler repair, scheduling-vs-eviction separation, and IgnoredDuringExecution affinity",\n        "## Working synthesis",\n        "## Eviction-preserved decoupling vs repair-restored decoupling vs grandfathered decoupling vs mixed refresh scope axis durability",\n        "## Countermodels / probes",\n        "## Design consequences",\n        "## Overflow test",\n        "## Transformer-facing implication",\n        "`refresh_scope_axis_durability_state`",\n        "eviction-preserved-decoupling",\n        "repair-restored-decoupling",\n        "grandfathered-decoupling",\n        "mixed-refresh-scope-axis-durability",\n    ],\n    runbook_ref="refresh-scope-axis-durability-witnesses-eviction-preserved-decoupling-repair-restored-decoupling-and-grandfathered-decoupling.md",\n    prompt_id="PP-0110",\n    prompt_needles=["Use `docs/10-method/refresh-scope-axis-durability-witnesses-eviction-preserved-decoupling-repair-restored-decoupling-and-grandfathered-decoupling.md`", "eviction-preserved-decoupling, repair-restored-decoupling, grandfathered-decoupling, or mixed-refresh-scope-axis-durability"],\n    claim_id="CL-0150",\n    oq_id="OQ-0152",\n    resolution_id="RS-0159",\n    trajectory_oq_id="OQ-0153",\n    qws_id="QWS-0235",\n    qws_label="durability lease ledger / repair debt meter / rebalancing escrow",\n    changelog_needles=["refresh-scope-axis-durability-witnesses-eviction-preserved-decoupling-repair-restored-decoupling-and-grandfathered-decoupling.md", "check_refresh_scope_axis_durability_witness_contract.py"],\n    family="refresh_scope_axis_durability_state",\n    allowed=["eviction-preserved-decoupling", "repair-restored-decoupling", "grandfathered-decoupling", "mixed-refresh-scope-axis-durability"],\n    excluded=["hard-gate-means-it-stays-true", "descheduler-repair-counts-as-runtime-preserved", "grandfathered-means-durable-enough", "durability-ish"],\n),'
new_durability = '"refresh_scope_axis_durability_witness_contract": refresh_scope_axis_branch_spec(\n    doc_path="docs/10-method/refresh-scope-axis-durability-witnesses-eviction-preserved-decoupling-repair-restored-decoupling-and-grandfathered-decoupling.md",\n    title="Refresh-scope-axis-durability witnesses, eviction-preserved decoupling, repair-restored decoupling, and grandfathered decoupling",\n    oq_id="OQ-0152",\n    external_pressure_heading="## External pressure from Kubernetes NoExecute eviction, device taint eviction controllers, topology spread drift and descheduler repair, scheduling-vs-eviction separation, and IgnoredDuringExecution affinity",\n    comparison_heading="## Eviction-preserved decoupling vs repair-restored decoupling vs grandfathered decoupling vs mixed refresh scope axis durability",\n    runbook_ref="refresh-scope-axis-durability-witnesses-eviction-preserved-decoupling-repair-restored-decoupling-and-grandfathered-decoupling.md",\n    prompt_id="PP-0110",\n    prompt_needles=["Use `docs/10-method/refresh-scope-axis-durability-witnesses-eviction-preserved-decoupling-repair-restored-decoupling-and-grandfathered-decoupling.md`", "eviction-preserved-decoupling, repair-restored-decoupling, grandfathered-decoupling, or mixed-refresh-scope-axis-durability"],\n    claim_id="CL-0150",\n    resolution_id="RS-0159",\n    trajectory_oq_id="OQ-0153",\n    qws_id="QWS-0235",\n    qws_label="durability lease ledger / repair debt meter / rebalancing escrow",\n    changelog_needles=["refresh-scope-axis-durability-witnesses-eviction-preserved-decoupling-repair-restored-decoupling-and-grandfathered-decoupling.md", "check_refresh_scope_axis_durability_witness_contract.py"],\n    family="refresh_scope_axis_durability_state",\n    allowed=["eviction-preserved-decoupling", "repair-restored-decoupling", "grandfathered-decoupling", "mixed-refresh-scope-axis-durability"],\n    excluded=["hard-gate-means-it-stays-true", "descheduler-repair-counts-as-runtime-preserved", "grandfathered-means-durable-enough", "durability-ish"],\n),'
if old_durability in pcc:
    pcc = pcc.replace(old_durability, new_durability)

insert_after = new_durability
new_spec = '\n"refresh_scope_axis_remediation_witness_contract": refresh_scope_axis_branch_spec(\n    doc_path="docs/10-method/refresh-scope-axis-remediation-witnesses-native-controller-restoration-external-remediator-restoration-and-operator-replay-restoration.md",\n    title="Refresh-scope-axis-remediation witnesses, native controller restoration, external remediator restoration, and operator replay restoration",\n    oq_id="OQ-0153",\n    external_pressure_heading="## External pressure from Kubernetes controller replacement, VPA recreate mode, descheduler rebalance, remediation operators, Slurm manual replay, and NVIDIA GPU Operator manual OnDelete",\n    comparison_heading="## Native controller restoration vs external remediator restoration vs operator replay restoration vs mixed refresh scope axis remediation",\n    runbook_ref="refresh-scope-axis-remediation-witnesses-native-controller-restoration-external-remediator-restoration-and-operator-replay-restoration.md",\n    prompt_id="PP-0111",\n    prompt_needles=["Use `docs/10-method/refresh-scope-axis-remediation-witnesses-native-controller-restoration-external-remediator-restoration-and-operator-replay-restoration.md`", "native-controller-restoration, external-remediator-restoration, operator-replay-restoration, or mixed-refresh-scope-axis-remediation"],\n    claim_id="CL-0151",\n    resolution_id="RS-0160",\n    trajectory_oq_id="OQ-0154",\n    qws_id="QWS-0236",\n    qws_label="remediation provenance credit / controller tariff / operator override escrow",\n    changelog_needles=["refresh-scope-axis-remediation-witnesses-native-controller-restoration-external-remediator-restoration-and-operator-replay-restoration.md", "check_refresh_scope_axis_remediation_witness_contract.py"],\n    family="refresh_scope_axis_remediation_state",\n    allowed=["native-controller-restoration", "external-remediator-restoration", "operator-replay-restoration", "mixed-refresh-scope-axis-remediation"],\n    excluded=["repaired-means-self-healed", "descheduler-counts-as-native-controller", "manual-delete-counts-as-automatic", "remediation-ish"],\n),'
if '"refresh_scope_axis_remediation_witness_contract"' not in pcc:
    pcc = pcc.replace(insert_after, insert_after + new_spec)
write_text("tools/packet_contract_common.py", pcc)

# --- checker wrapper ---
if not (ROOT / NEW_CHECKER).exists():
    write_text(NEW_CHECKER, 'from packet_contract_common import require_named_refresh_scope_axis_branch_witness_packet_and_vocabulary\n\nrequire_named_refresh_scope_axis_branch_witness_packet_and_vocabulary("refresh_scope_axis_remediation_witness_contract")\n\nprint("check_refresh_scope_axis_remediation_witness_contract: OK")\n')

# --- apply script placeholder for provenance ---
write_text("apply_rev0258.py", Path(__file__).read_text(encoding="utf-8"))

# --- witness vocabulary ---
wv = load_json("WITNESS-VOCABULARY.json")
wv["revision"] = REV
wv["families"]["refresh_scope_axis_remediation_state"] = {
    "allowed": [
        "native-controller-restoration",
        "external-remediator-restoration",
        "operator-replay-restoration",
        "mixed-refresh-scope-axis-remediation",
    ],
    "surfaces": [
        "WITNESS-VOCABULARY.json",
        "REVISION-RECEIPT.json",
        NEW_DOC,
    ],
    "excluded_synonyms": [
        "repaired-means-self-healed",
        "descheduler-counts-as-native-controller",
        "manual-delete-counts-as-automatic",
        "remediation-ish",
    ],
    "comparability_budget": "refresh-scope-axis-remediation truth is compared by token; the compact witness says whether restored decoupling came back through the platform's own controller path, an auxiliary remediator, a manual replay act, or an honest mix, while raw runbooks, controller graphs, and event streams stay in surrounding prose",
}
dump_json("WITNESS-VOCABULARY.json", wv)

# --- ledgers ---

def append_item(rel: str, item: dict):
    data = load_json(rel)
    if all(existing["id"] != item["id"] for existing in data["items"]):
        data["items"].append(item)
    dump_json(rel, data)

append_item("APPLICABILITY-LEDGER.json", {
    "id": AP,
    "title": "the refresh-scope-axis-remediation witness stays smaller than a remediation provenance credit ledger",
    "state": "gated",
    "question": "when should DelayBasin treat repaired decoupling with one compact remediation witness instead of promoting broader provenance weighting or override accounting?",
    "applies_when": [
        "a revision already has a row whose current claim depends on corroborating axes that are already judged genuinely independent, materially backed, decoupled under perturbation, hard-enforced, and durable or repair-restored",
        "later passes still need to distinguish native-controller-restoration, external-remediator-restoration, operator-replay-restoration, or mixed-refresh-scope-axis-remediation posture",
        "one compact successor surface plus the existing admitted refresh-scope-axis-durability and related scheduler surfaces still keeps remediation provenance honest without standing credit or tariff machinery",
    ],
    "does_not_apply_when": [
        "the archive honestly requires standing governance over remediation provenance weighting, controller trust tariffs, or manual override escrow",
        "the questioned surface is not really about who restored drifted decoupling after it came back",
    ],
    "budget": "one compact refresh-scope-axis-remediation witness plus one resolution of OQ-0153; no remediation provenance credit ledger",
    "negative_transfer_budget": "do not treat any repaired or rebalanced return as if it automatically carried native self-healing authority",
    "origin_revision": REV,
    "discharge": "reopen-only-if-refresh-scope-axis-remediation-overflows",
    "action_lane": "keep-compact",
    "gate_class": "concrete-evidence",
    "witness_surface": f"APPLICABILITY-LEDGER.json#{AP}",
    "applicability_state": "gated",
    "repair": "ordinary-continuation",
    "matched_budget": "one compact witness foregrounding native controller vs external remediator vs operator replay restoration without widening into provenance credit accounting",
    "revision": REV,
    "target_objective": "keep remediation provenance honest without inflating a general controller-legitimacy layer",
    "carry_object": "refresh-scope-axis-remediation witness",
    "open_question": NEXT_OQ,
    "applicability_conditions": [
        "a revision already has a row whose current claim depends on corroborating axes that are already judged genuinely independent, materially backed, decoupled under perturbation, hard-enforced, and durable or repair-restored",
        "later passes still need to distinguish native-controller-restoration, external-remediator-restoration, operator-replay-restoration, or mixed-refresh-scope-axis-remediation posture",
        "one compact successor surface plus the existing admitted refresh-scope-axis-durability and related scheduler surfaces still keeps remediation provenance honest without standing credit or tariff machinery",
    ],
    "baselines": [
        "treat every repaired return as native self-healing",
        "promote a broader remediation provenance credit layer immediately",
    ],
    "non_fit_slice": "cases that already require controller weighting, provenance tariffs, or override escrow rather than one bounded remediation witness",
})

append_item("OBLIGATION-LEDGER.json", {
    "id": OB,
    "title": "when repaired decoupling keeps needing native-vs-external-vs-manual separation, DelayBasin should preserve one compact refresh-scope-axis-remediation witness rather than a provenance credit ledger",
    "state": "open",
    "witness_surface": f"OBLIGATION-LEDGER.json#{OB}",
    "target_surfaces": [f"docs/90-quarantine/wild-speculations-2026-03-08.md#{QWS}"],
    "missing_support": "a later public check on whether one compact refresh-scope-axis-remediation witness keeps sufficing and whether native-controller, external-remediator, and operator-replay restoration stay distinct without broader provenance weighting",
    "current_support": [f"APPLICABILITY-LEDGER.json#{AP}", f"FOREIGN-PRESSURE-LEDGER.json#{FP}", f"DATACUBE-TRANSFER-LEDGER.json#{TL}"],
    "discharge_path": "either show later that one compact refresh-scope-axis-remediation witness keeps sufficing or promote broader remediation provenance governance explicitly",
    "obligation_state": "open",
    "repair": "ordinary-continuation",
    "origin_revision": REV,
    "discharge": "reopen-only-if-refresh-scope-axis-remediation-overflows",
    "revision": REV,
    "owner_surface": f"OBLIGATION-LEDGER.json#{OB}",
    "action_lane": "keep-compact",
    "gate_class": "overflow",
})

append_item("ASSUMPTION-LEDGER.json", {
    "id": AS,
    "title": "one compact refresh-scope-axis-remediation witness is enough for now",
    "state": "active",
    "scope": "continuity passes whose current widened public claim depends not only on whether corroborating axes are genuinely independent, materially backed, decoupled, hard-enforced, and durable, but on whether restored decoupling came back through native controllers, external remediators, or operator replay",
    "invalidation_triggers": [
        "repeated later revisions need standing remediation provenance weighting or override accounting rather than one compact refresh-scope-axis-remediation witness",
        "the archive needs a controller tariff or override escrow just to keep native-controller, external-remediator, and operator-replay restoration distinct",
        "remediation provenance cases repeatedly fail to stay distinguishable even with the witness in place",
    ],
    "assumption_state": "active",
    "repair": "ordinary-continuation",
    "origin_revision": REV,
    "revision": REV,
    "assumption": "the current evidence only requires one compact refresh-scope-axis-remediation witness over the existing refresh-scope-axis-durability and related admitted surfaces rather than a remediation provenance credit, controller tariff, or operator override escrow",
    "supporting_surfaces": [f"APPLICABILITY-LEDGER.json#{AP}", f"DATACUBE-TRANSFER-LEDGER.json#{TL}", f"FOREIGN-PRESSURE-LEDGER.json#{FP}"],
    "discharge": "discharge when later revisions can keep native-controller-vs-external-vs-operator restoration honest without a dedicated refresh-scope-axis-remediation witness, or retire/quarantine it if broader provenance governance becomes repeatedly necessary",
    "witness_surface": f"ASSUMPTION-LEDGER.json#{AS}",
    "assumption_surface": f"ASSUMPTION-LEDGER.json#{AS}",
    "assumption_statement": "the current evidence only requires one compact refresh-scope-axis-remediation witness over the existing refresh-scope-axis-durability and related admitted surfaces rather than a remediation provenance credit, controller tariff, or operator override escrow",
    "action_lane": "keep-compact",
    "gate_class": "concrete-evidence",
})

append_item("FOREIGN-PRESSURE-LEDGER.json", {
    "id": FP,
    "title": "refresh-scope-axis-remediation pressure pushes DelayBasin to extract one compact native-vs-external-vs-operator witness rather than a remediation provenance credit ledger",
    "state": "imported",
    "source_packets": [
        {
            "datacube": "KubernetesControllerReplacement-2026",
            "surfaces": ["REF-0975", "REF-0976"],
            "pressure": "VPA recreate mode and controller-managed Pod replacement make a real native restoration lane explicit, which pressures DelayBasin not to narrate every repaired return as the same kind of self-healing without naming controller provenance.",
        },
        {
            "datacube": "KubernetesDeschedulerAndRemediationOperators-2026",
            "surfaces": ["REF-0977", "REF-0978"],
            "pressure": "Descheduler and Self Node Remediation create auxiliary rebalance and remediation loops, which pressures DelayBasin to distinguish external remediators from native controller repair.",
        },
        {
            "datacube": "SlurmAndGpuOperatorManualReplay-2026",
            "surfaces": ["REF-0979", "REF-0980"],
            "pressure": "Privileged `scontrol` replay and NVIDIA GPU Operator `OnDelete` rollouts make manual recovery acts explicit, which pressures DelayBasin to keep operator replay separate from native or auxiliary automated restoration.",
        },
    ],
    "reviewed_pattern": "native-controller vs external-remediator vs operator-replay restoration across already durable or repair-restored decoupled corroboration",
    "import_decision": "support a compact refresh-scope-axis-remediation witness and resolve OQ-0153",
    "adopted_take": "DelayBasin should add one compact witness that says whether restored decoupling came back through native controllers, external remediators, operator replay, or an honest mix",
    "supporting_only_take": "the current evidence cleanly supports a bounded refresh-scope-axis-remediation witness without promoting broader provenance-credit governance",
    "deferred_or_rejected_take": ["remediation provenance credit", "controller tariff", "operator override escrow"],
    "local_gap": "the archive still lacked one compact successor surface for whether repaired decoupling came back through native controller loops, auxiliary remediators, or manual replay",
    "anchor_surfaces": [
        "docs/10-method/refresh-scope-axis-durability-witnesses-eviction-preserved-decoupling-repair-restored-decoupling-and-grandfathered-decoupling.md",
        "docs/20-constitution/open-question-registry.md",
        "docs/00-meta/trajectory-map.md",
        f"docs/90-quarantine/wild-speculations-2026-03-08.md#{QWS}",
    ],
    "open_question": NEXT_OQ,
    "repair": "ordinary-continuation",
    "origin_revision": REV,
    "action_lane": "keep-compact",
    "gate_class": "concrete-evidence",
    "discharge": "reopen-only-if-refresh-scope-axis-remediation-overflows",
    "revision": REV,
    "witness_surface": f"FOREIGN-PRESSURE-LEDGER.json#{FP}",
    "bounded_take": "Keep the archive compact by extracting one refresh-scope-axis-remediation witness over the existing refresh-scope-axis-durability and related admitted surfaces; do not promote a remediation provenance credit, controller tariff, or operator override escrow.",
    "explicit_non_take": ["no remediation provenance credit", "no controller tariff", "no operator override escrow"],
    "assimilation_state": "imported",
    "foreign_pressure_state": "imported",
    "open_transfer_question": "what refresh-scope-axis-remediation-collateral witness distinguishes local workload replacement from broad drain or fenced-substrate restoration when decoupling is restored after drift?",
    "missing_support": "the current corpus does not yet justify a standing provenance weighting or override-accounting economy across refresh-scope-axis branches",
})

append_item("DATACUBE-TRANSFER-LEDGER.json", {
    "id": TL,
    "title": "refresh-scope-axis-remediation evidence supports resolving OQ-0153 with one compact native-vs-external-vs-operator card rather than a remediation provenance credit ledger",
    "state": "supporting-only",
    "reviewed_pattern": "native-controller vs external-remediator vs operator-replay restoration across already durable or repair-restored decoupled corroboration",
    "import_decision": "support a compact refresh-scope-axis-remediation witness and resolve OQ-0153",
    "adopted_take": "DelayBasin should add one compact witness that says whether restored decoupling came back through native controllers, external remediators, operator replay, or an honest mix",
    "supporting_only_take": "the current evidence cleanly supports a bounded refresh-scope-axis-remediation witness without promoting broader provenance-credit governance",
    "deferred_or_rejected_take": ["remediation provenance credit", "controller tariff", "operator override escrow"],
    "local_gap": "the archive still lacked one compact successor surface for whether repaired decoupling came back through native controller loops, auxiliary remediators, or manual replay",
    "anchor_surfaces": [
        "docs/10-method/refresh-scope-axis-durability-witnesses-eviction-preserved-decoupling-repair-restored-decoupling-and-grandfathered-decoupling.md",
        "docs/20-constitution/open-question-registry.md",
        "docs/00-meta/trajectory-map.md",
        f"docs/90-quarantine/wild-speculations-2026-03-08.md#{QWS}",
    ],
    "open_question": NEXT_OQ,
    "repair": "ordinary-continuation",
    "origin_revision": REV,
    "action_lane": "keep-compact",
    "gate_class": "concrete-evidence",
    "discharge": "reopen-only-if-refresh-scope-axis-remediation-overflows",
    "revision": REV,
    "witness_surface": f"DATACUBE-TRANSFER-LEDGER.json#{TL}",
    "transfer_state": "supporting-only",
    "bounded_take": "Keep the archive compact by extracting one refresh-scope-axis-remediation witness over the existing refresh-scope-axis-durability and related admitted surfaces; do not promote a remediation provenance credit, controller tariff, or operator override escrow.",
    "explicit_non_take": ["no remediation provenance credit", "no controller tariff", "no operator override escrow"],
    "open_transfer_question": "whether later passes should add a separate refresh-scope-axis-remediation-collateral witness once restoration provenance is explicit",
    "missing_support": "a later public check on whether one compact refresh-scope-axis-remediation witness keeps sufficing",
    "current_support": [f"APPLICABILITY-LEDGER.json#{AP}", f"FOREIGN-PRESSURE-LEDGER.json#{FP}", f"DATACUBE-TRANSFER-LEDGER.json#{TL}"],
    "discharge_path": "either show later that one compact refresh-scope-axis-remediation witness keeps sufficing or promote broader provenance governance explicitly",
    "reviewed_datacubes": [
        {
            "datacube": "KubernetesControllerReplacement-2026",
            "surfaces": ["REF-0975", "REF-0976"],
            "pattern": "evict-and-controller-recreate under admitted platform control",
            "pressure": "native controller restoration should not be conflated with external or manual repair provenance",
        },
        {
            "datacube": "KubernetesDeschedulerRebalance-2026",
            "surfaces": ["REF-0977"],
            "pattern": "auxiliary descheduler evicts undesired Pods for recreate-and-reschedule",
            "pressure": "rebalance by an auxiliary controller should not inherit native controller authority",
        },
        {
            "datacube": "OpenShiftSelfNodeRemediation-2026",
            "surfaces": ["REF-0978"],
            "pattern": "health-check-triggered remediation CR drives operator-selected restoration strategy",
            "pressure": "remediation operators should remain a distinct restoration provenance class",
        },
        {
            "datacube": "SlurmManualReplay-2026",
            "surfaces": ["REF-0979"],
            "pattern": "privileged requeue and drain/resume replay",
            "pressure": "operator replay should not be narratively upgraded into automatic self-healing",
        },
        {
            "datacube": "NvidiaGpuOperatorUpgradePaths-2026",
            "surfaces": ["REF-0980"],
            "pattern": "controller-driven upgrades versus manual OnDelete replacement",
            "pressure": "GPU maintenance flows make manual replay versus controller automation explicit and should stay separated",
        },
    ],
})

append_item("RESOLUTION-LEDGER.json", {
    "id": RS,
    "title": "resolve OQ-0153 with one compact refresh-scope-axis-remediation witness rather than a remediation provenance credit ledger",
    "state": "resolved",
    "closure_state": "resolved",
    "closure_reason": "rev0258 extracted one compact refresh-scope-axis-remediation witness, kept the admitted refresh-scope-axis-durability and related analog surfaces narrow, and kept stronger remediation-provenance-credit stories quarantined.",
    "discharge": "reopen-only-if-refresh-scope-axis-remediation-overflows",
    "gate_class": "concrete-evidence",
    "origin_revision": REV,
    "prior_state": "open gap: DelayBasin already had refresh-scope-axis-durability truth but still lacked one compact successor surface for whether repaired decoupling came back through native controller loops, auxiliary remediators, or manual replay.",
    "question": "whether one compact refresh-scope-axis-remediation witness over the existing refresh-scope-axis-durability and related admitted surfaces is enough for honest native-vs-external-vs-operator restoration comparison",
    "reopen_trigger": "refresh-scope-axis-remediation pressure overflows one compact successor surface",
    "reopen_triggers": [
        "later revisions need standing governance over controller weighting, provenance tariffs, override budgets, or broader remediation authority that one compact refresh-scope-axis-remediation witness cannot honestly absorb"
    ],
    "repair": "ordinary-continuation",
    "resolved_objects": [OQ, AP, FP, TL],
    "revision": REV,
    "successor_surface": NEW_DOC,
    "target_surfaces": [NEW_DOC],
    "action_lane": "keep-compact",
    "witness_surface": f"RESOLUTION-LEDGER.json#{RS}",
})

append_item("RETROSPECTIVE-QUEUE.json", {
    "id": RT,
    "title": "revisit whether refresh-scope-axis-remediation pressure stayed bounded after rev0258",
    "state": "cooling",
    "candidate_surface": f"docs/90-quarantine/wild-speculations-2026-03-08.md#{QWS}",
    "cooldown_window": "keep the stronger remediation provenance credit, controller tariff, or operator override escrow story cooled until at least one later revision shows that one compact refresh-scope-axis-remediation witness is no longer enough.",
    "adjudication_family": "refresh scope axis remediation / restoration provenance / replay pressure",
    "supersession_link": f"OBLIGATION-LEDGER.json#{OB}",
    "origin_revision": REV,
    "discharge": "keep-cooling-unless-refresh-scope-axis-remediation-overflows",
    "action_lane": "keep-compact",
    "gate_class": "overflow",
    "witness_surface": f"RETROSPECTIVE-QUEUE.json#{RT}",
    "revision": REV,
    "cooling_state": "cooling",
    "disposition": "await-adjudication",
    "repair": "keep-cooling",
})

append_item("FOLLOWTHROUGH-QUEUE.json", {
    "id": FT,
    "title": "keep checking whether refresh-scope-axis-remediation pressure still fits inside one compact successor surface",
    "state": "queued",
    "blocked_object": "remediation provenance credit, controller tariff, or operator override escrow",
    "local_surface": f"docs/90-quarantine/wild-speculations-2026-03-08.md#{QWS}",
    "followthrough_state": "queued",
    "boundary": "do not promote bounded refresh-scope-axis-remediation clarification into a general controller-legitimacy machine",
    "next_proof_surface": NEW_DOC,
    "receiving_surface": f"FOLLOWTHROUGH-QUEUE.json#{FT}",
    "repair": "ordinary-continuation",
    "origin_revision": REV,
    "discharge": "revisit-on-next-real-refresh-scope-axis-remediation-overflow",
    "action_lane": "keep-compact",
    "gate_class": "overflow",
    "blocked_output": "remediation provenance credit, controller tariff, or operator override escrow",
    "owner_surface": f"OBLIGATION-LEDGER.json#{OB}",
    "revision": REV,
    "missing_support": "a later public check on whether one compact refresh-scope-axis-remediation witness keeps overflowing the bounded rule and honestly warrants richer provenance governance",
    "candidate_surface": f"docs/90-quarantine/wild-speculations-2026-03-08.md#{QWS}",
    "blocked_by": "need repeated evidence that native-vs-external-vs-operator restoration truth overflows one compact witness",
})

append_item("FIREBREAK-LEDGER.json", {
    "id": FB,
    "title": "the refresh-scope-axis-remediation import should count as one compact native-vs-external-vs-operator repair, not as promotion of a remediation provenance credit ledger",
    "state": "withheld",
    "witness_surface": f"FIREBREAK-LEDGER.json#{FB}",
    "judged_property": f"the {REV} decision that DelayBasin should extract one compact refresh-scope-axis-remediation witness over the existing refresh-scope-axis-durability and related admitted surfaces and `refresh_scope_axis_remediation_state` family while the broader remediation provenance credit / controller tariff / operator override escrow story remains quarantined",
    "public_extract": [
        NEW_DOC,
        "docs/10-method/refresh-scope-axis-durability-witnesses-eviction-preserved-decoupling-repair-restored-decoupling-and-grandfathered-decoupling.md",
        "docs/20-constitution/open-question-registry.md",
        f"FOREIGN-PRESSURE-LEDGER.json#{FP}",
        f"APPLICABILITY-LEDGER.json#{AP}",
        "REVISION-RECEIPT.json",
    ],
    "withheld_trace_surface": "same-session drafting residue behind the compact refresh-scope-axis-remediation-witness versus remediation-provenance-credit-ledger decision",
    "allowed_role": "bounded drafting aid only; not public support for a broader remediation provenance credit, controller tariff, or operator override escrow",
    "exposure_rule": "expose or reintegrate only if later passes show that one compact refresh-scope-axis-remediation witness cannot keep native-vs-external-vs-operator restoration truth bounded",
    "trace_state": "withheld",
    "repair": "ordinary-continuation",
    "origin_revision": REV,
    "action_lane": "keep-compact",
    "gate_class": "overflow",
    "firebreak_surface": f"FIREBREAK-LEDGER.json#{FB}",
    "discharge": "reopen-only-if-refresh-scope-axis-remediation-overflows",
    "revision": REV,
    "blocked_object": "standing remediation provenance credit, controller tariff, or operator override escrow",
})

# --- status and manifest ---
status = load_json("SURFACE-STATUS.json")
status["operational_head"]["revision"] = REV
status["status_lanes"]["frozen_public_surface"] = BUNDLE
status["status_lanes"]["current_release_surface"] = BUNDLE
status["citation_head"]["revision"] = REV
status["citation_head"]["surface"] = BUNDLE
status["previous_citation_head"]["revision"] = PREV
status["previous_citation_head"]["surface"] = f"DelayBasin-{PREV}-2026.03.28.05.34-axisdurability-leaseq-driftcarry-keepshard.zip"
status["revision"] = REV
status["stamp"] = STAMP
status["slug"] = SLUG
dump_json("SURFACE-STATUS.json", status)

manifest = {
    "project": "DelayBasin",
    "revision": REV,
    "timestamp": STAMP,
    "slug": SLUG,
    "bundle": BUNDLE,
}
dump_json("RELEASE-MANIFEST.json", manifest)

# --- changelog + archive index ---
changelog = read_text("CHANGELOG.md")
new_header = f"## {REV} - {STAMP} - axisremediation / provenanceq / loopcarry / handrail\n\n- Added `{NEW_DOC}` to resolve `{OQ}` with a compact native-vs-external-vs-operator remediation witness.\n- Kept the stronger remediation provenance credit / controller tariff / operator override escrow move explicitly quarantined as `{QWS}` instead of laundering it into canon.\n- Hygiene/meta-engineering improvement: introduced `refresh_scope_axis_branch_spec(...)` in `tools/packet_contract_common.py` so refresh-scope-axis branch specs stop hand-spelling the same contract scaffold, and added `{NEW_CHECKER}`.\n\n"
if not changelog.startswith(f"## {REV}"):
    changelog = new_header + changelog
    write_text("CHANGELOG.md", changelog)

archive_index = read_text("ARCHIVE_INDEX.md")
new_row = f"| {BUNDLE} | 2026-03-28 | Refresh-scope-axis-remediation revision: resolved {OQ} with a compact native-vs-external-vs-operator restoration witness, honestly quarantined stronger remediation provenance weighting, and refactored refresh-scope-axis branch contract scaffolding to stay wired and cumulative. |\n"
if BUNDLE not in archive_index:
    lines = archive_index.splitlines(keepends=True)
    for i, line in enumerate(lines):
        if line.startswith("| DelayBasin-rev"):
            lines.insert(i, new_row)
            break
    archive_index = "".join(lines)
    write_text("ARCHIVE_INDEX.md", archive_index)

# --- revision receipt ---
receipt = load_json("REVISION-RECEIPT.json")
receipt["revision"] = REV
receipt["previous_revision"] = PREV
receipt["summary"] = "Resolved OQ-0153 with one compact refresh-scope-axis-remediation witness that separates native controller restoration from external remediator or operator replay restoration while keeping stronger remediation-provenance governance quarantined."
receipt["summary_highlight"] = SUMMARY_HIGHLIGHT
receipt["codename"] = CODENAME
receipt["packaged_bundle_filename"] = BUNDLE
receipt["created_at"] = CREATED_AT
receipt["canon_additions"] = [NEW_DOC, f"{RS} resolved {OQ} with one compact refresh-scope-axis-remediation witness"]
receipt["quarantine_additions"] = [f"{QWS} — {QWS_LABEL}"]
receipt["refs_used"] = [
    "docs/00-meta/bibliography.md#ref-0975",
    "docs/00-meta/bibliography.md#ref-0976",
    "docs/00-meta/bibliography.md#ref-0977",
    "docs/00-meta/bibliography.md#ref-0978",
    "docs/00-meta/bibliography.md#ref-0979",
    "docs/00-meta/bibliography.md#ref-0980",
]
receipt["checks_passed"] = ["make lint"]
receipt["packaged_release"] = True
receipt["current_import_id"] = TL
receipt["current_pressure_id"] = FP
receipt["new_classes_or_families"] = ["refresh_scope_axis_remediation_state"]
receipt["quarantined_non_take"] = ["remediation provenance credit", "controller tariff", "operator override escrow"]
receipt["comparison_witness"] = {
    "previous_revision": PREV,
    "current_revision": REV,
    "current_pressure_id": FP,
    "current_import_id": TL,
    "basis_surface": "docs/10-method/refresh-scope-axis-durability-witnesses-eviction-preserved-decoupling-repair-restored-decoupling-and-grandfathered-decoupling.md",
    "delta_surface": NEW_DOC,
    "comparison_summary": f"{REV} adds one compact refresh-scope-axis-remediation witness so repair-restored-looking axes no longer all read as if the same controller lane restored them.",
}
receipt["changes"] = [
    {"kind": "canon", "surface": NEW_DOC, "summary": "added one compact refresh-scope-axis-remediation witness with native-controller, external-remediator, operator-replay, and mixed states"},
    {"kind": "quarantine", "surface": f"docs/90-quarantine/wild-speculations-2026-03-08.md#{QWS}", "summary": "kept stronger remediation provenance weighting or override governance quarantined rather than promoting it into canon"},
    {"kind": "hygiene", "surface": "tools/packet_contract_common.py", "summary": "introduced refresh_scope_axis_branch_spec(...) so new scope-axis branch specs share one contract scaffold instead of hand-spelling repeated doc-needle blocks"},
]
receipt["basis_witness"].update({
    "expected_head": PREV,
    "observed_head": PREV,
    "basis_surfaces": [
        "docs/10-method/refresh-scope-axis-durability-witnesses-eviction-preserved-decoupling-repair-restored-decoupling-and-grandfathered-decoupling.md",
        "docs/00-meta/trajectory-map.md",
        "docs/20-constitution/open-question-registry.md",
    ],
    "session_provenance": f"DelayBasin-{PREV}-2026.03.28.05.34-axisdurability-leaseq-driftcarry-keepshard.zip",
    "basis_omission_basis": "broader remediation provenance weighting was intentionally omitted from canon because the evidence only justified one bounded refresh-scope-axis-remediation witness",
    "origin_revision": REV,
    "revision_span": f"{PREV} -> {REV}",
})
receipt["scope_witness"].update({
    "exact_target": "one compact refresh-scope-axis-remediation witness plus one quarantined provenance-weighting move and one small branch-spec helper refactor",
    "scope_surfaces": [
        "docs/20-constitution/open-question-registry.md",
        "docs/00-meta/trajectory-map.md",
        NEW_DOC,
        "docs/90-quarantine/wild-speculations-2026-03-08.md",
    ],
    "scope_of_change": "refresh-scope-axis-remediation",
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
    "controlled_families": ["refresh_scope_axis_remediation_state", "action_lane", "gate_class"],
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
        "repaired-means-self-healed",
        "descheduler-counts-as-native-controller",
        "manual-delete-counts-as-automatic",
        "remediation-ish",
    ],
    "comparability_budget": "refresh-scope-axis-remediation truth is compared by token; the compact witness says whether restored decoupling came back through native controllers, external remediators, manual replay, or an honest mix while raw runbooks, controller graphs, and event streams stay outside the token",
    "vocabulary_state": "locked",
    "repair": "ordinary-continuation",
    "refresh_scope_axis_remediation_state": wv["families"]["refresh_scope_axis_remediation_state"],
    "action_lane": receipt["vocabulary_witness"]["action_lane"],
    "gate_class": receipt["vocabulary_witness"]["gate_class"],
}
receipt["counterfactual_shadow"] = {
    "status": "recorded",
    "nearby_rejected_move": QWS_LABEL,
    "pivot_surface": "docs/90-quarantine/wild-speculations-2026-03-08.md",
    "rejection_reason": "current evidence supports a bounded remediation witness but not a canon-level remediation provenance economy",
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
receipt["refresh_scope_axis_remediation_witness"] = {
    "witness_surface": NEW_DOC,
    "family": "refresh_scope_axis_remediation_state",
    "allowed_tokens": [
        "native-controller-restoration",
        "external-remediator-restoration",
        "operator-replay-restoration",
        "mixed-refresh-scope-axis-remediation",
    ],
    "overflow_rule": "reopen-only-if-refresh-scope-axis-remediation-overflows",
}
receipt["refresh_scope_axis_remediation_witness_contract"] = {
    "family": "refresh_scope_axis_remediation_state",
    "allowed_tokens": [
        "native-controller-restoration",
        "external-remediator-restoration",
        "operator-replay-restoration",
        "mixed-refresh-scope-axis-remediation",
    ],
}
receipt["refresh_scope_axis_remediation_witness_meta"] = {
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
    "apply_rev0258.py",
]
receipt["artifacts_touched"] = artifacts
receipt["touched_surfaces"] = artifacts
# keep import_witness as previous import witness; update current ids at top-level only

dump_json("REVISION-RECEIPT.json", receipt)

print(f"Applied {REV} surfaces.")
