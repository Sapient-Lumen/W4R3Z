from __future__ import annotations

import json
from pathlib import Path

import yaml
from typer.testing import CliRunner

from vhk.cli import app


runner = CliRunner()


def _make_project(tmp_path: Path) -> Path:
    project_dir = tmp_path / "proj"
    (project_dir / "macros").mkdir(parents=True)

    (project_dir / "macros" / "reply.yaml").write_text(
        yaml.safe_dump(
            {
                "name": "reply",
                "steps": [
                    {"type": "PromptForm", "title": "Reply", "fields": [{"name": "name", "label": "Name"}]},
                    {"type": "TypeText", "text": "Hello ${reply.name}"},
                ],
            },
            sort_keys=False,
        )
    )

    (project_dir / "project.yaml").write_text(
        yaml.safe_dump(
            {
                "name": "proj",
                "settings": {"desktop_backend": "wayland"},
                "bindings": [{"keys": "Mod4+V", "macro": "reply"}],
            },
            sort_keys=False,
        )
    )
    return project_dir



def test_gen_native_install_pack_writes_docs_handoff_and_scripts(tmp_path: Path) -> None:
    project_dir = _make_project(tmp_path)

    res = runner.invoke(app, ["gen-native-install-pack", str(project_dir), "--force", "--quiet"])
    assert res.exit_code == 0, res.output

    doc = (project_dir / "docs" / "VHK_NATIVE_INSTALL.md").read_text()
    plan = json.loads((project_dir / "docs" / "VHK_NATIVE_INSTALL_PLAN.json").read_text())
    script = (project_dir / "scripts" / "vhk_refresh_native_install_pack.sh").read_text()

    assert "# VHK native install pack for proj" in doc
    assert "## Native install posture" in doc
    assert "## XDG-local install defaults" in doc
    assert "~/.local/bin" in doc

    story = dict(plan["native_install_story"])
    assert story["app_id"] == "io.visualhotkey.proj"
    assert story["command_name"] == "vhk-proj"
    assert story["bundle_kind"] == "project"
    assert story["xdg_defaults"]["install_root"] == "${XDG_DATA_HOME}/vhk/apps/vhk-proj"

    assert "vhk gen-native-install-pack . --force --quiet" in script
    assert "vhk gen-runtime-embed-pack . --force --quiet" in script

    native_root = project_dir / "build" / "publish" / "proj" / "native"
    assert (native_root / "README.md").exists()
    assert (native_root / "vhk_native_install_handoff.json").exists()
    assert (native_root / "assemble_native_app.sh").exists()
    assert (native_root / "install_xdg_local_app.sh").exists()
    assert (native_root / "uninstall_xdg_local_app.sh").exists()
    assert (native_root / "smoke_test_native_install.sh").exists()

    launcher = (native_root / "app" / "bin" / "vhk-proj").read_text()
    desktop = (native_root / "app" / "share" / "applications" / "io.visualhotkey.proj.desktop").read_text()
    assert 'EMBEDDED_VHK="$APP_ROOT/lib/vhk-runtime/bin/vhk"' in launcher
    assert 'SELF_PATH="$(resolve_self_path)"' in launcher
    assert 'APP_ROOT="${APP_ROOT:-$(CDPATH= cd -- "$(dirname -- "$SELF_PATH")/.." && pwd)}"' in launcher
    assert 'CACHE_ROOT="${VHK_CACHE_ROOT:-$XDG_CACHE_HOME/vhk/apps/vhk-proj}"' in launcher
    assert 'STATE_ROOT="${VHK_STATE_ROOT:-$XDG_STATE_HOME/vhk/apps/vhk-proj}"' in launcher
    assert 'materialize-bundle "$BUNDLE_PATH" "$MATERIALIZED_ROOT"' in launcher
    assert 'DOC_ROOT="$APP_ROOT/share/doc/vhk"' in launcher
    assert 'APP_HOME_DOC="$DOC_ROOT/VHK_APP_HOME.md"' in launcher
    assert '--refresh-desktop-actions' in launcher
    assert '--pin-entry' in launcher
    assert '--list-pinned-entries' in launcher
    assert 'STATUS_ROOT="$STATE_ROOT/status"' in launcher
    assert 'STATUS_JSON="$STATUS_ROOT/VHK_APP_STATUS.json"' in launcher
    assert 'STATUS_MD="$STATUS_ROOT/VHK_APP_STATUS.md"' in launcher
    assert 'SERVICE_UNIT_BASE="vhk-busd-proj"' in launcher
    assert '--home-json|--support-json' in launcher
    assert '--status-json' in launcher
    assert '--open-status-report' in launcher
    assert 'refresh_status_report() {' in launcher
    assert 'refresh_desktop_actions() {' in launcher
    assert 'record_recent_entry() {' in launcher
    assert 'exec gio open "$target"' in launcher
    assert 'exec xdg-open "$target"' in launcher
    assert 'print_status()' in launcher
    assert 'set -- palette "$PROJECT_ROOT"' in launcher
    assert 'exec "$VHK_CMD" inspect-bundle "$BUNDLE_PATH"' in launcher

    assert '[Desktop Action OpenPalette]' in desktop
    assert '[Desktop Action OpenHomeDoc]' in desktop
    assert '[Desktop Action OpenSupportGuide]' in desktop
    assert '[Desktop Action OpenServiceGuide]' in desktop
    assert '[Desktop Action OpenStatusReport]' in desktop
    assert '[Desktop Action InspectBundle]' in desktop
    assert '[Desktop Action RefreshBundle]' in desktop
    assert '[Desktop Action RefreshLauncherActions]' in desktop
    assert '__VHK_LAUNCHER_EXEC__' in desktop

    assemble = (native_root / "assemble_native_app.sh").read_text()
    assert 'sh "$PUBLISH_ROOT/bundle_release.sh"' in assemble
    assert 'cp "$DIST_DIR/proj.zip" "$APP_ROOT/share/vhk/project/proj.zip"' in assemble
    assert 'bootstrap_runtime_at_target.sh' in assemble

    install_script = (native_root / "install_xdg_local_app.sh").read_text()
    assert 'XDG_DATA_HOME="${XDG_DATA_HOME:-$HOME/.local/share}"' in install_script
    assert 'VHK_BIN_HOME="${VHK_BIN_HOME:-$HOME/.local/bin}"' in install_script
    assert 'LAUNCHER_PATH="$VHK_BIN_HOME/vhk-proj"' in install_script
    assert 'ln -sfn "$APP_DEST/bin/vhk-proj" "$LAUNCHER_PATH"' in install_script
    assert 'VHK_DESKTOP_TEMPLATE="$APP_DEST/share/applications/io.visualhotkey.proj.desktop"' in install_script
    assert "text = text.replace('__VHK_LAUNCHER_EXEC__', quote(launcher))" in install_script
    assert "text = text.replace('__VHK_LAUNCHER_TRYEXEC__', launcher)" in install_script
    assert 'if "$LAUNCHER_PATH" --refresh-desktop-actions >/dev/null 2>&1; then' in install_script

    home_doc = (native_root / "app" / "share" / "doc" / "vhk" / "VHK_APP_HOME.md").read_text()
    home_json = json.loads((native_root / "app" / "share" / "doc" / "vhk" / "VHK_APP_HOME.json").read_text())
    assert '# VHK app home for proj' in home_doc
    assert '## Packaged docs' in home_doc
    assert home_json['native_install']['command_name'] == 'vhk-proj'
    assert home_json['native_install']['state_root'].endswith('/vhk/apps/vhk-proj')
    assert home_json['bundled_docs'][0]['kind'] == 'home'
    assert home_json['service']['mode'] == 'environment-only'

    refresh_actions = (native_root / "refresh_desktop_actions.sh").read_text()
    assert '--refresh-desktop-actions' in refresh_actions

    smoke = (native_root / "smoke_test_native_install.sh").read_text()
    assert 'sh "$SCRIPT_DIR/assemble_native_app.sh"' in smoke
    assert 'XDG_DATA_HOME="$SMOKE_ROOT/data" VHK_BIN_HOME="$SMOKE_ROOT/bin" sh "$SCRIPT_DIR/install_xdg_local_app.sh"' in smoke
    assert 'test -x "$SMOKE_ROOT/bin/vhk-proj"' in smoke
    assert 'test -x "$SCRIPT_DIR/refresh_desktop_actions.sh"' in smoke
    assert 'grep -q "Actions=OpenPalette;OpenHomeDoc;OpenSupportGuide;OpenServiceGuide;OpenStatusReport;InspectBundle;RefreshBundle;RefreshLauncherActions;"' in smoke
    assert 'test -f "$SMOKE_ROOT/data/vhk/apps/vhk-proj/share/doc/vhk/VHK_APP_HOME.md"' in smoke
    assert 'test -f "$SMOKE_ROOT/data/vhk/apps/vhk-proj/share/doc/vhk/VHK_APP_HOME.json"' in smoke



def test_gen_native_install_pack_stage_target_keeps_profile_context(tmp_path: Path) -> None:
    project_dir = _make_project(tmp_path)

    res = runner.invoke(
        app,
        [
            "gen-native-install-pack",
            str(project_dir),
            "--bundle-target-profile",
            "gnome-wayland",
            "--app-id",
            "org.example.vhkdemo",
            "--python-cmd",
            "python3.12",
            "--force",
            "--quiet",
        ],
    )
    assert res.exit_code == 0, res.output

    plan = json.loads((project_dir / "docs" / "VHK_NATIVE_INSTALL_PLAN.json").read_text())
    story = dict(plan["native_install_story"])
    assert story["bundle_kind"] == "release-stage"
    assert story["bundle_profile_id"] == "gnome-wayland"
    assert story["app_id"] == "org.example.vhkdemo"
    assert story["python_cmd"] == "python3.12"

    native_root = project_dir / "build" / "publish" / "proj-gnome-wayland" / "native"
    manifest = json.loads((native_root / "vhk_native_install_handoff.json").read_text())
    assert manifest["bundle_profile_id"] == "gnome-wayland"
    assert manifest["command_name"] == "vhk-vhkdemo"

    refresh = (native_root / "refresh_native_install_inputs.sh").read_text()
    assert "--bundle-target-profile gnome-wayland" in refresh

    assemble = (native_root / "assemble_native_app.sh").read_text()
    assert 'cp "$DIST_DIR/proj-gnome-wayland.zip" "$APP_ROOT/share/vhk/project/proj-gnome-wayland.zip"' in assemble

    desktop = (native_root / "app" / "share" / "applications" / "org.example.vhkdemo.desktop").read_text()
    assert "[Desktop Action OpenPalette]" in desktop
    assert "[Desktop Action OpenHomeDoc]" in desktop
    assert "[Desktop Action OpenSupportGuide]" in desktop
    assert "[Desktop Action OpenServiceGuide]" in desktop
    assert "[Desktop Action OpenStatusReport]" in desktop
    assert "[Desktop Action InspectBundle]" in desktop
    assert "[Desktop Action RefreshLauncherActions]" in desktop
    assert "Exec=__VHK_LAUNCHER_EXEC__" in desktop
    assert "TryExec=__VHK_LAUNCHER_TRYEXEC__" in desktop
