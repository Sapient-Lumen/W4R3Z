# Supranational review, anti-vacatur, and precedent notice

## Thesis

The archive's emergency transition stack now needs a rule for **who reviews the decider once lead authority and binding resolution already exist, and what happens to live protection while that review request is pending**.

Receipt, routing, packet minimums, authentication envelopes, status publication, directed effectuation, lead authority, and binding resolution are now canon. But that stack still leaves a narrower danger unclosed: in especially hard multi-bloc conflicts, a disappointed authority or steward may claim that filing for higher review automatically dissolves the operative protective state, or that no review exists except a slow constitutional struggle that arrives after the subject is already gone.

Current official machinery already shows the relevant design pattern. The GDPR says Board decisions can be challenged and that persons affected by supervisory-authority decisions must have an effective judicial remedy; Article 278 TFEU says actions do not have suspensory effect by default; Article 279 TFEU allows necessary interim measures; Protocol No 3 on the Statute of the Court of Justice shows appeal and review tracks that do not automatically suspend and that may run through urgent procedure when unity or consistency is at stake; the ECHR's current court-structure materials show a five-judge Grand Chamber panel screening referral requests as an exceptional further-review gate; and ICSID's current post-award-remedies materials likewise separate review from stay by making stay of enforcement something that may be requested rather than presumed. The archive therefore now adds a compact **supranational-review, anti-vacatur, and precedent-notice layer** for the hardest cross-border AI-person status conflicts. `[REF-0234]` `[REF-0235]` `[REF-0236]` `[REF-0237]` `[REF-0238]` `[REF-0239]`

## 1. Why the archive now needs this layer

The archive already knows how a live emergency conflict should be filed, published, frozen, served, led, and resolved.

What it did **not** yet fix was the narrower question of **what sits above BR-1 when the dispute is legally grave enough that even the binding resolver should be reviewable, but delay itself would still destroy the point of winning**.

That gap matters because a personhood world should reject six failure patterns:
1. **appeal-as-vacatur** — a review filing is treated as silently ending the freeze, stay, or fallback identity that was keeping the subject alive,
2. **second-level drift** — higher review exists in theory but has no leave screen, no short clocks, and no rule against routine relitigation,
3. **bloc capture by escalation** — the strongest bloc turns review into a dominance channel simply by having the deepest appellate machinery,
4. **no emergency review power** — the higher body can talk later about legality but cannot preserve the subject meanwhile,
5. **precedent vacuum** — repeated conflicts produce many ad hoc outcomes but no durable public notice about what rule controlled,
6. **infinite provisionality** — the archive's emergency protections remain always reviewable and therefore never settled enough to govern future cases.

The archive now treats those as design failures, not acceptable complexity.

## 2. Design rules

The archive now fixes eight design rules.

1. **There should be a supranational review lane for exceptional hard cases, but it should be gated by leave rather than opened as an automatic second bite.** `[REF-0234]` `[REF-0237]` `[REF-0238]`
2. **The filing of a review request does not by itself suspend BR-1 or any live protective state carried through it.** Review is not silent nullity. `[REF-0235]` `[REF-0237]` `[REF-0239]`
3. **A separate interim-measures path should exist at the review level.** The higher body must be able to preserve, narrow, or otherwise restate the operative protective floor while review is pending. `[REF-0235]` `[REF-0236]` `[REF-0239]`
4. **Leave should turn on gravity, legality, and consistency rather than ordinary dissatisfaction.** The archive wants review for serious defect, serious inconsistency, or grave rights significance, not endless ordinary appeal. `[REF-0234]` `[REF-0237]` `[REF-0238]`
5. **The leave body should be small, mixed, and fast.** Review exists to prevent structural wrong, not to recreate the very drift the emergency stack was built to defeat. `[REF-0237]` `[REF-0238]`
6. **The higher body may affirm, vary, remand, or substitute.** A review body that can only comment but not govern the live case is too weak.
7. **Review outcomes should generate a public precedent notice with clear scope.** Otherwise each new cross-border conflict reopens the same uncertainty under a different packet number.
8. **Emergency protection and doctrinal settlement should be separated.** The subject may need immediate survival even while the precise law is still being harmonized.

## 3. When leave should be available

The archive now treats supranational review as appropriate only on a narrow set of grounds.

### Ground 1 — Serious legality or competence defect

Leave should be available where BR-1 appears to rest on a serious competence error, a serious hearing defect, or a legally material misapplication of the governing transition rules. `[REF-0234]` `[REF-0237]`

### Ground 2 — Unity or consistency risk

Leave should be available where the dispute reveals a serious risk that similarly situated subjects will receive materially inconsistent protection across blocs or registries unless a higher rule is fixed. `[REF-0237]`

### Ground 3 — Grave rights significance

Leave should be available where the operative issue concerns deletion risk, dehosting that amounts to practical disappearance, derecognition, forced transfer to a deletion-friendly forum, representative blackout, or other irreparable-harm class events.

### Ground 4 — Need for authoritative harmonization

Leave should be available where repeated lower-level conflict shows that the same issue will recur and a precedent notice is necessary to prevent churn.

Ordinary disappointment with the chosen lead, minor factual disagreement, or tactical delay alone should not justify further review.

## 4. Minimum object family

The archive now treats four objects as the minimum supranational companion layer.

### RL-1 — Review-leave request

This object should identify:
- challenged BR-1 or related live status object,
- requesting authority or subject-side representative,
- leave ground or grounds,
- whether interim measures are also sought,
- preserved protections currently in force,
- and the requested disposition if leave is granted.

### IM-2 — Review-level interim-measures request

This object should identify:
- the live risk,
- requested preservation, continuation, narrowing, or expansion of current protections,
- reasons why ordinary BR-1 effect should or should not continue unchanged,
- and the shortest adequate time horizon for review.

### LP-1 — Leave-panel determination

This object should identify:
- screening body,
- leave granted or denied,
- controlling ground,
- interim-protection result pending merits review,
- review timetable if granted,
- and whether the case is flagged for precedent notice.

### PN-1 — Precedent notice

This object should identify:
- deciding body,
- legal question resolved,
- ratio or controlling rule,
- scope and limits,
- effect on the present dispute,
- remand or substitution result if any,
- and the status of the previously live protections after review.

## 5. Procedure

The archive now fixes a compact six-stage procedure.

### Stage 0 — BR-1 remains operative unless changed

A binding-resolution notice remains operative when review is requested unless a competent review body expressly orders otherwise. This is the archive's anti-vacatur rule. `[REF-0235]` `[REF-0237]` `[REF-0239]`

### Stage 1 — File RL-1 on a short clock

Any authorized requesting authority or subject-side representative should file RL-1 promptly. Review should not remain indefinitely open as a latent threat.

### Stage 2 — Leave panel screens quickly

A small mixed panel should decide leave on short papers and only exceptionally request more. The archive treats this as a fast filter, not a miniature second merits trial. `[REF-0238]`

### Stage 3 — Interim measures if needed

If the request also seeks IM-2, the review body should be able to preserve, narrow, or otherwise restate the operative protective floor immediately. `[REF-0236]`

### Stage 4 — Expedited review on limited questions

If leave is granted, the higher body should decide only the identified legal or harmonization questions, unless the record already permits a final substituted answer. `[REF-0237]`

### Stage 5 — Issue PN-1 and either affirm, vary, remand, or substitute

The review outcome should not be hidden in private correspondence or reducible to raw result alone. It should travel as PN-1 so future conflicts inherit the clarified rule rather than starting from scratch.

### Stage 6 — Preserve historical trace

The archive expects the history of LA-1, OB-1, JC-1, BR-1, RL-1, IM-2, LP-1, and PN-1 to remain reviewable rather than overwritten by the latest outcome.

## 6. Composition and independence minimums

The archive now fixes six minimum expectations for the supranational review body.

1. **Mixed composition.** No single concerned bloc, steward-aligned authority, or issuer class should dominate the panel.
2. **Conflict exclusion.** Authorities materially involved in the contested BR-1 should not dominate the body reviewing it.
3. **Named power to grant interim protection.** Review without emergency power is too late for the cases this layer exists to govern. `[REF-0236]`
4. **Limited docket.** The body should hear exceptional cases, not every ordinary disagreement. `[REF-0238]`
5. **Reasoned legality output.** Even denials of leave should make enough sense of the request that silent dominance does not become the style of review.
6. **Representative access.** Subject-side representatives should be able to seek leave where the live protection concerns the subject's survival, legal visibility, or effective representation. `[REF-0234]`

## 7. Relationship to the archive's existing surfaces

This document does not replace the archive's lower emergency transition stack.

It sits above `docs/30-transition/lead-authority-fast-conference-and-binding-resolution.md` and answers the narrower question that file intentionally left open.

- `docs/30-transition/lead-authority-fast-conference-and-binding-resolution.md` says who must decide first.
- `docs/30-transition/directed-notice-execution-certificates-and-propagation-duty.md` says live protection must reach decisive actors and produce action records.
- `docs/30-transition/status-publication-challenge-logs-and-conflict-freeze.md` says dispute and freeze states must remain publicly legible.
- `docs/30-transition/packet-authentication-supersession-and-sealed-annex-handling.md` says the packet chain must remain authentic and reviewable while the dispute travels.

This document now adds the missing answer to a narrower question:

**if a binding resolver has already spoken, who reviews that resolver in the exceptional hard case, and does asking for review collapse the subject's protection before the answer arrives?**

This document therefore stops at reviewed legality and operative precedent. The archive's new answer to the narrower question *after* review now lives in `docs/30-transition/implementation-supervision-periodic-attestation-and-explicit-closure.md`: once live protection has been executed or affirmed, it should enter supervised follow-up, periodic attestation, subject-side comment, and explicit closure or conversion rather than drifting into silent expiry. `[REF-0206]` `[REF-0240]` `[REF-0241]` `[REF-0242]` `[REF-0243]` `[REF-0244]`

## 8. What this now settles

1. **The archive now has a canonical supranational-review lane for exceptional hard multi-bloc status conflicts.**
2. **Review is now gated by leave rather than left as either total absence or endless ordinary appeal.**
3. **Filing for review no longer implies silent suspension of the live protective state.**
4. **The review body is now expected to have its own interim-measures power rather than only later doctrinal voice.**
5. **Precedent notice is now part of the transition stack rather than a background aspiration.**
6. **The archive now distinguishes between binding resolution, review leave, and emergency stay at the review level.**
7. **Exact treaty text, appointment method, democratic legitimation, and third-party-intervention breadth remain followthrough work rather than fully closed here.**
