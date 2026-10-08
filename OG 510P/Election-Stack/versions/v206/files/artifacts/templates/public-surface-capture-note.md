# Public-surface capture note (hashes-first)

> Ship as `capture-note.md` alongside a parity snapshot / divergence bundle.
> Keep it small. Do not include secrets (tokens/cookies). Prefer digests over body copies.

## Subject
- surface_kind: `...` *(e.g., `public_notice_feed_latest`, `well_known_discovery`, `status_board`)*
- stable_target: `...` *(e.g., `/notices/feed/latest.json`)*
- channel_id: `...` *(from `artifacts/registries/official-channels.csv`)*
- retrieval_location: `...` *(bounded description; avoid raw URLs if publishing publicly)*

## Acquisition metadata
- fetched_at_utc: `YYYY-MM-DDTHH:MM:SSZ`
- time_source: `nts_ntp|roughtime|system_clock|unknown` *(cite `DOC:docs/192-time-attestation-and-timestamping-as-evidence.md` if relevant)*
- time_uncertainty: `±2s|±30s|unknown`
- tool: `curl|wget|other`
- tool_version: `...`
- command_summary: `...` *(omit auth headers; remove tokens; cite redaction checklist if edited)*

## Request context (bounded)
- ua_class: `...` *(coarse: `desktop_chrome`, `mobile_safari`, `cli_curl`, ...)*
- accept_language: `...|none` *(primary BCP47 tag only; omit q-weights)*
- cache_bypass: `none|no-cache|force-refresh`
- cookies: `none|present_redacted` *(never include values)*
- geo_hint: `country=US|region=US-CA|unknown` *(optional, coarse; avoid coords/IPs)*
- asn_hint: `asn=...|unknown` *(optional)*
- resolver_hint: `system_resolver|public_resolver|pinned_resolver|unknown` *(optional; names OK; transcripts usually private)*
- response_vary: `...|none|unknown` *(optional: response `Vary` header; prefer canonical lower-case, comma-separated, no spaces)*
- response_age: `...|none|unknown` *(optional: response `Age` header)*
- request_context_compact: `none|req[ua=...;lang=...;cache=...;cookie=...;geo=...;asn=...;resolver=...] vary[accept-language,user-agent] age[120]` *(optional; see `DOC:docs/232-compact-request-context-notes.md`; copy/pasteable into parity/beacon `observations[].notes`)*

*(See `DOC:docs/232-compact-request-context-notes.md` and `DOC:docs/224-request-context-and-variant-probing-for-public-surfaces.md`.)*

## Digest pins
- body_sha256: `sha256:<64-hex>`
- capture_file_sha256: `sha256:<64-hex>` *(headers + body as captured)*
- time_proof_digests: `none|sha256:<...>; ...` *(optional: RFC3161 token / Roughtime transcript / time beacon digest)*
- notes_on_transforms: `none|...` *(if decompressed/normalized, pin both digests and describe transform)*

## Network context (minimal)
- dns_context: `system_resolver|...` *(optional: resolved IPs if publishable)*
- tls_context: `none|spki_sha256:<...>|leaf_cert_sha256:<...>` *(optional)*

## Redaction / sensitivity notes (optional)
- redactions_applied: `none|...`
- cite: `CHECK:artifacts/checklists/public-artifact-redaction-checklist.md`
- if a published derivative was produced (cropped/blurred/excerpted), include: `MANIFEST:redaction-log.md` (see `DOC:docs/225-redaction-logs-and-transformation-accountability.md`)

## Bundle linkage (optional)
- related_parity_snapshot_digest: `sha256:<...>`
- related_notice_ids: `...`
