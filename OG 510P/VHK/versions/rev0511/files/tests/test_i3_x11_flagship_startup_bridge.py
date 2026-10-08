from __future__ import annotations

from vhk.project.i3_x11_flagship_startup_bridge import (
    FLAGSHIP_RUNTIME_KIND,
    build_i3_x11_flagship_startup_bridge_contract,
    summarize_i3_x11_flagship_startup_bridge_contract,
)


def test_build_i3_x11_flagship_startup_bridge_contract_prefers_graphical_session_owner() -> None:
    contract = build_i3_x11_flagship_startup_bridge_contract(unit_base="vhk-busd-demo", project_root="/tmp/demo")

    assert contract["runtime_kind"] == FLAGSHIP_RUNTIME_KIND
    assert contract["desktop_backend"] == "x11"
    assert contract["window_manager"] == "i3"
    assert contract["helper_paths"]["autostart_desktop"] == "autostart/vhk-busd-demo.desktop"
    assert contract["helper_paths"]["sync_session_activation_env"] == "bin/sync_session_activation_env.sh"
    assert contract["helper_paths"]["install_user_session"] == "install_user_session.sh"
    assert contract["helper_paths"]["verify_user_session_json"] == "verify_user_session_json.sh"
    assert contract["helper_paths"]["repair_user_session"] == "repair_user_session.sh"
    assert contract["helper_paths"]["uninstall_user_session"] == "uninstall_user_session.sh"
    assert contract["helper_paths"]["smoke_install"] == "smoke_install.sh"
    assert contract["session_target_policy"]["mode"] == "graphical-session-bound"
    assert contract["session_target_policy"]["binds_to_graphical_session"] is True
    assert contract["session_readiness_policy"]["mode"] == "exec-condition-session-ready"
    assert contract["session_readiness_policy"]["display_requirement"] == "x11-display"
    assert contract["session_readiness_policy"]["display_any_of"] == ["DISPLAY"]
    assert contract["startup_handoff_policy"]["mode"] == "graphical-target-primary-autostart-fallback"
    assert contract["startup_handoff_policy"]["primary_owner"] == "graphical-session.target"
    assert contract["startup_handoff_policy"]["install_toggles"]["default_install_autostart_bridge"] is False
    assert contract["install_contract"]["primary_startup_owner"] == "graphical-session.target"
    assert contract["install_contract"]["default_enable_user_unit"] is True
    assert contract["install_contract"]["default_install_autostart_bridge"] is False
    assert contract["llm_contract"]["preferred_dispatch_entrypoint"] == "bin/dispatch_macro_checked.sh <macro>"
    assert contract["llm_contract"]["runtime_repair_entrypoints"][:2] == [
        "verify_user_session_json.sh",
        "repair_user_session.sh",
    ]


def test_summarize_i3_x11_flagship_startup_bridge_contract_exposes_policy_digest() -> None:
    summary = summarize_i3_x11_flagship_startup_bridge_contract(
        build_i3_x11_flagship_startup_bridge_contract(unit_base="vhk-busd-demo", project_root="/tmp/demo")
    )

    assert summary["runtime_kind"] == FLAGSHIP_RUNTIME_KIND
    assert summary["window_manager"] == "i3"
    assert summary["desktop_backend"] == "x11"
    assert summary["primary_startup_owner"] == "graphical-session.target"
    assert summary["fallback_startup_owner"] == "xdg-autostart"
    assert summary["helper_count"] == 14
    assert summary["session_activation_policy"]["required"] is True
    assert summary["session_target_policy"]["binds_to_graphical_session"] is True
    assert summary["session_readiness_policy"]["display_requirement"] == "x11-display"
    assert summary["startup_handoff_policy"]["default_install_autostart_bridge"] is False
