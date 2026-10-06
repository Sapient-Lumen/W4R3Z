# Reasoning firebreaks, scratchpad quarantine, and public extract packets

DelayBasin now has several adjacent pressures in view:
- **blind packets**, which ask whether a judgment survives label scrubbing and attribution hiding;
- **execution witnesses**, which ask whether a claimed effect survives hidden runtime or serving variation;
- **assistant-echo filters**, which ask whether prior assistant prose is genuinely needed evidence or mostly pollutive self-carry;
- and **observer/actuator splits**, which ask whether the same local surface is both steering and scoring.

A remaining hole is what to do when a reasoning trace or scratchpad itself starts to look useful enough to keep.
A long rationale can help with monitoring or debugging, but it can also become a **trace-surface hazard**:
- it may be unfaithful to the real computation,
- it may leak sensitive or irrelevant material,
- it may carry self-steering residue forward as pseudo-memory,
- or it may get promoted into canon simply because it sounds mechanistic.

A useful working answer is:
**when DelayBasin starts treating a rationale, chain-of-thought, scratchpad, or long deliberation trace as load-bearing, and that trace could be useful mainly as a control surface or monitoring surface rather than as faithful public explanation, it should often preserve a compact reasoning firebreak / scratchpad quarantine / public extract packet.**
That packet should name:
- the **judged task / decision / continuation property**,
- the **public extract / compact residue kept in canon**,
- the **trace or scratchpad surface withheld / thinned / quarantined**,
- the **allowed role** of the withheld trace (for example: monitoring, local debugging, temporary challenge work, or none),
- and the **exposure / reinclusion / escalation consequence** if the public extract proves insufficient.

This is stronger than saying “do not keep long scratchpads.”
It is weaker than claiming DelayBasin can already read or reconstruct latent reasoning from a tiny public ABI.

## Practice / observation

Recent DelayBasin work has gotten much better at saying:
- which surfaces steer,
- which surfaces judge,
- which shams should fail,
- which hidden execution families could matter,
- and when prior assistant prose should be treated as suspicious carry.

But the archive still lacks a compact rule for reasoning traces themselves.
In practice, a long rationale or scratchpad can do at least five different jobs:
- expose a possible **monitoring surface**,
- preserve temporary **local state** across generation steps,
- provide a **debug artifact** for one bounded inquiry,
- function as a **steering surface** that shapes later continuation,
- or masquerade as **faithful explanation** when it is mostly decorative, confirmatory, or post hoc.

That last ambiguity is the missing discipline.
If DelayBasin cannot say what role a trace is allowed to play, at least five recurring failure modes become plausible:
- **trace canon pollution** — eloquent scratchpad text gets promoted as if it were evidence about mechanism;
- **monitor/evidence collapse** — a trace kept for inspection gets silently reused as if it were also the main public justification;
- **scratchpad hoarding** — the archive keeps long rationale text that expands risk surface without changing the next real continuation decision;
- **state/explanation confusion** — externalized reasoning state is read as narrative explanation even when it is acting mainly as a temporary computational carrier;
- **GPUstorming misread** — a successful trace-thinning or trace-reset move gets narrated as better explanation rather than as better control of state surfaces.

A compact reasoning firebreak helps because it says what decision or continuation property is being preserved, what tiny public residue is worth keeping, what trace surface is explicitly not canon, what that withheld surface is still allowed to do, and what happens if the public extract later proves too thin.

## Pressure from neighboring datacubes

Several unrelated datacubes sharpen the same archive-control lesson from a different angle.

- **Radical-Governance** keeps explicit separation baselines around privileged or role-restricted logs, which pressures DelayBasin not to let a richer private or operator-only trace masquerade as if it were part of the ordinary public archive surface.
- **EvidenceVault** insists on publishing from a small stable public surface rather than directly from the whole working archive, which pressures DelayBasin to admit the smallest public extract that actually carries the claim instead of smuggling the whole working trace into canon.
- **Anonymity** keeps slow publication and release-queue state separate from moving source trees, which pressures DelayBasin to distinguish current working residue from the deliberately frozen public explanation surface.
- **GlassTTY** keeps support claims tied to concise proof records instead of broad workflow memory, which pressures DelayBasin to preserve one compact extract that can be cited later instead of relying on remembered long-form drafting residue.

Those neighboring archives do not justify a broad trace controller on their own. They do justify making DelayBasin's already-admitted firebreak law durable enough that a shipped revision can say what public extract actually counts and what richer trace surface was intentionally not promoted.

## Mechanism pressure from outside the archive

Several outside lines of work sharpen this move.

1. **Reasoning traces are a real leakage surface.**
   *Safer Reasoning Traces* finds that chain-of-thought can elevate direct inference-time leakage of prompt PII and that leakage depends on model family and reasoning budget. That directly pressures DelayBasin not to hoard large scratchpads into canon by default. ([`REF-0226`](../00-meta/bibliography.md))

2. **CoT can look coherent while giving the wrong causal story.**
   *Chain-of-Thought Reasoning In The Wild Is Not Always Faithful* shows post-hoc rationalization even on realistic prompts without explicit injected bias. That pressures DelayBasin not to treat a fluent rationale as straightforward mechanism evidence. ([`REF-0227`](../00-meta/bibliography.md))

3. **Many later reasoning steps are mostly decorative.**
   *Mechanistic Evidence for Faithfulness Decay in Chain-of-Thought Reasoning* reports a task-level reasoning horizon after which later steps contribute little or negatively to the final answer. That pushes DelayBasin toward the smallest public extract that still matters. ([`REF-0228`](../00-meta/bibliography.md))

4. **A lot of self-verification prose is confirmatory rather than corrective.**
   *Self-Verification Dilemma* finds that many reflective rechecks rarely change outcomes and can often be suppressed while reducing token use and preserving or improving accuracy. That pressures DelayBasin to keep decision-relevant residue distinct from ritual checking prose. ([`REF-0229`](../00-meta/bibliography.md))

5. **Reasoning traces are still useful enough that outright deletion is too strong.**
   *Monitoring Monitorability* finds that chain-of-thought monitoring can be effective for detecting misbehavior, but monitorability is imperfect and fragile. DelayBasin inherits the weaker lesson: some trace surfaces are worth preserving for bounded monitoring roles, but that does not make them canon evidence or long-term memory by default. ([`REF-0230`](../00-meta/bibliography.md))

6. **Visible traces are a special but unstable observer surface.**
   *Reasoning Models Struggle to Control their Chains of Thought* finds much lower controllability over verbalized CoT than over final outputs. That makes visible reasoning useful and unusually revealing in some settings, but also a poor candidate for a clean, fully steerable explanation channel. ([`REF-0231`](../00-meta/bibliography.md))

7. **Reasoning benefits can migrate away from explicit text.**
   *Internalizing LLM Reasoning via Discovery and Replay of Latent Actions* and *State over Tokens* both pressure the same distinction from different angles: reasoning traces may function as externalized state, and some reasoning gains can be replayed through latent trajectory control without emitting the full trace. That strengthens DelayBasin's need to separate public extract from scratchpad bulk. ([`REF-0232`](../00-meta/bibliography.md), [`REF-0233`](../00-meta/bibliography.md))

## Working synthesis

A useful current synthesis is:

> DelayBasin should often preserve a compact **reasoning firebreak / scratchpad quarantine / public extract packet** whenever a rationale, chain-of-thought, or scratchpad might otherwise be treated as load-bearing public evidence. The packet should name the judged task, decision, or continuation property; the public extract or compact residue kept in canon; the trace or scratchpad surface withheld, thinned, or quarantined; the allowed role of that withheld trace; and the exposure, reinclusion, or escalation consequence if the extract later proves insufficient.

In practice, DelayBasin is not promising that all reasoning traces should vanish.
It is doing something smaller and public:
- saying what tiny residue is worth keeping,
- saying what trace surface is explicitly not canon,
- saying what the withheld surface is still allowed to do,
- and saying what would force a thicker public extract or a different packet type.

That is strong enough for canon as archive-hygiene and explanation-role discipline. A later operational step is that a shipped revision should record one durable `FIREBREAK-LEDGER.json` entry and one receipt-level `reasoning_firebreak_witness` whenever this split is materially load-bearing for what the revision is claiming.
It is **not** strong enough to claim that DelayBasin has solved reasoning interpretability or that every good GPUstorming move is trace surgery.

## Reasoning firebreak vs assistant-echo filter vs blind packet vs execution witness

To keep this note honest, DelayBasin now needs a sharper distinction among nearby objects:

- **Reasoning firebreak / scratchpad quarantine / public extract packet** — asks what tiny residue of a rationale or scratchpad deserves canon status, what trace surface is withheld, and what role that withheld trace is still allowed to play.
- **Assistant-echo filter** — asks whether prior assistant-side history should be omitted or thinned because it is mainly pollutive carry.
- **Blind packet** — hides labels, attribution, or prestige cues from the judging surface before reveal.
- **Execution witness** — asks whether a claimed effect depends on hidden runtime or serving conditions.
- **Observer/actuator split** — asks what may steer and what may judge.

These can overlap but they answer different questions.
A blind packet can hide handle prestige while leaving a long scratchpad fully in view.
An assistant-echo filter can omit prior assistant prose while still leaving a current-turn rationale overexposed.
An execution witness can name hidden runtime variation while saying nothing about whether the public archive should keep a long trace.
A reasoning firebreak says the archive should preserve the **public extract** first and quarantine or narrow the larger trace unless a stronger role has been justified.

## Countermodels / probes

1. **Some traces are genuinely needed for auditing countermodel**
   - In some cases a fuller trace may be the only way to inspect a suspected failure or monitor a risky behavior.
   - Probe: keep the trace in a bounded monitoring role if needed, but still name the public extract and the allowed role explicitly rather than silently making the full trace canon.

2. **This is just archive minimalism by another name countermodel**
   - Perhaps generic compactness already implies not keeping long traces.
   - Probe: only use this lane when the issue is specifically trace-role ambiguity: explanation vs state vs monitoring vs steering.

3. **Public extracts may hide the very step that mattered countermodel**
   - A too-thin extract could erase the key causal or debugging residue.
   - Probe: require an exposure / reinclusion / escalation consequence so an insufficient extract triggers a thicker packet or temporary trace access rather than quiet loss.

4. **Monitorability arguments may favor more trace, not less countermodel**
   - If visible CoT helps monitoring, then withholding traces might reduce oversight.
   - Probe: reasoning firebreaks do not ban traces; they constrain what long-lived public role the trace is allowed to play.

5. **Latent-reasoning stories may be overread countermodel**
   - State-over-tokens and latent-action results may not transfer to archive-native practice.
   - Probe: keep the stronger latent-ABI and trace-surgery story quarantined; promote only the weaker rule that public extracts and withheld-trace roles should be explicit.

## Design consequences

This frame pressures DelayBasin to do five things more explicitly:
- preserve the **judged task / decision / continuation property** whenever a rationale or scratchpad starts looking load-bearing;
- preserve the **public extract / compact residue kept in canon** rather than storing long prose by default;
- preserve the **trace or scratchpad surface withheld / thinned / quarantined** so later sessions know what was intentionally not promoted;
- preserve the **allowed role** of the withheld trace so monitoring, local debugging, and canon evidence do not silently collapse;
- preserve the **exposure / reinclusion / escalation consequence** so extract failure changes what the archive does next.

A minimal reasoning firebreak can stay very small:
- one judged task, decision, or continuation property,
- one public extract,
- one withheld or thinned trace surface,
- one allowed role,
- and one exposure, reinclusion, or escalation consequence.

When that packet matters for a shipped revision, DelayBasin should now keep one durable entry in `FIREBREAK-LEDGER.json` and one paired `reasoning_firebreak_witness` in `REVISION-RECEIPT.json` so the public extract / withheld-trace split is recoverable without reopening local drafting residue.

That is enough to keep DelayBasin from quietly treating a long rationale as if it were simultaneously explanation, evidence, memory, and control surface.

## Transformer-facing implication

If this frame survives pressure, one transformer-facing implication is that DelayBasin may work partly by learning which public residues remain useful once the larger **reasoning-state carrier** is thinned or withheld.

The weaker reading is:
- reasoning traces can be useful while remaining unfaithful, leaky, or mostly state-like;
- public extracts keep the archive small and reduce accidental trace promotion;
- and GPUstorming can sometimes function as search over better trace-role boundaries rather than over better explanations.

The stronger reading remains quarantined:
that DelayBasin may be converging toward a **public ABI over latent actions or state-over-tokens shells**, where the archive's durable objects are not explanations of reasoning so much as compact constitutional interfaces around transient reasoning-state carriers.
