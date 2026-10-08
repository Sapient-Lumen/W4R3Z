#!/usr/bin/env python3
"""Release-gate smoke check for manifest/ZIP builder byte and file-type policy.

The verifier side rejects CRLF control files, symlinks, and non-regular release
paths.  The builder side must fail closed too: `build_manifest.py --check` must
compare raw bytes without text-mode newline normalization, and manifest/ZIP file
selection must refuse release-scope symlinks or special files before hashing or
packaging them.
"""

from __future__ import annotations

import os
import sys
import tempfile
from contextlib import contextmanager
from pathlib import Path

sys.dont_write_bytecode = True

import build_manifest
import build_release_zip
import release_control_files

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / release_control_files.MANIFEST_NAME
README = ROOT / "README.md"


@contextmanager
def tiny_release_root(prefix: str = "tes_builder_tiny_"):
    """Yield a small release-shaped root for filesystem-policy probes.

    Most negative controls only need builder semantics, not a 2k-file cube.
    Running those probes against a tiny root keeps the gate deterministic and
    prevents release-builder hardening tests from spending the session hashing
    or zipping unrelated archive content.
    """

    with tempfile.TemporaryDirectory(prefix=prefix) as td:
        troot = Path(td)
        (troot / "README.md").write_text("tiny release root for builder negative controls\n", encoding="utf-8")
        (troot / "VERSION").write_text("v0000\n", encoding="utf-8")
        yield troot


def with_manifest_root(temp_root: Path, fn) -> None:
    """Run a manifest-builder probe with build_manifest.ROOT rebound."""

    old_root = build_manifest.ROOT
    try:
        build_manifest.ROOT = temp_root  # type: ignore[assignment]
        fn()
    finally:
        build_manifest.ROOT = old_root  # type: ignore[assignment]


def fail(msg: str) -> None:
    print("ERROR:", msg, file=sys.stderr)
    raise SystemExit(2)


def expect_system_exit_contains(fn, needle: str) -> None:
    try:
        fn()
    except SystemExit as exc:
        text = str(exc)
        if needle not in text:
            fail(f"expected SystemExit containing {needle!r}, got {text!r}")
        return
    fail(f"expected SystemExit containing {needle!r}, but call succeeded")



def probe_crlf_manifest_check() -> None:
    with tiny_release_root() as troot:
        manifest = troot / release_control_files.MANIFEST_NAME

        def run_probe() -> None:
            expected = build_manifest.build_manifest_bytes()
            if b"\r" in expected:
                fail("freshly generated manifest unexpectedly contains CR bytes")
            manifest.write_bytes(expected.replace(b"\n", b"\r\n"))
            ok, _want, _cur, problems = build_manifest.check_manifest_bytes()
            if ok:
                fail("build_manifest byte check accepted a CRLF-normalized MANIFEST.sha256")
            joined = "\n".join(problems)
            if "CR bytes" not in joined and "not canonical" not in joined:
                fail(f"CRLF manifest byte check failed for the wrong reason: {problems!r}")

        with_manifest_root(troot, run_probe)


def _restore_manifest_bytes(old: bytes, manifest: Path = MANIFEST) -> None:
    """Restore MANIFEST.sha256 after destructive control-file probes."""

    try:
        if manifest.is_symlink() or manifest.exists():
            if manifest.is_dir() and not manifest.is_symlink():
                manifest.rmdir()
            else:
                manifest.unlink()
    except FileNotFoundError:
        pass
    manifest.write_bytes(old)


def probe_manifest_control_file_route_rejection() -> None:
    """MANIFEST.sha256 itself must not be read or overwritten through aliases."""

    with tiny_release_root() as troot:
        manifest = troot / release_control_files.MANIFEST_NAME
        dist = troot / "dist"

        def run_probe() -> None:
            old = build_manifest.build_manifest_bytes()
            manifest.write_bytes(old)
            dist.mkdir(exist_ok=True)
            target = dist / "manifest-control-target.sha256"
            target.write_bytes(old)
            try:
                if hasattr(os, "symlink"):
                    manifest.unlink()
                    if symlink_or_skip(target, manifest):
                        ok, _want, _cur, problems = build_manifest.check_manifest_bytes()
                        if ok:
                            fail("build_manifest --check accepted a symlinked MANIFEST.sha256 control file")
                        if "must not be a symlink" not in "\n".join(problems):
                            fail(f"symlinked manifest control file failed for wrong reason: {problems!r}")
                        expect_system_exit_contains(
                            lambda: build_manifest.write_manifest_control_bytes(old),
                            "must not be a symlink",
                        )
                    _restore_manifest_bytes(old, manifest)

                manifest.unlink()
                manifest.mkdir()
                ok, _want, _cur, problems = build_manifest.check_manifest_bytes()
                if ok:
                    fail("build_manifest --check accepted a directory at MANIFEST.sha256")
                if "regular file" not in "\n".join(problems):
                    fail(f"non-regular manifest control file failed for wrong reason: {problems!r}")
                expect_system_exit_contains(
                    lambda: build_manifest.write_manifest_control_bytes(old),
                    "regular file",
                )
            finally:
                _restore_manifest_bytes(old, manifest)
                try:
                    target.unlink()
                except FileNotFoundError:
                    pass
                try:
                    dist.rmdir()
                except OSError:
                    pass

        with_manifest_root(troot, run_probe)


def probe_manifest_control_publish_recheck() -> None:
    """A MANIFEST.sha256 symlink swap before publish must fail closed."""

    if not hasattr(os, "symlink"):
        return
    with tiny_release_root() as troot:
        manifest = troot / release_control_files.MANIFEST_NAME
        dist = troot / "dist"

        def run_probe() -> None:
            old = build_manifest.build_manifest_bytes()
            manifest.write_bytes(old)
            dist.mkdir(exist_ok=True)
            target = dist / "manifest-control-publish-target.sha256"
            target.write_bytes(b"must not receive regenerated manifest bytes\n")
            original_target_problems = build_manifest._manifest_control_target_problems
            call_count = 0

            def mutating_target_problems(path, *, allow_missing):
                nonlocal call_count
                problems = original_target_problems(path, allow_missing=allow_missing)
                if allow_missing and not problems:
                    call_count += 1
                    if call_count == 1:
                        manifest.unlink()
                        os.symlink(target, manifest)
                return problems

            try:
                build_manifest._manifest_control_target_problems = mutating_target_problems  # type: ignore[attr-defined]
                expect_system_exit_contains(
                    lambda: build_manifest.write_manifest_control_bytes(old),
                    "must not be a symlink",
                )
                if target.read_bytes() != b"must not receive regenerated manifest bytes\n":
                    fail("build_manifest followed a MANIFEST.sha256 symlink and overwrote the target")
            finally:
                build_manifest._manifest_control_target_problems = original_target_problems  # type: ignore[attr-defined]
                _restore_manifest_bytes(old, manifest)
                try:
                    target.unlink()
                except FileNotFoundError:
                    pass
                try:
                    dist.rmdir()
                except OSError:
                    pass

        with_manifest_root(troot, run_probe)

def probe_symlink_file_rejection() -> None:
    if not hasattr(os, "symlink"):
        return
    with tiny_release_root() as troot:
        probe = troot / "tmp_release_symlink_probe.md"
        def run_manifest_probe() -> None:
            expect_system_exit_contains(build_manifest.build_manifest_entries, "symlink")
        try:
            try:
                os.symlink("README.md", probe)
            except (OSError, NotImplementedError):
                return
            with_manifest_root(troot, run_manifest_probe)
            expect_system_exit_contains(lambda: build_release_zip.release_file_names(troot), "symlink")
        finally:
            try:
                probe.unlink()
            except FileNotFoundError:
                pass


def probe_special_file_rejection() -> None:
    if not hasattr(os, "mkfifo"):
        return
    with tiny_release_root() as troot:
        probe = troot / "tmp_release_fifo_probe"
        def run_manifest_probe() -> None:
            expect_system_exit_contains(build_manifest.build_manifest_entries, "not a regular file")
        try:
            try:
                os.mkfifo(probe)
            except (OSError, NotImplementedError):
                return
            with_manifest_root(troot, run_manifest_probe)
            expect_system_exit_contains(lambda: build_release_zip.release_file_names(troot), "not a regular file")
        finally:
            try:
                probe.unlink()
            except FileNotFoundError:
                pass


def probe_unsafe_governed_path_rejection() -> None:
    with tiny_release_root() as troot:
        probe = troot / "tmp release unsafe.md"
        def run_manifest_probe() -> None:
            expect_system_exit_contains(build_manifest.build_manifest_entries, "unsafe release-scope path")
        try:
            probe.write_text("unsafe release path should fail closed\n", encoding="utf-8")
            with_manifest_root(troot, run_manifest_probe)
            expect_system_exit_contains(lambda: build_release_zip.release_file_names(troot), "unsafe release-scope path")
        finally:
            try:
                probe.unlink()
            except FileNotFoundError:
                pass

def symlink_or_skip(target: Path | str, link: Path) -> bool:
    if not hasattr(os, "symlink"):
        return False
    try:
        os.symlink(target, link)
    except (OSError, NotImplementedError):
        return False
    return True




def probe_manifest_source_root_path_firewall() -> None:
    """Manifest generation must reject ambiguous or symlink-routed source roots."""

    original_root = build_manifest.ROOT
    try:
        build_manifest.ROOT = os.fspath(ROOT.parent) + f"/./{ROOT.name}"  # type: ignore[assignment]
        expect_system_exit_contains(build_manifest.build_manifest_entries, "current/parent")

        build_manifest.ROOT = os.fspath(ROOT.parent) + f"//{ROOT.name}"  # type: ignore[assignment]
        expect_system_exit_contains(build_manifest.build_manifest_entries, "empty separator")

        build_manifest.ROOT = os.fspath(ROOT) + os.sep  # type: ignore[assignment]
        expect_system_exit_contains(build_manifest.build_manifest_entries, "trailing separator")

        with tempfile.TemporaryDirectory(prefix="tes_manifest_root_") as td:
            tdir = Path(td)
            plain_file_root = tdir / "not-a-directory"
            plain_file_root.write_text("not a release root\n", encoding="utf-8")
            build_manifest.ROOT = plain_file_root  # type: ignore[assignment]
            expect_system_exit_contains(build_manifest.build_manifest_entries, "must be a directory")

            if hasattr(os, "symlink"):
                final_link = tdir / "repo-link"
                if symlink_or_skip(ROOT, final_link):
                    build_manifest.ROOT = final_link  # type: ignore[assignment]
                    expect_system_exit_contains(build_manifest.build_manifest_entries, "must not be a symlink")

                parent_link = tdir / "parent-link"
                if symlink_or_skip(ROOT.parent, parent_link):
                    build_manifest.ROOT = parent_link / ROOT.name  # type: ignore[assignment]
                    expect_system_exit_contains(build_manifest.build_manifest_entries, "symlink component")
    finally:
        build_manifest.ROOT = original_root  # type: ignore[assignment]



def probe_manifest_member_read_recheck() -> None:
    """A manifest source member swapped to a symlink after discovery must fail."""

    if not hasattr(os, "symlink"):
        return
    with tiny_release_root() as troot:
        probe = troot / "tmp_release_manifest_read_probe.md"
        redirect = troot / "tmp_release_manifest_read_target.md"
        original_open_member = build_manifest._open_manifest_member_fd
        swapped = False
        try:
            probe.write_text("original governed manifest bytes\n", encoding="utf-8")
            redirect.write_text("redirected bytes that must not be manifested\n", encoding="utf-8")

            def mutating_open_member(root, rel):
                nonlocal swapped
                if Path(root) == troot and rel == probe.name and not swapped:
                    swapped = True
                    if probe.exists() or probe.is_symlink():
                        probe.unlink()
                    os.symlink(redirect.name, probe)
                return original_open_member(root, rel)

            def run_manifest_probe() -> None:
                build_manifest._open_manifest_member_fd = mutating_open_member  # type: ignore[attr-defined]
                try:
                    expect_system_exit_contains(build_manifest.build_manifest_entries, "manifest member")
                finally:
                    build_manifest._open_manifest_member_fd = original_open_member  # type: ignore[attr-defined]

            with_manifest_root(troot, run_manifest_probe)
        finally:
            build_manifest._open_manifest_member_fd = original_open_member  # type: ignore[attr-defined]
            for path in (probe, redirect):
                try:
                    path.unlink()
                except FileNotFoundError:
                    pass


def probe_manifest_member_parent_symlink_recheck() -> None:
    """A manifest source member parent swapped to a symlink after discovery must fail."""

    if not hasattr(os, "symlink"):
        return
    with tiny_release_root() as troot:
        probe_dir = troot / "tmp_release_manifest_parent_probe"
        probe = probe_dir / "leaf.md"
        redirect_dir = troot / "tmp_release_manifest_parent_target"
        redirect_leaf = redirect_dir / "leaf.md"
        original_open_member = build_manifest._open_manifest_member_fd
        swapped = False
        try:
            probe_dir.mkdir()
            probe.write_text("original governed manifest bytes\n", encoding="utf-8")
            redirect_dir.mkdir()
            redirect_leaf.write_text("redirected bytes that must not be manifested\n", encoding="utf-8")

            def mutating_open_member(root, rel):
                nonlocal swapped
                if Path(root) == troot and rel == "tmp_release_manifest_parent_probe/leaf.md" and not swapped:
                    swapped = True
                    if probe.exists() or probe.is_symlink():
                        probe.unlink()
                    try:
                        probe_dir.rmdir()
                    except OSError as exc:
                        fail(f"could not remove manifest probe source parent before symlink swap: {exc}")
                    os.symlink(redirect_dir.name, probe_dir)
                return original_open_member(root, rel)

            def run_manifest_probe() -> None:
                build_manifest._open_manifest_member_fd = mutating_open_member  # type: ignore[attr-defined]
                try:
                    expect_system_exit_contains(build_manifest.build_manifest_entries, "manifest member ancestry")
                finally:
                    build_manifest._open_manifest_member_fd = original_open_member  # type: ignore[attr-defined]

            with_manifest_root(troot, run_manifest_probe)
        finally:
            build_manifest._open_manifest_member_fd = original_open_member  # type: ignore[attr-defined]
            for path in (probe, redirect_leaf):
                try:
                    path.unlink()
                except FileNotFoundError:
                    pass
            for path in (probe_dir, redirect_dir):
                try:
                    if path.is_symlink():
                        path.unlink()
                    else:
                        path.rmdir()
                except FileNotFoundError:
                    pass
                except OSError:
                    pass

def probe_zip_source_root_path_firewall() -> None:
    """Builder source roots must be concrete before release file discovery."""

    explicit_dot_root = os.fspath(ROOT.parent) + f"/./{ROOT.name}"
    expect_system_exit_contains(
        lambda: build_release_zip.release_file_names(explicit_dot_root),
        "current/parent",
    )

    repeated_sep_root = os.fspath(ROOT.parent) + f"//{ROOT.name}"
    expect_system_exit_contains(
        lambda: build_release_zip.release_file_names(repeated_sep_root),
        "empty separator",
    )

    trailing_sep_root = os.fspath(ROOT) + os.sep
    expect_system_exit_contains(
        lambda: build_release_zip.release_file_names(trailing_sep_root),
        "trailing separator",
    )

    with tempfile.TemporaryDirectory(prefix="tes_builder_root_") as td:
        tdir = Path(td)
        plain_file_root = tdir / "not-a-directory"
        plain_file_root.write_text("not a release root\n", encoding="utf-8")
        expect_system_exit_contains(
            lambda: build_release_zip.release_file_names(plain_file_root),
            "must be a directory",
        )

        if hasattr(os, "symlink"):
            final_link = tdir / "repo-link"
            if symlink_or_skip(ROOT, final_link):
                expect_system_exit_contains(
                    lambda: build_release_zip.release_file_names(final_link),
                    "must not be a symlink",
                )

            parent_link = tdir / "parent-link"
            if symlink_or_skip(ROOT.parent, parent_link):
                routed_root = parent_link / ROOT.name
                expect_system_exit_contains(
                    lambda: build_release_zip.release_file_names(routed_root),
                    "symlink component",
                )



def probe_zip_source_output_alias_symlink_rejection() -> None:
    """A governed symlink must not be hidden by the output-ZIP skip path."""

    if not hasattr(os, "symlink"):
        return
    with tiny_release_root() as troot:
        with tempfile.TemporaryDirectory(prefix="tes_builder_source_alias_") as td:
            out = Path(td) / "release.zip"
            out.write_text("placeholder output artifact\n", encoding="utf-8")
            probe = troot / "tmp_release_output_alias_probe.md"
            try:
                if not symlink_or_skip(out, probe):
                    return
                expect_system_exit_contains(
                    lambda: build_release_zip.release_file_names(troot, out),
                    "symlink",
                )
            finally:
                try:
                    probe.unlink()
                except FileNotFoundError:
                    pass


def probe_zip_source_member_read_recheck() -> None:
    """A source member swapped to a symlink after discovery must fail closed."""

    if not hasattr(os, "symlink"):
        return
    with tiny_release_root() as troot:
        probe = troot / "tmp_release_source_read_probe.md"
        redirect = troot / "tmp_release_source_read_target.md"
        original_release_file_names = build_release_zip.release_file_names
        try:
            probe.write_text("original governed source bytes\n", encoding="utf-8")
            redirect.write_text("redirected bytes that must not be packaged\n", encoding="utf-8")

            def mutating_release_file_names(repo_root, out_zip=None):
                rels = original_release_file_names(repo_root, out_zip)
                if Path(repo_root) == troot:
                    if probe.exists() or probe.is_symlink():
                        probe.unlink()
                    os.symlink(redirect.name, probe)
                return rels

            build_release_zip.release_file_names = mutating_release_file_names  # type: ignore[assignment]
            with tempfile.TemporaryDirectory(prefix="tes_builder_source_read_") as td:
                out = Path(td) / "release.zip"
                expect_system_exit_contains(
                    lambda: build_release_zip.build_zip(troot, out),
                    "release source member",
                )
                if out.exists():
                    fail("build_release_zip published an archive after a source member symlink swap")
        finally:
            build_release_zip.release_file_names = original_release_file_names  # type: ignore[assignment]
            for path in (probe, redirect):
                try:
                    path.unlink()
                except FileNotFoundError:
                    pass


def probe_zip_source_member_parent_symlink_recheck() -> None:
    """A source member parent swapped to a symlink after discovery must fail."""

    if not hasattr(os, "symlink"):
        return
    with tiny_release_root() as troot:
        probe_dir = troot / "tmp_release_source_parent_probe"
        probe = probe_dir / "leaf.md"
        redirect_dir = troot / "tmp_release_source_parent_target"
        redirect_leaf = redirect_dir / "leaf.md"
        original_release_file_names = build_release_zip.release_file_names
        try:
            probe_dir.mkdir()
            probe.write_text("original governed source bytes\n", encoding="utf-8")
            redirect_dir.mkdir()
            redirect_leaf.write_text("redirected bytes that must not be packaged\n", encoding="utf-8")

            def mutating_release_file_names(repo_root, out_zip=None):
                rels = original_release_file_names(repo_root, out_zip)
                if Path(repo_root) == troot:
                    if probe.exists() or probe.is_symlink():
                        probe.unlink()
                    try:
                        probe_dir.rmdir()
                    except OSError as exc:
                        fail(f"could not remove probe source parent before symlink swap: {exc}")
                    os.symlink(redirect_dir.name, probe_dir)
                return rels

            build_release_zip.release_file_names = mutating_release_file_names  # type: ignore[assignment]
            with tempfile.TemporaryDirectory(prefix="tes_builder_source_parent_") as td:
                out = Path(td) / "release.zip"
                expect_system_exit_contains(
                    lambda: build_release_zip.build_zip(troot, out),
                    "source member ancestry",
                )
                if out.exists():
                    fail("build_release_zip published an archive after a source member parent symlink swap")
        finally:
            build_release_zip.release_file_names = original_release_file_names  # type: ignore[assignment]
            for path in (probe, redirect_leaf):
                try:
                    path.unlink()
                except FileNotFoundError:
                    pass
            for path in (probe_dir, redirect_dir):
                try:
                    if path.is_symlink():
                        path.unlink()
                    else:
                        path.rmdir()
                except FileNotFoundError:
                    pass
                except OSError:
                    pass


def probe_zip_output_path_firewall() -> None:
    """Builder output routes must match verifier/extractor path strictness."""

    with tiny_release_root() as troot:
        with tempfile.TemporaryDirectory(prefix="tes_builder_output_") as td:
            tdir = Path(td)

            lexical_out = os.fspath(tdir / "lexical") + "/./release.zip"
            expect_system_exit_contains(lambda: build_release_zip.build_zip(troot, lexical_out), "current/parent")
            if (tdir / "lexical").exists():
                fail("build_release_zip created an output parent for a lexically ambiguous output path")

            repeated_sep_out = os.fspath(tdir) + "//release.zip"
            expect_system_exit_contains(lambda: build_release_zip.build_zip(troot, repeated_sep_out), "empty separator")
            if (tdir / "release.zip").exists():
                fail("build_release_zip normalized away a repeated separator in the output path")

            dir_out = tdir / "directory-output.zip"
            dir_out.mkdir()
            expect_system_exit_contains(lambda: build_release_zip.build_zip(troot, dir_out), "regular file")

            if hasattr(os, "symlink"):
                target_zip = tdir / "real.zip"
                target_zip.write_text("operator target that must not be overwritten through a symlink\n", encoding="utf-8")
                symlink_out = tdir / "symlink-output.zip"
                if symlink_or_skip(target_zip.name, symlink_out):
                    expect_system_exit_contains(lambda: build_release_zip.build_zip(troot, symlink_out), "must not be a symlink")
                    if not symlink_out.is_symlink():
                        fail("build_release_zip removed or replaced a symlinked output path")

                real_parent = tdir / "real-parent"
                real_parent.mkdir()
                symlink_parent = tdir / "symlink-parent"
                if symlink_or_skip(real_parent, symlink_parent):
                    redirected_out = symlink_parent / "release.zip"
                    expect_system_exit_contains(lambda: build_release_zip.build_zip(troot, redirected_out), "symlink component")
                    if (real_parent / "release.zip").exists():
                        fail("build_release_zip published through a symlinked output parent")


def probe_zip_output_publish_recheck() -> None:
    """A final-path symlink swap before publish must not be followed."""

    if not hasattr(os, "symlink"):
        return
    with tiny_release_root() as troot:
        with tempfile.TemporaryDirectory(prefix="tes_builder_publish_") as td:
            tdir = Path(td)
            out = tdir / "release.zip"
            target = tdir / "redirect-target.zip"
            target.write_text("must not receive release bytes\n", encoding="utf-8")
            original_writer = build_release_zip._write_zip_bytes

            def mutating_writer(repo_root: Path, rel_files: list[str], tmp_path: Path) -> None:
                original_writer(repo_root, rel_files, tmp_path)
                try:
                    os.symlink(target.name, out)
                except (OSError, NotImplementedError):
                    return

            build_release_zip._write_zip_bytes = mutating_writer  # type: ignore[attr-defined]
            try:
                expect_system_exit_contains(lambda: build_release_zip.build_zip(troot, out), "must not be a symlink")
            finally:
                build_release_zip._write_zip_bytes = original_writer  # type: ignore[attr-defined]

            if out.exists() and not out.is_symlink():
                fail("build_release_zip replaced a final-path symlink introduced before publish")
            if target.read_text(encoding="utf-8") != "must not receive release bytes\n":
                fail("build_release_zip followed a final-path symlink and overwrote the target")
            leftovers = list(tdir.glob(f".{out.name}.tmp.*.zip"))
            if leftovers:
                fail("build_release_zip left temporary ZIP output behind after publish rejection")

def main() -> int:
    if not README.exists():
        fail("README.md missing; symlink probe target unavailable")
    probe_crlf_manifest_check()
    probe_manifest_control_file_route_rejection()
    probe_manifest_control_publish_recheck()
    probe_symlink_file_rejection()
    probe_special_file_rejection()
    probe_unsafe_governed_path_rejection()
    probe_manifest_source_root_path_firewall()
    probe_manifest_member_read_recheck()
    probe_manifest_member_parent_symlink_recheck()
    probe_zip_source_root_path_firewall()
    probe_zip_source_output_alias_symlink_rejection()
    probe_zip_source_member_read_recheck()
    probe_zip_source_member_parent_symlink_recheck()
    probe_zip_output_path_firewall()
    probe_zip_output_publish_recheck()
    print("PASS: release builders use raw manifest bytes, protect MANIFEST.sha256 control-file read/write routes, reject unsafe paths, symlinks, and special files in governed scope, reject ambiguous or symlink-routed manifest and release ZIP source/output paths, and recheck manifest and ZIP source-member leaves and ancestry before hashing or ZIP publication")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
