# PublicNotice divergence dispute bundle checklist (bounded)

**Track:** Shared (cross-cutting)


Use when official channels do not converge on the same “current state” outside the holdback window (`221`).

- ☐ Freeze the **time window** (start/end) and record the **holdback policy** used (`221.4`).
- ☐ Capture ≥1 `hfv.public.surface_parity_snapshot` for:
  - `public_notice_feed_latest`
  - any user-facing comms/status surface implicated (`195`, `201`)
- ☐ Record a bounded request context (UA class / language / cache-bypass / cookie presence) for each divergence observation per `DOC:docs/224-request-context-and-variant-probing-for-public-surfaces.md` (prefer `capture-note.md` or `observations[].notes`).
- ☐ If you retained raw HTTP capture bytes to defend the snapshot computation, include a small `capture-note.md` per `DOC:docs/223-public-surface-capture-notes-and-reproducibility.md` (template: `TEMPLATE:artifacts/templates/public-surface-capture-note.md`).
  - Start `observations[].notes` with `surface_effective_state_divergence` when applicable (`docs/SURFACE_ANOMALY_CODES.md`).
- ☐ If any evidence-relevant exhibit was redacted/transformed for publication, include `redaction-log.md` (template: `TEMPLATE:artifacts/templates/redaction-log.md`; quickcheck: `CHECK:artifacts/checklists/redaction-log-quickcheck.md`; spec: `DOC:docs/225-redaction-logs-and-transformation-accountability.md`).
- ☐ Include the `hfv.public.notice_feed` envelope(s) for each official channel involved (`200`).
- ☐ Include all referenced `hfv.public.notice` envelopes needed to compute effective state (`186`, `220`).
- ☐ Draft `claim.md` using `artifacts/templates/claim-card.md`:
  - cite boundaries (`166`/`167`)
  - tag load-bearing statements `[TAG|CONF]` (`218`)
  - list heads as `(notice_id, sha256)` pairs (bounded).
- ☐ Publish a bounded incident `hfv.public.notice` that cites snapshot digest(s) and commits to next update (`219`).
- ☐ Package using canonical layout (`173`), then verify:
  - `Verify: python3 tools/observer_verify_packet.py <packet_dir>`
  - `Lint (publishable): python3 tools/observer_verify_packet.py <packet_dir> --lint-public` (or `python3 tools/public_artifact_lint.py --packet <packet_dir>`)
- ☐ (Recommended) Generate a digest-only public fingerprint for mirroring/comparison:
  - preferred (stable file output): `python3 tools/public_fingerprint_report.py <packet_dir> --write-default --stable`
  - or one-command: `python3 tools/observer_verify_packet.py <packet_dir> --lint-public --public-fingerprint --public-fingerprint-out public-fingerprint.json --public-fingerprint-stable`
  - reviewer verify shipped fingerprint matches bytes: `python3 tools/observer_verify_packet.py <packet_dir> --lint-public --verify-public-fingerprint`
  - if comparing two copies: `python3 tools/compare_public_fingerprints.py <packet_a_dir> <packet_b_dir>`
- ☐ Ship `hfv.verifier.packet_verification_report` for the packet (`193`).