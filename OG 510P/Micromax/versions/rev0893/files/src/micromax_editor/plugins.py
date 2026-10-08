from __future__ import annotations

from contextlib import ExitStack, nullcontext
import hashlib
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

from micromax import VM
from micromax.vm import MicromaxError, Word

from .plugin_meta import load_plugin_meta, PluginMeta
from .plugin_grants import PluginLoadGrant
from .plugin_io import DEFAULT_PLUGIN_MAX_BYTES, plugin_file_exists, plugin_root_path, read_plugin_bytes, read_plugin_text
from .plugin_runtime import (
    RuntimeGroupOperationError,
    RuntimeGroupOperationReport,
    RuntimeRegistrationSnapshot,
    VmDictionarySnapshot,
    cleanup_plugin_generation_state,
    cleanup_runtime_group,
    restore_runtime_generation_state,
    restore_runtime_group_state,
    restore_runtime_registrations,
    restore_vm_dictionary_state,
    restore_vm_execution_state,
    retag_runtime_group,
    snapshot_runtime_generation_state,
    snapshot_runtime_group_state,
    snapshot_runtime_registrations,
    snapshot_vm_dictionary_state,
    snapshot_vm_execution_state,
)
from .vm_load_policy import plugin_load_root_context


PLUGIN_PACKAGE_MAX_FILES = 512
PLUGIN_PACKAGE_MAX_TOTAL_BYTES = 8 * DEFAULT_PLUGIN_MAX_BYTES


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
        fingerprint: _PluginPackageFingerprint | None = None,
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
        """Return the contained files that make up the approved plugin package.

        A restricted workspace grant approves the plugin bytes visible at the
        time of the user's explicit ``plugin load NAME`` decision.  Include all
        ordinary files under the plugin root rather than only ``init.mx`` so a
        later edit to an included helper file also makes the grant stale.  Each
        file read below still goes through fd-backed plugin containment before it
        contributes to the digest.
        """

        root = plugin_root_path(cand.root)
        try:
            max_files = int(getattr(self, "package_fingerprint_max_files", PLUGIN_PACKAGE_MAX_FILES))
        except Exception:
            max_files = PLUGIN_PACKAGE_MAX_FILES
        paths: list[Path] = []
        try:
            iterator = root.rglob("*")
        except OSError as e:
            raise MicromaxError(f"plugin fingerprint: cannot scan {cand.name}: {e}") from e
        for path in iterator:
            try:
                if path.is_dir():
                    continue
                if not path.is_file():
                    continue
                path.relative_to(root)
            except Exception as e:
                raise MicromaxError(f"plugin fingerprint: file outside plugin root: {path}") from e
            paths.append(path)
            if max_files >= 0 and len(paths) > max_files:
                raise MicromaxError(
                    f"plugin fingerprint: too many files for {cand.name}: {len(paths)} > {max_files}"
                )
        if cand.init_path not in paths:
            paths.append(cand.init_path)
            if max_files >= 0 and len(paths) > max_files:
                raise MicromaxError(
                    f"plugin fingerprint: too many files for {cand.name}: {len(paths)} > {max_files}"
                )
        return sorted(set(paths), key=lambda p: p.relative_to(root).as_posix())

    def _candidate_package_fingerprint(self, cand: _PluginCandidate) -> _PluginPackageFingerprint:
        """Return a deterministic digest for the candidate's current package bytes."""

        root = plugin_root_path(cand.root)
        try:
            max_total = int(
                getattr(self, "package_fingerprint_max_total_bytes", PLUGIN_PACKAGE_MAX_TOTAL_BYTES)
            )
        except Exception:
            max_total = PLUGIN_PACKAGE_MAX_TOTAL_BYTES
        h = hashlib.sha256()
        count = 0
        total_bytes = 0
        for path in self._candidate_package_paths(cand):
            rel = path.relative_to(root).as_posix()
            data = read_plugin_bytes(path, root)
            total_bytes += len(data)
            if max_total >= 0 and total_bytes > max_total:
                raise MicromaxError(
                    f"plugin fingerprint: package too large for {cand.name}: {total_bytes} > {max_total} bytes"
                )
            file_hash = hashlib.sha256(data).hexdigest()
            h.update(rel.encode("utf-8", "surrogateescape"))
            h.update(b"\0")
            h.update(str(len(data)).encode("ascii"))
            h.update(b"\0")
            h.update(file_hash.encode("ascii"))
            h.update(b"\n")
            count += 1
        return _PluginPackageFingerprint(digest="sha256:" + h.hexdigest(), file_count=int(count))

    def refresh_candidate(self, name: str) -> _PluginCandidate:
        """Re-read one candidate's metadata and contained entry path from disk."""

        plugin_name = str(name)
        fresh = self._candidate_from_disk(plugin_name, self._candidate_root_for_grant(plugin_name))
        self.candidates[plugin_name] = fresh
        return fresh

    def grant_load(
        self,
        name: str,
        *,
        issuer: str = "user",
        duration: str = "session",
        provenance: str = "",
    ) -> PluginLoadGrant:
        """Record an explicit approval to evaluate one plugin candidate.

        The grant is bound to the candidate's current root, entry file,
        and package digest.  Later metadata, entry-path, or same-path package
        byte changes invalidate the grant until the user runs the explicit load
        command again.
        """

        plugin_name = str(name)
        fresh = self.refresh_candidate(plugin_name)
        fp = self._candidate_package_fingerprint(fresh)
        grant = PluginLoadGrant(
            plugin=plugin_name,
            root=str(fresh.root),
            entry=str(fresh.init_path),
            package_digest=str(fp.digest),
            package_file_count=int(fp.file_count),
            issuer=str(issuer or "user"),
            duration=str(duration or "session"),
            provenance=str(provenance or ""),
            issued_at=self._next_grant_serial(),
        )
        self.load_grants[plugin_name] = grant
        return grant

    def active_load_grant(self, name: str, *, refresh: bool = False) -> PluginLoadGrant | None:
        """Return the active grant for *name* when it still matches disk."""

        plugin_name = str(name)
        grant = self.load_grants.get(plugin_name)
        if grant is None or grant.revoked:
            return None
        try:
            cand = self.refresh_candidate(plugin_name) if refresh else self.candidates.get(plugin_name)
        except Exception:
            return None
        if cand is None:
            return None
        if not self._grant_matches_candidate(grant, cand):
            return None
        return grant

    def _loaded_plugin_record(self, plugin: Plugin | str) -> Plugin | None:
        """Return the loaded plugin record named by *plugin*, if any."""

        if isinstance(plugin, Plugin):
            return plugin
        return self.plugins.get(str(plugin))

    def loaded_plugin_package_current(
        self,
        plugin: Plugin | str,
        *,
        require_digest: bool = False,
    ) -> bool:
        """Return whether a loaded plugin still matches its committed package bytes.

        Restricted workspaces give loaded plugin callbacks package-local include
        authority only while the files on disk still match the bytes that were
        evaluated for that loaded generation.  Trusted loads often have no
        package digest because they predate or deliberately bypass manual grants;
        callers that are enforcing restricted trust should set ``require_digest``
        so missing evidence fails closed.
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

        Content freshness alone is not enough in a restricted workspace: revoking
        the session grant should stop *future* lazy includes even though already
        evaluated plugin words may still run until the plugin is unloaded.
        """

        pl = self._loaded_plugin_record(plugin)
        if pl is None:
            return False
        if not self.loaded_plugin_package_current(pl, require_digest=require_digest):
            return False
        digest = str(getattr(pl, "package_digest", "") or "")
        if not digest:
            return not bool(require_digest)
        grant = self.active_load_grant(str(pl.name), refresh=True)
        if grant is None:
            return False
        return str(grant.package_digest) == digest

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
        return True

    def load_grant_rows(self) -> list[list[object]]:
        """Return small diagnostic rows for session plugin-load grants."""

        rows: list[list[object]] = []
        for name in sorted(self.load_grants, key=lambda s: str(s).casefold()):
            grant = self.load_grants[name]
            state = "revoked" if grant.revoked else ("active" if self.active_load_grant(name) else "stale")
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
        root: Path,
        generation: int | None = None,
        *,
        replaces_generation: int | None = None,
    ):
        """Evaluate plugin code with script authority plus package-local loads."""

        stack = ExitStack()
        stack.enter_context(
            plugin_load_root_context(
                self.vm,
                root,
                generation=generation,
                replaces_generation=replaces_generation,
            )
        )
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
        package_fingerprint: _PluginPackageFingerprint | None = None,
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

        plugin_root = plugin_root_path(root if root is not None else init_path.parent)
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
            package_digest=str(package_fingerprint.digest) if package_fingerprint is not None else "",
            package_file_count=int(package_fingerprint.file_count) if package_fingerprint is not None else 0,
        )
        try:
            self.vm.modules[plugin_name] = wid
            self.vm.current_wid = wid
            self.vm.current_hook_group = str(group)
            self.vm.current_editor_group = str(group)
            self.vm.set_search_order([wid] + [w for w in prev_order if int(w) != int(wid)])
            source_snapshot = snapshot_vm_execution_state(self.vm)
            try:
                source = read_plugin_text(init_path, plugin_root)
                with self._plugin_execution_context(
                    plugin_root,
                    plugin.generation,
                    replaces_generation=replaces_generation,
                ):
                    self.vm.eval(source, filename=str(init_path))
            finally:
                restore_vm_execution_state(self.vm, source_snapshot)
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

    def load_available(self, name: str, *, grant: PluginLoadGrant | None = None) -> Plugin:
        """Load a known-but-currently-unloaded plugin candidate.

        This is the recovery path for plugins that failed initial load or were
        dropped by an unsuccessful reload.  It re-reads plugin metadata from
        disk so fixing ``plugin.json`` or changing ``entry`` does not require a
        whole editor restart.
        """

        plugin_name = str(name)
        if plugin_name in self.plugins:
            raise MicromaxError(f"Plugin already loaded: {plugin_name}")
        if plugin_name not in self.candidates:
            raise MicromaxError(f"Plugin is not loaded: {plugin_name}")

        try:
            fresh = self.refresh_candidate(plugin_name)
            fp = self._candidate_package_fingerprint(fresh)
            if grant is not None and not self._grant_matches_candidate(grant, fresh, fingerprint=fp):
                raise MicromaxError(f"plugin load grant is stale: {plugin_name}")
            self._check_loaded_dependencies(plugin_name, fresh.meta)
            plugin = self.load_plugin(
                plugin_name,
                init_path=fresh.init_path,
                meta=fresh.meta,
                root=fresh.root,
                package_fingerprint=fp if grant is not None else None,
            )
            if grant is not None:
                self.mark_load_grant_used(plugin_name)
            return plugin
        except Exception as e:
            self._record_load_error(plugin_name, e)
            raise

    def _discover_candidates(self, rootp: Path) -> dict[str, _PluginCandidate]:
        """Scan one plugin root for metadata and contained entry files only.

        Discovery is intentionally side-effect-light: it may read plugin.json and
        check entry containment, but it must not evaluate plugin source.  Startup
        restricted mode uses this to make plugins visible without running them.
        """

        candidates: dict[str, _PluginCandidate] = {}

        for d in sorted(p for p in rootp.iterdir() if p.is_dir()):
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
        if not rootp.exists():
            self.candidates = {}
            return []

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
        if not rootp.exists():
            self.candidates = {}
            return []

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
        package_fingerprint: _PluginPackageFingerprint | None = None,
    ) -> Plugin:
        plugin_name = str(name)
        plugin = self._build_plugin(
            plugin_name,
            init_path=init_path,
            meta=meta,
            group=self._stable_group(plugin_name),
            root=root,
            allow_loaded=False,
            package_fingerprint=package_fingerprint,
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

    def unload(self, name: str, *, force: bool = False) -> None:
        plugin_name = str(name)
        pl = self.plugins.get(plugin_name)
        if pl is None:
            return
        dependents = self.loaded_dependents(plugin_name)
        if dependents and not force:
            raise MicromaxError(f"Plugin has loaded dependents: {', '.join(dependents)}")

        if not force:
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
        self.clear_load_errors(plugin_name)
        self._retire_plugin_wordlist(pl, reason="unload")

    def reload(self, name: str) -> Plugin:
        plugin_name = str(name)
        pl = self.plugins.get(plugin_name)
        if pl is None:
            return self.load_available(plugin_name)

        try:
            fresh = self._candidate_from_disk(plugin_name, pl.root)
            self.candidates[plugin_name] = fresh
            self._check_loaded_dependencies(plugin_name, fresh.meta)
        except Exception as e:
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
            fp = self._candidate_package_fingerprint(fresh) if str(getattr(old_plugin, "package_digest", "") or "") else None
            staged = self._build_plugin(
                plugin_name,
                init_path=fresh.init_path,
                meta=fresh.meta,
                group=stage_group,
                root=fresh.root,
                allow_loaded=True,
                replaces_generation=old_plugin.generation,
                package_fingerprint=fp,
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
        exec_snapshot = snapshot_vm_execution_state(self.vm)
        try:
            if pl.wid not in self.vm.search_order:
                self.vm.set_search_order([pl.wid] + prev_order)
            self.vm.current_wid = pl.wid
            self.vm.current_hook_group = self._plugin_group(pl)
            self.vm.current_editor_group = self._plugin_group(pl)
            with self._plugin_execution_context(
                pl.root,
                pl.generation,
                replaces_generation=replaces_generation,
            ):
                self.vm.exec_xt(w)
        finally:
            restore_vm_execution_state(self.vm, exec_snapshot)
            self.vm.set_search_order(prev_order)
            self.vm.current_wid = prev_current
            self.vm.current_hook_group = prev_group
            self.vm.current_editor_group = prev_editor_group
        return True
