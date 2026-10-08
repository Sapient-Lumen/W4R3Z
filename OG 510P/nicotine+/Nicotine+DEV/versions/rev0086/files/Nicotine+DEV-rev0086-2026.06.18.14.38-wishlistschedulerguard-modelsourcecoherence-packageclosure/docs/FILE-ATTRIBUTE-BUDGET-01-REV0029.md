# FILE-ATTRIBUTE-BUDGET-01 — rev0029

Canonical packet: **U-199**.

Status: **verified audited backlog**, **not strict-promoted**.

## Finding summary

Nicotine+ result/list parsers carry a per-file file-attribute section shaped as:

```text
uint32 number_of_attributes
repeat number_of_attributes:
  uint32 attribute_code
  uint32 attribute_value
```

Across the archived source lanes, the parser reads the peer-supplied count and iterates that many pairs. It only retains known attributes, but the loop itself is not semantically capped to the small known retained attribute budget.

The current helper shape is:

```python
pos, numattr = cls.unpack_uint32(message, pos)

for _ in range(numattr):
    pos, attrnum = cls.unpack_uint32(message, pos)
    pos, attr = cls.unpack_uint32(message, pos)

    if attrnum in valid_file_attributes:
        attrs[attrnum] = attr
```

On master, the parser has moved to an instance-offset style and a `FileAttributes` object, but the relevant shape remains the same:

```python
numattr = self.unpack_uint32()

for _ in range(numattr):
    attrnum = self.unpack_uint32()
    attr = self.unpack_uint32()
```

The three verified call sites are:

```text
SharedFileListResponse  -> browse/share-list parser
FileSearchResponse      -> search-result parser
FolderContentsResponse  -> folder-content parser
```

## Proof status

Maintainer-style current-behavior test:

```text
maintainer_artifacts/file-attribute-budget-01/test_file_attribute_budget_reproducer.py
```

Run summary:

```text
github-tag-3.3.10:   3 passed
github-branch-3.3.x: 3 passed
github-branch-master: 3 passed
```

The witness proves:

```text
Search results:
  a compressed FileSearchResponse containing one file with eleven filler
  attributes followed by a valid bitrate attribute is accepted; the final
  bitrate survives parsing.

Browse/share lists:
  a compressed SharedFileListResponse containing one file with the same
  over-budget attribute layout is accepted; the final bitrate survives parsing.

Folder contents:
  a compressed FolderContentsResponse containing one file with the same
  over-budget attribute layout is accepted; the final bitrate survives parsing.
```

The valid attribute is deliberately placed after the known retained file-attribute budget. If a semantic cap were enforced before walking excess pairs, that final attribute would not be consumed and retained under the test design.

## Impact framing

This is a low/medium parser budget hardening item. It is not code execution, not an authentication bypass, and not a standalone peer-only file disclosure.

Likely consequences:

- An accepted result/list payload can spend parser work on excess per-file metadata pairs.
- The broad uncompressed-message cap bounds total decompressed bytes, but does not express the smaller semantic budget for attributes per file.
- The same helper behavior exists across search, browse, and folder-content surfaces, so a single fixed-behavior regression test can cover all three.

The most conservative description is:

```text
Peer-controlled result/list payloads can specify more file-attribute pairs per
file than Nicotine+ semantically uses, and current parsers walk the supplied
count rather than enforcing a small field-level budget.
```

## Why not strict-promoted

This packet is verified, but it does not outrank the current strict candidates:

- **U-123** has a clearer transfer-token/lifetime consequence.
- **PB-01** has a clearer connection identity/generation consequence.
- **SEARCH-RESP-01 / U-163** has a clearer accepted-response token/source/scope binding consequence.

FILE-ATTRIBUTE-BUDGET-01 is lower because:

- attacker cost is proportional to supplied bytes;
- broad uncompressed-message limits already provide a coarse outer bound;
- observed behavior is parser work/availability hardening rather than direct data disclosure or code execution;
- public protocol documentation openly describes a variable attribute-count field, and captured searches found broad adjacent hardening but no exact direct public semantic-count cap report.

## Fix-shape notes

A coherent fix should be small and compatibility-preserving:

```text
- Define a protocol semantic maximum for retained file attributes, likely equal
  to the known retained set size plus any intentional compatibility slack.
- Enforce the cap in the shared file-attribute unpacker, not separately in every
  result/list parser.
- Decide whether excess pairs should be skipped cheaply, rejected as malformed,
  or recorded as a soft parse warning. The safest compatibility path is usually
  bounded skip with tests, unless maintainers prefer strict malformed-message
  rejection.
- Keep the broad uncompressed-message byte cap; this packet complements it with
  a smaller subfield budget.
- Add fixed-behavior tests for search results, shared-file lists, folder
  contents, duplicate valid attributes, excess unknown attributes, and truncated
  attribute data.
```

## Evidence files

```text
evidence/rev0029-file-attribute-budget-pytest-run.txt
evidence/rev0029-file-attribute-budget-source-trace.md
evidence/rev0029-file-attribute-budget-source-trace.json
evidence/rev0029-web-public-overlap-file-attribute-budget.md
```
