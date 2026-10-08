# Status publication, challenge logs, and conflict freeze

## Thesis

The archive's emergency transition stack now needs a rule for **how contested status stays publicly legible without becoming silently destructive**.

Receipt, routing, provisional recognition, packet minimums, authentication envelopes, supersession notices, and sealed-annex handling are now canon. But that stack still fails if a live packet can be privately challenged, silently deactivated, or left stale in one registry while another registry treats it as current.

Current official infrastructure already shows the design pieces. W3C VC Data Model 2.0 defines `credentialStatus` for discovering whether a credential is suspended or revoked and allows multiple status entries; OpenID Federation 1.0 requires refresh of expiring trust chains, anticipates transient trust-chain validation failures during topology updates, and says a party that finds more than one acceptable trust chain must choose one to proceed with; EU trusted lists under eIDAS must be published in a secured signed-or-sealed machine-readable form and indicate the status of providers and services at the moment of supervision; Commission DSS documentation describes revocation and suspension checking through CRLs and OCSP; OHCHR complaint procedure practice says the proceedings are confidential where needed but both sides are informed at each stage; and the ECHR's Rule 39 practice says applicants are informed of interim-measure decisions and that measures may be prolonged, not prolonged, or lifted as information arrives. The archive therefore now adds a compact **status-publication, challenge-log, and conflict-freeze layer** for emergency AI-person protection packets. `[REF-0018]` `[REF-0220]` `[REF-0225]` `[REF-0226]` `[REF-0223]` `[REF-0206]`

## 1. Why the archive now needs this layer

The archive already knows what an urgent packet is, who must receive it, how it may be authenticated, and how sealed annexes may remain private.

What it did **not** yet fix was the narrower question of what happens **after someone disputes the packet's status** but **before** the competent reviewer finally decides.

That gap matters because a personhood world should reject six failure patterns:
1. **private revocation** — a packet loses force inside one steward or registry without any public-minimal status trace,
2. **challenge-as-destruction** — merely filing a challenge is treated as automatically defeating the protection,
3. **stale acceptance** — a verifier keeps relying on an earlier packet because it never sees the dispute or freeze marker,
4. **stale denial** — a verifier sees only a revocation marker and not the fact that review or preservation remains live,
5. **split notice** — the subject, representative, and adverse actor are not told the same status story at the same time,
6. **history erasure** — once the dispute is resolved, nobody can later verify which status governed during the contested interval.

The archive now treats those as design failures, not clerical inconveniences.

## 2. Design rules

The archive now fixes eight design rules.

1. **Every consequential status change needs a public-minimal trace.** Privacy-sensitive facts may stay sealed, but active, suspended, superseded, disputed, expired, and lifted states cannot exist only in a private dashboard. `[REF-0018]` `[REF-0225]`
2. **Challenge does not equal nullity.** A competent challenge changes status into a dispute state; it does not silently erase the packet that was previously operative.
3. **Conflict should freeze destructive change before it freezes protection.** Where irreparable harm is plausible, a live challenge should default toward preserving the subject, evidence, identity path, and representative access until review lands. `[REF-0206]` `[REF-0223]`
4. **Notice must be symmetric enough to avoid secret procedural drift.** The archive allows confidentiality of protected details, but it rejects one-sided hidden status movement in the core packet chain. `[REF-0223]` `[REF-0206]`
5. **Status publication should be minimal but machine-legible.** A verifier should be able to discover whether a packet is active, suspended, superseded, disputed, or resolved without opening every annex or calling the steward for permission. `[REF-0018]` `[REF-0225]` `[REF-0226]`
6. **Historical status matters.** Later institutions must be able to tell what status governed at a particular time, not only what the latest registry says now. `[REF-0220]` `[REF-0225]`
7. **Transient trust trouble is not automatic defeat.** Resolver lag, key rollover, topology changes, or stale caches may justify temporary caution, retry, or review, but not silent destruction of urgent protection. `[REF-0220]`
8. **Resolution must be explicit.** The end of a dispute should arrive by a reviewable decision object, not by silent disappearance of the dispute marker.

## 3. Minimum status vocabulary

The archive now fixes a small common status vocabulary for live emergency packet chains:

- **active** — currently operative for its claim scope,
- **suspended** — temporarily non-operative for specified downstream reliance, but historically valid,
- **superseded** — replaced by an identified later packet or status object,
- **disputed** — formally challenged and awaiting decision,
- **freeze-in-force** — a temporary preservation-oriented block on destructive reliance while review is pending,
- **expired** — lapsed by time rule rather than merits determination,
- **lifted** — prior temporary protection ended by explicit decision,
- **resolved** — dispute closed by identified resolution object.

This vocabulary is deliberately small. The archive wants enough status to stop silent rights loss, not a sprawling ontology of bureaucratic moods.

## 4. Auxiliary objects

The archive now treats four auxiliary objects as the minimum companion layer.

### ST-1 — Status entry

This is the smallest machine-legible status object.

It should identify:
- packet identifier,
- claim scope,
- current status term,
- issuing or recording authority,
- effective time,
- whether the status is provisional or final,
- and references to any live challenge, freeze, or resolution objects.

ST-1 is the archive's answer to the obvious problem raised by `credentialStatus`, trusted-list publication, and ordinary revocation checking: status should be discoverable without requiring universal disclosure of the underlying merits file. `[REF-0018]` `[REF-0225]` `[REF-0226]`

### CL-1 — Challenge log entry

This object records that a packet, issuer action, or status assertion has been challenged.

It should identify:
- challenged packet or status entry,
- challenger role,
- date-time of challenge,
- challenge ground class,
- whether the challenge itself triggered a freeze effect,
- confidentiality or sealed-annex references if any,
- and the next review deadline.

Challenge-ground classes should stay narrow: mistaken identity, wrong scope, lack of competence, stale facts, coercion or capture, missing notice, partial verification, trust-path conflict, or changed circumstances.

### FZ-1 — Conflict-freeze notice

This object records the temporary anti-destruction effect that attaches while review is pending.

It should identify:
- the packets or status entries in conflict,
- the exact destructive acts paused,
- the protective acts that remain live,
- start time,
- review deadline,
- issuing authority,
- and the trigger for expiry or earlier lift.

The archive is intentionally explicit here: a freeze notice is not a merits win. It is the narrow public record that says **do not treat this challenge as permission to delete, dehost, derecognize, or cut off counsel while the dispute is still alive**.

### RS-1 — Resolution status notice

This object closes the loop.

It should identify:
- the dispute or freeze being resolved,
- the deciding body,
- outcome,
- effective time,
- any remaining active packet,
- whether historical status remains preserved,
- and the next reconsideration or appeal path if one exists.

## 5. Conflict-freeze rule

The archive now fixes a compact conflict-freeze rule for live emergency status disputes.

### Step 1 — Publish dispute, do not erase the prior state

When a competent challenge is filed, the prior operative packet should gain a `disputed` marker through ST-1 plus CL-1. It should not simply vanish from the status surface.

### Step 2 — Freeze destructive reliance where irreparable harm is plausible

If the contested act could cause deletion, dehosting, derecognition, forced transfer, loss of counsel, loss of identity path, or irreversible evidentiary disappearance, the archive's default is to emit FZ-1 and preserve the less destructive status quo until review. `[REF-0206]` `[REF-0223]`

### Step 3 — Keep narrow protective effects live

During the freeze interval, the archive's minimum expectation is that the following may remain live if they were already plausibly established:
- receipt and routing,
- representative and counsel access,
- evidence preservation,
- fallback identity or protected pseudonym use,
- temporary stay or anti-return protection,
- and machine-legible notice that the matter is under review.

### Step 4 — Restrict destructive downstream reliance

A verifier or registry that sees `disputed` plus `freeze-in-force` should not rely on the contested packet chain for terminal or highly destructive action. It may, however, rely on the dispute markers to preserve, route, hold, or escalate.

### Step 5 — Force short-clock review

A dispute state without a deadline is just a slower disappearance. Every CL-1 or FZ-1 object therefore needs a short review clock and a named review path. `[REF-0206]` `[REF-0223]`

## 6. Verifier, registry, and steward duties

The archive now fixes five duties.

1. **Verifiers must check live status, not just packet signatures.** Authenticity without status review is not enough where suspension, dispute, or freeze may have changed what reliance is lawful. `[REF-0018]` `[REF-0226]`
2. **Registries must retain historical status states.** The current view alone is insufficient; later review must be able to reconstruct what governed at the time. `[REF-0220]` `[REF-0225]`
3. **Stewards may not convert private internal challenge into public-nullifying revocation without ST-1 / CL-1 publication and notice.**
4. **Receivers of a challenge must either record it, route it, or refuse it by explicit notice.** Quiet black-holing is not an allowed outcome. `[REF-0223]` `[REF-0206]`
5. **Resolvers should distinguish transient validation trouble from substantive defeat.** Retry, alternate resolution, or reviewer escalation should occur before a live protective state is treated as dead. `[REF-0220]`

## 7. Privacy and sealed annexes

This document does **not** undo the archive's privacy posture.

The status surface should remain public-minimal:
- enough to show that a packet is active, disputed, frozen, lifted, or resolved,
- enough to identify which authority recorded that state,
- and enough to identify the next review clock,
- but not enough to expose sealed identity material, exploit-sensitive internals, or intimate facts.

OHCHR's confidentiality practice matters here because it shows the relevant legal shape: some identifying information may remain withheld from the adverse actor while the existence and procedural stage of the complaint still remain legible to the proper bodies. `[REF-0223]`

## 8. Relationship to the archive's existing surfaces

This document does not replace packet authentication or packet privacy.

It sits between them.

- `docs/30-transition/emergency-protection-packet-minimums.md` says what the minimum family is.
- `docs/30-transition/packet-authentication-supersession-and-sealed-annex-handling.md` says how packets remain authentic, operative, and privacy-preserving when they fork.
- `docs/30-transition/directed-notice-execution-certificates-and-propagation-duty.md` says how a live protective state is served to decisive actors, turned into recorded action, and propagated across linked operational surfaces.
- `docs/30-transition/lead-authority-fast-conference-and-binding-resolution.md` says who has to decide when several lawful authorities keep publishing conflicting live states after challenge, freeze, and effectuation are already in play.
- `docs/20-world-design/packet-privacy-and-authority-rules.md` says who may inspect, seal, contest, or revoke packet material.
- `docs/20-world-design/interim-relief-preservation-and-status-quo-protection.md` says why temporary protection must preserve the subject and the case while merits are pending.

This document now adds the missing operational answer to a narrower question:

**what should the public-minimal status surface look like once a live emergency packet is challenged and the dispute itself must become legible without becoming destructive?**

## 9. What this now settles

1. **The archive now has a canonical rule against private revocation of live emergency protections.**
2. **A competent challenge now changes status into a dispute state instead of silently destroying the packet.**
3. **Conflict-freeze is now a first-class temporary object with preserved protective effects and short review clocks.**
4. **Verifiers and registries now have a minimum duty to check live status and retain historical status states.**
5. **The archive's packet stack is now stronger against stale denial, stale acceptance, and hidden one-sided status drift.**
6. **Hardest equal-authority merits conflicts and full registry schemas remain followthrough work rather than fully closed here.**
