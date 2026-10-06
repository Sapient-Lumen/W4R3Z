# Anti-rollback beyond signatures (rollback indices)

Signed artifacts aren’t enough if an attacker can force a **rollback** to an older, vulnerable version.
DeriveBSD already addresses replay/freeze/rollback at the *repository metadata* layer (TUF-style).
Some ecosystems also harden the *boot/activation* layer with **rollback protection**.

Reference (Android Verified Boot):
- Verified Boot + rollback protection overview: https://source.android.com/docs/security/features/verifiedboot
- Boot flow note (A/B + rollback metadata): https://source.android.com/docs/security/features/verifiedboot/boot-flow

## Lesson to steal

- store a **monotonic rollback index** in tamper-resistant storage
- refuse to boot/activate images with an index lower than the stored value
- only advance the stored value after a new version is known-good

## DeriveBSD mapping (optional, policy-gated)

### Object model

- each host generation (and optionally each microVM base) includes:
  - `rollback_index` (or `min_rollback_index`)
- the host maintains:
  - `stored_rollback_index[channel]` in a monotonic store (TPM NV where available; otherwise policy may disable)

### Activation algorithm (sketch)

1) verify artifacts + policy decision record as usual
2) check `generation.rollback_index >= stored_rollback_index[channel]`
3) switch tentatively (boot env) and run health gate
4) on health success: advance stored rollback index

### Operational nuance

- break-glass rollback remains possible only with **explicit policy override** (and leaves evidence)
- pairs naturally with:
  - `docs/61-channel-metadata-tuf-inspired.md`
  - `docs/62-replay-rollback-freeze.md`
  - `docs/112-health-gated-updates.md`

Candidate RFC: *Rollback indices for high-assurance channels*.

Last updated: 2026-02-23
