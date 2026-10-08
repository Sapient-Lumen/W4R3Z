# rev0019 audit/refactor notes

## Refactor focus

This revision adds a tail-contract patcher and updates current-revision outputs so dashboards can separate:

- direct catastrophic/tail metrics,
- surrogate tail contracts,
- non-lossy probes,
- probes that still need true hardening.

## Native posture

C++ remains source-only. Native audit syntax-compiles every `experiments/*/*.cpp`, inspects current-revision JSON outputs, verifies declared primary metrics, and rejects checked-in binaries.

## Known limitation

A surrogate tail contract is not evidence. It only prevents silent promotion of mean-only lossy probes.
