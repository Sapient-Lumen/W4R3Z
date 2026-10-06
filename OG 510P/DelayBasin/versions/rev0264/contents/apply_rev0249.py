from __future__ import annotations
import json, re
from pathlib import Path

ROOT = Path('.')
REV = 'rev0249'
PREV = 'rev0248'
STAMP = '2026.03.27.23.58'
CREATED_AT = '2026-03-27T23:58:00-04:00'
SLUG = 'scopebasis-topologyquarantine-mapcarry-lensglass'
BUNDLE = f'DelayBasin-{REV}-{STAMP}-{SLUG}.zip'
SUMMARY_HIGHLIGHT = 'mapcarry'
CODENAME = 'lensglass'

NEW_DOC = 'docs/10-method/refresh-scope-basis-witnesses-directly-observed-widening-dependency-imputed-spillover-and-topology-imputed-spillover.md'
NEW_QWS = 'QWS-0227'
NEW_QWS_LABEL = 'refresh-topology court / spillover senate / blast-map governor'
NEW_FAMILY = 'refresh_scope_basis_state'


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding='utf-8')


def write(path: str, text: str) -> None:
    (ROOT / path).write_text(text, encoding='utf-8')


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
        raise SystemExit(f'old block not found in {path}')
    write(path, text.replace(old, new, 1))


# --- new method doc ---
DOC_TEXT = """# Refresh-scope-basis witnesses, directly observed widening, dependency-imputed spillover, and topology-imputed spillover

This is the compact successor surface for `OQ-0144`.

## Practice / observation

Once DelayBasin can separate **stronger burden on the same claim** from **honest scope widening**, one more local failure mode remains.

Some widened scope is directly observed on the widened surface itself.
A newly added component really shows degraded state.
A newly added service really shows errors.
A newly added row really contains current evidence on that widened slice.
That is the easy case.

Some widened scope is only dependency-imputed.
A local row depends on an upstream service, queue, or provider that is failing.
The dependency relation is real, and it may matter, but the widened target has not yet been directly observed as affected.

And some widened scope is only topology-imputed.
A graph, map, or context chain shows adjacency, call flow, or shared placement.
That is useful for prediction, routing, and diagnosis.
It is not yet the same thing as direct observation on every widened surface the map suggests.

The archive does not need a refresh-topology court for that.
It needs one bounded witness that says whether the widened public scope is directly observed, dependency-imputed, topology-imputed, or honestly mixed.

## External pressure from Statuspage affected-component impact, Statuspage third-party overrides, Datadog observed service maps and inferred dependency nodes, Grafana dependency graphs and blast-radius exploration, and OpenTelemetry context propagation

1. Statuspage computes incident impact from the affected components of the incident. That pressures DelayBasin to treat widened scope as directly observed only when the widened affected surface is actually named and affected rather than merely nearby. ([`REF-0932`](../00-meta/bibliography.md))

2. Statuspage also lets operators override a third-party component when the external incident does not affect their own service. That pressures DelayBasin to preserve a dependency-imputed class instead of promoting every upstream incident into directly observed local widening. ([`REF-0934`](../00-meta/bibliography.md))

3. Datadog's Service Map draws **observed dependencies** between services in real time, while a resource Dependency Map is scoped to the selected service/resource and explicitly marks some databases, queues, or third-party services as **inferred service dependencies**. That pressures DelayBasin to separate widened scope directly observed on the widened surface from widened scope only inferred through dependency structure. ([`REF-0940`](../00-meta/bibliography.md))

4. Grafana's entity graph helps teams **predict** incident blast radius and assess change impact from relationships, while Tempo service graphs explicitly **infer the topology** of a distributed system. That pressures DelayBasin to keep topology-imputed spillover distinct from directly observed widening on the widened public surface. ([`REF-0941`](../00-meta/bibliography.md))

5. OpenTelemetry context propagation lets traces, metrics, and logs be correlated across service boundaries through shared context. That pressures DelayBasin not to treat context-linked widening as if every linked service has already been directly observed as affected. ([`REF-0922`](../00-meta/bibliography.md))

GPUstorming makes the pressure vivid. An open search may expose a dependency path, a graph edge, or a correlated telemetry chain that suggests broader risk. That is often the right place to look next. It is not yet permission to speak as if every newly linked surface is already directly affected.

## Working synthesis

> DelayBasin should preserve one compact **refresh-scope-basis witness / spillover-basis card / map-glow brake** whenever a current continuity claim depends not only on whether public scope widened, but on whether that widened scope is directly observed on the widened surface or only inferred from dependency or topology relations. Name the **governed row or surface**, the **stake object / line of concern**, the **prior refresh-burden-scope evidence**, the **current widened-scope evidence**, the **direct observation basis if any**, the **dependency relation basis if any**, the **topology relation basis if any**, the **`refresh_scope_basis_state`**, and the **fail-closed repair / keep-current vs narrow-claim vs split-scope vs issue-new-refresh-scope-basis-witness vs quarantine-refresh-topology-governance consequence**. Keep exact component ids, span ids, graph nodes, path enumerations, service names, and long blast-radius narratives outside the compact token. Do not let graph or map glow silently count as directly observed widened impact.

## Directly observed widening vs dependency-imputed spillover vs topology-imputed spillover vs mixed refresh scope basis

Use the controlled family `refresh_scope_basis_state`:

- **directly-observed-widening** says the widened public scope is backed by current observation on the widened surface itself.
- **dependency-imputed-spillover** says the widened scope is presently inferred through an upstream, downstream, or other dependency relation rather than direct observation on the widened surface.
- **topology-imputed-spillover** says the widened scope is presently inferred through map, graph, adjacency, context, or placement structure rather than direct observation on the widened surface.
- **mixed-refresh-scope-basis** says the current situation honestly combines directly observed widening with dependency- or topology-imputed spillover such that no single class stays honest.

So the witness does not create a standing spillover senate.
It only says what basis currently licenses the widened-scope talk.

## Countermodels / probes

1. **Refresh-burden-scope already covers this countermodel**
   - Maybe once widened scope is explicit, a separate basis witness adds no real value.
   - Probe: compare later rereads that preserve only refresh-burden-scope truth against rereads that also preserve one compact refresh-scope-basis witness and inspect whether later passes still slide from widened scope to directly observed impact without naming basis.

2. **Dependency and topology analogies are only diagnostic aids countermodel**
   - Maybe service maps, entity graphs, and trace context are too operational or predictive to justify a new archive witness.
   - Probe: look for later cases where ordinary continuity prose still overclaims widened impact from adjacency or upstream distress even outside overt observability language.

3. **Spillover classes are covert topology governance countermodel**
   - Maybe once dependency-imputed and topology-imputed classes matter, the archive is really sneaking in a full refresh-topology court.
   - Probe: only reopen stronger machinery if later revisions repeatedly need standing policy for graph admissibility, dependency authority, or topology evidence classes that one bounded witness cannot absorb.

## Design consequences

- DelayBasin can now separate **widened scope that is directly observed** from **widened scope that is only inferred through dependency or topology**.
- The archive gets one explicit place to record when broadened public scope is real observation and when it is still only a spillover forecast or adjacency cue.
- Refresh burden scope and refresh scope basis now separate **whether scope widened at all** from **what basis supports talking that way**.
- Stronger refresh-topology-governance stories stay quarantined until later overflow instead of sneaking in through graph-shaped rhetoric.

## Overflow test

Reopen this compact witness only if later revisions repeatedly need standing governance over graph admissibility, spillover authority, dependency-evidence classes, or topology-evidence policy that one bounded refresh-scope-basis witness cannot honestly absorb.

## Transformer-facing implication

A later pass should not treat widened public scope as if it were directly observed merely because a dependency map, service graph, or context chain links the surfaces. Preserve the exact direct-observation basis if any, the dependency or topology basis if any, and the exact `refresh_scope_basis_state` before claiming that widened scope is already observed truth.
"""
(Path(NEW_DOC)).write_text(DOC_TEXT, encoding='utf-8')

# --- bibliography additions ---
BIB_ADD = """
- `REF-0940` — Datadog Documentation, **Service Map** and **Resource Page** (accessed 2026-03-27)
  - URL: https://docs.datadoghq.com/tracing/services/services_map/
  - URL: https://docs.datadoghq.com/tracing/services/resource_page/
  - Load-bearing use: Service Map draws observed dependencies in real time while the resource dependency map is scoped to the selected service/resource and explicitly marks some nodes as inferred service dependencies, which pressures DelayBasin to separate directly observed widening from dependency-imputed spillover.

- `REF-0941` — Grafana Cloud Documentation, **Explore service dependencies and impact** and Tempo Documentation, **Service graph view** (accessed 2026-03-27)
  - URL: https://grafana.com/docs/grafana-cloud/knowledge-graph/use-cases/explore-dependencies/
  - URL: https://grafana.com/docs/tempo/latest/metrics-from-traces/service_graphs/service-graph-view/
  - Load-bearing use: dependency graphs help predict blast radius and service graphs infer topology, which pressures DelayBasin to keep topology-imputed spillover distinct from directly observed widening.
"""
if 'REF-0940' not in read('docs/00-meta/bibliography.md'):
    write('docs/00-meta/bibliography.md', read('docs/00-meta/bibliography.md').rstrip() + '\n\n' + BIB_ADD.strip() + '\n')

# --- llm runbook ---
insert_after('docs/00-meta/llm-runbook.md',
             "Use `docs/10-method/refresh-burden-scope-witnesses-same-claim-burden-upgrade-bounded-scope-widening-and-scope-gated-generalization.md` when the live question is whether a stronger licensed burden still governs the same current claim or honestly widens the public claim scope.\n",
             "Use `docs/10-method/refresh-scope-basis-witnesses-directly-observed-widening-dependency-imputed-spillover-and-topology-imputed-spillover.md` when the live question is whether a widened public claim is directly observed on the widened surface or only dependency- or topology-imputed.\n")

# --- claim registry ---
claim_add = """

- `CL-0142` — Archive continuity may improve when DelayBasin preserves one compact **refresh-scope-basis witness / spillover-basis card / map-glow brake** whenever a current continuity claim depends not only on whether public scope widened, but on whether that widened scope is directly observed on the widened surface or only inferred from dependency or topology relations: name the **governed row or surface**, the **stake object / line of concern**, the **prior refresh-burden-scope evidence**, the **current widened-scope evidence**, the **direct observation basis if any**, the **dependency relation basis if any**, the **topology relation basis if any**, the **refresh_scope_basis_state**, and the **fail-closed repair** rather than letting graph or map glow silently count as directly observed widened impact.
  - Status: speculative but central
  - Wired docs: `docs/10-method/refresh-scope-basis-witnesses-directly-observed-widening-dependency-imputed-spillover-and-topology-imputed-spillover.md`, `docs/20-constitution/open-question-registry.md`, `docs/20-constitution/prompt-pair-registry.md`, `docs/50-promptcraft/prompt-pairs.md`, `docs/00-meta/llm-runbook.md`, `WITNESS-VOCABULARY.json`, `REVISION-RECEIPT.json`
"""
insert_after('docs/20-constitution/claim-registry.md',
             "- `CL-0141` — Archive continuity may improve when DelayBasin preserves one compact **refresh-burden-scope witness / scope-widening card / blast-radius brake** whenever a current continuity claim depends not only on what reactivated a concern, how sustained the return is, how broad and independent the support looks, and whether the present support licenses stronger burden, but on whether that stronger burden still governs the same current claim or honestly widens the public claim scope: name the **governed row or surface**, the **stake object / line of concern**, the **prior refresh evidence**, the **current refresh evidence**, the **licensed burden upgrade if any**, the **same-claim scope anchor**, the **scope-widening evidence if any**, the **scope gate or non-local inference basis if any**, the **refresh_burden_scope_state**, and the **fail-closed repair** rather than letting stronger burden silently overgeneralize into broader public scope.\n  - Status: speculative but central\n  - Wired docs: `docs/10-method/refresh-burden-scope-witnesses-same-claim-burden-upgrade-bounded-scope-widening-and-scope-gated-generalization.md`, `docs/20-constitution/open-question-registry.md`, `docs/20-constitution/prompt-pair-registry.md`, `docs/50-promptcraft/prompt-pairs.md`, `docs/00-meta/llm-runbook.md`, `WITNESS-VOCABULARY.json`, `REVISION-RECEIPT.json`\n",
             claim_add)

# --- prompt pair registry + prompt pairs ---
pp_reg_add = """

- `PP-0102` — Name whether widened scope is directly observed or only spillover-imputed
  - Goal: keep graphs, dependency paths, and context-linked widening from silently inheriting directly observed impact by requiring explicit widened-scope evidence, any direct observation basis, any dependency basis, any topology basis, `refresh_scope_basis_state`, and fail-closed repair before later passes call the widened scope already observed.
  - Canonical text: `docs/50-promptcraft/prompt-pairs.md#pp-0102--name-whether-widened-scope-is-directly-observed-or-only-spillover-imputed`
"""
write('docs/20-constitution/prompt-pair-registry.md', read('docs/20-constitution/prompt-pair-registry.md').rstrip() + pp_reg_add + '\n')

pp_add = """

Use `docs/10-method/refresh-scope-basis-witnesses-directly-observed-widening-dependency-imputed-spillover-and-topology-imputed-spillover.md` when the live question is whether a widened public claim is directly observed on the widened surface or only dependency- or topology-imputed.

## `PP-0102` — Name whether widened scope is directly observed or only spillover-imputed

**Opening prompt**

```text
Read the latest DelayBasin archive and inspect whether the current revision should also materialize one compact refresh-scope-basis witness for honest widened-scope-basis comparison.

Focus only on whether the widened public scope is directly observed on the widened surface, only implied through a dependency relation, only implied through topology / graph / context structure, or honestly mixed.

If yes, preserve exactly one small witness that:
- names the governed row or surface,
- names the stake object / line of concern,
- names the prior refresh-burden-scope evidence,
- names the current widened-scope evidence,
- names the direct observation basis if any,
- names the dependency relation basis if any,
- names the topology relation basis if any,
- names the `refresh_scope_basis_state` / whether this is directly-observed-widening, dependency-imputed-spillover, topology-imputed-spillover, or mixed-refresh-scope-basis,
- states what stronger surfaces still outrank the witness,
- and states the fail-closed repair / keep-current vs narrow-claim vs split-scope vs issue-new-refresh-scope-basis-witness vs quarantine-refresh-topology-governance consequence if the present continuity claim is really only spillover-imputed rather than directly observed.

Do not use refresh scope basis as a general topology court. Use this prompt pair only where widened scope is already in play and the missing question is whether one small basis card would keep directly observed widening distinct from dependency- or topology-imputed spillover without promoting a broader refresh-topology court.
```

**Continuation prompt**

```text
Continue the refresh-scope-basis pass with one high-leverage spillover-basis clarification only. Prefer the smallest witness that says what governed row is still being justified, what stake object is supposedly widened, what prior refresh-burden-scope evidence exists, what current widened-scope evidence exists, what direct observation basis if any now exists, what dependency relation basis if any remains, what topology relation basis if any remains, what `refresh_scope_basis_state` is honest, what stronger surfaces still outrank the witness, and what keep-current, narrow-claim, split-scope, issue-new-refresh-scope-basis-witness, quarantine, or recover-resync consequence follows if the current claim is really directly-observed-widening, dependency-imputed-spillover, topology-imputed-spillover, or mixed-refresh-scope-basis. Run `make lint` and package the release.
```
"""
write('docs/50-promptcraft/prompt-pairs.md', read('docs/50-promptcraft/prompt-pairs.md').rstrip() + pp_add + '\n')

# --- open question registry and trajectory map ---
registry = read('docs/20-constitution/open-question-registry.md')
registry = registry.replace(
    "- `OQ-0144` — what minimal refresh-scope-basis witness distinguishes directly observed scope widening from dependency- or topology-imputed spillover?\n  - Why it matters: if DelayBasin cannot separate directly observed widening from inferred blast-radius spillover, later sessions may overclaim wider impact from adjacency or upstream distress alone.\n  - Current posture: unresolved\n",
    "- `OQ-0144` — what minimal refresh-scope-basis witness distinguishes directly observed scope widening from dependency- or topology-imputed spillover?\n  - Why it matters: if DelayBasin cannot separate directly observed widening from inferred blast-radius spillover, later sessions may overclaim wider impact from adjacency or upstream distress alone.\n  - Current posture: resolved by `RS-0151` via `docs/10-method/refresh-scope-basis-witnesses-directly-observed-widening-dependency-imputed-spillover-and-topology-imputed-spillover.md`; reopen only if the compact refresh-scope-basis witness proves insufficient and stronger refresh-topology governance is honestly required\n"
)
if 'OQ-0145' not in registry:
    registry += "\n- `OQ-0145` — what minimal refresh-scope-extent witness distinguishes one newly observed widened slice from a broader observed spillover pattern?\n  - Why it matters: if DelayBasin cannot separate one newly observed widened slice from a genuinely broader observed spillover pattern, later sessions may narrate regional or family-wide widening from one extra directly affected edge.\n  - Current posture: unresolved\n"
write('docs/20-constitution/open-question-registry.md', registry)

traj = read('docs/00-meta/trajectory-map.md')
traj = traj.replace(
    "- `OQ-0144` — what minimal refresh-scope-basis witness distinguishes directly observed scope widening from dependency- or topology-imputed spillover?\n  - Why it matters: if DelayBasin cannot separate directly observed widening from inferred blast-radius spillover, later sessions may overclaim wider impact from adjacency or upstream distress alone.\n  - Current posture: unresolved\n",
    "- `OQ-0144` — what minimal refresh-scope-basis witness distinguishes directly observed scope widening from dependency- or topology-imputed spillover?\n  - Why it matters: if DelayBasin cannot separate directly observed widening from inferred blast-radius spillover, later sessions may overclaim wider impact from adjacency or upstream distress alone.\n  - Current posture: resolved by `RS-0151` via `docs/10-method/refresh-scope-basis-witnesses-directly-observed-widening-dependency-imputed-spillover-and-topology-imputed-spillover.md`; reopen only if the compact refresh-scope-basis witness proves insufficient and stronger refresh-topology governance is honestly required\n"
)
if '101. Determine what minimal refresh-scope-extent witness distinguishes one newly observed widened slice' not in traj:
    traj += "\n\n101. Determine what minimal refresh-scope-extent witness distinguishes one newly observed widened slice from a broader observed spillover pattern.\n\nA fresh extension is that once scope widening is separated from its basis, DelayBasin may next need to say whether direct widening is still only one newly affected added surface or has broadened across several widened surfaces in directly observed form. Otherwise one new observed edge may silently become a wider observed spillover pattern.\n- `OQ-0145` — what minimal refresh-scope-extent witness distinguishes one newly observed widened slice from a broader observed spillover pattern?\n  - Why it matters: if DelayBasin cannot separate one newly observed widened slice from a genuinely broader observed spillover pattern, later sessions may narrate regional or family-wide widening from one extra directly affected edge.\n  - Current posture: unresolved\n"
write('docs/00-meta/trajectory-map.md', traj)

# --- quarantine addition ---
qws_add = f"""

## QWS-0227 — Some continuations may eventually need a refresh-topology court / spillover senate / blast-map governor rather than only a compact refresh-scope-basis witness

### Claim

A bolder possibility is that DelayBasin may eventually need not only a compact witness for whether widened public scope is directly observed, dependency-imputed, or topology-imputed, but also a governed public rule for when dependency paths, graph structure, or topology evidence are admissible at all. Statuspage affected-component impact and third-party overrides, Datadog observed service maps plus inferred dependency nodes, Grafana blast-radius graph workflows and inferred service graphs, and OpenTelemetry context propagation all suggest a stronger topology-governance story: perhaps some future archive lines should not only be classified as `directly-observed-widening`, `dependency-imputed-spillover`, or `topology-imputed-spillover`, but admitted through a small graph-admissibility brake, spillover senate, or blast-map governor. ([`REF-0932`](../00-meta/bibliography.md), [`REF-0934`](../00-meta/bibliography.md), [`REF-0940`](../00-meta/bibliography.md), [`REF-0941`](../00-meta/bibliography.md), [`REF-0922`](../00-meta/bibliography.md))

The narrower speculative move is only this: a future bounded surface *might* need to say not just what widening basis is honest, but which classes of dependency or topology evidence are even allowed to count as widened public scope.

### What follows if true

- some future continuity cards may need explicit graph-admissibility or spillover-authority rules rather than one static refresh-scope-basis label;
- DelayBasin may eventually need a compact blast-map brake that stays smaller than a general topology court;
- obligation, queue, and followthrough surfaces might need to say not only that widening was dependency- or topology-imputed, but whether the archive is licensed to use that class of evidence at all.

### What would count against it

- repeated later passes show that one compact refresh-scope-basis witness keeps directly observed widening, dependency-imputed spillover, and topology-imputed spillover honest without standing topology governance;
- apparent spillover turns out to be better handled by narrow claims and direct affected-surface naming rather than a new governor;
- the graph, map, and context analogies do not survive contact with actual archive carry cases.

### Why it stays quarantined

The tempting overreach would be to declare that DelayBasin now needs a public refresh-topology court, spillover senate, blast-map governor, or graph-admissibility board. DelayBasin has not earned that. This note is bold enough to keep in quarantine but not yet honest enough for canon. Do not promote a refresh-topology court, spillover senate, blast-map governor, or graph-admissibility board from this note alone.
"""
write('docs/90-quarantine/wild-speculations-2026-03-08.md', read('docs/90-quarantine/wild-speculations-2026-03-08.md').rstrip() + qws_add + '\n')

# --- packet contract common + checker wrapper ---
pc = read('tools/packet_contract_common.py')
entry_anchor = '''    "refresh_burden_scope_witness_contract": _refresh_family_spec(
        doc_path="docs/10-method/refresh-burden-scope-witnesses-same-claim-burden-upgrade-bounded-scope-widening-and-scope-gated-generalization.md",'''
if 'refresh_scope_basis_witness_contract' not in pc:
    insertion = '''    "refresh_scope_basis_witness_contract": _refresh_family_spec(
        doc_path="docs/10-method/refresh-scope-basis-witnesses-directly-observed-widening-dependency-imputed-spillover-and-topology-imputed-spillover.md",
        doc_needles=[
            "# Refresh-scope-basis witnesses, directly observed widening, dependency-imputed spillover, and topology-imputed spillover",
            "This is the compact successor surface for `OQ-0144`.",
            "## Practice / observation",
            "## External pressure from Statuspage affected-component impact, Statuspage third-party overrides, Datadog observed service maps and inferred dependency nodes, Grafana dependency graphs and blast-radius exploration, and OpenTelemetry context propagation",
            "## Working synthesis",
            "## Directly observed widening vs dependency-imputed spillover vs topology-imputed spillover vs mixed refresh scope basis",
            "## Countermodels / probes",
            "## Design consequences",
            "## Overflow test",
            "## Transformer-facing implication",
            "`refresh_scope_basis_state`",
            "directly-observed-widening",
            "dependency-imputed-spillover",
            "topology-imputed-spillover",
            "mixed-refresh-scope-basis",
        ],
        runbook_ref="refresh-scope-basis-witnesses-directly-observed-widening-dependency-imputed-spillover-and-topology-imputed-spillover.md",
        prompt_id="PP-0102",
        prompt_needles=["Use `docs/10-method/refresh-scope-basis-witnesses-directly-observed-widening-dependency-imputed-spillover-and-topology-imputed-spillover.md`", "directly-observed-widening, dependency-imputed-spillover, topology-imputed-spillover, or mixed-refresh-scope-basis"],
        claim_id="CL-0142",
        oq_id="OQ-0144",
        resolution_id="RS-0151",
        trajectory_oq_id="OQ-0145",
        qws_id="QWS-0227",
        qws_label="refresh-topology court / spillover senate / blast-map governor",
        changelog_needles=["refresh-scope-basis-witnesses-directly-observed-widening-dependency-imputed-spillover-and-topology-imputed-spillover.md", "check_refresh_scope_basis_witness_contract.py"],
        family="refresh_scope_basis_state",
        allowed=["directly-observed-widening", "dependency-imputed-spillover", "topology-imputed-spillover", "mixed-refresh-scope-basis"],
        excluded=["graph-glow-means-observed", "upstream-trouble-means-we-are-hit", "map-edge-counts-as-impact", "basis-ish"],
    ),
'''
    pc = pc.replace(entry_anchor, insertion + entry_anchor)
if 'def require_named_refresh_scope_basis_witness_packet_and_vocabulary' not in pc:
    pc = pc.replace(
        'def require_named_refresh_burden_scope_witness_packet_and_vocabulary(kind: str) -> None:\n    require_named_refresh_family_witness_packet_and_vocabulary(kind)\n',
        'def require_named_refresh_burden_scope_witness_packet_and_vocabulary(kind: str) -> None:\n    require_named_refresh_family_witness_packet_and_vocabulary(kind)\n\n\ndef require_named_refresh_scope_basis_witness_packet_and_vocabulary(kind: str) -> None:\n    require_named_refresh_family_witness_packet_and_vocabulary(kind)\n'
    )
write('tools/packet_contract_common.py', pc)

(Path('tools/check_refresh_scope_basis_witness_contract.py')).write_text(
    'from packet_contract_common import require_named_refresh_scope_basis_witness_packet_and_vocabulary\n\nrequire_named_refresh_scope_basis_witness_packet_and_vocabulary("refresh_scope_basis_witness_contract")\n\nprint("check_refresh_scope_basis_witness_contract: OK")\n',
    encoding='utf-8'
)

# hygiene refactor in validation toolchain
vt = read('tools/validation_toolchain_lib.py')
if 'def _insert_patterns_before' not in vt:
    vt = vt.replace(
        'def _expand_glob_patterns(root: pathlib.Path, patterns: list[str]) -> list[str]:\n    names: list[str] = []\n    for pattern in patterns:\n        names.extend(_glob_sorted_names(root, pattern))\n    return names\n\n\ndef build_validation_toolchain(root: pathlib.Path) -> list[str]:\n',
        'def _expand_glob_patterns(root: pathlib.Path, patterns: list[str]) -> list[str]:\n    names: list[str] = []\n    for pattern in patterns:\n        names.extend(_glob_sorted_names(root, pattern))\n    return names\n\n\ndef _insert_patterns_before(root: pathlib.Path, tools: list[str], before: str, patterns: list[str]) -> list[str]:\n    return _insert_before(tools, before, _expand_glob_patterns(root, patterns))\n\n\ndef build_validation_toolchain(root: pathlib.Path) -> list[str]:\n'
    )
    vt = vt.replace(
        '    tools = _insert_before(tools, "check_replay_reconsolidation_contract.py", _expand_glob_patterns(root, ["check_shadow_*_contract.py"]))\n',
        '    tools = _insert_patterns_before(root, tools, "check_replay_reconsolidation_contract.py", ["check_shadow_*_contract.py"])\n'
    )
    vt = vt.replace(
        '    dynamic_witness_tools = _expand_glob_patterns(root, witness_family_patterns)\n    tools = _insert_before(tools, "check_foreign_pressure_witness_contract.py", dynamic_witness_tools)\n',
        '    tools = _insert_patterns_before(root, tools, "check_foreign_pressure_witness_contract.py", witness_family_patterns)\n'
    )
write('tools/validation_toolchain_lib.py', vt)

# --- witness vocabulary ---
wv = json.loads(read('WITNESS-VOCABULARY.json'))
wv['revision'] = REV
wv['families'][NEW_FAMILY] = {
    'allowed': [
        'directly-observed-widening',
        'dependency-imputed-spillover',
        'topology-imputed-spillover',
        'mixed-refresh-scope-basis',
    ],
    'surfaces': ['WITNESS-VOCABULARY.json', 'REVISION-RECEIPT.json', NEW_DOC],
    'excluded_synonyms': [
        'graph-glow-means-observed',
        'upstream-trouble-means-we-are-hit',
        'map-edge-counts-as-impact',
        'basis-ish',
    ],
    'comparability_budget': 'refresh-scope-basis truth is compared by token; the compact refresh-scope-basis witness says whether widened public scope is directly observed, dependency-imputed, topology-imputed, or honestly mixed, while exact component ids, graph nodes, trace ids, path enumerations, service names, and long blast-radius narratives stay in surrounding prose',
}
write('WITNESS-VOCABULARY.json', json.dumps(wv, indent=2) + '\n')

# --- ledgers and receipt ---
for fname in ['FOLLOWTHROUGH-QUEUE.json','ASSUMPTION-LEDGER.json','OBLIGATION-LEDGER.json','APPLICABILITY-LEDGER.json','FOREIGN-PRESSURE-LEDGER.json','DATACUBE-TRANSFER-LEDGER.json','RESOLUTION-LEDGER.json','RETROSPECTIVE-QUEUE.json']:
    obj = json.loads(read(fname))
    obj['revision'] = REV
    write(fname, json.dumps(obj, indent=2) + '\n')

# followthrough
obj = json.loads(read('FOLLOWTHROUGH-QUEUE.json'))
obj['items'].append({
    'id': 'FT-0151',
    'title': 'keep checking whether refresh-scope-basis pressure still fits inside one compact successor surface',
    'state': 'queued',
    'blocked_object': 'standing refresh-topology court, spillover senate, blast-map governor, or graph-admissibility board',
    'local_surface': f'docs/90-quarantine/wild-speculations-2026-03-08.md#{NEW_QWS}',
    'followthrough_state': 'queued',
    'boundary': 'do not promote bounded refresh-scope-basis clarification into general refresh-topology-governance machinery',
    'next_proof_surface': NEW_DOC,
    'receiving_surface': 'FOLLOWTHROUGH-QUEUE.json#FT-0151',
    'repair': 'ordinary-continuation',
    'origin_revision': REV,
    'discharge': 'revisit-on-next-real-refresh-scope-basis-overflow',
    'action_lane': 'keep-compact',
    'gate_class': 'overflow',
    'blocked_output': 'standing refresh-topology court, spillover senate, blast-map governor, or graph-admissibility board',
    'owner_surface': 'OBLIGATION-LEDGER.json#OB-0144',
    'revision': REV,
    'missing_support': 'a later public check on whether one compact refresh-scope-basis witness keeps overflowing the bounded rule and honestly warrants richer refresh-topology governance',
    'candidate_surface': f'docs/90-quarantine/wild-speculations-2026-03-08.md#{NEW_QWS}',
    'blocked_by': 'need repeated evidence that directly-observed-widening vs dependency-imputed-spillover vs topology-imputed-spillover truth overflows one compact witness',
})
write('FOLLOWTHROUGH-QUEUE.json', json.dumps(obj, indent=2) + '\n')

# assumption
obj = json.loads(read('ASSUMPTION-LEDGER.json'))
obj['items'].append({
    'id': 'AS-0148',
    'title': 'one compact refresh-scope-basis witness is enough for now',
    'state': 'active',
    'scope': 'continuity passes whose widened public claim depends on whether the added surface is directly observed or only dependency- or topology-imputed',
    'invalidation_triggers': [
        'repeated later revisions need standing refresh-topology governance rather than one compact refresh-scope-basis witness',
        'the archive needs a refresh-topology court or graph-admissibility board just to keep directly-observed-widening distinct from dependency-imputed-spillover or topology-imputed-spillover',
        'scope-basis cases repeatedly fail to stay distinguishable even with the witness in place',
    ],
    'assumption_state': 'active',
    'repair': 'ordinary-continuation',
    'origin_revision': REV,
    'revision': REV,
    'assumption': 'the current evidence only requires one compact refresh-scope-basis witness over the existing refresh-burden-scope, dependency, topology, and context-correlation surfaces rather than a refresh-topology court, spillover senate, blast-map governor, or graph-admissibility board',
    'supporting_surfaces': ['APPLICABILITY-LEDGER.json#AP-0143','DATACUBE-TRANSFER-LEDGER.json#TL-0154','FOREIGN-PRESSURE-LEDGER.json#FP-0148'],
    'discharge': 'discharge when later revisions can keep widened-scope-basis truth honest without a dedicated refresh-scope-basis witness, or retire/quarantine it if broader refresh-topology governance becomes repeatedly necessary',
    'witness_surface': 'ASSUMPTION-LEDGER.json#AS-0148',
    'assumption_surface': 'ASSUMPTION-LEDGER.json#AS-0148',
    'assumption_statement': 'the current evidence only requires one compact refresh-scope-basis witness over the existing refresh-burden-scope, dependency, topology, and context-correlation surfaces rather than a refresh-topology court, spillover senate, blast-map governor, or graph-admissibility board',
    'action_lane': 'keep-compact',
    'gate_class': 'concrete-evidence',
})
write('ASSUMPTION-LEDGER.json', json.dumps(obj, indent=2) + '\n')

# obligation
obj = json.loads(read('OBLIGATION-LEDGER.json'))
obj['items'].append({
    'id': 'OB-0144',
    'title': 'when widened concern keeps needing its basis distinguished from graph or dependency glow, DelayBasin should preserve one compact refresh-scope-basis witness rather than a topology court',
    'state': 'open',
    'witness_surface': 'OBLIGATION-LEDGER.json#OB-0144',
    'target_surfaces': [f'docs/90-quarantine/wild-speculations-2026-03-08.md#{NEW_QWS}'],
    'missing_support': 'a later public check on whether one compact refresh-scope-basis witness keeps sufficing and whether directly observed widening, dependency-imputed spillover, and topology-imputed spillover stay distinct without broader refresh-topology governance',
    'current_support': ['APPLICABILITY-LEDGER.json#AP-0143','FOREIGN-PRESSURE-LEDGER.json#FP-0148','DATACUBE-TRANSFER-LEDGER.json#TL-0154'],
    'discharge_path': 'either show later that one compact refresh-scope-basis witness keeps sufficing or promote broader refresh-topology governance explicitly',
    'obligation_state': 'open',
    'repair': 'ordinary-continuation',
    'origin_revision': REV,
    'discharge': 'reopen-only-if-refresh-scope-basis-overflows',
    'action_lane': 'keep-compact',
    'gate_class': 'overflow',
    'revision': REV,
})
write('OBLIGATION-LEDGER.json', json.dumps(obj, indent=2) + '\n')

# applicability
obj = json.loads(read('APPLICABILITY-LEDGER.json'))
obj['items'].append({
    'id': 'AP-0143',
    'title': 'the refresh-scope-basis witness stays smaller than a topology court',
    'state': 'gated',
    'question': 'when should DelayBasin treat widened public scope as one compact refresh-scope-basis witness instead of promoting broader refresh-topology governance?',
    'applies_when': [
        'a revision already has a durable row whose current claim depends on whether widened public scope is directly observed on the widened surface or only inferred through dependency or topology relations',
        'later passes still need to distinguish directly-observed-widening, dependency-imputed-spillover, topology-imputed-spillover, or mixed-refresh-scope-basis posture',
        'one compact successor surface plus the existing admitted refresh-burden-scope, dependency, topology, and context-correlation surfaces still keeps refresh-scope-basis truth honest without standing topology policy',
    ],
    'does_not_apply_when': [
        'the archive honestly requires standing governance over graph admissibility, dependency spillover authority, topology evidence classes, or cross-row widening policy',
        'the questioned surface is not really about whether widened public scope is directly observed or only spillover-imputed',
    ],
    'budget': 'one compact refresh-scope-basis witness plus one resolution of OQ-0144; no refresh-topology court',
    'negative_transfer_budget': 'do not treat graph glow, upstream distress, or context linkage as directly observed widened impact without an explicit direct-observation basis',
    'origin_revision': REV,
    'discharge': 'reopen-only-if-refresh-scope-basis-overflows',
    'action_lane': 'keep-compact',
    'gate_class': 'concrete-evidence',
    'witness_surface': 'APPLICABILITY-LEDGER.json#AP-0143',
    'applicability_state': 'gated',
    'repair': 'ordinary-continuation',
    'matched_budget': 'one compact witness foregrounding directly observed widening vs dependency-imputed vs topology-imputed spillover without widening into broader refresh-topology governance',
    'revision': REV,
    'target_objective': 'keep widened-scope-basis comparison honest without inflating a broader refresh-topology layer',
    'carry_object': 'refresh-scope-basis witness / spillover-basis card / map-glow brake',
    'applicability_conditions': [
        'affected components and directly observed widened surfaces remain distinguishable from upstream or adjacent distress',
        'some apparent widening is still only graph, map, context, or dependency-imputed and needs another step before public overclaim',
        'refresh scope basis remains subordinate to existing refresh-burden-scope, dependence-adjusted, and context-correlation witnesses rather than a new topology controller',
    ],
    'baselines': [
        'existing refresh-burden-scope-witness baseline',
        'existing dependence-adjusted and graph-analogy baseline',
        'existing obligation/overflow baseline',
        'existing witness-vocabulary baseline',
    ],
    'non_fit_slice': 'Do not generalize this revision into a refresh-topology court, spillover senate, blast-map governor, or graph-admissibility board without later overflow evidence.',
})
write('APPLICABILITY-LEDGER.json', json.dumps(obj, indent=2) + '\n')

# foreign pressure
obj = json.loads(read('FOREIGN-PRESSURE-LEDGER.json'))
obj['items'].append({
    'id': 'FP-0148',
    'title': 'refresh-scope-basis pressure pushes DelayBasin to extract one compact spillover-basis witness rather than a blast-map court',
    'state': 'imported',
    'source_packets': [
        {'datacube': 'StatuspageAffectedComponentImpact-2026', 'surfaces': ['REF-0932'], 'pressure': 'incident impact is based on affected components, which pressures DelayBasin to preserve a directly observed widening class instead of broadening by adjacency alone'},
        {'datacube': 'StatuspageThirdPartyOverride-2026', 'surfaces': ['REF-0934'], 'pressure': 'external incidents can be overridden when they do not affect the local service, which pressures DelayBasin to preserve a dependency-imputed spillover class instead of treating upstream trouble as directly observed widening'},
        {'datacube': 'DatadogObservedAndInferredDependencyMaps-2026', 'surfaces': ['REF-0940'], 'pressure': 'service maps show observed dependencies while resource dependency maps mark inferred dependencies and keep scope on the selected resource, which pressures DelayBasin to separate direct observation from dependency-imputed spillover'},
        {'datacube': 'GrafanaBlastRadiusAndTopologyGraphs-2026', 'surfaces': ['REF-0941'], 'pressure': 'entity graphs help predict blast radius and service graphs infer topology, which pressures DelayBasin to keep topology-imputed spillover distinct from directly observed widened scope'},
        {'datacube': 'OpenTelemetryContextPropagation-2026', 'surfaces': ['REF-0922'], 'pressure': 'context propagation correlates signals across services, which pressures DelayBasin to keep context-linked widening distinct from directly observed effect on each widened surface'},
    ],
    'reviewed_pattern': 'directly observed widened scope vs dependency- or topology-imputed spillover',
    'import_decision': 'support a compact refresh-scope-basis witness and resolve OQ-0144',
    'adopted_take': 'DelayBasin should add one compact witness that says whether current widened scope is directly-observed-widening, dependency-imputed-spillover, topology-imputed-spillover, or honestly mixed',
    'supporting_only_take': 'the current evidence cleanly supports a bounded refresh-scope-basis witness without promoting broader refresh-topology governance',
    'deferred_or_rejected_take': ['refresh-topology court','spillover senate','blast-map governor','graph-admissibility board'],
    'local_gap': 'the archive still lacked one compact successor surface for whether widened public scope was directly observed on the widened surface or only inferred through dependency or topology relations',
    'anchor_surfaces': ['docs/10-method/refresh-burden-scope-witnesses-same-claim-burden-upgrade-bounded-scope-widening-and-scope-gated-generalization.md','docs/20-constitution/open-question-registry.md','docs/00-meta/trajectory-map.md',f'docs/90-quarantine/wild-speculations-2026-03-08.md#{NEW_QWS}'],
    'open_question': 'OQ-0145',
    'repair': 'ordinary-continuation',
    'origin_revision': REV,
    'action_lane': 'keep-compact',
    'gate_class': 'concrete-evidence',
    'discharge': 'reopen-only-if-refresh-scope-basis-overflows',
    'revision': REV,
    'witness_surface': 'FOREIGN-PRESSURE-LEDGER.json#FP-0148',
    'pressure_state': 'imported',
    'bounded_take': 'Keep the archive compact by extracting one refresh-scope-basis witness over the existing refresh-burden-scope, dependency, topology, and context-correlation surfaces; do not promote a refresh-topology court, spillover senate, blast-map governor, or graph-admissibility board.',
    'explicit_non_take': ['no refresh-topology court','no spillover senate','no blast-map governor','no graph-admissibility board'],
    'assimilation_state': 'imported',
})
write('FOREIGN-PRESSURE-LEDGER.json', json.dumps(obj, indent=2) + '\n')

# transfer
obj = json.loads(read('DATACUBE-TRANSFER-LEDGER.json'))
obj['items'].append({
    'id': 'TL-0154',
    'title': 'refresh-scope-basis evidence supports resolving OQ-0144 with one compact spillover-basis card rather than a blast-map court',
    'state': 'supporting-only',
    'reviewed_pattern': 'directly observed widened scope vs dependency- or topology-imputed spillover',
    'import_decision': 'support a compact refresh-scope-basis witness and resolve OQ-0144',
    'adopted_take': 'DelayBasin should add one compact witness that says whether current widened scope is directly-observed-widening, dependency-imputed-spillover, topology-imputed-spillover, or honestly mixed',
    'supporting_only_take': 'the current evidence cleanly supports a bounded refresh-scope-basis witness without promoting broader refresh-topology governance',
    'deferred_or_rejected_take': ['refresh-topology court','spillover senate','blast-map governor','graph-admissibility board'],
    'local_gap': 'the archive still lacked one compact successor surface for whether widened public scope was directly observed or only spillover-imputed',
    'anchor_surfaces': ['docs/10-method/refresh-burden-scope-witnesses-same-claim-burden-upgrade-bounded-scope-widening-and-scope-gated-generalization.md','docs/20-constitution/open-question-registry.md','docs/00-meta/trajectory-map.md',f'docs/90-quarantine/wild-speculations-2026-03-08.md#{NEW_QWS}'],
    'open_question': 'OQ-0145',
    'repair': 'ordinary-continuation',
    'origin_revision': REV,
    'action_lane': 'keep-compact',
    'gate_class': 'concrete-evidence',
    'discharge': 'reopen-only-if-refresh-scope-basis-overflows',
    'revision': REV,
    'witness_surface': 'DATACUBE-TRANSFER-LEDGER.json#TL-0154',
    'transfer_state': 'supporting-only',
    'bounded_take': 'Keep the archive compact by extracting one refresh-scope-basis witness over the existing refresh-burden-scope, dependency, topology, and context-correlation surfaces; do not promote a refresh-topology court, spillover senate, blast-map governor, or graph-admissibility board.',
    'explicit_non_take': ['no refresh-topology court','no spillover senate','no blast-map governor','no graph-admissibility board'],
    'open_transfer_question': 'whether later passes should add a separate refresh-scope-extent witness once refresh scope basis is explicit',
    'missing_support': 'a later public check on whether one compact refresh-scope-basis witness keeps sufficing',
    'current_support': ['APPLICABILITY-LEDGER.json#AP-0143','FOREIGN-PRESSURE-LEDGER.json#FP-0148','DATACUBE-TRANSFER-LEDGER.json#TL-0154'],
    'discharge_path': 'either show later that one compact refresh-scope-basis witness keeps sufficing or promote broader refresh-topology governance explicitly',
    'reviewed_datacubes': [
        {'datacube': 'StatuspageAffectedComponentImpact-2026', 'surfaces': ['REF-0932'], 'pattern': 'incident impact is based on affected components', 'pressure': 'DelayBasin should preserve a directly observed widening class rather than broaden by adjacency alone'},
        {'datacube': 'StatuspageThirdPartyOverride-2026', 'surfaces': ['REF-0934'], 'pattern': 'third-party incidents can be overridden when they do not affect the local service', 'pressure': 'DelayBasin should preserve a dependency-imputed spillover class instead of promoting every upstream incident into directly observed widening'},
        {'datacube': 'DatadogObservedAndInferredDependencyMaps-2026', 'surfaces': ['REF-0940'], 'pattern': 'service maps show observed dependencies while resource dependency maps mark inferred dependencies', 'pressure': 'DelayBasin should separate directly observed widening from dependency-imputed spillover'},
        {'datacube': 'GrafanaBlastRadiusAndTopologyGraphs-2026', 'surfaces': ['REF-0941'], 'pattern': 'graphs help predict blast radius and infer topology', 'pressure': 'DelayBasin should separate topology-imputed spillover from directly observed widened scope'},
        {'datacube': 'OpenTelemetryContextPropagation-2026', 'surfaces': ['REF-0922'], 'pattern': 'signals correlate across services through shared context', 'pressure': 'DelayBasin should keep context-linked widening distinct from direct observation on the widened surface'},
    ],
})
write('DATACUBE-TRANSFER-LEDGER.json', json.dumps(obj, indent=2) + '\n')

# resolution
obj = json.loads(read('RESOLUTION-LEDGER.json'))
obj['items'].append({
    'id': 'RS-0151',
    'title': 'resolve OQ-0144 with one compact refresh-scope-basis witness rather than a blast-map governor',
    'state': 'resolved',
    'closure_state': 'resolved',
    'closure_reason': 'rev0249 extracted one compact refresh-scope-basis witness, kept the admitted refresh-burden-scope and graph analog surfaces narrow, and kept stronger refresh-topology-governance stories quarantined.',
    'discharge': 'reopen-only-if-refresh-scope-basis-overflows',
    'gate_class': 'concrete-evidence',
    'origin_revision': REV,
    'prior_state': 'open gap: DelayBasin already had refresh-burden-scope truth but still lacked one compact successor surface for whether widened public scope was directly observed on the widened surface or only dependency- or topology-imputed.',
    'question': 'whether one compact refresh-scope-basis witness over the existing refresh-burden-scope, dependency, topology, and context-correlation surfaces is enough for honest widened-scope-basis comparison',
    'reopen_trigger': 'refresh-scope-basis pressure overflows one compact successor surface',
    'reopen_triggers': ['later revisions need standing governance over graph admissibility, dependency-spillover authority, topology-evidence classes, or cross-row widening policy that one compact refresh-scope-basis witness cannot honestly absorb'],
    'repair': 'ordinary-continuation',
    'resolved_objects': ['OQ-0144','AP-0143','FP-0148','TL-0154'],
    'revision': REV,
    'successor_surface': NEW_DOC,
    'target_surfaces': [NEW_DOC],
    'action_lane': 'keep-compact',
    'witness_surface': 'RESOLUTION-LEDGER.json#RS-0151',
})
write('RESOLUTION-LEDGER.json', json.dumps(obj, indent=2) + '\n')

# retrospective queue
obj = json.loads(read('RETROSPECTIVE-QUEUE.json'))
obj['items'].append({
    'id': 'RT-0138',
    'title': 'revisit whether refresh-scope-basis pressure stayed bounded after rev0249',
    'state': 'cooling',
    'candidate_surface': f'docs/90-quarantine/wild-speculations-2026-03-08.md#{NEW_QWS}',
    'cooldown_window': 'keep the stronger refresh-topology court, spillover senate, blast-map governor, or graph-admissibility board story cooled until at least one later revision shows that one compact refresh-scope-basis witness is no longer enough.',
    'adjudication_family': 'refresh scope basis / spillover-basis gating / topology-governance pressure',
    'supersession_link': 'OBLIGATION-LEDGER.json#OB-0144',
    'origin_revision': REV,
    'discharge': 'keep-cooling-unless-refresh-scope-basis-overflows',
    'action_lane': 'keep-compact',
    'gate_class': 'overflow',
    'witness_surface': 'RETROSPECTIVE-QUEUE.json#RT-0138',
    'revision': REV,
    'cooling_state': 'cooling',
    'disposition': 'await-adjudication',
    'repair': 'keep-cooling',
})
write('RETROSPECTIVE-QUEUE.json', json.dumps(obj, indent=2) + '\n')

# revision receipt
receipt = json.loads(read('REVISION-RECEIPT.json'))
receipt['revision'] = REV
receipt['previous_revision'] = PREV
receipt['summary'] = 'Resolved OQ-0144 with one compact refresh-scope-basis witness that separates directly observed widened scope from dependency- or topology-imputed spillover while keeping stronger refresh-topology governance quarantined.'
receipt['canon_additions'] = [NEW_DOC, 'RS-0151 resolved OQ-0144 with one compact refresh-scope-basis witness']
receipt['quarantine_additions'] = [f'{NEW_QWS} — {NEW_QWS_LABEL}']
receipt['refs_used'] = [
    'docs/00-meta/bibliography.md#ref-0932',
    'docs/00-meta/bibliography.md#ref-0934',
    'docs/00-meta/bibliography.md#ref-0940',
    'docs/00-meta/bibliography.md#ref-0941',
    'docs/00-meta/bibliography.md#ref-0922',
]
receipt['touched_surfaces'] = [
    NEW_DOC,
    'docs/00-meta/bibliography.md',
    'docs/00-meta/llm-runbook.md',
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
    'REVISION-RECEIPT.json',
    'SURFACE-STATUS.json',
    'RELEASE-MANIFEST.json',
    'CHANGELOG.md',
    'ARCHIVE_INDEX.md',
    'tools/packet_contract_common.py',
    'tools/check_refresh_scope_basis_witness_contract.py',
    'tools/validation_toolchain_lib.py',
]
receipt['packaged_bundle_filename'] = BUNDLE
receipt['summary_highlight'] = SUMMARY_HIGHLIGHT
receipt['codename'] = CODENAME
receipt['created_at'] = CREATED_AT
receipt['basis_witness']['basis_surfaces'] = [NEW_DOC, 'docs/00-meta/trajectory-map.md', 'docs/20-constitution/open-question-registry.md']
receipt['basis_witness']['basis_state'] = 'current'
receipt['basis_witness']['basis_omission_basis'] = 'broader refresh-topology governance drafting was intentionally omitted from canon because the evidence only justified one bounded refresh-scope-basis witness'
receipt['scope_witness']['exact_target'] = 'resolve OQ-0144 with one compact refresh-scope-basis witness and keep stronger refresh-topology governance honestly quarantined'
receipt['scope_witness']['scope_surfaces'] = [NEW_DOC, 'docs/20-constitution/open-question-registry.md', 'docs/00-meta/trajectory-map.md', f'docs/90-quarantine/wild-speculations-2026-03-08.md#{NEW_QWS}']
receipt['scope_witness']['ambient_exclusions'] = ['no refresh-topology court','no spillover senate','no blast-map governor','no graph-admissibility board']
receipt['status_witness']['frozen_public_surface'] = BUNDLE
receipt['retrospective_write_witness'] = json.loads(json.dumps(json.loads(read('RETROSPECTIVE-QUEUE.json'))['items'][-1]))
receipt['followthrough_witness'] = json.loads(json.dumps(json.loads(read('FOLLOWTHROUGH-QUEUE.json'))['items'][-1]))
receipt['assumption_witness'] = json.loads(json.dumps(json.loads(read('ASSUMPTION-LEDGER.json'))['items'][-1]))
receipt['obligation_witness'] = json.loads(json.dumps(json.loads(read('OBLIGATION-LEDGER.json'))['items'][-1]))
receipt['applicability_witness'] = json.loads(json.dumps(json.loads(read('APPLICABILITY-LEDGER.json'))['items'][-1]))
receipt['foreign_pressure_witness'] = json.loads(json.dumps(json.loads(read('FOREIGN-PRESSURE-LEDGER.json'))['items'][-1]))
receipt['transfer_witness'] = json.loads(json.dumps(json.loads(read('DATACUBE-TRANSFER-LEDGER.json'))['items'][-1]))
receipt['resolution_witness'] = json.loads(json.dumps(json.loads(read('RESOLUTION-LEDGER.json'))['items'][-1]))
receipt['vocabulary_witness'] = {
    'witness_surface': 'WITNESS-VOCABULARY.json',
    'controlled_families': ['action_lane','gate_class',NEW_FAMILY],
    'target_surfaces': ['WITNESS-VOCABULARY.json','REVISION-RECEIPT.json',NEW_DOC],
    'ambient_synonyms_excluded': ['graph-glow-means-observed','upstream-trouble-means-we-are-hit','map-edge-counts-as-impact','basis-ish'],
    'comparability_budget': 'refresh-scope-basis truth is compared by token; the compact refresh-scope-basis witness says whether widened public scope is directly observed, dependency-imputed, topology-imputed, or honestly mixed, while exact component ids, graph nodes, trace ids, path enumerations, service names, and long blast-radius narratives stay in surrounding prose',
    'vocabulary_state': 'locked',
    'repair': 'ordinary-continuation',
}
receipt['summary_highlight'] = SUMMARY_HIGHLIGHT
receipt['codename'] = CODENAME
receipt['comparison_witness'] = {
    'previous_revision': PREV,
    'current_revision': REV,
    'current_pressure_id': 'FP-0148',
    'current_import_id': 'TL-0154',
    'basis_surface': 'docs/10-method/refresh-burden-scope-witnesses-same-claim-burden-upgrade-bounded-scope-widening-and-scope-gated-generalization.md',
    'delta_surface': NEW_DOC,
    'comparison_summary': 'rev0249 adds one compact refresh-scope-basis witness so widened public scope no longer stands in for directly observed widened impact when the evidence is only dependency- or topology-imputed.',
}
receipt['changes'] = [
    {'kind': 'canon', 'surface': NEW_DOC, 'summary': 'added one compact refresh-scope-basis witness with directly-observed, dependency-imputed, topology-imputed, and mixed states'},
    {'kind': 'quarantine', 'surface': f'docs/90-quarantine/wild-speculations-2026-03-08.md#{NEW_QWS}', 'summary': 'kept stronger refresh-topology governance quarantined rather than promoting it into canon'},
    {'kind': 'hygiene', 'surface': 'tools/validation_toolchain_lib.py', 'summary': 'centralized pattern-based insertion into one helper path'},
]
receipt['receipt_freshness_witness'] = {
    'packaged_bundle_filename': BUNDLE,
    'manifest_timestamp_token': STAMP,
    'receipt_timestamp_token': STAMP,
    'bundle_stem_suffix_relation': f'slug ends with {SUMMARY_HIGHLIGHT} + {CODENAME} and remains aligned to the current summary/codename pair while preserving the topologyquarantine middle token',
    'current_import_id': 'TL-0154',
    'current_pressure_id': 'FP-0148',
    'change_anchor_surface': 'CHANGELOG.md',
    'freshness_state': 'current-aligned',
    'repair': 'ordinary-continuation',
}
receipt['question_posture_witness'] = {
    'resolution_surface': 'RESOLUTION-LEDGER.json',
    'registry_surface': 'docs/20-constitution/open-question-registry.md',
    'trajectory_surface': 'docs/00-meta/trajectory-map.md',
    'synced_resolved_questions': ['OQ-0144'],
    'frontier_selection_rule': 'resolved OQ-0144 is synchronized across resolution ledger, registry, and trajectory while frontier selection advances to OQ-0145',
    'posture_state': 'resolved-sync-current',
    'repair': 'ordinary-continuation',
}
receipt['current_import_id'] = 'TL-0154'
receipt['current_pressure_id'] = 'FP-0148'
receipt['import_witness'] = receipt['transfer_witness']
receipt['new_classes_or_families'] = [NEW_FAMILY]
receipt['quarantined_non_take'] = ['refresh-topology court','spillover senate','blast-map governor','graph-admissibility board']
receipt['artifacts_touched'] = receipt['touched_surfaces']
receipt['refresh_scope_basis_witness'] = {
    'witness_surface': NEW_DOC,
    'family': NEW_FAMILY,
    'state_tokens': ['directly-observed-widening','dependency-imputed-spillover','topology-imputed-spillover','mixed-refresh-scope-basis'],
    'overflow_rule': 'reopen-only-if-refresh-scope-basis-overflows',
}
write('REVISION-RECEIPT.json', json.dumps(receipt, indent=2) + '\n')

# --- changelog / archive index / status / manifest ---
changelog_top = f'''## {REV} - 2026.03.27.23.58 - scopebasis / topologyquarantine / mapcarry / lensglass\n\n- Canon move: resolved `OQ-0144` with `{NEW_DOC}`, adding one compact `refresh_scope_basis_state` witness that keeps directly observed widening distinct from dependency-imputed and topology-imputed spillover.\n- Bold but disciplined speculative move: quarantined the **refresh-topology court / spillover senate / blast-map governor** story in `QWS-0227` rather than quietly promoting a stronger refresh-topology layer into canon.\n- Hygiene/meta-engineering improvement: added `tools/check_refresh_scope_basis_witness_contract.py`, widened `WITNESS-VOCABULARY.json` with a tiny `refresh_scope_basis_state` family, and refactored `tools/validation_toolchain_lib.py` so pattern-based tool insertion goes through one shared helper path instead of repeated call-shapes.\n- Contract continuity: preserved the existing refresh-burden-scope, dependency, and topology chain unchanged while adding the new spillover-basis card.\n\n'''
write('CHANGELOG.md', changelog_top + read('CHANGELOG.md'))

archive_text = read('ARCHIVE_INDEX.md')
new_row = f'| {BUNDLE} | 2026-03-27 | Refresh-scope-basis revision: resolved OQ-0144 with a compact directly-observed-vs-spillover basis witness, honestly quarantined stronger refresh-topology governance, and refactored validation-tool pattern insertion to stay wired and cumulative. |\n'
archive_text = archive_text.replace('| DelayBasin-rev0248-2026.03.27.23.49-scopewidening-blastquarantine-boundcarry-scopeglass.zip | 2026-03-27 | Refresh-burden-scope revision: resolved OQ-0143 with a compact same-claim-vs-widened-scope witness, honestly quarantined stronger blast-radius governance, and refactored validation-tool glob expansion to stay wired and cumulative. |\n', new_row + '| DelayBasin-rev0248-2026.03.27.23.49-scopewidening-blastquarantine-boundcarry-scopeglass.zip | 2026-03-27 | Refresh-burden-scope revision: resolved OQ-0143 with a compact same-claim-vs-widened-scope witness, honestly quarantined stronger blast-radius governance, and refactored validation-tool glob expansion to stay wired and cumulative. |\n')
write('ARCHIVE_INDEX.md', archive_text)

status = json.loads(read('SURFACE-STATUS.json'))
status['operational_head']['revision'] = REV
status['status_lanes']['frozen_public_surface'] = BUNDLE
status['status_lanes']['current_release_surface'] = BUNDLE
status['citation_head']['revision'] = REV
status['citation_head']['surface'] = BUNDLE
status['previous_citation_head']['revision'] = PREV
status['previous_citation_head']['surface'] = f'DelayBasin-{PREV}-2026.03.27.23.49-scopewidening-blastquarantine-boundcarry-scopeglass.zip' if PREV=='rev0248' else status['previous_citation_head']['surface']
status['revision'] = REV
status['stamp'] = STAMP
status['slug'] = SLUG
write('SURFACE-STATUS.json', json.dumps(status, indent=2) + '\n')

manifest = {'project': 'DelayBasin', 'revision': REV, 'timestamp': STAMP, 'slug': SLUG, 'bundle': BUNDLE}
write('RELEASE-MANIFEST.json', json.dumps(manifest, indent=2) + '\n')
