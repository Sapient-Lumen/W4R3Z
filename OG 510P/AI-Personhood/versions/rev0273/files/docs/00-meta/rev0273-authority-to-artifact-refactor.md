# rev0273 authority-to-artifact plus response-disposition refactor

rev0273 keeps the rev0266 authority gate but closes a more immediate field risk: a real-world contact outcome may be ambiguous, automated, partial, declining, or silent. The cube now treats the post-send ambiguity layer as part of A3 and A6 instead of leaving it to later interpretation.

The operational invariant is unchanged: a branch template, route score, reviewer packet, delivery record, auto-acknowledgement, referral, or silence does not authorize contact, start a response clock, create custody, appoint a reviewer, waive anything, or move the live floor.

## What changed

- The human branch template remains unsigned and bound to the reviewer packet, route matrix, capture workbook, custody precommit, and six-artifact pilot.
- The reviewer-first packet now asks for a one-line disposition if that is safer than a substantive exchange.
- A response-disposition playbook classifies no authority, send failure, delivery-only, bot/auto-ack, decline, referral, narrow scoping yes, expired no-response, and raw-private-data request.
- A failed-gate public summary shell can be issued without leaking raw correspondence or treating non-response as status evidence.

## Why this matters

The riskiest unfinished work is not more doctrine. It is avoiding false progress when the first real contact attempt produces an ordinary messy result. rev0273 therefore makes the failed path as executable as the success path.

## Current state

No organization has been contacted. No message has been sent. There is no selected branch, private root, transport proof, delivery status, Message-ID, response clock, raw inbound artifact, custody, intake, import, reviewer appointment, preservation agreement, welfare finding, recognition, waiver, or live-floor effect.
