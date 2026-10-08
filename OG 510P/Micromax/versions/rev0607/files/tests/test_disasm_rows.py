from __future__ import annotations

from micromax import VM


def test_disasm_rows_returns_structure_for_compiled_code() -> None:
    vm = VM()
    vm.eval(': add1 ( n -- n ) 1 + ;')
    vm.eval("' add1 compile disasm-rows")
    rows = vm.pop_list()
    assert rows, 'expected non-empty disassembly rows'
    pc0, op0, arg0, span0 = rows[0]
    assert isinstance(pc0, int)
    assert isinstance(op0, str)
    # Arg is 0 or a const value.
    assert span0 == 0 or (isinstance(span0, list) and len(span0) == 3)


def test_disasm_rows_returns_0_for_uncompiled_or_primitive() -> None:
    vm = VM()
    vm.eval("' + disasm-rows")
    assert vm.pop() == 0
