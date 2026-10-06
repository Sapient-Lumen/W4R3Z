# RFC-0084: Witness rebuilders and diffoscope integration

Status: Draft

## Summary

Add an optional independent verification lane:
- require N witness rebuild attestations for promotion
- when witnesses disagree, produce deep diffs (diffoscope-style) as evidence objects

References:
- diffoscope: https://diffoscope.org/
- rebuilderd: https://github.com/kpcyrd/rebuilderd

## Goals

- Strengthen “treat builders hostile” posture.
- Make divergence explainable, not mysterious.

## Design sketch

- Witness builders rebuild from Plan digest.
- Emit DSSE/in-toto witness attestation bound to artifact digest.
- If mismatch: store a diff report object; expose summaries via JSON.

See: `docs/116-witness-rebuilders-diffoscope.md`.
