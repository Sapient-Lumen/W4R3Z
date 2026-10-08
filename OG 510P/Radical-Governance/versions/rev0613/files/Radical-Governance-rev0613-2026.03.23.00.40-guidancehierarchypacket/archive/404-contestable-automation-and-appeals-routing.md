# 404 — Contestable automation and appeals routing

## One-line thesis

No consequential automated system should be allowed to operate without a visible path from **notice** to **reason** to **override** to **appeal** to **remedy**.

## Core claim

Most oversight regimes still concentrate on pre-deployment review. But everyday legitimacy depends on what happens **after a person is affected**. The archive should therefore treat contestability infrastructure as a first-class institution, not a downstream customer-service feature.

## Minimal rights bundle

For any high-impact system used in public administration or delegated public service delivery, affected people should get:

- notice that automation is being used,
- a plain-language explanation of the decision pathway,
- a case-specific reason packet sufficient to challenge the result,
- access to a human reviewer with authority to pause or reverse,
- a clear appeal channel and deadline,
- traceable remedy when harm is found.

## Pattern pack

### 1. Decision receipt

Issue a standard receipt every time a consequential machine-assisted decision is produced. It should include:

- case identifier,
- model or rule family used,
- timestamp,
- decision class,
- principal factors or triggers,
- confidence / uncertainty notation where relevant,
- reviewer identity or office,
- route to challenge.

### 2. Reason packet

Maintain an internal and external explanation layer.

External layer:

- plain-language summary,
- salient facts used,
- missing facts that could alter the result,
- next steps to contest.

Internal layer:

- logs,
- model / ruleset version,
- input transformations,
- thresholds,
- operator interventions,
- linked evidence and overrides.

### 3. Appeals router

Create a common appeals intake that can route across agencies and vendors instead of forcing people to guess the right office. The router should:

- classify the kind of grievance,
- preserve filing timestamps,
- assign responsibility,
- escalate unresolved cases,
- generate public service-level metrics.

### 4. Human authority, not decorative oversight

A named human reviewer must have real powers to:

- halt execution,
- request additional evidence,
- disregard system output,
- trigger incident review,
- mark a case as precedent-setting.

### 5. Harms and near-misses register

Track not only proved harms but also:

- near misses,
- recurring edge cases,
- demographic skews,
- vendor-caused outages,
- appeal bottlenecks,
- override frequency by office.

### 6. Friction budget

If contesting a decision costs too much time, literacy, bandwidth, or travel, the right is fictional. Systems need explicit service standards on:

- maximum clicks or forms,
- multilingual support,
- offline filing options,
- accessibility,
- response deadlines,
- interim relief when delay itself causes harm.

## Institutional architecture

The archive should distinguish five layers:

1. **provider duties** — design, logging, instructions, limits;
2. **deployer duties** — context-specific use, human oversight, impact assessment;
3. **operator duties** — correct use, flagging, override, escalation;
4. **appeals institution** — independent review and remedy;
5. **public reporting layer** — aggregated metrics, incidents, systemic corrections.

## Failure modes

- users are told a system is “only advisory” even when it strongly anchors outcomes;
- explanations are generic and cannot be used to challenge a case;
- human review exists on paper but reviewers lack authority or time;
- appeals channels are fragmented across agencies and contractors;
- logs exist but are unreadable, unexportable, or unavailable during disputes.

## Metrics that matter

Track:

- appeal rate,
- average time to human review,
- percentage of decisions reversed or modified,
- repeat incidents by failure type,
- share of complaints resolved without litigation,
- number of cases where interim relief prevented compounding harm.

## Compression rule for the archive

When reviewing any automated governance system, ask one blunt question:

**Can an affected person realistically contest this in time to matter?**

If the answer is no, the system is institutionally incomplete no matter how polished its pre-deployment assurance may be.
