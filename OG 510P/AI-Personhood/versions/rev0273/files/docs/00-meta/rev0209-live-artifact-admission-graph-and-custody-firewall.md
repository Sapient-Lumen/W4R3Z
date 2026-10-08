# rev0209 live artifact admission graph and custody firewall

rev0209 targets the most dangerous remaining gap: a first real artifact could still be mishandled by creating a response, intake, envelope, or import gate through a parallel path rather than through LEAP and raw custody.

The revision adds an executable admission graph: **LEAP -> custody -> response -> intake -> non-host envelope/import gate -> computed floor**. The graph has no live-floor effect. It exists to block shortcuts.

## Operational changes

- `schemas/external-receipt-response-record.schema.json` now requires `linked_live_evidence_acquisition_packet_ref` and `linked_custody_record_ref` when `response_state` is `actual-response-received`.
- `schemas/external-receipt-intake-record.schema.json` now requires the same lineage when `receipt_state` is `actual-external`.
- `schemas/nonhost-response-artifact-envelope.schema.json` now requires LEAP and custody lineage for `artifact_mode=live-counterparty`.
- `schemas/actual-receipt-import-gate.schema.json` now requires `source_provenance.linked_live_evidence_acquisition_packet_ref` and `source_provenance.custody_record_ref` for `actual-live-import`.
- `schemas/live-evidence-acquisition-packet.schema.json` now has conditional admission states: candidate/admitted states must prove raw custody, request trace, non-host retention, cryptographic binding, authority, and independence before downstream locks can release.

## Executable surfaces

- `tools/build_live_artifact_admission_graph.py` computes the graph and writes `examples/live-artifact-admission-graph-rev0209.json`.
- `tools/audit_live_artifact_admission_graph.py` validates the graph, probes the downstream schemas, and verifies the negative fixtures are registered.
- `fixtures/negative-tests/live-artifact-admission-graph-response-before-custody.json` blocks actual-response creation before raw custody.
- `fixtures/negative-tests/live-artifact-admission-graph-import-without-leap.json` blocks actual-live import without LEAP/custody provenance.

## Current decision

No actual live external artifact is present. LEAP remains `ready-no-live-artifact`. The admission graph reports downstream creation blocked and the computed live receipt floor remains zero.

The next real action is not another registry expansion. It is to receive one genuine raw counterparty artifact and force it through the graph. If any edge is missing, the artifact is rejected or quarantined with a failed-gate public shell.
