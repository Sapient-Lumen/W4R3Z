# rev0046 patch-stack topology evidence

rev0046 tests the seven strict/front packets as an integrated patch stack rather than as isolated proofs.

## Applied stack per lane

```text
1. U-123 selected transfer-session identity patch
   - touches pynicotine/downloads.py and pynicotine/transfers.py
2. PB-01 selected primary-election patch
   - touches pynicotine/slskproto.py
3. SEARCH-RESP source-set patch from rev0043
   - touches pynicotine/search.py
   - stacks/supersedes rev0039 user guard and rev0040 buddy snapshot guard
4. SEARCH-RESP parser-budget patch from rev0042
   - touches pynicotine/slskmessages.py
   - stacks/supersedes rev0041 username-prefix guard
```

## Integration result

The full stack was applied to the three archived source lanes from the external 2026-06-12 source bundle. All seven fixed-behavior regressions passed on all three lanes.

The important refactor result is that filing should not treat the seven packets as seven unrelated patches. They are now four coherent filing bundles:

```text
1. U-123 transfer-session identity
2. PB-01 peer primary-election compatibility
3. FileSearchResponse source-admission series: 01A + 01B + 01C
4. FileSearchResponse parser-budget series: prefix cap + result-count budget
```
