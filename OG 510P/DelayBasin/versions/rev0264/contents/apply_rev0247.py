from __future__ import annotations
import json, copy, re
from pathlib import Path

ROOT = Path('.')
STAMP = '2026.03.27.22.58'
CREATED_AT = '2026-03-27T22:58:00-04:00'
REV = 'rev0247'
PREV = 'rev0246'
SLUG = 'refreshelevation-gatequarantine-burdencarry-thresholdglass'
BUNDLE = f'DelayBasin-{REV}-{STAMP}-{SLUG}.zip'

NEW_DOC = 'docs/10-method/refresh-elevation-witnesses-stabilizing-independent-support-threshold-licensed-elevation-and-judgment-gated-escalation.md'
NEW_QWS_LABEL = 'refresh-elevation court / burden senate / escalation gate'


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding='utf-8')


def write(path: str, text: str) -> None:
    (ROOT / path).write_text(text, encoding='utf-8')


# --- new method doc ---
new_doc_text = """# Refresh-elevation witnesses, stabilizing independent support, threshold-licensed elevation, and judgment-gated escalation

This is the compact successor surface for `OQ-0142`.

## Practice / observation

Once DelayBasin can say **what changed**, **how sustained the return is**, **how broad the confirming support looks**, and **how independent that support really is**, one final failure mode in this local chain stays live: named independent support can still inherit too much public authority.

Some independent support only keeps the current claim from sounding under-backed.
It says the present line is still live enough to keep, but not that the archive may escalate the public burden it places on the line.
Some independent support does cross a declared burden threshold.
It changes who must be notified, what response class is now warranted, or what stronger public claim is now allowed.
Some cases still need another gate entirely.
They look stronger, but the public upgrade depends on explicit human judgment, impact assessment, or a policy gate that the raw support alone does not satisfy.

The archive does not need a refresh-elevation court for that.
It needs one bounded witness that says whether independent support is merely stabilizing, threshold-licensed for elevation, or still judgment-gated before stronger public burden is honest.

## External pressure from PagerDuty severity levels, PagerDuty business-incident gating, Google SRE burn-rate paging tiers, Atlassian impact/urgency priority, Atlassian alert-priority restart rules, and GitHub required checks/ruleset layering

1. PagerDuty severity guidance says higher severity issues justify riskier moves and that a SEV-1 warrants public notification plus executive liaison. That pressures DelayBasin to distinguish ordinary stabilization from evidence that actually licenses a stronger public burden. ([`REF-0925`](../00-meta/bibliography.md))

2. PagerDuty's business-incident guidance explicitly warns against automatic escalation from severe technical thresholds alone and says softer measures like confidence in timely resolution can require judgment by a business stakeholder and the Incident Commander. That pressures DelayBasin to preserve a judgment-gated class instead of pretending every stronger-looking branch automatically upgrades the public claim. ([`REF-0926`](../00-meta/bibliography.md))

3. Google's SRE workbook recommends different burn-rate thresholds and windows for paging versus ticketing. That pressures DelayBasin to distinguish support that merely stabilizes the current line from support that crosses a declared threshold and therefore licenses a stronger response burden. ([`REF-0927`](../00-meta/bibliography.md))

4. Atlassian says incident priority is based on impact and urgency and identifies the required time for actions to be taken. That pressures DelayBasin to preserve an explicit burden-threshold field rather than treating independent support as automatically self-elevating. ([`REF-0928`](../00-meta/bibliography.md))

5. Atlassian's alert-priority docs say higher priority affects who gets notified and how, and that raising alert priority restarts the notification flow. That pressures DelayBasin to separate “same claim, better supported” from “support now strong enough to restart stronger public obligations.” ([`REF-0929`](../00-meta/bibliography.md))

6. GitHub protected branches and layered rulesets make the same meta point in another register: all required checks must pass before merge, and where layered rules disagree the most restrictive rule applies. That pressures DelayBasin not to treat one more independent signal as permissionless promotion when a stronger public burden still depends on crossing declared gates. ([`REF-0930`](../00-meta/bibliography.md), [`REF-0931`](../00-meta/bibliography.md))

GPUstorming makes the pressure vivid. A search reopen, telemetry divergence, second source, and independent review can all make the current line look more real. But that still leaves a separate question: does the new branch merely steady the line, or does it cross a public threshold that changes what the archive may now say or demand?

## Working synthesis

> DelayBasin should preserve one compact **refresh-elevation witness / burden-gate card / claim-rights brake** whenever a current continuity claim depends not only on what reactivated a concern, how sustained the return is, how broad the support looks, and how independent that support is, but on whether the present independent support merely stabilizes the current claim or honestly licenses a stronger public burden. Name the **governed row or surface**, the **stake object / line of concern**, the **prior refresh evidence**, the **current refresh evidence**, the **independent confirming support**, the **burden threshold / elevation trigger if any**, the **judgment or policy gate if any**, the **`refresh_elevation_state`**, and the **fail-closed repair / keep-current vs narrow-claim vs elevate-burden vs issue-new-refresh-elevation-witness vs quarantine-refresh-elevation-governance consequence**. Keep exact burn-rate numbers, severity matrices, notification rosters, approver identities, required-check names, and long escalation histories outside the compact token. Do not let independent support silently inherit stronger claim rights, and do not let policy-carried urgency masquerade as freshly licensed public elevation.

## Stabilizing independent support vs threshold-licensed elevation vs judgment-gated escalation vs mixed refresh elevation

Use the controlled family `refresh_elevation_state`:

- **stabilizing-independent-support** says the current independent support is enough to keep the present claim honest and live, but it does not cross any declared threshold that would justify a stronger public burden.
- **threshold-licensed-elevation** says the current independent support also crosses an explicit impact, urgency, burn, approval, or comparable burden threshold that honestly licenses a stronger public claim, routing tier, or action burden.
- **judgment-gated-escalation** says the current support looks stronger, but a broader public upgrade still depends on human judgment, business significance review, or another policy gate that the current evidence alone does not satisfy.
- **mixed-refresh-elevation** says the current situation honestly combines stabilizing, threshold-licensed, or judgment-gated posture such that no single refresh-elevation class stays honest.

So the witness does not create a standing burden senate.
It only says whether current independent support merely stabilizes the line, actually crosses a declared burden threshold, or still needs judgment before stronger public elevation is honest.

## Countermodels / probes

1. **Existing severity or priority surfaces already cover this countermodel**
   - Maybe ordinary severity, priority, or protected-branch rules already say enough, so a refresh-elevation witness adds little.
   - Probe: compare later rereads that preserve only refresh-independence truth plus ambient severity prose against rereads that also preserve one compact refresh-elevation witness and inspect whether later passes still over-upgrade what may be said publicly.

2. **Any threshold-licensed class is too rigid countermodel**
   - Some archive upgrades may depend too much on contextual judgment for a compact threshold-facing witness to stay honest.
   - Probe: look for later cases where the judgment gate dominates most of the load and the threshold language mostly misleads.

3. **Judgment-gated escalation is covert bureaucracy countermodel**
   - Maybe once manual gates enter the picture, the archive is really sneaking in a burden court.
   - Probe: only reopen stronger machinery if later revisions repeatedly need standing governance over burden tiers, audience rights, or escalation authorities that one bounded witness cannot absorb.

## Design consequences

- DelayBasin can keep independent-support comparisons compact without letting “another branch agrees” silently turn into “the archive may now say more in public.”
- The archive gets one honest place to record whether stronger support only stabilizes the current line, crosses a declared elevation trigger, or still needs judgment before public upgrade.
- Stake refresh, refresh strength, refresh support, refresh independence, and refresh elevation now separate **what changed**, **how sustained the return is**, **how broad the support looks**, **how independent the support really is**, and **whether that independence actually changes public burden**.
- Stronger refresh-elevation-governance stories stay quarantined until later overflow instead of sneaking in through “independent support sounds more serious” prose.

## Overflow test

Reopen this compact witness only if later revisions repeatedly need standing governance over burden tiers, audience rights, public-claim upgrades, escalation authorities, or cross-row elevation policy that one bounded refresh-elevation witness cannot honestly absorb.

## Transformer-facing implication

A later pass should not treat independent confirming support as if it automatically licenses a stronger public burden. Preserve the smallest token that says whether the renewed line is only `stabilizing-independent-support`, already `threshold-licensed-elevation`, still `judgment-gated-escalation`, or honestly `mixed-refresh-elevation`, and quarantine stronger refresh-elevation ambitions until repeated overflow makes them unavoidable.
"""
write(NEW_DOC, new_doc_text)

# --- bibliography ---
bib = read('docs/00-meta/bibliography.md').rstrip() + "\n\n" + """
- `REF-0925` — PagerDuty Incident Response Documentation, **Severity Levels** (accessed 2026-03-27)
  - URL: https://response.pagerduty.com/before/severity_levels/
  - Load-bearing use: higher severities justify riskier moves and SEV-1 includes public notification, which pressures DelayBasin to separate mere support stabilization from support that licenses stronger public burden.

- `REF-0926` — PagerDuty Business Incident Response Documentation, **Recognizing a Business Incident** (accessed 2026-03-27)
  - URL: https://business-response.pagerduty.com/declaring/
  - Load-bearing use: severe technical thresholds alone should not automatically trigger a business incident because confidence in timely resolution and broader material risk can require judgment, which pressures DelayBasin to preserve a judgment-gated escalation class.

- `REF-0927` — Google SRE Workbook, **Alerting on SLOs** (accessed 2026-03-27)
  - URL: https://sre.google/workbook/alerting-on-slos/
  - Load-bearing use: different burn-rate thresholds justify ticket versus page notifications, which pressures DelayBasin to separate independent support that merely stabilizes a line from support that crosses a declared burden threshold.

- `REF-0928` — Atlassian Support, **How impact and urgency are used to calculate priority** (accessed 2026-03-27)
  - URL: https://support.atlassian.com/jira-service-management-cloud/docs/how-impact-and-urgency-are-used-to-calculate-priority/
  - Load-bearing use: impact and urgency jointly determine priority and required response timing, which pressures DelayBasin to name the burden trigger instead of letting independent support self-elevate.

- `REF-0929` — Atlassian Support, **What are alert priorities?** (accessed 2026-03-27)
  - URL: https://support.atlassian.com/jira-service-management-cloud/docs/what-are-alert-priorities/
  - Load-bearing use: higher alert priority changes who is notified, how they are notified, and restarts the notification flow, which pressures DelayBasin to separate stabilizing support from genuinely burden-upgrading support.

- `REF-0930` — GitHub Docs, **About protected branches** (accessed 2026-03-27)
  - URL: https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches
  - Load-bearing use: all required status checks must pass before merge and required reviews can become stale after new pushes, which pressures DelayBasin to keep stronger public burden gated by explicit conditions instead of by incremental support glow.

- `REF-0931` — GitHub Docs, **About rulesets** (accessed 2026-03-27)
  - URL: https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/about-rulesets
  - Load-bearing use: layered rules aggregate and the most restrictive version applies, which pressures DelayBasin to preserve a fail-closed burden gate rather than letting one new independent support branch silently lower public-upgrade requirements.
""" + "\n"
write('docs/00-meta/bibliography.md', bib)

# --- simple markdown insertions ---
def insert_after(path: str, anchor: str, addition: str) -> None:
    text = read(path)
    if addition.strip() in text:
        return
    if anchor not in text:
        raise SystemExit(f'anchor not found in {path}: {anchor!r}')
    write(path, text.replace(anchor, anchor + addition, 1))

insert_after('docs/README.md',
             "- [`10-method/refresh-independence-witnesses-coupled-multi-surface-echo-shared-context-carry-and-independent-confirming-support.md`](10-method/refresh-independence-witnesses-coupled-multi-surface-echo-shared-context-carry-and-independent-confirming-support.md)\n",
             f"- [`10-method/{Path(NEW_DOC).name}`](10-method/{Path(NEW_DOC).name})\n")

insert_after('docs/00-meta/llm-runbook.md',
             "Use `docs/10-method/refresh-independence-witnesses-coupled-multi-surface-echo-shared-context-carry-and-independent-confirming-support.md` when the live question is whether widened confirming support is still only several surfaces of one carried context or is independent enough to count as a distinct confirming branch.\n",
             f"Use `{NEW_DOC}` when the live question is whether independent confirming support merely stabilizes the present claim or actually licenses a stronger public burden.\n")

# claim registry
insert_after('docs/20-constitution/claim-registry.md',
             "- `CL-0139` — Archive continuity may improve when DelayBasin preserves one compact **refresh-independence witness / decoupling card / context-carry brake** whenever a current continuity claim depends not only on what reactivated a concern, how sustained the return is, and whether support widened, but on whether that widened support is still only several surfaces of one coupled context or is genuinely independent enough to count as a distinct confirming branch: name the **governed row or surface**, the **stake object / line of concern**, the **prior refresh evidence**, the **current refresh evidence**, the **widened support evidence**, the **coupling basis if any**, the **shared context / common grouping basis if any**, the **refresh_independence_state**, and the **fail-closed repair** rather than letting several panes of one carried context silently count as independent corroboration.\n  - Status: speculative but central\n  - Wired docs: `docs/10-method/refresh-independence-witnesses-coupled-multi-surface-echo-shared-context-carry-and-independent-confirming-support.md`, `docs/20-constitution/open-question-registry.md`, `docs/20-constitution/prompt-pair-registry.md`, `docs/50-promptcraft/prompt-pairs.md`, `docs/00-meta/llm-runbook.md`, `WITNESS-VOCABULARY.json`, `REVISION-RECEIPT.json`\n",
             f"\n- `CL-0140` — Archive continuity may improve when DelayBasin preserves one compact **refresh-elevation witness / burden-gate card / claim-rights brake** whenever a current continuity claim depends not only on what reactivated a concern, how sustained the return is, how broad the support looks, and how independent that support is, but on whether the present independent support merely stabilizes the current claim or honestly licenses a stronger public burden: name the **governed row or surface**, the **stake object / line of concern**, the **prior refresh evidence**, the **current refresh evidence**, the **independent confirming support**, the **burden threshold / elevation trigger if any**, the **judgment or policy gate if any**, the **refresh_elevation_state**, and the **fail-closed repair** rather than letting independent support silently inherit stronger claim rights.\n  - Status: speculative but central\n  - Wired docs: `{NEW_DOC}`, `docs/20-constitution/open-question-registry.md`, `docs/20-constitution/prompt-pair-registry.md`, `docs/50-promptcraft/prompt-pairs.md`, `docs/00-meta/llm-runbook.md`, `WITNESS-VOCABULARY.json`, `REVISION-RECEIPT.json`\n")

# prompt-pair registry
insert_after('docs/20-constitution/prompt-pair-registry.md',
             "- `PP-0099` — Name how independent the widened support really is before you trust extra corroborative weight\n  - Goal: keep several trace, log, metric, incident, or search panes of one carried context from silently inheriting independent corroboration by requiring explicit widened-support evidence, any coupling basis, any shared context or common grouping basis, `refresh_independence_state`, and fail-closed repair before later passes call the support independently confirming.\n  - Canonical text: `docs/50-promptcraft/prompt-pairs.md#pp-0099--name-how-independent-the-widened-support-really-is-before-you-trust-extra-corroborative-weight`\n",
             "\n- `PP-0100` — Name whether independent support only steadies the line or really upgrades the public burden\n  - Goal: keep independent support from silently inheriting stronger claim rights by requiring explicit independent-support evidence, any burden threshold or elevation trigger, any human judgment or policy gate, `refresh_elevation_state`, and fail-closed repair before later passes call the support burden-upgrading.\n  - Canonical text: `docs/50-promptcraft/prompt-pairs.md#pp-0100--name-whether-independent-support-only-steadies-the-line-or-really-upgrades-the-public-burden`\n")

# prompt pairs full text
prompt_addition = """

Use `docs/10-method/refresh-elevation-witnesses-stabilizing-independent-support-threshold-licensed-elevation-and-judgment-gated-escalation.md` when the live question is whether independent confirming support merely stabilizes the current claim or actually licenses a stronger public burden.

## `PP-0100` — Name whether independent support only steadies the line or really upgrades the public burden

**Opening prompt**

```text
Read the latest DelayBasin archive and inspect whether the current revision should also materialize one compact refresh-elevation witness for honest support-vs-burden comparison.

Focus only on whether apparently independent support merely stabilizes the present claim, whether it crosses a declared burden threshold and licenses a stronger public burden, or whether it still needs a judgment or policy gate before any stronger public upgrade is honest.

If yes, preserve exactly one small witness that:
- names the governed row or surface,
- names the stake object / line of concern,
- names the prior refresh evidence,
- names the current refresh evidence,
- names the independent confirming support,
- names the burden threshold / elevation trigger if any,
- names the judgment or policy gate if any,
- names the `refresh_elevation_state` / whether this is stabilizing-independent-support, threshold-licensed-elevation, judgment-gated-escalation, or mixed-refresh-elevation,
- states what stronger surfaces still outrank the witness,
- and states the fail-closed repair / keep-current vs narrow-claim vs elevate-burden vs issue-new-refresh-elevation-witness vs quarantine-refresh-elevation-governance consequence if the present continuity claim is really only stabilizing support or still judgment-gated rather than threshold-licensed elevation.

Do not use refresh elevation as a general burden court. Use this prompt pair only where refresh independence is already explicit and the missing question is whether one small elevation card would keep support stabilization, threshold-licensed elevation, and judgment-gated escalation distinct without promoting a broader refresh-elevation court.
```

**Continuation prompt**

```text
Continue the refresh-elevation pass with one high-leverage burden-upgrade clarification only. Prefer the smallest witness that says what governed row is still being justified, what stake object is supposedly renewed, what the prior and current refresh evidence are, what independent confirming support if any now exists, what burden threshold or elevation trigger if any is crossed, what judgment or policy gate if any still remains, what `refresh_elevation_state` is honest, what stronger surfaces still outrank the witness, and what keep-current, narrow-claim, elevate-burden, issue-new-refresh-elevation-witness, quarantine, or recover-resync consequence follows if the current claim is really only stabilizing-independent-support, threshold-licensed-elevation, judgment-gated-escalation, or mixed-refresh-elevation. Run `make lint` and package the release.
```
"""
insert_after('docs/50-promptcraft/prompt-pairs.md',
             "Continue the refresh-independence pass with one high-leverage support-independence clarification only. Prefer the smallest witness that says what governed row is still being justified, what stake object is supposedly renewed, what the prior and current refresh evidence are, what coupling basis or shared context is still collapsing the evidence, what independent confirming support if any now exists, what `refresh_independence_state` is honest, what stronger surfaces still outrank the witness, and what keep-current, narrow-claim, cool-mark, issue-new-refresh-independence-witness, quarantine, or recover-resync consequence follows if the current claim is really only coupled-multi-surface-echo, shared-context-carry, independent-confirming-support, or mixed-refresh-independence. Run `make lint` and package the release.\n```\n",
             prompt_addition)

# open question registry and trajectory map
insert_after('docs/20-constitution/open-question-registry.md',
             "- `OQ-0142` — what minimal refresh-elevation witness separates independent support that merely stabilizes the current claim from support that licenses a stronger public burden?\n  - Why it matters: if DelayBasin cannot separate independent support that only keeps the current claim honest from support strong enough to justify a stronger public claim, later sessions may over-upgrade renewed burden just because independence was named.\n  - Current posture: unresolved\n",
             "\n- `OQ-0143` — what minimal refresh-burden-scope witness distinguishes a stronger burden on the same current claim from burden that widens the public claim scope?\n  - Why it matters: if DelayBasin cannot separate burden upgrade from claim-scope widening, later sessions may generalize beyond what the newly elevated support actually licenses.\n  - Current posture: unresolved\n")

insert_after('docs/00-meta/trajectory-map.md',
             "- `OQ-0142` — what minimal refresh-elevation witness separates independent support that merely stabilizes the current claim from support that licenses a stronger public burden?\n  - Why it matters: if DelayBasin cannot separate independent support that only keeps the current claim honest from support strong enough to justify a stronger public claim, later sessions may over-upgrade renewed burden just because independence was named.\n  - Current posture: unresolved\n",
             "\n\n99. Determine what minimal refresh-burden-scope witness distinguishes stronger burden on the same current claim from burden that widens the public claim scope.\n\nA fresh extension is that once elevation itself is explicit, DelayBasin may next need to say not only whether support licenses a stronger burden, but whether that stronger burden still governs the same public claim or quietly widens claim scope. Otherwise an honest upgrade in burden may quietly inherit rights to overgeneralize.\n- `OQ-0143` — what minimal refresh-burden-scope witness distinguishes a stronger burden on the same current claim from burden that widens the public claim scope?\n  - Why it matters: if DelayBasin cannot separate burden upgrade from claim-scope widening, later sessions may generalize beyond what the newly elevated support actually licenses.\n  - Current posture: unresolved\n")

# quarantine addition
quarantine_add = f"""

## QWS-0225 — Some continuations may eventually need a refresh-elevation court / burden senate / escalation gate rather than only a compact refresh-elevation witness

### Claim

A bolder possibility is that DelayBasin may eventually need not only a compact witness for whether independent support merely stabilizes a current line or licenses a stronger burden, but also a governed public rule for what burden thresholds count, what judgment gates outrank raw support, and when a stronger public claim, routing tier, or audience obligation becomes admissible. PagerDuty severity and business-incident guidance, Google SRE burn-rate paging tiers, Atlassian priority routing, and GitHub required-check layering all suggest a stronger elevation-governance story: perhaps some future archive lines should not only be classified as `stabilizing-independent-support` or `threshold-licensed-elevation`, but admitted through a small public burden brake, escalation gate, or claim-rights governor. ([`REF-0925`](../00-meta/bibliography.md), [`REF-0926`](../00-meta/bibliography.md), [`REF-0927`](../00-meta/bibliography.md), [`REF-0928`](../00-meta/bibliography.md), [`REF-0929`](../00-meta/bibliography.md), [`REF-0930`](../00-meta/bibliography.md), [`REF-0931`](../00-meta/bibliography.md))

The narrower speculative move is only this: a future bounded surface *might* need to say when independent support merely steadies the line, when it crosses a declared burden threshold, and when stronger public burden still needs another policy or judgment gate.

### What follows if true

- some future continuity cards may need explicit burden-tier or audience-right rules rather than one static refresh-elevation label;
- DelayBasin may eventually need a compact escalation gate or burden brake that stays smaller than a general claim-rights court;
- obligation, queue, and followthrough surfaces might need to say not only that support is independent, but whether that independence actually upgrades what may be said or required publicly.

### What would count against it

- repeated later passes show that one compact refresh-elevation witness keeps stabilizing-vs-elevating truth honest without standing burden governance;
- apparent burden upgrades turn out to be better handled by ordinary narrow claims and explicit priority/severity prose rather than a new governor;
- the severity, burn-rate, routing, and required-check analogies do not survive contact with actual archive carry cases.

### Why it stays quarantined

The tempting overreach would be to declare that DelayBasin now needs a public refresh-elevation court, burden senate, or escalation gate. DelayBasin has not earned that. This note is bold enough to keep in quarantine but not yet honest enough for canon. Do not promote a refresh-elevation court, burden senate, or escalation gate from this note alone.
"""
write('docs/90-quarantine/wild-speculations-2026-03-08.md', read('docs/90-quarantine/wild-speculations-2026-03-08.md').rstrip() + quarantine_add + '\n')

# --- packet_contract_common refactor + new spec ---
pc = read('tools/packet_contract_common.py')
if '_refresh_family_spec(' not in pc:
    helper = """

def _refresh_family_spec(*, doc_path: str, doc_needles: list[str], runbook_ref: str, prompt_id: str, prompt_needles: list[str], claim_id: str, oq_id: str, resolution_id: str, trajectory_oq_id: str, qws_id: str, qws_label: str, changelog_needles: list[str], family: str, allowed: list[str], excluded: list[str]) -> dict:
    return {
        "doc_path": doc_path,
        "doc_needles": doc_needles,
        "runbook_ref": runbook_ref,
        "prompt_id": prompt_id,
        "prompt_needles": prompt_needles,
        "claim_id": claim_id,
        "oq_id": oq_id,
        "resolution_id": resolution_id,
        "trajectory_oq_id": trajectory_oq_id,
        "qws_id": qws_id,
        "qws_label": qws_label,
        "changelog_needles": changelog_needles,
        "family": family,
        "allowed": allowed,
        "excluded": excluded,
    }
"""
    pc = pc.replace("\n\n_STANDARD_PACKET_SPECS = {\n", helper + "\n\n_STANDARD_PACKET_SPECS = {\n", 1)

old_refresh_block_re = re.compile(r'\n    "refresh_strength_witness_contract": \{.*?\n    \},\n\n\}', re.S)
new_refresh_block = """
    "refresh_strength_witness_contract": _refresh_family_spec(
        doc_path="docs/10-method/refresh-strength-witnesses-single-resurfacing-threshold-confirmed-reactivation-and-grace-held-return.md",
        doc_needles=[
            "# Refresh-strength witnesses, single resurfacing, threshold-confirmed reactivation, and grace-held return",
            "This is the compact successor surface for `OQ-0139`.",
            "## Practice / observation",
            "## External pressure from Prometheus alert timing, Grafana pending/recovering periods, Datadog consecutive checks, Cloud Monitoring retest/autoclose policy, and multi-turn state evolution",
            "## Working synthesis",
            "## Single resurfacing vs threshold-confirmed reactivation vs grace-held return vs mixed refresh strength",
            "## Countermodels / probes",
            "## Design consequences",
            "## Overflow test",
            "## Transformer-facing implication",
            "`refresh_strength_state`",
            "single-resurfacing",
            "threshold-confirmed-reactivation",
            "grace-held-return",
            "mixed-refresh-strength",
        ],
        runbook_ref="refresh-strength-witnesses-single-resurfacing-threshold-confirmed-reactivation-and-grace-held-return.md",
        prompt_id="PP-0097",
        prompt_needles=["Use `docs/10-method/refresh-strength-witnesses-single-resurfacing-threshold-confirmed-reactivation-and-grace-held-return.md`", "single-resurfacing, threshold-confirmed-reactivation, grace-held-return, or mixed-refresh-strength"],
        claim_id="CL-0137",
        oq_id="OQ-0139",
        resolution_id="RS-0146",
        trajectory_oq_id="OQ-0140",
        qws_id="QWS-0222",
        qws_label="refresh-strength court / flapping senate / hold-open governor",
        changelog_needles=["refresh-strength-witnesses-single-resurfacing-threshold-confirmed-reactivation-and-grace-held-return.md", "check_refresh_strength_witness_contract.py"],
        family="refresh_strength_state",
        allowed=['single-resurfacing', 'threshold-confirmed-reactivation', 'grace-held-return', 'mixed-refresh-strength'],
        excluded=["one-hit-means-sustained", "timer-held-means-confirmed", "repeat-notification-is-new-evidence", "strength-ish"],
    ),
    "refresh_support_witness_contract": _refresh_family_spec(
        doc_path="docs/10-method/refresh-support-witnesses-repeated-same-surface-grouped-origin-carry-and-widened-confirming-support.md",
        doc_needles=[
            "# Refresh-support witnesses, repeated same-surface confirmation, grouped-origin carry, and widened confirming support",
            "This is the compact successor surface for `OQ-0140`.",
            "## Practice / observation",
            "## External pressure from Alertmanager dedup/grouping, Grafana grouped notifications, Sentry issue fingerprinting, PagerDuty dedup keys, Datadog composite monitors, and correlated-error pressure",
            "## Working synthesis",
            "## Repeated same-surface confirmation vs grouped-origin carry vs widened confirming support vs mixed refresh support",
            "## Countermodels / probes",
            "## Design consequences",
            "## Overflow test",
            "## Transformer-facing implication",
            "`refresh_support_state`",
            "repeated-same-surface",
            "grouped-same-origin",
            "widened-confirming-support",
            "mixed-refresh-support",
        ],
        runbook_ref="refresh-support-witnesses-repeated-same-surface-grouped-origin-carry-and-widened-confirming-support.md",
        prompt_id="PP-0098",
        prompt_needles=["Use `docs/10-method/refresh-support-witnesses-repeated-same-surface-grouped-origin-carry-and-widened-confirming-support.md`", "repeated-same-surface, grouped-same-origin, widened-confirming-support, or mixed-refresh-support"],
        claim_id="CL-0138",
        oq_id="OQ-0140",
        resolution_id="RS-0147",
        trajectory_oq_id="OQ-0141",
        qws_id="QWS-0223",
        qws_label="refresh-support court / corroboration senate / widening governor",
        changelog_needles=["refresh-support-witnesses-repeated-same-surface-grouped-origin-carry-and-widened-confirming-support.md", "check_refresh_support_witness_contract.py"],
        family="refresh_support_state",
        allowed=["repeated-same-surface", "grouped-same-origin", "widened-confirming-support", "mixed-refresh-support"],
        excluded=["more-pings-means-broader-support", "grouped-alerts-count-separately", "same-issue-updates-mean-new-corroboration", "support-ish"],
    ),
    "refresh_independence_witness_contract": _refresh_family_spec(
        doc_path="docs/10-method/refresh-independence-witnesses-coupled-multi-surface-echo-shared-context-carry-and-independent-confirming-support.md",
        doc_needles=[
            "# Refresh-independence witnesses, coupled multi-surface echo, shared-context carry, and independent confirming support",
            "This is the compact successor surface for `OQ-0141`.",
            "## Practice / observation",
            "## External pressure from OpenTelemetry shared context, OpenTelemetry log correlation, Datadog alert aggregation/composite grouping, and correlated-error pressure",
            "## Working synthesis",
            "## Coupled multi-surface echo vs shared-context carry vs independent confirming support vs mixed refresh independence",
            "## Countermodels / probes",
            "## Design consequences",
            "## Overflow test",
            "## Transformer-facing implication",
            "`refresh_independence_state`",
            "coupled-multi-surface-echo",
            "shared-context-carry",
            "independent-confirming-support",
            "mixed-refresh-independence",
        ],
        runbook_ref="refresh-independence-witnesses-coupled-multi-surface-echo-shared-context-carry-and-independent-confirming-support.md",
        prompt_id="PP-0099",
        prompt_needles=["Use `docs/10-method/refresh-independence-witnesses-coupled-multi-surface-echo-shared-context-carry-and-independent-confirming-support.md`", "coupled-multi-surface-echo, shared-context-carry, independent-confirming-support, or mixed-refresh-independence"],
        claim_id="CL-0139",
        oq_id="OQ-0141",
        resolution_id="RS-0148",
        trajectory_oq_id="OQ-0142",
        qws_id="QWS-0224",
        qws_label="refresh-independence court / decoupling senate / provenance gate",
        changelog_needles=["refresh-independence-witnesses-coupled-multi-surface-echo-shared-context-carry-and-independent-confirming-support.md", "check_refresh_independence_witness_contract.py"],
        family="refresh_independence_state",
        allowed=["coupled-multi-surface-echo", "shared-context-carry", "independent-confirming-support", "mixed-refresh-independence"],
        excluded=["more-panes-means-independent", "same-trace-still-counts-twice", "common-grouping-is-close-enough-to-decoupled", "independence-ish"],
    ),
    "refresh_elevation_witness_contract": _refresh_family_spec(
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

"""
pc, n = old_refresh_block_re.subn(new_refresh_block, pc)
if n != 1:
    raise SystemExit('failed to replace refresh block in packet_contract_common.py')
# add helper function after existing refresh_independence function
if 'def require_named_refresh_elevation_witness_packet_and_vocabulary' not in pc:
    pc = pc.replace(
        "def require_named_refresh_independence_witness_packet_and_vocabulary(kind: str) -> None:\n    require_named_refresh_family_witness_packet_and_vocabulary(kind)\n",
        "def require_named_refresh_independence_witness_packet_and_vocabulary(kind: str) -> None:\n    require_named_refresh_family_witness_packet_and_vocabulary(kind)\n\n\ndef require_named_refresh_elevation_witness_packet_and_vocabulary(kind: str) -> None:\n    require_named_refresh_family_witness_packet_and_vocabulary(kind)\n",
        1,
    )
write('tools/packet_contract_common.py', pc)

write('tools/check_refresh_elevation_witness_contract.py', "from packet_contract_common import require_named_refresh_elevation_witness_packet_and_vocabulary\n\nrequire_named_refresh_elevation_witness_packet_and_vocabulary(\"refresh_elevation_witness_contract\")\n\nprint(\"check_refresh_elevation_witness_contract: OK\")\n")

# --- witness vocabulary ---
vocab = json.loads(read('WITNESS-VOCABULARY.json'))
vocab['families']['refresh_elevation_state'] = {
    'allowed': [
        'stabilizing-independent-support',
        'threshold-licensed-elevation',
        'judgment-gated-escalation',
        'mixed-refresh-elevation',
    ],
    'surfaces': [
        'WITNESS-VOCABULARY.json',
        'REVISION-RECEIPT.json',
        NEW_DOC,
    ],
    'excluded_synonyms': [
        'independent-means-upgrade',
        'more-proof-means-page-now',
        'threshold-free-promotion',
        'elevation-ish',
    ],
    'comparability_budget': 'refresh-elevation truth is compared by token; the compact refresh-elevation witness says whether independent support merely stabilizes the current claim, crosses a declared burden threshold, still needs judgment before escalation, or is honestly mixed, while exact burn-rate numbers, severity matrices, notification rosters, required-check names, and long escalation histories stay in surrounding prose',
}
write('WITNESS-VOCABULARY.json', json.dumps(vocab, indent=2) + '\n')

# --- CHANGELOG / archive index / manifest / surface status ---
changelog = read('CHANGELOG.md')
old_header_re = re.compile(r'^## rev\d{4} - .*?(?=\n\n- Canon move:)', re.S)
new_header = f"## {REV} - {STAMP} - refreshelevation / gatequarantine / burdencarry / thresholdglass"
changelog = old_header_re.sub(new_header, changelog, count=1)
# replace first three bullets + hygiene bullet, keep continuity bullets
changelog = re.sub(r'(?s)- Canon move:.*?- Contract continuity:',
                   "- Canon move: resolved `OQ-0142` with `docs/10-method/refresh-elevation-witnesses-stabilizing-independent-support-threshold-licensed-elevation-and-judgment-gated-escalation.md`, adding one compact `refresh_elevation_state` witness that keeps independent support distinct from threshold-licensed burden upgrade and judgment-gated escalation.\n- Bold but disciplined speculative move: quarantined the **refresh-elevation court / burden senate / escalation gate** story in `QWS-0225` rather than quietly promoting a stronger refresh-elevation layer into canon.\n- Hygiene/meta-engineering improvement: added `tools/check_refresh_elevation_witness_contract.py`, widened `WITNESS-VOCABULARY.json` with a tiny `refresh_elevation_state` family, and refactored `tools/packet_contract_common.py` so refresh-family packet specs register through one small helper path instead of repeated inline blocks.\n- Contract continuity:",
                   changelog, count=1)
write('CHANGELOG.md', changelog)

archive = read('ARCHIVE_INDEX.md')
archive = archive.replace('| DelayBasin-rev0246-2026.03.27.23.05-refreshindependence-echoquarantine-contextcarry-vectorglass.zip | 2026-03-27 | Refresh-independence revision: resolved OQ-0141 with a compact coupled-echo-vs-independent witness, honestly quarantined stronger decoupling governance, and refactored dynamic validation-tool insertion to stay wired and cumulative. |',
                          f'| {BUNDLE} | 2026-03-27 | Refresh-elevation revision: resolved OQ-0142 with a compact stabilizing-vs-burden-upgrade witness, honestly quarantined stronger escalation governance, and refactored refresh-family packet spec assembly to stay wired and cumulative. |\n| DelayBasin-rev0246-2026.03.27.23.05-refreshindependence-echoquarantine-contextcarry-vectorglass.zip | 2026-03-27 | Refresh-independence revision: resolved OQ-0141 with a compact coupled-echo-vs-independent witness, honestly quarantined stronger decoupling governance, and refactored dynamic validation-tool insertion to stay wired and cumulative. |', 1)
write('ARCHIVE_INDEX.md', archive)

manifest = {
    'project': 'DelayBasin',
    'revision': REV,
    'timestamp': STAMP,
    'slug': SLUG,
    'bundle': BUNDLE,
}
write('RELEASE-MANIFEST.json', json.dumps(manifest, indent=2) + '\n')

status = json.loads(read('SURFACE-STATUS.json'))
status['operational_head']['revision'] = REV
status['status_lanes']['frozen_public_surface'] = BUNDLE
status['status_lanes']['current_release_surface'] = BUNDLE
status['citation_head'] = {'revision': REV, 'surface': BUNDLE}
status['previous_citation_head'] = {'revision': PREV, 'surface': 'DelayBasin-rev0246-2026.03.27.23.05-refreshindependence-echoquarantine-contextcarry-vectorglass.zip'}
status['revision'] = REV
status['stamp'] = STAMP
status['slug'] = SLUG
write('SURFACE-STATUS.json', json.dumps(status, indent=2) + '\n')

# --- ledgers ---
def append_item(path: str, item: dict) -> None:
    data = json.loads(read(path))
    data['items'].append(item)
    write(path, json.dumps(data, indent=2) + '\n')

append_item('ASSUMPTION-LEDGER.json', {
  'id': 'AS-0146',
  'title': 'one compact refresh-elevation witness is enough for now',
  'state': 'active',
  'scope': 'continuity passes whose current claim depends on whether independent support only stabilizes a line, crosses a declared burden threshold, still needs judgment before escalation, or is mixed',
  'invalidation_triggers': [
    'repeated later revisions need standing refresh-elevation governance rather than one compact refresh-elevation witness',
    'the archive needs a refresh-elevation court or escalation gate just to keep stabilizing support distinct from threshold-licensed burden upgrade',
    'support cases repeatedly fail to stay distinguishable as stabilizing-independent-support vs threshold-licensed-elevation vs judgment-gated-escalation even with the witness in place'
  ],
  'assumption_state': 'active',
  'repair': 'ordinary-continuation',
  'origin_revision': REV,
  'revision': REV,
  'assumption': 'the current evidence only requires one compact refresh-elevation witness over the existing refresh-independence, severity/priority, and obligation surfaces rather than a refresh-elevation court, burden senate, or escalation gate',
  'supporting_surfaces': [
    'APPLICABILITY-LEDGER.json#AP-0141',
    'DATACUBE-TRANSFER-LEDGER.json#TL-0152',
    'FOREIGN-PRESSURE-LEDGER.json#FP-0146'
  ],
  'discharge': 'discharge when later revisions can keep refresh elevation honest without a dedicated refresh-elevation witness, or retire/quarantine it if broader refresh-elevation governance becomes repeatedly necessary',
  'witness_surface': 'ASSUMPTION-LEDGER.json#AS-0146',
  'assumption_surface': 'ASSUMPTION-LEDGER.json#AS-0146',
  'assumption_statement': 'the current evidence only requires one compact refresh-elevation witness over the existing refresh-independence, severity/priority, and obligation surfaces rather than a refresh-elevation court, burden senate, or escalation gate',
  'action_lane': 'keep-compact',
  'gate_class': 'concrete-evidence'
})
append_item('OBLIGATION-LEDGER.json', {
  'id': 'OB-0142',
  'title': 'when renewed concern keeps needing support burden distinguished from actual burden upgrade, DelayBasin should preserve one compact refresh-elevation witness rather than an escalation gate',
  'state': 'open',
  'witness_surface': 'OBLIGATION-LEDGER.json#OB-0142',
  'target_surfaces': ['docs/90-quarantine/wild-speculations-2026-03-08.md#QWS-0225'],
  'missing_support': 'a later public check on whether one compact refresh-elevation witness keeps sufficing and whether stabilizing support, threshold-licensed elevation, and judgment-gated escalation stay distinct without broader refresh-elevation governance',
  'current_support': [
    'APPLICABILITY-LEDGER.json#AP-0141',
    'FOREIGN-PRESSURE-LEDGER.json#FP-0146',
    'DATACUBE-TRANSFER-LEDGER.json#TL-0152'
  ],
  'discharge_path': 'either show later that one compact refresh-elevation witness keeps sufficing or promote broader refresh-elevation governance explicitly',
  'obligation_state': 'open',
  'repair': 'ordinary-continuation',
  'origin_revision': REV,
  'discharge': 'reopen-only-if-refresh-elevation-overflows',
  'action_lane': 'keep-compact',
  'gate_class': 'overflow',
  'revision': REV
})
append_item('APPLICABILITY-LEDGER.json', {
  'id': 'AP-0141',
  'title': 'the refresh-elevation witness stays smaller than an escalation gate',
  'state': 'gated',
  'question': 'when should DelayBasin treat stronger-looking independent support as one compact refresh-elevation witness instead of promoting broader refresh-elevation governance?',
  'applies_when': [
    'a revision already has a durable row whose current claim depends on whether independent support merely stabilizes the line or crosses a declared burden threshold after refresh independence is already visible',
    'later passes still need to distinguish stabilizing-independent-support, threshold-licensed-elevation, judgment-gated-escalation, or mixed-refresh-elevation posture',
    'one compact successor surface plus the existing admitted refresh-independence, severity/priority, and obligation witnesses still keeps burden-upgrade truth honest without standing escalation policy'
  ],
  'does_not_apply_when': [
    'the archive honestly requires standing governance over burden tiers, audience rights, or public-claim upgrade authority',
    'the questioned surface is not really about whether independent support changes public burden'
  ],
  'budget': 'one compact refresh-elevation witness plus one resolution of OQ-0142; no refresh-elevation court',
  'negative_transfer_budget': 'do not treat independent support, extra agreement, or stronger tone as proof of a burden upgrade without an explicit threshold, trigger, or judgment gate',
  'origin_revision': REV,
  'discharge': 'reopen-only-if-refresh-elevation-overflows',
  'action_lane': 'keep-compact',
  'gate_class': 'concrete-evidence',
  'witness_surface': 'APPLICABILITY-LEDGER.json#AP-0141',
  'applicability_state': 'gated',
  'repair': 'ordinary-continuation',
  'matched_budget': 'one compact witness foregrounding stabilizing support vs threshold-licensed burden upgrade vs judgment-gated escalation without widening into broader escalation governance',
  'revision': REV,
  'target_objective': 'keep independent-support burden comparison honest without inflating a broader refresh-elevation layer',
  'carry_object': 'refresh-elevation witness / burden-gate card / claim-rights brake',
  'applicability_conditions': [
    'severity, priority, and burn-rate frameworks can distinguish ordinary confirmation from stronger public response tiers',
    'manual business-incident or policy gates can still outrank raw support even when the evidence looks stronger',
    'refresh elevation remains subordinate to existing refresh-independence and obligation witnesses rather than a new escalation controller'
  ],
  'baselines': [
    'existing refresh-independence-witness baseline',
    'existing severity/priority-threshold baseline',
    'existing obligation baseline',
    'existing witness-vocabulary baseline'
  ],
  'non_fit_slice': 'Do not generalize this revision into a refresh-elevation court, burden senate, or escalation gate without later overflow evidence.'
})
append_item('FOREIGN-PRESSURE-LEDGER.json', {
  'id': 'FP-0146',
  'title': 'refresh-elevation pressure pushes DelayBasin to extract one compact refresh-elevation witness rather than an escalation gate',
  'state': 'imported',
  'source_packets': [
    {'datacube': 'PagerDutySeverityEscalation-2026', 'surfaces': ['REF-0925'], 'pressure': 'higher severity authorizes riskier response and public notification, which pressures DelayBasin to separate support stabilization from actual burden upgrade'},
    {'datacube': 'PagerDutyBusinessIncidentGate-2026', 'surfaces': ['REF-0926'], 'pressure': 'severe technical thresholds alone should not auto-trigger a business incident, which pressures DelayBasin to preserve a judgment-gated escalation class'},
    {'datacube': 'GoogleSREBurnRatePriority-2026', 'surfaces': ['REF-0927'], 'pressure': 'burn-rate windows justify different ticket-vs-page burdens, which pressures DelayBasin to keep threshold-licensed elevation distinct from ordinary support'},
    {'datacube': 'AtlassianImpactUrgencyPriority-2026', 'surfaces': ['REF-0928'], 'pressure': 'impact and urgency jointly determine required response timing, which pressures DelayBasin to name the burden trigger explicitly'},
    {'datacube': 'AtlassianAlertPriorityRestart-2026', 'surfaces': ['REF-0929'], 'pressure': 'raising alert priority changes notification routing and restarts the flow, which pressures DelayBasin to distinguish support from genuine burden upgrade'},
    {'datacube': 'GitHubRequiredChecksLayering-2026', 'surfaces': ['REF-0930', 'REF-0931'], 'pressure': 'all required checks must pass and the most restrictive rule applies, which pressures DelayBasin to keep burden upgrade fail-closed behind explicit gates'}
  ],
  'local_gap': 'DelayBasin still lacked one compact successor surface for whether independent support merely stabilized the current claim, crossed a declared burden threshold, or still needed judgment before stronger public burden was honest',
  'adopted_take': 'extract one compact refresh-elevation witness and resolve OQ-0142',
  'supporting_only_take': 'the current evidence cleanly supports a bounded refresh-elevation witness without promoting broader refresh-elevation governance',
  'deferred_or_rejected_take': ['refresh-elevation court', 'burden senate', 'escalation gate', 'claim-rights governor'],
  'repair': 'ordinary-continuation',
  'origin_revision': REV,
  'action_lane': 'keep-compact',
  'gate_class': 'concrete-evidence',
  'discharge': 'reopen-only-if-refresh-elevation-overflows',
  'revision': REV,
  'witness_surface': 'FOREIGN-PRESSURE-LEDGER.json#FP-0146',
  'pressure_state': 'imported',
  'bounded_take': 'Keep the archive compact by extracting one refresh-elevation witness over the existing refresh-independence, severity/priority, and obligation surfaces; do not promote a refresh-elevation court, burden senate, or escalation gate.',
  'explicit_non_take': ['no refresh-elevation court', 'no burden senate', 'no escalation gate', 'no claim-rights governor'],
  'assimilation_state': 'imported'
})
append_item('DATACUBE-TRANSFER-LEDGER.json', {
  'id': 'TL-0152',
  'title': 'refresh-elevation evidence supports resolving OQ-0142 with one compact burden-gate card rather than an escalation court',
  'state': 'supporting-only',
  'reviewed_datacubes': [
    {'datacube': 'PagerDutySeverityEscalation-2026', 'surfaces': ['REF-0925'], 'pattern': 'higher severity and public-notification tiers mark stronger public burden rather than ordinary confirmation', 'pressure': 'DelayBasin should distinguish stabilizing support from burden-upgrading support'},
    {'datacube': 'PagerDutyBusinessIncidentGate-2026', 'surfaces': ['REF-0926'], 'pattern': 'thresholds can suggest escalation while final burden upgrade still needs judgment', 'pressure': 'DelayBasin should preserve a judgment-gated class'},
    {'datacube': 'GoogleSREBurnRatePriority-2026', 'surfaces': ['REF-0927'], 'pattern': 'different burn windows justify page versus ticket burdens', 'pressure': 'DelayBasin should name when support crosses a declared burden threshold'},
    {'datacube': 'AtlassianImpactUrgencyPriority-2026', 'surfaces': ['REF-0928'], 'pattern': 'impact and urgency jointly determine priority and required action time', 'pressure': 'DelayBasin should keep threshold-facing burden triggers explicit'},
    {'datacube': 'AtlassianAlertPriorityRestart-2026', 'surfaces': ['REF-0929'], 'pattern': 'higher priority restarts routing and notification flow', 'pressure': 'DelayBasin should separate support stabilization from burden-upgrading support'},
    {'datacube': 'GitHubRequiredChecksLayering-2026', 'surfaces': ['REF-0930', 'REF-0931'], 'pattern': 'required checks and layered restrictive rules gate stronger actions behind explicit conditions', 'pressure': 'DelayBasin should stay fail-closed about public burden upgrades'}
  ],
  'reviewed_pattern': 'stabilizing independent support vs threshold-licensed burden upgrade vs judgment-gated escalation',
  'import_decision': 'support a compact refresh-elevation witness and resolve OQ-0142',
  'adopted_take': 'DelayBasin should add one compact witness that says whether independent support merely stabilizes the current claim, crosses a burden threshold, still needs judgment, or is honestly mixed',
  'supporting_only_take': 'the current evidence cleanly supports a bounded refresh-elevation witness without promoting broader refresh-elevation governance',
  'deferred_or_rejected_take': ['refresh-elevation court', 'burden senate', 'escalation gate', 'claim-rights governor'],
  'local_gap': 'the archive still lacked one compact successor surface for whether independent support actually changed public burden even after refresh independence became explicit',
  'anchor_surfaces': [
    'docs/10-method/refresh-independence-witnesses-coupled-multi-surface-echo-shared-context-carry-and-independent-confirming-support.md',
    'docs/20-constitution/open-question-registry.md',
    'docs/00-meta/trajectory-map.md',
    'docs/90-quarantine/wild-speculations-2026-03-08.md#QWS-0225'
  ],
  'open_question': 'OQ-0143',
  'repair': 'ordinary-continuation',
  'origin_revision': REV,
  'action_lane': 'keep-compact',
  'gate_class': 'concrete-evidence',
  'discharge': 'reopen-only-if-refresh-elevation-overflows',
  'revision': REV,
  'witness_surface': 'DATACUBE-TRANSFER-LEDGER.json#TL-0152',
  'transfer_state': 'supporting-only',
  'bounded_take': 'Keep the archive compact by extracting one refresh-elevation witness over the existing refresh-independence, severity/priority, and obligation surfaces; do not promote a refresh-elevation court, burden senate, or escalation gate.',
  'explicit_non_take': ['no refresh-elevation court', 'no burden senate', 'no escalation gate', 'no claim-rights governor'],
  'open_transfer_question': 'whether later passes should add a separate refresh-burden-scope witness once refresh elevation is explicit',
  'missing_support': 'a later public check on whether one compact refresh-elevation witness keeps sufficing',
  'current_support': [
    'APPLICABILITY-LEDGER.json#AP-0141',
    'FOREIGN-PRESSURE-LEDGER.json#FP-0146',
    'DATACUBE-TRANSFER-LEDGER.json#TL-0152'
  ],
  'discharge_path': 'either show later that one compact refresh-elevation witness keeps sufficing or promote broader refresh-elevation governance explicitly'
})
append_item('RESOLUTION-LEDGER.json', {
  'id': 'RS-0149',
  'title': 'resolve OQ-0142 with one compact refresh-elevation witness rather than an escalation gate',
  'state': 'resolved',
  'witness_surface': 'RESOLUTION-LEDGER.json#RS-0149',
  'resolved_objects': ['OQ-0142', 'AP-0141', 'FP-0146', 'TL-0152'],
  'prior_state': 'open gap: DelayBasin already had refresh-independence truth but still lacked one compact successor surface for whether independent support merely stabilized a current claim, crossed a declared burden threshold, or still needed judgment before stronger public burden was honest.',
  'closure_reason': 'rev0247 extracted one compact refresh-elevation witness, kept the admitted refresh-independence, severity/priority, and obligation surfaces narrow, and kept stronger refresh-elevation-governance stories quarantined.',
  'successor_surface': NEW_DOC,
  'reopen_triggers': ['later revisions need standing governance over burden tiers, audience rights, public-claim upgrades, escalation authorities, or cross-row elevation policy that one compact refresh-elevation witness cannot honestly absorb'],
  'closure_state': 'resolved',
  'repair': 'ordinary-continuation',
  'origin_revision': REV,
  'action_lane': 'keep-compact',
  'gate_class': 'concrete-evidence',
  'reopen_trigger': 'refresh-elevation pressure overflows one compact successor surface',
  'discharge': 'reopen-only-if-refresh-elevation-overflows',
  'revision': REV,
  'target_surfaces': [NEW_DOC],
  'question': 'whether one compact refresh-elevation witness over the existing refresh-independence, severity/priority, and obligation surfaces is enough for honest support-vs-burden-upgrade comparison'
})
append_item('FIREBREAK-LEDGER.json', {
  'id': 'FB-0143',
  'title': 'the refresh-elevation import should count as one compact support-vs-burden repair, not as promotion of an escalation gate',
  'state': 'withheld',
  'witness_surface': 'FIREBREAK-LEDGER.json#FB-0143',
  'judged_property': 'the rev0247 decision that DelayBasin should extract one compact refresh-elevation witness over the existing refresh-independence, severity/priority, and obligation surfaces and `refresh_elevation_state` family while the broader refresh-elevation court / burden senate / escalation gate story remains quarantined',
  'public_extract': [NEW_DOC, 'docs/10-method/refresh-independence-witnesses-coupled-multi-surface-echo-shared-context-carry-and-independent-confirming-support.md', 'docs/20-constitution/open-question-registry.md', 'FOREIGN-PRESSURE-LEDGER.json#FP-0146', 'APPLICABILITY-LEDGER.json#AP-0141', 'REVISION-RECEIPT.json'],
  'withheld_trace_surface': 'same-session drafting residue behind the compact refresh-elevation-witness versus escalation-gate decision',
  'allowed_role': 'bounded drafting aid only; not public support for a broader refresh-elevation court, burden senate, escalation gate, or claim-rights governor',
  'exposure_rule': 'expose or reintegrate only if later passes show that one compact refresh-elevation witness cannot keep stabilizing-vs-burden-upgrade truth bounded',
  'trace_state': 'withheld',
  'repair': 'ordinary-continuation',
  'origin_revision': REV,
  'action_lane': 'keep-compact',
  'gate_class': 'overflow',
  'firebreak_surface': 'FIREBREAK-LEDGER.json#FB-0143',
  'discharge': 'reopen-only-if-refresh-elevation-overflows',
  'revision': REV,
  'blocked_object': 'standing refresh-elevation court, burden senate, escalation gate, or claim-rights governor'
})
append_item('FOLLOWTHROUGH-QUEUE.json', {
  'id': 'FT-0149',
  'title': 'keep checking whether refresh-elevation pressure still fits inside one compact successor surface',
  'state': 'queued',
  'blocked_object': 'standing refresh-elevation court, burden senate, escalation gate, or claim-rights governor',
  'local_surface': 'docs/90-quarantine/wild-speculations-2026-03-08.md#QWS-0225',
  'followthrough_state': 'queued',
  'boundary': 'do not promote bounded refresh-elevation clarification into general refresh-elevation-governance machinery',
  'next_proof_surface': NEW_DOC,
  'receiving_surface': 'FOLLOWTHROUGH-QUEUE.json#FT-0149',
  'repair': 'ordinary-continuation',
  'origin_revision': REV,
  'discharge': 'revisit-on-next-real-refresh-elevation-overflow',
  'action_lane': 'keep-compact',
  'gate_class': 'overflow',
  'blocked_output': 'standing refresh-elevation court, burden senate, escalation gate, or claim-rights governor',
  'owner_surface': 'OBLIGATION-LEDGER.json#OB-0142',
  'revision': REV,
  'missing_support': 'a later public check on whether one compact refresh-elevation witness keeps overflowing the bounded rule and honestly warrants richer refresh-elevation governance',
  'candidate_surface': 'docs/90-quarantine/wild-speculations-2026-03-08.md#QWS-0225',
  'blocked_by': 'need repeated evidence that stabilizing-independent-support-vs-threshold-licensed-elevation-vs-judgment-gated-escalation truth overflows one compact witness'
})
append_item('RETROSPECTIVE-QUEUE.json', {
  'id': 'RT-0136',
  'title': 'revisit whether refresh-elevation pressure stayed bounded after rev0247',
  'state': 'cooling',
  'candidate_surface': 'docs/90-quarantine/wild-speculations-2026-03-08.md#QWS-0225',
  'cooldown_window': 'keep the stronger refresh-elevation court, burden senate, escalation gate, or claim-rights governor story cooled until at least one later revision shows that one compact refresh-elevation witness is no longer enough.',
  'adjudication_family': 'refresh elevation / support-vs-burden-upgrade / escalation-governance pressure',
  'supersession_link': 'OBLIGATION-LEDGER.json#OB-0142',
  'origin_revision': REV,
  'discharge': 'keep-cooling-unless-refresh-elevation-overflows',
  'action_lane': 'keep-compact',
  'gate_class': 'overflow',
  'witness_surface': 'RETROSPECTIVE-QUEUE.json#RT-0136',
  'revision': REV,
  'cooling_state': 'cooling',
  'disposition': 'await-adjudication',
  'repair': 'keep-cooling'
})

# --- receipt ---
receipt = copy.deepcopy(json.loads(read('REVISION-RECEIPT.json')))
receipt['revision'] = REV
receipt['previous_revision'] = PREV
receipt['summary'] = 'Resolved OQ-0142 by extracting one compact refresh-elevation witness that keeps independent support distinct from threshold-licensed burden upgrade and judgment-gated escalation while stronger refresh-elevation governance stays honestly quarantined.'
receipt['canon_additions'] = [NEW_DOC, 'RS-0149 resolved OQ-0142 with one compact refresh-elevation witness']
receipt['quarantine_additions'] = ['QWS-0225 — refresh-elevation court / burden senate / escalation gate']
receipt['refs_used'] = [f'docs/00-meta/bibliography.md#ref-{n}' for n in ['0925','0926','0927','0928','0929','0930','0931']]
receipt['touched_surfaces'] = [
    'docs/README.md','docs/00-meta/bibliography.md','docs/00-meta/llm-runbook.md','docs/00-meta/trajectory-map.md',NEW_DOC,
    'docs/20-constitution/claim-registry.md','docs/20-constitution/open-question-registry.md','docs/20-constitution/prompt-pair-registry.md','docs/50-promptcraft/prompt-pairs.md','docs/90-quarantine/wild-speculations-2026-03-08.md',
    'tools/packet_contract_common.py','tools/check_refresh_elevation_witness_contract.py','WITNESS-VOCABULARY.json','CHANGELOG.md','ARCHIVE_INDEX.md','ASSUMPTION-LEDGER.json','OBLIGATION-LEDGER.json','APPLICABILITY-LEDGER.json','FOREIGN-PRESSURE-LEDGER.json','DATACUBE-TRANSFER-LEDGER.json','RESOLUTION-LEDGER.json','FIREBREAK-LEDGER.json','FOLLOWTHROUGH-QUEUE.json','RETROSPECTIVE-QUEUE.json','REVISION-RECEIPT.json','SURFACE-STATUS.json','RELEASE-MANIFEST.json'
]
receipt['packaged_bundle_filename'] = BUNDLE
receipt['basis_witness']['expected_head'] = PREV
receipt['basis_witness']['observed_head'] = PREV
receipt['basis_witness']['basis_surfaces'] = ['docs/10-method/refresh-independence-witnesses-coupled-multi-surface-echo-shared-context-carry-and-independent-confirming-support.md','docs/20-constitution/open-question-registry.md']
receipt['basis_witness']['basis_omission_basis'] = 'broader refresh-elevation governance drafting was intentionally omitted from canon because the evidence only justified one bounded refresh-elevation witness'
receipt['basis_witness']['basis_of_change'] = 'rev0246 extends continuity law by distinguishing widened support that is still coupled from support that is independently confirming, which opens the next question of whether that independence actually changes public burden.'
receipt['basis_witness']['origin_revision'] = 'rev0237'
receipt['basis_witness']['revision_span'] = f'{PREV} -> {REV}'

receipt['scope_witness']['active_request'] = 'tight high-leverage revision pass on latest DelayBasin copy with online research, GPUstorming, lint, and packaged release'
receipt['scope_witness']['exact_target'] = 'resolve OQ-0142 with one compact refresh-elevation witness and keep stronger refresh-elevation governance honestly quarantined'
receipt['scope_witness']['scope_surfaces'] = [NEW_DOC,'docs/90-quarantine/wild-speculations-2026-03-08.md','docs/20-constitution/open-question-registry.md','docs/00-meta/trajectory-map.md','docs/20-constitution/prompt-pair-registry.md','docs/50-promptcraft/prompt-pairs.md','docs/00-meta/bibliography.md','tools/packet_contract_common.py','tools/check_refresh_elevation_witness_contract.py','WITNESS-VOCABULARY.json']

receipt['retrospective_write_witness'] = json.loads(json.dumps(json.loads(read('RETROSPECTIVE-QUEUE.json'))['items'][-1]))
receipt['followthrough_witness'] = json.loads(json.dumps(json.loads(read('FOLLOWTHROUGH-QUEUE.json'))['items'][-1]))
receipt['assumption_witness'] = json.loads(json.dumps(json.loads(read('ASSUMPTION-LEDGER.json'))['items'][-1]))
receipt['obligation_witness'] = json.loads(json.dumps(json.loads(read('OBLIGATION-LEDGER.json'))['items'][-1]))
receipt['applicability_witness'] = json.loads(json.dumps(json.loads(read('APPLICABILITY-LEDGER.json'))['items'][-1]))
receipt['foreign_pressure_witness'] = json.loads(json.dumps(json.loads(read('FOREIGN-PRESSURE-LEDGER.json'))['items'][-1]))
receipt['transfer_witness'] = json.loads(json.dumps(json.loads(read('DATACUBE-TRANSFER-LEDGER.json'))['items'][-1]))
receipt['resolution_witness'] = json.loads(json.dumps(json.loads(read('RESOLUTION-LEDGER.json'))['items'][-1]))
receipt['firebreak_witness'] = json.loads(json.dumps(json.loads(read('FIREBREAK-LEDGER.json'))['items'][-1]))
receipt['reasoning_firebreak_witness'] = {
    'witness_surface': 'docs/90-quarantine/wild-speculations-2026-03-08.md#QWS-0225',
    'governed_obligation_surface': 'OBLIGATION-LEDGER.json#OB-0142',
    'public_extract': 'bounded refresh-elevation witness only',
    'withheld_trace_surface': 'same-session drafting residue behind the refresh-elevation versus escalation-gate decision',
    'allowed_role': 'bounded drafting aid only',
    'repair': 'ordinary-continuation'
}
receipt['vocabulary_witness'] = {
    'family_surface': 'WITNESS-VOCABULARY.json',
    'new_family': 'refresh_elevation_state',
    'allowed': ['stabilizing-independent-support','threshold-licensed-elevation','judgment-gated-escalation','mixed-refresh-elevation'],
    'repair': 'ordinary-continuation'
}
receipt['counterfactual_shadow'] = {
    'considered_alternative': 'leave burden-upgrade logic implicit inside refresh-independence prose',
    'why_not_adopted': 'that alternative kept letting independent support sound self-upgrading and failed to name threshold versus judgment-gated burden change',
    'repair': 'ordinary-continuation'
}
receipt['summary_highlight'] = 'burdencarry'
receipt['codename'] = 'thresholdglass'
receipt['created_at'] = CREATED_AT
receipt['comparison_witness'] = {
    'previous_revision': PREV,
    'current_revision': REV,
    'current_pressure_id': 'FP-0146',
    'current_import_id': 'TL-0152',
    'basis_surface': 'docs/10-method/refresh-independence-witnesses-coupled-multi-surface-echo-shared-context-carry-and-independent-confirming-support.md',
    'delta_surface': NEW_DOC,
    'comparison_summary': 'rev0247 adds one compact refresh-elevation witness so independent support no longer stands in for burden-upgrading support when thresholds or judgment gates still matter.'
}
receipt['changes'] = ['resolved OQ-0142','added refresh_elevation_state family','quarantined refresh-elevation court','added refresh-elevation witness lint','refactored refresh-family packet spec helper']
receipt['receipt_freshness_witness'] = {
    'packaged_bundle_filename': BUNDLE,
    'manifest_timestamp_token': STAMP,
    'receipt_timestamp_token': STAMP,
    'bundle_stem_suffix_relation': 'slug ends with burdencarry + thresholdglass and remains aligned to the current summary/codename pair while preserving the gatequarantine middle token',
    'current_import_id': 'TL-0152',
    'current_pressure_id': 'FP-0146',
    'change_anchor_surface': 'CHANGELOG.md',
    'freshness_state': 'current-aligned',
    'repair': 'ordinary-continuation'
}
receipt['question_posture_witness'] = {
    'resolution_surface': 'RESOLUTION-LEDGER.json',
    'registry_surface': 'docs/20-constitution/open-question-registry.md',
    'trajectory_surface': 'docs/00-meta/trajectory-map.md',
    'synced_resolved_questions': ['OQ-0142'],
    'frontier_selection_rule': 'resolved OQ-0142 is synchronized across resolution ledger, registry, and trajectory while frontier selection advances to OQ-0143',
    'posture_state': 'resolved-sync-current',
    'repair': 'ordinary-continuation'
}
receipt['current_import_id'] = 'TL-0152'
receipt['current_pressure_id'] = 'FP-0146'
receipt['import_witness'] = 'DATACUBE-TRANSFER-LEDGER.json#TL-0152'
receipt['new_classes_or_families'] = ['refresh_elevation_state']
receipt['quarantined_non_take'] = ['refresh-elevation court','burden senate','escalation gate','claim-rights governor']
receipt['artifacts_touched'] = receipt['touched_surfaces']
receipt['exception_witness'] = {
    'witness_surface': 'docs/90-quarantine/wild-speculations-2026-03-08.md#QWS-0225',
    'governed_obligation_surface': 'OBLIGATION-LEDGER.json#OB-0142',
    'exception_basis': 'bold speculation stays quarantined',
    'honor_window': 'until stronger refresh-elevation governance receives direct public witness support',
    'aggregate_effect': 'stronger refresh-elevation governance remains non-canonical',
    'repair': 'ordinary-continuation'
}
receipt['renewal_witness'] = {
    'witness_surface': 'OBLIGATION-LEDGER.json#OB-0142',
    'governed_obligation_surface': 'OBLIGATION-LEDGER.json#OB-0142',
    'prior_exception_window': 'quarantined',
    'renewal_act': 'none',
    'current_honor_window': 'unchanged',
    'repair': 'ordinary-continuation'
}
receipt['renewal_scope_witness'] = {
    'witness_surface': 'OBLIGATION-LEDGER.json#OB-0142',
    'governed_obligation_surface': 'OBLIGATION-LEDGER.json#OB-0142',
    'prior_local_target': 'refresh elevation',
    'current_refreshed_target': 'refresh elevation',
    'renewal_scope_state_family': 'local-refresh',
    'repair': 'ordinary-continuation'
}
receipt['refresh_elevation_witness'] = {
    'id': 'RELW-0149',
    'surface': NEW_DOC,
    'refresh_elevation_state': 'stabilizing-independent-support|threshold-licensed-elevation|judgment-gated-escalation|mixed-refresh-elevation',
    'repair': 'keep-current|narrow-claim|elevate-burden|issue-new-refresh-elevation-witness|quarantine-refresh-elevation-governance'
}
write('REVISION-RECEIPT.json', json.dumps(receipt, indent=2) + '\n')
