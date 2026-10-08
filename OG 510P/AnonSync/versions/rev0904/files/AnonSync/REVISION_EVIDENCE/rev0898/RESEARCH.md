# AnonSync rev0898 research and speculation

Research was consulted on 2026-07-25. These are primary implementation sources;
all proposed changes below are design hypotheses until implemented and tested.

## SQLite durability and role identity

- SQLite Write-Ahead Logging: https://www.sqlite.org/wal.html
  WAL uses sidecar files, assumes same-host shared-memory coordination, and does
  not make a transaction spanning multiple attached databases atomic as a set.
- SQLite ATTACH: https://sqlite.org/lang_attach.html
  This reinforces that a multi-store deployment needs an explicit protocol if
  whole-set commit semantics matter.
- SQLite database file format: https://www.sqlite.org/fileformat.html
  The application_id field is a candidate supplementary role discriminator.
  Speculation: pair a fixed per-role application_id with schema attestation and
  a shared deployment identifier; do not treat application_id alone as proof.

## Descriptor-rooted path authority

- Linux openat2(2): https://man7.org/linux/man-pages/man2/openat2.2.html
  Resolution controls such as beneath/in-root/no-symlink/no-magic-link suggest a
  stronger Linux authority owner than lexical normalization plus final-component
  no-follow. Speculation: introduce a root directory descriptor capability and
  resolve every manifest-bound path relative to it, with a portable component
  walk or platform-specific equivalent elsewhere.

## Supervision and operational hardening

- systemd.exec: https://www.freedesktop.org/software/systemd/man/systemd.exec.html
- systemd.service: https://www.freedesktop.org/software/systemd/man/systemd.service.html
  Speculation: keep the C++ worker bounded and deterministic, while a narrow
  service unit owns restart policy, deadlines, filesystem sandboxing, resource
  limits, and secret injection. This should supplement, not replace, in-process
  authority checks.

## Build-cost experiments

- CMake UNITY_BUILD: https://cmake.org/cmake/help/latest/prop_tgt/UNITY_BUILD.html
- CMake compiler launchers: https://cmake.org/cmake/help/latest/variable/CMAKE_LANG_COMPILER_LAUNCHER.html
- CMake compile job pools: https://cmake.org/cmake/help/latest/prop_tgt/JOB_POOL_COMPILE.html
  Speculation: first measure cache hit rate and target fan-out; then trial a
  compiler cache launcher and unity builds only on stable leaf libraries.
  Global unity mode could create ODR/macro hazards and obscure dependency
  boundaries, so it should not be enabled merely to hide graph fragmentation.

## Privacy nonclaim

Mutual TLS and SPKI authorization authenticate peers and protect transport
contents. They do not by themselves provide anonymity, endpoint hiding,
unlinkability, cover traffic, metadata minimization, or traffic-analysis
resistance. Those remain separate product and threat-model workstreams.
