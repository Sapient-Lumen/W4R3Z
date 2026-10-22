#!/usr/bin/env python3
"""capgraph_diff.py

Tiny diff tool for CH-CAPG v0 snapshots (RFC-0035).

Default policy: fail if the *new* snapshot introduces any new authority edges.

Usage:
  python3 tools/capgraph_diff.py before.json after.json

Options:
  --allow-added REGEX   Allow added edges whose pretty string matches REGEX (repeatable).
  --quiet              Only print failures.

Input format: JSON object following docs/30-architecture/capability-graph-schema-v0.md.

This tool is intentionally minimal; it is not a full validator.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence, Set, Tuple


@dataclass(frozen=True)
class Node:
    kind: str
    label: str


@dataclass(frozen=True)
class Edge:
    src: Node
    dst: Node
    etype: str
    rights: str

    def pretty(self) -> str:
        r = f" rights={self.rights}" if self.rights else ""
        return f"{self.src.kind}:{self.src.label} -[{self.etype}{r}]-> {self.dst.kind}:{self.dst.label}"


def _load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as e:
        raise SystemExit(f"error: failed to parse JSON {path}: {e}")


def _expect(cond: bool, msg: str) -> None:
    if not cond:
        raise SystemExit(f"error: {msg}")


def _to_nodes(obj: Mapping[str, Any]) -> Dict[int, Node]:
    nodes = obj.get("nodes")
    _expect(isinstance(nodes, list), "CH-CAPG must have list 'nodes'")
    out: Dict[int, Node] = {}
    for n in nodes:
        _expect(isinstance(n, dict), "node must be object")
        nid = n.get("nid")
        kind = n.get("kind")
        label = n.get("label", "")
        _expect(isinstance(nid, int), "node.nid must be int")
        _expect(isinstance(kind, str), "node.kind must be str")
        _expect(isinstance(label, str), "node.label must be str")
        out[nid] = Node(kind=kind, label=label)
    return out


def _to_edges(obj: Mapping[str, Any], nodes: Mapping[int, Node]) -> Set[Edge]:
    edges = obj.get("edges")
    _expect(isinstance(edges, list), "CH-CAPG must have list 'edges'")
    out: Set[Edge] = set()
    for e in edges:
        _expect(isinstance(e, dict), "edge must be object")
        src = e.get("src")
        dst = e.get("dst")
        etype = e.get("etype")
        rights = e.get("rights", "") or ""
        _expect(isinstance(src, int) and src in nodes, "edge.src must reference a node nid")
        _expect(isinstance(dst, int) and dst in nodes, "edge.dst must reference a node nid")
        _expect(isinstance(etype, str), "edge.etype must be str")
        _expect(isinstance(rights, str), "edge.rights must be str")
        out.add(Edge(src=nodes[src], dst=nodes[dst], etype=etype, rights=rights))
    return out


def load_capg(path: Path) -> Set[Edge]:
    obj = _load_json(path)
    _expect(isinstance(obj, dict), "CH-CAPG root must be object")
    schema = obj.get("schema")
    _expect(isinstance(schema, str) and schema.startswith("CH-CAPG"), "missing/invalid 'schema' (expected CH-CAPG)")

    nodes = _to_nodes(obj)
    return _to_edges(obj, nodes)


def main(argv: Sequence[str]) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("before", type=Path)
    ap.add_argument("after", type=Path)
    ap.add_argument("--allow-added", action="append", default=[], help="regex for allowed added edges (repeatable)")
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args(argv)

    allow_re = [re.compile(p) for p in args.allow_added]

    before = load_capg(args.before)
    after = load_capg(args.after)

    added = sorted((after - before), key=lambda e: e.pretty())
    removed = sorted((before - after), key=lambda e: e.pretty())

    # Filter allowed added edges
    not_allowed: List[Edge] = []
    for e in added:
        s = e.pretty()
        if any(r.search(s) for r in allow_re):
            continue
        not_allowed.append(e)

    if not args.quiet:
        if removed:
            print("removed edges:")
            for e in removed:
                print("  -", e.pretty())
        if added:
            print("added edges:")
            for e in added:
                print("  +", e.pretty())

    if not_allowed:
        print("FAIL: unexpected new authority edges detected:")
        for e in not_allowed:
            print("  +", e.pretty())
        return 2

    if not args.quiet:
        print("OK: no unexpected new edges")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
