#!/usr/bin/env python3
"""Generate hard-search workpackets from rev0005 public-overlap ledger.

This helper does not browse the web. It prints exact queries and a markdown skeleton
for a selected set of IDs so a human/assistant can fill sources and conclusions.
"""
import argparse, csv, pathlib, sys

parser = argparse.ArgumentParser()
parser.add_argument('--ledger', default='data/rev0005_public_overlap_status.csv')
parser.add_argument('ids', nargs='*')
args = parser.parse_args()
root = pathlib.Path.cwd()
with (root / args.ledger).open(newline='', encoding='utf-8') as f:
    rows = list(csv.DictReader(f))
if args.ids:
    wanted = set(args.ids)
    rows = [r for r in rows if r['id'] in wanted]
for r in rows:
    print(f"## {r['id']} — {r['title']}")
    print()
    print(f"Cluster: {r['cluster']}")
    print(f"Current status: {r['public_overlap_class']}")
    print()
    print("### Required searches")
    queries = r.get('queries_or_next_queries') or 'TODO: derive exact root-cause, sink, class, and fix-shape searches'
    for q in [x.strip() for x in queries.split(';') if x.strip()]:
        print(f"- {q}")
    print()
    print("### Fill-in evidence")
    print("- Direct public overlap:")
    print("- Public-adjacent overlap:")
    print("- Upstream-in-flight overlap:")
    print("- No-direct-public searches performed:")
    print("- Final classification:")
    print()
