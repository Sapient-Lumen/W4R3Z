# Source-anchor capsule — SEARCH-RESP-PARSE-BUDGET-A

These anchors were generated from the external rev0003 source bundle. They support source review of the existing production-gated packet and do not promote a new packet.

|lane|anchor|file:line|role|matched text|
|---|---|---|---|---|
|github-tag-3.3.10|srpba-fsr-class|pynicotine/slskmessages.py:3234|FileSearchResponse parser class|`class FileSearchResponse(PeerMessage):`|
|github-branch-3.3.x|srpba-fsr-class|pynicotine/slskmessages.py:3262|FileSearchResponse parser class|`class FileSearchResponse(PeerMessage):`|
|github-branch-master|srpba-fsr-class|pynicotine/slskmessages.py:3435|FileSearchResponse parser class|`class FileSearchResponse(PeerMessage):`|
|github-tag-3.3.10|srpba-prefix-first-u32|pynicotine/slskmessages.py:3282|parser inflates first four compressed bytes to learn username length|`_pos, username_len = self.unpack_uint32(decompressor.decompress(message, 4))`|
|github-branch-3.3.x|srpba-prefix-first-u32|pynicotine/slskmessages.py:3312|parser inflates first four compressed bytes to learn username length|`_pos, username_len = self.unpack_uint32(decompressor.decompress(message, 4))`|
|github-branch-master|srpba-prefix-first-u32|pynicotine/slskmessages.py:3486|parser inflates first four compressed bytes to learn username length|`self._message = memoryview(decompressor.decompress(self._message, 4))`|
|github-tag-3.3.10|srpba-prefix-username-plus-token|pynicotine/slskmessages.py:3284|parser inflates advertised username prefix plus token before token rejection|`decompressor.decompress(decompressor.unconsumed_tail, username_len + 4), username_len)`|
|github-branch-3.3.x|srpba-prefix-username-plus-token|pynicotine/slskmessages.py:3314|parser inflates advertised username prefix plus token before token rejection|`decompressor.decompress(decompressor.unconsumed_tail, username_len + 4), username_len)`|
|github-branch-master|srpba-prefix-username-plus-token|pynicotine/slskmessages.py:3488|parser inflates advertised username prefix plus token before token rejection|`self._message = memoryview(decompressor.decompress(decompressor.unconsumed_tail, username_len + 4))`|
|github-tag-3.3.10|srpba-token-allowed-check|pynicotine/slskmessages.py:3286|token allow-list check occurs after prefix materialization|`if self.token not in SEARCH_TOKENS_ALLOWED:`|
|github-branch-3.3.x|srpba-token-allowed-check|pynicotine/slskmessages.py:3316|token allow-list check occurs after prefix materialization|`if self.token not in SEARCH_TOKENS_ALLOWED:`|
|github-branch-master|srpba-token-allowed-check|pynicotine/slskmessages.py:3491|token allow-list check occurs after prefix materialization|`if self.token not in self.allowed_responses:`|

## Filing guardrail

Use these anchors with the rev0050 minimum-claim capsule. Do not broaden the claim based on file proximity or shared modules.
