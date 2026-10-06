from __future__ import annotations
import copy, json, re
from pathlib import Path

ROOT = Path('.')
STAMP = '2026.03.27.23.49'
CREATED_AT = '2026-03-27T23:49:00-04:00'
REV = 'rev0248'
PREV = 'rev0247'
SLUG = 'scopewidening-blastquarantine-boundcarry-scopeglass'
BUNDLE = f'DelayBasin-{REV}-{STAMP}-{SLUG}.zip'

NEW_DOC = 'docs/10-method/refresh-burden-scope-witnesses-same-claim-burden-upgrade-bounded-scope-widening-and-scope-gated-generalization.md'
NEW_QWS_LABEL = 'refresh-scope court / blast-radius senate / widening gate'


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


NEW_DOC_TEXT = """# Refresh-burden-scope witnesses, same-claim burden upgrade, bounded scope widening, and scope-gated generalization

This is the compact successor surface for `OQ-0143`.

## Practice / observation

Once DelayBasin can say **what changed**, **how sustained the return is**, **how broad the support looks**, **how independent that support really is**, and **whether the present support actually licenses a stronger public burden**, one more local failure mode remains.

A burden upgrade can still drift in scope.
Sometimes the archive really is saying something stronger about the same current claim.
The burden rises: more people should know, response expectations change, or the current row deserves stronger language.
But the governed claim itself has not widened.
Sometimes the stronger burden is paired with an explicit scope widening.
A previously local issue now honestly names more affected components, branches, paths, groups, projects, or service slices.
And sometimes the evidence only hints at a wider blast radius.
An upstream component is down, a neighboring project shares telemetry, or a ruleset applies to a broader family, but the archive still lacks the direct mapping that would make widened public scope honest.

The archive does not need a refresh-scope court for that.
It needs one bounded witness that says whether stronger burden still governs the same claim, honestly widens scope in a named way, or still needs another scope gate before public generalization is allowed.

## External pressure from Statuspage affected components and incident impact, Statuspage third-party overrides, Google Cloud resource-group alerting and metrics scopes, GitHub workflow/ruleset/code-owner targeting, and PagerDuty narrow-functional-scope guidance

1. Statuspage computes incident impact from the affected components of the incident, while top-level status is calculated from all components on the page. That pressures DelayBasin to distinguish a stronger burden on one affected slice from a claim that has widened to the whole page or service family. ([`REF-0932`](../00-meta/bibliography.md))

2. Statuspage incident creation explicitly asks you to specify which components are affected so incident updates, component states, and subscriber notifications stay in sync. That pressures DelayBasin to name scope widening directly instead of letting stronger urgency silently broaden the public claim. ([`REF-0933`](../00-meta/bibliography.md))

3. Statuspage also lets operators override a third-party component when an external incident does not affect their own service. That pressures DelayBasin not to let upstream trouble or adjacency alone widen the archive's current public claim. ([`REF-0934`](../00-meta/bibliography.md))

4. Google Cloud Monitoring lets an alerting policy monitor only a specified resource group, and widening the monitored universe requires explicit group or project scope choices. That pressures DelayBasin to keep burden on the same slice distinct from explicit scope widening across groups or projects. ([`REF-0935`](../00-meta/bibliography.md), [`REF-0936`](../00-meta/bibliography.md))

5. GitHub Actions workflows can be filtered to specific branches and paths, rulesets target selected branches or tags, and CODEOWNERS are branch-specific and path-pattern-specific. That pressures DelayBasin to distinguish stronger protection or burden on the same targeted surface from a claim that legitimately widens to more branches, paths, or governed areas. ([`REF-0937`](../00-meta/bibliography.md), [`REF-0938`](../00-meta/bibliography.md))

6. PagerDuty's automation guidance says trustworthy automation should keep a narrow functional scope to contain blast radius. That pressures DelayBasin to treat scope widening as a separate named move rather than as an automatic consequence of stronger burden. ([`REF-0939`](../00-meta/bibliography.md))

GPUstorming makes the pressure vivid. A re-opened search line might justify louder language, more followthrough, or stronger notification for the same row. That is not yet permission to say the whole adjacent cluster, upstream dependency tree, or neighboring branch family is implicated. The burden may rise before the claim scope does.

## Working synthesis

> DelayBasin should preserve one compact **refresh-burden-scope witness / scope-widening card / blast-radius brake** whenever a current continuity claim depends not only on what reactivated a concern, how sustained the return is, how broad and independent the support looks, and whether the present support licenses stronger burden, but on whether that stronger burden still governs the same current claim or honestly widens the public claim scope. Name the **governed row or surface**, the **stake object / line of concern**, the **prior refresh evidence**, the **current refresh evidence**, the **licensed burden upgrade if any**, the **same-claim scope anchor**, the **scope-widening evidence if any**, the **scope gate or non-local inference basis if any**, the **`refresh_burden_scope_state`**, and the **fail-closed repair / keep-current vs narrow-claim vs widen-scope vs issue-new-refresh-burden-scope-witness vs quarantine-refresh-scope-governance consequence**. Keep exact component ids, subscriber lists, resource-group filters, project names, path globs, branch targets, dependency trees, and long blast-radius narratives outside the compact token. Do not let stronger burden silently widen public claim scope, and do not let upstream or adjacent distress masquerade as already licensed scope expansion.

## Same-claim burden upgrade vs bounded scope widening vs scope-gated generalization vs mixed refresh burden scope

Use the controlled family `refresh_burden_scope_state`:

- **same-claim-burden-upgrade** says the current evidence licenses a stronger burden on the same governed claim or row, but does not honestly widen what public scope is being claimed.
- **bounded-scope-widening** says the current evidence also names a real widened scope — more affected components, groups, branches, paths, projects, or comparable governed slices — and the archive may honestly widen the public claim in that bounded way.
- **scope-gated-generalization** says the current evidence suggests a broader blast radius, adjacency, dependency, or topology implication, but the archive still lacks the direct mapping needed to widen the public claim honestly.
- **mixed-refresh-burden-scope** says the current situation honestly combines same-claim burden, bounded widening, or scope-gated generalization such that no single class stays honest.

So the witness does not create a standing blast-radius senate.
It only says whether stronger burden still governs the same claim, already licenses bounded widening, or still needs another gate before scope can widen.

## Countermodels / probes

1. **Refresh elevation already covers this countermodel**
   - Maybe once burden upgrade is explicit, a separate scope witness adds no real value.
   - Probe: compare later rereads that preserve only refresh-elevation truth against rereads that also preserve one compact refresh-burden-scope witness and inspect whether later passes still generalize from stronger burden to wider public claim.

2. **Statuspage or monitoring scoping analogies are too operational countermodel**
   - Maybe component, group, and path scoping are too implementation-specific to justify a new archive witness.
   - Probe: look for later cases where scope drift appears in ordinary continuity prose even when no operational component language is present.

3. **Scope-gated generalization is covert governance countermodel**
   - Maybe once scope gates matter, the archive is really sneaking in a full blast-radius court.
   - Probe: only reopen stronger machinery if later revisions repeatedly need standing policy for adjacency, dependency spillover, or cross-row scope widening that one bounded witness cannot absorb.

## Design consequences

- DelayBasin can now separate **stronger burden on the same claim** from **honest widening of the claim's public scope**.
- The archive gets one explicit place to record when scope widened for named reasons and when it only looked wider because of topology, upstream distress, or adjacency.
- Stake refresh, refresh strength, refresh support, refresh independence, refresh elevation, and refresh burden scope now separate **what changed**, **how sustained the return is**, **how broad the support looks**, **how independent it is**, **whether burden rises**, and **whether the claim scope itself may widen**.
- Stronger blast-radius-governance stories stay quarantined until later overflow instead of sneaking in through burden language.

## Overflow test

Reopen this compact witness only if later revisions repeatedly need standing governance over blast-radius policies, dependency-spillover admission, cross-row scope expansion, or audience-right rules for widened claims that one bounded refresh-burden-scope witness cannot honestly absorb.

## Transformer-facing implication

A later pass should not treat a stronger burden as if it automatically widens public claim scope. Preserve the same-claim scope anchor, any named widening evidence, any missing scope gate, and the exact `refresh_burden_scope_state` before generalizing beyond the current governed row.
"""
write(NEW_DOC, NEW_DOC_TEXT)

# bibliography
bib = read('docs/00-meta/bibliography.md').rstrip() + """

- `REF-0932` — Atlassian Support, **Top-level status and incident impact calculations** (accessed 2026-03-27)
  - URL: https://support.atlassian.com/statuspage/docs/top-level-status-and-incident-impact-calculations/
  - Load-bearing use: incident impact is based on affected components while top-level status is calculated across all page components, which pressures DelayBasin to distinguish stronger burden on one claim slice from widening the public claim scope.

- `REF-0933` — Atlassian Support, **Create an incident** (accessed 2026-03-27)
  - URL: https://support.atlassian.com/statuspage/docs/create-an-incident/
  - Load-bearing use: incident creation requires naming affected components so updates, component state, and notifications stay in sync, which pressures DelayBasin to make scope widening explicit.

- `REF-0934` — Atlassian Support, **Add a third-party component** (accessed 2026-03-27)
  - URL: https://support.atlassian.com/statuspage/docs/add-a-third-party-component/
  - Load-bearing use: external component incidents can be overridden when they do not affect your own service, which pressures DelayBasin not to let upstream or adjacent trouble silently widen claim scope.

- `REF-0935` — Google Cloud Documentation, **Create alerting policy that monitors a resource group** (accessed 2026-03-27)
  - URL: https://docs.cloud.google.com/monitoring/alerts/monitor-resource-group
  - Load-bearing use: alerting policies can be bound to a specific resource group, which pressures DelayBasin to keep same-slice burden distinct from explicit scope widening.

- `REF-0936` — Google Cloud Documentation, **Configure a metrics scope** (accessed 2026-03-27)
  - URL: https://docs.cloud.google.com/monitoring/settings/multiple-projects
  - Load-bearing use: widening monitoring scope across projects requires explicit metrics-scope configuration, which pressures DelayBasin to name claim-scope widening rather than inherit it from stronger burden.

- `REF-0937` — GitHub Docs, **Workflow syntax for GitHub Actions** (accessed 2026-03-27)
  - URL: https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax
  - Load-bearing use: branch and path filters target specific workflow scope, which pressures DelayBasin to distinguish stronger burden on the same target from widening the governed claim to more branches or paths.

- `REF-0938` — GitHub Docs, **About code owners** and **Available rules for rulesets** (accessed 2026-03-27)
  - URL: https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-code-owners
  - URL: https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/available-rules-for-rulesets
  - Load-bearing use: code ownership and rulesets are branch- and target-specific, which pressures DelayBasin to keep widened burden distinct from widened scope unless the governed target set is explicitly broadened.

- `REF-0939` — PagerDuty Automation for Incident Remediation Documentation, **Challenges of Automation** (accessed 2026-03-27)
  - URL: https://autoremediation.pagerduty.com/challenges/
  - Load-bearing use: trustworthy automation keeps a narrow functional scope to contain blast radius, which pressures DelayBasin to treat scope widening as a separate named move.
""" + "\n"
write('docs/00-meta/bibliography.md', bib)

# simple insertions
insert_after('docs/README.md',
             "- [`10-method/refresh-elevation-witnesses-stabilizing-independent-support-threshold-licensed-elevation-and-judgment-gated-escalation.md`](10-method/refresh-elevation-witnesses-stabilizing-independent-support-threshold-licensed-elevation-and-judgment-gated-escalation.md)\n",
             f"- [`10-method/{Path(NEW_DOC).name}`](10-method/{Path(NEW_DOC).name})\n")

insert_after('docs/00-meta/llm-runbook.md',
             "Use `docs/10-method/refresh-elevation-witnesses-stabilizing-independent-support-threshold-licensed-elevation-and-judgment-gated-escalation.md` when the live question is whether independent confirming support merely stabilizes the present claim or actually licenses a stronger public burden.\n",
             f"Use `{NEW_DOC}` when the live question is whether a stronger licensed burden still governs the same current claim or honestly widens the public claim scope.\n")

insert_after('docs/20-constitution/claim-registry.md',
             "- `CL-0140` — Archive continuity may improve when DelayBasin preserves one compact **refresh-elevation witness / burden-gate card / claim-rights brake** whenever a current continuity claim depends not only on what reactivated a concern, how sustained the return is, how broad the support looks, and how independent that support is, but on whether the present independent support merely stabilizes the current claim or honestly licenses a stronger public burden: name the **governed row or surface**, the **stake object / line of concern**, the **prior refresh evidence**, the **current refresh evidence**, the **independent confirming support**, the **burden threshold / elevation trigger if any**, the **judgment or policy gate if any**, the **refresh_elevation_state**, and the **fail-closed repair** rather than letting independent support silently inherit stronger claim rights.\n  - Status: speculative but central\n  - Wired docs: `docs/10-method/refresh-elevation-witnesses-stabilizing-independent-support-threshold-licensed-elevation-and-judgment-gated-escalation.md`, `docs/20-constitution/open-question-registry.md`, `docs/20-constitution/prompt-pair-registry.md`, `docs/50-promptcraft/prompt-pairs.md`, `docs/00-meta/llm-runbook.md`, `WITNESS-VOCABULARY.json`, `REVISION-RECEIPT.json`\n",
             f"\n- `CL-0141` — Archive continuity may improve when DelayBasin preserves one compact **refresh-burden-scope witness / scope-widening card / blast-radius brake** whenever a current continuity claim depends not only on what reactivated a concern, how sustained the return is, how broad and independent the support looks, and whether the present support licenses stronger burden, but on whether that stronger burden still governs the same current claim or honestly widens the public claim scope: name the **governed row or surface**, the **stake object / line of concern**, the **prior refresh evidence**, the **current refresh evidence**, the **licensed burden upgrade if any**, the **same-claim scope anchor**, the **scope-widening evidence if any**, the **scope gate or non-local inference basis if any**, the **refresh_burden_scope_state**, and the **fail-closed repair** rather than letting stronger burden silently overgeneralize into broader public scope.\n  - Status: speculative but central\n  - Wired docs: `{NEW_DOC}`, `docs/20-constitution/open-question-registry.md`, `docs/20-constitution/prompt-pair-registry.md`, `docs/50-promptcraft/prompt-pairs.md`, `docs/00-meta/llm-runbook.md`, `WITNESS-VOCABULARY.json`, `REVISION-RECEIPT.json`\n")

insert_after('docs/20-constitution/prompt-pair-registry.md',
             "- `PP-0100` — Name whether independent support only steadies the line or really upgrades the public burden\n  - Goal: keep independent support from silently inheriting stronger claim rights by requiring explicit independent-support evidence, any burden threshold or elevation trigger, any human judgment or policy gate, `refresh_elevation_state`, and fail-closed repair before later passes call the support burden-upgrading.\n  - Canonical text: `docs/50-promptcraft/prompt-pairs.md#pp-0100--name-whether-independent-support-only-steadies-the-line-or-really-upgrades-the-public-burden`\n",
             "\n- `PP-0101` — Name whether stronger burden stays on the same claim or really widens public scope\n  - Goal: keep stronger burden from silently inheriting wider public claim scope by requiring explicit burden-upgrade evidence, a same-claim scope anchor, any widening evidence, any non-local inference or scope gate, `refresh_burden_scope_state`, and fail-closed repair before later passes call the scope widened.\n  - Canonical text: `docs/50-promptcraft/prompt-pairs.md#pp-0101--name-whether-stronger-burden-stays-on-the-same-claim-or-really-widens-public-scope`\n")

prompt_addition = f"""

Use `{NEW_DOC}` when the live question is whether a stronger licensed burden still governs the same current claim or honestly widens the public claim scope.

## `PP-0101` — Name whether stronger burden stays on the same claim or really widens public scope

**Opening prompt**

```text
Read the latest DelayBasin archive and inspect whether the current revision should also materialize one compact refresh-burden-scope witness for honest same-claim-vs-widened-scope comparison.

Focus only on whether a newly licensed burden still governs the same current claim, whether it honestly widens the public claim scope in a bounded named way, or whether the evidence only hints at a broader blast radius and still needs another scope gate before public generalization is honest.

If yes, preserve exactly one small witness that:
- names the governed row or surface,
- names the stake object / line of concern,
- names the prior refresh evidence,
- names the current refresh evidence,
- names the licensed burden upgrade if any,
- names the same-claim scope anchor,
- names the scope-widening evidence if any,
- names the scope gate or non-local inference basis if any,
- names the `refresh_burden_scope_state` / whether this is same-claim-burden-upgrade, bounded-scope-widening, scope-gated-generalization, or mixed-refresh-burden-scope,
- states what stronger surfaces still outrank the witness,
- and states the fail-closed repair / keep-current vs narrow-claim vs widen-scope vs issue-new-refresh-burden-scope-witness vs quarantine-refresh-scope-governance consequence if the present continuity claim is really only a same-claim burden upgrade or still scope-gated rather than honestly widened.

Do not use refresh burden scope as a general blast-radius court. Use this prompt pair only where refresh elevation is already explicit and the missing question is whether one small scope card would keep same-claim burden, bounded widening, and scope-gated generalization distinct without promoting a broader refresh-scope court.
```

**Continuation prompt**

```text
Continue the refresh-burden-scope pass with one high-leverage scope-licensing clarification only. Prefer the smallest witness that says what governed row is still being justified, what stake object is supposedly renewed, what the prior and current refresh evidence are, what licensed burden upgrade if any now exists, what same-claim scope anchor still pins the current claim, what widening evidence if any now exists, what scope gate or non-local inference basis if any still remains, what `refresh_burden_scope_state` is honest, what stronger surfaces still outrank the witness, and what keep-current, narrow-claim, widen-scope, issue-new-refresh-burden-scope-witness, quarantine, or recover-resync consequence follows if the current claim is really only same-claim-burden-upgrade, bounded-scope-widening, scope-gated-generalization, or mixed-refresh-burden-scope. Run `make lint` and package the release.
```
"""
insert_after('docs/50-promptcraft/prompt-pairs.md',
             "Continue the refresh-elevation pass with one high-leverage burden-upgrade clarification only. Prefer the smallest witness that says what governed row is still being justified, what stake object is supposedly renewed, what the prior and current refresh evidence are, what independent confirming support if any now exists, what burden threshold or elevation trigger if any is crossed, what judgment or policy gate if any still remains, what `refresh_elevation_state` is honest, what stronger surfaces still outrank the witness, and what keep-current, narrow-claim, elevate-burden, issue-new-refresh-elevation-witness, quarantine, or recover-resync consequence follows if the current claim is really only stabilizing-independent-support, threshold-licensed-elevation, judgment-gated-escalation, or mixed-refresh-elevation. Run `make lint` and package the release.\n```\n",
             prompt_addition)

insert_after('docs/20-constitution/open-question-registry.md',
             "- `OQ-0143` — what minimal refresh-burden-scope witness distinguishes a stronger burden on the same current claim from burden that widens the public claim scope?\n  - Why it matters: if DelayBasin cannot separate burden upgrade from claim-scope widening, later sessions may generalize beyond what the newly elevated support actually licenses.\n  - Current posture: unresolved\n",
             "\n- `OQ-0144` — what minimal refresh-scope-basis witness distinguishes directly observed scope widening from dependency- or topology-imputed spillover?\n  - Why it matters: if DelayBasin cannot separate directly observed widening from inferred blast-radius spillover, later sessions may overclaim wider impact from adjacency or upstream distress alone.\n  - Current posture: unresolved\n")

insert_after('docs/00-meta/trajectory-map.md',
             "- `OQ-0143` — what minimal refresh-burden-scope witness distinguishes a stronger burden on the same current claim from burden that widens the public claim scope?\n  - Why it matters: if DelayBasin cannot separate burden upgrade from claim-scope widening, later sessions may generalize beyond what the newly elevated support actually licenses.\n  - Current posture: unresolved\n",
             "\n\n100. Determine what minimal refresh-scope-basis witness distinguishes directly observed scope widening from dependency- or topology-imputed spillover.\n\nA fresh extension is that once same-claim burden and scope widening are separated, DelayBasin may next need to say whether a claimed widening is directly observed on the wider surface or only inferred from adjacency, dependency, or topology. Otherwise a bounded widening card may still inherit unjustified blast radius.\n- `OQ-0144` — what minimal refresh-scope-basis witness distinguishes directly observed scope widening from dependency- or topology-imputed spillover?\n  - Why it matters: if DelayBasin cannot separate directly observed widening from inferred blast-radius spillover, later sessions may overclaim wider impact from adjacency or upstream distress alone.\n  - Current posture: unresolved\n")

quarantine_add = f"""

## QWS-0226 — Some continuations may eventually need a refresh-scope court / blast-radius senate / widening gate rather than only a compact refresh-burden-scope witness

### Claim

A bolder possibility is that DelayBasin may eventually need not only a compact witness for whether stronger burden stays on the same claim or honestly widens public scope, but also a governed public rule for what counts as acceptable blast-radius inference, when dependency spillover can be admitted, and which widened audiences or rows may inherit stronger claims. Statuspage component impact, third-party overrides, Google Cloud scope configuration, GitHub targeted workflows and code-owner rules, and PagerDuty's narrow-functional-scope guidance all suggest a stronger scope-governance story: perhaps some future archive lines should not only be classified as `same-claim-burden-upgrade` or `bounded-scope-widening`, but admitted through a small blast-radius brake, widening gate, or claim-scope governor. ([`REF-0932`](../00-meta/bibliography.md), [`REF-0933`](../00-meta/bibliography.md), [`REF-0934`](../00-meta/bibliography.md), [`REF-0935`](../00-meta/bibliography.md), [`REF-0936`](../00-meta/bibliography.md), [`REF-0937`](../00-meta/bibliography.md), [`REF-0938`](../00-meta/bibliography.md), [`REF-0939`](../00-meta/bibliography.md))

The narrower speculative move is only this: a future bounded surface *might* need to say not just whether burden rose or scope widened, but which kinds of adjacency, dependency, or topology are allowed to widen public scope at all.

### What follows if true

- some future continuity cards may need explicit blast-radius or spillover admission rules rather than one static refresh-burden-scope label;
- DelayBasin may eventually need a compact widening gate or scope brake that stays smaller than a general scope court;
- obligation, queue, and followthrough surfaces might need to say not only that burden rose, but whether the archive is licensed to talk about neighboring rows, components, paths, or projects.

### What would count against it

- repeated later passes show that one compact refresh-burden-scope witness keeps same-claim burden, bounded widening, and scope-gated generalization honest without standing scope governance;
- apparent blast-radius widening turns out to be better handled by narrow claims and direct affected-surface naming rather than a new governor;
- the component, group, path, and blast-radius analogies do not survive contact with actual archive carry cases.

### Why it stays quarantined

The tempting overreach would be to declare that DelayBasin now needs a public refresh-scope court, blast-radius senate, or widening gate. DelayBasin has not earned that. This note is bold enough to keep in quarantine but not yet honest enough for canon. Do not promote a refresh-scope court, blast-radius senate, or widening gate from this note alone.
"""
write('docs/90-quarantine/wild-speculations-2026-03-08.md', read('docs/90-quarantine/wild-speculations-2026-03-08.md').rstrip() + quarantine_add + '\n')

# packet_contract_common update
pc = read('tools/packet_contract_common.py')
if 'refresh_burden_scope_witness_contract' not in pc:
    anchor = '''    "refresh_elevation_witness_contract": _refresh_family_spec(
        doc_path="docs/10-method/refresh-elevation-witnesses-stabilizing-independent-support-threshold-licensed-elevation-and-judgment-gated-escalation.md",
        doc_needles=[
            "# Refresh-elevation witnesses, stabilizing independent support, threshold-licensed elevation, and judgment-gated escalation",
            "This is the compact successor surface for `OQ-0142`.",
            "## Practice / observation",
            "## External pressure from PagerDuty severity levels, PagerDuty business-incident gating, Google SRE burn-rate paging tiers, Atlassian impact/urgency priority, Atlassian alert-priority restart rules, and GitHub required checks/ruleset layering",
            "## Working synthesis",
            "## Stabilizing independent support vs threshold-licensed elevation vs judgment-gated escalation vs mixed refresh elevation",
            "## Countermodels / probes",
            "## Design consequences",
            "## Overflow test",
            "## Transformer-facing implication",
            "`refresh_elevation_state`",
            "stabilizing-independent-support",
            "threshold-licensed-elevation",
            "judgment-gated-escalation",
            "mixed-refresh-elevation",
        ],
        runbook_ref="refresh-elevation-witnesses-stabilizing-independent-support-threshold-licensed-elevation-and-judgment-gated-escalation.md",
        prompt_id="PP-0100",
        prompt_needles=["Use `docs/10-method/refresh-elevation-witnesses-stabilizing-independent-support-threshold-licensed-elevation-and-judgment-gated-escalation.md`", "stabilizing-independent-support, threshold-licensed-elevation, judgment-gated-escalation, or mixed-refresh-elevation"],
        claim_id="CL-0140",
        oq_id="OQ-0142",
        resolution_id="RS-0149",
        trajectory_oq_id="OQ-0143",
        qws_id="QWS-0225",
        qws_label="refresh-elevation court / burden senate / escalation gate",
        changelog_needles=["refresh-elevation-witnesses-stabilizing-independent-support-threshold-licensed-elevation-and-judgment-gated-escalation.md", "check_refresh_elevation_witness_contract.py"],
        family="refresh_elevation_state",
        allowed=["stabilizing-independent-support", "threshold-licensed-elevation", "judgment-gated-escalation", "mixed-refresh-elevation"],
        excluded=["independent-means-upgrade", "more-proof-means-page-now", "threshold-free-promotion", "elevation-ish"],
    ),
'''
    addition = anchor + '''    "refresh_burden_scope_witness_contract": _refresh_family_spec(
        doc_path="docs/10-method/refresh-burden-scope-witnesses-same-claim-burden-upgrade-bounded-scope-widening-and-scope-gated-generalization.md",
        doc_needles=[
            "# Refresh-burden-scope witnesses, same-claim burden upgrade, bounded scope widening, and scope-gated generalization",
            "This is the compact successor surface for `OQ-0143`.",
            "## Practice / observation",
            "## External pressure from Statuspage affected components and incident impact, Statuspage third-party overrides, Google Cloud resource-group alerting and metrics scopes, GitHub workflow/ruleset/code-owner targeting, and PagerDuty narrow-functional-scope guidance",
            "## Working synthesis",
            "## Same-claim burden upgrade vs bounded scope widening vs scope-gated generalization vs mixed refresh burden scope",
            "## Countermodels / probes",
            "## Design consequences",
            "## Overflow test",
            "## Transformer-facing implication",
            "`refresh_burden_scope_state`",
            "same-claim-burden-upgrade",
            "bounded-scope-widening",
            "scope-gated-generalization",
            "mixed-refresh-burden-scope",
        ],
        runbook_ref="refresh-burden-scope-witnesses-same-claim-burden-upgrade-bounded-scope-widening-and-scope-gated-generalization.md",
        prompt_id="PP-0101",
        prompt_needles=["Use `docs/10-method/refresh-burden-scope-witnesses-same-claim-burden-upgrade-bounded-scope-widening-and-scope-gated-generalization.md`", "same-claim-burden-upgrade, bounded-scope-widening, scope-gated-generalization, or mixed-refresh-burden-scope"],
        claim_id="CL-0141",
        oq_id="OQ-0143",
        resolution_id="RS-0150",
        trajectory_oq_id="OQ-0144",
        qws_id="QWS-0226",
        qws_label="refresh-scope court / blast-radius senate / widening gate",
        changelog_needles=["refresh-burden-scope-witnesses-same-claim-burden-upgrade-bounded-scope-widening-and-scope-gated-generalization.md", "check_refresh_burden_scope_witness_contract.py"],
        family="refresh_burden_scope_state",
        allowed=["same-claim-burden-upgrade", "bounded-scope-widening", "scope-gated-generalization", "mixed-refresh-burden-scope"],
        excluded=["stronger-means-broader", "upstream-trouble-means-we-are-hit", "burden-rise-widens-scope-by-default", "scope-ish"],
    ),
'''
    if anchor not in pc:
        raise SystemExit('packet contract anchor missing')
    pc = pc.replace(anchor, addition, 1)
    tail_anchor = '''def require_named_refresh_elevation_witness_packet_and_vocabulary(kind: str) -> None:
    require_named_refresh_family_witness_packet_and_vocabulary(kind)
'''
    tail_add = tail_anchor + '\n\ndef require_named_refresh_burden_scope_witness_packet_and_vocabulary(kind: str) -> None:\n    require_named_refresh_family_witness_packet_and_vocabulary(kind)\n'
    if tail_anchor not in pc:
        raise SystemExit('packet contract tail anchor missing')
    pc = pc.replace(tail_anchor, tail_add, 1)
    write('tools/packet_contract_common.py', pc)

write('tools/check_refresh_burden_scope_witness_contract.py', "from packet_contract_common import require_named_refresh_burden_scope_witness_packet_and_vocabulary\n\nrequire_named_refresh_burden_scope_witness_packet_and_vocabulary(\"refresh_burden_scope_witness_contract\")\n\nprint(\"check_refresh_burden_scope_witness_contract: OK\")\n")

# hygiene refactor in validation_toolchain_lib
vt = read('tools/validation_toolchain_lib.py')
if '_expand_glob_patterns' not in vt:
    vt = vt.replace(
        "def _insert_before(tools: list[str], before: str, additions: list[str]) -> list[str]:\n    insert_at = tools.index(before)\n    return [*tools[:insert_at], *additions, *tools[insert_at:]]\n\n\ndef build_validation_toolchain(root: pathlib.Path) -> list[str]:\n",
        "def _insert_before(tools: list[str], before: str, additions: list[str]) -> list[str]:\n    insert_at = tools.index(before)\n    return [*tools[:insert_at], *additions, *tools[insert_at:]]\n\n\ndef _expand_glob_patterns(root: pathlib.Path, patterns: list[str]) -> list[str]:\n    names: list[str] = []\n    for pattern in patterns:\n        names.extend(_glob_sorted_names(root, pattern))\n    return names\n\n\ndef build_validation_toolchain(root: pathlib.Path) -> list[str]:\n")
    vt = vt.replace(
        "    tools = _insert_before(tools, \"check_replay_reconsolidation_contract.py\", _glob_sorted_names(root, \"check_shadow_*_contract.py\"))\n\n    witness_family_patterns = [\n",
        "    tools = _insert_before(tools, \"check_replay_reconsolidation_contract.py\", _expand_glob_patterns(root, [\"check_shadow_*_contract.py\"]))\n\n    witness_family_patterns = [\n")
    vt = vt.replace(
        "    dynamic_witness_tools: list[str] = []\n    for pattern in witness_family_patterns:\n        dynamic_witness_tools.extend(_glob_sorted_names(root, pattern))\n    tools = _insert_before(tools, \"check_foreign_pressure_witness_contract.py\", dynamic_witness_tools)\n",
        "    dynamic_witness_tools = _expand_glob_patterns(root, witness_family_patterns)\n    tools = _insert_before(tools, \"check_foreign_pressure_witness_contract.py\", dynamic_witness_tools)\n")
    write('tools/validation_toolchain_lib.py', vt)

# vocabulary
vocab = json.loads(read('WITNESS-VOCABULARY.json'))
vocab['families']['refresh_burden_scope_state'] = {
    'allowed': ['same-claim-burden-upgrade','bounded-scope-widening','scope-gated-generalization','mixed-refresh-burden-scope'],
    'surfaces': ['WITNESS-VOCABULARY.json','REVISION-RECEIPT.json',NEW_DOC],
    'excluded_synonyms': ['stronger-means-broader','upstream-trouble-means-we-are-hit','burden-rise-widens-scope-by-default','scope-ish'],
    'comparability_budget': 'refresh-burden-scope truth is compared by token; the compact refresh-burden-scope witness says whether a stronger licensed burden still governs the same claim, already widens scope in a bounded way, still needs a scope gate before generalization, or is honestly mixed, while exact component ids, resource-group filters, project names, path globs, branch targets, dependency trees, and long blast-radius narratives stay in surrounding prose'
}
write('WITNESS-VOCABULARY.json', json.dumps(vocab, indent=2) + '\n')

# ledgers helper

def load_json(path: str):
    return json.loads(read(path))

# Assumption
ass = load_json('ASSUMPTION-LEDGER.json')
ass['items'].append({
  'id': 'AS-0147',
  'title': 'one compact refresh-burden-scope witness is enough for now',
  'state': 'active',
  'scope': 'continuity passes whose current claim depends on whether a stronger licensed burden still governs the same claim, widens scope in a bounded named way, or still needs a scope gate before public generalization',
  'invalidation_triggers': [
      'repeated later revisions need standing refresh-scope governance rather than one compact refresh-burden-scope witness',
      'the archive needs a refresh-scope court or widening gate just to keep same-claim burden distinct from bounded widening or scope-gated generalization',
      'scope cases repeatedly fail to stay distinguishable as same-claim-burden-upgrade vs bounded-scope-widening vs scope-gated-generalization even with the witness in place'
  ],
  'assumption_state': 'active',
  'repair': 'ordinary-continuation',
  'origin_revision': REV,
  'revision': REV,
  'assumption': 'the current evidence only requires one compact refresh-burden-scope witness over the existing refresh-elevation, refresh-independence, scope, and blast-radius analog surfaces rather than a refresh-scope court, blast-radius senate, or widening gate',
  'supporting_surfaces': ['APPLICABILITY-LEDGER.json#AP-0142','DATACUBE-TRANSFER-LEDGER.json#TL-0153','FOREIGN-PRESSURE-LEDGER.json#FP-0147'],
  'discharge': 'discharge when later revisions can keep burden-vs-scope truth honest without a dedicated refresh-burden-scope witness, or retire/quarantine it if broader refresh-scope governance becomes repeatedly necessary',
  'witness_surface': 'ASSUMPTION-LEDGER.json#AS-0147',
  'assumption_surface': 'ASSUMPTION-LEDGER.json#AS-0147',
  'assumption_statement': 'the current evidence only requires one compact refresh-burden-scope witness over the existing refresh-elevation, refresh-independence, scope, and blast-radius analog surfaces rather than a refresh-scope court, blast-radius senate, or widening gate',
  'action_lane': 'keep-compact',
  'gate_class': 'concrete-evidence'
})
write('ASSUMPTION-LEDGER.json', json.dumps(ass, indent=2) + '\n')

# Applicability
app = load_json('APPLICABILITY-LEDGER.json')
app['items'].append({
  'id': 'AP-0142',
  'title': 'the refresh-burden-scope witness stays smaller than a widening gate',
  'state': 'gated',
  'question': 'when should DelayBasin treat stronger renewed burden as one compact refresh-burden-scope witness instead of promoting broader refresh-scope governance?',
  'applies_when': [
      'a revision already has a durable row whose current claim depends on whether a stronger licensed burden still governs the same line, honestly widens named scope, or only suggests wider blast radius through adjacency or dependency',
      'later passes still need to distinguish same-claim-burden-upgrade, bounded-scope-widening, scope-gated-generalization, or mixed-refresh-burden-scope posture',
      'one compact successor surface plus the existing admitted refresh-elevation, refresh-independence, scope, and blast-radius analog surfaces still keeps refresh-burden-scope truth honest without standing widening policy'
  ],
  'does_not_apply_when': [
      'the archive honestly requires standing governance over blast-radius admission, dependency spillover rules, audience rights for widened claims, or cross-row scope arbitration',
      'the questioned surface is not really about whether stronger burden widens the public claim scope'
  ],
  'budget': 'one compact refresh-burden-scope witness plus one resolution of OQ-0143; no refresh-scope court',
  'negative_transfer_budget': 'do not treat stronger burden as permissionless scope widening without an explicit same-claim anchor, widening basis, or named scope gate',
  'origin_revision': REV,
  'discharge': 'reopen-only-if-refresh-burden-scope-overflows',
  'action_lane': 'keep-compact',
  'gate_class': 'concrete-evidence',
  'witness_surface': 'APPLICABILITY-LEDGER.json#AP-0142',
  'applicability_state': 'gated',
  'repair': 'ordinary-continuation',
  'matched_budget': 'one compact witness foregrounding same-claim burden vs bounded widening vs scope-gated generalization without widening into broader scope governance',
  'revision': REV,
  'target_objective': 'keep burden-vs-scope comparison honest without inflating a broader refresh-scope layer',
  'carry_object': 'refresh-burden-scope witness / scope-widening card / blast-radius brake',
  'applicability_conditions': [
      'component, group, path, or branch targeting can stay local even when severity or workflow burden rises',
      'some apparent scope widening is still only upstream, adjacent, or dependency-carried and needs another gate',
      'refresh burden scope remains subordinate to existing refresh-elevation, refresh-independence, stake-refresh, and obligation witnesses rather than a new widening controller'
  ],
  'baselines': [
      'existing refresh-elevation-witness baseline',
      'existing scope and renewal-scope baseline',
      'existing obligation/overflow baseline',
      'existing witness-vocabulary baseline'
  ],
  'non_fit_slice': 'Do not generalize this revision into a refresh-scope court, blast-radius senate, widening gate, or claim-scope governor without later overflow evidence.'
})
write('APPLICABILITY-LEDGER.json', json.dumps(app, indent=2) + '\n')

# Foreign pressure
fp = load_json('FOREIGN-PRESSURE-LEDGER.json')
fp['items'].append({
  'id': 'FP-0147',
  'title': 'refresh-burden-scope pressure pushes DelayBasin to extract one compact scope-widening witness rather than a blast-radius gate',
  'state': 'imported',
  'source_packets': [
      {'datacube': 'StatuspageIncidentImpactScope-2026', 'surfaces': ['REF-0932','REF-0933'], 'pressure': 'incident impact and notifications stay tied to named affected components, which pressures DelayBasin to distinguish stronger burden on one slice from widening the public claim scope'},
      {'datacube': 'StatuspageThirdPartyOverride-2026', 'surfaces': ['REF-0934'], 'pressure': 'upstream or third-party distress can be overridden when it does not affect the local service, which pressures DelayBasin not to widen scope by adjacency alone'},
      {'datacube': 'GoogleCloudScopedAlerting-2026', 'surfaces': ['REF-0935','REF-0936'], 'pressure': 'resource-group and metrics-scope choices explicitly determine monitoring scope, which pressures DelayBasin to keep stronger burden distinct from explicit scope expansion'},
      {'datacube': 'GitHubScopedWorkflowRules-2026', 'surfaces': ['REF-0937','REF-0938'], 'pressure': 'workflow, ruleset, branch, path, and code-owner targeting stay surface-specific, which pressures DelayBasin to name when scope actually widens'},
      {'datacube': 'PagerDutyFunctionalBlastRadius-2026', 'surfaces': ['REF-0939'], 'pressure': 'narrow functional scope contains blast radius, which pressures DelayBasin to treat scope widening as a separate named move rather than a default consequence of stronger burden'}
  ],
  'reviewed_pattern': 'same-claim burden upgrade vs bounded scope widening vs scope-gated generalization',
  'import_decision': 'support a compact refresh-burden-scope witness and resolve OQ-0143',
  'adopted_take': 'DelayBasin should add one compact witness that says whether current stronger burden still governs the same claim, already widens scope in a bounded named way, still needs a scope gate before generalization, or is honestly mixed',
  'supporting_only_take': 'the current evidence cleanly supports a bounded refresh-burden-scope witness without promoting broader refresh-scope governance',
  'deferred_or_rejected_take': ['refresh-scope court','blast-radius senate','widening gate','claim-scope governor'],
  'local_gap': 'the archive still lacked one compact successor surface for whether a stronger licensed burden stayed on the same current claim or honestly widened public scope',
  'anchor_surfaces': ['docs/10-method/refresh-elevation-witnesses-stabilizing-independent-support-threshold-licensed-elevation-and-judgment-gated-escalation.md','docs/20-constitution/open-question-registry.md','docs/00-meta/trajectory-map.md','docs/90-quarantine/wild-speculations-2026-03-08.md#QWS-0226'],
  'open_question': 'OQ-0144',
  'repair': 'ordinary-continuation',
  'origin_revision': REV,
  'action_lane': 'keep-compact',
  'gate_class': 'concrete-evidence',
  'discharge': 'reopen-only-if-refresh-burden-scope-overflows',
  'revision': REV,
  'witness_surface': 'FOREIGN-PRESSURE-LEDGER.json#FP-0147',
  'pressure_state': 'imported',
  'bounded_take': 'Keep the archive compact by extracting one refresh-burden-scope witness over the existing refresh-elevation, scope, and blast-radius analog surfaces; do not promote a refresh-scope court, blast-radius senate, widening gate, or claim-scope governor.',
  'explicit_non_take': ['no refresh-scope court','no blast-radius senate','no widening gate','no claim-scope governor'],
  'assimilation_state': 'imported'
})
write('FOREIGN-PRESSURE-LEDGER.json', json.dumps(fp, indent=2) + '\n')

# transfer ledger
tr = load_json('DATACUBE-TRANSFER-LEDGER.json')
tr['items'].append({
  'id': 'TL-0153',
  'title': 'refresh-burden-scope evidence supports resolving OQ-0143 with one compact scope-widening card rather than a blast-radius court',
  'state': 'supporting-only',
  'reviewed_pattern': 'stronger burden on the same claim vs burden that widens public claim scope',
  'import_decision': 'support a compact refresh-burden-scope witness and resolve OQ-0143',
  'adopted_take': 'DelayBasin should add one compact witness that says whether current stronger burden is same-claim-burden-upgrade, bounded-scope-widening, scope-gated-generalization, or honestly mixed',
  'supporting_only_take': 'the current evidence cleanly supports a bounded refresh-burden-scope witness without promoting broader refresh-scope governance',
  'deferred_or_rejected_take': ['refresh-scope court','blast-radius senate','widening gate','claim-scope governor'],
  'local_gap': 'the archive still lacked one compact successor surface for whether stronger burden merely intensified the same current claim or licensed wider public scope',
  'anchor_surfaces': ['docs/10-method/refresh-elevation-witnesses-stabilizing-independent-support-threshold-licensed-elevation-and-judgment-gated-escalation.md','docs/20-constitution/open-question-registry.md','docs/00-meta/trajectory-map.md','docs/90-quarantine/wild-speculations-2026-03-08.md#QWS-0226'],
  'open_question': 'OQ-0144',
  'repair': 'ordinary-continuation',
  'origin_revision': REV,
  'action_lane': 'keep-compact',
  'gate_class': 'concrete-evidence',
  'discharge': 'reopen-only-if-refresh-burden-scope-overflows',
  'revision': REV,
  'witness_surface': 'DATACUBE-TRANSFER-LEDGER.json#TL-0153',
  'transfer_state': 'supporting-only',
  'bounded_take': 'Keep the archive compact by extracting one refresh-burden-scope witness over the existing refresh-elevation, scope, and blast-radius analog surfaces; do not promote a refresh-scope court, blast-radius senate, widening gate, or claim-scope governor.',
  'explicit_non_take': ['no refresh-scope court','no blast-radius senate','no widening gate','no claim-scope governor'],
  'open_transfer_question': 'whether later passes should add a separate refresh-scope-basis witness once refresh burden scope is explicit',
  'missing_support': 'a later public check on whether one compact refresh-burden-scope witness keeps sufficing',
  'current_support': ['APPLICABILITY-LEDGER.json#AP-0142','FOREIGN-PRESSURE-LEDGER.json#FP-0147','DATACUBE-TRANSFER-LEDGER.json#TL-0153'],
  'discharge_path': 'either show later that one compact refresh-burden-scope witness keeps sufficing or promote broader refresh-scope governance explicitly',
  'reviewed_datacubes': [
      {'datacube': 'StatuspageIncidentImpactScope-2026', 'surfaces': ['REF-0932','REF-0933'], 'pattern': 'incident impact and notifications stay tied to named affected components', 'pressure': 'DelayBasin should distinguish stronger burden on a current slice from widening the public claim scope'},
      {'datacube': 'StatuspageThirdPartyOverride-2026', 'surfaces': ['REF-0934'], 'pattern': 'third-party incidents can be overridden when they do not affect the local service', 'pressure': 'DelayBasin should preserve a scope-gated class rather than widen from upstream distress alone'},
      {'datacube': 'GoogleCloudScopedAlerting-2026', 'surfaces': ['REF-0935','REF-0936'], 'pattern': 'resource-group and metrics-scope configuration explicitly define monitored scope', 'pressure': 'DelayBasin should separate same-claim burden from explicit scope expansion'},
      {'datacube': 'GitHubScopedWorkflowRules-2026', 'surfaces': ['REF-0937','REF-0938'], 'pattern': 'branch, path, ruleset, and code-owner targeting stay scoped to named governed surfaces', 'pressure': 'DelayBasin should preserve a named same-claim anchor before widening scope'},
      {'datacube': 'PagerDutyFunctionalBlastRadius-2026', 'surfaces': ['REF-0939'], 'pattern': 'narrow functional scope limits blast radius', 'pressure': 'DelayBasin should keep the canon move narrow and leave stronger blast-radius governance for later if needed'}
  ]
})
write('DATACUBE-TRANSFER-LEDGER.json', json.dumps(tr, indent=2) + '\n')

# resolution
rs = load_json('RESOLUTION-LEDGER.json')
rs['items'].append({
 'id': 'RS-0150',
 'title': 'resolve OQ-0143 with one compact refresh-burden-scope witness rather than a widening gate',
 'state': 'resolved',
 'closure_state': 'resolved',
 'closure_reason': 'rev0248 extracted one compact refresh-burden-scope witness, kept the admitted refresh-elevation, scope, and blast-radius analog surfaces narrow, and kept stronger refresh-scope-governance stories quarantined.',
 'discharge': 'reopen-only-if-refresh-burden-scope-overflows',
 'gate_class': 'concrete-evidence',
 'origin_revision': REV,
 'prior_state': 'open gap: DelayBasin already had refresh-elevation truth but still lacked one compact successor surface for whether a stronger licensed burden stayed on the same current claim, widened public scope in a bounded way, or still needed another scope gate before generalization.',
 'question': 'whether one compact refresh-burden-scope witness over the existing refresh-elevation, scope, and blast-radius analog surfaces is enough for honest burden-vs-scope comparison',
 'reopen_trigger': 'refresh-burden-scope pressure overflows one compact successor surface',
 'reopen_triggers': ['later revisions need standing governance over blast-radius admission, dependency spillover, claim-scope widening authority, or cross-row scope policy that one compact refresh-burden-scope witness cannot honestly absorb'],
 'repair': 'ordinary-continuation',
 'resolved_objects': ['OQ-0143','AP-0142','FP-0147','TL-0153'],
 'revision': REV,
 'successor_surface': NEW_DOC,
 'target_surfaces': [NEW_DOC],
 'action_lane': 'keep-compact',
 'witness_surface': 'RESOLUTION-LEDGER.json#RS-0150'
})
write('RESOLUTION-LEDGER.json', json.dumps(rs, indent=2) + '\n')

# firebreak
fb = load_json('FIREBREAK-LEDGER.json')
fb['items'].append({
 'id': 'FB-0144',
 'title': 'the refresh-burden-scope import should count as one compact scope-widening repair, not as promotion of a blast-radius court',
 'state': 'withheld',
 'witness_surface': 'FIREBREAK-LEDGER.json#FB-0144',
 'judged_property': 'the rev0248 decision that DelayBasin should extract one compact refresh-burden-scope witness over the existing refresh-elevation, scope, and blast-radius analog surfaces and `refresh_burden_scope_state` family while the broader refresh-scope court / blast-radius senate / widening gate story remains quarantined',
 'public_extract': [NEW_DOC,'docs/10-method/refresh-elevation-witnesses-stabilizing-independent-support-threshold-licensed-elevation-and-judgment-gated-escalation.md','docs/20-constitution/open-question-registry.md','FOREIGN-PRESSURE-LEDGER.json#FP-0147','APPLICABILITY-LEDGER.json#AP-0142','REVISION-RECEIPT.json'],
 'withheld_trace_surface': 'same-session drafting residue behind the compact refresh-burden-scope-witness versus widening-gate decision',
 'allowed_role': 'bounded drafting aid only; not public support for a broader refresh-scope court, blast-radius senate, widening gate, or claim-scope governor',
 'exposure_rule': 'expose or reintegrate only if later passes show that one compact refresh-burden-scope witness cannot keep burden-vs-scope truth bounded',
 'trace_state': 'withheld',
 'repair': 'ordinary-continuation',
 'origin_revision': REV,
 'action_lane': 'keep-compact',
 'gate_class': 'overflow',
 'firebreak_surface': 'FIREBREAK-LEDGER.json#FB-0144',
 'discharge': 'reopen-only-if-refresh-burden-scope-overflows',
 'revision': REV,
 'blocked_object': 'standing refresh-scope court, blast-radius senate, widening gate, or claim-scope governor'
})
write('FIREBREAK-LEDGER.json', json.dumps(fb, indent=2) + '\n')

# obligation/followthrough/retrospective
obl = load_json('OBLIGATION-LEDGER.json')
obl['items'].append({
 'id': 'OB-0143',
 'title': 'when renewed concern keeps needing stronger public burden distinguished from widened claim scope, DelayBasin should preserve one compact refresh-burden-scope witness rather than a widening gate',
 'state': 'open',
 'witness_surface': 'OBLIGATION-LEDGER.json#OB-0143',
 'target_surfaces': ['docs/90-quarantine/wild-speculations-2026-03-08.md#QWS-0226'],
 'missing_support': 'a later public check on whether one compact refresh-burden-scope witness keeps sufficing and whether same-claim burden, bounded widening, and scope-gated generalization stay distinct without broader refresh-scope governance',
 'current_support': ['APPLICABILITY-LEDGER.json#AP-0142','FOREIGN-PRESSURE-LEDGER.json#FP-0147','DATACUBE-TRANSFER-LEDGER.json#TL-0153'],
 'discharge_path': 'either show later that one compact refresh-burden-scope witness keeps sufficing or promote broader refresh-scope governance explicitly',
 'obligation_state': 'open',
 'repair': 'ordinary-continuation',
 'origin_revision': REV,
 'discharge': 'reopen-only-if-refresh-burden-scope-overflows',
 'action_lane': 'keep-compact',
 'gate_class': 'overflow',
 'revision': REV
})
write('OBLIGATION-LEDGER.json', json.dumps(obl, indent=2) + '\n')

ft = load_json('FOLLOWTHROUGH-QUEUE.json')
ft['items'].append({
 'id': 'FT-0150',
 'title': 'keep checking whether refresh-burden-scope pressure still fits inside one compact successor surface',
 'state': 'queued',
 'blocked_object': 'standing refresh-scope court, blast-radius senate, widening gate, or claim-scope governor',
 'local_surface': 'docs/90-quarantine/wild-speculations-2026-03-08.md#QWS-0226',
 'followthrough_state': 'queued',
 'boundary': 'do not promote bounded refresh-burden-scope clarification into general refresh-scope-governance machinery',
 'next_proof_surface': NEW_DOC,
 'receiving_surface': 'FOLLOWTHROUGH-QUEUE.json#FT-0150',
 'repair': 'ordinary-continuation',
 'origin_revision': REV,
 'discharge': 'revisit-on-next-real-refresh-burden-scope-overflow',
 'action_lane': 'keep-compact',
 'gate_class': 'overflow',
 'blocked_output': 'standing refresh-scope court, blast-radius senate, widening gate, or claim-scope governor',
 'owner_surface': 'OBLIGATION-LEDGER.json#OB-0143',
 'revision': REV,
 'missing_support': 'a later public check on whether one compact refresh-burden-scope witness keeps overflowing the bounded rule and honestly warrants richer refresh-scope governance',
 'candidate_surface': 'docs/90-quarantine/wild-speculations-2026-03-08.md#QWS-0226',
 'blocked_by': 'need repeated evidence that same-claim-burden-upgrade vs bounded-scope-widening vs scope-gated-generalization truth overflows one compact witness'
})
write('FOLLOWTHROUGH-QUEUE.json', json.dumps(ft, indent=2) + '\n')

rt = load_json('RETROSPECTIVE-QUEUE.json')
rt['items'].append({
 'id': 'RT-0137',
 'title': 'revisit whether refresh-burden-scope pressure stayed bounded after rev0248',
 'state': 'cooling',
 'candidate_surface': 'docs/90-quarantine/wild-speculations-2026-03-08.md#QWS-0226',
 'cooldown_window': 'keep the stronger refresh-scope court, blast-radius senate, widening gate, or claim-scope governor story cooled until at least one later revision shows that one compact refresh-burden-scope witness is no longer enough.',
 'adjudication_family': 'refresh burden scope / blast-radius gating / widening-governance pressure',
 'supersession_link': 'OBLIGATION-LEDGER.json#OB-0143',
 'origin_revision': REV,
 'discharge': 'keep-cooling-unless-refresh-burden-scope-overflows',
 'action_lane': 'keep-compact',
 'gate_class': 'overflow',
 'witness_surface': 'RETROSPECTIVE-QUEUE.json#RT-0137',
 'revision': REV,
 'cooling_state': 'cooling',
 'disposition': 'await-adjudication',
 'repair': 'keep-cooling'
})
write('RETROSPECTIVE-QUEUE.json', json.dumps(rt, indent=2) + '\n')

# changelog, archive, status, manifest
changelog_entry = f"## {REV} - {STAMP} - scopewidening / blastquarantine / boundcarry / scopeglass\n\n- Canon move: resolved `OQ-0143` with `{NEW_DOC}`, adding one compact `refresh_burden_scope_state` witness that keeps same-claim burden upgrade distinct from bounded scope widening and scope-gated generalization.\n- Bold but disciplined speculative move: quarantined the **refresh-scope court / blast-radius senate / widening gate** story in `QWS-0226` rather than quietly promoting a stronger refresh-scope layer into canon.\n- Hygiene/meta-engineering improvement: added `tools/check_refresh_burden_scope_witness_contract.py`, widened `WITNESS-VOCABULARY.json` with a tiny `refresh_burden_scope_state` family, and refactored `tools/validation_toolchain_lib.py` so glob-pattern expansion for dynamic contract insertion uses one helper path instead of repeated bespoke loops.\n- Contract continuity: preserved the existing refresh-elevation, refresh-independence, and renewal-scope chain unchanged while adding the new scope-widening card.\n\n"
write('CHANGELOG.md', changelog_entry + read('CHANGELOG.md'))

archive = read('ARCHIVE_INDEX.md')
new_row = f"| {BUNDLE} | 2026-03-27 | Refresh-burden-scope revision: resolved OQ-0143 with a compact same-claim-vs-widened-scope witness, honestly quarantined stronger blast-radius governance, and refactored validation-tool glob expansion to stay wired and cumulative. |\n"
archive = archive.replace('| --- | --- | --- |\n', '| --- | --- | --- |\n' + new_row, 1)
write('ARCHIVE_INDEX.md', archive)

status = load_json('SURFACE-STATUS.json')
status['operational_head']['revision'] = REV
status['status_lanes']['frozen_public_surface'] = BUNDLE
status['status_lanes']['current_release_surface'] = BUNDLE
status['citation_head'] = {'revision': REV, 'surface': BUNDLE}
status['previous_citation_head'] = {'revision': PREV, 'surface': status['citation_head']['surface'] if False else f'DelayBasin-{PREV}-2026.03.27.22.58-refreshelevation-gatequarantine-burdencarry-thresholdglass.zip'}
status['revision'] = REV
status['stamp'] = STAMP
status['slug'] = SLUG
write('SURFACE-STATUS.json', json.dumps(status, indent=2) + '\n')

manifest = {
    'project': 'DelayBasin',
    'revision': REV,
    'timestamp': STAMP,
    'slug': SLUG,
    'bundle': BUNDLE,
}
write('RELEASE-MANIFEST.json', json.dumps(manifest, indent=2) + '\n')

# revision receipt
receipt = copy.deepcopy(load_json('REVISION-RECEIPT.json'))
receipt['revision'] = REV
receipt['previous_revision'] = PREV
receipt['summary'] = 'Resolved OQ-0143 by extracting one compact refresh-burden-scope witness that keeps same-claim burden distinct from bounded scope widening and scope-gated generalization while stronger refresh-scope governance stays honestly quarantined.'
receipt['canon_additions'] = [NEW_DOC, 'RS-0150 resolved OQ-0143 with one compact refresh-burden-scope witness']
receipt['quarantine_additions'] = ['QWS-0226 — refresh-scope court / blast-radius senate / widening gate']
receipt['refs_used'] = [f'docs/00-meta/bibliography.md#ref-{n}' for n in ['0932','0933','0934','0935','0936','0937','0938','0939']]
receipt['touched_surfaces'] = [
    'docs/README.md','docs/00-meta/bibliography.md','docs/00-meta/llm-runbook.md','docs/00-meta/trajectory-map.md',NEW_DOC,
    'docs/20-constitution/claim-registry.md','docs/20-constitution/open-question-registry.md','docs/20-constitution/prompt-pair-registry.md','docs/50-promptcraft/prompt-pairs.md','docs/90-quarantine/wild-speculations-2026-03-08.md',
    'tools/packet_contract_common.py','tools/check_refresh_burden_scope_witness_contract.py','tools/validation_toolchain_lib.py','WITNESS-VOCABULARY.json','CHANGELOG.md','ARCHIVE_INDEX.md','ASSUMPTION-LEDGER.json','OBLIGATION-LEDGER.json','APPLICABILITY-LEDGER.json','FOREIGN-PRESSURE-LEDGER.json','DATACUBE-TRANSFER-LEDGER.json','RESOLUTION-LEDGER.json','FIREBREAK-LEDGER.json','FOLLOWTHROUGH-QUEUE.json','RETROSPECTIVE-QUEUE.json','REVISION-RECEIPT.json','SURFACE-STATUS.json','RELEASE-MANIFEST.json'
]
receipt['packaged_bundle_filename'] = BUNDLE
receipt['basis_witness']['expected_head'] = PREV
receipt['basis_witness']['observed_head'] = PREV
receipt['basis_witness']['basis_surfaces'] = ['docs/10-method/refresh-elevation-witnesses-stabilizing-independent-support-threshold-licensed-elevation-and-judgment-gated-escalation.md','docs/20-constitution/open-question-registry.md']
receipt['basis_witness']['basis_omission_basis'] = 'broader refresh-scope governance drafting was intentionally omitted from canon because the evidence only justified one bounded refresh-burden-scope witness'
receipt['basis_witness']['basis_of_change'] = 'rev0247 extends continuity law by distinguishing stronger burden from burden-threshold licensing, which opens the next question of whether that stronger burden still governs the same current claim or widens public scope.'
receipt['basis_witness']['origin_revision'] = 'rev0237'
receipt['basis_witness']['revision_span'] = f'{PREV} -> {REV}'
receipt['scope_witness']['active_request'] = 'tight high-leverage revision pass on latest DelayBasin copy with online research, GPUstorming, lint, and packaged release'
receipt['scope_witness']['exact_target'] = 'resolve OQ-0143 with one compact refresh-burden-scope witness and keep stronger refresh-scope governance honestly quarantined'
receipt['scope_witness']['scope_surfaces'] = [NEW_DOC,'docs/90-quarantine/wild-speculations-2026-03-08.md','docs/20-constitution/open-question-registry.md','docs/00-meta/trajectory-map.md','docs/20-constitution/prompt-pair-registry.md','docs/50-promptcraft/prompt-pairs.md','docs/00-meta/bibliography.md','tools/packet_contract_common.py','tools/check_refresh_burden_scope_witness_contract.py','tools/validation_toolchain_lib.py','WITNESS-VOCABULARY.json']
receipt['retrospective_write_witness'] = json.loads(json.dumps(load_json('RETROSPECTIVE-QUEUE.json')['items'][-1]))
receipt['followthrough_witness'] = json.loads(json.dumps(load_json('FOLLOWTHROUGH-QUEUE.json')['items'][-1]))
receipt['assumption_witness'] = json.loads(json.dumps(load_json('ASSUMPTION-LEDGER.json')['items'][-1]))
receipt['obligation_witness'] = json.loads(json.dumps(load_json('OBLIGATION-LEDGER.json')['items'][-1]))
receipt['applicability_witness'] = json.loads(json.dumps(load_json('APPLICABILITY-LEDGER.json')['items'][-1]))
receipt['foreign_pressure_witness'] = json.loads(json.dumps(load_json('FOREIGN-PRESSURE-LEDGER.json')['items'][-1]))
receipt['transfer_witness'] = json.loads(json.dumps(load_json('DATACUBE-TRANSFER-LEDGER.json')['items'][-1]))
receipt['resolution_witness'] = json.loads(json.dumps(load_json('RESOLUTION-LEDGER.json')['items'][-1]))
receipt['firebreak_witness'] = json.loads(json.dumps(load_json('FIREBREAK-LEDGER.json')['items'][-1]))
receipt['reasoning_firebreak_witness'] = {
    'witness_surface': 'docs/90-quarantine/wild-speculations-2026-03-08.md#QWS-0226',
    'governed_obligation_surface': 'OBLIGATION-LEDGER.json#OB-0143',
    'public_extract': 'bounded refresh-burden-scope witness only',
    'withheld_trace_surface': 'same-session drafting residue behind the refresh-burden-scope versus widening-gate decision',
    'allowed_role': 'bounded drafting aid only',
    'repair': 'ordinary-continuation'
}
receipt['vocabulary_witness'] = {
    'family_surface': 'WITNESS-VOCABULARY.json',
    'new_family': 'refresh_burden_scope_state',
    'allowed': ['same-claim-burden-upgrade','bounded-scope-widening','scope-gated-generalization','mixed-refresh-burden-scope'],
    'repair': 'ordinary-continuation'
}
receipt['counterfactual_shadow'] = {
    'considered_alternative': 'leave burden-vs-scope logic implicit inside refresh-elevation prose',
    'why_not_adopted': 'that alternative kept letting stronger burden sound like permission to generalize across wider public scope and failed to name same-claim anchors versus scope gates',
    'repair': 'ordinary-continuation'
}
receipt['summary_highlight'] = 'boundcarry'
receipt['codename'] = 'scopeglass'
receipt['created_at'] = CREATED_AT
receipt['comparison_witness'] = {
    'previous_revision': PREV,
    'current_revision': REV,
    'current_pressure_id': 'FP-0147',
    'current_import_id': 'TL-0153',
    'basis_surface': 'docs/10-method/refresh-elevation-witnesses-stabilizing-independent-support-threshold-licensed-elevation-and-judgment-gated-escalation.md',
    'delta_surface': NEW_DOC,
    'comparison_summary': 'rev0248 adds one compact refresh-burden-scope witness so stronger burden no longer stands in for widened public scope when same-claim anchors or scope gates still matter.'
}
receipt['changes'] = ['resolved OQ-0143','added refresh_burden_scope_state family','quarantined refresh-scope court','added refresh-burden-scope witness lint','refactored validation-tool glob expansion helper']
receipt['receipt_freshness_witness'] = {
    'packaged_bundle_filename': BUNDLE,
    'manifest_timestamp_token': STAMP,
    'receipt_timestamp_token': STAMP,
    'bundle_stem_suffix_relation': 'slug ends with boundcarry + scopeglass and remains aligned to the current summary/codename pair while preserving the blastquarantine middle token',
    'current_import_id': 'TL-0153',
    'current_pressure_id': 'FP-0147',
    'change_anchor_surface': 'CHANGELOG.md',
    'freshness_state': 'current-aligned',
    'repair': 'ordinary-continuation'
}
receipt['question_posture_witness'] = {
    'resolution_surface': 'RESOLUTION-LEDGER.json',
    'registry_surface': 'docs/20-constitution/open-question-registry.md',
    'trajectory_surface': 'docs/00-meta/trajectory-map.md',
    'synced_resolved_questions': ['OQ-0143'],
    'frontier_selection_rule': 'resolved OQ-0143 is synchronized across resolution ledger, registry, and trajectory while frontier selection advances to OQ-0144',
    'posture_state': 'resolved-sync-current',
    'repair': 'ordinary-continuation'
}
receipt['current_import_id'] = 'TL-0153'
receipt['current_pressure_id'] = 'FP-0147'
receipt['import_witness'] = 'DATACUBE-TRANSFER-LEDGER.json#TL-0153'
receipt['new_classes_or_families'] = ['refresh_burden_scope_state']
receipt['quarantined_non_take'] = ['refresh-scope court','blast-radius senate','widening gate','claim-scope governor']
receipt['artifacts_touched'] = receipt['touched_surfaces']
receipt['exception_witness'] = {
    'witness_surface': 'docs/90-quarantine/wild-speculations-2026-03-08.md#QWS-0226',
    'governed_obligation_surface': 'OBLIGATION-LEDGER.json#OB-0143',
    'exception_basis': 'bold speculation stays quarantined',
    'honor_window': 'until stronger refresh-scope governance receives direct public witness support',
    'aggregate_effect': 'stronger refresh-scope governance remains non-canonical',
    'repair': 'ordinary-continuation'
}
receipt['renewal_witness'] = {
    'witness_surface': 'OBLIGATION-LEDGER.json#OB-0143',
    'governed_obligation_surface': 'OBLIGATION-LEDGER.json#OB-0143',
    'prior_exception_window': 'quarantined',
    'renewal_act': 'none',
    'current_honor_window': 'unchanged',
    'repair': 'ordinary-continuation'
}
receipt['renewal_scope_witness'] = {
    'witness_surface': 'OBLIGATION-LEDGER.json#OB-0143',
    'governed_obligation_surface': 'OBLIGATION-LEDGER.json#OB-0143',
    'prior_local_target': 'refresh burden scope',
    'current_refreshed_target': 'refresh burden scope',
    'renewal_scope_state_family': 'local-refresh',
    'repair': 'ordinary-continuation'
}
receipt['refresh_burden_scope_witness'] = {
    'id': 'RBSW-0150',
    'surface': NEW_DOC,
    'refresh_burden_scope_state': 'same-claim-burden-upgrade|bounded-scope-widening|scope-gated-generalization|mixed-refresh-burden-scope',
    'repair': 'keep-current|narrow-claim|widen-scope|issue-new-refresh-burden-scope-witness|quarantine-refresh-scope-governance'
}
write('REVISION-RECEIPT.json', json.dumps(receipt, indent=2) + '\n')
