#!/usr/bin/env python3
"""Release-gate smoke test for scripts/extract_release_zip.py.

The archive verifier proves a ZIP is canonical, and the manifest verifier proves
an extracted tree is closed. This check exercises the operator-facing bridge
between them: a verifier-backed extractor that refuses to write from a bad ZIP,
preserves the raw ZIP input path boundary, extracts only the verifier's byte
snapshot, publishes only after post-extraction manifest verification, rechecks
the temporary extraction root and output-parent identities at publication, and does not clobber an
existing non-empty directory unless --clean semantics are requested.
"""

from __future__ import annotations

import hashlib
import os
import shutil
import sys
import tempfile
import zipfile
from pathlib import Path

sys.dont_write_bytecode = True

import build_manifest
import build_release_zip
import extract_release_zip
import verify_manifest
import verify_release_zip
from _cli_harness import run_python_cli

ROOT = Path(__file__).resolve().parents[1]
FIXED_ZIP_DT = verify_release_zip.FIXED_ZIP_DT
EXTRACT_TOOL = ROOT / "scripts" / "extract_release_zip.py"


def fail(msg: str) -> None:
    print("ERROR:", msg, file=sys.stderr)
    raise SystemExit(2)


def zipinfo(name: str) -> zipfile.ZipInfo:
    zi = zipfile.ZipInfo(name)
    zi.compress_type = zipfile.ZIP_STORED
    zi.date_time = FIXED_ZIP_DT
    zi.external_attr = (verify_release_zip.CANONICAL_MODE & 0xFFFF) << 16
    return zi


def write_entry(zf: zipfile.ZipFile, name: str, data: bytes) -> None:
    zf.writestr(zipinfo(name), data)


def build_zip_with_fresh_manifest(out_zip: Path) -> None:
    manifest = ROOT / "MANIFEST.sha256"
    old = manifest.read_bytes() if manifest.exists() else None
    try:
        manifest.write_text(build_manifest.build_manifest_text(), encoding="utf-8")
        build_release_zip.build_zip(ROOT, out_zip)
    finally:
        if old is None:
            try:
                manifest.unlink()
            except FileNotFoundError:
                pass
        else:
            manifest.write_bytes(old)


def make_bad_hash_zip(path: Path) -> None:
    version = b"v999\n"
    manifest = ("0" * 64 + "  VERSION\n").encode("utf-8")
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_STORED, strict_timestamps=False) as zf:
        write_entry(zf, "MANIFEST.sha256", manifest)
        write_entry(zf, "VERSION", version)


def expect_bad(result: extract_release_zip.ExtractResult, needle: str) -> None:
    if result.ok:
        fail("negative safe-extractor probe unexpectedly passed")
    joined = "\n".join(result.problems)
    if needle not in joined:
        fail(f"negative safe-extractor probe did not report {needle!r}; problems={result.problems!r}")


def check_extractor_uses_verified_zip_snapshot(good_zip: Path, out: Path) -> None:
    """Ensure extraction reads the verifier snapshot, not the path a second time."""

    expected_hash = hashlib.sha256(good_zip.read_bytes()).hexdigest()
    original_verify = extract_release_zip.verify_release_zip.verify_zip

    def mutating_verify(path):  # type: ignore[no-untyped-def]
        result = original_verify(path)
        if result.ok:
            Path(path).write_bytes(b"not the verified release ZIP after verifier returned\n")
        return result

    extract_release_zip.verify_release_zip.verify_zip = mutating_verify
    try:
        result = extract_release_zip.extract_release_zip(good_zip, out)
    finally:
        extract_release_zip.verify_release_zip.verify_zip = original_verify

    if not result.ok:
        fail("safe extractor did not extract from the verifier snapshot after path mutation: " + "; ".join(result.problems[:10]))
    if result.zip_sha256 != expected_hash:
        fail(f"safe extractor reported hash {result.zip_sha256}, expected verifier snapshot hash {expected_hash}")
    tree = verify_manifest.verify_tree(out)
    if not tree.ok:
        fail("snapshot-extracted tree did not verify: " + "; ".join(tree.problems[:10]))




def check_extractor_member_write_no_symlink_redirect(good_zip: Path, out: Path) -> None:
    """Ensure member writes do not follow a just-swapped extraction directory."""

    if not hasattr(os, "symlink") or os.open not in getattr(os, "supports_dir_fd", set()):
        return

    attacker = out.parent / "attacker-member-target"
    attacker.mkdir()
    state: dict[str, object] = {}
    original_mkdtemp = extract_release_zip.tempfile.mkdtemp
    original_mkdir = extract_release_zip.os.mkdir

    def recording_mkdtemp(*args, **kwargs):  # type: ignore[no-untyped-def]
        name = original_mkdtemp(*args, **kwargs)
        state["tmp_root"] = Path(name)
        return name

    def swapping_mkdir(path, mode=0o777, *, dir_fd=None):  # type: ignore[no-untyped-def]
        result = original_mkdir(path, mode, dir_fd=dir_fd)
        if path == "docs" and dir_fd is not None and "tmp_root" in state and not state.get("swapped"):
            docs_dir = Path(state["tmp_root"]) / "docs"
            try:
                docs_dir.rmdir()
                os.symlink(attacker, docs_dir)
                state["swapped"] = True
            except OSError as exc:
                fail(f"could not stage extraction member symlink-swap probe: {exc}")
        return result

    extract_release_zip.tempfile.mkdtemp = recording_mkdtemp
    extract_release_zip.os.mkdir = swapping_mkdir
    try:
        result = extract_release_zip.extract_release_zip(good_zip, out, clean=True)
    finally:
        extract_release_zip.os.mkdir = original_mkdir
        extract_release_zip.tempfile.mkdtemp = original_mkdtemp

    expect_bad(result, "without following symlinks")
    redirected = [p.relative_to(attacker).as_posix() for p in attacker.rglob("*")]
    if redirected:
        fail("safe extractor followed a swapped member directory symlink and wrote outside the temp root: " + ", ".join(redirected[:10]))
    if out.exists():
        fail("safe extractor published output after member directory symlink-swap probe")


def check_extractor_rejects_temp_root_swap_before_publish(good_zip: Path, out: Path) -> None:
    """Ensure a verified temp tree cannot be swapped before publication."""

    if not hasattr(os, "symlink"):
        return

    attacker = out.parent / "attacker-publish-target"
    attacker.mkdir()
    state: dict[str, object] = {}
    original_mkdtemp = extract_release_zip.tempfile.mkdtemp
    original_verify_tree = extract_release_zip.verify_manifest.verify_tree

    def recording_mkdtemp(*args, **kwargs):  # type: ignore[no-untyped-def]
        name = original_mkdtemp(*args, **kwargs)
        state["tmp_root"] = Path(name)
        return name

    def swapping_verify_tree(root):  # type: ignore[no-untyped-def]
        result = original_verify_tree(root)
        tmp_root = state.get("tmp_root")
        if result.ok and tmp_root is not None and Path(root) == tmp_root and not state.get("swapped"):
            saved = tmp_root.with_name(tmp_root.name + ".verified-before-swap")
            try:
                tmp_root.rename(saved)
                os.symlink(attacker, tmp_root)
                state["swapped"] = True
            except OSError as exc:
                fail(f"could not stage temporary-root publish-swap probe: {exc}")
        return result

    extract_release_zip.tempfile.mkdtemp = recording_mkdtemp
    extract_release_zip.verify_manifest.verify_tree = swapping_verify_tree
    try:
        result = extract_release_zip.extract_release_zip(good_zip, out, clean=True)
    finally:
        extract_release_zip.verify_manifest.verify_tree = original_verify_tree
        extract_release_zip.tempfile.mkdtemp = original_mkdtemp

    expect_bad(result, "temporary extraction root")
    if os.path.lexists(out):
        fail("safe extractor published an output path after the verified temp root was swapped")
    redirected = [p.relative_to(attacker).as_posix() for p in attacker.rglob("*")]
    if redirected:
        fail("temporary-root swap probe wrote release bytes into the attacker target: " + ", ".join(redirected[:10]))



def check_extractor_rejects_output_parent_swap_before_publish(good_zip: Path, out: Path) -> None:
    """Ensure a verified tree cannot be published through a swapped parent route."""

    state: dict[str, object] = {}
    original_remove = extract_release_zip._remove_empty_or_clean_output

    def swapping_remove(*args, **kwargs):  # type: ignore[no-untyped-def]
        if not state.get("swapped"):
            parent = out.parent
            saved = parent.with_name(parent.name + ".verified-parent-before-swap")
            try:
                parent.rename(saved)
                parent.mkdir()
                state["swapped"] = True
            except OSError as exc:
                fail(f"could not stage output-parent publish-swap probe: {exc}")
        return original_remove(*args, **kwargs)

    extract_release_zip._remove_empty_or_clean_output = swapping_remove
    try:
        result = extract_release_zip.extract_release_zip(good_zip, out, clean=True)
    finally:
        extract_release_zip._remove_empty_or_clean_output = original_remove

    expect_bad(result, "output parent directory")
    if out.exists():
        fail("safe extractor published an output path after the output parent route was swapped")
    swapped_parent = out.parent.with_name(out.parent.name + ".verified-parent-before-swap")
    if (swapped_parent / out.name).exists():
        fail("safe extractor published into the original parent after the output parent route was swapped")



def symlink_or_skip(target: Path | str, link: Path) -> bool:
    if not hasattr(os, "symlink"):
        return False
    try:
        os.symlink(target, link)
    except (OSError, NotImplementedError):
        return False
    return True


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="tes_safe_extract_") as td:
        tdir = Path(td)
        version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
        rev = int(version[1:])
        good_zip = tdir / f"The-Election-Stack-rev{rev:04d}.zip"
        build_zip_with_fresh_manifest(good_zip)

        out = tdir / "out"
        result = extract_release_zip.extract_release_zip(good_zip, out)
        if not result.ok:
            fail("safe extractor rejected a freshly built release ZIP: " + "; ".join(result.problems[:10]))
        tree = verify_manifest.verify_tree(out)
        if not tree.ok:
            fail("safe-extracted tree did not verify: " + "; ".join(tree.problems[:10]))
        root_mode = out.stat().st_mode & 0o777
        if root_mode != verify_manifest.CANONICAL_ROOT_DIR_MODE:
            fail(f"safe extractor left non-canonical root directory mode: {oct(root_mode)}")
        for d in out.rglob("*"):
            if d.is_dir():
                mode = d.stat().st_mode & 0o777
                if mode != verify_manifest.CANONICAL_DIR_MODE:
                    fail(f"safe extractor left non-canonical directory mode: {d.relative_to(out)} {oct(mode)}")
        if result.version != version:
            fail(f"safe extractor result version mismatch (got={result.version!r}, want={version!r})")

        member_swap_out = tdir / "member-swap-out"
        check_extractor_member_write_no_symlink_redirect(good_zip, member_swap_out)

        publish_swap_out = tdir / "publish-swap-out"
        check_extractor_rejects_temp_root_swap_before_publish(good_zip, publish_swap_out)

        parent_swap_out = tdir / "parent-swap" / "out"
        check_extractor_rejects_output_parent_swap_before_publish(good_zip, parent_swap_out)

        snapshot_zip = tdir / f"snapshot-{good_zip.name}"
        snapshot_zip.write_bytes(good_zip.read_bytes())
        snapshot_out = tdir / "snapshot-out"
        check_extractor_uses_verified_zip_snapshot(snapshot_zip, snapshot_out)

        lexical_zip_out = tdir / "lexical-zip-out"
        result = extract_release_zip.extract_release_zip(str(good_zip.parent) + "/./" + good_zip.name, lexical_zip_out)
        expect_bad(result, "current/parent")
        if lexical_zip_out.exists():
            fail("safe extractor created output for a lexically ambiguous ZIP input path")

        repeated_sep_zip_out = tdir / "repeated-separator-zip-out"
        result = extract_release_zip.extract_release_zip(str(good_zip.parent) + "//" + good_zip.name, repeated_sep_zip_out)
        expect_bad(result, "empty separator")
        if repeated_sep_zip_out.exists():
            fail("safe extractor created output for a repeated-separator ZIP input path")

        cli_lexical_zip_out = tdir / "cli-lexical-zip-out"
        code, cli_out, cli_err = run_python_cli(
            EXTRACT_TOOL,
            [str(good_zip.parent) + "/./" + good_zip.name, cli_lexical_zip_out, "--quiet"],
            cwd=ROOT,
        )
        if code == 0:
            fail("safe extractor CLI accepted a lexically ambiguous ZIP input path")
        if "current/parent" not in (cli_out + cli_err):
            fail("safe extractor CLI did not preserve raw ZIP path spelling in diagnostics")
        if cli_lexical_zip_out.exists():
            fail("safe extractor CLI created output for a lexically ambiguous ZIP input path")

        nonempty = tdir / "nonempty"
        nonempty.mkdir()
        (nonempty / "local.txt").write_text("operator-local file\n", encoding="utf-8")
        result = extract_release_zip.extract_release_zip(good_zip, nonempty)
        expect_bad(result, "not empty")
        if not (nonempty / "local.txt").exists():
            fail("safe extractor modified a non-empty output directory without --clean")

        result = extract_release_zip.extract_release_zip(good_zip, nonempty, clean=True)
        if not result.ok:
            fail("safe extractor --clean failed on non-empty output: " + "; ".join(result.problems[:10]))
        if (nonempty / "local.txt").exists():
            fail("safe extractor --clean left stale local file behind")
        if not (nonempty / "MANIFEST.sha256").exists():
            fail("safe extractor --clean did not populate release manifest")

        bad_zip = tdir / "bad-hash.zip"
        make_bad_hash_zip(bad_zip)
        bad_out = tdir / "bad-out"
        result = extract_release_zip.extract_release_zip(bad_zip, bad_out)
        expect_bad(result, "release ZIP verification failed before extraction")
        if bad_out.exists():
            fail("safe extractor created output directory for a bad ZIP")

        if hasattr(os, "symlink"):
            symlink_zip = tdir / f"The-Election-Stack-rev{rev - 1:04d}.zip"
            if symlink_or_skip(good_zip.name, symlink_zip):
                symlink_zip_out = tdir / "symlink-zip-out"
                result = extract_release_zip.extract_release_zip(symlink_zip, symlink_zip_out, clean=True)
                expect_bad(result, "must not be a symlink")
                if symlink_zip_out.exists():
                    fail("safe extractor created output for a symlinked ZIP input path")

            target = tdir / "target"
            target.mkdir()
            symlink_out = tdir / "symlink-out"
            if symlink_or_skip(target, symlink_out):
                result = extract_release_zip.extract_release_zip(good_zip, symlink_out, clean=True)
                expect_bad(result, "symlink")
                if not symlink_out.is_symlink():
                    fail("safe extractor removed or replaced an output symlink")

            real_parent = tdir / "real-parent"
            real_parent.mkdir()
            symlink_parent = tdir / "symlink-parent"
            if symlink_or_skip(real_parent, symlink_parent):
                redirected_out = symlink_parent / "out"
                result = extract_release_zip.extract_release_zip(good_zip, redirected_out, clean=True)
                expect_bad(result, "symlink component")
                if (real_parent / "out").exists():
                    fail("safe extractor published through a symlinked parent component")

                # The extractor must reject symlinked ancestry before creating
                # any resolved output parent.  Otherwise an invalid output path
                # such as symlink-parent/new-child/out can still leave
                # new-child behind inside the symlink target.
                side_effect_out = symlink_parent / "new-child" / "out"
                result = extract_release_zip.extract_release_zip(good_zip, side_effect_out, clean=True)
                expect_bad(result, "symlink component")
                if (real_parent / "new-child").exists():
                    fail("safe extractor created a resolved parent directory before rejecting symlinked output ancestry")

        traversal_out = os.fspath(tdir / "traversal") + "/../lexical-out"
        result = extract_release_zip.extract_release_zip(good_zip, traversal_out, clean=True)
        expect_bad(result, "traversal")
        if (tdir / "lexical-out").exists():
            fail("safe extractor accepted an output path containing lexical parent traversal")

        dot_component_out = os.fspath(tdir / "dot-component") + "/./out"
        result = extract_release_zip.extract_release_zip(good_zip, dot_component_out, clean=True)
        expect_bad(result, "current/parent")
        if (tdir / "dot-component").exists():
            fail("safe extractor normalized away a lexical current-directory component before rejecting it")

        empty_component_out = os.fspath(tdir / "empty-component") + "//out"
        result = extract_release_zip.extract_release_zip(good_zip, empty_component_out, clean=True)
        expect_bad(result, "empty separator")
        if (tdir / "empty-component").exists():
            fail("safe extractor normalized away an empty separator component before rejecting it")

        result = extract_release_zip.extract_release_zip(good_zip, os.sep, clean=True)
        expect_bad(result, "filesystem root")

    print("PASS: safe release extractor verifies before extraction, rechecks manifest closure, protects non-empty outputs, rejects bad/ambiguous/symlinked ZIP inputs through both API and CLI paths, extracts from the verified ZIP snapshot, rejects symlinked output ancestry, rejects non-canonical lexical output paths, normalizes release root and directory modes, avoids redirected-parent side effects, refuses swapped extraction member directories without redirected writes, and rejects verified temporary-root and output-parent route swaps before publication")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
