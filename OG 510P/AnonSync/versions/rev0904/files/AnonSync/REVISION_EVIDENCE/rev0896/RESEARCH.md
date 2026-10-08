# AnonSync rev0896 research notes

## SQLite upstream observation

Official SQLite pages observed during this session still report 3.53.4 as the
latest release, dated 2026-07-24. The download page lists
`sqlite-amalgamation-3530400.zip` for SQLite 3.53.4 with SHA3-256
`628a44cfe82c66aed1ccbbe85a562d2e33ebe64b3288981ed76285612227934e`, and the
release log lists SHA3-256 for `sqlite3.c` as
`67f423e9ebbbdc473cbc4772c872ee6b89f31fde4ed0279a5c25d5f65c043a16`.

The local tree still verifies the bundled SQLite 3.53.3 amalgamation at CMake
configure time. A 3.53.4 upgrade is not claimed in rev0896.

## Product speculation

The most useful next product surface is not a broad UI. It is a daemon loop that
consumes the same status facts now exposed by the CLI, with every transition
bounded and restartable. Status should become the guardrail for deciding whether
there is claimable outbox work, whether clock health blocks liveness, whether
payload retention is sufficient, whether receiver effects are staged or
published, and whether membership anchors are current.

The privacy/anonymity name remains ahead of implementation. TLS and SPKI
authentication protect content in transit and bind peer identity, but they do
not hide endpoints, graph shape, overlap, timing, or access patterns. A future
privacy layer needs an explicit threat model before adding mechanisms.
