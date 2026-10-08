import json
import os
import sqlite3
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable


SCHEMA_VERSION = 2

DEFAULT_MAX_ATTEMPTS = 5
DEFAULT_RETRY_BACKOFF_SECONDS = 30


def _utc_now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _now_ts() -> float:
    return time.time()


def _parse_pid_owner(owner: str) -> int | None:
    if not owner.startswith("pid:"):
        return None
    rest = owner[len("pid:") :]
    digits: list[str] = []
    for ch in rest:
        if ch.isdigit():
            digits.append(ch)
        else:
            break
    if not digits:
        return None
    try:
        return int("".join(digits))
    except ValueError:
        return None


def _pid_alive(pid: int) -> bool:
    if pid <= 0:
        return False
    try:
        os.kill(pid, 0)
        return True
    except ProcessLookupError:
        return False
    except PermissionError:
        return True


def init_db(db_path: Path) -> None:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(str(db_path)) as con:
        con.execute("PRAGMA journal_mode=WAL")
        con.execute("PRAGMA foreign_keys=ON")
        con.execute(
            """
            CREATE TABLE IF NOT EXISTS meta (
              k TEXT PRIMARY KEY,
              v TEXT NOT NULL
            )
            """
        )
        con.execute(
            """
            CREATE TABLE IF NOT EXISTS tasks (
              key TEXT PRIMARY KEY,
              task_id TEXT NOT NULL,
              task_path TEXT NOT NULL,
              artifact_path TEXT NOT NULL,
              status TEXT NOT NULL,
              attempts INTEGER NOT NULL,
              max_attempts INTEGER NOT NULL,
              retry_backoff_seconds INTEGER NOT NULL,
              next_attempt_at REAL,
              last_error TEXT,
              lease_owner TEXT,
              lease_expires_at REAL,
              last_started_at REAL,
              last_finished_at REAL,
              last_duration_ms INTEGER,
              created_at TEXT NOT NULL,
              updated_at TEXT NOT NULL
            )
            """
        )
        con.execute(
            """
            CREATE TABLE IF NOT EXISTS artifacts (
              key TEXT PRIMARY KEY,
              artifact_path TEXT NOT NULL,
              artifact_hash TEXT NOT NULL,
              artifact_input_hash TEXT,
              engine_version TEXT,
              schema_version INTEGER,
              task_id TEXT,
              world_id TEXT,
              strategy_a_id TEXT,
              strategy_b_id TEXT,
              rounds INTEGER,
              avg_a REAL,
              avg_b REAL,
              coop_a REAL,
              coop_b REAL,
              mutual_c REAL,
              indexed_at TEXT NOT NULL,
              artifact_mtime REAL NOT NULL
            )
            """
        )
        con.execute("CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status)")
        con.execute(
            "CREATE INDEX IF NOT EXISTS idx_tasks_lease ON tasks(status, lease_expires_at)"
        )
        con.execute(
            "INSERT OR REPLACE INTO meta(k, v) VALUES(?, ?)",
            ("schema_version", str(SCHEMA_VERSION)),
        )
        con.execute(
            "INSERT OR REPLACE INTO meta(k, v) VALUES(?, COALESCE((SELECT v FROM meta WHERE k=?), ?))",
            ("default_max_attempts", "default_max_attempts", str(DEFAULT_MAX_ATTEMPTS)),
        )
        con.execute(
            "INSERT OR REPLACE INTO meta(k, v) VALUES(?, COALESCE((SELECT v FROM meta WHERE k=?), ?))",
            (
                "default_retry_backoff_seconds",
                "default_retry_backoff_seconds",
                str(DEFAULT_RETRY_BACKOFF_SECONDS),
            ),
        )

        cols = {r[1] for r in con.execute("PRAGMA table_info(tasks)")}
        # Best-effort migrations for older DBs.
        if "max_attempts" not in cols:
            con.execute(
                f"ALTER TABLE tasks ADD COLUMN max_attempts INTEGER NOT NULL DEFAULT {DEFAULT_MAX_ATTEMPTS}"
            )
        if "retry_backoff_seconds" not in cols:
            con.execute(
                f"ALTER TABLE tasks ADD COLUMN retry_backoff_seconds INTEGER NOT NULL DEFAULT {DEFAULT_RETRY_BACKOFF_SECONDS}"
            )
        if "next_attempt_at" not in cols:
            con.execute("ALTER TABLE tasks ADD COLUMN next_attempt_at REAL")
        if "last_started_at" not in cols:
            con.execute("ALTER TABLE tasks ADD COLUMN last_started_at REAL")
        if "last_finished_at" not in cols:
            con.execute("ALTER TABLE tasks ADD COLUMN last_finished_at REAL")
        if "last_duration_ms" not in cols:
            con.execute("ALTER TABLE tasks ADD COLUMN last_duration_ms INTEGER")


@dataclass(frozen=True)
class QueueCounts:
    pending: int
    running: int
    done: int
    error: int
    dead: int


@dataclass(frozen=True)
class ClaimedTask:
    key: str
    task_id: str
    task_path: Path
    artifact_path: Path


@dataclass(frozen=True)
class ReconcileResult:
    marked_done: int
    released_stale: int


@dataclass(frozen=True)
class ListedTask:
    key: str
    task_id: str
    task_path: Path
    artifact_path: Path
    status: str
    attempts: int
    last_error: str | None
    lease_owner: str | None
    lease_expires_at: float | None


class Queue:
    def __init__(self, run_dir: Path, db_path: Path) -> None:
        self.run_dir = run_dir
        self.db_path = db_path

    def init(self) -> None:
        init_db(self.db_path)

    def _connect(self) -> sqlite3.Connection:
        con = sqlite3.connect(str(self.db_path), isolation_level=None)
        con.execute("PRAGMA journal_mode=WAL")
        con.execute("PRAGMA foreign_keys=ON")
        return con

    def import_manifest(self, manifest: dict[str, Any]) -> int:
        now = _utc_now()
        max_attempts = int(
            manifest.get("queue_max_attempts", DEFAULT_MAX_ATTEMPTS) or DEFAULT_MAX_ATTEMPTS
        )
        retry_backoff_seconds = int(
            manifest.get("queue_retry_backoff_seconds", DEFAULT_RETRY_BACKOFF_SECONDS)
            or DEFAULT_RETRY_BACKOFF_SECONDS
        )
        rows: list[tuple[str, str, str, str, str, int, int, int, str]] = []

        for t in manifest.get("tasks", []):
            key = str(t["key"])
            task_id = str(t["task_id"])
            task_path = str(t["task_path"])
            artifact_path = str(t["artifact_path"])

            abs_art = (self.run_dir / artifact_path).resolve()
            status = "done" if abs_art.exists() else "pending"
            rows.append(
                (
                    key,
                    task_id,
                    task_path,
                    artifact_path,
                    status,
                    0,
                    max_attempts,
                    retry_backoff_seconds,
                    now,
                )
            )

        with self._connect() as con:
            con.execute("BEGIN IMMEDIATE")
            inserted = 0
            for (
                key,
                task_id,
                task_path,
                artifact_path,
                status,
                attempts,
                max_attempts,
                retry_backoff_seconds,
                ts,
            ) in rows:
                cur = con.execute(
                    """
                    INSERT OR IGNORE INTO tasks(
                      key, task_id, task_path, artifact_path,
                      status, attempts, max_attempts, retry_backoff_seconds,
                      created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        key,
                        task_id,
                        task_path,
                        artifact_path,
                        status,
                        attempts,
                        max_attempts,
                        retry_backoff_seconds,
                        ts,
                        ts,
                    ),
                )
                inserted += int(cur.rowcount)
            con.execute("COMMIT")
            return inserted

    def counts(self) -> QueueCounts:
        with self._connect() as con:
            rows = dict(con.execute("SELECT status, COUNT(*) FROM tasks GROUP BY status"))
        return QueueCounts(
            pending=int(rows.get("pending", 0)),
            running=int(rows.get("running", 0)),
            done=int(rows.get("done", 0)),
            error=int(rows.get("error", 0)),
            dead=int(rows.get("dead", 0)),
        )

    def indexed_artifacts_count(self) -> int:
        with self._connect() as con:
            row = con.execute("SELECT COUNT(*) FROM artifacts").fetchone()
        return int(row[0]) if row else 0

    def claim_next(
        self,
        owner: str,
        lease_seconds: int,
        retry_errors: bool = False,
    ) -> ClaimedTask | None:
        now = _now_ts()
        lease_expires_at = now + max(1, int(lease_seconds))
        ts = _utc_now()

        with self._connect() as con:
            con.execute("BEGIN IMMEDIATE")
            row = con.execute(
                """
                SELECT key, task_id, task_path, artifact_path
                FROM tasks
                WHERE
                  (
                    status = 'pending'
                    AND (next_attempt_at IS NULL OR next_attempt_at <= ?)
                  )
                  OR (
                    status = 'running'
                    AND lease_expires_at IS NOT NULL
                    AND lease_expires_at < ?
                  )
                  OR (
                    ?
                    AND status = 'error'
                    AND attempts < max_attempts
                    AND (next_attempt_at IS NULL OR next_attempt_at <= ?)
                  )
                ORDER BY created_at, key
                LIMIT 1
                """,
                (now, now, 1 if retry_errors else 0, now),
            ).fetchone()

            if row is None:
                con.execute("COMMIT")
                return None

            key, task_id, task_path, artifact_path = row
            con.execute(
                """
                UPDATE tasks
                SET
                  status='running',
                  attempts=attempts+1,
                  lease_owner=?,
                  lease_expires_at=?,
                  last_started_at=?,
                  updated_at=?
                WHERE key=?
                """,
                (owner, lease_expires_at, now, ts, key),
            )
            con.execute("COMMIT")

        return ClaimedTask(
            key=str(key),
            task_id=str(task_id),
            task_path=(self.run_dir / str(task_path)).resolve(),
            artifact_path=(self.run_dir / str(artifact_path)).resolve(),
        )

    def renew_lease(self, key: str, owner: str, lease_seconds: int) -> bool:
        now = time.time()
        lease_expires_at = now + max(1, int(lease_seconds))
        ts = _utc_now()
        with self._connect() as con:
            cur = con.execute(
                """
                UPDATE tasks
                SET lease_expires_at=?, updated_at=?
                WHERE key=? AND status='running' AND lease_owner=?
                """,
                (lease_expires_at, ts, key, owner),
            )
            return bool(cur.rowcount)

    def abandon_to_pending(self, key: str, owner: str, reason: str) -> bool:
        ts = _utc_now()
        now = _now_ts()
        with self._connect() as con:
            row = con.execute(
                "SELECT last_started_at FROM tasks WHERE key=? AND status='running' AND lease_owner=?",
                (key, owner),
            ).fetchone()
            started = float(row[0]) if row and row[0] is not None else None
            duration_ms = int((now - started) * 1000) if started is not None else None
            cur = con.execute(
                """
                UPDATE tasks
                SET
                  status='pending',
                  last_error=?,
                  next_attempt_at=NULL,
                  attempts=CASE WHEN attempts > 0 THEN attempts - 1 ELSE 0 END,
                  lease_owner=NULL,
                  lease_expires_at=NULL,
                  last_finished_at=?,
                  last_duration_ms=?,
                  updated_at=?
                WHERE key=? AND status='running' AND lease_owner=?
                """,
                (reason, now, duration_ms, ts, key, owner),
            )
            return bool(cur.rowcount)

    def mark_done(self, key: str) -> None:
        ts = _utc_now()
        now = _now_ts()
        with self._connect() as con:
            row = con.execute(
                "SELECT last_started_at FROM tasks WHERE key=?", (key,)
            ).fetchone()
            started = float(row[0]) if row and row[0] is not None else None
            duration_ms = int((now - started) * 1000) if started is not None else None
            con.execute(
                """
                UPDATE tasks SET
                  status='done',
                  lease_owner=NULL,
                  lease_expires_at=NULL,
                  next_attempt_at=NULL,
                  last_error=NULL,
                  last_finished_at=?,
                  last_duration_ms=?,
                  updated_at=?
                WHERE key=?
                """,
                (now, duration_ms, ts, key),
            )

    def mark_error(self, key: str, err: str, retry_backoff_seconds: int | None = None) -> None:
        ts = _utc_now()
        now = _now_ts()
        with self._connect() as con:
            row = con.execute(
                "SELECT attempts, max_attempts, retry_backoff_seconds, last_started_at FROM tasks WHERE key=?",
                (key,),
            ).fetchone()
            if row is None:
                return
            attempts, max_attempts, backoff, started_at = row
            backoff_seconds = int(retry_backoff_seconds) if retry_backoff_seconds is not None else int(backoff)
            next_attempt_at = now + max(0, backoff_seconds)
            started = float(started_at) if started_at is not None else None
            duration_ms = int((now - started) * 1000) if started is not None else None
            status = "dead" if int(attempts) >= int(max_attempts) else "error"
            con.execute(
                """
                UPDATE tasks
                SET
                  status=?,
                  last_error=?,
                  next_attempt_at=?,
                  lease_owner=NULL,
                  lease_expires_at=NULL,
                  last_finished_at=?,
                  last_duration_ms=?,
                  updated_at=?
                WHERE key=?
                """,
                (status, err, next_attempt_at, now, duration_ms, ts, key),
            )

    def reset_errors(self, include_dead: bool = False) -> int:
        ts = _utc_now()
        with self._connect() as con:
            statuses = ("error", "dead") if include_dead else ("error",)
            qmarks = ",".join(["?"] * len(statuses))
            cur = con.execute(
                """
                UPDATE tasks
                SET status='pending', last_error=NULL, next_attempt_at=NULL, updated_at=?
                WHERE status IN (""" + qmarks + """)
                """,
                (ts, *statuses),
            )
            return int(cur.rowcount)

    def list_tasks(self, status: str, limit: int = 50) -> list[ListedTask]:
        if limit <= 0:
            limit = 50
        with self._connect() as con:
            rows = con.execute(
                """
                SELECT key, task_id, task_path, artifact_path, status, attempts, last_error, lease_owner, lease_expires_at
                FROM tasks
                WHERE status = ?
                ORDER BY updated_at DESC, key
                LIMIT ?
                """,
                (status, int(limit)),
            ).fetchall()

        out: list[ListedTask] = []
        for (
            key,
            task_id,
            task_path,
            artifact_path,
            st,
            attempts,
            last_error,
            lease_owner,
            lease_expires_at,
        ) in rows:
            out.append(
                ListedTask(
                    key=str(key),
                    task_id=str(task_id),
                    task_path=(self.run_dir / str(task_path)).resolve(),
                    artifact_path=(self.run_dir / str(artifact_path)).resolve(),
                    status=str(st),
                    attempts=int(attempts),
                    last_error=str(last_error) if last_error is not None else None,
                    lease_owner=str(lease_owner) if lease_owner is not None else None,
                    lease_expires_at=float(lease_expires_at)
                    if lease_expires_at is not None
                    else None,
                )
            )
        return out

    def reconcile(self) -> ReconcileResult:
        marked_done = 0
        released_stale = 0
        now = _now_ts()

        with self._connect() as con:
            con.execute("BEGIN IMMEDIATE")
            rows = con.execute(
                """
                SELECT key, artifact_path, status, lease_owner, lease_expires_at
                FROM tasks
                WHERE status IN ('pending', 'running', 'error', 'dead')
                """
            ).fetchall()

            done_keys: list[str] = []
            stale_keys: list[str] = []
            dead_owner_keys: list[str] = []
            for key, artifact_path, status, lease_owner, lease_expires_at in rows:
                abs_art = (self.run_dir / str(artifact_path)).resolve()
                if abs_art.exists():
                    done_keys.append(str(key))
                elif (
                    str(status) == "running"
                    and lease_owner is not None
                    and (pid := _parse_pid_owner(str(lease_owner))) is not None
                    and not _pid_alive(pid)
                ):
                    dead_owner_keys.append(str(key))
                elif (
                    str(status) == "running"
                    and lease_expires_at is not None
                    and float(lease_expires_at) < now
                ):
                    stale_keys.append(str(key))

            ts = _utc_now()
            for key in done_keys:
                cur = con.execute(
                    """
                    UPDATE tasks
                    SET status='done', lease_owner=NULL, lease_expires_at=NULL, updated_at=?
                    WHERE key=? AND status != 'done'
                    """,
                    (ts, key),
                )
                marked_done += int(cur.rowcount)

            for key in stale_keys:
                cur = con.execute(
                    """
                    UPDATE tasks
                    SET status='pending', lease_owner=NULL, lease_expires_at=NULL, updated_at=?
                    WHERE key=? AND status='running'
                    """,
                    (ts, key),
                )
                released_stale += int(cur.rowcount)

            for key in dead_owner_keys:
                cur = con.execute(
                    """
                    UPDATE tasks
                    SET status='pending', lease_owner=NULL, lease_expires_at=NULL, updated_at=?
                    WHERE key=? AND status='running'
                    """,
                    (ts, key),
                )
                released_stale += int(cur.rowcount)

            con.execute("COMMIT")

        return ReconcileResult(marked_done=marked_done, released_stale=released_stale)

    def index_artifacts(self, limit: int = 0) -> int:
        inserted = 0
        now = _utc_now()
        with self._connect() as con:
            rows = con.execute(
                """
                SELECT key, artifact_path
                FROM tasks
                WHERE status = 'done'
                ORDER BY updated_at DESC, key
                """
            ).fetchall()

        processed = 0
        for key, artifact_path in rows:
            abs_art = (self.run_dir / str(artifact_path)).resolve()
            if not abs_art.exists():
                continue
            mtime = abs_art.stat().st_mtime
            with self._connect() as con:
                row = con.execute(
                    "SELECT artifact_mtime FROM artifacts WHERE key=?", (str(key),)
                ).fetchone()
                if row is not None and float(row[0]) == float(mtime):
                    continue

            b = abs_art.read_bytes()
            artifact_hash = crate_sha256_hex(b)
            try:
                obj = json.loads(b.decode("utf-8"))
            except Exception:
                obj = None

            def _get(d: Any, *path: str) -> Any:
                cur: Any = d
                for p in path:
                    if not isinstance(cur, dict) or p not in cur:
                        return None
                    cur = cur[p]
                return cur

            artifact_input_hash = _get(obj, "input_hash") if obj else None
            engine_version = _get(obj, "engine_version") if obj else None
            schema_version = _get(obj, "schema_version") if obj else None
            task_id = _get(obj, "task_id") if obj else None
            world_id = _get(obj, "world_id") if obj else None
            strategy_a_id = _get(obj, "strategy_a_id") if obj else None
            strategy_b_id = _get(obj, "strategy_b_id") if obj else None
            rounds = _get(obj, "stats", "rounds") if obj else None
            avg_a = _get(obj, "stats", "avg_payoff_a") if obj else None
            avg_b = _get(obj, "stats", "avg_payoff_b") if obj else None
            coop_a = _get(obj, "stats", "coop_rate_a") if obj else None
            coop_b = _get(obj, "stats", "coop_rate_b") if obj else None
            mutual_c = _get(obj, "stats", "mutual_coop_rate") if obj else None

            with self._connect() as con:
                con.execute("BEGIN IMMEDIATE")
                con.execute(
                    """
                    INSERT INTO artifacts(
                      key, artifact_path, artifact_hash, artifact_input_hash, engine_version, schema_version,
                      task_id, world_id, strategy_a_id, strategy_b_id, rounds, avg_a, avg_b, coop_a, coop_b, mutual_c,
                      indexed_at, artifact_mtime
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(key) DO UPDATE SET
                      artifact_path=excluded.artifact_path,
                      artifact_hash=excluded.artifact_hash,
                      artifact_input_hash=excluded.artifact_input_hash,
                      engine_version=excluded.engine_version,
                      schema_version=excluded.schema_version,
                      task_id=excluded.task_id,
                      world_id=excluded.world_id,
                      strategy_a_id=excluded.strategy_a_id,
                      strategy_b_id=excluded.strategy_b_id,
                      rounds=excluded.rounds,
                      avg_a=excluded.avg_a,
                      avg_b=excluded.avg_b,
                      coop_a=excluded.coop_a,
                      coop_b=excluded.coop_b,
                      mutual_c=excluded.mutual_c,
                      indexed_at=excluded.indexed_at,
                      artifact_mtime=excluded.artifact_mtime
                    """,
                    (
                        str(key),
                        str(artifact_path),
                        artifact_hash,
                        str(artifact_input_hash) if artifact_input_hash is not None else None,
                        str(engine_version) if engine_version is not None else None,
                        int(schema_version) if schema_version is not None else None,
                        str(task_id) if task_id is not None else None,
                        str(world_id) if world_id is not None else None,
                        str(strategy_a_id) if strategy_a_id is not None else None,
                        str(strategy_b_id) if strategy_b_id is not None else None,
                        int(rounds) if rounds is not None else None,
                        float(avg_a) if avg_a is not None else None,
                        float(avg_b) if avg_b is not None else None,
                        float(coop_a) if coop_a is not None else None,
                        float(coop_b) if coop_b is not None else None,
                        float(mutual_c) if mutual_c is not None else None,
                        now,
                        float(mtime),
                    ),
                )
                con.execute("COMMIT")
                inserted += 1

            processed += 1
            if limit and processed >= limit:
                break

        return inserted


def load_manifest(run_dir: Path) -> dict[str, Any]:
    path = run_dir / "manifest.json"
    return json.loads(path.read_text(encoding="utf-8"))


def crate_sha256_hex(b: bytes) -> str:
    # keep this local and stable (avoid pulling in hashing libs)
    import hashlib

    return hashlib.sha256(b).hexdigest()


def iter_missing_artifacts(run_dir: Path, manifest: dict[str, Any]) -> Iterable[tuple[Path, Path]]:
    for t in manifest.get("tasks", []):
        task_path = (run_dir / t["task_path"]).resolve()
        out_path = (run_dir / t["artifact_path"]).resolve()
        if not out_path.exists():
            yield (task_path, out_path)
