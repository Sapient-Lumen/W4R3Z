# Research notes — rev0146

Research was used as design input, not as authority over Lacuna’s invariants.

## 1. Gwern: retcon planning

Gwern’s June 2, 2026 essay proposes periodically replacing hidden state with a new abductive explanation of player-observed events, rolling candidates forward, scoring them, compressing a winner, and discarding the detailed future. It explicitly warns about “rubber reality” and calls for a commitment budget as hidden facts generate visible consequences.

Lacuna adopts delayed commitment, forgetting of speculative rollouts, and consequence-sensitive revision. It rejects the single “canon paragraph” and single winning state card as insufficiently typed.

Source: https://gwern.net/blog/2026/llm-retcon

## 2. MCP: resources, prompts, and tools are distinct surfaces

The stable Model Context Protocol specification separates server-provided resources, prompts, and tools. That decomposition maps cleanly onto Lacuna:

- context projection as a resource;
- turn packet as a prompt/workflow template;
- turn commit as a mutation tool.

The specification also emphasizes explicit user control and clear tool invocation. Rev0146 therefore keeps privileged director context opt-in and returns structured refusal rather than silently widening access.

Sources:

- https://modelcontextprotocol.io/specification/2025-11-25
- https://modelcontextprotocol.io/specification/2025-11-25/server/tools

Rev0146 does not ship an MCP server. It establishes protocol-shaped local commands first so an MCP adapter can remain thin.

## 3. IVIE and validated incremental world generation

IVIE describes a neuro-symbolic pipeline in which LLM creativity is grounded by symbolic validation while incrementally generating playable interactive-fiction worlds. The reported remaining failures—constraints that occasionally slip through and structurally impossible goals—support keeping model output on the proposal side of a validator.

Source: https://arxiv.org/abs/2606.13348

Lacuna differs by making epistemic plurality and perspective custody central rather than treating the world as one validated state.

## 4. World-state transformations

Work on world-state transformations for neuro-symbolic interactive storytelling explores free-text input triggering validated, pre-programmed state transitions. This supports a plan/diff/validate/apply boundary: expressive language is accepted at the edge, while state transition remains typed.

Source: https://arxiv.org/abs/2605.24719

## 5. Orchestrated Reality / PDVA

“Orchestrated Reality” frames an LLM-driven world as a parameterized-action POMDP and proposes Plan-Diff-Validate-Apply over content-hashed JSON deltas. This is close to Lacuna’s turn adapter structurally.

Source: https://arxiv.org/abs/2606.16014

The important divergence is ontological: one canonical JSON tree is not enough for testimony, private belief, unreliable narrators, or multiple surviving hidden explanations. Lacuna’s delta applies to an epistemic ledger, not only a world snapshot.

## 6. Agentic world modeling

Recent world-model framing emphasizes state-transition dynamics, action selection, and look-ahead planning. It is useful for future counterfactual probes, but narrative systems must add audience-specific observation functions and distinguish model belief from represented-world truth.

Source: https://arxiv.org/abs/2604.22748

## Design conclusions taken this revision

1. Keep the model call outside Lacuna; make the local protocol complete first.
2. Expose context, workflow, and mutation as separate surfaces.
3. Label privileged and perspective data structurally.
4. Validate deltas, not prose confidence.
5. Preserve narration provenance without making prose storage an accidental kernel responsibility.
6. Make IDs easy for models through sequential aliases rather than asking a model to compute hashes.
7. Treat a campaign as a human entrance, not a new truth layer.

## 7. Belief revision and dynamic epistemic action

Classical belief-revision work distinguishes a logically closed belief set from a finite belief base. Lacuna is intentionally closer to a provenance-bearing belief base: it stores explicit assertions and does not silently infer every logical consequence. That makes future revision inspectable, but means logical closure and contradiction relations must be introduced explicitly rather than assumed.

Dynamic epistemic logic contributes a second distinction: an action may change the world, change what an agent observes, and change what agents believe about one another in different ways. Candidate worlds in Lacuna are currently planner hypotheses; they are **not** yet per-agent accessibility relations or a complete nested-belief model.

Relevant sources:

- https://plato.stanford.edu/entries/logic-belief-revision/
- https://www.ijcai.org/Proceedings/13/Papers/178.pdf
- https://www.ijcai.org/proceedings/2019/0071.pdf
- https://dl.acm.org/doi/10.5555/3505378.3505382

Design consequence: a future action record should separate its ontic delta from its observation policy. “The door opened,” “Mira saw it open,” and “Jon believes Mira saw it” must remain different updates. Lacuna should not call its global candidate-world bank an epistemic accessibility graph until it actually represents agent-relative alternatives and nested belief.
