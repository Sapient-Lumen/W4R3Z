from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from micromax import VM
from micromax.vm import MicromaxError, Word

from .plugin_meta import load_plugin_meta, PluginMeta


@dataclass
class Plugin:
    name: str
    root: Path
    wid: int
    meta: dict[str, Any]


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
      - hot reload is just "forget and load" (for now)
      - lifecycle words are optional: preinit/init/postinit/deinit

    Inspired by micro's plugin help topic which describes lifecycle callbacks
    like `preinit`, `init`, `postinit`, and `deinit`. (See micro runtime help.)
    """

    def __init__(self, vm: VM) -> None:
        self.vm = vm
        self.plugins: dict[str, Plugin] = {}
        # Non-fatal plugin load errors captured during load_tree().
        self.load_errors: list[tuple[str, str]] = []
        # Last scanned plugin candidates (including those blocked by deps).
        self.candidates: dict[str, _PluginCandidate] = {}
        self.root: Path | None = None

    def load_tree(self, root: str | Path) -> list[Plugin]:
        """Load plugins from a directory tree.

        Each plugin is a subdirectory containing:
          - optional plugin.json
          - an entry file (default: init.mx / init.mmx / init.mf)

        If plugin.json declares `requires`, load order is dependency-aware.
        Missing dependencies are treated as non-fatal load errors (plugin skipped).
        """
        rootp = Path(root)
        self.root = rootp
        if not rootp.exists():
            self.candidates = {}
            return []

        candidates: dict[str, _PluginCandidate] = {}

        # Discover candidates + validate metadata early so we can sort by deps.
        for d in sorted(p for p in rootp.iterdir() if p.is_dir()):
            try:
                meta = load_plugin_meta(d.name, d)
            except Exception as e:
                self.load_errors.append((str(d.name), str(e)))
                continue

            init: Path | None = None
            if meta.entry:
                init = d / meta.entry
            else:
                for cand in ["init.mx", "init.mmx", "init.mf"]:
                    if (d / cand).exists():
                        init = d / cand
                        break

            if init is None:
                continue

            candidates[str(d.name)] = _PluginCandidate(name=str(d.name), root=d, init_path=init, meta=meta)

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

        # Toposort by requires (best-effort; cycles fall back to lexical order).
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
            # cycle (or something inconsistent): record and load remaining in lexical order.
            cyc = ", ".join(remaining)
            for n in remaining:
                self.load_errors.append((n, f"dependency cycle detected among: {cyc}"))
            order.extend(remaining)

        loaded: list[Plugin] = []
        for name in order:
            if name in blocked:
                continue
            cand = candidates.get(name)
            if cand is None:
                continue
            try:
                loaded.append(self.load_plugin(name, init_path=cand.init_path, meta=cand.meta))
            except Exception as e:
                self.load_errors.append((str(name), str(e)))
                continue
        return loaded

    def load_plugin(self, name: str, *, init_path: Path, meta: PluginMeta | None = None) -> Plugin:
        if name in self.plugins:
            raise MicromaxError(f"Plugin already loaded: {name}")

        if meta is None:
            meta_rec = load_plugin_meta(name, init_path.parent)
        else:
            meta_rec = meta
        # Store normalized metadata (preserve unknown keys, but ensure core fields exist).
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

        wid = self.vm.new_wordlist(name=f"plugin:{name}")
        self.vm.modules[name] = wid

        prev_current, prev_order = self.vm.current_wid, list(self.vm.search_order)
        prev_group = self.vm.current_hook_group
        prev_editor_group = self.vm.current_editor_group
        try:
            self.vm.current_wid = wid
            self.vm.current_hook_group = f"plugin:{name}"
            self.vm.current_editor_group = f"plugin:{name}"
            self.vm.set_search_order([wid] + [w for w in prev_order if w != wid])
            try:
                self.vm.eval(init_path.read_text(encoding="utf-8"), filename=str(init_path))
            except Exception as e:
                # Best-effort cleanup so a half-loaded plugin doesn't leak hooks/commands/bindings.
                group = f"plugin:{name}"
                try:
                    self.vm.remove_hook_group(group)
                except Exception:
                    pass
                ed = getattr(self.vm, "editor_owner", None)
                if ed is not None:
                    try:
                        ed.command_dispatcher.remove_group(group)
                    except Exception:
                        pass
                    try:
                        ed.keymap.remove_group(group)
                    except Exception:
                        pass
                    try:
                        ed.timers.cancel_group(group)
                    except Exception:
                        pass
                self.vm.modules.pop(name, None)
                raise
        finally:
            self.vm.current_wid = prev_current
            self.vm.current_hook_group = prev_group
            self.vm.current_editor_group = prev_editor_group
            self.vm.set_search_order(prev_order)

        pl = Plugin(name=name, root=init_path.parent, wid=wid, meta=meta_dict)
        self.plugins[name] = pl

        # lifecycle: init
        self.call_lifecycle(name, "preinit")
        self.call_lifecycle(name, "init")
        self.call_lifecycle(name, "postinit")
        return pl

    def unload(self, name: str) -> None:
        pl = self.plugins.get(name)
        if pl is None:
            return
        self.call_lifecycle(name, "deinit")
        group = f"plugin:{name}"
        self.vm.remove_hook_group(group)
        ed = getattr(self.vm, "editor_owner", None)
        if ed is not None:
            ed.command_dispatcher.remove_group(group)
            ed.keymap.remove_group(group)
            try:
                ed.timers.cancel_group(group)
            except Exception:
                pass
        del self.plugins[name]
        # NOTE: we do not yet GC wordlists; they remain in vm.wordlists.
        # Hook-group cleanup keeps stale handlers from surviving reloads.

    def reload(self, name: str) -> Plugin:
        pl = self.plugins.get(name)
        if pl is None:
            raise MicromaxError(f"Plugin is not loaded: {name}")

        # Prefer explicit `entry` from plugin.json (rev69+), then fall back to init.*.
        entry = ""
        try:
            entry = str(pl.meta.get("entry") or "").strip()
        except Exception:
            entry = ""
        init: Path | None = None
        if entry:
            cand = pl.root / entry
            if not cand.exists():
                raise MicromaxError(f"Plugin entry not found: {name} ({entry})")
            init = cand

        if init is None:
            for cand in ["init.mx", "init.mmx", "init.mf"]:
                if (pl.root / cand).exists():
                    init = pl.root / cand
                    break
        if init is None:
            raise MicromaxError(f"Plugin init file not found: {name}")

        self.unload(name)
        try:
            return self.load_plugin(name, init_path=init)
        except Exception as e:
            self.load_errors.append((name, str(e)))
            raise


    def call_lifecycle(self, name: str, word: str) -> bool:
        pl = self.plugins.get(name)
        if pl is None:
            return False
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
            if pl.wid not in self.vm.search_order:
                self.vm.set_search_order([pl.wid] + prev_order)
            self.vm.current_wid = pl.wid
            self.vm.current_hook_group = f"plugin:{name}"
            self.vm.current_editor_group = f"plugin:{name}"
            self.vm.exec_xt(w)
        finally:
            self.vm.set_search_order(prev_order)
            self.vm.current_wid = prev_current
            self.vm.current_hook_group = prev_group
            self.vm.current_editor_group = prev_editor_group
        return True
