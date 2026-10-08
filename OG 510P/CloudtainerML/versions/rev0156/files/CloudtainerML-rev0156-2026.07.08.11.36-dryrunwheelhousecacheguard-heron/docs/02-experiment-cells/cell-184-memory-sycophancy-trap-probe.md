# CELL-184: Memory Sycophancy Trap Probe

Priority: P0

Status: runnable

Idea: IDEA-0183

Source: SRC-0221

Cheap first run: C++ symbolic persistent-memory safety toy; output REV0015_MEMORY_SYCOPHANCY_TRAP_SMOKE.json.

Metrics:
- sycophancy rate
- accuracy rate
- unsafe high-stakes rate
- memory recall

Baselines:
- belief snippet memory
- recency memory
- provenance balanced
- skeptical high-stakes
- no persistent memory
- oracle memory

Stop condition: If no simple provenance/skeptical policy beats no-memory, keep as safety red-team not core optimization.
