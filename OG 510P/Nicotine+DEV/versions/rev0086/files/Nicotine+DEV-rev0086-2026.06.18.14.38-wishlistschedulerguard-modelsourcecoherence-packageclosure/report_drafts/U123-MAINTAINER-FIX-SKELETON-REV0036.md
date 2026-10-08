# U-123 maintainer fix skeleton — rev0036

This is a design skeleton, not a submitted patch.

## Required invariant

```text
For any deactivation/timeout callback carrying Transfer object A, destructive removal of active_users[username][token] is allowed only if that map entry still points to A.
```

## Minimal identity-guard sketch

```python
def _deactivate_transfer(self, transfer):
    username = transfer.username
    token = transfer.token

    if token is None:
        return False

    active_for_user = self.active_users.get(username, {})
    active_transfer = active_for_user.get(token)

    if active_transfer is transfer:
        del active_for_user[token]
        if not active_for_user:
            del self.active_users[username]
    elif active_transfer is not None:
        # Stale callback for an older same-user/same-token transfer.
        # Do not remove the newer active transfer.
        pass
    else:
        # No active slot; still consider transfer-local cleanup.
        pass

    # Existing transfer-local cleanup and accounting should then be applied
    # to the object being deactivated, not to whatever currently occupies
    # active_users[username][token].
```

## Alternative acceptable shapes

```text
1. Reject duplicate same-user/same-token activation while a different transfer is active.
2. Bind active transfer callbacks to a local session/generation ID in addition to the protocol token.
3. Keep username+token as the protocol lookup key but make every destructive callback verify object identity before mutating the shared slot.
```

## Regression gate

The new regression skeleton should pass after the chosen fix:

```bash
PYTHONPATH=/path/to/nicotine-plus python3 maintainer_artifacts/u123/test_downloads_duplicate_transfer_token_fixed_regression.py
```

The old current-behavior witness should be inverted or removed after the fix lands.
