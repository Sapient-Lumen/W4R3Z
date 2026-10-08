from micromax import VM, MicromaxError


def test_smoke_arith_and_definitions(capsys):
    vm = VM()
    vm.eval("1 2 + . cr")
    vm.eval(": square dup * ;")
    vm.eval("7 square . cr")
    out = capsys.readouterr().out
    assert "3" in out
    assert "49" in out


def test_quotation_call(capsys):
    vm = VM()
    vm.eval("[ 10 1 - ] call . cr")
    out = capsys.readouterr().out
    assert "9" in out


def test_runtime_if(capsys):
    vm = VM()
    vm.eval('1 [ "yes" . ] [ "no" . ] if cr')
    vm.eval('0 [ "yes" . ] [ "no" . ] if cr')
    out = capsys.readouterr().out
    assert "yes" in out
    assert "no" in out


def test_variable_and_constant():
    vm = VM()
    vm.eval("123 constant magic")
    vm.eval("magic")
    assert vm.pop_int() == 123

    vm.eval("variable x")
    vm.eval("999 x !")
    vm.eval("x @")
    assert vm.pop_int() == 999


def test_catch_restores_stack_and_sets_last_error(capsys):
    vm = VM()
    # leave some stack state, then error inside catch
    vm.eval("1 2 [ drop drop drop ] catch")
    ior = vm.pop_int()
    assert ior != 0
    assert vm.stack == [1, 2]

    vm.eval("last-error.")
    out = capsys.readouterr().out
    assert "Stack underflow" in out


def test_wordlists_search_order_isolation():
    vm = VM()
    vm.eval("wordlist")
    wid = vm.pop_int()

    # Define a word in plugin wordlist only.
    vm.stack.append(wid)
    vm.eval("set-current")
    vm.eval(": hello 42 ;")

    # Reset current and search order to forth only; hello should not exist.
    vm.eval("only")
    try:
        vm.eval("hello")
        assert False, "expected unknown word"
    except MicromaxError:
        pass

    # Add plugin wordlist to search order: wid forth 2 set-order  (wid searched first)
    vm.stack.extend([vm.forth_wid, wid, 2])  # wid_n ... wid_1 n => forth wid 2 means wid searched first
    vm.eval("set-order")
    vm.eval("hello")
    assert vm.pop_int() == 42


def test_hostcall_allowlist():
    vm = VM()

    def add1(v: VM) -> None:
        n = v.pop_int()
        v.stack.append(n + 1)

    vm.register_host("add1", add1)
    vm.eval('10 "add1" hostcall')
    assert vm.pop_int() == 11


def test_step_budget_prevents_infinite_loop():
    vm = VM()
    vm.eval("[ 10 [ [ 1 ] [ ] while ] with-budget ] catch")
    ior = vm.pop_int()
    assert ior == -100
    # last error should mention budget
    vm.eval("last-error")
    s = vm.pop_str()
    assert "budget" in s.lower()


def test_tick_execute_and_defer():
    vm = VM()
    vm.eval(": inc 1 + ;")
    vm.eval("41 ' inc execute")
    assert vm.pop_int() == 42

    # deferred words
    vm.eval("defer hook")
    vm.eval("' inc is hook")
    vm.eval("41 hook")
    assert vm.pop_int() == 42

    # defer@ / defer!
    vm.eval("' hook defer@")  # returns xt
    xt = vm.pop()  # Word
    assert getattr(xt, "name", "") == "inc"

    vm.eval(": dec 1 - ;")
    vm.eval("' dec ' hook defer!")  # set hook to dec
    vm.eval("41 hook")
    assert vm.pop_int() == 40
