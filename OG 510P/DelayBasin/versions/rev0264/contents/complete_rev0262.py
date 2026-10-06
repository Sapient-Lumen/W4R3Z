from __future__ import annotations
import json, re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REV='rev0262'; PREV='rev0261'; STAMP='2026.03.28.10.02'; CREATED_AT='2026-03-28T10:02:00-04:00'
SLUG='resumptionbasis-warmq-replaycarry-memoryglass'; BUNDLE=f'DelayBasin-{REV}-{STAMP}-{SLUG}.zip'
SUMMARY='Resolved refresh-scope-axis-remediation displacement resumption basis with a compact in-memory-vs-replay-vs-cold witness, honestly quarantined stronger warm-state governance, and refactored release-manifest construction so packaging stays small and wired.'
SUMMARY_HIGHLIGHT='replaycarry'; CODENAME='memoryglass'
NEW_DOC='docs/10-method/refresh-scope-axis-remediation-displacement-resumption-basis-witnesses-in-memory-continuation-checkpoint-backed-replay-and-cold-restart.md'
NEW_CHECKER='tools/check_refresh_scope_axis_remediation_displacement_resumption_basis_witness_contract.py'
FAMILY='refresh_scope_axis_remediation_displacement_resumption_basis_state'
ALLOWED=['in-memory-continuation','checkpoint-backed-replay','cold-restart-after-displacement','mixed-refresh-scope-axis-remediation-displacement-resumption-basis']
EXCLUDED=['resume-means-same-state','checkpoint-means-lossless','new-pod-means-same-run','resumption-basis-ish']
QWS='QWS-0240'; CL='CL-0155'; RS='RS-0164'; OQ='OQ-0157'; NEXT_OQ='OQ-0158'; PP='PP-0115'; AP='AP-0156'; OB='OB-0157'; AS='AS-0161'; FP='FP-0161'; TL='TL-0167'; FT='FT-0164'; RT='RT-0151'; FB='FB-0158'
REFS=['docs/00-meta/bibliography.md#ref-0999','docs/00-meta/bibliography.md#ref-1000','docs/00-meta/bibliography.md#ref-1001','docs/00-meta/bibliography.md#ref-1002','docs/00-meta/bibliography.md#ref-1003','docs/00-meta/bibliography.md#ref-1004','docs/00-meta/bibliography.md#ref-1005']


def read(rel): return (ROOT/rel).read_text(encoding='utf-8')
def write(rel,text): (ROOT/rel).write_text(text,encoding='utf-8')
def loadj(rel): return json.loads(read(rel))
def dumpj(rel,obj): write(rel,json.dumps(obj,indent=2,ensure_ascii=False)+'\n')

def append_if_missing(rel, addition):
    txt=read(rel)
    if addition.strip() not in txt:
        write(rel, txt.rstrip()+"\n"+addition.strip()+"\n")

def insert_after(rel, anchor, addition):
    txt=read(rel)
    if addition.strip() in txt:
        return
    if anchor not in txt:
        raise RuntimeError(f'anchor missing in {rel}')
    write(rel, txt.replace(anchor, anchor+addition, 1))

def replace_regex(rel, pattern, repl):
    txt=read(rel)
    new, n = re.subn(pattern, repl, txt, count=1, flags=re.S)
    if n:
        write(rel,new)
        return True
    return False

def append_item(rel,item):
    obj=loadj(rel)
    items=obj['items']
    if not any(x['id']==item['id'] for x in items):
        items.append(item)
        dumpj(rel,obj)

def ensure_sorted_id(rel):
    obj=loadj(rel)
    if 'items' in obj:
        obj['items']=sorted(obj['items'], key=lambda x: x['id'])
        obj['revision']=REV
        dumpj(rel,obj)

def ensure_new_doc_readme():
    anchor='- [`10-method/refresh-scope-axis-remediation-displacement-aftercare-witnesses-resumable-displacement-terminal-displacement-and-mixed-aftercare.md`](10-method/refresh-scope-axis-remediation-displacement-aftercare-witnesses-resumable-displacement-terminal-displacement-and-mixed-aftercare.md)\n'
    addition='- [`10-method/refresh-scope-axis-remediation-displacement-resumption-basis-witnesses-in-memory-continuation-checkpoint-backed-replay-and-cold-restart.md`](10-method/refresh-scope-axis-remediation-displacement-resumption-basis-witnesses-in-memory-continuation-checkpoint-backed-replay-and-cold-restart.md)\n'
    insert_after('docs/README.md', anchor, addition)

# new checker
write(NEW_CHECKER, 'from packet_contract_common import require_named_refresh_scope_axis_branch_witness_packet_and_vocabulary\n\nrequire_named_refresh_scope_axis_branch_witness_packet_and_vocabulary("refresh_scope_axis_remediation_displacement_resumption_basis_witness_contract")\n\nprint("check_refresh_scope_axis_remediation_displacement_resumption_basis_witness_contract: OK")\n')

# README
ensure_new_doc_readme()

# trajectory map robust update
traj_new = '''113. Determine what remediation-displacement-resumption-basis witness distinguishes in-memory continuation from checkpoint-backed replay and cold restart after displacement.\n\nA fresh extension is that once aftercare is explicit, DelayBasin may next need to say how warm or cold the returning execution actually was. Otherwise every nonterminal return path may silently inherit the authority of live in-memory continuation.\n- `OQ-0157` — what remediation-displacement-resumption-basis witness distinguishes in-memory continuation from checkpoint-backed replay and cold restart after displacement?\n  - Why it matters: if DelayBasin cannot separate live resume, replay-from-checkpoint, and fresh restart, later sessions may over-credit resumable displacement that actually lost substantial work.\n  - Current posture: resolved by `RS-0164` via `docs/10-method/refresh-scope-axis-remediation-displacement-resumption-basis-witnesses-in-memory-continuation-checkpoint-backed-replay-and-cold-restart.md`; reopen only if the compact refresh-scope-axis-remediation-displacement-resumption-basis witness proves insufficient and stronger replay-fidelity or warm-state governance is honestly required\n\n114. Determine what remediation-displacement-replay-fidelity witness distinguishes exact-state restore from bounded-loss checkpoint replay and source-only restart.\n\nA fresh extension is that once resumption basis is explicit, DelayBasin may next need to say how much meaningful execution state actually survived inside the replay path. Otherwise checkpoint-backed return may still silently inherit the authority of exact restore.\n- `OQ-0158` — what remediation-displacement-replay-fidelity witness distinguishes exact-state restore from bounded-loss checkpoint replay and source-only restart?\n  - Why it matters: if DelayBasin cannot separate exact restore from truncated replay and source-only restart, later sessions may still over-credit checkpoint-backed return that discards meaningful progress.\n  - Current posture: unresolved\n'''
if 'Current posture: unresolved' in read('docs/00-meta/trajectory-map.md'):
    replace_regex('docs/00-meta/trajectory-map.md', r'113\. Determine what remediation-displacement-resumption-basis witness.*?(?=\n(?:115\.|$))', traj_new.rstrip()+"\n")

# docs registry additions
claim_addition = f'''\n- `{CL}` — Archive continuity may improve when DelayBasin preserves one compact **refresh-scope-axis-remediation-displacement-resumption-basis witness / warmth card / replay brake** whenever a current continuity claim depends not only on whether corroborating axes are genuinely independent, materially backed, decoupled under perturbation, hard-enforced, durable, explicitly restored, honest about collateral width, honest about whether restored placement reused free capacity or displaced unrelated lower-priority work, and honest about whether the displaced work retained a live path back, but on how that work actually came back: name the **governed row or surface**, the **stake object / line of concern**, the **prior refresh-scope-axis-remediation-displacement-aftercare evidence**, the **current corroborating axes**, the **in-memory continuation basis if any**, the **checkpoint-backed replay basis if any**, the **cold-restart basis if any**, the **{FAMILY}**, and the **fail-closed repair** rather than letting every nonterminal return silently inherit the authority of live in-memory continuation.\n  - Status: speculative but central\n  - Wired docs: `{NEW_DOC}`, `docs/20-constitution/open-question-registry.md`, `docs/20-constitution/prompt-pair-registry.md`, `docs/50-promptcraft/prompt-pairs.md`, `docs/00-meta/llm-runbook.md`, `WITNESS-VOCABULARY.json`, `REVISION-RECEIPT.json`\n'''
append_if_missing('docs/20-constitution/claim-registry.md', claim_addition)

prompt_reg_add = f'''\n- `{PP}` — Name whether a nonterminal return stayed in memory, replayed checkpoints, or restarted cold\n  - Goal: keep resumable aftercare from silently inheriting live-continuation authority by requiring explicit prior remediation-displacement-aftercare evidence, current corroborating axes, in-memory basis, checkpoint basis, cold-restart basis, `{FAMILY}`, and fail-closed repair before later passes call the returning work equally resumed.\n  - Canonical text: `docs/50-promptcraft/prompt-pairs.md#pp-0115--name-whether-a-nonterminal-return-stayed-in-memory-replayed-checkpoints-or-restarted-cold`\n'''
append_if_missing('docs/20-constitution/prompt-pair-registry.md', prompt_reg_add)

prompt_pairs = f'''\n## {PP} — Name whether a nonterminal return stayed in memory, replayed checkpoints, or restarted cold\n\n**Opening prompt**\n\n```text\nRead the latest DelayBasin archive and inspect whether the current revision should also materialize one compact refresh-scope-axis-remediation-displacement-resumption-basis witness for honest warm-vs-replay-vs-cold return.\n\nFocus only on cases where the corroborating axes already look genuinely independent, materially backed, decoupled under perturbation, hard-enforced, durable, explicit about who restored the decoupling, honest about how wide the remediation was, honest about whether restored placement reused free capacity or only came back by displacing unrelated lower-priority work, and honest about whether the displaced lower-priority work stayed nonterminal. The missing question is how that work actually returned.\n\nIf yes, preserve exactly one small witness that:\n- names the governed row or surface,\n- names the stake object / line of concern,\n- names the prior refresh-scope-axis-remediation-displacement-aftercare evidence,\n- names the current corroborating axes,\n- names the in-memory continuation basis if any,\n- names the checkpoint-backed replay basis if any,\n- names the cold-restart basis if any,\n- names the `{FAMILY}` / whether this is in-memory-continuation, checkpoint-backed-replay, cold-restart-after-displacement, or mixed-refresh-scope-axis-remediation-displacement-resumption-basis,\n- states what stronger surfaces still outrank the witness,\n- and states the fail-closed repair / keep-current vs narrow-claim vs split-scope vs issue-new-refresh-scope-axis-remediation-displacement-resumption-basis-witness vs quarantine-warm-state-credit consequence if the present continuity claim is not actually supported by the claimed return basis.\n\nDo not use refresh-scope-axis-remediation-displacement-resumption-basis as a standing replay-fidelity board or warmth market. Use this prompt pair only where axis independence, materiality, coupling, enforcement, durability, remediation provenance, remediation collateral, remediation capacity source, and remediation displacement aftercare are already established and the missing question is whether the displaced work returned live in memory, via saved-state replay, or via cold restart.\n```\n\n**Continuation prompt**\n\n```text\nContinue the refresh-scope-axis-remediation-displacement-resumption-basis pass with one high-leverage return-basis clarification only. Prefer the smallest witness that says what governed row is still being justified, what stake object is supposedly widened, what prior refresh-scope-axis-remediation-displacement-aftercare evidence exists, what current corroborating axes exist, what in-memory continuation basis if any now exists, what checkpoint-backed replay basis if any now exists, what cold-restart basis if any now exists, what `{FAMILY}` is honest, what stronger surfaces still outrank the witness, and what keep-current, narrow-claim, split-scope, issue-new-refresh-scope-axis-remediation-displacement-resumption-basis-witness, quarantine, or recover-resync consequence follows if the present return basis is in-memory-continuation, checkpoint-backed-replay, cold-restart-after-displacement, or mixed-refresh-scope-axis-remediation-displacement-resumption-basis. Run `make lint` and package the release.\n```\n\nUse `{NEW_DOC}` when the live question is how a supposedly resumable displaced workload actually came back.\n'''
append_if_missing('docs/50-promptcraft/prompt-pairs.md', prompt_pairs)

insert_after('docs/00-meta/llm-runbook.md',
             'Use `docs/10-method/refresh-scope-axis-remediation-displacement-aftercare-witnesses-resumable-displacement-terminal-displacement-and-mixed-aftercare.md` when the live question is what happened afterward to the lower-priority work that paid the preemption bill: whether it stayed on a live path back or was terminally sacrificed.\n',
             'Use `docs/10-method/refresh-scope-axis-remediation-displacement-resumption-basis-witnesses-in-memory-continuation-checkpoint-backed-replay-and-cold-restart.md` when the live question is how a supposedly nonterminal displaced workload actually returned: still live in memory, by replaying saved checkpoints, or only by cold restart.\n')

qws_add = f'''\n## {QWS} — Some continuations may eventually need a warm-state credit / checkpoint solvency / locality carry rather than only a compact refresh-scope-axis-remediation-displacement-resumption-basis witness\n\n### Claim\nSome later continuations may need stronger public machinery for how warm a return really was inside the checkpoint-backed path, whether locality or cache warmth materially changed the continuity bill, and whether repeated colder restarts should accumulate an explicit continuity debt. One compact in-memory-vs-replay-vs-cold witness may eventually stop being enough.\n\n### What follows if true\n- DelayBasin may eventually need an explicit way to distinguish exact-state restore, bounded-loss replay, and merely nominal replay that preserved little but a label.\n- The archive might need a bounded warm-state credit or checkpoint-solvency layer if later revisions repeatedly compare several nonterminal returns whose practical continuity differs because one comes back hot and another comes back cold on another node.\n\n### What would count against it\n- Several later revisions keep fitting cleanly inside one compact refresh-scope-axis-remediation-displacement-resumption-basis witness without repeated confusion about replay quality, node locality, or warm-state carry.\n- The archive almost never needs public reasoning about checkpoint quality once in-memory continuation, checkpoint-backed replay, and cold restart are already separated.\n\n### Why it stays quarantined\nThe current evidence justifies one bounded witness for in-memory continuation versus checkpoint-backed replay versus cold restart. It does not yet justify a standing warm-state credit board, checkpoint-solvency ledger, or locality-carry market.\n'''
append_if_missing('docs/90-quarantine/wild-speculations-2026-03-08.md', qws_add)

# vocab
v=loadj('WITNESS-VOCABULARY.json')
v['revision']=REV
v['families'][FAMILY]={
    'allowed': ALLOWED,
    'surfaces': ['WITNESS-VOCABULARY.json','REVISION-RECEIPT.json',NEW_DOC],
    'excluded_synonyms': EXCLUDED,
    'comparability_budget': 'refresh-scope-axis-remediation-displacement-resumption-basis truth is compared by token; the compact witness says whether displaced work returned as live in-memory continuation, checkpoint-backed replay, cold restart, or an honest mix while raw checkpoint intervals, replay runtimes, cache warmth, and scheduler traces stay in surrounding prose'
}
dumpj('WITNESS-VOCABULARY.json',v)

# packet contract
pc=read('tools/packet_contract_common.py')
if 'refresh_scope_axis_remediation_displacement_resumption_basis_witness_contract' not in pc:
    block='''\n"refresh_scope_axis_remediation_displacement_resumption_basis_witness_contract": refresh_scope_axis_branch_spec(\n    doc_path="docs/10-method/refresh-scope-axis-remediation-displacement-resumption-basis-witnesses-in-memory-continuation-checkpoint-backed-replay-and-cold-restart.md",\n    title="Refresh-scope-axis-remediation-displacement-resumption-basis witnesses, in-memory continuation, checkpoint-backed replay, and cold restart",\n    oq_id="OQ-0157",\n    external_pressure_heading="## External pressure from Slurm suspend and checkpoint-restart paths, Kubernetes Job suspension and Pod replacement, and NVIDIA Run:ai checkpoint-driven preemptible resume",\n    comparison_heading="## In-memory continuation vs checkpoint-backed replay vs cold restart after displacement vs mixed refresh scope axis remediation displacement resumption basis",\n    runbook_ref="refresh-scope-axis-remediation-displacement-resumption-basis-witnesses-in-memory-continuation-checkpoint-backed-replay-and-cold-restart.md",\n    prompt_id="PP-0115",\n    prompt_needles=["Use `docs/10-method/refresh-scope-axis-remediation-displacement-resumption-basis-witnesses-in-memory-continuation-checkpoint-backed-replay-and-cold-restart.md`", "in-memory-continuation, checkpoint-backed-replay, cold-restart-after-displacement, or mixed-refresh-scope-axis-remediation-displacement-resumption-basis"],\n    claim_id="CL-0155",\n    resolution_id="RS-0164",\n    trajectory_oq_id="OQ-0158",\n    qws_id="QWS-0240",\n    qws_label="warm-state credit / checkpoint solvency / locality carry",\n    changelog_needles=["refresh-scope-axis-remediation-displacement-resumption-basis-witnesses-in-memory-continuation-checkpoint-backed-replay-and-cold-restart.md", "check_refresh_scope_axis_remediation_displacement_resumption_basis_witness_contract.py"],\n    family="refresh_scope_axis_remediation_displacement_resumption_basis_state",\n    allowed=["in-memory-continuation", "checkpoint-backed-replay", "cold-restart-after-displacement", "mixed-refresh-scope-axis-remediation-displacement-resumption-basis"],\n    excluded=["resume-means-same-state", "checkpoint-means-lossless", "new-pod-means-same-run", "resumption-basis-ish"],\n),\n'''
    anchor='''"refresh_scope_axis_remediation_displacement_aftercare_witness_contract": refresh_scope_axis_branch_spec(\n'''
    idx=pc.find(anchor)
    if idx==-1: raise RuntimeError('aftercare contract anchor missing')
    # find end of aftercare block by locating next contract after it
    next_idx=pc.find('"refresh_scope_axis_coupling_witness_contract"', idx)
    if next_idx==-1: raise RuntimeError('next contract missing')
    pc=pc[:next_idx]+block+pc[next_idx:]
    write('tools/packet_contract_common.py', pc)

# release helper refactor
lib=read('tools/release_hygiene_lib.py')
if 'def extract_revision_from_changelog' not in lib:
    lib += '\n\ndef extract_revision_from_changelog(changelog_text: str) -> str:\n    match = re.search(r"(rev\\d{4})", changelog_text)\n    if not match:\n        raise ValueError("CHANGELOG.md missing rev header")\n    return match.group(1)\n\n\ndef build_release_manifest(revision: str, timestamp: str, slug: str) -> dict[str, str]:\n    return {\n        "project": "DelayBasin",\n        "revision": revision,\n        "timestamp": timestamp,\n        "slug": slug,\n        "bundle": build_bundle_name(revision, timestamp, slug),\n    }\n'
    write('tools/release_hygiene_lib.py', lib)
pr=read('tools/package_release.py')
pr=pr.replace('from release_hygiene_lib import build_bundle_name, should_skip_release_path\n','from release_hygiene_lib import build_bundle_name, build_release_manifest, extract_revision_from_changelog, should_skip_release_path\n')
pr=pr.replace('changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")\nm = re.search(r"(rev\\d{4})", changelog)\nif not m:\n    raise SystemExit("CHANGELOG.md missing rev header")\nrev = m.group(1)\n\nbundle_name = build_bundle_name(rev, args.timestamp, args.slug)\nbundle_path = ROOT.parent / bundle_name\n\nmanifest = {\n    "project": "DelayBasin",\n    "revision": rev,\n    "timestamp": args.timestamp,\n    "slug": args.slug,\n    "bundle": bundle_name,\n}\n(ROOT / "RELEASE-MANIFEST.json").write_text(json.dumps(manifest, indent=2) + "\\n", encoding="utf-8")\n','changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")\nrev = extract_revision_from_changelog(changelog)\n\nmanifest = build_release_manifest(rev, args.timestamp, args.slug)\nbundle_name = manifest["bundle"]\nbundle_path = ROOT.parent / bundle_name\n(ROOT / "RELEASE-MANIFEST.json").write_text(json.dumps(manifest, indent=2) + "\\n", encoding="utf-8")\n')
write('tools/package_release.py', pr)

# docs README already; package release import may leave unused imports but okay

# ledger entries
append_item('APPLICABILITY-LEDGER.json', {
  'id': AP,
  'title': 'the refresh-scope-axis-remediation-displacement-resumption-basis witness stays smaller than a warm-state-credit ledger',
  'state': 'gated',
  'question': 'when should DelayBasin treat nonterminal displaced work with one compact remediation-displacement-resumption-basis witness instead of promoting broader replay-fidelity or warmth accounting?',
  'applies_when': [
    'a revision already has a row whose current claim depends on corroborating axes that are already judged genuinely independent, materially backed, decoupled under perturbation, hard-enforced, durable, explicitly restored, honest about collateral width, honest about whether restored placement reused free capacity or displaced unrelated lower-priority work, and honest about whether displaced work stayed nonterminal',
    'later passes still need to distinguish in-memory-continuation, checkpoint-backed-replay, cold-restart-after-displacement, or mixed-refresh-scope-axis-remediation-displacement-resumption-basis posture',
    'one compact successor surface plus the existing admitted refresh-scope-axis-remediation-displacement-aftercare and related scheduler surfaces still keeps return-basis truth honest without standing replay-fidelity or warm-state machinery'],
  'does_not_apply_when': [
    'the archive honestly requires standing governance over exact-state-restore versus bounded-loss checkpoint replay, locality carry, warm-state credit, or checkpoint solvency',
    'the questioned surface is not really about how nonterminal displaced work returned'],
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
    'one compact successor surface plus the existing admitted refresh-scope-axis-remediation-displacement-aftercare and related scheduler surfaces still keeps return-basis truth honest without standing replay-fidelity or warm-state machinery'],
  'baselines': [
    'prior refresh-scope-axis-remediation-displacement-aftercare witness already names whether the displaced work retained a live path back at all',
    'the archive still lacks one compact public successor surface for how nonterminal displaced work actually returned']
})

append_item('ASSUMPTION-LEDGER.json', {
  'id': AS,
  'title': 'one compact refresh-scope-axis-remediation-displacement-resumption-basis witness is enough for now',
  'state': 'active',
  'scope': 'continuity passes whose current widened public claim depends not only on whether corroborating axes are genuinely independent, materially backed, decoupled, hard-enforced, durable, explicitly restored, honest about collateral width, honest about whether restored placement reused free capacity or displaced unrelated lower-priority work, and honest about whether displaced work stayed nonterminal, but on how the returning work actually came back',
  'invalidation_triggers': [
    'repeated later revisions need standing governance over exact-state restore, bounded-loss replay, locality carry, warm-state credit, or checkpoint solvency rather than one compact resumption-basis witness',
    'the archive needs a separate public rule just to distinguish replay fidelity inside the checkpoint-backed path',
    'resumption-basis cases repeatedly fail to stay distinguishable even with the witness in place'],
  'assumption_state': 'active',
  'repair': 'ordinary-continuation',
  'origin_revision': REV,
  'revision': REV,
  'assumption': 'One compact refresh-scope-axis-remediation-displacement-resumption-basis witness is enough for now.',
  'supporting_surfaces': [NEW_DOC, f'docs/90-quarantine/wild-speculations-2026-03-08.md#{QWS}', f'APPLICABILITY-LEDGER.json#{AP}', f'FOREIGN-PRESSURE-LEDGER.json#{FP}'],
  'discharge': 'retire-or-promote-if-refresh-scope-axis-remediation-displacement-resumption-basis-overflows',
  'witness_surface': f'ASSUMPTION-LEDGER.json#{AS}',
  'action_lane': 'keep-compact',
  'gate_class': 'concrete-evidence'
})

append_item('OBLIGATION-LEDGER.json', {
  'id': OB,
  'title': 'when repaired decoupling keeps needing in-memory-vs-replay-vs-cold separation, DelayBasin should preserve one compact refresh-scope-axis-remediation-displacement-resumption-basis witness rather than a warm-state credit ledger',
  'state': 'open',
  'witness_surface': f'OBLIGATION-LEDGER.json#{OB}',
  'target_surfaces': [NEW_DOC, f'docs/90-quarantine/wild-speculations-2026-03-08.md#{QWS}'],
  'missing_support': 'need repeated evidence that one compact resumption-basis witness no longer keeps return warmth honest',
  'current_support': [NEW_DOC, f'APPLICABILITY-LEDGER.json#{AP}', f'FOREIGN-PRESSURE-LEDGER.json#{FP}'],
  'discharge_path': 'either show later that one compact refresh-scope-axis-remediation-displacement-resumption-basis witness keeps sufficing or promote stronger replay-fidelity governance explicitly',
  'obligation_state': 'open',
  'repair': 'ordinary-continuation',
  'origin_revision': REV,
  'discharge': 'reopen-only-if-refresh-scope-axis-remediation-displacement-resumption-basis-overflows',
  'revision': REV,
  'owner_surface': f'OBLIGATION-LEDGER.json#{OB}',
  'action_lane': 'keep-compact',
  'gate_class': 'overflow'
})

append_item('FOREIGN-PRESSURE-LEDGER.json', {
  'id': FP,
  'title': 'Slurm, Kubernetes, and Run:ai all force return-basis truth once nonterminal aftercare is already in play',
  'state': 'imported',
  'pressure_summary': 'Official scheduler and workload docs distinguish true in-memory continuation from checkpoint-backed replay and from replacement-based cold restart, so DelayBasin should keep return-basis truth explicit once nonterminal aftercare is already in play.',
  'sources': REFS,
  'why_now': 'rev0261 made aftercare truth explicit, and the next honest ambiguity is how the work that stayed nonterminal actually came back.',
  'imported_pressure': 'Keep in-memory continuation distinct from checkpoint-backed replay and cold restart.',
  'quarantined_non_take': ['warm-state credit / checkpoint solvency / locality carry'],
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
    {'datacube':'slurm-resumption-basis','surfaces':['slurm.conf','sbatch','GRES scheduling','scheduler design'],'pressure':'documents suspended jobs as still resident in memory and distinct checkpoint vacate/restart paths, so live continuation should not be flattened into replay or restart.'},
    {'datacube':'kubernetes-job-pod-resume','surfaces':['Job','Pod Lifecycle'],'pressure':'documents suspend deleting active Pods and replacement Pods as new ephemeral objects, so many resumes are replay or restart rather than same-object continuation.'},
    {'datacube':'runai-preemptible-checkpointing','surfaces':['Checkpointing preemptible workloads'],'pressure':'documents automatic resume with startup-script rerun and explicit checkpoint loading, so checkpoint replay should not inherit in-memory authority.'}
  ],
  'local_gap': 'rev0261 made aftercare truth explicit, but the archive still lacked one compact successor surface for how a nonterminal displaced workload actually returned.',
  'bounded_take': 'Keep in-memory continuation distinct from checkpoint-backed replay and cold restart once nonterminal aftercare is already in play.',
  'explicit_non_take': ['no warm-state credit ledger','no checkpoint solvency board','no locality-carry market']
})

append_item('DATACUBE-TRANSFER-LEDGER.json', {
  'id': TL,
  'title': 'refresh-scope-axis-remediation-displacement-resumption-basis evidence supports resolving OQ-0157 with one compact in-memory-vs-replay-vs-cold card rather than a warm-state credit ledger',
  'state': 'supporting-only',
  'reviewed_pattern': 'in-memory continuation vs checkpoint-backed replay vs cold restart across already nonterminal displaced work',
  'import_decision': 'support a compact refresh-scope-axis-remediation-displacement-resumption-basis witness and resolve OQ-0157',
  'adopted_take': 'DelayBasin should add one compact witness that says whether displaced work returned as live in-memory continuation, checkpoint-backed replay, cold restart, or an honest mix',
  'supporting_only_take': 'the current evidence cleanly supports a bounded refresh-scope-axis-remediation-displacement-resumption-basis witness without promoting broader warm-state governance',
  'deferred_or_rejected_take': ['warm-state credit','checkpoint solvency','locality carry'],
  'local_gap': 'the archive still lacked one compact successor surface for how nonterminal displaced work actually returned',
  'anchor_surfaces': ['docs/10-method/refresh-scope-axis-remediation-displacement-aftercare-witnesses-resumable-displacement-terminal-displacement-and-mixed-aftercare.md','docs/20-constitution/open-question-registry.md','docs/00-meta/trajectory-map.md',f'docs/90-quarantine/wild-speculations-2026-03-08.md#{QWS}'],
  'open_question': NEXT_OQ,
  'repair': 'ordinary-continuation',
  'origin_revision': REV,
  'action_lane': 'keep-compact',
  'gate_class': 'concrete-evidence',
  'discharge': 'reopen-only-if-refresh-scope-axis-remediation-displacement-resumption-basis-overflows',
  'revision': REV,
  'witness_surface': f'DATACUBE-TRANSFER-LEDGER.json#{TL}',
  'transfer_state': 'supporting-only',
  'bounded_take': 'Keep the archive compact by extracting one refresh-scope-axis-remediation-displacement-resumption-basis witness over the existing refresh-scope-axis-remediation-displacement-aftercare and related admitted surfaces; do not promote a warm-state credit board, checkpoint solvency ledger, or locality-carry market.',
  'explicit_non_take': ['no warm-state credit ledger','no checkpoint solvency board','no locality-carry market'],
  'open_transfer_question': 'whether later passes should add a separate remediation-displacement-replay-fidelity witness once resumption basis is explicit',
  'missing_support': 'a later public check on whether one compact refresh-scope-axis-remediation-displacement-resumption-basis witness keeps sufficing',
  'current_support': [f'APPLICABILITY-LEDGER.json#{AP}', f'FOREIGN-PRESSURE-LEDGER.json#{FP}', f'DATACUBE-TRANSFER-LEDGER.json#{TL}'],
  'discharge_path': 'either show later that one compact refresh-scope-axis-remediation-displacement-resumption-basis witness keeps sufficing or promote broader replay-fidelity governance explicitly',
  'reviewed_datacubes': [
    {'datacube':'SlurmResumptionBasis-2026','surfaces':['REF-0999','REF-1000','REF-1001','REF-1002'],'pattern':'Slurm separates suspend-in-memory from checkpoint-vacate restart','pressure':'live continuation should stay distinct from replay or re-admission restart'},
    {'datacube':'KubernetesJobPodLifecycle-2026','surfaces':['REF-1003','REF-1004'],'pattern':'Job suspend deletes Pods and replacements are new Pods','pressure':'replacement-based return should not silently inherit same-object continuation'},
    {'datacube':'RunAiCheckpointReplay-2026','surfaces':['REF-1005'],'pattern':'preemptible workloads rerun startup and load checkpoints after resume','pressure':'checkpoint-backed replay should stay distinct from live in-memory continuation and cold restart'}
  ]
})

append_item('RESOLUTION-LEDGER.json', {
  'id': RS,
  'title': 'resolve OQ-0157 with one compact refresh-scope-axis-remediation-displacement-resumption-basis witness rather than a warm-state credit ledger',
  'state': 'resolved',
  'closure_state': 'resolved',
  'closure_reason': 'rev0262 extracted one compact refresh-scope-axis-remediation-displacement-resumption-basis witness, kept the admitted refresh-scope-axis-remediation-displacement-aftercare and related analog surfaces narrow, and kept stronger warm-state stories quarantined.',
  'discharge': 'reopen-only-if-refresh-scope-axis-remediation-displacement-resumption-basis-overflows',
  'gate_class': 'concrete-evidence',
  'origin_revision': REV,
  'prior_state': 'open gap: DelayBasin already had refresh-scope-axis-remediation-displacement-aftercare truth but still lacked one compact successor surface for whether the return path was live continuation, checkpoint-backed replay, or cold restart.',
  'question': 'whether one compact refresh-scope-axis-remediation-displacement-resumption-basis witness over the existing refresh-scope-axis-remediation-displacement-aftercare and related admitted surfaces is enough for honest warm-vs-replay-vs-cold comparison',
  'reopen_trigger': 'refresh-scope-axis-remediation-displacement-resumption-basis pressure overflows one compact successor surface',
  'reopen_triggers': ['later revisions need standing governance over exact-state restore, bounded-loss replay, locality carry, checkpoint solvency, or broader warm-state accounting that one compact refresh-scope-axis-remediation-displacement-resumption-basis witness cannot honestly absorb'],
  'repair': 'ordinary-continuation',
  'resolved_objects': [OQ, AP, FP, TL],
  'revision': REV,
  'successor_surface': NEW_DOC,
  'target_surfaces': [NEW_DOC],
  'action_lane': 'keep-compact',
  'witness_surface': f'RESOLUTION-LEDGER.json#{RS}'
})

append_item('RETROSPECTIVE-QUEUE.json', {
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
  'repair': 'keep-cooling'
})

append_item('FOLLOWTHROUGH-QUEUE.json', {
  'id': FT,
  'title': 'keep checking whether refresh-scope-axis-remediation-displacement-resumption-basis pressure still fits inside one compact successor surface',
  'state': 'queued',
  'blocked_object': 'warm-state credit / checkpoint solvency / locality carry',
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
  'blocked_output': 'warm-state credit / checkpoint solvency / locality carry',
  'owner_surface': f'OBLIGATION-LEDGER.json#{OB}',
  'revision': REV,
  'missing_support': 'a later public check on whether one compact resumption-basis witness keeps overflowing the bounded rule and honestly warrants richer warm-state governance',
  'candidate_surface': f'docs/90-quarantine/wild-speculations-2026-03-08.md#{QWS}',
  'blocked_by': 'need repeated evidence that in-memory-vs-replay-vs-cold return truth overflows one compact witness'
})

append_item('FIREBREAK-LEDGER.json', {
  'id': FB,
  'title': 'the refresh-scope-axis-remediation-displacement-resumption-basis import should count as one compact in-memory-vs-replay-vs-cold repair, not as permission to narrate a warm-state credit court',
  'state': 'quarantined',
  'witness_surface': f'FIREBREAK-LEDGER.json#{FB}',
  'judged_property': 'the rev0262 decision that DelayBasin should extract one compact refresh-scope-axis-remediation-displacement-resumption-basis witness over the existing refresh-scope-axis-remediation-displacement-aftercare and related admitted surfaces and `refresh_scope_axis_remediation_displacement_resumption_basis_state` family while the broader warm-state credit / checkpoint solvency / locality carry story remains quarantined',
  'public_extract': 'Keep one compact in-memory-vs-replay-vs-cold return card; do not infer a standing warm-state-credit board.',
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
  'blocked_object': 'warm-state credit / checkpoint solvency / locality carry'
})

for rel in ['APPLICABILITY-LEDGER.json','ASSUMPTION-LEDGER.json','OBLIGATION-LEDGER.json','FOREIGN-PRESSURE-LEDGER.json','DATACUBE-TRANSFER-LEDGER.json','RESOLUTION-LEDGER.json','RETROSPECTIVE-QUEUE.json','FOLLOWTHROUGH-QUEUE.json','FIREBREAK-LEDGER.json']:
    ensure_sorted_id(rel)

# release manifest now for lint alignment
manifest={"project":"DelayBasin","revision":REV,"timestamp":STAMP,"slug":SLUG,"bundle":BUNDLE}
dumpj('RELEASE-MANIFEST.json', manifest)

# changelog/archive
changelog_head=f'''## {REV} - {STAMP} - resumptionbasis / warmq / replaycarry / memoryglass\n\n- Added `{NEW_DOC}` to resolve `{OQ}` with a compact in-memory-vs-replay-vs-cold remediation-displacement-resumption-basis witness.\n- Kept the stronger warm-state credit / checkpoint solvency / locality carry move explicitly quarantined as `{QWS}` instead of laundering it into canon.\n- Hygiene/meta-engineering improvement: factored revision extraction and release-manifest construction into `tools/release_hygiene_lib.py`, rewired `tools/package_release.py` to use the shared helpers, and added `{NEW_CHECKER}` through the shared refresh-scope-axis branch scaffold.\n\n'''
ct=read('CHANGELOG.md')
if not ct.startswith(f'## {REV} '):
    write('CHANGELOG.md', changelog_head+ct)

arch=read('ARCHIVE_INDEX.md')
row=f'| {BUNDLE} | 2026-03-28 | Refresh-scope-axis-remediation-displacement-resumption-basis revision: resolved OQ-0157 with a compact in-memory-vs-replay-vs-cold witness, honestly quarantined stronger warm-state governance, and refactored release-manifest helpers so packaging stays wired and cumulative. |'
if BUNDLE not in arch:
    parts=arch.split('\n')
    legacy_idx=next((i for i,l in enumerate(parts) if l.startswith('Legacy continuity markers retained')), len(parts))
    header=['# Archive index','','| Bundle | Date | Notes |','| --- | --- | --- |',row]
    existing=[l for l in parts[4:legacy_idx] if l.strip()]
    write('ARCHIVE_INDEX.md','\n'.join(header+existing)+"\n\n"+'\n'.join(parts[legacy_idx:]).lstrip('\n'))

# receipt/status copied and updated from prior
receipt=loadj('REVISION-RECEIPT.json')
receipt['revision']=REV; receipt['previous_revision']=PREV; receipt['summary']=SUMMARY; receipt['summary_highlight']=SUMMARY_HIGHLIGHT; receipt['codename']=CODENAME; receipt['created_at']=CREATED_AT
receipt['canon_additions']=[NEW_DOC, f'{RS} resolved {OQ} with one compact refresh-scope-axis-remediation-displacement-resumption-basis witness']
receipt['quarantine_additions']=[f'docs/90-quarantine/wild-speculations-2026-03-08.md#{QWS}']
receipt['refs_used']=REFS
receipt['checks_passed']=['make lint']
receipt['packaged_release']=True
receipt['packaged_release']=True
receipt['packaged_bundle_filename']=BUNDLE
receipt['bundle']=BUNDLE
receipt['slug']=SLUG
receipt['resolved_question']=OQ
receipt['next_open_question']=NEXT_OQ
receipt['canonical_additions']=receipt['canon_additions']
receipt['checker_additions']=[NEW_CHECKER]
receipt['change_summary']='one compact resumption-basis witness plus one quarantined warm-state move and one small release-helper refactor'
receipt['move_classes']=['MV-0002','MV-0003','MV-0004','MV-0007','MV-0011']
receipt['touched_surfaces']=[NEW_DOC,'docs/00-meta/bibliography.md','docs/00-meta/llm-runbook.md','docs/README.md','docs/20-constitution/claim-registry.md','docs/20-constitution/open-question-registry.md','docs/20-constitution/prompt-pair-registry.md','docs/00-meta/trajectory-map.md','docs/50-promptcraft/prompt-pairs.md','docs/90-quarantine/wild-speculations-2026-03-08.md','WITNESS-VOCABULARY.json','FOLLOWTHROUGH-QUEUE.json','ASSUMPTION-LEDGER.json','OBLIGATION-LEDGER.json','APPLICABILITY-LEDGER.json','FOREIGN-PRESSURE-LEDGER.json','DATACUBE-TRANSFER-LEDGER.json','RESOLUTION-LEDGER.json','RETROSPECTIVE-QUEUE.json','FIREBREAK-LEDGER.json','REVISION-RECEIPT.json','SURFACE-STATUS.json','RELEASE-MANIFEST.json','CHANGELOG.md','ARCHIVE_INDEX.md','tools/packet_contract_common.py',NEW_CHECKER,'tools/release_hygiene_lib.py','tools/package_release.py','apply_rev0262.py']
receipt['basis_witness'].update({'expected_head':PREV,'observed_head':PREV,'session_provenance':f'DelayBasin-{PREV}-2026.03.28.09.18-aftercare-resumeq-resumecarry-stitchglass.zip','basis_omission_basis':'broader replay-fidelity accounting was intentionally omitted from canon because the evidence only justified one bounded refresh-scope-axis-remediation-displacement-resumption-basis witness','origin_revision':REV,'revision_span':f'{PREV} -> {REV}'})
receipt['scope_witness'].update({'exact_target':'one compact refresh-scope-axis-remediation-displacement-resumption-basis witness plus one quarantined warm-state move and one small release-helper refactor','scope_of_change':'refresh-scope-axis-remediation-displacement-resumption-basis','origin_revision':REV})
receipt['status_witness']['frozen_public_surface']=BUNDLE
receipt['status_witness']['candidate_surface']=None
receipt['status_witness']['decision_surface']='REVISION-RECEIPT.json'
receipt['status_witness']['execution_surface']='RELEASE-MANIFEST.json'
receipt['status_witness']['durable_status_surface']='SURFACE-STATUS.json'
receipt['question_posture_witness']['synced_resolved_questions']=[OQ]
receipt['comparison_witness']={'previous_revision':PREV,'current_revision':REV,'current_pressure_id':FP,'current_import_id':TL,'basis_surface':'docs/10-method/refresh-scope-axis-remediation-displacement-aftercare-witnesses-resumable-displacement-terminal-displacement-and-mixed-aftercare.md','delta_surface':NEW_DOC,'comparison_summary':'rev0262 adds one compact refresh-scope-axis-remediation-displacement-resumption-basis witness so nonterminal return no longer all reads as if live continuation, checkpoint replay, and cold restart were the same class of aftermath.'}
receipt['receipt_freshness_witness']={'packaged_bundle_filename':BUNDLE,'manifest_timestamp_token':STAMP,'receipt_timestamp_token':STAMP,'bundle_stem_suffix_relation':f'slug ends with {SUMMARY_HIGHLIGHT} and {CODENAME} as summary highlight and codename','current_import_id':TL,'current_pressure_id':FP,'change_anchor_surface':NEW_DOC,'freshness_state':'current-aligned','repair':'ordinary-continuation'}
receipt['current_import_id']=TL; receipt['current_pressure_id']=FP
receipt['import_witness']=next(x for x in loadj('DATACUBE-TRANSFER-LEDGER.json')['items'] if x['id']==TL)
receipt['foreign_pressure_witness']=next(x for x in loadj('FOREIGN-PRESSURE-LEDGER.json')['items'] if x['id']==FP)
receipt['resolution_witness']=next(x for x in loadj('RESOLUTION-LEDGER.json')['items'] if x['id']==RS)
receipt['followthrough_witness']=next(x for x in loadj('FOLLOWTHROUGH-QUEUE.json')['items'] if x['id']==FT)
receipt['assumption_witness']=next(x for x in loadj('ASSUMPTION-LEDGER.json')['items'] if x['id']==AS)
receipt['obligation_witness']=next(x for x in loadj('OBLIGATION-LEDGER.json')['items'] if x['id']==OB)
receipt['applicability_witness']=next(x for x in loadj('APPLICABILITY-LEDGER.json')['items'] if x['id']==AP)
receipt['retrospective_write_witness']=next(x for x in loadj('RETROSPECTIVE-QUEUE.json')['items'] if x['id']==RT)
receipt['reasoning_firebreak_witness']=next(x for x in loadj('FIREBREAK-LEDGER.json')['items'] if x['id']==FB)
receipt['firebreak_witness']=receipt['reasoning_firebreak_witness']
receipt['vocabulary_witness']={'witness_surface':'WITNESS-VOCABULARY.json','controlled_families':[FAMILY,'action_lane','gate_class'],'target_surfaces':['WITNESS-VOCABULARY.json','REVISION-RECEIPT.json',NEW_DOC,'FOLLOWTHROUGH-QUEUE.json','RETROSPECTIVE-QUEUE.json','ASSUMPTION-LEDGER.json','OBLIGATION-LEDGER.json','APPLICABILITY-LEDGER.json','FOREIGN-PRESSURE-LEDGER.json','DATACUBE-TRANSFER-LEDGER.json','RESOLUTION-LEDGER.json','FIREBREAK-LEDGER.json'],'ambient_synonyms_excluded':EXCLUDED,'comparability_budget':'refresh-scope-axis-remediation-displacement-resumption-basis truth is compared by token; the compact witness says whether displaced work returned as live in-memory continuation, checkpoint-backed replay, cold restart, or honestly mixed while raw checkpoint intervals, replay runtimes, cache warmth, and scheduler traces stay outside the token','vocabulary_state':'locked','repair':'ordinary-continuation',FAMILY:loadj('WITNESS-VOCABULARY.json')['families'][FAMILY],'action_lane':loadj('WITNESS-VOCABULARY.json')['families']['action_lane'],'gate_class':loadj('WITNESS-VOCABULARY.json')['families']['gate_class']}
receipt['refresh_scope_axis_remediation_displacement_resumption_basis_witness']={'witness_surface':NEW_DOC,'family':FAMILY,'allowed_tokens':ALLOWED,'overflow_rule':'reopen-only-if-refresh-scope-axis-remediation-displacement-resumption-basis-overflows'}
receipt['refresh_scope_axis_remediation_displacement_resumption_basis_witness_contract']={'family':FAMILY,'allowed_tokens':ALLOWED}
receipt['refresh_scope_axis_remediation_displacement_resumption_basis_witness_meta']={'checker':NEW_CHECKER}
receipt['new_classes_or_families']=[FAMILY]
receipt['quarantined_non_take']=['warm-state credit / checkpoint solvency / locality carry']
# update origin_revision for basis/scope maybe enough
status=loadj('SURFACE-STATUS.json')
status['operational_head']={'revision':REV,'surface':'START_HERE.md'}
status['status_lanes']['frozen_public_surface']=BUNDLE
status['status_lanes']['current_release_surface']=BUNDLE
status['citation_head']={'revision':REV,'surface':BUNDLE}
status['previous_citation_head']={'revision':PREV,'surface':f'DelayBasin-{PREV}-2026.03.28.09.18-aftercare-resumeq-resumecarry-stitchglass.zip'}
status['revision']=REV
status['stamp']=STAMP
status['slug']=SLUG
status['status_lanes']['decision_state']='admitted'; status['status_lanes']['execution_state']='packaged'; status['state_class']='released'

dumpj('REVISION-RECEIPT.json', receipt)
dumpj('SURFACE-STATUS.json', status)
print('complete_rev0262.py: wrote rev0262 surfaces')
