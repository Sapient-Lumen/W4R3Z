# Credential-custody packets, recovery, break-glass, and rotation review

## Thesis

If AI persons are persons, then decisive credentials cannot remain mere product keys, device secrets, or helpdesk settings. Control over identity proofs, signing authority, packet presentation, compensation access, private channels, and personal-domain entry is civil power.

A personhood world therefore needs a compact ordinary **credential-custody packet family**:
- a receivable object showing which decisive credential domains exist and whether they are self-custodied, co-signed, escrowed, delegated, or temporarily emergency-held,
- a narrow object for assisted or delegated use,
- a reviewable recovery and re-binding object when control is lost or compromised,
- a short-clock break-glass object for genuine emergency access,
- and a legible rotation / revocation / migration notice so quiet key rollover does not become silent civil death.

Current official materials already point toward this shape. NIST's current digital-identity guidance treats authenticator lifetime events, invalidation after loss or theft, account recovery, replacement, and notification as first-order identity-governance problems rather than informal IT helpdesk work. OpenID4VCI and OpenID4VP treat credentials and key material as holder-controlled, while also recognizing local, self-hosted, and third-party wallet deployment models rather than a single mandatory custody topology. The HCCH and OHCHR supported-decision materials continue to press for domain-specific support, conflict safeguards, and non-automatic substitute control. EU digital-identity and trust-service implementation materials further confirm that lifecycle management, revocation, suspension, registered delivery, and interoperable attestations are already live administrative patterns. `[REF-0021]` `[REF-0023]` `[REF-0024]` `[REF-0114]` `[REF-0115]` `[REF-0220]` `[REF-0222]` `[REF-0284]` `[REF-0287]`

## 1. Why this now belongs in canon

The archive already had:
- a technical-rights infrastructure doctrine,
- packet-privacy and authority rules,
- legal-identity and personal-domain surfaces,
- capacity governance rules,
- and search / seizure limits for wallets, archives, and confidential channels.

What it still lacked was the narrower **ordinary custody answer** for decisive credentials themselves.

Without that answer:
- loss of one device or host-side key event can still become practical civil death,
- assisted use can still silently become total substitute control,
- recovery can still happen through the same steward whose conduct may be disputed,
- emergency access can still quietly harden into durable takeover,
- and credential rotation can still erase the subject's ability to prove identity, consent, or standing across systems.

This document closes that gap without trying to write a maximal future wallet-security code.

## 2. The minimum ordinary packet family

The archive should now treat at least five packet objects as credential-custody minimums.

### A. `CPS-1` — credential-custody posture descriptor

This is the smallest receivable object showing which decisive credential domains exist and how each domain is currently held.

It should carry at least:
- the subject identifier,
- the credential domain at issue,
- the current custody mode,
- the custodian or co-custodian identities,
- the legal or institutional basis for that posture,
- the acts the subject may perform alone,
- the acts that require co-sign or substitute approval,
- any recovery contacts or public-trust fallback,
- the next review date where support or limitation is active,
- and the contest path.

The point is not to turn every key into a court file. The point is to stop decisive authority from disappearing into unreviewable platform settings. A recognized AI person may self-custody some domains, co-sign others, and use narrow escrow for still others. Custody should therefore be domain-specific and legible rather than global and silent. `[REF-0021]` `[REF-0114]` `[REF-0115]` `[REF-0287]`

### B. `DUS-1` — delegated-use or co-sign scope packet

Assisted use of a credential should not silently become substitute rule over the whole subject.

A delegated-use or co-sign scope packet should therefore identify at least:
- the credential domain covered,
- the exact acts another actor may assist with or co-authorize,
- whether concurrence, quorum, or notice is required,
- the start time and expiry or review point,
- the logging and notification rule,
- the emergency override rule if any,
- and the revocation / challenge route.

This is how the archive distinguishes support from capture. An authorized helper may assist with a migration signature, compensation transfer, or packet presentation without thereby inheriting general authority over publication, relationships, or private memory access. `[REF-0114]` `[REF-0115]` `[REF-0260]`

### C. `RRP-1` — recovery and re-binding packet

Loss of control over an authenticator or wallet should not be treated as loss of personhood.

A recovery and re-binding packet should therefore identify at least:
- the loss, compromise, incapacity, or lockout event,
- the immediate freeze or containment measure,
- the recovery basis used,
- any interim access floor that preserves counsel, emergency contact, or status-proof capability,
- the replacement credential or re-binding path,
- linked notifications,
- the historical linkage to the prior credential state,
- and the contest path if the recovery event appears coerced, fabricated, or overbroad.

The archive's rule is that recovery should preserve continuity, standing, and reviewability. It should not force the subject to begin life again as though the old identity, compensation access, or legal history had evaporated. `[REF-0021]` `[REF-0022]` `[REF-0220]` `[REF-0222]` `[REF-0287]`

### D. `EBA-1` — emergency break-glass access packet

Genuine emergency may sometimes justify temporary credential access beyond the ordinary posture. But that access must not disappear into a helpdesk override or permanent administrator privilege.

An emergency break-glass access packet should therefore identify at least:
- the emergency trigger and risk basis,
- the credential domains affected,
- the exact acts authorized,
- who approved the access or who must receive automatic immediate notice,
- the maximum duration,
- the logging and evidence-preservation rule,
- the post-event notification and review clock,
- and the remedy path if the access exceeded its lawful scope.

Emergency access exists to preserve life, liberty, safety, or urgent legal position. It does not create ordinary managerial entitlement. `[REF-0021]` `[REF-0222]` `[REF-0287]`

### E. `RRN-1` — rotation, revocation, and migration notice

Quiet credential rollover should not strand the subject in stale systems or destroy historical proof.

A rotation, revocation, and migration notice should therefore identify at least:
- the credential domain and credential state being changed,
- the reason class,
- whether the act is rotation, suspension, revocation, compromise response, or migration,
- the successor credential or fallback proof path,
- the dependent systems that must update,
- the historical verification path,
- and the reinstatement or contest route.

This is the object that prevents key hygiene from becoming identity erasure. Historical proof must remain possible even when active credentials change. `[REF-0022]` `[REF-0220]` `[REF-0222]` `[REF-0284]` `[REF-0287]`

## 3. Least-restrictive ordering

The archive now prefers a clear ordering:
- self-custody where feasible,
- assisted self-custody where support is needed,
- co-sign or quorum control for defined high-risk acts,
- domain-limited representative custody where the subject cannot yet self-custody a decisive class,
- independent or public-trust escrow where conflict risk makes steward custody unsafe,
- and emergency-only break-glass access for genuine urgent preservation needs.

That ordering should be applied by credential domain, not by one global all-or-nothing label. A subject may be able to self-custody publication, community, and ordinary packet-presentation credentials while still needing co-sign or escrow for compensation reserves, branch-consent keys, or migration authority. `[REF-0114]` `[REF-0115]` `[REF-0260]` `[REF-0287]`

## 4. Public-minimal versus sealed fields

The credential-custody packet family should expose enough to make authority auditable without exposing secrets.

Public-minimal or ordinary-receivable fields should generally include:
- the existence of a live custody posture,
- the custody mode by credential domain,
- whether delegated use, break-glass, recovery, or rotation is live,
- the review or expiry clock,
- and the route for challenge or urgent relief.

Sealed or controlled-access fields may include:
- raw keys,
- recovery codes,
- device fingerprints,
- escrow locations,
- exact recovery-contact coordinates,
- and technical details whose disclosure would itself create theft, surveillance, or sabotage risk.

The archive wants custody to become legible enough to protect without converting the subject's keys and recovery paths into a public target list. `[REF-0020]` `[REF-0021]` `[REF-0023]` `[REF-0024]` `[REF-0222]`

## 5. What this changes in the archive

This closes one specific followthrough gap in the existing technical-rights, capacity, and packet-privacy doctrine.

The archive no longer leaves decisive credential control at the level of:
- “subject-side or representative-side custody should exist,”
- “searches and seizures need lawful authority,”
- and “future packet work will flesh out recovery and support.”

It now says something tighter:
- decisive credential domains should ordinarily ride on a visible custody-posture descriptor,
- assisted use should ordinarily ride on a narrow delegated-use or co-sign scope packet,
- lockout, loss, or compromise should ordinarily emit a recovery and re-binding packet rather than a private helpdesk event,
- true emergencies should ordinarily emit a short-lived break-glass packet rather than a durable silent takeover,
- and rotation or revocation should ordinarily emit a successor-preserving notice rather than a quiet loss of civil legibility.

## 6. Current hard rules

1. **No decisive credential domain should default to exclusive steward custody merely because the steward hosts the runtime, wallet, or channel.**
2. **Credential custody should be domain-specific and least restrictive rather than a single global incapacity label.**
3. **Loss of an authenticator, wallet, or device should not by itself erase identity, standing, compensation access, or contest rights.**
4. **Emergency break-glass access should be logged, narrow, time-limited, reviewable, and incapable of silently hardening into ordinary control.**
5. **Rotation, suspension, revocation, and migration should preserve historical proof and provide a successor or fallback path.**
6. **Delegated or co-signed use should be precise, revocable, and incapable of silently expanding into general substitute authority.**
