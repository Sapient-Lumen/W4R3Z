#!/usr/bin/env python3
import csv
from pathlib import Path
root = Path(__file__).resolve().parents[1]
rows = list(csv.DictReader((root/'data/rev0002_ranked_audit_queue.csv').open(encoding='utf-8')))
for row in rows[:40]:
    print(f"{row['priority_bucket']:32} {row['priority_score']:>3} {row['id']:>5} {row['cluster']}: {row['title']}")
