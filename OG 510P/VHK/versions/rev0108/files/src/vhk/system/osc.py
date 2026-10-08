from __future__ import annotations

import base64
import json
import socketserver
import struct
import threading
from dataclasses import dataclass
from typing import Any, Iterable, Iterator, Sequence


class OscDecodeError(ValueError):
    pass


def _pad4(n: int) -> int:
    return (4 - (n % 4)) % 4


def _read_osc_string(buf: bytes, offset: int) -> tuple[str, int]:
    if offset >= len(buf):
        raise OscDecodeError("unexpected end of packet while reading osc-string")
    end = buf.find(b"\x00", offset)
    if end < 0:
        raise OscDecodeError("osc-string missing NUL terminator")
    s = buf[offset:end].decode("utf-8", errors="replace")
    nxt = end + 1
    nxt += _pad4(nxt)
    return s, nxt


def _read_int32(buf: bytes, offset: int) -> tuple[int, int]:
    if offset + 4 > len(buf):
        raise OscDecodeError("unexpected end of packet while reading int32")
    return struct.unpack(">i", buf[offset : offset + 4])[0], offset + 4


def _read_int64(buf: bytes, offset: int) -> tuple[int, int]:
    if offset + 8 > len(buf):
        raise OscDecodeError("unexpected end of packet while reading int64")
    return struct.unpack(">q", buf[offset : offset + 8])[0], offset + 8


def _read_float32(buf: bytes, offset: int) -> tuple[float, int]:
    if offset + 4 > len(buf):
        raise OscDecodeError("unexpected end of packet while reading float32")
    return struct.unpack(">f", buf[offset : offset + 4])[0], offset + 4


def _read_float64(buf: bytes, offset: int) -> tuple[float, int]:
    if offset + 8 > len(buf):
        raise OscDecodeError("unexpected end of packet while reading float64")
    return struct.unpack(">d", buf[offset : offset + 8])[0], offset + 8


def _read_blob(buf: bytes, offset: int) -> tuple[bytes, int]:
    size, offset = _read_int32(buf, offset)
    if size < 0:
        raise OscDecodeError("negative blob size")
    end = offset + size
    if end > len(buf):
        raise OscDecodeError("unexpected end of packet while reading blob")
    blob = buf[offset:end]
    offset = end
    offset += _pad4(offset)
    return blob, offset


def _blob_to_json(blob: bytes) -> dict[str, str]:
    return {"_type": "blob", "b64": base64.b64encode(blob).decode("ascii")}


def decode_osc_message(packet: bytes) -> tuple[str, list[Any]]:
    """Decode a single OSC message.

    Supports a practical subset of OSC 1.0:
      - address (osc-string)
      - typetag string (osc-string beginning with ',')
      - arguments for tags: i, f, s, b, h, d, T, F, N, I

    Notes
    -----
    OSC is defined in terms of 4-byte aligned fields. Address patterns and type
    tag strings are NUL-terminated and padded to a 4-byte boundary.
    """

    off = 0
    address, off = _read_osc_string(packet, off)
    typetags, off = _read_osc_string(packet, off)
    if not typetags.startswith(","):
        raise OscDecodeError("typetag string must begin with ','")

    tags = typetags[1:]
    args: list[Any] = []

    for t in tags:
        if t == "i":
            v, off = _read_int32(packet, off)
            args.append(v)
        elif t == "h":
            v, off = _read_int64(packet, off)
            args.append(v)
        elif t == "f":
            v, off = _read_float32(packet, off)
            args.append(v)
        elif t == "d":
            v, off = _read_float64(packet, off)
            args.append(v)
        elif t == "s":
            v, off = _read_osc_string(packet, off)
            args.append(v)
        elif t == "b":
            blob, off = _read_blob(packet, off)
            args.append(_blob_to_json(blob))
        elif t == "T":
            args.append(True)
        elif t == "F":
            args.append(False)
        elif t == "N":
            args.append(None)
        elif t == "I":
            args.append({"_type": "impulse"})
        else:
            # Unknown tag: keep a placeholder and stop parsing to avoid drifting.
            args.append({"_type": "unknown", "tag": t})
            break

    return address, args


def iter_osc_packets(packet: bytes) -> Iterator[tuple[str, list[Any]]]:
    """Iterate OSC messages from a packet.

    Supports OSC bundles (#bundle) by yielding each contained element that is a
    message (nested bundles are expanded recursively).
    """

    if packet.startswith(b"#bundle\x00"):
        # Bundle format:
        #   '#bundle\0' + 8-byte timetag + [ int32 size + element bytes ]*
        off = 8
        if off + 8 > len(packet):
            raise OscDecodeError("bundle missing timetag")
        off += 8
        while off < len(packet):
            sz, off = _read_int32(packet, off)
            if sz < 0:
                raise OscDecodeError("negative element size in bundle")
            end = off + sz
            if end > len(packet):
                raise OscDecodeError("bundle element overruns packet")
            elem = packet[off:end]
            off = end
            # Elements may be bundles or messages.
            for msg in iter_osc_packets(elem):
                yield msg
        return

    # Plain message.
    yield decode_osc_message(packet)


def _try_parse_json(s: str) -> Any:
    try:
        return json.loads(s)
    except Exception:
        return s


@dataclass
class OscdConfig:
    host: str = "127.0.0.1"
    port: int = 40001
    bus_socket: str = ""
    default_event: str = "osc"
    dispatch_event: str = "hotkey"
    token: str | None = None


class _OscUDPServer(socketserver.ThreadingUDPServer):
    allow_reuse_address = True


class _OscHandler(socketserver.BaseRequestHandler):
    def handle(self) -> None:
        data = self.request[0]
        srv: "OscdServer" = self.server  # type: ignore
        srv.handle_packet(data)


class OscdServer:
    """A small OSC UDP server that emits VHK bus events."""

    def __init__(self, cfg: OscdConfig):
        self.cfg = cfg
        self._srv = _OscUDPServer((cfg.host, int(cfg.port)), _OscHandler)
        # Attach self to server for handler access.
        self._srv.handle_packet = self.handle_packet  # type: ignore[attr-defined]

    @property
    def address(self) -> tuple[str, int]:
        host, port = self._srv.server_address
        return str(host), int(port)

    def serve_forever(self, *, poll_interval: float = 0.1) -> None:
        self._srv.serve_forever(poll_interval=poll_interval)

    def shutdown(self) -> None:
        self._srv.shutdown()

    def server_close(self) -> None:
        self._srv.server_close()

    def handle_packet(self, packet: bytes) -> None:
        from vhk.system.event_bus import emit_bus_event

        for address, args in iter_osc_packets(packet):
            # Optional token gate: if set, the first argument must match.
            if self.cfg.token:
                if not args:
                    continue
                if str(args[0]) != str(self.cfg.token):
                    continue
                args = args[1:]

            addr = (address or "").strip()
            if not addr.startswith("/"):
                addr = "/" + addr

            # Control addresses.
            if addr == "/vhk/emit":
                if not args:
                    continue
                ev = str(args[0])
                payload: Any = None
                if len(args) >= 2:
                    if isinstance(args[1], str):
                        payload = _try_parse_json(args[1])
                    else:
                        payload = args[1]
                emit_bus_event(self.cfg.bus_socket, ev,
                    payload,
                )
                continue

            if addr.startswith("/vhk/emit/"):
                ev = addr[len("/vhk/emit/") :].replace("/", ".")
                payload: Any = None
                if args:
                    if len(args) == 1 and isinstance(args[0], str):
                        payload = _try_parse_json(args[0])
                    else:
                        payload = args
                emit_bus_event(self.cfg.bus_socket, ev, payload)
                continue

            if addr == "/vhk/dispatch" or addr.startswith("/vhk/dispatch/"):
                macro = ""
                payload: dict[str, Any] = {"vars": {}}

                if addr.startswith("/vhk/dispatch/"):
                    macro = addr[len("/vhk/dispatch/") :].split("/", 1)[0]

                if args:
                    if not macro:
                        macro = str(args[0])
                        rest = args[1:]
                    else:
                        rest = args

                    if rest:
                        if isinstance(rest[0], str):
                            v = _try_parse_json(rest[0])
                            if isinstance(v, dict):
                                payload["vars"] = v
                            else:
                                payload["vars"] = {"value": v}
                        else:
                            payload["vars"] = {"value": rest[0]}

                if not macro:
                    continue
                payload["macro"] = macro
                payload["source"] = "osc"
                payload["address"] = addr
                payload["args"] = args
                emit_bus_event(self.cfg.bus_socket, self.cfg.dispatch_event, payload)
                continue

            if addr.startswith("/vhk/bus/"):
                ev = addr[len("/vhk/bus/") :].replace("/", ".")
                payload: Any = None
                if args:
                    if len(args) == 1 and isinstance(args[0], str):
                        payload = _try_parse_json(args[0])
                    else:
                        payload = args
                emit_bus_event(self.cfg.bus_socket, ev, payload)
                continue

            # Default: emit a generic osc event.
            emit_bus_event(
                self.cfg.bus_socket,
                self.cfg.default_event,
                {"address": addr, "args": args},
            )


def make_oscd_server(cfg: OscdConfig) -> OscdServer:
    return OscdServer(cfg)


def start_oscd_in_thread(cfg: OscdConfig) -> tuple[OscdServer, threading.Thread]:
    srv = make_oscd_server(cfg)
    th = threading.Thread(target=srv.serve_forever, kwargs={"poll_interval": 0.05}, daemon=True)
    th.start()
    return srv, th


# ----- minimal encoder (primarily for tests) -----

def _osc_string_bytes(s: str) -> bytes:
    b = s.encode("utf-8", errors="replace") + b"\x00"
    b += b"\x00" * _pad4(len(b))
    return b


def encode_osc_message(address: str, args: Sequence[Any] = ()) -> bytes:
    """Encode a small OSC message.

    Supports tags: i, f, s, b, h, d, T/F/N (inferred from Python types).
    """

    addr = address if address.startswith("/") else "/" + address

    tags = ","
    arg_bytes: list[bytes] = []

    for a in args:
        if a is True:
            tags += "T"
        elif a is False:
            tags += "F"
        elif a is None:
            tags += "N"
        elif isinstance(a, int) and -(2**31) <= a < 2**31:
            tags += "i"
            arg_bytes.append(struct.pack(">i", int(a)))
        elif isinstance(a, int):
            tags += "h"
            arg_bytes.append(struct.pack(">q", int(a)))
        elif isinstance(a, float):
            tags += "f"
            arg_bytes.append(struct.pack(">f", float(a)))
        elif isinstance(a, (bytes, bytearray)):
            tags += "b"
            bb = bytes(a)
            arg_bytes.append(struct.pack(">i", len(bb)) + bb + (b"\x00" * _pad4(len(bb))))
        else:
            tags += "s"
            arg_bytes.append(_osc_string_bytes(str(a)))

    out = b"".join([
        _osc_string_bytes(addr),
        _osc_string_bytes(tags),
        *arg_bytes,
    ])
    return out
