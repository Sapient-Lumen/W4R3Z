"""Current-behavior witness for F-connection fixed-width frame fragmentation.

Run from a Nicotine+ source root with:
    python -m pytest /path/to/test_fconn_frame_current_behavior.py

The assertions intentionally describe current behavior: partial FileTransferInit/FileOffset
fragments are consumed instead of retained until the fixed-width frame is complete.
"""

import struct
from types import SimpleNamespace

from pynicotine.slskmessages import ConnectionType, FileTransferInit, PeerInit
from pynicotine.slskproto import NetworkThread, PeerConnection


def _network_thread():
    nt = NetworkThread()
    nt._emit_network_message_event = lambda msg: None
    nt._selector = SimpleNamespace(modify=lambda *args, **kwargs: None)
    return nt


def _file_connection(username="peer_a"):
    init = PeerInit(init_user=username, target_user=username, conn_type=ConnectionType.FILE)
    return PeerConnection(sock=object(), init=init)


def test_complete_file_transfer_init_still_parses():
    nt = _network_thread()
    conn = _file_connection("complete-init")
    conn.in_buffer += struct.pack("<I", 0x01020304)

    nt._process_file_input(conn)

    assert len(conn.in_buffer) == 0
    assert nt._file_init_msgs[conn].token == 0x01020304


def test_fragmented_file_transfer_init_is_consumed_before_complete():
    nt = _network_thread()
    conn = _file_connection("fragmented-init")
    frame = struct.pack("<I", 0x01020304)

    conn.in_buffer += frame[:2]
    nt._process_file_input(conn)

    assert len(conn.in_buffer) == 0
    assert conn.has_post_init_activity is True
    assert conn not in nt._file_init_msgs

    conn.in_buffer += frame[2:]
    nt._process_file_input(conn)

    assert len(conn.in_buffer) == 0
    assert conn not in nt._file_init_msgs


def test_complete_file_offset_still_updates_upload_offset():
    nt = _network_thread()
    conn = _file_connection("complete-offset")
    upload = SimpleNamespace(offset=None, token=0x3333, sentbytes=0, file=SimpleNamespace(seek=lambda offset: None))
    nt._file_init_msgs[conn] = FileTransferInit(token=0x3333)
    nt._file_upload_msgs[conn] = upload
    conn.in_buffer += struct.pack("<Q", 0x0102030405060708)

    nt._process_file_input(conn)

    assert len(conn.in_buffer) == 0
    assert upload.offset == 0x0102030405060708


def test_fragmented_file_offset_is_consumed_before_complete():
    nt = _network_thread()
    conn = _file_connection("fragmented-offset")
    upload = SimpleNamespace(offset=None, token=0x4444, sentbytes=0, file=SimpleNamespace(seek=lambda offset: None))
    nt._file_init_msgs[conn] = FileTransferInit(token=0x4444)
    nt._file_upload_msgs[conn] = upload
    frame = struct.pack("<Q", 0x0102030405060708)

    conn.in_buffer += frame[:4]
    nt._process_file_input(conn)

    assert len(conn.in_buffer) == 0
    assert conn.has_post_init_activity is True
    assert upload.offset is None

    conn.in_buffer += frame[4:]
    nt._process_file_input(conn)

    assert len(conn.in_buffer) == 0
    assert upload.offset is None
