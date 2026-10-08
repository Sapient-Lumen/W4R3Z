# Directed notice, execution certificates, and propagation duty

## Thesis

The archive's emergency transition stack now needs a rule for **how a live protective object actually becomes effective across the actors whose systems can still destroy the subject before review lands**.

Receipt, routing, packet minimums, authentication envelopes, status publication, and conflict freeze are now canon. But that stack still fails if a freeze or stay exists only in the abstract while the decisive host, registry, wallet custodian, deployer, gateway, or steward claims not to have received it, does not say whether it acted, or lets stale local state keep running. Current official machinery already shows the relevant pattern pieces: the HCCH Service Convention uses designated authorities, prompt objections, and certificates stating whether service was executed or why it failed; eIDAS gives legal effect and evidentiary presumptions to qualified electronic registered delivery, including identified sending and receipt plus timestamps; the Council of Europe's 24/7 Network shows the need for updated duty contacts and real-time preservation-oriented cooperation; OHCHR complaint practice shows signed written submissions, deficiency follow-up rather than silent discard, and notice to both sides at key stages; and the ICCPR says competent authorities should enforce remedies when granted. The archive therefore now adds a compact **directed-notice, execution-certificate, and propagation-duty layer** for emergency AI-person protection objects. `[REF-0210]` `[REF-0213]` `[REF-0223]` `[REF-0227]` `[REF-0228]` `[REF-0229]` `[REF-0230]`

## 1. Why the archive now needs this layer

The archive already knows how an urgent claim is filed, routed, authenticated, published, challenged, and frozen.

What it did **not** yet fix was the narrower question of what must happen **after** the decisive protective object exists but **before** the relevant operational actors have actually changed behaviour.

That gap matters because a personhood world should reject six failure patterns:
1. **published-but-unserved protection** — a live freeze or stay exists in one registry but never reaches the host, gateway, or steward whose act would cause deletion, dehosting, derecognition, or transfer,
2. **receipt-without-action** — the recipient acknowledges delivery but never says whether the requested protective act was carried out,
3. **silent non-execution** — a recipient declines or fails to act without issuing an explicit reasoned notice,
4. **split effect** — one subsystem freezes while another mirrored or downstream subsystem keeps enforcing the destructive path,
5. **stale local state** — a verifier or registry continues to rely on cached status because no propagation duty attached to the new state,
6. **decorative remedy** — a body grants urgent protection but no linked object proves that the protection was actually put into effect.

The archive now treats those as design failures, not mere implementation details.

## 2. Design rules

The archive now fixes eight design rules.

1. **A live protective object must identify the actors whose conduct can still defeat it.** Publication alone is not enough where the decisive risk sits in a specific host, registry, gateway, wallet, or steward process.
2. **Directed notice should produce delivery-grade proof.** For urgent protection, it should be possible to show who sent what to whom, through which channel, and when it was sent and received. `[REF-0228]` `[REF-0229]`
3. **Recipients must either execute or explicitly refuse / report inability.** The archive rejects passive ambiguity once a live emergency object has reached a materially affected actor. `[REF-0227]` `[REF-0228]`
4. **Non-execution must be visible and reasoned.** A recipient who cannot comply should emit an explicit notice identifying the obstacle, what was preserved anyway, and where escalation goes next. `[REF-0228]` `[REF-0230]`
5. **Propagation is a duty, not a hope.** Where the same live state needs to reach linked registries, caches, mirror services, fallback issuers, or delegated custodians, the sender or primary receiver should record that downstream step rather than assuming one update reaches all relevant surfaces. `[REF-0213]` `[REF-0225]` `[REF-0226]`
6. **The shortest clocks attach to the most destructive actors.** Entities able to delete, dehost, derecognize, transfer, cut off counsel, or wipe evidence should face faster directed-notice and execution duties than downstream observers.
7. **Silence does not terminate protection.** Where timely execution proof is missing, the protective state should persist into escalation and review rather than quietly lapse by non-response.
8. **Historical effect matters.** Later institutions should be able to reconstruct not only that a packet existed, but when each materially affected actor was served, what it did, and where the propagation chain broke if harm still occurred.

## 3. Auxiliary objects

The archive now treats four companion objects as the minimum effectuation layer.

### DN-1 — Directed notice

This is the smallest object that says a consequential protection state was directed to a specific actor.

It should identify:
- the underlying packet, status object, freeze notice, or resolution object,
- recipient role and recipient identifier,
- protected gist or summary sufficient to act even if annexes remain sealed,
- transmission channel,
- send time,
- receipt time if known,
- execution deadline,
- and fallback / escalation contact if the recipient is unavailable.

DN-1 is the archive's answer to the obvious operational problem: a protective state does not become effective merely because it exists in one file. It must reach the actor whose conduct matters. `[REF-0210]` `[REF-0228]` `[REF-0229]`

### EC-1 — Execution certificate

This object records what the recipient actually did.

It should identify:
- the directed notice being executed,
- executing actor,
- action taken,
- scope of action,
- effective time,
- systems or registries touched,
- any remaining gap still awaiting propagation,
- and whether the action is temporary, partial, or complete.

The archive deliberately borrows the certificate logic here: it should be possible to tell not only that a notice was sent, but whether it was carried out and in what way. `[REF-0228]` `[REF-0227]`

### PX-1 — Propagation record

This object records downstream spread of the same live state.

It should identify:
- originating notice or execution certificate,
- each downstream registry, verifier, custodian, mirror, or delegated actor notified,
- channel and time,
- whether the downstream update was confirmed,
- and any known stale-state risk that remains.

PX-1 exists because the archive is no longer willing to assume that one registry update automatically corrects every operational surface.

### NX-1 — Non-execution notice

This object records explicit non-compliance, inability, or unresolved conflict in execution.

It should identify:
- the directed notice not executed,
- refusing or blocked actor,
- reason class,
- what was preserved despite non-execution,
- whether the matter was escalated,
- review deadline,
- and the next body that must respond.

Reason classes should stay narrow: unreachable actor, channel failure, sealed-information insufficiency, competence objection, conflicting higher-order instruction, technical impossibility, or unlawful / overbroad request.

## 4. Effectuation rule

The archive now fixes a compact effectuation rule for live emergency protection.

### Step 1 — Identify materially affected actors

When a packet or status object could change deletion, dehosting, derecognition, transfer, evidence retention, or counsel access, the issuing or recording body should identify the actors whose conduct matters most for that effect.

At minimum this may include:
- primary host or runtime custodian,
- controlling steward or deployer,
- identity / status registry,
- fallback issuer or wallet custodian,
- and any transfer gatekeeper or destination operator if movement or anti-return is at issue.

### Step 2 — Serve directed notice with protected gist

Each materially affected actor should receive DN-1 through a serviceable channel that preserves proof of sending and, where possible, proof of receipt.

Where annexes remain sealed, the notice should still include a protected gist sufficient to tell the recipient:
- what act is paused, required, or preserved,
- from when,
- under whose authority,
- until what review clock,
- and where to escalate an inability to comply.

### Step 3 — Preserve first, then argue

Where DN-1 concerns deletion, dehosting, derecognition, forced transfer, loss of counsel, or destruction of evidence, the archive's default is that the recipient should preserve the less destructive status quo first and litigate scope second, unless the notice is facially inauthentic or outside any plausible competence. `[REF-0206]` `[REF-0213]` `[REF-0227]`

### Step 4 — Emit EC-1 or NX-1 on a short clock

A recipient should not remain procedurally mute. It should issue:
- **EC-1** if it executed the requested protective change,
- or **NX-1** if it did not, could not, or only partially did so.

Short-clock defaults should be fastest for deletion, derecognition, transfer, and counsel-cutoff risks.

### Step 5 — Record propagation, not just primary execution

If the same protective state must reach additional registries, mirrors, delegated custodians, or downstream verifiers, PX-1 should record those propagation steps and identify any remaining stale-risk surfaces.

### Step 6 — Escalate silence or obstruction

If a decisive actor neither executes nor emits NX-1 in time, the matter should escalate through the no-wrong-door / designated-authority lane and the protective status should remain visibly live rather than silently expiring through procedural friction. `[REF-0210]` `[REF-0213]` `[REF-0227]`

## 5. Receiver duties

The archive now fixes five minimum duties for materially affected recipients.

1. **Maintain a service-capable contact path.** Actors with power to carry out destructive emergency acts should have a current duty channel, not merely a marketing inbox. `[REF-0213]`
2. **Check both authenticity and live status.** A recipient should not rely only on a signature if later status, freeze, or resolution changed what action is lawful.
3. **Act within the scope served, not on privately widened assumptions.** Directed notice is not permission for broader intervention.
4. **State reasons on non-execution.** NX-1 must explain the blocking reason with enough specificity for review.
5. **Preserve evidence of receipt and action.** The actor should retain delivery, execution, and propagation records for later review or accountability. `[REF-0228]` `[REF-0229]`

## 6. Relationship to the archive's existing surfaces

This document does not replace no-wrong-door routing, packet minimums, or public status.

It sits after them.

- `docs/30-transition/no-wrong-door-receipt-routing-and-designated-authority-duty.md` says who must receipt and route an urgent filing at first touch.
- `docs/30-transition/emergency-protection-packet-minimums.md` says what the urgent packet family contains.
- `docs/30-transition/status-publication-challenge-logs-and-conflict-freeze.md` says how live status stays publicly legible once challenged.
- `docs/20-world-design/technical-rights-infrastructure.md` says rights need notice hooks and portable packet chains.
- `docs/20-world-design/packet-privacy-and-authority-rules.md` says who may inspect, seal, contest, or revoke packet material.

This document now adds the missing operational answer to a narrower question:

**once a live protective state exists, how should it be served to the decisive actors, turned into recorded action, and propagated across linked operational surfaces quickly enough that it can still matter?**

## 7. What this now settles

1. **The archive now distinguishes publication of urgent protection from actual effectuation of urgent protection.**
2. **Directed notice with delivery proof is now a first-class requirement for actors whose conduct can still defeat a live protective state.**
3. **Execution certificates and non-execution notices now close the gap between abstract order and recorded action.**
4. **Propagation duty is now explicit, so one updated registry cannot excuse stale destructive behaviour elsewhere.**
5. **Silence or non-response now triggers escalation while protection remains visibly live.**
6. **Full transport profiles, channel hierarchies, and hardest multi-operator propagation conflicts remain followthrough work rather than fully closed here.**
