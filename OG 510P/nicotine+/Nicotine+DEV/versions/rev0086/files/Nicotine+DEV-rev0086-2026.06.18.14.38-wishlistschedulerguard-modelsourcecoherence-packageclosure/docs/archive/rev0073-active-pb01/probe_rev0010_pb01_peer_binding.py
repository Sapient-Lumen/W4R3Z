#!/usr/bin/env python3
"""rev0010 PB-01 peer binding probes for archived Nicotine+ source lanes.

The probes are intentionally state-machine/unit-style rather than network-live:
* U-168: handler-level incoming PeerInit can replace an established primary P connection
  based on the claimed username+connection type in the PeerInit message.
* U-176: a secondary P connection associated with the same init object can become the
  primary socket after any post-init peer-message processing path returns.

The script imports each source lane in isolation and records current behavior.
"""
from __future__ import annotations

import argparse
import json
import os
import pathlib
import struct
import sys
import time
from typing import Any, Dict, List


class FakeSelector:
    def __init__(self) -> None:
        self.unregistered: List[str] = []
        self.modified: List[str] = []

    def unregister(self, sock: Any) -> None:
        self.unregistered.append(getattr(sock, "name", repr(sock)))

    def modify(self, sock: Any, events: Any) -> None:
        self.modified.append(getattr(sock, "name", repr(sock)))

    def register(self, sock: Any, events: Any) -> None:  # not used, but keeps fakes complete
        pass


class FakeSock:
    def __init__(self, name: str) -> None:
        self.name = name
        self.closed = False
        self.shutdown_called = False
        self.setsockopt_calls: List[tuple] = []

    def shutdown(self, *_args: Any) -> None:
        self.shutdown_called = True

    def close(self) -> None:
        self.closed = True

    def setsockopt(self, *args: Any) -> None:
        self.setsockopt_calls.append(args)

    def fileno(self) -> int:
        # stable fake fd derived from name, not used by FakeSelector
        return abs(hash(self.name)) % 100000 + 1000

    def __repr__(self) -> str:
        return f"<FakeSock {self.name} closed={self.closed}>"


def purge_pynicotine_modules() -> None:
    for name in list(sys.modules):
        if name == "pynicotine" or name.startswith("pynicotine."):
            del sys.modules[name]


def frame_peer_init(PeerInit: Any, PEER_INIT_MESSAGE_CODES: Dict[Any, int], init_user: str, conn_type: str) -> bytearray:
    msg = PeerInit(init_user=init_user, conn_type=conn_type)
    content = msg.make_network_message()
    msg_code = PEER_INIT_MESSAGE_CODES[PeerInit]
    return bytearray(struct.pack("<I", len(content) + 1) + bytes([msg_code]) + content)


def run_lane(lane_name: str, lane_path: pathlib.Path) -> Dict[str, Any]:
    purge_pynicotine_modules()
    sys.path.insert(0, str(lane_path))
    try:
        from pynicotine.slskmessages import ConnectionType, PeerInit, PEER_INIT_MESSAGE_CODES
        from pynicotine.slskproto import NetworkThread, PeerConnection

        net = NetworkThread()
        # Silence event fanout for this isolated probe. The Events singleton uses slots,
        # so patch the instance method that slskproto calls for parsed messages instead.
        net._emit_network_message_event = lambda *args, **kwargs: None
        net._should_process_queue = True
        net._selector = FakeSelector()
        net._server_username = "localuser"
        net._num_sockets = 2

        # U-168: incoming direct PeerInit claims the same remote username/type as an existing connection.
        primary_sock = FakeSock(f"{lane_name}:primary")
        incoming_sock = FakeSock(f"{lane_name}:incoming-direct")
        primary_init = PeerInit(init_user="localuser", target_user="peerA", conn_type=ConnectionType.PEER)
        primary_init.sock = primary_sock
        primary_conn = PeerConnection(sock=primary_sock, addr=("198.51.100.10", 4000), init=primary_init)
        primary_conn.is_established = True
        incoming_conn = PeerConnection(sock=incoming_sock, addr=("203.0.113.55", 5000))
        incoming_conn.is_established = True
        incoming_conn.in_buffer = frame_peer_init(PeerInit, PEER_INIT_MESSAGE_CODES, "peerA", ConnectionType.PEER)
        net._conns[primary_sock] = primary_conn
        net._conns[incoming_sock] = incoming_conn
        net._username_init_msgs["peerA" + ConnectionType.PEER] = primary_init

        before_u168 = {
            "username_init_sock": getattr(net._username_init_msgs["peerA" + ConnectionType.PEER].sock, "name", None),
            "primary_in_conns": primary_sock in net._conns,
            "incoming_in_conns": incoming_sock in net._conns,
        }
        net._process_conn_incoming_messages(incoming_conn)
        after_init = net._username_init_msgs.get("peerA" + ConnectionType.PEER)
        after_u168 = {
            "username_init_sock": getattr(after_init.sock, "name", None) if after_init else None,
            "primary_in_conns": primary_sock in net._conns,
            "incoming_in_conns": incoming_sock in net._conns,
            "primary_sock_closed": primary_sock.closed,
            "primary_shutdown_called": primary_sock.shutdown_called,
            "selector_unregistered": list(net._selector.unregistered),
            "queued_msgs_migrated": [getattr(item, "label", repr(item)) for item in getattr(after_init, "outgoing_msgs", [])] if after_init else [],
            "incoming_conn_init_target": getattr(incoming_conn.init, "target_user", None),
            "incoming_conn_init_sock": getattr(getattr(incoming_conn, "init", None), "sock", None).name if getattr(incoming_conn, "init", None) else None,
        }

        # U-176: a secondary connection that shares the primary init becomes primary after post-init activity.
        secondary_sock = FakeSock(f"{lane_name}:secondary")
        secondary_conn = PeerConnection(sock=secondary_sock, addr=("203.0.113.66", 6000), init=after_init)
        secondary_conn.is_established = True
        secondary_conn.in_buffer = bytearray(b"post-init-message-placeholder")
        net._conns[secondary_sock] = secondary_conn
        net._num_sockets += 1

        # Isolate the promotion rule: treat a peer message as successfully processed without depending on a
        # particular peer-message type or downstream subsystem.
        processed = {"called": False, "conn_sock": None, "init_sock_before": None}

        def fake_process_peer_input(conn: Any) -> None:
            processed["called"] = True
            processed["conn_sock"] = getattr(conn.sock, "name", None)
            processed["init_sock_before"] = getattr(conn.init.sock, "name", None)
            conn.in_buffer.clear()

        net._process_peer_input = fake_process_peer_input
        before_u176 = {
            "init_sock": getattr(after_init.sock, "name", None),
            "secondary_sock": secondary_sock.name,
        }
        net._process_conn_incoming_messages(secondary_conn)
        after_u176 = {
            "init_sock": getattr(after_init.sock, "name", None),
            "secondary_sock": secondary_sock.name,
            "peer_input_called": processed["called"],
            "processed_conn_sock": processed["conn_sock"],
            "processed_init_sock_before": processed["init_sock_before"],
            "promoted": after_init.sock is secondary_sock,
        }

        observed_replacement = (
            after_u168["username_init_sock"] == incoming_sock.name
            and after_u168["primary_sock_closed"] is True
            and after_u168["primary_in_conns"] is False
            and after_u168["incoming_conn_init_target"] == "peerA"
        )

        return {
            "lane": lane_name,
            "lane_path": str(lane_path),
            "ok": True,
            "u168_direct_peerinit_replacement": {
                "before": before_u168,
                "after": after_u168,
                "identity_diag": {
                    "username_init_is_incoming_conn_init": after_init is incoming_conn.init,
                    "username_init_sock_is_incoming_sock": after_init.sock is incoming_sock,
                },
                "observed_replacement": observed_replacement,
            },
            "u176_secondary_post_init_promotion": {
                "before": before_u176,
                "after": after_u176,
                "observed_promotion": after_u176["promoted"] is True,
            },
        }
    except Exception as exc:  # keep lane failures explicit in JSONL evidence
        import traceback
        return {
            "lane": lane_name,
            "lane_path": str(lane_path),
            "ok": False,
            "error": repr(exc),
            "traceback": traceback.format_exc(),
        }
    finally:
        try:
            sys.path.remove(str(lane_path))
        except ValueError:
            pass
        purge_pynicotine_modules()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-root", required=True, help="Directory containing source-trees/<lane>")
    parser.add_argument("--output-jsonl", required=True)
    args = parser.parse_args()

    source_root = pathlib.Path(args.source_root)
    if (source_root / "source-trees").is_dir():
        source_root = source_root / "source-trees"

    lanes = ["github-tag-3.3.10", "github-branch-3.3.x", "github-branch-master"]
    results = [run_lane(lane, source_root / lane) for lane in lanes]

    out_path = pathlib.Path(args.output_jsonl)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as fh:
        for row in results:
            fh.write(json.dumps(row, sort_keys=True) + "\n")

    print(json.dumps({"results": results}, indent=2, sort_keys=True))
    return 0 if all(row.get("ok") for row in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
