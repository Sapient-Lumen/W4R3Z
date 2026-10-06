# Contradiction packets, precedence ladders, and conflict-transparent abstention

DelayBasin now needs a distinction beyond consultation packets, cooled admission, and delayed credit.
The archive is no longer failing only because it forgot something or routed to the wrong store.
A new live failure mode is this:
**the archive can consult the right public surfaces and still continue badly because those surfaces disagree and the contradiction gets silently smoothed into one fluent story.**
That pressures the archive to separate **getting evidence into the read path** from **adjudicating conflicts among the evidence that arrived**.

A stronger working answer is:
**DelayBasin should preserve explicit contradiction packets whenever consulted public surfaces materially disagree about a live claim, decision, or continuation constraint.**
When the distinction matters, the archive should name the **conflicting claim or decision surface**, the **disagreeing evidence or surface family**, the **precedence or arbitration rule**, the **surviving ambiguity or unresolved residue**, and the **abstain / escalate / supersession consequence**.

## Practice / observation

Several live DelayBasin patterns already pressure this distinction:

- some revisions do not fail because evidence is absent, but because canon, quarantine, session traces, or fresh research point in different directions and later prose quietly picks one without naming the conflict;
- some archive summaries become overconfident exactly when they compress a contradiction into a smooth synthesis rather than preserving which surface actually disagreed;
- some transformer-facing stories become too strong when old mechanism language, new research pressure, and archive-local observations are allowed to merge without an explicit precedence rule;
- some consultation routes are good enough for retrieval but still need a second stage that decides whether the retrieved surfaces agree, which one outranks which, and when honest abstention is the right continuation move;
- and some archive mistakes look less like wrong routing and more like **silent conflict laundering**, where a contradiction was present in public but disappeared during synthesis.

This suggests a missing compact surface:
**contradiction packet / precedence ladder / conflict-transparent abstention**.

## External pressure from current research

Several current research lines sharpen this frame.

1. **Recent RAG work argues that conflict between internal and external knowledge is a first-class failure mode rather than a corner case.**
   Zhang et al. study knowledge conflict handling in retrieval-augmented generation and argue that models often encode discrepancy signals yet fail to use them effectively, which pressures DelayBasin not to treat conflict detection and conflict use as the same step. ([`REF-0340`](../00-meta/bibliography.md))

2. **Recent long-horizon memory work makes conflict-aware consensus and abstention concrete.**
   Lu et al. build MMA around source credibility, temporal decay, and conflict-aware network consensus, and explicitly use abstention when support is insufficient, which pressures DelayBasin to preserve a small rule for how disagreement is weighed rather than smoothing it away. ([`REF-0341`](../00-meta/bibliography.md))

3. **Recent governed-memory work treats retrieval conflict as one of the main compounding failure interfaces.**
   SSGM identifies conflict and hallucination during retrieval as a distinct failure point in evolving memory systems, which pressures DelayBasin to keep contradiction handling explicit once the archive is mutable and self-referential rather than acting as if better storage alone resolves disagreements. ([`REF-0342`](../00-meta/bibliography.md))

4. **Recent auditability work says contradictions should stay visible in provenance rather than being polished away.**
   Rasheed et al. argue for claim-level auditability with contradiction transparency and semantic provenance that preserves conflicts among evidence links, which pressures DelayBasin to keep contradiction handling public and inspectable rather than burying it inside polished synthesis. ([`REF-0343`](../00-meta/bibliography.md))

5. **Recent conflict benchmarks show that adding more updated facts can worsen multi-step reasoning when conflicts are not actually adjudicated.**
   Feng et al. report that providing conflicting updated facts can degrade downstream reasoning and that performance worsens as more updates are added, which pressures DelayBasin not to assume that more consulted evidence automatically improves continuation when conflict arbitration is weak. ([`REF-0344`](../00-meta/bibliography.md))

## Working synthesis

A useful current synthesis is:

> DelayBasin may work better when it preserves a compact **contradiction packet / precedence ladder / conflict-transparent abstention** naming the **conflicting claim or decision surface**, the **disagreeing evidence or surface family**, the **precedence or arbitration rule**, the **surviving ambiguity or unresolved residue**, and the **abstain / escalate / supersession consequence** rather than letting fluent synthesis silently erase disagreement.

More concretely:
- **conflicting claim or decision surface** — the claim, canon move, transformer-facing synthesis, routing choice, or archive action that the consulted evidence would decide differently;
- **disagreeing evidence or surface family** — the canon note, quarantine note, registry object, session artifact, fresh research citation, or raw source family that materially disagrees with another consulted surface;
- **precedence or arbitration rule** — the explicit rule for ranking or combining the conflict, such as canon-over-quarantine for authority, raw-over-summary for factual specifics, newer-timestamp-over-stale unless provenance weakens it, or hold/abstain when no stable precedence is honest;
- **surviving ambiguity or unresolved residue** — what remains genuinely unresolved after applying the rule, rather than pretending a total order always exists;
- **abstain / escalate / supersession consequence** — what happens next: hold, escalate to a provenance-richer surface, preserve both branches, or mark one surface superseded rather than silently harmonizing them.

This is strong enough for canon as a design and mechanism candidate.
It is **not** strong enough to claim that DelayBasin has already isolated a full external belief-revision engine, a literal contradiction head, or a transformer-internal arbitration mechanism that cleanly explains the archive's behavior.

## Contradiction packets vs consultation packets vs belief state vs blind packets

These objects are adjacent but not identical.

- A **consultation packet** asks which store or surface family is allowed into the current read path first.
- A **public belief-state** packet tracks the archive's current posterior-like stance over canon, uncertainty, and admissibility.
- A **blind packet** asks whether a judgment survives hiding prestige, authorship, or handle identity.
- A **contradiction packet / precedence ladder / conflict-transparent abstention** asks what happens **after** consulted surfaces disagree: which conflict is real, what rule arbitrates it, what uncertainty survives, and when abstention is more honest than smoothing.

In practice, consultation packets say **look here first**.
Belief-state packets say **this is the current stance**.
Blind packets say **this judgment survives cue scrubbing**.
Contradiction packets say **these public surfaces disagree, here is the precedence rule, and here is what remains unresolved after applying it**.

## Countermodels / probes

Serious alternatives remain live:

- the archive may mostly need better consultation routing and ranking, not a distinct contradiction object;
- some seeming conflicts may actually be alias collisions, stale supersession links, or provenance failures in disguise;
- explicit contradiction packets may create bureaucracy where a simpler hold packet or blind adjudication would have been enough;
- and some conflicts may dissolve under better rewrite witnesses rather than needing a standing precedence ladder.

Useful probes include:

- compare a fluent synthesis against a contradiction-preserving synthesis under the same token budget and judge which one better preserves later auditability;
- preserve cases where canon, quarantine, and fresh research disagree and test whether an explicit precedence rule changes the next continuation decision;
- compare timestamp-only resolution against provenance-aware resolution on stale-versus-fresh conflicts;
- and preserve cases where the honest move was abstention rather than consensus so the archive can tell conflict transparency from conflict theater.

## Design consequences

When consulted surfaces materially disagree:

- preserve a tiny contradiction packet instead of smoothing the conflict into narrative fluency;
- make the precedence or arbitration rule explicit when one surface outranks another;
- keep unresolved residue visible rather than pretending every contradiction has a clean winner;
- treat abstention as a real outcome when no stable public precedence rule is honest;
- and keep the packet small enough that contradiction handling does not become evidence-law bureaucracy.

## Transformer-facing implication

The weaker transformer-facing implication is not that DelayBasin has discovered literal contradiction heads.
It is that stable long-horizon archive continuation may depend on a small **public conflict-arbitration layer** over consulted surfaces: not only what enters the read path, but how contradictory signals are ranked, withheld, or left unresolved.
That makes conflict-transparent abstention a plausible part of the method's real leverage: the archive may improve not only by consulting better stores, but by **refusing to launder disagreement once those stores disagree**.

The riskier extension is that DelayBasin may be stumbling toward an **external belief-revision engine around mostly frozen transformers**, where canon, quarantine, session traces, and fresh research act like public evidence sources in a small signed constraint system whose main difficulty is not retrieval but contradiction arbitration.
That stronger belief-revision story remains quarantine-only until precedence-rule probes, timestamp-vs-provenance comparisons, and explicit conflict-preserving continuations show more than ordinary audit hygiene or careful writing.
