# Observer Kit (offline)

**Track:** Shared (cross-cutting)


This directory defines a portable evidence bundle format and a minimal offline integrity verifier.

Manifests are signed over RFC8785-JCS canonical bytes (see `docs/92-offline-verifier-bundle-spec.md`).

The goal is **portable, court-friendly integrity checking**: independent parties can verify that a bundle’s
contents match its manifest and that the manifest was signed by a known key.

This is intentionally **not** a full ballot-verification implementation.

See also:
- `docs/92-offline-verifier-bundle-spec.md`
- `docs/173-canonical-evidence-envelopes-and-packets.md`
- `docs/176-canonicalization-and-signing-rules-for-evidence-envelopes.md`
- `docs/177-observer-kit-offline-verification-walkthrough.md`
- `docs/179-evidence-api-surface.md`
- `docs/188-verifier-minimum-viable-path.md`
- `docs/track-a/VOTER_VERIFICATION.md` (what a voter can verify vs. what they delegate)
- `artifacts/templates/verifier-onboarding-mini-curriculum.md`
- `artifacts/playbooks/spec-error-response-playbook.md` (if verifier output disagrees / looks wrong)

Quick start:
```bash
python3 tools/offline_verifier.py .
```

Common usage:

- Verify the demo bundle:
  ```bash
  python3 tools/offline_verifier.py .
  ```

- Verify a bundle directory you received:
  ```bash
  python3 tools/offline_verifier.py /path/to/bundle
  ```

Replace the demo bundle contents with real election artifacts for your deployment, but keep the verifier
workflow stable: the verifier should be able to run **offline** on an air-gapped machine.
