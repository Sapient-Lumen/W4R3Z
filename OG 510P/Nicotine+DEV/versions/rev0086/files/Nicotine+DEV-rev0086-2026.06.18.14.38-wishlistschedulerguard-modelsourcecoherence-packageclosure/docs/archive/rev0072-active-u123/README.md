# U-123 maintainer artifact packet — rev0036

Contents:

```text
test_downloads_duplicate_transfer_token_reproducer.py
test_downloads_duplicate_transfer_token_fixed_regression.py
```

`test_downloads_duplicate_transfer_token_reproducer.py` is the original current-behavior witness. It demonstrates that a stale timeout belonging to the first transfer can delete the active-map entry for a later same-user/same-token F-connection session.

`test_downloads_duplicate_transfer_token_fixed_regression.py` is the new rev0036 fixed-behavior regression skeleton. It is intentionally expected to fail against the archived current source lanes and expected to pass after the transfer deactivation path is made identity-aware.

Run the current-behavior witness from an extracted Nicotine+ source tree with:

```bash
PYTHONPATH=/path/to/nicotine-plus python3 test_downloads_duplicate_transfer_token_reproducer.py
```

Run the fixed-behavior regression skeleton with:

```bash
PYTHONPATH=/path/to/nicotine-plus python3 test_downloads_duplicate_transfer_token_fixed_regression.py
```

Rev0036 results:

```text
current-behavior witness:
  github-tag-3.3.10:   OK
  github-branch-3.3.x: OK
  github-branch-master: OK

fixed-behavior regression against current source:
  github-tag-3.3.10:   expected failure at missing active username+token mapping
  github-branch-3.3.x: expected failure at missing active username+token mapping
  github-branch-master: expected failure at missing active username+token mapping

identity-guard simulation:
  github-tag-3.3.10:   OK
  github-branch-3.3.x: OK
  github-branch-master: OK
```

The simulation helper in `tools/run_u123_identity_guard_sim.py` is not a proposed upstream patch. It only proves that the fixed regression is reachable with a narrow object-identity guard that leaves a newer username+token session mapped while cleaning the stale transfer object.
