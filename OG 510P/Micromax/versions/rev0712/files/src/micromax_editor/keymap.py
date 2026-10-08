from __future__ import annotations

from dataclasses import dataclass

from micromax.vm import Span


ChainSep = str  # one of ',', '|', '&'


@dataclass(frozen=True)
class ChainStep:
    """One step in a micro-style action chain.

    `sep` is the separator *after* this action ('' for the last action).
    """

    action: str
    sep: ChainSep


@dataclass(frozen=True)
class Binding:
    key: str
    action_spec: str
    span: Span | None = None
    group: str | None = None
    mode: str = "global"
    desc: str = ""


def parse_action_chain(spec: str) -> list[ChainStep]:
    """Parse a micro-style action chain.

    Micro supports `,` (always continue), `|` (abort if success), and `&` (abort
    if failure). Separators may be escaped with `\\` or wrapped in quotes.

    Source inspiration: micro runtime help/keybindings.md.

    We intentionally keep this parser small and dependency-free.
    """

    out: list[ChainStep] = []
    buf: list[str] = []

    in_single = False
    in_double = False
    escape = False

    def flush(sep: str) -> None:
        act = "".join(buf)
        act = act.lstrip()
        if act:
            out.append(ChainStep(action=act, sep=sep))
        buf.clear()

    for ch in spec:
        if escape:
            buf.append(ch)
            escape = False
            continue

        if ch == "\\":
            # Backslash escapes the next character (used to escape separators).
            escape = True
            continue

        if ch == "'" and not in_double:
            in_single = not in_single
            buf.append(ch)
            continue

        if ch == '"' and not in_single:
            in_double = not in_double
            buf.append(ch)
            continue

        if (not in_single) and (not in_double) and ch in [",", "|", "&"]:
            flush(ch)
            continue

        buf.append(ch)

    flush("")
    return out


class Keymap:
    def __init__(self) -> None:
        self._bindings: dict[str, dict[str, Binding]] = {"global": {}}

    def _norm_mode(self, mode: str | None) -> str:
        return str(mode) if mode else "global"

    def _mode_bindings(self, mode: str | None) -> dict[str, Binding]:
        m = self._norm_mode(mode)
        if m not in self._bindings:
            self._bindings[m] = {}
        return self._bindings[m]

    def _iter_bindings(self) -> list[Binding]:
        out: list[Binding] = []
        for mode in sorted(self._bindings.keys()):
            for key in sorted(self._bindings[mode].keys()):
                out.append(self._bindings[mode][key])
        return out

    def bind(
        self,
        key: str,
        action_spec: str,
        *,
        span: Span | None = None,
        group: str | None = None,
        mode: str | None = None,
        desc: str = "",
    ) -> None:
        m = self._norm_mode(mode)
        self._mode_bindings(m)[key] = Binding(key=key, action_spec=action_spec, span=span, group=group, mode=m, desc=str(desc))

    def unbind(self, key: str, *, mode: str | None = None) -> bool:
        m = self._norm_mode(mode)
        mb = self._bindings.get(m)
        if mb is None:
            return False
        ok = mb.pop(key, None) is not None
        if m != "global" and mb == {}:
            self._bindings.pop(m, None)
        return ok

    def lookup(self, key: str, *, modes: list[str] | None = None) -> str | None:
        b = self.get_binding(key, modes=modes)
        return None if b is None else b.action_spec

    def get_binding(self, key: str, modes: list[str] | None = None) -> Binding | None:
        if modes is None:
            return self._bindings.get("global", {}).get(key)
        seen: set[str] = set()
        order = [self._norm_mode(m) for m in modes] + ["global"]
        for mode in order:
            if mode in seen:
                continue
            seen.add(mode)
            b = self._bindings.get(mode, {}).get(key)
            if b is not None:
                return b
        return None


    def set_desc(self, key: str, desc: str, *, mode: str | None = None) -> bool:
        m = self._norm_mode(mode)
        mb = self._bindings.get(m)
        if mb is None or key not in mb:
            return False
        b = mb[key]
        mb[key] = Binding(
            key=b.key,
            action_spec=b.action_spec,
            span=b.span,
            group=b.group,
            mode=b.mode,
            desc=str(desc),
        )
        return True

    def bindings(self, *, mode: str | None = None) -> dict[str, str]:
        m = self._norm_mode(mode)
        return {k: b.action_spec for k, b in self._bindings.get(m, {}).items()}

    def binding_rows(self) -> list[list[object]]:
        rows: list[list[object]] = []
        for b in self._iter_bindings():
            span = 0 if b.span is None else [b.span.filename, int(b.span.line), int(b.span.col)]
            rows.append([b.key, b.action_spec, span])
        return rows

    def binding_detail_rows(self) -> list[list[object]]:
        rows: list[list[object]] = []
        for b in self._iter_bindings():
            span = 0 if b.span is None else [b.span.filename, int(b.span.line), int(b.span.col)]
            rows.append([b.key, b.action_spec, b.group or 0, span])
        return rows

    def binding_info_rows(self) -> list[list[object]]:
        rows: list[list[object]] = []
        for b in self._iter_bindings():
            span = 0 if b.span is None else [b.span.filename, int(b.span.line), int(b.span.col)]
            rows.append([b.key, b.action_spec, b.desc or 0, b.group or 0, span])
        return rows

    def binding_detail_rows_for(self, mode: str | None = None) -> list[list[object]]:
        m = self._norm_mode(mode)
        rows: list[list[object]] = []
        for key in sorted(self._bindings.get(m, {}).keys()):
            b = self._bindings[m][key]
            span = 0 if b.span is None else [b.span.filename, int(b.span.line), int(b.span.col)]
            rows.append([b.key, b.action_spec, b.group or 0, span])
        return rows

    def binding_info_rows_for(self, mode: str | None = None) -> list[list[object]]:
        m = self._norm_mode(mode)
        rows: list[list[object]] = []
        for key in sorted(self._bindings.get(m, {}).keys()):
            b = self._bindings[m][key]
            span = 0 if b.span is None else [b.span.filename, int(b.span.line), int(b.span.col)]
            rows.append([b.key, b.action_spec, b.desc or 0, b.group or 0, span])
        return rows

    def binding_mode_rows(self) -> list[list[object]]:
        rows: list[list[object]] = []
        for b in self._iter_bindings():
            span = 0 if b.span is None else [b.span.filename, int(b.span.line), int(b.span.col)]
            rows.append([b.mode, b.key, b.action_spec, b.group or 0, span])
        return rows

    def resolved_binding_rows(self, modes: list[str] | None = None) -> list[list[object]]:
        seen_modes: set[str] = set()
        order = [self._norm_mode(m) for m in (modes or [])] + ["global"]
        winners: dict[str, Binding] = {}
        for mode in order:
            if mode in seen_modes:
                continue
            seen_modes.add(mode)
            for key, b in self._bindings.get(mode, {}).items():
                if key not in winners:
                    winners[key] = b
        rows: list[list[object]] = []
        for key in sorted(winners.keys()):
            b = winners[key]
            span = 0 if b.span is None else [b.span.filename, int(b.span.line), int(b.span.col)]
            rows.append([b.mode, b.key, b.action_spec, b.group or 0, span])
        return rows

    def resolved_binding_info_rows(self, modes: list[str] | None = None) -> list[list[object]]:
        seen_modes: set[str] = set()
        order = [self._norm_mode(m) for m in (modes or [])] + ["global"]
        winners: dict[str, Binding] = {}
        for mode in order:
            if mode in seen_modes:
                continue
            seen_modes.add(mode)
            for key, b in self._bindings.get(mode, {}).items():
                if key not in winners:
                    winners[key] = b
        rows: list[list[object]] = []
        for key in sorted(winners.keys()):
            b = winners[key]
            span = 0 if b.span is None else [b.span.filename, int(b.span.line), int(b.span.col)]
            rows.append([b.mode, b.key, b.action_spec, b.desc or 0, b.group or 0, span])
        return rows

    def resolved_binding_row(self, key: str, modes: list[str] | None = None) -> list[object] | int:
        b = self.get_binding(key, modes=modes)
        if b is None:
            return 0
        span = 0 if b.span is None else [b.span.filename, int(b.span.line), int(b.span.col)]
        return [b.mode, b.key, b.action_spec, b.group or 0, span]

    def resolved_binding_info_row(self, key: str, modes: list[str] | None = None) -> list[object] | int:
        b = self.get_binding(key, modes=modes)
        if b is None:
            return 0
        span = 0 if b.span is None else [b.span.filename, int(b.span.line), int(b.span.col)]
        return [b.mode, b.key, b.action_spec, b.desc or 0, b.group or 0, span]

    def remove_group(self, group: str) -> int:
        removed = 0
        for mode in list(self._bindings.keys()):
            mb = self._bindings[mode]
            for key, b in list(mb.items()):
                if b.group == group:
                    del mb[key]
                    removed += 1
            if mode != "global" and mb == {}:
                self._bindings.pop(mode, None)
        return removed

    def groups(self) -> list[str]:
        out = sorted({str(b.group) for b in self._iter_bindings() if b.group})
        return out

    def modes(self) -> list[str]:
        out = sorted([str(m) for m, binds in self._bindings.items() if binds])
        if "global" not in out:
            out.insert(0, "global")
        return out
