from __future__ import annotations

import json
import os
import socket
import threading
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable

JsonDict = dict[str, Any]


@dataclass(eq=False)
class ClientSession:
    conn: socket.socket
    lock: threading.Lock = field(default_factory=threading.Lock)

    def send(self, message: JsonDict) -> None:
        data = (json.dumps(message, ensure_ascii=False) + "\n").encode("utf-8")
        with self.lock:
            self.conn.sendall(data)


class BrokerServer:
    def __init__(self, socket_path: Path, emit_to_extension: Callable[[JsonDict], None], status_provider: Callable[[], JsonDict]):
        self.socket_path = socket_path
        self.emit_to_extension = emit_to_extension
        self.status_provider = status_provider
        self.server: socket.socket | None = None
        self.clients: set[ClientSession] = set()
        self.clients_lock = threading.Lock()
        self.should_stop = threading.Event()
        self.thread: threading.Thread | None = None

    def start(self) -> None:
        self.socket_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            if self.socket_path.exists():
                self.socket_path.unlink()
        except FileNotFoundError:
            pass

        self.server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.server.bind(os.fspath(self.socket_path))
        self.server.listen(8)
        self.thread = threading.Thread(target=self._serve, name="glasstty-broker", daemon=True)
        self.thread.start()

    def stop(self) -> None:
        self.should_stop.set()
        if self.server is not None:
            try:
                self.server.close()
            except OSError:
                pass
        try:
            if self.socket_path.exists():
                self.socket_path.unlink()
        except FileNotFoundError:
            pass

    def status(self) -> JsonDict:
        with self.clients_lock:
            clients = len(self.clients)
        return {
            "ok": True,
            "socket_path": os.fspath(self.socket_path),
            "connected_clients": clients,
            **self.status_provider(),
        }

    def broadcast(self, message: JsonDict) -> None:
        dead: list[ClientSession] = []
        with self.clients_lock:
            clients = list(self.clients)
        for client in clients:
            try:
                client.send(message)
            except OSError:
                dead.append(client)
        if dead:
            with self.clients_lock:
                for client in dead:
                    self.clients.discard(client)
                    try:
                        client.conn.close()
                    except OSError:
                        pass

    def _serve(self) -> None:
        assert self.server is not None
        while not self.should_stop.is_set():
            try:
                conn, _addr = self.server.accept()
            except OSError:
                break
            session = ClientSession(conn=conn)
            with self.clients_lock:
                self.clients.add(session)
            thread = threading.Thread(target=self._handle_client, args=(session,), daemon=True)
            thread.start()

    def _handle_client(self, session: ClientSession) -> None:
        file = session.conn.makefile("r", encoding="utf-8")
        try:
            session.send({"stream": "server", "type": "hello", "payload": self.status()})
            for line in file:
                line = line.strip()
                if not line:
                    continue
                try:
                    message = json.loads(line)
                except json.JSONDecodeError as exc:
                    session.send({"stream": "server", "type": "error", "payload": {"error": f"invalid json: {exc}"}})
                    continue
                self._handle_client_message(session, message)
        finally:
            with self.clients_lock:
                self.clients.discard(session)
            try:
                session.conn.close()
            except OSError:
                pass

    def _handle_client_message(self, session: ClientSession, message: JsonDict) -> None:
        op = message.get("op")
        if op == "ping":
            session.send({"stream": "server", "type": "pong", "payload": self.status()})
            return
        if op == "watch":
            session.send({"stream": "server", "type": "watch.ready", "payload": self.status()})
            return
        if op == "status":
            session.send({"stream": "server", "type": "status", "payload": self.status()})
            return
        if op == "submit_browser_request":
            outbound = message.get("message")
            if not isinstance(outbound, dict):
                session.send({"stream": "server", "type": "error", "payload": {"error": "submit_browser_request requires object message"}})
                return
            self.emit_to_extension({
                "version": "0.1",
                "request_id": outbound.get("request_id"),
                "type": "bridge.forward_to_active_tab",
                "timestamp": outbound.get("timestamp"),
                "payload": {
                    "request": outbound,
                },
            })
            session.send({"stream": "server", "type": "submit.ack", "payload": {"request_id": outbound.get("request_id")}})
            return
        session.send({"stream": "server", "type": "error", "payload": {"error": f"unknown op: {op}"}})
