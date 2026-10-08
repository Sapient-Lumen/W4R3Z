# Split-view variant probing checklist (tight, one axis at a time)

**Track:** Shared (cross-cutting)


Use this when a public surface appears to serve different bytes to different audiences.
See: `DOC:docs/224-request-context-and-variant-probing-for-public-surfaces.md`.

## Rules
- Probe **one axis at a time**; keep the rest constant.
- Record each probe as an observation with a compact `req[...] vary[...] age[...]` note (224.2a).
- Never publish secrets: `Cookie:` / `Authorization:` headers, tokens, or cookie values.

## Probes (suggested order)
- [ ] Baseline context recorded (`req[ua=...;lang=...;cache=none;cookie=...]`).
- [ ] Cookie state flipped (`cookie=none` vs `cookie=present_redacted`) and recorded.
- [ ] Cache bypass attempted (`cache=no-cache` or `cache=force-refresh`) and recorded.
- [ ] Language switched (second primary tag) and recorded.
- [ ] UA class switched (desktop↔mobile or browser↔CLI) and recorded.
- [ ] Second vantage / resolver class probed and recorded (if feasible).

## Publishable preflight
- [ ] `python3 tools/observer_verify_packet.py <PACKET_DIR> --lint-public` passes (no FAIL).
- [ ] If a published derivative exists, include `redaction-log.md` (see `DOC:docs/225-redaction-logs-and-transformation-accountability.md`).
