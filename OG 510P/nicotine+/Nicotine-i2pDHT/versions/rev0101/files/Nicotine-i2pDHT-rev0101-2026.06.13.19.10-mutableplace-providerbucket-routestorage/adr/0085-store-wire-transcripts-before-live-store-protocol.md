# ADR 0085 — STORE wire transcripts before live STORE protocol

Accepted for rev0021.

Before a live STORE protocol exists, exact-digest STORE requests, receipts, custody challenges, and custody proofs must have deterministic canonical wire fixtures.  A signed frame is not enough; payload role and frame kind must agree.
