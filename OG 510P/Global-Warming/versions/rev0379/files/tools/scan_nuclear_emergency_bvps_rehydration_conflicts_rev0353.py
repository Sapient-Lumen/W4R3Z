#!/usr/bin/env python3
import csv, json
from pathlib import Path
base = Path(__file__).resolve().parents[1]
board = list(csv.DictReader(open(base/'cube/nuclear-emergency-bvps-offline-live-release-conflict-repair-board-rev0353.csv', newline='', encoding='utf-8')))
summary = {
    'rows': len(board),
    'claim_freeze_active': sum(1 for r in board if r['claim_freeze']=='active'),
    'auto_close_blocks': sum(1 for r in board if r['auto_close_block']=='yes'),
    'open_repairs': sum(1 for r in board if r['repair_board_state']=='open')
}
print(json.dumps(summary, indent=2))
