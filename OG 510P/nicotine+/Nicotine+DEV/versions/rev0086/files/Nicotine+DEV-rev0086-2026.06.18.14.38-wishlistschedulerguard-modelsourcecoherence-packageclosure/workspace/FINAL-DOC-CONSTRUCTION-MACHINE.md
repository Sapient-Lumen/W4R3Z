# Final-document construction machine

The office machine for this cube is simple: every row moves through gates, and the final documents are generated from gate state rather than edited by vibes.

## Outputs being built

1. `docs/HIGH-PRIORITY-HIGH-QUALITY.md` — strict lane. It should be empty unless a finding survives source lock, public-overlap, duplicate, and verification gates.
2. `docs/AUDITED-BACKLOG-RANKED.md` — broad lane. It can include public-adjacent, known, low-confidence, regression, and future-source overlap items, but each row must say why it is there.

## Per-finding gate sequence

```text
seeded -> source-shaped -> public-searched -> duplicate-checked -> verified/downgraded -> document-assigned
```

## Evidence records

Each promoted or downgraded finding should have a workpacket with:

- exact title and ID;
- root invariant;
- affected lanes: 3.3.10, 3.3.x, master;
- public-overlap query list;
- public-overlap conclusion;
- source snippets or file/line anchors;
- reproduction or static proof notes;
- severity boundary;
- proposed fix shape;
- final document destination.

## rev0005 operating rule

From rev0005 onward, the cube may not call a finding `fresh` in a final-facing document unless its public-overlap record says `candidate no-direct-public-found` or stronger, and includes searches. Items with release-note, issue, discussion, PR, or source-lane overlap remain useful, but they belong in the broad/backlog document or in a regression/backport section.
