from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Callable

from micromax.vm import Span

from .binding_commands import (
    c_bind,
    c_binddoc,
    c_bindmode,
    c_bindmodedoc,
    c_bindmodeprefix,
    c_bindprefix,
    c_unbind,
    c_unbindmode,
)
from .buffer_commands import (
    c_buffer,
    c_buffers,
    c_cd,
    c_close,
    c_closeall,
    c_diff,
    c_diskstate,
    c_goto,
    c_jump,
    c_jumpback,
    c_jumpforward,
    c_mark,
    c_markjump,
    c_marks,
    c_new,
    c_only,
    c_open,
    c_prevbuf,
    c_pwd,
    c_recent,
    c_recentdirpick,
    c_recentpick,
    c_revert_bang,
    c_revert_soft,
    c_save,
    c_save_bang,
    c_saveas,
    c_showbuffer,
    c_showbuffergroups,
    c_showjump,
    c_showjumpgroups,
    c_showmark,
    c_showmarkgroups,
    c_showpalettegroups,
    c_showrecent,
    c_showrecentdir,
    c_showrecentdirgroups,
    c_showrecentgroups,
)
from .cmdline import CommandLine
from .file_scriptops import checked_sandbox_path
from .help_commands import (
    c_help,
    c_helpback,
    c_helpfollow,
    c_helpforward,
    c_helpjump,
    c_helplinkcopy,
    c_helplinkpick,
    c_helpnavpick,
    c_helpoutlinepick,
    c_helphistory,
    c_helppick,
    c_helpprune,
    c_helpresume,
    c_urlcopy,
    c_urlopen,
)
from .keymode_commands import (
    c_keymode,
    c_popkeymode,
    c_prefixmode,
    c_pushkeymode,
    c_pushkeymode_once,
    c_rawkeys,
)
from .macro_commands import MACRO_ROOT_DOC, c_macro
from .option_commands import c_set, c_setlocal, c_show, c_toggle, c_togglelocal
from .picker_commands import (
    c_apropos,
    c_bindingpick,
    c_bufferpick,
    c_commandpick,
    c_filepick,
    c_jumppick,
    c_jumps,
    c_markpick,
    c_pluginpick,
    c_statusfmt,
    c_topicpick,
)
from .plugin_commands import PLUGIN_ROOT_DOC, c_plugin
from .replace_commands import (
    c_qreplace,
    c_replace,
    c_replaceall,
    c_replacepreview,
)
from .recovery_commands import (
    c_recover,
    c_recoverclean,
    c_recoverdismiss,
    c_recoveries,
    c_recovermode,
    c_recovertemps,
)
from .session_commands import c_quit, c_redo, c_reload, c_undo, c_undostatus
from .show_commands import (
    c_showaction,
    c_showbindings,
    c_showbindingmodes,
    c_showcmd,
    c_showdoc,
    c_showdocs,
    c_showhelpheading,
    c_showhelplink,
    c_showhelpnav,
    c_showhook,
    c_showhooks,
    c_showkey,
    c_showkeymode,
    c_showkeymodes,
    c_showmacro,
    c_showoption,
    c_showoptiongroups,
    c_showplugin,
    c_showplugins,
    c_showstatus,
    c_showtopic,
    c_showtopics,
    c_showword,
    c_whichkey,
)


CommandFn = Callable[["Editor", list[str]], bool]


@dataclass(frozen=True)
class Command:
    name: str
    fn: CommandFn
    doc: str = ""
    span: Span | None = None
    group: str | None = None
    script_context: bool = False
    plugin_load_root: str | None = None
    plugin_generation: int | None = None
    script_origin_id: str | None = None


class CommandDispatcher:
    def __init__(self) -> None:
        self._cmds: dict[str, Command] = {}

    def register(
        self,
        name: str,
        fn: CommandFn,
        *,
        doc: str = "",
        span: Span | None = None,
        group: str | None = None,
        script_context: bool = False,
        plugin_load_root: str | None = None,
        plugin_generation: int | None = None,
        script_origin_id: str | None = None,
    ) -> None:
        self._cmds[name] = Command(
            name=name,
            fn=fn,
            doc=doc,
            span=span,
            group=group,
            script_context=bool(script_context),
            plugin_load_root=(str(plugin_load_root) if plugin_load_root else None),
            plugin_generation=(int(plugin_generation) if plugin_generation not in (None, "") else None),
            script_origin_id=(str(script_origin_id) if script_origin_id else None),
        )

    def remove(self, name: str) -> bool:
        return self._cmds.pop(name, None) is not None

    def get(self, name: str) -> Command | None:
        return self._cmds.get(name)

    def names(self) -> list[str]:
        return sorted(self._cmds.keys())

    def command_rows(self) -> list[list[object]]:
        rows: list[list[object]] = []
        for name in sorted(self._cmds.keys()):
            c = self._cmds[name]
            span = 0 if c.span is None else [c.span.filename, int(c.span.line), int(c.span.col)]
            rows.append([c.name, c.doc, c.group or 0, span])
        return rows

    def remove_group(self, group: str) -> int:
        removed = 0
        for name, c in list(self._cmds.items()):
            if c.group == group:
                del self._cmds[name]
                removed += 1
        return removed

    def retag_group(self, old: str, new: str) -> int:
        """Rename a command-registration group in place.

        Plugin reload can stage a replacement under a temporary group so a
        failed load does not disturb the currently-running plugin.  Once the
        replacement has fully loaded, the staged commands need to become the
        stable plugin group before the temporary tag disappears from inventory
        rows and cleanup paths.
        """

        old_group = str(old)
        new_group = str(new)
        changed = 0
        for name, c in list(self._cmds.items()):
            if c.group == old_group:
                self._cmds[name] = replace(c, group=new_group)
                changed += 1
        return changed

    def groups(self) -> list[str]:
        out = sorted({str(c.group) for c in self._cmds.values() if c.group})
        return out

    def exec(self, ed: "Editor", cl: CommandLine) -> bool:
        cmd = self.get(cl.name)
        if cmd is None:
            ed.message(f"command: no such command: {cl.name}")
            return False
        message_witness = (len(ed.messages), ed.last_visible_message())
        try:
            ok = bool(cmd.fn(ed, cl.args))
        except Exception as e:
            ed.message(f"command {cl.name}: error: {e}")
            return False
        if not ok and message_witness == (len(ed.messages), ed.last_visible_message()):
            # A failed command must not leave the prior success message looking
            # current.  This is especially important for transactional plugin
            # callbacks: rollback intentionally restores prompt/editor state,
            # including any message the callback emitted before returning false.
            ed.message(f"command {cl.name}: failed")
        return ok


def install_default_commands(ed: "Editor") -> None:
    """Install a micro-inspired set of command-bar commands.

    Reference: micro runtime help/commands.md (Ctrl-e command bar, help/save/quit,
    set/toggle/show, reload, etc.).
    """

    d = ed.command_dispatcher

    d.register("help", c_help, doc="help [topic] - show help for commands/actions")
    d.register("helppick", c_helppick, doc="helppick [QUERY] - open searchable docs picker")
    d.register("helpback", c_helpback, doc="helpback - go back in docs help navigation")
    d.register("helpresume", c_helpresume, doc="helpresume - reopen the last dormant session-local docs help target")
    d.register("helpprune", c_helpprune, doc="helpprune - prune missing docs targets from local help history")
    d.register("helpforward", c_helpforward, doc="helpforward - go forward in docs help navigation")
    d.register("helphistory", c_helphistory, doc="helphistory - show the tiny docs help history register")
    d.register("helpfollow", c_helpfollow, doc="helpfollow - follow a markdown link under cursor in docs help")
    d.register("helplinkcopy", c_helplinkcopy, doc="helplinkcopy - copy markdown link target under cursor in docs help")
    d.register("helpcopylink", c_helplinkcopy, doc="helpcopylink - alias for helplinkcopy")
    d.register("helplinkpick", c_helplinkpick, doc="helplinkpick [QUERY] - pick a link from the current docs page")
    d.register("helpoutlinepick", c_helpoutlinepick, doc="helpoutlinepick [QUERY] - pick a heading from the current docs page")
    d.register("helpnavpick", c_helpnavpick, doc="helpnavpick [QUERY] - pick a heading or link from the current docs page")
    d.register("helpjump", c_helpjump, doc="helpjump [QUERY] - jump to a heading on the current docs page")
    d.register("urlopen", c_urlopen, doc="urlopen [URL] - open URL under cursor (or explicit URL) [cap.open-url]")
    d.register("openurl", c_urlopen, doc="openurl [URL] - alias for urlopen")
    d.register("urlcopy", c_urlcopy, doc="urlcopy [URL] - copy URL under cursor (or explicit URL)")

    d.register("sfmt", c_statusfmt, doc="sfmt TEMPLATE - render a statusformat template (debug)")
    d.register("commandpick", c_commandpick, doc="commandpick [QUERY] - open searchable command/action palette")
    d.register("topicpick", c_topicpick, doc="topicpick [QUERY] - open searchable topic/help prompt")
    d.register("bindingpick", c_bindingpick, doc="bindingpick [QUERY] - open searchable current-binding prompt")
    d.register("bufferpick", c_bufferpick, doc="bufferpick [QUERY] - open searchable buffer picker")
    d.register("filepick", c_filepick, doc="filepick [QUERY] - open bounded project-file picker")
    d.register("pluginpick", c_pluginpick, doc="pluginpick [QUERY] - open searchable plugin picker")
    d.register("markpick", c_markpick, doc="markpick [QUERY] - open searchable mark picker")
    d.register("jumppick", c_jumppick, doc="jumppick [QUERY|N|#N] - open searchable jumplist picker or jump to visible slot")
    d.register("jumps", c_jumps, doc="jumps - show the current jumplist register")
    d.register("showjump", c_showjump, doc="showjump INDEX|#N - show exact jumplist entry without jumping")
    d.register("apropos", c_apropos, doc="apropos QUERY - search commands/actions/words/docs by name")
    d.register("bind", c_bind, doc="bind KEY ACTIONSPEC - bind a global key")
    d.register("bindmode", c_bindmode, doc="bindmode MODE KEY ACTIONSPEC - bind a key in a mode")
    d.register("bindprefix", c_bindprefix, doc="bindprefix KEY MODE [DOC...] - bind a prefix key that enters a one-shot mode")
    d.register("bindmodeprefix", c_bindmodeprefix, doc="bindmodeprefix OWNERMODE KEY MODE [DOC...] - bind a mode-local prefix key that enters a one-shot mode")
    d.register("binddoc", c_binddoc, doc="binddoc KEY DOC... - attach a keybinding description")
    d.register("bindmodedoc", c_bindmodedoc, doc="bindmodedoc MODE KEY DOC... - attach a mode-keybinding description")
    d.register("unbind", c_unbind, doc="unbind KEY - remove a global key binding")
    d.register("unbindmode", c_unbindmode, doc="unbindmode MODE KEY - remove a mode-specific binding")
    d.register("keymode", c_keymode, doc="keymode [MODE|global] - show/set active key mode")
    d.register("pushkeymode", c_pushkeymode, doc="pushkeymode MODE - push an active key mode")
    d.register("pushkeymode-once", c_pushkeymode_once, doc="pushkeymode-once MODE - push a one-shot key mode")
    d.register("prefixmode", c_prefixmode, doc="prefixmode MODE - enter a one-shot prefix mode and show reachable bindings")
    d.register("popkeymode", c_popkeymode, doc="popkeymode - pop the active key mode")
    d.register("showkeymodes", c_showkeymodes, doc="showkeymodes - show active and known key modes")
    d.register("showkeymode", c_showkeymode, doc="showkeymode MODE - show exact keymode detail")
    d.register("showoption", c_showoption, doc="showoption NAME - show exact option value/default/doc detail")
    d.register("showoptiongroups", c_showoptiongroups, doc="showoptiongroups [QUERY] - show count-aware option families")
    d.register("showbuffergroups", c_showbuffergroups, doc="showbuffergroups [QUERY] - show count-aware buffer sections")
    d.register("showbuffer", c_showbuffer, doc="showbuffer NAME - show exact buffer state without switching")
    d.register("showrecent", c_showrecent, doc="showrecent PATH|N|#N - show exact recent-file state without opening")
    d.register("showrecentdir", c_showrecentdir, doc="showrecentdir DIR|N|#N - show exact recent-directory bucket state without opening")
    d.register("showmark", c_showmark, doc="showmark NAME - show exact mark state without jumping")
    d.register("showmacro", c_showmacro, doc="showmacro NAME - show exact macro state without replaying")
    d.register("showmarkgroups", c_showmarkgroups, doc="showmarkgroups [QUERY] - show count-aware mark buckets by owning buffer")
    d.register("showjumpgroups", c_showjumpgroups, doc="showjumpgroups [QUERY] - show count-aware jumplist sections")
    d.register("showpalettegroups", c_showpalettegroups, doc="showpalettegroups [QUERY] - show count-aware command-palette buckets")
    d.register("showkey", c_showkey, doc="showkey KEY - show resolved binding for key")
    d.register("rawkeys", c_rawkeys, doc="rawkeys [on|off] - TUI raw key debugging (print key events instead of dispatching)")
    d.register("showbindings", c_showbindings, doc="showbindings [MODE|active] - show discoverable bindings")
    d.register("showbindingmodes", c_showbindingmodes, doc="showbindingmodes [QUERY] - show reachable binding buckets by winning mode")
    d.register("whichkey", c_whichkey, doc="whichkey - show currently available bindings with descriptions")
    d.register("showcmd", c_showcmd, doc="show command docs/provenance")
    d.register("showaction", c_showaction, doc="showaction NAME - show editor action docs")
    d.register("showword", c_showword, doc="showword NAME - show visible micromax word docs/effect/provenance")
    d.register("showdoc", c_showdoc, doc="showdoc TOPIC - show resolved docs title/section/summary/path")
    d.register("showtopic", c_showtopic, doc="showtopic NAME - show exact help topic detail without reopening docs")
    d.register("showtopics", c_showtopics, doc="showtopics [QUERY] - show count-aware generic help-topic sections")
    d.register("showdocs", c_showdocs, doc="showdocs - show count-aware docs-family sections")
    d.register("showplugins", c_showplugins, doc="showplugins [QUERY] - show count-aware plugin-state sections")
    d.register("showplugin", c_showplugin, doc="showplugin NAME - show exact plugin state without opening verbose detail")
    d.register("showhelpheading", c_showhelpheading, doc="showhelpheading - show current docs heading under cursor")
    d.register("showhelplink", c_showhelplink, doc="showhelplink - show current docs-link target under cursor")
    d.register("showhelpnav", c_showhelpnav, doc="showhelpnav [QUERY] - show count-aware current-doc navigation sections")
    d.register("showhook", c_showhook, doc="showhook NAME - show installed hook handlers")
    d.register("showhooks", c_showhooks, doc="showhooks [QUERY] - show count-aware live hook summary")
    d.register("showstatus", c_showstatus, doc="showstatus - show portable statusline summary")
    d.register("undo", c_undo, doc="undo - undo the latest edit")
    d.register("redo", c_redo, doc="redo - redo the latest undone edit")
    d.register("undostatus", c_undostatus, doc="undostatus - show undo/redo depth and retained text bytes")
    d.register("macro", c_macro, doc=MACRO_ROOT_DOC)
    d.register("goto", c_goto, doc="goto line[:col] - go to absolute line")
    d.register("jump", c_jump, doc="jump +/-n[:col] - move relative lines")
    d.register("jumpback", c_jumpback, doc="jumpback - jump to the previous jumplist entry")
    d.register("jumpforward", c_jumpforward, doc="jumpforward - jump to the next jumplist entry")
    d.register("replace", c_replace, doc="replace SEARCH VALUE [-a] [-l] - replace (regex by default)")
    d.register("replaceall", c_replaceall, doc="replaceall SEARCH VALUE [-l] - replace all occurrences")
    d.register("replacepreview", c_replacepreview, doc="replacepreview SEARCH VALUE [-a] [-l] - preview replace changes without mutating")
    d.register("qreplace", c_qreplace, doc="qreplace SEARCH VALUE [-l] - interactive confirming replace")
    d.register("queryreplace", c_qreplace, doc="queryreplace SEARCH VALUE [-l] - alias for qreplace")
    d.register("new", c_new, doc="new [NAME] - create an empty untitled buffer")
    d.register("open", c_open, doc="open FILE - open file")
    d.register("save", c_save, doc="save [FILE] - save (optionally save as)")
    d.register("save!", c_save_bang, doc="save! [FILE] - force save/overwrite an external change")
    d.register("saveas", c_saveas, doc="saveas FILE - save as")
    d.register("recoveries", c_recoveries, doc="recoveries - list interrupted saves without reading their payloads")
    d.register("recover", c_recover, doc="recover [#N|ID] - open interrupted bytes in a dirty buffer; disk stays unchanged")
    d.register("recovermode", c_recovermode, doc="recovermode [#N|ID] - verify and finish an interrupted atomic-save permission restore")
    d.register("recovertemps", c_recovertemps, doc="recovertemps - list bounded private save residue without opening payloads")
    d.register("recoverclean", c_recoverclean, doc="recoverclean [#N|ID] - revalidate and remove one stale private save temp")
    d.register("recoverdismiss", c_recoverdismiss, doc="recoverdismiss [#N|ID] - permanently discard one interrupted save")
    d.register("revert", c_revert_soft, doc="revert - reload current buffer from disk if clean")
    d.register("revert!", c_revert_bang, doc="revert! - discard local edits and reload from disk")
    d.register("diff", c_diff, doc="diff [N|--all] - show disk-vs-buffer diff for current file")
    d.register("diskdiff", c_diff, doc="diskdiff [N|--all] - alias for diff")
    d.register("diskstate", c_diskstate, doc="diskstate [--all] - list buffer disk freshness/conflict states")
    d.register("diskconflicts", c_diskstate, doc="diskconflicts - alias for diskstate")
    d.register("close", c_close, doc="close [NAME] [-f] - close a buffer")
    d.register("closeall", c_closeall, doc="closeall [-f] - close all buffers")
    d.register("closeall!", lambda ed, args: c_closeall(ed, ["-f", *args]), doc="closeall! - force close all buffers")
    d.register("only", c_only, doc="only [-f] - close all other buffers")
    d.register("only!", lambda ed, args: c_only(ed, ["-f", *args]), doc="only! - force close other buffers")
    d.register("prevbuf", c_prevbuf, doc="prevbuf - switch to previous buffer")
    d.register("close!", lambda ed, args: c_close(ed, ["-f", *args]), doc="close! - force close a buffer")
    d.register("recent", c_recent, doc="recent [N|#N|clear] - show/open recent files")
    d.register("recentpick", c_recentpick, doc="recentpick [QUERY] - open searchable recent file picker")
    d.register("recentdirpick", c_recentdirpick, doc="recentdirpick [QUERY] - open searchable recent file picker grouped by directory")
    d.register("showrecentgroups", c_showrecentgroups, doc="showrecentgroups [QUERY] - show count-aware recent file buckets")
    d.register("showrecentdirgroups", c_showrecentdirgroups, doc="showrecentdirgroups [QUERY] - show count-aware recent directory buckets")

    d.register("buffers", c_buffers, doc="buffers - list open buffers")
    d.register("buffer", c_buffer, doc="buffer NAME - switch active buffer")
    d.register("mark", c_mark, doc="mark NAME - set a named mark at the primary cursor")
    d.register("markjump", c_markjump, doc="markjump NAME - jump to a named mark")
    d.register("marks", c_marks, doc="marks - list marks")

    d.register("quit", c_quit, doc="quit - request editor quit")
    d.register("quit!", lambda ed, args: c_quit(ed, ["-f", *args]), doc="quit! - force quit (no warning)")
    d.register("pwd", c_pwd, doc="pwd - show current directory")
    d.register("cd", c_cd, doc="cd PATH - change directory")
    d.register("set", c_set, doc="set OPTION VALUE")
    d.register("setlocal", c_setlocal, doc="setlocal OPTION VALUE")
    d.register("show", c_show, doc="show [OPTION] - show option(s)")
    d.register("toggle", c_toggle, doc="toggle OPTION")
    d.register("togglelocal", c_togglelocal, doc="togglelocal OPTION")
    d.register("reload", c_reload, doc="reload - reload runtime/plugins")
    d.register("plugin", c_plugin, doc=PLUGIN_ROOT_DOC)
