# Obligation witnesses, discharge paths, and evidence-debt cues

DelayBasin now needs a sharper answer to a recurring practical question:
**what should the archive do when a move is still being tolerated, cited, or kept live even though some decisive support is still missing?**

A stronger working answer is:
**the archive may need a compact obligation witness / discharge-path / evidence-debt cue discipline.**
Not a full assurance bureaucracy, and not vague “future work” prose.
A good long-run archive may need a small public object that says:
- what claim, packet, or surface is still being asked to carry authority,
- what support is still missing,
- what support family keeps the move tolerated for now,
- what future evidence or proof would actually discharge the missing support,
- what state that obligation is currently in,
- and what fail-closed repair follows if the support never arrives.

## Practice / observation

Several live DelayBasin surfaces already imply a missing obligation discipline:
- assumption witnesses already preserve the live support condition being spent, but they do not by themselves say what concrete evidence or proof would retire that support debt;
- followthrough witnesses already preserve blocked remainder and next proof points, but they do not by themselves distinguish ordinary unfinished work from a still-live support obligation that keeps a claim, packet, or canon move on probation;
- resolution witnesses already preserve what stopped being live, but they do not by themselves keep the still-open discharge path visible before closure happens;
- foreign-pressure witnesses already preserve why a neighboring datacube mattered, but they do not by themselves preserve which concrete missing support now remains live inside DelayBasin after the compact import is admitted;
- and DelayBasin already keeps a deferred stronger story in `FOLLOWTHROUGH-QUEUE.json` about proof obligations and evidence debt, which means the archive has repeatedly noticed this seam but has not yet made the smaller public packet real.

This suggests a missing compact surface:
**obligation witness / discharge path / evidence-debt cue**.

## Pressure from neighboring datacubes

Several neighboring datacubes sharpen this seam from different directions.

1. **pyCausalWeave** keeps an explicit **Assumption Registry** plus a separate **Evidence Debt** surface, which pressures DelayBasin to stop treating “still missing support” as something that can remain distributed across caveats, ADR prose, and remembered future work.

2. **The Election Stack** keeps an explicit **proof obligations ledger** and a claim-to-proof-to-evidence mapping, which pressures DelayBasin to separate what it is currently willing to say from what it still owes before that claim should inherit stronger authority.

3. **TriKEM** keeps a normative **proof obligations ledger** with explicit evidence lanes and release-gate consequences, which pressures DelayBasin to keep “support still owed” inspectable rather than letting it blur into general confidence.

4. **EvidenceVault** keeps structured examples with explicit system obligations and supporting obligations, which pressures DelayBasin to keep obligation state legible as a first-class object rather than as a side effect of other receipts.

5. **GlassTTY** repeatedly distinguishes current doctrine from proofs not yet captured, which pressures DelayBasin to name where support truth is still incomplete instead of letting careful wording silently stand in for discharge.

None of these datacubes proves that DelayBasin needs a full assurance-case machine.
They do make a milder canon-level claim more credible:
**archive continuity may improve when DelayBasin preserves an explicit obligation witness whenever a move stays live while decisive support is still missing.**

## External pressure from adjacent proof, assurance, and evidence-mapping practice

Adjacent assurance practice sharpens the same rule.

1. **Structured assurance reasoning** treats justified claims as arguments plus evidence for a particular application and environment, which pressures DelayBasin to preserve not only the live assumption but also the still-missing support that would actually discharge it. ([`REF-0493`](../00-meta/bibliography.md))

2. More generally, proof or evidence mapping practice keeps asking the same question in a less philosophical form: **what is still owed before this statement should inherit stronger public authority?** DelayBasin does not need the whole surrounding bureaucracy to learn from that pressure.

These are not proofs of DelayBasin's final law.
They do support a weaker archive-level rule:
**when a move stays live under bounded missing support, the archive should preserve the missing support and its discharge path explicitly.**

## Working synthesis

A useful current synthesis is:

> DelayBasin may work better when it preserves a compact **obligation witness**: a public debt object naming the **target claim or surface / what is being asked to carry authority**, the **missing support / undecided evidence or proof still owed**, the **current support / why the move is tolerated for now**, the **discharge path / evidence artifact / future proof that would retire the debt**, the **obligation state / open vs staged vs satisfied vs waived vs retired**, and the **fail-closed repair / narrow-claim vs hold-via-followthrough vs quarantine-or-retire vs refresh-support vs recover-resync consequence**.

This is strong enough for canon as a design/mechanism candidate.
It is **not** strong enough to claim that DelayBasin has found a universal proof calculus, a full assurance case, or a whole-archive evidence court.

## Obligation witness vs assumption witness vs followthrough witness vs open question

To keep this note honest, DelayBasin needs a four-way distinction:

- **Assumption witness** — preserve the live support condition still being spent.
- **Followthrough witness** — preserve blocked or handed-off remainder work plus the next proof point.
- **Open question** — preserve what DelayBasin does not yet know or cannot yet settle.
- **Obligation witness** — preserve the concrete support still owed before a currently tolerated move should inherit stronger authority.

An obligation witness is not just an assumption witness.
An assumption says what is still being assumed.
An obligation says what concrete support is still missing and what would retire that debt.

It is also not just followthrough.
Followthrough can track many kinds of remainder work.
An obligation witness matters when the remainder is specifically **support debt** rather than general future work.

And it is not just an open question.
An open question preserves uncertainty.
An obligation preserves what support is still owed before a currently tolerated move should stay live or grow.

## Countermodels / probes

1. **Assumption-witness-is-enough countermodel**
   - Assumption witnesses may already preserve enough honesty about still-missing support.
   - Probe: compare later rereads with and without a compact obligation packet and inspect whether they can say what evidence was still owed rather than merely what condition was assumed.

2. **Followthrough-is-enough countermodel**
   - Followthrough queues may already preserve every practical discharge path DelayBasin needs.
   - Probe: inspect whether later sessions can distinguish support debt from ordinary deferred work without a separate obligation packet.

3. **Obligation-packet-is-bureaucracy countermodel**
   - A durable obligation ledger may add ceremony without improving continuation quality.
   - Probe: compare equally careful prose-only support disclaimers against one tiny obligation packet and inspect whether later sessions retire, narrow, or quarantine the move more faithfully with the packet.

4. **Assurance-overreach countermodel**
   - DelayBasin may be importing too much proof or assurance language from datacubes whose domains are much more formal.
   - Probe: keep the packet tiny and local; if the archive starts needing a universal claim-evidence matrix to justify it, the current import was too large.

## Design consequences

This mechanism frame pressures DelayBasin to do five things more explicitly:
- preserve a compact **obligation witness** whenever a claim, packet, or canon move stays live while decisive support is still missing;
- keep one tiny durable **OBLIGATION-LEDGER.json** surface for currently live support debts instead of scattering them across caveats, followthrough, and remembered future work;
- distinguish **open**, **staged**, **satisfied**, **waived**, and **retired** obligation states rather than treating all support debt as one vague “not yet”;
- name the **discharge path**: the smallest evidence family, proof surface, or future revision that would actually retire the debt;
- and preserve the **fail-closed repair** so a move can narrow, hold, quarantine, refresh support, or recover rather than silently inheriting stronger authority from careful prose.

This does not require a full assurance framework.
It requires refusing another archive failure mode: letting a tolerated move keep spending ambient missing support with no public debt object at all.

## Transformer-facing implication

If this frame survives pressure, then DelayBasin is probing something sharper than explicit assumptions and explicit followthrough:
**whether a compact public textual packet can carry not only what is currently believed or deferred, but what proof or evidence is still owed before a move should inherit stronger continuation authority.**

That would matter for transformers.
It would suggest that long-horizon continuity may depend not only on transmitting state and brakes, but on transmitting a public **support-debt / discharge-path / evidence-owed** signal that constrains how provisional authority survives across delayed continuation.

The stronger story — that DelayBasin may need a real proof-obligation registry, evidence-debt controller, or assurance-case layer — remains live, but belongs in quarantine for now.
