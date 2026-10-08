# rev0035 public-overlap notes — strict/front lane

This pass refreshed public-overlap status only for the three existing strict/front report candidates.

## Searches performed

```text
site:github.com/nicotine-plus/nicotine-plus duplicate transfer token active_users TransferRequest FileTransferInit
site:github.com/nicotine-plus/nicotine-plus PeerInit secondary connection promote primary PierceFireWall
site:github.com/nicotine-plus/nicotine-plus FileSearchResponse token unexpected peer search response private results
Nicotine+ duplicate transfer token FileTransferInit
Nicotine+ PeerInit PierceFireWall primary connection promotion
Nicotine+ FileSearchResponse token private results parser
```

## Outcome

- U-123: no exact duplicate-token/stale-timeout/F-session orphan public match was captured. Public transfer-lifecycle adjacency remains via GitHub #653 and #2978.
- PB-01: no exact direct public match was captured. The official protocol documentation is compatibility context: PeerInit's token is documented as zero/ignored, and only a single active P connection to a peer is expected.
- SEARCH-RESP-01: no exact source/scope-token public match was captured. The official protocol documentation confirms the FileSearchResponse token is derived from the original FileSearch/UserSearch/RoomSearch and documents the public/private result-list parse shape.

## Conservative classification

The rev0035 strict lane should not claim final public novelty. It should say: targeted searches did not capture direct duplicates, but public adjacent material exists and a final pre-filing overlap check remains mandatory.

## References captured

- GitHub issue #653: transfer connection initiation following an unallowed/queued transfer response.
- GitHub issue #2978: connection closed / active-transferring transfer lifecycle symptoms.
- Nicotine+ SLSK protocol documentation: PeerInit, FileSearchResponse, and FileTransferInit token semantics.
