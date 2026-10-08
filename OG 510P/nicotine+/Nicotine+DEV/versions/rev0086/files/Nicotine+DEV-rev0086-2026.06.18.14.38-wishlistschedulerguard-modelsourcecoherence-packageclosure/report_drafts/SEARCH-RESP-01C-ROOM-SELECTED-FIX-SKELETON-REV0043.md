# SEARCH-RESP-01C-ROOM selected fix skeleton — rev0043

## Invariant

Room-mode search responses should be source-bound when a request-time local joined-room membership snapshot exists, while preserving broad-source compatibility when no usable local snapshot exists.

## Search creation

In room-mode search-term processing, after plugin room/search-term feedback is applied:

```python
room_obj = getattr(getattr(core, "chatrooms", None), "joined_rooms", {}).get(room)

if room_obj is not None and room_obj.users:
    users = tuple(room_obj.users)
```

The existing `SearchRequest.users` field stores the snapshot. No protocol-message shape changes are required.

## Response admission

In `_file_search_response()` after the `search` object and `username` are available, and before ignored-user/IP policy:

```python
if search.mode == "user":
    expected_users = search.users or ()
    if username not in expected_users:
        msg.token = None
        return

elif search.mode == "buddies" and search.users is not None:
    if username not in search.users:
        msg.token = None
        return

elif search.mode == "rooms" and search.users is not None:
    if username not in search.users:
        msg.token = None
        return
```

## Compatibility notes

- `search.users is None` in room mode means no usable local room snapshot existed at request time; preserve current broad-source behavior.
- An empty joined-room user set should not be treated as authoritative for fail-closed behavior. It can represent a not-yet-populated room state.
- Room membership changes after sending the search should not mutate the accepted source set for that token.
- Global and wishlist modes remain broad-source.

## Regression gate

```bash
PYTHONPATH=/path/to/nicotine-plus pytest -q \
  maintainer_artifacts/search-resp-01/test_search_response_room_scope_fixed_regression.py
```
