# 225 — Redaction logs & transformation accountability (hashes-first, bounded)

**Track:** A (Deployable core)

Public election evidence often needs **redaction** (to remove secrets, PII, or sensitive operational details).
Redaction is necessary — but it creates a predictable dispute attack:

> “You edited the evidence.”

This doc defines a **small, hashes-first “redaction log” convention** that lets third parties audit *what was transformed* (and why)
without re‑publishing the removed material and without bloating bundles.

Related:
- Secrets policy (hard prohibitions): `DOC:docs/189-sensitive-material-and-secrets.md`
- Public redaction pre‑publish gate: `CHECK:artifacts/checklists/public-artifact-redaction-checklist.md`
- Claim cards (bundle boundary): `DOC:docs/217-claim-cards-and-traceability-minspec.md`
- Capture notes (raw fetch provenance): `DOC:docs/223-public-surface-capture-notes-and-reproducibility.md`
- Canonical packet layout: `DOC:docs/173-canonical-evidence-envelopes-and-packets.md`


## 225.1 The invariant

If any published/bundled artifact is **derived from** another artifact by redaction or transformation, you want a verifier to be able to say:

- *I can see the exact bytes that were published (digest).*
- *I can see the declared source bytes (digest), even if the source is sealed/private.*
- *I can see the declared transformation and the reason, in bounded text.*

A redaction log is not a general “chain of custody” system.
It is a narrow, publishable **anti‑tamper narrative** for edits you *must* do.


## 225.2 What counts as a “transformation” here

Include a log entry when you do any of the following to an evidence-relevant artifact:

- remove/blank sensitive strings (tokens, cookies, query params)
- redact PII (names, addresses, IDs)
- crop/blur a screenshot or image
- normalize/decompress bytes for analysis (when you also publish the normalized derivative)
- excerpt a small region of a larger body for publication

Do **not** log trivial formatting edits to your own prose docs.
Log transformations that affect **evidence bytes** or publishable supporting exhibits.


## 225.3 Redaction log minspec (keep it tiny)

Ship a single markdown file (recommended name: `redaction-log.md`).
Use the template:

- `TEMPLATE:artifacts/templates/redaction-log.md`

Each entry SHOULD include:

- `entry_id`: `RED-###`
- `source_path` (or an artifact token) + `source_sha256`
- `derived_path` + `derived_sha256`
- `transformation`: a bounded description (e.g., `crop + blur top-right region`)
- `tool`: e.g., `imagemagick 7.x`, `python script`, `manual blackbox`
- `reason`: e.g., `remove_cookie`, `remove_voter_identifier`, `remove_internal_endpoint`
- `review`: `self_reviewed|two_person|unknown` (bounded)

Hard rules:

- NEVER include the removed secrets/PII as “before/after” text.
- If the **source bytes are private/sealed**, you can still publish `source_sha256`.
- Prefer **one entry per published derivative** (not per tiny redaction step).


## 225.4 Integration points (where this belongs)

### A. Claim cards (`217`)

If redaction was involved in the bundle, `claim.md` SHOULD cite:

- `DOC:docs/225-redaction-logs-and-transformation-accountability.md`
- `MANIFEST:redaction-log.md`

…and (optionally) list the most load-bearing `RED-###` entry IDs.

### B. Capture notes (`223`)

If you edited a capture note command line or removed any context for publication:

- cite the redaction checklist, and
- add a redaction-log entry if the edit materially changes a published artifact.

### C. Divergence / split-view dispute bundles (`222`)

For disputes that may go adversarial (“you fabricated the screenshot / excerpt”),
include `redaction-log.md` so the bundle contains:

- published bytes (digests)
- declared source bytes (digests)
- the transformation intent + reason (bounded)


## 225.5 Size and safety discipline

- Keep the log to **one screen** per bundle when possible.
- Use **digests** and short reasons; do not paste bodies.
- Do not include internal filenames that leak private infrastructure; use bundle-relative paths.
- Run `CHECK:artifacts/checklists/redaction-log-quickcheck.md` before publishing.
