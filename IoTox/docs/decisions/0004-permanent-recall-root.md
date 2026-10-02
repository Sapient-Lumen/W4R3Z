# ADR 0004: Permanent memorized re-entry through RecallRoot-v1

**Status:** accepted for rev0002

## Context

The product should remain recoverable without a vendor account, escrow service, retained controller database, or removable backup file. The desired experience is stronger than ordinary backup: an owner who remembers a permanent printed phrase should be able to reproduce the owner-side root and reach previously owned devices.

This necessarily permits offline guessing and makes phrase disclosure equivalent to root compromise.

## Decision

Adopt a fixed, versioned Argon2id derivation contract named `iotox-recall-root-v1`.

The supported v1 creation format is exactly eight independently and uniformly selected words from the pinned 7,776-entry EFF long word list. Input is canonicalized to lowercase ASCII words separated by one ASCII space. Argon2id version 19 runs with 65,536 KiB memory, three iterations, four lanes/threads, fixed 16-byte salt `IoToxRecallRoot1`, and a 32-byte output.

The contract is permanent. Implementations may add a future version but may never silently alter v1 parameters or normalization. Migration to a new root or contract requires an explicit signed ownership transition.

## Consequences

- From memory or the printed card, the same root can be reproduced anywhere.
- There is no online rate limit and no vendor-assisted password reset.
- The public fixed salt permits offline and cross-user guess amortization.
- A generated eight-word phrase has approximately 103.4 bits of entropy; a human-created phrase has no such guarantee.
- Product creation flows must generate phrases rather than soliciting weak prose.
- Phrase theft is owner-root compromise and must be described honestly.
- Root-derived key domains and the Tox re-entry handshake still require separate decisions and tests.
