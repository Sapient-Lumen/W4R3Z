# PB-01 upstream history evidence — rev0074

Source: local full Git repository corresponding to the supplied source bundle. No source tree is embedded in this cube.

## Compatibility fix

```text
commit 34b442a1218e42d906286d4ffd7c560ed993bb04
AuthorDate: 2024-01-16
Title: slskproto.py: be less aggressive when rejecting indirect connections
Message: Fixes connectivity issue with some SoulseekQt users. Related to #2829.
```

The diff keeps an indirect connection open when a direct connection is already established and comments that some clients may send a message over the indirect connection.

## Immediate follow-up

```text
commit 4932ef94c09956861e65b411c729cd74d947c4b9
Parent: 34b442a1218e42d906286d4ffd7c560ed993bb04
AuthorDate: 2024-01-17
Title: slskproto.py: replace init socket when necessary
```

The diff assigns `init.sock` to a secondary connection after that connection carries a post-init message and logs that it is promoted to primary.

## Older replacement intent

```text
commit de9970d1873159d1e0621a10f2f88afb4285875d
AuthorDate: 2022-02-01
Title: slskproto.py: replace existing peer connection when indirect request arrives
```

This establishes that replacement behavior itself was introduced deliberately, although it does not settle the safest current policy.

## Commands used

```bash
git show --format=fuller 34b442a1218e42d906286d4ffd7c560ed993bb04 -- pynicotine/slskproto.py
git show --format=fuller 4932ef94c09956861e65b411c729cd74d947c4b9 -- pynicotine/slskproto.py
git show --format=fuller de9970d1873159d1e0621a10f2f88afb4285875d -- pynicotine/slskproto.py
```

Interpretation: PB-01B overlaps a documented compatibility repair. A patch that disables it needs stronger integration evidence than a synthetic primary-preservation assertion.
