# ADR 0031: Derive one stable owner principal from RecallRoot-v1

**Status:** accepted and implemented in rev0009

## Context

IoTox deliberately keeps a permanent printed or remembered generated phrase. The desired
property is not ordinary account recovery: from memory, the owner can reconstruct cryptographic
authority without an IoTox service or universal vendor key.

The fixed Argon2id RecallRoot-v1 contract already makes the same 32-byte root reproducible. It
also permits offline guessing, so generated phrase entropy is structural rather than optional.
The remaining choice was how that root becomes an owner identity without using raw Argon2 output
for unrelated purposes.

## Decision

RecallRoot-v1 derives an Ed25519 owner seed through the fixed IoTox keyed-BLAKE2b contract using
the domain:

```text
iotox-owner-signing-seed-v1
```

The resulting deterministic Ed25519 public key is the owner principal. The same phrase therefore
reconstructs the same owner principal across devices.

Recall mutation commands read the phrase only from standard input in a short-lived invocation of
the one `iotox` executable. That invocation parses the embedded pinned 7776-word list, performs
Argon2id, derives the owner key, signs the daemon-prepared record, wipes owned secret buffers,
and exits. The daemon receives only public request fields and the final signed record. It never
receives or stores the phrase, RecallRoot, owner seed, or owner secret key.

No IoTox vendor key or server participates.

## Consequences

The permanent phrase can bootstrap or exercise owner authority from memory. A shell argument is
not required, reducing ordinary history leakage.

The owner public key is globally stable and therefore linkable wherever disclosed. That is an
explicit current tradeoff for direct re-entry. A later per-device delegation layer may reduce
routine linkability while retaining the recalled owner as a root authority.

Anyone who obtains the phrase can reproduce owner signing power. Anyone with a verifier can try
guesses offline. The product must generate strong phrases and must not market user-chosen
passwords as equivalent. ADR 0054 later defines a successor-signed epoch cut for planned transfer
or suspected phrase compromise while current authority remains available.
