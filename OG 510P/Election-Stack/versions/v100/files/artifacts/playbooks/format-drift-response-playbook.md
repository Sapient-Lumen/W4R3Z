# Format drift response playbook

## When to use this
Use when independent verifiers disagree on hashes/digests for supposedly identical evidence objects, or when signatures stop validating due to serialization differences.

## Immediate actions (0–2 hours)
1. **Freeze publication:** stop producing new evidence objects until canonicalization is confirmed.
2. **Collect samples:** gather the conflicting objects (bytes) from each source, plus the tooling versions used to generate them.
3. **Compute a diff:** compare canonical bytes vs. pretty-printed bytes; identify which fields differ and whether differences are semantic or purely formatting.

## Triage
- If differences are **pure formatting** (whitespace, key order): treat as canonicalization pipeline failure.
- If differences are **semantic** (different values): treat as potential equivocation / corruption and escalate to fork/suppression procedures.

## Remediation
1. Re-issue a corrected packet using the canonicalization/signing rules in `docs/176`.
2. Publish an `EvidenceEnvelope` of kind `hfv.incident.format_drift` describing:
   - what diverged,
   - which artifacts are superseded,
   - which hashes should be treated as canonical going forward.
3. If any audience received only the broken artifacts, publish a suppression-style report explaining the corrective action.

## Prevention
- Keep payloads in I-JSON; prefer string ids.
- Run the offline verifier in CI (`tools/observer_verify_packet.py`).
- Require at least one **independent** verifier implementation to check digests before major releases.
