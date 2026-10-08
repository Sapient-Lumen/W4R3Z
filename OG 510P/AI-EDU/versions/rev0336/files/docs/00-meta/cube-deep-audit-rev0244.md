# Cube deep audit rev0244 — executable owner-reply triage

## Finding

Rev0243 made the first `FT-0181` owner reply easy to fill, but the next handoff was still too
human-memory dependent. A maintainer receiving a CSV had to remember the blocked-material rules,
authority boundary, claim ceiling, and staging path from several Markdown surfaces before opening the
owner packet workbench.

That is a real forward-motion risk. The cube could receive a useful small reply and still lose time
in manual interpretation, or worse, paste an unsafe CSV into a downstream form because the inbound
classification was prose-only.

## Change made

Rev0244 adds `tools/triage_owner_reply_csv.py`, a local conservative classifier for returned
`FT-0181` eight-row owner-reply CSVs. It returns one intake outcome before the workbench opens:

- `PROCEED-STAGED` for a minimized, answered eight-row owner reply;
- `RE-ASK-ONCE` for malformed CSVs or one/two missing or ambiguous rows;
- `NO-OWNER-PACKET` for a blank template or mostly absent reply;
- `BLOCK-OVERBROAD`, `BLOCK-PROTECTED`, `BLOCK-SECURITY`, `BLOCK-AUTHORITY`, or `BLOCK-EVIDENCE` for
  unsafe or unsupported material.

`tools/check_owner_reply_triage.py` self-tests the classifier on generated local fixtures. The tests
cover blank, safe staged, protected, overbroad, authority-failing, and unsupported-claim replies
without adding any synthetic packet to the evidence plane.

## Refactor principle

The tool is not another registry. It is a receipt-side reducer:

1. run the CSV through the tool;
2. stage only if the outcome is `PROCEED-STAGED`;
3. otherwise re-ask once, block, quarantine locally, or record `NO-OWNER-PACKET`;
4. do not widen the request and do not treat the classification as evidence.

## Waste removed

Before rev0244, the first returned CSV had three unnecessary failure modes:

- a maintainer could open the full workbench before classifying the reply;
- security payloads were discussed in some docs but not in the first result table;
- no executable check proved the blank template, staged packet, and common block cases routed
  consistently.

Rev0244 closes those gaps while leaving `FT-0181` open and externally gated.

## Still missing

No owner has been contacted. No filled owner CSV has returned. No `SRC2+` evidence has been imported.
The classifier only helps the cube avoid wasting or mishandling the first real reply when it arrives.
