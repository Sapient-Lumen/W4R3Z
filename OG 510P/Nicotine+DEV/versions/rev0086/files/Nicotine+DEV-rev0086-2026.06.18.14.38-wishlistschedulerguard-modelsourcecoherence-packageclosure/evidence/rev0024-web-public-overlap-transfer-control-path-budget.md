# rev0024 public-overlap refresh — transfer-control path budget

Search status: no direct exact public report was found for the combined QueueUpload / legacy TransferRequest / PlaceInQueueRequest / FolderContentsRequest semantic path-budget invariant.

Relevant public-adjacent material:

- Nicotine+ protocol documentation defines the peer messages in scope: FolderContentsRequest/Response, TransferRequest, QueueUpload, PlaceInQueueRequest, and PlaceInQueueResponse: https://nicotine-plus.org/doc/SLSKPROTOCOL.html
- Draft PR #3741 publicly explores virtual-path and file-name component validation for scanning shares and receiving search results, folder contents, and browsed share lists. It also discusses component/path/depth limits and maintainer compatibility concerns: https://github.com/nicotine-plus/nicotine-plus/pull/3741
- Discussion #1997 includes debug logs around repeated QueueUpload and PlaceInQueueRequest traffic: https://github.com/nicotine-plus/nicotine-plus/discussions/1997
- Issue #2978 includes broader connection/transfer debug adjacency with QueueUpload and PlaceInQueueRequest objects: https://github.com/nicotine-plus/nicotine-plus/issues/2978

Conclusion: mark as `candidate no direct exact public match found / public-adjacent`; do not claim clean novelty.
