from __future__ import annotations

"""Small stack/capability guards for editor hostcalls.

Capability-denied hostcalls should fail before consuming their operation
arguments.  That keeps denied host operations inspectable from scripts and
matches the newer readonly edit-boundary behavior.
"""

from typing import Any, Type

from micromax.vm import MicromaxError, Quotation, Word


def require_option_enabled(
    ed: Any,
    option: str,
    message: str,
    *,
    error_cls: Type[Exception] = MicromaxError,
) -> None:
    """Raise ``error_cls(message)`` unless an editor option is truthy."""

    try:
        enabled = bool(ed.options.get(str(option)))
    except Exception:
        enabled = False
    if not enabled:
        raise error_cls(str(message))


def peek_stack_arg(vm: Any, word: str, *, depth: int = 1) -> Any:
    """Return the stack argument at ``depth`` without consuming it.

    ``depth=1`` is the top item, ``depth=2`` is one below the top, and so on.
    """

    if int(depth) <= 0:
        raise ValueError("depth must be positive")
    if len(vm.stack) < int(depth):
        raise MicromaxError(f"{word}: stack underflow")
    return vm.stack[-int(depth)]


def peek_str_arg(vm: Any, word: str, *, depth: int = 1) -> str:
    """Return a string argument without consuming it."""

    value = peek_stack_arg(vm, word, depth=depth)
    if not isinstance(value, str):
        raise MicromaxError(f"{word}: expected str, got {type(value).__name__}")
    return str(value)


def peek_int_arg(vm: Any, word: str, *, depth: int = 1) -> int:
    """Return an integer argument without consuming it."""

    value = peek_stack_arg(vm, word, depth=depth)
    if not isinstance(value, int):
        raise MicromaxError(f"{word}: expected int, got {type(value).__name__}")
    return int(value)


def peek_list_arg(vm: Any, word: str, *, depth: int = 1) -> list[Any]:
    """Return a list argument without consuming it."""

    value = peek_stack_arg(vm, word, depth=depth)
    if not isinstance(value, list):
        raise MicromaxError(f"{word}: expected list, got {type(value).__name__}")
    return value


def peek_quote_arg(vm: Any, word: str, *, depth: int = 1) -> Quotation:
    """Return a quotation argument without consuming it."""

    value = peek_stack_arg(vm, word, depth=depth)
    if not isinstance(value, Quotation):
        raise MicromaxError(f"{word}: expected quotation, got {type(value).__name__}")
    return value


def peek_xt_arg(vm: Any, word: str, *, depth: int = 1) -> Any:
    """Return an execution-token argument without consuming it."""

    value = peek_stack_arg(vm, word, depth=depth)
    if not isinstance(value, (Word, Quotation)):
        raise MicromaxError(f"{word}: expected execution token, got {type(value).__name__}")
    return value


def pop_str_arg(vm: Any, word: str) -> str:
    """Pop a string argument after preflighting its type."""

    peek_str_arg(vm, word)
    return str(vm.stack.pop())


def pop_int_arg(vm: Any, word: str) -> int:
    """Pop an integer argument after preflighting its type."""

    peek_int_arg(vm, word)
    return int(vm.stack.pop())


def pop_list_arg(vm: Any, word: str) -> list[Any]:
    """Pop a list argument after preflighting its type."""

    peek_list_arg(vm, word)
    return list(vm.stack.pop())


def pop_quote_arg(vm: Any, word: str) -> Quotation:
    """Pop a quotation argument after preflighting its type."""

    peek_quote_arg(vm, word)
    return vm.stack.pop()


def pop_xt_arg(vm: Any, word: str) -> Any:
    """Pop an execution-token argument after preflighting its type."""

    peek_xt_arg(vm, word)
    return vm.stack.pop()
