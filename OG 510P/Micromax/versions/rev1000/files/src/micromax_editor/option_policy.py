from __future__ import annotations

"""Policy for option writes that originate from lower-authority scripts.

Capability options are not the only knobs that can change host authority.
Several ordinary-looking options decide which external programs are launched,
where persistence files are read/written, or whether save-conflict guards are
active.  Script-created commands, keybindings, hooks, timers, and macros may
outlive the script call that created them, so these options need a shared
mutation policy rather than one-off command checks.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class ScriptOptionPolicy:
    """Result of checking whether a script may mutate an option."""

    allowed: bool
    reason: str = ""


@dataclass(frozen=True)
class ScriptOptionReadPolicy:
    """Result of checking whether a script may inspect an option value."""

    allowed: bool
    reason: str = ""


# Exact non-capability options that alter host authority, persistence paths, or
# save safety policy.  Aliases are resolved before this set is checked.
SCRIPT_PROTECTED_OPTIONS: frozenset[str] = frozenset(
    {
        # External clipboard / terminal escape integration.  A script should
        # not be able to seed a command override that a later user copy/paste
        # executes outside script authority.
        "clipboard",
        "clipboard.osc52",
        "clipboard.osc52.max",
        "clipboard.external.cmd",
        "clipboard.external.args",
        "clipboard.external.timeout",
        "clipboard.external.inputmax",
        "clipboard.external.outputmax",
        "clipboard.external.readcmd",
        "clipboard.external.readargs",
        "clipboard.external.readtimeout",
        "clipboard.external.import",
        # URL-opening policy.  The capability bit is protected separately; the
        # confirmation bit is also user policy.
        "open-url.confirm",
        # Persistence is a host filesystem surface.  Scripts may use structured
        # persistence only when the host exposes it, but should not redirect or
        # enable editor-owned persistence as a side effect.
        "recent.persist",
        "recent.file",
        "history.persist",
        "history.file",
        "history.limit",
        "savecursor",
        "savecursor.file",
        "persist.atomic",
        "persist.fsync",
        "persist.maxbytes",
        # Save authority and data-loss protections.  Granting cap.fs-save should
        # not also let a script lower stale-write checks or turn on automatic
        # write/parent-creation behavior for later ambient editor operations.
        "autosave",
        "mkparents",
        "readonly",
        "save.atomic",
        "save.checkexternal",
        "save.checkexternal.hashmax",
        "save.preserveperm",
        "save.fsync",
        # Undo retention is a user recovery policy.  A lower-authority script
        # must not silently shrink it and retire trusted history on the next
        # edit, although reading the numeric limit is harmless.
        "undobytes",
    }
)


# Option values can carry host authority, local paths, external commands, or
# data-loss policy.  Names/docs are public enough for discovery; the live values
# of these options are not ambient script-visible state.
SCRIPT_PROTECTED_READ_OPTIONS: frozenset[str] = frozenset(
    SCRIPT_PROTECTED_OPTIONS - {"undobytes"}
)


def script_option_read_policy(canonical_name: str, *, capability_enabled: bool = False) -> ScriptOptionReadPolicy:
    """Return whether script-originated code may read an option value.

    Capability bits and host-adjacent knobs are intentionally treated as
    protected values.  Scripts can probe enabled host surfaces through
    ``host.feature?``/``host.capabilities``; reading the raw configured roots,
    external commands, persistence files, or save-safety flags requires the
    explicit ``cap.option-read`` override.
    """

    name = str(canonical_name or "")
    if bool(capability_enabled):
        return ScriptOptionReadPolicy(True, "")
    if name.startswith("cap."):
        return ScriptOptionReadPolicy(False, "capability option")
    if name in SCRIPT_PROTECTED_READ_OPTIONS:
        return ScriptOptionReadPolicy(False, "protected option")
    return ScriptOptionReadPolicy(True, "")


def script_option_policy(canonical_name: str) -> ScriptOptionPolicy:
    """Return whether script-originated code may mutate ``canonical_name``.

    ``canonical_name`` must already have aliases resolved.  The function keeps
    message categories stable: capability failures still say "capability
    option", while adjacent unsafe knobs say "protected option".
    """

    name = str(canonical_name or "")
    if name.startswith("cap."):
        return ScriptOptionPolicy(False, "capability option")
    if name in SCRIPT_PROTECTED_OPTIONS:
        return ScriptOptionPolicy(False, "protected option")
    return ScriptOptionPolicy(True, "")
