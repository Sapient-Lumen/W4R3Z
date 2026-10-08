from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from micromax.host_limits import DEFAULT_HOSTCALL_RESULT_MAX_BYTES
from micromax.host_regex import (
    DEFAULT_REGEX_HAYSTACK_MAX_BYTES,
    DEFAULT_REGEX_TIMEOUT_SECONDS,
)
from micromax.regex_runtime import DEFAULT_REGEX_WORKER_MEMORY_HEADROOM_BYTES
from micromax.stdlib_resource import STDLIB_RESOURCE_NAME
from micromax_editor.effect_contracts import (
    ACTIVE_SEARCH_OWNER_ROW,
    HELP_HISTORY_OWNER_ROW,
    MARK_OWNER_ROW,
    PALETTE_RECENT_OWNER_ROW,
    PROMPT_HISTORY_OWNER_ROW,
    OPTION_STATE_OWNER_ROW,
    RECENT_FILES_OWNER_ROW,
    RECOVERY_OWNER_ROW,
    EFFECT_CONTRACT_HELP_DOC,
    EFFECT_CONTRACT_SCHEMA,
    effect_contract_help_markdown,
    effect_resource_contract,
    validate_effect_resource_contract,
)
from micromax_editor.hostcall_boundary import DEFAULT_FS_READ_MAX_BYTES, DEFAULT_SHELL_TIMEOUT_SECONDS
from micromax_editor.open_url_process import DEFAULT_OPEN_URL_TIMEOUT_SECONDS

ROOT = Path(__file__).resolve().parents[1]


def _rows_by_name(payload: dict[str, object]) -> dict[str, dict[str, object]]:
    rows = payload["rows"]
    assert isinstance(rows, list)
    return {str(row["name"]): row for row in rows if isinstance(row, dict)}


def test_effect_contracts_generate_live_high_risk_rows() -> None:
    payload = effect_resource_contract(rev=940)

    assert payload["schema"] == EFFECT_CONTRACT_SCHEMA
    assert payload["project"] == "micromax"
    assert validate_effect_resource_contract(payload) == []

    rows = _rows_by_name(payload)
    fs_read = rows["ed.fs-read"]
    assert fs_read["handler"] == "hc_ed_fs_read"
    assert fs_read["capability_option"] == "cap.fs-read"
    assert fs_read["effect_class"] == "filesystem-read"
    fs_read_budgets = fs_read["budgets"]
    assert isinstance(fs_read_budgets, dict)
    assert fs_read_budgets["input_max_bytes"] == DEFAULT_FS_READ_MAX_BYTES
    assert fs_read_budgets["result_max_bytes"] == DEFAULT_HOSTCALL_RESULT_MAX_BYTES

    open_url = rows["ed.open-url"]
    assert open_url["capability_option"] == "cap.open-url"
    assert open_url["effect_class"] == "external-browser-process"
    open_url_budgets = open_url["budgets"]
    assert isinstance(open_url_budgets, dict)
    assert open_url_budgets["timeout_seconds"] == DEFAULT_OPEN_URL_TIMEOUT_SECONDS

    shell = rows["ed.shell"]
    assert shell["capability_option"] == "cap.shell"
    shell_budgets = shell["budgets"]
    assert isinstance(shell_budgets, dict)
    assert shell_budgets["timeout_seconds"] == DEFAULT_SHELL_TIMEOUT_SECONDS

    regex = rows["re.search"]
    assert regex["surface"] == "vm-hostcall"
    regex_budgets = regex["budgets"]
    assert isinstance(regex_budgets, dict)
    assert regex_budgets["timeout_seconds"] == DEFAULT_REGEX_TIMEOUT_SECONDS
    assert (
        regex_budgets["linux_worker_memory_headroom_bytes"]
        == DEFAULT_REGEX_WORKER_MEMORY_HEADROOM_BYTES
    )

    escaped = rows["re.escape"]
    assert escaped["effect_class"] == "regex-escape"
    escaped_budgets = escaped["budgets"]
    assert isinstance(escaped_budgets, dict)
    assert escaped_budgets["input_max_bytes"] == DEFAULT_REGEX_HAYSTACK_MAX_BYTES
    assert "timeout_seconds" not in escaped_budgets
    assert "linux_worker_memory_headroom_bytes" not in escaped_budgets

    mark = rows[MARK_OWNER_ROW]
    assert mark["surface"] == "editor-owner"
    assert mark["effect_class"] == "retained-mark-navigation-authority"
    assert mark["capability_options"] == ["cap.mark-read", "cap.mark-jump"]
    assert mark["owner_methods_present"]["MarkRegisterSnapshot"] is True
    assert mark["owner_methods_present"]["snapshot_mark_group_state"] is True

    recent_files = rows[RECENT_FILES_OWNER_ROW]
    assert recent_files["surface"] == "editor-owner"
    assert recent_files["effect_class"] == "retained-path-history-authority"
    assert recent_files["capability_options"] == ["cap.recent-read", "cap.history-clear", "cap.persist"]
    assert recent_files["owner_methods_present"]["RecentFilesRegisterSnapshot"] is True
    assert recent_files["owner_methods_present"]["snapshot_recent_files_group_state"] is True

    palette_recent = rows[PALETTE_RECENT_OWNER_ROW]
    assert palette_recent["surface"] == "editor-owner"
    assert palette_recent["effect_class"] == "retained-command-launch-authority"
    assert palette_recent["capability_options"] == ["cap.command-read", "cap.action-read", "cap.history-clear"]
    assert palette_recent["owner_methods_present"]["PaletteRecentRegisterSnapshot"] is True
    assert palette_recent["owner_methods_present"]["snapshot_palette_recent_group_state"] is True

    active_search = rows[ACTIVE_SEARCH_OWNER_ROW]
    assert active_search["surface"] == "editor-owner"
    assert active_search["effect_class"] == "delayed-navigation-authority"
    assert active_search["capability_options"] == ["cap.search-read", "cap.search-replay"]
    assert active_search["owner_methods_present"]["ActiveSearchRegisterSnapshot"] is True
    assert active_search["owner_methods_present"]["snapshot_search_group_state"] is True

    prompt_history = rows[PROMPT_HISTORY_OWNER_ROW]
    assert prompt_history["surface"] == "editor-owner"
    assert prompt_history["effect_class"] == "durable-replay-history-authority"
    assert prompt_history["capability_options"] == ["cap.history-clear", "cap.persist"]
    assert prompt_history["owner_methods_present"]["PromptHistoryRegisterSnapshot"] is True
    assert prompt_history["owner_methods_present"]["snapshot_prompt_history_group_state"] is True

    help_history = rows[HELP_HISTORY_OWNER_ROW]
    assert help_history["surface"] == "editor-owner"
    assert help_history["effect_class"] == "retained-help-navigation-authority"
    assert help_history["capability_options"] == ["cap.history-clear"]
    assert help_history["owner_methods_present"]["HelpHistoryRegisterSnapshot"] is True
    assert help_history["owner_methods_present"]["snapshot_help_history_group_state"] is True

    recovery = rows[RECOVERY_OWNER_ROW]
    assert recovery["surface"] == "editor-owner"
    assert recovery["effect_class"] == "retained-cursor-selection-navigation-authority"
    assert recovery["capability_options"] == ["cap.cursor-restore", "cap.history-clear"]
    assert recovery["owner_methods_present"]["RecoveryRegisterSnapshot"] is True
    assert recovery["owner_methods_present"]["snapshot_recovery_group_state"] is True

    option_state = rows[OPTION_STATE_OWNER_ROW]
    assert option_state["surface"] == "editor-owner"
    assert option_state["effect_class"] == "configuration-capability-state-authority"
    assert option_state["capability_options"] == ["cap.option-read"]
    assert option_state["owner_methods_present"]["OptionStateSnapshot"] is True
    assert option_state["owner_methods_present"]["snapshot_option_state"] is True

    stdlib = rows[STDLIB_RESOURCE_NAME]
    assert stdlib["surface"] == "package-resource"
    assert stdlib["effect_class"] == "package-resource-read-eval"


def test_effect_contract_help_markdown_is_generated_from_contract_payload() -> None:
    payload = effect_resource_contract(rev=948)
    markdown = effect_contract_help_markdown(payload)

    assert markdown.startswith("# Effect/resource contract\n")
    assert "Revision: `rev0948`" in markdown
    assert "| `ed.open-url` | editor-hostcall | external-browser-process | cap.open-url |" in markdown
    assert "| `ed.fs-read` | editor-hostcall | filesystem-read | cap.fs-read |" in markdown
    assert "| `ed.mark-register` | editor-owner | retained-mark-navigation-authority | cap.mark-read, cap.mark-jump |" in markdown
    assert "| `ed.recovery-register` | editor-owner | retained-cursor-selection-navigation-authority | cap.cursor-restore, cap.history-clear |" in markdown
    assert "| `ed.option-state-register` | editor-owner | configuration-capability-state-authority | cap.option-read |" in markdown
    assert "python tools/mxeffects.py --write-help-doc --check-help-doc --check" in markdown




def test_mxeffects_cli_json_and_check() -> None:
    proc = subprocess.run(
        [sys.executable, str(ROOT / "tools" / "mxeffects.py"), "--json", "--check"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert proc.returncode == 0, proc.stderr or proc.stdout
    payload = json.loads(proc.stdout)

    assert payload["schema"] == EFFECT_CONTRACT_SCHEMA
    assert payload["checks"] == {"errors": [], "ok": True}
    assert payload["help_doc"]["path"] == EFFECT_CONTRACT_HELP_DOC
    rows = _rows_by_name(payload)
    assert rows["ed.require"]["capability_option"] == "cap.fs-require"
    assert rows["ed.clipboard-import"]["capability_option"] == "cap.clipboard-read"
    assert rows[MARK_OWNER_ROW]["audit_flags"]["mark_owner_snapshot_present"] is True
    assert rows[RECENT_FILES_OWNER_ROW]["audit_flags"]["recent_files_owner_snapshot_present"] is True
    assert rows[PALETTE_RECENT_OWNER_ROW]["audit_flags"]["palette_recent_owner_snapshot_present"] is True
    assert rows[ACTIVE_SEARCH_OWNER_ROW]["audit_flags"]["active_search_owner_snapshot_present"] is True
    assert rows[PROMPT_HISTORY_OWNER_ROW]["audit_flags"]["prompt_history_owner_snapshot_present"] is True
    assert rows[HELP_HISTORY_OWNER_ROW]["audit_flags"]["help_history_owner_snapshot_present"] is True
    assert rows[RECOVERY_OWNER_ROW]["audit_flags"]["recovery_owner_snapshot_present"] is True
    assert rows[OPTION_STATE_OWNER_ROW]["audit_flags"]["option_state_owner_snapshot_present"] is True
    assert rows["re.sub"]["budgets"]["replacement_max_bytes"] > 0


def test_mxeffects_human_output_names_substantive_boundaries() -> None:
    proc = subprocess.run(
        [sys.executable, str(ROOT / "tools" / "mxeffects.py"), "--check"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    )

    assert "Micromax effect/resource contract" in proc.stdout
    assert "ed.open-url: external-browser-process via cap.open-url" in proc.stdout
    assert "ed.fs-read: filesystem-read via cap.fs-read" in proc.stdout
    assert "ed.mark-register: retained-mark-navigation-authority via unsafe retained buffer+position authority" in proc.stdout
    assert "ed.shell: process via cap.shell" in proc.stdout
    assert "ed.recent-files-register: retained-path-history-authority via unsafe retained path authority" in proc.stdout
    assert "ed.palette-recent-register: retained-command-launch-authority via unsafe retained command/action authority" in proc.stdout
    assert "ed.active-search-register: delayed-navigation-authority via unsafe delayed authority" in proc.stdout
    assert "ed.prompt-history-register: durable-replay-history-authority via unsafe retained replay authority" in proc.stdout
    assert "ed.help-history-register: retained-help-navigation-authority via unsafe retained docs-navigation authority" in proc.stdout
    assert "ed.recovery-register: retained-cursor-selection-navigation-authority via unsafe retained cursor/selection recovery authority" in proc.stdout
    assert "ed.option-state-register: configuration-capability-state-authority via unsafe configuration/capability authority" in proc.stdout
    assert "re.search: regex-engine" in proc.stdout
    assert "micromax/stdlib/core.mx: package-resource-read-eval" in proc.stdout


def test_mxeffects_markdown_check_matches_installed_help_doc() -> None:
    proc = subprocess.run(
        [sys.executable, str(ROOT / "tools" / "mxeffects.py"), "--markdown", "--check-help-doc", "--check"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert proc.returncode == 0, proc.stderr or proc.stdout
    assert proc.stdout == (ROOT / EFFECT_CONTRACT_HELP_DOC).read_text(encoding="utf-8")
    assert "# Effect/resource contract" in proc.stdout
