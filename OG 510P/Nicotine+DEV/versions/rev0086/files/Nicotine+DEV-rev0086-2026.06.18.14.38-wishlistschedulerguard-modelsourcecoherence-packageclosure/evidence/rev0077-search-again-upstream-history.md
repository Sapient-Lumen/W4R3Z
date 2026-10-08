# rev0077 Search Again upstream-history evidence

## Local full-history result

```text
commit:  d8ffe30c773ab059899b825eeeb5c073833e6f3d
date:    2025-05-02T02:28:55+03:00
subject: search.py: refactor search requests to allow searching again
```

Before that refactor, `do_peer_search()` used the component-wide `self.token` both for `_own_tokens` and the outgoing `UserSearch`. The refactor introduced stored `SearchRequest` objects and changed the outgoing message to `search.token`, but left the adjacent authorization write as `self.token`.

Condensed transition:

```diff
-def do_peer_search(self, text, users):
-    for username in users:
+def _send_peer_search_request(self, search):
+    for username in search.users:
         if username == core.users.login_username:
             self._own_tokens.add(self.token)
-        core.send_message_to_server(UserSearch(username, self.token, text))
+        core.send_message_to_server(
+            UserSearch(username, search.token, search.term_transmitted)
+        )
```

At executable proxy `f4e17d59783dbc48ea31d2e899a681e2dd1ed500`, blame assigns the function and wire-token expressions to `d8ffe30c77`, while `_own_tokens.add(self.token)` still traces to `314af37ec2` from 2024. This is strong provenance for a stale owner reference rather than a deliberate split-token policy.

## Branch boundary

The exact supported `3.3.x` lane does not expose the reusable `send_search_request(existing_token)` Search Again path. The defect is therefore classified as master/3.4.0-line behavior, not as a confirmed defect in the exact supported branch.

## Reproduction boundary

The history explains how the mismatch arose but does not prove runtime impact by itself. Runtime evidence is in:

```text
data/rev0077_search_again_test_matrix.csv
data/rev0077_search_again_summary.json
evidence/rev0077-search-again-runtime/
```
