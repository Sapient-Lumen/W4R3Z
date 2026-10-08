# Effect/resource contract

Generated from live Micromax registries, capability rows, owner methods, and default resource budgets.
This installed help page is intentionally generated so the runtime-facing contract does not drift behind revision notes.

- Schema: `micromax.effect-resource-contract.v1`
- Revision: `rev1000`
- Rows: `24`

| Name | Surface | Effect class | Capabilities | Budgets | Audit |
| --- | --- | --- | --- | --- | --- |
| `ed.open-url` | editor-hostcall | external-browser-process | cap.open-url | output_max_bytes=16384; result_max_bytes=1048576; result_max_cells=8192; timeout_seconds=6 | open_url_process_timeout_boundary=ok |
| `ed.fs-read` | editor-hostcall | filesystem-read | cap.fs-read | input_max_bytes=1000000; result_max_bytes=1048576; result_max_cells=8192; timeout_seconds=5 | fs_read_preflight_byte_budget=ok; fs_read_timeout_worker=ok |
| `ed.fs-list` | editor-hostcall | filesystem-list | cap.fs-list | result_max_bytes=1048576; result_max_cells=8192; row_max=500; timeout_seconds=5 | fs_list_timeout_worker=ok |
| `ed.fs-stat` | editor-hostcall | filesystem-stat | cap.fs-stat | result_max_bytes=1048576; result_max_cells=8192; timeout_seconds=5 | fs_stat_timeout_worker=ok |
| `ed.open` | editor-hostcall | filesystem-open-buffer | cap.fs-open | read_timeout_seconds=5; result_max_bytes=1048576; result_max_cells=8192; stat_timeout_seconds=5 | editor_open_read_timeout_boundary=ok |
| `ed.save` | editor-hostcall | filesystem-save | cap.fs-save | freshness_timeout_seconds=5; mkparents_timeout_seconds=5; result_max_bytes=1048576; result_max_cells=8192; write_timeout_seconds=5 | editor_atomic_write_timeout_boundary=ok; editor_save_freshness_timeout_boundary=ok |
| `ed.shell` | editor-hostcall | process | cap.shell | command_max_bytes=4096; output_max_bytes=262144; result_max_bytes=1048576; result_max_cells=8192; timeout_seconds=5 | shell_output_timeout_budget=ok |
| `ed.require` | editor-hostcall | source-load-eval | cap.fs-require | eval_step_budget=50000; load_graph_max_total_bytes=1048576; load_max_depth=32; read_timeout_seconds=5; result_max_bytes=1048576; result_max_cells=8192; source_max_bytes=262144 | source_load_eval_budget=ok; source_load_graph_budget=ok |
| `ed.clipboard-import` | editor-hostcall | clipboard-import-process | cap.clipboard-read | output_max_bytes=262144; result_max_bytes=1048576; result_max_cells=8192; timeout_seconds=5 | external_clipboard_process_budget=ok |
| `ed.mark-register` | editor-owner | retained-mark-navigation-authority | cap.mark-read, cap.mark-jump | authority_capability_count=2; cleanup_scope_count=2 | mark_owner_snapshot_present=ok |
| `ed.recent-files-register` | editor-owner | retained-path-history-authority | cap.recent-read, cap.history-clear, cap.persist | authority_capability_count=3; cleanup_scope_count=3; persist_option=recent.persist; recent_limit_option=recent.limit | recent_files_owner_snapshot_present=ok |
| `ed.palette-recent-register` | editor-owner | retained-command-launch-authority | cap.command-read, cap.action-read, cap.history-clear | authority_capability_count=3; cleanup_scope_count=3; palette_recent_limit=12 | palette_recent_owner_snapshot_present=ok |
| `ed.active-search-register` | editor-owner | delayed-navigation-authority | cap.search-read, cap.search-replay | authority_capability_count=2; cleanup_scope_count=3 | active_search_owner_snapshot_present=ok |
| `ed.prompt-history-register` | editor-owner | durable-replay-history-authority | cap.history-clear, cap.persist | authority_capability_count=2; cleanup_scope_count=3; history_limit_option=history.limit; persist_option=history.persist | prompt_history_owner_snapshot_present=ok |
| `ed.saved-cursor-register` | editor-owner | retained-cursor-navigation-authority | cap.cursor-restore, cap.persist | authority_capability_count=2; cleanup_scope_count=3; enable_option=savecursor; persist_file_option=savecursor.file; persist_option=cap.persist | saved_cursor_owner_snapshot_present=ok |
| `ed.help-history-register` | editor-owner | retained-help-navigation-authority | cap.history-clear | authority_capability_count=1; cleanup_scope_count=3; help_stack_limit=40; lanes=back,forward,session | help_history_owner_snapshot_present=ok |
| `ed.recovery-register` | editor-owner | retained-cursor-selection-navigation-authority | cap.cursor-restore, cap.history-clear | authority_capability_count=2; cleanup_scope_count=3; lanes=selection,jump | recovery_owner_snapshot_present=ok |
| `ed.option-state-register` | editor-owner | configuration-capability-state-authority | cap.option-read | authority_capability_count=1; lanes=global-options,buffer-local-options; rollback_scope_count=2 | option_state_owner_snapshot_present=ok |
| `re.search` | vm-hostcall | regex-engine | allowlisted-hostcall | haystack_max_bytes=262144; linux_worker_memory_headroom_bytes=150994944; pattern_max_bytes=10000; result_max_bytes=1048576; result_max_cells=8192; timeout_seconds=0.25 | regex_hostcall_input_budget=ok; regex_hostcall_timeout_worker=ok |
| `re.findall` | vm-hostcall | regex-engine | allowlisted-hostcall | haystack_max_bytes=262144; linux_worker_memory_headroom_bytes=150994944; pattern_max_bytes=10000; result_max_bytes=1048576; result_max_cells=8192; timeout_seconds=0.25 | regex_hostcall_input_budget=ok; regex_hostcall_timeout_worker=ok |
| `re.sub` | vm-hostcall | regex-engine | allowlisted-hostcall | haystack_max_bytes=262144; linux_worker_memory_headroom_bytes=150994944; pattern_max_bytes=10000; replacement_max_bytes=262144; result_max_bytes=1048576; result_max_cells=8192; timeout_seconds=0.25 | regex_hostcall_input_budget=ok; regex_hostcall_timeout_worker=ok |
| `re.subn` | vm-hostcall | regex-engine | allowlisted-hostcall | haystack_max_bytes=262144; linux_worker_memory_headroom_bytes=150994944; pattern_max_bytes=10000; replacement_max_bytes=262144; result_max_bytes=1048576; result_max_cells=8192; timeout_seconds=0.25 | regex_hostcall_input_budget=ok; regex_hostcall_timeout_worker=ok |
| `re.escape` | vm-hostcall | regex-escape | allowlisted-hostcall | input_max_bytes=262144; result_max_bytes=1048576; result_max_cells=8192 | regex_hostcall_input_budget=ok |
| `micromax/stdlib/core.mx` | package-resource | package-resource-read-eval | bundled-trusted-resource | resource_max_bytes=65536 | stdlib_resource_contract_present=ok |

## How to regenerate

Run `python tools/mxeffects.py --write-help-doc --check-help-doc --check` from the repository root.
Edit `src/micromax_editor/effect_contracts.py` or the live registries/owner methods, not this table by hand.
