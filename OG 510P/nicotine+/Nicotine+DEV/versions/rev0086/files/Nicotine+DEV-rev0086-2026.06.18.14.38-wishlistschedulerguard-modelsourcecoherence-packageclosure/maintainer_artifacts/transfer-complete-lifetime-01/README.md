# TRANSFER-COMPLETE-LIFETIME-01 / U-269 maintainer witness

Current-behavior pytest packet for rev0022.

Run against a source lane with:

```bash
NICOTINE_SOURCE=/path/to/nicotine-plus python -m pytest -q \
  test_completed_upload_socket_lifetime_reproducer.py
```

The assertions document current behavior, not desired behavior. They show that an upload that has sent exactly its advertised byte count remains active until close/idle cleanup, and that invalid post-completion input on the F connection refreshes connection activity while preserving the active upload slot.
