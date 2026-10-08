# U-123 research artifact map — rev0073

U-123 is a confirmed transfer-session ownership defect on the exact supported `3.3.x` snapshot used by this cube. Rev0073 classifies it as a low-severity public correctness research question, not an active private security-report candidate.

All files here are generated research instruments. They are not upstream contribution material.

## Classified state matrix

| Artifact | Role | Unpatched | Selected minimal | Strict experiment |
|---|---|---:|---:|---:|
| `test_downloads_duplicate_transfer_token_reproducer.py` | Current-bad-state witness | pass | fail | fail |
| `test_downloads_duplicate_transfer_token_collision_rejection_regression.py` | Selected admission invariant | fail | pass | pass |
| `test_downloads_duplicate_transfer_token_identity_guard_regression.py` | Defense-in-depth cleanup invariant, using a directly constructed conflicting-owner state | fail | pass | pass |
| `test_downloads_duplicate_transfer_token_burst_bound_regression.py` | Bounded 32-request resource-footprint invariant | fail | pass | pass |
| `test_downloads_duplicate_transfer_token_fixed_regression.py` | Composite of the three selected fixed invariants | fail | pass | pass |
| `test_downloads_duplicate_transfer_token_same_object_reentry_experiment.py` | Synthetic reachability experiment, not selected acceptance | fail | fail | pass |

The selected minimal prototype rejects a token only when a **different** transfer already owns it and makes stale deactivation identity-aware. The stricter experiment rejects every occupied token, including a deliberately synthesized same-object reentry. Rev0073 did not show that extra state is reachable through supported runtime transitions, so the stricter behavior is not selected.

`u123_harness.py` centralizes the isolated configuration, module-global substitution, queued-transfer construction, fake socket identity, and cleanup shared by the six entrypoints.

## Superseded rev0072 packet

The byte-for-byte rev0072 active packet is preserved under:

```text
docs/archive/rev0072-active-u123/
```

It is superseded because its README and tests encoded conflicting policy generations. The active rev0073 files do not silently mutate that historical record.

## Rerun

From the cube root, with the external source bundle available:

```bash
python tools/probe_rev0073_u123_disposition.py --source-zip auto --write-data
python tools/probe_rev0073_u123_native_patch.py --source-zip auto --write-data
```

The expected/observed matrix is written to:

```text
data/rev0073_u123_test_matrix.csv
```

Read `docs/U123-CURRENT-DISPOSITION-REV0073.md` before drawing impact or routing conclusions.
