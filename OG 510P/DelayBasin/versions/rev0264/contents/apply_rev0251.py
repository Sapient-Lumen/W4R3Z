from __future__ import annotations

import json
import re
from copy import deepcopy
from pathlib import Path
from textwrap import dedent

ROOT = Path('.')
REV = 'rev0251'
PREV = 'rev0250'
STAMP = '2026.03.28.00.18'
CREATED_AT = '2026-03-28T00:18:00-04:00'
SLUG = 'scopedistribution-diffusionquarantine-clustercarry-weaveglass'
BUNDLE = f'DelayBasin-{REV}-{STAMP}-{SLUG}.zip'
SUMMARY_HIGHLIGHT = 'clustercarry'
CODENAME = 'weaveglass'

NEW_DOC = 'docs/10-method/refresh-scope-distribution-witnesses-clustered-observed-spillover-dispersed-observed-spillover-and-distribution-gated-generalization.md'
NEW_QWS = 'QWS-0229'
NEW_QWS_LABEL = 'refresh-distribution court / diffusion senate / spread governor'
NEW_FAMILY = 'refresh_scope_distribution_state'


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


# --- method doc ---
DOC_TEXT = dedent(f"""
# Refresh-scope-distribution witnesses, clustered observed spillover, dispersed observed spillover, and distribution-gated generalization

This is the compact successor surface for `OQ-0146`.

## Practice / observation

Once DelayBasin can separate **one newly observed widened slice** from **a broader observed spillover pattern**, one more local failure mode remains.

Some observed spillover is still clustered.
Several widened slices are real and directly observed, but they still sit inside one local family: one component group, one team label, one service cluster, one zone, one topology neighborhood, one small children-set under a common parent.
That is broader than a single slice, but it is not yet the same thing as dispersed spread.

Some observed spillover is honestly dispersed.
The widened slices are still directly observed, but they now span multiple named families or failure domains rather than one local cluster.
Different component groups are affected.
Different label groups are affected.
Different teams, services, zones, or topology domains are affected.
That is the point where "spread" becomes the more honest word.

And some cases are still gated.
A few widened families are observed, but not enough to license archive-wide, page-wide, or family-class generalization.
The archive needs one more compact witness before it turns clustered or partial dispersion into diffusion talk.

DelayBasin does not need a refresh-distribution court for that.
It needs one bounded witness that says whether the current observed spillover is still clustered, already dispersed, still distribution-gated from broader generalization, or honestly mixed.

## External pressure from Statuspage component groups, Alertmanager grouping, Grafana grouping and scope routing, Kubernetes topology spread, and Google Cloud failure domains

1. Statuspage lets operators create **component groups**, add components to groups, and reorder the children inside a group. That pressures DelayBasin to distinguish spillover that still sits inside one named component family from spillover that is dispersed across several families. ([`REF-0946`](../00-meta/bibliography.md))

2. Alertmanager groups alerts of similar nature into a single notification, and during larger outages recommends grouping alerts by labels such as `cluster` and `alertname` while still letting operators see exactly which service instances were affected. That pressures DelayBasin to distinguish a clustered observed spillover inside one grouping label from broader spread across multiple groups or clusters. ([`REF-0947`](../00-meta/bibliography.md))

3. Grafana groups alert instances only when they have the same exact label values for the configured `Group by` labels, and its notification policies are explicitly scoped by labels such as team or service. That pressures DelayBasin to keep one grouped local cluster distinct from dispersed observed spillover across several scopes. ([`REF-0948`](../00-meta/bibliography.md))

4. Kubernetes topology spread constraints are about how Pods are spread across failure-domains such as regions, zones, nodes, and other topology domains. That pressures DelayBasin to distinguish a local observed cluster inside one failure domain from spillover dispersed across multiple topology domains. ([`REF-0949`](../00-meta/bibliography.md))

5. Google Cloud says resources should be distributed across multiple zones and regions to tolerate outages, and that zones are designed to minimize correlated failures from physical infrastructure problems. That pressures DelayBasin to distinguish one local correlated cluster from a genuinely dispersed multi-zone or multi-region spread. ([`REF-0950`](../00-meta/bibliography.md))

GPUstorming makes the pressure vivid. An open search can easily yield a small local family of observed matches that *feels* broad because the results arrive in parallel panes. But clustered hits inside one group, one domain, or one topology neighborhood are not yet the same thing as dispersed spread across several widened families.

## Working synthesis

> DelayBasin should preserve one compact **refresh-scope-distribution witness / diffusion card / cluster-spread brake** whenever a current continuity claim depends not only on whether public scope widened, on whether that widened scope is directly observed, and on whether the observed widening is already a broader pattern, but on whether the present observed spillover still clusters inside one named widened family or is honestly dispersed across several widened families. Name the **governed row or surface**, the **stake object / line of concern**, the **prior refresh-scope-extent evidence**, the **current widened-scope evidence**, the **observed clustered-family basis if any**, the **dispersed widened-family evidence if any**, the **distribution gate or uncovered family remainder if any**, the **`refresh_scope_distribution_state`**, and the **fail-closed repair / keep-current vs narrow-claim vs split-scope vs issue-new-refresh-scope-distribution-witness vs quarantine-refresh-distribution-governance consequence**. Keep exact component rosters, label matrices, topology-domain ids, zone names, graph inventories, and long diffusion narratives outside the compact token. Do not let a local observed cluster silently count as dispersed spread.

## Clustered observed spillover vs dispersed observed spillover vs distribution-gated generalization vs mixed refresh scope distribution

Use the controlled family `refresh_scope_distribution_state`:

- **clustered-observed-spillover** says the current observed spillover is real and broader than one slice, but still clustered inside one named widened family, group, or failure domain.
- **dispersed-observed-spillover** says the current observed spillover is directly observed across several named widened families or domains rather than remaining one local cluster.
- **distribution-gated-generalization** says some dispersion is observed, but broader family-wide or archive-wide generalization is still gated by uncovered families or incomplete spread.
- **mixed-refresh-scope-distribution** says the current situation honestly combines clustered and dispersed signals such that no single class stays honest.

So the witness does not create a standing diffusion senate.
It only says how the currently observed widened spillover is distributed.

## Countermodels / probes

1. **Refresh-scope-extent already covers this countermodel**
   - Maybe once one-vs-many slice truth is explicit, a separate distribution witness adds no real value.
   - Probe: compare later rereads that preserve only refresh-scope-extent truth against rereads that also preserve one compact refresh-scope-distribution witness and inspect whether local clusters still get narrated as dispersed spread.

2. **Grouping and topology are only notification conveniences countermodel**
   - Maybe component groups, label groups, and topology domains are too operational to justify a new archive witness.
   - Probe: look for later cases where ordinary continuity prose still slides from one grouped or co-located cluster to family-wide diffusion claims even without explicit observability jargon.

3. **Distribution classes are covert diffusion governance countermodel**
   - Maybe once clustered vs dispersed truth matters, the archive is really sneaking in a full refresh-distribution court.
   - Probe: only reopen stronger machinery if later revisions repeatedly need standing policy for cluster-admissibility, dispersion thresholds, or cross-domain diffusion authority that one bounded witness cannot absorb.

## Design consequences

- DelayBasin can now separate **broader observed spillover that is still clustered** from **broader observed spillover that is honestly dispersed**.
- The archive gets one explicit place to record when spread is still local to one named family, group, or domain.
- Refresh scope extent and refresh scope distribution now separate **how many widened slices are observed** from **how those observed slices are distributed across widened families**.
- Stronger refresh-distribution-governance stories stay quarantined until later overflow instead of sneaking in through diffusion rhetoric.

## Overflow test

Reopen this compact witness only if later revisions repeatedly need standing governance over cluster admissibility, dispersion thresholds, cross-domain spread authority, or diffusion policy that one bounded refresh-scope-distribution witness cannot honestly absorb.

## Transformer-facing implication

A later pass should not treat broader observed spillover as if it were already dispersed spread merely because several observed slices exist. Preserve the exact clustered-family basis if any, the dispersed-family evidence if any, the uncovered remainder if any, and the exact `refresh_scope_distribution_state` before claiming that the widening is already family-diffuse or archive-diffuse.
""").strip() + "\n"
write(NEW_DOC, DOC_TEXT)

# --- bibliography additions ---
BIB_ADD = dedent("""

- `REF-0946` — Atlassian Support, **Create a component group** (accessed 2026-03-28)
  - URL: https://support.atlassian.com/statuspage/docs/create-a-component-group/
  - Load-bearing use: component groups collect child components under one named family, which pressures DelayBasin to distinguish spillover still clustered inside one group from spillover dispersed across several groups.

- `REF-0947` — Prometheus Documentation, **Alertmanager** (accessed 2026-03-28)
  - URL: https://prometheus.io/docs/alerting/latest/alertmanager/
  - Load-bearing use: Alertmanager groups alerts by labels such as cluster and alertname during larger outages while still exposing exactly which instances were affected, which pressures DelayBasin to distinguish clustered observed spillover from broader dispersed spread.

- `REF-0948` — Grafana Documentation, **Group alert notifications** and **Introduction to Grafana Alerting** (accessed 2026-03-28)
  - URL: https://grafana.com/docs/grafana/latest/alerting/fundamentals/notifications/group-alert-notifications/
  - URL: https://grafana.com/docs/grafana/latest/alerting/fundamentals/
  - Load-bearing use: alert instances group only when the configured label values exactly match, and notification policies are scoped by labels such as team or service, which pressures DelayBasin to distinguish one grouped cluster from dispersed spillover across several scopes.

- `REF-0949` — Kubernetes Documentation, **Pod Topology Spread Constraints** (accessed 2026-03-28)
  - URL: https://kubernetes.io/docs/concepts/scheduling-eviction/topology-spread-constraints/
  - Load-bearing use: topology spread explicitly reasons about distribution across failure-domains such as regions, zones, nodes, and user-defined domains, which pressures DelayBasin to distinguish local clustered spillover from dispersed multi-domain spread.

- `REF-0950` — Google Cloud Documentation, **Regions and zones** (accessed 2026-03-28)
  - URL: https://docs.cloud.google.com/compute/docs/regions-zones
  - Load-bearing use: resources are distributed across multiple zones and regions to tolerate outages, and zones are designed to minimize correlated failures, which pressures DelayBasin to distinguish one local correlated cluster from dispersed multi-zone or multi-region spread.
""")
if '`REF-0946`' not in read('docs/00-meta/bibliography.md'):
    write('docs/00-meta/bibliography.md', read('docs/00-meta/bibliography.md').rstrip() + BIB_ADD + '\n')

# --- docs indexes and registries ---
insert_after(
    'docs/README.md',
    "- [`10-method/refresh-scope-extent-witnesses-single-observed-slice-patterned-observed-spillover-and-extent-gated-generalization.md`](10-method/refresh-scope-extent-witnesses-single-observed-slice-patterned-observed-spillover-and-extent-gated-generalization.md)\n",
    f"- [`10-method/{Path(NEW_DOC).name}`](10-method/{Path(NEW_DOC).name})\n",
)

insert_after(
    'docs/20-constitution/claim-registry.md',
    "- `CL-0143` — Archive continuity may improve when DelayBasin preserves one compact **refresh-scope-extent witness / spillover-pattern card / slice-count brake** whenever a current continuity claim depends not only on whether public scope widened and on whether that widened scope is directly observed, but on whether the present direct widening is still only one newly observed slice or already a broader observed spillover pattern: name the **governed row or surface**, the **stake object / line of concern**, the **prior refresh-scope-basis evidence**, the **current widened-scope evidence**, the **observed widened slice or slice family**, the **broader observed spillover-pattern evidence if any**, the **extent gate or unobserved remainder if any**, the **refresh_scope_extent_state**, and the **fail-closed repair** rather than letting one newly affected slice silently count as a broader observed spillover pattern.\n  - Status: speculative but central\n  - Wired docs: `docs/10-method/refresh-scope-extent-witnesses-single-observed-slice-patterned-observed-spillover-and-extent-gated-generalization.md`, `docs/20-constitution/open-question-registry.md`, `docs/20-constitution/prompt-pair-registry.md`, `docs/50-promptcraft/prompt-pairs.md`, `docs/00-meta/llm-runbook.md`, `WITNESS-VOCABULARY.json`, `REVISION-RECEIPT.json`\n",
    "\n- `CL-0144` — Archive continuity may improve when DelayBasin preserves one compact **refresh-scope-distribution witness / diffusion card / cluster-spread brake** whenever a current continuity claim depends not only on whether public scope widened, on whether that widened scope is directly observed, and on whether the observed widening already forms a broader pattern, but on whether the present observed spillover still clusters inside one named widened family or is honestly dispersed across several widened families: name the **governed row or surface**, the **stake object / line of concern**, the **prior refresh-scope-extent evidence**, the **current widened-scope evidence**, the **observed clustered-family basis if any**, the **dispersed widened-family evidence if any**, the **distribution gate or uncovered family remainder if any**, the **refresh_scope_distribution_state**, and the **fail-closed repair** rather than letting a local observed cluster silently count as dispersed spread.\n  - Status: speculative but central\n  - Wired docs: `docs/10-method/refresh-scope-distribution-witnesses-clustered-observed-spillover-dispersed-observed-spillover-and-distribution-gated-generalization.md`, `docs/20-constitution/open-question-registry.md`, `docs/20-constitution/prompt-pair-registry.md`, `docs/50-promptcraft/prompt-pairs.md`, `docs/00-meta/llm-runbook.md`, `WITNESS-VOCABULARY.json`, `REVISION-RECEIPT.json`\n",
)

replace_once(
    'docs/20-constitution/open-question-registry.md',
    "- `OQ-0146` — what minimal refresh-scope-distribution witness distinguishes clustered observed spillover from dispersed observed spillover across widened families?\n  - Why it matters: if DelayBasin cannot separate a local observed cluster from a dispersed observed spread, later sessions may narrate archive-wide or family-wide diffusion from a still-local widening pattern.\n  - Current posture: unresolved\n",
    "- `OQ-0146` — what minimal refresh-scope-distribution witness distinguishes clustered observed spillover from dispersed observed spillover across widened families?\n  - Why it matters: if DelayBasin cannot separate a local observed cluster from a dispersed observed spread, later sessions may narrate archive-wide or family-wide diffusion from a still-local widening pattern.\n  - Current posture: resolved by `RS-0153` via `docs/10-method/refresh-scope-distribution-witnesses-clustered-observed-spillover-dispersed-observed-spillover-and-distribution-gated-generalization.md`; reopen only if the compact refresh-scope-distribution witness proves insufficient and stronger refresh-distribution governance is honestly required\n\n- `OQ-0147` — what minimal refresh-scope-axis witness distinguishes dispersed spread across one named family axis from dispersed spread corroborated across independent family axes?\n  - Why it matters: if DelayBasin cannot separate one-axis dispersion from cross-axis corroborated dispersion, later sessions may narrate archive-wide diffusion from a still single-partition view.\n  - Current posture: unresolved\n",
)

replace_once(
    'docs/00-meta/trajectory-map.md',
    "102. Determine what minimal refresh-scope-distribution witness distinguishes clustered observed spillover from dispersed observed spillover across widened families.\n\nA fresh extension is that once observed widening extent is explicit, DelayBasin may next need to say whether the observed spillover remains a local cluster or is honestly dispersed across multiple widened families. Otherwise several nearby directly affected slices may silently become archive-wide or family-wide diffusion talk.\n- `OQ-0146` — what minimal refresh-scope-distribution witness distinguishes clustered observed spillover from dispersed observed spillover across widened families?\n  - Why it matters: if DelayBasin cannot separate a local observed cluster from a dispersed observed spread, later sessions may narrate archive-wide or family-wide diffusion from a still-local widening pattern.\n  - Current posture: unresolved\n",
    "102. Determine what minimal refresh-scope-distribution witness distinguishes clustered observed spillover from dispersed observed spillover across widened families.\n\nA fresh extension is that once observed widening extent is explicit, DelayBasin may next need to say whether the observed spillover remains a local cluster or is honestly dispersed across multiple widened families. Otherwise several nearby directly affected slices may silently become archive-wide or family-wide diffusion talk.\n- `OQ-0146` — what minimal refresh-scope-distribution witness distinguishes clustered observed spillover from dispersed observed spillover across widened families?\n  - Why it matters: if DelayBasin cannot separate a local observed cluster from a dispersed observed spread, later sessions may narrate archive-wide or family-wide diffusion from a still-local widening pattern.\n  - Current posture: resolved by `RS-0153` via `docs/10-method/refresh-scope-distribution-witnesses-clustered-observed-spillover-dispersed-observed-spillover-and-distribution-gated-generalization.md`; reopen only if the compact refresh-scope-distribution witness proves insufficient and stronger refresh-distribution governance is honestly required\n\n103. Determine what minimal refresh-scope-axis witness distinguishes dispersed spread across one named family axis from dispersed spread corroborated across independent family axes.\n\nA fresh extension is that once clustered-vs-dispersed truth is explicit, DelayBasin may next need to say whether the dispersion still lives inside one grouping axis or is corroborated across independent family axes. Otherwise one partition view may silently become archive-wide diffusion talk.\n- `OQ-0147` — what minimal refresh-scope-axis witness distinguishes dispersed spread across one named family axis from dispersed spread corroborated across independent family axes?\n  - Why it matters: if DelayBasin cannot separate one-axis dispersion from cross-axis corroborated dispersion, later sessions may narrate archive-wide diffusion from a still single-partition view.\n  - Current posture: unresolved\n",
)

insert_after(
    'docs/00-meta/llm-runbook.md',
    "Use `docs/10-method/refresh-scope-extent-witnesses-single-observed-slice-patterned-observed-spillover-and-extent-gated-generalization.md` when the live question is whether directly observed widened scope is still only one newly affected slice or already a broader observed spillover pattern.\n",
    "\nUse `docs/10-method/refresh-scope-distribution-witnesses-clustered-observed-spillover-dispersed-observed-spillover-and-distribution-gated-generalization.md` when the live question is whether broader directly observed spillover still clusters inside one named widened family or is honestly dispersed across several widened families.\n",
)

insert_after(
    'docs/20-constitution/prompt-pair-registry.md',
    "- `PP-0103` — Name whether widened impact is still one observed slice or already a broader observed spillover pattern\n  - Goal: keep one newly affected component, label-set instance, or widened slice from silently inheriting broader observed spillover by requiring explicit observed-slice evidence, any broader observed pattern evidence, any extent gate or unobserved remainder, `refresh_scope_extent_state`, and fail-closed repair before later passes call the widening broadly observed.\n  - Canonical text: `docs/50-promptcraft/prompt-pairs.md#pp-0103--name-whether-widened-impact-is-still-one-observed-slice-or-already-a-broader-observed-spillover-pattern`\n",
    "\n- `PP-0104` — Name whether observed spillover is still clustered or already dispersed across widened families\n  - Goal: keep a local observed family cluster from silently inheriting dispersed diffusion by requiring explicit clustered-family evidence, any dispersed-family evidence, any uncovered remainder or distribution gate, `refresh_scope_distribution_state`, and fail-closed repair before later passes call the spread family-diffuse.\n  - Canonical text: `docs/50-promptcraft/prompt-pairs.md#pp-0104--name-whether-observed-spillover-is-still-clustered-or-already-dispersed-across-widened-families`\n",
)

PROMPT_ADDITION = dedent("""

Use `docs/10-method/refresh-scope-distribution-witnesses-clustered-observed-spillover-dispersed-observed-spillover-and-distribution-gated-generalization.md` when the live question is whether broader directly observed spillover still clusters inside one named widened family or is honestly dispersed across several widened families.

## `PP-0104` — Name whether observed spillover is still clustered or already dispersed across widened families

**Opening prompt**

```text
Read the latest DelayBasin archive and inspect whether the current revision should also materialize one compact refresh-scope-distribution witness for honest clustered-vs-dispersed spillover comparison.

Focus only on whether the broader directly observed spillover still clusters inside one named widened family, is already dispersed across several widened families, is still distribution-gated from broader generalization, or is honestly mixed.

If yes, preserve exactly one small witness that:
- names the governed row or surface,
- names the stake object / line of concern,
- names the prior refresh-scope-extent evidence,
- names the current widened-scope evidence,
- names the observed clustered-family basis if any,
- names the dispersed widened-family evidence if any,
- names the distribution gate or uncovered family remainder if any,
- names the `refresh_scope_distribution_state` / whether this is clustered-observed-spillover, dispersed-observed-spillover, distribution-gated-generalization, or mixed-refresh-scope-distribution,
- states what stronger surfaces still outrank the witness,
- and states the fail-closed repair / keep-current vs narrow-claim vs split-scope vs issue-new-refresh-scope-distribution-witness vs quarantine-refresh-distribution-governance consequence if the present continuity claim is really only a clustered observed spillover rather than dispersed spread.

Do not use refresh scope distribution as a general diffusion court. Use this prompt pair only where broadened observed spillover is already real and the missing question is whether the spillover still clusters inside one named family or is honestly dispersed across several widened families.
```

**Continuation prompt**

```text
Continue the refresh-scope-distribution pass with one high-leverage cluster-vs-dispersion clarification only. Prefer the smallest witness that says what governed row is still being justified, what stake object is supposedly widened, what prior refresh-scope-extent evidence exists, what current widened-scope evidence exists, what observed clustered-family basis if any now exists, what dispersed widened-family evidence if any now exists, what distribution gate or uncovered family remainder if any still remains, what `refresh_scope_distribution_state` is honest, what stronger surfaces still outrank the witness, and what keep-current, narrow-claim, split-scope, issue-new-refresh-scope-distribution-witness, quarantine, or recover-resync consequence follows if the current claim is really clustered-observed-spillover, dispersed-observed-spillover, distribution-gated-generalization, or mixed-refresh-scope-distribution. Run `make lint` and package the release.
```
""")
insert_after(
    'docs/50-promptcraft/prompt-pairs.md',
    "Continue the refresh-scope-extent pass with one high-leverage spillover-pattern clarification only. Prefer the smallest witness that says what governed row is still being justified, what stake object is supposedly widened, what prior refresh-scope-basis evidence exists, what current widened-scope evidence exists, what observed widened slice or slice family now exists, what broader observed spillover-pattern evidence if any now exists, what extent gate or unobserved remainder if any still remains, what `refresh_scope_extent_state` is honest, what stronger surfaces still outrank the witness, and what keep-current, narrow-claim, split-scope, issue-new-refresh-scope-extent-witness, quarantine, or recover-resync consequence follows if the current claim is really single-observed-slice, patterned-observed-spillover, extent-gated-generalization, or mixed-refresh-scope-extent. Run `make lint` and package the release.\n```\n",
    PROMPT_ADDITION,
)

# --- quarantine ---
quarantine_add = dedent(f"""

## {NEW_QWS} — Some continuations may eventually need a refresh-distribution court / diffusion senate / spread governor rather than only a compact refresh-scope-distribution witness

### Claim

A bolder possibility is that DelayBasin may eventually need not only a compact witness for whether broader observed spillover still clusters inside one named family or is already dispersed across several widened families, but also a governed public rule for what counts as admissible spread, when crossing family or topology boundaries becomes public diffusion, and which uncovered remainders still block generalization. Statuspage component groups, Alertmanager grouping by cluster and alertname, Grafana grouping by exact label values and scoped notification policies, Kubernetes topology spread, and Google Cloud failure-domain guidance all suggest a stronger distribution-governance story: perhaps some future archive lines should not only be classified as `clustered-observed-spillover`, `dispersed-observed-spillover`, `distribution-gated-generalization`, or `mixed-refresh-scope-distribution`, but admitted through a small cluster-spread brake, diffusion gate, or spread governor. ([`REF-0946`](../00-meta/bibliography.md), [`REF-0947`](../00-meta/bibliography.md), [`REF-0948`](../00-meta/bibliography.md), [`REF-0949`](../00-meta/bibliography.md), [`REF-0950`](../00-meta/bibliography.md))

The narrower speculative move is only this: a future bounded surface *might* need to say not just how spillover is currently distributed, but what minimum cross-family spread or cross-domain coverage is even admissible as dispersed public diffusion.

### What follows if true

- some future continuity cards may need explicit cluster-admissibility or diffusion-gating rules rather than one static refresh-scope-distribution label;
- DelayBasin may eventually need a compact spread governor that stays smaller than a general diffusion court;
- obligation, queue, and followthrough surfaces might need to say not only that observed spillover is broader than one slice, but whether it is still one local family cluster or broad enough to count as dispersed spread.

### What would count against it

- repeated later passes show that one compact refresh-scope-distribution witness keeps clustered-vs-dispersed truth honest without standing distribution governance;
- apparent diffusion turns out to be better handled by narrow clustered claims and explicit uncovered-remainder naming rather than a new governor;
- the family, group, cluster, and topology analogies do not survive contact with actual archive carry cases.

### Why it stays quarantined

The tempting overreach would be to declare that DelayBasin now needs a public refresh-distribution court, diffusion senate, or spread governor. DelayBasin has not earned that. This note is bold enough to keep in quarantine but not yet honest enough for canon. Do not promote a refresh-distribution court, diffusion senate, or spread governor from this note alone.
""")
if NEW_QWS not in read('docs/90-quarantine/wild-speculations-2026-03-08.md'):
    write('docs/90-quarantine/wild-speculations-2026-03-08.md', read('docs/90-quarantine/wild-speculations-2026-03-08.md').rstrip() + '\n' + quarantine_add.strip() + '\n')

# --- packet contract common + checker ---
pc_path = ROOT / 'tools' / 'packet_contract_common.py'
pc = pc_path.read_text(encoding='utf-8')
if 'refresh_scope_distribution_witness_contract' not in pc:
    insert_anchor = '    "refresh_scope_extent_witness_contract": _refresh_family_spec(\n'
    spec = dedent('''
    "refresh_scope_distribution_witness_contract": _refresh_family_spec(
        doc_path="docs/10-method/refresh-scope-distribution-witnesses-clustered-observed-spillover-dispersed-observed-spillover-and-distribution-gated-generalization.md",
        doc_needles=[
            "# Refresh-scope-distribution witnesses, clustered observed spillover, dispersed observed spillover, and distribution-gated generalization",
            "This is the compact successor surface for `OQ-0146`.",
            "## Practice / observation",
            "## External pressure from Statuspage component groups, Alertmanager grouping, Grafana grouping and scope routing, Kubernetes topology spread, and Google Cloud failure domains",
            "## Working synthesis",
            "## Clustered observed spillover vs dispersed observed spillover vs distribution-gated generalization vs mixed refresh scope distribution",
            "## Countermodels / probes",
            "## Design consequences",
            "## Overflow test",
            "## Transformer-facing implication",
            "`refresh_scope_distribution_state`",
            "clustered-observed-spillover",
            "dispersed-observed-spillover",
            "distribution-gated-generalization",
            "mixed-refresh-scope-distribution",
        ],
        runbook_ref="refresh-scope-distribution-witnesses-clustered-observed-spillover-dispersed-observed-spillover-and-distribution-gated-generalization.md",
        prompt_id="PP-0104",
        prompt_needles=["Use `docs/10-method/refresh-scope-distribution-witnesses-clustered-observed-spillover-dispersed-observed-spillover-and-distribution-gated-generalization.md`", "clustered-observed-spillover, dispersed-observed-spillover, distribution-gated-generalization, or mixed-refresh-scope-distribution"],
        claim_id="CL-0144",
        oq_id="OQ-0146",
        resolution_id="RS-0153",
        trajectory_oq_id="OQ-0147",
        qws_id="QWS-0229",
        qws_label="refresh-distribution court / diffusion senate / spread governor",
        changelog_needles=["refresh-scope-distribution-witnesses-clustered-observed-spillover-dispersed-observed-spillover-and-distribution-gated-generalization.md", "check_refresh_scope_distribution_witness_contract.py"],
        family="refresh_scope_distribution_state",
        allowed=["clustered-observed-spillover", "dispersed-observed-spillover", "distribution-gated-generalization", "mixed-refresh-scope-distribution"],
        excluded=["many-nearby-hits-means-dispersed", "one-group-counts-as-every-family", "same-domain-spread-is-broad-enough", "distribution-ish"],
    ),
''')
    pc = pc.replace(insert_anchor, spec + insert_anchor, 1)

if 'def require_named_refresh_scope_family_witness_packet_and_vocabulary' not in pc:
    old = dedent('''

def require_named_refresh_burden_scope_witness_packet_and_vocabulary(kind: str) -> None:
    require_named_refresh_family_witness_packet_and_vocabulary(kind)


def require_named_refresh_scope_basis_witness_packet_and_vocabulary(kind: str) -> None:
    require_named_refresh_family_witness_packet_and_vocabulary(kind)


def require_named_refresh_scope_extent_witness_packet_and_vocabulary(kind: str) -> None:
    require_named_refresh_family_witness_packet_and_vocabulary(kind)
''')
    new = dedent('''

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
''')
    if old not in pc:
        raise SystemExit('expected refresh scope wrapper block not found')
    pc = pc.replace(old, new, 1)

pc_path.write_text(pc, encoding='utf-8')

checker_path = ROOT / 'tools' / 'check_refresh_scope_distribution_witness_contract.py'
checker_path.write_text(dedent('''
from packet_contract_common import require_named_refresh_scope_distribution_witness_packet_and_vocabulary

require_named_refresh_scope_distribution_witness_packet_and_vocabulary("refresh_scope_distribution_witness_contract")

print("check_refresh_scope_distribution_witness_contract: OK")
''').lstrip(), encoding='utf-8')

# --- changelog and archive index ---
CHANGELOG_ENTRY = dedent(f"""## {REV} - {STAMP} - scopedistribution / diffusionquarantine / clustercarry / {CODENAME}

- Canon move: resolved `OQ-0146` with `{NEW_DOC}`, adding one compact `{NEW_FAMILY}` witness that keeps clustered observed spillover distinct from dispersed observed spillover and distribution-gated generalization.
- Bold but disciplined speculative move: quarantined the **refresh-distribution court / diffusion senate / spread governor** story in `{NEW_QWS}` rather than quietly promoting a stronger refresh-distribution layer into canon.
- Hygiene/meta-engineering improvement: added `tools/check_refresh_scope_distribution_witness_contract.py`, widened `WITNESS-VOCABULARY.json` with a tiny `{NEW_FAMILY}` family, and refactored `tools/packet_contract_common.py` so refresh-scope-family validator entrypoints share one helper path instead of repeated wrappers.
- Contract continuity: preserved the existing refresh-scope-extent, refresh-scope-basis, and scope-widening chain unchanged while adding the new cluster-vs-spread card.

""")
if not read('CHANGELOG.md').startswith(f'## {REV}'):
    write('CHANGELOG.md', CHANGELOG_ENTRY + read('CHANGELOG.md'))

ARCHIVE_ROW = f"| {BUNDLE} | 2026-03-28 | Refresh-scope-distribution revision: resolved OQ-0146 with a compact clustered-vs-dispersed witness, honestly quarantined stronger refresh-distribution governance, and refactored refresh-scope-family validator entrypoints to stay wired and cumulative. |\n"
insert_after('ARCHIVE_INDEX.md', '| Bundle | Date | Notes |\n| --- | --- | --- |\n', ARCHIVE_ROW)

# --- JSON ledgers ---
def append_item(path: str, item: dict) -> None:
    obj = json.loads(read(path))
    if any(existing.get('id') == item.get('id') for existing in obj['items']):
        obj['revision'] = REV
        write_json(path, obj)
        return
    obj['items'].append(item)
    obj['revision'] = REV
    write_json(path, obj)

append_item('FOLLOWTHROUGH-QUEUE.json', {
    'id': 'FT-0153',
    'title': 'keep checking whether refresh-scope-distribution pressure still fits inside one compact successor surface',
    'state': 'queued',
    'blocked_object': 'standing refresh-distribution court, diffusion senate, or spread governor',
    'local_surface': f'docs/90-quarantine/wild-speculations-2026-03-08.md#{NEW_QWS}',
    'followthrough_state': 'queued',
    'boundary': 'do not promote bounded refresh-scope-distribution clarification into general refresh-distribution-governance machinery',
    'next_proof_surface': NEW_DOC,
    'receiving_surface': 'FOLLOWTHROUGH-QUEUE.json#FT-0153',
    'repair': 'ordinary-continuation',
    'origin_revision': REV,
    'discharge': 'revisit-on-next-real-refresh-scope-distribution-overflow',
    'action_lane': 'keep-compact',
    'gate_class': 'overflow',
    'blocked_output': 'standing refresh-distribution court, diffusion senate, or spread governor',
    'owner_surface': 'OBLIGATION-LEDGER.json#OB-0146',
    'revision': REV,
    'missing_support': 'a later public check on whether one compact refresh-scope-distribution witness keeps overflowing the bounded rule and honestly warrants richer refresh-distribution governance',
    'candidate_surface': f'docs/90-quarantine/wild-speculations-2026-03-08.md#{NEW_QWS}',
    'blocked_by': 'need repeated evidence that clustered-observed-spillover vs dispersed-observed-spillover vs distribution-gated-generalization truth overflows one compact witness',
})

append_item('ASSUMPTION-LEDGER.json', {
    'id': 'AS-0150',
    'title': 'one compact refresh-scope-distribution witness is enough for now',
    'state': 'active',
    'scope': 'continuity passes whose widened public claim depends on whether broader directly observed spillover still clusters inside one named family or is honestly dispersed across several widened families',
    'invalidation_triggers': [
        'repeated later revisions need standing refresh-distribution governance rather than one compact refresh-scope-distribution witness',
        'the archive needs a refresh-distribution court or spread governor just to keep clustered-observed-spillover distinct from dispersed-observed-spillover or distribution-gated-generalization',
        'scope-distribution cases repeatedly fail to stay distinguishable even with the witness in place',
    ],
    'assumption_state': 'active',
    'repair': 'ordinary-continuation',
    'origin_revision': REV,
    'revision': REV,
    'assumption': 'the current evidence only requires one compact refresh-scope-distribution witness over the existing refresh-scope-extent, grouping, topology-domain, and failure-domain surfaces rather than a refresh-distribution court, diffusion senate, or spread governor',
    'supporting_surfaces': [
        'APPLICABILITY-LEDGER.json#AP-0145',
        'DATACUBE-TRANSFER-LEDGER.json#TL-0156',
        'FOREIGN-PRESSURE-LEDGER.json#FP-0150',
    ],
    'discharge': 'discharge when later revisions can keep clustered-vs-dispersed truth honest without a dedicated refresh-scope-distribution witness, or retire/quarantine it if broader refresh-distribution governance becomes repeatedly necessary',
    'witness_surface': 'ASSUMPTION-LEDGER.json#AS-0150',
    'assumption_surface': 'ASSUMPTION-LEDGER.json#AS-0150',
    'assumption_statement': 'the current evidence only requires one compact refresh-scope-distribution witness over the existing refresh-scope-extent, grouping, topology-domain, and failure-domain surfaces rather than a refresh-distribution court, diffusion senate, or spread governor',
    'action_lane': 'keep-compact',
    'gate_class': 'concrete-evidence',
})

append_item('OBLIGATION-LEDGER.json', {
    'id': 'OB-0146',
    'title': 'when broader observed spillover keeps needing one local cluster distinguished from dispersed spread, DelayBasin should preserve one compact refresh-scope-distribution witness rather than a diffusion court',
    'state': 'open',
    'witness_surface': 'OBLIGATION-LEDGER.json#OB-0146',
    'target_surfaces': [f'docs/90-quarantine/wild-speculations-2026-03-08.md#{NEW_QWS}'],
    'missing_support': 'a later public check on whether one compact refresh-scope-distribution witness keeps sufficing and whether clustered observed spillover, dispersed observed spillover, and distribution-gated generalization stay distinct without broader refresh-distribution governance',
    'current_support': [
        'APPLICABILITY-LEDGER.json#AP-0145',
        'FOREIGN-PRESSURE-LEDGER.json#FP-0150',
        'DATACUBE-TRANSFER-LEDGER.json#TL-0156',
    ],
    'discharge_path': 'either show later that one compact refresh-scope-distribution witness keeps sufficing or promote broader refresh-distribution governance explicitly',
    'obligation_state': 'open',
    'repair': 'ordinary-continuation',
    'origin_revision': REV,
    'discharge': 'reopen-only-if-refresh-scope-distribution-overflows',
    'action_lane': 'keep-compact',
    'gate_class': 'overflow',
    'revision': REV,
})

append_item('APPLICABILITY-LEDGER.json', {
    'id': 'AP-0145',
    'title': 'the refresh-scope-distribution witness stays smaller than a diffusion court',
    'state': 'gated',
    'question': 'when should DelayBasin treat broader directly observed spillover as one compact refresh-scope-distribution witness instead of promoting broader refresh-distribution governance?',
    'applies_when': [
        'a revision already has a durable row whose current claim depends on directly observed widened scope and on whether broader observed spillover still clusters or is dispersed',
        'later passes still need to distinguish clustered-observed-spillover, dispersed-observed-spillover, distribution-gated-generalization, or mixed-refresh-scope-distribution posture',
        'one compact successor surface plus the existing admitted refresh-scope-extent, grouping, topology-domain, and failure-domain surfaces still keeps refresh-scope-distribution truth honest without standing spread policy',
    ],
    'does_not_apply_when': [
        'the archive honestly requires standing governance over cluster admissibility, dispersion thresholds, or cross-domain spread policy',
        'the questioned surface is not really about whether broader directly observed spillover still clusters or is already dispersed',
    ],
    'budget': 'one compact refresh-scope-distribution witness plus one resolution of OQ-0146; no refresh-distribution court',
    'negative_transfer_budget': 'do not treat several nearby widened slices inside one named family or failure domain as dispersed spread without explicit cross-family evidence',
    'origin_revision': REV,
    'discharge': 'reopen-only-if-refresh-scope-distribution-overflows',
    'action_lane': 'keep-compact',
    'gate_class': 'concrete-evidence',
    'witness_surface': 'APPLICABILITY-LEDGER.json#AP-0145',
    'applicability_state': 'gated',
    'repair': 'ordinary-continuation',
    'matched_budget': 'one compact witness foregrounding clustered vs dispersed observed spillover without widening into broader refresh-distribution governance',
    'revision': REV,
    'target_objective': 'keep widened-scope-distribution comparison honest without inflating a broader refresh-distribution layer',
    'carry_object': 'refresh-scope-distribution witness / diffusion card / cluster-spread brake',
    'applicability_conditions': [
        'broader observed spillover remains distinguishable by named families, groups, or failure domains',
        'some apparent diffusion is still only a local observed cluster and needs another step before public overclaim',
        'refresh scope distribution remains subordinate to existing refresh-scope-extent, refresh-scope-basis, and scope-widening witnesses rather than a new diffusion controller',
    ],
    'baselines': [
        'existing refresh-scope-extent-witness baseline',
        'existing grouping and topology-domain baseline',
        'existing obligation/overflow baseline',
        'existing witness-vocabulary baseline',
    ],
    'non_fit_slice': 'Do not generalize this revision into a refresh-distribution court, diffusion senate, or spread governor without later overflow evidence.',
})

append_item('FOREIGN-PRESSURE-LEDGER.json', {
    'id': 'FP-0150',
    'title': 'refresh-scope-distribution pressure pushes DelayBasin to extract one compact cluster-vs-spread witness rather than a diffusion court',
    'state': 'imported',
    'source_packets': [
        {
            'datacube': 'StatuspageComponentGroups-2026',
            'surfaces': ['REF-0946'],
            'pressure': 'grouped child components make one local named family visible, which pressures DelayBasin to distinguish clustered spillover inside one group from dispersed spillover across several groups',
        },
        {
            'datacube': 'AlertmanagerClusterGrouping-2026',
            'surfaces': ['REF-0947'],
            'pressure': 'alerts grouped by cluster and alertname can still expose many exact affected instances, which pressures DelayBasin to distinguish a local clustered spillover from broader dispersed spread',
        },
        {
            'datacube': 'GrafanaScopedGrouping-2026',
            'surfaces': ['REF-0948'],
            'pressure': 'exact label grouping and team/service notification scopes pressure DelayBasin to keep one grouped local family distinct from dispersed cross-scope spread',
        },
        {
            'datacube': 'KubernetesTopologySpread-2026',
            'surfaces': ['REF-0949'],
            'pressure': 'spread across topology domains pressures DelayBasin to distinguish one local failure-domain cluster from multi-domain dispersed spillover',
        },
        {
            'datacube': 'GoogleCloudFailureDomains-2026',
            'surfaces': ['REF-0950'],
            'pressure': 'zones and regions minimize correlated failures, which pressures DelayBasin to distinguish one local correlated cluster from genuinely dispersed multi-zone or multi-region spread',
        },
    ],
    'reviewed_pattern': 'clustered observed spillover vs dispersed observed spillover across widened families',
    'import_decision': 'support a compact refresh-scope-distribution witness and resolve OQ-0146',
    'adopted_take': 'DelayBasin should add one compact witness that says whether broader directly observed spillover is clustered-observed-spillover, dispersed-observed-spillover, distribution-gated-generalization, or honestly mixed',
    'supporting_only_take': 'the current evidence cleanly supports a bounded refresh-scope-distribution witness without promoting broader refresh-distribution governance',
    'deferred_or_rejected_take': [
        'refresh-distribution court',
        'diffusion senate',
        'spread governor',
    ],
    'local_gap': 'the archive still lacked one compact successor surface for whether broader directly observed spillover still clustered inside one named family or was already dispersed across several widened families',
    'anchor_surfaces': [
        NEW_DOC,
        'docs/20-constitution/open-question-registry.md',
        'docs/00-meta/trajectory-map.md',
        f'docs/90-quarantine/wild-speculations-2026-03-08.md#{NEW_QWS}',
    ],
    'open_question': 'OQ-0147',
    'repair': 'ordinary-continuation',
    'origin_revision': REV,
    'action_lane': 'keep-compact',
    'gate_class': 'concrete-evidence',
    'discharge': 'reopen-only-if-refresh-scope-distribution-overflows',
    'revision': REV,
    'witness_surface': 'FOREIGN-PRESSURE-LEDGER.json#FP-0150',
    'pressure_state': 'imported',
    'bounded_take': 'Keep the archive compact by extracting one refresh-scope-distribution witness over the existing refresh-scope-extent, grouping, topology-domain, and failure-domain surfaces; do not promote a refresh-distribution court, diffusion senate, or spread governor.',
    'explicit_non_take': [
        'no refresh-distribution court',
        'no diffusion senate',
        'no spread governor',
    ],
    'assimilation_state': 'imported',
})

# transfer ledger has top-level open_questions too
transfer = json.loads(read('DATACUBE-TRANSFER-LEDGER.json'))
if not any(item.get('id') == 'TL-0156' for item in transfer['items']):
    transfer['items'].append({
        'id': 'TL-0156',
        'title': 'refresh-scope-distribution evidence supports resolving OQ-0146 with one compact cluster-vs-spread card rather than a diffusion court',
        'state': 'supporting-only',
        'reviewed_pattern': 'clustered observed spillover vs dispersed observed spillover across widened families',
        'import_decision': 'support a compact refresh-scope-distribution witness and resolve OQ-0146',
        'adopted_take': 'DelayBasin should add one compact witness that says whether broader directly observed spillover is clustered-observed-spillover, dispersed-observed-spillover, distribution-gated-generalization, or honestly mixed',
        'supporting_only_take': 'the current evidence cleanly supports a bounded refresh-scope-distribution witness without promoting broader refresh-distribution governance',
        'deferred_or_rejected_take': ['refresh-distribution court', 'diffusion senate', 'spread governor'],
        'local_gap': 'the archive still lacked one compact successor surface for whether broader directly observed spillover still clustered inside one named family or was already dispersed across several widened families',
        'anchor_surfaces': [
            'docs/10-method/refresh-scope-extent-witnesses-single-observed-slice-patterned-observed-spillover-and-extent-gated-generalization.md',
            'docs/20-constitution/open-question-registry.md',
            'docs/00-meta/trajectory-map.md',
            f'docs/90-quarantine/wild-speculations-2026-03-08.md#{NEW_QWS}',
        ],
        'open_question': 'OQ-0147',
        'repair': 'ordinary-continuation',
        'origin_revision': REV,
        'action_lane': 'keep-compact',
        'gate_class': 'concrete-evidence',
        'discharge': 'reopen-only-if-refresh-scope-distribution-overflows',
        'revision': REV,
        'witness_surface': 'DATACUBE-TRANSFER-LEDGER.json#TL-0156',
        'transfer_state': 'supporting-only',
        'bounded_take': 'Keep the archive compact by extracting one refresh-scope-distribution witness over the existing refresh-scope-extent, grouping, topology-domain, and failure-domain surfaces; do not promote a refresh-distribution court, diffusion senate, or spread governor.',
        'explicit_non_take': ['no refresh-distribution court', 'no diffusion senate', 'no spread governor'],
        'open_transfer_question': 'whether later passes should add a separate refresh-scope-axis witness once refresh scope distribution is explicit',
        'missing_support': 'a later public check on whether one compact refresh-scope-distribution witness keeps sufficing',
        'current_support': [
            'APPLICABILITY-LEDGER.json#AP-0145',
            'FOREIGN-PRESSURE-LEDGER.json#FP-0150',
            'DATACUBE-TRANSFER-LEDGER.json#TL-0156',
        ],
        'discharge_path': 'either show later that one compact refresh-scope-distribution witness keeps sufficing or promote broader refresh-distribution governance explicitly',
        'reviewed_datacubes': [
            {
                'datacube': 'StatuspageComponentGroups-2026',
                'surfaces': ['REF-0946'],
                'pattern': 'child components can remain inside one named component group',
                'pressure': 'DelayBasin should distinguish a local grouped family cluster from broader dispersed spread',
            },
            {
                'datacube': 'AlertmanagerClusterGrouping-2026',
                'surfaces': ['REF-0947'],
                'pattern': 'many exact alerts can still be grouped by cluster and alertname',
                'pressure': 'DelayBasin should distinguish clustered observed spillover from dispersed spread across several groups',
            },
            {
                'datacube': 'GrafanaScopedGrouping-2026',
                'surfaces': ['REF-0948'],
                'pattern': 'grouping depends on exact label matches and distinct team/service scopes',
                'pressure': 'DelayBasin should keep one grouped local family distinct from dispersed cross-scope spread',
            },
            {
                'datacube': 'KubernetesTopologySpread-2026',
                'surfaces': ['REF-0949'],
                'pattern': 'spread is evaluated across named topology domains',
                'pressure': 'DelayBasin should distinguish one local failure-domain cluster from dispersed multi-domain spread',
            },
            {
                'datacube': 'GoogleCloudFailureDomains-2026',
                'surfaces': ['REF-0950'],
                'pattern': 'zones and regions are used to separate correlated failures',
                'pressure': 'DelayBasin should distinguish one local correlated cluster from dispersed multi-zone or multi-region spread',
            },
        ],
    })
# update transfer open_questions if present
if 'open_questions' in transfer and isinstance(transfer['open_questions'], list):
    new_open_question = 'Whether a later pass should add one bounded refresh-scope-axis witness once refresh scope distribution is explicit, but only if one-axis dispersion keeps being mistaken for cross-axis corroborated diffusion in honest continuation work.'
    if new_open_question not in transfer['open_questions']:
        transfer['open_questions'].append(new_open_question)
transfer['revision'] = REV
write_json('DATACUBE-TRANSFER-LEDGER.json', transfer)

append_item('RESOLUTION-LEDGER.json', {
    'id': 'RS-0153',
    'title': 'resolve OQ-0146 with one compact refresh-scope-distribution witness rather than a diffusion governor',
    'state': 'resolved',
    'closure_state': 'resolved',
    'closure_reason': 'rev0251 extracted one compact refresh-scope-distribution witness, kept the admitted refresh-scope-extent and grouping/domain analog surfaces narrow, and kept stronger refresh-distribution-governance stories quarantined.',
    'discharge': 'reopen-only-if-refresh-scope-distribution-overflows',
    'gate_class': 'concrete-evidence',
    'origin_revision': REV,
    'prior_state': 'open gap: DelayBasin already had refresh-scope-extent truth but still lacked one compact successor surface for whether broader directly observed spillover still clustered inside one named family or was already dispersed across several widened families.',
    'question': 'whether one compact refresh-scope-distribution witness over the existing refresh-scope-extent, grouping, topology-domain, and failure-domain surfaces is enough for honest clustered-vs-dispersed comparison',
    'reopen_trigger': 'refresh-scope-distribution pressure overflows one compact successor surface',
    'reopen_triggers': [
        'later revisions need standing governance over cluster admissibility, diffusion thresholds, spread authority, or broader dispersed-spillover policy that one compact refresh-scope-distribution witness cannot honestly absorb',
    ],
    'repair': 'ordinary-continuation',
    'resolved_objects': ['OQ-0146', 'AP-0145', 'FP-0150', 'TL-0156'],
    'revision': REV,
    'successor_surface': NEW_DOC,
    'target_surfaces': [NEW_DOC],
    'action_lane': 'keep-compact',
    'witness_surface': 'RESOLUTION-LEDGER.json#RS-0153',
})

append_item('RETROSPECTIVE-QUEUE.json', {
    'id': 'RT-0140',
    'title': 'revisit whether refresh-scope-distribution pressure stayed bounded after rev0251',
    'state': 'cooling',
    'candidate_surface': f'docs/90-quarantine/wild-speculations-2026-03-08.md#{NEW_QWS}',
    'cooldown_window': 'keep the stronger refresh-distribution court, diffusion senate, or spread governor story cooled until at least one later revision shows that one compact refresh-scope-distribution witness is no longer enough.',
    'adjudication_family': 'refresh scope distribution / cluster-vs-diffusion gating / spread-governance pressure',
    'supersession_link': 'OBLIGATION-LEDGER.json#OB-0146',
    'origin_revision': REV,
    'discharge': 'keep-cooling-unless-refresh-scope-distribution-overflows',
    'action_lane': 'keep-compact',
    'gate_class': 'overflow',
    'witness_surface': 'RETROSPECTIVE-QUEUE.json#RT-0140',
    'revision': REV,
    'cooling_state': 'cooling',
    'disposition': 'await-adjudication',
    'repair': 'keep-cooling',
})

append_item('FIREBREAK-LEDGER.json', {
    'id': 'FB-0147',
    'title': 'the refresh-scope-distribution import should count as one compact cluster-vs-spread repair, not as promotion of a diffusion court',
    'state': 'withheld',
    'witness_surface': 'FIREBREAK-LEDGER.json#FB-0147',
    'judged_property': 'the rev0251 decision that DelayBasin should extract one compact refresh-scope-distribution witness over the existing refresh-scope-extent, grouping, topology-domain, and failure-domain surfaces and `refresh_scope_distribution_state` family while the broader refresh-distribution court / diffusion senate / spread governor story remains quarantined',
    'public_extract': [
        NEW_DOC,
        'docs/10-method/refresh-scope-extent-witnesses-single-observed-slice-patterned-observed-spillover-and-extent-gated-generalization.md',
        'docs/20-constitution/open-question-registry.md',
        'FOREIGN-PRESSURE-LEDGER.json#FP-0150',
        'APPLICABILITY-LEDGER.json#AP-0145',
        'REVISION-RECEIPT.json',
    ],
    'withheld_trace_surface': 'same-session drafting residue behind the compact refresh-scope-distribution-witness versus spread-governor decision',
    'allowed_role': 'bounded drafting aid only; not public support for a broader refresh-distribution court, diffusion senate, or spread governor',
    'exposure_rule': 'expose or reintegrate only if later passes show that one compact refresh-scope-distribution witness cannot keep cluster-vs-dispersed truth bounded',
    'trace_state': 'withheld',
    'repair': 'ordinary-continuation',
    'origin_revision': REV,
    'action_lane': 'keep-compact',
    'gate_class': 'overflow',
    'firebreak_surface': 'FIREBREAK-LEDGER.json#FB-0147',
    'discharge': 'reopen-only-if-refresh-scope-distribution-overflows',
    'revision': REV,
    'blocked_object': 'standing refresh-distribution court, diffusion senate, or spread governor',
})

# --- witness vocabulary ---
vocab = json.loads(read('WITNESS-VOCABULARY.json'))
vocab['revision'] = REV
vocab['families'][NEW_FAMILY] = {
    'allowed': [
        'clustered-observed-spillover',
        'dispersed-observed-spillover',
        'distribution-gated-generalization',
        'mixed-refresh-scope-distribution',
    ],
    'surfaces': [
        'WITNESS-VOCABULARY.json',
        'REVISION-RECEIPT.json',
        NEW_DOC,
    ],
    'excluded_synonyms': [
        'many-nearby-hits-means-dispersed',
        'one-group-counts-as-every-family',
        'same-domain-spread-is-broad-enough',
        'distribution-ish',
    ],
    'comparability_budget': 'refresh-scope-distribution truth is compared by token; the compact refresh-scope-distribution witness says whether broader directly observed spillover is still clustered inside one named widened family, already dispersed across several widened families, still distribution-gated from broader generalization, or honestly mixed, while exact component rosters, label matrices, topology-domain ids, zone names, and long diffusion narratives stay in surrounding prose',
}
write_json('WITNESS-VOCABULARY.json', vocab)

# --- surface status and manifest prepackage ---
status = json.loads(read('SURFACE-STATUS.json'))
status['operational_head']['revision'] = REV
status['status_lanes']['frozen_public_surface'] = BUNDLE
status['status_lanes']['current_release_surface'] = BUNDLE
status['citation_head']['revision'] = REV
status['citation_head']['surface'] = BUNDLE
status['previous_citation_head']['revision'] = PREV
status['previous_citation_head']['surface'] = f'DelayBasin-{PREV}-2026.03.27.23.59-scopeextent-patternquarantine-slicecarry-ridgeglass.zip'
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

# --- revision receipt ---
receipt = json.loads(read('REVISION-RECEIPT.json'))
receipt['revision'] = REV
receipt['previous_revision'] = PREV
receipt['summary'] = 'Resolved OQ-0146 with one compact refresh-scope-distribution witness that separates clustered observed spillover from dispersed observed spillover while keeping stronger refresh-distribution governance quarantined.'
receipt['canon_additions'] = [NEW_DOC, 'RS-0153 resolved OQ-0146 with one compact refresh-scope-distribution witness']
receipt['quarantine_additions'] = [f'{NEW_QWS} — refresh-distribution court / diffusion senate / spread governor']
receipt['refs_used'] = ['REF-0946', 'REF-0947', 'REF-0948', 'REF-0949', 'REF-0950']
receipt['touched_surfaces'] = [
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
    'tools/packet_contract_common.py',
    'tools/check_refresh_scope_distribution_witness_contract.py',
]
receipt['packaged_bundle_filename'] = BUNDLE
receipt['basis_witness'].update({
    'expected_head': PREV,
    'observed_head': PREV,
    'basis_surfaces': [
        'docs/10-method/refresh-scope-extent-witnesses-single-observed-slice-patterned-observed-spillover-and-extent-gated-generalization.md',
        'docs/00-meta/trajectory-map.md',
        'docs/20-constitution/open-question-registry.md',
    ],
    'basis_omission_basis': 'broader refresh-distribution governance drafting was intentionally omitted from canon because the evidence only justified one bounded refresh-scope-distribution witness',
    'basis_of_change': 'rev0250 extends continuity law by distinguishing one newly observed widened slice from a broader observed spillover pattern, which opens the next question of whether broader observed spillover still clusters locally or is honestly dispersed across widened families.',
    'revision_span': f'{PREV} -> {REV}',
})
receipt['scope_witness'].update({
    'exact_target': 'resolve OQ-0146 with one compact refresh-scope-distribution witness and keep stronger refresh-distribution governance honestly quarantined',
    'scope_surfaces': [NEW_DOC, 'docs/20-constitution/open-question-registry.md', 'docs/00-meta/trajectory-map.md', 'docs/90-quarantine/wild-speculations-2026-03-08.md'],
    'ambient_exclusions': ['no refresh-distribution court', 'no diffusion senate', 'no spread governor'],
    'scope_of_change': 'one compact successor witness plus one quarantined speculative move',
})
receipt['status_witness'].update({
    'frozen_public_surface': BUNDLE,
})
receipt['retrospective_write_witness'] = json.loads(read('RETROSPECTIVE-QUEUE.json'))['items'][-1]
receipt['followthrough_witness'] = json.loads(read('FOLLOWTHROUGH-QUEUE.json'))['items'][-1]
receipt['assumption_witness'] = json.loads(read('ASSUMPTION-LEDGER.json'))['items'][-1]
receipt['obligation_witness'] = json.loads(read('OBLIGATION-LEDGER.json'))['items'][-1]
receipt['applicability_witness'] = json.loads(read('APPLICABILITY-LEDGER.json'))['items'][-1]
receipt['foreign_pressure_witness'] = json.loads(read('FOREIGN-PRESSURE-LEDGER.json'))['items'][-1]
receipt['transfer_witness'] = json.loads(read('DATACUBE-TRANSFER-LEDGER.json'))['items'][-1]
receipt['resolution_witness'] = json.loads(read('RESOLUTION-LEDGER.json'))['items'][-1]
receipt['reasoning_firebreak_witness'] = json.loads(read('FIREBREAK-LEDGER.json'))['items'][-1]
receipt['vocabulary_witness'] = {
    'witness_surface': 'WITNESS-VOCABULARY.json',
    'controlled_families': ['action_lane', 'gate_class', NEW_FAMILY],
    'target_surfaces': ['WITNESS-VOCABULARY.json', 'REVISION-RECEIPT.json', NEW_DOC],
    'ambient_synonyms_excluded': ['many-nearby-hits-means-dispersed', 'one-group-counts-as-every-family', 'same-domain-spread-is-broad-enough', 'distribution-ish'],
    'comparability_budget': 'refresh-scope-distribution truth is compared by token; the compact refresh-scope-distribution witness says whether broader directly observed spillover is still clustered inside one named widened family, already dispersed across several widened families, still distribution-gated from broader generalization, or honestly mixed, while exact component rosters, label matrices, topology-domain ids, zone names, and long diffusion narratives stay in surrounding prose',
    'vocabulary_state': 'locked',
    'repair': 'ordinary-continuation',
    NEW_FAMILY: 'clustered-observed-spillover|dispersed-observed-spillover|distribution-gated-generalization|mixed-refresh-scope-distribution',
}
receipt['counterfactual_shadow'] = {
    'status': 'rejected-nearby-move',
    'nearby_rejected_move': 'broader refresh-distribution court / diffusion senate / spread governor',
    'pivot_surface': f'docs/90-quarantine/wild-speculations-2026-03-08.md#{NEW_QWS}',
    'rejection_reason': 'current external pressure supports one compact cluster-vs-spread witness, not standing governance over diffusion or spread admissibility',
    'still_live': f'docs/90-quarantine/wild-speculations-2026-03-08.md#{NEW_QWS}',
}
receipt['summary_highlight'] = SUMMARY_HIGHLIGHT
receipt['codename'] = CODENAME
receipt['created_at'] = CREATED_AT
receipt['comparison_witness'] = {
    'previous_revision': PREV,
    'current_revision': REV,
    'current_pressure_id': 'FP-0150',
    'current_import_id': 'TL-0156',
    'basis_surface': 'docs/10-method/refresh-scope-extent-witnesses-single-observed-slice-patterned-observed-spillover-and-extent-gated-generalization.md',
    'delta_surface': NEW_DOC,
    'comparison_summary': 'rev0251 adds one compact refresh-scope-distribution witness so broader directly observed spillover no longer stands in for dispersed spread when the evidence is still only a local named family cluster.',
}
receipt['changes'] = [
    {
        'kind': 'canon',
        'surface': NEW_DOC,
        'summary': 'added one compact refresh-scope-distribution witness with clustered, dispersed, distribution-gated, and mixed states',
    },
    {
        'kind': 'quarantine',
        'surface': f'docs/90-quarantine/wild-speculations-2026-03-08.md#{NEW_QWS}',
        'summary': 'kept stronger refresh-distribution governance quarantined rather than promoting it into canon',
    },
    {
        'kind': 'hygiene',
        'surface': 'tools/packet_contract_common.py',
        'summary': 'centralized refresh-scope-family validator entrypoints into one helper path',
    },
]
receipt['firebreak_witness'] = json.loads(read('FIREBREAK-LEDGER.json'))['items'][-1]
receipt['receipt_freshness_witness'] = {
    'packaged_bundle_filename': BUNDLE,
    'manifest_timestamp_token': STAMP,
    'receipt_timestamp_token': STAMP,
    'bundle_stem_suffix_relation': 'slug ends with clustercarry + weaveglass and remains aligned to the current summary/codename pair while preserving the diffusionquarantine middle token',
    'current_import_id': 'TL-0156',
    'current_pressure_id': 'FP-0150',
    'change_anchor_surface': 'CHANGELOG.md',
    'freshness_state': 'current-aligned',
    'repair': 'ordinary-continuation',
}
receipt['question_posture_witness'] = {
    'resolution_surface': 'RESOLUTION-LEDGER.json',
    'registry_surface': 'docs/20-constitution/open-question-registry.md',
    'trajectory_surface': 'docs/00-meta/trajectory-map.md',
    'synced_resolved_questions': ['OQ-0146'],
    'frontier_selection_rule': 'resolved OQ-0146 is synchronized across resolution ledger, registry, and trajectory while frontier selection advances to OQ-0147',
    'posture_state': 'resolved-sync-current',
    'repair': 'ordinary-continuation',
}
receipt['current_import_id'] = 'TL-0156'
receipt['current_pressure_id'] = 'FP-0150'
receipt['import_witness'] = deepcopy(receipt['transfer_witness'])
receipt['new_classes_or_families'] = [NEW_FAMILY]
receipt['quarantined_non_take'] = ['refresh-distribution court', 'diffusion senate', 'spread governor']
receipt['artifacts_touched'] = list(receipt['touched_surfaces'])
receipt['refresh_scope_distribution_witness'] = {
    'witness_surface': NEW_DOC,
    'family': NEW_FAMILY,
    'state_tokens': ['clustered-observed-spillover', 'dispersed-observed-spillover', 'distribution-gated-generalization', 'mixed-refresh-scope-distribution'],
    'overflow_rule': 'reopen-only-if-refresh-scope-distribution-overflows',
}
receipt['refresh_scope_distribution_witness_contract'] = {
    'family': NEW_FAMILY,
    'states': ['clustered-observed-spillover', 'dispersed-observed-spillover', 'distribution-gated-generalization', 'mixed-refresh-scope-distribution'],
}
receipt['refresh_scope_distribution_witness_meta'] = {'checker': 'tools/check_refresh_scope_distribution_witness_contract.py'}
write_json('REVISION-RECEIPT.json', receipt)

# touch remaining top-level revision fields
for path in [
    'FOLLOWTHROUGH-QUEUE.json',
    'ASSUMPTION-LEDGER.json',
    'OBLIGATION-LEDGER.json',
    'APPLICABILITY-LEDGER.json',
    'FOREIGN-PRESSURE-LEDGER.json',
    'DATACUBE-TRANSFER-LEDGER.json',
    'RESOLUTION-LEDGER.json',
    'RETROSPECTIVE-QUEUE.json',
    'FIREBREAK-LEDGER.json',
    'WITNESS-VOCABULARY.json',
    'SURFACE-STATUS.json',
    'RELEASE-MANIFEST.json',
    'REVISION-RECEIPT.json',
]:
    obj = json.loads(read(path))
    if 'revision' in obj:
        obj['revision'] = REV
        write_json(path, obj)

print('apply_rev0251: OK')
