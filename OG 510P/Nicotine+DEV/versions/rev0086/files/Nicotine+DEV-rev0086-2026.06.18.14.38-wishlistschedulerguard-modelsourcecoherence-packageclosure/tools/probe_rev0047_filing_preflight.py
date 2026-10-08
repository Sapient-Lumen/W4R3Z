#!/usr/bin/env python3
from __future__ import annotations
import csv, json, sys
from pathlib import Path
PACKETS = [
 ("U-123", "report_drafts/U123-PRODUCTION-READY-MAINTAINER-REPORT-REV0037.md", "maintainer_artifacts/u123/test_downloads_duplicate_transfer_token_collision_rejection_regression.py", ["report_drafts/U123-SELECTED-PATCH-REV0037.diff", "evidence/rev0037-u123-collision-rejection-rerun.txt"], {"pynicotine/downloads.py":["active_users", "TransferRequest"], "pynicotine/transfers.py":["active_users"]}, False),
 ("PB-01", "report_drafts/PB01-PRODUCTION-READY-MAINTAINER-REPORT-REV0038.md", "maintainer_artifacts/pb01/test_peer_connection_primary_election_fixed_regression.py", ["report_drafts/PB01-SELECTED-PATCH-REV0038.diff", "evidence/rev0038-pb01-fixed-regression-rerun.txt"], {"pynicotine/slskproto.py":["_replace_existing_connection", "_process_peer_init_message", "_process_conn_incoming_messages"]}, False),
 ("SEARCH-RESP-01A", "report_drafts/SEARCH-RESP-01A-PRODUCTION-READY-MAINTAINER-REPORT-REV0039.md", "maintainer_artifacts/search-resp-01/test_search_response_user_scope_fixed_regression.py", ["report_drafts/SEARCH-RESP-01C-ROOM-SELECTED-PATCH-REV0043-master.diff", "evidence/rev0039-search-resp-user-scope-rerun-matrix.txt"], {"pynicotine/search.py":["_file_search_response", "UserSearch", "FileSearchResponse"]}, True),
 ("SEARCH-RESP-01B-BUDDY", "report_drafts/SEARCH-RESP-01B-PRODUCTION-READY-MAINTAINER-REPORT-REV0040.md", "maintainer_artifacts/search-resp-01/test_search_response_buddy_scope_fixed_regression.py", ["report_drafts/SEARCH-RESP-01C-ROOM-SELECTED-PATCH-REV0043-master.diff", "evidence/rev0040-search-resp-buddy-scope-rerun-matrix.txt"], {"pynicotine/search.py":["buddies", "UserSearch", "_file_search_response"]}, True),
 ("SEARCH-RESP-01C-ROOM", "report_drafts/SEARCH-RESP-01C-ROOM-PRODUCTION-READY-MAINTAINER-REPORT-REV0043.md", "maintainer_artifacts/search-resp-01/test_search_response_room_scope_fixed_regression.py", ["report_drafts/SEARCH-RESP-01C-ROOM-SELECTED-PATCH-REV0043-master.diff", "evidence/rev0043-search-resp-room-scope-rerun-matrix.txt"], {"pynicotine/search.py":["RoomSearch", "_file_search_response"], "pynicotine/chatrooms.py":["joined_rooms", "users"]}, False),
 ("SEARCH-RESP-PARSE-BUDGET-A", "report_drafts/SEARCH-RESP-PARSE-BUDGET-A-PRODUCTION-READY-MAINTAINER-REPORT-REV0041.md", "maintainer_artifacts/search-resp-01/test_search_response_prefix_budget_fixed_regression.py", ["report_drafts/SEARCH-RESP-PARSE-BUDGET-B-SELECTED-PATCH-REV0042-master.diff", "evidence/rev0041-search-resp-prefix-budget-rerun-matrix.txt"], {"pynicotine/slskmessages.py":["class FileSearchResponse", "username_len", "zlib"]}, True),
 ("SEARCH-RESP-PARSE-BUDGET-B", "report_drafts/SEARCH-RESP-PARSE-BUDGET-B-PRODUCTION-READY-MAINTAINER-REPORT-REV0042.md", "maintainer_artifacts/search-resp-01/test_search_response_result_budget_fixed_regression.py", ["report_drafts/SEARCH-RESP-PARSE-BUDGET-B-SELECTED-PATCH-REV0042-master.diff", "evidence/rev0042-search-resp-result-budget-rerun-matrix.txt"], {"pynicotine/slskmessages.py":["class FileSearchResponse", "privatelist", "_parse_result_list"]}, False),
]
LANES=["github-tag-3.3.10","github-branch-3.3.x","github-branch-master"]
def source_root(arg):
    if not arg: return None
    p=Path(arg).resolve()
    if (p/"source-trees").is_dir(): return p
    m=list(p.glob("*/source-trees"))
    return m[0].parent if m else p
def read(p):
    try: return p.read_text(encoding='utf-8', errors='replace')
    except FileNotFoundError: return ''
def main():
    cube=Path(__file__).resolve().parents[1]
    src=source_root(sys.argv[1]) if len(sys.argv)>1 else None
    errors=[]; checks=[]
    matrix=list(csv.DictReader((cube/'data/rev0046_strict_bundle_integration_matrix.csv').open(encoding='utf-8')))
    keys={(r['lane'],r['packet']) for r in matrix}
    matrix_ok=len(matrix)==21 and all(r.get('status')=='pass' for r in matrix)
    checks.append({'check':'rev0046 integration matrix','status':'pass' if matrix_ok else 'fail','rows':len(matrix)})
    if not matrix_ok: errors.append('rev0046 integration matrix is not a clean 21-row pass matrix')
    for packet,report,regression,req,anchors,needs_addendum in PACKETS:
        per=[]
        for rel in [report,regression,*req]:
            if not (cube/rel).is_file(): per.append(f'missing {rel}')
        if needs_addendum and '## Rev0047 filing addendum' not in read(cube/report): per.append('missing rev0047 filing addendum')
        for lane in LANES:
            if (lane,packet) not in keys: per.append(f'missing matrix row {lane}')
        if src:
            for lane in LANES:
                lane_root=src/'source-trees'/lane
                for rel, words in anchors.items():
                    txt=read(lane_root/rel)
                    for word in words:
                        if word not in txt: per.append(f'missing source anchor {lane}:{rel}:{word}')
        checks.append({'check':'packet preflight','packet':packet,'status':'pass' if not per else 'fail','errors':per})
        errors.extend([f'{packet}: {e}' for e in per])
    globals=["report_drafts/STRICT-FRONT-FILING-BUNDLE-INDEX-REV0047.md","report_drafts/STRICT-FRONT-MAINTAINER-COVER-NOTE-REV0047.md","report_drafts/SEARCH-RESP-SERIES-MAINTAINER-COVER-REV0047.md","data/rev0047_strict_filing_preflight.csv","data/rev0047_report_language_refactor.csv"]
    miss=[x for x in globals if not (cube/x).is_file()]
    if miss: errors.extend([f'missing global {x}' for x in miss])
    checks.append({'check':'rev0047 global files','status':'pass' if not miss else 'fail','missing':miss})
    out={'revision':'rev0047','status':'pass' if not errors else 'fail','source_root_checked':str(src) if src else None,'packet_count':len(PACKETS),'matrix_rows':len(matrix),'checks':checks,'errors':errors}
    print(json.dumps(out,indent=2))
    return 0 if not errors else 1
if __name__=='__main__': raise SystemExit(main())
