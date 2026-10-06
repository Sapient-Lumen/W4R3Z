# Exosomatic delay-embedding

Status: `speculative`, but mechanistically serious.

## Hypothesis

The archive functions as an **exosomatic delay-embedding**:
an externalized coordinate history that helps reconstruct the project’s latent state after the system loses direct access to prior internal trajectory.

## Why this frame is attractive

If transformer attention can operate as an adaptive delay-embedding mechanism under partial observability, then a long-lived archive may be doing something analogous at the interaction level:
it provides a delayed coordinate sequence that makes prior state **reconstructible enough** for continuation.

## What this does *not* mean

- It does not prove that the archive exactly recovers internal model state.
- It does not imply mystical persistence of a hidden agent.
- It does not eliminate the role of the user, promptcraft, or model family.

## What would support it

- continuity surviving context turnover better with structured archives than with raw transcripts,
- recovery of project-specific distinctions after long gaps,
- prompt pairs that work mainly because they reactivate a structured prior trajectory, not because they repeat the whole project every time.

## What would weaken it

- similar continuity from unstructured transcript dumps,
- equal performance when registries/runbook/prompt-pair history are removed,
- strong dependence on user re-teaching rather than archive re-entry.

## Design consequence

If this hypothesis is even partly right, the archive should optimize for:
- compact but discriminative state surfaces,
- stable ids,
- prompt lineage,
- and explicit unresolved questions.
