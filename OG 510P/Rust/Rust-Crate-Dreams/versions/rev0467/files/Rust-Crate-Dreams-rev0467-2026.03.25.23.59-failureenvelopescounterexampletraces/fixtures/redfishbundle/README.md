# redfishbundle

Evidence bundles for Redfish schema versions, service snapshots, and conformance runs.

## Suggested top-level files

- `manifest.json`\n- `schema.lock`\n- `snapshot.json`\n- `conformance.json`\n- `diff.json`\n- `repro.yaml`\n- `redaction.json`\n

## Notes

- Bundles should be **redactable by default** and signable via Evidence Bundle Core (P-0256).
- Prefer canonical, diffable formats; avoid raw pcap unless needed.
