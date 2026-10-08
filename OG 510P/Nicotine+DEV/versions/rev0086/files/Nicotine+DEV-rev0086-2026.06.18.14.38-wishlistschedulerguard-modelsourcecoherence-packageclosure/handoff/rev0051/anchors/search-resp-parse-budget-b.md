# Source-anchor capsule — SEARCH-RESP-PARSE-BUDGET-B

These anchors were generated from the external rev0003 source bundle. They support source review of the existing production-gated packet and do not promote a new packet.

|lane|anchor|file:line|role|matched text|
|---|---|---|---|---|
|github-tag-3.3.10|srpbb-fsr-class|pynicotine/slskmessages.py:3234|FileSearchResponse parser class|`class FileSearchResponse(PeerMessage):`|
|github-branch-3.3.x|srpbb-fsr-class|pynicotine/slskmessages.py:3262|FileSearchResponse parser class|`class FileSearchResponse(PeerMessage):`|
|github-branch-master|srpbb-fsr-class|pynicotine/slskmessages.py:3435|FileSearchResponse parser class|`class FileSearchResponse(PeerMessage):`|
|github-tag-3.3.10|srpbb-token-allowed-check|pynicotine/slskmessages.py:3286|accepted-result parsing is reached only after token validation|`if self.token not in SEARCH_TOKENS_ALLOWED:`|
|github-branch-3.3.x|srpbb-token-allowed-check|pynicotine/slskmessages.py:3316|accepted-result parsing is reached only after token validation|`if self.token not in SEARCH_TOKENS_ALLOWED:`|
|github-branch-master|srpbb-token-allowed-check|pynicotine/slskmessages.py:3491|accepted-result parsing is reached only after token validation|`if self.token not in self.allowed_responses:`|
|github-tag-3.3.10|srpbb-rest-decompress|pynicotine/slskmessages.py:3284|accepted response body is decompressed after token validation|`decompressor.decompress(decompressor.unconsumed_tail, username_len + 4), username_len)`|
|github-branch-3.3.x|srpbb-rest-decompress|pynicotine/slskmessages.py:3314|accepted response body is decompressed after token validation|`decompressor.decompress(decompressor.unconsumed_tail, username_len + 4), username_len)`|
|github-branch-master|srpbb-rest-decompress|pynicotine/slskmessages.py:3488|accepted response body is decompressed after token validation|`self._message = memoryview(decompressor.decompress(decompressor.unconsumed_tail, username_len + 4))`|
|github-tag-3.3.10|srpbb-public-result-list|pynicotine/slskmessages.py:3297|public result-list materialization entry|`pos, self.list = self._parse_result_list(message)`|
|github-branch-3.3.x|srpbb-public-result-list|pynicotine/slskmessages.py:3328|public result-list materialization entry|`pos, self.list = self._parse_result_list(message)`|
|github-branch-master|srpbb-public-result-list|pynicotine/slskmessages.py:3503|public result-list materialization entry|`self.list = self._parse_result_list()`|
|github-tag-3.3.10|srpbb-private-result-list|pynicotine/slskmessages.py:3306|private result-list materialization entry|`pos, self.privatelist = self._parse_result_list(message, pos)`|
|github-branch-3.3.x|srpbb-private-result-list|pynicotine/slskmessages.py:3337|private result-list materialization entry|`pos, self.privatelist = self._parse_result_list(message, pos)`|
|github-branch-master|srpbb-private-result-list|pynicotine/slskmessages.py:3512|private result-list materialization entry|`self.privatelist = self._parse_result_list()`|

## Filing guardrail

Use these anchors with the rev0050 minimum-claim capsule. Do not broaden the claim based on file proximity or shared modules.
