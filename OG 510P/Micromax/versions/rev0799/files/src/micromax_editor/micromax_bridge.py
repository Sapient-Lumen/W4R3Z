from __future__ import annotations

import shlex
import subprocess
from contextlib import ExitStack

from pathlib import Path

from micromax import VM
from micromax.vm import MicromaxError
from micromax.host_strings import install_string_hostcalls
from micromax.host_regex import install_regex_hostcalls

from .editor import Editor, MacroStep
from .buffer import Cursor
from .capabilities import capability_rows
from .edit_boundary import require_editable_buffer, set_buffer_text_undoably
from .file_hostcalls import install_file_recovery_hostcalls
from .file_recovery import read_file_for_editor
from .file_scriptops import checked_sandbox_path, fs_cap_root, save_current_buffer_under_caps
from .fs_hostcalls import fs_list_dir, fs_read_text, fs_stat_path
from .hostcall_boundary import (
    peek_int_arg,
    peek_list_arg,
    peek_quote_arg,
    peek_stack_arg,
    peek_str_arg,
    peek_xt_arg,
    pop_int_arg,
    pop_list_arg,
    pop_quote_arg,
    pop_str_arg,
    pop_xt_arg,
    require_option_enabled,
)
from .hostcall_transactions import (
    capture_cursor_state,
    capture_messages,
    capture_vm_stack,
    restore_cursor_state,
    restore_messages,
    restore_vm_stack_snapshot,
)
from .vm_load_policy import install_editor_vm_load_policy


def install_editor_hostcalls(ed: Editor) -> None:
    """Register a minimal set of hostcalls for editor scripting."""

    vm: VM = ed.vm
    vm.editor_owner = ed
    install_editor_vm_load_policy(ed)

    def _pop_two_int_args(vm: VM, word: str) -> tuple[int, int]:
        """Pop two integer operands after checking both are well-typed.

        The VM's legacy ``pop_int`` consumes before type-checking.  Bridge
        hostcalls should keep malformed operation operands available for
        diagnostics/recovery, so multi-operand readers preflight the whole
        operand group before deleting anything from the stack.
        """

        first = peek_int_arg(vm, word, depth=2)
        second = peek_int_arg(vm, word, depth=1)
        del vm.stack[-2:]
        return int(first), int(second)

    def _pop_four_int_args(vm: VM, word: str) -> tuple[int, int, int, int]:
        """Pop four integer operands after checking the full operand group."""

        first = peek_int_arg(vm, word, depth=4)
        second = peek_int_arg(vm, word, depth=3)
        third = peek_int_arg(vm, word, depth=2)
        fourth = peek_int_arg(vm, word, depth=1)
        del vm.stack[-4:]
        return int(first), int(second), int(third), int(fourth)

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
    vm.host_features.add("ed.macro-detail-row")
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
    vm.host_features.add("ed.replace-preview")
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
    install_file_recovery_hostcalls(ed)

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
            : macro-detail    ( name -- row|0 )     "ed.macro-detail-row" hostcall ;
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
            : disk-state      ( -- m ) "ed.disk-state" hostcall ;
            : disk-states     ( include-all -- rows ) "ed.disk-states" hostcall ;
            : diskdiff-lines  ( max-lines -- ok lines err ) "ed.diff" hostcall ;
            : revert-buffer   ( force -- ok info err ) "ed.revert" hostcall ;
            : save-buffer     ( force -- ok info err ) "ed.save-info" hostcall ;
            : save-buffer-as  ( path force -- ok info err ) "ed.save-as-info" hostcall ;

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
        s = pop_str_arg(vm, "ed.msg")
        ed.message(s)

    def hc_ed_messages(vm: VM) -> None:
        """( -- msgs ) Return current message list as ["...", ...]."""
        vm.stack.append([str(x) for x in ed.messages])

    def hc_ed_last_message(vm: VM) -> None:
        """( -- s ) Return last message (or "")."""
        vm.stack.append(str(ed.messages[-1]) if ed.messages else "")

    def hc_ed_pop_message(vm: VM) -> None:
        """( -- s ) Pop oldest message (or "")."""
        vm.stack.append(str(ed.pop_message()))

    def hc_ed_clear_messages(vm: VM) -> None:
        """( -- ) Clear messages."""
        ed.clear_messages()

    # ----- capability registry + optional unsafe surfaces -----
    def hc_host_capabilities(vm: VM) -> None:
        """( -- rows ) Return capability registry rows.

        Rows are: [feature option kind enabled doc]
        """

        vm.stack.append(capability_rows(ed))

    def hc_ed_prompt_panel(vm: VM) -> None:
        """( lines cols -- m ) Return the shared visible picker-panel model."""

        lines, cols = _pop_two_int_args(vm, "ed.prompt-panel")
        vm.stack.append(ed.prompt_panel_model(lines=lines, cols=cols))

    def hc_ed_screen_layout(vm: VM) -> None:
        """( lines cols -- m ) Return the tiny shared curses screen-layout model."""

        lines, cols = _pop_two_int_args(vm, "ed.screen-layout")
        vm.stack.append(ed.screen_layout_model(lines=lines, cols=cols))

    def hc_ed_gutter_model(vm: VM) -> None:
        """( lines cols -- m ) Return the shared visible gutter model."""

        lines, cols = _pop_two_int_args(vm, "ed.gutter-model")
        vm.stack.append(ed.gutter_model(lines=lines, cols=cols))

    def hc_ed_edit_window(vm: VM) -> None:
        """( lines cols -- m ) Return the shared reference visible edit-window model."""

        lines, cols = _pop_two_int_args(vm, "ed.edit-window")
        vm.stack.append(ed.edit_window_model(lines=lines, cols=cols))

    def hc_ed_search_rows(vm: VM) -> None:
        """( lines cols -- m ) Return the shared visible search-row model."""

        lines, cols = _pop_two_int_args(vm, "ed.search-rows")
        vm.stack.append(ed.search_rows_model(lines=lines, cols=cols))

    def hc_ed_showchars_rows(vm: VM) -> None:
        """( lines cols -- m ) Return the shared visible showchars-row model."""

        lines, cols = _pop_two_int_args(vm, "ed.showchars-rows")
        vm.stack.append(ed.showchars_rows_model(lines=lines, cols=cols))

    def hc_ed_display_rows(vm: VM) -> None:
        """( lines cols -- m ) Return the shared display-text screen rows."""

        lines, cols = _pop_two_int_args(vm, "ed.display-rows")
        vm.stack.append(ed.display_rows_model(lines=lines, cols=cols))

    def hc_ed_docs_cues(vm: VM) -> None:
        """( lines cols -- m ) Return the shared visible docs/help-cue model."""

        lines, cols = _pop_two_int_args(vm, "ed.docs-cues")
        vm.stack.append(ed.docs_cues_model(lines=lines, cols=cols))

    def hc_ed_viewport_cues(vm: VM) -> None:
        """( lines cols -- m ) Return the shared visible viewport-cue model."""

        lines, cols = _pop_two_int_args(vm, "ed.viewport-cues")
        vm.stack.append(ed.viewport_cues_model(lines=lines, cols=cols))

    def hc_ed_viewport_rows(vm: VM) -> None:
        """( lines cols -- m ) Return the shared visible viewport-row model."""

        lines, cols = _pop_two_int_args(vm, "ed.viewport-rows")
        vm.stack.append(ed.viewport_rows_model(lines=lines, cols=cols))

    def hc_ed_screen_model(vm: VM) -> None:
        """( lines cols -- m ) Return the shared visible-screen model."""

        lines, cols = _pop_two_int_args(vm, "ed.screen-model")
        vm.stack.append(ed.screen_model(lines=lines, cols=cols))

    def hc_ed_screen_rows(vm: VM) -> None:
        """( lines cols -- m ) Return the shared plain-text screen rows."""

        lines, cols = _pop_two_int_args(vm, "ed.screen-rows")
        vm.stack.append(ed.screen_rows_model(lines=lines, cols=cols))

    def hc_ed_open_url(vm: VM) -> None:
        """( url -- ok ) Open an external URL (capability-gated)."""

        require_option_enabled(
            ed,
            "cap.open-url",
            "ed.open-url disabled (set cap.open-url true)",
            error_cls=MicromaxError,
        )
        url = pop_str_arg(vm, "ed.open-url")
        ok = ed.open_url(url)
        vm.stack.append(1 if ok else 0)

    def hc_ed_shell(vm: VM) -> None:
        """( cmd -- code out err ) Run a shell command (capability-gated).

        This is intentionally simple and best-effort. Hosts that want a real
        job system should provide an alternative surface.
        """

        require_option_enabled(
            ed,
            "cap.shell",
            "ed.shell disabled (set cap.shell true)",
            error_cls=MicromaxError,
        )
        cmd = pop_str_arg(vm, "ed.shell")
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

        require_option_enabled(
            ed,
            "cap.fs-read",
            "ed.fs-read disabled (set cap.fs-read true)",
            error_cls=MicromaxError,
        )
        path = pop_str_arg(vm, "ed.fs-read")
        result = fs_read_text(ed, str(path))
        vm.stack.append(1 if result.ok else 0)
        vm.stack.append(str(result.text))
        vm.stack.append(str(result.err))


    def hc_ed_fs_list(vm: VM) -> None:
        """( path -- ok rows err ) List directory entries (capability-gated).

        Rows are: [[name kind path] ...] where kind is "dir"|"file"|"other".
        """

        require_option_enabled(
            ed,
            "cap.fs-list",
            "ed.fs-list disabled (set cap.fs-list true)",
            error_cls=MicromaxError,
        )
        path = pop_str_arg(vm, "ed.fs-list")
        result = fs_list_dir(ed, str(path))
        vm.stack.append(1 if result.ok else 0)
        vm.stack.append(list(result.rows))
        vm.stack.append(str(result.err))


    def hc_ed_fs_stat(vm: VM) -> None:
        """( path -- ok info err ) Stat a path (capability-gated).

        Info is a small portable map:
          {"path": str, "exists": 0|1, "kind": "file"|"dir"|"other", "size": int, "mtime": int}
        """

        require_option_enabled(
            ed,
            "cap.fs-stat",
            "ed.fs-stat disabled (set cap.fs-stat true)",
            error_cls=MicromaxError,
        )
        path = pop_str_arg(vm, "ed.fs-stat")
        result = fs_stat_path(ed, str(path))
        vm.stack.append(1 if result.ok else 0)
        vm.stack.append(dict(result.info))
        vm.stack.append(str(result.err))


    def hc_ed_buffers(vm: VM) -> None:
        """( -- names ) Return open buffer names."""
        vm.stack.append(ed.buffer_names())

    def hc_ed_buffer_inventory_rows(vm: VM) -> None:
        """( -- rows ) Tiny inspectable buffer inventory rows as [name position active dirty readonly]."""
        vm.stack.append(ed.buffer_inventory_rows())

    def hc_ed_buffer_detail_row(vm: VM) -> None:
        """( name -- row|0 ) Tiny inspectable exact buffer-detail row as [name position active dirty readonly section path line_count]."""
        name = pop_str_arg(vm, "ed.buffer-detail-row")
        row = ed.buffer_detail_row(name)
        vm.stack.append(0 if row is None else row)

    def hc_ed_buffer_section_rows(vm: VM) -> None:
        """( query -- sections ) Grouped buffer rows by visible picker section."""
        query = pop_str_arg(vm, "ed.buffer-section-rows")
        vm.stack.append(ed.buffer_section_rows(query))

    def hc_ed_buffer_section_summary_rows(vm: VM) -> None:
        """( query -- rows ) Tiny count-aware broad buffer-section rows."""
        query = pop_str_arg(vm, "ed.buffer-section-summary-rows")
        vm.stack.append(ed.buffer_section_summary_rows(query))

    def hc_ed_active_buffer(vm: VM) -> None:
        """( -- "name" ) Return active buffer name (or "")."""
        vm.stack.append(str(ed.active or ""))

    def hc_ed_set_active_buffer(vm: VM) -> None:
        """( "name" -- ok ) Switch active buffer if it exists."""
        name = pop_str_arg(vm, "ed.set-active-buffer")
        ok = ed.switch_buffer(name)
        vm.stack.append(1 if ok else 0)

    def hc_ed_mark_set(vm: VM) -> None:
        """( "name" -- ok ) Set a named mark at the primary cursor."""
        name = peek_str_arg(vm, "ed.mark-set")
        ok = ed.mark_set(name)
        del vm.stack[-1:]
        vm.stack.append(1 if ok else 0)

    def hc_ed_mark_jump(vm: VM) -> None:
        """( "name" -- ok ) Jump to a named mark."""
        name = pop_str_arg(vm, "ed.mark-jump")
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
        name = pop_str_arg(vm, "ed.mark-detail-row")
        row = ed.mark_detail_row(name)
        vm.stack.append(0 if row is None else row)

    def hc_ed_mark_section_rows(vm: VM) -> None:
        """( query -- sections ) Grouped mark rows by owning buffer."""
        query = pop_str_arg(vm, "ed.mark-section-rows")
        vm.stack.append(ed.mark_section_rows(query))

    def hc_ed_mark_section_summary_rows(vm: VM) -> None:
        """( query -- rows ) Tiny count-aware broad mark-section rows."""
        query = pop_str_arg(vm, "ed.mark-section-summary-rows")
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

        template = pop_str_arg(vm, "ed.statusfmt")
        st = ed.status_model()
        vm.stack.append(render_status_template(template, ed=ed, status=st))

    def hc_ed_statusline_text(vm: VM) -> None:
        """( width -- s ) Render the full statusline string for a given width."""
        width = pop_int_arg(vm, "ed.statusline-text")
        vm.stack.append(ed.statusline_text(int(width)))

    def hc_ed_statusline_model(vm: VM) -> None:
        """( width -- m ) Return the shared statusline layout model for one width."""
        width = pop_int_arg(vm, "ed.statusline-model")
        vm.stack.append(ed.statusline_model(int(width)))

    def hc_ed_interaction_model(vm: VM) -> None:
        """( width -- m ) Return the shared prompt/capture row model for one width."""
        width = pop_int_arg(vm, "ed.interaction-model")
        vm.stack.append(ed.interaction_model(int(width)))

    def hc_ed_keymenu_model(vm: VM) -> None:
        """( width -- m ) Return the shared keymenu row model for one width."""
        width = pop_int_arg(vm, "ed.keymenu-model")
        vm.stack.append(ed.keymenu_model(int(width)))

    def hc_ed_infobar_model(vm: VM) -> None:
        """( width -- m ) Return the shared idle infobar row model for one width."""
        width = pop_int_arg(vm, "ed.infobar-model")
        vm.stack.append(ed.infobar_model(int(width)))

    def hc_ed_bottom_rows(vm: VM) -> None:
        """( width -- rows ) Return the visible bottom-row chrome as row maps."""
        width = pop_int_arg(vm, "ed.bottom-rows")
        vm.stack.append(ed.bottom_rows_model(int(width)))

    def hc_ed_with_buffer(vm: VM) -> None:
        """( name q -- ok ) Switch to buffer name for duration of quotation, then restore."""
        q = peek_quote_arg(vm, "ed.with-buffer", depth=1)
        name = peek_str_arg(vm, "ed.with-buffer", depth=2)
        del vm.stack[-2:]
        stack_snapshot = capture_vm_stack(vm)
        old = str(ed.active or "")
        if name and not ed.switch_buffer(str(name)):
            vm.stack.append(0)
            return
        try:
            try:
                vm.exec_xt(q)
            except Exception:
                restore_vm_stack_snapshot(vm, stack_snapshot)
                raise
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
        q = peek_quote_arg(vm, "ed.with-viewport")
        del vm.stack[-1:]
        stack_snapshot = capture_vm_stack(vm)
        saved = dict(ed.viewport_model())
        try:
            try:
                vm.exec_xt(q)
            except Exception:
                restore_vm_stack_snapshot(vm, stack_snapshot)
                raise
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
        row = ed.plugin_detail_row(pop_str_arg(vm, "ed.plugin-detail-row"))
        vm.stack.append(row if row is not None else 0)

    def hc_ed_plugin_section_rows(vm: VM) -> None:
        """( query -- sections ) Grouped plugin rows by visible picker section."""
        query = pop_str_arg(vm, "ed.plugin-section-rows")
        vm.stack.append(ed.plugin_section_rows(query))

    def hc_ed_plugin_section_summary_rows(vm: VM) -> None:
        """( query -- rows ) Tiny count-aware plugin-section rows."""
        query = pop_str_arg(vm, "ed.plugin-section-summary-rows")
        vm.stack.append(ed.plugin_section_summary_rows(query))

    def hc_ed_recent(vm: VM) -> None:
        """( -- xs ) Return recent file paths as a list of strings (MRU order)."""
        xs = getattr(ed, 'recent_files', [])
        vm.stack.append([str(x) for x in list(xs)])

    def _safe_clear_recent_files() -> int:
        # Do not bypass the editor's recent-file authority guard here.  Earlier
        # compatibility fallback code would clear the list after broad failures;
        # destructive MRU mutation must go through Editor.clear_recent_files().
        return int(ed.clear_recent_files())

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
        row = ed.recent_detail_row(pop_str_arg(vm, "ed.recent-detail-row"))
        vm.stack.append(row if row is not None else 0)

    def hc_ed_recent_slot_detail_row(vm: VM) -> None:
        """( n|"#n" -- row|0 ) Tiny inspectable exact recent-file row addressed by visible 1-based MRU slot."""
        try:
            value = peek_stack_arg(vm, "ed.recent-slot-detail-row")
            del vm.stack[-1:]
            row = ed.recent_detail_row_by_index(value)
        except Exception:
            row = None
        vm.stack.append(row if row is not None else 0)

    def hc_ed_recent_dir_detail_row(vm: VM) -> None:
        """( dir -- row|0 ) Tiny inspectable exact recent-directory row as [query directory count active_count open_count dirty_count readonly_count sample_path sample_detail]."""
        row = ed.recent_dir_detail_row(pop_str_arg(vm, "ed.recent-dir-detail-row"))
        vm.stack.append(row if row is not None else 0)

    def hc_ed_recent_slot_dir_detail_row(vm: VM) -> None:
        """( n|"#n" -- row|0 ) Tiny inspectable exact recent-directory row addressed by visible 1-based MRU slot."""
        try:
            value = peek_stack_arg(vm, "ed.recent-slot-dir-detail-row")
            del vm.stack[-1:]
            row = ed.recent_dir_detail_row_by_index(value)
        except Exception:
            row = None
        vm.stack.append(row if row is not None else 0)

    def hc_ed_recent_section_rows(vm: VM) -> None:
        """( query -- sections ) Grouped recent-file rows by project root."""
        query = pop_str_arg(vm, "ed.recent-section-rows")
        try:
            vm.stack.append(ed.recent_section_rows_by_project(query))
        except Exception:
            vm.stack.append([])

    def hc_ed_recent_section_summary_rows(vm: VM) -> None:
        """( query -- rows ) Tiny count-aware recent-file section rows by project root."""
        query = pop_str_arg(vm, "ed.recent-section-summary-rows")
        try:
            vm.stack.append(ed.recent_section_summary_rows(query))
        except Exception:
            vm.stack.append([])

    def hc_ed_recent_dir_section_rows(vm: VM) -> None:
        """( query -- sections ) Grouped recent-file rows by directory."""
        query = pop_str_arg(vm, "ed.recent-dir-section-rows")
        try:
            vm.stack.append(ed.recent_section_rows_by_dir(query))
        except Exception:
            vm.stack.append([])

    def hc_ed_recent_dir_section_summary_rows(vm: VM) -> None:
        """( query -- rows ) Tiny count-aware recent-file section rows by directory."""
        query = pop_str_arg(vm, "ed.recent-dir-section-summary-rows")
        try:
            vm.stack.append(ed.recent_dir_section_summary_rows(query))
        except Exception:
            vm.stack.append([])

    def hc_ed_recent_prompt_rows(vm: VM) -> None:
        """( query -- rows ) Return visible recentpick rows as [[path kind menu info] ...]."""
        query = pop_str_arg(vm, "ed.recent-prompt-rows")
        try:
            vm.stack.append(ed._recent_prompt_rows(query))
        except Exception:
            vm.stack.append([])

    def hc_ed_recent_dir_prompt_rows(vm: VM) -> None:
        """( query -- rows ) Return visible recentdirpick rows as [[path kind menu info] ...]."""
        query = pop_str_arg(vm, "ed.recent-dir-prompt-rows")
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
        query = pop_str_arg(vm, "ed.doc-section-rows")
        try:
            vm.stack.append(ed.doc_section_rows(query))
        except Exception:
            vm.stack.append([])

    def hc_ed_doc_section_summary_rows(vm: VM) -> None:
        """( query -- rows ) Tiny count-aware docs-section summaries."""
        query = pop_str_arg(vm, "ed.doc-section-summary-rows")
        try:
            vm.stack.append(ed.doc_section_summary_rows(query))
        except Exception:
            vm.stack.append([])

    def hc_ed_help_doc(vm: VM) -> None:
        """( topic -- ok ) Open a docs page into a protected help buffer."""
        topic = pop_str_arg(vm, "ed.help-doc")
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
        query = pop_str_arg(vm, "ed.help-link-rows")
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
        query = pop_str_arg(vm, "ed.helplink-section-rows")
        try:
            vm.stack.append(ed.help_link_section_rows(query))
        except Exception:
            vm.stack.append([])

    def hc_ed_help_outline_rows(vm: VM) -> None:
        """( query -- rows ) Markdown headings in the current docs buffer as rows."""
        query = pop_str_arg(vm, "ed.help-outline-rows")
        try:
            vm.stack.append(ed.help_outline_rows(query))
        except Exception:
            vm.stack.append([])

    def hc_ed_help_outline_section_rows(vm: VM) -> None:
        """( query -- sections ) Grouped outline rows for the current docs buffer."""
        query = pop_str_arg(vm, "ed.help-outline-section-rows")
        try:
            vm.stack.append(ed.help_outline_section_rows(query))
        except Exception:
            vm.stack.append([])

    def hc_ed_helpnav_section_rows(vm: VM) -> None:
        """( query -- sections ) Grouped headings + links for the current docs buffer."""
        query = pop_str_arg(vm, "ed.helpnav-section-rows")
        try:
            vm.stack.append(ed.help_nav_section_rows(query))
        except Exception:
            vm.stack.append([])


    def hc_ed_helpnav_section_summary_rows(vm: VM) -> None:
        """( query -- rows ) Tiny current-doc help-nav summaries as [[label count sample_name sample_detail] ...]."""
        query = pop_str_arg(vm, "ed.helpnav-section-summary-rows")
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

        q = peek_quote_arg(vm, "ed.with-messages")
        del vm.stack[-1:]
        stack_snapshot = capture_vm_stack(vm)
        saved = capture_messages(ed)
        try:
            try:
                vm.exec_xt(q)
            except Exception:
                restore_vm_stack_snapshot(vm, stack_snapshot)
                raise
        finally:
            restore_messages(ed, saved)
        vm.stack.append(1)

    def hc_ed_capture_messages(vm: VM) -> None:
        """( q -- msgs ok ) Run quotation, returning messages it emitted.

        The editor's message log is cleared for the duration of the call.
        After running, the previous message log is restored.
        """

        q = peek_quote_arg(vm, "ed.capture-messages")
        del vm.stack[-1:]
        stack_snapshot = capture_vm_stack(vm)
        saved = capture_messages(ed)
        ed.messages[:] = []
        if hasattr(ed, "message_authority"):
            ed.message_authority[:] = []
        try:
            try:
                vm.exec_xt(q)
                captured = [str(x) for x in ed.messages]
            except Exception:
                restore_vm_stack_snapshot(vm, stack_snapshot)
                raise
        finally:
            restore_messages(ed, saved)
        vm.stack.append(captured)
        vm.stack.append(1)

    def _binding_origin_kwargs() -> dict[str, object]:
        return ed.script_callback_origin_kwargs()

    def hc_ed_bind(vm: VM) -> None:
        """( key action-spec -- ) Bind a global key with best-effort provenance."""
        action_spec = peek_str_arg(vm, "ed.bind", depth=1)
        key = peek_str_arg(vm, "ed.bind", depth=2)
        sp = getattr(vm, 'last_span', None)
        group = getattr(vm, 'current_editor_group', None)
        ed.bind_key_checked(
            key,
            action_spec,
            span=sp,
            group=group,
            **_binding_origin_kwargs(),
        )
        del vm.stack[-2:]

    def hc_ed_bind_mode(vm: VM) -> None:
        """( mode key action-spec -- ) Bind a key in a named keymap mode."""
        action_spec = peek_str_arg(vm, "ed.bind-mode", depth=1)
        key = peek_str_arg(vm, "ed.bind-mode", depth=2)
        mode = peek_str_arg(vm, "ed.bind-mode", depth=3)
        sp = getattr(vm, 'last_span', None)
        group = getattr(vm, 'current_editor_group', None)
        ed.bind_key_checked(
            key,
            action_spec,
            span=sp,
            group=group,
            mode=mode,
            **_binding_origin_kwargs(),
        )
        del vm.stack[-3:]

    def hc_ed_bind_doc(vm: VM) -> None:
        """( key doc -- ok ) Attach/replace a human description for a global binding."""
        doc = peek_str_arg(vm, "ed.bind-doc", depth=1)
        key = peek_str_arg(vm, "ed.bind-doc", depth=2)
        ok = ed.set_key_binding_desc_checked(key, doc)
        del vm.stack[-2:]
        vm.stack.append(1 if ok else 0)

    def hc_ed_bind_mode_doc(vm: VM) -> None:
        """( mode key doc -- ok ) Attach/replace a human description for a mode binding."""
        doc = peek_str_arg(vm, "ed.bind-mode-doc", depth=1)
        key = peek_str_arg(vm, "ed.bind-mode-doc", depth=2)
        mode = peek_str_arg(vm, "ed.bind-mode-doc", depth=3)
        ok = ed.set_key_binding_desc_checked(key, doc, mode=mode)
        del vm.stack[-3:]
        vm.stack.append(1 if ok else 0)

    def hc_ed_bind_prefix(vm: VM) -> None:
        """( key mode doc|0 -- ok ) Bind a global prefix key that enters a one-shot mode.

        The resulting binding is just a normal keymap entry with action-spec
        `command:prefixmode MODE`, so it remains inspectable and portable. If
        doc is 0/empty, a small default description is used.
        """

        doc = peek_stack_arg(vm, "ed.bind-prefix", depth=1)
        mode = peek_str_arg(vm, "ed.bind-prefix", depth=2)
        key = peek_str_arg(vm, "ed.bind-prefix", depth=3)
        spec = f"command:prefixmode {shlex.quote(mode)}"
        sp = getattr(vm, 'last_span', None)
        group = getattr(vm, 'current_editor_group', None)
        desc = str(doc).strip() if doc not in (0, None) else ''
        ed.bind_key_checked(
            key,
            spec,
            span=sp,
            group=group,
            desc=desc or f"prefix {mode}",
            **_binding_origin_kwargs(),
        )
        del vm.stack[-3:]
        vm.stack.append(1)

    def hc_ed_bind_mode_prefix(vm: VM) -> None:
        """( owner-mode key mode doc|0 -- ok ) Bind a mode-local prefix key.

        This is the mode-local sibling of `ed.bind-prefix`: it still stores a
        normal binding whose action-spec is `command:prefixmode MODE`, but the
        binding itself lives in OWNER-MODE.
        """

        doc = peek_stack_arg(vm, "ed.bind-mode-prefix", depth=1)
        mode = peek_str_arg(vm, "ed.bind-mode-prefix", depth=2)
        key = peek_str_arg(vm, "ed.bind-mode-prefix", depth=3)
        owner_mode = peek_str_arg(vm, "ed.bind-mode-prefix", depth=4)
        spec = f"command:prefixmode {shlex.quote(mode)}"
        sp = getattr(vm, 'last_span', None)
        group = getattr(vm, 'current_editor_group', None)
        desc = str(doc).strip() if doc not in (0, None) else ''
        ed.bind_key_checked(
            key,
            spec,
            span=sp,
            group=group,
            mode=owner_mode,
            desc=desc or f"prefix {mode}",
            **_binding_origin_kwargs(),
        )
        del vm.stack[-4:]
        vm.stack.append(1)

    def hc_ed_prefix_mode(vm: VM) -> None:
        """( mode -- ok ) Enter a one-shot prefix mode and show reachable bindings."""
        mode = peek_str_arg(vm, "ed.prefix-mode")
        if not mode or mode in ('global', 'none'):
            del vm.stack[-1:]
            vm.stack.append(0)
            return
        ed.push_key_mode(mode, once=True)
        del vm.stack[-1:]
        ed.exec_command_line('whichkey')
        vm.stack.append(1)

    def hc_ed_unbind(vm: VM) -> None:
        """( key -- ok ) Remove a global key binding."""
        key = peek_str_arg(vm, "ed.unbind")
        ok = ed.unbind_key_checked(key)
        del vm.stack[-1:]
        vm.stack.append(1 if ok else 0)

    def hc_ed_unbind_mode(vm: VM) -> None:
        """( mode key -- ok ) Remove a key binding from a named mode."""
        key = peek_str_arg(vm, "ed.unbind-mode", depth=1)
        mode = peek_str_arg(vm, "ed.unbind-mode", depth=2)
        ok = ed.unbind_key_checked(key, mode=mode)
        del vm.stack[-2:]
        vm.stack.append(1 if ok else 0)

    def hc_ed_bindings(vm: VM) -> None:
        """( -- rows ) Return [[key action-spec [file line col]|0] ...]."""
        vm.stack.append(ed.keymap.binding_rows())

    def hc_ed_binding_detail(vm: VM) -> None:
        """( -- rows ) Return [[key action group|0 [file line col]|0] ...]."""
        vm.stack.append(ed.keymap.binding_detail_rows())

    def hc_ed_binding_detail_row(vm: VM) -> None:
        """( key -- [mode key action desc|0 group|0 [file line col]|0] | 0 ) Return the tiny shared resolved-binding row behind ``showkey``."""
        vm.stack.append(ed.binding_detail_row(pop_str_arg(vm, "ed.binding-detail-row")))

    def hc_ed_binding_modes(vm: VM) -> None:
        """( -- rows ) Return [[mode key action group|0 [file line col]|0] ...]."""
        vm.stack.append(ed.keymap.binding_mode_rows())

    def hc_ed_binding_rows_for(vm: VM) -> None:
        """( mode|0 -- rows ) Return [[key action group|0 [file line col]|0] ...] for a mode."""
        mode = peek_stack_arg(vm, "ed.binding-rows-for")
        del vm.stack[-1:]
        vm.stack.append(ed.keymap.binding_detail_rows_for(None if mode == 0 else str(mode)))

    def hc_ed_binding_info_for(vm: VM) -> None:
        """( mode|0 -- rows ) Return [[key action desc|0 group|0 [file line col]|0] ...] for a mode."""
        mode = peek_stack_arg(vm, "ed.binding-info-for")
        del vm.stack[-1:]
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
        vm.stack.append(ed.keymap.resolved_binding_row(pop_str_arg(vm, "ed.resolve-key"), modes=ed.active_key_modes()))

    def hc_ed_resolve_key_info(vm: VM) -> None:
        """( key -- [mode key action desc|0 group|0 [file line col]|0] | 0 ) Resolve a key with description through active keymodes."""
        vm.stack.append(ed.resolve_key_info_row(pop_str_arg(vm, "ed.resolve-key-info")))

    def hc_ed_keymode_store(vm: VM) -> None:
        """( mode|0 -- ) Set the active key mode (global fallback remains)."""
        mode = peek_stack_arg(vm, "ed.keymode!")
        if mode == 0:
            ed.set_key_mode(None)
        else:
            ed.set_key_mode(str(mode))
        del vm.stack[-1:]

    def hc_ed_keymode_fetch(vm: VM) -> None:
        """( -- mode|0 ) Return the current active key mode, or 0."""
        vm.stack.append(ed.current_key_mode() or 0)

    def hc_ed_keymode_push(vm: VM) -> None:
        """( mode -- ) Push an active key mode onto the stack."""
        mode = peek_str_arg(vm, "ed.keymode-push")
        ed.push_key_mode(mode)
        del vm.stack[-1:]

    def hc_ed_keymode_push_once(vm: VM) -> None:
        """( mode -- ) Push a one-shot active key mode onto the stack."""
        mode = peek_str_arg(vm, "ed.keymode-push-once")
        ed.push_key_mode(mode, once=True)
        del vm.stack[-1:]

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
        row = ed.keymode_detail_row(pop_str_arg(vm, "ed.keymode-detail-row"))
        vm.stack.append(row if row is not None else 0)

    def hc_ed_group_store(vm: VM) -> None:
        """( group|0 -- ) Set default editor registration group."""
        group = peek_stack_arg(vm, "ed.group!")
        vm.current_editor_group = ed.set_runtime_group_value(
            group,
            current=getattr(vm, "current_editor_group", None),
            kind="editor",
        )
        del vm.stack[-1:]

    def hc_ed_group_fetch(vm: VM) -> None:
        """( -- group|0 ) Current default editor registration group."""
        vm.stack.append(str(vm.current_editor_group) if vm.current_editor_group else 0)

    def hc_ed_run(vm: VM) -> None:
        action_spec = peek_str_arg(vm, "ed.run")
        with ed.script_context():
            ok = ed.run_action_chain(action_spec)
        del vm.stack[-1:]
        vm.stack.append(1 if ok else 0)

    def hc_ed_press_key(vm: VM) -> None:
        """( key -- ok ) Resolve and execute a bound key through active keymodes."""
        key = peek_str_arg(vm, "ed.press-key")
        with ed.script_context():
            ok = ed.dispatch_key(key)
        del vm.stack[-1:]
        vm.stack.append(1 if ok else 0)

    def hc_ed_command(vm: VM) -> None:
        cmdline = peek_str_arg(vm, "ed.command")
        with ed.script_context():
            ok = ed.exec_command_line(cmdline)
        del vm.stack[-1:]
        vm.stack.append(1 if ok else 0)

    def hc_ed_command_edit(vm: VM) -> None:
        s = peek_str_arg(vm, "ed.command-edit")
        with ed.script_context():
            ed.enter_prompt("command", prefill=s)
        del vm.stack[-1:]

    def hc_ed_topic_prompt(vm: VM) -> None:
        s = peek_str_arg(vm, "ed.topic-prompt")
        with ed.script_context():
            ed.enter_topic_prompt(s)
        del vm.stack[-1:]

    def hc_ed_binding_prompt(vm: VM) -> None:
        s = peek_str_arg(vm, "ed.binding-prompt")
        with ed.script_context():
            ed.enter_binding_prompt(s)
        del vm.stack[-1:]


    # ----- micromax-defined command-bar commands -----
    def hc_ed_cmd_add(vm: VM) -> None:
        """( xt name doc -- ok ) Define or replace a command-bar command.

        The command's xt is executed with `( args -- ... )` where args is a list
        of strings (the command line arguments). If the xt leaves an int/bool on
        top of the stack, it is treated as an ok flag; otherwise ok defaults to 1.

        A best-effort source span is attached (via vm.last_span) so `help <cmd>`
        can show where the command was registered.
        """

        doc = peek_str_arg(vm, "ed.cmd-add", depth=1)
        name = peek_str_arg(vm, "ed.cmd-add", depth=2)
        xt = peek_xt_arg(vm, "ed.cmd-add", depth=3)
        sp = getattr(vm, 'last_span', None)
        group = getattr(vm, 'current_editor_group', None)
        try:
            origin = ed.script_callback_origin_kwargs()
        except Exception:
            origin = {}
        from_script = bool(origin.get("script_context", False))
        plugin_load_root = origin.get("plugin_load_root")
        plugin_generation = origin.get("plugin_generation")
        script_origin_id = origin.get("script_origin_id")

        def _run(ed2: Editor, args: list[str]) -> bool:
            depth = len(vm.stack)

            def _body() -> bool:
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

            try:
                if from_script:
                    return bool(
                        ed2.run_script_origin_callback(
                            _body,
                            plugin_load_root=plugin_load_root,
                            group=group,
                            plugin_generation=plugin_generation,
                            script_origin_id=script_origin_id,
                            rollback_on_false=True,
                        )
                    )
                return _body()
            except Exception as e:
                if isinstance(e, MicromaxError):
                    detail = vm.format_error(e)
                else:
                    detail = str(e)
                ed2.message(f'command {name}: error: {detail}')
                return False
            finally:
                del vm.stack[depth:]

        ed.register_command_checked(
            str(name),
            _run,
            doc=str(doc),
            span=sp,
            group=group,
            script_context=from_script,
            plugin_load_root=(str(plugin_load_root) if plugin_load_root else None),
            plugin_generation=(int(plugin_generation) if plugin_generation not in (None, "") else None),
            script_origin_id=(str(script_origin_id) if script_origin_id else None),
        )
        del vm.stack[-3:]
        vm.stack.append(1)

    def hc_ed_cmd_rm(vm: VM) -> None:
        """( name -- ok ) Remove a command-bar command by name."""
        name = peek_str_arg(vm, "ed.cmd-rm")
        ok = ed.remove_command_checked(str(name))
        del vm.stack[-1:]
        vm.stack.append(1 if ok else 0)

    def hc_ed_cmds(vm: VM) -> None:
        """( -- names ) List command names (including micromax-defined)."""
        vm.stack.append(ed.command_dispatcher.names())

    def hc_ed_cmd_rows(vm: VM) -> None:
        """( -- rows ) Return [[name doc group|0 [file line col]|0] ...]."""
        vm.stack.append(ed.command_dispatcher.command_rows())

    def hc_ed_command_detail_row(vm: VM) -> None:
        """( name -- row|0 ) Tiny inspectable command-detail row as [name doc group|0 [file line col]|0]."""
        name = pop_str_arg(vm, "ed.command-detail-row")
        row = ed.command_detail_row(name)
        vm.stack.append(0 if row is None else row)

    def hc_ed_action_detail_row(vm: VM) -> None:
        """( name -- row|0 ) Tiny inspectable action-detail row as [name doc [file line col]|0]."""
        name = pop_str_arg(vm, "ed.action-detail-row")
        row = ed.action_detail_row(name)
        vm.stack.append(0 if row is None else row)

    def hc_ed_word_detail_row(vm: VM) -> None:
        """( name -- row|0 ) Tiny inspectable visible-word detail row as [name kind effect wordlist doc [file line col]|0 source|0]."""
        name = pop_str_arg(vm, "ed.word-detail-row")
        row = ed.word_detail_row(name)
        vm.stack.append(0 if row is None else row)

    def hc_ed_doc_detail_row(vm: VM) -> None:
        """( topic -- row|0 ) Tiny inspectable docs-detail row as [topic title summary section path]."""
        name = pop_str_arg(vm, "ed.doc-detail-row")
        row = ed.doc_detail_row(name)
        vm.stack.append(0 if row is None else row)

    def hc_ed_topic_detail_row(vm: VM) -> None:
        """( name -- row|0 ) Tiny inspectable exact-topic row as [name kind detail_row]."""
        name = pop_str_arg(vm, "ed.topic-detail-row")
        row = ed.topic_detail_row(name)
        vm.stack.append(0 if row is None else row)

    def hc_ed_help_current_heading_detail_row(vm: VM) -> None:
        """( -- row|0 ) Tiny inspectable current docs-heading row as [topic title fragment level line col section]."""
        row = ed.current_help_heading_detail_row()
        vm.stack.append(0 if row is None else row)

    def hc_ed_help_heading_detail_row(vm: VM) -> None:
        """( query -- row|0 ) Tiny inspectable help-heading row as [topic title fragment level line col section]."""
        query = pop_str_arg(vm, "ed.help-heading-detail-row")
        row = ed.help_heading_detail_row(query)
        vm.stack.append(0 if row is None else row)

    def hc_ed_hook_detail_row(vm: VM) -> None:
        """( name -- row|0 ) Tiny inspectable exact hook row as [query name handler_count sample_handler|0 sample_detail|0 [file line col]|0]."""
        row = ed.hook_detail_row(pop_str_arg(vm, "ed.hook-detail-row"))
        vm.stack.append(0 if row is None else row)

    def hc_ed_hook_inventory_rows(vm: VM) -> None:
        """( name -- rows|0 ) Tiny inspectable hook-handler rows as [handler group|0 [file line col]|0]."""
        name = pop_str_arg(vm, "ed.hook-inventory-rows")
        rows = ed.hook_inventory_rows(name)
        vm.stack.append(0 if rows is None else rows)

    def hc_ed_hook_summary_rows(vm: VM) -> None:
        """( query -- rows ) Tiny inspectable hook summary rows as [name handler_count sample_handler|0 [file line col]|0]."""
        query = pop_str_arg(vm, "ed.hook-summary-rows")
        vm.stack.append(ed.hook_summary_rows(query))

    def hc_ed_command_palette(vm: VM) -> None:
        """( query -- ) Open the searchable command/action palette."""
        query = pop_str_arg(vm, "ed.command-palette")
        with ed.script_context():
            ed.enter_command_palette(query)

    def hc_ed_command_palette_rows(vm: VM) -> None:
        """( query -- rows ) Return [[name kind menu info] ...] for the command/action palette."""
        query = pop_str_arg(vm, "ed.command-palette-rows")
        vm.stack.append(ed.command_palette_apropos_rows(query))

    def hc_ed_command_palette_section_rows(vm: VM) -> None:
        """( query -- sections ) Return grouped palette rows as [[label [[name kind menu info] ...]] ...]."""
        query = pop_str_arg(vm, "ed.command-palette-section-rows")
        vm.stack.append(ed.command_palette_section_rows(query))

    def hc_ed_command_palette_section_summary_rows(vm: VM) -> None:
        """( query -- rows ) Tiny count-aware command-palette bucket summaries."""
        query = pop_str_arg(vm, "ed.command-palette-section-summary-rows")
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
        query = pop_str_arg(vm, "ed.apropos-rows")
        vm.stack.append(ed.apropos_rows(query))

    def hc_ed_apropos_section_rows(vm: VM) -> None:
        """( query -- sections ) Return grouped apropos rows as [[label [[name kind menu info] ...]] ...]."""
        query = pop_str_arg(vm, "ed.apropos-section-rows")
        vm.stack.append(ed.apropos_section_rows(query))

    def hc_ed_apropos_section_summary_rows(vm: VM) -> None:
        """( query -- rows ) Tiny count-aware apropos-section summaries."""
        query = pop_str_arg(vm, "ed.apropos-section-summary-rows")
        vm.stack.append(ed.apropos_section_summary_rows(query))

    def hc_ed_binding_prompt_rows(vm: VM) -> None:
        """( query -- rows ) Return [[key kind menu info] ...] for searchable current bindings."""
        query = pop_str_arg(vm, "ed.binding-prompt-rows")
        vm.stack.append(ed.binding_apropos_rows(query))

    def hc_ed_binding_section_rows(vm: VM) -> None:
        """( query -- sections ) Return grouped current-binding rows by winning mode."""
        query = pop_str_arg(vm, "ed.binding-section-rows")
        vm.stack.append(ed.binding_section_rows(query))

    def hc_ed_binding_section_summary_rows(vm: VM) -> None:
        """( query -- rows ) Tiny count-aware winning-mode binding summaries."""
        query = pop_str_arg(vm, "ed.binding-section-summary-rows")
        vm.stack.append(ed.binding_section_summary_rows(query))

    def hc_ed_prompt_kind(vm: VM) -> None:
        vm.stack.append(ed.prompt.kind if ed.prompt else "")

    def hc_ed_prompt_text(vm: VM) -> None:
        vm.stack.append(ed.prompt.text if ed.prompt else "")

    def hc_ed_prompt_set(vm: VM) -> None:
        s = pop_str_arg(vm, "ed.prompt-set")
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
        lines = pop_int_arg(vm, "ed.prompt-window")
        vm.stack.append(ed.prompt_window_model(max_lines=lines))

    def hc_ed_prompt_display(vm: VM) -> None:
        """( lines cols -- rows ) Return shared rendered prompt rows."""
        lines, width = _pop_two_int_args(vm, "ed.prompt-display")
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
        direction = pop_int_arg(vm, "ed.prompt-complete")
        with ed.script_context():
            ok = ed.prompt_complete(direction=direction)
        vm.stack.append(1 if ok else 0)

    def hc_ed_prompt_clear_suggestions(vm: VM) -> None:
        """( -- ok ) Clear the active prompt suggestion session."""
        with ed.script_context():
            ok = ed.clear_prompt_suggestions()
        vm.stack.append(1 if ok else 0)

    def hc_ed_input_set(vm: VM) -> None:
        """( key val -- ) Set an action/command input value."""
        key = peek_str_arg(vm, "ed.input-set", depth=2)
        val = peek_stack_arg(vm, "ed.input-set", depth=1)
        del vm.stack[-2:]
        ed.input[key] = val


    def hc_ed_input_get(vm: VM) -> None:
        """( key -- val|0 ) Get an action/command input value (or 0 if missing)."""
        key = pop_str_arg(vm, "ed.input-get")
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
        s = pop_str_arg(vm, "ed.insert")
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

        require_option_enabled(
            ed,
            "cap.fs-open",
            "ed.open disabled (set cap.fs-open true)",
            error_cls=MicromaxError,
        )
        path = pop_str_arg(vm, "ed.open")
        try:
            raw_path, initial_cursor = ed._parse_open_target(str(path))
            p = checked_sandbox_path(ed, raw_path)
            ok = bool(ed.open_file(str(p), initial_cursor=initial_cursor, containment_root=fs_cap_root(ed)))
            vm.stack.append(1 if ok else 0)
            vm.stack.append("")
        except Exception as e:
            vm.stack.append(0)
            vm.stack.append(str(e))

    def hc_ed_save(vm: VM) -> None:
        """( -- ok err ) Save the current buffer to disk (capability-gated).

        This legacy hostcall keeps its two-cell result shape.  Internally it
        now uses the same transactional, cap.fs-root-aware helper as the
        structured `ed.save-info` hostcall.
        """

        if not bool(ed.options.get("cap.fs-save")):
            raise MicromaxError("ed.save disabled (set cap.fs-save true)")

        try:
            save_current_buffer_under_caps(ed, force=False)
            vm.stack.append(1)
            vm.stack.append("")
        except Exception as e:
            vm.stack.append(0)
            vm.stack.append(str(e))

    def hc_ed_text(vm: VM) -> None:
        vm.stack.append(ed.cur().buf.get_text())

    def hc_ed_set_text(vm: VM) -> None:
        require_editable_buffer(ed, "ed.set-text", error_cls=MicromaxError)
        s = peek_str_arg(vm, "ed.set-text")
        del vm.stack[-1:]
        set_buffer_text_undoably(ed, s, description="SetText")

    def hc_ed_line(vm: VM) -> None:
        """( line -- s ) Get one buffer line (0-based; clamped)."""
        li = peek_int_arg(vm, "ed.line")
        del vm.stack[-1:]
        eb = ed.cur()
        if not eb.buf.lines:
            vm.stack.append("")
            return
        li2 = max(0, min(int(li), len(eb.buf.lines) - 1))
        vm.stack.append(str(eb.buf.lines[li2]))

    def hc_ed_lines(vm: VM) -> None:
        """( start count -- lines ) Get a range of lines as ["...", ...]."""
        start = peek_int_arg(vm, "ed.lines", depth=2)
        count = peek_int_arg(vm, "ed.lines", depth=1)
        del vm.stack[-2:]
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
        start = peek_int_arg(vm, "ed.highlight", depth=2)
        count = peek_int_arg(vm, "ed.highlight", depth=1)
        del vm.stack[-2:]
        vm.stack.append(ed.highlight_spans(int(start), int(count)))

    def hc_ed_highlight_tags(vm: VM) -> None:
        """( -- tags ) Return known highlight tag vocabulary."""
        vm.stack.append(ed.highlight_tags())

    # ----- timers -----
    def hc_ed_after(vm: VM) -> None:
        """( ms q -- id ) Schedule quotation to run after ms milliseconds."""
        q = peek_quote_arg(vm, "ed.after", depth=1)
        ms = peek_int_arg(vm, "ed.after", depth=2)
        group = getattr(vm, "current_editor_group", None)
        origin = ed.script_callback_origin_kwargs()
        del vm.stack[-2:]
        tid = ed.timers.schedule(
            now=ed.now(),
            delay_ms=int(ms),
            xt=q,
            group=group,
            script_context=bool(origin.get("script_context")),
            plugin_load_root=origin.get("plugin_load_root"),
            plugin_generation=origin.get("plugin_generation"),
            script_origin_id=origin.get("script_origin_id"),
        )
        vm.stack.append(int(tid))

    def hc_ed_cancel_timer(vm: VM) -> None:
        """( id -- ok ) Cancel a scheduled timer."""
        tid = peek_int_arg(vm, "ed.cancel-timer")
        ok = ed.cancel_timer_checked(int(tid))
        del vm.stack[-1:]
        vm.stack.append(1 if ok else 0)

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
        try:
            in_script = bool(ed.in_script_context())
        except Exception:
            in_script = False
        if in_script and not bool(ed.options.get("cap.fs-require")):
            ed.message("plugin reload: disabled for scripts (cap.fs-require)")
            vm.stack.append(0)
            return
        name = pop_str_arg(vm, "plugin.reload")
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
        top, left, height, width = _pop_four_int_args(vm, "ed.viewport!")
        ed.set_viewport(top_line=top, left_col=left, height=height, width=width, follow_cursor=True)

    def hc_ed_cursor(vm: VM) -> None:
        """( -- line col ) Primary cursor position (0-based)."""
        c = ed.primary_cursor()
        vm.stack.append(int(c.line))
        vm.stack.append(int(c.col))

    def hc_ed_set_cursor(vm: VM) -> None:
        """( line col -- ) Set primary cursor (0-based; clamped)."""
        line = peek_int_arg(vm, "ed.set-cursor", depth=2)
        col = peek_int_arg(vm, "ed.set-cursor", depth=1)
        del vm.stack[-2:]
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
        raw = peek_list_arg(vm, "ed.set-cursors")
        curs: list[Cursor] = []
        for it in raw:
            if not isinstance(it, list) or len(it) != 2:
                raise MicromaxError("ed.set-cursors: expected [[line col] ...]")
            try:
                line = int(it[0])
                col = int(it[1])
            except Exception as e:
                raise MicromaxError("ed.set-cursors: expected integer line/col entries") from e
            curs.append(Cursor(line, col))
        del vm.stack[-1:]
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
        i = peek_int_arg(vm, "ed.set-primary")
        del vm.stack[-1:]
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

        raw = peek_list_arg(vm, "ed.set-selections")
        eb = ed.cur()
        ed._normalize_cursor_lists(eb)
        if len(raw) != len(eb.cursors):
            raise MicromaxError("ed.set-selections: sels length must match cursor count")

        new_anchors: list[Cursor | None] = []
        new_cursors: list[Cursor] = []
        for i, it in enumerate(raw):
            if it == []:
                new_anchors.append(None)
                new_cursors.append(eb.cursors[i])
                continue
            if not isinstance(it, list) or len(it) != 4:
                raise MicromaxError("ed.set-selections: expected [] or [aL aC cL cC]")
            try:
                aL, aC, cL, cC = (int(it[0]), int(it[1]), int(it[2]), int(it[3]))
            except Exception as e:
                raise MicromaxError("ed.set-selections: expected integer selection entries") from e
            new_anchors.append(eb.buf.clamp(Cursor(aL, aC)))
            new_cursors.append(eb.buf.clamp(Cursor(cL, cC)))

        # Clearing the saved-selection recovery register is a destructive side
        # effect of this setter.  Preflight it before mutating cursor state so a
        # denied script-origin call leaves both cursor state and recovery stack
        # intact.
        ed.clear_saved_selections()

        del vm.stack[-1:]
        eb.sel_anchors[:] = new_anchors
        eb.cursors[:] = new_cursors
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

        line1 = peek_int_arg(vm, "ed.set-selection-range", depth=4)
        col1 = peek_int_arg(vm, "ed.set-selection-range", depth=3)
        line2 = peek_int_arg(vm, "ed.set-selection-range", depth=2)
        col2 = peek_int_arg(vm, "ed.set-selection-range", depth=1)
        del vm.stack[-4:]
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

        require_editable_buffer(ed, "ed.replace-selections", error_cls=MicromaxError)
        raw = peek_stack_arg(vm, "ed.replace-selections")
        if isinstance(raw, list):
            reps = [str(x) for x in raw]
        else:
            reps = [str(raw)]

        eb = ed.cur()
        ed._normalize_cursor_lists(eb)

        if len(reps) == len(eb.cursors):
            per = reps
        elif len(reps) == 1:
            per = reps * len(eb.cursors)
        else:
            raise MicromaxError("ed.replace-selections: replacements must be 1 or match cursor count")

        del vm.stack[-1:]
        before = ed._snapshot_buffer_state(eb)

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
        try:
            ed._note_buffer_changed(eb)
        except Exception:
            pass

        c = ed.primary_cursor()
        vm.stack.append(int(c.line))
        vm.stack.append(int(c.col))


    def hc_ed_range_text(vm: VM) -> None:
        """( line1 col1 line2 col2 -- "text" ) Get text in range (primary buffer)."""
        line1 = peek_int_arg(vm, "ed.range-text", depth=4)
        col1 = peek_int_arg(vm, "ed.range-text", depth=3)
        line2 = peek_int_arg(vm, "ed.range-text", depth=2)
        col2 = peek_int_arg(vm, "ed.range-text", depth=1)
        del vm.stack[-4:]
        eb = ed.cur()
        s = eb.buf.clamp(Cursor(line1, col1))
        e = eb.buf.clamp(Cursor(line2, col2))
        if (s.line, s.col) > (e.line, e.col):
            s, e = e, s
        vm.stack.append(eb.buf.get_range_text(s, e))

    def hc_ed_replace_preview(vm: VM) -> None:
        """( search value replace_all literal -- row ) Plan replace without mutating.

        The row shape is ``[ok count replace_all literal case_sensitive start_index error rows]``.
        Match rows are ``[line col end_line end_col old new]`` using zero-based
        editor coordinates.  Argument shape is preflighted before stack
        consumption so failed preview requests remain inspectable.
        """

        if len(vm.stack) < 4:
            raise MicromaxError("ed.replace-preview: expected search value replace_all literal")
        search, value, replace_all, literal = vm.stack[-4:]
        if not isinstance(search, str):
            raise MicromaxError(f"ed.replace-preview: expected search str, got {type(search).__name__}")
        if not isinstance(value, str):
            raise MicromaxError(f"ed.replace-preview: expected value str, got {type(value).__name__}")
        if not isinstance(replace_all, int):
            raise MicromaxError(
                f"ed.replace-preview: expected replace_all int, got {type(replace_all).__name__}"
            )
        if not isinstance(literal, int):
            raise MicromaxError(f"ed.replace-preview: expected literal int, got {type(literal).__name__}")
        del vm.stack[-4:]
        plan = ed.replace_plan(search, value, replace_all=bool(replace_all), literal=bool(literal))
        vm.stack.append(plan.summary_row())


    def hc_ed_replace_range(vm: VM) -> None:
        """( line1 col1 line2 col2 "text" -- line col ) Replace range with text (undoable)."""
        require_editable_buffer(ed, "ed.replace-range", error_cls=MicromaxError)
        text = peek_str_arg(vm, "ed.replace-range", depth=1)
        col2 = peek_int_arg(vm, "ed.replace-range", depth=2)
        line2 = peek_int_arg(vm, "ed.replace-range", depth=3)
        col1 = peek_int_arg(vm, "ed.replace-range", depth=4)
        line1 = peek_int_arg(vm, "ed.replace-range", depth=5)
        del vm.stack[-5:]
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
        try:
            ed._note_buffer_changed(eb)
        except Exception:
            pass
        c = ed.primary_cursor()
        vm.stack.append(int(c.line))
        vm.stack.append(int(c.col))

    def hc_ed_delete_range(vm: VM) -> None:
        """( line1 col1 line2 col2 -- line col ) Delete range (undoable)."""
        require_editable_buffer(ed, "ed.delete-range", error_cls=MicromaxError)
        col2 = peek_int_arg(vm, "ed.delete-range", depth=1)
        line2 = peek_int_arg(vm, "ed.delete-range", depth=2)
        col1 = peek_int_arg(vm, "ed.delete-range", depth=3)
        line1 = peek_int_arg(vm, "ed.delete-range", depth=4)
        del vm.stack[-4:]
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
        try:
            ed._note_buffer_changed(eb)
        except Exception:
            pass
        c = ed.primary_cursor()
        vm.stack.append(int(c.line))
        vm.stack.append(int(c.col))


    # ----- undo grouping / transactions -----
    def hc_ed_with_undo(vm: VM) -> None:
        """( "desc" [ ... ] -- ok ) Run quotation as a single undo step.

        This groups buffer-visible changes across all open buffers into one undo
        entry.  If the quotation raises, every affected buffer is restored and
        no undo entry is recorded.
        """

        q = peek_quote_arg(vm, "ed.with-undo", depth=1)
        desc = peek_str_arg(vm, "ed.with-undo", depth=2)
        del vm.stack[-2:]
        stack_snapshot = capture_vm_stack(vm)
        before = ed._buffer_transaction_snapshot()
        try:
            with ed.undo.suppress_recording():
                vm.exec_xt(q)
        except Exception:
            ed._restore_macro_replay_snapshot(before)
            restore_vm_stack_snapshot(vm, stack_snapshot)
            raise
        after = ed._buffer_transaction_snapshot()
        if ed._buffer_transaction_changed(before, after):
            ed._record_buffer_transaction_snapshot(before, after, desc or 'with-undo')
            for buffer_name in {snap.name for snap in after.buffers if snap not in before.buffers}:
                eb = ed.buffers.get(str(buffer_name))
                if eb is None:
                    continue
                try:
                    ed._note_buffer_changed(eb)
                except Exception:
                    pass
        vm.stack.append(1)

    # ----- clipboard -----
    def hc_ed_clipboard(vm: VM) -> None:
        """( -- "text" ) Return clipboard as a single string."""

        vm.stack.append(ed.clipboard_text())

    def hc_ed_set_clipboard(vm: VM) -> None:
        """( "text" -- ) Set clipboard from a single string (kind=items)."""

        s = peek_str_arg(vm, "ed.set-clipboard")
        ed.set_clipboard_items([s], kind='items')
        del vm.stack[-1:]
        ed._paste_reset()

    def hc_ed_clipboard_items(vm: VM) -> None:
        """( -- items kind ) Return clipboard items + kind ("items"|"lines")."""

        items, kind = ed.clipboard_items_snapshot()
        vm.stack.append(items)
        vm.stack.append(str(kind))

    def hc_ed_set_clipboard_items(vm: VM) -> None:
        """( items kind -- ) Set clipboard from item list + kind ("items"|"lines")."""

        kind = peek_str_arg(vm, "ed.set-clipboard-items", depth=1)
        raw = peek_list_arg(vm, "ed.set-clipboard-items", depth=2)
        if kind not in ('items', 'lines'):
            raise MicromaxError('ed.set-clipboard-items: kind must be items|lines')
        ed.set_clipboard_items([str(x) for x in raw], kind=kind)
        del vm.stack[-2:]
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

        state = peek_list_arg(vm, "ed.set-cursorstate")
        if len(state) != 2:
            raise MicromaxError('ed.set-cursorstate: expected [primary [[id line col aL aC] ...]]')

        try:
            primary = int(state[0])
        except Exception as e:
            raise MicromaxError('ed.set-cursorstate: primary must be an integer') from e
        raw = state[1]
        if not isinstance(raw, list):
            raise MicromaxError('ed.set-cursorstate: expected [primary [[...]]].')

        eb = ed.cur()
        curs: list[Cursor] = []
        anchors: list[Cursor | None] = []
        pending_ids: list[int] = []

        seen: set[int] = set()
        for it in raw:
            if not isinstance(it, list) or len(it) != 5:
                raise MicromaxError('ed.set-cursorstate: expected entries [id line col aL aC]')
            try:
                cid, line, col, aL, aC = (int(it[0]), int(it[1]), int(it[2]), int(it[3]), int(it[4]))
            except Exception as e:
                raise MicromaxError('ed.set-cursorstate: expected integer entries') from e

            if cid <= 0 or cid in seen:
                pending_ids.append(0)
            else:
                pending_ids.append(cid)
                seen.add(cid)

            curs.append(eb.buf.clamp(Cursor(line, col)))
            if aL < 0 or aC < 0:
                anchors.append(None)
            else:
                anchors.append(eb.buf.clamp(Cursor(aL, aC)))

        del vm.stack[-1:]
        ids: list[int] = []
        for cid in pending_ids:
            ids.append(int(cid) if int(cid) > 0 else ed._alloc_cursor_id())
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

        q = peek_quote_arg(vm, "ed.with-cursorstate")
        del vm.stack[-1:]
        stack_snapshot = capture_vm_stack(vm)
        snap = capture_cursor_state(ed)
        try:
            try:
                vm.exec_xt(q)
            except Exception:
                restore_vm_stack_snapshot(vm, stack_snapshot)
                raise
        finally:
            restore_cursor_state(ed, snap)
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
        query = pop_str_arg(vm, "ed.jump-detail-row")
        row = ed.jump_detail_row(query)
        vm.stack.append(0 if row is None else row)

    def hc_ed_jump_section_rows(vm: VM) -> None:
        """( query -- sections ) Grouped jumplist rows by current/back/forward."""
        query = pop_str_arg(vm, "ed.jump-section-rows")
        vm.stack.append(ed.jump_section_rows(query))

    def hc_ed_jump_section_summary_rows(vm: VM) -> None:
        """( query -- rows ) Tiny count-aware jumplist section summaries."""
        query = pop_str_arg(vm, "ed.jump-section-summary-rows")
        vm.stack.append(ed.jump_section_summary_rows(query))

    def hc_ed_find(vm: VM) -> None:
        q = pop_str_arg(vm, "ed.find")
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
        query = pop_str_arg(vm, "ed.option-section-summary-rows")
        vm.stack.append(ed.option_section_summary_rows(query))

    def hc_ed_option_detail_row(vm: VM) -> None:
        """( name -- row|0 ) Tiny inspectable exact option-detail row as [query canonical value default kind local_override doc]."""
        name = pop_str_arg(vm, "ed.option-detail-row")
        row = ed.option_detail_row(name)
        vm.stack.append(0 if row is None else row)

    def hc_ed_opt_get(vm: VM) -> None:
        name = pop_str_arg(vm, "ed.opt-get")
        val = ed.options.get(name, local=ed.cur().local_options)
        if isinstance(val, bool):
            vm.stack.append(1 if val else 0)
        else:
            vm.stack.append(val)

    def hc_ed_opt_set(vm: VM) -> None:
        raw = peek_str_arg(vm, "ed.opt-set", depth=1)
        name = peek_str_arg(vm, "ed.opt-set", depth=2)
        # Global set (like the command-bar `set`).
        try:
            ed._guard_option_mutation(name)
            del vm.stack[-2:]
            val = ed.set_option_value(name, raw)
        except Exception as e:
            raise MicromaxError(f"ed.opt-set: {e}") from e
        if isinstance(val, bool):
            vm.stack.append(1 if val else 0)
        else:
            vm.stack.append(val)

    def hc_ed_opt_set_local(vm: VM) -> None:
        """( "name" "raw" -- value ) Set a buffer-local option."""
        raw = peek_str_arg(vm, "ed.opt-set-local", depth=1)
        name = peek_str_arg(vm, "ed.opt-set-local", depth=2)
        try:
            ed._guard_option_mutation(name)
            del vm.stack[-2:]
            val = ed.set_option_value(name, raw, local=True)
        except Exception as e:
            raise MicromaxError(f"ed.opt-set-local: {e}") from e
        if isinstance(val, bool):
            vm.stack.append(1 if val else 0)
        else:
            vm.stack.append(val)

    def hc_ed_require(vm: VM) -> None:
        """( path -- ) Load/evaluate a Micromax file through fs capability policy."""
        require_option_enabled(
            ed,
            "cap.fs-require",
            "ed.require disabled (set cap.fs-require true)",
            error_cls=MicromaxError,
        )
        path = pop_str_arg(vm, "ed.require")
        try:
            p = checked_sandbox_path(ed, str(path))
            result = read_file_for_editor(p, encoding="utf-8", containment_root=fs_cap_root(ed))
        except FileNotFoundError as e:
            raise MicromaxError(f"ed.require: file not found: {path}") from e
        except IsADirectoryError as e:
            raise MicromaxError(f"ed.require: not a file: {path}") from e
        except Exception as e:
            raise MicromaxError(f"ed.require: {e}") from e
        with ed.script_context():
            vm.eval(result.text, filename=str(result.path))


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
                row: list[object] = ["a", str(st.name), pairs]
                if bool(getattr(st, "script_context", False)):
                    row.append("script")
                out.append(row)
            elif st.kind == "command":
                row = ["c", str(st.payload.get("cmdline", ""))]
                if bool(getattr(st, "script_context", False)):
                    row.append("script")
                out.append(row)
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
                if len(it) not in (3, 4):
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
                script_origin = bool(len(it) >= 4 and str(it[3]) in {"script", "script-context", "s"})
                steps.append(MacroStep(kind="action", name=name, payload={"input": inp}, script_context=script_origin))
                continue
            if tag == "c":
                if len(it) not in (2, 3):
                    raise MicromaxError("macro: command step must be ['c', cmdline]")
                cmdline = str(it[1])
                script_origin = bool(len(it) >= 3 and str(it[2]) in {"script", "script-context", "s"})
                steps.append(MacroStep(kind="command", name="command", payload={"cmdline": cmdline}, script_context=script_origin))
                continue
            raise MicromaxError(f"macro: unknown step tag {tag!r}")
        return steps

    def hc_ed_macro_names(vm: VM) -> None:
        """( -- names ) List available macro names."""
        vm.stack.append(ed.macro_names())

    def hc_ed_macro_detail_row(vm: VM) -> None:
        """( name -- row|0 ) Tiny inspectable exact macro row as [query canonical state steps default shadow_steps]."""
        row = ed.macro_detail_row(pop_str_arg(vm, "ed.macro-detail-row"))
        vm.stack.append(row if row is not None else 0)

    def hc_ed_macro_inventory_rows(vm: VM) -> None:
        """( -- rows ) Tiny inspectable macro inventory rows as [name steps]."""
        vm.stack.append(ed.macro_inventory_rows())

    def hc_ed_macro_status_rows(vm: VM) -> None:
        """( -- rows ) Combined macro status rows as [section ...]."""
        vm.stack.append(ed.macro_status_rows())

    def hc_ed_macro_get(vm: VM) -> None:
        """( name -- steps ) Get a macro as portable steps."""
        name = pop_str_arg(vm, "ed.macro-get")
        vm.stack.append(_encode_macro_steps(ed.get_macro(name)))

    def hc_ed_macro_set(vm: VM) -> None:
        """( steps name -- ) Set a macro from portable steps."""
        name = peek_str_arg(vm, "ed.macro-set", depth=1)
        raw_steps = peek_stack_arg(vm, "ed.macro-set", depth=2)
        steps = _decode_macro_steps(raw_steps)
        if bool(ed.in_script_context()):
            steps = [
                MacroStep(
                    kind=str(step.kind),
                    name=str(step.name),
                    payload=dict(step.payload),
                    script_context=True,
                )
                for step in steps
            ]
        try:
            ed.set_macro(name, steps)
        except RuntimeError as e:
            raise MicromaxError(str(e)) from e
        del vm.stack[-2:]

    def hc_ed_macro_record(vm: VM) -> None:
        """( name -- ok ) Start recording macro into name."""
        name = pop_str_arg(vm, "ed.macro-record")
        vm.stack.append(1 if ed.start_macro(name) else 0)

    def hc_ed_macro_stop(vm: VM) -> None:
        """( -- ok ) Stop recording and save."""
        vm.stack.append(1 if ed.stop_macro() else 0)

    def hc_ed_macro_cancel(vm: VM) -> None:
        """( -- ok ) Cancel recording without saving."""
        vm.stack.append(1 if ed.cancel_macro() else 0)

    def hc_ed_macro_play(vm: VM) -> None:
        """( name n -- ok ) Play named macro n times."""
        n = peek_int_arg(vm, "ed.macro-play", depth=1)
        name = peek_str_arg(vm, "ed.macro-play", depth=2)
        # Direct hostcall replay is script-originated.  The interactive
        # `macro play` command remains a user-authority action, but a script
        # should not be able to replay a saved command step that grants cap.*
        # options before continuing with a gated file operation.
        with ed.script_context():
            ok = ed.play_macro(name, count=n)
        del vm.stack[-2:]
        vm.stack.append(1 if ok else 0)

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
    vm.register_host("ed.macro-detail-row", hc_ed_macro_detail_row)
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
    vm.register_host("ed.replace-preview", hc_ed_replace_preview)
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
            val = ed.set_option_value(name, raw)
        except Exception as e:
            raise MicromaxError(f"set: {e}", span=getattr(t, 'span', None))
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
            val = ed.toggle_option_value(name)
        except Exception as e:
            raise MicromaxError(f"toggle: {e}")
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
