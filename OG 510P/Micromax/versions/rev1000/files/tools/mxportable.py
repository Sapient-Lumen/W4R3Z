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
    boot_stdlib_manifest_inventory,
    boot_stdlib_portability_manifest,
    selected_boot_stdlib_word_inventory,
    default_corpus_path,
    load_portability_cases,
    portability_case_record,
    portability_inventory,
    portability_result_record,
    portability_summary,
    run_portability_cases,
    select_boot_stdlib_manifest_entries,
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
            "words": list(args.word),
            "word_contains": str(args.word_contains or ""),
            "show_source": bool(args.show_source),
            "show_deps": bool(args.show_deps),
            "show_closure": bool(args.show_closure),
            "show_users": bool(args.show_users),
            "show_impact": bool(args.show_impact),
            "impact_words": list(args.impact_word),
            "impact_word_contains": str(args.impact_word_contains or ""),
            "impact_distances": [int(distance) for distance in args.impact_distance],
            "impact_categories": list(args.impact_category),
            "impact_tags": list(args.impact_tag),
            "impact_names": list(args.impact_name),
            "impact_name_contains": str(args.impact_name_contains or ""),
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


def _impact_group_paths_text(group: dict) -> str:
    parts: list[str] = []
    for raw_path in group.get("paths") or []:
        path = [str(tok) for tok in raw_path if str(tok)]
        if path:
            parts.append(" -> ".join(path))
    return " | ".join(parts) or "-"


def _name_count_text(rows: list[dict] | None) -> str:
    if not rows:
        return "-"
    return ", ".join(f"{row['name']}={row['count']}" for row in rows)


def _impact_filter_suffix(row: dict) -> str:
    suffix = str(row.get("filter_suffix") or "")
    if not suffix:
        return ""
    mode = str(row.get("family_mode") or "").strip()
    effective = str(row.get("effective_family_suffix") or "").strip()
    if mode == "append" and effective and effective != suffix:
        return f"{mode}:{suffix} => {effective}"
    if mode:
        return f"{mode}:{suffix}"
    return suffix


def _impact_filter_preview(row: dict) -> str:
    word_count = int(row.get("preview_impact_word_count") or 0)
    case_count = int(row.get("preview_impact_case_count") or 0)
    stage_count = int(row.get("preview_impact_stage_count") or 0)
    effect = str(row.get("preview_effect") or "").strip()
    word_delta = int(row.get("preview_impact_word_delta") or 0)
    case_delta = int(row.get("preview_impact_case_delta") or 0)
    stage_delta = int(row.get("preview_impact_stage_delta") or 0)
    parts: list[str] = []
    if effect and effect != 'narrower':
        parts.append(effect)
    if word_delta or case_delta or stage_delta:
        parts.append(f"delta:w{word_delta:+d},c{case_delta:+d},d{stage_delta:+d}")
    if word_count or case_count or stage_count:
        parts.append(f"result:w={word_count},c={case_count},d={stage_count}")
    return "; ".join(parts)


def _impact_filter_equivalents_text(row: dict) -> str:
    equivalents = list(row.get('equivalent_options') or [])
    if not equivalents:
        return ''
    parts = [
        f"{str(item.get('option_family') or '?')}:{str(item.get('option_label') or '-')}"
        for item in equivalents
    ]
    return 'same-result: ' + ', '.join(parts)


def _impact_filter_words_text(rows: list[dict] | None) -> str:
    if not rows:
        return "-"
    parts: list[str] = []
    for row in rows:
        text = f"{row['name']}@{int(row.get('distance') or 0)}={int(row.get('case_count') or 0)}"
        extras: list[str] = []
        suffix = _impact_filter_suffix(row)
        if suffix:
            extras.append(suffix)
        preview = _impact_filter_preview(row)
        if preview:
            extras.append(preview)
        equivalents = _impact_filter_equivalents_text(row)
        if equivalents:
            extras.append(equivalents)
        if extras:
            text += f" [{'; '.join(extras)}]"
        parts.append(text)
    return ", ".join(parts)


def _impact_filter_distances_text(rows: list[dict] | None) -> str:
    if not rows:
        return "-"
    parts: list[str] = []
    for row in rows:
        words = ",".join(row.get("words") or []) or "-"
        text = f"{int(row.get('distance') or 0)}(words={words},cases={int(row.get('case_count') or 0)})"
        extras: list[str] = []
        suffix = _impact_filter_suffix(row)
        if suffix:
            extras.append(suffix)
        preview = _impact_filter_preview(row)
        if preview:
            extras.append(preview)
        equivalents = _impact_filter_equivalents_text(row)
        if equivalents:
            extras.append(equivalents)
        if extras:
            text += f" [{'; '.join(extras)}]"
        parts.append(text)
    return ", ".join(parts)


def _impact_filter_name_counts_text(rows: list[dict] | None) -> str:
    if not rows:
        return "-"
    parts: list[str] = []
    for row in rows:
        text = f"{row['name']}={row['count']}"
        extras: list[str] = []
        suffix = _impact_filter_suffix(row)
        if suffix:
            extras.append(suffix)
        preview = _impact_filter_preview(row)
        if preview:
            extras.append(preview)
        equivalents = _impact_filter_equivalents_text(row)
        if equivalents:
            extras.append(equivalents)
        if extras:
            text += f" [{'; '.join(extras)}]"
        parts.append(text)
    return ", ".join(parts)


def _impact_filter_names_text(rows: list[dict] | None) -> str:
    if not rows:
        return "-"
    parts: list[str] = []
    for row in rows:
        words = ",".join(row.get("words") or []) or "-"
        distances = ",".join(str(int(distance)) for distance in (row.get("distances") or [])) or "-"
        text = f"{row['name']}[words={words};depths={distances}]"
        extras: list[str] = []
        suffix = _impact_filter_suffix(row)
        if suffix:
            extras.append(suffix)
        preview = _impact_filter_preview(row)
        if preview:
            extras.append(preview)
        equivalents = _impact_filter_equivalents_text(row)
        if equivalents:
            extras.append(equivalents)
        if extras:
            text += f" [{'; '.join(extras)}]"
        parts.append(text)
    return ", ".join(parts)


def _impact_filter_represented_alternatives_text(row: dict) -> str:
    alternatives = list(row.get('represented_alternatives') or [])
    if not alternatives:
        return ''
    parts: list[str] = []
    for item in alternatives:
        family = str(item.get('option_family') or '?')
        label = str(item.get('option_label') or '')
        parts.append(f"{family}:{label}" if label else family)
    return 'covers: ' + ', '.join(parts)


def _impact_filter_represented_ranks_text(row: dict) -> str:
    ranks = [int(rank) for rank in (row.get('represented_recommendation_ranks') or []) if int(rank) > 0]
    if not ranks:
        return ''
    joined = ','.join(str(rank) for rank in ranks)
    return 'full ranks: ' + joined


def _impact_filter_representative_reason_text(row: dict) -> str:
    reason = str(row.get('representative_reason') or '').strip()
    if not reason:
        return ''
    return 'why: ' + reason


def _impact_filter_option_text(family: str, row: dict) -> str:
    kind = str(family or '')
    if kind == 'words':
        return _impact_filter_words_text([row])
    if kind == 'distances':
        return _impact_filter_distances_text([row])
    if kind in {'tags', 'categories'}:
        return _impact_filter_name_counts_text([row])
    if kind == 'names':
        return _impact_filter_names_text([row])
    return str(row.get('name') or row.get('distance') or '-')


def _print_impact_filter_options(options: dict | None, *, indent: str) -> None:
    if not options:
        print(f"{indent}impact filter options: -")
        return
    print(f"{indent}impact filter options:")
    print(f"{indent}  words: {_impact_filter_words_text(options.get('words'))}")
    print(f"{indent}  distances: {_impact_filter_distances_text(options.get('distances'))}")
    print(f"{indent}  categories: {_impact_filter_name_counts_text(options.get('categories'))}")
    print(f"{indent}  tags: {_impact_filter_name_counts_text(options.get('tags'))}")
    print(f"{indent}  names: {_impact_filter_names_text(options.get('names'))}")
    primary = dict(options.get('recommended_primary') or {})
    if not primary:
        print(f"{indent}  recommended next: -")
    else:
        family = str(primary.get('option_family') or '?')
        text = _impact_filter_option_text(family, primary)
        covered = _impact_filter_represented_alternatives_text(primary)
        if covered:
            text += f" [{covered}]"
        ranks_text = _impact_filter_represented_ranks_text(primary)
        if ranks_text:
            text += f" [{ranks_text}]"
        reason = _impact_filter_representative_reason_text(primary)
        if reason:
            text += f" [{reason}]"
        print(f"{indent}  recommended next: {family}: {text}")
        print(f"{indent}    command: {primary.get('show_impact_command') or '-'}")
    recommended = list(options.get('recommended') or [])
    if not recommended:
        print(f"{indent}  recommended: -")
    else:
        print(f"{indent}  recommended:")
        for row in recommended:
            rank = int(row.get('recommendation_rank') or 0)
            family = str(row.get('option_family') or '?')
            print(f"{indent}    {rank}. {family}: {_impact_filter_option_text(family, row)}")
    recommended_distinct = list(options.get('recommended_distinct') or [])
    if not recommended_distinct:
        print(f"{indent}  recommended distinct: -")
    else:
        print(f"{indent}  recommended distinct:")
        for row in recommended_distinct:
            rank = int(row.get('recommendation_rank') or 0)
            family = str(row.get('option_family') or '?')
            text = _impact_filter_option_text(family, row)
            covered = _impact_filter_represented_alternatives_text(row)
            if covered:
                text += f" [{covered}]"
            ranks_text = _impact_filter_represented_ranks_text(row)
            if ranks_text:
                text += f" [{ranks_text}]"
            reason = _impact_filter_representative_reason_text(row)
            if reason:
                text += f" [{reason}]"
            print(f"{indent}    {rank}. {family}: {text}")
    groups = list(options.get('recommended_distinct_groups') or [])
    if not groups:
        print(f"{indent}  recommended distinct groups: -")
        return
    print(f"{indent}  recommended distinct groups:")
    for group in groups:
        rank = int(group.get('recommendation_rank') or 0)
        representative = dict(group.get('representative') or {})
        family = str(representative.get('option_family') or '?')
        label = str(representative.get('option_label') or '')
        header = f"{family}: {label}" if label else family
        print(f"{indent}    {rank}. {header}")
        alternatives = list(group.get('represented_alternatives') or [])
        if not alternatives:
            print(f"{indent}      alternatives: -")
        else:
            parts: list[str] = []
            for item in alternatives:
                alt_family = str(item.get('option_family') or '?')
                alt_label = str(item.get('option_label') or '')
                parts.append(f"{alt_family}:{alt_label}" if alt_label else alt_family)
            print(f"{indent}      alternatives: {', '.join(parts)}")
        ranks_text = _impact_filter_represented_ranks_text(group)
        print(f"{indent}      {ranks_text or 'full ranks: -'}")
        reason = str(group.get('representative_reason') or '').strip()
        print(f"{indent}      why: {reason or '-'}")


def _print_impact_groups(groups: list[dict], *, indent: str) -> None:
    if not groups:
        print(f"{indent}impact groups: -")
        return
    print(f"{indent}impact groups:")
    for group in groups:
        case_names = ", ".join(group.get("case_names") or []) or "-"
        print(f"{indent}  {group.get('word') or '-'} <= {_impact_group_paths_text(group)} :: {case_names}")
        print(f"{indent}    retest: {group.get('retest_command') or '-'}")


def _print_impact_stages(stages: list[dict], *, indent: str) -> None:
    if not stages:
        print(f"{indent}impact stages: -")
        return
    print(f"{indent}impact stages:")
    for stage in stages:
        words = ", ".join(stage.get("words") or []) or "-"
        case_names = ", ".join(stage.get("case_names") or []) or "-"
        print(f"{indent}  depth {int(stage.get('distance') or 0)}: {words} :: {case_names}")
        print(f"{indent}    retest: {stage.get('retest_command') or '-'}")


def _impact_filter_summary(args: argparse.Namespace) -> str:
    parts: list[str] = []
    if args.impact_word:
        parts.append(f"words={','.join(args.impact_word)}")
    if args.impact_word_contains:
        parts.append(f"word-contains={args.impact_word_contains}")
    if args.impact_distance:
        parts.append(
            "distances=" + ",".join(str(max(int(distance), 0)) for distance in args.impact_distance)
        )
    if args.impact_category:
        parts.append(f"categories={','.join(args.impact_category)}")
    if args.impact_tag:
        parts.append(f"tags={','.join(args.impact_tag)}")
    if args.impact_name:
        parts.append(f"names={','.join(args.impact_name)}")
    if args.impact_name_contains:
        parts.append(f"name-contains={args.impact_name_contains}")
    return " ".join(parts)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run the Micromax portability corpus")
    parser.add_argument("path", nargs="?", default=str(default_corpus_path()), help="path to a portability corpus JSON file")
    parser.add_argument("--category", action="append", default=[], help="limit execution to one or more categories (repeatable)")
    parser.add_argument("--tag", action="append", default=[], help="limit execution to cases containing all requested tags (repeatable)")
    parser.add_argument("--name", action="append", default=[], help="limit execution to exact case names (repeatable)")
    parser.add_argument("--name-contains", default="", help="limit execution to case names containing this substring")
    parser.add_argument("--list", action="store_true", help="list matching cases without running them")
    parser.add_argument("--inventory", action="store_true", help="show categories/tags/case names for matching cases without running them")
    parser.add_argument("--stdlib-manifest", action="store_true", help="show the boot-stdlib portability manifest instead of running or listing corpus cases")
    parser.add_argument("--word", action="append", default=[], help="limit --stdlib-manifest to one or more exact boot-stdlib words (repeatable)")
    parser.add_argument("--word-contains", default="", help="limit --stdlib-manifest to boot-stdlib words containing this substring")
    parser.add_argument("--show-source", action="store_true", help="include boot-stdlib source line, stack effect, and definition text in --stdlib-manifest output")
    parser.add_argument("--show-deps", action="store_true", help="include boot-stdlib body tokens and referenced words in --stdlib-manifest output")
    parser.add_argument("--show-closure", action="store_true", help="include transitive stdlib/kernel prerequisite metadata in --stdlib-manifest output")
    parser.add_argument("--show-users", action="store_true", help="include reverse stdlib usage metadata in --stdlib-manifest output")
    parser.add_argument("--show-impact", action="store_true", help="include impacted boot-stdlib words and portability cases to retest after changing a word")
    parser.add_argument("--impact-word", action="append", default=[], help="limit --show-impact slices to one or more exact impacted boot-stdlib words (repeatable)")
    parser.add_argument("--impact-word-contains", default="", help="limit --show-impact slices to impacted boot-stdlib words containing this substring")
    parser.add_argument("--impact-distance", action="append", default=[], type=int, help="limit --show-impact slices to one or more shortest-path distances (repeatable)")
    parser.add_argument("--impact-category", action="append", default=[], help="limit --show-impact case slices to one or more exact portability categories (repeatable)")
    parser.add_argument("--impact-tag", action="append", default=[], help="limit --show-impact case slices to portability cases containing all requested impact tags (repeatable)")
    parser.add_argument("--impact-name", action="append", default=[], help="limit --show-impact case slices to one or more exact portability case names (repeatable)")
    parser.add_argument("--impact-name-contains", default="", help="limit --show-impact case slices to portability case names containing this substring")
    parser.add_argument("--json", action="store_true", help="emit machine-readable JSON instead of human text")
    parser.add_argument("--quiet", action="store_true", help="when running cases, print only the final summary unless a case fails")
    args = parser.parse_args(argv)

    all_cases = load_portability_cases(args.path)
    cases = select_portability_cases(
        all_cases,
        categories=args.category,
        tags=args.tag,
        names=args.name,
        name_contains=args.name_contains,
    )

    if args.stdlib_manifest:
        manifest = select_boot_stdlib_manifest_entries(
            boot_stdlib_portability_manifest(),
            words=args.word,
            word_contains=args.word_contains,
        )
        inventory = boot_stdlib_manifest_inventory(cases, manifest)
        source_inventory = None
        source_rows: dict[str, dict] = {}
        if args.show_source or args.show_deps or args.show_closure or args.show_users or args.show_impact:
            source_inventory = selected_boot_stdlib_word_inventory(
                manifest=manifest,
                impact_manifest=boot_stdlib_portability_manifest(),
                cases=all_cases,
                words=args.word,
                word_contains=args.word_contains,
                impact_filter_words=args.impact_word,
                impact_word_contains=args.impact_word_contains,
                impact_distances=args.impact_distance,
                impact_case_categories=args.impact_category,
                impact_case_tags=args.impact_tag,
                impact_case_names=args.impact_name,
                impact_case_name_contains=args.impact_name_contains,
            )
            source_rows = {row["word"]: row for row in source_inventory["words"]}
        if args.json:
            payload = _json_payload(path=args.path, cases=cases, args=args)
            payload["manifest"] = inventory
            if source_inventory is not None:
                payload["source_inventory"] = source_inventory
            payload.pop("cases", None)
            print(json.dumps(payload, indent=2, sort_keys=True))
            return 0 if inventory["all_cases_present"] and (source_inventory is None or source_inventory["all_words_present"]) else 1

        impact_filter_text = _impact_filter_summary(args)
        if args.show_impact and impact_filter_text:
            print(f"impact filters: {impact_filter_text}\n")
        for row in inventory["words"]:
            mark = "ok" if row["covered"] else "MISS"
            case_list = ", ".join(row["case_names"])
            print(f"[{mark}] {row['word']}: {case_list}")
            if row["missing_case_names"]:
                print(f"      missing: {', '.join(row['missing_case_names'])}")
            if args.show_source or args.show_deps or args.show_closure or args.show_users or args.show_impact:
                source_row = source_rows.get(row["word"])
                if source_row is None:
                    print("      source: MISSING")
                else:
                    if args.show_source:
                        print(f"      source: {source_row['source_path']}:{source_row['line']} {source_row['stack_effect']}")
                        print(f"      def: {source_row['definition']}")
                    if args.show_deps:
                        if source_row.get("alias_of"):
                            print(f"      alias: {source_row['alias_of']}")
                        print(f"      refs: {', '.join(source_row['word_refs']) or '-'}")
                        print(f"      stdlib refs: {', '.join(source_row['stdlib_refs']) or '-'}")
                        print(f"      nonstdlib refs: {', '.join(source_row['nonstdlib_refs']) or '-'}")
                    if args.show_closure:
                        print(f"      dependency order: {', '.join(source_row['dependency_order']) or '-'}")
                        print(f"      transitive stdlib refs: {', '.join(source_row['transitive_stdlib_refs']) or '-'}")
                        print(f"      transitive nonstdlib refs: {', '.join(source_row['transitive_nonstdlib_refs']) or '-'}")
                        print(f"      stdlib depth: {source_row['stdlib_depth']}")
                    if args.show_users:
                        print(f"      direct stdlib users: {', '.join(source_row['direct_stdlib_users']) or '-'}")
                        print(f"      transitive stdlib users: {', '.join(source_row['transitive_stdlib_users']) or '-'}")
                        print(f"      user depth: {source_row['user_depth']}")
                    if args.show_impact:
                        print(f"      impact words: {', '.join(source_row['impact_words']) or '-'}")
                        print(f"      impact cases: {', '.join(source_row['impact_case_names']) or '-'}")
                        print(f"      show impact command: {source_row.get('show_impact_command') or '-'}")
                        print(f"      show impact json: {source_row.get('show_impact_json_command') or '-'}")
                        _print_impact_filter_options(source_row.get('impact_filter_options'), indent='      ')
                        _print_impact_groups(list(source_row.get('impact_groups') or []), indent='      ')
                        _print_impact_stages(list(source_row.get('impact_stages') or []), indent='      ')
                        print(f"      impact categories: {_name_count_text(source_row.get('impact_categories'))}")
                        print(f"      impact tags: {_name_count_text(source_row.get('impact_tags'))}")
                        print(f"      impact case count: {source_row['impact_case_count']}")
        if args.show_impact and source_inventory is not None:
            summary = source_inventory.get("impact_summary") or {}
            print("\nSelected impact summary:")
            if impact_filter_text:
                print(f"  impact filters: {impact_filter_text}")
            print(f"  impact words: {', '.join(summary.get('impact_words') or []) or '-'}")
            print(f"  impact cases: {', '.join(summary.get('impact_case_names') or []) or '-'}")
            print(f"  show impact command: {summary.get('show_impact_command') or '-'}")
            print(f"  show impact json: {summary.get('show_impact_json_command') or '-'}")
            _print_impact_filter_options(summary.get('impact_filter_options'), indent='  ')
            _print_impact_groups(list(summary.get('impact_groups') or []), indent='  ')
            _print_impact_stages(list(summary.get('impact_stages') or []), indent='  ')
            print(f"  impact categories: {_name_count_text(summary.get('impact_categories'))}")
            print(f"  impact tags: {_name_count_text(summary.get('impact_tags'))}")
            print(f"  impact case count: {int(summary.get('impact_case_count') or 0)}")
            print(f"  retest command: {summary.get('retest_command') or '-'}")
            print(f"  retest json: {summary.get('retest_json_command') or '-'}")
        if args.show_source and source_inventory and source_inventory["missing_words"]:
            print(f"      missing source rows: {', '.join(source_inventory['missing_words'])}")
        print(f"\n{inventory['word_count'] - len(inventory['missing_words'])}/{inventory['word_count']} boot stdlib words covered")
        return 0 if inventory["all_cases_present"] and (source_inventory is None or source_inventory["all_words_present"]) else 1

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

    if not args.quiet or failed:
        for res in results:
            mark = "ok" if res.ok else "FAIL"
            print(f"[{mark}] {res.name}")
            if res.detail:
                print(f"      {res.detail}")

    print(f"{len(results) - len(failed)}/{len(results)} portability cases passed")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
