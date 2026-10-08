# Wake from amnesia — rev0020

Start here after sleep:

1. `docs/180-rev0020-epochgate-repairmarket-wirecanon.md`
2. `docs/181-epoch-gated-mutable-heads.md`
3. `docs/182-repair-market-without-authority.md`
4. `docs/183-wire-canonicalization-before-live-transport.md`
5. `docs/184-surface-fold-audit-refactor.md`
6. `docs/185-python-surface-rev0020.md`

rev0020's main insight:

```text
Mutability, repair capacity, and wire framing are safety boundaries, not plumbing details.
```

The next likely risk lanes are repeated epoch observation under split view, repair-market replay/collusion across time windows, STORE wire transcript fixtures tied to custody drills, and a deeper provider-surface wrapper migration.
