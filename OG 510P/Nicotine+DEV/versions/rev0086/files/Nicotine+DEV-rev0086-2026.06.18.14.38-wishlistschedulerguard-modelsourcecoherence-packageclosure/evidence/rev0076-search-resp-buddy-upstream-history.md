# rev0076 upstream history evidence — SEARCH-RESP-01B

## Exact executable lanes

```text
supported 3.3.x: 98089ac233aa57786e8dbdc48123f6ac1c4767d8
bundled master:  f4e17d59783dbc48ea31d2e899a681e2dd1ed500
source bundle:   feaa8df98bbd0f28ba00eb8d52dcc3b9b9860e8d59039c7d41a98a0117505e5b
```

The probe validates twelve source invariants across search processing, buddy sending, result admission, connection username assignment, local share permission direction, and master Search Again behavior.

## Compatibility history

Official commit `5e3e8fcd1d4fa1965976fd29595784a4dcaad3d6` changed search result attribution to the username associated with the peer connection because old Museek clients can send the wrong username in the result message. The rev0076 identity test mirrors that boundary: the parsed body username is not used as connection identity.

## Live public source shape

During the session, the visible master head was `a96406e` dated 2026-06-15. The current raw search module retained the relevant shape: Search Again can retrieve an existing search by token, and the buddy sender consults the live buddy list. This was a source-shape check, not an exact locally executed live-master lane.
