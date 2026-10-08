# rev0039 selected SEARCH-RESP-01A patch diffs

The selected patch is intentionally narrow: user-scoped searches reject `FileSearchResponse` events from peers outside the requested `search.users` set, while global, room, wishlist, and buddy modes remain unchanged in this revision.

## 3.3.10 / 3.3.x handler shape

```diff
--- a/pynicotine/search.py
+++ b/pynicotine/search.py
@@ -463,6 +463,14 @@
             return

         username = msg.username
+
+        if search.mode == "user":
+            expected_users = search.users or ()
+
+            if username not in expected_users:
+                msg.token = None
+                return
+
         ip_address, _port = msg.addr

         if core.network_filter.is_user_ignored(username):
```

## master handler shape

```diff
--- a/pynicotine/search.py
+++ b/pynicotine/search.py
@@ -627,6 +627,13 @@
             msg.token = None
             return

+        if search.mode == "user":
+            expected_users = search.users or ()
+
+            if username not in expected_users:
+                msg.token = None
+                return
+
         if isinstance(search, WishSearchRequest) and (search.is_ignored or username in search.ignored_users):
             msg.token = None
             return
```
