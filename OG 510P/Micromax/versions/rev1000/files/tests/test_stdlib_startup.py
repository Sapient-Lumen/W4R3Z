from __future__ import annotations

import importlib

import pytest

from micromax import MicromaxError, VM
from micromax import stdlib_resource


def test_vm_reports_loaded_stdlib_health() -> None:
    vm = VM()

    assert vm.stdlib_loaded is True
    assert vm.stdlib_error is None
    assert vm.startup_diagnostics == []
    assert vm.find_word("finally") is not None
    assert vm.find_word("2drop") is not None
    health = vm.stdlib_health()
    assert health["state"] == "loaded"
    assert health["resource"] == "micromax/stdlib/core.mx"
    assert health["loaded"] is True
    assert health["source"] == "<stdlib/core.mx>"
    assert health["error"] is None
    contract = health["resource_contract"]
    assert contract["schema"] == "micromax.stdlib-resource.v1"
    assert contract["trust"] == "bundled-package-resource"
    assert contract["authority"] == "package-local; not workspace/plugin filesystem authority"
    assert contract["max_bytes"] == 64 * 1024
    assert contract["bytes"] == 4221
    assert contract["sha256"] == "941bdfa608d6ca546a95966b522d7501be827365b1d1fd8fa654ab08b7f086e1"


def test_vm_can_disable_stdlib_explicitly() -> None:
    vm = VM(load_stdlib=False)

    assert vm.stdlib_loaded is False
    assert vm.find_word("finally") is None
    assert vm.stdlib_health()["state"] == "disabled"
    assert vm.startup_diagnostics == [
        {
            "kind": "stdlib-disabled",
            "resource": "micromax/stdlib/core.mx",
            "message": "Micromax stdlib loading was disabled by the host",
        }
    ]


def test_missing_stdlib_resource_is_observable(monkeypatch: pytest.MonkeyPatch) -> None:
    resource_mod = importlib.import_module("micromax.stdlib_resource")

    def missing_files(package: str) -> object:
        raise FileNotFoundError(f"missing package resources for {package}")

    monkeypatch.setattr(resource_mod.importlib_resources, "files", missing_files)

    vm = VM()

    assert vm.stdlib_loaded is False
    assert vm.find_word("finally") is None
    health = vm.stdlib_health()
    assert health["state"] == "missing"
    assert health["resource"] == "micromax/stdlib/core.mx"
    assert "FileNotFoundError" in str(health["error"])
    assert vm.startup_diagnostics[0]["kind"] == "missing-stdlib"
    assert vm.startup_diagnostics[0]["resource"] == "micromax/stdlib/core.mx"


def test_strict_missing_stdlib_resource_fails_closed(monkeypatch: pytest.MonkeyPatch) -> None:
    resource_mod = importlib.import_module("micromax.stdlib_resource")

    def missing_files(package: str) -> object:
        raise FileNotFoundError(f"missing package resources for {package}")

    monkeypatch.setattr(resource_mod.importlib_resources, "files", missing_files)

    with pytest.raises(MicromaxError, match="Micromax stdlib resource missing"):
        VM(strict_stdlib=True)


def test_stdlib_resource_reader_has_byte_budget() -> None:
    loaded = stdlib_resource.read_stdlib_resource_bounded(max_bytes=5000)

    assert loaded.metadata["bytes"] == len(loaded.text.encode("utf-8"))
    assert loaded.metadata["bytes"] <= loaded.metadata["max_bytes"]
    assert loaded.metadata["trust"] == "bundled-package-resource"


def test_stdlib_resource_reader_rejects_oversize_budget() -> None:
    with pytest.raises(stdlib_resource.StdlibResourceLimitError, match="exceeds stdlib resource budget"):
        stdlib_resource.read_stdlib_resource_bounded(max_bytes=100)
