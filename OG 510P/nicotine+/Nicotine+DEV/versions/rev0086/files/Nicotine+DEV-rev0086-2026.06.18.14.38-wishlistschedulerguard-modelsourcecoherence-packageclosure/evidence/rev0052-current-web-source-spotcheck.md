# rev0052 current-web source spotcheck

This is a lightweight web spotcheck, not a full current-upstream source refresh. The build environment could not clone GitHub directly, so rev0052 records only public web observations and keeps the full checkout/rerun as the top queue item.

Observed public context:

- Nicotine+ NEWS still listed Version 3.3.11 Release Candidate 1, including broad corrections for uncompressed network message limits, upload spoofing, username identity, distributed search, and empty-room search crash behavior.
- The GitHub 3.3.11 milestone was observed at 97% complete with open PR #3781 for safe path joining/path traversal.

Observed current master web snippets:

- `pynicotine/transfers.py`: visible snippet showed `_activate_transfer()` assigning `self.active_users[transfer.username][token] = transfer` and `_deactivate_transfer()` deleting `self.active_users[username][token]` without an object-identity comparison in the snippet.
- `pynicotine/slskproto.py`: visible snippet showed `_replace_existing_connection()` popping `username + conn_type` and closing a prior initialized socket.
- `pynicotine/search.py`: visible snippet showed `_file_search_response()` retrieving the `search` by token and `username` before ignored-user/IP filtering, with no user/buddy/room source-admission guard visible in that snippet.
- `pynicotine/slskmessages.py`: public web find did not locate the selected symbolic caps `MAX_SEARCH_RESPONSE_USERNAME_LENGTH` or `MAX_SEARCH_RESPONSE_RESULT_COUNT`.

Decision: retain all seven production-gated packets and their current-source caveat. Do not treat this web spotcheck as proof of current-master exploitability or as a replacement for a clean checkout and rerun.
