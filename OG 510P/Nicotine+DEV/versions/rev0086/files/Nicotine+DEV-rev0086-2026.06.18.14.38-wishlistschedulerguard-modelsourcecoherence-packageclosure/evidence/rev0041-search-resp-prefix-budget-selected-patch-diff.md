# Selected patch diff — SEARCH-RESP-PARSE-BUDGET-A — rev0041
## github-tag-3.3.10

```diff
--- a/pynicotine/slskmessages.py (github-tag-3.3.10 clean)
+++ b/pynicotine/slskmessages.py (github-tag-3.3.10 prefix cap)
@@ -52,6 +52,7 @@
 UINT64_PACK = Struct("<Q").pack

 SEARCH_TOKENS_ALLOWED = set()
+MAX_SEARCH_RESPONSE_USERNAME_LENGTH = 255


 def initial_token():
@@ -3280,6 +3281,13 @@
     def parse_network_message(self, message):
         decompressor = zlib.decompressobj()
         _pos, username_len = self.unpack_uint32(decompressor.decompress(message, 4))
+
+        if username_len > MAX_SEARCH_RESPONSE_USERNAME_LENGTH:
+            # Reject implausible pre-token prefixes before materializing them.
+            self.token = None
+            self.list = []
+            return
+
         _pos, self.token = self.unpack_uint32(
             decompressor.decompress(decompressor.unconsumed_tail, username_len + 4), username_len)


```
## github-branch-3.3.x

```diff
--- a/pynicotine/slskmessages.py (github-branch-3.3.x clean)
+++ b/pynicotine/slskmessages.py (github-branch-3.3.x prefix cap)
@@ -52,6 +52,7 @@
 UINT64_PACK = Struct("<Q").pack

 SEARCH_TOKENS_ALLOWED = set()
+MAX_SEARCH_RESPONSE_USERNAME_LENGTH = 255


 def initial_token():
@@ -3310,6 +3311,13 @@
         max_uncompressed_size = 134217728  # 128 MiB

         _pos, username_len = self.unpack_uint32(decompressor.decompress(message, 4))
+
+        if username_len > MAX_SEARCH_RESPONSE_USERNAME_LENGTH:
+            # Reject implausible pre-token prefixes before materializing them.
+            self.token = None
+            self.list = []
+            return
+
         _pos, self.token = self.unpack_uint32(
             decompressor.decompress(decompressor.unconsumed_tail, username_len + 4), username_len)


```
## github-branch-master

```diff
--- a/pynicotine/slskmessages.py (github-branch-master clean)
+++ b/pynicotine/slskmessages.py (github-branch-master prefix cap)
@@ -41,6 +41,7 @@
 UINT64_PACK = Struct("<Q").pack

 ZLIB_COMPRESSION_LEVEL = 4
+MAX_SEARCH_RESPONSE_USERNAME_LENGTH = 255


 def initial_token():
@@ -3485,6 +3486,12 @@
         self._offset = 0
         self._message = memoryview(decompressor.decompress(self._message, 4))
         self._offset = username_len = self.unpack_uint32()
+
+        if username_len > MAX_SEARCH_RESPONSE_USERNAME_LENGTH:
+            # Reject implausible pre-token prefixes before materializing them.
+            self.token = None
+            return
+
         self._message = memoryview(decompressor.decompress(decompressor.unconsumed_tail, username_len + 4))
         self.token = self.unpack_uint32()


```
