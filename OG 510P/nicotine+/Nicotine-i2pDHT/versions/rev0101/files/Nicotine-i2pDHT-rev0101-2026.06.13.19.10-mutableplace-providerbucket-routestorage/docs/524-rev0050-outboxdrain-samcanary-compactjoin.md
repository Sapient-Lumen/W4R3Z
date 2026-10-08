# rev0050 — outboxdrain-samcanary-compactjoin

rev0050 moves one step closer to the eventual public write without crossing into live I2P/SAM transport. The risky seam is now:

```text
public outbox staged
+ publish dry-run accepted
+ SAM trace accepted
+ scope journal accepted
+ compaction reports accepted
    ≠ safe drain
    ≠ safe commit
    ≠ safe SAM send
    ≠ safe negative-evidence forgetting
```

The new design rule:

> A queued public side effect is not safe to drain because it was staged; it is safe only when commit receipt, SAM canary, and compacted negative evidence bind to the same exact boundary.

New surfaces:

- `outboxdrain.py` — signed prepare/commit receipts for draining a public outbox entry without sending anything.
- `samcanary.py` — no-network canaries that bind a future SAM send to session, destination, frame, egress, idempotency, and exact scope.
- `compactjoin.py` — joined witness/audit/redress/scope-journal compaction so hard negatives are not split away.
- `drainfold.py` — current fold audit preserving rev0049 publish/outbox predecessor history.

This revision deliberately treats commit, canary, and compaction as different permissions. Passing one cannot authorize another.
