# Packet authentication, supersession, and sealed-annex handling

## Thesis

The archive's emergency packet family now needs a rule for **which packet counts**.

Receipt, forwarding, provisional recognition, preservation, fallback identity, and review are now canonically packetized. But that stack still fails if institutions cannot answer three narrower questions fast enough:
- is this packet chain authentic enough to act on,
- which packet is the currently operative one for the issue in dispute,
- and what happens when the decisive detail sits in a sealed annex that not every actor may open.

Current official infrastructure already provides the design pieces. W3C's verifiable-credential and data-integrity standards give tamper-evident credentials, proof sets and chains, and selective disclosure; OpenID Federation now provides explicit trust-chain resolution, policy application, multiple-valid-chain handling, transient-error logic, and historical-key reasoning; OpenID4VP requires a wallet to refuse a request if trust cannot be established; eIDAS trust-services guidance distinguishes seals, timestamps, preservation, and registered-delivery proof of sending and receipt; OHCHR complaint procedure practice allows confidentiality requests so identity need not be transmitted to the adverse State; and HCCH's e-APP supports electronic issuance and verification through e-register patterns. The archive therefore now adds a compact **packet-authentication, supersession, and sealed-annex layer** for live emergency AI-person claims. `[REF-0018]` `[REF-0219]` `[REF-0220]` `[REF-0221]` `[REF-0222]` `[REF-0223]` `[REF-0224]`

## 1. Why the archive now needs this layer

The archive already knows what an urgent packet should contain and how it should travel.

What it did **not** yet fix was the rule for choosing the operative packet when:
- two facially valid packets speak to the same issue,
- a later packet corrects only one field and not the whole claim,
- a verifier can authenticate the envelope and some claims but not every annex,
- key rollover or registry migration makes an older packet temporarily harder to verify,
- or sealed annexes must support urgent action without being exposed to every intermediary.

That gap matters because a personhood world should reject five failure patterns:
1. **timestamp fetish** — the newest packet wins even if the issuer lacked authority for that scope,
2. **all-or-nothing verification** — one unverifiable annex voids the whole urgent claim,
3. **silent supersession** — a subject's active protection disappears because a later internal packet quietly displaced it,
4. **privacy-for-protection barter** — the subject must expose everything in order to get any urgent action,
5. **transient trust collapse** — routine migration, key rollover, or routing changes are treated as substantive nullity.

## 2. Design rules

The archive now fixes seven design rules.

1. **Authentication is claim- and scope-specific.** A packet is not "valid" in the abstract; it is valid for particular claims issued by actors competent to issue those claims.
2. **Supersession must be explicit.** No packet should be displaced merely by implication, timestamp, or internal database overwrite.
3. **The operative packet is selected by lawful scope first, recency second.** Later time matters only after issuer competence and supersession scope are established.
4. **Verified core beats unverified expansion.** If the core urgency, identity path, or preservation need is authenticated but a wider annex remains disputed, the verified core may still justify narrow preservative action.
5. **Sealed annexes need public-safe descriptors.** Sensitive content may stay sealed, but the existence, holder, hash or equivalent integrity marker, access rule, and gist-level purpose should remain legible.
6. **Transient trust failure is not automatic defeat.** A chain that fails because of migration, resolver lag, or key rollover should move to retry, alternate verification, or review rather than instant nullity. `[REF-0220]`
7. **Historical verifiability matters.** The archive should preserve enough proof material, timestamps, and key-history references to verify why an urgent act was lawful when made even if the live trust chain later changes. `[REF-0219]` `[REF-0220]` `[REF-0222]`

## 3. Minimum metadata that every live emergency packet chain now needs

The archive now adds eight minimum metadata items to the emergency packet family:

1. **authentication envelope reference** — where the proof set, signature, seal, or trust-chain material for this packet lives,
2. **authoritative timestamp** — issuance time plus an attributable timestamp or equivalent time source,
3. **scope statement** — which claim class this packet may create, change, suspend, or supersede,
4. **supersedes / superseded-by fields** — explicit backward and forward references,
5. **verification status marker** — fully verified, core verified / annex pending, transient failure, final failure, or dispute marker,
6. **sealed-annex descriptor references** — if any sealed materials exist,
7. **historical-key or trust-path reference** — where a reviewer can verify older proofs after rollover or migration,
8. **review clock for unresolved conflict** — when the next authority must decide the conflict instead of letting ambiguity drift.

This is still deliberately small. The archive is not trying to embed a full identity-federation profile in every doctrine surface. It is fixing the minimum data that stops live packet chains from becoming clerical mystery objects.

## 4. Auxiliary packet objects

The archive now treats four auxiliary objects as the minimum companion layer.

### AU-1 — Authentication envelope

This object binds the packet to attributable proof.

It should include:
- packet identifier,
- issuer identifier,
- proof type or trust method,
- proof set or proof chain reference,
- authoritative timestamp,
- current verification status,
- and historical-key or trust-path reference if later verification may require it.

AU-1 may be embedded or external. What matters is that another competent actor can tell **who signed what, when, and under what trust path**. The archive is deliberately borrowing from proof-set / proof-chain logic and trust-chain resolution patterns rather than inventing a custom metaphysics of digital sincerity. `[REF-0219]` `[REF-0220]`

### SX-1 — Supersession notice

This object says what changed.

It should identify:
- prior packet,
- superseding packet,
- issuer,
- effective time,
- scope of supersession,
- reason code,
- whether the prior packet remains historically valid,
- and whether emergency protection stays in force during review.

Reason codes should stay narrow: clerical correction, added evidence, changed facts, extension, lift, transfer of competence, or withdrawal.

The archive rejects silent overwriting. If a packet changes legal position, there should be a reviewable SX-1 object that tells later institutions what changed and why.

### SA-1 — Sealed-annex descriptor

This object lets annexes stay sealed without becoming invisible.

It should identify:
- annex identifier,
- holder or custodian,
- integrity marker,
- sensitivity class,
- opening authority class,
- public-safe gist,
- and notification rule for any opening.

The gist must be enough to explain why the annex matters without disclosing the protected content itself. OHCHR confidentiality practice shows the right pattern: some information, including identity, may remain confidential without making the complaint nonexistent. `[REF-0223]`

### VX-1 — Verification exception or challenge marker

This object records what could not yet be verified.

It should identify:
- the packet or annex at issue,
- whether the problem is transient, substantive, or scope-based,
- whether core urgency is still verified,
- what temporary acts remain lawful while review continues,
- and the next retry or review deadline.

VX-1 matters because "cannot verify everything yet" is not the same as "nothing here may be acted on."

## 5. Operative-packet rule

The archive now fixes a compact operative-packet rule for live emergency disputes.

### Step 1 — Separate the claims

Different claims may have different competent issuers.

The same packet chain may contain:
- steward-authenticated operational facts,
- tribunal-authenticated stays,
- fallback-issuer identity facts,
- and representative acknowledgments.

No institution should pretend that one actor's competence for one field automatically extends to all others.

### Step 2 — Check explicit supersession

If an SX-1 notice exists from a competent actor for that scope, it governs unless suspended or stayed.

### Step 3 — Prefer narrower lawful competence over mere later time

If two packets conflict, the operative one is chosen by:
1. competent authority for that claim scope,
2. explicit supersession,
3. review or court order over ordinary issuer action,
4. later authoritative time only after the first three checks.

### Step 4 — If same-scope conflict remains, preserve and escalate

If two same-scope packets remain facially valid and neither is clearly subordinate, the archive's minimum rule is:
- preserve the subject, evidence, and identity path,
- keep the less destructive status quo where feasible,
- emit VX-1,
- and force short-clock review by a body competent to decide the conflict.

A packet conflict should not silently liquidate the subject's protections.

## 6. Sealed-annex handling

The archive now fixes five handling rules.

1. **Sealed annexes may support temporary protection.** A sealed annex plus SA-1 descriptor may justify receipt, routing, preservation, anti-return, or short stay where the face packet and gist show credible risk.
2. **Terminal or merits-heavy acts need fuller review.** Final derecognition, destructive transfer, or terminal adverse merits action should not rest only on unseen annex content unavailable to any independent reviewer.
3. **Identity may stay sealed from the adverse actor where exposure itself is dangerous.** `[REF-0223]`
4. **Opening a sealed annex is a logged event.** The opening authority, time, basis, scope, and notification decision should be recorded.
5. **Redaction is not supersession.** A redacted packet and its sealed annex descriptor may coexist with the full packet; one does not silently replace the other.

## 7. Partial verification, trust failure, and historical proof

OpenID Federation already anticipates multiple valid trust chains, transient validation errors during topology changes, deterministic policy resolution, and historical-key problems. OpenID4VP already says the wallet must refuse a request if it cannot establish trust. eIDAS guidance already distinguishes seals, timestamps, preservation, and registered delivery proof of sending and receipt. `[REF-0220]` `[REF-0221]` `[REF-0222]`

The archive therefore fixes four rules.

1. **Multiple valid chains require a local policy, not denial by confusion.** A shorter chain, more specific authority path, or other published local rule may choose among valid chains, but the rule should be declared rather than improvised. `[REF-0220]`
2. **Transient verification failure triggers retry, alternate resolution, or reviewer escalation.** It should not be treated as proof of falsity. `[REF-0220]`
3. **A verifier who cannot establish trust should refuse broader reliance, but should still emit a reviewable exception marker rather than black-holing the packet.** `[REF-0221]`
4. **Historical proof must remain checkable.** Preservation services, timestamps, historical keys, or equivalent proof references should let later reviewers verify why a packet was relied on when issued. `[REF-0219]` `[REF-0222]`

## 8. Relationship to the archive's existing surfaces

This document does not replace the emergency packet family.

It says how the family stays legally legible once it starts forking, correcting itself, redacting itself, or moving across trust paths.

- `docs/30-transition/emergency-protection-packet-minimums.md` says what the minimum family is.
- `docs/30-transition/no-wrong-door-receipt-routing-and-designated-authority-duty.md` says who must receive and forward it.
- `docs/30-transition/provisional-proof-anti-derecognition-and-fallback-issuer-minimums.md` says when emergency identity and standing may start.
- `docs/20-world-design/packet-privacy-and-authority-rules.md` says who may inspect, seal, freeze, or contest consequential packets.
- `docs/30-transition/status-publication-challenge-logs-and-conflict-freeze.md` says what must become publicly legible once an authenticated live packet is challenged and why the dispute should freeze destructive drift rather than erase status.
- `docs/20-world-design/technical-rights-infrastructure.md` says why a packetized rights substrate is needed in the first place.

This document now adds the missing operational answer to a narrower question:

**what should count as the operative live packet when authentication is partial, supersession is contested, and some decisive material must stay sealed?**

## 9. What this now settles

1. **The archive's emergency stack now has a canonical operative-packet rule, not just a packet family.**
2. **Supersession is now an explicit, reviewable event rather than an internal overwrite.**
3. **Sealed annexes may support urgent protection without becoming universally visible.**
4. **Partial verification can justify narrow preservation and short-clock review without forcing all-or-nothing nullity.**
5. **Historical proof and trust-path preservation are now part of the minimum design for live emergency packet chains.**
6. **Full schema profiles, resolver implementations, and hardest equal-authority conflict cases remain followthrough work rather than fully closed here.**
