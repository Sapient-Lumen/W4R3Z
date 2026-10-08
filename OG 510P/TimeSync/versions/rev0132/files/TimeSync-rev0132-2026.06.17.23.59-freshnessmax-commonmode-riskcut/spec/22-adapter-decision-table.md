# 22 — Adapter decision table

## Use the smallest adapter that fits the boundary

| Boundary need | Preferred adapter mode | Typical payload | Notes |
|---|---|---|---|
| Source emits only a time assertion | `in_band_claim` | `wire_claim` | Receiver still performs local assessment. |
| Operator or peer asks for optional items | `out_of_band_pull` | `discovery_request`, `discovery_result` | Flat request/result surface only. |
| Device publishes current assessed state | `out_of_band_push` | `local_assessed_state` | Telemetry timestamp is not TimeState freshness. |
| Relay terminates and restates state | `relay_boundary` | `local_assessed_state` | Use `boundary_context.action = restate` or downgrade as applicable. |
| Audit package leaves configured boundary | `detached_export` | `retained_assessment_export` | Requires retained state and profile-reference strength appropriate to boundary. |
| Schema or validator fixture | `test_fixture` | any message type | Not a deployment claim. |

## Do not promote carrier features into TimeState

Carrier feature:

```text
TLS session
management API identity
stream offset
file creation time
payload signature
message sequence number
```

Allowed use:

```text
access control
correlation
integrity
operational troubleshooting
fixture validation
```

Disallowed use by itself:

```text
freshness
traceability
profile satisfaction
applicability upgrade
fallback justification
```

## Cross-boundary export rule

When a payload leaves a configured or authenticated local context, the profile reference must be strong enough for the receiver's boundary. The adapter can carry the reference; it cannot make a weak reference strong.

## Adapter escalation rule

If a carrier needs protocol-level behavior such as negotiation, retransmission, path measurement, grandmaster selection, leap handling, or clock discipline, that belongs to the carrier or a separate protocol. It should not be added to the TimeSync envelope.
