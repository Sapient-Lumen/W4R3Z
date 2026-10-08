# 231 — Placeholder domains, identifiers, and documentation ranges

**Track:** Shared

Examples and templates in this archive are routinely copied into real systems.
To prevent accidental reliance on real domains or addresses, examples MUST use **reserved**
placeholders that are safe to publish and safe to copy.

This doc is intentionally small. It complements the publishable-lint guidance in `189.4`.

## 231.1 Reserved placeholders (preferred)

Use **RFC2606** reserved example domains/TLDs for anything that looks like a real endpoint:

- **Domains:** `example.com`, `example.net`, `example.org` (xref: rfc2606_txt)
- **TLDs:** `.test`, `.example`, `.invalid`, `.localhost` (xref: rfc2606_txt)

Recommended canonical placeholders for Election Stack examples:

- **Primary official web domain:** `elections.example`
- **Status page domain (separate operator):** `status.example`
- **Mirror domains:** `mirror1.example.net`, `mirror2.example.org`
- **Email examples:** `alerts@elections.example` (or `alerts@example.invalid` when you want an address that MUST NOT resolve)

### Avoid restricted/loaded TLDs in examples

Do **not** use `.gov`, `.mil`, `.edu`, or country-code TLDs in examples. Even with “example” labels,
these can be misread as authoritative or imply a real governance boundary.

If you need to communicate “this is typically a government domain,” do it in prose:
"(often hosted under a jurisdiction's official domain)".

## 231.2 Documentation IP ranges

When an example needs an address literal, use the IETF documentation ranges:

- IPv4: `192.0.2.0/24`, `198.51.100.0/24`, `203.0.113.0/24` (xref: rfc5737_txt)
- IPv6: `2001:db8::/32` (xref: rfc3849_txt)

## 231.3 Drift firewall guidance

- New examples should prefer the canonical placeholders above.
- If you find `example dot gov` / `example dot edu`-style placeholders, convert them to `.example` or `.invalid`.

