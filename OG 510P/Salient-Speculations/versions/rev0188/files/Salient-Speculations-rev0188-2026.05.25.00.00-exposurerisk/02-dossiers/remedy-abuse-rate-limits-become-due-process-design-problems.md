---
id: ss-0185-remedy_abuse_rate_limits_become_due_process_design_problems
revision_promoted: rev0185
title: Remedy-abuse rate limits become due-process design problems
constellation:
- managed-legibility
- administrative-repair
- market-and-state-capacity
status: dossier
maturity: S2-artifact-emerging
confidence: medium-high
time_horizon: near
domain:
- platform moderation / content governance
- procurement / purchasing / offtake
- diligence packets
- public services / eligibility
bottleneck_type:
- appealability / redress
- abuse filtering
- procedural capacity
- interim reliance authority
enforcement_surface:
- platform governance
- broker terms
- procurement / framework contract
- supervisory audit
artifact_type:
- abuse classifier
- frivolousness notice
- repeat-filing ledger
- rate-limit rule
lifecycle_stage:
- intake
- abuse-screen
- stay
- review
- sanction
failure_modes:
- frivolous-filing
- retaliatory-appeal
- suppression-by-rate-limit
- strategic-delay
- forum-spam
refactor_cluster:
- remedy-lifecycle
remedy_role: bad-faith filtering without destroying appealability
remedy_stage:
- intake
- abuse-screen
- stay
- review
- sanction
consolidation_status: standalone-mechanism
state_family:
- remedy
source_refs:
- S1541
- S1542
- S1552
---
# Remedy-abuse rate limits become due-process design problems

## Core claim

Once an appeal can pause reliance, restrict processing, reserve money, reopen scoring, delay award, or force human review, appeal rights become valuable enough to abuse. The same mechanism that protects against false denials can be used for harassment, delay, leverage, evasion, and capacity exhaustion.

The speculative claim: **remedy-abuse rate limits become due-process design problems**. Mature systems will need a vocabulary for frivolous, duplicate, manifestly unfounded, bad-faith, wrong-forum, abusive-volume, leverage-only, bot-filed, and harassment appeals — but they must also make those labels contestable. Abuse filtering that is not itself reviewable becomes a denial of remedy.

## Why this belongs in the cube

The archive has strong faith in appealability as repair. rev0182 added adversarial stress-testing for proof objects. The remedy cluster now needs the same stress layer. Every right to appeal creates a new attack surface.

The Digital Services Act is the clearest analogue. It gives users routes to contest platform decisions, but the DSA also contains protections against misuse, including suspension of processing for frequently submitted manifestly unfounded notices or complaints under specified safeguards [S1541, S1542, S1552]. This is not a minor exception; it is a design principle for any high-volume redress infrastructure.

Packet markets will discover similar tensions. A supplier may file appeals to delay a buyer. A buyer may over-file to pressure a supplier. A marketplace seller may appeal every takedown. A litigant may use packet appeals for discovery. A fraud ring may probe explanation packets to learn thresholds. A competitor may file public-interest complaints to slow market access.

## The normalized abuse states

A remedy system should distinguish:

- `insufficient-evidence` — the filing lacks required information but may be cured.
- `duplicate` — the matter is already pending or decided.
- `late-filed` — the clock expired, subject to equitable or outage exceptions.
- `wrong-forum` — another process controls, with routing obligation.
- `manifestly-unfounded` — no plausible remedy theory after minimal review.
- `bad-faith` — evidence of harassment, evasion, or strategic abuse.
- `abusive-volume` — rate threshold exceeded, after warning.
- `restricted-stay-effect` — appeal may continue but no automatic stay applies.
- `abuse-label-appealable` — the abuse classification itself can be challenged.

The point is not to block appeal. It is to prevent appeal from becoming a denial-of-service tool while preserving a route for legitimate edge cases.

## Speculative consequences

### 1. Stay effect separates from appeal receipt

A system may accept an appeal while denying automatic stay, score exclusion, holdback reservation, or publication suspension because abuse risk is high. That separation will require reasons and review.

### 2. Abuse metrics become publishable governance indicators

Platforms, brokers, and public agencies may publish rates of rejected, duplicate, late, manifestly unfounded, and bad-faith appeals. But those metrics can also hide suppression. A high abuse rate may mean abuse, or it may mean the portal is unusable.

### 3. Warning systems become procedural infrastructure

Before rate-limiting a user or supplier, systems may need warning notices, cure opportunities, explanation of thresholds, and exception processes.

### 4. Anti-abuse design becomes distributive

High-resource actors can craft formally valid appeals. Low-resource actors are more likely to file messy or incomplete ones. Abuse filters that punish imperfect filings can deepen inequality.

## Abuse and capture

This dossier is about abuse, but the anti-abuse layer is itself abusable. Institutions can label inconvenient complaints as frivolous, set impossible substantiation thresholds, deny stays to weaker parties, or use rate limits to protect dominant actors. Public dashboards can stigmatize high-appeal populations without showing underlying error rates.

The remedy-lifecycle model should therefore require appealable abuse labels, representative assistance, cure windows, and independent audits of false-abuse classification.

## Falsifiers

The thesis weakens if appeal volume stays low or stay effects remain weak. It strengthens if broker terms, platform policies, procurement rules, or regulators start defining abusive appeals, rate-limiting conditions, or stay-denial categories with procedural safeguards.
