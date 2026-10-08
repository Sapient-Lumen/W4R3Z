# Current authority and historical-provenance refactor — rev0080

Rev0079 centralized current revision paths. Rev0080 extends that contract in two ways:

1. `audit_current_source_history.py` is a current script and its contract/output are package authorities.
2. `search-repeat-01` replaces `search-epoch-01` as the open-first artifact. The old artifact remains present but is no longer required by current navigation or package authority.

This prevents three quiet failures:

```text
a current-file audit misses an interacting historical deletion
an old optional architecture branch remains framed as the minimum design
a large historical model stays current merely because later docs keep linking it
```

Current navigation must point to the rev0080 disposition, repeat-policy packet, provenance contract, and probe. It must not point to rev0079 as current authority.
