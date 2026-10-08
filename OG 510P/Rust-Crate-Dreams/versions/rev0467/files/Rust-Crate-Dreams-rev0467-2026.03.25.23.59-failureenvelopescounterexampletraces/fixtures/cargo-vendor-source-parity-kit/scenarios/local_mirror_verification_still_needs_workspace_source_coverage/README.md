# Scenario — local mirror verification still needs workspace source coverage

This fixture exists to prove that **P-0496 Cargo Vendor & Source Parity Kit** must keep mirror verification and workspace-local source coverage separate.

The review question is not:
> “Did we import a trustworthy mirror receipt?”

It is:
> “Did the actual workspace resolution stay inside the covered mirror / vendored boundary?”

## What the scenario should force

- `mirror-verification.import.json` may say the mirror is cryptographically trustworthy.
- `source-origin.receipt.json` should still reveal path or git dependencies outside the covered mirror surface.
- `source-coverage.report.json` should classify the result as **partial** or **blocked** if uncovered sources remain.
- `vendor-parity.report.json` should refuse to turn imported trust into a fake full-parity verdict.

## Why it matters

Rust’s mirror-verification work is about proving that mirrors can serve unmodified crates.
That is valuable, but it is not the same as proving that a workspace used only covered mirrored sources.
