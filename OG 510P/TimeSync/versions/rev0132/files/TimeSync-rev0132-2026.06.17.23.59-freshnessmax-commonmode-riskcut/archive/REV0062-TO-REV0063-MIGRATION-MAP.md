# Migration map — rev0062 to rev0063

## Conceptual migration

rev0062 had mature semantic objects but no concrete carriage wrapper. rev0063 adds one thin layer below semantics.

```text
rev0062 semantic object
  -> rev0063 transport envelope
       adapter metadata
       semantic_payload = unchanged rev0062 object
```

## Files added

```text
spec/18-minimal-transport-envelope.md
spec/19-adapter-binding-catalog.md
spec/20-retained-export-envelope.md
spec/21-transport-security-boundaries.md
spec/22-adapter-decision-table.md
transport/adapter-catalog.json
transport/ADAPTER-CATALOG.md
schema/transport-envelope.schema.json
schema/transport-adapter.schema.json
schema/transport-adapter-catalog.schema.json
schema/transport-capability.schema.json
schema/retained-export.schema.json
examples/transport/*.json
```

## Files changed

```text
README.md
START_HERE.md
INDEX.md
CHANGELOG.md
REVISION-RECEIPT.json
frontier-ticket.json
tests/acceptance-tests.yaml
tests/acceptance-tests.md
tests/semantic-test-vectors.yaml
tests/TRACEABILITY-MATRIX.md
tools/validate_archive.py
VALIDATION-REPORT.md
MANIFEST.json
```

## No semantic migration required

Existing rev0062 TimeState, wire claim, local assessed state, profile assessment, discovery request/result, and profile catalog objects remain valid.

To carry one over a boundary, wrap it as:

```json
{
  "envelope_version": "1.0",
  "message_type": "local_assessed_state",
  "adapter": { "id": "timesync.adapter.telemetry-push", "carrier": "telemetry_stream", "mode": "out_of_band_push", "binding_strength": "authenticated_transport" },
  "semantic_payload": { }
}
```

The nested `semantic_payload` is the unchanged rev0062 object.
