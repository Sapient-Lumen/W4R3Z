# rev0048 audit quorum is local evidence

`auditquorum.py` treats bridge publication audit receipts as local evidence, not global truth.

Receipts can support a bridge shadow only when they bind to the exact shadow digest, public payload digest, scope, request, profile, and service. Stale-public-record receipts, payload mismatch receipts, replay, low diversity, and receipt monoculture block or hold acceptance.

Current test surface: `tests/test_rev0048_bridgeshadow_auditquorum_redressgc.py`.
