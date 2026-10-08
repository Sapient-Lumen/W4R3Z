# Selected fix skeleton — SEARCH-RESP-PARSE-BUDGET-A — rev0041

## Legacy parser shape

```python
_pos, username_len = self.unpack_uint32(decompressor.decompress(message, 4))

if username_len > MAX_SEARCH_RESPONSE_USERNAME_LENGTH:
    self.token = None
    self.list = []
    return

_pos, self.token = self.unpack_uint32(
    decompressor.decompress(decompressor.unconsumed_tail, username_len + 4), username_len)
```

## Master parser shape

```python
self._offset = username_len = self.unpack_uint32()

if username_len > MAX_SEARCH_RESPONSE_USERNAME_LENGTH:
    self.token = None
    return

self._message = memoryview(decompressor.decompress(decompressor.unconsumed_tail, username_len + 4))
self.token = self.unpack_uint32()
```

## Maintainer choices

- Replace `255` with an existing username-limit constant if one exists.
- Prefer returning without result admission over trying to continue parsing after an implausible prefix.
- Keep accepted result-list caps as a separate patch to avoid changing result compatibility in the prefix fix.
