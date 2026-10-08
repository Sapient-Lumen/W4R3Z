# Web/public-overlap refresh — FILE-ATTRIBUTE-BUDGET-01 / U-199 — rev0029

Date: 2026-06-14 (America/New_York)

## Captured searches

- `site:github.com/nicotine-plus/nicotine-plus file attribute count semantic cap FileSearchResponse FolderContentsResponse SharedFileListResponse`
- `site:github.com/nicotine-plus/nicotine-plus "uncompressed" "FileSearchResponse" "FolderContentsResponse"`
- `site:github.com/nicotine-plus/nicotine-plus "unpack_file_attributes"`
- `site:github.com/nicotine-plus/nicotine-plus "SharedFileListResponse" "FileSearchResponse" "attributes"`
- `"unpack_file_attributes" "nicotine-plus"`
- `"FileSearchResponse" "Nicotine+" "uncompressed" "128 MiB"`
- `"FolderContentsResponse" "Nicotine+" "128 MiB"`
- `"file attributes" "Nicotine+" "FileSearchResponse"`

## Public material found

- Nicotine+ protocol documentation describes all three relevant result/list surfaces as carrying a `uint32 number of attributes` followed by an iteration over that number of `(uint32 attribute code, uint32 attribute value)` pairs:
  - `SharedFileListResponse` / Peer Code 5
  - `FileSearchResponse` / Peer Code 9
  - `FolderContentsResponse` / Peer Code 37
  URL: https://nicotine-plus.org/doc/SLSKPROTOCOL.html

- Nicotine+ release notes for 3.3.11 RC1 include broad adjacent parser/resource hardening: maximum sizes for uncompressed network messages. That is public-adjacent to U-199 but does not itself establish a semantic cap on the per-file attribute count field.
  URL: https://nicotine-plus.org/NEWS.html

- GitHub issue #2688 is attribute-adjacent but not a semantic-count cap report. It describes file attributes not showing for large files.
  URL: https://github.com/nicotine-plus/nicotine-plus/issues/2688

- GitHub issue #2415 is search-result/file-properties-adjacent but not a semantic-count cap report. It describes an AttributeError when opening File Properties from search results.
  URL: https://github.com/nicotine-plus/nicotine-plus/issues/2415

## Local public snapshot cross-check

The embedded rev0003 GitHub open-issue snapshot contained one open issue matching `attribute` / `file attributes`:

```text
#2688 File attributes not showing for files larger than 3-4gb
state: open
created_at: 2023-10-17T16:56:42Z
updated_at: 2024-03-12T17:06:13Z
```

No open PR in the embedded snapshot matched `attribute`, `unpack_file_attributes`, `FileSearchResponse`, `FolderContentsResponse`, or `SharedFileListResponse` as an exact U-199 fix.

## Overlap decision

Classification: **candidate no-direct-public-found / broad uncompressed-message and protocol-schema adjacent**.

Reason:

```text
- The public protocol schema openly documents an attacker-controlled attribute count field.
- Current release notes publicly acknowledge broad uncompressed network-message caps.
- Captured searches did not surface a direct issue/PR specifically about enforcing a semantic per-file attribute-count cap across search, browse, and folder result parsers.
- Therefore U-199 should be framed as a low/medium semantic-budget regression-test and maintainer-hardening packet, not as a strict/new disclosure candidate.
```
