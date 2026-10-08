from pathlib import Path

ROOT = Path(__file__).resolve().parent
DOCS = ROOT / 'docs'
README = ROOT / 'README.md'

files = {
'1258-resilio-mixed-version-capability-floor-platform-gating-and-license-conflict-fragmentation-evaluation.md': r'''# Resilio mixed-version capability-floor, platform-gating, and license-conflict fragmentation evaluation

## What current official docs still make clear

Another current Resilio pass strengthens the archive's clone-veto line rather than weakening it.

Current official docs still say several things that are operationally real and worth borrowing:

- current `FAQ Resilio Sync 3.0.0` docs still say Sync v2 and v3 preserve synchronization compatibility
- those same current FAQ docs still say devices linked under one identity should all be updated to v3 to avoid license conflicts
- current identity-linking docs sharpen that again: they still say linking devices where v2 and v3 are mixed is highly inadvisable because applied licenses can conflict and access to UI and shares configuration may be lost, even though stored files are not affected
- current supported-platforms docs still say the v3 platform envelope is narrower than v2 in important ways: v3 is not supported on Windows Server, while current v2 docs still list Windows Server 2008 R2 and newer; current v2 docs also still list FreeBSD and wider CPU coverage that v3 no longer lists
- current `Selective Sync` docs still say the feature is fully available in v3 but in v2 is available only in licensed editions
- current installation and NAS-package docs still say Sync Business must remain on v2, the latest available v2 release is 2.8.1 for that lane, and attempting to install v3 over a Business installation is unsupported and can lose access to configured shares until reinstall

That is real candor.
It is useful product truth.

## What still should not be cloned

The operator is still asked to reconstruct several materially different questions from several different pages:

1. **can these peers still exchange bytes at all?**
2. **what major-version floor governs the cohort's safe feature envelope?**
3. **which peers are blocked not by reachability but by platform class or product lane?**
4. **which features are present in some seats but not safely claimable for the whole cohort?**
5. **which upgrade moves are actually forbidden because of business/NAS posture rather than mere lag?**

Current Resilio docs still spread those answers across FAQ, identity-linking, supported-platforms, feature pages, and installation articles.

So a user can learn all the pieces and still not get one stable product answer to:

> this cohort still syncs, but what is the strongest truthful sentence about what the whole group can safely do, which members set the floor, and which upgrades are blocked by license or platform lane rather than simple staleness?

That page-contract gap is exactly why AnonSync should not clone the behavior.

## Why this matters for AnonSync

AnonSync should borrow five habits directly:

- **say openly when wire compatibility survives but cohort capability does not fully survive**
- **say openly when mixed majors are byte-compatible but identity-linked administration is unsafe**
- **say openly when platform class narrows the cohort's future upgrade lane**
- **say openly when a feature is only locally available and cannot be safely promised cohort-wide**
- **say openly when a node is held on an older lane by product policy rather than operator neglect**

But AnonSync should reject five weaker habits:

- one optimistic `compatible` sentence that hides linked-family license conflict risk
- version badges that do not publish the effective cohort floor
- feature marketing that does not publish seat-class and platform gates
- upgrade prompts that ignore NAS / Business immobility
- capability claims derived from a strongest node instead of the weakest governing node

## Replacement pages added for this seam

This revision therefore adds six narrower replacement pages:

- `1259` — Capability-floor contract sheet
- `1260` — Version interlock review
- `1261` — Feature envelope proof
- `1262` — Capability-floor timeline
- `1263` — Capability-floor lineage receipt

These pages keep the Resilio candor and reject the scattered-capability-floor semantics problem.

## Sharper non-clone line after this pass

The archive now has one tighter sentence for this seam:

> borrow Resilio's candor that wire compatibility, linked-identity safety, platform support, feature entitlement, and upgrade lane are different truths; refuse any interface contract where the operator must reconstruct the cohort's real capability floor from several FAQ, platform, identity, and installation articles instead of one explicit capability-floor object.
''',
'1259-capability-floor-contract-sheet-page-cohort-version-floor-platform-gate-and-feature-ceiling-interface-spec.md': r'''# Capability-floor contract sheet page: cohort version floor, platform gate, and feature ceiling interface spec

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
''',
'1260-version-interlock-review-page-linked-family-mixed-major-risk-and-upgrade-boundary-interface-spec.md': r'''# Version interlock review page: linked-family mixed-major risk and upgrade boundary interface spec

## Purpose

This page exists for the moment when bytes may still flow but administration truth has already degraded.
It is the focused review for mixed-major cohorts, especially identity-linked families where one optimistic `compatible` label would be dangerously incomplete.

## Core decision

AnonSync must treat **mixed-major interlock** as first-class review state whenever any of the following are true:

- a linked family contains more than one major version
- byte exchange remains possible but license or configuration safety degrades
- one upgrade path is forbidden because a member is Business/NAS constrained
- one feature claim depends on collapsing several members to the same major first

## Review layout

1. **Interlock summary rail**
2. **Member matrix**
3. **Risk translation card**
4. **Upgrade-boundary decision card**
5. **Receipts and next actions**

### 1) Interlock summary rail

Show:

- `mixed_major_present`
- `linked_family_present`
- `byte_exchange_survives`
- `admin_safety_degraded`
- `license_conflict_risk_present`
- `upgrade_boundary_kind`

Supported summary states:

- `safe-same-major`
- `mixed-major-unlinked`
- `mixed-major-linked-risk`
- `migration-blocked-by-lane`
- `migration-blocked-by-platform`
- `unknown`

### 2) Member matrix

Each member row must show:

- member ref
- current major version
- linked-family membership
- product lane (`personal`, `business`, `unknown`)
- platform class
- target-lane eligibility
- governing blocker

The operator must be able to answer:

> which exact member is setting the risk floor?

### 3) Risk translation card

Translate mixed-version facts into operator language:

- `bytes still sync`
- `admin state may conflict`
- `license application may conflict`
- `shares configuration access may be lost`
- `stored data remains intact`
- `migration requires cohort split first`

This card exists because the technical fact and the operator consequence are different truths.

### 4) Upgrade-boundary decision card

Supported verdicts must include:

- `upgrade-together-now`
- `hold-current-until-linked-family-is-split`
- `never-upgrade-this-member-to-target-lane`
- `replace-member-before-upgrade`
- `safe-byte-compatibility-only`

Each verdict must show:

- why it is safe
- what stronger sentence it blocks
- who must move first
- whether reinstall or reconfiguration is required

### 5) Receipts and next actions

Allowed actions:

- `Create migration tranche`
- `Split linked family`
- `Freeze feature rollout`
- `Export interlock receipt`

## Hard rules

- a mixed-major linked family must always escalate to review; it cannot stay a silent badge
- `compatible` must never be shown alone when admin-safety truth is worse
- data-preservation reassurance must never be used to hide UI/configuration risk
- business-held members must be named explicitly, not implied as generic laggards
''',
'1261-feature-envelope-proof-page-feature-gates-seat-type-platform-class-and-cohort-floor-interface-spec.md': r'''# Feature envelope proof page: feature gates, seat type, platform class, and cohort floor interface spec

## Purpose

The capability-floor sheet says what the group can safely claim.
This page proves *why* a given feature claim is allowed, degraded, or blocked.

## Core decision

AnonSync must require a **Feature envelope proof** whenever a feature claim could be misunderstood because of:

- version mismatch
- platform mismatch
- personal vs business lane split
- paid / entitled vs general availability split
- linked-family mixed-major risk

## Proof layout

1. **Feature headline**
2. **Gate stack**
3. **Per-member satisfaction table**
4. **Cohort claim verdict**
5. **Blocked stronger sentence**

### 1) Feature headline

Show:

- feature name
- current claim verdict
- strongest safe sentence
- blocked stronger sentence
- proof freshness

### 2) Gate stack

Supported gate classes:

- `version-gate`
- `license-or-entitlement-gate`
- `platform-gate`
- `product-lane-gate`
- `linked-family-safety-gate`
- `unknown-gate`

The operator must be able to answer:

> what kinds of conditions stand between this feature and a truthful cohort-wide claim?

### 3) Per-member satisfaction table

Each row must show:

- member ref
- version satisfaction
- platform satisfaction
- seat/lane satisfaction
- safety satisfaction
- final contribution (`supports`, `degrades`, `blocks`, `unknown`)

### 4) Cohort claim verdict

Supported verdicts:

- `claim-safe-cohort-wide`
- `claim-safe-only-on-subset`
- `blocked-by-one-governing-member`
- `blocked-by-lane-split`
- `blocked-by-platform-floor`
- `blocked-by-admin-safety-floor`

Each verdict must print one exact sentence suitable for UI reuse.

### 5) Blocked stronger sentence

Examples:

- `Selective Sync is safe to claim cohort-wide` blocked because one v2 member lacks the required entitlement
- `v3 management features are safe cohort-wide` blocked because one Business/NAS member must stay on v2
- `all linked devices are safely on one major` blocked because mixed-major linking risk remains

## Hard rules

- feature availability on one member may never silently imply cohort availability
- the proof must name the governing blocker, not just mark the feature unavailable
- entitlement and platform blockers must stay distinct
- the interface must preserve the difference between `bytes still sync` and `this feature is safe to roll out`
''',
'1262-capability-floor-timeline-page-upgrade-drift-unsupported-nodes-and-floor-change-events-interface-spec.md': r'''# Capability-floor timeline page: upgrade drift, unsupported nodes, and floor-change events interface spec

## Purpose

Capability floors are not static.
They move when a member upgrades, a new member joins, a NAS node enters the cohort, a linked family splits, or an unsupported platform becomes the blocker.
This page exists to make those changes legible over time.

## Core decision

AnonSync must keep one **Capability-floor timeline** for every subject whose truthful capability claim can change because of cohort composition.

## Timeline events to preserve

Supported event kinds must include:

- `member-upgraded-major`
- `member-downgraded-or-held`
- `mixed-major-linked-family-created`
- `mixed-major-linked-family-resolved`
- `business-held-node-joined`
- `platform-floor-tightened`
- `feature-ceiling-raised`
- `feature-ceiling-lowered`
- `migration-blocker-cleared`
- `unknown-became-known`

## Entry shape

Each entry must show:

- event time
- event kind
- affected members
- old strongest safe sentence
- new strongest safe sentence
- old blocked stronger sentence
- new blocked stronger sentence
- evidence basis

## Special views

The page must support these filters:

- `show only floor-lowering events`
- `show only lane blockers`
- `show only linked-family risk events`
- `show only feature-ceiling raises`

## Hard rules

- timeline entries must preserve sentence changes, not just raw version changes
- a new blocker must name whether it is version, lane, platform, or safety based
- a cleared blocker must not erase the prior weaker period from history
''',
'1263-capability-floor-lineage-receipt-page-cohort-floor-blocked-feature-and-remediation-basis-interface-spec.md': r'''# Capability-floor lineage receipt page: cohort floor, blocked feature, and remediation basis interface spec

## Purpose

This receipt is the exportable proof for a capability-floor judgment.
It exists so the operator can answer later:

> why did the product refuse to claim more, which member set the floor, and what exactly had to change before the stronger claim became true?

## Receipt contents

The receipt must preserve:

- `capability_floor_id`
- subject ref
- issuance time
- byte-compatibility grade
- cohort major floor
- platform support floor
- product lane floor
- feature claim ceiling
- governing blockers
- strongest safe sentence
- blocked stronger sentence
- recommended remediations
- evidence freshness

## Human-readable summary

Example summary:

- `Bytes remain interoperable across this cohort, but the truthful feature envelope is capped by one Business-held v2 NAS member and one mixed-major linked family. Cohort-wide v3 management claims remain blocked until those blockers are resolved.`

## Hard rules

- the receipt must always separate `can still sync bytes` from `can safely claim feature parity`
- governing blockers must be named individually
- remediation steps must preserve whether each blocker is removable, permanent, or policy-held
- the blocked stronger sentence must survive export intact
'''
}

readme_addendum = r'''## Revision addendum — mixed-version capability floor, platform gating, and feature-ceiling truth after rev0352

This revision continues directly from `rev0352` and does eight concrete things:

1. Re-checks another current official Resilio cluster around **v2/v3 byte compatibility, linked-family mixed-major license conflict risk, platform-envelope differences between v2 and v3, Selective Sync feature gating, and Business/NAS installs that must remain on v2**.
2. Tightens the non-clone line again: borrow Resilio's candor that wire compatibility, identity-linked safety, platform support, feature entitlement, and upgrade lane are different truths; refuse any contract where the operator still has to reconstruct `what can this whole cohort safely claim, which member sets the floor, and what upgrade is actually forbidden rather than merely delayed?` from several articles.
3. Adds one new **Resilio evaluation** document focused on why present-day mixed-version capability truth is still too fragmented to clone even though the distinctions are useful.
4. Adds five new **interface specs** for capability-floor contract sheet, version interlock review, feature envelope proof, capability-floor timeline, and capability-floor lineage receipt.
5. Makes one hard product decision explicit: **byte compatibility is weaker than capability compatibility.**
6. Makes another hard product decision explicit: **linked-family mixed-major risk is first-class state rather than a footnote under generic compatibility.**
7. Makes a third hard product decision explicit: **product lane and platform class can permanently cap the cohort even when newer peers exist.**
8. Packages the result as another continuation archive whose new tranche makes the `capability-floor-contract / version-interlock-review / feature-envelope-proof / capability-floor-timeline / capability-floor-receipt` seam explicit in the reading order and page family.

New docs in this tranche:

- `1258-resilio-mixed-version-capability-floor-platform-gating-and-license-conflict-fragmentation-evaluation.md`
- `1259-capability-floor-contract-sheet-page-cohort-version-floor-platform-gate-and-feature-ceiling-interface-spec.md`
- `1260-version-interlock-review-page-linked-family-mixed-major-risk-and-upgrade-boundary-interface-spec.md`
- `1261-feature-envelope-proof-page-feature-gates-seat-type-platform-class-and-cohort-floor-interface-spec.md`
- `1262-capability-floor-timeline-page-upgrade-drift-unsupported-nodes-and-floor-change-events-interface-spec.md`
- `1263-capability-floor-lineage-receipt-page-cohort-floor-blocked-feature-and-remediation-basis-interface-spec.md`

## Current conclusion, tightened again

Another current official Resilio pass still supports the same overall judgment:

- **borrow Resilio's practical candor**
- **do not clone Resilio's mixed-version capability contract**

This time the reason is especially clear around **v2/v3 wire compatibility, mixed-major linked-family risk, narrower v3 platform support, feature gating by version/license, and Business/NAS lanes that must stay on v2**.
Current official materials simultaneously show that:

- current `FAQ Resilio Sync 3.0.0` docs still say v2 and v3 preserve synchronization compatibility, but devices linked with one identity should all be updated to v3 to avoid license conflicts
- current `Sync Private Identity & Linking My Devices` docs still say it is highly advisable not to link devices where v2 and v3 are mixed because licenses can conflict and lead to lost access to Sync UI and shares configuration, even though files on storage are not affected
- current `Supported platforms and system requirements` docs still say v3 is not supported on Windows Server while v2 still lists Windows Server support; those same docs also still show a wider v2 platform envelope including FreeBSD and wider CPU coverage
- current `Selective Sync` docs still say the feature is fully available in v3, while in v2 it is available only in licensed editions
- current Linux and NAS installation docs still say Sync Business must remain on v2, the latest available Business lane is 2.8.1, and installing v3 over a Business installation is unsupported and can lose access to configured shares until reinstall

That candor is useful.
The capability-floor contract is the problem.
AnonSync should not clone a world where the operator still has to translate `compatible`, `linked devices`, `supported platform`, `licensed feature`, and `Business must stay on v2` into byte-compatibility grade, admin-safety ceiling, platform floor, feature envelope, and forbidden upgrade lane by stitching together several FAQ, identity, platform, feature, and install pages.

So the harder product stance now becomes explicit:

> **AnonSync is not cloning Resilio because mixed-version truth is a real contract with separate truths for wire compatibility, linked-family safety, platform eligibility, feature entitlement, and upgrade lane, but the present contract still scatters the answer to `what can this whole cohort safely claim, which member sets the floor, and what upgrade is actually forbidden rather than merely delayed?` across several KB articles instead of owning it as one explicit capability-floor page family.**
'''

DOCS.mkdir(exist_ok=True)
for name, content in files.items():
    (DOCS / name).write_text(content.rstrip() + '\n', encoding='utf-8')

old = README.read_text(encoding='utf-8')
README.write_text(readme_addendum.rstrip() + '\n\n' + old, encoding='utf-8')
print('wrote', len(files), 'docs and updated README')
