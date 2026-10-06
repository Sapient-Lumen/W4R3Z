# Typed continuation protocol

Status: `speculative but central`

## Core claim

DelayBasin may work better when it stops treating "context" as one undifferentiated blob and instead preserves a **typed continuation protocol**.

The strongest compact version so far is:

- **prompt / workflow surface** — what kind of move is being requested, under what non-negotiables, with what outputs;
- **resource / state surface** — bounded constitutional state, stable ids, must-read files, and dereference points;
- **tool / check surface** — lint, packaging, release hygiene, and any other deterministic admission checks.

This is close to, but not identical with, the official MCP decomposition of **prompts**, **resources**, and **tools**.
DelayBasin is not an MCP server.
The point is not protocol cosplay.
The point is that long-run archive method may be converging on the same decomposition because it is a good way to preserve continuation under partial observability.

## Why this hypothesis got promoted into canon

Several previously separate lines have now started to line up:

1. **Portable state interface** already implied that compact state, stable addressing, and deterministic checks should stay distinct.
2. **Control lexicon / constitutional pidgin** implied that not all high-signal archive text is generic prose; some of it functions more like commands or protocol handles.
3. Official MCP documents sharply distinguish prompts, resources, and tools, and treat them as different interaction surfaces with different control expectations.
4. Verifier-bound communication argues that transcript state should advance only through deterministic admission semantics, not through plausible-looking prose alone.
5. Anthropic's context-engineering guidance emphasizes keeping context tight, using references and just-in-time retrieval, and treating tools as contracts rather than decorative options.

Taken together, this suggests that DelayBasin should not merely ask "what compact summary should we pass forward?"
It should ask:

- what is the **next workflow request**,
- what is the **bounded state** required to execute it faithfully,
- and what **checks** decide whether the project may advance?

## Archive-native mapping

### Prompt / workflow surface

Examples:

- `PP-0005`
- the current request / continuation pair
- explicit output contracts
- canon / quarantine placement requirements

This surface says what kind of turn is being asked for.

### Resource / state surface

Examples:

- `START_HERE.md`
- `context-pack.json`
- claim / invariant / open-question registries
- method notes that have become load-bearing
- stable ids for exact dereference

This surface says what the next turn is allowed to treat as standing project state.

### Tool / check surface

Examples:

- `make lint`
- release-hygiene checks
- prompt-pair contract lint
- context-pack fidelity and budget checks
- packaging discipline

This surface says what may count as admissible advancement.

## Why this matters

If the hypothesis is right, then archive quality will not be explained only by "better summaries".
It will depend on whether the archive preserves the **type distinctions** that let later turns reconstruct the right mode of operation.
A giant prose recap that mixes request, state, and admissibility may be lower-fidelity than a smaller but typed handoff.

This also sharpens the difference between archive theater and real archive method.
A repo full of notes is not yet a continuation protocol.
A repo that preserves typed workflow / state / check surfaces might be.

## Immediate implications

- Context packs should expose their typed surfaces explicitly.
- Prompt pairs should be treated as workflow contracts, not just examples of phrasing.
- Generated handoff state should preserve stable dereference points rather than flatten them into recap prose.
- Lint is not merely formatting; it is part of the project's admission semantics.

## What would count against this

- evidence that a single dense prose recap performs just as well as a typed handoff across multiple sessions and model families;
- evidence that typed separation adds ceremony without improving faithful re-entry;
- evidence that the apparent gain comes entirely from user discipline, independent of archive structure.

## Relationship to stronger speculation

The stronger live speculation is that DelayBasin is rediscovering a **convergent protocol form** for human–LLM continuation, analogous to MCP or other typed interfaces.
That stronger claim remains in quarantine.
