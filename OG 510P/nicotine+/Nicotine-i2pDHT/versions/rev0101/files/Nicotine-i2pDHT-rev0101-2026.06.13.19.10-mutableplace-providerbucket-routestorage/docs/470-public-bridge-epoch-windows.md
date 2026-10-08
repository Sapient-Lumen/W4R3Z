# Public bridge epoch windows

`bridgeepoch.py` treats public bridge exposure as a signed, scoped epoch lane.

The modeled actions are:

- `open_public`
- `renew_public`
- `close_public`
- `withdraw_public`

Each notice binds profile, service, scope, request, catalog digest, announcement digest, control-receipt digest, sequence, previous epoch digest, time window, family, and path family.

The hard guesses under test:

- a valid close notice that still exposes a public announcement is stale public replay;
- a close/withdraw epoch may require accepted announcement repair;
- same-sequence forks are worse than delay;
- a sequence advance without the previous digest is suspicious;
- old public bridge state must not survive restart just because it was once signed.

This is still local memory. It does not prove global bridge truth.
