# Scenario — hidden obligations from `build.rs`, `links`, and proc macros

This scenario exists to force **P-0510** to keep separate:

- the crate’s stated support profile,
- hidden adoption obligations,
- public interop value,
- and raw functionality.

## Why it matters

A crate may be otherwise attractive but still impose non-trivial downstream costs through build scripts, native linkage, proc macros, or workspace metadata inheritance.
Those are often visible in Cargo/docs surfaces, but they are rarely joined into one downstream-facing support contract.

## Expected artifact pressure

- `support-obligation.receipt.json` should record `build_script_present`, `native_links_present`, and `proc_macro_present` with explicit origins.
- `claim-class.policy.json` should prevent those obligations from being silently downgraded into inferred trivia.
- `profile-fidelity.report.json` should make it possible for a crate’s functional claims to be `fully_observed` while its adoption-cost story remains only `mostly_observed` or `manual_review_required`.
