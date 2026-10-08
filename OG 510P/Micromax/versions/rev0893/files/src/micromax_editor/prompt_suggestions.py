from __future__ import annotations

from typing import Any


ROOT_COMMAND_ROW_METHODS: dict[str, tuple[str, dict[str, object]]] = {
    "jumpback": ("_prompt_jump_navigation_command_row", {"direction": "back"}),
    "jumpforward": ("_prompt_jump_navigation_command_row", {"direction": "forward"}),
    "jumps": ("_prompt_jumps_command_row", {}),
    "jumppick": ("_prompt_jumppick_command_row", {}),
    "plugin": ("_prompt_plugin_root_command_row", {}),
    "macro": ("_prompt_macro_root_command_row", {}),
    "pluginpick": ("_prompt_pluginpick_command_row", {}),
    "recent": ("_prompt_recent_command_summary_row", {}),
    "recentpick": ("_prompt_recentpick_command_row", {}),
    "recentdirpick": ("_prompt_recentdirpick_command_row", {}),
    "showrecent": ("_prompt_showrecent_command_row", {}),
    "showrecentgroups": ("_prompt_showrecentgroups_command_row", {}),
    "showrecentdir": ("_prompt_showrecentdir_command_row", {}),
    "showrecentdirgroups": ("_prompt_showrecentdirgroups_command_row", {}),
    "showjump": ("_prompt_showjump_command_row", {}),
    "showjumpgroups": ("_prompt_showjumpgroups_command_row", {}),
    "showhelpheading": ("_prompt_showhelpheading_command_row", {}),
    "showhelplink": ("_prompt_showhelplink_command_row", {}),
    "helpfollow": ("_prompt_helpfollow_command_row", {}),
    "helpback": ("_prompt_helpback_command_row", {}),
    "helpforward": ("_prompt_helpforward_command_row", {}),
    "helpresume": ("_prompt_helpresume_command_row", {}),
    "helphistory": ("_prompt_helphistory_command_row", {}),
    "helpjump": ("_prompt_helpjump_command_row", {}),
    "helpoutlinepick": ("_prompt_helpoutlinepick_command_row", {}),
    "helpnavpick": ("_prompt_helpnavpick_command_row", {}),
    "helplinkpick": ("_prompt_helplinkpick_command_row", {}),
    "helpprune": ("_prompt_helpprune_command_row", {}),
    "helplinkcopy": ("_prompt_helplinkcopy_command_row", {}),
    "helpcopylink": ("_prompt_helplinkcopy_command_row", {}),
    "urlopen": ("_prompt_urlopen_command_row", {}),
    "openurl": ("_prompt_urlopen_command_row", {}),
    "urlcopy": ("_prompt_urlcopy_command_row", {}),
    "showstatus": ("_prompt_showstatus_command_row", {}),
    "showkeymodes": ("_prompt_showkeymodes_command_row", {}),
    "showkeymode": ("_prompt_showkeymode_command_row", {}),
    "showcmd": ("_prompt_showcmd_command_row", {}),
    "showaction": ("_prompt_showaction_command_row", {}),
    "showword": ("_prompt_showword_command_row", {}),
    "buffers": ("_prompt_buffers_command_row", {}),
    "buffer": ("_prompt_buffer_command_row", {}),
    "showbuffer": ("_prompt_showbuffer_command_row", {}),
    "bufferpick": ("_prompt_bufferpick_command_row", {}),
    "marks": ("_prompt_marks_command_row", {}),
    "mark": ("_prompt_mark_command_row", {}),
    "markjump": ("_prompt_mark_command_row", {}),
    "showmark": ("_prompt_showmark_command_row", {}),
    "showmacro": ("_prompt_showmacro_command_row", {}),
    "markpick": ("_prompt_markpick_command_row", {}),
    "showoption": ("_prompt_showoption_command_row", {}),
    "showhook": ("_prompt_showhook_command_row", {}),
    "showhooks": ("_prompt_showhooks_command_row", {}),
    "showbindings": ("_prompt_showbindings_command_row", {}),
    "showkey": ("_prompt_showkey_command_row", {}),
    "whichkey": ("_prompt_whichkey_command_row", {}),
    "showdoc": ("_prompt_showdoc_command_row", {}),
    "showtopic": ("_prompt_showtopic_command_row", {}),
    "showhelpnav": ("_prompt_showhelpnav_command_row", {}),
    "showplugins": ("_prompt_showplugins_command_row", {}),
    "showplugin": ("_prompt_showplugin_command_row", {}),
    "save": ("_prompt_save_command_row", {}),
    "saveas": ("_prompt_save_command_row", {"saveas": True}),
}

ROOT_SECTION_SUMMARY_NOUNS = {
    "showtopics": "topic",
    "showoptiongroups": "option",
    "showbuffergroups": "buffer",
    "showmarkgroups": "mark",
    "showpalettegroups": "item",
    "showdocs": "doc",
    "showbindingmodes": "binding",
}

ROOT_COMMAND_ARG_ROW_METHODS = {
    "quit": "_prompt_quit_command_row",
    "quit!": "_prompt_quit_command_row",
    "undo": "_prompt_undo_redo_command_row",
    "redo": "_prompt_undo_redo_command_row",
    "close": "_prompt_close_command_row",
    "close!": "_prompt_close_command_row",
    "closeall": "_prompt_close_command_row",
    "closeall!": "_prompt_close_command_row",
    "only": "_prompt_close_command_row",
    "only!": "_prompt_close_command_row",
}


def root_command_specific_row(editor: Any, *, raw: str, insert: str) -> list[str] | None:
    """Return a specialized root-command prompt row, when one is registered."""

    method_spec = ROOT_COMMAND_ROW_METHODS.get(raw)
    if method_spec is not None:
        method_name, kwargs = method_spec
        return getattr(editor, method_name)(insert, **kwargs)
    noun = ROOT_SECTION_SUMMARY_NOUNS.get(raw)
    if noun is not None:
        return editor._prompt_section_summary_command_row(insert, cmd=raw, noun=noun)
    method_name = ROOT_COMMAND_ARG_ROW_METHODS.get(raw)
    if method_name is not None:
        return getattr(editor, method_name)(insert, command=raw)
    return None


def prompt_commandish_suggestion_rows(
    editor: Any,
    *,
    cmd: str,
    toks: list[str],
    tok_i: int,
    candidates: list[str],
) -> list[list[str]]:
    self = editor
    rows: list[list[str]] = []
    recent_rows_by_index: dict[str, list[object]] = {}
    if tok_i == 1 and cmd == "recent":
        for item in self.recent_inventory_rows():
            try:
                recent_rows_by_index[str(int(item[0]))] = list(item)
            except Exception:
                continue
    docs_batch = self._prompt_commandish_rows_need_docs_batch(cmd=cmd, tok_i=tok_i, toks=toks)
    if docs_batch:
        self._enter_doc_prompt_rows_batch()
    try:
        for cand in candidates:
            insert = str(cand)
            raw = insert[:-1] if insert.endswith(" ") else insert
            row = [insert, "", "", ""]

            if tok_i == 0:
                c = self.command_dispatcher.get(raw)
                if c is not None:
                    info = ""
                    if c.group:
                        info = f"group={c.group}"
                    row = [insert, "command", str(c.doc or ""), info]
                    specific = root_command_specific_row(self, raw=raw, insert=insert)
                    if specific is not None:
                        row = specific
                rows.append(row)
                continue

            if tok_i == 1 and cmd in ("set", "setlocal", "show", "toggle", "togglelocal"):
                rows.append(self._prompt_option_row(raw, local=(cmd in ("setlocal", "togglelocal"))))
                continue

            if tok_i == 1 and cmd == "showoption":
                rows.append(self._prompt_exact_option_row(insert, fallback_info="inspect exact option", strict_missing=True))
                continue

            if tok_i == 2 and cmd in ("set", "setlocal") and len(toks) >= 2:
                name = str(toks[1])
                spec = self.options.spec(name)
                cur_local = self.cur().local_options if cmd == "setlocal" else None
                cur = None
                if spec is not None:
                    cur = self.options.get(name, local=cur_local)
                menu = f"value for {name}"
                if cur is not None and raw == self._prompt_display_value(cur):
                    menu = menu + " (current)"
                info = str(spec.doc or "") if spec is not None else ""
                row = [insert, "value", menu, info]
                rows.append(row)
                continue

            if tok_i == 1 and cmd in ("help", "apropos"):
                row2 = self._prompt_help_topic_row(insert)
                if cmd == "apropos" and len(row2) >= 4 and str(row2[1]) in ("command", "action", "word", "doc"):
                    row2 = self._prompt_topic_search_row(row2)
                rows.append(row2)
                continue

            if cmd == "helpjump" and tok_i >= 1:
                rows.append(self._prompt_help_heading_row(insert, fallback_info="jump to heading"))
                continue

            if tok_i == 1 and cmd == "commandpick":
                c = self.command_dispatcher.get(raw)
                if c is not None:
                    rows.append(
                        self._prompt_command_palette_row(
                            self._prompt_command_row(insert, fallback_info="command palette")
                        )
                    )
                    continue
                a = self.actions.get(raw)
                if a is not None:
                    rows.append(
                        self._prompt_command_palette_row(
                            self._prompt_action_row(insert, fallback_info="command palette")
                        )
                    )
                    continue

            if tok_i == 1 and cmd == "showcmd":
                rows.append(self._prompt_command_row(insert, strict_missing=True))
                continue

            if tok_i == 1 and cmd == "showaction":
                rows.append(self._prompt_action_row(insert, fallback_info="inspect exact action", strict_missing=True))
                continue

            if tok_i == 1 and cmd == "showhook":
                rows.append(self._prompt_hook_row(insert, strict_missing=True))
                continue

            if tok_i == 1 and cmd == "showhooks":
                rows.append(self._prompt_hook_summary_row(insert))
                continue

            if tok_i == 1 and cmd == "showword":
                rows.append(self._prompt_vm_word_row(insert, strict_missing=True))
                continue

            if tok_i == 1 and cmd == "showdoc":
                rows.append(self._prompt_doc_row(insert, strict_missing=True))
                continue

            if tok_i == 1 and cmd == "showtopic":
                rows.append(self._prompt_help_topic_row(insert, strict_missing=True))
                continue

            if tok_i == 2 and cmd == "help" and len(toks) >= 2 and str(toks[1]).casefold() in ("doc", "docs"):
                rows.append(self._prompt_doc_row(insert))
                continue

            if tok_i == 1 and cmd in ("buffer", "showbuffer"):
                info = "inspect exact buffer" if cmd == "showbuffer" else "switch buffer"
                rows.append(
                    self._prompt_exact_buffer_row(
                        insert,
                        fallback_info=info,
                        strict_missing=(cmd == "showbuffer"),
                    )
                )
                continue

            if tok_i == 1 and cmd == "showtopics":
                rows.append(
                    self._prompt_section_summary_row(
                        insert,
                        cmd=cmd,
                        kind="topic-group",
                        noun="topic",
                        fallback_info="filter generic help-topic families",
                    )
                )
                continue

            if tok_i == 1 and cmd == "showoptiongroups":
                rows.append(
                    self._prompt_section_summary_row(
                        insert,
                        cmd=cmd,
                        kind="option-group",
                        noun="option",
                        fallback_info="filter option families",
                    )
                )
                continue

            if tok_i == 1 and cmd == "showbuffergroups":
                rows.append(
                    self._prompt_section_summary_row(
                        insert,
                        cmd=cmd,
                        kind="buffer-group",
                        noun="buffer",
                        fallback_info="filter buffer sections",
                    )
                )
                continue

            if tok_i == 1 and cmd == "showrecentgroups":
                rows.append(
                    self._prompt_section_summary_row(
                        insert,
                        cmd=cmd,
                        kind="recent-group",
                        noun="file",
                        fallback_info="filter recent file buckets",
                        empty_info="0 section(s), 0 files",
                    )
                )
                continue

            if tok_i == 1 and cmd == "showrecentdirgroups":
                rows.append(
                    self._prompt_section_summary_row(
                        insert,
                        cmd=cmd,
                        kind="recentdir-group",
                        noun="file",
                        fallback_info="filter recent directory buckets",
                        empty_info="0 section(s), 0 files",
                    )
                )
                continue

            if tok_i == 1 and cmd == "showmarkgroups":
                rows.append(
                    self._prompt_section_summary_row(
                        insert,
                        cmd=cmd,
                        kind="mark-group",
                        noun="mark",
                        fallback_info="filter mark buckets",
                    )
                )
                continue

            if tok_i == 1 and cmd == "showjumpgroups":
                rows.append(
                    self._prompt_section_summary_row(
                        insert,
                        cmd=cmd,
                        kind="jump-group",
                        noun="jump",
                        fallback_info="filter jumplist sections",
                    )
                )
                continue

            if tok_i == 1 and cmd == "showpalettegroups":
                rows.append(
                    self._prompt_section_summary_row(
                        insert,
                        cmd=cmd,
                        kind="palette-group",
                        noun="item",
                        fallback_info="filter palette buckets",
                    )
                )
                continue

            if tok_i == 1 and cmd == "showhelpnav":
                rows.append(
                    self._prompt_section_summary_row(
                        insert,
                        cmd=cmd,
                        kind="helpnav-group",
                        noun="target",
                        fallback_info="filter current-doc navigation buckets",
                    )
                )
                continue

            if tok_i == 1 and cmd == "showdocs":
                rows.append(
                    self._prompt_section_summary_row(
                        insert,
                        cmd=cmd,
                        kind="doc-group",
                        noun="doc",
                        fallback_info="filter docs families",
                    )
                )
                continue

            if tok_i == 1 and cmd == "showplugins":
                rows.append(
                    self._prompt_section_summary_row(
                        insert,
                        cmd=cmd,
                        kind="plugin-group",
                        noun="plugin",
                        fallback_info="filter plugin-state buckets",
                    )
                )
                continue

            if tok_i == 1 and cmd == "showbindingmodes":
                rows.append(
                    self._prompt_section_summary_row(
                        insert,
                        cmd=cmd,
                        kind="bindingmode-group",
                        noun="binding",
                        fallback_info="filter winning-mode binding buckets",
                    )
                )
                continue

            if tok_i == 1 and cmd == "showrecent":
                rows.append(
                    self._prompt_exact_recent_row(
                        insert,
                        fallback_info="inspect exact recent file",
                        strict_missing=True,
                    )
                )
                continue

            if tok_i == 1 and cmd in ("recentpick", "recentdirpick"):
                rows.append(
                    self._prompt_exact_recent_row(
                        insert,
                        fallback_info="filter recent picker",
                        empty_info="0 recent file(s)",
                    )
                )
                continue

            if tok_i == 1 and cmd == "showrecentdir":
                rows.append(
                    self._prompt_exact_recentdir_row(
                        insert,
                        fallback_info="inspect exact recent directory",
                        strict_missing=True,
                    )
                )
                continue

            if tok_i == 1 and cmd == "recent":
                rows.append(
                    self._prompt_recent_command_row(
                        insert,
                        row=recent_rows_by_index.get(raw),
                        fallback_info="open recent file",
                    )
                )
                continue

            if tok_i == 1 and cmd == "showmark":
                rows.append(
                    self._prompt_exact_mark_row(
                        insert,
                        fallback_info="inspect exact mark",
                        strict_missing=True,
                    )
                )
                continue

            if tok_i == 1 and cmd == "showmacro":
                rows.append(
                    self._prompt_exact_macro_row(
                        insert,
                        fallback_info="inspect exact macro",
                        strict_missing=True,
                    )
                )
                continue

            if tok_i == 1 and cmd == "showjump":
                rows.append(
                    self._prompt_exact_jump_row(
                        insert,
                        fallback_info="inspect exact jump",
                        strict_missing=True,
                    )
                )
                continue

            if tok_i == 1 and cmd == "jumppick":
                row2 = self.jump_detail_row(raw)
                if row2 is not None:
                    rows.append(self._prompt_exact_jump_row(insert, fallback_info="pick exact jump"))
                    continue

            if tok_i == 1 and cmd == "showplugin":
                rows.append(
                    self._prompt_plugin_row(
                        insert,
                        strict_missing=True,
                        include_error_count_in_menu=True,
                        prefer_state_info_when_blank=True,
                    )
                )
                continue

            if tok_i == 1 and cmd == "showkey":
                rows.append(
                    self._prompt_binding_row(
                        insert,
                        fallback_info="inspect exact binding",
                        strict_missing=True,
                    )
                )
                continue

            if tok_i == 1 and cmd == "buffer":
                rows.append(self._prompt_buffer_row(insert))
                continue

            if tok_i == 1 and cmd in ("mark", "markjump"):
                info = "jump to mark" if cmd == "markjump" else "set mark"
                rows.append(self._prompt_exact_mark_row(insert, fallback_info=info))
                continue

            if tok_i == 1 and cmd == "plugin":
                rows.append(self._prompt_plugin_command_row(insert, subcommand=raw))
                continue

            if tok_i == 2 and cmd == "plugin" and len(toks) >= 2 and str(toks[1]) in ("load", "unload", "reload", "info", "errors", "cleanup", "revoke"):
                rows.append(self._prompt_plugin_target_row(insert, subcommand=str(toks[1])))
                continue

            if tok_i == 1 and cmd == "macro":
                rows.append(self._prompt_macro_command_row(insert, subcommand=raw))
                continue

            if tok_i == 2 and cmd == "macro" and len(toks) >= 2 and toks[1] in ("play", "run", "record", "rec", "start"):
                rows.append(self._prompt_macro_slot_row(insert, subcommand=str(toks[1])))
                continue

            if tok_i == 3 and cmd == "macro" and len(toks) >= 3 and toks[1] in ("play", "run"):
                rows.append(
                    self._prompt_macro_count_row(
                        insert,
                        subcommand=str(toks[1]),
                        slot_name=str(toks[2]),
                    )
                )
                continue

            if cmd == "macro" and len(toks) >= 2:
                sub = str(toks[1]).strip().lower()
                if tok_i == 2 and sub in ("stop", "end", "cancel", "abort", "list", "ls", "status", "st"):
                    rows.append(self._prompt_macro_arity_row(insert, subcommand=sub))
                    continue
                if tok_i == 3 and sub in ("record", "rec", "start"):
                    rows.append(self._prompt_macro_arity_row(insert, subcommand=sub))
                    continue
                if tok_i >= 4 and sub in ("play", "run"):
                    rows.append(self._prompt_macro_arity_row(insert, subcommand=sub))
                    continue

            if tok_i == 1 and cmd in ("keymode", "pushkeymode", "pushkeymode-once", "prefixmode", "showkeymode"):
                info = "inspect exact keymode" if cmd == "showkeymode" else ""
                rows.append(
                    self._prompt_keymode_row(
                        insert,
                        fallback_info=info,
                        strict_missing=(cmd == "showkeymode"),
                    )
                )
                continue

            if tok_i == 1 and cmd == "showbindings":
                rows.append(self._prompt_showbindings_mode_row(insert))
                continue

            if tok_i == 1 and cmd in ("bindmode", "bindmodedoc", "unbindmode", "bindmodeprefix"):
                rows.append([insert, "keymode", "owner mode", ""])
                continue

            if tok_i == 3 and cmd == "bindmodeprefix":
                rows.append([insert, "keymode", "prefix mode", ""])
                continue

            rows.append(row)
    finally:
        if docs_batch:
            self._leave_doc_prompt_rows_batch()
    return rows

def prompt_bind_suggestion_rows(
    editor: Any,
    *,
    cmd: str,
    toks: list[str],
    tok_i: int,
    candidates: list[str],
) -> list[list[str]]:
    self = editor
    action_tok_i = 2 if cmd == "bind" else 3
    if tok_i < action_tok_i or len(toks) <= action_tok_i:
        return [[str(c), "", "", ""] for c in candidates]

    action_head = toks[action_tok_i]
    for lead in ("command-edit:", "command:"):
        if action_head.startswith(lead):
            first = action_head[len(lead):]
            nested_toks = [first] + toks[action_tok_i + 1 :]
            nested_tok_i = tok_i - action_tok_i
            if nested_tok_i == 0:
                rows: list[list[str]] = []
                for cand in candidates:
                    insert = str(cand)
                    raw = insert[:-1] if insert.endswith(" ") else insert
                    if raw.startswith(lead):
                        nested_raw = raw[len(lead):]
                    else:
                        nested_raw = raw
                    nested_rows = self._prompt_commandish_suggestion_rows(
                        cmd=nested_raw,
                        toks=[nested_raw],
                        tok_i=0,
                        candidates=[nested_raw + (" " if insert.endswith(" ") else "")],
                    )
                    nr = nested_rows[0] if nested_rows else [nested_raw, "command", "", ""]
                    rows.append([insert, "binding-command", nr[2], lead[:-1]])
                return rows
            return self._prompt_commandish_suggestion_rows(
                cmd=(nested_toks[0] if nested_toks else ""),
                toks=nested_toks,
                tok_i=nested_tok_i,
                candidates=candidates,
            )

    if tok_i == action_tok_i:
        rows: list[list[str]] = []
        for cand in candidates:
            insert = str(cand)
            raw = insert[:-1] if insert.endswith(" ") else insert
            if raw in ("command:", "command-edit:"):
                rows.append([insert, "binding-prefix", "binding command rhs", ""])
                continue
            a = self.actions.get(raw)
            if a is not None:
                rows.append([insert, "action", str(a.doc or ""), "binding rhs"])
                continue
            rows.append([insert, "", "", ""])
        return rows

    return [[str(c), "", "", ""] for c in candidates]

def prompt_suggestion_rows(
    editor: Any,
    *,
    cmd: str,
    toks: list[str],
    tok_i: int,
    candidates: list[str],
    path_mode: bool = False,
    path_candidates: set[str] | frozenset[str] | None = None,
) -> list[list[str]]:
    self = editor
    if path_mode or path_candidates:
        path_set = set(path_candidates or (set(candidates) if path_mode else set()))
        rows: list[list[str]] = []
        for cand in candidates:
            if str(cand) in path_set:
                rows.append(self._prompt_path_row(cand))
            else:
                rows.append([str(cand), "", "", ""])
        return rows
    if cmd in ("bind", "bindmode"):
        return self._prompt_bind_suggestion_rows(cmd=cmd, toks=toks, tok_i=tok_i, candidates=candidates)
    return self._prompt_commandish_suggestion_rows(cmd=cmd, toks=toks, tok_i=tok_i, candidates=candidates)

def prompt_action_spec_prefix_candidates(
    editor: Any,
    prefix: str,
    *,
    at_eol: bool,
) -> tuple[list[str], bool]:
    self = editor
    names = self.action_names() + ["command:", "command-edit:"]
    chosen, fuzzy = self._completion_candidates_for_prefix(names, prefix, at_eol=False)
    out: list[str] = []
    for c in chosen:
        if c.endswith(":"):
            out.append(c)
        elif at_eol:
            out.append(c + " ")
        else:
            out.append(c)
    return (out, fuzzy)

def prompt_bind_action_candidates(
    editor: Any,
    *,
    cmd: str,
    toks: list[str],
    tok_i: int,
    prefix: str,
    at_eol: bool,
) -> tuple[list[str], bool]:
    self = editor
    if cmd == "bind":
        action_tok_i = 2
    elif cmd == "bindmode":
        action_tok_i = 3
    else:
        return ([], False)

    if tok_i < action_tok_i or len(toks) <= action_tok_i:
        return ([], False)

    action_head = toks[action_tok_i]
    for lead in ("command-edit:", "command:"):
        if action_head.startswith(lead):
            first = action_head[len(lead) :]
            nested_toks = [first] + toks[action_tok_i + 1 :]
            nested_tok_i = tok_i - action_tok_i
            nested_cmd = nested_toks[0] if nested_toks else ""
            nested_prefix = first if nested_tok_i == 0 else prefix
            candidates, fuzzy = self._prompt_command_token_candidates(
                cmd=nested_cmd,
                toks=nested_toks,
                tok_i=nested_tok_i,
                prefix=nested_prefix,
                at_eol=at_eol,
            )
            if nested_tok_i == 0:
                candidates = [lead + c for c in candidates]
            return (candidates, fuzzy)

    if tok_i == action_tok_i:
        return self._prompt_action_spec_prefix_candidates(prefix, at_eol=at_eol)
    return ([], False)

def prompt_command_token_candidates(
    editor: Any,
    *,
    cmd: str,
    toks: list[str],
    tok_i: int,
    prefix: str,
    at_eol: bool,
) -> tuple[list[str], bool]:
    self = editor
    if tok_i == 0:
        return self._completion_candidates_for_prefix(
            self.command_names(),
            prefix,
            at_eol=at_eol,
        )
    if tok_i == 1 and cmd == "showoption":
        candidates, fuzzy = self._completion_candidates_for_prefix(
            [spec.name for spec in self.options.list_specs(include_aliases=True)],
            prefix,
            at_eol=at_eol,
        )
        if not candidates and str(prefix).strip():
            token = str(prefix)
            candidates = [token + (" " if at_eol else "")]
            fuzzy = False
        return (candidates, fuzzy)
    if tok_i == 1 and cmd in ("set", "setlocal", "show", "toggle", "togglelocal"):
        return self._completion_candidates_for_prefix(
            [spec.name for spec in self.options.list_specs(include_aliases=True)],
            prefix,
            at_eol=at_eol,
        )
    if tok_i == 2 and cmd in ("set", "setlocal") and len(toks) >= 2:
        return self._prompt_option_value_candidates(toks[1], prefix, at_eol=at_eol)
    if tok_i == 1 and cmd in ("help", "apropos"):
        return self._completion_candidates_for_prefix(
            self._prompt_help_topic_names(),
            prefix,
            at_eol=at_eol,
        )
    if tok_i == 1 and cmd == "helpjump":
        return self._completion_candidates_for_prefix(
            self._prompt_help_heading_names(),
            prefix,
            at_eol=at_eol,
        )
    if tok_i == 1 and cmd == "commandpick":
        return self._completion_candidates_for_prefix(
            self._prompt_command_palette_names(),
            prefix,
            at_eol=at_eol,
        )
    if tok_i == 1 and cmd == "showcmd":
        candidates, fuzzy = self._completion_candidates_for_prefix(
            self.command_names(),
            prefix,
            at_eol=at_eol,
        )
        if not candidates and str(prefix).strip():
            token = str(prefix)
            candidates = [token + (" " if at_eol else "")]
            fuzzy = False
        return (candidates, fuzzy)
    if tok_i == 1 and cmd == "showaction":
        candidates, fuzzy = self._completion_candidates_for_prefix(
            self.action_names(),
            prefix,
            at_eol=at_eol,
        )
        if not candidates and str(prefix).strip():
            token = str(prefix)
            candidates = [token + (" " if at_eol else "")]
            fuzzy = False
        return (candidates, fuzzy)
    if tok_i == 1 and cmd == "showhook":
        candidates, fuzzy = self._completion_candidates_for_prefix(
            self._prompt_hook_names(),
            prefix,
            at_eol=at_eol,
        )
        typed = str(prefix or "").strip()
        if typed and not candidates:
            exact = typed + (" " if at_eol else "")
            candidates = [exact]
            fuzzy = False
        return (candidates, fuzzy)
    if tok_i == 1 and cmd == "showhooks":
        return self._completion_candidates_for_prefix(
            self._prompt_hook_names(),
            prefix,
            at_eol=at_eol,
        )
    if tok_i == 1 and cmd == "showword":
        candidates, fuzzy = self._completion_candidates_for_prefix(
            self._prompt_vm_word_names(),
            prefix,
            at_eol=at_eol,
        )
        if not candidates and str(prefix).strip():
            token = str(prefix)
            candidates = [token + (" " if at_eol else "")]
            fuzzy = False
        return (candidates, fuzzy)
    if tok_i == 1 and cmd == "showdoc":
        candidates, fuzzy = self._completion_candidates_for_prefix(
            self._prompt_doc_names(),
            prefix,
            at_eol=at_eol,
        )
        if not candidates and str(prefix).strip():
            token = str(prefix)
            candidates = [token + (" " if at_eol else "")]
            fuzzy = False
        return (candidates, fuzzy)
    if tok_i == 1 and cmd == "showtopic":
        candidates, fuzzy = self._completion_candidates_for_prefix(
            self._prompt_help_topic_names(),
            prefix,
            at_eol=at_eol,
        )
        if not candidates and str(prefix).strip():
            token = str(prefix)
            candidates = [token + (" " if at_eol else "")]
            fuzzy = False
        return (candidates, fuzzy)
    if tok_i == 2 and cmd == "help" and len(toks) >= 2 and str(toks[1]).casefold() in ("doc", "docs"):
        return self._completion_candidates_for_prefix(
            self._prompt_doc_names(),
            prefix,
            at_eol=at_eol,
        )

    if tok_i == 1 and cmd == "showbuffer":
        candidates, fuzzy = self._completion_candidates_for_prefix(
            self.buffer_names(),
            prefix,
            at_eol=at_eol,
        )
        if not candidates and str(prefix).strip():
            token = str(prefix)
            candidates = [token + (" " if at_eol else "")]
            fuzzy = False
        return (candidates, fuzzy)
    if tok_i == 1 and cmd == "buffer":
        return self._completion_candidates_for_prefix(
            self.buffer_names(),
            prefix,
            at_eol=at_eol,
        )
    if tok_i == 1 and cmd in (
        "showtopics",
        "showoptiongroups",
        "showbuffergroups",
        "showrecentgroups",
        "showrecentdirgroups",
        "showmarkgroups",
        "showjumpgroups",
        "showpalettegroups",
        "showhelpnav",
        "showdocs",
        "showplugins",
        "showbindingmodes",
    ):
        candidates, fuzzy = self._completion_candidates_for_prefix(
            self._prompt_section_summary_names_for_command(cmd),
            prefix,
            at_eol=at_eol,
        )
        if not candidates and str(prefix).strip() and cmd in ("showrecentgroups", "showrecentdirgroups"):
            token = str(prefix)
            candidates = [token + (" " if at_eol else "")]
            fuzzy = False
        return (candidates, fuzzy)
    if tok_i == 1 and cmd == "showrecent":
        slot_names = [str(int(row[0])) for row in self.recent_inventory_rows()]
        names = [f"#{slot}" for slot in slot_names] if str(prefix).startswith("#") else list(slot_names)
        names.extend(str(x) for x in self.visible_recent_files())
        seen: set[str] = set()
        ordered: list[str] = []
        for name in names:
            key = str(name)
            if key in seen:
                continue
            seen.add(key)
            ordered.append(key)
        exact = [name for name in ordered if str(name).startswith(prefix)]
        fuzzy = False
        if exact:
            chosen = exact
        elif prefix != '':
            scored: list[tuple[FuzzySortKey, str]] = []
            for name in ordered:
                key = self._completion_fuzzy_sort_key(str(name), prefix)
                if key is not None:
                    scored.append((key, str(name)))
            scored.sort(key=lambda item: item[0])
            chosen = [name for _key, name in scored]
            fuzzy = bool(chosen)
        else:
            chosen = list(ordered)
        candidates = [name + (" " if at_eol else "") for name in chosen]
        if not candidates and str(prefix).strip():
            token = str(prefix)
            candidates = [token + (" " if at_eol else "")]
            fuzzy = False
        return (candidates, fuzzy)
    if tok_i == 1 and cmd in ("recentpick", "recentdirpick"):
        candidates, fuzzy = self._completion_candidates_for_prefix(
            self.visible_recent_files(),
            prefix,
            at_eol=at_eol,
        )
        if not candidates and str(prefix).strip():
            token = str(prefix)
            candidates = [token + (" " if at_eol else "")]
            fuzzy = False
        return (candidates, fuzzy)
    if tok_i == 1 and cmd == "recent":
        slot_names = [str(int(row[0])) for row in self.recent_inventory_rows()]
        names = [f"#{slot}" for slot in slot_names] if str(prefix).startswith("#") else list(slot_names)
        names.append("clear")
        exact = [name for name in names if name.startswith(prefix)]
        fuzzy = False
        if exact:
            chosen = exact
        elif prefix != "":
            scored: list[tuple[FuzzySortKey, str]] = []
            for name in names:
                key = self._completion_fuzzy_sort_key(name, prefix)
                if key is not None:
                    scored.append((key, name))
            scored.sort(key=lambda item: item[0])
            chosen = [name for _key, name in scored]
            fuzzy = bool(chosen)
        else:
            chosen = []
        if not chosen and str(prefix).strip() and self.parse_recent_slot_token(prefix) is not None:
            chosen = [str(prefix)]
            fuzzy = False
        if at_eol:
            chosen = [name + " " for name in chosen]
        return (chosen, fuzzy)
    if tok_i == 1 and cmd == "showrecentdir":
        slot_names = [str(int(row[0])) for row in self.recent_inventory_rows()]
        if str(prefix).startswith("#"):
            names = [f"#{slot}" for slot in slot_names]
        elif str(prefix)[:1].isdigit():
            names = list(slot_names)
        else:
            names = self.recent_dir_names()
        candidates, fuzzy = self._completion_candidates_for_prefix(
            names,
            prefix,
            at_eol=at_eol,
        )
        if not candidates and str(prefix).strip():
            token = str(prefix)
            candidates = [token + (" " if at_eol else "")]
            fuzzy = False
        return (candidates, fuzzy)
    if tok_i == 1 and cmd == "showmark":
        candidates, fuzzy = self._completion_candidates_for_prefix(
            [str(name) for name in sorted(self.marks.keys()) if self._mark_read_allowed(str(name))],
            prefix,
            at_eol=at_eol,
        )
        if not candidates and str(prefix).strip():
            token = str(prefix)
            candidates = [token + (" " if at_eol else "")]
            fuzzy = False
        return (candidates, fuzzy)
    if tok_i == 1 and cmd == "showmacro":
        names: list[str] = ['last']
        names.extend(str(row[0]) for row in self.macro_inventory_rows() if row and str(row[0]).strip())
        if getattr(self, 'macro_recording', False):
            target = str(getattr(self, '_macro_target', '') or 'last')
            names.append(target)
        if getattr(self, '_macro_playing', False):
            play_name = str(getattr(self, '_macro_play_name', '') or '')
            if play_name:
                names.append(play_name)
        ordered = sorted(names, key=lambda value: (0 if str(value) == 'last' else 1, str(value)))
        candidates, fuzzy = self._completion_candidates_for_prefix_preserving_order(
            ordered,
            prefix,
            at_eol=at_eol,
        )
        if not candidates and str(prefix).strip():
            token = str(prefix)
            candidates = [token + (" " if at_eol else "")]
            fuzzy = False
        return (candidates, fuzzy)
    if tok_i == 1 and cmd in ("mark", "markjump"):
        return self._completion_candidates_for_prefix(
            [str(name) for name in sorted(self.marks.keys()) if self._mark_read_allowed(str(name))],
            prefix,
            at_eol=at_eol,
        )
    if tok_i == 1 and cmd == "showjump":
        index_names = [str(row[2]) for row in self.jump_history_rows() if len(row) >= 3]
        names = [f"#{name}" for name in index_names] if str(prefix).startswith("#") else index_names
        candidates, fuzzy = self._completion_candidates_for_prefix(
            names,
            prefix,
            at_eol=at_eol,
        )
        if not candidates and str(prefix).strip():
            token = str(prefix)
            candidates = [token + (" " if at_eol else "")]
            fuzzy = False
        return (candidates, fuzzy)
    if tok_i == 1 and cmd == "jumppick":
        index_names = [str(row[2]) for row in self.jump_history_rows() if len(row) >= 3]
        names = [f"#{name}" for name in index_names] if str(prefix).startswith("#") else index_names
        return self._completion_candidates_for_prefix(
            names,
            prefix,
            at_eol=at_eol,
        )
    if tok_i == 1 and cmd == "showplugin":
        candidates, fuzzy = self._completion_candidates_for_prefix(
            self.plugin_names(),
            prefix,
            at_eol=at_eol,
        )
        if not candidates and str(prefix).strip():
            token = str(prefix)
            candidates = [token + (" " if at_eol else "")]
            fuzzy = False
        return (candidates, fuzzy)
    if tok_i == 1 and cmd == "showkey":
        candidates, fuzzy = self._completion_candidates_for_prefix(
            [str(row[0]) for row in self.binding_prompt_rows() if row],
            prefix,
            at_eol=at_eol,
        )
        if not candidates and str(prefix).strip():
            token = str(prefix)
            candidates = [token + (" " if at_eol else "")]
            fuzzy = False
        return (candidates, fuzzy)
    if tok_i == 1 and cmd == "plugin":
        return self._completion_candidates_for_prefix(
            ["list", "load", "unload", "reload", "info", "errors", "cleanup", "grants", "revoke"],
            prefix,
            at_eol=at_eol,
        )
    if tok_i == 2 and cmd == "plugin" and len(toks) >= 2:
        sub = str(toks[1])
        if sub == "load":
            candidates, fuzzy = self._completion_candidates_for_prefix(
                self.plugin_names(),
                prefix,
                at_eol=at_eol,
            )
            if not candidates and str(prefix).strip():
                token = str(prefix)
                candidates = [token + (" " if at_eol else "")]
                fuzzy = False
            return (candidates, fuzzy)
        if sub in ("unload", "reload"):
            raw_names = list(self.plugin_manager.plugins.keys()) if self.plugin_manager else []
            names = [str(n) for n in raw_names if self._plugin_read_allowed(str(n))]
            candidates, fuzzy = self._completion_candidates_for_prefix(
                names,
                prefix,
                at_eol=at_eol,
            )
            if not candidates and str(prefix).strip():
                token = str(prefix)
                candidates = [token + (" " if at_eol else "")]
                fuzzy = False
            return (candidates, fuzzy)
        if sub == "revoke":
            rows = self.plugin_load_grant_rows()
            names = [str(row[0]) for row in rows if row]
            candidates, fuzzy = self._completion_candidates_for_prefix(
                names,
                prefix,
                at_eol=at_eol,
            )
            if not candidates and str(prefix).strip():
                token = str(prefix)
                candidates = [token + (" " if at_eol else "")]
                fuzzy = False
            return (candidates, fuzzy)
        if sub in ("info", "errors", "cleanup"):
            candidates, fuzzy = self._completion_candidates_for_prefix(
                self.plugin_names(),
                prefix,
                at_eol=at_eol,
            )
            if not candidates and str(prefix).strip():
                token = str(prefix)
                candidates = [token + (" " if at_eol else "")]
                fuzzy = False
            return (candidates, fuzzy)
    if tok_i == 1 and cmd == "macro":
        candidates, fuzzy = self._completion_candidates_for_prefix(
            ["record", "rec", "start", "stop", "end", "cancel", "abort", "play", "run", "list", "ls", "status", "st"],
            prefix,
            at_eol=at_eol,
        )
        if not candidates and str(prefix).strip():
            token = str(prefix)
            candidates = [token + (" " if at_eol else "")]
            fuzzy = False
        return (candidates, fuzzy)
    if tok_i == 2 and cmd == "macro" and len(toks) >= 2:
        sub = str(toks[1])
        if sub in ("play", "run"):
            if getattr(self, "_macro_playing", False) or getattr(self, "macro_recording", False):
                if str(prefix).strip():
                    token = str(prefix)
                    return ([token + (" " if at_eol else "")], False)
                return ([], False)
            names = [str(row[0]) for row in self.macro_inventory_rows() if row]
            ordered = sorted(names, key=lambda value: (0 if str(value) == 'last' else 1, str(value)))
            return self._completion_candidates_for_prefix_preserving_order(
                ordered,
                prefix,
                at_eol=at_eol,
            )
        if sub in ("record", "rec", "start"):
            if getattr(self, "_macro_playing", False) or getattr(self, "macro_recording", False):
                if str(prefix).strip():
                    token = str(prefix)
                    return ([token + (" " if at_eol else "")], False)
                return ([], False)
            names = ['last'] + [str(name) for name in self.macros.keys()]
            ordered = sorted(names, key=lambda value: (0 if str(value) == 'last' else 1, str(value)))
            return self._completion_candidates_for_prefix_preserving_order(
                ordered,
                prefix,
                at_eol=at_eol,
            )
    if tok_i == 3 and cmd == "macro" and len(toks) >= 3 and str(toks[1]) in ("play", "run"):
        slot_name = str(toks[2])
        have_slot = any(row and str(row[0]) == slot_name for row in self.macro_inventory_rows())
        if not have_slot:
            if str(prefix).strip():
                token = str(prefix)
                return ([token + (" " if at_eol else "")], False)
            return ([], False)
        if getattr(self, "_macro_playing", False) or getattr(self, "macro_recording", False):
            if str(prefix).strip():
                token = str(prefix)
                return ([token + (" " if at_eol else "")], False)
            return ([], False)
        candidates = ["1", "2", "3", "5", "10"]
        token = str(prefix)
        if token:
            options = [item for item in candidates if item.startswith(token)]
        else:
            options = list(candidates)
        if at_eol:
            options = [item + " " for item in options]
        if not options and str(prefix).strip():
            token = str(prefix)
            options = [token + (" " if at_eol else "")]
        return (options, False)
    if cmd == "macro" and len(toks) >= 2:
        sub = str(toks[1]).strip().lower()
        if tok_i == 2 and sub in ("stop", "end", "cancel", "abort", "list", "ls", "status", "st"):
            if str(prefix).strip():
                token = str(prefix)
                return ([token + (" " if at_eol else "")], False)
            return ([], False)
        if tok_i == 3 and sub in ("record", "rec", "start"):
            if str(prefix).strip():
                token = str(prefix)
                return ([token + (" " if at_eol else "")], False)
            return ([], False)
        if tok_i >= 4 and sub in ("play", "run"):
            if str(prefix).strip():
                token = str(prefix)
                return ([token + (" " if at_eol else "")], False)
            return ([], False)
    if tok_i == 1 and cmd == "showkeymode":
        mode_names = [m for m in self._prompt_known_keymodes() if m != "global"]
        mode_names = ["global"] + mode_names
        candidates, fuzzy = self._completion_candidates_for_prefix(
            mode_names,
            prefix,
            at_eol=at_eol,
        )
        if not candidates and str(prefix).strip():
            token = str(prefix)
            candidates = [token + (" " if at_eol else "")]
            fuzzy = False
        return (candidates, fuzzy)
    if tok_i == 1 and cmd in ("keymode", "pushkeymode", "pushkeymode-once", "prefixmode"):
        mode_names = [m for m in self._prompt_known_keymodes() if m != "global"]
        if cmd == "keymode":
            mode_names = ["global"] + mode_names
        return self._completion_candidates_for_prefix(
            mode_names,
            prefix,
            at_eol=at_eol,
        )
    if tok_i == 1 and cmd == "showbindings":
        candidates, fuzzy = self._completion_candidates_for_prefix(
            ["active"] + self._prompt_known_keymodes(),
            prefix,
            at_eol=at_eol,
        )
        if not candidates and str(prefix).strip():
            token = str(prefix)
            candidates = [token + (" " if at_eol else "")]
            fuzzy = False
        return (candidates, fuzzy)
    if tok_i == 1 and cmd in ("bindmode", "bindmodedoc", "unbindmode"):
        mode_names = [m for m in self._prompt_known_keymodes() if m != "global"]
        return self._completion_candidates_for_prefix(
            mode_names,
            prefix,
            at_eol=at_eol,
        )
    if tok_i == 1 and cmd == "bindmodeprefix":
        mode_names = [m for m in self._prompt_known_keymodes() if m != "global"]
        return self._completion_candidates_for_prefix(
            mode_names,
            prefix,
            at_eol=at_eol,
        )
    if tok_i == 3 and cmd == "bindmodeprefix":
        mode_names = [m for m in self._prompt_known_keymodes() if m != "global"]
        return self._completion_candidates_for_prefix(
            mode_names,
            prefix,
            at_eol=at_eol,
        )
    if cmd in ("bind", "bindmode"):
        return self._prompt_bind_action_candidates(
            cmd=cmd,
            toks=toks,
            tok_i=tok_i,
            prefix=prefix,
            at_eol=at_eol,
        )
    return ([], False)
