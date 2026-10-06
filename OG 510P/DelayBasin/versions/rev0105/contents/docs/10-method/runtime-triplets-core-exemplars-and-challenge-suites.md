# Runtime triplets, core-exemplars splits, and challenge suites

Claude's deeper pressure on DelayBasin does not end at “run the self-sufficiency probe.”
Once the archive starts asking what minimal support core is actually load-bearing,
it also has to ask **what kind of thing** that minimal object is.
A single undifferentiated blob is too coarse.
Current DelayBasin practice mixes at least three different functions:
constitutional rules, worked exemplars, and challenge probes.
If those roles stay fused, then self-sufficiency results are hard to interpret.
A small failure could mean the rules were insufficient, or that the examples were missing, or that the evaluation surface never checked the right failure mode.

DelayBasin therefore needs a compact canon object for this split:
a **runtime triplet / core-exemplars split / challenge-suite packet**.
The weaker canon claim is procedural: when testing archive self-sufficiency, family compression, or minimal loaders, preserve the runtime split explicitly.
The stronger claim — that DelayBasin may ultimately compile to a tiny cross-family runtime object — remains speculative.

## Practice / observation

DelayBasin has now named two adjacent pressures.
The **archive self-sufficiency probe** asks whether the current archive mass is really load-bearing.
The **template-law audit** asks whether repeated revision families are discovery or ceremony.
Claude's bundle also supplied family-level summaries and candidate minimal sets.
That made a deeper omission visible: the archive has mostly been speaking as if the answer to compression is “find the smallest text that still works.”

But the archive does not contain one kind of thing.
Some surfaces behave like constitutional directives or public rules.
Some behave more like worked exemplars or local demonstrations of the move class.
Some behave like challenge probes, sham tests, or admissibility rubrics that keep the other two honest.
When these roles are fused, “minimal archive” claims become hard to read.
A stripped core may fail because the rules were too weak, because no exemplars anchored the style of application, or because the judged replay lacked the challenge surface that would reveal a false positive.

Claude's family consolidation notes point in exactly this direction.
The family summaries already treat some member documents as general law, some as exemplar pressure, and some as narrow reference or challenge material.
Taking that seriously means DelayBasin should not only ask what to shrink.
It should ask how to preserve a minimal **runtime triplet** whose parts do different jobs.

## External pressure from current research

Several current research lines sharpen this split.

1. **Prompt engineering needs explicit documentation and evaluation surfaces.**
   Prompt Cards argues that prompts are complex multi-part objects whose intent, contextualization, and evaluation practices should be documented explicitly rather than left implicit. That pressures DelayBasin to preserve not just a support core but the role-separation inside that support core. ([`REF-0288`](../00-meta/bibliography.md))

2. **Many-shot adaptation is real but configuration-sensitive.**
   Test-Time Adaptation via Many-Shot Prompting treats demonstrations as input-space updates and shows that benefits depend strongly on ordering, selection policy, and task type; open-ended generation often benefits less than structured tasks. That pressures DelayBasin not to treat “add examples” as a generic answer, and to separate constitutional rules from exemplar banks whose effect depends on selection policy. ([`REF-0289`](../00-meta/bibliography.md))

3. **Exemplar choice is itself a budgeted optimization problem.**
   CASE shows that exemplar selection is essential under context budgets and can be improved greatly without brute-force evaluation. That pressures DelayBasin to treat exemplar banks as a distinct design object rather than as accidental leftovers from previous revisions. ([`REF-0290`](../00-meta/bibliography.md))

4. **Instructions, examples, and their combination do different work across turns.**
   Show and Tell reports that instruction-based prompts maintain compression discipline across expansion better than examples alone, while combined instruction+example prompting works best initially. That is direct pressure for a core/exemplar split: instructions and demonstrations are not interchangeable carriers. ([`REF-0291`](../00-meta/bibliography.md))

5. **Real context learning is much harder than easy replay makes it look.**
   CL-bench shows that tasks requiring models to genuinely learn new knowledge, rules, or procedures from context remain difficult for frontier models, with average success around 17.2% and the best model only 23.7%. That pressures DelayBasin not to accept easy continuation as evidence that a reduced runtime really preserves the needed law. A challenge suite matters. ([`REF-0292`](../00-meta/bibliography.md))

6. **Verification can become circular if the test is derived from the same object being judged.**
   ConVerTest frames this as “verify the verifier” and warns that tests generated from the implementation under test can merely mirror its current logic. That pressures DelayBasin to keep challenge suites at least partially independent from the support object they judge. ([`REF-0293`](../00-meta/bibliography.md))

## Working synthesis

A useful current synthesis is:

> DelayBasin may work better when any serious compression, self-sufficiency, or family-consolidation move preserves an explicit **runtime triplet / core-exemplars split / challenge-suite packet** naming the **constitutional core** (rules, contracts, stable ids, and normative boundaries), the **exemplar bank** (the smallest worked examples or family exemplars thought to teach style of application), the **challenge suite** (shams, canaries, admissibility rubrics, and failure probes), the **selection policy under budget** for exemplars or challenges, and the **shrink / reinflate / quarantine consequence** if one part proves to be doing hidden work.

This is strong enough for canon as a design object.
It is not yet strong enough to claim that DelayBasin already knows the uniquely correct triplet, nor that every future revision should preserve all three parts in equal weight, nor that a tiny triplet already beats the full archive across model families.

## Runtime triplet vs archive self-sufficiency probe vs template-law audit vs sufficiency witness

These objects are adjacent but not identical.

- A **runtime triplet / core-exemplars split / challenge-suite packet** names the internal decomposition of a candidate minimal archive runtime.
- An **archive self-sufficiency probe** asks whether a bounded archive object is enough at all.
- A **template-law audit / family-compression frontier / anti-ceremony test** asks whether repeated form is discovering reusable structure or merely manufacturing admissible-looking family members.
- A **sufficiency witness / replay capsule** asks whether one reduced packet re-enters faithfully under named conditions.

In practice, the self-sufficiency probe asks *whether* a bounded runtime exists.
The runtime triplet asks *what kind of bounded object* that runtime should be.
The template-law audit asks *which repeated family traces belong in the core, which belong as exemplars, and which should shrink away*.
The sufficiency witness is the local replay test that checks one candidate reduced object.

## Countermodels / probes

1. **Core-only countermodel**
   - The archive may not need exemplar banks or challenge suites; perhaps constitutional rules alone are enough.
   - Probe: compare core-only replay against core+exemplars and core+challenge variants under the same judged continuation family.

2. **Examples-are-ballast countermodel**
   - Exemplars may mostly duplicate what the rules already say.
   - Probe: hold the core and challenge suite fixed while ablating exemplars or replacing them with family summaries.

3. **Challenge-suite bureaucracy countermodel**
   - A runtime triplet may smuggle in evaluation theater and rebuild archive bulk under another name.
   - Probe: require each challenge to name the confound it controls and the decision it changes; challenges that change nothing should compress or disappear.

4. **Prestige-through-structure countermodel**
   - The triplet decomposition may only feel principled because it sounds like software or systems design.
   - Probe: ask whether the split changes what DelayBasin actually shrinks, preserves, or quarantines compared with a plain self-sufficiency probe.

5. **False-success replay countermodel**
   - A reduced runtime may appear successful on easy continuations while failing on the archive's real hard cases.
   - Probe: keep a compact challenge suite with sham tasks, alien-noun checks, and at least one continuation that requires learning from the supplied context rather than generic DelayBasin imitation.

## Transformer-facing implication

The strongest transformer-facing implication is that a long-horizon archive may not reduce to one monolithic prompt.
It may reduce more naturally to a small **external runtime** with distinct functional parts:
- a **constitutional core** that acts like the normative program,
- a small **exemplar bank** that shapes application style or local induction,
- and a **challenge suite** that prevents false positives and circular self-certification.

Current research already pressures each side of that picture.
Prompt engineering increasingly looks like structured program design and documentation.
Demonstrations act like input-space updates but are sensitive to ordering, selection, and task structure.
And verification needs partially independent rubrics or challenges when the system under test can otherwise teach the verifier what to accept.

DelayBasin has not yet earned the stronger claim that it already possesses a tiny portable runtime triplet.
What it has earned is a stricter recursive rule:
when shrinking the archive or taking Claude's consolidation pressure seriously, separate **core, exemplars, and challenges** explicitly so compression results say something interpretable about how transformers are actually being steered and checked.
