# TR-STATUS-01 maintainer artifact — rev0012

Current-behavior pytest reproducer for download-side transfer status message provenance.

Run against an upstream checkout:

```bash
NICOTINE_SOURCE=/path/to/nicotine-plus python -m pytest -q test_transfer_status_message_binding_reproducer.py
```

rev0012 run result across archived lanes:

```text
github-tag-3.3.10: 4 passed
github-branch-3.3.x: 4 passed
github-branch-master: 4 passed
```

These tests assert current behavior, not a proposed fixed invariant. They should be converted to fixed-behavior regressions only after maintainers choose a compatibility-preserving provenance model.
