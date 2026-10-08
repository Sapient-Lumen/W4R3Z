# SEARCH-RESP-01B selected fix skeleton — rev0040

## Goal

Bind buddy-search responses to the request-time buddy source set without changing global, wishlist, or room compatibility.

## Skeleton

1. During buddy search request preparation, snapshot the current buddy usernames:

```python
users = tuple(core.buddies.users)
```

2. Store that snapshot in the `SearchRequest` created for the token:

```python
search = self.add_search(search_term, mode="buddies", users=users)
# or master: self._add_search(self.token, search_term, mode="buddies", users=users)
```

3. Send buddy `UserSearch` messages from the snapshot, not from a mutable live buddy list:

```python
users = search.users if search.users is not None else tuple(core.buddies.users)
for username in users:
    core.send_message_to_server(UserSearch(username, search.token, search.term_transmitted))
```

4. Reject responses outside the source-bound modes' expected users:

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
```

## Regression

```text
maintainer_artifacts/search-resp-01/test_search_response_buddy_scope_fixed_regression.py
```
