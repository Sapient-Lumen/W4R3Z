# Audit — rev0108 transport capability claim refactor

rev0108 continues FT-0090 with executable validation work only. The six-field TimeState core is unchanged.

## Risk selected

The riskiest remaining non-temporal seam was transport capability metadata. Capability advertisements are descriptive, but before rev0108 they could claim support for profile references or request items without those claims being checked against the adapter catalog or profile catalog.

The dangerous cases were small but important:

- `supported_profiles` could name a profile that is absent from the profile catalog.
- `requestable_items` could include private or non-TimeSync material such as `source_roster`.
- an adapter whose catalog policy says `may_carry_profile_reference: false` could still advertise supported profile references in capability metadata.

That creates a misleading capability surface. It does not directly mutate TimeState, but it can steer downstream request construction and review assumptions toward material the adapter/profile boundary does not actually permit.

## Executable change

Added:

```text
tools/transport_capability_semantics.py
```

The helper now checks capability advertisements against:

```text
transport/adapter-catalog.json
profiles/profile-catalog.json
TimeSync assessment/request item vocabulary
```

It rejects:

```text
supported_profiles not resolvable in the profile catalog
requestable_items outside the TimeSync assessment/request vocabulary
requestable_items not supported by any advertised profile obligation/default/requestable surface
supported_profiles on adapters whose profile_reference_policy forbids profile references
unsupported message types for the advertised adapter
incomplete negative_result_statuses
```

## Refactor effect

`tools/validate_archive.py` no longer owns the transport capability message-type and negative-status checks inline. It delegates capability semantics to the new helper.

This keeps the work in the current FT-0090 pattern: smaller validator branches, targeted helper self-tests, and no new registry layer.

## Fixtures

Added three derivation-checked negatives:

```text
examples/negative/transport-capability-unknown-profile-invalid.json
examples/negative/transport-capability-unknown-request-item-invalid.json
examples/negative/transport-capability-profile-ref-forbidden-adapter-invalid.json
```

Added semantic vectors:

```text
TV-N292
TV-N293
TV-N294
```

Added fixture derivations:

```text
DF-0108-001
DF-0108-002
DF-0108-003
```

## Boundary preserved

rev0108 does not create a capability negotiation protocol, a transport registry, or a profile credential system. A capability advertisement remains descriptive. The new check only prevents descriptive metadata from overstating adapter/profile surfaces.

## Remaining work

FT-0090 should remain open. The next pass should continue to extract validator concern families only when that extraction makes executable behavior smaller or harder to misuse. Candidate areas include digest-binding policy validation, semantic-version policy validation, and selected aggregate/replay fixture-family derivations.
