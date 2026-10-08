# AnonSync rev0764

Integrates canonical-to-SQLite parent projection verification into the production peer-ingress lifecycle. The revision adds an exact twelve-field typed join, strict storage-class decoding, value-free corruption diagnostics, operational row-shape validation, commit-gated enqueue mutation reporting, and focused corruption/rollback tests. It also repairs the stale rev0762 package identity inherited by rev0763.

Start with `../../docs/0149-rev0764-verified-parent-projection-runtime-boundary.md` and `../../ARCHITECTURE-AUDIT-rev0764.md`.
