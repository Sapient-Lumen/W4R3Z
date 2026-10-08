# rev0019 scout notes — tail poison, execution state, equal cost

This revision keeps the C++-first posture and adds four native probes instead of only ledger notes. The center of gravity shifted from generic cache compression to **trustworthy state and memory selection under adversarial or long-horizon pressure**.

## New source cluster

- `SRC-0249` memory poisoning: persistent memory can convert untrusted input into trusted future context.
- `SRC-0250` trustworthy memory search: memory retrieval is a trust boundary, not just a semantic top-k operation.
- `SRC-0251` execution-state management: long-horizon agent memory should preserve active path/state, not retrieve disconnected similar fragments.
- `SRC-0252` agent memory systems characterization: construction, retrieval, generation, freshness, and energy/cost are different axes.
- `SRC-0253` active graph reconstruction: memory can be reconstructed through iterative graph evidence gathering.
- `SRC-0254` head-aware KV: cache objects should not always be monolithic token sequences.

## New native probes

- `memory_poisoning_gate.cpp`: similarity-only retrieval vs write/read/provenance gates.
- `mage_state_tree_probe.cpp`: semantic retrieval vs active path/tree memory under branching and errors.
- `prefill_anchor_equalcost_probe.cpp`: sparse chunk anchors under equal processed-token cost.
- `memory_lifecycle_cost_probe.cpp`: memory construction/serve/freshness phase diagram.

## Working recommendation

The best next hardening target is **CELL-223 Memory Poisoning Gate**, because it now binds safety-tail metrics, provenance/correction memory, and trust-boundary search into one native phase diagram. Second choice is **CELL-224 Execution-State Tree**, which is the strongest candidate for a tiny trained-agent environment later.
