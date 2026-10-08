# ADR 0156 — public edge staging is a side effect

Accepted for rev0049.

A node must not treat bridge-shadow/audit/redress acceptance as automatic permission to stage a public record.  `publishdryrun.py` creates a separate signed, scoped, sequenced dry-run attempt before any future network write.
