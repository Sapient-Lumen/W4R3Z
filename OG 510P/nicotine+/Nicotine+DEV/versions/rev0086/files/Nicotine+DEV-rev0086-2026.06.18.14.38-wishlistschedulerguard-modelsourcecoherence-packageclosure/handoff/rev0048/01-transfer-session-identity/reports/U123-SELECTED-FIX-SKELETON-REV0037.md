# U-123 selected fix skeleton — rev0037

This is a prototype skeleton, not a submitted upstream patch.

## Part 1 — reject colliding active download token before dequeue/accept

```python
download = (self.queued_users.get(username, {}).get(virtual_path)
            or self.failed_users.get(username, {}).get(virtual_path))
active_download = self.active_users.get(username, {}).get(token)

if active_download is not None and active_download is not download:
    reason = TransferRejectReason.QUEUED if download is not None else TransferRejectReason.CANCELLED
    return TransferResponse(allowed=False, reason=reason, token=token)
```

The check belongs before `_unfail_transfer(download)` and `_dequeue_transfer(download)`, so a colliding queued transfer remains queued.

## Part 2 — identity-aware deactivation

```python
active_transfers = self.active_users.get(username, {})
active_transfer = active_transfers.get(token)
deactivated = False

if active_transfer is transfer:
    del active_transfers[token]
    if not active_transfers:
        del self.active_users[username]
    deactivated = True

# Continue transfer-local cleanup for the object being aborted.
return deactivated
```

Identity-aware deactivation is retained as defensive hardening. It is not sufficient by itself because it does not stop a second same-user/same-token request from replacing an already active F-connection owner.

## Regression gate

```bash
PYTHONPATH=/path/to/nicotine-plus python3 maintainer_artifacts/u123/test_downloads_duplicate_transfer_token_collision_rejection_regression.py
```
