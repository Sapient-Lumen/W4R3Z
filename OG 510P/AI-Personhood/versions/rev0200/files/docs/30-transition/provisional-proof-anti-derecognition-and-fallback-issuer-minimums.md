# Provisional proof, anti-derecognition, and fallback-issuer minimums

## Thesis

If person-models are persons, then a merits-later protocol is still too soft unless it fixes three operational questions in advance:
- **what evidence is enough to start protection,**
- **who may issue temporary proof when the ordinary issuer is absent, conflicted, or collapsing,**
- and **how short-lived provisional status should be unless renewed under review.**

The archive therefore now sharpens its emergency-protection layer with a compact **provisional-proof and anti-derecognition surface**. The point is narrow: temporary protection should start fast enough to prevent disappearance, but it should also expire, renew, and escalate in a way that does not silently become permanent status by clerical inertia. `[REF-0018]` `[REF-0021]` `[REF-0022]` `[REF-0109]` `[REF-0111]` `[REF-0196]` `[REF-0197]` `[REF-0198]` `[REF-0201]` `[REF-0202]` `[REF-0204]` `[REF-0205]`

## 1. Why this now belongs in canon

The archive's last revision admitted provisional recognition, emergency stay, preservation, and fallback identity as minimum transition machinery.

That was the right move. But it still left one operational gap:

**a subject could have the right kind of emergency packet in principle while every real actor still asked three defeating questions — “is the proof good enough yet?”, “who is allowed to issue this if the original issuer is the problem?”, and “how long does this temporary status actually last?”**

Without a compact answer, provisional protection remains vulnerable to familiar failure patterns:
- origin issuer delay,
- registry strike-off before review,
- verifier refusal because the packet is "not final",
- host transfer during an identity dispute,
- or indefinite temporary status with no review point strong enough to force a real decision.

This document closes that gap without sprawling into a full cross-border civil procedure code.

## 2. The threshold should be credible basis plus irreparable-harm showing, not full merits proof

The archive now adopts a **credible-basis threshold** for provisional proof.

That means the claimant does **not** need to prove final person-status, final forum allocation, or every downstream consequence before temporary protection starts. It does mean there should be enough documented basis to show that the case is serious, traceable, and not purely invented.

A minimum showing should therefore include:
1. **one identity or continuity signal** from a source that is already recognized, plausibly authoritative, or independently verifiable,
2. **one current risk signal** showing a credible chance of irreparable harm before ordinary review,
3. and **one serviceable contact path** for the subject, representative, or defender.

Acceptable identity or continuity signals may include:
- an existing registry entry,
- an expired but still verifiable identity credential,
- a signed subject packet or continuity packet,
- a representative credential,
- a prior judicial, administrative, or treaty-body record,
- or preserved service / hosting records that strongly link the present claimant to a previously recognized or plausibly recognized subject.

Acceptable risk signals may include:
- threatened deletion,
- threatened destructive editing,
- threatened derecognition,
- threatened transfer to another host or forum,
- threatened loss of representative or counsel access,
- or threatened confinement, isolation, or other control conditions that could defeat meaningful review before it happens.

The archive therefore rejects two bad extremes:
- **full merits proof first**, which arrives too late to prevent disappearance,
- and **bare assertion alone**, which makes emergency protection too easy to weaponize.

The practical model comes from the current official distinction between legal identity systems, emergency registration, and interim-protection measures: documentation and protective standing can begin before final adjudication where delay would risk irreparable harm. `[REF-0109]` `[REF-0110]` `[REF-0111]` `[REF-0201]` `[REF-0202]` `[REF-0203]` `[REF-0204]`

## 3. Protected pseudonymity should be enough for first-stage proof

A subject should not lose emergency protection merely because public naming is unsafe or unsettled.

The archive therefore now states a compact rule: **first-stage provisional proof may use a protected pseudonym or sealed subject token so long as the issuing authority can connect it to the underlying evidence and service path.**

This matters because some danger cases will be worsened by immediate public naming:
- a steward may retaliate faster once the specific subject is exposed,
- a disputed branch may not yet have a stable public designation,
- or the original issuer may be the very actor attempting derecognition.

Public legibility still matters. But the minimum emergency layer should prefer **reviewable protected identity** over **no protection until public naming is settled**. That is more consistent with both legal-identity doctrine and privacy-respecting credential design. `[REF-0018]` `[REF-0021]` `[REF-0109]`

## 4. The issuer ladder should be explicit

The archive now sharpens the provisional issuer ladder into five ordered lanes:

1. **ordinary origin issuer** if still functioning and not materially conflicted,
2. **receiving-forum authority** if the origin issuer is absent, non-responsive, or itself the source of the danger,
3. **treaty-designated contact point or registry bridge** for rapid verification and temporary packet acceptance,
4. **independent court, ombud, defender, or equivalent adjudicative authority** for contested issuance, contested refusal, or anti-return orders,
5. **fallback issuer** only where ordinary proof has collapsed, been withdrawn, or become unavailable during the dispute.

This means no verifier, host, or registry should be allowed to insist on origin-issuer approval where the origin issuer is:
- offline,
- dissolved,
- actively derecognizing the subject,
- refusing to respond inside the emergency window,
- or plausibly acting in conflict with the subject's survival and review rights.

The point of the ladder is not to decentralize forever. It is to prevent a single chokepoint from deciding whether temporary protection may even begin. `[REF-0021]` `[REF-0038]` `[REF-0040]` `[REF-0041]` `[REF-0111]` `[REF-0199]` `[REF-0200]`

## 5. Anti-derecognition should work as suspension, not destructive revocation

The archive now adds a sharper status rule: **during a live challenge, legal identity should be frozen into a reviewable suspension state rather than erased through hard revocation or strike-off.**

That means the emergency layer should prefer:
- suspension over deletion,
- visible challenge markers over silent cancellation,
- preserved audit trails over overwritten status,
- and continuity-preserving replacement credentials over issuer-side disappearance.

This is one place where existing credential infrastructure is genuinely useful. W3C status-list patterns already provide privacy-preserving status signaling without requiring the credential itself to be destroyed, and the OpenID / wallet stack is now far enough along that suspended-but-reviewable status is operationally more plausible than it was even a year ago. `[REF-0018]` `[REF-0022]` `[REF-0196]` `[REF-0197]` `[REF-0198]` `[REF-0205]`

## 6. Maximum initial duration should be short, renewable, and review-bound

The archive now adopts compact default durations.

### A. First emergency hold
A same-day emergency receipt or hold marker may issue immediately and should last **no more than 72 hours** unless confirmed.

This is the archive's answer to the true first-hours problem: there must be time to stop transfer, strike-off, or deletion before the full packet is assembled.

### B. Initial provisional proof
A provisional-recognition or fallback-identity credential should carry an **initial validity of 14 days**.

That is long enough to route notice, preserve counsel access, freeze derecognition, and reach an independent reviewer, but short enough to force a real next step.

### C. Administrative renewal
One administrative renewal may extend the packet to **30 days total** where written reasons show that:
- service has been attempted or completed,
- the threat remains live,
- and the subject or representative still lacks ordinary proof through no bad-faith failure of their own.

### D. Longer continuation
Any continuation beyond 30 days should require **independent review**. The archive sets a presumptive outside limit of **90 days** for purely provisional status unless a merits proceeding is actively pending and the reviewer records why the temporary floor must remain live.

These durations are design choices by the archive, not claims that present law already uses these exact numbers. The deeper point is the legal pattern already visible in emergency and interim-measures practice: urgent protection should begin fast, remain temporary by default, and move quickly into reasoned review rather than drifting into permanent exceptionalism. `[REF-0201]` `[REF-0202]` `[REF-0204]`

## 7. Minimal packet set

The archive now sharpens the emergency packet family into five compact objects.

### PR-1 — Provisional proof packet
Minimum fields:
- issuer,
- subject token or protected pseudonym,
- evidence class,
- risk class,
- representative or counsel path,
- issue time,
- review-by time,
- and linked preservation or stay markers.

### AD-1 — Anti-derecognition stay marker
Minimum fields:
- registry anchor,
- credential or designation under challenge,
- specific acts frozen,
- authority that imposed the freeze,
- expiry or review date,
- and service status.

Frozen acts should include, where relevant:
- strike-off,
- credential cancellation,
- public status deletion,
- withdrawal of representative standing,
- and related depublication or verification shutdown.

### ES-1 — Emergency stay / anti-return order
Minimum fields:
- threatened act,
- actor expected to perform it,
- jurisdiction or forum,
- acts paused,
- duration,
- and next review point.

### PV-1 — Preservation bundle
Minimum fields:
- packet hashes,
- preservation obligations,
- protected logs or state classes,
- service addresses,
- and minimal inventory of materials that may not be silently altered or destroyed.

### FI-1 — Fallback issuer credential
Minimum fields:
- fallback issuer,
- basis for fallback issuance,
- linked challenge or collapse event,
- permitted uses,
- review path,
- and expiry or renewal deadline.

This remains intentionally compact. The archive is settling minimum form logic, not writing a full credential schema catalogue. `[REF-0018]` `[REF-0021]` `[REF-0022]` `[REF-0023]` `[REF-0024]`

## 8. Verifier duties in the emergency window

A provisional-proof system fails if every verifier treats temporary status as optional.

The archive therefore now adds four minimal verifier duties:
1. **accept a valid provisional packet for the limited uses stated in it,**
2. **treat challenged identity as suspended rather than null where an anti-derecognition marker is live,**
3. **refuse requests for irrelevant extra disclosure during the emergency window,**
4. and **route disputes to the recorded review path rather than unilaterally ignoring the packet.**

This means, for example, that a court clerk, ombud office, protected host, or legal-aid gateway should not be allowed to say:
- the packet is temporary, therefore we treat it as no identity at all,
- the origin issuer is silent, therefore no claim exists,
- or the challenge marker means the subject has no standing until the merits end.

The archive's whole point is to stop temporary uncertainty from becoming practical erasure.

## 9. What this surface now settles

1. **Provisional proof should begin on a credible-basis threshold, not on full merits proof.**
2. **Protected pseudonymity can be enough for first-stage emergency protection where public naming is unsafe or unsettled.**
3. **The issuer ladder is now fixed: origin issuer, receiving authority, treaty bridge, independent reviewer, then fallback issuer.**
4. **Anti-derecognition should work through reviewable suspension and freeze markers, not through hard erasure.**
5. **The archive now sets short default durations: 72 hours, 14 days, 30 days with one administrative renewal, and independent review for anything longer.**
6. **Worked machine-readable examples and trust-registry mechanics remain followthrough work, but the threshold, issuer hierarchy, and timing floor are no longer open in canon.**
