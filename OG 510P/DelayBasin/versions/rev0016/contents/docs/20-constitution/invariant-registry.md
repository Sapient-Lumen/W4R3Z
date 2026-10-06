# Invariant registry

- `INV-0001` — Every substantial claim must carry a status orientation:
  `observed`, `inferred`, `speculative`, `adversarial-countermodel`, or `quarantined-wild-speculation`.

- `INV-0002` — Every new doc must be linked from `docs/README.md`.

- `INV-0003` — Every new prompt pair must get a stable `PP-####` id and registry entry.

- `INV-0004` — The archive must preserve at least one explicit disagreement surface.

- `INV-0005` — Each revision should add at least one ratchet:
  a guardrail, a clarified distinction, a refined open question, a new prompt pair, or a new canonical surface.

- `INV-0006` — External research may sharpen the archive, but it must not silently replace archive-internal observations.

- `INV-0007` — Release artifacts must remain small enough to hand off and inspect.

- `INV-0008` — The archive must not pretend repo hygiene is causal unless it can point to a plausible mechanism or observed effect.

- `INV-0009` — Risky transformer-facing speculation is allowed and encouraged, but if its status is too weak for canon it must enter quarantine rather than leak upward implicitly.

- `INV-0010` — A bounded constitutional state should preserve the current load-bearing control lexicon needed for faithful re-entry, not just generic summary prose.

- `INV-0011` — Portable state surfaces must preserve structural fidelity: bounded state, stable ids, and generated context-pack entries may not silently degrade through formatting accidents.

- `INV-0012` — If a handoff surface claims to be portable project state, it should preserve typed continuation structure where applicable: workflow request, bounded state/resources, and deterministic checks/tools should not be silently collapsed together.

- `INV-0013` — If the archive relies on local control language, certified core terms and provisional/private handles must remain distinguishable; provisional terms may not silently masquerade as certified canon.
- `INV-0014` — If the archive relies on certified move classes, revisions should be able to name which move classes they instantiated; otherwise procedural admission collapses back into vibe.
- `INV-0015` — If a revision promotes or demotes canon-level trust, the archive should preserve the promotion contract or demotion reason explicitly enough that later sessions can tell why the status changed and what could reverse it.

- `INV-0016` — If a canon-level claim depends materially on fresh external literature or fast-moving ecosystem state, the archive should either preserve a compact temporal-validity / decay-watch posture for it or keep it below canon.


- `INV-0017` — If the archive claims a recovery route back to legitimate continuation, it should preserve a small recovery kernel and an explicit recovery move rather than treating recovery as a vague promise.


- `INV-0018` — If the archive claims a revision counted as legitimate progress, it should preserve a compact revision receipt naming move classes, status changes, refs used, and checks passed rather than leaving admissibility implicit in prose alone.


- `INV-0019` — If a substantial revision had a real nearby rejected alternative, the archive should preserve a compact counterfactual shadow rather than letting the accepted move erase the local decision boundary.
