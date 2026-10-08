# rev0020 scout notes — memory contracts, execution verification, provenance DAGs

This revision keeps the C++-first posture and hardens the P0 agent-memory safety lane rather than adding a random spread of probes.

## Fresh source cluster

- `SRC-0261` evidence tracing/provenance: memory items should carry source, revision, retrieval, use, and invalidation state.
- `SRC-0262` PersonaTree: support paths from evidence to stable claims.
- `SRC-0263` MERIT: episode-level and turn-level memory have different horizons.
- `SRC-0266` failed trajectories / harness reliability: runtime state and failure traces are part of the agent, not just model inputs.
- `SRC-0267` triggered multimodal memory poisoning: delayed trigger activation deserves a separate trap.

## New native probes

- `memory_admissibility_hpo.cpp`
- `execution_state_verify_probe.cpp`
- `evidence_provenance_dag_probe.cpp`
- `horizon_memory_retrieval_probe.cpp`

## Working recommendation

Rev0021 should harden one of: memory admissibility HPO, execution-state verification, or evidence-provenance DAG scoring. The priority bias is still toward memory poisoning/trust boundaries because they create useful negative cases at tiny scale.
