import pathlib
import tempfile

from release_hygiene_lib import iter_release_paths, should_skip_release_path


with tempfile.TemporaryDirectory(prefix="DelayBasin-rev9999-root-shaped-") as tmp:
    root = pathlib.Path(tmp)
    (root / "README.md").write_text("kept\n", encoding="utf-8")
    (root / "docs").mkdir()
    (root / "docs" / "note.md").write_text("kept\n", encoding="utf-8")
    frozen = root / "DelayBasin-rev0001-old-bundle-overlay"
    frozen.mkdir()
    (frozen / "stale.md").write_text("skip\n", encoding="utf-8")
    cache = root / "__pycache__"
    cache.mkdir()
    (cache / "x.pyc").write_bytes(b"skip")
    bundle_name = "DelayBasin-rev9999-2099.01.01.00.00-test.zip"
    (root / bundle_name).write_text("skip zip\n", encoding="utf-8")

    kept = [path.relative_to(root).as_posix() for path in iter_release_paths(root, bundle_name)]
    expected = ["README.md", "docs/note.md"]
    if kept != expected:
        raise SystemExit(f"release hygiene relative-root regression failed: {kept!r} != {expected!r}")
    if should_skip_release_path(root / "README.md", bundle_name, root):
        raise SystemExit("root-relative file was skipped because an absolute parent looked frozen")

print("check_release_hygiene_relative_root: OK")
