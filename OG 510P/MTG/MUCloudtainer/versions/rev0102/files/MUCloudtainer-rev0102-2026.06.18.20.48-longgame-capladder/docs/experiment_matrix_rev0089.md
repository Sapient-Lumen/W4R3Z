# rev0089 experiment matrix

| Input evidence | Rows scanned | Replay sample | Mismatches | Interpretation |
| --- | ---: | ---: | ---: | --- |
| rev0069 population frontier games | 144 | 16 | 0 | Current runtime reproduces sampled frontier rows. |
| rev0070 population precision games | 288 | 16 | 0 | Current runtime reproduces sampled precision rows. |
| rev0080 size ladder games | 720 | 16 | 0 | Current runtime reproduces sampled complete-panel rows. |
| rev0084 candidate transfer games | 480 | 16 | 0 | Current runtime reproduces sampled adaptive candidate rows. |

Identity coverage:

| Source | Rows | Missing runtime digest rows | Missing pair digest rows |
| --- | ---: | ---: | ---: |
| rev0069 | 144 | 144 | 144 |
| rev0070 | 288 | 288 | 288 |
| rev0080 | 720 | 720 | 720 |
| rev0084 | 480 | 480 | 480 |

The identity gap is expected for inherited rows. The new refactor ensures future annotated rows carry the digest fields.
