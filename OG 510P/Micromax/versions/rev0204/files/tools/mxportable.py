#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from micromax.portability_suite import (  # noqa: E402
    default_corpus_path,
    load_portability_cases,
    portability_case_record,
    portability_inventory,
    portability_result_record,
    portability_summary,
    run_portability_cases,
    select_portability_cases,
)


def _json_payload(*, path: str, cases: list[dict], args: argparse.Namespace, results: list | None = None) -> dict:
    payload = {
        "path": path,
        "filters": {
            "categories": list(args.category),
            "tags": list(args.tag),
            "names": list(args.name),
            "name_contains": str(args.name_contains or ""),
        },
        "summary": portability_summary(cases),
    }
    if results is None:
        payload["cases"] = [portability_case_record(case) for case in cases]
        return payload

    result_rows = [portability_result_record(case, result) for case, result in zip(cases, results)]
    failed = [row for row in result_rows if not row["ok"]]
    payload.update(
        {
            "passed": len(result_rows) - len(failed),
            "failed": len(failed),
            "results": result_rows,
        }
    )
    return payload


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run the Micromax portability corpus")
    parser.add_argument(
        "path",
        nargs="?",
        default=str(default_corpus_path()),
        help="path to a portability corpus JSON file",
    )
    parser.add_argument(
        "--category",
        action="append",
        default=[],
        help="limit execution to one or more categories (repeatable)",
    )
    parser.add_argument(
        "--tag",
        action="append",
        default=[],
        help="limit execution to cases containing all requested tags (repeatable)",
    )
    parser.add_argument(
        "--name",
        action="append",
        default=[],
        help="limit execution to exact case names (repeatable)",
    )
    parser.add_argument(
        "--name-contains",
        default="",
        help="limit execution to case names containing this substring",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="list matching cases without running them",
    )
    parser.add_argument(
        "--inventory",
        action="store_true",
        help="show categories/tags/case names for matching cases without running them",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="emit machine-readable JSON instead of human text",
    )
    args = parser.parse_args(argv)

    cases = load_portability_cases(args.path)
    cases = select_portability_cases(
        cases,
        categories=args.category,
        tags=args.tag,
        names=args.name,
        name_contains=args.name_contains,
    )

    if args.list or args.inventory:
        if args.json:
            payload = _json_payload(path=args.path, cases=cases, args=args)
            if args.inventory:
                payload["inventory"] = portability_inventory(cases)
                payload.pop("cases", None)
            print(json.dumps(payload, indent=2, sort_keys=True))
            return 0
        if args.inventory:
            inventory = portability_inventory(cases)
            print("Categories:")
            for row in inventory["categories"]:
                print(f"- {row['name']}: {row['count']}")
            print("\nTags:")
            for row in inventory["tags"]:
                print(f"- {row['name']}: {row['count']}")
            print("\nCase names:")
            for name in inventory["case_names"]:
                print(f"- {name}")
            print(f"\n{inventory['count']} matching portability cases")
            return 0
        for case in cases:
            tags = list(case.get("tags") or [])
            extra = f" tags={','.join(tags)}" if tags else ""
            print(f"[{case['category']}] {case['name']}{extra}")
        print(f"\n{len(cases)} matching portability cases")
        return 0

    results = run_portability_cases(cases)
    failed = [r for r in results if not r.ok]

    if args.json:
        print(json.dumps(_json_payload(path=args.path, cases=cases, args=args, results=results), indent=2, sort_keys=True))
        return 0 if not failed else 1

    for res in results:
        mark = "ok" if res.ok else "FAIL"
        print(f"[{mark}] {res.name}")
        if res.detail:
            print(f"      {res.detail}")

    print(f"\n{len(results) - len(failed)}/{len(results)} portability cases passed")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
