#!/usr/bin/env python3
"""Generate PROTO-FRAME-PARSER-01 / U-137+U-175 evidence across archived source lanes."""
from __future__ import annotations

import csv
import json
import os
import subprocess
import sys
from pathlib import Path

SRC_ROOT = Path(os.environ.get(
    "NICOTINE_SOURCE_ROOT",
    "/mnt/data/src_rev0003/Nicotine+DEV-rev0003-upstream-sources-20260612T181540Z/source-trees",
))
LANES = ["github-tag-3.3.10", "github-branch-3.3.x", "github-branch-master"]
OUT_DIR = Path(os.environ.get("PROTO_FRAME_PROBE_OUT", "/mnt/data"))

CHILD = r'''
from __future__ import annotations
import json, struct
from types import SimpleNamespace
import pynicotine.slskproto as proto_mod
from pynicotine.slskproto import NetworkThread
from pynicotine.slskmessages import SayChatroom, FileSearchRequest, DistribSearch, SlskMessage, ConnectionType, PeerInit

class FakeLog:
    def __init__(self): self.debug=[]; self.conn=[]; self.msgs=[]
    def add_debug(self, message, args=None): self.debug.append((message, repr(args)))
    def add_conn(self, message, args=None): self.conn.append((message, repr(args)))
    def add(self, message, args=None): self.conn.append((message, repr(args)))
    def add_msg_contents(self, msg): self.msgs.append(type(msg).__name__)

class FakeEvents:
    def __init__(self): self.emitted=[]
    def connect(self, *a, **k): return None
    def emit_main_thread(self, event_name, *args, **kwargs): self.emitted.append((event_name, args, kwargs))

def pack_declared(declared, actual): return struct.pack('<I', declared) + actual

def make_msg(cls, payload):
    try: return cls(msg_content=memoryview(payload))
    except TypeError: return cls()

def parse_msg(obj, payload):
    try:
        obj.parse_network_message(memoryview(payload))
    except TypeError:
        if getattr(obj, '_message', None) is None:
            obj._message=memoryview(payload); obj._offset=0
        obj.parse_network_message()

def final_field_cases():
    cases=[
        ('u137_server_saychatroom_final_string_truncated', SayChatroom, pack_declared(4,b'room')+pack_declared(4,b'user')+pack_declared(10,b'abc'), 'message', 'abc', 10, 3),
        ('u137_peer_filesearchrequest_final_string_truncated', FileSearchRequest, struct.pack('<I', 0x12345678)+pack_declared(12,b'needle'), 'searchterm', 'needle', 12, 6),
        ('u137_distrib_search_final_string_truncated', DistribSearch, struct.pack('<I',1)+pack_declared(6,b'srcusr')+struct.pack('<I',0x778899aa)+pack_declared(12,b'query'), 'searchterm', 'query', 12, 5),
    ]
    rows=[]
    for case, cls, payload, attr, expected, declared, actual in cases:
        obj=make_msg(cls, payload); error=None; ok=True
        try: parse_msg(obj, payload)
        except Exception as exc: ok=False; error=repr(exc)
        rows.append({'case':case,'family':'U-137','boundary':case.split('_')[1], 'ok':ok, 'error':error, 'declared_len':declared, 'actual_len':actual, 'payload_len':len(payload), 'field_value':getattr(obj, attr, None), 'accepted_truncated':ok and getattr(obj, attr, None)==expected, 'parser_offset':getattr(obj,'_offset',None)})
    payload=pack_declared(20,b'abc'); error=None; ok=True; value=None; offset=None
    try:
        try:
            offset,value=SlskMessage.unpack_bytes(memoryview(payload),0)
        except TypeError:
            obj=SlskMessage(msg_content=memoryview(payload)); value=obj.unpack_bytes(); offset=obj._offset
    except Exception as exc:
        ok=False; error=repr(exc)
    rows.append({'case':'u137_lowlevel_unpack_bytes_truncated','family':'U-137','boundary':'helper','ok':ok,'error':error,'declared_len':20,'actual_len':3,'payload_len':len(payload),'value_len':None if value is None else len(value),'accepted_truncated':ok and value==b'abc','parser_offset':offset})
    return rows

def frame_cases():
    fake_log=FakeLog(); fake_events=FakeEvents(); proto_mod.log=fake_log; proto_mod.events=fake_events
    proto=NetworkThread(); closed=[]; proto._close_connection=lambda conn: closed.append(conn)
    rows=[]
    def frame(size): return bytearray(struct.pack('<I',size)+struct.pack('<I',0x41424344))
    for boundary in ['server','peer']:
        for size in [0,1,2,3]:
            fake_log.debug.clear(); closed.clear()
            if boundary=='server':
                conn=SimpleNamespace(in_buffer=frame(size), has_post_init_activity=False)
                proto._process_server_input(conn)
            else:
                conn=SimpleNamespace(in_buffer=frame(size), has_post_init_activity=False, init=PeerInit(init_user='peer', target_user='peer', conn_type=ConnectionType.PEER), sock=object(), addr=('203.0.113.9',2234))
                proto._process_peer_input(conn)
            rows.append({'case':f'u175_{boundary}_declared_size_less_than_code_width','family':'U-175','boundary':boundary,'declared_size':size,'minimum_code_width':4,'closed':bool(closed),'remaining_buffer_len':len(conn.in_buffer),'remaining_hex':conn.in_buffer.hex(),'debug_count':len(fake_log.debug),'has_post_init_activity':getattr(conn,'has_post_init_activity',None),'not_rejected':not bool(closed)})
    fake_log.debug.clear(); closed.clear()
    conn=SimpleNamespace(in_buffer=bytearray(struct.pack('<I',0)+b'X'), has_post_init_activity=False, init=PeerInit(init_user='peer', target_user='peer', conn_type=ConnectionType.DISTRIBUTED), sock=object(), addr=('203.0.113.9',2234))
    proto._process_distrib_input(conn)
    rows.append({'case':'u175_distrib_declared_size_less_than_code_width','family':'U-175','boundary':'distributed','declared_size':0,'minimum_code_width':1,'closed':bool(closed),'remaining_buffer_len':len(conn.in_buffer),'remaining_hex':conn.in_buffer.hex(),'debug_count':len(fake_log.debug),'has_post_init_activity':getattr(conn,'has_post_init_activity',None),'not_rejected':not bool(closed)})
    return rows

print(json.dumps(final_field_cases()+frame_cases(), sort_keys=True))
'''

def run_lane(lane: str) -> list[dict]:
    env = os.environ.copy()
    env["PYTHONPATH"] = str(SRC_ROOT / lane)
    proc = subprocess.run([sys.executable, "-c", CHILD], env=env, text=True, capture_output=True, check=True, timeout=60)
    rows = json.loads(proc.stdout)
    for row in rows:
        row["lane"] = lane
    return rows

all_rows: list[dict] = []
for lane in LANES:
    all_rows.extend(run_lane(lane))

OUT_DIR.mkdir(parents=True, exist_ok=True)
jsonl = OUT_DIR / "rev0025-proto-frame-parser-probe.jsonl"
csv_path = OUT_DIR / "rev0025-proto-frame-parser-probe-summary.csv"
with jsonl.open("w", encoding="utf-8") as fh:
    for row in all_rows:
        fh.write(json.dumps(row, sort_keys=True) + "\n")
fields = sorted({key for row in all_rows for key in row})
with csv_path.open("w", encoding="utf-8", newline="") as fh:
    writer = csv.DictWriter(fh, fieldnames=fields)
    writer.writeheader()
    writer.writerows(all_rows)
print(jsonl)
print(csv_path)
