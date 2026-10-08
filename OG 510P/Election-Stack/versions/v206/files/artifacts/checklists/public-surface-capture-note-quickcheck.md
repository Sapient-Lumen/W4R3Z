# Public-surface capture note quickcheck

Use this when a dispute bundle needs raw-capture provenance without shipping huge bodies.
See: `DOC:docs/223-public-surface-capture-notes-and-reproducibility.md`.

## Must be true
- [ ] The note identifies **surface_kind + stable_target** (per `DOC:docs/201-public-surface-parity-snapshots.md`).
- [ ] The note identifies the **official channel** (`channel_id` from `artifacts/registries/official-channels.csv`).
- [ ] The note includes `fetched_at_utc` in **UTC**.
- [ ] The note records `time_source` and `time_uncertainty` (or explicitly states `unknown`).
- [ ] The note includes `tool` and `tool_version`.
- [ ] The note records a bounded **request context** line (prefer canonical `req[...]` format; UA class, language (primary tag only), cache-bypass attempt, and cookie presence) or explicitly states `unknown` (see `DOC:docs/224-request-context-and-variant-probing-for-public-surfaces.md`).
- [ ] The note includes **both** `body_sha256` and `capture_file_sha256`.
- [ ] If any transform occurred (decompression/normalization), the note pins **both digests** and describes the transform.
- [ ] The note contains **no secrets** (cookies, tokens, auth headers). If edits were required:
  - [ ] it cites `CHECK:artifacts/checklists/public-artifact-redaction-checklist.md`.
  - [ ] if the edit produced a published derivative, the bundle includes `redaction-log.md` (see `DOC:docs/225-redaction-logs-and-transformation-accountability.md`).

## Should be true
- [ ] If wall-clock time is load-bearing for the claim, the note includes a time proof pointer (e.g., `time_proof_digests` or a cited `hfv.time.beacon`) per `DOC:docs/192-time-attestation-and-timestamping-as-evidence.md`.
- [ ] The note includes a minimal DNS/TLS context line (or explicitly says `none`).
- [ ] If available, the note records response variance hints (`Vary` / `Age`) in canonical compact form (`vary[lowercase,comma-separated,no-spaces] age[int_seconds]`) to support split-view root-cause analysis.
- [ ] The note points to the related parity snapshot digest (if present).
- [ ] The claim card (`claim.md`) cites the capture note (path + digest pins) in “Evidence present.”
