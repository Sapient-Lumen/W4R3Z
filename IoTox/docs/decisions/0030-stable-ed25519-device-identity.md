# ADR 0030: Give IoTox a stable Ed25519 device identity above Tox

**Status:** accepted and implemented in rev0009

## Context

A Tox public key is a valuable authenticated transport identity, but it is persisted inside a
Tox profile, may need rotation after compromise or corruption, and cannot by itself express the
IoTox ownership constitution. Treating it as the permanent physical-device identity would make
transport recovery indistinguishable from device replacement and would couple every future
Tor/I2P route choice to ownership.

IoTox also needs a mature signature implementation for owner records and later session-bound
proofs. The source-linked product already depends on libsodium through c-toxcore.

## Decision

IoTox has a separate stable Ed25519 device keypair. The public key is the application-level
device identifier. Tox keys remain replaceable transport endpoints.

The current private identity file is exactly 80 bytes:

```text
0..7   magic "IOTOXID1"
8      format version 1
9      algorithm 1 (Ed25519)
10..15 zero
16..47 32-byte seed
48..79 32-byte public key
```

The file is opened without following symlinks, must be a regular file owned by the process
user, may have no group/other permissions, and must have the exact length. The public key is
rederived from the seed on every load. Creation uses the operating-system CSPRNG and atomic
mode-0600 persistence.

If a nonempty authority ledger exists and the identity cannot be loaded, the agent fails. It
must not silently create a different constitutional device for an existing ledger.

IoTox uses libsodium Ed25519 and BLAKE2b-256 through one narrow provider. Runtime loading
remains available for local research and exact tests. The source-linked product compiles the
same provider against pinned static libsodium and does not require a runtime shared library.

## Consequences

A Tox profile can later rotate without changing the stable IoTox device identifier. Route
bindings can eventually be signed by this identity. Authorization records can be bound to the
physical/application device rather than a transient friend number or route key.

The current seed is private plaintext protected by filesystem ownership and mode. This is not
secure-element protection and is not claimed to resist a privileged host or stolen unencrypted
disk. Product-specific keystore integration can supersede the storage backend without changing
the public identity contract.
