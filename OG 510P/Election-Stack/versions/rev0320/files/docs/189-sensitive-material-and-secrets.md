# 189 — Sensitive material and secrets policy

**Track:** Shared

This archive is designed to be public / redistributable.
A single accidental secret can invalidate the entire evidence program.

## 189.1 Absolute prohibitions (MUST NOT appear anywhere in the repo)

- **Private keys** in any form (PEM / PKCS8 / OpenSSH / P12/PFX), even for “examples”.
- **Credentials / tokens** (API keys, bearer tokens, session cookies, cloud keys).
- **PII** or voter-specific data (names, addresses, DOB, IDs), unless it is **synthetic** and explicitly labeled as such.
- **Raw operational incident logs** that include sensitive endpoints, credentials, or internal-only identifiers.

If you need to reference such material:
- include **only a citation** (or a pinned upstream hash in `evidence/lock/`),
- or include a **redacted** excerpt that cannot be used to authenticate or deanonymize.

## 189.2 Handling rules for maintainers (human or LLM)

- Treat *all pasted blobs* as suspect.
- Prefer **public keys** and **key IDs**; never add private material.
- If a key-like blob appears in a draft, **delete it immediately** and replace with:
  - a short description (what it is for), and
  - a reference to an external, properly governed key management process.

## 189.3 Drift firewall

The release gate includes `scripts/check_no_private_keys.py`.
It fails if it detects:
- private key headers (e.g., `-----BEGIN ... PRIVATE KEY-----`), or
- keyfile extensions (`.pem`, `.key`, `.p12`, `.pfx`).

This is not a general secret scanner; it is a high-signal guardrail for the most catastrophic mistake.
In addition, publishable bundles should be preflighted with the conservative publishable lint:
- `python3 tools/observer_verify_packet.py <PACKET_DIR> --lint-public` (or `python3 tools/public_artifact_lint.py --packet <PACKET_DIR>`)

It FAILs on obvious header/secret markers and token patterns, and WARNs on likely identifying literals (IPs/emails/phones/coordinates) so operators can keep public artifacts coarse and non-identifying (DOC:docs/173-canonical-evidence-envelopes-and-packets.md).


## 189.4 Handling publishable-lint WARNs (tight exceptions)

The publishable lint is intentionally conservative: it WARNs on *likely* identifiers.
Preferred resolution order:

1. **Replace with documentation placeholders** (non-identifying):
   - IPv4 documentation ranges: `192.0.2.0/24`, `198.51.100.0/24`, `203.0.113.0/24` (xref: rfc5737_txt)
   - IPv6 documentation ranges: `2001:db8::/32` (xref: rfc3849_txt) and `3fff::/20` (xref: rfc9637_txt)
   - Example domains: `example.com/.org/.net`, `.test`, etc. (xref: rfc2606_txt)
   - Placeholder conventions (domains, emails, IP ranges): `231`

2. **Coarsen**: prefer `geo=country=XX`, `asn=<digits>`, `resolver=<class>` over literal IPs/emails.

3. **If an identifier is truly load-bearing**, record the minimization + justification in `redaction-log.md` and add a WARN suppression directive:
   - `lint-allow: <code>`

Suppressions are **WARN-only** (FAIL is never suppressed) and are packet-scoped by design; use them rarely.
For PII framing and incident handling norms, see NIST guidance (xref: nist_sp800_122_pdf).

