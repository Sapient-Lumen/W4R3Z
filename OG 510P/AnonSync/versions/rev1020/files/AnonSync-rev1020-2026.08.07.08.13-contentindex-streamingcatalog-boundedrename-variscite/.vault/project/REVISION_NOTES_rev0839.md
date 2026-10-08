# AnonSync rev0839

## Mission increment

A daemon may be replaced only when evidence says that its durable authority is no
longer live **and** the exact recorded process incarnation is no longer present. A PID
and a stale wall-clock deadline are observations, not takeover authority.

## Delivered

- New typed `sync_process_identity_observation` C++ leaf.
- Linux PID + boot UUID + `/proc` starttime observation with bounded canonical parsing.
- Optional pidfd polling for supported kernels; explicit typed fallback and failure.
- Windows PID + process creation FILETIME implementation path.
- Heartbeat schema v2 with exact nested/top-level PID relationship.
- Legacy v1 downgrade fence: non-final PID-only evidence blocks service re-entry.
- Shared typed lifecycle evaluator used by both daemon preflight and operator status.
- Stale-but-exact-process-live fence.
- First-write process binding and later-write fork/inheritance mismatch rejection.
- Operator/API telemetry for match kind, liveness, exact match, boot/start material.
- Dedicated focused test and source/dependency audit.
- Permanent sanitizer compile/link parity audit after finding and fixing an omitted
  sanitizer-runtime link owner.
- Reduced focused dependency graph by removing an unused inherited-process wrapper.
- Quiescent exact-range validation protocol after quarantining stale cloudtainer streams.

## Validation

- CTest: **131/131**
- Registered audit tests: **39/39**
- Process identity focused: **15/15**
- Heartbeat lifecycle focused: **55/55**
- Domain integration: **602/602**
- Focused repeat: **700/700**
- Process source audit: **27/27**
- Heartbeat source audit: **29/29**
- Clang 17 `-Werror`: **70/70**
- GCC 14 ASan+UBSan, leak detection enabled: **70/70**
- Source patch replay: **PASS** across 229 active files
- Parent: directory **21/21**, ZIP **25/25**

## Important interpretation

The new tuple is not an authentication credential. It is written to a document and can
be forged by anyone who can write that document. It supplements—but never replaces—the
exact durable owner-generation check. It primarily prevents unsafe optimistic takeover
when a stale daemon process remains alive and distinguishes straightforward PID reuse.

The running cloudtainer reports Linux 4.4 and returns `ENOSYS` for `pidfd_open`; runtime
validation therefore exercised the procfs fallback. Pidfd logic is source- and unit-
tested but not runtime-demonstrated here. The Windows branch was not compiled or run.

## Scope limits

No heartbeat authenticity, hard failure detector, full-project sanitizer, full Release
all-target build, arbitrary crash/power-loss completeness, Windows runtime result,
hostile-worker sandbox, distributed convergence proof, confidentiality, anonymity,
metadata hiding, key lifecycle, forward secrecy, post-compromise recovery, or secure
erasure is claimed.

## Handoff

See `REVISION_EVIDENCE/rev0839/AUDIT.md`, `RESEARCH.md`, `NEXT_WORK.md`, and
`validation/VALIDATION_SUMMARY.json`.
