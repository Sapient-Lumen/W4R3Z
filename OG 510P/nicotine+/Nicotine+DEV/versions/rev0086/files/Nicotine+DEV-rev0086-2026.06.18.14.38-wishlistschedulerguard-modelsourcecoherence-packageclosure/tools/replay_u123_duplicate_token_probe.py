import sys, collections, json
from pathlib import Path
lane=Path(sys.argv[1])
sys.path.insert(0,str(lane))
from pynicotine.transfers import Transfers, Transfer
import pynicotine.transfers as tr
class Users:
    def __init__(self): self.calls=[]
    def watch_user(self, username, context=None): self.calls.append((username, context))
class Core: pass
core=Core(); core.users=Users(); tr.core=core
class Events:
    def __init__(self): self.n=0
    def schedule(self, delay, callback, callback_args=(), repeat=False):
        self.n += 1
        return f'timer-{self.n}'
events=Events(); tr.events=events
obj=Transfers.__new__(Transfers)
for name, val in {
    'transfers': {}, 'queued_transfers': {}, 'queued_users': collections.defaultdict(dict),
    'active_users': collections.defaultdict(dict), 'failed_users': collections.defaultdict(dict),
    'transfers_file_path': '', 'total_bandwidth': 0, '_name': 'downloads',
    '_allow_saving_transfers': False, '_online_users': set(), '_user_queue_limits': collections.defaultdict(int),
    '_user_queue_sizes': collections.defaultdict(int)
}.items():
    setattr(obj, name, val)

t1=Transfer('alice','\\Music\\a.mp3',size=1,status='Queued')
t2=Transfer('alice','\\Music\\b.mp3',size=1,status='Queued')
obj._activate_transfer(t1, 4242)
obj._activate_transfer(t2, 4242)
print(json.dumps({
    'lane': lane.name,
    'active_user_keys': list(obj.active_users.keys()),
    'active_tokens': list(obj.active_users['alice'].keys()),
    'active_virtual_path': obj.active_users['alice'][4242].virtual_path,
    'first_transfer_still_indexed': any(x is t1 for x in obj.active_users['alice'].values()),
    'second_transfer_indexed': any(x is t2 for x in obj.active_users['alice'].values()),
    'first_transfer_token': t1.token,
    'second_transfer_token': t2.token,
    'first_timer': t1.request_timer_id,
    'second_timer': t2.request_timer_id,
    'watch_calls': core.users.calls
}, sort_keys=True))
