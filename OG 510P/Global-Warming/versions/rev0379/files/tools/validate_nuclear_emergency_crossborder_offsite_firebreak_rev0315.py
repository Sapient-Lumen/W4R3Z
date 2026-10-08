#!/usr/bin/env python3
"""Validate that rev0315 public/offsite source firebreak fixture outcomes match expected verdicts."""
import csv, sys
from pathlib import Path
p=Path(sys.argv[1] if len(sys.argv)>1 else "cube/nuclear-emergency-crossborder-firebreak-test-result-rev0315.csv")
rows=list(csv.DictReader(p.open(newline="")))
bad=[r for r in rows if r.get("expected_verdict")!=r.get("actual_verdict") or r.get("pass_fail")!="pass"]
print(f"rows={len(rows)} bad={len(bad)}")
sys.exit(1 if bad else 0)
