# Current-web snapshot limitations — rev0054

rev0054 improves rev0053 by recording current web-visible source markers for `master` and `3.3.x`, but it deliberately does not collapse the filing gate.

A source tree is still needed to:

```text
1. record exact commit/hash/date
2. classify native/equivalent fixes beyond selected literal markers
3. apply selected patch stack if needed
4. run seven fixed-behavior regressions
5. refresh maintainer report language against the tested source
```

The web snapshot is therefore useful for triage: it suggests that the seven private packets are not visibly resolved by the selected literal markers on current public branches, while preserving the final checkout/regression gate.
