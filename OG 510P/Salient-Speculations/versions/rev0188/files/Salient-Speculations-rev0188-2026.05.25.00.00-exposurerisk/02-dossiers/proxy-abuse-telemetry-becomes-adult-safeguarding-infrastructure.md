---
id: ss-0186-proxy-abuse-telemetry
revision_promoted: rev0186
title: Proxy-abuse telemetry becomes adult-safeguarding infrastructure
constellation:
- care-and-demography
- managed-legibility
- administrative-repair
status: dossier
maturity: S2-artifact-emerging
confidence: medium
time_horizon: near
domain:
- care / ageing / household capacity
- identity / credentials / delegated authority
- healthcare / biological observability / diagnostics
- consumer services / transactions / redress
- public services / eligibility
bottleneck_type:
- delegated authority
- fraud resistance
- human review capacity
- appealability / redress
- liability-tail custody
enforcement_surface:
- adult safeguarding
- financial-services compliance
- healthcare proxy access
- public-benefit administration
- consumer protection
artifact_type:
- abuse telemetry
- proxy-use log
- safeguarding referral
- authority-risk score
- representative review packet
lifecycle_stage:
- act
- log
- audit
- dispute
- revoke
- propagate
failure_modes:
- coercive-delegation
- self-dealing
- undetected-proxy-misuse
- false-abuse-flag
- care-access-interruption
- privacy-intrusion
refactor_cluster:
- authority-lifecycle
authority_role: guardian-fiduciary and abuse-monitor
authority_stage:
- act
- log
- audit
- dispute
- revoke
consolidation_status: standalone-mechanism
state_family:
- authority
- remedy
state_terms:
- abuse-watch
- suspended
- disputed-authority
- revoked
- fallback-accepted
evidence_grade: E2-signal-cluster
decision_grade: DG-B
decision_total: 14
source_refs:
- S1554
- S1555
- S1562
- S1563
---
# Proxy-abuse telemetry becomes adult-safeguarding infrastructure

## Core claim

Delegation is usually framed as access: helping someone file, pay, appeal, obtain care, manage money, or navigate digital services. But every proxy layer also creates an abuse surface. The same machinery that lets a trusted helper act can let a coercive relative, bad caregiver, rogue professional, compromised account, or exploitative agent act.

The speculative claim: **proxy-abuse telemetry becomes adult-safeguarding infrastructure**. As delegated authority becomes machine-readable, systems will start generating signals about misuse, coercion, self-dealing, unusual access, representative conflicts, revocation lag, and suspicious transaction patterns. Those signals will become part of safeguarding, supervision, and remedy design.

## Why this belongs in the cube

The archive has strong access-oriented delegation dossiers. This dossier adds the darker half: **delegation needs abuse observability**.

GOV.UK's LPA guidance makes the risk visible. Attorneys must follow donor restrictions, act in the donor's best interests, keep money separate, respect confidentiality, not let others use the LPA, and keep records; their decisions can be checked [S1563]. Those are not merely ethical statements. In a digital proxy ecosystem, they imply logs, checks, exception flags, and review routes.

The EUDI Wallet architecture explicitly considers representation of minors, people with diminished capacity, elderly or incapacitated individuals, caregivers, relatives, and powers of attorney [S1554]. The same architecture defines rights and permissions as wallet-relevant attributes and represents users as natural or legal persons, or natural persons representing others [S1555]. Once that representation is operationalized, misuse becomes a data and governance problem.

Tax representation shows the same risk in a less care-focused domain: a representative authorized by Form 2848 can receive and inspect confidential tax information [S1562]. A representative-of-record system therefore needs not only access checks but misuse checks.

## Likely telemetry signals

- unusual volume of proxy actions;
- repeated access outside normal hours or channels;
- high-risk actions soon after appointment;
- changes to payment destination, mailing address, contact method, or consent preferences;
- attempts to suppress notices to the principal;
- actions inconsistent with restrictions or joint-decision rules;
- use after revocation or expiry;
- representative acting for many vulnerable subjects;
- repeated failed standing or scope checks;
- disputes, complaints, or reversals associated with a representative;
- sudden use of offline fallback when live authority would fail.

## Speculative consequences

### 1. Safeguarding moves into transaction logs

A safeguarding system that waits for external reports may miss digital abuse. Portal, wallet, and representative-of-record logs may become early warning sources.

### 2. Representative risk becomes supervised

Professional representatives, carers, attorneys, brokers, and agent operators may be monitored by abuse rates, complaint rates, revocation incidents, and high-risk action patterns.

### 3. The privacy tradeoff becomes acute

The represented person may need protection from a proxy, but telemetry itself can expose intimate facts about health, finances, care, family conflict, benefits, or capacity.

### 4. False positives become access harms

If a legitimate caregiver is suspended because of crude anomaly rules, the principal may lose care access, bill payment, benefits, or healthcare coordination. Abuse telemetry needs remedy and human review.

### 5. Coercive control becomes an authorization-design problem

Consent alone may be insufficient when a principal is pressured. Systems may need independent channels, cooling-off periods, principal-visible activity feeds, periodic re-confirmation, or trusted third-party alerts.

## Abuse of the abuse layer

- institutions over-monitor families and carers;
- representatives are risk-scored without appeal;
- vulnerable people lose informal support because formal proxy systems are too burdensome;
- abusive proxies learn to avoid high-risk signals;
- platforms use “safeguarding” as a reason to deny legitimate representation;
- telemetry becomes a surveillance product.

## What would make this decision-grade

- public agencies publish representative-risk metrics;
- banks, benefits systems, or health portals use proxy activity logs for safeguarding referral;
- regulators require proxy-use audit trails;
- litigation or complaints turn on whether a system detected suspicious representative behavior;
- wallets or authority-check APIs include abuse-watch or suspended-representative states.

## Near miss / not this

Ordinary fraud monitoring is not proxy-abuse telemetry unless it is specifically about misuse of delegated authority, representative access, or fiduciary power.
