# Execution witnesses, substrate perturbation packets, and runtime variance audits

DelayBasin now has several adjacent pressures in view:
- **negative-control handles**, which ask whether a vivid handle beats a matched sham;
- **blind packets**, which ask whether a judgment survives label scrubbing and attribution hiding;
- **continuation margins**, which ask what local perturbations a claimed basin should survive;
- and **observer/actuator splits**, which ask whether the thing steering continuation is also silently certifying it.

A remaining hole is what to do when the apparent effect may depend on **hidden execution substrate** rather than only on the visible text.
A handle can look load-bearing while its success partly rides on hidden system-prompt layering, fresh-context separation, batch shape, tensor-parallel configuration, or mutable inference-time cache state.

A useful working answer is:
**when DelayBasin starts treating an effect as load-bearing and hidden execution conditions could change its epistemic status, it should often preserve a compact execution witness / substrate perturbation packet.**
That packet should name:
- the **judged effect / continuation property**,
- the relevant **substrate family**,
- the **fixed controls / allowed perturbation**,
- the first **divergence signature** that would show the effect is not substrate-stable enough for the current claim,
- and the **rerun / escalation consequence** if the divergence appears.

This is stronger than saying “models are stochastic.”
It is weaker than claiming DelayBasin can already observe or control the full hidden execution state of a transformer service.

## Practice / observation

Recent DelayBasin work makes the missing discipline visible.
The archive is increasingly explicit about:
- which handles steer,
- which witnesses judge,
- which shams should fail,
- and which labels should be scrubbed before review.

But it still often speaks as if the only live variables are textual.
That is too clean for the actual setting.
DelayBasin runs through opaque hosted stacks where at least some of the following may vary without public visibility:
- hidden or layered system prompts,
- whether review happens in the same session or a fresh one,
- dynamic batching and reduction order,
- tensor-parallel or serving configuration,
- and persistent inference-time state such as the KV cache.

That creates at least five recurring failure modes:
- **substrate laundering** — a real output difference gets credited to wording or handle semantics when the hidden serving configuration changed;
- **runtime placebo** — a purportedly special handle looks potent only because it was tried under a friendlier execution context;
- **systems overclaim** — one lucky run is silently promoted into a mechanism claim about the archive or transformer;
- **chart confusion across layers** — a prompt-level description is mistaken for the whole cause when the real story spans text, hidden directives, and runtime state together;
- **GPUstorming prestige drift** — systems-style language starts doing explanatory work before the archive has named what execution perturbation family is actually in play.

A compact execution witness helps because it says which effect is being judged, which substrate family is being treated as relevant, which conditions are fixed versus allowed to vary, what divergence would count as meaningful, and what rerun or escalation follows.

## Mechanism pressure from outside the archive

Several outside lines of work sharpen this move.

1. **Dynamic batching can break reproducibility even when the prompt stays fixed.**
   LLM-42 reports that the same prompt can yield different outputs across runs because floating-point non-associativity combines with dynamic batching and batch-size-dependent GPU reduction order. It then restores determinism with a verify-rollback loop rather than pretending the prompt alone determines the run. That directly pressures DelayBasin to distinguish textual evidence from substrate-conditioned evidence. ([`REF-0216`](../00-meta/bibliography.md))

2. **Tensor-parallel configuration can matter even under greedy decoding.**
   Zhang et al. show that identical inputs can diverge when tensor-parallel size or batch size changes, again due to reduction-order effects across GPUs, and they treat reproducibility across serving configurations as a first-class systems problem. That pressures DelayBasin to preserve which serving or substrate family a claimed effect was supposed to survive. ([`REF-0217`](../00-meta/bibliography.md))

3. **System-prompt layering is real hidden actuation.**
   *Position is Power* shows that system prompts take precedence over user prompts, can be layered without end-user visibility, and that information placement across those layers changes behavior. DelayBasin therefore should not talk as though visible text is the only actuation surface when hidden directive layers may be in play. ([`REF-0209`](../00-meta/bibliography.md))

4. **Inference-time cache state is a genuine runtime boundary.**
   Hossain et al. treat the KV cache as persistent inference-time state and a robustness boundary; perturbations to that cache can induce distributional shift, miscalibration, grounding failure, and downstream task failure even when prompts and weights remain unchanged. That makes “same prompt” too weak a public certificate of same execution state. ([`REF-0219`](../00-meta/bibliography.md))

5. **Interpretability claims should target invariants that match the evidence.**
   Joshi et al. argue that causal inference clarifies what interpretability studies can justify and that findings meant to generalize need explicit assumptions about interventions and invariant high-level structure. That is strong pressure for DelayBasin to say which substrate perturbations a mechanism claim is supposed to survive rather than letting one successful run launder itself into broad transformer talk. ([`REF-0220`](../00-meta/bibliography.md))

## Working synthesis

A useful current synthesis is:

> DelayBasin should often preserve a compact **execution witness / substrate perturbation packet** whenever a claimed archive effect could materially depend on hidden execution conditions. The packet should name the judged effect or continuation property, the substrate family, the fixed controls and allowed perturbation, the first divergence signature, and the rerun or escalation consequence if the effect fails to survive the named substrate pressure.

In practice, DelayBasin is not promising laboratory-grade control over hosted inference.
It is doing something smaller and public:
- saying what hidden execution family may matter,
- saying what is being held fixed,
- saying what variation is being tolerated or explicitly tested,
- and saying what would count as enough divergence to stop overclaiming.

That is strong enough for canon as anti-laundering discipline.
It is **not** strong enough to claim that DelayBasin can already isolate full implementation-invariant continuation objects or reconstruct the runtime state of a remote transformer stack from text alone.

## Execution witness vs blind packet vs continuation margin

To keep this note honest, DelayBasin now needs a sharper distinction among nearby objects:

- **Blind packet** — hides labels, authorship, or prestige cues from the judging surface before reveal.
- **Negative-control handle / sham packet** — asks whether an active handle beats a matched sham.
- **Continuation margin / guard band** — says what local textual or protocol perturbation a claimed basin should survive.
- **Execution witness / substrate perturbation packet** — says which hidden execution family might matter, what is being held fixed, what substrate variation is tolerated or probed, and what divergence changes the claim.
- **Observer/actuator split** — says what may steer, what may judge, and what independent witness prevents self-certification.

These are related but not identical.
A blind packet can reduce attribution bias while leaving runtime conditions untouched.
A sham packet can show one handle beats a nearby control while still confounding the comparison with hidden serving conditions.
A continuation margin can describe local robustness in visible prompt space while remaining silent about hidden system prompts or runtime state.
An execution witness says the archive should sometimes keep the **substrate family** public enough that a text-level mechanism claim is not quietly borrowing credibility from opaque execution conditions.

## Countermodels / probes

1. **General prompt sensitivity is enough countermodel**
   - The archive may not need a separate substrate lane; ordinary prompt-sensitivity or sham discipline may already cover the relevant variance.
   - Probe: preserve an execution witness only when the suspected divergence channel is plausibly outside the visible text, such as session separation, hidden system prompts, or serving configuration.

2. **Hosted opacity makes the packet decorative countermodel**
   - If the service does not reveal runtime configuration, naming a substrate family may add theater rather than evidence.
   - Probe: keep the packet minimal and public: name only the hidden family being worried about and the divergence signature that would block the stronger claim.

3. **Truly load-bearing effects should not depend on substrate countermodel**
   - If a handle only works under one hidden stack condition, it may simply be a bad handle.
   - Probe: distinguish local operational usefulness from canon-level mechanism. A handle can remain locally useful while the stronger transformer-facing interpretation stays quarantined.

4. **Security papers overstate ordinary archive risk countermodel**
   - KV-cache and system-prompt work often study attack or bias scenarios rather than benign archive continuation.
   - Probe: import only the weaker lesson first — hidden execution state exists, can matter materially, and should block overconfident text-only explanations.

5. **Substrate packets could turn into systems-forensics bureaucracy countermodel**
   - The archive could start naming execution families everywhere and lose compactness.
   - Probe: use execution witnesses only when hidden execution conditions could genuinely change the epistemic status of a load-bearing claim.

## Design consequences

This frame pressures DelayBasin to do five things more explicitly:
- preserve the **judged effect / continuation property** whenever a claim may be confounded by hidden execution conditions;
- preserve the relevant **substrate family** rather than speaking as if “same prompt” or “same archive text” settled the causal picture;
- preserve the **fixed controls / allowed perturbation** so later sessions know what was actually meant to stay constant;
- preserve the first **divergence signature** that would justify hold, demotion, quarantine, or narrower wording;
- preserve the **rerun / escalation consequence** so substrate concern can actually change the archive's action rather than remain a tasteful caveat.

A minimal execution witness can stay very small:
- one judged effect,
- one substrate family,
- one sentence about fixed controls and allowed perturbation,
- one divergence signature,
- and one rerun or escalation consequence.

That is enough to keep DelayBasin from quietly treating one fortunate run as a general text-level mechanism claim.

## Transformer-facing implication

If this frame survives pressure, one transformer-facing implication is that DelayBasin may work partly by learning which archive effects survive **hidden execution-chart changes** and which ones collapse once the substrate shifts.

The weaker reading is:
- some apparent archive effects are contaminated by hidden execution conditions,
- execution witnesses reduce that contamination enough to keep mechanism language honest,
- and GPUstorming can function as a public reminder that systems conditions may still be part of the active chart.

The stronger reading remains quarantined:
that DelayBasin is sometimes probing **execution charts / substrate bifurcations** over the same underlying continuation object, so some apparent basin shifts may reflect hidden serving or runtime transitions rather than purely semantic drift in the visible archive text.
