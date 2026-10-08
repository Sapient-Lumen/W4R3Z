from __future__ import annotations

import importlib

import pytest

from micromax import MicromaxError, VM


def test_vm_reports_loaded_stdlib_health() -> None:
    vm = VM()

    assert vm.stdlib_loaded is True
    assert vm.stdlib_error is None
    assert vm.startup_diagnostics == []
    assert vm.find_word("finally") is not None
    assert vm.find_word("2drop") is not None
    assert vm.stdlib_health() == {
        "state": "loaded",
        "resource": "micromax/stdlib/core.mx",
        "loaded": True,
        "source": "<stdlib/core.mx>",
        "error": None,
    }


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
    vm_mod = importlib.import_module("micromax.vm")

    def missing_files(package: str) -> object:
        raise FileNotFoundError(f"missing package resources for {package}")

    monkeypatch.setattr(vm_mod.importlib_resources, "files", missing_files)

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
    vm_mod = importlib.import_module("micromax.vm")

    def missing_files(package: str) -> object:
        raise FileNotFoundError(f"missing package resources for {package}")

    monkeypatch.setattr(vm_mod.importlib_resources, "files", missing_files)

    with pytest.raises(MicromaxError, match="Micromax stdlib resource missing"):
        VM(strict_stdlib=True)
