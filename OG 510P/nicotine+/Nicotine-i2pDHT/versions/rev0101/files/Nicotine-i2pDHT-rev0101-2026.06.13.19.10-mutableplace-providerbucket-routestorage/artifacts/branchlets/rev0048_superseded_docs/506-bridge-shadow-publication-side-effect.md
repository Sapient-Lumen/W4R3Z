# Bridge shadow public side effect

`bridgeshadow.py` is the rev0048 no-network boundary between local publication acceptance and any future externally visible bridge refresh, withdrawal, repair, mutable-head write, or garden mirror request.

The important bug class is component mixing: a publication guard, publication ledger, and quench report can each be valid but belong to different scope/request/payload boundaries. A bridge-shadow step signs the exact public payload, side-effect digest, component report digests, sequence, previous digest, family, and path family before the local node treats the future public side effect as eligible.

A quench report can still hold the side effect. A watched component can make the shadow watched. A replayed step, sequence fork, previous-link mismatch, payload drift, component digest drift, or one-family path is not silently promoted.
