# spdmbundle

Evidence bundles for SPDM sessions and secured messaging transcripts.

## Suggested top-level files

- `manifest.json`\n- `transcript.json`\n- `capabilities.json`\n- `policy.json`\n- `divergences.json`\n- `repro.yaml`\n

## Notes

- Bundles should be **redactable by default** and signable via Evidence Bundle Core (P-0256).
- Prefer canonical, diffable formats; avoid raw pcap unless needed.
