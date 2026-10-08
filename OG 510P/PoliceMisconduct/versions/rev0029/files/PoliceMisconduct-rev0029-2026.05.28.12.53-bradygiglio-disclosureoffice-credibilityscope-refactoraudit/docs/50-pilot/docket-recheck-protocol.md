# Docket recheck protocol — rev0005

This protocol is the gate between a status signal and a current-status candidate.

## Status signal examples

- DOJ cases page label: `Enforcement`, `Closed`, `Investigation`.
- DOJ press release: court terminated decree, motion filed, agreement completed, lawsuit dismissed.
- Monitor page: sustainment/compliance assessment.
- Court document: order entering, modifying, partially terminating, or terminating a decree.

## Minimum before current-status candidate

1. Identify the court, case caption, and docket number or reliable docket path.
2. Locate the latest relevant order or docket entry.
3. Distinguish motion from order, partial from full termination, dismissal from closure, and retraction from record deletion.
4. Check whether monitor/local/state surfaces continue after federal action.
5. Attach rollback triggers: appeal, later modification, page correction, monitor report, city/local page contradiction.
6. Write public copy with source scope and uncertainty.

## Forbidden shortcuts

- Do not convert a press release into a current-status claim.
- Do not convert a cases-page label into a current-status claim.
- Do not treat dismissal/retraction as history erasure.
- Do not extract officer/civilian names while conducting status rechecks.

## First test queue

1. New Orleans — same-owner conflict: cases page `Enforcement`, press release terminal event.
2. Newark — same-owner conflict: cases page `Enforcement`, press release terminal event.
3. Cleveland — motion-to-terminate signal; needs post-motion order check.
