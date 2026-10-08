# Missing path review page: moved, deleted, remounted, trash-return, and safe-continue branches interface spec

## Operator question

> this subject disappeared — was it deleted, moved within the same root, moved across roots, remounted later, or merely recoverable from trash, and which continuation branch preserves the most truth?

## Why this page exists

Current official Resilio docs still distinguish these cases, but they do not own them as one stable review.
This page does.

## Branches the page must model

The page must always separate at least these branches:

1. **trash / recycle recovery branch**
2. **same-root move or rename branch**
3. **cross-root rehome branch**
4. **returned-root / remount candidate branch**
5. **fresh-bind branch**
6. **remove-and-readd branch**

## Required sections

### A. Loss-cause hypothesis matrix

Show hypotheses with confidence:

- deleted but recoverable
- moved within same root
- moved across root / partition
- root offline / unmounted
- permission / principal visibility mismatch
- unknown

### B. Supported repair consequences

For each branch show:

- peer continuity effect
- whether subject identity is preserved, reviewed, or replaced
- whether local bytes are reused, re-indexed, or ignored
- whether reconnect prompts or non-empty warnings are expected
- whether the branch is blocked on platform limits

### C. Strong statements blocked by this page

Examples:

- `The subject is gone forever.`
- `This returned path is definitely the same subject.`
- `Continue is safe with zero reconnect cost.`
- `Remove and add again preserves all previous relationships.`

## Example outcomes

- `Recovered from trash at original root; continuity class remains live-bind pending re-index confirmation.`
- `Moved within same root; same-root repair is available and full re-share is not required.`
- `Cross-root rehome detected; path continuity is broken and a reviewed rebind is required.`
- `Returned removable root detected; continue only after remount witness review.`
- `Unknown cause; strongest safe branch is branch-or-rebind review, not silent reconnect.`

## Action rail

Allow only:

- `Restore path from trash`
- `Point at corrected location`
- `Review remount witness`
- `Open rebind proof`
- `Branch as fresh bind`
- `Emit receipt`

Never allow a generic `Fix` button that hides which branch won.
