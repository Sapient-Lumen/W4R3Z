# Structured outputs (stable JSON contracts)

This file is a short pointer; the authoritative contract lives in:
- `docs/87-structured-output-contract.md`
- RFC-0057
- ADR-0028

## Extra mile (optional)

If we need streaming progress/events, prefer JSONL event streams (still schema-versioned and safe):
- `progress`
- `warnings`
- `policy.decisions`
- `final.result`

Last updated: 2026-02-23
