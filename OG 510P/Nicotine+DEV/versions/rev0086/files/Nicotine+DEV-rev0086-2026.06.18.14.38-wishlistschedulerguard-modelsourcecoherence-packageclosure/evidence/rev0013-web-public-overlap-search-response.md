# rev0013 public-overlap refresh — SEARCH-RESP-01

## Classification

- U-163 / SEARCH-RESP-01: **candidate no direct public match found, public-adjacent**.
- U-262: **public-adjacent display-policy topic; parser-ordering subcase not standalone**.
- U-267: **candidate parser-budget support fact; not standalone strict item**.
- U-266/U-263/U-265/U-264/U-254: **search-result performance/policy-ordering backlog cluster**.

## Search intent

The hard-search target was a direct public issue/PR/advisory/release-note match for:

```text
FileSearchResponse token-only acceptance
search-response source/scope binding
user-search result accepted from unexpected peer
private FileSearchResponse parsed while private results are disabled
invalid-token search response decompressing prefix fields before token validation
```

## Public material found

- Nicotine+ issue #1400 publicly discusses search-result visible/total limits and memory/performance motivations for not showing all results at once. This overlaps U-266/U-263 style result-limit accounting, not U-163 source/scope binding.
- Nicotine+ issue #2128 publicly reports OS hardlock symptoms when getting many search results. This is broad search-result performance adjacency, not a direct source/scope invariant.
- Nicotine+ issues #1595 and #2886 publicly discuss private/locked search-result visibility policy. This overlaps private-result display semantics, not the parser-ordering fact that private rows are materialized before the display preference is consulted.
- Nicotine+ release notes document past search-result limiting, private/locked result display options, and historical search-ticket randomization. These are strong adjacency signals; they are not a direct report of the current user-scoped/room-scoped token-only response acceptance invariant.
- The official Soulseek protocol documentation says FileSearchResponse takes its token from the original FileSearch, UserSearch, or RoomSearch server message. That supports the remediation shape: an accepted response should be checked against the request mode/source/scope, not only against token membership.

## Resulting decision

Promote **SEARCH-RESP-01 / U-163** as a strict report-candidate because the current behavior is reproduced across all source lanes and the report can be framed narrowly around source/scope binding. Do **not** promote U-262, U-267, U-266, U-263, U-264, U-265, or U-254 as separate strict findings in this revision. They are support cases and regression tests for the same parser/response-ordering family.
