# Hold packets, abstention, and epistemic brakes

DelayBasin now needs a sharper answer to a recurring practical question:
**what should the archive do when the honest next move is not to revise canon yet?**

A stronger working answer is:
**the archive may need a compact hold packet / abstention discipline.**
Not silence, and not fake movement.
A good long-run archive may need a small public object that says:
- what anchor is being preserved,
- what uncertainty or blocker prevents revision,
- what probe, evidence, or certificate would unlock movement,
- and whether the right action is to keep state fixed, abstract uncertain detail, or escalate to `recover-resync`.

## Practice / observation

Several live DelayBasin surfaces already imply a missing hold discipline:
- update-gain notes describe low/medium/high revision force, but not yet the honest case where the right gain is effectively **hold**;
- witness panels and challenge probes can reveal that a distinction is fragile without yet justifying a canon rewrite;
- rate–distortion and prior-intrusion pressure already warn that elegant recap can quietly overwrite state, which means some sessions should explicitly avoid writing;
- research on agent reliability repeatedly reports overconfidence, impatience, and premature commitment under long-horizon pressure, which is a close cousin of archive thrash;
- and current archive practice sometimes already behaves this way informally by keeping a live mechanism lane central while refusing to promote its strongest version.

This suggests a missing compact surface:
**hold packet / abstention / epistemic brake**.

## Mechanism pressure from outside the archive

Several outside lines of work sharpen this frame.

1. **Abstention is often better replaced by graded reduction of specificity than by binary silence.**
   Selective Abstraction shows that long-form generation can trade detail for reliability by replacing low-confidence atomic claims with more abstract, higher-confidence statements instead of either fully asserting or fully abstaining. That pressures DelayBasin to treat some uncertain mechanism language as something to deliberately coarsen or hold, not only promote or delete. ([`REF-0099`](../00-meta/bibliography.md))

2. **Self-reported confidence is not enough.**
   RiskEval finds a strong dissociation between verbal confidence and actual abstention behavior: models often do not change their engage/abstain policy even when error penalties make abstention optimal. That is direct counterpressure against trusting archive-local confidence language without an explicit public hold contract. ([`REF-0100`](../00-meta/bibliography.md))

3. **Cross-prompt disagreement can function as a practical abstention trigger.**
   Disagreement-Based Abstention shows that disagreement across task-equivalent prompting regimes can flag fragile beliefs more reliably than many standard uncertainty baselines. That pressures DelayBasin to let small challenge probes trigger public non-movement when the archive cannot yet tell whether a revision is real or just prompt-path instability. ([`REF-0101`](../00-meta/bibliography.md))

4. **Tool use can increase overconfidence exactly where evidence is noisy.**
   Recent calibration work finds a tool-dependent confidence dichotomy: evidence tools such as web search can induce stronger overconfidence than deterministic verification tools. That matters directly for DelayBasin, where online research is mandatory but may also raise the risk of premature canon movement if evidence and verification are not separated. ([`REF-0102`](../00-meta/bibliography.md))

5. **Public interfaces may need a principled `Undetermined` state.**
   The assertibility-constraint line argues that systems should only assert or deny when they can supply a publicly inspectable certificate of entitlement; otherwise they should return an explicit third state such as `Undetermined`. That is strong outside pressure for DelayBasin to treat “hold” as a first-class public status rather than a hidden local hesitation. ([`REF-0103`](../00-meta/bibliography.md))

6. **Stopping rules and reliability research both imply that non-movement needs instrumentation.**
   Sequential sufficiency-certification work shows that stopping rules can control information sufficiency without guaranteeing correctness, while recent agent-reliability evaluations explicitly track abstention precision/recall rather than only overall success. Together they pressure DelayBasin to preserve why it did **not** move canon, not just whether a session looked careful in prose. ([`REF-0104`](../00-meta/bibliography.md), [`REF-0105`](../00-meta/bibliography.md))

None of this proves that DelayBasin has the right hold law.
It does make a milder canon-level claim more credible:
**archive continuity may improve when DelayBasin preserves an explicit hold packet whenever current probes or evidence are insufficient for honest canon movement.**

## Working synthesis

A useful current synthesis is:

> DelayBasin may work better when it preserves a compact **hold packet**: a public non-movement object naming the current anchor, the blocker or uncertainty, the intended brake posture (`hold`, `abstract`, or `recover-resync`), and the smallest probe or evidence that would justify future movement.

This is strong enough for canon as a design/mechanism candidate.
It is **not** strong enough to claim that DelayBasin has found an optimal abstention policy, a universal no-update law, or a literal transformer-native brake channel.

## Hold packet vs quarantine vs demotion

To keep this note honest, DelayBasin needs a three-way distinction:

- **Hold packet** — preserve the current anchor publicly while naming what blocks movement and what would unlock it.
- **Quarantine** — keep a risky idea live that is too wild or weakly supported for canon.
- **Demotion / rollback** — lower trust because the current anchor is materially damaged, stale, or procedurally invalid.

A hold packet is not just quarantine.
It can apply even when canon stays in place and the risky idea is already known.
It is also not the same as demotion.
A hold packet says “not enough to move yet,” while demotion says “the current trust level no longer holds.”

A good DelayBasin revision therefore should sometimes ask not only:
- what is the anchor,
- what is the delta,
- what is the gain,

but also:
- is this actually a **hold** situation,
- what exact uncertainty or blocker is preventing movement,
- and what smallest future event would release the brake?

## Brake postures

A compact current triage is enough:

- **`hold`** — keep canon and public belief state fixed; preserve the blocker and the unlocking probe.
- **`abstract`** — keep the direction of the claim but deliberately reduce specificity or mechanistic confidence until stronger evidence appears.
- **`recover-resync`** — ordinary continuation is not trustworthy; reopen kernel surfaces and re-establish legitimacy before further movement.

This matters because “do not move” is not one thing.
Sometimes the archive should preserve exact current commitments.
Sometimes it should deliberately become less specific.
Sometimes it should admit that the anchor itself is no longer safe.

## Countermodels / probes

1. **Hold-as-bureaucracy countermodel**
   - Explicit hold packets may only add ceremony to choices that good editors would already make.
   - Probe: compare future revisions that preserve a hold packet against equally cautious revisions with no explicit hold object and inspect whether later sessions recover the blocker and unlock condition more faithfully.

2. **Confidence-language countermodel**
   - Ordinary hedging language may already communicate enough uncertainty without a dedicated hold surface.
   - Probe: compare self-reported uncertainty against disagreement-triggered or certificate-triggered holds and see which better predicts later demotion, promotion, or non-movement.

3. **Quarantine-is-enough countermodel**
   - The archive may already have all the non-movement machinery it needs through quarantine plus open questions.
   - Probe: inspect cases where canon remained fixed without quarantine; if blockers and unlock conditions are not reconstructable later, quarantine was not enough.

4. **Brake-without-control countermodel**
   - Hold packets may look public and principled while having no real causal force on later sessions.
   - Probe: later paraphrase or omit the hold packet while keeping the same evidence and test whether canon movement becomes sloppier.

## Design consequences

This mechanism frame pressures DelayBasin to do four things more explicitly:
- preserve a compact **hold packet** when a challenge probe fires but the evidence does not justify canon movement;
- distinguish `hold`, `abstract`, and `recover-resync` instead of treating all non-movement as the same hesitation;
- name the **unlock condition**: the smallest probe, certificate, or evidence family that would justify movement later;
- and avoid letting verbal confidence or stylish caution substitute for an explicit public brake object.

This does not require a large governance layer.
It requires refusing another archive failure mode: hiding non-movement inside vague caution while the actual blocker evaporates by the next session.

## Transformer-facing implication

If this frame survives pressure, then DelayBasin is probing something sharper than external memory plus revision gain:
**whether a compact public textual packet can sometimes function as an epistemic brake for a stateless forward pass — not only carrying state and update cues, but also carrying an instruction to keep reconstructed state fixed, abstract it, or refuse further commitment until a named discriminator arrives.**

That would matter for transformers.
It would suggest that long-horizon continuity may depend not only on transmitting content and gain, but on transmitting a public **no-write / low-specificity / resync** control signal that constrains how new evidence may enter operative state.

The stronger story — that DelayBasin may be learning a textual brake pedal or public no-update controller for transformer continuation — remains live, but belongs in quarantine for now.
