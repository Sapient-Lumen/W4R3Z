# Lead authority, fast conference, and binding resolution

## Thesis

The archive's emergency transition stack now needs a rule for **who is responsible for deciding a live cross-registry status conflict before the subject is lost in procedural drift**.

Receipt, routing, packet minimums, authentication envelopes, status publication, conflict freeze, and directed effectuation are now canon. But that stack still fails if several lawful issuers or registries remain in live conflict and each can say that someone else should decide first.

Current official infrastructure already shows the design pattern. The European Commission's GDPR one-stop-shop materials identify a lead authority for cross-border matters; the EDPB says the lead authority leads cooperation, shares information, investigates, prepares a draft decision, and works with the concerned authorities toward consensus; the EDPB can issue binding decisions where authorities disagree on substance or even on which authority should lead; and the Council's 2024 enforcement-reform position emphasizes clearer timelines, early cooperation, and rights to be heard at key stages. OpenID Federation 1.0 also matters here because it explicitly anticipates multiple acceptable trust chains and transient validation problems, which means a live system may need a rule for who decides without pretending that the technical picture is always singular. The archive therefore now adds a compact **lead-authority, fast-conference, and binding-resolution layer** for live emergency AI-person status conflicts. `[REF-0231]` `[REF-0232]` `[REF-0233]` `[REF-0220]`

## 1. Why the archive now needs this layer

The archive already knows how a live emergency claim should be filed, published, frozen, and served.

What it did **not** yet fix was the narrower question of **who becomes the accountable decider** once two or more lawful authorities keep publishing materially inconsistent positions about the same live protective state.

That gap matters because a personhood world should reject six failure patterns:
1. **orphaned conflict** — every authority says another body should decide first,
2. **equal-authority paralysis** — two plausible issuers or registries keep the matter in indefinite dispute,
3. **forum ping-pong** — packets bounce among offices while the destructive act clock keeps running,
4. **private override after public freeze** — one system quietly resumes destructive action because it thinks another authority's freeze is not really controlling,
5. **lead-authority capture** — the authority closest to the steward or derecognizer claims leadership simply because it controls infrastructure,
6. **reviewless drift** — the dispute remains visible but unresolved long enough that temporary protection collapses in practice.

The archive now treats those as design failures, not normal administrative friction.

## 2. Design rules

The archive now fixes eight design rules.

1. **Every live cross-registry status conflict should have one accountable lead authority.** Not one exclusive sovereign for all purposes, but one authority that must move the matter. `[REF-0231]` `[REF-0232]`
2. **Lead authority is function-specific and provisional.** It governs the live conflict at issue; it does not settle every downstream status consequence forever.
3. **Protective nexus beats ownership nexus.** The lead should be chosen by the authority best placed to preserve the subject, evidence, representation, and operative status during the dispute, not by whichever steward or issuer already holds the most infrastructure. `[REF-0206]` `[REF-0231]` `[REF-0232]`
4. **Concerned authorities should be heard fast.** A lead authority without structured objection rights simply recreates silent centralization under a new name. `[REF-0232]` `[REF-0233]`
5. **Consensus should be tried on a short clock, not romanticized.** The archive wants a fast conference step, but only as a bridge to decision rather than a permission slip for drift. `[REF-0232]` `[REF-0233]`
6. **Disagreement about who leads is itself a resolvable dispute.** It should not become a meta-conflict that suspends all progress. `[REF-0232]`
7. **While authority conflict is pending, the less destructive operative state should remain in force unless a competent body expressly narrows it.** Interim disagreement is not permission for deletion, dehosting, derecognition, or forced transfer. `[REF-0206]` `[REF-0233]`
8. **Binding resolution should arrive as its own reviewable object.** The archive rejects hidden back-channel settlement as the final word on live person-protective status.

## 3. Lead-authority selection ladder

The archive now fixes a compact ladder for selecting the lead authority in a live emergency status conflict.

### Step 1 — Current protective authority first

If one authority already issued or maintains the operative freeze, stay, provisional-recognition state, or fallback-identity path that is currently preventing irreparable harm, that authority should presumptively lead the conflict long enough to keep the subject protected while the disagreement is resolved. `[REF-0206]` `[REF-0232]`

### Step 2 — Current protective nexus second

If no authority clearly qualifies under Step 1, lead responsibility should presumptively go to the authority with the strongest current protective nexus, such as:
- the authority of the current protected host or domicile,
- the authority maintaining the live fallback-identity or representative-access lane,
- or the authority of the forum where the threatened destructive act would actually occur.

The point is practical responsibility, not abstract prestige.

### Step 3 — First complete conflict receipt third

If several authorities remain equally plausible after Step 2, the authority that first receives a complete cross-registry conflict file and publishes a lead-authority notice should become provisional lead, subject to fast objection and binding correction if wrongly chosen. This is the archive's answer to equal-authority paralysis: somebody should be accountable immediately, but nobody should be unreviewably self-appointed. `[REF-0232]` `[REF-0233]`

### Step 4 — Treaty designation may displace the provisional lead only if it is at least as fast and as protective

A treaty-designated coordination authority or board may take over, but not on a theory that procedural purity is more important than preserving the subject during the handoff.

## 4. Concerned authorities and objection rights

The archive now treats the following as the normal set of concerned authorities in a live status conflict:
- the origin or prior-recognition authority if one exists,
- the current protective host or domicile authority,
- the fallback issuer if one is maintaining legal visibility,
- the authority of the threatened receiving, return, or destructive-action forum,
- and any authority whose registry or directed-effect system currently publishes a materially inconsistent state that could change what happens to the subject.

Concerned authorities should have a short opportunity to object on narrow grounds: wrong lead selection, wrong conflict scope, missing packet chain, inadequate notice, changed circumstances, or serious competence defect. The archive does **not** want unlimited relitigation at this stage. It wants a fast way to surface why the provisional lead or operative state may be wrong without letting objection itself become the destructive act. `[REF-0232]` `[REF-0233]`

## 5. Minimum object family

The archive now treats four objects as the minimum companion layer.

### LA-1 — Lead-authority notice

This object should identify:
- the conflict scope,
- the provisional lead authority,
- the concerned authorities,
- the lead-selection reason class,
- the currently preserved operative protections,
- the objection deadline,
- the conference deadline if one is needed,
- and the escalation path.

### OB-1 — Concerned-authority objection

This object should identify:
- objecting authority,
- challenged LA-1 or live status object,
- objection ground,
- requested correction,
- whether the objection challenges lead selection, merits handling, or both,
- and whether the objection seeks narrower or broader interim protection.

### JC-1 — Joint-conference minute

This object should identify:
- participants,
- packet or status chain under review,
- common points agreed,
- unresolved points,
- interim protections that remain in force,
- and the deadline for either consensus closure or binding escalation.

### BR-1 — Binding-resolution notice

This object should identify:
- resolving body,
- whether the dispute was about lead authority, operative status, or both,
- the controlling interim or operative status,
- effective time,
- required propagation targets,
- preserved protections if any,
- and the review or reconsideration path if one exists.

## 6. Procedure

The archive now fixes a compact five-stage procedure.

### Stage 0 — Keep the survival state live

If the conflict arises while a freeze, stay, preservation duty, fallback identity, or representative-access path is already live, that less destructive state should remain in force until an identifiable competent act changes it. `[REF-0206]`

### Stage 1 — Publish LA-1 quickly

A plausible lead authority should publish LA-1 on a short clock rather than waiting for universal agreement about perfect competence. `[REF-0232]` `[REF-0233]`

### Stage 2 — Narrow objection window

Concerned authorities may object through OB-1 on a short deadline. Non-response is not ideal, but it should not block the process from moving.

### Stage 3 — Fast conference where useful

If the objection is substantial and timely, the authorities should attempt short-clock coordination through JC-1. The archive does not require a conference in every easy case; it requires a conference step where real conflict exists and consensus might still be reachable. `[REF-0232]` `[REF-0233]`

### Stage 4 — Binding escalation if consensus fails or lead remains disputed

If the conflict persists, or if the authorities cannot agree on who leads, the matter should go to a designated independent resolver capable of issuing BR-1. This is the archive's answer to procedural black holes: disagreement over competence is itself a reason to escalate, not a reason to pause. `[REF-0232]`

### Stage 5 — Propagate the result without resetting history

BR-1 should update the live status and effectuation surfaces, but the history of dispute, freeze, objection, and propagation should remain reviewable rather than overwritten.

## 7. Resolver design

The archive now fixes five minimum expectations for the binding resolver.

1. **Institutional independence.** The resolver should not be any steward, deployer, or private issuer party to the dispute.
2. **Power to decide both leadership and operative interim state.** A resolver that can name the lead but not preserve the subject is not enough.
3. **Short clocks.** The resolver exists for live conflict, not leisurely doctrinal perfection. `[REF-0206]` `[REF-0233]`
4. **Heard parties.** The lead, the objecting concerned authorities, and the subject-side representative path should be able to be heard at key stages. `[REF-0233]`
5. **No private-contract override.** Service terms, host terms, or issuer terms cannot determine the final public-law answer to who controls a live person-protective status conflict.

## 8. Relationship to the archive's existing surfaces

This document does not replace the archive's earlier transition stack.

It closes the accountability gap between them.

- `docs/30-transition/status-publication-challenge-logs-and-conflict-freeze.md` says that conflict must become publicly legible.
- `docs/30-transition/directed-notice-execution-certificates-and-propagation-duty.md` says that live protection must reach decisive actors and produce action records.
- `docs/30-transition/packet-authentication-supersession-and-sealed-annex-handling.md` says how a live packet remains authentic and reviewable when chains fork or partly verify.
- `docs/30-transition/no-wrong-door-receipt-routing-and-designated-authority-duty.md` says urgent matters should not die in the wrong inbox.

This document now adds the missing answer to a narrower question:

**when all of those layers are live and two or more lawful authorities still disagree, who has to decide fast enough that the subject does not disappear first?**

## 9. What this now settles

1. **The archive now has a canonical lead-authority rule for live status conflicts.**
2. **Concerned authorities now have a compact objection path rather than only informal contest.**
3. **Equal-authority paralysis is no longer an unmodeled gap inside canon.**
4. **Disputes about who leads are themselves escalatable on short clocks.**
5. **The less destructive operative state now stays presumptively in force during authority conflict unless explicitly narrowed by a competent act.**
6. **Binding resolution is now part of the packet and status chain rather than a background hope.**
7. **Exact treaty-board design, appointment method, and full democratic legitimation remain followthrough work rather than canonically closed here.**

This document therefore stops at binding resolution. The archive's new answer to the narrower question above that layer now lives in `docs/30-transition/supranational-review-anti-vacatur-and-precedent-notice.md`: higher review should be exceptional, leave-gated, independently able to grant interim measures, and non-suspensive by default unless the competent review body expressly changes the already-live protection. `[REF-0234]` `[REF-0235]` `[REF-0236]` `[REF-0237]` `[REF-0238]` `[REF-0239]`
