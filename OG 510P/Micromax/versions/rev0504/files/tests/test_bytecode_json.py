from __future__ import annotations

import json

import pytest

from micromax import VM


def test_bytecode_json_roundtrip_and_late_binding() -> None:
    vm = VM()
    vm.eval(": foo 1 ;")

    # compile and serialize
    vm.eval("[ foo ] compile bytecode-json")
    s1 = vm.pop_str()

    # deterministic
    vm.stack.append(vm.find_word("foo"))  # just to ensure stack isn't empty later
    vm.stack.pop()
    vm.eval("[ foo ] compile bytecode-json")
    s2 = vm.pop_str()
    assert s1 == s2

    obj = json.loads(s1)
    assert obj["magic"] == "micromax-bc"
    assert obj["ver"] == 1

    # redefine after serialization: loaded bytecode must see the new definition
    vm.eval(": foo 2 ;")

    vm.stack.append(s1)
    vm.eval("bytecode-load-json call")
    assert vm.pop_int() == 2


def test_bytecode_json_includes_nested_quotations() -> None:
    vm = VM()
    vm.eval("[ [ 1 ] call ] compile bytecode-json")
    s = vm.pop_str()
    # nested quote constant tag is "q"
    assert '"q"' in s
