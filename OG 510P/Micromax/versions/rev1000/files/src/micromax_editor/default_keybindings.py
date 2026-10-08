"""Trusted product defaults for the Micromax editor keymap.

The bundled ``plugins/core/init.mx`` file mirrors the public rows so the
configuration language remains readable and portable, but the editor host owns
the shipped baseline. A plugin may repeat an exact row idempotently; it does
not acquire the authority of a later physical user keypress.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Iterable

if TYPE_CHECKING:
    from .keymap import Keymap


@dataclass(frozen=True, slots=True)
class DefaultKeyBinding:
    """One declarative host-owned default binding."""

    mode: str
    key: str
    action_spec: str


# Rows intentionally mirrored by ``plugins/core/init.mx``.  Keep order stable:
# it is useful in documentation, tests, and tiny embedders that want to render
# the defaults without constructing an Editor.
CORE_MIRRORED_KEY_BINDINGS: tuple[DefaultKeyBinding, ...] = (
    DefaultKeyBinding(mode='global', key='LeftArrow', action_spec='CursorLeft'),
    DefaultKeyBinding(mode='global', key='RightArrow', action_spec='CursorRight'),
    DefaultKeyBinding(mode='global', key='UpArrow', action_spec='PromptHistoryPrev|CursorUp'),
    DefaultKeyBinding(mode='global', key='DownArrow', action_spec='PromptHistoryNext|CursorDown'),
    DefaultKeyBinding(mode='global', key='Home', action_spec='StartOfLine'),
    DefaultKeyBinding(mode='global', key='End', action_spec='EndOfLine'),
    DefaultKeyBinding(mode='global', key='Ctrl-LeftArrow', action_spec='WordLeft'),
    DefaultKeyBinding(mode='global', key='Ctrl-RightArrow', action_spec='WordRight'),
    DefaultKeyBinding(mode='global', key='Shift-Ctrl-LeftArrow', action_spec='SelectWordLeft'),
    DefaultKeyBinding(mode='global', key='Shift-Ctrl-RightArrow', action_spec='SelectWordRight'),
    DefaultKeyBinding(mode='global', key='PageUp', action_spec='PageUp'),
    DefaultKeyBinding(mode='global', key='PageDown', action_spec='PageDown'),
    DefaultKeyBinding(mode='global', key='Ctrl-Home', action_spec='DocTop'),
    DefaultKeyBinding(mode='global', key='Ctrl-End', action_spec='DocBottom'),
    DefaultKeyBinding(mode='global', key='Ctrl-z', action_spec='Undo'),
    DefaultKeyBinding(mode='global', key='Ctrl-y', action_spec='Redo'),
    DefaultKeyBinding(mode='global', key='Backspace', action_spec='Backspace'),
    DefaultKeyBinding(mode='global', key='Delete', action_spec='Delete'),
    DefaultKeyBinding(mode='global', key='Enter', action_spec='SubmitPrompt|InsertNewline'),
    DefaultKeyBinding(mode='global', key='Shift-LeftArrow', action_spec='SelectLeft'),
    DefaultKeyBinding(mode='global', key='Shift-RightArrow', action_spec='SelectRight'),
    DefaultKeyBinding(mode='global', key='Shift-UpArrow', action_spec='SelectUp'),
    DefaultKeyBinding(mode='global', key='Shift-DownArrow', action_spec='SelectDown'),
    DefaultKeyBinding(mode='global', key='Ctrl-a', action_spec='SelectAll'),
    DefaultKeyBinding(mode='global', key='Ctrl-c', action_spec='Copy'),
    DefaultKeyBinding(mode='global', key='Ctrl-x', action_spec='Cut'),
    DefaultKeyBinding(mode='global', key='Ctrl-v', action_spec='Paste'),
    DefaultKeyBinding(mode='global', key='Ctrl-k', action_spec='CutLine'),
    DefaultKeyBinding(mode='global', key='Ctrl-d', action_spec='DuplicateLine'),
    DefaultKeyBinding(mode='global', key='Alt-UpArrow', action_spec='MoveLinesUp'),
    DefaultKeyBinding(mode='global', key='Alt-DownArrow', action_spec='MoveLinesDown'),
    DefaultKeyBinding(mode='global', key='Tab', action_spec='Autocomplete|IndentSelection|InsertTab'),
    DefaultKeyBinding(mode='global', key='Shift-Tab', action_spec='PromptCompletePrev|UnindentSelection'),
    DefaultKeyBinding(mode='global', key='Ctrl-e', action_spec='CommandMode'),
    DefaultKeyBinding(mode='global', key='Ctrl-o', action_spec='FilePicker'),
    DefaultKeyBinding(mode='global', key='Alt-o', action_spec='OpenUrlUnderCursor'),
    DefaultKeyBinding(mode='global', key='Alt-y', action_spec='CopyUrlUnderCursor'),
    DefaultKeyBinding(mode='global', key='Ctrl-r', action_spec='command-edit:replace '),
    DefaultKeyBinding(mode='global', key='Alt-%', action_spec='command-edit:qreplace '),
    DefaultKeyBinding(mode='global', key='Ctrl-b', action_spec='command:bufferpick'),
    DefaultKeyBinding(mode='global', key='Ctrl-Space', action_spec='CommandPalette'),
    DefaultKeyBinding(mode='global', key='Ctrl-f', action_spec='Find'),
    DefaultKeyBinding(mode='global', key='Ctrl-n', action_spec='FindNext'),
    DefaultKeyBinding(mode='global', key='Ctrl-p', action_spec='FindPrevious'),
    DefaultKeyBinding(mode='global', key='Alt-g', action_spec='BindingPrompt'),
    DefaultKeyBinding(mode='global', key='Esc', action_spec='Escape|ClearSelection|RemoveAllMultiCursors'),
    DefaultKeyBinding(mode='global', key='Ctrl-s', action_spec='command:save'),
    DefaultKeyBinding(mode='global', key='Ctrl-q', action_spec='command:quit'),
    DefaultKeyBinding(mode='global', key='Alt-Shift-p', action_spec='command:pwd'),
    DefaultKeyBinding(mode='global', key='Ctrl-g', action_spec='command:helppick'),
    DefaultKeyBinding(mode='global', key='Ctrl-u', action_spec='ToggleMacro'),
    DefaultKeyBinding(mode='global', key='Ctrl-j', action_spec='PlayMacro'),
    DefaultKeyBinding(mode='global', key='Alt-j', action_spec='PushJump'),
    DefaultKeyBinding(mode='global', key='Alt-LeftArrow', action_spec='JumpBack'),
    DefaultKeyBinding(mode='global', key='Alt-RightArrow', action_spec='JumpForward'),
    DefaultKeyBinding(mode='global', key='Alt-n', action_spec='SpawnMultiCursorSelect'),
    DefaultKeyBinding(mode='global', key='Alt-Shift-Up', action_spec='SpawnMultiCursorUp'),
    DefaultKeyBinding(mode='global', key='Alt-Shift-Down', action_spec='SpawnMultiCursorDown'),
    DefaultKeyBinding(mode='global', key='Alt-p', action_spec='RemoveMultiCursor'),
    DefaultKeyBinding(mode='global', key='Alt-c', action_spec='RemoveAllMultiCursors'),
    DefaultKeyBinding(mode='global', key='Alt-x', action_spec='SkipMultiCursor'),
    DefaultKeyBinding(mode='global', key='Alt-m', action_spec='SpawnMultiCursor'),
    DefaultKeyBinding(mode='global', key='Alt-;', action_spec='FlipSelections'),
    DefaultKeyBinding(mode='global', key='Alt-:', action_spec='EnsureSelectionsForward'),
    DefaultKeyBinding(mode='global', key='Alt-,', action_spec='CollapseToPrimary'),
    DefaultKeyBinding(mode='prompt', key='LeftArrow', action_spec='PromptLeft'),
    DefaultKeyBinding(mode='prompt', key='RightArrow', action_spec='PromptRight'),
    DefaultKeyBinding(mode='prompt', key='Home', action_spec='PromptHome'),
    DefaultKeyBinding(mode='prompt', key='End', action_spec='PromptEnd'),
    DefaultKeyBinding(mode='prompt', key='Backspace', action_spec='PromptBackspace'),
    DefaultKeyBinding(mode='prompt', key='Delete', action_spec='PromptDelete'),
    DefaultKeyBinding(mode='prompt', key='UpArrow', action_spec='PromptSuggestPrev|PromptHistoryPrev'),
    DefaultKeyBinding(mode='prompt', key='DownArrow', action_spec='PromptSuggestNext|PromptHistoryNext'),
    DefaultKeyBinding(mode='prompt', key='PageUp', action_spec='PromptSuggestPageUp|PromptHistoryPrev'),
    DefaultKeyBinding(mode='prompt', key='PageDown', action_spec='PromptSuggestPageDown|PromptHistoryNext'),
    DefaultKeyBinding(mode='prompt', key='Alt-UpArrow', action_spec='PromptSuggestPrevSection'),
    DefaultKeyBinding(mode='prompt', key='Alt-DownArrow', action_spec='PromptSuggestNextSection'),
    DefaultKeyBinding(mode='prompt', key='Ctrl-y', action_spec='PromptCopySelected'),
    DefaultKeyBinding(mode='prompt', key='Ctrl-Home', action_spec='PromptSuggestFirst|PromptHome'),
    DefaultKeyBinding(mode='prompt', key='Ctrl-End', action_spec='PromptSuggestLast|PromptEnd'),
    DefaultKeyBinding(mode='qreplace', key='y', action_spec='QueryReplaceYes'),
    DefaultKeyBinding(mode='qreplace', key='Y', action_spec='QueryReplaceYes'),
    DefaultKeyBinding(mode='qreplace', key='Enter', action_spec='QueryReplaceYes'),
    DefaultKeyBinding(mode='qreplace', key='n', action_spec='QueryReplaceNo'),
    DefaultKeyBinding(mode='qreplace', key='N', action_spec='QueryReplaceNo'),
    DefaultKeyBinding(mode='qreplace', key='a', action_spec='QueryReplaceAll'),
    DefaultKeyBinding(mode='qreplace', key='A', action_spec='QueryReplaceAll'),
    DefaultKeyBinding(mode='qreplace', key='l', action_spec='QueryReplaceLast'),
    DefaultKeyBinding(mode='qreplace', key='L', action_spec='QueryReplaceLast'),
    DefaultKeyBinding(mode='qreplace', key='q', action_spec='QueryReplaceQuit'),
    DefaultKeyBinding(mode='qreplace', key='Q', action_spec='QueryReplaceQuit'),
    DefaultKeyBinding(mode='qreplace', key='Esc', action_spec='QueryReplaceQuit'),
)


# Editor-internal confirmation bindings are host policy only.  They are not
# exposed as plugin-owned defaults because they guard delayed privileged UI.
INTERNAL_ONLY_KEY_BINDINGS: tuple[DefaultKeyBinding, ...] = (
    DefaultKeyBinding(mode='openurl', key='y', action_spec='OpenUrlYes'),
    DefaultKeyBinding(mode='openurl', key='Y', action_spec='OpenUrlYes'),
    DefaultKeyBinding(mode='openurl', key='Enter', action_spec='OpenUrlYes'),
    DefaultKeyBinding(mode='openurl', key='n', action_spec='OpenUrlNo'),
    DefaultKeyBinding(mode='openurl', key='N', action_spec='OpenUrlNo'),
    DefaultKeyBinding(mode='openurl', key='Esc', action_spec='OpenUrlNo'),
    DefaultKeyBinding(mode='openurl', key='c', action_spec='OpenUrlCopy'),
    DefaultKeyBinding(mode='openurl', key='C', action_spec='OpenUrlCopy'),
)


DEFAULT_KEY_BINDINGS: tuple[DefaultKeyBinding, ...] = (
    CORE_MIRRORED_KEY_BINDINGS + INTERNAL_ONLY_KEY_BINDINGS
)


# The minimal ``Editor`` embed historically installs only the modal rows needed
# to finish internal prompt/confirmation loops without loading product plugins.
# The full CLI/TUI startup installs every row above before plugin evaluation.
_EMBED_BOOTSTRAP_KEYS: frozenset[tuple[str, str]] = frozenset({
    ('openurl', 'C'),
    ('openurl', 'Enter'),
    ('openurl', 'Esc'),
    ('openurl', 'N'),
    ('openurl', 'Y'),
    ('openurl', 'c'),
    ('openurl', 'n'),
    ('openurl', 'y'),
    ('prompt', 'Alt-DownArrow'),
    ('prompt', 'Alt-UpArrow'),
    ('prompt', 'Ctrl-End'),
    ('prompt', 'Ctrl-Home'),
    ('prompt', 'Ctrl-y'),
    ('prompt', 'DownArrow'),
    ('prompt', 'PageDown'),
    ('prompt', 'PageUp'),
    ('prompt', 'UpArrow'),
    ('qreplace', 'A'),
    ('qreplace', 'Enter'),
    ('qreplace', 'Esc'),
    ('qreplace', 'L'),
    ('qreplace', 'N'),
    ('qreplace', 'Q'),
    ('qreplace', 'Y'),
    ('qreplace', 'a'),
    ('qreplace', 'l'),
    ('qreplace', 'n'),
    ('qreplace', 'q'),
    ('qreplace', 'y'),
})


def _install(keymap: "Keymap", rows: Iterable[DefaultKeyBinding]) -> None:
    for row in rows:
        keymap.bind(
            row.key,
            row.action_spec,
            mode=(None if row.mode == "global" else row.mode),
            script_context=False,
        )


def install_embed_bootstrap_keybindings(keymap: "Keymap") -> None:
    """Install only internal rows required by a minimal headless embed."""

    _install(
        keymap,
        (row for row in DEFAULT_KEY_BINDINGS if (row.mode, row.key) in _EMBED_BOOTSTRAP_KEYS),
    )


def install_default_keybindings(keymap: "Keymap") -> None:
    """Install the complete trusted CLI/TUI default keymap."""

    _install(keymap, DEFAULT_KEY_BINDINGS)


__all__ = [
    "CORE_MIRRORED_KEY_BINDINGS",
    "DEFAULT_KEY_BINDINGS",
    "DefaultKeyBinding",
    "INTERNAL_ONLY_KEY_BINDINGS",
    "install_default_keybindings",
    "install_embed_bootstrap_keybindings",
]
