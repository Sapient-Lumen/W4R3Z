# Scenario — advisory + pubtime + docs build drift generate a recheck ticket

This scenario proves that a worthy front-door crate should not wait for a full manual repo refresh before reopening review.

Three later facts arrived:
- a candidate crate received a new release with a fresh `pubtime`,
- a security signal changed,
- and the hosted docs/support story shifted.

The correct `0.1` output is **not** “pick a new winner automatically”.
It is one compact **recheck ticket** that:
- references the frozen basis,
- records the trigger set,
- recommends the next packet family,
- and preserves a manual-review ceiling.
