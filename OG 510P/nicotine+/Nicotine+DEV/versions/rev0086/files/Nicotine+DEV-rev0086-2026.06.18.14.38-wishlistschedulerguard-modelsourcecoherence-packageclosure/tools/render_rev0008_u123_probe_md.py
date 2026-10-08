#!/usr/bin/env python3
import json, csv
from pathlib import Path
rows=[]
md=['# rev0008 U-123 socket/F-connection limbo probe','','## Scope','','Local non-network harness. It uses Nicotine+ source-lane code paths for `Downloads._transfer_request()`, `Downloads._file_transfer_init()`, `Downloads._file_download_progress()`, and `Downloads._file_connection_closed()`. It does not connect to the Soulseek network and it only opens temporary local incomplete-download files.','','## Result matrix','', '| lane | duplicate requests accepted | second F socket attached | stale first timeout deleted second active mapping | later progress ignored | later close ignored / handle left open | distinct-token control survives |', '|---|---:|---:|---:|---:|---:|---:|']
for line in Path('/mnt/data/rev0008_u123_socket_limbo_probe.jsonl').read_text().splitlines():
    r=json.loads(line); inv=r['invariants']; lane=r['lane']
    rows.append({'lane':lane, **{k:str(v) for k,v in inv.items()}})
    md.append(f"| {lane} | {inv['both_duplicate_requests_allowed']} | {inv['duplicate_second_attached_f_socket']} | {inv['stale_first_timeout_deleted_second_active_mapping']} | {inv['progress_after_deletion_was_ignored']} | {inv['close_after_deletion_was_ignored_and_handle_left_open']} | {inv['control_second_mapping_survives_first_timeout']} |")
md += ['','## Interpreted invariant','','The duplicate-token path is materially stronger than the rev0007 handler/timer proof. The later transfer can reach the F-connection stage and transition to `Transferring`; after the first transfer\'s stale timer fires, the shared `active_users[username][token]` entry is deleted. Subsequent progress and close callbacks for the second transfer lookup the same `username + token` key, find no active transfer, and return without cleaning the second socket/file session.','','The distinct-token control demonstrates the stale first timeout does not inherently break unrelated second transfers: with token 4243 for the second request, the second mapping survives, progress updates `current_byte_offset`, and close cleanup closes/aborts the second session.','','## Representative duplicate-token state sequence','','The same shape appeared in all three lanes. Compact state for each lane:','']
for line in Path('/mnt/data/rev0008_u123_socket_limbo_probe.jsonl').read_text().splitlines():
    r=json.loads(line); lane=r['lane']; states={s['label']:s for s in r['duplicate_token_result']['states']}
    md.append(f'### {lane}')
    md.append('')
    md.append('| state | active identity for token | second status | second indexed | second socket | second file handle open | second offset |')
    md.append('|---|---|---|---:|---:|---:|---|')
    for label in ['after_second_transfer_request','after_file_transfer_init_for_second_token','after_stale_first_timeout','after_progress_callback_for_second','after_close_callback_for_second_socket']:
        s=states[label]; second=s['second']
        md.append(f"| {label} | {s['active_identity_for_token']} | {second['status']} | {second['indexed_by_own_token']} | {second['sock_attached']} | {second['file_handle_open']} | {second['current_byte_offset']} |")
    md.append('')
md += ['## Why this belongs with U-169/U-170 but is not identical','','U-123 now proves an active transfer-session map integrity failure from a duplicate peer-supplied `TransferRequest` token. U-169/U-170 remain adjacent because F-connection attach/unknown-token behavior shares the same `username + token` lookup boundary. The coherent report should be one transfer-session integrity report, not three separate claims that ask for incompatible changes.','','## Fix shape tested by implication','','A single dictionary overwrite guard is not enough. The proof uses both activation and deactivation: activation overwrites the key, then stale deactivation deletes whatever object is now mapped at that key. The minimal coherent shape is:','','```text','1. Reject or quarantine a second active TransferRequest for the same username+token unless it is demonstrably the same transfer generation.','2. Make _deactivate_transfer() identity-checked: delete active_users[username][token] only when the mapped object is the same transfer being deactivated.','3. Keep FileTransferInit/progress/close compatibility with username+token, but require the found transfer to be in the expected generation/socket state.','```','','## Raw evidence','','Raw JSONL: `evidence/rev0008-u123-socket-limbo-probe.jsonl`']
Path('/mnt/data/rev0008_u123_socket_limbo_probe.md').write_text('\n'.join(md), encoding='utf-8')
with open('/mnt/data/rev0008_u123_socket_limbo_probe_summary.csv','w',newline='',encoding='utf-8') as f:
    fields=['lane','both_duplicate_requests_allowed','duplicate_second_attached_f_socket','stale_first_timeout_deleted_second_active_mapping','progress_after_deletion_was_ignored','close_after_deletion_was_ignored_and_handle_left_open','control_second_mapping_survives_first_timeout','control_progress_updates_second','control_close_aborts_or_cleans_second']
    w=csv.DictWriter(f, fieldnames=fields); w.writeheader(); w.writerows(rows)
print('/mnt/data/rev0008_u123_socket_limbo_probe.md')
