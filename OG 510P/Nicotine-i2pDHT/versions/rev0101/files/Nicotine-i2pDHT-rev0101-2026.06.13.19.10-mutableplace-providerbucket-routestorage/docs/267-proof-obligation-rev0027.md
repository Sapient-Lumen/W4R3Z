# Proof obligations — rev0027

Toy-tested obligations added:

- persisted snapshots round-trip through canonical parseguarded bytes;
- snapshot rollback, same-sequence fork, previous-link mismatch, and malformed bytes quarantine;
- hard-negative evidence survives compaction/reload;
- deterministic malformed parser/wire/shadow cases classify accepted and rejected cases;
- repeated useful-refusal receipt replay across windows quarantines;
- refusal-only laundering streaks quarantine;
- balanced service with bounded useful refusal remains acceptable;
- branchmergefold keeps both rev0026 branchlets and rev0027 surfaces visible.
