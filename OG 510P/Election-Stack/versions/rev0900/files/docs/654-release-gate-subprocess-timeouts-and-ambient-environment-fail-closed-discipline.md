# 654. Release-gate subprocess timeouts and ambient-environment fail-closed discipline

**Track:** Shared / Release engineering

This document records the v781 reconstruction pass for release-gate execution hygiene. It is a maintainer-control document, not a new voter-facing evidence surface.

## Audit finding

The archive has grown a broad release gate, and several gate steps invoke helper tools or verifier tools as subprocesses. Before this revision, the top-level gate did not set a per-step timeout. A reviewer environment with an ambient Python startup hook, a blocked import, a stuck subprocess, or a tool regression could hang the whole release gate instead of producing a bounded failure.

That is a release-control weakness even when the underlying content is correct. A gate that can hang silently is not a gate; it is an invitation to bypass the gate under deadline pressure.

## Reconstruction rule

`Release gate completion` is now part of the evidence-control surface.

The top-level runner must fail closed when a child step exceeds a bounded time budget. A timeout is not success, and it is not a warning. It is a release failure with the timed-out command printed so the maintainer can reproduce or isolate the hang.

The default step budget is intentionally modest and configurable:

- default: `60` seconds per step;
- override: `ELECTION_STACK_RELEASE_STEP_TIMEOUT=<seconds>`;
- behavior: timeout returns release-gate failure, preserving any captured stdout/stderr when available.

This is a harness-level guardrail, not a replacement for tool-specific regression tests.

## Scope boundaries

This pass does not add network fetching, source downloading, or bundled third-party artifacts. It also does not promote a new voter-facing surface. The change is a release-engineering containment rule: the archive may keep accumulating checks, but each check must remain bounded and reviewable.

Do not use the timeout as a license to add slow checks. Long-running source refresh, web retrieval, or large-download verification belongs outside the default release gate unless it is explicitly marked as an operator-chosen audit mode.

## Failure taxonomy

Treat timeout failures as one of four bounded causes:

1. **Ambient environment interference:** local Python startup, user-site packages, shell hooks, antivirus, filesystem sync, or similar environment effects change tool startup behavior.
2. **Unbounded subprocess drift:** a check invokes a helper without its own timeout and the helper blocks.
3. **Accidental network dependency:** a nominally local check begins waiting on a URL, DNS, certificate path, or remote schema.
4. **Algorithmic blow-up:** a scanner becomes quadratic or worse as the archive grows.

The maintainer response is to shrink or isolate the check, not to increase the archive's copied evidence bodies.

## Compression posture

This revision adds one compact control document and one small harness change. It deliberately avoids a new sibling doc for each subprocess-using checker. If future gate hangs appear, add a row or note here, patch the specific tool, and keep the rule centralized. The v782 follow-on in `docs/655-release-gate-failure-locality-failfast-and-manifest-write-quarantine.md` adds fail-fast default behavior and manifest-write quarantine so a bounded failure is reported at the point of failure rather than buried behind later checks.

## Internal anchors

- `scripts/release_gate.py`
- `scripts/check_example_packets.py`
- `scripts/check_operator_tools_smoke.py`
- `scripts/check_packet_verification_report_linkage.py`
- `scripts/check_packet_verification_report_emit_packet.py`
- `scripts/check_public_surface_pins_coverage.py`
- `docs/162-release-and-ci-evidence-pipeline.md`
- `docs/653-source-reference-parser-lockfile-closure-and-xref-reconstruction.md`
