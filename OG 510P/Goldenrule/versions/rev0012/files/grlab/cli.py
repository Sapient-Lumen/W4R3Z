import argparse
import json
import os
import random
import shutil
import signal
import sqlite3
import subprocess
import sys
import threading
import time
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from grlab.certify import CertifyError, certify_memory_one_pair
from grlab.defdiff import compute_definitions_hash, diff_manifests
from grlab.hashing import hash_obj
from grlab.attest import attest_run_dir
from grlab.exporter import export_run_internal_tar, export_run_public_tar, redact_run_public
from grlab.html_report import render_report_html
from grlab.queue import Queue, load_manifest
from grlab.validate import validate_run_dir
from grlab.verify import verify_run_dir, verify_tarball


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ENGINE_BIN = REPO_ROOT / "target" / "debug" / "gr-engine"
RUNS_DIR = REPO_ROOT / "runs"


def _utc_now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json_atomic(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(f".{path.name}.tmp.{os.getpid()}")
    tmp.write_text(json.dumps(obj, indent=2, sort_keys=True), encoding="utf-8")
    os.replace(tmp, path)


def _write_text_atomic(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(f".{path.name}.tmp.{os.getpid()}")
    tmp.write_text(text, encoding="utf-8")
    os.replace(tmp, path)


def _engine_bin() -> Path:
    override = os.environ.get("GRLAB_ENGINE_BIN", "").strip()
    if override:
        return Path(override).expanduser().resolve()
    return DEFAULT_ENGINE_BIN


def _ensure_engine_built() -> None:
    engine = _engine_bin()
    if engine.exists():
        return
    if os.environ.get("GRLAB_ENGINE_BIN", "").strip():
        raise RuntimeError(f"GRLAB_ENGINE_BIN does not exist: {engine}")
    subprocess.check_call(
        ["cargo", "build", "-p", "gr_engine", "--bin", "gr-engine"],
        cwd=str(REPO_ROOT),
    )


@dataclass(frozen=True)
class Task:
    task_id: str
    task_path: Path
    out_path: Path


def _task_key(task_obj: Any) -> str:
    return hash_obj(task_obj)


def _run_engine_task(task_path: Path, out_path: Path) -> None:
    _ensure_engine_built()

    cmd = [
        str(_engine_bin()),
        "run-task",
        "--task",
        str(task_path),
        "--out",
        str(out_path),
        "--pretty",
    ]
    proc = subprocess.Popen(cmd, cwd=str(REPO_ROOT), start_new_session=True)

    def _terminate(*_args: object) -> None:
        try:
            os.killpg(proc.pid, signal.SIGTERM)
        except ProcessLookupError:
            pass

    old_term = signal.signal(signal.SIGTERM, _terminate)
    old_int = signal.signal(signal.SIGINT, _terminate)
    try:
        rc = proc.wait()
        if rc != 0:
            raise subprocess.CalledProcessError(rc, cmd)
    finally:
        signal.signal(signal.SIGTERM, old_term)
        signal.signal(signal.SIGINT, old_int)


def cmd_doctor(_args: argparse.Namespace) -> int:
    print(f"repo: {REPO_ROOT}")
    print(f"engine: {_engine_bin()}")
    print(f"python: {sys.version.split()[0]}")
    print(f"cargo: {shutil.which('cargo') or 'missing'}")
    return 0


def _load_world(spec: dict[str, Any], base: Path) -> dict[str, Any]:
    world = spec["world"]
    if isinstance(world, str):
        return _read_json((base / world).resolve())
    return world


def _load_strategies(spec: dict[str, Any], base: Path) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for s in spec["strategies"]:
        if isinstance(s, str):
            out.append(_read_json((base / s).resolve()))
        else:
            out.append(s)
    return out


def _resolve_world(spec: dict[str, Any], base: Path) -> tuple[dict[str, Any], str]:
    world_ref = spec["world"]
    if isinstance(world_ref, str):
        world_path = (base / world_ref).resolve()
        return (_read_json(world_path), str(world_ref))
    return (world_ref, "<inline>")


def _resolve_strategies(spec: dict[str, Any], base: Path) -> list[tuple[dict[str, Any], str]]:
    out: list[tuple[dict[str, Any], str]] = []
    for s in spec["strategies"]:
        if isinstance(s, str):
            strat_path = (base / s).resolve()
            out.append((_read_json(strat_path), str(s)))
        else:
            out.append((s, "<inline>"))
    return out


def cmd_run(args: argparse.Namespace) -> int:
    exp_path = Path(args.experiment).resolve()
    spec = _read_json(exp_path)
    base = exp_path.parent

    world, world_source = _resolve_world(spec, base)
    strategies_with_sources = _resolve_strategies(spec, base)
    strategies = [s for (s, _src) in strategies_with_sources]
    replications = int(spec.get("replications", 1))
    trace_rounds = int(spec.get("trace_rounds", 0))

    run_id = args.run_id or f"{time.strftime('%Y%m%d_%H%M%S')}_{spec.get('id','run')}"
    run_dir = RUNS_DIR / run_id
    tasks_dir = run_dir / "tasks"
    artifacts_dir = run_dir / "artifacts"

    tasks_dir.mkdir(parents=True, exist_ok=True)
    artifacts_dir.mkdir(parents=True, exist_ok=True)

    definition_world = {"id": world.get("id"), "source": world_source, "hash": hash_obj(world)}
    definition_strategies = []
    for (s, src) in strategies_with_sources:
        definition_strategies.append({"id": s.get("id"), "source": src, "hash": hash_obj(s)})

    manifest = {
        "schema_version": 3,
        "run_id": run_id,
        "created_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "experiment": str(exp_path),
        "experiment_hash": hash_obj(spec),
        "world_id": world.get("id"),
        "replications": replications,
        "trace_rounds": trace_rounds,
        "definitions": {"world": definition_world, "strategies": definition_strategies},
        "tasks": [],
    }
    manifest["definitions_hash"] = compute_definitions_hash(manifest)

    tasks: list[Task] = []
    for rep in range(replications):
        for i, a in enumerate(strategies):
            for j, b in enumerate(strategies):
                task_obj = {
                    "task_id": f"{a['id']}__vs__{b['id']}__rep{rep}",
                    "world": world,
                    "strategy_a": a,
                    "strategy_b": b,
                    "match_seed": int(world["seed"]) + 1000 * rep + 31 * i + j,
                    "trace_rounds": trace_rounds,
                }
                key = _task_key(task_obj)
                task_path = tasks_dir / f"{key}.task.json"
                out_path = artifacts_dir / f"{key}.artifact.json"
                if not task_path.exists():
                    task_path.write_text(json.dumps(task_obj, indent=2, sort_keys=True), encoding="utf-8")
                manifest["tasks"].append(
                    {
                        "key": key,
                        "task_id": task_obj["task_id"],
                        "task_path": str(task_path.relative_to(run_dir)),
                        "artifact_path": str(out_path.relative_to(run_dir)),
                    }
                )
                tasks.append(Task(task_id=task_obj["task_id"], task_path=task_path, out_path=out_path))

    _write_json_atomic(run_dir / "manifest.json", manifest)

    if args.enqueue:
        q = Queue(run_dir=run_dir, db_path=_queue_db_path(run_dir))
        q.init()
        q.import_manifest(manifest)

    if args.plan_only:
        print(run_id)
        return 0

    done = 0
    for t in tasks:
        if t.out_path.exists():
            done += 1
            continue
        _run_engine_task(t.task_path, t.out_path)
        done += 1
        if args.limit and done >= args.limit:
            break

    print(run_id)
    return 0


def cmd_resume(args: argparse.Namespace) -> int:
    run_dir = Path(args.run_dir).resolve()
    manifest = _read_json(run_dir / "manifest.json")

    done = 0
    for t in manifest["tasks"]:
        task_path = run_dir / t["task_path"]
        out_path = run_dir / t["artifact_path"]
        if out_path.exists():
            done += 1
            continue
        _run_engine_task(task_path, out_path)
        done += 1
        if args.limit and done >= args.limit:
            break

    print(manifest["run_id"])
    return 0


def cmd_validate(args: argparse.Namespace) -> int:
    run_dir = Path(args.run_dir).resolve()
    res = validate_run_dir(
        run_dir,
        check_queue=bool(args.check_queue),
        check_definitions=bool(args.check_definitions),
    )
    print(json.dumps({"run_dir": str(run_dir), **res}, indent=2))
    return 0 if res["ok"] else 1


def cmd_verify(args: argparse.Namespace) -> int:
    target = Path(args.target).resolve()
    if target.is_dir():
        res = verify_run_dir(target, check_definitions_hash=bool(args.check_definitions_hash))
        out = {"ok": res.ok, "problems": res.problems, "target": str(target), "kind": "run_dir"}
    else:
        res = verify_tarball(target, check_definitions_hash=bool(args.check_definitions_hash))
        out = {"ok": res.ok, "problems": res.problems, "target": str(target), "kind": "tarball"}

    print(json.dumps(out, indent=2))
    return 0 if res.ok else 1


def _build_report_rows(run_dir: Path, manifest: dict[str, Any], use_db: bool) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    if use_db:
        q = Queue(run_dir=run_dir, db_path=_queue_db_path(run_dir))
        q.init()
        q.import_manifest(manifest)
        q.reconcile()
        q.index_artifacts(limit=0)
        with sqlite3.connect(str(q.db_path)) as con:
            for r in con.execute(
                """
                SELECT task_id, world_id, strategy_a_id, strategy_b_id, rounds, avg_a, avg_b, coop_a, coop_b, mutual_c
                FROM artifacts
                ORDER BY task_id
                """
            ):
                rows.append(
                    {
                        "task_id": r[0],
                        "world_id": r[1],
                        "a": r[2],
                        "b": r[3],
                        "rounds": r[4],
                        "avg_a": r[5],
                        "avg_b": r[6],
                        "coop_a": r[7],
                        "coop_b": r[8],
                        "mutual_c": r[9],
                    }
                )
        return rows

    for t in manifest.get("tasks", []):
        if not isinstance(t, dict):
            continue
        artifact_path = t.get("artifact_path")
        if not isinstance(artifact_path, str) or not artifact_path:
            continue
        art_path = run_dir / artifact_path
        if not art_path.exists():
            continue
        art = _read_json(art_path)
        stats = art.get("stats", {}) if isinstance(art, dict) else {}
        rows.append(
            {
                "task_id": art.get("task_id") if isinstance(art, dict) else None,
                "world_id": art.get("world_id") if isinstance(art, dict) else None,
                "a": art.get("strategy_a_id") if isinstance(art, dict) else None,
                "b": art.get("strategy_b_id") if isinstance(art, dict) else None,
                "rounds": stats.get("rounds") if isinstance(stats, dict) else None,
                "avg_a": stats.get("avg_payoff_a") if isinstance(stats, dict) else None,
                "avg_b": stats.get("avg_payoff_b") if isinstance(stats, dict) else None,
                "coop_a": stats.get("coop_rate_a") if isinstance(stats, dict) else None,
                "coop_b": stats.get("coop_rate_b") if isinstance(stats, dict) else None,
                "mutual_c": stats.get("mutual_coop_rate") if isinstance(stats, dict) else None,
            }
        )
    return rows


def _build_report(run_dir: Path, use_db: bool) -> dict[str, Any]:
    manifest = _read_json(run_dir / "manifest.json")
    rows = _build_report_rows(run_dir=run_dir, manifest=manifest, use_db=use_db)
    return {
        "run_id": manifest.get("run_id"),
        "schema_version": manifest.get("schema_version", 1),
        "experiment": manifest.get("experiment"),
        "experiment_hash": manifest.get("experiment_hash"),
        "definitions_hash": manifest.get("definitions_hash"),
        "world_id": manifest.get("world_id"),
        "replications": manifest.get("replications"),
        "trace_rounds": manifest.get("trace_rounds"),
        "n_artifacts": len(rows),
        "rows": rows,
    }


def cmd_report(args: argparse.Namespace) -> int:
    run_dir = Path(args.run_dir).resolve()
    report = _build_report(run_dir=run_dir, use_db=bool(args.use_db))
    _write_json_atomic(run_dir / "report.json", report)
    print(json.dumps({"run_id": report["run_id"], "n_artifacts": report["n_artifacts"]}, indent=2))
    return 0


def cmd_report_html(args: argparse.Namespace) -> int:
    run_dir = Path(args.run_dir).resolve()

    if (run_dir / "report.json").exists() and not args.refresh:
        report = _read_json(run_dir / "report.json")
    else:
        report = _build_report(run_dir=run_dir, use_db=bool(args.use_db))
        _write_json_atomic(run_dir / "report.json", report)

    artifact_path_by_task_id: dict[str, str] = {}
    if (run_dir / "manifest.json").exists():
        man = _read_json(run_dir / "manifest.json")
        for t in man.get("tasks", []) if isinstance(man, dict) else []:
            if not isinstance(t, dict):
                continue
            task_id = t.get("task_id")
            ap = t.get("artifact_path")
            if isinstance(task_id, str) and isinstance(ap, str) and task_id and ap:
                artifact_path_by_task_id[task_id] = ap

    title = str(args.title) if args.title else "Concord Report"
    html_text = render_report_html(
        report if isinstance(report, dict) else {},
        title=title,
        artifact_path_by_task_id=artifact_path_by_task_id,
    )

    out_path = Path(args.out).resolve() if args.out else (run_dir / "report.html").resolve()
    _write_text_atomic(out_path, html_text)
    print(str(out_path))
    return 0


def cmd_diff_match(args: argparse.Namespace) -> int:
    a = Path(args.a).resolve()
    b = Path(args.b).resolve()
    out = Path(args.out).resolve()
    _ensure_engine_built()

    cmd = [
        str(_engine_bin()),
        "diff-match-artifacts",
        "--a",
        str(a),
        "--b",
        str(b),
        "--out",
        str(out),
        "--id",
        str(args.id),
    ]
    if args.pretty:
        cmd.append("--pretty")
    subprocess.check_call(cmd, cwd=str(REPO_ROOT))
    print(str(out))
    return 0


def cmd_defdiff(args: argparse.Namespace) -> int:
    run_a = Path(args.run_a).resolve()
    run_b = Path(args.run_b).resolve()
    man_a = _read_json(run_a / "manifest.json")
    man_b = _read_json(run_b / "manifest.json")

    d = diff_manifests(man_a, man_b)
    payload = {
        "run_a": str(run_a),
        "run_b": str(run_b),
        "changed": d.changed,
        "definitions_hash_changed": d.definitions_hash_changed,
        "a_definitions_hash": d.a_definitions_hash,
        "b_definitions_hash": d.b_definitions_hash,
        "experiment_changed": d.experiment_changed,
        "world_changed": d.world_changed,
        "strategies_added": d.strategies_added,
        "strategies_removed": d.strategies_removed,
        "strategies_changed": d.strategies_changed,
    }
    if args.out:
        _write_json_atomic(Path(args.out).resolve(), payload)
    print(json.dumps(payload, indent=2))
    return 0


def cmd_trace(args: argparse.Namespace) -> int:
    if not args.diff:
        raise SystemExit("trace currently only supports --diff")

    def _artifact_for_task_id(run_dir: Path, task_id: str) -> Path:
        man = _read_json(run_dir / "manifest.json")
        for t in man.get("tasks", []):
            if not isinstance(t, dict):
                continue
            if str(t.get("task_id", "")) != task_id:
                continue
            ap = t.get("artifact_path")
            if not isinstance(ap, str) or not ap:
                break
            return (run_dir / ap).resolve()
        raise FileNotFoundError(f"task_id not found in manifest: {task_id}")

    a: Path | None = None
    b: Path | None = None
    if args.run_a and args.run_b and args.task_id:
        run_a = Path(args.run_a).resolve()
        run_b = Path(args.run_b).resolve()
        a = _artifact_for_task_id(run_a, str(args.task_id))
        b = _artifact_for_task_id(run_b, str(args.task_id))
    else:
        a = Path(args.a).resolve() if args.a else None
        b = Path(args.b).resolve() if args.b else None

    if a is None or b is None:
        raise SystemExit("trace --diff requires either (--a and --b) or (--run-a, --run-b, --task-id)")
    if not a.exists():
        raise FileNotFoundError(f"missing artifact A: {a}")
    if not b.exists():
        raise FileNotFoundError(f"missing artifact B: {b}")

    keep_path: Path | None = None
    tmp_path: Path | None = None
    if args.out:
        keep_path = Path(args.out).resolve()
        out_path = keep_path
    else:
        fd, p = tempfile.mkstemp(prefix="grlab_trace_diff_", suffix=".json")
        os.close(fd)
        tmp_path = Path(p).resolve()
        out_path = tmp_path

    try:
        _ensure_engine_built()
        cmd = [
            str(_engine_bin()),
            "diff-match-artifacts",
            "--a",
            str(a),
            "--b",
            str(b),
            "--out",
            str(out_path),
            "--id",
            str(args.id),
        ]
        if args.pretty:
            cmd.append("--pretty")
        subprocess.check_call(cmd, cwd=str(REPO_ROOT))
        d = _read_json(out_path)
        summary = {
            "changed": d.get("changed"),
            "stats_changed": d.get("stats_changed"),
            "trace_changed": d.get("trace_changed"),
            "first_diff_round": d.get("first_diff_round"),
            "diff_path": str(out_path) if keep_path is not None else None,
        }
        print(json.dumps(summary, indent=2))
        return 0
    finally:
        if tmp_path is not None:
            try:
                tmp_path.unlink()
            except FileNotFoundError:
                pass


def cmd_compare(args: argparse.Namespace) -> int:
    run_a = Path(args.run_a).resolve()
    run_b = Path(args.run_b).resolve()

    man_a = _read_json(run_a / "manifest.json")
    man_b = _read_json(run_b / "manifest.json")
    defs = diff_manifests(man_a, man_b)

    rep_a_path = run_a / "report.json"
    rep_b_path = run_b / "report.json"
    if rep_a_path.exists() and not args.refresh:
        rep_a = _read_json(rep_a_path)
        rep_a_from = "file"
    else:
        rep_a = _build_report(run_dir=run_a, use_db=bool(args.use_db))
        rep_a_from = "computed"
        if args.refresh:
            _write_json_atomic(rep_a_path, rep_a)

    if rep_b_path.exists() and not args.refresh:
        rep_b = _read_json(rep_b_path)
        rep_b_from = "file"
    else:
        rep_b = _build_report(run_dir=run_b, use_db=bool(args.use_db))
        rep_b_from = "computed"
        if args.refresh:
            _write_json_atomic(rep_b_path, rep_b)

    rows_a = rep_a.get("rows", [])
    rows_b = rep_b.get("rows", [])
    if not isinstance(rows_a, list):
        rows_a = []
    if not isinstance(rows_b, list):
        rows_b = []

    def _map(rows: list[Any]) -> dict[str, dict[str, Any]]:
        out: dict[str, dict[str, Any]] = {}
        for r in rows:
            if isinstance(r, dict) and isinstance(r.get("task_id"), str):
                out[str(r["task_id"])] = r
        return out

    a_map = _map(rows_a)
    b_map = _map(rows_b)
    a_ids = set(a_map.keys())
    b_ids = set(b_map.keys())
    common = sorted(a_ids & b_ids)
    only_a = sorted(a_ids - b_ids)
    only_b = sorted(b_ids - a_ids)

    metrics = ["avg_a", "avg_b", "coop_a", "coop_b", "mutual_c", "rounds"]
    deltas: dict[str, list[float]] = {m: [] for m in metrics}
    per_task: list[dict[str, Any]] = []
    for tid in common:
        ra = a_map[tid]
        rb = b_map[tid]
        row: dict[str, Any] = {"task_id": tid, "a": ra.get("a"), "b": ra.get("b")}
        for m in metrics:
            va = ra.get(m)
            vb = rb.get(m)
            if isinstance(va, (int, float)) and isinstance(vb, (int, float)):
                d = float(vb) - float(va)
                row[f"delta_{m}"] = d
                deltas[m].append(d)
        per_task.append(row)

    def _mean(xs: list[float]) -> float | None:
        if not xs:
            return None
        return sum(xs) / float(len(xs))

    def _max_abs(xs: list[float]) -> float | None:
        if not xs:
            return None
        return max(abs(x) for x in xs)

    metric = str(args.metric)
    if metric not in metrics:
        raise SystemExit(f"unknown metric: {metric} (choose from {metrics})")
    top_n = int(args.top)
    if top_n < 0:
        top_n = 0

    per_task_sorted = sorted(
        per_task,
        key=lambda r: abs(float(r.get(f"delta_{metric}", 0.0))),
        reverse=True,
    )
    top = per_task_sorted[:top_n] if top_n else []

    def _strategy_summary(rows: list[Any]) -> dict[str, dict[str, float | int | None]]:
        acc: dict[str, dict[str, float]] = {}
        counts: dict[str, int] = {}
        rounds_counts: dict[str, int] = {}

        def _ensure(sid: str) -> None:
            if sid not in acc:
                acc[sid] = {
                    "payoff_sum": 0.0,
                    "coop_sum": 0.0,
                    "mutual_c_sum": 0.0,
                    "rounds_sum": 0.0,
                }
                counts[sid] = 0
                rounds_counts[sid] = 0

        for r in rows:
            if not isinstance(r, dict):
                continue
            sa = r.get("a")
            sb = r.get("b")
            if not isinstance(sa, str) or not isinstance(sb, str):
                continue
            _ensure(sa)
            _ensure(sb)

            avg_a = r.get("avg_a")
            avg_b = r.get("avg_b")
            coop_a = r.get("coop_a")
            coop_b = r.get("coop_b")
            mutual_c = r.get("mutual_c")
            rounds = r.get("rounds")

            if isinstance(avg_a, (int, float)):
                acc[sa]["payoff_sum"] += float(avg_a)
            if isinstance(avg_b, (int, float)):
                acc[sb]["payoff_sum"] += float(avg_b)
            if isinstance(coop_a, (int, float)):
                acc[sa]["coop_sum"] += float(coop_a)
            if isinstance(coop_b, (int, float)):
                acc[sb]["coop_sum"] += float(coop_b)
            if isinstance(mutual_c, (int, float)):
                acc[sa]["mutual_c_sum"] += float(mutual_c)
                acc[sb]["mutual_c_sum"] += float(mutual_c)
            if isinstance(rounds, (int, float)):
                acc[sa]["rounds_sum"] += float(rounds)
                acc[sb]["rounds_sum"] += float(rounds)
                rounds_counts[sa] += 1
                rounds_counts[sb] += 1

            counts[sa] += 1
            counts[sb] += 1

        out: dict[str, dict[str, float | int | None]] = {}
        for sid, sums in acc.items():
            n = counts.get(sid, 0)
            rn = rounds_counts.get(sid, 0)
            out[sid] = {
                "n_games": n,
                "payoff_mean": (sums["payoff_sum"] / float(n)) if n else None,
                "coop_mean": (sums["coop_sum"] / float(n)) if n else None,
                "mutual_c_mean": (sums["mutual_c_sum"] / float(n)) if n else None,
                "rounds_mean": (sums["rounds_sum"] / float(rn)) if rn else None,
            }
        return out

    strat_a = _strategy_summary(rows_a)
    strat_b = _strategy_summary(rows_b)
    all_ids = sorted(set(strat_a.keys()) | set(strat_b.keys()))
    strat_delta: list[dict[str, Any]] = []
    for sid in all_ids:
        ra = strat_a.get(sid)
        rb = strat_b.get(sid)
        row: dict[str, Any] = {"strategy_id": sid, "a": ra, "b": rb}
        if ra is not None and rb is not None:
            for k in ["payoff_mean", "coop_mean", "mutual_c_mean", "rounds_mean"]:
                va = ra.get(k)
                vb = rb.get(k)
                if isinstance(va, (int, float)) and isinstance(vb, (int, float)):
                    row[f"delta_{k}"] = float(vb) - float(va)
        strat_delta.append(row)

    payload = {
        "run_a": str(run_a),
        "run_b": str(run_b),
        "definitions": {
            "changed": defs.changed,
            "definitions_hash_changed": defs.definitions_hash_changed,
            "a_definitions_hash": defs.a_definitions_hash,
            "b_definitions_hash": defs.b_definitions_hash,
            "experiment_changed": defs.experiment_changed,
            "world_changed": defs.world_changed,
            "strategies_added": defs.strategies_added,
            "strategies_removed": defs.strategies_removed,
            "strategies_changed": defs.strategies_changed,
        },
        "reports": {
            "run_a_report_path": str(rep_a_path) if rep_a_path.exists() else None,
            "run_b_report_path": str(rep_b_path) if rep_b_path.exists() else None,
            "run_a_from": rep_a_from,
            "run_b_from": rep_b_from,
        },
        "artifacts": {"common": len(common), "only_a": len(only_a), "only_b": len(only_b)},
        "delta_summary": {
            m: {"mean": _mean(deltas[m]), "max_abs": _max_abs(deltas[m])} for m in metrics
        },
        "strategy_deltas": strat_delta,
        "top_metric": metric,
        "top": top,
    }
    if args.out:
        _write_json_atomic(Path(args.out).resolve(), payload)
    print(json.dumps(payload, indent=2))
    return 0


def cmd_reproduce(args: argparse.Namespace) -> int:
    run_dir = Path(args.run_dir).resolve()
    manifest = _read_json(run_dir / "manifest.json")

    task_entry: dict[str, Any] | None = None
    for t in manifest.get("tasks", []):
        if not isinstance(t, dict):
            continue
        if args.key and str(t.get("key", "")) == str(args.key):
            task_entry = t
            break
        if args.task_id and str(t.get("task_id", "")) == str(args.task_id):
            task_entry = t
            break

    if task_entry is None:
        raise SystemExit("task not found (provide --task-id or --key)")

    key = str(task_entry.get("key", ""))
    task_path = run_dir / str(task_entry.get("task_path", ""))
    orig_artifact_path = run_dir / str(task_entry.get("artifact_path", ""))
    if not key or not task_path.exists() or not orig_artifact_path.exists():
        raise SystemExit("task/artifact paths are missing for selected task")

    out_dir = (run_dir / "reproduce").resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    stamp = time.strftime("%Y%m%d_%H%M%S")
    new_artifact_path = out_dir / f"{key}.repro.{stamp}.artifact.json"

    _run_engine_task(task_path, new_artifact_path)

    diff_path = out_dir / f"{key}.repro.{stamp}.diff.json"
    _ensure_engine_built()
    cmd = [
        str(_engine_bin()),
        "diff-match-artifacts",
        "--a",
        str(orig_artifact_path),
        "--b",
        str(new_artifact_path),
        "--out",
        str(diff_path),
        "--id",
        str(args.id),
        "--pretty",
    ]
    subprocess.check_call(cmd, cwd=str(REPO_ROOT))
    d = _read_json(diff_path)

    payload = {
        "run_dir": str(run_dir),
        "task_id": task_entry.get("task_id"),
        "key": key,
        "task_path": str(task_path),
        "artifact_original": str(orig_artifact_path),
        "artifact_reproduced": str(new_artifact_path),
        "diff_path": str(diff_path),
        "changed": d.get("changed"),
        "stats_changed": d.get("stats_changed"),
        "trace_changed": d.get("trace_changed"),
        "first_diff_round": d.get("first_diff_round"),
    }
    if args.out:
        _write_json_atomic(Path(args.out).resolve(), payload)
    print(json.dumps(payload, indent=2))
    return 0


def cmd_quick(args: argparse.Namespace) -> int:
    world = _read_json(Path(args.world).resolve())
    a = _read_json(Path(args.strategy_a).resolve())
    b = _read_json(Path(args.strategy_b).resolve())
    task = {
        "schema_version": 1,
        "task_id": str(args.task_id),
        "world": world,
        "strategy_a": a,
        "strategy_b": b,
        "match_seed": int(args.match_seed),
        "trace_rounds": int(args.trace_rounds),
    }
    out_path = Path(args.out).resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    tmp_task = out_path.with_name(f".{out_path.name}.task.tmp.{os.getpid()}")
    tmp_task.write_text(json.dumps(task, indent=2, sort_keys=True), encoding="utf-8")
    try:
        _run_engine_task(tmp_task, out_path)
    finally:
        try:
            tmp_task.unlink()
        except FileNotFoundError:
            pass
    print(str(out_path))
    return 0


def cmd_redact(args: argparse.Namespace) -> int:
    if not args.public:
        raise SystemExit("only --public redaction is supported right now")
    run_dir = Path(args.run_dir).resolve()
    out_dir = Path(args.out_dir).resolve()
    report = _build_report(run_dir=run_dir, use_db=bool(args.use_db))
    denylist_path: Path | None = None
    if not bool(getattr(args, "no_denylist", False)):
        denylist_path = Path(args.denylist).resolve()
    _ = redact_run_public(
        run_dir=run_dir,
        out_dir=out_dir,
        report=report,
        denylist_path=denylist_path,
        allow_sensitive=bool(getattr(args, "allow_sensitive", False)),
    )
    print(str(out_dir))
    return 0


def cmd_export(args: argparse.Namespace) -> int:
    run_dir = Path(args.run_dir).resolve()
    out_path = Path(args.out).resolve()
    if args.public:
        report = _build_report(run_dir=run_dir, use_db=bool(args.use_db))
        denylist_path: Path | None = None
        if not bool(getattr(args, "no_denylist", False)):
            denylist_path = Path(args.denylist).resolve()
        _ = export_run_public_tar(
            run_dir=run_dir,
            out_path=out_path,
            report=report,
            denylist_path=denylist_path,
            allow_sensitive=bool(getattr(args, "allow_sensitive", False)),
        )
    elif args.internal:
        _ = export_run_internal_tar(run_dir=run_dir, out_path=out_path)
    else:
        raise SystemExit("export requires --public or --internal")
    print(str(out_path))
    return 0


def cmd_attest(args: argparse.Namespace) -> int:
    run_dir = Path(args.run_dir).resolve()
    payload = attest_run_dir(
        run_dir,
        include_queue_db=bool(args.include_queue_db),
        include_artifacts=bool(args.include_artifacts),
    )
    if args.out:
        _write_json_atomic(Path(args.out).resolve(), payload)
    print(json.dumps(payload, indent=2))
    return 0


def cmd_frontier(args: argparse.Namespace) -> int:
    run_dir = Path(args.run_dir).resolve()
    report_path = run_dir / "report.json"
    if report_path.exists() and not args.refresh:
        report = _read_json(report_path)
    else:
        report = _build_report(run_dir=run_dir, use_db=bool(args.use_db))
        if args.refresh:
            _write_json_atomic(report_path, report)

    rows = report.get("rows", [])
    if not isinstance(rows, list):
        rows = []

    acc: dict[str, dict[str, float]] = {}
    counts: dict[str, int] = {}

    def _ensure(sid: str) -> None:
        if sid not in acc:
            acc[sid] = {"payoff_sum": 0.0, "coop_sum": 0.0, "mutual_c_sum": 0.0}
            counts[sid] = 0

    for r in rows:
        if not isinstance(r, dict):
            continue
        sa = r.get("a")
        sb = r.get("b")
        if not isinstance(sa, str) or not isinstance(sb, str):
            continue
        _ensure(sa)
        _ensure(sb)

        avg_a = r.get("avg_a")
        avg_b = r.get("avg_b")
        coop_a = r.get("coop_a")
        coop_b = r.get("coop_b")
        mutual_c = r.get("mutual_c")

        if isinstance(avg_a, (int, float)):
            acc[sa]["payoff_sum"] += float(avg_a)
        if isinstance(avg_b, (int, float)):
            acc[sb]["payoff_sum"] += float(avg_b)
        if isinstance(coop_a, (int, float)):
            acc[sa]["coop_sum"] += float(coop_a)
        if isinstance(coop_b, (int, float)):
            acc[sb]["coop_sum"] += float(coop_b)
        if isinstance(mutual_c, (int, float)):
            acc[sa]["mutual_c_sum"] += float(mutual_c)
            acc[sb]["mutual_c_sum"] += float(mutual_c)

        counts[sa] += 1
        counts[sb] += 1

    summaries: list[dict[str, Any]] = []
    for sid in sorted(acc.keys()):
        n = counts.get(sid, 0)
        if n < int(args.min_games):
            continue
        payoff_mean = acc[sid]["payoff_sum"] / float(n) if n else None
        coop_mean = acc[sid]["coop_sum"] / float(n) if n else None
        mutual_c_mean = acc[sid]["mutual_c_sum"] / float(n) if n else None
        summaries.append(
            {
                "strategy_id": sid,
                "n_games": n,
                "payoff_mean": payoff_mean,
                "coop_mean": coop_mean,
                "mutual_c_mean": mutual_c_mean,
            }
        )

    metric_map = {
        "payoff": "payoff_mean",
        "coop": "coop_mean",
        "mutual_c": "mutual_c_mean",
    }
    x_key = metric_map.get(str(args.x), "")
    y_key = metric_map.get(str(args.y), "")
    if not x_key or not y_key:
        raise SystemExit(f"unknown metrics: x={args.x} y={args.y} (choose payoff|coop|mutual_c)")

    def _val(row: dict[str, Any], k: str) -> float:
        v = row.get(k)
        return float(v) if isinstance(v, (int, float)) else float("-inf")

    frontier: list[dict[str, Any]] = []
    for i, ri in enumerate(summaries):
        xi = _val(ri, x_key)
        yi = _val(ri, y_key)
        dominated = False
        for j, rj in enumerate(summaries):
            if i == j:
                continue
            xj = _val(rj, x_key)
            yj = _val(rj, y_key)
            if xj >= xi and yj >= yi and (xj > xi or yj > yi):
                dominated = True
                break
        if not dominated:
            frontier.append(ri)

    frontier = sorted(frontier, key=lambda r: (_val(r, x_key), _val(r, y_key)), reverse=True)
    top_n = int(args.top)
    if top_n > 0:
        frontier = frontier[:top_n]

    payload = {
        "run_dir": str(run_dir),
        "definitions_hash": report.get("definitions_hash"),
        "x": str(args.x),
        "y": str(args.y),
        "summary": summaries,
        "frontier": frontier,
    }
    if args.out:
        _write_json_atomic(Path(args.out).resolve(), payload)
    print(json.dumps(payload, indent=2))
    return 0


def _queue_db_path(run_dir: Path) -> Path:
    return run_dir / "queue.sqlite3"


def cmd_queue_init(args: argparse.Namespace) -> int:
    run_dir = Path(args.run_dir).resolve()
    q = Queue(run_dir=run_dir, db_path=_queue_db_path(run_dir))
    q.init()
    print(json.dumps({"run_dir": str(run_dir), "db": str(q.db_path)}, indent=2))
    return 0


def cmd_queue_import(args: argparse.Namespace) -> int:
    run_dir = Path(args.run_dir).resolve()
    q = Queue(run_dir=run_dir, db_path=_queue_db_path(run_dir))
    q.init()
    manifest = load_manifest(run_dir)
    if args.max_attempts:
        manifest["queue_max_attempts"] = int(args.max_attempts)
    if args.retry_backoff_seconds:
        manifest["queue_retry_backoff_seconds"] = int(args.retry_backoff_seconds)
    inserted = q.import_manifest(manifest)
    counts = q.counts()
    print(
        json.dumps(
            {
                "run_dir": str(run_dir),
                "inserted": inserted,
                "counts": counts.__dict__,
            },
            indent=2,
        )
    )
    return 0


def cmd_queue_status(args: argparse.Namespace) -> int:
    run_dir = Path(args.run_dir).resolve()
    q = Queue(run_dir=run_dir, db_path=_queue_db_path(run_dir))
    q.init()
    counts = q.counts()
    indexed = q.indexed_artifacts_count()
    print(
        json.dumps(
            {"run_dir": str(run_dir), "counts": counts.__dict__, "indexed_artifacts": indexed},
            indent=2,
        )
    )
    return 0


def cmd_queue_reset_errors(args: argparse.Namespace) -> int:
    run_dir = Path(args.run_dir).resolve()
    q = Queue(run_dir=run_dir, db_path=_queue_db_path(run_dir))
    q.init()
    reset = q.reset_errors(include_dead=bool(args.include_dead))
    counts = q.counts()
    print(
        json.dumps(
            {"run_dir": str(run_dir), "reset": reset, "counts": counts.__dict__}, indent=2
        )
    )
    return 0


def cmd_queue_work(args: argparse.Namespace) -> int:
    run_dir = Path(args.run_dir).resolve()
    q = Queue(run_dir=run_dir, db_path=_queue_db_path(run_dir))
    q.init()

    manifest = load_manifest(run_dir)
    if args.max_attempts:
        manifest["queue_max_attempts"] = int(args.max_attempts)
    if args.retry_backoff_seconds:
        manifest["queue_retry_backoff_seconds"] = int(args.retry_backoff_seconds)
    q.import_manifest(manifest)

    q.reconcile()

    _ensure_engine_built()

    owner_base = args.owner or f"pid:{os.getpid()}"
    lease_seconds = int(args.lease_seconds)
    heartbeat_seconds = int(args.heartbeat_seconds)
    workers = int(args.workers)
    retry_errors = bool(args.retry_errors)
    task_timeout_seconds = int(args.task_timeout_seconds)
    limit = int(args.limit) if args.limit else 0

    if workers <= 0:
        workers = 1
    if heartbeat_seconds <= 0:
        heartbeat_seconds = max(1, min(60, lease_seconds // 3 if lease_seconds else 10))

    stop = threading.Event()
    term_grace_sec_env = os.environ.get("TERM_GRACE_SEC", "").strip()
    term_grace_sec = float(term_grace_sec_env) if term_grace_sec_env else 0.0

    @dataclass(frozen=True)
    class RunningProc:
        proc: subprocess.Popen[bytes]

    running: dict[int, RunningProc] = {}
    running_lock = threading.Lock()
    claimed: dict[str, str] = {}
    claimed_lock = threading.Lock()
    shutdown_deadline: list[float | None] = [None]

    def _kill_running(sig: int) -> None:
        with running_lock:
            procs = list(running.values())
        for p in procs:
            try:
                os.killpg(p.proc.pid, sig)
            except ProcessLookupError:
                pass

    def _prune_finished_running() -> None:
        with running_lock:
            finished = [pid for pid, p in running.items() if p.proc.poll() is not None]
            for pid in finished:
                running.pop(pid, None)

    def _abandon_claimed(reason: str) -> None:
        with claimed_lock:
            items = list(claimed.items())
        for key, owner in items:
            q.abandon_to_pending(key, owner, reason)

    def _handle_signal(_signum: int, _frame: object) -> None:
        stop.set()
        if shutdown_deadline[0] is None and term_grace_sec > 0:
            shutdown_deadline[0] = time.time() + term_grace_sec
        _abandon_claimed(f"terminated by signal {_signum}")
        _kill_running(signal.SIGTERM)

    old_term = signal.signal(signal.SIGTERM, _handle_signal)
    old_int = signal.signal(signal.SIGINT, _handle_signal)

    processed = 0
    processed_lock = threading.Lock()

    def _run_one(task: Any, worker_owner: str) -> None:
        if task.artifact_path.exists():
            q.mark_done(task.key)
            return
        if stop.is_set():
            q.abandon_to_pending(task.key, worker_owner, "terminated (shutdown requested)")
            return

        cmd = [
            str(_engine_bin()),
            "run-task",
            "--task",
            str(task.task_path),
            "--out",
            str(task.artifact_path),
            "--pretty",
        ]
        proc = subprocess.Popen(cmd, cwd=str(REPO_ROOT), start_new_session=True)
        with running_lock:
            running[proc.pid] = RunningProc(proc=proc)
        try:
            start = time.time()
            next_renew = time.time() + float(heartbeat_seconds)
            while True:
                if stop.is_set():
                    try:
                        os.killpg(proc.pid, signal.SIGTERM)
                    except ProcessLookupError:
                        pass
                    q.abandon_to_pending(task.key, worker_owner, "terminated (shutdown requested)")
                    break
                rc = proc.poll()
                if rc is not None:
                    if rc != 0:
                        raise subprocess.CalledProcessError(rc, cmd)
                    if not task.artifact_path.exists():
                        raise RuntimeError("engine returned success but artifact is missing")
                    q.mark_done(task.key)
                    break
                now = time.time()
                if task_timeout_seconds > 0 and (now - start) > float(task_timeout_seconds):
                    try:
                        os.killpg(proc.pid, signal.SIGTERM)
                    except ProcessLookupError:
                        pass
                    raise TimeoutError(f"task timeout after {task_timeout_seconds}s")
                if now >= next_renew:
                    q.renew_lease(task.key, worker_owner, lease_seconds)
                    next_renew = now + float(heartbeat_seconds)
                time.sleep(0.2)
        finally:
            if not stop.is_set():
                with running_lock:
                    running.pop(proc.pid, None)

    def _worker(i: int) -> None:
        nonlocal processed
        worker_owner = f"{owner_base}#w{i}"
        while not stop.is_set():
            with processed_lock:
                if limit and processed >= limit:
                    break
            task = q.claim_next(
                owner=worker_owner,
                lease_seconds=lease_seconds,
                retry_errors=retry_errors,
            )
            if task is None:
                break
            try:
                with claimed_lock:
                    claimed[task.key] = worker_owner
                _run_one(task, worker_owner)
            except Exception as e:  # noqa: BLE001
                q.mark_error(task.key, f"{type(e).__name__}: {e}")
            finally:
                with claimed_lock:
                    claimed.pop(task.key, None)
                with processed_lock:
                    processed += 1

    threads = [threading.Thread(target=_worker, args=(i,), daemon=True) for i in range(workers)]
    try:
        for t in threads:
            t.start()
        while True:
            any_alive = False
            for t in threads:
                if t.is_alive():
                    any_alive = True
                    t.join(timeout=0.2)
            if not any_alive:
                break
            if stop.is_set() and shutdown_deadline[0] is not None and time.time() >= shutdown_deadline[0]:
                _abandon_claimed("terminated (shutdown deadline exceeded)")
                _kill_running(signal.SIGKILL)
                break

        if stop.is_set() and shutdown_deadline[0] is not None:
            while time.time() < shutdown_deadline[0]:
                _prune_finished_running()
                with running_lock:
                    if not running:
                        break
                time.sleep(0.05)
            _prune_finished_running()
            with running_lock:
                any_running = bool(running)
            if any_running:
                _kill_running(signal.SIGKILL)
    finally:
        signal.signal(signal.SIGTERM, old_term)
        signal.signal(signal.SIGINT, old_int)

    counts = q.counts()
    print(
        json.dumps(
            {"run_dir": str(run_dir), "worked": processed, "counts": counts.__dict__}, indent=2
        )
    )
    return 0


def cmd_queue_reconcile(args: argparse.Namespace) -> int:
    run_dir = Path(args.run_dir).resolve()
    q = Queue(run_dir=run_dir, db_path=_queue_db_path(run_dir))
    q.init()
    result = q.reconcile()
    counts = q.counts()
    print(
        json.dumps(
            {
                "run_dir": str(run_dir),
                "reconcile": result.__dict__,
                "counts": counts.__dict__,
            },
            indent=2,
        )
    )
    return 0


def cmd_queue_list(args: argparse.Namespace) -> int:
    run_dir = Path(args.run_dir).resolve()
    q = Queue(run_dir=run_dir, db_path=_queue_db_path(run_dir))
    q.init()
    status = str(args.status)
    limit = int(args.limit)
    rows = q.list_tasks(status=status, limit=limit)
    out = []
    for r in rows:
        out.append(
            {
                "key": r.key,
                "task_id": r.task_id,
                "status": r.status,
                "attempts": r.attempts,
                "lease_owner": r.lease_owner,
                "lease_expires_at": r.lease_expires_at,
                "last_error": r.last_error,
                "task_path": str(r.task_path),
                "artifact_path": str(r.artifact_path),
            }
        )
    print(json.dumps({"run_dir": str(run_dir), "tasks": out}, indent=2))
    return 0


def cmd_queue_index(args: argparse.Namespace) -> int:
    run_dir = Path(args.run_dir).resolve()
    q = Queue(run_dir=run_dir, db_path=_queue_db_path(run_dir))
    q.init()
    q.reconcile()
    indexed = q.index_artifacts(limit=int(args.limit))
    counts = q.counts()
    print(
        json.dumps(
            {
                "run_dir": str(run_dir),
                "indexed": indexed,
                "indexed_total": q.indexed_artifacts_count(),
                "counts": counts.__dict__,
            },
            indent=2,
        )
    )
    return 0


def cmd_watch(args: argparse.Namespace) -> int:
    run_dir = Path(args.run_dir).resolve()
    q = Queue(run_dir=run_dir, db_path=_queue_db_path(run_dir))
    q.init()
    interval = float(args.interval)
    once = bool(args.once)
    show_errors = bool(args.errors)

    while True:
        q.reconcile()
        counts = q.counts()
        payload: dict[str, Any] = {
            "t": _utc_now(),
            "run_dir": str(run_dir),
            "counts": counts.__dict__,
        }
        if show_errors:
            payload["errors"] = [
                {
                    "key": r.key,
                    "task_id": r.task_id,
                    "attempts": r.attempts,
                    "last_error": r.last_error,
                }
                for r in q.list_tasks(status="error", limit=10)
            ]
        print(json.dumps(payload))
        if once:
            break
        time.sleep(max(0.1, interval))
    return 0


def cmd_afk(args: argparse.Namespace) -> int:
    # Stage 3 foundation: "afk" is currently a thin alias for durable queue work.
    # Long-run, this will grow into a stricter worker-pool + monitoring loop.
    return cmd_queue_work(args)


def cmd_search(args: argparse.Namespace) -> int:
    world_path = Path(args.world).resolve()
    world = _read_json(world_path)

    search_seed: int
    if args.seed is not None:
        search_seed = int(args.seed)
    else:
        search_seed = int.from_bytes(os.urandom(8), "big") & ((1 << 63) - 1)
    random.seed(search_seed)
    
    if args.self_play:
        opponent = None
        opponent_id = "self"
    else:
        if not args.opponent:
            raise SystemExit("Search requires either --opponent or --self-play")
        opp_path = Path(args.opponent).resolve()
        opponent = _read_json(opp_path)
        opponent_id = opponent.get("id")

    trials = int(args.trials)
    top_n = int(args.top)
    metric = str(args.metric)

    results = []
    _ensure_engine_built()

    print(f"Searching {trials} trials ({args.mode}) against {opponent_id} in {world.get('id')}...")

    def _gen_random_mem1() -> dict[str, Any]:
        return {
            "family": "memory_one",
            "p0": random.random(),
            "p_cc": random.random(),
            "p_cd": random.random(),
            "p_dc": random.random(),
            "p_dd": random.random(),
        }

    def _gen_random_mem1_exit() -> dict[str, Any]:
        def _pair():
            c = random.random()
            d = random.random() * (1.0 - c)
            return c, d
        
        p0c, p0d = _pair()
        pccc, pccd = _pair()
        pcdc, pcdd = _pair()
        pdcc, pdcd = _pair()
        pddc, pddd = _pair()
        
        return {
            "family": "memory_one_exit",
            "p0_c": p0c, "p0_d": p0d,
            "p_cc_c": pccc, "p_cc_d": pccd,
            "p_cd_c": pcdc, "p_cd_d": pcdd,
            "p_dc_c": pdcc, "p_dc_d": pdcd,
            "p_dd_c": pddc, "p_dd_d": pddd,
        }

    def _gen_random_fsm(n_states: int) -> dict[str, Any]:
        states = []
        for i in range(n_states):
            states.append({
                "id": i,
                "output_c": random.random(),
                "trans_c": random.randint(0, n_states - 1),
                "trans_d": random.randint(0, n_states - 1),
                "trans_exit": 0,
            })
        return {
            "family": "fsm",
            "initial_state": 0,
            "states": states,
        }

    def _gen_candidate(prefix: str, idx: int) -> dict[str, Any]:
        if args.fsm_states:
            c = _gen_random_fsm(int(args.fsm_states))
        else:
            c = _gen_random_mem1_exit() if args.exit else _gen_random_mem1()
        c["id"] = f"{prefix}_{idx}"
        return c

    def _perturb_mem1(prev: dict[str, Any], sigma: float) -> dict[str, Any]:
        next_c = {"family": "memory_one"}
        for k in ["p0", "p_cc", "p_cd", "p_dc", "p_dd"]:
            next_c[k] = max(0.0, min(1.0, prev[k] + random.gauss(0, sigma)))
        return next_c

    def _perturb_mem1_exit(prev: dict[str, Any], sigma: float) -> dict[str, Any]:
        next_c = {"family": "memory_one_exit"}
        keys = [
            ("p0_c", "p0_d"), ("p_cc_c", "p_cc_d"), ("p_cd_c", "p_cd_d"),
            ("p_dc_c", "p_dc_d"), ("p_dd_c", "p_dd_d")
        ]
        for kc, kd in keys:
            c = max(0.0, min(1.0, prev[kc] + random.gauss(0, sigma)))
            d = max(0.0, min(1.0 - c, prev[kd] + random.gauss(0, sigma)))
            next_c[kc] = c
            next_c[kd] = d
        return next_c

    def _perturb_fsm(prev: dict[str, Any], sigma: float) -> dict[str, Any]:
        next_c = {
            "family": "fsm",
            "initial_state": prev["initial_state"],
            "states": []
        }
        n_states = len(prev["states"])
        for s in prev["states"]:
            new_s = s.copy()
            # Mutate output probability
            new_s["output_c"] = max(0.0, min(1.0, s["output_c"] + random.gauss(0, sigma)))
            
            # Occasionally mutate transitions
            if random.random() < sigma:
                new_s["trans_c"] = random.randint(0, n_states - 1)
            if random.random() < sigma:
                new_s["trans_d"] = random.randint(0, n_states - 1)
            
            next_c["states"].append(new_s)
        return next_c

    def _perturb(prev: dict[str, Any], idx: int, sigma: float) -> dict[str, Any]:
        if args.fsm_states:
            c = _perturb_fsm(prev, sigma)
        elif args.exit:
            c = _perturb_mem1_exit(prev, sigma)
        else:
            c = _perturb_mem1(prev, sigma)
        c["id"] = f"hill_climb_step_{idx}"
        return c

    def _run_candidate(cand: dict[str, Any], trial_idx: int) -> dict[str, Any]:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            task_path = tmpdir_path / "task.json"
            art_path = tmpdir_path / "artifact.json"

            task = {
                "schema_version": 1,
                "task_id": cand["id"],
                "world": world,
                "strategy_a": cand,
                "strategy_b": cand if args.self_play else opponent,
                "match_seed": int(world.get("seed", 0)) + trial_idx,
                "trace_rounds": 0,
            }
            task_path.write_text(json.dumps(task, indent=2), encoding="utf-8")
            _run_engine_task(task_path, art_path)
            art = _read_json(art_path)
            
            metric_map = {
                "avg_a": "avg_payoff_a",
                "avg_b": "avg_payoff_b",
                "coop_a": "coop_rate_a",
                "coop_b": "coop_rate_b",
                "mutual_c": "mutual_coop_rate",
            }
            stats = art.get("stats", {})
            if metric == "exploitation":
                val = stats.get("avg_payoff_a", 0.0) - stats.get("avg_payoff_b", 0.0)
            elif metric == "efficiency":
                val = stats.get("avg_payoff_a", 0.0) + stats.get("avg_payoff_b", 0.0)
            elif metric == "symmetry":
                diff = stats.get("payoff_diff", 0.0)
                val = 1.0 / (1.0 + diff)
            else:
                actual_key = metric_map.get(metric, metric)
                val = stats.get(actual_key, 0.0)
            return {"candidate": cand, "metric_value": val, "stats": stats}

    if args.mode == "random":
        for i in range(trials):
            candidate = _gen_candidate("random_cand", i)
            try:
                results.append(_run_candidate(candidate, i))
            except Exception as e:
                print(f"Trial {i} failed: {e}")
    elif args.mode == "hill_climb":
        # Start with a random seed
        current_cand = _gen_candidate("hill_climb_start", 0)
        try:
            best_res = _run_candidate(current_cand, 0)
            results.append(best_res)
            sigma = float(args.sigma)

            for i in range(1, trials):
                next_cand = _perturb(best_res["candidate"], i, sigma)
                res = _run_candidate(next_cand, i)
                if res["metric_value"] >= best_res["metric_value"]:
                    best_res = res
                    results.append(res)
        except Exception as e:
            print(f"Hill climb failed: {e}")
    else:
        raise SystemExit(f"Unknown search mode: {args.mode}")


    results.sort(key=lambda x: x["metric_value"], reverse=True)
    top_results = results[:top_n]

    try:
        world_rel = str(world_path.relative_to(REPO_ROOT))
    except ValueError:
        world_rel = str(world_path)

    opponent_path_rel: str | None = None
    opponent_hash: str | None = None
    if args.self_play:
        opponent_hash = None
    else:
        opp_path = Path(args.opponent).resolve()
        try:
            opponent_path_rel = str(opp_path.relative_to(REPO_ROOT))
        except ValueError:
            opponent_path_rel = str(opp_path)
        opponent_hash = hash_obj(opponent)

    payload = {
        "schema_version": 1,
        "kind": "search_result",
        "world_id": world.get("id"),
        "opponent_id": opponent_id,
        "world_path": world_rel,
        "world_hash": hash_obj(world),
        "opponent_path": opponent_path_rel,
        "opponent_hash": opponent_hash,
        "metric": metric,
        "mode": str(args.mode),
        "exit": bool(args.exit),
        "fsm_states": int(args.fsm_states) if args.fsm_states else None,
        "sigma": float(args.sigma),
        "search_seed": search_seed,
        "trials": trials,
        "top_n": top_n,
        "top": top_results,
    }

    _write_json_atomic(Path(args.out).resolve(), payload)
    if top_results:
        print(f"Best {metric} found: {top_results[0]['metric_value']}")
    return 0


def cmd_gauntlet(args: argparse.Namespace) -> int:
    cand_path = Path(args.candidate).resolve()
    candidate = _read_json(cand_path)
    world_path = Path(args.world).resolve()
    world = _read_json(world_path)

    spec_path_raw = Path(args.spec).expanduser()
    if spec_path_raw.is_absolute():
        spec_path = spec_path_raw.resolve()
    else:
        spec_path = (REPO_ROOT / spec_path_raw).resolve()
    spec = _read_json(spec_path)
    if not isinstance(spec, dict) or int(spec.get("schema_version", 0)) != 1:
        raise SystemExit(f"invalid GauntletSpec: {spec_path}")

    spec_hash = hash_obj(spec)

    opponents: list[tuple[str, dict[str, Any] | None, str | None]] = []

    for o in spec.get("opponents", []):
        if not isinstance(o, dict):
            continue
        name = o.get("name")
        if not isinstance(name, str) or not name:
            continue
        if o.get("self_play"):
            opponents.append((name, None, None))
            continue
        strategy_rel = o.get("strategy")
        if not isinstance(strategy_rel, str) or not strategy_rel:
            raise SystemExit(f"GauntletSpec opponent missing strategy path: {name}")
        strategy_path = (REPO_ROOT / strategy_rel).resolve()
        opp = _read_json(strategy_path)
        opponents.append((name, opp, str(Path(strategy_rel))))

    # Preferred terminology is "adversaries"; keep "vampires" for backward compatibility.
    group_specs: list[tuple[dict[str, Any], str]] = []
    adversaries = spec.get("adversaries")
    if isinstance(adversaries, dict):
        group_specs.append((adversaries, "adversary_"))
    vampires = spec.get("vampires")
    if isinstance(vampires, dict):
        group_specs.append((vampires, "vampire_"))

    for group_spec, default_prefix in group_specs:
        g_dir_rel = group_spec.get("dir")
        g_glob = group_spec.get("glob", "*.json")
        g_prefix = group_spec.get("prefix", default_prefix)
        if isinstance(g_dir_rel, str) and g_dir_rel:
            g_dir = (REPO_ROOT / g_dir_rel).resolve()
            if g_dir.exists():
                for gfile in sorted(g_dir.glob(str(g_glob))):
                    if not gfile.is_file():
                        continue
                    name = f"{g_prefix}{gfile.stem}"
                    try:
                        rel = str(gfile.relative_to(REPO_ROOT))
                    except ValueError:
                        rel = str(gfile)
                    opp = _read_json(gfile)
                    opponents.append((name, opp, rel))

    results = {}
    resolved_opponents = []
    _ensure_engine_built()

    print(f"Running Gauntlet for {candidate.get('id')}...")

    for name, opp, opp_rel_path in opponents:
        resolved: dict[str, Any] = {"name": name}
        if opp is None:
            resolved["self_play"] = True
            opp = candidate
        else:
            resolved["strategy_id"] = opp.get("id")
            resolved["strategy_hash"] = hash_obj(opp)
            resolved["strategy_path"] = opp_rel_path
        resolved_opponents.append(resolved)
        
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            task_path = tmpdir_path / "task.json"
            art_path = tmpdir_path / "artifact.json"

            task = {
                "schema_version": 1,
                "task_id": f"gauntlet_{name}",
                "world": world,
                "strategy_a": candidate,
                "strategy_b": opp,
                "match_seed": int(world.get("seed", 0)),
                "trace_rounds": 0,
            }
            task_path.write_text(json.dumps(task, indent=2), encoding="utf-8")
            _run_engine_task(task_path, art_path)
            art = _read_json(art_path)
            results[name] = art.get("stats", {})

    def _cmp(op: str, got: float, want: float) -> bool:
        if op in {"ge", ">="}:
            return got >= want
        if op in {"gt", ">"}:
            return got > want
        if op in {"le", "<="}:
            return got <= want
        if op in {"lt", "<"}:
            return got < want
        raise ValueError(f"unsupported gate op: {op}")

    gate_results = []
    gates = spec.get("gates", [])
    if not isinstance(gates, list) or not gates:
        raise SystemExit(f"GauntletSpec missing non-empty 'gates': {spec_path}")

    for g in gates:
        if not isinstance(g, dict):
            continue
        gate_name = g.get("name")
        stat = g.get("stat")
        op = g.get("op")
        want = g.get("value")
        if not isinstance(gate_name, str) or not gate_name:
            raise SystemExit("GauntletSpec gate missing name")
        if not isinstance(stat, str) or not stat:
            raise SystemExit(f"GauntletSpec gate missing stat: {gate_name}")
        if not isinstance(op, str) or not op:
            raise SystemExit(f"GauntletSpec gate missing op: {gate_name}")
        if not isinstance(want, (int, float)):
            raise SystemExit(f"GauntletSpec gate missing numeric value: {gate_name}")

        selected = []
        if isinstance(g.get("opponent"), str):
            selected = [g["opponent"]]
        elif isinstance(g.get("opponent_prefix"), str):
            prefix = g["opponent_prefix"]
            selected = sorted([k for k in results.keys() if k.startswith(prefix)])
        else:
            raise SystemExit(f"GauntletSpec gate missing opponent selector: {gate_name}")

        checked = []
        failures = []
        skipped = False

        if not selected:
            skipped = True
            passed_gate = True
        else:
            passed_gate = True
            for opp_name in selected:
                got_raw = results.get(opp_name, {}).get(stat)
                got = float(got_raw) if isinstance(got_raw, (int, float)) else None
                checked.append({"opponent": opp_name, "got": got})
                ok = got is not None and _cmp(op, got, float(want))
                if not ok:
                    passed_gate = False
                    failures.append({"opponent": opp_name, "got": got, "want": float(want), "op": op, "stat": stat})

        gate_results.append(
            {
                "name": gate_name,
                "passed": passed_gate,
                "skipped": skipped,
                "selector": {"opponent": g.get("opponent"), "opponent_prefix": g.get("opponent_prefix")},
                "stat": stat,
                "op": op,
                "value": float(want),
                "checked": checked,
                "failures": failures,
            }
        )

    passed = all(bool(gr.get("passed")) for gr in gate_results)

    try:
        spec_rel = str(spec_path.relative_to(REPO_ROOT))
    except ValueError:
        spec_rel = str(spec_path)

    payload = {
        "schema_version": 1,
        "kind": "gauntlet_result",
        "candidate_id": candidate.get("id"),
        "passed": passed,
        "world_id": world.get("id"),
        "world_hash": hash_obj(world),
        "gauntlet_spec_id": spec.get("id"),
        "gauntlet_spec_path": spec_rel,
        "gauntlet_spec_hash": spec_hash,
        "gauntlet_opponents": resolved_opponents,
        "gauntlet_opponents_hash": hash_obj(
            [
                {
                    "name": o.get("name"),
                    "self_play": o.get("self_play"),
                    "strategy_id": o.get("strategy_id"),
                    "strategy_hash": o.get("strategy_hash"),
                }
                for o in resolved_opponents
            ]
        ),
        "results": results,
        "gates": gate_results,
    }

    if args.out:
        _write_json_atomic(Path(args.out).resolve(), payload)
    
    print(json.dumps({"passed": passed, "candidate": candidate.get("id")}, indent=2))
    return 0 if passed else 1


def cmd_status(_args: argparse.Namespace) -> int:
    afk_dir = REPO_ROOT / "runs" / "afk_discovery"
    strategy_root = REPO_ROOT / "examples" / "strategies"
    candidate_dir = strategy_root / "candidates"
    if not candidate_dir.exists():
        candidate_dir = strategy_root / "discovered"
    adversary_dir = strategy_root / "adversaries"
    if not adversary_dir.exists():
        adversary_dir = strategy_root / "vampires"

    def _list_json(d: Path) -> list[Path]:
        if not d.exists():
            return []
        return sorted(d.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True)

    n_trials = len(list(afk_dir.glob("mission_*.json"))) if afk_dir.exists() else 0
    candidates = _list_json(candidate_dir)
    adversaries = _list_json(adversary_dir)

    print("--- Concord Lab Status ---")
    print(f"AFK Trials: {n_trials}")
    print(f"Candidates: {len(candidates)}")
    print(f"Adversaries: {len(adversaries)}")

    if candidates:
        print("\nRecent Candidates:")
        for s in candidates[:5]:
            print(f"  - {s.name}")

    if adversaries:
        print("\nRecent Adversaries:")
        for v in adversaries[:5]:
            print(f"  - {v.name}")

    return 0


def cmd_describe_fsm(args: argparse.Namespace) -> int:
    path = Path(args.path).resolve()
    strat = _read_json(path)
    if strat.get("family") != "fsm":
        print(f"Error: Strategy {strat.get('id')} is not an FSM.")
        return 1

    print(f"--- FSM Description: {strat.get('id')} ---")
    print(f"Initial State: {strat.get('initial_state')}")
    
    for s in strat.get("states", []):
        sid = s.get("id")
        out_c = s.get("output_c", 0.0)
        tc = s.get("trans_c")
        td = s.get("trans_d")
        te = s.get("trans_exit")
        
        tag = ""
        if out_c >= 0.9: tag = "[COOPERATIVE]"
        if out_c <= 0.1: tag = "[PUNITIVE]"
        
        print(f"State {sid}: P(C)={out_c:.2f} {tag}")
        print(f"  -> if Opp C: {tc}")
        print(f"  -> if Opp D: {td}")
        if te is not None: print(f"  -> if Opp Exit: {te}")

    return 0


def cmd_certify(args: argparse.Namespace) -> int:
    path_a = Path(args.a).resolve()
    path_b = Path(args.b).resolve()
    strat_a = _read_json(path_a)
    strat_b = _read_json(path_b)

    try:
        result = certify_memory_one_pair(strat_a, strat_b)
        print(json.dumps(result, indent=2))
    except CertifyError as e:
        print(f"Mathematical Error: {e}")
        return 1

    return 0


def cmd_holdout(args: argparse.Namespace) -> int:
    cand_path = Path(args.candidate).resolve()
    candidate = _read_json(cand_path)

    spec_path_raw = Path(args.spec).expanduser()
    if spec_path_raw.is_absolute():
        spec_path = spec_path_raw.resolve()
    else:
        spec_path = (REPO_ROOT / spec_path_raw).resolve()
    spec = _read_json(spec_path)
    if not isinstance(spec, dict) or int(spec.get("schema_version", 0)) != 1:
        raise SystemExit(f"invalid HoldoutSpec: {spec_path}")

    spec_hash = hash_obj(spec)
    candidate_hash = hash_obj(candidate)

    _ensure_engine_built()
    print(f"Running Holdout Validation for {candidate.get('id')}...")

    probes = spec.get("probes", [])
    if not isinstance(probes, list) or not probes:
        raise SystemExit(f"HoldoutSpec missing non-empty 'probes': {spec_path}")

    probe_results = []
    all_passed = True

    for p in probes:
        if not isinstance(p, dict):
            continue
        pid = p.get("id")
        probe_rel = p.get("probe")
        if not isinstance(pid, str) or not pid:
            raise SystemExit("HoldoutSpec probe missing id")
        if not isinstance(probe_rel, str) or not probe_rel:
            raise SystemExit(f"HoldoutSpec probe missing path: {pid}")

        probe_path = (REPO_ROOT / probe_rel).resolve()
        if not probe_path.exists():
            raise SystemExit(f"HoldoutSpec probe path missing: {probe_path}")

        probe = _read_json(probe_path)
        probe_source_hash = hash_obj(probe)

        inject = p.get("inject", {})
        if inject is None:
            inject = {}
        if not isinstance(inject, dict):
            raise SystemExit(f"HoldoutSpec probe inject must be an object: {pid}")

        inject_a = inject.get("strategy_a")
        inject_b = inject.get("strategy_b")
        if inject_a not in {None, "candidate"}:
            raise SystemExit(f"HoldoutSpec inject.strategy_a must be 'candidate' or null: {pid}")
        if inject_b not in {None, "candidate"}:
            raise SystemExit(f"HoldoutSpec inject.strategy_b must be 'candidate' or null: {pid}")

        matchups = probe.get("matchups", [])
        if not isinstance(matchups, list):
            matchups = []
        for m in matchups:
            if not isinstance(m, dict):
                continue
            if inject_a == "candidate" and m.get("strategy_a") is None:
                m["strategy_a"] = candidate
            if inject_b == "candidate" and m.get("strategy_b") is None:
                m["strategy_b"] = candidate

        probe_injected_hash = hash_obj(probe)

        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_probe = Path(tmpdir) / "probe.json"
            tmp_res = Path(tmpdir) / "res.json"
            tmp_probe.write_text(json.dumps(probe, indent=2), encoding="utf-8")

            cmd = [str(_engine_bin()), "run-probe", "--probe", str(tmp_probe), "--out", str(tmp_res)]
            subprocess.check_call(cmd, cwd=str(REPO_ROOT))
            res = _read_json(tmp_res)
            passed = bool(res.get("passed"))
            if not passed:
                all_passed = False
                print(f"  - FAILED Holdout: {pid}")
            else:
                print(f"  - PASSED Holdout: {pid}")
            probe_results.append(
                {
                    "id": pid,
                    "probe_path": probe_rel,
                    "probe_source_hash": probe_source_hash,
                    "probe_injected_hash": probe_injected_hash,
                    "passed": passed,
                    "result": res,
                }
            )

    try:
        spec_rel = str(spec_path.relative_to(REPO_ROOT))
    except ValueError:
        spec_rel = str(spec_path)

    payload = {
        "schema_version": 1,
        "kind": "holdout_result",
        "candidate_id": candidate.get("id"),
        "candidate_hash": candidate_hash,
        "holdout_passed": all_passed,
        "holdout_spec_id": spec.get("id"),
        "holdout_spec_path": spec_rel,
        "holdout_spec_hash": spec_hash,
        "probes": probe_results,
    }
    if args.out:
        _write_json_atomic(Path(args.out).resolve(), payload)
    print(json.dumps(payload, indent=2))
    return 0 if all_passed else 1


def cmd_ecology(args: argparse.Namespace) -> int:
    pool_dir = REPO_ROOT / "examples" / "strategies"
    candidate_dir = pool_dir / "candidates"
    discovered_dir = pool_dir / "discovered"
    adversary_dir = pool_dir / "adversaries"
    vampire_dir = pool_dir / "vampires"
    world_path = Path(args.world).resolve()
    world = _read_json(world_path)

    # 1. Build the Pool
    pool_by_id: dict[str, dict[str, Any]] = {}

    def _add_pool_dir(d: Path) -> None:
        if not d.exists():
            return
        for p in d.glob("*.json"):
            obj = _read_json(p)
            sid = str(obj.get("id", p.stem))
            pool_by_id[sid] = obj

    _add_pool_dir(candidate_dir)
    _add_pool_dir(discovered_dir)  # backward-compatible location
    _add_pool_dir(adversary_dir)
    _add_pool_dir(vampire_dir)  # backward-compatible location
    _add_pool_dir(pool_dir)  # baseline strategies at root

    pool = list(pool_by_id.values())

    if not pool:
        print("Error: Strategy pool is empty.")
        return 1

    n_agents = len(pool)
    generations = int(args.generations)
    
    # Simple Wright-Fisher-like population dynamics
    # We maintain a population vector: how many of each strategy exists.
    pop = {s["id"]: 1.0 / n_agents for s in pool}

    _ensure_engine_built()
    print(f"Simulating ecology over {generations} generations with {n_agents} types...")

    for g in range(generations):
        payoffs = {s["id"]: 0.0 for s in pool}
        # Round Robin (weighted by frequency)
        for i, s1 in enumerate(pool):
            for j, s2 in enumerate(pool):
                freq_pair = pop[s1["id"]] * pop[s2["id"]]
                if freq_pair <= 0: continue
                
                with tempfile.TemporaryDirectory() as tmpdir:
                    task_path = Path(tmpdir) / "task.json"
                    art_path = Path(tmpdir) / "art.json"
                    task = {
                        "schema_version": 1, "task_id": "eco", "world": world,
                        "strategy_a": s1, "strategy_b": s2, "match_seed": g + i + j,
                    }
                    task_path.write_text(json.dumps(task), encoding="utf-8")
                    _run_engine_task(task_path, art_path)
                    art = _read_json(art_path)
                    stats = art.get("stats", {})
                    payoffs[s1["id"]] += stats.get("avg_payoff_a", 0.0) * pop[s2["id"]]

        # Reproduction (Selection)
        total_fit = sum(payoffs.values())
        if total_fit <= 0: break
        
        new_pop = {}
        for sid in pop:
            # Replicator Equation: new_freq = old_freq * (fitness / avg_fitness)
            new_pop[sid] = pop[sid] * (payoffs[sid] / (total_fit / n_agents))
        
        # Normalize
        s = sum(new_pop.values())
        pop = {sid: val / s for sid, val in new_pop.items()}
        
        # Print top 3 frequencies
        top = sorted(pop.items(), key=lambda x: x[1], reverse=True)[:3]
        print(f"Gen {g}: " + ", ".join([f"{sid}: {f:.2f}" for sid, f in top]))

    return 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="grlab")
    sub = p.add_subparsers(dest="cmd", required=True)

    d = sub.add_parser("doctor", help="print environment info")
    d.set_defaults(func=cmd_doctor)

    r = sub.add_parser("run", help="run an experiment (resumable)")
    r.add_argument("experiment", help="path to experiment JSON")
    r.add_argument("--limit", type=int, default=0, help="run only the first N tasks (debug)")
    r.add_argument("--run-id", default="", help="explicit run id (folder name)")
    r.add_argument(
        "--plan-only",
        action="store_true",
        help="write tasks + manifest but do not execute",
    )
    r.add_argument(
        "--enqueue",
        action="store_true",
        help="also import tasks into queue.sqlite3",
    )
    r.set_defaults(func=cmd_run)

    rs = sub.add_parser("resume", help="resume a partially-completed run directory")
    rs.add_argument("run_dir", help="path to runs/<run_id>")
    rs.add_argument("--limit", type=int, default=0, help="run only the first N missing tasks (debug)")
    rs.set_defaults(func=cmd_resume)

    v = sub.add_parser("validate", help="validate a run directory for consistency")
    v.add_argument("run_dir", help="path to runs/<run_id>")
    v.add_argument("--check-queue", action="store_true", help="also validate queue.sqlite3")
    v.add_argument(
        "--check-definitions",
        action="store_true",
        help="also verify definition sources exist and hashes match",
    )
    v.set_defaults(func=cmd_validate)

    ver = sub.add_parser("verify", help="verify attestation for a run dir or export tarball")
    ver.add_argument("target", help="path to runs/<run_id> or bundle.tar.gz")
    ver.add_argument(
        "--check-definitions-hash",
        action="store_true",
        help="recompute definitions_hash from manifest definitions and compare",
    )
    ver.set_defaults(func=cmd_verify)

    rep = sub.add_parser("report", help="summarize a run into report.json")
    rep.add_argument("run_dir", help="path to runs/<run_id>")
    rep.add_argument(
        "--use-db",
        action="store_true",
        help="use queue.sqlite3 artifact index for reporting (builds it if needed)",
    )
    rep.set_defaults(func=cmd_report)

    rep_html = sub.add_parser("report-html", help="render report.json as a static HTML page")
    rep_html.add_argument("run_dir", help="path to runs/<run_id>")
    rep_html.add_argument("--out", default="", help="output html path (default: runs/<id>/report.html)")
    rep_html.add_argument(
        "--use-db",
        action="store_true",
        help="use queue.sqlite3 artifact index for reporting (builds it if needed)",
    )
    rep_html.add_argument(
        "--refresh",
        action="store_true",
        help="rebuild report.json even if it exists",
    )
    rep_html.add_argument("--title", default="", help="HTML page title")
    rep_html.set_defaults(func=cmd_report_html)

    dm = sub.add_parser(
        "diff-match", help="diff two Stage-1 match artifacts (drift diagnosis)"
    )
    dm.add_argument("--a", required=True, help="path to match artifact A")
    dm.add_argument("--b", required=True, help="path to match artifact B")
    dm.add_argument("--out", required=True, help="output diff artifact path")
    dm.add_argument("--id", default="diff_match", help="diff id")
    dm.add_argument("--pretty", action="store_true", help="pretty-print JSON output")
    dm.set_defaults(func=cmd_diff_match)

    tr = sub.add_parser("trace", help="trace tools (currently supports --diff)")
    tr.add_argument("--diff", action="store_true", help="diff two match artifacts")
    tr.add_argument("--a", default="", help="path to match artifact A (for --diff)")
    tr.add_argument("--b", default="", help="path to match artifact B (for --diff)")
    tr.add_argument("--run-a", default="", help="path to runs/<run_id> (A)")
    tr.add_argument("--run-b", default="", help="path to runs/<run_id> (B)")
    tr.add_argument("--task-id", default="", help="task_id to diff (requires --run-a/--run-b)")
    tr.add_argument("--out", default="", help="optional diff artifact output path")
    tr.add_argument("--id", default="trace_diff", help="diff id")
    tr.add_argument("--pretty", action="store_true", help="pretty-print JSON output")
    tr.set_defaults(func=cmd_trace)

    cmp = sub.add_parser("compare", help="compare two runs (definition-aware)")
    cmp.add_argument("run_a", help="path to runs/<run_id> (A)")
    cmp.add_argument("run_b", help="path to runs/<run_id> (B)")
    cmp.add_argument("--metric", default="avg_a", help="metric for top deltas")
    cmp.add_argument("--top", type=int, default=10, help="top N task deltas to show")
    cmp.add_argument(
        "--use-db",
        action="store_true",
        help="build reports via queue.sqlite3 artifact index (if report.json missing/refresh)",
    )
    cmp.add_argument(
        "--refresh",
        action="store_true",
        help="rebuild report.json for both runs before comparing",
    )
    cmp.add_argument("--out", default="", help="optional output JSON path")
    cmp.set_defaults(func=cmd_compare)

    repro = sub.add_parser("reproduce", help="rerun a task and diff against prior artifact")
    repro.add_argument("run_dir", help="path to runs/<run_id>")
    repro.add_argument("--task-id", default="", help="task_id to reproduce")
    repro.add_argument("--key", default="", help="task key to reproduce")
    repro.add_argument("--id", default="reproduce_diff", help="diff id")
    repro.add_argument("--out", default="", help="optional output JSON path")
    repro.set_defaults(func=cmd_reproduce)

    qk = sub.add_parser("quick", help="run one match without creating a full run dir")
    qk.add_argument("--world", required=True, help="path to world JSON")
    qk.add_argument("--strategy-a", required=True, help="path to strategy JSON (A)")
    qk.add_argument("--strategy-b", required=True, help="path to strategy JSON (B)")
    qk.add_argument("--match-seed", type=int, required=True, help="match seed")
    qk.add_argument("--trace-rounds", type=int, default=0, help="trace rounds (0 disables)")
    qk.add_argument("--task-id", default="quick", help="task id")
    qk.add_argument("--out", required=True, help="output artifact path")
    qk.set_defaults(func=cmd_quick)

    red = sub.add_parser("redact", help="create a redacted copy of a run directory")
    red.add_argument("run_dir", help="path to runs/<run_id>")
    red.add_argument("--out-dir", required=True, help="output directory path")
    red.add_argument(
        "--public",
        action="store_true",
        help="public-safe redaction (strips traces and tasks)",
    )
    red.add_argument(
        "--denylist",
        default=str(REPO_ROOT / "policy" / "public_export_denylist.json"),
        help="path to public export denylist JSON (only applies to --public)",
    )
    red.add_argument(
        "--no-denylist",
        action="store_true",
        help="disable denylist checks (only applies to --public)",
    )
    red.add_argument(
        "--allow-sensitive",
        action="store_true",
        help="override denylist blocks (only applies to --public)",
    )
    red.add_argument("--use-db", action="store_true", help="build report via queue.sqlite3 index")
    red.set_defaults(func=cmd_redact)

    exp = sub.add_parser("export", help="export a run as a bundle (tar.gz)")
    exp.add_argument("run_dir", help="path to runs/<run_id>")
    exp.add_argument("--out", required=True, help="output tar.gz path")
    exp.add_argument(
        "--public",
        action="store_true",
        help="public-safe export (strips traces and tasks)",
    )
    exp.add_argument(
        "--denylist",
        default=str(REPO_ROOT / "policy" / "public_export_denylist.json"),
        help="path to public export denylist JSON (only applies to --public)",
    )
    exp.add_argument(
        "--no-denylist",
        action="store_true",
        help="disable denylist checks (only applies to --public)",
    )
    exp.add_argument(
        "--allow-sensitive",
        action="store_true",
        help="override denylist blocks (only applies to --public)",
    )
    exp.add_argument(
        "--internal",
        action="store_true",
        help="internal export (includes tasks, queue db, and full artifacts)",
    )
    exp.add_argument("--use-db", action="store_true", help="build report via queue.sqlite3 index")
    exp.set_defaults(func=cmd_export)

    at = sub.add_parser("attest", help="write a small provenance attestation for a run dir")
    at.add_argument("run_dir", help="path to runs/<run_id>")
    at.add_argument("--out", default="", help="optional output JSON path")
    at.add_argument(
        "--include-queue-db",
        action="store_true",
        help="include queue.sqlite3 sha256 if present",
    )
    at.add_argument(
        "--include-artifacts",
        action="store_true",
        help="include a stable sha256 over artifacts/* file hashes",
    )
    at.set_defaults(func=cmd_attest)

    fr = sub.add_parser("frontier", help="compute a simple 2D Pareto frontier over strategies")
    fr.add_argument("run_dir", help="path to runs/<run_id>")
    fr.add_argument("--x", default="payoff", help="x metric: payoff|coop|mutual_c")
    fr.add_argument("--y", default="mutual_c", help="y metric: payoff|coop|mutual_c")
    fr.add_argument("--min-games", type=int, default=1, help="min games per strategy")
    fr.add_argument("--top", type=int, default=0, help="keep only top N frontier points (0=all)")
    fr.add_argument("--use-db", action="store_true", help="build from queue.sqlite3 index")
    fr.add_argument(
        "--refresh",
        action="store_true",
        help="rebuild and write report.json before computing",
    )
    fr.add_argument("--out", default="", help="optional output JSON path")
    fr.set_defaults(func=cmd_frontier)

    dd = sub.add_parser("defdiff", help="diff run definitions (experiment/world/strategies)")
    dd.add_argument("run_a", help="path to runs/<run_id> (A)")
    dd.add_argument("run_b", help="path to runs/<run_id> (B)")
    dd.add_argument("--out", default="", help="optional output JSON path")
    dd.set_defaults(func=cmd_defdiff)

    search = sub.add_parser("search", help="random search for strategies against an opponent")
    search.add_argument("--world", required=True, help="path to world JSON")
    search.add_argument("--opponent", help="path to opponent strategy JSON")
    search.add_argument("--self-play", action="store_true", help="search for best self-play strategy")
    search.add_argument("--trials", type=int, default=100, help="number of random trials")
    search.add_argument("--top", type=int, default=5, help="number of top strategies to keep")
    search.add_argument("--metric", default="avg_a", help="metric: avg_a|avg_b|coop_a|coop_b|mutual_c")
    search.add_argument("--mode", default="random", help="search mode: random|hill_climb")
    search.add_argument("--exit", action="store_true", help="search in MemoryOneExit space")
    search.add_argument("--fsm-states", type=int, help="search in FSM space with N states")
    search.add_argument("--sigma", type=float, default=0.05, help="perturbation sigma for hill_climb")
    search.add_argument("--seed", type=int, help="seed for the search itself")
    search.add_argument("--out", required=True, help="output JSON path for search results")
    search.set_defaults(func=cmd_search)

    gauntlet = sub.add_parser("gauntlet", help="evaluate a strategy against a suite of baselines")
    gauntlet.add_argument("--candidate", required=True, help="path to candidate strategy JSON")
    gauntlet.add_argument("--world", required=True, help="path to world JSON")
    gauntlet.add_argument(
        "--spec",
        default="examples/gauntlet/gauntlet_v2.json",
        help="path to GauntletSpec JSON (relative to repo root if not absolute)",
    )
    gauntlet.add_argument("--out", default="", help="optional output JSON path")
    gauntlet.set_defaults(func=cmd_gauntlet)

    stat = sub.add_parser("status", help="show summary of lab discovery progress")
    stat.set_defaults(func=cmd_status)

    hold = sub.add_parser("holdout", help="evaluate a strategy against a holdout suite")
    hold.add_argument("--candidate", required=True, help="path to candidate strategy JSON")
    hold.add_argument(
        "--spec",
        default="examples/holdouts/holdout_v1.json",
        help="path to HoldoutSpec JSON (relative to repo root if not absolute)",
    )
    hold.add_argument("--out", default="", help="optional output JSON path")
    hold.set_defaults(func=cmd_holdout)

    eco = sub.add_parser("ecology", help="simulate population dynamics of discovered strategies")
    eco.add_argument("--world", required=True, help="path to world JSON")
    eco.add_argument("--generations", type=int, default=10, help="number of evolutionary steps")
    eco.set_defaults(func=cmd_ecology)

    dfsm = sub.add_parser("describe-fsm", help="print a human-readable summary of an FSM strategy")
    dfsm.add_argument("path", help="path to FSM strategy JSON")
    dfsm.set_defaults(func=cmd_describe_fsm)

    cert = sub.add_parser(
        "certify",
        help="compute analytic stationary payoffs for a memory_one strategy pair",
    )
    cert.add_argument("--a", required=True, help="path to strategy A JSON (memory_one)")
    cert.add_argument("--b", required=True, help="path to strategy B JSON (memory_one)")
    cert.set_defaults(func=cmd_certify)

    qi = sub.add_parser("queue-init", help="initialize durable SQLite queue in a run dir")
    qi.add_argument("run_dir", help="path to runs/<run_id>")
    qi.set_defaults(func=cmd_queue_init)

    qim = sub.add_parser(
        "queue-import", help="import tasks from manifest.json into the queue"
    )
    qim.add_argument("run_dir", help="path to runs/<run_id>")
    qim.add_argument("--max-attempts", type=int, default=0, help="per-task max attempts")
    qim.add_argument(
        "--retry-backoff-seconds",
        type=int,
        default=0,
        help="seconds to wait before retrying an error task",
    )
    qim.set_defaults(func=cmd_queue_import)

    qs = sub.add_parser("queue-status", help="print queue status counts")
    qs.add_argument("run_dir", help="path to runs/<run_id>")
    qs.set_defaults(func=cmd_queue_status)

    qre = sub.add_parser("queue-reset-errors", help="reset error tasks back to pending")
    qre.add_argument("run_dir", help="path to runs/<run_id>")
    qre.add_argument("--include-dead", action="store_true", help="also reset dead tasks")
    qre.set_defaults(func=cmd_queue_reset_errors)

    qw = sub.add_parser("queue-work", help="run tasks from the queue (single-worker loop)")
    qw.add_argument("run_dir", help="path to runs/<run_id>")
    qw.add_argument("--owner", default="", help="lease owner tag (default: pid:<pid>)")
    qw.add_argument("--lease-seconds", type=int, default=600, help="lease TTL seconds")
    qw.add_argument(
        "--heartbeat-seconds",
        type=int,
        default=0,
        help="lease renewal interval seconds (default: derived from lease)",
    )
    qw.add_argument("--workers", type=int, default=1, help="number of worker threads")
    qw.add_argument(
        "--retry-errors",
        action="store_true",
        help="also process retry-eligible error tasks when their backoff expires",
    )
    qw.add_argument("--max-attempts", type=int, default=0, help="per-task max attempts")
    qw.add_argument(
        "--retry-backoff-seconds",
        type=int,
        default=0,
        help="seconds to wait before retrying an error task",
    )
    qw.add_argument(
        "--task-timeout-seconds",
        type=int,
        default=0,
        help="kill and mark error if a task exceeds this wall time (0 disables)",
    )
    qw.add_argument("--limit", type=int, default=0, help="process at most N tasks")
    qw.set_defaults(func=cmd_queue_work)

    qrc = sub.add_parser(
        "queue-reconcile", help="reconcile queue state with filesystem artifacts"
    )
    qrc.add_argument("run_dir", help="path to runs/<run_id>")
    qrc.set_defaults(func=cmd_queue_reconcile)

    ql = sub.add_parser("queue-list", help="list tasks by status")
    ql.add_argument("run_dir", help="path to runs/<run_id>")
    ql.add_argument(
        "--status", default="error", help="status to list (pending|running|done|error)"
    )
    ql.add_argument("--limit", type=int, default=50, help="max rows")
    ql.set_defaults(func=cmd_queue_list)

    qidx = sub.add_parser(
        "queue-index", help="index artifact summaries into queue.sqlite3"
    )
    qidx.add_argument("run_dir", help="path to runs/<run_id>")
    qidx.add_argument("--limit", type=int, default=0, help="index at most N artifacts")
    qidx.set_defaults(func=cmd_queue_index)

    w = sub.add_parser("watch", help="watch queue status (JSON lines)")
    w.add_argument("run_dir", help="path to runs/<run_id>")
    w.add_argument("--interval", type=float, default=2.0, help="refresh interval seconds")
    w.add_argument("--once", action="store_true", help="print once then exit")
    w.add_argument("--errors", action="store_true", help="include top errors")
    w.set_defaults(func=cmd_watch)

    afk = sub.add_parser("afk", help="durable queue worker loop (kill/resume friendly)")
    afk.add_argument("run_dir", help="path to runs/<run_id>")
    afk.add_argument("--owner", default="", help="lease owner tag (default: pid:<pid>)")
    afk.add_argument("--lease-seconds", type=int, default=600, help="lease TTL seconds")
    afk.add_argument(
        "--heartbeat-seconds",
        type=int,
        default=0,
        help="lease renewal interval seconds (default: derived from lease)",
    )
    afk.add_argument("--workers", type=int, default=1, help="number of worker threads")
    afk.add_argument(
        "--retry-errors",
        action="store_true",
        help="also process retry-eligible error tasks when their backoff expires",
    )
    afk.add_argument("--max-attempts", type=int, default=0, help="per-task max attempts")
    afk.add_argument(
        "--retry-backoff-seconds",
        type=int,
        default=0,
        help="seconds to wait before retrying an error task",
    )
    afk.add_argument(
        "--task-timeout-seconds",
        type=int,
        default=0,
        help="kill and mark error if a task exceeds this wall time (0 disables)",
    )
    afk.add_argument("--limit", type=int, default=0, help="process at most N tasks")
    afk.set_defaults(func=cmd_afk)

    args = p.parse_args(argv)
    if getattr(args, "limit", 0) == 0:
        args.limit = None
    return int(args.func(args))
