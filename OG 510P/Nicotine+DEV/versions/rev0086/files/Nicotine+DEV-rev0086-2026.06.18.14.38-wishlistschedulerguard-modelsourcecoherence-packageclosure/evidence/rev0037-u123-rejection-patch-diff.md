# rev0037 U-123 selected prototype patch diff

This is a prototype maintainer fix shape, not an embedded source tree. The same logical diff applied cleanly to `github-tag-3.3.10`, `github-branch-3.3.x`, and `github-branch-master` in the archived source bundle.

```diff
--- a/pynicotine/transfers.py
+++ b/pynicotine/transfers.py
@@ -551,13 +551,20 @@
         username = transfer.username
         token = transfer.token
 
-        if token is None or token not in self.active_users.get(username, {}):
+        if token is None:
             return False
 
-        del self.active_users[username][token]
-
-        if not self.active_users[username]:
-            del self.active_users[username]
+        active_transfers = self.active_users.get(username, {})
+        active_transfer = active_transfers.get(token)
+        deactivated = False
+
+        if active_transfer is transfer:
+            del active_transfers[token]
+
+            if not active_transfers:
+                del self.active_users[username]
+
+            deactivated = True
 
         if transfer.speed > 0:
             self.total_bandwidth = max(0, self.total_bandwidth - transfer.speed)
@@ -570,7 +577,7 @@
         transfer.sock = None
         transfer.token = None
 
-        return True
+        return deactivated
 
     def _fail_transfer(self, transfer):
         self.failed_users[transfer.username][transfer.virtual_path] = transfer

--- a/pynicotine/downloads.py
+++ b/pynicotine/downloads.py
@@ -1054,6 +1054,14 @@
 
         download = (self.queued_users.get(username, {}).get(virtual_path)
                     or self.failed_users.get(username, {}).get(virtual_path))
+        active_download = self.active_users.get(username, {}).get(token)
+
+        if active_download is not None and active_download is not download:
+            log.add_transfer("Rejected duplicate download request with token %s for file %s from user %s; "
+                             "token is already bound to active file %s",
+                             (token, virtual_path, username, active_download.virtual_path))
+            reason = TransferRejectReason.QUEUED if download is not None else TransferRejectReason.CANCELLED
+            return TransferResponse(allowed=False, reason=reason, token=token)
 
         if download is not None:
             # Remote peer is signaling a transfer is ready, attempting to download it

```
