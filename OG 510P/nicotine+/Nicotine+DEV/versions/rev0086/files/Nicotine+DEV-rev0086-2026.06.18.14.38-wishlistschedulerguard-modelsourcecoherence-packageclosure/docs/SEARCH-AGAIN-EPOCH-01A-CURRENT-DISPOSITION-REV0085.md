# SEARCH-AGAIN-EPOCH-01A current disposition — rev0085

```text
scope: ordinary global, room, buddy, and user SearchRequest pages
status: open-native-ui-validation
selected patch: none
security route: not applicable
```

Same-token Search Again remains a confirmed low-severity correctness defect at
the display cap. The cumulative rev0085 research candidate retains the
fresh-token, same-page rekey developed in rev0081–rev0084, with stable page and
notification identity and no old-token alias registry.

Rev0085 narrows the eligibility rule to request ownership. Ordinary
`SearchRequest` pages remain refreshable; persistent `WishSearchRequest` pages
do not. This prevents GUI mode strings from deciding core lifecycle policy.

The remaining gate is native GTK3/GTK4 behavior: focus, active page, unread
state, filters, grouping, sort, expansion, selection, scroll, rapid repeat,
close, and online/offline transitions. No implementation is selected.
