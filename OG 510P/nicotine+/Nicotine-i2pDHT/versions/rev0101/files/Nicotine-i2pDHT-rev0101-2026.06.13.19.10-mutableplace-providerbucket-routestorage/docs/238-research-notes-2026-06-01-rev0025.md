# Research notes — 2026-06-01 — rev0025

No new external dependency was introduced in rev0025. The revision continues the same design line:

- capability delegation is useful only when revocation and resource narrowing are tested with the dispatch path;
- mutable heads need local history and split-view pressure rather than pointer freshness alone;
- garden nodes should give capacity but not become truth authorities;
- evidence preservation helps detect rollback/fork/resurrection, but evidence retention itself becomes a DOS surface;
- admission and useful refusal are part of protocol safety, not just operational ergonomics.

The important internal research result this turn is architectural: the riskiest bugs are increasingly cross-surface bugs. rev0025 therefore builds joined tests rather than another standalone object model.
