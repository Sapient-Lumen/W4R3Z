# amqpbundle

Evidence bundles for AMQP 1.0 scenarios, canonical transcripts, and conformance results.

## Suggested top-level files

- `manifest.json`\n- `scenario.yaml`\n- `transcript.json`\n- `fingerprints.json`\n- `divergences.json`\n- `repro.yaml`\n- `redaction.json`\n

## Notes

- Bundles should be **redactable by default** and signable via Evidence Bundle Core (P-0256).
- Prefer canonical, diffable formats; avoid raw pcap unless needed.
