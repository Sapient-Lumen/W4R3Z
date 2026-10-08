from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Prompt:
    """A minimal prompt model (command bar / find bar).

    This is headless and UI-agnostic. A UI layer can render it however it wants.

    History navigation is implemented with two extra fields:
      - hist_index: index into the history list (0..len-1) or None if not browsing
      - hist_saved: the prompt text before history navigation started

    Prompt completion is modeled as a simple *suggestion session*:
      - suggestions: candidate strings
      - suggest_index: current candidate index
      - suggest_start/suggest_end: the replacement range in `suggest_base`
      - suggest_base: the prompt text at the start of the session
    """

    kind: str  # 'command' or 'find'
    text: str = ""
    cursor: int = 0

    hist_index: int | None = None
    hist_saved: str = ""

    # Completion/suggestion state (command prompt only).
    suggestions: list[str] = field(default_factory=list)
    suggestion_rows: list[list[str]] = field(default_factory=list)
    suggest_index: int = 0
    suggest_start: int = 0
    suggest_end: int = 0
    suggest_base: str = ""

    def clear_suggestions(self) -> None:
        self.suggestions = []
        self.suggestion_rows = []
        self.suggest_index = 0
        self.suggest_start = 0
        self.suggest_end = 0
        self.suggest_base = ""

    def set_text(self, s: str) -> None:
        self.text = s
        self.cursor = min(self.cursor, len(self.text))
        # Any text mutation cancels an in-progress suggestion session.
        self.clear_suggestions()

    def set_cursor(self, pos: int) -> None:
        self.cursor = max(0, min(pos, len(self.text)))

    def prefill(self, s: str) -> None:
        self.text = s
        self.cursor = len(self.text)
        self.hist_index = None
        self.hist_saved = ""
        self.clear_suggestions()

    def begin_suggestions(
        self,
        cands: list[str],
        *,
        start: int,
        end: int,
        rows: list[list[str]] | None = None,
    ) -> None:
        self.suggestions = list(cands)
        if rows is None:
            self.suggestion_rows = [[str(c), "", "", ""] for c in cands]
        else:
            out: list[list[str]] = []
            for i, c in enumerate(cands):
                if i < len(rows):
                    row = list(rows[i])
                else:
                    row = [str(c), "", "", ""]
                while len(row) < 4:
                    row.append("")
                row[0] = str(c)
                out.append([str(row[0]), str(row[1]), str(row[2]), str(row[3])])
            self.suggestion_rows = out
        self.suggest_index = 0
        self.suggest_start = int(start)
        self.suggest_end = int(end)
        self.suggest_base = self.text

    def apply_suggestion(self, index: int) -> None:
        if not self.suggestions:
            return
        i = int(index) % len(self.suggestions)
        cand = self.suggestions[i]
        base = self.suggest_base
        s = base[: self.suggest_start] + cand + base[self.suggest_end :]
        self.text = s
        self.cursor = self.suggest_start + len(cand)
        self.suggest_index = i
