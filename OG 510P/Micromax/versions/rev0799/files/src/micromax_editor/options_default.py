from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .editor import Editor, EditorBuffer


def install_default_options(self: Any) -> None:
    self.options.register("ignorecase", True, kind="bool", doc="case-insensitive searching")
    self.options.register("incsearch", True, kind="bool", doc="incremental search as you type")
    self.options.register("hlsearch", False, kind="bool", doc="highlight matches (UI layer)")
    self.options.register("hltrailingws", False, kind="bool", doc="highlight visible trailing whitespace (UI layer)")
    self.options.register("cursorline", True, kind="bool", doc="highlight the current visible row (UI layer)")
    self.options.register(
        "matchbrace",
        True,
        kind="bool",
        doc="highlight matching braces under or just left of the cursor (UI layer)",
    )
    self.options.register(
        "matchbraceleft",
        True,
        kind="bool",
        doc="match braces immediately left of the cursor too (UI layer)",
    )
    self.options.register(
        "matchbracestyle",
        "underline",
        kind="enum",
        enum=["underline", "highlight"],
        doc="matchbrace: render visible matches with underline or highlight (UI layer)",
    )


    # Paste aggregation: when enabled, UI layers may aggregate bursts of
    # character key events into a single insert so terminal pastes don't
    # trigger auto-indent/auto-pairs on a per-key basis. (micro-esque)
    self.options.register(
        "paste",
        False,
        kind="bool",
        doc="aggregate paste bursts (UI layer; enable temporarily if your terminal lacks bracketed paste)",
    )

    self.options.register(
        "clipboard",
        "internal",
        kind="enum",
        enum=["internal", "external", "terminal"],
        doc="clipboard backend (internal/external/terminal)",
    )


    # Terminal clipboard export (OSC 52). UI layers can optionally export
    # the editor's clipboard to the system clipboard via terminal escape
    # sequences. This is best-effort (terminal support varies).
    self.options.register(
        "clipboard.osc52",
        True,
        kind="bool",
        doc="clipboard=terminal: export copies via OSC 52 (TUI, best-effort)",
    )
    self.options.register(
        "clipboard.osc52.max",
        100000,
        kind="int",
        doc="clipboard=terminal: max UTF-8 bytes to export via OSC 52 (0=unlimited)",
    )

    # External clipboard export (best-effort). UI layers may use these
    # settings to pipe copied text to a system clipboard tool.
    self.options.register(
        "clipboard.external.cmd",
        "",
        kind="str",
        doc="clipboard=external: override clipboard tool command (empty=auto-detect)",
    )
    self.options.register(
        "clipboard.external.args",
        "",
        kind="str",
        doc="clipboard=external: override clipboard tool args (shell-like string)",
    )
    self.options.register(
        "clipboard.external.timeout",
        1.0,
        kind="float",
        doc="clipboard=external: timeout (seconds) for clipboard tool",
    )

    # External clipboard import (best-effort). Paste may use these settings
    # to read the system clipboard via a platform clipboard tool.
    self.options.register(
        "clipboard.external.readcmd",
        "",
        kind="str",
        doc="clipboard=external: override clipboard read command (empty=auto-detect)",
    )
    self.options.register(
        "clipboard.external.readargs",
        "",
        kind="str",
        doc="clipboard=external: override clipboard read args (shell-like string)",
    )
    self.options.register(
        "clipboard.external.readtimeout",
        1.0,
        kind="float",
        doc="clipboard=external: timeout (seconds) for clipboard read tool",
    )
    self.options.register(
        "clipboard.external.import",
        True,
        kind="bool",
        doc="clipboard=external: on Paste, import from system clipboard (best-effort)",
    )

    # Capability gate: allow script-driven clipboard exports when a privileged
    # clipboard backend is in use (terminal/external). Interactive copy/cut
    # remains allowed; this only affects exports triggered in script context.
    self.options.register(
        "cap.clipboard-write",
        False,
        kind="bool",
        doc="allow scripts to export clipboard to system clipboard (terminal/external)",
    )

    # Capability gate: allow scripts to read/import the system clipboard via
    # external tools. Interactive paste remains allowed.
    self.options.register(
        "cap.clipboard-read",
        False,
        kind="bool",
        doc="allow scripts to import system clipboard via external tools",
    )

    self.options.register("jumplist.auto", True, kind="bool", doc="auto-push jumplist for jump commands (goto/jump)")

    self.options.register("indent", "    ", kind="str", doc="indent prefix")
    self.options.register(
        "fileformat",
        "unix",
        kind="enum",
        enum=["unix", "dos"],
        doc="line ending format used when saving this buffer (unix=LF, dos=CRLF)",
    )
    self.options.register(
        "encoding",
        "utf-8",
        kind="str",
        doc="text encoding used when opening and saving this buffer",
    )
    self.options.register(
        "fastdirty",
        False,
        kind="bool",
        doc="use a cheap modified flag instead of comparing buffer content against the last clean baseline",
    )
    self.options.register(
        "autoindent",
        True,
        kind="bool",
        doc="preserve the current line's leading whitespace when inserting a newline",
    )
    self.options.register(
        "autosave",
        0,
        kind="int",
        doc="automatically save dirty path-backed buffers every N seconds (0=off)",
    )
    self.options.register(
        "readonly",
        False,
        kind="bool",
        doc="disallow edits and saves in the current buffer unless locally overridden",
    )
    self.options.register(
        "keepautoindent",
        False,
        kind="bool",
        doc="keep whitespace-only autoindent lines when pressing Enter again",
    )

    # Tabs: we follow micro-esque naming so config muscle-memory ports.
    # - tabsize controls *display* width (and how many spaces we insert when
    #   tabstospaces=true).
    # - tabstospaces controls whether the Tab key inserts '\t' or spaces.
    # Note: the core buffer is character-based; UI layers render tabs using
    # tabsize and can choose their own visual policies.
    self.options.register("tabsize", 4, kind="int", doc="tab width in spaces (display + tab insertion)")
    self.options.register("tabstospaces", True, kind="bool", doc="convert typed tabs to spaces")
    self.options.register(
        "tabmovement",
        False,
        kind="bool",
        doc="treat leading runs of tabsize spaces like one tab stop for left/right motion",
    )
    self.options.register(
        "rmtrailingws",
        False,
        kind="bool",
        doc="trim trailing spaces/tabs from lines when saving the buffer",
    )
    self.options.register(
        "eofnewline",
        False,
        kind="bool",
        doc="ensure non-empty saves end with a final newline",
    )
    self.options.register(
        "mkparents",
        False,
        kind="bool",
        doc="create missing parent directories automatically when saving",
    )

    self.options.register(
        "save.atomic",
        True,
        kind="bool",
        doc="write saves through a same-directory temp file and atomic replace when possible",
    )
    self.options.register(
        "save.checkexternal",
        True,
        kind="bool",
        doc="refuse to save when the file changed on disk since the buffer last synced",
    )
    self.options.register(
        "save.checkexternal.hashmax",
        1048576,
        kind="int",
        doc="maximum file size in bytes to hash for stronger save.checkexternal detection",
    )
    self.options.register(
        "save.preserveperm",
        True,
        kind="bool",
        doc="atomic saves preserve existing file permission bits when replacing a file",
    )
    self.options.register(
        "save.fsync",
        False,
        kind="bool",
        doc="fsync atomic-save temp file and parent directory before reporting success",
    )

    self.options.register("page.height", 30, kind="int", doc="page movement size for PageUp/PageDown")
    self.options.register(
        "pageoverlap",
        0,
        kind="int",
        doc="rows to keep visible between PageUp/PageDown moves",
    )
    self.options.register(
        "prompt.page",
        8,
        kind="int",
        doc="picker prompts: PageUp/PageDown selection jump size (rows)",
    )
    self.options.register(
        "prompt.wrap",
        True,
        kind="bool",
        doc="picker prompts: wrap selection at ends (true) or clamp (false)",
    )

    # Docs browser: controls how `helplinkpick` sections are labeled.
    # - kind: legacy Docs/Files/External grouping
    # - heading: group links by nearest markdown heading (Top/Links/...)
    self.options.register(
        "help.linksections",
        "kind",
        kind="enum",
        enum=["kind", "heading"],
        doc="docs browser: helplinkpick section labels (kind|heading)",
    )
    # Viewport defaults for UI layers. A future TUI should call `ed.viewport!`
    # on startup and on resize to keep these current.
    self.options.register("viewport.height", 30, kind="int", doc="viewport height (lines) for UI scrolling")
    self.options.register("viewport.width", 80, kind="int", doc="viewport width (cols) for UI horizontal scrolling")
    self.options.register(
        "scrollmargin",
        0,
        kind="int",
        doc="minimum vertical context rows to keep around the cursor while scrolling",
    )
    self.options.register(
        "colorcolumn",
        0,
        kind="int",
        doc="highlight a single visible guide column in the TUI/editor view (0=off)",
    )
    self.options.register(
        "scrollbar",
        False,
        kind="bool",
        doc="show a tiny right-edge scrollbar cue in the TUI/editor view",
    )
    self.options.register(
        "scrollbarchar",
        "|",
        kind="str",
        doc="character used for the tiny right-edge scrollbar cue (TUI/editor view)",
    )
    self.options.register(
        "showchars",
        "",
        kind="str",
        doc="show tiny visible replacements for spaces/tabs in the TUI/editor view (micro-esque key=value list)",
    )
    self.options.register(
        "overflowmarkers",
        False,
        kind="bool",
        doc="show tiny left/right markers for horizontally clipped lines in the TUI/editor view",
    )
    self.options.register("softwrap", False, kind="bool", doc="soft-wrap long lines instead of horizontal scrolling")
    self.options.register("wordwrap", False, kind="bool", doc="wrap softwrapped lines at spaces when possible")
    self.options.register("softwrap.contindent", -1, kind="int", doc="softwrap continuation indent columns (-1=auto, 0=off)")
    self.options.register("ruler", False, kind="bool", doc="show line numbers in the TUI/editor view")
    self.options.register("relativeruler", False, kind="bool", doc="show relative line numbers when ruler is enabled")
    self.options.register(
        "keymenu",
        False,
        kind="bool",
        doc="show a tiny nano-style key menu in the curses TUI",
    )
    self.options.register(
        "hltaberrors",
        False,
        kind="bool",
        doc="highlight tabs when spaces are expected and leading spaces when tabs are expected",
    )

    # Recent files MRU + prompt history (optional persistence).
    #
    # Persistence touches the host filesystem, so it is gated by `cap.persist`
    # (disabled by default). When enabled, `cap.persist-root` can constrain
    # where persistence files live.
    self.options.register("recent.persist", False, kind="bool", doc="persist recent file MRU to disk (requires cap.persist)")
    self.options.register("recent.file", "~/.config/micromax/recent.json", kind="str", doc="path for recent file MRU persistence")
    self.options.register("persist.atomic", True, kind="bool", doc="write editor persistence files with the shared atomic writer")
    self.options.register("persist.fsync", False, kind="bool", doc="fsync editor persistence writes (slower, safer on power loss)")
    self.options.register("persist.maxbytes", 1048576, kind="int", doc="maximum bytes to read from one editor persistence JSON file")

    self.options.register("history.persist", False, kind="bool", doc="persist prompt history to disk (requires cap.persist)")
    self.options.register_alias(
        "savehistory",
        "history.persist",
        doc="remember prompt/command history between sessions (requires cap.persist)",
    )
    self.options.register("history.file", "~/.config/micromax/history.json", kind="str", doc="path for prompt history persistence")
    self.options.register("history.limit", 200, kind="int", doc="max stored history entries per prompt kind")

    self.options.register("savecursor", False, kind="bool", doc="persist per-file primary cursor positions (requires cap.persist)")
    self.options.register("savecursor.file", "~/.config/micromax/cursor.json", kind="str", doc="path for savecursor persistence")
    self.options.register("parsecursor", False, kind="bool", doc="parse open targets like file:line[:col] into an initial cursor position")
    self.options.register("smartpaste", False, kind="bool", doc="best-effort indent multi-line pastes to the current line prefix")

    # Capability gates (host-owned world). These control whether *unsafe*
    # host surfaces are advertised/enabled.
    self.options.register("cap.persist", False, kind="bool", doc="allow editor-owned persistence files (recent/history/savecursor) to be read/written (unsafe)")
    self.options.register("cap.persist-root", "~/.config/micromax", kind="str", doc="sandbox root for persistence files (empty=unrestricted)")
    self.options.register("cap.open-url", False, kind="bool", doc="allow opening external URLs from docs (unsafe)")
    self.options.register(
        "open-url.confirm",
        True,
        kind="bool",
        doc="confirm before opening external URLs from docs (even when cap.open-url is enabled)",
    )
    self.options.register("cap.shell", False, kind="bool", doc="allow running shell commands from scripts (unsafe)")
    self.options.register("cap.fs-open", False, kind="bool", doc="allow scripts to open files from disk (unsafe)")
    self.options.register("cap.fs-save", False, kind="bool", doc="allow scripts to save buffers to disk (unsafe)")
    self.options.register(
        "cap.fs-force-save",
        False,
        kind="bool",
        doc="allow scripts to force-save over detected disk changes (unsafe)",
    )
    self.options.register(
        "cap.buffer-discard",
        False,
        kind="bool",
        doc="allow scripts to discard unsaved editor buffer changes via force close/revert/quit (unsafe)",
    )
    self.options.register(
        "cap.history-clear",
        False,
        kind="bool",
        doc="allow scripts to clear editor navigation/recent/message history registers (unsafe)",
    )
    self.options.register(
        "cap.undo-redo",
        False,
        kind="bool",
        doc="allow scripts to replay trusted/editor undo-redo history entries (unsafe)",
    )
    self.options.register("cap.fs-read", False, kind="bool", doc="allow scripts to read arbitrary files from disk (unsafe)")
    self.options.register("cap.fs-list", False, kind="bool", doc="allow scripts to list directory entries from disk (unsafe)")
    self.options.register("cap.fs-stat", False, kind="bool", doc="allow scripts to stat paths on disk (unsafe)")
    self.options.register("cap.fs-require", False, kind="bool", doc="allow scripts to load/evaluate Micromax files from disk (unsafe)")
    self.options.register("cap.fs-chdir", False, kind="bool", doc="allow scripts to change the process current directory (unsafe)")
    self.options.register("cap.fs-root", "", kind="str", doc="filesystem sandbox root for cap.fs-* helpers (empty=unrestricted)")

    # Statusline / infobar: micro-esque split format strings.
    # Directives are embedded as $() expressions, e.g. $(filename), $(line),
    # $(opt:filetype), $(bind:SomeAction).
    self.options.register("statusline", True, kind="bool", doc="show status line (UI layer)")
    self.options.register("infobar", True, kind="bool", doc="show the idle message/prompt line in the curses TUI")
    self.options.register(
        "constantshow",
        False,
        kind="bool",
        doc="show a tiny right-aligned cursor summary in the idle infobar (nano-esque)",
    )
    self.options.register("basename", False, kind="bool", doc="show only the basename in filename/statusline displays instead of the full path")
    # TUI debug helpers.
    self.options.register(
        "tui.bracketedpaste",
        True,
        kind="bool",
        doc="TUI: enable bracketed paste mode (CSI ? 2004 h/l)",
    )
    self.options.register("tui.rawkeys", False, kind="bool", doc="TUI: show raw key events instead of dispatching")
    self.options.register(
        "statusformatl",
        "$(filename)$(modified)$(readonly)$(disk)",
        kind="str",
        doc="status line left format string (micro-esque $() directives)",
    )
    self.options.register(
        "statusformatr",
        "ft:$(opt:filetype) enc:$(opt:encoding) $(opt:fileformat)$(searchpos)$(bufpos) $(position)$(cur)$(sel) $(percentage)% $(mode)$(keymode)$(macro)",
        kind="str",
        doc="status line right format string (micro-esque $() directives)",
    )
