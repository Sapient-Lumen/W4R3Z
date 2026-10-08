# Scenario — public Tokio types leak a supposedly runtime-neutral async profile

This scenario exists to force **P-0511** to keep separate:

- the claimed shared ecosystem profile,
- the obligations needed to fit that profile,
- pairwise compatibility reality,
- and raw “these crates use the same broad ecosystem” vibes.

## Why it matters

A crate can use Tokio internally and still be runtime-neutral publicly, but once Tokio types or spawn handles leak into the public API the profile claim is no longer just an implementation detail.

## Expected artifact pressure

- `profile-class.policy.json` should allow the profile to stay an `ecosystem_boundary` while still requiring explicit manual review when public runtime coupling appears.
- `boundary-obligation.receipt.json` should record that runtime coupling must be explicit and show where the public leak was observed.
- `pair-fidelity.report.json` should make it possible for a static provider-only scan to stay weaker than a witnessed provider/consumer check.
