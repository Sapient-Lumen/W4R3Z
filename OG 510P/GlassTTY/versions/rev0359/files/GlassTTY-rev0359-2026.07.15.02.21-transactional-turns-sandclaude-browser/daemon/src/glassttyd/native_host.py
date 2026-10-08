from __future__ import annotations

import hashlib
import json
import os
import signal
import sys
import threading
import uuid
from datetime import datetime, timezone
from pathlib import Path

from .broker import BrokerServer
from .broker_lock import BrokerOwnershipLease
from .overflow_artifacts import compact_overflow_inventory_summary
from .protocol import JsonDict, NATIVE_MESSAGE_HOST_MAX_BYTES, eprint, make_envelope, native_message_budget_report, read_native_message, write_native_message
from .state import StateStore


PASSTHROUGH_TYPES = {
    'prompt.read',
    'transcript.latest',
    'prompt.write',
    'prompt.submit',
    'prompt.continue',
    'generation.state',
    'surface.probe',
    'surface.overrides.set',
    'surface.overrides.get',
    'attach.begin',
    'attach.chunk',
    'attach.commit',
    'attach.abort',
    'attach.status',
    'attach.clear',
    'prompt.stop',
    'chat.new',
    'selection.read',
    'state.snapshot',
    'fixture.capture',
    'debug.dom_candidates',
    'adapter.detected',
    'transcript.delta',
    'error.report',
    'bridge.contexts',
    'bridge.trace',
    'bridge.probe',
    'bridge.offscreen_fixture',
    'bridge.set_target_tab',
    'bridge.clear_target_tab',
}


class NativeBridge:
    def __init__(self, store: StateStore):
        self.store = store
        self.stdout_lock = threading.Lock()
        self.started_at = self._utc_now()
        self.boot_id = str(uuid.uuid4())
        self.message_count = 0
        self.first_message_at: str | None = None
        self.first_message_type: str | None = None
        self.last_message_at: str | None = None
        self.last_message_type: str | None = None
        self.broker_role = 'uninitialized'
        self.broker_started = False
        self.broker_lease = BrokerOwnershipLease(self.store.run_dir)
        self._broker: BrokerServer | None = None

    def socket_path(self) -> Path:
        return self.store.run_dir / 'daemon.sock'

    def host_identity(self) -> JsonDict:
        return {
            'pid': os.getpid(),
            'boot_id': self.boot_id,
            'started_at': self.started_at,
            'message_count': self.message_count,
            'first_message_at': self.first_message_at,
            'first_message_type': self.first_message_type,
            'last_message_at': self.last_message_at,
            'last_message_type': self.last_message_type,
        }

    def broker(self) -> BrokerServer:
        if self._broker is None:
            self._broker = BrokerServer(self.socket_path(), self.emit_to_extension, self.status)
        return self._broker

    def broker_intent(self, message: JsonDict) -> str:
        payload = message.get('payload') if isinstance(message.get('payload'), dict) else {}
        declared = payload.get('broker_intent') if isinstance(payload, dict) else None
        if declared in {'owner_candidate', 'secondary_only'}:
            return str(declared)
        if message.get('type') == 'bridge.status':
            return 'secondary_only'
        return 'owner_candidate'

    def ensure_broker_role_for_message(self, message: JsonDict) -> str:
        intent = self.broker_intent(message)
        if self.broker_role == 'owner':
            return self.broker_role
        if intent == 'secondary_only':
            if self.broker_role == 'uninitialized':
                self.broker_role = 'secondary'
            return self.broker_role
        self.start_broker_if_owner()
        return self.broker_role

    def broker_status(self) -> JsonDict:
        owner_metadata = self.broker_lease.read_metadata()
        return {
            'role': self.broker_role if self.broker_role != 'uninitialized' else 'unknown',
            'lock_path': str(self.broker_lease.lock_path),
            'metadata_path': str(self.broker_lease.metadata_path),
            'socket_path': str(self.socket_path()),
            'socket_exists': self.socket_path().exists(),
            'connected_clients': self.broker().connected_client_count() if self.broker_started and self._broker is not None else None,
            'owner_metadata': owner_metadata,
        }

    def start_broker_if_owner(self) -> bool:
        if self.broker_role == 'owner':
            return True
        if self.broker_role == 'secondary':
            return False
        metadata = {
            'native_host': 'com.glasstty.bridge',
            'socket_path': str(self.socket_path()),
            'lock_path': str(self.broker_lease.lock_path),
            'metadata_path': str(self.broker_lease.metadata_path),
            'host_identity': self.host_identity(),
        }
        if self.broker_lease.try_acquire(metadata):
            self.broker().start()
            self.broker_started = True
            self.broker_role = 'owner'
            return True
        self.broker_role = 'secondary'
        return False

    def stop_broker_if_owner(self) -> None:
        try:
            if self.broker_started and self._broker is not None:
                self.broker().stop()
        finally:
            self.broker_started = False
            self.broker_lease.release()

    def status(self) -> JsonDict:
        return {
            'native_host': 'com.glasstty.bridge',
            'socket_path': str(self.socket_path()),
            'host_identity': self.host_identity(),
            'broker': self.broker_status(),
            **self.store.status(),
            'last_oversized_host_message': self.store.read_latest('oversized-host-outbound'),
            'overflow_inventory': compact_overflow_inventory_summary(self.store.root.parent),
        }

    def _utc_now(self) -> str:
        return datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')

    def _safe_token(self, value: object, *, fallback: str) -> str:
        raw = str(value or '').strip().lower()
        cleaned = ''.join(ch if ch.isalnum() else '-' for ch in raw).strip('-')
        return (cleaned[:48] or fallback)

    def _oversized_outbound_notice(self, message: JsonDict, *, size_bytes: int, artifact_path: Path, emitted_at: str) -> JsonDict:
        payload: JsonDict = {
            'ok': False,
            'error': f'native host outbound message exceeded Chrome host-to-extension limit of {NATIVE_MESSAGE_HOST_MAX_BYTES} bytes',
            'overflow': True,
            'original_type': message.get('type'),
            'message_size_bytes': size_bytes,
            'limit_bytes': NATIVE_MESSAGE_HOST_MAX_BYTES,
            'artifact_path': str(artifact_path),
            'emitted_at': emitted_at,
            'native_host': 'com.glasstty.bridge',
        }
        return make_envelope(
            'error.report',
            payload,
            request_id=message.get('request_id') if isinstance(message.get('request_id'), str) else None,
            tab_id=message.get('tab_id') if isinstance(message.get('tab_id'), int) else None,
            timestamp=message.get('timestamp') if isinstance(message.get('timestamp'), str) else emitted_at,
        )

    def _spill_oversized_outbound_message(self, message: JsonDict, *, size_bytes: int) -> tuple[Path, JsonDict]:
        emitted_at = self._utc_now()
        digest = hashlib.sha256(json.dumps(message, ensure_ascii=False, sort_keys=True).encode('utf-8')).hexdigest()[:12]
        stem = '-'.join([
            'oversized-host-outbound',
            self._safe_token(message.get('type'), fallback='unknown-type'),
            self._safe_token(message.get('request_id'), fallback='no-request-id'),
            digest,
        ])
        artifact_payload: JsonDict = {
            'kind': 'oversized-host-outbound',
            'captured_at': emitted_at,
            'budget': native_message_budget_report(message),
            'message': message,
        }
        artifact_path = self.store.write_fixture(stem, artifact_payload)
        summary: JsonDict = {
            'kind': 'oversized-host-outbound',
            'captured_at': emitted_at,
            'artifact_path': str(artifact_path),
            'original_type': message.get('type'),
            'request_id': message.get('request_id'),
            'tab_id': message.get('tab_id'),
            **native_message_budget_report(message),
        }
        self.store.write_latest('oversized-host-outbound', summary)
        self.store.append_event({'stream': 'host_outbound_overflow', 'summary': summary})
        return artifact_path, summary

    def emit_to_extension(self, message: JsonDict) -> None:
        report = native_message_budget_report(message)
        if report['fits']:
            self.store.append_event({'stream': 'host_outbound', 'message': message, 'budget': report})
            with self.stdout_lock:
                write_native_message(sys.stdout, message)
            return

        artifact_path, summary = self._spill_oversized_outbound_message(message, size_bytes=int(report['size_bytes']))
        eprint(
            '[glasstty-native-host] oversized outbound message',
            f"type={summary.get('original_type')}",
            f"size={summary.get('size_bytes')}",
            f"artifact={artifact_path}",
        )
        notice = self._oversized_outbound_notice(message, size_bytes=int(report['size_bytes']), artifact_path=artifact_path, emitted_at=str(summary['captured_at']))
        with self.stdout_lock:
            try:
                write_native_message(sys.stdout, notice)
            except RuntimeError:
                minimal_notice = make_envelope(
                    'error.report',
                    {
                        'ok': False,
                        'error': 'native host outbound message exceeded Chrome host-to-extension limit',
                        'overflow': True,
                        'message_size_bytes': report['size_bytes'],
                        'limit_bytes': NATIVE_MESSAGE_HOST_MAX_BYTES,
                    },
                    request_id=message.get('request_id') if isinstance(message.get('request_id'), str) else None,
                    tab_id=message.get('tab_id') if isinstance(message.get('tab_id'), int) else None,
                    timestamp=summary['captured_at'],
                )
                write_native_message(sys.stdout, minimal_notice)

    def record_browser_message(self, message: JsonDict) -> None:
        message_type = str(message.get('type') or 'unknown')
        recorded_at = self._utc_now()
        self.message_count += 1
        if self.first_message_at is None:
            self.first_message_at = recorded_at
            self.first_message_type = message_type
        self.last_message_at = recorded_at
        self.last_message_type = message_type
        if self.broker_role == 'owner' and self.broker_lease.acquired:
            self.broker_lease.write_metadata({
                'native_host': 'com.glasstty.bridge',
                'socket_path': str(self.socket_path()),
                'lock_path': str(self.broker_lease.lock_path),
                'metadata_path': str(self.broker_lease.metadata_path),
                'host_identity': self.host_identity(),
            })
        self.store.append_event({'stream': 'browser_inbound', 'message': message})
        safe_name = message_type.replace('.', '_')
        self.store.write_latest('last-browser-message', message)
        self.store.write_latest(safe_name, message)
        if self.broker_started:
            self.broker().broadcast({'stream': 'browser_event', 'message': message})

    def handle_browser_message(self, message: JsonDict) -> JsonDict | None:
        self.ensure_broker_role_for_message(message)
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
                    'host_identity': self.host_identity(),
                    'broker': self.broker_status(),
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

        if message_type in PASSTHROUGH_TYPES or (isinstance(message_type, str) and message_type.startswith('bridge.') and message_type != 'bridge.status'):
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
        eprint('[glasstty-native-host] starting')
        eprint(f'[glasstty-native-host] socket={self.socket_path()} role=deferred')

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
            self.stop_broker_if_owner()
            eprint('[glasstty-native-host] exiting')


def state_root() -> Path:
    return Path(os.environ.get('GLASSTTY_HOME', Path.home() / '.local' / 'share' / 'glasstty')) / 'state'


def main() -> None:
    NativeBridge(StateStore(state_root())).run()


if __name__ == '__main__':
    main()
