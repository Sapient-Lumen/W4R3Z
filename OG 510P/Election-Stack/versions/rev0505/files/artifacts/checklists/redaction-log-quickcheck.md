# Redaction log quickcheck (bounded)

**Track:** Shared (cross-cutting)


Use this when a bundle publishes any redacted/transformed evidence-relevant artifact.
See: `DOC:docs/225-redaction-logs-and-transformation-accountability.md`.

## Must be true
- [ ] `redaction-log.md` exists **only if** redactions/transforms were used.
- [ ] Each entry has **both** `source_sha256` and `derived_sha256`.
- [ ] Each entry states a bounded `transformation` and a bounded `reason`.
- [ ] No entry includes the removed bytes (no “before/after” secret strings; no pasted PII).
- [ ] `source_path` / `derived_path` are bundle-relative (do not leak private infrastructure paths).
- [ ] If the source bytes are sealed/private, the log says so (digest-only is acceptable).

## Should be true
- [ ] The claim card (`claim.md`) cites `MANIFEST:redaction-log.md` and lists any load-bearing `RED-###` IDs.
- [ ] If the redaction involved capture notes or public-surface artifacts, the log cites `CHECK:artifacts/checklists/public-artifact-redaction-checklist.md`.
- [ ] If multiple people reviewed the redaction, `review=two_person` is used.
