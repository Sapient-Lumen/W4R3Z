from __future__ import annotations

from collections.abc import Iterator, Sequence

from micromax_editor.project_picker import (
    PROJECT_FILE_CONTEXT_LIMIT,
    normalize_project_context_paths,
    normalize_project_status_by_path,
    project_file_rows,
    project_file_section_label,
)


def test_empty_query_puts_bounded_context_first_without_duplicates() -> None:
    inventory = [
        "README.md",
        "src/active.py",
        "src/previous.py",
        "tests/test_active.py",
    ]
    rows = project_file_rows(
        inventory,
        context_paths=["src/previous.py", "README.md", "src/previous.py"],
        status_by_path={
            "src/active.py": "active",
            "src/previous.py": "previous",
            "README.md": "recent",
        },
        limit=40,
    )

    assert [row[0] for row in rows[:2]] == ["src/previous.py", "README.md"]
    assert [row[1] for row in rows[:2]] == ["projectfile-context", "projectfile-context"]
    assert [row[2] for row in rows[:2]] == ["previous", "recent"]
    assert project_file_section_label(rows[0], query="") == "Open and recent"
    assert len([row[0] for row in rows]) == len({row[0] for row in rows})

    active = next(row for row in rows if row[0] == "src/active.py")
    assert active[1:] == ["projectfile", "active", "src"]
    assert project_file_section_label(active, query="") == "src"


def test_query_searches_complete_inventory_once_and_uses_match_section() -> None:
    inventory = ["README.md", "src/alpha.py", "src/beta.py", "tests/test_alpha.py"]
    rows = project_file_rows(
        inventory,
        "alpha",
        context_paths=["README.md", "src/beta.py"],
        status_by_path={"src/beta.py": "previous", "src/alpha.py": "active"},
        limit=40,
    )

    assert {row[0] for row in rows} == {"src/alpha.py", "tests/test_alpha.py"}
    assert all(row[1] == "projectfile" for row in rows)
    assert all(project_file_section_label(row, query="alpha") == "Matches" for row in rows)
    assert len(rows) == len({row[0] for row in rows})


def test_context_and_status_normalization_rejects_nonmembers_and_stays_bounded() -> None:
    inventory = [f"src/{index:02d}.py" for index in range(PROJECT_FILE_CONTEXT_LIMIT + 5)]
    values = ["", "../escape", *inventory, inventory[0]]

    context = normalize_project_context_paths(values, inventory=inventory)
    assert context == tuple(inventory[:PROJECT_FILE_CONTEXT_LIMIT])

    statuses = normalize_project_status_by_path(
        {
            inventory[0]: "previous",
            inventory[1]: "",
            "../escape": "active",
            "not-in-snapshot.py": "recent",
        },
        inventory=inventory,
    )
    assert statuses == {inventory[0]: "previous"}

    rows = project_file_rows(
        inventory,
        context_paths=values,
        status_by_path={"../escape": "active", inventory[0]: "previous"},
        limit=PROJECT_FILE_CONTEXT_LIMIT + 5,
    )
    assert all(row[0] in inventory for row in rows)
    assert len([row for row in rows if row[1] == "projectfile-context"]) == PROJECT_FILE_CONTEXT_LIMIT


class _CountingInventory(Sequence[str]):
    def __init__(self, values: list[str]) -> None:
        self.values = list(values)
        self.iterations = 0

    def __len__(self) -> int:
        return len(self.values)

    def __getitem__(self, index: int) -> str:
        return self.values[index]

    def __iter__(self) -> Iterator[str]:
        self.iterations += 1
        return iter(self.values)


def test_row_planner_normalizes_snapshot_once_per_refresh() -> None:
    inventory = _CountingInventory(
        ["README.md", *[f"src/generated-{index:04d}.py" for index in range(4096)]]
    )

    rows = project_file_rows(
        inventory,
        context_paths=["src/generated-0001.py"],
        status_by_path={"src/generated-0001.py": "previous"},
        limit=40,
    )

    assert inventory.iterations == 1
    assert rows[0][:3] == [
        "src/generated-0001.py",
        "projectfile-context",
        "previous",
    ]
