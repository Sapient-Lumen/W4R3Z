# rev0005 public-overlap hard-search batch 01

Purpose: record public-overlap status before anything moves toward the strict document. This is an initial hard-search batch, not a final statement of novelty.

## Rules used in this revision

A finding cannot be marked fresh merely because the previous cube called it fresh. It needs a per-finding public-overlap record with exact-term searches, source-lane checks, and a written conclusion.

Classification terms:

- `direct-public`: public issue/PR/discussion/advisory appears to describe the same root cause or remediation target.
- `public-adjacent`: public material describes the same family, symptom, or adjacent code path, but not enough to prove the exact root is already public.
- `upstream-in-flight`: current or future source/release material appears to implement or discuss a relevant fix shape.
- `candidate no-direct-public-found`: initial hard searches did not find a direct public overlap, but this is not a guarantee.
- `not searched`: no adequate public-overlap work yet.

## Captured public sources

- Official Nicotine+ release notes for 3.3.11 RC1: records maximum-size enforcement for uncompressed network messages, spoofed-user upload prevention, peer-identity fix, and distributed-search fixes.
- Official/draft PR #3741: `PeerMessage: parse_virtual_path() to validate directory name components`; draft source discussion mentions protocol-level limits, virtual path and file name validation while scanning shares and receiving search results/folder contents/browsed lists, illegal control characters, path traversal identifiers, component sizes, total path+filename size, nesting depth, and search-result entry caps.
- GitHub discussion #1997: repeated `QueueUpload` and `PlaceInQueueRequest` log messages are discussed in connection with stalled background downloads.
- GitHub issue search pages captured for `FolderContentsResponse` and `PlaceInQueueRequest`: `FolderContentsResponse` has older parser/dialog/type-annotation results; `PlaceInQueueRequest` maps to issue #2978 connectivity logs.
- GitHub search for FileSearchResponse/token/private-search/trailing-partial terms: captured results were broad or unrelated, not a direct report of the exact parser-ordering claims in this batch.

## Batch 01 status by finding

### U-169 — FileTransferInit attaches active file transfers by claimed username plus transfer token without pending-source or socket/address binding

- Public-overlap class: `upstream-in-flight / adjacent-public`
- Search level: initial hard-search pass complete for this revision
- Evidence summary: Exact FileTransferInit/token public issue search did not surface a direct issue in the captured GitHub search page, but the 3.3.11 RC explicitly fixes spoofed-user upload flow and 3.3.x/master source closes unknown FileTransferInit tokens. Keep as upstream-overlap/backport/regression candidate, not a clean fresh strict item.
- Queries/next queries: FileTransferInit token; FileTransferInit username token; spoofed users upload; release notes spoofed users; issue search FileTransferInit
- Sources/evidence: NEWS 3.3.11 RC spoofed-user upload; GitHub issue search FileTransferInit no-results page; local source lanes downloads/uploads _file_transfer_init
- Strict decision: not promoted - upstream overlap and dynamic binding proof still needed

### U-262 — Private FileSearchResponse result lists are parsed even when private search results are disabled

- Public-overlap class: `candidate no-direct-public-found / generic-upstream-overlap`
- Search level: initial hard-search pass complete for this revision
- Evidence summary: Exact private_search_results/FileSearchResponse-private issue searches did not surface a direct match in captured GitHub search pages. The generic 3.3.11 RC uncompressed-message cap and master parser gating overlap the resource-budget shape, but not necessarily the private-results policy-ordering claim. Needs source trace of the UI policy branch and minimal parser-cost test before promotion.
- Queries/next queries: private_search_results; private search results FileSearchResponse; FileSearchResponse private; search results private policy
- Sources/evidence: GitHub issue searches for private_search_results/private search results no direct matches; NEWS 3.3.11 uncompressed-message cap; local source lanes FileSearchResponse parser
- Strict decision: not promoted - direct source/policy proof incomplete

### U-267 — FileSearchResponse invalid-token early drop still decompresses peer-controlled username length before token validation

- Public-overlap class: `candidate no-direct-public-found / partial-upstream-overlap`
- Search level: initial hard-search pass complete for this revision
- Evidence summary: Captured searches did not identify a direct public report for invalid-token FileSearchResponse prefix decompression. Source still shows username-length/token prefix decompression before token rejection across 3.3.10, 3.3.x, and master; later branches add a 128 MiB rest-of-message cap. Needs microbenchmark/repro and check whether parser-level prefix cap exists elsewhere.
- Queries/next queries: FileSearchResponse token; invalid token decompression; search response token Nicotine+; FileSearchResponse invalid token
- Sources/evidence: GitHub issue search FileSearchResponse/token yielded unrelated or broad issues; NEWS uncompressed-message cap; local source lanes FileSearchResponse parser
- Strict decision: not promoted - dynamic prefix-budget proof needed

### U-270 — FileSearchResponse peer connections can stay open after results by appending trailing partial data

- Public-overlap class: `candidate no-direct-public-found / broad-public-adjacent`
- Search level: initial hard-search pass complete for this revision
- Evidence summary: Exact trailing-partial FileSearchResponse query did not produce a direct public issue in the captured results. Public search/connection/open-file/socket issues are broad-adjacent only. Needs network lifecycle trace or reproduction before this can be ranked high.
- Queries/next queries: FileSearchResponse trailing partial; search response connection stays open; peer search response socket open; trailing partial data Nicotine+
- Sources/evidence: GitHub search results show broad search hardlock/socket/connectivity history, not exact trailing-partial connection lifetime
- Strict decision: not promoted - source/dynamic proof not complete

### U-163 — FileSearchResponse acceptance is token-only and not bound to requested source/scope; initial search tokens have low entropy and then increment linearly

- Public-overlap class: `candidate no-direct-public-found / future-source-adjacent`
- Search level: initial hard-search pass complete for this revision
- Evidence summary: Issue searches for search-response/token surfaced old/general search items, not the exact token-only source/scope-binding claim. Master source uses allowed_responses in FileSearchResponse parsing, which is a future-source overlap signal; exact requested-source/scope binding remains to be audited.
- Queries/next queries: FileSearchResponse token; search response token; search result source binding; accepted search token
- Sources/evidence: GitHub issue searches for FileSearchResponse/search-token; local master FileSearchResponse allowed_responses; 3.3.10/3.3.x search handler token checks
- Strict decision: not promoted - future-source overlap and scope proof needed

### U-176 — Secondary peer/distributed/file connections can be promoted to primary on any post-init message without source or generation binding

- Public-overlap class: `upstream-in-flight / adjacent-public`
- Search level: initial hard-search pass started, not complete
- Evidence summary: Broad peer identity/spoofing fixes in the 3.3.11 RC overlap this class. Exact secondary-connection promotion binding still needs targeted public search and source trace before any freshness claim.
- Queries/next queries: secondary peer connection primary promotion; PeerInit existing connection; spoofed peers username theirs; direct PeerInit replace connection
- Sources/evidence: NEWS 3.3.11 RC peer-identity/spoofed-user fixes; local slskproto to be traced in next batch
- Strict decision: not promoted - exact hard search incomplete

### U-167 — FolderContentsResponse accepts pending folder requests by claimed username and folder path while ignoring the request token

- Public-overlap class: `candidate no-direct-public-found / parser-public-adjacent`
- Search level: initial hard-search pass complete for this revision
- Evidence summary: FolderContentsResponse public issue search finds old parser/dialog/type-annotation items but not a direct request-token binding report. Master source has allowed_responses gating for username+directory, so future-source overlap is significant. Treat as regression/backport/source-lane item until token/username/path semantics are fully checked.
- Queries/next queries: FolderContentsResponse token; FolderContentsResponse request token; folder contents response pending request; FolderContentsResponse allowed_responses
- Sources/evidence: GitHub FolderContentsResponse issue search; local master FolderContentsResponse allowed_responses; local 3.3.10 parser
- Strict decision: not promoted - future-source overlap and exact invariant still under review

### U-168 — Incoming direct PeerInit can replace an existing peer/distributed connection using only a claimed username and connection type

- Public-overlap class: `upstream-in-flight / adjacent-public`
- Search level: initial hard-search pass started, not complete
- Evidence summary: Direct PeerInit replacement is in the same broad peer identity/spoofing family as 3.3.11 RC fixes. Needs exact public search for PeerInit replacement plus source diff around direct/indirect connection adoption.
- Queries/next queries: PeerInit replace existing connection; PeerInit username spoof; peer identity spoofed Nicotine+
- Sources/evidence: NEWS 3.3.11 RC peer identity/spoofed-user fixes; local slskproto to be traced next
- Strict decision: not promoted - exact hard search incomplete

### U-217 — UserInfoResponse profile responses are accepted by claimed username without socket/address/request-generation binding

- Public-overlap class: `candidate pending hard-search`
- Search level: queued; not searched enough for classification
- Evidence summary: High-ranked claimed-username response-correlation item. Held for next exact search batch because this revision focused on FileSearchResponse/FileTransferInit/FolderContents/PlaceInQueue lanes.
- Queries/next queries: UserInfoResponse claimed username request generation; user info profile spoofed username; UserInfoResponse socket binding
- Sources/evidence: none captured in rev0005 beyond source lane availability
- Strict decision: not promoted - hard search not complete

### U-171 — Server ConnectToPeer can force outbound peer-connection attempts to arbitrary server-supplied addresses without a local pending-request budget

- Public-overlap class: `candidate pending hard-search`
- Search level: queued; not searched enough for classification
- Evidence summary: Server-supplied address outbound-connection item. Needs exact public search against issues/discussions/PRs and comparison to 3.3.11 connection fixes.
- Queries/next queries: ConnectToPeer arbitrary address; GetPeerAddress reserved address; outbound connection internal address Nicotine+
- Sources/evidence: none captured in rev0005 beyond source lane availability
- Strict decision: not promoted - hard search not complete

### U-181 — Pending PeerInit/GetPeerAddress state can buffer outbound peer messages without per-user or global budgets

- Public-overlap class: `candidate pending hard-search`
- Search level: queued; not searched enough for classification
- Evidence summary: Pending PeerInit/GetPeerAddress outbound-buffer growth is closely related to peer-connection lifecycle issues. Search/source pass scheduled after U-169/U-176/U-168.
- Queries/next queries: pending PeerInit buffered outbound messages; GetPeerAddress pending queue; peer messages before address resolved
- Sources/evidence: none captured in rev0005 beyond source lane availability
- Strict decision: not promoted - hard search not complete

### U-123 — Duplicate peer-supplied download transfer tokens can overwrite active-transfer state

- Public-overlap class: `candidate pending hard-search`
- Search level: queued; not searched enough for classification
- Evidence summary: Duplicate transfer-token state overwrite is near U-169/U-170. Needs exact token-collision search and active_users source trace.
- Queries/next queries: duplicate transfer token overwrite; active_users token FileTransferInit; transfer token collision Nicotine+
- Sources/evidence: none captured in rev0005 beyond source lane availability
- Strict decision: not promoted - hard search not complete

### U-265 — FileSearchResponse rows are fully decompressed, parsed, and sorted before search-term include/exclude filtering drops wrong results

- Public-overlap class: `candidate no-direct-public-found / broad search-performance adjacent`
- Search level: initial hard-search pass partial
- Evidence summary: Search performance/hardlock issues exist publicly, but the exact parse-then-filter ordering claim was not found directly in captured searches. Needs source trace through term-match include/exclude filter and dynamic measurement.
- Queries/next queries: search result filter after parsing; FileSearchResponse include exclude filtering; search results hardlock; max_displayed_results search
- Sources/evidence: GitHub issue #2128 broad search hardlock; local FileSearchResponse parser source
- Strict decision: not promoted - exact hard search/source proof incomplete

### U-266 — FileSearchResponse parser ignores max_displayed_results and materializes/sorts the full accepted result list before the UI cap

- Public-overlap class: `public-adjacent / possible known-performance overlap`
- Search level: initial hard-search pass partial
- Evidence summary: Public issue #2128 mentions search-result hardlock and max_displayed_results, making this not a clean fresh claim. The exact parser ignoring UI cap still needs source proof and should be framed as regression/performance hardening if retained.
- Queries/next queries: max_displayed_results search hardlock; FileSearchResponse max_displayed_results; search results sort full list
- Sources/evidence: GitHub issue #2128; local FileSearchResponse parser source
- Strict decision: not promoted - public-adjacent performance issue

### U-274 — PlaceInQueueRequest virtual paths are decoded and dictionary-looked-up before semantic length or component caps

- Public-overlap class: `public-adjacent / not-clean-fresh`
- Search level: initial hard-search pass complete for this revision
- Evidence summary: PlaceInQueueRequest appears in public discussion #1997 and issue #2978 connectivity logs, and draft PR #3741 overlaps virtual-path component validation. The exact oversized PlaceInQueueRequest lookup/echo claim was not found directly, but it should be marked adjacent/upstream-context, not clean fresh.
- Queries/next queries: PlaceInQueueRequest QueueUpload; PlaceInQueueRequest repeated; PlaceInQueueRequest virtual path; parse_virtual_path PlaceInQueueRequest
- Sources/evidence: GitHub discussion #1997 repeated QueueUpload/PlaceInQueueRequest; GitHub issue search PlaceInQueueRequest -> #2978; PR #3741 virtual path validation
- Strict decision: not promoted - public adjacent and low/medium severity

### U-254 — FileSearchResponse parsing performs full decompression/result parsing before ignored-user or ignored-IP policy drops the response

- Public-overlap class: `candidate no-direct-public-found / broad search-policy adjacent`
- Search level: initial hard-search pass partial
- Evidence summary: No exact parse-before-ignore public issue surfaced in captured searches. It overlaps U-163/U-262/U-265/U-266 and generic uncompressed cap work; keep as cluster evidence, not standalone strict item yet.
- Queries/next queries: FileSearchResponse ignored user parse before ignore; search result ignored IP parse first; FileSearchResponse policy drop
- Sources/evidence: local search._file_search_response source; broad search issues only
- Strict decision: not promoted - cluster merge likely

### U-256 — FolderContentsRequest echoes attacker-controlled directory strings into FolderContentsResponse without semantic size or response-budget checks

- Public-overlap class: `public-adjacent / future-pr-overlap`
- Search level: initial hard-search pass complete for this revision
- Evidence summary: PR #3741 directly overlaps virtual-path component/depth/count validation for peer search/browse/folder responses, and FolderContentsResponse issue search has old parser context. The exact FolderContentsRequest directory echo path may be distinct, but this should not be claimed as cleanly unmentioned until PR scope is fully checked.
- Queries/next queries: FolderContentsRequest directory echo; FolderContentsResponse folder path validation; parse_virtual_path FolderContentsResponse; FolderContentsRequest oversized directory
- Sources/evidence: PR #3741; GitHub FolderContentsResponse issue search; local FolderContentsRequest/Response source
- Strict decision: not promoted - future PR overlap

