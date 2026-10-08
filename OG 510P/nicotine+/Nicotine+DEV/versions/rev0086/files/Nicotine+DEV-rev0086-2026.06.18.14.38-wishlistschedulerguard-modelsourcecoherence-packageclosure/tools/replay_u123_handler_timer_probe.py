#!/usr/bin/env python3
import sys, json, collections, types, traceback
from pathlib import Path

lane = Path(sys.argv[1]).resolve()
sys.path.insert(0, str(lane))

try:
    import pynicotine.downloads as dl
    import pynicotine.transfers as tr
    from pynicotine.downloads import Downloads
    from pynicotine.transfers import Transfer, TransferStatus
    from pynicotine.slskmessages import TransferDirection

    class FakeUsers:
        def __init__(self):
            self.watch_calls=[]; self.unwatch_calls=[]; self.login_status = 2; self.statuses={}
        def watch_user(self, username, context=None):
            self.watch_calls.append((username, context))
        def unwatch_user(self, username, context=None):
            self.unwatch_calls.append((username, context))
    class FakeCore:
        def __init__(self):
            self.users=FakeUsers(); self.peer_messages=[]; self.network_messages=[]
        def send_message_to_peer(self, username, msg):
            self.peer_messages.append({
                "username": username,
                "type": type(msg).__name__,
                "allowed": getattr(msg, "allowed", None),
                "token": getattr(msg, "token", None),
                "reason": getattr(msg, "reason", None)
            })
        def send_message_to_network_thread(self, msg):
            self.network_messages.append(type(msg).__name__)
    class FakeEvents:
        def __init__(self):
            self.next_id=0; self.scheduled={}; self.cancelled=[]; self.emitted=[]
        def schedule(self, delay, callback, callback_args=(), repeat=False):
            self.next_id += 1
            ident = f"timer-{self.next_id}"
            self.scheduled[ident] = {
                "delay": delay,
                "callback_name": getattr(callback, "__name__", repr(callback)),
                "callback": callback,
                "callback_args": callback_args,
                "repeat": repeat,
            }
            return ident
        def cancel_scheduled(self, ident):
            self.cancelled.append(ident)
            self.scheduled.pop(ident, None)
        def emit(self, *args):
            self.emitted.append([repr(x) for x in args])
        def connect(self, *args, **kwargs):
            pass
    class FakeLog:
        def __init__(self): self.transfer=[]; self.general=[]
        def add_transfer(self, msg, args=None): self.transfer.append([str(msg), repr(args)])
        def add(self, msg, args=None): self.general.append([str(msg), repr(args)])

    fake_core=FakeCore(); fake_events=FakeEvents(); fake_log=FakeLog()
    for mod in (tr, dl):
        mod.core = fake_core
        mod.events = fake_events
        mod.log = fake_log

    # Construct Downloads without subscribing to application events.
    obj = Downloads.__new__(Downloads)
    for name, val in {
        'transfers': {}, 'queued_transfers': {}, 'queued_users': collections.defaultdict(dict),
        'active_users': collections.defaultdict(dict), 'failed_users': collections.defaultdict(dict),
        'transfers_file_path': '', 'total_bandwidth': 0, '_name': 'downloads',
        '_allow_saving_transfers': False, '_online_users': set(), '_user_queue_limits': collections.defaultdict(int),
        '_user_queue_sizes': collections.defaultdict(int),
        '_requested_folders': collections.defaultdict(dict), '_requested_folder_token': 0,
        '_folder_basename_byte_limits': {}, '_pending_queue_messages': {},
        '_download_queue_timer_id': None, '_retry_connection_downloads_timer_id': None,
        '_retry_io_downloads_timer_id': None,
    }.items():
        setattr(obj, name, val)

    # Two separate queued downloads from the same username.
    t1 = Transfer('alice', '\\Music\\a.mp3', '/tmp/nicotine-test', size=111, status=TransferStatus.QUEUED)
    t2 = Transfer('alice', '\\Music\\b.mp3', '/tmp/nicotine-test', size=222, status=TransferStatus.QUEUED)
    for t in (t1, t2):
        obj.transfers[t.username + t.virtual_path] = t
        obj.queued_users[t.username][t.virtual_path] = t
        obj.queued_transfers[t] = None
        obj._user_queue_sizes[t.username] += t.size

    def snapshot(label):
        active = obj.active_users.get('alice', {})
        queued = obj.queued_users.get('alice', {})
        failed = obj.failed_users.get('alice', {})
        return {
            "label": label,
            "active_tokens": [str(k) for k in active.keys()],
            "active_paths": {str(k): v.virtual_path for k, v in active.items()},
            "active_identity": {str(k): ("t1" if v is t1 else "t2" if v is t2 else "other") for k, v in active.items()},
            "queued_paths": list(queued.keys()),
            "failed_paths": list(failed.keys()),
            "t1_status": t1.status, "t1_token": t1.token, "t1_timer": t1.request_timer_id,
            "t2_status": t2.status, "t2_token": t2.token, "t2_timer": t2.request_timer_id,
        }

    states=[]
    states.append(snapshot("initial_queued"))

    token = 4242
    msg1 = types.SimpleNamespace(username='alice', direction=TransferDirection.UPLOAD, file='\\Music\\a.mp3', filesize=111, token=token)
    msg2 = types.SimpleNamespace(username='alice', direction=TransferDirection.UPLOAD, file='\\Music\\b.mp3', filesize=222, token=token)

    obj._transfer_request(msg1)
    states.append(snapshot("after_transfer_request_a"))
    first_timer = t1.request_timer_id
    obj._transfer_request(msg2)
    states.append(snapshot("after_transfer_request_b_same_token"))

    # Replay the stale timer from the overwritten first transfer.
    first_timer_before_fire = first_timer
    obj._transfer_timeout(t1)
    states.append(snapshot("after_stale_timer_for_a"))

    result = {
        "lane": lane.name,
        "ok": True,
        "token": token,
        "states": states,
        "peer_responses": fake_core.peer_messages,
        "watch_calls": fake_core.users.watch_calls,
        "unwatch_calls": fake_core.users.unwatch_calls,
        "cancelled_timers": fake_events.cancelled,
        "first_timer_before_fire": first_timer_before_fire,
        "invariant_result": {
            "second_request_overwrote_first": states[2]["active_identity"].get(str(token)) == "t2",
            "stale_first_timer_removed_second_mapping": str(token) not in states[3]["active_tokens"],
            "second_transfer_left_with_token_but_unindexed": (t2.token == token and str(token) not in states[3]["active_tokens"]),
            "both_transfer_requests_allowed": [m.get("allowed") for m in fake_core.peer_messages] == [True, True],
        }
    }
except Exception as e:
    result = {"lane": lane.name, "ok": False, "error": repr(e), "traceback": traceback.format_exc()}
print(json.dumps(result, sort_keys=True))
