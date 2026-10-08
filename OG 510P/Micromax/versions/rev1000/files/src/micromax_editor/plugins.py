from __future__ import annotations

from contextlib import ExitStack, nullcontext
import multiprocessing
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

from micromax import VM
from micromax.vm import MicromaxError, Word

from .plugin_meta import load_plugin_meta, parse_plugin_meta, PluginMeta
from .plugin_grants import PluginLoadGrant
from .file_access import (
    FilesystemOperationTimeoutError,
    list_dir_contained_bounded,
    stat_path_contained_bounded,
)
from .plugin_io import plugin_file_exists, plugin_root_path, read_plugin_text
from .plugin_package import (
    PLUGIN_PACKAGE_FINGERPRINT_TIMEOUT_SECONDS,
    PLUGIN_PACKAGE_MAX_FILES,
    PLUGIN_PACKAGE_MAX_RETAINED_BYTES,
    PLUGIN_PACKAGE_MAX_TOTAL_BYTES,
    PluginPackageSnapshot,
    plugin_package_fingerprint_inline as _plugin_package_fingerprint_inline,
    plugin_package_fingerprint_worker as _plugin_package_fingerprint_worker,
    plugin_package_paths as _plugin_package_paths,
    plugin_package_snapshot_inline as _plugin_package_snapshot_inline,
    plugin_package_snapshot_worker as _plugin_package_snapshot_worker,
)
from .plugin_runtime import (
    RuntimeGroupOperationError,
    RuntimeGroupOperationReport,
    RuntimeRegistrationSnapshot,
    VmDictionarySnapshot,
    cleanup_plugin_generation_state,
    cleanup_runtime_group,
    isolated_vm_execution_state,
    restore_runtime_generation_state,
    restore_runtime_group_state,
    restore_runtime_registrations,
    restore_vm_dictionary_state,
    retag_runtime_group,
    snapshot_runtime_generation_state,
    snapshot_runtime_group_state,
    snapshot_runtime_registrations,
    snapshot_vm_dictionary_state,
)
from .plugin_execution_budget import plugin_execution_budget
from .vm_load_policy import plugin_load_root_context
from .worker_process import (
    WorkerResultChannel,
    WorkerResultTimeoutError,
    collect_worker_result,
    create_one_shot_worker,
    isolated_worker_context,
    normalize_worker_timeout_seconds,
)


PLUGIN_DISCOVERY_MAX_DIRS = 512
PLUGIN_DISCOVERY_TIMEOUT_SECONDS = 5.0


def _plugin_worker_context() -> multiprocessing.context.BaseContext:
    """Return a process context for killable plugin filesystem workers."""

    return isolated_worker_context()


def _collect_plugin_worker_result(
    proc: multiprocessing.Process,
    channel: WorkerResultChannel,
    *,
    timeout: float,
    operation: str,
    plugin: str,
) -> object:
    """Collect one framed package result and preserve plugin-facing errors."""

    timeout_value = normalize_worker_timeout_seconds(
        timeout,
        default=PLUGIN_PACKAGE_FINGERPRINT_TIMEOUT_SECONDS,
    )
    timeout_value = max(0.01, timeout_value)
    try:
        return collect_worker_result(
            proc,
            channel,
            timeout_seconds=timeout_value,
            operation=f"{operation}: {plugin}",
            require_clean_exit=True,
        )
    except WorkerResultTimeoutError as e:
        raise MicromaxError(
            f"{operation} timed out after {timeout_value:.3g}s: {plugin}"
        ) from e
    except (KeyboardInterrupt, SystemExit):
        raise
    except BaseException as e:
        raise MicromaxError(f"{operation} worker result failed: {plugin}: {e}") from e


@dataclass
class Plugin:
    name: str
    root: Path
    wid: int
    meta: dict[str, Any]
    group: str = ""
    generation: int = 0
    package_digest: str = ""
    package_file_count: int = 0
    package_snapshot: PluginPackageSnapshot | None = None


@dataclass(frozen=True)
class _PluginCandidate:
    name: str
    root: Path
    init_path: Path
    meta: PluginMeta


@dataclass(frozen=True)
class _PluginPackageFingerprint:
    digest: str
    file_count: int


@dataclass(frozen=True)
class PluginWordlistTombstone:
    """Compact record for a committed plugin wordlist retired from the VM.

    Reload and unload used to leave old plugin wordlists in ``vm.wordlists`` for
    later provenance inspection.  That kept executable ``Word`` objects alive
    indefinitely.  Tombstones preserve the debug metadata needed by humans and
    tests without retaining executable definitions in the live dictionary.
    """

    plugin: str
    root: str
    wid: int
    generation: int
    group: str
    reason: str
    word_count: int
    words: tuple[str, ...]
    spans: tuple[tuple[str, str, int, int], ...] = ()
    package_digest: str = ""
    package_file_count: int = 0


class PluginManager:
    """Very small plugin loader.

    Design goals:
      - predictable namespaces (one wordlist per plugin)
      - hot reload stages replacements before swapping live registrations
      - lifecycle words are optional: preinit/init/postinit/deinit

    Inspired by micro's plugin help topic which describes lifecycle callbacks
    like `preinit`, `init`, `postinit`, and `deinit`. (See micro runtime help.)
    """

    def __init__(self, vm: VM) -> None:
        self.vm = vm
        self.plugins: dict[str, Plugin] = {}
        # Non-fatal plugin load/reload errors for the current plugin state.
        # Successful loads clear the matching plugin's older errors so inventory
        # rows do not keep reporting stale failures after a fix.
        self.load_errors: list[tuple[str, str]] = []
        # Last scanned plugin candidates (including those blocked by deps).
        self.candidates: dict[str, _PluginCandidate] = {}
        self.load_grants: dict[str, PluginLoadGrant] = {}
        # Exact bytes approved by each live session grant.  Keeping this beside
        # the small grant record lets initial load, later reload, and deferred
        # package-local source reads consume one immutable package generation
        # instead of checking live paths and then reopening them.
        self.approved_package_snapshots: dict[str, PluginPackageSnapshot] = {}
        self.root: Path | None = None
        self._reload_serial: int = 0
        self._generation_serial: int = 0
        self._grant_serial: int = 0
        # Bounded evidence for plugin group cleanup/retag sweeps.  Runtime group
        # operations are intentionally best-effort today, but failures must be
        # observable instead of disappearing behind broad except/pass clauses.
        self.runtime_group_reports: list[RuntimeGroupOperationReport] = []
        # Bounded compact provenance for committed plugin wordlists that have
        # been unloaded or replaced.  Old executable Word objects are removed
        # from the VM; this keeps enough metadata to explain what was retired.
        self.retired_wordlists: list[PluginWordlistTombstone] = []
        self.retired_wordlist_limit: int = 64
        self.package_fingerprint_max_files: int = PLUGIN_PACKAGE_MAX_FILES
        self.package_fingerprint_max_total_bytes: int = PLUGIN_PACKAGE_MAX_TOTAL_BYTES
        self.package_fingerprint_timeout_seconds: float = PLUGIN_PACKAGE_FINGERPRINT_TIMEOUT_SECONDS
        self.package_snapshot_max_retained_bytes: int = PLUGIN_PACKAGE_MAX_RETAINED_BYTES
        self.plugin_discovery_max_dirs: int = PLUGIN_DISCOVERY_MAX_DIRS
        self.plugin_discovery_timeout_seconds: float = PLUGIN_DISCOVERY_TIMEOUT_SECONDS

    def clear_load_errors(self, name: str | None = None) -> int:
        """Clear recorded load/reload errors.

        With *name*, only that plugin's errors are removed.  Without it, the
        whole scan/reload error register is reset.  The plugin manager treats
        ``load_errors`` as current-state evidence rather than an append-only
        diary; a successful repair should not leave a plugin labeled as broken.
        """

        if name is None:
            count = len(self.load_errors)
            self.load_errors = []
            return int(count)
        plugin_name = str(name)
        before = len(self.load_errors)
        self.load_errors = [(n, e) for (n, e) in self.load_errors if str(n) != plugin_name]
        return int(before - len(self.load_errors))

    def _record_load_error(self, name: str, err: object) -> None:
        item = (str(name), str(err))
        if item not in self.load_errors:
            self.load_errors.append(item)


    def _next_grant_serial(self) -> int:
        """Return a monotonically increasing session grant token."""

        self._grant_serial += 1
        return int(self._grant_serial)

    def _grant_matches_candidate(
        self,
        grant: PluginLoadGrant,
        cand: _PluginCandidate,
        *,
        fingerprint: _PluginPackageFingerprint | PluginPackageSnapshot | None = None,
    ) -> bool:
        fp = fingerprint if fingerprint is not None else self._candidate_package_fingerprint(cand)
        return grant.matches(
            plugin=cand.name,
            root=cand.root,
            entry=cand.init_path,
            package_digest=fp.digest,
        )

    def _candidate_root_for_grant(self, name: str) -> Path:
        """Return the root that should be re-read for a grant-sensitive plugin."""

        plugin_name = str(name)
        cand = self.candidates.get(plugin_name)
        if cand is not None:
            return Path(cand.root)
        pl = self.plugins.get(plugin_name)
        if pl is not None:
            return Path(pl.root)
        raise MicromaxError(f"Plugin is not available: {plugin_name}")

    def _candidate_package_paths(self, cand: _PluginCandidate) -> list[Path]:
        """Return contained plugin package paths for explicit debug/direct mode.

        Ordinary grant validation now calls ``_candidate_package_fingerprint`` so
        recursive scanning and byte reads are owned by a killable worker.  This
        helper remains as the small in-process implementation for tests or
        embeddings that deliberately set ``package_fingerprint_timeout_seconds``
        to zero.
        """

        try:
            max_files = int(getattr(self, "package_fingerprint_max_files", PLUGIN_PACKAGE_MAX_FILES))
        except Exception:
            max_files = PLUGIN_PACKAGE_MAX_FILES
        return _plugin_package_paths(cand.name, cand.root, cand.init_path, max_files=max_files)

    def _candidate_package_fingerprint_direct(self, cand: _PluginCandidate) -> _PluginPackageFingerprint:
        """Return the package fingerprint in-process for explicit direct mode."""

        try:
            max_files = int(getattr(self, "package_fingerprint_max_files", PLUGIN_PACKAGE_MAX_FILES))
        except Exception:
            max_files = PLUGIN_PACKAGE_MAX_FILES
        try:
            max_total = int(
                getattr(self, "package_fingerprint_max_total_bytes", PLUGIN_PACKAGE_MAX_TOTAL_BYTES)
            )
        except Exception:
            max_total = PLUGIN_PACKAGE_MAX_TOTAL_BYTES
        digest, count = _plugin_package_fingerprint_inline(
            cand.name,
            cand.root,
            cand.init_path,
            max_files=max_files,
            max_total_bytes=max_total,
        )
        return _PluginPackageFingerprint(digest=digest, file_count=int(count))

    def _candidate_package_fingerprint(self, cand: _PluginCandidate) -> _PluginPackageFingerprint:
        """Return a deterministic digest for the candidate's current package bytes.

        Restricted-workspace manual load grants depend on this fingerprint.  The
        underlying recursive directory walk and contained byte reads are bounded
        with a killable worker so a remote, enormous, or wedged plugin tree cannot
        monopolize the editor before the user has even approved execution.
        """

        timeout = normalize_worker_timeout_seconds(
            getattr(
                self,
                "package_fingerprint_timeout_seconds",
                PLUGIN_PACKAGE_FINGERPRINT_TIMEOUT_SECONDS,
            ),
            default=PLUGIN_PACKAGE_FINGERPRINT_TIMEOUT_SECONDS,
        )
        if timeout <= 0:
            return self._candidate_package_fingerprint_direct(cand)

        try:
            max_files = int(getattr(self, "package_fingerprint_max_files", PLUGIN_PACKAGE_MAX_FILES))
        except Exception:
            max_files = PLUGIN_PACKAGE_MAX_FILES
        try:
            max_total = int(
                getattr(self, "package_fingerprint_max_total_bytes", PLUGIN_PACKAGE_MAX_TOTAL_BYTES)
            )
        except Exception:
            max_total = PLUGIN_PACKAGE_MAX_TOTAL_BYTES

        ctx = _plugin_worker_context()
        proc, channel = create_one_shot_worker(
            ctx,
            target=_plugin_package_fingerprint_worker,
            args=(str(cand.name), str(cand.root), str(cand.init_path), max_files, max_total),
            max_result_bytes=1024 * 1024,
        )
        payload = _collect_plugin_worker_result(
            proc,
            channel,
            timeout=timeout,
            operation="plugin fingerprint",
            plugin=cand.name,
        )

        status = str(payload[0]) if payload else "err"
        if status == "ok" and len(payload) >= 3:
            return _PluginPackageFingerprint(digest=str(payload[1]), file_count=int(payload[2]))
        if status == "err" and len(payload) >= 3:
            kind = str(payload[1])
            message = str(payload[2])
            if kind == "MicromaxError":
                raise MicromaxError(message)
            raise MicromaxError(message or kind)
        raise MicromaxError(f"plugin fingerprint worker returned invalid result: {cand.name}")

    def _candidate_package_snapshot_direct(self, cand: _PluginCandidate) -> PluginPackageSnapshot:
        """Capture exact candidate bytes in-process for explicit direct mode."""

        try:
            max_files = int(getattr(self, "package_fingerprint_max_files", PLUGIN_PACKAGE_MAX_FILES))
        except Exception:
            max_files = PLUGIN_PACKAGE_MAX_FILES
        try:
            max_total = int(
                getattr(self, "package_fingerprint_max_total_bytes", PLUGIN_PACKAGE_MAX_TOTAL_BYTES)
            )
        except Exception:
            max_total = PLUGIN_PACKAGE_MAX_TOTAL_BYTES
        return _plugin_package_snapshot_inline(
            cand.name,
            cand.root,
            cand.init_path,
            max_files=max_files,
            max_total_bytes=max_total,
        )

    def _candidate_package_snapshot(self, cand: _PluginCandidate) -> PluginPackageSnapshot:
        """Capture one bounded immutable package generation in a killable worker."""

        timeout = normalize_worker_timeout_seconds(
            getattr(
                self,
                "package_fingerprint_timeout_seconds",
                PLUGIN_PACKAGE_FINGERPRINT_TIMEOUT_SECONDS,
            ),
            default=PLUGIN_PACKAGE_FINGERPRINT_TIMEOUT_SECONDS,
        )
        if timeout <= 0:
            return self._candidate_package_snapshot_direct(cand)

        try:
            max_files = int(getattr(self, "package_fingerprint_max_files", PLUGIN_PACKAGE_MAX_FILES))
        except Exception:
            max_files = PLUGIN_PACKAGE_MAX_FILES
        try:
            max_total = int(
                getattr(self, "package_fingerprint_max_total_bytes", PLUGIN_PACKAGE_MAX_TOTAL_BYTES)
            )
        except Exception:
            max_total = PLUGIN_PACKAGE_MAX_TOTAL_BYTES

        ctx = _plugin_worker_context()
        proc, channel = create_one_shot_worker(
            ctx,
            target=_plugin_package_snapshot_worker,
            args=(str(cand.name), str(cand.root), str(cand.init_path), max_files, max_total),
            max_result_bytes=max(
                8 * 1024 * 1024,
                (
                    max_total
                    if max_total >= 0
                    else PLUGIN_PACKAGE_MAX_RETAINED_BYTES
                )
                + 8 * 1024 * 1024,
            ),
        )
        payload = _collect_plugin_worker_result(
            proc,
            channel,
            timeout=timeout,
            operation="plugin snapshot",
            plugin=cand.name,
        )
        status = str(payload[0]) if payload else "err"
        if status == "ok" and len(payload) >= 2 and isinstance(payload[1], PluginPackageSnapshot):
            return payload[1]
        if status == "err" and len(payload) >= 3:
            kind = str(payload[1])
            message = str(payload[2])
            if kind == "MicromaxError":
                raise MicromaxError(message)
            raise MicromaxError(message or kind)
        raise MicromaxError(f"plugin snapshot worker returned invalid result: {cand.name}")

    def _resolve_snapshot_init_path(
        self,
        name: str,
        snapshot: PluginPackageSnapshot,
        meta: PluginMeta,
    ) -> Path:
        if meta.entry:
            path = snapshot.absolute_path(meta.entry)
            if snapshot.contains_path(path):
                return path
            raise MicromaxError(f"Plugin entry file not found: {name}: {meta.entry}")
        for entry in ("init.mx", "init.mmx", "init.mf"):
            path = snapshot.absolute_path(entry)
            if snapshot.contains_path(path):
                return path
        raise MicromaxError(f"Plugin init file not found: {name}")

    def _candidate_from_snapshot(
        self,
        name: str,
        snapshot: PluginPackageSnapshot,
    ) -> _PluginCandidate:
        """Derive metadata and entry from the same bytes that will execute."""

        plugin_name = str(name)
        if str(snapshot.name) != plugin_name:
            raise MicromaxError(f"plugin snapshot name mismatch: {snapshot.name} != {plugin_name}")
        meta = parse_plugin_meta(
            plugin_name,
            snapshot.optional_text("plugin.json"),
            entry_exists=lambda entry: snapshot.contains_relative(entry),
        )
        init_path = self._resolve_snapshot_init_path(plugin_name, snapshot, meta)
        return _PluginCandidate(
            name=plugin_name,
            root=snapshot.root_path,
            init_path=init_path,
            meta=meta,
        )

    def _retained_snapshot_bytes(
        self,
        *,
        excluding_loaded: str | None = None,
        excluding_approved: str | None = None,
        include: PluginPackageSnapshot | None = None,
    ) -> int:
        """Return retained snapshot bytes, counting shared objects once."""

        snapshots: list[PluginPackageSnapshot] = []
        for name, plugin in self.plugins.items():
            if excluding_loaded is not None and str(name) == str(excluding_loaded):
                continue
            snapshot = getattr(plugin, "package_snapshot", None)
            if isinstance(snapshot, PluginPackageSnapshot):
                snapshots.append(snapshot)
        for name, snapshot in self.approved_package_snapshots.items():
            if excluding_approved is not None and str(name) == str(excluding_approved):
                continue
            if isinstance(snapshot, PluginPackageSnapshot):
                snapshots.append(snapshot)
        if isinstance(include, PluginPackageSnapshot):
            snapshots.append(include)

        total = 0
        seen: set[int] = set()
        for snapshot in snapshots:
            ident = id(snapshot)
            if ident in seen:
                continue
            seen.add(ident)
            total += int(snapshot.total_bytes)
        return int(total)

    def _check_snapshot_retention_budget(
        self,
        snapshot: PluginPackageSnapshot,
        *,
        replacing: str | None = None,
        replacing_approval: str | None = None,
    ) -> None:
        try:
            limit = int(
                getattr(self, "package_snapshot_max_retained_bytes", PLUGIN_PACKAGE_MAX_RETAINED_BYTES)
            )
        except Exception:
            limit = PLUGIN_PACKAGE_MAX_RETAINED_BYTES
        if limit < 0:
            return
        projected = self._retained_snapshot_bytes(
            excluding_loaded=replacing,
            excluding_approved=replacing_approval,
            include=snapshot,
        )
        if projected > limit:
            raise MicromaxError(
                f"plugin snapshot retention budget exceeded: {projected} > {limit} bytes"
            )

    def refresh_candidate(self, name: str) -> _PluginCandidate:
        """Re-read one candidate's metadata and contained entry path from disk."""

        plugin_name = str(name)
        fresh = self._candidate_from_disk(plugin_name, self._candidate_root_for_grant(plugin_name))
        self.candidates[plugin_name] = fresh
        return fresh

    def grant_load_snapshot(
        self,
        name: str,
        *,
        issuer: str = "user",
        duration: str = "session",
        provenance: str = "",
    ) -> tuple[PluginLoadGrant, PluginPackageSnapshot]:
        """Record approval and return the exact package bytes it authorized.

        The grant is bound to the candidate's current root, entry file,
        and package digest.  Later metadata, entry-path, or same-path package
        byte changes invalidate the grant until the user runs the explicit load
        command again.  Callers that activate immediately can pass the returned
        snapshot into ``load_available`` so approval and evaluation consume the
        same bytes without a second package walk or check-to-use gap.
        """

        plugin_name = str(name)
        disk_candidate = self.refresh_candidate(plugin_name)
        snapshot = self._candidate_package_snapshot(disk_candidate)
        fresh = self._candidate_from_snapshot(plugin_name, snapshot)
        loaded = self.plugins.get(plugin_name)
        loaded_snapshot = getattr(loaded, "package_snapshot", None)
        if (
            isinstance(loaded_snapshot, PluginPackageSnapshot)
            and loaded_snapshot == snapshot
        ):
            # Reapproving byte-identical live files should preserve the current
            # generation's deferred-source authority and avoid retaining a
            # duplicate multi-MiB snapshot object.
            snapshot = loaded_snapshot
        self._check_snapshot_retention_budget(
            snapshot,
            replacing_approval=plugin_name,
        )
        self.candidates[plugin_name] = fresh
        grant = PluginLoadGrant(
            plugin=plugin_name,
            root=str(fresh.root),
            entry=str(fresh.init_path),
            package_digest=str(snapshot.digest),
            package_file_count=int(snapshot.file_count),
            issuer=str(issuer or "user"),
            duration=str(duration or "session"),
            provenance=str(provenance or ""),
            issued_at=self._next_grant_serial(),
        )
        self.load_grants[plugin_name] = grant
        self.approved_package_snapshots[plugin_name] = snapshot
        return grant, snapshot

    def grant_load(
        self,
        name: str,
        *,
        issuer: str = "user",
        duration: str = "session",
        provenance: str = "",
    ) -> PluginLoadGrant:
        """Record an explicit content-bound approval for one plugin candidate."""

        grant, _snapshot = self.grant_load_snapshot(
            name,
            issuer=issuer,
            duration=duration,
            provenance=provenance,
        )
        return grant

    def _require_current_load_grant(
        self,
        name: str,
        presented: PluginLoadGrant | None,
    ) -> PluginLoadGrant:
        """Return the active grant issuance or reject a stale handle.

        Revocation and reapproval replace the manager-owned grant record.  A
        caller retaining an older immutable record must not be able to replay it
        merely because its package fields still match retained bytes.  Compare
        the session issuance token and authority-bearing fields before any disk
        capture or source evaluation.  Usage-count replacements preserve the
        same issuance, so ordinary embedders do not need to reacquire a handle
        after every successful load.  ``presented=None`` is the internal lane
        used by ``reload`` to consume the manager's current record directly.
        """

        plugin_name = str(name)
        current = self.load_grants.get(plugin_name)
        if current is None or bool(current.revoked):
            raise MicromaxError(f"plugin load grant is stale: {plugin_name}")
        if presented is not None:
            same_issuance = (
                not bool(presented.revoked)
                and int(presented.issued_at) == int(current.issued_at)
                and str(presented.plugin) == str(current.plugin)
                and str(Path(presented.root)) == str(Path(current.root))
                and str(Path(presented.entry)) == str(Path(current.entry))
                and str(presented.package_digest) == str(current.package_digest)
                and int(presented.package_file_count) == int(current.package_file_count)
            )
            if not same_issuance:
                raise MicromaxError(f"plugin load grant is stale: {plugin_name}")
        return current

    def active_load_grant(self, name: str, *, refresh: bool = False) -> PluginLoadGrant | None:
        """Return an active content-bound grant.

        The ordinary path compares against the already approved immutable
        snapshot and performs no filesystem traversal.  ``refresh=True`` is the
        explicit diagnostic path that asks whether the live package still has
        the approved digest.
        """

        plugin_name = str(name)
        grant = self.load_grants.get(plugin_name)
        if grant is None or grant.revoked:
            return None
        try:
            if refresh:
                cand = self.refresh_candidate(plugin_name)
                fingerprint: _PluginPackageFingerprint | PluginPackageSnapshot | None = None
            else:
                snapshot = self.approved_package_snapshots.get(plugin_name)
                if not isinstance(snapshot, PluginPackageSnapshot):
                    return None
                cand = self._candidate_from_snapshot(plugin_name, snapshot)
                fingerprint = snapshot
        except Exception:
            return None
        if not self._grant_matches_candidate(grant, cand, fingerprint=fingerprint):
            return None
        return grant

    def _loaded_plugin_record(self, plugin: Plugin | str) -> Plugin | None:
        """Return the currently advertised loaded record named by *plugin*.

        A retired ``Plugin`` object may remain reachable through a stale callback
        or embedder reference.  Object identity is part of runtime authority; an
        old record must never recover package access merely because its name and
        digest still resemble the current session grant.
        """

        if isinstance(plugin, Plugin):
            current = self.plugins.get(str(plugin.name))
            return plugin if current is plugin else None
        return self.plugins.get(str(plugin))

    def loaded_plugin_package_current(
        self,
        plugin: Plugin | str,
        *,
        require_digest: bool = False,
    ) -> bool:
        """Return whether a loaded plugin still matches its committed package bytes.

        This is an explicit live-disk diagnostic, not the callback authority
        check.  Restricted callbacks consume their committed immutable snapshot
        even when the package directory later changes; reload requires a separate
        approval of the replacement bytes.  Trusted loads often have no package
        digest, so callers that need content evidence should set ``require_digest``.
        """

        pl = self._loaded_plugin_record(plugin)
        if pl is None:
            return False
        digest = str(getattr(pl, "package_digest", "") or "")
        if not digest:
            return not bool(require_digest)
        try:
            cand = self._candidate_from_disk(str(pl.name), Path(pl.root))
            fp = self._candidate_package_fingerprint(cand)
        except Exception:
            return False
        return str(fp.digest) == digest

    def loaded_plugin_package_authorized(
        self,
        plugin: Plugin | str,
        *,
        require_digest: bool = False,
    ) -> bool:
        """Return whether package-local source loads remain authorized now.

        Restricted callback authority is the intersection of the currently
        advertised generation, its immutable byte snapshot, and the active grant.
        Interactive revocation also unloads managed runtime surfaces, but this
        predicate remains fail-closed for embedders and interrupted transitions.
        """

        return not self.loaded_plugin_source_load_denial(
            plugin,
            require_digest=require_digest,
        )

    def loaded_plugin_source_load_denial(
        self,
        plugin: Plugin | str,
        *,
        require_digest: bool = False,
    ) -> str:
        """Return why a loaded generation may not consume package source now.

        Restricted generations read package-local source only from the exact
        immutable snapshot that was approved and evaluated.  This check is
        therefore identity/grant validation only: it never walks or hashes the
        live package and cannot open a check-to-use window before the later read.
        Live-disk freshness is evaluated explicitly when a new grant is issued or
        when ``active_load_grant(..., refresh=True)`` is requested.
        """

        pl = self._loaded_plugin_record(plugin)
        if pl is None:
            return "plugin source load denied: plugin generation is not loaded"

        name = str(getattr(pl, "name", "") or "<unknown>")
        generation = int(getattr(pl, "generation", 0) or 0)
        label = name + (f" generation {generation}" if generation else "")
        prefix = f"plugin source load denied: {label}: "
        digest = str(getattr(pl, "package_digest", "") or "")
        if not digest:
            if require_digest:
                return prefix + "loaded package has no committed digest"
            return ""

        grant = self.load_grants.get(name)
        if grant is None:
            return prefix + "no active load grant"
        if bool(grant.revoked):
            return prefix + "load grant revoked"
        if str(grant.plugin) != name:
            return prefix + "load grant plugin identity mismatch"
        if str(Path(grant.root)) != str(Path(pl.root)):
            return prefix + "load grant root does not authorize the plugin root"

        snapshot = getattr(pl, "package_snapshot", None)
        if not isinstance(snapshot, PluginPackageSnapshot):
            return prefix + "loaded package has no committed byte snapshot"
        if str(snapshot.name) != name or str(snapshot.root_path) != str(Path(pl.root)):
            return prefix + "committed byte snapshot identity mismatch"
        if str(snapshot.digest) != digest:
            return prefix + "committed byte snapshot digest mismatch"
        if int(snapshot.file_count) != int(getattr(pl, "package_file_count", 0) or 0):
            return prefix + "committed byte snapshot file-count mismatch"

        # A newly approved replacement is deliberately distinct from the still
        # committed generation.  The old generation keeps consuming its own
        # immutable bytes until reload commits; the latest grant/snapshot pair
        # merely authorizes the future replacement.  Revocation remains decisive
        # because it marks this one session grant revoked before any callback can
        # consume package source again (and the interactive command unloads too).
        approved = self.approved_package_snapshots.get(name)
        if not isinstance(approved, PluginPackageSnapshot):
            return prefix + "active load grant has no approved byte snapshot"
        if str(approved.name) != name or str(approved.root_path) != str(Path(grant.root)):
            return prefix + "approved byte snapshot identity mismatch"
        if str(approved.digest) != str(grant.package_digest):
            return prefix + "approved byte snapshot digest does not match the load grant"
        if int(approved.file_count) != int(grant.package_file_count):
            return prefix + "approved byte snapshot file count does not match the load grant"
        if not approved.contains_path(grant.entry):
            return prefix + "load grant entry is absent from the approved snapshot"
        return ""

    def mark_load_grant_used(self, name: str) -> None:
        plugin_name = str(name)
        grant = self.load_grants.get(plugin_name)
        if grant is not None:
            self.load_grants[plugin_name] = grant.used()

    def revoke_load_grant(self, name: str) -> bool:
        plugin_name = str(name)
        grant = self.load_grants.get(plugin_name)
        if grant is None:
            return False
        self.load_grants[plugin_name] = grant.revoked_copy()
        self.approved_package_snapshots.pop(plugin_name, None)
        return True

    def load_grant_rows(self, *, verify_disk: bool = False) -> list[list[object]]:
        """Return small diagnostic rows for session plugin-load grants.

        The default is prompt-safe and compares immutable in-memory approval
        state only.  ``verify_disk=True`` performs the explicit bounded package
        refresh needed to label an approval stale relative to current files.
        """

        rows: list[list[object]] = []
        for name in sorted(self.load_grants, key=lambda s: str(s).casefold()):
            grant = self.load_grants[name]
            state = "revoked" if grant.revoked else (
                "active"
                if self.active_load_grant(name, refresh=bool(verify_disk))
                else "stale"
            )
            rows.append([
                str(grant.plugin),
                state,
                str(grant.duration),
                str(grant.issuer),
                str(grant.scope),
                str(grant.provenance),
                int(grant.issued_at),
                int(grant.use_count),
                str(grant.package_digest),
                int(grant.package_file_count),
            ])
        return rows

    def _stable_group(self, name: str) -> str:
        return f"plugin:{str(name)}"

    def _next_stage_group(self, name: str) -> str:
        self._reload_serial += 1
        return f"{self._stable_group(name)}#reload{int(self._reload_serial)}"

    def _next_generation(self) -> int:
        """Return a monotonically increasing loaded-plugin generation token."""

        self._generation_serial += 1
        return int(self._generation_serial)

    def _plugin_group(self, plugin: Plugin | str) -> str:
        if isinstance(plugin, Plugin):
            return str(plugin.group or self._stable_group(plugin.name))
        return self._stable_group(str(plugin))

    def _plugin_requires(self, plugin: Plugin) -> tuple[str, ...]:
        """Return normalized direct imports declared by one plugin."""

        raw = plugin.meta.get("requires", []) if isinstance(plugin.meta, dict) else []
        return tuple(dict.fromkeys(str(name) for name in (raw or []) if str(name).strip()))

    def plugin_dependency_closure(self, plugin: Plugin) -> tuple[Plugin, ...]:
        """Return the deterministic loaded dependency closure for *plugin*.

        Micromax words resolve dynamically through the active search order, so a
        dependency's own code also needs its declared dependencies while it is
        called by another plugin.  Breadth-first traversal keeps every direct
        import ahead of transitive implementation details, preserves manifest
        order within each level, and de-duplicates shared dependencies.
        """

        seen = {str(plugin.name)}
        pending = list(self._plugin_requires(plugin))
        out: list[Plugin] = []
        while pending:
            dep_name = str(pending.pop(0))
            if dep_name in seen:
                continue
            dep = self.plugins.get(dep_name)
            if dep is None:
                raise MicromaxError(
                    f"plugin {plugin.name}: declared dependency is not loaded: {dep_name}"
                )
            seen.add(dep_name)
            out.append(dep)
            pending.extend(self._plugin_requires(dep))
        return tuple(out)

    def plugin_execution_search_order(self, plugin: Plugin) -> list[int]:
        """Return the only wordlists readable during one plugin generation."""

        ordered = [int(plugin.wid)]
        ordered.extend(int(dep.wid) for dep in self.plugin_dependency_closure(plugin))
        ordered.append(int(self.vm.forth_wid))
        return list(dict.fromkeys(ordered))

    def _editor_owner(self) -> Any:
        return getattr(self.vm, "editor_owner", None)

    def _script_context(self):
        """Return the editor script-context manager when available."""

        ed = self._editor_owner()
        ctx = getattr(ed, "script_context", None)
        if callable(ctx):
            return ctx()
        return nullcontext()

    def _plugin_execution_context(
        self,
        plugin: Plugin,
        *,
        replaces_generation: int | None = None,
    ):
        """Evaluate plugin code with exact namespace and package authority."""

        readable = tuple(self.plugin_execution_search_order(plugin))
        stack = ExitStack()
        stack.enter_context(
            plugin_load_root_context(
                self.vm,
                plugin.root,
                generation=plugin.generation,
                replaces_generation=replaces_generation,
                package_snapshot=plugin.package_snapshot,
                plugin_name=plugin.name,
                readable_wids=readable,
                writable_wids=(int(plugin.wid),),
            )
        )
        stack.enter_context(plugin_execution_budget(self.vm))
        stack.enter_context(self._script_context())
        return stack

    def _snapshot_registrations(self) -> RuntimeRegistrationSnapshot:
        return snapshot_runtime_registrations(self.vm)

    def _restore_registrations(self, snap: RuntimeRegistrationSnapshot) -> None:
        restore_runtime_registrations(self.vm, snap)

    def _snapshot_dictionary(self) -> VmDictionarySnapshot:
        return snapshot_vm_dictionary_state(self.vm)

    def _restore_dictionary(self, snap: VmDictionarySnapshot) -> None:
        restore_vm_dictionary_state(self.vm, snap)

    def _restore_transaction_state(
        self,
        dictionary: VmDictionarySnapshot,
        registrations: RuntimeRegistrationSnapshot,
    ) -> None:
        """Restore VM dictionary plus editor/runtime registration state.

        Dictionary restoration must run before registration restoration so hook
        handler lists are applied to the restored hook-word objects, not to a
        transient word that a failed plugin definition just installed.
        """

        self._restore_dictionary(dictionary)
        self._restore_registrations(registrations)

    def _remember_runtime_group_report(
        self,
        report: RuntimeGroupOperationReport,
    ) -> RuntimeGroupOperationReport:
        self.runtime_group_reports.append(report)
        if len(self.runtime_group_reports) > 50:
            del self.runtime_group_reports[:-50]
        if not report.ok:
            ed = self._editor_owner()
            recorder = getattr(ed, "record_plugin_cleanup_report", None)
            if callable(recorder):
                try:
                    recorder(report)
                except Exception:
                    pass
        return report

    def runtime_group_failures(self) -> list[RuntimeGroupOperationReport]:
        """Return retained cleanup/retag reports with at least one failure."""

        return [report for report in self.runtime_group_reports if not report.ok]

    def _plugin_name_from_runtime_group(self, group: object) -> str:
        """Return the plugin name encoded in a stable or staged runtime group."""

        text = str(group or "")
        prefix = "plugin:"
        if not text.startswith(prefix):
            return text
        name = text[len(prefix):]
        if "#" in name:
            name = name.split("#", 1)[0]
        return name

    def runtime_group_failure_rows(self, name: str | None = None) -> list[list[object]]:
        """Return retained cleanup/retag/generation failure rows.

        Rows are intentionally small and command/host friendly:
        ``[plugin action group target_group surface operation detail]``.  The
        source reports remain bounded in ``runtime_group_reports``; this method
        makes their failed surfaces inspectable without exposing the internal
        dataclass shape as a UI contract.
        """

        plugin_filter = str(name or "").strip()
        rows: list[list[object]] = []
        for report in self.runtime_group_failures():
            plugin_name = self._plugin_name_from_runtime_group(report.group)
            if plugin_filter and plugin_name != plugin_filter:
                continue
            for failure in report.failures:
                rows.append([
                    plugin_name,
                    str(report.action),
                    str(report.group),
                    str(report.target_group),
                    str(failure.surface),
                    str(failure.action),
                    str(failure.detail or "failed"),
                ])
        return rows

    def _cleanup_group(self, group: str) -> RuntimeGroupOperationReport:
        return self._remember_runtime_group_report(cleanup_runtime_group(self.vm, group))

    def _retag_group(self, old: str, new: str) -> RuntimeGroupOperationReport:
        return self._remember_runtime_group_report(retag_runtime_group(self.vm, old, new))

    def _group_operation_or_restore(
        self,
        plugin_name: str,
        context: str,
        run: Callable[[], RuntimeGroupOperationReport],
        *,
        snapshot_groups: tuple[str, ...] | None = None,
    ) -> RuntimeGroupOperationReport:
        """Run a commit-critical group operation or restore pre-operation state.

        Runtime-group cleanup/retag is a multi-surface sweep.  If one surface
        fails after earlier surfaces succeeded, the caller must not continue and
        claim the plugin was unloaded or reloaded.  Snapshot just before the
        sweep, keep the full report for diagnostics, restore only group-sweep
        surfaces on failure, and raise a report-carrying MicromaxError.
        """

        group_snapshot = snapshot_runtime_group_state(self.vm, groups=snapshot_groups)
        report = run()
        if report.ok:
            return report
        restore_runtime_group_state(self.vm, group_snapshot)
        raise self._runtime_operation_error(plugin_name, context, report)

    def _cleanup_group_or_restore(
        self,
        plugin_name: str,
        group: str,
        context: str,
    ) -> RuntimeGroupOperationReport:
        return self._group_operation_or_restore(
            plugin_name,
            context,
            lambda: self._cleanup_group(group),
            snapshot_groups=(str(group),),
        )

    def _retag_group_or_restore(
        self,
        plugin_name: str,
        old: str,
        new: str,
        context: str,
    ) -> RuntimeGroupOperationReport:
        return self._group_operation_or_restore(
            plugin_name,
            context,
            lambda: self._retag_group(old, new),
            snapshot_groups=(str(old), str(new)),
        )

    def _runtime_operation_error(
        self,
        plugin_name: str,
        context: str,
        report: RuntimeGroupOperationReport,
    ) -> RuntimeGroupOperationError:
        err = RuntimeGroupOperationError(context, report)
        self._record_load_error(plugin_name, err)
        return err

    def _cleanup_plugin_generation_state(self, plugin: Plugin) -> RuntimeGroupOperationReport:
        """Remove delayed editor state owned by one committed plugin generation."""

        return self._remember_runtime_group_report(
            cleanup_plugin_generation_state(
                self.vm,
                group=self._plugin_group(plugin),
                plugin_load_root=plugin.root,
                plugin_generation=plugin.generation,
            )
        )

    def _cleanup_plugin_generation_or_restore(
        self,
        plugin_name: str,
        plugin: Plugin,
        context: str,
    ) -> RuntimeGroupOperationReport:
        snapshot = snapshot_runtime_generation_state(
            self.vm,
            plugin_load_root=plugin.root,
            plugin_generation=plugin.generation,
        )
        report = self._cleanup_plugin_generation_state(plugin)
        if report.ok:
            return report
        restore_runtime_generation_state(self.vm, snapshot)
        raise self._runtime_operation_error(plugin_name, context, report)

    def _cleanup_loaded_plugin_state_or_restore(
        self,
        plugin_name: str,
        plugin: Plugin,
        context: str,
    ) -> tuple[RuntimeGroupOperationReport, RuntimeGroupOperationReport]:
        """Commit runtime-group and generation cleanup or restore both surfaces."""

        runtime_group = self._plugin_group(plugin)
        group_snapshot = snapshot_runtime_group_state(self.vm, groups=(runtime_group,))
        generation_snapshot = snapshot_runtime_generation_state(
            self.vm,
            plugin_load_root=plugin.root,
            plugin_generation=plugin.generation,
        )
        group_report = self._cleanup_group(runtime_group)
        if not group_report.ok:
            restore_runtime_group_state(self.vm, group_snapshot)
            restore_runtime_generation_state(self.vm, generation_snapshot)
            raise self._runtime_operation_error(plugin_name, context, group_report)
        generation_report = self._cleanup_plugin_generation_state(plugin)
        if not generation_report.ok:
            restore_runtime_group_state(self.vm, group_snapshot)
            restore_runtime_generation_state(self.vm, generation_snapshot)
            raise self._runtime_operation_error(plugin_name, context, generation_report)
        return group_report, generation_report

    def _metadata_dict(self, meta_rec: PluginMeta) -> dict[str, Any]:
        """Return normalized metadata while preserving unknown plugin.json keys."""

        meta_dict: dict[str, Any] = dict(meta_rec.raw)
        meta_dict.setdefault("name", str(meta_rec.name))
        if meta_rec.version is not None:
            meta_dict.setdefault("version", str(meta_rec.version))
        if meta_rec.description is not None:
            meta_dict.setdefault("description", str(meta_rec.description))
        if meta_rec.entry is not None:
            meta_dict.setdefault("entry", str(meta_rec.entry))
        if meta_rec.requires:
            meta_dict["requires"] = list(meta_rec.requires)
        return meta_dict

    def _restore_module_mapping(self, name: str, previous: int | None) -> None:
        plugin_name = str(name)
        if previous is None:
            self.vm.modules.pop(plugin_name, None)
        else:
            self.vm.modules[plugin_name] = int(previous)

    def _word_span_tuple(self, name: str, word: object) -> tuple[str, str, int, int] | None:
        """Return compact source-span metadata for one retired VM word."""

        span = getattr(word, "span", None)
        filename = str(getattr(span, "filename", "") or "")
        if not filename:
            return None
        try:
            line = int(getattr(span, "line", 0) or 0)
            col = int(getattr(span, "col", 0) or 0)
        except Exception:
            line = 0
            col = 0
        return (str(name), filename, line, col)

    def _record_retired_wordlist(
        self,
        plugin: Plugin,
        *,
        reason: str,
    ) -> PluginWordlistTombstone | None:
        """Append a compact tombstone for a committed plugin wordlist.

        The tombstone is intentionally metadata-only.  It must never keep a
        strong reference to a retired ``Word`` object, otherwise it would merely
        move the leak from the VM dictionary to the diagnostics ledger.
        """

        wid = int(plugin.wid)
        words = self.vm.wordlists.get(wid)
        if not isinstance(words, dict):
            return None
        names = tuple(sorted(str(name) for name in words.keys()))
        spans = tuple(
            row
            for row in (
                self._word_span_tuple(str(name), word)
                for name, word in sorted(words.items(), key=lambda item: str(item[0]))
            )
            if row is not None
        )
        tombstone = PluginWordlistTombstone(
            plugin=str(plugin.name),
            root=str(plugin.root),
            wid=wid,
            generation=int(plugin.generation),
            group=str(plugin.group),
            reason=str(reason),
            word_count=len(words),
            words=names,
            spans=spans,
            package_digest=str(plugin.package_digest or ""),
            package_file_count=int(plugin.package_file_count or 0),
        )
        self.retired_wordlists.append(tombstone)
        try:
            limit = int(getattr(self, "retired_wordlist_limit", 64))
        except Exception:
            limit = 64
        if limit <= 0:
            self.retired_wordlists = []
        elif len(self.retired_wordlists) > limit:
            self.retired_wordlists = self.retired_wordlists[-limit:]
        return tombstone

    def retired_wordlist_rows(self, name: str | None = None) -> list[list[object]]:
        """Return compact retired-wordlist rows for diagnostics.

        Rows are ``[plugin reason wid generation word_count group digest root preview]``.
        ``preview`` is a bounded comma-separated word-name sample; complete names
        and spans remain available in ``retired_wordlists`` for in-process tests.
        """

        plugin_filter = str(name or "").strip()
        rows: list[list[object]] = []
        for tombstone in list(getattr(self, "retired_wordlists", [])):
            if plugin_filter and str(tombstone.plugin) != plugin_filter:
                continue
            preview_items = list(tombstone.words[:8])
            preview = ",".join(preview_items)
            if len(tombstone.words) > len(preview_items):
                preview += f",+{len(tombstone.words) - len(preview_items)}"
            rows.append([
                str(tombstone.plugin),
                str(tombstone.reason),
                int(tombstone.wid),
                int(tombstone.generation),
                int(tombstone.word_count),
                str(tombstone.group),
                str(tombstone.package_digest),
                str(tombstone.root),
                preview,
            ])
        return rows

    def _mark_retired_wordlist_words(self, plugin: Plugin, *, reason: str) -> None:
        """Mark external direct references to retired words as stale."""

        words = self.vm.wordlists.get(int(plugin.wid))
        if not isinstance(words, dict):
            return
        for word in list(words.values()):
            try:
                setattr(word, "_micromax_retired_reason", str(reason))
                setattr(word, "_micromax_retired_plugin", str(plugin.name))
                setattr(word, "_micromax_retired_generation", int(plugin.generation))
                setattr(word, "_micromax_retired_wordlist", int(plugin.wid))
            except Exception:
                continue

    def _remove_wordlist(self, wid: int) -> None:
        """Forget a plugin wordlist and scrub dictionary-indexed sidecars."""

        target = int(wid)
        if target in self.vm.search_order:
            self.vm.set_search_order([w for w in self.vm.search_order if int(w) != target])
        removed_words = self.vm.wordlists.pop(target, None)
        removed_name = self.vm.wordlist_names.pop(target, None)
        ed = getattr(self.vm, "editor_owner", None)
        forget_wordlist_authority = getattr(ed, "_forget_wordlist_authority", None)
        if callable(forget_wordlist_authority):
            forget_wordlist_authority(target)
        if removed_words is not None or removed_name is not None:
            touch = getattr(self.vm, "_touch_dict", None)
            if callable(touch):
                touch()

    def _retire_plugin_wordlist(self, plugin: Plugin, *, reason: str) -> None:
        """Replace a committed plugin wordlist with compact tombstone metadata."""

        self._record_retired_wordlist(plugin, reason=reason)
        self._mark_retired_wordlist_words(plugin, reason=reason)
        self._remove_wordlist(int(plugin.wid))

    def _replace_search_order_wid(self, old_wid: int, new_wid: int) -> None:
        """Replace a reloaded plugin wordlist while preserving search-order intent."""

        old_id = int(old_wid)
        new_id = int(new_wid)
        changed = False
        out: list[int] = []
        for wid in list(self.vm.search_order):
            current = int(wid)
            if current == old_id or current == new_id:
                if new_id not in out:
                    out.append(new_id)
                changed = True
            else:
                out.append(current)
        if changed:
            self.vm.set_search_order(out)

    def _build_plugin(
        self,
        name: str,
        *,
        init_path: Path,
        meta: PluginMeta | None,
        group: str,
        root: Path | None = None,
        allow_loaded: bool = False,
        replaces_generation: int | None = None,
        package_snapshot: PluginPackageSnapshot | None = None,
    ) -> Plugin:
        """Evaluate a plugin candidate and run startup lifecycle hooks.

        This helper is intentionally used by both ordinary load and staged
        reload.  It leaves ``vm.modules[name]`` pointing at the new wordlist only
        after source evaluation *and* ``preinit``/``init``/``postinit`` complete.
        On any failure, it restores the previous module mapping, removes grouped
        registrations made by the candidate, and forgets the uncommitted
        wordlist so a failed reload does not leak live plugin state.
        """

        plugin_name = str(name)
        if not allow_loaded and plugin_name in self.plugins:
            raise MicromaxError(f"Plugin already loaded: {plugin_name}")

        plugin_root = (
            package_snapshot.root_path
            if package_snapshot is not None
            else plugin_root_path(root if root is not None else init_path.parent)
        )
        if package_snapshot is not None:
            snap_candidate = self._candidate_from_snapshot(plugin_name, package_snapshot)
            init_path = snap_candidate.init_path
            meta_rec = snap_candidate.meta
        else:
            meta_rec = load_plugin_meta(plugin_name, plugin_root) if meta is None else meta
        meta_dict = self._metadata_dict(meta_rec)
        dict_snapshot = self._snapshot_dictionary()
        reg_snapshot = self._snapshot_registrations()
        wid = self.vm.new_wordlist(name=f"plugin:{plugin_name}")

        prev_current = self.vm.current_wid
        prev_order = list(self.vm.search_order)
        prev_group = self.vm.current_hook_group
        prev_editor_group = self.vm.current_editor_group
        committed = False
        plugin = Plugin(
            name=plugin_name,
            root=plugin_root,
            wid=wid,
            meta=meta_dict,
            group=str(group),
            generation=self._next_generation(),
            package_digest=str(package_snapshot.digest) if package_snapshot is not None else "",
            package_file_count=int(package_snapshot.file_count) if package_snapshot is not None else 0,
            package_snapshot=package_snapshot,
        )
        try:
            self.vm.modules[plugin_name] = wid
            self.vm.current_wid = wid
            self.vm.current_hook_group = str(group)
            self.vm.current_editor_group = str(group)
            self.vm.set_search_order(self.plugin_execution_search_order(plugin))
            source = (
                package_snapshot.read_text(init_path)
                if package_snapshot is not None
                else read_plugin_text(init_path, plugin_root)
            )
            with isolated_vm_execution_state(self.vm):
                with self._plugin_execution_context(
                    plugin,
                    replaces_generation=replaces_generation,
                ):
                    self.vm.eval(source, filename=str(init_path))
        except Exception:
            self._cleanup_group(str(group))
            self._restore_transaction_state(dict_snapshot, reg_snapshot)
            raise
        finally:
            self.vm.current_wid = prev_current
            self.vm.current_hook_group = prev_group
            self.vm.current_editor_group = prev_editor_group
            self.vm.set_search_order(prev_order)

        try:
            self._call_lifecycle_for(plugin, "preinit", replaces_generation=replaces_generation)
            self._call_lifecycle_for(plugin, "init", replaces_generation=replaces_generation)
            self._call_lifecycle_for(plugin, "postinit", replaces_generation=replaces_generation)
            committed = True
            return plugin
        finally:
            if not committed:
                self._cleanup_group(str(group))
                self._restore_transaction_state(dict_snapshot, reg_snapshot)

    def _resolve_init_path(self, name: str, root: Path, meta: PluginMeta) -> Path:
        """Return the contained entry file for one plugin candidate."""

        if meta.entry:
            p = Path(root) / meta.entry
            if plugin_file_exists(p, root):
                return p
            raise MicromaxError(f"Plugin entry file not found: {name}: {meta.entry}")
        for cand in ["init.mx", "init.mmx", "init.mf"]:
            p = Path(root) / cand
            if plugin_file_exists(p, root):
                return p
        raise MicromaxError(f"Plugin init file not found: {name}")

    def _check_loaded_dependencies(self, name: str, meta: PluginMeta) -> None:
        """Raise if a direct dependency is not currently loaded."""

        for dep in meta.requires:
            dep_name = str(dep)
            if dep_name not in self.plugins:
                if dep_name in self.candidates:
                    raise MicromaxError(f"dependency not loaded: {dep_name}")
                raise MicromaxError(f"missing dependency: {dep_name}")

    def _candidate_from_disk(self, name: str, root: Path) -> _PluginCandidate:
        plugin_root = plugin_root_path(root)
        meta = load_plugin_meta(str(name), plugin_root)
        init = self._resolve_init_path(str(name), plugin_root, meta)
        return _PluginCandidate(name=str(name), root=plugin_root, init_path=init, meta=meta)

    def _discovery_timeout_seconds(self) -> float:
        return normalize_worker_timeout_seconds(
            getattr(
                self,
                "plugin_discovery_timeout_seconds",
                PLUGIN_DISCOVERY_TIMEOUT_SECONDS,
            ),
            default=PLUGIN_DISCOVERY_TIMEOUT_SECONDS,
        )

    def _discovery_max_dirs(self) -> int:
        try:
            return int(getattr(self, "plugin_discovery_max_dirs", PLUGIN_DISCOVERY_MAX_DIRS))
        except Exception:
            return PLUGIN_DISCOVERY_MAX_DIRS

    def _candidate_directories(self, rootp: Path) -> list[Path]:
        """Return top-level plugin directories through a bounded list seam."""

        max_dirs = self._discovery_max_dirs()
        limit = None if max_dirs < 0 else max_dirs + 1
        try:
            entries = list_dir_contained_bounded(
                rootp,
                containment_root=rootp,
                limit=limit,
                timeout_seconds=self._discovery_timeout_seconds(),
            )
        except FilesystemOperationTimeoutError as e:
            self._record_load_error("<plugins>", f"plugin discovery timed out: {e}")
            return []
        except Exception as e:
            msg = str(e)
            if "NotADirectoryPathError" in msg or "not a directory" in msg:
                return []
            self._record_load_error("<plugins>", f"plugin discovery failed: {e}")
            return []

        if limit is not None and len(entries) > max_dirs:
            self._record_load_error(
                "<plugins>",
                f"plugin discovery: too many top-level entries: {len(entries)} > {max_dirs}",
            )
            entries = entries[:max_dirs]

        out: list[Path] = []
        for entry in sorted(entries, key=lambda row: Path(row.path).name.casefold()):
            d = Path(entry.path)
            if entry.kind == "dir":
                out.append(d)
                continue
            if entry.kind != "other":
                continue
            # ``list_dir_contained`` classifies children without following
            # symlinks.  Preserve the older behavior for symlinked plugin dirs
            # whose resolved target remains inside the configured plugin root,
            # but make the follow/check step bounded too.
            try:
                st = stat_path_contained_bounded(
                    d,
                    containment_root=rootp,
                    timeout_seconds=self._discovery_timeout_seconds(),
                )
            except Exception as e:
                self._record_load_error(d.name, f"plugin directory outside plugin root: {e}")
                continue
            if st.exists and st.kind == "dir":
                out.append(d)
        return out

    def load_available(
        self,
        name: str,
        *,
        grant: PluginLoadGrant | None = None,
        package_snapshot: PluginPackageSnapshot | None = None,
    ) -> Plugin:
        """Load a known-but-currently-unloaded plugin candidate.

        Trusted loads refresh metadata from disk.  Grant-backed restricted loads
        instead evaluate the retained immutable package snapshot so approval and
        execution cannot drift between separate filesystem reads.
        """

        plugin_name = str(name)
        if plugin_name in self.plugins:
            raise MicromaxError(f"Plugin already loaded: {plugin_name}")
        if plugin_name not in self.candidates:
            raise MicromaxError(f"Plugin is not loaded: {plugin_name}")

        record_error = True
        try:
            if grant is not None:
                grant = self._require_current_load_grant(plugin_name, grant)
                if package_snapshot is None:
                    package_snapshot = self.approved_package_snapshots.get(plugin_name)
                if package_snapshot is None:
                    disk_candidate = self.refresh_candidate(plugin_name)
                    package_snapshot = self._candidate_package_snapshot(disk_candidate)
                fresh = self._candidate_from_snapshot(plugin_name, package_snapshot)
                self.candidates[plugin_name] = fresh
                if not self._grant_matches_candidate(
                    grant,
                    fresh,
                    fingerprint=package_snapshot,
                ):
                    record_error = False
                    raise MicromaxError(f"plugin load grant is stale: {plugin_name}")
                self._check_snapshot_retention_budget(package_snapshot)
            else:
                if package_snapshot is not None:
                    record_error = False
                    raise MicromaxError(
                        f"plugin package snapshot requires an explicit load grant: {plugin_name}"
                    )
                fresh = self.refresh_candidate(plugin_name)
            self._check_loaded_dependencies(plugin_name, fresh.meta)
            plugin = self.load_plugin(
                plugin_name,
                init_path=fresh.init_path,
                meta=fresh.meta,
                root=fresh.root,
                package_snapshot=package_snapshot,
            )
            if grant is not None:
                self.approved_package_snapshots[plugin_name] = package_snapshot
                self.mark_load_grant_used(plugin_name)
            return plugin
        except Exception as e:
            if record_error:
                self._record_load_error(plugin_name, e)
            raise

    def _discover_candidates(self, rootp: Path) -> dict[str, _PluginCandidate]:
        """Scan one plugin root for metadata and contained entry files only.

        Discovery is intentionally side-effect-light: it may read plugin.json and
        check entry containment, but it must not evaluate plugin source.  Startup
        restricted mode uses this to make plugins visible without running them.
        """

        candidates: dict[str, _PluginCandidate] = {}

        for d in self._candidate_directories(rootp):
            try:
                plugin_dir = plugin_root_path(d)
                # Symlinked plugin dirs are accepted only when the resolved
                # target remains inside the configured plugin root.
                plugin_dir.relative_to(rootp)
            except Exception:
                self.load_errors.append((str(d.name), "plugin directory outside plugin root"))
                continue

            try:
                meta = load_plugin_meta(d.name, plugin_dir)
            except Exception as e:
                self.load_errors.append((str(d.name), str(e)))
                continue

            try:
                init = self._resolve_init_path(str(d.name), plugin_dir, meta)
            except MicromaxError as e:
                # Directories without an entry file are not plugins; malformed
                # candidates and containment denials should remain visible.
                msg = str(e)
                if "Plugin init file not found" not in msg:
                    self.load_errors.append((str(d.name), msg))
                continue

            candidates[str(d.name)] = _PluginCandidate(
                name=str(d.name),
                root=plugin_dir,
                init_path=init,
                meta=meta,
            )

        self.candidates = dict(candidates)
        return candidates

    def _candidate_load_order(self, candidates: dict[str, _PluginCandidate]) -> list[str]:
        """Return dependency-safe candidate names and record blocked states."""

        if not candidates:
            return []

        names = set(candidates.keys())

        blocked: set[str] = set()
        for name, cand in candidates.items():
            for dep in cand.meta.requires:
                if dep not in names:
                    self.load_errors.append((name, f"missing dependency: {dep}"))
                    blocked.add(name)
                    break

        deps: dict[str, set[str]] = {}
        indeg: dict[str, int] = {}
        for name, cand in candidates.items():
            if name in blocked:
                continue
            reqs = {d for d in cand.meta.requires if d in names and d not in blocked}
            deps[name] = reqs
            indeg[name] = len(reqs)

        ready = sorted([n for n, k in indeg.items() if k == 0])
        order: list[str] = []
        while ready:
            n = ready.pop(0)
            order.append(n)
            for m_name, reqs in deps.items():
                if n in reqs:
                    reqs.remove(n)
                    indeg[m_name] -= 1
                    if indeg[m_name] == 0:
                        ready.append(m_name)
                        ready.sort()

        remaining = sorted([n for n, k in indeg.items() if k != 0])
        if remaining:
            # Cycles cannot be satisfied by any deterministic load order.  Older
            # revisions recorded the cycle but still loaded the plugins in lexical
            # order, which left a graph that claimed dependencies were met when
            # they were not.  Keep the candidates visible, but do not activate
            # cyclic plugins until the graph is repaired.
            cyc = ", ".join(remaining)
            for n in remaining:
                self.load_errors.append((n, f"dependency cycle detected among: {cyc}"))

        return order

    def scan_tree(self, root: str | Path) -> list[str]:
        """Discover plugin candidates without evaluating plugin source.

        Restricted startup uses this path to make plugin metadata inspectable
        while avoiding automatic code execution from the workspace.
        """

        rootp = plugin_root_path(root)
        self.root = rootp
        self.clear_load_errors()
        candidates = self._discover_candidates(rootp)
        self._candidate_load_order(candidates)
        return sorted(candidates.keys(), key=lambda s: s.casefold())

    def load_tree(self, root: str | Path) -> list[Plugin]:
        """Load plugins from a directory tree.

        Each plugin is a subdirectory containing:
          - optional plugin.json
          - an entry file (default: init.mx / init.mmx / init.mf)

        If plugin.json declares `requires`, load order is dependency-aware.
        Missing dependencies are treated as non-fatal load errors (plugin skipped).
        """
        rootp = plugin_root_path(root)
        self.root = rootp
        self.clear_load_errors()
        candidates = self._discover_candidates(rootp)
        order = self._candidate_load_order(candidates)
        if not candidates:
            return []

        loaded: list[Plugin] = []
        for name in order:
            cand = candidates.get(name)
            if cand is None:
                continue
            if name in self.plugins:
                self.clear_load_errors(name)
                loaded.append(self.plugins[name])
                continue
            try:
                loaded.append(
                    self.load_plugin(name, init_path=cand.init_path, meta=cand.meta, root=cand.root)
                )
            except Exception as e:
                self._record_load_error(str(name), e)
                continue
        return loaded

    def load_plugin(
        self,
        name: str,
        *,
        init_path: Path,
        meta: PluginMeta | None = None,
        root: Path | None = None,
        package_snapshot: PluginPackageSnapshot | None = None,
    ) -> Plugin:
        plugin_name = str(name)
        plugin = self._build_plugin(
            plugin_name,
            init_path=init_path,
            meta=meta,
            group=self._stable_group(plugin_name),
            root=root,
            allow_loaded=False,
            package_snapshot=package_snapshot,
        )
        self.plugins[plugin_name] = plugin
        self.clear_load_errors(plugin_name)
        return plugin

    def loaded_dependents(self, name: str) -> list[str]:
        """Return loaded plugins that directly require *name*."""

        plugin_name = str(name)
        out: list[str] = []
        for other_name, plugin in self.plugins.items():
            if str(other_name) == plugin_name:
                continue
            requires = plugin.meta.get("requires") if isinstance(plugin.meta, dict) else []
            if any(str(dep) == plugin_name for dep in (requires or [])):
                out.append(str(other_name))
        return sorted(out)

    def unload(
        self,
        name: str,
        *,
        force: bool = False,
        run_deinit: bool = True,
    ) -> None:
        """Retire one loaded plugin generation.

        ``force=True`` preserves the operator-recovery lane: it skips dependent
        checks and plugin lifecycle code.  ``run_deinit=False`` is narrower.  It
        still refuses to strand loaded dependents and still uses transactional
        host-owned cleanup, but does not execute more plugin code.  Interactive
        revocation uses that lane so withdrawing authority cannot be blocked—or
        turned into fresh execution—by the plugin's own ``deinit`` word.
        """

        plugin_name = str(name)
        pl = self.plugins.get(plugin_name)
        if pl is None:
            return
        dependents = self.loaded_dependents(plugin_name)
        if dependents and not force:
            raise MicromaxError(f"Plugin has loaded dependents: {', '.join(dependents)}")

        if not force and run_deinit:
            dict_snapshot = self._snapshot_dictionary()
            reg_snapshot = self._snapshot_registrations()
            try:
                self._call_lifecycle_for(pl, "deinit")
            except Exception as e:
                # A failing deinit means the plugin is still the current live version.
                # Restore both dictionary/module topology and editor registrations so
                # a broken deinit cannot leave extra modules/words behind while the
                # plugin remains reported as loaded.
                self._restore_transaction_state(dict_snapshot, reg_snapshot)
                self.plugins[plugin_name] = pl
                self._record_load_error(plugin_name, e)
                raise
            # Deinit is a cleanup hook, not a dictionary-definition API.  Keep
            # messages and other host-side observations, but discard words,
            # modules, search-order changes, and runtime registration rewrites
            # made while leaving the plugin.  Group cleanup below performs the
            # committed unload state change explicitly.
            self._restore_transaction_state(dict_snapshot, reg_snapshot)

        self._cleanup_loaded_plugin_state_or_restore(
            plugin_name,
            pl,
            "plugin unload cleanup",
        )
        if self.vm.modules.get(plugin_name) == pl.wid:
            self.vm.modules.pop(plugin_name, None)
        if pl.wid in self.vm.search_order:
            self.vm.set_search_order([w for w in self.vm.search_order if int(w) != int(pl.wid)])
        del self.plugins[plugin_name]
        self.approved_package_snapshots.pop(plugin_name, None)
        self.clear_load_errors(plugin_name)
        self._retire_plugin_wordlist(pl, reason="unload")

    def reload(self, name: str, *, grant: PluginLoadGrant | None = None) -> Plugin:
        plugin_name = str(name)
        pl = self.plugins.get(plugin_name)
        if pl is None:
            return self.load_available(plugin_name, grant=grant)

        record_error = True
        try:
            package_snapshot: PluginPackageSnapshot | None = None
            if str(getattr(pl, "package_digest", "") or ""):
                try:
                    active_grant = self._require_current_load_grant(plugin_name, grant)
                except MicromaxError:
                    record_error = False
                    raise
                package_snapshot = self.approved_package_snapshots.get(plugin_name)
                if package_snapshot is None:
                    # Legacy/embedder grants may predate retained snapshots.  Capture
                    # once, then require that exact generation to match the grant.
                    disk_candidate = self._candidate_from_disk(plugin_name, pl.root)
                    package_snapshot = self._candidate_package_snapshot(disk_candidate)
                fresh = self._candidate_from_snapshot(plugin_name, package_snapshot)
                if not self._grant_matches_candidate(
                    active_grant,
                    fresh,
                    fingerprint=package_snapshot,
                ):
                    record_error = False
                    raise MicromaxError(f"plugin load grant is stale: {plugin_name}")
                self._check_snapshot_retention_budget(
                    package_snapshot,
                    replacing=plugin_name,
                )
            else:
                active_grant = None
                fresh = self._candidate_from_disk(plugin_name, pl.root)
            self.candidates[plugin_name] = fresh
            self._check_loaded_dependencies(plugin_name, fresh.meta)
        except Exception as e:
            if record_error:
                self._record_load_error(plugin_name, e)
            raise

        old_plugin = pl
        dict_snapshot = self._snapshot_dictionary()
        reg_snapshot = self._snapshot_registrations()
        stage_group = self._next_stage_group(plugin_name)
        # Temporarily remove delayed state owned by the old generation before
        # evaluating the staged replacement.  That lets a plugin reload replace
        # a same-named saved macro, while the transaction snapshot below restores
        # the old macro set if the staged load fails.
        self._cleanup_plugin_generation_or_restore(
            plugin_name,
            old_plugin,
            "plugin reload pre-stage generation cleanup",
        )
        try:
            staged = self._build_plugin(
                plugin_name,
                init_path=fresh.init_path,
                meta=fresh.meta,
                group=stage_group,
                root=fresh.root,
                allow_loaded=True,
                replaces_generation=old_plugin.generation,
                package_snapshot=package_snapshot,
            )
        except Exception as e:
            self._restore_transaction_state(dict_snapshot, reg_snapshot)
            self.plugins[plugin_name] = old_plugin
            self._record_load_error(plugin_name, e)
            raise

        # While the old plugin is running its own deinit hook, module lookups
        # for its name should still resolve to the old wordlist.  The staged
        # wordlist is promoted only after old cleanup has succeeded.
        self.vm.modules[plugin_name] = old_plugin.wid
        deinit_dict_snapshot = self._snapshot_dictionary()
        deinit_reg_snapshot = self._snapshot_registrations()
        try:
            self._call_lifecycle_for(old_plugin, "deinit")
        except Exception as e:
            self._cleanup_group(stage_group)
            self._restore_transaction_state(dict_snapshot, reg_snapshot)
            self.plugins[plugin_name] = old_plugin
            self._record_load_error(plugin_name, e)
            raise
        # Keep the staged replacement, but discard arbitrary dictionary/runtime
        # mutations made by the old plugin's cleanup hook before promotion.
        self._restore_transaction_state(deinit_dict_snapshot, deinit_reg_snapshot)

        try:
            self._cleanup_loaded_plugin_state_or_restore(
                plugin_name,
                old_plugin,
                "plugin reload cleanup old generation",
            )
            self._retag_group_or_restore(
                plugin_name,
                stage_group,
                self._stable_group(plugin_name),
                "plugin reload promote staged generation",
            )
        except RuntimeGroupOperationError:
            # A failed commit sweep means the old plugin is still the only safe
            # advertised version.  Remove staged leftovers best-effort, then
            # restore the full pre-reload transaction snapshot so partially
            # cleaned old surfaces are not left behind.
            self._cleanup_group(stage_group)
            self._restore_transaction_state(dict_snapshot, reg_snapshot)
            self.plugins[plugin_name] = old_plugin
            self.vm.modules[plugin_name] = old_plugin.wid
            raise
        staged.group = self._stable_group(plugin_name)
        self.plugins[plugin_name] = staged
        self.vm.modules[plugin_name] = staged.wid
        self._replace_search_order_wid(old_plugin.wid, staged.wid)
        self._retire_plugin_wordlist(old_plugin, reason="reload")
        if active_grant is not None:
            if package_snapshot is not None:
                self.approved_package_snapshots[plugin_name] = package_snapshot
            self.mark_load_grant_used(plugin_name)
        self.clear_load_errors(plugin_name)
        return staged


    def call_lifecycle(self, name: str, word: str) -> bool:
        pl = self.plugins.get(name)
        if pl is None:
            return False
        return self._call_lifecycle_for(pl, word)

    def _call_lifecycle_for(
        self,
        pl: Plugin,
        word: str,
        *,
        replaces_generation: int | None = None,
    ) -> bool:
        w = self.vm.find_word_in_wid(pl.wid, word)
        if w is None:
            return False
        if not isinstance(w, Word):
            return False
        prev_order = list(self.vm.search_order)
        prev_current = self.vm.current_wid
        prev_group = self.vm.current_hook_group
        prev_editor_group = self.vm.current_editor_group
        try:
            self.vm.set_search_order(self.plugin_execution_search_order(pl))
            self.vm.current_wid = pl.wid
            self.vm.current_hook_group = self._plugin_group(pl)
            self.vm.current_editor_group = self._plugin_group(pl)
            with isolated_vm_execution_state(self.vm):
                with self._plugin_execution_context(
                    pl,
                    replaces_generation=replaces_generation,
                ):
                    self.vm.exec_xt(w)
        finally:
            self.vm.set_search_order(prev_order)
            self.vm.current_wid = prev_current
            self.vm.current_hook_group = prev_group
            self.vm.current_editor_group = prev_editor_group
        return True
