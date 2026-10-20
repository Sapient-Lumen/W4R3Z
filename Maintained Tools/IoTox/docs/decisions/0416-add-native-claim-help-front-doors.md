# ADR 0416: Add native claim/help front doors

Date: 2026-10-01

## Status

Accepted.

## Context

IoTox has become broad enough that the most confusing commands are no longer
the raw sync or terminal mutations. The confusing layer is the claim layer:
routes, evidence, shipping, and support. Operators can already ask
`readiness`, `ship-check`, `evidence collect`, `route-qualification-check`, and
`support-bundle` questions, but the short native help topics did not yet teach
how those pieces relate.

That gap makes two bad mistakes more likely:

- a human treats a working demo or route connection as a product claim; or
- a human exports diagnostics/evidence without understanding what the artifact
  does not prove.

The existing `iotox help` split made the root help calm and moved exhaustive
inventory to `iotox help all`. The next coherence step is to make the claim
layer discoverable without sending the user into long docs first.

## Decision

Add four binary-native help topics:

```sh
iotox help routes
iotox help evidence
iotox help shipping
iotox help support
```

Each topic is read-only and recipe-first. Each prints exact commands and the
nonclaim that prevents the topic from becoming invisible authority:

- `routes` points to route readiness and qualification checks while repeating
  that native/Tor/I2P are explicit route classes with no silent fallback or
  anonymity certification.
- `evidence` explains dossier planning, sync and terminal evidence collection,
  manifest creation, and stable ship-check consumption while repeating that
  evidence collectors shape-check receipts rather than creating truth.
- `shipping` explains stable versus founder-preview `ship-check` and the repo
  datacube handoff while repeating that packaging is distribution, not proof.
- `support` explains support-bundle plan/create/inspect and diagnostics export
  while repeating that content-free is not information-free.

Keep the exhaustive command list in `iotox help all`; do not re-expand root
help into a wall.

## Consequences

- Product-claim surfaces are now as discoverable as sync, Ratox, pairing, self,
  and person surfaces.
- A reviewer can start from the binary for “what can I claim?” before reading
  `docs/ship-readiness.md` or `docs/stable-release-evidence.md`.
- The help text remains non-authoritative: it teaches commands, but readiness,
  evidence, route, support, and shipping commands still own their receipts and
  pass/fail results.
- Root help stays short; `help all` remains the full inventory.

## Tests

- `cmake --build build --target iotox iotox_tests -j2`
- `ctest --test-dir build -R 'iotox\.(client-help|client-version|client-absent-daemon|human-cli|docs-coherence)' --output-on-failure`
