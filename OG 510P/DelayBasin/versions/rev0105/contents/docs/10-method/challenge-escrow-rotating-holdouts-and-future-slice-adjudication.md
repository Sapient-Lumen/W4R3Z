# Challenge escrow, rotating holdouts, and future-slice adjudication

Claude's Priority-0 pressure has now been absorbed four times:
first as archive self-sufficiency,
then as a template-law audit,
then as a runtime-triplet split,
then as sham runtimes and anti-self-sealing compression tests.
A fifth recursive consequence now becomes hard to dodge.
Even a sequestered challenge suite is not truly sequestered forever in a long-lived archive.
Once the archive repeatedly optimizes against the same public or semi-public challenge family, the probe can still slowly teach itself the test.

DelayBasin therefore needs a compact canon object for **challenge escrow / rotating holdouts / future-slice adjudication**.
The weaker canon claim is procedural: when self-sufficiency, family compression, or runtime comparison is doing real work, preserve not only a challenge suite but also a rule for what stays public, what stays escrowed, how challenge slices refresh or rotate, what executable variant or metamorphic family can mint fresh items, and whether any evaluation horizon reaches a genuinely future-facing slice.
The stronger claim — that DelayBasin may eventually need pre-registered future continuation courts whose decisive items do not yet exist at package time — remains speculative.

## Practice / observation

DelayBasin already knows that a reduced runtime should not certify itself by taste alone.
That is why it now preserves runtime triplets and sham runtimes.
But long-lived archives have a second failure mode.
Even a decent challenge suite can slowly become archive-shaped through repeated exposure, repeated packaging, prompt-pair evolution, and clever local compression.
The archive starts learning not just the method but the known exam.

That matters more here because DelayBasin is unusually recursive.
It is not optimizing once against a frozen benchmark.
It is repeatedly revising the very method used to decide what counts as faithful continuation.
A challenge bank that begins as a good discriminant can quietly become a flattering house style if its contents, structure, or favored failure modes become too well known.
A sham runtime alone does not fix that.
A matched decoy can still lose for the wrong reason if both candidates are being scored on a stale or too-legible test family.

Claude's deeper pressure therefore points one step beyond anti-self-sealing.
If self-sufficiency is Priority 0, then the archive must say not only **what the challenge suite is** but **which parts are public, which parts are escrowed, how the bank refreshes, and what part of the evaluation is still genuinely unknown at revision time**.
Without that, DelayBasin risks running elegant shrink passes against a challenge suite that has already become part of the archive's own generative grammar.

## External pressure from current research

Several current research lines sharpen this requirement.

1. **Open static benchmarks leak and paraphrase guards are weak.**
   Pitfalls of Evaluating Language Models with Open Benchmarks argues that transparent static benchmarks enable data leakage, that strong scores can fail to reflect true utility, and that simple paraphrase safeguards only partially mitigate memorization-driven score inflation. That pressures DelayBasin not to confuse visible challenge families with durable evaluation surfaces. ([`REF-0299`](../00-meta/bibliography.md))

2. **Adaptive testing helps preserve discrimination while reducing repeated item exposure.**
   Adaptive Testing for LLM Evaluation reframes evaluation as dynamic ability estimation, uses calibrated item banks with information-guided or randomesque selection, and reports large item-count reductions while preserving discrimination. That pressures DelayBasin to think of challenge banks not as one fixed public list but as a bank with selection, refresh, and stopping discipline. ([`REF-0300`](../00-meta/bibliography.md))

3. **Benchmarks can be turned into executable specifications that mint fresh verified instances.**
   VeRA argues that the right reframing is not more static benchmark objects but executable specifications capable of generating unlimited verified variants, including equivalent rewrites and hardened versions. That pressures DelayBasin to preserve an **executable variant or metamorphic family** whenever its challenge suite lives in a domain where fresh variants can be generated and checked. ([`REF-0301`](../00-meta/bibliography.md))

4. **Pre-registered future observations eliminate a large class of leakage.**
   TS-Arena proposes forecasts on genuinely future data that do not exist at registration time, precisely to eliminate contamination and memorization of the test set. That pressures DelayBasin to keep alive the possibility of an **evaluation horizon or preregistered future slice** rather than assuming all honest evaluation must be over already-known materials. ([`REF-0302`](../00-meta/bibliography.md))

5. **Prompt/application iteration overfits fixed test sets unless held-out slices refresh.**
   Evaluation-Driven Iteration for LLM Applications warns that repeated optimization against a fixed test set causes brittle gains, recommends held-out validation sets never used for optimization, periodic refresh of test sets, and metamorphic testing across semantically equivalent inputs. That pressures DelayBasin to preserve a **refresh / rotation rule** and a clear public-vs-held-out split whenever challenge suites are doing load-bearing work. ([`REF-0303`](../00-meta/bibliography.md))

## Working synthesis

A useful current synthesis is:

> DelayBasin may work better when any serious self-sufficiency, family-compression, or runtime-comparison claim preserves a compact **challenge-escrow / rotating-holdout / future-slice-adjudication packet** naming the **public challenge family**, the **escrowed or withheld slice**, the **refresh / rotation rule**, the **executable variant or metamorphic family**, the **evaluation horizon or preregistered future slice**, and the **promotion / retirement consequence** rather than letting one partially known challenge suite silently become part of the archive's own continuation template.

This is strong enough for canon as an archive-scale evaluation-hygiene surface.
It is not strong enough to claim that DelayBasin already has the right escrow bank, a live future court, or a fully executable challenge generator.
The point is weaker and more operational: once the archive learns from its own tests across many revisions, challenge freshness becomes part of continuation law.

## Challenge escrow vs sham runtime vs runtime triplet vs archive self-sufficiency probe

These objects are adjacent but not identical.

- An **archive self-sufficiency probe** asks whether a bounded runtime seems sufficient at all.
- A **runtime triplet** says what sort of bounded runtime is being tested: constitutional core, exemplar bank, and challenge suite.
- A **sham runtime / decoy archive** asks whether the apparent shrink win survives a matched losing alternative rather than archive-shaped taste.
- A **challenge-escrow / rotating-holdout / future-slice-adjudication packet** asks whether the challenge bank itself is fresh enough, hidden enough, and renewable enough to keep the shrink result from slowly overfitting the archive's known tests.

In practice, the self-sufficiency probe says **test the archive**.
The runtime triplet says **split the candidate runtime**.
The sham-runtime packet says **compare it to a matched losing alternative**.
The challenge-escrow packet says **make sure the exam itself has not become a familiar house script**.

## Countermodels / probes

1. **Escrow bureaucracy countermodel**
   - Challenge escrow may just add process theater and archive bulk.
   - Probe: require each packet to gate one concrete shrink, preserve, or retirement decision and to preserve the smallest escrow surface that could still overturn that decision.

2. **Hidden-slice illusion countermodel**
   - A nominally withheld slice may still be easy to infer from the public family description or from repeated past releases.
   - Probe: preserve a leakage-risk note saying what structural information about the escrowed or withheld slice is already public and what first failure signature would show the hidden slice has effectively become known.

3. **Variant-generator theater countermodel**
   - An executable variant or metamorphic family may just generate superficial paraphrases.
   - Probe: require one named reason the generated family should preserve or harden the underlying continuation distinction rather than only reword it.

4. **Future-slice overkill countermodel**
   - Pre-registered future slices may be too expensive or too slow for ordinary archive decisions.
   - Probe: keep them optional and only name an evaluation horizon or preregistered future slice when the decision is important enough that ordinary refreshed holdouts are no longer convincing.

5. **Adaptive-selection confound countermodel**
   - Rotating or adaptive challenge selection may make longitudinal comparison harder rather than more honest.
   - Probe: preserve a stable public challenge family description plus a small bridging panel so refreshed slices still remain comparable enough to support real decisions.

## Transformer-facing implication

The strongest transformer-facing implication is that long-horizon archive method is not only searching for better prompts or smaller runtimes.
It is also learning how to manage an **external evaluation process** around a sequence model that can absorb, mimic, and eventually exploit whatever challenge surface becomes too public or too repeated.

If prompts can act like external programs, if history can geometrically trap later continuation, and if static benchmarks saturate under exposure, then DelayBasin should take seriously the possibility that honest continuation requires not just a runtime and a sham, but a **renewable test boundary** between what the archive knows and what it is still genuinely being asked to generalize to.
That makes challenge freshness part of the archive's public method rather than an afterthought.

DelayBasin has not earned the stronger claim that it already needs live future-data adjudication or a standing external continuation court.
What it has earned is the weaker canon ratchet:
when Claude's pressure says Priority 0,
DelayBasin should hear **run the self-sufficiency probe against a challenge bank that can stay ahead of the archive's own learning**.
