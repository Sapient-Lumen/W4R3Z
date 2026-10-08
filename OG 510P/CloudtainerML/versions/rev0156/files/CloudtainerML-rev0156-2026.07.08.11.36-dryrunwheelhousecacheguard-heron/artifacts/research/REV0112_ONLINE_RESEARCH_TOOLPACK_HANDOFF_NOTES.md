# Online research notes — REV0112

Status: `pass_with_blockers`  
Promotion allowed: `false`

The useful pattern from the online check is digest-first verification. SLSA verification emphasizes that provenance is useful only when inspected; in-toto Statements bind predicates to subject artifacts by digest; Hugging Face snapshot workflows require explicit revisions for immutable model identity.

Decision for rev0112: make public-trace handoff archives carry a self-contained verifier/evaluator/selector/replay toolpack by SHA-256 subject digests. This reduces the risk that an archive passes only because it is replayed inside a lucky or stale cube checkout.
