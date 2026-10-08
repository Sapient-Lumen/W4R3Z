---
id: ss-migrated-authority-freshness-guarantees-become-compliance-metrics
revision_promoted: pre-rev0182
migration_status: inferred-rev0182+freshness-reviewed
title: Authority Freshness Guarantees Become Compliance Metrics
constellation:
- managed-legibility
- energy-sovereignty
- anti-legibility
- operational-resilience
status: dossier
maturity: S2-artifact-emerging
confidence: medium
time_horizon: near
domain:
- identity / credentials / delegated authority
- civic services / casework / appeals
- procurement / purchasing / offtake
bottleneck_type:
- state freshness
enforcement_surface:
- procurement / framework contract
- platform eligibility
- audit / assurance engagement
artifact_type:
- registry entry
- notice
lifecycle_stage:
- publish
- rely
failure_modes:
- stale-state
refactor_cluster:
- evidence-freshness
- authority-lifecycle
freshness_role: authority-state currentness
consolidation_status: standalone-mechanism
state_family:
- freshness
- authority
freshness_clock:
- validated_at
- relied_at
state_terms:
- valid-cached
- revalidation-due
- authority-stale
- revocation-pending
- revoked
- expired
authority_role: revocation-publisher and verifier-relying-party
authority_stage:
- verify
- revoke
- propagate
- audit
---
# Dossier: Authority Freshness Guarantees Become Compliance Metrics

## Core claim

The important shift is not merely that more services recognise helpers, attorneys, brokers, carers, nominees, tax professionals, or proxies. It is that **once delegated action becomes normal, institutions increasingly need to know how current that authority state really is**. A mandate that was valid at some earlier moment may no longer be valid now. That pushes review dates, expiry windows, reauthorisation cycles, revalidation triggers, status checks, and stale-state tolerances toward the center of service design.

The stronger version of the thesis is not simply that revocation matters. It is that **authority freshness guarantees become compliance metrics**. Services increasingly need explicit answers to questions such as: how long may an authority record sit unreviewed, when must it expire, how quickly must a change become visible, when must a user be reverified, how long may a pending request remain unresolved, and what fallback is acceptable if the freshest state is unavailable.

## Why this belongs in the archive

The archive already contains dossiers on mandate-lifecycle registries, revocation propagation, and authority-check middleware. The missing layer was **freshness governance**: not only whether authority can be represented or checked, but whether institutions begin treating the *currentness* of that authority as something that must be designed, bounded, audited, and eventually compared.

The UK’s March 2026 digital-identity consultation now makes the update problem explicit. It says digital-ID attributes must be alterable, credentials reissued if issuance errors are discovered, and digital IDs updated or reissued periodically to accommodate technology changes or expiry dates [S451]. That same text also says government will need powers to revoke a digital ID in strictly controlled circumstances [S451]. This matters because it frames validity not as a one-time proof but as an ongoing lifecycle with explicit refresh and revocation expectations.

The trust-framework lineage points the same way. The UK digital identity and attributes trust framework gamma 0.4 says holder-service providers must have processes to revoke, suspend, close, recover, and make changes to accounts, and it adds a specific requirement to reverify an inactive identity before it can be used again after 14 months [S452]. That is a direct sign that a service can no longer treat dormant authority or identity state as indefinitely reliable.

Tax administration now shows the same shift in operational form. IRS Tax Pro Account says approved authorization requests should display immediately after taxpayer approval and that withdrawals occur in real time, with the authorization immediately removed from the CAF database [S429]. IRS’s internal systems guidance adds that any authorization not in approved status is removed after 120 days and that some requests explicitly expire if the taxpayer has not acted within that window [S450]. The important point is not just digitisation. It is that IRS is now giving authority state explicit freshness semantics: immediate appearance, immediate removal, and defined pending-state expiry.

Healthcare and public-benefit systems are moving in parallel. NHS England’s National proxy service is building a national proxy data store that includes expiry and review dates plus an auditable record of changes, and it is intended to become mandatory for GP proxy awards in England from 2027 [S441]. CMS’s 2025 Marketplace compliance deck says consumers must authorize an agent or broker every 365 days to act for them at the Marketplace Call Center [S449]. Social Security’s Representative Payee Program mails annual reports to many payees and can also select payees for review; the FY 2024 annual report shows a standing review apparatus with periodic, targeted, educational, state-onsite, and predictive-model review types [S453][S454]. These are all versions of the same institutional move: authority is not merely granted, it is kept current on a schedule.

The Office of the Public Guardian’s LPA stack shows the same logic in a narrower but very revealing form. OPG’s online LPA view uses access codes that are valid for 30 days, and the activation keys used to add an LPA to an account expire after a year and must then be reissued by post [S455][S456]. Australia’s Relationship Authorisation Manager similarly turns consent and machine credentials into governed-duration objects: consent is now valid for up to 7 years, machine credentials remain valid for 2 years, expiry warnings are sent at 60, 30, and 7 days, and unclaimed suspended credentials are automatically revoked after 60 days [S457][S458][S437]. These are not minor UX details. They are evidence that institutions increasingly need explicit *freshness budgets* for authority-bearing artifacts.

Taken together, these signals support a broader thesis than the earlier authority dossiers: **once delegated authority becomes infrastructural, freshness rules stop being backend hygiene and start becoming an operational compliance surface**.

## Speculative consequences worth tracking

### 1. Freshness windows become action-specific

High-risk actions may come to require live or near-live checks, while lower-risk actions tolerate recent snapshots or longer review intervals.

### 2. Review cadence turns into an auditable obligation

Institutions may increasingly need to show not only that they can revoke or update authority, but that they review, refresh, and expire authority on a defensible schedule.

### 3. Stale-state tolerance becomes a policy choice

Questions like “is a 30-day-old proxy state acceptable?” or “how long may a suspended credential remain usable?” may increasingly become legal and supervisory questions rather than purely technical tuning.

### 4. Freshness failures produce a new class of harm

More institutions may start treating stale authority as a distinct failure mode: not quite fraud, not quite outage, but action taken on permissions that were once valid and are no longer current enough.

### 5. Fallback channels gain constitutional weight

If fresh checks are required for important actions, then supervised override, paper evidence, three-way calls, in-person verification, and emergency exceptions may become the legitimacy valves that keep services usable during mismatch or downtime.

### 6. Metrics and SLAs may emerge around authority state

Once freshness is treated as a governed surface, organisations may start publishing or internally tracking measures such as reauthorisation completion rates, review-date overruns, revocation-latency distributions, stale-cache exposure, and share of actions completed on live versus snapshot authority.

## What could falsify or weaken the thesis

- Most services remain comfortable with static documents and rarely impose explicit refresh or review windows.
- Expiry dates and revalidation rules remain scattered implementation details rather than becoming governance or compliance concerns.
- Authority freshness matters only in a few narrow sectors such as tax or elder-law, without broader spread across benefits, health, company law, and identity systems.
- Institutions continue to care mainly about whether authority exists, with little attention to how stale the checked state might be.
- Human casework continues to absorb stale-state problems informally, preventing freshness guarantees from becoming visible metrics.

## Research queue

- Which actions actually require live authority state, and which can rely safely on a recent snapshot?
- What are defensible stale-state tolerances by action class: payment, filing, consent, access, amendment, or viewing?
- Who should bear liability when an institution acts on authority state that was technically valid but too stale for the action?
- Which freshness indicators are most publishable without creating new privacy or attack-surface problems?
- How often do institutions prefer short-lived access codes and periodic reauthorisation over continuous live lookup, and why?
