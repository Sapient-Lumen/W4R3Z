# FILE-ATTRIBUTE-BUDGET coherence refactor — rev0029

This pass deliberately avoids inflating the strict lane. FILE-ATTRIBUTE-BUDGET-01 is a useful maintainer hardening packet, but it should not be merged into broader byte caps or response-token binding findings.

## Canonical packet

```text
FILE-ATTRIBUTE-BUDGET-01:
  U-199 = canonical lead.
```

## Kept separate

```text
UNCOMPRESSED-MESSAGE-CAPS / U-02:
  Broad zlib/uncompressed byte budget.
  Public/upstream-adjacent through 3.3.11 RC release notes.
  U-199 is narrower: a semantic per-file subfield budget after the outer byte cap.

SEARCH-RESP-01 / U-163:
  Accepted inbound FileSearchResponse token/source/scope binding.
  Already strict-promoted in rev0013.
  Do not dilute it with per-file metadata-count parser work.

FOLDER-RESP-01 / U-167 and U-255 family:
  Requested-folder binding and parse-before-filter behavior.
  U-199 touches the same FolderContentsResponse parser surface, but the fix point is the shared attribute parser.

SEARCH-RESP parser/order support:
  U-254/U-262/U-263/U-264/U-265/U-266/U-267/U-270 remain response-side parser/policy/accounting/lifetime rows.

Virtual-path budget family:
  U-221/U-224/U-271 remain path length/component/control-character budget rows, not file-attribute-count rows.
```

## Compatibility guardrails

A good fix should preserve legitimate Soulseek/Nicotine+ interoperability while bounding parser work.

```text
Avoid:
  - rejecting ordinary clients that send the known bitrate/length/vbr/sample-rate/bit-depth set;
  - enforcing separate inconsistent limits in search, browse, and folder parsers;
  - treating the broad uncompressed-message byte cap as a substitute for semantic subfield caps;
  - silently changing duplicate valid-attribute semantics without a test.

Prefer:
  - one shared constant near the file-attribute parser;
  - bounded skip or well-documented malformed-message rejection for excess pairs;
  - fixed-behavior tests for all three public surfaces;
  - explicit tests for excess unknown attribute codes and duplicate known codes.
```

## Strict decision

```text
Verified current behavior: yes.
Hard-search status: candidate no direct exact public match found, but public/protocol adjacent.
Strict promotion: no.
Reason: low/medium parser work hardening with proportional attacker bytes and broad cap adjacency; lower impact than current strict candidates.
```
