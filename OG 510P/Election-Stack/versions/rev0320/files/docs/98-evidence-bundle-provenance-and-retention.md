# 98 — Evidence Bundle Provenance & Retention

**Track:** A+C (Core + North Star)


## Goal
Make the public record durable and verifiable under:
- website compromise,
- takedowns,
- and long-term archival needs.

## Bundle retention policy
- Maintain multiple mirrors with content addressing.
- Use immutable object storage where possible.
- Publish hash indices so third parties can mirror confidently.

## Privacy-safe retention
- Publish a redaction policy for logs and operational artifacts.
- Use `artifacts/checklists/public-artifact-redaction-checklist.md` as the bounded, publishable checklist.
- Prefer aggregated or role-based logs where possible.
- Avoid including IPs, device IDs, or per-voter metadata in public bundles.

## Long-term verification
- Keep a stable set of verification tools (or hashes + builds) for historical elections.
- Store notarization artifacts (timestamps, inclusion proofs) alongside bundles.

## Canonical packaging
See `docs/173-canonical-evidence-envelopes-and-packets.md` for the normative evidence envelope and packet layout.
