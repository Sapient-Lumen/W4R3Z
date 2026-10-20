# rev0039 cube import and bare-metal qualification

Date: 2026-08-20

Qualified source commit: `af109350e35bd71d4d50ee16d535d5e7fcdde891`

Host: NixOS 24.05, Linux 6.12.34, x86-64

## Source and lineage

The inspected handoff was:

```text
DR0Pbox/IoTox-rev0026-2026.08.20.00.14-continuous-psi-tripwire-quiet-window-citadel.zip
SHA-256 f062d8c5f90b78fd33b617207475b61f3a78ee54e2f75b9f266ad64ce72c1008
```

The outer filename says rev0026, but the verified repository payload identifies itself as IoTox
0.39.0 rev0039 and carries Git tip `2bb5548cf7f1221b1bde01e5fd8c1c0b6ed6a1f9`. Its complete Git
bundle was imported first as `import/rev0039-citadel`. The former official tip
`7d975d3` is its ancestor: the comparison was 0 commits unique to the old tree and 67 commits unique
to the cube. `main` was therefore advanced with `--ff-only`; no history was replaced and no divergent
line was synthesized.

The 67 commits supply the Ratox session/authority/PTTY/controller/restart chain and the later cgroup,
resource-accounting, PSI-admission, continuous-trigger, testing, documentation, and retained-evidence
work through rev0039. The externally misnumbered archive should not be cited as a rev0026 source tree
without this payload qualification.

## Bare-metal corrections

Four construction-environment assumptions were exposed and corrected before accepting the import:

1. A canonical inherited-identity profile configured `limit-processes=8`. On Linux this becomes
   `RLIMIT_NPROC`, which is charged across the complete real UID rather than one terminal. The busy
   founding account could create the PTY but its payload could not create another task (`EAGAIN`).
   Production now rejects that unsafe combination. Inherited profiles use zero, while a true
   per-session limit belongs in delegated-cgroup `pids.max`.
2. Several process tests constructed Unix-domain socket paths too long for Linux's `sockaddr_un` when
   the inherited temporary root was long. Test-owned directory names are now short and collision-safe.
3. Python safe-path behavior omitted the analyzer script directory, and Nix compiler wrappers injected
   linker-only inputs into Clang's non-linking `--analyze` mode. The CTest route now provides the exact
   module path; the analyzer removes wrapper link variables and suppresses only the corresponding
   driver-level unused-input warning while project diagnostics remain fatal.
4. GCC 15 diagnosed two bounded library constructions as string-operation false positives under
   `-Werror`. Both were rewritten as direct bounded element operations without suppressing GCC
   diagnostics or changing the wire bytes.

## Evidence

The imported IoTox implementation was built against pinned source-linked c-toxcore 0.2.23 and static
libsodium/Argon2. The complete final-source matrix passed:

- GCC 15.3 Debug and Release: 19 CTest routes each;
- Clang 21.1.8 Debug: 19 routes;
- Clang 21.1.8 ASan/UBSan and GCC 15.3 TSan: 34 sharded routes each;
- four focused Clang path-sensitive analyzer units, zero diagnostics;
- eleven libFuzzer targets, 5,000 units each;
- linked-system-Argon2: 19 routes;
- Mutorr preservation: 21 routes;
- final marker: `final-source-matrix=pass`.

The direct owned IoTox registry remains 359 checks. The native PTY process oracle additionally covers
the inherited-identity `RLIMIT_NPROC` refusal.

The preserved toxsync 0.7.0 engine was then qualified independently with 121 native checks and two
CTest routes in each of GCC Debug, GCC Release, GCC portable Release (builtin C++ SHA-256 and scalar
rolling checksum), Clang Debug, and Clang ASan/UBSan. The new
`tools/build-toxsync-matrix.sh` reproduced all five lanes and emitted
`toxsync-source-matrix=pass`. The pinned Nix derivation built successfully as `toxsync-0.7.0`.

Local raw transcript digests at qualification time were:

```text
cd7317dbbd1941a7f7e502d40eaa9c4839baa49941e417813e5d35dfdcf9b83b  rev0039-import-final-matrix.log
76cb4b13040c6f7c35cde92178f322802e4f3ce643ca4ce66035b5d865200470  rev0039-import-fuzzer-smoke.log
61173c79a72d4ef784b531e8a285e08e9a50ad8ea4cd7c349d5377c2ea55604b  rev0039-import-focused-static-analysis.log
7b3eff27be6817be754aa2f98700f452870a1191749e30e50982233f54b3c59f  rev0039-import-baremetal-ctest.log
```

These raw logs are local ignored build evidence, not tracked release artifacts. The source and exact
claims in this report are durable; a distributable evidence bundle must regenerate and retain its own
transcripts from the cited commit.

## Capability gaps and nonclaims

Five private-cgroup process routes skipped by their explicit code-77 capability contract in each
applicable lane: lifecycle recovery, memory/PID resources, CPU resources, I/O resources, and PSI
admission/trigger registration. This host did not provide the exclusive writable delegated cgroup-v2
root those positive oracles require. Their pure policy, parser, state-machine, startup-refusal, and
mock-backed paths passed; positive live controller and PSI-trigger delivery remain unclaimed.

This qualification also does not establish genuine two-host Ratox keypress latency, bulk
interference, physical-host fault behavior, or two-host toxsync convergence. Toxsync is qualified as a
transport-neutral component but is not linked into the IoTox daemon. Its authority, persistence,
framing, worker, and activation integration is deliberately gated by
`docs/toxsync-integration-plan.md`.
