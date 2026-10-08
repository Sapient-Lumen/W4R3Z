# Registered-ledger revision alignment audit

This audit checks whether executable ledgers listed in `LEDGER-FAMILY-REGISTRY.json` expose the same top-level `revision` as `RELEASE-MANIFEST.json`.

It does not judge scientific content.  It prevents restart drift:

```text
ledger content changed
+ registry lists the ledger
+ release manifest moved forward
but ledger top-level revision still names an old bundle
= stale executable surface
```

The generated report is `docs/30-program/registered-ledger-revision-alignment-audit.generated.md` and is lint-enforced.
