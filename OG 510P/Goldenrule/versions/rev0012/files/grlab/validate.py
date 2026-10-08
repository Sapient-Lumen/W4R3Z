import json
import sqlite3
from pathlib import Path
from typing import Any

from grlab.defdiff import compute_definitions_hash
from grlab.hashing import hash_obj


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _definition_base(manifest: dict[str, Any], run_dir: Path) -> Path:
    exp = manifest.get("experiment")
    if isinstance(exp, str) and exp:
        exp_path = Path(exp).expanduser()
        if exp_path.exists():
            return exp_path.resolve().parent
    return run_dir


def validate_run_dir(
    run_dir: Path, check_queue: bool = False, check_definitions: bool = False
) -> dict[str, Any]:
    problems: list[str] = []
    manifest_path = run_dir / "manifest.json"
    if not manifest_path.exists():
        return {"ok": False, "problems": ["missing manifest.json"]}

    try:
        manifest = _read_json(manifest_path)
    except Exception as e:  # noqa: BLE001
        return {"ok": False, "problems": [f"manifest.json parse error: {type(e).__name__}: {e}"]}

    schema_version = manifest.get("schema_version", 1)
    if not isinstance(schema_version, int):
        problems.append("manifest.schema_version must be an integer")
        schema_version = 1

    if schema_version >= 2:
        exp_hash = manifest.get("experiment_hash")
        if not isinstance(exp_hash, str) or not exp_hash:
            problems.append("manifest.experiment_hash missing/invalid (schema_version >= 2)")

        defs = manifest.get("definitions")
        if not isinstance(defs, dict):
            problems.append("manifest.definitions missing/invalid (schema_version >= 2)")
        else:
            w = defs.get("world")
            if not isinstance(w, dict) or not isinstance(w.get("hash"), str) or not w.get("hash"):
                problems.append("manifest.definitions.world.hash missing/invalid (schema_version >= 2)")

            rows = defs.get("strategies")
            if not isinstance(rows, list):
                problems.append(
                    "manifest.definitions.strategies missing/invalid (schema_version >= 2)"
                )
            else:
                seen: set[str] = set()
                for r in rows:
                    if not isinstance(r, dict):
                        problems.append(
                            "manifest.definitions.strategies contains non-object entry"
                        )
                        continue
                    sid = r.get("id")
                    sh = r.get("hash")
                    if not isinstance(sid, str) or not sid:
                        problems.append(
                            "manifest.definitions.strategies entry missing/invalid id"
                        )
                        continue
                    if sid in seen:
                        problems.append(
                            f"manifest.definitions.strategies contains duplicate id {sid}"
                        )
                    seen.add(sid)
                    if not isinstance(sh, str) or not sh:
                        problems.append(
                            f"manifest.definitions.strategies[{sid}].hash missing/invalid"
                        )

    if schema_version >= 3:
        def_hash = manifest.get("definitions_hash")
        if not isinstance(def_hash, str) or not def_hash:
            problems.append("manifest.definitions_hash missing/invalid (schema_version >= 3)")
        else:
            computed = compute_definitions_hash(manifest)
            if computed is None:
                problems.append("manifest.definitions_hash cannot be recomputed (schema_version >= 3)")
            elif computed != def_hash:
                problems.append(
                    f"manifest.definitions_hash mismatch: expected {computed}, got {def_hash}"
                )

    if check_definitions and schema_version >= 2:
        defs = manifest.get("definitions")
        if isinstance(defs, dict):
            base = _definition_base(manifest, run_dir=run_dir)

            w = defs.get("world")
            if isinstance(w, dict):
                w_source = w.get("source")
                w_hash = w.get("hash")
                if isinstance(w_source, str) and w_source and w_source != "<inline>":
                    world_path = (base / w_source).resolve()
                    if not world_path.exists():
                        problems.append(f"missing world definition source: {w_source}")
                    else:
                        try:
                            world_obj = _read_json(world_path)
                            computed = hash_obj(world_obj)
                            if isinstance(w_hash, str) and w_hash and computed != w_hash:
                                problems.append(
                                    f"world definition hash mismatch for source {w_source}: expected {w_hash}, got {computed}"
                                )
                            if isinstance(world_obj, dict):
                                wid_manifest = w.get("id")
                                wid_loaded = world_obj.get("id")
                                if (
                                    isinstance(wid_manifest, str)
                                    and isinstance(wid_loaded, str)
                                    and wid_manifest
                                    and wid_loaded
                                    and wid_manifest != wid_loaded
                                ):
                                    problems.append(
                                        f"world definition id mismatch for source {w_source}: expected {wid_manifest}, got {wid_loaded}"
                                    )
                        except Exception as e:  # noqa: BLE001
                            problems.append(
                                f"world definition source parse error {w_source}: {type(e).__name__}: {e}"
                            )

            rows = defs.get("strategies")
            if isinstance(rows, list):
                for r in rows:
                    if not isinstance(r, dict):
                        continue
                    sid = r.get("id")
                    src = r.get("source")
                    sh = r.get("hash")
                    if not isinstance(sid, str) or not sid:
                        continue
                    if not isinstance(src, str) or not src or src == "<inline>":
                        continue
                    strat_path = (base / src).resolve()
                    if not strat_path.exists():
                        problems.append(f"missing strategy definition source for id {sid}: {src}")
                        continue
                    try:
                        s_obj = _read_json(strat_path)
                        computed = hash_obj(s_obj)
                        if isinstance(sh, str) and sh and computed != sh:
                            problems.append(
                                f"strategy definition hash mismatch for id {sid} source {src}: expected {sh}, got {computed}"
                            )
                        if isinstance(s_obj, dict):
                            sid_loaded = s_obj.get("id")
                            if (
                                isinstance(sid_loaded, str)
                                and sid_loaded
                                and sid != sid_loaded
                            ):
                                problems.append(
                                    f"strategy definition id mismatch for id {sid} source {src}: got {sid_loaded}"
                                )
                    except Exception as e:  # noqa: BLE001
                        problems.append(
                            f"strategy definition source parse error for id {sid} {src}: {type(e).__name__}: {e}"
                        )

    tasks = manifest.get("tasks", [])
    if not isinstance(tasks, list):
        problems.append("manifest.tasks must be a list")
        tasks = []

    keys: set[str] = set()
    missing_tasks = 0
    missing_artifacts = 0
    for t in tasks:
        if not isinstance(t, dict):
            problems.append("manifest.tasks contains non-object entry")
            continue
        key = str(t.get("key", ""))
        if not key:
            problems.append("task entry missing key")
            continue
        if key in keys:
            problems.append(f"duplicate task key {key}")
        keys.add(key)

        task_path = t.get("task_path")
        artifact_path = t.get("artifact_path")
        if not isinstance(task_path, str) or not task_path:
            problems.append(f"task {key} missing task_path")
            continue
        if not isinstance(artifact_path, str) or not artifact_path:
            problems.append(f"task {key} missing artifact_path")
            continue

        abs_task = (run_dir / task_path).resolve()
        abs_art = (run_dir / artifact_path).resolve()
        if not abs_task.exists():
            missing_tasks += 1
        if not abs_art.exists():
            missing_artifacts += 1

    queue_summary: dict[str, Any] | None = None
    if check_queue:
        db_path = run_dir / "queue.sqlite3"
        if not db_path.exists():
            problems.append("missing queue.sqlite3")
        else:
            try:
                with sqlite3.connect(str(db_path)) as con:
                    task_count = int(con.execute("SELECT COUNT(*) FROM tasks").fetchone()[0])
                    artifact_count = int(
                        con.execute("SELECT COUNT(*) FROM artifacts").fetchone()[0]
                    )
                    queue_summary = {
                        "tasks": task_count,
                        "artifacts": artifact_count,
                    }
                    if task_count and task_count != len(keys):
                        problems.append(
                            f"queue task count {task_count} != manifest task count {len(keys)} (run queue-import?)"
                        )
            except Exception as e:  # noqa: BLE001
                problems.append(f"queue.sqlite3 error: {type(e).__name__}: {e}")

    ok = len(problems) == 0
    out: dict[str, Any] = {
        "ok": ok,
        "schema_version": schema_version,
        "tasks_total": len(keys),
        "missing_task_files": missing_tasks,
        "missing_artifacts": missing_artifacts,
        "problems": problems,
    }
    if queue_summary is not None:
        out["queue"] = queue_summary
    return out
