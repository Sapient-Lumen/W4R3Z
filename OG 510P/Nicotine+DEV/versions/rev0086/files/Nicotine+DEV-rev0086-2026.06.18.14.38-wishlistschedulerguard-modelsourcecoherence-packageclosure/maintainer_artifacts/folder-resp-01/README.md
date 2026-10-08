# FOLDER-RESP-01 maintainer artifact

This directory contains a current-behavior pytest reproducer for the folder-response token and parser-ordering family.

Run from this cube with an external Nicotine+ source checkout:

```bash
NICOTINE_SOURCE=/path/to/nicotine-plus python -m pytest -q   maintainer_artifacts/folder-resp-01/test_folder_contents_response_binding_and_parse_order_reproducer.py
```

rev0014 ran it against the archived external source lanes from the rev0003 source bundle:

```text
github-tag-3.3.10: 5 passed
github-branch-3.3.x: 5 passed
github-branch-master: 5 passed
```

The tests assert current behavior, not fixed behavior.
