from __future__ import annotations

import json
import tarfile
from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
from typing import Any

from grlab.defdiff import compute_definitions_hash


def _sha256_hex(b: bytes) -> str:
    return sha256(b).hexdigest()


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _read_bytes(path: Path) -> bytes:
    return path.read_bytes()


@dataclass(frozen=True)
class VerifyResult:
    ok: bool
    problems: list[str]


def _get_attestation_fields(att: dict[str, Any]) -> tuple[str | None, str | None, str | None, str | None]:
    manifest_sha256 = att.get("manifest_sha256")
    report_sha256 = att.get("report_sha256")
    queue_db_sha256 = att.get("queue_db_sha256")
    definitions_hash = att.get("definitions_hash")
    return (
        manifest_sha256 if isinstance(manifest_sha256, str) else None,
        report_sha256 if isinstance(report_sha256, str) else None,
        queue_db_sha256 if isinstance(queue_db_sha256, str) else None,
        definitions_hash if isinstance(definitions_hash, str) else None,
    )


def _att_artifacts_tree_sha256(att: dict[str, Any]) -> str | None:
    v = att.get("artifacts_tree_sha256")
    return v if isinstance(v, str) and v else None


def _artifacts_tree_sha256_dir(run_dir: Path) -> str | None:
    artifacts_dir = (run_dir / "artifacts").resolve()
    if not artifacts_dir.exists() or not artifacts_dir.is_dir():
        return None
    entries: list[tuple[str, str]] = []
    for p in sorted(artifacts_dir.rglob("*")):
        if p.is_dir():
            continue
        rel = p.relative_to(run_dir).as_posix()
        entries.append((rel, _sha256_hex(_read_bytes(p))))
    payload = json.dumps(entries, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return _sha256_hex(payload)


def verify_run_dir(
    run_dir: Path,
    attestation_path: Path | None = None,
    check_definitions_hash: bool = False,
) -> VerifyResult:
    run_dir = run_dir.resolve()
    problems: list[str] = []

    att_path = attestation_path.resolve() if attestation_path else (run_dir / "attestation.json")
    if not att_path.exists():
        return VerifyResult(ok=False, problems=[f"missing attestation.json at {att_path}"])

    try:
        att = _read_json(att_path)
    except Exception as e:  # noqa: BLE001
        return VerifyResult(ok=False, problems=[f"attestation parse error: {type(e).__name__}: {e}"])
    if not isinstance(att, dict):
        return VerifyResult(ok=False, problems=["attestation.json is not an object"])

    man_hash, rep_hash, q_hash, def_hash = _get_attestation_fields(att)
    art_tree_hash = _att_artifacts_tree_sha256(att)

    manifest_path = run_dir / "manifest.json"
    if man_hash is None:
        if manifest_path.exists():
            problems.append("attestation.manifest_sha256 missing but manifest.json exists")
    else:
        if not manifest_path.exists():
            problems.append("manifest.json missing but attestation.manifest_sha256 present")
        else:
            got = _sha256_hex(_read_bytes(manifest_path))
            if got != man_hash:
                problems.append(f"manifest sha256 mismatch: expected {man_hash}, got {got}")

    report_path = run_dir / "report.json"
    if rep_hash is None:
        if report_path.exists():
            problems.append("attestation.report_sha256 missing but report.json exists")
    else:
        if not report_path.exists():
            problems.append("report.json missing but attestation.report_sha256 present")
        else:
            got = _sha256_hex(_read_bytes(report_path))
            if got != rep_hash:
                problems.append(f"report sha256 mismatch: expected {rep_hash}, got {got}")

    queue_path = run_dir / "queue.sqlite3"
    if q_hash is None:
        # internal/public exports often omit or disable queue hashing; don't complain.
        pass
    else:
        if not queue_path.exists():
            problems.append("queue.sqlite3 missing but attestation.queue_db_sha256 present")
        else:
            got = _sha256_hex(_read_bytes(queue_path))
            if got != q_hash:
                problems.append(f"queue sqlite sha256 mismatch: expected {q_hash}, got {got}")

    if def_hash is not None and manifest_path.exists():
        try:
            manifest = _read_json(manifest_path)
            if isinstance(manifest, dict):
                mh = manifest.get("definitions_hash")
                if isinstance(mh, str) and mh and mh != def_hash:
                    problems.append(
                        f"definitions_hash mismatch: attestation {def_hash} != manifest {mh}"
                    )
                if check_definitions_hash:
                    computed = compute_definitions_hash(manifest)
                    if computed is None:
                        problems.append(
                            "cannot recompute definitions_hash from manifest (missing definitions?)"
                        )
                    elif isinstance(mh, str) and mh and computed != mh:
                        problems.append(
                            f"manifest definitions_hash mismatch: expected {computed}, got {mh}"
                        )
                    elif def_hash is not None and computed != def_hash:
                        problems.append(
                            f"attestation definitions_hash mismatch: expected {computed}, got {def_hash}"
                        )
        except Exception as e:  # noqa: BLE001
            problems.append(f"manifest.json parse error while checking definitions_hash: {type(e).__name__}: {e}")

    if art_tree_hash is not None:
        computed = _artifacts_tree_sha256_dir(run_dir)
        if computed is None:
            problems.append("attestation.artifacts_tree_sha256 present but artifacts/ is missing")
        elif computed != art_tree_hash:
            problems.append(
                f"artifacts_tree_sha256 mismatch: expected {art_tree_hash}, got {computed}"
            )

    ok = len(problems) == 0
    return VerifyResult(ok=ok, problems=problems)


def _tar_read_member_bytes(tf: tarfile.TarFile, name: str) -> bytes | None:
    try:
        m = tf.getmember(name)
    except KeyError:
        return None
    f = tf.extractfile(m)
    if f is None:
        return None
    return f.read()


def verify_tarball(tar_path: Path, check_definitions_hash: bool = False) -> VerifyResult:
    tar_path = tar_path.resolve()
    problems: list[str] = []
    if not tar_path.exists():
        return VerifyResult(ok=False, problems=[f"missing tarball: {tar_path}"])

    with tarfile.open(str(tar_path), "r:*") as tf:
        att_b = _tar_read_member_bytes(tf, "attestation.json")
        if att_b is None:
            return VerifyResult(ok=False, problems=["missing attestation.json in tarball"])
        try:
            att = json.loads(att_b.decode("utf-8"))
        except Exception as e:  # noqa: BLE001
            return VerifyResult(ok=False, problems=[f"attestation parse error: {type(e).__name__}: {e}"])
        if not isinstance(att, dict):
            return VerifyResult(ok=False, problems=["attestation.json is not an object"])

        man_hash, rep_hash, q_hash, def_hash = _get_attestation_fields(att)
        art_tree_hash = _att_artifacts_tree_sha256(att)

        manifest_b = _tar_read_member_bytes(tf, "manifest.json")
        if man_hash is None:
            if manifest_b is not None:
                problems.append("attestation.manifest_sha256 missing but manifest.json present")
        else:
            if manifest_b is None:
                problems.append("manifest.json missing but attestation.manifest_sha256 present")
            else:
                got = _sha256_hex(manifest_b)
                if got != man_hash:
                    problems.append(f"manifest sha256 mismatch: expected {man_hash}, got {got}")

        report_b = _tar_read_member_bytes(tf, "report.json")
        if rep_hash is None:
            if report_b is not None:
                problems.append("attestation.report_sha256 missing but report.json present")
        else:
            if report_b is None:
                problems.append("report.json missing but attestation.report_sha256 present")
            else:
                got = _sha256_hex(report_b)
                if got != rep_hash:
                    problems.append(f"report sha256 mismatch: expected {rep_hash}, got {got}")

        queue_b = _tar_read_member_bytes(tf, "queue.sqlite3")
        if q_hash is None:
            if queue_b is not None:
                # We don't require queue hashing on public exports.
                pass
        else:
            if queue_b is None:
                problems.append("queue.sqlite3 missing but attestation.queue_db_sha256 present")
            else:
                got = _sha256_hex(queue_b)
                if got != q_hash:
                    problems.append(f"queue sqlite sha256 mismatch: expected {q_hash}, got {got}")

        if def_hash is not None and manifest_b is not None:
            try:
                manifest = json.loads(manifest_b.decode("utf-8"))
                if isinstance(manifest, dict):
                    mh = manifest.get("definitions_hash")
                    if isinstance(mh, str) and mh and mh != def_hash:
                        problems.append(
                            f"definitions_hash mismatch: attestation {def_hash} != manifest {mh}"
                        )
                    if check_definitions_hash:
                        computed = compute_definitions_hash(manifest)
                        if computed is None:
                            problems.append(
                                "cannot recompute definitions_hash from manifest (missing definitions?)"
                            )
                        elif isinstance(mh, str) and mh and computed != mh:
                            problems.append(
                                f"manifest definitions_hash mismatch: expected {computed}, got {mh}"
                            )
                        elif def_hash is not None and computed != def_hash:
                            problems.append(
                                f"attestation definitions_hash mismatch: expected {computed}, got {def_hash}"
                            )
            except Exception as e:  # noqa: BLE001
                problems.append(
                    f"manifest.json parse error while checking definitions_hash: {type(e).__name__}: {e}"
                )

        # Optional consistency check: n_artifacts should match report rows length when report exists.
        if report_b is not None:
            try:
                report = json.loads(report_b.decode("utf-8"))
                if isinstance(report, dict):
                    rows = report.get("rows")
                    if isinstance(rows, list):
                        n = att.get("n_artifacts")
                        if isinstance(n, int) and n != len(rows):
                            problems.append(
                                f"n_artifacts mismatch: attestation {n} != report rows {len(rows)}"
                            )
            except Exception:
                pass

        if art_tree_hash is not None:
            entries: list[tuple[str, str]] = []
            for m in sorted(tf.getmembers(), key=lambda x: x.name):
                if not m.isfile():
                    continue
                if not m.name.startswith("artifacts/"):
                    continue
                b = _tar_read_member_bytes(tf, m.name)
                if b is None:
                    continue
                entries.append((m.name, _sha256_hex(b)))
            payload = json.dumps(entries, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
            computed = _sha256_hex(payload)
            if computed != art_tree_hash:
                problems.append(
                    f"artifacts_tree_sha256 mismatch: expected {art_tree_hash}, got {computed}"
                )

    ok = len(problems) == 0
    return VerifyResult(ok=ok, problems=problems)
