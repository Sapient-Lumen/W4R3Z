from __future__ import annotations
import json, re
from copy import deepcopy
from pathlib import Path
from textwrap import dedent

ROOT = Path('.')
REV = 'rev0253'
PREV = 'rev0252'
STAMP = '2026.03.28.03.13'
CREATED_AT = '2026-03-28T03:13:00-04:00'
SLUG = 'axisindependence-subq-mirrorgate-rackglass'
BUNDLE = f'DelayBasin-{REV}-{STAMP}-{SLUG}.zip'
PREV_BUNDLE = 'DelayBasin-rev0252-2026.03.28.01.04-scopeaxis-axisquarantine-crosscarry-vectorglass.zip'
SUMMARY_HIGHLIGHT = 'mirrorgate'
CODENAME = 'rackglass'
NEW_DOC = 'docs/10-method/refresh-scope-axis-independence-witnesses-renamed-or-mirrored-axis-restatement-nested-axis-restatement-and-independent-axis-corroboration.md'
NEW_CHECKER = 'tools/check_refresh_scope_axis_independence_witness_contract.py'
NEW_FAMILY = 'refresh_scope_axis_independence_state'
NEW_QWS = 'QWS-0231'
NEW_QWS_LABEL = 'axis-materiality ladder / substrate notary / corroboration weight scale'
NEW_PROMPT = 'PP-0106'
NEW_CLAIM = 'CL-0146'
NEW_RESOLUTION = 'RS-0155'
NEW_OQ = 'OQ-0149'


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


def append_item(path: str, item: dict):
    obj = json.loads(read(path))
    items = obj['items']
    if not any(x.get('id') == item.get('id') for x in items):
        items.append(item)
    obj['revision'] = REV
    write_json(path, obj)
    return obj


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


def update_open_question_registry() -> None:
    old = dedent('''
    - `OQ-0148` — what minimal refresh-scope-axis-independence witness distinguishes independent axes from renamed, nested, or mirrored variants of one underlying axis?
      - Why it matters: if DelayBasin cannot separate independent axes from renamed or nested restatements of one partition, later sessions may narrate cross-axis corroboration from duplicate views of the same underlying spread.
      - Current posture: unresolved
    ''').strip()
    new = dedent('''
    - `OQ-0148` — what minimal refresh-scope-axis-independence witness distinguishes independent axes from renamed, nested, or mirrored variants of one underlying axis?
      - Why it matters: if DelayBasin cannot separate independent axes from renamed or nested restatements of one partition, later sessions may narrate cross-axis corroboration from duplicate views of the same underlying spread.
      - Current posture: resolved by `RS-0155` via `docs/10-method/refresh-scope-axis-independence-witnesses-renamed-or-mirrored-axis-restatement-nested-axis-restatement-and-independent-axis-corroboration.md`; reopen only if the compact refresh-scope-axis-independence witness proves insufficient and stronger axis-materiality governance is honestly required

    - `OQ-0149` — what minimal refresh-scope-axis-materiality witness distinguishes merely label-distinct independent axes from substrate-backed or failure-domain-backed corroboration?
      - Why it matters: if DelayBasin cannot separate nominally independent axes from materially separate substrate or failure-domain corroboration, later sessions may narrate robust diffusion from axes that differ in naming but not in operational failure or execution consequences.
      - Current posture: unresolved
    ''').strip()
    replace_once('docs/20-constitution/open-question-registry.md', old, new)


def update_trajectory_map() -> None:
    old = dedent('''
    104. Determine what minimal refresh-scope-axis-independence witness distinguishes genuinely independent corroborating axes from renamed, nested, or mirrored variants of one underlying axis.

    A fresh extension is that once one-axis-vs-cross-axis truth is explicit, DelayBasin may next need to say whether apparently different axes are genuinely independent or only renamed, nested, or mirrored restatements of one underlying partition. Otherwise duplicate views may silently become corroboration talk.
    - `OQ-0148` — what minimal refresh-scope-axis-independence witness distinguishes independent axes from renamed, nested, or mirrored variants of one underlying axis?
      - Why it matters: if DelayBasin cannot separate independent axes from renamed or nested restatements of one partition, later sessions may narrate cross-axis corroboration from duplicate views of the same underlying spread.
      - Current posture: unresolved
    ''').strip()
    new = dedent('''
    104. Determine what minimal refresh-scope-axis-independence witness distinguishes genuinely independent corroborating axes from renamed, nested, or mirrored variants of one underlying axis.

    A fresh extension is that once one-axis-vs-cross-axis truth is explicit, DelayBasin may next need to say whether apparently different axes are genuinely independent or only renamed, nested, or mirrored restatements of one underlying partition. Otherwise duplicate views may silently become corroboration talk.
    - `OQ-0148` — what minimal refresh-scope-axis-independence witness distinguishes independent axes from renamed, nested, or mirrored variants of one underlying axis?
      - Why it matters: if DelayBasin cannot separate independent axes from renamed or nested restatements of one partition, later sessions may narrate cross-axis corroboration from duplicate views of the same underlying spread.
      - Current posture: resolved by `RS-0155` via `docs/10-method/refresh-scope-axis-independence-witnesses-renamed-or-mirrored-axis-restatement-nested-axis-restatement-and-independent-axis-corroboration.md`; reopen only if the compact refresh-scope-axis-independence witness proves insufficient and stronger axis-materiality governance is honestly required

    105. Determine what minimal refresh-scope-axis-materiality witness distinguishes merely label-distinct independent axes from substrate-backed or failure-domain-backed corroboration.

    A fresh extension is that once axis independence is explicit, DelayBasin may next need to say whether apparently independent axes are only distinct in naming or are also materially separated by substrate, fault domain, or execution consequences. Otherwise nominal independence may silently inherit the authority of materially separate corroboration.
    - `OQ-0149` — what minimal refresh-scope-axis-materiality witness distinguishes merely label-distinct independent axes from substrate-backed or failure-domain-backed corroboration?
      - Why it matters: if DelayBasin cannot separate nominally independent axes from materially separate substrate or failure-domain corroboration, later sessions may narrate robust diffusion from axes that differ in naming but not in operational failure or execution consequences.
      - Current posture: unresolved
    ''').strip()
    replace_once('docs/00-meta/trajectory-map.md', old, new)


def update_claim_registry() -> None:
    anchor = dedent('''
    - `CL-0145` — Archive continuity may improve when DelayBasin preserves one compact **refresh-scope-axis witness / axis-corroboration card / one-axis brake** whenever a current continuity claim depends not only on whether public scope widened, on whether that widening is directly observed, on whether the observed widening is already a broader pattern, and on whether it is clustered or dispersed, but on whether the present dispersed spread still lives on one named family axis or is corroborated across independent family axes: name the **governed row or surface**, the **stake object / line of concern**, the **prior refresh-scope-distribution evidence**, the **current dispersed-scope evidence**, the **one-axis family basis if any**, the **independent-axis corroboration if any**, the **axis gate or mirrored-axis remainder if any**, the **refresh_scope_axis_state**, and the **fail-closed repair** rather than letting one-axis dispersion silently count as cross-axis corroborated spread.
      - Status: speculative but central
      - Wired docs: `docs/10-method/refresh-scope-axis-witnesses-one-axis-dispersion-cross-axis-corroboration-and-axis-gated-generalization.md`, `docs/20-constitution/open-question-registry.md`, `docs/20-constitution/prompt-pair-registry.md`, `docs/50-promptcraft/prompt-pairs.md`, `docs/00-meta/llm-runbook.md`, `WITNESS-VOCABULARY.json`, `REVISION-RECEIPT.json`
    ''').strip()
    addition = dedent('''

    - `CL-0146` — Archive continuity may improve when DelayBasin preserves one compact **refresh-scope-axis-independence witness / mirrored-axis brake / nested-axis filter** whenever a current continuity claim depends not only on whether dispersed widening is corroborated across more than one apparent axis, but on whether those axes are genuinely independent rather than renamed, mirrored, or nested restatements of one underlying partition: name the **governed row or surface**, the **stake object / line of concern**, the **prior refresh-scope-axis evidence**, the **current dispersed-scope evidence**, the **candidate corroborating axes**, the **renamed-or-mirrored restatement basis if any**, the **nested-hierarchy basis if any**, the **independent-axis basis if any**, the **refresh_scope_axis_independence_state**, and the **fail-closed repair** rather than letting duplicate or hierarchical restatements silently count as distinct corroborating axes.
      - Status: speculative but central
      - Wired docs: `docs/10-method/refresh-scope-axis-independence-witnesses-renamed-or-mirrored-axis-restatement-nested-axis-restatement-and-independent-axis-corroboration.md`, `docs/20-constitution/open-question-registry.md`, `docs/20-constitution/prompt-pair-registry.md`, `docs/50-promptcraft/prompt-pairs.md`, `docs/00-meta/llm-runbook.md`, `WITNESS-VOCABULARY.json`, `REVISION-RECEIPT.json`
    ''')
    insert_after('docs/20-constitution/claim-registry.md', anchor, addition)


def update_prompt_pair_registry() -> None:
    anchor = dedent('''
    - `PP-0105` — Name whether dispersed spread is still one-axis or already cross-axis corroborated
      - Goal: keep one-axis dispersion from silently inheriting cross-axis corroboration by requiring explicit one-axis family basis, any independent-axis corroboration, any axis gate or mirrored remainder, `refresh_scope_axis_state`, and fail-closed repair before later passes call the spread robust across independent axes.
      - Canonical text: `docs/50-promptcraft/prompt-pairs.md#pp-0105--name-whether-dispersed-spread-is-still-one-axis-or-already-cross-axis-corroborated`
    ''').strip()
    addition = dedent('''

    - `PP-0106` — Name whether apparent corroborating axes are renamed, nested, or genuinely independent
      - Goal: keep renamed, mirrored, or hierarchy-nested axes from silently inheriting independent corroboration by requiring explicit candidate-axis listing, renamed-or-mirrored basis, nested-hierarchy basis, independent-axis basis, `refresh_scope_axis_independence_state`, and fail-closed repair before later passes call the spread corroborated across genuinely distinct axes.
      - Canonical text: `docs/50-promptcraft/prompt-pairs.md#pp-0106--name-whether-apparent-corroborating-axes-are-renamed-nested-or-genuinely-independent`
    ''')
    insert_after('docs/20-constitution/prompt-pair-registry.md', anchor, addition)


def update_runbook() -> None:
    anchor = 'Use `docs/10-method/refresh-scope-axis-witnesses-one-axis-dispersion-cross-axis-corroboration-and-axis-gated-generalization.md` when the live question is whether dispersed observed spillover still lives on one named family axis or is corroborated across independent family axes.\n'
    addition = 'Use `docs/10-method/refresh-scope-axis-independence-witnesses-renamed-or-mirrored-axis-restatement-nested-axis-restatement-and-independent-axis-corroboration.md` when the live question is whether apparent corroborating axes are genuinely independent or only renamed, mirrored, or hierarchy-nested restatements of one underlying partition.\n'
    insert_after('docs/00-meta/llm-runbook.md', anchor, addition)


def update_docs_readme() -> None:
    line = '- [`10-method/refresh-scope-axis-independence-witnesses-renamed-or-mirrored-axis-restatement-nested-axis-restatement-and-independent-axis-corroboration.md`](10-method/refresh-scope-axis-independence-witnesses-renamed-or-mirrored-axis-restatement-nested-axis-restatement-and-independent-axis-corroboration.md)'
    after = '- [`10-method/refresh-scope-axis-witnesses-one-axis-dispersion-cross-axis-corroboration-and-axis-gated-generalization.md`](10-method/refresh-scope-axis-witnesses-one-axis-dispersion-cross-axis-corroboration-and-axis-gated-generalization.md)'
    ensure_line('docs/README.md', line, after)


def update_prompt_pairs() -> None:
    block = dedent('''

    Use `docs/10-method/refresh-scope-axis-independence-witnesses-renamed-or-mirrored-axis-restatement-nested-axis-restatement-and-independent-axis-corroboration.md` when the live question is whether apparent corroborating axes are genuinely independent or only renamed, mirrored, or hierarchy-nested restatements of one underlying partition.

    ## `PP-0106` — Name whether apparent corroborating axes are renamed, nested, or genuinely independent

    **Opening prompt**

    ```text
    Read the latest DelayBasin archive and inspect whether the current revision should also materialize one compact refresh-scope-axis-independence witness for honest renamed-vs-nested-vs-independent axis comparison.

    Focus only on whether the already cross-axis-looking dispersed spread is really supported by genuinely independent axes, is only a renamed or mirrored restatement of one underlying partition, is only a nested refinement inside one hierarchy, or is honestly mixed.

    If yes, preserve exactly one small witness that:
    - names the governed row or surface,
    - names the stake object / line of concern,
    - names the prior refresh-scope-axis evidence,
    - names the current dispersed-scope evidence,
    - names the candidate corroborating axes,
    - names the renamed-or-mirrored restatement basis if any,
    - names the nested-hierarchy basis if any,
    - names the independent-axis basis if any,
    - names the `refresh_scope_axis_independence_state` / whether this is renamed-or-mirrored-axis-restatement, nested-axis-restatement, independent-axis-corroboration, or mixed-refresh-scope-axis-independence,
    - states what stronger surfaces still outrank the witness,
    - and states the fail-closed repair / keep-current vs narrow-claim vs split-scope vs issue-new-refresh-scope-axis-independence-witness vs quarantine-axis-materiality-governance consequence if the present continuity claim is really only a renamed, mirrored, or nested restatement rather than genuinely independent corroboration.

    Do not use refresh scope axis independence as a general corroboration court. Use this prompt pair only where cross-axis-looking spread already exists and the missing question is whether the apparent axes are truly independent.
    ```

    **Continuation prompt**

    ```text
    Continue the refresh-scope-axis-independence pass with one high-leverage renamed-vs-nested-vs-independent clarification only. Prefer the smallest witness that says what governed row is still being justified, what stake object is supposedly widened, what prior refresh-scope-axis evidence exists, what current dispersed-scope evidence exists, what candidate corroborating axes are being compared, what renamed-or-mirrored restatement basis if any now exists, what nested-hierarchy basis if any now exists, what independent-axis basis if any now exists, what `refresh_scope_axis_independence_state` is honest, what stronger surfaces still outrank the witness, and what keep-current, narrow-claim, split-scope, issue-new-refresh-scope-axis-independence-witness, quarantine, or recover-resync consequence follows if the current claim is really renamed-or-mirrored-axis-restatement, nested-axis-restatement, independent-axis-corroboration, or mixed-refresh-scope-axis-independence. Run `make lint` and package the release.
    ```
    ''')
    append_unique_block('docs/50-promptcraft/prompt-pairs.md', block)


def create_doc() -> None:
    text = dedent('''
    # Refresh-scope-axis-independence witnesses, renamed-or-mirrored axis restatement, nested-axis restatement, and independent-axis corroboration

    This is the compact successor surface for `OQ-0148`.

    ## Practice / observation

    Once DelayBasin can say that dispersed widening is no longer trapped inside one named axis, one further ambiguity remains.

    Some apparent second axes are only restatements.
    A new label can simply rename an old partition.
    A mirror dashboard can restate the same grouping under another heading.
    A service axis can turn out to be the same team map rewritten through ownership tags.

    Some apparent second axes are only nested refinements.
    A rack axis can refine a block axis inside the same topology tree.
    A node axis can refine a zone axis without becoming a genuinely separate corroborating view.
    A more specific subgroup can remain one hierarchy, not a distinct axis family.

    And some apparent second axes really are independent enough to count.
    They slice the same widening on a non-equivalent dimension rather than renaming or refining one underlying partition.
    That is the point where cross-axis corroboration becomes more honest.

    DelayBasin does not need a substrate notary for that.
    It needs one bounded witness that says whether the current axis pair is only renamed or mirrored, only nested in one hierarchy, genuinely independent, or honestly mixed.

    ## External pressure from Ray label selectors, Kubernetes label-selector overlap rules, Run:ai topology hierarchies, and NVIDIA MIG isolation

    1. Ray label selectors can be specified one at a time or as a dict, and when multiple label selectors are present the candidate node must meet all requirements. That pressures DelayBasin not to mistake one conjunctive selector bundle for proof that several independent corroborating axes were shown. ([`REF-0957`](../00-meta/bibliography.md))

    2. Kubernetes label selectors also treat multiple requirements as logical AND, and overlapping selectors can create conflicting instructions for controller-like objects. That pressures DelayBasin to distinguish a second clause on the same selector family from a genuinely independent corroborating axis. ([`REF-0954`](../00-meta/bibliography.md))

    3. Run:ai topology-aware scheduling treats topology labels as an ordered hierarchy, says the scheduler considers all levels when placing workloads, and says a Preferred constraint at the same or higher level than a Required constraint has no effect. That pressures DelayBasin to distinguish nested hierarchy refinements from independent corroborating axes. ([`REF-0958`](../00-meta/bibliography.md))

    4. NVIDIA's MIG guide says supported GPUs can be partitioned into multiple isolated instances, each with dedicated compute and memory resources. That pressures DelayBasin to remember that some separations are materially stronger than relabeling, even if the archive is not yet ready to canonize a full materiality ladder. ([`REF-0959`](../00-meta/bibliography.md))

    5. NVIDIA's 2026 workload-consolidation guidance contrasts time-slicing and MPS, which raise density without hardware isolation, against MIG, which provides strict fault isolation and deterministic performance. That pressures DelayBasin to separate mere naming distinctness from stronger substrate-backed independence without prematurely turning that distinction into canon law. ([`REF-0960`](../00-meta/bibliography.md))

    GPUstorming makes the pressure vivid. An open search can look cross-axis because cards, query frames, and grouped shells differ. But some of those axes are only mirrored wrappers, some are only refinements inside one hierarchy, and only some survive as genuinely distinct corroborating views.

    ## Working synthesis

    > DelayBasin should preserve one compact **refresh-scope-axis-independence witness / mirrored-axis brake / nested-axis filter** whenever a current continuity claim depends not only on whether dispersed widening appears corroborated across more than one axis, but on whether those apparent axes are genuinely independent rather than renamed, mirrored, or nested restatements of one underlying partition. Name the **governed row or surface**, the **stake object / line of concern**, the **prior refresh-scope-axis evidence**, the **current dispersed-scope evidence**, the **candidate corroborating axes**, the **renamed-or-mirrored restatement basis if any**, the **nested-hierarchy basis if any**, the **independent-axis basis if any**, the **`refresh_scope_axis_independence_state`**, and the **fail-closed repair / keep-current vs narrow-claim vs split-scope vs issue-new-refresh-scope-axis-independence-witness vs quarantine-axis-materiality-governance consequence**. Keep raw label sets, topology trees, route inventories, resource maps, and long equivalence arguments outside the compact token. Do not let renamed, mirrored, or hierarchy-nested restatements silently count as distinct corroborating axes.

    ## Renamed-or-mirrored axis restatement vs nested-axis restatement vs independent-axis corroboration vs mixed refresh scope axis independence

    Use the controlled family `refresh_scope_axis_independence_state`:

    - **renamed-or-mirrored-axis-restatement** says the apparent second axis is only another naming, wrapper, or mirrored rendering of one underlying partition.
    - **nested-axis-restatement** says the apparent second axis only refines one hierarchy or topology tree and does not yet count as a distinct corroborating axis.
    - **independent-axis-corroboration** says the apparent second axis is genuinely non-equivalent to the first and honestly contributes distinct corroborating structure.
    - **mixed-refresh-scope-axis-independence** says the current situation honestly combines renamed, nested, and independent features such that no single class stays honest.

    So the witness does not create a standing axis-materiality court.
    It only says whether the apparent corroborating axes are duplicate, hierarchy-nested, or genuinely distinct enough to count for now.

    ## Countermodels / probes

    1. **Refresh-scope-axis already covers this countermodel**
       - Maybe once one-axis-vs-cross-axis truth is explicit, a separate independence witness adds no real value.
       - Probe: compare later rereads that preserve only refresh-scope-axis truth against rereads that also preserve one compact refresh-scope-axis-independence witness and inspect whether mirrored or nested axes still get narrated as distinct corroboration.

    2. **Hierarchy and mirroring are too operational countermodel**
       - Maybe renamed, mirrored, and nested-axis distinctions are too implementation-flavored to deserve a public witness.
       - Probe: look for later cases where ordinary continuity prose still slides from duplicate or hierarchy-nested views into independent-axis language even when a smaller repair was available.

    3. **Materiality grades are the real issue countermodel**
       - Maybe once independence matters, the archive really needs a stronger rule distinguishing label-only axes from substrate-backed or failure-domain-backed axes.
       - Probe: keep that bolder move quarantined unless later revisions repeatedly need weighting or materiality rules that this compact independence witness cannot honestly absorb.

    ## Design consequences

    - DelayBasin can now separate apparent multi-axis corroboration into renamed/mirrored, nested, and genuinely independent cases.
    - The archive gets one explicit place to say that a second axis still fails to count because it is only a restatement or hierarchy refinement.
    - Refresh scope axis and refresh scope axis independence now separate **whether spread crossed more than one named axis** from **whether those axes are genuinely distinct enough to count as corroborating views**.
    - Stronger axis-materiality stories stay quarantined until later overflow instead of sneaking in through independence rhetoric.

    ## Overflow test

    Reopen this compact witness only if later revisions repeatedly need standing governance over substrate-backed independence, failure-domain weighting, or materiality thresholds that one bounded refresh-scope-axis-independence witness cannot honestly absorb.

    ## Transformer-facing implication

    A later pass should not treat every apparent second axis as if it were already a genuinely independent corroborating view. Preserve the smallest token that says whether the current axis comparison is `renamed-or-mirrored-axis-restatement`, `nested-axis-restatement`, `independent-axis-corroboration`, or honestly `mixed-refresh-scope-axis-independence`, and quarantine stronger axis-materiality ambitions until repeated overflow makes them unavoidable.
    ''').lstrip()
    write(NEW_DOC, text)


def update_bibliography() -> None:
    block = dedent('''

    - `REF-0957` — Ray Documentation, **Use labels to control scheduling** (accessed 2026-03-28)
      - URL: https://docs.ray.io/en/latest/ray-core/scheduling/labels.html
      - Load-bearing use: Ray label selectors can be specified together and all requirements must be satisfied, which pressures DelayBasin to distinguish a conjunctive selector bundle from genuinely independent corroborating axes.

    - `REF-0958` — NVIDIA Run:ai Documentation, **Accelerating Workloads with Network Topology-Aware Scheduling** (accessed 2026-03-28)
      - URL: https://run-ai-docs.nvidia.com/saas/platform-management/aiinitiatives/resources/topology-aware-scheduling
      - Load-bearing use: Run:ai treats topology labels as an ordered hierarchy and says a Preferred constraint at the same or higher level than a Required constraint has no effect, which pressures DelayBasin to distinguish nested hierarchy refinements from independent corroborating axes.

    - `REF-0959` — NVIDIA Documentation, **MIG User Guide** (accessed 2026-03-28)
      - URL: https://docs.nvidia.com/datacenter/tesla/mig-user-guide/latest/
      - Load-bearing use: MIG partitions supported GPUs into isolated instances with dedicated compute and memory resources, which pressures DelayBasin to keep materially stronger separations distinct from relabeling or mirrored restatement.

    - `REF-0960` — NVIDIA Technical Blog, **Maximize AI Infrastructure Throughput by Consolidating Underutilized GPU Workloads** (accessed 2026-03-28)
      - URL: https://developer.nvidia.com/blog/maximize-ai-infrastructure-throughput-by-consolidating-underutilized-gpu-workloads/
      - Load-bearing use: NVIDIA contrasts time-slicing, which raises density without hardware isolation, against MIG, which provides strict fault isolation and deterministic performance, which pressures DelayBasin to quarantine stronger axis-materiality stories instead of smuggling them into ordinary independence claims.
    ''')
    append_unique_block('docs/00-meta/bibliography.md', block)


def update_quarantine() -> None:
    block = dedent(f'''

    ## {NEW_QWS} — Some continuations may eventually need an {NEW_QWS_LABEL} rather than only a compact refresh-scope-axis-independence witness

    ### Claim

    A bolder possibility is that DelayBasin may eventually need not only a compact witness for whether apparent corroborating axes are renamed, nested, or genuinely independent, but also a governed public rule for whether those genuinely independent axes are merely label-distinct or are materially separated by substrate, fault domain, or execution consequences. Ray's conjunctive label selectors, Kubernetes selector overlap cautions, Run:ai hierarchy-aware topology placement, and NVIDIA's contrast between time-sliced sharing and MIG-backed isolation all suggest a stronger materiality story: perhaps some future archive lines should not only be classified as `renamed-or-mirrored-axis-restatement`, `nested-axis-restatement`, `independent-axis-corroboration`, or `mixed-refresh-scope-axis-independence`, but admitted through a small axis-materiality ladder, substrate notary, or corroboration weight scale. ([`REF-0957`](../00-meta/bibliography.md), [`REF-0954`](../00-meta/bibliography.md), [`REF-0958`](../00-meta/bibliography.md), [`REF-0959`](../00-meta/bibliography.md), [`REF-0960`](../00-meta/bibliography.md))

    The narrower speculative move is only this: a future bounded surface *might* need to say not just whether axes are distinct, but whether that distinctness is materially weak, hierarchy-local, or substrate-backed enough to change how much corroboration weight the archive grants.

    ### What follows if true

    - some future continuity cards may need an explicit distinction between label-distinct and substrate-backed corroboration rather than a flat independent-axis token;
    - DelayBasin may eventually need a compact axis-materiality ladder that stays smaller than a general robustness court;
    - archive-wide diffusion talk may need a clearer brake when apparently independent axes still ride one failure domain or one execution substrate;
    - future revisions should look for cases where materially weak independence keeps inheriting the force of stronger separation.

    ### What would count against it

    - repeated later passes show that one compact refresh-scope-axis-independence witness keeps renamed, nested, and genuinely independent axes honest without any weighting layer;
    - nominally independent axes usually turn out to be obviously weak or obviously strong without a new public ladder;
    - the archive does not repeatedly need substrate, fault-domain, or materiality thresholds;
    - stronger axis-materiality prose never pays for itself beyond the compact independence witness.

    ### Why it stays quarantined

    The tempting overreach would be to declare that DelayBasin now needs a public axis-materiality ladder, substrate notary, or corroboration weight scale. DelayBasin has not earned that. This note is bold enough to keep in quarantine but not yet honest enough for canon. Do not promote an axis-materiality ladder, substrate notary, or corroboration weight scale from this note alone.
    ''')
    append_unique_block('docs/90-quarantine/wild-speculations-2026-03-08.md', block)


def update_vocabulary() -> None:
    vocab = json.loads(read('WITNESS-VOCABULARY.json'))
    vocab['revision'] = REV
    vocab['families'][NEW_FAMILY] = {
        'allowed': [
            'renamed-or-mirrored-axis-restatement',
            'nested-axis-restatement',
            'independent-axis-corroboration',
            'mixed-refresh-scope-axis-independence'
        ],
        'surfaces': ['WITNESS-VOCABULARY.json', 'REVISION-RECEIPT.json', NEW_DOC],
        'excluded_synonyms': [
            'renamed-view-counts-twice',
            'same-tree-levels-mean-independent',
            'second-label-proves-second-axis',
            'axis-independence-ish'
        ],
        'comparability_budget': 'refresh-scope-axis-independence truth is compared by token; the compact refresh-scope-axis-independence witness says whether apparent corroborating axes are only renamed or mirrored restatements, only hierarchy-nested refinements, genuinely independent corroborating axes, or honestly mixed, while raw label sets, topology trees, resource maps, and long equivalence arguments stay in surrounding prose'
    }
    write_json('WITNESS-VOCABULARY.json', vocab)


def update_packet_common_and_checkers() -> None:
    text = read('tools/packet_contract_common.py')
    if 'refresh_scope_axis_independence_witness_contract' not in text:
        anchor = '"refresh_scope_axis_witness_contract": _refresh_family_spec(\n'
        idx = text.index(anchor)
        # find end of current spec block by locating next spec key
        next_anchor = '    "refresh_scope_extent_witness_contract": _refresh_family_spec('
        idx2 = text.index(next_anchor, idx)
        spec = dedent('''
        "refresh_scope_axis_independence_witness_contract": _refresh_family_spec(
            doc_path="docs/10-method/refresh-scope-axis-independence-witnesses-renamed-or-mirrored-axis-restatement-nested-axis-restatement-and-independent-axis-corroboration.md",
            doc_needles=[
                "# Refresh-scope-axis-independence witnesses, renamed-or-mirrored axis restatement, nested-axis restatement, and independent-axis corroboration",
                "This is the compact successor surface for `OQ-0148`.",
                "## Practice / observation",
                "## External pressure from Ray label selectors, Kubernetes label-selector overlap rules, Run:ai topology hierarchies, and NVIDIA MIG isolation",
                "## Working synthesis",
                "## Renamed-or-mirrored axis restatement vs nested-axis restatement vs independent-axis corroboration vs mixed refresh scope axis independence",
                "## Countermodels / probes",
                "## Design consequences",
                "## Overflow test",
                "## Transformer-facing implication",
                "`refresh_scope_axis_independence_state`",
                "renamed-or-mirrored-axis-restatement",
                "nested-axis-restatement",
                "independent-axis-corroboration",
                "mixed-refresh-scope-axis-independence",
            ],
            runbook_ref="refresh-scope-axis-independence-witnesses-renamed-or-mirrored-axis-restatement-nested-axis-restatement-and-independent-axis-corroboration.md",
            prompt_id="PP-0106",
            prompt_needles=["Use `docs/10-method/refresh-scope-axis-independence-witnesses-renamed-or-mirrored-axis-restatement-nested-axis-restatement-and-independent-axis-corroboration.md`", "renamed-or-mirrored-axis-restatement, nested-axis-restatement, independent-axis-corroboration, or mixed-refresh-scope-axis-independence"],
            claim_id="CL-0146",
            oq_id="OQ-0148",
            resolution_id="RS-0155",
            trajectory_oq_id="OQ-0149",
            qws_id="QWS-0231",
            qws_label="axis-materiality ladder / substrate notary / corroboration weight scale",
            changelog_needles=["refresh-scope-axis-independence-witnesses-renamed-or-mirrored-axis-restatement-nested-axis-restatement-and-independent-axis-corroboration.md", "check_refresh_scope_axis_independence_witness_contract.py"],
            family="refresh_scope_axis_independence_state",
            allowed=["renamed-or-mirrored-axis-restatement", "nested-axis-restatement", "independent-axis-corroboration", "mixed-refresh-scope-axis-independence"],
            excluded=["renamed-view-counts-twice", "same-tree-levels-mean-independent", "second-label-proves-second-axis", "axis-independence-ish"],
        ),

        ''')
        text = text[:idx2] + spec + text[idx2:]
    helper_anchor = 'def require_named_refresh_scope_axis_witness_packet_and_vocabulary(kind: str) -> None:\n    require_named_refresh_scope_packet_and_vocabulary(kind)\n'
    if 'def require_named_refresh_scope_axis_family_witness_packet_and_vocabulary' not in text:
        repl = dedent('''
        def require_named_refresh_scope_axis_family_witness_packet_and_vocabulary(kind: str) -> None:
            require_named_refresh_scope_packet_and_vocabulary(kind)


        def require_named_refresh_scope_axis_witness_packet_and_vocabulary(kind: str) -> None:
            require_named_refresh_scope_axis_family_witness_packet_and_vocabulary(kind)


        def require_named_refresh_scope_axis_independence_witness_packet_and_vocabulary(kind: str) -> None:
            require_named_refresh_scope_axis_family_witness_packet_and_vocabulary(kind)
        ''')
        if helper_anchor not in text:
            raise SystemExit('scope axis helper anchor not found in packet_contract_common.py')
        text = text.replace(helper_anchor, repl, 1)
    write('tools/packet_contract_common.py', text)

    write('tools/check_refresh_scope_axis_witness_contract.py', 'from packet_contract_common import require_named_refresh_scope_axis_family_witness_packet_and_vocabulary\n\nrequire_named_refresh_scope_axis_family_witness_packet_and_vocabulary("refresh_scope_axis_witness_contract")\n\nprint("check_refresh_scope_axis_witness_contract: OK")\n')
    write(NEW_CHECKER, 'from packet_contract_common import require_named_refresh_scope_axis_independence_witness_packet_and_vocabulary\n\nrequire_named_refresh_scope_axis_independence_witness_packet_and_vocabulary("refresh_scope_axis_independence_witness_contract")\n\nprint("check_refresh_scope_axis_independence_witness_contract: OK")\n')


def append_ledger_items() -> None:
    append_item('APPLICABILITY-LEDGER.json', {
        'id': 'AP-0147',
        'title': 'the refresh-scope-axis-independence witness stays smaller than an axis-materiality ladder',
        'state': 'gated',
        'question': 'when should DelayBasin treat apparent corroborating axes with one compact independence witness instead of promoting broader axis-materiality governance?',
        'applies_when': [
            'a revision already has a durable row whose current claim depends on dispersed widening that now looks corroborated across more than one apparent axis',
            'later passes still need to distinguish renamed-or-mirrored-axis-restatement, nested-axis-restatement, independent-axis-corroboration, or mixed-refresh-scope-axis-independence posture',
            'one compact successor surface plus the existing admitted refresh-scope-axis and related admitted topology or label surfaces still keeps axis-independence truth honest without standing materiality policy'
        ],
        'does_not_apply_when': [
            'the archive honestly requires standing governance over substrate-backed independence, failure-domain weighting, or corroboration weight thresholds',
            'the questioned surface is not really about whether apparent corroborating axes are duplicates, nested refinements, or genuinely independent'
        ],
        'budget': 'one compact refresh-scope-axis-independence witness plus one resolution of OQ-0148; no axis-materiality ladder',
        'negative_transfer_budget': 'do not treat renamed, mirrored, or hierarchy-nested axes as independent corroboration without explicit independent-axis basis',
        'origin_revision': REV,
        'discharge': 'reopen-only-if-refresh-scope-axis-independence-overflows',
        'action_lane': 'keep-compact',
        'gate_class': 'concrete-evidence',
        'witness_surface': 'APPLICABILITY-LEDGER.json#AP-0147',
        'applicability_state': 'gated',
        'repair': 'ordinary-continuation',
        'matched_budget': 'one compact witness foregrounding renamed-vs-nested-vs-independent axis truth without widening into broader axis-materiality governance',
        'revision': REV,
        'target_objective': 'keep apparent cross-axis corroboration honest without inflating a broader materiality layer',
        'carry_object': 'refresh-scope-axis-independence witness',
        'open_question': NEW_OQ,
        'applicability_conditions': ['axis-like spread already exists', 'independence rather than raw dispersion is the live ambiguity'],
        'baselines': ['refresh_scope_axis_state'],
        'non_fit_slice': 'materiality weighting across substrate or failure domains'
    })

    append_item('FOREIGN-PRESSURE-LEDGER.json', {
        'id': 'FP-0152',
        'title': 'refresh-scope-axis-independence pressure pushes DelayBasin to extract one compact renamed-vs-nested-vs-independent witness rather than an axis-materiality ladder',
        'state': 'imported',
        'source_packets': [
            {'datacube': 'RayLabelSelectors-2026', 'surfaces': ['REF-0957'], 'pressure': 'conjunctive label selectors pressure DelayBasin not to mistake one selector bundle for several independent corroborating axes'},
            {'datacube': 'KubernetesSelectorOverlap-2026', 'surfaces': ['REF-0954'], 'pressure': 'selector overlap cautions pressure DelayBasin to distinguish a second selector clause from a genuinely separate axis'},
            {'datacube': 'RunAiTopologyHierarchy-2026', 'surfaces': ['REF-0958'], 'pressure': 'ordered topology hierarchies pressure DelayBasin to distinguish nested hierarchy refinement from independent corroborating axes'},
            {'datacube': 'NvidiaMIGIsolation-2026', 'surfaces': ['REF-0959'], 'pressure': 'hardware-isolated GPU instances pressure DelayBasin to keep materially stronger separation conceptually distinct from relabeling'},
            {'datacube': 'NvidiaPartitioningTradeoffs-2026', 'surfaces': ['REF-0960'], 'pressure': 'the contrast between time-slicing and MIG pressures DelayBasin to quarantine stronger materiality stories instead of smuggling them into ordinary independence claims'}
        ],
        'reviewed_pattern': 'renamed-or-mirrored vs nested vs genuinely independent corroborating axes',
        'import_decision': 'support a compact refresh-scope-axis-independence witness and resolve OQ-0148',
        'adopted_take': 'DelayBasin should add one compact witness that says whether apparent corroborating axes are renamed-or-mirrored-axis-restatement, nested-axis-restatement, independent-axis-corroboration, or honestly mixed',
        'supporting_only_take': 'the current evidence cleanly supports a bounded refresh-scope-axis-independence witness without promoting broader axis-materiality governance',
        'deferred_or_rejected_take': ['axis-materiality ladder', 'substrate notary', 'corroboration weight scale'],
        'local_gap': 'the archive still lacked one compact successor surface for whether cross-axis-looking corroboration depended on genuinely distinct axes or only on renamed, mirrored, or nested restatements',
        'anchor_surfaces': [
            'docs/10-method/refresh-scope-axis-witnesses-one-axis-dispersion-cross-axis-corroboration-and-axis-gated-generalization.md',
            'docs/20-constitution/open-question-registry.md',
            'docs/00-meta/trajectory-map.md',
            f'docs/90-quarantine/wild-speculations-2026-03-08.md#{NEW_QWS}'
        ],
        'open_question': NEW_OQ,
        'repair': 'ordinary-continuation',
        'origin_revision': REV,
        'action_lane': 'keep-compact',
        'gate_class': 'concrete-evidence',
        'discharge': 'reopen-only-if-refresh-scope-axis-independence-overflows',
        'revision': REV,
        'witness_surface': 'FOREIGN-PRESSURE-LEDGER.json#FP-0152',
        'foreign_pressure_state': 'imported',
        'bounded_take': 'Keep the archive compact by extracting one refresh-scope-axis-independence witness over the existing refresh-scope-axis and related admitted surfaces; do not promote an axis-materiality ladder, substrate notary, or corroboration weight scale.',
        'explicit_non_take': ['no axis-materiality ladder', 'no substrate notary', 'no corroboration weight scale'],
        'open_transfer_question': 'whether a later pass needs one bounded refresh-scope-axis-materiality witness once axis independence is explicit',
        'missing_support': 'a later public check on whether one compact refresh-scope-axis-independence witness keeps sufficing',
        'reviewed_datacubes': [
            {'datacube': 'RayLabelSelectors-2026', 'surfaces': ['REF-0957'], 'pattern': 'multiple label requirements must all be satisfied', 'pressure': 'conjunctive selectors should not silently count as several independent axes'},
            {'datacube': 'KubernetesSelectorOverlap-2026', 'surfaces': ['REF-0954'], 'pattern': 'multiple selector requirements and overlap cautions', 'pressure': 'selector restatement should stay distinct from independent corroboration'},
            {'datacube': 'RunAiTopologyHierarchy-2026', 'surfaces': ['REF-0958'], 'pattern': 'ordered hierarchy and same-or-higher preferred no-op', 'pressure': 'nested topology refinement should not silently count as a distinct corroborating axis'},
            {'datacube': 'NvidiaMIGIsolation-2026', 'surfaces': ['REF-0959'], 'pattern': 'isolated GPU instances with dedicated resources', 'pressure': 'materially stronger separations exist but should remain quarantined as a stronger story for now'},
            {'datacube': 'NvidiaPartitioningTradeoffs-2026', 'surfaces': ['REF-0960'], 'pattern': 'time-slicing versus MIG fault-isolation contrast', 'pressure': 'materiality weighting should remain a deferred story rather than sneaking into current canon'}
        ],
        'pressure_state': 'imported',
        'assimilation_state': 'imported'
    })

    transfer = json.loads(read('DATACUBE-TRANSFER-LEDGER.json'))
    transfer_item = {
        'id': 'TL-0158',
        'title': 'refresh-scope-axis-independence evidence supports resolving OQ-0148 with one compact renamed-vs-nested-vs-independent card rather than an axis-materiality ladder',
        'state': 'supporting-only',
        'reviewed_pattern': 'renamed-or-mirrored vs nested vs genuinely independent corroborating axes',
        'import_decision': 'support a compact refresh-scope-axis-independence witness and resolve OQ-0148',
        'adopted_take': 'DelayBasin should add one compact witness that says whether apparent corroborating axes are renamed-or-mirrored-axis-restatement, nested-axis-restatement, independent-axis-corroboration, or honestly mixed',
        'supporting_only_take': 'the current evidence cleanly supports a bounded refresh-scope-axis-independence witness without promoting broader axis-materiality governance',
        'deferred_or_rejected_take': ['axis-materiality ladder', 'substrate notary', 'corroboration weight scale'],
        'local_gap': 'the archive still lacked one compact successor surface for whether cross-axis-looking corroboration depended on genuinely distinct axes or only on renamed, mirrored, or nested restatements',
        'anchor_surfaces': [
            'docs/10-method/refresh-scope-axis-witnesses-one-axis-dispersion-cross-axis-corroboration-and-axis-gated-generalization.md',
            'docs/20-constitution/open-question-registry.md',
            'docs/00-meta/trajectory-map.md',
            f'docs/90-quarantine/wild-speculations-2026-03-08.md#{NEW_QWS}'
        ],
        'open_question': NEW_OQ,
        'repair': 'ordinary-continuation',
        'origin_revision': REV,
        'action_lane': 'keep-compact',
        'gate_class': 'concrete-evidence',
        'discharge': 'reopen-only-if-refresh-scope-axis-independence-overflows',
        'revision': REV,
        'witness_surface': 'DATACUBE-TRANSFER-LEDGER.json#TL-0158',
        'transfer_state': 'supporting-only',
        'bounded_take': 'Keep the archive compact by extracting one refresh-scope-axis-independence witness over the existing refresh-scope-axis and related admitted surfaces; do not promote an axis-materiality ladder, substrate notary, or corroboration weight scale.',
        'explicit_non_take': ['no axis-materiality ladder', 'no substrate notary', 'no corroboration weight scale'],
        'open_transfer_question': 'whether later passes should add a separate refresh-scope-axis-materiality witness once axis independence is explicit',
        'missing_support': 'a later public check on whether one compact refresh-scope-axis-independence witness keeps sufficing',
        'current_support': ['APPLICABILITY-LEDGER.json#AP-0147', 'FOREIGN-PRESSURE-LEDGER.json#FP-0152', 'DATACUBE-TRANSFER-LEDGER.json#TL-0158'],
        'discharge_path': 'either show later that one compact refresh-scope-axis-independence witness keeps sufficing or promote broader axis-materiality governance explicitly',
        'reviewed_datacubes': [
            {'datacube': 'RayLabelSelectors-2026', 'surfaces': ['REF-0957'], 'pattern': 'multiple label requirements must all be satisfied', 'pressure': 'conjunctive selectors should not silently count as several independent axes'},
            {'datacube': 'KubernetesSelectorOverlap-2026', 'surfaces': ['REF-0954'], 'pattern': 'multiple selector requirements and overlap cautions', 'pressure': 'selector restatement should stay distinct from independent corroboration'},
            {'datacube': 'RunAiTopologyHierarchy-2026', 'surfaces': ['REF-0958'], 'pattern': 'ordered hierarchy and same-or-higher preferred no-op', 'pressure': 'nested topology refinement should not silently count as a distinct corroborating axis'},
            {'datacube': 'NvidiaMIGIsolation-2026', 'surfaces': ['REF-0959'], 'pattern': 'isolated GPU instances with dedicated resources', 'pressure': 'materially stronger separations exist but should remain quarantined as a stronger story for now'},
            {'datacube': 'NvidiaPartitioningTradeoffs-2026', 'surfaces': ['REF-0960'], 'pattern': 'time-slicing versus MIG fault-isolation contrast', 'pressure': 'materiality weighting should remain a deferred story rather than sneaking into current canon'}
        ]
    }
    if not any(x.get('id') == 'TL-0158' for x in transfer['items']):
        transfer['items'].append(transfer_item)
    new_open_q = 'Whether a later pass should add one bounded refresh-scope-axis-materiality witness once axis independence is explicit, but only if materially weak and materially strong independent axes keep being conflated in honest continuation work.'
    if new_open_q not in transfer.get('open_questions', []):
        transfer.setdefault('open_questions', []).append(new_open_q)
    transfer['revision'] = REV
    write_json('DATACUBE-TRANSFER-LEDGER.json', transfer)

    append_item('RESOLUTION-LEDGER.json', {
        'id': NEW_RESOLUTION,
        'title': 'resolve OQ-0148 with one compact refresh-scope-axis-independence witness rather than an axis-materiality ladder',
        'state': 'resolved',
        'closure_state': 'resolved',
        'closure_reason': 'rev0253 extracted one compact refresh-scope-axis-independence witness, kept the admitted refresh-scope-axis and related analog surfaces narrow, and kept stronger axis-materiality stories quarantined.',
        'discharge': 'reopen-only-if-refresh-scope-axis-independence-overflows',
        'gate_class': 'concrete-evidence',
        'origin_revision': REV,
        'prior_state': 'open gap: DelayBasin already had refresh-scope-axis truth but still lacked one compact successor surface for whether apparent corroborating axes were genuinely distinct or only renamed, mirrored, or nested restatements.',
        'question': 'whether one compact refresh-scope-axis-independence witness over the existing refresh-scope-axis and related admitted surfaces is enough for honest renamed-vs-nested-vs-independent comparison',
        'reopen_trigger': 'refresh-scope-axis-independence pressure overflows one compact successor surface',
        'reopen_triggers': ['later revisions need standing governance over substrate-backed independence, failure-domain weighting, or broader axis-materiality policy that one compact refresh-scope-axis-independence witness cannot honestly absorb'],
        'repair': 'ordinary-continuation',
        'resolved_objects': ['OQ-0148', 'AP-0147', 'FP-0152', 'TL-0158'],
        'revision': REV,
        'successor_surface': NEW_DOC,
        'target_surfaces': [NEW_DOC],
        'action_lane': 'keep-compact',
        'witness_surface': f'RESOLUTION-LEDGER.json#{NEW_RESOLUTION}'
    })

    append_item('RETROSPECTIVE-QUEUE.json', {
        'id': 'RT-0142',
        'title': 'revisit whether refresh-scope-axis-independence pressure stayed bounded after rev0253',
        'state': 'cooling',
        'candidate_surface': f'docs/90-quarantine/wild-speculations-2026-03-08.md#{NEW_QWS}',
        'cooldown_window': 'keep the stronger axis-materiality ladder, substrate notary, or corroboration weight scale story cooled until at least one later revision shows that one compact refresh-scope-axis-independence witness is no longer enough.',
        'adjudication_family': 'refresh scope axis independence / corroboration weighting / materiality pressure',
        'supersession_link': 'OBLIGATION-LEDGER.json#OB-0148',
        'origin_revision': REV,
        'discharge': 'keep-cooling-unless-refresh-scope-axis-independence-overflows',
        'action_lane': 'keep-compact',
        'gate_class': 'overflow',
        'witness_surface': 'RETROSPECTIVE-QUEUE.json#RT-0142',
        'revision': REV,
        'cooling_state': 'cooling',
        'disposition': 'await-adjudication',
        'repair': 'keep-cooling'
    })

    append_item('FIREBREAK-LEDGER.json', {
        'id': 'FB-0149',
        'title': 'the refresh-scope-axis-independence import should count as one compact renamed-vs-nested-vs-independent repair, not as promotion of an axis-materiality ladder',
        'state': 'withheld',
        'witness_surface': 'FIREBREAK-LEDGER.json#FB-0149',
        'judged_property': 'the rev0253 decision that DelayBasin should extract one compact refresh-scope-axis-independence witness over the existing refresh-scope-axis and related admitted surfaces and `refresh_scope_axis_independence_state` family while the broader axis-materiality ladder / substrate notary / corroboration weight scale story remains quarantined',
        'public_extract': [NEW_DOC, 'docs/10-method/refresh-scope-axis-witnesses-one-axis-dispersion-cross-axis-corroboration-and-axis-gated-generalization.md', 'docs/20-constitution/open-question-registry.md', 'FOREIGN-PRESSURE-LEDGER.json#FP-0152', 'APPLICABILITY-LEDGER.json#AP-0147', 'REVISION-RECEIPT.json'],
        'withheld_trace_surface': 'same-session drafting residue behind the compact refresh-scope-axis-independence-witness versus axis-materiality-ladder decision',
        'allowed_role': 'bounded drafting aid only; not public support for a broader axis-materiality ladder, substrate notary, or corroboration weight scale',
        'exposure_rule': 'expose or reintegrate only if later passes show that one compact refresh-scope-axis-independence witness cannot keep renamed-vs-nested-vs-independent truth bounded',
        'trace_state': 'withheld',
        'repair': 'ordinary-continuation',
        'origin_revision': REV,
        'action_lane': 'keep-compact',
        'gate_class': 'overflow',
        'firebreak_surface': 'FIREBREAK-LEDGER.json#FB-0149',
        'discharge': 'reopen-only-if-refresh-scope-axis-independence-overflows',
        'revision': REV,
        'blocked_object': 'axis-materiality ladder, substrate notary, or corroboration weight scale'
    })

    append_item('OBLIGATION-LEDGER.json', {
        'id': 'OB-0148',
        'title': 'when apparent corroborating axes keep needing renamed-vs-nested-vs-independent separation, DelayBasin should preserve one compact refresh-scope-axis-independence witness rather than an axis-materiality ladder',
        'state': 'open',
        'witness_surface': 'OBLIGATION-LEDGER.json#OB-0148',
        'target_surfaces': [f'docs/90-quarantine/wild-speculations-2026-03-08.md#{NEW_QWS}'],
        'missing_support': 'a later public check on whether one compact refresh-scope-axis-independence witness keeps sufficing and whether materially weak and materially strong independent axes need stronger governance',
        'current_support': ['APPLICABILITY-LEDGER.json#AP-0147', 'FOREIGN-PRESSURE-LEDGER.json#FP-0152', 'DATACUBE-TRANSFER-LEDGER.json#TL-0158'],
        'discharge_path': 'either show later that one compact refresh-scope-axis-independence witness keeps sufficing or promote broader axis-materiality governance explicitly',
        'obligation_state': 'open',
        'repair': 'ordinary-continuation',
        'origin_revision': REV,
        'discharge': 'reopen-only-if-refresh-scope-axis-independence-overflows',
        'action_lane': 'keep-compact',
        'gate_class': 'overflow',
        'revision': REV
    })

    append_item('ASSUMPTION-LEDGER.json', {
        'id': 'AS-0152',
        'title': 'one compact refresh-scope-axis-independence witness is enough for now',
        'state': 'active',
        'scope': 'continuity passes whose current widened public claim depends not only on whether dispersed widening looks corroborated across more than one axis, but on whether those apparent axes are genuinely independent rather than renamed, mirrored, or hierarchy-nested restatements',
        'invalidation_triggers': [
            'repeated later revisions need standing axis-materiality governance rather than one compact refresh-scope-axis-independence witness',
            'the archive needs an axis-materiality ladder or substrate notary just to keep renamed, nested, and genuinely independent axes distinct',
            'axis-independence cases repeatedly fail to stay distinguishable even with the witness in place'
        ],
        'assumption_state': 'active',
        'repair': 'ordinary-continuation',
        'origin_revision': REV,
        'revision': REV,
        'assumption': 'the current evidence only requires one compact refresh-scope-axis-independence witness over the existing refresh-scope-axis and related admitted surfaces rather than an axis-materiality ladder, substrate notary, or corroboration weight scale',
        'supporting_surfaces': ['APPLICABILITY-LEDGER.json#AP-0147', 'DATACUBE-TRANSFER-LEDGER.json#TL-0158', 'FOREIGN-PRESSURE-LEDGER.json#FP-0152'],
        'discharge': 'discharge when later revisions can keep renamed-vs-nested-vs-independent truth honest without a dedicated refresh-scope-axis-independence witness, or retire/quarantine it if broader axis-materiality governance becomes repeatedly necessary',
        'witness_surface': 'ASSUMPTION-LEDGER.json#AS-0152',
        'assumption_surface': 'ASSUMPTION-LEDGER.json#AS-0152',
        'assumption_statement': 'the current evidence only requires one compact refresh-scope-axis-independence witness over the existing refresh-scope-axis and related admitted surfaces rather than an axis-materiality ladder, substrate notary, or corroboration weight scale',
        'action_lane': 'keep-compact',
        'gate_class': 'concrete-evidence'
    })

    append_item('FOLLOWTHROUGH-QUEUE.json', {
        'id': 'FT-0155',
        'title': 'keep checking whether refresh-scope-axis-independence pressure still fits inside one compact successor surface',
        'state': 'queued',
        'blocked_object': 'axis-materiality ladder, substrate notary, or corroboration weight scale',
        'local_surface': f'docs/90-quarantine/wild-speculations-2026-03-08.md#{NEW_QWS}',
        'followthrough_state': 'queued',
        'boundary': 'do not promote bounded refresh-scope-axis-independence clarification into general axis-materiality-governance machinery',
        'next_proof_surface': NEW_DOC,
        'receiving_surface': 'FOLLOWTHROUGH-QUEUE.json#FT-0155',
        'repair': 'ordinary-continuation',
        'origin_revision': REV,
        'discharge': 'revisit-on-next-real-refresh-scope-axis-independence-overflow',
        'action_lane': 'keep-compact',
        'gate_class': 'overflow',
        'blocked_output': 'axis-materiality ladder, substrate notary, or corroboration weight scale',
        'owner_surface': 'OBLIGATION-LEDGER.json#OB-0148',
        'revision': REV,
        'missing_support': 'a later public check on whether one compact refresh-scope-axis-independence witness keeps overflowing the bounded rule and honestly warrants richer axis-materiality governance',
        'candidate_surface': f'docs/90-quarantine/wild-speculations-2026-03-08.md#{NEW_QWS}',
        'blocked_by': 'need repeated evidence that renamed-or-mirrored-axis-restatement vs nested-axis-restatement vs independent-axis-corroboration truth overflows one compact witness'
    })


def update_changelog_and_index() -> None:
    changelog_entry = dedent(f'''## {REV} - {STAMP} - axisindependence / substratequarantine / mirrorgate / {CODENAME}

- Added `docs/10-method/refresh-scope-axis-independence-witnesses-renamed-or-mirrored-axis-restatement-nested-axis-restatement-and-independent-axis-corroboration.md` to resolve `OQ-0148` with a compact renamed-vs-nested-vs-independent axis witness.
- Kept the stronger axis-materiality ladder / substrate notary / corroboration weight scale move explicitly quarantined as `{NEW_QWS}` instead of laundering it into canon.
- Refactored refresh-scope-axis contract helpers so both scope-axis families share one narrower validation path, and added `{NEW_CHECKER}`.

''')
    text = read('CHANGELOG.md')
    if not text.startswith(f'## {REV} - '):
        write('CHANGELOG.md', changelog_entry + text)

    row = f'| {BUNDLE} | 2026-03-28 | Refresh-scope-axis-independence revision: resolved OQ-0148 with a compact renamed-vs-nested-vs-independent witness, honestly quarantined stronger axis-materiality governance, and tightened shared scope-axis contract wiring to stay wired and cumulative. |'
    idx = read('ARCHIVE_INDEX.md')
    if row not in idx:
        lines = idx.splitlines()
        insert_at = 2 if len(lines) >= 2 else len(lines)
        lines.insert(insert_at, row)
        write('ARCHIVE_INDEX.md', '\n'.join(lines) + '\n')


def update_surface_status_and_manifest() -> None:
    status = json.loads(read('SURFACE-STATUS.json'))
    status['operational_head']['revision'] = REV
    status['status_lanes']['decision_state'] = 'admitted'
    status['status_lanes']['execution_state'] = 'packaged'
    status['status_lanes']['frozen_public_surface'] = BUNDLE
    status['status_lanes']['public_state'] = 'frozen-citable'
    status['status_lanes']['current_release_surface'] = BUNDLE
    status['citation_head'] = {'revision': REV, 'surface': BUNDLE}
    status['previous_citation_head'] = {'revision': PREV, 'surface': PREV_BUNDLE}
    status['state_class'] = 'released'
    status['revision'] = REV
    status['stamp'] = STAMP
    status['slug'] = SLUG
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
    r['summary'] = 'Resolved OQ-0148 with one compact refresh-scope-axis-independence witness that separates renamed or nested restatements from genuinely independent corroborating axes while keeping stronger axis-materiality governance quarantined.'
    r['move_classes'] = ['MV-0002', 'MV-0003', 'MV-0004', 'MV-0007', 'MV-0011']
    r['canon_additions'] = [NEW_DOC, 'RS-0155 resolved OQ-0148 with one compact refresh-scope-axis-independence witness']
    r['quarantine_additions'] = [f'{NEW_QWS} — {NEW_QWS_LABEL}']
    r['refs_used'] = [f'docs/00-meta/bibliography.md#ref-0957', f'docs/00-meta/bibliography.md#ref-0954', f'docs/00-meta/bibliography.md#ref-0958', f'docs/00-meta/bibliography.md#ref-0959', f'docs/00-meta/bibliography.md#ref-0960']
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
        'CHANGELOG.md', 'ARCHIVE_INDEX.md', 'tools/packet_contract_common.py', 'tools/check_refresh_scope_axis_witness_contract.py', NEW_CHECKER, 'apply_rev0253.py'
    ]
    r['touched_surfaces'] = touched
    r['packaged_release'] = True
    r['packaged_bundle_filename'] = BUNDLE
    r['basis_witness'].update({
        'expected_head': PREV,
        'observed_head': PREV,
        'basis_surfaces': ['docs/10-method/refresh-scope-axis-witnesses-one-axis-dispersion-cross-axis-corroboration-and-axis-gated-generalization.md', 'docs/00-meta/trajectory-map.md', 'docs/20-constitution/open-question-registry.md'],
        'session_provenance': PREV_BUNDLE,
        'basis_state': 'current',
        'basis_anchor_precision': 'underlier-plus-wrapper',
        'basis_omission_basis': 'broader axis-materiality drafting was intentionally omitted from canon because the evidence only justified one bounded refresh-scope-axis-independence witness',
        'repair': 'ordinary-continuation',
        'witness_surface': 'REVISION-RECEIPT.json',
        'basis_of_change': 'current prior packaged revision',
        'origin_revision': REV,
        'revision_span': f'{PREV} -> {REV}'
    })
    r['scope_witness'].update({
        'active_request': 'Continue researching online, GPUstorming, and evolving DelayBasin with tight, high-leverage revisions; make at least one bold but disciplined speculative move, do at least one hygiene/meta-engineering improvement, run make lint, package the archive, and provide a working link.',
        'exact_target': 'one compact refresh-scope-axis-independence witness plus one quarantined axis-materiality move and one small contract-helper refactor',
        'scope_surfaces': ['docs/20-constitution/open-question-registry.md', 'docs/00-meta/trajectory-map.md', NEW_DOC, 'docs/90-quarantine/wild-speculations-2026-03-08.md'],
        'ambient_exclusions': ['no broad axis-materiality canonization', 'no archive-wide governance layer', 'no uncited external pressure claims'],
        'scope_state': 'exact',
        'repair': 'ordinary-continuation',
        'scope_of_change': 'refresh-scope-axis-independence',
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
        'ambient_synonyms_excluded': ['renamed-view-counts-twice', 'same-tree-levels-mean-independent', 'second-label-proves-second-axis', 'axis-independence-ish'],
        'comparability_budget': 'refresh-scope-axis-independence truth is compared by token; the compact witness says whether apparent corroborating axes are renamed or mirrored restatements, hierarchy-nested refinements, genuinely independent corroboration, or honestly mixed while raw label sets, topology trees, and resource maps stay outside the token',
        'vocabulary_state': 'stable',
        'repair': 'ordinary-continuation',
        NEW_FAMILY: json.loads(read('WITNESS-VOCABULARY.json'))['families'][NEW_FAMILY]
    }
    r['counterfactual_shadow'] = {
        'status': 'rejected-nearby-move',
        'nearby_rejected_move': NEW_QWS_LABEL,
        'pivot_surface': f'docs/90-quarantine/wild-speculations-2026-03-08.md#{NEW_QWS}',
        'rejection_reason': 'current evidence supports a bounded independence witness but not a canon-level weighting or materiality ladder',
        'still_live': True
    }
    r['summary_highlight'] = SUMMARY_HIGHLIGHT
    r['codename'] = CODENAME
    r['created_at'] = CREATED_AT
    r['comparison_witness'] = {
        'previous_revision': PREV,
        'current_revision': REV,
        'current_pressure_id': 'FP-0152',
        'current_import_id': 'TL-0158',
        'basis_surface': 'docs/10-method/refresh-scope-axis-witnesses-one-axis-dispersion-cross-axis-corroboration-and-axis-gated-generalization.md',
        'delta_surface': NEW_DOC,
        'comparison_summary': 'rev0253 adds one compact refresh-scope-axis-independence witness so renamed, mirrored, or nested axes no longer stand in for genuinely independent corroboration.'
    }
    r['changes'] = [
        {'kind': 'canon', 'surface': NEW_DOC, 'summary': 'added one compact refresh-scope-axis-independence witness with renamed/mirrored, nested, independent, and mixed states'},
        {'kind': 'quarantine', 'surface': f'docs/90-quarantine/wild-speculations-2026-03-08.md#{NEW_QWS}', 'summary': 'kept stronger axis-materiality weighting quarantined rather than promoting it into canon'},
        {'kind': 'hygiene', 'surface': 'tools/packet_contract_common.py', 'summary': 'introduced a narrower shared refresh-scope-axis-family validator path and wired a new independence contract checker'}
    ]
    r['receipt_freshness_witness'] = {
        'packaged_bundle_filename': BUNDLE,
        'manifest_timestamp_token': STAMP,
        'receipt_timestamp_token': STAMP,
        'bundle_stem_suffix_relation': 'aligned',
        'current_import_id': 'TL-0158',
        'current_pressure_id': 'FP-0152',
        'change_anchor_surface': 'CHANGELOG.md',
        'freshness_state': 'fresh',
        'repair': 'ordinary-continuation'
    }
    r['question_posture_witness'] = {
        'resolution_surface': 'RESOLUTION-LEDGER.json',
        'registry_surface': 'docs/20-constitution/open-question-registry.md',
        'trajectory_surface': 'docs/00-meta/trajectory-map.md',
        'synced_resolved_questions': ['OQ-0148'],
        'frontier_selection_rule': 'select the last source-backed unresolved hot open question already projected into context-pack.json',
        'posture_state': 'synced',
        'repair': 'ordinary-continuation'
    }
    r['current_import_id'] = 'TL-0158'
    r['current_pressure_id'] = 'FP-0152'
    r['new_classes_or_families'] = [NEW_FAMILY]
    r['quarantined_non_take'] = ['axis-materiality ladder', 'substrate notary', 'corroboration weight scale']
    r['artifacts_touched'] = touched
    r['refresh_scope_axis_independence_witness'] = {
        'witness_surface': NEW_DOC,
        'family': NEW_FAMILY,
        'state_tokens': ['renamed-or-mirrored-axis-restatement', 'nested-axis-restatement', 'independent-axis-corroboration', 'mixed-refresh-scope-axis-independence'],
        'overflow_rule': 'reopen-only-if-refresh-scope-axis-independence-overflows'
    }
    r['refresh_scope_axis_independence_witness_contract'] = {'family': NEW_FAMILY, 'states': ['renamed-or-mirrored-axis-restatement', 'nested-axis-restatement', 'independent-axis-corroboration', 'mixed-refresh-scope-axis-independence']}
    r['refresh_scope_axis_independence_witness_meta'] = {'checker': NEW_CHECKER}
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
