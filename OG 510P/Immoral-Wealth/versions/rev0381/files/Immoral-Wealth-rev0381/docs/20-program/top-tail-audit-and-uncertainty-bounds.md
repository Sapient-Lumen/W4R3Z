---
status: active_protocol
claim_kind: measurement_protocol
route_role: certification_core
canonical_anchor: true
route_refs:
- measurement_uncertainty_core
- certification_core
- case_calibration_core
supersedes: null
depends_on:
- scoreboard-spec.md
- measurement-and-scoreboard.md
source_refresh_due: 2026-12-31
---

# Top-tail audit and uncertainty bounds

The top-tail audit is now mandatory for any case that seeks `acceptable_but_vulnerable`, `near_ideal`, or better on the share surface. It is optional only for subsystem cases that do not use national wealth-share certification.

## Audit sequence

### Step 1 — identify source family

Classify every core wealth-share claim:

- survey-only;
- survey with high-net-worth oversample;
- survey plus rich-list adjustment;
- administrative/tax capitalization;
- distributional national accounts;
- national-accounts-consistent experimental table;
- registry/property-based reconstruction;
- mixed estimate.

The source family must be recorded in the scoreboard. WID notes that current wealth inequality estimates remain unsatisfactory because access to country-level wealth survey and tax data is limited; that warning is now a doctrine input, not an aside.[S141]

### Step 2 — test top-tail sensitivity

Ask whether the top 1%, top 0.1%, or top 0.01% share changes materially after:

- rich-list supplementation;
- capitalization of income;
- administrative tax linkage;
- national-accounts alignment;
- correction for survey nonresponse or item nonresponse;
- offshore or entity ownership adjustment;
- private-business valuation changes.

The Canada PBO update is the model for why this matters: adjusted high-net-worth family data can show much higher top concentration than unadjusted survey data.[S146]

### Step 3 — build a moral interval

Use three readings where possible:

| Reading | Purpose |
|---|---|
| conservative low concentration | tests whether the case could pass under generous assumptions |
| central estimate | ordinary descriptive anchor |
| conservative high concentration | tests opacity/top-tail risk |

The certification question is not “which point estimate is best?” but “does the verdict change across plausible readings?”

### Step 4 — assign an uncertainty consequence

| Evidence pattern | Consequence |
|---|---|
| low uncertainty, all bounds pass | share gate may pass |
| bounds straddle pass/fail | `proof_debt`; no comfort certification |
| top-tail adjustment worsens concentration materially | `top_tail_audit_required` or `warning` |
| survey status suspended/accreditation warning | no survey-only pass |
| hidden owner/control channel material | gate 10 blocks certification |
| lower-half usable wealth uncertain due to debt/liquidity/title | floor gate re-read downward |

### Step 5 — route action

Top-tail uncertainty routes to one or more rails:

- high-net-worth oversampling;
- administrative/tax data linkage;
- macro/micro reconciliation;
- property and beneficial-owner registers;
- trust/legal-arrangement reporting;
- rich-list and private-company valuation documentation;
- publication of uncertainty bands.

The goal is not perfect data. The goal is to prevent a comfort verdict from resting on a measurement system that structurally misses the people and assets most relevant to wealth-to-rule risk.
