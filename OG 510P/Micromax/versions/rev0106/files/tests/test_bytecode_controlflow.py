from __future__ import annotations

from micromax import VM
from micromax.vm import ColonWord


def test_tier2_compiles_if_when_while_to_jumps() -> None:
    vm = VM()

    vm.eval(": choose  ( flag -- n )  [ 1 ] [ 2 ] if ;")
    choose = vm.find_word("choose")
    assert isinstance(choose, ColonWord)
    vm.compile_xt(choose)
    assert choose.code.bytecode is not None
    ops = [ins.op for ins in choose.code.bytecode.instrs]
    # Peephole should avoid runtime `if` call.
    assert ops.count("CALL_Q") == 2
    assert "JZ" in ops and "JMP" in ops

    vm.stack.append(0)
    vm.eval("choose")
    assert vm.pop_int() == 2
    vm.stack.append(1)
    vm.eval("choose")
    assert vm.pop_int() == 1

    vm.eval(": maybe ( flag -- ? ) [ 7 ] when ;")
    maybe = vm.find_word("maybe")
    assert isinstance(maybe, ColonWord)
    vm.compile_xt(maybe)
    assert maybe.code.bytecode is not None
    ops2 = [ins.op for ins in maybe.code.bytecode.instrs]
    assert ops2.count("CALL_Q") == 1
    assert "JZ" in ops2 and "JMP" not in ops2

    vm.stack.append(0)
    vm.eval("maybe")
    assert vm.stack == []
    vm.stack.append(1)
    vm.eval("maybe")
    assert vm.pop_int() == 7

    vm.eval(": inc5 ( n -- n ) [ dup 5 < ] [ 1 + ] while ;")
    inc5 = vm.find_word("inc5")
    assert isinstance(inc5, ColonWord)
    vm.compile_xt(inc5)
    assert inc5.code.bytecode is not None
    ops3 = [ins.op for ins in inc5.code.bytecode.instrs]
    assert ops3.count("CALL_Q") == 2
    assert "JZ" in ops3 and "JMP" in ops3

    vm.stack.append(0)
    vm.eval("inc5")
    assert vm.pop_int() == 5
