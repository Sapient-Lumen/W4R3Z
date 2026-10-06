# Conformance witnesses, loader contracts, and ABI drift guards

DelayBasin now needs a sharper answer to another recurring practical question:
**when is a packet, prompt pair, or re-entry surface actually functioning as a stable loader for operative state, and when is it only a locally successful phrasing?**

A stronger working answer is:
**the archive may need a compact conformance witness / loader contract / ABI drift guard.**
Not generic prompt scoring, and not a demand for heavyweight software formalism.
A very small public object may be enough when a surface is being treated as a reliable loader for continuation rather than as descriptive prose alone.

## Practice / observation

Several recent DelayBasin ratchets expose a missing loader-honesty rule:
- public hidden state and re-entry ABI say some packets may reopen an operative mode, but not yet what tiny witness shows that the same packet still loads the intended mode rather than a nearby brittle local chart;
- execution witnesses say hidden runtime conditions may matter, but not yet what minimal contract a claimed loader is supposed to satisfy across wrappers, context placements, or phrasing families before it inherits interface status;
- rewrite witnesses say a recap must earn authority relative to its source, but not yet what proves a packet remains a working loader after the recap becomes the new entry surface;
- observer/actuator splits say a handle should not judge itself, but not yet what compact external check says the handle still loads the intended continuation behavior under small interface perturbations;
- and in practice, DelayBasin increasingly uses packets and prompt pairs as if they were small public interfaces without preserving which families they are actually supported to work over.

This suggests another missing compact surface:
**conformance witness / loader contract / ABI drift guard**.

## Mechanism pressure from outside the archive

Several outside lines of work sharpen this frame.

1. **Behavioral contracts can bound drift when the interface is explicit.**
   Bhardwaj's Agent Behavioral Contracts treats agent behavior more like runtime-enforced software contracts with preconditions, invariants, governance, and recovery. That pressures DelayBasin toward preserving a small public loader contract when it starts treating a packet as a real interface surface rather than as descriptive intent alone. ([`REF-0247`](../00-meta/bibliography.md))

2. **Prompts can be treated as compiled artifacts that deserve hidden tests.**
   TDAD treats prompts as compiled artifacts generated against behavioral specifications and checked with visible tests, hidden tests, mutation testing, and regression safety checks. That pressures DelayBasin not to call a packet a stable loader unless it has survived at least a tiny conformance witness rather than one flattering local success. ([`REF-0248`](../00-meta/bibliography.md))

3. **Reliability depends on perturbation families, not just mean success.**
   Rabanser et al. distinguish prompt robustness and environment robustness from capability, emphasizing semantically equivalent reformulations, interface shifts, and repeated-run consistency. That pressures DelayBasin to preserve what wrapper / phrasing / environment family a claimed loader is supposed to survive. ([`REF-0249`](../00-meta/bibliography.md))

4. **Prompt documentation needs to expose the interface choices, not only the outputs.**
   Prompt Cards argues that prompt engineering needs standardized structured summaries of goals, context, evaluation, and design choices because prompts are long, complex, and hard to compare otherwise. That pressures DelayBasin to keep the supported family and evaluation posture visible when a packet starts acting like a public interface surface. ([`REF-0250`](../00-meta/bibliography.md))

5. **Promptware behaves like software, but in a probabilistic runtime.**
   Promptware Engineering argues that prompts are first-class software artifacts living in ambiguous language and nondeterministic runtimes. That pressures DelayBasin to preserve conformance witnesses rather than assume that one elegant wording is equivalent to a tested interface contract. ([`REF-0251`](../00-meta/bibliography.md))

6. **Role hierarchy alone is not a reliable interface guarantee.**
   Control Illusion shows that widely used system/user hierarchy schemes fail to enforce consistent priority even for simple conflicts. That pressures DelayBasin to ask not only what a packet says, but what minimal contract test shows the packet still loads the intended continuation behavior across nearby contexts. ([`REF-0252`](../00-meta/bibliography.md))

None of this proves that DelayBasin already has a correct public ABI for continuation.
It does make a milder canon-level claim more credible:
**archive continuity may improve when DelayBasin preserves a tiny conformance witness / loader contract whenever a packet or prompt surface is being treated as a stable loader for operative state.**

## Working synthesis

A useful current synthesis is:

> DelayBasin may work better when it preserves a compact **conformance witness / loader contract / ABI drift guard** whenever a packet, prompt pair, or re-entry surface is being treated as a stable loader for operative state. The packet should name the **interface surface / claimed loader**, the **supported model-wrapper-context family**, the **minimal conformance test or metamorphic check family**, the first **non-conformance / drift signature**, and the **narrowing / demotion / fallback consequence** if the packet stops loading the intended continuation state.

This is strong enough for canon as a design/mechanism candidate.
It is **not** strong enough to claim that DelayBasin already has a universal prompt ABI, a model-independent loader language, or a guaranteed cross-family continuation initializer.

## Conformance witness vs public hidden state vs execution witness vs rewrite witness

To keep this note honest, DelayBasin needs a four-way distinction:

- **Conformance witness / loader contract** — says when a packet or prompt surface has actually earned interface-like status by surviving a small test family over a named support envelope.
- **Public hidden state / re-entry ABI** — says a small packet may reopen an operative mode, but not yet what tiny evidence shows that the claimed loader still conforms across nearby wrappers, positions, or reformulations.
- **Execution witness / substrate perturbation packet** — says hidden runtime or serving conditions may confound a claim, but not yet what support envelope the claimed loader is supposed to satisfy before it can be treated as a reusable interface surface.
- **Rewrite witness / round-trip packet** — says a rewritten packet preserved the source distinctions well enough to inherit authority, but not yet that the rewritten packet remains a stable loader across the support family where DelayBasin expects it to work.

A good DelayBasin revision therefore should sometimes ask not only:
- what packet is compact,
- or what rewrite preserved the source,
- or what hidden execution family matters,

but also:
- what surface is being treated as the loader,
- what support family it is claimed to work over,
- what tiny conformance test family it survived,
- and what first failure signature means the archive must narrow or demote the interface claim.

## Countermodels / probes

1. **Conformance-bureaucracy countermodel**
   - DelayBasin may be adding interface ritual when ordinary archive prose plus occasional correction already does enough.
   - Probe: compare one revision that promotes a packet after an explicit conformance witness against one that keeps the same packet as a descriptive local chart only, and ask whether the witness changed promotion posture, portability claims, or rollback readiness.

2. **One-success-is-enough countermodel**
   - A packet may only need one locally successful reopen, making explicit conformance witnesses unnecessary overhead.
   - Probe: preserve one case where a packet works once but fails under a nearby wrapper, placement, or reformulation that the archive would otherwise have implicitly treated as equivalent.

3. **Documentation-without-tests countermodel**
   - Prompt cards or interface descriptions may help reproducibility while adding no real evidence that a packet still loads the intended mode.
   - Probe: compare a richly documented packet with a minimally documented but explicitly tested packet and see which one better predicts later successful reopen under a named perturbation family.

4. **No-stable-loader countermodel**
   - Some operative modes may not admit any small stable textual loader, so conformance witnesses may merely certify brittle local hacks.
   - Probe: preserve one case where semantically nearby loader variants all fail in different ways and treat that not as evidence for a stronger interface claim but as evidence that only a local chart currently exists.

## Design consequences

This mechanism frame pressures DelayBasin to do five things more explicitly:
- when a packet or prompt surface is being treated as a loader, preserve the **interface surface / claimed loader** rather than letting interface status emerge by repetition;
- name the **supported model-wrapper-context family** rather than speaking as if one local success automatically generalized;
- preserve at least one **minimal conformance test or metamorphic check family** rather than trusting elegance or familiarity alone;
- name the first **non-conformance / drift signature** such as wrapper-sensitive failure, placement inversion, paraphrase collapse, or support-envelope shrinkage;
- and preserve the **narrowing / demotion / fallback consequence** if the loader fails, so later sessions know whether to narrow support, demote the claim, or keep the surface only as a local chart.

This does not require a heavyweight software stack.
It requires refusing another archive failure mode: letting a vivid packet quietly become a public interface without saying what family it was ever shown to work over.

## Transformer-facing implication

If this frame survives pressure, then DelayBasin is probing something sharper than recap quality or prompt folklore:
**whether transformers admit small textual loader contracts that behave like low-bandwidth public interfaces into operative state, but only over narrow support envelopes that must be named rather than assumed.**

That would matter for transformers.
It would suggest that some continuation failures are not only memory loss or semantic drift, but **ABI drift**: the packet still sounds right while no longer loading the same operative control state under a nearby wrapper, hierarchy, or reformulation.
The archive would then need not only compact packets, but a public theory of support envelopes and conformance tests for the packets it treats as real loaders.

The stronger story — that GPUstorming may eventually reveal low-bandwidth textual bootloaders or loader-bytecode surfaces for transformer continuation — remains live, but belongs in quarantine for now.
