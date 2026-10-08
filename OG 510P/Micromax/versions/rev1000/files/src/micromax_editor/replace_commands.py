from __future__ import annotations

from .replace_plan import ReplacePlan


def _reject_unknown_replace_flags(
    ed: "Editor", action_name: str, flag_args: list[str], allowed: set[str]
) -> bool:
    unknown = [flag for flag in flag_args if flag not in allowed]
    if not unknown:
        return False
    ed.message(f"{action_name}: unknown flag: {unknown[0]}")
    return True


def _occurrence_label(n: int) -> str:
    return "occurrence" if int(n) == 1 else "occurrences"


def _replace_plan_for_current_buffer(
    ed: "Editor",
    search: str,
    value: str,
    *,
    replace_all: bool,
    literal: bool,
    sample_limit: int = 3,
) -> ReplacePlan:
    return ed.replace_plan(
        search,
        value,
        replace_all=replace_all,
        literal=literal,
        sample_limit=sample_limit,
    )


def _quote_preview(value: str, *, limit: int = 24) -> str:
    text = str(value).replace("\n", "\\n")
    if len(text) > limit:
        text = text[: max(0, limit - 1)] + "…"
    return '"' + text.replace('"', '\\"') + '"'


def _replace_preview_message(action_name: str, plan: ReplacePlan) -> str:
    if not plan.ok:
        return f"{action_name}: {plan.error}"
    head = f"{action_name}: would replace {plan.count} {_occurrence_label(plan.count)}"
    if not plan.matches:
        return head
    first = plan.matches[0]
    sample = (
        f"first {first.line + 1}:{first.col} "
        f"{_quote_preview(first.old)} -> {_quote_preview(first.new)}"
    )
    more = max(0, int(plan.count) - 1)
    if more:
        sample += f" (+{more} more)"
    return f"{head}; {sample}"


def c_replace(ed: "Editor", args: list[str]) -> bool:
    if len(args) < 2:
        ed.message("usage: replace SEARCH VALUE [-a] [-l]")
        return False

    search = args[0]
    value = args[1]
    flag_args = list(args[2:])
    flags = set(flag_args)
    replace_all = "-a" in flags
    literal = "-l" in flags
    action_name = "replaceall" if replace_all else "replace"
    if _reject_unknown_replace_flags(ed, action_name, flag_args, {"-a", "-l"}):
        return False

    # Protected buffers (help/docs) should reject edits.
    try:
        if hasattr(ed, "is_protected_buffer") and ed.is_protected_buffer():
            ed.message(f"{action_name}: read-only buffer")
            return False
    except Exception:
        pass

    eb = ed.cur()
    before = ed._snapshot_undo_buffer_state(eb)
    plan = _replace_plan_for_current_buffer(
        ed,
        search,
        value,
        replace_all=replace_all,
        literal=literal,
    )
    if not plan.ok or plan.new_text is None:
        ed.message(f"{action_name}: {plan.error}")
        return False

    eb.buf.set_text(plan.new_text)
    after = ed._snapshot_undo_buffer_state(eb)
    ed._record_undo_snapshot(eb, before, after, action_name)
    try:
        ed._note_buffer_changed(eb)
    except Exception:
        pass
    if replace_all:
        ed.message(f"replaceall: replaced {plan.count} {_occurrence_label(plan.count)}")
    else:
        ed.message(f"replace: replaced {plan.count} {_occurrence_label(plan.count)} from cursor")
    return True


def c_replacepreview(ed: "Editor", args: list[str]) -> bool:
    if len(args) < 2:
        ed.message("usage: replacepreview SEARCH VALUE [-a] [-l]")
        return False
    search = args[0]
    value = args[1]
    flag_args = list(args[2:])
    flags = set(flag_args)
    replace_all = "-a" in flags
    literal = "-l" in flags
    if _reject_unknown_replace_flags(ed, "replacepreview", flag_args, {"-a", "-l"}):
        return False
    plan = _replace_plan_for_current_buffer(
        ed,
        search,
        value,
        replace_all=replace_all,
        literal=literal,
    )
    ed.message(_replace_preview_message("replacepreview", plan))
    return bool(plan.ok)


def c_replaceall(ed: "Editor", args: list[str]) -> bool:
    # micro has replaceall as a convenience wrapper for replace -a.
    if len(args) < 2:
        ed.message("usage: replaceall SEARCH VALUE [-l]")
        return False
    return c_replace(ed, [args[0], args[1], "-a", *args[2:]])


def c_qreplace(ed: "Editor", args: list[str]) -> bool:
    """Interactive (confirming) replace loop.

    This mirrors micro's "replace then confirm" workflow: it finds matches
    from the cursor and asks the user to confirm each replacement.
    """
    if len(args) < 2:
        ed.message("usage: qreplace SEARCH VALUE [-l]")
        return False
    flag_args = list(args[2:])
    flags = set(flag_args)
    if _reject_unknown_replace_flags(ed, "qreplace", flag_args, {"-l"}):
        return False
    literal = "-l" in flags
    return bool(ed.begin_query_replace(args[0], args[1], literal=literal))
