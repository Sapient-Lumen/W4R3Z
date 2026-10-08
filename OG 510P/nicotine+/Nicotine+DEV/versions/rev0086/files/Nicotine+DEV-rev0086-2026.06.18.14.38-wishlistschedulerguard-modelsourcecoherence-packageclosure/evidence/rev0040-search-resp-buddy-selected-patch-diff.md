# rev0040 SEARCH-RESP-01B selected patch diffs

The selected patch records a request-time buddy recipient snapshot and applies direct-user plus buddy source-set admission checks.

## github-tag-3.3.10

```diff
--- /mnt/data/source_work/Nicotine+DEV-rev0003-upstream-sources-20260612T181540Z/source-trees/github-tag-3.3.10/pynicotine/search.py	2026-06-12 18:15:58.000000000 +0000
+++ /mnt/data/rev0040_patch_consistency/source-trees/github-tag-3.3.10/pynicotine/search.py	2026-06-15 05:28:20.189123747 +0000
@@ -280,6 +280,8 @@
             if feedback is not None:
                 search_term = feedback[0]
 
+            users = tuple(core.buddies.users)
+
         elif mode == "user":
             if not users:
                 users = [core.users.login_username]
@@ -328,7 +330,7 @@
             self.do_rooms_search(search.term_transmitted, room)
 
         elif mode == "buddies":
-            self.do_buddies_search(search.term_transmitted)
+            self.do_buddies_search(search.term_transmitted, search.users)
 
         elif mode == "user":
             self.do_peer_search(search.term_transmitted, users)
@@ -346,8 +348,11 @@
     def do_rooms_search(self, text, room):
         core.send_message_to_server(RoomSearch(room, self.token, text))
 
-    def do_buddies_search(self, text):
-        for username in core.buddies.users:
+    def do_buddies_search(self, text, users=None):
+        if users is None:
+            users = tuple(core.buddies.users)
+
+        for username in users:
             core.send_message_to_server(UserSearch(username, self.token, text))
 
     def do_peer_search(self, text, users):
@@ -463,6 +468,19 @@
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
+        elif search.mode == "buddies" and search.users is not None:
+            if username not in search.users:
+                msg.token = None
+                return
+
         ip_address, _port = msg.addr
 
         if core.network_filter.is_user_ignored(username):
```

## github-branch-3.3.x

```diff
--- /mnt/data/source_work/Nicotine+DEV-rev0003-upstream-sources-20260612T181540Z/source-trees/github-branch-3.3.x/pynicotine/search.py	2026-06-12 18:15:58.000000000 +0000
+++ /mnt/data/rev0040_patch_consistency/source-trees/github-branch-3.3.x/pynicotine/search.py	2026-06-15 05:28:22.260685503 +0000
@@ -280,6 +280,8 @@
             if feedback is not None:
                 search_term = feedback[0]
 
+            users = tuple(core.buddies.users)
+
         elif mode == "user":
             if not users:
                 users = [core.users.login_username]
@@ -328,7 +330,7 @@
             self.do_rooms_search(search.term_transmitted, room)
 
         elif mode == "buddies":
-            self.do_buddies_search(search.term_transmitted)
+            self.do_buddies_search(search.term_transmitted, search.users)
 
         elif mode == "user":
             self.do_peer_search(search.term_transmitted, users)
@@ -346,8 +348,11 @@
     def do_rooms_search(self, text, room):
         core.send_message_to_server(RoomSearch(room, self.token, text))
 
-    def do_buddies_search(self, text):
-        for username in core.buddies.users:
+    def do_buddies_search(self, text, users=None):
+        if users is None:
+            users = tuple(core.buddies.users)
+
+        for username in users:
             core.send_message_to_server(UserSearch(username, self.token, text))
 
     def do_peer_search(self, text, users):
@@ -463,6 +468,19 @@
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
+        elif search.mode == "buddies" and search.users is not None:
+            if username not in search.users:
+                msg.token = None
+                return
+
         ip_address, _port = msg.addr
 
         if core.network_filter.is_user_ignored(username):
```

## github-branch-master

```diff
--- /mnt/data/source_work/Nicotine+DEV-rev0003-upstream-sources-20260612T181540Z/source-trees/github-branch-master/pynicotine/search.py	2026-06-12 18:15:58.000000000 +0000
+++ /mnt/data/rev0040_patch_consistency/source-trees/github-branch-master/pynicotine/search.py	2026-06-15 05:28:24.444049261 +0000
@@ -481,6 +481,8 @@
             if feedback is not None:
                 search_term = feedback[0]
 
+            users = tuple(core.buddies.users)
+
         elif mode == "user":
             if not users:
                 users = [core.users.login_username or config.sections["server"]["login"]]
@@ -508,7 +510,9 @@
         core.send_message_to_server(RoomSearch(search.room, search.token, search.term_transmitted))
 
     def _send_buddies_search_request(self, search):
-        for username in core.buddies.users:
+        users = search.users if search.users is not None else tuple(core.buddies.users)
+
+        for username in users:
             core.send_message_to_server(UserSearch(username, search.token, search.term_transmitted))
 
     def _send_peer_search_request(self, search):
@@ -627,6 +631,18 @@
             msg.token = None
             return
 
+        if search.mode == "user":
+            expected_users = search.users or ()
+
+            if username not in expected_users:
+                msg.token = None
+                return
+
+        elif search.mode == "buddies" and search.users is not None:
+            if username not in search.users:
+                msg.token = None
+                return
+
         if isinstance(search, WishSearchRequest) and (search.is_ignored or username in search.ignored_users):
             msg.token = None
             return
```

