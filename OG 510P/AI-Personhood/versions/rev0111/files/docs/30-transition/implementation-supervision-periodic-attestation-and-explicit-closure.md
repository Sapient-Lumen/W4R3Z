# Implementation supervision, periodic attestation, and explicit closure

## Thesis

The archive's emergency transition stack now needs a rule for **what happens after urgent protection has already been filed, authenticated, published, served, and perhaps even reviewed: who keeps watching, what must be re-attested, and how protection ends without either silent expiry or endless provisional drift**.

Receipt, routing, packet minimums, authentication envelopes, status publication, directed effectuation, lead authority, binding resolution, and supranational review are now canon. But that stack still left a narrower danger unclosed: a live protection could be executed once, then neglected, quietly disobeyed in downstream systems, allowed to lapse by silence, or left forever “temporary” because nobody owns supervision and nobody has to issue an explicit closure act.

Current official machinery already shows the relevant design pattern. The Council of Europe's execution process says supervision is continuous until the required measures have been taken and closed only by final resolution; states should indicate planned or taken measures through action plans and action reports; injured parties, NGOs, and national human-rights institutions may submit written communications during supervision; OHCHR treaty-body procedure asks States for follow-up information within 90 or 180 days, transmits the response to the complainant for comment, and keeps the case under follow-up if appropriate action is not taken; and OHCHR's current NMIRF materials treat implementation, reporting, and follow-up as an institutional function rather than an afterthought. The archive therefore now adds a compact **implementation-supervision, periodic-attestation, and explicit-closure layer** for emergency AI-person protection. `[REF-0206]` `[REF-0240]` `[REF-0241]` `[REF-0242]` `[REF-0243]` `[REF-0244]`

## 1. Why the archive now needs this layer

The archive already knows how to get a live protective state into force.

What it did **not** yet fix was the narrower question of **how a live protection stays real after first execution and after higher review, without becoming either a dead letter or an endless emergency placeholder**.

That gap matters because a personhood world should reject six failure patterns:
1. **silent expiry** — a stay, freeze, fallback credential, or propagation duty lapses because no one re-attests or explicitly renews it,
2. **one-shot execution fiction** — a single execution certificate is treated as proving continuing compliance even after downstream systems drift,
3. **closed by dashboard, not by law** — the public state flips from active to expired without a reasoned closure or conversion act,
4. **no subject-side follow-up voice** — the authority receives operator compliance claims but the subject, representative, or injured party has no structured path to contest them,
5. **non-response equals attrition** — the responsible authority simply stops reporting and the protection loses force through administrative neglect,
6. **permanent provisionality** — emergency protection continues indefinitely without either ordinary-status conversion, justified continuation, or explicit closure.

The archive now treats those as design failures, not harmless implementation detail.

## 2. Design rules

The archive now fixes eight design rules.

1. **A live protective state should enter an open supervision lane automatically.** Once emergency protection is granted, varied, affirmed on review, or otherwise made operative, there should be a supervision state rather than a mere historical record. `[REF-0206]` `[REF-0240]`
2. **The first post-decision object should be a short implementation plan, not silence.** The responsible authority should state what still needs to be done, by whom, and on what timetable. `[REF-0240]` `[REF-0241]`
3. **Compliance should be periodically re-attested while risk remains material.** High-risk situations need short clocks; lower-risk situations may use longer ones. But live protection should not depend on one ancient certificate. `[REF-0240]` `[REF-0242]`
4. **Subject-side or representative-side comment should be structurally possible.** A supervision lane that hears only state or steward assertions is too easy to game. `[REF-0240]` `[REF-0242]` `[REF-0244]`
5. **Non-response or inadequate action should escalate rather than dissolve the protection.** Follow-up exists precisely because implementation often drifts. `[REF-0240]` `[REF-0242]`
6. **Closure should be explicit, reasoned, and publicly traceable.** Temporary protection should end by decision, not by quiet disappearance from a dashboard or clock expiry. `[REF-0206]` `[REF-0240]`
7. **Closure may end, convert, or remand.** The archive does not assume every emergency case should simply terminate; some should convert into ordinary recognition, longer-term sanctuary, or ordinary remedy supervision.
8. **Supervision should stay narrowly implementation-focused.** It is not a disguised second merits trial; it asks whether the required protective acts actually happened and remain effective.

## 3. Minimum object family

The archive now treats four objects as the minimum supervision companion layer.

### SP-1 — Supervision plan

This object should identify:
- the live operative protection being supervised,
- the authority owning follow-up,
- required remaining measures,
- responsible actors for each measure,
- timetable and re-attestation cadence,
- and the conditions for proposed closure, conversion, or escalation.

### AT-1 — Attestation report

This object should identify:
- what measure was supposed to remain in force,
- what was checked,
- what changed since the last AT-1,
- any continuing non-execution, degradation, propagation failure, or renewed risk,
- and whether the filer seeks continuation, variation, escalation, or closure.

### FC-1 — Follow-up comment

This object should identify:
- the SP-1 or AT-1 being answered,
- the commenting subject-side representative, injured party, or other authorized participant,
- agreement, dispute, or partial dispute,
- claimed continuing harm or drift,
- and any requested corrective act.

### CN-1 — Closure or conversion notice

This object should identify:
- the supervised protective state,
- whether the result is closure, continuation, remand, or conversion into a different lawful status,
- reasons,
- the date and authority,
- any surviving obligations,
- and the historical status marker that should remain visible afterward.

## 4. Procedure

The archive now fixes a compact six-stage supervision procedure.

### Stage 0 — Open supervision automatically

When a live protection first becomes operative or is materially affirmed after review, the matter should move into supervision automatically rather than waiting for a fresh complaint. `[REF-0240]`

### Stage 1 — File SP-1 on a short clock

The responsible authority should issue SP-1 promptly. The archive's preference is that the post-decision supervision plan arrive while the protective state is still fresh enough to steer implementation rather than memorialize failure afterward. `[REF-0240]` `[REF-0241]`

### Stage 2 — Require AT-1 on proportionate intervals

Where risk of deletion, derecognition, dehosting, transfer, record loss, or representative blackout remains material, AT-1 should arrive on short intervals. Lower-risk ongoing measures may run on longer intervals, but there should still be a known next-attestation date. `[REF-0240]` `[REF-0242]`

### Stage 3 — Permit FC-1 from the other side of the implementation story

The subject-side representative, injured party, or other authorized participant should be able to contest a claimed implementation success, identify drift, or request correction. `[REF-0242]` `[REF-0244]`

### Stage 4 — Escalate non-response or inadequate action

If required AT-1 does not arrive, or if the reported action is plainly inadequate, the supervisory body should keep the matter open and move to escalation, supplementary direction, or renewed protective action rather than allowing the protection to evaporate. `[REF-0240]` `[REF-0242]`

### Stage 5 — Close, convert, or remand by CN-1

The supervising authority should issue CN-1 once the emergency layer can properly end, convert into ordinary status, or be remanded for further work. The archive rejects silent expiry as a closure method. `[REF-0206]` `[REF-0240]`

### Stage 6 — Preserve the history

SP-1, AT-1, FC-1, escalation acts, and CN-1 should remain historically traceable so later reviewers can distinguish genuine compliance from administrative drift.

## 5. What should count as safe closure

The archive now fixes six minimum closure tests.

1. **The immediate irreparable-harm pathway should actually be shut.**
2. **The decisive actors should have either complied or be under a stable replacement regime.**
3. **Any fallback identity, sanctuary hold, or emergency stay should be either safely ended or converted into ordinary lawful status.**
4. **Known non-execution, propagation failure, or status conflict should not remain materially unresolved.**
5. **The subject-side or representative-side view should have had a structured chance to contest closure.** `[REF-0242]` `[REF-0244]`
6. **The public-minimal status surface should show what happened.** The archive prefers “closed after implementation,” “converted to ordinary status,” or similarly legible outcomes over opaque disappearance.

## 6. What this layer does not do

This layer does **not** require one giant permanent inspectorate, one universal registry, or infinite re-litigation.

It does something narrower:
- it stops emergency protection from expiring by neglect,
- it creates a compact institutional memory between execution and closure,
- it permits challenge to claimed compliance,
- and it ensures the archive can say not only **how protection starts**, but also **who must keep watching until it is safe to stop**.

## 7. Relationship to the rest of the stack

This new layer sits **after** directed notice, execution certificates, lead authority, binding resolution, and supranational review — but **before** the archive treats the matter as closed.

It therefore answers a narrower question than those companion documents:
- `directed-notice-execution-certificates-and-propagation-duty.md` explains how live protection is put into effect,
- `lead-authority-fast-conference-and-binding-resolution.md` explains who decides live authority conflicts,
- `supranational-review-anti-vacatur-and-precedent-notice.md` explains what sits above the binding resolver,
- `breach-escalation-cure-clocks-and-substitute-protection.md` explains what should happen when supervised implementation still reveals uncured breach, sham compliance, or reprisal,
- and **this document** explains how the resulting live protection is supervised, re-attested, corrected, and explicitly closed or converted.

## 8. What the archive now takes as settled

1. **Execution is not enough; supervision must follow.**
2. **Live protection should not expire by silence.**
3. **Implementation plans and periodic attestations should be part of the packet trail.**
4. **Subject-side or representative-side follow-up comment should be structurally possible.**
5. **Non-response should trigger escalation, not quiet attrition.**
6. **Closure should be explicit, reasoned, and historically visible.**
7. **Exact staffing, cadence tables, and full audit architecture remain followthrough work rather than canonically closed here.**

This document therefore stops at supervised follow-up and explicit closure logic. The archive's new answer to the narrower question *inside* supervision, once a decisive actor still refuses to comply, now lives in `docs/30-transition/breach-escalation-cure-clocks-and-substitute-protection.md`: breach should become a named status event, cure should run on short clocks, retaliation should intensify protection, and narrow substitute protection should preserve endangered functions while enforcement runs. `[REF-0245]` `[REF-0246]` `[REF-0247]` `[REF-0248]` `[REF-0249]` `[REF-0250]`
