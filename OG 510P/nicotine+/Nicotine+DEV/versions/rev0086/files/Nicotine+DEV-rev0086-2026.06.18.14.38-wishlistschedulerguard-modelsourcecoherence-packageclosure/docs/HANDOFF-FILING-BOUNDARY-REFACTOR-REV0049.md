# Handoff filing boundary refactor — rev0049

Rev0049 refactors the handoff boundary into two categories.

## Private maintainer packets

These remain production-gated and unchanged:

```text
U-123
PB-01
SEARCH-RESP-01A
SEARCH-RESP-01B-BUDDY
SEARCH-RESP-01C-ROOM
SEARCH-RESP-PARSE-BUDGET-A
SEARCH-RESP-PARSE-BUDGET-B
```

## Public/context-only rows

These are not private packets:

```text
PUBLIC-PATH-JOIN-PR-3781
PUBLIC-PATH-JOIN-PR-3723
```

## Refactor rule

Do not group rows merely because they are security-adjacent or appear in the same release cycle. The cube groups by invariant:

- transfer-session identity;
- peer primary-election compatibility;
- FileSearchResponse source admission;
- FileSearchResponse parser budget;
- public path joining/source-refresh context.

This prevents both over-reporting and accidental duplicate/private restatement of public maintainer work.
