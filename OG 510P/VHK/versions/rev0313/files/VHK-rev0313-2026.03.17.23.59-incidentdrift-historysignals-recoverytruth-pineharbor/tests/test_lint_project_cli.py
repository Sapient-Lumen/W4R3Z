from __future__ import annotations

import json
from pathlib import Path

import yaml
from typer.testing import CliRunner

from vhk.cli import app


runner = CliRunner()


def test_lint_project_check_and_json(tmp_path: Path) -> None:
    project_dir = tmp_path / "proj"
    (project_dir / "macros").mkdir(parents=True)
    (project_dir / "project.yaml").write_text("name: proj\n")

    (project_dir / "macros" / "a.yaml").write_text(
        yaml.safe_dump(
            {
                "name": "a",
                "steps": [
                    {"type": "Delay", "ms": 2000},
                    {"type": "MouseClickAt", "x": 1, "y": 2},
                ],
            },
            sort_keys=False,
        )
    )

    res = runner.invoke(app, ["lint-project", str(project_dir), "--check", "--json"])
    assert res.exit_code == 1
    data = json.loads(res.output)
    assert data["issue_count"] >= 2
    assert any(i.get("macro") == "macros/a.yaml" for i in data["issues"])


def test_lint_project_warns_on_missing_session_capabilities(tmp_path: Path, monkeypatch) -> None:
    project_dir = tmp_path / "proj"
    (project_dir / "macros").mkdir(parents=True)
    (project_dir / "project.yaml").write_text(
        yaml.safe_dump(
            {
                "name": "proj",
                "macros": {"main": "macros/main.yaml"},
                "bindings": [{"keys": "Mod4+M", "macro": "main"}],
            },
            sort_keys=False,
        )
    )
    (project_dir / "macros" / "main.yaml").write_text(
        yaml.safe_dump(
            {
                "name": "main",
                "steps": [{"type": "TypeText", "text": "hello"}],
            },
            sort_keys=False,
        )
    )

    import vhk.cli as cli_mod

    monkeypatch.setattr(
        cli_mod,
        "_validation_session_capability_matrix",
        lambda: {
            "global_hotkeys": {"status": "missing", "mechanisms": [], "recommended": None, "notes": [], "portal_backends": []},
            "text_injection": {"status": "limited", "mechanisms": ["portal:RemoteDesktop(keyboard)"], "recommended": None, "notes": ["interactive"], "portal_backends": ["gnome"]},
            "screen_capture": {"status": "ok", "mechanisms": ["portal:Screenshot"], "recommended": "portal:Screenshot", "notes": [], "portal_backends": ["gtk"]},
            "pointer_injection": {"status": "ok", "mechanisms": [], "recommended": None, "notes": [], "portal_backends": []},
            "window_introspection": {"status": "ok", "mechanisms": [], "recommended": None, "notes": [], "portal_backends": []},
        },
    )

    res = runner.invoke(app, ["lint-project", str(project_dir), "--json", "--check"])
    assert res.exit_code == 1, res.output
    data = json.loads(res.output)
    assert data["session_capabilities"]["text_injection"]["status"] == "limited"
    sess = [i for i in data["issues"] if i.get("macro") == "<project>"]
    assert any(i.get("capability") == "global_hotkeys" for i in sess)
    assert any(i.get("capability") == "text_injection" for i in sess)
    assert data["capability_usage"]["global_hotkeys"]
    assert data["capability_usage"]["text_injection"]


def test_lint_project_can_disable_session_capability_check(tmp_path: Path, monkeypatch) -> None:
    project_dir = tmp_path / "proj"
    (project_dir / "macros").mkdir(parents=True)
    (project_dir / "project.yaml").write_text(
        yaml.safe_dump(
            {
                "name": "proj",
                "macros": {"main": "macros/main.yaml"},
            },
            sort_keys=False,
        )
    )
    (project_dir / "macros" / "main.yaml").write_text(
        yaml.safe_dump(
            {
                "name": "main",
                "steps": [{"type": "TypeText", "text": "hello"}],
            },
            sort_keys=False,
        )
    )

    import vhk.cli as cli_mod

    monkeypatch.setattr(
        cli_mod,
        "_validation_session_capability_matrix",
        lambda: (_ for _ in ()).throw(AssertionError("should not be called")),
    )

    res = runner.invoke(app, ["lint-project", str(project_dir), "--json", "--no-session-check"])
    assert res.exit_code == 0, res.output
    data = json.loads(res.output)
    assert data["session_capabilities"] is None
    assert all(i.get("category") != "session_capability" for i in data["issues"])


def test_lint_project_warns_on_voice_phrase_collisions_in_same_scope(tmp_path: Path) -> None:
    project_dir = tmp_path / "proj_voice"
    (project_dir / "macros").mkdir(parents=True)
    (project_dir / "project.yaml").write_text(
        yaml.safe_dump(
            {
                "name": "proj_voice",
                "macros": {
                    "alpha": "macros/alpha.yaml",
                    "beta": "macros/beta.yaml",
                },
            },
            sort_keys=False,
        )
    )
    for name in ["alpha", "beta"]:
        (project_dir / "macros" / f"{name}.yaml").write_text(
            yaml.safe_dump(
                {
                    "name": name,
                    "voice_phrases": ["open dashboard"],
                    "steps": [{"type": "Return", "value": "ok"}],
                },
                sort_keys=False,
            )
        )

    res = runner.invoke(app, ["lint-project", str(project_dir), "--json", "--no-session-check", "--check"])
    assert res.exit_code == 1, res.output
    data = json.loads(res.output)
    issues = [i for i in data["issues"] if i.get("code") == "VOICE_PHRASE_COLLISION"]
    assert len(issues) == 2
    assert {i["backend"] for i in issues} == {"dragonfly", "talon"}
    assert all(i["phrase"] == "open dashboard" for i in issues)


def test_lint_project_does_not_warn_when_voice_phrase_is_scoped_by_context(tmp_path: Path) -> None:
    project_dir = tmp_path / "proj_voice_ctx"
    (project_dir / "macros").mkdir(parents=True)
    (project_dir / "project.yaml").write_text(
        yaml.safe_dump(
            {
                "name": "proj_voice_ctx",
                "macros": {
                    "alpha": "macros/alpha.yaml",
                    "beta": "macros/beta.yaml",
                },
            },
            sort_keys=False,
        )
    )
    for name, title in [("alpha", "Dashboard A"), ("beta", "Dashboard B")]:
        (project_dir / "macros" / f"{name}.yaml").write_text(
            yaml.safe_dump(
                {
                    "name": name,
                    "voice_phrases": ["open dashboard"],
                    "voice_when": {"class": "Firefox", "title": title},
                    "steps": [{"type": "Return", "value": "ok"}],
                },
                sort_keys=False,
            )
        )

    res = runner.invoke(app, ["lint-project", str(project_dir), "--json", "--no-session-check"])
    assert res.exit_code == 0, res.output
    data = json.loads(res.output)
    assert all(i.get("code") != "VOICE_PHRASE_COLLISION" for i in data["issues"])


def test_lint_project_warns_on_voice_context_export_gaps(tmp_path: Path) -> None:
    project_dir = tmp_path / "proj_voice_gap"
    (project_dir / "macros").mkdir(parents=True)
    (project_dir / "project.yaml").write_text(
        yaml.safe_dump(
            {
                "name": "proj_voice_gap",
                "macros": {"alpha": "macros/alpha.yaml"},
            },
            sort_keys=False,
        )
    )
    (project_dir / "macros" / "alpha.yaml").write_text(
        yaml.safe_dump(
            {
                "name": "alpha",
                "voice_phrases": ["open alpha"],
                "voice_when": {"app_id": "org.example.Alpha"},
                "steps": [{"type": "Return", "value_expr": '"ok"'}],
            },
            sort_keys=False,
        )
    )

    res = runner.invoke(app, ["lint-project", str(project_dir), "--json", "--no-session-check", "--check"])
    assert res.exit_code == 1, res.output
    data = json.loads(res.output)
    issues = [i for i in data["issues"] if i.get("code") == "VOICE_CONTEXT_EXPORT_GAP"]
    assert len(issues) == 2
    assert {i["backend"] for i in issues} == {"dragonfly", "talon"}
    assert all("app_id" in i["unsupported_fields"] for i in issues)


def test_lint_project_warns_on_autokey_scope_approximation_requirement(tmp_path: Path) -> None:
    project_dir = tmp_path / "proj_autokey_scope"
    (project_dir / "macros").mkdir(parents=True)
    (project_dir / "project.yaml").write_text(
        yaml.safe_dump(
            {
                "name": "proj_autokey_scope",
                "macros": {"main": "macros/main.yaml"},
                "bindings": [
                    {"keys": "Mod4+M", "macro": "main", "when": {"class": "Firefox"}},
                ],
            },
            sort_keys=False,
        )
    )
    (project_dir / "macros" / "main.yaml").write_text(
        yaml.safe_dump(
            {
                "name": "main",
                "steps": [{"type": "TypeText", "text": "hello"}],
            },
            sort_keys=False,
        )
    )

    res = runner.invoke(app, ["lint-project", str(project_dir), "--json", "--no-session-check", "--check"])
    assert res.exit_code == 1, res.output
    data = json.loads(res.output)
    issues = [i for i in data["issues"] if i.get("code") == "AUTOKEY_SCOPE_APPROXIMATION_REQUIRED"]
    assert len(issues) == 1
    assert issues[0]["trigger_kind"] == "binding"
    assert issues[0]["trigger"] == "Mod4+M"


def test_lint_project_warns_on_espanso_wayland_scope_and_composites(tmp_path: Path) -> None:
    project_dir = tmp_path / "proj_espanso_wayland"
    (project_dir / "macros").mkdir(parents=True)
    (project_dir / "project.yaml").write_text(
        yaml.safe_dump(
            {
                "name": "proj_espanso_wayland",
                "settings": {"desktop_backend": "wayland"},
                "macros": {
                    "firefox": "macros/firefox.yaml",
                    "inbox": "macros/inbox.yaml",
                },
                "hotstrings": [
                    {"trigger": ":ff", "macro": "firefox", "mode": "return", "when": {"class": "Firefox"}},
                    {"trigger": ":in", "macro": "inbox", "mode": "return", "when": {"title": "Inbox"}},
                ],
            },
            sort_keys=False,
        )
    )
    for name in ["firefox", "inbox"]:
        (project_dir / "macros" / f"{name}.yaml").write_text(
            yaml.safe_dump(
                {
                    "name": name,
                    "steps": [{"type": "Return", "value_expr": '"ok"'}],
                },
                sort_keys=False,
            )
        )

    res = runner.invoke(app, ["lint-project", str(project_dir), "--json", "--no-session-check"])
    assert res.exit_code == 0, res.output
    data = json.loads(res.output)
    codes = {i.get("code") for i in data["issues"]}
    assert "ESPANSO_APP_SCOPE_WAYLAND" in codes
    assert "ESPANSO_SCOPE_COMPOSITE_CONFIG" in codes


def test_lint_project_warns_on_espanso_unsupported_scope_fields(tmp_path: Path) -> None:
    project_dir = tmp_path / "proj_espanso_gap"
    (project_dir / "macros").mkdir(parents=True)
    (project_dir / "project.yaml").write_text(
        yaml.safe_dump(
            {
                "name": "proj_espanso_gap",
                "macros": {"main": "macros/main.yaml"},
                "hotstrings": [
                    {"trigger": ":main", "macro": "main", "mode": "return", "when": {"workspace": "2:web"}},
                ],
            },
            sort_keys=False,
        )
    )
    (project_dir / "macros" / "main.yaml").write_text(
        yaml.safe_dump(
            {
                "name": "main",
                "steps": [{"type": "Return", "value_expr": '"ok"'}],
            },
            sort_keys=False,
        )
    )

    res = runner.invoke(app, ["lint-project", str(project_dir), "--json", "--no-session-check", "--check"])
    assert res.exit_code == 1, res.output
    data = json.loads(res.output)
    issues = [i for i in data["issues"] if i.get("code") == "ESPANSO_SCOPE_EXPORT_GAP"]
    assert len(issues) == 1
    assert issues[0]["trigger"] == ":main"
    assert "workspace" in issues[0]["unsupported_fields"]


def test_lint_project_warns_on_xremap_runtime_only_scope_fields(tmp_path: Path) -> None:
    project_dir = tmp_path / "proj_xremap_gap"
    (project_dir / "macros").mkdir(parents=True)
    (project_dir / "project.yaml").write_text(
        yaml.safe_dump(
            {
                "name": "proj_xremap_gap",
                "macros": {"main": "macros/main.yaml"},
                "bindings": [
                    {
                        "keys": "Mod4+M",
                        "macro": "main",
                        "when": {
                            "class": "Firefox",
                            "title": "Inbox .*",
                            "title_regex": True,
                            "workspace": "2:web",
                            "focused": True,
                        },
                    }
                ],
            },
            sort_keys=False,
        )
    )
    (project_dir / "macros" / "main.yaml").write_text(
        yaml.safe_dump(
            {
                "name": "main",
                "steps": [{"type": "TypeText", "text": "hello"}],
            },
            sort_keys=False,
        )
    )

    res = runner.invoke(app, ["lint-project", str(project_dir), "--json", "--no-session-check"])
    assert res.exit_code == 0, res.output
    data = json.loads(res.output)
    issues = [i for i in data["issues"] if i.get("code") == "XREMAP_SCOPE_EXPORT_GAP"]
    assert len(issues) == 1
    assert issues[0]["trigger"] == "Mod4+M"
    assert "workspace" in issues[0]["unsupported_fields"]
    assert "focused" in issues[0]["unsupported_fields"]
    assert "title_regex" not in issues[0]["unsupported_fields"]


def test_lint_project_warns_when_legacy_trigger_exports_keep_scope_runtime_only(tmp_path: Path) -> None:
    project_dir = tmp_path / "proj_trigger_runtime"
    (project_dir / "macros").mkdir(parents=True)
    (project_dir / "project.yaml").write_text(
        yaml.safe_dump(
            {
                "name": "proj_trigger_runtime",
                "settings": {"desktop_backend": "wayland"},
                "macros": {"main": "macros/main.yaml"},
                "bindings": [
                    {
                        "keys": "Mod4+M",
                        "macro": "main",
                        "when": {
                            "class": "Firefox",
                            "workspace": "2:web",
                        },
                    }
                ],
            },
            sort_keys=False,
        )
    )
    (project_dir / "macros" / "main.yaml").write_text(
        yaml.safe_dump(
            {
                "name": "main",
                "steps": [{"type": "TypeText", "text": "hello"}],
            },
            sort_keys=False,
        )
    )

    res = runner.invoke(app, ["lint-project", str(project_dir), "--json", "--no-session-check", "--check"])
    assert res.exit_code == 1, res.output
    data = json.loads(res.output)
    codes = {i.get("code") for i in data["issues"]}
    assert "KEYD_SCOPE_RUNTIME_ONLY" in codes
    assert "KANATA_SCOPE_RUNTIME_ONLY" in codes
    assert "KMONAD_SCOPE_RUNTIME_ONLY" in codes
    assert "SXHKD_SCOPE_RUNTIME_ONLY" in codes
    assert "KMONAD_TRIGGER_SHAPE_CHANGE" in codes
    assert "SXHKD_X11_ONLY" in codes
    keyd_issue = next(i for i in data["issues"] if i.get("code") == "KEYD_SCOPE_RUNTIME_ONLY")
    assert keyd_issue["trigger"] == "Mod4+M"
    assert "class" in keyd_issue["runtime_only_fields"]
    assert "workspace" in keyd_issue["runtime_only_fields"]


def test_lint_project_warns_when_kmonad_needs_selector_sublayers_for_collisions(tmp_path: Path) -> None:
    project_dir = tmp_path / "proj_kmonad_collision"
    (project_dir / "macros").mkdir(parents=True)
    (project_dir / "project.yaml").write_text(
        yaml.safe_dump(
            {
                "name": "proj_kmonad_collision",
                "macros": {
                    "alpha": "macros/alpha.yaml",
                    "beta": "macros/beta.yaml",
                },
                "bindings": [
                    {"keys": "Mod4+P", "macro": "alpha"},
                    {"keys": "Control+P", "macro": "beta"},
                ],
            },
            sort_keys=False,
        )
    )
    for name in ["alpha", "beta"]:
        (project_dir / "macros" / f"{name}.yaml").write_text(
            yaml.safe_dump(
                {
                    "name": name,
                    "steps": [{"type": "Return", "value_expr": '"ok"'}],
                },
                sort_keys=False,
            )
        )

    res = runner.invoke(app, ["lint-project", str(project_dir), "--json", "--no-session-check"])
    assert res.exit_code == 0, res.output
    data = json.loads(res.output)
    collision = next(i for i in data["issues"] if i.get("code") == "KMONAD_COLLISION_SELECTOR_LAYER")
    assert collision["parsed_key"] == "p"
    assert collision["triggers"] == ["Control+P", "Mod4+P"]


def test_lint_project_warns_on_voice_phrase_normalization_quality_issues(tmp_path: Path) -> None:
    project_dir = tmp_path / "proj_voice_quality"
    (project_dir / "macros").mkdir(parents=True)
    (project_dir / "project.yaml").write_text(
        yaml.safe_dump(
            {
                "name": "proj_voice_quality",
                "macros": {"alpha": "macros/alpha.yaml"},
            },
            sort_keys=False,
        )
    )
    (project_dir / "macros" / "alpha.yaml").write_text(
        yaml.safe_dump(
            {
                "name": "alpha",
                "voice_phrases": ["Open-URL", "open url", "!!!"],
                "steps": [{"type": "Return", "value": "ok"}],
            },
            sort_keys=False,
        )
    )

    res = runner.invoke(app, ["lint-project", str(project_dir), "--json", "--no-session-check", "--check"])
    assert res.exit_code == 1, res.output
    data = json.loads(res.output)

    normalized = [i for i in data["issues"] if i.get("code") == "VOICE_PHRASE_NORMALIZED"]
    assert len(normalized) == 1
    assert normalized[0]["raw_phrase"] == "Open-URL"
    assert normalized[0]["normalized_phrase"] == "open url"

    empty = [i for i in data["issues"] if i.get("code") == "VOICE_PHRASE_EMPTY_AFTER_NORMALIZATION"]
    assert len(empty) == 1
    assert empty[0]["raw_phrase"] == "!!!"

    redundant = [i for i in data["issues"] if i.get("code") == "VOICE_PHRASE_REDUNDANT_VARIANT"]
    assert len(redundant) == 1
    assert redundant[0]["normalized_phrase"] == "open url"
    assert redundant[0]["raw_phrases"] == ["Open-URL", "open url"]



def test_lint_project_warns_on_short_global_voice_phrases(tmp_path: Path) -> None:
    project_dir = tmp_path / "proj_voice_short"
    (project_dir / "macros").mkdir(parents=True)
    (project_dir / "project.yaml").write_text(
        yaml.safe_dump(
            {
                "name": "proj_voice_short",
                "macros": {"undo": "macros/undo.yaml"},
            },
            sort_keys=False,
        )
    )
    (project_dir / "macros" / "undo.yaml").write_text(
        yaml.safe_dump(
            {
                "name": "undo",
                "voice_phrases": ["undo"],
                "steps": [{"type": "Return", "value": "ok"}],
            },
            sort_keys=False,
        )
    )

    res = runner.invoke(app, ["lint-project", str(project_dir), "--json", "--no-session-check"])
    assert res.exit_code == 0, res.output
    data = json.loads(res.output)
    issues = [i for i in data["issues"] if i.get("code") == "VOICE_PHRASE_SHORT_GLOBAL"]
    assert len(issues) == 1
    assert issues[0]["target"] == "undo"
    assert issues[0]["phrases"] == ["undo"]



def test_lint_project_does_not_warn_on_short_voice_phrases_when_context_scoped(tmp_path: Path) -> None:
    project_dir = tmp_path / "proj_voice_short_scoped"
    (project_dir / "macros").mkdir(parents=True)
    (project_dir / "project.yaml").write_text(
        yaml.safe_dump(
            {
                "name": "proj_voice_short_scoped",
                "macros": {"undo": "macros/undo.yaml"},
            },
            sort_keys=False,
        )
    )
    (project_dir / "macros" / "undo.yaml").write_text(
        yaml.safe_dump(
            {
                "name": "undo",
                "voice_phrases": ["undo"],
                "voice_when": {"class": "Firefox", "title": "Editor"},
                "steps": [{"type": "Return", "value": "ok"}],
            },
            sort_keys=False,
        )
    )

    res = runner.invoke(app, ["lint-project", str(project_dir), "--json", "--no-session-check"])
    assert res.exit_code == 0, res.output
    data = json.loads(res.output)
    assert all(i.get("code") != "VOICE_PHRASE_SHORT_GLOBAL" for i in data["issues"])


def test_lint_project_warns_on_portal_trigger_export_gap(tmp_path: Path) -> None:
    project_dir = tmp_path / "proj_portal_gap"
    (project_dir / "macros").mkdir(parents=True)
    (project_dir / "project.yaml").write_text(
        yaml.safe_dump(
            {
                "name": "proj_portal_gap",
                "macros": {"main": "macros/main.yaml"},
                "bindings": [
                    {"keys": "Ctrl+ä", "macro": "main"},
                ],
            },
            sort_keys=False,
        )
    )
    (project_dir / "macros" / "main.yaml").write_text(
        yaml.safe_dump(
            {
                "name": "main",
                "steps": [{"type": "Return", "value": "ok"}],
            },
            sort_keys=False,
        )
    )

    res = runner.invoke(app, ["lint-project", str(project_dir), "--json", "--no-session-check", "--check"])
    assert res.exit_code == 1, res.output
    data = json.loads(res.output)
    issues = [i for i in data["issues"] if i.get("code") == "PORTAL_TRIGGER_EXPORT_GAP"]
    assert len(issues) == 1
    assert issues[0]["trigger"] == "Ctrl+ä"


def test_lint_project_warns_on_portal_runtime_only_scope(tmp_path: Path) -> None:
    project_dir = tmp_path / "proj_portal_scope"
    (project_dir / "macros").mkdir(parents=True)
    (project_dir / "project.yaml").write_text(
        yaml.safe_dump(
            {
                "name": "proj_portal_scope",
                "macros": {"main": "macros/main.yaml"},
                "bindings": [
                    {"keys": "Mod4+Shift+P", "macro": "main", "when": {"class": "Firefox", "title": "Docs"}},
                ],
            },
            sort_keys=False,
        )
    )
    (project_dir / "macros" / "main.yaml").write_text(
        yaml.safe_dump(
            {
                "name": "main",
                "steps": [{"type": "Return", "value": "ok"}],
            },
            sort_keys=False,
        )
    )

    res = runner.invoke(app, ["lint-project", str(project_dir), "--json", "--no-session-check"])
    assert res.exit_code == 0, res.output
    data = json.loads(res.output)
    issues = [i for i in data["issues"] if i.get("code") == "PORTAL_SCOPE_RUNTIME_ONLY"]
    assert len(issues) == 1
    assert issues[0]["trigger"] == "Mod4+Shift+P"
    assert issues[0]["runtime_only_fields"] == ["class", "title"]


def test_lint_project_warns_on_long_literal_typed_text(tmp_path: Path) -> None:
    project_dir = tmp_path / "proj_long_text"
    (project_dir / "macros").mkdir(parents=True)
    (project_dir / "project.yaml").write_text(
        yaml.safe_dump(
            {
                "name": "proj_long_text",
                "macros": {"snippet": "macros/snippet.yaml"},
            },
            sort_keys=False,
        )
    )
    (project_dir / "macros" / "snippet.yaml").write_text(
        yaml.safe_dump(
            {
                "name": "snippet",
                "steps": [
                    {
                        "type": "TypeText",
                        "backend": "native",
                        "text": "This is a deliberately long literal snippet that should be linted because per-character typing is slower than a clipboard lane on Linux.",
                    }
                ],
            },
            sort_keys=False,
        )
    )

    res = runner.invoke(app, ["lint-project", str(project_dir), "--json", "--no-session-check"])
    assert res.exit_code == 0, res.output
    data = json.loads(res.output)
    issues = [i for i in data["issues"] if i.get("code") == "LONG_TYPED_TEXT_LITERAL"]
    assert len(issues) == 1
    assert issues[0]["step_type"] == "TypeText"
    assert "backend=clipboard" in str(issues[0]["suggestion"])


def test_lint_project_warns_on_structured_literal_typed_text(tmp_path: Path) -> None:
    project_dir = tmp_path / "proj_structured_text"
    (project_dir / "macros").mkdir(parents=True)
    (project_dir / "project.yaml").write_text(
        yaml.safe_dump(
            {
                "name": "proj_structured_text",
                "macros": {"form": "macros/form.yaml"},
            },
            sort_keys=False,
        )
    )
    (project_dir / "macros" / "form.yaml").write_text(
        yaml.safe_dump(
            {
                "name": "form",
                "steps": [
                    {
                        "type": "TypeText",
                        "backend": "auto",
                        "text": "Email:	person@example.com\nCompany:	Very Long Company Name",
                    }
                ],
            },
            sort_keys=False,
        )
    )

    res = runner.invoke(app, ["lint-project", str(project_dir), "--json", "--no-session-check"])
    assert res.exit_code == 0, res.output
    data = json.loads(res.output)
    issues = [i for i in data["issues"] if i.get("code") == "STRUCTURED_TYPED_TEXT_LITERAL"]
    assert len(issues) == 1
    assert issues[0]["step_type"] == "TypeText"
    assert "segment-paste-text" in str(issues[0]["suggestion"])


def test_lint_project_surfaces_macro_route_drift(tmp_path: Path) -> None:
    project_dir = tmp_path / "proj_route_drift"
    (project_dir / "macros").mkdir(parents=True)
    (project_dir / "project.yaml").write_text(
        yaml.safe_dump(
            {
                "name": "proj_route_drift",
                "settings": {"desktop_backend": "wayland"},
                "macros": {
                    "snippet": "macros/snippet.yaml",
                    "remap": "macros/remap.yaml",
                    "vision": "macros/vision.yaml",
                    "sync": "macros/sync.yaml",
                },
                "bindings": [
                    {"keys": "Mod4+R", "macro": "remap"},
                    {"keys": "Mod4+V", "macro": "vision"},
                ],
                "hotstrings": [{"trigger": ":em", "macro": "snippet"}],
                "bus_watchers": [{"name": "sync-watch", "event": "proj.sync", "macro": "sync"}],
            },
            sort_keys=False,
        )
    )
    (project_dir / "macros" / "snippet.yaml").write_text(
        yaml.safe_dump(
            {
                "name": "snippet",
                "steps": [{"type": "TypeText", "text": "hello from snippet"}],
            },
            sort_keys=False,
        )
    )
    (project_dir / "macros" / "remap.yaml").write_text(
        yaml.safe_dump(
            {
                "name": "remap",
                "steps": [{"type": "Key", "keys": "F5"}],
            },
            sort_keys=False,
        )
    )
    (project_dir / "macros" / "vision.yaml").write_text(
        yaml.safe_dump(
            {
                "name": "vision",
                "steps": [
                    {"type": "WaitForImage", "needle_path": "assets/button.png"},
                    {"type": "MouseClickAt", "x": 20, "y": 40},
                ],
            },
            sort_keys=False,
        )
    )
    (project_dir / "macros" / "sync.yaml").write_text(
        yaml.safe_dump(
            {
                "name": "sync",
                "steps": [{"type": "RunShell", "command": "echo sync"}],
            },
            sort_keys=False,
        )
    )
    (project_dir / "assets").mkdir()
    (project_dir / "assets" / "button.png").write_bytes(b"png")

    res = runner.invoke(app, ["lint-project", str(project_dir), "--json", "--no-session-check"])
    assert res.exit_code == 0, res.output
    data = json.loads(res.output)

    by_code = {issue["code"]: issue for issue in data["issues"] if str(issue.get("code", "")).startswith("ROUTE_DRIFT_")}
    assert by_code["ROUTE_DRIFT_TEXT_TIER"]["fit"] in {"strong", "good"}
    assert "Espanso" in by_code["ROUTE_DRIFT_TEXT_TIER"]["tools"]
    assert by_code["ROUTE_DRIFT_REMAPPER_TIER"]["activation_route_id"] in {"remapper-route", "native-trigger-route"}
    assert "xremap" in by_code["ROUTE_DRIFT_REMAPPER_TIER"]["tools"]
    assert by_code["ROUTE_DRIFT_HELPER_BOUNDARY"]["severity"] == "warning"
    assert "pointer_injection" in by_code["ROUTE_DRIFT_HELPER_BOUNDARY"]["evidence"]
    assert by_code["ROUTE_DRIFT_WATCHER_SERVICE"]["route_id"] == "watcher-service"


def test_lint_project_emits_promotion_gate_issues(tmp_path: Path) -> None:
    project_dir = tmp_path / "proj_promotion_gates"
    (project_dir / "macros").mkdir(parents=True)
    (project_dir / "assets").mkdir()
    (project_dir / "assets" / "button.png").write_bytes(b"png")
    (project_dir / "project.yaml").write_text(
        yaml.safe_dump(
            {
                "name": "proj_promotion_gates",
                "settings": {"desktop_backend": "wayland"},
                "macros": {
                    "snippet": "macros/snippet.yaml",
                    "vision": "macros/vision.yaml",
                    "sync": "macros/sync.yaml",
                },
                "hotstrings": [{"trigger": ":ty", "macro": "snippet"}],
                "bindings": [{"keys": "Mod4+V", "macro": "vision"}],
                "bus_watchers": [{"name": "sync-watch", "event": "proj.sync", "macro": "sync"}],
            },
            sort_keys=False,
        )
    )
    (project_dir / "macros" / "snippet.yaml").write_text(
        yaml.safe_dump({"name": "snippet", "steps": [{"type": "TypeText", "text": "hello from snippet lane"}]}, sort_keys=False)
    )
    (project_dir / "macros" / "vision.yaml").write_text(
        yaml.safe_dump(
            {
                "name": "vision",
                "steps": [
                    {"type": "WaitForImage", "needle_path": "assets/button.png"},
                    {"type": "MouseClickAt", "x": 10, "y": 20},
                ],
            },
            sort_keys=False,
        )
    )
    (project_dir / "macros" / "sync.yaml").write_text(
        yaml.safe_dump({"name": "sync", "steps": [{"type": "WaitForBusEvent", "event": "proj.sync"}]}, sort_keys=False)
    )

    res = runner.invoke(app, ["lint-project", str(project_dir), "--json", "--no-session-check"])
    assert res.exit_code == 0, res.output
    data = json.loads(res.output)

    gate_issues = [issue for issue in data["issues"] if str(issue.get("code", "")).startswith("PROMOTION_GATE_")]
    by_code = {issue["code"]: issue for issue in gate_issues}
    assert "PROMOTION_GATE_REVIEW" in by_code or "PROMOTION_GATE_FAIL" in by_code
    claim_issue = next(issue for issue in gate_issues if issue.get("gate_id") == "claim-discipline-gate")
    assert claim_issue["status"] in {"review", "fail"}
    assert "text-package-export" in claim_issue["affected_surfaces"]

    evidence_issues = [issue for issue in data["issues"] if str(issue.get("code", "")).startswith("PROMOTION_EVIDENCE_")]
    assert evidence_issues
    by_code = {issue["code"]: issue for issue in evidence_issues}
    assert "PROMOTION_EVIDENCE_MISSING" in by_code or "PROMOTION_EVIDENCE_PARTIAL" in by_code
    claim_evidence = next(issue for issue in evidence_issues if issue.get("evidence_id") == "gate:claim-discipline-gate")
    assert claim_evidence["evidence_status"] in {"missing", "partial"}
    assert "docs/VHK_TARGET_CLAIMS.yaml" in claim_evidence["required_artifacts"]
