# 151. Authoritative sources, pinning, and drift tracking

**Track:** Shared


This spec pack cites many external standards, regulations, and research artifacts.
To prevent **silent drift** and “source substitution” attacks (or simple link rot), all external dependencies should be pinned in a lockfile.

## 151.1 Precedence order (recommended)

When sources conflict, the preferred precedence is:

1. Statutory law / binding regulations for the jurisdiction.
2. Election authority standards and certification materials (e.g., EAC/VVSG in the U.S.).
3. NIST publications and Common Data Formats.
4. IETF RFC Editor publications (normative protocol specs).
5. Peer-reviewed academic publications.
6. Vendor whitepapers / blogs (informative only).

## 151.2 External sources lockfile

See `evidence/lock/external-sources.toml`.
Each entry should include:

- stable URL (and archive URL when possible)
- publication date
- sha256 of the retrieved bytes
- a short “why it matters” note
- drift trigger tags (e.g., `vvsg`, `cdf`, `ct`, `ohttp`)

## 151.3 Drift monitoring

At a minimum, run a quarterly drift review (monthly in the 60 days before an election).
When drift triggers fire, follow `150-maintainer-bootstrap-and-change-protocol.md` and record an ADR.