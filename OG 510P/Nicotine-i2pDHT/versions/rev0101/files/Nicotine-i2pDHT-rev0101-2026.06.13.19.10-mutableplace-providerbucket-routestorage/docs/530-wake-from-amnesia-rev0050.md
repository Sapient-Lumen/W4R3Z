# Wake from amnesia — rev0050

Read these first:

1. `docs/524-rev0050-outboxdrain-samcanary-compactjoin.md`
2. `docs/525-outbox-drain-commit-receipts.md`
3. `docs/526-sam-canary-before-live-send.md`
4. `docs/527-compact-join-negative-evidence.md`
5. `docs/528-drainfold-audit-refactor.md`
6. `tests/test_rev0050_outboxdrain_samcanary_compactjoin.py`

Needles: rev0050 outboxdrain samcanary compactjoin drainfold.

Core thought: public-edge work is still shadow work. Commit receipts and SAM canaries are local boundaries, not live writes.
