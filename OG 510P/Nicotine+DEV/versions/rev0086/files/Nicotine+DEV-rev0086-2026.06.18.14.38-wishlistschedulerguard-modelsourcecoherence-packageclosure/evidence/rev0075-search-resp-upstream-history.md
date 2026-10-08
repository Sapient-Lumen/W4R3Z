# SEARCH-RESP-01A upstream history evidence — rev0075

Source: local full Git repository corresponding to the supplied source bundle. No upstream source tree is embedded in this cube.

## Payload username compatibility decision

```text
commit 5e3e8fcd1d4fa1965976fd29595784a4dcaad3d6
AuthorDate: 2021-07-08
Title: Use username from PeerInit object for search results
```

Commit message:

```text
There are still old Museek clients around that send the wrong username in
FileSearchResult messages. Use the username associated with the peer
connection instead.
```

The diff changes result attribution from the response payload's username to `conn.init.target_user`. This is the direct historical reason the current result source and the payload username are separate values.

## Current upstream acknowledgement of spoofability

```text
commit a942fe46539a68510cd17fa207474a43f08a4164
AuthorDate: 2026-01-12
Title: shares.py: only grant 'public' perimission level for own username
```

The code comment says username spoofing cannot be fully prevented in the Soulseek protocol and avoids granting buddy/trusted permission to the local user's own username.

```text
commit f5f535906403c84b6863ef98dbba6fb28659118a
AuthorDate: 2026-01-12
Title: downloads.py: disallow files sent from our own username
```

This adjacent hardening rejects arbitrary uploads attributed to the local username because it is an obvious spoofing choice.

These commits do not adjudicate SEARCH-RESP-01A. They are probative of the trust boundary: a username attached to a peer connection is not generally equivalent to authenticated identity.

## Current-master continuity

The captured current master still assigns peer-message usernames from `conn.init.target_user` and still does not compare a user search's expected users in `_file_search_response()`. It moves allowed-response IDs into the network thread, which strengthens parser correlation but does not bind an allowed token to a username.

## Commands used

```bash
git show --format=fuller 5e3e8fcd1d4fa1965976fd29595784a4dcaad3d6 -- pynicotine/pynicotine.py
git show --format=fuller a942fe46539a68510cd17fa207474a43f08a4164 -- pynicotine/shares.py
git show --format=fuller f5f535906403c84b6863ef98dbba6fb28659118a -- pynicotine/downloads.py
git show upstream/master:pynicotine/search.py
git show upstream/master:pynicotine/slskproto.py
```

Interpretation: the rev0039 guard can enforce a local source-set invariant, but its compared username is not an authentication primitive.
