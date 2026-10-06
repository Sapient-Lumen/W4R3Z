from pathlib import Path
import json, re

ROOT = Path('.')
REV = 'rev0240'
PREV = 'rev0239'
STAMP = '2026.03.24.00.54'
SLUG = 'recoverywriteback-canonbranch-sandbox-mergeglass'
BUNDLE = f'DelayBasin-{REV}-{STAMP}-{SLUG}.zip'

# ---------- helper ----------
def read(rel):
    return (ROOT / rel).read_text(encoding='utf-8')

def write(rel, text):
    (ROOT / rel).write_text(text, encoding='utf-8')

def replace_once(rel, old, new):
    txt = read(rel)
    if old not in txt:
        raise SystemExit(f'missing pattern in {rel}: {old[:80]}')
    write(rel, txt.replace(old, new, 1))

def append_text(rel, text):
    write(rel, read(rel).rstrip() + '\n\n' + text.rstrip() + '\n')

# ---------- new canon doc ----------
new_doc = '''# Recovery-writeback witnesses, canonical writeback, branch-local writeback, and sandbox-only restore

This is the compact successor surface for `OQ-0135`.

## Practice / observation

Once DelayBasin already distinguishes recovery anchor and recovery identity, one further failure mode stays live: a current row can honestly say that restored work is the same run or a branch and still fail to say whether that restored lineage is allowed to write back into canon.

A row can truthfully say that work resumed, a tuner continued, or a container was restored from checkpoint, yet that phrase can still hide whether the resumed lineage keeps writing to the canonical run, writes only to a derived branch, or must remain an isolated sandbox.

The archive does not need a standing recovery-writeback court for that.
It needs one bounded witness that says where write authority actually lands once a restore exists.

## External pressure from same-location experiment restore, existing-run result tables, experiment-directory autoresume, repeated named restores, and forensic sandbox copies

1. Ray Train keeps canonical continuation explicit at the storage lane. Its `BaseTrainer.restore()` docs say that the restored run continues writing results to the same cloud storage location. That pressures DelayBasin to keep same-run canonical writeback distinct from merely checkpoint-derived continuation. ([`REF-0884`](../00-meta/bibliography.md))

2. Ray Tune keeps existing-run writeback explicit. Its `Tuner.restore()` docs say all trials from the existing run are added to the result table, unfinished trials are continued, and the restored run continues writing results to the same cloud storage location. That pressures DelayBasin to keep existing-run canonical writeback distinct from branch-local retries or clones. ([`REF-0885`](../00-meta/bibliography.md))

3. BioNeMo keeps experiment-directory writeback explicit. Its ESM2 training docs say `experiment_name` is the sub-directory of `result_dir` that stores logs and checkpoints, and `resume_if_exists` attempts to resume if the checkpoint exists. That pressures DelayBasin to keep resumed same-experiment writeback distinct from noncanonical derivative runs that merely reuse checkpoint state. ([`REF-0886`](../00-meta/bibliography.md))

4. Podman keeps branch-local restore explicit. Its restore docs say a checkpoint tarball can be restored multiple times with different names and different IP identities, and `--keep` is needed if the checkpoint should remain reusable rather than consumed. That pressures DelayBasin to keep repeated named restores from silently inheriting canonical writeback authority. ([`REF-0883`](../00-meta/bibliography.md))

5. Kubernetes forensic checkpointing keeps sandbox isolation explicit. Its blog says the copy of a container can be analyzed and restored in a sandbox environment multiple times without the original container being aware of it. That pressures DelayBasin to keep sandbox-restored output from silently counting as authoritative continuation. ([`REF-0880`](../00-meta/bibliography.md))

GPUstorming sharpens the point. Real GPU systems increasingly mix interrupted-run autoresume into the same experiment directory, branch-like restores for debugging or replay, and sandbox checkpoint analysis. If DelayBasin only says that restored work "continued," later passes can still overclaim by letting branch-local output or sandbox artifacts leak back as canonical writeback.

## Working synthesis

> DelayBasin should preserve one compact **recovery-writeback witness / canon-write card / sandbox-isolation brake** whenever a current continuity claim depends not only on restore identity, but on whether restored output may update the canonical lineage. Name the **governed row or surface**, the **restore / resume / write path**, the **prior recovery-writeback evidence**, the **current recovery-writeback evidence**, the **recovery_writeback_state**, and the **fail-closed repair / keep-current vs narrow-claim vs split-row vs issue-new-recovery-writeback-witness vs quarantine-recovery-writeback-governance consequence**. Keep exact run ids, trial ids, object-store URIs, experiment directories, container names, branch names, checkpoint tarball paths, sandbox labels, and hostnames outside the compact token. Do not let “restored” or “continued” silently count as canonical write authority without explicit support.

## Canonical writeback vs branch-local writeback vs sandbox-only vs mixed recovery writeback

Use the controlled family `recovery_writeback_state`:

- **canonical-writeback** says the restored lineage is allowed to keep writing into the canonical run or authoritative result surface itself.
- **branch-local-writeback** says the restored lineage may keep writing, but only into a derived branch, clone, retry lane, or other noncanonical result surface.
- **sandbox-only** says the restored lineage is isolated to forensic, debugging, rehearsal, or sandbox use and should not count as an authoritative writeback lane.
- **mixed-recovery-writeback** says the current situation honestly combines canonical-writeback, branch-local-writeback, or sandbox-only layers such that no single recovery-writeback class stays honest.

So the witness does not create a standing promotion senate.
It only says where write authority lands once a restore exists.

## Countermodels / probes

1. **Recovery identity already covers this countermodel**
   - Maybe once DelayBasin already tracks same-run versus branch identity, writeback adds nothing.
   - Probe: compare later rereads that preserve only `recovery_identity_state` against rereads that also preserve one compact recovery-writeback witness and inspect whether later passes still confuse branch-local output or sandbox artifacts with canonical continuation.

2. **Writeback authority is too implementation-local countermodel**
   - Maybe output-directory or result-table details are too stack-specific for one compact token.
   - Probe: keep the witness at the coarse level of canonical-writeback vs branch-local-writeback vs sandbox-only vs mixed-recovery-writeback and inspect whether later passes still need per-system arbitration rather than one bounded write-authority card.

3. **Any honest writeback story needs standing governance countermodel**
   - Maybe once the archive starts separating canonical writeback from derived-branch or sandbox-only restore, one compact witness will always overflow into broader promotion governance.
   - Probe: keep the witness narrow first and inspect whether repeated later passes still require standing recovery-writeback governance rather than ordinary clarification of write authority.

## Design consequences

- add one controlled `recovery_writeback_state` family to `WITNESS-VOCABULARY.json` with the allowed tokens `canonical-writeback`, `branch-local-writeback`, `sandbox-only`, and `mixed-recovery-writeback`;
- use the witness only where a current continuity claim depends on whether restored output may update canonical lineage rather than merely existing as a resumed or derived branch;
- keep exact run ids, trial names, cloud/object-store URIs, result directories, checkpoint paths, container names, and sandbox labels outside the compact token itself;
- prefer `narrow-claim`, `split-row`, or `issue-new-recovery-writeback-witness` when the current claim honestly only supports branch-local or sandbox-only output rather than canonical writeback;
- and quarantine any stronger recovery-writeback court, promotion senate, or sandbox board unless repeated overflow shows that one bounded witness is no longer enough.

## Overflow test

Reopen the stronger machinery only if one compact recovery-writeback witness is no longer enough — for example, if the archive honestly needs standing governance over branch promotion, sandbox-to-canonical carryover, cross-row merge arbitration, or writeback admission policy that cannot be expressed as one bounded witness plus the existing recovery-anchor and recovery-identity surfaces.

Until then, prefer this compact successor surface over a recovery-writeback court, promotion senate, or sandbox board.

## Transformer-facing implication

If this frame survives, then DelayBasin is preserving something sharper than “the system restored and continued.”
It is also preserving whether restored output may keep writing into canon, only into a derived branch, or only into an isolated sandbox.
That matters because later stateless passes can preserve all the nearby recovery and lineage prose and still silently overclaim authority just by sounding continuation-consistent.
'''
write('docs/10-method/recovery-writeback-witnesses-canonical-writeback-derived-branch-writeback-and-sandbox-isolation.md', new_doc)

# ---------- runbook ----------
replace_once('docs/00-meta/llm-runbook.md',
    'Use `docs/10-method/recovery-identity-witnesses-continuing-resumes-checkpoint-forked-clones-and-sandbox-restored-branches.md` when the live question is whether a restore is still the interrupted run continuing or instead a checkpoint-forked clone, a sandbox branch, or an honest mixture.\n',
    'Use `docs/10-method/recovery-identity-witnesses-continuing-resumes-checkpoint-forked-clones-and-sandbox-restored-branches.md` when the live question is whether a restore is still the interrupted run continuing or instead a checkpoint-forked clone, a sandbox branch, or an honest mixture.\nUse `docs/10-method/recovery-writeback-witnesses-canonical-writeback-derived-branch-writeback-and-sandbox-isolation.md` when the live question is whether restored output may keep writing into canonical lineage, only into a derived branch, only into a sandbox, or an honest mixture.\n')

# ---------- claim registry ----------
append_text('docs/20-constitution/claim-registry.md', '''- `CL-0133` — Archive continuity may improve when DelayBasin preserves one compact **recovery-writeback witness / canon-write card / sandbox-isolation brake** whenever a current continuity claim depends on restored work sounding authoritative even though the real write authority may be canonical-writeback, branch-local-writeback, sandbox-only, or mixed-recovery-writeback: name the **governed row or surface**, the **restore / resume / write path**, the **prior recovery-writeback evidence**, the **current recovery-writeback evidence**, the **recovery_writeback_state**, and the **fail-closed repair** rather than letting any restored or continued phrase silently count as canonical write authority.
  - Status: speculative but central
  - Wired docs: `docs/10-method/recovery-writeback-witnesses-canonical-writeback-derived-branch-writeback-and-sandbox-isolation.md`, `docs/20-constitution/open-question-registry.md`, `docs/20-constitution/prompt-pair-registry.md`, `docs/50-promptcraft/prompt-pairs.md`, `docs/00-meta/llm-runbook.md`, `WITNESS-VOCABULARY.json`, `REVISION-RECEIPT.json`''')

# ---------- prompt pair registry ----------
append_text('docs/20-constitution/prompt-pair-registry.md', '''- `PP-0093` — Name where restored output is allowed to write back
  - Goal: keep restored or continued prose from silently inheriting canonical authority by requiring explicit prior/current writeback evidence, `recovery_writeback_state`, and fail-closed repair before later passes call a restored lineage authoritative continuation.
  - Canonical text: `docs/50-promptcraft/prompt-pairs.md#pp-0093--name-where-restored-output-is-allowed-to-write-back`''')

# ---------- prompt pairs ----------
append_text('docs/50-promptcraft/prompt-pairs.md', '''Use `docs/10-method/recovery-writeback-witnesses-canonical-writeback-derived-branch-writeback-and-sandbox-isolation.md` when the live question is whether restored output writes back into canon, only into a derived branch, only into a sandbox, or an honest mixture.

## `PP-0093` — Name where restored output is allowed to write back

**Opening prompt**

```text
Read the latest DelayBasin archive and inspect whether the current revision should also materialize one compact recovery-writeback witness for honest restored-lineage authority.

Focus only on whether restored output may keep writing into canonical lineage, only into a derived branch, or only into a sandbox.

If yes, preserve exactly one small witness that:
- names the governed row or surface,
- names the restore / resume / write path,
- names the prior recovery-writeback evidence,
- names the current recovery-writeback evidence,
- names the recovery_writeback_state / whether this is canonical-writeback, branch-local-writeback, sandbox-only, or mixed-recovery-writeback,
- states what stronger surfaces still outrank the witness,
- and states the fail-closed repair / keep-current vs narrow-claim vs split-row vs issue-new-recovery-writeback-witness vs quarantine-recovery-writeback-governance consequence if the present continuity claim only supports branch-local or sandbox-only output rather than canonical writeback.

Do not use recovery writeback as a governance metaphor. Use this prompt pair only where a durable row already depends on restored work sounding authoritative and the missing question is whether one small writeback card would keep canonical continuation, derived-branch output, and sandbox-only restore distinct without promoting a broader recovery-writeback court.
```

**Continuation prompt**

```text
Continue the recovery-writeback pass with one high-leverage authority clarification only. Prefer the smallest witness that says what governed row is still being justified, what restore, resume, or write path is supposedly unchanged, what the prior recovery-writeback evidence was, what the current recovery-writeback evidence is, what recovery_writeback_state is honest, what stronger surfaces still outrank the witness, and what keep-current, narrow-claim, split-row, issue-new-recovery-writeback-witness, quarantine, or recover-resync consequence follows if the current claim is really only branch-local or sandbox-only rather than canonical writeback. Run lint and package the release.
```''')

# ---------- bibliography ----------
append_text('docs/00-meta/bibliography.md', '''- `REF-0884` — Ray Documentation, **BaseTrainer.restore** (accessed 2026-03-24)
  - URL: https://docs.ray.io/en/latest/train/api/doc/ray.train.trainer.BaseTrainer.restore.html
  - Load-bearing use: documents that a restored Train run continues writing results to the same cloud storage location, which pressures DelayBasin to keep canonical writeback distinct from merely restored lineage.

- `REF-0885` — Ray Documentation, **Tuner.restore** (accessed 2026-03-24)
  - URL: https://docs.ray.io/en/latest/tune/api/doc/ray.tune.Tuner.restore.html
  - Load-bearing use: documents that all trials from the existing run are added to the result table, unfinished trials are continued, and the restored run continues writing results to the same cloud storage location, which pressures DelayBasin to keep existing-run canonical writeback distinct from derived branch output.

- `REF-0886` — BioNeMo Framework, **Train esm2** (accessed 2026-03-24)
  - URL: https://docs.nvidia.com/bionemo-framework/2.6/API_reference/bionemo/esm2/scripts/train_esm2/
  - Load-bearing use: documents that `experiment_name` names the `result_dir` sub-directory storing logs and checkpoints and that `resume_if_exists` attempts to resume there, which pressures DelayBasin to keep same-experiment writeback distinct from noncanonical derivative runs.''')

# ---------- open question registry ----------
replace_once('docs/20-constitution/open-question-registry.md',
'''- `OQ-0135` — what recovery-writeback witness distinguishes canonical continuation from isolated branch or sandbox-only restore?
  - Why it matters: if DelayBasin cannot say whether a restored branch may write back into canonical lineage or must stay isolated, later sessions may mistake clone or sandbox output for authoritative continuation.
  - Current posture: unresolved
''',
'''- `OQ-0135` — what recovery-writeback witness distinguishes canonical continuation from isolated branch or sandbox-only restore?
  - Why it matters: if DelayBasin cannot say whether a restored branch may write back into canonical lineage or must stay isolated, later sessions may mistake clone or sandbox output for authoritative continuation.
  - Current posture: resolved by `RS-0142` via `docs/10-method/recovery-writeback-witnesses-canonical-writeback-derived-branch-writeback-and-sandbox-isolation.md`; reopen only if the compact recovery-writeback witness proves insufficient and stronger recovery-writeback governance is honestly required

- `OQ-0136` — what recovery-promotion witness distinguishes direct canonical writeback from promotion-gated branch import or sandbox export-only carryover?
  - Why it matters: if DelayBasin cannot say how noncanonical restored output may later re-enter canon, later sessions may mistake branch-local success or sandbox analysis for already-promoted authority.
  - Current posture: unresolved
''')

# ---------- trajectory map ----------
replace_once('docs/00-meta/trajectory-map.md',
'''91. Determine what minimal recovery-writeback witness distinguishes canonical continuation from isolated branch or sandbox-only restore.

A fresh extension is that DelayBasin may next need to say not only whether a restore is the same run or a branch, but whether that restore may write back into canonical lineage or must remain isolated. Once compact recovery-identity witnesses exist, the archive may next need one bounded recovery-writeback witness naming whether resumed work may update the canonical run, only a derived branch, or only a sandbox.
- `OQ-0135` — what recovery-writeback witness distinguishes canonical continuation from isolated branch or sandbox-only restore?
  - Why it matters: if DelayBasin cannot say whether a restored branch may write back into canonical lineage or must stay isolated, later sessions may mistake clone or sandbox output for authoritative continuation.
  - Current posture: unresolved
''',
'''91. Determine what minimal recovery-writeback witness distinguishes canonical continuation from isolated branch or sandbox-only restore.

A fresh extension is that DelayBasin may next need to say not only whether a restore is the same run or a branch, but whether that restore may write back into canonical lineage or must remain isolated. Once compact recovery-identity witnesses exist, the archive may next need one bounded recovery-writeback witness naming whether resumed work may update the canonical run, only a derived branch, or only a sandbox.
- `OQ-0135` — what recovery-writeback witness distinguishes canonical continuation from isolated branch or sandbox-only restore?
  - Why it matters: if DelayBasin cannot say whether a restored branch may write back into canonical lineage or must stay isolated, later sessions may mistake clone or sandbox output for authoritative continuation.
  - Current posture: resolved by `RS-0142` via `docs/10-method/recovery-writeback-witnesses-canonical-writeback-derived-branch-writeback-and-sandbox-isolation.md`; reopen only if the compact recovery-writeback witness proves insufficient and stronger recovery-writeback governance is honestly required

92. Determine what minimal recovery-promotion witness distinguishes direct canonical writeback from promotion-gated branch import or sandbox export-only carryover.

A fresh extension is that DelayBasin may next need to say not only whether restored output writes back into canon, but how noncanonical output may later re-enter canonical lineage. Once compact recovery-writeback witnesses exist, the archive may next need one bounded recovery-promotion witness naming whether branch or sandbox output is already authoritative, promotion-gated, or export-only.
- `OQ-0136` — what recovery-promotion witness distinguishes direct canonical writeback from promotion-gated branch import or sandbox export-only carryover?
  - Why it matters: if DelayBasin cannot say how noncanonical restored output may later re-enter canon, later sessions may mistake branch-local success or sandbox analysis for already-promoted authority.
  - Current posture: unresolved
''')

# ---------- quarantine ----------
append_text('docs/90-quarantine/wild-speculations-2026-03-08.md', '''## QWS-0218 — Some recovery-writeback wins may require a stronger recovery-writeback court / promotion senate / sandbox board rather than one compact recovery-writeback witness

### Claim

Some future revisions may need a stronger recovery-writeback court / promotion senate / sandbox board rather than one compact recovery-writeback witness.

### What follows if true

- DelayBasin would need an explicit standing lane for canonical-versus-branch-versus-sandbox write authority rather than keeping all such pressure inside one bounded recovery-writeback witness.
- later revisions would need to distinguish compact write-authority cards from broader promotion governance more explicitly;
- some durable rows might need persistent recovery-writeback machinery rather than one controlled `recovery_writeback_state` family plus surrounding prose.

### What would count against it

- repeated later passes show that `docs/10-method/recovery-writeback-witnesses-canonical-writeback-derived-branch-writeback-and-sandbox-isolation.md` is enough to keep write-authority truth legible;
- recovery-writeback maintenance stays legible without needing standing promotion governance machinery;
- apparent overflow turns out to be better handled by existing recovery-anchor and recovery-identity witnesses plus surrounding recovery-promotion prose instead of a new sandbox board.

### Why it stays quarantined

The current imported evidence only shows that mainstream training and container systems repeatedly separate canonical same-run writeback from derived-branch restores and sandbox copies. It does not yet justify standing governance for all archive recovery-writeback decisions.''')

# ---------- packet contract common ----------
text = read('tools/packet_contract_common.py')
insert_after = '''    "recovery_identity_witness_contract": {
        "doc_path": "docs/10-method/recovery-identity-witnesses-continuing-resumes-checkpoint-forked-clones-and-sandbox-restored-branches.md",
        "doc_needles": [
            "# Recovery-identity witnesses, continuing resumes, checkpoint-forked clones, and sandbox-restored branches",
            "This is the compact successor surface for `OQ-0134`.",
            "## Practice / observation",
            "## External pressure from interrupted-run restore, unfinished-experiment autoresume, repeated named checkpoint restores, and forensic sandbox copies",
            "## Working synthesis",
            "## Continuing resume vs checkpoint fork vs sandbox branch vs mixed recovery identity",
            "## Countermodels / probes",
            "## Design consequences",
            "## Overflow test",
            "## Transformer-facing implication",
            "`recovery_identity_state`",
            "continuing-resume",
            "checkpoint-fork",
            "sandbox-branch",
            "mixed-recovery-identity",
        ],
        "runbook_ref": "recovery-identity-witnesses-continuing-resumes-checkpoint-forked-clones-and-sandbox-restored-branches.md",
        "prompt_id": "PP-0092",
        "prompt_needles": ["Use `docs/10-method/recovery-identity-witnesses-continuing-resumes-checkpoint-forked-clones-and-sandbox-restored-branches.md`", "continuing-resume, checkpoint-fork, sandbox-branch, or mixed-recovery-identity"],
        "claim_id": "CL-0132",
        "oq_id": "OQ-0134",
        "resolution_id": "RS-0141",
        "trajectory_oq_id": "OQ-0135",
        "qws_id": "QWS-0217",
        "qws_label": "recovery-identity court / clone senate / sandbox board",
        "changelog_needles": ["recovery-identity-witnesses-continuing-resumes-checkpoint-forked-clones-and-sandbox-restored-branches.md", "check_recovery_identity_witness_contract.py"],
        "family": "recovery_identity_state",
        "allowed": ["continuing-resume", "checkpoint-fork", "sandbox-branch", "mixed-recovery-identity"],
        "excluded": ["same-checkpoint-means-same-run", "clone-is-close-enough", "sandbox-counts-as-canonical", "identity-ish"],
    }
}
'''
new_block = '''    "recovery_identity_witness_contract": {
        "doc_path": "docs/10-method/recovery-identity-witnesses-continuing-resumes-checkpoint-forked-clones-and-sandbox-restored-branches.md",
        "doc_needles": [
            "# Recovery-identity witnesses, continuing resumes, checkpoint-forked clones, and sandbox-restored branches",
            "This is the compact successor surface for `OQ-0134`.",
            "## Practice / observation",
            "## External pressure from interrupted-run restore, unfinished-experiment autoresume, repeated named checkpoint restores, and forensic sandbox copies",
            "## Working synthesis",
            "## Continuing resume vs checkpoint fork vs sandbox branch vs mixed recovery identity",
            "## Countermodels / probes",
            "## Design consequences",
            "## Overflow test",
            "## Transformer-facing implication",
            "`recovery_identity_state`",
            "continuing-resume",
            "checkpoint-fork",
            "sandbox-branch",
            "mixed-recovery-identity",
        ],
        "runbook_ref": "recovery-identity-witnesses-continuing-resumes-checkpoint-forked-clones-and-sandbox-restored-branches.md",
        "prompt_id": "PP-0092",
        "prompt_needles": ["Use `docs/10-method/recovery-identity-witnesses-continuing-resumes-checkpoint-forked-clones-and-sandbox-restored-branches.md`", "continuing-resume, checkpoint-fork, sandbox-branch, or mixed-recovery-identity"],
        "claim_id": "CL-0132",
        "oq_id": "OQ-0134",
        "resolution_id": "RS-0141",
        "trajectory_oq_id": "OQ-0135",
        "qws_id": "QWS-0217",
        "qws_label": "recovery-identity court / clone senate / sandbox board",
        "changelog_needles": ["recovery-identity-witnesses-continuing-resumes-checkpoint-forked-clones-and-sandbox-restored-branches.md", "check_recovery_identity_witness_contract.py"],
        "family": "recovery_identity_state",
        "allowed": ["continuing-resume", "checkpoint-fork", "sandbox-branch", "mixed-recovery-identity"],
        "excluded": ["same-checkpoint-means-same-run", "clone-is-close-enough", "sandbox-counts-as-canonical", "identity-ish"],
    },
    "recovery_writeback_witness_contract": {
        "doc_path": "docs/10-method/recovery-writeback-witnesses-canonical-writeback-derived-branch-writeback-and-sandbox-isolation.md",
        "doc_needles": [
            "# Recovery-writeback witnesses, canonical writeback, branch-local writeback, and sandbox-only restore",
            "This is the compact successor surface for `OQ-0135`.",
            "## Practice / observation",
            "## External pressure from same-location experiment restore, existing-run result tables, experiment-directory autoresume, repeated named restores, and forensic sandbox copies",
            "## Working synthesis",
            "## Canonical writeback vs branch-local writeback vs sandbox-only vs mixed recovery writeback",
            "## Countermodels / probes",
            "## Design consequences",
            "## Overflow test",
            "## Transformer-facing implication",
            "`recovery_writeback_state`",
            "canonical-writeback",
            "branch-local-writeback",
            "sandbox-only",
            "mixed-recovery-writeback",
        ],
        "runbook_ref": "recovery-writeback-witnesses-canonical-writeback-derived-branch-writeback-and-sandbox-isolation.md",
        "prompt_id": "PP-0093",
        "prompt_needles": ["Use `docs/10-method/recovery-writeback-witnesses-canonical-writeback-derived-branch-writeback-and-sandbox-isolation.md`", "canonical-writeback, branch-local-writeback, sandbox-only, or mixed-recovery-writeback"],
        "claim_id": "CL-0133",
        "oq_id": "OQ-0135",
        "resolution_id": "RS-0142",
        "trajectory_oq_id": "OQ-0136",
        "qws_id": "QWS-0218",
        "qws_label": "recovery-writeback court / promotion senate / sandbox board",
        "changelog_needles": ["recovery-writeback-witnesses-canonical-writeback-derived-branch-writeback-and-sandbox-isolation.md", "check_recovery_writeback_witness_contract.py"],
        "family": "recovery_writeback_state",
        "allowed": ["canonical-writeback", "branch-local-writeback", "sandbox-only", "mixed-recovery-writeback"],
        "excluded": ["restored-means-authoritative", "branch-output-is-close-enough-to-canon", "sandbox-counts-as-writeback", "writeback-ish"],
    }
}
'''
if insert_after not in text:
    raise SystemExit('packet_contract_common tail block not found')
text = text.replace(insert_after, new_block, 1)
text = text.replace(
"def require_named_recovery_lineage_witness_packet_and_vocabulary(kind: str) -> None:\n    require_named_recovery_family_witness_packet_and_vocabulary(kind)\n",
"def require_named_recovery_lineage_witness_packet_and_vocabulary(kind: str) -> None:\n    require_named_recovery_family_witness_packet_and_vocabulary(kind)\n\n\ndef require_named_recovery_writeback_witness_packet_and_vocabulary(kind: str) -> None:\n    require_named_recovery_lineage_witness_packet_and_vocabulary(kind)\n",
1)
write('tools/packet_contract_common.py', text)

write('tools/check_recovery_writeback_witness_contract.py', "from packet_contract_common import require_named_recovery_writeback_witness_packet_and_vocabulary\n\nrequire_named_recovery_writeback_witness_packet_and_vocabulary(\"recovery_writeback_witness_contract\")\n\nprint(\"check_recovery_writeback_witness_contract: OK\")\n")
write('tools/check_recovery_identity_witness_contract.py', "from packet_contract_common import require_named_recovery_writeback_witness_packet_and_vocabulary\n\nrequire_named_recovery_writeback_witness_packet_and_vocabulary(\"recovery_identity_witness_contract\")\n\nprint(\"check_recovery_identity_witness_contract: OK\")\n")

# ---------- vocabulary ----------
vocab = json.loads(read('WITNESS-VOCABULARY.json'))
families = vocab['families']
families['recovery_writeback_state'] = {
    'description': 'Compact recovery-writeback witness saying where restored output is allowed to write: canonical lineage, derived branch, sandbox only, or an honest mixture.',
    'allowed_values': [
        'canonical-writeback',
        'branch-local-writeback',
        'sandbox-only',
        'mixed-recovery-writeback'
    ],
    'governing_question': 'OQ-0135',
    'successor_surface': 'docs/10-method/recovery-writeback-witnesses-canonical-writeback-derived-branch-writeback-and-sandbox-isolation.md',
    'witness_id': 'RWW-0142',
    'category': 'recovery-lineage-ish',
    'comparability_budget': 'recovery-writeback truth is compared by token; the compact recovery-writeback witness says whether restored output keeps canonical write authority, only branch-local authority, sandbox-only isolation, or a mixed writeback posture, while exact run ids, trial ids, result paths, checkpoint tarballs, container names, and sandbox labels stay in surrounding prose'
}
write('WITNESS-VOCABULARY.json', json.dumps(vocab, indent=2) + '\n')

# ---------- ledgers ----------
# common new items
AP = {
  'id':'AP-0134',
  'title':'the recovery-writeback witness stays smaller than a recovery-writeback court',
  'state':'gated',
  'question':'when should DelayBasin treat restored-output authority as one compact recovery-writeback witness instead of promoting broader promotion or sandbox governance?',
  'applies_when':[
    'a revision already has a durable row whose current claim depends on restored work sounding authoritative after identity is already known',
    'later passes still need to distinguish canonical-writeback, branch-local-writeback, sandbox-only, or mixed-recovery-writeback posture',
    'one compact successor surface plus the existing admitted recovery-anchor and recovery-identity witnesses still keeps write authority honest without standing promotion governance'
  ],
  'does_not_apply_when':[
    'the archive honestly requires standing governance over branch promotion, sandbox-to-canonical carryover, or cross-row merge arbitration',
    'the questioned surface is not really about where restored output is allowed to write'
  ],
  'budget':'one compact recovery-writeback witness plus one resolution of OQ-0135; no recovery-writeback court',
  'negative_transfer_budget':'do not treat restored or continued wording as proof of canonical write authority without explicit writeback support',
  'origin_revision':REV,
  'discharge':'reopen-only-if-recovery-writeback-overflows',
  'action_lane':'keep-compact',
  'gate_class':'concrete-evidence',
  'witness_surface':'APPLICABILITY-LEDGER.json#AP-0134',
  'applicability_state':'gated',
  'repair':'ordinary-continuation',
  'matched_budget':'one compact witness foregrounding canonical-vs-branch-vs-sandbox write authority without widening into broader promotion governance',
  'revision':REV,
  'target_objective':'keep recovery-writeback comparison honest without inflating a broader promotion-governance layer',
  'carry_object':'recovery-writeback witness / canon-write card / sandbox-isolation brake',
  'applicability_conditions':[
    'mainstream training and container systems keep same-run writeback distinct from derived-branch or sandbox restore lanes',
    'the archive can keep exact run ids, trial ids, result paths, checkpoint URIs, container names, and sandbox labels in surrounding prose',
    'recovery writeback remains subordinate to existing recovery-anchor and recovery-identity witnesses rather than a new promotion court'
  ],
  'baselines':['existing recovery-anchor-witness baseline','existing recovery-identity-witness baseline','existing witness-vocabulary baseline'],
  'non_fit_slice':'Do not generalize this revision into a recovery-writeback court, promotion senate, or sandbox board without later overflow evidence.',
  'fit_slice':'Bounded write-authority truth is best handled as one compact successor witness over the existing recovery-identity witness rather than as broader promotion governance.'
}
FP = {
  'id':'FP-0139',
  'title':'restore-writeback pressure pushes DelayBasin to extract one compact recovery-writeback witness rather than a recovery-writeback court',
  'state':'imported',
  'source_packets':[
    {'datacube':'RayTrainSameLocationWriteback-2026','surfaces':['REF-0884'],'pressure':'Ray Train explicitly says a restored run continues writing results to the same cloud storage location, which pressures DelayBasin to keep canonical writeback distinct from merely restored lineage.'},
    {'datacube':'RayTuneExistingRunWriteback-2026','surfaces':['REF-0885'],'pressure':'Ray Tune explicitly says all trials from the existing run stay in the result table, unfinished trials are continued, and the restored run keeps writing to the same cloud storage location, which pressures DelayBasin to preserve existing-run canonical writeback as a distinct authority class.'},
    {'datacube':'BioNeMoExperimentDirectoryResume-2026','surfaces':['REF-0886'],'pressure':'BioNeMo explicitly ties logs and checkpoints to an experiment sub-directory and attempts resume there when checkpoints exist, which pressures DelayBasin to keep same-experiment writeback distinct from derivative restore lanes.'},
    {'datacube':'PodmanRepeatedNamedRestore-2026','surfaces':['REF-0883'],'pressure':'Podman explicitly documents restoring the same checkpoint multiple times with different names and different IP identities, which pressures DelayBasin to keep repeated named restores from silently inheriting canonical writeback authority.'},
    {'datacube':'KubernetesForensicSandboxCopies-2026','surfaces':['REF-0880'],'pressure':'Kubernetes explicitly documents sandbox-restored checkpoint copies that can be restored multiple times without the original container being aware, which pressures DelayBasin to keep sandbox-restored output distinct from authoritative continuation.'}
  ],
  'local_gap':'DelayBasin already had compact recovery-anchor and recovery-identity witnesses, but it still lacked one compact successor surface for whether restored output may write back into canon, only a branch, or only a sandbox.',
  'bounded_take':'Extract one compact recovery-writeback witness, keep the current admitted recovery-anchor and recovery-identity surfaces narrow, and resolve OQ-0135 without opening broader recovery-writeback governance.',
  'explicit_non_take':['no recovery-writeback court','no promotion senate','no sandbox board','no standing merge tribunal'],
  'assimilation_state':'imported','repair':'ordinary-continuation','origin_revision':REV,'action_lane':'keep-compact','gate_class':'concrete-evidence','discharge':'reopen-only-if-recovery-writeback-overflows','revision':REV,
  'pressure':'the remaining gap is one missing compact successor surface for honest canonical-vs-branch-vs-sandbox write authority adjacent to the existing recovery-identity witness',
  'witness_surface':'FOREIGN-PRESSURE-LEDGER.json#FP-0139','foreign_pressure_surface':'FOREIGN-PRESSURE-LEDGER.json#FP-0139'
}
TL = {
  'id':'TL-0145',
  'title':'restore-writeback evidence supports resolving OQ-0135 with one compact recovery-writeback witness',
  'state':'supporting-only',
  'reviewed_datacubes':[
    {'datacube':'DelayBasin-rev0239','surfaces':['docs/10-method/recovery-identity-witnesses-continuing-resumes-checkpoint-forked-clones-and-sandbox-restored-branches.md','docs/10-method/recovery-anchor-witnesses-self-lineage-checkpoints-imported-seeds-converted-checkpoints-and-migrated-runtime-images.md','docs/20-constitution/open-question-registry.md','docs/00-meta/trajectory-map.md','OBLIGATION-LEDGER.json'],'pattern':'the archive already had recovery-anchor and recovery-identity witnesses but still lacked one compact successor surface for whether restored output could write back into canon or only into noncanonical lanes','pressure':'the honest next move is extraction and resolution, not a larger recovery-writeback layer'},
    {'datacube':'RayTrainSameLocationWriteback-2026','surfaces':['REF-0884'],'pattern':'a restored Train run continues writing results to the same cloud storage location','pressure':'DelayBasin should keep canonical same-run writeback distinct from merely restored lineage'},
    {'datacube':'RayTuneExistingRunWriteback-2026','surfaces':['REF-0885'],'pattern':'all trials from the existing run stay in the result table, unfinished trials are continued, and writes continue to the same cloud storage location','pressure':'DelayBasin should keep existing-run canonical writeback distinct from derived branch output'},
    {'datacube':'BioNeMoExperimentDirectoryResume-2026','surfaces':['REF-0886'],'pattern':'resume_if_exists targets the experiment sub-directory that stores logs and checkpoints','pressure':'DelayBasin should keep same-experiment writeback distinct from derivative restore lanes'},
    {'datacube':'PodmanRepeatedNamedRestore-2026','surfaces':['REF-0883'],'pattern':'the same checkpoint can be restored multiple times with different names and different IP identities','pressure':'DelayBasin should keep repeated named restores distinct from canonical writeback authority'},
    {'datacube':'KubernetesForensicSandboxCopies-2026','surfaces':['REF-0880'],'pattern':'checkpoint copies can be restored multiple times in a sandbox without the original container being aware','pressure':'DelayBasin should keep sandbox-restored output distinct from authoritative continuation and leave promotion policy for the next open seam'}
  ],
  'reviewed_pattern':'current recovery systems repeatedly distinguish canonical same-run writeback from derived branch or sandbox restore lanes whenever restored work might otherwise sound authoritative',
  'import_decision':'supporting-only',
  'adopted_take':'extract one compact recovery-writeback witness and resolve OQ-0135',
  'supporting_only_take':'the current evidence cleanly supports a bounded canonical-vs-branch-vs-sandbox write-authority witness without promoting broader recovery-writeback governance',
  'deferred_or_rejected_take':['recovery-writeback court','promotion senate','sandbox board','standing merge tribunal'],
  'local_gap':'the archive still lacked one compact successor surface for where restored output could write even after recovery identity was explicit',
  'anchor_surfaces':['docs/10-method/recovery-identity-witnesses-continuing-resumes-checkpoint-forked-clones-and-sandbox-restored-branches.md','docs/10-method/recovery-anchor-witnesses-self-lineage-checkpoints-imported-seeds-converted-checkpoints-and-migrated-runtime-images.md','docs/20-constitution/open-question-registry.md','docs/00-meta/trajectory-map.md','docs/90-quarantine/wild-speculations-2026-03-08.md#QWS-0218'],
  'open_question':'OQ-0136','repair':'ordinary-continuation','origin_revision':REV,'action_lane':'keep-compact','gate_class':'concrete-evidence','discharge':'reopen-only-if-recovery-writeback-overflows','revision':REV,'witness_surface':'DATACUBE-TRANSFER-LEDGER.json#TL-0145','transfer_state':'supporting-only',
  'bounded_take':'Keep the archive compact by extracting one recovery-writeback witness over the existing recovery-anchor and recovery-identity surfaces; do not promote a recovery-writeback court, promotion senate, or sandbox board.',
  'explicit_non_take':['no recovery-writeback court','no promotion senate','no sandbox board','no standing merge tribunal'],
  'open_transfer_question':'whether later canonical-vs-branch write-authority maintenance still stays bounded or forces richer promotion or merge-governance machinery',
  'missing_support':'a later public check on whether one compact recovery-writeback witness keeps sufficing or whether repeated branch pressure honestly requires broader governance',
  'current_support':['APPLICABILITY-LEDGER.json#AP-0134','FOREIGN-PRESSURE-LEDGER.json#FP-0139','DATACUBE-TRANSFER-LEDGER.json#TL-0145'],
  'discharge_path':'either show later that one compact recovery-writeback witness keeps sufficing or promote broader recovery-writeback governance explicitly'
}
RS = {
  'id':'RS-0142',
  'title':'resolve OQ-0135 with one compact recovery-writeback witness rather than a recovery-writeback court',
  'state':'resolved','witness_surface':'RESOLUTION-LEDGER.json#RS-0142',
  'resolved_objects':['OQ-0135','AP-0134','FP-0139','TL-0145'],
  'prior_state':'open gap: DelayBasin already had recovery-anchor and recovery-identity witnesses but still lacked one compact successor surface for whether restored output kept canonical write authority, only branch-local authority, or only sandbox isolation.',
  'closure_reason':'rev0240 extracted one compact recovery-writeback witness, kept the admitted recovery-anchor and recovery-identity surfaces narrow, and kept broader promotion-governance stories quarantined.',
  'successor_surface':'docs/10-method/recovery-writeback-witnesses-canonical-writeback-derived-branch-writeback-and-sandbox-isolation.md',
  'reopen_triggers':['later revisions need standing governance over branch promotion, sandbox-to-canonical carryover, or cross-row merge policy that one compact recovery-writeback witness cannot honestly absorb'],
  'closure_state':'resolved','repair':'ordinary-continuation','origin_revision':REV,'action_lane':'keep-compact','gate_class':'concrete-evidence','reopen_trigger':'recovery-writeback pressure overflows one compact successor surface','discharge':'reopen-only-if-recovery-writeback-overflows','revision':REV,
  'target_surfaces':['docs/10-method/recovery-writeback-witnesses-canonical-writeback-derived-branch-writeback-and-sandbox-isolation.md'],
  'question':'whether one compact recovery-writeback witness over the existing recovery-anchor and recovery-identity surfaces is enough for honest canonical-vs-branch write-authority comparison'
}
OB = {
  'id':'OB-0135','title':'when restored output keeps needing canonical writeback distinguished from branch-local or sandbox lanes, DelayBasin should preserve one compact recovery-writeback witness rather than a recovery-writeback court','state':'open','witness_surface':'OBLIGATION-LEDGER.json#OB-0135',
  'target_surfaces':['docs/90-quarantine/wild-speculations-2026-03-08.md#QWS-0218'],
  'missing_support':'a later public check on whether one compact recovery-writeback witness keeps sufficing and whether canonical, branch-local, and sandbox restore lanes stay distinct without broader recovery-writeback governance',
  'current_support':['APPLICABILITY-LEDGER.json#AP-0134','FOREIGN-PRESSURE-LEDGER.json#FP-0139','DATACUBE-TRANSFER-LEDGER.json#TL-0145'],
  'discharge_path':'either show later that one compact recovery-writeback witness keeps sufficing or promote broader recovery-writeback governance explicitly',
  'obligation_state':'open','repair':'ordinary-continuation','origin_revision':REV,'discharge':'reopen-only-if-recovery-writeback-overflows','action_lane':'keep-compact','gate_class':'overflow','revision':REV
}
FB = {
  'id':'FB-0136','title':'the recovery-writeback import should count as one compact canonical-vs-branch authority repair, not as promotion of a recovery-writeback court','state':'withheld','witness_surface':'FIREBREAK-LEDGER.json#FB-0136',
  'judged_property':'the rev0240 decision that DelayBasin should extract one compact recovery-writeback witness over the existing recovery-anchor and recovery-identity surfaces and `recovery_writeback_state` family while the broader recovery-writeback court / promotion senate / sandbox board story remains quarantined',
  'public_extract':['docs/10-method/recovery-writeback-witnesses-canonical-writeback-derived-branch-writeback-and-sandbox-isolation.md','docs/10-method/recovery-identity-witnesses-continuing-resumes-checkpoint-forked-clones-and-sandbox-restored-branches.md','docs/20-constitution/open-question-registry.md','FOREIGN-PRESSURE-LEDGER.json#FP-0139','APPLICABILITY-LEDGER.json#AP-0134','REVISION-RECEIPT.json'],
  'withheld_trace_surface':'same-session drafting residue behind the compact recovery-writeback-witness versus recovery-writeback-court decision','allowed_role':'bounded drafting aid only; not public support for a broader recovery-writeback court, promotion senate, or sandbox board','exposure_rule':'expose or reintegrate only if later passes show that one compact recovery-writeback witness cannot keep canonical-vs-branch write authority bounded','trace_state':'withheld','repair':'ordinary-continuation','origin_revision':REV,'action_lane':'keep-compact','gate_class':'overflow','firebreak_surface':'FIREBREAK-LEDGER.json#FB-0136','discharge':'reopen-only-if-recovery-writeback-overflows','revision':REV,'blocked_object':'standing recovery-writeback court, promotion senate, or sandbox board'
}
FT = {
  'id':'FT-0142','title':'keep checking whether recovery-writeback pressure still fits inside one compact successor surface','state':'queued','blocked_object':'standing recovery-writeback court, promotion senate, or sandbox board','local_surface':'docs/90-quarantine/wild-speculations-2026-03-08.md#QWS-0218','followthrough_state':'queued','boundary':'do not promote bounded recovery-writeback clarification into general promotion-governance machinery','next_proof_surface':'docs/10-method/recovery-writeback-witnesses-canonical-writeback-derived-branch-writeback-and-sandbox-isolation.md','receiving_surface':'FOLLOWTHROUGH-QUEUE.json#FT-0142','repair':'ordinary-continuation','origin_revision':REV,'discharge':'revisit-on-next-real-recovery-writeback-overflow','action_lane':'keep-compact','gate_class':'overflow','blocked_output':'standing recovery-writeback court, promotion senate, or sandbox board','owner_surface':'OBLIGATION-LEDGER.json#OB-0135','revision':REV,'missing_support':'a later public check on whether one compact recovery-writeback witness keeps overflowing the bounded rule and honestly warrants richer recovery-writeback governance','candidate_surface':'docs/90-quarantine/wild-speculations-2026-03-08.md#QWS-0218','blocked_by':'need repeated evidence that canonical-vs-branch write authority overflows one compact recovery-writeback witness'
}
AS = {
  'id':'AS-0139','title':'one compact recovery-writeback witness is enough for now','state':'active','scope':'continuity passes whose current claim depends on restored-output authority while the actual writeback may really be canonical-writeback, branch-local-writeback, sandbox-only, or mixed','invalidation_triggers':['repeated later revisions need standing recovery-writeback governance rather than one compact recovery-writeback witness','the archive needs a recovery-writeback court or promotion senate just to keep canonical-vs-branch write authority legible','recovery cases repeatedly fail to stay distinguishable as canonical-writeback vs branch-local-writeback vs sandbox-only vs mixed-recovery-writeback even with the witness in place'],'assumption_state':'active','repair':'ordinary-continuation','origin_revision':REV,'revision':REV,'assumption':'the current evidence only requires one compact recovery-writeback witness over the existing recovery-anchor and recovery-identity surfaces rather than a standing recovery-writeback court, promotion senate, or sandbox board','supporting_surfaces':['APPLICABILITY-LEDGER.json#AP-0134','DATACUBE-TRANSFER-LEDGER.json#TL-0145','FOREIGN-PRESSURE-LEDGER.json#FP-0139'],'discharge':'discharge when later revisions can keep recovery writeback honest without a dedicated recovery-writeback witness, or retire/quarantine it if broader recovery-writeback governance becomes repeatedly necessary','witness_surface':'ASSUMPTION-LEDGER.json#AS-0139','assumption_surface':'ASSUMPTION-LEDGER.json#AS-0139','assumption_statement':'the current evidence only requires one compact recovery-writeback witness over the existing recovery-anchor and recovery-identity surfaces rather than a standing recovery-writeback court, promotion senate, or sandbox board','action_lane':'keep-compact','gate_class':'concrete-evidence'
}
RT = {
  'id':'RT-0129','title':'revisit whether recovery-identity pressure stayed bounded after rev0239','state':'cooling','candidate_surface':'docs/90-quarantine/wild-speculations-2026-03-08.md#QWS-0217','cooldown_window':'keep the stronger recovery-identity court, clone senate, or sandbox board story cooled until at least one later revision shows that one compact recovery-identity witness is no longer enough.','adjudication_family':'recovery identity / same-run-vs-branch truth / recovery-governance pressure','supersession_link':'OBLIGATION-LEDGER.json#OB-0134','origin_revision':'rev0239','discharge':'keep-cooling-unless-recovery-identity-overflows','action_lane':'keep-compact','gate_class':'overflow','witness_surface':'RETROSPECTIVE-QUEUE.json#RT-0129','revision':'rev0239','cooling_state':'cooling','disposition':'await-adjudication','repair':'keep-cooling'
}

for fname, item in [
    ('APPLICABILITY-LEDGER.json', AP),
    ('FOREIGN-PRESSURE-LEDGER.json', FP),
    ('RESOLUTION-LEDGER.json', RS),
    ('OBLIGATION-LEDGER.json', OB),
    ('FIREBREAK-LEDGER.json', FB),
    ('FOLLOWTHROUGH-QUEUE.json', FT),
    ('ASSUMPTION-LEDGER.json', AS),
    ('RETROSPECTIVE-QUEUE.json', RT),
]:
    obj = json.loads(read(fname))
    obj['revision'] = REV
    obj['items'].append(item)
    write(fname, json.dumps(obj, indent=2) + '\n')

obj = json.loads(read('DATACUBE-TRANSFER-LEDGER.json'))
obj['revision'] = REV
obj['items'].append(TL)
# replace final open question string or append if absent
if isinstance(obj.get('open_questions'), list) and obj['open_questions']:
    obj['open_questions'][-1] = 'Whether a later pass should promote a broader recovery-promotion court or discoverability surface only if several revisions accumulate honest canonical-versus-branch writeback distinctions that the current compact recovery-writeback packet cannot absorb honestly.'
write('DATACUBE-TRANSFER-LEDGER.json', json.dumps(obj, indent=2) + '\n')

# ---------- root revision/status/manifest/changelog/archive ----------
# CHANGELOG
old_header = '## rev0239 - 2026.03.24.00.34 - recoveryidentity / resumeclone / sandbox / norecoveryidentitycourt / forkglass\n\n- Extracted the compact successor surface `docs/10-method/recovery-identity-witnesses-continuing-resumes-checkpoint-forked-clones-and-sandbox-restored-branches.md`, so the archive now resolves `OQ-0134` with one bounded recovery-identity packet that keeps continuing resumes distinct from checkpoint-forked clones and sandbox-restored branches.\n- Bold but disciplined speculative move: quarantined the broader **recovery-identity court / clone senate / sandbox board** story in `QWS-0217` rather than quietly promoting standing lineage governance, while projecting `OQ-0135` as the next honest recovery-writeback frontier.\n- Hygiene: added `tools/check_recovery_identity_witness_contract.py`, factored a shared recovery-lineage packet helper alias in `tools/packet_contract_common.py`, and rewired the recovery-anchor checker onto that helper.\n- Research pressure added from Ray interrupted-run restore vs `resume_from_checkpoint`, Ray Tune existing-run continuation, NeMo unfinished-experiment resume, Podman repeated named restores, and Kubernetes forensic sandbox copies.\n- Ran `make lint` and packaged `DelayBasin-rev0239-2026.03.24.00.34-recoveryidentity-resumeclone-sandbox-forkglass.zip`.\n\n'
new_header = f'''## {REV} - {STAMP} - recoverywriteback / canonbranch / sandbox / norecoverywritebackcourt / mergeglass\n\n- Extracted the compact successor surface `docs/10-method/recovery-writeback-witnesses-canonical-writeback-derived-branch-writeback-and-sandbox-isolation.md`, so the archive now resolves `OQ-0135` with one bounded recovery-writeback packet that keeps canonical writeback distinct from branch-local and sandbox-only restore lanes.\n- Bold but disciplined speculative move: quarantined the broader **recovery-writeback court / promotion senate / sandbox board** story in `QWS-0218` rather than quietly promoting standing promotion governance, while projecting `OQ-0136` as the next honest recovery-promotion frontier.\n- Hygiene: added `tools/check_recovery_writeback_witness_contract.py`, factored a shared recovery-writeback packet helper alias in `tools/packet_contract_common.py`, and rewired the recovery-identity checker onto that helper.\n- Research pressure added from Ray same-location restore writeback, Ray Tune existing-run result-table continuation, BioNeMo experiment-directory autoresume, Podman repeated named restores, and Kubernetes forensic sandbox copies.\n- Ran `make lint` and packaged `{BUNDLE}`.\n\n'''
replace_once('CHANGELOG.md', old_header, new_header)

replace_once('ARCHIVE_INDEX.md',
'| DelayBasin-rev0239-2026.03.24.00.34-recoveryidentity-resumeclone-sandbox-forkglass.zip | 2026-03-24 | Recovery-identity revision: resolved OQ-0134 with a compact same-run-vs-branch packet, quarantined recovery-identity overflow, widened `recovery_identity_state` minimally, and tightened shared recovery-lineage lint. |\n',
'| DelayBasin-rev0240-2026.03.24.00.54-recoverywriteback-canonbranch-sandbox-mergeglass.zip | 2026-03-24 | Recovery-writeback revision: resolved OQ-0135 with a compact canonical-vs-branch authority packet, quarantined recovery-writeback overflow, widened `recovery_writeback_state` minimally, and tightened shared recovery-writeback lint. |\n| DelayBasin-rev0239-2026.03.24.00.34-recoveryidentity-resumeclone-sandbox-forkglass.zip | 2026-03-24 | Recovery-identity revision: resolved OQ-0134 with a compact same-run-vs-branch packet, quarantined recovery-identity overflow, widened `recovery_identity_state` minimally, and tightened shared recovery-lineage lint. |\n')

# release manifest and status
manifest = {'project':'DelayBasin','revision':REV,'timestamp':STAMP,'slug':SLUG,'bundle':BUNDLE}
write('RELEASE-MANIFEST.json', json.dumps(manifest, indent=2)+'\n')
status = json.loads(read('SURFACE-STATUS.json'))
status['operational_head']['revision']=REV
status['status_lanes']['frozen_public_surface']=BUNDLE
status['status_lanes']['current_release_surface']=BUNDLE
status['citation_head']={'revision':REV,'surface':BUNDLE}
status['previous_citation_head']={'revision':PREV,'surface':'DelayBasin-rev0239-2026.03.24.00.34-recoveryidentity-resumeclone-sandbox-forkglass.zip'}
status['revision']=REV
status['stamp']=STAMP
status['slug']=SLUG
write('SURFACE-STATUS.json', json.dumps(status, indent=2)+'\n')

# receipt
receipt = json.loads(read('REVISION-RECEIPT.json'))
receipt['revision']=REV
receipt['previous_revision']=PREV
receipt['summary']='Resolved OQ-0135 by extracting one compact recovery-writeback witness that keeps canonical writeback distinct from branch-local and sandbox-only restore lanes while stronger promotion-governance stories stay honestly quarantined.'
receipt['canon_additions']=['docs/10-method/recovery-writeback-witnesses-canonical-writeback-derived-branch-writeback-and-sandbox-isolation.md','RS-0142 resolved OQ-0135 with one compact recovery-writeback witness']
receipt['quarantine_additions']=['QWS-0218 — recovery-writeback court / promotion senate / sandbox board']
receipt['refs_used']=['REF-0884','REF-0885','REF-0886','REF-0883','REF-0880']
receipt['checks_passed']=['make lint']
receipt['packaged_release']=True
receipt['packaged_bundle_filename']=BUNDLE
receipt['summary_highlight']='sandbox'
receipt['codename']='mergeglass'
receipt['created_at']=STAMP.replace('.', '-', 2).replace('.', '-', 2)  # temp fix then overwrite below
receipt['created_at']='2026-03-24T00:54:00-04:00'
receipt['current_import_id']='TL-0145'
receipt['current_pressure_id']='FP-0139'
receipt['new_classes_or_families']=['recovery_writeback_state']
receipt['quarantined_non_take']=['recovery-writeback court','promotion senate','sandbox board','standing merge tribunal']
# append touched surfaces minimally
extra_surfaces=[
 'docs/10-method/recovery-writeback-witnesses-canonical-writeback-derived-branch-writeback-and-sandbox-isolation.md',
 'docs/00-meta/llm-runbook.md','docs/20-constitution/claim-registry.md','docs/20-constitution/open-question-registry.md','docs/20-constitution/prompt-pair-registry.md','docs/50-promptcraft/prompt-pairs.md','docs/90-quarantine/wild-speculations-2026-03-08.md','docs/00-meta/bibliography.md','tools/packet_contract_common.py','tools/check_recovery_identity_witness_contract.py','tools/check_recovery_writeback_witness_contract.py','WITNESS-VOCABULARY.json','CHANGELOG.md','ARCHIVE_INDEX.md','ASSUMPTION-LEDGER.json','OBLIGATION-LEDGER.json','APPLICABILITY-LEDGER.json','FOREIGN-PRESSURE-LEDGER.json','DATACUBE-TRANSFER-LEDGER.json','RESOLUTION-LEDGER.json','FIREBREAK-LEDGER.json','FOLLOWTHROUGH-QUEUE.json','RETROSPECTIVE-QUEUE.json','REVISION-RECEIPT.json','SURFACE-STATUS.json','RELEASE-MANIFEST.json']
# preserve order unique
seen=[]
new=[]
for x in receipt.get('touched_surfaces',[])+extra_surfaces:
    if x not in seen:
        seen.append(x); new.append(x)
receipt['touched_surfaces']=new
receipt['changes']=['resolved OQ-0135','added recovery_writeback_state family','quarantined broader recovery-writeback governance','refactored recovery writeback helper alias','updated reentry and ledger surfaces']
receipt['basis_witness']['expected_head']='rev0238'
receipt['basis_witness']['observed_head']='rev0238'
receipt['basis_witness']['basis_surfaces']=['docs/10-method/recovery-identity-witnesses-continuing-resumes-checkpoint-forked-clones-and-sandbox-restored-branches.md','docs/20-constitution/open-question-registry.md','docs/00-meta/trajectory-map.md','OBLIGATION-LEDGER.json','WITNESS-VOCABULARY.json']
receipt['basis_witness']['basis_omission_basis']='broader recovery-identity and recovery-writeback governance drafting was intentionally omitted because the evidence only justified one bounded recovery-writeback witness.'
receipt['status_witness']['frozen_public_surface']=BUNDLE
receipt['followthrough_witness']=FT
receipt['assumption_witness']=AS
receipt['obligation_witness']=OB
receipt['applicability_witness']=AP
receipt['foreign_pressure_witness']=FP
receipt['transfer_witness']=TL
receipt['resolution_witness']=RS
receipt['reasoning_firebreak_witness']=FB
receipt['retrospective_write_witness']=RT
receipt['receipt_freshness_witness']={
 'packaged_bundle_filename':BUNDLE,
 'manifest_timestamp_token':STAMP,
 'receipt_timestamp_token':STAMP,
 'bundle_stem_suffix_relation':'summary_highlight and codename now align to the shorter packaged bundle stem `sandbox` / `mergeglass` without stale carryforward from rev0239',
 'current_import_id':'TL-0145',
 'current_pressure_id':'FP-0139',
 'change_anchor_surface':'CHANGELOG.md',
 'freshness_state':'current-aligned',
 'repair':'ordinary-continuation'
}
receipt['question_posture_witness']={
 'selected_focus_id':'OQ-0136',
 'resolved_question_id':'OQ-0135',
 'resolution_surface':'RESOLUTION-LEDGER.json#RS-0142',
 'next_open_question_surface':'docs/20-constitution/open-question-registry.md#oq-0136',
 'question_state':'advanced',
 'repair':'ordinary-continuation'
}
receipt['vocabulary_witness']['surface']='WITNESS-VOCABULARY.json'
receipt['comparison_witness']['anchor_revision']=PREV if isinstance(receipt.get('comparison_witness'),dict) else receipt.get('comparison_witness')
receipt['recovery_writeback_witness']={
 'id':'RWW-0142',
 'surface':'docs/10-method/recovery-writeback-witnesses-canonical-writeback-derived-branch-writeback-and-sandbox-isolation.md',
 'recovery_writeback_state':'canonical-writeback|branch-local-writeback|sandbox-only|mixed-recovery-writeback',
 'repair':'keep-current|narrow-claim|split-row|issue-new-recovery-writeback-witness|quarantine-recovery-writeback-governance'
}
write('REVISION-RECEIPT.json', json.dumps(receipt, indent=2)+'\n')
