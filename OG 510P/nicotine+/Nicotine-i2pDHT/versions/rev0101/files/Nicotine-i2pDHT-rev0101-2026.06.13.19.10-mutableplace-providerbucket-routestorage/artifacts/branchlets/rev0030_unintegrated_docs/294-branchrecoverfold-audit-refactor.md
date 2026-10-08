# Branchrecoverfold audit/refactor

rev0030 is partly an audit/refactor revision: it recovers useful parallel rev0029 branchlet work and makes it visible from the current cube surface.

`branchrecoverfold.py` checks that the following paths exist and are named from public surfaces:

- `absencegate.py`
- `keycrisis.py`
- `peerbook.py`
- `deltasketch.py`
- `rangesetdelta.py`
- `liveprobe.py`
- `branchrecoverfold.py`
- `tests/test_rev0030_negspace_peer_delta_keycrisis.py`
- rev0030 docs

It also runs the rev0029 `foldseal.py` predecessor audit and the rev0030 surface ledger.

The refactor stance is append-heavy but not entropy-blind: useful branchlets become named active surfaces; broken/inactive smoke fragments are not shipped as current active surfaces.
