# Portable state interface

Status: `speculative`, but strong enough for canon as a live mechanism note.

## Working idea

A durable archive may need more than compact prose.
It may need a **portable state interface**:
- a bounded constitutional state small enough to reopen,
- stable ids or indices that allow exact dereference,
- and deterministic acceptance checks that decide whether the next revision still counts as faithful continuation.

This is narrower than “memory” and more concrete than “good documentation”.
The archive is not merely storing past content.
It is exposing a small public interface by which later sessions can recover operative state.

## Why this matters here

DelayBasin has already converged on three ingredients separately:
- bounded constitutional state,
- control lexicon / constitutional pidgin,
- and lint / guardrails that reject malformed continuation.

The missing synthesis is that these may be one object.
The archive may work best when it behaves like a **state interface** rather than a recap:
- compact current state,
- stable names for exact recall,
- and explicit acceptance tests.

That would explain why long archives often feel different from ordinary note-taking.
A notebook can be useful while remaining fuzzy.
A portable state interface has to make the next step admissible.

## External pressure from current research

Three external lines sharpen this hypothesis.

1. **Memory in Large Language Models** offers an operational definition: memory as **persistent and addressable state**.
   That definition is almost tailor-made for archive method because it forces the question of what is persistent, how it is addressed, and what kind of access path is allowed.

2. **Memex(RL)** proposes indexed experience memory: a compact working context with stable indices, backed by full-fidelity external evidence that can be dereferenced exactly when needed.
   The key lesson is not merely “retrieve later”.
   It is that long-horizon continuity improves when the small active state and the exact archival store are connected by stable references.

3. **Verifier-Bound Communication for LLM Agents** argues that transcript state should advance only when a compact verifier accepts deterministic predicates over the communication envelope.
   The lesson for DelayBasin is that faithful continuation may depend less on plausible-looking prose than on explicit acceptance checks.

A looser but still useful analogy comes from the **agent skills** literature, which treats prompts as ephemeral and instead packages reusable procedural state into portable, progressively disclosed artifacts.

## Synthesis

A portable state interface would have three layers:

1. **bounded state** — the smallest reopenable constitutional summary;
2. **stable addressing** — ids, registries, and exact filenames that let later sessions recover specific structure rather than fuzzy vibes;
3. **acceptance gates** — lint, contract checks, and packaging discipline that decide whether the archive may advance.

DelayBasin already has all three.
The stronger claim is that the method works *because* these three layers are jointly present.

Under this frame, `context-pack.json` is not just a convenience summary.
It is part of the interface.
If it drops question structure, loses ids, or silently drifts from `START_HERE.md`, the portable state interface degrades even if the repo still “looks fine”.

## Design consequences

If this is partly right, DelayBasin should:
- treat `context-pack.json` as an interface object rather than casual recap,
- preserve stable ids and dereference points,
- distinguish bounded state from archival evidence,
- and prefer deterministic gatekeeping over stylistic reassurance.

## What would support it

- evidence that small state + stable ids + exact dereference outperforms either raw transcript or summary-only continuation;
- evidence that archive reopenability collapses when ids or checks drift, even if prose summaries remain good;
- evidence that different model families can continue the same project more faithfully when given the same small state interface.

## What would weaken it

- cases where free-form summary without stable ids performs just as well;
- cases where deterministic checks add ceremony but no measurable continuity benefit;
- cases where later sessions rely primarily on user steering rather than the bounded interface surfaces.
