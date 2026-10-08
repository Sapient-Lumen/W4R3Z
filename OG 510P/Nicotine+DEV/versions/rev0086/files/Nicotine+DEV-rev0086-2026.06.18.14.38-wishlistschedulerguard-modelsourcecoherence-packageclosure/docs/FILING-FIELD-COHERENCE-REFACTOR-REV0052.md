# Filing-field coherence refactor — rev0052

This audit/refactor pass separates five things that had become easy to blur during handoff preparation:

1. **Minimum private packet claims** — still the seven production-gated packets.
2. **Filing fields** — reviewer-facing crosswalk of report, fix, patch, regression, source anchors, and non-claims.
3. **Archived source anchors** — rev0051 line-level anchors generated from the external rev0003 source bundle.
4. **Current public web spotcheck** — lightweight, non-authoritative evidence that does not replace a current checkout.
5. **Public path-traversal work** — PR #3781/#3723 remain public-watch-only rows.

Refactor data:

```text
data/rev0052_filing_field_refactor.csv
```
