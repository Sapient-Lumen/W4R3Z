# ADR 0418: Align explain topics with human help porches

Status: accepted

Date: 2026-10-01

## Context

IoTox has grown a native human porch: `iotox help quickstart`, `help sync`,
`help terminal`, `help pairing`, `help service`, `help self`, `help person`,
`help routes`, `help evidence`, `help shipping`, `help support`, and
`help storage-readiness`. Those commands tell a human what to try first.

`iotox explain TOPIC` originally focused on refusal classes such as invalid
namespaces, route fallback, missing libsodium, and precious-data readiness. That
was useful after an error, but it created a sharp edge: a human could type
`iotox help sync` successfully, then reasonably try `iotox explain sync` and get
an unknown-topic error.

## Decision

The binary-native `iotox explain` table now includes the same porch-level topics
as `iotox help`:

- `quickstart`
- `sync`
- `terminal`
- `pairing`
- `service`
- `self`
- `person`
- `routes`
- `evidence`
- `shipping`
- `support`
- `storage-readiness`

Each record carries the same structured fields as the stricter refusal records:
`problem`, `why`, `safe-next`, `doc`, and `boundary`.

## Consequences

Human-facing help is now coherent:

- `iotox help TOPIC` shows the recipe.
- `iotox explain TOPIC` explains why the recipe is shaped that way.
- `iotox explain last` remains explicit about not inventing a hidden stderr log.

The table is regression-tested in `tests/test_human_cli.py` so future CLI polish
does not drift back into "known in help, unknown in explain."
