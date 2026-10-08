# rev0289 cube deep audit

## Finding

The cube now has strong gates through terminal live-window readout, post-readout dispatch, and dated recheck. The next failure mode is provenance drift when a recheck says new owner context exists: the actual returned context must not be confused with the recheck artifact or with an old first-contact clock.

## Audit result

Before `rev0289`, the router could say “route actual new owner context through `owner-field-next CSV=...`,” but the returned-CSV branch still preferred active contact-status clocks. That was safe for ordinary first/reask replies but stale for post-readout owner context.

## Refactor

`rev0289` adds a context receipt recorder, guard, lint check, router branch, and intake/seed provenance split. The returned CSV path now has a post-readout branch:

1. source recheck says `new_owner_context_available`;
2. actual CSV/source packet is hash-linked in `post-readout-context-receipt.json`;
3. intake runs from `SOURCE_POST_READOUT_CONTEXT_RECEIPT`;
4. workbench seed revalidates that same provenance.

## Waste removed

This removes a likely future doctrinal distinction between “context discovered by recheck” and “initial owner reply.” The distinction is now executable and hash-checked. The archive remains large, but this change reduces operator-memory load at a late, high-risk handoff.
