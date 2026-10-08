#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import sys
from collections import Counter, defaultdict
from functools import lru_cache
from pathlib import Path

PUBLIC_PATTERNS: list[tuple[str, str]] = [
    ("fn", r"^\s*pub(?:\([^)]*\))?\s+fn\s+([A-Za-z0-9_]+)"),
    ("struct", r"^\s*pub\s+struct\s+([A-Za-z0-9_]+)"),
    ("enum", r"^\s*pub\s+enum\s+([A-Za-z0-9_]+)"),
    ("trait", r"^\s*pub\s+trait\s+([A-Za-z0-9_]+)"),
    ("type", r"^\s*pub\s+type\s+([A-Za-z0-9_]+)"),
    ("const", r"^\s*pub\s+const\s+([A-Za-z0-9_]+)"),
]
USE_RE = re.compile(r"^\s*use\s+crate::([A-Za-z0-9_]+)", flags=re.MULTILINE)
TEST_RE = re.compile(r"#\[test\]")
PROPTEST_RE = re.compile(r"proptest!")


class ModuleInfo(dict):
    pass


def extract_public_items(text: str) -> list[dict[str, str]]:
    items: list[dict[str, str]] = []
    for kind, pattern in PUBLIC_PATTERNS:
        for match in re.finditer(pattern, text, flags=re.MULTILINE):
            items.append({"kind": kind, "name": match.group(1)})
    items.sort(key=lambda row: (row["kind"], row["name"]))
    return items


def tarjan_scc(graph: dict[str, set[str]]) -> list[list[str]]:
    index = 0
    stack: list[str] = []
    on_stack: set[str] = set()
    indices: dict[str, int] = {}
    lowlinks: dict[str, int] = {}
    components: list[list[str]] = []

    sys.setrecursionlimit(10000)

    def visit(node: str) -> None:
        nonlocal index
        indices[node] = index
        lowlinks[node] = index
        index += 1
        stack.append(node)
        on_stack.add(node)

        for dep in sorted(graph[node]):
            if dep not in graph:
                continue
            if dep not in indices:
                visit(dep)
                lowlinks[node] = min(lowlinks[node], lowlinks[dep])
            elif dep in on_stack:
                lowlinks[node] = min(lowlinks[node], indices[dep])

        if lowlinks[node] == indices[node]:
            component: list[str] = []
            while True:
                popped = stack.pop()
                on_stack.remove(popped)
                component.append(popped)
                if popped == node:
                    break
            components.append(sorted(component))

    for node in sorted(graph):
        if node not in indices:
            visit(node)

    return components


def collect(root: Path) -> dict[str, object]:
    src_dir = root / "crates" / "gr_engine" / "src"
    tests_dir = root / "crates" / "gr_engine" / "tests"

    src_files = sorted(src_dir.glob("*.rs"))
    test_files = sorted(tests_dir.glob("*.rs"))

    modules: dict[str, ModuleInfo] = {}
    graph: dict[str, set[str]] = {}
    inbound = Counter()
    public_kind_counts = Counter()

    for path in src_files:
        text = path.read_text(encoding="utf-8")
        module = path.stem
        deps = {dep for dep in USE_RE.findall(text) if dep != module}
        items = extract_public_items(text)
        for item in items:
            public_kind_counts[item["kind"]] += 1
        test_count = len(TEST_RE.findall(text))
        proptest_macro_count = len(PROPTEST_RE.findall(text))
        info: ModuleInfo = ModuleInfo(
            module=module,
            path=path.relative_to(root).as_posix(),
            lines=text.count("\n") + 1,
            public_items=items,
            public_item_count=len(items),
            outbound_deps=sorted(deps),
            outbound_dep_count=len(deps),
            inline_test_count=test_count,
            proptest_macro_count=proptest_macro_count,
        )
        modules[module] = info
        graph[module] = deps

    for module, deps in graph.items():
        for dep in deps:
            if dep in graph:
                inbound[dep] += 1

    module_test_counts = Counter()
    external_test_total = 0
    for path in test_files:
        text = path.read_text(encoding="utf-8")
        count = len(TEST_RE.findall(text))
        external_test_total += count
        stem = path.stem
        module_key = stem
        if stem.endswith("_suite"):
            module_key = stem
        elif stem.endswith("_run"):
            module_key = stem.rsplit("_", 1)[0]
        elif stem.endswith("_spec"):
            module_key = stem.rsplit("_", 1)[0]
        module_test_counts[module_key] += count

    for module, info in modules.items():
        info["inbound_ref_count"] = inbound[module]
        info["external_test_count"] = module_test_counts[module]
        info["total_test_coverage_count"] = info["inline_test_count"] + info["external_test_count"]

    components = tarjan_scc(graph)
    component_index = {module: i for i, comp in enumerate(components) for module in comp}
    component_deps: dict[int, set[int]] = defaultdict(set)
    for module, deps in graph.items():
        src_idx = component_index[module]
        for dep in deps:
            if dep not in component_index:
                continue
            dst_idx = component_index[dep]
            if src_idx != dst_idx:
                component_deps[src_idx].add(dst_idx)

    @lru_cache(maxsize=None)
    def depth(idx: int) -> int:
        if not component_deps[idx]:
            return 0
        return 1 + max(depth(dep) for dep in component_deps[idx])

    reading_waves = []
    for idx, comp in sorted(enumerate(components), key=lambda item: (depth(item[0]), item[1])):
        reading_waves.append(
            {
                "wave": depth(idx),
                "modules": comp,
                "depends_on": [components[dep] for dep in sorted(component_deps[idx], key=lambda n: components[n])],
            }
        )

    hotspots = []
    for info in sorted(modules.values(), key=lambda row: (-row["lines"], -row["inbound_ref_count"], row["module"])):
        hotspots.append(
            {
                "module": info["module"],
                "path": info["path"],
                "lines": info["lines"],
                "public_item_count": info["public_item_count"],
                "inbound_ref_count": info["inbound_ref_count"],
                "outbound_dep_count": info["outbound_dep_count"],
                "total_test_coverage_count": info["total_test_coverage_count"],
            }
        )

    inventory = {
        "inventory_version": "2026-03-22.rust_surface_inventory.v1",
        "scope": {
            "crate": "gr_engine",
            "src_glob": "crates/gr_engine/src/*.rs",
            "test_glob": "crates/gr_engine/tests/*.rs",
            "method": "static_regex_scan",
            "limitations": [
                "This inventory is source-text based and does not invoke rustc, cargo, macro expansion, or type checking.",
                "Dependency edges are extracted only from `use crate::...` statements in src files.",
                "Public-item counts are approximations from regex patterns and may undercount macro-generated or re-exported surfaces.",
            ],
        },
        "summary": {
            "src_module_count": len(src_files),
            "test_file_count": len(test_files),
            "public_item_count": sum(info["public_item_count"] for info in modules.values()),
            "public_item_kind_counts": dict(sorted(public_kind_counts.items())),
            "inline_test_count": sum(info["inline_test_count"] for info in modules.values()),
            "external_test_count": external_test_total,
            "total_test_count": sum(info["inline_test_count"] for info in modules.values()) + external_test_total,
            "largest_strongly_connected_component": max((len(comp) for comp in components), default=0),
        },
        "reading_waves": reading_waves,
        "hotspots": hotspots,
        "modules": [modules[name] for name in sorted(modules)],
    }
    return inventory


def render_markdown(inventory: dict[str, object]) -> str:
    summary = inventory["summary"]
    modules = inventory["modules"]
    reading_waves = inventory["reading_waves"]
    hotspots = inventory["hotspots"]

    lines = [
        "# Rust Surface Inventory",
        "",
        "Generated by `scripts/report/build_rust_surface_inventory.py`. This is a static source-text inventory for Rust-blocked sessions; it does not replace `cargo` / `rustc` execution.",
        "",
        "## Snapshot",
        "",
        f"- crate: `gr_engine`",
        f"- src_modules: {summary['src_module_count']}",
        f"- test_files: {summary['test_file_count']}",
        f"- public_items: {summary['public_item_count']}",
        f"- rust_tests_seen: {summary['total_test_count']} (`{summary['inline_test_count']}` inline + `{summary['external_test_count']}` external)",
        f"- largest_strongly_connected_component: {summary['largest_strongly_connected_component']}",
        "",
        "Public item kinds:",
        "",
    ]
    for kind, count in summary["public_item_kind_counts"].items():
        lines.append(f"- `{kind}`: {count}")

    lines.extend(
        [
            "",
            "## Suggested reading waves",
            "",
            "These waves follow static crate dependencies. Lower waves are the least dependent surfaces and are the best starting points when the Rust toolchain is unavailable.",
            "",
            "| wave | modules | why start here |",
            "|---:|---|---|",
        ]
    )
    for row in reading_waves:
        modules_text = ", ".join(f"`{name}`" for name in row["modules"])
        if row["depends_on"]:
            deps_text = "; depends on " + "; ".join(
                ", ".join(f"`{name}`" for name in dep_group) for dep_group in row["depends_on"]
            )
        else:
            deps_text = "; foundation/no internal deps"
        lines.append(f"| {row['wave']} | {modules_text} | static dependency wave{deps_text} |")

    lines.extend(
        [
            "",
            "## Highest-leverage modules",
            "",
            "Sorted by source size, then by inbound references. These are the most likely places where a future Rust-capable pass will matter most.",
            "",
            "| module | loc | public items | inbound refs | outbound refs | tests seen |",
            "|---|---:|---:|---:|---:|---:|",
        ]
    )
    for row in hotspots[:10]:
        lines.append(
            f"| `{row['module']}` | {row['lines']} | {row['public_item_count']} | {row['inbound_ref_count']} | {row['outbound_dep_count']} | {row['total_test_coverage_count']} |"
        )

    lines.extend(
        [
            "",
            "## Module inventory",
            "",
            "| module | path | loc | public items | outbound deps | inbound refs | tests seen | notable public symbols |",
            "|---|---|---:|---:|---|---:|---:|---|",
        ]
    )
    for row in modules:
        symbols = ", ".join(
            f"`{item['kind']} {item['name']}`" for item in row["public_items"][:6]
        )
        if row["public_item_count"] > 6:
            symbols += ", …"
        deps = ", ".join(f"`{dep}`" for dep in row["outbound_deps"]) if row["outbound_deps"] else ""
        lines.append(
            f"| `{row['module']}` | `{row['path']}` | {row['lines']} | {row['public_item_count']} | {deps} | {row['inbound_ref_count']} | {row['total_test_coverage_count']} | {symbols} |"
        )

    lines.extend(
        [
            "",
            "## Practical interpretation for Rust-blocked sessions",
            "",
            "1. Start with `spec`, `artifact`, and `sim` if the goal is to understand simulation truth and state semantics.",
            "2. Move next to the large central cycle (`probe`, `snapshot`, `scorecard`, `run_snapshot`, `metamorphic`, `scorecard_suite`) if the goal is orchestration/report coupling.",
            "3. Leave `*diff` modules and `snapshotrun_diff` for later unless the task is archive comparison or regression reporting.",
            "4. Treat this file as a navigation aid only; runtime truth still belongs to the Rust lane once `cargo` / `junest` are available again.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    write = "--write" in sys.argv
    root = Path(__file__).resolve().parents[2]
    inventory = collect(root)

    out_json = root / "artifacts" / "reports" / "rust_surface_inventory.json"
    out_md = root / "docs" / "RUST_SURFACE_INVENTORY.md"
    out_json.parent.mkdir(parents=True, exist_ok=True)

    out_json.write_text(json.dumps(inventory, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    expected = render_markdown(inventory)

    if write or not out_md.exists():
        out_md.write_text(expected, encoding="utf-8")
        print(f"rust-surface-inventory: wrote {out_md}")
        print(f"rust-surface-inventory: wrote {out_json}")
        return 0

    current = out_md.read_text(encoding="utf-8")
    if current != expected:
        print("rust-surface-inventory: drift detected; run with --write", file=sys.stderr)
        return 1

    print(f"rust-surface-inventory: ok ({inventory['summary']['src_module_count']} modules)")
    print(f"rust-surface-inventory: wrote {out_json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
