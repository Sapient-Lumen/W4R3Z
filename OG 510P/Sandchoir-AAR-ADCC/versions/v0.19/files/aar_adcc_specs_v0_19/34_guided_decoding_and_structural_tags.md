# 34 — Guided Decoding + Structural Tags (v0.19)

Guided decoding is an optional lane to improve parse reliability and reduce retries.
Use it only for **headers** (CTRL/CTRLJSON), never for full responses.

## Why “structural tags”
Some backends support “structural tag” patterns that can enforce an outer wrapper
while allowing flexible content inside. This is ideal for:

- forcing the presence of `@CTRL` and `@VOTE` blocks
- keeping everything else freeform

## Version churn warning
Guided decoding APIs change. Treat any integration as:
- CAP-gated
- optional
- fall back to Tier 1 repair

## Practical integration rule
- If guided decoding exists: constrain only `CTRLJSON` schema.
- If not: use BCC + router-side JSON healing + bounded re-ask.
