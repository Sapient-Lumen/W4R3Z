# REV0019 native memory-safety and execution-state probes

New C++ probes:

- `experiments/memory_poisoning_gate/memory_poisoning_gate.cpp`
- `experiments/execution_state_tree/mage_state_tree_probe.cpp`
- `experiments/prefill_anchor_equalcost/prefill_anchor_equalcost_probe.cpp`
- `experiments/agent_memory_lifecycle_cost/memory_lifecycle_cost_probe.cpp`

These are synthetic wind tunnels, not paper reproductions. They exist to test whether a claim deserves a heavier trained-model harness.

Primary new invariant: memory-selection probes should report tail-risk or trust-failure fields, not only mean utility.
