# SEARCH-AGAIN-EPOCH-01 repeat-policy packet

This rev0080 packet replaces the prior *minimum-architecture* assumption with a four-policy comparison.

```text
current same-token Retry/Merge
clear then same-token retry
fresh-token page replacement
fresh-token in-place transactional refresh
```

## Confirmed regression

Once a page has reached `max_displayed_results`, Search Again re-allows the same token and sends the full request fan-out, but the first returning response immediately retires that token because the stored-result count was never reset. No new row can be displayed. Repeated clicks can therefore emit repeated buddy/user fan-outs while display capacity remains zero.

## Historical interaction

The May 2025 Search Again commit shipped next to a manual **Clear All Results** command. The January 2026 wishlist overhaul removed that command and its handler while leaving same-token Search Again intact. The source-history audit validates both commits from the external content-addressed Git bundle.

## Architecture correction

Rev0078–rev0079 correctly modeled the hard version: an in-place, failure-atomic page migration with a stable logical identity. Rev0080 corrects the claim that this is the minimum implementation of Search Again. If the command is defined as closing one search/page lifetime and creating another with a fresh token, existing best-effort new-search semantics do not require a network-applied acknowledgement. They do require an explicit carry-over policy for filters, tab position, notifications, plugins, wishlist state, and undo history.

No upstream patch is selected. The packet establishes the current defect, retires same-token clearing as an epoch solution, and narrows the next experiment to fresh-token replacement integration.

All files are research-only and are not upstream contribution material.
