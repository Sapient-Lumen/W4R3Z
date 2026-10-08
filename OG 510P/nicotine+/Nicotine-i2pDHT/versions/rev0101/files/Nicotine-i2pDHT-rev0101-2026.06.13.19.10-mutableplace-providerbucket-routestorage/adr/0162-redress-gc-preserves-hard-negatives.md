# ADR 0162 — Redress GC preserves hard negatives

Accepted for rev0048.

Redress cleanup is a protocol boundary.  Expired soft evidence can be dropped, but hard negatives such as live quarantine, compromise, false-service, and fork evidence must not be removed merely because redress evidence exists or byte pressure is inconvenient.
