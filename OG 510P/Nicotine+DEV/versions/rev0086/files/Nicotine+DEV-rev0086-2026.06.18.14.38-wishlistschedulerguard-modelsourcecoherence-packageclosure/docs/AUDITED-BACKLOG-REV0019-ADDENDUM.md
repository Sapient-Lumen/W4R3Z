# Audited backlog addendum — rev0019

## New verified audited-backlog packet

```text
TRANSFER-EOF-01 / U-251
```

U-251 is now source-traced and dynamically witnessed across:

```text
github-tag-3.3.10
github-branch-3.3.x
github-branch-master
```

The behavior is real:

```text
- EOF before advertised upload size is not treated as terminal.
- The upload remains active until generic idle/close handling.
- Later file growth after an earlier EOF can still be sent.
- Sent-byte overshoot misses exact completion because the finish gate is `== size`, not `>= size`.
```

## Strict document status

```text
Strict/front-lane report-candidates retained: 3
New strict promotions in rev0019: 0
Production-ready disclosure texts: 0
```

Strict candidates remain:

```text
1. U-123 — duplicate peer-supplied download transfer tokens / stale-timeout / F-session orphaning.
2. PB-01 / U-168+U-176 — peer connection primary election replacement/promotion without source/generation binding.
3. SEARCH-RESP-01 / U-163 — FileSearchResponse token/source/scope binding.
```

## Queue change

```text
U-251 moved from queued-next to verified audited backlog.
U-107/U-198 were reclassified as support siblings for fixed-behavior planning.
U-269 was explicitly kept separate.
U-244 becomes the next narrow upload/transfer policy target.
```
