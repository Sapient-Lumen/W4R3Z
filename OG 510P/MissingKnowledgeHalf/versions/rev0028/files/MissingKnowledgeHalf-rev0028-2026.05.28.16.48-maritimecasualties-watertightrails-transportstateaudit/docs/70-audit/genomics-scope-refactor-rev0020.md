# Genomics scope refactor audit — rev0020

Audit target: the genomics lane after rev0018 and rev0019.

Problem found: records were increasingly careful in prose, but no common overlay forced future sessions to preserve phenotype, ancestry/population, portability, and governance cautions.

Repair made: added `scope_qualifiers` to the current genomics-related NEG, MET, INF, CTL, and PAT records. This is a soft overlay rather than a schema requirement. It allows resumption sessions to search the lane by scope hazards without freezing ontology too early.

Still open: no full semantic second-pass review; no monitor source-code audit; no clinical implementation review; no negative-control/counterexample record for MKH-PAT-0016.
