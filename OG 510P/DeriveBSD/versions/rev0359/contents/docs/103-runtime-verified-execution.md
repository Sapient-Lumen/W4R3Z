# Runtime verified execution (optional)

DeriveBSD already aims to **sign** and **attest** artifacts. This direction makes runtime enforcement possible:

- “only closure-approved executables run”
- “only closure-approved libraries load”

## BSD hooks worth stealing

- **NetBSD Veriexec**: kernel-enforced file integrity with an allowlist model. (ref: https://www.netbsd.org/docs/guide/en/chap-veriexec.html)
- **FreeBSD MAC framework**: pluggable security policies, with enough surface area to support “deny unexpected exec/load” styles of enforcement. (ref: FreeBSD Handbook MAC chapter https://docs.freebsd.org/en/books/handbook/mac/)

## Related prior art: file authenticity via Merkle trees (fs-verity style)

Linux’s **fs-verity** is a useful mental model: per-file authenticity enforced by the filesystem using a Merkle tree over file contents, with an associated signature that the kernel verifies before serving data.
DeriveBSD doesn’t need to adopt Linux’s API, but the idea maps well onto our goals:

- store objects are digest-addressed already → the Merkle root can be the stable identity
- kernel-side enforcement can refuse to exec/load unexpected bytes (same intent as Veriexec/MAC)
- userspace can publish signatures over the canonical digest, and policy can require them

References (context):
- fs-verity docs: https://docs.kernel.org/filesystems/fsverity.html
- fsverity-utils (signing workflow notes): https://github.com/ebiggers/fsverity-utils
- Android Verified Boot notes on fs-verity usage: https://source.android.com/docs/security/features/verifiedboot/on-device-signing-architecture

## DeriveBSD stance

- optional feature (not required for v1)
- generated from *existing evidence*:
  - closure manifest/proof
  - deployment object

## Integration sketch

- Build produces closure manifest + proof.
- Activation emits a *fingerprints* artifact derived from the manifest.
- Runtime enforcement loads fingerprints during activation and denies unexpected exec/load.

### A pragmatic stepping stone (MAC “file system firewall”)

Even without full veriexec, FreeBSD’s MAC ecosystem includes “firewall-like” filesystem policies (e.g. `mac_bsdextended(4)`). Those are not a complete verified-exec story, but they can enforce “this jail/service may only read/exec from these paths”. (refs: https://man.freebsd.org/cgi/man.cgi?query=mac_bsdextended&sektion=4 , handbook overview https://docs.freebsd.org/en/books/handbook/mac/)

See also: `docs/233-verified-execution-as-evidence.md`

See RFC-0072.
Last updated: 2026-02-26r91
