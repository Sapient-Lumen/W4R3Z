from __future__ import annotations

from .command_authority import script_code_load_allowed
from .command_formatters import (
    _plugin_dependency_entry,
    _plugin_error_count_line,
    _plugin_inventory_entry,
    _plugin_inventory_entry_from_row,
    _plugin_inventory_state,
    _plugin_inventory_state_from_row,
    _plugin_runtime_error_line,
    _plugin_runtime_root_summary,
    _plugin_zero_error_state_suffix,
)

PLUGIN_ROOT_DOC = "plugin list|load NAME|unload NAME|reload NAME|info NAME|errors [NAME]|cleanup [NAME]|grants|revoke NAME"
PLUGIN_USAGE = "usage: plugin list|load NAME|unload NAME|reload NAME|info NAME|errors [NAME]|cleanup [NAME]|grants|revoke NAME"


def _cleanup_failure_line(row: list[object]) -> str:
    """Return one compact retained cleanup-failure diagnostic line."""

    plugin = str(row[0] if len(row) > 0 else "")
    action = str(row[1] if len(row) > 1 else "")
    target = str(row[3] if len(row) > 3 else "")
    surface = str(row[4] if len(row) > 4 else "")
    op = str(row[5] if len(row) > 5 else "")
    detail = str(row[6] if len(row) > 6 else "failed")
    head = plugin
    if action:
        head += f" {action}"
    if target:
        head += f" {target}"
    surface_op = ".".join(part for part in [surface, op] if part)
    if surface_op:
        head += f" {surface_op}"
    return f"  - {head}: {detail}"


def c_plugin(ed: "Editor", args: list[str]) -> bool:
    if not args:
        ed.message(_plugin_runtime_root_summary(ed))
        ed.message(PLUGIN_USAGE)
        return False
    sub = args[0]
    if sub == "list":
        if getattr(ed, "plugin_manager", None) is None:
            ed.message("plugin list: no plugin manager")
            return False
        rows = ed.plugin_inventory_rows()
        if not rows:
            ed.message("plugin list: 0 plugin(s)")
            return True
        parts = [_plugin_inventory_entry_from_row(list(row)) for row in rows]
        counts = {"error": 0, "loaded": 0, "available": 0}
        for row in rows:
            state = _plugin_inventory_state_from_row(list(row))
            counts[state] = counts.get(state, 0) + 1
        count_parts = [
            f"{counts['error']} error" + ("s" if counts['error'] != 1 else "")
            for _k in [0]
            if counts['error']
        ]
        count_parts += [
            f"{counts['loaded']} loaded"
            for _k in [0]
            if counts['loaded']
        ]
        count_parts += [
            f"{counts['available']} available"
            for _k in [0]
            if counts['available']
        ]
        prefix = f"plugin list: {len(rows)} plugin(s)"
        if count_parts:
            prefix += " (" + ", ".join(count_parts) + ")"
        ed.message(prefix + "; " + "; ".join(parts))
        return True
    if sub == "load" and len(args) >= 2:
        try:
            script_restricted = bool(ed.in_script_context() and ed._workspace_restricted())
        except Exception:
            script_restricted = False
        if script_restricted:
            ed.message("plugin load: disabled for scripts in restricted workspace")
            return False
        if not script_code_load_allowed(ed, "plugin load"):
            return False
        return ed.plugin_load_with_feedback(str(args[1]))
    if sub == "unload" and len(args) >= 2:
        try:
            if ed.in_script_context():
                ed.message("plugin unload: disabled for scripts")
                return False
        except Exception:
            pass
        return ed.plugin_unload_with_feedback(str(args[1]))
    if sub == "reload" and len(args) >= 2:
        if not script_code_load_allowed(ed, "plugin reload"):
            return False
        return ed.plugin_reload_with_feedback(str(args[1]))
    if sub == "grants":
        pm = ed.plugin_manager
        if not pm:
            ed.message("plugin grants: no plugin manager")
            return False
        try:
            if bool(ed.in_script_context() and not ed._script_plugin_read_capability_enabled()):
                ed.message("plugin grants: hidden in script context (cap.plugin-read)")
                return False
        except Exception:
            pass
        rows = ed.plugin_load_grant_rows(verify_disk=True)
        if not rows:
            ed.message("plugin grants: 0 grant(s)")
            return True
        parts = [ed._plugin_grant_entry_from_row(list(row)) for row in rows]
        ed.message(f"plugin grants: {len(rows)} grant(s); " + "; ".join(parts))
        return True
    if sub == "revoke" and len(args) >= 2:
        try:
            if ed.in_script_context():
                ed.message("plugin revoke: disabled for scripts")
                return False
        except Exception:
            pass
        return ed.plugin_revoke_with_feedback(str(args[1]))
    if sub == "errors":
        pm = ed.plugin_manager
        if not pm:
            ed.message("plugin errors: no plugin manager")
            return False
        flt = args[1] if len(args) >= 2 else ""
        if flt:
            name = str(flt)
            try:
                ed._guard_plugin_read(name, action="read")
            except PermissionError:
                ed.message(f"plugin errors: no such plugin: {name}")
                return False
        errs = [
            (n, e)
            for (n, e) in getattr(pm, "load_errors", [])
            if (not flt or str(n) == str(flt))
            and (bool(flt) or ed._plugin_read_allowed(str(n)))
        ]
        if flt:
            name = str(flt)
            loaded = bool(name in getattr(pm, "plugins", {}))
            cand = getattr(pm, "candidates", {}).get(name) if hasattr(pm, "candidates") else None
            if cand is None and not loaded and not errs:
                ed.message(f"plugin errors: no such plugin: {name}")
                return False
            ed.message(f"plugin errors: {_plugin_inventory_entry(ed, name)}")
            if not errs:
                ed.message(_plugin_error_count_line(0, _plugin_zero_error_state_suffix(ed, name)))
                return True
            ed.message(_plugin_runtime_error_line(len(errs), str(errs[-1][1]) if errs else ""))
            if len(errs) > 1:
                for _n, err in errs[-50:]:
                    ed.message(f"    - {err}")
            return True
        if not errs:
            inventory = ed.plugin_inventory_rows()
            summary = "plugin errors: 0 plugin(s), 0 error(s)"
            if inventory:
                summary += f" · {len(inventory)} plugin total"
                summary += f" · e.g. {_plugin_inventory_entry_from_row(list(inventory[0]))}"
            ed.message(summary)
            return True
        grouped: dict[str, list[str]] = {}
        order: list[str] = []
        for n, err in errs:
            name = str(n)
            if name not in grouped:
                grouped[name] = []
                order.append(name)
            grouped[name].append(str(err))
        ed.message(f"plugin errors: {len(grouped)} plugin(s), {len(errs)} error(s)")
        for name in order[-50:]:
            item_errs = grouped.get(name, [])
            label = "error" if len(item_errs) == 1 else "errors"
            ed.message(f"  - {_plugin_inventory_entry(ed, name)} ({len(item_errs)} {label})")
            for err in item_errs[-50:]:
                ed.message(f"    - {err}")
        return True
    if sub == "cleanup":
        pm = ed.plugin_manager
        if not pm:
            ed.message("plugin cleanup: no plugin manager")
            return False
        flt = args[1] if len(args) >= 2 else ""
        if flt:
            name = str(flt)
            try:
                known = name in ed._all_plugin_names()
            except Exception:
                known = False
            try:
                ed._guard_plugin_read(name, action="read")
            except PermissionError:
                ed.message(f"plugin cleanup: no such plugin: {name}")
                return False
            rows = ed.plugin_cleanup_failure_rows(name)
            if not rows and not known:
                ed.message(f"plugin cleanup: no such plugin: {name}")
                return False
            if not rows:
                ed.message(f"plugin cleanup {name}: 0 cleanup failure(s)")
                return True
            ed.message(f"plugin cleanup {name}: {len(rows)} failure(s)")
            for row in rows[-50:]:
                ed.message(_cleanup_failure_line(list(row)))
            return True
        rows = ed.plugin_cleanup_failure_rows()
        if not rows:
            inventory = ed.plugin_inventory_rows()
            summary = "plugin cleanup: 0 cleanup failure(s)"
            if inventory:
                summary += f" · {len(inventory)} plugin total"
                summary += f" · e.g. {_plugin_inventory_entry_from_row(list(inventory[0]))}"
            ed.message(summary)
            return True
        plugins = []
        seen = set()
        for row in rows:
            name = str(row[0] if row else "")
            if name and name not in seen:
                seen.add(name)
                plugins.append(name)
        ed.message(f"plugin cleanup: {len(plugins)} plugin(s), {len(rows)} failure(s)")
        for row in rows[-50:]:
            ed.message(_cleanup_failure_line(list(row)))
        return True

    if sub == "info" and len(args) >= 2:
        pm = ed.plugin_manager
        if not pm:
            ed.message("plugin info: no plugin manager")
            return False
        name = args[1]
        try:
            ed._guard_plugin_read(str(name), action="read")
        except PermissionError:
            ed.message(f"plugin info: no such plugin: {name}")
            return False
        loaded = bool(name in getattr(pm, "plugins", {}))
        cand = getattr(pm, "candidates", {}).get(name) if hasattr(pm, "candidates") else None
        errs = [e for (n, e) in getattr(pm, "load_errors", []) if str(n) == str(name)]
        if cand is None and not loaded and not errs:
            ed.message(f"plugin info: no such plugin: {name}")
            return False
        ed.message(f"plugin info: {_plugin_inventory_entry(ed, name)}")
        version = ""
        desc = ""
        reqs: list[str] = []
        entry = ""
        root = ""
        try:
            if cand is not None:
                version = str(cand.meta.version or "")
                desc = str(cand.meta.description or "")
                reqs = list(cand.meta.requires or [])
                entry = str(cand.meta.entry or "")
                root = str(cand.root)
            elif loaded:
                pl = pm.plugins.get(name)
                if pl is not None:
                    root = str(pl.root)
                    meta = pl.meta or {}
                    version = str(meta.get("version") or "")
                    desc = str(meta.get("description") or "")
                    entry = str(meta.get("entry") or "")
                    reqs = list(meta.get("requires") or [])
        except Exception:
            pass
        if version:
            ed.message(f"  version: {version}")
        if entry:
            ed.message(f"  entry: {entry}")
        if root:
            ed.message(f"  root: {root}")
        if desc:
            ed.message(f"  desc: {desc}")
        retired_rows: list[list[object]] = []
        try:
            retired_wordlist_rows = getattr(pm, "retired_wordlist_rows", None)
            if callable(retired_wordlist_rows):
                retired_rows = [list(row) for row in retired_wordlist_rows(str(name))]
        except Exception:
            retired_rows = []
        if retired_rows:
            retired_words = 0
            for row in retired_rows:
                try:
                    retired_words += int(row[4])
                except Exception:
                    pass
            label = "wordlist" if len(retired_rows) == 1 else "wordlists"
            ed.message(f"  retired wordlists: {len(retired_rows)} {label}, {retired_words} word(s) compacted")
        dep_counts = {"loaded": 0, "error": 0, "missing": 0, "available": 0}
        for dep in reqs:
            state = _plugin_inventory_state(ed, dep)
            pm_dep = getattr(ed, "plugin_manager", None)
            dep_name = str(dep)
            known = False
            if pm_dep is not None:
                try:
                    known = bool(dep_name in getattr(pm_dep, "plugins", {}))
                except Exception:
                    known = False
                if not known:
                    try:
                        known = getattr(pm_dep, "candidates", {}).get(dep_name) is not None if hasattr(pm_dep, "candidates") else False
                    except Exception:
                        known = False
                if not known:
                    try:
                        known = any(str(n) == dep_name for (n, _e) in getattr(pm_dep, "load_errors", []))
                    except Exception:
                        known = False
            if not known:
                state = "missing"
            dep_counts[state] = dep_counts.get(state, 0) + 1
        dep_count_parts = [
            f"{dep_counts['loaded']} loaded"
            for _k in [0]
            if dep_counts['loaded']
        ]
        dep_count_parts += [
            f"{dep_counts['error']} error" + ("s" if dep_counts['error'] != 1 else "")
            for _k in [0]
            if dep_counts['error']
        ]
        dep_count_parts += [
            f"{dep_counts['available']} available"
            for _k in [0]
            if dep_counts['available']
        ]
        dep_count_parts += [
            f"{dep_counts['missing']} missing"
            for _k in [0]
            if dep_counts['missing']
        ]
        dep_prefix = f"  requires: {len(reqs)}"
        if dep_count_parts:
            dep_prefix += " (" + ", ".join(dep_count_parts) + ")"
        ed.message(dep_prefix)
        for dep in reqs:
            ed.message(f"    - {_plugin_dependency_entry(ed, dep)}")
        if not errs:
            zero_suffix = _plugin_zero_error_state_suffix(ed, str(name))
            if not zero_suffix and _plugin_inventory_state(ed, str(name)) == "loaded":
                zero_suffix = "loaded plugin"
            ed.message(_plugin_error_count_line(0, zero_suffix))
            return True
        ed.message(_plugin_runtime_error_line(len(errs), str(errs[-1]) if errs else ""))
        if len(errs) > 1:
            for err in errs[-50:]:
                ed.message(f"    - {err}")
        return True
    ed.message(PLUGIN_USAGE)
    return False
