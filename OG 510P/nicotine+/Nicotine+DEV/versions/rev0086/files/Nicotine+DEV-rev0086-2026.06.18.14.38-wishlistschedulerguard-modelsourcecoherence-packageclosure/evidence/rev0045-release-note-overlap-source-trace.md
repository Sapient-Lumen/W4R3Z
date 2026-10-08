# rev0045 release-note/source overlap trace

## Public release-note context

The public Nicotine+ NEWS page for Version 3.3.11 Release Candidate 1 lists several important corrections relevant to cube triage:

```text
- Enforce maximum sizes for uncompressed network messages to avoid unbounded memory use.
- Prevent file uploads from going through to spoofed users.
- Fixed an issue where peers would sometimes be told our username is theirs.
- Some fixes for incorrect behavior in the distributed search network.
- Fixed a crash when performing a file search in rooms mode with an empty room name.
```

## Local source-bundle context

The provided source bundle's branch lanes include the same family of 3.3.11 RC notes:

```text
source-trees/github-branch-3.3.x/NEWS.md
source-trees/github-branch-master/NEWS.md
```

Static source observations from the bundled lanes:

```text
github-tag-3.3.10: slskproto.py uses MAX_INCOMING_MESSAGE_SIZE = 448 MiB.
github-branch-3.3.x: slskproto.py has LARGE/MEDIUM/SMALL message-size caps; FileSearchResponse has a 128 MiB decompression cap.
github-branch-master: same family of LARGE/MEDIUM/SMALL message-size caps; FileSearchResponse has a 128 MiB decompression cap.
```

## Cube-specific re-score

The broad message-size caps are real hardening, but they do not retire the two search-response parser-budget packets:

```text
SEARCH-RESP-PARSE-BUDGET-A asks for a username-prefix plausibility cap before username_len + 4 decompression.
SEARCH-RESP-PARSE-BUDGET-B asks for a public/private accepted result-row budget before row-object materialization.
```

Rev0045 manual smoke evidence shows both fixed regressions still fail on current branch/master lanes and pass after applying the selected cube patch.

## Refactor outcome

No release-note item is treated as an exact duplicate retirement for U-123, PB-01, SEARCH-RESP-01A/B/C, or SEARCH-RESP-PARSE-BUDGET-A/B in this revision.
