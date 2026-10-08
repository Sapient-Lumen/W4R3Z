# 67 — Blackboard Rationale + Anytime Packets (v0.19)

Your system is best understood as a modern blackboard architecture:
- WS is the blackboard (strict working memory)
- agents are knowledge sources
- AAR is the control component that decides what knowledge sources see next
- MetaLLM is the supervisor that tunes the control component

This framing is useful because it explains why strict WS/ledger separation matters.

## 1) Anytime packets
Because slice counts are unknown and truncation is common:
- every agent output is treated like an “anytime algorithm” result:
  - valid even if interrupted
  - improves if more time/slices occur

Therefore:
- early CTRL capture matters
- partial structured content is worth salvaging
- strict bounded repair loops matter

## 2) Why WS must stay clean
In blackboard systems, the central shared memory must remain legible and consistent.
Your WS caps + compaction are the modern equivalent of keeping the blackboard usable.

## 3) Practical consequence
Design everything so that:
- progress is possible even if only one agent produces a good CTRL
- the system can “contract” into PatchOnly mode under bandwidth collapse
- evidence runs remain bounded and cached

## 4) Where this can mislead you
Classic blackboard systems can devolve into unstructured accumulation.
Your invariants (50_) prevent that via:
- strict view assembly
- typed objects
- compaction

This is why you’re not “just letting them chat.”
