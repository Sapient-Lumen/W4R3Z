# Source trace — SEARCH-RESP-PARSE-BUDGET-A — rev0041

All three archived lanes parse `FileSearchResponse` by first inflating four bytes of compressed data to read a username-length prefix, then asking zlib for `username_len + 4` bytes so the token can be unpacked.

| lane | parser shape | trace |
|---|---|---|
| github-tag-3.3.10 | legacy | `decompress(message, 4)` for `username_len`, then `decompress(unconsumed_tail, username_len + 4)` before token admission. |
| github-branch-3.3.x | legacy | Same prefix/token pattern; later result-body limits do not bound the pre-token username prefix. |
| github-branch-master | memoryview/master | `decompress(self._message, 4)`, `_offset = username_len`, then `decompress(unconsumed_tail, username_len + 4)` before token validation. |

Result: the fix belongs immediately after `username_len` is decoded and before any `username_len + 4` decompression call.
