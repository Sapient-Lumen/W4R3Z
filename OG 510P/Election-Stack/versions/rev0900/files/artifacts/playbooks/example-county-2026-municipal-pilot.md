# Example County 2026 Municipal synthetic pilot playbook

This playbook ties the v824 example packets into one synthetic Track A path. It is not live evidence.

1. Verify `artifacts/examples/evidence_packet_election_parameters_bundle_minimal`.
2. Verify `artifacts/examples/evidence_packet_witness_set_minimal`.
3. Verify `artifacts/examples/evidence_packet_public_notice_feed`.
4. Verify `artifacts/examples/evidence_packet_results_closeout_index_minimal`.
5. Simulate a key issue with `artifacts/examples/evidence_packet_incident_key_compromise_event_minimal` and `artifacts/examples/evidence_packet_witness_set_change_minimal`.
6. Record the exercise in `artifacts/registries/drill-runs.csv`.
7. Replace all placeholder digests and unsigned signatures before any live pilot claim.
