from __future__ import annotations
import json, pathlib, re, copy

ROOT = pathlib.Path(__file__).resolve().parent

REV = 'rev0263'
PREV = 'rev0262'
STAMP = '2026.03.28.10.45'
CREATED_AT = '2026-03-28T10:45:00-04:00'
SLUG = 'replayfidelity-cacheq-exactcarry-shadowglass'
BUNDLE = f'DelayBasin-{REV}-{STAMP}-{SLUG}.zip'
SUMMARY_HIGHLIGHT = 'exactcarry'
CODENAME = 'shadowglass'

NEW_DOC = 'docs/10-method/refresh-scope-axis-remediation-displacement-replay-fidelity-witnesses-exact-state-restore-bounded-loss-checkpoint-replay-and-source-only-restart.md'
NEW_CHECKER = 'tools/check_refresh_scope_axis_remediation_displacement_replay_fidelity_witness_contract.py'
NEW_FAMILY = 'refresh_scope_axis_remediation_displacement_replay_fidelity_state'

QWS = 'QWS-0241'
QWS_LABEL = 'functional exactness / performance shadow / cache-carry residue'
CL = 'CL-0156'
RS = 'RS-0165'
OQ = 'OQ-0158'
NEXT_OQ = 'OQ-0159'
PP = 'PP-0116'
AP = 'AP-0157'
OB = 'OB-0158'
AS = 'AS-0162'
FP = 'FP-0162'
TL = 'TL-0168'
FT = 'FT-0165'
RT = 'RT-0152'
FB = 'FB-0159'
REFS = ['REF-1006', 'REF-1007', 'REF-1008', 'REF-1009', 'REF-1010']

ALLOWED = [
    'exact-state-restore',
    'bounded-loss-checkpoint-replay',
    'source-only-restart',
    'mixed-refresh-scope-axis-remediation-displacement-replay-fidelity',
]
EXCLUDED = [
    'checkpoint-means-same-enough',
    'restored-means-no-loss',
    'latest-checkpoint-means-exact',
    'replay-fidelity-ish',
]

NEW_DOC_TEXT = """# Refresh-scope-axis-remediation-displacement-replay-fidelity witnesses, exact-state restore, bounded-loss checkpoint replay, and source-only restart

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
"""


def read(rel: str) -> str:
    return (ROOT / rel).read_text(encoding='utf-8')

def write(rel: str, text: str) -> None:
    (ROOT / rel).write_text(text, encoding='utf-8')

def loadj(rel: str):
    return json.loads(read(rel))

def dumpj(rel: str, obj) -> None:
    write(rel, json.dumps(obj, indent=2, ensure_ascii=False) + '\n')

def append_text(rel: str, addition: str) -> None:
    text = read(rel)
    if addition in text:
        return
    if not text.endswith('\n'):
        text += '\n'
    text += addition
    if not text.endswith('\n'):
        text += '\n'
    write(rel, text)

def insert_after(rel: str, needle: str, addition: str) -> None:
    text = read(rel)
    if addition in text:
        return
    if needle not in text:
        raise RuntimeError(f'needle not found in {rel}: {needle[:120]}')
    write(rel, text.replace(needle, needle + addition, 1))

def replace_once(rel: str, old: str, new: str) -> None:
    text = read(rel)
    if new in text:
        return
    if old not in text:
        raise RuntimeError(f'old block not found in {rel}')
    write(rel, text.replace(old, new, 1))

def append_item(rel: str, item: dict) -> None:
    obj = loadj(rel)
    items = obj['items']
    if any(existing['id'] == item['id'] for existing in items):
        return
    items.append(item)
    dumpj(rel, obj)

# new doc
write(NEW_DOC, NEW_DOC_TEXT + '\n')

# bibliography refs
bib_add = """
- `REF-1006` — Kubernetes Documentation, **Kubelet Checkpoint API** (accessed 2026-03-28)
  - URL: https://kubernetes.io/docs/reference/node/kubelet-checkpoint-api/
  - Load-bearing use: Kubernetes says a restored checkpointed container continues to run at exactly the same point it was checkpointed, which pressures DelayBasin to reserve an exact-state-restore lane rather than flattening every replay path into bounded-loss resume.

- `REF-1007` — CRIU Documentation, **ZDTM test suite** (accessed 2026-03-28)
  - URL: https://criu.org/ZDTM_test_suite
  - Load-bearing use: CRIU says its restore tests explicitly check that files remain open, memory remains mapped, and pipe contents remain intact after restore, which pressures DelayBasin to treat same-state preservation as a stronger replay-fidelity class than mere relaunch.

- `REF-1008` — NVIDIA Run:ai Documentation, **Best Practices: Checkpointing Preemptible Training Workloads** (accessed 2026-03-28)
  - URL: https://run-ai-docs.nvidia.com/self-hosted/2.22/workloads-in-nvidia-run-ai/using-training/checkpointing-preemptible-workloads
  - Load-bearing use: Run:ai says preempted workloads should periodically save checkpoints, resume from the latest checkpoint, may restart on a different node, and rerun the same startup script before loading checkpoints, which pressures DelayBasin to distinguish bounded-loss checkpoint replay from exact-state restore.

- `REF-1009` — Kubernetes Documentation, **Jobs** and **Pod Lifecycle** (accessed 2026-03-28)
  - URL: https://kubernetes.io/docs/concepts/workloads/controllers/job/ ; https://kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/
  - Load-bearing use: Kubernetes says suspending a Job deletes active Pods until resume and that Pods are ephemeral one-shot scheduled objects whose replacements are new Pods, which pressures DelayBasin to keep source-only restart distinct from replay-backed return when no saved-state basis is public.

- `REF-1010` — NVIDIA Documentation, **CUPTI Checkpoint API Usage** (accessed 2026-03-28)
  - URL: https://docs.nvidia.com/cupti/main/main.html
  - Load-bearing use: NVIDIA says CUPTI checkpoint restore can restore functional device state but not performance-critical state such as caches and does not restore host state, which pressures DelayBasin to quarantine stronger performance-equivalence stories rather than smuggling them into replay-fidelity canon.
""".lstrip('\n')
append_text('docs/00-meta/bibliography.md', '\n' + bib_add)

# docs README
append_text('docs/README.md', f'- [`10-method/{pathlib.Path(NEW_DOC).name}`](10-method/{pathlib.Path(NEW_DOC).name})\n')

# claim registry
claim_add = f"""

- `{CL}` — Archive continuity may improve when DelayBasin preserves one compact **refresh-scope-axis-remediation-displacement-replay-fidelity witness / exactness card / replay-loss brake** whenever a current continuity claim depends not only on whether corroborating axes are genuinely independent, materially backed, decoupled under perturbation, hard-enforced, durable, explicitly restored, honest about collateral width, honest about whether restored placement reused free capacity or displaced unrelated lower-priority work, honest about whether the displaced work retained a live path back, and honest about whether the return was in-memory, checkpoint-backed, or cold, but on how much execution state actually survived inside the replay path: name the **governed row or surface**, the **stake object / line of concern**, the **prior refresh-scope-axis-remediation-displacement-resumption-basis evidence**, the **current corroborating axes**, the **exact-state-restore basis if any**, the **bounded-loss checkpoint basis if any**, the **source-only restart basis if any**, the **{NEW_FAMILY}**, and the **fail-closed repair** rather than letting every saved-state return silently inherit the authority of exact restore.
  - Status: speculative but central
  - Wired docs: `{NEW_DOC}`, `docs/20-constitution/open-question-registry.md`, `docs/20-constitution/prompt-pair-registry.md`, `docs/50-promptcraft/prompt-pairs.md`, `docs/00-meta/llm-runbook.md`, `WITNESS-VOCABULARY.json`, `REVISION-RECEIPT.json`
"""
append_text('docs/20-constitution/claim-registry.md', claim_add)

# prompt pair registry
pp_reg_add = f"""
- `{PP}` — Name whether checkpoint-backed return restored exact state, only the latest durable boundary, or just restarted from source
  - Goal: keep checkpoint-backed return from silently inheriting exact-restore authority by requiring explicit prior remediation-displacement-resumption-basis evidence, current corroborating axes, exact-state basis, bounded-loss checkpoint basis, source-only restart basis, `{NEW_FAMILY}`, and fail-closed repair before later passes call the replay path equally faithful.
  - Canonical text: `docs/50-promptcraft/prompt-pairs.md#{PP.lower()}--name-whether-checkpoint-backed-return-restored-exact-state-only-the-latest-durable-boundary-or-just-restarted-from-source`
"""
append_text('docs/20-constitution/prompt-pair-registry.md', '\n' + pp_reg_add)

# prompt pairs
pp_add = f"""
## {PP} — Name whether checkpoint-backed return restored exact state, only the latest durable boundary, or just restarted from source

**Opening prompt**

```text
Read the latest DelayBasin archive and inspect whether the current revision should also materialize one compact refresh-scope-axis-remediation-displacement-replay-fidelity witness for honest exact-vs-bounded-loss-vs-source-only return.

Focus only on cases where the corroborating axes already look genuinely independent, materially backed, decoupled under perturbation, hard-enforced, durable, explicit about who restored the decoupling, honest about how wide the remediation was, honest about whether restored placement reused free capacity or only came back by displacing unrelated lower-priority work, honest about whether the displaced lower-priority work stayed nonterminal, and honest about whether the return was in-memory, checkpoint-backed, or cold. The missing question is how much execution state actually survived inside the replay path.

If yes, preserve exactly one small witness that:
- names the governed row or surface,
- names the stake object / line of concern,
- names the prior refresh-scope-axis-remediation-displacement-resumption-basis evidence,
- names the current corroborating axes,
- names the exact-state-restore basis if any,
- names the bounded-loss checkpoint basis if any,
- names the source-only restart basis if any,
- names the `{NEW_FAMILY}` / whether this is exact-state-restore, bounded-loss-checkpoint-replay, source-only-restart, or mixed-refresh-scope-axis-remediation-displacement-replay-fidelity,
- states what stronger surfaces still outrank the witness,
- and states the fail-closed repair / keep-current vs narrow-claim vs split-scope vs issue-new-refresh-scope-axis-remediation-displacement-replay-fidelity-witness vs quarantine-performance-shadow consequence if the present continuity claim is not actually supported by the claimed replay-fidelity lane.

Do not use refresh-scope-axis-remediation-displacement-replay-fidelity as a standing performance-equivalence board or warm-cache market. Use this prompt pair only where axis independence, materiality, coupling, enforcement, durability, remediation provenance, remediation collateral, remediation capacity source, remediation displacement aftercare, and remediation displacement resumption basis are already established and the missing question is whether the returning work restored exact saved state, only the latest durable checkpoint boundary, or merely restarted from source.
```

**Continuation prompt**

```text
Continue the refresh-scope-axis-remediation-displacement-replay-fidelity pass with one high-leverage replay-loss clarification only. Prefer the smallest witness that says what governed row is still being justified, what stake object is supposedly widened, what prior refresh-scope-axis-remediation-displacement-resumption-basis evidence exists, what current corroborating axes exist, what exact-state-restore basis if any now exists, what bounded-loss checkpoint basis if any now exists, what source-only restart basis if any now exists, what `{NEW_FAMILY}` is honest, what stronger surfaces still outrank the witness, and what keep-current, narrow-claim, split-scope, issue-new-refresh-scope-axis-remediation-displacement-replay-fidelity-witness, quarantine, or recover-resync consequence follows if the present replay lane is exact-state-restore, bounded-loss-checkpoint-replay, source-only-restart, or mixed-refresh-scope-axis-remediation-displacement-replay-fidelity. Run `make lint` and package the release.
```

Use `{NEW_DOC}` when the live question is how faithful a checkpoint-backed or replacement-based return really was.
"""
append_text('docs/50-promptcraft/prompt-pairs.md', '\n' + pp_add)
append_text('docs/00-meta/llm-runbook.md', f'Use `{NEW_DOC}` when the live question is whether a supposedly checkpoint-backed return really restored exact saved state, only the latest durable boundary, or merely restarted from source.\n')

# open question registry and trajectory map
old_oq_block = """- `OQ-0158` — what remediation-displacement-replay-fidelity witness distinguishes exact-state restore from bounded-loss checkpoint replay and source-only restart?
  - Why it matters: if DelayBasin cannot separate exact restore from truncated replay and source-only restart, later sessions may still over-credit checkpoint-backed return that discards meaningful progress.
  - Current posture: unresolved
"""
new_oq_block = f"""- `{OQ}` — what remediation-displacement-replay-fidelity witness distinguishes exact-state restore from bounded-loss checkpoint replay and source-only restart?
  - Why it matters: if DelayBasin cannot separate exact restore from truncated replay and source-only restart, later sessions may still over-credit checkpoint-backed return that discards meaningful progress.
  - Current posture: resolved by `{RS}` via `{NEW_DOC}`; reopen only if the compact refresh-scope-axis-remediation-displacement-replay-fidelity witness proves insufficient and stronger replay-equivalence or performance-shadow governance is honestly required

- `{NEXT_OQ}` — what remediation-displacement-replay-equivalence witness distinguishes functionally exact restore from performance-shadow restore?
  - Why it matters: if DelayBasin cannot separate functional exactness from performance-shadow restore, later sessions may narrate full continuity from returns that preserve correctness while losing meaningful warmth, cache state, or host/device parity.
  - Current posture: unresolved
"""
replace_once('docs/20-constitution/open-question-registry.md', old_oq_block, new_oq_block)

traj_old = """114. Determine what remediation-displacement-replay-fidelity witness distinguishes exact-state restore from bounded-loss checkpoint replay and source-only restart.

A fresh extension is that once resumption basis is explicit, DelayBasin may next need to say how much meaningful execution state actually survived inside the replay path. Otherwise checkpoint-backed return may still silently inherit the authority of exact restore.
- `OQ-0158` — what remediation-displacement-replay-fidelity witness distinguishes exact-state restore from bounded-loss checkpoint replay and source-only restart?
  - Why it matters: if DelayBasin cannot separate exact restore from truncated replay and source-only restart, later sessions may still over-credit checkpoint-backed return that discards meaningful progress.
  - Current posture: unresolved
"""
traj_new = f"""114. Determine what remediation-displacement-replay-fidelity witness distinguishes exact-state restore from bounded-loss checkpoint replay and source-only restart.

A fresh extension is that once resumption basis is explicit, DelayBasin may next need to say how much meaningful execution state actually survived inside the replay path. Otherwise checkpoint-backed return may still silently inherit the authority of exact restore.
- `{OQ}` — what remediation-displacement-replay-fidelity witness distinguishes exact-state restore from bounded-loss checkpoint replay and source-only restart?
  - Why it matters: if DelayBasin cannot separate exact restore from truncated replay and source-only restart, later sessions may still over-credit checkpoint-backed return that discards meaningful progress.
  - Current posture: resolved by `{RS}` via `{NEW_DOC}`; reopen only if the compact refresh-scope-axis-remediation-displacement-replay-fidelity witness proves insufficient and stronger replay-equivalence or performance-shadow governance is honestly required

115. Determine what remediation-displacement-replay-equivalence witness distinguishes functionally exact restore from performance-shadow restore.

A fresh extension is that once replay fidelity is explicit, DelayBasin may next need to say whether an apparently exact restore is only functionally exact or also performance-equivalent. Otherwise a same-state return may silently inherit the authority of cache-warm, host/device-complete, or locality-preserving restore.
- `{NEXT_OQ}` — what remediation-displacement-replay-equivalence witness distinguishes functionally exact restore from performance-shadow restore?
  - Why it matters: if DelayBasin cannot separate functional exactness from performance-shadow restore, later sessions may narrate full continuity from returns that preserve correctness while losing meaningful warmth, cache state, or host/device parity.
  - Current posture: unresolved
"""
replace_once('docs/00-meta/trajectory-map.md', traj_old, traj_new)

# quarantine
qws_add = f"""
## {QWS} — Some continuations may eventually need a functional exactness / performance shadow / cache-carry residue court rather than only a compact refresh-scope-axis-remediation-displacement-replay-fidelity witness

### Claim
Some later continuations may need stronger public machinery for whether an apparently exact restore preserved only correctness or also preserved the practical warmth and host/device parity that made the original run fast. One compact exact-vs-bounded-loss-vs-source-only witness may eventually stop being enough.

### What follows if true
- DelayBasin may eventually need an explicit way to distinguish functionally exact restore from performance-shadow restore when caches, occupancy, locality, or host-side state materially change the continuity bill.
- The archive might need a bounded functional-exactness or cache-carry residue layer if later revisions repeatedly compare several exact-looking restores whose practical runtime continuity differs.

### What would count against it
- Several later revisions keep fitting cleanly inside one compact refresh-scope-axis-remediation-displacement-replay-fidelity witness without repeated confusion about cache warmth, host/device asymmetry, or performance-equivalence.
- The archive almost never needs public reasoning about performance shadow once exact-state restore, bounded-loss replay, and source-only restart are already separated.

### Why it stays quarantined
The current evidence justifies one bounded witness for exact-state restore versus bounded-loss checkpoint replay versus source-only restart. It does not yet justify a standing functional-exactness court, performance-shadow ledger, or cache-carry residue market.
"""
append_text('docs/90-quarantine/wild-speculations-2026-03-08.md', '\n' + qws_add)

# witness vocabulary
wv = loadj('WITNESS-VOCABULARY.json')
families = wv['families']
families[NEW_FAMILY] = {
    'allowed': ALLOWED,
    'surfaces': ['WITNESS-VOCABULARY.json', 'REVISION-RECEIPT.json', NEW_DOC],
    'excluded_synonyms': EXCLUDED,
    'comparability_budget': 'refresh-scope-axis-remediation-displacement-replay-fidelity truth is compared by token; the compact witness says whether displaced work returned through exact-state restore, bounded-loss checkpoint replay, source-only restart, or an honest mix while raw cache traces, host/device asymmetry, restart timing, and scheduler traces stay in surrounding prose',
}
dumpj('WITNESS-VOCABULARY.json', wv)

# frontier ticket hygiene refactor
frontier_lib = ROOT / 'tools/frontier_ticket_lib.py'
frontier_lib.write_text("""import json\nimport pathlib\n\nROOT = pathlib.Path(__file__).resolve().parents[1]\n\n\ndef load_json(rel: str):\n    return json.loads((ROOT / rel).read_text(encoding=\"utf-8\"))\n\n\ndef latest_open_obligation(items):\n    return next((item for item in reversed(items) if item.get(\"state\") == \"open\" or item.get(\"obligation_state\") == \"open\"), None)\n\n\ndef latest_cooling_retrospective(items):\n    return next((item for item in reversed(items) if item.get(\"state\") == \"cooling\"), None)\n""", encoding='utf-8')
write('tools/gen_frontier_ticket.py', """import json\nimport pathlib\n\nfrom frontier_ticket_lib import load_json, latest_cooling_retrospective, latest_open_obligation\n\nROOT = pathlib.Path(__file__).resolve().parents[1]\nout = ROOT / \"frontier-ticket.json\"\n\ncontext = load_json(\"context-pack.json\")\nstatus = load_json(\"SURFACE-STATUS.json\")\nobligations = load_json(\"OBLIGATION-LEDGER.json\")[\"items\"]\nretros = load_json(\"RETROSPECTIVE-QUEUE.json\")[\"items\"]\n\nfocus = context[\"open_questions\"][-1]\nlatest_open_ob = latest_open_obligation(obligations)\nlatest_cooling_rt = latest_cooling_retrospective(retros)\nif latest_open_ob is None:\n    raise SystemExit(\"no open obligation row found\")\nif latest_cooling_rt is None:\n    raise SystemExit(\"no cooling retrospective row found\")\n\nstatus_lanes = status[\"status_lanes\"]\npack = {\n    \"project\": \"DelayBasin\",\n    \"revision\": context[\"revision\"],\n    \"derivative_note\": \"Derivative frontier aid; canon wins.\",\n    \"selection_policy\": {\n        \"primary_focus_rule\": \"select the last source-backed unresolved hot open question already projected into context-pack.json\",\n        \"background_rule\": \"carry the latest open obligation and latest cooling retrospective as compact continuity checks\",\n        \"source_surfaces\": [\n            \"context-pack.json\",\n            \"docs/20-constitution/open-question-registry.md\",\n            \"docs/00-meta/trajectory-map.md\",\n            \"OBLIGATION-LEDGER.json\",\n            \"RETROSPECTIVE-QUEUE.json\",\n        ],\n    },\n    \"current_posture\": {\n        \"operational_head\": status[\"operational_head\"][\"surface\"],\n        \"citation_head\": status[\"citation_head\"][\"surface\"],\n        \"decision_state\": status_lanes[\"decision_state\"],\n        \"execution_state\": status_lanes[\"execution_state\"],\n        \"public_state\": status_lanes[\"public_state\"],\n        \"state_class\": status[\"state_class\"],\n    },\n    \"primary_focus\": {\n        \"id\": focus[\"id\"],\n        \"source\": focus[\"source\"],\n        \"selection_source\": focus[\"selection_source\"],\n        \"text\": focus[\"text\"],\n        \"governing_surface\": f\"{focus['source']}#{focus['id'].lower()}\",\n    },\n    \"background_checks\": {\n        \"latest_obligation\": {\n            \"id\": latest_open_ob[\"id\"],\n            \"surface\": f\"OBLIGATION-LEDGER.json#{latest_open_ob['id']}\",\n            \"title\": latest_open_ob[\"title\"],\n            \"discharge\": latest_open_ob[\"discharge\"],\n        },\n        \"latest_retrospective\": {\n            \"id\": latest_cooling_rt[\"id\"],\n            \"surface\": f\"RETROSPECTIVE-QUEUE.json#{latest_cooling_rt['id']}\",\n            \"title\": latest_cooling_rt[\"title\"],\n            \"discharge\": latest_cooling_rt[\"discharge\"],\n        },\n    },\n    \"reentry_anchors\": {\n        \"startup_surface\": \"START_HERE.md\",\n        \"wrapper_surface\": \"AGENTS.md\",\n        \"runbook_surface\": \"docs/00-meta/llm-runbook.md\",\n        \"compact_packet\": \"context-pack.json\",\n        \"status_surface\": \"SURFACE-STATUS.json\",\n    },\n}\nout.write_text(json.dumps(pack, ensure_ascii=False, separators=(\",\", \":\")) + \"\\n\", encoding=\"utf-8\")\nprint(f\"wrote {out}\")\n""")
write('tools/check_frontier_ticket_contract.py', """import pathlib\n\nfrom frontier_ticket_lib import load_json, latest_cooling_retrospective, latest_open_obligation\n\nROOT = pathlib.Path(__file__).resolve().parents[1]\npack = load_json(\"frontier-ticket.json\")\ncontext = load_json(\"context-pack.json\")\nstatus = load_json(\"SURFACE-STATUS.json\")\nobligations = load_json(\"OBLIGATION-LEDGER.json\")[\"items\"]\nretros = load_json(\"RETROSPECTIVE-QUEUE.json\")[\"items\"]\n\nrequired = {\"project\", \"revision\", \"derivative_note\", \"selection_policy\", \"current_posture\", \"primary_focus\", \"background_checks\", \"reentry_anchors\"}\nmissing = required - set(pack)\nif missing:\n    raise SystemExit(f\"frontier-ticket missing keys: {sorted(missing)}\")\nif pack[\"project\"] != \"DelayBasin\":\n    raise SystemExit(\"frontier-ticket project mismatch\")\nif pack[\"revision\"] != context[\"revision\"]:\n    raise SystemExit(\"frontier-ticket revision must match context-pack\")\nif pack[\"derivative_note\"] != \"Derivative frontier aid; canon wins.\":\n    raise SystemExit(\"frontier-ticket derivative_note drift\")\n\nsp = pack[\"selection_policy\"]\nfor key in [\"primary_focus_rule\", \"background_rule\", \"source_surfaces\"]:\n    if key not in sp:\n        raise SystemExit(f\"frontier-ticket selection_policy missing {key}\")\nfor rel in sp[\"source_surfaces\"]:\n    if not (ROOT / rel).exists():\n        raise SystemExit(f\"frontier-ticket selection_policy source missing: {rel}\")\n\ncp = pack[\"current_posture\"]\nctx_cp = context[\"current_posture\"]\nfor key in [\"operational_head\", \"citation_head\", \"decision_state\", \"execution_state\", \"public_state\", \"state_class\"]:\n    if cp.get(key) != ctx_cp.get(key):\n        raise SystemExit(f\"frontier-ticket current_posture mismatch on {key}\")\n\npf = pack[\"primary_focus\"]\nctx_focus = context[\"open_questions\"][-1]\nfor key in [\"id\", \"source\", \"selection_source\", \"text\"]:\n    if pf.get(key) != ctx_focus.get(key):\n        raise SystemExit(f\"frontier-ticket primary_focus mismatch on {key}\")\nexpected_gov = f\"{ctx_focus['source']}#{ctx_focus['id'].lower()}\"\nif pf.get(\"governing_surface\") != expected_gov:\n    raise SystemExit(\"frontier-ticket governing_surface mismatch\")\nif not (ROOT / pf[\"source\"]).exists() or not (ROOT / pf[\"selection_source\"]).exists():\n    raise SystemExit(\"frontier-ticket primary_focus surfaces missing\")\n\nlatest_open_ob = latest_open_obligation(obligations)\nlatest_cooling_rt = latest_cooling_retrospective(retros)\nif latest_open_ob is None or latest_cooling_rt is None:\n    raise SystemExit(\"frontier-ticket background rows unavailable\")\nbackground = pack[\"background_checks\"]\nob = background.get(\"latest_obligation\")\nrt = background.get(\"latest_retrospective\")\nif ob.get(\"id\") != latest_open_ob[\"id\"]:\n    raise SystemExit(\"frontier-ticket latest obligation mismatch\")\nif rt.get(\"id\") != latest_cooling_rt[\"id\"]:\n    raise SystemExit(\"frontier-ticket latest retrospective mismatch\")\n\nanchors = pack[\"reentry_anchors\"]\nfor key in [\"startup_surface\", \"wrapper_surface\", \"runbook_surface\", \"compact_packet\", \"status_surface\"]:\n    if key not in anchors:\n        raise SystemExit(f\"frontier-ticket reentry_anchors missing {key}\")\n    if not (ROOT / anchors[key]).exists():\n        raise SystemExit(f\"frontier-ticket anchor missing: {anchors[key]}\")\nif anchors[\"compact_packet\"] != \"context-pack.json\" or anchors[\"status_surface\"] != \"SURFACE-STATUS.json\":\n    raise SystemExit(\"frontier-ticket anchor drift\")\n\nprint(\"check_frontier_ticket_contract: OK\")\n""")

# checker
write(NEW_CHECKER, 'from packet_contract_common import require_named_refresh_scope_axis_branch_witness_packet_and_vocabulary\n\nrequire_named_refresh_scope_axis_branch_witness_packet_and_vocabulary("refresh_scope_axis_remediation_displacement_replay_fidelity_witness_contract")\n\nprint("check_refresh_scope_axis_remediation_displacement_replay_fidelity_witness_contract: OK")\n')

# packet contract common block insert
block = f'''
\n"refresh_scope_axis_remediation_displacement_replay_fidelity_witness_contract": refresh_scope_axis_branch_spec(
    doc_path="{NEW_DOC}",
    title="Refresh-scope-axis-remediation-displacement-replay-fidelity witnesses, exact-state restore, bounded-loss checkpoint replay, and source-only restart",
    oq_id="{OQ}",
    external_pressure_heading="## External pressure from Kubernetes stateful container checkpoint/restore, CRIU restore-preservation tests, NVIDIA Run:ai latest-checkpoint resume, Kubernetes Job Pod replacement, and NVIDIA CUPTI functional-only restore limits",
    comparison_heading="## Exact-state restore vs bounded-loss checkpoint replay vs source-only restart vs mixed refresh scope axis remediation displacement replay fidelity",
    runbook_ref="{pathlib.Path(NEW_DOC).name}",
    prompt_id="{PP}",
    prompt_needles=["Use `{NEW_DOC}`", "exact-state-restore, bounded-loss-checkpoint-replay, source-only-restart, or mixed-refresh-scope-axis-remediation-displacement-replay-fidelity"],
    claim_id="{CL}",
    resolution_id="{RS}",
    trajectory_oq_id="{NEXT_OQ}",
    qws_id="{QWS}",
    qws_label="{QWS_LABEL}",
    changelog_needles=["{pathlib.Path(NEW_DOC).name}", "{pathlib.Path(NEW_CHECKER).name}"],
    family="{NEW_FAMILY}",
    allowed={ALLOWED!r},
    excluded={EXCLUDED!r},
),
'''
needle = '"refresh_scope_axis_coupling_witness_contract": refresh_scope_axis_branch_spec('
insert_after('tools/packet_contract_common.py', '),\n"refresh_scope_axis_coupling_witness_contract": refresh_scope_axis_branch_spec(', block[1:])

# ledgers and queues
append_item('FOLLOWTHROUGH-QUEUE.json', {
    'id': FT,
    'title': 'carry the stronger functionally exact versus performance-shadow replay-equivalence question forward only as successor work after resolving exact-versus-bounded-loss replay fidelity',
    'state': 'local',
    'blocked_object': NEXT_OQ,
    'local_surface': NEW_DOC,
    'followthrough_state': 'local',
    'boundary': 'one compact replay-fidelity witness only; performance-shadow governance remains successor work',
    'next_proof_surface': 'docs/20-constitution/open-question-registry.md',
    'receiving_surface': f'docs/20-constitution/open-question-registry.md#{NEXT_OQ.lower()}',
    'repair': 'ordinary-continuation',
    'origin_revision': REV,
    'revision': REV,
    'action_lane': 'keep-compact',
    'gate_class': 'concrete-evidence',
    'witness_surface': f'FOLLOWTHROUGH-QUEUE.json#{FT}',
    'discharge': 'reopen-only-if-replay-fidelity-overflows',
})
append_item('APPLICABILITY-LEDGER.json', {
    'id': AP,
    'title': 'one compact refresh-scope-axis-remediation-displacement-replay-fidelity witness is enough when the live question is exact restore versus latest-boundary replay versus source-only restart',
    'state': 'admitted',
    'target_objective': 'keep checkpoint-backed return from silently inheriting exact-restore authority',
    'carry_object': 'one compact refresh-scope-axis-remediation-displacement-replay-fidelity witness over the already-admitted aftercare and resumption-basis surfaces',
    'applicability_conditions': [
        'the current claim already depends on axis independence, materiality, coupling, enforcement, durability, remediation provenance, remediation collateral, remediation capacity source, remediation displacement aftercare, and remediation displacement resumption basis truth',
        'the missing ambiguity is whether the replay path restored exact saved state, only the latest durable checkpoint boundary, or merely restarted from source',
        'one bounded witness still keeps replay-loss truth honest without standing performance-equivalence machinery'],
    'non_fit_slice': 'cases whose real missing question is performance-shadow restore, cache warmth, host/device asymmetry, or restart-credit accounting rather than exact-versus-bounded-loss-versus-source-only replay fidelity',
    'budget': 'one compact replay-fidelity witness plus one resolution of OQ-0158; no performance-shadow court',
    'negative_transfer_budget': 'if a later pass needs public accounting for cache warmth, host/device parity, or performance-equivalent restore, do not overload this witness; reopen successor work instead',
    'applicability_state': 'admitted',
    'repair': 'ordinary-continuation',
    'origin_revision': REV,
    'revision': REV,
    'witness_surface': f'APPLICABILITY-LEDGER.json#{AP}',
    'action_lane': 'keep-compact',
    'gate_class': 'concrete-evidence',
    'baselines': [
        'prior refresh-scope-axis-remediation-displacement-resumption-basis witness already names whether the return was in-memory, checkpoint-backed, or cold',
        'the archive still lacks one compact public successor surface for how faithful the replay path actually was'],
})
append_item('ASSUMPTION-LEDGER.json', {
  'id': AS,
  'title': 'one compact refresh-scope-axis-remediation-displacement-replay-fidelity witness is enough for now',
  'state': 'active',
  'scope': 'continuity passes whose current public claim depends on how much execution state actually survived inside a replay or restart path after displacement',
  'invalidation_triggers': [
    'repeated later revisions need standing governance over functional-exact versus performance-shadow restore rather than one compact replay-fidelity witness',
    'the archive needs separate public rules just to distinguish optimizer, dataloader, host-side, or device-side loss boundaries inside replay',
    'replay-fidelity cases repeatedly fail to stay distinguishable even with the witness in place'],
  'assumption_state': 'active',
  'repair': 'ordinary-continuation',
  'origin_revision': REV,
  'revision': REV,
  'assumption': 'One compact refresh-scope-axis-remediation-displacement-replay-fidelity witness is enough for now.',
  'supporting_surfaces': [NEW_DOC, f'docs/90-quarantine/wild-speculations-2026-03-08.md#{QWS}', f'APPLICABILITY-LEDGER.json#{AP}', f'FOREIGN-PRESSURE-LEDGER.json#{FP}'],
  'discharge': 'retire-or-promote-if-refresh-scope-axis-remediation-displacement-replay-fidelity-overflows',
  'witness_surface': f'ASSUMPTION-LEDGER.json#{AS}',
  'action_lane': 'keep-compact',
  'gate_class': 'concrete-evidence'
})
append_item('OBLIGATION-LEDGER.json', {
  'id': OB,
  'title': 'when checkpoint-backed return keeps needing exact-vs-bounded-loss-vs-source-only separation, DelayBasin should preserve one compact refresh-scope-axis-remediation-displacement-replay-fidelity witness rather than a performance-shadow court',
  'state': 'open',
  'witness_surface': f'OBLIGATION-LEDGER.json#{OB}',
  'target_surfaces': [NEW_DOC, f'docs/90-quarantine/wild-speculations-2026-03-08.md#{QWS}'],
  'missing_support': 'need repeated evidence that one compact replay-fidelity witness no longer keeps return exactness honest',
  'current_support': [NEW_DOC, f'APPLICABILITY-LEDGER.json#{AP}', f'FOREIGN-PRESSURE-LEDGER.json#{FP}'],
  'discharge_path': 'either show later that one compact refresh-scope-axis-remediation-displacement-replay-fidelity witness keeps sufficing or promote stronger replay-equivalence governance explicitly',
  'obligation_state': 'open',
  'repair': 'ordinary-continuation',
  'origin_revision': REV,
  'discharge': 'reopen-only-if-refresh-scope-axis-remediation-displacement-replay-fidelity-overflows',
  'revision': REV,
  'owner_surface': f'OBLIGATION-LEDGER.json#{OB}',
  'action_lane': 'keep-compact',
  'gate_class': 'overflow'
})
append_item('FOREIGN-PRESSURE-LEDGER.json', {
  'id': FP,
  'title': 'Kubernetes, CRIU, Run:ai, and CUPTI all force replay-fidelity truth once return basis is already explicit',
  'state': 'imported',
  'pressure_summary': 'Official checkpoint/restore and GPU runtime docs separate exact saved-state restore from latest-checkpoint replay, source-only restart, and stronger performance-shadow concerns, so DelayBasin should keep replay fidelity explicit once return basis is already in play.',
  'sources': REFS,
  'why_now': 'rev0262 made return-basis truth explicit, and the next honest ambiguity is how much execution state actually survived inside the replay path.',
  'imported_pressure': 'Keep exact-state restore distinct from bounded-loss checkpoint replay and source-only restart while quarantining stronger performance-shadow governance.',
  'quarantined_non_take': [QWS_LABEL],
  'pressure_state': 'adopted',
  'repair': 'ordinary-continuation',
  'origin_revision': REV,
  'revision': REV,
  'witness_surface': f'FOREIGN-PRESSURE-LEDGER.json#{FP}',
  'action_lane': 'keep-compact',
  'gate_class': 'concrete-evidence',
  'discharge': 'retain-unless-a-later-revision-needs-stronger-replay-equivalence-accounting',
  'assimilation_state': 'imported',
  'source_packets': [
    {'datacube':'kubernetes-checkpoint-exactness','surfaces':['Kubelet Checkpoint API'],'pressure':'documents restored containers continuing at exactly the same checkpointed point, so exact-state restore should remain a distinct replay-fidelity lane.'},
    {'datacube':'criu-restore-preservation','surfaces':['ZDTM test suite'],'pressure':'documents concrete state preservation across restore, so same-state replay should not be flattened into successful relaunch.'},
    {'datacube':'runai-latest-checkpoint-resume','surfaces':['Best Practices: Checkpointing Preemptible Training Workloads'],'pressure':'documents periodic checkpoint saving, startup-script rerun, and resume from latest checkpoint, so bounded-loss replay should stay distinct from exact restore.'},
    {'datacube':'kubernetes-source-restart','surfaces':['Jobs','Pod Lifecycle'],'pressure':'documents pod deletion and replacement without same-object continuation, so source-only restart should stay explicit when no restore basis is public.'},
    {'datacube':'cupti-functional-vs-performance-state','surfaces':['CUPTI Checkpoint API'],'pressure':'documents functional device-state restore but not performance-critical state or host state, so stronger performance-shadow governance should remain quarantined.'}
  ],
  'local_gap': 'rev0262 made return-basis truth explicit, but the archive still lacked one compact successor surface for how faithful a replay path actually was.',
  'bounded_take': 'Keep exact-state restore distinct from bounded-loss checkpoint replay and source-only restart once return basis is already explicit.',
  'explicit_non_take': ['no performance-shadow court','no cache-carry residue ledger','no functional-exactness market']
})
append_item('DATACUBE-TRANSFER-LEDGER.json', {
  'id': TL,
  'title': 'refresh-scope-axis-remediation-displacement-replay-fidelity evidence supports resolving OQ-0158 with one compact exact-vs-bounded-loss-vs-source-only card rather than a performance-shadow court',
  'state': 'supporting-only',
  'reviewed_pattern': 'exact-state restore vs bounded-loss checkpoint replay vs source-only restart across already-nonterminal return paths',
  'import_decision': 'support a compact refresh-scope-axis-remediation-displacement-replay-fidelity witness and resolve OQ-0158',
  'adopted_take': 'DelayBasin should add one compact witness that says whether displaced work returned through exact-state restore, bounded-loss checkpoint replay, source-only restart, or an honest mix',
  'supporting_only_take': 'the current evidence cleanly supports a bounded refresh-scope-axis-remediation-displacement-replay-fidelity witness without promoting broader performance-equivalence governance',
  'deferred_or_rejected_take': [QWS_LABEL],
  'local_gap': 'the archive still lacked one compact successor surface for how faithful an already checkpoint-backed or replacement-based return really was',
  'anchor_surfaces': ['docs/10-method/refresh-scope-axis-remediation-displacement-resumption-basis-witnesses-in-memory-continuation-checkpoint-backed-replay-and-cold-restart.md','docs/20-constitution/open-question-registry.md','docs/00-meta/trajectory-map.md',f'docs/90-quarantine/wild-speculations-2026-03-08.md#{QWS}'],
  'open_question': NEXT_OQ,
  'repair': 'ordinary-continuation',
  'origin_revision': REV,
  'action_lane': 'keep-compact',
  'gate_class': 'concrete-evidence',
  'discharge': 'reopen-only-if-refresh-scope-axis-remediation-displacement-replay-fidelity-overflows',
  'revision': REV,
  'witness_surface': f'DATACUBE-TRANSFER-LEDGER.json#{TL}',
  'transfer_state': 'supporting-only',
  'bounded_take': 'Keep the archive compact by extracting one refresh-scope-axis-remediation-displacement-replay-fidelity witness over the existing resumption-basis and related admitted surfaces; do not promote a performance-shadow court, cache-carry residue ledger, or functional-exactness market.',
  'explicit_non_take': ['no performance-shadow court','no cache-carry residue ledger','no functional-exactness market'],
  'open_transfer_question': 'whether later passes should add a separate replay-equivalence witness once replay fidelity is explicit',
  'missing_support': 'a later public check on whether one compact refresh-scope-axis-remediation-displacement-replay-fidelity witness keeps sufficing',
  'current_support': [f'APPLICABILITY-LEDGER.json#{AP}', f'FOREIGN-PRESSURE-LEDGER.json#{FP}', f'DATACUBE-TRANSFER-LEDGER.json#{TL}'],
  'discharge_path': 'either show later that one compact refresh-scope-axis-remediation-displacement-replay-fidelity witness keeps sufficing or promote broader replay-equivalence governance explicitly',
  'reviewed_datacubes': [
    {'datacube':'KubernetesCheckpointExactness-2026','surfaces':['REF-1006'],'pattern':'Kubelet checkpoint restore promises continuation at the exact checkpointed point','pressure':'exact-state restore deserves its own lane'},
    {'datacube':'CRIURestorePreservation-2026','surfaces':['REF-1007'],'pattern':'CRIU tests concrete state preservation after restore','pressure':'same-state preservation should remain stronger than successful relaunch'},
    {'datacube':'RunAILatestCheckpoint-2026','surfaces':['REF-1008'],'pattern':'Run:ai resumes from latest checkpoint with startup rerun and possible node change','pressure':'bounded-loss checkpoint replay should stay distinct from exact restore'},
    {'datacube':'KubernetesSourceRestart-2026','surfaces':['REF-1009'],'pattern':'Job suspend deletes Pods and replacements are new ephemeral Pods','pressure':'source-only restart should stay explicit when no replay basis is public'},
    {'datacube':'CUPTIPerformanceShadow-2026','surfaces':['REF-1010'],'pattern':'CUPTI restores functional device state but not performance-critical or host state','pressure':'keep stronger performance-shadow talk out of canon for now'}
  ]
})
append_item('RESOLUTION-LEDGER.json', {
  'id': RS,
  'title': 'resolve replay fidelity after displacement with one compact exact-vs-bounded-loss-vs-source-only witness',
  'state': 'admitted',
  'closure_state': 'resolved',
  'resolved_objects': [OQ],
  'closure_reason': 'added one compact refresh-scope-axis-remediation-displacement-replay-fidelity witness grounded in Kubernetes, CRIU, Run:ai, Kubernetes Job/Pod replacement, and CUPTI while keeping stronger performance-shadow machinery quarantined',
  'successor_surface': f'docs/20-constitution/open-question-registry.md#{NEXT_OQ.lower()}',
  'reopen_triggers': ['repeated later revisions need public accounting for performance-equivalent restore or host/device asymmetry that the compact replay-fidelity witness cannot absorb'],
  'repair': 'ordinary-continuation',
  'origin_revision': REV,
  'revision': REV,
  'witness_surface': f'RESOLUTION-LEDGER.json#{RS}',
  'action_lane': 'promote',
  'gate_class': 'concrete-evidence'
})
append_item('RETROSPECTIVE-QUEUE.json', {
  'id': RT,
  'title': 'revisit whether refresh-scope-axis-remediation-displacement-replay-fidelity pressure stayed bounded after rev0263',
  'state': 'cooling',
  'witness_surface': f'RETROSPECTIVE-QUEUE.json#{RT}',
  'candidate_surface': f'docs/90-quarantine/wild-speculations-2026-03-08.md#{QWS}',
  'cooldown_window': 'keep separate performance-shadow, cache-carry, and host/device-parity governance cooled until at least one later pass shows that source-backed replay-fidelity rows tied to the open-question registry and trajectory map cannot keep current work honest inside context-pack.json',
  'adjudication_family': 'replay-fidelity / replay-equivalence / performance-shadow pressure',
  'supersession_link': f'RETROSPECTIVE-QUEUE.json#{RT}',
  'cooling_state': 'cooling',
  'disposition': 'quarantine',
  'repair': 'keep-cooling',
  'origin_revision': REV,
  'revision': REV,
  'action_lane': 'await-adjudication',
  'gate_class': 'repeat-pass',
  'discharge': 'keep-cooling-unless-refresh-scope-axis-remediation-displacement-replay-fidelity-overflows'
})
append_item('FIREBREAK-LEDGER.json', {
  'id': FB,
  'title': 'keep performance-shadow restore speculation quarantined while resolving only exact-versus-bounded-loss replay fidelity',
  'state': 'active',
  'witness_surface': f'FIREBREAK-LEDGER.json#{FB}',
  'judged_property': 'the rev0263 decision that DelayBasin should extract one compact refresh-scope-axis-remediation-displacement-replay-fidelity witness over the existing resumption-basis and related admitted surfaces while the broader functional exactness / performance shadow / cache-carry residue story remains quarantined',
  'public_extract': 'One compact replay-fidelity witness is admitted; stronger performance-shadow governance stays quarantined.',
  'withheld_trace_surface': f'docs/90-quarantine/wild-speculations-2026-03-08.md#{QWS}',
  'allowed_role': 'public-summary-safe',
  'exposure_rule': 'may summarize the admitted compact witness and the fact of quarantine, but must not promote the quarantined performance-shadow court as canon',
  'trace_state': 'withheld',
  'repair': 'ordinary-continuation',
  'origin_revision': REV,
  'action_lane': 'keep-compact',
  'gate_class': 'concrete-evidence',
  'firebreak_surface': 'docs/10-method/reasoning-firebreaks-scratchpad-quarantine-and-public-extract-packets.md',
  'discharge': 'retain-until-a-later-revision-either-promotes-or-retires-the-quarantine',
  'revision': REV,
  'blocked_object': QWS
})

# CHANGELOG / ARCHIVE_INDEX
changelog = read('CHANGELOG.md')
if not changelog.startswith('## rev0263'):
    new_head = f"## {REV} — replay fidelity, performance-shadow quarantine, and frontier-ticket helper refactor\n\n- Added `{NEW_DOC}` to resolve `{OQ}` with a compact exact-state-vs-bounded-loss-vs-source-only replay-fidelity witness.\n- Kept the stronger {QWS_LABEL} move explicitly quarantined as `{QWS}` instead of laundering it into canon.\n- Hygiene/meta-engineering improvement: factored frontier-ticket row selection into `tools/frontier_ticket_lib.py`, rewired `tools/gen_frontier_ticket.py` and `tools/check_frontier_ticket_contract.py` to use the shared helpers, and added `{NEW_CHECKER}` through the shared refresh-scope-axis branch scaffold.\n\n" + changelog
    write('CHANGELOG.md', new_head)

archive = read('ARCHIVE_INDEX.md')
new_row = f'| {BUNDLE} | 2026-03-28 | Refresh-scope-axis-remediation-displacement-replay-fidelity revision: resolved {OQ} with a compact exact-vs-bounded-loss-vs-source-only witness, honestly quarantined stronger performance-shadow governance, and refactored frontier-ticket helpers so packaging stays wired and cumulative. |\n'
if new_row not in archive:
    archive = archive.replace('| --- | --- | --- |\n', '| --- | --- | --- |\n' + new_row, 1)
    write('ARCHIVE_INDEX.md', archive)

# surface status / release manifest placeholder
status = loadj('SURFACE-STATUS.json')
status['citation_head']['surface'] = BUNDLE
status['status_lanes']['frozen_public_surface'] = BUNDLE
status['status_lanes']['decision_state'] = 'admitted'
status['status_lanes']['execution_state'] = 'packaged'
status['status_lanes']['public_state'] = 'frozen-citable'
status['state_class'] = 'released'
dumpj('SURFACE-STATUS.json', status)

manifest = {
    'project': 'DelayBasin',
    'revision': REV,
    'timestamp': STAMP,
    'slug': SLUG,
    'bundle': BUNDLE,
}
dumpj('RELEASE-MANIFEST.json', manifest)

# receipt
old_receipt = loadj('REVISION-RECEIPT.json')
r = copy.deepcopy(old_receipt)
r['revision'] = REV
r['previous_revision'] = PREV
r['summary'] = 'Resolved replay fidelity after displacement with a compact exact-vs-bounded-loss-vs-source-only witness, honestly quarantined stronger performance-shadow governance, and refactored frontier-ticket helper selection so derivative handoff stays wired.'
r['summary_highlight'] = SUMMARY_HIGHLIGHT
r['codename'] = CODENAME
r['created_at'] = CREATED_AT
r['canon_additions'] = [NEW_DOC, f'{RS} resolved {OQ} with one compact refresh-scope-axis-remediation-displacement-replay-fidelity witness']
r['canonical_additions'] = r['canon_additions']
r['quarantine_additions'] = [f'docs/90-quarantine/wild-speculations-2026-03-08.md#{QWS}']
r['refs_used'] = [f'docs/00-meta/bibliography.md#{ref.lower()}' for ref in REFS]
r['touched_surfaces'] = [
    NEW_DOC,
    'docs/00-meta/bibliography.md',
    'docs/00-meta/llm-runbook.md',
    'docs/README.md',
    'docs/20-constitution/claim-registry.md',
    'docs/20-constitution/open-question-registry.md',
    'docs/20-constitution/prompt-pair-registry.md',
    'docs/00-meta/trajectory-map.md',
    'docs/50-promptcraft/prompt-pairs.md',
    'docs/90-quarantine/wild-speculations-2026-03-08.md',
    'WITNESS-VOCABULARY.json',
    'FOLLOWTHROUGH-QUEUE.json',
    'ASSUMPTION-LEDGER.json',
    'OBLIGATION-LEDGER.json',
    'APPLICABILITY-LEDGER.json',
    'FOREIGN-PRESSURE-LEDGER.json',
    'DATACUBE-TRANSFER-LEDGER.json',
    'RESOLUTION-LEDGER.json',
    'RETROSPECTIVE-QUEUE.json',
    'FIREBREAK-LEDGER.json',
    'REVISION-RECEIPT.json',
    'SURFACE-STATUS.json',
    'RELEASE-MANIFEST.json',
    'CHANGELOG.md',
    'ARCHIVE_INDEX.md',
    'tools/frontier_ticket_lib.py',
    'tools/gen_frontier_ticket.py',
    'tools/check_frontier_ticket_contract.py',
    'tools/packet_contract_common.py',
    NEW_CHECKER,
    'apply_rev0263.py',
]
r['artifacts_touched'] = r['touched_surfaces']
r['packaged_release'] = True
r['packaged_bundle_filename'] = BUNDLE
r['bundle'] = BUNDLE
r['slug'] = SLUG
r['checks_passed'] = ['make lint']
r['basis_witness']['expected_head'] = PREV
r['basis_witness']['observed_head'] = PREV
r['basis_witness']['basis_surfaces'] = ['docs/10-method/refresh-scope-axis-remediation-displacement-resumption-basis-witnesses-in-memory-continuation-checkpoint-backed-replay-and-cold-restart.md','docs/00-meta/trajectory-map.md','docs/20-constitution/open-question-registry.md']
r['basis_witness']['basis_omission_basis'] = 'broader performance-shadow accounting was intentionally omitted from canon because the evidence only justified one bounded refresh-scope-axis-remediation-displacement-replay-fidelity witness'
r['scope_witness']['active_request'] = 'Continue researching online, GPUstorming, and evolving DelayBasin with tight, high-leverage revisions; make at least one bold but disciplined speculative move, do at least one hygiene/meta-engineering improvement, run make lint, package the archive, and provide a working link.'
r['scope_witness']['exact_target'] = 'resolve OQ-0158 with one compact replay-fidelity witness, quarantine the stronger performance-shadow move, keep the archive small and cumulative, and refactor one small hygiene surface'
r['scope_witness']['scope_of_change'] = 'one compact replay-fidelity witness plus one honest quarantine and one frontier-ticket helper refactor'
r['move_classes'] = ['MV-0002','MV-0003','MV-0004','MV-0007','MV-0011']
r['status_witness']['frozen_public_surface'] = BUNDLE
r['status_witness']['decision_state'] = 'admitted'
r['status_witness']['execution_state'] = 'packaged'
r['status_witness']['public_state'] = 'frozen-citable'
r['retrospective_write_witness'] = {
    'witness_surface': f'RETROSPECTIVE-QUEUE.json#{RT}',
    'candidate_surface': f'docs/90-quarantine/wild-speculations-2026-03-08.md#{QWS}',
    'cooldown_window': 'keep separate performance-shadow, cache-carry, and host/device-parity governance cooled until at least one later pass shows that source-backed replay-fidelity rows tied to the open-question registry and trajectory map cannot keep current open work honest inside context-pack.json',
    'adjudication_family': 'replay-fidelity / replay-equivalence / performance-shadow pressure',
    'supersession_link': f'RETROSPECTIVE-QUEUE.json#{RT}',
    'cooling_state': 'cooling',
    'disposition': 'quarantine',
    'repair': 'keep-cooling'
}
r['followthrough_witness'] = {
    'blocked_object': NEXT_OQ,
    'local_surface': NEW_DOC,
    'followthrough_state': 'local',
    'boundary': 'one compact replay-fidelity witness only; stronger performance-shadow governance remains successor work',
    'next_proof_surface': 'docs/20-constitution/open-question-registry.md',
    'receiving_surface': f'docs/20-constitution/open-question-registry.md#{NEXT_OQ.lower()}',
    'repair': 'ordinary-continuation'
}
r['assumption_witness'] = {
    'assumption_surface': f'ASSUMPTION-LEDGER.json#{AS}',
    'assumption_statement': 'One compact refresh-scope-axis-remediation-displacement-replay-fidelity witness is enough for now.',
    'scope': 'continuity passes whose current public claim depends on how much execution state actually survived inside a replay or restart path after displacement',
    'supporting_surfaces': [NEW_DOC, f'docs/90-quarantine/wild-speculations-2026-03-08.md#{QWS}', f'APPLICABILITY-LEDGER.json#{AP}', f'FOREIGN-PRESSURE-LEDGER.json#{FP}'],
    'invalidation_triggers': ['repeated later revisions need standing governance over functional-exact versus performance-shadow restore rather than one compact replay-fidelity witness', 'the archive needs separate public rules just to distinguish optimizer, dataloader, host-side, or device-side loss boundaries inside replay', 'replay-fidelity cases repeatedly fail to stay distinguishable even with the witness in place'],
    'assumption_state': 'active',
    'repair': 'ordinary-continuation'
}
r['obligation_witness'] = {
    'witness_surface': f'OBLIGATION-LEDGER.json#{OB}',
    'target_surfaces': [NEW_DOC, f'docs/90-quarantine/wild-speculations-2026-03-08.md#{QWS}'],
    'missing_support': 'need repeated evidence that one compact replay-fidelity witness no longer keeps return exactness honest',
    'current_support': [NEW_DOC, f'APPLICABILITY-LEDGER.json#{AP}', f'FOREIGN-PRESSURE-LEDGER.json#{FP}'],
    'discharge_path': 'either show later that one compact refresh-scope-axis-remediation-displacement-replay-fidelity witness keeps sufficing or promote stronger replay-equivalence governance explicitly',
    'obligation_state': 'open',
    'repair': 'ordinary-continuation'
}
r['applicability_witness'] = {
    'witness_surface': f'APPLICABILITY-LEDGER.json#{AP}',
    'target_objective': 'keep checkpoint-backed return from silently inheriting exact-restore authority',
    'carry_object': 'one compact refresh-scope-axis-remediation-displacement-replay-fidelity witness over the already-admitted aftercare and resumption-basis surfaces',
    'applicability_conditions': ['the current claim already depends on axis independence, materiality, coupling, enforcement, durability, remediation provenance, remediation collateral, remediation capacity source, remediation displacement aftercare, and remediation displacement resumption basis truth', 'the missing ambiguity is whether the replay path restored exact saved state, only the latest durable checkpoint boundary, or merely restarted from source', 'one bounded witness still keeps replay-loss truth honest without standing performance-equivalence machinery'],
    'baselines': ['prior refresh-scope-axis-remediation-displacement-resumption-basis witness already names whether the return was in-memory, checkpoint-backed, or cold', 'the archive still lacks one compact public successor surface for how faithful the replay path actually was'],
    'non_fit_slice': 'cases whose real missing question is performance-shadow restore, cache warmth, host/device asymmetry, or restart-credit accounting rather than exact-versus-bounded-loss-versus-source-only replay fidelity',
    'budget': 'one compact replay-fidelity witness plus one resolution of OQ-0158; no performance-shadow court',
    'negative_transfer_budget': 'if a later pass needs public accounting for cache warmth, host/device parity, or performance-equivalent restore, do not overload this witness; reopen successor work instead',
    'applicability_state': 'admitted',
    'repair': 'ordinary-continuation'
}
r['foreign_pressure_witness'] = {
    'witness_surface': f'FOREIGN-PRESSURE-LEDGER.json#{FP}',
    'source_packets': [
        {'datacube':'kubernetes-checkpoint-exactness','surfaces':['Kubelet Checkpoint API'],'pressure':'documents restored containers continuing at exactly the same checkpointed point, so exact-state restore should remain a distinct replay-fidelity lane.'},
        {'datacube':'criu-restore-preservation','surfaces':['ZDTM test suite'],'pressure':'documents concrete state preservation across restore, so same-state replay should not be flattened into successful relaunch.'},
        {'datacube':'runai-latest-checkpoint-resume','surfaces':['Best Practices: Checkpointing Preemptible Training Workloads'],'pressure':'documents periodic checkpoint saving, startup-script rerun, and resume from latest checkpoint, so bounded-loss replay should stay distinct from exact restore.'},
        {'datacube':'kubernetes-source-restart','surfaces':['Jobs','Pod Lifecycle'],'pressure':'documents pod deletion and replacement without same-object continuation, so source-only restart should stay explicit when no replay basis is public.'},
        {'datacube':'cupti-functional-vs-performance-state','surfaces':['CUPTI Checkpoint API'],'pressure':'documents functional device-state restore but not performance-critical state or host state, so stronger performance-shadow governance should remain quarantined.'}
    ],
    'local_gap': 'rev0262 made return-basis truth explicit, but the archive still lacked one compact successor surface for how faithful a replay path actually was.',
    'bounded_take': 'Keep exact-state restore distinct from bounded-loss checkpoint replay and source-only restart once return basis is already explicit.',
    'explicit_non_take': ['no performance-shadow court','no cache-carry residue ledger','no functional-exactness market'],
    'assimilation_state': 'imported',
    'repair': 'ordinary-continuation'
}
r['transfer_witness'] = {
    'witness_surface': f'DATACUBE-TRANSFER-LEDGER.json#{TL}',
    'reviewed_datacubes': [
        {'datacube':'KubernetesCheckpointExactness-2026','surfaces':['REF-1006'],'pattern':'Kubelet checkpoint restore promises continuation at the exact checkpointed point','pressure':'exact-state restore deserves its own lane'},
        {'datacube':'CRIURestorePreservation-2026','surfaces':['REF-1007'],'pattern':'CRIU tests concrete state preservation after restore','pressure':'same-state preservation should remain stronger than successful relaunch'},
        {'datacube':'RunAILatestCheckpoint-2026','surfaces':['REF-1008'],'pattern':'Run:ai resumes from latest checkpoint with startup rerun and possible node change','pressure':'bounded-loss checkpoint replay should stay distinct from exact restore'},
        {'datacube':'KubernetesSourceRestart-2026','surfaces':['REF-1009'],'pattern':'Job suspend deletes Pods and replacements are new ephemeral Pods','pressure':'source-only restart should stay explicit when no replay basis is public'},
        {'datacube':'CUPTIPerformanceShadow-2026','surfaces':['REF-1010'],'pattern':'CUPTI restores functional device state but not performance-critical or host state','pressure':'keep stronger performance-shadow talk out of canon for now'}
    ],
    'local_gap': 'the archive still lacked one compact successor surface for how faithful an already checkpoint-backed or replacement-based return really was',
    'bounded_take': 'Keep the archive compact by extracting one refresh-scope-axis-remediation-displacement-replay-fidelity witness over the existing resumption-basis and related admitted surfaces; do not promote a performance-shadow court, cache-carry residue ledger, or functional-exactness market.',
    'explicit_non_take': ['no performance-shadow court','no cache-carry residue ledger','no functional-exactness market'],
    'anchor_surfaces': ['docs/10-method/refresh-scope-axis-remediation-displacement-resumption-basis-witnesses-in-memory-continuation-checkpoint-backed-replay-and-cold-restart.md','docs/20-constitution/open-question-registry.md','docs/00-meta/trajectory-map.md',f'docs/90-quarantine/wild-speculations-2026-03-08.md#{QWS}'],
    'open_transfer_question': NEXT_OQ,
    'transfer_state': 'supporting-only'
}
r['resolution_witness'] = {
    'witness_surface': f'RESOLUTION-LEDGER.json#{RS}',
    'resolved_objects': [OQ],
    'prior_state': 'unresolved frontier open question',
    'closure_reason': 'added one compact refresh-scope-axis-remediation-displacement-replay-fidelity witness grounded in Kubernetes, CRIU, Run:ai, Kubernetes Job/Pod replacement, and CUPTI while keeping stronger performance-shadow machinery quarantined',
    'successor_surface': f'docs/20-constitution/open-question-registry.md#{NEXT_OQ.lower()}',
    'reopen_triggers': ['repeated later revisions need public accounting for performance-equivalent restore or host/device asymmetry that the compact replay-fidelity witness cannot absorb'],
    'closure_state': 'resolved',
    'repair': 'ordinary-continuation'
}
r['reasoning_firebreak_witness'] = loadj('FIREBREAK-LEDGER.json')['items'][-1]
r['vocabulary_witness'] = {
    'witness_surface': 'WITNESS-VOCABULARY.json',
    'controlled_families': [NEW_FAMILY, 'action_lane', 'gate_class'],
    'target_surfaces': ['WITNESS-VOCABULARY.json', 'REVISION-RECEIPT.json', NEW_DOC, 'FOLLOWTHROUGH-QUEUE.json', 'RETROSPECTIVE-QUEUE.json', 'ASSUMPTION-LEDGER.json', 'OBLIGATION-LEDGER.json', 'APPLICABILITY-LEDGER.json', 'FOREIGN-PRESSURE-LEDGER.json', 'DATACUBE-TRANSFER-LEDGER.json', 'RESOLUTION-LEDGER.json', 'FIREBREAK-LEDGER.json'],
    'ambient_synonyms_excluded': EXCLUDED,
    'comparability_budget': 'refresh-scope-axis-remediation-displacement-replay-fidelity truth is compared by token; the compact witness says whether displaced work returned through exact-state restore, bounded-loss checkpoint replay, source-only restart, or an honest mix while raw cache traces, host/device asymmetry, restart timing, and scheduler traces stay outside the token',
    'vocabulary_state': 'locked',
    'repair': 'ordinary-continuation',
    NEW_FAMILY: wv['families'][NEW_FAMILY],
    'action_lane': wv['families']['action_lane'],
    'gate_class': wv['families']['gate_class'],
}
r['counterfactual_shadow'] = {
    'status': 'kept-nearby',
    'nearby_rejected_move': QWS,
    'pivot_surface': f'docs/90-quarantine/wild-speculations-2026-03-08.md#{QWS}',
    'rejection_reason': 'the evidence supported one compact replay-fidelity witness but not a standing performance-shadow court',
    'still_live': True,
}
r['receipt_freshness_witness'] = {
    'packaged_bundle_filename': BUNDLE,
    'manifest_timestamp_token': STAMP,
    'receipt_timestamp_token': STAMP,
    'bundle_stem_suffix_relation': 'aligned',
    'current_import_id': TL,
    'current_pressure_id': FP,
    'change_anchor_surface': 'CHANGELOG.md',
    'freshness_state': 'current',
    'repair': 'ordinary-continuation'
}
r['question_posture_witness'] = {
    'resolution_surface': 'RESOLUTION-LEDGER.json',
    'registry_surface': 'docs/20-constitution/open-question-registry.md',
    'trajectory_surface': 'docs/00-meta/trajectory-map.md',
    'synced_resolved_questions': [OQ],
    'frontier_selection_rule': 'select the last source-backed unresolved hot open question already projected into context-pack.json',
    'posture_state': 'synced',
    'repair': 'ordinary-continuation'
}
r['current_import_id'] = TL
r['current_pressure_id'] = FP
r['new_classes_or_families'] = [NEW_FAMILY]
r['quarantined_non_take'] = [QWS_LABEL]
r['refresh_scope_axis_remediation_displacement_replay_fidelity_witness'] = {
    'status': 'admitted',
    'family': NEW_FAMILY,
    'doc_path': NEW_DOC,
    'oq_id': OQ,
    'resolution_id': RS,
    'trajectory_oq_id': NEXT_OQ,
}
r['refresh_scope_axis_remediation_displacement_replay_fidelity_witness_contract'] = {
    'family': NEW_FAMILY,
    'checker': NEW_CHECKER,
    'doc_path': NEW_DOC,
    'oq_id': OQ,
    'claim_id': CL,
    'prompt_id': PP,
    'resolution_id': RS,
    'trajectory_oq_id': NEXT_OQ,
    'qws_id': QWS,
}
r['refresh_scope_axis_remediation_displacement_replay_fidelity_witness_meta'] = {'checker': NEW_CHECKER}
r['resolved_question'] = OQ
r['next_open_question'] = NEXT_OQ
r['checker_additions'] = [NEW_CHECKER]
r['change_summary'] = [f'{RS} resolved {OQ} with one compact refresh-scope-axis-remediation-displacement-replay-fidelity witness']
r['changes'] = r['change_summary']
dumpj('REVISION-RECEIPT.json', r)

# innovation packet and frontier/context will regenerate later
print('apply_rev0263 complete')
