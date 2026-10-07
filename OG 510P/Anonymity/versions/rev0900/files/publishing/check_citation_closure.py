#!/usr/bin/env python3
"""Audit static citation/reference closure for shipped paper.tex files.

This is intentionally static and source-only.  It does not attempt to compile
LaTeX; instead it verifies that every citation key used by a paper resolves to a
local ``\bibitem``/local bibliography entry and that local reference commands
resolve to labels in the same source file.  Release compilation remains a later,
selected-candidate preflight step.
"""

from __future__ import annotations

import argparse
import collections
import hashlib
import json
import pathlib
import re
import sys
from typing import Any

from release_preflight import (
    BIBITEM_RE,
    CITE_COMMAND_RE,
    citation_and_reference_closure,
    collect_bib_keys,
    split_keys,
    strip_tex_comments,
)


def sha256_file(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load_json(path: pathlib.Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))




MALFORMED_BIB_COMMAND_RE = re.compile(r"(?m)^\s*(ibitem|ewblock)\b")


def malformed_bibliography_commands(text: str) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    for line_no, line in enumerate(text.splitlines(), 1):
        match = MALFORMED_BIB_COMMAND_RE.match(line)
        if match:
            findings.append({"line": line_no, "command_fragment": match.group(1), "text": line.strip()[:160]})
    return findings


def paper_paths(root: pathlib.Path) -> list[pathlib.Path]:
    paths = list(root.glob("series/**/paper.tex")) + list(root.glob("published/**/paper.tex"))
    return sorted({p.resolve() for p in paths})


def queue_state_map(root: pathlib.Path) -> dict[str, list[str]]:
    queue_path = root / "release_queue" / "QUEUE_INDEX.json"
    if not queue_path.exists():
        return {}
    queue = load_json(queue_path)
    out: dict[str, list[str]] = collections.defaultdict(list)
    for state, items in queue.get("states", {}).items():
        for item in items if isinstance(items, list) else []:
            if isinstance(item, dict) and item.get("source_tex"):
                out[str(item["source_tex"])].append(str(state))
    return {key: sorted(set(values)) for key, values in out.items()}


def global_graph(root: pathlib.Path, papers: list[pathlib.Path]) -> dict[str, Any]:
    bibitem_occurrences: dict[str, list[str]] = collections.defaultdict(list)
    citation_occurrences: dict[str, list[str]] = collections.defaultdict(list)
    malformed_by_source: dict[str, list[dict[str, Any]]] = {}
    for path in papers:
        rel = path.relative_to(root).as_posix()
        text = path.read_text(encoding="utf-8", errors="replace")
        clean = strip_tex_comments(text)
        malformed = malformed_bibliography_commands(text)
        if malformed:
            malformed_by_source[rel] = malformed[:20]
        local_bib_keys, _ = collect_bib_keys(path, clean)
        for key in local_bib_keys:
            bibitem_occurrences[key].append(rel)
        for raw in CITE_COMMAND_RE.findall(clean):
            for key in split_keys(raw):
                citation_occurrences[key].append(rel)

    globally_undefined = sorted(key for key in citation_occurrences if key not in bibitem_occurrences)
    duplicate_bibitems = {
        key: sorted(paths)
        for key, paths in sorted(bibitem_occurrences.items())
        if len(set(paths)) > 1
    }
    return {
        "citation_key_count": len(citation_occurrences),
        "bibliography_key_count": len(bibitem_occurrences),
        "globally_undefined_citation_count": len(globally_undefined),
        "globally_undefined_citations": globally_undefined,
        "duplicate_bibitem_key_count": len(duplicate_bibitems),
        "malformed_bibliography_command_file_count": len(malformed_by_source),
        "malformed_bibliography_command_count": sum(len(v) for v in malformed_by_source.values()),
        "malformed_bibliography_command_sources": [
            {"path": path, "findings": findings}
            for path, findings in sorted(malformed_by_source.items())[:40]
        ],
        "duplicate_bibitem_keys_sample": [
            {"key": key, "paths": paths[:8], "path_count": len(paths)}
            for key, paths in list(duplicate_bibitems.items())[:40]
        ],
        "note": "Duplicate bibitem keys across separate standalone paper sources are expected in this source-only archive; local closure is the publication blocker.",
    }


def check(root: pathlib.Path) -> dict[str, Any]:
    release_manifest = load_json(root / "RELEASE_MANIFEST.json")
    qstates = queue_state_map(root)
    papers = paper_paths(root)
    entries = []
    blocker_counter: collections.Counter[str] = collections.Counter()

    for path in papers:
        rel = path.relative_to(root).as_posix()
        text = path.read_text(encoding="utf-8", errors="replace")
        closure = citation_and_reference_closure(path, text)
        malformed = malformed_bibliography_commands(text)
        blockers = []
        if closure["missing_bibliography_files"]:
            blockers.append({"category": "missing_bibliography_files", "detail": closure["missing_bibliography_files"]})
        if closure["undefined_citations"]:
            blockers.append({"category": "undefined_citations", "count": len(closure["undefined_citations"]), "detail": closure["undefined_citations"][:60]})
        if closure["undefined_references"]:
            blockers.append({"category": "undefined_references", "count": len(closure["undefined_references"]), "detail": closure["undefined_references"][:60]})
        if malformed:
            blockers.append({"category": "malformed_bibliography_commands", "count": len(malformed), "detail": malformed[:20]})
        for blocker in blockers:
            blocker_counter[str(blocker["category"])] += 1
        entries.append({
            "path": rel,
            "sha256": sha256_file(path),
            "queue_states": qstates.get(rel, []),
            "status": "pass" if not blockers else "fail",
            "blocker_count": len(blockers),
            "blockers": blockers,
            "citation_key_count": closure["citation_key_count"],
            "bibliography_key_count": closure["bibliography_key_count"],
            "reference_key_count": closure["reference_key_count"],
            "label_count": closure["label_count"],
            "malformed_bibliography_command_count": len(malformed),
        })

    graph = global_graph(root, papers)
    failed = [entry for entry in entries if entry["status"] != "pass"]
    global_failure = graph["globally_undefined_citation_count"] != 0 or graph.get("malformed_bibliography_command_count", 0) != 0
    return {
        "status": "pass" if not failed and not global_failure else "fail",
        "generated_for_revision": release_manifest["revision"],
        "checked_bundle": release_manifest["bundle"],
        "publication_authorized": False,
        "scope": "series/**/paper.tex plus published/**/paper.tex",
        "paper_count": len(entries),
        "papers": entries,
        "global_citation_graph": graph,
        "summary": {
            "papers_checked": len(entries),
            "papers_passed": len(entries) - len(failed),
            "papers_failed": len(failed),
            "blocker_category_counts": dict(sorted(blocker_counter.items())),
            "globally_undefined_citation_count": graph["globally_undefined_citation_count"],
            "malformed_bibliography_command_count": graph.get("malformed_bibliography_command_count", 0),
            "malformed_bibliography_command_file_count": graph.get("malformed_bibliography_command_file_count", 0),
        },
        "fail_closed_rule": "A paper with unresolved local citations/references or malformed bibliography command fragments is not freeze-ready. A global citation miss is an archive repair blocker even if no paper is published in the current turn.",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--write-report", default="")
    args = parser.parse_args()

    root = pathlib.Path(args.root).resolve()
    report = check(root)
    text = json.dumps(report, indent=2) + "\n"
    if args.write_report:
        out = root / args.write_report
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text, encoding="utf-8")
    sys.stdout.write(text)
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
