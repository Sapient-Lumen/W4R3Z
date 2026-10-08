# ADR 0093 — Admission wall before expensive handler work

Accepted for rev0023.

Parse-safe and signature-valid traffic can still be hostile or simply too expensive. rev0023 adds a namespace/family/budget admission wall with signed useful-refusal receipts before future handlers spend streams, bytes, metadata, RAM, or custody IO.
