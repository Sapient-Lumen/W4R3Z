# Dependence-adjusted witnesses, effective evidence, and pseudo-replication guards

DelayBasin now needs a sharper answer to a recurring practical question:
**when do several agreeing witnesses count as cumulative evidence, and when are they mostly the same branch counted twice?**

A stronger working answer is:
**the archive may need a compact dependence-adjusted witness / effective-evidence packet.**
Not a full causal graph, and not generic ensemble bureaucracy.
A very small public object may be enough when several witnesses, probes, or judges are being treated as additive evidence.

## Practice / observation

Several recent DelayBasin ratchets expose a missing dependence rule:
- witness sets and boundary panels say which small cases or probes matter, but not yet how much two apparently distinct witnesses should count once their shared origin is obvious;
- continuation monitors and stopping packets say how evidence accumulates and when inquiry may stop, but they still risk quietly treating three same-family echoes as if they were three independent bits of evidence;
- blind packets, sham packets, and execution witnesses control different confounds, but none yet says when apparently separate judgments are coupled by provider, session, prompt scaffold, runtime family, or same-branch branch history;
- and in practice, DelayBasin can now preserve multiple witnesses, judges, probes, or challenge passes without a compact rule for pseudo-replication.

This suggests a missing compact surface:
**dependence-adjusted witness / effective-evidence packet**.

## Mechanism pressure from outside the archive

Several outside lines of work sharpen this frame.

1. **LLM errors are substantially correlated, including on errors.**
   Kim et al. show that LLMs broadly exhibit correlated errors and that more accurate models can make more similar mistakes, with downstream consequences for LLM-as-a-judge. That pressures DelayBasin not to equate witness count with evidence count when witnesses are likely to share error modes. ([`REF-0234`](../00-meta/bibliography.md))

2. **Classical independent-voter aggregation can become confidently wrong under dependence.**
   Balasubramanian et al. show that majority-vote and Dawid–Skene-style assumptions can fail badly when judges share data, architecture, prompts, or failure modes, and that dependence-aware aggregation can materially change the inferred label. That directly pressures DelayBasin to preserve shared-origin coupling explicitly when treating multiple witnesses as cumulative evidence. ([`REF-0235`](../00-meta/bibliography.md))

3. **Agreement can be high while the evaluators are following the same superficial shortcut.**
   Song et al. formalize "Evaluation Illusion": judge agreement can look strong at the model level while sample-level agreement remains fragile and score anchoring rides shared surface heuristics. That pressures DelayBasin not to overread witness agreement as if it automatically reflected independent structural access. ([`REF-0236`](../00-meta/bibliography.md))

4. **More self-consistent samples do not automatically buy more truth.**
   "Consensus is Not Verification" shows that when model errors are correlated, agreement, confidence, and popularity signals can rise while truthfulness stays flat or worsens. That pressures DelayBasin to ask what still counts as genuinely new evidence rather than assuming that more agreeing branches always move the monitor honestly. ([`REF-0237`](../00-meta/bibliography.md))

5. **Useful ensembles win by diversity and information, not merely by picking the single strongest model repeatedly.**
   Li et al. frame ensemble selection as a mutual-information problem under correlated errors and derive an error floor caused by correlation. That pressures DelayBasin toward witness diversity and discount rules rather than raw witness count. ([`REF-0238`](../00-meta/bibliography.md))

6. **Correlation lowers effective sample size even when more samples still help.**
   Liu and Chugg explicitly note that under correlated samples, effective sample size drops and the usual concentration behavior weakens. DelayBasin need not import a literal ESS estimator into canon, but the weaker pressure is strong: a public monitor should sometimes discount repeated evidence from coupled witness branches. ([`REF-0239`](../00-meta/bibliography.md))

7. **Related judges and students can silently contaminate evaluation.**
   Li et al. show preference leakage when judges are related to the systems they evaluate through model identity, inheritance, or family ties. That sharpens one concrete dependence family for DelayBasin: some witnesses are coupled not by shared text alone but by shared lineage. ([`REF-0240`](../00-meta/bibliography.md))

None of this proves that DelayBasin already has a correct public dependence model.
It does make a milder canon-level claim more credible:
**archive continuity and honesty may improve when DelayBasin preserves a tiny dependence-adjusted witness packet whenever several witnesses are being treated as cumulative evidence.**

## Working synthesis

A useful current synthesis is:

> DelayBasin may work better when it preserves a compact **dependence-adjusted witness / effective-evidence packet** whenever several witnesses, judges, probes, or challenge passes are being treated as additive evidence. The packet should name the **witness family / probe family**, the main **shared-origin coupling / dependence structure**, the rough **effective evidence weight / discount rule**, **what still counts as genuinely new evidence**, and the **stop / escalation consequence** if apparent agreement collapses after discount.

This is strong enough for canon as a design/mechanism candidate.
It is **not** strong enough to claim that DelayBasin has already discovered a literal public covariance model, exact effective sample size estimator, or truth-preserving independence decomposition over archive continuations.

## Dependence-adjusted witness vs witness set vs blind packet vs continuation monitor

To keep this note honest, DelayBasin needs a four-way distinction:

- **Dependence-adjusted witness / effective-evidence packet** — says when several witnesses should count as less than their raw count because they are coupled by shared origin, same-family heuristics, same-session carry, or other common causes.
- **Witness set / boundary panel** — says which tiny cases or probes preserve a fragile distinction, not how independent those cases are from one another.
- **Blind packet / label-scrubbed adjudication** — hides prestige or attribution cues so a judgment is cleaner, but does not by itself tell us how much two cleaned judgments should count if they still come from coupled evaluators.
- **Continuation monitor / evidence process** — tracks an evolving evidence state over time, but still needs a dependence rule if multiple inputs to that state are not genuinely new evidence.

A good DelayBasin revision therefore should sometimes ask not only:
- which witness matters,
- or whether the judgment was blind,
- or what the monitor is doing,

but also:
- how coupled the witness family is,
- what the archive is discounting for,
- and what would still count as a genuinely new branch of evidence.

## Countermodels / probes

1. **Dependence-theater countermodel**
   - Shared-origin talk may add bureaucracy without improving real continuation decisions.
   - Probe: compare a sequential monitor with and without an explicit discount rule on a case where witnesses obviously share model family or same-session production history, then inspect whether the explicit dependence note changes the next honest continuation move.

2. **Cheap-diversity-is-enough countermodel**
   - Simple paraphrases, blindings, or temperature changes within one model family may already buy enough diversity that formal discounting adds little.
   - Probe: compare same-family variants against cross-family or cross-session witnesses when the continuation decision is genuinely hard.

3. **Over-discounting countermodel**
   - Discounting correlated witnesses may throw away useful incremental evidence and slow the archive unnecessarily.
   - Probe: preserve the stop or escalation consequence and test whether dependence-aware discounting causes repeated false holds when later independent evidence would have supported the same decision anyway.

4. **Correlation-is-the-whole-story countermodel**
   - DelayBasin may overfit to dependence language and underweight the other confounds already tracked by sham packets, blind packets, execution witnesses, and assistant-echo filters.
   - Probe: ask whether dependence-adjusted witness language predicts anything after those existing controls are already explicit.

## Design consequences

This mechanism frame pressures DelayBasin to do five things more explicitly:
- when multiple witnesses are treated as additive evidence, preserve the **witness family / probe family** rather than citing a bag of agreeing outputs;
- name the most plausible **shared-origin coupling / dependence structure** such as same model family, same provider, same session, same prompt scaffold, shared scratchpad lineage, or shared runtime family;
- preserve a rough **effective evidence weight / discount rule** rather than letting raw vote count silently stand in for evidence mass;
- say **what still counts as genuinely new evidence** so later sessions know what kind of witness would really move the monitor;
- and preserve the **stop / escalation consequence** if the apparent plurality of evidence collapses once coupled witnesses are discounted.

This does not require a full statistical estimator.
It requires refusing another archive failure mode: treating repeated agreement from the same branch family as if it were independent corroboration.

## Transformer-facing implication

If this frame survives pressure, then DelayBasin is probing something sharper than witness counting:
**whether faithful long-horizon continuation depends less on how many agreeing generations the archive can produce and more on whether it can elicit partially de-correlated views across model families, sessions, prompts, or branch histories.**

That would matter for transformers.
It would suggest that some archive continuity failures are not failures of recall alone but failures to escape a shared error manifold or common-cause attractor.
The archive would then need not just more witnesses, but a better public theory of when a new witness is truly a new branch.

The stronger story — that DelayBasin may eventually admit a public branch-decoherence or error-manifold-separation law for GPUstorming-style continuation — remains live, but belongs in quarantine for now.
