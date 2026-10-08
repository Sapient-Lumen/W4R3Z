# TimeSync rev0126 audit — liveharness-sourcestats-riskcut

## Risk selected

The riskiest incomplete area after rev0125 was not another profile registry. It was the remaining gap between a replayable chrony adapter and a live command transcript path. Without exercising the subprocess capture path, future live-capture failures could hide behind replay fixtures.

A second risk was partial implementation of the FT-0121 evidence surface. The frontier asked for tracking, sources, and sourcestats. Only tracking and sources were retained before rev0126, leaving estimator diagnostics out of the vertical slice and inviting a later untested parser.

## Changes made

- Added `sourcestats` as a required command role in `tools/chrony_capture.py`.
- Regenerated `tests/fixtures/chrony/capture-normal.json` with the `sourcestats` command and a longer deterministic monotonic bracket.
- Added `examples/chrony/sourcestats-normal.txt` and `tests/fixtures/chrony/observation-sourcestats-normal.json`.
- Added sourcestats parsing to `tools/chrony_adapter.py` while keeping it out of P1 lane selection.
- Added a fake-live harness to `tools/chrony_capture.py --self-test`, using a temporary `chronyc` executable to drive the real subprocess runner.
- Added `CHRONY-P1-SOURCESTATS-DIAGNOSTIC-CAPTURED` and semantic vector `TV-126-001`.
- Extended the RFC 9249 crosswalk with sourcestats estimator fields, classifying them as non-core adapter diagnostics.

## Audit/refactor result

The key refactor is in the capture boundary: capture roles are now the source of truth for replay extraction, and the fake-live harness proves the command path without relying on a host chronyd installation.

Sourcestats parsing is intentionally placed in `chrony_adapter.py`, not in `chrony_policy.py`. This keeps policy from becoming a dump for implementation-specific measurement state. P1 still evaluates the tracking-derived conservative bound plus replay growth.

## Severe/wasteful issue corrected

The project was at risk of repeatedly polishing replay objects while the live command path remained untested. The fake-live harness corrects that waste by making the subprocess path part of normal validation. It is not a substitute for real chronyd evidence, but it removes a class of avoidable glue failures before a real host run.

## Still open

- The live path is exercised through a fake `chronyc`, not a real chronyd/chronyc host.
- NTS and symmetric-key authentication are not verified.
- UTC is chrony-reported and unqualified; named UTC realization is not proven.
- Leap-smear policy discovery is not implemented.
- RFC 9249 remains a comparison guard, not proof of interoperability.
- Sourcestats is diagnostic-only; it does not yet feed a separate estimator-quality policy.
