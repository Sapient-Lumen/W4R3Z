# Selected fix skeleton — SEARCH-RESP-PARSE-BUDGET-B rev0042

```python
MAX_SEARCH_RESPONSE_RESULT_COUNT = 10000

# after username-prefix and token validation
accepted_result_count_header = decompressor.decompress(decompressor.unconsumed_tail, 4)
if len(accepted_result_count_header) < 4:
    self.token = None
    self.list = []
    return

_pos, accepted_result_count = self.unpack_uint32(accepted_result_count_header)
if accepted_result_count > MAX_SEARCH_RESPONSE_RESULT_COUNT:
    self.token = None
    self.list = []
    self.privatelist = []
    return

# inflate accepted body only after public count passes
# parse public list with MAX_SEARCH_RESPONSE_RESULT_COUNT
# parse private list with remaining budget
```

The lane-specific diffs in this revision show both legacy handler shape and master handler shape.
