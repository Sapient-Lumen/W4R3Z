# rev0029 worklog

1. Focused on FILE-ATTRIBUTE-BUDGET-01 / U-199.
2. Re-read the rev0028 handoff and preserved the compact cube workflow.
3. Extracted and used the supplied upstream source bundle for all three lanes:
   - github-tag-3.3.10
   - github-branch-3.3.x
   - github-branch-master
4. Traced the shared file-attribute parser and the three result/list surfaces that call it:
   - SharedFileListResponse / browse shares
   - FileSearchResponse / search results
   - FolderContentsResponse / folder contents
5. Built a maintainer-style current-behavior pytest witness with compact compressed peer messages.
6. Ran the witness against all archived source lanes.
7. Captured web/public-overlap context and local snapshot overlap.
8. Refactored U-199 into a single semantic field-budget packet, separate from U-02 broad uncompressed caps, SEARCH-RESP-01 token/source binding, and parser-before-policy rows.
9. Kept strict/front lane unchanged at 3 report-candidates.
10. Performed cube hygiene: pruned generated pytest caches from maintainer_artifacts and wrote a fresh rev0029 audit/manifest.

No large source bundle was embedded.
