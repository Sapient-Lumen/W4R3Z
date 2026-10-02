#!/usr/bin/env python3
"""Generate and strictly verify IoTox's deterministic SPDX 2.3 SBOM."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import re
import sys
import tempfile
import uuid


LOCK_KEYS = {
    "IOTOX_C_TOXCORE_VERSION",
    "IOTOX_C_TOXCORE_URL",
    "IOTOX_C_TOXCORE_SHA256",
    "IOTOX_C_TOXCORE_LICENSE",
    "IOTOX_CMP_COMMIT",
    "IOTOX_CMP_URL",
    "IOTOX_CMP_SHA256",
    "IOTOX_CMP_LICENSE",
    "IOTOX_LIBSODIUM_VERSION",
    "IOTOX_LIBSODIUM_URL",
    "IOTOX_LIBSODIUM_SHA256",
    "IOTOX_LIBSODIUM_LICENSE",
    "IOTOX_ARGON2_VERSION",
    "IOTOX_ARGON2_URL",
    "IOTOX_ARGON2_SHA256",
    "IOTOX_ARGON2_LICENSE",
    "IOTOX_EFF_WORDLIST_VERSION",
    "IOTOX_EFF_WORDLIST_URL",
    "IOTOX_EFF_WORDLIST_SHA256",
    "IOTOX_EFF_WORDLIST_LICENSE",
}
LOCK_RECORD = re.compile(r"^([A-Z0-9_]+)='([^']*)'$", re.ASCII)
VERSION_RECORD = re.compile(
    r"^project\(IoTox VERSION ([0-9]+\.[0-9]+\.[0-9]+) LANGUAGES C CXX\)$",
    re.MULTILINE,
)
REVISION_RECORD = re.compile(r"^rev[0-9]{4}$", re.ASCII)
COMMIT_RECORD = re.compile(r"^[0-9a-f]{40,64}$", re.ASCII)
SHA256_RECORD = re.compile(r"^[0-9a-f]{64}$", re.ASCII)
SPDX_NAMESPACE = uuid.UUID("ec76272e-7e63-5ff4-bcb7-37dfe0f69c48")


class SbomError(RuntimeError):
    pass


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_lock(root: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    for line in (root / "dependencies.lock").read_text(encoding="utf-8").splitlines():
        match = LOCK_RECORD.fullmatch(line)
        if match and match.group(1) in LOCK_KEYS:
            if match.group(1) in values:
                raise SbomError(f"duplicate dependency lock key: {match.group(1)}")
            values[match.group(1)] = match.group(2)
    missing = sorted(LOCK_KEYS - values.keys())
    if missing:
        raise SbomError("dependency lock is missing: " + ", ".join(missing))
    for key, value in values.items():
        if key.endswith("_SHA256") and not SHA256_RECORD.fullmatch(value):
            raise SbomError(f"dependency lock has invalid SHA-256: {key}")
    return values


def project_identity(root: Path) -> tuple[str, str]:
    cmake = (root / "CMakeLists.txt").read_text(encoding="utf-8")
    version = VERSION_RECORD.search(cmake)
    if version is None:
        raise SbomError("unable to find canonical IoTox version")
    revision = (root / "REVISION").read_text(encoding="ascii").strip()
    if not REVISION_RECORD.fullmatch(revision):
        raise SbomError("IoTox revision is not canonical")
    return version.group(1), revision


def canonical_commit(value: str | None) -> str:
    if value is None or value == "":
        return "NOASSERTION"
    lowered = value.lower()
    if not COMMIT_RECORD.fullmatch(lowered):
        raise SbomError("source commit must be one complete hexadecimal object id")
    return lowered


def canonical_epoch(value: int | str | None) -> int:
    if value is None or value == "":
        value = os.environ.get("SOURCE_DATE_EPOCH", "1")
    try:
        epoch = int(value)
    except (TypeError, ValueError) as error:
        raise SbomError("source date epoch must be an integer") from error
    if epoch < 0 or epoch > 253402300799:
        raise SbomError("source date epoch is outside the UTC timestamp range")
    return epoch


def package(
    spdx_id: str,
    name: str,
    version: str,
    download: str,
    license_expression: str,
    checksum: str,
    purpose: str,
    purl: str,
    comment: str | None = None,
) -> dict[str, object]:
    record: dict[str, object] = {
        "SPDXID": spdx_id,
        "name": name,
        "versionInfo": version,
        "downloadLocation": download,
        "filesAnalyzed": False,
        "licenseConcluded": license_expression,
        "licenseDeclared": license_expression,
        "copyrightText": "NOASSERTION",
        "checksums": [{"algorithm": "SHA256", "checksumValue": checksum}],
        "primaryPackagePurpose": purpose,
        "externalRefs": [
            {
                "referenceCategory": "PACKAGE-MANAGER",
                "referenceType": "purl",
                "referenceLocator": purl,
            }
        ],
    }
    if comment is not None:
        record["comment"] = comment
    return record


def build_document(
    root: Path,
    binary: Path,
    source_commit: str | None,
    source_date_epoch: int | str | None,
) -> dict[str, object]:
    if not binary.is_file() or binary.is_symlink():
        raise SbomError("SBOM binary must be one regular non-symlink file")
    version, revision = project_identity(root)
    locked = load_lock(root)
    commit = canonical_commit(source_commit)
    epoch = canonical_epoch(source_date_epoch)
    binary_sha256 = sha256_file(binary)
    qualified_version = f"{version}-{revision}"
    namespace_name = "|".join(
        ("IoTox", qualified_version, binary_sha256, commit)
    )
    namespace = f"urn:uuid:{uuid.uuid5(SPDX_NAMESPACE, namespace_name)}"
    created = dt.datetime.fromtimestamp(epoch, tz=dt.timezone.utc).strftime(
        "%Y-%m-%dT%H:%M:%SZ"
    )

    packages = [
        package(
            "SPDXRef-Package-IoTox",
            "IoTox",
            qualified_version,
            "NOASSERTION",
            "MIT",
            binary_sha256,
            "APPLICATION",
            f"pkg:generic/iotox@{qualified_version}",
            "sourceCommit=" + commit,
        ),
        package(
            "SPDXRef-Package-c-toxcore",
            "c-toxcore",
            locked["IOTOX_C_TOXCORE_VERSION"],
            locked["IOTOX_C_TOXCORE_URL"],
            locked["IOTOX_C_TOXCORE_LICENSE"],
            locked["IOTOX_C_TOXCORE_SHA256"],
            "LIBRARY",
            "pkg:github/TokTok/c-toxcore@" + locked["IOTOX_C_TOXCORE_VERSION"],
            "The source-linked product carries the iotox-file-rr1 scheduler and tcp-connect120 slow-overlay establishment patches.",
        ),
        package(
            "SPDXRef-Package-cmp",
            "cmp",
            locked["IOTOX_CMP_COMMIT"],
            locked["IOTOX_CMP_URL"],
            locked["IOTOX_CMP_LICENSE"],
            locked["IOTOX_CMP_SHA256"],
            "LIBRARY",
            "pkg:github/TokTok/cmp@" + locked["IOTOX_CMP_COMMIT"],
        ),
        package(
            "SPDXRef-Package-libsodium",
            "libsodium",
            locked["IOTOX_LIBSODIUM_VERSION"],
            locked["IOTOX_LIBSODIUM_URL"],
            locked["IOTOX_LIBSODIUM_LICENSE"],
            locked["IOTOX_LIBSODIUM_SHA256"],
            "LIBRARY",
            "pkg:generic/libsodium@" + locked["IOTOX_LIBSODIUM_VERSION"],
        ),
        package(
            "SPDXRef-Package-argon2",
            "Argon2 reference implementation",
            locked["IOTOX_ARGON2_VERSION"],
            locked["IOTOX_ARGON2_URL"],
            locked["IOTOX_ARGON2_LICENSE"],
            locked["IOTOX_ARGON2_SHA256"],
            "LIBRARY",
            "pkg:github/P-H-C/phc-winner-argon2@" + locked["IOTOX_ARGON2_VERSION"],
        ),
        package(
            "SPDXRef-Package-eff-wordlist",
            "EFF large word list",
            locked["IOTOX_EFF_WORDLIST_VERSION"],
            locked["IOTOX_EFF_WORDLIST_URL"],
            locked["IOTOX_EFF_WORDLIST_LICENSE"],
            locked["IOTOX_EFF_WORDLIST_SHA256"],
            "DATA",
            "pkg:generic/eff-large-word-list@"
            + locked["IOTOX_EFF_WORDLIST_VERSION"],
        ),
    ]
    return {
        "spdxVersion": "SPDX-2.3",
        "dataLicense": "CC0-1.0",
        "SPDXID": "SPDXRef-DOCUMENT",
        "name": f"IoTox-{qualified_version}-source-component-sbom",
        "documentNamespace": namespace,
        "creationInfo": {
            "created": created,
            "creators": ["Tool: iotox-generate-sbom/1"],
            "licenseListVersion": "3.27",
        },
        "documentDescribes": ["SPDXRef-Package-IoTox"],
        "comment": (
            "Deterministic source-component and embedded-data inventory for the "
            "source-linked IoTox executable. The host operating-system runtime "
            "closure is deployment-specific and intentionally outside this document."
        ),
        "packages": packages,
        "files": [
            {
                "SPDXID": "SPDXRef-File-iotox",
                "fileName": "./iotox",
                "checksums": [
                    {"algorithm": "SHA256", "checksumValue": binary_sha256}
                ],
                "licenseConcluded": "NOASSERTION",
                "copyrightText": "NOASSERTION",
                "fileTypes": ["BINARY"],
            }
        ],
        "relationships": [
            {
                "spdxElementId": "SPDXRef-DOCUMENT",
                "relationshipType": "DESCRIBES",
                "relatedSpdxElement": "SPDXRef-Package-IoTox",
            },
            {
                "spdxElementId": "SPDXRef-Package-IoTox",
                "relationshipType": "CONTAINS",
                "relatedSpdxElement": "SPDXRef-File-iotox",
            },
            *[
                {
                    "spdxElementId": "SPDXRef-Package-IoTox",
                    "relationshipType": "DEPENDS_ON",
                    "relatedSpdxElement": dependency,
                }
                for dependency in (
                    "SPDXRef-Package-c-toxcore",
                    "SPDXRef-Package-libsodium",
                    "SPDXRef-Package-argon2",
                    "SPDXRef-Package-eff-wordlist",
                )
            ],
            {
                "spdxElementId": "SPDXRef-Package-c-toxcore",
                "relationshipType": "CONTAINS",
                "relatedSpdxElement": "SPDXRef-Package-cmp",
            },
        ],
    }


def write_document(document: dict[str, object], output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    payload = (json.dumps(document, indent=2, sort_keys=True) + "\n").encode("utf-8")
    temporary = output.with_name(output.name + f".part.{os.getpid()}")
    try:
        with temporary.open("xb") as target:
            target.write(payload)
            target.flush()
            os.fsync(target.fileno())
        os.chmod(temporary, 0o644)
        os.replace(temporary, output)
    finally:
        try:
            temporary.unlink()
        except FileNotFoundError:
            pass


def verify_document(root: Path, binary: Path, sbom: Path) -> dict[str, object]:
    try:
        document = json.loads(sbom.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise SbomError(f"unable to read canonical SPDX JSON: {error}") from error
    if not isinstance(document, dict):
        raise SbomError("SPDX document root must be an object")
    if document.get("spdxVersion") != "SPDX-2.3":
        raise SbomError("SPDX version is not 2.3")
    if document.get("dataLicense") != "CC0-1.0":
        raise SbomError("SPDX document data license is not CC0-1.0")
    creation = document.get("creationInfo")
    if not isinstance(creation, dict) or creation.get("creators") != [
        "Tool: iotox-generate-sbom/1"
    ]:
        raise SbomError("SPDX creator is not canonical")

    packages = document.get("packages")
    if not isinstance(packages, list):
        raise SbomError("SPDX package inventory is missing")
    by_id = {
        item.get("SPDXID"): item
        for item in packages
        if isinstance(item, dict) and isinstance(item.get("SPDXID"), str)
    }
    expected_ids = {
        "SPDXRef-Package-IoTox",
        "SPDXRef-Package-c-toxcore",
        "SPDXRef-Package-cmp",
        "SPDXRef-Package-libsodium",
        "SPDXRef-Package-argon2",
        "SPDXRef-Package-eff-wordlist",
    }
    if set(by_id) != expected_ids or len(packages) != len(expected_ids):
        raise SbomError("SPDX package inventory is incomplete or contains aliases")

    binary_sha256 = sha256_file(binary)
    checksums = by_id["SPDXRef-Package-IoTox"].get("checksums")
    if checksums != [{"algorithm": "SHA256", "checksumValue": binary_sha256}]:
        raise SbomError("IoTox package checksum does not bind the executable")
    files = document.get("files")
    if files != [
        {
            "SPDXID": "SPDXRef-File-iotox",
            "fileName": "./iotox",
            "checksums": [{"algorithm": "SHA256", "checksumValue": binary_sha256}],
            "licenseConcluded": "NOASSERTION",
            "copyrightText": "NOASSERTION",
            "fileTypes": ["BINARY"],
        }
    ]:
        raise SbomError("SPDX file inventory does not bind exactly one IoTox executable")

    locked = load_lock(root)
    expected = {
        "SPDXRef-Package-c-toxcore": (
            locked["IOTOX_C_TOXCORE_VERSION"],
            locked["IOTOX_C_TOXCORE_URL"],
            locked["IOTOX_C_TOXCORE_LICENSE"],
            locked["IOTOX_C_TOXCORE_SHA256"],
        ),
        "SPDXRef-Package-cmp": (
            locked["IOTOX_CMP_COMMIT"],
            locked["IOTOX_CMP_URL"],
            locked["IOTOX_CMP_LICENSE"],
            locked["IOTOX_CMP_SHA256"],
        ),
        "SPDXRef-Package-libsodium": (
            locked["IOTOX_LIBSODIUM_VERSION"],
            locked["IOTOX_LIBSODIUM_URL"],
            locked["IOTOX_LIBSODIUM_LICENSE"],
            locked["IOTOX_LIBSODIUM_SHA256"],
        ),
        "SPDXRef-Package-argon2": (
            locked["IOTOX_ARGON2_VERSION"],
            locked["IOTOX_ARGON2_URL"],
            locked["IOTOX_ARGON2_LICENSE"],
            locked["IOTOX_ARGON2_SHA256"],
        ),
        "SPDXRef-Package-eff-wordlist": (
            locked["IOTOX_EFF_WORDLIST_VERSION"],
            locked["IOTOX_EFF_WORDLIST_URL"],
            locked["IOTOX_EFF_WORDLIST_LICENSE"],
            locked["IOTOX_EFF_WORDLIST_SHA256"],
        ),
    }
    for spdx_id, (version, download, license_expression, checksum) in expected.items():
        candidate = by_id[spdx_id]
        if (
            candidate.get("versionInfo") != version
            or candidate.get("downloadLocation") != download
            or candidate.get("licenseDeclared") != license_expression
            or candidate.get("licenseConcluded") != license_expression
            or candidate.get("checksums")
            != [{"algorithm": "SHA256", "checksumValue": checksum}]
        ):
            raise SbomError(f"SPDX component drift: {spdx_id}")

    expected_relationships = {
        (item["spdxElementId"], item["relationshipType"], item["relatedSpdxElement"])
        for item in build_document(root, binary, None, 1)["relationships"]
    }
    relationships = document.get("relationships")
    if not isinstance(relationships, list):
        raise SbomError("SPDX relationships are missing")
    observed_relationships = {
        (item.get("spdxElementId"), item.get("relationshipType"), item.get("relatedSpdxElement"))
        for item in relationships
        if isinstance(item, dict)
    }
    if observed_relationships != expected_relationships or len(relationships) != len(
        expected_relationships
    ):
        raise SbomError("SPDX dependency relationships are incomplete or aliased")
    return document


def self_test() -> None:
    with tempfile.TemporaryDirectory(prefix="iotox-sbom-selftest-") as raw:
        root = Path(raw)
        (root / "CMakeLists.txt").write_text(
            "project(IoTox VERSION 0.48.0 LANGUAGES C CXX)\n", encoding="utf-8"
        )
        (root / "REVISION").write_text("rev0048\n", encoding="ascii")
        lock_values = {
            key: (
                "1" * 64
                if key.endswith("_SHA256")
                else "MIT"
                if key.endswith("_LICENSE")
                else "https://example.invalid/source"
                if key.endswith("_URL")
                else "1.0"
            )
            for key in LOCK_KEYS
        }
        (root / "dependencies.lock").write_text(
            "".join(f"{key}='{lock_values[key]}'\n" for key in sorted(lock_values)),
            encoding="utf-8",
        )
        binary = root / "iotox"
        binary.write_bytes(b"iotox-sbom-fixture\n")
        first = root / "first.json"
        second = root / "second.json"
        document = build_document(root, binary, "a" * 40, 1_700_000_000)
        write_document(document, first)
        write_document(document, second)
        if first.read_bytes() != second.read_bytes():
            raise SbomError("deterministic SPDX rendering changed")
        verify_document(root, binary, first)
        binary.write_bytes(b"changed\n")
        try:
            verify_document(root, binary, first)
        except SbomError:
            pass
        else:
            raise SbomError("binary substitution was not rejected")
    print("iotox SPDX SBOM self-test: PASS")


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("--self-test", action="store_true")
    subcommands = result.add_subparsers(dest="command")
    generate = subcommands.add_parser("generate")
    generate.add_argument("--root", type=Path, required=True)
    generate.add_argument("--binary", type=Path, required=True)
    generate.add_argument("--output", type=Path, required=True)
    generate.add_argument("--source-commit")
    generate.add_argument("--source-date-epoch")
    verify = subcommands.add_parser("verify")
    verify.add_argument("--root", type=Path, required=True)
    verify.add_argument("--binary", type=Path, required=True)
    verify.add_argument("--sbom", type=Path, required=True)
    return result


def main(argv: list[str]) -> int:
    arguments = parser().parse_args(argv)
    try:
        if arguments.self_test:
            self_test()
        elif arguments.command == "generate":
            document = build_document(
                arguments.root.resolve(),
                arguments.binary.resolve(),
                arguments.source_commit,
                arguments.source_date_epoch,
            )
            write_document(document, arguments.output.resolve())
            print(f"spdx-sbom={arguments.output.resolve()}")
        elif arguments.command == "verify":
            document = verify_document(
                arguments.root.resolve(),
                arguments.binary.resolve(),
                arguments.sbom.resolve(),
            )
            print(
                "spdx-sbom=pass "
                f"namespace={document['documentNamespace']} "
                f"packages={len(document['packages'])}"
            )
        else:
            parser().error("choose generate, verify, or --self-test")
    except (OSError, SbomError) as error:
        print(f"SBOM failure: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
