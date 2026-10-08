# Scenario: wrapper / RUSTFLAGS drift

Purpose:
- prove that wrapper and flag changes can be explained as a first-class rebuild story
- without promising to identify which individual flag changed Cargo's reuse decision

Expected output shape:
- `rebuild.receipt.json` should preserve before/after wrapper and flag posture
- `fingerprint-delta.json` should label the verdict `wrapper_or_flags_changed`
