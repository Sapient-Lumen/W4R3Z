# Strict/front source-refresh re-score — rev0045

Rev0045 follows the rev0044 instruction to re-score before opening any new row. No new production packet is added here. The goal is to consolidate the seven production-gated packets, compare them with the current release-note/source context carried by the provided source bundle, and preserve a filing-ready index.

## Inputs

```text
previous cube: rev0044
external source bundle: Nicotine+DEV-rev0003-upstream-sources-20260612T181540Z
source lanes: github-tag-3.3.10, github-branch-3.3.x, github-branch-master
public context checked: Nicotine+ NEWS / 3.3.11 Release Candidate 1 and protocol documentation
```

The source bundle already carries 3.3.11 RC NEWS entries in `github-branch-3.3.x` and `github-branch-master`. Those release notes include broad network-message-size and identity-adjacent corrections, so rev0045 treats them as overlap context rather than ignoring them.

## Rerun method

The inherited all-in-one wrapper helpers were too heavy in this environment and produced timeouts/OOM behavior when they tried to run many failing pytest cases in one process. Rev0045 therefore uses a leaner gate:

```text
1. On current source, run each fixed-behavior regression with --maxfail=1 and require an expected failure.
2. Copy the lane's pynicotine package into a temporary checkout.
3. Apply the selected cube patch/skeleton for that packet.
4. Run the full fixed-behavior regression and require a pass.
```

This preserves the important source-refresh signal without materializing full failing matrices repeatedly.

## Source-refresh result

```text
production-gated packets before rev0045: 7
production-gated packets retained:       7
new production-gated packets in rev0045: 0
packets retired by 3.3.11 RC overlap:   0
```

Retained packets:

```text
U-123
PB-01
SEARCH-RESP-01A
SEARCH-RESP-01B-BUDDY
SEARCH-RESP-01C-ROOM
SEARCH-RESP-PARSE-BUDGET-A
SEARCH-RESP-PARSE-BUDGET-B
```

## Evidence map

```text
evidence/rev0045-u123-manual-source-refresh.txt
evidence/rev0045-u123-selected-patch-pass.txt
evidence/rev0045-pb01-manual-source-refresh.txt
evidence/rev0045-searchresp01a-manual-source-refresh.txt
evidence/rev0045-searchresp01b-manual-source-refresh.txt
evidence/rev0045-searchresp-prefixbudget-manual-source-refresh.txt
evidence/rev0045-searchresp-resultbudget-manual-source-refresh.txt
evidence/rev0045-searchresp-roomscope-manual-source-refresh.txt
evidence/rev0045-release-note-overlap-source-trace.md
```

The structured summary is in:

```text
data/rev0045_strict_packet_index.csv/json
data/rev0045_strict_source_refresh_matrix.csv/json
data/rev0045_release_note_overlap_rescore.csv/json
```

## Decision

Rev0045 retains all seven strict/front packets as production-gated maintainer packets. The 3.3.11 RC release-note entries are meaningful context, especially for broad network-message-size caps and identity-adjacent fixes, but the rev0045 smoke gates still show current archived branch/master source failing the packet-specific fixed regressions until the selected cube patch is applied.
