from __future__ import annotations

from collections import Counter

from micromax import VM
from micromax.core_registry import CORE_PRIMITIVE_REGISTRY, core_primitive_names


def test_core_primitive_registry_names_are_unique() -> None:
    counts = Counter(core_primitive_names())
    assert [name for name, count in counts.items() if count != 1] == []


def test_core_primitive_registry_entries_are_defined() -> None:
    vm = VM(load_stdlib=False)
    defined = set(vm.wordlists[vm.forth_wid].keys())
    assert set(core_primitive_names()).issubset(defined)
    assert len(CORE_PRIMITIVE_REGISTRY) == len(core_primitive_names())


def test_see_primitive_keeps_final_documentation_without_duplicate_registration() -> None:
    docs = {entry.name: entry.doc for entry in CORE_PRIMITIVE_REGISTRY}
    assert docs["see"] == "( -- ) parse next name; print definition"

    vm = VM(load_stdlib=False)
    see = vm.find_word("see")
    assert see is not None
    assert see.doc == docs["see"]
