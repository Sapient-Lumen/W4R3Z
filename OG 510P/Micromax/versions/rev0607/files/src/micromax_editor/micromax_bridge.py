from __future__ import annotations

import shlex
import subprocess

from pathlib import Path

from micromax import VM
from micromax.vm import MicromaxError
from micromax.host_strings import install_string_hostcalls
from micromax.host_regex import install_regex_hostcalls

from .editor import Editor, MacroStep
from .buffer import Cursor
from .capabilities import capability_rows
from .fs_sandbox import resolve_path as fs_resolve_path, is_allowed as fs_path_allowed, deny_reason as fs_deny_reason


def install_editor_hostcalls(ed: Editor) -> None:
    """Register a minimal set of hostcalls for editor scripting."""

    vm: VM = ed.vm
    vm.editor_owner = ed

    # Advertise host features for scripts that want to probe capabilities.
    vm.host_features.add("micromax-editor")
    vm.host_features.add("host.capabilities")
    vm.host_features.add("ed.jumplist")
    vm.host_features.add("ed.jump-history-rows")
    vm.host_features.add("ed.jump-detail-row")
    vm.host_features.add("ed.jump-section-rows")
    vm.host_features.add("ed.jump-section-summary-rows")
    vm.host_features.add("ed.messages")
    vm.host_features.add("ed.macros")
    vm.host_features.add("ed.marks")
    vm.host_features.add("ed.mark-inventory-rows")
    vm.host_features.add("ed.mark-detail-row")
    vm.host_features.add("ed.mark-section-rows")
    vm.host_features.add("ed.mark-section-summary-rows")
    vm.host_features.add("ed.buffers")
    vm.host_features.add("ed.buffer-inventory-rows")
    vm.host_features.add("ed.buffer-detail-row")
    vm.host_features.add("ed.buffer-section-rows")
    vm.host_features.add("ed.buffer-section-summary-rows")
    vm.host_features.add("ed.prompt-suggestions")
    vm.host_features.add("ed.prompt-suggestion-rows")
    vm.host_features.add("ed.prompt-current-row")
    vm.host_features.add("ed.prompt-current-section")
    vm.host_features.add("ed.prompt-current-preview")
    vm.host_features.add("ed.prompt-current-position")
    vm.host_features.add("ed.prompt-window")
    vm.host_features.add("ed.prompt-display")
    vm.host_features.add("ed.prompt-panel")
    vm.host_features.add("ed.prompt-mx-completion")
    vm.host_features.add("ed.micromax-commands")
    vm.host_features.add("ed.bindings")
    vm.host_features.add("ed.binding-detail-row")
    vm.host_features.add("ed.command-rows")
    vm.host_features.add("ed.command-detail-row")
    vm.host_features.add("ed.action-detail-row")
    vm.host_features.add("ed.word-detail-row")
    vm.host_features.add("ed.doc-detail-row")
    vm.host_features.add("ed.topic-detail-row")
    vm.host_features.add("ed.help-current-heading-detail-row")
    vm.host_features.add("ed.help-heading-detail-row")
    vm.host_features.add("ed.hook-detail-row")
    vm.host_features.add("ed.hook-inventory-rows")
    vm.host_features.add("ed.hook-summary-rows")
    vm.host_features.add("ed.command-palette")
    vm.host_features.add("ed.command-palette-rows")
    vm.host_features.add("ed.command-palette-section-rows")
    vm.host_features.add("ed.command-palette-section-summary-rows")
    vm.host_features.add("ed.topic-rows")
    vm.host_features.add("ed.topic-section-rows")
    vm.host_features.add("ed.topic-section-summary-rows")
    vm.host_features.add("ed.apropos-section-rows")
    vm.host_features.add("ed.apropos-section-summary-rows")
    vm.host_features.add("ed.topic-prompt")
    vm.host_features.add("ed.binding-prompt")
    vm.host_features.add("ed.binding-prompt-rows")
    vm.host_features.add("ed.binding-section-rows")
    vm.host_features.add("ed.binding-section-summary-rows")
    vm.host_features.add("ed.registration-groups")
    vm.host_features.add("ed.keymodes")
    vm.host_features.add("ed.keymode-inventory-rows")
    vm.host_features.add("ed.keymode-detail-row")
    vm.host_features.add("ed.transient-keymodes")
    vm.host_features.add("ed.binding-discovery")
    vm.host_features.add("ed.available-binding-inventory-rows")
    vm.host_features.add("ed.option-inventory-rows")
    vm.host_features.add("ed.option-section-summary-rows")
    vm.host_features.add("ed.option-detail-row")
    vm.host_features.add("ed.prefix-maps")
    vm.host_features.add("ed.mode-prefix-maps")
    vm.host_features.add("ed.statusline")
    vm.host_features.add("ed.statusfmt")
    vm.host_features.add("ed.statusline-text")
    vm.host_features.add("ed.statusline-model")
    vm.host_features.add("ed.interaction-model")
    vm.host_features.add("ed.keymenu-model")
    vm.host_features.add("ed.infobar-model")
    vm.host_features.add("ed.screen-layout")
    vm.host_features.add("ed.gutter-model")
    vm.host_features.add("ed.edit-window")
    vm.host_features.add("ed.search-rows")
    vm.host_features.add("ed.showchars-rows")
    vm.host_features.add("ed.viewport-cues")
    vm.host_features.add("ed.docs-cues")
    vm.host_features.add("ed.display-rows")
    vm.host_features.add("ed.viewport-rows")
    vm.host_features.add("ed.screen-model")
    vm.host_features.add("ed.screen-rows")
    vm.host_features.add("ed.bottom-rows")
    vm.host_features.add("ed.with-buffer")
    vm.host_features.add("ed.with-viewport")
    vm.host_features.add("ed.recent")
    vm.host_features.add("ed.recent-clear")
    vm.host_features.add("ed.recent-clear-count")
    vm.host_features.add("ed.recent-inventory-rows")
    vm.host_features.add("ed.recent-detail-row")
    vm.host_features.add("ed.recent-slot-detail-row")
    vm.host_features.add("ed.recent-dir-detail-row")
    vm.host_features.add("ed.recent-slot-dir-detail-row")
    vm.host_features.add("ed.recent-section-rows")
    vm.host_features.add("ed.recent-section-summary-rows")
    vm.host_features.add("ed.recent-dir-section-rows")
    vm.host_features.add("ed.recent-dir-section-summary-rows")
    vm.host_features.add("ed.recent-prompt-rows")
    vm.host_features.add("ed.recent-dir-prompt-rows")
    vm.host_features.add("ed.doc-rows")
    vm.host_features.add("ed.doc-section-rows")
    vm.host_features.add("ed.doc-section-summary-rows")
    vm.host_features.add("ed.help-doc")
    vm.host_features.add("ed.help-follow")
    vm.host_features.add("ed.help-back")
    vm.host_features.add("ed.help-forward")
    vm.host_features.add("ed.help-resume")
    vm.host_features.add("ed.help-prune")
    vm.host_features.add("ed.help-link-rows")
    vm.host_features.add("ed.help-link-detail-row")
    vm.host_features.add("ed.helphistory-rows")
    vm.host_features.add("ed.helplink-section-rows")
    vm.host_features.add("ed.help-outline-rows")
    vm.host_features.add("ed.help-outline-section-rows")
    vm.host_features.add("ed.helpnav-section-rows")
    vm.host_features.add("ed.helpnav-section-summary-rows")
    vm.host_features.add("ed.filetype")
    vm.host_features.add("ed.viewport")
    vm.host_features.add("ed.lines")
    vm.host_features.add("ed.highlight")
    vm.host_features.add("ed.highlight-tags")
    vm.host_features.add("ed.after")
    vm.host_features.add("ed.cancel-timer")
    vm.host_features.add("ed.pump-timers")
    vm.host_features.add("ed.plugin-inventory-rows")
    vm.host_features.add("ed.plugin-detail-row")
    vm.host_features.add("ed.plugin-section-rows")
    vm.host_features.add("ed.plugin-section-summary-rows")
    vm.host_features.add("plugin.list")
    vm.host_features.add("plugin.reload")
    vm.host_features.add("plugin.errors")

    # General-purpose host helpers (non-editor-specific).
    # These are registered as hostcalls and then surfaced as convenience words
    # in the default wordlist so plugins can write ergonomic code.
    install_string_hostcalls(vm)
    try:
        vm.eval(
            """
            ( host-provided string helpers; implemented as hostcalls )
            : s+         ( a b -- s )      "s+" hostcall ;
            : s-len      ( s -- n )        "s-len" hostcall ;
            : s-slice    ( s a b -- s2 )   "s-slice" hostcall ;
            : s-index    ( hay needle -- i ) "s-index" hostcall ;
            : s-contains? ( hay needle -- flag ) "s-contains?" hostcall ;
            : s-split    ( s delim -- parts ) "s-split" hostcall ;
            : s-join     ( parts delim -- s ) "s-join" hostcall ;
            : s-replace  ( s old new -- s2 ) "s-replace" hostcall ;
            : s-trim     ( s -- s2 )       "s-trim" hostcall ;
            : s-upper    ( s -- s2 )       "s-upper" hostcall ;
            : s-lower    ( s -- s2 )       "s-lower" hostcall ;
            : s-format   ( ... fmt n -- s ) "s-format" hostcall ;
            : format     ( ... fmt n -- s ) "s-format" hostcall ;
            """,
            filename="<host-strings>",
        )
    except Exception:
        # Best-effort: avoid failing editor startup if a host disables strings.
        pass

    # Regex helpers (align with editor find/replace semantics).
    install_regex_hostcalls(vm)
    try:
        vm.eval(
            """
            ( host-provided regex helpers; implemented as hostcalls )
            : re-search  ( hay pat start flags -- m|0 )  "re.search" hostcall ;
            : re-findall ( hay pat start flags -- ms )   "re.findall" hostcall ;
            : re-sub     ( hay pat repl flags -- out )   "re.sub" hostcall ;
            : re-subn    ( hay pat repl flags -- out n ) "re.subn" hostcall ;
            : re-escape  ( s -- s2 )                     "re.escape" hostcall ;
            """,
            filename="<host-regex>",
        )
    except Exception:
        # Best-effort: don't fail startup if regex is disabled.
        pass

    # Small editor-specific convenience words implemented as hostcalls.
    try:
        vm.eval(
            """
            : statusfmt       ( template -- s )      "ed.statusfmt" hostcall ;
            : statusline-text ( width -- s )         "ed.statusline-text" hostcall ;
            : statusline-model ( width -- m )        "ed.statusline-model" hostcall ;
            : interaction-model ( width -- m )       "ed.interaction-model" hostcall ;
            : keymenu-model  ( width -- m )          "ed.keymenu-model" hostcall ;
            : infobar-model  ( width -- m )          "ed.infobar-model" hostcall ;
            : screen-layout  ( lines cols -- m )     "ed.screen-layout" hostcall ;
            : gutter-model   ( lines cols -- m )      "ed.gutter-model" hostcall ;
            : edit-window   ( lines cols -- m )      "ed.edit-window" hostcall ;
            : search-rows   ( lines cols -- m )      "ed.search-rows" hostcall ;
            : showchars-rows ( lines cols -- m )     "ed.showchars-rows" hostcall ;
            : viewport-cues ( lines cols -- m )      "ed.viewport-cues" hostcall ;
            : docs-cues    ( lines cols -- m )       "ed.docs-cues" hostcall ;
            : display-rows ( lines cols -- m )       "ed.display-rows" hostcall ;
            : viewport-rows ( lines cols -- m )      "ed.viewport-rows" hostcall ;
            : screen-model  ( lines cols -- m )      "ed.screen-model" hostcall ;
            : screen-rows   ( lines cols -- m )      "ed.screen-rows" hostcall ;
            : bottom-rows    ( width -- rows )       "ed.bottom-rows" hostcall ;
            : with-buffer     ( name q -- ok )       "ed.with-buffer" hostcall ;
            : with-viewport   ( q -- ok )            "ed.with-viewport" hostcall ;
            : recent-files    ( -- xs )              "ed.recent" hostcall ;
            : recent-clear    ( -- )                 "ed.recent-clear" hostcall ;
            : recent-clear-count ( -- n )            "ed.recent-clear-count" hostcall ;
            : recent-prompt-rows ( q -- rows )      "ed.recent-prompt-rows" hostcall ;
            : recent-dir-prompt-rows ( q -- rows )  "ed.recent-dir-prompt-rows" hostcall ;
            : jump-detail     ( n|"#n" -- row|0 )  "ed.jump-detail-row" hostcall ;
            : jump-section-summaries ( q -- rows )  "ed.jump-section-summary-rows" hostcall ;
            : mark-detail     ( name -- row|0 )     "ed.mark-detail-row" hostcall ;
            : mark-section-summaries ( q -- rows ) "ed.mark-section-summary-rows" hostcall ;
            : recent-detail   ( path -- row|0 )     "ed.recent-detail-row" hostcall ;
            : recent-slot-detail ( n -- row|0 )     "ed.recent-slot-detail-row" hostcall ;
            : recent-dir-detail ( dir -- row|0 )    "ed.recent-dir-detail-row" hostcall ;
            : recent-slot-dir-detail ( n -- row|0 ) "ed.recent-slot-dir-detail-row" hostcall ;
            : recent-sections ( q -- sections )     "ed.recent-section-rows" hostcall ;
            : recent-section-summaries ( q -- rows ) "ed.recent-section-summary-rows" hostcall ;
            : recent-dir-sections ( q -- sections ) "ed.recent-dir-section-rows" hostcall ;
            : recent-dir-section-summaries ( q -- rows ) "ed.recent-dir-section-summary-rows" hostcall ;
            : buffer-detail ( name -- row|0 )       "ed.buffer-detail-row" hostcall ;
            : buffer-sections ( q -- sections )     "ed.buffer-section-rows" hostcall ;
            : buffer-section-summaries ( q -- rows ) "ed.buffer-section-summary-rows" hostcall ;
            : plugin-detail ( name -- row|0 )      "ed.plugin-detail-row" hostcall ;
            : plugin-sections ( q -- sections )     "ed.plugin-section-rows" hostcall ;
            : binding-sections ( q -- sections )    "ed.binding-section-rows" hostcall ;
            : binding-section-summaries ( q -- rows ) "ed.binding-section-summary-rows" hostcall ;
            : palette-section-summaries ( q -- rows ) "ed.command-palette-section-summary-rows" hostcall ;
            : doc-sections    ( q -- sections )     "ed.doc-section-rows" hostcall ;
            : prompt-current-position ( -- m )      "ed.prompt-current-position" hostcall ;
            : prompt-window   ( lines -- m )         "ed.prompt-window" hostcall ;
            : prompt-display  ( lines cols -- rows )  "ed.prompt-display" hostcall ;
            : prompt-panel   ( lines cols -- m )     "ed.prompt-panel" hostcall ;
            : capabilities    ( -- rows )           "host.capabilities" hostcall ;
            : open-url        ( url -- ok )         "ed.open-url" hostcall ;
            : shell           ( cmd -- code out err ) "ed.shell" hostcall ;
            : fs-read         ( path -- ok text err ) "ed.fs-read" hostcall ;
            : fs-list         ( path -- ok rows err ) "ed.fs-list" hostcall ;
            : fs-stat         ( path -- ok info err ) "ed.fs-stat" hostcall ;

            ( docs browser helpers )
            : help-forward      ( -- ok )           "ed.help-forward" hostcall ;
            : help-resume       ( -- ok )           "ed.help-resume" hostcall ;
            : help-prune        ( -- ok )           "ed.help-prune" hostcall ;
            : helphistory-rows  ( -- rows )         "ed.helphistory-rows" hostcall ;
            : helplink-sections  ( q -- sections )   "ed.helplink-section-rows" hostcall ;
            : helplink-detail    ( -- row|0 )        "ed.help-link-detail-row" hostcall ;
            : help-current-heading-detail ( -- row|0 ) "ed.help-current-heading-detail-row" hostcall ;
            : helpoutline-rows   ( q -- rows )       "ed.help-outline-rows" hostcall ;
            : helpoutline-sections ( q -- sections ) "ed.help-outline-section-rows" hostcall ;
            : helpnav-sections   ( q -- sections )   "ed.helpnav-section-rows" hostcall ;
            : helpnav-summaries  ( q -- rows )       "ed.helpnav-section-summary-rows" hostcall ;
            : keymode-detail  ( name -- row|0 )      "ed.keymode-detail-row" hostcall ;
            : hook-state      ( name -- row|0 )      "ed.hook-detail-row" hostcall ;
            """,
            filename="<host-editor>",
        )
    except Exception:
        pass

    def hc_ed_msg(vm: VM) -> None:
        s = vm.pop_str()
        ed.message(s)

    def hc_ed_messages(vm: VM) -> None:
        """( -- msgs ) Return current message list as ["...", ...]."""
        vm.stack.append([str(x) for x in ed.messages])

    def hc_ed_last_message(vm: VM) -> None:
        """( -- s ) Return last message (or "")."""
        vm.stack.append(str(ed.messages[-1]) if ed.messages else "")

    def hc_ed_pop_message(vm: VM) -> None:
        """( -- s ) Pop oldest message (or "")."""
        if ed.messages:
            vm.stack.append(str(ed.messages.pop(0)))
        else:
            vm.stack.append("")

    def hc_ed_clear_messages(vm: VM) -> None:
        """( -- ) Clear messages."""
        ed.messages.clear()

    # ----- capability registry + optional unsafe surfaces -----
    def hc_host_capabilities(vm: VM) -> None:
        """( -- rows ) Return capability registry rows.

        Rows are: [feature option kind enabled doc]
        """

        vm.stack.append(capability_rows(ed))

    def hc_ed_prompt_panel(vm: VM) -> None:
        """( lines cols -- m ) Return the shared visible picker-panel model."""

        cols = vm.pop_int()
        lines = vm.pop_int()
        vm.stack.append(ed.prompt_panel_model(lines=lines, cols=cols))

    def hc_ed_screen_layout(vm: VM) -> None:
        """( lines cols -- m ) Return the tiny shared curses screen-layout model."""

        cols = vm.pop_int()
        lines = vm.pop_int()
        vm.stack.append(ed.screen_layout_model(lines=lines, cols=cols))

    def hc_ed_gutter_model(vm: VM) -> None:
        """( lines cols -- m ) Return the shared visible gutter model."""

        cols = vm.pop_int()
        lines = vm.pop_int()
        vm.stack.append(ed.gutter_model(lines=lines, cols=cols))

    def hc_ed_edit_window(vm: VM) -> None:
        """( lines cols -- m ) Return the shared reference visible edit-window model."""

        cols = vm.pop_int()
        lines = vm.pop_int()
        vm.stack.append(ed.edit_window_model(lines=lines, cols=cols))

    def hc_ed_search_rows(vm: VM) -> None:
        """( lines cols -- m ) Return the shared visible search-row model."""

        cols = vm.pop_int()
        lines = vm.pop_int()
        vm.stack.append(ed.search_rows_model(lines=lines, cols=cols))

    def hc_ed_showchars_rows(vm: VM) -> None:
        """( lines cols -- m ) Return the shared visible showchars-row model."""

        cols = vm.pop_int()
        lines = vm.pop_int()
        vm.stack.append(ed.showchars_rows_model(lines=lines, cols=cols))

    def hc_ed_display_rows(vm: VM) -> None:
        """( lines cols -- m ) Return the shared display-text screen rows."""

        cols = vm.pop_int()
        lines = vm.pop_int()
        vm.stack.append(ed.display_rows_model(lines=lines, cols=cols))

    def hc_ed_docs_cues(vm: VM) -> None:
        """( lines cols -- m ) Return the shared visible docs/help-cue model."""

        cols = vm.pop_int()
        lines = vm.pop_int()
        vm.stack.append(ed.docs_cues_model(lines=lines, cols=cols))

    def hc_ed_viewport_cues(vm: VM) -> None:
        """( lines cols -- m ) Return the shared visible viewport-cue model."""

        cols = vm.pop_int()
        lines = vm.pop_int()
        vm.stack.append(ed.viewport_cues_model(lines=lines, cols=cols))

    def hc_ed_viewport_rows(vm: VM) -> None:
        """( lines cols -- m ) Return the shared visible viewport-row model."""

        cols = vm.pop_int()
        lines = vm.pop_int()
        vm.stack.append(ed.viewport_rows_model(lines=lines, cols=cols))

    def hc_ed_screen_model(vm: VM) -> None:
        """( lines cols -- m ) Return the shared visible-screen model."""

        cols = vm.pop_int()
        lines = vm.pop_int()
        vm.stack.append(ed.screen_model(lines=lines, cols=cols))

    def hc_ed_screen_rows(vm: VM) -> None:
        """( lines cols -- m ) Return the shared plain-text screen rows."""

        cols = vm.pop_int()
        lines = vm.pop_int()
        vm.stack.append(ed.screen_rows_model(lines=lines, cols=cols))

    def hc_ed_open_url(vm: VM) -> None:
        """( url -- ok ) Open an external URL (capability-gated)."""

        url = vm.pop_str()
        if not bool(ed.options.get("cap.open-url")):
            raise MicromaxError("ed.open-url disabled (set cap.open-url true)")
        ok = ed.open_url(url)
        vm.stack.append(1 if ok else 0)

    def hc_ed_shell(vm: VM) -> None:
        """( cmd -- code out err ) Run a shell command (capability-gated).

        This is intentionally simple and best-effort. Hosts that want a real
        job system should provide an alternative surface.
        """

        cmd = vm.pop_str()
        if not bool(ed.options.get("cap.shell")):
            raise MicromaxError("ed.shell disabled (set cap.shell true)")
        try:
            p = subprocess.run(
                str(cmd),
                shell=True,
                capture_output=True,
                text=True,
                timeout=5,
            )
            vm.stack.append(int(p.returncode))
            vm.stack.append(str(p.stdout or ""))
            vm.stack.append(str(p.stderr or ""))
        except Exception as e:
            # surface as a non-fatal error tuple
            vm.stack.append(127)
            vm.stack.append("")
            vm.stack.append(str(e))


    def hc_ed_fs_read(vm: VM) -> None:
        """( path -- ok text err ) Read a file from disk as UTF-8 (capability-gated)."""

        path = vm.pop_str()
        if not bool(ed.options.get("cap.fs-read")):
            raise MicromaxError("ed.fs-read disabled (set cap.fs-read true)")
        try:
            p = fs_resolve_path(ed, str(path))
            if not fs_path_allowed(ed, p):
                vm.stack.append(0)
                vm.stack.append("")
                vm.stack.append(fs_deny_reason(ed, p))
                return
            if not p.exists() or not p.is_file():
                vm.stack.append(0)
                vm.stack.append("")
                vm.stack.append(f"not a file: {p}")
                return

            max_bytes = 1_000_000
            try:
                if int(p.stat().st_size) > int(max_bytes):
                    vm.stack.append(0)
                    vm.stack.append("")
                    vm.stack.append(f"file too large (> {max_bytes} bytes): {p}")
                    return
            except Exception:
                pass

            text = p.read_text(encoding="utf-8", errors="replace")
            vm.stack.append(1)
            vm.stack.append(str(text))
            vm.stack.append("")
        except Exception as e:
            vm.stack.append(0)
            vm.stack.append("")
            vm.stack.append(str(e))


    def hc_ed_fs_list(vm: VM) -> None:
        """( path -- ok rows err ) List directory entries (capability-gated).

        Rows are: [[name kind path] ...] where kind is "dir"|"file"|"other".
        """

        path = vm.pop_str()
        if not bool(ed.options.get("cap.fs-list")):
            raise MicromaxError("ed.fs-list disabled (set cap.fs-list true)")
        try:
            p = fs_resolve_path(ed, str(path))
            if not fs_path_allowed(ed, p):
                vm.stack.append(0)
                vm.stack.append([])
                vm.stack.append(fs_deny_reason(ed, p))
                return
            if not p.exists() or not p.is_dir():
                vm.stack.append(0)
                vm.stack.append([])
                vm.stack.append(f"not a directory: {p}")
                return

            limit = 500
            entries = []
            try:
                items = list(p.iterdir())
            except Exception as e:
                vm.stack.append(0)
                vm.stack.append([])
                vm.stack.append(str(e))
                return

            def _rank(child: Path) -> tuple[int, str]:
                try:
                    if child.is_dir():
                        return (0, child.name.casefold())
                except Exception:
                    pass
                return (1, child.name.casefold())

            items.sort(key=_rank)
            for child in items[:limit]:
                name = child.name
                kind = "other"
                try:
                    if child.is_dir():
                        kind = "dir"
                        name = name + "/"
                    elif child.is_file():
                        kind = "file"
                except Exception:
                    kind = "other"
                entries.append([str(name), str(kind), str(child)])

            vm.stack.append(1)
            vm.stack.append(entries)
            vm.stack.append("")
        except Exception as e:
            vm.stack.append(0)
            vm.stack.append([])
            vm.stack.append(str(e))


    def hc_ed_fs_stat(vm: VM) -> None:
        """( path -- ok info err ) Stat a path (capability-gated).

        Info is a small portable map:
          {"path": str, "exists": 0|1, "kind": "file"|"dir"|"other", "size": int, "mtime": int}
        """

        path = vm.pop_str()
        if not bool(ed.options.get("cap.fs-stat")):
            raise MicromaxError("ed.fs-stat disabled (set cap.fs-stat true)")
        try:
            p = fs_resolve_path(ed, str(path))
            if not fs_path_allowed(ed, p):
                vm.stack.append(0)
                vm.stack.append({"path": str(p), "exists": 0})
                vm.stack.append(fs_deny_reason(ed, p))
                return

            if not p.exists():
                vm.stack.append(0)
                vm.stack.append({"path": str(p), "exists": 0})
                vm.stack.append(f"not found: {p}")
                return

            kind = "other"
            size = 0
            mtime = 0
            try:
                if p.is_dir():
                    kind = "dir"
                elif p.is_file():
                    kind = "file"
            except Exception:
                kind = "other"

            try:
                st = p.stat()
                size = int(getattr(st, "st_size", 0) or 0)
                mtime = int(getattr(st, "st_mtime", 0) or 0)
            except Exception:
                size = 0
                mtime = 0

            info = {
                "path": str(p),
                "exists": 1,
                "kind": str(kind),
                "size": int(size),
                "mtime": int(mtime),
            }
            vm.stack.append(1)
            vm.stack.append(info)
            vm.stack.append("")
        except Exception as e:
            vm.stack.append(0)
            vm.stack.append({})
            vm.stack.append(str(e))

    def hc_ed_buffers(vm: VM) -> None:
        """( -- names ) Return open buffer names."""
        vm.stack.append(ed.buffer_names())

    def hc_ed_buffer_inventory_rows(vm: VM) -> None:
        """( -- rows ) Tiny inspectable buffer inventory rows as [name position active dirty readonly]."""
        vm.stack.append(ed.buffer_inventory_rows())

    def hc_ed_buffer_detail_row(vm: VM) -> None:
        """( name -- row|0 ) Tiny inspectable exact buffer-detail row as [name position active dirty readonly section path line_count]."""
        name = vm.pop_str()
        row = ed.buffer_detail_row(name)
        vm.stack.append(0 if row is None else row)

    def hc_ed_buffer_section_rows(vm: VM) -> None:
        """( query -- sections ) Grouped buffer rows by visible picker section."""
        query = vm.pop_str()
        vm.stack.append(ed.buffer_section_rows(query))

    def hc_ed_buffer_section_summary_rows(vm: VM) -> None:
        """( query -- rows ) Tiny count-aware broad buffer-section rows."""
        query = vm.pop_str()
        vm.stack.append(ed.buffer_section_summary_rows(query))

    def hc_ed_active_buffer(vm: VM) -> None:
        """( -- "name" ) Return active buffer name (or "")."""
        vm.stack.append(str(ed.active or ""))

    def hc_ed_set_active_buffer(vm: VM) -> None:
        """( "name" -- ok ) Switch active buffer if it exists."""
        name = vm.pop_str()
        ok = ed.switch_buffer(name)
        vm.stack.append(1 if ok else 0)

    def hc_ed_mark_set(vm: VM) -> None:
        """( "name" -- ok ) Set a named mark at the primary cursor."""
        name = vm.pop_str()
        ok = ed.mark_set(name)
        vm.stack.append(1 if ok else 0)

    def hc_ed_mark_jump(vm: VM) -> None:
        """( "name" -- ok ) Jump to a named mark."""
        name = vm.pop_str()
        ok = ed.mark_jump(name)
        vm.stack.append(1 if ok else 0)

    def hc_ed_marks(vm: VM) -> None:
        """( -- rows ) Return mark rows as [[name buffer line col] ...]."""
        vm.stack.append(ed.mark_rows())

    def hc_ed_mark_inventory_rows(vm: VM) -> None:
        """( -- rows ) Tiny inspectable mark inventory rows as [name buffer position preview active here]."""
        vm.stack.append(ed.mark_inventory_rows())

    def hc_ed_mark_detail_row(vm: VM) -> None:
        """( name -- row|0 ) Tiny inspectable exact mark row as [name buffer position preview active here]."""
        name = vm.pop_str()
        row = ed.mark_detail_row(name)
        vm.stack.append(0 if row is None else row)

    def hc_ed_mark_section_rows(vm: VM) -> None:
        """( query -- sections ) Grouped mark rows by owning buffer."""
        query = vm.pop_str()
        vm.stack.append(ed.mark_section_rows(query))

    def hc_ed_mark_section_summary_rows(vm: VM) -> None:
        """( query -- rows ) Tiny count-aware broad mark-section rows."""
        query = vm.pop_str()
        vm.stack.append(ed.mark_section_summary_rows(query))

    def hc_ed_status(vm: VM) -> None:
        """( -- m ) Return the portable statusline/infobar model as a map."""
        vm.stack.append(ed.status_model())

    def hc_ed_status_summary(vm: VM) -> None:
        """( -- s ) Return a compact summary string for headless/debug use."""
        vm.stack.append(ed.status_summary())

    def hc_ed_statusfmt(vm: VM) -> None:
        """( template -- s ) Render a statusformat template against current status_model()."""
        from .statusformat import render_status_template

        template = vm.pop_str()
        st = ed.status_model()
        vm.stack.append(render_status_template(template, ed=ed, status=st))

    def hc_ed_statusline_text(vm: VM) -> None:
        """( width -- s ) Render the full statusline string for a given width."""
        width = vm.pop_int()
        vm.stack.append(ed.statusline_text(int(width)))

    def hc_ed_statusline_model(vm: VM) -> None:
        """( width -- m ) Return the shared statusline layout model for one width."""
        width = vm.pop_int()
        vm.stack.append(ed.statusline_model(int(width)))

    def hc_ed_interaction_model(vm: VM) -> None:
        """( width -- m ) Return the shared prompt/capture row model for one width."""
        width = vm.pop_int()
        vm.stack.append(ed.interaction_model(int(width)))

    def hc_ed_keymenu_model(vm: VM) -> None:
        """( width -- m ) Return the shared keymenu row model for one width."""
        width = vm.pop_int()
        vm.stack.append(ed.keymenu_model(int(width)))

    def hc_ed_infobar_model(vm: VM) -> None:
        """( width -- m ) Return the shared idle infobar row model for one width."""
        width = vm.pop_int()
        vm.stack.append(ed.infobar_model(int(width)))

    def hc_ed_bottom_rows(vm: VM) -> None:
        """( width -- rows ) Return the visible bottom-row chrome as row maps."""
        width = vm.pop_int()
        vm.stack.append(ed.bottom_rows_model(int(width)))

    def hc_ed_with_buffer(vm: VM) -> None:
        """( name q -- ok ) Switch to buffer name for duration of quotation, then restore."""
        q = vm.pop_quote()
        name = vm.pop_str()
        old = str(ed.active or "")
        if name and not ed.switch_buffer(str(name)):
            vm.stack.append(0)
            return
        try:
            vm.exec_xt(q)
        finally:
            if old:
                try:
                    ed.switch_buffer(old)
                except Exception:
                    pass
        vm.stack.append(1)

    def hc_ed_with_viewport(vm: VM) -> None:
        """( q -- ok ) Run quotation and then restore the viewport model.

        This is a small resource helper for scripted flows that want to
        temporarily scroll or resize the viewport without leaving state behind.
        """
        q = vm.pop_quote()
        saved = dict(ed.viewport_model())
        try:
            vm.exec_xt(q)
        finally:
            try:
                ed.set_viewport(
                    top_line=int(saved.get('top_line', 0)),
                    top_subline=int(saved.get('top_subline', 0)),
                    left_col=int(saved.get('left_col', 0)),
                    height=int(saved.get('height', 0)),
                    width=int(saved.get('width', 0)),
                    follow_cursor=False,
                )
            except Exception:
                pass
        vm.stack.append(1)

    def hc_ed_plugin_inventory_rows(vm: VM) -> None:
        """( -- rows ) Tiny inspectable plugin inventory rows."""
        vm.stack.append(ed.plugin_inventory_rows())

    def hc_ed_plugin_detail_row(vm: VM) -> None:
        """( name -- row|0 ) Tiny inspectable exact plugin row as [query name state version deps error_count detail]."""
        row = ed.plugin_detail_row(vm.pop_str())
        vm.stack.append(row if row is not None else 0)

    def hc_ed_plugin_section_rows(vm: VM) -> None:
        """( query -- sections ) Grouped plugin rows by visible picker section."""
        query = vm.pop_str()
        vm.stack.append(ed.plugin_section_rows(query))

    def hc_ed_plugin_section_summary_rows(vm: VM) -> None:
        """( query -- rows ) Tiny count-aware plugin-section rows."""
        query = vm.pop_str()
        vm.stack.append(ed.plugin_section_summary_rows(query))

    def hc_ed_recent(vm: VM) -> None:
        """( -- xs ) Return recent file paths as a list of strings (MRU order)."""
        xs = getattr(ed, 'recent_files', [])
        vm.stack.append([str(x) for x in list(xs)])

    def _safe_clear_recent_files() -> int:
        try:
            return int(ed.clear_recent_files())
        except Exception:
            xs = getattr(ed, "recent_files", None)
            if xs is None:
                return 0
            try:
                forgotten = len(list(xs))
            except Exception:
                forgotten = 0
            try:
                xs.clear()
            except Exception:
                pass
            return forgotten

    def hc_ed_recent_clear(vm: VM) -> None:
        """( -- ) Clear the recent file MRU list."""
        _safe_clear_recent_files()

    def hc_ed_recent_clear_count(vm: VM) -> None:
        """( -- n ) Clear the recent file MRU list and return forgotten count."""
        vm.stack.append(_safe_clear_recent_files())

    def hc_ed_recent_inventory_rows(vm: VM) -> None:
        """( -- rows ) Tiny inspectable recent-file inventory rows as [index path position active open dirty readonly disk_truth action_truth]."""
        vm.stack.append(ed.recent_inventory_rows())

    def hc_ed_recent_detail_row(vm: VM) -> None:
        """( path -- row|0 ) Tiny inspectable exact recent-file row as [query path index position active open dirty readonly section detail disk_truth action_truth]."""
        row = ed.recent_detail_row(vm.pop_str())
        vm.stack.append(row if row is not None else 0)

    def hc_ed_recent_slot_detail_row(vm: VM) -> None:
        """( n|"#n" -- row|0 ) Tiny inspectable exact recent-file row addressed by visible 1-based MRU slot."""
        try:
            row = ed.recent_detail_row_by_index(vm.pop())
        except Exception:
            row = None
        vm.stack.append(row if row is not None else 0)

    def hc_ed_recent_dir_detail_row(vm: VM) -> None:
        """( dir -- row|0 ) Tiny inspectable exact recent-directory row as [query directory count active_count open_count dirty_count readonly_count sample_path sample_detail]."""
        row = ed.recent_dir_detail_row(vm.pop_str())
        vm.stack.append(row if row is not None else 0)

    def hc_ed_recent_slot_dir_detail_row(vm: VM) -> None:
        """( n|"#n" -- row|0 ) Tiny inspectable exact recent-directory row addressed by visible 1-based MRU slot."""
        try:
            row = ed.recent_dir_detail_row_by_index(vm.pop())
        except Exception:
            row = None
        vm.stack.append(row if row is not None else 0)

    def hc_ed_recent_section_rows(vm: VM) -> None:
        """( query -- sections ) Grouped recent-file rows by project root."""
        query = vm.pop_str()
        try:
            vm.stack.append(ed.recent_section_rows_by_project(query))
        except Exception:
            vm.stack.append([])

    def hc_ed_recent_section_summary_rows(vm: VM) -> None:
        """( query -- rows ) Tiny count-aware recent-file section rows by project root."""
        query = vm.pop_str()
        try:
            vm.stack.append(ed.recent_section_summary_rows(query))
        except Exception:
            vm.stack.append([])

    def hc_ed_recent_dir_section_rows(vm: VM) -> None:
        """( query -- sections ) Grouped recent-file rows by directory."""
        query = vm.pop_str()
        try:
            vm.stack.append(ed.recent_section_rows_by_dir(query))
        except Exception:
            vm.stack.append([])

    def hc_ed_recent_dir_section_summary_rows(vm: VM) -> None:
        """( query -- rows ) Tiny count-aware recent-file section rows by directory."""
        query = vm.pop_str()
        try:
            vm.stack.append(ed.recent_dir_section_summary_rows(query))
        except Exception:
            vm.stack.append([])

    def hc_ed_recent_prompt_rows(vm: VM) -> None:
        """( query -- rows ) Return visible recentpick rows as [[path kind menu info] ...]."""
        query = vm.pop_str()
        try:
            vm.stack.append(ed._recent_prompt_rows(query))
        except Exception:
            vm.stack.append([])

    def hc_ed_recent_dir_prompt_rows(vm: VM) -> None:
        """( query -- rows ) Return visible recentdirpick rows as [[path kind menu info] ...]."""
        query = vm.pop_str()
        try:
            vm.stack.append(ed._recent_dir_prompt_rows(query))
        except Exception:
            vm.stack.append([])

    def hc_ed_doc_rows(vm: VM) -> None:
        """( -- rows ) Docs picker rows as [[topic kind menu info] ...]."""
        try:
            vm.stack.append(ed.doc_prompt_rows())
        except Exception:
            vm.stack.append([])

    def hc_ed_doc_section_rows(vm: VM) -> None:
        """( query -- sections ) Grouped docs picker rows."""
        query = vm.pop_str()
        try:
            vm.stack.append(ed.doc_section_rows(query))
        except Exception:
            vm.stack.append([])

    def hc_ed_doc_section_summary_rows(vm: VM) -> None:
        """( query -- rows ) Tiny count-aware docs-section summaries."""
        query = vm.pop_str()
        try:
            vm.stack.append(ed.doc_section_summary_rows(query))
        except Exception:
            vm.stack.append([])

    def hc_ed_help_doc(vm: VM) -> None:
        """( topic -- ok ) Open a docs page into a protected help buffer."""
        topic = vm.pop_str()
        try:
            vm.stack.append(1 if ed.open_help_doc(topic) else 0)
        except Exception:
            vm.stack.append(0)

    def hc_ed_help_follow(vm: VM) -> None:
        """( -- ok ) Follow a markdown link under cursor in help buffer."""
        try:
            vm.stack.append(1 if ed.help_follow() else 0)
        except Exception:
            vm.stack.append(0)

    def hc_ed_help_back(vm: VM) -> None:
        """( -- ok ) Go back to previous docs page in help buffer."""
        try:
            vm.stack.append(1 if ed.help_back() else 0)
        except Exception:
            vm.stack.append(0)

    def hc_ed_help_forward(vm: VM) -> None:
        """( -- ok ) Go forward to next docs page after ``helpback``."""
        try:
            vm.stack.append(1 if ed.help_forward() else 0)
        except Exception:
            vm.stack.append(0)

    def hc_ed_help_resume(vm: VM) -> None:
        """( -- ok ) Reopen the last session-local docs target."""
        try:
            vm.stack.append(1 if ed.help_resume() else 0)
        except Exception:
            vm.stack.append(0)

    def hc_ed_help_prune(vm: VM) -> None:
        """( -- ok ) Prune missing docs targets from local help history."""
        try:
            vm.stack.append(1 if ed.help_prune() else 0)
        except Exception:
            vm.stack.append(0)

    def hc_ed_help_link_rows(vm: VM) -> None:
        """( query -- rows ) Markdown links in the current docs buffer as rows."""
        query = vm.pop_str()
        try:
            vm.stack.append(ed.help_link_rows(query))
        except Exception:
            vm.stack.append([])

    def hc_ed_help_link_detail_row(vm: VM) -> None:
        """( -- row|0 ) Tiny inspectable current docs-link row as [topic label target kind line col section]."""
        row = ed.help_link_detail_row()
        vm.stack.append(0 if row is None else row)

    def hc_ed_helphistory_rows(vm: VM) -> None:
        """( -- rows ) Tiny docs-history rows as [[lane depth topic title position state] ...]."""
        try:
            vm.stack.append(ed.help_history_rows())
        except Exception:
            vm.stack.append([])

    def hc_ed_helplink_section_rows(vm: VM) -> None:
        """( query -- sections ) Grouped markdown links for the current docs buffer."""
        query = vm.pop_str()
        try:
            vm.stack.append(ed.help_link_section_rows(query))
        except Exception:
            vm.stack.append([])

    def hc_ed_help_outline_rows(vm: VM) -> None:
        """( query -- rows ) Markdown headings in the current docs buffer as rows."""
        query = vm.pop_str()
        try:
            vm.stack.append(ed.help_outline_rows(query))
        except Exception:
            vm.stack.append([])

    def hc_ed_help_outline_section_rows(vm: VM) -> None:
        """( query -- sections ) Grouped outline rows for the current docs buffer."""
        query = vm.pop_str()
        try:
            vm.stack.append(ed.help_outline_section_rows(query))
        except Exception:
            vm.stack.append([])

    def hc_ed_helpnav_section_rows(vm: VM) -> None:
        """( query -- sections ) Grouped headings + links for the current docs buffer."""
        query = vm.pop_str()
        try:
            vm.stack.append(ed.help_nav_section_rows(query))
        except Exception:
            vm.stack.append([])


    def hc_ed_helpnav_section_summary_rows(vm: VM) -> None:
        """( query -- rows ) Tiny current-doc help-nav summaries as [[label count sample_name sample_detail] ...]."""
        query = vm.pop_str()
        try:
            vm.stack.append(ed.help_nav_section_summary_rows(query))
        except Exception:
            vm.stack.append([])


    def hc_ed_filetype(vm: VM) -> None:
        """( -- s ) Return detected filetype for active buffer."""
        vm.stack.append(str(ed.filetype()))


    def hc_ed_with_messages(vm: VM) -> None:
        """( q -- ok ) Run quotation and then restore the message log.

        This is the messaging analogue of `ed.with-cursorstate` (save/restore):
        it lets commands emit temporary debug output without polluting the
        persistent message list.
        """

        q = vm.pop_quote()
        saved = list(ed.messages)
        try:
            vm.exec_xt(q)
        finally:
            ed.messages[:] = saved
        vm.stack.append(1)

    def hc_ed_capture_messages(vm: VM) -> None:
        """( q -- msgs ok ) Run quotation, returning messages it emitted.

        The editor's message log is cleared for the duration of the call.
        After running, the previous message log is restored.
        """

        q = vm.pop_quote()
        saved = list(ed.messages)
        ed.messages[:] = []
        try:
            vm.exec_xt(q)
            captured = [str(x) for x in ed.messages]
        finally:
            ed.messages[:] = saved
        vm.stack.append(captured)
        vm.stack.append(1)

    def hc_ed_bind(vm: VM) -> None:
        """( key action-spec -- ) Bind a global key with best-effort provenance."""
        action_spec = vm.pop_str()
        key = vm.pop_str()
        sp = getattr(vm, 'last_span', None)
        group = getattr(vm, 'current_editor_group', None)
        ed.keymap.bind(key, action_spec, span=sp, group=group)

    def hc_ed_bind_mode(vm: VM) -> None:
        """( mode key action-spec -- ) Bind a key in a named keymap mode."""
        action_spec = vm.pop_str()
        key = vm.pop_str()
        mode = vm.pop_str()
        sp = getattr(vm, 'last_span', None)
        group = getattr(vm, 'current_editor_group', None)
        ed.keymap.bind(key, action_spec, span=sp, group=group, mode=mode)

    def hc_ed_bind_doc(vm: VM) -> None:
        """( key doc -- ok ) Attach/replace a human description for a global binding."""
        doc = vm.pop_str()
        key = vm.pop_str()
        vm.stack.append(1 if ed.keymap.set_desc(key, doc) else 0)

    def hc_ed_bind_mode_doc(vm: VM) -> None:
        """( mode key doc -- ok ) Attach/replace a human description for a mode binding."""
        doc = vm.pop_str()
        key = vm.pop_str()
        mode = vm.pop_str()
        vm.stack.append(1 if ed.keymap.set_desc(key, doc, mode=mode) else 0)

    def hc_ed_bind_prefix(vm: VM) -> None:
        """( key mode doc|0 -- ok ) Bind a global prefix key that enters a one-shot mode.

        The resulting binding is just a normal keymap entry with action-spec
        `command:prefixmode MODE`, so it remains inspectable and portable. If
        doc is 0/empty, a small default description is used.
        """

        doc = vm.pop()
        mode = vm.pop_str()
        key = vm.pop_str()
        spec = f"command:prefixmode {shlex.quote(mode)}"
        sp = getattr(vm, 'last_span', None)
        group = getattr(vm, 'current_editor_group', None)
        ed.keymap.bind(key, spec, span=sp, group=group)
        desc = str(doc).strip() if doc not in (0, None) else ''
        ed.keymap.set_desc(key, desc or f"prefix {mode}")
        vm.stack.append(1)

    def hc_ed_bind_mode_prefix(vm: VM) -> None:
        """( owner-mode key mode doc|0 -- ok ) Bind a mode-local prefix key.

        This is the mode-local sibling of `ed.bind-prefix`: it still stores a
        normal binding whose action-spec is `command:prefixmode MODE`, but the
        binding itself lives in OWNER-MODE.
        """

        doc = vm.pop()
        mode = vm.pop_str()
        key = vm.pop_str()
        owner_mode = vm.pop_str()
        spec = f"command:prefixmode {shlex.quote(mode)}"
        sp = getattr(vm, 'last_span', None)
        group = getattr(vm, 'current_editor_group', None)
        ed.keymap.bind(key, spec, span=sp, group=group, mode=owner_mode)
        desc = str(doc).strip() if doc not in (0, None) else ''
        ed.keymap.set_desc(key, desc or f"prefix {mode}", mode=owner_mode)
        vm.stack.append(1)

    def hc_ed_prefix_mode(vm: VM) -> None:
        """( mode -- ok ) Enter a one-shot prefix mode and show reachable bindings."""
        mode = vm.pop_str()
        if not mode or mode in ('global', 'none'):
            vm.stack.append(0)
            return
        ed.push_key_mode(mode, once=True)
        ed.exec_command_line('whichkey')
        vm.stack.append(1)

    def hc_ed_unbind(vm: VM) -> None:
        """( key -- ok ) Remove a global key binding."""
        key = vm.pop_str()
        vm.stack.append(1 if ed.keymap.unbind(key) else 0)

    def hc_ed_unbind_mode(vm: VM) -> None:
        """( mode key -- ok ) Remove a key binding from a named mode."""
        key = vm.pop_str()
        mode = vm.pop_str()
        vm.stack.append(1 if ed.keymap.unbind(key, mode=mode) else 0)

    def hc_ed_bindings(vm: VM) -> None:
        """( -- rows ) Return [[key action-spec [file line col]|0] ...]."""
        vm.stack.append(ed.keymap.binding_rows())

    def hc_ed_binding_detail(vm: VM) -> None:
        """( -- rows ) Return [[key action group|0 [file line col]|0] ...]."""
        vm.stack.append(ed.keymap.binding_detail_rows())

    def hc_ed_binding_detail_row(vm: VM) -> None:
        """( key -- [mode key action desc|0 group|0 [file line col]|0] | 0 ) Return the tiny shared resolved-binding row behind ``showkey``."""
        vm.stack.append(ed.binding_detail_row(vm.pop_str()))

    def hc_ed_binding_modes(vm: VM) -> None:
        """( -- rows ) Return [[mode key action group|0 [file line col]|0] ...]."""
        vm.stack.append(ed.keymap.binding_mode_rows())

    def hc_ed_binding_rows_for(vm: VM) -> None:
        """( mode|0 -- rows ) Return [[key action group|0 [file line col]|0] ...] for a mode."""
        mode = vm.pop()
        vm.stack.append(ed.keymap.binding_detail_rows_for(None if mode == 0 else str(mode)))

    def hc_ed_binding_info_for(vm: VM) -> None:
        """( mode|0 -- rows ) Return [[key action desc|0 group|0 [file line col]|0] ...] for a mode."""
        mode = vm.pop()
        vm.stack.append(ed.binding_info_rows_for(None if mode == 0 else str(mode)))

    def hc_ed_available_bindings(vm: VM) -> None:
        """( -- rows ) Return precedence-resolved [[mode key action group|0 [file line col]|0] ...]."""
        vm.stack.append(ed.available_binding_rows())

    def hc_ed_available_binding_info(vm: VM) -> None:
        """( -- rows ) Return precedence-resolved [[mode key action desc|0 group|0 [file line col]|0] ...]."""
        vm.stack.append(ed.available_binding_info_rows())

    def hc_ed_available_binding_inventory_rows(vm: VM) -> None:
        """( -- rows ) Tiny inspectable current-binding inventory rows as [mode key action label once]."""
        vm.stack.append(ed.available_binding_inventory_rows())

    def hc_ed_resolve_key(vm: VM) -> None:
        """( key -- [mode key action group|0 [file line col]|0] | 0 ) Resolve a key through active keymodes."""
        vm.stack.append(ed.keymap.resolved_binding_row(vm.pop_str(), modes=ed.active_key_modes()))

    def hc_ed_resolve_key_info(vm: VM) -> None:
        """( key -- [mode key action desc|0 group|0 [file line col]|0] | 0 ) Resolve a key with description through active keymodes."""
        vm.stack.append(ed.resolve_key_info_row(vm.pop_str()))

    def hc_ed_keymode_store(vm: VM) -> None:
        """( mode|0 -- ) Set the active key mode (global fallback remains)."""
        mode = vm.pop()
        if mode == 0:
            ed.set_key_mode(None)
        else:
            ed.set_key_mode(str(mode))

    def hc_ed_keymode_fetch(vm: VM) -> None:
        """( -- mode|0 ) Return the current active key mode, or 0."""
        vm.stack.append(ed.current_key_mode() or 0)

    def hc_ed_keymode_push(vm: VM) -> None:
        """( mode -- ) Push an active key mode onto the stack."""
        ed.push_key_mode(vm.pop_str())

    def hc_ed_keymode_push_once(vm: VM) -> None:
        """( mode -- ) Push a one-shot active key mode onto the stack."""
        ed.push_key_mode(vm.pop_str(), once=True)

    def hc_ed_keymode_pop(vm: VM) -> None:
        """( -- mode|0 ) Pop and return the current active key mode."""
        vm.stack.append(ed.pop_key_mode() or 0)

    def hc_ed_keymodes(vm: VM) -> None:
        """( -- modes known ) Return active key modes and known binding modes."""
        vm.stack.append(ed.active_key_modes())
        vm.stack.append(ed.keymap.modes())

    def hc_ed_keymode_rows(vm: VM) -> None:
        """( -- rows known ) Return [[mode once?] ...] and known binding modes."""
        vm.stack.append(ed.active_key_mode_rows())
        vm.stack.append(ed.keymap.modes())

    def hc_ed_keymode_inventory_rows(vm: VM) -> None:
        """( -- rows ) Return the shared active/known keymode inventory rows."""
        vm.stack.append(ed.keymode_inventory_rows())

    def hc_ed_keymode_detail_row(vm: VM) -> None:
        """( name -- row|0 ) Return one shared exact keymode detail row."""
        row = ed.keymode_detail_row(vm.pop_str())
        vm.stack.append(row if row is not None else 0)

    def hc_ed_group_store(vm: VM) -> None:
        """( group|0 -- ) Set default editor registration group."""
        group = vm.pop()
        if group == 0:
            vm.current_editor_group = None
        else:
            vm.current_editor_group = str(group)

    def hc_ed_group_fetch(vm: VM) -> None:
        """( -- group|0 ) Current default editor registration group."""
        vm.stack.append(str(vm.current_editor_group) if vm.current_editor_group else 0)

    def hc_ed_run(vm: VM) -> None:
        action_spec = vm.pop_str()
        ok = ed.run_action_chain(action_spec)
        vm.stack.append(1 if ok else 0)

    def hc_ed_press_key(vm: VM) -> None:
        """( key -- ok ) Resolve and execute a bound key through active keymodes."""
        with ed.script_context():
            ok = ed.dispatch_key(vm.pop_str())
        vm.stack.append(1 if ok else 0)

    def hc_ed_command(vm: VM) -> None:
        cmdline = vm.pop_str()
        with ed.script_context():
            ok = ed.exec_command_line(cmdline)
        vm.stack.append(1 if ok else 0)

    def hc_ed_command_edit(vm: VM) -> None:
        s = vm.pop_str()
        ed.enter_prompt("command", prefill=s)

    def hc_ed_topic_prompt(vm: VM) -> None:
        s = vm.pop_str()
        ed.enter_topic_prompt(s)

    def hc_ed_binding_prompt(vm: VM) -> None:
        s = vm.pop_str()
        ed.enter_binding_prompt(s)


    # ----- micromax-defined command-bar commands -----
    def hc_ed_cmd_add(vm: VM) -> None:
        """( xt name doc -- ok ) Define or replace a command-bar command.

        The command's xt is executed with `( args -- ... )` where args is a list
        of strings (the command line arguments). If the xt leaves an int/bool on
        top of the stack, it is treated as an ok flag; otherwise ok defaults to 1.

        A best-effort source span is attached (via vm.last_span) so `help <cmd>`
        can show where the command was registered.
        """

        doc = vm.pop_str()
        name = vm.pop_str()
        xt = vm.pop_xt()
        sp = getattr(vm, 'last_span', None)
        group = getattr(vm, 'current_editor_group', None)

        def _run(ed2: Editor, args: list[str]) -> bool:
            depth = len(vm.stack)
            try:
                vm.stack.append([str(a) for a in args])
                vm.exec_xt(xt)
                ok = 1
                if len(vm.stack) > depth:
                    top = vm.stack[-1]
                    if isinstance(top, bool):
                        ok = 1 if top else 0
                    elif isinstance(top, int):
                        ok = int(top)
                return bool(ok)
            except Exception as e:
                if isinstance(e, MicromaxError):
                    detail = vm.format_error(e)
                else:
                    detail = str(e)
                ed2.message(f'command {name}: error: {detail}')
                return False
            finally:
                del vm.stack[depth:]

        ed.command_dispatcher.register(str(name), _run, doc=str(doc), span=sp, group=group)
        vm.stack.append(1)

    def hc_ed_cmd_rm(vm: VM) -> None:
        """( name -- ok ) Remove a command-bar command by name."""
        name = vm.pop_str()
        vm.stack.append(1 if ed.command_dispatcher.remove(str(name)) else 0)

    def hc_ed_cmds(vm: VM) -> None:
        """( -- names ) List command names (including micromax-defined)."""
        vm.stack.append(ed.command_dispatcher.names())

    def hc_ed_cmd_rows(vm: VM) -> None:
        """( -- rows ) Return [[name doc group|0 [file line col]|0] ...]."""
        vm.stack.append(ed.command_dispatcher.command_rows())

    def hc_ed_command_detail_row(vm: VM) -> None:
        """( name -- row|0 ) Tiny inspectable command-detail row as [name doc group|0 [file line col]|0]."""
        name = vm.pop_str()
        row = ed.command_detail_row(name)
        vm.stack.append(0 if row is None else row)

    def hc_ed_action_detail_row(vm: VM) -> None:
        """( name -- row|0 ) Tiny inspectable action-detail row as [name doc [file line col]|0]."""
        name = vm.pop_str()
        row = ed.action_detail_row(name)
        vm.stack.append(0 if row is None else row)

    def hc_ed_word_detail_row(vm: VM) -> None:
        """( name -- row|0 ) Tiny inspectable visible-word detail row as [name kind effect wordlist doc [file line col]|0 source|0]."""
        name = vm.pop_str()
        row = ed.word_detail_row(name)
        vm.stack.append(0 if row is None else row)

    def hc_ed_doc_detail_row(vm: VM) -> None:
        """( topic -- row|0 ) Tiny inspectable docs-detail row as [topic title summary section path]."""
        name = vm.pop_str()
        row = ed.doc_detail_row(name)
        vm.stack.append(0 if row is None else row)

    def hc_ed_topic_detail_row(vm: VM) -> None:
        """( name -- row|0 ) Tiny inspectable exact-topic row as [name kind detail_row]."""
        name = vm.pop_str()
        row = ed.topic_detail_row(name)
        vm.stack.append(0 if row is None else row)

    def hc_ed_help_current_heading_detail_row(vm: VM) -> None:
        """( -- row|0 ) Tiny inspectable current docs-heading row as [topic title fragment level line col section]."""
        row = ed.current_help_heading_detail_row()
        vm.stack.append(0 if row is None else row)

    def hc_ed_help_heading_detail_row(vm: VM) -> None:
        """( query -- row|0 ) Tiny inspectable help-heading row as [topic title fragment level line col section]."""
        query = vm.pop_str()
        row = ed.help_heading_detail_row(query)
        vm.stack.append(0 if row is None else row)

    def hc_ed_hook_detail_row(vm: VM) -> None:
        """( name -- row|0 ) Tiny inspectable exact hook row as [query name handler_count sample_handler|0 sample_detail|0 [file line col]|0]."""
        row = ed.hook_detail_row(vm.pop_str())
        vm.stack.append(0 if row is None else row)

    def hc_ed_hook_inventory_rows(vm: VM) -> None:
        """( name -- rows|0 ) Tiny inspectable hook-handler rows as [handler group|0 [file line col]|0]."""
        name = vm.pop_str()
        rows = ed.hook_inventory_rows(name)
        vm.stack.append(0 if rows is None else rows)

    def hc_ed_hook_summary_rows(vm: VM) -> None:
        """( query -- rows ) Tiny inspectable hook summary rows as [name handler_count sample_handler|0 [file line col]|0]."""
        query = vm.pop_str()
        vm.stack.append(ed.hook_summary_rows(query))

    def hc_ed_command_palette(vm: VM) -> None:
        """( query -- ) Open the searchable command/action palette."""
        query = vm.pop_str()
        ed.enter_command_palette(query)

    def hc_ed_command_palette_rows(vm: VM) -> None:
        """( query -- rows ) Return [[name kind menu info] ...] for the command/action palette."""
        query = vm.pop_str()
        vm.stack.append(ed.command_palette_apropos_rows(query))

    def hc_ed_command_palette_section_rows(vm: VM) -> None:
        """( query -- sections ) Return grouped palette rows as [[label [[name kind menu info] ...]] ...]."""
        query = vm.pop_str()
        vm.stack.append(ed.command_palette_section_rows(query))

    def hc_ed_command_palette_section_summary_rows(vm: VM) -> None:
        """( query -- rows ) Tiny count-aware command-palette bucket summaries."""
        query = vm.pop_str()
        vm.stack.append(ed.command_palette_section_summary_rows(query))

    def hc_ed_topic_rows(vm: VM) -> None:
        """( -- rows ) Return [[name kind menu info] ...] for commands/actions/words."""
        vm.stack.append(ed.help_topic_rows())

    def hc_ed_topic_section_rows(vm: VM) -> None:
        """( -- sections ) Return [[label [[name kind menu info] ...]] ...] for topic groups."""
        vm.stack.append(ed.help_topic_section_rows())

    def hc_ed_topic_section_summary_rows(vm: VM) -> None:
        """( -- rows ) Tiny count-aware topic-section summaries."""
        vm.stack.append(ed.help_topic_section_summary_rows())

    def hc_ed_apropos_rows(vm: VM) -> None:
        """( query -- rows ) Return [[name kind menu info] ...] ranked by fuzzy-ish name match."""
        query = vm.pop_str()
        vm.stack.append(ed.apropos_rows(query))

    def hc_ed_apropos_section_rows(vm: VM) -> None:
        """( query -- sections ) Return grouped apropos rows as [[label [[name kind menu info] ...]] ...]."""
        query = vm.pop_str()
        vm.stack.append(ed.apropos_section_rows(query))

    def hc_ed_apropos_section_summary_rows(vm: VM) -> None:
        """( query -- rows ) Tiny count-aware apropos-section summaries."""
        query = vm.pop_str()
        vm.stack.append(ed.apropos_section_summary_rows(query))

    def hc_ed_binding_prompt_rows(vm: VM) -> None:
        """( query -- rows ) Return [[key kind menu info] ...] for searchable current bindings."""
        query = vm.pop_str()
        vm.stack.append(ed.binding_apropos_rows(query))

    def hc_ed_binding_section_rows(vm: VM) -> None:
        """( query -- sections ) Return grouped current-binding rows by winning mode."""
        query = vm.pop_str()
        vm.stack.append(ed.binding_section_rows(query))

    def hc_ed_binding_section_summary_rows(vm: VM) -> None:
        """( query -- rows ) Tiny count-aware winning-mode binding summaries."""
        query = vm.pop_str()
        vm.stack.append(ed.binding_section_summary_rows(query))

    def hc_ed_prompt_kind(vm: VM) -> None:
        vm.stack.append(ed.prompt.kind if ed.prompt else "")

    def hc_ed_prompt_text(vm: VM) -> None:
        vm.stack.append(ed.prompt.text if ed.prompt else "")

    def hc_ed_prompt_set(vm: VM) -> None:
        s = vm.pop_str()
        if ed.prompt is None:
            ed.message("no prompt")
            return
        # Treat scripted prompt manipulation as script-originated.
        with ed.script_context():
            ed.set_prompt_text(s)

    def hc_ed_prompt_submit(vm: VM) -> None:
        with ed.script_context():
            ok = ed.submit_prompt()
        vm.stack.append(1 if ok else 0)


    def hc_ed_prompt_suggestions(vm: VM) -> None:
        """( -- suggs ) Return current prompt suggestions as ["...", ...]."""
        if ed.prompt is None:
            vm.stack.append([])
            return
        vm.stack.append([str(x) for x in ed.prompt.suggestions])

    def hc_ed_prompt_suggestion_rows(vm: VM) -> None:
        """( -- rows ) Return [[insert kind menu info] ...] for prompt suggestions."""
        vm.stack.append(ed.prompt_suggestion_rows())

    def hc_ed_prompt_current_row(vm: VM) -> None:
        """( -- row|[] ) Return [insert kind menu info] for the current prompt selection."""
        vm.stack.append(ed.prompt_current_row())

    def hc_ed_prompt_current_section(vm: VM) -> None:
        """( -- label ) Return the current prompt item's coarse section label."""
        vm.stack.append(ed.prompt_current_section())

    def hc_ed_prompt_current_preview(vm: VM) -> None:
        """( -- s ) Return a compact preview string for the current prompt item."""
        vm.stack.append(ed.prompt_current_preview())

    def hc_ed_prompt_current_position(vm: VM) -> None:
        """( -- m ) Return {index count section section_index section_count summary}."""
        vm.stack.append(ed.prompt_current_position())

    def hc_ed_prompt_window(vm: VM) -> None:
        """( lines -- m ) Return shared picker-window metadata."""
        lines = vm.pop_int()
        vm.stack.append(ed.prompt_window_model(max_lines=lines))

    def hc_ed_prompt_display(vm: VM) -> None:
        """( lines cols -- rows ) Return shared rendered prompt rows."""
        width = vm.pop_int()
        lines = vm.pop_int()
        vm.stack.append(ed.prompt_display_model(max_lines=lines, width=width))

    def hc_ed_prompt_suggest_index(vm: VM) -> None:
        """( -- i ) Current suggestion index, or -1 if none."""
        if ed.prompt is None or not ed.prompt.suggestions:
            vm.stack.append(-1)
            return
        vm.stack.append(int(ed.prompt.suggest_index))

    def hc_ed_prompt_complete(vm: VM) -> None:
        """( dir -- ok ) Complete/cycle prompt suggestions.

        dir >= 0 cycles forward; dir < 0 cycles backward.
        """
        direction = vm.pop_int()
        ok = ed.prompt_complete(direction=direction)
        vm.stack.append(1 if ok else 0)

    def hc_ed_prompt_clear_suggestions(vm: VM) -> None:
        """( -- ok ) Clear the active prompt suggestion session."""
        ok = ed.clear_prompt_suggestions()
        vm.stack.append(1 if ok else 0)

    def hc_ed_input_set(vm: VM) -> None:
        """( key val -- ) Set an action/command input value."""
        val = vm.pop()
        key = vm.pop_str()
        ed.input[key] = val


    def hc_ed_input_get(vm: VM) -> None:
        """( key -- val|0 ) Get an action/command input value (or 0 if missing)."""
        key = vm.pop_str()
        vm.stack.append(ed.input.get(key, 0))

    def hc_ed_input_keys(vm: VM) -> None:
        """( -- keys ) Return sorted input keys."""
        vm.stack.append(sorted([str(k) for k in ed.input.keys()]))

    def hc_ed_input_clear(vm: VM) -> None:
        """( -- ) Clear the input dict."""
        ed.input.clear()

    def hc_ed_input(vm: VM) -> None:
        """( -- pairs ) Return input as [[key val] ...] sorted by key."""
        out: list[list[object]] = []
        for k in sorted([str(x) for x in ed.input.keys()]):
            out.append([k, ed.input.get(k)])
        vm.stack.append(out)

    def hc_ed_insert(vm: VM) -> None:
        s = vm.pop_str()
        ed.input["text"] = s
        ed.run_action("InsertText")

    def hc_ed_backspace(vm: VM) -> None:
        ed.run_action("Backspace")

    def hc_ed_open(vm: VM) -> None:
        """( path -- ok err ) Open a file into a buffer (capability-gated).

        This is intentionally capability-gated because, combined with `ed.text`,
        it provides ambient filesystem read access to scripts.

        When `cap.fs-root` is set, the resolved target must remain within it.
        """

        path = vm.pop_str()
        if not bool(ed.options.get("cap.fs-open")):
            raise MicromaxError("ed.open disabled (set cap.fs-open true)")
        try:
            raw_path, initial_cursor = ed._parse_open_target(str(path))
            p = fs_resolve_path(ed, raw_path)
            if not fs_path_allowed(ed, p):
                vm.stack.append(0)
                vm.stack.append(fs_deny_reason(ed, p))
                return
            ok = bool(ed.open_file(str(p), initial_cursor=initial_cursor))
            vm.stack.append(1 if ok else 0)
            vm.stack.append("")
        except Exception as e:
            vm.stack.append(0)
            vm.stack.append(str(e))

    def hc_ed_save(vm: VM) -> None:
        """( -- ok err ) Save the current buffer to disk (capability-gated).

        This is intentionally capability-gated because it writes to the host
        filesystem. When `cap.fs-root` is set, the target path must remain
        within it.
        """

        if not bool(ed.options.get("cap.fs-save")):
            raise MicromaxError("ed.save disabled (set cap.fs-save true)")

        try:
            eb = ed.cur()
            if bool(ed.options.get("readonly", local=eb.local_options)):
                vm.stack.append(0)
                vm.stack.append("Buffer is read-only")
                return
            if not eb.buf.path:
                vm.stack.append(0)
                vm.stack.append("Buffer has no path")
                return

            p = fs_resolve_path(ed, str(eb.buf.path))
            if not fs_path_allowed(ed, p):
                vm.stack.append(0)
                vm.stack.append(fs_deny_reason(ed, p))
                return

            if p.exists() and p.is_dir():
                vm.stack.append(0)
                vm.stack.append(f"is a directory: {p}")
                return

            eb.buf.path = str(p)
            ed._save_buffer(eb)
            vm.stack.append(1)
            vm.stack.append("")
        except Exception as e:
            vm.stack.append(0)
            vm.stack.append(str(e))

    def hc_ed_text(vm: VM) -> None:
        vm.stack.append(ed.cur().buf.get_text())

    def hc_ed_set_text(vm: VM) -> None:
        s = vm.pop_str()
        try:
            if hasattr(ed, "is_protected_buffer") and ed.is_protected_buffer():
                ed.message("ed.set-text: read-only buffer")
                return
        except Exception:
            pass
        ed.cur().buf.set_text(s)

    def hc_ed_line(vm: VM) -> None:
        """( line -- s ) Get one buffer line (0-based; clamped)."""
        li = vm.pop_int()
        eb = ed.cur()
        if not eb.buf.lines:
            vm.stack.append("")
            return
        li2 = max(0, min(int(li), len(eb.buf.lines) - 1))
        vm.stack.append(str(eb.buf.lines[li2]))

    def hc_ed_lines(vm: VM) -> None:
        """( start count -- lines ) Get a range of lines as ["...", ...]."""
        count = vm.pop_int()
        start = vm.pop_int()
        eb = ed.cur()
        if count <= 0:
            vm.stack.append([])
            return
        a = max(0, int(start))
        b = min(len(eb.buf.lines), a + int(count))
        vm.stack.append([str(x) for x in eb.buf.lines[a:b]])

    def hc_ed_highlight(vm: VM) -> None:
        """( start count -- spans ) Return per-line highlight spans.

        `spans` is a list aligned with the requested range; each element is
        [[start end tag] ...] for that line.
        """
        count = vm.pop_int()
        start = vm.pop_int()
        vm.stack.append(ed.highlight_spans(int(start), int(count)))

    def hc_ed_highlight_tags(vm: VM) -> None:
        """( -- tags ) Return known highlight tag vocabulary."""
        vm.stack.append(ed.highlight_tags())

    # ----- timers -----
    def hc_ed_after(vm: VM) -> None:
        """( ms q -- id ) Schedule quotation to run after ms milliseconds."""
        q = vm.pop_quote()
        ms = vm.pop_int()
        group = getattr(vm, "current_editor_group", None)
        tid = ed.timers.schedule(now=ed.now(), delay_ms=int(ms), xt=q, group=group)
        vm.stack.append(int(tid))

    def hc_ed_cancel_timer(vm: VM) -> None:
        """( id -- ok ) Cancel a scheduled timer."""
        tid = vm.pop_int()
        vm.stack.append(1 if ed.timers.cancel(int(tid)) else 0)

    def hc_ed_pump_timers(vm: VM) -> None:
        """( -- ran ) Run due timers and return how many ran."""
        vm.stack.append(int(ed.pump_timers()))

    # ----- plugins -----
    def hc_plugin_list(vm: VM) -> None:
        """( -- xs ) Return loaded plugin names."""
        pm = getattr(ed, "plugin_manager", None)
        vm.stack.append(sorted(pm.plugins.keys()) if pm else [])

    def hc_plugin_reload(vm: VM) -> None:
        """( "name" -- ok ) Reload a plugin by name.

        The live scripting path should reuse the same trust-first feedback dialect
        as the command-bar `plugin reload NAME` path instead of drifting back to
        older generic error messages.
        """
        name = vm.pop_str()
        vm.stack.append(1 if ed.plugin_reload_with_feedback(str(name)) else 0)

    def hc_plugin_errors(vm: VM) -> None:
        """( -- xs ) Return captured plugin load errors as [[name,err] ...]."""
        pm = getattr(ed, "plugin_manager", None)
        vm.stack.append([[n, err] for (n, err) in (pm.load_errors if pm else [])])



    def hc_ed_viewport(vm: VM) -> None:
        """( -- m ) Return viewport as {top_line,top_subline,left_col,height,width}."""
        vm.stack.append(ed.viewport_model())

    def hc_ed_viewport_store(vm: VM) -> None:
        """( top left height width -- ) Set viewport model."""
        width = vm.pop_int()
        height = vm.pop_int()
        left = vm.pop_int()
        top = vm.pop_int()
        ed.set_viewport(top_line=top, left_col=left, height=height, width=width, follow_cursor=True)

    def hc_ed_cursor(vm: VM) -> None:
        """( -- line col ) Primary cursor position (0-based)."""
        c = ed.primary_cursor()
        vm.stack.append(int(c.line))
        vm.stack.append(int(c.col))

    def hc_ed_set_cursor(vm: VM) -> None:
        """( line col -- ) Set primary cursor (0-based; clamped)."""
        col = vm.pop_int()
        line = vm.pop_int()
        eb = ed.cur()
        ed._normalize_cursor_lists(eb)
        eb.cursors[eb.primary] = eb.buf.clamp(Cursor(line, col))

    def hc_ed_has_selection(vm: VM) -> None:
        vm.stack.append(1 if ed.has_primary_selection() else 0)

    def hc_ed_selection_text(vm: VM) -> None:
        vm.stack.append(ed.selection_text(None))

    def hc_ed_clear_selection(vm: VM) -> None:
        eb = ed.cur()
        ed._normalize_cursor_lists(eb)
        ed.clear_selection(eb.primary)

    # ----- multicursor / selections -----
    def hc_ed_cursors(vm: VM) -> None:
        """( -- cursors ) Return cursor list in document order as [[line col] ...]."""
        eb = ed.cur()
        ed._normalize_cursor_lists(eb)
        vm.stack.append([[int(c.line), int(c.col)] for c in eb.cursors])

    def hc_ed_set_cursors(vm: VM) -> None:
        """( cursors -- ) Set cursor list from [[line col] ...]. Clears selections."""
        raw = vm.pop_list()
        curs: list[Cursor] = []
        for it in raw:
            if not isinstance(it, list) or len(it) != 2:
                raise MicromaxError("ed.set-cursors: expected [[line col] ...]")
            line = int(it[0])
            col = int(it[1])
            curs.append(Cursor(line, col))
        if not curs:
            curs = [Cursor(0, 0)]
        eb = ed.cur()
        eb.cursors[:] = [eb.buf.clamp(Cursor(c.line, c.col)) for c in curs]
        eb.sel_anchors[:] = [None] * len(eb.cursors)
        eb.cursor_ids[:] = [ed._alloc_cursor_id() for _ in eb.cursors]
        eb.primary = 0
        ed._normalize_cursor_lists(eb)

    def hc_ed_primary(vm: VM) -> None:
        """( -- i ) Return primary cursor index (into ed.cursors)."""
        vm.stack.append(ed.primary_index())

    def hc_ed_set_primary(vm: VM) -> None:
        """( i -- ) Set primary cursor index."""
        i = vm.pop_int()
        ed.set_primary_index(i)

    def hc_ed_selections(vm: VM) -> None:
        """( -- sels ) Return selections per cursor as [[aL aC cL cC] ...] or [] if none."""
        eb = ed.cur()
        ed._normalize_cursor_lists(eb)
        out: list[list[int]] = []
        for i in range(len(eb.cursors)):
            a = eb.sel_anchors[i]
            if a is None:
                out.append([])
            else:
                c = eb.cursors[i]
                out.append([int(a.line), int(a.col), int(c.line), int(c.col)])
        vm.stack.append(out)

    def hc_ed_set_selections(vm: VM) -> None:
        """( sels -- ) Set selections per cursor.

        `sels` must be a list with length == cursor count.

        Each entry is either:
          - []            : clear selection for that cursor (cursor position unchanged)
          - [aL aC cL cC] : set anchor+cursor for that cursor (directed)

        This is intentionally a low-level state setter that uses only lists/ints.
        """

        raw = vm.pop_list()
        eb = ed.cur()
        ed._normalize_cursor_lists(eb)
        if len(raw) != len(eb.cursors):
            raise MicromaxError("ed.set-selections: sels length must match cursor count")

        for i, it in enumerate(raw):
            if it == []:
                eb.sel_anchors[i] = None
                continue
            if not isinstance(it, list) or len(it) != 4:
                raise MicromaxError("ed.set-selections: expected [] or [aL aC cL cC]")
            aL, aC, cL, cC = (int(it[0]), int(it[1]), int(it[2]), int(it[3]))
            eb.sel_anchors[i] = eb.buf.clamp(Cursor(aL, aC))
            eb.cursors[i] = eb.buf.clamp(Cursor(cL, cC))

        ed._normalize_cursor_lists(eb)

    def hc_ed_selection_range(vm: VM) -> None:
        """( -- range ) Return the *normalized* primary selection range.

        Returns [] if there is no non-empty selection, else [line1 col1 line2 col2].
        Note: this is range-oriented (directionless). For directed endpoints, use
        `ed.selections`.
        """

        rng = ed.selection_range(None)
        if rng is None:
            vm.stack.append([])
            return
        s, e = rng
        vm.stack.append([int(s.line), int(s.col), int(e.line), int(e.col)])

    def hc_ed_set_selection_range(vm: VM) -> None:
        """( line1 col1 line2 col2 -- ) Set the primary selection to a range.

        The stored selection is directed, but the inputs are treated as a
        range: if the endpoints are reversed, they are swapped.
        """

        col2 = vm.pop_int()
        line2 = vm.pop_int()
        col1 = vm.pop_int()
        line1 = vm.pop_int()
        eb = ed.cur()
        ed._normalize_cursor_lists(eb)
        a = eb.buf.clamp(Cursor(line1, col1))
        c = eb.buf.clamp(Cursor(line2, col2))
        if (a.line, a.col) > (c.line, c.col):
            a, c = c, a
        eb.sel_anchors[eb.primary] = a
        eb.cursors[eb.primary] = c
        ed._normalize_cursor_lists(eb)

    def hc_ed_replace_selections(vm: VM) -> None:
        """( replacements -- line col ) Replace each selection (or insert at cursor if none).

        `replacements` can be:
          - a list of strings with length == cursor count (per-cursor)
          - a single string (applies to all cursors)

        This is undoable.
        """

        raw = vm.pop()
        if isinstance(raw, list):
            reps = [str(x) for x in raw]
        else:
            reps = [str(raw)]

        eb = ed.cur()
        ed._normalize_cursor_lists(eb)
        before = ed._snapshot_buffer_state(eb)

        if len(reps) == len(eb.cursors):
            per = reps
        elif len(reps) == 1:
            per = reps * len(eb.cursors)
        else:
            raise MicromaxError("ed.replace-selections: replacements must be 1 or match cursor count")

        ops: list[tuple[int, Cursor, Cursor]] = []
        for i in range(len(eb.cursors)):
            rng = ed.selection_range(i)
            if rng is None:
                s = eb.cursors[i]
                e = eb.cursors[i]
            else:
                s, e = rng
            ops.append((i, s, e))

        ops.sort(key=lambda t: (t[1].line, t[1].col), reverse=True)
        for i, s, e in ops:
            eb.cursors[i] = eb.buf.replace_range(s, e, per[i])
            eb.sel_anchors[i] = None

        after = ed._snapshot_buffer_state(eb)
        ed._record_undo_snapshot(eb, before, after, "ReplaceSelections")

        c = ed.primary_cursor()
        vm.stack.append(int(c.line))
        vm.stack.append(int(c.col))


    def hc_ed_range_text(vm: VM) -> None:
        """( line1 col1 line2 col2 -- "text" ) Get text in range (primary buffer)."""
        col2 = vm.pop_int()
        line2 = vm.pop_int()
        col1 = vm.pop_int()
        line1 = vm.pop_int()
        eb = ed.cur()
        s = eb.buf.clamp(Cursor(line1, col1))
        e = eb.buf.clamp(Cursor(line2, col2))
        if (s.line, s.col) > (e.line, e.col):
            s, e = e, s
        vm.stack.append(eb.buf.get_range_text(s, e))

    def hc_ed_replace_range(vm: VM) -> None:
        """( line1 col1 line2 col2 "text" -- line col ) Replace range with text (undoable)."""
        text = vm.pop_str()
        col2 = vm.pop_int()
        line2 = vm.pop_int()
        col1 = vm.pop_int()
        line1 = vm.pop_int()
        eb = ed.cur()
        ed._normalize_cursor_lists(eb)
        before = ed._snapshot_buffer_state(eb)
        s = eb.buf.clamp(Cursor(line1, col1))
        e = eb.buf.clamp(Cursor(line2, col2))
        if (s.line, s.col) > (e.line, e.col):
            s, e = e, s
        ed._normalize_cursor_lists(eb)
        eb.cursors[eb.primary] = eb.buf.replace_range(s, e, text)
        eb.sel_anchors[eb.primary] = None
        after = ed._snapshot_buffer_state(eb)
        ed._record_undo_snapshot(eb, before, after, 'ReplaceRange')
        c = ed.primary_cursor()
        vm.stack.append(int(c.line))
        vm.stack.append(int(c.col))

    def hc_ed_delete_range(vm: VM) -> None:
        """( line1 col1 line2 col2 -- line col ) Delete range (undoable)."""
        col2 = vm.pop_int()
        line2 = vm.pop_int()
        col1 = vm.pop_int()
        line1 = vm.pop_int()
        eb = ed.cur()
        ed._normalize_cursor_lists(eb)
        before = ed._snapshot_buffer_state(eb)
        s = eb.buf.clamp(Cursor(line1, col1))
        e = eb.buf.clamp(Cursor(line2, col2))
        if (s.line, s.col) > (e.line, e.col):
            s, e = e, s
        ed._normalize_cursor_lists(eb)
        eb.cursors[eb.primary] = eb.buf.replace_range(s, e, '')
        eb.sel_anchors[eb.primary] = None
        after = ed._snapshot_buffer_state(eb)
        ed._record_undo_snapshot(eb, before, after, 'DeleteRange')
        c = ed.primary_cursor()
        vm.stack.append(int(c.line))
        vm.stack.append(int(c.col))


    # ----- undo grouping / transactions -----
    def hc_ed_with_undo(vm: VM) -> None:
        """( "desc" [ ... ] -- ok ) Run quotation as a single undo step.

        This groups *buffer-visible* changes in the active buffer into one undo entry.
        If the quotation raises, the buffer is restored and no undo entry is recorded.
        """

        q = vm.pop_quote()
        desc = vm.pop_str()
        eb = ed.cur()
        ed._normalize_cursor_lists(eb)
        before = ed._snapshot_buffer_state(eb)
        try:
            with ed.undo.suppress_recording():
                vm.exec_xt(q)
        except Exception:
            ed._restore_buffer_state(eb, before)
            raise
        after = ed._snapshot_buffer_state(eb)
        if after != before:
            ed._record_undo_snapshot(eb, before, after, desc or 'with-undo')
        vm.stack.append(1)

    # ----- clipboard -----
    def hc_ed_clipboard(vm: VM) -> None:
        """( -- "text" ) Return clipboard as a single string."""

        vm.stack.append(ed.clipboard_text())

    def hc_ed_set_clipboard(vm: VM) -> None:
        """( "text" -- ) Set clipboard from a single string (kind=items)."""

        s = vm.pop_str()
        ed.set_clipboard_items([s], kind='items')
        ed._paste_reset()

    def hc_ed_clipboard_items(vm: VM) -> None:
        """( -- items kind ) Return clipboard items + kind ("items"|"lines")."""

        vm.stack.append([str(x) for x in ed.clipboard_items])
        vm.stack.append(str(ed.clipboard_kind))

    def hc_ed_set_clipboard_items(vm: VM) -> None:
        """( items kind -- ) Set clipboard from item list + kind ("items"|"lines")."""

        kind = vm.pop_str()
        raw = vm.pop_list()
        if kind not in ('items', 'lines'):
            raise MicromaxError('ed.set-clipboard-items: kind must be items|lines')
        ed.set_clipboard_items([str(x) for x in raw], kind=kind)
        ed._paste_reset()


    def hc_ed_clipboard_import(vm: VM) -> None:
        """( -- ok text err ) Import system clipboard via external tools (capability-gated)."""

        if not bool(ed.options.get("cap.clipboard-read")):
            raise MicromaxError("ed.clipboard-import disabled (set cap.clipboard-read true)")

        text, err = ed.clipboard_external_import_text()
        if text is None:
            vm.stack.append(0)
            vm.stack.append("")
            vm.stack.append(str(err or "clipboard import failed"))
            return

        vm.stack.append(1)
        vm.stack.append(str(text))
        vm.stack.append("")

    # ----- cursor/selection recovery stack -----
    def hc_ed_push_selections(vm: VM) -> None:
        """( -- ) Save current cursor+selection state to a small stack."""

        ed.push_selections()

    def hc_ed_pop_selections(vm: VM) -> None:
        """( -- ok ) Restore last saved cursor+selection state."""

        vm.stack.append(1 if ed.pop_selections() else 0)

    def hc_ed_clear_saved_selections(vm: VM) -> None:
        """( -- ) Clear saved selection states."""

        ed.clear_saved_selections()

    # ----- cursor/selection state snapshot (portable save/restore) -----
    def hc_ed_cursorstate(vm: VM) -> None:
        """( -- state ) Return cursor+selection state for the active buffer.

        Returns:
          [primary [[id line col aL aC] ...]]

        Where aL/aC are -1/-1 if there is no selection anchor for that cursor.

        This is intended as a low-level, portable snapshot (lists + ints only)
        that can be stored by plugins and restored later.
        """

        eb = ed.cur()
        ed._normalize_cursor_lists(eb)
        entries: list[list[int]] = []
        for i, c in enumerate(eb.cursors):
            cid = int(eb.cursor_ids[i])
            a = eb.sel_anchors[i]
            if a is None:
                entries.append([cid, int(c.line), int(c.col), -1, -1])
            else:
                entries.append([cid, int(c.line), int(c.col), int(a.line), int(a.col)])
        vm.stack.append([int(eb.primary), entries])

    def hc_ed_set_cursorstate(vm: VM) -> None:
        """( state -- ) Restore cursor+selection state for the active buffer.

        `state` must be [primary [[id line col aL aC] ...]].
        """

        state = vm.pop_list()
        if len(state) != 2:
            raise MicromaxError('ed.set-cursorstate: expected [primary [[id line col aL aC] ...]]')

        primary = int(state[0])
        raw = state[1]
        if not isinstance(raw, list):
            raise MicromaxError('ed.set-cursorstate: expected [primary [[...]]].')

        eb = ed.cur()
        curs: list[Cursor] = []
        anchors: list[Cursor | None] = []
        ids: list[int] = []

        seen: set[int] = set()
        for it in raw:
            if not isinstance(it, list) or len(it) != 5:
                raise MicromaxError('ed.set-cursorstate: expected entries [id line col aL aC]')
            cid, line, col, aL, aC = (int(it[0]), int(it[1]), int(it[2]), int(it[3]), int(it[4]))

            if cid <= 0 or cid in seen:
                cid = ed._alloc_cursor_id()
            seen.add(cid)

            curs.append(eb.buf.clamp(Cursor(line, col)))
            if aL < 0 or aC < 0:
                anchors.append(None)
            else:
                anchors.append(eb.buf.clamp(Cursor(aL, aC)))
            ids.append(cid)

        if not curs:
            curs = [Cursor(0, 0)]
            anchors = [None]
            ids = [ed._alloc_cursor_id()]
            primary = 0

        eb.cursors[:] = curs
        eb.sel_anchors[:] = anchors
        eb.cursor_ids[:] = ids
        eb.primary = primary

        # Keep the id allocator monotonic even if we restored older ids.
        try:
            mx = max(int(x) for x in eb.cursor_ids)
            if mx >= ed._next_cursor_id:
                ed._next_cursor_id = mx + 1
        except Exception:
            pass

        ed._normalize_cursor_lists(eb)

    def hc_ed_with_cursorstate(vm: VM) -> None:
        """( q -- ok ) Run quotation and then restore cursor/selection state.

        This is the editor analogue of Emacs' `save-excursion` and Vim's
        "save/restore cursor" mapping patterns: it lets commands perform helper
        edits/navigation without permanently moving the user's cursor(s).

        Only cursor/selection state is restored (not buffer text).
        """

        q = vm.pop_quote()
        eb = ed.cur()
        ed._normalize_cursor_lists(eb)
        snap = (
            [Cursor(c.line, c.col) for c in eb.cursors],
            [Cursor(a.line, a.col) if a is not None else None for a in eb.sel_anchors],
            [int(x) for x in eb.cursor_ids],
            int(eb.primary),
        )
        try:
            vm.exec_xt(q)
        finally:
            eb.cursors[:] = [Cursor(c.line, c.col) for c in snap[0]]
            eb.sel_anchors[:] = [Cursor(a.line, a.col) if a is not None else None for a in snap[1]]
            eb.cursor_ids[:] = [int(x) for x in snap[2]]
            eb.primary = int(snap[3])
            ed._normalize_cursor_lists(eb)
        vm.stack.append(1)

    # ----- jumplist (navigation history) -----
    def hc_ed_push_jump(vm: VM) -> None:
        vm.stack.append(1 if ed.push_jump() else 0)

    def hc_ed_jump_back(vm: VM) -> None:
        vm.stack.append(1 if ed.jump_back() else 0)

    def hc_ed_jump_forward(vm: VM) -> None:
        vm.stack.append(1 if ed.jump_forward() else 0)

    def hc_ed_jump_info(vm: VM) -> None:
        idx, n = ed.jump_info()
        vm.stack.append([int(idx), int(n)])

    def hc_ed_clear_jumps(vm: VM) -> None:
        ed.clear_jumps()

    def hc_ed_jump_history_rows(vm: VM) -> None:
        """( -- rows ) Ordered jumplist register rows for the current buffer."""
        vm.stack.append(ed.jump_history_rows())

    def hc_ed_jump_detail_row(vm: VM) -> None:
        """( n|"#n" -- row|0 ) Tiny inspectable exact jumplist row as [query index lane depth buffer position preview]."""
        query = vm.pop_str()
        row = ed.jump_detail_row(query)
        vm.stack.append(0 if row is None else row)

    def hc_ed_jump_section_rows(vm: VM) -> None:
        """( query -- sections ) Grouped jumplist rows by current/back/forward."""
        query = vm.pop_str()
        vm.stack.append(ed.jump_section_rows(query))

    def hc_ed_jump_section_summary_rows(vm: VM) -> None:
        """( query -- rows ) Tiny count-aware jumplist section summaries."""
        query = vm.pop_str()
        vm.stack.append(ed.jump_section_summary_rows(query))

    def hc_ed_find(vm: VM) -> None:
        q = vm.pop_str()
        ok = ed.find(q, literal=ed.search.literal)
        vm.stack.append(1 if ok else 0)

    def hc_ed_find_next(vm: VM) -> None:
        vm.stack.append(1 if ed.find_next() else 0)

    def hc_ed_find_prev(vm: VM) -> None:
        vm.stack.append(1 if ed.find_prev() else 0)

    def hc_ed_option_inventory_rows(vm: VM) -> None:
        vm.stack.append(ed.option_inventory_rows())

    def hc_ed_option_section_summary_rows(vm: VM) -> None:
        """( query -- rows ) Tiny count-aware option-family summaries as [label count sample_name sample_detail]."""
        query = vm.pop_str()
        vm.stack.append(ed.option_section_summary_rows(query))

    def hc_ed_option_detail_row(vm: VM) -> None:
        """( name -- row|0 ) Tiny inspectable exact option-detail row as [query canonical value default kind local_override doc]."""
        name = vm.pop_str()
        row = ed.option_detail_row(name)
        vm.stack.append(0 if row is None else row)

    def hc_ed_opt_get(vm: VM) -> None:
        name = vm.pop_str()
        val = ed.options.get(name, local=ed.cur().local_options)
        if isinstance(val, bool):
            vm.stack.append(1 if val else 0)
        else:
            vm.stack.append(val)

    def hc_ed_opt_set(vm: VM) -> None:
        raw = vm.pop_str()
        name = vm.pop_str()
        # Global set (like the command-bar `set`).
        val = ed.options.set(name, raw)
        if str(ed.options.resolve_name(str(name))) == "fastdirty":
            try:
                ed._sync_all_buffer_fastdirty_modes()
            except Exception:
                pass
        if str(name).startswith("cap."):
            try:
                ed.refresh_capabilities()
            except Exception:
                pass
        if isinstance(val, bool):
            vm.stack.append(1 if val else 0)
        else:
            vm.stack.append(val)

    def hc_ed_opt_set_local(vm: VM) -> None:
        """( "name" "raw" -- value ) Set a buffer-local option."""
        raw = vm.pop_str()
        name = vm.pop_str()
        val = ed.options.set(name, raw, local=ed.cur().local_options)
        if str(ed.options.resolve_name(str(name))) == "fastdirty":
            try:
                ed._sync_all_buffer_fastdirty_modes()
            except Exception:
                pass
        if isinstance(val, bool):
            vm.stack.append(1 if val else 0)
        else:
            vm.stack.append(val)

    def hc_ed_require(vm: VM) -> None:
        """( path -- ) Load a micromax file relative to cwd."""
        path = vm.pop_str()
        p = Path(path)
        if not p.exists():
            raise MicromaxError(f"ed.require: file not found: {path}")
        vm.eval(p.read_text(encoding="utf-8"), filename=str(p))


    # ----- macros (portable representation) -----
    # Portable macro encoding uses only lists/ints/strings:
    #   ["a", ACTION, [[key val] ...]]   action step with input snapshot
    #   ["c", CMDLINE]                  command-bar line
    def _encode_macro_steps(steps: list["MacroStep"]) -> list[list[object]]:
        out: list[list[object]] = []
        for st in steps:
            if st.kind == "action":
                inp = dict(st.payload.get("input", {}))
                pairs = [[str(k), inp.get(k)] for k in sorted(inp.keys(), key=lambda x: str(x))]
                out.append(["a", str(st.name), pairs])
            elif st.kind == "command":
                out.append(["c", str(st.payload.get("cmdline", ""))])
        return out

    def _decode_macro_steps(raw: object) -> list["MacroStep"]:
        if not isinstance(raw, list):
            raise MicromaxError("macro: expected list of steps")
        steps: list[MacroStep] = []
        for it in raw:
            if not isinstance(it, list) or not it:
                raise MicromaxError("macro: bad step")
            tag = str(it[0])
            if tag == "a":
                if len(it) != 3:
                    raise MicromaxError("macro: action step must be ['a', name, [[k v]...]]")
                name = str(it[1])
                pairs = it[2]
                if not isinstance(pairs, list):
                    raise MicromaxError("macro: action step inputs must be list")
                inp: dict[str, object] = {}
                for pv in pairs:
                    if not isinstance(pv, list) or len(pv) != 2:
                        raise MicromaxError("macro: input pair must be [k v]")
                    inp[str(pv[0])] = pv[1]
                steps.append(MacroStep(kind="action", name=name, payload={"input": inp}))
                continue
            if tag == "c":
                if len(it) != 2:
                    raise MicromaxError("macro: command step must be ['c', cmdline]")
                cmdline = str(it[1])
                steps.append(MacroStep(kind="command", name="command", payload={"cmdline": cmdline}))
                continue
            raise MicromaxError(f"macro: unknown step tag {tag!r}")
        return steps

    def hc_ed_macro_names(vm: VM) -> None:
        """( -- names ) List available macro names."""
        vm.stack.append(ed.macro_names())

    def hc_ed_macro_inventory_rows(vm: VM) -> None:
        """( -- rows ) Tiny inspectable macro inventory rows as [name steps]."""
        vm.stack.append(ed.macro_inventory_rows())

    def hc_ed_macro_status_rows(vm: VM) -> None:
        """( -- rows ) Combined macro status rows as [section ...]."""
        vm.stack.append(ed.macro_status_rows())

    def hc_ed_macro_get(vm: VM) -> None:
        """( name -- steps ) Get a macro as portable steps."""
        name = vm.pop_str()
        vm.stack.append(_encode_macro_steps(ed.get_macro(name)))

    def hc_ed_macro_set(vm: VM) -> None:
        """( steps name -- ) Set a macro from portable steps."""
        name = vm.pop_str()
        steps = _decode_macro_steps(vm.pop())
        ed.set_macro(name, steps)

    def hc_ed_macro_record(vm: VM) -> None:
        """( name -- ok ) Start recording macro into name."""
        name = vm.pop_str()
        vm.stack.append(1 if ed.start_macro(name) else 0)

    def hc_ed_macro_stop(vm: VM) -> None:
        """( -- ok ) Stop recording and save."""
        vm.stack.append(1 if ed.stop_macro() else 0)

    def hc_ed_macro_cancel(vm: VM) -> None:
        """( -- ok ) Cancel recording without saving."""
        vm.stack.append(1 if ed.cancel_macro() else 0)

    def hc_ed_macro_play(vm: VM) -> None:
        """( name n -- ok ) Play named macro n times."""
        n = vm.pop_int()
        name = vm.pop_str()
        vm.stack.append(1 if ed.play_macro(name, count=n) else 0)

    def hc_ed_macro_recording(vm: VM) -> None:
        """( -- flag ) True if macro recording is active."""
        vm.stack.append(1 if ed.macro_recording else 0)

    def hc_ed_macro_playing(vm: VM) -> None:
        """( -- flag ) True if macro playback is active."""
        vm.stack.append(1 if getattr(ed, "_macro_playing", False) else 0)

    vm.register_host("ed.msg", hc_ed_msg)
    vm.register_host("ed.messages", hc_ed_messages)
    vm.register_host("ed.last-message", hc_ed_last_message)
    vm.register_host("ed.pop-message", hc_ed_pop_message)
    vm.register_host("ed.clear-messages", hc_ed_clear_messages)

    vm.register_host("host.capabilities", hc_host_capabilities)
    vm.register_host("ed.open-url", hc_ed_open_url)
    vm.register_host("ed.shell", hc_ed_shell)
    vm.register_host("ed.fs-read", hc_ed_fs_read)
    vm.register_host("ed.fs-list", hc_ed_fs_list)
    vm.register_host("ed.fs-stat", hc_ed_fs_stat)

    vm.register_host("ed.buffers", hc_ed_buffers)
    vm.register_host("ed.buffer-inventory-rows", hc_ed_buffer_inventory_rows)
    vm.register_host("ed.buffer-detail-row", hc_ed_buffer_detail_row)
    vm.register_host("ed.buffer-section-rows", hc_ed_buffer_section_rows)
    vm.register_host("ed.buffer-section-summary-rows", hc_ed_buffer_section_summary_rows)
    vm.register_host("ed.active-buffer", hc_ed_active_buffer)
    vm.register_host("ed.set-active-buffer", hc_ed_set_active_buffer)
    vm.register_host("ed.mark-set", hc_ed_mark_set)
    vm.register_host("ed.mark-jump", hc_ed_mark_jump)
    vm.register_host("ed.marks", hc_ed_marks)
    vm.register_host("ed.mark-inventory-rows", hc_ed_mark_inventory_rows)
    vm.register_host("ed.mark-detail-row", hc_ed_mark_detail_row)
    vm.register_host("ed.mark-section-rows", hc_ed_mark_section_rows)
    vm.register_host("ed.mark-section-summary-rows", hc_ed_mark_section_summary_rows)
    vm.register_host("ed.status", hc_ed_status)
    vm.register_host("ed.status-summary", hc_ed_status_summary)
    vm.register_host("ed.statusfmt", hc_ed_statusfmt)
    vm.register_host("ed.statusline-text", hc_ed_statusline_text)
    vm.register_host("ed.statusline-model", hc_ed_statusline_model)
    vm.register_host("ed.prompt-panel", hc_ed_prompt_panel)
    vm.register_host("ed.gutter-model", hc_ed_gutter_model)
    vm.register_host("ed.interaction-model", hc_ed_interaction_model)
    vm.register_host("ed.keymenu-model", hc_ed_keymenu_model)
    vm.register_host("ed.infobar-model", hc_ed_infobar_model)
    vm.register_host("ed.screen-layout", hc_ed_screen_layout)
    vm.register_host("ed.edit-window", hc_ed_edit_window)
    vm.register_host("ed.search-rows", hc_ed_search_rows)
    vm.register_host("ed.showchars-rows", hc_ed_showchars_rows)
    vm.register_host("ed.viewport-cues", hc_ed_viewport_cues)
    vm.register_host("ed.docs-cues", hc_ed_docs_cues)
    vm.register_host("ed.display-rows", hc_ed_display_rows)
    vm.register_host("ed.viewport-rows", hc_ed_viewport_rows)
    vm.register_host("ed.screen-model", hc_ed_screen_model)
    vm.register_host("ed.screen-rows", hc_ed_screen_rows)
    vm.register_host("ed.bottom-rows", hc_ed_bottom_rows)
    vm.register_host("ed.with-buffer", hc_ed_with_buffer)
    vm.register_host("ed.with-viewport", hc_ed_with_viewport)
    vm.register_host("ed.plugin-inventory-rows", hc_ed_plugin_inventory_rows)
    vm.register_host("ed.plugin-detail-row", hc_ed_plugin_detail_row)
    vm.register_host("ed.plugin-section-rows", hc_ed_plugin_section_rows)
    vm.register_host("ed.plugin-section-summary-rows", hc_ed_plugin_section_summary_rows)
    vm.register_host("ed.recent", hc_ed_recent)
    vm.register_host("ed.recent-clear", hc_ed_recent_clear)
    vm.register_host("ed.recent-clear-count", hc_ed_recent_clear_count)
    vm.register_host("ed.recent-inventory-rows", hc_ed_recent_inventory_rows)
    vm.register_host("ed.recent-detail-row", hc_ed_recent_detail_row)
    vm.register_host("ed.recent-slot-detail-row", hc_ed_recent_slot_detail_row)
    vm.register_host("ed.recent-dir-detail-row", hc_ed_recent_dir_detail_row)
    vm.register_host("ed.recent-slot-dir-detail-row", hc_ed_recent_slot_dir_detail_row)
    vm.register_host("ed.recent-section-rows", hc_ed_recent_section_rows)
    vm.register_host("ed.recent-section-summary-rows", hc_ed_recent_section_summary_rows)
    vm.register_host("ed.recent-dir-section-rows", hc_ed_recent_dir_section_rows)
    vm.register_host("ed.recent-dir-section-summary-rows", hc_ed_recent_dir_section_summary_rows)
    vm.register_host("ed.recent-prompt-rows", hc_ed_recent_prompt_rows)
    vm.register_host("ed.recent-dir-prompt-rows", hc_ed_recent_dir_prompt_rows)
    vm.register_host("ed.doc-rows", hc_ed_doc_rows)
    vm.register_host("ed.doc-section-rows", hc_ed_doc_section_rows)
    vm.register_host("ed.doc-section-summary-rows", hc_ed_doc_section_summary_rows)
    vm.register_host("ed.help-doc", hc_ed_help_doc)
    vm.register_host("ed.help-follow", hc_ed_help_follow)
    vm.register_host("ed.help-back", hc_ed_help_back)
    vm.register_host("ed.help-forward", hc_ed_help_forward)
    vm.register_host("ed.help-resume", hc_ed_help_resume)
    vm.register_host("ed.help-prune", hc_ed_help_prune)
    vm.register_host("ed.help-link-rows", hc_ed_help_link_rows)
    vm.register_host("ed.help-link-detail-row", hc_ed_help_link_detail_row)
    vm.register_host("ed.helphistory-rows", hc_ed_helphistory_rows)
    vm.register_host("ed.helplink-section-rows", hc_ed_helplink_section_rows)
    vm.register_host("ed.help-outline-rows", hc_ed_help_outline_rows)
    vm.register_host("ed.help-outline-section-rows", hc_ed_help_outline_section_rows)
    vm.register_host("ed.helpnav-section-rows", hc_ed_helpnav_section_rows)
    vm.register_host("ed.helpnav-section-summary-rows", hc_ed_helpnav_section_summary_rows)
    vm.register_host("ed.filetype", hc_ed_filetype)
    vm.register_host("ed.with-messages", hc_ed_with_messages)
    vm.register_host("ed.capture-messages", hc_ed_capture_messages)
    vm.register_host("ed.macro-names", hc_ed_macro_names)
    vm.register_host("ed.macro-inventory-rows", hc_ed_macro_inventory_rows)
    vm.register_host("ed.macro-status-rows", hc_ed_macro_status_rows)
    vm.register_host("ed.macro-get", hc_ed_macro_get)
    vm.register_host("ed.macro-set", hc_ed_macro_set)
    vm.register_host("ed.macro-record", hc_ed_macro_record)
    vm.register_host("ed.macro-stop", hc_ed_macro_stop)
    vm.register_host("ed.macro-cancel", hc_ed_macro_cancel)
    vm.register_host("ed.macro-play", hc_ed_macro_play)
    vm.register_host("ed.macro-recording?", hc_ed_macro_recording)
    vm.register_host("ed.macro-playing?", hc_ed_macro_playing)
    vm.register_host("ed.cmd-add", hc_ed_cmd_add)
    vm.register_host("ed.hook-detail-row", hc_ed_hook_detail_row)
    vm.register_host("ed.hook-inventory-rows", hc_ed_hook_inventory_rows)
    vm.register_host("ed.hook-summary-rows", hc_ed_hook_summary_rows)
    vm.register_host("ed.cmd-rm", hc_ed_cmd_rm)
    vm.register_host("ed.cmds", hc_ed_cmds)
    vm.register_host("ed.cmd-rows", hc_ed_cmd_rows)
    vm.register_host("ed.command-detail-row", hc_ed_command_detail_row)
    vm.register_host("ed.action-detail-row", hc_ed_action_detail_row)
    vm.register_host("ed.word-detail-row", hc_ed_word_detail_row)
    vm.register_host("ed.doc-detail-row", hc_ed_doc_detail_row)
    vm.register_host("ed.topic-detail-row", hc_ed_topic_detail_row)
    vm.register_host("ed.help-current-heading-detail-row", hc_ed_help_current_heading_detail_row)
    vm.register_host("ed.help-heading-detail-row", hc_ed_help_heading_detail_row)
    vm.register_host("ed.command-palette", hc_ed_command_palette)
    vm.register_host("ed.command-palette-rows", hc_ed_command_palette_rows)
    vm.register_host("ed.command-palette-section-rows", hc_ed_command_palette_section_rows)
    vm.register_host("ed.command-palette-section-summary-rows", hc_ed_command_palette_section_summary_rows)
    vm.register_host("ed.topic-rows", hc_ed_topic_rows)
    vm.register_host("ed.topic-section-rows", hc_ed_topic_section_rows)
    vm.register_host("ed.topic-section-summary-rows", hc_ed_topic_section_summary_rows)
    vm.register_host("ed.topic-prompt", hc_ed_topic_prompt)
    vm.register_host("ed.binding-prompt", hc_ed_binding_prompt)
    vm.register_host("ed.apropos-rows", hc_ed_apropos_rows)
    vm.register_host("ed.apropos-section-rows", hc_ed_apropos_section_rows)
    vm.register_host("ed.apropos-section-summary-rows", hc_ed_apropos_section_summary_rows)
    vm.register_host("ed.binding-prompt-rows", hc_ed_binding_prompt_rows)
    vm.register_host("ed.binding-section-rows", hc_ed_binding_section_rows)
    vm.register_host("ed.binding-section-summary-rows", hc_ed_binding_section_summary_rows)
    vm.register_host("ed.bind", hc_ed_bind)
    vm.register_host("ed.bind-mode", hc_ed_bind_mode)
    vm.register_host("ed.bind-doc", hc_ed_bind_doc)
    vm.register_host("ed.bind-mode-doc", hc_ed_bind_mode_doc)
    vm.register_host("ed.bind-prefix", hc_ed_bind_prefix)
    vm.register_host("ed.bind-mode-prefix", hc_ed_bind_mode_prefix)
    vm.register_host("ed.unbind", hc_ed_unbind)
    vm.register_host("ed.unbind-mode", hc_ed_unbind_mode)
    vm.register_host("ed.bindings", hc_ed_bindings)
    vm.register_host("ed.binding-detail", hc_ed_binding_detail)
    vm.register_host("ed.binding-detail-row", hc_ed_binding_detail_row)
    vm.register_host("ed.binding-modes", hc_ed_binding_modes)
    vm.register_host("ed.binding-rows-for", hc_ed_binding_rows_for)
    vm.register_host("ed.binding-info-for", hc_ed_binding_info_for)
    vm.register_host("ed.available-bindings", hc_ed_available_bindings)
    vm.register_host("ed.available-binding-info", hc_ed_available_binding_info)
    vm.register_host("ed.available-binding-inventory-rows", hc_ed_available_binding_inventory_rows)
    vm.register_host("ed.resolve-key", hc_ed_resolve_key)
    vm.register_host("ed.resolve-key-info", hc_ed_resolve_key_info)
    vm.register_host("ed.keymode!", hc_ed_keymode_store)
    vm.register_host("ed.keymode@", hc_ed_keymode_fetch)
    vm.register_host("ed.keymode-push", hc_ed_keymode_push)
    vm.register_host("ed.keymode-push-once", hc_ed_keymode_push_once)
    vm.register_host("ed.prefix-mode", hc_ed_prefix_mode)
    vm.register_host("ed.keymode-pop", hc_ed_keymode_pop)
    vm.register_host("ed.keymodes", hc_ed_keymodes)
    vm.register_host("ed.keymode-rows", hc_ed_keymode_rows)
    vm.register_host("ed.keymode-inventory-rows", hc_ed_keymode_inventory_rows)
    vm.register_host("ed.keymode-detail-row", hc_ed_keymode_detail_row)
    vm.register_host("ed.group!", hc_ed_group_store)
    vm.register_host("ed.group@", hc_ed_group_fetch)
    vm.register_host("ed.run", hc_ed_run)
    vm.register_host("ed.press-key", hc_ed_press_key)
    vm.register_host("ed.command", hc_ed_command)
    vm.register_host("ed.command-edit", hc_ed_command_edit)
    vm.register_host("ed.prompt-kind", hc_ed_prompt_kind)
    vm.register_host("ed.prompt-text", hc_ed_prompt_text)
    vm.register_host("ed.prompt-set", hc_ed_prompt_set)
    vm.register_host("ed.prompt-submit", hc_ed_prompt_submit)
    vm.register_host("ed.prompt-suggestions", hc_ed_prompt_suggestions)
    vm.register_host("ed.prompt-suggestion-rows", hc_ed_prompt_suggestion_rows)
    vm.register_host("ed.prompt-current-row", hc_ed_prompt_current_row)
    vm.register_host("ed.prompt-current-section", hc_ed_prompt_current_section)
    vm.register_host("ed.prompt-current-preview", hc_ed_prompt_current_preview)
    vm.register_host("ed.prompt-current-position", hc_ed_prompt_current_position)
    vm.register_host("ed.prompt-window", hc_ed_prompt_window)
    vm.register_host("ed.prompt-display", hc_ed_prompt_display)
    vm.register_host("ed.prompt-suggest-index", hc_ed_prompt_suggest_index)
    vm.register_host("ed.prompt-complete", hc_ed_prompt_complete)
    vm.register_host("ed.prompt-clear-suggestions", hc_ed_prompt_clear_suggestions)
    vm.register_host("ed.input-set", hc_ed_input_set)
    vm.register_host("ed.input-get", hc_ed_input_get)
    vm.register_host("ed.input-keys", hc_ed_input_keys)
    vm.register_host("ed.input-clear", hc_ed_input_clear)
    vm.register_host("ed.input", hc_ed_input)
    vm.register_host("ed.insert", hc_ed_insert)
    vm.register_host("ed.backspace", hc_ed_backspace)
    vm.register_host("ed.open", hc_ed_open)
    vm.register_host("ed.save", hc_ed_save)
    vm.register_host("ed.text", hc_ed_text)
    vm.register_host("ed.set-text", hc_ed_set_text)
    vm.register_host("ed.line", hc_ed_line)
    vm.register_host("ed.lines", hc_ed_lines)
    vm.register_host("ed.highlight", hc_ed_highlight)
    vm.register_host("ed.highlight-tags", hc_ed_highlight_tags)
    vm.register_host("ed.after", hc_ed_after)
    vm.register_host("ed.cancel-timer", hc_ed_cancel_timer)
    vm.register_host("ed.pump-timers", hc_ed_pump_timers)
    vm.register_host("plugin.list", hc_plugin_list)
    vm.register_host("plugin.reload", hc_plugin_reload)
    vm.register_host("plugin.errors", hc_plugin_errors)
    vm.register_host("ed.viewport", hc_ed_viewport)
    vm.register_host("ed.viewport!", hc_ed_viewport_store)
    vm.register_host("ed.cursor", hc_ed_cursor)
    vm.register_host("ed.set-cursor", hc_ed_set_cursor)
    vm.register_host("ed.has-selection", hc_ed_has_selection)
    vm.register_host("ed.selection", hc_ed_selection_text)
    vm.register_host("ed.clear-selection", hc_ed_clear_selection)
    vm.register_host("ed.cursors", hc_ed_cursors)
    vm.register_host("ed.set-cursors", hc_ed_set_cursors)
    vm.register_host("ed.primary", hc_ed_primary)
    vm.register_host("ed.set-primary", hc_ed_set_primary)
    vm.register_host("ed.selections", hc_ed_selections)
    vm.register_host("ed.set-selections", hc_ed_set_selections)
    vm.register_host("ed.replace-selections", hc_ed_replace_selections)
    vm.register_host("ed.selection-range", hc_ed_selection_range)
    vm.register_host("ed.set-selection-range", hc_ed_set_selection_range)
    vm.register_host("ed.range-text", hc_ed_range_text)
    vm.register_host("ed.replace-range", hc_ed_replace_range)
    vm.register_host("ed.delete-range", hc_ed_delete_range)
    vm.register_host("ed.with-undo", hc_ed_with_undo)
    vm.register_host("ed.clipboard", hc_ed_clipboard)
    vm.register_host("ed.set-clipboard", hc_ed_set_clipboard)
    vm.register_host("ed.clipboard-items", hc_ed_clipboard_items)
    vm.register_host("ed.set-clipboard-items", hc_ed_set_clipboard_items)
    vm.register_host("ed.clipboard-import", hc_ed_clipboard_import)
    vm.register_host("ed.push-selections", hc_ed_push_selections)
    vm.register_host("ed.pop-selections", hc_ed_pop_selections)
    vm.register_host("ed.clear-saved-selections", hc_ed_clear_saved_selections)
    vm.register_host("ed.cursorstate", hc_ed_cursorstate)
    vm.register_host("ed.set-cursorstate", hc_ed_set_cursorstate)
    vm.register_host("ed.with-cursorstate", hc_ed_with_cursorstate)
    vm.register_host("ed.push-jump", hc_ed_push_jump)
    vm.register_host("ed.jump-back", hc_ed_jump_back)
    vm.register_host("ed.jump-forward", hc_ed_jump_forward)
    vm.register_host("ed.jump-info", hc_ed_jump_info)
    vm.register_host("ed.clear-jumps", hc_ed_clear_jumps)
    vm.register_host("ed.jump-history-rows", hc_ed_jump_history_rows)
    vm.register_host("ed.jump-detail-row", hc_ed_jump_detail_row)
    vm.register_host("ed.jump-section-rows", hc_ed_jump_section_rows)
    vm.register_host("ed.jump-section-summary-rows", hc_ed_jump_section_summary_rows)
    vm.register_host("ed.find", hc_ed_find)
    vm.register_host("ed.find-next", hc_ed_find_next)
    vm.register_host("ed.find-prev", hc_ed_find_prev)
    vm.register_host("ed.option-inventory-rows", hc_ed_option_inventory_rows)
    vm.register_host("ed.option-section-summary-rows", hc_ed_option_section_summary_rows)
    vm.register_host("ed.option-detail-row", hc_ed_option_detail_row)
    vm.register_host("ed.opt-get", hc_ed_opt_get)
    vm.register_host("ed.opt-set", hc_ed_opt_set)
    vm.register_host("ed.opt-set-local", hc_ed_opt_set_local)
    vm.register_host("ed.require", hc_ed_require)


    # ----- option helpers (micromax-friendly) -----
    #
    # The editor already exposes hostcalls `ed.opt-get`/`ed.opt-set`, but it is
    # ergonomic to have immediate, command-like words in init/plugin scripts:
    #
    #   set cap.shell true
    #   toggle ignorecase
    #   show tabsize
    #
    # These parse the next token(s) directly, like `' name`.

    def _next_noncomment(vm: VM):
        t = vm.next_token()
        while getattr(t, 'kind', None) == 'comment':
            t = vm.next_token()
        return t

    def _tok_str(t) -> str:
        k = getattr(t, 'kind', '')
        v = getattr(t, 'value', '')
        if k == 'str':
            return str(v)
        if k == 'int':
            return str(int(v))
        if k == 'word':
            return str(v)
        if k == 'sym':
            return str(v)
        return str(v)

    def _opt_name(vm: VM) -> str:
        t = _next_noncomment(vm)
        if getattr(t, 'kind', None) == 'word':
            return str(t.value)
        if getattr(t, 'kind', None) == 'str':
            return str(t.value)
        raise MicromaxError('set/toggle/show: expected option name', span=getattr(t, 'span', None))

    def _push_opt_value(vm: VM, val: object) -> None:
        if isinstance(val, bool):
            vm.stack.append(1 if val else 0)
        else:
            vm.stack.append(val)

    def w_set_option(vm: VM) -> None:
        """( -- value ) Parse OPTION VALUE and set editor option."""
        name = _opt_name(vm)
        t = _next_noncomment(vm)
        raw = _tok_str(t)
        try:
            val = ed.options.set(name, raw)
        except Exception as e:
            raise MicromaxError(f"set: {e}", span=getattr(t, 'span', None))
        if str(ed.options.resolve_name(str(name))) == 'fastdirty':
            try:
                ed._sync_all_buffer_fastdirty_modes()
            except Exception:
                pass
        if str(name).startswith('cap.'):
            try:
                ed.refresh_capabilities()
            except Exception:
                pass
        _push_opt_value(vm, val)

    def w_show_option(vm: VM) -> None:
        """( -- value ) Parse OPTION and push its current value."""
        name = _opt_name(vm)
        try:
            val = ed.options.get(name, local=ed.cur().local_options)
        except Exception as e:
            raise MicromaxError(f"show: {e}")
        _push_opt_value(vm, val)

    def w_toggle_option(vm: VM) -> None:
        """( -- value ) Parse OPTION and toggle it (bool only)."""
        name = _opt_name(vm)
        try:
            val = ed.options.toggle(name)
        except Exception as e:
            raise MicromaxError(f"toggle: {e}")
        if str(ed.options.resolve_name(str(name))) == 'fastdirty':
            try:
                ed._sync_all_buffer_fastdirty_modes()
            except Exception:
                pass
        if str(name).startswith('cap.'):
            try:
                ed.refresh_capabilities()
            except Exception:
                pass
        _push_opt_value(vm, val)

    # Install these in the default wordlist so init.mx can use them.
    vm.define_primitive('set', w_set_option, doc='( -- value ) parse option name + value; set editor option')
    vm.define_primitive('show', w_show_option, doc='( -- value ) parse option name; push value')
    vm.define_primitive('toggle', w_toggle_option, doc='( -- value ) parse option name; toggle bool option')

    # Stack-oriented synonyms for scripts that prefer explicitness.
    try:
        vm.eval(
            """
            : opt@   ( "name" -- value )  "ed.opt-get" hostcall ;
            : opt!   ( "name" "raw" -- value )  "ed.opt-set" hostcall ;
            """,
            filename='<editor-options>',
        )
    except Exception:
        pass
