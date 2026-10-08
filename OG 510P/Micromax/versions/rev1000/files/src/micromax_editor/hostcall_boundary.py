from __future__ import annotations

"""Small stack/capability guards for editor hostcalls.

Capability-denied hostcalls should fail before consuming their operation
arguments.  That keeps denied host operations inspectable from scripts and
matches the newer readonly edit-boundary behavior.
"""

import math
from typing import Any, Type

from micromax.host_limits import utf8_size
from micromax.vm import MicromaxError, Quotation, Word


# Conservative preflight defaults for hostcall-visible editor model builders.
# These limits bound *input-controlled traversal* before a screen/docs/prompt
# model walks host-owned state or allocates row payloads.  The VM's shared
# hostcall result budget still owns output size after a helper returns.
DEFAULT_EDITOR_MODEL_MAX_LINES = 1000
DEFAULT_EDITOR_MODEL_MAX_COLS = 1000
DEFAULT_EDITOR_MODEL_MAX_CELLS = 262_144
DEFAULT_EDITOR_MODEL_MAX_WIDTH = 4096
DEFAULT_EDITOR_QUERY_MAX_BYTES = 4096
DEFAULT_EDITOR_SCAN_MAX_ROWS = 512
DEFAULT_FS_READ_MAX_BYTES = 1_000_000
DEFAULT_FS_READ_TIMEOUT_SECONDS = 5.0
DEFAULT_FS_LIST_MAX_ROWS = 500
DEFAULT_FS_LIST_TIMEOUT_SECONDS = 5.0
DEFAULT_FS_STAT_TIMEOUT_SECONDS = 5.0
DEFAULT_PROJECT_FILE_MAX_FILES = 4096
DEFAULT_PROJECT_FILE_MAX_DIRS = 2048
DEFAULT_PROJECT_FILE_MAX_DEPTH = 32
DEFAULT_PROJECT_FILE_MAX_ENTRIES = 32768
DEFAULT_PROJECT_FILE_MAX_PATH_BYTES = 1_048_576
DEFAULT_PROJECT_FILE_TIMEOUT_SECONDS = 1.0
DEFAULT_FILE_WRITE_TIMEOUT_SECONDS = 5.0
DEFAULT_FILE_FRESHNESS_TIMEOUT_SECONDS = 5.0
DEFAULT_FILE_MKPARENTS_TIMEOUT_SECONDS = 5.0
DEFAULT_SOURCE_LOAD_MAX_BYTES = 262_144
DEFAULT_SOURCE_EVAL_STEP_BUDGET = 50_000
DEFAULT_SOURCE_LOAD_MAX_DEPTH = 32
DEFAULT_SOURCE_LOAD_MAX_TOTAL_BYTES = 1_048_576
DEFAULT_SHELL_COMMAND_MAX_BYTES = 4096
DEFAULT_SHELL_OUTPUT_MAX_BYTES = 262_144
DEFAULT_SHELL_TIMEOUT_SECONDS = 5.0


def _int_limit(vm: Any, attr: str, default: int) -> int:
    try:
        value = int(getattr(vm, attr, default))
    except Exception:
        return int(default)
    return int(value)


def _utf8_size(value: str, *, stop_after: int | None = None) -> int:
    return utf8_size(str(value), stop_after=stop_after)


def _float_limit(vm: Any, attr: str, default: float) -> float:
    raw = getattr(vm, attr, default)
    if isinstance(raw, bool):
        return float(default)
    try:
        value = float(raw)
    except Exception:
        return float(default)
    return float(value)


def require_editor_query_budget(vm: Any, word: str, query: str) -> None:
    """Reject oversized free-text query strings before host-state scans.

    Query-shaped editor hostcalls are observational, but broad docs/help/prompt
    and inventory helpers can scan host-owned state before the VM's post-call
    result budget sees the returned rows.  The limit is VM-tunable and byte-based
    so embeddings can reason about memory pressure consistently with other
    hostcall resource budgets.  Non-positive values intentionally disable this
    specific cap for hosts that supply a stronger external boundary.
    """

    limit = _int_limit(vm, "editor_hostcall_query_max_bytes", DEFAULT_EDITOR_QUERY_MAX_BYTES)
    if limit <= 0:
        return
    size = _utf8_size(query, stop_after=limit)
    if size > limit:
        raise MicromaxError(
            f"{word}: query {size} bytes exceeds editor query input budget {limit}"
        )


def peek_query_arg(vm: Any, word: str, *, depth: int = 1) -> str:
    """Return a free-text query argument after type and byte-budget preflight."""

    query = peek_str_arg(vm, word, depth=depth)
    require_editor_query_budget(vm, word, query)
    return str(query)


def pop_query_arg(vm: Any, word: str) -> str:
    """Pop a free-text query argument only after query-budget preflight."""

    query = peek_query_arg(vm, word)
    del vm.stack[-1:]
    return str(query)


def effective_editor_scan_max_rows(vm: Any) -> int | None:
    """Return the VM-tunable broad editor scan/candidate row budget.

    Query length and post-call result budgets do not cap how much host state a
    row builder may walk before it can return.  This limit gives embeddings a
    small, executable pre/post traversal dial for broad palette, picker, docs,
    and filesystem listing surfaces.  Non-positive values intentionally disable
    the cap for hosts that provide a stronger external boundary.
    """

    limit = _int_limit(vm, "editor_hostcall_scan_max_rows", DEFAULT_EDITOR_SCAN_MAX_ROWS)
    if limit <= 0:
        return None
    return int(limit)


def effective_fs_list_max_rows(vm: Any) -> int | None:
    """Return the VM-tunable filesystem-list row budget.

    ``ed.fs-list`` is an observational hostcall, but a large directory can still
    consume memory/CPU before the VM inspects the returned rows.  Keep the
    default close to the historical fixed list cap while making it visible to
    embedders alongside the other hostcall resource limits.
    """

    limit = _int_limit(vm, "editor_hostcall_fs_list_max_rows", DEFAULT_FS_LIST_MAX_ROWS)
    if limit <= 0:
        return None
    return int(limit)


def effective_fs_read_max_bytes(vm: Any) -> int | None:
    """Return the VM-tunable filesystem-read byte budget.

    ``ed.fs-read`` is already capability-gated and returns an ``ok text err``
    tuple for ordinary filesystem failures.  Its byte ceiling is still a hostcall
    boundary, not an option exposed to scripts, so embeddings tune it on the VM
    object.  Non-positive values intentionally disable the pre-read/final-read
    byte cap for hosts that provide their own stronger containment.
    """

    limit = _int_limit(vm, "editor_hostcall_fs_read_max_bytes", DEFAULT_FS_READ_MAX_BYTES)
    if limit <= 0:
        return None
    return int(limit)



def effective_fs_read_timeout_seconds(vm: Any) -> float:
    """Return the VM-tunable wall-clock timeout for ``ed.fs-read``.

    Byte budgets keep ordinary reads from materializing unbounded text, but file
    open/fstat/read work can still block on unusual or remote filesystems after
    capability preflight.  A positive timeout runs the contained read through a
    killable worker.  Non-positive values intentionally disable this worker
    boundary for hosts that provide stronger external filesystem containment.
    """

    return _optional_positive_float_limit(
        vm,
        "editor_hostcall_fs_read_timeout_seconds",
        DEFAULT_FS_READ_TIMEOUT_SECONDS,
    )


def effective_fs_list_timeout_seconds(vm: Any) -> float:
    """Return the VM-tunable wall-clock timeout for ``ed.fs-list``.

    Row budgets keep large directories from materializing unbounded result lists,
    but directory open/scandir/stat work can still block on unusual or remote
    filesystems.  A positive timeout runs listing through a killable worker.
    Non-positive values intentionally disable this worker boundary for hosts
    that provide stronger external filesystem containment.
    """

    return _optional_positive_float_limit(
        vm,
        "editor_hostcall_fs_list_timeout_seconds",
        DEFAULT_FS_LIST_TIMEOUT_SECONDS,
    )


def _positive_int_limit(vm: Any, attr: str, default: int) -> int:
    """Return a finite positive host limit; malformed/disabled values fail safe."""

    value = _int_limit(vm, attr, default)
    return int(value) if value > 0 else int(default)


def _positive_float_limit(vm: Any, attr: str, default: float) -> float:
    """Return a finite positive host timeout; malformed/disabled values fail safe."""

    value = _float_limit(vm, attr, default)
    if not math.isfinite(value) or value <= 0:
        return float(default)
    return float(value)


def _optional_positive_float_limit(vm: Any, attr: str, default: float) -> float:
    """Return a finite timeout while preserving an explicit disable value.

    Several filesystem workers intentionally let embeddings set a non-positive
    timeout to disable Micromax's reference process boundary.  NaN and infinity
    are not disable values: they make deadline arithmetic unreliable or
    unbounded, so malformed/non-finite values fail closed to the documented
    finite default.
    """

    value = _float_limit(vm, attr, default)
    if not math.isfinite(value):
        return float(default)
    if value <= 0:
        return 0.0
    return float(value)


def effective_project_file_max_files(vm: Any) -> int:
    return _positive_int_limit(vm, "editor_project_file_max_files", DEFAULT_PROJECT_FILE_MAX_FILES)


def effective_project_file_max_dirs(vm: Any) -> int:
    return _positive_int_limit(vm, "editor_project_file_max_dirs", DEFAULT_PROJECT_FILE_MAX_DIRS)


def effective_project_file_max_depth(vm: Any) -> int:
    return _positive_int_limit(vm, "editor_project_file_max_depth", DEFAULT_PROJECT_FILE_MAX_DEPTH)


def effective_project_file_max_entries(vm: Any) -> int:
    return _positive_int_limit(vm, "editor_project_file_max_entries", DEFAULT_PROJECT_FILE_MAX_ENTRIES)


def effective_project_file_max_path_bytes(vm: Any) -> int:
    return _positive_int_limit(
        vm,
        "editor_project_file_max_path_bytes",
        DEFAULT_PROJECT_FILE_MAX_PATH_BYTES,
    )


def effective_project_file_timeout_seconds(vm: Any) -> float:
    return _positive_float_limit(
        vm,
        "editor_project_file_timeout_seconds",
        DEFAULT_PROJECT_FILE_TIMEOUT_SECONDS,
    )


def effective_fs_stat_timeout_seconds(vm: Any) -> float:
    """Return the VM-tunable wall-clock timeout for ``ed.fs-stat``.

    Filesystem metadata/open/fstat calls can still block on unusual or remote
    filesystems after capability and byte/row preflight.  A positive timeout
    runs stat through a killable worker process.  Non-positive values
    intentionally disable this worker boundary for hosts that provide stronger
    external filesystem containment.
    """

    return _optional_positive_float_limit(
        vm,
        "editor_hostcall_fs_stat_timeout_seconds",
        DEFAULT_FS_STAT_TIMEOUT_SECONDS,
    )


def effective_file_freshness_timeout_seconds(vm: Any) -> float:
    """Return the VM-tunable wall-clock timeout for save freshness preflight.

    Positive values run save-time stat/hash freshness capture in a killable
    worker process.  Non-positive values disable this reference boundary for
    lightweight embeddings or hosts that provide stronger filesystem isolation.
    Hot stat-only status rendering intentionally does not use this timeout; the
    editor applies it at save/open-sync boundaries where a worker cost is
    justified by data-loss protection.
    """

    if vm is None or not hasattr(vm, "editor_file_freshness_timeout_seconds"):
        return 0.0
    return _optional_positive_float_limit(
        vm,
        "editor_file_freshness_timeout_seconds",
        DEFAULT_FILE_FRESHNESS_TIMEOUT_SECONDS,
    )


def effective_file_mkparents_timeout_seconds(vm: Any) -> float:
    """Return the VM-tunable wall-clock timeout for save parent creation.

    Positive values run ``mkparents`` directory creation in a killable worker.
    Non-positive values disable this reference boundary for hosts with stronger
    containment or embeddings that intentionally do not offer ``mkparents``.
    """

    if vm is None or not hasattr(vm, "editor_file_mkparents_timeout_seconds"):
        return 0.0
    return _optional_positive_float_limit(
        vm,
        "editor_file_mkparents_timeout_seconds",
        DEFAULT_FILE_MKPARENTS_TIMEOUT_SECONDS,
    )


def effective_file_write_timeout_seconds(vm: Any) -> float:
    """Return the VM-tunable wall-clock timeout for atomic editor writes.

    Positive values run the atomic temp-file commit in a killable worker process
    and trigger best-effort temp cleanup on timeout.  Non-positive values disable
    this reference boundary for hosts that provide stronger external filesystem
    containment.  Direct/non-atomic writes intentionally ignore this timeout
    because killing them can leave the real target partially written.
    """

    # Plain ``Editor()`` instances used by tests and lightweight embeddings do
    # not install hostcall VM knobs.  Avoid spawning one process per ordinary
    # unit-test save unless the bridge or embedding has explicitly installed
    # the write timeout attribute.
    if vm is None or not hasattr(vm, "editor_file_write_timeout_seconds"):
        return 0.0
    return _optional_positive_float_limit(
        vm,
        "editor_file_write_timeout_seconds",
        DEFAULT_FILE_WRITE_TIMEOUT_SECONDS,
    )


def effective_source_load_max_bytes(vm: Any) -> int | None:
    """Return the VM-tunable executable source-load byte budget.

    ``ed.require`` and script-context core ``include``/``require``/``reload``
    cross from observational file access into executable authority.  Keep the
    source-size dial separate from ``ed.fs-read`` so embedders can allow larger
    text observation than executable script loading.  Non-positive values
    intentionally disable this cap for hosts with stronger external containment.
    """

    limit = _int_limit(vm, "editor_source_load_max_bytes", DEFAULT_SOURCE_LOAD_MAX_BYTES)
    if limit <= 0:
        return None
    return int(limit)


def effective_source_eval_step_budget(vm: Any) -> int | None:
    """Return the VM-tunable nested source evaluation step budget.

    Size caps stop a huge source file from being read, but a small file can still
    contain an expensive or nonterminating script.  This returns a per-loaded
    source ``VM.eval(..., step_budget=...)`` budget for editor-owned executable
    loads.  Non-positive values intentionally leave nested evaluation unbounded.
    """

    limit = _int_limit(vm, "editor_source_eval_step_budget", DEFAULT_SOURCE_EVAL_STEP_BUDGET)
    if limit <= 0:
        return None
    return int(limit)


def effective_source_load_max_depth(vm: Any) -> int | None:
    """Return the VM-tunable executable source dependency-depth budget.

    Per-file size limits do not stop a small source from recursively loading many
    small files.  This cap counts the active executable load stack for
    ``ed.require`` and script-context core ``include``/``require``/``reload``.
    Non-positive values intentionally disable this cap.
    """

    limit = _int_limit(vm, "editor_source_load_max_depth", DEFAULT_SOURCE_LOAD_MAX_DEPTH)
    if limit <= 0:
        return None
    return int(limit)


def effective_source_load_max_total_bytes(vm: Any) -> int | None:
    """Return the VM-tunable executable source dependency-graph byte budget.

    This is a cumulative byte ceiling across one source-load graph, separate from
    the per-file executable source cap.  It prevents many individually small
    dependencies from turning one hostcall/script load into an unbounded source
    ingest.  Non-positive values intentionally disable this cap.
    """

    limit = _int_limit(vm, "editor_source_load_max_total_bytes", DEFAULT_SOURCE_LOAD_MAX_TOTAL_BYTES)
    if limit <= 0:
        return None
    return int(limit)


def require_shell_command_budget(vm: Any, word: str, command: str) -> None:
    """Reject oversized shell command strings before process creation.

    ``ed.shell`` is capability-gated, but command text is still hostcall input
    that can drive shell parsing, environment expansion, and child setup before
    a post-call result budget sees anything.  Non-positive values intentionally
    disable only this command-string cap.
    """

    limit = _int_limit(vm, "editor_shell_command_max_bytes", DEFAULT_SHELL_COMMAND_MAX_BYTES)
    if limit <= 0:
        return
    size = _utf8_size(command)
    if size > limit:
        raise MicromaxError(
            f"{word}: command {size} bytes exceeds shell command input budget {limit}"
        )


def peek_shell_command_arg(vm: Any, word: str, *, depth: int = 1) -> str:
    """Return a shell command argument after type and byte-budget preflight."""

    command = peek_str_arg(vm, word, depth=depth)
    require_shell_command_budget(vm, word, command)
    return str(command)


def pop_shell_command_arg(vm: Any, word: str) -> str:
    """Pop a shell command only after type and input-budget preflight."""

    command = peek_shell_command_arg(vm, word)
    del vm.stack[-1:]
    return str(command)


def effective_shell_output_max_bytes(vm: Any) -> int | None:
    """Return the VM-tunable combined stdout/stderr byte budget for ``ed.shell``."""

    limit = _int_limit(vm, "editor_shell_output_max_bytes", DEFAULT_SHELL_OUTPUT_MAX_BYTES)
    if limit <= 0:
        return None
    return int(limit)


def effective_shell_timeout_seconds(vm: Any) -> float:
    """Return the VM-tunable wall-clock timeout for ``ed.shell``."""

    return _positive_float_limit(
        vm,
        "editor_shell_timeout_seconds",
        DEFAULT_SHELL_TIMEOUT_SECONDS,
    )


def _effective_dimension(value: int) -> int:
    # Existing editor model builders clamp negative sizes to zero.  Preserve
    # that harmless behavior while still rejecting huge positive dimensions.
    return max(0, int(value))


def _require_dimension_limit(vm: Any, word: str, *, label: str, value: int, attr: str, default: int) -> None:
    limit = _int_limit(vm, attr, default)
    effective = _effective_dimension(value)
    if limit > 0 and effective > limit:
        raise MicromaxError(
            f"{word}: {label} {int(value)} exceeds editor model input budget {limit}"
        )


def require_editor_model_budget(
    vm: Any,
    word: str,
    *,
    lines: int | None = None,
    cols: int | None = None,
    width: int | None = None,
) -> None:
    """Reject oversized editor model dimensions before host-state traversal.

    Screen/docs/help/prompt hostcalls are observational, but their row builders
    can walk host-owned state and allocate large payloads before the VM's shared
    post-call result budget gets a chance to reject the output.  This helper is
    deliberately small and VM-attribute-tunable so embeddings can raise, lower,
    or disable limits without creating a new registry layer.
    """

    if lines is not None:
        _require_dimension_limit(
            vm,
            word,
            label="lines",
            value=int(lines),
            attr="editor_hostcall_model_max_lines",
            default=DEFAULT_EDITOR_MODEL_MAX_LINES,
        )
    if cols is not None:
        _require_dimension_limit(
            vm,
            word,
            label="cols",
            value=int(cols),
            attr="editor_hostcall_model_max_cols",
            default=DEFAULT_EDITOR_MODEL_MAX_COLS,
        )
    if width is not None:
        _require_dimension_limit(
            vm,
            word,
            label="width",
            value=int(width),
            attr="editor_hostcall_model_max_width",
            default=DEFAULT_EDITOR_MODEL_MAX_WIDTH,
        )

    if lines is not None and cols is not None:
        area_limit = _int_limit(
            vm,
            "editor_hostcall_model_max_cells",
            DEFAULT_EDITOR_MODEL_MAX_CELLS,
        )
        area = _effective_dimension(int(lines)) * _effective_dimension(int(cols))
        if area_limit > 0 and area > area_limit:
            raise MicromaxError(
                f"{word}: screen area {area} exceeds editor model input budget {area_limit}"
            )


def peek_model_dimensions_arg(vm: Any, word: str) -> tuple[int, int]:
    """Return ``(lines, cols)`` after type and budget preflight."""

    lines = peek_int_arg(vm, word, depth=2)
    cols = peek_int_arg(vm, word, depth=1)
    require_editor_model_budget(vm, word, lines=lines, cols=cols)
    return int(lines), int(cols)


def pop_model_dimensions_arg(vm: Any, word: str) -> tuple[int, int]:
    """Pop ``(lines, cols)`` only after type and input-budget preflight."""

    lines, cols = peek_model_dimensions_arg(vm, word)
    del vm.stack[-2:]
    return int(lines), int(cols)


def peek_model_lines_arg(vm: Any, word: str, *, depth: int = 1) -> int:
    """Return a row-count argument after type and budget preflight."""

    lines = peek_int_arg(vm, word, depth=depth)
    require_editor_model_budget(vm, word, lines=lines)
    return int(lines)


def pop_model_lines_arg(vm: Any, word: str) -> int:
    """Pop a row-count argument only after type and input-budget preflight."""

    lines = peek_model_lines_arg(vm, word)
    del vm.stack[-1:]
    return int(lines)


def peek_model_width_arg(vm: Any, word: str, *, depth: int = 1) -> int:
    """Return a width argument after type and budget preflight."""

    width = peek_int_arg(vm, word, depth=depth)
    require_editor_model_budget(vm, word, width=width)
    return int(width)


def pop_model_width_arg(vm: Any, word: str) -> int:
    """Pop a width argument only after type and input-budget preflight."""

    width = peek_model_width_arg(vm, word)
    del vm.stack[-1:]
    return int(width)


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
