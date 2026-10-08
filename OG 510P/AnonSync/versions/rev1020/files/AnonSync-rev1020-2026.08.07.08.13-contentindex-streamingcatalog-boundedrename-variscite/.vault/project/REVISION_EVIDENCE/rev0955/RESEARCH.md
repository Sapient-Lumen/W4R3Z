# Rev0955 research notes

These primary sources informed the implementation boundary and future-work
speculation. They are references, not claims that AnonSync already implements
the referenced facilities.

## SHA-256 continuation ceiling

NIST FIPS 180-4 specifies SHA-256 for messages shorter than 2^64 bits. For a
byte-aligned payload API, the largest admissible byte count is therefore
2^61-1. Rev0955 rejects larger durable or live continuation state rather than
allowing the terminal 64-bit bit count to wrap. As checked on July 31, 2026, NIST still lists FIPS 180-4 as the final Secure
Hash Standard and separately plans FIPS 180-5 before the end-of-2030 SHA-1
transition. The SHA-256 algorithm and this length encoding therefore remain the
current normative basis used here; the implementation does not assume that a
future editorial revision will preserve every surrounding document detail.

References:
https://csrc.nist.gov/pubs/fips/180-4/upd1/final
https://csrc.nist.gov/news/2022/nist-transitioning-away-from-sha-1-for-all-apps
https://csrc.nist.gov/news/2023/decision-to-revise-fips-180-4

## Allocation-independent fault evidence

The C++ fixed-size array abstraction represents an inline fixed-size sequence,
which is a better fit than heap-owning strings for a safety witness that must be
retained while reporting memory pressure. Rev0955 still uses exceptions in the
ordinary product; the relevant design lesson from WG21's failure-oriented
discussion is narrower: code executed at a failure boundary must not depend on a
second allocation merely to preserve the evidence that keeps authority revoked.
The production witness therefore stores two exact 64-character SHA-256 values in
fixed arrays, proves its optional assignment is nonthrowing at compile time, and
marks retention `noexcept`.

References:
https://eel.is/c++draft/array
https://eel.is/c++draft/expr.new
https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2019/p0709r4.pdf

## Filesystem integrity layers

Linux fs-verity builds a Merkle tree, makes an enabled file read-only, verifies
reads in the kernel, and exposes a measurement. It may eventually be a qualified
on-read accelerator for immutable payloads, but it is filesystem-specific and
cannot replace AnonSync's portable SHA-256 content identity, rooted namespace
proof, atomic publication, or cross-platform behavior.

Btrfs scrub and ordinary Btrfs checksum verification provide valuable
storage-layer detection and, with redundancy, repair. They do not prove that a
digest-named application payload contains the bytes named by that digest and
are not portable application semantics.

References:
https://docs.kernel.org/filesystems/fsverity.html
https://btrfs.readthedocs.io/en/latest/Scrub.html
https://btrfs.readthedocs.io/en/latest/Checksumming.html

## Incremental indexing

Syncthing's Block Exchange Protocol retains an index ID and monotonic maximum
sequence number so reconnecting peers can request only later index updates. The
analogy supports a future durable AnonSync change-sequence index with the rooted
scanner retained as rebuild and rotating-scrub oracle. It does not justify
turning the rev0955 scrub journal into namespace authority.

Reference:
https://docs.syncthing.net/specs/bep-v1.html

## Advisory locking and route isolation

Linux `flock(2)` locks are advisory and associated with open file descriptions;
rev0955 consequently makes no hostile same-UID writer claim. Tor's SOCKS
extensions define stream-isolation parameters; route qualification should keep
measuring DNS/address leakage, circuit separation, reconnect behavior, and
traffic shape rather than inferring anonymity from connector construction alone.

References:
https://man7.org/linux/man-pages/man2/flock.2.html
https://spec.torproject.org/socks-extensions.html
