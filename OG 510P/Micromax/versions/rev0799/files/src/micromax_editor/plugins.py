from __future__ import annotations

from contextlib import ExitStack, nullcontext
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from micromax import VM
from micromax.vm import MicromaxError, Word

from .plugin_meta import load_plugin_meta, PluginMeta
from .plugin_io import plugin_file_exists, plugin_root_path, read_plugin_text
from .plugin_runtime import (
    RuntimeRegistrationSnapshot,
    VmDictionarySnapshot,
    cleanup_runtime_group,
    restore_runtime_registrations,
    restore_vm_dictionary_state,
    restore_vm_execution_state,
    retag_runtime_group,
    snapshot_runtime_registrations,
    snapshot_vm_dictionary_state,
    snapshot_vm_execution_state,
)
from .vm_load_policy import plugin_load_root_context


@dataclass
class Plugin:
    name: str
    root: Path
    wid: int
    meta: dict[str, Any]
    group: str = ""
    generation: int = 0


@dataclass(frozen=True)
class _PluginCandidate:
    name: str
    root: Path
    init_path: Path
    meta: PluginMeta


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
        self.root: Path | None = None
        self._reload_serial: int = 0
        self._generation_serial: int = 0

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

    def _cleanup_group(self, group: str) -> None:
        cleanup_runtime_group(self.vm, group)

    def _retag_group(self, old: str, new: str) -> None:
        retag_runtime_group(self.vm, old, new)

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

    def _remove_wordlist(self, wid: int) -> None:
        """Forget an uncommitted plugin wordlist and scrub it from search order."""

        target = int(wid)
        if target in self.vm.search_order:
            self.vm.set_search_order([w for w in self.vm.search_order if int(w) != target])
        self.vm.wordlists.pop(target, None)
        self.vm.wordlist_names.pop(target, None)
        touch = getattr(self.vm, "_touch_dict", None)
        if callable(touch):
            touch()

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

    def load_available(self, name: str) -> Plugin:
        """Load a known-but-currently-unloaded plugin candidate.

        This is the recovery path for plugins that failed initial load or were
        dropped by an unsuccessful reload.  It re-reads plugin metadata from
        disk so fixing ``plugin.json`` or changing ``entry`` does not require a
        whole editor restart.
        """

        plugin_name = str(name)
        if plugin_name in self.plugins:
            raise MicromaxError(f"Plugin already loaded: {plugin_name}")
        cand = self.candidates.get(plugin_name)
        if cand is None:
            raise MicromaxError(f"Plugin is not loaded: {plugin_name}")

        try:
            fresh = self._candidate_from_disk(plugin_name, cand.root)
            self.candidates[plugin_name] = fresh
            self._check_loaded_dependencies(plugin_name, fresh.meta)
            return self.load_plugin(plugin_name, init_path=fresh.init_path, meta=fresh.meta, root=fresh.root)
        except Exception as e:
            self._record_load_error(plugin_name, e)
            raise

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

        candidates: dict[str, _PluginCandidate] = {}

        # Discover candidates + validate metadata early so we can sort by deps.
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

            candidates[str(d.name)] = _PluginCandidate(name=str(d.name), root=plugin_dir, init_path=init, meta=meta)

        # Preserve candidates for inspection/UX even if some are blocked or not loaded.
        self.candidates = dict(candidates)

        if not candidates:
            return []

        names = set(candidates.keys())

        # Filter plugins with missing deps.
        blocked: set[str] = set()
        for name, cand in candidates.items():
            for dep in cand.meta.requires:
                if dep not in names:
                    self.load_errors.append((name, f"missing dependency: {dep}"))
                    blocked.add(name)
                    break

        # Toposort by requires; cyclic plugins remain available but unloaded.
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

        loaded: list[Plugin] = []
        for name in order:
            if name in blocked:
                continue
            cand = candidates.get(name)
            if cand is None:
                continue
            if name in self.plugins:
                self.clear_load_errors(name)
                loaded.append(self.plugins[name])
                continue
            try:
                loaded.append(self.load_plugin(name, init_path=cand.init_path, meta=cand.meta, root=cand.root))
            except Exception as e:
                self._record_load_error(str(name), e)
                continue
        return loaded

    def load_plugin(self, name: str, *, init_path: Path, meta: PluginMeta | None = None, root: Path | None = None) -> Plugin:
        plugin_name = str(name)
        plugin = self._build_plugin(
            plugin_name,
            init_path=init_path,
            meta=meta,
            group=self._stable_group(plugin_name),
            root=root,
            allow_loaded=False,
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

        self._cleanup_group(self._plugin_group(pl))
        if self.vm.modules.get(plugin_name) == pl.wid:
            self.vm.modules.pop(plugin_name, None)
        if pl.wid in self.vm.search_order:
            self.vm.set_search_order([w for w in self.vm.search_order if int(w) != int(pl.wid)])
        del self.plugins[plugin_name]
        self.clear_load_errors(plugin_name)
        # NOTE: we do not yet GC committed wordlists by default; they remain in
        # vm.wordlists for historical/provenance inspection.  Live module/search
        # surfaces and grouped handlers are scrubbed so unloaded plugins stop
        # participating in runtime lookup.

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
        try:
            staged = self._build_plugin(
                plugin_name,
                init_path=fresh.init_path,
                meta=fresh.meta,
                group=stage_group,
                root=fresh.root,
                allow_loaded=True,
                replaces_generation=old_plugin.generation,
            )
        except Exception as e:
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

        self._cleanup_group(self._plugin_group(old_plugin))
        self._retag_group(stage_group, self._stable_group(plugin_name))
        staged.group = self._stable_group(plugin_name)
        self.plugins[plugin_name] = staged
        self.vm.modules[plugin_name] = staged.wid
        self._replace_search_order_wid(old_plugin.wid, staged.wid)
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
