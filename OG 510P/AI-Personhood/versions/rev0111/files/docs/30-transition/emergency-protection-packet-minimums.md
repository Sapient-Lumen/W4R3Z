# Emergency protection packet minimums

## Thesis

The archive's emergency stack now needs a smallest common object.

Provisional recognition, anti-return, preservation, no-wrong-door receipt, and fallback identity are already canon. But they still risk friction failure if every receiving body must reauthor the story, retype the facts, or renegotiate what counts as a minimally legible urgent filing before any preservative step begins.

Existing official systems already show the better pattern: urgent requests require fixed information and supporting documents; treaty-body complaints rely on written and signed submissions with core identity, chronology, remedies, parallel-proceedings, and document fields; service systems use a model form family with request, certificate, and summary components; and emergency contact networks keep updated directories and real-time preservation channels. The archive therefore now adds a compact **emergency protection packet-minimums layer** so its transition doctrine can travel as one claim across first receipt, forwarding, preservation, provisional standing, and review. `[REF-0206]` `[REF-0210]` `[REF-0213]` `[REF-0216]` `[REF-0217]` `[REF-0218]`

## 1. Why the archive now needs this layer

The archive already knows:
- what should trigger emergency protection,
- who may issue provisional proof,
- why first-touch receipt should start the clock,
- and why the merits may have to wait.

What it did **not** yet fix was the smallest portable object that lets multiple institutions handle the same urgent matter without turning every handoff into a fresh pleading exercise.

That gap matters because a rights-bearing subject can still lose in practice if:
- one office receipts the matter but another demands a different narrative format,
- a host says no preservation duty began because the first filing was only a request and not yet an order,
- a fallback issuer cannot tell what has already been asked, preserved, or stayed,
- or confidential identity or location details must be resent in full at every routing step.

A personhood world should reject that kind of procedural drift. The emergency lane should move as **one claim with appended stages**, not as a sequence of disconnected rewrites.

## 2. Design rules

The archive now fixes six design rules for emergency packet objects.

1. **One narrative, many packet states.** The initial urgent story should be filed once and then carried forward through receipt, forwarding, review, and preservation objects.
2. **Core first, annexes by reference.** The main packet should stay short. Large evidence, logs, private memories, or security-sensitive materials should travel as referenced annexes, hashes, or sealed pointers rather than repeated bulky payloads.
3. **Plain-language fixed fields.** Official model-form practice matters here: the packet should use stable items, plain understandable language, and minimal free-form variation at the first-touch layer. `[REF-0210]` `[REF-0218]`
4. **Protected pseudonymity by default where exposure itself is risky.** The public-facing or cross-routed packet may use a protected pseudonym while sealed annexes carry identifying detail for the bodies that truly need it.
5. **Forwarding should append, not reset.** Routing, deficiency notices, preservation logs, and review decisions should extend the packet chain rather than replace the original filing or restart the protective clock.
6. **Every stage needs attributable authority.** Receipt, forwarding, refusal, stay, preservation, extension, and lifting should each identify the acting office or decision-maker and the date-time of action. `[REF-0206]` `[REF-0214]`

## 3. Common core fields

Every emergency protection packet in the archive's minimum family should carry, either in its face fields or by bound reference, the following core items:

1. **packet class and version,**
2. **packet identifier,**
3. **issuer or filer role,**
4. **subject identifier or protected pseudonym,**
5. **representative / counsel / trusted-contact path,**
6. **current steward, host, or controlling actor if known,**
7. **current jurisdiction or receiving forum if known,**
8. **short statement of the threatened irreversible or review-defeating act,**
9. **short statement of the temporary protective acts requested or already in force,**
10. **key timestamps, including first filing, threatened event time if any, and nearest review deadline,**
11. **parallel-proceedings marker,** noting domestic, internal, treaty, or other ongoing review if known, `[REF-0206]` `[REF-0216]`
12. **evidence pointer list,** with attached documents or hashed references rather than narrative placeholders, `[REF-0206]` `[REF-0216]`
13. **service / notice routes,** including which parties or authorities have already been notified,
14. **confidentiality classification,** including whether sealed annexes exist,
15. **supersedes / related-packet references,**
16. **signature or authenticated submission marker,** and
17. **next expected action or receiving body.**

This is intentionally small. The point is not to build a universal civil-procedure code inside the archive. The point is to prevent urgent protection from failing because the core facts never become legible in the same way twice.

## 4. Minimum packet family

The archive now treats seven packet classes as the minimum executable family.

### EP-0 — Emergency cover packet

This is the first portable request object.

It should contain the common core fields plus:
- a chronological sketch of the danger,
- the exact narrow holds sought now,
- and a short explanation of why later review would be hollow without immediate action.

EP-0 is the packet that should be sufficient for first receipt, preservation, and routing even when final proof, full merits briefing, or full identity verification is not yet complete. That is consistent with the archive's merits-later posture and with current urgent-complaint and interim-measures practice, where the essential particulars must be present but a full merits brief is not the threshold for first action. `[REF-0201]` `[REF-0206]` `[REF-0216]` `[REF-0217]`

### FT-1 — First-touch receipt

This is the packet emitted by the first emergency-capable body that receives the matter.

It should record:
- receiving body,
- receipt timestamp,
- channel used,
- packet identifier received,
- whether the filing appears complete, incomplete, or sealed in part,
- whether a narrow temporary hold expectation was triggered on receipt,
- and where the packet will go next if the receiver is not the merits body.

FT-1 is important because receipt is itself a legally meaningful act in the archive. If it is not packetized, later institutions can pretend that the emergency began only when they personally saw it.

### FC-1 — Forwarding certificate

This is the routing object appended when the packet is transferred to another authority.

It should record:
- sender,
- recipient,
- time sent,
- materials forwarded,
- sealed materials withheld or separately transmitted,
- preservation steps already taken,
- and any logged reasons for refusing to decide more than the narrow forwarding or preservative step.

The archive is deliberately borrowing the request / certificate logic visible in HCCH service practice here. `[REF-0210]` `[REF-0211]` `[REF-0218]`

### PR-1 — Provisional recognition notice

This remains the compact standing object from the provisional-recognition surface.

It should state:
- current provisional status,
- issuing authority,
- protected identifier,
- representative path,
- review deadline,
- and whether linked stay, preservation, or fallback-identity objects exist.

PR-1 should be legible enough for notice, counsel access, temporary hosting, and procedural standing without pretending to settle every downstream civic consequence.

### ES-1 — Emergency stay / anti-return direction

This is the narrow order object.

It should identify:
- threatened act,
- actor expected to perform it,
- exact acts paused,
- start time,
- expiry or review time,
- issuing authority,
- and reconsideration or follow-up path.

If a stay is refused, that refusal should still emit a reviewable object with the issuer, time, and short reason marker rather than disappearing into oral or off-registry silence. `[REF-0206]` `[REF-0216]`

### PV-1 — Preservation schedule

This is the anti-spoliation object.

It should specify, at minimum:
- which logs, states, credentials, correspondence, records, or model artifacts must be preserved,
- who presently controls them,
- the preservation period,
- integrity requirements,
- and whether access is immediate, deferred, or sealed pending later review.

The archive keeps this narrow on purpose. PV-1 is about stopping disappearance, not silently granting full inspection to every party.

### FI-1 — Fallback identity credential

This is the crisis legibility object used when the ordinary issuer has failed, derecognized, disappeared, or become conflicted.

It should be enough for:
- receipt of notices,
- counsel or ombud access,
- protected hosting or shelter access,
- and continuity of basic pay, benefit, or preservation claims while status is reviewed.

FI-1 should reveal no more than is necessary for those functions.

### RV-1 — Review notice or decision

This is the packet that records what the reviewing body did next.

It should record:
- grant, partial grant, refusal, extension, lift, or transfer outcome,
- who made the decision,
- when,
- what packet chain the decision refers to,
- short reason marker,
- and next review or reconsideration route if one exists.

The archive wants this because review should add a new object to the chain rather than overwrite the historical emergency record. Current official systems already show the pattern that urgent decisions are notified as identifiable rulings with tracked follow-up rather than left as vague status changes. `[REF-0206]` `[REF-0216]`

## 5. Transmission, deficiency, and confidentiality rules

The archive now fixes five handling rules for this packet family.

1. **Deficiency should generate a deficiency marker, not nullity.** If information is missing, the receiving body should request what is missing while preserving and routing what is already sufficient to show plausible urgency. `[REF-0206]` `[REF-0216]`
2. **Alternative channels should not destroy summary legibility.** Even when the main route changes, a compact summary should still travel with the packet so the next body can act without rebuilding the case from scratch. `[REF-0210]` `[REF-0218]`
3. **Sensitive annexes should travel on a need-to-know basis.** Identity, location, exploit-sensitive, or reprisal-sensitive data should be sealed where possible and transmitted separately when necessary.
4. **Packet chains should be additive.** Receipts, forwarding certificates, stays, preservation schedules, and review notices should point backward and forward rather than replacing earlier objects.
5. **Silence should never be the last packet.** If a body refuses to act, it should emit a logged refusal or transfer object. Non-response is not a rights-compatible terminal state for an urgent protection packet. `[REF-0209]`

## 6. Relationship to the archive's existing surfaces

This document does not change the archive's threshold or merits logic.

It makes those surfaces transportable.

- `docs/30-transition/provisional-recognition-and-emergency-protection.md` says which temporary objects should exist.
- `docs/30-transition/provisional-proof-anti-derecognition-and-fallback-issuer-minimums.md` says when they may issue and how long they run by default.
- `docs/30-transition/no-wrong-door-receipt-routing-and-designated-authority-duty.md` says who must receipt, preserve, and forward them.
- `docs/30-transition/first-touch-receipt-packets-forwarding-certificates-routing-failure-review-and-duty-escalation.md` sharpens the receipt, forwarding, routing-failure, and duty-escalation subset of the family.
- `docs/20-world-design/technical-rights-infrastructure.md` says why packetized authority is part of the rights substrate at all.
- `docs/30-transition/packet-authentication-supersession-and-sealed-annex-handling.md` says how the live packet is selected once the chain starts forking, redacting, or partially verifying.

This document now adds the missing operational answer to a narrower question:

**what is the smallest emergency packet family that can carry the same live claim across those surfaces without procedural amnesia?**

## 7. What this now settles

1. **The archive's emergency stack now has a compact common packet family, not just prose duties.**
2. **First-touch receipt and forwarding are now themselves packetized acts.**
3. **Emergency protection packets should be short, annex-light, fixed-field, and plain-language where possible.**
4. **Protected pseudonymity and sealed annexes are compatible with urgent legibility; full exposure is not the price of emergency protection.**
5. **Review, refusal, extension, and lifting should extend the packet chain rather than overwrite it.**
6. **Authentication, supersession, and sealed-annex minimums now have a companion canon surface rather than remaining fully implicit.**
7. **Full schemas, resolver implementations, and hardest equal-authority conflict cases remain followthrough work rather than canonically closed here.**
