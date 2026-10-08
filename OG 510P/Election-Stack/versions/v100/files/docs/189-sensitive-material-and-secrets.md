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
