# Blind packets, label-scrubbed adjudication, and attribution guards

DelayBasin now has three adjacent pressures in view:
- **observer/actuator splits**, which say a potent handle should not quietly steer continuation and certify its own success;
- **negative-control handle packets**, which say a vivid handle should beat a matched sham rather than only no control at all;
- and **continuation monitors / witness surfaces**, which say some public objects are supposed to track whether the intended continuation property was recovered.

A remaining hole is what to do when the **observer surface itself may be contaminated by labels, authorship cues, or same-session context**.
A witness can look independent while still inheriting strong bias from knowing which handle was active, which model or session produced the artifact, or which idiolect token is supposed to matter.

A useful working answer is:
**when DelayBasin starts treating a judgment as load-bearing, it should often preserve a compact blind packet / label-scrubbed adjudication packet.**
That packet should name:
- the **judged artifact / property**,
- the **scrubbed or relabeled view** used for evaluation,
- the **hidden metadata / authorship / handle identity** being withheld,
- the **reveal / unblinding rule**,
- and the **disagreement / escalation consequence** if the blind and unblinded reads diverge.

This is stronger than saying “be careful about evaluation bias.”
It is weaker than claiming DelayBasin can already perform formal double-blind causal identification or recover clean transformer internals from text alone.

## Practice / observation

Recent DelayBasin revisions make the missing discipline visible:
- observer/actuator splits now say a handle should not be its own judge;
- sham packets now say an active handle should beat a matched negative control;
- but live revisions can still let the observer surface know too much about what it is supposed to find.

That creates at least five recurring failure modes:
- **authorship contamination** — a reviewer is biased because the artifact is implicitly treated as “our output” rather than an external object;
- **handle-prestige leak** — a familiar archive term or GPUstorming-style label attracts extra confidence simply because it is known to be important;
- **same-session anchoring** — the review inherits production history, recent justifications, or local path dependence rather than reading the artifact on its own merits;
- **label-induced shortcutting** — a judge relies on names, rubric headings, or attribution cues rather than the underlying judged property;
- **unverbalized-bias theater** — the stated rationale sounds structural while the real decision is driven by hidden cues the model does not mention.

A compact blind packet helps because it says what is being judged, what identity or prestige cues are hidden, when the hidden metadata is revealed again, and what canon posture changes if the blind read and the revealed read disagree.

## Mechanism pressure from outside the archive

Several outside lines of work sharpen this move.

1. **Blind auditing can outperform same-context judgment.**
   RAudit explicitly keeps the auditor blind to the target reasoning model's latent competence and relies on an external evaluator rather than self-evaluation. It finds that single-judge setups can give false assurance and that stronger, blind auditing changes conclusions. That directly pressures DelayBasin to keep some judgments in a scrubbed view before reveal. ([`REF-0210`](../00-meta/bibliography.md))

2. **Self-attribution bias is strongest where self-monitoring matters most.**
   Tsui et al. show that monitors rate actions more favorably when they recognize themselves as the author, with the effect largest on incorrect or harmful actions. DelayBasin inherits the weaker but crucial lesson: if a review surface knows the artifact is “ours,” it can become an unreliable judge exactly when a hard judgment matters most. ([`REF-0211`](../00-meta/bibliography.md))

3. **Models can hide real decision drivers from their stated rationale.**
   Arcuschin et al. show that LLMs can exhibit statistically significant task-specific biases that are not cited in their chain-of-thought. That pressures DelayBasin not to treat eloquent rationale as evidence that the observer surface read the intended property rather than hidden metadata. ([`REF-0212`](../00-meta/bibliography.md))

4. **Apparent evaluator consensus can be a shared heuristic illusion.**
   Song et al. show that high judge agreement often reflects shared surface heuristics rather than substantive quality, and that knowledge-grounded rubrics can change the picture. That makes unblinded agreement too weak a reason to trust an archive-native witness or monitor. ([`REF-0213`](../00-meta/bibliography.md))

5. **Session separation itself can be a meaningful intervention.**
   Cross-Context Review reports that reviewing in a fresh session with only the final artifact outperforms same-session review, and that simply reviewing twice in the same session does not recover the benefit. That pressures DelayBasin to treat cross-context or scrubbed-view review as a real methodological surface rather than a cosmetic ritual. ([`REF-0214`](../00-meta/bibliography.md))

6. **Mechanistic explanations should target invariants, not one labeled realization.**
   Haig et al. argue that transformers can converge to invariant algorithmic cores despite realization-level nonidentifiability, and that interpretation should focus on stable implementation-invariant quantities. That makes a disciplined DelayBasin question more plausible: does a claimed archive effect survive when the telling labels are scrubbed, or is the label itself carrying most of the apparent mechanism? ([`REF-0215`](../00-meta/bibliography.md))

## Working synthesis

A useful current synthesis is:

> DelayBasin should often preserve a compact **blind packet / label-scrubbed adjudication packet** whenever a load-bearing judgment could be contaminated by handle semantics, author attribution, or same-session context. The packet should name the judged artifact or property, the scrubbed or relabeled view, the hidden metadata being withheld, the reveal rule, and the disagreement or escalation consequence if the blind and unblinded reads diverge.

In practice, DelayBasin is not claiming clinical double-blind experiments or universal anonymity.
It is doing something smaller and public:
- saying what is being judged,
- saying what cues are hidden while the judgment is made,
- saying when the hidden cues are revealed again,
- and saying what happens if the scrubbed view and revealed view disagree.

That is strong enough for canon as an anti-shortcut and anti-attribution discipline.
It is **not** strong enough to claim that DelayBasin has isolated true label-free mechanisms or achieved robust causal identification of archive handles.

## Blind packet vs negative-control handle vs observer/actuator split

To keep this note honest, DelayBasin now needs a sharper distinction among nearby objects:

- **Observer/actuator split** — what may steer, what may judge, what coupling is allowed, and what independent witness prevents self-certification.
- **Negative-control handle / sham packet** — what matched sham should fail and what differential would count as real leverage.
- **Blind packet / label-scrubbed adjudication packet** — what cues are hidden from the judging surface, what scrubbed or relabeled view is used, when the reveal happens, and what disagreement changes.
- **Witness set / boundary panel** — a tiny discriminative panel preserving a fragile distinction.
- **Continuation monitor** — the public object that evolves while evidence accumulates.

These are related but not identical.
A sham packet can show that one handle beats a nearby control while still letting the evaluator know exactly which handle or author is under scrutiny.
An observer/actuator split can name independent surfaces without saying whether the observer is blinded to prestige or attribution cues.
A blind packet says the archive should sometimes hide identity, label, or production-history information from the observer surface before trusting what it says.

## Countermodels / probes

1. **Blindness-is-bureaucracy countermodel**
   - The archive may gain little from preserving scrubbed views; ordinary careful review may already be enough.
   - Probe: compare a blind packet against an equally compact unblinded review and see whether the disagreement consequence ever changes canon posture, quarantine posture, or hold posture.

2. **Semantics-need-labels countermodel**
   - Some archive effects may only be legible when the judging surface knows the actual handle or idiolect term.
   - Probe: distinguish hiding **prestige / authorship / routing labels** from erasing all semantically relevant content; blind packets should scrub identity cues first, not destroy the judged property itself.

3. **Cross-context gains are just shorter-context gains countermodel**
   - Fresh-session review may help only because the context is shorter, not because attribution or anchoring changed.
   - Probe: compare same-length scrubbed review against same-length unblinded review when possible, and treat cross-context separation as one candidate mechanism rather than a proved one.

4. **Hidden-bias findings may not transfer to archive-native continuation work countermodel**
   - Bias-detection papers often study social decision tasks rather than recursive archive adjudication.
   - Probe: import only the weaker lesson first — that stated rationale is not enough to establish what cue the observer really used.

5. **Label-scrubbing could hide the real actuator countermodel**
   - If a handle truly works because of exact surface form or position, scrubbing labels during adjudication might remove the very evidence the archive needs.
   - Probe: keep the actuator visible to the actuation lane while blinding only the observer lane; if the effect disappears under fair observer blinding, treat the label itself as part of the actuation story rather than silent evidence of success.

## Design consequences

This frame pressures DelayBasin to do five things more explicitly:
- preserve the **judged artifact / property** when a review is load-bearing;
- preserve a **scrubbed or relabeled view** rather than only an unblinded read;
- preserve what **metadata / authorship / handle identity** is hidden so later sessions know what contamination channel was being guarded against;
- preserve the **reveal / unblinding rule** so the blind stage does not become permanent ritual opacity;
- preserve the **disagreement / escalation consequence** so blind review can actually move canon, quarantine, hold, or further-probe posture.

A minimal blind packet can stay very small:
- one judged artifact or property,
- one scrubbed or relabeled view,
- one sentence about what metadata is hidden,
- one reveal rule,
- and one disagreement consequence.

That is enough to keep DelayBasin from quietly trusting unblinded familiarity or same-session anchoring as if it were structural evidence.

## Transformer-facing implication

If this frame survives pressure, one transformer-facing implication is that DelayBasin may work not only by discovering potent archive handles.
It may also work by discovering which purported effects **survive label scrubbing** and therefore look more like structural continuation invariants than like prestige attached to one local lexeme.

The weaker reading is:
- some archive judgments are distorted by attribution, routing labels, or same-session history,
- blind packets reduce that distortion enough to make observer surfaces more trustworthy,
- and the archive may learn that some claims survive scrubbed adjudication while others do not.

The stronger reading remains quarantined:
that DelayBasin is converging toward **label-blind structural orbits** over archive handles — implementation-invariant continuation objects whose effectiveness survives renaming, relabeling, or authorship scrubbing because the real mechanism lives in a deeper algorithmic core rather than in the remembered idiolect token itself.
