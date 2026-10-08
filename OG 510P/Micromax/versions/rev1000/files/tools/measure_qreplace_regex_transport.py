#!/usr/bin/env python3
"""Measure regex query-replace source transport at the real editor boundary.

The rev0998 reference joins the immutable line snapshot into one parent ``str``
and then sends that complete value through the worker's JSON/stdin protocol.  The
product case enters ordinary rev0999 query-replace, which stages bounded canonical
chunks in a private temporary file and sends only a small exactness descriptor.

Each sample runs in a fresh supervisor-owned Python process.  Source and Editor
construction finish before a READY/GO barrier and before ``tracemalloc`` starts.
On Linux, the supervisor also polls the complete process tree's RSS while the
operation runs.  When cgroup v2 ``memory.current`` is readable, it records that
noisy container-wide context as well; unlike RSS, that includes charged page
cache from the temporary source file.

Examples:
  PYTHONPATH=src python tools/measure_qreplace_regex_transport.py
  PYTHONPATH=src python tools/measure_qreplace_regex_transport.py --chars 33554432
  PYTHONPATH=src python tools/measure_qreplace_regex_transport.py --json-out report.json
"""

from __future__ import annotations

import argparse
import gc
import json
import os
try:
    import resource
except ImportError:  # pragma: no cover - resource is Unix-only
    resource = None  # type: ignore[assignment]
import statistics
import subprocess
import sys
import tempfile
import time
import tracemalloc
from pathlib import Path
from collections.abc import Sequence
from typing import Any, Callable

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = "micromax.qreplace-regex-transport-measurement.v1"
TOKEN = "needle-42"
PATTERN = r"needle-([0-9]+)"
REPLACEMENT = r"value-$1"
_DYNAMIC_METRICS = (
    "elapsed_seconds",
    "traced_current_bytes",
    "traced_peak_bytes",
    "parent_ru_maxrss_before_bytes",
    "parent_ru_maxrss_after_bytes",
    "child_ru_maxrss_bytes",
    "protocol_request_bytes",
    "parent_rss_baseline_bytes",
    "parent_rss_peak_bytes",
    "parent_rss_incremental_peak_bytes",
    "descendant_rss_peak_bytes",
    "process_tree_rss_peak_bytes",
    "process_tree_rss_incremental_peak_bytes",
    "cgroup_memory_baseline_bytes",
    "cgroup_memory_peak_bytes",
    "cgroup_memory_incremental_peak_bytes",
)


def _source(*, chars: int, line_chars: int) -> str:
    width = max(len(TOKEN) + 2, int(line_chars))
    target = max(width, int(chars))
    line_count = max(1, (target + width) // (width + 1))
    lines = ["a" * width for _ in range(line_count)]
    middle = line_count // 2
    token_at = max(0, (width - len(TOKEN)) // 2)
    lines[middle] = (
        ("a" * token_at)
        + TOKEN
        + ("a" * (width - token_at - len(TOKEN)))
    )
    return "\n".join(lines)


def _ru_maxrss_bytes(*, children: bool) -> int | None:
    if resource is None:
        return None
    who = resource.RUSAGE_CHILDREN if children else resource.RUSAGE_SELF
    value = int(resource.getrusage(who).ru_maxrss)
    # Linux and the BSDs report KiB; macOS reports bytes.
    return value if sys.platform == "darwin" else value * 1024


def _legacy_flat_regex_scan(
    lines: Sequence[str],
    search: str,
    value: str,
    **kwargs: object,
) -> object:
    """Reproduce the rev0998 query-replace source/protocol shape."""

    from micromax_editor.replace_plan import scan_replacement_edits

    kwargs.pop("line_starts", None)
    kwargs.pop("chunk_chars", None)
    source = "\n".join(lines)
    return scan_replacement_edits(
        source,
        search,
        value,
        literal=False,
        **kwargs,
    )


def _run_case(*, case: str, chars: int, line_chars: int) -> dict[str, Any]:
    import micromax.regex_runtime as regex_runtime
    import micromax_editor.editor as editor_module
    from micromax_editor.editor import Editor

    if case == "reference":
        editor_module.scan_regex_replacement_edits_lines = (  # type: ignore[assignment]
            _legacy_flat_regex_scan
        )
    elif case != "product":
        raise ValueError(f"unknown measurement case: {case}")

    source = _source(chars=chars, line_chars=line_chars)
    document_chars = len(source)
    line_count = source.count("\n") + 1
    editor = Editor()
    editor.new_buffer("*regex-transport-measurement*", source)
    editor.cur().buf.fastdirty = True
    # This is a transport-memory witness, not a 250 ms foreground-deadline
    # benchmark. Keep the killable boundary finite while avoiding scheduler or
    # source-transfer noise at larger evidence sizes.
    editor.search_regex_timeout_seconds = 5.0
    del source
    gc.collect()

    observed: dict[str, object] = {}
    original_worker = regex_runtime._run_stdlib_subprocess_worker

    def observed_worker(
        request: dict[str, object],
        *,
        timeout: float,
        startup_timeout: float,
        max_result_bytes: int,
    ) -> dict[str, object]:
        encoded = json.dumps(
            request,
            ensure_ascii=False,
            separators=(",", ":"),
        ).encode("utf-8")
        descriptor = request.get("haystack_file")
        encoded_size = len(encoded)
        del encoded
        observed.update(
            {
                "protocol_request_bytes": encoded_size,
                "request_contains_haystack": "haystack" in request,
                "request_contains_file_transport": isinstance(descriptor, dict),
                "staged_source_bytes": (
                    int(descriptor.get("bytes", 0))
                    if isinstance(descriptor, dict)
                    else 0
                ),
                "staged_source_characters": (
                    int(descriptor.get("characters", 0))
                    if isinstance(descriptor, dict)
                    else 0
                ),
            }
        )
        return original_worker(
            request,
            timeout=timeout,
            startup_timeout=startup_timeout,
            max_result_bytes=max_result_bytes,
        )

    regex_runtime._run_stdlib_subprocess_worker = observed_worker

    print("READY", flush=True)
    if sys.stdin.readline().strip() != "GO":
        raise RuntimeError("measurement supervisor did not release case")

    parent_ru_before = _ru_maxrss_bytes(children=False)
    tracemalloc.start()
    tracemalloc.reset_peak()
    started = time.perf_counter()
    ok = editor.begin_query_replace(PATTERN, REPLACEMENT, literal=False)
    elapsed = time.perf_counter() - started
    gc.collect()
    traced_current, traced_peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    parent_ru_after = _ru_maxrss_bytes(children=False)
    child_ru = _ru_maxrss_bytes(children=True)

    session = editor.qreplace
    if not ok or session is None or len(session.planned_matches) != 1:
        raise RuntimeError("regex query-replace did not produce exactly one plan row")
    edit = session.planned_matches[0]
    temp_root = Path(tempfile.gettempdir())
    residue = sorted(path.name for path in temp_root.glob("micromax-regex-*"))
    return {
        "case": case,
        "document_chars": document_chars,
        "line_count": line_count,
        "elapsed_seconds": float(elapsed),
        "traced_current_bytes": int(traced_current),
        "traced_peak_bytes": int(traced_peak),
        "parent_ru_maxrss_before_bytes": parent_ru_before,
        "parent_ru_maxrss_after_bytes": parent_ru_after,
        "child_ru_maxrss_bytes": child_ru,
        "protocol_request_bytes": int(observed.get("protocol_request_bytes", 0)),
        "request_contains_haystack": bool(observed.get("request_contains_haystack")),
        "request_contains_file_transport": bool(
            observed.get("request_contains_file_transport")
        ),
        "staged_source_bytes": int(observed.get("staged_source_bytes", 0)),
        "staged_source_characters": int(
            observed.get("staged_source_characters", 0)
        ),
        "plan_rows": [[int(edit.start), int(edit.end), str(edit.new)]],
        "match_old": str(session.match_old),
        "match_replacement": str(session.match_repl),
        "temporary_transport_residue": residue,
    }


def _rss_bytes(pid: int) -> int | None:
    status = Path(f"/proc/{int(pid)}/status")
    try:
        for line in status.read_text(encoding="ascii", errors="replace").splitlines():
            if line.startswith("VmRSS:"):
                return int(line.split()[1]) * 1024
    except (OSError, ValueError, IndexError):
        return None
    return None


def _linux_parent_map() -> dict[int, set[int]]:
    """Return one /proc snapshot keyed by parent PID.

    Some container procfs mounts omit ``task/*/children``. Parsing the stable
    parent field from ``/proc/<pid>/stat`` keeps the measurement stdlib-only and
    also sees children created by Micromax's temporary Popen starter thread.
    """

    parents: dict[int, set[int]] = {}
    proc_root = Path("/proc")
    try:
        entries = tuple(proc_root.iterdir())
    except OSError:
        return parents
    for entry in entries:
        if not entry.name.isdigit():
            continue
        try:
            stat_text = (entry / "stat").read_text(encoding="ascii")
            suffix = stat_text.rsplit(")", 1)[1].split()
            parent = int(suffix[1])
            child = int(entry.name)
        except (OSError, ValueError, IndexError):
            continue
        parents.setdefault(parent, set()).add(child)
    return parents


def _descendants(pid: int) -> set[int]:
    parents = _linux_parent_map()
    found: set[int] = set()
    pending = [int(pid)]
    while pending:
        parent = pending.pop()
        for child in parents.get(parent, ()):
            if child not in found:
                found.add(child)
                pending.append(child)
    return found


def _cgroup_memory_reader() -> tuple[str | None, Callable[[], int | None]]:
    candidates = (
        Path("/sys/fs/cgroup/memory.current"),
        Path("/sys/fs/cgroup/memory/memory.usage_in_bytes"),
    )
    for path in candidates:
        if path.is_file():
            def read(path: Path = path) -> int | None:
                try:
                    return int(path.read_text(encoding="ascii").strip())
                except (OSError, ValueError):
                    return None

            return str(path), read
    return None, lambda: None


def _terminate_case(process: subprocess.Popen[str]) -> None:
    try:
        if os.name == "posix":
            os.killpg(process.pid, 9)
        else:
            process.kill()
    except (OSError, ProcessLookupError):
        pass
    try:
        process.communicate(timeout=2.0)
    except (OSError, subprocess.TimeoutExpired):
        pass


def _supervised_case(
    *,
    case: str,
    chars: int,
    line_chars: int,
    deadline_seconds: float = 45.0,
) -> dict[str, Any]:
    with tempfile.TemporaryDirectory(prefix="micromax-regex-measure-") as temp_root:
        environment = dict(os.environ)
        environment.update(
            {
                "TMPDIR": temp_root,
                "TEMP": temp_root,
                "TMP": temp_root,
                "PYTHONHASHSEED": "0",
                "OPENBLAS_NUM_THREADS": "1",
                "OMP_NUM_THREADS": "1",
                "MKL_NUM_THREADS": "1",
                "NUMEXPR_NUM_THREADS": "1",
            }
        )
        process = subprocess.Popen(
            [
                sys.executable,
                str(Path(__file__).resolve()),
                "--case",
                case,
                "--chars",
                str(int(chars)),
                "--line-chars",
                str(int(line_chars)),
            ],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            env=environment,
            start_new_session=(os.name == "posix"),
        )
        assert process.stdout is not None
        assert process.stdin is not None
        ready = process.stdout.readline().strip()
        if ready != "READY":
            stdout, stderr = process.communicate(timeout=5.0)
            raise RuntimeError(
                f"{case} measurement did not become ready: {ready!r} "
                f"stdout={stdout!r} stderr={stderr!r}"
            )

        parent_baseline = _rss_bytes(process.pid)
        cgroup_path, read_cgroup = _cgroup_memory_reader()
        cgroup_baseline = read_cgroup()
        parent_peak = int(parent_baseline or 0)
        descendant_peak = 0
        tree_peak = int(parent_baseline or 0)
        cgroup_peak = int(cgroup_baseline or 0)

        process.stdin.write("GO\n")
        process.stdin.flush()
        deadline = time.monotonic() + max(1.0, float(deadline_seconds))
        while process.poll() is None:
            if time.monotonic() >= deadline:
                _terminate_case(process)
                raise RuntimeError(f"{case} regex transport measurement timed out")
            root_rss = int(_rss_bytes(process.pid) or 0)
            descendants = _descendants(process.pid)
            descendant_rss = sum(int(_rss_bytes(pid) or 0) for pid in descendants)
            parent_peak = max(parent_peak, root_rss)
            descendant_peak = max(descendant_peak, descendant_rss)
            tree_peak = max(tree_peak, root_rss + descendant_rss)
            cgroup_value = read_cgroup()
            if cgroup_value is not None:
                cgroup_peak = max(cgroup_peak, int(cgroup_value))
            time.sleep(0.001)

        stdout, stderr = process.communicate(timeout=5.0)
        if process.returncode != 0:
            raise RuntimeError(
                f"{case} measurement failed with {process.returncode}: {stderr.strip()}"
            )
        try:
            result = json.loads(stdout)
        except json.JSONDecodeError as exc:
            raise RuntimeError(
                f"{case} measurement returned malformed JSON: {stdout!r}"
            ) from exc

        residue = sorted(path.name for path in Path(temp_root).iterdir())
        result.update(
            {
                "parent_rss_baseline_bytes": parent_baseline,
                "parent_rss_peak_bytes": parent_peak if parent_baseline is not None else None,
                "parent_rss_incremental_peak_bytes": (
                    max(0, parent_peak - int(parent_baseline))
                    if parent_baseline is not None
                    else None
                ),
                "descendant_rss_peak_bytes": (
                    descendant_peak if Path("/proc").is_dir() else None
                ),
                "process_tree_rss_peak_bytes": (
                    tree_peak if parent_baseline is not None else None
                ),
                "process_tree_rss_incremental_peak_bytes": (
                    max(0, tree_peak - int(parent_baseline))
                    if parent_baseline is not None
                    else None
                ),
                "cgroup_memory_path": cgroup_path,
                "cgroup_memory_baseline_bytes": cgroup_baseline,
                "cgroup_memory_peak_bytes": (
                    cgroup_peak if cgroup_baseline is not None else None
                ),
                "cgroup_memory_incremental_peak_bytes": (
                    max(0, cgroup_peak - int(cgroup_baseline))
                    if cgroup_baseline is not None
                    else None
                ),
                "supervisor_temp_residue": residue,
            }
        )
        return result


def _median_case(rows: list[dict[str, Any]]) -> dict[str, Any]:
    if not rows:
        raise ValueError("measurement requires at least one sample")
    dynamic = set(_DYNAMIC_METRICS)
    first = rows[0]
    for row in rows[1:]:
        for key, value in first.items():
            if key not in dynamic and row.get(key) != value:
                raise RuntimeError(f"regex transport shape changed at {key}")

    result = {key: value for key, value in first.items() if key not in dynamic}
    result["samples"] = len(rows)
    for metric in _DYNAMIC_METRICS:
        values = [row.get(metric) for row in rows]
        numeric = [value for value in values if isinstance(value, (int, float))]
        result[f"{metric}_median"] = (
            int(statistics.median(numeric))
            if numeric and all(isinstance(value, int) for value in numeric)
            else round(float(statistics.median(numeric)), 6)
            if numeric
            else None
        )
    return result


def _reduction_percent(reference: object, product: object) -> float | None:
    if not isinstance(reference, (int, float)) or reference <= 0:
        return None
    if not isinstance(product, (int, float)):
        return None
    return round((float(reference) - float(product)) * 100.0 / float(reference), 3)


def build_report(
    *,
    chars: int,
    line_chars: int = 4096,
    samples: int = 1,
) -> dict[str, Any]:
    reference_rows: list[dict[str, Any]] = []
    product_rows: list[dict[str, Any]] = []
    for _ in range(max(1, int(samples))):
        reference_rows.append(
            _supervised_case(
                case="reference",
                chars=chars,
                line_chars=line_chars,
            )
        )
        product_rows.append(
            _supervised_case(
                case="product",
                chars=chars,
                line_chars=line_chars,
            )
        )

    reference = _median_case(reference_rows)
    product = _median_case(product_rows)
    return {
        "schema": SCHEMA,
        "method": {
            "source": "many-line canonical editor buffer with one capture-expanded regex match",
            "barrier": "source and Editor exist before READY; tracing and RSS polling begin at GO",
            "worker_deadline": "finite 5 s per case to isolate transport memory from the 250 ms default",
            "reference": "ordinary editor journey with rev0998 join plus full JSON/stdin haystack",
            "product": "ordinary editor journey with bounded chunks plus a file-backed path/count descriptor",
            "parent_python_memory": "CPython tracemalloc in each fresh case process",
            "process_memory": "Linux /proc RSS sampled every 1 ms; short peaks can be missed",
            "container_memory": "cgroup memory.current when available; includes unrelated cgroup activity and page cache",
            "timing": "local elapsed context only; not a portable performance bound",
        },
        "rev0998_joined_json_reference": reference,
        "file_backed_chunk_transport_product": product,
        "comparison": {
            "plans_exactly_equal": reference["plan_rows"] == product["plan_rows"],
            "match_views_exactly_equal": (
                reference["match_old"] == product["match_old"]
                and reference["match_replacement"] == product["match_replacement"]
            ),
            "reference_request_contains_complete_haystack": bool(
                reference["request_contains_haystack"]
            ),
            "product_request_contains_complete_haystack": bool(
                product["request_contains_haystack"]
            ),
            "product_request_uses_file_backed_transport": bool(
                product["request_contains_file_transport"]
            ),
            "product_staged_exact_document_chars": (
                int(product["staged_source_characters"])
                == int(product["document_chars"])
            ),
            "product_cleanup_residue_empty": (
                product["temporary_transport_residue"] == []
                and product["supervisor_temp_residue"] == []
            ),
            "protocol_request_reduction_percent": _reduction_percent(
                reference["protocol_request_bytes_median"],
                product["protocol_request_bytes_median"],
            ),
            "parent_traced_peak_reduction_percent": _reduction_percent(
                reference["traced_peak_bytes_median"],
                product["traced_peak_bytes_median"],
            ),
            "parent_rss_incremental_peak_reduction_percent": _reduction_percent(
                reference["parent_rss_incremental_peak_bytes_median"],
                product["parent_rss_incremental_peak_bytes_median"],
            ),
            "descendant_rss_peak_reduction_percent": _reduction_percent(
                reference["descendant_rss_peak_bytes_median"],
                product["descendant_rss_peak_bytes_median"],
            ),
            "process_tree_rss_incremental_peak_reduction_percent": _reduction_percent(
                reference["process_tree_rss_incremental_peak_bytes_median"],
                product["process_tree_rss_incremental_peak_bytes_median"],
            ),
            "cgroup_memory_comparison": (
                "context only: deleted file pages and unrelated processes persist "
                "in the shared cgroup across sequential samples"
            ),
        },
        "residuals": [
            "the child still materializes the one contiguous str required by Python re",
            "the private temporary file duplicates source bytes and may charge cgroup page cache until reclaimed",
            "SIGKILL or host loss can leave a private temp directory for later external cleanup",
            "staging time and filesystem capacity are not yet governed by a separate source-transfer budget",
            "RSS polling can miss sub-millisecond peaks; cgroup memory is noisy shared context",
            "regex capture output and packed match coordinates remain O(matches)",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--chars", type=int, default=16 * 1024 * 1024)
    parser.add_argument("--line-chars", type=int, default=4096)
    parser.add_argument("--samples", type=int, default=3)
    parser.add_argument("--json-out", type=Path)
    parser.add_argument("--case", choices=("reference", "product"), help=argparse.SUPPRESS)
    args = parser.parse_args()

    if args.case is not None:
        report = _run_case(
            case=str(args.case),
            chars=max(1, int(args.chars)),
            line_chars=max(1, int(args.line_chars)),
        )
    else:
        report = build_report(
            chars=max(1, int(args.chars)),
            line_chars=max(1, int(args.line_chars)),
            samples=max(1, int(args.samples)),
        )
    payload = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.json_out is not None:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(payload, encoding="utf-8")
    print(payload, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
