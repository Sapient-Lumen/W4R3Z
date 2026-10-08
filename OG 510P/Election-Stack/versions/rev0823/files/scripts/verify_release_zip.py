#!/usr/bin/env python3
"""Verify a deterministic Election Stack release ZIP.

This checks the archive artifact itself, not merely an extracted tree:
- safe, unique, sorted member names
- canonical byte layout: no preamble, no overlay, contiguous local records
- fixed timestamps, canonical 0644 permissions, and stored entries
- VERSION/MANIFEST presence and optional filename-version agreement
- MANIFEST.sha256 closure over every non-manifest ZIP entry
- per-entry SHA-256 hashes against in-ZIP bytes
- byte-for-byte canonical rebuild from the sealed stored member payloads
- lexical input-path canonicality and single-snapshot archive reads so path, hash, layout, parser, and extractor checks stay coherent

The script is stdlib-only and does not require extracting the ZIP.
"""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
import re
import stat
import struct
import sys
import zipfile
from dataclasses import dataclass, field
from pathlib import Path

sys.dont_write_bytecode = True

import release_control_files
import release_path_policy

FIXED_ZIP_DT = (1980, 1, 1, 0, 0, 0)
MANIFEST_NAME = release_control_files.MANIFEST_NAME
VERSION_NAME = release_control_files.VERSION_NAME
VERSION_RE = release_control_files.VERSION_RE
FILENAME_VERSION_TOKEN_RE = re.compile(
    r"(?:^|[-_])(?P<token>(?P<kind>rev|v)(?P<num>\d+))(?=$|[-_.])",
    re.IGNORECASE,
)
CANONICAL_MODE = 0o644
CANONICAL_COMPRESSION = zipfile.ZIP_STORED
CANONICAL_COMPRESSION_NAME = "ZIP_STORED"
EOCD_SIG = b"PK\x05\x06"
LOCAL_FILE_HEADER_SIG = b"PK\x03\x04"
CENTRAL_DIR_HEADER_SIG = b"PK\x01\x02"
EOCD_FIXED_SIZE = 22
LOCAL_FILE_HEADER_FIXED_SIZE = 30
CENTRAL_DIR_HEADER_FIXED_SIZE = 46
DATA_DESCRIPTOR_FLAG = 0x0008
FIXED_DOS_TIME = 0
FIXED_DOS_DATE = 33  # 1980-01-01
EXPECTED_VERSION_MADE_BY = (3 << 8) | 20  # Unix + ZIP 2.0
EXPECTED_VERSION_NEEDED = 20
EXPECTED_GENERAL_PURPOSE_FLAG = 0



@dataclass
class VerifyResult:
    ok: bool
    zip_sha256: str
    version: str | None
    entries: int
    manifest_entries: int
    problems: list[str] = field(default_factory=list)
    zip_bytes: bytes = field(default=b"", repr=False, compare=False)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _decode_pathlike(path: Path | str) -> str:
    """Return a raw operator-supplied path string for lexical preflight.

    ``Path`` objects are already partly normalized by pathlib; the CLI passes the
    original ``argparse`` string so current-directory, parent-directory, repeated
    separator, and trailing-separator components remain observable before any
    filesystem lookup.  Imported callers should pass a string when they need the
    same raw lexical audit boundary.
    """

    raw = os.fspath(path)
    if isinstance(raw, bytes):  # pragma: no cover - PathLike bytes are uncommon in this repo.
        raw = raw.decode(sys.getfilesystemencoding(), "surrogateescape")
    return raw


def _input_path_lexical_problems(path: Path | str) -> list[str]:
    """Return problems for ambiguous operator-supplied ZIP input paths.

    Release ZIP filenames are evidence-bearing carrier metadata once they contain
    version tokens.  The input path used to present that carrier should therefore
    be as concrete as the symlink and single-snapshot checks around it: no
    ``.``, ``..``, repeated separator, NUL, or trailing-separator spelling may be
    accepted and then hidden by ``pathlib`` or the operating system resolver.
    """

    raw = _decode_pathlike(path)
    if raw == "":
        return ["release ZIP input path must not be empty"]
    if "\x00" in raw:
        return ["release ZIP input path must not contain NUL bytes"]

    seps = [os.sep]
    if os.altsep and os.altsep not in seps:
        seps.append(os.altsep)

    if len(raw) > 1 and any(raw.endswith(sep) for sep in seps):
        return [f"release ZIP input path must identify a file without a trailing separator: {raw!r}"]

    normalized = raw
    for sep in seps:
        if sep != "/":
            normalized = normalized.replace(sep, "/")

    parts = normalized.split("/")
    for idx, part in enumerate(parts):
        # A single leading empty component is the root marker for absolute paths.
        if idx == 0 and part == "":
            continue
        if part == "":
            return [f"release ZIP input path must not contain empty separator components: {raw!r}"]
        if part in {".", ".."}:
            return [f"release ZIP input path must not contain current/parent traversal components: {raw!r}"]
    return []


def _read_zip_snapshot(path: Path) -> tuple[bytes | None, list[str]]:
    """Read the candidate ZIP bytes exactly once through a regular-file handle.

    Verification must not compute the artifact hash from one path read, parse ZIP
    members from a second path read, and inspect layout bytes from a third path
    read.  A mutable or replaced input path could otherwise make diagnostics
    describe a mixture of byte streams.  This helper returns one immutable byte
    snapshot; every later verifier stage operates on that same buffer.
    """

    flags = os.O_RDONLY
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW

    try:
        fd = os.open(path, flags)
    except OSError as exc:
        return None, [f"could not open ZIP snapshot: {exc}"]

    try:
        try:
            before = os.fstat(fd)
        except OSError as exc:
            return None, [f"could not stat open ZIP snapshot: {exc}"]

        if not stat.S_ISREG(before.st_mode):
            return None, [f"release ZIP input path must open as a regular file: {str(path)!r}"]

        with os.fdopen(fd, "rb") as f:
            fd = -1
            data = f.read()
            try:
                after = os.fstat(f.fileno())
            except OSError as exc:
                return None, [f"could not restat open ZIP snapshot after read: {exc}"]
    finally:
        if fd >= 0:
            try:
                os.close(fd)
            except OSError:
                pass

    if before.st_size != after.st_size or after.st_size != len(data):
        return None, [
            "release ZIP input changed size while being snapshotted "
            f"(before={before.st_size}, after={after.st_size}, read={len(data)})"
        ]

    return data, []


def _absolute_lexical_path(path: Path) -> Path:
    """Return an absolute path without resolving symlinks in the input."""

    return path if path.is_absolute() else Path.cwd() / path


def _path_ancestors_no_symlinks(path: Path | str) -> list[str]:
    """Return problems if an existing input path is routed through symlinks.

    The release ZIP filename is carrier metadata.  Resolving an operator-supplied
    path before verification can replace that carrier name with the target name
    of a symlink and can also route the read through a symlinked directory.  The
    artifact verifier therefore accepts only a concrete regular file reached via
    concrete ancestor directories.
    """

    problems: list[str] = []
    raw = Path(path)
    lexical = _absolute_lexical_path(raw)

    try:
        st = lexical.lstat()
    except OSError as exc:
        return [f"could not stat release ZIP input path {str(raw)!r}: {exc}"]

    if stat.S_ISLNK(st.st_mode):
        problems.append(f"release ZIP input path must not be a symlink: {str(raw)!r}")
    elif not stat.S_ISREG(st.st_mode):
        problems.append(f"release ZIP input path must be a regular file: {str(raw)!r}")

    parts = lexical.parts
    if not parts:
        return problems
    if lexical.is_absolute():
        cur = Path(parts[0])
        rest = parts[1:-1]
    else:  # pragma: no cover - lexical is absolute for normal callers
        cur = Path()
        rest = parts[:-1]

    for part in rest:
        cur = cur / part
        try:
            ast = cur.lstat()
        except OSError as exc:
            problems.append(f"could not stat release ZIP input path ancestor {str(cur)!r}: {exc}")
            break
        if stat.S_ISLNK(ast.st_mode):
            problems.append(f"release ZIP input path ancestry must not contain symlink component: {str(cur)!r}")
            break

    return problems


def _safe_member_name(name: str) -> str | None:
    problem = release_path_policy.release_path_problem(name)
    if problem:
        return problem
    return None


def _parse_manifest(raw: bytes) -> tuple[dict[str, str], list[str]]:
    return release_control_files.parse_manifest_bytes(raw)


def _filename_version_tokens(path: Path) -> list[tuple[str, str, str]]:
    """Return version-like filename tokens as (raw token, kind, digits).

    Release names may carry a padded ``revNNNN`` sorting token and may also
    carry an unpadded semantic ``vNNN`` token.  Treat every such token as
    evidence-bearing metadata once it appears in the filename; a verifier must
    not silently use only the first matching token when a later token disagrees.
    """

    return [
        (m.group("token"), m.group("kind"), m.group("num"))
        for m in FILENAME_VERSION_TOKEN_RE.finditer(path.name)
    ]


def _semantic_filename_version(token: str, kind: str, digits: str) -> tuple[str | None, list[str]]:
    """Return the semantic version for one filename token, plus problems."""

    problems: list[str] = []
    kind_l = kind.lower()
    if kind_l == "rev":
        # rev tokens are artifact-sort labels; leading zeroes are allowed there.
        return f"v{int(digits)}", problems

    semantic = f"v{digits}"
    if kind != "v" or not VERSION_RE.fullmatch(semantic):
        problems.append(
            f"filename semantic version token {token!r} must be lowercase canonical vNNN with no leading zeroes"
        )
    return f"v{int(digits)}", problems


def _version_from_filename(path: Path) -> str | None:
    tokens = _filename_version_tokens(path)
    if not tokens:
        return None
    token, kind, digits = tokens[0]
    semantic, _problems = _semantic_filename_version(token, kind, digits)
    return semantic


def _filename_version_problems(path: Path, version: str | None) -> list[str]:
    """Return filename/version-token coherence problems.

    A filename without a version token remains acceptable for local diagnostics.
    Once a filename carries one or more ``revNNNN``/``vNNN`` tokens, every token
    must normalize to the same semantic version, and any semantic ``v`` token
    must use the same unpadded grammar as the internal VERSION file.
    """

    problems: list[str] = []
    semantics: list[tuple[str, str]] = []
    for token, kind, digits in _filename_version_tokens(path):
        semantic, token_problems = _semantic_filename_version(token, kind, digits)
        problems.extend(token_problems)
        if semantic is not None:
            semantics.append((token, semantic))

    unique = sorted({semantic for _token, semantic in semantics})
    if len(unique) > 1:
        details = ", ".join(f"{token}->{semantic}" for token, semantic in semantics)
        problems.append(f"filename version tokens disagree: {details}")

    if version is not None:
        for token, semantic in semantics:
            if semantic != version:
                problems.append(f"filename version token {token!r} normalizes to {semantic}, not VERSION {version}")

    return problems


def _decode_zip_name(raw_name: bytes, flag_bits: int) -> str | None:
    encoding = "utf-8" if flag_bits & 0x0800 else "cp437"
    try:
        return raw_name.decode(encoding)
    except UnicodeDecodeError:
        return None


def _canonical_zipinfo(name: str) -> zipfile.ZipInfo:
    """Return the canonical ZipInfo record used by release ZIP rebuilds."""

    zi = zipfile.ZipInfo(name)
    zi.compress_type = CANONICAL_COMPRESSION
    zi.date_time = FIXED_ZIP_DT
    zi.create_system = 3
    zi.create_version = EXPECTED_VERSION_NEEDED
    zi.extract_version = EXPECTED_VERSION_NEEDED
    zi.flag_bits = EXPECTED_GENERAL_PURPOSE_FLAG
    zi.external_attr = (CANONICAL_MODE & 0xFFFF) << 16
    return zi


def _canonical_rebuild_bytes(zf: zipfile.ZipFile, infos: list[zipfile.ZipInfo]) -> bytes:
    """Rebuild the ZIP byte stream from in-archive member payload bytes.

    The layout verifier proves that the archive has safe member names and
    canonical header fields.  This function closes the remaining byte-stream
    seam by rebuilding the ZIP from sealed member payload bytes.  Release ZIPs
    use stored members, so this rebuild is independent of zlib/DEFLATE runtime
    choices while still catching raw header/order/size drift.
    """

    out = io.BytesIO()
    with zipfile.ZipFile(
        out,
        "w",
        compression=CANONICAL_COMPRESSION,
        strict_timestamps=False,
    ) as rebuilt:
        for info in sorted(infos, key=lambda item: item.filename):
            zi = _canonical_zipinfo(info.filename)
            with zf.open(info, "r") as f:
                rebuilt.writestr(zi, f.read())
    return out.getvalue()


def _canonical_rebuild_problems(actual: bytes, zf: zipfile.ZipFile, infos: list[zipfile.ZipInfo]) -> list[str]:
    """Return problems if raw archive bytes differ from canonical rebuild bytes."""

    try:
        rebuilt = _canonical_rebuild_bytes(zf, infos)
    except Exception as exc:  # pragma: no cover - defensive reporting for corrupt archives
        return [f"could not perform canonical ZIP rebuild comparison: {exc}"]

    if actual == rebuilt:
        return []
    return [
        "ZIP byte stream does not match canonical rebuild from sealed member bytes "
        f"(actual_sha256={sha256_bytes(actual)}, canonical_sha256={sha256_bytes(rebuilt)})"
    ]


def _central_directory_problems(
    data: bytes,
    cd_offset: int,
    final_eocd_offset: int,
    infos: list[zipfile.ZipInfo],
) -> list[str]:
    """Return canonical central-directory problems for the raw ZIP bytes."""

    problems: list[str] = []
    pos = cd_offset
    for info in infos:
        if pos + CENTRAL_DIR_HEADER_FIXED_SIZE > final_eocd_offset:
            problems.append(f"central directory entry for {info.filename!r} extends beyond EOCD")
            return problems
        if data[pos:pos + 4] != CENTRAL_DIR_HEADER_SIG:
            problems.append(f"central directory entry for {info.filename!r} at byte {pos} does not start with PK\\x01\\x02")
            return problems
        try:
            (
                _sig,
                version_made_by,
                version_needed,
                flag_bits,
                compression_method,
                mod_time,
                mod_date,
                crc32,
                compressed_size,
                uncompressed_size,
                name_len,
                extra_len,
                comment_len,
                disk_start,
                internal_attr,
                external_attr,
                local_header_offset,
            ) = struct.unpack_from("<IHHHHHHIIIHHHHHII", data, pos)
        except struct.error as exc:
            problems.append(f"central directory entry for {info.filename!r} could not be parsed: {exc}")
            return problems

        name_start = pos + CENTRAL_DIR_HEADER_FIXED_SIZE
        name_end = name_start + name_len
        extra_end = name_end + extra_len
        comment_end = extra_end + comment_len
        if comment_end > final_eocd_offset:
            problems.append(f"central directory entry for {info.filename!r} name/extra/comment extends beyond EOCD")
            return problems

        central_name = _decode_zip_name(data[name_start:name_end], flag_bits)
        if central_name != info.filename:
            problems.append(f"{info.filename}: central-directory name {central_name!r} does not match zipfile name")
        if version_made_by != EXPECTED_VERSION_MADE_BY:
            problems.append(f"{info.filename}: version_made_by {version_made_by} != canonical {EXPECTED_VERSION_MADE_BY}")
        if version_needed != EXPECTED_VERSION_NEEDED:
            problems.append(f"{info.filename}: version_needed {version_needed} != canonical {EXPECTED_VERSION_NEEDED}")
        if flag_bits != EXPECTED_GENERAL_PURPOSE_FLAG:
            problems.append(f"{info.filename}: general-purpose flag bits {flag_bits:#06x} != canonical 0x0000")
        if compression_method != CANONICAL_COMPRESSION:
            problems.append(f"{info.filename}: central compression method {compression_method} != {CANONICAL_COMPRESSION_NAME}")
        if mod_time != FIXED_DOS_TIME or mod_date != FIXED_DOS_DATE:
            problems.append(f"{info.filename}: central DOS timestamp time={mod_time} date={mod_date} != canonical")
        if crc32 != info.CRC:
            problems.append(f"{info.filename}: central CRC {crc32:08x} != zipfile {info.CRC:08x}")
        if compressed_size != info.compress_size:
            problems.append(f"{info.filename}: central compressed size {compressed_size} != zipfile {info.compress_size}")
        if uncompressed_size != info.file_size:
            problems.append(f"{info.filename}: central uncompressed size {uncompressed_size} != zipfile {info.file_size}")
        if compression_method == CANONICAL_COMPRESSION and compressed_size != uncompressed_size:
            problems.append(f"{info.filename}: stored central sizes differ compressed={compressed_size} uncompressed={uncompressed_size}")
        if extra_len != 0:
            problems.append(f"{info.filename}: central extra fields must be empty")
        if comment_len != 0:
            problems.append(f"{info.filename}: central per-file comments must be empty")
        if disk_start != 0:
            problems.append(f"{info.filename}: central disk_start {disk_start} != 0")
        if internal_attr != 0:
            problems.append(f"{info.filename}: central internal_attr {internal_attr} != 0")
        expected_external = (CANONICAL_MODE & 0xFFFF) << 16
        if external_attr != expected_external:
            problems.append(f"{info.filename}: central external_attr {external_attr:#010x} != canonical {expected_external:#010x}")
        if local_header_offset != info.header_offset:
            problems.append(f"{info.filename}: central local-header offset {local_header_offset} != zipfile {info.header_offset}")

        pos = comment_end

    if pos != final_eocd_offset:
        problems.append(f"central directory parse ended at byte {pos}, expected EOCD at byte {final_eocd_offset}")
    return problems


def _zip_layout_problems(data: bytes, zf: zipfile.ZipFile, infos: list[zipfile.ZipInfo]) -> list[str]:
    """Return deterministic-layout problems for the raw ZIP byte stream.

    ``zipfile.ZipFile`` deliberately accepts useful non-release shapes such as
    self-extracting preambles and appended overlay bytes.  The Election Stack
    release artifact is stricter: it is a canonical ZIP byte stream whose local
    records begin at byte zero, are contiguous, and are followed immediately by
    the central directory and an empty-comment EOCD record at EOF.
    """

    problems: list[str] = []

    if len(data) < EOCD_FIXED_SIZE:
        return ["ZIP byte stream is too short to contain an EOCD record"]

    final_eocd_offset = len(data) - EOCD_FIXED_SIZE
    if data[final_eocd_offset:final_eocd_offset + 4] != EOCD_SIG:
        # zipfile may still accept this if it finds an earlier EOCD and treats
        # later bytes as an overlay; deterministic releases must not.
        found = data.rfind(EOCD_SIG)
        if found >= 0:
            problems.append(
                "ZIP EOCD record must be the final empty-comment record; "
                f"found EOCD at byte {found} with {len(data) - found - EOCD_FIXED_SIZE} trailing byte(s)"
            )
        else:
            problems.append("ZIP EOCD record not found at final empty-comment position")
        return problems

    try:
        (
            _sig,
            disk_no,
            cd_start_disk,
            entries_this_disk,
            entries_total,
            cd_size,
            cd_offset,
            comment_len,
        ) = struct.unpack_from("<IHHHHIIH", data, final_eocd_offset)
    except struct.error as exc:
        return [f"could not parse ZIP EOCD record: {exc}"]

    if comment_len != 0:
        problems.append(f"ZIP EOCD comment length must be 0, got {comment_len}")
    if final_eocd_offset + EOCD_FIXED_SIZE + comment_len != len(data):
        problems.append("ZIP EOCD does not terminate exactly at EOF")
    if disk_no != 0 or cd_start_disk != 0:
        problems.append("multi-disk ZIP archives are not allowed")
    if entries_this_disk != entries_total:
        problems.append("ZIP central-directory entry counts disagree across disks")
    if entries_total != len(infos):
        problems.append(f"ZIP EOCD entry count {entries_total} != central-directory entries read {len(infos)}")
    if cd_offset + cd_size != final_eocd_offset:
        problems.append(
            f"central directory must end immediately before EOCD: "
            f"offset={cd_offset} size={cd_size} eocd={final_eocd_offset}"
        )
    if getattr(zf, "start_dir", cd_offset) != cd_offset:
        problems.append(
            f"central directory start offset mismatch: EOCD={cd_offset} zipfile={getattr(zf, 'start_dir', None)}"
        )
    if infos and data[cd_offset:cd_offset + 4] != CENTRAL_DIR_HEADER_SIG:
        problems.append(f"central directory does not begin with a central-file-header signature at byte {cd_offset}")
    problems.extend(_central_directory_problems(data, cd_offset, final_eocd_offset, infos))

    if not infos:
        return problems

    offsets = [info.header_offset for info in infos]
    if offsets[0] != 0:
        problems.append(
            f"ZIP local payload must begin at byte 0; first local header is at byte {offsets[0]} "
            "(preamble/self-extractor data is not allowed)"
        )
    if offsets != sorted(offsets):
        problems.append("central-directory member order must match local-file-header order")

    expected = 0
    for info in infos:
        off = info.header_offset
        if off != expected:
            problems.append(f"{info.filename}: local header offset {off} != expected contiguous offset {expected}")
            # Keep parsing the actual header to report additional concrete facts.
        if off < 0 or off + LOCAL_FILE_HEADER_FIXED_SIZE > len(data):
            problems.append(f"{info.filename}: local header offset {off} is outside the ZIP byte stream")
            continue
        if data[off:off + 4] != LOCAL_FILE_HEADER_SIG:
            problems.append(f"{info.filename}: local header at byte {off} does not start with PK\\x03\\x04")
            continue
        try:
            (
                _local_sig,
                version_needed,
                flag_bits,
                compression_method,
                mod_time,
                mod_date,
                crc32,
                compressed_size,
                uncompressed_size,
                name_len,
                extra_len,
            ) = struct.unpack_from("<IHHHHHIIIHH", data, off)
        except struct.error as exc:
            problems.append(f"{info.filename}: could not parse local header: {exc}")
            continue

        name_start = off + LOCAL_FILE_HEADER_FIXED_SIZE
        name_end = name_start + name_len
        extra_end = name_end + extra_len
        if extra_end > len(data):
            problems.append(f"{info.filename}: local header name/extra fields extend beyond EOF")
            continue

        raw_name = data[name_start:name_end]
        try:
            local_name = raw_name.decode("utf-8" if flag_bits & 0x0800 else "cp437")
        except UnicodeDecodeError as exc:
            problems.append(f"{info.filename}: local header name is not decodable: {exc}")
            local_name = None
        if local_name != info.filename:
            problems.append(f"{info.filename}: local header name {local_name!r} does not match central-directory name")
        if version_needed != EXPECTED_VERSION_NEEDED:
            problems.append(f"{info.filename}: local version_needed {version_needed} != canonical {EXPECTED_VERSION_NEEDED}")
        if flag_bits != EXPECTED_GENERAL_PURPOSE_FLAG:
            problems.append(f"{info.filename}: local general-purpose flag bits {flag_bits:#06x} != canonical 0x0000")
        if flag_bits & DATA_DESCRIPTOR_FLAG:
            problems.append(f"{info.filename}: data descriptors are not allowed in deterministic release ZIPs")
        if compression_method != CANONICAL_COMPRESSION:
            problems.append(f"{info.filename}: local compression method {compression_method} != {CANONICAL_COMPRESSION_NAME}")
        if mod_time != FIXED_DOS_TIME or mod_date != FIXED_DOS_DATE:
            problems.append(f"{info.filename}: local DOS timestamp time={mod_time} date={mod_date} != canonical")
        if extra_len != 0:
            problems.append(f"{info.filename}: local extra fields must be empty")
        if compressed_size != info.compress_size:
            problems.append(f"{info.filename}: local compressed size {compressed_size} != central {info.compress_size}")
        if uncompressed_size != info.file_size:
            problems.append(f"{info.filename}: local uncompressed size {uncompressed_size} != central {info.file_size}")
        if compression_method == CANONICAL_COMPRESSION and compressed_size != uncompressed_size:
            problems.append(f"{info.filename}: stored local sizes differ compressed={compressed_size} uncompressed={uncompressed_size}")
        if crc32 != info.CRC:
            problems.append(f"{info.filename}: local CRC {crc32:08x} != central {info.CRC:08x}")

        expected = extra_end + info.compress_size

    if expected != cd_offset:
        problems.append(f"local file records end at byte {expected}, but central directory starts at byte {cd_offset}")

    return problems


def verify_zip(path: Path | str) -> VerifyResult:
    problems: list[str] = []
    lexical_problems = _input_path_lexical_problems(path)
    if lexical_problems:
        return VerifyResult(False, "", None, 0, 0, lexical_problems)
    input_path = Path(_decode_pathlike(path))
    input_path_problems = _path_ancestors_no_symlinks(input_path)
    if input_path_problems:
        return VerifyResult(False, "", None, 0, 0, input_path_problems)

    # Use the operator-supplied basename for carrier-token checks, but read the
    # concrete lexical path after rejecting symlink final components and
    # symlink-routed ancestry.
    carrier_path = input_path
    path = _absolute_lexical_path(input_path)
    zip_bytes, snapshot_problems = _read_zip_snapshot(path)
    if snapshot_problems or zip_bytes is None:
        return VerifyResult(False, "", None, 0, 0, snapshot_problems)
    zip_hash = sha256_bytes(zip_bytes)
    version: str | None = None

    try:
        zf = zipfile.ZipFile(io.BytesIO(zip_bytes))
    except (OSError, zipfile.BadZipFile) as exc:
        return VerifyResult(False, zip_hash, None, 0, 0, [f"could not open ZIP: {exc}"], zip_bytes=zip_bytes)

    with zf:
        bad_crc = zf.testzip()
        if bad_crc is not None:
            problems.append(f"ZIP CRC check failed first at {bad_crc!r}")

        infos = zf.infolist()
        names = [info.filename for info in infos]
        problems.extend(_zip_layout_problems(zip_bytes, zf, infos))
        if len(names) != len(set(names)):
            seen: set[str] = set()
            dups: list[str] = []
            for n in names:
                if n in seen and n not in dups:
                    dups.append(n)
                seen.add(n)
            problems.append("duplicate ZIP members: " + ", ".join(dups[:10]))

        portable_collisions = release_path_policy.find_portable_path_collisions(names)
        for key, vals in sorted(portable_collisions.items()):
            problems.append(f"portable ZIP member path collision for {key!r}: {', '.join(vals)}")

        shape_conflicts = release_path_policy.find_extraction_shape_conflicts(names)
        for prefix, children in sorted(shape_conflicts.items()):
            problems.append(
                f"ZIP extraction shape conflict: file path {prefix!r} also prefixes {', '.join(children)}"
            )

        if names != sorted(names):
            problems.append("ZIP members must be sorted by path")

        for info in infos:
            unsafe = _safe_member_name(info.filename)
            if unsafe:
                problems.append(f"unsafe ZIP member {info.filename!r}: {unsafe}")
            if info.date_time != FIXED_ZIP_DT:
                problems.append(f"{info.filename}: timestamp {info.date_time!r} != {FIXED_ZIP_DT!r}")
            if info.compress_type != CANONICAL_COMPRESSION:
                problems.append(f"{info.filename}: compress_type {info.compress_type} != {CANONICAL_COMPRESSION_NAME}")
            mode = (info.external_attr >> 16) & 0xFFFF
            if mode != CANONICAL_MODE:
                problems.append(f"{info.filename}: mode {oct(mode)} != canonical {oct(CANONICAL_MODE)}")
            if info.extra:
                problems.append(f"{info.filename}: ZIP extra fields must be empty")
            if info.comment:
                problems.append(f"{info.filename}: per-file ZIP comments must be empty")

        if zf.comment:
            problems.append("archive ZIP comment must be empty")

        if VERSION_NAME not in names:
            problems.append("missing VERSION entry")
            version_bytes = b""
        else:
            version_bytes = zf.read(VERSION_NAME)
            version, version_problems = release_control_files.parse_version_bytes(version_bytes)
            problems.extend(version_problems)

        problems.extend(_filename_version_problems(carrier_path, version))

        if MANIFEST_NAME not in names:
            problems.append("missing MANIFEST.sha256 entry")
            manifest_entries: dict[str, str] = {}
        else:
            manifest_entries, manifest_problems = _parse_manifest(zf.read(MANIFEST_NAME))
            problems.extend(manifest_problems)

        zip_payload_names = set(names) - {MANIFEST_NAME}
        manifest_names = set(manifest_entries)
        missing_from_zip = sorted(manifest_names - zip_payload_names)
        unsealed_in_zip = sorted(zip_payload_names - manifest_names)
        if missing_from_zip:
            problems.append("manifest entries missing from ZIP: " + ", ".join(missing_from_zip[:20]))
        if unsealed_in_zip:
            problems.append("ZIP entries not sealed by MANIFEST.sha256: " + ", ".join(unsealed_in_zip[:20]))

        for rel, expected in manifest_entries.items():
            if rel not in zip_payload_names:
                continue
            actual = sha256_bytes(zf.read(rel))
            if actual != expected:
                problems.append(f"{rel}: sha256 mismatch manifest={expected} actual={actual}")

        # Only accepted-candidate archives need the heavier canonical-byte
        # rebuild. Already-failing archives remain rejected by their concrete
        # structural/content problem without spending extra work on a
        # byte-for-byte rebuild that cannot rescue them.
        if not problems:
            problems.extend(_canonical_rebuild_problems(zip_bytes, zf, infos))

    return VerifyResult(
        ok=not problems,
        zip_sha256=zip_hash,
        version=version,
        entries=len(names) if 'names' in locals() else 0,
        manifest_entries=len(manifest_entries) if 'manifest_entries' in locals() else 0,
        problems=problems,
        zip_bytes=zip_bytes if not problems else b"",
    )


def main() -> int:
    ap = argparse.ArgumentParser(description="Verify a deterministic Election Stack release ZIP")
    ap.add_argument("zip", help="release ZIP path")
    ap.add_argument("--quiet", action="store_true", help="only print failures")
    ap.add_argument("--json", action="store_true", help="emit a machine-readable summary")
    args = ap.parse_args()

    result = verify_zip(args.zip)
    if args.json:
        print(json.dumps({
            "ok": result.ok,
            "zip_sha256": result.zip_sha256,
            "version": result.version,
            "entries": result.entries,
            "manifest_entries": result.manifest_entries,
            "problems": result.problems,
        }, sort_keys=True))
        return 0 if result.ok else 2

    if result.ok:
        if not args.quiet:
            print(
                "PASS: release ZIP verified "
                f"(version={result.version}, entries={result.entries}, "
                f"manifest_entries={result.manifest_entries}, sha256={result.zip_sha256})"
            )
        return 0

    print("FAIL: release ZIP verification failed", file=sys.stderr)
    for problem in result.problems[:100]:
        print(f"  - {problem}", file=sys.stderr)
    if len(result.problems) > 100:
        print(f"  ... {len(result.problems) - 100} more", file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
