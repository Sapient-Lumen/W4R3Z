from __future__ import annotations

import io
import json
import os
from pathlib import Path
import subprocess
import sys

import pytest

import micromax_editor.screen_consumer as screen_consumer
from micromax_editor import Editor
from micromax_editor.screen_consumer import (
    ScreenContractError,
    UnsupportedScreenContract,
    main,
    parse_screen_contract_v1,
    read_screen_contract_v1,
    screen_contract_summary,
    screen_contract_text,
    validate_screen_contract_v1,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURE = REPO_ROOT / "tests" / "fixtures" / "screen-v1" / "blank-4x16.json"


def _contract() -> dict[str, object]:
    editor = Editor()
    editor.new_buffer("*scratch*", "")
    return editor.screen_contract(4, 16)


def test_golden_fixture_is_a_real_strict_consumer_input() -> None:
    raw = FIXTURE.read_bytes()
    contract = parse_screen_contract_v1(raw)

    assert contract == _contract()
    assert screen_contract_text(contract).splitlines()[-1] == "ur:1/1 0% normal"
    assert screen_contract_summary(contract) == {
        "schema": "micromax.screen.v1",
        "size": {"lines": 4, "cols": 16},
        "cursor": {"visible": True, "mode": "edit", "y": 0, "x": 0},
        "rows": 4,
        "source_rows": 1,
        "row_kinds": {"infobar": 1, "statusline": 1, "viewport": 2},
        "cues": 0,
        "cue_kinds": {},
    }


def test_consumer_rejects_unknown_schema_and_fields() -> None:
    contract = _contract()
    contract["schema"] = "micromax.screen.v2"
    with pytest.raises(UnsupportedScreenContract, match="unsupported screen contract"):
        validate_screen_contract_v1(contract)

    contract = _contract()
    contract["internal"] = True
    with pytest.raises(ScreenContractError, match="unknown field.*internal"):
        validate_screen_contract_v1(contract)

    contract = _contract()
    contract[1] = True
    with pytest.raises(ScreenContractError, match="object member name must be a string"):
        validate_screen_contract_v1(contract)

    contract = _contract()
    contract["bad\x1b\u202e\n"] = True
    with pytest.raises(ScreenContractError) as caught:
        validate_screen_contract_v1(contract)
    message = str(caught.value)
    assert "\x1b" not in message
    assert "\u202e" not in message
    assert "\n" not in message
    assert r"bad\x1b\u202e\n" in message


def test_consumer_enforces_relational_cursor_row_and_cue_invariants() -> None:
    contract = _contract()
    contract["rows"] = list(contract["rows"])[:-1]  # type: ignore[arg-type]
    with pytest.raises(ScreenContractError, match="row count 3 must equal size.lines 4"):
        validate_screen_contract_v1(contract)

    contract = _contract()
    contract["rows"][1]["y"] = 3  # type: ignore[index]
    with pytest.raises(ScreenContractError, match="expected contiguous screen row 1"):
        validate_screen_contract_v1(contract)

    contract = _contract()
    contract["cursor"] = {"visible": False, "mode": "edit", "x": 0}
    with pytest.raises(ScreenContractError, match="hidden cursor must omit y and x"):
        validate_screen_contract_v1(contract)

    contract = _contract()
    contract["cues"] = [
        {"y": 0, "x": 2, "end": 3, "kind": "search"},
        {"y": 0, "x": 1, "end": 2, "kind": "search"},
    ]
    with pytest.raises(ScreenContractError, match="out of order"):
        validate_screen_contract_v1(contract)

    contract = _contract()
    contract["cues"] = [{"y": 0, "x": 15, "end": 17, "kind": "search"}]
    with pytest.raises(ScreenContractError, match=r"\.end: must be <= 16"):
        validate_screen_contract_v1(contract)


def test_parser_rejects_nonportable_json_and_duplicate_names() -> None:
    with pytest.raises(ScreenContractError, match="duplicate JSON object name 'schema'"):
        parse_screen_contract_v1(b'{"schema":"a","schema":"b"}')
    with pytest.raises(ScreenContractError, match="non-standard JSON number 'NaN'"):
        parse_screen_contract_v1(b'{"value":NaN}')
    with pytest.raises(ScreenContractError, match="non-integer JSON number '1.25'"):
        parse_screen_contract_v1(b'{"value":1.25}')
    with pytest.raises(ScreenContractError, match="interoperable magnitude"):
        parse_screen_contract_v1(b'{"value":9007199254740992}')
    with pytest.raises(ScreenContractError, match=r"unpaired UTF-16 surrogate U\+D800"):
        parse_screen_contract_v1(b'{"value":"\\ud800"}')
    with pytest.raises(ScreenContractError, match="not valid UTF-8"):
        parse_screen_contract_v1(b"\xff")


def test_parser_preflights_nesting_before_the_recursive_decoder() -> None:
    data = b"[" * 65 + b"]" * 65
    with pytest.raises(ScreenContractError, match="nesting exceeds depth budget 64"):
        parse_screen_contract_v1(data)

    # Delimiters inside strings, including escaped quotes, do not count.
    with pytest.raises(ScreenContractError, match="missing field"):
        parse_screen_contract_v1(b'{"text":"[[[{\\"deep}]]"}')


def test_bounded_reader_stops_after_the_input_budget(monkeypatch) -> None:
    import micromax_editor.screen_consumer as consumer

    monkeypatch.setattr(consumer, "SCREEN_CONTRACT_MAX_JSON_BYTES", 8)
    stream = io.BytesIO(b"123456789tail")
    with pytest.raises(ScreenContractError, match="exceeds budget 8 bytes"):
        read_screen_contract_v1(stream)
    assert stream.tell() == 9


def test_bounded_reader_handles_short_reads_until_eof() -> None:
    class ShortReader:
        def __init__(self, data: bytes) -> None:
            self._data = data
            self._offset = 0

        def read(self, size: int = -1) -> bytes:
            if self._offset >= len(self._data):
                return b""
            width = min(3, max(0, int(size)))
            chunk = self._data[self._offset : self._offset + width]
            self._offset += len(chunk)
            return chunk

    assert read_screen_contract_v1(ShortReader(FIXTURE.read_bytes())) == _contract()  # type: ignore[arg-type]


def test_direct_validator_requires_concrete_json_container_shapes() -> None:
    contract = _contract()
    contract["rows"] = tuple(contract["rows"])  # type: ignore[arg-type]

    with pytest.raises(ScreenContractError, match=r"\$\.rows: expected array"):
        validate_screen_contract_v1(contract)

    class DictSubclass(dict[str, object]):
        pass

    with pytest.raises(ScreenContractError, match=r"\$: expected object"):
        validate_screen_contract_v1(DictSubclass(_contract()))

    class StringSubclass(str):
        def __repr__(self) -> str:
            raise AssertionError("validator must not invoke caller-defined repr")

    contract = _contract()
    contract[StringSubclass("internal")] = True
    with pytest.raises(ScreenContractError, match="object member name must be a string"):
        validate_screen_contract_v1(contract)

    contract = _contract()
    contract["schema"] = StringSubclass("micromax.screen.v1")
    with pytest.raises(ScreenContractError, match=r"\$\.schema: expected string"):
        validate_screen_contract_v1(contract)


def test_public_tokens_are_ascii_interoperable() -> None:
    contract = _contract()
    contract["rows"][0]["kind"] = "café"  # type: ignore[index]

    with pytest.raises(ScreenContractError, match="alphanumeric hyphen token"):
        validate_screen_contract_v1(contract)


def test_text_projection_escapes_terminal_and_bidi_controls() -> None:
    contract = _contract()
    raw = "a\\\x1b\u009b\n\t\u202e\u202c\u2028\u2029"
    contract["rows"][0]["text"] = raw  # type: ignore[index]

    rendered = screen_contract_text(contract)

    assert rendered.splitlines()[0] == (
        r"a\\\x1b\x9b\n\t\u202e\u202c\u2028\u2029"
    )
    assert "\x1b" not in rendered
    assert "\u009b" not in rendered
    assert "\u202e" not in rendered
    assert "\u2028" not in rendered
    assert "\u2029" not in rendered
    assert "\u202c" not in rendered
    assert len(rendered.splitlines()) == 4


def test_consumer_cli_neutralizes_terminal_controls_in_errors(
    monkeypatch,
    capsys,
) -> None:
    def fail_open(_path: str):
        raise OSError("open failed \x1b\u009b\n\r\u202e\u2028")

    monkeypatch.setattr(screen_consumer, "_open_input", fail_open)

    assert main(["ignored", "--check"]) == 2
    error = capsys.readouterr().err
    assert "\x1b" not in error
    assert "\u009b" not in error
    assert "\u202e" not in error
    assert "\u2028" not in error
    assert r"\x1b\x9b\n\r\u202e\u2028" in error


def test_consumer_cli_supports_check_text_summary_and_visible_errors(
    tmp_path: Path,
    capsys,
) -> None:
    target = tmp_path / "screen.json"
    target.write_bytes(FIXTURE.read_bytes())

    assert main([str(target), "--check"]) == 0
    assert capsys.readouterr().out == ""

    assert main([str(target), "--text"]) == 0
    text = capsys.readouterr().out
    assert text.splitlines()[-1] == "ur:1/1 0% normal"

    contract = _contract()
    contract["rows"][0]["text"] = "a\\\x1b\u009b\n\t\u202e\u202c\u2028\u2029"  # type: ignore[index]
    target.write_text(json.dumps(contract), encoding="utf-8")
    assert main([str(target), "--text"]) == 0
    escaped = capsys.readouterr().out
    assert escaped.splitlines()[0] == r"a\\\x1b\x9b\n\t\u202e\u202c\u2028\u2029"
    assert "\x1b" not in escaped
    assert "\u009b" not in escaped
    assert "\u202e" not in escaped
    assert "\u2028" not in escaped
    assert "\u2029" not in escaped
    assert len(escaped.splitlines()) == 4

    target.write_bytes(FIXTURE.read_bytes())
    assert main([str(target), "--summary"]) == 0
    summary = json.loads(capsys.readouterr().out)
    assert summary["schema"] == "micromax.screen.v1"
    assert summary["row_kinds"]["viewport"] == 2

    target.write_text("{}", encoding="utf-8")
    assert main([str(target), "--check"]) == 2
    assert "missing field" in capsys.readouterr().err


def test_editor_output_pipes_into_independent_consumer_process(tmp_path: Path) -> None:
    sample = tmp_path / "sample.txt"
    sample.write_text("alpha\nbeta\n", encoding="utf-8")
    env = dict(os.environ)
    env["HOME"] = str(tmp_path)
    env["MICROMAX_INIT"] = str(tmp_path / "missing-init.mx")
    env["PYTHONPATH"] = str(REPO_ROOT / "src")

    producer = subprocess.run(
        [
            sys.executable,
            "-m",
            "micromax_editor",
            str(sample),
            "--plugins",
            str(tmp_path / "no-plugins"),
            "--dump-screen",
            "8",
            "40",
        ],
        cwd=REPO_ROOT,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
        timeout=30,
    )
    assert producer.returncode == 0, producer.stderr.decode("utf-8", errors="replace")

    consumer = subprocess.run(
        [sys.executable, "-m", "micromax_editor.screen_consumer", "--check"],
        cwd=REPO_ROOT,
        env=env,
        input=producer.stdout,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
        timeout=30,
    )
    assert consumer.returncode == 0, consumer.stderr.decode("utf-8", errors="replace")
    assert consumer.stdout == b""
