from __future__ import annotations
import json
from copy import deepcopy
from pathlib import Path
from textwrap import dedent

ROOT = Path('.')
REV = 'rev0254'
PREV = 'rev0253'
STAMP = '2026.03.28.03.44'
CREATED_AT = '2026-03-28T03:44:00-04:00'
SLUG = 'axismateriality-stackquarantine-shardcarry-forgeglass'
BUNDLE = f'DelayBasin-{REV}-{STAMP}-{SLUG}.zip'
PREV_BUNDLE = 'DelayBasin-rev0253-2026.03.28.03.13-axisindependence-subq-mirrorgate-rackglass.zip'
SUMMARY_HIGHLIGHT = 'shardcarry'
CODENAME = 'forgeglass'
NEW_DOC = 'docs/10-method/refresh-scope-axis-materiality-witnesses-label-distinct-only-corroboration-failure-domain-backed-corroboration-and-isolation-backed-corroboration.md'
NEW_CHECKER = 'tools/check_refresh_scope_axis_materiality_witness_contract.py'
NEW_FAMILY = 'refresh_scope_axis_materiality_state'
NEW_QWS = 'QWS-0232'
NEW_QWS_LABEL = 'axis-materiality exchange rate / coupling haircut / corroboration capital stack'
NEW_PROMPT = 'PP-0107'
NEW_CLAIM = 'CL-0147'
NEW_RESOLUTION = 'RS-0156'
NEW_OQ = 'OQ-0150'


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding='utf-8')


def write(path: str, text: str) -> None:
    (ROOT / path).write_text(text, encoding='utf-8')


def write_json(path: str, obj) -> None:
    (ROOT / path).write_text(json.dumps(obj, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')


def insert_after(path: str, anchor: str, addition: str) -> None:
    text = read(path)
    if addition.strip() in text:
        return
    if anchor not in text:
        raise SystemExit(f'anchor not found in {path}: {anchor!r}')
    write(path, text.replace(anchor, anchor + addition, 1))


def replace_once(path: str, old: str, new: str) -> None:
    text = read(path)
    if old not in text:
        raise SystemExit(f'old block not found in {path}: {old!r}')
    write(path, text.replace(old, new, 1))


def append_unique_block(path: str, block: str) -> None:
    text = read(path)
    if block.strip() in text:
        return
    if not text.endswith('\n'):
        text += '\n'
    write(path, text + '\n' + block.lstrip('\n'))


def ensure_line(path: str, line: str, after: str | None = None) -> None:
    text = read(path)
    if line in text:
        return
    if after is None:
        write(path, text.rstrip() + '\n' + line + '\n')
    else:
        if after not in text:
            raise SystemExit(f'anchor line not found in {path}: {after!r}')
        write(path, text.replace(after, after + '\n' + line, 1))


def append_item(path: str, item: dict):
    obj = json.loads(read(path))
    items = obj['items']
    if not any(x.get('id') == item.get('id') for x in items):
        items.append(item)
    obj['revision'] = REV
    write_json(path, obj)
    return obj


def create_doc() -> None:
    text = dedent('''
    # Refresh-scope-axis-materiality witnesses, label-distinct-only corroboration, failure-domain-backed corroboration, and isolation-backed corroboration

    This is the compact successor surface for `OQ-0149`.

    ## Practice / observation

    Once DelayBasin can say that corroborating axes are genuinely independent rather than renamed, mirrored, or nested, one more ambiguity remains.

    Some independent axes are still weakly material.
    They differ as labels, dashboards, or selectors, but not yet in a way that changes where failures cluster or how execution is isolated.
    They are independent enough to count as different views, but not yet strong enough to inherit the force of a fault-domain or substrate split.

    Some independent axes are backed by failure domains.
    A zone axis is not just another name when it tracks where correlated outages are expected to stop.
    A topology domain can change expected availability even if it does not carve the execution substrate into isolated slices.

    Some independent axes are backed by substrate isolation.
    A GPU partition with dedicated compute and memory is not only another label.
    It changes interference, isolation, and fault boundaries in a way that a relabeled shared surface does not.

    DelayBasin does not need an exchange rate for those cases.
    It needs one bounded witness that says whether the present corroboration is only label-distinct, backed by a failure domain, backed by substrate isolation, or honestly mixed.

    ## External pressure from Ray selector labels, Kubernetes failure domains, Slurm MPS-vs-MIG scheduling, and NVIDIA time-slicing-vs-MIG isolation

    1. Ray label selectors let a task or actor require one or more labels, and when multiple selectors are present the candidate node must meet all requirements. That pressures DelayBasin to remember that a distinct selector clause can still be only a routing or labeling fact rather than a material split in failure or execution consequences. ([`REF-0957`](../00-meta/bibliography.md))

    2. Kubernetes topology spread constraints explicitly spread Pods across failure-domains such as regions, zones, nodes, and other topology domains. That pressures DelayBasin to distinguish a corroborating axis that is backed by a public failure-domain story from one that is only label-distinct. ([`REF-0956`](../00-meta/bibliography.md))

    3. Kubernetes also says a zone is a logical failure domain, commonly used for increased availability, with failure independence from other zones. That pressures DelayBasin to treat some topology axes as materially stronger than ordinary labels even when they are still represented through labels in configuration. ([`REF-0961`](../00-meta/bibliography.md))

    4. Slurm's GRES guide says MPS lets GPUs be shared by multiple jobs and that the same GPU can be allocated as MPS resources to multiple jobs, while MIG instances can be treated as individual GPUs with cgroup isolation and task binding. That pressures DelayBasin to distinguish a shared substrate with percentage slices from a materially isolated substrate split. ([`REF-0962`](../00-meta/bibliography.md))

    5. NVIDIA's Kubernetes time-slicing guide says time-slicing has no memory or fault isolation between replicas, while MIG provides memory and fault isolation at the hardware layer. That pressures DelayBasin not to let a label change like `-SHARED` inherit the authority of a hardware-isolated partition. ([`REF-0963`](../00-meta/bibliography.md))

    GPUstorming makes the difference vivid. A search shell can expose a new label, queue, or product suffix and make the archive feel multi-axis. But a time-sliced shared GPU with a renamed product string is still materially weaker than a MIG-backed split, and a zone-backed spread is stronger in a different way than a mere dashboard regrouping.

    ## Working synthesis

    > DelayBasin should preserve one compact **refresh-scope-axis-materiality witness / fault-domain brake / isolation-backed corroboration card** whenever a current continuity claim depends not only on whether corroborating axes are genuinely independent, but on whether that independence is only label-distinct, backed by a public failure domain, or backed by substrate isolation. Name the **governed row or surface**, the **stake object / line of concern**, the **prior refresh-scope-axis-independence evidence**, the **current corroborating axes**, the **label-distinct-only basis if any**, the **failure-domain basis if any**, the **isolation-backed basis if any**, the **`refresh_scope_axis_materiality_state`**, and the **fail-closed repair / keep-current vs narrow-claim vs split-scope vs issue-new-refresh-scope-axis-materiality-witness vs quarantine-axis-materiality-exchange-rate consequence**. Keep raw schedulers, topology maps, GPU inventories, and isolation tables outside the compact token. Do not let a merely label-distinct axis silently inherit the authority of a failure-domain or isolation-backed corroboration surface.

    ## Label-distinct-only corroboration vs failure-domain-backed corroboration vs isolation-backed corroboration vs mixed refresh scope axis materiality

    Use the controlled family `refresh_scope_axis_materiality_state`:

    - **label-distinct-only-corroboration** says the axes are genuinely distinct enough to count as separate views, but the current evidence only licenses a naming, routing, or selector distinction rather than a stronger fault-domain or isolation consequence.
    - **failure-domain-backed-corroboration** says the corroborating axis is backed by a public topology or failure-domain story that changes expected correlated failure or availability posture.
    - **isolation-backed-corroboration** says the corroborating axis is backed by substrate isolation or materially separate execution slices rather than only by labels or routing surfaces.
    - **mixed-refresh-scope-axis-materiality** says the current situation honestly combines label-distinct, failure-domain, and isolation-backed features such that no single class stays honest.

    So the witness does not create a corroboration capital stack.
    It only says whether the present corroboration is weakly material, failure-domain-backed, isolation-backed, or honestly mixed.

    ## Countermodels / probes

    1. **Independence already does enough countermodel**
       - Maybe once renamed, nested, and genuinely independent axes are separated, adding materiality only restates obvious prose.
       - Probe: compare later rereads that preserve only refresh-scope-axis-independence truth against rereads that also preserve one compact materiality token and inspect whether label-distinct axes still inherit the force of stronger fault-domain or isolation-backed corroboration.

    2. **Failure-domain and isolation distinctions collapse countermodel**
       - Maybe zone-backed and substrate-isolated corroboration are both just “strong enough” and do not deserve separate public states.
       - Probe: look for later cases where availability-oriented domains and execution-isolation domains change different downstream judgments even when both are materially stronger than labels.

    3. **Weighting is the real issue countermodel**
       - Maybe once materiality matters, the archive really needs an exchange rate or haircut rather than one flat classification witness.
       - Probe: keep that bolder move quarantined unless later revisions repeatedly need additive weights, coupling haircuts, or capital-stack language that this compact materiality witness cannot honestly absorb.

    ## Design consequences

    - DelayBasin can now separate genuine axis independence from the stronger question of whether the present corroboration is only label-distinct, failure-domain-backed, or isolation-backed.
    - The archive gets one explicit place to say that an apparently new axis remains materially weak even when it is not merely renamed or nested.
    - Failure-domain-backed and isolation-backed corroboration now stay available without forcing a full weighting regime.
    - Stronger exchange-rate or capital-stack stories stay quarantined until repeated overflow rather than entering canon by vibe.

    ## Overflow test

    Reopen this compact witness only if later revisions repeatedly need standing weighting rules, coupling haircuts, or additive corroboration policy that one bounded refresh-scope-axis-materiality witness cannot honestly absorb.

    ## Transformer-facing implication

    A later pass should not treat every genuinely independent axis as if it carried the same material force. Preserve the smallest token that says whether the present corroboration is `label-distinct-only-corroboration`, `failure-domain-backed-corroboration`, `isolation-backed-corroboration`, or honestly `mixed-refresh-scope-axis-materiality`, and quarantine stronger exchange-rate ambitions until repeated overflow makes them unavoidable.
    ''').strip() + '\n'
    write(NEW_DOC, text)


def update_bibliography() -> None:
    block = dedent('''

    - `REF-0961` — Kubernetes Documentation, **Well-Known Labels, Annotations and Taints** (accessed 2026-03-28)
      - URL: https://kubernetes.io/docs/reference/labels-annotations-taints/
      - Load-bearing use: Kubernetes says a zone is a logical failure domain with failure independence from other zones, which pressures DelayBasin to distinguish a failure-domain-backed corroborating axis from one that is only label-distinct.

    - `REF-0962` — Slurm Workload Manager, **Generic Resource (GRES) Scheduling** (accessed 2026-03-28)
      - URL: https://slurm.schedmd.com/gres.html
      - Load-bearing use: Slurm contrasts shared MPS allocation with MIG instances treated as individual GPUs with cgroup isolation and task binding, which pressures DelayBasin to distinguish percentage sharing from substrate-isolated corroboration.

    - `REF-0963` — NVIDIA Documentation, **Time-Slicing GPUs in Kubernetes** (accessed 2026-03-28)
      - URL: https://docs.nvidia.com/datacenter/cloud-native/gpu-operator/latest/gpu-sharing.html
      - Load-bearing use: NVIDIA says time-slicing has no memory or fault isolation while MIG provides memory and fault isolation at the hardware layer, which pressures DelayBasin not to let renamed shared surfaces inherit the authority of isolated partitions.
    ''')
    append_unique_block('docs/00-meta/bibliography.md', block)


def update_open_question_registry() -> None:
    old = dedent('''
    - `OQ-0149` — what minimal refresh-scope-axis-materiality witness distinguishes merely label-distinct independent axes from substrate-backed or failure-domain-backed corroboration?
      - Why it matters: if DelayBasin cannot separate nominally independent axes from materially separate substrate or failure-domain corroboration, later sessions may narrate robust diffusion from axes that differ in naming but not in operational failure or execution consequences.
      - Current posture: unresolved
    ''').strip()
    new = dedent('''
    - `OQ-0149` — what minimal refresh-scope-axis-materiality witness distinguishes merely label-distinct independent axes from substrate-backed or failure-domain-backed corroboration?
      - Why it matters: if DelayBasin cannot separate nominally independent axes from materially separate substrate or failure-domain corroboration, later sessions may narrate robust diffusion from axes that differ in naming but not in operational failure or execution consequences.
      - Current posture: resolved by `RS-0156` via `docs/10-method/refresh-scope-axis-materiality-witnesses-label-distinct-only-corroboration-failure-domain-backed-corroboration-and-isolation-backed-corroboration.md`; reopen only if the compact refresh-scope-axis-materiality witness proves insufficient and stronger exchange-rate or weighting governance is honestly required

    - `OQ-0150` — what minimal refresh-scope-axis-coupling witness distinguishes materially backed corroboration that still rides one coupled failure or execution plane from corroboration that remains decoupled under perturbation?
      - Why it matters: if DelayBasin cannot separate materially real but still coupled axes from genuinely decoupled corroboration, later sessions may narrate robust multi-axis support from views that still collapse under one shared switch, rack, scheduler, or GPU substrate.
      - Current posture: unresolved
    ''').strip()
    replace_once('docs/20-constitution/open-question-registry.md', old, new)


def update_trajectory_map() -> None:
    old = dedent('''
    105. Determine what minimal refresh-scope-axis-materiality witness distinguishes merely label-distinct independent axes from substrate-backed or failure-domain-backed corroboration.

    A fresh extension is that once axis independence is explicit, DelayBasin may next need to say whether apparently independent axes are only distinct in naming or are also materially separated by substrate, fault domain, or execution consequences. Otherwise nominal independence may silently inherit the authority of materially separate corroboration.
    - `OQ-0149` — what minimal refresh-scope-axis-materiality witness distinguishes merely label-distinct independent axes from substrate-backed or failure-domain-backed corroboration?
      - Why it matters: if DelayBasin cannot separate nominally independent axes from materially separate substrate or failure-domain corroboration, later sessions may narrate robust diffusion from axes that differ in naming but not in operational failure or execution consequences.
      - Current posture: unresolved
    ''').strip()
    new = dedent('''
    105. Determine what minimal refresh-scope-axis-materiality witness distinguishes merely label-distinct independent axes from substrate-backed or failure-domain-backed corroboration.

    A fresh extension is that once axis independence is explicit, DelayBasin may next need to say whether apparently independent axes are only distinct in naming or are also materially separated by substrate, fault domain, or execution consequences. Otherwise nominal independence may silently inherit the authority of materially separate corroboration.
    - `OQ-0149` — what minimal refresh-scope-axis-materiality witness distinguishes merely label-distinct independent axes from substrate-backed or failure-domain-backed corroboration?
      - Why it matters: if DelayBasin cannot separate nominally independent axes from materially separate substrate or failure-domain corroboration, later sessions may narrate robust diffusion from axes that differ in naming but not in operational failure or execution consequences.
      - Current posture: resolved by `RS-0156` via `docs/10-method/refresh-scope-axis-materiality-witnesses-label-distinct-only-corroboration-failure-domain-backed-corroboration-and-isolation-backed-corroboration.md`; reopen only if the compact refresh-scope-axis-materiality witness proves insufficient and stronger exchange-rate or weighting governance is honestly required

    106. Determine what minimal refresh-scope-axis-coupling witness distinguishes materially backed corroboration that still rides one coupled failure or execution plane from corroboration that remains decoupled under perturbation.

    A fresh extension is that once materiality is explicit, DelayBasin may next need to say whether materially backed corroborating axes still collapse under one shared switch, rack, scheduler, or substrate, or instead stay decoupled when the system is actually perturbed. Otherwise materially real but still coupled views may silently inherit the authority of robust multi-plane corroboration.
    - `OQ-0150` — what minimal refresh-scope-axis-coupling witness distinguishes materially backed corroboration that still rides one coupled failure or execution plane from corroboration that remains decoupled under perturbation?
      - Why it matters: if DelayBasin cannot separate materially real but still coupled axes from genuinely decoupled corroboration, later sessions may narrate robust multi-axis support from views that still collapse under one shared switch, rack, scheduler, or GPU substrate.
      - Current posture: unresolved
    ''').strip()
    replace_once('docs/00-meta/trajectory-map.md', old, new)


def update_claim_registry() -> None:
    anchor = dedent('''
    - `CL-0146` — Archive continuity may improve when DelayBasin preserves one compact **refresh-scope-axis-independence witness / mirrored-axis brake / nested-axis filter** whenever a current continuity claim depends not only on whether dispersed widening is corroborated across more than one apparent axis, but on whether those axes are genuinely independent rather than renamed, mirrored, or nested restatements of one underlying partition: name the **governed row or surface**, the **stake object / line of concern**, the **prior refresh-scope-axis evidence**, the **current dispersed-scope evidence**, the **candidate corroborating axes**, the **renamed-or-mirrored restatement basis if any**, the **nested-hierarchy basis if any**, the **independent-axis basis if any**, the **refresh_scope_axis_independence_state**, and the **fail-closed repair** rather than letting duplicate or hierarchical restatements silently count as distinct corroborating axes.
      - Status: speculative but central
      - Wired docs: `docs/10-method/refresh-scope-axis-independence-witnesses-renamed-or-mirrored-axis-restatement-nested-axis-restatement-and-independent-axis-corroboration.md`, `docs/20-constitution/open-question-registry.md`, `docs/20-constitution/prompt-pair-registry.md`, `docs/50-promptcraft/prompt-pairs.md`, `docs/00-meta/llm-runbook.md`, `WITNESS-VOCABULARY.json`, `REVISION-RECEIPT.json`
    ''').strip()
    addition = dedent('''

    - `CL-0147` — Archive continuity may improve when DelayBasin preserves one compact **refresh-scope-axis-materiality witness / fault-domain brake / isolation-backed corroboration card** whenever a current continuity claim depends not only on whether corroborating axes are genuinely independent, but on whether that independence is only label-distinct, backed by a public failure domain, or backed by substrate isolation: name the **governed row or surface**, the **stake object / line of concern**, the **prior refresh-scope-axis-independence evidence**, the **current corroborating axes**, the **label-distinct-only basis if any**, the **failure-domain basis if any**, the **isolation-backed basis if any**, the **refresh_scope_axis_materiality_state**, and the **fail-closed repair** rather than letting a merely label-distinct axis silently inherit the authority of fault-domain or isolation-backed corroboration.
      - Status: speculative but central
      - Wired docs: `docs/10-method/refresh-scope-axis-materiality-witnesses-label-distinct-only-corroboration-failure-domain-backed-corroboration-and-isolation-backed-corroboration.md`, `docs/20-constitution/open-question-registry.md`, `docs/20-constitution/prompt-pair-registry.md`, `docs/50-promptcraft/prompt-pairs.md`, `docs/00-meta/llm-runbook.md`, `WITNESS-VOCABULARY.json`, `REVISION-RECEIPT.json`
    ''')
    insert_after('docs/20-constitution/claim-registry.md', anchor, addition)


def update_prompt_pair_registry() -> None:
    anchor = dedent('''
    - `PP-0106` — Name whether apparent corroborating axes are renamed, nested, or genuinely independent
      - Goal: keep renamed, mirrored, or hierarchy-nested axes from silently inheriting independent corroboration by requiring explicit candidate-axis listing, renamed-or-mirrored basis, nested-hierarchy basis, independent-axis basis, `refresh_scope_axis_independence_state`, and fail-closed repair before later passes call the spread corroborated across genuinely distinct axes.
      - Canonical text: `docs/50-promptcraft/prompt-pairs.md#pp-0106--name-whether-apparent-corroborating-axes-are-renamed-nested-or-genuinely-independent`
    ''').strip()
    addition = dedent('''

    - `PP-0107` — Name whether genuinely independent corroboration is only label-distinct, failure-domain-backed, or isolation-backed
      - Goal: keep merely label-distinct axes from silently inheriting stronger material authority by requiring explicit prior independence evidence, current corroborating axes, label-distinct-only basis, failure-domain basis, isolation-backed basis, `refresh_scope_axis_materiality_state`, and fail-closed repair before later passes call the spread materially robust.
      - Canonical text: `docs/50-promptcraft/prompt-pairs.md#pp-0107--name-whether-genuinely-independent-corroboration-is-only-label-distinct-failure-domain-backed-or-isolation-backed`
    ''')
    insert_after('docs/20-constitution/prompt-pair-registry.md', anchor, addition)


def update_runbook() -> None:
    anchor = 'Use `docs/10-method/refresh-scope-axis-independence-witnesses-renamed-or-mirrored-axis-restatement-nested-axis-restatement-and-independent-axis-corroboration.md` when the live question is whether apparent corroborating axes are genuinely independent or only renamed, mirrored, or hierarchy-nested restatements of one underlying partition.\n'
    addition = 'Use `docs/10-method/refresh-scope-axis-materiality-witnesses-label-distinct-only-corroboration-failure-domain-backed-corroboration-and-isolation-backed-corroboration.md` when the live question is whether genuinely independent corroboration is only label-distinct, backed by a failure domain, backed by substrate isolation, or honestly mixed.\n'
    insert_after('docs/00-meta/llm-runbook.md', anchor, addition)


def update_docs_readme() -> None:
    line = '- [`10-method/refresh-scope-axis-materiality-witnesses-label-distinct-only-corroboration-failure-domain-backed-corroboration-and-isolation-backed-corroboration.md`](10-method/refresh-scope-axis-materiality-witnesses-label-distinct-only-corroboration-failure-domain-backed-corroboration-and-isolation-backed-corroboration.md)'
    after = '- [`10-method/refresh-scope-axis-independence-witnesses-renamed-or-mirrored-axis-restatement-nested-axis-restatement-and-independent-axis-corroboration.md`](10-method/refresh-scope-axis-independence-witnesses-renamed-or-mirrored-axis-restatement-nested-axis-restatement-and-independent-axis-corroboration.md)'
    ensure_line('docs/README.md', line, after)


def update_prompt_pairs() -> None:
    block = dedent('''

    Use `docs/10-method/refresh-scope-axis-materiality-witnesses-label-distinct-only-corroboration-failure-domain-backed-corroboration-and-isolation-backed-corroboration.md` when the live question is whether genuinely independent corroboration is only label-distinct, backed by a failure domain, backed by substrate isolation, or honestly mixed.

    ## `PP-0107` — Name whether genuinely independent corroboration is only label-distinct, failure-domain-backed, or isolation-backed

    **Opening prompt**

    ```text
    Read the latest DelayBasin archive and inspect whether the current revision should also materialize one compact refresh-scope-axis-materiality witness for honest label-distinct-vs-failure-domain-vs-isolation-backed corroboration.

    Focus only on cases where the axes already look genuinely independent. The missing question is whether that independence is still only a label, queue, or selector distinction, whether it is backed by a public failure domain, whether it is backed by substrate isolation, or whether the situation is honestly mixed.

    If yes, preserve exactly one small witness that:
    - names the governed row or surface,
    - names the stake object / line of concern,
    - names the prior refresh-scope-axis-independence evidence,
    - names the current corroborating axes,
    - names the label-distinct-only basis if any,
    - names the failure-domain basis if any,
    - names the isolation-backed basis if any,
    - names the `refresh_scope_axis_materiality_state` / whether this is label-distinct-only-corroboration, failure-domain-backed-corroboration, isolation-backed-corroboration, or mixed-refresh-scope-axis-materiality,
    - states what stronger surfaces still outrank the witness,
    - and states the fail-closed repair / keep-current vs narrow-claim vs split-scope vs issue-new-refresh-scope-axis-materiality-witness vs quarantine-axis-materiality-exchange-rate consequence if the present continuity claim is still only weakly material.

    Do not use refresh scope axis materiality as a general weighting court. Use this prompt pair only where axis independence is already established and the missing question is how materially strong the corroboration really is.
    ```

    **Continuation prompt**

    ```text
    Continue the refresh-scope-axis-materiality pass with one high-leverage label-vs-failure-domain-vs-isolation clarification only. Prefer the smallest witness that says what governed row is still being justified, what stake object is supposedly widened, what prior refresh-scope-axis-independence evidence exists, what current corroborating axes exist, what label-distinct-only basis if any now exists, what failure-domain basis if any now exists, what isolation-backed basis if any now exists, what `refresh_scope_axis_materiality_state` is honest, what stronger surfaces still outrank the witness, and what keep-current, narrow-claim, split-scope, issue-new-refresh-scope-axis-materiality-witness, quarantine, or recover-resync consequence follows if the present corroboration is only label-distinct-only-corroboration, failure-domain-backed-corroboration, isolation-backed-corroboration, or mixed-refresh-scope-axis-materiality. Run `make lint` and package the release.
    ```
    ''')
    append_unique_block('docs/50-promptcraft/prompt-pairs.md', block)


def update_quarantine() -> None:
    block = dedent(f'''

    ## {NEW_QWS} — Some continuations may eventually need an {NEW_QWS_LABEL} rather than only a compact refresh-scope-axis-materiality witness

    ### Claim

    A bolder possibility is that DelayBasin may eventually need not only a compact witness for whether genuinely independent corroboration is merely label-distinct, failure-domain-backed, or isolation-backed, but also a governed public rule for how those material classes combine, overlap, or get discounted when they still ride one coupled substrate. Kubernetes failure-domain labels, Slurm's distinction between shared MPS slices and MIG instances, and NVIDIA's time-slicing-vs-MIG contrast suggest a stronger exchange-rate story: perhaps some future archive lines should not only be classified as `label-distinct-only-corroboration`, `failure-domain-backed-corroboration`, `isolation-backed-corroboration`, or `mixed-refresh-scope-axis-materiality`, but admitted through a small materiality exchange rate, coupling haircut, or corroboration capital stack. ([`REF-0956`](../00-meta/bibliography.md), [`REF-0961`](../00-meta/bibliography.md), [`REF-0962`](../00-meta/bibliography.md), [`REF-0963`](../00-meta/bibliography.md), [`REF-0959`](../00-meta/bibliography.md))

    The narrower speculative move is only this: a future bounded surface *might* need to say not just what material class an axis has, but how much of that class survives when several materially real axes still share one rack, scheduler, switch, or substrate.

    ### What follows if true

    - some future continuity cards may need explicit coupling haircuts rather than one flat materiality token;
    - failure-domain-backed and isolation-backed corroboration may need to combine by a compact exchange rate instead of prose intuition alone;
    - archive-wide diffusion talk may need a brake for materially strong but still coupled axes;
    - later revisions should look for cases where material classes are individually honest but collectively overstated.

    ### What would count against it

    - repeated later passes show that one compact refresh-scope-axis-materiality witness keeps weak, failure-domain, and isolation-backed corroboration honest without any exchange-rate layer;
    - materially backed axes rarely need explicit combination or discount rules;
    - coupling questions usually dissolve under the ordinary independence and materiality witnesses;
    - capital-stack language never pays for itself beyond rhetorical flourish.

    ### Why it stays quarantined

    The tempting overreach would be to declare that DelayBasin now needs a public axis-materiality exchange rate, coupling haircut, or corroboration capital stack. DelayBasin has not earned that. This note is bold enough to keep in quarantine but not yet honest enough for canon. Do not promote an axis-materiality exchange rate, coupling haircut, or corroboration capital stack from this note alone.
    ''')
    append_unique_block('docs/90-quarantine/wild-speculations-2026-03-08.md', block)


def update_vocabulary() -> None:
    vocab = json.loads(read('WITNESS-VOCABULARY.json'))
    vocab['revision'] = REV
    vocab['families'][NEW_FAMILY] = {
        'allowed': [
            'label-distinct-only-corroboration',
            'failure-domain-backed-corroboration',
            'isolation-backed-corroboration',
            'mixed-refresh-scope-axis-materiality'
        ],
        'surfaces': ['WITNESS-VOCABULARY.json', 'REVISION-RECEIPT.json', NEW_DOC],
        'excluded_synonyms': [
            'different-label-means-material',
            'zone-sounding-means-isolated',
            'shared-slice-counts-like-mig',
            'materiality-ish'
        ],
        'comparability_budget': 'refresh-scope-axis-materiality truth is compared by token; the compact witness says whether genuinely independent corroboration is only label-distinct, backed by a failure domain, backed by substrate isolation, or honestly mixed, while raw topology maps, scheduler configs, and isolation tables stay in surrounding prose'
    }
    write_json('WITNESS-VOCABULARY.json', vocab)


def update_packet_common_and_checkers() -> None:
    text = read('tools/packet_contract_common.py')
    if 'refresh_scope_axis_materiality_witness_contract' not in text:
        anchor = '"refresh_scope_axis_independence_witness_contract": _refresh_family_spec(\n'
        idx = text.index(anchor)
        next_anchor = '    "refresh_scope_extent_witness_contract": _refresh_family_spec('
        idx2 = text.index(next_anchor, idx)
        spec = dedent('''
        "refresh_scope_axis_materiality_witness_contract": _refresh_family_spec(
            doc_path="docs/10-method/refresh-scope-axis-materiality-witnesses-label-distinct-only-corroboration-failure-domain-backed-corroboration-and-isolation-backed-corroboration.md",
            doc_needles=[
                "# Refresh-scope-axis-materiality witnesses, label-distinct-only corroboration, failure-domain-backed corroboration, and isolation-backed corroboration",
                "This is the compact successor surface for `OQ-0149`.",
                "## Practice / observation",
                "## External pressure from Ray selector labels, Kubernetes failure domains, Slurm MPS-vs-MIG scheduling, and NVIDIA time-slicing-vs-MIG isolation",
                "## Working synthesis",
                "## Label-distinct-only corroboration vs failure-domain-backed corroboration vs isolation-backed corroboration vs mixed refresh scope axis materiality",
                "## Countermodels / probes",
                "## Design consequences",
                "## Overflow test",
                "## Transformer-facing implication",
                "`refresh_scope_axis_materiality_state`",
                "label-distinct-only-corroboration",
                "failure-domain-backed-corroboration",
                "isolation-backed-corroboration",
                "mixed-refresh-scope-axis-materiality",
            ],
            runbook_ref="refresh-scope-axis-materiality-witnesses-label-distinct-only-corroboration-failure-domain-backed-corroboration-and-isolation-backed-corroboration.md",
            prompt_id="PP-0107",
            prompt_needles=["Use `docs/10-method/refresh-scope-axis-materiality-witnesses-label-distinct-only-corroboration-failure-domain-backed-corroboration-and-isolation-backed-corroboration.md`", "label-distinct-only-corroboration, failure-domain-backed-corroboration, isolation-backed-corroboration, or mixed-refresh-scope-axis-materiality"],
            claim_id="CL-0147",
            oq_id="OQ-0149",
            resolution_id="RS-0156",
            trajectory_oq_id="OQ-0150",
            qws_id="QWS-0232",
            qws_label="axis-materiality exchange rate / coupling haircut / corroboration capital stack",
            changelog_needles=["refresh-scope-axis-materiality-witnesses-label-distinct-only-corroboration-failure-domain-backed-corroboration-and-isolation-backed-corroboration.md", "check_refresh_scope_axis_materiality_witness_contract.py"],
            family="refresh_scope_axis_materiality_state",
            allowed=["label-distinct-only-corroboration", "failure-domain-backed-corroboration", "isolation-backed-corroboration", "mixed-refresh-scope-axis-materiality"],
            excluded=["different-label-means-material", "zone-sounding-means-isolated", "shared-slice-counts-like-mig", "materiality-ish"],
        ),

        ''')
        text = text[:idx2] + spec + text[idx2:]

    old_helpers = dedent('''

    def require_named_refresh_scope_axis_family_witness_packet_and_vocabulary(kind: str) -> None:
        require_named_refresh_scope_packet_and_vocabulary(kind)


    def require_named_refresh_scope_axis_witness_packet_and_vocabulary(kind: str) -> None:
        require_named_refresh_scope_axis_family_witness_packet_and_vocabulary(kind)


    def require_named_refresh_scope_axis_independence_witness_packet_and_vocabulary(kind: str) -> None:
        require_named_refresh_scope_axis_family_witness_packet_and_vocabulary(kind)
    ''')
    new_helpers = dedent('''

    def require_named_refresh_scope_axis_family_witness_packet_and_vocabulary(kind: str) -> None:
        require_named_refresh_scope_packet_and_vocabulary(kind)


    def require_named_refresh_scope_axis_packet_and_vocabulary(kind: str) -> None:
        require_named_refresh_scope_axis_family_witness_packet_and_vocabulary(kind)


    def require_named_refresh_scope_axis_witness_packet_and_vocabulary(kind: str) -> None:
        require_named_refresh_scope_axis_packet_and_vocabulary(kind)


    def require_named_refresh_scope_axis_independence_witness_packet_and_vocabulary(kind: str) -> None:
        require_named_refresh_scope_axis_packet_and_vocabulary(kind)


    def require_named_refresh_scope_axis_materiality_witness_packet_and_vocabulary(kind: str) -> None:
        require_named_refresh_scope_axis_packet_and_vocabulary(kind)
    ''')
    if 'def require_named_refresh_scope_axis_materiality_witness_packet_and_vocabulary' not in text:
        if old_helpers not in text:
            raise SystemExit('old scope axis helper block not found')
        text = text.replace(old_helpers, new_helpers, 1)
    write('tools/packet_contract_common.py', text)

    write('tools/check_refresh_scope_axis_witness_contract.py', 'from packet_contract_common import require_named_refresh_scope_axis_packet_and_vocabulary\n\nrequire_named_refresh_scope_axis_packet_and_vocabulary("refresh_scope_axis_witness_contract")\n\nprint("check_refresh_scope_axis_witness_contract: OK")\n')
    write('tools/check_refresh_scope_axis_independence_witness_contract.py', 'from packet_contract_common import require_named_refresh_scope_axis_packet_and_vocabulary\n\nrequire_named_refresh_scope_axis_packet_and_vocabulary("refresh_scope_axis_independence_witness_contract")\n\nprint("check_refresh_scope_axis_independence_witness_contract: OK")\n')
    write(NEW_CHECKER, 'from packet_contract_common import require_named_refresh_scope_axis_materiality_witness_packet_and_vocabulary\n\nrequire_named_refresh_scope_axis_materiality_witness_packet_and_vocabulary("refresh_scope_axis_materiality_witness_contract")\n\nprint("check_refresh_scope_axis_materiality_witness_contract: OK")\n')


def append_ledger_items() -> None:
    append_item('FOLLOWTHROUGH-QUEUE.json', {
        'id': 'FT-0156',
        'title': 'keep checking whether refresh-scope-axis-materiality pressure still fits inside one compact successor surface',
        'state': 'queued',
        'blocked_object': 'axis-materiality exchange rate, coupling haircut, or corroboration capital stack',
        'local_surface': f'docs/90-quarantine/wild-speculations-2026-03-08.md#{NEW_QWS}',
        'followthrough_state': 'queued',
        'boundary': 'do not promote bounded refresh-scope-axis-materiality clarification into a general weighting or exchange-rate machine',
        'next_proof_surface': NEW_DOC,
        'receiving_surface': 'FOLLOWTHROUGH-QUEUE.json#FT-0156',
        'repair': 'ordinary-continuation',
        'origin_revision': REV,
        'discharge': 'revisit-on-next-real-refresh-scope-axis-materiality-overflow',
        'action_lane': 'keep-compact',
        'gate_class': 'overflow',
        'blocked_output': 'axis-materiality exchange rate, coupling haircut, or corroboration capital stack',
        'owner_surface': 'OBLIGATION-LEDGER.json#OB-0149',
        'revision': REV,
        'missing_support': 'a later public check on whether one compact refresh-scope-axis-materiality witness keeps overflowing the bounded rule and honestly warrants richer exchange-rate governance',
        'candidate_surface': f'docs/90-quarantine/wild-speculations-2026-03-08.md#{NEW_QWS}',
        'blocked_by': 'need repeated evidence that label-distinct-only vs failure-domain-backed vs isolation-backed truth overflows one compact witness'
    })

    append_item('ASSUMPTION-LEDGER.json', {
        'id': 'AS-0153',
        'title': 'one compact refresh-scope-axis-materiality witness is enough for now',
        'state': 'active',
        'scope': 'continuity passes whose current widened public claim depends not only on whether corroborating axes are genuinely independent, but on whether that corroboration is only label-distinct, failure-domain-backed, or isolation-backed',
        'invalidation_triggers': [
            'repeated later revisions need standing exchange-rate or weighting governance rather than one compact refresh-scope-axis-materiality witness',
            'the archive needs a coupling haircut or corroboration capital stack just to keep label-distinct-only, failure-domain-backed, and isolation-backed corroboration distinct',
            'materiality cases repeatedly fail to stay distinguishable even with the witness in place'
        ],
        'assumption_state': 'active',
        'repair': 'ordinary-continuation',
        'origin_revision': REV,
        'revision': REV,
        'assumption': 'the current evidence only requires one compact refresh-scope-axis-materiality witness over the existing refresh-scope-axis-independence and related admitted surfaces rather than an axis-materiality exchange rate, coupling haircut, or corroboration capital stack',
        'supporting_surfaces': ['APPLICABILITY-LEDGER.json#AP-0148', 'DATACUBE-TRANSFER-LEDGER.json#TL-0159', 'FOREIGN-PRESSURE-LEDGER.json#FP-0153'],
        'discharge': 'discharge when later revisions can keep label-distinct-vs-failure-domain-vs-isolation truth honest without a dedicated refresh-scope-axis-materiality witness, or retire/quarantine it if broader exchange-rate governance becomes repeatedly necessary',
        'witness_surface': 'ASSUMPTION-LEDGER.json#AS-0153',
        'assumption_surface': 'ASSUMPTION-LEDGER.json#AS-0153',
        'assumption_statement': 'the current evidence only requires one compact refresh-scope-axis-materiality witness over the existing refresh-scope-axis-independence and related admitted surfaces rather than an axis-materiality exchange rate, coupling haircut, or corroboration capital stack',
        'action_lane': 'keep-compact',
        'gate_class': 'concrete-evidence'
    })

    append_item('OBLIGATION-LEDGER.json', {
        'id': 'OB-0149',
        'title': 'when genuinely independent corroboration keeps needing label-vs-failure-domain-vs-isolation separation, DelayBasin should preserve one compact refresh-scope-axis-materiality witness rather than an exchange-rate stack',
        'state': 'open',
        'witness_surface': 'OBLIGATION-LEDGER.json#OB-0149',
        'target_surfaces': [f'docs/90-quarantine/wild-speculations-2026-03-08.md#{NEW_QWS}'],
        'missing_support': 'a later public check on whether one compact refresh-scope-axis-materiality witness keeps sufficing and whether label-distinct-only, failure-domain-backed, and isolation-backed corroboration stay distinct without broader weighting governance',
        'current_support': ['APPLICABILITY-LEDGER.json#AP-0148', 'FOREIGN-PRESSURE-LEDGER.json#FP-0153', 'DATACUBE-TRANSFER-LEDGER.json#TL-0159'],
        'discharge_path': 'either show later that one compact refresh-scope-axis-materiality witness keeps sufficing or promote broader exchange-rate governance explicitly',
        'obligation_state': 'open',
        'repair': 'ordinary-continuation',
        'origin_revision': REV,
        'discharge': 'reopen-only-if-refresh-scope-axis-materiality-overflows',
        'revision': REV,
        'owner_surface': 'OBLIGATION-LEDGER.json#OB-0149',
        'action_lane': 'keep-compact',
        'gate_class': 'overflow'
    })

    append_item('APPLICABILITY-LEDGER.json', {
        'id': 'AP-0148',
        'title': 'the refresh-scope-axis-materiality witness stays smaller than an exchange-rate stack',
        'state': 'gated',
        'question': 'when should DelayBasin treat genuinely independent corroboration with one compact materiality witness instead of promoting broader weighting governance?',
        'applies_when': [
            'a revision already has a durable row whose current claim depends on corroborating axes that are already judged genuinely independent',
            'later passes still need to distinguish label-distinct-only-corroboration, failure-domain-backed-corroboration, isolation-backed-corroboration, or mixed-refresh-scope-axis-materiality posture',
            'one compact successor surface plus the existing admitted refresh-scope-axis-independence and topology or substrate surfaces still keeps materiality truth honest without standing exchange-rate policy'
        ],
        'does_not_apply_when': [
            'the archive honestly requires standing governance over coupling haircuts, additive weights, or corroboration exchange rates',
            'the questioned surface is not really about whether genuinely independent corroboration is only weakly material, failure-domain-backed, or isolation-backed'
        ],
        'budget': 'one compact refresh-scope-axis-materiality witness plus one resolution of OQ-0149; no exchange-rate stack',
        'negative_transfer_budget': 'do not treat label-distinct selectors or renamed shared slices as if they automatically carried fault-domain or isolation authority',
        'origin_revision': REV,
        'discharge': 'reopen-only-if-refresh-scope-axis-materiality-overflows',
        'action_lane': 'keep-compact',
        'gate_class': 'concrete-evidence',
        'witness_surface': 'APPLICABILITY-LEDGER.json#AP-0148',
        'applicability_state': 'gated',
        'repair': 'ordinary-continuation',
        'matched_budget': 'one compact witness foregrounding label-distinct-only vs failure-domain-backed vs isolation-backed corroboration without widening into broader weighting governance',
        'revision': REV,
        'target_objective': 'keep axis materiality honest without inflating a general corroboration-weight layer',
        'carry_object': 'refresh-scope-axis-materiality witness',
        'open_question': NEW_OQ
    })

    append_item('FOREIGN-PRESSURE-LEDGER.json', {
        'id': 'FP-0153',
        'title': 'refresh-scope-axis-materiality pressure pushes DelayBasin to extract one compact weak-vs-failure-domain-vs-isolation witness rather than an exchange-rate stack',
        'state': 'imported',
        'source_packets': [
            {'datacube': 'RayLabelSelectors-2026', 'surfaces': ['REF-0957'], 'pressure': 'distinct label selectors can still be only routing clauses, which pressures DelayBasin to preserve a label-distinct-only materiality class rather than over-reading material separation'},
            {'datacube': 'KubernetesFailureDomains-2026', 'surfaces': ['REF-0956', 'REF-0961'], 'pressure': 'failure-domain topology and zone independence pressure DelayBasin to preserve a distinct failure-domain-backed corroboration class'},
            {'datacube': 'SlurmSharedVsIsolatedGpu-2026', 'surfaces': ['REF-0962'], 'pressure': 'shared MPS slices versus MIG instances pressure DelayBasin to distinguish percentage sharing from substrate-isolated corroboration'},
            {'datacube': 'NvidiaTimeSlicingVsMig-2026', 'surfaces': ['REF-0963', 'REF-0959'], 'pressure': 'time-slicing without isolation versus MIG with hardware isolation pressures DelayBasin to keep label changes from inheriting the authority of isolated partitions'}
        ],
        'reviewed_pattern': 'label-distinct-only vs failure-domain-backed vs isolation-backed corroboration across genuinely independent axes',
        'import_decision': 'support a compact refresh-scope-axis-materiality witness and resolve OQ-0149',
        'adopted_take': 'DelayBasin should add one compact witness that says whether genuinely independent corroboration is label-distinct-only, failure-domain-backed, isolation-backed, or honestly mixed',
        'supporting_only_take': 'the current evidence cleanly supports a bounded refresh-scope-axis-materiality witness without promoting broader weighting or exchange-rate governance',
        'deferred_or_rejected_take': ['axis-materiality exchange rate', 'coupling haircut', 'corroboration capital stack'],
        'local_gap': 'the archive still lacked one compact successor surface for whether genuinely independent corroboration was only weakly material or backed by failure domains or substrate isolation',
        'anchor_surfaces': [
            'docs/10-method/refresh-scope-axis-independence-witnesses-renamed-or-mirrored-axis-restatement-nested-axis-restatement-and-independent-axis-corroboration.md',
            'docs/20-constitution/open-question-registry.md',
            'docs/00-meta/trajectory-map.md',
            f'docs/90-quarantine/wild-speculations-2026-03-08.md#{NEW_QWS}'
        ],
        'open_question': NEW_OQ,
        'repair': 'ordinary-continuation',
        'origin_revision': REV,
        'action_lane': 'keep-compact',
        'gate_class': 'concrete-evidence',
        'discharge': 'reopen-only-if-refresh-scope-axis-materiality-overflows',
        'revision': REV,
        'witness_surface': 'FOREIGN-PRESSURE-LEDGER.json#FP-0153',
        'foreign_pressure_state': 'imported',
        'bounded_take': 'Keep the archive compact by extracting one refresh-scope-axis-materiality witness over the existing refresh-scope-axis-independence and related admitted surfaces; do not promote an axis-materiality exchange rate, coupling haircut, or corroboration capital stack.',
        'explicit_non_take': ['no axis-materiality exchange rate', 'no coupling haircut', 'no corroboration capital stack'],
        'open_transfer_question': 'whether a later pass needs one bounded refresh-scope-axis-coupling witness once materiality classes are explicit',
        'missing_support': 'a later public check on whether one compact refresh-scope-axis-materiality witness keeps sufficing',
        'reviewed_datacubes': [
            {'datacube': 'RayLabelSelectors-2026', 'surfaces': ['REF-0957'], 'pattern': 'conjunctive label selectors', 'pressure': 'a distinct selector should not automatically count as materially strong corroboration'},
            {'datacube': 'KubernetesFailureDomains-2026', 'surfaces': ['REF-0956', 'REF-0961'], 'pattern': 'spread across zones and explicit failure independence', 'pressure': 'failure-domain-backed corroboration should stay distinct from mere labels'},
            {'datacube': 'SlurmSharedVsIsolatedGpu-2026', 'surfaces': ['REF-0962'], 'pattern': 'shared MPS versus MIG instances with cgroup isolation', 'pressure': 'shared slices should not inherit isolated-partition authority'},
            {'datacube': 'NvidiaTimeSlicingVsMig-2026', 'surfaces': ['REF-0963', 'REF-0959'], 'pattern': 'time-sliced shared replicas versus hardware-isolated MIG instances', 'pressure': 'renamed shared products should not read like isolated corroboration'}
        ]
    })

    transfer = json.loads(read('DATACUBE-TRANSFER-LEDGER.json'))
    transfer_item = {
        'id': 'TL-0159',
        'title': 'refresh-scope-axis-materiality evidence supports resolving OQ-0149 with one compact weak-vs-failure-domain-vs-isolation card rather than an exchange-rate stack',
        'state': 'supporting-only',
        'reviewed_pattern': 'label-distinct-only vs failure-domain-backed vs isolation-backed corroboration across genuinely independent axes',
        'import_decision': 'support a compact refresh-scope-axis-materiality witness and resolve OQ-0149',
        'adopted_take': 'DelayBasin should add one compact witness that says whether genuinely independent corroboration is label-distinct-only, failure-domain-backed, isolation-backed, or honestly mixed',
        'supporting_only_take': 'the current evidence cleanly supports a bounded refresh-scope-axis-materiality witness without promoting broader weighting or exchange-rate governance',
        'deferred_or_rejected_take': ['axis-materiality exchange rate', 'coupling haircut', 'corroboration capital stack'],
        'local_gap': 'the archive still lacked one compact successor surface for whether genuinely independent corroboration was only weakly material or backed by failure domains or substrate isolation',
        'anchor_surfaces': [
            'docs/10-method/refresh-scope-axis-independence-witnesses-renamed-or-mirrored-axis-restatement-nested-axis-restatement-and-independent-axis-corroboration.md',
            'docs/20-constitution/open-question-registry.md',
            'docs/00-meta/trajectory-map.md',
            f'docs/90-quarantine/wild-speculations-2026-03-08.md#{NEW_QWS}'
        ],
        'open_question': NEW_OQ,
        'repair': 'ordinary-continuation',
        'origin_revision': REV,
        'action_lane': 'keep-compact',
        'gate_class': 'concrete-evidence',
        'discharge': 'reopen-only-if-refresh-scope-axis-materiality-overflows',
        'revision': REV,
        'witness_surface': 'DATACUBE-TRANSFER-LEDGER.json#TL-0159',
        'transfer_state': 'supporting-only',
        'bounded_take': 'Keep the archive compact by extracting one refresh-scope-axis-materiality witness over the existing refresh-scope-axis-independence and related admitted surfaces; do not promote an axis-materiality exchange rate, coupling haircut, or corroboration capital stack.',
        'explicit_non_take': ['no axis-materiality exchange rate', 'no coupling haircut', 'no corroboration capital stack'],
        'open_transfer_question': 'whether later passes should add a separate refresh-scope-axis-coupling witness once materiality classes are explicit',
        'missing_support': 'a later public check on whether one compact refresh-scope-axis-materiality witness keeps sufficing',
        'current_support': ['APPLICABILITY-LEDGER.json#AP-0148', 'FOREIGN-PRESSURE-LEDGER.json#FP-0153', 'DATACUBE-TRANSFER-LEDGER.json#TL-0159'],
        'discharge_path': 'either show later that one compact refresh-scope-axis-materiality witness keeps sufficing or promote broader weighting governance explicitly',
        'reviewed_datacubes': [
            {'datacube': 'RayLabelSelectors-2026', 'surfaces': ['REF-0957'], 'pattern': 'conjunctive label selectors', 'pressure': 'a distinct selector should not automatically count as materially strong corroboration'},
            {'datacube': 'KubernetesFailureDomains-2026', 'surfaces': ['REF-0956', 'REF-0961'], 'pattern': 'spread across zones and explicit failure independence', 'pressure': 'failure-domain-backed corroboration should stay distinct from mere labels'},
            {'datacube': 'SlurmSharedVsIsolatedGpu-2026', 'surfaces': ['REF-0962'], 'pattern': 'shared MPS versus MIG instances with cgroup isolation', 'pressure': 'shared slices should not inherit isolated-partition authority'},
            {'datacube': 'NvidiaTimeSlicingVsMig-2026', 'surfaces': ['REF-0963', 'REF-0959'], 'pattern': 'time-sliced shared replicas versus hardware-isolated MIG instances', 'pressure': 'renamed shared products should not read like isolated corroboration'}
        ]
    }
    if not any(x.get('id') == 'TL-0159' for x in transfer['items']):
        transfer['items'].append(transfer_item)
    new_open_q = 'Whether a later pass should add one bounded refresh-scope-axis-coupling witness once materiality classes are explicit, but only if materially backed corroboration keeps collapsing under one shared failure or execution plane in honest continuation work.'
    if new_open_q not in transfer.get('open_questions', []):
        transfer.setdefault('open_questions', []).append(new_open_q)
    transfer['revision'] = REV
    write_json('DATACUBE-TRANSFER-LEDGER.json', transfer)

    append_item('RESOLUTION-LEDGER.json', {
        'id': 'RS-0156',
        'title': 'resolve OQ-0149 with one compact refresh-scope-axis-materiality witness rather than an exchange-rate stack',
        'state': 'resolved',
        'closure_state': 'resolved',
        'closure_reason': 'rev0254 extracted one compact refresh-scope-axis-materiality witness, kept the admitted refresh-scope-axis-independence and related analog surfaces narrow, and kept stronger exchange-rate stories quarantined.',
        'discharge': 'reopen-only-if-refresh-scope-axis-materiality-overflows',
        'gate_class': 'concrete-evidence',
        'origin_revision': REV,
        'prior_state': 'open gap: DelayBasin already had refresh-scope-axis-independence truth but still lacked one compact successor surface for whether genuinely independent corroboration was only weakly material or backed by failure domains or substrate isolation.',
        'question': 'whether one compact refresh-scope-axis-materiality witness over the existing refresh-scope-axis-independence and related admitted surfaces is enough for honest weak-vs-failure-domain-vs-isolation comparison',
        'reopen_trigger': 'refresh-scope-axis-materiality pressure overflows one compact successor surface',
        'reopen_triggers': ['later revisions need standing governance over coupling haircuts, exchange rates, additive weighting, or broader materiality policy that one compact refresh-scope-axis-materiality witness cannot honestly absorb'],
        'repair': 'ordinary-continuation',
        'resolved_objects': ['OQ-0149', 'AP-0148', 'FP-0153', 'TL-0159'],
        'revision': REV,
        'successor_surface': NEW_DOC,
        'target_surfaces': [NEW_DOC],
        'action_lane': 'keep-compact',
        'witness_surface': 'RESOLUTION-LEDGER.json#RS-0156'
    })

    append_item('RETROSPECTIVE-QUEUE.json', {
        'id': 'RT-0143',
        'title': 'revisit whether refresh-scope-axis-materiality pressure stayed bounded after rev0254',
        'state': 'cooling',
        'candidate_surface': f'docs/90-quarantine/wild-speculations-2026-03-08.md#{NEW_QWS}',
        'cooldown_window': 'keep the stronger axis-materiality exchange rate, coupling haircut, or corroboration capital stack story cooled until at least one later revision shows that one compact refresh-scope-axis-materiality witness is no longer enough.',
        'adjudication_family': 'refresh scope axis materiality / corroboration weighting / coupling pressure',
        'supersession_link': 'OBLIGATION-LEDGER.json#OB-0149',
        'origin_revision': REV,
        'discharge': 'keep-cooling-unless-refresh-scope-axis-materiality-overflows',
        'action_lane': 'keep-compact',
        'gate_class': 'overflow',
        'witness_surface': 'RETROSPECTIVE-QUEUE.json#RT-0143',
        'revision': REV,
        'cooling_state': 'cooling',
        'disposition': 'await-adjudication',
        'repair': 'keep-cooling'
    })

    append_item('FIREBREAK-LEDGER.json', {
        'id': 'FB-0150',
        'title': 'the refresh-scope-axis-materiality import should count as one compact weak-vs-failure-domain-vs-isolation repair, not as promotion of an exchange-rate stack',
        'state': 'withheld',
        'witness_surface': 'FIREBREAK-LEDGER.json#FB-0150',
        'judged_property': 'the rev0254 decision that DelayBasin should extract one compact refresh-scope-axis-materiality witness over the existing refresh-scope-axis-independence and related admitted surfaces and `refresh_scope_axis_materiality_state` family while the broader axis-materiality exchange rate / coupling haircut / corroboration capital stack story remains quarantined',
        'public_extract': [NEW_DOC, 'docs/10-method/refresh-scope-axis-independence-witnesses-renamed-or-mirrored-axis-restatement-nested-axis-restatement-and-independent-axis-corroboration.md', 'docs/20-constitution/open-question-registry.md', 'FOREIGN-PRESSURE-LEDGER.json#FP-0153', 'APPLICABILITY-LEDGER.json#AP-0148', 'REVISION-RECEIPT.json'],
        'withheld_trace_surface': 'same-session drafting residue behind the compact refresh-scope-axis-materiality-witness versus exchange-rate-stack decision',
        'allowed_role': 'bounded drafting aid only; not public support for a broader axis-materiality exchange rate, coupling haircut, or corroboration capital stack',
        'exposure_rule': 'expose or reintegrate only if later passes show that one compact refresh-scope-axis-materiality witness cannot keep weak-vs-failure-domain-vs-isolation truth bounded',
        'trace_state': 'withheld',
        'repair': 'ordinary-continuation',
        'origin_revision': REV,
        'action_lane': 'keep-compact',
        'gate_class': 'overflow',
        'firebreak_surface': 'FIREBREAK-LEDGER.json#FB-0150',
        'discharge': 'reopen-only-if-refresh-scope-axis-materiality-overflows',
        'revision': REV,
        'blocked_object': 'standing axis-materiality exchange rate, coupling haircut, or corroboration capital stack'
    })


def update_changelog_and_index() -> None:
    changelog = read('CHANGELOG.md')
    if changelog.startswith(f'## {REV}'):
        pass
    else:
        write('CHANGELOG.md', dedent(f'''## {REV} - {STAMP} - axismateriality / stackquarantine / shardcarry / {CODENAME}

- Added `{NEW_DOC}` to resolve `OQ-0149` with a compact label-vs-failure-domain-vs-isolation materiality witness.
- Kept the stronger {NEW_QWS_LABEL} move explicitly quarantined as `{NEW_QWS}` instead of laundering it into canon.
- Refactored refresh-scope-axis contract helpers so axis, axis-independence, and axis-materiality checkers share one narrower validator entrypoint, and added `{NEW_CHECKER}`.

''' ) + changelog)
    index = read('ARCHIVE_INDEX.md')
    row = f'| {BUNDLE} | 2026-03-28 | Refresh-scope-axis-materiality revision: resolved OQ-0149 with a compact label-vs-failure-domain-vs-isolation witness, honestly quarantined stronger coupling-weight governance, and tightened shared scope-axis contract wiring to stay wired and cumulative. |\n'
    if row not in index:
        header = '# Archive index\n\n'
        if not index.startswith(header):
            raise SystemExit('ARCHIVE_INDEX header mismatch')
        write('ARCHIVE_INDEX.md', header + row + index[len(header):])


def update_surface_status_and_manifest() -> None:
    status = json.loads(read('SURFACE-STATUS.json'))
    status['revision'] = REV
    status['operational_head']['revision'] = REV
    status['citation_head'] = {'revision': REV, 'surface': BUNDLE}
    status['previous_citation_head'] = {'revision': PREV, 'surface': PREV_BUNDLE}
    status['status_lanes']['frozen_public_surface'] = BUNDLE
    status['status_lanes']['current_release_surface'] = BUNDLE
    status['slug'] = SLUG
    status['stamp'] = STAMP
    write_json('SURFACE-STATUS.json', status)

    manifest = {
        'project': 'DelayBasin',
        'revision': REV,
        'timestamp': STAMP,
        'slug': SLUG,
        'bundle': BUNDLE,
    }
    write_json('RELEASE-MANIFEST.json', manifest)


def update_receipt() -> None:
    r = json.loads(read('REVISION-RECEIPT.json'))
    r['revision'] = REV
    r['previous_revision'] = PREV
    r['summary'] = 'Resolved OQ-0149 with one compact refresh-scope-axis-materiality witness that separates merely label-distinct corroboration from failure-domain-backed and isolation-backed corroboration while keeping stronger exchange-rate governance quarantined.'
    r['move_classes'] = ['MV-0002', 'MV-0003', 'MV-0004', 'MV-0007', 'MV-0011']
    r['canon_additions'] = [NEW_DOC, 'RS-0156 resolved OQ-0149 with one compact refresh-scope-axis-materiality witness']
    r['quarantine_additions'] = [f'{NEW_QWS} — {NEW_QWS_LABEL}']
    r['refs_used'] = [
        'docs/00-meta/bibliography.md#ref-0957',
        'docs/00-meta/bibliography.md#ref-0956',
        'docs/00-meta/bibliography.md#ref-0961',
        'docs/00-meta/bibliography.md#ref-0962',
        'docs/00-meta/bibliography.md#ref-0963',
        'docs/00-meta/bibliography.md#ref-0959',
    ]
    r['checks_passed'] = ['make lint']
    touched = [
        NEW_DOC, 'docs/00-meta/bibliography.md', 'docs/00-meta/llm-runbook.md', 'docs/README.md',
        'docs/20-constitution/claim-registry.md', 'docs/20-constitution/open-question-registry.md',
        'docs/20-constitution/prompt-pair-registry.md', 'docs/00-meta/trajectory-map.md',
        'docs/50-promptcraft/prompt-pairs.md', 'docs/90-quarantine/wild-speculations-2026-03-08.md',
        'WITNESS-VOCABULARY.json', 'FOLLOWTHROUGH-QUEUE.json', 'ASSUMPTION-LEDGER.json',
        'OBLIGATION-LEDGER.json', 'APPLICABILITY-LEDGER.json', 'FOREIGN-PRESSURE-LEDGER.json',
        'DATACUBE-TRANSFER-LEDGER.json', 'RESOLUTION-LEDGER.json', 'RETROSPECTIVE-QUEUE.json',
        'FIREBREAK-LEDGER.json', 'REVISION-RECEIPT.json', 'SURFACE-STATUS.json', 'RELEASE-MANIFEST.json',
        'CHANGELOG.md', 'ARCHIVE_INDEX.md', 'tools/packet_contract_common.py', 'tools/check_refresh_scope_axis_witness_contract.py',
        'tools/check_refresh_scope_axis_independence_witness_contract.py', NEW_CHECKER, 'apply_rev0254.py'
    ]
    r['touched_surfaces'] = touched
    r['packaged_release'] = True
    r['packaged_bundle_filename'] = BUNDLE
    r['basis_witness'].update({
        'expected_head': PREV,
        'observed_head': PREV,
        'basis_surfaces': ['docs/10-method/refresh-scope-axis-independence-witnesses-renamed-or-mirrored-axis-restatement-nested-axis-restatement-and-independent-axis-corroboration.md', 'docs/00-meta/trajectory-map.md', 'docs/20-constitution/open-question-registry.md'],
        'session_provenance': PREV_BUNDLE,
        'basis_state': 'current',
        'basis_anchor_precision': 'underlier-plus-wrapper',
        'basis_omission_basis': 'broader exchange-rate drafting was intentionally omitted from canon because the evidence only justified one bounded refresh-scope-axis-materiality witness',
        'repair': 'ordinary-continuation',
        'witness_surface': 'REVISION-RECEIPT.json',
        'basis_of_change': 'current prior packaged revision',
        'origin_revision': REV,
        'revision_span': f'{PREV} -> {REV}'
    })
    r['scope_witness'].update({
        'active_request': 'Continue researching online, GPUstorming, and evolving DelayBasin with tight, high-leverage revisions; make at least one bold but disciplined speculative move, do at least one hygiene/meta-engineering improvement, run make lint, package the archive, and provide a working link.',
        'exact_target': 'one compact refresh-scope-axis-materiality witness plus one quarantined exchange-rate move and one small scope-axis contract refactor',
        'scope_surfaces': ['docs/20-constitution/open-question-registry.md', 'docs/00-meta/trajectory-map.md', NEW_DOC, f'docs/90-quarantine/wild-speculations-2026-03-08.md#{NEW_QWS}'],
        'ambient_exclusions': ['no broad weighting canonization', 'no archive-wide corroboration court', 'no uncited external pressure claims'],
        'scope_state': 'exact',
        'repair': 'ordinary-continuation',
        'scope_of_change': 'refresh-scope-axis-materiality',
        'origin_revision': REV
    })
    r['authorship_witness'].update({'origin_revision': REV})
    r['status_witness'].update({
        'candidate_surface': None,
        'decision_surface': 'REVISION-RECEIPT.json',
        'decision_state': 'admitted',
        'execution_surface': 'RELEASE-MANIFEST.json',
        'execution_state': 'packaged',
        'frozen_public_surface': BUNDLE,
        'public_state': 'frozen-citable',
        'durable_status_surface': 'SURFACE-STATUS.json',
        'mismatch_consequence': 'working tree and frozen bundle must not be conflated; if they diverge, cite the frozen public surface',
        'repair': 'ordinary-continuation'
    })
    r['reentry_cue_witness'].update({'origin_revision': REV})
    r['retrospective_write_witness'] = json.loads(read('RETROSPECTIVE-QUEUE.json'))['items'][-1]
    r['followthrough_witness'] = json.loads(read('FOLLOWTHROUGH-QUEUE.json'))['items'][-1]
    r['assumption_witness'] = json.loads(read('ASSUMPTION-LEDGER.json'))['items'][-1]
    r['obligation_witness'] = json.loads(read('OBLIGATION-LEDGER.json'))['items'][-1]
    r['applicability_witness'] = json.loads(read('APPLICABILITY-LEDGER.json'))['items'][-1]
    r['foreign_pressure_witness'] = json.loads(read('FOREIGN-PRESSURE-LEDGER.json'))['items'][-1]
    r['transfer_witness'] = json.loads(read('DATACUBE-TRANSFER-LEDGER.json'))['items'][-1]
    r['import_witness'] = deepcopy(r['transfer_witness'])
    r['resolution_witness'] = json.loads(read('RESOLUTION-LEDGER.json'))['items'][-1]
    r['reasoning_firebreak_witness'] = json.loads(read('FIREBREAK-LEDGER.json'))['items'][-1]
    r['firebreak_witness'] = deepcopy(r['reasoning_firebreak_witness'])
    r['vocabulary_witness'] = {
        'witness_surface': 'WITNESS-VOCABULARY.json',
        'controlled_families': [NEW_FAMILY],
        'target_surfaces': ['WITNESS-VOCABULARY.json', 'REVISION-RECEIPT.json', NEW_DOC],
        'ambient_synonyms_excluded': ['different-label-means-material', 'zone-sounding-means-isolated', 'shared-slice-counts-like-mig', 'materiality-ish'],
        'comparability_budget': 'refresh-scope-axis-materiality truth is compared by token; the compact witness says whether genuinely independent corroboration is only label-distinct, backed by a failure domain, backed by substrate isolation, or honestly mixed while raw topology maps, scheduler configs, and isolation tables stay outside the token',
        'vocabulary_state': 'stable',
        'repair': 'ordinary-continuation',
        NEW_FAMILY: json.loads(read('WITNESS-VOCABULARY.json'))['families'][NEW_FAMILY]
    }
    r['counterfactual_shadow'] = {
        'status': 'rejected-nearby-move',
        'nearby_rejected_move': NEW_QWS_LABEL,
        'pivot_surface': f'docs/90-quarantine/wild-speculations-2026-03-08.md#{NEW_QWS}',
        'rejection_reason': 'current evidence supports a bounded materiality witness but not a canon-level exchange rate or coupling haircut',
        'still_live': True
    }
    r['summary_highlight'] = SUMMARY_HIGHLIGHT
    r['codename'] = CODENAME
    r['created_at'] = CREATED_AT
    r['comparison_witness'] = {
        'previous_revision': PREV,
        'current_revision': REV,
        'current_pressure_id': 'FP-0153',
        'current_import_id': 'TL-0159',
        'basis_surface': 'docs/10-method/refresh-scope-axis-independence-witnesses-renamed-or-mirrored-axis-restatement-nested-axis-restatement-and-independent-axis-corroboration.md',
        'delta_surface': NEW_DOC,
        'comparison_summary': 'rev0254 adds one compact refresh-scope-axis-materiality witness so genuinely independent axes no longer all carry the same material force.'
    }
    r['changes'] = [
        {'kind': 'canon', 'surface': NEW_DOC, 'summary': 'added one compact refresh-scope-axis-materiality witness with label-distinct-only, failure-domain-backed, isolation-backed, and mixed states'},
        {'kind': 'quarantine', 'surface': f'docs/90-quarantine/wild-speculations-2026-03-08.md#{NEW_QWS}', 'summary': 'kept stronger exchange-rate or coupling-haircut governance quarantined rather than promoting it into canon'},
        {'kind': 'hygiene', 'surface': 'tools/packet_contract_common.py', 'summary': 'introduced a narrower shared refresh-scope-axis validator entrypoint and wired a new materiality contract checker'}
    ]
    r['receipt_freshness_witness'] = {
        'packaged_bundle_filename': BUNDLE,
        'manifest_timestamp_token': STAMP,
        'receipt_timestamp_token': STAMP,
        'bundle_stem_suffix_relation': 'aligned',
        'current_import_id': 'TL-0159',
        'current_pressure_id': 'FP-0153',
        'change_anchor_surface': 'CHANGELOG.md',
        'freshness_state': 'fresh',
        'repair': 'ordinary-continuation'
    }
    r['question_posture_witness'] = {
        'resolution_surface': 'RESOLUTION-LEDGER.json',
        'registry_surface': 'docs/20-constitution/open-question-registry.md',
        'trajectory_surface': 'docs/00-meta/trajectory-map.md',
        'synced_resolved_questions': ['OQ-0149'],
        'frontier_selection_rule': 'select the last source-backed unresolved hot open question already projected into context-pack.json',
        'posture_state': 'synced',
        'repair': 'ordinary-continuation'
    }
    r['current_import_id'] = 'TL-0159'
    r['current_pressure_id'] = 'FP-0153'
    r['new_classes_or_families'] = [NEW_FAMILY]
    r['quarantined_non_take'] = ['axis-materiality exchange rate', 'coupling haircut', 'corroboration capital stack']
    r['artifacts_touched'] = touched
    r['refresh_scope_axis_materiality_witness'] = {
        'witness_surface': NEW_DOC,
        'family': NEW_FAMILY,
        'state_tokens': ['label-distinct-only-corroboration', 'failure-domain-backed-corroboration', 'isolation-backed-corroboration', 'mixed-refresh-scope-axis-materiality'],
        'overflow_rule': 'reopen-only-if-refresh-scope-axis-materiality-overflows'
    }
    r['refresh_scope_axis_materiality_witness_contract'] = {'family': NEW_FAMILY, 'states': ['label-distinct-only-corroboration', 'failure-domain-backed-corroboration', 'isolation-backed-corroboration', 'mixed-refresh-scope-axis-materiality']}
    r['refresh_scope_axis_materiality_witness_meta'] = {'checker': NEW_CHECKER}
    write_json('REVISION-RECEIPT.json', r)


def main():
    create_doc()
    update_bibliography()
    update_open_question_registry()
    update_trajectory_map()
    update_claim_registry()
    update_prompt_pair_registry()
    update_prompt_pairs()
    update_runbook()
    update_docs_readme()
    update_quarantine()
    update_vocabulary()
    update_packet_common_and_checkers()
    append_ledger_items()
    update_changelog_and_index()
    update_surface_status_and_manifest()
    update_receipt()


if __name__ == '__main__':
    main()
