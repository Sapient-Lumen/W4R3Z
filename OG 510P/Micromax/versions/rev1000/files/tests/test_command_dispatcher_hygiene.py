from __future__ import annotations

import ast
import inspect

from micromax_editor.command_dispatcher import install_default_commands


def _default_register_calls() -> list[ast.Call]:
    source = inspect.getsource(install_default_commands)
    module = ast.parse(source)
    calls: list[ast.Call] = []
    for node in ast.walk(module):
        if not isinstance(node, ast.Call):
            continue
        fn = node.func
        if isinstance(fn, ast.Attribute) and fn.attr == "register":
            calls.append(node)
    return calls


def _literal_default_command_names() -> list[str]:
    names: list[str] = []
    for call in _default_register_calls():
        if not call.args:
            continue
        name = call.args[0]
        if isinstance(name, ast.Constant) and isinstance(name.value, str):
            names.append(name.value)
    return names


def test_default_command_registration_names_are_unique() -> None:
    names = _literal_default_command_names()
    duplicates = sorted({name for name in names if names.count(name) > 1})
    assert duplicates == []
    assert len(names) >= 120


def test_default_command_registration_docs_are_present() -> None:
    missing: list[str] = []
    for call in _default_register_calls():
        if not call.args or not isinstance(call.args[0], ast.Constant):
            continue
        name = str(call.args[0].value)
        doc_kw = next((kw for kw in call.keywords if kw.arg == "doc"), None)
        if doc_kw is None:
            missing.append(name)
            continue
        value = doc_kw.value
        if isinstance(value, ast.Constant) and isinstance(value.value, str) and value.value.strip():
            continue
        if isinstance(value, ast.Name) and value.id.endswith("_DOC"):
            continue
        missing.append(name)
    assert missing == []


def _default_install_nested_function_names() -> set[str]:
    source = inspect.getsource(install_default_commands)
    module = ast.parse(source)
    return {
        node.name
        for node in ast.walk(module)
        if isinstance(node, ast.FunctionDef) and node.name != "install_default_commands"
    }



def test_default_command_install_is_registration_only() -> None:
    assert _default_install_nested_function_names() == set()

def test_default_command_install_closure_keeps_formatting_and_buffer_families_extracted() -> None:
    nested_names = _default_install_nested_function_names()
    assert not any(name.startswith("_format_") for name in nested_names)
    assert "c_open" not in nested_names
    assert "c_close" not in nested_names
    assert "c_recent" not in nested_names


def test_default_command_install_closure_keeps_command_families_extracted() -> None:
    nested_names = _default_install_nested_function_names()
    extracted = {
        "c_help",
        "c_helpjump",
        "c_urlopen",
        "c_bind",
        "c_bindmode",
        "c_unbind",
        "c_keymode",
        "c_pushkeymode",
        "c_rawkeys",
        "c_set",
        "c_toggle",
        "c_commandpick",
        "c_apropos",
        "c_quit",
        "c_reload",
        "c_showcmd",
        "c_showaction",
        "c_showword",
        "c_showdoc",
        "c_showtopic",
        "c_showkey",
        "c_showbindings",
        "c_showplugin",
        "c_showplugins",
        "c_showhook",
        "c_showhooks",
        "c_macro",
        "c_plugin",
        "c_replace",
        "c_replaceall",
        "c_replacepreview",
        "c_qreplace",
    }
    assert sorted(extracted & nested_names) == []
