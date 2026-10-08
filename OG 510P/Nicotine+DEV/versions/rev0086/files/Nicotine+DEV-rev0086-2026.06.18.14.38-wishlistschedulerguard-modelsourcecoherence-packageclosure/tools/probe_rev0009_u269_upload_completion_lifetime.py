#!/usr/bin/env python3
"""rev0009 U-269 upload completion/lifetime probe.

Local non-network simulation against a Nicotine+ source tree. It checks the main-thread
upload lifecycle after the network layer reports that advertised bytes have been sent:
FileTransferInit -> UploadFile issuance -> file-upload-progress with offset+bytes == size.
It does not open a real network socket.
"""
from __future__ import annotations
import argparse, collections, json, os, sys, tempfile, types, time
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument('source_tree')
parser.add_argument('--lane', default='unknown')
args = parser.parse_args()
SRC=str(Path(args.source_tree).resolve())
sys.path.insert(0, SRC)

try:
    import pynicotine.uploads as uploads_mod
    import pynicotine.transfers as transfers_mod
    import pynicotine.config as config_mod
    from pynicotine.uploads import Uploads
    from pynicotine.transfers import Transfer, TransferStatus
    from pynicotine.slskmessages import FileTransferInit, UploadFile, SendUploadSpeed, CloseConnection, UserStatus
except Exception as exc:
    print(json.dumps({'lane': args.lane, 'status':'import-error', 'error':repr(exc)}, sort_keys=True))
    raise SystemExit(0)

class FakeSock:
    def __repr__(self): return '<FakeSock rev0009-u269>'

class StubUsers:
    def __init__(self):
        self.watches=[]; self.unwatches=[]; self.addresses={}; self.statuses={}; self.login_status=2
    def watch_user(self, username, context=None): self.watches.append({'username': username, 'context': context})
    def unwatch_user(self, username, context=None): self.unwatches.append({'username': username, 'context': context})

class StubShares:
    def __init__(self, mapping): self.mapping=mapping
    def virtual2real(self, virtual_path, revert_backslash=False, is_lowercase_path=False): return self.mapping[virtual_path]

class StubPluginHandler:
    def __init__(self): self.started=[]; self.finished=[]
    def upload_started_notification(self, username, virtual_path, real_path): self.started.append({'username': username, 'path': virtual_path, 'real_path': str(real_path)})
    def upload_finished_notification(self, username, virtual_path, real_path): self.finished.append({'username': username, 'path': virtual_path, 'real_path': str(real_path)})

class StubStatistics:
    def __init__(self): self.values=[]
    def append_stat_value(self, key, value): self.values.append({'key':key,'value':value})

class StubCore:
    def __init__(self, mapping):
        self.users=StubUsers(); self.users.addresses['peer']='203.0.113.10'; self.users.statuses['peer']=UserStatus.ONLINE
        self.shares=StubShares(mapping)
        self.pluginhandler=StubPluginHandler(); self.statistics=StubStatistics(); self.sent_network=[]; self.sent_peer=[]; self.sent_server=[]
    def send_message_to_network_thread(self, msg):
        self.sent_network.append({'class': msg.__class__.__name__, 'token': getattr(msg,'token',None), 'size': getattr(msg,'size',None), 'sock_repr': repr(getattr(msg,'sock',None))})
    def send_message_to_peer(self, username, msg):
        self.sent_peer.append({'username': username, 'class': msg.__class__.__name__, 'file': getattr(msg, 'file', None)})
    def send_message_to_server(self, msg):
        self.sent_server.append({'class': msg.__class__.__name__, 'speed': getattr(msg, 'speed', None)})

class StubEvents:
    def __init__(self): self.cancelled=[]; self.scheduled=[]; self.emitted=[]
    def schedule(self, delay=None, callback=None, callback_args=(), repeat=False, **kwargs):
        tid=f'timer-{len(self.scheduled)+1}'; self.scheduled.append({'timer_id':tid,'delay':delay,'callback':getattr(callback,'__name__',repr(callback))}); return tid
    def cancel_scheduled(self, timer_id): self.cancelled.append(timer_id)
    def emit(self,*args,**kwargs): self.emitted.append({'args':[str(a) for a in args], 'kwargs':{k:str(v) for k,v in kwargs.items()}})
    def connect(self,*args,**kwargs): pass

class StubLog:
    def __init__(self): self.entries=[]
    def add(self, fmt, args=None): self.entries.append({'type':'general','fmt':str(fmt),'args':repr(args)})
    def add_transfer(self, fmt, args=None): self.entries.append({'type':'transfer','fmt':str(fmt),'args':repr(args)})
    def add_upload(self, fmt, args=None): self.entries.append({'type':'upload','fmt':str(fmt),'args':repr(args)})

class ProbeUploads(Uploads):
    __slots__=('updates',)
    def _update_transfer(self, transfer):
        self.updates.append({'status': transfer.status, 'token': transfer.token, 'sock_attached': transfer.sock is not None, 'current': transfer.current_byte_offset, 'size': transfer.size, 'file_open': transfer.file_handle is not None and not getattr(transfer.file_handle, 'closed', True)})
    def _check_upload_queue(self): pass
    def _show_queued_upload_notifications(self): pass

def patch(tmpdir, mapping):
    core=StubCore(mapping); events=StubEvents(); log=StubLog()
    cfg=types.SimpleNamespace(data_folder_path=tmpdir, sections={'transfers': {'autoclear_uploads': False, 'use_upload_speed_limit': 'unlimited', 'uploadlimit': 0, 'uploadlimitalt':0}, 'notifications': {}})
    for mod in (uploads_mod, transfers_mod):
        mod.core=core; mod.events=events; mod.log=log; mod.config=cfg
    try: config_mod.config=cfg
    except Exception: pass
    return core, events, log, cfg

def make_uploads(tmpdir):
    obj=ProbeUploads.__new__(ProbeUploads)
    fields={
        'transfers':{}, 'queued_transfers':{}, 'queued_users':collections.defaultdict(dict), 'active_users':collections.defaultdict(dict), 'failed_users':collections.defaultdict(dict),
        'transfers_file_path':os.path.join(tmpdir,'uploads.json'), 'total_bandwidth':0, '_name':'uploads', '_allow_saving_transfers':False, '_online_users':set(), '_user_queue_limits':collections.defaultdict(int), '_user_queue_sizes':collections.defaultdict(int),
        'pending_shutdown':False, 'upload_speed':0, 'token':1000, '_queue_positions':{}, '_queue_position_users':collections.defaultdict(dict), '_privileged_position_requested':False, '_pending_network_msgs':[], '_queue_notification_users':collections.defaultdict(list), '_user_update_counter':0, '_user_update_counters':{}, '_queue_notification_timer_id':None, '_upload_queue_timer_id':None, '_retry_failed_uploads_timer_id':None}
    for k,v in fields.items():
        try: setattr(obj,k,v)
        except Exception: pass
    obj.updates=[]
    return obj

def make_file_init(username, token, sock):
    msg=FileTransferInit(token=token, is_outgoing=True)
    try:
        wire=msg.make_network_message()
        try:
            parsed=FileTransferInit(); parsed.parse_network_message(memoryview(wire))
        except TypeError:
            parsed=FileTransferInit(msg_content=memoryview(wire)); parsed.parse_network_message();
            try: parsed.finish_parsing()
            except Exception: pass
        msg=parsed
    except Exception: pass
    msg.username=username; msg.token=token; msg.is_outgoing=True; msg.sock=sock
    return msg

def snapshot(label, obj, transfer, core, events):
    active=obj.active_users.get(transfer.username,{})
    return {'label': label, 'status': transfer.status, 'token': transfer.token, 'current': transfer.current_byte_offset, 'last': transfer.last_byte_offset, 'size': transfer.size, 'sock_attached': transfer.sock is not None, 'file_open': transfer.file_handle is not None and not getattr(transfer.file_handle,'closed',True), 'active_tokens': sorted([str(k) for k in active]), 'indexed': transfer.token is not None and active.get(transfer.token) is transfer, 'network_messages': list(core.sent_network), 'server_messages': list(core.sent_server), 'cancelled_timers': list(events.cancelled)}

def run():
    with tempfile.TemporaryDirectory(prefix='nplus-u269-') as tmpdir:
        virtual='Music\\complete.flac'; real=os.path.join(tmpdir,'share.flac'); data=b'A'*64
        Path(real).write_bytes(data)
        core, events, log, cfg=patch(tmpdir, {virtual: real})
        obj=make_uploads(tmpdir); t=Transfer(username='peer', virtual_path=virtual, folder_path=None, size=len(data)); t.status=TransferStatus.GETTING_STATUS; t.start_time=time.monotonic(); token=9001
        obj.transfers[t.username+t.virtual_path]=t; obj.active_users[t.username][token]=t; t.token=token; t.request_timer_id='request-timeout'
        states=[snapshot('active_before_file_init', obj, t, core, events)]
        obj._file_transfer_init(make_file_init('peer', token, FakeSock()))
        states.append(snapshot('after_file_transfer_init', obj, t, core, events))
        obj._file_upload_progress('peer', token, offset=0, bytes_sent=len(data), speed=999)
        states.append(snapshot('after_progress_all_bytes_sent_no_close', obj, t, core, events))
        # Control: if the peer closes, the same handler finalizes.
        sock=t.sock
        obj._file_connection_closed('peer', token, sock, timed_out=False)
        states.append(snapshot('after_control_close', obj, t, core, events))
        return {'lane': args.lane, 'source_tree': SRC, 'status':'ran', 'states':states, 'updates': obj.updates, 'logs': log.entries[-10:], 'invariants': {
            'uploadfile_issued': any(m['class']=='UploadFile' and m['size']==len(data) for m in core.sent_network),
            'all_bytes_progress_keeps_transfer_active': states[2]['indexed'] and states[2]['status']==TransferStatus.TRANSFERRING and states[2]['file_open'] is True,
            'no_finish_on_all_bytes_progress_alone': states[2]['status'] != TransferStatus.FINISHED,
            'control_close_finishes': states[3]['status']==TransferStatus.FINISHED and states[3]['indexed'] is False and states[3]['file_open'] is False,
        }}
try:
    print(json.dumps(run(), sort_keys=True))
except Exception as exc:
    print(json.dumps({'lane': args.lane, 'source_tree': SRC, 'status':'error', 'error':repr(exc)}, sort_keys=True))
