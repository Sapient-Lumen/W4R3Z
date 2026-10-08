"""micromax.core

Core words for the micromax VM.

Micromax is Forth-inspired but not standards-bound: we take what helps scripting and embedding.


These are chosen to support fast iteration and editor embedding.
"""

from __future__ import annotations

from typing import Any, Optional

from .vm import (
    VM,
    MicromaxError,
    Span,
    Code,
    Bytecode,
    Quotation,
    Cell,
    PrimitiveWord,
    ColonWord,
    Word,
    DeferredWord,
    HookWord,
    HookHandler,
    word_effect,
    word_doc_summary,
    quote_effect,
    infer_effect_sig_for_code,
    parse_effect_sig,
)


def install_core_words(vm: VM, *, wid: Optional[int] = None) -> None:
    install_wid = vm.forth_wid if wid is None else wid

    # ----- printing / debugging -----
    def w_dot(vm: VM) -> None:
        x = vm.pop()
        print(x, end="")

    def w_cr(vm: VM) -> None:
        print()

    def w_emit(vm: VM) -> None:
        n = vm.pop_int()
        print(chr(n & 0x10FFFF), end="")

    def w_dots(vm: VM) -> None:
        print("stack:", vm.stack)

    def w_callstack(vm: VM) -> None:
        """( -- xs ) Return the current callstack as a list of names.

        This is a debugging helper for hosts/UIs. It intentionally excludes
        the callstack word itself when present.
        """

        xs = list(getattr(vm, "callstack", []) or [])
        if xs and str(xs[-1]) in ("callstack", "trace"):
            xs = xs[:-1]
        vm.stack.append([str(x) for x in xs])

    def w_words(vm: VM) -> None:
        names = sorted(vm.all_words_view().keys())
        for n in names:
            print(n)

    def w_words_list(vm: VM) -> None:
        """( -- names ) Return a list of word names in the current search order."""
        vm.stack.append(sorted(vm.all_words_view().keys()))

    def w_wid_words(vm: VM) -> None:
        """( wid -- names ) Return a list of word names in a specific wordlist."""
        wid = vm.pop_int()
        vm.stack.append(sorted(vm.wordlists.get(int(wid), {}).keys()))

    def w_wid_name(vm: VM) -> None:
        """( wid -- s ) Return the friendly name of a wordlist (or "")."""
        wid = vm.pop_int()
        vm.stack.append(str(vm.wordlist_names.get(int(wid), "")))

    def _xt_kind_str(xt: Any) -> str:
        if isinstance(xt, Quotation):
            return "quote"
        if isinstance(xt, PrimitiveWord):
            return "primitive"
        if isinstance(xt, ColonWord):
            return "colon"
        if isinstance(xt, DeferredWord):
            return "deferred"
        if isinstance(xt, HookWord):
            return "hook"
        if isinstance(xt, Word):
            return "word"
        return type(xt).__name__

    def _word_row(vm: VM, name: str, w: Word, wid: int) -> list[Any]:
        return [
            str(name),
            _xt_kind_str(w),
            str(word_effect(w) or ""),
            str(word_doc_summary(w) or ""),
            int(wid),
            str(vm.wordlist_names.get(wid, str(wid))),
        ]

    def w_words_rows(vm: VM) -> None:
        """( -- rows ) Return rows [name kind effect doc wid wl] for visible words."""
        rows = []
        for name in sorted(vm.all_words_view().keys()):
            found = vm.find_word_with_wid(name)
            if found is None:
                continue
            wid, w = found
            rows.append(_word_row(vm, name, w, wid))
        vm.stack.append(rows)

    def w_wid_word_rows(vm: VM) -> None:
        """( wid -- rows ) Return rows [name kind effect doc wid wl] for one wordlist."""
        wid = vm.pop_int()
        wl = vm.wordlists.get(int(wid), {})
        rows = [_word_row(vm, name, wl[name], int(wid)) for name in sorted(wl.keys())]
        vm.stack.append(rows)

    def _tok_to_src(t) -> str:
        if t.kind == "int":
            return str(t.value)
        if t.kind == "str":
            s = str(t.value)
            s = s.replace("\\", "\\\\").replace("\n", "\\n").replace("\t", "\\t").replace('"', '\\"')
            return f'"{s}"'
        if t.kind in ("sym", "word"):
            return str(t.value)
        if t.kind == "comment":
            return f"( {t.value} )"
        return str(t.value)

    def _print_word_help_lines(w: Word) -> None:
        effect = word_effect(w)
        if effect:
            print(f"  effect: {effect}")
        summary = word_doc_summary(w)
        if summary:
            for line in summary.splitlines():
                print(f"  {line}")

    def w_see(vm: VM) -> None:
        """( -- ) Decompile / describe the next named word."""
        name = vm.expect_word_name()
        found = vm.find_word_with_wid(name)
        if found is None:
            print(f"{name}: (unknown)")
            return
        wid, w = found
        wl = vm.wordlist_names.get(wid, str(wid))

        def _span_comment(sp: Span | None) -> str:
            if sp is None:
                return ""
            return f" ; {sp.filename}:{sp.line}:{sp.col}"

        def _fmt_const(x: object) -> str:
            if isinstance(x, Quotation):
                return f"[{len(x.code.tokens)}t{'*' if x.code.bytecode else ''}]"
            if hasattr(x, 'name') and type(x).__name__ == 'WordRef':
                return str(getattr(x, 'name'))
            return repr(x)

        def _disasm_lines(bc: Bytecode) -> list[str]:
            lines: list[str] = []
            for pc, ins in enumerate(bc.instrs):
                if ins.op in ("JMP", "JZ"):
                    off = int(ins.arg or 0)
                    tgt = pc + 1 + off
                    arg_s = f"{off:+d} -> {tgt:04d}"
                    lines.append(f"{pc:04d} {ins.op:9} {arg_s:<22}{_span_comment(ins.span)}")
                    continue

                arg_s = ""
                if ins.arg is not None:
                    try:
                        arg_s = _fmt_const(bc.consts[int(ins.arg)])
                    except Exception:
                        arg_s = str(ins.arg)
                lines.append(f"{pc:04d} {ins.op:9} {arg_s:<22}{_span_comment(ins.span)}")
            if bc.consts:
                lines.append("\\ consts")
                for i, c in enumerate(bc.consts):
                    lines.append(f"\\  [{i}] {_fmt_const(c)}")
            return lines

        if isinstance(w, PrimitiveWord):
            print(f"{name}  [{wid}:{wl}]  primitive")
            _print_word_help_lines(w)
            return
        if isinstance(w, ColonWord):
            body = " ".join(_tok_to_src(t) for t in w.code.tokens)
            print(f": {name} {body} ;")
            effect = word_effect(w)
            if effect:
                print(f"\\ effect {effect}")
            summary = word_doc_summary(w)
            if summary:
                for line in summary.splitlines():
                    print(f"\\ doc {line}")
            if getattr(w, "span", None) is not None:
                sp = w.span
                print(f"\\ defined at {sp.filename}:{sp.line}:{sp.col}")
            if w.code.bytecode is not None:
                bc = w.code.bytecode
                print(f"\\ compiled {len(bc.instrs)} insns, {len(bc.consts)} consts")
                print("\\ disasm")
                for line in _disasm_lines(bc):
                    # keep disassembly comments-friendly (so `xt-src` parsers can ignore it)
                    print(f"\\ {line}")
            return
        if isinstance(w, DeferredWord):
            xt = w.cell.value
            xtn = getattr(xt, "name", "<quote>") if xt is not None else "<unset>"
            print(f"defer {name}  (is {xtn})")
            _print_word_help_lines(w)
            return
        if isinstance(w, HookWord):
            hs = [_hook_handler_desc(h) for h in w.handlers]
            print(f"hook {name}  handlers: {', '.join(hs) if hs else '(none)'}")
            if getattr(w, "span", None) is not None:
                sp = w.span
                print(f"\\ defined at {sp.filename}:{sp.line}:{sp.col}")
            _print_word_help_lines(w)
            return

        print(f"{name}  [{wid}:{wl}]  {type(w).__name__}")
        _print_word_help_lines(w)

    def w_help(vm: VM) -> None:
        name = vm.expect_word_name()
        found = vm.find_word_with_wid(name)
        if found is None:
            print(f"{name}: (unknown)")
            return
        wid, w = found
        wl = vm.wordlist_names.get(wid, str(wid))
        print(f"{name}  [{wid}:{wl}]  {type(w).__name__}")
        _print_word_help_lines(w)

    def w_where(vm: VM) -> None:
        name = vm.expect_word_name()
        for wid in vm.search_order:
            wl = vm.wordlists.get(wid, {})
            if name in wl:
                print(f"{name} -> {wid}:{vm.wordlist_names.get(wid, '?')}")
                return
        print(f"{name}: (not found)")

    def w_order(vm: VM) -> None:
        parts = []
        for wid in vm.search_order:
            parts.append(f"{wid}:{vm.wordlist_names.get(wid, '?')}")
        print("order:", " ".join(parts), " | current:", f"{vm.current_wid}:{vm.wordlist_names.get(vm.current_wid,'?')}")

    # ----- stack ops -----
    def w_dup(vm: VM) -> None:
        if not vm.stack:
            raise MicromaxError("Stack underflow")
        vm.stack.append(vm.stack[-1])

    def w_drop(vm: VM) -> None:
        vm.pop()

    def w_swap(vm: VM) -> None:
        if len(vm.stack) < 2:
            raise MicromaxError("Stack underflow")
        vm.stack[-1], vm.stack[-2] = vm.stack[-2], vm.stack[-1]

    def w_over(vm: VM) -> None:
        if len(vm.stack) < 2:
            raise MicromaxError("Stack underflow")
        vm.stack.append(vm.stack[-2])

    def w_rot(vm: VM) -> None:
        if len(vm.stack) < 3:
            raise MicromaxError("Stack underflow")
        a, b, c = vm.stack[-3], vm.stack[-2], vm.stack[-1]
        vm.stack[-3], vm.stack[-2], vm.stack[-1] = b, c, a

    def w_depth(vm: VM) -> None:
        """( -- n ) Stack depth."""
        vm.stack.append(len(vm.stack))

    def w_clear(vm: VM) -> None:
        """( -- ) Clear the data stack."""
        vm.stack.clear()

    def w_pick(vm: VM) -> None:
        """( ... u -- ... x ) Copy the u-th item (0=top)."""
        u = vm.pop_int()
        if u < 0:
            raise MicromaxError("pick: u must be >= 0")
        if len(vm.stack) <= u:
            raise MicromaxError("Stack underflow")
        vm.stack.append(vm.stack[-1 - u])

    def w_roll(vm: VM) -> None:
        """( ... u -- ... ) Move u-th item (0=top) to the top."""
        u = vm.pop_int()
        if u < 0:
            raise MicromaxError("roll: u must be >= 0")
        if len(vm.stack) <= u:
            raise MicromaxError("Stack underflow")
        idx = -1 - u
        x = vm.stack.pop(idx)
        vm.stack.append(x)

    # ----- return stack (rev12) -----
    def w_to_r(vm: VM) -> None:
        """( x -- ) Move x to the return stack."""
        vm.rstack.append(vm.pop())

    def w_r_from(vm: VM) -> None:
        """( -- x ) Move top of return stack to data stack."""
        if not vm.rstack:
            raise MicromaxError("Return stack underflow")
        vm.stack.append(vm.rstack.pop())

    def w_r_fetch(vm: VM) -> None:
        """( -- x ) Copy top of return stack to data stack."""
        if not vm.rstack:
            raise MicromaxError("Return stack underflow")
        vm.stack.append(vm.rstack[-1])

    def w_rdepth(vm: VM) -> None:
        """( -- n ) Return stack depth."""
        vm.stack.append(len(vm.rstack))

    # ----- arithmetic -----
    def binop_int(vm: VM, op) -> None:
        b = vm.pop_int()
        a = vm.pop_int()
        vm.stack.append(op(a, b))

    def w_add(vm: VM) -> None:
        binop_int(vm, lambda a, b: a + b)

    def w_sub(vm: VM) -> None:
        binop_int(vm, lambda a, b: a - b)

    def w_mul(vm: VM) -> None:
        binop_int(vm, lambda a, b: a * b)

    def w_div(vm: VM) -> None:
        b = vm.pop_int()
        a = vm.pop_int()
        if b == 0:
            raise MicromaxError("Division by zero")
        vm.stack.append(a // b)

    def w_mod(vm: VM) -> None:
        b = vm.pop_int()
        a = vm.pop_int()
        if b == 0:
            raise MicromaxError("Division by zero")
        vm.stack.append(a % b)

    # ----- comparisons -----
    def w_eq(vm: VM) -> None:
        b = vm.pop()
        a = vm.pop()
        vm.stack.append(1 if a == b else 0)

    def w_lt(vm: VM) -> None:
        b = vm.pop_int()
        a = vm.pop_int()
        vm.stack.append(1 if a < b else 0)

    def w_gt(vm: VM) -> None:
        b = vm.pop_int()
        a = vm.pop_int()
        vm.stack.append(1 if a > b else 0)

    def w_0eq(vm: VM) -> None:
        a = vm.pop_int()
        vm.stack.append(1 if a == 0 else 0)

    # ----- type predicates (portable; useful for defensive scripts) -----
    def w_int_q(vm: VM) -> None:
        """( x -- flag ) 1 if x is an int."""
        x = vm.pop()
        vm.stack.append(1 if isinstance(x, int) else 0)

    def w_str_q(vm: VM) -> None:
        """( x -- flag ) 1 if x is a string."""
        x = vm.pop()
        vm.stack.append(1 if isinstance(x, str) else 0)

    def w_list_q(vm: VM) -> None:
        """( x -- flag ) 1 if x is a list."""
        x = vm.pop()
        vm.stack.append(1 if isinstance(x, list) else 0)

    def w_quote_q(vm: VM) -> None:
        """( x -- flag ) 1 if x is a quotation."""
        x = vm.pop()
        vm.stack.append(1 if isinstance(x, Quotation) else 0)

    def w_xt_q(vm: VM) -> None:
        """( x -- flag ) 1 if x is an execution token (word or quotation)."""
        x = vm.pop()
        vm.stack.append(1 if isinstance(x, (Word, Quotation)) else 0)

    # ----- string-specific comparisons (typed) -----
    def w_s_eq(vm: VM) -> None:
        b = vm.pop_str()
        a = vm.pop_str()
        vm.stack.append(1 if a == b else 0)

    def w_s_lt(vm: VM) -> None:
        b = vm.pop_str()
        a = vm.pop_str()
        vm.stack.append(1 if a < b else 0)

    # ----- conversions (portable) -----
    def w_to_int(vm: VM) -> None:
        x = vm.pop()
        if isinstance(x, int):
            vm.stack.append(int(x))
            return
        if isinstance(x, str):
            s = x.strip()
            try:
                vm.stack.append(int(s, 10))
                return
            except Exception as e:
                raise MicromaxError("to-int: invalid integer") from e
        raise MicromaxError(f"to-int: expected int or str, got {type(x).__name__}")

    def _to_str_repr(x: Any, *, depth: int = 0) -> str:
        # Deterministic-ish, portable representation for tooling and messages.
        # Strings are JSON-quoted when nested (in lists/maps).
        import json

        if depth > 6:
            return "..."
        if isinstance(x, str):
            return json.dumps(x, ensure_ascii=False)
        if isinstance(x, int):
            return str(int(x))
        if isinstance(x, list):
            inner = ", ".join(_to_str_repr(v, depth=depth + 1) for v in x)
            return "[" + inner + "]"
        if isinstance(x, dict):
            # Portable maps are string-keyed; sort for stable output.
            items = []
            for k in sorted(x.keys(), key=lambda kk: str(kk)):
                ks = json.dumps(str(k), ensure_ascii=False)
                vs = _to_str_repr(x.get(k), depth=depth + 1)
                items.append(f"{ks}: {vs}")
            return "{" + ", ".join(items) + "}"
        if isinstance(x, Cell):
            return f"<cell { _to_str_repr(x.value, depth=depth + 1) }>"
        if isinstance(x, Quotation):
            return "<quote>"
        if isinstance(x, Word):
            nm = getattr(x, "name", "<xt>")
            return f"<xt {nm}>"
        return f"<{type(x).__name__}>"

    def w_to_str(vm: VM) -> None:
        x = vm.pop()
        if isinstance(x, str):
            vm.stack.append(x)
            return
        vm.stack.append(_to_str_repr(x))
    # ----- quotations / combinators -----
    def w_call(vm: VM) -> None:
        q = vm.pop_quote()
        vm.exec_xt(q)

    def w_execute(vm: VM) -> None:
        """( xt -- ) Execute an execution token (word or quotation)."""
        xt = vm.pop_xt()
        vm.exec_xt(xt)

    def w_tick(vm: VM) -> None:
        """( -- xt ) Parse next name and push its execution token."""
        name = vm.expect_word_name()
        w = vm.find_word(name)
        if w is None:
            raise MicromaxError(f"Unknown word: {name}")
        vm.stack.append(w)

    def w_defer(vm: VM) -> None:
        """( -- ) Parse next name and define a deferred word."""
        name = vm.expect_word_name()
        cell = Cell(None)
        dw = DeferredWord(name=name, cell=cell, doc="( -- ) deferred")
        vm._add_word(vm.current_wid, dw)

    def w_is(vm: VM) -> None:
        """( xt -- ) Parse deferred word name and set its behavior."""
        name = vm.expect_word_name()
        xt = vm.pop_xt()
        w = vm.find_word(name)
        if not isinstance(w, DeferredWord):
            raise MicromaxError(f"IS expects a deferred word, got: {name}")
        w.cell.value = xt

    def w_defer_fetch(vm: VM) -> None:
        """( dw -- xt|0 ) Fetch current xt from deferred word (0 if unset)."""
        dw = vm.pop()
        if not isinstance(dw, DeferredWord):
            raise MicromaxError("defer@: expected deferred word xt")
        vm.stack.append(dw.cell.value if dw.cell.value is not None else 0)

    def w_defer_store(vm: VM) -> None:
        """( xt dw -- ) Store xt into deferred word."""
        dw = vm.pop()
        xt = vm.pop_xt()
        if not isinstance(dw, DeferredWord):
            raise MicromaxError("defer!: expected deferred word xt")
        dw.cell.value = xt

    def w_xt_name(vm: VM) -> None:
        """( xt -- s ) Return a name for an execution token."""
        xt = vm.pop()
        if isinstance(xt, Quotation):
            vm.stack.append("<quote>")
            return
        if isinstance(xt, Word):
            vm.stack.append(getattr(xt, "name", "<word>"))
            return
        raise MicromaxError("xt-name: expected execution token")

    def w_xt_kind(vm: VM) -> None:
        """( xt -- s ) Return a stable kind string for an execution token."""

        xt = vm.pop()
        if isinstance(xt, Quotation):
            vm.stack.append("quote")
            return
        if isinstance(xt, PrimitiveWord):
            vm.stack.append("primitive")
            return
        if isinstance(xt, ColonWord):
            vm.stack.append("colon")
            return
        if isinstance(xt, DeferredWord):
            vm.stack.append("deferred")
            return
        if isinstance(xt, HookWord):
            vm.stack.append("hook")
            return
        if isinstance(xt, Word):
            vm.stack.append("word")
            return
        raise MicromaxError("xt-kind: expected execution token")

    def w_xt_effect(vm: VM) -> None:
        """( xt -- s ) Return stack-effect string for xt (or "")."""

        xt = vm.pop()
        if isinstance(xt, Quotation):
            vm.stack.append(str(quote_effect(xt) or ""))
            return
        if isinstance(xt, Word):
            vm.stack.append(str(word_effect(xt) or ""))
            return
        raise MicromaxError("xt-effect: expected execution token")

    def w_stackcheck_store(vm: VM) -> None:
        """( n -- ) Set dev-mode stack effect checking.

        n:
          0 = off
          1 = warn (stderr)
          2 = error (raise)
        """
        n = vm.pop_int()
        if n <= 0:
            vm.stackcheck_mode = 0
        elif n == 1:
            vm.stackcheck_mode = 1
        else:
            vm.stackcheck_mode = 2

    def w_stackcheck_fetch(vm: VM) -> None:
        """( -- n ) Return current stackcheck mode (0/1/2)."""
        vm.stack.append(int(getattr(vm, "stackcheck_mode", 0)))

    def w_infer_effect(vm: VM) -> None:
        """( xt -- s|0 ) Infer a closed stack effect for straight-line code.

        This is best-effort and intentionally conservative:
        - succeeds for simple quotations/colon words that only call other
          closed-effect words and push literals
        - returns 0 if unknown
        """
        xt = vm.pop_xt()

        if isinstance(xt, Quotation):
            inferred = infer_effect_sig_for_code(vm, xt.code.tokens)
            vm.stack.append(inferred.raw if inferred is not None else 0)
            return
        if isinstance(xt, ColonWord):
            inferred = infer_effect_sig_for_code(vm, xt.code.tokens)
            vm.stack.append(inferred.raw if inferred is not None else 0)
            return

        # For primitives and other words, inference is "declared effect if closed".
        sig = parse_effect_sig(word_effect(xt)) if isinstance(xt, Word) else None
        vm.stack.append(sig.raw if sig is not None and sig.closed else 0)

    def w_check_effect(vm: VM) -> None:
        """( xt -- flag ) 1 if declared effect matches inferred effect."""
        xt = vm.pop_xt()
        if isinstance(xt, Quotation):
            decl = parse_effect_sig(quote_effect(xt))
            inf = infer_effect_sig_for_code(vm, xt.code.tokens)
            vm.stack.append(1 if decl is not None and decl.closed and inf is not None and inf.closed and (decl.ins, decl.outs) == (inf.ins, inf.outs) else 0)
            return
        if isinstance(xt, ColonWord):
            decl = parse_effect_sig(word_effect(xt))
            inf = infer_effect_sig_for_code(vm, xt.code.tokens)
            vm.stack.append(1 if decl is not None and decl.closed and inf is not None and inf.closed and (decl.ins, decl.outs) == (inf.ins, inf.outs) else 0)
            return
        vm.stack.append(0)

    def w_xt_doc(vm: VM) -> None:
        """( xt -- s ) Return documentation string for xt (or "")."""

        xt = vm.pop()
        if isinstance(xt, Quotation):
            vm.stack.append("")
            return
        if isinstance(xt, Word):
            vm.stack.append(str(word_doc_summary(xt) or ""))
            return
        raise MicromaxError("xt-doc: expected execution token")

    def w_xt_src(vm: VM) -> None:
        """( xt -- s ) Return a source-ish representation for xt.

        This is intentionally *best effort* (not a full pretty-printer). It is meant
        for tooling: debugging, inspection UIs, and editor help surfaces.

        Policy:
        - The *first line* is a compact "definition-ish" form (so tests and tools can
          `startswith()` it reliably).
        - Optional metadata is appended as `\\` comment lines: effect, doc, span,
          and tier-2 compilation info.
        """

        xt = vm.pop()

        def _meta_lines_for_word(w: Word, *, code: Code | None = None) -> list[str]:
            out: list[str] = []
            eff = str(word_effect(w) or "").strip()
            if eff:
                out.append(f"\\ effect {eff}")
            doc = str(word_doc_summary(w) or "").strip()
            if doc:
                for line in doc.splitlines():
                    line = line.strip()
                    if line:
                        out.append(f"\\ doc {line}")
            sp = getattr(w, "span", None)
            if sp is not None:
                out.append(f"\\ defined at {sp.filename}:{sp.line}:{sp.col}")
            if code is not None and code.bytecode is not None:
                bc = code.bytecode
                out.append(f"\\ compiled {len(bc.instrs)} insns, {len(bc.consts)} consts")
            return out

        if isinstance(xt, Quotation):
            body = " ".join(_tok_to_src(t) for t in xt.code.tokens)
            lines = [f"[ {body} ]"]
            sp = getattr(xt, "span", None)
            if sp is not None:
                lines.append(f"\\ defined at {sp.filename}:{sp.line}:{sp.col}")
            if xt.code.bytecode is not None:
                bc = xt.code.bytecode
                lines.append(f"\\ compiled {len(bc.instrs)} insns, {len(bc.consts)} consts")
            vm.stack.append("\n".join(lines))
            return

        if isinstance(xt, ColonWord):
            body = " ".join(_tok_to_src(t) for t in xt.code.tokens)
            lines = [f": {xt.name} {body} ;"]
            lines.extend(_meta_lines_for_word(xt, code=xt.code))
            vm.stack.append("\n".join(lines))
            return

        if isinstance(xt, PrimitiveWord):
            lines = [f"{xt.name} <primitive>"]
            # primitives can still carry doc/effect metadata
            lines.extend(_meta_lines_for_word(xt, code=None))
            vm.stack.append("\n".join(lines))
            return

        if isinstance(xt, DeferredWord):
            tgt = xt.cell.value
            tgt_name = getattr(tgt, "name", "<quote>") if tgt is not None else "<unset>"
            lines = [f"defer {xt.name} (is {tgt_name})"]
            lines.extend(_meta_lines_for_word(xt, code=None))
            vm.stack.append("\n".join(lines))
            return

        if isinstance(xt, HookWord):
            hs = [_hook_handler_desc(h) for h in xt.handlers]
            lines = [f"hook {xt.name} handlers: {', '.join(hs) if hs else '(none)'}"]
            lines.extend(_meta_lines_for_word(xt, code=None))
            vm.stack.append("\n".join(lines))
            return

        if isinstance(xt, Word):
            lines = [f"{xt.name} <word>"]
            lines.extend(_meta_lines_for_word(xt, code=None))
            vm.stack.append("\n".join(lines))
            return

        raise MicromaxError("xt-src: expected execution token")

    def w_xt_src_rows(vm: VM) -> None:
        """( xt -- rows ) Return structured source-ish rows for xt.

        Returns `[[text kind span|0] ...]` where:
        - `text` is one line of `xt-src`
        - `kind` is one of: def|effect|doc|span|compiled|meta
        - `span` is `[filename line col]` (1-based) or 0

        This is a tiny, UI-friendly companion to `xt-src`: UIs and tooling can
        render rows without parsing the free-form `xt-src` string.
        """

        xt = vm.pop()

        def _span_list(sp: Span | None) -> object:
            if sp is None:
                return 0
            return [str(sp.filename), int(sp.line), int(sp.col)]

        def _classify(line: str, i: int) -> str:
            if i == 0:
                return "def"
            if line.startswith("\\ effect"):
                return "effect"
            if line.startswith("\\ doc"):
                return "doc"
            if line.startswith("\\ defined at"):
                return "span"
            if line.startswith("\\ compiled"):
                return "compiled"
            return "meta"

        def _meta_lines_for_word(w: Word, *, code: Code | None = None) -> list[str]:
            out: list[str] = []
            eff = str(word_effect(w) or "").strip()
            if eff:
                out.append(f"\\ effect {eff}")
            doc = str(word_doc_summary(w) or "").strip()
            if doc:
                for line in doc.splitlines():
                    line = line.strip()
                    if line:
                        out.append(f"\\ doc {line}")
            sp = getattr(w, "span", None)
            if sp is not None:
                out.append(f"\\ defined at {sp.filename}:{sp.line}:{sp.col}")
            if code is not None and code.bytecode is not None:
                bc = code.bytecode
                out.append(f"\\ compiled {len(bc.instrs)} insns, {len(bc.consts)} consts")
            return out

        # Build lines in the same order as `xt-src`.
        base_span: Span | None = None
        lines: list[str] = []

        if isinstance(xt, Quotation):
            body = " ".join(_tok_to_src(t) for t in xt.code.tokens)
            lines = [f"[ {body} ]"]
            base_span = getattr(xt, "span", None)
            if base_span is not None:
                lines.append(f"\\ defined at {base_span.filename}:{base_span.line}:{base_span.col}")
            if xt.code.bytecode is not None:
                bc = xt.code.bytecode
                lines.append(f"\\ compiled {len(bc.instrs)} insns, {len(bc.consts)} consts")

        elif isinstance(xt, ColonWord):
            body = " ".join(_tok_to_src(t) for t in xt.code.tokens)
            lines = [f": {xt.name} {body} ;"]
            base_span = getattr(xt, "span", None)
            lines.extend(_meta_lines_for_word(xt, code=xt.code))

        elif isinstance(xt, PrimitiveWord):
            lines = [f"{xt.name} <primitive>"]
            base_span = getattr(xt, "span", None)
            lines.extend(_meta_lines_for_word(xt, code=None))

        elif isinstance(xt, DeferredWord):
            tgt = xt.cell.value
            tgt_name = getattr(tgt, "name", "<quote>") if tgt is not None else "<unset>"
            lines = [f"defer {xt.name} (is {tgt_name})"]
            base_span = getattr(xt, "span", None)
            lines.extend(_meta_lines_for_word(xt, code=None))

        elif isinstance(xt, HookWord):
            hs = [_hook_handler_desc(h) for h in xt.handlers]
            lines = [f"hook {xt.name} handlers: {', '.join(hs) if hs else '(none)'}"]
            base_span = getattr(xt, "span", None)
            lines.extend(_meta_lines_for_word(xt, code=None))

        elif isinstance(xt, Word):
            lines = [f"{xt.name} <word>"]
            base_span = getattr(xt, "span", None)
            lines.extend(_meta_lines_for_word(xt, code=None))

        else:
            raise MicromaxError("xt-src-rows: expected execution token")

        rows: list[list[object]] = []
        for i, line in enumerate(lines):
            kind = _classify(line, i)
            # Use the XT's base span for definition + human metadata rows.
            sp = base_span if kind in ("def", "effect", "doc", "span", "meta") else None
            rows.append([str(line), str(kind), _span_list(sp)])
        vm.stack.append(rows)


    def w_xt_span(vm: VM) -> None:
        """( xt -- span|0 ) Return source span for xt.

        If known, returns `[filename line col]` (1-based line/col).
        Otherwise returns 0.
        """

        xt = vm.pop()
        sp = None
        if isinstance(xt, Quotation):
            sp = xt.span
        elif isinstance(xt, ColonWord):
            sp = xt.span
        elif isinstance(xt, HookWord):
            sp = xt.span
        if sp is None:
            vm.stack.append(0)
            return
        vm.stack.append([str(sp.filename), int(sp.line), int(sp.col)])


    def w_here_span(vm: VM) -> None:
        """( -- span|0 ) Return the current execution span.

        If known, returns `[filename line col]` (1-based line/col).
        Otherwise returns 0.

        This is best-effort debugging/provenance intended for embeddings.
        """

        sp = getattr(vm, "last_span", None)
        if sp is None:
            vm.stack.append(0)
            return
        vm.stack.append([str(sp.filename), int(sp.line), int(sp.col)])


    def w_if(vm: VM) -> None:
        qfalse = vm.pop_quote()
        qtrue = vm.pop_quote()
        flag = vm.pop_int()
        vm.exec_xt(qtrue if flag != 0 else qfalse)

    def w_when(vm: VM) -> None:
        q = vm.pop_quote()
        flag = vm.pop_int()
        if flag != 0:
            vm.exec_xt(q)

    def w_while(vm: VM) -> None:
        qbody = vm.pop_quote()
        qcond = vm.pop_quote()
        while True:
            vm.exec_xt(qcond)
            flag = vm.pop_int()
            if flag == 0:
                break
            vm.exec_xt(qbody)

    # ----- small combinators (rev12) -----
    def w_throw(vm: VM) -> None:
        code = vm.pop_int()
        if code != 0:
            msg = "THROW"
            if vm.last_error is not None and str(vm.last_error):
                msg = str(vm.last_error)
            raise MicromaxError(msg, code=code)

    def w_catch(vm: VM) -> None:
        q = vm.pop_quote()
        saved = list(vm.stack)
        try:
            vm.exec_xt(q)
            vm.stack.append(0)
        except MicromaxError as e:
            # restore stack to what it was at CATCH entry (after removing q)
            vm.stack[:] = saved
            vm.last_error = e
            vm.stack.append(e.code if e.code != 0 else -1)

    def w_last_error(vm: VM) -> None:
        if vm.last_error is None:
            vm.stack.append("")
            return
        vm.stack.append(vm.format_error(vm.last_error))

    def w_last_error_dot(vm: VM) -> None:
        if vm.last_error is None:
            return
        print(vm.format_error(vm.last_error))

    # ----- execution budgets (safety) -----
    def w_set_budget(vm: VM) -> None:
        """( n -- ) Set the *base* step budget. n<0 clears budgets (unlimited)."""
        n = vm.pop_int()
        if n < 0:
            vm._budget_stack.clear()
            return
        vm._budget_stack[:] = [n]

    def w_budget(vm: VM) -> None:
        """( -- n depth ) Report innermost remaining budget and budget depth."""
        if not vm._budget_stack:
            vm.stack.append(-1)
            vm.stack.append(0)
            return
        vm.stack.append(vm._budget_stack[-1])
        vm.stack.append(len(vm._budget_stack))

    def w_with_budget(vm: VM) -> None:
        """( n q -- ) Execute quotation with an additional step budget."""
        q = vm.pop_quote()
        n = vm.pop_int()
        if n < 0:
            raise MicromaxError("with-budget: n must be >= 0")
        vm._budget_stack.append(n)
        try:
            vm.exec_xt(q)
        finally:
            vm._budget_stack.pop()

    # ----- wordlists / search order (namespace hygiene) -----
    def w_wordlist(vm: VM) -> None:
        vm.stack.append(vm.new_wordlist())

    def w_set_current(vm: VM) -> None:
        wid = vm.pop_int()
        if wid not in vm.wordlists:
            raise MicromaxError(f"Unknown wordlist id {wid}")
        vm.current_wid = wid

    def w_get_current(vm: VM) -> None:
        vm.stack.append(vm.current_wid)

    def w_set_order(vm: VM) -> None:
        n = vm.pop_int()
        if n == -1:
            vm.set_search_order([vm.forth_wid])
            return
        if n < 0:
            raise MicromaxError("set-order: n must be >=0 or -1")
        if len(vm.stack) < n:
            raise MicromaxError("set-order: stack underflow")
        wids = [vm.pop_int() for _ in range(n)]  # wid1..widn
        for wid in wids:
            if wid not in vm.wordlists:
                raise MicromaxError(f"set-order: unknown wordlist id {wid}")
        vm.set_search_order(wids)

    def w_get_order(vm: VM) -> None:
        # push wid_n ... wid_1 n
        for wid in reversed(vm.search_order):
            vm.stack.append(wid)
        vm.stack.append(len(vm.search_order))

    def w_only(vm: VM) -> None:
        vm.set_search_order([vm.forth_wid])

    def w_also(vm: VM) -> None:
        if not vm.search_order:
            vm.set_search_order([vm.forth_wid])
        else:
            vm.set_search_order([vm.search_order[0]] + vm.search_order)

    def w_previous(vm: VM) -> None:
        if vm.search_order:
            vm.set_search_order(vm.search_order[1:])

    def w_definitions(vm: VM) -> None:
        # set CURRENT to the first searched wordlist
        if not vm.search_order:
            vm.current_wid = vm.forth_wid
        else:
            vm.current_wid = vm.search_order[0]

    # ----- defining words: constant / variable -----
    def w_constant(vm: VM) -> None:
        name = vm.expect_word_name()
        val = vm.pop()

        def push_const(vm2: VM, v=val) -> None:
            vm2.stack.append(v)

        vm.define_primitive(name, push_const, doc=f"( -- {type(val).__name__} ) constant", wid=vm.current_wid)

    def w_variable(vm: VM) -> None:
        name = vm.expect_word_name()
        cell = Cell(0)

        def push_cell(vm2: VM, c=cell) -> None:
            vm2.stack.append(c)

        vm.define_primitive(name, push_cell, doc="( -- cell ) variable", wid=vm.current_wid)

    def w_fetch(vm: VM) -> None:
        cell = vm.pop_cell()
        vm.stack.append(cell.value)

    def w_store(vm: VM) -> None:
        cell = vm.pop_cell()
        val = vm.pop()
        cell.value = val

    # ----- host bridge -----
    def w_hostcall(vm: VM) -> None:
        name = vm.pop_str()
        fn = vm.host_fns.get(name)
        if fn is None:
            raise MicromaxError(f"Unknown hostcall: {name}")
        fn(vm)

    # ----- host API contract -----
    def w_host_api_version(vm: VM) -> None:
        vm.stack.append(vm.host_api_version)

    def w_host_feature_q(vm: VM) -> None:
        feat = vm.pop_str()
        vm.stack.append(1 if feat in vm.host_features else 0)

    def w_host_features(vm: VM) -> None:
        vm.stack.append(sorted(list(vm.host_features)))

    # ----- message send (dynamic word invocation) -----
    def w_send(vm: VM) -> None:
        """( name -- ) Execute a word by its name (string).

        This pairs with postfix sugar in the VM: `.foo` expands to `"foo" send`.
        """
        name = vm.pop_str()
        w = vm.find_word(name)
        if w is None:
            raise MicromaxError(f"send: unknown word: {name}")
        vm.callstack.append(f"send:{name}")
        try:
            w.execute(vm)
        finally:
            vm.callstack.pop()

    def w_responds_q(vm: VM) -> None:
        """( name -- flag ) Return 1 if a word with this name exists."""
        name = vm.pop_str()
        vm.stack.append(1 if vm.find_word(name) is not None else 0)

    # ----- dictionary / compilation helpers -----
    def w_find(vm: VM) -> None:
        """( "name" -- xt|0 ) Find a word by string name (0 if missing)."""
        name = vm.pop_str()
        w = vm.find_word(name)
        vm.stack.append(w if w is not None else 0)

    def w_error(vm: VM) -> None:
        """( "msg" -- ) Raise a VM error with the given message."""
        msg = vm.pop_str()
        raise MicromaxError(msg)

    def w_dict_version(vm: VM) -> None:
        """( -- n ) Return the global dictionary/search-order version.

        This is bumped on any definition change or search-order mutation and is
        used to invalidate tier-2 call-site inline caches.
        """
        vm.stack.append(vm.dict_version)


    def w_bytecode_json(vm: VM) -> None:
        """( xt -- s ) Serialize xt's tier-2 bytecode to JSON.

        This compiles xt if needed.

        Note: this is tooling-oriented and not part of the minimal portable kernel.
        """

        xt = vm.pop_xt()
        vm.compile_xt(xt)
        code: Optional[Code] = None
        if isinstance(xt, Quotation):
            code = xt.code
        elif isinstance(xt, ColonWord):
            code = xt.code
        else:
            raise MicromaxError("bytecode-json: expected quotation or colon word")

        if code.bytecode is None:
            raise MicromaxError("bytecode-json: no bytecode attached")
        vm.stack.append(vm.bytecode_to_json(code.bytecode))

    def w_bytecode_load_json(vm: VM) -> None:
        """( s -- q ) Parse bytecode JSON into a quotation.

        The returned quotation has no tier-1 tokens, only tier-2 bytecode.
        """

        s = vm.pop_str()
        vm.stack.append(vm.quote_from_bytecode_json(s))

    def w_compile(vm: VM) -> None:
        """( xt -- xt ) Compile quotation/colonword to tier-2 bytecode (best effort)."""
        xt = vm.pop_xt()
        vm.compile_xt(xt)
        vm.stack.append(xt)

    def w_compiled_q(vm: VM) -> None:
        """( xt -- flag ) 1 if xt currently has tier-2 bytecode attached."""
        xt = vm.pop()
        if isinstance(xt, Quotation):
            vm.stack.append(1 if xt.code.bytecode is not None else 0)
            return
        if isinstance(xt, ColonWord):
            vm.stack.append(1 if xt.code.bytecode is not None else 0)
            return
        vm.stack.append(0)

    def w_disasm(vm: VM) -> None:
        """( xt -- ) Print tier-2 disassembly (if compiled)."""
        xt = vm.pop_xt()
        code: Optional[Code] = None
        label = getattr(xt, 'name', '<xt>')
        if isinstance(xt, Quotation):
            code = xt.code
            label = '<quote>'
        elif isinstance(xt, ColonWord):
            code = xt.code
            label = xt.name
        else:
            print(f"{label}: primitive")
            return
        if code.bytecode is None:
            print(f"{label}: (uncompiled) {len(code.tokens)} tokens")
            return
        bc = code.bytecode
        assert bc is not None
        print(f"{label}: {len(bc.instrs)} insns, {len(bc.consts)} consts")
        for i, ins in enumerate(bc.instrs):
            sp = ins.span

            # For jumps, the operand is a relative offset, not a const index.
            if ins.op in ("JMP", "JZ"):
                off = int(ins.arg or 0)
                tgt = i + 1 + off
                arg_s = f"{off:+d} -> {tgt:04d}"
                print(f"{i:04d} {ins.op:9} {arg_s:<22} ; {sp.filename}:{sp.line}:{sp.col}")
                continue

            arg = None
            if ins.arg is not None:
                try:
                    arg = bc.consts[int(ins.arg)]
                except Exception:
                    arg = ins.arg

            if isinstance(arg, Quotation):
                arg_s = f"[{len(arg.code.tokens)}t{'*' if arg.code.bytecode else ''}]"
            elif hasattr(arg, 'name') and type(arg).__name__ == 'WordRef':
                arg_s = str(getattr(arg, 'name'))
            else:
                arg_s = repr(arg)
            print(f"{i:04d} {ins.op:9} {arg_s:<22} ; {sp.filename}:{sp.line}:{sp.col}")

        if bc.consts:
            print("consts:")
            for i, c in enumerate(bc.consts):
                if isinstance(c, Quotation):
                    cs = f"[{len(c.code.tokens)}t{'*' if c.code.bytecode else ''}]"
                elif hasattr(c, 'name') and type(c).__name__ == 'WordRef':
                    cs = str(getattr(c, 'name'))
                else:
                    cs = repr(c)
                print(f"  [{i}] {cs}")

    def w_disasm_rows(vm: VM) -> None:
        """( xt -- rows|0 ) Return a structured tier-2 disassembly.

        Returns 0 if xt is uncompiled or not disassemblable.

        Each row is: ``[pc op arg span]`` where:
        - ``pc`` is an int program counter
        - ``op`` is an opcode string
        - ``arg`` is:
            - for JMP/JZ: signed relative offset
            - otherwise: the constant value (from the const pool)
            - 0 if the instruction has no argument
        - ``span`` is ``[file line col]`` or 0

        This is UI/tooling-friendly: renderers do not need to parse the free-form
        string output of `disasm`.
        """

        xt = vm.pop_xt()
        code: Optional[Code] = None
        if isinstance(xt, Quotation):
            code = xt.code
        elif isinstance(xt, ColonWord):
            code = xt.code
        else:
            vm.stack.append(0)
            return

        if code.bytecode is None:
            vm.stack.append(0)
            return

        bc = code.bytecode
        assert bc is not None
        rows: list[list[object]] = []
        for pc, ins in enumerate(bc.instrs):
            sp = ins.span
            span_obj: object = [str(sp.filename), int(sp.line), int(sp.col)] if sp is not None else 0
            if ins.op in ("JMP", "JZ"):
                arg_obj: object = int(ins.arg or 0)
            elif ins.arg is None:
                arg_obj = 0
            else:
                try:
                    arg_obj = bc.consts[int(ins.arg)]
                except Exception:
                    arg_obj = int(ins.arg)
            rows.append([int(pc), str(ins.op), arg_obj, span_obj])
        vm.stack.append(rows)

    # ----- locals helpers -----
    def w_locals(vm: VM) -> None:
        """( -- ) Print locals visible in the current frame (debug)."""
        names = sorted(vm.locals_stack[-1].keys())
        if not names:
            print("(locals: <none>)")
            return
        print("(locals:", " ".join(names) + ")")

    def w_local_fetch(vm: VM) -> None:
        """( -- x ) Parse a name and push its local value."""
        name = vm.expect_word_name()
        val = vm._lookup_local(name)
        if val is None:
            raise MicromaxError(f"local@: unknown local: {name}")
        vm.stack.append(val)

    def w_local_q(vm: VM) -> None:
        """( -- x flag ) Parse a name and check if it exists as a local."""
        name = vm.expect_word_name()
        val = vm._lookup_local(name)
        if val is None:
            vm.stack.append(0)
            vm.stack.append(0)
        else:
            vm.stack.append(val)
            vm.stack.append(1)

    def w_local_store(vm: VM) -> None:
        """( x -- ) Parse a name and store x into the current locals frame."""
        name = vm.expect_word_name()
        x = vm.pop()
        vm._set_local(name, x)

    def w_unlocal(vm: VM) -> None:
        """( -- ) Parse a name and remove it from the current locals frame."""
        name = vm.expect_word_name()
        vm._del_local(name)

    def w_locals_clear(vm: VM) -> None:
        """( -- ) Clear the persistent session locals (not call frames)."""
        vm._clear_session_locals()


    # ----- lists (host values) -----
    def w_list(vm: VM) -> None:
        vm.stack.append([])

    def w_push(vm: VM) -> None:
        lst = vm.pop_list()
        x = vm.pop()
        lst.append(x)
        vm.stack.append(lst)

    def w_pop(vm: VM) -> None:
        lst = vm.pop_list()
        if not lst:
            raise MicromaxError("Empty list")
        vm.stack.append(lst.pop())
        vm.stack.append(lst)

    def w_len(vm: VM) -> None:
        lst = vm.pop_list()
        vm.stack.append(len(lst))

    def w_nth(vm: VM) -> None:
        lst = vm.pop_list()
        n = vm.pop_int()
        try:
            vm.stack.append(lst[n])
        except Exception as e:
            raise MicromaxError("Index out of range") from e

    def w_set_nth(vm: VM) -> None:
        lst = vm.pop_list()
        n = vm.pop_int()
        x = vm.pop()
        try:
            lst[n] = x
        except Exception as e:
            raise MicromaxError("Index out of range") from e
        vm.stack.append(lst)

    def w_clone(vm: VM) -> None:
        x = vm.pop()
        if isinstance(x, list):
            vm.stack.append(list(x))
        elif isinstance(x, dict):
            vm.stack.append(dict(x))
        else:
            vm.stack.append(x)

    # ----- maps (portable dicts; string keys) -----
    def w_map(vm: VM) -> None:
        """( -- map ) Create an empty map."""
        vm.stack.append({})

    def w_map_q(vm: VM) -> None:
        """( x -- flag ) 1 if x is a map."""
        x = vm.pop()
        vm.stack.append(1 if isinstance(x, dict) else 0)

    def _pop_map_key(vm: VM) -> tuple[dict, str]:
        m = vm.pop_map()
        k = vm.pop_str()
        return m, k

    def w_m_fetch(vm: VM) -> None:
        """( key map -- val|0 ) Fetch value (0 if missing)."""
        m, k = _pop_map_key(vm)
        vm.stack.append(m.get(k, 0))

    def w_m_has(vm: VM) -> None:
        """( key map -- flag ) 1 if key exists."""
        m, k = _pop_map_key(vm)
        vm.stack.append(1 if k in m else 0)

    def w_m_store(vm: VM) -> None:
        """( val key map -- map ) Store val at key (mutates map)."""
        m = vm.pop_map()
        k = vm.pop_str()
        v = vm.pop()
        m[k] = v
        vm.stack.append(m)

    def w_m_del(vm: VM) -> None:
        """( key map -- map ) Delete key if present (mutates map)."""
        m, k = _pop_map_key(vm)
        m.pop(k, None)
        vm.stack.append(m)

    def w_m_keys(vm: VM) -> None:
        """( map -- keys ) Return sorted list of keys."""
        m = vm.pop_map()
        vm.stack.append(sorted([str(k) for k in m.keys()]))

    def w_m_items(vm: VM) -> None:
        """( map -- items ) Return [[key val] ...] sorted by key."""
        m = vm.pop_map()
        out: list[list[object]] = []
        for k in sorted([str(k) for k in m.keys()]):
            out.append([k, m.get(k)])
        vm.stack.append(out)

    def w_m_merge(vm: VM) -> None:
        """( src dst -- dst ) Merge all entries from src into dst (mutates dst)."""
        dst = vm.pop_map()
        src = vm.pop_map()
        for k, v in src.items():
            dst[str(k)] = v
        vm.stack.append(dst)

    # ----- hooks (multi-handler callbacks) -----
    def _hook_handler_xt(h: Any) -> Any:
        return h.xt if isinstance(h, HookHandler) else h

    def _hook_handler_span(h: Any) -> Any:
        return h.span if isinstance(h, HookHandler) else None

    def _hook_handler_group(h: Any) -> str | None:
        return h.group if isinstance(h, HookHandler) else None

    def _hook_handler_name(h: Any) -> str:
        return getattr(_hook_handler_xt(h), "name", "<quote>")

    def _hook_handler_rows(hw: HookWord) -> list[list[Any]]:
        rows: list[list[Any]] = []
        for h in hw.handlers:
            sp = _hook_handler_span(h)
            span = 0 if sp is None else [str(sp.filename), int(sp.line), int(sp.col)]
            rows.append([_hook_handler_name(h), span])
        return rows

    def _hook_handler_detail_rows(hw: HookWord) -> list[list[Any]]:
        rows: list[list[Any]] = []
        for h in hw.handlers:
            sp = _hook_handler_span(h)
            span = 0 if sp is None else [str(sp.filename), int(sp.line), int(sp.col)]
            group = _hook_handler_group(h)
            rows.append([_hook_handler_name(h), str(group) if group else 0, span])
        return rows

    def _hook_handler_desc(h: Any) -> str:
        hs = _hook_handler_name(h)
        group = _hook_handler_group(h)
        sp = _hook_handler_span(h)
        if group:
            hs += f"#{group}"
        if sp is not None:
            hs += f"@{sp.filename}:{sp.line}:{sp.col}"
        return hs

    def w_hook(vm: VM) -> None:
        name = vm.expect_word_name()
        sp = getattr(vm, "last_span", None)
        hw = HookWord(name=name, handlers=[], doc="( -- ) hook", span=sp)
        vm._add_word(vm.current_wid, hw)

    def _expect_hook(vm: VM, name: str) -> HookWord:
        w = vm.find_word(name)
        if not isinstance(w, HookWord):
            raise MicromaxError(f"Expected hook word: {name}")
        return w

    def w_hook_add(vm: VM) -> None:
        xt = vm.pop()
        name = vm.expect_word_name()
        hw = _expect_hook(vm, name)
        sp = getattr(vm, "last_span", None)
        group = getattr(vm, "current_hook_group", None)
        hw.handlers.append(HookHandler(xt=xt, span=sp, group=group))

    def w_hook_remove(vm: VM) -> None:
        xt = vm.pop()
        name = vm.expect_word_name()
        hw = _expect_hook(vm, name)
        hw.handlers = [h for h in hw.handlers if _hook_handler_xt(h) is not xt]

    def w_hook_clear(vm: VM) -> None:
        name = vm.expect_word_name()
        hw = _expect_hook(vm, name)
        hw.handlers.clear()

    def w_hook_fetch(vm: VM) -> None:
        name = vm.expect_word_name()
        hw = _expect_hook(vm, name)
        vm.stack.append([_hook_handler_xt(h) for h in hw.handlers])

    def w_hook_rows(vm: VM) -> None:
        """( -- rows ) Parse hook name; return [[handler-name [file line col]|0] ...]."""
        name = vm.expect_word_name()
        hw = _expect_hook(vm, name)
        vm.stack.append(_hook_handler_rows(hw))

    def w_hook_detail(vm: VM) -> None:
        """( -- rows ) Parse hook name; return [[handler-name group|0 span|0] ...]."""
        name = vm.expect_word_name()
        hw = _expect_hook(vm, name)
        vm.stack.append(_hook_handler_detail_rows(hw))

    def w_hook_groups(vm: VM) -> None:
        """( -- groups ) Parse hook name; return sorted unique handler groups."""
        name = vm.expect_word_name()
        hw = _expect_hook(vm, name)
        groups = sorted({g for g in (_hook_handler_group(h) for h in hw.handlers) if g})
        vm.stack.append(groups)

    def w_hook_remove_group(vm: VM) -> None:
        """( group -- n ) Parse hook name; remove handlers in a group."""
        group = vm.pop()
        if group == 0 or group is None:
            target = None
        else:
            target = str(group)
        name = vm.expect_word_name()
        hw = _expect_hook(vm, name)
        before = len(hw.handlers)
        hw.handlers = [h for h in hw.handlers if _hook_handler_group(h) != target]
        vm.stack.append(before - len(hw.handlers))

    def w_hook_group_store(vm: VM) -> None:
        """( group|0 -- ) Set the default hook registration group (0 clears)."""
        group = vm.pop()
        if group == 0 or group is None or group == "":
            vm.current_hook_group = None
            return
        vm.current_hook_group = str(group)

    def w_hook_group_fetch(vm: VM) -> None:
        """( -- group|0 ) Return the default hook registration group."""
        vm.stack.append(str(vm.current_hook_group) if vm.current_hook_group else 0)

    def w_hooks(vm: VM) -> None:
        names = []
        for wid, wl in vm.wordlists.items():
            for n, w in wl.items():
                if isinstance(w, HookWord):
                    names.append(f"{n} [{wid}:{vm.wordlist_names.get(wid,'?')}]")
        for n in sorted(names):
            print(n)

    # ----- modules (named wordlists) -----
    def w_module(vm: VM) -> None:
        name = vm.expect_word_name()
        if name in vm.modules:
            raise MicromaxError(f"Module already exists: {name}")
        prev_current = vm.current_wid
        prev_order = list(vm.search_order)
        wid = vm.new_wordlist(name)
        vm.modules[name] = wid
        vm.current_wid = wid
        vm.set_search_order([wid] + vm.search_order)
        vm._module_stack.append((prev_current, prev_order))

    def w_endmodule(vm: VM) -> None:
        if not vm._module_stack:
            raise MicromaxError("endmodule without module")
        prev_current, prev_order = vm._module_stack.pop()
        vm.current_wid = prev_current
        vm.set_search_order(prev_order)

    def w_use(vm: VM) -> None:
        name = vm.expect_word_name()
        wid = vm.modules.get(name)
        if wid is None:
            raise MicromaxError(f"Unknown module: {name}")
        if wid not in vm.search_order:
            vm.set_search_order([wid] + vm.search_order)

    def w_in(vm: VM) -> None:
        name = vm.expect_word_name()
        wid = vm.modules.get(name)
        if wid is None:
            raise MicromaxError(f"Unknown module: {name}")
        vm.current_wid = wid

    def w_modules(vm: VM) -> None:
        for name in sorted(vm.modules.keys()):
            wid = vm.modules[name]
            print(f"{name}: {wid}:{vm.wordlist_names.get(wid,'?')}")

    # ----- file loading -----
    def w_include(vm: VM) -> None:
        path = vm.pop_str()
        resolved = vm.resolve_load_path(path, span=vm.last_span)
        with open(resolved, "r", encoding="utf-8") as f:
            vm.eval(f.read(), filename=resolved)

    def w_require(vm: VM) -> None:
        path = vm.pop_str()
        abspath = vm.resolve_load_path(path, span=vm.last_span)
        if abspath in vm.loaded_paths:
            return
        vm.loaded_paths.add(abspath)
        with open(abspath, "r", encoding="utf-8") as f:
            vm.eval(f.read(), filename=abspath)

    def w_reload(vm: VM) -> None:
        """( path -- ) Load a file even if it was previously `require`d.

        This is a simple building block for hot-reloadable configs/plugins.
        """
        path = vm.pop_str()
        abspath = vm.resolve_load_path(path, span=vm.last_span)
        vm.loaded_paths.add(abspath)
        with open(abspath, "r", encoding="utf-8") as f:
            vm.eval(f.read(), filename=abspath)

    def w_unrequire(vm: VM) -> None:
        """( path -- ) Forget a previously `require`d path (by resolved absolute path).

        This is best-effort: if the file no longer exists, we fall back to the
        current working directory resolution for relative paths.
        """
        import os

        path = vm.pop_str()
        try:
            abspath = vm.resolve_load_path(path, span=vm.last_span)
        except Exception:
            abspath = os.path.abspath(os.path.expanduser(str(path)))
        vm.loaded_paths.discard(abspath)

    # ----- repl convenience -----
    def w_bye(vm: VM) -> None:
        raise SystemExit(0)

    # Register
    vm.define_primitive(".", w_dot, doc="( x -- ) print top of stack", wid=install_wid)
    vm.define_primitive("cr", w_cr, doc="( -- ) newline", wid=install_wid)
    vm.define_primitive("emit", w_emit, doc="( n -- ) print character", wid=install_wid)
    vm.define_primitive(".s", w_dots, doc="( -- ) print stack", wid=install_wid)

    vm.define_primitive("callstack", w_callstack, doc="( -- xs ) return current callstack (debug)", wid=install_wid)
    vm.define_primitive("trace", w_callstack, doc="( -- xs ) alias for callstack", wid=install_wid)

    vm.define_primitive("words", w_words, doc="( -- ) list words in current search order", wid=install_wid)
    vm.define_primitive("words-list", w_words_list, doc="( -- names ) list word names in current search order", wid=install_wid)
    vm.define_primitive("words-rows", w_words_rows, doc="( -- rows ) list visible word rows [name kind effect doc wid wl]", wid=install_wid)
    vm.define_primitive("wid-words", w_wid_words, doc="( wid -- names ) list word names in a wordlist", wid=install_wid)
    vm.define_primitive("wid-word-rows", w_wid_word_rows, doc="( wid -- rows ) list word rows [name kind effect doc wid wl] in a wordlist", wid=install_wid)
    vm.define_primitive("wid-name", w_wid_name, doc="( wid -- s ) friendly wordlist name", wid=install_wid)
    vm.define_primitive("see", w_see, doc="( -- ) parse next name; show its definition", wid=install_wid)
    vm.define_primitive("help", w_help, doc="( -- ) parse next name; show documentation", wid=install_wid)
    vm.define_primitive("where", w_where, doc="( -- ) parse next name; show defining wordlist", wid=install_wid)
    vm.define_primitive("order", w_order, doc="( -- ) print search order + current wordlist", wid=install_wid)

    vm.define_primitive("dup", w_dup, wid=install_wid, effect="( x -- x x )")
    vm.define_primitive("drop", w_drop, wid=install_wid, effect="( x -- )")
    vm.define_primitive("swap", w_swap, wid=install_wid, effect="( a b -- b a )")
    vm.define_primitive("over", w_over, wid=install_wid, effect="( a b -- a b a )")
    vm.define_primitive("rot", w_rot, wid=install_wid, effect="( a b c -- b c a )")
    vm.define_primitive("depth", w_depth, wid=install_wid, effect="( -- n )")
    vm.define_primitive("clear", w_clear, wid=install_wid, effect="( -- )")
    vm.define_primitive("pick", w_pick, wid=install_wid)
    vm.define_primitive("roll", w_roll, wid=install_wid)

    vm.define_primitive(">r", w_to_r, doc="( x -- ) move to return stack", wid=install_wid)
    vm.define_primitive("r>", w_r_from, doc="( -- x ) move from return stack", wid=install_wid)
    vm.define_primitive("r@", w_r_fetch, doc="( -- x ) copy top of return stack", wid=install_wid)
    vm.define_primitive("rdepth", w_rdepth, doc="( -- n ) return stack depth", wid=install_wid)

    vm.define_primitive("+", w_add, wid=install_wid, effect="( a b -- n )")
    vm.define_primitive("-", w_sub, wid=install_wid, effect="( a b -- n )")
    vm.define_primitive("*", w_mul, wid=install_wid, effect="( a b -- n )")
    vm.define_primitive("/", w_div, wid=install_wid, effect="( a b -- n )")
    vm.define_primitive("mod", w_mod, wid=install_wid, effect="( a b -- n )")

    vm.define_primitive("=", w_eq, wid=install_wid, effect="( a b -- flag )")
    vm.define_primitive("<", w_lt, wid=install_wid, effect="( a b -- flag )")
    vm.define_primitive(">", w_gt, wid=install_wid, effect="( a b -- flag )")
    vm.define_primitive("0=", w_0eq, wid=install_wid, effect="( n -- flag )")

    vm.define_primitive("int?", w_int_q, doc="( x -- flag ) 1 if x is an int", wid=install_wid)
    vm.define_primitive("str?", w_str_q, doc="( x -- flag ) 1 if x is a string", wid=install_wid)
    vm.define_primitive("list?", w_list_q, doc="( x -- flag ) 1 if x is a list", wid=install_wid)
    vm.define_primitive("quote?", w_quote_q, doc="( x -- flag ) 1 if x is a quotation", wid=install_wid)
    vm.define_primitive("xt?", w_xt_q, doc="( x -- flag ) 1 if x is an execution token", wid=install_wid)
    vm.define_primitive("s=", w_s_eq, doc="( a b -- flag ) typed string equality", wid=install_wid)
    vm.define_primitive("s<", w_s_lt, doc="( a b -- flag ) typed string less-than", wid=install_wid)
    vm.define_primitive("to-int", w_to_int, doc="( x -- n ) parse int (x is int or str)", wid=install_wid)
    vm.define_primitive("to-str", w_to_str, doc="( x -- s ) convert to string", wid=install_wid)

    vm.define_primitive("call", w_call, doc="( ..a q -- ..b ) execute quotation (q: ..a -- ..b)", wid=install_wid)
    vm.define_primitive("execute", w_execute, doc="( ..a xt -- ..b ) execute xt", wid=install_wid)
    vm.define_primitive("'", w_tick, doc="( -- xt ) parse next name; push xt", wid=install_wid)
    vm.define_primitive("defer", w_defer, doc="( -- ) parse next name; define deferred word", wid=install_wid)
    vm.define_primitive("is", w_is, doc="( xt -- ) parse deferred name; set it", wid=install_wid)
    vm.define_primitive("defer@", w_defer_fetch, doc="( dw -- xt|0 ) get deferred xt", wid=install_wid)
    vm.define_primitive("defer!", w_defer_store, doc="( xt dw -- ) set deferred xt", wid=install_wid)
    vm.define_primitive("xt-name", w_xt_name, doc="( xt -- s ) name of execution token", wid=install_wid)
    vm.define_primitive("xt-kind", w_xt_kind, doc="( xt -- s ) kind string for xt (primitive|colon|quote|...)", wid=install_wid)
    vm.define_primitive("xt-effect", w_xt_effect, doc="( xt -- s ) stack-effect string for xt", wid=install_wid)
    vm.define_primitive("stackcheck!", w_stackcheck_store, doc="( n -- ) set dev stack effect checking (0 off, 1 warn, 2 error)", wid=install_wid)
    vm.define_primitive("stackcheck@", w_stackcheck_fetch, doc="( -- n ) current stackcheck mode (0/1/2)", wid=install_wid)
    vm.define_primitive("infer-effect", w_infer_effect, doc="( xt -- s|0 ) infer a closed stack effect for straight-line code", wid=install_wid)
    vm.define_primitive("check-effect", w_check_effect, doc="( xt -- flag ) 1 if declared effect matches inferred", wid=install_wid)
    vm.define_primitive("xt-doc", w_xt_doc, doc="( xt -- s ) documentation string for xt", wid=install_wid)
    vm.define_primitive("xt-src", w_xt_src, doc="( xt -- s ) source-ish representation for xt", wid=install_wid)
    vm.define_primitive("xt-src-rows", w_xt_src_rows, doc="( xt -- rows ) structured source rows [[text kind span|0] ...]", wid=install_wid)
    vm.define_primitive("xt-span", w_xt_span, doc="( xt -- span|0 ) source span as [file line col] (or 0)", wid=install_wid)
    vm.define_primitive("here-span", w_here_span, doc="( -- span|0 ) current execution span as [file line col] (or 0)", wid=install_wid)
    vm.define_primitive("if", w_if, doc="( ..a flag qtrue qfalse -- ..b ) runtime if (qtrue/qfalse: ..a -- ..b)", wid=install_wid)
    vm.define_primitive("when", w_when, doc="( ..a flag q -- ..b ) execute q if flag!=0 (q: ..a -- ..b)", wid=install_wid)
    vm.define_primitive("while", w_while, doc="( ..a qcond qbody -- ..b ) loop (qcond: ..a -- ..a flag, qbody: ..a -- ..a)", wid=install_wid)


    vm.define_primitive("catch", w_catch, doc="( ..a q -- ..b ior ) execute q; on error restore entry stack and push ior", wid=install_wid)
    vm.define_primitive("throw", w_throw, doc="( ior -- ) raise error if ior != 0", wid=install_wid)
    vm.define_primitive("last-error", w_last_error, doc="( -- s ) formatted last error string", wid=install_wid)
    vm.define_primitive("error", w_error, doc='( "msg" -- ) raise a VM error', wid=install_wid)
    vm.define_primitive("dict-version", w_dict_version, doc="( -- n ) dictionary/search-order version", wid=install_wid)
    vm.define_primitive("last-error.", w_last_error_dot, doc="( -- ) print last error", wid=install_wid)

    vm.define_primitive("set-budget", w_set_budget, doc="( n -- ) set base step budget (-1 clears)", wid=install_wid)
    vm.define_primitive("budget", w_budget, doc="( -- n depth ) inspect budgets", wid=install_wid)
    vm.define_primitive("with-budget", w_with_budget, doc="( ..a n q -- ..b ) execute q with extra budget", wid=install_wid)

    vm.define_primitive("wordlist", w_wordlist, doc="( -- wid ) create a new wordlist", wid=install_wid)
    vm.define_primitive("set-current", w_set_current, doc="( wid -- ) set CURRENT wordlist", wid=install_wid)
    vm.define_primitive("get-current", w_get_current, doc="( -- wid ) get CURRENT wordlist", wid=install_wid)
    vm.define_primitive("set-order", w_set_order, doc="( wid_n ... wid_1 n -- ) set search order", wid=install_wid)
    vm.define_primitive("get-order", w_get_order, doc="( -- wid_n ... wid_1 n ) get search order", wid=install_wid)
    vm.define_primitive("only", w_only, doc="( -- ) set search order to FORTH only", wid=install_wid)
    vm.define_primitive("also", w_also, doc="( -- ) duplicate top of search order", wid=install_wid)
    vm.define_primitive("previous", w_previous, doc="( -- ) drop top of search order", wid=install_wid)
    vm.define_primitive("definitions", w_definitions, doc="( -- ) set CURRENT to top of search order", wid=install_wid)

    vm.define_primitive("constant", w_constant, doc="( x -- ) parse next name; define constant word", wid=install_wid)
    vm.define_primitive("variable", w_variable, doc="( -- ) parse next name; define variable word", wid=install_wid)
    vm.define_primitive("@", w_fetch, doc="( cell -- x ) fetch", wid=install_wid)
    vm.define_primitive("!", w_store, doc="( x cell -- ) store", wid=install_wid)

    vm.define_primitive("hostcall", w_hostcall, doc='( "name" -- ... ) call allowlisted host function', wid=install_wid)
    vm.define_primitive("host.api-version", w_host_api_version, doc="( -- s ) host API version string", wid=install_wid)
    vm.define_primitive("host.feature?", w_host_feature_q, doc='( "feat" -- flag ) 1 if host feature is available', wid=install_wid)
    vm.define_primitive("host.features", w_host_features, doc="( -- list ) list known host features", wid=install_wid)

    vm.define_primitive("send", w_send, doc='( "name" -- ) execute word by name (pairs with .name sugar)', wid=install_wid)
    vm.define_primitive("responds?", w_responds_q, doc='( "name" -- flag ) 1 if word exists', wid=install_wid)
    vm.define_primitive("find", w_find, doc='( "name" -- xt|0 ) find a word by string name (0 if missing)', wid=install_wid)

    vm.define_primitive("locals", w_locals, doc="( -- ) print current locals frame (debug)", wid=install_wid)
    vm.define_primitive("local@", w_local_fetch, doc="( -- x ) parse name; fetch local value", wid=install_wid)
    vm.define_primitive("local?", w_local_q, doc="( -- x flag ) parse name; check local", wid=install_wid)
    vm.define_primitive("local!", w_local_store, doc="( x -- ) parse name; store into locals", wid=install_wid)
    vm.define_primitive("unlocal", w_unlocal, doc="( -- ) parse name; remove from locals", wid=install_wid)
    vm.define_primitive("locals-clear", w_locals_clear, doc="( -- ) clear session locals", wid=install_wid)

    vm.define_primitive("see", w_see, doc="( -- ) parse next name; print definition", wid=install_wid)
    vm.define_primitive("compile", w_compile, doc="( xt -- xt ) compile quotation/colonword to tier-2 bytecode", wid=install_wid)
    vm.define_primitive("compiled?", w_compiled_q, doc="( xt -- flag ) 1 if xt has tier-2 bytecode", wid=install_wid)
    vm.define_primitive("disasm", w_disasm, doc="( xt -- ) disassemble compiled code (if any)", wid=install_wid)
    vm.define_primitive("disasm-rows", w_disasm_rows, doc="( xt -- rows|0 ) structured disassembly rows", wid=install_wid)
    vm.define_primitive("bytecode-json", w_bytecode_json, doc="( xt -- s ) serialize tier-2 bytecode as JSON", wid=install_wid)
    vm.define_primitive("bytecode-load-json", w_bytecode_load_json, doc="( s -- q ) parse bytecode JSON into a quotation", wid=install_wid)


    vm.define_primitive("map", w_map, doc="( -- map ) create an empty map", wid=install_wid)
    vm.define_primitive("map?", w_map_q, doc="( x -- flag ) 1 if x is a map", wid=install_wid)
    vm.define_primitive("m@", w_m_fetch, doc="( key map -- val|0 ) fetch (0 if missing)", wid=install_wid)
    vm.define_primitive("m?", w_m_has, doc="( key map -- flag ) 1 if key exists", wid=install_wid)
    vm.define_primitive("m!", w_m_store, doc="( val key map -- map ) store (mutates)", wid=install_wid)
    vm.define_primitive("m-del", w_m_del, doc="( key map -- map ) delete key (mutates)", wid=install_wid)
    vm.define_primitive("m-keys", w_m_keys, doc="( map -- keys ) sorted keys", wid=install_wid)
    vm.define_primitive("m-items", w_m_items, doc="( map -- items ) [[key val]...] sorted", wid=install_wid)
    vm.define_primitive("m-merge", w_m_merge, doc="( src dst -- dst ) merge (mutates dst)", wid=install_wid)

    vm.define_primitive("list", w_list, doc="( -- list ) create an empty list", wid=install_wid)
    vm.define_primitive("push", w_push, doc="( x list -- list ) append", wid=install_wid)
    vm.define_primitive("pop", w_pop, doc="( list -- x list ) pop last", wid=install_wid)
    vm.define_primitive("len", w_len, doc="( list -- n ) length", wid=install_wid)
    vm.define_primitive("nth", w_nth, doc="( n list -- x ) index", wid=install_wid)
    vm.define_primitive("set-nth", w_set_nth, doc="( x n list -- list ) store", wid=install_wid)
    vm.define_primitive("clone", w_clone, doc="( x -- x' ) shallow clone lists/dicts", wid=install_wid)

    vm.define_primitive("hook", w_hook, doc="( -- ) parse next name; define a hook", wid=install_wid)
    vm.define_primitive("hook-add", w_hook_add, doc="( xt -- ) parse hook name; add handler", wid=install_wid)
    vm.define_primitive("hook-rm", w_hook_remove, doc="( xt -- ) parse hook name; remove handler", wid=install_wid)
    vm.define_primitive("hook-clear", w_hook_clear, doc="( -- ) parse hook name; remove all", wid=install_wid)
    vm.define_primitive("hook@", w_hook_fetch, doc="( -- list ) parse hook name; get handlers", wid=install_wid)
    vm.define_primitive("hook-rows", w_hook_rows, doc="( -- rows ) parse hook name; get handler names + spans", wid=install_wid)
    vm.define_primitive("hook-detail", w_hook_detail, doc="( -- rows ) parse hook name; get handler names + groups + spans", wid=install_wid)
    vm.define_primitive("hook-groups", w_hook_groups, doc="( -- groups ) parse hook name; list handler groups", wid=install_wid)
    vm.define_primitive("hook-rm-group", w_hook_remove_group, doc="( group -- n ) parse hook name; remove grouped handlers", wid=install_wid)
    vm.define_primitive("hook-group!", w_hook_group_store, doc="( group|0 -- ) set default hook registration group", wid=install_wid)
    vm.define_primitive("hook-group@", w_hook_group_fetch, doc="( -- group|0 ) current default hook registration group", wid=install_wid)
    vm.define_primitive("hooks", w_hooks, doc="( -- ) list hooks", wid=install_wid)

    vm.define_primitive("module", w_module, doc="( -- ) parse name; create+enter module", wid=install_wid)
    vm.define_primitive("endmodule", w_endmodule, doc="( -- ) leave last module", wid=install_wid)
    vm.define_primitive("use", w_use, doc="( -- ) parse module; add to search order", wid=install_wid)
    vm.define_primitive("in", w_in, doc="( -- ) parse module; set CURRENT", wid=install_wid)
    vm.define_primitive("modules", w_modules, doc="( -- ) list known modules", wid=install_wid)

    vm.define_primitive("include", w_include, doc='( "path" -- ) load and eval file', wid=install_wid)
    vm.define_primitive("require", w_require, doc='( "path" -- ) load file once (absolute path)', wid=install_wid)
    vm.define_primitive("reload", w_reload, doc='( "path" -- ) force reload file', wid=install_wid)
    vm.define_primitive("unrequire", w_unrequire, doc='( "path" -- ) forget required file', wid=install_wid)
    vm.define_primitive("bye", w_bye, doc="( -- ) exit", wid=install_wid)
