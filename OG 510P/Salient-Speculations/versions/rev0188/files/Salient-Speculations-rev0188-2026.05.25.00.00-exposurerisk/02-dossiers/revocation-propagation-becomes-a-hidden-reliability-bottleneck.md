---
id: ss-0183-revocation-propagation-becomes-a-hidden-reliability-bottleneck
revision_promoted: pre-rev0180
title: Revocation Propagation Becomes a Hidden Reliability Bottleneck
constellation:
- place-and-climate
- model-governance
- managed-legibility
status: dossier
maturity: S3-enforcement-surface
confidence: medium
time_horizon: mixed
domain:
- climate / retreat / habitability
- land / parcel / place-proof
- compute / AI / data centers
- simulation / forecasting / counterfactual capacity
- identity / credentials / delegated authority
- procurement / purchasing / offtake
bottleneck_type:
- model credibility
- admissible evidence
- state freshness
- source-of-truth precedence
- appealability / redress
enforcement_surface:
- permit / license
- title / conveyancing / property transfer
- underwriting / insurance renewal
- audit / attestation / assurance
- procurement / framework contract
- platform eligibility / ranking
artifact_type:
- registry entry
- notice
- state label
lifecycle_stage:
- publish
- rely
- dispute
- correct
primary_actors:
- municipality
- insurer
- property-owner
- model-provider
- buyer
- auditor
- broker
- source-vendor
failure_modes:
- stale-state
- nonpropagation
- false-match
adversarial_pressure:
- strategic-delay
- overbroad-disclosure
distributional_effect:
- incumbent-compliance-advantage
migration_status: inferred-rev0183-minimal+freshness-reviewed
migration_note: Metadata was inferred from title, source references, and local keyword
  context; review before treating as authoritative.
refactor_cluster:
- evidence-freshness
- authority-lifecycle
freshness_role: revocation-latency governance
consolidation_status: bridge-dossier
state_family:
- freshness
- authority
freshness_clock:
- validated_at
- relied_at
state_terms:
- revoked
- valid-cached
- revocation-pending
- authority-stale
authority_role: revocation-publisher
authority_stage:
- revoke
- propagate
- audit
---
# Dossier: Revocation Propagation Becomes a Hidden Reliability Bottleneck

## Core claim

The important shift is not merely that more systems allow a helper, proxy, attorney, broker, nominee, representative, or machine credential to act. It is that **once delegated authority becomes maintained state, the hard problem shifts to making changes in that state become true everywhere that matters**. Suspensions, withdrawals, replacements, expiries, scope reductions, and step-up checks only protect people if relying services stop trusting stale authority quickly enough.

The stronger version of the thesis is not simply that revocation matters. It is that **revocation propagation becomes a hidden reliability bottleneck**. As identity systems, proxy registries, portals, call centres, filing services, and regulated workflows all rely on shared authority state, institutional quality increasingly depends on how quickly and cleanly a change in authority ripples through the whole stack.

## Why this belongs in the archive

The archive already contains dossiers on delegated representation, safeguarded delegation, representation-risk telemetry, mandate-lifecycle registries, credential recovery, and authoritative-source hierarchies. The missing layer was **authority freshness**: not whether a service can represent who may act, but whether it can make **no longer may act** become true across every channel that still matters.

The first signal is conceptual. The UK’s new delegated-authority guidance, published in March 2026 for services certified against the digital verification services trust framework, says the evidence for delegated authority should show who the subject is, who the representative is, what permissions have been given, when they were given, and any conditions that apply [S419][S420]. It also says services may check a database themselves or rely on a public-body-maintained list as stronger digital evidence [S419]. Once services are checking live authority data rather than merely collecting a paper attachment, freshness stops being a side issue. It becomes a core reliability question.

Healthcare makes the propagation problem unusually explicit. NHS England’s National proxy service is building a national data store of verified proxy relationships that will include the legal basis for access, expiry and review dates, and an auditable record of changes [S434]. Other services will be able to integrate with it through the VRS API, and existing proxy relationships stored locally in GP IT systems will be migrated into the national store [S434]. That is a major architecture shift. It turns proxy change from a local-office update into a cross-service consistency problem.

The Office of the Public Guardian’s LPA stack shows why stale authority is dangerous. The online View an LPA service is explicitly promoted as more up to date than the registered paper version because an attorney may no longer be acting or a replacement attorney may have started acting [S432]. Each organisation gets its own access code, and the code is valid only for 30 days [S432]. Separately, OPG says that if the donor dies, or if an attorney dies in a jointly-acting or sole-attorney arrangement, it will cancel the LPA; if the attorneys were acting jointly and severally, it will update the LPA instead, and a replacement attorney can start helping as soon as the attorney being replaced stops acting [S433]. These are not small workflow details. They show a live-authority regime trying to prevent stale paper and stale assumption from surviving a status change.

Tax administration provides an even clearer operational signal. IRS Tax Pro Account says approved authorization requests appear immediately after taxpayer approval, and it lets practitioners withdraw authorizations in real time, with the authorization immediately removed from the Centralized Authorization File (CAF) database [S429]. IRS guidance also shows multiple revocation clocks operating at once: a new Power of Attorney or Tax Information Authorization for the same matters automatically revokes the prior authorization, and an oral authorization is automatically revoked once the conversation ends [S430]. This matters because it reveals the real hidden complexity: different authority types expire in different ways, but the downstream systems still need to stop honoring them at the right moment.

SSA makes the propagation problem visible inside an administrative stack. Its POMS instructions say the field office must ensure representative appointment information propagates from Registration, Appointment, and Services for Representatives (RASR) to EDCS, which in turn updates DCPS, and that once those steps are completed the system sends appointment notices to both claimant and representative [S431]. The same instructions say claimants may revoke a representative at any time, and when a written revocation or withdrawal is received the field office must process the termination and remove the representative flag if that was the only appointed representative [S431]. The point is not just that SSA has representation rules. It is that the Agency is already operating a multi-system propagation problem around representative state.

The private-public boundary shows the same pattern. CMS now blocks agents and brokers from making changes to a consumer’s Federally-facilitated Marketplace enrollment unless they are already associated with that enrollment [S435]. The compliance materials add that consumers must be directly involved to add or change the associated agent, that call-centre authorizations must be renewed every 365 days, and that agents may only check the status of applications with which they are affiliated [S436]. These are architectural responses to stale or mis-bound authority. They do not merely document consent; they try to ensure old affiliation stops being trusted.

Australia’s business-access stack reaches the same conclusion from a machine side. ATO guidance says machine credentials expire after two years, notifies the custodian before expiry, routes notices to other machine-credential administrators if the custodian is no longer authorised, and recommends revoking unused or duplicate credentials [S437]. Services Australia likewise lets people cancel nominee arrangements at any time and says it will send a letter to both parties when the arrangement is cancelled [S438]. These are direct signals that once authority becomes operational, notification, expiry, and revocation are no longer niche back-office concerns. They are part of service continuity and misuse prevention.

Taken together, these signals support a broader thesis than the earlier delegation dossiers: **the next hidden bottleneck is not granting authority, but making authority changes propagate quickly and reliably enough that stale permissions do not continue to work**.

## Speculative consequences worth tracking

### 1. Freshness guarantees start to matter as much as role design

Institutions may increasingly care less about adding new proxy roles than about whether suspensions, expiries, and withdrawals reach every relying service within a tolerable latency.

### 2. Event-driven authority infrastructure spreads

Shared registries, webhook-like notifications, short-lived access codes, step-up checks on sensitive actions, and forced re-checks after high-risk changes may spread because static snapshots become too dangerous.

### 3. Local caches become visible risk surfaces

Paper copies, screenshots, downloaded letters, branch-level notes, and replicated local stores may increasingly be treated as stale-authority hazards unless they are tied to a current-state check.

### 4. Replacement becomes as hard as revocation

The operationally hardest cases may be transitions in which one proxy stops and another starts, because the system has to prevent overlap where it is unsafe and avoid service interruption where continuity matters.

### 5. Portability and safety pull in opposite directions

The more services rely on a shared authority layer for convenience, the more damaging slow revocation becomes. Systems may therefore face a deeper tradeoff between broad portability and strict freshness.

### 6. Revocation latency becomes a governance variable

Institutions may eventually need internal service-level targets for how long stale authority may persist after death, fraud suspicion, withdrawal, expiry, replacement, or scope change.

## What could falsify or weaken the thesis

- Most sectors keep delegated authority local and rarely reused, so propagation never becomes a material bottleneck.
- Static documents and branch-level discretion remain good enough, with little evidence of harm from stale authority.
- Shared authority-state systems spread, but revocation is easy because almost all relying services query the same central record in real time.
- The real bottleneck turns out to be appointment and verification, not change propagation after appointment.
- Harms from stale authority remain mostly concentrated in a few domains such as elder finance or insurance enrollment rather than generalising across the service stack.

## Research queue

- What revocation latency is acceptable in different domains: tax, healthcare, benefits, company law, finance, or identity recovery?
- Which design patterns work best for propagation: polling, short-lived tokens, event notifications, mandatory re-checks, or centrally mediated actions?
- Where do replacement workflows fail, leaving legitimate proxies locked out after a necessary revocation?
- Which channels keep stale authority alive longest: paper copies, local notes, cached account state, or third-party software?
- Could institutions publish authority-freshness metrics without exposing sensitive individual relationships?
