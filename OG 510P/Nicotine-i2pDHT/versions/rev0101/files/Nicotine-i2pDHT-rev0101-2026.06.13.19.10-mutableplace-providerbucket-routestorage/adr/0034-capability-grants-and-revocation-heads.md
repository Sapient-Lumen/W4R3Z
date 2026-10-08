# ADR 0034 — Capability grants and revocation heads

Accepted for rev0009. Delegated work should use scoped, expiring, signed grants. Revocation is represented as signed revocation entries published through mutable heads.

Consequences: revocation is eventually consistent and imperfect, so grants should be narrow and short-lived.
