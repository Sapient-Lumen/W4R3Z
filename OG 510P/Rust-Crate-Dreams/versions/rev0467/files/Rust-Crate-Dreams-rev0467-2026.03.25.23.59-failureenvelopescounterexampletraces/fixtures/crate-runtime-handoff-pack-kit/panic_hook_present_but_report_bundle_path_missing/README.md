# Scenario — panic hook exists but no report-bundle path is actually handed off

This scenario exists to force **P-0513** to keep separate:

- the fact that a custom panic hook was installed,
- the stronger claim that a support artifact path was really emitted,
- the share-safety class of that artifact,
- and the fidelity of the resulting panic handoff.

## Why it matters

A crate may already customize panic reporting, but users and support still need to know whether a file, URL, or stable bundle path was actually produced.
“Custom panic hook” is weaker than “panic handoff artifact exists and was witnessed”.

## Expected artifact pressure

- `capture-exactness.policy.json` should distinguish observed panic location/payload facts from merely declared report-path expectations.
- `share-safety.receipt.json` should classify whether the path or artifact is safe to publish, local-only, or omitted.
- `handoff-fidelity.report.json` should make it possible for panic support to stay weaker than a full runtime bundle when no report artifact path was actually witnessed.
