# Public artifact redaction checklist (bounded, publishable)

**Track:** A (Deployable core)

Use this checklist **before publishing** packets, digest cards, or monitor reports to a public surface.

## Principles (do first)
- Prefer **hashes-first** (SHA-256 digests + byte lengths) over raw bodies.
- Prefer **stable targets** (e.g., `subject.stable_target`) over full URLs.
- Prefer **structured anomaly codes** over narrative in `notes`.

## Checklist
- [ ] **No voter identifiers:** no per‑voter IDs, tokens, receipts, or voter-linked metadata (docs/173).
- [ ] **No network identifiers:** remove/avoid IP addresses, full user agents, device IDs; keep only coarse vantage if necessary.
- [ ] **Use documentation placeholders in examples:** prefer RFC-reserved example IPs/domains over real identifiers (DOC:docs/189-sensitive-material-and-secrets.md).
- [ ] **Request-context notes are coarse:** if you include compact `req[...] vary[...] age[...]` notes (see `DOC:docs/232-compact-request-context-notes.md`), use UA *classes* (not full UA strings), ensure `cookie=none|present_redacted` (never values), and keep `vary[...]` canonical (lower-case, comma-separated, no spaces) and `age[...]` as integer seconds. Do not paste `Cookie:` or `Authorization:` headers.
- [ ] **No secrets / tokens:** strip query params, fragments, auth headers, cookies, bearer tokens, CSRF tokens.
- [ ] **Bound URLs:** if a URL must be shown, remove query/fragment; prefer `stable_target` + channel label.
- [ ] **Bound headers:** include only freshness/identity subset when relevant (ETag, Cache-Control, Age, Last-Modified) and truncate long values (docs/210, docs/205).
- [ ] **Avoid raw bodies:** do not publish response bodies by default; publish `body_sha256` + `content_type` + `http_status`.
- [ ] **If a body is crucial:** publish **the smallest possible excerpt** and document the redaction rationale; never include secrets or PII.
- [ ] **If you produced a redacted/edited derivative:** include `redaction-log.md` (template: `TEMPLATE:artifacts/templates/redaction-log.md`) with source/derived digests and run `CHECK:artifacts/checklists/redaction-log-quickcheck.md` (see `DOC:docs/225-redaction-logs-and-transformation-accountability.md`).
- [ ] **Notes discipline:** when describing public-surface anomalies, prefer codes from `artifacts/registries/surface-anomaly-codes.csv`; keep freeform notes short and non-identifying.
- [ ] **Run the publishable lint:** `python3 tools/observer_verify_packet.py <PACKET_DIR> --lint-public` (or `python3 tools/public_artifact_lint.py --packet <PACKET_DIR>`) must exit 0. It FAILs on obvious body/capture fields and secret-token markers; it WARNs on likely PII literals (IPs/emails/phones/coords) and unbounded request-context hints.
- [ ] **If a WARN is load-bearing:** document the minimization + justification in `redaction-log.md` and (rarely) add `lint-allow: <code>` to suppress that WARN for the packet (WARN-only; FAIL is never suppressed).
- [ ] **Run a drift check:** render digest cards (`tools/*_card.py`) and ensure payload/TBS recomputation matches declared digests.
- [ ] **Run archive safety checks:** at minimum `scripts/check_no_private_keys.py` and the full `scripts/release_gate.py` for releases.

## Where this matters most
- Public surfaces: well‑known discovery, official channel directory, notice feed, signing keyset (docs/200–205).
- Monitoring artifacts: `PublicSurfaceParitySnapshot` (docs/201) and `LivenessBeacon` (docs/210).
- Bundles: offline verifier bundles and long-term mirrors (docs/92, docs/98).
