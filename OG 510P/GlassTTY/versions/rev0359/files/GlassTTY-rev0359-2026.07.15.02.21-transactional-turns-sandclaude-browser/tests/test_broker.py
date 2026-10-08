from __future__ import annotations

import json
import socket
from pathlib import Path

from glassttyd.broker import BrokerServer


def test_broker_accepts_status_and_request(tmp_path: Path) -> None:
    emitted: list[dict] = []
    server = BrokerServer(
        tmp_path / 'daemon.sock',
        emit_to_extension=emitted.append,
        status_provider=lambda: {'ok': True, 'state_root': str(tmp_path)},
    )
    server.start()
    try:
        client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        client.connect(str(tmp_path / 'daemon.sock'))
        file = client.makefile('r', encoding='utf-8')

        hello = json.loads(file.readline())
        assert hello['type'] == 'hello'

        client.sendall((json.dumps({'op': 'status'}) + '\n').encode('utf-8'))
        status = json.loads(file.readline())
        assert status['type'] == 'status'

        payload = {
            'op': 'submit_browser_request',
            'message': {
                'request_id': 'abc',
                'type': 'prompt.read',
                'timestamp': 'now',
                'tab_id': 42,
                'payload': {},
            },
        }
        client.sendall((json.dumps(payload) + '\n').encode('utf-8'))
        ack = json.loads(file.readline())
        assert ack['type'] == 'submit.ack'
        assert emitted[-1]['type'] == 'bridge.forward_to_active_tab'
        assert emitted[-1]['payload']['request']['tab_id'] == 42
    finally:
        server.stop()
