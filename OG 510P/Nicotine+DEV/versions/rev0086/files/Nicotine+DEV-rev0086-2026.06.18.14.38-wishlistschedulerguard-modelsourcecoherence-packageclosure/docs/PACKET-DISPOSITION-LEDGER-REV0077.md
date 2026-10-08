# Packet disposition ledger — rev0077

This file overrides historical status language for current cube navigation.

Primary source authority: `github-branch-3.3.x` at `98089ac233aa57786e8dbdc48123f6ac1c4767d8`.

Per-packet source fields override that primary lane when a packet exists only on another branch.

## Current rows

### U-123 — same-user duplicate transfer-token ownership

```text
status:         closed-research-disposition
behavior:       confirmed
impact:         low-severity transfer correctness and bounded transient retention in the harness
security route: retired on current evidence
selected patch: research prototype retained; not upstream contribution material
current doc:    docs/U123-CURRENT-DISPOSITION-REV0073.md
```

### PB-01A/U-168 — incoming direct PeerInit replaces an established same-user/type primary

```text
status:         open-protocol-hardening-research
behavior:       confirmed on exact current source
impact:         connection ownership and queue migration correctness; stronger security impact unproven
security route: not supported by current evidence
selected patch: None
current doc:    docs/PB01-CURRENT-DISPOSITION-REV0074.md
```

### PB-01B/U-176 — post-init traffic promotes a secondary connection sharing the PeerInit

```text
status:         retired-as-defect-on-current-evidence
behavior:       confirmed but reached through the valid direct/indirect race
impact:         intentional compatibility/failover behavior in the demonstrated path
security route: not supported
selected patch: None
current doc:    docs/PB01-CURRENT-DISPOSITION-REV0074.md
```

### SEARCH-RESP-01A/U-163A — direct user-search response source admission

```text
status:         open-defense-in-depth-research
behavior:       confirmed on exact current source: a token-valid result under an off-request connection username is accepted
impact:         local request-scope consistency gap; unauthorized result injection impact not demonstrated
security route: not supported by current evidence
selected patch: None
current doc:    docs/SEARCH-RESP-01A-CURRENT-DISPOSITION-REV0075.md
```

### SEARCH-RESP-01B/U-163B — buddy-search response source admission and recipient epoch

```text
status:         open-request-epoch-design-research
behavior:       confirmed on exact supported source: buddy fan-out reads the live buddy list and token-valid results are not compared with a request recipient set
impact:         local request-scope and attribution consistency; authorization or material security impact not demonstrated
security route: not supported by current evidence
selected patch: None
current doc:    docs/SEARCH-RESP-01B-CURRENT-DISPOSITION-REV0076.md
```

### SEARCH-AGAIN-SELF-01 — Search Again self-user authorization token binding

```text
status:         closed-research-disposition
behavior:       confirmed on current public master relevant flow and the bundled master executable proxy
impact:         low-severity self-search correctness: an older resend can suppress its intended local result and temporarily authorize an unrelated current token
security route: not applicable; ordinary low-severity correctness
selected patch: maintainer_artifacts/search-again-01/master-search-again-self-token.patch
current doc:    docs/SEARCH-AGAIN-SELF-01-CURRENT-DISPOSITION-REV0077.md
source lane:    github-branch-master
source ref:     a96406e7aa285a3fb2a3e35900686d164a22bf02
executable ref: f4e17d59783dbc48ea31d2e899a681e2dd1ed500
```

## Authority mechanism

```text
data/current_packet_dispositions.json
data/rev0077_packet_dispositions.json
data/current_packet_dispositions.schema.json
data/current_packet_disposition_contract.json
tools/validate_current_packet_dispositions.py
```

Historical status prose is evidence, not current authority. The current ledger plus its contract and same-revision snapshot control navigation.
