from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys

import pytest

from micromax import MicromaxError, VM
from micromax.vm import (
    Bytecode,
    Instruction,
    PORTABLE_INT_MAX,
    PORTABLE_INT_MIN,
    Span,
)


ROOT = Path(__file__).resolve().parents[1]


def test_signed_i64_literal_boundaries_and_unicode_decimal_digits() -> None:
    vm = VM(load_stdlib=False)

    vm.eval(
        f"{PORTABLE_INT_MIN} {PORTABLE_INT_MAX} ١٢٣",
        filename="<i64-literals>",
    )

    assert vm.stack == [PORTABLE_INT_MIN, PORTABLE_INT_MAX, 123]


@pytest.mark.parametrize(
    "literal",
    [
        str(PORTABLE_INT_MAX + 1),
        str(PORTABLE_INT_MIN - 1),
        "9" * 20_000,
    ],
)
def test_out_of_range_literals_fail_before_execution_with_a_source_span(
    literal: str,
) -> None:
    vm = VM(load_stdlib=False)

    with pytest.raises(
        MicromaxError,
        match=r"integer literal: integer out of range \(signed 64-bit\)",
    ) as excinfo:
        vm.eval(literal, filename="risk.mx")

    assert excinfo.value.span == Span(filename="risk.mx", line=1, col=1)
    assert vm.stack == []


def test_huge_leading_zero_literal_is_parsed_without_materializing_a_bigint() -> None:
    vm = VM(load_stdlib=False)

    vm.eval(("0" * 20_000) + "42", filename="<leading-zero-literal>")

    assert vm.stack == [42]


@pytest.mark.parametrize(
    ("source", "message", "expected_stack"),
    [
        (
            f"{PORTABLE_INT_MAX} 1 +",
            r"integer overflow: \+ exceeds signed 64-bit range",
            [PORTABLE_INT_MAX, 1],
        ),
        (
            f"{PORTABLE_INT_MIN} 1 -",
            r"integer overflow: - exceeds signed 64-bit range",
            [PORTABLE_INT_MIN, 1],
        ),
        (
            "4294967296 4294967296 *",
            r"integer overflow: \* exceeds signed 64-bit range",
            [4294967296, 4294967296],
        ),
        (
            f"{PORTABLE_INT_MIN} -1 /",
            r"integer overflow: / exceeds signed 64-bit range",
            [PORTABLE_INT_MIN, -1],
        ),
        ("7 0 /", "Division by zero", [7, 0]),
        ("7 0 mod", "Division by zero", [7, 0]),
    ],
)
def test_arithmetic_denials_are_transactional(
    source: str,
    message: str,
    expected_stack: list[int],
) -> None:
    vm = VM(load_stdlib=False)

    with pytest.raises(MicromaxError, match=message):
        vm.eval(source, filename="<checked-arithmetic>")

    assert vm.stack == expected_stack

    # One failed primitive does not poison the shared VM.
    vm.stack.clear()
    vm.eval("20 22 +", filename="<after-checked-arithmetic>")
    assert vm.stack == [42]


def test_repeated_squaring_is_stopped_at_the_first_i64_overflow() -> None:
    vm = VM(load_stdlib=False)

    with pytest.raises(MicromaxError, match=r"integer overflow: \*"):
        vm.eval("2 " + ("dup * " * 32), filename="<amplify-int>")

    assert vm.stack == [4294967296, 4294967296]


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        ("-3 2 /", -2),
        ("3 -2 /", -2),
        ("-3 2 mod", 1),
        ("3 -2 mod", -1),
        (f"{PORTABLE_INT_MIN} -1 mod", 0),
    ],
)
def test_signed_division_and_remainder_keep_micromax_floor_semantics(
    source: str,
    expected: int,
) -> None:
    vm = VM(load_stdlib=False)

    vm.eval(source, filename="<floor-division>")

    assert vm.stack == [expected]


def test_compiled_arithmetic_uses_the_same_checked_primitive() -> None:
    vm = VM(load_stdlib=False)
    vm.eval(
        f"[ {PORTABLE_INT_MAX} 1 + ] compile",
        filename="<compiled-overflow>",
    )

    with pytest.raises(MicromaxError, match=r"integer overflow: \+"):
        vm.eval("call", filename="<compiled-overflow-call>")

    assert vm.stack == [PORTABLE_INT_MAX, 1]


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        (" +9_223_372_036_854_775_807 ", PORTABLE_INT_MAX),
        (" -9_223_372_036_854_775_808\n", PORTABLE_INT_MIN),
        ("٠_٠_٤٢", 42),
        (("0" * 20_000) + "7", 7),
    ],
)
def test_to_int_parses_only_bounded_values_without_consuming_the_source(
    text: str,
    expected: int,
) -> None:
    vm = VM(load_stdlib=False)
    vm.stack.append(text)

    vm.eval("to-int", filename="<bounded-to-int>")

    assert vm.stack == [expected]


@pytest.mark.parametrize(
    ("value", "message"),
    [
        (str(PORTABLE_INT_MAX + 1), r"to-int: integer out of range"),
        (str(PORTABLE_INT_MIN - 1), r"to-int: integer out of range"),
        ("1__0", r"to-int: invalid integer"),
        ("_10", r"to-int: invalid integer"),
        ("10_", r"to-int: invalid integer"),
        ([], r"to-int: expected int or str"),
    ],
)
def test_to_int_denial_preserves_the_original_value(
    value: object,
    message: str,
) -> None:
    vm = VM(load_stdlib=False)
    vm.stack.append(value)

    with pytest.raises(MicromaxError, match=message):
        vm.eval("to-int", filename="<to-int-denial>")

    assert vm.stack == [value]
    assert vm.stack[0] is value


def test_host_injected_bigint_is_rejected_without_decimal_rendering_or_consumption() -> None:
    vm = VM(load_stdlib=False)
    giant = 1 << 100_000
    vm.stack.append(giant)

    with pytest.raises(MicromaxError, match=r"integer out of range \(signed 64-bit\)"):
        vm.pop_int()

    assert vm.stack == [giant]
    assert vm.stack[0] is giant

    vm.stack.clear()
    vm.stack.append(giant)
    vm.eval("int?", filename="<host-bigint-predicate>")
    assert vm.stack == [0]


def test_bytecode_json_rejects_out_of_range_integers_before_python_bigint_decode() -> None:
    raw = json.dumps(
        {
            "magic": "micromax-bc",
            "ver": 1,
            "consts": [],
            "instrs": [],
        },
        separators=(",", ":"),
    )
    raw = raw.replace('"consts":[]', f'"consts":[["i",{"9" * 20_000}]]')

    with pytest.raises(MicromaxError, match=r"bytecode-from-json: integer out of range"):
        VM.bytecode_from_json(raw)


def test_bytecode_load_failure_preserves_its_source_string() -> None:
    vm = VM(load_stdlib=False)
    raw = (
        '{"magic":"micromax-bc","ver":1,'
        f'"consts":[["i",{PORTABLE_INT_MAX + 1}]],"instrs":[]}}'
    )
    vm.stack.append(raw)

    with pytest.raises(MicromaxError, match=r"bytecode-from-json: integer out of range"):
        vm.eval("bytecode-load-json", filename="<bytecode-denial>")

    assert vm.stack == [raw]


def test_bytecode_export_rejects_a_host_injected_nonportable_constant() -> None:
    vm = VM(load_stdlib=False)
    span = Span(filename="<host-bytecode>", line=1, col=1)
    bytecode = Bytecode(
        consts=[1 << 100_000],
        instrs=[Instruction(op="PUSH", arg=0, span=span)],
    )

    with pytest.raises(MicromaxError, match=r"bytecode: integer out of range"):
        vm.bytecode_to_json(bytecode)

    quotation = vm.quote_from_bytecode_json(
        '{"magic":"micromax-bc","ver":1,"consts":[["i",1]],'
        '"instrs":[["PUSH",0,["<loaded>",1,1]]]}'
    )
    assert quotation.code.bytecode is not None
    quotation.code.bytecode.consts[0] = 1 << 100_000
    vm.stack.append(quotation)
    with pytest.raises(MicromaxError, match=r"bytecode: integer out of range"):
        vm.eval("call", filename="<mutated-bytecode>")


def test_checked_integer_path_survives_tight_address_space_headroom() -> None:
    if sys.platform != "linux" or not Path("/proc/self/statm").exists():
        pytest.skip("requires Linux RLIMIT_AS and /proc")

    script = r'''
import json
import os
import resource
from micromax import VM

vm = VM(load_stdlib=False)
pages = int(open("/proc/self/statm", encoding="ascii").read().split()[0])
current_vms = pages * os.sysconf("SC_PAGE_SIZE")
soft, hard = resource.getrlimit(resource.RLIMIT_AS)
ceiling = current_vms + 16 * 1024 * 1024
if hard not in (-1, resource.RLIM_INFINITY):
    ceiling = min(ceiling, hard)
resource.setrlimit(resource.RLIMIT_AS, (ceiling, hard))
try:
    vm.eval("2 " + ("dup * " * 32), filename="<rlimit-int-probe>")
except Exception as exc:
    print(json.dumps({
        "type": type(exc).__name__,
        "message": str(exc),
        "stack": vm.stack,
    }, sort_keys=True))
else:
    print(json.dumps({"type": "none", "message": "", "stack": vm.stack}))
'''
    env = dict(os.environ)
    env["PYTHONPATH"] = str(ROOT / "src")
    proc = subprocess.run(
        [sys.executable, "-c", script],
        cwd=ROOT,
        env=env,
        text=True,
        capture_output=True,
        timeout=10,
        check=False,
    )

    assert proc.returncode == 0, proc.stderr
    assert json.loads(proc.stdout) == {
        "message": "integer overflow: * exceeds signed 64-bit range",
        "stack": [4294967296, 4294967296],
        "type": "MicromaxError",
    }


def test_host_boolean_is_not_a_portable_integer() -> None:
    vm = VM(load_stdlib=False)
    vm.stack.append(True)

    with pytest.raises(MicromaxError, match=r"Expected int, got bool"):
        vm.pop_int()

    assert vm.stack == [True]
    vm.eval("int?", filename="<host-bool-predicate>")
    assert vm.stack == [0]


@pytest.mark.parametrize(
    "raw",
    [
        '{"magic":"micromax-bc","ver":true,"consts":[],"instrs":[]}',
        '{"magic":"micromax-bc","ver":1,"consts":[["i",true]],"instrs":[]}',
    ],
)
def test_bytecode_json_does_not_treat_json_booleans_as_integers(raw: str) -> None:
    with pytest.raises(MicromaxError, match=r"bytecode-from-json: expected int, got bool"):
        VM.bytecode_from_json(raw)


def test_bytecode_export_checks_operands_and_source_coordinates() -> None:
    vm = VM(load_stdlib=False)
    normal_span = Span(filename="<host-bytecode>", line=1, col=1)
    giant = 1 << 100_000

    with pytest.raises(MicromaxError, match=r"bytecode operand: integer out of range"):
        vm.bytecode_to_json(
            Bytecode(
                consts=[1],
                instrs=[Instruction(op="PUSH", arg=giant, span=normal_span)],
            )
        )

    with pytest.raises(MicromaxError, match=r"bytecode span line: integer out of range"):
        vm.bytecode_to_json(
            Bytecode(
                consts=[1],
                instrs=[
                    Instruction(
                        op="PUSH",
                        arg=0,
                        span=Span(filename="<host-bytecode>", line=giant, col=1),
                    )
                ],
            )
        )


def test_mutated_bytecode_operand_is_rechecked_at_dispatch() -> None:
    vm = VM(load_stdlib=False)
    quotation = vm.quote_from_bytecode_json(
        '{"magic":"micromax-bc","ver":1,"consts":[["i",1]],'
        '"instrs":[["PUSH",0,["<loaded>",1,1]]]}'
    )
    assert quotation.code.bytecode is not None
    quotation.code.bytecode.instrs[0].arg = 1 << 100_000
    vm.stack.append(quotation)

    with pytest.raises(MicromaxError, match=r"bytecode operand: integer out of range"):
        vm.eval("call", filename="<mutated-bytecode-operand>")

    assert vm.stack == []


def test_bytecode_constant_pool_indexes_are_checked_at_import_and_export() -> None:
    vm = VM(load_stdlib=False)
    span = Span(filename="<const-index>", line=1, col=1)

    for operand in (-1, 1):
        raw = json.dumps(
            {
                "magic": "micromax-bc",
                "ver": 1,
                "consts": [["i", 42]],
                "instrs": [["PUSH", operand, ["<loaded>", 1, 1]]],
            },
            separators=(",", ":"),
        )
        with pytest.raises(
            MicromaxError,
            match=r"bytecode-from-json: PUSH constant index out of range",
        ):
            VM.bytecode_from_json(raw)

    with pytest.raises(
        MicromaxError,
        match=r"bytecode operand: PUSH constant index out of range",
    ):
        vm.bytecode_to_json(
            Bytecode(
                consts=[42],
                instrs=[Instruction(op="PUSH", arg=-1, span=span)],
            )
        )


def test_mutated_negative_constant_index_has_no_python_list_semantics() -> None:
    vm = VM(load_stdlib=False)
    quotation = vm.quote_from_bytecode_json(
        '{"magic":"micromax-bc","ver":1,"consts":[["i",42]],'
        '"instrs":[["PUSH",0,["<loaded>",1,1]]]}'
    )
    assert quotation.code.bytecode is not None
    quotation.code.bytecode.instrs[0].arg = -1
    vm.stack.append(quotation)

    with pytest.raises(
        MicromaxError,
        match=r"bytecode operand: PUSH constant index out of range",
    ):
        vm.eval("call", filename="<mutated-negative-index>")

    assert vm.stack == []
