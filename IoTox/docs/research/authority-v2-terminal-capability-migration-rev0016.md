# Authority-v2 terminal capability migration research note — rev0016

Date: 2026-08-16

This note records primary references rechecked while defining the R2 authority boundary and its
local rollback guard. They are design inputs, not protocol dependencies or third-party approval of
IoTox.

## Sources

- c-toxcore v0.2.23 release:
  https://github.com/TokTok/c-toxcore/releases/tag/v0.2.23
- RFC 6709, *Design Considerations for Protocol Extensions*:
  https://www.rfc-editor.org/rfc/rfc6709.html
- RFC 9170, *Long-Term Viability of Protocol Extension Mechanisms*:
  https://www.rfc-editor.org/rfc/rfc9170.html
- RFC 8032, *Edwards-Curve Digital Signature Algorithm (EdDSA)*:
  https://www.rfc-editor.org/rfc/rfc8032.html
- RFC 9591, *The Flexible Round-Optimized Schnorr Threshold (FROST) Protocol for Two-Round Schnorr
  Signatures*:
  https://www.rfc-editor.org/rfc/rfc9591.html

## Applied lessons

RFC 6709 treats a change to protocol semantics or the security model as a major extension requiring
explicit compatibility, versioning, unknown-extension behavior, and testability. Adding terminal
authority is therefore a signed v2 boundary with independent wire values and old-code rejection,
not an in-place expansion of v1 `all`.

RFC 9170 emphasizes that extension points can ossify or become ambiguous when implementations do
not exercise and negotiate them consistently. IoTox advertises authority v2 through a distinct
transcript-bound feature bit, carries the format in challenge/proof bytes, and keeps v1/v2 behavior
directional rather than silently downgrading a migrated verifier.

RFC 8032 fixes the Ed25519 algorithm and its canonical encodings, while also illustrating why a
protocol must define the exact message being signed. IoTox signs fixed canonical record bodies under
version-specific application domains. The RecallRoot client additionally decodes and compares the
daemon-prepared body with the requested ceremony before producing a signature, so canonical bytes
do not become permission for semantic substitution.

RFC 9591 is not used for threshold signing, but its protocol construction gives another current
example of explicit context strings and participant/transcript binding around signatures. IoTox
keeps v1/v2 record and proof domains independent and binds authority proof to verifier, exact ledger
head, confirmed-session transcript, nonce, and challenge ID.

The c-toxcore v0.2.23 release remains the pinned transport target. Its continued emphasis on bounds,
lifetime, allocation-failure, and testing repairs reinforces the local construction rule that the
security boundary must fail before effects and preserve exact state across errors; it does not prove
or approve the IoTox authority design.

## Rollback-guard inference and limits

A digest-chained signed ledger authenticates content and order but does not identify which valid
snapshot is newest. IoTox adds a separate private `IOTOXAG2` committed/pending head file so a ledger
append has two explicit crash-recoverable states. That detects rollback, deletion, or fork of the
ledger alone and permits exact recovery when either the ledger replace or final guard promotion was
interrupted.

The guard is deliberately described as a local witness, not a cryptographic or hardware monotonic
counter. A same-privilege attacker able to restore both ledger and guard as an older consistent pair
can still evade it. Replicated checkpoints, trusted hardware, or owner-observed heads remain future
work.
