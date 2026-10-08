from __future__ import annotations

import random
from pathlib import Path

import pytest

import micromax_editor.buffer as buffer_module
import micromax_editor.editor as editor_module
from micromax_editor.buffer import (
    FASTDIRTY_AUTO_BYTES,
    Buffer,
    Cursor,
    _splice_line_text,
    normalize_buffer_text,
)
from micromax_editor.editor import Editor, MacroStep


def _count_current_signatures(
    buffer: Buffer,
    monkeypatch: pytest.MonkeyPatch,
) -> list[int]:
    calls = [0]
    original = buffer._current_signature

    def counted() -> tuple[int, str]:
        calls[0] += 1
        return original()

    monkeypatch.setattr(buffer, "_current_signature", counted)
    return calls


def test_live_growth_promotes_once_then_stops_whole_document_hashing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    baseline = "x" * (FASTDIRTY_AUTO_BYTES - 1)
    editor = Editor()
    editor.new_buffer("growing.txt", baseline)
    eb = editor.cur()
    calls = _count_current_signatures(eb.buf, monkeypatch)

    end = eb.buf.insert(Cursor(0, len(baseline)), "YZ")

    assert calls == [1]
    assert eb.buf.get_text() == baseline + "YZ"
    assert eb.buf.fastdirty is True
    assert eb.buf.dirty is True
    assert eb.buf.current_byte_size == FASTDIRTY_AUTO_BYTES + 1
    assert eb.local_options["fastdirty"] is True
    assert editor.options.get("fastdirty", local=eb.local_options) is True

    end = eb.buf.insert(end, "!")
    assert calls == [1]
    assert eb.buf.current_signature is None

    # The automatic local value is ordinary visible option state.  An explicit
    # local false restores exact semantics and prevents immediate re-promotion.
    assert editor.exec_command_line("setlocal fastdirty false") is True
    assert calls == [2]
    assert eb.buf.fastdirty is False
    assert eb.local_options["fastdirty"] is False

    eb.buf.delete_range(Cursor(0, len(baseline)), end)
    assert calls == [3]
    assert eb.buf.get_text() == baseline
    assert eb.buf.dirty is False
    assert eb.buf.fastdirty is False


def test_live_growth_threshold_is_measured_in_utf8_bytes() -> None:
    # U+00E9 occupies two UTF-8 bytes, so promotion must follow the exact byte
    # signature rather than Python character count.
    baseline = "é" * (FASTDIRTY_AUTO_BYTES // 2 - 1)
    editor = Editor()
    editor.new_buffer("unicode-growth.txt", baseline)
    eb = editor.cur()

    assert eb.buf.baseline_byte_size == FASTDIRTY_AUTO_BYTES - 2
    eb.buf.insert(Cursor(0, len(baseline)), "é")

    assert eb.buf.current_byte_size == FASTDIRTY_AUTO_BYTES
    assert eb.buf.fastdirty is True
    assert eb.local_options["fastdirty"] is True


def test_explicit_local_false_opts_out_of_live_growth_promotion(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    baseline = "x" * (FASTDIRTY_AUTO_BYTES - 1)
    editor = Editor()
    editor.new_buffer("exact.txt", baseline)
    eb = editor.cur()
    assert editor.exec_command_line("setlocal fastdirty false") is True
    calls = _count_current_signatures(eb.buf, monkeypatch)

    end = eb.buf.insert(Cursor(0, len(baseline)), "YZ")
    assert calls == [1]
    assert eb.buf.fastdirty is False
    assert eb.local_options["fastdirty"] is False
    assert eb.buf.current_byte_size == FASTDIRTY_AUTO_BYTES + 1

    eb.buf.insert(end, "!")
    assert calls == [2]
    assert eb.buf.fastdirty is False


def test_local_fastdirty_authority_change_does_not_rehash_other_exact_buffers(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    editor = Editor()
    editor.new_buffer("one.txt", "alpha")
    editor.new_buffer("two.txt", "beta")
    one = editor.buffers["one.txt"]
    two = editor.buffers["two.txt"]
    calls_one = _count_current_signatures(one.buf, monkeypatch)
    calls_two = _count_current_signatures(two.buf, monkeypatch)

    assert editor.switch_buffer("one.txt") is True
    assert editor.exec_command_line("setlocal fastdirty false") is True

    assert one.local_options["fastdirty"] is False
    assert calls_one == [0]
    assert calls_two == [0]
    assert one.buf.fastdirty is False
    assert two.buf.fastdirty is False


def test_failed_macro_restores_live_growth_promotion_authority() -> None:
    baseline = "x" * (FASTDIRTY_AUTO_BYTES - 1)
    editor = Editor()
    editor.new_buffer("rollback.txt", baseline)
    eb = editor.cur()
    editor.set_macro(
        "fail-after-opt-out",
        [
            MacroStep(
                kind="command",
                name="command",
                payload={"cmdline": "setlocal fastdirty false"},
            ),
            MacroStep(
                kind="action",
                name="rev0994-missing-action",
                payload={"input": {}},
            ),
        ],
    )

    assert editor.play_macro("fail-after-opt-out") is False
    assert "fastdirty" not in eb.local_options
    assert eb.buf.fastdirty is False

    eb.buf.insert(Cursor(0, len(baseline)), "YZ")
    assert eb.buf.fastdirty is True
    assert eb.local_options["fastdirty"] is True


def test_exact_generation_signature_is_reused_by_mark_clean(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    buffer = Buffer("abc")
    calls = _count_current_signatures(buffer, monkeypatch)

    end = buffer.insert(Cursor(0, 3), "d")
    assert calls == [1]
    live = buffer.current_signature
    assert live is not None

    buffer.mark_clean()
    assert calls == [1]
    assert buffer.current_signature == live
    assert buffer._saved_sig == live
    assert buffer.dirty is False

    buffer.set_fastdirty(True)
    buffer.insert(end, "e")
    assert buffer.current_signature is None
    buffer.mark_clean()
    assert calls == [2]
    assert buffer.current_signature == buffer._saved_sig


def test_failed_cleanup_save_restores_cached_crossing_generation(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    baseline = "x" * (FASTDIRTY_AUTO_BYTES - 1)
    path = tmp_path / "crossing.txt"
    path.write_text(baseline, encoding="utf-8")

    editor = Editor()
    editor.new_buffer(str(path), baseline, path=str(path))
    eb = editor.cur()
    eb.buf.insert(Cursor(0, len(baseline)), " X ")
    assert eb.buf.fastdirty is True
    crossing_signature = eb.buf.current_signature
    assert crossing_signature is not None
    assert editor.exec_command_line("setlocal rmtrailingws true") is True
    assert editor.exec_command_line("setlocal eofnewline false") is True

    def fail_write(*args: object, **kwargs: object) -> object:
        raise OSError("simulated write failure")

    monkeypatch.setattr(editor_module, "write_file_bytes", fail_write)

    with pytest.raises(OSError, match="simulated write failure"):
        editor.save()

    assert eb.buf.get_text() == baseline + " X "
    assert eb.buf.fastdirty is True
    assert eb.buf.dirty is True
    assert eb.buf.current_signature == crossing_signature
    assert eb.buf._saved_sig != crossing_signature


def test_observed_raw_line_write_invalidates_generation_signature() -> None:
    editor = Editor()
    editor.new_buffer("raw-lines.txt", "before")
    eb = editor.cur()
    original_signature = eb.buf.current_signature
    assert original_signature == eb.buf._saved_sig

    def mutate_lines(current: Editor) -> bool:
        current.cur().buf.lines[:] = ["after"]
        return True

    editor.actions.register("Rev0994RawLines", mutate_lines)
    editor.set_macro(
        "raw-lines",
        [MacroStep(kind="action", name="Rev0994RawLines", payload={"input": {}})],
    )

    assert editor.play_macro("raw-lines") is True
    assert eb.buf.get_text() == "after"
    assert eb.buf.current_signature is None

    # Direct mutable-line compatibility still requires ``touch_external()`` for
    # version/dirty publication, but a missed notification must not let save
    # adopt the old generation's cached signature.
    eb.buf.mark_clean()
    assert eb.buf.current_signature == eb.buf._current_signature()
    assert eb.buf._saved_sig == eb.buf.current_signature
    assert eb.buf._saved_sig != original_signature


def test_cross_line_range_to_one_line_preserves_exact_splice_witness() -> None:
    buffer = Buffer("alpha\nbeta\ngamma")

    forward = buffer.replace_range_with_witness(
        Cursor(0, 2),
        Cursor(1, 2),
        "X",
    )

    assert forward.old_text == "pha\nbe"
    assert forward.new_text == "X"
    assert forward.new_end == Cursor(0, 3)
    assert buffer.snapshot_lines() == ("alXta", "gamma")
    assert buffer.get_text() == "alXta\ngamma"

    inverse = buffer.replace_range_with_witness(
        forward.start,
        forward.new_end,
        forward.old_text,
        expected_old_text=forward.new_text,
    )
    assert inverse.new_end == forward.old_end
    assert buffer.get_text() == "alpha\nbeta\ngamma"


def test_random_multiline_replace_matches_flat_text_reference() -> None:
    alphabet = "abαβ🙂\ud800"
    rng = random.Random(994_2)

    def random_row() -> str:
        return "".join(rng.choice(alphabet) for _ in range(rng.randrange(12)))

    def offset_for(lines: tuple[str, ...], cursor: Cursor) -> int:
        return sum(len(line) + 1 for line in lines[: cursor.line]) + cursor.col

    for _ in range(1_500):
        original_lines = tuple(random_row() for _ in range(rng.randrange(1, 7)))
        original_text = "\n".join(original_lines)
        buffer = Buffer(original_text)
        raw_start = Cursor(rng.randrange(-2, 9), rng.randrange(-4, 18))
        raw_end = Cursor(rng.randrange(-2, 9), rng.randrange(-4, 18))
        start = buffer.clamp(raw_start)
        end = buffer.clamp(raw_end)
        if (end.line, end.col) < (start.line, start.col):
            start, end = end, start

        replacement_parts = [random_row() for _ in range(rng.randrange(1, 5))]
        raw_replacement = "\r\n".join(replacement_parts)
        replacement = normalize_buffer_text(raw_replacement)
        start_offset = offset_for(original_lines, start)
        end_offset = offset_for(original_lines, end)
        old_text = original_text[start_offset:end_offset]
        expected = (
            original_text[:start_offset]
            + replacement
            + original_text[end_offset:]
        )

        witness = buffer.replace_range_with_witness(
            raw_start,
            raw_end,
            raw_replacement,
        )

        assert witness.start == start
        assert witness.old_end == end
        assert witness.old_text == old_text
        assert witness.new_text == replacement
        assert witness.changed is (old_text != replacement)
        assert buffer.get_text() == expected

        if witness.changed:
            inverse = buffer.replace_range_with_witness(
                witness.start,
                witness.new_end,
                witness.old_text,
                expected_old_text=witness.new_text,
            )
            assert inverse.new_end == witness.old_end
            assert buffer.get_text() == original_text


def test_single_line_splice_matches_clamped_reference() -> None:
    original = "immutable"
    assert _splice_line_text(original, 4, 4, "") is original

    alphabet = "abαβ🙂\ud800"
    rng = random.Random(994)

    for _ in range(2_000):
        line = "".join(rng.choice(alphabet) for _ in range(rng.randrange(80)))
        replacement = "".join(
            rng.choice(alphabet) for _ in range(rng.randrange(20))
        )
        raw_start = rng.randrange(-20, len(line) + 21)
        raw_end = rng.randrange(-20, len(line) + 21)
        start = max(0, min(raw_start, len(line)))
        end = max(start, min(raw_end, len(line)))

        expected = line[:start] + replacement + line[end:]
        assert _splice_line_text(line, raw_start, raw_end, replacement) == expected


def test_all_single_line_mutators_share_one_pass_splice_constructor(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[tuple[str, ...]] = []
    original = buffer_module._join_line_fragments

    def counted(*parts: str) -> str:
        calls.append(tuple(parts))
        return original(*parts)

    monkeypatch.setattr(buffer_module, "_join_line_fragments", counted)
    buffer = Buffer("abcdefgh")
    buffer.set_fastdirty(True)

    end = buffer.insert(Cursor(0, 4), "XY")
    assert buffer.get_text() == "abcdXYefgh"
    assert calls[-1] == ("abcd", "XY", "efgh")

    buffer.delete_range(Cursor(0, 2), Cursor(0, 5))
    assert buffer.get_text() == "abYefgh"
    assert calls[-1] == ("ab", "Yefgh")

    witness = buffer.replace_range_with_witness(Cursor(0, 1), Cursor(0, 4), "!")
    assert witness.changed is True
    assert buffer.get_text() == "a!fgh"
    assert calls[-1] == ("a", "!", "fgh")
    assert end == Cursor(0, 6)
