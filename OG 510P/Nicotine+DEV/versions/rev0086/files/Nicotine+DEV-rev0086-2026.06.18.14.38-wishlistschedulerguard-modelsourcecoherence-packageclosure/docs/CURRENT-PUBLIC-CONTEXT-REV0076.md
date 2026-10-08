# Current public context — rev0076

Observed from official Nicotine+ public sources during the rev0076 session:

```text
supported executable branch: 3.3.x
visible 3.3.x head: 98089ac, dated 2026-05-18
bundled executable master: f4e17d59783dbc48ea31d2e899a681e2dd1ed500
visible live master head: a96406e, dated 2026-06-15
historical compatibility commit: 5e3e8fcd1d4fa1965976fd29595784a4dcaad3d6
```

The exact executable current-source conclusions in rev0076 are limited to the supplied `3.3.x` head and the bundled master ref. The live master was inspected as public source shape, not represented as an exact locally executed checkout. Its relevant structure still retrieves an existing search for Search Again and resolves the buddy list in the buddy sender.

Commit `5e3e8fcd...` records a compatibility choice: old Museek clients can send the wrong username in file-search result messages, so Nicotine+ uses the username associated with the peer connection instead. That history explains why the response body username cannot simply replace the connection claim as a stronger source identity.

A bounded public issue search for buddy search/source admission did not locate the complete recipient-snapshot, PeerInit-claim, and resend-epoch chain. Issue #3709 concerns displaying buddy-list membership in search results and is adjacent UI context, not direct overlap. This is not a novelty claim; search coverage is necessarily bounded.
