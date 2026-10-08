# rev0007 public-overlap packet — U-123

## Classification

U-123 remains **candidate no direct public match found**, but it is not cleanly isolated from public transfer-lifecycle history.

## Captured searches

| query | result class | interpretation |
|---|---|---|
| `site:github.com/Nicotine-Plus/nicotine-plus duplicate transfer token TransferRequest FileTransferInit` | no direct duplicate-token hit found | Did not surface an issue/PR using the duplicate-token active-map collision language. |
| `site:github.com/Nicotine-Plus/nicotine-plus "FileTransferInit" "token" "active_users"` | protocol/source-adjacent | Reinforces that FileTransferInit token handling is public/source-visible, not a private discovery by itself. |
| `site:github.com/nicotine-plus/nicotine-plus/issues "transfer token" "downloads"` | adjacent transfer lifecycle tickets | Found #653, #2978, #1933-class transfer/connection symptoms, not this specific invariant. |
| `"Duplicate peer-supplied download transfer tokens"` | no relevant public hit | Captured no direct public title/phrase match. |

## Public adjacent material

- Issue #653: transfer connection initiation after queued/disallowed transfer responses; includes TransferRequest/TransferResponse/FileTransferInit timing and token language.
- Issue #2978: connection closed/timeout/queued symptoms where downloads can ignore actions; adjacent symptom space, not duplicate token proof.
- Issue #1933: upload slots not opening; transfer lifecycle/slot behavior, not download active-map token collision.
- Nicotine+ protocol docs: FileTransferInit uses the same token previously included in TransferRequest, and the download example flow confirms TransferRequest precedes TransferResponse and F-connection setup.

## Working conclusion

Mark U-123 as: `candidate-no-direct-public-found / transfer-lifecycle-public-adjacent`.

Do not claim absolute novelty. The correct phrasing is: **no direct public duplicate-token active-map/stale-timer report found in captured searches**.
