from __future__ import annotations

from pathlib import Path

from glassttyd.state import StateStore


def test_state_store_writes_event_and_latest(tmp_path: Path) -> None:
    store = StateStore(tmp_path / 'state')
    store.append_event({'type': 'x'})
    store.write_latest('sample', {'ok': True})

    assert store.events_path.exists()
    assert store.read_latest('sample') == {'ok': True}
    assert store.status()['event_count'] == 1
