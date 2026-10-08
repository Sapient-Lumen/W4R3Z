# FILE-ATTRIBUTE-BUDGET-01 maintainer artifact

Current-behavior witness for U-199.

Run against a source lane with:

```bash
PYTHONPATH=/path/to/source-tree pytest -q test_file_attribute_budget_reproducer.py
```

The test constructs compact compressed peer messages for:

```text
SharedFileListResponse
FileSearchResponse
FolderContentsResponse
```

Each message contains one file whose valid bitrate attribute appears after eleven filler attribute pairs. Current behavior retains the final bitrate in all archived lanes.
