from __future__ import annotations

import os
import signal
import sys
import threading
from pathlib import Path

from .broker import BrokerServer
from .protocol import JsonDict, eprint, make_envelope, read_native_message, write_native_message
from .state import StateStore


class NativeBridge:
    def __init__(self, store: StateStore):
        self.store = store
        self.stdout_lock = threading.Lock()
        self.broker = BrokerServer(self.socket_path(), self.emit_to_extension, self.status)

    def socket_path(self) -> Path:
        return self.store.run_dir / 'daemon.sock'

    def status(self) -> JsonDict:
        return {
            'native_host': 'com.glasstty.bridge',
            'socket_path': str(self.socket_path()),
            **self.store.status(),
        }

    def emit_to_extension(self, message: JsonDict) -> None:
        self.store.append_event({'stream': 'host_outbound', 'message': message})
        with self.stdout_lock:
            write_native_message(sys.stdout, message)

    def record_browser_message(self, message: JsonDict) -> None:
        self.store.append_event({'stream': 'browser_inbound', 'message': message})
        message_type = str(message.get('type') or 'unknown')
        safe_name = message_type.replace('.', '_')
        self.store.write_latest('last-browser-message', message)
        self.store.write_latest(safe_name, message)
        self.broker.broadcast({'stream': 'browser_event', 'message': message})

    def handle_browser_message(self, message: JsonDict) -> JsonDict | None:
        self.record_browser_message(message)
        message_type = message.get('type')

        if message_type == 'health.ping':
            return make_envelope(
                'health.ping',
                {
                    'ok': True,
                    'echo': message.get('payload', {}),
                    'native_host': 'com.glasstty.bridge',
                    'socket_path': str(self.socket_path()),
                },
                request_id=message.get('request_id'),
                timestamp=message.get('timestamp'),
            )

        if message_type == 'bridge.status':
            return make_envelope(
                'bridge.status',
                {
                    'ok': True,
                    **self.status(),
                },
                request_id=message.get('request_id'),
                timestamp=message.get('timestamp'),
            )

        if message_type in {'prompt.read', 'transcript.latest', 'prompt.write', 'prompt.submit', 'selection.read', 'state.snapshot', 'debug.dom_candidates', 'adapter.detected', 'transcript.delta', 'error.report'}:
            return None

        return make_envelope(
            'error.report',
            {
                'ok': False,
                'error': f'unrecognized native-host message type: {message_type}',
            },
            request_id=message.get('request_id'),
            tab_id=message.get('tab_id') if isinstance(message.get('tab_id'), int) else None,
            timestamp=message.get('timestamp'),
        )

    def run(self) -> None:
        self.broker.start()
        eprint('[glasstty-native-host] starting')
        eprint(f'[glasstty-native-host] socket={self.socket_path()}')

        def _stop(_signum, _frame) -> None:
            raise KeyboardInterrupt

        signal.signal(signal.SIGTERM, _stop)

        try:
            while True:
                message = read_native_message(sys.stdin)
                if message is None:
                    break
                response = self.handle_browser_message(message)
                if response is not None:
                    self.emit_to_extension(response)
        except KeyboardInterrupt:
            pass
        finally:
            self.broker.stop()
            eprint('[glasstty-native-host] exiting')


def state_root() -> Path:
    return Path(os.environ.get('GLASSTTY_HOME', Path.home() / '.local' / 'share' / 'glasstty')) / 'state'


def main() -> None:
    NativeBridge(StateStore(state_root())).run()


if __name__ == '__main__':
    main()
