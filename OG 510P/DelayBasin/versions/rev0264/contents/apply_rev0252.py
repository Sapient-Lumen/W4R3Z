from __future__ import annotations

import json
from pathlib import Path
from textwrap import dedent

ROOT = Path('.')
REV = 'rev0252'
PREV = 'rev0251'
STAMP = '2026.03.28.01.04'
CREATED_AT = '2026-03-28T01:04:00-04:00'
SLUG = 'scopeaxis-axisquarantine-crosscarry-vectorglass'
BUNDLE = f'DelayBasin-{REV}-{STAMP}-{SLUG}.zip'
SUMMARY_HIGHLIGHT = 'crosscarry'
CODENAME = 'vectorglass'

NEW_DOC = 'docs/10-method/refresh-scope-axis-witnesses-one-axis-dispersion-cross-axis-corroboration-and-axis-gated-generalization.md'
NEW_CHECKER = 'tools/check_refresh_scope_axis_witness_contract.py'
NEW_FAMILY = 'refresh_scope_axis_state'
NEW_QWS = 'QWS-0230'
NEW_QWS_LABEL = 'refresh-axis court / axis quorum / corroboration simplex'


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


def prepend(path: str, addition: str) -> None:
    text = read(path)
    if addition.strip() in text:
        return
    write(path, addition + text)


def replace_once(path: str, old: str, new: str) -> None:
    text = read(path)
    if old not in text:
        raise SystemExit(f'old block not found in {path}: {old!r}')
    write(path, text.replace(old, new, 1))


DOC_TEXT = dedent("""
# Refresh-scope-axis witnesses, one-axis dispersion, cross-axis corroboration, and axis-gated generalization

This is the compact successor surface for `OQ-0147`.

## Practice / observation

Once DelayBasin can separate **clustered observed spillover** from **dispersed observed spillover**, one more local ambiguity remains.

Some dispersion is still one-axis.
The widening is genuinely dispersed, but only across one named family axis: several component groups, several teams, several services, several partitions, several zones, several source clusters, or several query buckets.
That is broader than one local cluster.
But it is still only one partition view.

Some dispersion is cross-axis corroborated.
The same widened spread is now visible across independent family axes rather than only one naming scheme.
Several teams and several services are implicated.
Several zones and several nodes are implicated.
Several products and several environments are implicated.
That is the point where stronger diffusion talk becomes more honest.

And some cases are still gated.
One axis looks dispersed, but the second axis is still missing, mirrored, nested, or not yet independently shown.
The archive needs one more compact witness before it turns one-axis dispersion into robust cross-axis corroboration talk.

DelayBasin does not need an axis quorum board for that.
It needs one bounded witness that says whether the present dispersed widening still lives on one named axis, is corroborated across independent axes, is still axis-gated from broader generalization, or is honestly mixed.

## External pressure from Alertmanager multi-label grouping, Grafana AND-routed labels, Datadog grouped attributes, Kubernetes multi-dimensional labels and multi-constraint spread, and Google Cloud layered dimensions

1. Alertmanager route configuration supports `group_by` over multiple labels, and child routes can regroup alerts by a different label set such as `product` and `environment` instead of `cluster` and `alertname`. That pressures DelayBasin to distinguish dispersion that is only visible on one label axis from dispersion corroborated across independent axes. ([`REF-0951`](../00-meta/bibliography.md))

2. Grafana notification policies route alerts by label matchers, and when multiple label matchers are used they are combined with logical AND. Grafana also groups alerts only when the selected labels have the same exact values. That pressures DelayBasin to distinguish one-axis grouping from corroboration that survives an additional independent matcher axis. ([`REF-0952`](../00-meta/bibliography.md))

3. Datadog monitor queries can already be grouped by multiple attributes such as `topic` and `partition`, while `notify_by` can collapse notifications onto one chosen group axis such as `topic`. That pressures DelayBasin to distinguish underlying multi-attribute spread from the thinner one-axis surface that notifications may still expose. ([`REF-0953`](../00-meta/bibliography.md))

4. Kubernetes says managed objects are often multi-dimensional and that management often requires cross-cutting operations rather than a single rigid hierarchy. It also recommends multiple labels when resource sets must be distinguished along more than one dimension. That pressures DelayBasin to distinguish one named family axis from corroboration across independent axes. ([`REF-0954`](../00-meta/bibliography.md))

5. Kubernetes topology spread constraints can be defined one at a time or in multiple entries, and the scheduler only considers placements that satisfy all defined constraints. Kubernetes gives an explicit example of combining zone and node constraints together. That pressures DelayBasin to distinguish one-axis dispersion from cross-axis corroboration. ([`REF-0956`](../00-meta/bibliography.md))

6. Google Cloud says the default resource hierarchy models only a few business dimensions and lacks the flexibility to layer multiple business dimensions together, which is why tags exist as an additional annotation layer. That pressures DelayBasin to name when a wider story is still only one axis versus corroborated across layered dimensions. ([`REF-0955`](../00-meta/bibliography.md))

GPUstorming makes the pressure vivid. An open search can look dispersed across one visible axis — many cards, many sources, many grouped buckets — while still resting on one partition view. Unless the same widening survives another independent axis such as query framing, grouping labels, or route shape, DelayBasin should not narrate fully corroborated diffusion.

## Working synthesis

> DelayBasin should preserve one compact **refresh-scope-axis witness / axis-corroboration card / one-axis brake** whenever a current continuity claim depends not only on whether public scope widened, on whether that widening is directly observed, on whether the observed widening is already a broader pattern, and on whether it is clustered or dispersed, but on whether the present dispersed spread still lives on one named family axis or is corroborated across independent family axes. Name the **governed row or surface**, the **stake object / line of concern**, the **prior refresh-scope-distribution evidence**, the **current dispersed-scope evidence**, the **one-axis family basis if any**, the **independent-axis corroboration if any**, the **axis gate / mirrored-axis remainder if any**, the **`refresh_scope_axis_state`**, and the **fail-closed repair / keep-current vs narrow-claim vs split-scope vs issue-new-refresh-scope-axis-witness vs quarantine-refresh-axis-governance consequence**. Keep raw label matrices, axis inventories, topology maps, full route trees, and long corroboration narratives outside the compact token. Do not let one-axis dispersion silently count as cross-axis corroborated spread.

## One-axis dispersion vs cross-axis corroborated dispersion vs axis-gated generalization vs mixed refresh scope axis

Use the controlled family `refresh_scope_axis_state`:

- **one-axis-dispersion** says the current dispersed widening is real, but still only visible across one named family axis.
- **cross-axis-corroborated-dispersion** says the current dispersed widening is corroborated across independent family axes rather than only one partition view.
- **axis-gated-generalization** says some axis corroboration exists, but broader family-class or archive-wide generalization is still gated by missing, mirrored, or uncovered axes.
- **mixed-refresh-scope-axis** says the current situation honestly combines one-axis and cross-axis signals such that no single class stays honest.

So the witness does not create a standing corroboration simplex.
It only says how many independent axes the currently dispersed widening has honestly crossed.

## Countermodels / probes

1. **Refresh-scope-distribution already covers this countermodel**
   - Maybe once clustered-vs-dispersed truth is explicit, a separate axis witness adds no real value.
   - Probe: compare later rereads that preserve only refresh-scope-distribution truth against rereads that also preserve one compact refresh-scope-axis witness and inspect whether one-axis dispersion still gets narrated as cross-axis corroboration.

2. **Axis layering is only naming convenience countermodel**
   - Maybe labels, tags, routes, and topology keys are too operational or arbitrary to justify a new archive witness.
   - Probe: look for later cases where ordinary continuity prose still slides from one visible partition axis to broader diffusion talk even when no second independent axis was shown.

3. **Axis corroboration is covert governance countermodel**
   - Maybe once one-axis-vs-cross-axis truth matters, the archive is really sneaking in a broader axis court.
   - Probe: only reopen stronger machinery if later revisions repeatedly need standing rules for axis independence, mirrored-axis exclusion, or corroboration thresholds that one bounded witness cannot absorb.

## Design consequences

- DelayBasin can now separate **dispersion across one named family axis** from **dispersion corroborated across independent axes**.
- The archive gets one explicit place to record when spread is broad but still one-view only.
- Refresh scope distribution and refresh scope axis now separate **how observed widening is distributed across widened families** from **how many independent axes corroborate that dispersion**.
- Stronger refresh-axis-governance stories stay quarantined until later overflow instead of sneaking in through cross-axis rhetoric.

## Overflow test

Reopen this compact witness only if later revisions repeatedly need standing governance over axis independence, corroboration thresholds, mirrored-axis exclusions, or axis quorum policy that one bounded refresh-scope-axis witness cannot honestly absorb.

## Transformer-facing implication

A later pass should not treat dispersed spread across one named family axis as if it were already robust cross-axis corroboration merely because the widening looks broad inside that axis. Preserve the exact one-axis basis if any, the independent-axis corroboration if any, the mirrored or missing remainder if any, and the exact `refresh_scope_axis_state` before claiming that the widening is already corroborated across independent axes.
""").lstrip()

write(NEW_DOC, DOC_TEXT)
write(NEW_CHECKER, "from packet_contract_common import require_named_refresh_scope_axis_witness_packet_and_vocabulary\n\nrequire_named_refresh_scope_axis_witness_packet_and_vocabulary(\"refresh_scope_axis_witness_contract\")\n\nprint(\"check_refresh_scope_axis_witness_contract: OK\")\n")

# bibliography
BIB_ADD = dedent("""

- `REF-0951` — Prometheus Documentation, **Configuration** (accessed 2026-03-28)
  - URL: https://prometheus.io/docs/alerting/latest/configuration/
  - Load-bearing use: Alertmanager route configuration supports grouping by multiple labels and child routes can regroup alerts by a different label set such as `product` and `environment`, which pressures DelayBasin to distinguish one-axis dispersion from cross-axis corroboration.

- `REF-0952` — Grafana Documentation, **Notification policies** and **Group alert notifications** (accessed 2026-03-28)
  - URL: https://grafana.com/docs/grafana/latest/alerting/fundamentals/notifications/notification-policies/
  - URL: https://grafana.com/docs/grafana/latest/alerting/fundamentals/notifications/group-alert-notifications/
  - Load-bearing use: multiple label matchers are combined with logical AND and alerts group only when selected labels have the same exact values, which pressures DelayBasin to distinguish one-axis grouping from corroboration that survives an additional independent axis.

- `REF-0953` — Datadog Documentation, **Alert aggregation** (accessed 2026-03-28)
  - URL: https://docs.datadoghq.com/monitors/guide/alert_aggregation/
  - Load-bearing use: monitor queries can already be grouped by multiple attributes such as `topic` and `partition`, while `notify_by` can collapse notifications onto one chosen group axis, which pressures DelayBasin to distinguish underlying multi-attribute spread from a thinner one-axis notification surface.

- `REF-0954` — Kubernetes Documentation, **Labels and Selectors** (accessed 2026-03-28)
  - URL: https://kubernetes.io/docs/concepts/overview/working-with-objects/labels/
  - Load-bearing use: Kubernetes objects are often multi-dimensional and management often requires cross-cutting operations across multiple labels, which pressures DelayBasin to distinguish one named family axis from corroboration across independent axes.

- `REF-0955` — Google Cloud Documentation, **Tags overview** (accessed 2026-03-28)
  - URL: https://docs.cloud.google.com/resource-manager/docs/tags/tags-overview
  - Load-bearing use: the default Google Cloud resource hierarchy lacks the flexibility to layer multiple business dimensions together, which pressures DelayBasin to name when a wider story is still only one axis versus corroborated across layered dimensions.

- `REF-0956` — Kubernetes Documentation, **Pod Topology Spread Constraints** (accessed 2026-03-28)
  - URL: https://kubernetes.io/docs/concepts/scheduling-eviction/topology-spread-constraints/
  - Load-bearing use: Kubernetes allows multiple topology spread constraints and gives an explicit example combining zone and node constraints, where the scheduler only considers placements satisfying all constraints, which pressures DelayBasin to distinguish one-axis dispersion from cross-axis corroboration.
""")
insert_after('docs/00-meta/bibliography.md', '- `REF-0950` — Google Cloud Documentation, **Regions and zones** (accessed 2026-03-28)\n  - URL: https://docs.cloud.google.com/compute/docs/regions-zones\n  - Load-bearing use: resources are distributed across multiple zones and regions to tolerate outages, and zones are designed to minimize correlated failures, which pressures DelayBasin to distinguish one local correlated cluster from dispersed multi-zone or multi-region spread.\n', BIB_ADD)

# runbook/docs readme
insert_after('docs/00-meta/llm-runbook.md', 'Use `docs/10-method/refresh-scope-distribution-witnesses-clustered-observed-spillover-dispersed-observed-spillover-and-distribution-gated-generalization.md` when the live question is whether broader directly observed spillover still clusters inside one named widened family or is honestly dispersed across several widened families.\n', '\nUse `docs/10-method/refresh-scope-axis-witnesses-one-axis-dispersion-cross-axis-corroboration-and-axis-gated-generalization.md` when the live question is whether dispersed observed spillover still lives on one named family axis or is corroborated across independent family axes.\n')
insert_after('docs/README.md', '- [`10-method/refresh-scope-distribution-witnesses-clustered-observed-spillover-dispersed-observed-spillover-and-distribution-gated-generalization.md`](10-method/refresh-scope-distribution-witnesses-clustered-observed-spillover-dispersed-observed-spillover-and-distribution-gated-generalization.md)\n', '- [`10-method/refresh-scope-axis-witnesses-one-axis-dispersion-cross-axis-corroboration-and-axis-gated-generalization.md`](10-method/refresh-scope-axis-witnesses-one-axis-dispersion-cross-axis-corroboration-and-axis-gated-generalization.md)\n')

# claim registry
CLAIM_ADD = dedent("""

- `CL-0145` — Archive continuity may improve when DelayBasin preserves one compact **refresh-scope-axis witness / axis-corroboration card / one-axis brake** whenever a current continuity claim depends not only on whether public scope widened, on whether that widening is directly observed, on whether the observed widening is already a broader pattern, and on whether it is clustered or dispersed, but on whether the present dispersed spread still lives on one named family axis or is corroborated across independent family axes: name the **governed row or surface**, the **stake object / line of concern**, the **prior refresh-scope-distribution evidence**, the **current dispersed-scope evidence**, the **one-axis family basis if any**, the **independent-axis corroboration if any**, the **axis gate or mirrored-axis remainder if any**, the **refresh_scope_axis_state**, and the **fail-closed repair** rather than letting one-axis dispersion silently count as cross-axis corroborated spread.
  - Status: speculative but central
  - Wired docs: `docs/10-method/refresh-scope-axis-witnesses-one-axis-dispersion-cross-axis-corroboration-and-axis-gated-generalization.md`, `docs/20-constitution/open-question-registry.md`, `docs/20-constitution/prompt-pair-registry.md`, `docs/50-promptcraft/prompt-pairs.md`, `docs/00-meta/llm-runbook.md`, `WITNESS-VOCABULARY.json`, `REVISION-RECEIPT.json`
""")
insert_after('docs/20-constitution/claim-registry.md', '- `CL-0144` — Archive continuity may improve when DelayBasin preserves one compact **refresh-scope-distribution witness / diffusion card / cluster-spread brake** whenever a current continuity claim depends not only on whether public scope widened, on whether that widened scope is directly observed, and on whether the observed widening already forms a broader pattern, but on whether the present observed spillover still clusters inside one named widened family or is honestly dispersed across several widened families: name the **governed row or surface**, the **stake object / line of concern**, the **prior refresh-scope-extent evidence**, the **current widened-scope evidence**, the **observed clustered-family basis if any**, the **dispersed widened-family evidence if any**, the **distribution gate or uncovered family remainder if any**, the **refresh_scope_distribution_state**, and the **fail-closed repair** rather than letting a local observed cluster silently count as dispersed spread.\n  - Status: speculative but central\n  - Wired docs: `docs/10-method/refresh-scope-distribution-witnesses-clustered-observed-spillover-dispersed-observed-spillover-and-distribution-gated-generalization.md`, `docs/20-constitution/open-question-registry.md`, `docs/20-constitution/prompt-pair-registry.md`, `docs/50-promptcraft/prompt-pairs.md`, `docs/00-meta/llm-runbook.md`, `WITNESS-VOCABULARY.json`, `REVISION-RECEIPT.json`\n', CLAIM_ADD)

# open question registry / trajectory map
old_oq_block = dedent("""
- `OQ-0147` — what minimal refresh-scope-axis witness distinguishes dispersed spread across one named family axis from dispersed spread corroborated across independent family axes?
  - Why it matters: if DelayBasin cannot separate one-axis dispersion from cross-axis corroborated dispersion, later sessions may narrate archive-wide diffusion from a still single-partition view.
  - Current posture: unresolved
""")
new_oq_block = dedent("""
- `OQ-0147` — what minimal refresh-scope-axis witness distinguishes dispersed spread across one named family axis from dispersed spread corroborated across independent family axes?
  - Why it matters: if DelayBasin cannot separate one-axis dispersion from cross-axis corroborated dispersion, later sessions may narrate archive-wide diffusion from a still single-partition view.
  - Current posture: resolved by `RS-0154` via `docs/10-method/refresh-scope-axis-witnesses-one-axis-dispersion-cross-axis-corroboration-and-axis-gated-generalization.md`; reopen only if the compact refresh-scope-axis witness proves insufficient and stronger refresh-axis governance is honestly required

- `OQ-0148` — what minimal refresh-scope-axis-independence witness distinguishes genuinely independent corroborating axes from renamed, nested, or mirrored variants of one underlying axis?
  - Why it matters: if DelayBasin cannot separate independent axes from renamed or nested restatements of one partition, later sessions may narrate cross-axis corroboration from duplicate views of the same underlying spread.
  - Current posture: unresolved
""")
replace_once('docs/20-constitution/open-question-registry.md', old_oq_block, new_oq_block)

old_traj_block = dedent("""
103. Determine what minimal refresh-scope-axis witness distinguishes dispersed spread across one named family axis from dispersed spread corroborated across independent family axes.

A fresh extension is that once clustered-vs-dispersed truth is explicit, DelayBasin may next need to say whether the dispersion still lives inside one grouping axis or is corroborated across independent family axes. Otherwise one partition view may silently become archive-wide diffusion talk.
- `OQ-0147` — what minimal refresh-scope-axis witness distinguishes dispersed spread across one named family axis from dispersed spread corroborated across independent family axes?
  - Why it matters: if DelayBasin cannot separate one-axis dispersion from cross-axis corroborated dispersion, later sessions may narrate archive-wide diffusion from a still single-partition view.
  - Current posture: unresolved
""")
new_traj_block = dedent("""
103. Determine what minimal refresh-scope-axis witness distinguishes dispersed spread across one named family axis from dispersed spread corroborated across independent family axes.

A fresh extension is that once clustered-vs-dispersed truth is explicit, DelayBasin may next need to say whether the dispersion still lives inside one grouping axis or is corroborated across independent family axes. Otherwise one partition view may silently become archive-wide diffusion talk.
- `OQ-0147` — what minimal refresh-scope-axis witness distinguishes dispersed spread across one named family axis from dispersed spread corroborated across independent family axes?
  - Why it matters: if DelayBasin cannot separate one-axis dispersion from cross-axis corroborated dispersion, later sessions may narrate archive-wide diffusion from a still single-partition view.
  - Current posture: resolved by `RS-0154` via `docs/10-method/refresh-scope-axis-witnesses-one-axis-dispersion-cross-axis-corroboration-and-axis-gated-generalization.md`; reopen only if the compact refresh-scope-axis witness proves insufficient and stronger refresh-axis governance is honestly required

104. Determine what minimal refresh-scope-axis-independence witness distinguishes genuinely independent corroborating axes from renamed, nested, or mirrored variants of one underlying axis.

A fresh extension is that once one-axis-vs-cross-axis truth is explicit, DelayBasin may next need to say whether apparently different axes are genuinely independent or only renamed, nested, or mirrored restatements of one underlying partition. Otherwise duplicate views may silently become corroboration talk.
- `OQ-0148` — what minimal refresh-scope-axis-independence witness distinguishes genuinely independent corroborating axes from renamed, nested, or mirrored variants of one underlying axis?
  - Why it matters: if DelayBasin cannot separate independent axes from renamed or nested restatements of one partition, later sessions may narrate cross-axis corroboration from duplicate views of the same underlying spread.
  - Current posture: unresolved
""")
replace_once('docs/00-meta/trajectory-map.md', old_traj_block, new_traj_block)

# prompt pair registry and prompt pairs
PP_REG_ADD = dedent("""

- `PP-0105` — Name whether dispersed spread is still one-axis or already cross-axis corroborated
  - Goal: keep one-axis dispersion from silently inheriting cross-axis corroboration by requiring explicit one-axis family basis, any independent-axis corroboration, any axis gate or mirrored remainder, `refresh_scope_axis_state`, and fail-closed repair before later passes call the spread robust across independent axes.
  - Canonical text: `docs/50-promptcraft/prompt-pairs.md#pp-0105--name-whether-dispersed-spread-is-still-one-axis-or-already-cross-axis-corroborated`
""")
insert_after('docs/20-constitution/prompt-pair-registry.md', '- `PP-0104` — Name whether observed spillover is still clustered or already dispersed across widened families\n  - Goal: keep a local observed family cluster from silently inheriting dispersed diffusion by requiring explicit clustered-family evidence, any dispersed-family evidence, any uncovered remainder or distribution gate, `refresh_scope_distribution_state`, and fail-closed repair before later passes call the spread family-diffuse.\n  - Canonical text: `docs/50-promptcraft/prompt-pairs.md#pp-0104--name-whether-observed-spillover-is-still-clustered-or-already-dispersed-across-widened-families`\n', PP_REG_ADD)

PROMPT_ADD = dedent("""

Use `docs/10-method/refresh-scope-axis-witnesses-one-axis-dispersion-cross-axis-corroboration-and-axis-gated-generalization.md` when the live question is whether dispersed observed spillover still lives on one named family axis or is corroborated across independent family axes.

## `PP-0105` — Name whether dispersed spread is still one-axis or already cross-axis corroborated

**Opening prompt**

```text
Read the latest DelayBasin archive and inspect whether the current revision should also materialize one compact refresh-scope-axis witness for honest one-axis-vs-cross-axis dispersed-spread comparison.

Focus only on whether the already-dispersed observed spillover still lives on one named family axis, is corroborated across independent family axes, is still axis-gated from broader generalization, or is honestly mixed.

If yes, preserve exactly one small witness that:
- names the governed row or surface,
- names the stake object / line of concern,
- names the prior refresh-scope-distribution evidence,
- names the current dispersed-scope evidence,
- names the one-axis family basis if any,
- names the independent-axis corroboration if any,
- names the axis gate or mirrored-axis remainder if any,
- names the `refresh_scope_axis_state` / whether this is one-axis-dispersion, cross-axis-corroborated-dispersion, axis-gated-generalization, or mixed-refresh-scope-axis,
- states what stronger surfaces still outrank the witness,
- and states the fail-closed repair / keep-current vs narrow-claim vs split-scope vs issue-new-refresh-scope-axis-witness vs quarantine-refresh-axis-governance consequence if the present continuity claim is really only one-axis dispersion rather than cross-axis corroboration.

Do not use refresh scope axis as a general corroboration court. Use this prompt pair only where dispersed widening is already real and the missing question is whether the dispersion still lives on one named family axis or is honestly corroborated across independent axes.
```

**Continuation prompt**

```text
Continue the refresh-scope-axis pass with one high-leverage one-axis-vs-cross-axis clarification only. Prefer the smallest witness that says what governed row is still being justified, what stake object is supposedly widened, what prior refresh-scope-distribution evidence exists, what current dispersed-scope evidence exists, what one-axis family basis if any now exists, what independent-axis corroboration if any now exists, what axis gate or mirrored remainder if any still remains, what `refresh_scope_axis_state` is honest, what stronger surfaces still outrank the witness, and what keep-current, narrow-claim, split-scope, issue-new-refresh-scope-axis-witness, quarantine, or recover-resync consequence follows if the current claim is really one-axis-dispersion, cross-axis-corroborated-dispersion, axis-gated-generalization, or mixed-refresh-scope-axis. Run `make lint` and package the release.
```
""")
insert_after('docs/50-promptcraft/prompt-pairs.md', 'Continue the refresh-scope-distribution pass with one high-leverage cluster-vs-dispersion clarification only. Prefer the smallest witness that says what governed row is still being justified, what stake object is supposedly widened, what prior refresh-scope-extent evidence exists, what current widened-scope evidence exists, what observed clustered-family basis if any now exists, what dispersed widened-family evidence if any now exists, what distribution gate or uncovered family remainder if any still remains, what `refresh_scope_distribution_state` is honest, what stronger surfaces still outrank the witness, and what keep-current, narrow-claim, split-scope, issue-new-refresh-scope-distribution-witness, quarantine, or recover-resync consequence follows if the current claim is really clustered-observed-spillover, dispersed-observed-spillover, distribution-gated-generalization, or mixed-refresh-scope-distribution. Run `make lint` and package the release.\n```\n', PROMPT_ADD)

# quarantine
QWS_ADD = dedent("""

## QWS-0230 — Some continuations may eventually need a refresh-axis court / axis quorum / corroboration simplex rather than only a compact refresh-scope-axis witness

### Claim

A bolder possibility is that DelayBasin may eventually need not only a compact witness for whether dispersed widening still lives on one named family axis or is corroborated across independent family axes, but also a governed public rule for what counts as an independent axis at all, when mirrored or nested axes still count as one view, and how much cross-axis corroboration is enough before broader diffusion talk is admissible. Alertmanager multi-label regrouping, Grafana AND-routed labels, Datadog grouped attributes with one-axis notification collapse, Kubernetes multi-dimensional labels, Kubernetes multi-constraint spread, and Google Cloud layered tag dimensions all suggest a stronger axis-governance story: perhaps some future archive lines should not only be classified as `one-axis-dispersion`, `cross-axis-corroborated-dispersion`, `axis-gated-generalization`, or `mixed-refresh-scope-axis`, but admitted through a small axis quorum, corroboration simplex, or cross-axis governor. ([`REF-0951`](../00-meta/bibliography.md), [`REF-0952`](../00-meta/bibliography.md), [`REF-0953`](../00-meta/bibliography.md), [`REF-0954`](../00-meta/bibliography.md), [`REF-0955`](../00-meta/bibliography.md), [`REF-0956`](../00-meta/bibliography.md))

The narrower speculative move is only this: a future bounded surface *might* need to say not just how many axes currently corroborate the widening, but what minimum independence test or quorum makes those axes count as truly distinct.

### What follows if true

- some future continuity cards may need explicit axis-independence or mirrored-axis exclusion rules rather than one static refresh-scope-axis label;
- DelayBasin may eventually need a compact axis quorum that stays smaller than a general corroboration court;
- archive-wide diffusion talk may need an explicit cross-axis gate rather than prose confidence alone;
- future revisions should look for cases where one-axis dispersion repeatedly gets mistaken for robust corroboration even after the compact witness exists.

### What would count against it

- repeated later passes show that one compact refresh-scope-axis witness keeps one-axis-vs-cross-axis truth honest without standing corroboration governance;
- apparently separate axes usually turn out to be obviously distinct or obviously mirrored without requiring a new public rule;
- the archive does not repeatedly need explicit axis-independence tests, mirrored-axis exclusions, or corroboration thresholds;
- stronger axis-governance prose never pays for itself beyond the compact witness.

### Why it stays quarantined

The tempting overreach would be to declare that DelayBasin now needs a public refresh-axis court, axis quorum, or corroboration simplex. DelayBasin has not earned that. This note is bold enough to keep in quarantine but not yet honest enough for canon. Do not promote a refresh-axis court, axis quorum, or corroboration simplex from this note alone.
""")
insert_after('docs/90-quarantine/wild-speculations-2026-03-08.md', '## QWS-0229 — Some continuations may eventually need a refresh-distribution court / diffusion senate / spread governor rather than only a compact refresh-scope-distribution witness\n', '')
# append at end if missing
if '## QWS-0230' not in read('docs/90-quarantine/wild-speculations-2026-03-08.md'):
    write('docs/90-quarantine/wild-speculations-2026-03-08.md', read('docs/90-quarantine/wild-speculations-2026-03-08.md').rstrip() + '\n' + QWS_ADD)

# packet contract common spec + helper refactor
insert_after('tools/packet_contract_common.py', '"refresh_scope_distribution_witness_contract": _refresh_family_spec(\n', '')
axis_spec = dedent("""
    "refresh_scope_axis_witness_contract": _refresh_family_spec(
        doc_path="docs/10-method/refresh-scope-axis-witnesses-one-axis-dispersion-cross-axis-corroboration-and-axis-gated-generalization.md",
        doc_needles=[
            "# Refresh-scope-axis witnesses, one-axis dispersion, cross-axis corroboration, and axis-gated generalization",
            "This is the compact successor surface for `OQ-0147`.",
            "## Practice / observation",
            "## External pressure from Alertmanager multi-label grouping, Grafana AND-routed labels, Datadog grouped attributes, Kubernetes multi-dimensional labels and multi-constraint spread, and Google Cloud layered dimensions",
            "## Working synthesis",
            "## One-axis dispersion vs cross-axis corroborated dispersion vs axis-gated generalization vs mixed refresh scope axis",
            "## Countermodels / probes",
            "## Design consequences",
            "## Overflow test",
            "## Transformer-facing implication",
            "`refresh_scope_axis_state`",
            "one-axis-dispersion",
            "cross-axis-corroborated-dispersion",
            "axis-gated-generalization",
            "mixed-refresh-scope-axis",
        ],
        runbook_ref="refresh-scope-axis-witnesses-one-axis-dispersion-cross-axis-corroboration-and-axis-gated-generalization.md",
        prompt_id="PP-0105",
        prompt_needles=["Use `docs/10-method/refresh-scope-axis-witnesses-one-axis-dispersion-cross-axis-corroboration-and-axis-gated-generalization.md`", "one-axis-dispersion, cross-axis-corroborated-dispersion, axis-gated-generalization, or mixed-refresh-scope-axis"],
        claim_id="CL-0145",
        oq_id="OQ-0147",
        resolution_id="RS-0154",
        trajectory_oq_id="OQ-0148",
        qws_id="QWS-0230",
        qws_label="refresh-axis court / axis quorum / corroboration simplex",
        changelog_needles=["refresh-scope-axis-witnesses-one-axis-dispersion-cross-axis-corroboration-and-axis-gated-generalization.md", "check_refresh_scope_axis_witness_contract.py"],
        family="refresh_scope_axis_state",
        allowed=["one-axis-dispersion", "cross-axis-corroborated-dispersion", "axis-gated-generalization", "mixed-refresh-scope-axis"],
        excluded=["one-wide-view-means-two-axes", "duplicate-partitions-count-twice", "same-partition-restated-is-corroboration", "axis-ish"],
    ),
""")
insert_after('tools/packet_contract_common.py', '    excluded=["many-nearby-hits-means-dispersed", "one-group-counts-as-every-family", "same-domain-spread-is-broad-enough", "distribution-ish"],\n),\n', axis_spec)

old_helper_block = dedent("""
def require_named_refresh_scope_family_witness_packet_and_vocabulary(kind: str) -> None:
    require_named_refresh_family_witness_packet_and_vocabulary(kind)


def require_named_refresh_burden_scope_witness_packet_and_vocabulary(kind: str) -> None:
    require_named_refresh_scope_family_witness_packet_and_vocabulary(kind)


def require_named_refresh_scope_basis_witness_packet_and_vocabulary(kind: str) -> None:
    require_named_refresh_scope_family_witness_packet_and_vocabulary(kind)


def require_named_refresh_scope_extent_witness_packet_and_vocabulary(kind: str) -> None:
    require_named_refresh_scope_family_witness_packet_and_vocabulary(kind)


def require_named_refresh_scope_distribution_witness_packet_and_vocabulary(kind: str) -> None:
    require_named_refresh_scope_family_witness_packet_and_vocabulary(kind)
""")
new_helper_block = dedent("""
def require_named_refresh_scope_family_witness_packet_and_vocabulary(kind: str) -> None:
    require_named_refresh_family_witness_packet_and_vocabulary(kind)


def require_named_refresh_scope_packet_and_vocabulary(kind: str) -> None:
    require_named_refresh_scope_family_witness_packet_and_vocabulary(kind)


def require_named_refresh_burden_scope_witness_packet_and_vocabulary(kind: str) -> None:
    require_named_refresh_scope_packet_and_vocabulary(kind)


def require_named_refresh_scope_basis_witness_packet_and_vocabulary(kind: str) -> None:
    require_named_refresh_scope_packet_and_vocabulary(kind)


def require_named_refresh_scope_extent_witness_packet_and_vocabulary(kind: str) -> None:
    require_named_refresh_scope_packet_and_vocabulary(kind)


def require_named_refresh_scope_distribution_witness_packet_and_vocabulary(kind: str) -> None:
    require_named_refresh_scope_packet_and_vocabulary(kind)


def require_named_refresh_scope_axis_witness_packet_and_vocabulary(kind: str) -> None:
    require_named_refresh_scope_packet_and_vocabulary(kind)
""")
replace_once('tools/packet_contract_common.py', old_helper_block, new_helper_block)

# changelog/archive index textual heads
CHANGELOG_HEAD = dedent(f"""## {REV} - {STAMP} - scopeaxis / axisquarantine / {SUMMARY_HIGHLIGHT} / {CODENAME}

- Canon move: resolved `OQ-0147` with `{NEW_DOC}`, adding one compact `{NEW_FAMILY}` witness that keeps one-axis dispersion distinct from cross-axis corroborated dispersion and axis-gated generalization.
- Bold but disciplined speculative move: quarantined the **{NEW_QWS_LABEL}** story in `{NEW_QWS}` rather than quietly promoting a stronger refresh-axis layer into canon.
- Hygiene/meta-engineering improvement: added `{NEW_CHECKER}`, widened `WITNESS-VOCABULARY.json` with a tiny `{NEW_FAMILY}` family, and refactored `tools/packet_contract_common.py` so refresh-scope witness checkers share one explicit helper path instead of adding bespoke alias logic.
- Contract continuity: preserved the existing refresh-scope-distribution, refresh-scope-extent, and refresh-scope-basis chain unchanged while adding the new one-axis-vs-cross-axis card.

""")
prepend('CHANGELOG.md', CHANGELOG_HEAD)

ARCHIVE_ROW = f'| {BUNDLE} | 2026-03-28 | Refresh-scope-axis revision: resolved OQ-0147 with a compact one-axis-vs-cross-axis witness, honestly quarantined stronger refresh-axis governance, and extended shared refresh-scope contract wiring to stay wired and cumulative. |\n'
insert_after('ARCHIVE_INDEX.md', '| --- | --- | --- |\n', ARCHIVE_ROW)

print('apply_rev0252: OK')
