#!/usr/bin/env python3
"""Generate SEARCH-RESP-01 evidence for archived Nicotine+ source lanes."""
from __future__ import annotations

import csv
import json
import os
import subprocess
import sys
from pathlib import Path

SRC_ROOT = Path('/mnt/data/upstream_sources/Nicotine+DEV-rev0003-upstream-sources-20260612T181540Z/source-trees')
LANES = ['github-tag-3.3.10', 'github-branch-3.3.x', 'github-branch-master']

CHILD = r'''
from __future__ import annotations
import inspect, json, struct, time, tracemalloc, zlib
from types import SimpleNamespace
import pynicotine.search as search_mod
from pynicotine.search import Search, SearchRequest
from pynicotine.slskmessages import FileSearchResponse, initial_token, increment_token
try:
    from pynicotine.slskmessages import SEARCH_TOKENS_ALLOWED
except ImportError:
    SEARCH_TOKENS_ALLOWED = None

TOKEN = 0x12345678

class FakeNetworkFilter:
    def __init__(self, ignored_users=frozenset(), ignored_ips=frozenset()):
        self.ignored_users=set(ignored_users); self.ignored_ips=set(ignored_ips)
    def is_user_ignored(self, username): return username in self.ignored_users
    def is_user_ip_ignored(self, username, ip_address): return (username, ip_address) in self.ignored_ips

def patch_core(nf=None):
    if nf is None: nf=FakeNetworkFilter()
    search_mod.core = SimpleNamespace(network_filter=nf)

def make_req(mode='user', users=None, is_ignored=False):
    kwargs=dict(token=TOKEN, term='needle', term_sanitized='needle', term_transmitted='needle', included_words=['needle'], excluded_words=[], mode=mode, room='room-a' if mode=='rooms' else None, users=users)
    if 'is_ignored' in inspect.signature(SearchRequest).parameters:
        kwargs['is_ignored']=is_ignored
    return SearchRequest(**kwargs)

def make_search(req):
    s=Search.__new__(Search); s.searches={TOKEN:req}; return s

def allow_token():
    if SEARCH_TOKENS_ALLOWED is not None:
        SEARCH_TOKENS_ALLOWED.clear(); SEARCH_TOKENS_ALLOWED.add(TOKEN)

def clear_token():
    if SEARCH_TOKENS_ALLOWED is not None:
        SEARCH_TOKENS_ALLOWED.clear()

def parse(payload, allowed=True):
    if SEARCH_TOKENS_ALLOWED is not None:
        if allowed: allow_token()
        else: clear_token()
        msg=FileSearchResponse(); msg.parse_network_message(payload); return msg
    msg=FileSearchResponse(msg_content=memoryview(payload))
    if allowed: msg.allowed_responses.add(TOKEN)
    msg.parse_network_message(); return msg

def pack_oversized_username(username_len=1_000_000, token=TOKEN):
    raw=bytearray(); raw += struct.pack('<I', username_len); raw += b'A'*username_len; raw += struct.pack('<I', token)
    raw += struct.pack('<I', 0); raw += struct.pack('?', True); raw += struct.pack('<I', 0); raw += struct.pack('<I', 0); raw += struct.pack('<I', 0)
    return zlib.compress(bytes(raw))

def make_private_payload():
    return FileSearchResponse(search_username='local-user', token=TOKEN, shares=[], freeulslots=True, ulspeed=0, inqueue=0, private_shares=[('private\\needle.mp3', 123, None, None)]).make_network_message()

results=[]
patch_core()
allow_token()
for mode, users, username in [('user',['expected-user'],'unexpected-user'), ('buddies',None,'not-in-buddies')]:
    msg=SimpleNamespace(token=TOKEN, username=username, addr=('203.0.113.10', 2242), list=[], privatelist=[], freeulslots=True, ulspeed=0, inqueue=0)
    make_search(make_req(mode=mode, users=users))._file_search_response(msg)
    results.append({'case':f'{mode}_unexpected_source_survives_core_gate','mode':mode,'requested_users':users,'response_username':username,'token_after':msg.token,'accepted':msg.token==TOKEN})

patch_core(FakeNetworkFilter(ignored_users={'blocked-user'})); allow_token()
msg=SimpleNamespace(token=TOKEN, username='blocked-user', addr=('203.0.113.12', 2242), list=[], privatelist=[], freeulslots=True, ulspeed=0, inqueue=0)
make_search(make_req(mode='user', users=['blocked-user']))._file_search_response(msg)
results.append({'case':'ignored_user_guard_drops_response','mode':'user','requested_users':['blocked-user'],'response_username':'blocked-user','token_after':msg.token,'accepted':msg.token==TOKEN})

payload=pack_oversized_username(1_000_000, TOKEN)
tracemalloc.start(); t0=time.perf_counter(); msg=parse(payload, allowed=False); dt=time.perf_counter()-t0; _cur, peak=tracemalloc.get_traced_memory(); tracemalloc.stop()
results.append({'case':'invalid_token_oversized_username_prefix_consumed','compressed_len':len(payload),'token_after':msg.token,'list_is_none':msg.list is None,'list_len':None if msg.list is None else len(msg.list),'seconds':dt,'tracemalloc_peak_bytes':peak})

payload=make_private_payload(); msg=parse(payload, allowed=True)
results.append({'case':'private_results_parsed_before_display_policy','compressed_len':len(payload),'token_after':msg.token,'public_len':None if msg.list is None else len(msg.list),'private_len':None if msg.privatelist is None else len(msg.privatelist)})

# token shape sample. Avoid claiming cryptographic proof; just record range and linear increment.
try:
    sample=[initial_token() for _ in range(32)]
    base=sample[0]
    inc=[increment_token(base+i) for i in range(3)]
    results.append({'case':'token_shape_sample','sample_min':min(sample),'sample_max':max(sample),'sample_count':len(sample),'increment_sequence_from_first':[base, *inc]})
except Exception as exc:
    results.append({'case':'token_shape_sample','error':repr(exc)})

print(json.dumps(results, sort_keys=True))
'''

def run_lane(lane: str):
    env = os.environ.copy()
    env['PYTHONPATH'] = str(SRC_ROOT / lane)
    proc = subprocess.run([sys.executable, '-c', CHILD], text=True, capture_output=True, env=env, check=True, timeout=60)
    data = json.loads(proc.stdout)
    for row in data:
        row['lane'] = lane
    return data

all_rows=[]
for lane in LANES:
    all_rows.extend(run_lane(lane))

out_jsonl=Path('/mnt/data/rev0013-search-resp-probe-results.jsonl')
out_csv=Path('/mnt/data/rev0013-search-resp-probe-summary.csv')
with out_jsonl.open('w', encoding='utf-8') as fh:
    for row in all_rows:
        fh.write(json.dumps(row, sort_keys=True)+"\n")

fields=sorted({key for row in all_rows for key in row})
with out_csv.open('w', encoding='utf-8', newline='') as fh:
    writer=csv.DictWriter(fh, fieldnames=fields)
    writer.writeheader()
    writer.writerows(all_rows)

print(out_jsonl)
print(out_csv)
