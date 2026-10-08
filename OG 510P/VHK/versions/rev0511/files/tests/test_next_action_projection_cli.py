from pathlib import Path

from vhk.cli import _render_i3_stack_next_action_json_script, _render_i3_stack_next_action_script, _render_i3_stack_state_json_script, _render_i3_stack_state_script


def test_next_action_and_stack_scripts_carry_forced_receipt_projection_and_debt_fields(tmp_path: Path):
    next_action_script = _render_i3_stack_next_action_json_script(unit_base="vhk-i3-busd-hotkeys", project_dir=tmp_path)
    next_action_summary_script = _render_i3_stack_next_action_script(project_dir=tmp_path)
    stack_state_json_script = _render_i3_stack_state_json_script(
        project_dir=tmp_path,
        unit_base="vhk-i3-busd-hotkeys",
        vhk_cmd="python -m vhk.cli",
        vhk_pythonpath="src",
    )
    stack_state_script = _render_i3_stack_state_script(project_dir=tmp_path)

    assert "inspect_forced_receipt_before_clean_replacement" in next_action_script
    assert "clean_replacement_required" in next_action_script
    assert "recommendation_trace_selected_macro_handoff_clean_replacement_required" in next_action_summary_script
    assert "selected_action_clean_replacement_required" in stack_state_json_script
    assert "selected_macro_handoff_clean_replacement_required" in stack_state_json_script
    assert "primary_action_clean_replacement_required" in stack_state_script
