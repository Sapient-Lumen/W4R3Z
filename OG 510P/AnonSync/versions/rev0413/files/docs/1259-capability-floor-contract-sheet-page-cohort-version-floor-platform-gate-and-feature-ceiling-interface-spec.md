# Capability-floor contract sheet page: cohort version floor, platform gate, and feature ceiling interface spec

## Purpose

The archive already has pages for reachability provenance, cohort census, redundancy floor, effective seat posture, and presence.
What it still lacked was one ordinary page for the narrower question:

> even if these peers can still exchange bytes, what is the strongest truthful sentence about what this whole cohort can safely do, which node sets the floor, and which feature or upgrade claims are blocked right now?

Current official Resilio docs make this seam concrete.
They separately describe v2/v3 wire compatibility, mixed-major linked-device risk, platform differences between v2 and v3, feature gating by version and license, and Business/NAS lanes that must stay on v2.
That is useful truth.
It should not remain scattered.

## Core decision

AnonSync must expose one first-class **Capability-floor contract sheet** whenever a subject's truthful behavior depends on the weakest governing node, the most constrained product lane, or the least-capable platform class in the current cohort.

The sheet exists to answer six things in one place:

1. whether byte exchange compatibility currently exists
2. what major-version floor governs the cohort
3. what platform class floor governs the cohort
4. what feature ceiling is safe to claim cohort-wide
5. what upgrade lane is blocked by product posture or policy
6. what stronger capability sentence remains blocked

## Fixed page order

1. **Capability header**
2. **Cohort floor card**
3. **Platform and lane gates card**
4. **Feature ceiling card**
5. **Upgrade / migration rail**
6. **Blocked stronger sentence**

### 1) Capability header

Show at minimum:

- `capability_floor_id`
- subject ref
- last cohort capability witness time
- strongest safe sentence
- blocked stronger sentence
- current byte-compatibility grade
- current feature-ceiling grade

Supported headline states must include:

- `byte-compatible-but-admin-floor-lowered`
- `feature-compatible-cohort`
- `mixed-major-risky-linked-family`
- `platform-gated-cohort`
- `lane-split-cohort`
- `unknown`

Example safe sentence:

- `This cohort can still exchange bytes, but its safe feature claims are capped by one v2 Business/NAS participant and one mixed-major linked family.`

### 2) Cohort floor card

Show explicit rows for at least:

- highest observed major version
- lowest governing major version
- linked-family mixed-major risk
- byte-exchange compatibility state
- administration-safety state
- identity / license interlock state

Every row must show:

- `current floor value`
- `governing members`
- `freshness`
- `why this floor matters`

The operator must be able to answer:

> are we merely connected, or do we also safely share one feature and management envelope?

### 3) Platform and lane gates card

Separate these gates explicitly:

- unsupported platform for current target lane
- legacy platform still valid only on older lane
- personal-only lane
- business-only / business-held lane
- NAS-specific hold
- unknown package posture

Every row must show:

- governing platform class
- affected members
- whether upgrade is allowed
- whether reinstall / migration is required

The operator must be able to answer:

> what is stopping this cohort from moving together?

### 4) Feature ceiling card

Separate these truths explicitly:

- feature available cohort-wide
- feature available only on newer members
- feature available only under a paid or entitled lane
- feature blocked by older version floor
- feature blocked by platform class
- feature blocked by business/personal lane split

Each feature row must show:

- `claim level`
- `strongest safe sentence`
- `blocked stronger sentence`
- `governing blocker`

The operator must be able to answer:

> what can I promise for everyone, not just for the newest machine?

### 5) Upgrade / migration rail

Supported action rows must include:

- `upgrade all linked-family members to same major`
- `hold Business/NAS members on supported lane`
- `split mixed-purpose cohorts before upgrade`
- `replace unsupported platform member`
- `open migration plan`
- `export capability receipt`

Each action row must show:

- remediation target
- whether bytes remain compatible during delay
- whether admin safety remains degraded during delay
- whether reinstall is required

### 6) Blocked stronger sentence

Allowed examples:

- `Show why cohort-wide Selective Sync claim is blocked`
- `Show why v3 migration is blocked for this NAS member`
- `Show why linked-family admin safety is degraded`

Blocked examples:

- `Claim uniform v3 cohort` when a Business/NAS node must stay on v2
- `Claim feature parity` when a feature is licensed in v2 but general in v3
- `Claim safe mixed-major linking` when identity-linked v2/v3 conflict risk remains

## Field vocabulary

Use these exact field names where practical:

- `byte_compatibility_grade`
- `cohort_major_floor`
- `linked_family_mixed_major_state`
- `platform_support_floor`
- `product_lane_floor`
- `feature_claim_ceiling`
- `governing_blockers`
- `upgrade_lane_state`
- `blocked_stronger_sentence`

## Hard rules

- no compatibility badge may appear without an adjacent `feature claim ceiling`
- linked-family mixed-major risk must never be flattened into generic `compatible`
- Business/NAS hold state must never be flattened into simple `outdated`
- unsupported target-platform members must never silently count as migration-ready
- the strongest safe sentence must be printed before any upgrade optimism or health color
