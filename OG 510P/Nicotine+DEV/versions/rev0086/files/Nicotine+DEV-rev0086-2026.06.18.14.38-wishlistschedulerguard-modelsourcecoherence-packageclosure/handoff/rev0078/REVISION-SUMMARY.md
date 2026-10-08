# rev0078 revision summary

Rev0078 resolves the next design question without selecting premature code.

Current Search Again reuses one overloaded token, retains results, and suppresses later responses from usernames already present on the page. A replacement refresh needs a stable logical search identity, a replaceable wire epoch token, and explicit routing between them. The new source-shaped packet exercises partial re-keying, late responses, rollback at every pre-enqueue checkpoint, page closure, audience policy, result-cap behavior, queue rejection, and disconnect clearing.

The deepest correction is that queue acceptance is not network application. A composite accepted/rejected enqueue can repair the immediate silent-drop problem, but disconnect drains accepted work and clears parser admission. No broad patch is selected until an applied acknowledgement or reconnect reconciliation is designed and tested.

```text
source invariants:                 24/24 pass
research/model tests:              33/33 pass
compile checks:                    13/13 pass
upstream units:                    60 passed, 1 skipped
packet authority:                 187/187 pass
shared-runtime adoption audit:     23/23 pass
```

The cube refactor centralizes current-tool runtime helpers, adds generic manifest/delta/package entrypoints, and brings the current packet validator under the adoption contract. Historical tools remain intact.

Open `docs/START-HERE.md` first.
