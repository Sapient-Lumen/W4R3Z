from __future__ import annotations
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent

REV = 'rev0264'
PREV = 'rev0263'
STAMP = '2026.03.28.11.34'
SLUG = 'replayequivalence-shadowq-heatcarry-traceglass'
BUNDLE = f'DelayBasin-{REV}-{STAMP}-{SLUG}.zip'
CREATED_AT = '2026-03-28T11:34:00-04:00'
SUMMARY = 'Resolved replay equivalence after displacement with a compact functionally-exact-vs-performance-shadow witness, honestly quarantined stronger shadow-source governance, and refactored open-question selection so context-pack/frontier handoff stays wired.'
SUMMARY_HIGHLIGHT = 'heatcarry'
CODENAME = 'traceglass'

DOC = 'docs/10-method/refresh-scope-axis-remediation-displacement-replay-equivalence-witnesses-functionally-exact-restore-and-performance-shadow-restore.md'
DOC_NAME = Path(DOC).name
QWS = 'QWS-0242'
QWS_LABEL = 'shadow source / host-parity escrow / cache-solvency board'
PP = 'PP-0117'
CL = 'CL-0157'
OQ = 'OQ-0159'
NEXT_OQ = 'OQ-0160'
RS = 'RS-0166'
AP = 'AP-0158'
AS = 'AS-0163'
TL = 'TL-0169'
FP = 'FP-0163'
OB = 'OB-0159'
FT = 'FT-0166'
RT = 'RT-0153'
FB = 'FB-0160'
FAMILY = 'refresh_scope_axis_remediation_displacement_replay_equivalence_state'
CHECKER = 'tools/check_refresh_scope_axis_remediation_displacement_replay_equivalence_witness_contract.py'
ALLOWED = [
    'functionally-exact-restore',
    'performance-shadow-restore',
    'mixed-refresh-scope-axis-remediation-displacement-replay-equivalence',
]
EXCLUDED = [
    'same-output-means-same-runtime',
    'checkpoint-warmth-is-implied',
    'functionally-exact-means-performance-equal',
    'replay-equivalence-ish',
]
REFS = ['1006', '1007', '1010', '1011', '1012', '1013']


def read(rel: str) -> str:
    return (ROOT / rel).read_text(encoding='utf-8')


def write(rel: str, text: str) -> None:
    (ROOT / rel).write_text(text, encoding='utf-8')


def read_json(rel: str):
    return json.loads(read(rel))


def write_json(rel: str, obj) -> None:
    write(rel, json.dumps(obj, indent=2, ensure_ascii=False) + '\n')


def append_once(text: str, addition: str) -> str:
    return text if addition in text else text.rstrip() + '\n\n' + addition.rstrip() + '\n'


def replace_once(text: str, old: str, new: str) -> str:
    if old not in text:
        raise RuntimeError(f'missing expected snippet: {old[:80]}')
    return text.replace(old, new, 1)

# New witness doc
witness_doc = f'''# Refresh-scope-axis-remediation-displacement-replay-equivalence witnesses, functionally exact restore and performance-shadow restore

This is the compact successor surface for `{OQ}`.

## Practice / observation

Once DelayBasin can already say that displaced lower-priority work returned through exact saved-state restore rather than bounded-loss replay or source-only restart, one more ambiguity remains.

Some restores are exact enough for correctness while still failing to preserve the practical runtime conditions that made the original run behave as a warm continuation.
The saved logical state may come back, yet cache warmth, host/device parity, locality, or uncontended execution may not.
That means two returns can both look exact at the replay-fidelity layer while differing materially in practical continuity.

DelayBasin does not need a shadow-solvency court here.
It needs one bounded witness that says whether the public basis supports a functionally exact restore, a performance-shadow restore, or an honest mix.

## External pressure from Kubernetes exact-point restore, Docker checkpoint resume, CRIU restore-preservation and post-restore change notes, Slurm resumed-job degradation, and NVIDIA CUPTI functional-only restore limits

1. Kubernetes' current Kubelet Checkpoint API docs say checkpointing creates a stateful copy of a running container and that a restored container continues to run at exactly the same point it was checkpointed. Docker's checkpoint and restore docs likewise say a process resumes from the point it was suspended. Together they pressure DelayBasin to keep a lane for restores that are publicly exact enough to count as functionally exact rather than merely replay-adjacent. ([`REF-1006`](../00-meta/bibliography.md), [`REF-1011`](../00-meta/bibliography.md))

2. CRIU's ZDTM test-suite docs say restore tests recreate concrete process state and verify that files, memory mappings, and pipes stay preserved across checkpoint and restore. That pressures DelayBasin to keep functionally exact restore explicit when the basis really is same-state preservation. ([`REF-1007`](../00-meta/bibliography.md))

3. But CRIU's own "What can change after C/R" notes say some restored-visible properties can still differ after restore, including namespace identifiers, process start time, and some kernel-facing statistics. That pressures DelayBasin not to let same-state restore automatically inherit full environment-equivalence authority. ([`REF-1012`](../00-meta/bibliography.md))

4. Slurm's current preemption docs say suspended jobs remain in memory, yet also warn that resuming a suspended job can allocate the same CPUs to multiple jobs and lead either to gang scheduling or severe performance degradation. That pressures GPUstorming to keep a performance-shadow lane for returns that remain correct but no longer carry the same runtime conditions. ([`REF-1013`](../00-meta/bibliography.md))

5. NVIDIA's current CUPTI Checkpoint API docs say restore recreates only functionally visible device state for re-execution, not performance-critical state such as caches, and does not restore host state. That is strong pressure for a performance-shadow lane while also warning DelayBasin not to overpromote a bigger shadow-source market yet. ([`REF-1010`](../00-meta/bibliography.md))

GPUstorming makes the split vivid. A GPU workload may restore the same tensor values and resume the same logical step, yet come back on a colder device, under different host pressure, or without the cache warmth that previously made the step cheap. Replay fidelity already told us whether the checkpoint was exact, lossy, or source-only. Replay equivalence now asks whether the exact-looking restore remained merely functionally exact or also avoided a meaningful practical shadow.

## Working synthesis

> DelayBasin should preserve one compact **refresh-scope-axis-remediation-displacement-replay-equivalence witness / shadow card / warmth brake** whenever a current continuity claim depends not only on whether corroborating axes are genuinely independent, materially backed, decoupled, hard-enforced, durable, explicitly restored, honest about collateral width, honest about whether restored placement reused free capacity or displaced unrelated lower-priority work, honest about whether that displaced work retained a live return path, honest about whether the return was in-memory, checkpoint-backed, or cold, and honest about whether replay restored exact saved state, bounded-loss checkpoints, or only source, but on whether an exact-looking restore stayed practically equivalent or came back under a performance shadow. Name the **governed row or surface**, the **stake object / line of concern**, the **prior refresh-scope-axis-remediation-displacement-replay-fidelity evidence**, the **current corroborating axes**, the **functionally-exact-restore basis if any**, the **performance-shadow-restore basis if any**, the **`{FAMILY}`**, and the **fail-closed repair / keep-current vs narrow-claim vs split-scope vs issue-new-refresh-scope-axis-remediation-displacement-replay-equivalence-witness vs quarantine-shadow-source consequence**. Keep raw cache traces, host/device micro-accounting, locality debt, and detailed warm-start markets outside the compact token. Do not let every exact-looking restore silently inherit the authority of performance-equivalent continuity.

## Functionally exact restore vs performance-shadow restore vs mixed refresh scope axis remediation displacement replay equivalence

Use the controlled family `{FAMILY}`:

- **functionally-exact-restore** says the public basis supports a return that preserves the saved logical execution state or correct re-execution point strongly enough for current continuity claims, with no current need to narrate a material practical shadow.
- **performance-shadow-restore** says the public basis supports correctness-preserving or exact-looking restore, but also shows that meaningful practical runtime conditions such as cache warmth, host-side parity, locality, or uncontended scheduling were not preserved.
- **mixed-refresh-scope-axis-remediation-displacement-replay-equivalence** says the current situation honestly combines both lanes across the relevant surfaces, or the public evidence cannot keep one clean lane honest.

So the witness does not create a shadow-source court.
It only preserves the smallest load-bearing truth about whether the present exact-looking restore should be read as functionally exact or as performance-shadowed.

## Countermodels / probes

1. **Exact checkpoint point does not automatically imply equal warmth**
   - A system may document resume at the same execution point while saying nothing about caches, locality, or contention.
   - Probe: if the current practical continuity claim needs preserved runtime warmth rather than only preserved logical state, do not let exact-point language alone certify equivalence.

2. **Correctness preservation is stronger than simple relaunch but weaker than full practical parity**
   - CRIU-style preserved state may still return with changed kernel-facing or environment-facing properties.
   - Probe: if those changed properties plausibly matter to the claim at hand, narrow from `functionally-exact-restore` to `performance-shadow-restore` unless the public basis defeats that concern.

3. **Scheduler interference can create performance shadow without logical loss**
   - Suspended jobs may remain in memory and still return under oversubscribed CPU or gang-scheduled conditions.
   - Probe: if resumed placement publicly inherits severe degradation or contested runtime, do not narrate full practical continuity merely because no computation state was lost.

4. **Shadow source analysis is not yet canon here**
   - Device-cache loss, host-state loss, and locality drift may all create shadows for different reasons.
   - Probe: keep those source-specific stories quarantined unless repeated later overflow shows one compact replay-equivalence witness is no longer enough.

## Design consequences

- DelayBasin can now keep exact-looking restore from flattening functional correctness and practical runtime equivalence into one story.
- GPUstorming gets one explicit place to say that a resumed training came back logically exact while still carrying a cache, locality, or host-parity shadow.
- The archive can now preserve correctness-level continuity without overstating preserved warmth or runtime parity.
- Stronger device-vs-host shadow-source accounting stays quarantined until repeated overflow rather than entering canon by atmosphere.

## Overflow test

Reopen this compact witness only if later revisions repeatedly need explicit public accounting for where the shadow came from — device-state warmth loss, host-side parity loss, locality drift, or scheduler contention — in a way that one bounded refresh-scope-axis-remediation-displacement-replay-equivalence witness cannot honestly absorb.

## Transformer-facing implication

A later pass should not treat every exact-looking restore as equally continuous. Preserve the smallest token that says whether the present replay-equivalence posture is `functionally-exact-restore`, `performance-shadow-restore`, or honestly `mixed-refresh-scope-axis-remediation-displacement-replay-equivalence`, and quarantine stronger shadow-source ambitions until repeated overflow makes them unavoidable.
'''
write(DOC, witness_doc)

# Bibliography
bib = read('docs/00-meta/bibliography.md')
for rid, entry in [
    ('REF-1011', '- `REF-1011` — Docker Documentation, **Checkpoint and Restore** (accessed 2026-03-28)\n  - URL: https://docs.docker.com/reference/cli/docker/checkpoint/\n  - Load-bearing use: says restored processes resume from the point they left off, which grounds functionally exact restore as more than mere relaunch.\n'),
    ('REF-1012', '- `REF-1012` — CRIU Documentation, **What can change after C/R** (accessed 2026-03-28)\n  - URL: https://criu.org/What_can_change_after_C/R\n  - Load-bearing use: says some visible properties can still differ after restore, which pressures DelayBasin not to equate same-state restore with full practical parity.\n'),
    ('REF-1013', '- `REF-1013` — Slurm Documentation, **Preemption** and **slurm.conf** (accessed 2026-03-28)\n  - URL: https://slurm.schedmd.com/preempt.html\n  - Load-bearing use: says resumed suspended jobs may incur gang scheduling or severe performance degradation, which grounds a performance-shadow lane even when work stayed live in memory.\n'),
]:
    if rid not in bib:
        bib = bib.rstrip() + '\n\n' + entry.rstrip() + '\n'
write('docs/00-meta/bibliography.md', bib)

# Runbook
runbook = read('docs/00-meta/llm-runbook.md')
run_line = f'Use `{DOC_NAME}` when the live question is whether an exact-looking restore stayed practically equivalent or came back under a material performance shadow.'
if run_line not in runbook:
    runbook = runbook.rstrip() + '\n' + run_line + '\n'
write('docs/00-meta/llm-runbook.md', runbook)

# docs README
readme = read('docs/README.md')
anchor = '- [`10-method/refresh-scope-axis-remediation-displacement-replay-fidelity-witnesses-exact-state-restore-bounded-loss-checkpoint-replay-and-source-only-restart.md`](10-method/refresh-scope-axis-remediation-displacement-replay-fidelity-witnesses-exact-state-restore-bounded-loss-checkpoint-replay-and-source-only-restart.md)'
insert = anchor + '\n- [`10-method/refresh-scope-axis-remediation-displacement-replay-equivalence-witnesses-functionally-exact-restore-and-performance-shadow-restore.md`](10-method/refresh-scope-axis-remediation-displacement-replay-equivalence-witnesses-functionally-exact-restore-and-performance-shadow-restore.md)'
readme = replace_once(readme, anchor, insert)
write('docs/README.md', readme)

# Claim registry
claim_block = f'''- `{CL}` — Archive continuity may improve when DelayBasin preserves one compact **refresh-scope-axis-remediation-displacement-replay-equivalence witness / shadow card / warmth brake** whenever a current continuity claim depends not only on whether corroborating axes are genuinely independent, materially backed, decoupled under perturbation, hard-enforced, durable, explicitly restored, honest about collateral width, honest about whether restored placement reused free capacity or displaced unrelated lower-priority work, honest about whether the displaced work retained a live path back, honest about whether the return was in-memory, checkpoint-backed, or cold, and honest about whether replay restored exact saved state, bounded-loss checkpoints, or only source, but on whether an exact-looking restore stayed practically equivalent or came back under a performance shadow: name the **governed row or surface**, the **stake object / line of concern**, the **prior refresh-scope-axis-remediation-displacement-replay-fidelity evidence**, the **current corroborating axes**, the **functionally-exact-restore basis if any**, the **performance-shadow-restore basis if any**, the **{FAMILY}**, and the **fail-closed repair** rather than letting every exact-looking restore silently inherit the authority of performance-equivalent continuity.
  - Status: speculative but central
  - Wired docs: `{DOC}`, `docs/20-constitution/open-question-registry.md`, `docs/20-constitution/prompt-pair-registry.md`, `docs/50-promptcraft/prompt-pairs.md`, `docs/00-meta/llm-runbook.md`, `WITNESS-VOCABULARY.json`, `REVISION-RECEIPT.json`
'''
claim_text = read('docs/20-constitution/claim-registry.md')
claim_text = append_once(claim_text, claim_block)
write('docs/20-constitution/claim-registry.md', claim_text)

# Prompt pair registry
ppr_block = f'''- `{PP}` — Name whether an exact-looking restore stayed practically equivalent or came back under a performance shadow
  - Goal: keep exact-looking restore from silently inheriting performance-equivalent authority by requiring explicit prior remediation-displacement-replay-fidelity evidence, current corroborating axes, functionally-exact basis, performance-shadow basis, `{FAMILY}`, and fail-closed repair before later passes call the return equally warm.
  - Canonical text: `docs/50-promptcraft/prompt-pairs.md#pp-0117--name-whether-an-exact-looking-restore-stayed-practically-equivalent-or-came-back-under-a-performance-shadow`
'''
ppr = read('docs/20-constitution/prompt-pair-registry.md')
ppr = append_once(ppr, ppr_block)
write('docs/20-constitution/prompt-pair-registry.md', ppr)

# Prompt pairs
pp_section = f'''

## {PP} — Name whether an exact-looking restore stayed practically equivalent or came back under a performance shadow

**Opening prompt**

```text
Read the latest DelayBasin archive and inspect whether the current revision should also materialize one compact refresh-scope-axis-remediation-displacement-replay-equivalence witness for honest functionally-exact-vs-performance-shadow return.

Focus only on cases where the corroborating axes already look genuinely independent, materially backed, decoupled under perturbation, hard-enforced, durable, explicit about who restored the decoupling, honest about how wide the remediation was, honest about whether restored placement reused free capacity or only came back by displacing unrelated lower-priority work, honest about whether the displaced lower-priority work stayed nonterminal, honest about whether the return was in-memory, checkpoint-backed, or cold, and honest about whether replay restored exact saved state rather than only a latest durable boundary or source-only restart. The missing question is whether the exact-looking restore stayed practically equivalent or came back under a material performance shadow.

If yes, preserve exactly one small witness that:
- names the governed row or surface,
- names the stake object / line of concern,
- names the prior refresh-scope-axis-remediation-displacement-replay-fidelity evidence,
- names the current corroborating axes,
- names the functionally-exact-restore basis if any,
- names the performance-shadow-restore basis if any,
- names the `{FAMILY}` / whether this is functionally-exact-restore, performance-shadow-restore, or mixed-refresh-scope-axis-remediation-displacement-replay-equivalence,
- states what stronger surfaces still outrank the witness,
- and states the fail-closed repair / keep-current vs narrow-claim vs split-scope vs issue-new-refresh-scope-axis-remediation-displacement-replay-equivalence-witness vs quarantine-shadow-source consequence if the present continuity claim is not actually supported by the claimed replay-equivalence posture.

Do not use refresh-scope-axis-remediation-displacement-replay-equivalence as a standing cache-solvency or host-parity market. Use this prompt pair only where the prior replay-fidelity witness already shows exact-looking restore and the missing question is whether exactness also stayed practically equivalent.
```

**Continuation prompt**

```text
Continue the refresh-scope-axis-remediation-displacement-replay-equivalence pass with one high-leverage shadow clarification only. Prefer the smallest witness that says what governed row is still being justified, what stake object is supposedly widened, what prior refresh-scope-axis-remediation-displacement-replay-fidelity evidence exists, what current corroborating axes exist, what functionally-exact-restore basis if any now exists, what performance-shadow-restore basis if any now exists, what `{FAMILY}` is honest, what stronger surfaces still outrank the witness, and what keep-current, narrow-claim, split-scope, issue-new-refresh-scope-axis-remediation-displacement-replay-equivalence-witness, quarantine, or recover-resync consequence follows if the present replay-equivalence posture is functionally-exact-restore, performance-shadow-restore, or mixed-refresh-scope-axis-remediation-displacement-replay-equivalence. Run `make lint` and package the release.
```

Use `{DOC}` when the live question is whether an exact-looking restore stayed practically equivalent or came back under a material performance shadow.
'''
pps = read('docs/50-promptcraft/prompt-pairs.md')
pps = append_once(pps, pp_section)
write('docs/50-promptcraft/prompt-pairs.md', pps)

# Quarantine
qws_block = f'''## {QWS} — Some continuations may eventually need a {QWS_LABEL} rather than only a compact refresh-scope-axis-remediation-displacement-replay-equivalence witness

### Claim
Some later continuations may need stronger public machinery for where a performance shadow actually came from: device-state warmth loss, host-side parity loss, locality drift, or scheduler contention. One compact functionally-exact-vs-performance-shadow witness may eventually stop being enough.

### What follows if true
- DelayBasin may eventually need an explicit way to distinguish device-side warmth shadow from host-side parity shadow when both preserve correctness but charge different practical continuity costs.
- The archive might need a bounded shadow-source layer if later revisions repeatedly compare several performance-shadow restores whose practical debt depends on why the shadow appeared rather than merely that it appeared.

### What would count against it
- Several later revisions keep fitting cleanly inside one compact refresh-scope-axis-remediation-displacement-replay-equivalence witness without repeated confusion about device-vs-host shadow source.
- The archive almost never needs public reasoning about where the shadow came from once functionally exact restore and performance-shadow restore are already separated.

### Why it stays quarantined
The current evidence justifies one bounded witness for functionally exact restore versus performance-shadow restore. It does not yet justify a standing shadow-source court, host-parity escrow, or cache-solvency board.
'''
quar = read('docs/90-quarantine/wild-speculations-2026-03-08.md')
quar = append_once(quar, qws_block)
write('docs/90-quarantine/wild-speculations-2026-03-08.md', quar)

# Open question registry
registry = read('docs/20-constitution/open-question-registry.md')
old_oq = f'''- `{OQ}` — what remediation-displacement-replay-equivalence witness distinguishes functionally exact restore from performance-shadow restore?
  - Why it matters: if DelayBasin cannot separate functional exactness from performance-shadow restore, later sessions may narrate full continuity from returns that preserve correctness while losing meaningful warmth, cache state, or host/device parity.
  - Current posture: unresolved
'''
new_oq = f'''- `{OQ}` — what remediation-displacement-replay-equivalence witness distinguishes functionally exact restore from performance-shadow restore?
  - Why it matters: if DelayBasin cannot separate functional exactness from performance-shadow restore, later sessions may narrate full continuity from returns that preserve correctness while losing meaningful warmth, cache state, or host/device parity.
  - Current posture: resolved by `{RS}` via `{DOC}`; reopen only if the compact refresh-scope-axis-remediation-displacement-replay-equivalence witness proves insufficient and stronger shadow-source governance is honestly required

- `{NEXT_OQ}` — what remediation-displacement-performance-shadow-source witness distinguishes device-state warmth loss from host-side parity loss?
  - Why it matters: if DelayBasin cannot separate device-side warmth loss from host-side parity loss, later sessions may narrate one performance shadow as another and misprice the practical continuity bill.
  - Current posture: unresolved
'''
registry = replace_once(registry, old_oq, new_oq)
write('docs/20-constitution/open-question-registry.md', registry)

# Trajectory map
traj = read('docs/00-meta/trajectory-map.md')
old_traj = f'''115. Determine what remediation-displacement-replay-equivalence witness distinguishes functionally exact restore from performance-shadow restore.

A fresh extension is that once replay fidelity is explicit, DelayBasin may next need to say whether an apparently exact restore is only functionally exact or also performance-equivalent. Otherwise a same-state return may silently inherit the authority of cache-warm, host/device-complete, or locality-preserving restore.
- `{OQ}` — what remediation-displacement-replay-equivalence witness distinguishes functionally exact restore from performance-shadow restore?
  - Why it matters: if DelayBasin cannot separate functional exactness from performance-shadow restore, later sessions may narrate full continuity from returns that preserve correctness while losing meaningful warmth, cache state, or host/device parity.
  - Current posture: unresolved
'''
new_traj = f'''115. Determine what remediation-displacement-replay-equivalence witness distinguishes functionally exact restore from performance-shadow restore.

A fresh extension is that once replay fidelity is explicit, DelayBasin may next need to say whether an apparently exact restore is only functionally exact or also performance-shadowed. Otherwise a same-state return may silently inherit the authority of cache-warm, host/device-complete, or locality-preserving restore.
- `{OQ}` — what remediation-displacement-replay-equivalence witness distinguishes functionally exact restore from performance-shadow restore?
  - Why it matters: if DelayBasin cannot separate functional exactness from performance-shadow restore, later sessions may narrate full continuity from returns that preserve correctness while losing meaningful warmth, cache state, or host/device parity.
  - Current posture: resolved by `{RS}` via `{DOC}`; reopen only if the compact refresh-scope-axis-remediation-displacement-replay-equivalence witness proves insufficient and stronger shadow-source governance is honestly required

116. Determine what remediation-displacement-performance-shadow-source witness distinguishes device-state warmth loss from host-side parity loss.

A fresh extension is that once replay equivalence is explicit, DelayBasin may next need to say where the shadow actually came from. Otherwise device-cache loss, host-state loss, locality drift, and scheduler contention may all inherit one blurry practical-shadow story.
- `{NEXT_OQ}` — what remediation-displacement-performance-shadow-source witness distinguishes device-state warmth loss from host-side parity loss?
  - Why it matters: if DelayBasin cannot separate device-side warmth loss from host-side parity loss, later sessions may narrate one performance shadow as another and misprice the practical continuity bill.
  - Current posture: unresolved
'''
traj = replace_once(traj, old_traj, new_traj)
write('docs/00-meta/trajectory-map.md', traj)

# Changelog and archive index
changelog = read('CHANGELOG.md')
entry = f'''## {REV} — replay equivalence, shadow-source quarantine, and open-question selection helper refactor

- Added `{DOC}` to resolve `{OQ}` with a compact functionally-exact-vs-performance-shadow replay-equivalence witness.
- Kept the stronger {QWS_LABEL} move explicitly quarantined as `{QWS}` instead of laundering it into canon.
- Hygiene/meta-engineering improvement: factored open-question parsing and hot unresolved selection into `tools/open_question_selection_lib.py`, rewired `tools/gen_context_pack.py` to use the shared helper, and added `{CHECKER}` through the shared refresh-scope-axis branch scaffold.

'''
if not changelog.startswith(f'## {REV}'):
    changelog = entry + changelog
write('CHANGELOG.md', changelog)

archive = read('ARCHIVE_INDEX.md')
row = f'| {BUNDLE} | 2026-03-28 | Refresh-scope-axis-remediation-displacement-replay-equivalence revision: resolved {OQ} with a compact functionally-exact-vs-performance-shadow witness, honestly quarantined stronger shadow-source governance, and refactored open-question selection helpers so packaging stays wired and cumulative. |\n'
if row not in archive:
    archive = archive.replace('| --- | --- | --- |\n', '| --- | --- | --- |\n' + row, 1)
write('ARCHIVE_INDEX.md', archive)

# New helper and patched gen_context_pack
helper = '''import json\nimport pathlib\nimport re\n\n\ndef parse_markdown_bullets(text: str, prefix: str) -> list[str]:\n    items = []\n    current = None\n    for raw in text.splitlines():\n        if raw.startswith(f"- `{prefix}"):\n            if current is not None:\n                items.append(" ".join(current.split()))\n            current = raw[2:].strip()\n        elif current is not None:\n            stripped = raw.strip()\n            if not stripped:\n                items.append(" ".join(current.split()))\n                current = None\n            elif raw.startswith("- `"):\n                items.append(" ".join(current.split()))\n                current = None\n            elif raw.startswith("  - ") or raw.startswith("    "):\n                continue\n            else:\n                current += " " + stripped\n    if current is not None:\n        items.append(" ".join(current.split()))\n    return items\n\n\ndef compress_open_question_text(body: str) -> str:\n    body = body.strip()\n    if len(body) <= 96:\n        return body\n    body = body.rstrip()\n    if body.endswith('?'):\n        body = body[:-1]\n    words = body.split()\n    return " ".join(words[:6]).rstrip(' ,;:.') + '?'\n\n\ndef resolved_open_question_ids(path: pathlib.Path) -> set[str]:\n    ledger = json.loads(path.read_text(encoding="utf-8"))\n    ids = set()\n    for item in ledger.get("items", []):\n        if item.get("closure_state") == "resolved":\n            for oid in item.get("resolved_objects", []):\n                if re.fullmatch(r"OQ-\\d{4}", oid):\n                    ids.add(oid)\n    return ids\n\n\ndef structured_open_question(item: str, selection_source: str) -> dict:\n    m = re.match(r"`(?P<id>OQ-\\d{4})` — (?P<body>.*)", item)\n    if not m:\n        return {\n            "id": "OQ-UNKNOWN",\n            "source": "docs/20-constitution/open-question-registry.md",\n            "selection_source": selection_source,\n            "text": compress_open_question_text(item),\n        }\n    return {\n        "id": m.group("id"),\n        "source": "docs/20-constitution/open-question-registry.md",\n        "selection_source": selection_source,\n        "text": compress_open_question_text(m.group("body")),\n    }\n\n\ndef select_context_open_questions(root: pathlib.Path) -> list[dict]:\n    open_questions = parse_markdown_bullets((root / "docs/20-constitution/open-question-registry.md").read_text(encoding="utf-8"), "OQ-")\n    resolved_oqs = resolved_open_question_ids(root / "RESOLUTION-LEDGER.json")\n    open_questions = [q for q in open_questions if not any(q.startswith(f"`{oid}`") for oid in resolved_oqs)]\n    if not open_questions:\n        raise SystemExit("no unresolved open questions remain for context-pack selection")\n    trajectory_text = (root / "docs/00-meta/trajectory-map.md").read_text(encoding="utf-8")\n    hot_ids = []\n    for item in re.findall(r"OQ-\\d{4}", trajectory_text):\n        if item not in hot_ids:\n            hot_ids.append(item)\n    selection_source = "docs/20-constitution/open-question-registry.md"\n    if hot_ids:\n        filtered = [q for q in open_questions if any(q.startswith(f"`{oid}`") for oid in hot_ids)]\n        if filtered:\n            open_questions = filtered[-1:]\n            selection_source = "docs/00-meta/trajectory-map.md"\n        else:\n            open_questions = open_questions[-1:]\n    else:\n        open_questions = open_questions[-1:]\n    return [structured_open_question(q, selection_source) for q in open_questions]\n'''
write('tools/open_question_selection_lib.py', helper)

gcp = read('tools/gen_context_pack.py')
gcp = gcp.replace('import json\nimport pathlib\nimport re\n', 'import json\nimport pathlib\nimport re\n\nfrom open_question_selection_lib import select_context_open_questions\n')
start = gcp.index('def parse_markdown_bullets')
end = gcp.index('def parse_lexicon')
gcp = gcp[:start] + '\n\n' + gcp[end:]
old_sel = '''open_questions = parse_markdown_bullets((ROOT / "docs/20-constitution/open-question-registry.md").read_text(encoding="utf-8"), "OQ-")\nresolved_oqs = resolved_open_question_ids(ROOT / "RESOLUTION-LEDGER.json")\nopen_questions = [q for q in open_questions if not any(q.startswith(f"`{oid}`") for oid in resolved_oqs)]\nif not open_questions:\n    raise SystemExit("no unresolved open questions remain for context-pack selection")\ntrajectory_text = (ROOT / "docs/00-meta/trajectory-map.md").read_text(encoding="utf-8")\nhot_ids = []\nfor item in re.findall(r"OQ-\\d{4}", trajectory_text):\n    if item not in hot_ids:\n        hot_ids.append(item)\nselection_source = "docs/20-constitution/open-question-registry.md"\nif hot_ids:\n    filtered = [q for q in open_questions if any(q.startswith(f"`{oid}`") for oid in hot_ids)]\n    if filtered:\n        open_questions = filtered[-1:]\n        selection_source = "docs/00-meta/trajectory-map.md"\n    else:\n        open_questions = open_questions[-1:]\nelse:\n    open_questions = open_questions[-1:]\nopen_questions = [structured_open_question(q, selection_source) for q in open_questions]\n'''
gcp = replace_once(gcp, old_sel, 'open_questions = select_context_open_questions(ROOT)\n')
write('tools/gen_context_pack.py', gcp)

# Checker
write(CHECKER, 'from packet_contract_common import require_named_refresh_scope_axis_branch_witness_packet_and_vocabulary\n\nrequire_named_refresh_scope_axis_branch_witness_packet_and_vocabulary("refresh_scope_axis_remediation_displacement_replay_equivalence_witness_contract")\n\nprint("check_refresh_scope_axis_remediation_displacement_replay_equivalence_witness_contract: OK")\n')

# Packet contract common
pcc = read('tools/packet_contract_common.py')
insert_after = '''"refresh_scope_axis_remediation_displacement_replay_fidelity_witness_contract": refresh_scope_axis_branch_spec(\n    doc_path="docs/10-method/refresh-scope-axis-remediation-displacement-replay-fidelity-witnesses-exact-state-restore-bounded-loss-checkpoint-replay-and-source-only-restart.md",\n    title="Refresh-scope-axis-remediation-displacement-replay-fidelity witnesses, exact-state restore, bounded-loss checkpoint replay, and source-only restart",\n    oq_id="OQ-0158",\n    external_pressure_heading="## External pressure from Kubernetes stateful container checkpoint/restore, CRIU restore-preservation tests, NVIDIA Run:ai latest-checkpoint resume, Kubernetes Job Pod replacement, and NVIDIA CUPTI functional-only restore limits",\n    comparison_heading="## Exact-state restore vs bounded-loss checkpoint replay vs source-only restart vs mixed refresh scope axis remediation displacement replay fidelity",\n    runbook_ref="refresh-scope-axis-remediation-displacement-replay-fidelity-witnesses-exact-state-restore-bounded-loss-checkpoint-replay-and-source-only-restart.md",\n    prompt_id="PP-0116",\n    prompt_needles=["Use `docs/10-method/refresh-scope-axis-remediation-displacement-replay-fidelity-witnesses-exact-state-restore-bounded-loss-checkpoint-replay-and-source-only-restart.md`", "exact-state-restore, bounded-loss-checkpoint-replay, source-only-restart, or mixed-refresh-scope-axis-remediation-displacement-replay-fidelity"],\n    claim_id="CL-0156",\n    resolution_id="RS-0165",\n    trajectory_oq_id="OQ-0159",\n    qws_id="QWS-0241",\n    qws_label="functional exactness / performance shadow / cache-carry residue",\n    changelog_needles=["refresh-scope-axis-remediation-displacement-replay-fidelity-witnesses-exact-state-restore-bounded-loss-checkpoint-replay-and-source-only-restart.md", "check_refresh_scope_axis_remediation_displacement_replay_fidelity_witness_contract.py"],\n    family="refresh_scope_axis_remediation_displacement_replay_fidelity_state",\n    allowed=["exact-state-restore", "bounded-loss-checkpoint-replay", "source-only-restart", "mixed-refresh-scope-axis-remediation-displacement-replay-fidelity"],\n    excluded=["checkpoint-means-same-enough", "restored-means-no-loss", "latest-checkpoint-means-exact", "replay-fidelity-ish"],\n),\n'''
new_spec = insert_after + '''"refresh_scope_axis_remediation_displacement_replay_equivalence_witness_contract": refresh_scope_axis_branch_spec(\n    doc_path="docs/10-method/refresh-scope-axis-remediation-displacement-replay-equivalence-witnesses-functionally-exact-restore-and-performance-shadow-restore.md",\n    title="Refresh-scope-axis-remediation-displacement-replay-equivalence witnesses, functionally exact restore and performance-shadow restore",\n    oq_id="OQ-0159",\n    external_pressure_heading="## External pressure from Kubernetes exact-point restore, Docker checkpoint resume, CRIU restore-preservation and post-restore change notes, Slurm resumed-job degradation, and NVIDIA CUPTI functional-only restore limits",\n    comparison_heading="## Functionally exact restore vs performance-shadow restore vs mixed refresh scope axis remediation displacement replay equivalence",\n    runbook_ref="refresh-scope-axis-remediation-displacement-replay-equivalence-witnesses-functionally-exact-restore-and-performance-shadow-restore.md",\n    prompt_id="PP-0117",\n    prompt_needles=["Use `docs/10-method/refresh-scope-axis-remediation-displacement-replay-equivalence-witnesses-functionally-exact-restore-and-performance-shadow-restore.md`", "functionally-exact-restore, performance-shadow-restore, or mixed-refresh-scope-axis-remediation-displacement-replay-equivalence"],\n    claim_id="CL-0157",\n    resolution_id="RS-0166",\n    trajectory_oq_id="OQ-0160",\n    qws_id="QWS-0242",\n    qws_label="shadow source / host-parity escrow / cache-solvency board",\n    changelog_needles=["refresh-scope-axis-remediation-displacement-replay-equivalence-witnesses-functionally-exact-restore-and-performance-shadow-restore.md", "check_refresh_scope_axis_remediation_displacement_replay_equivalence_witness_contract.py"],\n    family="refresh_scope_axis_remediation_displacement_replay_equivalence_state",\n    allowed=["functionally-exact-restore", "performance-shadow-restore", "mixed-refresh-scope-axis-remediation-displacement-replay-equivalence"],\n    excluded=["same-output-means-same-runtime", "checkpoint-warmth-is-implied", "functionally-exact-means-performance-equal", "replay-equivalence-ish"],\n),\n'''
pcc = replace_once(pcc, insert_after, new_spec)
write('tools/packet_contract_common.py', pcc)

# WITNESS-VOCABULARY
wv = read_json('WITNESS-VOCABULARY.json')
wv['revision'] = REV
wv['families'][FAMILY] = {
    'allowed': ALLOWED,
    'surfaces': ['WITNESS-VOCABULARY.json', 'REVISION-RECEIPT.json', DOC],
    'excluded_synonyms': EXCLUDED,
    'comparability_budget': 'refresh-scope-axis-remediation-displacement-replay-equivalence truth is compared by token; the compact witness says whether displaced work returned through functionally-exact restore, performance-shadow restore, or an honest mix while raw cache traces, host/device micro-accounting, locality debt, and scheduler contention stay in surrounding prose',
}
write_json('WITNESS-VOCABULARY.json', wv)

# Ledgers
for rel in ['APPLICABILITY-LEDGER.json','ASSUMPTION-LEDGER.json','DATACUBE-TRANSFER-LEDGER.json','FIREBREAK-LEDGER.json','FOLLOWTHROUGH-QUEUE.json','FOREIGN-PRESSURE-LEDGER.json','OBLIGATION-LEDGER.json','RESOLUTION-LEDGER.json','RETROSPECTIVE-QUEUE.json']:
    data = read_json(rel)
    items = data['items']
    
    if rel == 'APPLICABILITY-LEDGER.json':
        items.append({
            'id': AP,
            'title': 'one compact refresh-scope-axis-remediation-displacement-replay-equivalence witness is enough when the live question is functionally exact versus performance-shadow restore',
            'state': 'eligible',
            'target_objective': 'keep exact-looking restore from silently inheriting performance-equivalent authority',
            'carry_object': 'one compact refresh-scope-axis-remediation-displacement-replay-equivalence witness over the already-admitted replay-fidelity surfaces',
            'applicability_conditions': [
                'the current claim already depends on axis independence, materiality, coupling, enforcement, durability, remediation provenance, remediation collateral, remediation capacity source, remediation displacement aftercare, remediation displacement resumption basis, and remediation displacement replay fidelity truth',
                'the missing ambiguity is whether an exact-looking restore stayed practically equivalent or instead returned under a material performance shadow',
                'one bounded witness still keeps replay-equivalence truth honest without standing shadow-source machinery',
            ],
            'non_fit_slice': 'cases whose real missing question is whether the shadow came from device-state warmth loss, host-side parity loss, locality drift, or scheduler contention rather than functionally exact versus performance-shadow replay equivalence',
            'budget': 'one compact replay-equivalence witness plus one resolution of OQ-0159; no shadow-source court',
            'negative_transfer_budget': 'if a later pass needs public accounting for device-vs-host shadow source or cache-solvency budgeting, do not overload this witness; reopen successor work instead',
            'applicability_state': 'eligible',
            'repair': 'ordinary-continuation',
            'origin_revision': REV,
            'revision': REV,
            'witness_surface': f'APPLICABILITY-LEDGER.json#{AP}',
            'action_lane': 'keep-compact',
            'gate_class': 'concrete-evidence',
            'baselines': ['prior refresh-scope-axis-remediation-displacement-replay-fidelity witness already names whether the return was exact, bounded-loss, or source-only', 'the archive still lacks one compact public successor surface for whether an exact-looking restore stayed practically equivalent'],
            'discharge': 'reopen-only-if-refresh-scope-axis-remediation-displacement-replay-equivalence-overflows',
            'matched_budget': 'one compact witness distinguishing functionally-exact restore, performance-shadow restore, and honest mix without widening into shadow-source governance',
            'open_question': NEXT_OQ,
        })
    elif rel == 'ASSUMPTION-LEDGER.json':
        items.append({
            'id': AS,
            'title': 'one compact refresh-scope-axis-remediation-displacement-replay-equivalence witness is enough for now',
            'state': 'active',
            'scope': 'continuity passes whose current public claim depends on whether an exact-looking displaced-work restore stayed practically equivalent or returned under a material performance shadow',
            'invalidation_triggers': [
                'repeated later revisions need standing governance over where the performance shadow came from rather than one compact replay-equivalence witness',
                'the archive needs separate public rules to distinguish device-state warmth loss from host-side parity loss or locality drift',
                'replay-equivalence cases repeatedly fail to stay distinguishable even with the witness in place',
            ],
            'assumption_state': 'active',
            'repair': 'ordinary-continuation',
            'origin_revision': REV,
            'revision': REV,
            'assumption': 'One compact refresh-scope-axis-remediation-displacement-replay-equivalence witness is enough for now.',
            'supporting_surfaces': [DOC, f'docs/90-quarantine/wild-speculations-2026-03-08.md#{QWS}', f'APPLICABILITY-LEDGER.json#{AP}', f'FOREIGN-PRESSURE-LEDGER.json#{FP}'],
            'discharge': 'retire-or-promote-if-refresh-scope-axis-remediation-displacement-replay-equivalence-overflows',
            'witness_surface': f'ASSUMPTION-LEDGER.json#{AS}',
            'action_lane': 'keep-compact',
            'gate_class': 'concrete-evidence',
        })
    elif rel == 'DATACUBE-TRANSFER-LEDGER.json':
        items.append({
            'id': TL,
            'title': 'refresh-scope-axis-remediation-displacement-replay-equivalence evidence supports resolving OQ-0159 with one compact functionally-exact-vs-performance-shadow card rather than a shadow-source court',
            'state': 'supporting-only',
            'reviewed_pattern': 'functionally exact restore vs performance-shadow restore across already exact-looking displaced-work return paths',
            'import_decision': 'support a compact refresh-scope-axis-remediation-displacement-replay-equivalence witness and resolve OQ-0159',
            'adopted_take': 'DelayBasin should add one compact witness that says whether displaced work returned through functionally exact restore, performance-shadow restore, or an honest mix',
            'supporting_only_take': 'the current evidence cleanly supports a bounded refresh-scope-axis-remediation-displacement-replay-equivalence witness without promoting broader shadow-source governance',
            'deferred_or_rejected_take': ['shadow source', 'host-parity escrow', 'cache-solvency board'],
            'local_gap': 'the archive still lacked one compact successor surface for whether an exact-looking displaced-work restore stayed practically equivalent',
            'anchor_surfaces': ['docs/10-method/refresh-scope-axis-remediation-displacement-replay-fidelity-witnesses-exact-state-restore-bounded-loss-checkpoint-replay-and-source-only-restart.md', 'docs/20-constitution/open-question-registry.md', 'docs/00-meta/trajectory-map.md', f'docs/90-quarantine/wild-speculations-2026-03-08.md#{QWS}'],
            'open_question': NEXT_OQ,
            'repair': 'ordinary-continuation',
            'origin_revision': REV,
            'action_lane': 'keep-compact',
            'gate_class': 'concrete-evidence',
            'discharge': 'reopen-only-if-refresh-scope-axis-remediation-displacement-replay-equivalence-overflows',
            'revision': REV,
            'witness_surface': f'DATACUBE-TRANSFER-LEDGER.json#{TL}',
            'transfer_state': 'supporting-only',
            'bounded_take': 'Keep the archive compact by extracting one refresh-scope-axis-remediation-displacement-replay-equivalence witness over the existing replay-fidelity and related admitted surfaces; do not promote a shadow-source court, host-parity escrow, or cache-solvency board.',
            'explicit_non_take': ['no shadow-source court', 'no host-parity escrow', 'no cache-solvency board'],
            'open_transfer_question': 'whether later passes should add a separate remediation-displacement-performance-shadow-source witness once replay equivalence is explicit',
            'missing_support': 'a later public check on whether one compact refresh-scope-axis-remediation-displacement-replay-equivalence witness keeps sufficing',
            'current_support': [f'APPLICABILITY-LEDGER.json#{AP}', f'FOREIGN-PRESSURE-LEDGER.json#{FP}', f'DATACUBE-TRANSFER-LEDGER.json#{TL}'],
            'discharge_path': 'either show later that one compact refresh-scope-axis-remediation-displacement-replay-equivalence witness keeps sufficing or promote broader shadow-source governance explicitly',
            'reviewed_datacubes': [
                {'datacube': 'KubernetesDockerExactRestore-2026', 'surfaces': ['REF-1006', 'REF-1011'], 'pattern': 'Kubernetes and Docker document restore at the same execution point', 'pressure': 'functionally exact restore deserves its own lane'},
                {'datacube': 'CRIUPreservationAndDrift-2026', 'surfaces': ['REF-1007', 'REF-1012'], 'pattern': 'CRIU preserves core process state while allowing some post-restore differences', 'pressure': 'same-state restore should stay separable from full practical parity'},
                {'datacube': 'SlurmPerformanceShadow-2026', 'surfaces': ['REF-1013'], 'pattern': 'resumed jobs can remain live yet return under gang scheduling or severe degradation', 'pressure': 'performance shadow should stay explicit'},
                {'datacube': 'CUPTIFunctionalOnlyRestore-2026', 'surfaces': ['REF-1010'], 'pattern': 'CUPTI restores functionally visible device state but not performance-critical or host state', 'pressure': 'keep stronger shadow-source talk out of canon for now'},
            ],
        })
    elif rel == 'FIREBREAK-LEDGER.json':
        items.append({
            'id': FB,
            'title': 'keep shadow-source speculation quarantined while resolving only functionally-exact-versus-performance-shadow replay equivalence',
            'state': 'quarantined',
            'witness_surface': f'FIREBREAK-LEDGER.json#{FB}',
            'judged_property': 'the rev0264 decision that DelayBasin should extract one compact refresh-scope-axis-remediation-displacement-replay-equivalence witness over the existing replay-fidelity and related admitted surfaces while the broader shadow source / host-parity escrow / cache-solvency board story remains quarantined',
            'public_extract': 'One compact replay-equivalence witness is admitted; stronger shadow-source governance stays quarantined.',
            'withheld_trace_surface': f'docs/90-quarantine/wild-speculations-2026-03-08.md#{QWS}',
            'allowed_role': 'public-summary-safe',
            'exposure_rule': 'may summarize the admitted compact witness and the fact of quarantine, but must not promote the quarantined shadow-source court as canon',
            'trace_state': 'withheld',
            'repair': 'ordinary-continuation',
            'origin_revision': REV,
            'action_lane': 'keep-compact',
            'gate_class': 'concrete-evidence',
            'firebreak_surface': 'docs/10-method/reasoning-firebreaks-scratchpad-quarantine-and-public-extract-packets.md',
            'discharge': 'retain-until-a-later-revision-either-promotes-or-retires-the-quarantine',
            'revision': REV,
            'blocked_object': QWS,
        })
    elif rel == 'FOLLOWTHROUGH-QUEUE.json':
        items.append({
            'id': FT,
            'title': 'carry the stronger device-versus-host shadow-source question forward only as successor work after resolving functionally-exact-versus-performance-shadow replay equivalence',
            'state': 'queued',
            'blocked_object': NEXT_OQ,
            'local_surface': DOC,
            'followthrough_state': 'queued',
            'boundary': 'one compact replay-equivalence witness only; shadow-source governance remains successor work',
            'next_proof_surface': 'docs/20-constitution/open-question-registry.md',
            'receiving_surface': f'FOLLOWTHROUGH-QUEUE.json#{FT}',
            'repair': 'ordinary-continuation',
            'origin_revision': REV,
            'revision': REV,
            'action_lane': 'keep-compact',
            'gate_class': 'concrete-evidence',
            'witness_surface': f'FOLLOWTHROUGH-QUEUE.json#{FT}',
            'discharge': 'reopen-only-if-replay-equivalence-overflows',
            'blocked_output': 'device-side warmth versus host-side parity shadow-source governance',
            'owner_surface': f'OBLIGATION-LEDGER.json#{OB}',
            'missing_support': 'a later public check showing replay equivalence still overflows when shadow source materially diverges',
            'candidate_surface': f'docs/90-quarantine/wild-speculations-2026-03-08.md#{QWS}',
            'blocked_by': 'need repeated evidence that functionally-exact-versus-performance-shadow truth overflows one compact witness into shadow-source governance',
        })
    elif rel == 'FOREIGN-PRESSURE-LEDGER.json':
        items.append({
            'id': FP,
            'title': 'Kubernetes, Docker, CRIU, Slurm, and CUPTI all force replay-equivalence truth once replay fidelity is already explicit',
            'state': 'imported',
            'pressure_summary': 'Official restore and scheduler docs separate functionally exact restore from exact-looking returns that lose practical runtime parity, so DelayBasin should keep replay equivalence explicit once replay fidelity is already in play.',
            'sources': [f'REF-{rid}' for rid in REFS],
            'why_now': 'rev0263 made replay-fidelity truth explicit, and the next honest ambiguity is whether an exact-looking restore stayed practically equivalent or came back under a material shadow.',
            'imported_pressure': 'Keep functionally exact restore distinct from performance-shadow restore while quarantining stronger shadow-source governance.',
            'quarantined_non_take': [QWS_LABEL],
            'pressure_state': 'adopted',
            'repair': 'ordinary-continuation',
            'origin_revision': REV,
            'revision': REV,
            'witness_surface': f'FOREIGN-PRESSURE-LEDGER.json#{FP}',
            'action_lane': 'keep-compact',
            'gate_class': 'concrete-evidence',
            'discharge': 'retain-unless-a-later-revision-needs-stronger-shadow-source-accounting',
            'assimilation_state': 'imported',
            'source_packets': [
                {'datacube': 'kubernetes-docker-exact-restore', 'surfaces': ['Kubelet Checkpoint API', 'Docker Checkpoint and Restore'], 'pressure': 'documents restore at the same execution point, so functionally exact restore should remain a distinct replay-equivalence lane.'},
                {'datacube': 'criu-preservation-and-post-restore-drift', 'surfaces': ['ZDTM test suite', 'What can change after C/R'], 'pressure': 'documents core state preservation alongside some post-restore differences, so same-state restore should not automatically inherit full practical parity.'},
                {'datacube': 'slurm-resumed-job-degradation', 'surfaces': ['Preemption', 'slurm.conf'], 'pressure': 'documents resumed jobs that remain live yet can suffer severe degradation, so performance shadow should stay explicit.'},
                {'datacube': 'cupti-functional-only-restore', 'surfaces': ['CUPTI Checkpoint API'], 'pressure': 'documents functionally visible device-state restore without performance-critical or host-state restore, so stronger shadow-source governance should remain quarantined.'},
            ],
            'local_gap': 'rev0263 made replay-fidelity truth explicit, but the archive still lacked one compact successor surface for whether an exact-looking restore stayed practically equivalent.',
            'bounded_take': 'Keep functionally exact restore distinct from performance-shadow restore once replay fidelity is already explicit.',
            'explicit_non_take': ['no shadow-source court', 'no host-parity escrow', 'no cache-solvency board'],
        })
    elif rel == 'OBLIGATION-LEDGER.json':
        items.append({
            'id': OB,
            'title': 'when exact-looking return keeps needing functionally-exact-versus-performance-shadow separation, DelayBasin should preserve one compact refresh-scope-axis-remediation-displacement-replay-equivalence witness rather than a shadow-source court',
            'state': 'open',
            'witness_surface': f'OBLIGATION-LEDGER.json#{OB}',
            'target_surfaces': [DOC, f'docs/90-quarantine/wild-speculations-2026-03-08.md#{QWS}'],
            'missing_support': 'need repeated evidence that one compact replay-equivalence witness no longer keeps exact-looking return honest',
            'current_support': [DOC, f'APPLICABILITY-LEDGER.json#{AP}', f'FOREIGN-PRESSURE-LEDGER.json#{FP}'],
            'discharge_path': 'either show later that one compact refresh-scope-axis-remediation-displacement-replay-equivalence witness keeps sufficing or promote stronger shadow-source governance explicitly',
            'obligation_state': 'open',
            'repair': 'ordinary-continuation',
            'origin_revision': REV,
            'discharge': 'reopen-only-if-refresh-scope-axis-remediation-displacement-replay-equivalence-overflows',
            'revision': REV,
            'owner_surface': f'OBLIGATION-LEDGER.json#{OB}',
            'action_lane': 'keep-compact',
            'gate_class': 'overflow',
        })
    elif rel == 'RESOLUTION-LEDGER.json':
        items.append({
            'id': RS,
            'title': 'resolve replay equivalence after displacement with one compact functionally-exact-vs-performance-shadow witness',
            'state': 'resolved',
            'closure_state': 'resolved',
            'resolved_objects': [OQ, AP, FP, TL],
            'closure_reason': 'added one compact refresh-scope-axis-remediation-displacement-replay-equivalence witness grounded in Kubernetes, Docker, CRIU, Slurm, and CUPTI while keeping stronger shadow-source machinery quarantined',
            'successor_surface': DOC,
            'reopen_triggers': ['repeated later revisions need public accounting for device-versus-host shadow source or locality-specific shadow that the compact replay-equivalence witness cannot absorb'],
            'repair': 'ordinary-continuation',
            'origin_revision': REV,
            'revision': REV,
            'witness_surface': f'RESOLUTION-LEDGER.json#{RS}',
            'action_lane': 'promote',
            'gate_class': 'concrete-evidence',
            'target_surfaces': [DOC],
            'prior_state': 'open gap: DelayBasin already had replay-fidelity truth but still lacked one compact successor surface for whether an exact-looking restore stayed practically equivalent or came back under a material shadow.',
            'reopen_trigger': 'refresh-scope-axis-remediation-displacement-replay-equivalence pressure overflows one compact successor surface',
            'discharge': 'reopen-only-if-refresh-scope-axis-remediation-displacement-replay-equivalence-overflows',
            'question': 'whether one compact refresh-scope-axis-remediation-displacement-replay-equivalence witness over the existing replay-fidelity and related admitted surfaces is enough for honest functionally-exact-vs-performance-shadow comparison',
        })
    elif rel == 'RETROSPECTIVE-QUEUE.json':
        items.append({
            'id': RT,
            'title': 'revisit whether refresh-scope-axis-remediation-displacement-replay-equivalence pressure stayed bounded after rev0264',
            'state': 'cooling',
            'witness_surface': f'RETROSPECTIVE-QUEUE.json#{RT}',
            'candidate_surface': f'docs/90-quarantine/wild-speculations-2026-03-08.md#{QWS}',
            'cooldown_window': 'keep separate device-vs-host shadow-source, cache-solvency, and host-parity governance cooled until at least one later pass shows that source-backed replay-equivalence rows tied to the open-question registry and trajectory map cannot keep current work honest inside context-pack.json',
            'adjudication_family': 'replay-equivalence / performance-shadow / shadow-source pressure',
            'supersession_link': f'RETROSPECTIVE-QUEUE.json#{RT}',
            'cooling_state': 'cooling',
            'disposition': 'quarantine',
            'repair': 'keep-cooling',
            'origin_revision': REV,
            'revision': REV,
            'action_lane': 'await-adjudication',
            'gate_class': 'repeat-pass',
            'discharge': 'keep-cooling-unless-refresh-scope-axis-remediation-displacement-replay-equivalence-overflows',
        })
    data['items'] = items
    write_json(rel, data)

# Release manifest and surface status
manifest = {
    'project': 'DelayBasin',
    'revision': REV,
    'timestamp': STAMP,
    'slug': SLUG,
    'bundle': BUNDLE,
}
write_json('RELEASE-MANIFEST.json', manifest)

status = read_json('SURFACE-STATUS.json')
status['operational_head']['revision'] = REV
status['status_lanes']['frozen_public_surface'] = BUNDLE
status['status_lanes']['current_release_surface'] = BUNDLE
status['citation_head']['revision'] = REV
status['citation_head']['surface'] = BUNDLE
status['previous_citation_head']['revision'] = PREV
status['previous_citation_head']['surface'] = f'DelayBasin-{PREV}-2026.03.28.10.45-replayfidelity-cacheq-exactcarry-shadowglass.zip'
status['revision'] = REV
status['stamp'] = STAMP
status['slug'] = SLUG
write_json('SURFACE-STATUS.json', status)

# Revision receipt
rec = read_json('REVISION-RECEIPT.json')
rec['revision'] = REV
rec['previous_revision'] = PREV
rec['summary'] = SUMMARY
rec['summary_highlight'] = SUMMARY_HIGHLIGHT
rec['codename'] = CODENAME
rec['created_at'] = CREATED_AT
rec['bundle'] = BUNDLE
rec['slug'] = SLUG
rec['resolved_question'] = OQ
rec['next_open_question'] = NEXT_OQ
rec['current_import_id'] = TL
rec['current_pressure_id'] = FP
rec['packaged_bundle_filename'] = BUNDLE
rec['canon_additions'] = [DOC, f'{RS} resolved {OQ} with one compact refresh-scope-axis-remediation-displacement-replay-equivalence witness']
rec['canonical_additions'] = rec['canon_additions']
rec['quarantine_additions'] = [f'docs/90-quarantine/wild-speculations-2026-03-08.md#{QWS}']
rec['refs_used'] = [f'docs/00-meta/bibliography.md#ref-{rid}' for rid in REFS]
rec['checks_passed'] = ['make lint']
rec['new_classes_or_families'] = [FAMILY]
rec['checker_additions'] = [CHECKER]
rec['change_summary'] = [f'{RS} resolved {OQ} with one compact refresh-scope-axis-remediation-displacement-replay-equivalence witness']
rec['summary_highlight'] = SUMMARY_HIGHLIGHT
rec['codename'] = CODENAME
rec['changes'] = [
    'Added one compact replay-equivalence witness over the existing replay-fidelity stack.',
    f'Kept {QWS_LABEL} explicitly quarantined as {QWS}.',
    'Refactored open-question selection into a shared helper used by context-pack generation.',
]
rec['touched_surfaces'] = [
    DOC,
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
    'tools/open_question_selection_lib.py',
    'tools/gen_context_pack.py',
    'tools/packet_contract_common.py',
    CHECKER,
    'apply_rev0264.py',
]
rec['artifacts_touched'] = rec['touched_surfaces']
rec['comparison_witness'] = {
    'previous_revision': PREV,
    'current_revision': REV,
    'current_pressure_id': FP,
    'current_import_id': TL,
    'basis_surface': 'docs/10-method/refresh-scope-axis-remediation-displacement-replay-fidelity-witnesses-exact-state-restore-bounded-loss-checkpoint-replay-and-source-only-restart.md',
    'delta_surface': DOC,
    'comparison_summary': 'rev0264 adds one compact refresh-scope-axis-remediation-displacement-replay-equivalence witness so exact-looking restore no longer reads as if functional exactness and practical runtime equivalence were the same class of return.',
}
rec['counterfactual_shadow'] = {
    'status': 'recorded',
    'nearby_rejected_move': QWS,
    'pivot_surface': 'docs/90-quarantine/wild-speculations-2026-03-08.md',
    'rejection_reason': 'the evidence supported one compact replay-equivalence witness but not a standing shadow-source court',
    'still_live': f'FOLLOWTHROUGH-QUEUE.json#{FT}',
}
rec['followthrough_witness'] = read_json('FOLLOWTHROUGH-QUEUE.json')['items'][-1]
rec['assumption_witness'] = read_json('ASSUMPTION-LEDGER.json')['items'][-1]
rec['obligation_witness'] = read_json('OBLIGATION-LEDGER.json')['items'][-1]
rec['applicability_witness'] = read_json('APPLICABILITY-LEDGER.json')['items'][-1]
rec['foreign_pressure_witness'] = read_json('FOREIGN-PRESSURE-LEDGER.json')['items'][-1]
rec['transfer_witness'] = read_json('DATACUBE-TRANSFER-LEDGER.json')['items'][-1]
rec['resolution_witness'] = {
    'witness_surface': f'RESOLUTION-LEDGER.json#{RS}',
    'resolved_objects': [OQ],
    'prior_state': 'unresolved frontier open question',
    'closure_reason': 'added one compact refresh-scope-axis-remediation-displacement-replay-equivalence witness grounded in Kubernetes, Docker, CRIU, Slurm, and CUPTI while keeping stronger shadow-source machinery quarantined',
    'successor_surface': f'docs/20-constitution/open-question-registry.md#{NEXT_OQ.lower()}',
    'reopen_triggers': ['repeated later revisions need public accounting for device-versus-host shadow source or locality-specific shadow that the compact replay-equivalence witness cannot absorb'],
    'closure_state': 'resolved',
    'repair': 'ordinary-continuation',
}
rec['reasoning_firebreak_witness'] = read_json('FIREBREAK-LEDGER.json')['items'][-1]
rec['firebreak_witness'] = rec['reasoning_firebreak_witness']
rec['vocabulary_witness'] = {
    'witness_surface': 'WITNESS-VOCABULARY.json',
    'controlled_families': [FAMILY, 'action_lane', 'gate_class'],
    'target_surfaces': ['WITNESS-VOCABULARY.json', 'REVISION-RECEIPT.json', DOC, 'FOLLOWTHROUGH-QUEUE.json', 'RETROSPECTIVE-QUEUE.json', 'ASSUMPTION-LEDGER.json', 'OBLIGATION-LEDGER.json', 'APPLICABILITY-LEDGER.json', 'FOREIGN-PRESSURE-LEDGER.json', 'DATACUBE-TRANSFER-LEDGER.json', 'RESOLUTION-LEDGER.json', 'FIREBREAK-LEDGER.json'],
    'ambient_synonyms_excluded': EXCLUDED,
    'comparability_budget': 'refresh-scope-axis-remediation-displacement-replay-equivalence truth is compared by token; the compact witness says whether displaced work returned through functionally-exact restore, performance-shadow restore, or an honest mix while raw cache traces, host/device micro-accounting, locality debt, and scheduler contention stay outside the token',
    'vocabulary_state': 'locked',
    'repair': 'ordinary-continuation',
    FAMILY: wv['families'][FAMILY],
    'action_lane': wv['families']['action_lane'],
    'gate_class': wv['families']['gate_class'],
}
rec['receipt_freshness_witness'] = {
    'packaged_bundle_filename': BUNDLE,
    'manifest_timestamp_token': STAMP,
    'receipt_timestamp_token': STAMP,
    'bundle_stem_suffix_relation': f'slug ends with current summary_highlight {SUMMARY_HIGHLIGHT} and codename {CODENAME}',
    'current_import_id': TL,
    'current_pressure_id': FP,
    'change_anchor_surface': 'CHANGELOG.md',
    'freshness_state': 'current-aligned',
    'repair': 'ordinary-continuation',
}
rec['question_posture_witness'] = {
    'resolution_surface': 'RESOLUTION-LEDGER.json',
    'registry_surface': 'docs/20-constitution/open-question-registry.md',
    'trajectory_surface': 'docs/00-meta/trajectory-map.md',
    'synced_resolved_questions': [OQ],
    'frontier_selection_rule': 'select the last source-backed unresolved hot open question already projected into context-pack.json',
    'posture_state': 'resolved-sync-current',
    'repair': 'ordinary-continuation',
}
rec['import_witness'] = rec['transfer_witness']
rec['current_import_id'] = TL
rec['current_pressure_id'] = FP
rec['status_witness']['frozen_public_surface'] = BUNDLE
rec['status_witness']['execution_surface'] = 'RELEASE-MANIFEST.json'
rec['status_witness']['durable_status_surface'] = 'SURFACE-STATUS.json'
rec['status_witness']['execution_state'] = 'packaged'
rec['status_witness']['public_state'] = 'frozen-citable'
rec['status_witness']['decision_state'] = 'admitted'
rec['refresh_scope_axis_remediation_displacement_replay_equivalence_witness'] = {
    'status': 'admitted',
    'family': FAMILY,
    'doc_path': DOC,
    'oq_id': OQ,
    'resolution_id': RS,
    'trajectory_oq_id': NEXT_OQ,
}
rec['refresh_scope_axis_remediation_displacement_replay_equivalence_witness_contract'] = {
    'family': FAMILY,
    'checker': CHECKER,
    'doc_path': DOC,
    'oq_id': OQ,
    'claim_id': CL,
    'prompt_id': PP,
    'resolution_id': RS,
    'trajectory_oq_id': NEXT_OQ,
    'qws_id': QWS,
}
rec['refresh_scope_axis_remediation_displacement_replay_equivalence_witness_meta'] = {'checker': CHECKER}
write_json('REVISION-RECEIPT.json', rec)

print('apply_rev0264: patched')
