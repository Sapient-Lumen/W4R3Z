# rev0042 — multiservice-cooldown-keyoperator

rev0042 continues the risk-first DHT-over-I2P cube by treating shared garden control as a joined boundary. A single valid service exit, router stop, or resume signal is not enough when multiple services share one router profile, one operator authority, and one public bridge exposure surface.

New active surfaces:

- `multiservice.py` — signed runtime observations for sibling service/router pressure.
- `profilecooldown.py` — profile-level emergency-freeze cooldown and recovery evidence.
- `operatorkey.py` — operator-key rotation, compromise, recovery, and hard-negative preservation.
- `announcementrepair.py` — catalog and announcement repair after public bridge disable.
- `controlplanefold.py` — rev0042 audit/refactor fold preserving rev0041 controlfold predecessor history.

Strongest sentence: **a router-backed profile is not safe because one service is safe; the shared control plane must agree at the profile, service, key, announcement, and cooldown boundary.**

Nonclaims remain unchanged: no live I2P/SAM transport, no production DHT, no production garden lifecycle manager, no private retrieval guarantee, no global reputation, no mutable-head consensus, no Sybil/anonymity guarantee, and no Nicotine+ patch.
