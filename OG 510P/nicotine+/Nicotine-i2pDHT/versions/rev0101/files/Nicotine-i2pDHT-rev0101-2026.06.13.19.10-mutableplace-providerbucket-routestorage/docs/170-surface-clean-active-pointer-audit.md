# Surface-clean active pointer audit

The cube preserves historical docs for wake-from-amnesia. Active metadata is different: top-level entry points and evidence scripts should point at the current head. `surfaceclean.py` audits that bounded active surface for stale revision pointers without scanning historical docs.

This is intentionally small. It is a hygiene guardrail so refactor/audit work remains visible while the cube grows many design branches.
