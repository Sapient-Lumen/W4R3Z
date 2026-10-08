# Audited backlog addendum — rev0029

## FILE-ATTRIBUTE-BUDGET-01 / U-199

Decision: **verified audited backlog; not strict-promoted**.

Run summary:

```text
github-tag-3.3.10:   3 passed
github-branch-3.3.x: 3 passed
github-branch-master: 3 passed
```

What was verified:

```text
SharedFileListResponse:
  one file with eleven filler attributes followed by a valid bitrate attribute
  is parsed; the final bitrate survives.

FileSearchResponse:
  same over-budget per-file attribute layout is parsed; the final bitrate survives.

FolderContentsResponse:
  same over-budget per-file attribute layout is parsed; the final bitrate survives.
```

Why backlog rather than strict:

```text
- parser work/availability hardening, not code execution;
- attacker sends bytes proportional to parser work;
- broad uncompressed-message caps provide an outer bound;
- public protocol schema documents variable attribute counts;
- no direct exact public semantic-count cap issue surfaced in captured searches;
- lower value than U-123, PB-01, and SEARCH-RESP-01.
```

Suggested next target: **WMA/ASF parser tiny-step amplification / U-273**, unless queue re-scoring chooses a different compact local parser-budget row.
